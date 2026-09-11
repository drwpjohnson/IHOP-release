"""fav_convention_check.py -- does the retired RP convention move the FAVORABLE fits?

QUESTION (W.P.J., 2026-08-26). All Li/Tong columns were excised after 10 PV -- "one cannot
physically run 7 PV after excising the column" -- so `favorable_both_models.py`, which still builds
its RP as the eq (4) injection-window snapshot, is on the convention that was retired as invalid for
`unfav_master_fit.py` on 2026-08-25. Table 5 -> r_s -> FAVFIT -> every unfavorable alpha, so this
had to be measured rather than argued.

METHOD. Refit every favorable column TWICE, once under each convention, with everything else held
identical to `favorable_both_models.py` Model 2: k_r pinned per medium (at the values Table 5 used),
r_s free +/-0.6 dex of the plateau seed, alpha_s / alpha_m / f_x free, joint BTEC+RP objective,
same weights (W_RP 6, W_SH 2.5, W_BT 3), same two starts, same bounds, same max_nfev. Paired within
column, so nothing but the convention differs. `--ridge COL` sweeps r_s on one column with the other
three parameters refitted at each value, which is what distinguishes a real relocation from the
optimiser sliding along the r_s*alpha_s degeneracy.

CONTROL. Data are read from `Data/LiTong_experimental_data_tidy.csv` because the source workbook is
not reachable from the sandbox. The snapshot pass is therefore its own control: it must reproduce the
delivered Table 5. It does, exactly, on Tong L 47.5 / CS 15.2 / O 56.7 / AB 30.2 and quartz Li
B 120.6 / E 62.3 / I 68.9. It does NOT on the three Glass Beads Li columns, and that turned out to be
a defect in the CSV, not in the fit -- see the note at the foot of this docstring.

RESULT (2026-08-26). ** The convention does not move the favorable fits. ** Nine of ten columns move
r_s by <= 0.014 dex (3%), median 0.004 dex, at unchanged cost and with no r_s on its bound; RP RMS
slightly IMPROVES under accum on six of them. The tenth, quartz Li I (1.1 um, 8 m/d), appears to move
-0.208 dex -- but `--ridge qu-Li-I` shows r_s can be pinned anywhere from 42.7 to 68.9 for <= 0.01%
cost UNDER EITHER CONVENTION, with alpha_s sliding 0.88 -> 0.60 to compensate. r_s is simply not
identifiable on that column; the apparent move is the r_s*alpha_s degeneracy, not the convention.
Across all ten the identifiable product r_s*alpha_s moves at most 0.040 dex, median 0.003.
CONCLUSION: FAVFIT stands as it is. Keeping quartz(1.1, 8.0) = 68.9 costs 0.01% under accum.

WHY THE FAVORABLE SET IS INSENSITIVE WHERE THE UNFAVORABLE SET WAS NOT (W.P.J.): under favorable
chemistry the multiple-intercepting population is negligible, so almost nothing is left in a mobile
state to redistribute during the 7 PV of elution that the snapshot ignores. The extra pore volumes of
extended tailing are therefore not a problem here. The unfavorable set, where that population carries
the interior peak, is the case the convention actually mattered for -- and it was corrected there.

** DEFECT FOUND IN PASSING, 2026-08-26. RESOLVED 2026-09-01 -- see Records/CLAUDE.md. ** In the tidy
CSV, `Microspheres Glass Beads Li` col E carries BYTE-IDENTICAL BTEC and RP to `Microspheres Glass
Beads Tong` col AB, though the two are labelled as different experiments (0.98 um / 10 mM vs 1.0 um /
50 mM). W.P.J. confirmed 2026-09-01 this is not a data-entry error: both studies used the same
underlying run, deliberately -- so it is ONE experiment, not two.
   The "Glass Beads Li B also misses Table 5 (49.9 vs 57.9) and Li H by 0.003 dex, cause not
established" note below was this session's own earlier finding of the SAME root cause, not a separate
mystery: `favorable_both_models.py`'s `load_li()` used one hardcoded RP row range for both Li sheets,
correct for Quartz but 6 rows short for Glass Beads Li (whose RP header sits lower), silently
truncating Glass Li B/E/H's RP to 4 of 10 points. This script's own fit, reading the CSV (already
correctly ranged since `extract_tidy_data.py`'s 2026-08-28 fix), got the right answer all along --
49.9 for B -- while the buggy direct-xlsx Table 5 fit stayed stuck at 57.9. Fixed in
`favorable_both_models.py` 2026-09-01; Table 5 now reads 49.9 / 30.2 / 29.6 for B/E/H. `FAVFIT`
(this file's own dict elsewhere in `Code/`) was updated to match the corrected numbers the same day.

Usage:  python3 fav_convention_check.py [budget_seconds]      # fits both conventions, caches
        python3 fav_convention_check.py --report              # prints the comparison table
        python3 fav_convention_check.py --ridge qu-Li-I       # r_s sweep at fixed cost
Writes fav_convention_check.json (cache; delete to refit).
"""
import csv, json, math, os, sys, time
import numpy as np
from scipy.linalg import expm
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import splu
from scipy.optimize import least_squares

