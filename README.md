# IHOP — Interception-History Outcome Predictor for colloid transport in porous media

**Code, data, and methods records for:**
Johnson, W. P., et al. (2026). *[manuscript title]*. Submitted to *Water Resources Research*.

**Archival copy:** Zenodo, [https://doi.org/10.5281/zenodo.22715530](https://doi.org/10.5281/zenodo.22715530)
**This repository:** the same deposit, browsable, tagged `v1.0-wrr-submission` at the state deposited to Zenodo.

---

## What this is

IHOP is a colloid-transport model that makes two mechanisms explicit: **interception history** — colloids that attach on a first, single interception versus colloids that attach only after multiple, returned interceptions — and **interception focusing**, the enhanced delivery of the returned population into a grain-to-grain crawl. One structure reproduces excised-column retention profiles (RP) and full breakthrough–elution curves (BTEC) — multiexponential and nonmonotonic RPs, BTEC plateaus and extended tailing — across two media (glass beads, quartz sand), colloid sizes 0.1–2.0 µm, pore velocities 2–8 m/day, ionic strengths 3–50 mM, and both favorable and unfavorable attachment chemistry, with no straining and no detachment terms.

**This deposit is a curated subset of a larger private research repository.** It contains what is needed to reproduce the figures, tables, and claims of the paper. It deliberately omits exploratory model variants that were tested and not adopted, development history superseded by the published structure, and manuscript drafts. `MANIFEST.md` lists every withheld script and record by name, so a reference to one of them inside an included file is not a broken link.

The experimental data are **digitized from previously published column experiments** (Li et al.; Li and Johnson; Tong and Johnson — see `Records/data_inventory.md` for the full source list). This is a compilation, not a new dataset; cite the original papers for the measurements.

---

## Contents

```
MANIFEST.md                    what ships, what is withheld, and why
Code/                          44 scripts: the fitting engine, trend analyses, figure and table builders
Code/HYDEQ/                    the conventional-model (HYDEQ) comparison, fitted under the identical objective
Records/                       12 methods and decision records (see RELEASE_MANIFEST.md for the reasoning)
Data/                          the tidy experimental dataset (CSV), its extractor, and its README
Manuscript/Figures/            figure workbooks — the manuscript figures are native Excel charts,
                               so these files ARE the plotted values (SI-Figures/ holds the SI sources)
Manuscript/Tables/             the curated table artefacts, named by table number (what the paper reports)
Manuscript/FigsExcelsUnfav/    generated workbooks: UnfavorableMaster.xlsx (the central fit product),
                               k_r / f_x / alpha trend workbooks, transfer test, weight robustness
Manuscript/FigsExcelsFavorable/  the favorable-chemistry fits
Manuscript/HYDEQ/              the HYDEQ comparison workbook and the HYDRUS-1D cross-check
Manuscript/SI-spreadsheets/    CodeInventory.xlsx (one row per script) and DLVO_Kramers.xlsx
```

Provenance chain for any table: script → generated workbook (`FigsExcels*/`) → curated table file (`Tables/`). The generated workbooks are the guideposts for recreating the analysis; the `Tables/` files are what the paper reports. Regenerating a workbook may differ from the shipped copy in the last decimal.

---

## Requirements

Python 3.9 or later with `numpy`, `scipy`, `openpyxl`, `matplotlib` (`pip install -r requirements.txt`).
One script, `Code/build_manuscript_tables.js`, is Node.js and needs the `docx` package (`npm install docx`).

---

## Reproducing the analysis

Run every script **from inside `Code/`** (they locate data and outputs by `../Data/` and `../Manuscript/` relative paths).

> **Scripts write into `../Manuscript/FigsExcels*/`, overwriting the shipped workbooks.** If you want to compare a fresh run against the deposited values, copy the `Manuscript/` tree aside first.

The chain, in dependency order:

| step | command | produces |
|---|---|---|
| 1 | `python unfav_master_fit.py` | `UnfavorableMaster.xlsx` — all 29 unfavorable columns fitted (~10 min) |
| 2 | `python alpha_trends.py` · `python kr_trend.py` · `python fx_trend.py` | the three trend workbooks behind Figures 5, 7–10 and Tables 4–5, SI-6 |
| 3 | `python canon_nokr_fit.py` | `fits_canonical_IHOP.xlsx`, `canon_nokr_stats.json` — the k_r necessity test |
| 4 | `python transfer_test.py` · `python weight_robustness.py` | `TransferTest.xlsx`, `WeightRobustness.xlsx` |
| 5 | `python build_table3.py` | `table3_rows.json` and the Table 3 markdown |
| 6 | `cd HYDEQ && python hydeq_fit.py --conv accum` then `python hydeq_export.py --fullset` and `python hydeq_fullset_analysis.py` | the 29-column × 8-structure HYDEQ comparison (this is the long step: 112 fits) and `hydeq_fullset_stats.json` |
| 7 | `python build_figure7.py` … `build_figure10.py`, `driver_fig6.py`, `driver_fig4_si5.py` | the native-Excel figure workbooks |
| 8 | `python check_consistency.py` | re-derives every headline number from the artefact that owns it and greps the tree for superseded values asserted as current |

`Records/` documents each step's method, the decisions behind it, and the numbers it is expected to reproduce.

### Applying the model to other data

This deposit is a reproducer chain for the paper, not a package. The IHOP engine and its data conventions live in unfav_master_fit.py, and every number in the paper comes from running the scripts here as they are. To fit IHOP to other column experiments, write your data into the tidy-CSV format described in Records/data_inventory.md (one row per BTEC or RP point, with column metadata) or adapt the loader at the top of unfav_master_fit.py. Do not re-derive the model from the paper or rewrite the fitting engine. In particular:

The retention profile is the accumulated solid phase at excision (all attached colloids at the end of the 10 PV run). An earlier convention, an injection-window snapshot, is retired and must not be reintroduced; the favorable-condition script favorable_both_models.py still uses it for reasons documented in Records/plateau_rs_decision.md §3b, and is not a template for new fits.

The objective, weights, RP-shape window rule, C₀ handling, plateau tolerance and detection floor are method choices, recorded with their reasons in Records/. Change them only deliberately, and say so in your own record.

Two load-time checks protect this dataset — the tidy CSV must have ≥ 1,200 rows from both source studies, and every RP must have exactly 10 depth points. They exist because both conditions were once silently violated here (Records/CLAUDE.md). For a different dataset they will fail by design; relax them in the loader knowingly rather than working around them.

If you are using an AI assistant to do the adaptation, give it this section and Records/CLAUDE.md before it touches a file, and have it confirm that a refit of two or three of the published columns reproduces the values in Manuscript/FigsExcelsUnfav/UnfavorableMaster.xlsx before and after its changes. A rewritten engine that runs without error is the failure mode to guard against, not a crash.

### Two things to know before running

**`check_consistency.py` reports "8 source artefact(s) missing" on a fresh clone.** This is expected, not a defect. It derives several claims from three JSON files that are *not* shipped — `hydeq_fullset_stats.json`, `canon_nokr_stats.json`, `table3_rows.json` — because they are plumbing between the Python analyses and the document builders, and the workbooks carry the same numbers. They are regenerated by steps 3, 5 and 6 above; once those have run, the checker covers all of its claims.

**Nine scripts read the original source workbook, `Data/DataFromLi&Tong.xlsx`, which is not redistributed** (it is the authors' digitization of the published experiments; the tidy CSV is the licensed extract). These are the favorable-chemistry and early size-series scripts: `favorable_both_models.py`, `favorable_tail_SI.py`, `favorable_tail_clean.py`, `fx_pin_test.py`, `gl_is_free_test.py`, `gl_is_fx.py`, `qz_is_fx.py`, `serial3_quartz_check.py`, `serial3_size_fit.py`. Their outputs ship (`Manuscript/FigsExcelsFavorable/Favorable_data_and_sim.xlsx`, `Tables/Table-SI-4-ParamsFavorable.xlsx`), and the scripts are included so the method is inspectable, but they cannot be re-run from this deposit alone. Every unfavorable-set script reads the shipped CSV and runs as-is.

---

## Model in one paragraph

Four mobile/immobile states in series — core (c) → near-surface wall population (w) → grain-contact crawl (g) → attached (a) — with delivery rate r_s from clean-bed filtration theory, single-interception attachment efficiency α_s, crawl attachment efficiency α_m, focusing fraction f_x (w → g recruitment), and a crawl-to-wall release rate k_r; near-surface velocity v_ns = 0.05 v. Per column, α_s, α_m, f_x and k_r are fitted jointly to the BTEC and RP under a five-block weighted log-residual objective; r_s is pinned to the favorable-chemistry anchor for the same medium, size and velocity. `Records/` and the paper's Methods give the full statement; `Records/identifiability_and_necessity_tests.md` and `weight_robustness.md` record what each parameter is doing and whether the conclusions survive reweighting.

---

## Related code

The physics IHOP draws on — DLVO interaction energies (secondary-minimum depth |U_sec| for k_r) and the Happel sphere-in-cell flow field (single-collector efficiency for r_s) — lives in the **PartiSuite** repository (Fortran). This repository is the Python transport-model layer built on that physics.

---

## License

Code: MIT (see `LICENSE`). The tidy experimental-data extract (`Data/LiTong_experimental_data_tidy.csv`): CC-BY 4.0, with attribution to the original source publications.

## Contact

William P. Johnson, Department of Geology & Geophysics, University of Utah — william.johnson@utah.edu
