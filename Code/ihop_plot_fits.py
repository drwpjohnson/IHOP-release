"""ihop_plot_fits.py -- the Serial-3 (IHOP) fit galleries: three figures, one panel-pair per condition.

    fit-gallery-glass-4mday.png    fit-gallery-glass-8mday.png    fit-gallery-quartz.png

** FILENAME PREFIX IS 'fit-gallery' AND MUST STAY THAT WAY (W.P.J., 2026-08-24). Do not prepend a model
   name such as 'Serial-3-'. The model is named in the figure TITLE, where it can be corrected in one
   place; putting it in the filename would force a rename of every downstream reference the next time the
   model designation changes. **

Each row is one physical condition: BTEC on the left (log10 C/C0 vs pore volumes), retention profile on
the right (log10 spheres vs distance). Points are the WITHIN-STUDY mean +- stdev over replicate columns;
lines are the fit. Data blue, fit red. Where both studies ran the same condition they share a row, which
is the point of the layout -- the between-study offset is then visible directly rather than inferred.

WHY THIS FILE EXISTS (W.P.J., 2026-08-24). These galleries were previously produced by an ad-hoc script
that was never saved into Code/, so the figures in circulation had no reproducer and could not be
regenerated after the objective correction. That is the same failure mode as fx_trend.xlsx (workbook with
no script) and kr_trend.py / alpha_trends.py (script with hard-coded numbers). This script is committed so
the galleries are reproducible, and it READS UnfavorableMaster.xlsx rather than re-fitting, so the figures
cannot drift from the master table: if the workbook is regenerated, the galleries follow.

WHAT IT READS. The 18 per-condition sheets of UnfavorableMaster.xlsx (written by unfav_master_fit.py),
each carrying, for BTEC and RP: per-column experimental x/y, per-column fit x/y on a common grid, and a
within-study mean/stdev block for studies with replicates. Nothing is recomputed here -- this file only
draws. If a number looks wrong in a figure it is wrong in the workbook, and the fix belongs upstream.
(18 sheets, 19 master-table rows: glass 1.1 um 4 m/day 20 mM was run by BOTH studies and shares one sheet
and one row of the gallery.)

CONVENTIONS WORTH KNOWING BEFORE READING THE FIGURES
  * The fit LINE for a study is the mean of that study's per-column fit curves, not a fit to the mean
    data. Those differ when replicates disagree; the per-column fits are in the 'Per-column fits' sheet.
  * Error bars are the stdev across replicate columns in dex, and are absent where a study contributed a
    single column -- absence of a bar means n=1, NOT a tight measurement.
  * BTEC data are floored at log10 C/C0 = -6 (data_inventory.md s366: -6 is a software fill for
    below-detection, not a measurement). A curve sitting flat on -6 is a non-detect, not a fitted value.
  * Panel axis limits are shared across all rows of a figure, and the RP y-axis is deliberately common to
    every panel, so rows can be compared by eye without rescaling.
  * The in-panel label has a PRESCRIBED field order -- study(ies), medium, velocity, size, ionic strength
    -- and lives inside the axes so the panels stay as large as possible. Do not move it outside or
    reorder the fields.

Usage:  python3 ihop_plot_fits.py --master UnfavorableMaster.xlsx  [--outdir .]
        --master is REQUIRED and has no default, for the same reason as in alpha_trends.py: a default
        path is how a stale workbook gets plotted silently.
"""
import argparse, json, os, re, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Manuscript Figure 1 is set in 18 pt; match it so the SI galleries read the same size on the page.
FS = 18
import openpyxl

LI, TONG = "#c0392b", "#1f4e79"
COLOR = {"Li": LI, "Tong": TONG}
# Series colour is by ROLE, not by study: measured data (and their error bars) blue, fit red.
DATA_COLOR, FIT_COLOR = "#1f4e79", "#c0392b"
BTEC_YLIM = (-6.4, 0.7)
RP_YLIM = (5.3, 9.7)
BTEC_XLIM = (0.0, 10.0)
RP_XLIM = (0.0, 0.200)
FLOOR = -6.0


