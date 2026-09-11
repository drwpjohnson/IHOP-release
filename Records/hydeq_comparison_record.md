# HYDEQ — the conventional-model comparator: working record

*Started 2026-08-24 (W.P.J. + assistant). Executes the plan in `two_site_straining_plan.md`. HYDEQ = HYDRUS-EQuivalent: the standard colloid-transport toolkit (kinetic attachment with detachment, depth-dependent straining, Langmuir blocking, dual porosity) built as an explicit comparator for the interception-history model (IHOP / Serial-3). Code: `Code/HYDEQ/`.*

> **⚠ BOUNDARY RULE — HYDEQ IS NOT IHOP.** Every parameter, fit, cost and conclusion in this file describes a model the program argues **against**. HYDEQ numbers must never be quoted as IHOP's, and the two must never be mixed in a table without the model named in the row. The code lives in its own directory and nothing in `Code/*.py` imports it. *(This rule exists because the two documented contamination incidents in this record set — the α₁/α₂ name collision (`overview.md` §3) and the retracted Happel-workbook route (`data_inventory.md` §0) — were both cases of a number from the wrong source being used as if it came from the right one.)*

---

## 1. What is being tested

`overview.md` §2 and §4 flag the conventional toolkit as the incumbent the program must out-explain, and `evidence_map.md` claim 1 asserts that incumbent's inadequacy — but the working record marks the head-to-head **"NOT recorded"** (§6z-AH item A3). This workstream supplies it.

**The proposition (W.P.J.):** HYDRUS with all of its tools either (a) cannot fit the data with only four fitted parameters, or (b) can fit it only by adding parameters — blocking, mobile–immobile — and by violating physical rules that IHOP obeys.

## 2. Model structures

All share the IHOP numerics exactly (90 cells, dt = dx/v, matrix-exponential reaction → upwind advection → implicit dispersion, Pe = 150, 2.98 PV injection, 10 PV total). **Only the reaction block differs**, so any difference in fit quality is structural, not numerical. Verified: the Serial-3 block run through the HYDEQ machinery reproduces `Code/unfav_master_fit.py` at max |Δlog₁₀| = **0.00e+00** on both observables, all four canonical conditions (`hydeq_verify.py` check C).

| structure | fitted parameters | count |
|---|---|---|
| One kinetic site (irreversible) | k_a1 | 1 |
| Two kinetic sites, attachment and detachment | k_a1, k_d1, k_a2, k_d2 | 4 |
| One kinetic site + depth-dependent straining | k_a1, k_d1, k_str, β | 4 |
| One kinetic site + dual porosity (v_slow pinned at 0.05·v) | k_a1, k_d1, f_slow, ω | 4 |
| + Langmuir blocking | + S1max | 5 |
| straining + dual porosity | k_a1, k_d1, k_str, β, f_slow, ω | 6 |
| all terms | + S1max | 7 |
| **IHOP Serial-3 (reference)** | α_s, α_m, f_x, k_r | **4** |

**Parameter parity is exact, and this was initially got wrong.** An early draft claimed IHOP had an advantage because r_s is pinned. It does not: the mobile-phase sink is α_s·k_f·c = α_s·r_s·v·c, the direct analogue of k_a1·C, and `plateau_rs_decision.md` §3 establishes that only the *product* r_s·α_s is identifiable. Pinning r_s buys a **chemistry-independence claim, not a degree of freedom**. Four against four. (W.P.J. caught this.)

**Three distinct four-parameter conventional structures exist**, not one — two kinetic sites; one site plus straining; one site plus dual porosity. Proposition (a) requires all three to fail, or a reviewer familiar with HYDRUS can ask about whichever was skipped.

## 3. Fairness — what binds, what is relaxed

**Data discipline binds BOTH models** (copied verbatim from `unfav_master_fit.py`): W_RP = 6.0, W_SHAPE = 2.5, W_PLAT = 20.0 with PLAT_TOL = 0.25 dex over 1.2–4 PV, W_TAIL = 3.0, W_TSLOPE = 16.0; RP amplitude **FIXED by C₀ through logK, never floated**; BTEC floored at −6; IS ≤ 1 mM dropped; downgradient/DI/perturbation excluded upstream. Relax any of these and the comparison is meaningless.

**Physical-mechanism rules are HYDEQ's to break** — detachment at constant IS/flow (§6z-N CANON), straining at colloid:grain ≈ 0.002 (`data_inventory` §0 SETTLED), transient site-filling, and a fitted second flow region. HYDEQ is given free rein on all four.

**Choices made generous to the comparator, recorded so they can be challenged:** attachment acts on both mobile regions at the same k_a1 (HYDRUS does not velocity-scale it; IHOP does, via k_c = (v_ns/v)·k_f — so the comparator gets *more* slow-region retention than the interception argument allows); β is fitted freely rather than fixed at the literature 0.43; detachment returns colloids to the fast region.

**d50 = 510 µm for BOTH media** (`data_inventory` §4), so ψ(x) = ((d50+x)/d50)^(−β) is **identical for glass and quartz** and cannot encode a medium difference. Over the measured depth range (x/d50 = 19.6→372.5) k_str is exactly degenerate with d50^β, so the fitted k_str is an **amplitude, not a separable rate**.

## 4. Column selection — the quartz peak is an ionic-strength effect

Classifying every unfavorable quartz Li retention profile by where its maximum sits [MEASURED, tidy CSV]:

| IS | column | max at | rise above inlet |
|---|---|---|---|
| 20 mM | M | inlet | nonmonotonic |
| 20 mM | P | inlet | nonmonotonic |
| 20 mM | S | 3 cm | +0.038 log |
| 6 mM | V | 3 cm | +0.215 log |
| 6 mM | Y | 3 cm | +0.367 log |
| 6 mM | AB | 5 cm | +0.503 log |
| 3 mM | AE | 5 cm | +0.484 log |
| 3 mM | AH | 7 cm | +0.801 log |

**Two of three quartz 20 mM replicates do not peak**, and the third rises by 0.038 log — an order of magnitude below any 6 mM rise and plausibly within scatter. Both peak height and depth grow as IS falls. ⇒ the discriminating columns are **quartz 6 and 3 mM**, not 20 mM; testing straining only at 20 mM would be a null test.

> ### ⚠ TERMINOLOGY — "nonmonotonic" is a CONTINUUM, not a binary, and this sentence originally got it backwards
>
> **W.P.J., 2026-09-09: the record must be clear that a profile classed nonmonotonic can be effectively non-peaking.** The interior maximum is not an on/off feature. As conditions become **less unfavorable** the retention profile trends toward a simple exponential, and the maximum flattens until it is not visibly a peak at all — so membership in the nonmonotonic class shades continuously into the multiexponential class rather than switching.
>
> **Quartz 20 mM is exactly that boundary case.** Column S rises by 0.038 log, an order of magnitude below any 6 mM rise; the two-point test calls it peaked, the eye would not. The condition-level majority vote therefore assigns the condition to the non-peaking branch (`unfav_master_fit.py`, `condition_branch`). Both statements are correct, and neither is a defect.
>
> **Consequences for reading and quoting this record:**
> - The classification is produced by a **two-point test** (does RP point 2 exceed point 1?), which is deliberately local and says nothing about peak *prominence*. Prominence is the `rise (log)` column of the table above — use it, not the class label, whenever the argument depends on the peak being visible.
> - **An earlier version of the sentence above used "nonmonotonic" to mean the opposite** — describing the two replicates that do *not* peak. That was a slip, now corrected to "do not peak." Anywhere else in this file that "nonmonotonic" appears, it means **has an interior maximum**, matching the manuscript.
> - The code's vocabulary is **peaked / non-peaking**; `alpha_trends.py` carries its own note on why "multiexponential" was rejected as the name for the negative class. The manuscript's pairing is **nonmonotonic / multiexponential**. The three vocabularies denote the same partition; only the labels differ.

