# Reentrainment k_r — size / IS / velocity independence, and the RFSP reading (record)

**Reproducer:** `Code/kr_trend.py` → `k_r_trend.xlsx` (sheets: k_r fitted, reference constants, DLVO‑Kramers curve, k_r necessity) + `new_kr_vs_size.png`, `new_kr_vs_IS.png`, `new_kr_vs_velocity.png`. Engine + data via `Code/unfav_master_fit.py` on `Data/LiTong_experimental_data_tidy.csv`. DLVO/Kramers physics from `Code/dlvo_kramers_size.py`. Companion: `Code/fx_trend.py` (focusing f_x, the |U_sec|‑driven contrast).

**Fit setup (current):** Serial‑3 with r_s **fixed** at the favorable interception anchor; α_s / α_m / f_x / **k_r free per column**; v_ns 5%; BTEC floored at −6; IS ≤ 1 mM dropped. k_r here is the crawl→wall release (reentrainment) rate, in /s.

> ## ⚠ HEADLINE NUMBERS, CURRENT AS OF 2026‑08‑25 — read this before quoting anything below
>
> The **accumulated‑profile refit** and the **two‑sided identifiability filter** (both 2026‑08‑25) moved every constant in this record. The current values, derived from `k_r_trend.xlsx` by `Code/check_consistency.py`:
>
> | quantity | CURRENT (08‑25) | superseded (08‑24, quoted throughout the sections below) |
> |---|---|---|
> | glass constant | **3.75×10⁻⁵ /s** (n = 14) | 4.46×10⁻⁵ /s (n = 17) |
> | quartz constant | **1.82×10⁻⁵ /s** (n = 6) | 2.09×10⁻⁵ /s (n = 10) |
> | ratio | **2.06×** | 2.13× (superseded) |
> | pinning penalty | **+4.8% glass / +0.9% quartz** | +4.3% / +0.8% |
> | canonical drop‑it excess | **+1.7%** total, +4.0% median | +2.5% total, +4.2% median (superseded) |
>
> Two changes did this. (i) The exclusion rule is no longer a **floor test** (`k_r ≤ 1.5×10⁻⁶`) but a **two‑sided pinning‑penalty test** (`PEN ≥ 1%`): a column whose cost barely moves when k_r is pinned carries no information about k_r and cannot vote on its value, whether its k_r railed *down* or flew *up*. Under accum, Li.M's k_r stopped railing at 10⁻⁶ and flew to 5.6×10⁻³ at unchanged cost — invisible to a floor test. The new filter excludes 9 of 29 columns rather than 2, which is why every n below is smaller. (ii) The retention profile is now the **accumulated solid phase at excision**, not the eq (4) injection‑window snapshot.
>
> **The conclusions are unchanged**: k_r is a per‑medium constant, the medium offset is ~2×, quartz sits below glass, and no size / IS / velocity dependence is resolvable. Only the digits moved. The sections below are kept because they record *why* each correction was made and what it cost.

> **NUMBERS REVISED 2026‑08‑24 (W.P.J.).** Everything below is on the **corrected objective**: mean‑log plateau target (PV 1.2–4, ±0.25 dex, W_PLAT = 20) replacing the superseded dead‑zone band, plus the branch‑aware RP‑shape inlet window (`plateau_rs_decision.md` §6). `kr_trend.py` had been running the dead‑zone while `unfav_master_fit.py` ran the mean‑log target, so this record and the script's own docstring had drifted apart and disagreed with each other — which is how the drift was caught. The stale sets were: this record +4.2% / +1.9%, 4.5e‑5 / 1.45e‑5, 3.1×; the docstring +4.3% / +0.5%, 4.5e‑5 / 2.0e‑5, 2.3×. **Neither is reproducible.** Both are replaced below by numbers re‑run on all 29 columns and cross‑checked by an independent reimplementation (`kr_check.py`) that agreed to every printed digit.

## Result — k_r is a per‑medium constant — digits as of 2026‑08‑24, SUPERSEDED, kept for the audit trail

**Necessity test (`k_r necessity` sheet).** Pinning k_r to a single per‑medium constant (vs free per column, α_s/α_m/f_x still free to compensate), across ALL columns (every size, velocity, IS):

- **Glass: +4.3%** total cost (n = 18; free 400.3 → pinned 417.6).
- **Quartz: +0.8%** total cost (n = 11; free 334.1 → pinned 336.7).

