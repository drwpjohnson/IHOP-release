"""fx_trend.py -- trends in the focus/recruitment fraction f_x (near-surface graze -> grain-contact crawl),
its two necessity tests, and the f_x(|U_sec|) closure, under the CURRENT Serial-3 objective.

REFACTORED 2026-08-24 (W.P.J. approved). The Box copy of this script could not produce the distributed
fx_trend.xlsx at all: it wrote 4 sheets with different names, from f_x literals HARD-CODED out of the
pre-master scripts (Serial-3b base, serial3_size_fit.py, quartz on fixed-k_f). The distributed workbook
has 5 sheets and newer numbers (e.g. Tong.AX f_x 0.0006 in the script vs 0.0011 in the workbook), so the
generator was some other script that is not in Code/. Everything is now computed live from the engine in
unfav_master_fit.py, on the corrected objective (mean-log plateau target PV 1.2-4 +-0.25 dex W_PLAT=20;
branch-aware RP-shape inlet window, plateau_rs_decision.md s6).

** CLOSURE HISTORY -- FOUR STAGES; STAGE 4 IS CURRENT AND ADOPTS A RANGE, NOT A VALUE. **
    STAGE 1, SUPERSEDED   fmax = 0.0033, U* = 0.42 kT, x/1.62, n=7  -- fx_usec_closure.py docstring and
        fx_trend_analysis.md. Fitted when r_s was still allowed to FLOAT within a 0.25 dex window, under a
        cost<=3.5 reliability cut calibrated on the old objective's cost scale.
    STAGE 2, SUPERSEDED   fmax = 0.0088, U* = 2.00 kT, x/2.57, n=12 -- the 'f_x(Usec) closure REVISED'
        sheet of the distributed fx_trend.xlsx. Arose, per W.P.J., when r_s was PINNED to the favorable-
        condition anchor instead of floating. That is a change to the fitted f_x values themselves, not to
        how they were filtered afterwards: with r_s free over ~0.25 dex, r_s absorbed part of the retention
        that f_x now has to carry, and it did so unevenly across |U_sec|, the shallow-well columns having
        the most room to trade. Pinning r_s moves f_x, and the closure fitted to it stretched.
    STAGE 3, SUPERSEDED   fmax = 0.0047, U* = 0.80 kT, x/2.48, n=15. Stage 2's mechanism is
        accepted; its NUMBER is not, because it rested on one non-identifiable point. See below.
        Correct as far as it went, but fitted under the eq (4) snapshot and with a ONE-SIDED filter.
    STAGE 4, CURRENT (2026-08-25). Two changes: the retention profile moved to the ACCUMULATED solid
        phase at excision (the eq (4) injection-window snapshot ignores 7.0 of the 10 PV and is
        retired -- see unfav_master_fit.py), and the degeneracy filter became TWO-SIDED. The second
        change matters more than the first: the closure is DOMINATED BY THE FILTER.
              old one-sided k_r floor      n=16  fmax 0.0036  U* 0.52 kT  RMS 0.440   (superseded)
              same, Li.M removed by hand   n=15  fmax 0.0047  U* 0.77 kT  RMS 0.394   (superseded)
              f_x-identifiability  <== USED HERE
                                           n=16  fmax 0.0060  U* 0.99 kT  RMS 0.439
              k_r-identifiability          n=13  fmax 0.0061  U* 1.20 kT  RMS 0.421
              k_r-identifiability, by cond n=10  fmax 0.0064  U* 1.35 kT  RMS 0.430
        RMS 0.39-0.48 throughout: the data do not choose between them.
        ** ADOPTED: the SHAPE plus the RANGE "half to a few kT" (W.P.J., 2026-08-25). NOT a value. **
        Audit trail: 0.52 kT was provisionally accepted that day, on the strength of pore-scale
        simulations putting the onset of real secondary-minimum effect near 0.5 kT. It was then found
        to be an artefact -- under accum, Li.M's k_r no longer rails at 1e-6 but flies to 5.6e-3 at
        unchanged cost, so the one-sided floor stopped catching it and it re-entered the closure at
        the DEEPEST well (|U_sec| 6.57 kT) with f_x = 0.00055 against replicates at 0.00427 and
        0.00151, pulling the plateau down. The external agreement made a contaminated number look
        right; that is exactly when corroboration is most dangerous. Acceptance withdrawn, range
        adopted instead.

WHY STAGE 2 WAS NOT KEPT. Refitting stage 2's own published 12 points reproduces it exactly (fmax 0.0088,
U* 2.00, RMS 0.411, x/2.57 -- an exact digit-for-digit match, which is also this script's validation that
its closure fitter is correct). But leave-one-out on that same set shows the result is carried by a SINGLE
point, Li-Qtz20:
      as published                fmax 0.0088   U* 2.00 kT
      minus Li-Qtz20 only         fmax 0.0038   U* 0.59 kT   <-- collapses back to ~stage 1
      minus CI only               fmax 0.0070   U* 1.51 kT   (largest other single influence)
No other point does that. And in the current per-column fits, that condition's elevated f_x comes from
column Li.M, whose free k_r sits ON the 1e-6 optimiser bound: f_x = 0.21 at cost 0.72. That is the
f_x<->k_r degeneracy, not a measurement -- with k_r pinned to a bound, f_x absorbs everything, and the fit
earns a LOW cost precisely because it is degenerate, so no cost filter can catch it. Li.M is the same
column kr_trend.py already drops as a floor-hit when forming its 'clean' k_r geomean. Applying that
identical threshold symmetrically to f_x removed Li.M and Tong.U and yielded stage 3.
  ** That threshold was ONE-SIDED and has since failed -- see FX_PEN_MIN below and the stage-4 note.
  Li.M is now caught by its f_x pinning penalty instead, which does not care which bound a degenerate
  parameter drifts to. **

WHAT IS AND IS NOT ESTABLISHED. Robust: f_x RISES with |U_sec| and SATURATES, and the size series and the
IS series populate one curve -- the direction and the fact of saturation survive every variant tried. NOT
established by this dataset: the saturation SCALE (0.5-1.4 kT across defensible degeneracy filters under
accum; 0.6-2 kT counting older variants) or the plateau HEIGHT (0.004-0.009). Quote the closure as a
shape with a stated band and the range "half to a few kT", never as a precise U*.
  TENSION TO KEEP VISIBLE: part2_apriori_alpha_machinery.md s87 expects grain-contact transfer g to
  saturate by ~2 kT. That was cited in support of stage 2 and it does NOT support stage 3. It is left
  standing as a disagreement between the a-priori machinery and the fitted closure rather than quietly
  dropped now that it points the other way; if the ~2 kT expectation is right, the reading is that the
  fitted f_x cannot resolve the deep end, not that the machinery is wrong.

WHAT IT DOES
  * fits every unfavorable column free (a_s, a_m, f_x, k_r; r_s pinned) -- the SAME free fits kr_trend.py
    performs, so f_x and k_r here are from one common set, not two separate fitting runs;
  * necessity vs SIZE  (glass Tong, 8 m/day, 20 mM): f_x free vs pinned to the series geometric mean;
  * necessity vs IONIC STRENGTH (glass Li, 1.1 um, 4 m/day, 6/20/50 mM): same test;
  * |U_sec| per column by DLVO, imported from fx_vs_usec.py (NOT re-implemented -- one copy of that physics);
  * saturating closure f_x = fmax*(1-exp(-|U_sec|/U*)) refit in log10 on the reliable points.

TWO CONVENTIONS ARE REPORTED FOR THE CLOSURE, because the distributed workbook mixed them: it used
PER-COLUMN rows for glass but PER-CONDITION MEANS for quartz, and for glass 1.1 um 20 mM it kept only
column AQ out of the three replicates AE/AK/AQ. That mixture is arbitrary. This script reports the closure
fitted (a) per column, uniformly, and (b) per condition, uniformly -- and quotes neither as "the" answer
without the other. See the 'f_x(Usec) closure' sheet.

NOT INCLUDED, AND WHY -- TWO ZETA GAPS, BOTH ON QUARTZ. Every column is fitted and appears in the f_x
table, but four carry no |U_sec| and so cannot enter the closure:
  * quartz Li 1.1 um at 3 mM (AE, AH) -- Johnson 2018 Table SI-1 gives colloid/collector zeta at 6 / 20 /
    50 mM only, nothing at 3 mM. Since W.P.J. has asked that 3 mM be part of the manuscript, this is a real
    gap that needs a measured or interpolated 3 mM zeta.
  * quartz Tong 0.5 um at 50 mM (H, R) -- Table SI-1 gives QUARTZ collector zeta at 6 and 20 mM only.
Do NOT invent a value to fill either. Note both gaps sit on quartz, so the closure's quartz support is
thinner than the column count suggests.

Usage:  python3 fx_trend.py  [--out fx_trend.xlsx]
        Run from Code/, with the cleaned CSV in ../Data/ and unfav_master_fit.py + fx_vs_usec.py alongside.
        NOTE this script takes NO --master argument, unlike alpha_trends.py: it does not read
        UnfavorableMaster.xlsx at all. It re-fits every column itself, because the two necessity tests
        need PINNED refits that no stored workbook contains. The free fits it produces are the same ones
        the master and kr_trend.py use, so the three stay consistent by construction rather than by
        copying numbers between files.
"""
import argparse, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.styles import Font
from openpyxl.formatting.rule import ColorScaleRule

