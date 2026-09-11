"""hydeq_engine.py -- HYDEQ (HYDRUS-EQuivalent): conventional colloid-transport model structures,
built as an explicit COMPARATOR for the interception-history model (IHOP / Serial-3).

SCOPE. This module implements the standard colloid-transport toolkit -- kinetic attachment with
detachment, depth-dependent straining, Langmuir blocking, and a two-region (dual-porosity)
formulation -- with NO near-surface interception-history population. It is deliberately kept in a
separate directory from the IHOP code (Code/*.py) and must never be imported by it.

NUMERICS ARE IDENTICAL TO Code/unfav_master_fit.py BY DESIGN. Same grid (90 cells), same time step
(dt = dx/v, unit Courant for the fast pool), same operator split (matrix-exponential reaction ->
upwind advection -> implicit dispersion), same dispersion (D = v*L/150, Pe = 150), same injection
(INJPV = T0/(L/Vref) = 2.98 PV) and same 10 PV total. Only the REACTION BLOCK differs. Any
difference in fit quality is therefore attributable to model structure, not to numerics. This is
verified in hydeq_verify.py check C, which reproduces unfav_master_fit.py to machine precision.

STATE VECTOR (4 states; unused states stay identically zero)
    Y[0] = Cf  mobile, fast region, advects at pore velocity v, dispersed
    Y[1] = Cs  mobile, slow region, advects at V_SLOW_FRAC*v, NOT dispersed  [dual porosity only]
    Y[2] = S1  solid site 1 -- reversible kinetic attachment/detachment (optionally blocked)
    Y[3] = S2  solid site 2 -- second kinetic site OR irreversible straining

GOVERNING REACTION TERMS (per cell, x = cell midpoint)
    psi(x) = ((d50 + x)/d50)^(-beta)                 depth-dependent straining multiplier
    b1     = max(0, 1 - S1/S1max)                    Langmuir blocking on site 1 (1.0 if disabled)
    w_fs   = omega*f_slow,  w_sf = omega*(1-f_slow)  two-region exchange; equilibrium Cs/Cf = f_slow/(1-f_slow)

    dCf/dt = -(k_a1*b1 + k_a2 + k_str*psi(x))*Cf + k_d1*S1 + k_d2*S2 - w_fs*Cf + w_sf*Cs
    dCs/dt = -(k_a1*b1 + k_a2)*Cs                                    + w_fs*Cf - w_sf*Cs
    dS1/dt =  k_a1*b1*(Cf + Cs) - k_d1*S1
    dS2/dt =  k_a2*(Cf + Cs) + k_str*psi(x)*Cf - k_d2*S2

CONVENTIONAL CHOICES MADE EXPLICIT (each is generous to the comparator; all are recorded so they can be
challenged rather than discovered):
  * Detachment returns colloids to the FAST region (Cf), the standard formulation.
  * Attachment acts on both mobile regions at the SAME k_a1. HYDRUS does not scale the attachment
    rate by region velocity; IHOP does (k_c = (v_ns/v)*k_f) because interception is an encounter
    rate. Using a single k_a1 gives the comparator MORE retention in the slow region than the
    interception argument would allow. Flagged, not corrected.
  * Straining filters the flowing suspension, so it acts on Cf only.
  * d50 = 510 um for BOTH media (MEASURED, Records/data_inventory.md section 4 -- grain size is
    constant across every sheet and both media), so psi(x) is IDENTICAL for glass and quartz and
    cannot encode a medium difference. Note k_str is exactly degenerate with d50^beta over the
    measured depth range (x/d50 = 19.6 to 372.5), so the fitted k_str is an amplitude, not a
    separable rate.

RETENTION PROFILE -- THREE CONVENTIONS ARE RETURNED. SETTLED 2026-08-24; canonical write-up is
Records/plateau_rs_decision.md section 5.
  rp_snap : the INSTANTANEOUS deposition rate near the end of injection -- the Johnson 2018 eq (4)
            convention, S(x) = V*t0*theta*C0*k_f*exp(-k_f*x/v), a steady rate times the full
            injection duration. This is what Code/unfav_master_fit.py uses.
  rp      : the ACCUMULATED solid phase at EXCISION (10 PV = 2.98 injection + 7 elution), divided
            by the injection duration so it passes through the identical logK amplitude. This is
            what the excised column physically holds. ** DEFAULT for the conventional models. **
  rp_inj  : accumulated to the end of INJECTION only. Provided for diagnostics. DO NOT FIT TO IT.

  Eq (4) is VALIDATED against rp: level offsets <= 0.007 log and tilts <= 0.039 log on IHOP's own
  parameters, i.e. inside the residuals being fitted (IHOP RP RMS 0.035-0.098). Two errors cancel:
  eq (4) over-pays at the outlet (it applies the end-of-injection rate over the whole injection,
  but the outlet deposited nothing until the front arrived ~1 PV in) and under-pays overall
  (10-15% of the final retained mass is deposited during the 7 PV elution, biased downstream
  because the crawl at 0.05*v needs ~20 PV to cross the column). ==> the published IHOP numbers do
  NOT require correction.

  ** rp_inj is the WORST of the three ** -- tilt -0.170 to -0.179 log against rp, i.e. 2-5x the RP
  residuals. It carries the front-arrival error without the compensating elution deposition.
  Recorded here so it is not re-proposed as "the physical one"; it is not.

  The cancellation depends on deposition being STEADY, which IHOP has (no detachment, no blocking)
  and the conventional structures do not: for a blocking model the end-of-injection rate is the
  LOWEST of the run, so eq (4) understates its retention; for a detachment model eq (4) ignores
  elution loss, so it overstates what remains. The conventional structures are therefore scored
  under rp (accumulate-to-excision), and IHOP was refit under the same convention for uniformity
  (costs moved a few percent; RP RMS unchanged to 3 decimals).

Run from Code/HYDEQ/. Author: W. P. Johnson group, 2026-08.
"""
import numpy as np
from scipy.linalg import expm
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import splu

