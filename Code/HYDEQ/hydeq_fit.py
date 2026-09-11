"""hydeq_fit.py -- fit every HYDEQ (conventional) model structure to the unfavorable Li/Tong
columns, under the SAME objective, weights, and amplitude discipline as IHOP.

WHAT BINDS BOTH MODELS (data discipline -- relax any of these and the comparison is meaningless):
    W_RP=6.0 retention-profile level, W_SHAPE=2.5 two-segment RP log-slope,
    W_PLAT=20.0 plateau mean-log target over 1.2-4 PV with PLAT_TOL=0.25 dex tolerance,
    W_TAIL=3.0 tail level (PV>4.2), W_TSLOPE=16.0 tail log-slope (PV 6-10);
    retention-profile amplitude FIXED by C0 through logK and NEVER floated;
    breakthrough floored at log10 C/C0 = -6 (detection limit) for both data and model;
    ionic strength <= 1 mM dropped; downgradient / DI / perturbation columns already excluded
    upstream by Data/extract_tidy_data.py.
All of the above are copied from Code/unfav_master_fit.py without modification.

WHAT IS RELAXED FOR THE CONVENTIONAL MODELS (physical-mechanism rules that IHOP obeys and HYDRUS
does not): detachment at constant ionic strength and flow; straining at a colloid-to-grain
diameter ratio of about 0.002; transient site-filling (blocking); and a fitted second flow region.
The conventional models are given free rein on all four. IHOP's interception rate r_s is pinned to
the favorable anchor, but that is a chemistry-independence claim, not a spare degree of freedom --
only the product r_s*alpha_s is identifiable (Records/plateau_rs_decision.md section 3), so IHOP
and the four-parameter conventional structures have the same number of free parameters.

BOTH RETENTION-PROFILE CONVENTIONS ARE RUN (W.P.J., 2026-08-24; settled in
Records/plateau_rs_decision.md section 5):
    'snap'  -- Johnson 2018 eq (4): steady deposition rate times full injection duration.
    'accum' -- accumulated solid phase at EXCISION (10 PV = 2.98 injection + 7 elution), which is
               what the excised column physically holds.
Eq (4) is validated against 'accum' to <= 0.007 log level offset and <= 0.039 log tilt on IHOP's
own parameters -- inside the residuals -- so the published IHOP numbers need no correction. The
cancellation behind that depends on deposition being steady, which the conventional structures do
not have, so they are scored under 'accum'; IHOP is refit under it too for uniformity. Do NOT fit
to the engine's rp_inj (accumulate to end of injection only) -- it is the worst of the three.

Results are written incrementally to a JSON cache, so a run can be interrupted and resumed and
already-computed entries are skipped.

Usage:
    python3 hydeq_fit.py                                    # full unfavorable set, real data
    python3 hydeq_fit.py --canon --conv accum               # canonical five-column main-text set
    python3 hydeq_fit.py --csv hydeq_working.csv            # a subset, for development
    python3 hydeq_fit.py --models M3_strain,M4_dualpor --conv accum
"""
import csv, sys, argparse, collections, warnings, functools, time
import numpy as np
warnings.filterwarnings("ignore"); print = functools.partial(print, flush=True)
from scipy.optimize import least_squares
from hydeq_engine import (HydeqEngine, IhopReferenceEngine, MODELS, MODEL_LABEL, MODEL_NPAR,
                          BOUNDS, LINEAR_PARS, DAY, L, REV, T0, Vref, INJPV, THETA)

# ---- objective weights, copied verbatim from Code/unfav_master_fit.py ----
W_RP, W_SHAPE, W_PLAT, W_TAIL, W_TSLOPE = 6.0, 2.5, 20.0, 3.0, 16.0
PLAT_TOL = 0.25
# IHOP per-medium crawl-release constant, used ONLY as an optimiser seed (it cannot bias a converged
# fit). Refreshed 2026-08-24 from the superseded necessity-fit values 5.58e-5 / 1.87e-5 to what were
# then the clean geomeans -- kr_trend_analysis.md.
# ** SUPERSEDED AGAIN 2026-08-25: the current constants are 3.75e-5 / 1.82e-5. ** Left unrefreshed on
# purpose -- these are multistart seeds, and moving a seed perturbs every converged fit for no gain.
KR_MED = {"glass": 4.46e-5, "quartz": 2.09e-5}   # SEED ONLY; superseded by 3.75e-5 / 1.82e-5

