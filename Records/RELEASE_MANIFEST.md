---
title: "Records/ release manifest — what is deposited with the WRR paper and what is not"
subtitle: "Include/exclude calls made 2026-09-08 at W.P.J.'s direction"
---

# Records/ release manifest

**Purpose.** The GitHub repository stays private and complete. The public artifact is a **Zenodo
deposit built by export**, not a curated repository — one-directional, so there is no mirror to keep
in sync and no way for public and private trees to drift (the failure mode `CLAUDE.md` rules 4, 5
and 9 exist to prevent). This file is the manifest for `Records/`; the `Code/` side is a `release`
column in `CodeInventory.xlsx`.

**Who decided.** The include/exclude calls below were made by the assistant at W.P.J.'s explicit
direction (2026-09-08: *"I need you to make the include exclude calls since I'm unfamiliar with the
Record. That's your baby."*). **They are reversible and should be reviewed before the deposit is
minted** — a Zenodo version is immutable once published.

**The test applied.** *Does a reader of the WRR paper need this to understand or reproduce a claim
the paper actually makes?* Not "is it interesting," and not "was it hard work." Exploratory routes
that were tested and not adopted are excluded even where the work was substantial, because the paper
does not rest on them and a deposit is not a lab notebook.

---

## INCLUDE — 11 of 30 files

| file | why it ships |
|---|---|
| `data_inventory.md` | The canonical description of the experimental dataset — conditions, exclusions, detection limits, the downgradient-column exclusions, the AB/E duplication. A reader cannot audit the data without it. |
| `plateau_rs_decision.md` | Justifies two Methods choices the paper asserts: the fixed-r_s treatment and the branch-aware RP-shape window. |
| `identifiability_and_necessity_tests.md` | Defines the two tests (local identifiability vs. necessity) that the paper's parameter arguments use by name. |
| `hydeq_comparison_record.md` | The conventional-model comparator. The paper's structural claim rests on it, including the reconciled experiment counts. |
| `hydeq_hydrus_verification.md` | Independent cross-check of the HYDEQ implementation against HYDRUS-1D. Directly answers the obvious reviewer question of whether the comparator was implemented fairly. |
| `replicate_transfer_test.md` | Methods record for the transfer test — the paper's strongest predictive claim. **See the consent note below.** |
| `weight_robustness.md` | Supports the SI robustness section, and documents that the objective is RP-shape-dominated. |
| `kr_trend_analysis.md` | Supports Figures 9 and 10 (k_r vs size, IS, velocity). |
| `fx_trend_analysis.md` | Supports Figure 8 (f_x closure against secondary-minimum depth). |
| `aplat_plateau_alpha.md` | Defines a_plat, the empirical plateau attachment efficiency used in the trend figures. |
| `favorable_tail_reality.md` | Supports the favorable-fit tail treatment reported in the favorable fits table. |

## EXCLUDE — 19 of 30 files

**Internal process, no scientific content**

- `CLAUDE.md` — standing rules and working protocol, including file-handling incidents. Entirely about how the work is conducted.
- `RESUME_2026-08-29.md`, `RESUME_2026-08-30.md` — session handoff briefs.
- `two_site_straining_plan.md` — a plan and new-chat brief, superseded by the work it planned.
- `evidence_map.md` — maps findings to a conference abstract, not to this paper.
- `figure1_hydeq_template_record.md` — how the native-Excel chart template was built. Production detail.

**Exploratory routes that were tested and NOT adopted.** Excluding these is the call most worth
re-examining, since negative results have real value. The reason to leave them out is that the paper
makes no claim about any of them, so they would arrive without the context needed to read them.

- `alpha_m_distribution.md` — global log-normal spread in α_m; nothing adopted.
- `rs_distribution.md` — spread r_s instead of stickiness; negative.
- `vns_free_exploration.md` — free crawl velocity as a replacement for k_r; nothing adopted.
- `amg_crawl_attachment.md` — decoupling crawl attachment (α_mg ≠ α_mw); 894 lines, nothing adopted.

**Model-development history, superseded by the adopted structure**

- `Serial-1-record.md`, `Serial-2-record.md`, `Serial-3-record.md`, `Serial-Arc-summary.md` — how the
  serial rendering converged. *Judgment call:* `Serial-Arc-summary.md` alone would be defensible to
  include as provenance for why IHOP has the structure it does. Excluded to keep the deposit to
  material the paper cites, but flip it if a reviewer asks how the structure was arrived at.

**Belongs to the broader a-priori-α program, not to this paper**

- `overview.md`, `part1_extraction.md`, `part2_apriori_alpha_machinery.md` — the FIND/CONTACT/ARREST
  machinery and the α-extraction program. This paper fits α; it does not predict α a priori.
- `interception_history_apriori_alpha_working_record.md` — 2,779 lines spanning the whole program.
  Too large, too internal, and mostly about work this paper does not report.

**Superseded by the manuscript itself**

- `model_doc.md` — carries its own `DATED SNAPSHOT` stamp: structure current, every fitted number
  superseded, and its own instruction is *"for the current model description read the manuscript."*
  Depositing a document that says its numbers are wrong would create exactly the confusion the stamp
  was written to prevent.

---

## Before minting the deposit — four things to settle

1. **✅ RESOLVED 2026-09-08 — the coauthor quotation in `replicate_transfer_test.md` is de-identified.**
   The file previously opened with a verbatim, attributed quote. It now reads "Proposed by a coauthor"
   and paraphrases the argument, at W.P.J.'s direction, which removes the consent question. **The
   tradeoff, recorded so it is a choice and not an accident: de-identifying also removes the credit.**
   The transfer test was that coauthor's idea and it is the paper's strongest predictive claim; within
   a coauthored paper, naming him is attribution rather than exposure. Restoring the attribution is a
   one-line change and can be done at any time before the deposit is minted.

2. **The included files are candid, and that is a choice.** Several carry `⚠ RETRACTED` and
   `⚠ Corrected` blocks, dated supersessions, and named attributions of decisions to W.P.J. Read
   generously this is an unusually transparent methods trail; read ungenerously it is a record of
   changing one's mind in public. The blocks are correctly marked and I would not strip them —
   removing them would leave superseded numbers with nothing saying so — but the choice should be
   deliberate rather than discovered after publication.

3. **✅ FIXED 2026-09-08 — the two `check_consistency.py` failures inside the include set were FALSE
   POSITIVES, and both are now clean. No reported number changed.**
   - `kr_trend_analysis.md:15,17` — a two-column *CURRENT vs superseded* comparison table. The flagged
     values (2.13×, +2.5% total) sit in a column literally headed "superseded", but the checker's
     excuse rule is same-line only and the header is a different line. **Fix:** appended
     `(superseded)` inside the right-hand cells, which is the file's own documented convention —
     put the marker on the number's own line.
   - `fx_trend_analysis.md:151` — a leave-one-out sensitivity row, `Tong.B | 0.0036 | 0.53 | −0.26`.
     Here the *checker* was wrong, not the record: 0.0036 is the f_max of the fit with Tong.B removed,
     a live sensitivity result that happens to equal an old headline. **Fix:** anchored the stale
     literal in `check_consistency.py` to an f_max context (`f_?max\D{0,20}0\.0036`), exactly as the
     k_r ratio literals were already anchored for the same collision problem. The cost is that a bare
     stale `0.0036` elsewhere would no longer be caught; that trade is recorded in the script.

   Both were fixed rather than left, because a deposit that ships with a self-check reporting
   failures invites a reader to conclude something is stale when nothing is.

   **Also cleared the same day — the two k_r-constant claims.** `5.58e-5` and `1.87e-5` were listed
   as stale values of the glass and quartz k_r constants, and fired on five shipped files every run.
   They are not stale: both are live in other roles — the multistart seeds, and the per-medium k_r
   **pin** in the favorable fits — and `5.58e-5` is additionally the glass shared constant from the
   size-series joint fit that anchors the Kramers curve in Figure 9, a different fitted object from
   the 29-column trend constant the claim derives. Removed from the stale lists for the reason the
   script already gives for the k_r ratio: a regex that fires on a different quantity trains the
   reader to ignore the checker. `4.46e-5` and `2.09e-5` remain, being genuinely superseded headline
   values with no other role.

   **W.P.J.'s judgment on the substance, recorded because it is the reason not to chase this
   further:** k_r proved an *unnecessary* parameter for this dataset — dropping it costs +1.7% total
   — so analyses of k_r itself are on thin ice regardless. Where these constants appear, k_r is being
   **pinned so that the other parameters can be extracted** (`favorable_both_models.py` pins it
   precisely so that f_x becomes identifiable). The exact pin is therefore not load-bearing for those
   extractions, and reconciling which constant was used where is not worth the effort.

   **`check_consistency.py` now reports all seven claims ok**, with no reported number changed. It
   still notes that **8 source artefacts are missing**, so those claims are not checked at all — a
   pre-existing gap, unrelated to the release work, and worth closing before the deposit if any of
   the missing artefacts back a shipped number.

4. **`data_inventory.md` §4d records the Tong AB / Li E duplication and its provenance** (Li ran the
   experiment; Tong reproduced it in her publications). That is the right place for it and it should
   ship — it is the answer to a reader who notices two identical columns.

---

# Code — 44 of 75 scripts

The per-script calls live in the **`release (WRR deposit)`** column of
`Manuscript/SI-Spreadsheets/CodeInventory.xlsx`, one row per script. The builder is
`Code/build_release.py`; `--dry-run` lists what would ship without writing anything.

**What ships:** the reproducer chain for the paper — the canonical fitter and its QA, the k_r and f_x
analyses, the DLVO/Kramers physics, the α trends, the favorable-column fits, the whole HYDEQ
comparator, every manuscript figure and table builder, the transfer test, the C₀ verification and the
weight-robustness scan. Plus the size/IS-series scripts that produce constants the shipped figures
and records depend on.

**What does not:** the Serial-1/2/3 development line, the exploratory heterogeneity probes (α_m and
r_s spreads, free v_ns), the α_mg decoupling family and its variant workbook builders, and the
document builders for deliverables that are not this paper.

## Two corrections made during the first build — both caught by checking, not by judgment

**1. Six scripts were wrongly excluded and are now in.** `serial3_size_fit.py`,
`serial3_quartz_check.py`, `gl_is_fx.py`, `qz_is_fx.py`, `gl_is_free_test.py` and `dlvo_four.py` were
first classed as corroboration runs. They are not: they generate values that shipped files rely on —
the glass shared k_r constant of 5.58×10⁻⁵ /s that anchors the Kramers curve in Figure 9, the |U_sec|
values behind Figure 8, and results cited by `identifiability_and_necessity_tests.md` and
`fx_trend_analysis.md`, both of which ship. Excluding them would have left shipped records pointing at
provenance a reader could not see.

**2. `identif_kr.py` was wrongly included and is now out — it would have shipped unrunnable.** It
imports eight modules (`li_extract`, `test_A_all_conditions`, `test_H_faithful`, `route_b_gated`,
`route_l_crawlrate`, `route_j_medium_vns`, `route_o_vnsphys`, `consol_rel`) that live in `archive/`,
a directory absent from the inventory entirely. Its outputs are not reported in the manuscript in any
case — no profile-likelihood result appears there — so withholding costs nothing.
`identifiability_canon.py`, which feeds `build_manuscript_tables.js`, does ship and is the
identifiability script the paper actually uses.

**The check is now automated.** `build_release.py` refuses to pass a build in which an included
script imports or `exec`-reads a file that is not in the deposit. Docstring *mentions* of withheld
scripts remain fine — MANIFEST.md's withheld list is what covers those — but an unsatisfiable live
dependency now fails loudly instead of shipping.

## The deposit tells readers it is a subset

`build_release.py` writes a `MANIFEST.md` into the deposit naming all 31 withheld scripts and 19
withheld records, and stating that the deposit is a curated subset of a private repository. A reader
who meets `amg_probe.py` in a docstring can then see that it exists and was deliberately not
included, rather than concluding the deposit is incomplete. That file also carries the note that the
experimental data are **digitized from previously published experiments and are a compilation, not a
new dataset**, directing citation to the original papers.

## If the scope is wrong

The include set is deliberately tight — 11 files, all of them things the paper leans on. Two
defensible expansions, in order of how likely I think they are to be wanted: add
`Serial-Arc-summary.md` for structural provenance, then add the four exploratory records as a
"routes not taken" appendix. Both are additive and neither disturbs the rest.