# ---- constants shared with unfav_master_fit.py (do not diverge) ----
DAY = 86400.0
L = 0.2                      # column length, m
REV, T0, Vref = 22.801836559387397, 3.58, 0.1667
INJPV = T0 / (L / Vref)      # 2.984 pore volumes injected
NX = 90                      # cells
PE = 150.0                   # column Peclet, D = v*L/PE
THETA = {"glass": 0.375, "quartz": 0.36}
D50 = 510e-6                 # grain diameter, m -- CONSTANT for both media (data_inventory sec 4)
V_SLOW_FRAC = 0.05           # slow-region velocity as a fraction of v, PINNED (matches IHOP v_ns)
RHO_SOLID = 2650.0           # kg/m3, quartz/glass solid density (for the HYDRUS mass-basis export)


def bulk_density(medium):
    """Bulk density rho_b = (1-theta)*rho_solid, kg/m3. Needed only to express solid-phase
    concentrations on HYDRUS's per-mass-of-grains basis; the solver itself is basis-free."""
    return (1.0 - THETA[medium]) * RHO_SOLID


# --------------------------------------------------------------------------------------
# Model registry. Each entry lists the FITTED parameters in order.
# --------------------------------------------------------------------------------------
# parameter keys: k_a1 k_d1 k_a2 k_d2 k_str beta S1max f_slow omega
# (SI units: rates in 1/s; beta and f_slow dimensionless; S1max in the dimensionless solid units)
MODELS = {
    "M1_1site":        ["k_a1"],
    "M2_2site":        ["k_a1", "k_d1", "k_a2", "k_d2"],
    "M3_strain":       ["k_a1", "k_d1", "k_str", "beta"],
    "M4_dualpor":      ["k_a1", "k_d1", "f_slow", "omega"],
    "M5_strain_block": ["k_a1", "k_d1", "k_str", "beta", "S1max"],
    "M6_strain_dp":    ["k_a1", "k_d1", "k_str", "beta", "f_slow", "omega"],
    "M7_all":          ["k_a1", "k_d1", "k_str", "beta", "S1max", "f_slow", "omega"],
}
MODEL_NPAR = {k: len(v) for k, v in MODELS.items()}

