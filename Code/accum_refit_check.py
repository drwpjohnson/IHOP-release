"""accum_refit_check.py -- what happens to the IHOP parameters when the invalid snapshot
convention is retired and the master is refitted against the ACCUMULATED solid phase.

WHY (W.P.J., 2026-08-25). The columns are excised at 10 PV, after ~7.0 PV of elution. The measured
retention profile is therefore the ACCUMULATED attached population. unfav_master_fit.py had been
fitting against Eng.run's `rp`, which was the Johnson 2018 eq (4) INJECTION-WINDOW RATE SNAPSHOT --
2.984 PV into a 10 PV run, with 70% of the experiment still to come. That is not a representation of
the observable and has been retired.

This script does NOT edit anything. It refits every unfavorable column both ways and reports how far
the parameters move, so the cost of the switch is known before it is made. Resumable: results
accumulate in accum_refit.json, one column per entry, so it can be run in short rounds.

RESULT (all 29 unfavorable columns, 2026-08-25) -- the switch is SAFE:
    a_s moves <= 0.090 dex        (largest: Li.S)
    a_m moves <= 0.180 dex        (largest: Li.M)
    RP peak depth moves > 0.5 cm on NO column -- the branch structure is untouched
    fit-quality median 12.42 -> 12.49; half-split n=17 median still 11.8 (the published value)
The only large shifts are f_x (2.6 dex) and k_r (3.8 dex) on Li.M, whose cost is unchanged to 2 dp
(0.72 -> 0.72). That is the known {f_x, v_ns, k_r} degeneracy on a column whose k_r is not
identifiable, not a real change -- and it is what exposed the one-sided degeneracy filters in
kr_trend.py and fx_trend.py, since Li.M's k_r stopped railing at 1e-6 and flew to 5.6e-3 instead.

WHAT WAS ALREADY KNOWN, and why the expectation was "barely moves":
  * At the MEASURED depths (1,3..19 cm) the two conventions differ by <= 0.033 log, essentially all
    of it at the single first point; on the column-integrated total they agree to <= 0.010 log,
    because assuming steady deposition across the whole injection overestimates by about what
    ignoring post-injection deposition underestimates. Two errors that nearly cancel -- which is why
    the eq (4) level-and-tilt validation passed: it measured the quantities that survive.
  * Scoring the master's own snap-fitted parameters under the accum objective gives 48.48 on Li.AE
    against the accum refit's 48.11 -- the objective values the same fit differently, it does not
    prefer different parameters.
  * The cost difference that does appear is almost entirely the RP-SHAPE block, because with nin=4
    the inlet log-slope is regressed over four points on a 6 cm baseline at weight 2.5, so a 0.032
    log shift at the first point alone moves the squared term by ~10.

Usage:  python3 accum_refit_check.py [--seconds 120]   (run repeatedly until it reports COMPLETE)
        Run from Code/ with the cleaned CSV in ../Data/.
"""
import argparse, json, os, time
import numpy as np

SNAP_SRC = "rp=(a_s*kf*Yst[0,:]+kmw*Yst[1,:]+kmg*Yst[2,:])"
# The accumulated attached population at the END of the run (10 PV), divided by the injection
# duration so it lands in the same units the amplitude anchor logK expects. This is exactly what
# Code/HYDEQ/hydeq_engine.py's IhopReferenceEngine returns as its `rp`.
ACCUM_SRC = "rp=(Y[3,:]/ti)"


