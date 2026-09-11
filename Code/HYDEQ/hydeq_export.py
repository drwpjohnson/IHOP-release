"""hydeq_export.py -- build the HYDEQ comparison workbook and the overlay figures.

Mirrors the structure of Code/unfav_master_fit.py's UnfavorableMaster.xlsx so the two can be read
side by side:

  'Comparison table'      one row per column x model structure: parameter count, weighted cost,
                          retention-profile RMS, retention-profile branch and peak depth (model and
                          measured), plateau in/out of band, cliff depth, shelf level and slope.
                          This sheet already carries the model_doc section 8.1 feature
                          decomposition, measured and modelled side by side, so there is no
                          separate feature sheet.
  'Fitted parameters'     the fitted parameter values for every column x structure, named, in SI
                          units, with the IHOP reference parameters in the same sheet.
  one sheet per column    plottable columns -- measured breakthrough and retention profile, then
                          the model curve for every structure, so the overlay can be redrawn in
                          Excel without rerunning anything.

Also writes one overlay figure per retention-profile convention (fit-gallery-hydeq-<conv>.png):
measured points with the model curves for IHOP, straining, dual porosity, blocking, and the full
seven-parameter structure.

Reads the fit cache written by hydeq_fit.py (default hydeq_canon.json, the canonical five-column
main-text set) and regenerates the model curves from the stored parameters, so no refitting happens
here. The cache key encodes the RP-shape window, so a cache written under the old always-half-split
objective simply will not match -- which is the intended behaviour, not a bug.

Run from Code/HYDEQ/:   python3 hydeq_export.py --csv ../Data/LiTong_experimental_data_tidy.csv
"""
import json, os, argparse, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.styles import Font, Alignment
from hydeq_engine import (HydeqEngine, IhopReferenceEngine, MODELS, MODEL_LABEL, DAY, L)
from hydeq_fit import load, prep, features, seed_rs, KR_MED, branch_windows, CANON_COLS

BF = Font(bold=True); IT = Font(italic=True)
ORDER = ["IHOP", "M1_1site", "M2_2site", "M3_strain", "M4_dualpor",
         "M5_strain_block", "M6_strain_dp", "M7_all"]
SHORT = {"IHOP": "IHOP Serial-3 (reference)", **MODEL_LABEL}
CONVNAME = {"snap": "Johnson 2018 eq (4) rate snapshot",
            "accum": "accumulated solid phase at excision (10 PV)"}


def rebuild(mdl, rec, d):
    """Regenerate the model curves from cached parameters."""
    if mdl == "IHOP":
        eng = IhopReferenceEngine(d['vel'], d['med'])
        return eng.run_ihop(rec['rs'] * d['V_MS'], rec['a_s'], rec['a_m'], rec['fx'], rec['kr'])
    eng = HydeqEngine(d['vel'], d['med'])
    return eng.run(mdl, np.array(rec['p']))


# ---- full-set gallery geometry, copied from Code/ihop_plot_fits.py so the two figure sets overlay ----
BTEC_YLIM, RP_YLIM = (-6.4, 0.7), (5.3, 9.7)
BTEC_XLIM, RP_XLIM = (0.0, 10.0), (0.0, 0.200)
STUDY_COLOR = {"Li": "#c0392b", "Tong": "#1f4e79"}
LABEL_WRAP = 38
FULLSET_FIGS = [("Glass, 4 m/day", "HydeqComparisonFullSet-glass-4mday.png",
                 lambda m: m["medium"] == "glass" and m["vel"] == 4),
                ("Glass, 8 m/day", "HydeqComparisonFullSet-glass-8mday.png",
                 lambda m: m["medium"] == "glass" and m["vel"] == 8),
                ("Quartz", "HydeqComparisonFullSet-quartz.png",
                 lambda m: m["medium"] == "quartz")]


