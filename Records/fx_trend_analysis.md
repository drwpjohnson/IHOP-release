# Focus fraction f_x — trend analysis (record)

**Reproducer:** `Code/fx_trend.py` → `fx_trend.xlsx` (6 sheets) + `fx_vs_usec.png`, `fx_vs_size.png`, `fx_vs_IS.png`. Engine + data via `Code/unfav_master_fit.py`; |U_sec| imported from `Code/fx_vs_usec.py`.

*`fx_vs_IS.png` regenerated 2026‑08‑24: one series per (study, medium, size, velocity), so ionic strength is the only variable moving along any line — the old figure let size and velocity vary within a series. Series with a single ionic strength are dropped rather than plotted as isolated points on an IS axis. Lines join geometric means; the two columns with k_r on the optimiser bound (Li.M, Tong.U) are ringed in red and excluded from the lines, since their f_x is not identifiable.*

> ⚠ **REBUILT 2026‑08‑24 (W.P.J. approved) — every f_x number below the "Fitted f_x" heading predates the rebuild unless marked otherwise.**
>
> The old `fx_trend.py` could not produce the distributed `fx_trend.xlsx` at all: it wrote 4 sheets with different names, from f_x literals **hard‑coded** out of `serial_model.py` / `serial3_size_fit.py` / `serial3_quartz_check.py` (quartz on fixed‑k_f). The workbook in circulation had 5 sheets and newer numbers, so its generator was a script that is **not in `Code/`**. Same failure mode as `kr_trend.py` and `alpha_trends.py`. Everything is now computed live on the corrected objective (mean‑log plateau, branch‑aware RP window), from the *same* free fits `kr_trend.py` runs — so f_x and k_r are one common set rather than two independent fitting runs.
>
> **Numbers that changed and must not be quoted from the old text:**
> - **Necessity vs size** is now +31.9% (n = 8, glass Tong at **constant v = 8 m/day**, 20 mM; pin = series geomean 0.0025). The old **+67.5%** came from a 10‑column set that **mixed 4 and 8 m/day**, so part of that penalty was velocity, not size. The direction and the conclusion survive; the magnitude roughly halves.
> - **Necessity vs ionic strength** is now +16.5% (n = 3, pin = geomean 0.0014). The distributed workbook's **+20.8%** pinned to **0.0017 — the 20 mM column's own f_x** — which is why its 20 mM row showed a delta of exactly 0. The geometric mean is used now, matching the size sheet and `kr_trend.py`.
> - **The closure** is revised twice over; see the closure section below for the full three‑stage history.
> - Per‑column f_x values all moved (e.g. Tong.AX 0.0006 → 0.00106, Tong.E 0.0052 → 0.0079).

## What f_x is

f_x is the fraction of the near-surface graze population (w) recruited into the grain-to-grain crawl (g): the w→g rate is k₂ = f_x·k_f. It is the operational encoding of **interception focusing** — "interception begets further interception" — with the mechanism being transport across grain-to-grain contacts (Johnson & Hilpert 2013; Johnson 2018). In Serial-3, f_x is the **only** feed into the crawl, and the crawl draining out is the multi-pore-volume shelf; so **f_x > 0 is necessary** for the shelf (set f_x = 0 → no shelf). This distinguishes it from the parallel model, where the crawl was fed from two routes and the separate multiplicative *focus factor* (the 2D η_mult ≈ 2× enhancement) was set to 1 / removed. **Note:** "focus = 1" in the parallel record refers to that enhancement factor, NOT to f_hold; f_hold (parallel) and f_x (serial) are the recruitment/focus *fractions* and are retained and fitted in both models.

## Identifiability status

f_x sits in the {recruitment, v_ns, k_r} collinear cluster. With v_ns pinned (5%), the live trade-off is **f_x ↔ k_r** (both shape the shelf). So f_x is **necessary but its magnitude is weakly identified**; the trends below are supporting/consistency directions, not independent determinations.

## Fitted f_x (quartz on fixed-k_f)

