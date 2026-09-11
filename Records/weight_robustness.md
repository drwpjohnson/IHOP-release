---
title: "Objective-weight robustness — do the conclusions survive reweighting?"
subtitle: "Closes the first item on the working record's 'sensitivity to fixed choices' list"
---

# Objective-weight robustness (2026-09-08, W.P.J. + assistant)

**Reproducer:** `Code/weight_robustness.py` → `Manuscript/FigsExcelsUnfav/WeightRobustness.xlsx`
(sheets: Conclusions, Weights, and one `fits <variant>` sheet per variant).
**Closes:** `interception_history_apriori_alpha_working_record.md` open item B-6, "Sensitivity to fixed
choices — objective weights … no systematic scan recorded" (weights only; Pe, logK and r_s source remain open).

---

## 1. Why this was done

The production objective is a five-block weighted log₁₀ residual, W_RP = 6.0, W_SHAPE = 2.5,
W_PLAT = 20.0, W_TAIL = 3.0, W_TSLOPE = 16.0, with a ±0.25 dex plateau dead zone. Those five numbers
were the most visible discretionary choice left in the paper and nothing in the Methods explained
where they came from, so on the page they read as tuned.

The question deliberately asked here is **not** whether the fitted parameters are stationary under
reweighting — they are not, and no objective's are. It is whether **the statements the manuscript
makes** survive. Those were scored as five trend claims plus two fit-quality diagnostics.

## 2. ⚠ The finding that was not expected: the weights badly misrepresent the pull

**The five blocks are not in the same units, so the weight numbers do not rank the blocks.** The
RP-shape residuals are log-*slopes* (d log₁₀S/dx) in dex per metre; every other block is in dex.
On this grid the raw shape residual has a median magnitude of **1.09 dex/m**, fifteen times the
RP-level residual (0.069 dex) and fifty times the tail-slope residual (0.022 dex).

Realised cost at the production fits, summed over all 29 unfavorable columns:

| block | w | n | nominal w²·n | nominal % | realised SSQ | **realised %** | raw \|r\| median |
|---|---|---|---|---|---|---|---|
| RP level | 6.0 | 290 | 10440 | 32.6% | 117.6 | 7.6% | 0.069 dex |
| **RP shape** | **2.5** | 58 | 362 | **1.1%** | **1282.7** | **83.2%** | **1.092 dex/m** |
| plateau | 20.0 | 29 | 11600 | 36.2% | 29.4 | 1.9% | 0.000 dex |
| tail level | 3.0 | 246 | 2214 | 6.9% | 100.9 | 6.5% | 0.103 dex |
| tail slope | 16.0 | 29 | 7424 | 23.2% | 11.5 | 0.7% | 0.022 dex |
| **total** | | 652 | 32040 | 100% | 1542.0 | 100% | |

**The block with the smallest weight carries 83% of the cost; the block with the largest weight
carries 1.9%.** The plateau block is inactive on **26 of 29 columns** because its ±0.25 dex dead
zone is not exceeded — its weight of 20 only ever bites on Tong.H, Tong.R and Tong.U. Tail slope,
at weight 16, contributes 0.7%.

This is **not new information hidden in the code** — the master's own 'Fit quality' sheet already
breaks RP level out from RP shape per condition and shows the same thing (Tong.AQ: shape 41.15 vs
level 2.40). It had simply never been totalled. The reconstruction agrees with those stored costs
(Li.O 12.75 vs 12.76; Li.R 5.65 vs 5.58).

**Consequence for how the weights are described.** They are *not* a block-size normalisation, which
was the working hypothesis going in. The nominal budget w²·n is roughly balanced across RP level
(33%), plateau (36%) and tail slope (23%) — so the numbers look deliberate — but the unit mismatch
means the realised objective is essentially "fit the two RP log-slopes, subject to loose constraints
from everything else." The Methods should say what the objective actually optimises rather than
listing five weights and leaving the reader to assume they rank the blocks.

## 3. The variants

`shape scale` multiplies the RP-shape residual; L = 0.2 m converts dex/m → dex.