def _f(v):
    """Cell -> float or nan. Fit cells at the floor are stored as the string '-6'."""
    if v is None or v == "":
        return np.nan
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def parse_sheet(ws):
    """-> {'BTEC': block, 'RP': block}; each block = {'exp':{col:(x,y)}, 'fit':{col:(x,y)},
    'mean':{study:(x,mean,sd)}}."""
    rows = list(ws.iter_rows(values_only=True))
    # Section markers are 'BTEC' and 'RP (retention profile)' -- match on the LEADING token, not on
    # equality. An earlier version tested `== 'RP'`, silently failed to find the RP section, and so
    # folded the RP rows into the BTEC block: RP panels came out empty AND the BTEC fit lines grew a
    # spurious limb from the RP data. Both symptoms, one cause.
    marks = {}
    for i, r in enumerate(rows):
        if r and isinstance(r[0], str):
            tok = r[0].strip().split()[0] if r[0].strip() else ""
            if tok in ("BTEC", "RP") and tok not in marks:
                marks[tok] = i
    out = {}
    order = sorted(marks.items(), key=lambda kv: kv[1])
    for n, (name, i0) in enumerate(order):
        stop = order[n + 1][1] if n + 1 < len(order) else len(rows)
        hdr = [("" if h is None else str(h)) for h in rows[i0 + 2]]
        data = rows[i0 + 3:stop]
        exp, fit, mean = {}, {}, {}
        j = 0
        while j < len(hdr):
            h = hdr[j]
            nxt = hdr[j + 1] if j + 1 < len(hdr) else ""
            if h.endswith(" xfit") and nxt.endswith(" fit"):
                tag = h[:-5]
                x = np.array([_f(d[j]) for d in data]); y = np.array([_f(d[j + 1]) for d in data])
                m = ~np.isnan(x) & ~np.isnan(y)
                fit[tag] = (x[m], y[m]); j += 2
            elif h.endswith(" x") and nxt.endswith(" exp"):
                tag = h[:-2]
                x = np.array([_f(d[j]) for d in data]); y = np.array([_f(d[j + 1]) for d in data])
                m = ~np.isnan(x) & ~np.isnan(y)
                exp[tag] = (x[m], y[m]); j += 2
            elif h.endswith(" x") and "mean log10" in nxt:
                st = h[:-2]
                x = np.array([_f(d[j]) for d in data]); y = np.array([_f(d[j + 1]) for d in data])
                sd = np.array([_f(d[j + 2]) for d in data]) if j + 2 < len(hdr) else np.full(len(x), np.nan)
                m = ~np.isnan(x) & ~np.isnan(y)
                mean[st] = (x[m], y[m], sd[m]); j += 3
            else:
                j += 1
        out[name] = dict(exp=exp, fit=fit, mean=mean)
    return out


def study_of(tag):
    return tag.split(".")[0]


def series(block, study):
    """Points (x, y, sd) for one study: the mean block if it exists, else the study's single column."""
    if study in block["mean"]:
        return block["mean"][study]
    cols = [t for t in block["exp"] if study_of(t) == study]
    if not cols:
        return None
    if len(cols) == 1:
        x, y = block["exp"][cols[0]]
        return x, y, np.full(len(x), np.nan)
    # more than one column but no mean block -- average on the first column's grid
    x0, y0 = block["exp"][cols[0]]
    ys = [np.interp(x0, *block["exp"][c]) for c in cols]
    return x0, np.mean(ys, axis=0), np.std(ys, axis=0)