| medium | size µm | v m/d | IS mM | f_x |
|---|---|---|---|---|
| glass | 0.1 | 8 | 20 | 0.0006 |
| glass | 0.2 | 4 | 20 | 0.0052 |
| glass | 0.2 | 8 | 20 | 0.0027, 0.0006, 0.0004 |
| glass | 0.5 | 4 | 20 | 0.0055 |
| glass | 0.5 | 8 | 20 | 0.0038 |
| glass | 1.1 | 4 | 6 | 0.0009 |
| glass | 1.1 | 4 | 20 | 0.0033, 0.0067 |
| glass | 2.0 | 8 | 20 | 0.0039, 0.0046 |
| quartz | 0.5 | 4 | 20 | 0.0268 |
| quartz | 0.5 | 4 | 50 | 0.0397 |
| quartz | 1.1 | 4 | 6 | 0.0034 |
| quartz | 1.1 | 4 | 20 | 0.0029 |

## Trends

**Medium (0.5 µm only — NOT a clean trend).** The elevation is confined to the two Tong 0.5 µm quartz columns (f_x 0.027–0.040, ~5–10× the glass 0.5 µm ~0.005). At **1.1 µm there is no medium effect** — quartz f_x (0.0029, 0.0034) is comparable to, and below, glass at the same size (glass AQ = 0.0067). A genuine angularity / Hamaker mechanism (more grain contacts, deeper |U_sec|) would raise quartz above glass at *all* sizes, which is not observed. So this is best read as a localized feature of the two 0.5 µm columns (Tong-B fair; Tong-H plateau-offset), i.e. **identifiability, not a clean glass-vs-quartz trend.** (Earlier draft over-stated this as "quartz above everything"; corrected per W.P.J.)

**Size (cost-verified — the robust f_x trend).** Small colloids (0.1–0.2 µm) require distinctly small f_x (~4×10⁻⁴–3×10⁻³); ≥0.5 µm cluster higher (~3×10⁻³–7×10⁻³). This is **not** scatter — the pin-vs-free test (below) shows the small-colloid columns cannot tolerate a larger f_x. Mechanistically clean via |U_sec| ∝ radius: small colloids have shallow secondary minima (0.18 kT at 0.1 µm vs 3.55 kT at 2.0 µm, DLVO calc) → poor near-surface capture → little recruitment across grain contacts → small f_x.

**Velocity (murky / second-order).** Only a faint tendency f_x(4 m/d) > f_x(8 m/d) at matched size, buried in scatter. Two pictures predict opposite things:
- *Pure Stokes-flow geometric recruitment* (colloid following the near-wall streamline into a contact): geometry is Reynolds-independent → f_x **velocity-independent**.
- *Secondary-minimum capture vs advective sweep*: the (velocity-independent) |U_sec| well holds the colloid near the surface while drag (∝ v) sweeps it downstream before it reaches a contact → f_x **decreases with velocity**, and by the *same* trap-vs-sweep balance that drives the size/medium trends (|U_sec| = trap, velocity = sweep).

The arrest-race cutoff velocities (v_contact ~22–150 m/d; arrest cutoff ~750 m/d for 1.1 µm — working record) are far above the 4–8 m/d experiments, so any sweep term should be **second-order** here; combined with the f_x↔k_r entanglement, the velocity signal is not cleanly resolvable. **Report velocity as tentative/second-order, not a trend.**

## Pin-vs-free test (decisive; `Code/fx_pin_test.py`)

Glass size series; each column fit with f_x FREE (5 params) vs f_x PINNED to a single constant F = 0.0039 (the free median), with k_f, α_s, α_m, k_r free to compensate. **Source:** all ten `col` identifiers are Excel column letters in the **"Microspheres Glass Beads Tong"** worksheet of `DataFromLi&Tong.xlsx` (unfavorable, pH 6.75, 0.02 M, elution-normalized; glass beads 417–600 µm). Read via `serial3_size_fit.py` / `fx_pin_test.py`.