A single per‑medium constant suffices — tighter than the earlier +9%, and on quartz the penalty is now essentially nil. So k_r carries **no** resolvable size, IS, or velocity dependence.

**Fair per‑medium constants** (geometric mean of the free fits, excluding fit‑floor hits, k_r ≤ 1.5×10⁻⁶): **glass 4.46×10⁻⁵ /s (n = 17), quartz 2.09×10⁻⁵ /s (n = 10)** — quartz **2.13× below** glass.

Two corrections to how that ratio used to be formed:

- **The floor‑hits are one per medium, and they are not both at 50 mM.** They are glass 0.5 µm **50 mM** (column U) and quartz 1.1 µm **20 mM** (column M), each pinned at the 10⁻⁶ lower bound. The old phrase "the two 50 mM floor‑hits" was wrong about the quartz one.
- **The exclusion used to be applied to glass only** — `kr_trend.py` computed `Fg_clean` but no `Fq_clean`, and formed the ratio as clean‑glass over all‑quartz. That is a clean numerator over a dirty denominator. Fixed 2026‑08‑24; the workbook now reports both, and **2.13× (clean/clean) is the figure to quote**. The asymmetric form gives 2.81× and is retained in the sheet only so the difference stays visible.

(Including all points the glass geomean drops to 3.61×10⁻⁵ and quartz to 1.59×10⁻⁵. The necessity **pin** deliberately uses these all‑column geomeans, not the clean constants — the penalty must not be helped by dropping points. Old necessity‑fit values were glass 5.58×10⁻⁵, quartz 1.87×10⁻⁵. All values on the current fits: mean‑log plateau rule + corrected R/O C0 = 8.2×10⁶.)

**Per axis:**
- **Size** — flat across 0.1–2.0 µm. The classical single‑colloid DLVO/Kramers escape from the secondary minimum predicts a **584×** rate swing over that range (steep, ∝ e^(−|U_sec|), |U_sec| ∝ radius); the data are flat → **refuted**.
- **Ionic strength** — ⚠ **revised 2026‑08‑24, and the earlier "flat 3–20 mM" was an artefact of a clipped axis.** The figures had `ylim` starting at 3×10⁻⁶, which silently cropped the two columns sitting on the 10⁻⁶ optimiser bound (glass 0.5 µm/50 mM **U**, quartz 1.1 µm/20 mM **M**). With the axis opened to 5×10⁻⁷ those points appear and the picture changes for quartz: **quartz 1.1 µm declines ~6× in geometric mean across 3 → 20 mM** (2.7×10⁻⁵ → 1.7×10⁻⁵ → 4.1×10⁻⁶), and its floor‑hit is at **20 mM, not 50**. Excluding the degenerate M column it is still a ~3× decline (2.7×10⁻⁵ → 8.4×10⁻⁶). **Glass** does behave roughly as described: ~flat to 20 mM, then a drop at 50 mM (L → 4.1×10⁻⁶, U at the floor).
  - This is **compatible with the +0.8% quartz pinning penalty** — a spread that noisy, on 11 columns with a ~decade of scatter, is absorbable by a single constant — but the two statements must be kept straight. The *necessity test* is the quantitative claim and it stands; "flat" was a description of a figure, and the figure was hiding points. Do not re‑assert flatness for quartz. **Correction:** the 50 mM points are *no longer* the only sizeable pinning penalties. Ranked: quartz Tong.B (0.5 µm, 20 mM) **+51.3%**, glass Li.L (1.1 µm, 50 mM) +33.7%, glass Tong.AK (1.1 µm, 20 mM) +18.4%, quartz Li.P (1.1 µm, 20 mM) +15.6%, glass Tong.U (0.5 µm, 50 mM) +15.6%. Tong.B is the largest single penalty in the set and it is a 20 mM column — the earlier "only the 50 mM points" claim must not be repeated. Tong.B is also the one column where the fitted and measured RP branches disagree (`aplat_plateau_alpha.md` §6), so its k_r is the least well determined in the set, and it is a single column: it does not establish an IS trend, but it does remove the tidiness of the old statement.
