"""favorable_both_models.py -- for every favorable column: (1) k_f-only model (alpha_s=1, clean-bed limit);
(2) full Serial-3 with k_r PINNED to the per-medium constant and everything else FREE -- delivery r_s (within
+/-0.6 dex of the plateau/RP-slope seed), single-interception alpha_s (via the MI fraction 1-alpha_s), crawl
attachment alpha_m, and recruitment f_x -- fit jointly to the BTEC AND the retention profile (RP level +
two-segment slope). k_r is the ONLY pinned kinetic parameter; pinning it breaks the f_x<->k_r degeneracy so
f_x can be free. Model 2 is run for columns that have BOTH a usable BTEC (>=3) and RP (>=3) with a known C0;
RP-only columns keep k_f-only. Writes Favorable_data_and_sim.xlsx (per-column BTEC+RP data and both model
curves) with a leading 'Favorable fits' summary sheet, plus favorable_MI_table.json.
Weights: RP level W_RP=6, RP two-segment slope W_SH=2.5, BTEC W_BT=3.

** TWO KNOWN STALENESSES, 2026-08-25. Read before re-running or quoting these fits. **

(A) RP CONVENTION. This script still builds its retention profile as the eq (4) END-OF-INJECTION RATE
    SNAPSHOT (see `Yst` in Eng.run and the note written into each sheet at row 10). That convention was
    RETIRED as invalid on 2026-08-25 for the unfavorable master: the columns are excised at 10 PV after
    ~7.0 PV of elution, so the observable is the ACCUMULATED solid phase, and the snapshot ignores 70%
    of the experiment. The favorable columns come from the same experiments and the same excision
    protocol, so the same objection applies here. `unfav_master_fit.py` was converted; this script was
    NOT. Consequence: the favorable r_s -- which `unfav_master_fit.py` then pins as FAVFIT -- is fitted
    under the retired convention.

(B) k_r CONSTANTS. KR_MED below is PINNED, not seeded, and its values are superseded (see the comment
    on that line).

Neither has been corrected, deliberately, and (A) is now corrected-by-measurement rather than by
argument. `Code/fav_convention_check.py` refits every favorable column under BOTH conventions, paired
within column: r_s moves <= 0.014 dex on nine of ten, median 0.004, at unchanged cost and with no r_s
on its bound. The tenth (quartz Li I) appears to move 0.208 dex, but r_s is NOT IDENTIFIABLE there --
pinning it anywhere across 42.7 to 68.9 costs <= 0.01% under EITHER convention, with alpha_s sliding
0.88 -> 0.60 to compensate. The identifiable product r_s*alpha_s moves <= 0.040 dex everywhere.
** So this script's output stands as delivered: FAVFIT is unchanged and nothing downstream was re-run
(W.P.J., 2026-08-26). ** The physical reason is that under favorable chemistry the multiple-intercepting
population is negligible, so almost nothing is left in a mobile state to redistribute during the 7 PV
of elution the snapshot ignores -- which is exactly the population that made the convention matter for
the unfavorable set. (B) is likewise left as-is by the same 2026-08-25 decision on the r_s <-> k_r loop.
Full workings: Records/plateau_rs_decision.md section 3b.1."""
import numpy as np, openpyxl, re, functools, json
from openpyxl.utils import column_index_from_string as cix
from openpyxl.styles import Font
from scipy.linalg import expm
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import splu
from scipy.optimize import least_squares
print=functools.partial(print,flush=True)
DATA="../Data/DataFromLi&Tong.xlsx"; DAY=86400.; L=0.2
REV,T0,Vref=22.801836559387397,3.58,0.1667; INJPV=T0/(L/Vref)
# ** k_r is PINNED here, not seeded ** -- Model 2 fixes it so that f_x becomes identifiable, and the
# r_s this script returns is what unfav_master_fit.py then pins as FAVFIT. So these two numbers are
# load-bearing, and they are SUPERSEDED: the current constants are 3.75e-5 / 1.82e-5 (glass/quartz),
# ~0.07 dex away. W.P.J. decided 2026-08-25 NOT to iterate the r_s <-> k_r loop (the shift is small,
# it is damped twice over, and iterating would force a full unfavorable refit for no resolvable
# change). CONSEQUENCE: the favorable fits are pinned to superseded constants, r_s must not be
# described as "independent" of the unfavorable fits, and re-running this script with the current
# constants would make the favorable fits disagree with the published unfavorable alphas. See
# Records/plateau_rs_decision.md section 3b and Records/kr_trend_analysis.md.
KR_MED={"glass":5.58e-5,"quartz":1.87e-5}   # PINNED; superseded by 3.75e-5 / 1.82e-5, deliberately not updated
W_RP,W_SH,W_BT=6.0,2.5,3.0
# Two favorable Tong columns have NO C0 in the sheet; use the RP-implied (mass-balance-closing) C0 (W.P.J. approved, 2026-08-20).
C0_OVERRIDE={("Glass Tong","CS"):1.157e6,("Quartz Tong","O"):8.2e6}  # O: same run as unfav twin R -> C0=8.2e6 (was 5.762e6; 2026-08-23)
PLACE={-6.,-9.94,-15.33}; isp=lambda v:any(abs(v-p)<0.05 for p in PLACE)
wb=openpyxl.load_workbook(DATA,data_only=True)
def c0cell(ws,c,r):
    m=re.search(r'([\d.]+)\s*E\s*([+-]?\d+)',str(ws.cell(r,c).value));return float(m.group(1))*10**int(m.group(2)) if m else None
