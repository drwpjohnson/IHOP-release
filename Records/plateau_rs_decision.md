# Plateau rule, r_s treatment, and the RP‑inlet limitation (decision record)

Settled decisions for the unfavorable Serial‑3 fits (`Code/unfav_master_fit.py`), 2026‑08. Written so we don't relitigate.

## 1. Plateau term: mean‑log target, not a dead‑zone

**Change:** the BTEC plateau term was a *dead‑zone* (penalize only if the model plateau left the [min,max] band of the 1.2–3.5 PV points). It's now a **mean‑log target**: match the model's mean log₁₀(C/C₀) over **1.2–4 PV** to the data's mean, with a **±0.25 dex tolerance** (no penalty inside ±0.25; `W_PLAT=20`).

**Why:** the dead‑zone let the plateau *height* float anywhere in the band. For declining/scattered breakthroughs (e.g. Tong quartz 0.5/8/50 = R) an early transient point inflated the band ceiling, so the model sat ~1 log too high. The mean‑log target pins the height. The ±0.25 tolerance was added because the pure mean over‑fit the already‑close columns and blew up f_x/k_r via the f_x↔k_r degeneracy (e.g. Li quartz 1.1/4/20 → f_x 1.0, k_r 12/PV). With the tolerance: flat columns unchanged, the declining ones pulled to their mean, no blow‑ups.

## 2. C0 correction for R and O (quartz 0.5 µm, 8 m/d, 50 mM)

R's recorded `Co = 3.36E5` is the **same bad placeholder** already flagged as ~17× low for its favorable twin O (which had no C0 and was set to the RP‑implied value). R and O are the **same run** (same colloid stock; differ only in pH 6.75 vs 2), so they share C0. Both set to **8.2×10⁶** (R's own RP‑implied value; joint R+O lowest cost; O's earlier 5.762×10⁶ raised to match). Applied via `C0_OVERRIDE` in `Data/extract_tidy_data.py` (override now takes precedence over the recorded cell) and `favorable_both_models.py`. Downstream: O's favorable r_s is **56.7** at the new C0 — **essentially unchanged from 56.9** (r_s is set by the RP *slope*, which is C0‑independent; the level shift is absorbed by α_s/f_x). So the quartz‑0.5/8 anchor `FAVFIT[('quartz',0.5,8.0)]` = 56.7 ≈ its old value; the C0 fix's real effect is on the RP *level* fits (R's cost 280 → ~28), not on r_s.

## 3. r_s stays FIXED — the ±0.25 dex band was explored and REJECTED

A ±0.25 dex r_s band (factor ~1.8, inside the CFT correlation spread) was tested to fix two things: (a) B/U (Tong quartz 0.5/4/20 and Tong glass 0.5/4/50), where fixed r_s left the plateau low and the RP high; and (b) the steep glass RP inlets. **Rejected because:**