# ---- IHOP r_s anchors, copied verbatim from Code/unfav_master_fit.py ----
kB = 1.381e-23; gg = 9.806; RHO_C = 1055.; RHO_F = 998.; MU = 9.8e-4; TK = 298.2; DP = 0.510e-3
HAM = {"glass": 7.17e-21, "quartz": 1.96e-20}


def TE_rs(size_um, vel, med):
    """Tufenkji-Elimelech (2004) clean-bed single-collector efficiency, x0.77, as r_s in 1/m."""
    dc = size_um * 1e-6; U = vel / DAY; th = THETA[med]; Ui = U * th
    gam = (1 - th) ** (1 / 3); Hm = HAM[med]
    As = 2 * (1 - gam ** 5) / (2 - 3 * gam + 3 * gam ** 5 - 2 * gam ** 6)
    D = kB * TK / (6 * np.pi * MU * (dc / 2))
    NR = dc / DP; NvdW = Hm / (kB * TK)
    NG = 2 * (dc / 2) ** 2 * (RHO_C - RHO_F) * gg / (9 * MU * Ui)
    NA = Hm / (12 * np.pi * MU * (DP / 2) ** 2 * Ui); NPe = Ui * DP / D
    TE = (2.4 * As ** (1 / 3) * NR ** (-0.081) * NPe ** (-0.715) * NvdW ** 0.052
          + 0.55 * As * NR ** 1.675 * NA ** 0.125
          + 0.22 * NR ** (-0.24) * NG ** 1.11 * NvdW ** 0.053)
    return -1.5 * (gam / DP) * np.log(1 - TE) * 0.77


# ---- the canonical main-text column set (W.P.J., 2026-08-24) ----
# Five Li columns, all 1.1 um at 4 m/day, so MEDIUM and IONIC STRENGTH are the only variables -- which
# is what the comparator argument turns on. Two matched glass/quartz pairs plus the low-IS extreme:
#   R  glass  6 mM  multiexponential            -- the case a conventional structure WINS (beats IHOP)
#   V  quartz 6 mM  peaked, peak 3.0 cm          -- cleanest peak; matched to R
#   O  glass 20 mM  multiexponential            -- matched to P
#   P  quartz 20 mM non-peaking                  -- the branch FLIPS within quartz as IS rises
#   AE quartz 3 mM  peaked, peak 5.0 cm          -- peak deepens as IS falls
# Chosen for readability: with eight structures, seven-plus columns made the gallery unreadable and
# buried the structure-to-structure differences the reader is meant to compare.
# On AE's cost -- CORRECTED 2026-08-25 (W.P.J.). This comment used to read "its IHOP cost is ~38, a
# poor fit in absolute terms ... AE's weakness must be stated wherever it is used." That is a
# mischaracterisation and it should not be repeated. Under the accum convention the block
# decomposition is:
#     Li.AE   cost 48.11   rp_shape 44.24 (92%)   rp_level 3.28   RP RMS 0.135   peak 4.56 vs 5.0 cm
#     Li.AH   cost 214.34  rp_shape 209.06 (98%)  rp_level 4.68   RP RMS 0.161   peak 7.00 vs 7.0 cm
# The cost is almost entirely ONE term -- the inlet log-slope, regressed over four points on a 6 cm
# baseline at weight 2.5 -- not diffuse misfit. The retention-profile LEVEL is fine (RMS 0.135/0.161
# against a set median of 0.092 and a set worst of 0.207) and the peak DEPTH is reproduced to 0.44 cm
# and 0.00 cm. Say which term carries the penalty; do not call these columns badly fitted.
CANON_COLS = {"R", "V", "O", "P", "AE"}


def sizeclass(s):
    s = float(s); return 1.1 if 0.9 <= s <= 1.15 else round(s, 2)


