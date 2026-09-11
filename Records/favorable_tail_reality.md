# Favorable fits — is the multi-PV tail real? (record)

**Reproducers:** `Code/favorable_both_models.py` → `Favorable_data_and_sim.xlsx` (Table 4, Table 5, per-column BTEC+RP data & model curves) + `favorable_MI_table.json`; `Code/favorable_tail_clean.py` → `favorable_tail_clean.png` (5 representative columns, two-panel); `Code/favorable_tail_SI.py` → `favorable_tail_SI.png` (the OTHER 5 fitted columns — CS, O, Glass Li B/E/H — for the SI). Data: `DataFromLi&Tong.xlsx` (C0 provenance in `data_inventory.md`).

**Favorable "condition" columns** in Tables 4/5 read **"favorable via" = pH 2 (Tong) / aminated colloids (Li)**, NOT ionic strength — favorability here is set by pH/surface chemistry, and the columns' IS (50 mM Tong, 10 mM Li) is incidental (50 mM is also an *un*favorable IS elsewhere, so quoting it was misleading). W.P.J., 2026-08-20.

**r_s band:** free within **±0.6 dex** (factor ~4) of the plateau/RP-slope seed. (Widening from ±0.4 changed nothing — r_s was already interior at every column; the residual bound-hits are in f_x and α_m, i.e. attachment, not delivery.)

## Question and setup

Under favorable chemistry the classical picture is pure clean-bed filtration (k_f only, no tail). But the BTECs carry a real multi-PV shelf (~10⁻⁴, well above the ~10⁻⁵ blank — `data_inventory §4b`). **Does that tail require the interception-history crawl, or can k_f-only explain it?**

Test on the **10 favorable columns that carry BOTH a BTEC (≥3) and an RP (≥3)**: GB Tong L, AB, CS; Qtz Tong O; Qtz Li B, E, I; GB Li B, E, H. (The three RP-only Tong columns — B, AU, BB — have no BTEC and stay k_f-only.)

