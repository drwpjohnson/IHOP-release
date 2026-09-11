"""kr_trend.py -- trends in the crawl->wall release (reentrainment) rate k_r under the CURRENT Serial-3 fits
(r_s FIXED at favorable anchor; a_s/a_m/f_x/k_r free per column; v_ns 5%; -6 BTEC floor; IS<=1 mM dropped).

Consolidates the earlier build_krtrend.py + kr_necessity.py + the three figure scripts. Produces:
  * k_r_trend.xlsx  -- sheets: 'k_r fitted (new)', 'reference constants', 'DLVO-Kramers curve',
                       'k_r necessity (shared const)'.
  * kr_vs_size.png, kr_vs_IS.png, kr_vs_velocity.png  (standalone 2D figures per axis).
    Filenames dropped the 'new_' prefix 2026-08-24 (W.P.J.) -- 'new' dates a file relative to a moment
    that has passed, which is exactly how stale artefacts end up looking current. All three share ONE
    y-range (KR_YLIM) so the panels can be read against each other, and every point is clip-checked.

** OBJECTIVE CORRECTED 2026-08-24 (W.P.J.); FINDING BELOW RE-RUN AND RE-RECORDED THE SAME DAY. **
This script had been running the SUPERSEDED dead-zone plateau term (band over PV 1.3-3.5) while
unfav_master_fit.py used the adopted MEAN-LOG target (PV 1.2-4, +-0.25 dex, W_PLAT=20) -- see
plateau_rs_decision.md s1. It has now been brought in line, and the branch-aware RP-shape inlet
window (plateau_rs_decision.md s6) added. Both change k_r.
  AUDIT TRAIL -- the two pre-correction sets disagreed with EACH OTHER, which is how the drift was
  caught: this docstring said glass +4.3% / quartz +0.5%, constants 4.5e-5 / 2.0e-5, ratio 2.3x;
  kr_trend_analysis.md said +4.2% / +1.9%, constants 4.5e-5 / 1.45e-5, ratio 3.1x (superseded). Neither was
  reproducible from this script. Both are now replaced by the verified numbers below.

FINDING (2026-08-24; re-verified 2026-08-25 under the accum convention): a single per-medium
constant suffices -- pinning k_r costs only +4.8% (glass, n=18) / +0.9% (quartz, n=11) excess cost, with
a_s/a_m/f_x free to compensate. That is the load-bearing claim.
  ** DO NOT restate this as "k_r is size-, IS-, and velocity-INDEPENDENT" (as this docstring did until
  2026-08-24). The necessity penalty says a constant is SUFFICIENT; it does not say the per-column values
  are featureless. On the IS axis they are not: with the figure y-limits opened to show the columns
  sitting on the 1e-6 bound -- which the old limits CLIPPED -- quartz 1.1 um declines ~6.5x in geometric
  mean from 3 mM to 20 mM (3.2x excluding the degenerate floor-hit M). Both statements are true; the
  small penalty means that decline is absorbable given the ~decade of per-column scatter. Quote the
  penalty, not "independent". See kr_trend_analysis.md. **

** RE-RUN 2026-08-25 UNDER THE ACCUM CONVENTION (W.P.J.). unfav_master_fit.py now fits the
ACCUMULATED solid phase at excision; the eq (4) injection-window snapshot is retired as invalid
(70% of the run happens after it). Necessity is essentially unchanged: +4.8% glass / +0.9% quartz,
against +4.3%/+0.8% before -- the load-bearing claim is untouched.
  THE CLEAN-SET FILTER HAD TO BE REPLACED, and the refit is what exposed it. It was a ONE-SIDED
  floor test (k_r <= 1.5e-6). Li.M's k_r moved from 1.00e-6, railed at the LOWER bound, to 5.63e-3 --
  3.75 dex -- at a cost unchanged to two decimals (0.72 -> 0.72). The floor test caught that column
  before and does not catch it now, so a column carrying ZERO information about k_r swung the quartz
  geomean from 1.97e-5 to 3.30e-5 and the ratio from 2.27x to 1.35x. Identifiability is two-sided;
  which bound a degenerate column drifts to is not the criterion. The filter is now the pinning
  penalty itself: a column whose cost is insensitive to k_r (<1%) cannot vote on its value. That
  excludes 9 of 29 columns -- stricter and more honest than the 2 the floor test caught. **
Fair constants (geomean over IDENTIFIABLE columns, pinning penalty >= 1%): glass 3.75e-5/s (n=14),
quartz 1.82e-5/s (n=6), i.e. quartz 2.06x below glass -- consistent with the superseded 2.13x recorded under
the snapshot convention, so the medium offset survives both the convention change and the corrected
filter. (Clean-over-all-quartz is 1.14x and is NOT the number to quote; it is kept in the workbook
only so the difference stays visible.)
The DLVO/Kramers single-colloid escape prediction sweeps 584x over 0.1-2.0 um and is refuted
(data flat). Largest pinning penalties: quartz Tong.B +51.3% (0.5 um 20 mM), glass Li.L +33.7%
(1.1 um 50 mM), glass Tong.AK +18.4%, glass Tong.U +15.6% (50 mM), quartz Li.P +15.6% -- so the 50 mM
points are no longer the ONLY sizeable ones, and that claim must not be repeated.
Contrast: f_x IS |U_sec|-driven over the SAME columns (see fx_trend.py) -> reentrainment and focusing have
different mechanisms. Reading: k_r = flow-structural release (expulsion at the rear flow stagnation point, RFSP),
not DLVO escape; the ~2.1x glass/quartz offset reflects grain angularity/RFSP geometry, not Hamaker. A faint
hint k_r(8 m/d) > k_r(4 m/d) in the two matched pairs (0.2 um 2.9->6.2e-5; 0.5 um 1.6->5.7e-5) is the
advective signature RFSP expulsion would predict (underpowered: single 4 m/d columns).
See Records/kr_trend_analysis.md.

Run from Code/ with the cleaned CSV in ../Data/ (needs unfav_master_fit.py alongside).  Usage: python3 kr_trend.py
"""
import numpy as np, warnings, functools, collections, json, matplotlib
warnings.filterwarnings("ignore"); print = functools.partial(print, flush=True); matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import openpyxl
from openpyxl.styles import Font