- **Velocity** — no strong dependence (folded inside the +4.3%). A **faint hint k_r(8 m/d) > k_r(4 m/d)** in both matched‑size glass pairs (0.2 µm 2.9→6.2×10⁻⁵; 0.5 µm 1.6→5.7×10⁻⁵) — both unchanged by the correction. Underpowered: single columns at 4 m/d.

## The contrast that carries the argument

f_x and k_r are fit from the **same columns over the same |U_sec| span** (~0.18–6.6 kT). Over that identical range **f_x rises ~an order of magnitude and organizes on |U_sec|** (capture‑limited focusing; see `fx_trend_analysis.md`), while **k_r stays flat** at its per‑medium constant. This is a within‑dataset control: the same scatter that leaves f_x's trend resolvable leaves no k_r trend. So focusing (recruitment into the crawl) and reentrainment (release) have **different drivers** — focusing is |U_sec|‑driven, reentrainment is not.

## Reading — release by RFSP expulsion, not DLVO escape

k_r shows **no |U_sec| signature on any axis** (size, IS, and an IS‑independent glass/quartz offset), and the DLVO/Kramers escape magnitude/slope is refuted. This points to a **flow‑structural** release: hydrodynamic **expulsion at the rear flow stagnation point (RFSP)** of the grain, consistent with direct pore‑scale observations. Then:

- the **~2.1× glass/quartz offset** reflects grain **angularity / RFSP geometry** (quartz sand vs glass beads), not Hamaker or double‑layer screening (which would move with IS — it doesn't). Note the offset is now **smaller** than the 3.1× this record previously carried, so it is a weaker quantitative hook than before; the qualitative point (a medium‑level, IS‑independent offset) is what survives;
- the **faint k_r‑vs‑velocity rise**, if real, is the **advective signature** RFSP expulsion predicts (release scales with the sweeping flow), whereas DLVO escape would be velocity‑independent. So it leans toward the mechanism rather than against it.

## What k_r actually buys — the drop‑it test on the canonical five (digits SUPERSEDED; see the box)

> **The block sums and per‑column excesses in this section are the FIRST (snapshot‑convention) run and are SUPERSEDED.** The section is kept because its *reading* — where the penalty lands — is the point, and that reading is unchanged. Current values, from `canon_nokr_stats.json`: total **343.09 → 349.00, +1.7%**; per‑column median **+4.0%**; blocks RP level **−0.36**, RP shape **−2.53**, plateau 0.00, tail level **+6.88**, tail slope **+1.92**; Li.S **+95%** (0.403 → 0.786); Li.M **+0.03%** (it read −0.3% under the snapshot, which is impossible for a nested pair and is what exposed the local optimum — cross‑seeding now prevents it).

Asked (W.P.J.) whether `fit_canonical_IHOP.png` had been run with and without k_r, mirroring the original **Serial‑3a (no k_r) / Serial‑3b (+k_r)** pair. It had not — the figure is drawn from `UnfavorableMaster.xlsx`, which stores only the 4‑parameter fits. The comparison has now been run under the current objective: `Code/canon_nokr_fit.py` → `fits_canonical_IHOP.xlsx`, `canon_nokr.json`, and the grey dashed overlay on `fit_canonical_IHOP.png`.

**"No k_r" means a REFIT**, as in the original `serial_model.py` (`setup(..., use_kr)`): k_r is dropped from the parameter vector and α_s, α_m, f_x are refitted. Holding the other three at their +k_r values would measure how much the model breaks when a parameter is vandalised, not whether the parameter is needed — the whole content of a necessity test is what the surviving parameters can absorb. Five conditions, **ten Li columns** (V=AB/V/Y, P=M/P/S, AE=AE/AH); each column fitted separately, the plotted line is the mean of the per‑column curves.

**Result — the effect on fit quality is MODEST.** Total cost over the ten columns 295.80 → 303.34, **+2.5%**; per‑column median **+4.2%**. Do not oversell this.

**Where the penalty lands is the informative part** (block sums over the ten columns):

| block | +k_r | no‑k_r | Δ |
|---|---|---|---|
| RP level | 15.52 | 14.89 | **−0.63** |
| RP shape | 275.23 | 274.59 | **−0.63** |
| plateau | 0.00 | 0.00 | 0.00 |
| tail level | 4.45 | 11.39 | **+6.94** |
| tail slope | 0.61 | 2.46 | **+1.86** |

The entire penalty is in the **elution tail**; the retention profile very slightly *improves* without k_r, because α_s/α_m/f_x are freed from having to serve the tail. That is exactly the role `Serial-3-record.md` §3 assigns k_r — an elution term orthogonal to the schematic's attachment structure — and it is why the grey dashed curve departs from the solid line only after injection stops and is **invisible under it in every RP panel**. f_x rises 20–60% when k_r is removed (Li.R 0.00066 → 0.00089); α_s barely moves.

**Two numbers that must not be quoted naively.** Li.S has the largest excess (+87%) but the smallest absolute cost (0.437 → 0.817) — a large percentage on a tiny denominator. Li.M shows **−0.3%**, i.e. no‑k_r nominally beating +k_r; its fitted k_r rails at the 10⁻⁶/s floor, so the two are the *same model* there and the sign is optimiser noise. Read |excess| below ~0.5% as indistinguishable.

*Two defects found and fixed in this exercise, both in my own first pass:* (i) railing was tested as a fixed distance in the log₁₀ search coordinate, which flags α_s as railed whenever α_s ≲ 4.5% because p₀ = log₁₀(1−α_s) crowds its bound — five false positives, including α_s = 0.0158, which is 158× its lower bound; now tested on the natural parameter against its own bound. (ii) The +k_r model *nests* the no‑k_r model, so cost(+k_r) ≤ cost(no‑k_r) must hold; the first run violated it on Li.M, proving a local optimum rather than a model result. Each fit is now also seeded from the other variant's solution. The +k_r fits reproduce `unfav_master_fit.fit_col` **identically on all ten columns**, and with nesting enforced no column improved — the master multistart was already at its optimum.

## These constants feed the favorable fits — the r_s ↔ k_r loop

The per‑medium constants are **not** an endpoint: `favorable_both_models.py` Model 2 **pins k_r to them** so that f_x can be fitted free (pinning one member of the f_x↔k_r pair is what makes the other identifiable). Model 2 then yields r_s, which `unfav_master_fit.py` pins as `FAVFIT` — closing the loop back to the fits that produced these constants.

**So changing k_r here changes the favorable fits, and in principle r_s and hence the unfavorable α values.** The 2026‑08‑25 accum refit + two‑sided filter moved these constants ≈0.07 dex (glass 4.46→3.75e‑5, quartz 2.09→1.82e‑5), which means **Table 5's favorable fits are pinned to superseded values**. W.P.J. decided on 2026‑08‑25 not to iterate the loop, and the reasoning — two independent damping mechanisms, plus the wording consequence for calling r_s "independent" — is recorded in `plateau_rs_decision.md` §3b. **Read that before quoting these constants as inputs to anything.**

## Caveats

- **Null result.** "No dependence" rests on the necessity penalty (**+4.8% glass / +0.9% quartz**, current); the f_x contrast supplies the power argument (same columns, same |U_sec| range, one parameter responds and one doesn't).
- **Floor‑hits.** Glass 0.5 µm/50 mM (U) and quartz 1.1 µm/20 mM (M) pin at the 10⁻⁶ lower bound; glass 1.1 µm/50 mM (L) is near it at 4.1×10⁻⁶ but above the 1.5×10⁻⁶ exclusion threshold and is kept. So the high‑IS drop is partly a bound artifact, and the fair constants exclude U and M — one per medium, symmetrically.
- **Quartz's small penalty (+0.9% current, +0.8% as first written) is not strong evidence of flatness on its own.** Eleven quartz columns span a narrower size range (0.5 and 1.1 µm only) than the glass set, so a small penalty there partly reflects a short lever arm. The size refutation rests on glass, which spans 0.1–2.0 µm.
- **Velocity underpowered.** Two size groups, single 4 m/d columns — the velocity hint needs more 4 m/d data before it can be claimed.
- **The necessity penalty is small in absolute terms** (**+1.7%** on the canonical five; **+4.8%/+0.9%** on the full glass/quartz sets — all current). k_r earns its place by *what* it buys — the elution tail, which nothing else in the model can produce — not by how much it lowers the cost. Any claim phrased as "k_r substantially improves the fit" is wrong.
- k_r is in the {f_x, v_ns, k_r} collinear cluster; with v_ns pinned and f_x free, the per‑column k_r is noisier than the constant it averages to (~a decade of scatter), which is exactly why the constant + necessity test, not the individual values, carry the claim.
