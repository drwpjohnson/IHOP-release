"""canon_nokr_fit.py -- the k_r NECESSITY test on the canonical five, and the workbook behind
fit_canonical_IHOP.png.

Produces:
  * canon_nokr.json            -- the k_r=0 model curves, read by ihop_plot_fits.py --canon --nokr
                                  (grey dashed overlay). The plotter stays a pure DRAWER; nothing is
                                  refitted there.
  * fits_canonical_IHOP.xlsx   -- data + BOTH sets of simulations, one sheet per canonical condition,
                                  plus a parameter/cost sheet carrying the necessity comparison.

WHAT "NO k_r" MEANS HERE, AND WHY IT IS A REFIT (W.P.J., 2026-08-25)
The comparison mimics the Serial-3a / Serial-3b pair of the original arc (Serial-3-record.md s3;
Serial-Arc-summary.md): Serial-3a is the SCHEMATIC-FAITHFUL model -- the Serial-3 schematic has no
grain-contact -> wall release path at all -- and Serial-3b adds k_r. The old implementation
(Code/serial_model.py, setup(..., use_kr)) DROPPED k_r from the parameter vector and REFITTED the
remaining parameters. This script does the same thing under the current objective:

    +k_r    4 free parameters:  a_s, a_m, f_x, k_r
    no-k_r  3 free parameters:  a_s, a_m, f_x       with k_r identically 0

** This is the only fair form of the test. Zeroing k_r while HOLDING the other three at their
   +k_r values would answer a different and uninteresting question -- "how much does the fitted model
   move if you break one of its parameters" -- and would overstate the necessity of k_r by whatever
   a_s, a_m and f_x could have absorbed. The whole content of a necessity test is what the surviving
   parameters can compensate. **

Everything else is held identical to unfav_master_fit.py: same objective and weights, r_s pinned at the
favorable anchor, v_ns = 5%, -6 BTEC floor, and the same CONDITION-level branch window (majority over
replicate columns) rather than each column's own classification.

The +k_r fits are ALSO recomputed here rather than read from the master workbook. That is deliberate:
it makes the two costs apples-to-apples (same optimiser, same starts, same machine), and the agreement
with UnfavorableMaster.xlsx is then a reproduction check, printed at the end. If the +k_r parameters
here disagree with the master, the master is stale -- do not paper over it by reading its costs.

The canonical five are FIVE CONDITIONS but THIRTEEN EXPERIMENTS: Li quartz 6 mM has AB/V/Y, quartz
20 mM has M/P/S, quartz 3 mM has AE/AH, and glass 1.1 um / 4 m/day / 20 mM has Li O PLUS Tong
AE/AK/AQ. Every experiment is fitted separately and the plotted line is the mean of the per-
experiment curves, exactly as ihop_plot_fits.py does for the +k_r fits -- NOT a fit to the mean.

⚠ The Tong trio was ADDED 2026-09-02 (W.P.J.); before that this script filtered to Li only and the
set was TEN experiments. Every number in the FINDING block below is the ten-experiment version and
has NOT been recomputed -- treat those as a DATED SNAPSHOT, not as current, until this is re-run.

FINDING (2026-08-25, REFRESHED under the accumulated-profile convention).
The figures first written here are superseded -- +2.5% total / +4.2% median / tail +6.94 / +1.86 /
RP -0.63 / -0.63 were the retired eq (4) snapshot's, and the sign of Li.M's excess changed with them.
Removing k_r costs +1.7% in total cost over the ten canonical columns (343.09 -> 349.00); the
per-column median excess is +4.0%. ** k_r's effect on FIT
QUALITY IS MODEST and should be described that way. ** The interesting part is not the size of the
penalty but WHERE it lands: summed over the ten columns, tail level +6.88 and tail slope +1.92,
against RP level -0.36 and RP shape -2.53 (i.e.
the retention profile very slightly IMPROVES without k_r, because a_s/a_m/f_x are freed from having to
serve the tail). Plateau is 0.00 in both. So k_r buys the elution tail and nothing else -- which is
exactly the role Serial-3-record.md s3 assigns it, and why the grey dashed curve in
fit_canonical_IHOP.png separates from the solid line only after injection stops, and is invisible
under it in every RP panel. f_x rises 20-60% when k_r is removed (e.g. Li.R 0.00066 -> 0.00089), a_s
barely moves: the near-surface population is asked to hold more colloids when none can be released.

Two columns are worth naming. Li.S carries the largest excess (+95%) but the smallest absolute cost
(0.403 -> 0.786), so the percentage is large because the denominator is tiny. Li.M shows +0.03%: its
fitted k_r rails at the 1e-6/s floor, so the two are the SAME model there and the excess is optimiser
noise around zero. (Under the retired snapshot convention Li.M read -0.3%, i.e. no-k_r nominally
BEATING the nesting model -- an impossibility that flagged a local optimum and led to the
cross-seeding now in fit_variant. It is non-negative under accum, as nesting requires.) Read |excess|
below ~0.5% as indistinguishable; neither column is evidence about the mechanism.

Usage:  python3 canon_nokr_fit.py [--outdir .]
        Run from Code/ with the cleaned CSV in ../Data/ (needs unfav_master_fit.py alongside).
        Then: python3 ihop_plot_fits.py --master UnfavorableMaster.xlsx --canon --nokr canon_nokr.json
"""
import argparse, collections, functools, json, os, warnings
import numpy as np
warnings.filterwarnings("ignore"); print = functools.partial(print, flush=True)
from scipy.optimize import least_squares
import openpyxl
from openpyxl.styles import Font