# corrected 2026-09-01 -- RP row-range bug fixed (Records/CLAUDE.md); glass 1.1/4 was mean(Tong AB, Li E)
# before they were known to be one experiment, now a single value (both equal 30.2 once corrected)
FAVFIT = {("glass", 0.5, 4.0): 47.5, ("glass", 1.1, 4.0): 30.2, ("glass", 2.0, 8.0): 15.2,
          ("glass", 1.1, 2.0): 49.9, ("glass", 1.1, 8.0): 29.6, ("quartz", 0.5, 8.0): 56.7,
          ("quartz", 1.1, 2.0): 120.6, ("quartz", 1.1, 4.0): 62.3, ("quartz", 1.1, 8.0): 68.9}
SEED_CQL = {("glass", 0.2, 4.0): 49.0, ("glass", 0.1, 8.0): 62.4, ("glass", 0.2, 8.0): 39.1}


def seed_rs(med, size, vel):
    k = (med, sizeclass(size), vel)
    if k in FAVFIT: return FAVFIT[k], "fav"
    if k in SEED_CQL: return SEED_CQL[k], "favRP"
    return TE_rs(size, vel, med), "TE"


# ---- objective helpers, copied verbatim from Code/unfav_master_fit.py ----
NIN_PEAKED = 4          # inlet points used to SCORE a peaked profile


def sl(x, y, nin=None):
    """Inlet and outlet RP log-slopes.  nin=None -> historical half-split; nin=k -> first k points.

    ** PARITY FIX 2026-08-24 (W.P.J.). ** This function previously had NO `nin` argument -- it was
    always the half-split -- while IHOP had moved to the branch-aware window (plateau_rs_decision.md s6).
    IHOP and the conventional structures were therefore being scored under two DIFFERENT objectives,
    which s3 of hydeq_comparison_record.md ("what binds both models") says makes the comparison
    meaningless. The mismatch hit 3 of the 7 columns then in use -- Li.AE, Li.AH, Li.V -- i.e. exactly
    the peaked quartz columns the whole comparator exists to test. See s4b of that record.
    """
    if nin is None:
        h = len(x) // 2
        return float(np.polyfit(x[:h + 1], y[:h + 1], 1)[0]), float(np.polyfit(x[h:], y[h:], 1)[0])
    return float(np.polyfit(x[:nin], y[:nin], 1)[0]), float(np.polyfit(x[nin - 1:], y[nin - 1:], 1)[0])


def rp_branch(rlog):
    """Two-point branch test on the MEASURED profile: point2 > point1 -> peaked."""
    return "peaked" if rlog[1] > rlog[0] else "non-peaking"


def condition_branch(branches):
    """One branch per CONDITION: majority over replicate columns; ties -> 'non-peaking' (conservative)."""
    nm = sum(1 for b in branches if b == "peaked")
    return "peaked" if nm > len(branches) - nm else "non-peaking"


def branch_windows(cols, meta):
    """Map every unfavorable column -> its RP-shape window (None = half-split, 4 = peaked).

    Computed over the FULL unfavorable set, NOT over whatever subset is being fitted. That matters:
    the branch is a per-CONDITION majority over replicate columns, so a subset holding only some of a
    condition's replicates would take a different vote. With the canonical five-column set, for example,
    only V of the V/Y/AB triplet is fitted -- deciding the branch from V alone happens to give the same
    answer, but by luck rather than by construction. Deriving it from the full CSV makes the HYDEQ
    window identical to IHOP's for every column, whatever subset is displayed.
    """
    colbr = {}
    for k, m in meta.items():
        if m['chem'] != 'unfavorable': continue
        if m['IS'] is not None and m['IS'] <= 1.0: continue
        rp = cols[k]['RP']
        if len(rp) >= 3 and len(cols[k]['BTEC']) >= 3:
            colbr[k] = rp_branch(rp[:, 1])
    grp = collections.defaultdict(list)
    for k in colbr:
        mm = meta[k]
        grp[(k[0], mm['medium'], mm['size'], mm['vel'], mm['IS'])].append(k)
    NIN = {}
    for key, ks in grp.items():
        b = condition_branch([colbr[k] for k in ks])
        for k in ks:
            NIN[k] = NIN_PEAKED if b == "peaked" else None
    return NIN


