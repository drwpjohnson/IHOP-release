# a_plat — the empirical plateau attachment efficiency (Part 1 extraction)

*Added 2026-08-24 (W.P.J. + assistant). A model-light attachment efficiency read straight from the BTEC plateau, used as an independent check on the fitted α_single / α_mult. Lives in `alpha_trends.xlsx` (reproducer `Code/alpha_trends.py` — refactored 2026‑08‑24, see §6). Companion diagnostic `fx_aplat_relation.py` → `fx_aplat_relation.png`.*

---

## 1. Definition

a_plat is the classical experimental attachment efficiency, read at the breakthrough plateau, of the unfavorable column relative to its favorable clean-bed twin:

    a_plat = kf_unfav_plat / kf_fav_plat,   kf = -ln(C/C0) * (v/L)

C/C0 at the plateau is taken as 10^(mean of log10 C/C0 over 1.2 < PV < 4) — the same mean-log plateau rule used in the Serial-3 fit objective (`plateau_rs_decision.md`). Because v/L cancels when the favorable reference shares the same study (same column length L) and velocity, a_plat reduces to the ratio of the two mean-log plateau depths. It is a **pure data quantity** (data plateau + favorable reference), independent of the fit — hence a genuine cross-check on the fitted α's.

L per study (RP max distance): Tong 0.192 m, Li 0.190 m.

## 2. Favorable reference = the same twin that pins r_s

The favorable reference is the velocity- and size-class-matched favorable BTEC — the SAME favorable that set the r_s pin in `unfav_master_fit.py` (`seed_rs` keyed on medium, sizeclass, velocity; sizeclass 1.1 covers 0.98–1.15). Prefer the same study so v and L cancel; one cross-study case (glass Tong 1.0 µm 8 m/d → Li 0.98 µm 8 m/d, v identical, L 0.192 vs 0.190) is flagged.

a_plat is therefore computable for exactly the **13** conditions whose r_s pin came from a real favorable fit (`fav`), and is **NFT** (no favorable twin) for the **6** where the pin fell back to a favorable RP-slope seed (`favRP`: glass 0.1/0.2 µm c<QL) or the TE correlation (`TE*`: glass 0.5 µm 8 m/d, quartz 0.5 µm 4 m/d 20/50 mM). No favorable BTEC exists at those size/velocity points, so there is nothing to divide by. The a_plat worksheet lists all 19 conditions in the same order as the full-model α sheets, with `NFT` in the favorable columns for those 6 (their unfavorable-side kf is still shown).

## 3. Finding — a_plat position vs α_single, α_mult tracks the RP branch

- **Glass (multiexponential RP, α_single > α_mult):** a_plat lands **between** α_single and α_mult (clearly so at 20/50 mM). Example glass Li 1.1 µm 4 m/d: a_plat 0.027 / 0.091 / 0.220 at 6 / 20 / 50 mM. The classical single-α reading is a fair lumped blend here; the single-collision picture roughly holds.
- **Quartz (peaked RP, α_mult > α_single):** a_plat sits **above both** α's. Example quartz Li 1.1 µm 4 m/d: a_plat 0.096 / 0.171 / 0.726 at 3 / 6 / 20 mM. A weighted average cannot exceed both — so this is not an average. The re-intercepting near-surface (crawling) population gets repeated attachment chances, and the column-integrated removal compounds past any single per-interception efficiency. **a_plat > max(α_single, α_mult) is an empirical fingerprint of multiple-interception-dominated attachment** — the crawl / RFSP story visible in a purely plateau-based number.
- **Near-favorable check:** quartz Tong 0.5 µm 8 m/d 50 mM (R) gives a_plat ≈ 1.01 — at 50 mM quartz, attachment reaches favorable levels, as expected. (Slightly >1 is within noise.)
- a_plat rises monotonically with IS in both media, matching the fitted α_single trend — an independent corroboration of the fits.

Both a_plat sign and the fitted α_mult-vs-α_single/(1−α_single) branch and the measured RP shape tell the same story from three semi-independent directions.

## 4. Test — is f_x the lever? No; the branch is

Hypothesis (W.P.J.): the recruitment parameter f_x (crawl → retained, a removal channel not requiring a fresh interception) might control whether a_plat exceeds both α's. Tested with Δ = a_plat − max(α_single, α_mult) vs fitted f_x over the 13 a_plat conditions (`fx_aplat_relation.py`):

