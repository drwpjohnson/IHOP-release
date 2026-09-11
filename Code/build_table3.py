"""build_table3.py -- regenerate the fit-quality table from the
CURRENT UnfavorableMaster.xlsx, as markdown plus a JSON the .docx builder reads.

WHY IT EXISTS. The circulating Table3_fit_quality_fullset.md and Table3_fit_quality_SI.docx were
generated before the 2026-08-24 objective corrections and are stale for the two conditions that the
branch-aware RP-shape window reclassified. The workbook sheet itself IS current; only the derived
documents were not. This script removes the hand-transcription step that let them drift.

It reads the 'Fit quality' sheet and writes:
    Table3_fit_quality_fullset.md     -- markdown table + the analysis paragraph
    table3_rows.json                  -- rows + summary stats for build_manuscript_tables.js

** THE CONVENTION CAVEAT IS NOT OPTIONAL. ** Costs are comparable only within one inlet-window
convention. Two conditions (Li quartz 1.1 um at 3 and 6 mM) are scored with the 4-point inlet window
and the other seventeen with the half-split; the 4-point window targets a far steeper measured rise, so
those two show LARGER costs even where the fit is closer to the data. Any ranking across the whole
table, or against a pre-2026-08-24 number, is invalid. The convention-independent columns are RP RMS
and RP peak depth, and those are what a reader should compare.

Note for anyone comparing against the previously published median of 11.8: that value is still the
median of the SEVENTEEN half-split conditions. The all-19 median of 12.4 is higher only because two
conditions moved to a harder scoring window. The fit did not degrade.

Usage:  python3 build_table3.py --master UnfavorableMaster.xlsx
"""
import argparse, json
import numpy as np
import openpyxl

SHEET = "Fit quality"
# Manuscript label style: "Tong, GB, 0.2 um, 4 m/d, 20 mM"
def pretty(cond):
    p = cond.split()
    study = p[0]
    med = "GB" if p[1] == "glass" else "Qtz"
    size = p[2].replace("um", " µm")
    vel = p[3].replace("md", " m/d")
    IS = p[4].replace("mM", " mM")
    return f"{study}, {med}, {size}, {vel}, {IS}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--md", default="Table3_fit_quality_fullset.md")
    ap.add_argument("--json", default="table3_rows.json")
    args = ap.parse_args()

    ws = openpyxl.load_workbook(args.master, data_only=True)[SHEET]
    rows = []
    for r in ws.iter_rows(min_row=5, values_only=True):
        if not r or not isinstance(r[0], str) or not r[0].strip():
            continue
        if r[0].startswith("median"):
            continue
        if not ("glass" in r[0] or "quartz" in r[0]):
            continue
        f = lambda v: (float(v) if v not in (None, "") else 0.0)
        rows.append(dict(cond=r[0], label=pretty(r[0]),
                         rp_level=f(r[1]), rp_shape=f(r[2]), rp_total=f(r[3]),
                         plateau=f(r[4]), tail_level=f(r[5]), tail_slope=f(r[6]),
                         btec_total=f(r[7]), total=f(r[8]),
                         window=str(r[9]), rp_rms=f(r[10]),
                         peak_model=f(r[11]), peak_meas=f(r[12])))

    tot = [x["total"] for x in rows]
    half = [x for x in rows if x["window"] == "half"]
    four = [x for x in rows if x["window"] != "half"]
    S = dict(n=len(rows), median=float(np.median(tot)), mx=float(max(tot)),
             mx_cond=rows[int(np.argmax(tot))]["label"],
             median_half=float(np.median([x["total"] for x in half])), n_half=len(half),
             median_four=float(np.median([x["total"] for x in four])), n_four=len(four),
             rms_median=float(np.median([x["rp_rms"] for x in rows])),
             rms_max=float(max(x["rp_rms"] for x in rows)),
             shape_frac=float(np.median([x["rp_shape"] / x["total"] for x in rows if x["total"] > 0])),
             plateau_nonzero=[x["label"] for x in rows if x["plateau"] > 0.01])
    json.dump(dict(rows=rows, summary=S), open(args.json, "w"), indent=1)

    L = []
    L.append("**Fit quality (full set).** Weighted cost (½·Σ weighted residual²) "
             "per condition, split into RP (level, shape) and BTEC (plateau, tail-level, tail-slope) "
             "parts. Replicate conditions are the mean over columns.")
    L.append("")
    L.append("> **⚠ Costs are comparable only WITHIN one inlet-window convention.** Peaked "
             "conditions are scored with a 4-point inlet window, non-peaking conditions with the "
             "half-split. The 4-point window targets the measured inlet rise over x = 1–7 cm, far "
             "steeper than the 1–11 cm half-split average, so a peaked condition is scored "
             "against a harder target and shows a larger cost *even when its fit is closer to the "
             "data*. Do not rank across the table, and do not compare any value here against a "
             "pre-2026-08-24 number. The convention-independent metrics are RP RMS and RP peak depth.")
    L.append("")
    L.append("| condition | RP level | RP shape | RP total | Plateau | Tail level | Tail slope | "
             "BTEC total | TOTAL | window | RP RMS | peak cm (model / measured) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for x in rows:
        pk = ("—" if x["peak_meas"] == 0 and x["peak_model"] == 0
              else f"{x['peak_model']:.1f} / {x['peak_meas']:.1f}")
        L.append(f"| {x['label']} | {x['rp_level']:.2f} | {x['rp_shape']:.2f} | {x['rp_total']:.2f} | "
                 f"{x['plateau']:.2f} | {x['tail_level']:.2f} | {x['tail_slope']:.2f} | "
                 f"{x['btec_total']:.2f} | {x['total']:.2f} | {x['window']} | {x['rp_rms']:.3f} | {pk} |")
    L.append("")
    L.append(f"*n = {S['n']}. Median total {S['median']:.1f}; max {S['mx']:.1f} ({S['mx_cond']}). "
             f"Within the half-split group (n = {S['n_half']}) the median is {S['median_half']:.1f}; "
             f"within the 4-point group (n = {S['n_four']}) it is {S['median_four']:.1f} — the two "
             f"are not comparable. RP RMS, which is convention-independent, has median "
             f"{S['rms_median']:.3f} and max {S['rms_max']:.3f} log units across all "
             f"{S['n']} conditions.*")
    open(args.md, "w").write("\n".join(L) + "\n")
    print(f"wrote {args.md} and {args.json}  ({len(rows)} conditions)")
    print(f"  median {S['median']:.1f} | max {S['mx']:.1f} ({S['mx_cond']})")
    print(f"  half-split n={S['n_half']} median {S['median_half']:.1f} | "
          f"4-point n={S['n_four']} median {S['median_four']:.1f}")
    print(f"  RP RMS median {S['rms_median']:.3f} max {S['rms_max']:.3f}")
    print(f"  plateau penalty non-zero on: {S['plateau_nonzero']}")


if __name__ == "__main__":
    main()