CSV = "Data/LiTong_experimental_data_tidy.csv"
CACHE = "fav_convention_check.json"
DAY = 86400.; L = 0.2
REV, T0, Vref = 22.801836559387397, 3.58, 0.1667
INJPV = T0 / (L / Vref)
KR_MED = {"glass": 5.58e-5, "quartz": 1.87e-5}   # as pinned in Table 5 (superseded values kept on purpose)
THETA = {"glass": 0.375, "quartz": 0.36}
W_RP, W_SH, W_BT = 6.0, 2.5, 3.0


def load():
    _all_rows = list(csv.DictReader(open(CSV)))
    # GUARD, 2026-09-01: the shared master CSV was silently overwritten with a 352-row/Li-only
    # a_mg-probe subset for a month before anyone noticed -- see Records/CLAUDE.md.
    _srcs = set(r['source'] for r in _all_rows)
    assert len(_all_rows) >= 1200 and 'Li' in _srcs and 'Tong' in _srcs, (
        f"CSV at {CSV!r} looks like a subset ({len(_all_rows)} rows, sources={_srcs}), not the full "
        "master (~1529 rows, both Li and Tong) -- refusing to run on a silently-truncated dataset.")
    rows = [r for r in _all_rows if r["chemistry"] == "favorable"]
    cols = {}
    for r in rows:
        key = (r["workbook_tab"], r["workbook_col"])
        d = cols.setdefault(key, dict(BTEC=[], RP=[], med=r["medium"],
                                      size=float(r["colloid_um"]), vel=float(r["velocity_mday"]),
                                      IS=float(r["IS_mM"]), C0=float(r["C0_per_mL"])))
        d[r["curve"]].append((float(r["x"]), float(r["value"])))
    # Model 2 needs BTEC>=3 AND RP>=3, as in favorable_both_models.py; the three RP-only Tong
    # columns (B, AU, BB) drop out here exactly as they do there. Key on medium+source+column,
    # because the column letter alone repeats across tabs.
    named = {}
    for (tab, col), d in cols.items():
        bt = np.array(sorted(d["BTEC"])) if d["BTEC"] else np.zeros((0, 2))
        rp = np.array(sorted(d["RP"]))
        if len(bt) < 3 or len(rp) < 3:
            continue
        d["bt"], d["rp"] = bt, rp
        named[f"{d['med'][:2]}-{'Tong' if 'Tong' in tab else 'Li'}-{col}"] = d
    return named


class Eng:
    def __init__(s, vmday):
        s.v = vmday / DAY; s.dx = L / 90; s.dt = s.dx / s.v; s.pv = L / s.v

    def run(s, k1, a_s, a_m, fx, kr, vns=0.05, tot=10):
        kf = k1; k2 = fx * kf; kmw = a_m * kf; kmg = a_m * vns * kf
        G = np.zeros((4, 4))
        G[0, 0] -= kf; G[3, 0] += a_s * kf; G[1, 0] += (1 - a_s) * kf
        G[1, 1] -= (kmw + k2); G[3, 1] += kmw; G[2, 1] += k2
        G[2, 2] -= kmg; G[3, 2] += kmg; G[1, 2] += kr; G[2, 2] -= kr
        E = expm(G * s.dt); D = s.v * L / 150; r = D * s.dt / s.dx**2
        mn = (1 + 2 * r) * np.ones(90); of = -r * np.ones(89); mn[0] = 1 + r; mn[-1] = 1 + r
        lu = splu(csc_matrix(diags([of, mn, of], [-1, 0, 1], format="csc")))
        nt = int(round(tot * 90)); ti = INJPV * s.pv; c = vns
        Y = np.zeros((4, 90)); C = np.zeros(nt); t = 0.; Yst = None
        for i in range(nt):
            Y = E @ Y
            C[i] = Y[0, -1] + Y[1, -1] + c * Y[2, -1]
            Y[0, 1:] = Y[0, :-1]; Y[0, 0] = 0; Y[1, 1:] = Y[1, :-1]; Y[1, 0] = 0
            ym = Y[2].copy(); Y[2, 1:] = ym[1:] - c * (ym[1:] - ym[:-1]); Y[2, 0] = ym[0] * (1 - c)
            t += s.dt
            if t < ti: Y[0, 0] += 1.
            Y[0, :] = lu.solve(Y[0, :]); Y[1, :] = lu.solve(Y[1, :])
            if t < ti and t > 0.9 * ti: Yst = Y.copy()
        tp = (np.arange(nt) + 1) * s.dt / s.pv; x = (np.arange(90) + 0.5) * s.dx
        rp_snap = a_s * kf * Yst[0, :] + kmw * Yst[1, :] + kmg * Yst[2, :]   # RETIRED convention
        rp_acc = Y[3, :] / ti                                               # accumulated at excision
        return dict(tp=tp, C=np.maximum(C, 1e-300), x=x,
                    snap=np.maximum(rp_snap, 1e-300), acc=np.maximum(rp_acc, 1e-300))