- **PINNED:** k_r to the per-medium constant from the size series (glass 5.58×10⁻⁵/s, quartz 1.87×10⁻⁵/s — the values in force when these fits were run, and **since superseded twice, now 3.75×10⁻⁵ / 1.82×10⁻⁵**; W.P.J. decided 2026‑08‑25 not to iterate the r_s ↔ k_r loop, so Table 5's favorable fits remain pinned to these superseded constants — see `plateau_rs_decision.md` §3b); v_ns = 5%. k_r is the ONLY pinned kinetic parameter — pinning it breaks the f_x↔k_r degeneracy, so f_x can be free.
- **FREE:** delivery r_s (within ±0.4 dex — a factor ~2.5 — of the plateau/RP-slope seed, so the RP slope can set delivery), single-interception α_s (via the MI fraction 1−α_s), crawl attachment α_m, recruitment f_x.
- **Objective:** joint BTEC + RP — RP level (W_RP=6) + two-segment RP slope (W_SH=2.5) + BTEC (W_BT=3). RP **amplitude is FIXED by C0** (never floated / offset-aligned), per `data_inventory §0`.

## Result — the tail is REAL

**Table 4 (tail reality).** The k_f-only model misses the tail by 5–8 log-RMS; adding the multiple-interceptor crawl (k_r pinned) drops it to 0.1–0.3. The Fit Ratio (tailRMS k_f-only → full) is the headline:

| col | (1−α_s) MI | α_m | f_x | r_s_fit /m | Fit Ratio (kf→full) |
|---|---|---|---|---|---|
| GB Tong L | 0.0385 | 0.473 | 0.041 | 47.5 | 5.11 → 0.148 |
| GB Tong AB | 0.0255 | 0.246 | 0.0069 | 30.2 | 6.96 → 0.156 |
| GB Tong CS | 0.0155 | 0.90* | 0.10* | 15.2 | 7.14 → 0.245 |
| Qtz Tong O | 0.0225 | 0.393 | 0.10* | 56.7 | — (no tail region) |
| Qtz Li B | 0.0042 | 0.107 | 0.0005 | 120.6 | — (no tail region) |
| Qtz Li E | 0.0055 | 0.262 | 0.0126 | 62.3 | 6.49 → 0.243 |
| Qtz Li I | 0.402 | 0.465 | 0.0061 | 68.9 | 7.24 → 0.105 |
| GB Li B | 0.0059 | 0.0005* | 0.0085 | 57.9 | 7.19 → 0.328 |
| GB Li E | 0.0066 | 0.0005* | 0.0078 | 28.8 | 6.96 → 0.154 |
| GB Li H | 0.0414 | 0.0005* | 0.0021 | 29.8 | 7.64 → 0.261 |

`—` = BTEC does not extend past 4.2 PV, so no tail region to score. `*` = at a fit bound.

**Table 5** carries the full parameter set (r_s_fit, r_s_seed, α_s, MI%, α_m, f_x, k_r/PV, tail RMS, RP RMS) — see the workbook.

## Caveats — read the Fit Ratio, not the individual params

Favorable columns have little curvature, so the 4-free-parameter joint fit is **under-constrained** in places: f_x pins to its 0.1 upper bound (CS, O) and α_m to a bound (CS 0.9 upper; GB Li 0.0005 lower). r_s is **interior at every column** — widening the band to ±0.6 dex changed nothing. **The tail-reality conclusion (huge Fit-Ratio drop) is robust; the bounded α_m/f_x are consistency, not determinations.**

**⚠ NOT a bound-hit — a real result:** Qtz Li I (8 m/d) α_s = 0.598 (MI 0.40) is *below* the 0.50 MI cap, i.e. interior, and has the **tightest fit in the favorable set** (rpRMS 0.024, tailRMS 0.105). It is a genuine velocity effect (below), not an artifact. (An earlier draft wrongly listed it among the bound-hits.)

## Velocity effect on α_s (Li 0.98 µm favorable velocity series, 2/4/8 m/day)

α_s (single-interception attachment) **falls with pore velocity** (W.P.J., 2026-08-20):

| medium | 2 m/d | 4 m/d | 8 m/d |
|---|---|---|---|
| **Quartz Li** (B/E/I) | 0.996 | 0.995 | **0.598** |
| Glass Li (B/E/H) | 0.994 | 0.993 | 0.959 |

Flat at ~0.995 through 4 m/d, then a drop at 8 m/d — **large for quartz, mild for glass**. The quartz 8 m/d point is the best-constrained fit in the favorable set (rpRMS 0.024), so the effect is well-supported, not fit noise. Mechanism: **trap-vs-sweep** — higher velocity sweeps more colloids past before they arrest, lowering single-interception attachment — the same balance behind the f_x recruitment and the |U_sec| size trend, now on the velocity axis. Significant but not huge (α_s still 0.60 at 8 m/d; the majority still attach on first interception). Worth a sentence in the manuscript as the velocity signature of α_s, distinct from the murkier velocity dependence of f_x.

## CFT cross-check — fitted r_s vs correlation collision-rate r_s (`cft_rs_compare.py`)

Cross-check of the fitted **interception** r_s against classical single-collector filtration theory, using the 5 correlations in the colleague's tool `Data/CorrelationEqs3.py` (RT 1976, TE 2004, MPFJ 2015, NG 2011, LH 2011). r_s convention = the tool's kf/U: **r_s = −(3/2)(γ/dp)·ln(1−η₀)**, γ=(1−θ)^(1/3), dp=510 µm. Inputs: ρ_c=1055, ρ_f=998, µ=9.8e-4, T=298.2 (tool defaults), θ glass 0.375 / quartz 0.36; **correct A₁₃₂** (glass 7.17e-21, quartz 1.96e-20 J) primary — the tool's default 3.84e-21 is outdated (`data_inventory §6`), shown as a reference block.

**Result:** fitted r_s lands within the 5-correlation envelope for every column (the correlations span ~2–3× among themselves). **Glass** sits mid-envelope (fit ≈ 0.6–1.0× MPFJ). **Quartz** runs at/above the top — Qz Li 8 m/d ≈ 2× MPFJ, above even LH — consistent with **angular quartz intercepting more than smooth-sphere theory predicts** (independent support for the angularity argument). The correlations predict η (hence r_s) falling ~2× from 2→8 m/d; the fitted quartz r_s falls less, and the 8 m/d point is high vs CFT, reflecting the r_s↔α_s trade at high velocity (same column where α_s dropped to 0.60). Deliverables: `CFT_rs_comparison.xlsx` (correct-H + tool-default-H blocks), `cft_rs_compare.png` (fitted vs MPFJ with the 5-correlation range as x-error bars, 1:1 line).

## C0 provenance fix (2026-08-20)

The favorable loader had read C0 from the wrong place, and an offset-alignment patch had hidden it (W.P.J. caught this — "stop and check in on such discrepancies"). Corrected:
- **C0 row map** (`data_inventory §4`): row **14** for `Microspheres Glass Beads Li`, row **8** for the other three sheets. Read the C0 *cell*, never scrape header text (numeric C0 has no "E" to regex).
- **CS and O have no C0 in the sheet.** Set to the **RP-implied, mass-balance-closing** C0 (CS 1.157×10⁶; O **8.2×10⁶** — updated 2026-08-23 to match its unfavorable twin R, the same run; was 5.762×10⁶). The 3.36×10⁵ placeholder was ~3× / ~17× low and is rejected wherever it appears (incl. R's recorded cell). Amplitude FIXED (`C0_OVERRIDE`). O's fitted r_s is robust to this (56.9 → 56.7; r_s set by the C0-independent RP slope).
- Offset-alignment patch removed; C0 is now always real and the RP amplitude is never floated.