# ONE shared y-range for all three k_r figures (W.P.J., 2026-08-24). Upper 2e-4 sits just above the
# largest fitted k_r (1.25e-4, Tong.CO); the old 1.5e-2 left two empty decades that made every panel
# look flatter than it is. Lower 5e-7 sits BELOW the 1e-6 optimiser bound, so the floor-hit columns are
# visible as floor-hits instead of being cropped away.
# Upper limit raised 2e-4 -> 1e-2 (W.P.J., 2026-08-25). Under the accum convention Li.M's
# unidentifiable k_r sits at 5.63e-3, which 2e-4 CLIPPED. Clipping is how the earlier "flat 3-20 mM"
# error happened, so the axis follows the data even at the cost of empty space; the degenerate point
# is excluded from the constants (see the identifiability filter in main()) but is still SHOWN.
KR_YLIM = (5e-7, 1e-2)
exec(open("unfav_master_fit.py").read().split("# ---- fit all unfavorable")[0])  # engine, seed_rs, loaders


def fit(k, kr_fixed=None, nin=None):
    """Fit a column; k_r free (4 params) unless kr_fixed given (3 params). Returns dict with k_r /s and cost.

    OBJECTIVE IS NOW IDENTICAL TO unfav_master_fit.py (corrected 2026-08-24, W.P.J.):
      * PLATEAU = MEAN-LOG TARGET over PV 1.2-4 with +-PLAT_TOL dex tolerance, W_PLAT=20. This script
        previously used the SUPERSEDED dead-zone over PV 1.3-3.5 (penalise only outside the measured
        [min,max] band), which plateau_rs_decision.md s1 replaced because the dead-zone let the plateau
        HEIGHT float anywhere in the band, so declining/scattered breakthroughs sat ~1 log too high.
      * RP-SHAPE INLET WINDOW is branch-aware: nin=None -> half-split (non-peaking condition), nin=4 ->
        first 4 points (peaked condition).  Branch is decided ONCE PER CONDITION by majority over
        replicate columns, in main(), exactly as unfav_master_fit.py does.  See plateau_rs_decision.md s6.
    ** All k_r values from this script are therefore NEW; every k_r number in Records/kr_trend_analysis.md
       predates this correction and is superseded. **
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
        a_s = 1 - 10 ** p[0]; am = 10 ** p[1]; fx = 10 ** p[2]
        krr = kr_fixed if kr_fixed is not None else 10 ** p[3]
        r = eng.run(kk, a_s, am, fx, krr)
        rl = np.interp(rx, r['x'], np.maximum(r['rp'], 1e-300)) / V_MS; lS = logK + np.log10(np.maximum(rl, 1e-300))
        rpx = W_RP * (lS - rlog); sm, sn = sl(rx, lS, nin); shp = W_SHAPE * np.array([sm - si, sn - so])
        mlog = np.mean(np.log10(np.maximum(np.interp(pvw, r['tp'], r['C']), 1e-6))); dev = mlog - dmean
        pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])   # mean-log target, not a dead-zone
        tl = W_TAIL * (np.log10(np.maximum(np.interp(pv[tm], r['tp'], r['C']), 1e-6)) - lc[tm]) if tm.sum() else np.array([0.])
        slm = ts(r['tp'], np.log10(np.maximum(r['C'], 1e-6))); tsl = W_TSLOPE * np.array([slm - sld if sld == sld else 0.])
        return np.concatenate([rpx, shp, pl, tl, tsl])
    if kr_fixed is not None:
        lo = [-3.3, -3.3, np.log10(1e-4)]; hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0)]
        starts = [[-1.5, -1., np.log10(.005)], [-.5, -.3, np.log10(.02)], [-2.3, -1.5, np.log10(.001)]]
    else:
        lo = [-3.3, -3.3, np.log10(1e-4), np.log10(1e-6)]; hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0), np.log10(.1)]
        starts = [[-1.5, -1., np.log10(.005), krs], [-.5, -.3, np.log10(.02), krs], [-2.3, -1.5, np.log10(.001), krs - 0.5]]
    best = None
    for s0 in starts:
        rr = least_squares(resid, s0, bounds=(lo, hi), max_nfev=80)
        if best is None or rr.cost < best.cost: best = rr
    kr = kr_fixed if kr_fixed is not None else 10 ** best.x[3]
    # a_s / a_m / f_x added 2026-08-26 so a pinned-k_r refit can be used downstream without a second
    # copy of this objective (delta_fx_probe.py). Purely additive -- existing callers index by key.
    return dict(kr=kr, cost=float(best.cost), size=size, vel=vel, IS=m['IS'], med=med, tag=k[0] + '.' + k[2],
                kr_pv=kr * (L / eng.v),
                a_s=float(1 - 10 ** best.x[0]), a_m=float(10 ** best.x[1]), fx=float(10 ** best.x[2]))


# ---- DLVO/Kramers single-colloid escape prediction (20 mM glass), from dlvo_kramers_size.py ----
_e = 1.602e-19; _kB = 1.381e-23; _T = 293.2; _kT = _kB * _T; _eps0 = 8.854e-12; _epsr = 80.; _NA = 6.022e23
_mu = 1e-3; _A = 7.17e-21; _lam = 100e-9; _I = 20.; _zc = -0.050; _zg = -0.051
_kap = np.sqrt(2 * _NA * _e ** 2 * _I / (_eps0 * _epsr * _kT)); _kinv = 1 / _kap; _h = np.linspace(2e-9, 120e-9, 60000)
def usec(a):
    U = ((-_A * a / (6 * _h)) / (1 + 14 * _h / _lam) + 64 * np.pi * _eps0 * _epsr * a * (_kT / _e) ** 2
         * np.tanh(_e * _zc / (4 * _kT)) * np.tanh(_e * _zg / (4 * _kT)) * np.exp(-_kap * _h)) / _kT
    m = _h > 8e-9; i = np.where(m)[0][0] + np.argmin(U[m]); return max(-U[i], 0.)
def kr_abs(a): return (_kT / (6 * np.pi * _mu * a) / _kinv ** 2) * np.exp(-usec(a))


def main():
    US = [k for k, m in meta.items() if m['chem'] == 'unfavorable' and (m['IS'] is None or m['IS'] > 1)]
    # ---- branch per CONDITION by majority over replicate columns, as unfav_master_fit.py does ----
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
        if len(set(colbr[k] for k in ks)) > 1:
            print(f"  NOTE replicates disagree: {key} -> majority = {b}")
    nnm = sum(1 for k in NIN if NIN[k])
    print(f"branch-aware RP-shape window: {nnm}/{len(NIN)} columns scored on {NIN_PEAKED} inlet points, rest half-split")
    FREE = {}
    for k in US:
        d = fit(k, None, nin=NIN.get(k))
        if d: FREE[k] = d
    gk = [FREE[k]['kr'] for k in FREE if FREE[k]['med'] == 'glass']
    qk = [FREE[k]['kr'] for k in FREE if FREE[k]['med'] == 'quartz']
    Fg = float(np.exp(np.mean(np.log(gk)))); Fq = float(np.exp(np.mean(np.log(qk))))
    # necessity: pin per medium to the ALL-column geomean (never the clean one -- the necessity
    # penalty must not be helped by dropping points). Run this BEFORE the clean geomean, because
    # the clean set is now defined from the per-column penalty computed here.
    nec = {'glass': {'F': Fg, 'free': 0., 'pin': 0., 'rows': []}, 'quartz': {'F': Fq, 'free': 0., 'pin': 0., 'rows': []}}
    PEN = {}
    for k in FREE:
        med = FREE[k]['med']; F = nec[med]['F']; cf = FREE[k]['cost']; cp = fit(k, F, nin=NIN.get(k))['cost']
        nec[med]['free'] += cf; nec[med]['pin'] += cp
        PEN[k] = 100 * (cp - cf) / max(cf, 1e-9)
        nec[med]['rows'].append((FREE[k]['tag'], FREE[k]['size'], FREE[k]['vel'], FREE[k]['IS'],
                                 round(FREE[k]['kr'], 8), round(cf, 2), round(cp, 2), round(PEN[k], 1)))
    # ---- 'clean' geomean = columns where k_r is IDENTIFIABLE (W.P.J., 2026-08-25) ----
    # WAS a one-sided floor test (k_r <= 1.5e-6). That is broken, and the accum refit proved it:
    # Li.M's k_r moved from 1.00e-6 (railed at the LOWER bound) to 5.63e-3 -- 3.75 dex -- at a cost
    # unchanged to 2 dp (0.72 -> 0.72). The floor test caught it before and does not catch it now, so
    # a column carrying ZERO information about k_r swung the headline quartz geomean from 1.97e-5 to
    # 3.30e-5 and the glass/quartz ratio from 2.27x to 1.35x. Identifiability is two-sided; the bound
    # a degenerate column happens to drift to is not the criterion.
    # The right test is already computed above: if pinning k_r to the medium constant costs this
    # column essentially nothing, the column cannot vote on what that constant should be.
    PEN_MIN = 1.0        # percent excess cost from pinning; below this, k_r is unconstrained here
    ident = {k for k in FREE if PEN[k] >= PEN_MIN}
    gkc = [FREE[k]['kr'] for k in ident if FREE[k]['med'] == 'glass']
    qkc = [FREE[k]['kr'] for k in ident if FREE[k]['med'] == 'quartz']
    Fg_clean = float(np.exp(np.mean(np.log(gkc)))) if gkc else float('nan')
    Fq_clean = float(np.exp(np.mean(np.log(qkc)))) if qkc else float('nan')
    excl = sorted(FREE[k]['tag'] for k in FREE if k not in ident)
    print(f"identifiability filter (pinning penalty < {PEN_MIN}%): excluded {len(excl)} column(s) {excl}")
    gp = 100 * (nec['glass']['pin'] - nec['glass']['free']) / nec['glass']['free']
    qp = 100 * (nec['quartz']['pin'] - nec['quartz']['free']) / nec['quartz']['free']
    print(f"glass n={len(gk)} geomean {Fg:.3e} (clean {Fg_clean:.3e}); "
          f"quartz n={len(qk)} geomean {Fq:.3e} (clean {Fq_clean:.3e})")
    print(f"ratio glass/quartz: {Fg_clean/Fq_clean:.2f}x symmetric-clean (QUOTE THIS) ; "
          f"{Fg_clean/Fq:.2f}x clean-over-all-quartz")
    print(f"NECESSITY: glass +{gp:.1f}% ; quartz +{qp:.1f}%")

    # ================= workbook =================
    B = Font(bold=True); IT = Font(italic=True); wb = openpyxl.Workbook(); wb.remove(wb.active)
    def hd(ws, r, vals):
        for j, v in enumerate(vals, 1): c = ws.cell(r, j, v); c.font = B

    def grp(d):
        if d['med'] == 'quartz': return 'quartz Li 1.1um' if abs(d['size'] - 1.1) < .15 else 'quartz Tong 0.5um'
        return 'glass 4 m/d' if d['vel'] == 4 else 'glass 8 m/d'
    ws = wb.create_sheet("k_r fitted (new)")
    ws.cell(1, 1, "Fitted crawl->wall release k_r -- CURRENT fits (r_s fixed; k_r FREE per column; -6 floor; IS>1 mM)").font = B
    ws.cell(2, 1, "Scatter data for the k_r-vs-size/IS/velocity figures. k_r in /s and /PV.").font = IT
    hd(ws, 4, ["medium", "col", "size_um", "v_mday", "IS_mM", "k_r_/s", "k_r_/PV", "fit_cost", "plot_group"])
    for i, k in enumerate(sorted(FREE, key=lambda k: (FREE[k]['med'], FREE[k]['size'], FREE[k]['vel'])), 5):
        d = FREE[k]
        for j, v in enumerate([d['med'], d['tag'], d['size'], d['vel'], d['IS'], round(d['kr'], 8), round(d['kr_pv'], 4), round(d['cost'], 2), grp(d)], 1):
            ws.cell(i, j, v)
    for c, w in zip("ABCDEFGHI", [8, 9, 8, 8, 7, 12, 10, 9, 16]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("reference constants")
    ws.cell(1, 1, "Reference k_r constants (per-medium)").font = B
    ws.cell(2, 1, "Geomean of free fits. 'clean' excludes fit-floor hits (k_r<=1.5e-6): ONE per medium under the corrected objective -- glass 0.5 um 50 mM (U) and quartz 1.1 um 20 mM (M). NOT 'the two 50 mM points' (the quartz floor-hit is at 20 mM). Superseded necessity-fit values: glass 5.58e-5, quartz 1.87e-5.").font = IT
    hd(ws, 4, ["line", "k_r_/s", "n", "note"])
    ws.cell(5, 1, "glass geomean (all)"); ws.cell(5, 2, round(Fg, 8)); ws.cell(5, 3, len(gk))
    ws.cell(6, 1, "glass geomean (clean)"); ws.cell(6, 2, round(Fg_clean, 8)); ws.cell(6, 3, sum(1 for x in gk if x > 1.5e-6)); ws.cell(6, 4, "excl floor-hit U (0.5 um 50 mM)")
    ws.cell(7, 1, "quartz geomean (all)"); ws.cell(7, 2, round(Fq, 8)); ws.cell(7, 3, len(qk))
    ws.cell(8, 1, "quartz geomean (clean)"); ws.cell(8, 2, round(Fq_clean, 8)); ws.cell(8, 3, sum(1 for x in qk if x > 1.5e-6)); ws.cell(8, 4, "excl floor-hit M (1.1 um 20 mM)")
    ws.cell(9, 1, "glass/quartz ratio (clean/clean)"); ws.cell(9, 2, round(Fg_clean / Fq_clean, 2)); ws.cell(9, 4, "SYMMETRIC -- quote this")
    ws.cell(10, 1, "glass/quartz ratio (clean/all)"); ws.cell(10, 2, round(Fg_clean / Fq, 2)); ws.cell(10, 4, "asymmetric; shown only for continuity with the pre-2026-08-24 sheets")
    for c, w in zip("ABCD", [24, 12, 6, 28]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("DLVO-Kramers curve")
    ws.cell(1, 1, "DLVO/Kramers single-colloid escape (20 mM glass) -- the REFUTED steep size dependence").font = B
    kref = kr_abs(0.55e-6); swing = kr_abs(0.05e-6) / kr_abs(1.0e-6)
    ws.cell(2, 1, f"k_r_abs=(D/kinv^2)exp(-|Usec|); anchored to glass clean geomean at 1.1um. Size swing 0.1->2.0um = {swing:.0f}x (data flat).").font = IT
    hd(ws, 4, ["diam_um", "|U_sec|_kT", "k_r_abs_/s", "k_r_anchored_/s"])
    for i, dia in enumerate(np.logspace(np.log10(0.1), np.log10(2.0), 40), 5):
        a = dia / 2 * 1e-6; ka = kr_abs(a)
        for j, v in enumerate([round(dia, 3), round(usec(a), 3), ka, Fg_clean * ka / kref], 1): ws.cell(i, j, v)
    for c, w in zip("ABCD", [10, 12, 14, 16]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("k_r necessity (shared const)")
    ws.cell(1, 1, "k_r NECESSITY: pin to one per-medium constant vs free per column (all sizes/velocities/IS)").font = B
    ws.cell(2, 1, f"GLASS pin {Fg:.3e}/s: free {nec['glass']['free']:.1f} pinned {nec['glass']['pin']:.1f} -> +{gp:.1f}%. QUARTZ pin {Fq:.3e}/s: free {nec['quartz']['free']:.1f} pinned {nec['quartz']['pin']:.1f} -> +{qp:.1f}%. One per-medium constant suffices => k_r NOT size/IS/velocity driven.").font = IT
    ws.cell(3, 1, f"Fair constants (both media excl their floor-hit): glass {Fg_clean:.2e}/s, quartz {Fq_clean:.2e}/s ({Fg_clean/Fq_clean:.2f}x). NOTE: the pin used in the necessity test above is the ALL-column geomean (Fg, Fq), not the clean constant -- the necessity penalty must not be helped by dropping points.").font = IT
    _pen = sorted(((row[7], med, row[0], row[1], row[3]) for med in ('glass', 'quartz') for row in nec[med]['rows']), reverse=True)[:5]
    ws.cell(4, 1, "Largest pinning penalties: " + "; ".join(f"{m} {t} ({s} um, {int(i_) if i_ else '?'} mM) +{p:.1f}%" for p, m, t, s, i_ in _pen)
            + ". The 50 mM points are NOT the only sizeable ones under the corrected objective -- do not repeat that claim.").font = IT
    r = 4
    for med in ('glass', 'quartz'):
        r += 1; ws.cell(r, 1, med.upper()).font = B; r += 1
        hd(ws, r, ["col", "size_um", "v_mday", "IS_mM", "k_r_free_/s", "cost_free", "cost_pinned", "delta_pct"]); r += 1
        for row in sorted(nec[med]['rows'], key=lambda z: (z[1], z[3])):
            for j, v in enumerate(row, 1): ws.cell(r, j, v)
            r += 1
        ws.cell(r, 1, "TOTAL").font = B; ws.cell(r, 6, round(nec[med]['free'], 1)).font = B
        ws.cell(r, 7, round(nec[med]['pin'], 1)).font = B
        ws.cell(r, 8, round(100 * (nec[med]['pin'] - nec[med]['free']) / nec[med]['free'], 1)).font = B; r += 1
    for c, w in zip("ABCDEFGH", [10, 8, 8, 7, 12, 10, 11, 9]): ws.column_dimensions[c].width = w
    wb.save("../Manuscript/FigsExcelsUnfav/k_r_trend.xlsx"); print("wrote ../Manuscript/FigsExcelsUnfav/k_r_trend.xlsx")

    # ================= figures =================
    GL, QL = '#1f77b4', '#7b2d8b'; DG = np.logspace(np.log10(0.1), np.log10(2.0), 40)
    def R(med): return [FREE[k] for k in FREE if FREE[k]['med'] == med]

    def clipcheck(ax, ys, name):
        """Warn if any plotted point falls outside the y-limits.

        The old hard-coded limits (3e-6 lower) silently CLIPPED the two columns whose k_r sits on the
        1e-6 optimiser bound -- Tong.U and Li.M -- so the figures showed fewer points than the fit
        produced, with nothing to indicate it. Points vanishing off an axis is a data-integrity fault,
        not a cosmetic one; this makes it noisy instead of silent."""
        lo, hi = ax.get_ylim()
        out = [y for y in ys if not (lo <= y <= hi)]
        if out:
            print(f"  !! {name}: {len(out)} point(s) CLIPPED outside y-limits "
                  f"[{lo:.1e},{hi:.1e}]: {['%.2e' % y for y in sorted(out)]}")

    # A) vs SIZE (IS=20)
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    for v in R('glass'):
        if v['IS'] == 20: ax.scatter(v['size'], v['kr'], s=80, color=('#1f77b4' if v['vel'] == 4 else '#2a9d8f'), edgecolor='k', zorder=5)
    for v in R('quartz'):
        if v['IS'] == 20: ax.scatter(v['size'], v['kr'], s=100, marker='s', color=QL, edgecolor='k', zorder=6)
    ax.plot(DG, [Fg_clean * kr_abs(d / 2 * 1e-6) / kref for d in DG], color='grey', lw=1.5, ls=':', label=f'DLVO/Kramers ({swing:.0f}x) - REFUTED')
    ax.axhline(Fg_clean, color=GL, lw=1.4, ls='--', label=f'glass k_r ~ {Fg_clean:.1e}/s')
    ax.axhline(Fq_clean, color=QL, lw=1.4, ls='--', label=f'quartz k_r ~ {Fq_clean:.1e}/s (~{Fg_clean/Fq_clean:.1f}x below)')
    ax.scatter([], [], s=80, color='#1f77b4', edgecolor='k', label='glass 4 m/d'); ax.scatter([], [], s=80, color='#2a9d8f', edgecolor='k', label='glass 8 m/d')
    ax.scatter([], [], s=100, marker='s', color=QL, edgecolor='k', label='quartz')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xticks([0.1, 0.2, 0.5, 1.1, 2.0]); ax.set_xticklabels(['0.1', '0.2', '0.5', '1.1', '2.0'])
    ax.set_ylim(*KR_YLIM); ax.set_xlabel('colloid diameter (µm)'); ax.set_ylabel('fitted k_r (/s)')
    ax.set_title(f'Serial-3 (r_s fixed): reentrainment k_r vs colloid size (IS=20 mM)\nglass flat; single-colloid DLVO/Kramers ({swing:.0f}x) refuted; necessity +{gp:.1f}% (glass)')
    ax.grid(alpha=.3, which='both'); ax.legend(fontsize=8, loc='lower left')
    clipcheck(ax, [v['kr'] for v in FREE.values() if v['IS'] == 20], 'kr_vs_size')
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/kr_vs_size.png", dpi=140)

    # B) vs IS (constant size+vel series; IS>1)
    fig, ax = plt.subplots(figsize=(8.4, 5.8)); G = collections.defaultdict(list)
    for v in FREE.values():
        if v['IS'] and v['IS'] > 1: G[(v['med'], round(v['size'], 1), v['vel'])].append((v['IS'], v['kr']))
    sty = {('glass', 1.1, 4.0): ('#1f77b4', 'o', 'glass 1.1µm 4md'), ('glass', 0.5, 4.0): ('#2a9d8f', 'o', 'glass 0.5µm 4md'),
           ('glass', 2.0, 8.0): ('#5dade2', 'o', 'glass 2.0µm 8md'), ('quartz', 1.1, 4.0): ('#7b2d8b', 's', 'quartz 1.1µm 4md'),
           ('quartz', 0.5, 4.0): ('#c39bd3', 's', 'quartz 0.5µm 4md')}
    for key, pts in G.items():
        if key not in sty: continue
        c, mk, lab = sty[key]; ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=75, color=c, marker=mk, edgecolor='k', zorder=5, label=lab)
        bI = collections.defaultdict(list)
        for IS, kr in pts: bI[IS].append(kr)
        xs = sorted(bI); ax.plot(xs, [np.exp(np.mean(np.log(bI[x]))) for x in xs], '-', color=c, lw=1.3, alpha=.7)
    ax.axhline(Fg_clean, color=GL, lw=1.2, ls='--', alpha=.7); ax.axhline(Fq_clean, color=QL, lw=1.2, ls='--', alpha=.7)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xticks([3, 6, 20, 50]); ax.set_xticklabels(['3', '6', '20', '50'])
    ax.set_ylim(*KR_YLIM); ax.set_xlabel('ionic strength (mM)'); ax.set_ylabel('fitted k_r (/s)')
    # Title corrected 2026-08-24. It read "flat 3-20 mM; weak (floor-limited) drop at 50 mM" -- which was
    # only defensible while the 1e-6 floor-hits were being CLIPPED off the bottom of the axis. With them
    # visible, quartz 1.1 um declines about 6x in geometric mean from 3 mM (2.7e-5) to 20 mM (4.1e-6),
    # and its floor-hit is at 20 mM, not 50. That is NOT flat. It remains compatible with the +0.8%
    # quartz pinning penalty -- a spread this noisy is absorbable by one constant -- but the figure must
    # not assert flatness the points do not show. See kr_trend_analysis.md.
    ax.set_title('Serial-3 (r_s fixed): reentrainment k_r vs ionic strength\n'
                 'glass ~flat to 20 mM then drops at 50 mM; quartz declines ~6x over 3-20 mM '
                 '(still within the +0.8% pinning penalty)')
    ax.grid(alpha=.3, which='both'); ax.legend(fontsize=8, loc='lower left')
    clipcheck(ax, [p[1] for key, pts in G.items() if key in sty for p in pts], 'kr_vs_IS')
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/kr_vs_IS.png", dpi=140)

    # C) vs VELOCITY -- EVERY matched (medium, size, ionic strength) group that has two velocities.
    # This previously hard-coded "glass 0.2 and 0.5 um at 20 mM", which silently omitted the one QUARTZ
    # velocity pair in the dataset (0.5 um, 50 mM: Tong.H at 4 m/d, Tong.R at 8 m/d). Quartz was not
    # absent from the data, only from the plot -- so the figure implied the velocity hint was a
    # glass-only observation when in fact quartz shows the same direction. Found by W.P.J., 2026-08-24.
    fig, ax = plt.subplots(figsize=(8.0, 5.8))
    VG = collections.defaultdict(list)
    for v in FREE.values():
        if v['IS'] and v['IS'] > 1:
            VG[(v['med'], round(v['size'], 1), v['IS'])].append((v['vel'], v['kr']))
    VG = {k: v for k, v in VG.items() if len({p[0] for p in v}) > 1}
    PAL = ['#e67e22', '#16a085', '#7b2d8b', '#5dade2', '#b03a5b']
    vy = []
    for i, key in enumerate(sorted(VG, key=lambda z: (z[0], z[1], z[2]))):
        pts = VG[key]; med, size, IS = key
        c = PAL[i % len(PAL)]; mk = 'o' if med == 'glass' else 's'
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=95, color=c, marker=mk, edgecolor='k',
                   zorder=5, label=f'{med} {size:g} µm, {IS:.0f} mM')
        vy += [p[1] for p in pts]
        bv = collections.defaultdict(list)
        for vv, kr in pts: bv[vv].append(kr)
        xs = sorted(bv); ax.plot(xs, [np.exp(np.mean(np.log(bv[x]))) for x in xs], '-', color=c, lw=1.5, alpha=.75)
    ax.axhline(Fg_clean, color=GL, lw=1.3, ls='--', alpha=.7, label=f'glass k_r ~ {Fg_clean:.1e}/s')
    ax.axhline(Fq_clean, color=QL, lw=1.3, ls='--', alpha=.7, label=f'quartz k_r ~ {Fq_clean:.1e}/s')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xticks([4, 8]); ax.set_xticklabels(['4', '8'])
    ax.set_xlim(3.2, 10); ax.set_ylim(*KR_YLIM)
    # A log x-axis spanning less than one decade lets matplotlib label the MINOR ticks too, which put a
    # stray '6 x 10^0' between the only two velocities in the dataset. Only 4 and 8 exist -- say so.
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('pore velocity (m/day)'); ax.set_ylabel('fitted k_r (/s)')
    ax.set_title('Serial-3 (r_s fixed): reentrainment k_r vs pore velocity\n'
                 'every matched size+IS pair - no strong dependence; faint k_r(8)>k_r(4) = advective (RFSP) hint')
    ax.grid(alpha=.3, which='both'); ax.legend(fontsize=8, loc='lower right')
    clipcheck(ax, vy, 'kr_vs_velocity')
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/kr_vs_velocity.png", dpi=140)
    print("wrote kr_vs_size.png, kr_vs_IS.png, kr_vs_velocity.png")


if __name__ == "__main__":
    main()
