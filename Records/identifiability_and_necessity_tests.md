# Two parameter tests — local identifiability vs. necessity (methods record)

The paper uses **two distinct** analyses to characterize the parameters. They are complementary, not the same test with a different readout; a parameter can be **locally soft yet globally necessary**. This note records the distinction, the reproducers, and the results, and reconciles the recruitment/k_r resolution.

## (i) Local identifiability — parameter correlations (SI Table S2)

- **What:** at a fitted optimum, form the Jacobian product JᵀJ, invert to the parameter covariance; report pairwise **correlations** and **aliasing amplitudes** (aliasing amplitude = marginal sd / conditional sd for a parameter; marginal = √diag(cov), conditional = 1/√diag(JᵀJ)).
- **Scope:** LOCAL and LINEARIZED, within a single condition's fit.
- **Reading:** high |corr| (→±1) = parameters trade off locally, individually soft.
- **Result:** the near-surface cluster {recruitment (f_x), v_ns, k_r} is collinear (|corr| 0.90–1.00) in both the parallel and serial renderings; k_f is orthogonal on glass, mildly coupled on quartz. Serial routing does not change the structure.
- **Reproducers:** `ident()` in `serial_model.py`; `identif_kr.py`.

## (ii) Necessity — single-constant (pin-vs-free) test

- **What:** refit every column with one parameter **fixed to a single shared value**, the others free to compensate; compare total weighted cost to the per-column free fits.
- **Scope:** GLOBAL, across conditions.
- **Reading:** small penalty → parameter is effectively constant; large penalty → its variation across conditions is required.
- **Results:**
  - **k_r:** a single shared k_r fits all ten glass size-series columns at small total cost → k_r is size- and velocity-independent (a per-medium constant). `serial3_size_fit.py`. *(Numbers superseded twice: this line's 5.58×10⁻⁵/s and +9.0% were the original run; the current glass constant is **3.75×10⁻⁵/s** at a pinning penalty of **+4.8%** over all 18 glass columns — `kr_trend_analysis.md`. The conclusion is unchanged.)*
  - **f_x:** a single constant (0.0039) costs **+67.5%**, ~90% of it from the three small-colloid columns (0.1–0.2 µm; up to +328%), which require small f_x and cannot be forced up even with k_r free → f_x's **size dependence is required**. `fx_pin_test.py`; see `fx_trend_analysis.md`.
- **Note:** this is the same methodology as the shared-k_r test, NOT the correlation analysis with a cost column added.

## (iii) Prior fairness — pinned-value corroboration (α_s, glass IS series)

- **Motivation:** α_s for the glass IS series was originally *pinned* to the Happel single-interception fraction. But that Happel value came from a clean-bed simulation whose surface coverage (SCOV) was itself tuned to the observed **breakthrough plateau** — so pinning α_s reuses that column's data, and is not an independent prior (circularity concern raised by W.P.J.).
- **Test:** free α_s while holding k_f at the **independent favorable clean-bed r_s** (from separate α≈1 experiments, not the unfavorable plateau). This makes α_s determined by the **retention-profile level** — a *different* observable than the plateau the SCOV was tuned to. Compare recovered α_s to the Happel value, and check whether f_x/α_m move. `gl_is_free_test.py`.
- **Result:** free α_s recovers the Happel value within **2% (6 mM), 2% (20 mM), 14% (50 mM)** at equal-or-lower cost; **f_x essentially unchanged** (0.0009/0.0023/0.0019→0.0022) and α_m stays on the same branch. So the pin was **not load-bearing**, and — because RP-level (free) and plateau (Happel) are independent observables that agree — this is an **internal-consistency corroboration**, not circularity. Table on the 'alpha_s pin-vs-free' sheet of `fx_trend.xlsx`.
- **Decision:** the glass IS series is now reported with **α_s fit freely** (canonical: `gl_is_fx.py`), eliminating the objection; the earlier pinned version is superseded. The |U_sec| closure shifts only within rounding (fmax 0.0032→0.0033, U* 0.39→0.42 kT).
  - ⚠ **Superseded 2026‑08‑24.** Those closure numbers are stage 1 of three. The α_s‑pinned‑vs‑free comparison itself still stands — that is genuinely a rounding‑level effect — but it was made against a closure that has since moved twice: to fmax 0.0088 / U\* 2.00 kT when **r_s was pinned** to the favorable anchor, and then to the reported **fmax 0.0047 / U\* 0.80 kT** once columns with k_r on the optimiser bound were excluded as non‑identifiable. Reproducer is now `Code/fx_trend.py`; full history in `fx_trend_analysis.md`. Do not quote 0.0033 / 0.42 kT from this line.
- **Distinction:** unlike (ii), this is not a single-constant necessity test — it asks whether an *externally-pinned* value is corroborated when freed (a prior-fairness / consistency check).

## Why the two can disagree — and the reconciliation

The local analysis (i) says f_x, v_ns, k_r trade off *within* a fit (all collinear). The necessity test (ii) says f_x *must vary across sizes*. Both are true: at a single colloid size {f_x, k_r} are degenerate given pinned v_ns (so one is pinned); the **size series breaks it** — k_r is size-independent while f_x is size-required, so across sizes they separate. Hence the resolution is: pin v_ns = 5%; the recruitment–k_r trade-off is then broken by the multi-size data, leaving k_r a DLVO-ordered per-medium constant and f_x a size-dependent recruitment fraction. (Earlier text said "pin v_ns and the recruitment fraction," which is only the single-size resolution; corrected in SI §S2/§S5.)