# Plain-language names for tables and figures (no internal shorthand).
MODEL_LABEL = {
    "M1_1site":        "One kinetic site (irreversible)",
    "M2_2site":        "Two kinetic sites, attachment and detachment",
    "M3_strain":       "One kinetic site plus depth-dependent straining",
    "M4_dualpor":      "One kinetic site plus dual porosity (slow-region velocity pinned)",
    "M5_strain_block": "One kinetic site, straining, and Langmuir blocking",
    "M6_strain_dp":    "One kinetic site, straining, and dual porosity",
    "M7_all":          "One kinetic site, straining, blocking, and dual porosity",
}

# Fitting ranges. LINEAR parameters are beta and f_slow; everything else is fitted in log10.
LINEAR_PARS = {"beta", "f_slow"}
BOUNDS = {           # (lo, hi, seed) -- log10 of a rate in 1/s, unless in LINEAR_PARS
    "k_a1":   (-8.0, -1.0, -4.0),
    "k_d1":   (-9.0, -2.0, -6.0),
    "k_a2":   (-8.0, -1.0, -5.0),
    "k_d2":   (-9.0, -2.0, -7.0),
    "k_str":  (-8.0, -1.0, -4.5),
    "beta":   (0.0, 3.0, 0.43),      # 0.43 is the conventional literature value; fitted freely here
    "S1max":  (-6.0, 3.0, -1.0),
    "f_slow": (1e-4, 0.5, 0.01),
    "omega":  (-8.0, -2.0, -5.0),
}


def unpack(model, p):
    """Map the free-parameter vector p (fit space) to a full physical parameter dict."""
    q = dict(k_a1=0.0, k_d1=0.0, k_a2=0.0, k_d2=0.0, k_str=0.0,
             beta=0.0, S1max=np.inf, f_slow=0.0, omega=0.0)
    for name, val in zip(MODELS[model], p):
        q[name] = val if name in LINEAR_PARS else 10.0 ** val
    return q