exec(open("unfav_master_fit.py").read().split("# ---- fit all unfavorable")[0])  # engine, seed_rs, loaders
from fx_vs_usec import usec as _usec_raw                                          # DLVO, single source

A_HAM = {"glass": 7.17e-21, "quartz": 1.96e-20}
ZETA_COLLOID = {6.0: -0.064, 20.0: -0.050, 50.0: -0.040}
ZETA_COLLECTOR = {"glass": {6.0: -0.070, 20.0: -0.051, 50.0: -0.038},
                  "quartz": {6.0: -0.083, 20.0: -0.069}}
REL_COST = 15.0        # reliability cut on fit cost for the closure (revised; see docstring)
REL_COST_OLD = 3.5     # superseded cut, printed for sensitivity only
# ---- DEGENERACY FILTER, two-sided (W.P.J., 2026-08-25) ----------------------------------------
# A column whose k_r is not identifiable is DEGENERATE in the {f_x, v_ns, k_r} cluster: f_x becomes
# the only remaining lever and absorbs everything, so its VALUE is not meaningful. Such a fit earns
# a LOW cost precisely because it is degenerate, so the cost filter cannot catch it.
#
# ** THIS WAS A ONE-SIDED FLOOR TEST (k_r <= 1.5e-6) AND IT FAILED THE MOMENT THE CONVENTION
#    CHANGED. ** Under the accumulated-solid-phase convention Li.M's k_r no longer rails at the 1e-6
# lower bound; it flies to 5.63e-3 at an unchanged cost (0.72). The floor test stopped catching it,
# Li.M re-entered the closure at |U_sec| = 6.57 kT -- the DEEPEST well in the set -- carrying
# f_x = 0.00055 against its own replicates at the identical |U_sec| (Li.P 0.00427, Li.S 0.00151).
# One non-identifiable point at the deep end dragged the plateau down and shortened U*:
#       with Li.M    n=16   fmax 0.0036   U* 0.52 kT   RMS 0.440   (superseded filter)
#       without      n=15   fmax 0.0047   U* 0.77 kT   RMS 0.394   (superseded) <-- better fit, too
# That is the SAME column, through the SAME degeneracy, that produced the spurious 2.00 kT closure
# at stage 2 -- in the opposite direction. It has now corrupted this closure twice.
#
# The criterion is IDENTIFIABILITY, not which bound the parameter happened to drift to.
#
# WHICH parameter's identifiability, though? For a closure IN f_x the test must be f_x's OWN: if
# pinning f_x to the all-column geomean costs this column essentially nothing, its f_x is
# unconstrained and it cannot inform the closure. I first used the k_r penalty here by analogy with
# kr_trend.py -- the wrong test for this quantity, since a column can be uninformative about k_r
# while still pinning f_x down, and vice versa. The k_r penalty is kept as a sensitivity variant
# (U* 1.20 per column, 1.35 per condition) and is reported in the docstring, not used as the filter.
FX_PEN_MIN = 1.0       # percent excess cost from pinning f_x; below this the column cannot vote
KR_PEN_MIN = 1.0       # same test on k_r; reported as a sensitivity variant, not the default
KR_FLOOR = 1.5e-6      # retained ONLY to flag floor-hits in the workbook; NOT the closure filter


