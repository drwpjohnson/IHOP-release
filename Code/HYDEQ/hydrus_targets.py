"""hydrus_targets.py -- emit plain-CSV target curves for the HYDRUS-1D forward cross-check.

For each canonical column, regenerates the HYDEQ two-site model curves from the cached fitted
parameters and writes one CSV per column. Noah runs the same parameters in HYDRUS-1D and diffs
against these files, rather than reading numbers off a spreadsheet by eye.
Companion document: Records/hydeq_hydrus_verification.md.

WHY THE TWO-SITE STRUCTURE. It is the right structure for a CODE-CORRECTNESS check:
  * all four rate coefficients are active (k_a1, k_d1, k_a2, k_d2), so both attachment and detachment
    are exercised on two independent sites -- the core of the kinetic machinery;
  * no straining term, so no psi(x) implementation question rides along;
  * no blocking, so the system is linear and reproducible exactly;
  * HYDRUS-1D supports two kinetic sites natively, with no mapping argument required;
  * and -- checked, not assumed -- NO two-site fit rails a parameter to a bound on any of the five
    canonical columns, so these are genuine fitted values rather than optimiser bound artifacts.
    (Two of the five STRAINING fits do rail k_str to its floor, which is why straining is a poor
    forward-check subject: it would verify that both codes reproduce a switched-off term.)

WHAT THE COLUMNS MEAN
  pore_volumes, log10_C_C0_model     breakthrough, HYDEQ two-site model
  log10_C_C0_measured                the data, on the measured PV grid (blank where not sampled);
                                     CONTEXT ONLY -- it is not the comparison target
  distance_m, distance_cm            retention-profile depth
  log10_spheres_model                RP in HYDEQ/manuscript units (log10 spheres per unit)
  S_final_dimensionless              solid phase at 10 PV, dimensionless: attached / C0, per mL
                                     of PORE WATER
  N_spheres_model                    # OF COLLOIDS PER SEGMENT = REV*theta*C0*S. This is the RAW
                                     DATA UNIT -- the measured RPs are counts per excised segment,
                                     REV = 22.80 mL. Identical to 10**log10_spheres_model.
  s_model_per_g_solid                THE SAME QUANTITY IN HYDRUS' BASIS: s = (theta/rho_b)*S*C0,
                                     per gram of solid. Compare HYDRUS' solid-phase output to THIS
                                     column directly -- the basis conversion is already done here so
                                     that a units slip cannot masquerade as a model disagreement.

The retention profile is taken at 10 PV (end of run), which is when the column is excised -- NOT at
end of injection. That single choice is the most common way this check goes wrong.

Usage:  python3 hydrus_targets.py --cache hydeq_canon.json --csv ../Data/LiTong_experimental_data_tidy.csv
"""
import argparse, csv, json, os
import numpy as np
from hydeq_engine import HydeqEngine, THETA, DAY, L, REV, T0, Vref, INJPV
from hydeq_fit import load, prep, branch_windows, CANON_COLS

RHO_SOLID = 2.65          # g/cm3, quartz/glass grain density
MODEL = "M2_2site"
LABEL = {"R": "glass 1.1um 4md 6mM", "V": "quartz 1.1um 4md 6mM", "O": "glass 1.1um 4md 20mM",
         "P": "quartz 1.1um 4md 20mM", "AE": "quartz 1.1um 4md 3mM"}