def ts(pv, lc, lo=6, hi=10):
    """Shelf log-slope over pore volumes 6 to 10."""
    m = (np.asarray(pv) >= lo) & (np.asarray(pv) <= hi)
    return float("nan") if np.sum(m) < 2 else float(np.polyfit(np.asarray(pv)[m], np.asarray(lc)[m], 1)[0])


# =======================================================================================
def load(csv_path):
    """Read the tidy CSV into per-column BTEC/RP arrays plus per-column metadata."""
    rows = list(csv.DictReader(open(csv_path)))
    # GUARD, 2026-09-01: the shared master CSV was silently overwritten with a 352-row/Li-only
    # a_mg-probe subset for a month before anyone noticed -- see Records/CLAUDE.md. Fail loudly
    # instead of fitting a partial dataset in silence.
    _srcs = set(r['source'] for r in rows)
    assert len(rows) >= 1200 and 'Li' in _srcs and 'Tong' in _srcs, (
        f"CSV at {csv_path!r} looks like a subset ({len(rows)} rows, sources={_srcs}), not the full "
        "master (~1529 rows, both Li and Tong) -- refusing to fit a silently-truncated dataset.")
    cols = collections.defaultdict(lambda: {"BTEC": [], "RP": []}); meta = {}
    # BTEC_ND (2026-08-28, wired in 2026-09-01): non-detect tail points, merged into BTEC -- same
    # convention as unfav_master_fit.py, see that file's comment for the reasoning.
    for r in rows:
        curve = 'BTEC' if r['curve'] == 'BTEC_ND' else r['curve']
        k = (r['source'], r['medium'], r['workbook_col'])
        cols[k][curve].append((float(r['x']), float(r['value'])))
        meta[k] = dict(medium=r['medium'], chem=r['chemistry'], size=float(r['colloid_um']),
                       vel=float(r['velocity_mday']),
                       IS=(None if r['IS_mM'] == '' else float(r['IS_mM'])),
                       C0=float(r['C0_per_mL']))
    for k in cols:
        for cu in ("BTEC", "RP"):
            cols[k][cu] = np.array(sorted(cols[k][cu])) if cols[k][cu] else np.zeros((0, 2))
    return cols, meta


def prep(k, cols, meta, nin=None):
    """Everything the objective needs that does not depend on the model.

    `nin` is the branch-aware RP-shape window for THIS column, from branch_windows(). It is stored on
    the returned dict so residual() applies the SAME window to the model profile that was used to
    measure the data profile -- scoring the two under different windows is the parity bug this fixes.
    """
    m = meta[k]; bt = cols[k]['BTEC']; rp = cols[k]['RP']
    if len(bt) < 3 or len(rp) < 3: return None
    med = m['medium']; theta = THETA[med]; V_MS = m['vel'] / DAY
    bt = bt.copy(); bt[:, 1] = np.maximum(bt[:, 1], -6.0)      # detection floor
    pv, lc = bt[:, 0], bt[:, 1]; rx, rlog = rp[:, 0], rp[:, 1]
    si, so = sl(rx, rlog, nin)
    wm = (pv > 1.2) & (pv < 4.0)
    d = dict(nin=nin, med=med, size=m['size'], vel=m['vel'], IS=m['IS'], C0=m['C0'], V_MS=V_MS,
             logK=np.log10(REV * T0 * theta * m['C0'] * Vref),
             pv=pv, lc=lc, rx=rx, rlog=rlog, si=si, so=so,
             pvw=pv[wm] if wm.sum() else pv,
             dmean=float(lc[wm].mean()) if wm.sum() else float(lc.mean()),
             tm=pv > 4.2, sld=ts(pv, lc))
    pw = (pv > 1.2) & (pv < 4.0)
    d['plat_band'] = (float(lc[pw].min()), float(lc[pw].max())) if pw.sum() else (np.nan, np.nan)
    return d


