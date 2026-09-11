"""
fx_vs_usec.py -- f_x collapsed onto secondary-minimum depth |U_sec| (DLVO), the single variable through
which colloid size, ionic strength, AND mineralogy all act.  Marker = medium (glass circle, quartz triangle);
color = fit cost (cool = low / reliable, warm = high / poor). Series (size vs IS) is intentionally NOT
distinguished -- |U_sec| unifies them.

|U_sec| ∝ colloid radius; it deepens with ionic strength (thinner double layer) and with quartz's larger
Hamaker constant. DLVO (sphere-plate; archive/dlvo_usec.py, Code/dlvo_four.py):
  U_vdw = -(A a)/(6h) * 1/(1+14h/lam)   (Gregory-retarded)
  U_edl = 64 pi eps0 epsr a (kT/ze)^2 tanh(ze z1/4kT) tanh(ze z2/4kT) exp(-kappa h)   (LSA)
  |U_sec| = -min_h [U_vdw+U_edl] over h>8 nm
Params: A132 glass = 7.17e-21 J, quartz = 1.96e-20 J; colloid zeta (shared) 6/20/50 mM = -0.064/-0.050/-0.040 V;
collector zeta glass = -0.070/-0.051/-0.038 V, quartz = -0.083/-0.069 V (6/20 mM); zeta from Johnson 2018 Table SI-1.

FINDING: f_x rises with |U_sec| and SATURATES (~a few kT) -- a capture-limited recruitment picture (shallow well
-> poor near-surface capture -> low f_x; deep well -> capture saturates). The size series and IS series populate
the SAME curve, unifying the two axes. Caveats (visible via the cost color): substantial scatter in the high-cost
points (0.2 um glass replicates; the two 1.1 um/20 mM points differ 3x between the Tong and Li studies), and Tong-B
(quartz 0.5 um) is a ~10x outlier -- so |U_sec| captures the DIRECTION and saturation, not a tight single curve.
NOTE: |U_sec| does NOT encode VELOCITY (the sweep side of trap-vs-sweep capture), a hidden variable here.

** 2026-08-24: the COND table below is STALE -- its f_x and cost literals predate the r_s pin and the
   mean-log plateau objective. The usec() FUNCTION is CURRENT and is the single source of that physics;
   Code/fx_trend.py imports it and supplies its own f_x from live fits. Do not read numbers off COND,
   and do not add new conditions to it -- add them in fx_trend.py. The FINDING paragraph above is also
   stage-1 vintage: "saturates (~a few kT)" is the robust part, but Tong-B is no longer treated as a
   named outlier (it passes the current cost filter on its merits), and the current closure is
   UNDER REVIEW as of 2026-08-25 -- do not quote a single U* from this file. Under the accumulated
   convention the closure is strongly sensitive to the degeneracy filter (superseded values): U* = 0.52 kT with the old
   one-sided k_r floor (which lets the non-identifiable column Li.M back in), 0.77 with Li.M removed
   by hand, 0.99-1.35 with a proper two-sided identifiability filter -- all at similar RMS
   (0.42-0.48). The dataset does not determine U*; the adopted statement is the SHAPE plus the range
   "half to a few kT" (W.P.J.). See Records/fx_trend_analysis.md. **

f_x/cost values: base-four Serial-3b; glass size series (serial3_size_fit.py); glass IS series (gl_is_fx.py);
quartz cross-check FIXED-k_f (qz_is_fx.py / serial3_quartz_check.py).  Writes fx_vs_usec.png.
Usage:  python3 fx_vs_usec.py
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

e = 1.602e-19; kB = 1.381e-23; T = 293.2; kT = kB * T
eps0 = 8.854e-12; epsr = 80.; NA = 6.022e23; z = 1.; lam = 100e-9
_h = np.linspace(2e-9, 140e-9, 70000)


def usec(ap, A, z1, z2, I_mM):
    """|U_sec|/kT for colloid radius ap (m), Hamaker A, colloid/collector zeta z1/z2 (V), IS in mM (=mol/m^3)."""
    kap = np.sqrt(2 * NA * e**2 * I_mM / (eps0 * epsr * kT))
    U = ((-A * ap / (6 * _h)) / (1 + 14 * _h / lam)
         + 64 * np.pi * eps0 * epsr * ap * (kT / (z * e))**2
         * np.tanh(z * e * z1 / (4 * kT)) * np.tanh(z * e * z2 / (4 * kT)) * np.exp(-kap * _h)) / kT
    m = _h > 8e-9
    i = np.where(m)[0][0] + np.argmin(U[m])
    return max(-U[i], 0.0)

Ag = 7.17e-21; Aq = 1.96e-20
# (label, medium, size_um, IS_mM, f_x, cost, A, zeta_colloid, zeta_collector)
# ** STALE f_x/cost -- see the 2026-08-24 note in the docstring. Kept only so the historical figure can
#    still be regenerated for comparison; the current numbers live in fx_trend.xlsx. **
COND = [("AX", "glass", 0.1, 20, 0.0006, 8.20, Ag, -0.050, -0.051), ("E", "glass", 0.2, 20, 0.0052, 4.05, Ag, -0.050, -0.051),
        ("BE", "glass", 0.2, 20, 0.0027, 3.34, Ag, -0.050, -0.051), ("BH", "glass", 0.2, 20, 0.0006, 7.80, Ag, -0.050, -0.051),
        ("BN", "glass", 0.2, 20, 0.0004, 5.50, Ag, -0.050, -0.051), ("O", "glass", 0.5, 20, 0.0055, 2.63, Ag, -0.050, -0.051),
        ("BU", "glass", 0.5, 20, 0.0038, 1.40, Ag, -0.050, -0.051), ("AQ", "glass", 1.1, 20, 0.0067, 17.29, Ag, -0.050, -0.051),
        ("CI", "glass", 2.0, 20, 0.0039, 1.15, Ag, -0.050, -0.051), ("CO", "glass", 2.0, 20, 0.0046, 10.82, Ag, -0.050, -0.051),
        ("R", "glass", 1.1, 6, 0.0009, 1.59, Ag, -0.064, -0.070), ("O_Li", "glass", 1.1, 20, 0.0023, 9.28, Ag, -0.050, -0.051),
        ("L", "glass", 1.1, 50, 0.0022, 1.80, Ag, -0.040, -0.038),  # glass IS: free-alpha_s (gl_is_fx.py)
        ("Li-Qtz6", "quartz", 1.1, 6, 0.0034, 6.0, Aq, -0.064, -0.083), ("Li-Qtz20", "quartz", 1.1, 20, 0.0029, 0.6, Aq, -0.050, -0.069),
        ("Tong-B", "quartz", 0.5, 20, 0.0268, 4.6, Aq, -0.050, -0.069)]


def main():
    U = np.array([usec(c[2] / 2 * 1e-6, c[6], c[7], c[8], c[3]) for c in COND])
    F = np.array([c[4] for c in COND]); C = np.array([c[5] for c in COND]); M = np.array([c[1] for c in COND])
    fig, ax = plt.subplots(figsize=(8.4, 5.9)); norm = LogNorm(vmin=0.5, vmax=20)
    sc = None
    for med, mk in [("glass", "o"), ("quartz", "^")]:
        s = M == med
        sc = ax.scatter(U[s], F[s], c=C[s], cmap="coolwarm", norm=norm, marker=mk, s=130, edgecolor="k", linewidth=.8, zorder=5)
    ax.scatter([], [], marker="o", facecolor="0.7", edgecolor="k", s=110, label="glass")
    ax.scatter([], [], marker="^", facecolor="0.7", edgecolor="k", s=110, label="quartz")
    cb = fig.colorbar(sc, ax=ax); cb.set_label("fit cost (½·SSE)  —  cool = reliable, warm = poor")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("secondary-minimum depth  |U_sec| / kT   (DLVO: size × ionic strength × mineralogy)")
    ax.set_ylabel("f_x  (grain-contact recruitment fraction)")
    ax.set_title("f_x vs secondary-minimum depth |U_sec|\nf_x rises with |U_sec| and saturates (capture-limited recruitment)")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout(); fig.savefig("artifacts/fx_vs_usec.png", dpi=140); print("wrote fx_vs_usec.png")
    for c, u in zip(COND, U): print(f"{c[0]:10}{c[1]:7}{u:>10.3f}{c[4]:>9.4f}{c[5]:>7.1f}")


if __name__ == "__main__":
    main()