- Raw Pearson Δ vs f_x = **+0.63** — looks supportive, BUT f_x vs α_mult = **+0.80** (the f_x↔k_r↔v_ns collinearity cluster). Δ vs α_mult = +0.59.
- Partial correlation Δ~f_x **controlling α_mult drops to +0.31** (+0.10 on log f_x) — most of the raw signal was α_mult riding along.
- Within-medium: glass alone Δ vs f_x = **−0.05** (nothing); quartz alone +0.96 but n=4 and dominated by the single 20 mM high-leverage point.

**Conclusion:** the sign/size of the a_plat excess tracks the **branch (α_mult vs α_single)** — the same quantity that sets RP shape — not recruitment. f_x co-varies only because the fit raises α_mult and f_x together in the quartz/high-crawl regime; at n=13 with that collinearity the data cannot hand the excess to f_x. Corollary: **a_plat cannot be used to break the f_x↔k_r degeneracy** (an earlier speculation) — the plateau constrains the total crawl contribution, not the f_x share.

## 5. Caveats

- The **qualitative ordering** (glass intermediate, quartz above both) is robust; **absolute a_plat magnitudes carry favorable-reference dependence** (favorable C0, plateau window).
- The 6 mM glass point sits near the model resolution floor (α's ~1e-2–1e-3, shallow plateau); a_plat there is at/just above α_single and noisy — do not over-read it.

## 6. `alpha_trends.py` refactor — 2026-08-24 (W.P.J. approved)

The Box copy of `alpha_trends.py` did **not** read `UnfavorableMaster.xlsx`. It carried α_single / α_mult as hard-coded literals (`ALPHA_S_IS`, `ALPHA_PAIRS`) and did not emit the `a_plat (plateau alpha)` sheet at all, even though the distributed workbook contained it — i.e. §6 below described a script that did not exist, and a refit of `unfav_master_fit.py` could not propagate. Same failure mode found in `kr_trend.py`. Fixed:

- **Reads** `UnfavorableMaster.xlsx` 'Master table' (α's, r_s, and the new measured-RP-branch column) and `LiTong_experimental_data_tidy.csv` (plateaus). Nothing is hard-coded.
- **Both inputs are required arguments — no defaults.** A default path is how a stale workbook gets read silently; the caller must now name what was used.
- **a_plat replicate rule corrected.** Plateau points are **pooled across all replicate columns of a condition**, then mean-logged. The obvious alternative (mean of per-column means) reproduces most conditions but misses Tong glass 1.1 µm/20 mM and Li quartz 1.1 µm/20 mM. Pooling reproduces the reference workbook exactly.
- **Two branch columns** now reported side by side: `RP_branch (fitted alpha)` (Eqn 15 on the fitted α's) and `RP_branch (measured)` (the two-point test on the profile, which selects the RP-shape scoring window — `plateau_rs_decision.md` §6), plus a `branches agree?` flag. **They can disagree, and the disagreement is a result, not an error** — §3 above leans on a_plat sign, fitted branch and measured RP shape being three semi-independent directions. Hiding a disagreement would destroy that argument. On the current fits they agree on 18 of 19 conditions; the single exception is Tong quartz 0.5 µm 20 mM (Tong.B), the same flat-inlet column flagged in `unfav_master_fit.py`'s `rp_branch` docstring.

**Validation.** Against the distributed `alpha_trends.xlsx`: α_single exact 19/19 and a_plat exact 19/19 across every intermediate column (one 1.29 vs 1.30 two-decimal display rounding). Against the post-correction refit master: **only 2 of 19 conditions move** — Li quartz 1.1 µm 3 mM (α_mult 0.0690 → 0.0530) and 6 mM (α_single 0.0596 → 0.0399, α_mult 0.1360 → 0.1180). **a_plat is unchanged** (largest shift 0.0001), as it must be — it is a pure data quantity. The §3 ordering claims survive: at quartz 3 mM a_plat 0.096 > max α 0.053; at 6 mM 0.171 > 0.118.

## 7. Files

- `alpha_trends.xlsx` (Box root) — sheets: `alpha_s vs IS`, `alpha_m vs alpha_s` (+ both branch columns and the a_plat column), `a_plat (plateau alpha)` (full transparency, NFT rows), `branch boundary` (analytic), `notes`. Reproducer `Code/alpha_trends.py`, run as `python3 alpha_trends.py --master UnfavorableMaster.xlsx --csv Data/LiTong_experimental_data_tidy.csv` (both arguments required).
- `fx_aplat_relation.py` → `fx_aplat_relation.png` — the Δ-vs-f_x diagnostic (scratch; not yet in Box unless saved).
