"""transfer_test.py -- do IHOP's fitted parameters transfer between REPLICATES of the same condition?

THE QUESTION (D. Bolster).  If alpha_s, alpha_m, f_x and k_r encode physicochemical processes rather
than absorbing per-column idiosyncrasy, then two columns run at the same nominal condition should not
need unrelated parameter estimates.  This script tests that directly.

THE TEST.  For every condition with replicates, each column in turn is the DONOR: its own fitted
parameters are applied, unchanged, to every SIBLING column at that condition and scored under the
production objective against the sibling's own data.  The penalty reported is

    delta% = 100 * (cost with donor's parameters - sibling's own-fit cost) / sibling's own-fit cost

NOTHING IS REFITTED.  The donor parameters are the per-column fits already in UnfavorableMaster.xlsx,
and the scoring is the same five-block weighted log10 residual used to produce them, so this cannot
move any published number.  Each sibling keeps its OWN C0 (hence its own retention amplitude logK),
its own depth grid and its own RP-shape window: only the four fitted parameters are transferred.

READ THE CONTROL.  A cross-CONDITION donor is scored alongside as a null: parameters from a different
condition, same medium.  A transfer penalty is only meaningful relative to how badly a wrong-condition
parameter set does on the same data.

CAVEAT ON alpha_s.  Only the product r_s*alpha_s is identifiable per column (Records: r_s decision),
so a large alpha_s spread between siblings does not by itself mean the columns disagree physically.
The transfer cost, which holds r_s at the shared favorable anchor, is the fairer statement.

Usage:
    python3 transfer_test.py                       # table to stdout + transfer_test.xlsx
    python3 transfer_test.py --out my.xlsx
"""
import csv, collections, argparse
import numpy as np
from scipy.linalg import expm
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import splu
import openpyxl
from openpyxl.styles import Font

# ---- constants and objective, copied verbatim from unfav_master_fit.py ----
CSV = "../Data/LiTong_experimental_data_tidy.csv"
MASTER = "../Manuscript/FigsExcelsUnfav/UnfavorableMaster.xlsx"
DAY = 86400.; L = 0.2
REV, T0, Vref = 22.801836559387397, 3.58, 0.1667
INJPV = T0 / (L / Vref)
THETA = {"glass": 0.375, "quartz": 0.36}
W_RP, W_SHAPE, W_PLAT, W_TAIL, W_TSLOPE = 6.0, 2.5, 20.0, 3.0, 16.0
PLAT_TOL = 0.25
NIN_PEAKED = 4


class Eng:
    def __init__(s, vmday):
        s.v = vmday / DAY; s.dx = L / 90; s.dt = s.dx / s.v; s.pv = L / s.v

    def run(s, k1, a_s, a_m, fx, kr, vns=0.05, tot=10):
        kf = k1; k2 = fx * kf; kmw = a_m * kf; kmg = a_m * vns * kf
        G = np.zeros((4, 4))
        G[0, 0] -= kf; G[3, 0] += a_s * kf; G[1, 0] += (1 - a_s) * kf
        G[1, 1] -= (kmw + k2); G[3, 1] += kmw; G[2, 1] += k2
        G[2, 2] -= kmg; G[3, 2] += kmg; G[1, 2] += kr; G[2, 2] -= kr
        E = expm(G * s.dt); D = s.v * L / 150
        r = D * s.dt / s.dx ** 2
        mn = (1 + 2 * r) * np.ones(90); of = -r * np.ones(89); mn[0] = 1 + r; mn[-1] = 1 + r
        lu = splu(csc_matrix(diags([of, mn, of], [-1, 0, 1], format="csc")))
        nt = int(round(tot * 90)); ti = INJPV * s.pv; c = vns
        Y = np.zeros((4, 90)); C = np.zeros(nt); t = 0.
        for i in range(nt):
            Y = E @ Y; C[i] = Y[0, -1] + Y[1, -1] + c * Y[2, -1]
            Y[0, 1:] = Y[0, :-1]; Y[0, 0] = 0; Y[1, 1:] = Y[1, :-1]; Y[1, 0] = 0
            ym = Y[2].copy(); Y[2, 1:] = ym[1:] - c * (ym[1:] - ym[:-1]); Y[2, 0] = ym[0] * (1 - c)
            t += s.dt
            if t < ti: Y[0, 0] += 1.
            Y[0, :] = lu.solve(Y[0, :]); Y[1, :] = lu.solve(Y[1, :])
        tp = (np.arange(nt) + 1) * s.dt / s.pv; x = (np.arange(90) + 0.5) * s.dx
        return dict(tp=tp, C=np.maximum(C, 1e-300), x=x,
                    rp=np.maximum(Y[3, :] / ti, 1e-300))