| variant | W_RP | W_SHAPE | W_PLAT | W_TAIL | W_TSLOPE | shape scale | why |
|---|---|---|---|---|---|---|---|
| `prod` | 6.0 | 2.50 | 20.0 | 3.0 | 16.0 | 1.0 | control |
| `flat` | 1.0 | 1.00 | 1.0 | 1.0 | 1.0 | 1.0 | the extreme |
| `shape_half` | 6.0 | 1.25 | 20.0 | 3.0 | 16.0 | 1.0 | the dominant block, down |
| `shape_x2` | 6.0 | 5.00 | 20.0 | 3.0 | 16.0 | 1.0 | the dominant block, up |
| `unitfix` | 6.0 | 2.50 | 20.0 | 3.0 | 16.0 | **0.2** | shape residual in dex, not dex/m |
| `plat_x2` | 6.0 | 2.50 | 40.0 | 3.0 | 16.0 | 1.0 | the dead-zone block |
| `tslope_half` | 6.0 | 2.50 | 20.0 | 3.0 | 8.0 | 1.0 | |

**Baseline verified.** `prod` re-fitted through this script reproduces `UnfavorableMaster.xlsx`
'Per-column fits' to a **median 0.0003 dex and a maximum 0.033 dex** across all four parameters and
29 columns — within the sheet's own display rounding (4 dp on α, 3 dp on k_r). Differences in the
other variants are therefore the weights', not the script's.

## 4. Result — every conclusion survives, including flat weights

Spearman ρ, all 29 unfavorable columns:

| claim | prod | flat | shape_half | shape_x2 | unitfix | plat_x2 | tslope_half |
|---|---|---|---|---|---|---|---|
| α_s vs IS (glass) | +0.70 | +0.70 | +0.70 | +0.70 | +0.70 | +0.70 | +0.70 |
| α_s vs IS (quartz) | +0.86 | +0.86 | +0.89 | +0.86 | +0.89 | +0.86 | +0.86 |
| k_r vs size | −0.15 | −0.28 | −0.15 | −0.04 | −0.19 | −0.11 | −0.17 |
| k_r vs velocity | +0.65 | +0.60 | +0.63 | +0.66 | +0.64 | +0.65 | +0.66 |
| f_x vs \|U_sec\| | +0.42 | +0.44 | +0.41 | +0.38 | +0.43 | +0.42 | +0.41 |
| median RP RMS (dex) | 0.092 | 0.106 | 0.088 | 0.098 | **0.081** | 0.092 | 0.092 |
| median BTEC RMS (dex) | 0.180 | 0.183 | 0.167 | 0.202 | **0.163** | 0.180 | 0.175 |
| RP peak within 1 cm | 22/29 | 23/29 | 22/29 | 22/29 | 21/29 | 22/29 | 22/29 |

**No sign flips anywhere.** α_s(IS) is essentially invariant. The two "no strong dependence" claims
(k_r vs size) stay small and non-significant under every variant, p = 0.14–0.82. The f_x closure
holds at ρ ≈ 0.4 throughout, dipping to p = 0.06 only under `shape_x2`. Fit quality moves by at most
0.014 dex in RP and 0.022 dex in BTEC.

**Parameter movement, |variant − prod| in dex:**

| variant | α_s med / max | α_m med / max | f_x med / max | k_r med / max |
|---|---|---|---|---|
| flat | 0.008 / 0.342 | 0.019 / 0.605 | 0.039 / 0.691 | 0.180 / 1.523 |
| unitfix | 0.022 / 0.269 | 0.045 / 0.280 | 0.016 / 0.516 | 0.017 / 1.361 |
| shape_half | 0.007 / 0.104 | 0.019 / 0.240 | 0.010 / 0.347 | 0.012 / 1.117 |
| shape_x2 | 0.004 / 0.298 | 0.015 / 0.494 | 0.012 / 1.533 | 0.038 / 1.394 |
| plat_x2 | 0.000 / 0.038 | 0.000 / 0.069 | 0.000 / 0.715 | 0.000 / 1.350 |
| tslope_half | 0.000 / 0.023 | 0.000 / 0.028 | 0.023 / 0.220 | 0.114 / 1.350 |

**α_s is the stable parameter** — within 0.1 dex of production on 27–29 of 29 columns under every
variant, including flat. That is the reassuring result, because α_s(IS) is the physical claim.

**k_r is the loose one**, moving up to 1.5 dex on individual columns. This is the *already-documented*
{f_x, v_ns, k_r} degeneracy, not new instability: the largest excursions are Tong.U (k_r rails at the
1e-6 lower bound), Li.AB, Tong.H, Li.AE and Tong.O. Only 2 of 29 columns sit at a k_r bound in
production. The *trends* in k_r are nonetheless stable, because they are driven by the columns where
k_r is identified, not by the railing ones.

