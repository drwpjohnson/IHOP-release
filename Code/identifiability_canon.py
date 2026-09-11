"""identifiability_canon.py -- local (correlation) identifiability of the Serial-3 parameters,
recomputed on the CURRENT objective for the canonical five conditions.

Replaces the earlier identifiability analysis, which was computed on the older consol_rel engine
(Code/identif_kr.py, four Li conditions) and predates BOTH 2026-08-24 objective corrections -- the
mean-log plateau target and the branch-aware RP-shape window. See Records/plateau_rs_decision.md s1, s6.

WHAT IT COMPUTES. At each column's fitted optimum, the numerical Jacobian J of the WEIGHTED residual
vector with respect to log10 of six parameters, then the correlation matrix from the pseudo-inverse of
J'J. Working in log10 makes the correlations scale-free and matches how the parameters are fitted.

    k_f   interception rate, r_s * v            (PINNED in the fit; freed here to ask the question)
    a_s   single-interception attachment efficiency
    a_m   multiple-interception attachment efficiency
    f_x   recruitment into the grain-contact crawl
    v_ns  near-surface / crawl velocity fraction    (PINNED at 5% in the fit; freed here)
    k_r   crawl -> wall release

The point of freeing k_f and v_ns is precisely that they are pinned in the production fit: the table
answers "what would happen if they were not", which is the justification for pinning them.

ALIASING AMPLIFICATION = marginal sd / conditional sd, per parameter, in log10 units. Conditional sd
is 1/sqrt(diag(J'J)) -- the sd if every other parameter were held fixed. Marginal sd is sqrt(diag(cov))
-- the sd with the others free to compensate. Their ratio is how much the parameter's uncertainty is
inflated by trade-off with the rest. A ratio of 1 means no aliasing; tens means the parameter is only
determined jointly with its partners.

WHY pinv AND NOT inv. J'J is singular by construction here -- only the PRODUCT r_s*a_s is identifiable
(Records/plateau_rs_decision.md s3), so the k_f and a_s columns of J are near-parallel. A plain inverse
either fails or returns garbage that looks like a result. The pseudo-inverse handles the flat direction
and the k_f<->a_s correlation then shows up honestly as ~-1.

FINDINGS (2026-08-25), which correct the manuscript in two places:
  * near-surface cluster |corr| spans 0.80-1.00, NOT 0.90-1.00; aliasing 7.3x-44.6x
  * k_f is near-independent of the cluster ON GLASS (|corr| <= 0.27) but NOT on quartz, where
    k_f<->f_x reaches 0.88. The blanket "<= 0.4" claim is false.
  * k_f<->a_s reaches 1.00 on four of five conditions -- the r_s*a_s product degeneracy, absent from
    the manuscript's analysis and the quantitative justification for pinning r_s.
  * AFTER pinning r_s and v_ns, k_r aliasing collapses from 7.3-15.7x to 1.0-1.2x, and no production
    parameter exceeds 1.4x. The manuscript's central identifiability claim is therefore CONFIRMED.

Usage:  python3 identifiability_canon.py
        (run from Code/ with the cleaned CSV in ../Data/ and unfav_master_fit.py alongside)
"""
import argparse, json
import numpy as np
from scipy.optimize import least_squares

exec(open("unfav_master_fit.py").read().split("# ---- fit all unfavorable")[0])  # Eng, seed_rs, sl, ts, weights

# canonical five, in matched-pair order: (study, column, label)
CANON = [("Li", "R",  "glass 1.1 um 6 mM"),
         ("Li", "V",  "quartz 1.1 um 6 mM"),
         ("Li", "O",  "glass 1.1 um 20 mM"),
         ("Li", "P",  "quartz 1.1 um 20 mM"),
         ("Li", "AE", "quartz 1.1 um 3 mM")]
PNAMES = ["k_f", "a_s", "a_m", "f_x", "v_ns", "k_r"]
NEAR = ["f_x", "v_ns", "k_r"]          # the near-surface cluster
NIN_PEAKED_ = 4


def branch_windows(cols, meta):
    """Per-column RP-shape window, decided per CONDITION by majority -- as unfav_master_fit.py does."""
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
        for k in ks: NIN[k] = NIN_PEAKED_ if b == "peaked" else None  # matches renamed condition_branch (exec-imported above)
    return NIN