def c0hdr(ws,c,br):
    H=" || ".join(str(ws.cell(r,c).value) for r in range(1,br) if ws.cell(r,c).value is not None)
    m=re.search(r'([\d.]+)\s*E\s*([+-]?\d+)',H);return float(m.group(1))*10**int(m.group(2)) if m else None
# RP_ROWS: the two Li sheets are NOT laid out the same -- Glass Beads Li's BTEC block runs longer, so its
# RP header sits 6 rows lower than Quartz Sand Li's. A single hardcoded row range for both sheets silently
# truncates whichever one it's NOT tuned for. Fixed 2026-09-01 (W.P.J.) to match the per-sheet ranges
# extract_tidy_data.py already uses (see that file's docstring, fixed there 2026-08-28). ALL RP data has
# exactly 10 depth points, always (W.P.J.) -- the assert below is not optional defensive code, it is the
# contract: any loader that produces a different count was read wrong, and must fail loudly, not silently.
RP_ROWS = {"Microspheres Glass Beads Li": (47, 57), "Microspheres Quartz Sand Li": (41, 51)}


def load_li(sh,dc):
    ws=wb[sh]
    bt=[(ws.cell(r,dc).value,ws.cell(r,dc+1).value) for r in range(10,45)];bt=[(a,b) for a,b in bt if isinstance(a,(int,float)) and isinstance(b,(int,float)) and b<0.5 and not isp(b)]
    r0,r1=RP_ROWS[sh]
    rp=[(ws.cell(r,dc).value,ws.cell(r,dc+1).value) for r in range(r0,r1)];rp=[(a,b) for a,b in rp if isinstance(a,(int,float)) and isinstance(b,(int,float)) and b>0.5 and not isp(b)]
    assert len(rp)==10, f"RP truncated: {sh} col {dc} got {len(rp)} points, expected 10 -- row range wrong for this sheet"
    return (np.array(bt) if bt else np.zeros((0,2))),np.array(rp),c0cell(ws,dc,14 if "Glass Beads Li" in sh else 8)  # C0 row: GB Li=14, Qtz Li=8 (data_inventory §4)
def load_tong(sh,c):
    ws=wb[sh];br=None
    for r in range(6,13):
        x=ws.cell(r,c).value
        if isinstance(x,str) and x.strip().upper().startswith("PV"):br=r;break
    pv=[];lc=[]
    for r in range(br+1,67):
        a=ws.cell(r,c).value;b=ws.cell(r,c+1).value
        if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isp(b) and b<0.5: pv.append(float(a));lc.append(float(b))
    xx=[];rp=[]
    for r in range(68,78):
        a=ws.cell(r,c).value;b=ws.cell(r,c+1).value
        if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isp(b): xx.append(float(a));rp.append(float(b))
    # ALL RP data has exactly 10 depth points, always (W.P.J., 2026-09-01) -- assert, don't silently truncate.
    if rp: assert len(rp)==10, f"RP truncated: {sh} col {c} got {len(rp)} points, expected 10"
    return (np.array(list(zip(pv,lc))) if pv else np.zeros((0,2))),np.array(list(zip(xx,rp))),c0cell(ws,c,8)  # Tong C0 at row 8 (read cell, not header scrape)