# engine, seed_rs, objective constants, CSV loader, sl/rp_branch/condition_branch, fit_col
exec(open("unfav_master_fit.py").read().split("# ---- fit all unfavorable")[0])

# The canonical five, in the HYDEQ main-text order (matched pairs first, 3 mM extreme last).
# (label, medium, size_um, vel_mday, IS_mM).
#
# ⚠ STUDY SCOPE, changed 2026-09-02 (W.P.J.) -- this list is a CONDITION list, and a condition is
# (medium, sizeclass, velocity, IS) ACROSS studies, exactly as unfav_master_fit.py's own condition
# sheets group it. It used to be filtered to Li columns only ("Li only, as in ihop_plot_fits.
# CANON_ROWS"), which silently dropped Tong AE/AK/AQ from the glass 1.1 um / 4 m/day / 20 mM
# condition -- so Figure 6 showed that condition with 1 of its 4 experiments and the "5 conditions /
# 10 experiments" count was a by-study count masquerading as a condition count. Default is now ALL
# studies (5 conditions / 13 experiments); --studies Li reproduces the historical 10-experiment set.
CANON = [("R",  "glass",  1.1, 4.0,  6.0),
         ("V",  "quartz", 1.1, 4.0,  6.0),
         ("O",  "glass",  1.1, 4.0, 20.0),
         ("P",  "quartz", 1.1, 4.0, 20.0),
         ("AE", "quartz", 1.1, 4.0,  3.0)]
SHEET = {"R": "gl_1.1um_4md_6mM", "V": "qu_1.1um_4md_6mM", "O": "gl_1.1um_4md_20mM",
         "P": "qu_1.1um_4md_20mM", "AE": "qu_1.1um_4md_3mM"}
# Railing is tested on the NATURAL parameter against its own bound, relatively (within 1%), NOT as a
# fixed distance in the log10 search coordinate. The first version of this script did the latter and
# reported a_s as railed whenever a_s < ~4.5%, because p0 = log10(1-a_s) crowds the upper bound as
# a_s -> 0 -- five false positives, including a_s = 0.0158 which is 158x its lower bound. (W.P.J.)
BOUNDS_NAT = {"a_s": (1e-4, 1 - 10 ** -3.3), "a_m": (10 ** -3.3, 0.999), "f_x": (1e-4, 1.0),
              "k_r": (1e-6, 0.1)}