def usec_for(medium, size_um, IS):
    """|U_sec|/kT, or None where no zeta exists at that ionic strength."""
    if IS is None: return None
    z1 = ZETA_COLLOID.get(float(IS)); z2 = ZETA_COLLECTOR[medium].get(float(IS))
    if z1 is None or z2 is None: return None
    return float(_usec_raw(size_um / 2 * 1e-6, A_HAM[medium], z1, z2, float(IS)))


def fit(k, fx_fixed=None, nin=None, kr_fixed=None):
    """Fit one column. 4 free params (a_s, a_m, f_x, k_r) unless one is pinned:
    fx_fixed -> 3 params (a_s, a_m, k_r);  kr_fixed -> 3 params (a_s, a_m, f_x).
    The kr_fixed branch exists to measure k_r IDENTIFIABILITY per column (KR_PEN_MIN).

    Objective identical to unfav_master_fit.py and kr_trend.py -- mean-log plateau target, branch-aware
    RP-shape window. The pinned variant leaves a_s/a_m/k_r free to compensate, so the cost increase is
    attributable to f_x and not to a loss of total flexibility.
    """
    m = meta[k]; bt = cols[k]['BTEC'].copy(); rp = cols[k]['RP']
    if len(bt) < 3 or len(rp) < 3: return None
    med = m['medium']; size = m['size']; vel = m['vel']; C0 = m['C0']; theta = THETA[med]; V_MS = vel / DAY
    eng = Eng(vel); krs = np.log10(KR_MED[med]); logK = np.log10(REV * T0 * theta * C0 * Vref)
    rs0, src = seed_rs(med, size, vel); kk = rs0 * V_MS
    bt[:, 1] = np.maximum(bt[:, 1], -6.0)
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]; si, so = sl(rx, rlog, nin)
    wm = (pv > 1.2) & (pv < 4.0); pvw = pv[wm] if wm.sum() else pv
    dmean = float(lc[wm].mean()) if wm.sum() else float(lc.mean())
    tm = pv > 4.2; sld = ts(pv, lc)

    def resid(p):
        a_s = 1 - 10 ** p[0]; am = 10 ** p[1]
        if fx_fixed is not None:
            fx = fx_fixed; krr = 10 ** p[2]
        elif kr_fixed is not None:
            fx = 10 ** p[2]; krr = kr_fixed
        else:
            fx = 10 ** p[2]; krr = 10 ** p[3]
        r = eng.run(kk, a_s, am, fx, krr)
        rl = np.interp(rx, r['x'], np.maximum(r['rp'], 1e-300)) / V_MS
        lS = logK + np.log10(np.maximum(rl, 1e-300))
        rpx = W_RP * (lS - rlog); sm, sn = sl(rx, lS, nin); shp = W_SHAPE * np.array([sm - si, sn - so])
        mlog = np.mean(np.log10(np.maximum(np.interp(pvw, r['tp'], r['C']), 1e-6))); dev = mlog - dmean
        pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])
        tl = (W_TAIL * (np.log10(np.maximum(np.interp(pv[tm], r['tp'], r['C']), 1e-6)) - lc[tm])
              if tm.sum() else np.array([0.]))
        slm = ts(r['tp'], np.log10(np.maximum(r['C'], 1e-6)))
        tsl = W_TSLOPE * np.array([slm - sld if sld == sld else 0.])
        return np.concatenate([rpx, shp, pl, tl, tsl])

    if fx_fixed is not None:
        lo = [-3.3, -3.3, np.log10(1e-6)]; hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(.1)]
        starts = [[-1.5, -1., krs], [-.5, -.3, krs], [-2.3, -1.5, krs - 0.5]]
    elif kr_fixed is not None:
        lo = [-3.3, -3.3, np.log10(1e-4)]; hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0)]
        starts = [[-1.5, -1., np.log10(.005)], [-.5, -.3, np.log10(.02)], [-2.3, -1.5, np.log10(.001)]]
    else:
        lo = [-3.3, -3.3, np.log10(1e-4), np.log10(1e-6)]
        hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0), np.log10(.1)]
        starts = [[-1.5, -1., np.log10(.005), krs], [-.5, -.3, np.log10(.02), krs],
                  [-2.3, -1.5, np.log10(.001), krs - 0.5]]
    best = None
    for s0 in starts:
        rr = least_squares(resid, s0, bounds=(lo, hi), max_nfev=80)
        if best is None or rr.cost < best.cost: best = rr
    fx = fx_fixed if fx_fixed is not None else 10 ** best.x[2]
    kr = (kr_fixed if kr_fixed is not None
          else 10 ** best.x[2 if fx_fixed is not None else 3])
    return dict(fx=fx, kr=kr, cost=float(best.cost), size=size, vel=vel, IS=m['IS'], med=med,
                tag=k[0] + '.' + k[2], study=k[0])