class HydeqEngine:
    """Forward solver. One instance per column (velocity and medium fixed)."""

    def __init__(self, vmday, medium):
        self.v = vmday / DAY                 # pore velocity, m/s
        self.medium = medium
        self.dx = L / NX
        self.dt = self.dx / self.v           # unit Courant for the fast pool
        self.pv = L / self.v                 # one pore volume, s
        self.x = (np.arange(NX) + 0.5) * self.dx
        self.v_slow = V_SLOW_FRAC * self.v
        # implicit dispersion operator (applied to the fast mobile pool only, as IHOP does)
        D = self.v * L / PE
        r = D * self.dt / self.dx ** 2
        mn = (1 + 2 * r) * np.ones(NX); mn[0] = 1 + r; mn[-1] = 1 + r
        of = -r * np.ones(NX - 1)
        self._lu = splu(csc_matrix(diags([of, mn, of], [-1, 0, 1], format="csc")))

    # -- reaction ---------------------------------------------------------------------
    def _rate_matrix(self, q, psi_cell):
        """Linear 4x4 reaction matrix for one cell (blocking factor folded in by caller)."""
        ka1, kd1, ka2, kd2 = q["k_a1"], q["k_d1"], q["k_a2"], q["k_d2"]
        kstr = q["k_str"] * psi_cell
        wfs = q["omega"] * q["f_slow"]
        wsf = q["omega"] * (1.0 - q["f_slow"])
        G = np.zeros((4, 4))
        # Cf
        G[0, 0] = -(ka1 + ka2 + kstr) - wfs
        G[0, 1] = wsf
        G[0, 2] = kd1
        G[0, 3] = kd2
        # Cs
        G[1, 0] = wfs
        G[1, 1] = -(ka1 + ka2) - wsf
        # S1
        G[2, 0] = ka1
        G[2, 1] = ka1
        G[2, 2] = -kd1
        # S2
        G[3, 0] = ka2 + kstr
        G[3, 1] = ka2
        G[3, 3] = -kd2
        return G

    def _psi(self, q):
        if q["k_str"] <= 0.0:
            return np.ones(NX)
        return ((D50 + self.x) / D50) ** (-q["beta"])

    def _deriv_blocked(self, Y, q, psi, S1max):
        """Nonlinear right-hand side used only when Langmuir blocking is active."""
        b1 = np.clip(1.0 - Y[2] / S1max, 0.0, 1.0)
        ka1 = q["k_a1"] * b1
        kstr = q["k_str"] * psi
        wfs = q["omega"] * q["f_slow"]
        wsf = q["omega"] * (1.0 - q["f_slow"])
        Cf, Cs, S1, S2 = Y
        dCf = -(ka1 + q["k_a2"] + kstr) * Cf + q["k_d1"] * S1 + q["k_d2"] * S2 - wfs * Cf + wsf * Cs
        dCs = -(ka1 + q["k_a2"]) * Cs + wfs * Cf - wsf * Cs
        dS1 = ka1 * (Cf + Cs) - q["k_d1"] * S1
        dS2 = q["k_a2"] * (Cf + Cs) + kstr * Cf - q["k_d2"] * S2
        return np.vstack([dCf, dCs, dS1, dS2])

    # -- forward run ------------------------------------------------------------------
    def run(self, model, p, total_pv=10.0, nsub=1):
        """Advance the column.

        Returns tp (pore volumes), C (effluent C/C0), x, plat, and the THREE retention-profile
        conventions: rp (accumulated to excision at 10 PV -- fit to this), rp_snap (Johnson 2018
        eq (4) rate snapshot -- what unfav_master_fit.py uses), and rp_inj (accumulated to end of
        injection only -- DIAGNOSTICS ONLY, do not fit to it; see the module docstring).

        nsub = Runge-Kutta substeps for the nonlinear (blocking) path. nsub=1 agrees with nsub=8 to
        1.3e-10 in log10 on both observables and is 3x faster; verified before adopting.
        """
        q = unpack(model, p)
        psi = self._psi(q)
        blocking = np.isfinite(q["S1max"])
        if not blocking:
            E = np.stack([expm(self._rate_matrix(q, psi[i]) * self.dt) for i in range(NX)])

        nt = int(round(total_pv * NX))
        ti = INJPV * self.pv
        vs = self.v_slow / self.v
        Y = np.zeros((4, NX))
        C = np.zeros(nt)
        t = 0.0
        S_end = None; rate_end = None

        for i in range(nt):
            # 1. reaction
            if blocking:
                h = self.dt / nsub
                for _ in range(nsub):                       # RK4 substeps (nonlinear)
                    k1 = self._deriv_blocked(Y, q, psi, q["S1max"])
                    k2 = self._deriv_blocked(Y + 0.5 * h * k1, q, psi, q["S1max"])
                    k3 = self._deriv_blocked(Y + 0.5 * h * k2, q, psi, q["S1max"])
                    k4 = self._deriv_blocked(Y + h * k3, q, psi, q["S1max"])
                    Y = Y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            else:
                Y = np.einsum("xij,jx->ix", E, Y)

            # 2. effluent (flux-weighted; the slow region contributes in proportion to its velocity)
            C[i] = Y[0, -1] + vs * Y[1, -1]

            # 3. advection -- upwind, unit Courant for the fast pool; fractional for the slow pool
            Y[0, 1:] = Y[0, :-1]; Y[0, 0] = 0.0
            ys = Y[1].copy()
            Y[1, 1:] = ys[1:] - vs * (ys[1:] - ys[:-1]); Y[1, 0] = ys[0] * (1 - vs)

            t += self.dt
            if t < ti:
                Y[0, 0] += 1.0

            # 4. dispersion (fast mobile pool only)
            Y[0, :] = self._lu.solve(Y[0, :])

            # Capture the end-of-injection state. The window (0.9*ti, ti) matches
            # Code/unfav_master_fit.py exactly and, critically, stays INSIDE the injection: at
            # t >= ti the inlet cell is no longer replenished, which depresses the inlet
            # deposition rate and corrupts the first cell.
            if t < ti and t > 0.9 * ti:
                S_end = (Y[2] + Y[3]).copy()
                b1 = np.clip(1.0 - Y[2] / q["S1max"], 0.0, 1.0) if blocking else 1.0
                rate_end = (q["k_a1"] * b1 * (Y[0] + Y[1]) + q["k_a2"] * (Y[0] + Y[1])
                            + q["k_str"] * psi * Y[0])

        if S_end is None:                                    # injection ran past the window
            S_end = Y[2] + Y[3]; rate_end = np.zeros(NX)
        S_final = Y[2] + Y[3]                                # solid phase at END OF EXPERIMENT

        tp = (np.arange(nt) + 1) * self.dt / self.pv
        m = (tp > 0.5 * INJPV) & (tp < INJPV)
        return dict(tp=tp,
                    C=np.maximum(C, 1e-300),
                    x=self.x,
                    rp=np.maximum(S_final / ti, 1e-300),      # accumulated to EXCISION (10 PV)
                    # Site-resolved solid phase at excision, added 2026-08-24 so the retained-mass
                    # split can be computed WITHOUT re-deriving it by hand. S1 is the reversible
                    # (detaching) site; S2 collects the second kinetic site AND straining, which are
                    # both irreversible-by-default here. Prediction 4 in hydeq_comparison_record.md
                    # turns on this split, and asserting it without computing it is how the earlier
                    # version of that section went wrong.
                    S1=np.maximum(Y[2], 0.0), S2=np.maximum(Y[3], 0.0),
                    rp_inj=np.maximum(S_end / ti, 1e-300),    # to end of injection only -- diagnostics
                    rp_snap=np.maximum(rate_end, 1e-300),     # eq (4) snapshot convention
                    plat=float(C[m].mean()) if m.any() else float("nan"))


