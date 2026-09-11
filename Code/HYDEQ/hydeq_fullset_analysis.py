"""hydeq_fullset_analysis.py -- the FULL-SET (29 unfavorable columns) IHOP vs HYDEQ comparison,
scored on bases that survive the composition of the experimental programme.

Reads the full-set fit cache (hydeq_full.json, from `hydeq_fit.py --conv accum` with no --canon)
and writes hydeq_fullset_stats.json + a printed summary. Nothing is refitted here.

** WHY THIS SCRIPT EXISTS -- THREE WEIGHTING TRAPS, ALL OF WHICH I FELL INTO (W.P.J., 2026-08-25) **

1. PER-COLUMN TOTALS WEIGHT BY REPLICATE COUNT. The programme ran 3 columns at glass 0.2 um/8 m/d
   and 1 at glass 0.1 um/8 m/d. Summing cost over columns silently triples the first condition.
   Aggregate PER CONDITION -- average the replicates first, then combine conditions.

2. THE SET IS 15 NON-PEAKING CONDITIONS TO 3 PEAKED. An unweighted total is ~83% decided by the
   class where conventional structures win, so it reports the sampling, not the physics. Report the
   two branch medians separately and, if one number is wanted, the MACRO mean of the two.
   ** On the raw per-column total, Hydeq7 (7 par) BEATS IHOP: 609.0 vs 777.1. That is a true
   statement about this column set and it must be reported, not buried. It is also the wrong
   summary, for the reason above. Print both. **

3. RAW "CORRECT BRANCH" COUNTS ARE INFLATED BY THE SAME IMBALANCE. M3_strain scores 22/29 while
   being STRUCTURALLY INCAPABLE of a peaked profile -- psi(x) is monotone decreasing, so it
   is right 22 times for no reason at all. Score branch as a classification: sensitivity,
   specificity, balanced accuracy and MCC. M3's MCC is 0.00; M4_dualpor buys sensitivity with 14
   false peaks (MCC 0.20).

THE PRIMARY EVIDENCE IS THE TRANSITION, NOT THE RESIDUAL.

** LANGUAGE (W.P.J., 2026-08-25). This is DESCRIPTION, not prediction, and must not be written up as
prediction. An earlier draft of this docstring said the eq-15 margin "predicts the measured branch
out of sample". That is wrong: a_s and a_m are fitted to these very columns, and the objective
contains the two-segment retention-profile log-slope term (W_SHAPE), so branch information is
inside the fit. Nothing here is held out. **

What IS true, and is the actual claim: the branch is not a degree of freedom of its own. There is no
branch parameter and no switch. It falls out of Al-Zghoul (2025) eq 15 -- peaked <=>
a_m > a_s/(1-a_s) -- from two parameters that must simultaneously serve the breakthrough curve and
the retention-profile level. Ranking the columns by margin log10[a_m(1-a_s)/a_s] puts 28 of 29 on
the correct side of zero; the single miss (Li.P, +0.04) sits on the boundary, as does the nearest
correct call (Tong.H, -0.05). Every glass column sits at <= -0.46 while quartz spans -2.06 to +2.91:
mineralogy sets the regime, ionic strength and size move you along it and across the crossing.

That ordering is the point. IHOP describes all 29 columns with one structure whose fitted parameters
land in a physically coherent arrangement, rather than requiring a different mechanism per regime.
The predictive claim is downstream and NOT demonstrated here: parameters that are interpretable and
ordered are what would make prediction possible later. Say "describes", not "predicts".
  CAVEAT, stated wherever the margin is: the three largest positive margins (Li.AE, Li.AB, Li.AH)
  all have a_s RAILED at its 1e-4 floor, which makes the threshold tiny and the margin huge. Only
  the SIGN is meaningful for those; the magnitude is a bound artifact.

Peak LOCATION is the discriminator that no conventional structure survives. Hydeq7 classifies the
branch well (MCC 0.91) yet places 0 of 7 peaks within 1 cm -- it can say a peak exists, not where.
Hydeq5 and Hydeq7 put Li.AH's peak at 19.9 cm in a 20 cm column against a measured 7.0 cm.

Usage:  python3 hydeq_fullset_analysis.py [--cache hydeq_full.json] [--csv ../Data/...] [--out .]
        Run from Code/HYDEQ/.
"""
import argparse, collections, csv, json, math, os
import numpy as np

ORDER = ["IHOP", "M1_1site", "M2_2site", "M3_strain", "M4_dualpor",
         "M5_strain_block", "M6_strain_dp", "M7_all"]
LABEL = {"IHOP": "IHOP Serial-3", "M1_1site": "Hydeq1  one kinetic site",
         "M2_2site": "Hydeq2  two kinetic sites", "M3_strain": "Hydeq3  site + straining",
         "M4_dualpor": "Hydeq4  site + dual porosity",
         "M5_strain_block": "Hydeq5  straining + blocking",
         "M6_strain_dp": "Hydeq6  straining + dual porosity",
         "M7_all": "Hydeq7  all mechanisms"}
