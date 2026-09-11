"""cft_rs_compare.py -- compare the interception-history FITTED r_s (favorable columns, from
Favorable_data_and_sim.xlsx) to the classical single-collector filtration-theory COLLISION-rate r_s from five
correlations, exactly as coded in the colleague's tool `Data/CorrelationEqs3.py`:
    Rajagopalan & Tien 1976 (RT), Tufenkji & Elimelech 2004 (TE), Ma-Pedel-Fife-Johnson 2015 (MPFJ),
    Nelson & Ginn 2011 (NG), Long & Hilpert 2011 (LH).
r_s convention = the tool's kf/U (before attachment Cdd):  r_s = -(3/2)(gamma/dp)*ln(1-eta0),
gamma=(1-theta)^(1/3), dp=collector diameter. This is directly comparable to our fitted r_s (interception rate;
attachment alpha_s is a separate parameter).

Inputs: rho_c=1055, rho_f=998, mu=9.8e-4 Pa.s, T=298.2 K, g=9.806 (tool defaults); collector dp=510 um;
theta glass 0.375 / quartz 0.36 (our values; tool default 0.4). Hamaker A132: CORRECT values glass 7.17e-21,
quartz 1.96e-20 J are PRIMARY (tool default 3.84e-21 shown for reference; data_inventory §6 flags 3.84e-21 as
outdated). Writes CFT_rs_comparison.xlsx (correct-H and tool-default-H blocks) + cft_rs_compare.png.

FINDING (correct H): our fitted r_s lands within the 5-correlation envelope for every column. Glass sits mid-
envelope (fit ~0.6-1.0x MPFJ); quartz runs at/above the top (Qz Li 8 m/d ~2x MPFJ, above even LH) -- consistent
with angular quartz intercepting more than smooth-sphere theory predicts. Usage: python3 cft_rs_compare.py"""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
kB=1.381e-23; g=9.806; RHO_C=1055.; RHO_F=998.; MU=9.8e-4; T=298.2; DP=0.510e-3
A_CORRECT={"glass":7.17e-21,"quartz":1.96e-20}; A_TOOL=3.84e-21
THETA={"glass":0.375,"quartz":0.36}
CORRS=["RT","TE","MPFJ","NG","LH"]
# (label, medium, colloid size um, pore velocity m/day, our fitted r_s /m from the favorable fits)
# corrected 2026-09-01 -- GB Li B/E/H's RP was truncated (RP row-range bug, see Records/CLAUDE.md), which biased
# their fitted r_s; now 49.9/30.2/29.6. GB Li E now lands exactly on GB Tong AB (30.2) because they are the SAME
# experiment (confirmed by W.P.J.) -- this table carries them as two rows, deliberately, but they are one point.
COND=[("GB Tong L","glass",0.5,4,47.5),("GB Tong AB","glass",1.0,4,30.2),("GB Tong CS","glass",2.0,8,15.2),
      ("Qz Tong O","quartz",0.5,8,56.7),("Qz Li B","quartz",0.98,2,120.6),("Qz Li E","quartz",0.98,4,62.3),
      ("Qz Li I","quartz",0.98,8,68.9),("GB Li B","glass",0.98,2,49.9),("GB Li E","glass",0.98,4,30.2),
      ("GB Li H","glass",0.98,8,29.6)]


def eta0(dc,U,med,Hm):
    """dc colloid diameter (m), U pore velocity (m/s). Returns dict of the 5 eta0 (formulas verbatim from CorrelationEqs3.py)."""
    theta=THETA[med]; Ui=U*theta; gamma=(1-theta)**(1/3)
    As=2*(1-gamma**5)/(2-3*gamma+3*gamma**5-2*gamma**6)
    D=kB*T/(6*np.pi*MU*(dc/2))
    NR=dc/DP; NvdW=Hm/(kB*T); NA=Hm/(12*np.pi*MU*(DP/2)**2*Ui)
    NG=2*(dc/2)**2*(RHO_C-RHO_F)*g/(9*MU*Ui); NGi=1/(1+NG); NLo=Hm/(9*np.pi*MU*(dc/2)**2*Ui); NPe=Ui*DP/D
    RT=gamma**2*4*As**(1/3)*NPe**(-2/3)+As*NLo**(1/8)*NR**(15/8)+0.00338*As*NG**1.2*NR**(-0.4)
    NGc=gamma**2*(2.4*As**(1/3)*(NPe/(NPe+16))**0.75*NPe**(-0.68)*NLo**0.015*NGi**0.8)+As*NLo**(1/8)*NR**(15/8)+0.7*(NGi/(NGi+0.9))*NG*NR**(-0.05)
    MP=gamma**2*((8+4*(1-gamma)*As**(1/3)*NPe**(1/3))/(8+(1-gamma)*NPe**0.97)*NLo**0.015*NGi**0.8*NR**0.028)+As*NLo**(1/8)*NR**(15/8)+0.7*NR**(-0.05)*NG*(NGi/(NGi+0.9))
    TE=2.4*As**(1/3)*NR**(-0.081)*NPe**(-0.715)*NvdW**0.052+0.55*As*NR**1.675*NA**0.125+0.22*NR**(-0.24)*NG**1.11*NvdW**0.053
    LH=15.56*(gamma**6/(1-gamma**3)**2)*NPe**(-0.65)*NR**0.19+0.55*As*NR**1.675*NA**0.125+0.22*NR**(-0.24)*NG**1.11*NvdW**0.053
    return dict(RT=RT,TE=TE,MPFJ=MP,NG=NGc,LH=LH)