def rs_plateau(bt):
    pv=bt[:,0];lc=bt[:,1];m=(pv>1.2)&(pv<3.4)
    if m.sum()<2:m=(pv>0.9)&(pv<3.6)
    if m.sum()<2:return None
    return -np.log(10)*float(np.median(lc[m]))/L
def rs_rpslope(rp): return -np.log(10)*float(np.polyfit(rp[:,0],rp[:,1],1)[0])
def sl(x,y):h=len(x)//2;return float(np.polyfit(x[:h+1],y[:h+1],1)[0]),float(np.polyfit(x[h:],y[h:],1)[0])
class Eng:
    def __init__(s,vmday):s.v=vmday/DAY;s.dx=L/90;s.dt=s.dx/s.v;s.pv=L/s.v
    def run(s,k1,a_s,a_m,fx,kr,vns=0.05,tot=10):
        kf=k1;k2=fx*kf;kmw=a_m*kf;kmg=a_m*vns*kf;G=np.zeros((4,4))
        G[0,0]-=kf;G[3,0]+=a_s*kf;G[1,0]+=(1-a_s)*kf
        G[1,1]-=(kmw+k2);G[3,1]+=kmw;G[2,1]+=k2;G[2,2]-=kmg;G[3,2]+=kmg;G[1,2]+=kr;G[2,2]-=kr
        E=expm(G*s.dt);D=s.v*L/150;r=D*s.dt/s.dx**2;mn=(1+2*r)*np.ones(90);of=-r*np.ones(89);mn[0]=1+r;mn[-1]=1+r
        lu=splu(csc_matrix(diags([of,mn,of],[-1,0,1],format="csc")))
        nt=int(round(tot*90));ti=INJPV*s.pv;c=vns;Y=np.zeros((4,90));C=np.zeros(nt);t=0.;Yst=None
        for i in range(nt):
            Y=E@Y;C[i]=Y[0,-1]+Y[1,-1]+c*Y[2,-1];Y[0,1:]=Y[0,:-1];Y[0,0]=0;Y[1,1:]=Y[1,:-1];Y[1,0]=0
            ym=Y[2].copy();Y[2,1:]=ym[1:]-c*(ym[1:]-ym[:-1]);Y[2,0]=ym[0]*(1-c);t+=s.dt
            if t<ti:Y[0,0]+=1.
            Y[0,:]=lu.solve(Y[0,:]);Y[1,:]=lu.solve(Y[1,:])
            if t<ti and t>0.9*ti:Yst=Y.copy()
        tp=(np.arange(nt)+1)*s.dt/s.pv;x=(np.arange(90)+0.5)*s.dx
        # ** RETIRED CONVENTION -- see staleness (A) in the module docstring. The unfavorable master
        #    now uses rp = Y[3,:]/ti (accumulated solid phase at excision). This line is the eq (4)
        #    injection-window RATE snapshot and is kept only so the favorable fits stay reproducible as shipped.
        rp=a_s*kf*Yst[0,:]+kmw*Yst[1,:]+kmg*Yst[2,:]
        return dict(tp=tp,C=np.maximum(C,1e-300),x=x,rp=np.maximum(rp,1e-300))
COLS=[("Glass Tong","L","tong","glass",0.5,4,50),("Glass Tong","AB","tong","glass",1.0,4,50),
 ("Glass Tong","B","tong","glass",0.2,4,50),("Glass Tong","AU","tong","glass",0.1,8,50),
 ("Glass Tong","BB","tong","glass",0.2,8,50),("Glass Tong","CS","tong","glass",2.0,8,50),
 ("Quartz Tong","O","tong","quartz",0.5,8,50),
 ("Quartz Li","B","li","quartz",0.98,2,10),("Quartz Li","E","li","quartz",0.98,4,10),("Quartz Li","I","li","quartz",0.98,8,10),
 ("Glass Li","B","li","glass",0.98,2,10),("Glass Li","E","li","glass",0.98,4,10),("Glass Li","H","li","glass",0.98,8,10)]
SHEET={"Glass Tong":"Microspheres Glass Beads Tong","Quartz Tong":"Microspheres Quartz Sand Tong",
       "Quartz Li":"Microspheres Quartz Sand Li","Glass Li":"Microspheres Glass Beads Li"}
