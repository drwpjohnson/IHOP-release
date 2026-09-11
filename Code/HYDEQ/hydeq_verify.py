"""hydeq_verify.py -- does the HYDEQ solver solve the equations it claims to?

This is a CODE-CORRECTNESS check, entirely separate from whether any model fits the data. If the
straining multiplier or the detachment term were mis-coded, the conventional models would fail for
the wrong reason and the whole comparison would be worthless.

  A  Irreversible one-site attachment reproduces the closed-form exponential retention profile.
     The correct target includes dispersion: the steady state of v dC/dx = D d2C/dx2 - k C is
     C ~ exp(lambda*x) with lambda = (v - sqrt(v^2 + 4*D*k))/(2*D), slightly shallower than -k/v.
  B  The reaction block alone (no advection) reproduces the exact two-state relaxation solution for
     reversible kinetics: C + S conserved, relaxation at rate (k_a1 + k_d1) to the equilibrium split.
  C  The IHOP Serial-3 reaction block run through this module reproduces Code/unfav_master_fit.py's
     engine to machine precision -- proves the reference model was transcribed correctly and that
     both models share numerics.
  D  Johnson 2018 eq (4) validated against what the excised column physically holds (accumulation
     to 10 PV, since the column is sectioned after the full injection AND elution). Also reports
     the cautionary third convention, accumulate-to-end-of-injection, which must not be fitted to.
     Canonical write-up: Records/plateau_rs_decision.md section 5.
  E  With blocking disabled, the nonlinear Runge-Kutta path reproduces the matrix-exponential path.
  F  The straining multiplier psi(x) is monotonically decreasing and matches its definition.

Run from Code/HYDEQ/:   python3 hydeq_verify.py
"""
import numpy as np
from scipy.linalg import expm
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import splu
from hydeq_engine import (HydeqEngine, IhopReferenceEngine, MODELS, LINEAR_PARS,
                          unpack, DAY, L, INJPV, NX, PE, D50)

OK = True
def report(name, passed, detail):
    global OK
    OK = OK and passed
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")


# ---------------------------------------------------------------------------------------
# Reference implementation copied verbatim from Code/unfav_master_fit.py (class Eng) so the
# transcription can be compared rather than trusted.
# ---------------------------------------------------------------------------------------
class EngReference:
    def __init__(s, vmday):
        s.v = vmday / DAY; s.dx = L / 90; s.dt = s.dx / s.v; s.pv = L / s.v
    def run(s, k1, a_s, a_m, fx, kr, vns=0.05, tot=10):
        kf = k1; k2 = fx * kf; kmw = a_m * kf; kmg = a_m * vns * kf; G = np.zeros((4, 4))
        G[0,0]-=kf; G[3,0]+=a_s*kf; G[1,0]+=(1-a_s)*kf; G[1,1]-=(kmw+k2); G[3,1]+=kmw
        G[2,1]+=k2; G[2,2]-=kmg; G[3,2]+=kmg; G[1,2]+=kr; G[2,2]-=kr
        E = expm(G*s.dt); D = s.v*L/150; r = D*s.dt/s.dx**2
        mn = (1+2*r)*np.ones(90); of = -r*np.ones(89); mn[0] = 1+r; mn[-1] = 1+r
        lu = splu(csc_matrix(diags([of,mn,of],[-1,0,1],format="csc")))
        nt = int(round(tot*90)); ti = INJPV*s.pv; c = vns
        Y = np.zeros((4,90)); C = np.zeros(nt); t = 0.; Yst = None
        for i in range(nt):
            Y = E@Y; C[i] = Y[0,-1]+Y[1,-1]+c*Y[2,-1]
            Y[0,1:] = Y[0,:-1]; Y[0,0] = 0; Y[1,1:] = Y[1,:-1]; Y[1,0] = 0
            ym = Y[2].copy(); Y[2,1:] = ym[1:]-c*(ym[1:]-ym[:-1]); Y[2,0] = ym[0]*(1-c); t += s.dt
            if t < ti: Y[0,0] += 1.
            Y[0,:] = lu.solve(Y[0,:]); Y[1,:] = lu.solve(Y[1,:])
            if t < ti and t > 0.9*ti: Yst = Y.copy()
        tp = (np.arange(nt)+1)*s.dt/s.pv; x = (np.arange(90)+0.5)*s.dx
        rp = (a_s*kf*Yst[0,:]+kmw*Yst[1,:]+kmg*Yst[2,:]); m = (tp>0.5*INJPV)&(tp<INJPV)
        return dict(tp=tp, C=np.maximum(C,1e-300), x=x, rp=np.maximum(rp,1e-300),
                    plat=float(C[m].mean()))