**⚠ Open item for W.P.J.** `model_doc` §8.1 lists Quartz 20 mM as "peaked ✓" and `Serial-Arc-summary` §4 gives its peak at 2.1 cm — defensible for column **S alone**, but two of three replicates at that condition do not peak. Whether the canonical "Qtz 20 mM" means column S specifically, or the condition is better described as marginal, is W.P.J.'s call. **Not edited.** *(The continuum note above is the answer to "how can both be true": at 20 mM the profile is at the boundary, so S's shallow rise and its siblings' flat inlets are the same physics sampled either side of a threshold, not a disagreement.)*

Also: the branch test here is a raw argmax over 10 points, fragile at a 0.038 log rise. The tidy CSV drops the workbook's `Std dev LOG(spheres)` column, so there is no scatter estimate to threshold against.

## 4a. Spin-off finding — the RP-shape inlet window (IHOP, not HYDEQ)

Investigating the quartz 6 mM branch miss produced a change to **IHOP's own objective**: the RP-shape inlet window must be branch-aware, because the inlet-half split straddles an interior peak and penalises a model that reproduces it. **Canonical write-up: `plateau_rs_decision.md` §6**; `model_doc` §5 carries the inline supersession marker. General rule (W.P.J.): *the window must focus on where the change is most dramatic*; n = 4 is specific to this dataset's point count and spacing. Reproducers: `Code/HYDEQ/hydeq_branch_margin.py`, `hydeq_shape_window.py`, `hydeq_anchor_curvature.py`. ~~**Not yet implemented in `unfav_master_fit.py`**~~ — **implemented and refit 2026-08-24** (`plateau_rs_decision.md` §6 "Consequences"): 17 of 19 conditions bit-identical, only Li quartz 1.1 µm 3 mM and 6 mM moved. **But see §4b — it was NOT implemented in HYDEQ, and that breaks the comparison.**

Related and still open for W.P.J.: the quartz 3 mM (AH) profile is over-deep under every window and anchor (model peak 8.8–9.2 cm vs measured 7.0) because the model cannot produce a profile as flat-topped as the data over 5–15 cm. A separate structural miss, not fixed by the window change.

## 4b. ⚠ PARITY BREAK — HYDEQ is scored on the OLD window and every result below predates the fix

*(Found 2026-08-24, after the IHOP refit. Recorded before repair so the defect is on the record independently of whatever the re-run shows.)*

§4a above ends "not yet implemented in `unfav_master_fit.py`." **It has since been implemented there — but NOT in `Code/HYDEQ/hydeq_fit.py`.** That file still carries the pre-change helper:

```python
def sl(x, y):          # no `nin` argument -- always the half-split
    h = len(x) // 2
```

So IHOP and the conventional structures are now scored under **two different RP-shape windows**, which §3 of this record ("what binds") says makes the comparison meaningless. This is not a marginal mismatch:

- **3 of the 7 HYDEQ columns are affected** — Li.AE, Li.AH (quartz 3 mM) and Li.V (quartz 6 mM) are branch-aware under IHOP, half-split under HYDEQ. The other four (Li.O, Li.P, Li.R, Li.S) are unaffected.
- Those three are **exactly the peaked quartz columns**, i.e. the ones carrying the question this whole workstream exists to answer (§1: can a conventional structure make the quartz peak?). The mismatch is concentrated where the argument lives, not spread harmlessly across the set.

**Expected direction, stated in advance so the re-run can contradict it.** The half-split straddles an interior peak and averages the rise against the fall, penalising a model that reproduces the peak — that is precisely why §6 of `plateau_rs_decision.md` replaced it. IHOP reproduces those peaks; the conventional structures are nonmonotonic there and so never paid that penalty. Fixing parity should therefore **move results in IHOP's favour on those three columns**. A correction that flatters our own conclusion deserves more scrutiny than one that costs us something, so the re-run must be reported whichever way it lands, including if the margin turns out to be negligible.

**Consequently, every number in §7, §8 and §8a — and the prediction verdicts in §6 — is provisional** until the re-run *(**⚠ SUPERSEDED — the re-run was completed the same day; see §4b.1 immediately below, and §8b "post-parity … CURRENT". This sentence describes the PRE-FIX state only and no longer applies to any number in this file.**)*. Predictions 1 and 2 were confirmed and 4 falsified on 3-of-7 mismatched columns. Prediction 1 (straining is non-peaking under both conventions) is a structural claim and is unlikely to move. Predictions 2 and 4 rest on cost magnitudes and retained-mass fractions and could.

> **⚠ Read this before quoting the provisional warning above.** The sentence was written deliberately
> *before* the repair, so the defect would be on the record independently of what the re-run showed —
> which was right. But it was never marked once §4b.1 landed six lines later, and it has since misled
> a reader into treating the current §7/§8 numbers as unverified: on 2026-09-10 the assistant flagged
> **16.09 / 34.99 (macro cost), 0.207 and 0.285–0.432 (worst-case RP RMS), and the 6-of-7 / 2-of-7
> peak-location counts** as provisional and told W.P.J. they might need regenerating before
> submission. **They do not — all are post-parity and current.** *(Marked 2026-09-10 at W.P.J.'s
> direction. General lesson for this record: a warning written before its own repair needs a
> supersession marker on its own line the moment the repair lands, or it outlives the defect.)*

**Also stale in `hydeq_fit.py`:** `KR_MED = {"glass": 5.58e-5, "quartz": 1.87e-5}`, the old necessity-fit k_r constants, superseded 2026‑08‑24 by 4.46e-5 / 2.09e-5 (`kr_trend_analysis.md`). These are optimiser **seeds** only, so they cannot bias a converged fit, but they must not sit in the file looking current. *(Both of those pairs are themselves now superseded: the current constants are **3.75e-5 / 1.82e-5**, ratio 2.06×, per the 2026‑08‑25 accum refit and two‑sided identifiability filter. Left in place as the audit trail of the 08‑24 state.)*

**The HYDEQ galleries (`hydeq_fits_accum.png`, `hydeq_fits_snap.png`) must not be regenerated or circulated until parity is restored** — they would picture a comparison this record itself calls invalid. *(**⚠ SUPERSEDED — parity was restored 2026-08-24, §4b.1. The embargo is lifted; the galleries are safe to regenerate and circulate.**)*

### 4b.1 — PARITY RESTORED and re-run, 2026-08-24

`hydeq_fit.py` now carries `sl(x, y, nin=None)`, `rp_branch`, `condition_branch` and `branch_windows()`, all matching `unfav_master_fit.py`. Three implementation points worth keeping:

- **The branch is derived from the FULL 29-column set, then applied to whatever subset is fitted.** Deriving it from the fitted subset would take a different majority vote whenever a condition's replicates are split across the in/out boundary. With the canonical five-column set only V of the V/Y/AB triplet is fitted; V alone happens to give the same answer, but by luck. Now it is identical to IHOP by construction, for any subset.
- **The results cache key now includes the window** (`w4`/`wH`). Without that, the fix would have been defeated by its own cache — every entry in `hydeq_results.json` was computed under the old objective and would have been served back as current.
- `KR_MED` seeds refreshed to 4.46e-5 / 2.09e-5. *(Superseded 2026‑08‑25 — current constants are 3.75e-5 / 1.82e-5. Seeds only; they cannot bias a converged fit.)*

**Control — the fix touched only what it should.** The three columns whose window did not change are **bit-identical** to the pre-fix run: Li.R IHOP 4.833 → 4.833, Li.O 12.492 → 12.492, Li.P 1.141 → 1.141, all Δ = +0.000. Only V and AE moved.