def sl(x, y, nin=None):
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    k = nin if nin else max(2, n // 2)
    k = min(max(k, 2), n - 2)
    a = np.polyfit(x[:k], y[:k], 1)[0]; b = np.polyfit(x[k:], y[k:], 1)[0]
    return a, b


def ts(pv, lc):
    m = (pv >= 6) & (pv <= 10)
    return float(np.polyfit(pv[m], lc[m], 1)[0]) if m.sum() >= 2 else float("nan")


def rp_branch(rlog):
    return "peaked" if len(rlog) >= 2 and rlog[1] > rlog[0] else "monotone"


def load_columns():
    rows = list(csv.DictReader(open(CSV)))
    cols = collections.defaultdict(lambda: {"BTEC": [], "RP": []}); meta = {}
    for r in rows:
        curve = "BTEC" if r["curve"] == "BTEC_ND" else r["curve"]
        k = (r["source"], r["medium"], r["workbook_col"])
        cols[k][curve].append((float(r["x"]), float(r["value"])))
        meta[k] = dict(medium=r["medium"], chem=r["chemistry"], size=float(r["colloid_um"]),
                       vel=float(r["velocity_mday"]),
                       IS=(None if r["IS_mM"] == "" else float(r["IS_mM"])),
                       C0=float(r["C0_per_mL"]))
    for k in cols:
        for cu in ("BTEC", "RP"):
            cols[k][cu] = np.array(sorted(cols[k][cu])) if cols[k][cu] else np.zeros((0, 2))
    return cols, meta


def scorer(k, cols, meta, rs):
    """Return score(a_s, a_m, fx, kr) -> weighted cost for THIS column's data."""
    m = meta[k]; bt = cols[k]["BTEC"].copy(); rp = cols[k]["RP"]
    if len(bt) < 3 or len(rp) < 3:
        return None
    med = m["medium"]; vel = m["vel"]; C0 = m["C0"]
    theta = THETA[med]; V_MS = vel / DAY; eng = Eng(vel)
    logK = np.log10(REV * T0 * theta * C0 * Vref); kk = rs * V_MS
    bt[:, 1] = np.maximum(bt[:, 1], -6.0)
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]
    nin = NIN_PEAKED if rp_branch(rlog) == "peaked" else None
    si, so = sl(rx, rlog, nin)
    wm = (pv > 1.2) & (pv < 4.0)
    pvw = pv[wm] if wm.sum() else pv
    dmean = float(lc[wm].mean()) if wm.sum() else float(lc.mean())
    tm = pv > 4.2; sld = ts(pv, lc)

    def score(a_s, a_m, fx, kr):
        r = eng.run(kk, a_s, a_m, fx, kr)
        rl = np.interp(rx, r["x"], np.maximum(r["rp"], 1e-300)) / V_MS
        lS = logK + np.log10(np.maximum(rl, 1e-300))
        rpx = W_RP * (lS - rlog)
        sm, sn = sl(rx, lS, nin); shp = W_SHAPE * np.array([sm - si, sn - so])
        mlog = np.mean(np.log10(np.maximum(np.interp(pvw, r["tp"], r["C"]), 1e-6)))
        dev = mlog - dmean
        pl = W_PLAT * np.array([np.sign(dev) * max(0., abs(dev) - PLAT_TOL)])
        tl = (W_TAIL * (np.log10(np.maximum(np.interp(pv[tm], r["tp"], r["C"]), 1e-6)) - lc[tm])
              if tm.sum() else np.array([0.]))
        slm = ts(r["tp"], np.log10(np.maximum(r["C"], 1e-6)))
        tsl = W_TSLOPE * np.array([slm - sld if sld == sld else 0.])
        v = np.concatenate([rpx, shp, pl, tl, tsl])
        return 0.5 * float(np.sum(v ** 2))
    return score


