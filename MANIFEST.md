# Deposit manifest

Built 2026-09-11 by `Code/build_release.py`.

**This deposit is a curated subset of a larger private research repository.** It contains the code,
data and methods records needed to reproduce the figures, tables and claims of the accompanying
paper. It deliberately omits exploratory routes that were tested and not adopted, model-development
history superseded by the published structure, session-management notes, and manuscript drafts.
Scripts and records named below under "withheld" exist but are not part of this deposit; a reference
to one of them inside an included file is not a broken link.

Selection is recorded in two places inside the deposit: the `release (WRR deposit)` column of
`Manuscript/SI-spreadsheets/CodeInventory.xlsx` (code) and `Records/RELEASE_MANIFEST.md`, which also
gives the reasoning for each call (records).

## Contents

- `Code/` — 44 scripts, the reproducer chain for the paper.
- `Records/` — 12 methods and decision records.
- `Data/` — the tidy experimental dataset, its extractor, and its README. **The experimental data are
  digitized from previously published experiments (Li et al.; Li and Johnson; Tong and Johnson); this
  is a compilation, not a new dataset. Cite the original papers for the measurements.**
- `Manuscript/Figures/` — the figure workbooks. The manuscript figures are native Excel charts, so
  these carry the plotted values.
- `Manuscript/Tables/` — the curated table artefacts, named by table number. These are **extractions**:
  the generating scripts in `Code/` write the workbooks under `Manuscript/FigsExcelsUnfav/` and
  `FigsExcelsFavorable/` (also included), and the critical elements were then lifted into these
  by-table-number files so that re-running a generator cannot disturb a table the paper depends on.
  So the provenance chain for any table is: script → generated workbook → this file. Regenerating a
  workbook may produce small differences from the copy included here; the generated workbooks are
  guideposts for recreating the analysis, whereas these table files are what the paper reports.

## Withheld — code (32 scripts)

- `Serial-1-Intended.py`
- `Serial-1-plot_fits.py`
- `Serial-2-plot_fits.py`
- `Serial-3-plot_fits.py`
- `am_sigma_probe.py`
- `amg_bidir_probe.py`
- `amg_kwc_probe.py`
- `amg_probe.py`
- `amg_release_probe.py`
- `amg_vns_probe.py`
- `build_fits_canonical.js`
- `build_hydeq_fullset_docx.js`
- `build_release.py`
- `build_summary_docx.js`
- `build_workbook.py`
- `build_workbook_d.py`
- `build_workbook_e.py`
- `build_workbook_f.py`
- `delta_fx_probe.py`
- `fx_usec_closure.py`
- `identif_kr.py`
- `mfpt_size.py`
- `overlay_bytag.py`
- `overlay_d_bytag.py`
- `plot_identif_kr.py`
- `quartz_check_fits.py`
- `rs_sigma_probe.py`
- `run_c.py`
- `serial3_favorable_fit.py`
- `serial_model.py`
- `tong_size_fit2.py`
- `vns_free_probe.py`

## Withheld — records (20 files)

- `CLAUDE.md`
- `RESUME_2026-08-29.md`
- `RESUME_2026-08-30.md`
- `RESUME_2026-09-10.md`
- `Serial-1-record.md`
- `Serial-2-record.md`
- `Serial-3-record.md`
- `Serial-Arc-summary.md`
- `alpha_m_distribution.md`
- `amg_crawl_attachment.md`
- `evidence_map.md`
- `figure1_hydeq_template_record.md`
- `interception_history_apriori_alpha_working_record.md`
- `model_doc.md`
- `overview.md`
- `part1_extraction.md`
- `part2_apriori_alpha_machinery.md`
- `rs_distribution.md`
- `two_site_straining_plan.md`
- `vns_free_exploration.md`