**⚠ My stated-in-advance expectation was directionally right and mechanistically wrong.** §4b predicted that parity would "move results in IHOP's favour on those three columns," reasoning that IHOP had been *paying a handicap* the nonmonotonic conventional structures never paid — which implies IHOP's own cost should fall. It did on V (2.89 → 2.72) but **rose sharply on AE (17.66 → 48.11)**. The window change is not handicap-removal; it is a **reweighting that makes the inlet region count far more**, and it raises absolute cost for any model that does not fit the inlet well — IHOP included. IHOP gains only in the *relative* sense, because the conventional structures are much worse at the inlet:

| Li.AE | pre-fix | post-fix |
|---|---|---|
| IHOP | 17.66 | 48.11 |
| best conventional (M7_all, 7 par) | 30.36 | 149.05 |
| IHOP advantage | 1.7× | **3.1×** |

**⚠ And the pre-fix numbers were actively misleading, in the direction that mattered.** On Li.V — a *peaked* column, the branch this whole workstream exists to test — the old half-split scoring had **two conventional structures beating IHOP**: M6_strain_dp 1.78 and M2_2site 1.86 against IHOP's 2.89. Post-fix those become 20.14 and 22.58 against IHOP's 2.72. The inversion was a scoring artifact: the half-split straddles the peak and averages the rise against the fall, so it *rewarded* a nonmonotonic fit on a peaked profile. Any conclusion drawn from the pre-fix V numbers was wrong in the comparator's favour.

Related and equally telling: **under the old window IHOP did not produce the V peak at all** (peak_m = 0.0, branch nonmonotonic). Post-fix it gives 2.6 cm against a measured 3.0 cm. The branch-aware window is what lets the fit express the peak the model is capable of.

## 5. Retention-profile convention

Settled — see **`plateau_rs_decision.md` §5** (canonical). Summary: eq (4) is validated to ≤0.007 log level offset and ≤0.039 log tilt against accumulate-to-excision; accumulating only to end of injection is the worst of the three and must not be re-proposed. **HYDEQ structures are scored under accumulate-to-excision** because eq (4) is not self-consistent for models with detachment or blocking; Serial-3 was refit under the same convention for uniformity (costs moved a few percent, RP RMS unchanged to 3 decimals).

## 6. Pre-registered predictions

Stated before fitting, so the outcome is a test and not a narrative.