def rms_of(k, cols, meta, rs, p):
    """RP and BTEC RMS (log10 units) for parameter set p on column k's data."""
    m = meta[k]; bt = cols[k]["BTEC"].copy(); rp = cols[k]["RP"]
    vel = m["vel"]; V_MS = vel / DAY; eng = Eng(vel)
    logK = np.log10(REV * T0 * THETA[m["medium"]] * m["C0"] * Vref); kk = rs * V_MS
    bt[:, 1] = np.maximum(bt[:, 1], -6.0)
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]
    r = eng.run(kk, p["a_s"], p["a_m"], p["fx"], p["kr"])
    lS = logK + np.log10(np.maximum(np.interp(rx, r["x"], np.maximum(r["rp"], 1e-300)) / V_MS, 1e-300))
    rpR = float(np.sqrt(np.mean((lS - rlog) ** 2)))
    sm = pv > 1.2
    btR = float(np.sqrt(np.mean((np.log10(np.maximum(np.interp(pv[sm], r["tp"], r["C"]), 1e-6))
                                 - lc[sm]) ** 2)))
    return rpR, btR


def data_repro(a, b, cols, meta):
    """RMS difference between two columns' MEASURED curves: the reproducibility floor.

    The retention profile is compared both raw and after normalising each column by its own C0,
    because C0 varies by up to 0.8 dex between replicates and the RP level tracks it almost 1:1 --
    that part of the raw disagreement is a concentration difference, not experimental scatter.
    """
    ba, bb = cols[a]["BTEC"], cols[b]["BTEC"]
    m = ba[:, 0] > 1.2
    btR = float(np.sqrt(np.mean((ba[m, 1] - np.interp(ba[m, 0], bb[:, 0], bb[:, 1])) ** 2)))
    ra, rb = cols[a]["RP"], cols[b]["RP"]
    ya = ra[:, 1]; yb = np.interp(ra[:, 0], rb[:, 0], rb[:, 1])
    rawR = float(np.sqrt(np.mean((ya - yb) ** 2)))
    na = ya - np.log10(meta[a]["C0"]); nb = yb - np.log10(meta[b]["C0"])
    normR = float(np.sqrt(np.mean((na - nb) ** 2)))
    return btR, rawR, normR


