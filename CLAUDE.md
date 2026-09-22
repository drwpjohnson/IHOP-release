# Instructions for AI assistants (and people) working in this repository

This is the archived reproducer chain for Johnson et al. (2026, *Water Resources Research*): the IHOP
colloid-transport model, the scripts that produced every number in the paper, the compiled dataset, and the
methods records. It is **not a package**. Read this file before editing or running anything.

## The one rule

**Do not rewrite the fitting engine, and do not re-derive the model from the paper.** The engine is
`Code/unfav_master_fit.py` (class `Eng`, function `fit_col`). Its conventions are the product of documented
decisions, several of which reversed earlier choices for reasons that are not visible from the equations alone.
Adapting this code to new data means adapting its **data loader**, not its model.

## Before you change a file, and again after

```
cd Code
python3 unfav_master_fit.py --check
```

This refits three published columns (~30 s) and compares them with the archived master workbook. It must say
`CHECK PASSED` before you start and after you finish. If it fails after your edit, the engine or objective no
longer does what the paper says it does — stop and find out why. A rewrite that *runs* is the failure mode
this guards against; a crash is the easy case.

## Conventions you must not silently change

- **Retention profile = accumulated solid phase at excision** (`rp = Y[3]/ti` in `Eng.run`). An earlier
  injection-window *snapshot* convention (Johnson et al. 2018 eq. 4) is **retired** and must not be reintroduced.
  `favorable_both_models.py` still carries it for the favorable-chemistry fits, for reasons recorded in
  `Records/plateau_rs_decision.md` §3b — it is not a template for new fits.
- **r_s is pinned**, not fitted, to the favorable-condition anchor for the same medium / size class / velocity
  (`FAVFIT` in `unfav_master_fit.py`). New media or sizes need their own anchor or the Tufenkji–Elimelech
  fallback the script already provides.
- **The objective** (five weighted blocks, `W_RP, W_SHAPE, W_PLAT, W_TAIL, W_TSLOPE`), the plateau tolerance,
  the −6 log₁₀ BTEC floor, the `IS ≤ 1 mM` exclusion, and the **branch-aware RP-shape window** (`rp_branch`,
  `condition_branch`, `NIN_PEAKED`) are method choices with their reasons in `Records/`. Change them only
  deliberately, and write down why.
- **v_ns = 0.05·v** is pinned. **k_r** is fitted but sits in a degeneracy with f_x; do not read meaning into
  its per-column value (`Records/kr_trend_analysis.md`).

## Fitting other data

1. Write the data into the tidy-CSV format of `Data/LiTong_experimental_data_tidy.csv` (columns documented in
   `Records/data_inventory.md`), **under a new filename**.
2. Run `python3 unfav_master_fit.py --csv yourfile.csv --allow-small-csv --out yourmaster.xlsx`.
   The `--allow-small-csv` flag relaxes a guard that exists to protect this project's shared master file;
   the message it prints explains why. If your retention profiles are not 10 points at 2 cm, `--nin-peaked`
   (the inlet points scored on a peaked profile) must be re-derived for your grid — see `sl()`.
3. If your columns need a loader change (different metadata, different C₀ handling), make it in the CSV-reading
   block of `unfav_master_fit.py`, run `--check` to confirm the published columns still reproduce, and record
   what you changed and why in your own notes.

## Where the reasons live

`Records/` holds the methods and decision records the paper cites. `MANIFEST.md` lists what this deposit
withholds (exploratory variants, the working notebook) and why. If a comment in a script points at a file
that is not here, that is the reason.