def residual(r, d, conv):
    """The five weighted blocks. Identical in form to unfav_master_fit.py's resid()."""
    rpm = r['rp'] if conv == 'accum' else r['rp_snap']
    rl = np.interp(d['rx'], r['x'], np.maximum(rpm, 1e-300)) / d['V_MS']
    lS = d['logK'] + np.log10(np.maximum(rl, 1e-300))
    rpx = W_RP * (lS - d['rlog'])
    sm, sn = sl(d['rx'], lS, d['nin']); shp = W_SHAPE * np.array([sm - d['si'], sn - d['so']])
    mlog = np.mean(np.log10(np.maximum(np.interp(d['pvw'], r['tp'], r['C']), 1e-6)))
    dev = mlog - d['dmean']
    pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])
    tm = d['tm']
    tl = (W_TAIL * (np.log10(np.maximum(np.interp(d['pv'][tm], r['tp'], r['C']), 1e-6)) - d['lc'][tm])
          if tm.sum() else np.array([0.]))
    slm = ts(r['tp'], np.log10(np.maximum(r['C'], 1e-6)))
    tsl = W_TSLOPE * np.array([slm - d['sld'] if d['sld'] == d['sld'] else 0.])
    return np.concatenate([rpx, shp, pl, tl, tsl])


def features(r, d, conv):
    """The model_doc section 8.1 feature decomposition, model and measured side by side."""
    rpm = r['rp'] if conv == 'accum' else r['rp_snap']
    lS_at = d['logK'] + np.log10(np.maximum(np.interp(d['rx'], r['x'], rpm) / d['V_MS'], 1e-300))
    rpRMS = float(np.sqrt(np.mean((lS_at - d['rlog']) ** 2)))
    # retention-profile branch: an interior maximum means peaked
    lS_full = d['logK'] + np.log10(np.maximum(rpm / d['V_MS'], 1e-300))
    imax = int(np.argmax(lS_full)); peak_m = float(r['x'][imax]) if imax > 0 else 0.0
    imax_d = int(np.argmax(d['rlog'])); peak_d = float(d['rx'][imax_d]) if imax_d > 0 else 0.0
    lcm = np.log10(np.maximum(r['C'], 1e-6))
    def at(p): return float(np.interp(p, r['tp'], lcm))
    def datat(p): return float(np.interp(p, d['pv'], d['lc']))
    mm = (r['tp'] > 6) & (r['tp'] <= 10); dm = (d['pv'] > 6) & (d['pv'] <= 10)
    plat_m = float(np.mean(np.log10(np.maximum(np.interp(d['pvw'], r['tp'], r['C']), 1e-6))))
    lo, hi = d['plat_band']
    # branch_m/branch_d: literal values "peaked"/"non-peaking" are a SERIALIZED OUTPUT BOUNDARY --
    # they are cached into hydeq_results.json (and any --cache path, e.g. hydeq_fullset_stats.json) and
    # then read back by string equality in hydeq_fullset_analysis.py (bd[c]=="peaked"/"non-peaking")
    # and written verbatim as xlsx cell values by hydeq_export.py. Renamed 2026-09-01 (W.P.J.): "monotone"
    # is retired project-wide, including at this output boundary and all files downstream of it.
    return dict(rpRMS=rpRMS,
                branch_m=("peaked" if imax > 0 else "non-peaking"), peak_m=peak_m,
                branch_d=("peaked" if imax_d > 0 else "non-peaking"), peak_d=peak_d,
                plat_m=plat_m, plat_lo=lo, plat_hi=hi,
                plat_in=(lo - PLAT_TOL <= plat_m <= hi + PLAT_TOL),
                cliff_m=at(3.5) - at(5.0), cliff_d=datat(3.5) - datat(5.0),
                shelf_m=float(lcm[mm].mean()) if mm.any() else np.nan,
                shelf_d=float(d['lc'][dm].mean()) if dm.any() else np.nan,
                sslope_m=ts(r['tp'], lcm), sslope_d=d['sld'])