def sl(x, y):
    h = len(x) // 2
    return float(np.polyfit(x[:h + 1], y[:h + 1], 1)[0]), float(np.polyfit(x[h:], y[h:], 1)[0])


def rs_plateau(bt):
    pv = bt[:, 0]; lc = bt[:, 1]; m = (pv > 1.2) & (pv < 3.4)
    if m.sum() < 2: m = (pv > 0.9) & (pv < 3.6)
    if m.sum() < 2: return None
    return -np.log(10) * float(np.median(lc[m])) / L


def fit_one(d, conv):
    med = d["med"]; vel = d["vel"]; bt = d["bt"]; rp = d["rp"]
    V_MS = vel / DAY; eng = Eng(vel); theta = THETA[med]; kr = KR_MED[med]
    logK = np.log10(REV * T0 * theta * d["C0"] * Vref)
    rs_seed = rs_plateau(bt)
    if rs_seed is None or rs_seed <= 0: return None
    pv = bt[:, 0]; lc = bt[:, 1]; rx = rp[:, 0]; rlog = rp[:, 1]
    si, so = sl(rx, rlog); k1s = np.log10(rs_seed * V_MS)

    def resid(p):
        kk = 10**p[0]; a_s = 1 - 10**p[1]; am = 10**p[2]; fx = 10**p[3]
        r = eng.run(kk, a_s, am, fx, kr)
        mC = np.log10(np.maximum(np.interp(pv, r["tp"], r["C"]), 1e-12))
        lS = logK + np.log10(np.maximum(np.interp(rx, r["x"], r[conv]) / V_MS, 1e-300))
        sm, sn = sl(rx, lS)
        return np.concatenate([W_RP * (lS - rlog), W_SH * np.array([sm - si, sn - so]),
                               W_BT * (mC - lc)])

    best = None
    for s0 in ([k1s, -1.5, -1.5, np.log10(.005)], [k1s, -2.0, -2.0, np.log10(.02)]):
        rr = least_squares(resid, s0,
                           bounds=([k1s - 0.6, -3, -3.3, np.log10(1e-4)],
                                   [k1s + 0.6, np.log10(0.5), np.log10(0.9), np.log10(0.1)]),
                           max_nfev=60)
        if best is None or rr.cost < best.cost: best = rr
    k1f = 10**best.x[0]; a_s = 1 - 10**best.x[1]; a_m = 10**best.x[2]; fx = 10**best.x[3]
    r1 = eng.run(k1f, a_s, a_m, fx, kr)
    lS1 = logK + np.log10(np.maximum(np.interp(rx, r1["x"], r1[conv]) / V_MS, 1e-300))
    tm = pv > 4.2
    tailRMS = (float(np.sqrt(np.mean((np.log10(np.maximum(
        np.interp(pv[tm], r1["tp"], r1["C"]), 1e-12)) - lc[tm])**2))) if tm.sum() >= 2 else None)
    return dict(rs_seed=rs_seed, rs=k1f / V_MS, a_s=a_s, MIpct=100 * (1 - a_s), a_m=a_m, fx=fx,
                cost=float(best.cost), rpRMS=float(np.sqrt(np.mean((lS1 - rlog)**2))),
                tailRMS=tailRMS, size=d["size"], vel=vel, IS=d["IS"], med=med,
                railed_rs=bool(abs(best.x[0] - k1s) > 0.599))