THETA={"glass":0.375,"quartz":0.36}
out=openpyxl.Workbook(); out.remove(out.active); Bf=Font(bold=True); IT=Font(italic=True); table=[]
def put(ws,r,c,v,bold=False,ital=False):
    cell=ws.cell(r,c,v)
    if bold:cell.font=Bf
    elif ital:cell.font=IT
    return cell
for tab,letter,layout,med,size,vel,IS in COLS:
    bt,rp,C0=(load_li(SHEET[tab],cix(letter)) if layout=="li" else load_tong(SHEET[tab],cix(letter)))
    if C0 is None: C0=C0_OVERRIDE.get((tab,letter))   # CS / O: no C0 in sheet -> RP-implied
    if len(bt)>=2: rs_seed=rs_plateau(bt); rssrc="plateau"
    elif len(rp)>=3: rs_seed=rs_rpslope(rp); rssrc="RP-slope"
    else: continue
    if rs_seed is None: continue
    V_MS=vel/DAY; eng=Eng(vel); theta=THETA[med]; kr_med=KR_MED[med]
    logK=(np.log10(REV*T0*theta*C0*Vref)) if C0 else None
    r0=eng.run(rs_seed*V_MS,1.0,0.0,0.0,0.0)   # Model 1: k_f only, at seed r_s
    # ---- Model 2: full fit (k_r pinned; r_s, a_s, a_m, f_x free) to BTEC + RP ----
    fit=None
    if len(bt)>=3 and len(rp)>=3 and logK is not None:
        pv=bt[:,0]; lc=bt[:,1]; rx=rp[:,0]; rlog=rp[:,1]; si,so=sl(rx,rlog); k1s=np.log10(rs_seed*V_MS)
        def rpmodel(r):  # log10 retained spheres at the data distances; amplitude FIXED by C0 (never offset-aligned)
            return logK+np.log10(np.maximum(np.interp(rx,r['x'],r['rp'])/V_MS,1e-300))
        def resid(p):
            kk=10**p[0]; a_s=1-10**p[1]; am=10**p[2]; fx=10**p[3]; r=eng.run(kk,a_s,am,fx,kr_med)
            mC=np.log10(np.maximum(np.interp(pv,r['tp'],r['C']),1e-12))
            lS=rpmodel(r); sm,sn=sl(rx,lS)
            return np.concatenate([W_RP*(lS-rlog),W_SH*np.array([sm-si,sn-so]),W_BT*(mC-lc)])
        best=None
        for s0 in [[k1s,-1.5,-1.5,np.log10(.005)],[k1s,-2.0,-2.0,np.log10(.02)]]:
            rr=least_squares(resid,s0,bounds=([k1s-0.6,-3,-3.3,np.log10(1e-4)],[k1s+0.6,np.log10(0.5),np.log10(0.9),np.log10(0.1)]),max_nfev=60)
            if best is None or rr.cost<best.cost:best=rr
        k1f=10**best.x[0]; a_s=1-10**best.x[1]; a_m=10**best.x[2]; fx=10**best.x[3]; rs_fit=k1f/V_MS
        r1=eng.run(k1f,a_s,a_m,fx,kr_med)
        tm=pv>4.2
        tailRMS=float(np.sqrt(np.mean((np.log10(np.maximum(np.interp(pv[tm],r1['tp'],r1['C']),1e-12))-lc[tm])**2))) if tm.sum()>=2 else None
        tailRMS_kf=float(np.sqrt(np.mean((np.log10(np.maximum(np.interp(pv[tm],r0['tp'],r0['C']),1e-12))-lc[tm])**2))) if tm.sum()>=2 else None
        lS1=rpmodel(r1)
        rpRMS=float(np.sqrt(np.mean((lS1-rlog)**2)))
        fit=dict(rs_fit=rs_fit,a_s=a_s,MIpct=100*(1-a_s),a_m=a_m,fx=fx,tailRMS=tailRMS,tailRMS_kf=tailRMS_kf,rpRMS=rpRMS,r1=r1)
    def rpL(r):
        rl=np.interp(rp[:,0],r['x'],r['rp'])/V_MS; rel=np.log10(np.maximum(rl,1e-300))
        if logK is not None: return logK+rel
        off=np.mean(rp[:,1]-rel); return rel+off
    table.append(dict(tab=tab,col=letter,med=med,size=size,vel=vel,IS=IS,favvia=("pH 2" if "Tong" in tab else "aminated"),rs_seed=round(rs_seed,1),rssrc=rssrc,
        kr_pv=round(kr_med*(L/eng.v),3),kr_s=kr_med,
        rs_fit=(round(fit['rs_fit'],1) if fit else None),a_s=(round(fit['a_s'],4) if fit else None),
        MIpct=(round(fit['MIpct'],2) if fit else None),a_m=(round(fit['a_m'],4) if fit else None),
        fx=(round(fit['fx'],4) if fit else None),
        tailRMS=(round(fit['tailRMS'],3) if (fit and fit['tailRMS'] is not None) else None),
        tailRMS_kf=(round(fit['tailRMS_kf'],2) if (fit and fit['tailRMS_kf'] is not None) else None),
        rpRMS=(round(fit['rpRMS'],3) if fit else None)))
    # ---- per-column sheet ----
    sn=("%s_%s"%(tab.replace(" ",""),letter))[:31]; ws=out.create_sheet(sn)
    put(ws,1,1,f"{tab} - {med} {size} um, {vel} m/day, {IS} mM, FAVORABLE (col {letter})",True)
    put(ws,3,1,"HEADER DATA",True)
    put(ws,4,1,f"medium={med} | diameter={size} um | pore velocity={vel} m/day | IS={IS} mM (favorable)")
    put(ws,5,1,f"C0={('%.3e /mL'%C0) if C0 else 'not in sheet (RP level data-aligned)'} | theta={theta} | L={L} m")
    put(ws,7,1,"MODEL SIMULATION PARAMETERS",True)
    put(ws,8,1,f"Model 1 - k_f ONLY (clean-bed limit): alpha_s=1, alpha_m=f_x=k_r=0, v_ns=5%. r_s={rs_seed:.2f}/m [seed from {rssrc}]"+(f", logK={logK:.3f}" if logK is not None else ""))
    if fit:
        put(ws,9,1,(f"Model 2 - FULL, k_r PINNED, all else FREE (fit to BTEC + RP): r_s={fit['rs_fit']:.1f}/m "
                    f"(seed {rs_seed:.1f}, free +/-0.6 dex), alpha_s={fit['a_s']:.4f} (MI 1-alpha_s={fit['MIpct']:.2f}%), "
                    f"alpha_m={fit['a_m']:.4f}, f_x={fit['fx']:.4f}, k_r={kr_med:.2e}/s = {kr_med*(L/eng.v):.3f}/PV (pinned), v_ns=5%. "
                    f"tailRMS={fit['tailRMS']}, rpRMS={fit['rpRMS']:.3f}"))
    else:
        put(ws,9,1,"Model 2 - n/a (needs BTEC>=3 & RP>=3 & known C0; k_f-only reported).")
    put(ws,10,1,"numerics: expm reaction + upwind advection + implicit dispersion (Pe=150), 90 cells; RP=end-of-injection snapshot (RETIRED convention -- see the module docstring).")
    r=12; put(ws,r,1,"BREAKTHROUGH-ELUTION CURVE (BTEC)",True);r+=1
    put(ws,r,1,"PV",True);put(ws,r,2,"LOG(C/Co) data",True);put(ws,r,3,"model 1: k_f only",True);put(ws,r,4,"model 2: full",True);r+=1
    if len(bt)>=1:
        m0=np.log10(np.maximum(np.interp(bt[:,0],r0['tp'],r0['C']),1e-12))
        mf=np.log10(np.maximum(np.interp(bt[:,0],fit['r1']['tp'],fit['r1']['C']),1e-12)) if fit else None
        for i in range(len(bt)):
            put(ws,r,1,round(float(bt[i,0]),4));put(ws,r,2,round(float(bt[i,1]),4));put(ws,r,3,round(float(m0[i]),4))
            put(ws,r,4,(round(float(mf[i]),4) if mf is not None else "n/a"));r+=1
    else:
        put(ws,r,1,"(no BTEC reported for this column)");r+=1
    r+=1; put(ws,r,1,"RETENTION PROFILE (RP)",True);r+=1
    put(ws,r,1,"Distance (m)",True);put(ws,r,2,"LOG(spheres) data",True);put(ws,r,3,"model 1: k_f only",True);put(ws,r,4,"model 2: full",True);r+=1
    lS0=rpL(r0); lS1=rpL(fit['r1']) if fit else None
    for i in range(len(rp)):
        put(ws,r,1,round(float(rp[i,0]),4));put(ws,r,2,round(float(rp[i,1]),4));put(ws,r,3,round(float(lS0[i]),4))
        put(ws,r,4,(round(float(lS1[i]),4) if lS1 is not None else "n/a"));r+=1
    ws.column_dimensions['A'].width=16