def railed_nat(vals):
    """-> list of parameter names sitting within 1% (relative) of one of their own bounds."""
    out = []
    for n, v in vals.items():
        lo, hi = BOUNDS_NAT[n]
        if v <= lo * 1.01 or v >= hi * 0.99:
            out.append(n)
    return out


def fit_variant(k, nin, use_kr, extra_starts=()):
    """Fit ONE column, with (use_kr=True, 4 params) or without (use_kr=False, 3 params) the release path.

    The residual vector is identical to unfav_master_fit.fit_col in every term; only the parameter
    vector differs, so the two costs are directly comparable. With use_kr=True and no extra starts
    this reproduces fit_col exactly (checked in main()).

    ** NESTING. The +k_r model CONTAINS the no-k_r model (k_r at its 1e-6/s floor is numerically zero
    over a 10 PV run), so cost(+k_r) <= cost(no-k_r) must hold at the global optimum. The first run of
    this script violated that on Li.M by -0.3%, which is not a model result -- it is proof that the
    3-start multistart landed the 4-parameter fit in a local optimum. Rather than report a negative
    "excess cost", each fit is now also seeded from the other variant's solution, which makes the
    nesting inequality hold by construction. Where that changes a +k_r cost relative to the master
    recipe, main() prints it: the master fit for that column is then slightly off its own optimum, and
    that is a finding about the master, not about k_r. **
    """
    m = meta[k]; bt = cols[k]['BTEC']; rp = cols[k]['RP']
    if len(bt) < 3 or len(rp) < 3: return None
    med = m['medium']; size = m['size']; vel = m['vel']; C0 = m['C0']
    theta = THETA[med]; V_MS = vel / DAY; eng = Eng(vel)
    logK = np.log10(REV * T0 * theta * C0 * Vref); rs0, src = seed_rs(med, size, vel); kk = rs0 * V_MS
    bt = bt.copy(); bt[:, 1] = np.maximum(bt[:, 1], -6.0)
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]
    si, so = sl(rx, rlog, nin)
    wm = (pv > 1.2) & (pv < 4.0); pvw = pv[wm] if wm.sum() else pv
    dmean = float(lc[wm].mean()) if wm.sum() else float(lc.mean())
    tm = pv > 4.2; sld = ts(pv, lc)

    def resid(p):
        a_s = 1 - 10 ** p[0]; am = 10 ** p[1]; fx = 10 ** p[2]
        krr = 10 ** p[3] if use_kr else 0.0                  # <-- k_r identically zero when off
        r = eng.run(kk, a_s, am, fx, krr)
        rl = np.interp(rx, r['x'], np.maximum(r['rp'], 1e-300)) / V_MS
        lS = logK + np.log10(np.maximum(rl, 1e-300))
        rpx = W_RP * (lS - rlog); sm, sn = sl(rx, lS, nin)
        shp = W_SHAPE * np.array([sm - si, sn - so])
        mlog = np.mean(np.log10(np.maximum(np.interp(pvw, r['tp'], r['C']), 1e-6))); dev = mlog - dmean
        pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])
        tl = W_TAIL * (np.log10(np.maximum(np.interp(pv[tm], r['tp'], r['C']), 1e-6)) - lc[tm]) \
            if tm.sum() else np.array([0.])
        slm = ts(r['tp'], np.log10(np.maximum(r['C'], 1e-6)))
        tsl = W_TSLOPE * np.array([slm - sld if sld == sld else 0.])
        return np.concatenate([rpx, shp, pl, tl, tsl])

    krs = np.log10(KR_MED[med])
    lo = [-3.3, -3.3, np.log10(1e-4)]; hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0)]
    starts = [[-1.5, -1., np.log10(.005)], [-.5, -.3, np.log10(.02)], [-2.3, -1.5, np.log10(.001)]]
    if use_kr:      # exactly the bounds and starts of unfav_master_fit.fit_col
        lo += [np.log10(1e-6)]; hi += [np.log10(.1)]
        for s, kv in zip(starts, (krs, krs, krs - 0.5)): s.append(kv)
    starts += [[float(np.clip(v, a, b)) for v, a, b in zip(s0, lo, hi)] for s0 in extra_starts]
    best = None
    for s0 in starts:
        rr = least_squares(resid, s0, bounds=(lo, hi), max_nfev=80)
        if best is None or rr.cost < best.cost: best = rr
    a_s = 1 - 10 ** best.x[0]; am = 10 ** best.x[1]; fx = 10 ** best.x[2]
    krf = 10 ** best.x[3] if use_kr else 0.0
    nat = dict(a_s=a_s, a_m=am, f_x=fx)
    if use_kr: nat["k_r"] = krf
    railed = railed_nat(nat)
    r1 = eng.run(kk, a_s, am, fx, krf)
    idx = np.linspace(0, len(r1['tp']) - 1, 90).astype(int)
    btf = np.column_stack([r1['tp'][idx], np.log10(np.maximum(r1['C'][idx], 1e-6))])
    rpf = np.column_stack([r1['x'], logK + np.log10(np.maximum(r1['rp'] / V_MS, 1e-300))])
    lS_at = logK + np.log10(np.maximum(np.interp(rx, r1['x'], r1['rp']) / V_MS, 1e-300))
    rpRMS = float(np.sqrt(np.mean((lS_at - rlog) ** 2)))
    stm = pv > 1.2
    btRMS = float(np.sqrt(np.mean((np.log10(np.maximum(np.interp(pv[stm], r1['tp'], r1['C']), 1e-6))
                                   - lc[stm]) ** 2))) if stm.sum() else float('nan')
    v = resid(best.x); n1 = len(rx); ntl = int(tm.sum()) if tm.sum() else 1
    hh = lambda a: 0.5 * float(np.sum(np.asarray(a) ** 2))
    blk = dict(rp_level=hh(v[:n1]), rp_shape=hh(v[n1:n1 + 2]), plateau=hh(v[n1 + 2:n1 + 3]),
               tail_level=hh(v[n1 + 3:n1 + 3 + ntl]), tail_slope=hh(v[n1 + 3 + ntl:]))
    return dict(rs=rs0, a_s=a_s, a_m=am, fx=fx, kr=krf, kr_pv=krf * (L / eng.v), cost=float(best.cost),
                p=[float(v) for v in best.x], rpRMS=rpRMS, btRMS=btRMS,
                bt_exp=bt, rp_exp=rp, bt_fit=btf, rp_fit=rpf,
                railed=railed, nin=(nin if nin else 0), **blk)


