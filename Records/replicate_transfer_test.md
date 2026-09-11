# Replicate parameter transfer — does IHOP predict a held-out replicate? (methods record)

**Origin.** Proposed by a coauthor, 2026-09-07: the dataset contains replicate conditions (4, 3, 3, 3,
2 and 2 replicates across six conditions), so fit ONE replicate and predict its siblings using exactly
the same parameter values. The argument: if IHOP's parameters genuinely encode physicochemical
processes, replicates at identical conditions should not each require unrelated estimates.

*(Paraphrased and de-identified 2026-09-08 at W.P.J.'s direction, since this file is in the public
release set — see `RELEASE_MANIFEST.md`. The original verbatim quotation and its attribution are in
the conversation record; restoring them is a one-line change if the coauthor prefers the credit.)*

**Reproducer:** `Code/transfer_test.py` → `Manuscript/FigsExcelsUnfav/TransferTest.xlsx` (three
sheets: Transfer test, Cross-condition null, Reproducibility floor).
**Manuscript text:** `Manuscript/Current Predictive Capability 2.docx` (Tables X, Y, Z, AA).

---

## What the test does

For each of the six replicated study-conditions, every column in turn is the **donor**: its four
fitted parameters (α_s, α_m, f_x, k_r) are applied *unchanged* to each **receiver** sibling and the
model is forward-run against that receiver's own data.

**Nothing is refitted.** Donor parameters are the per-column fits already in
`UnfavorableMaster.xlsx` ('Per-column fits'), and scoring reuses the production objective, so the
test cannot move any published number. Each receiver keeps its **own C₀** (hence its own retention
amplitude logK), its **own RP sampling depths**, and its **own RP-shape scoring window**. r_s stays
at the receiver's favorable anchor, so only the four fitted parameters transfer.

Agreement is reported as **RMS difference in log₁₀ units (dex)**, RP and BTEC separately:
RMS = √(mean((log₁₀ model − log₁₀ data)²)). 0.3 dex ≈ a factor of two in concentration.

## Three comparisons

| | what is compared | model run? | n |
|---|---|---|---|
| **Transfer** (Table Y) | model with a *sibling's* parameters vs this column's data | yes | 28 (directional) |
| **Cross-condition null** (Table AA) | model with a *foreign condition's* parameters vs this column's data | yes | 84 (all foreign donors, same medium) |
| **Reproducibility floor** (Table Z) | one column's *measured* data vs a sibling's *measured* data | no | 14 (symmetric) |

The floor is the benchmark: no parameter set can reproduce a sibling more closely than the siblings
agree with one another.

## Result

| median RMS (dex) | RP | BTEC |
|---|---|---|
| own fit | 0.092 | 0.168 |
| **replicate transfer** | **0.287** | **0.405** |
| **reproducibility floor** | **0.281** (C₀-normalised; 0.480 raw) | **0.386** |
| cross-condition null | 0.551 | 0.750 |

Transfer lands *at* the floor in both curves (0.287 vs 0.281; 0.405 vs 0.386). Foreign parameters
are roughly twice as far off. The fitted parameters therefore carry information specific to the
experimental condition rather than to the individual column, to within the precision with which
these experiments repeat.

## Two things that had to be got right

**C₀ had to be divided out of the floor, but only there.** BTECs are already C/C₀-normalised per
column and the model uses each column's own C₀ in logK, so C₀ is handled inside the fits. It matters
for the pairwise *raw* retention-profile comparison that defines the floor: replicates were run at
genuinely different injection concentrations (C₀ spans up to 0.8 dex, a factor of ~6), retained
numbers scale with injected numbers, and the RP level tracks C₀ almost 1:1 (e.g. Tong glass 0.2 µm:
C₀ offsets +0.06/+0.14/−0.33 dex against RP-level offsets +0.05/+0.28/−0.34 dex). Normalising each
profile by its own C₀ before comparing cuts the floor from 0.480 to 0.281 dex.

⚠ **Corrected 2026-09-07.** An earlier version of this note claimed the RP error bars in Figure 6
and SI-6 were inflated by C₀ and needed fixing. **They were not: `unfav_master_fit.py` already
normalises them** — see `normalize=(expkey=='rp_exp')` in its per-condition sheet writer, which
divides each replicate by its own C₀ and rescales by the group's geometric-mean C₀ before taking the
mean and sd; the sheet header records the C0avg used. Because the rescaling uses the geometric mean,
the plotted **means are unchanged** by the normalisation; only the sd differs. Verified by
`Code/verify_rp_c0_normalisation.py`, which reproduces the master's sd to 5e-5 dex and reports what
the bars would have been unnormalised (median 0.217 dex normalised vs 0.333 dex raw). No figure
change is required.

**Cost ratios were abandoned as the metric.** The first version reported
100·(cost_donor − cost_own)/cost_own. Several own-fit costs are below 2, so the ratio exploded
(median +398%, IQR 67–2928%) while the underlying discrepancy was ~0.2 dex. Percentages are
retained nowhere in the final tables; everything is dex.

## Caveats to keep with the result

- **α_s spread between siblings reaches 722×** (Li quartz 1.1 µm 6 mM). Only the product r_s·α_s is
  identifiable per column (`plateau_rs_decision.md` §3), so this is degeneracy, not physical
  disagreement. The transfer RMS, which holds r_s at the shared anchor, is the fairer statement.
- **Li quartz 1.1 µm 20 mM is the weakest condition:** sibling BTECs differ by 0.6–1.3 dex, far
  beyond what C₀ explains. Its transfers are correspondingly the worst in Table Y.
- **C₀ is known only to ~a factor of two** (Johnson and Pazmino, 2023), i.e. ~0.3 dex — the same size
  as the reproducibility floor. That is the reason no attempt was made to tune C₀ to improve
  agreement; doing so would be fitting within the noise.
- The null holds r_s at the *receiver's* anchor, so it isolates the four fitted parameters. A
  stricter null would carry the donor's r_s as well and would be worse still.

## History

- 2026-09-07: built as donor→sibling transfer, no refitting (the leave-one-out refit variant was
  rejected as it would introduce numbers that could disagree with the published per-column fits).
- 2026-09-07: cost-ratio columns and the single-representative-donor null removed; replaced by RMS
  in dex throughout and a null that uses every foreign donor with the receiver keyed on its full
  (study, medium, column) identity. The earlier null keyed baselines on the column *letter* alone,
  which is unsafe across studies.