def pvec(model, **kw):
    """Build a fit-space parameter vector for `model` from physical values."""
    out = []
    for name in MODELS[model]:
        v = kw[name]
        out.append(v if name in LINEAR_PARS else np.log10(v))
    return np.array(out)


print("=" * 78)
print("HYDEQ solver verification")
print("=" * 78)

VEL = 4.0                       # m/day, the canonical four columns
eng = HydeqEngine(VEL, "glass")
v_ms = VEL / DAY

# ---- A ---------------------------------------------------------------------------------
print("\nA. Irreversible one-site attachment vs the closed-form exponential")
print("   Steady state of  v dC/dx = D d2C/dx2 - k C  is C ~ exp(lambda*x) with")
print("   lambda = (v - sqrt(v^2 + 4*D*k)) / (2*D).  With D = v*L/150 this is slightly shallower")
print("   than the no-dispersion value -k/v, so the dispersion-corrected form is the right target.")
for rs in (22.9, 41.5):
    ka1 = rs * v_ms                                   # k_a1 = r_s * v  (1/s)
    r = eng.run("M1_1site", pvec("M1_1site", k_a1=ka1))
    x = r["x"]; lg = np.log10(r["rp_snap"])           # instantaneous rate = the steady-state form
    D = v_ms * L / PE
    lam = (v_ms - np.sqrt(v_ms ** 2 + 4 * D * ka1)) / (2 * D)
    want = lam / np.log(10)
    sl = np.polyfit(x[10:-10], lg[10:-10], 1)[0]
    report(f"r_s={rs:5.1f}/m  RP log-slope", abs(sl - want) / abs(want) < 0.01,
           f"fitted {sl:9.4f} /m vs analytic {want:9.4f} /m  "
           f"(no-dispersion value would be {-rs/np.log(10):.4f}; rel. err {abs(sl-want)/abs(want):.2e})")
    lin = np.polyfit(x[10:-10], lg[10:-10], 1)
    resid = lg[10:-10] - np.polyval(lin, x[10:-10])
    report(f"r_s={rs:5.1f}/m  RP is log-linear", np.max(np.abs(resid)) < 5e-4,
           f"max deviation from a straight line {np.max(np.abs(resid)):.2e} log units")

# ---- B ---------------------------------------------------------------------------------
print("\nB. Reaction block (no transport) vs the exact reversible-kinetics solution")
ka1, kd1 = 3.0e-4, 1.0e-4
G = np.zeros((4, 4))
G[0, 0] = -ka1; G[2, 0] = ka1; G[0, 2] = kd1; G[2, 2] = -kd1
Y0 = np.array([1.0, 0.0, 0.0, 0.0])
for t in (100.0, 1000.0, 20000.0):
    num = (expm(G * t) @ Y0)
    lam = ka1 + kd1
    Ceq = kd1 / lam; Seq = ka1 / lam
    Cex = Ceq + (1 - Ceq) * np.exp(-lam * t)
    Sex = Seq * (1 - np.exp(-lam * t))
    err = max(abs(num[0] - Cex), abs(num[2] - Sex))
    report(f"t={t:8.0f}s  C and S", err < 1e-12,
           f"numeric C={num[0]:.12f} S={num[2]:.12f} | exact C={Cex:.12f} S={Sex:.12f} | max err {err:.2e}")
report("mass conservation C+S", abs((expm(G * 5000.0) @ Y0).sum() - 1.0) < 1e-12,
       f"sum = {(expm(G*5000.0)@Y0).sum():.15f}")

# ---- C ---------------------------------------------------------------------------------
print("\nC. IHOP Serial-3 block transcribed into this module vs Code/unfav_master_fit.py")
# model_doc Tables 1A/1B, v_ns pinned at 5%. k_r converted from /PV to 1/s by dividing by L/v.
PV_S = L / v_ms
CASES = [("glass 20 mM", 22.9, 0.133, 0.0409, 0.00248, 0.087),
         ("glass  6 mM", 22.9, 0.0171, 0.0016, 0.00070, 0.156),
         ("quartz 20 mM", 41.5, 0.0547, 0.3540, 0.00191, 0.061),
         ("quartz  6 mM", 41.5, 0.0005, 0.2584, 0.00560, 0.113)]
ref_eng = IhopReferenceEngine(VEL, "glass")
for nm, rs, a_s, a_m, fh, kr_pv in CASES:
    kf = rs * v_ms; kr = kr_pv / PV_S
    a = EngReference(VEL).run(kf, a_s, a_m, fh, kr)
    b = ref_eng.run_ihop(kf, a_s, a_m, fh, kr)
    d_rp = np.max(np.abs(np.log10(a["rp"]) - np.log10(b["rp_snap"])))
    d_bt = np.max(np.abs(np.log10(a["C"]) - np.log10(b["C"])))
    report(f"{nm}  RP snapshot and BTEC", max(d_rp, d_bt) < 1e-10,
           f"max |dlog10| RP {d_rp:.2e}, BTEC {d_bt:.2e}")