def load_engine(accum):
    """Build a namespace from unfav_master_fit.py, optionally with the accumulated RP convention.

    NOTE: since 2026-08-25 unfav_master_fit.py IS the accum version, so the SNAP_SRC patch no longer
    matches and the snapshot arm of this comparison cannot be rebuilt from the current file. The
    measured result is recorded in the docstring above and in accum_refit.json. To re-run the
    comparison, recover the snapshot expression from version control first.
    """
    src = open("unfav_master_fit.py").read().split("# ---- fit all unfavorable")[0]
    if accum:
        if SNAP_SRC not in src:
            raise SystemExit("snapshot expression not found -- unfav_master_fit.py is already on the "
                             "accum convention (expected after 2026-08-25). See the docstring.")
        src = src.replace(SNAP_SRC, ACCUM_SRC)
    g = {}
    exec(src, g)
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--out", default="accum_refit.json")
    args = ap.parse_args()

    snap = load_engine(False)
    accum = load_engine(True)
    meta, cols = snap["meta"], snap["cols"]
    NIN_PEAKED = snap["NIN_PEAKED"]
    rp_branch, condition_branch = snap["rp_branch"], snap["condition_branch"]

    keys = [k for k, m in meta.items()
            if m["chem"] == "unfavorable" and not (m["IS"] is not None and m["IS"] <= 1.0)
            and len(cols[k]["RP"]) >= 3 and len(cols[k]["BTEC"]) >= 3]
    # condition-level branch window, exactly as the master computes it
    grp = {}
    for k in keys:
        m = meta[k]
        grp.setdefault((k[0], m["medium"], m["size"], m["vel"], m["IS"]), []).append(k)
    NIN = {}
    for key, ks in grp.items():
        b = condition_branch([rp_branch(cols[k]["RP"][:, 1]) for k in ks])
        for k in ks:
            # rp_branch/condition_branch are loaded via exec() from unfav_master_fit.py (line 79),
            # which was renamed 2026-09-01: the has-a-peak class is now literally "peaked".
            NIN[k] = NIN_PEAKED if b == "peaked" else None

    store = json.load(open(args.out)) if os.path.exists(args.out) else {}
    t0 = time.time()
    for k in sorted(keys):
        tag = f"{k[0]}.{k[2]}"
        if tag in store:
            continue
        if time.time() - t0 > args.seconds:
            break
        a = snap["fit_col"](k, nin_override=NIN[k])
        b = accum["fit_col"](k, nin_override=NIN[k])
        if a is None or b is None:
            continue
        store[tag] = dict(medium=meta[k]["medium"], size=meta[k]["size"], IS=meta[k]["IS"],
                          vel=meta[k]["vel"], nin=(NIN[k] or 0),
                          snap={f: a[f] for f in ("a_s", "a_m", "fx", "kr_pv", "cost", "rpRMS",
                                                  "rp_level", "rp_shape", "plateau", "tail_level",
                                                  "tail_slope", "pk_m")},
                          accum={f: b[f] for f in ("a_s", "a_m", "fx", "kr_pv", "cost", "rpRMS",
                                                   "rp_level", "rp_shape", "plateau", "tail_level",
                                                   "tail_slope", "pk_m")})
        json.dump(store, open(args.out, "w"), indent=1)
        print(f"  {tag:10s} done ({len(store)}/{len(keys)})", flush=True)

    if len(store) < len(keys):
        print(f"\nPARTIAL {len(store)}/{len(keys)} -- run again to continue")
        return

    print(f"\nCOMPLETE {len(store)}/{len(keys)} columns\n")
    hd = (f"{'column':10s}{'medium':7s}{'a_s snap':>10s}{'a_s acc':>10s}{'dex':>7s}"
          f"{'a_m snap':>10s}{'a_m acc':>10s}{'dex':>7s}{'f_x dex':>9s}{'k_r dex':>9s}"
          f"{'cost snap':>11s}{'cost acc':>10s}")
    print(hd); print("-" * len(hd))
    dex = lambda p, q: abs(np.log10(q / p)) if p > 0 and q > 0 else float("nan")
    worst = {"a_s": 0, "a_m": 0, "fx": 0, "kr_pv": 0}
    for tag in sorted(store):
        s, a = store[tag]["snap"], store[tag]["accum"]
        d = {f: dex(s[f], a[f]) for f in worst}
        for f in worst:
            worst[f] = max(worst[f], 0 if d[f] != d[f] else d[f])
        print(f"{tag:10s}{store[tag]['medium']:7s}{s['a_s']:10.4f}{a['a_s']:10.4f}{d['a_s']:7.3f}"
              f"{s['a_m']:10.4f}{a['a_m']:10.4f}{d['a_m']:7.3f}{d['fx']:9.3f}{d['kr_pv']:9.3f}"
              f"{s['cost']:11.2f}{a['cost']:10.2f}")
    print("\nlargest parameter shift, log10 units: " +
          "  ".join(f"{f} {v:.3f}" for f, v in worst.items()))
    pk = [(tag, store[tag]['snap']['pk_m'], store[tag]['accum']['pk_m']) for tag in sorted(store)]
    moved = [(t, x, y) for t, x, y in pk if abs(x - y) > 0.5]
    print(f"retention-profile peak depth changed by >0.5 cm on {len(moved)} columns: "
          + (", ".join(f"{t} {x:.1f}->{y:.1f}" for t, x, y in moved) if moved else "NONE"))


if __name__ == "__main__":
    main()