def mean_curve(curves):
    """Mean of per-column model curves on the first column's grid (matches ihop_plot_fits.fitline)."""
    x0 = curves[0][:, 0]
    ys = [c[:, 1] if len(c) == len(x0) and np.allclose(c[:, 0], x0) else np.interp(x0, c[:, 0], c[:, 1])
          for c in curves]
    return x0, np.mean(ys, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--studies", default="all",
                    help="'all' (default: every study contributing to each condition, 13 experiments) "
                         "or a single study name, e.g. 'Li' (the historical 10-experiment set)")
    args = ap.parse_args()

    # ---- which experiments belong to each canonical condition, and the CONDITION branch window ----
    # Study scope: every study by default (see the CANON comment). --studies Li restores the old
    # Li-only behaviour for reproducing the historical 10-experiment numbers.
    want_study = None if args.studies.lower() == "all" else args.studies
    groups = collections.OrderedDict()
    for lab, med, size, vel, IS in CANON:
        ks = [k for k, mm in meta.items()
              if (want_study is None or k[0] == want_study)
              and mm['chem'] == 'unfavorable' and mm['medium'] == med
              and abs(mm['size'] - size) < 0.15 and mm['vel'] == vel and mm['IS'] == IS
              and len(cols[k]['RP']) >= 3 and len(cols[k]['BTEC']) >= 3]
        if not ks: raise SystemExit(f"canonical condition {lab} has no experiments"
                                    f"{'' if want_study is None else ' for study ' + want_study}")
        br = condition_branch([rp_branch(cols[k]['RP'][:, 1]) for k in ks])
        nin = NIN_PEAKED if br == 'peaked' else None  # matches renamed rp_branch/condition_branch (exec-imported above)
        # sort by (study, column) -- with >1 study present, column letter alone is not a stable key
        ks = sorted(ks, key=lambda z: (z[0], z[2]))
        groups[lab] = dict(med=med, size=size, vel=vel, IS=IS, ks=ks, branch=br, nin=nin)
        print(f"{lab:3s} {med:6s} {IS:4.0f} mM  experiments {[f'{k[0]}.{k[2]}' for k in ks]}"
              f"  branch={br}  nin={nin or 'half-split'}")
    ntot = sum(len(g['ks']) for g in groups.values())
    print(f"canonical set: {len(groups)} conditions / {ntot} experiments "
          f"(studies: {'all' if want_study is None else want_study})")

    # ---- fit every column both ways ----
    # Order matters: master-recipe +k_r first (reproduction check against UnfavorableMaster), then
    # no-k_r seeded from it, then +k_r re-run seeded from the no-k_r solution so nesting is enforced.
    FIT = collections.OrderedDict(); drift = []; nudged = []
    print(f"\n{'column':10s}{'cost +k_r':>12s}{'cost no-k_r':>13s}{'excess':>9s}"
          f"{'a_s(+)':>9s}{'a_s(0)':>9s}{'f_x(+)':>10s}{'f_x(0)':>10s}{'k_r /PV':>10s}  railed (no-k_r)")
    for lab, g in groups.items():
        for k in g['ks']:
            ref = fit_col(k, nin_override=g['nin'])                    # master recipe, for the check
            wk = fit_variant(k, g['nin'], True)                        # same recipe, this script
            for f in ("a_s", "a_m", "fx", "cost"):
                if abs(wk[f] - ref[f]) > 1e-9 * max(1.0, abs(ref[f])):
                    drift.append(f"Li.{k[2]}.{f}: {ref[f]:.6g} vs {wk[f]:.6g}")
            nk = fit_variant(k, g['nin'], False, extra_starts=[wk['p'][:3]])
            wk2 = fit_variant(k, g['nin'], True,
                              extra_starts=[wk['p'], nk['p'] + [np.log10(1e-6)]])
            # 1e-4 relative, not 1e-9: below that the "improvement" is optimiser noise and printing it
            # cries wolf (the first version reported two columns as improved by -0.00%).
            if wk2['cost'] < wk['cost'] * (1 - 1e-4):
                nudged.append(f"Li.{k[2]} {wk['cost']:.4f} -> {wk2['cost']:.4f} "
                              f"({100*(wk2['cost']-wk['cost'])/wk['cost']:+.2f}%)")
            # The PLOTTED and TABULATED +k_r curves stay the master-recipe fit `wk`, so the workbook
            # and fit_canonical_IHOP.png cannot drift from UnfavorableMaster.xlsx. The nesting-enforced
            # fit `wk2` is used ONLY as the denominator/reference of the excess-cost comparison, where
            # a local optimum would otherwise manufacture a negative excess.
            FIT[(lab, k[2])] = dict(kr=wk, kr2=wk2, no=nk)
            ex = 100.0 * (nk['cost'] - wk2['cost']) / wk2['cost']
            print(f"Li.{k[2]:<7s}{wk['cost']:12.3f}{nk['cost']:13.3f}{ex:+8.1f}%"
                  f"{wk['a_s']:9.4f}{nk['a_s']:9.4f}{wk['fx']:10.5f}{nk['fx']:10.5f}"
                  f"{wk['kr_pv']:10.4f}  {','.join(nk['railed']) or '-'}")
    print("\nreproduction check vs unfav_master_fit.fit_col: " +
          ("IDENTICAL on all columns" if not drift else "DIFFERS -- " + "; ".join(drift)))
    print("nesting enforcement (+k_r reseeded from the no-k_r optimum): " +
          ("no column improved -- the master multistart was already at the optimum"
           if not nudged else "IMPROVED " + "; ".join(nudged) +
           "  <-- these master fits are slightly off their own optimum"))

    # ---- mean curves per condition, for the figure ----
    out = {}
    for lab, g in groups.items():
        rec = {}
        for tagname, key in (("bt", "bt_fit"), ("rp", "rp_fit")):
            x, y = mean_curve([FIT[(lab, k[2])]['no'][key] for k in g['ks']])
            rec[tagname] = dict(x=[float(v) for v in x], y=[float(v) for v in y])
        rec['sheet'] = SHEET[lab]; rec['columns'] = [k[2] for k in g['ks']]
        rec['branch'] = g['branch']
        out[SHEET[lab]] = rec
    jp = os.path.join(args.outdir, "canon_nokr.json")
    json.dump(out, open(jp, "w"), indent=1)
    print(f"\nwrote {os.path.basename(jp)}  ({len(out)} conditions)")

    # ================= workbook =================
    Bf = Font(bold=True); IT = Font(italic=True)
    wb = openpyxl.Workbook(); wb.remove(wb.active)

    def hd(ws, r, vals):
        for j, v in enumerate(vals, 1):
            ws.cell(r, j, v).font = Bf

    ps = wb.create_sheet("Parameters & k_r necessity")
    ps.cell(1, 1, "Canonical five -- IHOP (Serial-3) fits WITH and WITHOUT the crawl->wall release "
                  "pathway. Both are REFITS: no-k_r drops k_r from the parameter vector and refits "
                  "a_s, a_m, f_x. r_s pinned at the favorable anchor in both.").font = Bf
    ps.cell(2, 1, "cost = 0.5*sum(residual^2) under the adopted objective (W_RP 6.0, W_SHAPE 2.5, "
                  "W_PLAT 20.0 mean-log over PV 1.2-4 +-0.25 dex, W_TAIL 3.0, W_TSLOPE 16.0); "
                  "excess = (cost_nokr - cost_kr)/cost_kr.").font = IT
    ps.cell(3, 1, "Read |excess| below ~0.5% as indistinguishable. Where k_r rails at its 1e-6/s floor "
                  "(see 'railed (+k_r)') the two models are the SAME model, and the sign of the "
                  "difference is optimiser noise, not evidence against k_r.").font = IT
    hd(ps, 4, ["condition", "column", "medium", "IS (mM)", "branch", "inlet pts",
               "a_s +k_r", "a_m +k_r", "f_x +k_r", "k_r (/PV)", "cost +k_r", "RP RMS +k_r", "BTEC RMS +k_r",
               "a_s no-k_r", "a_m no-k_r", "f_x no-k_r", "cost no-k_r", "RP RMS no-k_r", "BTEC RMS no-k_r",
               "cost +k_r (nesting-enforced)", "excess cost %", "railed (+k_r)", "railed (no-k_r)"])
    r = 5
    for lab, g in groups.items():
        for k in g['ks']:
            w = FIT[(lab, k[2])]['kr']; w2 = FIT[(lab, k[2])]['kr2']; n = FIT[(lab, k[2])]['no']
            ex = 100.0 * (n['cost'] - w2['cost']) / w2['cost']
            for j, v in enumerate([lab, f"Li.{k[2]}", g['med'], g['IS'], g['branch'],
                                   (g['nin'] or "half-split"),
                                   w['a_s'], w['a_m'], w['fx'], w['kr_pv'], w['cost'], w['rpRMS'], w['btRMS'],
                                   n['a_s'], n['a_m'], n['fx'], n['cost'], n['rpRMS'], n['btRMS'],
                                   w2['cost'], ex,
                                   ",".join(w['railed']) or "-", ",".join(n['railed']) or "-"], 1):
                ps.cell(r, j, v)
            r += 1
    r += 1
    ps.cell(r, 1, "Cost block decomposition (0.5*sum sq per block) -- where the k_r=0 penalty lands").font = Bf
    r += 1
    hd(ps, r, ["condition", "column", "variant", "RP level", "RP shape", "plateau",
               "tail level", "tail slope", "total"])
    r += 1
    for lab, g in groups.items():
        for k in g['ks']:
            for tag, d in (("+k_r", FIT[(lab, k[2])]['kr']), ("no-k_r", FIT[(lab, k[2])]['no'])):
                for j, v in enumerate([lab, f"Li.{k[2]}", tag, d['rp_level'], d['rp_shape'],
                                       d['plateau'], d['tail_level'], d['tail_slope'], d['cost']], 1):
                    ps.cell(r, j, v)
                r += 1
    for c, w in zip("ABCDEFGHIJKLMNOPQRSTUVW", [11, 9, 8, 8, 14, 10] + [11] * 13 + [16, 13, 15, 16]):
        ps.column_dimensions[c].width = w

    # ---- one sheet per condition: experimental points + both model curves ----
    for lab, g in groups.items():
        ws = wb.create_sheet(SHEET[lab][:31])
        ws.cell(1, 1, f"{lab} -- Li, {g['med']}, {g['size']:g} um, {g['vel']:.0f} m/day, {g['IS']:.0f} mM"
                      f"   |   columns {', '.join(k[2] for k in g['ks'])}   |   RP branch {g['branch']}"
                      f", inlet pts scored {g['nin'] or 'half-split (5)'}").font = Bf
        ws.cell(2, 1, "'exp' = measured (BTEC floored at log10 C/C0 = -6, a below-detection fill, not a "
                      "measurement). 'fit' curves are per column; the plotted line is their MEAN, given "
                      "in the two 'MEAN' column pairs.").font = IT
        row0 = 4
        for name, xlab, ylab, ekey, fkey in (("BTEC", "pore volumes", "log10 C/C0", "bt_exp", "bt_fit"),
                                             ("RP (retention profile)", "distance (m)", "log10 spheres",
                                              "rp_exp", "rp_fit")):
            ws.cell(row0, 1, name).font = Bf
            hdr, data_cols = [], []
            for k in g['ks']:
                d = FIT[(lab, k[2])]['kr']
                hdr += [f"Li.{k[2]} x", f"Li.{k[2]} exp"]; data_cols.append(d[ekey])
            for tag, var in (("+k_r", 'kr'), ("no-k_r", 'no')):
                for k in g['ks']:
                    d = FIT[(lab, k[2])][var]
                    hdr += [f"Li.{k[2]} {tag} xfit", f"Li.{k[2]} {tag} fit"]; data_cols.append(d[fkey])
            for tag, var in (("+k_r", 'kr'), ("no-k_r", 'no')):
                x, y = mean_curve([FIT[(lab, k[2])][var][fkey] for k in g['ks']])
                hdr += [f"MEAN {tag} xfit", f"MEAN {tag} fit"]; data_cols.append(np.column_stack([x, y]))
            ws.cell(row0 + 1, 1, f"x = {xlab};  y = {ylab}").font = IT
            hd(ws, row0 + 2, hdr)
            nmax = max(len(a) for a in data_cols)
            for i in range(nmax):
                for j, a in enumerate(data_cols):
                    if i < len(a):
                        ws.cell(row0 + 3 + i, 2 * j + 1, float(a[i, 0]))
                        ws.cell(row0 + 3 + i, 2 * j + 2, float(a[i, 1]))
            row0 += nmax + 5
    xp = os.path.join(args.outdir, "fits_canonical_IHOP.xlsx")
    wb.save(xp)
    print(f"wrote {os.path.basename(xp)}  ({len(wb.sheetnames)} sheets)")

    # ---- stats JSON, so the write-ups read these numbers instead of quoting them ----
    # Added 2026-08-25 when the k_r section moved into HydeqComparisonFullSet.docx. Every number in
    # that section is read from here; nothing is typed into the prose. This project has twice shipped
    # a document whose literals had drifted from the fits, so the rule is: if a document states a
    # number, a script must have written it.
    blocks = {b: dict(kr=sum(FIT[k]['kr2'][b] for k in FIT),
                      no=sum(FIT[k]['no'][b] for k in FIT))
              for b in ("rp_level", "rp_shape", "plateau", "tail_level", "tail_slope")}
    ex_all = [100.0 * (FIT[k]['no']['cost'] - FIT[k]['kr2']['cost']) / FIT[k]['kr2']['cost'] for k in FIT]
    stats = dict(n_columns=len(FIT), n_conditions=len(groups),
                 total_kr=sum(FIT[k]['kr2']['cost'] for k in FIT),
                 total_nokr=sum(FIT[k]['no']['cost'] for k in FIT),
                 median_excess_pct=float(np.median(ex_all)),
                 blocks={b: dict(kr=v['kr'], no=v['no'], delta=v['no'] - v['kr'])
                         for b, v in blocks.items()},
                 per_column={f"{lab}/Li.{col}": dict(
                     kr=FIT[(lab, col)]['kr2']['cost'], no=FIT[(lab, col)]['no']['cost'],
                     excess_pct=100.0 * (FIT[(lab, col)]['no']['cost'] - FIT[(lab, col)]['kr2']['cost'])
                     / FIT[(lab, col)]['kr2']['cost']) for (lab, col) in FIT})
    stats['total_excess_pct'] = 100.0 * (stats['total_nokr'] - stats['total_kr']) / stats['total_kr']
    sp = os.path.join(args.outdir, "canon_nokr_stats.json")
    json.dump(stats, open(sp, "w"), indent=1)
    print(f"wrote {os.path.basename(sp)}")

    # ---- summary ----
    tot_k = sum(FIT[key]['kr2']['cost'] for key in FIT)
    tot_n = sum(FIT[key]['no']['cost'] for key in FIT)
    print(f"\nCANONICAL FIVE, {len(FIT)} Li columns: total cost +k_r {tot_k:.2f} -> no-k_r {tot_n:.2f}"
          f"  ({100*(tot_n-tot_k)/tot_k:+.1f}%)")
    ex = sorted(((100.0 * (FIT[key]['no']['cost'] - FIT[key]['kr2']['cost']) / FIT[key]['kr2']['cost']),
                 f"{key[0]}/Li.{key[1]}") for key in FIT)
    print(f"per-column excess cost: median {np.median([e for e, _ in ex]):+.1f}%, "
          f"range {ex[0][0]:+.1f}% ({ex[0][1]}) to {ex[-1][0]:+.1f}% ({ex[-1][1]})")
    for tag, var in (("+k_r", 'kr'), ("no-k_r", 'no')):
        rail = [f"{lab}/Li.{col}:{','.join(FIT[(lab, col)][var]['railed'])}"
                for (lab, col) in FIT if FIT[(lab, col)][var]['railed']]
        print(f"railed {tag} parameters: " + (", ".join(rail) if rail else "NONE"))
    # Where does removing k_r hurt? Sum each cost block over the ten columns.
    print(f"\n{'block':12s}{'+k_r':>10s}{'no-k_r':>10s}{'delta':>10s}")
    for b in ("rp_level", "rp_shape", "plateau", "tail_level", "tail_slope"):
        a = sum(FIT[key]['kr2'][b] for key in FIT); c = sum(FIT[key]['no'][b] for key in FIT)
        print(f"{b:12s}{a:10.2f}{c:10.2f}{c-a:+10.2f}")


if __name__ == "__main__":
    main()
