# HYDEQ → HYDRUS-1D forward cross-check: setup sheet

*For N. Willis. Rewritten 2026-08-25 (W.P.J.) — see §8 for what changed and why.*

---

## 1. The one question this exercise answers

**Does HYDRUS-1D, given the same parameters, produce the same curves as our HYDEQ reimplementation?**

That is a **code-correctness check on a forward run**. Parameters go in; curves come out; the curves are compared. Nothing is fitted. If the reimplementation were wrong, the conventional model structures would fail for the wrong reason and the whole comparison in `hydeq_comparison_record.md` would be worthless — so this check has to pass before any of that means anything.

**Explicitly NOT part of this exercise:**

- **Not** "does HYDRUS fit the data as well as HYDEQ does" — no fitting happens here.
- **Not** "does HYDRUS's optimiser also drive k_str to its lower bound" — see §7. That is a genuinely interesting question and it is deliberately excluded, because it cannot be made into a clean test.
- **Not** the dual-porosity structure — see §2.

## 2. What to run, and what not to

| structure | HYDRUS-1D setup | in this exercise? |
|---|---|---|
| **Two kinetic sites, attachment and detachment** | two kinetic sites, each with k_a and k_d | **YES — this is the task** |
| One kinetic site (irreversible) | one kinetic site, k_a only, k_d = 0 | optional smoke test |
| One kinetic site + depth-dependent straining | kinetic site + straining, ψ(x) = ((d50+x)/d50)^(−β) | later, if the two-site check passes |
| + Langmuir blocking | as above with the s_max term on site 1 | later |
| Dual porosity / mobile–immobile | — | **NO. Do not attempt.** |

**Why the two-site structure is the right one to start with.** All four rate coefficients are active, so attachment and detachment are both exercised on two independent sites — that is the core of the kinetic machinery and the part most likely to harbour an implementation error. There is no straining term, so no ψ(x) question rides along; the system is linear, so it is reproducible exactly; HYDRUS-1D supports two kinetic sites natively with no mapping argument required. And — checked rather than assumed — **no two-site fit rails a parameter to a bound on any of the five columns**, so these are genuine fitted values, not optimiser artifacts sitting on a limit.

**Why dual porosity is excluded.** The HYDEQ "dual porosity" is a *population* split in which the slow population **advects at 0.05·v**. HYDRUS-1D's standard two-region module gives the second region **zero velocity**, and its exchange term equilibrates *concentrations* whereas HYDEQ's equilibrates a *population fraction*. The nearest analogue is the dual-permeability formulation, and even that is not a term-by-term match. A disagreement would tell us nothing about either code. If we want that structure verified it needs its own exercise.

## 3. Column setup — identical for every run

| quantity | value | note |
|---|---|---|
| column length L | 0.2 m (20 cm) | |
| pore velocity v | 4 m/day | all five columns |
| porosity θ | 0.375 glass / 0.360 quartz | |
| bulk density ρ_b | 1.656 g/cm³ glass / 1.696 g/cm³ quartz | (1−θ)·2.65 |
| dispersivity α_L | **0.133 cm** | from Pe = vL/D = 150. Enter as α_L, **not** as D |
| grain diameter d50 | 510 µm, both media | only matters if straining is switched on |
| pulse | **2.98 pore volumes**, then clean water | T₀ = 3.58 hr at v = 0.1667 m/hr |
| total run | **10 pore volumes** | 2.98 injection + ~7 elution |
| influent C₀ | per column, in the CSV header | |
| retention profile read at | **10 PV, END OF RUN** | the column is excised after the full run, not after injection |

That last row is the single most common way this check goes wrong. Reading the profile at end of injection will produce a systematic disagreement that has nothing to do with either code.

## 4. Rate coefficients transfer directly — no conversion

HYDEQ solves, per unit mobile concentration:

    dS/dt = k_a1·C − k_d1·S          (S in the same concentration units as C)

HYDRUS solves, on a mass-of-solid basis:

    ρ_b ∂s/∂t = θ·k_a·C − ρ_b·k_d·s

Substituting S = (ρ_b/θ)·s into the first gives the second exactly, so **k_a and k_d carry over with no conversion** — both are 1/s. Only the solid-phase *values* need the basis change:

    s (per g solid) = (θ / ρ_b) · S · C₀

**You do not need to do that conversion yourself.** The target CSVs (§6) already carry a column `s_model_per_g_solid` in HYDRUS's basis, precisely so that a units slip cannot masquerade as a model disagreement.

### The full unit chain, stated once

S is dimensionless: **attached colloids ÷ C₀, per mL of pore WATER** — not per mL of bulk, and not per gram of solid. Everything else follows from multiplying it out:

| step | quantity | glass R inlet |
|---|---|---|
| S | dimensionless (÷ C₀, per mL pore water) | 0.05924 |
| × C₀ | # per mL pore water | 1.902 × 10⁵ |
| × θ | # per mL **bulk** | 7.131 × 10⁴ |
| **× REV = 22.80 mL** | **# per segment — the RAW DATA UNIT** | **1.626 × 10⁶** |
| × θ ÷ ρ_b (instead of × REV) | # per g solid — **what HYDRUS outputs** | 4.305 × 10⁴ |

REV is the excised segment volume; the measured retention profiles are counts per segment (`data_inventory.md`: *"S(x) = number of colloids retained per segment; V = segment volume"*). The CSVs carry the segment count as `N_spheres_model`, and `log10_spheres_model` is simply its log₁₀ — 6.211104 for the row above.

*Aside worth knowing:* the amplitude anchor logK = log₁₀(REV·T₀·θ·C₀·v) looks as though it depends on injection duration and velocity, but T₀·V_ref = INJPV·L cancels exactly against the engine's rp = S/T₀. It reduces to **spheres = REV·θ·C₀·S** — segment volume × water content × influent concentration × attached fraction, with nothing about the injection surviving.

Units: the table below is in 1/s. Multiply by 3600 for 1/hr or 86400 for 1/day, whichever project time unit you choose — just be consistent with dispersivity and velocity.

## 5. The parameters to enter

Two kinetic sites, attachment and detachment. All five canonical columns; **start with the two in bold**.

| column | medium, IS | k_a1 (1/s) | k_d1 (1/s) | k_a2 (1/s) | k_d2 (1/s) | θ | ρ_b (g/cm³) | C₀ (per mL) |
|---|---|---|---|---|---|---|---|---|
| **Li R** | **glass, 6 mM** | **5.662e-07** | **1.265e-04** | **4.819e-06** | **1.268e-06** | 0.375 | 1.656 | 3.21e6 |
| Li V | quartz, 6 mM | 1.141e-05 | 3.028e-04 | 4.069e-04 | 3.452e-07 | 0.360 | 1.696 | 3.29e6 |
| Li O | glass, 20 mM | 1.388e-06 | 1.518e-04 | 1.664e-04 | 2.141e-07 | 0.375 | 1.656 | 3.12e6 |
| Li P | quartz, 20 mM | 1.589e-06 | 1.425e-04 | 1.438e-03 | 8.310e-08 | 0.360 | 1.696 | 3.24e6 |
| **Li AE** | **quartz, 3 mM** | **4.786e-06** | **1.738e-04** | **1.103e-04** | **7.324e-07** | 0.360 | 1.696 | 3.30e6 |

**Start with Li R (glass, 6 mM) and Li AE (quartz, 3 mM)** — one per medium, and the two with the widest separation in attachment rate, so a rate-handling error shows up as a difference between them rather than a common offset.

*Optional smoke test first:* the one-site irreversible case (k_a only, k_d = 0) gives a pure exponential retention profile with log₁₀-slope λ/ln10, λ = (v − √(v² + 4Dk))/(2D). Useful for confirming the geometry and time units before adding a second site.

## 6. What to compare, and what counts as a pass

Target curves are in these files, one per column, plain CSV:

    hydrus_target_glR_6mM.csv     hydrus_target_quV_6mM.csv     hydrus_target_glO_20mM.csv
    hydrus_target_quP_20mM.csv    hydrus_target_quAE_3mM.csv

Each has a commented header with the exact parameters used, then two blocks:

| block | columns to compare against |
|---|---|
| `BREAKTHROUGH` | `pore_volumes` vs `log10_C_C0_model`. (`log10_C_C0_measured` is the experimental data, included for context only — it is **not** the comparison target.) |
| `RETENTION PROFILE (at 10 PV)` | `distance_cm` vs **`s_model_per_g_solid`** — already in HYDRUS's per-gram-of-solid basis, so this is the least error-prone comparison. |