class IhopReferenceEngine(HydeqEngine):
    """The IHOP Serial-3 reaction block, run through this module's machinery.

    Purpose is verification only (hydeq_verify.py checks C and D): running the reference model
    through the comparator's machinery must reproduce Code/unfav_master_fit.py exactly, which proves the
    numerics are shared and any fit difference is structural. States are remapped as Y[0]=c (bulk),
    Y[1]=w (near-surface graze), Y[2]=g (crawl, at v_ns), Y[3]=a (attached).
    """

    def run_ihop(self, kf, a_s, a_m, fx, kr, vns=0.05, total_pv=10.0):
        k2 = fx * kf; kmw = a_m * kf; kmg = a_m * vns * kf
        G = np.zeros((4, 4))
        G[0, 0] -= kf; G[3, 0] += a_s * kf; G[1, 0] += (1 - a_s) * kf
        G[1, 1] -= (kmw + k2); G[3, 1] += kmw; G[2, 1] += k2
        G[2, 2] -= kmg; G[3, 2] += kmg; G[1, 2] += kr; G[2, 2] -= kr
        E = expm(G * self.dt)
        nt = int(round(total_pv * NX)); ti = INJPV * self.pv
        Y = np.zeros((4, NX)); C = np.zeros(nt); t = 0.0
        S_end = None; rate_end = None
        for i in range(nt):
            Y = E @ Y
            C[i] = Y[0, -1] + Y[1, -1] + vns * Y[2, -1]
            Y[0, 1:] = Y[0, :-1]; Y[0, 0] = 0
            Y[1, 1:] = Y[1, :-1]; Y[1, 0] = 0
            ym = Y[2].copy(); Y[2, 1:] = ym[1:] - vns * (ym[1:] - ym[:-1]); Y[2, 0] = ym[0] * (1 - vns)
            t += self.dt
            if t < ti: Y[0, 0] += 1.0
            Y[0, :] = self._lu.solve(Y[0, :]); Y[1, :] = self._lu.solve(Y[1, :])
            if t < ti and t > 0.9 * ti:      # same capture window as unfav_master_fit.py
                S_end = Y[3].copy()
                rate_end = a_s * kf * Y[0] + kmw * Y[1] + kmg * Y[2]
        tp = (np.arange(nt) + 1) * self.dt / self.pv
        m = (tp > 0.5 * INJPV) & (tp < INJPV)
        return dict(tp=tp, C=np.maximum(C, 1e-300), x=self.x,
                    rp=np.maximum(Y[3] / ti, 1e-300),         # accumulated to EXCISION (10 PV)
                    rp_inj=np.maximum(S_end / ti, 1e-300),    # to end of injection only -- diagnostics
                    rp_snap=np.maximum(rate_end, 1e-300),
                    plat=float(C[m].mean()))