def sizeclass(s):
    s = float(s)
    return 1.1 if 0.9 <= s <= 1.15 else round(s, 2)


def wrap_label(s):
    """Break the in-panel label at a field boundary, never mid-field (as ihop_plot_fits.py does)."""
    if len(s) <= LABEL_WRAP:
        return s
    line, out = "", []
    for p in s.split(" · "):
        cand = p if not line else line + " · " + p
        if len(cand) > LABEL_WRAP and line:
            out.append(line); line = p
        else:
            line = cand
    out.append(line)
    return "\n".join(out)


def fullset_figures(convs, keys, prepped, store, ckey, args, PLOT, STYLE, ZORD):
    """Three per-condition galleries over all 29 unfavorable columns, in the ihop_plot_fits format:
    same three-way split, same fixed row order, in-panel labels, RP y-axis common to every panel.

    ** MEASURED POINTS ARE PLOTTED PER REPLICATE COLUMN, NOT AS A MEAN +- SD. ** The IHOP galleries
    can show mean +- sd because UnfavorableMaster.xlsx carries a precomputed mean block. Here the
    replicates do NOT share a sampling grid -- there are 19 distinct retention-profile depth grids
    across the 29 columns, and every one of the 6 multi-replicate study-conditions has a different
    breakthrough grid -- so a mean would have to be manufactured by interpolation. Showing the
    replicates raw is the honest alternative and displays the spread directly. (W.P.J., 2026-08-25)

    MODEL curves ARE averaged across the condition's columns, and that average is exact: the engine
    grids depend only on velocity, which is constant within a condition, so no interpolation occurs.
    """
    cond = collections.defaultdict(list)
    for k in keys:
        if k not in prepped:
            continue
        d = prepped[k]
        cond[(d["med"], sizeclass(d["size"]), d["vel"], d["IS"])].append(k)

    for conv in convs:
        for title, fname, sel in FULLSET_FIGS:
            rows = sorted([c for c in cond
                           if sel(dict(medium=c[0], vel=c[2]))],
                          key=lambda c: (c[2], c[1], c[3]))
            if not rows:
                print(f"  (skip {title}: no conditions)"); continue
            n = len(rows)
            grey_labeled = [False]     # list so the inner loop can set it
            head_in = 1.05
            fig_h = 2.32 * n + head_in
            fig, axes = plt.subplots(n, 2, figsize=(11.6, fig_h), squeeze=False)
            for i, ck_ in enumerate(rows):
                kk = sorted(cond[ck_], key=lambda z: (z[0], z[2]))
                studies = []
                for k in kk:
                    if k[0] not in studies:
                        studies.append(k[0])
                studies.sort(key=lambda s: (s != "Li", s))
                a0, a1 = axes[i][0], axes[i][1]
                for k in kk:                                  # measured, one series per column
                    d = prepped[k]; col = STUDY_COLOR.get(k[0], "0.3")
                    a0.plot(d["pv"], d["lc"], "o", ms=3.2, color=col, mew=0, zorder=5,
                            label="measured" if (i == 0 and k is kk[0]) else None)
                    a1.plot(np.array(d["rx"]), d["rlog"], "s", ms=4.0, color=col, mew=0, zorder=5)
                for mdl in PLOT:                              # model, averaged over the condition
                    cs, ls, lw = STYLE[mdl]; zo = ZORD.get(mdl, 3)
                    bt, rp = [], []
                    for k in kk:
                        key = ckey(conv, k, mdl)
                        if key not in store:
                            continue
                        d = prepped[k]; rr = rebuild(mdl, store[key], d)
                        bt.append((rr["tp"], np.log10(np.maximum(rr["C"], 1e-6))))
                        rpm = rr["rp"] if conv == "accum" else rr["rp_snap"]
                        rp.append((rr["x"], d["logK"] + np.log10(np.maximum(rpm / d["V_MS"], 1e-300))))
                    if not bt:
                        continue
                    # Per-column IHOP curves as thin grey lines UNDER the mean (W.P.J., 2026-08-25).
                    # Averaging curves whose peaks sit at different depths flattens the peak: quartz
                    # 6 mM averages fitted maxima at 5.0, 2.6 and 3.4 cm and the mean shows almost no
                    # bump, understating a feature every individual fit reproduces. The grey lines put
                    # that back, and show the replicate spread in the MODEL as well as in the data.
                    if mdl == "IHOP" and len(rp) > 1:
                        # Label on the FIRST condition that actually has replicates, not on row 0 --
                        # row 0 of a figure may be a single-column condition, in which case the
                        # legend entry never attaches and the grey lines go unexplained.
                        for xx, yy in rp:
                            a1.plot(xx, yy, "-", color="0.62", lw=0.7, zorder=1,
                                    label=None if grey_labeled[0] else "IHOP, individual columns")
                            grey_labeled[0] = True
                        for xx, yy in bt:
                            a0.plot(xx, yy, "-", color="0.62", lw=0.7, zorder=1)
                    a0.plot(bt[0][0], np.mean([b[1] for b in bt], axis=0), ls, color=cs, lw=lw,
                            zorder=zo, label=SHORT[mdl] if i == 0 else None)
                    a1.plot(rp[0][0], np.mean([r[1] for r in rp], axis=0), ls, color=cs, lw=lw,
                            zorder=zo)
                for ax, (xl, yl, xlab, ylab) in ((a0, (BTEC_XLIM, BTEC_YLIM, "pore volumes",
                                                       r"log$_{10}$ C/C$_0$")),
                                                 (a1, (RP_XLIM, RP_YLIM, "distance (m)",
                                                       r"log$_{10}$ spheres"))):
                    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.grid(alpha=.35, lw=.6)
                    ax.set_ylabel(ylab, fontsize=9); ax.tick_params(labelsize=8)
                    if i == n - 1:
                        ax.set_xlabel(xlab, fontsize=9)
                    else:
                        ax.set_xticklabels([])
                lab = wrap_label(", ".join(studies) + f" · {ck_[0]} · {ck_[2]:.0f} m/d · "
                                 f"{ck_[1]:g} µm · {ck_[3]:.0f} mM")
                a1.text(.985, .955, lab, transform=a1.transAxes, ha="right", va="top",
                        fontsize=8, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.32", fc="white", ec="0.35", lw=.8))
            fig.suptitle(f"Conventional (Hydeq) structures vs IHOP — {title}", fontsize=13.5,
                         fontweight="bold", y=1 - 0.30 / fig_h)
            fig.text(.5, 1 - 0.62 / fig_h,
                     "each row: BTEC (left, vs PV) + RP (right, vs distance);  points = every "
                     "replicate column (Li red / Tong blue);  coloured lines = model averaged over the "
                     "condition;  thin grey = IHOP per column",
                     ha="center", va="center", fontsize=9.5, style="italic")
            # Collect handles from EVERY axis, deduped by label. Taking them from axes[0][0] alone
            # (as the canonical figure does) silently drops any series first drawn on a later row or
            # on the RP axis -- which is exactly what happened to the grey per-column curves.
            hh, ll = [], []
            for row in axes:
                for ax in row:
                    for hd, lab in zip(*ax.get_legend_handles_labels()):
                        if lab and lab not in ll:
                            hh.append(hd); ll.append(lab)
            fig.legend(hh, ll, loc="lower center", ncol=3, fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, 0.0))
            fig.tight_layout(rect=[0, 0.030, 1, 1 - head_in / fig_h])
            fn = os.path.join(args.figdir, fname if conv == "accum"
                              else fname.replace(".png", f"-{conv}.png"))
            fig.savefig(fn, dpi=140); plt.close(fig)
            print(f"  wrote {os.path.basename(fn)}  ({n} conditions)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="../Data/LiTong_experimental_data_tidy.csv")
    ap.add_argument("--cache", default="hydeq_canon.json")
    ap.add_argument("--out", default=None,
                    help="workbook name; defaults to HydeqComparisonCanonical.xlsx with --canon "
                         "and HydeqComparisonFullSet.xlsx with --fullset")
    ap.add_argument("--figdir", default=".")
    ap.add_argument("--canon", action="store_true",
                    help="restrict to the canonical five-column main-text set")
    ap.add_argument("--fullset", action="store_true",
                    help="all 29 unfavorable columns, drawn as three per-condition galleries in the "
                         "SAME format as Code/ihop_plot_fits.py (HydeqComparisonFullSet-*.png)")
    args = ap.parse_args()
    if args.out is None:
        args.out = ("HydeqComparisonFullSet.xlsx" if args.fullset
                    else "HydeqComparisonCanonical.xlsx")

    store = json.load(open(args.cache))
    cols, meta = load(args.csv)
    keys = sorted(k for k, m in meta.items()
                  if m['chem'] == 'unfavorable' and not (m['IS'] is not None and m['IS'] <= 1.0))

    # Window map, from the FULL set, exactly as hydeq_fit.py does -- the cache key encodes the window,
    # so without this every lookup silently misses and the figures come out empty (or worse, fall back
    # to whatever old-format entries are still lying in the cache).
    NIN = branch_windows(cols, meta)

    def ckey(conv, k, mdl):
        return "|".join([conv, k[0], k[1], k[2], mdl, "w4" if NIN.get(k) else "wH"])

    if args.canon and args.fullset:
        raise SystemExit("--canon and --fullset are mutually exclusive")
    if args.canon:
        keys = [k for k in keys if k[2] in CANON_COLS and k[0] == "Li"]
    # Keep only columns this cache actually holds, so a canonical-set cache does not produce 24 empty rows.
    have = {(kk.split("|")[1], kk.split("|")[2], kk.split("|")[3]) for kk in store}
    keys = [k for k in keys if k in have]
    convs = sorted({k.split("|")[0] for k in store})
    print(f"export: {len(keys)} columns, conventions {convs}, cache {args.cache}")

    wb = openpyxl.Workbook(); wb.remove(wb.active)

    # ---------------- Comparison table ----------------
    cs = wb.create_sheet("Comparison table")
    cs.cell(1, 1, "HYDEQ conventional model structures vs the IHOP interception-history model, "
                  "fit to the same Li/Tong unfavorable columns under the same objective, weights, "
                  "and C0-fixed retention-profile amplitude.").font = BF
    cs.cell(2, 1, "Data discipline (objective, weights, amplitude, detection floor, exclusions) is "
                  "identical for both models and is copied from Code/unfav_master_fit.py. The "
                  "conventional structures are additionally allowed detachment, straining, "
                  "blocking, and a second flow region -- mechanisms IHOP forbids.").font = IT
    HDR = ["convention", "study", "medium", "column", "colloid (um)", "v (m/day)", "IS (mM)",
           "model structure", "fitted parameters", "weighted cost", "RP RMS (log10)",
           "RP branch (model)", "RP peak (cm, model)", "RP branch (measured)",
           "RP peak (cm, measured)", "plateau in band?", "cliff depth (model)",
           "cliff depth (measured)", "shelf level (model)", "shelf level (measured)",
           "shelf slope (model)", "shelf slope (measured)"]
    for j, h in enumerate(HDR, 1):
        c = cs.cell(4, j, h); c.font = BF; c.alignment = Alignment(wrap_text=True, vertical="top")
    r = 5
    prepped = {}
    for conv in convs:
        for k in keys:
            d = prep(k, cols, meta, nin=NIN.get(k))
            if d is None: continue
            prepped[k] = d
            for mdl in ORDER:
                ck = ckey(conv, k, mdl)
                if ck not in store: continue
                s = store[ck]
                row = [CONVNAME[conv], k[0], k[1], k[2], d['size'], d['vel'], d['IS'],
                       SHORT[mdl], s['npar'], round(s['cost'], 4), round(s['rpRMS'], 4),
                       s['branch_m'], round(s['peak_m'] * 100, 2),
                       s['branch_d'], round(s['peak_d'] * 100, 2),
                       "in" if s['plat_in'] else "OUT",
                       round(s['cliff_m'], 3), round(s['cliff_d'], 3),
                       round(s['shelf_m'], 3), round(s['shelf_d'], 3),
                       round(s['sslope_m'], 4) if s['sslope_m'] == s['sslope_m'] else "",
                       round(s['sslope_d'], 4) if s['sslope_d'] == s['sslope_d'] else ""]
                for j, v in enumerate(row, 1): cs.cell(r, j, v)
                r += 1
    for col, w in zip("ABCDEFGHIJKLMNOPQRSTUV",
                      [34, 7, 8, 8, 11, 10, 9, 46, 11, 12, 12, 14, 14, 15, 15, 13, 12, 13, 12, 13, 12, 13]):
        cs.column_dimensions[col].width = w

    # ---------------- Fitted parameters ----------------
    ps = wb.create_sheet("Fitted parameters")
    ps.cell(1, 1, "Fitted parameter values. Rates are in 1/s. beta and f_slow are dimensionless. "
                  "S1max is in the dimensionless solid-phase units of the solver.").font = BF
    ps.cell(2, 1, "NOTE: k_str is exactly degenerate with d50^beta over the measured depth range, "
                  "so the fitted k_str is an amplitude, not a separable rate. d50 = 510 um for BOTH "
                  "media, so the straining depth function is identical for glass and quartz.").font = IT
    PH = ["convention", "study", "medium", "column", "IS (mM)", "model structure", "parameter", "value"]
    for j, h in enumerate(PH, 1): ps.cell(4, j, h).font = BF
    r = 5
    for conv in convs:
        for k in keys:
            d = prepped.get(k)
            if d is None: continue
            for mdl in ORDER:
                ck = ckey(conv, k, mdl)
                if ck not in store: continue
                s = store[ck]
                if mdl == "IHOP":
                    pairs = [("r_s (/m, pinned)", s['rs']), ("r_s source", s['rs_src']),
                             ("alpha_s", s['a_s']), ("alpha_m", s['a_m']),
                             ("f_x", s['fx']), ("k_r (1/s)", s['kr'])]
                else:
                    pairs = list(zip(s['names'], [10 ** v if n not in ("beta", "f_slow") else v
                                                  for n, v in zip(s['names'], s['p'])]))
                for nm, val in pairs:
                    for j, v in enumerate([CONVNAME[conv], k[0], k[1], k[2], d['IS'], SHORT[mdl],
                                           nm, (round(val, 8) if isinstance(val, float) else val)], 1):
                        ps.cell(r, j, v)
                    r += 1
    for col, w in zip("ABCDEFGH", [34, 7, 8, 8, 9, 46, 20, 16]): ps.column_dimensions[col].width = w

    # ---------------- one plottable sheet per column ----------------
    for conv in convs:
        for k in keys:
            d = prepped.get(k)
            if d is None: continue
            nm = f"{conv}_{k[1][:2]}{k[2]}_{(d['IS'] or 0):.0f}mM"[:31]
            ws = wb.create_sheet(nm)
            ws.cell(1, 1, f"{k[0]} {k[1]} column {k[2]} -- {d['size']} um, {d['vel']:.0f} m/day, "
                          f"{d['IS']:.0f} mM, unfavorable. Retention-profile convention: "
                          f"{CONVNAME[conv]}.").font = BF
            ws.cell(2, 1, "Measured data first, then one model curve per structure. "
                          "Breakthrough y = log10 C/C0; retention profile y = log10 spheres.").font = IT
            # breakthrough block
            ws.cell(4, 1, "BREAKTHROUGH-ELUTION CURVE").font = BF
            ws.cell(5, 1, "pore volumes").font = BF; ws.cell(5, 2, "MEASURED log10 C/C0").font = BF
            for i, (x, y) in enumerate(zip(d['pv'], d['lc'])):
                ws.cell(6 + i, 1, round(float(x), 5)); ws.cell(6 + i, 2, round(float(y), 4))
            cc = 4
            for mdl in ORDER:
                ck = ckey(conv, k, mdl)
                if ck not in store: continue
                rr = rebuild(mdl, store[ck], d)
                idx = np.linspace(0, len(rr['tp']) - 1, 120).astype(int)
                ws.cell(5, cc, f"{SHORT[mdl]} : pore volumes").font = BF
                ws.cell(5, cc + 1, f"{SHORT[mdl]} : log10 C/C0").font = BF
                for i, ii in enumerate(idx):
                    ws.cell(6 + i, cc, round(float(rr['tp'][ii]), 5))
                    ws.cell(6 + i, cc + 1, round(float(np.log10(max(rr['C'][ii], 1e-6))), 4))
                cc += 3
            # retention-profile block
            r0 = 6 + max(len(d['pv']), 120) + 3
            ws.cell(r0, 1, "RETENTION PROFILE").font = BF
            ws.cell(r0 + 1, 1, "distance (m)").font = BF
            ws.cell(r0 + 1, 2, "MEASURED log10 spheres").font = BF
            for i, (x, y) in enumerate(zip(d['rx'], d['rlog'])):
                ws.cell(r0 + 2 + i, 1, round(float(x), 4)); ws.cell(r0 + 2 + i, 2, round(float(y), 4))
            cc = 4
            for mdl in ORDER:
                ck = ckey(conv, k, mdl)
                if ck not in store: continue
                rr = rebuild(mdl, store[ck], d)
                rpm = rr['rp'] if conv == 'accum' else rr['rp_snap']
                lS = d['logK'] + np.log10(np.maximum(rpm / d['V_MS'], 1e-300))
                ws.cell(r0 + 1, cc, f"{SHORT[mdl]} : distance (m)").font = BF
                ws.cell(r0 + 1, cc + 1, f"{SHORT[mdl]} : log10 spheres").font = BF
                for i in range(len(rr['x'])):
                    ws.cell(r0 + 2 + i, cc, round(float(rr['x'][i]), 4))
                    ws.cell(r0 + 2 + i, cc + 1, round(float(lS[i]), 4))
                cc += 3
            for j in range(1, 30):
                ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = 26

    wb.save(args.out)
    print("wrote " + args.out)

    # ---------------- figures ----------------
    PLOT = ["IHOP", "M3_strain", "M4_dualpor", "M5_strain_block", "M7_all"]
    # IHOP is the REFERENCE line, not the subject of the figure: thin, and UNDER the conventional
    # curves (W.P.J., 2026-08-24). It was lw=2.0, the heaviest line on the plot, so wherever a HYDEQ
    # curve tracked it the reference obscured the thing being compared. Weight and z-order both matter
    # -- a thin line drawn on top still hides what is beneath it.
    STYLE = {"IHOP": ("k", "-", 1.0), "M3_strain": ("tab:red", "-", 1.6),
             "M4_dualpor": ("tab:blue", "-", 1.6), "M5_strain_block": ("tab:green", "--", 1.6),
             "M7_all": ("tab:purple", ":", 1.8)}
    ZORD = {"IHOP": 2}          # everything else defaults to 3, i.e. drawn over IHOP
    # Row order for the canonical set is the MATCHED-PAIR order the set was designed around --
    # glass 6 / quartz 6, glass 20 / quartz 20, then the 3 mM extreme -- not alphabetical by column
    # letter, which interleaves the pairs and hides the comparison the figure exists to make.
    CANON_ROW_ORDER = ["R", "V", "O", "P", "AE"]

    def row_sort(kl):
        rank = {c: i for i, c in enumerate(CANON_ROW_ORDER)}
        return sorted(kl, key=lambda k: (rank.get(k[2], 99), k[1], k[2]))

    # ================= FULL-SET galleries, in the ihop_plot_fits.py format =================
    if args.fullset:
        fullset_figures(convs, keys, prepped, store, ckey, args, PLOT, STYLE, ZORD)
        wb.save(args.out); print("wrote " + args.out)
        return

    for conv in convs:
        kk = row_sort([k for k in keys if k in prepped])
        n = len(kk)
        fig, ax = plt.subplots(n, 2, figsize=(11, 2.5 * n), squeeze=False)
        for i, k in enumerate(kk):
            d = prepped[k]
            a0, a1 = ax[i][0], ax[i][1]
            lab = 'measured' if i == 0 else None
            a0.plot(d['pv'], d['lc'], 'o', ms=4, color='0.25', label=lab, zorder=5)
            a1.plot(np.array(d['rx']) * 100, d['rlog'], 'o', ms=5, color='0.25', zorder=5)
            for mdl in PLOT:
                ck = ckey(conv, k, mdl)
                if ck not in store: continue
                rr = rebuild(mdl, store[ck], d)
                c, ls, lw = STYLE[mdl]; zo = ZORD.get(mdl, 3)
                a0.plot(rr['tp'], np.log10(np.maximum(rr['C'], 1e-6)), ls, color=c, lw=lw, zorder=zo,
                        label=SHORT[mdl] if i == 0 else None)
                rpm = rr['rp'] if conv == 'accum' else rr['rp_snap']
                lS = d['logK'] + np.log10(np.maximum(rpm / d['V_MS'], 1e-300))
                a1.plot(rr['x'] * 100, lS, ls, color=c, lw=lw, zorder=zo)
            ttl = f"{k[1]} {k[2]}  {d['size']}um {d['vel']:.0f} m/d {d['IS']:.0f} mM"
            a0.set_title(ttl + " -- breakthrough", fontsize=9)
            a1.set_title(ttl + " -- retention profile", fontsize=9)
            a0.set_xlabel("pore volumes", fontsize=8); a0.set_ylabel("log10 C/C0", fontsize=8)
            a1.set_xlabel("distance (cm)", fontsize=8); a1.set_ylabel("log10 spheres", fontsize=8)
            a0.set_ylim(-6.3, 0.4); a0.tick_params(labelsize=7); a1.tick_params(labelsize=7)
            lo = min(d['rlog']); hi = max(d['rlog']); a1.set_ylim(lo - 1.2, hi + 0.6)
        fig.suptitle(f"HYDEQ conventional structures vs IHOP -- retention-profile convention: "
                     f"{CONVNAME[conv]}", fontsize=11, y=0.999)
        h, lb = ax[0][0].get_legend_handles_labels()
        fig.legend(h, lb, loc="lower center", ncol=2, fontsize=8.5, frameon=False,
                   bbox_to_anchor=(0.5, 0.0))
        fig.tight_layout(rect=[0, 0.055, 1, 0.985])
        # Canonical figure name (W.P.J., 2026-08-25): HydeqComparisonCanonical.*, matching the
        # workbook and Word doc of the same set. Was fit-gallery-hydeq-<conv>.png. The convention
        # suffix is kept only for non-adopted conventions, so the adopted 'accum' figure is the
        # bare name the manuscript references.
        fn = os.path.join(args.figdir, "HydeqComparisonCanonical.png" if conv == "accum"
                          else f"HydeqComparisonCanonical-{conv}.png")
        fig.savefig(fn, dpi=150, bbox_inches="tight"); plt.close(fig)
        print("wrote " + fn)


if __name__ == "__main__":
    main()