PEAK_TOL_CM = 1.0          # half a sampling interval; profiles are sampled every 2 cm
RAIL_AS = 1e-4 * 1.01      # a_s at or below this is railed at its lower bound


def sizeclass(s):
    s = float(s)
    return 1.1 if 0.9 <= s <= 1.15 else round(s, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="hydeq_full.json")
    ap.add_argument("--csv", default="../Data/LiTong_experimental_data_tidy.csv")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    store = json.load(open(args.cache))
    meta = {}
    _csv_rows = list(csv.DictReader(open(args.csv)))
    # GUARD, 2026-09-01: the shared master CSV was silently overwritten with a 352-row/Li-only
    # a_mg-probe subset for a month before anyone noticed -- see Records/CLAUDE.md.
    _srcs = set(r['source'] for r in _csv_rows)
    assert len(_csv_rows) >= 1200 and 'Li' in _srcs and 'Tong' in _srcs, (
        f"CSV at {args.csv!r} looks like a subset ({len(_csv_rows)} rows, sources={_srcs}), not the "
        "full master (~1529 rows, both Li and Tong) -- refusing to analyze a silently-truncated dataset.")
    for r in _csv_rows:
        if r["chemistry"] != "unfavorable":
            continue
        IS = r["IS_mM"]
        if IS != "" and float(IS) <= 1.0:
            continue
        meta[f"{r['source']}.{r['workbook_col']}"] = dict(
            study=r["source"], medium=r["medium"], size=float(r["colloid_um"]),
            sizecls=sizeclass(r["colloid_um"]), vel=float(r["velocity_mday"]), IS=float(IS))

    cost = collections.defaultdict(dict); rms = collections.defaultdict(dict)
    bm = collections.defaultdict(dict); pk = collections.defaultdict(dict)
    ihop = {}; bd = {}; pd_ = {}
    for k, v in store.items():
        conv, st, med, col, mdl, w = k.split("|")
        if conv != "accum":
            continue
        c = f"{st}.{col}"
        cost[mdl][c] = v["cost"]; rms[mdl][c] = v["rpRMS"]
        bm[mdl][c] = v["branch_m"]; pk[mdl][c] = v["peak_m"] * 100
        bd[c] = v["branch_d"]; pd_[c] = v["peak_d"] * 100
        if mdl == "IHOP":
            ihop[c] = v
    cols = sorted(bd)
    # NOTE (terminology pass, 2026-09-01, W.P.J.): "monotone" is retired project-wide. bd/bm now carry
    # "peaked"/"non-peaking" literally, because hydeq_fit.py's branch_d/branch_m (HYDEQ/hydeq_fit.py --
    # a separate, independently-COPIED engine, not exec-imported from unfav_master_fit.py) were renamed
    # to match on the same date. res's field names below were renamed in lockstep with the one consumer
    # that reads them, build_hydeq_fullset_docx.js -- do not rename one side without the other.
    peaked = [c for c in cols if bd[c] == "peaked"]
    nonpeaking = [c for c in cols if bd[c] == "non-peaking"]

    # ---- conditions: physical condition ACROSS studies, using the master's size classing ----
    cond = collections.defaultdict(list)
    for c in cols:
        m = meta[c]
        cond[(m["medium"], m["sizecls"], m["vel"], m["IS"])].append(c)
    cond_branch = {}
    for k, v in cond.items():
        nm = sum(1 for c in v if bd[c] == "peaked")
        cond_branch[k] = "peaked" if nm > len(v) - nm else "non-peaking"

    # res is serialized verbatim to hydeq_fullset_stats.json, read by build_hydeq_fullset_docx.js and
    # check_consistency.py -- check_consistency.py's tracked keys (n_columns, n_conditions,
    # total_excess_pct) are unaffected by this rename; build_hydeq_fullset_docx.js was updated to match
    # the renamed keys below in the same pass.
    res = {"n_columns": len(cols), "n_conditions": len(cond),
           "n_peaked_columns": len(peaked), "n_nonpeaking_columns": len(nonpeaking),
           "n_peaked_conditions": sum(1 for k in cond_branch if cond_branch[k] == "peaked"),
           "peak_tol_cm": PEAK_TOL_CM, "structures": {}}

    print(f"{len(cols)} columns -> {len(cond)} conditions "
          f"({res['n_peaked_conditions']} peaked, "
          f"{len(cond) - res['n_peaked_conditions']} non-peaking); "
          f"columns {len(peaked)} peaked / {len(nonpeaking)} non-peaking\n")

    hdr = (f"{'structure':30s}{'par':>4s}{'col TOT':>9s}{'cond TOT':>10s}{'cond med':>9s}"
           f"{'no-pk':>8s}{'peaked':>9s}{'MACRO':>8s}{'MCC':>7s}{'peak':>7s}{'RMS med':>9s}{'RMS max':>9s}")
    print(hdr); print("-" * len(hdr))
    for m in ORDER:
        percol = [cost[m][c] for c in cols]
        percond = {k: float(np.mean([cost[m][c] for c in v])) for k, v in cond.items()}
        cnonpk = [percond[k] for k in cond if cond_branch[k] == "non-peaking"]
        cpk = [percond[k] for k in cond if cond_branch[k] == "peaked"]
        macro = (float(np.median(cnonpk)) + float(np.median(cpk))) / 2
        TP = sum(1 for c in peaked if bm[m][c] == "peaked")
        FN = len(peaked) - TP
        FP = sum(1 for c in nonpeaking if bm[m][c] == "peaked")
        TN = len(nonpeaking) - FP
        sens = TP / (TP + FN) if TP + FN else 0.0
        spec = TN / (TN + FP) if TN + FP else 0.0
        den = math.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
        mcc = ((TP * TN - FP * FN) / den) if den else 0.0
        npk = sum(1 for c in peaked if abs(pk[m][c] - pd_[c]) <= PEAK_TOL_CM)
        r = [rms[m][c] for c in cols]
        worst_i = int(np.argmax(percol))
        d = dict(label=LABEL[m], npar=store[[k for k in store if f"|{m}|" in k][0]]["npar"],
                 col_total=float(sum(percol)), col_median=float(np.median(percol)),
                 col_worst=float(max(percol)), col_worst_column=cols[worst_i],
                 cond_total=float(sum(percond.values())),
                 cond_median=float(np.median(list(percond.values()))),
                 cond_median_nonpeaking=float(np.median(cnonpk)), cond_median_peaked=float(np.median(cpk)),
                 macro=macro, TP=TP, FN=FN, FP=FP, TN=TN, sens=sens, spec=spec,
                 balacc=(sens + spec) / 2, mcc=mcc,
                 can_switch=bool(TP + FP) and bool(TN + FN),
                 peaks_within_tol=npk, n_peaked=len(peaked),
                 rms_median=float(np.median(r)),
                 rms_median_nonpeaking=float(np.median([rms[m][c] for c in nonpeaking])),
                 rms_median_peaked=float(np.median([rms[m][c] for c in peaked])),
                 rms_worst=float(max(r)),
                 peaks={c: dict(measured=pd_[c], model=pk[m][c]) for c in peaked})
        res["structures"][m] = d
        print(f"{LABEL[m]:30s}{d['npar']:>4d}{d['col_total']:9.1f}{d['cond_total']:10.1f}"
              f"{d['cond_median']:9.2f}{d['cond_median_nonpeaking']:8.2f}{d['cond_median_peaked']:9.2f}"
              f"{macro:8.2f}{mcc:7.2f}{npk:>4d}/{len(peaked)}{d['rms_median']:9.3f}{d['rms_worst']:9.3f}")

    # ---- eq-15 margin: where the branch falls out of the fitted alphas ----
    marg = []
    for c in cols:
        a_s = ihop[c]["a_s"]; a_m = ihop[c]["a_m"]
        thr = a_s / (1 - a_s)
        mg = math.log10(a_m / thr) if a_m > 0 and thr > 0 else float("nan")
        pred = "peaked" if mg > 0 else "non-peaking"
        marg.append(dict(column=c, **meta[c], a_s=a_s, a_m=a_m, margin=mg,
                         predicted=pred, measured=bd[c], correct=(pred == bd[c]),
                         a_s_railed=bool(a_s <= RAIL_AS),
                         peak_measured=pd_[c], peak_model=pk["IHOP"][c]))
    marg.sort(key=lambda z: -z["margin"])
    ok = sum(1 for z in marg if z["correct"])
    res["eq15"] = dict(correct=ok, n=len(marg), rows=marg,
                       misses=[z["column"] for z in marg if not z["correct"]],
                       glass_max_margin=max(z["margin"] for z in marg if z["medium"] == "glass"),
                       quartz_min=min(z["margin"] for z in marg if z["medium"] == "quartz"),
                       quartz_max=max(z["margin"] for z in marg if z["medium"] == "quartz"))
    print(f"\neq-15 branch criterion (a consequence of the fitted a_s/a_m, not a separate parameter "
          f"-- DESCRIPTION, not prediction): {ok}/{len(marg)} on the correct side of zero; "
          f"misses {res['eq15']['misses']}")
    print(f"  every glass column <= {res['eq15']['glass_max_margin']:+.2f}; "
          f"quartz spans {res['eq15']['quartz_min']:+.2f} to {res['eq15']['quartz_max']:+.2f}")
    railed = [z['column'] for z in marg if z['a_s_railed']]
    print(f"  a_s railed at its 1e-4 floor on {len(railed)} columns {railed} -- for these the SIGN "
          f"of the margin is meaningful, the MAGNITUDE is a bound artifact")

    fn = os.path.join(args.out, "hydeq_fullset_stats.json")
    json.dump(res, open(fn, "w"), indent=1)
    print(f"\nwrote {fn}")


if __name__ == "__main__":
    main()
