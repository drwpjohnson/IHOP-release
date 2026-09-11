"""
dlvo_kramers_size.py -- REAL DLVO/Kramers prediction of the crawl->wall release k_r vs colloid size,
and the k_r-vs-size figure (serial3_kr_vs_size.png).

Point of the figure: the fitted k_r (crawl->wall release / reentrainment) is size- and velocity-
INDEPENDENT for glass (one shared constant fits all 10 size x velocity columns at +9% cost), and a
per-medium constant for quartz (~3x below glass). Traditional single-colloid escape from the DLVO
secondary minimum (Kramers) predicts a STEEP size dependence and a hugely different magnitude -- both
refuted here. This script computes that real DLVO/Kramers prediction from first principles and overlays
it on the fitted values.

DLVO (sphere-plate; grain >> colloid), 20 mM glass, from archive/dlvo_usec.py; zeta from Johnson 2018
Table SI-1:
  van der Waals (Gregory-retarded):  U_vdw(h) = -(A*a)/(6h) * 1/(1 + 14h/lam)
  electrostatic (LSA, const. pot.):  U_edl(h) = 64*pi*eps0*epsr*a*(kT/(z e))^2 * G1*G2 * exp(-kappa h)
                                     with Gi = tanh(z e zeta_i / (4 kT))
  Debye parameter:                   kappa = sqrt(2 NA e^2 I / (eps0 epsr kT)) ;  Debye length = 1/kappa
  secondary-minimum depth:           |U_sec| = -min_h [ U_vdw + U_edl ]  over h > 8 nm
Because both terms scale linearly with colloid radius a, |U_sec| is proportional to a (colloid size).

KRAMERS escape rate (overdamped; well width ~ Debye length):
  D(a) = kT / (6 pi mu a)                         (Stokes-Einstein; ~1/a)
  k_r(a) = (D / kappa^-2) * exp(-|U_sec|/kT)      (absolute)
The plotted curve is ANCHORED to the glass shared constant (5.58e-5 /s) at 1.1 um so its SIZE SLOPE is
comparable to the data; the absolute single-colloid rate is ~2.1e8x higher (a second refutation).

RESULT: |U_sec| runs 0.18 -> 3.55 kT over 0.1-2.0 um (1.95 kT at 1.1 um, secondary min at h~18.5 nm);
the anchored curve has a 584x size swing -- vs the flat, size-independent fitted k_r.

Data plotted (fitted values; provenance in comments below):
  glass per-column free-k_r  <- serial3_size_fit.py  (RS = clean-bed r_s per size; k_r free per column)
  glass shared k_r = 5.58e-5/s (fits all 10, +9.0%)  <- serial3_size_fit.py joint fit
  quartz k_r (FIXED-k_f)  <- serial3_quartz_check.py with k_f pinned at anchor r_s

Usage:  python3 dlvo_kramers_size.py        # prints |U_sec|(a), k_r(a); writes serial3_kr_vs_size.png
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- DLVO constants & 20 mM glass parameters (archive/dlvo_usec.py) ----------------
e = 1.602e-19; kB = 1.381e-23; T = 293.2; kT = kB * T
eps0 = 8.854e-12; epsr = 80.0; NA = 6.022e23; z = 1.0; mu = 1.0e-3      # water viscosity, Pa s
A = 7.17e-21                          # Hamaker A132, glass (J)
lam = 100e-9                          # vdW retardation length (m)
I = 20.0                              # ionic strength (mol/m^3 = 20 mM)
zeta_col = -0.050                     # CML colloid zeta (V), Johnson 2018
zeta_glass = -0.051                   # glass collector zeta (V), Johnson 2018
kappa = np.sqrt(2 * NA * e**2 * I / (eps0 * epsr * kT)); kinv = 1.0 / kappa   # Debye length
_h = np.linspace(2e-9, 120e-9, 60000)


def usec_kT(a):
    """Secondary-minimum depth |U_sec|/kT for a colloid of radius a (m) against a flat grain, 20 mM glass."""
    U = ((-A * a / (6 * _h)) / (1 + 14 * _h / lam)
         + 64 * np.pi * eps0 * epsr * a * (kT / (z * e))**2
         * np.tanh(z * e * zeta_col / (4 * kT)) * np.tanh(z * e * zeta_glass / (4 * kT))
         * np.exp(-kappa * _h)) / kT
    m = _h > 8e-9
    i = np.where(m)[0][0] + np.argmin(U[m])
    return max(-U[i], 0.0)


def D(a):        return kT / (6 * np.pi * mu * a)                 # Stokes-Einstein diffusivity
def kr_abs(a):   return (D(a) / kinv**2) * np.exp(-usec_kT(a))    # absolute Kramers escape rate (/s)

A_REF = 0.55e-6                        # 1.1 um diameter -> radius, the anchor size
KR_GLASS = 5.58e-5                     # glass shared constant (/s), serial3_size_fit.py
KR_QUARTZ = 1.75e-5                    # quartz mean (Li 1.1 um, FIXED-k_f), serial3_quartz_check.py
_kref = kr_abs(A_REF)
def kr_anchored(a): return KR_GLASS * kr_abs(a) / _kref           # curve anchored to glass const at 1.1 um

# ---------------- fitted k_r data (for the scatter) ----------------
# glass per-column free-k_r (diameter um, velocity m/day, k_r /s) -- serial3_size_fit.py
GLASS = [(0.1, 8, 6.67e-5), (0.2, 4, 3.30e-5), (0.2, 8, 2.84e-5), (0.2, 8, 8.71e-5),
         (0.2, 8, 9.23e-5), (0.5, 4, 1.98e-5), (0.5, 8, 5.68e-5), (1.1, 4, 7.19e-5),
         (2.0, 8, 9.08e-5), (2.0, 8, 1.43e-4)]
# quartz FIXED-k_f cross-check (diameter um, k_r /s) -- serial3_quartz_check.py, k_f pinned
QZ_LI = [(1.1, 1.03e-5), (1.1, 2.46e-5)]        # reliable
QZ_TONG_B = (0.5, 6.74e-5)                       # fair


def main():
    print(f"Debye length = {kinv*1e9:.2f} nm   |U_sec|(1.1um)/kT = {usec_kT(A_REF):.3f}")
    print(f"absolute kr(1.1um) = {kr_abs(A_REF):.2e}/s  (obs {KR_GLASS:.2e}/s -> ~{kr_abs(A_REF)/KR_GLASS:.1e}x too high)")
    print(f"{'diam_um':>8}{'|Usec|/kT':>11}{'kr_abs/s':>12}{'kr_anchored/s':>15}")
    for d in [0.1, 0.2, 0.5, 1.1, 2.0]:
        a = d / 2 * 1e-6
        print(f"{d:>8}{usec_kT(a):>11.3f}{kr_abs(a):>12.2e}{kr_anchored(a):>15.2e}")
    swing = kr_abs(0.05e-6) / kr_abs(1.0e-6)
    print(f"size swing 0.1->2.0 um (anchored) = {swing:.0f}x ;  quartz {KR_GLASS/KR_QUARTZ:.1f}x below glass")

    # ---------------- figure ----------------
    dg = np.logspace(np.log10(0.1), np.log10(2.0), 60)
    pred = np.array([kr_anchored(d / 2 * 1e-6) for d in dg])
    fig, ax = plt.subplots(figsize=(9, 6))
    for d, v, k in GLASS:
        ax.scatter(d, k, s=70, color="#1f77b4" if v == 4 else "#2a9d8f", edgecolor="k", zorder=5)
    ax.axhline(KR_GLASS, color="#1f77b4", lw=2, ls="--",
               label=f"glass shared k_r = {KR_GLASS:.2e}/s (fits all 10, +9.0%)")
    ax.plot(dg, pred, color="grey", lw=1.6, ls=":",
            label=f"DLVO/Kramers single-colloid escape ({swing:.0f}x over 0.1-2.0 um) - REFUTED")
    for d, k in QZ_LI:
        ax.scatter(d, k, s=90, marker="s", color="#7b2d8b", edgecolor="k", zorder=6)
    ax.scatter(*QZ_TONG_B, s=70, marker="s", color="#c39bd3", edgecolor="k", zorder=6,
               label="quartz Tong 0.5um (fair)")
    ax.axhline(KR_QUARTZ, color="#7b2d8b", lw=2, ls="--",
               label=f"quartz k_r = {KR_QUARTZ:.2e}/s (Li 1.1um, ~{KR_GLASS/KR_QUARTZ:.1f}x below glass)")
    ax.scatter([], [], s=70, color="#1f77b4", edgecolor="k", label="glass 4 m/day")
    ax.scatter([], [], s=70, color="#2a9d8f", edgecolor="k", label="glass 8 m/day")
    ax.scatter([], [], s=90, marker="s", color="#7b2d8b", edgecolor="k", label="quartz Li 1.1um (reliable, fixed-k_f)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("colloid diameter (um)"); ax.set_ylabel("fitted k_r (/s)")
    ax.set_xticks([0.1, 0.2, 0.5, 1.1, 2.0]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1.1", "2.0"])
    ax.set_title("Serial-3: fitted crawl->wall release k_r vs colloid size\n"
                 "glass = near-universal constant (size- & velocity-independent); quartz ~3.2x below (DLVO medium);\n"
                 f"single-colloid DLVO/Kramers escape ({swing:.0f}x swing) refuted")
    ax.legend(fontsize=8, loc="lower left"); ax.grid(alpha=0.3, which="both")
    fig.tight_layout(); fig.savefig("artifacts/serial3_kr_vs_size.png", dpi=140)
    print("wrote serial3_kr_vs_size.png")


if __name__ == "__main__":
    main()
