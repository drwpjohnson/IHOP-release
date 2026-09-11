"""fx_aplat_relation.py -- diagnostic: does the plateau-alpha excess relate to recruitment f_x?

Computes, over the 13 conditions that have a_plat (see Records/aplat_plateau_alpha.md),
Delta = a_plat - max(alpha_single, alpha_mult) and tests it against fitted f_x. Reports Pearson/
Spearman, the alpha_mult confound, the partial correlation controlling alpha_mult, and within-medium
correlations; writes fx_aplat_relation.png (Delta vs f_x, and a_plat vs f_x, colored by medium).

FINDING: raw Delta~f_x = +0.63, but f_x~alpha_mult = +0.80 (f_x<->k_r<->v_ns collinearity); partial
Delta~f_x | alpha_mult drops to +0.31 (+0.10 on log f_x); within glass = -0.05, within quartz = +0.96
(n=4, leverage). => the excess tracks the RP BRANCH (alpha_mult vs alpha_single), not recruitment f_x;
a_plat cannot break the f_x<->k_r degeneracy. W.P.J., 2026-08-24.

Paths are Box-root-relative (LiTong_experimental_data_tidy.csv, UnfavorableMaster.xlsx). Usage: python3 fx_aplat_relation.py
"""
import csv, math, numpy as np, openpyxl
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
L_STUDY={"Tong":0.19243,"Li":0.19}; LN10=math.log(10.0)
def sizeclass(s): s=float(s); return 1.1 if 0.9<=s<=1.15 else round(s,2)
rows=list(csv.DictReader(open("LiTong_experimental_data_tidy.csv")))
def meanlog(cond):
    vs=[float(r['value']) for r in rows if r['condition_id']==cond and r['curve']=='BTEC' and 1.2<float(r['x'])<4.0]
    if not vs:
        pts=sorted((float(r['x']),float(r['value'])) for r in rows if r['condition_id']==cond and r['curve']=='BTEC')
        if not pts: return None
        vs=[v for x,v in pts[-max(3,len(pts)//3):]]
    return sum(vs)/len(vs)
def meta(cond):
    r=next(rr for rr in rows if rr['condition_id']==cond)
    return dict(med=r['medium'],size=float(r['colloid_um']),v=float(r['velocity_mday']),IS=float(r['IS_mM']),study=r['source'])
allc=sorted(set(r['condition_id'] for r in rows))
FAV={}
for c in allc:
    if 'favor' in c and any(rr['condition_id']==c and rr['curve']=='BTEC' for rr in rows):
        m=meta(c); FAV[(m['med'],sizeclass(m['size']),m['v'],m['study'])]=(meanlog(c),m['v'],L_STUDY[m['study']])
def favref(med,size,vel,study):
    sc=sizeclass(size)
    if (med,sc,vel,study) in FAV: return FAV[(med,sc,vel,study)]
    for (mm,ss,vv,st),val in FAV.items():
        if (mm,ss,vv)==(med,sc,vel): return val
    return None
def unfid(med,size,vel,IS,study):
    for c in allc:
        if 'unfav' not in c: continue
        m=meta(c)
        if m['med']==med and abs(m['size']-size)<1e-6 and m['v']==vel and m['IS']==IS and m['study']==study: return c
    return None
wb=openpyxl.load_workbook("../Manuscript/FigsExcelsUnfav/UnfavorableMaster.xlsx",data_only=True); mt=wb["Master table"]
D=[]
for r in range(4,mt.max_row+1):
    st=mt.cell(r,1).value
    if st not in ("Tong","Li") or mt.cell(r,4).value is None: continue
    med=mt.cell(r,3).value; size=float(mt.cell(r,4).value); IS=float(mt.cell(r,5).value); v=float(mt.cell(r,6).value)
    rs=str(mt.cell(r,7).value); a_s=mt.cell(r,8).value; a_m=mt.cell(r,9).value; fx=mt.cell(r,10).value
    if rs.endswith('*') or sizeclass(size) in (0.1,0.2): continue
    cu=unfid(med,size,v,IS,st); fr=favref(med,size,v,st)
    if cu is None or fr is None: continue
    mlu=meanlog(cu); mlf,vf,Lf=fr
    aplat=(-LN10*mlu*(v/L_STUDY[st]))/(-LN10*mlf*(vf/Lf))
    D.append(dict(lbl=f"{st[:2]} {med[0]} {size}um {v:.0f}md {IS:.0f}mM",med=med,IS=IS,a_s=a_s,a_m=a_m,fx=fx,
                  aplat=aplat,delta=aplat-max(a_s,a_m),dmax=max(a_s,a_m)))
D.sort(key=lambda d:(d['med'],d['fx']))
print(f"{'condition':26}{'a_s':>7}{'a_m':>7}{'a_plat':>8}{'max':>7}{'Delta':>8}{'f_x':>9}")
for d in D:
    print(f"{d['lbl']:26}{d['a_s']:7.3f}{d['a_m']:7.3f}{d['aplat']:8.3f}{d['dmax']:7.3f}{d['delta']:+8.3f}{d['fx']:9.4f}")
delta=np.array([d['delta'] for d in D]); fx=np.array([d['fx'] for d in D]); am=np.array([d['a_m'] for d in D])
lfx=np.log10(fx)
def pear(a,b):
    a=np.array(a,float); b=np.array(b,float)
    return np.corrcoef(a,b)[0,1]
from scipy.stats import spearmanr
r_df=pear(delta,fx); r_dlf=pear(delta,lfx); r_dam=pear(delta,am); r_fam=pear(fx,am); r_lfam=pear(lfx,am)
def partial(rxy,rxz,ryz): return (rxy-rxz*ryz)/math.sqrt((1-rxz**2)*(1-ryz**2))
print(f"\nn={len(D)}")
print(f"Pearson Delta vs f_x        = {r_df:+.3f}")
print(f"Pearson Delta vs log10(f_x) = {r_dlf:+.3f}")
print(f"Spearman Delta vs f_x       = {spearmanr(delta,fx).statistic:+.3f}")
print(f"Pearson Delta vs a_m        = {r_dam:+.3f}   (the confound)")
print(f"Pearson f_x vs a_m          = {r_fam:+.3f}")
print(f"Partial Delta~f_x | a_m     = {partial(r_df,r_dam,r_fam):+.3f}")
print(f"Partial Delta~log f_x | a_m = {partial(r_dlf,r_dam,r_lfam):+.3f}")
for med in ("glass","quartz"):
    sub=[d for d in D if d['med']==med]
    if len(sub)>2:
        dd=np.array([s['delta'] for s in sub]); ff=np.array([s['fx'] for s in sub])
        print(f"  within {med:6} (n={len(sub)}): Pearson Delta vs f_x = {pear(dd,ff):+.3f}, Spearman = {spearmanr(dd,ff).statistic:+.3f}")

fig,ax=plt.subplots(1,2,figsize=(12,5))
col={'glass':'#1f77b4','quartz':'#7b2d8b'}
for d in D:
    ax[0].scatter(d['fx'],d['delta'],c=col[d['med']],s=90,edgecolor='k',zorder=3)
    ax[1].scatter(d['fx'],d['aplat'],c=col[d['med']],s=90,edgecolor='k',zorder=3)
ax[0].axhline(0,color='gray',lw=1,ls='--'); ax[0].set_xscale('log')
ax[0].set_xlabel('fitted f_x'); ax[0].set_ylabel('Delta = a_plat - max(a_s,a_m)')
ax[0].set_title(f'excess vs f_x  (Pearson {r_df:+.2f}, partial|a_m {partial(r_df,r_dam,r_fam):+.2f})')
ax[1].set_xscale('log'); ax[1].set_xlabel('fitted f_x'); ax[1].set_ylabel('a_plat')
ax[1].set_title('a_plat vs f_x')
from matplotlib.lines import Line2D
leg=[Line2D([0],[0],marker='o',color='w',markerfacecolor=col[m],markeredgecolor='k',markersize=10,label=m) for m in col]
ax[0].legend(handles=leg,loc='upper left'); ax[0].grid(alpha=.3); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/fx_aplat_relation.png",dpi=140); print("\nwrote fx_aplat_relation.png")