ORDER = ["R", "V", "O", "P", "AE"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="hydeq_canon.json")
    ap.add_argument("--csv", default="../Data/LiTong_experimental_data_tidy.csv")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    store = json.load(open(args.cache))
    cols, meta = load(args.csv)
    NIN = branch_windows(cols, meta)

    print(f"{'column':22s} {'k_a1':>10s} {'k_d1':>10s} {'k_a2':>10s} {'k_d2':>10s}   rho_b   theta")
    for cl in ORDER:
        kk = [k for k in meta if k[0] == "Li" and k[2] == cl]
        if not kk:
            print(f"  !! column Li.{cl} not in CSV"); continue
        k = kk[0]
        ck = "|".join(["accum", k[0], k[1], k[2], MODEL, "w4" if NIN.get(k) else "wH"])
        if ck not in store:
            print(f"  !! no cached {MODEL} fit for Li.{cl} (key {ck})"); continue
        rec = store[ck]
        d = prep(k, cols, meta, nin=NIN.get(k))
        med = d["med"]; theta = THETA[med]; rho_b = (1 - theta) * RHO_SOLID
        eng = HydeqEngine(d["vel"], med)
        r = eng.run(MODEL, np.array(rec["p"]))

        pars = dict(zip(rec["names"], [10.0 ** v for v in rec["p"]]))
        print(f"Li.{cl:<3s} {LABEL[cl]:16s} " +
              " ".join(f"{pars.get(n, float('nan')):10.3e}" for n in ("k_a1", "k_d1", "k_a2", "k_d2")) +
              f"  {rho_b:6.3f}  {theta:5.3f}")

        # breakthrough
        tp = r["tp"]; lc = np.log10(np.maximum(r["C"], 1e-300))
        meas = np.full(len(tp), np.nan)
        # nearest-neighbour tag of the measured points onto the model grid, for context only
        for xm, ym in zip(d["pv"], d["lc"]):
            j = int(np.argmin(np.abs(tp - xm)))
            meas[j] = ym

        # retention profile at 10 PV.
        # r['rp'] is S_final/ti -- a RATE, not the solid phase. Recover the solid phase itself before
        # any per-gram conversion: S_final = rp * ti, with ti the injection duration in seconds.
        # (Getting this wrong would hand Noah a target off by a factor of ti ~ 1.3e4 s, which would
        # look like a catastrophic model disagreement rather than a units slip.)
        ti = INJPV * eng.pv
        rp = r["rp"]                                    # accumulated to excision, /s
        lS = d["logK"] + np.log10(np.maximum(rp / d["V_MS"], 1e-300))
        S_final = rp * ti                               # dimensionless: solid phase in C/C0 units
        # THE UNIT CHAIN, once, so nobody has to rediscover it (W.P.J., 2026-08-25):
        #   S                 dimensionless -- attached / C0, per mL of PORE WATER
        #   x C0              # per mL pore water
        #   x theta           # per mL BULK
        #   x REV (22.80 mL)  # PER SEGMENT  <-- this is the raw data unit; = 10^log10_spheres
        #   (or, instead of x REV:  / rho_b  -> # per g solid, which is what HYDRUS outputs)
        # REV is the excised segment volume (data_inventory.md: "S(x) = number of colloids retained
        # per segment; V = segment volume", REV = 22.80 mL). It is reproducible from geometry:
        # pi*(0.75 inch = 1.905 cm)^2 * 2 cm = 22.801836559387397 -- a 1.5-inch-ID column in 2 cm
        # slices, matching the 1,3,5..19 cm RP midpoints.
        # Note logK = log10(REV*T0*theta*C0*v) LOOKS like it depends on injection duration and
        # velocity, but T0*Vref = INJPV*L cancels against rp = S_final/T0, leaving exactly
        #   spheres = REV * theta * C0 * S_final
        # Verified against log10_spheres_model to 6 decimals on glass R.
        # theta/rho_b = mL water per g solid; times S_final*C0 (colloids per mL water) -> per g solid
        s_per_g = (theta / rho_b) * S_final * d["C0"]
        n_spheres = REV * theta * d["C0"] * S_final     # linear count, same as 10**lS

        fn = os.path.join(args.outdir, f"hydrus_target_{med[:2]}{cl}_{d['IS']:.0f}mM.csv")
        with open(fn, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow([f"# HYDRUS-1D forward cross-check target -- Li column {cl}, {LABEL[cl]}"])
            w.writerow([f"# structure: two kinetic sites (attachment + detachment), HYDEQ {MODEL}"])
            w.writerow([f"# k_a1={pars.get('k_a1'):.6e} 1/s  k_d1={pars.get('k_d1'):.6e} 1/s  "
                        f"k_a2={pars.get('k_a2'):.6e} 1/s  k_d2={pars.get('k_d2'):.6e} 1/s"])
            w.writerow([f"# theta={theta:.4f}  rho_b={rho_b:.4f} g/cm3  C0={d['C0']:.4e} per mL  "
                        f"v={d['vel']:.1f} m/day  L={L:.3f} m"])
            w.writerow([f"# retention profile is at 10 PV (END OF RUN), not end of injection"])
            w.writerow([f"# unit chain:  S (per mL pore water, /C0)  x C0 -> #/mL water  "
                        f"x theta -> #/mL bulk  x REV({REV:.4f} mL) -> # PER SEGMENT (= raw data unit)"])
            w.writerow([f"# compare HYDRUS solid phase against s_model_per_g_solid -- conversion already applied"])
            w.writerow([])
            w.writerow(["BREAKTHROUGH"])
            w.writerow(["pore_volumes", "log10_C_C0_model", "log10_C_C0_measured"])
            for i in range(len(tp)):
                w.writerow([f"{tp[i]:.6f}", f"{lc[i]:.6f}",
                            "" if np.isnan(meas[i]) else f"{meas[i]:.6f}"])
            w.writerow([])
            w.writerow(["RETENTION PROFILE (at 10 PV)"])
            w.writerow(["distance_m", "distance_cm", "log10_spheres_model",
                        "S_final_dimensionless", "N_spheres_model", "s_model_per_g_solid"])
            for i in range(len(r["x"])):
                w.writerow([f"{r['x'][i]:.6f}", f"{r['x'][i]*100:.4f}", f"{lS[i]:.6f}",
                            f"{S_final[i]:.6e}", f"{n_spheres[i]:.6e}", f"{s_per_g[i]:.6e}"])
        print(f"    -> {os.path.basename(fn)}  ({len(tp)} BTEC rows, {len(r['x'])} RP rows)")


if __name__ == "__main__":
    main()