## 5. What this does and does not license

**Licensed.** "The conclusions are insensitive to the objective weights, including under equal
weighting" — with this table as the evidence. One paragraph plus the table belongs in the SI.

**Not licensed — read before quoting.**

- **The transfer test was not re-run per variant.** Transfer RMS is scored under the production
  objective and the headline result (transfer sitting at the reproducibility floor, 0.287 vs 0.281
  dex RP) is **conditional on the production weights**. That conditionality should be stated in the
  manuscript rather than chased; re-deriving it per variant multiplies the work without changing the
  robustness question. Deliberate scope decision, not an oversight.
- **This is a one-at-a-time scan, not a joint one.** Six variants around one point, not a 5-D
  exploration. It answers "does a reviewer's obvious perturbation break anything," not "what is the
  global weight-space geometry."
- **`unitfix` is not a proposal to change the objective.** It is a diagnostic showing the conclusions
  survive putting the shape block in the same units as the others. It also happens to give the best
  fit quality on both curves (RP 0.081, BTEC 0.163 dex) — worth knowing, but re-fitting the whole
  paper to gain 0.01 dex is not worth the disruption, and the production fits are the published ones.
- **k_r vs velocity is +0.65 and significant under every variant.** That is not a robustness failure,
  but it is a *positive* dependence and deserves a note on study balance.

  ⚠ **Corrected 2026-09-08, same day.** An earlier version of this bullet said velocity is fully
  confounded with study — "all 8 m/day unfavorable columns are Tong's, all 4 m/day are Li's." **The
  second half is false.** The actual split of the 29 unfavorable columns is **4 m/day: Li 11, Tong 8;
  8 m/day: Tong 10.** Only the 8 m/day end is single-study. Tong therefore spans **both** velocities,
  so a within-study velocity contrast exists (Tong 8 columns at 4 m/day vs 10 at 8 m/day) and the
  velocity trend is **not** inseparable from a between-study offset, as was claimed. What is true is
  narrower: **Li contributes no 8 m/day unfavorable data**, so the velocity range is not balanced
  across studies, and any velocity claim should be checked within Tong alone before being asserted
  over the pooled set. Unrelated to weights either way.

## 6. Files

- `Code/weight_robustness.py` — the scan. `--variants all` takes ~8 min; run in batches with `--json`
  and combine with `--merge` (no refitting) if a tool call cap gets in the way.
- `Manuscript/FigsExcelsUnfav/WeightRobustness.xlsx` — Conclusions, Weights, and per-variant fits.
- The §2 pull budget was computed by a scratch script that reconstructs the residual vector at the
  master's fitted parameters; its numbers are reproduced in the table above and it was not kept, since
  the same breakdown is already in the master's 'Fit quality' sheet per condition.

## 7. Two defects found in the manuscript's own Objective-function section

Found while drafting the replacement text (`Manuscript/Objective_function_section.docx`, 2026-09-08,
a NEW file — the manuscript itself was not touched). Recorded here so they are not lost if that draft
is not merged as written.

1. **The pull arithmetic uses the wrong n for RP shape.** The current paragraph gives the block pulls
   as "plateau (400), RP level (360), RP shape (62.5), tail level (72) and tail slope (256)". 62.5 is
   2.5²×10, i.e. it counts the ten RP *points*; the block has **two** slope terms, as the manuscript's
   own Table 1 states, so the value is 2.5²×2 = **12.5**. The RP-side total is therefore **372.5**, not
   422.5, against BTEC's 728. The stated conclusion — the two sides within a factor of two — survives,
   but only just, at **1.95×**.
2. **"At least two starts" should be three.** `unfav_master_fit.py` runs the bounded solver from three
   seeds and retains the lowest-cost solution.

Neither affects any fitted number.

## 8. Standing issue noticed while doing this

`UnfavorableMaster.xlsx` still carries the **`k_r (/PV)`** header and a sheet named **'Fit quality
(Table 3)'**, so it predates the k_r → /s export change and the de-referencing of manuscript table
numbers from code. `unfav_master_fit.py` has not been re-run since those edits. `weight_robustness.py`
reads either header, so it is unaffected — but `build_table3.py` expects a sheet named 'Fit quality'
and will not find it until the master is regenerated.