def fit_hydeq(model, d, conv, nstart=3, seed=0, maxnfev=80):
    """Fit one conventional structure to one column."""
    eng = HydeqEngine(d['vel'], d['med'])
    names = MODELS[model]
    lo = np.array([BOUNDS[n][0] for n in names]); hi = np.array([BOUNDS[n][1] for n in names])
    s0 = np.array([BOUNDS[n][2] for n in names])
    rng = np.random.default_rng(seed)
    best = None; bestp = None
    for j in range(nstart):
        start = s0 if j == 0 else np.clip(s0 + rng.normal(0, 0.6, len(s0)) * (hi - lo) / 6, lo, hi)
        try:
            rr = least_squares(lambda p: residual(eng.run(model, p), d, conv),
                               start, bounds=(lo, hi), max_nfev=maxnfev)
        except Exception:
            continue
        if best is None or rr.cost < best:
            best = rr.cost; bestp = rr.x
    if bestp is None: return None
    r = eng.run(model, bestp)
    f = features(r, d, conv)
    return dict(cost=float(best), p=bestp, names=names, npar=len(names), res=r, **f)


def fit_ihop(d, conv, maxnfev=80):
    """IHOP Serial-3 under the identical objective, as the reference line."""
    eng = IhopReferenceEngine(d['vel'], d['med'])
    rs0, src = seed_rs(d['med'], d['size'], d['vel'])
    kk = rs0 * d['V_MS']; krs = np.log10(KR_MED[d['med']])
    lo = [-3.3, -3.3, np.log10(1e-4), np.log10(1e-6)]
    hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0), np.log10(.1)]
    best = None
    for s0 in ([-1.5, -1., np.log10(.005), krs], [-.5, -.3, np.log10(.02), krs],
               [-2.3, -1.5, np.log10(.001), krs - 0.5]):
        rr = least_squares(lambda p: residual(
            eng.run_ihop(kk, 1 - 10 ** p[0], 10 ** p[1], 10 ** p[2], 10 ** p[3]), d, conv),
            s0, bounds=(lo, hi), max_nfev=maxnfev)
        if best is None or rr.cost < best.cost: best = rr
    a_s = 1 - 10 ** best.x[0]
    r = eng.run_ihop(kk, a_s, 10 ** best.x[1], 10 ** best.x[2], 10 ** best.x[3])
    f = features(r, d, conv)
    return dict(cost=float(best.cost), npar=4, rs=rs0, rs_src=src, a_s=a_s,
                a_m=10 ** best.x[1], fx=10 ** best.x[2], kr=10 ** best.x[3], res=r, **f)


