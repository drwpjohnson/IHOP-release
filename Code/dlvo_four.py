"""|U_sec| for all four conditions (GB/Qtz x 6/20 mM), 1 um colloid (a_p=0.5um).
DLVO = sphere-plate LSA-EDL (const-potential, Hogg-Healy-Fuerstenau form) + Gregory-retarded vdW,
same forms as dlvo_usec.py. zeta from Johnson 2018 Table SI-1; A132 glass 7.17e-21, quartz 1.96e-20 J.
Compare exp(-|U_sec|/kT) pattern to the fitted g->w k_rel (per PV)."""
import numpy as np
e=1.602e-19; kB=1.381e-23; T=293.2; kT=kB*T
eps0=8.854e-12; epsr=80.0; NA=6.022e23; z=1.0
a_p=0.5e-6; lam=100e-9                       # 1 um colloid (Johnson2018 SI-2 a1=5e-7)
def kappa(I):   return np.sqrt(2*NA*e**2*I/(eps0*epsr*kT))   # I mol/m^3
def Gam(zp):    return np.tanh(z*e*zp/(4*kT))
def U_edl(h,z1,z2,kap): return 64*np.pi*eps0*epsr*a_p*(kT/(z*e))**2*Gam(z1)*Gam(z2)*np.exp(-kap*h)
def U_vdw(h,A): return (-A*a_p/(6*h))/(1+14*h/lam)
h=np.linspace(1e-9,150e-9,300000)
# name, I(mol/m3), zeta_colloid, zeta_collector, A132, fitted k_rel (/PV)
C=[("GB 6mM ",6.0,-0.064,-0.070,7.17e-21,0.18),
   ("GB 20mM",20.0,-0.050,-0.051,7.17e-21,0.10),
   ("Qtz 6mM",6.0,-0.064,-0.083,1.96e-20,0.13),
   ("Qtz 20mM",20.0,-0.050,-0.069,1.96e-20,0.07)]
print(f"a_p={a_p*1e6:.2f}um  T={T}K  kT={kT:.3e}J")
print(f"{'cond':9}{'k-1(nm)':>8}{'h_sec(nm)':>10}{'|U_sec|kT':>10}{'exp(-U)':>9}{'k_rel/PV':>9}{'A_impl/s':>10}")
rows=[]
for name,I,z1,z2,A,kr in C:
    kap=kappa(I); u=(U_vdw(h,A)+U_edl(h,z1,z2,kap))/kT
    # secondary min: deepest local min for h> primary-barrier; if no barrier, min over h>3nm
    ipk=np.argmax(u[h<20e-9]); hb=h[ipk]
    reg=h>max(hb, 3e-9)
    isec=np.where(reg)[0][0]+np.argmin(u[reg]); depth=max(-u[isec],0.0); hsec=h[isec]
    kr_s=kr/4320.0                         # per-PV -> per-s (PVtime=L/v=0.2/(4/86400)=4320s)
    A_impl=kr_s/np.exp(-depth)             # implied Kramers prefactor
    rows.append((name,depth,kr,kr_s,A_impl))
    print(f"{name:9}{1/kap*1e9:8.2f}{hsec*1e9:10.2f}{depth:10.3f}{np.exp(-depth):9.4f}{kr:9.3f}{A_impl:10.2e}")
print("\n--- pattern checks (k_rel should track exp(-|U_sec|/kT) if a single prefactor A holds) ---")
d={r[0]:r for r in rows}
def ratio(a,b,i): return d[a][i]/d[b][i]
for (a,b) in [("GB 6mM ","GB 20mM"),("Qtz 6mM","Qtz 20mM"),("GB 6mM ","Qtz 6mM"),("GB 20mM","Qtz 20mM")]:
    kexp=np.exp(-d[a][1])/np.exp(-d[b][1]); kfit=d[a][2]/d[b][2]
    print(f"  {a} / {b}:  exp(-U) ratio {kexp:6.2f}   fitted k_rel ratio {kfit:6.2f}")