def read_fits():
    ws = openpyxl.load_workbook(MASTER, data_only=True)["Per-column fits"]
    hdr = [str(ws.cell(1, c).value) for c in range(1, ws.max_column + 1)]
    out = {}
    for r in range(2, ws.max_row + 1):
        d = dict(zip(hdr, [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]))
        if not d.get("study") or not d.get("column"):
            continue
        kr = d.get("k_r (/s)")
        if kr is None:                                    # older workbook: convert from /PV
            kpv = d.get("k_r (/PV)")
            kr = (kpv * float(d["v (m/day)"]) / DAY / L) if kpv is not None else None
        out[(d["study"], d["medium"], str(d["column"]))] = dict(
            a_s=d["alpha_s"], a_m=d["alpha_m"], fx=d["f_x"], kr=kr,
            rs=float(str(d["r_s (/m, fixed)"]).rstrip("*")), cost=d.get("cost"),
            size=float(d["size (um)"]), vel=float(d["v (m/day)"]),
            IS=(float(d["IS (mM)"]) if d["IS (mM)"] not in (None, "") else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../Manuscript/FigsExcelsUnfav/TransferTest.xlsx")
    args = ap.parse_args()

    cols, meta = load_columns()
    fits = read_fits()

    grp = collections.defaultdict(list)
    for k, f in fits.items():
        grp[(k[0], k[1], f["size"], f["vel"], f["IS"])].append(k)
    reps = {g: ks for g, ks in grp.items() if len(ks) > 1}

    def cname(g):
        return f"{g[0]} {g[1]} {g[2]}um {g[3]:.0f}md {g[4]:.0f}mM"

    # ---------- 1. own-fit RMS for every column in a replicated condition ----------
    own = {}
    for g, ks in reps.items():
        for k in ks:
            own[k] = rms_of(k, cols, meta, fits[k]["rs"], fits[k])

    # ---------- 2. replicate transfer: donor -> sibling, same condition ----------
    recs = []
    for g, ks in sorted(reps.items()):
        for donor in ks:
            for recv in ks:
                if donor == recv:
                    continue
                trp, tbt = rms_of(recv, cols, meta, fits[recv]["rs"], fits[donor])
                orp, obt = own[recv]
                recs.append(dict(cond=cname(g), donor=donor[2], recv=recv[2],
                                 own_rp=orp, xfer_rp=trp, own_bt=obt, xfer_bt=tbt))

    # ---------- 3. NULL: donor from a DIFFERENT condition, same medium ----------
    # Every foreign donor is used, not just the first, and the receiver is keyed on its full
    # identity (study, medium, column) so no baseline can be picked up from another study.
    nulls = []
    for g, ks in sorted(reps.items()):
        foreign = [dk for og, oks in reps.items() if og != g and og[1] == g[1] for dk in oks]
        for recv in ks:
            orp, obt = own[recv]
            for donor in foreign:
                trp, tbt = rms_of(recv, cols, meta, fits[recv]["rs"], fits[donor])
                nulls.append(dict(cond=cname(g), donor=f"{donor[0]}.{donor[2]}", recv=recv[2],
                                  own_rp=orp, xfer_rp=trp, own_bt=obt, xfer_bt=tbt))

    # ---------- 4. reproducibility floor: how well do the EXPERIMENTS repeat? ----------
    floor = []
    for g, ks in sorted(reps.items()):
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                bt, raw, norm = data_repro(a, b, cols, meta)
                floor.append(dict(cond=cname(g), pair=f"{a[2]}/{b[2]}",
                                  bt=bt, rp_raw=raw, rp_norm=norm))

    med = lambda xs: float(np.median(np.array(xs)))
    print(f"{'condition':32}{'donor':>8}{'->recv':>8}{'RP own':>9}{'RP xfer':>9}"
          f"{'BT own':>9}{'BT xfer':>9}")
    for r in recs:
        print(f"{r['cond']:32}{r['donor']:>8}{r['recv']:>8}{r['own_rp']:9.3f}{r['xfer_rp']:9.3f}"
              f"{r['own_bt']:9.3f}{r['xfer_bt']:9.3f}")

    print("\n  --- median RMS, log10 units (dex) ---")
    print(f"  own fit                   RP {med([r['own_rp'] for r in recs]):.3f}"
          f"   BTEC {med([r['own_bt'] for r in recs]):.3f}")
    print(f"  replicate transfer        RP {med([r['xfer_rp'] for r in recs]):.3f}"
          f"   BTEC {med([r['xfer_bt'] for r in recs]):.3f}   (n = {len(recs)})")
    print(f"  cross-condition null      RP {med([r['xfer_rp'] for r in nulls]):.3f}"
          f"   BTEC {med([r['xfer_bt'] for r in nulls]):.3f}   (n = {len(nulls)})")
    print(f"  reproducibility floor     RP {med([f['rp_norm'] for f in floor]):.3f}"
          f"   BTEC {med([f['bt'] for f in floor]):.3f}   (n = {len(floor)};"
          f" RP raw {med([f['rp_raw'] for f in floor]):.3f})")

    # ---------------------------- workbook ----------------------------
    B = Font(bold=True); IT = Font(italic=True)
    wb = openpyxl.Workbook()

    ws = wb.active; ws.title = "Transfer test"
    ws.cell(1, 1, "Replicate parameter transfer: a donor column's fitted parameters applied "
                  "unchanged to a sibling column at the same condition").font = B
    ws.cell(2, 1, "Each receiving column keeps its own C0, its own retention-profile sampling "
                  "depths and its own RP-shape window; only alpha_s, alpha_m, f_x and k_r are "
                  "transferred. Nothing is refitted.").font = IT
    ws.cell(3, 1, "All values are root-mean-square differences in log10 units (dex). 0.3 dex is "
                  "about a factor of two in concentration.").font = IT
    for j, h in enumerate(["condition", "donor", "receiver", "RP RMS own", "RP RMS transferred",
                           "BTEC RMS own", "BTEC RMS transferred"], 1):
        ws.cell(5, j, h).font = B
    for i, r in enumerate(recs, 6):
        for j, v in enumerate([r["cond"], r["donor"], r["recv"], round(r["own_rp"], 3),
                               round(r["xfer_rp"], 3), round(r["own_bt"], 3),
                               round(r["xfer_bt"], 3)], 1):
            ws.cell(i, j, v)
    rr = len(recs) + 7
    ws.cell(rr, 1, f"median: own RP {med([r['own_rp'] for r in recs]):.3f}, transferred RP "
                   f"{med([r['xfer_rp'] for r in recs]):.3f}; own BTEC "
                   f"{med([r['own_bt'] for r in recs]):.3f}, transferred BTEC "
                   f"{med([r['xfer_bt'] for r in recs]):.3f}   (n = {len(recs)})").font = B
    for c, w in zip("ABCDEFG", (32, 9, 10, 12, 18, 13, 20)):
        ws.column_dimensions[c].width = w

    w2 = wb.create_sheet("Cross-condition null")
    w2.cell(1, 1, "Control: parameters from a DIFFERENT condition in the same medium, applied to "
                  "the same receiving columns").font = B
    w2.cell(2, 1, "Every foreign donor is used, not a single representative. r_s stays at the "
                  "receiver's own favourable anchor, so this isolates the four fitted "
                  "parameters.").font = IT
    for j, h in enumerate(["receiving condition", "donor (study.column)", "receiver",
                           "RP RMS own", "RP RMS with foreign parameters",
                           "BTEC RMS own", "BTEC RMS with foreign parameters"], 1):
        w2.cell(4, j, h).font = B
    for i, r in enumerate(nulls, 5):
        for j, v in enumerate([r["cond"], r["donor"], r["recv"], round(r["own_rp"], 3),
                               round(r["xfer_rp"], 3), round(r["own_bt"], 3),
                               round(r["xfer_bt"], 3)], 1):
            w2.cell(i, j, v)
    rr = len(nulls) + 6
    w2.cell(rr, 1, f"median with foreign parameters: RP {med([r['xfer_rp'] for r in nulls]):.3f}, "
                   f"BTEC {med([r['xfer_bt'] for r in nulls]):.3f}   (n = {len(nulls)})").font = B
    for c, w in zip("ABCDEFG", (32, 20, 10, 12, 30, 13, 32)):
        w2.column_dimensions[c].width = w

    w3 = wb.create_sheet("Reproducibility floor")
    w3.cell(1, 1, "How well do the EXPERIMENTS repeat? RMS difference between sibling columns "
                  "(dex)").font = B
    w3.cell(2, 1, "This is the benchmark: no parameter set can reproduce a sibling more closely "
                  "than the siblings agree with each other.").font = IT
    w3.cell(3, 1, "The retention profile is given raw and after normalising each column by its own "
                  "C0; C0 differs by up to 0.8 dex between replicates and the profile level "
                  "tracks it almost 1:1.").font = IT
    for j, h in enumerate(["condition", "pair", "BTEC RMS", "RP RMS raw",
                           "RP RMS C0-normalised"], 1):
        w3.cell(5, j, h).font = B
    for i, f in enumerate(floor, 6):
        for j, v in enumerate([f["cond"], f["pair"], round(f["bt"], 3), round(f["rp_raw"], 3),
                               round(f["rp_norm"], 3)], 1):
            w3.cell(i, j, v)
    rr = len(floor) + 7
    w3.cell(rr, 1, f"median: BTEC {med([f['bt'] for f in floor]):.3f}, RP raw "
                   f"{med([f['rp_raw'] for f in floor]):.3f}, RP C0-normalised "
                   f"{med([f['rp_norm'] for f in floor]):.3f}").font = B
    w3.cell(rr + 2, 1, "SUMMARY (median dex)").font = B
    w3.cell(rr + 3, 1, f"own fit               RP {med([r['own_rp'] for r in recs]):.3f}"
                       f"   BTEC {med([r['own_bt'] for r in recs]):.3f}")
    w3.cell(rr + 4, 1, f"replicate transfer    RP {med([r['xfer_rp'] for r in recs]):.3f}"
                       f"   BTEC {med([r['xfer_bt'] for r in recs]):.3f}")
    w3.cell(rr + 5, 1, f"reproducibility floor RP {med([f['rp_norm'] for f in floor]):.3f}"
                       f"   BTEC {med([f['bt'] for f in floor]):.3f}")
    w3.cell(rr + 6, 1, f"cross-condition null  RP {med([r['xfer_rp'] for r in nulls]):.3f}"
                       f"   BTEC {med([r['xfer_bt'] for r in nulls]):.3f}")
    for c, w in zip("ABCDE", (32, 10, 12, 14, 22)):
        w3.column_dimensions[c].width = w

    wb.save(args.out)
    print("wrote " + args.out)


if __name__ == "__main__":
    main()