# ---- Favorable fits summary (leading sheet) ----
t5=out.create_sheet("Favorable fits"); out.move_sheet(t5,-(len(out.sheetnames)-1))
put(t5,1,1,"Serial-3 favorable-condition fits (k_r pinned per medium; r_s, alpha_s, alpha_m, f_x free; joint BTEC+RP)",True)
put(t5,2,1,"k_r pinned per medium: glass 5.58e-5/s, quartz 1.87e-5/s. r_s free within a factor of four (+/-0.6 dex) of the plateau/RP-slope seed. v_ns = 5% of v. RMS in log10 units. Favorable via = pH 2 (Tong) / aminated colloids (Li), NOT ionic strength.",ital=True)
hdr=["medium","study","col","size_um","v_mday","favorable via","r_s_fit /m","r_s_seed /m","alpha_s","MI% (1-a_s)","alpha_m","f_x","k_r /s (pin)","tail RMS","RP RMS"]
for j,h in enumerate(hdr,1): put(t5,4,j,h,True)
ri=5
for t in table:
    row=[t['med'],t['tab'],t['col'],t['size'],t['vel'],t['favvia'],t['rs_fit'],t['rs_seed'],t['a_s'],t['MIpct'],t['a_m'],t['fx'],float(f"{t['kr_s']:.3e}"),t['tailRMS'],t['rpRMS']]
    for j,v in enumerate(row,1): put(t5,ri,j,("" if v is None else v))
    ri+=1