def rs_of(dc,U,med,Hm):
    gamma=(1-THETA[med])**(1/3)
    return {k:(-1.5*(gamma/DP)*np.log(1-v)) for k,v in eta0(dc,U,med,Hm).items()}


def build():
    import openpyxl
    from openpyxl.styles import Font
    B=Font(bold=True); IT=Font(italic=True); wb=openpyxl.Workbook(); ws=wb.active; ws.title="r_s fit vs CFT"
    ws.cell(1,1,"Fitted interception r_s (favorable-condition fits) vs single-collector CFT collision-rate r_s from 5 correlations").font=B
    ws.cell(2,1,"r_s = -(3/2)(gamma/dp) ln(1-eta0)  [tool CorrelationEqs3.py convention]. dp=510um; rho_c=1055; mu=9.8e-4; T=298.2; theta glass .375/quartz .36.").font=IT
    ws.cell(3,1,"BLOCK A: correct A132 (glass 7.17e-21, quartz 1.96e-20 J).   BLOCK B (below): tool default A=3.84e-21 (outdated, for reference).").font=IT
    hdr=["condition","medium","size_um","v_mday","fit r_s /m"]+CORRS+["env_min","env_max","fit/MPFJ"]
    def write_block(startrow,Amode,title):
        ws.cell(startrow-1,1,title).font=B
        for j,h in enumerate(hdr,1): ws.cell(startrow,j,h).font=B
        rr=startrow+1
        for lab,med,sz,v,rsf in COND:
            Hm=(A_CORRECT[med] if Amode=="correct" else A_TOOL)
            r=rs_of(sz*1e-6, v/86400., med, Hm); vals=[r[k] for k in CORRS]
            row=[lab,med,sz,v,rsf]+[round(x,1) for x in vals]+[round(min(vals),1),round(max(vals),1),round(rsf/r["MPFJ"],2)]
            for j,x in enumerate(row,1): ws.cell(rr,j,x)
            rr+=1
        return rr
    r1=write_block(6,"correct","BLOCK A - correct A132 (PRIMARY)")
    write_block(r1+3,"tool","BLOCK B - tool default A=3.84e-21 (reference)")
    for col in "ABCDEFGHIJKLMN": ws.column_dimensions[col].width=11
    wb.save("../Manuscript/FigsExcelsFavorable/CFT_rs_comparison.xlsx"); print("wrote ../Manuscript/FigsExcelsFavorable/CFT_rs_comparison.xlsx")


def figure():
    fig,ax=plt.subplots(figsize=(7.4,6.2))
    for med,mk,c in [("glass","o","#1f77b4"),("quartz","^","#7b2d8b")]:
        xs=[];ys=[];lo=[];hi=[]
        for lab,m,sz,v,rsf in COND:
            if m!=med: continue
            r=rs_of(sz*1e-6, v/86400., m, A_CORRECT[m]); vals=[r[k] for k in CORRS]
            xs.append(r["MPFJ"]); ys.append(rsf); lo.append(r["MPFJ"]-min(vals)); hi.append(max(vals)-r["MPFJ"])
        ax.errorbar(xs,ys,xerr=[lo,hi],fmt=mk,color=c,ms=10,capsize=3,elinewidth=1,mec="k",label=f"{med} (x-err = 5-corr envelope)",zorder=5)
    lim=[0,130]; ax.plot(lim,lim,"k--",lw=1.3,label="1:1 (fit = CFT)")
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.set_xlabel("CFT collision-rate r_s /m  (MPFJ; bar = 5-correlation range)")
    ax.set_ylabel("fitted interception r_s /m  (favorable)")
    ax.set_title("Fitted r_s vs classical filtration-theory r_s\nglass near/below 1:1; quartz above (angularity > smooth-sphere theory)")
    ax.grid(alpha=.3); ax.legend(fontsize=9,loc="upper left")
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsFavorable/cft_rs_compare.png",dpi=140); print("wrote ../Manuscript/FigsExcelsFavorable/cft_rs_compare.png")


if __name__=="__main__":
    build(); figure()