- It dragged **glass BTEC plateaus systematically low** (r_s rose ~+0.25 to chase the RP inlet, dropping the plateau within the tolerance so it wasn't corrected).
- It **reopened the quartz r_s↔IS degeneracy**: r_s slid up with IS (Li quartz 1.1/4: 3 mM→36, 6 mM→73, 20 mM→91), α_s softened — exactly what fixing r_s was meant to prevent.
- Diagnostic: for quartz, **r_s is essentially unidentified** — the fit cost is flat across r_s = 25–110 /m (2.81–2.94) with α_s trading off to hold the plateau. So a band adds a degenerate knob the optimizer misuses, and fixing r_s costs ~nothing.

**Why the *original* 4‑condition Serial‑3 fit looked better on quartz:** it used **free r_s (k_f)**, which slid with IS (Qtz 20 mM k_f = 70.5, Qtz 6 mM = 33.3 — a 2× swing). That "better fit" was purchased by r_s absorbing the IS trend — the very behavior we removed for chemistry‑independence. Fixed r_s (grounded in CFT/favorable) is the intentional choice; **clean chemistry‑independence > fit quality** (W.P.J.).

## 3b. The r_s ↔ k_r LOOP — r_s is not strictly "independent" (W.P.J., 2026‑08‑25)

**Raised by W.P.J.:** *"Well, it's circular, right? If we re‑run favorable, we'll get slight changes in r_s. So then we'll need to re‑run unfavorable."* Correct, and it should be stated wherever r_s is described.

**The loop.** `unfav_master_fit.py` pins r_s to `FAVFIT`, commented in the code as *"fitted‑favorable r_s (Table 5)"*. Table 5 is `favorable_both_models.py` **Model 2**, whose header states *"k_r is the ONLY pinned kinetic parameter; pinning it breaks the f_x↔k_r degeneracy so f_x can be free."* That pinned k_r is the per‑medium constant from `kr_trend.py` — i.e. from the **unfavorable** set. So:

> unfavorable fits → per‑medium k_r → favorable Model 2 → r_s → `FAVFIT` → pinned in unfavorable fits

It is a fixed‑point iteration that has been executed **once, not to convergence.**

**Why one pass is enough — two independent damping mechanisms.**

1. **Different features of different curves.** The `FAVFIT` line already notes *"r_s set by RP slope, C0‑independent."* r_s is fixed by the retention‑profile **slope**; k_r acts on the elution **tail** (full‑set §8: removing k_r changes tail level +6.88 and tail slope +1.92 while the RP blocks *improve*). A shift in the pinned k_r has little purchase on the slope that sets r_s.
2. **The identifiable combination absorbs it.** Only the product **r_s·α_s** is identifiable (§3). Any residual shift in the pinned r_s therefore propagates into α_s, not into cost, branch or peak depth — the quantities every claim rests on. The degeneracy that motivated pinning r_s damps the loop.

**Magnitude of the current mismatch.** The 2026‑08‑25 accum refit plus the corrected two‑sided identifiability filter moved the per‑medium k_r constants from 4.46e‑5 → **3.75e‑5** (glass) and 2.09e‑5 → **1.82e‑5** (quartz), ≈0.07 dex. The favorable fits in Table 5 are therefore **pinned to superseded constants and are, strictly, stale.** By the two mechanisms above the propagated effect on r_s is expected to be far smaller than 0.07 dex, and its effect on α_s smaller still in anything that matters. **Decision (W.P.J.): not worth re‑running the loop.** Not iterating is the right call; not *recording* it would not be.

### The favorable fits are on the RETIRED snapshot convention — MEASURED, and it does not matter (2026‑08‑26)

**Raised 2026‑08‑25** while mirroring `favorable_both_models.py`: that script still builds its retention profile as the **eq (4) end‑of‑injection rate snapshot** (`Yst` in `Eng.run`; each per‑column sheet says so at row 10), the convention retired as *invalid* for `unfav_master_fit.py` the day before. **W.P.J. confirmed 2026‑08‑26 that all Li/Tong columns were excised after 10 PV** — *"one cannot physically run 7 PV after excising the column"* — so there is no protocol difference to hide behind: the same objection applies to the favorable columns. Since Table 5 → r_s → `FAVFIT` → every unfavorable α, this had to be measured rather than argued, and the "not worth re‑running" decision above was taken about the k_r constants (≈0.07 dex), not about the convention.

**Test.** `Code/fav_convention_check.py` → `fav_convention_check.json`. Every favorable column refitted **twice**, once per convention, everything else held identical to Model 2 (k_r pinned at the values Table 5 used, r_s free ±0.6 dex of the plateau seed, α_s/α_m/f_x free, same weights, starts, bounds, `max_nfev`). Paired within column, so nothing but the convention differs. **Control:** the snapshot pass reproduces the delivered Table 5 exactly on Tong L 47.5 / CS 15.2 / O 56.7 / AB 30.2 and quartz Li B 120.6 / E 62.3 / I 68.9.

**Result — the convention does not move the favorable fits.**

| column | r_s snap | r_s acc | Δ dex | Δ dex on r_s·α_s |
|---|---|---|---|---|
| gl‑Tong‑L (0.5 µm, 4 m/d) | 47.5 | 46.0 | −0.014 | −0.007 |
| gl‑Tong‑AB (1.1, 4) | 30.2 | 30.1 | −0.002 | −0.001 |
| gl‑Tong‑CS (2.0, 8) | 15.2 | 15.2 | +0.000 | +0.000 |
| qu‑Tong‑O (0.5, 8) | 56.7 | 55.0 | −0.013 | −0.008 |
| qu‑Li‑B (1.1, 2) | 120.6 | 119.2 | −0.005 | −0.005 |
| qu‑Li‑E (1.1, 4) | 62.3 | 61.8 | −0.004 | −0.003 |
| **qu‑Li‑I (1.1, 8)** | **68.9** | **42.7** | **−0.208** | **−0.040** |

Nine of ten columns move r_s by **≤0.014 dex (≤3%)**, median 0.004 dex, at cost unchanged to two decimals, with **no r_s on its ±0.6 dex bound** under either convention. RP RMS slightly *improves* under accum on six of them.

**The one apparent exception is not a convention effect.** On quartz Li I, `--ridge qu-Li-I` pins r_s and refits the other three: r_s can be placed anywhere from **42.7 to 68.9 — 0.21 dex — for ≤0.01% cost, under *both* conventions**, with α_s sliding 0.88 → 0.60 to compensate exactly. r_s is simply **not identifiable on that column**; the apparent move is the optimiser wandering along the r_s·α_s ridge of §3, not the convention relocating anything. Li I's snapshot α_s of 0.598 was already the outlier against 0.996 (Li B) and 0.995 (Li E). Across all ten columns the identifiable product r_s·α_s moves at most **0.040 dex**, median 0.003.

**DECISION (W.P.J., 2026‑08‑26): `FAVFIT` stands as it is; nothing downstream is re‑run.** Keeping quartz(1.1, 8.0) = 68.9 costs 0.01% under accum. The favorable fits are *nominally* on a retired convention and that should be stated, but it is a labelling matter, not a numerical one.

**Why the favorable set is insensitive where the unfavorable set was not (W.P.J.).** Under favorable chemistry the **multiple‑intercepting population is negligible**, so almost nothing is left in a mobile state to redistribute during the 7 PV of elution the snapshot ignores; the extra pore volumes of extended tailing are therefore not a problem here. The unfavorable set, where that population carries the interior peak, is the case the convention actually mattered for — and it was corrected there. That also makes explicit what the convention change *is*: not a numerical detail but a statement about which population is still moving after injection stops.

**Manuscript wording.** This is now a strength rather than a gap — the sensitivity was tested, not assumed. One sentence suffices: the favorable fits were checked under both conventions and r_s moved by less than 3% on every column where it is identifiable.

**⚠ A separate defect turned up in the same exercise, NOT fixed.** In `Data/LiTong_experimental_data_tidy.csv`, `Microspheres Glass Beads Li` col **E** carries **byte‑identical** BTEC and RP to `Microspheres Glass Beads Tong` col **AB**, though the two are labelled as different experiments (0.98 µm / 10 mM vs 1.0 µm / 50 mM). Table 5 has them at 28.8 and 30.2 — different, as they should be — so **the workbook is right and the CSV extraction is wrong**. It is the **only** duplicated curve block in the file and **no unfavorable column is affected**, so `unfav_master_fit.py` is clean. Glass Beads Li **B** also misses Table 5 by 0.065 dex (49.9 vs 57.9) and Li **H** by 0.003 dex; all three GB‑Li columns miss while every other column lands exactly, which points at that block rather than at coincidence — but the cause is **not established** (B's cost surface is not smooth, so a local optimum is also possible). Chase it in `data_inventory`, not here.

**⚠ CONSEQUENCE FOR WORDING — the one thing that does need care.** IHOP's r_s must **not** be described as coming from *independent* favorable‑condition experiments. It does not: favorable Model 2 consumed a k_r constant derived from the unfavorable set. Accurate phrasing:

> r_s is taken from favorable‑condition fits in which k_r was pinned to the unfavorable per‑medium constant — a weak coupling, since r_s is set by the retention‑profile slope and k_r by the elution tail.

The word "independent" appears in the qualifications of `HydeqComparisonFullSet.docx` and `HydeqComparisonCanonical.docx`. **W.P.J. has directed that those Word files not be updated** — the manuscript is the active document and will be reviewed separately. Fix it there.

**If a number is ever wanted instead of this argument:** refit two favorable columns with k_r at the old and new constants and read off the r_s shift directly. Minutes, not the full cascade.

## 4. RP inlets: a single‑population limitation, not a weighting problem

The first 1–2 RP points are structurally out of reach:

- **Glass (multiexponential):** the retention profile can't decline faster than ≈ −r_s/ln10; the glass inlets demand a near‑inlet removal (~48–63/m) *above* the fixed r_s (30–49/m) — impossible (would need α_eff > 1). This is **hyperexponential deposition** = deposition‑rate heterogeneity.
- **Quartz (peaked):** the crawl can build a *gentle* downstream peak, but not the sharp observed one.

An inlet‑emphasis objective (first‑3 points ×2.5 + an initial‑slope term) was prototyped: it sharpened the quartz peaks slightly and did nothing for glass (structural). Gains were cosmetic — **not adopted.** The homogeneous Serial‑3 captures the RP **level, bulk decline, full BTEC, the k_r/f_x trends, and the RP‑type classification** (branch plane); the inlet mismatch is reported as the single‑population/heterogeneity signature. A distributed‑α (2‑population) extension would fit the inlets but is a new model with new identifiability — **future work / SI sensitivity, not the main result.**

## 5. The eq‑(4) RP convention is VALIDATED against the physically accumulated profile (2026‑08‑24)

*Found while building the HYDEQ conventional‑model comparator (`Code/HYDEQ/`, `Records/hydeq_comparison_record.md`); W.P.J. raised the elution point that produced it. This is a corroboration, not a change — nothing here supersedes §1–§4.*

**The question.** Johnson 2018 eq (4), `S(x) = V·t₀·θ·C₀·k_f·exp(−k_f·x/v)`, builds the retention profile by multiplying an **end‑of‑injection deposition rate** by the **full injection duration**. But the column is excised after the **complete 10 PV** (2.98 PV injection + 7 PV elution, §0), and deposition does not stop when injection does. So is eq (4) the right target for the model to fit?

**Two errors, opposite signs, and they nearly cancel.**
- Eq (4) **over‑pays** at the outlet: it applies the steady end‑of‑injection rate over the whole injection, but the outlet deposited nothing until the front arrived (~1 PV in).
- Eq (4) **under‑pays** overall: **10–15 % of the final retained mass is deposited during the 7 PV elution** [COMPUTED, Serial‑3 at the model_doc Table 1A/1B parameters: 12.75 / 9.99 / 12.28 / 14.65 % for GB20 / GB6 / Qtz20 / Qtz6], biased downstream because the crawl g at v_ns = 0.05·v needs ~20 PV to cross the column and is only ~15 % through at end of injection. The quartz RP maximum moves **deeper by ~0.2 cm** (Qtz20 3.22→3.44 cm; Qtz6 4.11→4.33 cm).

**Result — eq (4) vs accumulate‑to‑excision, on Serial‑3's own parameters** [COMPUTED, `Code/HYDEQ/hydeq_verify.py`]. Both the level offset and the tilt are reported because **logK is FIXED and neither is absorbed**:

| condition | mean level offset (log₁₀) | tilt across column (log₁₀) | Serial‑3 RP RMS |
|---|---|---|---|
| glass 20 mM | +0.0038 | −0.0094 | 0.094 |
| glass 6 mM | +0.0064 | −0.0103 | 0.051 |
| quartz 20 mM | +0.0015 | +0.0217 | 0.035 |
| quartz 6 mM | −0.0066 | +0.0390 | 0.098 |

**Level offsets ≤ 0.007 log; tilts ≤ 0.039 log — inside the residuals already being fitted.** Eq (4) effectively pre‑books the elution deposition. ⇒ **the eq‑(4) convention stands, and the published Serial‑3 numbers do not require correction.**

**⚠ Do NOT accumulate only to the end of injection.** That third option — which looks more physical than eq (4) and is not — is the **worst** of the three: tilt **−0.170 to −0.179 log** against accumulate‑to‑excision, i.e. 2–5× the RP residuals. It captures the front‑arrival error without the compensating elution deposition. Recorded so it is not re‑proposed.

**The one place it is not negligible:** quartz 6 mM, tilt +0.039 vs its own RP RMS 0.098 — about 40 %, systematic rather than random. Enough to nudge fitted parameters, not enough to move a conclusion.

**Where it DOES matter: models with detachment or blocking.** The cancellation depends on deposition being steady, which Serial‑3 has (no detachment, no blocking) and the conventional structures do not. For a blocking model the end‑of‑injection rate is the *lowest* of the run, so eq (4) understates its retention; for a detachment model eq (4) ignores elution loss entirely, so it overstates what remains. Consequence for the HYDEQ comparison: the conventional structures are scored under **accumulate‑to‑excision**, because eq (4) is not self‑consistent for them and using it would flatter them. Serial‑3 was refit under the same convention for uniformity — costs moved by a few percent and RP RMS was unchanged to 3 decimals (`hydeq_results.json`).

**A new structural constraint on detachment, from the same observation.** Over 7 PV of elution a reversible site keeps losing retained mass [COMPUTED, `hydeq_engine.py` M2_2site]: retained(10 PV)/retained(3 PV) = 1.09 at k_d1 = 1e‑6 /s, 1.05 at 1e‑5, **0.95 at 3e‑5, 0.55 at 1e‑4**. Building a multi‑PV shelf by detachment needs a half‑life of a few PV — precisely where the RP starts hemorrhaging. With the amplitude FIXED by C₀ the model cannot rescale out of it. **The shelf and the RP pull k_d1 in opposite directions** — the same shape of conflict as blocking‑vs‑plateau.

## 6. The RP‑shape inlet window must be BRANCH‑AWARE (adopted 2026‑08‑24, W.P.J.)

*Found while investigating why Serial‑3 returns a nonmonotonic RP for quartz 1.1 µm / 4 m·day / 6 mM (column V) against a measured interior maximum at 3 cm. Reproducer: `Code/HYDEQ/hydeq_shape_window.py`.*

### The general rule (W.P.J.)

> **The inlet window of the RP shape term must focus on where the change is most dramatic.**

The "inlet **half**" split is arbitrary and only happens to satisfy that rule on a non-peaking profile. **n = 4 is the value for THIS dataset and must be re‑derived for any other** — it depends on the RP point count and spacing (here 10 points at 2 cm over a 0.2 m column, so the first 4 points span x = 1–7 cm) and on where the feature actually sits. ⚠ **Do not carry n = 4 to a dataset with different data density.**

### What was wrong

`model_doc` §5 scores the **inlet‑half and outlet‑half** RP log‑slopes (W_SHAPE = 2.5). On this grid the inlet half spans **x = 1–11 cm**. Where the data peak at 3–7 cm that window **straddles the peak and averages the rise against the fall**, so a model that correctly reproduces the peak is penalised. Column V stays nonmonotonic under **every** r_s from 30 to 90 /m and under both anchors [COMPUTED] — and flips to peaked the moment the shape term is switched off. Putting the peak in *improves* the point‑wise RP RMS (0.096 → 0.088 in the margin scan) while the half‑slope term charges ~5× for it, essentially all of the penalty landing in that one block (RP shape 0.25 → 13.09; RP level, tail level and tail slope all flat or improving).

### The adopted rule — TWO separate jobs, two different point counts

**(a) CLASSIFY the branch from the FIRST TWO measured points** (W.P.J., 2026‑08‑24). If point 2 > point 1 the profile is peaked; if point 2 < point 1 it is multiexponential. This is Al‑Zghoul Eqn 15's inlet‑slope criterion applied to the **data** rather than to fitted α's, and it is local by construction. It agrees with an `argmax` over all 10 points on **every unfavorable column** [COMPUTED], including the marginal quartz 20 mM (S) at +0.038 log. Use it in preference to `argmax`, which is more fragile.

**(b) SCORE with the branch‑appropriate window:** half‑split if classified non-peaking, **first 4 points** if classified peaked.

**⚠ Do NOT use the two classification points as the scoring window.** Tested [COMPUTED] — it chases a single point‑pair difference, so it produces peaks but overshoots them and degrades the point‑wise fit on every column:

| column | measured peak | half | n = 4 | n = 2 |
|---|---|---|---|---|
| glass 20 mM | — | 0.052 | 0.054 | 0.064 |
| glass 6 mM | — | 0.051 | 0.065 | **0.113** |
| quartz 20 mM (S) | 3.0 cm | 0.040, 1.4 cm | 0.041, 1.7 cm | 0.047, 2.3 cm |
| quartz 6 mM (V) | 3.0 cm | 0.099, nonmonotonic | 0.101, **2.3 cm** | 0.130, 3.9 cm |
| quartz 3 mM (AE) | 5.0 cm | 0.189, 4.8 cm | **0.172, 5.0 cm** | 0.178, **6.8 cm** |
| quartz 3 mM (AH) | 7.0 cm | 0.109, 8.8 cm | 0.124, 9.0 cm | 0.147, 9.2 cm |

Classification needs two points because it is a **sign** test; scoring needs four because it is a **magnitude** regression. The branch is read from the **measurement, not the model**, so the rule does not presuppose the answer.

### Evidence (model_doc anchor: r_s = 22.9 glass / 41.5 quartz; RP RMS, peak cm)

| column | measured peak | half‑split (current) | branch‑aware |
|---|---|---|---|
| glass 20 mM | none | 0.052, multiexponential | **unchanged by construction** |
| glass 6 mM | none | 0.051, multiexponential | **unchanged by construction** |
| quartz 20 mM (S) | 3.0 cm | 0.040, 1.4 cm | 0.041, **1.7 cm** |
| quartz 6 mM (V) | 3.0 cm | 0.099, **nonmonotonic** | 0.101, **2.3 cm** |
| quartz 3 mM (AE) | 5.0 cm | 0.189, 4.8 cm | **0.172, 5.0 cm** |
| quartz 3 mM (AH) | 7.0 cm | 0.109, 8.8 cm | 0.124, 9.0 cm |

**⚠ Why not simply shorten the window everywhere.** A single window cannot serve both branches: at n = 4 glass 6 mM degrades from RMS 0.051 to **0.065**, and at n = 3 to **0.081**. That column's multiexponential curvature is exactly what the half‑split measures well. The window must therefore depend on the branch.

**⚠ Quartz 3 mM (AH) is an exception and is NOT fixed by this.** It already overshot (8.8 cm vs 7.0) and moves to 9.0. Its model plateau sits below the measured points from 5–15 cm — the model cannot produce a profile that flat‑topped. That is a separate structural miss; the window change neither causes nor fixes it.

### Circularity — stated, not hidden

Scoring a shortened inlet window makes the peak agreement partly by construction, in **exactly the way §6z‑K already accepts for the slope term**: *"the slope match is partly by construction — the slope term is in the objective; the non‑circular evidence is the low pointwise logK‑anchored RP‑RMS."* The non‑circular evidence here is the same point‑wise RP RMS, reported above — and on AE it **improves** (0.189 → 0.172).

### Consequences — EXECUTED 2026‑08‑24

*(This section previously read "not yet executed — pending W.P.J.'s go‑ahead." The go‑ahead was given and the full refit was run. The four‑column table above remains as the evidence that motivated the change; the outcome over all 19 conditions is below.)*

**The refit is contained. 17 of 19 conditions are bit‑identical.** Only the two Li quartz 1.1 µm conditions moved:

| condition | α_single | α_mult |
|---|---|---|
| Li quartz 1.1 µm 4 m/d, 3 mM | unchanged | 0.0690 → **0.0530** |
| Li quartz 1.1 µm 4 m/d, 6 mM | 0.0596 → **0.0399** | 0.1360 → **0.1180** |

Five columns are scored on the 4‑point inlet window (Li.AE, Li.AH, Li.V, Li.Y, Li.AB); the other 24 keep the half‑split. Peak depth improved on all five reclassified columns. **a_plat did not move** (largest shift 0.0001), as it must not — it is a pure data quantity, and that it stayed put is a check on the refit rather than a coincidence.

**Propagation completed the same day**, each with its reproducer brought in line with this objective. *(The numbers in this list are as of 2026‑08‑24 and were superseded the next day by the accum refit + two‑sided filters — current values: k_r +4.8%/+0.9%, 3.75e‑5 / 1.82e‑5, 2.06×; closure fmax 0.0060 / U\* 0.99 kT, reported as a range. The list records what propagated where, not what the numbers are.)*

- `Code/unfav_master_fit.py` — branch classification (`rp_branch`, two‑point test), condition‑level majority (`condition_branch`), branch‑aware `sl(..., nin)`, two‑pass driver.
- `Code/kr_trend.py` → `kr_trend_analysis.md` — k_r re‑run (all superseded 08‑25): glass +4.3% / quartz +0.8%; constants 4.46e‑5 / 2.09e‑5 /s, ratio 2.13×. Also fixed a separate asymmetry bug (the "clean" floor‑hit exclusion had been applied to glass only).
- `Code/alpha_trends.py` → `aplat_plateau_alpha.md` §6 — refactored to READ the master workbook instead of hard‑coding α values; gained the pooled‑plateau rule and both branch columns.
- `Code/fx_trend.py` → `fx_trend_analysis.md` — rebuilt from scratch (the old script could not produce its own workbook); necessity vs size now +31.9% at fixed velocity, and the f_x(|U_sec|) closure moved to stage 3, fmax 0.0047 / U* 0.80 kT (stage 3 is superseded by stage 4).
- `Code/ihop_plot_fits.py` → `fit-gallery-glass-4mday.png`, `fit-gallery-glass-8mday.png`, `fit-gallery-quartz.png` — the fit galleries, newly committed as a reproducer (they previously had none) and regenerated from the refit workbook. The quartz 3 mM and 6 mM RP panels now show the interior peak with the fit tracking it, which is this section's argument made visible.

**Still outstanding from this change:** `model_doc` §5 / §8.1 / §8.3 and working‑record §6z‑M carry the pre‑refit quartz α values and have **not** been updated. The two conditions listed above are the only numbers affected, but they must be corrected there before either document is quoted.