def fitline(block, study):
    """Mean of that study's per-column fit curves (they share the xfit grid)."""
    cols = [t for t in block["fit"] if study_of(t) == study]
    if not cols:
        return None
    x0, _ = block["fit"][cols[0]]
    ys = []
    for c in cols:
        x, y = block["fit"][c]
        ys.append(y if len(y) == len(x0) and np.allclose(x, x0) else np.interp(x0, x, y))
    return x0, np.mean(ys, axis=0)


SHEET_RE = re.compile(r"^(gl|qu)_([0-9.]+)um_([0-9.]+)md_([0-9.]+)mM$")
LABEL_WRAP = 38          # characters; break at a ' · ' boundary past this width

# ---- the CANONICAL five (W.P.J., 2026-08-25) ----------------------------------------------------
# The same five conditions the HYDEQ comparison uses, in the same matched-pair order, so the
# IHOP-alone figure and the comparator figure show the SAME experiments row for row.
# Written as (sheet, study) pairs: the canonical set is defined as five *Li* columns, so the glass
# 20 mM row is restricted to Li even though that condition sheet also carries Tong's three
# replicates. Including Tong there would put data in the IHOP figure that is absent from the HYDEQ
# figure and break the one-to-one correspondence that is the entire reason for reusing the set.
CANON_ROWS = [
    ("gl_1.1um_4md_6mM",  "Li"),    # R  glass  6 mM   multiexponential
    ("qu_1.1um_4md_6mM",  "Li"),    # V  quartz 6 mM   peaked, peak 3.0 cm
    ("gl_1.1um_4md_20mM", "Li"),    # O  glass 20 mM   multiexponential  (Li only -- see above)
    ("qu_1.1um_4md_20mM", "Li"),    # P  quartz 20 mM  non-peaking
    ("qu_1.1um_4md_3mM",  "Li"),    # AE quartz 3 mM   peaked, peak 5.0 cm
]
CANON_OUT = "fit_canonical_IHOP.png"   # deliberately NOT fit-gallery-* : that prefix is the full set

# Optional grey-dashed overlay: the SCHEMATIC-FAITHFUL no-k_r refit (Serial-3a), mirroring the
# with/without-k_r pairing of the original Serial-3 figures. The curves are READ from canon_nokr.json,
# written by canon_nokr_fit.py -- this script still recomputes nothing. (W.P.J., 2026-08-25)
NOKR_STYLE = dict(color="0.45", ls="--", lw=1.3, zorder=3)