def make_resid(k, cols, meta, nin):
    """Weighted residual as a function of theta = log10([k_f, a_s, a_m, f_x, v_ns, k_r])."""
    m = meta[k]; bt = cols[k]['BTEC'].copy(); rp = cols[k]['RP']
    med = m['medium']; vel = m['vel']; C0 = m['C0']; theta_p = THETA[med]; V_MS = vel / DAY
    eng = Eng(vel); logK = np.log10(REV * T0 * theta_p * C0 * Vref)
    bt[:, 1] = np.maximum(bt[:, 1], -6.0)
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]
    si, so = sl(rx, rlog, nin)
    wm = (pv > 1.2) & (pv < 4.0); pvw = pv[wm] if wm.sum() else pv
    dmean = float(lc[wm].mean()) if wm.sum() else float(lc.mean())
    tm = pv > 4.2; sld = ts(pv, lc)

    def resid(th):
        kf, a_s, a_m, fx, vns, kr = [10.0 ** t for t in th]
        a_s = min(a_s, 1 - 1e-9)
        r = eng.run(kf, a_s, a_m, fx, kr, vns=vns)
        rl = np.interp(rx, r['x'], np.maximum(r['rp'], 1e-300)) / V_MS
        lS = logK + np.log10(np.maximum(rl, 1e-300))
        rpx = W_RP * (lS - rlog)
        sm, sn = sl(rx, lS, nin); shp = W_SHAPE * np.array([sm - si, sn - so])
        mlog = np.mean(np.log10(np.maximum(np.interp(pvw, r['tp'], r['C']), 1e-6))); dev = mlog - dmean
        pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])
        tl = (W_TAIL * (np.log10(np.maximum(np.interp(pv[tm], r['tp'], r['C']), 1e-6)) - lc[tm])
              if tm.sum() else np.array([0.]))
        slm = ts(r['tp'], np.log10(np.maximum(r['C'], 1e-6)))
        tsl = W_TSLOPE * np.array([slm - sld if sld == sld else 0.])
        return np.concatenate([rpx, shp, pl, tl, tsl])
    return resid, med, vel


def fit_column(k, cols, meta, nin):
    """Production fit: 4 free params, k_f and v_ns pinned. Returns theta at the optimum."""
    m = meta[k]; med = m['medium']
    rs0, _ = seed_rs(med, m['size'], m['vel']); kf = rs0 * (m['vel'] / DAY)
    resid6, _, _ = make_resid(k, cols, meta, nin)
    krs = np.log10(KR_MED[med])

    def r4(p):
        return resid6([np.log10(kf), np.log10(max(1 - 10 ** p[0], 1e-12)), p[1], p[2],
                       np.log10(0.05), p[3]])
    lo = [-3.3, -3.3, np.log10(1e-4), np.log10(1e-6)]
    hi = [np.log10(1 - 1e-4), np.log10(.999), np.log10(1.0), np.log10(.1)]
    best = None
    for s0 in ([-1.5, -1., np.log10(.005), krs], [-.5, -.3, np.log10(.02), krs],
               [-2.3, -1.5, np.log10(.001), krs - 0.5]):
        rr = least_squares(r4, s0, bounds=(lo, hi), max_nfev=80)
        if best is None or rr.cost < best.cost: best = rr
    a_s = 1 - 10 ** best.x[0]
    th = np.array([np.log10(kf), np.log10(a_s), best.x[1], best.x[2], np.log10(0.05), best.x[3]])
    return th, float(best.cost)