put(t5,ri+1,1,"Blank rows = RP-only columns (no BTEC): Model 2 not fit; see per-column sheets for k_f-only.",ital=True)
for col in "ABCDEFGHIJKLMNO": t5.column_dimensions[col].width=12
# ---- Favorable tail test summary (MI fraction + k_f->full fit ratio) ----
t4=out.create_sheet("Favorable tail test"); out.move_sheet(t4,-(len(out.sheetnames)-1))
put(t4,1,1,"Favorable extended tail: the k_f-only clean-bed model cannot reproduce the multi-PV tail; the multiple-interceptor crawl (k_r pinned) does.",True)
put(t4,2,1,"Fit Ratio = tail RMS (log10) k_f-only -> full model; large drop = the crawl is required. '—' = no tail region (<2 pts beyond 4.2 PV). Values are the new joint BTEC+RP free fit.",ital=True)
h4=["medium","study","col","size_um","v_mday","favorable via","(1-alpha_s) MI","alpha_m","f_x","r_s_fit /m","Fit Ratio (tailRMS kf->full)"]
for j,h in enumerate(h4,1): put(t4,4,j,h,True)
ri4=5
for t in table:
    fr=(f"{t['tailRMS_kf']:.2f} -> {t['tailRMS']:.2f}" if (t.get('tailRMS_kf') is not None and t['tailRMS'] is not None) else "—")
    row=[t['med'],t['tab'],t['col'],t['size'],t['vel'],t['favvia'],(round(1-t['a_s'],4) if t['a_s'] is not None else ""),t['a_m'],t['fx'],t['rs_fit'],fr]
    for j,v in enumerate(row,1): put(t4,ri4,j,("" if v is None else v))
    ri4+=1
for col in "ABCDEFGHIJK": t4.column_dimensions[col].width=13
out.save("../Manuscript/FigsExcelsFavorable/Favorable_data_and_sim.xlsx")
print(f"{'cond':16}{'rs_fit':>7}{'kr/s':>10}{'MI%':>7}{'a_m':>7}{'f_x':>8}{'tRMS':>7}{'rpRMS':>7}")
for t in table:
    print(f"{t['tab']+' '+t['col']:16}{str(t['rs_fit']):>7}{t['kr_s']:>10.3e}{str(t['MIpct']):>7}{str(t['a_m']):>7}{str(t['fx']):>8}{str(t['tailRMS']):>7}{str(t['rpRMS']):>7}")
json.dump(table,open("artifacts/favorable_MI_table.json","w"),indent=1)
print("wrote Favorable_data_and_sim.xlsx (favorable fits + per-column both-model sheets) + favorable_MI_table.json")