def wrap_subtitle(text, width=150):
    """Break the figure subtitle into lines at ';' CLAUSE boundaries only.

    Never breaks on spaces: the overlay label may contain mathtext ($\\sigma_{\\ln r_s}$) and
    splitting inside a $...$ span renders as literal TeX. Added 2026-08-28 -- the subtitle had no
    wrapping at all and a long --overlay-label ran off both edges of the figure (W.P.J.)."""
    parts = [c.strip() for c in text.split(";") if c.strip()]
    lines, cur = [], ""
    for c in parts:
        cand = c if not cur else cur + ";  " + c
        if len(cand) > width and cur:
            lines.append(cur); cur = c
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def wrap_label(s):
    """Break the in-panel label onto a second line at a field boundary, never mid-field."""
    if len(s) <= LABEL_WRAP:
        return s
    parts = s.split(" · ")
    line, out = "", []
    for p in parts:
        cand = p if not line else line + " · " + p
        if len(cand) > LABEL_WRAP and line:
            out.append(line); line = p
        else:
            line = cand
    out.append(line)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True,
                    help="path to UnfavorableMaster.xlsx -- REQUIRED, no default, so a stale workbook "
                         "can never be plotted silently (W.P.J., 2026-08-24)")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--canon", action="store_true",
                    help="draw ONLY the canonical five conditions (the HYDEQ main-text set) as "
                         "fit_canonical_IHOP.png, instead of the three full-set galleries")
    ap.add_argument("--nokr", default=None,
                    help="path to canon_nokr.json (from canon_nokr_fit.py): overlay the k_r=0 refit "
                         "as a grey dashed line. Canonical figure only.")
    # --overlay generalises --nokr: ANY per-condition {sheet: {bt:{x,y}, rp:{x,y}}} JSON can be drawn
    # in the grey dashed slot. Added 2026-08-28 for the distributed-alpha_m sigma probe. The label is
    # REQUIRED with it, because the subtitle otherwise claims the curve is the k_r=0 refit -- a silent
    # mislabelling of a figure is exactly the failure this script exists to prevent.
    # ** The overlay MUST be aggregated the way the workbook is -- mean of per-column fit CURVES over
    #    every column of the condition. Three canonical rows have replicates (V+AB+Y, P+M+S, AE+AH),
    #    so a single-column overlay plotted against a condition-mean line shows offsets that are the
    #    aggregation mismatch, not the effect being tested. That error was made and caught on
    #    2026-08-28; see Records/alpha_m_distribution.md section 6. **
    ap.add_argument("--overlay", default=None,
                    help="path to any per-condition overlay JSON, same shape as canon_nokr.json. "
                         "Mutually exclusive with --nokr; requires --overlay-label. Canonical only.")
    ap.add_argument("--overlay-label", default=None,
                    help="subtitle text for the grey dashed curve, e.g. 'global log-normal spread on "
                         "alpha_m, sigma = 1.0'. Required with --overlay.")
    # --columns draws one row per COLUMN instead of one row per condition, in the SAME panel grammar
    # (BTEC left, RP right, same axes, same label box, same overlay slot). Added 2026-08-28 after a
    # per-column figure was drawn by an ad-hoc script in a different format -- W.P.J.: "please stop
    # making new formats". Per-column exp/fit series are already in the sheets, so nothing is
    # recomputed here either. With --columns the overlay JSON is keyed by COLUMN TAG (e.g. "Li.AB"),
    # not by sheet, and no error bars are drawn: a single column has no within-study spread.
    ap.add_argument("--columns", default=None,
                    help="comma-separated column tags, e.g. Li.AB,Li.V,Li.Y,Li.AE,Li.AH. One row per "
                         "column, same format as --canon. Overlay JSON is keyed by tag.")
    ap.add_argument("--out", default=None, help="output filename (default: the mode's standard name)")
    ap.add_argument("--title", default=None, help="figure title text after the model name")
    args = ap.parse_args()
    if args.overlay and args.nokr:
        raise SystemExit("--overlay and --nokr both write the grey dashed slot; pass only one")
    if args.overlay and not args.overlay_label:
        raise SystemExit("--overlay requires --overlay-label, or the subtitle would mislabel the curve")
    overlay_label = "same model refitted with k$_r$ = 0"
    if args.overlay:
        nokr = json.load(open(args.overlay)); overlay_label = args.overlay_label
    else:
        nokr = json.load(open(args.nokr)) if args.nokr else {}
    if nokr and not (args.canon or args.columns):
        raise SystemExit("the grey dashed overlay is only defined for --canon / --columns")
    if args.columns and args.canon:
        raise SystemExit("--columns and --canon are different row schemes; pass only one")

    wb = openpyxl.load_workbook(args.master, data_only=True)
    conds = []
    for sn in wb.sheetnames:
        m = SHEET_RE.match(sn)
        if not m:
            continue
        med = "glass" if m.group(1) == "gl" else "quartz"
        conds.append(dict(sheet=sn, med=med, size=float(m.group(2)),
                          vel=float(m.group(3)), IS=float(m.group(4))))
    print(f"{len(conds)} condition sheets found in {os.path.basename(args.master)}")

    if args.columns:
        # One row per COLUMN. Locate each tag's sheet by scanning the parsed blocks.
        want = [t.strip() for t in args.columns.split(",") if t.strip()]
        where = {}
        for c in conds:
            blocks = parse_sheet(wb[c["sheet"]])
            for nm in ("BTEC", "RP"):
                for t in blocks.get(nm, {}).get("exp", {}):
                    where.setdefault(t, c)
        rows = []
        for t in want:
            if t not in where:
                raise SystemExit(f"column tag not found in any sheet: {t}")
            rows.append(dict(where[t], tag=t, only=study_of(t)))
        FIGS = [(args.title or "per-column fits", args.out or "fit-columns.png", rows)]
    elif args.canon:
        # Canonical five: explicit row list, explicit order, Li only. NOT sorted -- the matched-pair
        # order (glass 6 / quartz 6, glass 20 / quartz 20, then the 3 mM extreme) IS the content.
        by_sheet = {c["sheet"]: c for c in conds}
        rows = []
        for sn, study in CANON_ROWS:
            if sn not in by_sheet:
                raise SystemExit(f"canonical sheet missing from workbook: {sn}")
            rows.append(dict(by_sheet[sn], only=study))
        FIGS = [(args.title or "canonical five conditions", args.out or CANON_OUT, rows)]
    else:
        # Figure split and row order are FIXED (W.P.J.): glass is split by velocity, quartz is one
        # figure, and rows run (velocity, size, ionic strength). Do not re-sort.
        # Filenames keep the 'fit-gallery' prefix -- no model name in the filename (see header note).
        _s = lambda L: sorted(L, key=lambda c: (c["vel"], c["size"], c["IS"]))
        FIGS = [("Glass, 4 m/day", "fit-gallery-glass-4mday.png",
                 _s([c for c in conds if c["med"] == "glass" and c["vel"] == 4])),
                ("Glass, 8 m/day", "fit-gallery-glass-8mday.png",
                 _s([c for c in conds if c["med"] == "glass" and c["vel"] == 8])),
                ("Quartz", "fit-gallery-quartz.png",
                 _s([c for c in conds if c["med"] == "quartz"]))]

    for title, fname, sub in FIGS:
        if not sub:
            print(f"  (skip {title}: no conditions)"); continue
        n = len(sub)
        # The subtitle is composed FIRST because the header height depends on how many lines it wraps to.
        # NB: not named `sub` -- that is the loop's list of conditions, and shadowing it made the
        # closing per-figure print index a string. (W.P.J.)
        subtitle = ("each row: BTEC (left, vs PV) + RP (right, vs distance);  points = "
                    + ("single column (no error bars)" if sub[0].get("tag") else "within-study mean ± stdev")
                    + ",  lines = fit;  data blue / fit red")
        if nokr:
            subtitle += ";  grey dashed = " + overlay_label
        subtitle_lines = wrap_subtitle(subtitle)
        # Header space is reserved in INCHES, not as a fraction of the figure: the figure grows with the
        # number of rows, so a fixed y-fraction would let the subtitle drift into the title on short
        # figures and float away on tall ones.
        head_in = 1.55 + 0.34 * (len(subtitle_lines) - 1)
        fig_h = 2.55 * n + head_in
        fig, axes = plt.subplots(n, 2, figsize=(17.0, fig_h), squeeze=False)
        for i, c in enumerate(sub):
            blocks = parse_sheet(wb[c["sheet"]])
            studies = []
            for name in ("BTEC", "RP"):
                for t in blocks.get(name, {}).get("exp", {}):
                    s = study_of(t)
                    if s not in studies:
                        studies.append(s)
            studies.sort(key=lambda s: (s != "Li", s))   # Li (red) first, as in the legend note
            if c.get("only"):                            # canonical rows are restricted to one study
                studies = [s for s in studies if s == c["only"]]

            for k, (name, mk, ms) in enumerate((("BTEC", "o", 26), ("RP", "s", 34))):
                ax = axes[i][k]
                blk = blocks.get(name)
                if blk and c.get("tag"):
                    # --columns row: one column, drawn straight from the per-column series. No error
                    # bars -- a single column has no within-study spread to show.
                    col = DATA_COLOR
                    pts = blk["exp"].get(c["tag"])
                    if pts is not None:
                        ax.errorbar(pts[0], pts[1], yerr=None, fmt=mk, ms=np.sqrt(ms) * 1.3, color=col,
                                    linestyle="none", mew=0, zorder=5)
                    ln = blk["fit"].get(c["tag"])
                    if ln is not None:
                        ax.plot(ln[0], ln[1], "-", color=FIT_COLOR, lw=2.4, zorder=4)
                elif blk:
                    for st in studies:
                        col = DATA_COLOR
                        pts = series(blk, st)
                        if pts is not None:
                            x, y, sd = pts
                            yerr = None if np.all(np.isnan(sd)) else np.nan_to_num(sd)
                            ax.errorbar(x, y, yerr=yerr, fmt=mk, ms=np.sqrt(ms) * 1.3, color=col,
                                        ecolor=col, elinewidth=1.4, capsize=4.5, capthick=1.4, mew=0,
                                        linestyle="none", zorder=5)
                        ln = fitline(blk, st)
                        if ln is not None:
                            ax.plot(ln[0], ln[1], "-", color=FIT_COLOR, lw=2.4, zorder=4)
                # no-k_r overlay: one curve per condition (Li columns only), drawn UNDER the fit line
                nk = nokr.get(c["tag"]) if c.get("tag") else nokr.get(c["sheet"])
                if nk is not None:
                    d = nk["bt" if k == 0 else "rp"]
                    ax.plot(d["x"], d["y"], **NOKR_STYLE)
                ax.grid(alpha=.35, lw=.6)
                if k == 0:
                    ax.set_xlim(*BTEC_XLIM); ax.set_ylim(*BTEC_YLIM)
                    ax.set_ylabel(r"log$_{10}$ C/C$_0$", fontsize=FS)
                else:
                    ax.set_xlim(*RP_XLIM); ax.set_ylim(*RP_YLIM)
                    ax.set_ylabel(r"log$_{10}$ spheres", fontsize=FS)
                    # Label field order is PRESCRIBED and must not be rearranged (W.P.J.):
                    #   study(ies) · medium · velocity · size · ionic strength
                    # It sits INSIDE the RP panel only -- at 18 pt the box is wide enough to run
                    # into the breakthrough plateau if repeated in the BTEC panel.
                    lab = wrap_label(", ".join(studies) + f" · {c['med']} · {c['vel']:.0f} m/d · "
                                     f"{c['size']:g} µm · {c['IS']:.0f} mM"
                                     + (f" · Col{c['tag'].split('.')[1]}" if c.get("tag") else ""))
                    ax.text(.985, .955, lab, transform=ax.transAxes, ha="right", va="top",
                            fontsize=FS, fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec="0.35", lw=.8))
                ax.tick_params(labelsize=FS, length=6, width=1.2)
                if i < n - 1:
                    ax.set_xticklabels([])
            axes[i][0].set_xlabel("pore volumes", fontsize=FS) if i == n - 1 else None
            axes[i][1].set_xlabel("distance (m)", fontsize=FS) if i == n - 1 else None

        fig.suptitle(f"Serial-3 fits (r$_s$ fixed) — {title}", fontsize=FS + 2, fontweight="bold",
                     y=1 - 0.30 / fig_h)
        for li, line in enumerate(subtitle_lines):
            fig.text(.5, 1 - (0.60 + 0.20 * li) / fig_h, line, ha="center", va="center",
                     fontsize=FS - 3, style="italic")
        fig.tight_layout(rect=[0, 0, 1, 1 - head_in / fig_h])
        path = os.path.join(args.outdir, fname)
        fig.savefig(path, dpi=140); plt.close(fig)
        print(f"  wrote {fname}  ({n} conditions: " +
              ", ".join(f"{c['size']:g}um/{c['vel']:.0f}md/{c['IS']:.0f}mM" for c in sub) + ")")


if __name__ == "__main__":
    main()