# =======================================================================================
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="../Data/LiTong_experimental_data_tidy.csv")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--conv", default="snap,accum")
    ap.add_argument("--only", default="", help="substring filter on the column key")
    ap.add_argument("--canon", action="store_true",
                    help="restrict to the canonical five-column main-text set (see CANON_COLS)")
    ap.add_argument("--cache", default="hydeq_results.json",
                    help="incremental results cache; already-computed entries are skipped")
    ap.add_argument("--nstart", type=int, default=3)
    ap.add_argument("--maxnfev", type=int, default=80)
    args = ap.parse_args()

    import json, os
    CACHE = args.cache
    store = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    def ckey(conv, k, mdl):
        """Cache key. INCLUDES the RP-shape window.

        Without the window in the key, the 2026-08-24 parity fix would have been defeated by its own
        cache: every entry in hydeq_results.json was computed under the old always-half-split objective,
        and would have been served back as if current. A cached result is only reusable if the objective
        that produced it is the same objective. Old-format keys simply never match and are recomputed.
        """
        w = "w4" if NIN.get(k) else "wH"
        return "|".join([conv, k[0], k[1], k[2], mdl, w])

    def save():
        with open(CACHE, "w") as fh: json.dump(store, fh, indent=1)

    def keep(rec):
        """Strip the heavy arrays before caching; keep parameters and features."""
        return {kk: (list(map(float, vv)) if isinstance(vv, np.ndarray) else vv)
                for kk, vv in rec.items() if kk not in ("res",)}

    cols, meta = load(args.csv)
    keys = [k for k, m in meta.items()
            if m['chem'] == 'unfavorable' and not (m['IS'] is not None and m['IS'] <= 1.0)]

    # Branch windows come from the FULL unfavorable set, before any subsetting -- see branch_windows().
    NIN = branch_windows(cols, meta)

    if args.canon:
        keys = [k for k in keys if k[2] in CANON_COLS and k[0] == "Li"]
        missing = CANON_COLS - {k[2] for k in keys}
        if missing:
            sys.exit(f"canonical set incomplete -- missing columns {sorted(missing)} in {args.csv}")
    if args.only: keys = [k for k in keys if args.only in "|".join(map(str, k))]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    convs = [c.strip() for c in args.conv.split(",") if c.strip()]

    npk = sum(1 for k in keys if NIN.get(k))
    print(f"columns: {len(keys)}   structures: {len(models)}   conventions: {convs}")
    print(f"RP-shape window: {npk}/{len(keys)} of the fitted columns are branch-aware "
          f"({NIN_PEAKED} inlet points); branch decided over the FULL {len(NIN)}-column set")
    for k in sorted(keys):
        print(f"    {k[0]}.{k[2]:3s} {meta[k]['medium']:6s} {meta[k]['size']}um "
              f"{meta[k]['vel']:.0f}md {meta[k]['IS']:.0f}mM  "
              f"window={'4-point inlet' if NIN.get(k) else 'half-split'}")
    for conv in convs:
        print("\n" + "=" * 118)
        print(f"RETENTION-PROFILE CONVENTION: {conv}"
              f"   ({'accumulated to excision, 10 PV' if conv=='accum' else 'Johnson 2018 eq (4) rate snapshot'})")
        print("=" * 118)
        hdr = (f"{'column':28s} {'structure':52s} {'par':>3s} {'cost':>9s} {'rpRMS':>7s} "
               f"{'branch':>13s} {'peak cm':>8s} {'plat':>6s} {'cliff':>6s} {'shelf':>6s}")
        for k in sorted(keys):
            d = prep(k, cols, meta, nin=NIN.get(k))
            if d is None: continue
            tag = f"{k[0]}.{k[1][:2]}.{k[2]} {d['size']}um {d['vel']:.0f}md {d['IS']:.0f}mM"
            print("\n" + hdr); print("-" * 118)

            def show(label, r, npar, secs=None):
                print(f"{'':28s} {label:52s} {npar:3d} {r['cost']:9.3f} {r['rpRMS']:7.3f} "
                      f"{r['branch_m']:>13s} {r['peak_m']*100:8.2f} "
                      f"{'in' if r['plat_in'] else 'OUT':>6s} {r['cliff_m']:6.2f} "
                      f"{r['shelf_m']:6.2f}" + (f"   [{secs:.1f}s]" if secs else ""))

            ck = ckey(conv, k, "IHOP")
            if ck not in store:
                t0 = time.time(); ih = fit_ihop(d, conv, maxnfev=args.maxnfev)
                store[ck] = keep(ih); store[ck]['secs'] = time.time() - t0; save()
            ih = store[ck]
            print(f"{tag:28s}"[:28] + " " + f"{'IHOP Serial-3 (reference)':52s} {ih['npar']:3d} "
                  f"{ih['cost']:9.3f} {ih['rpRMS']:7.3f} {ih['branch_m']:>13s} "
                  f"{ih['peak_m']*100:8.2f} {'in' if ih['plat_in'] else 'OUT':>6s} "
                  f"{ih['cliff_m']:6.2f} {ih['shelf_m']:6.2f}")
            print(f"{'':28s} {'   MEASURED DATA':52s} {'':3s} {'':9s} {'':7s} "
                  f"{ih['branch_d']:>13s} {ih['peak_d']*100:8.2f} "
                  f"{'--':>6s} {ih['cliff_d']:6.2f} {ih['shelf_d']:6.2f}")
            for mdl in models:
                ck = ckey(conv, k, mdl)
                if ck not in store:
                    t0 = time.time()
                    fr = fit_hydeq(mdl, d, conv, nstart=args.nstart, maxnfev=args.maxnfev)
                    if fr is None:
                        print(f"{'':28s} {MODEL_LABEL[mdl]:52s}  FIT FAILED"); continue
                    store[ck] = keep(fr); store[ck]['secs'] = time.time() - t0; save()
                show(MODEL_LABEL[mdl], store[ck], store[ck]['npar'], store[ck].get('secs'))
    save()
    print("\nDone.  Results cached in " + CACHE)
