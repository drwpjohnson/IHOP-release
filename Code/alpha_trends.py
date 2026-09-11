"""alpha_trends.py -- alpha_s / alpha_m trends, the Al-Zghoul RP-branch boundary, and the plateau
attachment efficiency a_plat, for the full unfavorable set.

REFACTORED 2026-08-24 (W.P.J. approved): this script previously carried its alpha_s / alpha_m values
as HARD-CODED literals (ALPHA_S_IS, ALPHA_PAIRS), so a refit of unfav_master_fit.py did not propagate
and the two could drift silently.  It now READS them from UnfavorableMaster.xlsx 'Master table', which
is what the workbook's own 'notes' sheet already claimed the source was.  It also regains the
'a_plat (plateau alpha)' sheet, which the previous Box copy did not produce at all even though the
distributed workbook contained it.

WHAT IT READS
  * UnfavorableMaster.xlsx 'Master table'  -- alpha_s, alpha_m, r_s, and (new) the measured RP branch
  * LiTong_experimental_data_tidy.csv      -- BTEC plateaus, for a_plat

a_plat -- the classical experimental attachment efficiency read at the breakthrough plateau:
    a_plat = kf_unfav_plat / kf_fav_plat,     kf = -ln(C/C0) * (v/L)
    C/C0   = 10^(mean log10 C/C0 over 1.2 < PV < 4)     [the same mean-log plateau rule as the fit]
    L: Tong 0.192 m, Li 0.190 m
The favorable twin is the column matching (medium, sizeclass, velocity), same study preferred --
i.e. EXACTLY the favorable that pinned r_s in unfav_master_fit.py's FAVFIT.  So a_plat exists for
precisely the conditions whose r_s source is 'fav', and is NFT (no favorable twin) where the pin fell
back to a favorable RP-slope seed ('favRP') or the TE correlation ('TE').  v/L cancels for a
same-study velocity-matched twin, so a_plat reduces to ln(C/C0_unfav)/ln(C/C0_fav).

TWO BRANCH COLUMNS, AND THEY CAN DISAGREE (new 2026-08-24)
  * 'RP_branch (fitted alpha)'   -- Al-Zghoul Eqn 15 applied to the FITTED alphas: peaked iff
                                    alpha_m > alpha_s/(1-alpha_s).  This is what the sheet used to carry.
  * 'RP_branch (measured)'       -- the two-point test on the MEASURED profile (point2 > point1),
                                    which is what now selects the RP-shape scoring window in
                                    unfav_master_fit.py.  See plateau_rs_decision.md s6.
They agree on 18 of 19 conditions.  Where they disagree the disagreement is itself the result and must
not be hidden -- aplat_plateau_alpha.md s4 leans on a_plat sign, fitted branch and measured RP shape
being three semi-independent directions telling one story.

BOTH INPUTS ARE REQUIRED ARGUMENTS -- no defaults (W.P.J., 2026-08-24). A default path is how a
stale workbook gets read silently; making them explicit forces the caller to name what was used.

Usage:  python3 alpha_trends.py --master UnfavorableMaster.xlsx \
                               --csv ../Data/LiTong_experimental_data_tidy.csv
"""
import argparse, collections, csv as _csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.styles import Font

L_STUDY = {"Tong": 0.192, "Li": 0.190}      # RP max distance per study
PLAT_LO, PLAT_HI = 1.2, 4.0                 # mean-log plateau window, PV


def sizeclass(s):
    s = float(s); return 1.1 if 0.9 <= s <= 1.15 else round(s, 2)


def load_csv(path):
    rows = list(_csv.DictReader(open(path)))
    # GUARD, 2026-09-01: the shared master CSV was silently overwritten with a 352-row/Li-only
    # a_mg-probe subset for a month before anyone noticed -- see Records/CLAUDE.md.
    _srcs = set(r['source'] for r in rows)
    assert len(rows) >= 1200 and 'Li' in _srcs and 'Tong' in _srcs, (
        f"CSV at {path!r} looks like a subset ({len(rows)} rows, sources={_srcs}), not the full "
        "master (~1529 rows, both Li and Tong) -- refusing to run on a silently-truncated dataset.")
    cols = collections.defaultdict(lambda: {"BTEC": [], "RP": []}); meta = {}
    # BTEC_ND (2026-08-28, wired in 2026-09-01): non-detect tail points, merged into BTEC -- same
    # convention as unfav_master_fit.py, see that file's comment for the reasoning.
    for r in rows:
        curve = 'BTEC' if r['curve'] == 'BTEC_ND' else r['curve']
        k = (r['source'], r['medium'], r['workbook_col'])
        cols[k][curve].append((float(r['x']), float(r['value'])))
        meta[k] = dict(medium=r['medium'], chem=r['chemistry'], size=float(r['colloid_um']),
                       vel=float(r['velocity_mday']),
                       IS=(None if r['IS_mM'] == '' else float(r['IS_mM'])))
    for k in cols:
        for cu in ("BTEC", "RP"):
            cols[k][cu] = np.array(sorted(cols[k][cu])) if cols[k][cu] else np.zeros((0, 2))
    return cols, meta