def jacobian(resid, th, h=1e-4):
    """Central-difference Jacobian in log10 parameter space."""
    r0 = resid(th); J = np.zeros((len(r0), len(th)))
    for j in range(len(th)):
        tp = th.copy(); tm_ = th.copy(); tp[j] += h; tm_[j] -= h
        J[:, j] = (resid(tp) - resid(tm_)) / (2 * h)
    return J


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="Data/LiTong_experimental_data_tidy.csv")
    ap.add_argument("--out", default="identifiability_canon.json")
    args = ap.parse_args()

    # `cols` and `meta` come from the exec'd unfav_master_fit.py header, which loads the tidy CSV at
    # import time -- exactly as kr_trend.py and fx_trend.py rely on. There is no separate load() call,
    # and the --csv flag below is therefore documentation of what the header reads, not an override.
    NIN = branch_windows(cols, meta)
    key = {}
    for st, cl, lab in CANON:
        kk = [k for k in meta if k[0] == st and k[2] == cl]
        if not kk: raise SystemExit(f"column {st}.{cl} not found")
        key[(st, cl)] = kk[0]

    OUT = {}
    print(f"{'condition':22s} {'cost':>7s}  " + "  ".join(f"{n:>6s}" for n in PNAMES))
    for st, cl, lab in CANON:
        k = key[(st, cl)]; nin = NIN.get(k)
        th, cost = fit_column(k, cols, meta, nin)
        resid, med, vel = make_resid(k, cols, meta, nin)
        J = jacobian(resid, th)
        JtJ = J.T @ J
        cov = np.linalg.pinv(JtJ)
        dd = np.sqrt(np.clip(np.diag(cov), 0, None))
        with np.errstate(invalid='ignore', divide='ignore'):
            corr = cov / np.outer(dd, dd)
        diag = np.diag(JtJ)
        cond_sd = np.array([1 / np.sqrt(d) if d > 0 else np.inf for d in diag])
        amp = np.where(cond_sd > 0, dd / cond_sd, np.inf)
        OUT[lab] = dict(medium=med, cost=cost,
                        params={n: float(10 ** t) for n, t in zip(PNAMES, th)},
                        corr=corr.tolist(), amp=amp.tolist(),
                        cond_sd=cond_sd.tolist(), marg_sd=dd.tolist(),
                        condJtJ=float(np.linalg.cond(JtJ)), window=("4-pt" if nin else "half"))
        print(f"{lab:22s} {cost:7.2f}  " + "  ".join(f"{10**t:6.2e}"[:6] for t in th))

    print("\n" + "=" * 96)
    print("PAIRWISE |correlation| in log10 parameter space, at each fitted optimum")
    print("=" * 96)
    idx = {n: i for i, n in enumerate(PNAMES)}
    pairs = [("f_x", "v_ns"), ("f_x", "k_r"), ("v_ns", "k_r"),
             ("k_f", "f_x"), ("k_f", "v_ns"), ("k_f", "k_r"), ("k_f", "a_s"), ("a_s", "a_m")]
    print(f"{'condition':22s} " + " ".join(f"{a}/{b}".rjust(11) for a, b in pairs))
    for lab, d in OUT.items():
        C = np.array(d['corr'])
        print(f"{lab:22s} " + " ".join(f"{abs(C[idx[a], idx[b]]):11.2f}" for a, b in pairs))

    print("\nALIASING AMPLIFICATION (marginal sd / conditional sd, log10 units)")
    print(f"{'condition':22s} " + " ".join(f"{n:>9s}" for n in PNAMES))
    for lab, d in OUT.items():
        a = d['amp']
        print(f"{lab:22s} " + " ".join(f"{a[idx[n]]:9.1f}" for n in PNAMES))

    print("\nSUMMARY over the five conditions")
    C = {p: [abs(np.array(d['corr'])[idx[p[0]], idx[p[1]]]) for d in OUT.values()] for p in pairs}
    for p in pairs:
        v = C[p]
        print(f"   |corr| {p[0]:>5s}/{p[1]:<5s}  min {min(v):.2f}  max {max(v):.2f}  median {np.median(v):.2f}")
    for n in NEAR:
        v = [d['amp'][idx[n]] for d in OUT.values()]
        print(f"   aliasing {n:>5s}      min {min(v):.1f}x  max {max(v):.1f}x  median {np.median(v):.1f}x")
    v = [d['amp'][idx['k_f']] for d in OUT.values()]
    print(f"   aliasing {'k_f':>5s}      min {min(v):.1f}x  max {max(v):.1f}x  median {np.median(v):.1f}x")

    # ---- AFTER pinning: the production 4-parameter fit -------------------------------------------
    # The manuscript asserts the degeneracy "was resolved by pinning v_ns to 5% of v and then fitting
    # f_x, after which k_r became identifiable". That is a testable claim and it is tested here, not
    # assumed: rebuild the Jacobian over ONLY the four parameters that are actually free in production
    # (a_s, a_m, f_x, k_r) and see whether k_r's aliasing collapses.
    print("\n" + "=" * 96)
    print("AFTER PINNING r_s AND v_ns -- the production 4-parameter fit (a_s, a_m, f_x, k_r)")
    print("=" * 96)
    P4 = ["a_s", "a_m", "f_x", "k_r"]
    i4 = [PNAMES.index(n) for n in P4]
    print(f"{'condition':22s} " + " ".join(f"{a}/{b}".rjust(9) for a, b in
                                           [("a_s", "a_m"), ("f_x", "k_r"), ("a_s", "f_x"), ("a_m", "k_r")])
          + "   " + " ".join(f"amp {n}".rjust(9) for n in P4))
    A4 = {}
    for st, cl, lab in CANON:
        k = key[(st, cl)]; nin = NIN.get(k)
        th, _ = fit_column(k, cols, meta, nin)
        resid, _, _ = make_resid(k, cols, meta, nin)

        def r4(p4, th=th, resid=resid):
            t = th.copy()
            for j, ii in enumerate(i4): t[ii] = p4[j]
            return resid(t)
        J = jacobian(r4, th[i4])
        JtJ = J.T @ J
        cov = np.linalg.pinv(JtJ); dd = np.sqrt(np.clip(np.diag(cov), 0, None))
        with np.errstate(invalid='ignore', divide='ignore'):
            C = cov / np.outer(dd, dd)
        diag = np.diag(JtJ)
        csd = np.array([1 / np.sqrt(d) if d > 0 else np.inf for d in diag])
        amp = dd / csd
        j4 = {n: i for i, n in enumerate(P4)}
        A4[lab] = dict(corr=C.tolist(), amp=amp.tolist())
        print(f"{lab:22s} " +
              " ".join(f"{abs(C[j4[a], j4[b]]):9.2f}" for a, b in
                       [("a_s", "a_m"), ("f_x", "k_r"), ("a_s", "f_x"), ("a_m", "k_r")]) +
              "   " + " ".join(f"{amp[j4[n]]:9.1f}" for n in P4))
    print("\n  k_r aliasing, before vs after pinning:")
    for lab in OUT:
        b = OUT[lab]['amp'][PNAMES.index("k_r")]; a = A4[lab]['amp'][P4.index("k_r")]
        print(f"    {lab:22s} {b:6.1f}x  ->  {a:5.1f}x")
    for lab in A4: OUT[lab]['production4'] = A4[lab]

    json.dump(OUT, open(args.out, "w"), indent=1)
    print("\nwrote " + args.out)


if __name__ == "__main__":
    main()