1. **Straining cannot place the retention maximum below the inlet** — ψ(x) is monotonically decreasing and neither kinetic site adds a spatial peak.
2. **Blocking can make an interior peak, but only by forgoing inlet removal**, which raises the plateau out of its band at W_PLAT = 20. The measured within-injection plateaus *decline* (GB20 −0.05→−0.15; Qtz20 −1.60→−1.94, §6z-M), so blocking also opposes the observed drift.
3. **Detachment tuned to build the shelf blunts the PV 4–5 cliff** (measured depths 2.52 / 2.76 / 2.20 / 2.12 orders).
4. *(added after the convention work, from W.P.J.'s elution observation)* **Detachment fast enough to build the shelf strips the retention profile during the 7 PV elution**, and with the amplitude fixed by C₀ the model cannot rescale out of it.

**⚠ Prediction 4 is FALSIFIED — see §8a. The mechanism is real but the fits sidestep it, and how they sidestep it is the more important result.**

**⚠ ALL FOUR VERDICTS RE-TESTED 2026-08-24 on the parity-correct objective — see §8c, which supersedes the verdicts below and in §7/§8/§8a.** Summary of what changed: **1 confirmed** and now on a correct objective; **2 not reproduced** on the canonical set (its confirmation was specific to column S); **3 not supported** — the cliff is not blunted and is not discriminating; **4 still falsified, but the retained-mass split INVERTS between branches**, which is a different and stronger result than the one originally recorded.

## 7. Results — RETIRED snapshot convention, seven columns (kept for the audit trail)

Weighted cost (lower is better):

| structure | par | gl O 20 mM | gl R 6 mM | qz S 20 mM | qz V 6 mM | qz AE 3 mM | qz AH 3 mM |
|---|---|---|---|---|---|---|---|
| **IHOP Serial-3** | **4** | 12.42 | 4.81 | **0.44** | 2.86 | **14.76** | **36.42** |
| One kinetic site | 1 | 350.4 | 445.7 | 105.3 | 344.6 | 476.2 | 460.4 |
| Two kinetic sites | 4 | 37.7 | 184.0 | 19.6 | 2.31 | 57.7 | 111.1 |
| One site + straining | 4 | **6.87** | **2.36** | 20.1 | 3.83 | 57.9 | 124.5 |
| One site + dual porosity | 4 | 37.5 | 183.8 | 19.8 | **2.18** | 52.9 | 121.8 |
| straining + dual porosity | 6 | 6.64 | 0.96 | 19.5 | 1.88 | 52.9 | 121.8 |
| all terms | 7 | 6.64 | 0.96 | 19.7 | 4.32 | 10.27 | 41.85 |

**Retention-profile peak depth (cm), the discriminator:**

| column | measured | IHOP | straining | dual porosity | all terms |
|---|---|---|---|---|---|
| qz S 20 mM | 3.0 | 2.1 | nonmonotonic | nonmonotonic | nonmonotonic |
| qz V 6 mM | 3.0 | *nonmonotonic* | nonmonotonic | 0.6 | nonmonotonic |
| qz AE 3 mM | 5.0 | 4.1 | nonmonotonic | 1.7 | nonmonotonic |
| qz AH 3 mM | 7.0 | 6.8 | nonmonotonic | 2.6 | 16.1 |

### What holds

- **Prediction 1 confirmed without exception.** Straining returns a non-peaking profile on *every* column, including all four with a measured interior maximum.
- **Prediction 2 confirmed, sharply.** On column S, blocking pushed hard enough to reshape the profile drove the plateau **out of band** — the only OUT in the entire run — and collapsed the shelf to the detection floor (cost 731.8 vs straining's 20.1). On AH blocking produced a peak at **16.3 cm against a measured 7.0**, with RP RMS worsening to 0.372.
- **Even seven parameters do not fix it.** The full structure is nonmonotonic on S, V and AE, and overshoots to 16.1 cm on AH.

### The headline is not "straining fails"

**No single four-parameter conventional structure handles both branches.** Straining wins the glass multiexponential branch outright — and **beats IHOP** there (6.87 vs 12.42; 2.36 vs 4.81; RP RMS 0.047 vs 0.074 and 0.033 vs 0.042) — but is nonmonotonic on every quartz column. Dual porosity is the only conventional structure that makes quartz peaks, and fails glass badly (183.8). Each conventional mechanism owns one branch and fails the other; IHOP spans both with one structure and four parameters. That is `evidence_map` claim 4 demonstrated against a comparator rather than asserted.

**Reported against IHOP honestly:** IHOP misses the peak entirely on quartz 6 mM column V, where dual porosity both makes a peak and beats IHOP on cost (2.18 vs 2.86).

## 8. Results — accumulate-to-excision convention

IHOP barely moves (costs shift a few percent; RP RMS unchanged to 3 decimals), confirming §5. Two conventional results **do** move, and in the direction predicted — accumulation gives the transient mechanisms the whole elution to act:

- **Dual porosity on AH reaches the measured peak depth**: 2.56 → **6.78 cm** against a measured 7.0 (IHOP 6.78). Cost still worse (108.1 vs 42.2) and RP RMS 0.231 vs 0.142, but the peak-depth failure does **not** survive the fair convention. This must be reported.
- **Dual porosity on glass R invents a spurious peak** at 1.89 cm where the data are multiexponential, at cost 185.

## 8a. Prediction 4 falsified — and the conventional model needs TWO independent sinks

**The prediction.** Detachment fast enough to build the multi-PV shelf should also strip the retention profile during the 7 PV elution, since retained(10 PV)/retained(3 PV) falls to 0.95 at k_d1 = 3e-5 /s and 0.55 at 1e-4 [COMPUTED, sensitivity with the second site switched off].

**What the fits actually did.** Retention *grew* during elution in every accumulate-to-excision fit, ratio **1.03 to 1.34** — the opposite direction. Fitted k_d1 spans **1e-9 to 3.2e-4 /s** (half-lives 0.5 PV to 160,000 PV) with no cross-column pattern.

**Why — the two jobs are split across two sites.** Intervention test, one parameter changed at a time [COMPUTED]:

- **Set k_d1 → 0:** the shelf collapses. For one-site-plus-straining it falls to the −6 detection floor in every column (change −1.26 to −3.58 log). **Detachment is what makes the tail** — the mechanism in the prediction is real and load-bearing.
- **But the retention profile barely moves** — retained-mass ratio **1.000 to 1.119**.
- **Set k_str → 0** to isolate where the mass sits: **97.8–98.9 % of retained colloids are on the IRREVERSIBLE straining site** (columns O, R, AE, AH, P). The reversible pool carries ~1–2 % of the mass and exists only to generate the tail.

⇒ **The conventional structure avoids the conflict by giving the two observables two mechanically independent sinks**: an irreversible site holds the retention profile, and a separate ~1–2 % reversible pool makes the shelf. Neither constrains the other, so k_d1 is essentially unidentified by the retention profile — which is why it wanders five orders of magnitude across columns.

**Why this is the stronger criticism.** IHOP produces both observables from **one** colloid population differing only in interception history. The conventional model needs two sinks and a tuned ~1–2 % split — **which is the same structure `data_inventory.md` §5 already records W.P.J. annotating as "fabricated" in the original 2-k_f workbook** (`a1 = 0.01`: 1 % of the population assigned k_f2 ≈ 115× below bulk, "can force tailing by making fir…", "2k fabricated quartz"). The fitted HYDEQ structures rediscover that same invented subpopulation independently, from a free fit, without being told to.

**⚠ Two exceptions, reported not buried.** Columns S and V put only 0.1 % and 1.3 % on the irreversible site — the reversible pool holds essentially everything there. Those are two of the better-fitting quartz columns, so the 98/2 split is the common pattern (5 of 7) and not universal.

**Honest status of the prediction:** stated before fitting, tested, **not confirmed**. The physical mechanism behind it is confirmed (detachment makes the shelf; detachment at those rates does strip a reversible pool), but the structural conclusion drawn from it was wrong because the model has a second site to hide the profile on.

## 8b. RESULTS — canonical five-column set, post-parity (2026-08-24, CURRENT)

Reproducer: `python3 hydeq_fit.py --canon --conv accum`. Five Li columns at 1.1 µm / 4 m/day so **medium and ionic strength are the only variables**; two matched glass/quartz pairs plus the low-IS extreme. Chosen for readability — with eight structures, seven-plus columns buried the structure-to-structure differences the reader is meant to compare. Costs are ½·SSE; lower is better.

| structure | par | R glass 6 | V quartz 6 | O glass 20 | P quartz 20 | AE quartz 3 |
|---|---|---|---|---|---|---|
| **IHOP Serial-3** | 4 | 4.83 | **2.72** | 12.49 | **1.14** | **48.11** |
| M1 one site | 1 | 445.71 | 363.19 | 350.09 | 59.65 | 622.78 |
| M2 two site | 4 | 184.67 | 22.58 | 37.14 | 8.32 | 204.89 |
| M3 straining | 4 | **1.23** | 24.56 | **6.78** | 8.53 | 206.53 |
| M4 dual porosity | 4 | 184.99 | 20.14 | 37.51 | 7.86 | 164.45 |
| M5 strain+block | 5 | 1.23 | 6.30 | 6.78 | 1.23 | 164.82 |
| M6 strain+dualpor | 6 | **0.76** | 20.14 | 6.52 | 7.84 | 164.45 |
| M7 all | 7 | 0.76 | 3.51 | 6.68 | 7.93 | 149.05 |
| *measured branch* | | multiexponential | **peaked, 3.0 cm** | multiexponential | nonmonotonic | **peaked, 5.0 cm** |

> **✔ RESOLVED (2026‑08‑25) — NOT a defect. The IHOP row above is the *accum* scoring of the published fit, not a different fit.** Task #17 closed.
>
> I first reported this as an implementation defect, on the strength of a forward comparison that was **testing the wrong pair**: `unfav_master_fit.Eng.run`'s `rp` against `IhopReferenceEngine.run_ihop`'s `rp`. Those are two *different conventions* — the master's `rp` is the injection‑window rate snapshot, the reference engine's `rp` is the solid phase accumulated to excision. The like‑for‑like quantity is `rp_snap`, and against that the reference engine reproduces the master **exactly**: max |Δlog| = **0.00e+00** on both BTEC and RP, at every parameter set tested including the railed‑α_s ones. **The verification check that `IhopReferenceEngine` exists to perform passes perfectly.** My "0.273 log divergence" was the accum‑vs‑snap difference, correctly computed and wrongly attributed.
>
> The convention difference is real and worth documenting. It is monotone in α_s (a_m 0.10, f_x 0.005, k_r 3e‑5, quartz 4 m/d), max |Δlog| over the profile:
>
> | α_s | 0.50 | 0.34 | 0.10 | 0.05 | 0.02 | 0.005 | 0.001 | ≤2e‑4 |
> |---|---|---|---|---|---|---|---|---|
> | max Δlog | 0.014 | 0.012 | 0.003 | 0.011 | 0.043 | 0.130 | 0.225 | 0.267 |
>
> **Domain of validity of the eq‑(4) equivalence (§5): α_s ≳ 0.05**, where the difference stays ≤ ~0.014 log. It degrades below that and saturates near 0.27. The mean over the profile stays ≤ 0.009 log throughout, so the divergence is localised, not a global offset.
>
> **Why it grows as α_s → 0** — this is physics, not bookkeeping. At low α_s almost nothing attaches directly from the bulk; attachment proceeds through the near‑surface and crawl states, which keep delivering to the wall *after injection stops*. The accumulated profile at 10 PV therefore includes substantial post‑injection attachment that the injection‑window snapshot cannot see. At high α_s the direct route dominates and stops with the injection, so the two conventions agree.
>
> **Consequence for the tables:** AE reads 48.11 here and 38.42 in `UnfavorableMaster.xlsx` because the HYDEQ comparison scores under *accum* while the master's per‑column IHOP fits were made under *snap*.
>
> **⚠ RETRACTION, same day (W.P.J.): I first wrote "both are correct under their own convention; do not reconcile them." That is wrong and W.P.J. rejected it.** Snapshot is **not a valid convention**. The columns are excised at 10 PV, *after* elution, so the measured retention profile is the accumulated solid phase — full stop. `accum` is the observable; eq (4)'s injection‑window rate is not a representation of it. There is one correct convention here, not two.
>
> **Why snapshot is still in the analysis at all** — the only honest answer: `unfav_master_fit.py` fits against `Eng.run`'s `rp`, which *is* the snapshot. Every published per‑column IHOP parameter was fitted under it. It was retained on the strength of the §5 equivalence check (≤0.007 log offset, ≤0.039 tilt), which licensed leaving the published numbers alone. **That licence is now known to be bounded at α_s ≳ 0.05, and 10 of the 29 columns fall below it:**
>
> | column | α_s | | column | α_s |
> |---|---|---|---|---|
> | Li.AE | 1e‑4 **railed** | | Tong.O | 0.0185 |
> | Li.AB | 1e‑4 **railed** | | Tong.AK | 0.0218 |
> | Li.AH | 1e‑4 **railed** | | Li.Y | 0.0379 |
> | Tong.AX | 0.0107 | | Tong.B | 0.0492 |
> | Li.R | 0.0163 | | Tong.BU | 0.0181 |
>
> **W.P.J.'s mechanism confirmed:** injection is **2.984 PV of a 10 PV run**, so **7.016 PV — 70% of the experiment — elapses after the snapshot is taken**, and eq (4) accounts for none of it. Columns are excised at 10 PV. `accum` is the observable.
>
> **But my "0.27 log" alarm was also wrong, and by a lot.** That maximum sits at **x = 0.11 cm**, inside the first model grid cell — a depth that is never sampled. Measured depths are 1, 3, … 19 cm. Evaluated *there*, with the level offset removed, the shape error is:
>
> | α_s | 1 cm | 3 cm | 5–19 cm |
> |---|---|---|---|
> | 0.34 | +0.008 | +0.006 | ≤0.006 |
> | 0.02 | −0.015 | −0.002 | ≤0.003 |
> | 1e‑4 | **−0.032** | −0.002 | ≤0.005 |
>
> **≤0.033 log, essentially all of it at the single first point.** And on the *column‑integrated* total, eq (4) agrees with the excision‑time truth to **≤0.010 log at every α_s** — because assuming steady deposition for the whole injection overestimates by about what ignoring post‑injection deposition underestimates. Two errors that nearly cancel. That is why the §5 level‑and‑tilt validation passed: it was measuring the quantities that survive.
>
> ### Where the 38.42 → 48.48 gap actually comes from
>
> Scoring the master's own (snap‑fitted) parameters under the accum objective gives **48.48** on Li.AE against the accum refit's 48.11 — i.e. **the parameters barely move between conventions**; the cost moves because the objective values the same fit differently. Block decomposition, Li.AE:
>
> | block | snap | accum |
> |---|---|---|
> | rp_level | 3.30 | 3.66 |
> | **rp_shape** | **34.66** | **44.35** |
> | plateau / tail level / tail slope | 0.00 / 0.44 / 0.03 | 0.00 / 0.44 / 0.03 |
>
> **The entire gap is the RP‑shape term.** With `nin=4` the inlet log‑slope is regressed over the first four points on a 6 cm baseline at weight 2.5, so a −0.032 log shift at the *first point alone* tilts it enough to move the squared term by ~10. Same on AH (183.64 → 209.41).
>
> ### ✔ Both actions closed (2026‑08‑25)

**Task #19 done.** `unfav_master_fit.py` now fits the accumulated solid phase; the snapshot capture is deleted from the engine. The master's RP now equals `IhopReferenceEngine`'s to **0.000e+00**, and the master's costs equal the HYDEQ reference line exactly — R 4.83, V 2.72, O 12.49, P 1.14, AE 48.11. **The cross‑convention gap is closed, not papered over.** Measured cost of the switch across all 29 columns (`Code/accum_refit_check.py`): α_s ≤ **0.090 dex**, α_m ≤ **0.180 dex**, RP peak depth moved >0.5 cm on **no column**. Fit quality median 12.42 → 12.49; half‑split n=17 median still **11.8**.

**Task #21 done.** The "AE fits poorly" characterisation is retracted in `hydeq_fit.py`, `HydeqComparisonCanonical.docx` §5 and `HydeqComparisonFullSet.docx` §7. Numbers below are the current accum ones.

**One bug the refit exposed, in `kr_trend.py`.** The clean‑set filter was a ONE‑SIDED floor test (k_r ≤ 1.5e‑6). Li.M's k_r moved from 1.00e‑6 railed at the *lower* bound to **5.63e‑3** — 3.75 dex — at cost unchanged to 2 dp (0.72 → 0.72). The floor test caught that column before and does not catch it now, so a column carrying **zero information** about k_r swung the quartz geomean 1.97e‑5 → 3.30e‑5 and the glass/quartz ratio **2.27× → 1.35×**. Identifiability is two‑sided; which bound a degenerate column drifts to is not the criterion. The filter is now the **pinning penalty itself** (<1% ⇒ the column cannot vote), excluding 9 of 29 rather than 2, and giving **2.06×** — consistent with the 2.13× recorded under snapshot. Necessity unchanged at +4.8%/+0.9%. k_r figure y‑limit raised to 1e‑2 so the degenerate point is shown, not clipped.

**A second stale‑deliverable bug**, unrelated to the physics: `build_manuscript_tables.js` hard‑coded its input directory to `outputs/updated`, so the first post‑refit re‑run rebuilt Tables 3 and 4 from **old JSONs** and wrote them out looking current. Both paths are now CLI arguments.

**Task #22 CLOSED — `f_x` closure.** *(This paragraph originally read "Still open"; both numbers in it are superseded and are kept only to show the route.)* The first refit gave fmax 0.0036 / U\* = 0.52 kT against the then‑adopted 0.0047 / 0.80 kT — but 0.52 was an artefact of the same one‑sided floor filter described in the paragraph above, which let the non‑identifiable column Li.M back in at the deepest well. Under the two‑sided f_x‑identifiability filter the closure is **fmax 0.0060, U\* 0.99 kT** (`fx_trend.xlsx`), and the variants span 0.99–1.35 kT at indistinguishable RMS. **W.P.J. decided 2026‑08‑25 that no single U\* is adopted: report the shape and the range, "half to a few kT."** f_x necessity is unaffected either way (size +32.2%, IS +17.5%). Full four‑stage history in `fx_trend_analysis.md`.

### The finding that matters more than the convention
>
> **On Li.AE and Li.AH the cost is 90% and 98% rp_shape.** Their headline costs (38/48 and 188/214) are *one term* — the inlet log‑slope — not diffuse misfit. AE's RP RMS is 0.172 and AH's peak depth is reproduced at 7.00 cm against a measured 7.0. **Quoting "IHOP fits AE poorly, cost ~39" is misleading**: the level and the peak are right and a single heavily‑weighted 4‑point slope regression carries almost all the penalty. Anywhere those two columns are described, say which term is responsible.
>
> **Action (task #19): refit `unfav_master_fit.py` under `accum` and retire `snap` from the engines.** Snapshot is invalid and should not be selectable. The refit is **low risk** — parameters move negligibly (48.48 → 48.11 on the worst‑affected column) — so this is a correctness and hygiene fix, not a renegotiation of the results. Until it is done, the master's α values for the ten low‑α_s columns are fitted to the wrong observable, but by an amount that does not move them.

## 8d. THE FULL UNFAVORABLE SET — 29 columns, 18 conditions (2026‑08‑25)

Reproducers: `hydeq_fit.py --conv accum` (no `--canon`) → `hydeq_full.json`, 232 fits; `hydeq_fullset_analysis.py` → `hydeq_fullset_stats.json`; `hydeq_export.py --fullset` → `HydeqComparisonFullSet.xlsx` + three galleries; `build_hydeq_fullset_docx.js` → `HydeqComparisonFullSet.docx`. **Control: the full‑set cache reproduces all 40 canonical `accum` entries bit‑identically**, so §8b's numbers are a strict subset of these.

**§8b.0 below was written on the canonical five and its cost argument does not survive extension.** Corrected here; §8b.0 is retained for the audit trail and must not be cited on its own.

### How the experiments count — 18 vs 19 conditions, and where 29 sits (reconciled 2026‑08‑26)

Raised by W.P.J.: *"If there are 18 distinct conditions, and ten favorable experiments, there must be more than 29 experiments since there are multiple replicates among the 18 conditions."* The total **is** larger, but not because replicates push past 29 — **29 already counts replicates.** Replication is what turns 18 conditions into 29 columns; the extra experiments are the **favorable** set, which is disjoint from the 29.

**Unfavorable, fitted: 29 columns in 18 conditions.**

| replicates | conditions | columns | which |
|---|---|---|---|
| n = 4 | 1 | 4 | glass 1.1 µm / 4 m/d / 20 mM — Tong AE, AK, AQ **+ Li O** |
| n = 3 | 3 | 9 | glass 0.2/8/20 (BE, BH, BN); quartz 1.1/4/20 (M, P, S); quartz 1.1/4/6 (AB, V, Y) |
| n = 2 | 2 | 4 | glass 2.0/8/20 (CI, CO); quartz 1.1/4/3 (AE, AH) |
| n = 1 | 12 | 12 | — |
| **total** | **18** | **29** | |

**Favorable: 13 columns in 13 conditions, no replicates.** Ten carry both a BTEC and an RP and get the full Model 2 fit; three are **RP‑only** (Tong B, AU, BB) and stay k_f‑only. So "ten favorable" is the *fitted* subset, not the favorable set.

**Grand total: 42 fitted columns** = 29 unfavorable + 13 favorable. **43 exist in the data**; the extra is quartz Li 1.1 µm / 4 m/d / **1 mM** (col AK), removed by the `IS ≤ 1 mM` rule in the data discipline (§4).

**⚠ Why 18 here and 19 elsewhere — both are right, and the difference is a modelling choice, not drift.** Conditions are grouped by **(medium, size class, velocity, IS)**, and `sizeclass()` maps 0.98 / 1.0 / 1.1 µm all to 1.1. That merges **`glass_Li_1.1um_4mday_20mM`** (col O) with **`glass_Tong_1.1um_4mday_20mM`** (AE, AK, AQ) into the single n = 4 condition above — **across the two studies**. Group by `condition_id`, which keeps Li and Tong separate, and the same 29 columns fall into **19** conditions. `hydeq_fullset_stats.json` (`n_conditions`) and this section report **18**; CLAUDE.md's "17 of 19 conditions are bit‑identical" is the by‑study count. Neither is stale.

**That merge is substantive, not bookkeeping.** Every condition‑level quantity in this record — the branch‑majority vote that sets the RP‑shape window, `cond_total`, `cond_median`, the branch‑balanced macro average — treats one Li column and three Tong columns as replicates of one another. **If the manuscript reports a condition count, say which grouping it uses**, and consider whether the cross‑study merge needs stating outright.

### Three weighting traps, all of which I fell into

1. **Per‑column totals weight by replicate count.** Three columns at glass 0.2 µm/8 m/d against one at 0.1 µm/8 m/d — summing over columns triples the first condition. Aggregate per condition.
2. **The set is 15 non‑peaking conditions to 3 peaked.** An unweighted total is ~83% decided by the class where the conventional structures win. **On the raw per‑column total Hydeq7 (7 par) beats IHOP, 609.0 to 777.1.** True of this column set, and the wrong summary. Report both.
3. **Raw "correct branch" counts inherit the same imbalance.** Hydeq3 scores 22/29 while being *structurally incapable* of a peaked profile — right 22 times for no reason. MCC 0.00.

### Cost, per condition, branch‑balanced

| structure | par | macro | non‑peaking | peaked |
|---|---|---|---|---|
| **IHOP** | 4 | **16.09** | 11.82 | **20.35** |
| Hydeq7 all | 7 | 34.99 | **4.10** | 65.88 |
| Hydeq5 strain+block | 5 | 38.13 | 5.42 | 70.84 |
| Hydeq6 strain+dualpor | 6 | 43.47 | 7.47 | 79.46 |
| Hydeq3 straining | 4 | 52.02 | 9.72 | 94.32 |

**IHOP is genuinely worse on non‑peaking profiles** (11.82 vs 4.10; RP RMS 0.084 vs 0.069 log). Concede it.

### Retention‑profile RMS — no weights involved

IHOP median 0.092, **worst column 0.207**. Every conventional structure degrades to 0.285–0.432 on its worst (Hydeq5 0.432, Hydeq7 0.388). The uniform‑adequacy claim survives in this currency; it does not survive in composite cost on an unbalanced set.

### Branch as a classification, and the transition

| structure | sens | spec | MCC | verdict |
|---|---|---|---|---|
| **IHOP** | 1.00 | 1.00 | **1.00** | switches |
| Hydeq7 | 0.86 | 1.00 | 0.91 | switches |
| Hydeq6 | 0.71 | 1.00 | 0.81 | switches |
| Hydeq5 | 0.14 | 1.00 | 0.34 | switches |
| Hydeq4 | 0.86 | 0.36 | 0.20 | 14 false peaks |
| Hydeq3, Hydeq1 | 0.00 | 1.00 | **0.00** | **cannot switch** |
| Hydeq2 | 0.00 | 0.91 | −0.15 | worse than chance |

**Peak LOCATION is the discriminator nothing else survives.** Within 1 cm (half a sampling interval): IHOP 6/7, Hydeq4/6 2/7, everything else 0/7. Hydeq5 and Hydeq7 place Li.AH's peak at **19.89 cm in a 20 cm column** against a measured 7.0 cm — while scoring *lower cost* than IHOP. Cost and feature reproduction dissociate; that is the load‑bearing observation.

### The eq‑15 ordering — and the language it must be written in

Ranking all 29 by margin = log₁₀[α_m(1−α_s)/α_s] puts **28/29** on the correct side of zero. The miss, Li.P at **+0.04**, is on the boundary, as is the nearest correct call (Tong.H, −0.05). Every glass column ≤ **−0.46**; quartz spans **−2.06 to +2.91**. Mineralogy sets the regime; IS and size move a condition along it and across the crossing.

> **⚠ TERMINOLOGY — "non-peaking" is NOT "multiexponential" (W.P.J., 2026‑08‑26).** I wrote the eq‑15 ordering as a two‑way partition, multiexponential *versus* peaked. **That is wrong.** `rp_branch` tests one thing: whether the profile has an **interior peak**. Its negative class is **non-peaking**, and a non-peaking RP may be multiexponential (steep at the inlet, shallow downgradient) **or simply log‑linear**. Multiexponential is a *sub*class of non-peaking, not a synonym for it.
>
> The margin therefore reads as **three regimes, not two**:
>
> | margin | RP form |
> |---|---|
> | strongly negative | **multiexponential** — e.g. **Tong.R, quartz 0.5 µm / 8 m/d / 50 mM, −2.06**, the clean exemplar |
> | near zero | **log‑linear / single‑exponential** — neither label applies |
> | positive | **peaked** — interior peak |
>
> **Consequence for the one miss.** Li.P (quartz 1.1 µm / 4 m/d / 20 mM, **+0.045**) must **not** be described as a multiexponential column landing in the wrong region. Its fitted parameters say the profile should be essentially **log‑linear**, and a two‑point monotonicity test on a near‑log‑linear profile can fall either way. It is a column at the crossing, not a misclassification — which is the honest way to report it, and it is *weaker* language than "miss". Its replicates straddle the boundary too (Li.M −0.293 nonmonotonic, Li.S +0.668 peaked), so the condition itself is at the crossing.
>
> **Consequence for the figure and its caption.** The dashed line α_m = α_s/(1−α_s) separates **peaked (above) from non‑peaking (below)**. Multiexponential is the **far field of the non‑peaking side**, not the whole of it. Any caption or sentence that partitions the plot into "multiexponential" and "peaked" regions is mislabelling the lower half. The `predicted`/`measured` fields in `hydeq_fullset_stats.json` use monotone/non‑monotone correctly; only the prose drifted. **Fixed at source 2026‑08‑26 in `Code/alpha_trends.py`** — `branch_fitted()` returned `"multiexponential"` as the negative class, the measured branch was renamed to it, and the figure title read *"below = multiexponential"*. All four labels now say **monotone**. **The figure and the workbook must be regenerated to pick this up** (labels only; no numerical effect).
>
> **The clean multiexponential exemplar is Tong‑Qtz‑8m/d‑0.5µm‑50mM‑ColR at −2.06** (W.P.J.), the one column far enough below the line for the term to be earned.

> **Margin is a log ratio with α_s in the denominator, so it expands as α_s → 0 (2026‑08‑26).** The three largest positive margins — Li‑Qtz‑4m/d‑1.1µm‑3mM‑ColAE (+2.91), Li‑Qtz‑4m/d‑1.1µm‑6mM‑ColAB (+2.79), Li‑Qtz‑4m/d‑1.1µm‑3mM‑ColAH (+2.22) — are the three columns whose α_s sits at the 10⁻⁴ floor. **That is not an artifact to explain away** (W.P.J.): a vanishing α_s means almost nothing attaches on first interception, which is exactly what makes an RP strongly peaked. The regime assignment is real; only the *magnitude* is soft, because the scale stretches at small α_s.
>
> Practical consequence: **use the sign and the ordering, not the numerical spread.** Do not write "quartz spans five decades" — that width is the log scale opening up, not five decades of physical separation. Every glass column remains ≤ −0.46.

> **⚠ LANGUAGE (W.P.J., 2026‑08‑25).** My first write‑up called this "predicted, not fitted — out of sample". **That is wrong and W.P.J. corrected it.** α_s and α_m are fitted to these columns, and the objective contains the two‑segment RP log‑slope term, so branch information is *inside* the fit. Nothing is held out. What is true: the branch is **not a degree of freedom of its own** — no branch parameter, no switch — and falls out of two parameters that must simultaneously serve the BTEC and the RP level. **We are describing, not predicting.** IHOP's promise is that meaningful descriptive parameters will lead to improved prediction later; that promise is not evidence and must not be written as though it were. Corrected in `hydeq_fullset_analysis.py` and in the Word document.

### Caveats to carry forward

- **The diagnostic subset is 3 conditions of 18** (quartz 3, 6, 20 mM plus Tong.B). Branch‑balancing is right, but this is the vulnerability a reviewer will find — not the aggregate cost.
- **IHOP's worst column, Li.AH at 214.3**, is the reference engine's; `unfav_master_fit` gives 188.3 (task #17, α_s railed).
- **The galleries average model curves across replicates**, which flattens peaks sitting at different depths (quartz 6 mM: 5.0, 2.6, 3.4 cm). Thin grey per‑column IHOP curves were added underneath (W.P.J.'s suggestion) so the flattening is visible rather than silent.

## 8e. HydeqComparisonCanonical.docx RETIRED (2026‑08‑25, W.P.J. approved)

**One comparison document now, not two.** `HydeqComparisonFullSet.docx` supersedes the canonical one on every axis it shared:

| canonical section | disposition |
|---|---|
| §2 cost table, §3.1 worst‑member | **superseded and contradicted** — reverses on the full set (Hydeq7 609.0 vs IHOP 777.1 per column). It carried its own correction notice, which is not a state a document should ship in. |
| §3.2 collapse‑somewhere, §3.3 branch/peak | superseded — full set does both on 29 columns, with MCC instead of raw counts and 7 peaked columns instead of 2 |
| §5 qualifications | duplicated, computed on more data in the full set |
| §6 structures table | superseded by the full set's term‑activity matrix + governing equations (§1) |
| **§4 k_r necessity** | **MOVED to full set §8** |
| **Figure 1 (canonical fits, grey dashed k_r = 0)** | **MOVED to full set Figure 1** |

The two moved items were the only content that existed nowhere else, and neither depended on the canonical framing — the k_r work was done on the ten Li columns behind those five conditions.

`Code/build_fits_canonical.js` is marked **RETIRED, DO NOT REGENERATE** at the top and kept in the tree as the audit trail for how the canonical‑five argument was framed and why it was withdrawn. `Code/canon_nokr_fit.py` now emits **`canon_nokr_stats.json`**, and full‑set §8 reads every number from it — no literals in the prose, after this project shipped drifted numbers twice.

**Delete `HydeqComparisonCanonical*.docx` from Manuscript/HYDEQ when convenient**; the `.png` and `.xlsx` of that name remain valid (they are the canonical five‑column HYDEQ gallery and workbook, still generated by `hydeq_export.py --canon`).

### 8b.0 THE MAIN MESSAGE — read the collection, not the columns (W.P.J., 2026‑08‑25)

> **SUPERSEDED IN PART by §8d above.** The generality framing stands; the specific cost numbers here are the canonical five only, and the "worst member" argument reverses on the full set. Cite §8d.

**The claim is generality, not per‑column victory.** Reading this table column by column loses the argument, and an earlier draft of my analysis made exactly that mistake — leading with "straining beats IHOP on glass" as though the comparison were a series of separate contests. It is not. The question is *which single structure, with one parameterisation, describes the whole set.*

| structure | par | TOTAL | WORST column | branch right | peak within 1 cm |
|---|---|---|---|---|---|
| **IHOP, no k_r** | **3** | **64.3** | **39.5** | **5/5** | **2/2** |
| IHOP Serial‑3 | 4 | 59.5 | 38.4 | 5/5 | 2/2 |
| M1 one site | 1 | 1841.4 | 622.8 | 3/5 | 0/2 |
| M2 two site | 4 | 457.6 | 204.9 | 3/5 | 0/2 |
| M3 straining | 4 | 247.6 | 206.5 | 3/5 | 0/2 |
| M4 dual porosity | 4 | 415.0 | 185.0 | 3/5 | 1/2 |
| M5 strain+block | 5 | 180.4 | 164.8 | 3/5 | 0/2 |
| M6 strain+dualpor | 6 | 199.7 | 164.5 | 5/5 | 1/2 |
| M7 all | 7 | 167.9 | 149.0 | 5/5 | 0/2 |

*IHOP totals are on the `unfav_master_fit` engine; conventional totals on `IhopReferenceEngine`/HYDEQ — see the defect box below. Using the reference engine's AE (48.11) instead raises IHOP‑4's total to 69.3 and its worst column to 48.1, which changes nothing here.*

Three things follow, none of which depend on k_r:

1. **A model of a set is judged by its worst member.** IHOP's worst column is 39.5; the best conventional worst column is 149.0, from the seven‑parameter M7. Nearly 4× worse, at more than twice the parameters.
2. **Every conventional structure that wins somewhere collapses somewhere else, and they collapse in different places.** Straining is the best structure on both glass columns (1.23, 6.78) and the second‑worst of all on AE (206.5). Covering the five with conventional tools means *switching mechanism* between experiments that differ only in mineralogy and ionic strength. That is not a model of the phenomenon; it is a per‑experiment lookup table.
3. **The switch does not even work.** Four of the seven structures cannot produce an interior retention peak at all — ψ(x) = ((d50+x)/d50)^(−β) is monotone decreasing by construction — and the ones that can put it in the wrong place: M4/M6 at 0.78 cm where the data say 3.0 cm (V); M7 at 1.0 cm (V) and 2.3 cm (AE, measured 5.0). **No conventional structure gets both peaks.** IHOP, without k_r and with three parameters, gets the branch right on all five at the measurement resolution and both peaks inside half a sampling interval — V 3.44 cm vs 3.0, AE 5.22 cm vs 5.0.

So the per‑column glass loss is real and must still be reported (§below) — but as a detail *inside* a generality result, not as a counterweight to it. IHOP is never the best structure on glass; it is the only structure that is never bad. **Uniform adequacy across the collection, not sporadic excellence on members of it, is the finding.** And because the k_r‑free model retains all of it, the generality does not rest on reentrainment.

**The result splits cleanly by branch, not by medium-as-such.**

- **On the two multiexponential glass columns the conventional model WINS.** Straining beats IHOP on R (1.23 vs 4.83) and on O (6.78 vs 12.49), at equal parameter count. This is not a grudging concession — it is the honest headline of the glass half, and it must be reported as prominently as the quartz result. A model that could not be beaten anywhere would be suspicious.
- **On all three quartz columns IHOP wins**, and on the two peaked ones it wins against structures with **seven** free parameters: V 2.72 (4 par) vs 3.51 (7 par); AE 48.11 (4 par) vs 149.05 (7 par).

### Straining is non-peaking on every column — PREDICTION 1 CONFIRMED, now on a parity-correct objective

M3_strain returns `peak = 0.0`, branch non-peaking, on all five columns including both peaked ones. Depth-dependent straining ψ(x) = ((d50+x)/d50)^(−β) is a *decreasing* function of depth and cannot produce an interior maximum. This is structural, not a fitting failure, and it is the cleanest single result in the comparison.

### Dual porosity generates peaks — but it is a peak GENERATOR, not a peak reproducer

Only the dual-porosity structures (M4, M6, M7) ever go peaked, so on a first reading they "capture" the quartz peak. They do not:

| column | measured | M4 dual porosity |
|---|---|---|
| R glass 6 mM | **multiexponential** | peaked, 1.9 cm ← false positive |
| P quartz 20 mM | **nonmonotonic** | peaked, 0.3 cm ← false positive |
| V quartz 6 mM | peaked, 3.0 cm | peaked, **0.8 cm** (IHOP 2.6) |
| AE quartz 3 mM | peaked, 5.0 cm | peaked, 4.1 cm (IHOP 4.6) |

**M4 returns a peak on four of five columns while the data have one on two.** It produces peaks where none exist — including on glass, where the profile is plainly multiexponential — and on V it puts the peak at 0.8 cm against a measured 3.0. The mobile–immobile peak is an artifact of the slow region advecting, present almost regardless of the data, so its appearance carries no diagnostic weight. On AE it does land near the right depth (4.1 vs 5.0), which must be conceded — but at cost 164.45 against IHOP's 48.11 and rpRMS 0.257 against 0.135, i.e. right feature, wrong profile.

**Caveat on AE, stated wherever AE is used:** its IHOP cost of 48 is poor in absolute terms. It is in the set for the deep peak, not for fit quality. The harder column AH (measured peak 7.0 cm) is worse still, so this is not a case of choosing the column that flatters the argument — but AE alone should not carry the quartz conclusion, and V (IHOP 2.72, a good fit) is the column to lead with.

## 8c. Predictions 2, 3, 4 re-tested on the parity-correct objective (2026-08-24)

### Prediction 2 — NOT reproduced on the canonical set, and the earlier confirmation was column-specific

Blocking was predicted to buy an interior peak only by forgoing inlet removal, pushing the plateau out of band. On the canonical five, **M5_strain_block is non-peaking with the plateau IN band on every column** — the trade never arises. The earlier confirmation rested on column S, which is not in this set; it is not contradicted, but it does not generalise, and §7's blanket "prediction 2 confirmed" overstated it.

What blocking actually does here is bound-railing and cost-buying:

- On both **glass** columns `S1max` rails to its upper bound 3.0 — infinite capacity, i.e. **blocking switched off**. M5's cost is then *identical* to M3's (1.23 and 6.78), which is a useful internal consistency check: the extra parameter is doing exactly nothing.
- On **quartz** `S1max` takes finite values (0.50–1.20) and buys large cost reductions: V 24.56 → 6.30, P 8.53 → 1.23. On P that brings a 5-parameter conventional structure to within 8% of IHOP's 4-parameter 1.14.

### Prediction 3 — NOT supported; if anything the error runs the other way

Detachment tuned to build the shelf was predicted to *blunt* the PV 4–5 cliff. It does not. Cliff depths (orders, measured vs model):

| column | measured | IHOP | M2 two-site | M4 dual por | M7 all |
|---|---|---|---|---|---|
| glass 6 | 2.76 | 2.89 | 2.83 | 2.81 | 2.79 |
| quartz 6 | 1.43 | 1.48 | 1.70 | 1.64 | 1.48 |
| glass 20 | 2.52 | 2.58 | 2.34 | 2.36 | 2.59 |
| quartz 20 | 1.58 | 2.00 | 2.05 | 2.08 | 1.91 |
| quartz 3 | 1.56 | 1.77 | 1.89 | 1.31 | 1.44 |

Every structure lands within ~0.3–0.5 orders, and on quartz they **overshoot** the cliff rather than blunting it — as does IHOP (2.00 vs 1.58 on quartz 20). The cliff is not a discriminating feature between the two model families on this set, and should not be presented as one.

### Prediction 4 — the retained-mass split INVERTS between the two branches

Computed from the site-resolved solid phase at excision (`hydeq_engine.run()` now returns `S1`/`S2`; the split is calculated, not asserted). S1 is the reversible detaching site; S2 collects the second kinetic site and straining, both irreversible here.

| column | branch | S1 reversible | S2 irreversible | k_str |
|---|---|---|---|---|
| glass 6 | multiexponential | 1.8% | **98.2%** | 1e−3.73 active |
| glass 20 | multiexponential | 0.9% | **99.1%** | 1e−3.46 active |
| quartz 20 | nonmonotonic | 0.7% | 99.3% | 1e−2.85 active |
| **quartz 6** | **peaked** | **100.0%** | **0.0%** | **1e−8.00 — AT THE BOUND, straining OFF** |
| **quartz 3** | **peaked** | **100.0%** | **0.0%** | **1e−8.00 — AT THE BOUND, straining OFF** |

*(M3_strain shown; M5 and M7 give the same picture, except M5 on quartz 20 which flips to 85.4% reversible once blocking is active.)*

**The earlier finding — "97.8–98.9% of retained mass on the irreversible straining site" — is a GLASS-regime statement that was generalised to the whole set.** It holds on the multiexponential columns and is exactly reversed on the peaked ones.

**And the inversion is the result.** On both peaked quartz columns the optimiser drives `k_str` to its lower bound: it does not merely fail to use straining to make the peak, it **discards straining entirely** and places 100% of retained mass on a *reversible* site. Detachment at constant ionic strength and flow is the first of the four physical rules §3 lists as relaxed for the conventional models and obeyed by IHOP. So the conventional structures buy whatever quartz performance they have by leaning wholly on a mechanism they are only permitted because we granted it — and even then they lose to IHOP by 3× on AE and produce a peak at 0.8 cm against a measured 3.0 cm on V.

That is a stronger statement of the comparator's failure than "straining cannot make a peak", because it is about what the model *chooses* when given free rein, not only about what it cannot do.

## 9. Status and what remains

- Done: solver + six verification checks; snapshot pass, all 7 structures × 7 columns; accumulate-to-excision pass for the one-site, straining, dual-porosity, two-site and straining+dual-porosity structures.
- Outstanding: blocking structures under accumulate-to-excision; the full unfavorable set for SI; the k_d1-versus-shelf quantification (prediction 4) turned from a sensitivity into a result; the HYDRUS-1D setup sheet for N. Willis.
- Deliverable: `HydeqComparison.xlsx` (comparison table, fitted parameters, one plottable sheet per column) + `hydeq_fits_<conv>.png`, both regenerated by `hydeq_export.py`.

## 10. Reproducers

`Code/HYDEQ/hydeq_engine.py` (solver, model registry) · `hydeq_verify.py` (six correctness checks; run first) · `hydeq_fit.py` (fitter, incremental JSON cache) · `hydeq_export.py` (workbook + figures). Data: `Data/LiTong_experimental_data_tidy.csv` — the same tidy CSV `unfav_master_fit.py` reads, and the only data source used, so the whole comparison is reproducible from the public repository with nothing withheld.