# ---- D ---------------------------------------------------------------------------------
print("\nD. Johnson 2018 eq (4) validated against what the excised column physically holds.")
print("   The column is excised after the FULL 10 PV (2.98 injection + 7 elution), and deposition")
print("   does not stop when injection stops -- 10-15% of the final retained mass arrives during")
print("   elution, biased downstream. Eq (4) has two errors of opposite sign that nearly cancel:")
print("   it over-pays at the outlet (applies the end-of-injection rate over the whole injection,")
print("   but the outlet deposited nothing until the front arrived) and under-pays overall (it")
print("   ignores the elution deposition entirely). logK is FIXED, so BOTH the level offset and")
print("   the tilt are real fit errors -- neither is absorbed.")
print("   PASS = both inside the IHOP retention-profile residuals for that column.")
RMS = {"glass 20 mM": 0.094, "glass  6 mM": 0.051, "quartz 20 mM": 0.035, "quartz  6 mM": 0.098}
for nm, rs, a_s, a_m, fh, kr_pv in CASES:
    kf = rs * v_ms; kr = kr_pv / PV_S
    b = ref_eng.run_ihop(kf, a_s, a_m, fh, kr); x = b["x"]
    d = np.log10(b["rp_snap"]) - np.log10(b["rp"])          # eq (4) vs accumulate-to-excision
    tilt = np.polyfit(x, d, 1)[0] * (x[-1] - x[0])
    report(f"{nm}  eq (4) vs excision", abs(d.mean()) < RMS[nm] and abs(tilt) < RMS[nm],
           f"level offset {d.mean():+.4f}, tilt {tilt:+.4f}, both vs RP RMS {RMS[nm]:.3f}")
print("\n   CAUTIONARY: the third convention -- accumulate to END OF INJECTION only (rp_inj) --")
print("   looks more physical than eq (4) and is NOT. It carries the front-arrival error without")
print("   the compensating elution deposition. Reported here so it is not re-proposed:")
for nm, rs, a_s, a_m, fh, kr_pv in CASES:
    kf = rs * v_ms; kr = kr_pv / PV_S
    b = ref_eng.run_ihop(kf, a_s, a_m, fh, kr); x = b["x"]
    d = np.log10(b["rp_inj"]) - np.log10(b["rp"])
    tilt = np.polyfit(x, d, 1)[0] * (x[-1] - x[0])
    print(f"       {nm}: rp_inj vs excision -- tilt {tilt:+.4f} log units "
          f"({abs(tilt)/RMS[nm]:.1f}x the RP RMS)  <-- do NOT fit to this")

# ---- E ---------------------------------------------------------------------------------
print("\nE. Nonlinear Runge-Kutta path with blocking disabled vs the matrix-exponential path")
base = dict(k_a1=8.0e-4, k_d1=2.0e-5, k_str=3.0e-4, beta=0.43)
a = eng.run("M3_strain", pvec("M3_strain", **base))
b = eng.run("M5_strain_block", pvec("M5_strain_block", S1max=1.0e6, **base))
d_rp = np.max(np.abs(np.log10(a["rp"]) - np.log10(b["rp"])))
d_bt = np.max(np.abs(np.log10(a["C"]) - np.log10(b["C"])))
report("agreement", max(d_rp, d_bt) < 1e-5, f"max |dlog10| RP {d_rp:.2e}, BTEC {d_bt:.2e}")

# ---- F ---------------------------------------------------------------------------------
print("\nF. Depth-dependent straining multiplier psi(x)")
q = unpack("M3_strain", pvec("M3_strain", **base))
psi = eng._psi(q)
want = ((D50 + eng.x) / D50) ** (-q["beta"])
report("matches its definition", np.allclose(psi, want, rtol=1e-14),
       f"max |dpsi| {np.max(np.abs(psi-want)):.2e}")
report("monotonically decreasing", np.all(np.diff(psi) < 0),
       f"psi spans {psi[0]:.4f} (x={eng.x[0]*100:.1f} cm) to {psi[-1]:.4f} (x={eng.x[-1]*100:.1f} cm), "
       f"ratio {psi[0]/psi[-1]:.2f}")
report("d50 identical for both media", D50 == 510e-6,
       f"d50 = {D50*1e6:.0f} um for glass AND quartz -- psi(x) cannot encode a medium difference")

print("\n" + "=" * 78)
print("ALL CHECKS PASSED" if OK else "*** SOME CHECKS FAILED ***")
print("=" * 78)