| col | worksheet (Excel col #) | size µm | v (m/d) | f_x free | cost free | cost pinned | Δ% |
|---|---|---|---|---|---|---|---|
| AX | GB Tong (50) | 0.1 | 8 | 0.0006 | 8.20 | 16.80 | +104.8 |
| E | GB Tong (5) | 0.2 | 4 | 0.0052 | 4.05 | 4.42 | +9.2 |
| BE | GB Tong (57) | 0.2 | 8 | 0.0027 | 3.34 | 3.76 | +12.6 |
| BH | GB Tong (60) | 0.2 | 8 | 0.0006 | 7.80 | 18.99 | +143.4 |
| BN | GB Tong (66) | 0.2 | 8 | 0.0004 | 5.50 | 23.53 | +328.1 |
| O | GB Tong (15) | 0.5 | 4 | 0.0055 | 2.63 | 3.36 | +27.9 |
| BU | GB Tong (73) | 0.5 | 8 | 0.0038 | 1.40 | 1.40 | 0.0 |
| AQ | GB Tong (43) | 1.1 | 4 | 0.0067 | 17.29 | 19.81 | +14.5 |
| CI | GB Tong (87) | 2.0 | 8 | 0.0039 | 1.15 | 1.15 | 0.0 |
| CO | GB Tong (93) | 2.0 | 8 | 0.0046 | 10.82 | 10.91 | +0.9 |
| **Total** | | | | | **62.18** | **104.12** | **+67.5%** |

**Total cost: free = 62.2, pinned = 104.1 → +67.5%** (vs only +9% for a single shared k_r). So f_x is NOT reducible to a constant — it carries real per-column information. ~90% of the excess comes from three small-colloid columns (AX 0.1 µm +105%, BH 0.2 µm +143%, BN 0.2 µm +328%), which require small f_x (4–6×10⁻⁴) and cannot be forced up to 0.0039 even with k_r free; the ≥0.5 µm columns sit near the constant (0–28%). **Conclusion: the size dependence of f_x is required by the data** (small colloids → small f_x), mechanistically the shallow |U_sec| of small colloids. Medium and velocity remain within the scatter.

## Recommended manuscript paragraph

> ⚠ *Superseded 2026‑08‑24 — the +67.5% mixed two velocities. Use the paragraph below it.*
>
> f_x is necessary for the shelf and carries a robust size dependence: pinning f_x to a single constant across the glass size series raises the total cost by +67.5% (vs +9% for a single k_r), driven by the small colloids (0.1–0.2 µm), which require distinctly small f_x. This is consistent with interception focusing gated by secondary-minimum capture — small colloids have shallow |U_sec| and are poorly held near the surface, so are seldom recruited across grain-to-grain contacts (Johnson 2018). Medium and velocity dependences are not clean (the elevated quartz f_x is confined to two 0.5 µm columns and is not reproduced at 1.1 µm; the velocity effect is second-order and entangled with k_r), so we present the size dependence as the mechanistic result and treat medium and velocity as within the identifiability scatter.

**Current version (2026‑08‑24):**

> f_x is necessary for the shelf and carries a size dependence that survives holding velocity constant: pinning f_x to a single constant across the glass size series **at a fixed 8 m/day and 20 mM** raises the total cost by **+31.9%** (n = 8; α_s, α_m and k_r left free to compensate), against **+4.3%** for pinning k_r to one per‑medium constant across all 18 glass columns. The penalty is driven by the small colloids (0.1–0.2 µm), which require distinctly small f_x (≈6×10⁻⁴) and cannot be forced up to the series mean. A parallel test across ionic strength at fixed size and velocity gives **+16.5%** (n = 3). This is consistent with interception focusing gated by secondary‑minimum capture — small colloids and low ionic strength both give shallow |U_sec|, are poorly held near the surface, and are seldom recruited across grain‑to‑grain contacts (Johnson 2018). Medium and velocity dependences remain unclean and are treated as within the identifiability scatter.

*Why the number moved: the superseded +67.5% was computed over a 10‑column set spanning both 4 and 8 m/day, so velocity contributed to the penalty attributed to size. Restricting to one velocity roughly halves it. The contrast that carries the argument — f_x responds where k_r does not, on the same columns — is unaffected and in fact sharpens, since both figures are now on the same corrected objective.*

## f_x vs ionic strength and secondary-minimum depth |U_sec|  (`gl_is_fx.py`, `qz_is_fx.py`, `fx_vs_usec.py`)

**Sources** (`DataFromLi&Tong.xlsx`): glass IS series from **"Microspheres Glass Beads Li"** (GB Li) — cols R=6 mM (18), O=20 mM (15), L=50 mM (12); quartz IS series from **"Microspheres Quartz Sand Li"** (Qtz Li) — cols AK=1 mM (37), AH=3 mM (34), AB=6 mM (28), S=20 mM (19). All unfavorable, 1.1 µm, 4 m/day, elution-normalized.

**IS series (1.1 µm, 4 m/day).** Glass (**α_s fit freely**, k_f anchored to the independent favorable r_s): 6 mM f_x=0.0009 (cost 1.6), 20 mM 0.0023 (9.3), 50 mM 0.0022 (1.8) — rises ~2.5× from 6→20 mM then plateaus; all three fittable (glass retains a shelf even at 6 mM). α_s was formerly *pinned* to the Happel single fraction; freeing it recovers α_s within 2–14% of Happel at equal-or-lower cost with **f_x and the branch unchanged** (robustness note below), so the pin was not load-bearing and there is no circularity from the Happel SCOV having been tuned to the plateau. Quartz (fixed-k_f): 1 mM 0.0014 (18.8), 3 mM 0.0013 (19.2), 6 mM 0.0034 (6.0), 20 mM 0.0029 (0.6) — the **1–3 mM columns barely retain** (C/C₀ ≈ 0.9 / 0.8) and fit poorly (cost ~19), so their f_x is unreliable (no shelf to constrain it). Direction (f_x smaller at low IS) matches |U_sec|, but the low-IS quartz cannot be measured.

**|U_sec| collapse (the unifying view).** Size, IS, and mineralogy all act through the DLVO secondary-minimum depth |U_sec|, so plotting f_x vs |U_sec| (computed per condition; A₁₃₂ glass 7.17×10⁻²¹, quartz 1.96×10⁻²⁰ J; ζ from Johnson 2018) puts the size and IS series on one axis. **f_x rises with |U_sec| and saturates (~a few kT)** — capture-limited recruitment (shallow well → poor near-surface capture → low f_x; deep well → capture saturates). Caveats (shown by the cost color in `fx_vs_usec.png`): substantial scatter in the high-cost points (0.2 µm glass replicates; the two 1.1 µm/20 mM points differ 3× between the Tong and Li studies), and **Tong-B (quartz 0.5 µm) is a ~10× outlier** — so |U_sec| captures the DIRECTION and the saturation, not a tight single curve. **|U_sec| also does not encode VELOCITY** (the sweep side of trap-vs-sweep capture), a hidden variable — so 4 vs 8 m/day points at the same |U_sec| need not coincide.

Data: `fx_trend.xlsx` ('f_x vs IS' and 'f_x vs Usec (DLVO)' sheets). Figures: `fx_vs_IS.png`, `fx_vs_usec.png`.

## Recommended closure f_x(|U_sec|) — **REVISED 2026‑08‑24, reproducer now `Code/fx_trend.py`**

> ### Closure history — four stages, and the current one is the fourth
>
> | stage | f_max | U\* | band | n | status |
> |---|---|---|---|---|---|
> | 1 | 0.0033 | 0.42 kT | ×/÷1.62 | 7 | superseded — fitted while r_s still **floated** within a 0.25 dex window |
> | 2 | 0.0088 | 2.00 kT | ×/÷2.57 | 12 | superseded — arose when **r_s was pinned**; rests on one non‑identifiable point |
> | 3 | 0.0047 | 0.80 kT | ×/÷2.48 | 15 | superseded — correct, but under the retired eq (4) snapshot convention |
> | **4** | — | **UNDER REVIEW** | — | — | **no single value adopted; see below** |
>
> **Stage 3 → 4 (convention), and what it exposed.** The retention profile moved from the eq (4) injection‑window rate snapshot to the **accumulated solid phase at excision** (injection is 2.984 PV of a 10 PV run, so the snapshot ignores 70% of the experiment; retired from `unfav_master_fit.py`, 2026‑08‑25). The convention change turned out to be the *smaller* effect. The closure is **dominated by the degeneracy filter**:
>
> | filter | n | f_max | U\* | RMS |
> |---|---|---|---|---|
> | one‑sided k_r floor — *superseded filter* | 16 | 0.0036 | **0.52 kT** | 0.440 |
> | same, Li.M removed by hand — *superseded* | 15 | 0.0047 | **0.77 kT** | 0.394 |
> | f_x‑identifiability (pin f_x) | 16 | 0.0060 | **0.99 kT** | 0.439 |
> | k_r‑identifiability (pin k_r) | 13 | 0.0061 | **1.20 kT** | 0.421 |
> | k_r‑identifiability, per condition | 10 | 0.0064 | **1.35 kT** | 0.430 |
>
> RMS is 0.39–0.48 throughout: **the data do not choose between these.**
>
> **⚠ A provisional adoption was made and withdrawn, same day.** W.P.J. accepted 0.52 kT on 2026‑08‑25, noting corroboration from pore‑scale mechanistic simulations that put the onset of real secondary‑minimum effect near 0.5 kT. On checking the filter before finalising, **0.52 was found to be an artefact**: under the accumulated convention Li.M's k_r no longer rails at the 1e‑6 floor — it flies to 5.63e‑3 at unchanged cost — so the one‑sided floor test stopped catching it and it re‑entered the closure at |U_sec| = 6.57 kT, the deepest well in the set, carrying f_x = 0.00055 against its own replicates at the identical |U_sec| (Li.P 0.00427, Li.S 0.00151). One non‑identifiable point at the deep end pulled the plateau down and shortened U\*. Removing it *improves* the RMS (0.440 → 0.394).
>
> **This is the third time Li.M has corrupted this closure through the f_x↔k_r degeneracy** — it is the column behind the retired 2.00 kT stage‑2 result as well, in the opposite direction. The filter is now two‑sided (identifiability, not which bound the parameter drifted to), matching `kr_trend.py`.
>
> **The agreement with the pore‑scale number was a coincidence of a contaminated fit.** That is exactly the circumstance in which an external corroboration is most dangerous: it made a wrong number look right. Recorded deliberately.
>
> **Stage 1 → 2 (mechanism, accepted).** Per W.P.J.: the revision came about when r_s was pinned to the favorable‑condition anchor instead of floating within 0.25 dex. That changes the fitted f_x values *themselves*, not how they are filtered afterwards — with r_s free, r_s absorbed part of the retention f_x must now carry, and did so unevenly across |U_sec| (the shallow‑well columns had the most room to trade), so pinning r_s moved f_x and the closure stretched.
>
> **Stage 2 → 3 (number, rejected).** Refitting stage 2's own published 12 points reproduces it *exactly* — f_max 0.0088, U\* 2.00, RMS 0.411, ×/÷2.57 — which is also the validation that the current fitter is correct. But leave‑one‑out on that same set shows the whole result is carried by a **single point, Li‑Qtz20**: removing it gives f_max 0.0038, U\* **0.59 kT**, i.e. collapse back to stage 1. The next largest single influence, CI, only moves U\* to 1.51 kT. In the current per‑column fits that condition's elevated f_x comes from **column Li.M, whose free k_r sits on the 1e‑6 optimiser bound** (f_x = 0.21 at cost 0.72) — the f_x↔k_r degeneracy, not a measurement.

**Current closure.** Two filters, both principled, no by‑name exclusions: (1) fit cost ≤ 15; (2) free k_r > 1.5×10⁻⁶ /s. Filter (2) is the point: a column with k_r pinned to its lower bound is degenerate in the f_x↔k_r pair, so f_x absorbs everything and its value is meaningless — and such a fit earns a *low* cost, so filter (1) cannot catch it. It is the **same threshold `kr_trend.py` already uses** for its clean k_r geomean, applied to the other member of the same degenerate pair. It removes Li.M and Tong.U. Tong‑B is no longer excluded by name as the old scripts did ("~10× outlier"); it passes on its merits (cost 2.43).

> **f_x = f_max · (1 − exp(−|U_sec|/U\*))** — the SHAPE is the result. **f_max ≈ 0.004–0.006, U\* ≈ 0.8–1.4 kT** across defensible filters under the accumulated convention.

**What to quote.** The shape — f_x rises with |U_sec| and saturates, with the size and IS series on one curve — is robust across every variant tried, including all five in the filter table above. The saturation **scale** is not. Quote the closure as a shape with a band and a range for U\*; do not quote a value. This was already the standing advice in this record before stage 4, and stage 4 strengthens rather than changes it: the stage‑3 bootstrap CI was **[0.05, 10.4] kT**, and the filter sensitivity now adds a systematic spread of comparable importance to that statistical one.

The stage‑3 predictions below (0.2 kT → 0.0011, etc.) are superseded and should be recomputed once a filter is settled.

**What is and is not established.** Robust across *every* variant tried: f_x **rises with |U_sec| and saturates**, with the size and IS series on one curve. **Not** established by this dataset: the saturation **scale** (0.6–2 kT across defensible variants) or the plateau **height** (0.004–0.009). Quote the closure as a shape with its band; do not quote U\* as a precise number.

### How well is U\* actually determined? (added 2026‑08‑24, in answer to "are we comfortable with it?")

> **These two tests were run on the stage‑3 (0.80 kT, n=15) fit under the retired snapshot convention and have NOT been re‑run under accum.** Their *conclusions* carry over — leave‑one‑out robustness and a very wide bootstrap interval are properties of the data density, not of the convention, and stage 4 moved U\* by less than a third of the leave‑one‑out spread. The *numbers* below are stage 3's.

Two tests, and they point in opposite directions. Both are worth stating because quoting either alone would mislead.

**Test 1 — leave‑one‑out. 0.80 kT PASSES the test that retired 2.00 kT.** Removing any single point from the 15 shifts U\* by at most 0.31 kT:

| point removed | f_max | U\* | shift |
|---|---|---|---|
| Tong.E | 0.0049 | 1.10 | +0.31 |
| Li.S | 0.0060 | 1.09 | +0.30 |
| Tong.B | 0.0036 | 0.53 | −0.26 |
| Tong.BH | 0.0046 | 0.60 | −0.20 |
| *(all others)* | — | 0.62–0.96 | < 0.18 |

Compare stage 2, where removing **one** point moved U\* from 2.00 to 0.59 — a shift of −1.41, four times the worst case here. So the objection that retired the 2.00 kT closure does **not** apply to 0.80 kT. That distinction is earned, not assumed, and it was tested deliberately: applying leave‑one‑out to the closure we wanted to keep, having used it to reject the one we did not, is the minimum standard of fairness.

**Test 2 — bootstrap. The VALUE is barely determined at all.** 2000 resamples of the 15 points:

- U\* median **0.79 kT**, 68% CI **[0.33, 1.55]**, 95% CI **[0.05, 10.4]**
- f_max median 0.0046, 95% CI [0.0025, 0.0403]
- **9% of resamples give U\* > 2.0 kT**; 17% give U\* > 1.5 kT.

The 95% interval spans more than two decades. That is what a ×/÷2.48 scatter band on 15 points buys — and the scatter is not confined to the deep end: at |U_sec| ≈ 0.355 kT alone, Tong.E and Tong.BH differ by 13× in f_x.

**Consequences, and they matter for how this is written up:**

1. **Quote U\* as "sub‑kT to a few kT", never as a number.** Stage 4 makes this stronger, not weaker: five defensible degeneracy filters give 0.52, 0.77, 0.99, 1.20 and 1.35 kT at essentially the same RMS. There is no third significant figure to argue about — there is barely a first. The shape is what the data support.
2. **The apparent conflict with `part2_apriori_alpha_machinery.md` §87 is NOT a conflict.** The ~2 kT expectation sits comfortably inside the 95% interval, and 9% of resamples land above it. These data lack the power to contradict 2 kT. The earlier framing in this record and in `fx_trend.py` — "does not support" the machinery, a disagreement "left standing" — was too strong in our own favour; it implied the fit had ruled something out when it had not. **The correct statement is that the fitted closure cannot discriminate between ~0.8 and ~2 kT, so the a‑priori value may be used without contradicting the fits.**
3. This does not rehabilitate stage 2. The 2.00 kT *point estimate* was still driven by one non‑identifiable column; what changes is that 2 kT as a *physical expectation from independent reasoning* is not excluded by the data.

**Two dependencies to keep visible.**

- The old cost ≤ 3.5 cut cannot be rehabilitated: on current fits it leaves n = 4 and drives U\* onto its 0.05 kT lower bound. It is unusable, not merely different.
- `part2_apriori_alpha_machinery.md` §87 expects grain‑contact transfer g to saturate by **~2 kT**. That was cited as independent support for stage 2 and it does **not** support the reported stage‑3 closure. The disagreement is left standing rather than dropped now that it points the other way. If the ~2 kT expectation is right, the reading is that the fitted f_x cannot resolve the deep end — not that the machinery is wrong.

Data + parameters + the leave‑one‑out table: 'f_x(Usec) closure' sheet of `fx_trend.xlsx`. Figure `fx_vs_usec.png` now plots all three closures with the two degenerate points ringed and labelled.

## Caveats for the writeup

- Present **size and medium** as the mechanistic trends (trap depth |U_sec| + angularity); treat **velocity** cautiously.
- The quartz elevation rests on the two Tong 0.5 µm columns (Tong-B fair; Tong-H good tail/RP but plateau-offset cost) — real but from limited data.
- f_x is a *supporting* consistency argument, not a load-bearing determination; the shelf magnitude is carried jointly by f_x and k_r.