def plateau_points(bt):
    """log10 C/C0 points inside the plateau window, BTEC floored at -6 as in the fit."""
    if len(bt) < 3: return []
    pv = bt[:, 0]; lc = np.maximum(bt[:, 1], -6.0)
    w = (pv > PLAT_LO) & (pv < PLAT_HI)
    return list(lc[w]) if w.sum() else list(lc)


def plateau_meanlog(bt):
    p = plateau_points(bt)
    return float(np.mean(p)) if p else None


def read_master(path):
    """Read 'Master table' -> one record per (study, medium, size, vel, IS)."""
    ws = openpyxl.load_workbook(path, data_only=True)['Master table']
    hdr = None; out = []
    for r in ws.iter_rows(values_only=True):
        if r and r[0] == 'study': hdr = list(r); continue
        if hdr is None or not r or r[0] is None or not isinstance(r[3], (int, float)): continue
        d = dict(zip(hdr, r))
        rs_txt = str(d['r_s (/m, fixed)']); te = rs_txt.endswith('*')
        out.append(dict(study=d['study'], cols=d['column(s)'], medium=d['medium'],
                        size=float(d['size (um)']), vel=float(d['v (m/day)']),
                        IS=(float(d['IS (mM)']) if d['IS (mM)'] not in (None, '') else None),
                        rs=float(rs_txt.rstrip('*')), rs_is_TE=te,
                        a_s=float(d['alpha_s']), a_m=float(d['alpha_m']),
                        fx=float(d.get('f_x', 'nan') or 'nan'),
                        kr=float(d.get('k_r (/s)', d.get('k_r (/PV)', 'nan')) or 'nan'),  # /s since 2026-09-03; /PV fallback for older workbooks
                        meas_branch=d.get('RP branch (measured)')))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True,
                    help="path to UnfavorableMaster.xlsx -- REQUIRED, no default, so a stale "
                         "workbook can never be read silently (W.P.J., 2026-08-24)")
    ap.add_argument("--csv", required=True,
                    help="path to LiTong_experimental_data_tidy.csv -- REQUIRED, same reason")
    ap.add_argument("--out", default="alpha_trends.xlsx")
    args = ap.parse_args()

    rec = read_master(args.master)
    cols, meta = load_csv(args.csv)

    # ---- favorable plateau per (medium, sizeclass, velocity), same study preferred ----
    favp = collections.defaultdict(dict)
    for k, m in meta.items():
        if m['chem'] != 'favorable': continue
        ml = plateau_meanlog(cols[k]['BTEC'])
        if ml is None: continue
        favp[(m['medium'], sizeclass(m['size']), m['vel'])][k[0]] = (ml, k, m)

    # ---- unfavorable plateau per condition (mean over replicate columns) ----
    unfp = collections.defaultdict(list)
    for k, m in meta.items():
        if m['chem'] != 'unfavorable': continue
        # POOL every plateau point across replicate columns (verified against the reference
        # workbook: mean-of-column-means misses Tong glass 1.1/20 and Li quartz 1.1/20).
        unfp[(k[0], m['medium'], m['size'], m['vel'], m['IS'])].extend(plateau_points(cols[k]['BTEC']))

    rows = []
    for d in rec:
        key = (d['study'], d['medium'], d['size'], d['vel'], d['IS'])
        mlu = float(np.mean(unfp[key])) if unfp.get(key) else None
        Lu = L_STUDY[d['study']]
        kfu = (-np.log(10 ** mlu) * (d['vel'] / Lu)) if mlu is not None else None
        cand = favp.get((d['medium'], sizeclass(d['size']), d['vel']), {})
        pick = cand.get(d['study']) or (list(cand.values())[0] if cand else None)
        if pick is None or d['rs_is_TE']:
            note = ("no favorable twin (r_s TE*)" if d['rs_is_TE'] else "no favorable twin (r_s favRP)")
            rows.append(dict(d=d, mlu=mlu, kfu=kfu, mlf=None, kff=None, ap=None, ref="NFT", note=note))
        else:
            mlf, fk, fm = pick
            kff = -np.log(10 ** mlf) * (fm['vel'] / L_STUDY[fk[0]])
            ap = kfu / kff if (kfu and kff) else None
            ref = f"{fm['medium']} {fk[0]} {fm['size']}um {fm['vel']:.0f}mday {fm['IS']:.0f}mM"
            rows.append(dict(d=d, mlu=mlu, kfu=kfu, mlf=mlf, kff=kff, ap=ap, ref=ref, note=""))

    B = Font(bold=True); IT = Font(italic=True)
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    def hd(ws, r, vals):
        for j, v in enumerate(vals, 1): ws.cell(r, j, v).font = B

    def branch_fitted(a_s, a_m):
        # W.P.J., 2026-08-26: the negative class is NON-PEAKING, not "multiexponential". eq 15 tests
        # one thing -- whether the RP has an interior peak. A non-peaking RP may be multiexponential
        # (steep inlet, shallow downgradient) OR simply log-linear; multiexponential is a SUBclass.
        # Near-zero margin means log-linear, and calling such a column multiexponential is wrong.
        # "monotone" was ALSO retired as the class name (W.P.J.): it invited exactly the
        # "multiexponential" over-narrowing above, so the class is named for the property that
        # actually distinguishes it -- no interior peak -- rather than a shape adjective.
        return "peaked" if a_m > a_s / (1 - a_s) else "non-peaking"

    ws = wb.create_sheet("alpha_s vs IS")
    ws.cell(1, 1, "alpha_s vs ionic strength -- current Serial-3 fits (r_s FIXED at favorable anchor; UnfavorableMaster.xlsx)").font = B
    ws.cell(2, 1, "alpha_s = single-interception attachment efficiency (1-10^p). Condition-averaged over replicate columns.").font = IT
    hd(ws, 3, ["study", "medium", "size_um", "v_mday", "IS_mM", "alpha_s"])
    for i, r in enumerate(rows, 4):
        d = r['d']
        for j, v in enumerate([d['study'], d['medium'], d['size'], d['vel'], d['IS'], d['a_s']], 1):
            ws.cell(i, j, v)
    for c, w in zip("ABCDEF", [7, 8, 8, 8, 7, 9]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("alpha_m vs alpha_s")
    ws.cell(1, 1, "alpha_m vs alpha_s with RP branch + plateau attachment a_plat -- current Serial-3 fits").font = B
    ws.cell(2, 1, "RP_branch (fitted alpha): peaked if alpha_m > alpha_s/(1-alpha_s). RP_branch (measured): two-point test on the measured profile (pt2>pt1), which selects the RP-shape scoring window (plateau_rs_decision.md s6). THEY CAN DISAGREE -- the disagreement is a result, not an error. a_plat = kf_unfav/kf_fav (plateau), kf=-ln(C/C0)*v/L; NFT where no favorable twin.").font = IT
    hd(ws, 3, ["study", "condition(cols)", "medium", "size_um", "v_mday", "IS_mM", "alpha_s", "alpha_m",
               "RP_branch (fitted alpha)", "RP_branch (measured)", "branches agree?", "r_s /m (fixed)",
               "a_plat", "a_plat note"])
    for i, r in enumerate(rows, 4):
        d = r['d']; bf = branch_fitted(d['a_s'], d['a_m'])
        bm = d['meas_branch'] or ""
        bmn = bm   # was renamed to "multiexponential" here -- wrong, see branch_fitted()
        agree = "" if not bmn else ("yes" if bmn == bf else "NO")
        for j, v in enumerate([d['study'], d['cols'], d['medium'], d['size'], d['vel'], d['IS'],
                               d['a_s'], d['a_m'], bf, bmn, agree,
                               f"{d['rs']:.1f}{'*' if d['rs_is_TE'] else ''}",
                               ("NFT" if r['ap'] is None else round(r['ap'], 4)), r['note']], 1):
            ws.cell(i, j, v)
    for c, w in zip("ABCDEFGHIJKLMN", [7, 14, 8, 8, 8, 7, 9, 9, 22, 21, 15, 13, 9, 28]):
        ws.column_dimensions[c].width = w

    ws = wb.create_sheet("a_plat (plateau alpha)")
    ws.cell(1, 1, "Plateau attachment efficiency a_plat = kf_unfav_plat / kf_fav_plat").font = B
    ws.cell(2, 1, f"kf = -ln(C/C0)*(v/L). C/C0 = 10^(mean log10 C/C0 over {PLAT_LO}<PV<{PLAT_HI}). v/L cancels for a same-study, velocity-matched favorable twin (the SAME favorable used to pin r_s). L: Tong 0.192 m, Li 0.190 m.").font = IT
    hd(ws, 3, ["study", "medium", "size_um", "v_mday", "IS_mM", "unfav mean log10(C/C0)", "unfav C/C0",
               "kf_unfav /day", "favorable ref", "fav mean log10(C/C0)", "fav C/C0", "kf_fav /day",
               "a_plat", "note"])
    for i, r in enumerate(rows, 4):
        d = r['d']
        vals = [d['study'], d['medium'], d['size'], d['vel'], d['IS'],
                (round(r['mlu'], 3) if r['mlu'] is not None else ""),
                (round(10 ** r['mlu'], 4) if r['mlu'] is not None else ""),
                (round(r['kfu'], 2) if r['kfu'] is not None else ""), r['ref']]
        if r['ap'] is None:
            vals += ["NFT", "NFT", "NFT", "NFT", r['note']]
        else:
            vals += [round(r['mlf'], 3), round(10 ** r['mlf'], 5), round(r['kff'], 2),
                     round(r['ap'], 4), r['note']]
        for j, v in enumerate(vals, 1): ws.cell(i, j, v)
    for c, w in zip("ABCDEFGHIJKLMN", [7, 8, 8, 8, 7, 22, 11, 13, 30, 20, 11, 12, 9, 28]):
        ws.column_dimensions[c].width = w

    ws = wb.create_sheet("branch boundary")
    ws.cell(1, 1, "a_m = a_s/(1-a_s)  (NON-PEAKING below, peaked above). Non-peaking spans multiexponential (strongly negative margin) through log-linear (margin ~ 0); 'multiexponential' is NOT the whole lower half.").font = B
    hd(ws, 2, ["alpha_s", "alpha_m_boundary"])
    for i, a in enumerate(np.logspace(np.log10(5e-4), np.log10(0.99), 30), 3):
        ws.cell(i, 1, round(float(a), 5)); ws.cell(i, 2, round(float(a / (1 - a)), 5))
    for c, w in zip("AB", [10, 18]): ws.column_dimensions[c].width = w

    ws = wb.create_sheet("notes")
    for i, t in enumerate([
        f"Source: {args.master} 'Master table' (READ, not hard-coded -- refactored 2026-08-24).",
        "alpha_s, alpha_m: condition-averaged over replicate columns (parameter-level mean).",
        "a_plat: plateau attachment efficiency vs the velocity- and sizeclass-matched favorable twin (same favorable that pinned r_s).",
        "TWO branch columns are now reported: from the FITTED alphas (Eqn 15) and from the MEASURED profile (two-point test). Where they disagree, that is a result -- see plateau_rs_decision.md s6.",
        "Branch boundary a_m=a_s/(1-a_s) unchanged (analytic).",
        "k_r and f_x: see k_r_trend.xlsx / fx_trend.xlsx (both regenerated after the 2026-08-24 objective correction).",
    ], 1):
        ws.cell(i, 1, t)
    ws.column_dimensions['A'].width = 150

    wb.save(args.out); print("wrote " + args.out)

    # ---- figures ----
    for fn, xf, yf, xl, yl, ttl in [
        ("alpha_s_vs_IS.png", lambda r: r['d']['IS'], lambda r: r['d']['a_s'],
         "ionic strength (mM)", "alpha_s", "alpha_s vs ionic strength"),
    ]:
        fig, ax = plt.subplots(figsize=(7.6, 5.2))
        for med, c, mk in (("glass", "#1f77b4", "o"), ("quartz", "#7b2d8b", "s")):
            pts = [(xf(r), yf(r)) for r in rows if r['d']['medium'] == med and xf(r)]
            if pts: ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=70, color=c, marker=mk,
                               edgecolor='k', label=med, zorder=5)
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel(xl); ax.set_ylabel(yl)
        ax.set_title(ttl); ax.grid(alpha=.3, which='both'); ax.legend()
        fig.tight_layout(); fig.savefig(fn, dpi=140); plt.close(fig); print("wrote " + fn)

    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    aa = np.logspace(np.log10(5e-4), np.log10(0.95), 200)
    ax.plot(aa, aa / (1 - aa), 'k-', lw=1.3, label=r'branch boundary $a_m=a_s/(1-a_s)$')
    for med, c, mk in (("glass", "#1f77b4", "o"), ("quartz", "#7b2d8b", "s")):
        pts = [(r['d']['a_s'], r['d']['a_m']) for r in rows if r['d']['medium'] == med]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=70, color=c, marker=mk,
                   edgecolor='k', label=med, zorder=5)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('alpha_s'); ax.set_ylabel('alpha_m')
    ax.set_title('alpha_m vs alpha_s: above the line = peaked RP, below = non-peaking')
    ax.grid(alpha=.3, which='both'); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig("../Manuscript/FigsExcelsUnfav/alpha_m_vs_alpha_s.png", dpi=140); plt.close(fig)
    print("wrote alpha_m_vs_alpha_s.png")


if __name__ == "__main__":
    main()