def report():
    d = json.load(open(CACHE))
    names = sorted({k.split("|")[0] for k in d})
    print(f"{'column':12}{'med':7}{'um':>5}{'v':>4}{'r_s snap':>10}{'r_s acc':>9}{'dex':>7}"
          f"{'a_s snap':>10}{'a_s acc':>9}{'rs*a_s dex':>12}{'f_x snap':>10}{'f_x acc':>9}"
          f"{'rpRMS s':>9}{'rpRMS a':>9}{'cost s':>10}{'cost a':>10}")
    ds, ps = [], []
    for n in names:
        s_, a = d[n + "|snap"], d[n + "|acc"]
        dx = math.log10(a["rs"] / s_["rs"]); dp = math.log10((a["rs"] * a["a_s"]) / (s_["rs"] * s_["a_s"]))
        ds.append(abs(dx)); ps.append(abs(dp))
        print(f"{n:12}{s_['med']:7}{s_['size']:>5}{s_['vel']:>4.0f}{s_['rs']:>10.1f}{a['rs']:>9.1f}"
              f"{dx:>+7.3f}{s_['a_s']:>10.4f}{a['a_s']:>9.4f}{dp:>+12.3f}"
              f"{s_['fx']:>10.5f}{a['fx']:>9.5f}{s_['rpRMS']:>9.3f}{a['rpRMS']:>9.3f}"
              f"{s_['cost']:>10.2f}{a['cost']:>10.2f}")
    md = lambda v: sorted(v)[len(v) // 2]
    print(f"\n|d log10 r_s|       max {max(ds):.3f}  median {md(ds):.3f}  mean {sum(ds)/len(ds):.3f}")
    print(f"|d log10 r_s*a_s|   max {max(ps):.3f}  median {md(ps):.3f}  mean {sum(ps)/len(ps):.3f}")
    print(f"moving r_s > 0.02 dex: {[n for n, v in zip(names, ds) if v > 0.02]}")
    print(f"r_s on its +/-0.6 dex bound: {[k for k, v in d.items() if v['railed_rs']] or 'none'}")


def ridge(name, sweep=(68.9, 55.0, 42.7)):
    """Pin r_s, refit the other three, report the cost penalty -- flat => r_s not identifiable."""
    from scipy.optimize import least_squares as ls
    d = load()[name]
    V_MS = d["vel"] / DAY; eng = Eng(d["vel"]); kr = KR_MED[d["med"]]
    logK = np.log10(REV * T0 * THETA[d["med"]] * d["C0"] * Vref)
    bt, rp = d["bt"], d["rp"]; pv, lc = bt[:, 0], bt[:, 1]; rx, rlog = rp[:, 0], rp[:, 1]
    si, so = sl(rx, rlog)

    def at(rs_fixed, conv):
        kk = rs_fixed * V_MS

        def resid(p):
            a_s = 1 - 10**p[0]; am = 10**p[1]; fx = 10**p[2]
            r = eng.run(kk, a_s, am, fx, kr)
            mC = np.log10(np.maximum(np.interp(pv, r["tp"], r["C"]), 1e-12))
            lS = logK + np.log10(np.maximum(np.interp(rx, r["x"], r[conv]) / V_MS, 1e-300))
            sm, sn = sl(rx, lS)
            return np.concatenate([W_RP * (lS - rlog), W_SH * np.array([sm - si, sn - so]),
                                   W_BT * (mC - lc)])
        best = None
        for s0 in ([-1.5, -1.5, np.log10(.005)], [-2.0, -2.0, np.log10(.02)],
                   [-0.4, -0.3, np.log10(.01)]):
            rr = ls(resid, s0, bounds=([-3, -3.3, np.log10(1e-4)],
                                       [np.log10(0.5), np.log10(0.9), np.log10(0.1)]), max_nfev=60)
            if best is None or rr.cost < best.cost: best = rr
        return best.cost, 1 - 10**best.x[0], 10**best.x[1], 10**best.x[2]

    print(f"{name} -- r_s PINNED, alpha_s / alpha_m / f_x refitted at each value")
    print(f"{'convention':11}{'r_s pinned':>11}{'cost':>10}{'excess':>10}{'a_s':>9}{'a_m':>9}{'f_x':>10}")
    for conv in ("snap", "acc"):
        ref = min(at(v, conv)[0] for v in sweep)
        for rs in sweep:
            c, a_s, a_m, fx = at(rs, conv)
            print(f"{conv:11}{rs:>11.1f}{c:>10.2f}{100*(c-ref)/ref:>+9.2f}%{a_s:>9.4f}{a_m:>9.4f}{fx:>10.5f}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        return report()
    if len(sys.argv) > 2 and sys.argv[1] == "--ridge":
        return ridge(sys.argv[2])
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 150.
    t0 = time.time()
    cols = load()
    res = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [(n, c) for n in sorted(cols) for c in ("snap", "acc") if f"{n}|{c}" not in res]
    print(f"{len(cols)} favorable columns; {len(todo)} fits remaining")
    for n, c in todo:
        if time.time() - t0 > budget:
            print("budget reached; rerun to continue"); break
        r = fit_one(cols[n], c)
        res[f"{n}|{c}"] = r
        json.dump(res, open(CACHE, "w"), indent=1)
        print(f"  {n:16s} {c:5s} rs={r['rs']:8.1f} a_s={r['a_s']:.4f} f_x={r['fx']:.5f} "
              f"cost={r['cost']:.2f}  [{time.time()-t0:.0f}s]")
    print(f"done {len(res)} / {2*len(cols)}")


if __name__ == "__main__":
    main()