The retention block carries the same profile in three other units, all exactly equivalent (§4): `S_final_dimensionless` (per mL pore water, ÷C₀), `N_spheres_model` (**# per segment — the raw data unit**), and `log10_spheres_model` (its log₁₀, as the manuscript plots it). Use whichever you prefer, but convert HYDRUS's output *once* and check against the matching column rather than converting twice.

**Pass: agreement within ~0.02 log₁₀ on both curves.** That is well below the residuals the model comparison turns on, so anything inside it is irrelevant to our conclusions.

**If it disagrees**, report before concluding anything. In rough order of likelihood:

1. time-unit mismatch between the rate coefficients and the velocity/dispersivity;
2. dispersivity entered as D rather than α_L;
3. retention profile read at end of injection rather than at 10 PV;
4. solid-phase basis — compare against `s_model_per_g_solid`, not the dimensionless column;
5. a genuine difference in the equations, which is what we are actually looking for.

The same curves are also in `HydeqComparison.xlsx`, sheets `accum_glR_6mM` and `accum_quAE_3mM` — breakthrough block from row 4, with each structure in a column triplet (x, y, blank): two-site is in columns J/K. The CSVs are easier; the workbook is there if you want the other structures alongside.

## 7. The railing question — deliberately not part of this

The fits show something striking: on the quartz columns, straining fits drive **k_str to its lower bound** (straining switched off entirely) and dual-porosity fits drive **f_slow to its upper bound** (half the pore space immobile). Full detail in `hydeq_comparison_record.md` §8c and §5.2.

It is tempting to ask Noah to check whether HYDRUS's optimiser does the same. **That question is excluded from this exercise, on purpose.** It is an *inverse* problem, and it would need HYDRUS's parameter estimation to minimise the same objective we do — which it cannot. Ours has two-segment retention-profile log-slope terms, a mean-log plateau target with a ±0.25 dex dead-band, and a tail-slope term; HYDRUS-1D's inverse solution is weighted least squares on the observations. A disagreement between the two would be uninterpretable: it could mean the models differ, or merely that the objectives do.

That is the same reasoning that excludes dual porosity in §2, and an earlier version of this sheet applied it there while asking for the railing check two sections later. If we want the railing question answered it needs a matched-objective design, which is a separate piece of work.

## 8. What changed in this rewrite (2026-08-25)

The previous version had three defects, all found by W.P.J. asking how Noah was actually supposed to use it:

1. **A flat contradiction.** §1 said "do NOT reproduce the dual-porosity structure"; §5 then said "add the two-site and dual-porosity runs."
2. **It conflated two exercises.** The stated purpose was a forward code check, but §5 and §7 asked whether HYDRUS "also drives k_str to its floor" — an inverse question that cannot use our objective. Now excluded, with the reasoning stated (§7).
3. **The comparison was under-specified.** It said "overlay against the per-column sheets" without naming sheet, block or columns, and required a binary workbook. Now there are plain CSVs with the basis conversion already applied.

Also changed: the task structure is now **two-site** rather than site-plus-straining. Two of the five straining fits rail k_str to its floor, which makes them poor forward-check subjects — you would be verifying that both codes reproduce a switched-off term. No two-site fit rails anything.

**Reproducers:** parameters and curves from `Code/HYDEQ/hydeq_fit.py` → `hydeq_canon.json`; CSVs from `Code/HYDEQ/hydrus_targets.py`.

## 9. OPEN DIAGNOSTIC — HYDRUS shows excess dispersion vs HYDEQ (2026-08-31, W.P.J./N. Willis)

**Observation:** at 4 m/day, α_L = 0.133 cm was entered correctly (confirmed — not the §6 item-2 D-vs-α_L mix-up). The two-site kinetic attachment/detachment reaction terms otherwise agree between HYDRUS-1D and HYDEQ. HYDRUS's *effective* dispersion is much greater than HYDEQ's, and W.P.J. suspects it is non-physical rather than a genuine structural difference (§6 item 5).

**Working hypothesis:** numerical/artificial dispersion from an under-resolved HYDRUS spatial grid. α_L = 0.133 cm on a 20 cm column is small; if HYDRUS's node spacing Δx is not fine enough, its finite-element scheme adds its own truncation dispersion on top of the entered α_L. The standard diagnostic is the grid Peclet number Δx/α_L, with values much above ~2 being where this dominates.

**Planned check:** rerun HYDRUS-1D with **90 nodes** over the 20 cm column — matching HYDEQ/IHOP's own grid (`NX = 90`, `hydeq_engine.py` line 87). This gives Δx = 20/90 = 0.222 cm, so Δx/α_L ≈ **1.67** — inside the recommended ≤2 threshold. If the excess dispersion shrinks toward HYDEQ's value at 90 nodes, that confirms a numerical-grid artifact, not a code/equations disagreement, and the original coarser-grid run should not be read as evidence against HYDEQ's structure. **Not yet run — status OPEN.**

⚠ **Units to double check when logging the result:** §3's table gives α_L in cm (a length), not cm². Confirm HYDRUS's entered/reported dispersivity value carries the same units before comparing numbers, per the project's general units discipline (`CLAUDE.md` "Show the work").