def closure(U, F):
    """f_x = fmax*(1-exp(-|U_sec|/U*)) fit in log10. Returns (fmax, U*, log10RMS, band, n)."""
    U = np.asarray(U, float); F = np.asarray(F, float)
    def res(p): return np.log10(p[0] * (1 - np.exp(-U / p[1]))) - np.log10(F)
    best = None
    for s0 in ([0.004, 0.5], [0.005, 1.0], [0.003, 0.3], [0.009, 2.0], [0.02, 4.0]):
        r = least_squares(res, s0, bounds=([1e-4, 0.05], [0.2, 30]), max_nfev=400)
        if best is None or r.cost < best.cost: best = r
    rms = float(np.sqrt(np.mean(res(best.x) ** 2)))
    return float(best.x[0]), float(best.x[1]), rms, 10 ** rms, len(U)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fx_trend.xlsx")
    args = ap.parse_args()

    US = [k for k, m in meta.items() if m['chem'] == 'unfavorable' and (m['IS'] is None or m['IS'] > 1)]
    # branch per CONDITION by majority over replicates, exactly as unfav_master_fit.py / kr_trend.py
    colbr = {}
    for k in US:
        rp = cols[k]['RP']
        if len(rp) >= 3 and len(cols[k]['BTEC']) >= 3: colbr[k] = rp_branch(rp[:, 1])
    _grp = collections.defaultdict(list)
    for k in colbr:
        mm = meta[k]; _grp[(k[0], mm['medium'], mm['size'], mm['vel'], mm['IS'])].append(k)
    NIN = {}
    for key, ks in _grp.items():
        b = condition_branch([colbr[k] for k in ks])
        for k in ks: NIN[k] = NIN_PEAKED if b == 'peaked' else None  # matches renamed condition_branch (exec-imported above)
    print(f"branch-aware window: {sum(1 for k in NIN if NIN[k])}/{len(NIN)} columns on {NIN_PEAKED} inlet points")

    FREE = {}
    for k in US:
        d = fit(k, None, nin=NIN.get(k))
        if d: FREE[k] = d
    print(f"free fits: {len(FREE)} columns")

    def gm(v): return float(np.exp(np.mean(np.log(np.maximum(np.asarray(v, float), 1e-12)))))

    # ---------- necessity tests ----------
    def necessity(sel, label):
        ks = [k for k in FREE if sel(FREE[k])]
        F = gm([FREE[k]['fx'] for k in ks])
        rows = []; tf = tp = 0.
        for k in sorted(ks, key=lambda z: (FREE[z]['size'], FREE[z]['IS'] or 0)):
            cf = FREE[k]['cost']; cp = fit(k, F, nin=NIN.get(k))['cost']
            tf += cf; tp += cp
            rows.append((FREE[k]['tag'], FREE[k]['size'], FREE[k]['vel'], FREE[k]['IS'],
                         round(FREE[k]['fx'], 5), round(cf, 2), round(cp, 2),
                         round(100 * (cp - cf) / max(cf, 1e-9), 1)))
        pct = 100 * (tp - tf) / tf
        print(f"{label}: pin f_x={F:.4f} -> free {tf:.2f} pinned {tp:.2f} = +{pct:.1f}%  (n={len(ks)})")
        return dict(F=F, rows=rows, free=tf, pin=tp, pct=pct, n=len(ks))

    SIZE = necessity(lambda d: d['med'] == 'glass' and d['study'] == 'Tong' and d['vel'] == 8 and d['IS'] == 20,
                     "size necessity (glass Tong, 8 m/d, 20 mM)")
    ISN = necessity(lambda d: d['med'] == 'glass' and d['study'] == 'Li' and abs(d['size'] - 1.1) < .15 and d['vel'] == 4,
                    "IS necessity (glass Li, 1.1 um, 4 m/d)")

    # ---------- |U_sec| per column, and per condition ----------
    # IDENTIFIABILITY: refit each column with a parameter PINNED and record the excess cost. A column
    # the pin costs nothing cannot inform a closure in that parameter -- see FX_PEN_MIN above.
    # KRPIN is kept only so the k_r sensitivity variant can be recomputed on demand.
    _gk = [FREE[k]['kr'] for k in FREE if FREE[k]['med'] == 'glass']
    _qk = [FREE[k]['kr'] for k in FREE if FREE[k]['med'] == 'quartz']
    KRPIN = {'glass': gm(_gk), 'quartz': gm(_qk)}
    # Only the f_x penalty is computed in the run path -- it is the operative filter, and adding the
    # k_r penalty as well pushes this script past ~3 min. The k_r-identifiability variant (U* 1.20
    # per column, 1.35 per condition) is recorded in the docstring; recompute with kr_fixed=KRPIN
    # if it is needed again.
    FXPIN = gm([FREE[k]['fx'] for k in FREE])
    KRPEN = {}; FXPEN = {}
    for k in FREE:
        cf = FREE[k]['cost']
        FXPEN[k] = 100.0 * (fit(k, nin=NIN.get(k), fx_fixed=FXPIN)['cost'] - cf) / max(cf, 1e-9)
        KRPEN[k] = float('nan')

    percol = []
    for k in sorted(FREE, key=lambda z: (FREE[z]['med'], FREE[z]['size'], FREE[z]['IS'] or 0)):
        d = FREE[k]; U = usec_for(d['med'], d['size'], d['IS'])
        percol.append(dict(d, U=U, krpen=KRPEN[k], fxpen=FXPEN[k]))
    cond = collections.defaultdict(list)
    for r in percol:
        cond[(r['study'], r['med'], r['size'], r['vel'], r['IS'])].append(r)
    percond = []
    for key, rs in sorted(cond.items(), key=lambda z: (z[0][1], z[0][2], z[0][4] or 0)):
        ok = [r for r in rs if r.get('fxpen', 1e9) >= FX_PEN_MIN]   # drop degenerate columns first
        percond.append(dict(study=key[0], med=key[1], size=key[2], vel=key[3], IS=key[4],
                            fx=(gm([r['fx'] for r in ok]) if ok else None),
                            cost=(float(np.mean([r['cost'] for r in ok])) if ok else float('nan')),
                            kr=(gm([r['kr'] for r in ok]) if ok else 0.0),
                            krpen=(float(np.mean([r['krpen'] for r in ok])) if ok else 0.0),
                            fxpen=(float(np.mean([r['fxpen'] for r in ok])) if ok else 0.0),
                            U=rs[0]['U'], n=len(ok), ndrop=len(rs) - len(ok),
                            tag="/".join(r['tag'].split('.')[1] for r in rs)))

    def rel(rows, cut):
        # Degeneracy test is the f_x PINNING PENALTY, not the old one-sided k_r floor -- see
        # FX_PEN_MIN. Per-condition rows carry the mean penalty of their columns.
        return [r for r in rows if r['U'] is not None and r['fx'] is not None
                and r['cost'] <= cut and r.get('fxpen', 1e9) >= FX_PEN_MIN]
    CL_COL = closure([r['U'] for r in rel(percol, REL_COST)], [r['fx'] for r in rel(percol, REL_COST)])
    CL_CND = closure([r['U'] for r in rel(percond, REL_COST)], [r['fx'] for r in rel(percond, REL_COST)])
    CL_OLD = closure([r['U'] for r in rel(percol, REL_COST_OLD)], [r['fx'] for r in rel(percol, REL_COST_OLD)])
    for nm, c in (("per column, cost<=15", CL_COL), ("per condition, cost<=15", CL_CND),
                  ("per column, cost<=3.5 (superseded cut)", CL_OLD)):
        print(f"closure {nm:42s}: fmax={c[0]:.4f}  U*={c[1]:.2f} kT  RMS={c[2]:.3f}  band x/{c[3]:.2f}  n={c[4]}")
    print("distributed workbook 'closure REVISED' for comparison: fmax=0.0088  U*=2.00 kT  band x/2.57  n=12")

    # ================= workbook =================
    B = Font(bold=True); IT = Font(italic=True)
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    def hd(ws, r, vals):
        for j, v in enumerate(vals, 1): ws.cell(r, j, v).font = B

    ws = wb.create_sheet("f_x fitted")
    ws.cell(1, 1, "Fitted focus/recruitment fraction f_x -- CURRENT fits (r_s pinned; a_s/a_m/f_x/k_r free; mean-log plateau; branch-aware RP window; -6 floor; IS>1 mM)").font = B
    ws.cell(2, 1, "Every unfavorable column, fitted live -- the SAME free fits kr_trend.py runs, so f_x and k_r come from one common set. |U_sec| is blank where no zeta exists: quartz at 3 mM and quartz at 50 mM (Johnson 2018 Table SI-1 covers colloid/collector at 6/20/50 mM but quartz collector at 6/20 mM only).").font = IT
    hd(ws, 3, ["study", "medium", "col", "size_um", "v_mday", "IS_mM", "f_x", "k_r /s", "cost",
               "|U_sec|_kT", "RP window", "usable for closure?"])
    for i, r in enumerate(percol, 4):
        # Same test as rel() and as the 'f_x vs Usec' sheet -- f_x's own pinning penalty.
        if r['U'] is None: why = "no -- no zeta at this ionic strength"
        elif r['cost'] > REL_COST: why = f"no -- cost > {REL_COST:.0f}"
        elif r['fxpen'] < FX_PEN_MIN:
            why = f"NO -- pinning f_x costs {r['fxpen']:.1f}%: f_x not identifiable here (degenerate)"
        else: why = "yes"
        for j, v in enumerate([r['study'], r['med'], r['tag'], r['size'], r['vel'], r['IS'],
                               round(r['fx'], 5), float(f"{r['kr']:.3e}"), round(r['cost'], 2),
                               ("" if r['U'] is None else round(r['U'], 3)),
                               ("4-point inlet" if NIN.get(next(k for k in FREE if FREE[k]['tag'] == r['tag'])) else "half-split"),
                               why], 1):
            ws.cell(i, j, v)
    for c, w in zip("ABCDEFGHIJKL", [7, 8, 10, 8, 8, 7, 10, 11, 9, 11, 14, 44]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("f_x by condition")
    ws.cell(1, 1, "f_x per CONDITION -- geometric mean over replicate columns, mean cost").font = B
    ws.cell(2, 1, "Uniform rule for both media. The distributed workbook mixed conventions (per-column for glass, per-condition for quartz, and only AQ of the three glass 1.1 um 20 mM replicates); that mixture is arbitrary and is not reproduced.").font = IT
    ws.cell(3, 1, f"Degenerate columns -- those where pinning f_x costs less than {FX_PEN_MIN:.0f}%, i.e. f_x is not identifiable -- are dropped BEFORE averaging; see 'n dropped'. A condition with every column degenerate has no usable f_x. (This test replaced a one-sided 'k_r on the 1e-6 bound' test on 2026-08-25, which stopped catching Li.M once its k_r flew UP instead of railing down.)").font = IT
    hd(ws, 4, ["study", "medium", "cols", "size_um", "v_mday", "IS_mM", "n_used", "n dropped (degenerate)",
               "f_x (geomean)", "cost (mean)", "|U_sec|_kT"])
    for i, r in enumerate(percond, 5):
        for j, v in enumerate([r['study'], r['med'], r['tag'], r['size'], r['vel'], r['IS'], r['n'], r['ndrop'],
                               ("none usable" if r['fx'] is None else round(r['fx'], 5)),
                               ("" if r['fx'] is None else round(r['cost'], 2)),
                               ("" if r['U'] is None else round(r['U'], 3))], 1):
            ws.cell(i, j, v)
    for c, w in zip("ABCDEFGHIJK", [7, 8, 12, 8, 8, 7, 8, 21, 14, 12, 11]): ws.column_dimensions[c].width = w

    for nm, N, ttl, sub in (("size necessity v8_20mM", SIZE,
                             "f_x NECESSITY vs SIZE at constant v = 8 m/day, 20 mM (glass Tong 0.1-2.0 um)",
                             "f_x carries size information: pinning it to one constant across the size series costs this much, with a_s/a_m/k_r still free to compensate."),
                            ("f_x vs IS 1.1um_4md", ISN,
                             "f_x NECESSITY vs IONIC STRENGTH at constant 1.1 um, 4 m/day (glass Li 6/20/50 mM)",
                             "Pin is the SERIES GEOMETRIC MEAN, matching the size sheet and kr_trend.py's convention. NOTE: the distributed workbook pinned this series to 0.0017 -- the 20 mM column's own f_x -- which is why its 20 mM row showed a delta of exactly 0. That anchored choice is not reproduced here.")):
        ws = wb.create_sheet(nm)
        ws.cell(1, 1, ttl).font = B
        ws.cell(2, 1, f"f_x free vs PINNED to F = {N['F']:.4f}: total free {N['free']:.2f}, pinned {N['pin']:.2f} -> +{N['pct']:.1f}%  (n = {N['n']} columns).").font = IT
        ws.cell(3, 1, sub).font = IT
        hd(ws, 5, ["col", "size_um", "v_mday", "IS_mM", "f_x_free", "cost_free", "cost_pinned", "delta_pct"])
        r0 = 6
        for i, row in enumerate(N['rows'], r0):
            for j, v in enumerate(row, 1): ws.cell(i, j, v)
        tr = r0 + len(N['rows'])
        ws.cell(tr, 1, "TOTAL").font = B
        ws.cell(tr, 6, round(N['free'], 2)).font = B; ws.cell(tr, 7, round(N['pin'], 2)).font = B
        ws.cell(tr, 8, round(N['pct'], 1)).font = B
        for c, w in zip("ABCDEFGH", [10, 8, 8, 7, 10, 10, 11, 9]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("f_x vs Usec (DLVO)")
    ws.cell(1, 1, "f_x vs secondary-minimum depth |U_sec| -- the single variable through which size, ionic strength AND mineralogy act").font = B
    ws.cell(2, 1, "|U_sec| = -min_h[U_vdw+U_edl]/kT over h>8 nm, sphere-plate (Gregory-retarded vdW + LSA-EDL), imported from fx_vs_usec.py -- one copy of that physics, not a re-implementation. A132 glass 7.17e-21 J, quartz 1.96e-20 J; zeta from Johnson 2018 Table SI-1. |U_sec| does NOT encode velocity.").font = IT
    ws.cell(3, 1, "TWO zeta gaps, both on quartz: no colloid/collector zeta at 3 mM (Table SI-1 gives 6/20/50 mM), and no QUARTZ collector zeta at 50 mM (it gives quartz at 6 and 20 mM only). So quartz Li 1.1 um 3 mM and quartz Tong 0.5 um 50 mM carry no |U_sec| and cannot enter the closure. Since 3 mM is to be in the manuscript, that gap has to be closed with a measured or interpolated zeta -- do not invent one to fill the sheet.").font = IT
    hd(ws, 4, ["study", "medium", "col", "size_um", "IS_mM", "Hamaker_J", "zeta_colloid_V", "zeta_collector_V", "|U_sec|_kT", "f_x", "cost", "f_x pin penalty %", "in closure?"])
    for i, r in enumerate(percol, 5):
        z1 = ZETA_COLLOID.get(float(r['IS'])) if r['IS'] else None
        z2 = ZETA_COLLECTOR[r['med']].get(float(r['IS'])) if r['IS'] else None
        # This flag MUST use the same test as rel(). It previously used the old one-sided k_r floor
        # while the closure had moved to the f_x identifiability penalty, so the sheet marked Li.M
        # "yes" when the closure had excluded it -- a plotting trap for anyone reading the sheet
        # rather than rerunning the fit. (W.P.J., 2026-08-25)
        if r['U'] is None: inc = "no (no zeta)"
        elif r['cost'] > REL_COST: inc = "no (cost)"
        elif r['fxpen'] < FX_PEN_MIN: inc = "no (f_x not identifiable)"
        else: inc = "yes"
        for j, v in enumerate([r['study'], r['med'], r['tag'], r['size'], r['IS'], A_HAM[r['med']],
                               ("" if z1 is None else z1), ("" if z2 is None else z2),
                               ("" if r['U'] is None else round(r['U'], 3)),
                               round(r['fx'], 5), round(r['cost'], 2),
                               round(r['fxpen'], 1), inc], 1):
            ws.cell(i, j, v)
    ws.conditional_formatting.add(f"K5:K{4 + len(percol)}", ColorScaleRule(
        start_type="num", start_value=0.5, start_color="FF3B4CC0",
        mid_type="num", mid_value=3.16, mid_color="FFDDDDDD",
        end_type="num", end_value=20, end_color="FFB40426"))
    for c, w in zip("ABCDEFGHIJKL", [7, 8, 10, 8, 7, 12, 14, 15, 11, 10, 9, 13]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("f_x(Usec) closure")
    ws.cell(1, 1, "Saturating closure  f_x = fmax * (1 - exp(-|U_sec| / U*))  -- fitted in log10 f_x").font = B
    ws.cell(2, 1, "FOUR-STAGE HISTORY. Stage 1 (fmax 0.0033, U* 0.42 kT) was fitted while r_s still FLOATED within a 0.25 dex window. Stage 2 (0.0088, 2.00 kT) arose when r_s was PINNED to the favorable anchor: with r_s free it had absorbed part of the retention f_x must now carry, unevenly across |U_sec|, so pinning r_s moved the f_x values themselves and the closure stretched. That MECHANISM is accepted. Stage 2's NUMBER is not: the leave-one-out block below shows the whole 2 kT result rests on the single point Li-Qtz20, whose f_x traces to column Li.M with k_r pinned on the optimiser's 1e-6 bound -- degenerate, not measured. Stage 3 (0.0047, 0.80 kT) applied a ONE-SIDED k_r floor filter. Stage 4, THIS SHEET, refits under the ACCUMULATED solid phase at excision (the eq (4) injection-window snapshot ignores 7.0 of the 10 PV and is retired) AND replaces that filter with a two-sided identifiability test. NO SINGLE U* IS ADOPTED, because the closure turns out to depend more on the filter than on the convention: 0.52 kT with the old floor filter (which lets the non-identifiable column Li.M back in -- its k_r now flies to 5.6e-3 instead of railing at 1e-6, at unchanged cost), 0.77 with Li.M removed by hand, 0.99 with the f_x-identifiability filter used here, 1.20-1.35 with the k_r-identifiability filter. RMS is 0.39-0.48 throughout, so the data do not choose. REPORT THE SHAPE AND A RANGE -- 'half to a few kT' (W.P.J., 2026-08-25) -- NOT A VALUE. NOTE the a-priori machinery (part2_apriori_alpha_machinery.md s87) expects saturation by ~2 kT and therefore does NOT support the reported closure; that disagreement is left standing rather than dropped -- if the ~2 kT expectation is right, the reading is that the fitted f_x cannot resolve the deep end.").font = IT
    ws.cell(3, 1, f"TWO principled filters, no by-name exclusions. (1) cost <= {REL_COST:.0f}. (2) pinning f_x to the all-column geomean must cost at least {FX_PEN_MIN:.0f}% -- if it costs less, f_x is not identifiable on that column and it cannot inform a closure IN f_x. A degenerate fit earns a LOW cost precisely because it is degenerate, so filter (1) cannot catch it. Filter (2) replaced a ONE-SIDED test ('free k_r on the 1e-6 bound') on 2026-08-25: under the accumulated convention Li.M's k_r flies to 5.6e-3 instead of railing down, the floor test stopped catching it, and it re-entered the closure at the deepest well and shortened U* 0.77 -> 0.52 kT. Identifiability is two-sided. Tong-B is NOT excluded by name as the old scripts did ('~10x outlier'); it either passes these rules or it does not.").font = IT
    hd(ws, 5, ["variant", "reliability cut", "fmax", "U* (kT)", "log10-RMS (dex)", "band (x/)", "n points", "status"])
    for i, (nm, c, st) in enumerate((
            ("per column (uniform)", CL_COL, "*** REPORTED CLOSURE (stage 4) -- uniform rule, largest n. Quote the SHAPE and 'half to a few kT', not this U*. ***"),
            ("per condition (uniform)", CL_CND, f"replicate-averaged check: same shape, U* within {abs(CL_CND[1] - CL_COL[1]):.2f} kT"),
            ("per column, old cut", CL_OLD, "SUPERSEDED cut; U* lands ON its 0.05 lower bound at n=4 -- unusable, shown only to demonstrate the old cut cannot be rehabilitated")), 6):
        for j, v in enumerate([nm, (REL_COST_OLD if "old" in nm else REL_COST), round(c[0], 5), round(c[1], 3),
                               round(c[2], 3), round(c[3], 2), c[4], st], 1):
            ws.cell(i, j, v)
    for j, v in enumerate(["stage 2 (SUPERSEDED)", 15.0, 0.0088, 2.0, 0.411, 2.57, 12,
                           "distributed fx_trend.xlsx 'closure REVISED'; mixed per-column glass / per-condition quartz, Tong-B excluded by name. Reproduced exactly from its own points -- see leave-one-out below."], 1):
        ws.cell(9, j, v)
    for j, v in enumerate(["stage 1 (SUPERSEDED)", 3.5, 0.0033, 0.42, 0.218, 1.62, 7,
                           "fx_usec_closure.py / fx_trend_analysis.md; fitted while r_s still floated within 0.25 dex"], 1):
        ws.cell(10, j, v)

    ws.cell(12, 1, "LEAVE-ONE-OUT ON STAGE 2's OWN 12 POINTS -- the evidence that retired it").font = B
    ws.cell(13, 1, "Refitting stage 2's published points reproduces it digit-for-digit, which validates this script's closure fitter. Removing ONE point, Li-Qtz20, collapses it back to stage 1. No other point does that. In the current per-column fits, that condition's high f_x comes from Li.M, whose free k_r sits on the 1e-6 bound (f_x 0.21 at cost 0.72) -- degenerate, not measured.").font = IT
    hd(ws, 14, ["stage-2 set", "fmax", "U* (kT)", "note"])
    for i, row in enumerate((
            ("as published (n=12)", 0.0088, 2.00, "reproduced exactly by this script's fitter"),
            ("minus Li-Qtz20 (n=11)", 0.0038, 0.59, "COLLAPSES to ~stage 1 -- the whole 2 kT result is this one point"),
            ("minus CI (n=11)", 0.0070, 1.51, "largest other single influence, and it is mild")), 15):
        for j, v in enumerate(row, 1): ws.cell(i, j, v)

    ws.cell(19, 1, "REPORTED CLOSURE, EVALUATED").font = B
    hs = CL_COL[1] * np.log(2.0); p95 = CL_COL[1] * np.log(20.0)
    ws.cell(20, 1, f"f_x = {CL_COL[0]:.4f} * (1 - exp(-|U_sec| / {CL_COL[1]:.2f} kT)),  multiplicative band x/{CL_COL[3]:.2f} (the velocity + identifiability spread |U_sec| does not encode). Half-saturation at |U_sec| = {hs:.2f} kT; 95% of plateau by {p95:.2f} kT.").font = IT
    hd(ws, 21, ["|U_sec| (kT)", "predicted f_x", "band low", "band high"])
    # Dense enough to plot straight from the sheet: 40 points log-spaced over 0.1-10 kT. Was six
    # points, which meant redrawing the curve required re-implementing the formula. (W.P.J. 2026-08-25)
    for i, u in enumerate([float(x) for x in np.logspace(np.log10(0.1), np.log10(10.0), 40)], 22):
        f = CL_COL[0] * (1 - np.exp(-u / CL_COL[1]))
        for j, v in enumerate([u, round(f, 5), round(f / CL_COL[3], 5), round(f * CL_COL[3], 5)], 1):
            ws.cell(i, j, v)
    # Row 63, below the 40-point curve table (rows 22-61). At row 28 it was being overwritten by it.
    ws.cell(63, 1, "CAVEAT -- do not quote U* as a precise number. Across defensible degeneracy filters under the accumulated convention the scale spans 0.5-1.4 kT (0.52 old one-sided k_r floor / 0.77 that minus Li.M / 0.99 f_x-identifiability, used here / 1.20-1.35 k_r-identifiability) at log10-RMS 0.39-0.48 throughout -- the data do not choose between them. Quote the SHAPE and a range: f_x rises with |U_sec| and saturates, half to a few kT, with the size and IS series on one curve.").font = IT
    for c, w in zip("ABCDEFGH", [24, 15, 10, 10, 16, 11, 10, 42]): ws.column_dimensions[c].width = w

    wb.save(args.out); print("wrote " + args.out)

    # ================= figures =================
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    used = rel(percol, REL_COST)
    # Ringed/hollow markers must match rel(): degenerate = f_x not identifiable, NOT the old k_r floor.
    deg = [r for r in percol if r['U'] is not None and r['fxpen'] < FX_PEN_MIN]
    hic = [r for r in percol if r['U'] is not None and r['fxpen'] >= FX_PEN_MIN and r['cost'] > REL_COST]
    for med, mk in (("glass", "o"), ("quartz", "^")):
        s = [r for r in used if r['med'] == med]
        if s: ax.scatter([r['U'] for r in s], [r['fx'] for r in s], c=[r['cost'] for r in s],
                         cmap="coolwarm", vmin=0, vmax=REL_COST, marker=mk, s=130,
                         edgecolor="k", lw=.9, zorder=6)
        s = [r for r in hic if r['med'] == med]
        if s: ax.scatter([r['U'] for r in s], [r['fx'] for r in s], facecolor="none",
                         edgecolor="0.62", marker=mk, s=110, lw=1.1, zorder=3)
        s = [r for r in deg if r['med'] == med]
        if s: ax.scatter([r['U'] for r in s], [r['fx'] for r in s], facecolor="none",
                         edgecolor="#c0392b", marker=mk, s=190, lw=2.0, zorder=7)
    for r in deg:
        ax.annotate(r['tag'], (r['U'], r['fx']), textcoords="offset points", xytext=(9, 4),
                    fontsize=8, color="#c0392b")
    ug = np.logspace(np.log10(0.12), np.log10(11), 200)
    ax.plot(ug, CL_COL[0] * (1 - np.exp(-ug / CL_COL[1])), "k-", lw=2.2, zorder=8,
            label=f"REPORTED: fmax={CL_COL[0]:.4f}, U*={CL_COL[1]:.2f} kT")
    ax.plot(ug, 0.0088 * (1 - np.exp(-ug / 2.00)), "k--", lw=1.5, zorder=8,
            label="superseded stage 2: 0.0088, U*=2.00 kT")
    ax.plot(ug, 0.0033 * (1 - np.exp(-ug / 0.42)), color="0.45", ls=":", lw=1.5, zorder=8,
            label="superseded stage 1: 0.0033, U*=0.42 kT")
    ax.fill_between(ug, CL_COL[0] * (1 - np.exp(-ug / CL_COL[1])) / CL_COL[3],
                    CL_COL[0] * (1 - np.exp(-ug / CL_COL[1])) * CL_COL[3],
                    color="0.5", alpha=.16, zorder=2, label=f"x/{CL_COL[3]:.2f} band (velocity + identifiability)")
    ax.scatter([], [], marker="o", facecolor="0.7", edgecolor="k", s=110, label="glass")
    ax.scatter([], [], marker="^", facecolor="0.7", edgecolor="k", s=110, label="quartz")
    ax.scatter([], [], marker="o", facecolor="none", edgecolor="0.62", s=100, lw=1.1, label=f"excluded: cost > {REL_COST:.0f}")
    ax.scatter([], [], marker="o", facecolor="none", edgecolor="#c0392b", s=140, lw=2.0,
               label="excluded: f_x not identifiable (pinning it is free)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("secondary-minimum depth  |U_sec| / kT   (size x ionic strength x mineralogy)")
    ax.set_ylabel("f_x  (grain-contact recruitment fraction)")
    ax.set_title("f_x vs |U_sec|: the reported closure, and the two it supersedes\n"
                 "stage 2's U*=2 kT was carried by Li.M alone, whose k_r sits on the optimiser bound")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/fx_vs_usec.png", dpi=140); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 5.6))
    for med, mk, c in (("glass", "o", "#1f77b4"), ("quartz", "s", "#7b2d8b")):
        s = [r for r in percol if r['med'] == med]
        ax.scatter([r['size'] for r in s], [r['fx'] for r in s], s=85, marker=mk, color=c,
                   edgecolor="k", zorder=5, label=med)
    ax.axhline(SIZE['F'], color="#1f77b4", ls="--", lw=1.3, alpha=.7,
               label=f"glass 8 m/d 20 mM pin {SIZE['F']:.4f} (+{SIZE['pct']:.0f}% if pinned)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks([0.1, 0.2, 0.5, 1.1, 2.0]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1.1", "2.0"])
    ax.set_xlabel("colloid diameter (µm)"); ax.set_ylabel("f_x")
    ax.set_title("Focus fraction f_x vs colloid size (all unfavorable columns, current fits)")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/fx_vs_size.png", dpi=140); plt.close(fig)

    # --- f_x vs IONIC STRENGTH, at constant size AND velocity ---------------------------------
    # One series per (study, medium, size, velocity) so IS is the ONLY variable moving along a line.
    # Series with a single ionic strength are dropped -- they cannot show a trend and would read as
    # data points on an IS plot that carry no IS information.
    SER = collections.defaultdict(list)
    for r in percol:
        if r['IS'] and r['IS'] > 1:
            SER[(r['study'], r['med'], round(r['size'], 1), r['vel'])].append(r)
    SER = {k: v for k, v in SER.items() if len({r['IS'] for r in v}) > 1}
    sty = {('Li', 'glass', 1.1, 4.0):    ('#1f77b4', 'o', '-'),
           ('Li', 'quartz', 1.1, 4.0):   ('#7b2d8b', '^', '-'),
           ('Tong', 'glass', 0.5, 4.0):  ('#2a9d8f', 'o', '--'),
           ('Tong', 'glass', 2.0, 8.0):  ('#5dade2', 'o', '--'),
           ('Tong', 'quartz', 0.5, 4.0): ('#c39bd3', '^', '--')}
    fig, ax = plt.subplots(figsize=(8.4, 5.9))
    for key in sorted(SER, key=lambda z: (z[1], z[2], z[3])):
        rs = SER[key]; c, mk, ls = sty.get(key, ('0.5', 's', ':'))
        lab = f"{key[1]} {key[0]} {key[2]} um, {key[3]:.0f} m/d"
        good = [r for r in rs if r['fxpen'] >= FX_PEN_MIN]
        bad = [r for r in rs if r['fxpen'] < FX_PEN_MIN]
        ax.scatter([r['IS'] for r in good], [r['fx'] for r in good], s=85, marker=mk, color=c,
                   edgecolor='k', lw=.8, zorder=6, label=lab)
        if bad:
            ax.scatter([r['IS'] for r in bad], [r['fx'] for r in bad], s=180, marker=mk,
                       facecolor='none', edgecolor='#c0392b', lw=2.0, zorder=7)
            for r in bad:
                ax.annotate(r['tag'], (r['IS'], r['fx']), textcoords='offset points',
                            xytext=(9, 3), fontsize=8, color='#c0392b')
        byIS = collections.defaultdict(list)
        for r in good: byIS[r['IS']].append(r['fx'])
        xs = sorted(byIS)
        if len(xs) > 1:
            ax.plot(xs, [gm(byIS[x]) for x in xs], ls, color=c, lw=1.4, alpha=.75, zorder=4)
    ax.axhline(ISN['F'], color='#1f77b4', ls=':', lw=1.2, alpha=.8,
               label=f"glass Li 1.1 um pin {ISN['F']:.4f} (+{ISN['pct']:.1f}% if pinned)")
    ax.scatter([], [], marker='o', facecolor='none', edgecolor='#c0392b', s=140, lw=2.0,
               label='f_x not identifiable (pinning it is free)')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xticks([3, 6, 20, 50]); ax.set_xticklabels(['3', '6', '20', '50'])
    ax.set_xlabel('ionic strength (mM)'); ax.set_ylabel('f_x  (grain-contact recruitment fraction)')
    ax.set_title('Focus fraction f_x vs ionic strength, at constant colloid size AND velocity\n'
                 'lines join geometric means; single-IS series omitted; degenerate columns ringed')
    ax.grid(alpha=.3, which='both'); ax.legend(fontsize=7.5, loc='upper left')
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/fx_vs_IS.png", dpi=140); plt.close(fig)
    print("wrote fx_vs_usec.png, fx_vs_size.png, fx_vs_IS.png")


if __name__ == "__main__":
    main()
