# Data inventory & experimental conditions — interception-history project

*Manifest of data assets **and** the experimental/parameter facts needed to use them. Lives in **project knowledge** so any new chat knows what exists, what must be requested, and what the numbers mean.*

> **DOC-SET BOUNDARY RULE — this file POINTS, it does not restate.**
> - `interception_history_apriori_alpha_working_record.md` — **canonical** for provenance, sourcing, status, and the current program state.
> - `interception_history_extraction_model.md` — **canonical** for equations and derivations (the cascade, identifiability, α_plat de-blending, the transient BTEC).
> - `interception_history_paper_strategy_summary.md` — **canonical** for adoption strategy, the tool, the target audience, and the wedge. **Its thesis is accessibility; read it before writing any positioning or contribution claim.** (See §11.)
> - `section_4c_p_contact.md`, `section_4d_v_mob.md` — canonical for gates 2 and 3.
> - **This file** — canonical for *data assets, experimental conditions, and file-level defects*. Where it touches the above, it points.

**v8 — 2026-07-14** *(fork claim ⚠ RETRACTED 2026-07-15)*. **The extraction was EXECUTED** — but on the **wrong Happel workbooks** (see the §0 retraction breadcrumb); its `r_s = 23.0` / "2× fork resolved" output is **withdrawn** pending re-derivation from the `-UsedInPaper` files. Two findings from that session **survive** because they do not depend on `r_s`: **C₀ needs no factor-2 correction** (model-free mass balance closes) and **the RP amplitude must be FIXED, not floated**. **Supersedes v1–v7 — delete those from project knowledge.**
*(v4 added §9 the α₁/α₂ name collision; §10 Al-Zghoul; the k_f↔LogCCo relation; the FavViaQtz filename mismatch; the 5-and-2 stale tally.)*

> **⚠ READ vs RUN.** Project-knowledge files are readable via search. Recently added files also appear on disk at `/mnt/project/` (the 2026-07-14 paper batch did; older items did **not** — verify with `ls /mnt/project/` rather than assuming). **Anything that must be opened with `openpyxl`/`pandas` or executed with `python` should be uploaded to the chat** unless confirmed present on disk. `.docx` files in project knowledge arrive **pre-converted to plain text** — read them directly; `python-docx` will fail on them.

---

## Data files — the single canonical record (supersedes `Data/README_experimental_data.md`)

*The former `Data/README_experimental_data.md` is now a thin pointer to this section; this file is the one place the data is described.*

**Master (source of record):** `Data/DataFromLi&Tong.xlsx` — original multi-tab workbook (layout in §4).
**Plain-text snapshot:** `Data/LiTong_experimental_data_tidy.csv` (long format, UTF-8), regenerated deterministically by `Data/extract_tidy_data.py`, which **reuses the same loaders as the transport-model reproducers** (so the data the model sees == the CSV, by construction). **1,485 rows across 33 conditions (BTEC+RP), every row carrying C₀** — PRIMARY elution-normal columns only: `extract_tidy_data.py` drops downgradient (series-connected / +1-PV-offset), DI (no defined IS), and perturbation-elution columns (§4c). (The earlier 2,049-row extract kept those; removing them is the 33-condition set the transport models actually fit.) ⚠ An even earlier 1,861-row extract **silently dropped ALL of Glass Beads Li** (188 rows / 6 conditions): its taller header puts colloid size and velocity at rows 11–12, outside the old rows-1–9 header scan, so the "micron & m/day" filter excluded every GB-Li column, and GB-Li C₀ (row 14) was never read. Fixed 2026-08-20 (header scan → rows 1–14; C₀ read from the row-map cell; CS/O overrides).

**CSV column dictionary:** `source` · `medium` · `colloid_um` · `velocity_mday` · `IS_mM` · `chemistry` (favorable/unfavorable/?) · `condition_id` · `curve` (BTEC/RP) · `x` · `x_type` (PV/distance_m) · `value` (log₁₀ C/C₀ or log₁₀ spheres) · `C0_per_mL` · `column_role` (primary/downgradient/2PV-injection) · `workbook_tab` · `workbook_col`.

**⚠ C₀ provenance — the row map (this bit the favorable loader, 2026-08-20).** C₀ is at **row 14 for `Microspheres Glass Beads Li`** and **row 8 for the other three sheets** (Quartz Sand Li, Glass Beads Tong, Quartz Sand Tong). **Read the C₀ *cell* at that row — never scrape header text** (numeric C₀ cells carry no "E", so a scientific-notation regex silently misses them). Loaders that read GB-Li at row 8 pick up the "Favorable/Unfavorable" line instead and lose C₀.
- Two favorable Tong columns have **no C₀ in the sheet**: **GB Tong CS** (`Co = ` blank) and **Qtz Tong O** (no C₀ cell). Resolved (W.P.J., 2026-08-20) by using the **RP-implied, mass-balance-closing C₀** (the eq-4 amplitude the retention profile requires): **CS = 1.157×10⁶**. (An initially-suggested 3.36×10⁵ was ~3× low for CS and ~17× low for O — rejected by the mass-balance check.) Hard-coded as `C0_OVERRIDE`; amplitude FIXED, never floated.
- **⚠ C₀ correction — Qtz Tong O and R (2026-08-23).** The **`3.36E5` placeholder is wrong wherever it appears.** It sits in **Qtz Tong R** (unfavorable, 0.5 µm, 8 m/d, 50 mM) — the recorded cell literally reads `Co = 3.36E5`. R is the **unfavorable twin of favorable O** (same run, same colloid stock; differ only in pH 6.75 vs 2), so they share C₀. Both set to **8.2×10⁶** (R's RP-implied value; joint R+O lowest-cost; O raised from the earlier 5.762×10⁶ to match its twin). Now in `C0_OVERRIDE` in **both** `Data/extract_tidy_data.py` (override takes precedence over the recorded cell) and `favorable_both_models.py`. Downstream: O's favorable r_s stays **56.7** (≈ its old 56.9; r_s is set by the C₀-independent RP slope), the quartz-0.5/8 anchor.

Cleaning rules (placeholder fills −6.00/−9.94/−15.33 removed; LOD ≈1×10⁻⁵ left-censored; BTEC-vs-RP magnitude split; favorable/unfavorable classification) are in §4b; per-sheet row map in §4.

---

## 0. Experimental conditions — the Li/Tong columns (ASK BEFORE ASSUMING)

> **⚠⚠ RETRACTION BREADCRUMB (2026-07-15) — REFINED 2026-07-16/17 (fork resolved; glass reinstated).** What was retracted is the **workbook *route*** to `r_s`: the `FavViaGlass`/20 mM/other non-paper Happel files, `k_f = 3.838 /hr`, and the derivation of `r_s` from a Happel simulation input. Reference-invariant α **fate fractions** survive (independent of `k_f`).
> **⚠ SUPERSEDED — the flat "no favorable fork / 8.636 for both" claim.** There is **no fork *in the 2018 workbook*** (it uses a single `k_f = 8.636 /hr` by simplification, because the favorable difference is unimportant to the unfavorable-conditions theory test that paper ran) — **but there IS a real ~2× fork in the experiments** (W.P.J., 2026-07-16): Li-2004 glass favorable `k_f ≈ 4.0 /hr` vs Li&Johnson-2005 quartz `≈ 8.5 /hr`, a genuine Hamaker (A₁₃₂ qtz 1.96e-20 > glass 7.17e-21) / grain-angularity effect. **The extraction now reads `r_s` from the medium's own favorable BREAKTHROUGH plateau in the data being fit — glass → `r_s = 22.9 /m` (k_f 3.81), quartz → `r_s = 41.5 /m` (k_f 6.9)** — not from any Happel `k_f`. Quartz ≈ the workbook 8.636 either way; glass is the swing (22.9 vs ~52).
> **⇒ Glass extraction REINSTATED** (α_single 0.400/0.133/0.0171, P 1.751/0.981/0.042 — reproduce the withdrawn table to all digits; the withdrawal was a provenance technicality, not a numerical error). Quartz **provisional** (focusing-dominated → phase-2 grid-joint + imported η_mult). Canonical method + numbers now in **Part 1** (`part1_extraction.md`); reproducer `Li_extract.py`. Any Happel *re-derivation* of simulation rates still starts from the five `*-UsedInPaper.xlsx` files (GB 6/20 mM; Qtz 3/6/20 mM), labelled `Attached / Exited / Remaining` blocks in `Residence Time[_PS]` cols Q–AN — **never** θ-based classification (that was an invention, not the workbook's).

| quantity | value | source |
|---|---|---|
| column length L | **0.2 m** | RP sampled 0.01–0.19 m at 0.02 m spacing |
| average pore velocity v | **0.1667 m/hr = 4 m/day** | Johnson 2018 main text; `DataFromLi_Tong` L96 |
| near-surface velocity v₂ | **0.003 m/hr = 0.072 m/day** | Johnson 2018 Table 1 caption |
| porosity θ | **0.375** | Johnson 2018; sheet R96 |
| **injection duration t₀** | **3 pore volumes** | **Johnson 2018 main text** ("3 PV injection, 7 PV elution"); user |
| **elution duration** | **7 pore volumes** (total 10 PV) | **Johnson 2018 main text**; user |
| **influent concentration C₀** | **known only to within a factor of 2** | user, 2026-07-14 |
| colloid radius a₁ | 5.0e−7 m (1 µm CML) | Johnson 2018 SI Table SI-2 |
| collector radius a₂ | 2.55e−4 m (510 µm) | Johnson 2018 SI Table SI-2 |
| pH | 6.72 (unfavorable); ~2 favorable (Tong) | Johnson 2018 SI Table SI-1 |

**Consequences for fitting — do not get these wrong:**
- **⚠ SUPERSEDED 2026-07-14 — THE RP AMPLITUDE MUST BE *FIXED*, NOT FLOATED.** (This bullet previously said "float within ±log₁₀(2)". Wrong.) The **model-free mass balance closes at face value** — retained(RP)/removed(BTEC plateau) = **1.04 / 1.01 / 0.87** at 0.05 / 0.02 / 0.006 M *(⚠ reconcile: the canonical `Li_extract.py` / Part 1 §9 reports **0.97 / 1.08 / 0.74** for the same runs — both "close," but the exact ratios differ; Part 1's reproducer is canonical, this older read to be squared with it)* — so **C₀ needs no factor-2 correction for these runs** and the eq-(4) nominal amplitude is right. **Even a ±log₁₀(2) float is enough freedom to break the fit**: it picks parameters giving 2× too much removal, then halves the amplitude to land on the points (α_single → 0.25–0.45, ~30× Table 1; or → 0). **Fixed**, the fit reproduces the RP shape *and* forward-predicts the plateau to ~0.003 log units. See working record §6a and `li_extract.py`.
- **3 PV injection ⇒ `inject_pv=3, total_pv=10`.** The BTEC plateau spans ~PV 1.2–3.7 and the washout begins ~PV 4.0 (= 3 PV injection + ~1 PV advective transit). An earlier `inject_pv=4` was wrong.

### ✅ SETTLED — do not re-raise (W.P.J., 2026-07-15)

These are closed. Each is something a reader will otherwise re-derive from the papers in good faith and re-open. **They are not open questions.**

- **Straining plays NO role** for uniformly sized grains of 510 µm with uniformly sized colloids of **7 µm and below**. The Li IS series (1.1 µm in 417–600 µm uniform glass beads) is far inside that envelope. ⇒ **The 0.006 M point is NOT straining-contaminated; α_single = 0.0171 stands.**
  ⚠ *This supersedes a trap in the source paper.* Li 2004's Discussion reports that at 0.006 M the influent doublets/triplets are ~60% of the number of retained microspheres, and speculates straining of those aggregates could be *"a significant (even dominant) contributor"* at low IS (tying it to σ_lnkf = 5.3 at 0.006 M vs 2.2 at 0.02 M). **That speculation is superseded by 22 years of subsequent work.** (Li 2004 independently rules out *classical* straining anyway: colloid:grain ≈ 0.002, far below the 0.05 threshold.)
- **Microsphere size varies batch-to-batch** with purchase year. **Whatever each paper states is correct for that paper.** **0.93 / 1.0 / 1.1 µm are practically the same size and directly comparable.** So §0's `a₁` = 5.0e−7 m (radius; = 1.0 µm diameter) and Li 2004 Table 1's "1.1" are **both right and not in conflict** — do not flag it. (Minor: the working record's favorable "0.98 µm" should read **0.93 µm** — Li 2004 and Li & Johnson 2005 both say 0.93. Transcription slip, no consequence.)
- **C₀ is known to within a factor of 2**, as recorded above. Li 2004's stated "±15%" is **dilution reproducibility between experiments** (micropipette intake fluctuation), **not** absolute uncertainty — it excludes stock concentration and flow-cytometry calibration. Do not "correct" the factor-2 entry to ±15%. The amplitude-fixed result rests on the **mass balance closing at face value**, not on C₀'s prior.
- **Porosity 0.375 and pH 6.72 are correct as recorded.** Li 2004's 0.373 / 6.92 are not conflicts worth carrying.

### ✅ Identifiability — the source paper confirms the extraction's structure

Li 2004 Results states that at the lowest IS (**0.006 M**) the normalized steady-state plateau is **very close to unity**, which makes the plateau fit **insensitive to k_f**; the **retained profile supplied the information needed to constrain it** — despite the retained colloids being a minority of overall mass there (**%Sed = 2.4**).

⇒ **The extraction's identifiability structure is stated in the source, not assumed by us:** the plateau cannot carry the low-IS information; the RP must. This is also *why* the amplitude cannot float — at 0.006 M the RP is the only lever.

### The RP convention — Johnson 2018 eq (4)

```
S(x) = V · t₀ · θ · C₀ · k_f* · exp(−k_f* · x / v)
```
`S(x)` = **number of colloids retained per segment**; `V` = segment volume; `t₀` = injection duration; `θ` = volumetric water content; `C₀` = influent concentration; `k_f*` = placeholder for the two subpopulation rates (`k_f`, `k_f2`); `x` = segment midpoint.

So `Ave LOG(spheres)` in `DataFromLi_Tong.xlsx` **= log₁₀ S(x)**, and the amplitude offset is `log₁₀(V·t₀·θ·C₀)` — computable, subject to the factor-2 C₀ float.
The 2018 RP is the **superposition of eq (4) over the α₁ and (1−α₁) subpopulations** with `k_f` and `k_f2`.

### ⚠ RETRACTED — the favorable reference / 2× fork (was here; removed 2026-07-15)

This block claimed a glass-vs-quartz favorable **fork** resolved to `r_s = 23.0 /m` (`k_f = 3.838 /hr`), corroborated by Li 2004/2005 experimental favorable rates. **All of it was built on non-paper Happel workbooks.** The five `-UsedInPaper` files use **`k_f = 8.636 /hr` for both media** — there is no fork. Deleted rather than marked because it is self-contained and preserves nothing correct. `r_s` and everything divided by it (`k_f2`, `k_ns`, any α_mult obtained as P/r_s) must be **re-derived from the paper files**. See the retraction breadcrumb at the top of §0. The α **fate fractions** are reference-invariant and survive — see the α₁/α₂ definition immediately below and §3a.

### ⚠ α₁ / α₂ — **THREE different meanings. SEE §9 BEFORE USING.** (Johnson 2018 eq 1)

```
1 = α₁ + α₂ + α_reentrain + α_RFSZ·α_trans + α_RFSZ·(1−α_trans)
```
These are a **fate partition of near-surface colloids** from the trajectory simulations, **not** single- vs multiple-interceptor attachment efficiencies:
- **α₁** = rapidly arrest — *"probability of attachment from bulk fluid"* (`p_pa` in Hilpert & Johnson)
- **α₂** = slowly arrest — *"probability of attachment from near surface"* (`p_na`)
- **α_reentrain** = return to bulk fluid (`p_np`)
- **α_RFSZ·α_trans** = translate to a down-gradient collector (`p_nn`); α_trans = **0.25 glass, 0.5 quartz**

**⚠ SEE §9.** Al-Zghoul 2025 uses α₁/α₂ for *α_single/α_mult* — a **different** meaning from Johnson 2018's fate fractions above. The working record uses Al-Zghoul's notation while sourcing Johnson-2018's values. §9 proves the two are not interchangeable (substituting Johnson-2018 α₁/α₂ into Al-Zghoul's Eqn 15 predicts peaked glass beads, which are observed hyper-exponential).

---

## 1. In project knowledge

| File | What it is | Notes |
|---|---|---|
| `DataFromLiTong.xlsx` | **The column experiments — the extraction target.** | See §4 for layout. Also contains prior models (§5). |
| `favorable_eta_NG.xlsx` | η_single a priori (Nelson–Ginn) + α_plat anchor | `Glass unfav alpha_plat`: favorable glass 4 m/day = **−2.05** |
| `Analysis_Sim_ExptimesJohnsonetal2025.xlsx` | Johnson 2025 micromodel — the RTD **magnitude** anchor (≈0.1 ratio → 90–130 s dwell) | 6 sheets incl. `elapsed_time` |
| `pcontact.png` | Figure 1 (§4c) | output of `p_contact_reproduce.py` |
| **Papers** (plain-text converted): `JohnsonetalES_T2018-2-ChgsAccptd.docx` + SI; `JohnsonetalES_T2025…` + SI; `JohnsonetalES_T2026…` + SI; `Ron_Johnson2020…` + SI | | 2018 = the residence-time precursor. **Its Table 1 body did NOT survive conversion (caption only) — values recovered from a Happel workbook and transcribed in §3a.** The SI's tables DID survive (§6). |

## 2. NOT in project knowledge — **ask the user to upload**

**Seven Happel trajectory workbooks** (see §3). Needed for anything touching r_s, k_f, α₁/α₂, or Happel near-surface times.

```
HappelModel_1_0um_GB_510um_6mM_4mday_SCOV1E-5_SEPandCON-FavViaGlass_LogCCo-2_.xlsx
HappelModel_1_0um_GB_510um_6mM_4mday_SCOV1E-5_SEPandCON-FavViaQtz_LogCCo-4_.xlsx
HappelModel_1_0um_GB_510um_20mM_4mday_SCOV1E-5-FavViaGlass_LogCCo-2_.xlsx
HappelModel_1_0um_GB_510um_20mM_4mday_SCOV1E-5-FavViaQtz_LogCCo-4_.xlsx
HappelModel_1_0um_Qtz_510um_6mM_4mday_SCOV2E-5_Bimodal-_LogCCo-3_5_.xlsx
HappelModel_1_0um_Qtz_510um_6mM_4mday_SCOV2E-5_Bimodal-_LogCCo-4_5_.xlsx
HappelModel_1_0um_Qtz_510um_20mM_4mday_SCOV2E-5_Bimodal-_LogCCo-3_5_.xlsx
```

Filename axes: medium (**GB**/**Qtz**), IS (**6/20 mM**), SCOV (**1e-5 glass / 2e-5 quartz** — per Johnson 2018, quartz assumed 2× glass), **favorable reference + its log C/C₀** (see the 2× ambiguity above), attachment mode (**SEPandCON** = separation and contact; those files carry an extra `Unfav Contact` sheet).

## 3. Happel workbooks — structure and the α₁/α₂ defect

**Sheets:** `Residence Time` (± `_PS`/`_Contact`) — TBULK/TNEAR/TTOTAL bins for attached/exited/remaining; `1.1 um Fav`; `1.1 um Fav Exit`; `1.1 um Unfav Perfect Sink` (± `1.1 um Unfav Contact`); `Perfect Sink Exit`/`PS Exit`/`Contact Exit`. Run parameters in rows 1–4 (RB, AG, AP, TTIME, NPART, VSUP, POROSITY, ZETACST, ZETAP, ZETAHET, SCOV, IS, ATTMODE). Derived quantities in the AC/AK/AP–AQ blocks.

### ⚠⚠ COLUMN & CODE DICTIONARY — read before interpreting any trajectory sheet

| column | meaning |
|---|---|
| `TBULK` | time in bulk fluid |
| **`TNEAR`** | **CUMULATIVE time in the NSFD, summed over all visits.** ⚠ **Not** a per-interception dwell. |
| `TTOTAL` | `TBULK` + `TNEAR` = `ETIME` = `PTIMEOUT` − `PTIMEIN` |
| `NSVISIT` | number of NSFD entries |
| **`TFRIC`** | **time in CONTACT** (W.P.J., 2026-07-15). ⚠ Not "friction time". **0 by construction in perfect sink** — absorbed on contact. Zero is correct, not missing data. |
| `FRICVISIT` | contact events: `1` = contacted (→ attached); `0` = never contacted |
| `ZOUT`,`ROUT` | exit position ⇒ **θ = degrees(arccos(−ZOUT/AG))**; **θ=0 is the FFSP, θ=180 is the RFSP** |
| `AFRACT`,`HETTYPE` | heterodomain fields |

`ATTACHK` codes, verbatim from the sheet:
`1=EXIT` · `2=ATTACHED-BY-SEP-OR-TORQUE` · `3=REMAINING-IN-BULK` · `4=TORQUE-W-SLOW-MOTION` · `5=IN-NEAR-SURFACE-WITH-SLOW-MOTION` · `6=CRASHED`

### The classification is stated on the sheet — use the labelled blocks (⚠ NOT θ)

**The `Residence Time[_PS]` sheet labels the outcome itself**, in columns Q–AN: `Attached (fav)`, `Attached (unfav)`, `Exited (fav)`, `Exited (unfav)`, `Remaining (unfav)`, each with its own TBULK / TNEAR / TTOTAL / Bin columns and a count in row 3. **Read those. Do not classify by θ.**

> **⚠ RETRACTED 2026-07-15 — the "θ=180 = Remaining, not attachment" trap and its "verified 29/29, 348/348" numbers.** That was Claude's θ = degrees(arccos(−ZOUT/AG)) proxy applied to the *wrong* (20 mM / `FavViaGlass`) files, and it reconstructed by geometry what the sheet already states by label. The physical point may still hold — *whether a rear-pole `ATTACHK=2` should count as attachment or as "Remaining" is a real question* — but it is **W.P.J.'s to answer from the labelled blocks**, not Claude's from θ. The paper files' labelled counts are in the next section.

⚠ Related (unchanged, from Hilpert et al. 2017 / Hilpert & Johnson 2018): **both α_reentrain and α_RFSZ reentrain** — they differ by *location and mechanism*, not reentrained-vs-not. α_reentrain = diffusive escape upstream of the RFSZ; α_RFSZ = rides the arc to the RFSZ and is expelled there. Never call one "the reentrainment population" and the other "stuck".

### ⚠ RETRACTED 2026-07-15 — the "interceptors, not NPART" denominator note

~~interceptors = (Exit-sheet rows with TNEAR > 0) + (all rows in the Unfav Perfect Sink sheet); N = 1538 / 386~~ — this reconstructed the denominator from the raw sheets of the **wrong files**. The workbook's own denominator is **Σ = H35 + H36 + H37 = attached + "exiters near surface" + RFSZ = 1538** (paper file, GB 6 mM; see §3a). The *point* stands — the fate fractions are **per-interceptor, not per-NPART** — but take the counts from the labelled blocks of the `-UsedInPaper` files, not from a θ reconstruction. **NPART does differ between runs** (GB 6 mM = 20,000; the other four = 5,000) — that observation is correct and worth keeping.

### ⚠ LIVE vs STALE cells — the workbook is a MIX; do not judge it wholesale

- **LIVE (trust):** `Y1` TNEAR ave, `Y3` TNEAR stdev — reproduce from the rows to all digits. *(The specific values noted earlier — 528.5 at 6 mM, 1504.9 at "20 mM" — came partly from non-paper files; re-read from the `-UsedInPaper` files. The point that these cells are LIVE while AB1/AJ1/AO1 are stale is the durable part.)*
- **STALE (do not use):** `AB1`/`AJ1`/`AO1` and every α cell derived from them (`AD6`,`AL6`,`AQ6`) — see below.

### ⚠ KNOWN DEFECT — α₁/α₂ summary cells are stale (found 2026-07-14)

> **⚠ 2026-07-15:** the defect below was catalogued across **seven** workbooks, **five of which are not the paper's files.** The `AB1/AJ1/AO1` tallies and the "5 files / 2 files" grouping refer partly to discarded workbooks and should be **re-catalogued against the five `-UsedInPaper` files only.** The earlier "✅ RESOLVED — should be FORMULAS" verdict rested on the θ recomputation (now retracted); it is **plausible but re-open** — the fate partition *is* computed live in the paper files' `Residence Time_PS` rows 38–45 (dividing by H35:H37), so formulas are clearly feasible, but confirm against the paper files. The core observation — **these summary cells are stale; use Table 1 (§3a) instead** — stands.

```
AD6 (alpha1)              = AB1/(AB1+AJ1+AO1)
AL6 (alpha2)              = AJ1/(AB1+AJ1+AO1)
AQ6 (alpha2, reentrained) = AO1/(AB1+AJ1+AO1)
```
AB1/AJ1/AO1 are **hardcoded, typed-in counts** — not formulas reaching the trajectory data. The tally is **5 files and 2 files** (an earlier note saying "6 and 1" was wrong — both GB 6 mM variants share the second triple):
- **5 files** (both GB 20 mM, all 3 Qtz): `10 / 25 / =358+8` → 401 → α₁=0.0249, α₂=0.0623, third=0.9127
- **2 files** (both GB 6 mM SEPandCON): `3409 / 17 / =83+3823` → 7332 → α₁=0.4649, α₂=0.0023, third=0.5327

**Additional indicator — ⚠ RESTATED 2026-07-15.** The *hardcoded summary triple* is duplicated across the GB 6 mM SEP and CON variants — impossible, since SEP and CON are different attachment modes and are the reason those two files exist. **Note the earlier wording ("the sheets carry identical counts") was imprecise: the TRAJECTORY sheets are NOT identical** — 6 mM PS = 60 attached-flagged / 19,940 exited vs Contact = 64 / 19,936. It is only the stale summary cells that are duplicated. **The trajectory data are sound.**

**Four independent reasons these are stale:**
1. Identical values cannot follow from different zeta potentials / IS.
2. **The ZETACST cells DO vary correctly per file and match Johnson 2018 Table SI-1 exactly** (−0.051 glass 20 mM; −0.0688 quartz 20 mM; −0.0834 quartz 6 mM). Inputs were set per-run; the summary counts were not updated.
3. α₁ runs **backwards with IS** (0.025 at 20 mM vs 0.465 at 6 mM), whereas Johnson 2018 states *"All parameters (α₁, α₂, k_f and k_f2) increased with IS."*
4. Totals (401, 7332) don't correspond to `NPART = 20000`; `kf sim` caches 17.24 (6 mM) vs 0.198 (20 mM) — same backwards direction — and the α2/reentrainment `kf sim` cells read `0` and `#VALUE!` (formulas point at empty T1/Y1/O2/Q1).

**Consequence: do not read α₁/α₂ from the stale summary cells** — use Table 1 (§3a). On whether `AB1/AJ1/AO1` should be hand-pasted or formulas: the paper files compute the partition live in `Residence Time_PS` rows 38–45 (dividing by H35:H37), so **formulas are feasible** — but the earlier "✅ ANSWERED — should be FORMULAS, stale triple wrong by 150×" verdict used the retracted θ recomputation and wrong-file counts; **treat as plausible-but-unconfirmed pending re-derivation from the `-UsedInPaper` files. W.P.J.**

**Ground truth exists and is RECOVERED — see §3a.** Johnson 2018 Table 1 holds the per-IS α₁, α₂, k_f, k_f2 from these simulations. It is transcribed in §3a; use it instead of these cells. (Note §3a's finding that even un-staled, AD6/AL6/AQ6 are not the Table 1 quantities — the third category is mislabeled and the normalization omits α_reentrain.)

---

## 3a. Johnson 2018 **Table 1** — THE GROUND TRUTH (values transcribed here)

**Location:** *not* in the paper file (the table body did not survive docx→text conversion — caption only). The values live in **`HappelModel_1_0um_GB_510um_6mM_4mday_SCOV1E-5_SEPandCON-FavViaGlass_LogCCo-2_.xlsx`, first tab (`Residence Time_PS`), rows 45–56, columns I–P.** That workbook is NOT in project knowledge — hence the transcription below. **Use these numbers; do not use the workbook's AD6/AL6/AQ6 cells (§3 defect).**

### Glass beads — α fate fractions (⚠ header k_f corrected)

*(⚠ 2026-07-15: this table was headed "k_f = 3.838 /hr". The **paper files use k_f = 8.636 /hr**; 3.838 was the wrong-workbook value. The α columns below are **reference-invariant and correct**; only the k_f/rate header changes. `h` = η = 0.009113 is likewise a per-run value to re-confirm.)*

| | **0.006 M** | **0.02 M** |
|---|---|---|
| α₁ | 0.003250975292587776 | 0.01 |
| α₂ | 0.009102730819245773 | 0.065 |
| k_f2 (1/hr) | 0.0018071150426909532 | 0.0333 |
| α_reentrain | 0.9609882964889467 | 0.023 |
| α_RFSZ | 0.026657997399219768 | 0.9016 |
| α_trans | 0.25 | 0.25 |
| k_ns (1/hr) | 0.07267281087582218 | 1.15 |
| u₂ (m/hr) | 0.0030387352049705144 | 0.0012 |
| v₂ (m/hr) | 0.005 | 0.005 |

### Quartz sand — α fate fractions (⚠ header k_f corrected)

*(⚠ 2026-07-15: was headed "k_f = 6.71 /hr". Paper quartz files use **k_f = 8.636 /hr** (same as glass). α columns reference-invariant and correct; rate header retracted.)*

| | **0.003 M** | **0.006 M** | **0.02 M** |
|---|---|---|---|
| α₁ | 0.005277044854881266 | 0.0051 | 0.0169 |
| α₂ | 0.013192612137203167 | 0.0257 | 0.146 |
| k*_f2 (1/hr) | 0.05 | 0.0975 | 0.591 |
| α_reentrain | 0.931398416886544 | 0.00257 | 0.0056 |
| α_RFSZ | 0.05013192612137203 | 0.967 | 0.8315 |
| α_trans | 0.5 | 0.5 | 0.5 |
| k_ns (1/hr) | 0.255 | 3.409 | 3.76 |
| u₂ (m/hr) | 0.001841427364864865 | 0.00092 | 0.00075 |
| v₂ (m/hr) | 0.003 | 0.003 | 0.003 |

**Internal checks passed (reference-invariant — these stand):** α₁+α₂+α_reentrain+α_RFSZ = **1.0000**. Every IS trend matches the paper's prose (α₁, α₂, k_f2 rise with IS; α_reentrain and u₂ fall). ⚠ **RETRACTED:** ~~k_f = 3.838/hr is the anchor; r_s = 3.838/0.1667 = 23.0 /m~~ — the paper files use **k_f = 8.636 /hr**; r_s must be re-derived from that (see §0 breadcrumb). The α *trends* survive; the *rate* does not.

### The LogCCo filename suffixes DECODED

Each workbook's `LogCCo` suffix is the **favorable plateau implied by its k_f**. *(⚠ 2026-07-15: the paper's five files are all the **−4.0 / −4.5 → k_f = 8.636** row; the −2.0 (3.838) and −3.5 (6.71) rows are the discarded workbooks. The decode relation itself is correct and reference-invariant — it is the tool for re-deriving r_s = 8.636/0.1667.)*

| k_f (1/hr) | r = k_f/v | favorable log₁₀(C/C₀) = log₁₀(e^(−rL)) | filename suffix |
|---|---|---|---|
| **3.838** (glass, Table 1) | 23.0 /m | **−2.00** | `LogCCo-2_` |
| **6.71** (quartz, Table 1 — *simulated*) | 40.3 /m | **−3.50** | `LogCCo-3_5_` |
| **7.67** (quartz, `DataFromLi_Tong` R100 — *assumed = 2× glass*) | 46.0 /m | **−4.00** | `LogCCo-4_` |
| 8.64 | 51.8 /m | **−4.50** | `LogCCo-4_5_` |

**THE EXACT RELATION (verified to every digit across the workbooks):**
```
k_f = |LogCCo| · ln(10) · v / L          (v = 0.1667 m/hr, L = 0.2 m)
```
⇒ −2.0 → 3.838 · −3.5 → 6.717 · −4.0 → 7.677 · −4.5 → 8.636. **The favorable reference is the ONLY thing that sets k_f**; k_f2, k_ns, r_s and every α obtained by dividing all ride on it.

**The α's are INVARIANT to the favorable reference.** Confirmed by comparing the two GB 6 mM variants: α₁, α₂, α_reentrain, α_RFSZ, α_trans, u₂ are identical; only k_f (3.838 vs 8.636), k_f2 and k_ns change. **So Johnson-2018 Table 1's α's are reference-independent and safe to use — the 2× ambiguity contaminates r_s and the derived rates, but not the α's.**

**⚠ A FILENAME DOES NOT MATCH ITS CONTENTS — cosmetic only; the FILE IS CANONICAL.** `…GB_510um_6mM…SEPandCON-FavViaQtz_LogCCo-4_-UsedInPaper.xlsx` contains **k_f = 8.636**, i.e. **LogCCo = −4.50**, not the −4.0 in its name. **⚠ 2026-07-15 — this warning previously read "ask the user before attributing any result to it." That is now BACKWARDS and has been struck: this file is one of the FIVE the paper actually used.** The *filename* is mislabelled; the *contents* are correct and canonical. **Use it. Do not be steered off it by its name.**

**⚠ Johnson 2018's *text* states the favorable as C/C₀ = 10⁻⁴·⁰ (⇒ k_f = 7.677), but NO workbook uses that value** — the paper's five all carry **k_f = 8.636 (⇒ −4.5)**. The −4.0 branch appears only in `DataFromLi_Tong` R100. *(⚠ 2026-07-15: previously this was read as evidence the favorable reference was "being scanned." It is not — 8.636 is used throughout. The text-vs-workbook mismatch is a genuine open question for W.P.J., but it is NOT a fork to resolve by fitting.)*

**"h" in the workbook Table 1 is η** (Symbol-font eta rendering as "h"): `kf (1/hr) = 3.838, η = 0.009113`.

**⚠ RETRACTED — "the quartz k_f fork":** the paragraph here argued a 6.71-vs-7.67 quartz fork feeding §0's "favorable reference ambiguous by 2×." That whole framing is withdrawn — **the paper files use k_f = 8.636 for both media**, so there is no fork to reconcile. The *mechanical* decode above (`k_f = |LogCCo|·ln10·v/L`) and the invariance finding stay; the fork *narrative* does not. Re-derive r_s from 8.636.

### ⚠ PARTLY RETRACTED 2026-07-15 — Table 1 recomputation (right numbers, wrong provenance and classification)

**What survives (correct, and NOT dependent on the favorable reference):** the workbook computes the fate partition in `Residence Time_PS` rows 38–43 of the paper file, dividing by `H35:H37`:

| category | cell | value | source (paper file, GB 6 mM) |
|---|---|---|---|
| `aatt` (= α₁+α₂) | H43 = H35/Σ | **0.0123537** | H35 = 19 (attached), denominator Σ = 1538 |
| `areentrain` | H41 = H36/Σ | **0.9609883** | H36 = 1478 (*"Exiters near surface"* — a **hand-entered** subset, **not** the 19,940 total exits) |
| `aRFSZ` | H40 = H37/Σ | **0.0266580** | H37 = 41 (RFSZ / "Remaining") |
| `atrans` | H45 | 0.25 (glass) | hand-entered |

Σ = H35+H36+H37 = 19+1478+41 = **1538**. These α fate fractions are **reference-invariant** (identical across `FavViaGlass`, `FavViaQtz`, and the paper file) and match the transcribed Table 1. **Keep them; re-source to the five `-UsedInPaper` files.**

**⚠ RETRACTED from the earlier version of this block:**
- The classification "**θ<180 vs θ=180**" — Claude's geometric proxy, **not** the workbook's method. The workbook classifies by its labelled `Attached / Exited / Remaining` blocks (columns Q–AN) and residence-time **bins** (`a1 = SUM(H21:H26)/Σ`, `a2 = SUM(H27:H33)/Σ` — split at a residence-time cutoff **~76–114 s**, read off the histogram, not θ). That θ reproduced the counts was coincidence.
- "**5 and 14 colloids**" and the "**(39.41, 49.37 s) threshold**" — **fabricated.** The real a1/a2 split is the bin sum above.
- The "**20 mM**" column — **wrong file** (not one of the five `-UsedInPaper`).
- "**independently validated / closes the §3 defect**" — overstated. The numbers are read from the workbook's own cells; whether they are the right fate definitions for the manuscript is a **W.P.J. question**, not a Claude verification.

**Genuine open question (the real version of the fabricated one):** the workbook splits α₁/α₂ at a near-surface **residence-time bin boundary (~76–114 s)**. Is that the intended "rapidly arrest / slowly arrest" cut? **W.P.J.**

### ⚠ RETRACTED 2026-07-15 — BTEC-plateau validation (used r_s = 23.0)

~~Reading **α₁+α₂** as the per-interception attachment probability, with r_s = 23.0 /m and L = 0.2 m, removal = 1 − exp(−(α₁+α₂)·r_s·L)~~ — **this computation used `r_s = 23.0 /m`, which is retracted** (built on the wrong favorable reference; see §0 breadcrumb). The removal-vs-plateau comparison must be **re-run with r_s re-derived from the paper's `k_f = 8.636 /hr`**. The α₁+α₂ = 0.075 / 0.0124 inputs are reference-invariant and stand; only the r_s multiplier and the resulting removal %/"agreement" figures are withdrawn.

**Corollary — a fitting lesson that is load-bearing (this part does NOT depend on r_s and stands).** An RP fit with a *freely floating* amplitude returned α_single ≈ 0.25–0.45, ~30× above Table 1's total attachment probability (~0.01–0.08). The free amplitude absorbs the removal and destroys identifiability (fits also collapse to α_single→0 for some r_s). **⚠ CORRECTED 2026-07-15 — this bullet previously read "floated only within ±log₁₀(2)", which §0 supersedes.** The amplitude must be computed from eq (4) and **FIXED, not floated at all**: even a ±log₁₀(2) float is enough freedom to break identifiability (the fit picks parameters giving 2× too much removal, then halves the amplitude to land on the points). The model-free mass balance closes at face value (1.04/1.01/0.87), so C₀ needs no factor-2 correction *for these runs*. See §0 and working record §6a. This is not a refinement — it is required.

### ⚠ Three unresolved issues raised by Table 1

1. **The workbook's third category is MISLABELED.** `AO1` is captioned "alpha2 reentrainment", but its value (0.9127) tracks Table 1's **α_RFSZ** (0.9016), *not* α_reentrain (0.023). Moreover the workbook's three-way normalization `AB1/(AB1+AJ1+AO1)` omits α_reentrain entirely, while eq (1) is four-way. **So even if un-staled, AD6/AL6/AQ6 are not the Table 1 quantities.**
2. **v₂ inconsistency.** Table 1's glass column has v₂ = **0.005** m/hr *with* α_trans = 0.25. The paper's text says the simulations used v₂ = **0.003** with α_trans = 0.25, and offers v₂ = 0.005 with α_trans = **0.0** as the equally-good alternative (SI-3). Table 1 glass matches neither. Quartz has 0.003/0.5. *Is the glass column the SI-3 variant, or is 0.005 a typo?* **Ask the user.**
3. **α₁/α₂ vs α_single/α_mult is a STRUCTURAL mismatch, not just naming.** α₁ and α₂ are two *channels* available at every near-surface entry (attach-from-bulk vs attach-from-near-surface). α_single/α_mult are the *same channel* at different interception *counts*. Summing them (as the validation above does) is defensible for total removal; mapping α₁→α_single and α₂→α_mult is a stronger claim the equations do not license. **Make the bridge explicit in the manuscript.**


## 4. `DataFromLi_Tong.xlsx` — layout

4 sheets: `Microspheres Glass Beads Li`, `Microspheres Quartz Sand Li`, `Microspheres Glass Beads Tong`, `Microspheres Quartz Sand Tong`.

**Each condition is a 3-column block; BTEC and RP are STACKED, BTEC above RP** (Glass Beads Li; other sheets offset):

| rows | content | columns |
|---|---|---|
| 7–14 | condition headers (source, Favorable/Unfavorable, medium, IS **or** velocity, colloid size, velocity **or** IS, elution note, C₀) | ⚠ rows 10/12 **swap meaning** between favorable (10=IS, 12=v) and unfavorable (10=v, 12=IS) blocks |
| 15 | `PV \| Ave LOG(C/Co) \| Std dev LOG(C/Co)` | |
| **16–44** | **BTEC** (~28–29 pts, PV 0.21–9.9) | |
| 45 | blank | |
| 46 | `Distance (m) \| Ave LOG(spheres) \| Std dev LOG(spheres)` | |
| **47–56** | **RP** (10 pts, x = 0.01…0.19 m) | grid is **identical to `X` in `alpha_extract.py`** |

**⚠ The row map above is the `Glass Beads Li` sheet only.** Per-sheet row map (MEASURED — all four sheets read from cells 2026-08-10). **Every experiment is ONE 3-column stripe** (B–D, E–G, H–J, …) read top→bottom as **header → BTEC → RP**:

| sheet | header rows | elution-label row | BTEC rows | RP header row | RP rows |
|---|---|---|---|---|---|
| Glass Beads Li | 7–14 | **13** | 16–44 | 46 | 47–56 |
| Quartz Sand Li | 1–8 | **7** | 10–38 | 40 | 41–50 |
| Glass Beads Tong | 1–8 | **7** | 10–66 (ragged by col) | 67 | 68–77 |
| Quartz Sand Tong | 1–8 | **7** | 10–66 (ragged by col) | 67 | 68–77 |

**Header field-by-row (MEASURED).** The three compressed sheets (Qtz Li, both Tong) use an **8-row header**: **r1** source paper · **r2** Condition (Favorable / Unfavorable (pH)) · **r3** Medium + grain size · **r4** ionic strength · **r5** colloid size (diameter) · **r6** pore velocity · **r7** elution · **r8** C₀ · (r9 = `PV | Ave LOG(C/Co) | …` sub-header). `Glass Beads Li` carries the same fields over rows 7–14 (source 7, Condition 8, medium 9, colloid size 11, elution 13, C₀ 14) with **⚠ IS and velocity swapping rows** (fav: r10=IS, r12=v; unfav: r10=v, r12=IS). Qtz-Li shows the same row-swap between its favorable-velocity triplet and unfavorable-IS blocks — **read the label, don't assume the row.**

- **⚠ Grain size is CONSTANT = 510 µm (417–600 µm sieve) for ALL media and experiments** (W.P.J., 2026-08-10) — glass beads and quartz sand, every sheet. Stated in the Tong / Qtz-Li medium rows ("… 510 um (417–600 um)"); the GB-Li medium cell reads only "Glass Beads" but is the same 510 µm (= §0 collector radius 255 µm). **Grain diameter is not an experimental variable.**
- **Colloid size (diameter) IS a variable — the size lever lives in the Tong sheets.** `Glass Beads Tong` r5 = **0.1 / 0.2 / 0.5 / 1.0 / 1.1 / 2.0 µm** (a genuine colloid-size series, mostly 4 m/day, Fav pH 2 + Unfav pH 6.75); `Quartz Sand Tong` r5 = **0.5 µm at 4 and 8 m/day**. Li sheets are 0.98 µm aminated (favorable) / 1.1 µm (unfavorable). ⚠ Corrects an earlier note calling the size lever "thin/absent" — **it exists (Tong).**
- **Elution condition — the "line 7" rule:** the elution-normal vs perturbation label sits at **row 7** in the three compressed sheets and **row 13** in `Glass Beads Li` (its taller header). The four already-fit experiments (GB 20/6 mM, Qtz 20/6 mM) are all **elution normal**; the perturbation runs (2 PV MQ, pH 11, 0.0002 M, …) are separate deliberate-release experiments and are **excluded from constant-condition fits**.
- **Third column varies:** BTEC 3rd col is `Std dev LOG(C/Co)` (Li) or `C/Co` linear (Tong); RP 3rd col is `Std dev LOG(spheres)` (Li) or `# spheres` linear (Tong). RP value is always the **2nd** col (`Ave LOG(spheres)`).
- **⚠ Correction (2026-08-10):** a prior scan reported the **Tong sheets as BTEC-only — WRONG.** Both Tong sheets carry an RP block at **rows 67–77** (10 pts, x ≈ 0.01–0.19 m), sitting well below the BTEC after a blank gap — a capped/short scan misses it. **All four sheets have BTEC-over-RP.**

Glass Beads Li blocks start at cols **B, E, H** (Favorable 0.01 M, 0.98 µm **aminated**, 2/4/8 m/day) and **L, O, R** (Unfavorable 4 m/day, 1.1 µm, 0.05/0.02/0.006 M).
⚠ **Favorable used 0.98 µm aminated colloids; unfavorable used 1.1 µm.** r_s taken from favorable carries a colloid-size mismatch.
Quartz Sand Li carries the fuller IS series (0.02 M, 20 mM, 0.006 M, 6 mM, 0.003 M, 3 mM, 1 mM, DI) — the α_plat(IS) data.
Rows ~94–100 (Glass Li) hold column params and the fitted 2-kf model: `REV=22.80 mL, Co=9.63e6 #/mLw, t0=3.58 hr, e=0.375, v=0.1667 mREV/hr`; `0.02 M: kf=3.84, kf2=0.0333, a1=0.01` (glass) / `7.67, 0.04, 0.01` (quartz).

## 4a. Experimental design space — the SETS (MEASURED, elution-normal only; 2026-08-10)

Grain **510 µm throughout**. Perturbation-elution columns (2 PV MQ, pH 11, 0.0002 M) excluded. The live levers are **colloid size** and **velocity** (grain size fixed; medium *type* = glass/quartz chemistry).

**Favorable (α≈1 ⇒ k_f-only; anchors k_f vs Nelson–Ginn):**

| medium | colloid µm | velocity m/day | IS | source |
|---|---|---|---|---|
| Glass | 0.98 | 2 / 4 / 8 | 0.01 M | Li |
| Quartz | 0.98 (aminated) | 2 / 4 / 8 | 0.01 M | Li |
| Glass | **0.1 / 0.2 / 0.5 / 1.0 / 2.0** | **8** | 0.05 M | Tong |
| Glass | 0.2 / 0.5 / 1.0 | 4 | 0.05 M | Tong |
| Quartz | 0.5 | 8 | 0.05 M | Tong |

**Unfavorable (full model; attachment/tail physics):**

| medium | colloid µm | velocity m/day | IS | source |
|---|---|---|---|---|
| Glass | 1.1 | 4 | 0.05 / 0.02 / 0.006 M | Li — **fitted GB 20/6 mM = 0.02/0.006 M** |
| Quartz | 1.1 | 4 | 20 / 6 / 3 / 1 mM, DI (+prep variants) | Li — **fitted Qtz 20/6 mM** live here |
| Glass | **0.1 / 0.2 / 0.5 / 1.0 / 2.0** | **8** | 0.02 M | Tong (+ replicates) |
| Glass | 0.2 / 0.5 / 1.1 | 4 | 0.02 M | Tong |
| Quartz | 0.5 | 4 & 8 | 0.02 / 0.05 M | Tong |

**Structure that matters for route-separation:**
- **Size × velocity grid:** glass **0.2 / 0.5 / 1.0 µm exist at BOTH 4 and 8 m/day**, favorable AND unfavorable — a genuine partial grid, not velocity-at-one-size.
- **Full colloid-size sweep (0.1–2.0 µm) is at 8 m/day** (Tong glass); partial (0.2/0.5/1.0/1.1) at 4 m/day.
- **2 m/day exists only in the Li favorable sets** (0.98 µm). Confirmed 2026-09-08 against the tidy CSV: exactly **two** columns, Li glass B and Li quartz B, both 0.98 µm / 10 mM, both fitted. **No unfavorable experiment exists at 2 m/day**, so the unfavorable velocity axis is 4 and 8 m/day only — a single factor-of-two contrast. Any velocity trend read from the unfavorable fits (Figure 10) rests on those two levels, not on the three-velocity span of the favorable series.
- **Study balance across the unfavorable velocity axis is one-sided** (counted 2026-09-08 over the 29 fitted columns): **4 m/day — Li 11, Tong 8; 8 m/day — Tong 10.** Tong spans both velocities, so a within-study velocity contrast is available and velocity is *not* inseparable from a between-study offset; but **Li contributes nothing at 8 m/day**, so the range is unbalanced and a velocity claim should be checked within Tong alone before being asserted over the pooled set.
- **Levers:** colloid size (v_ns vs k_r scale *oppositely* with a) and velocity (v_ns ∝ v, k_r ≈ v-independent). Favorable version anchors **k_f(size, v) vs Nelson–Ginn**; unfavorable version isolates **v_ns vs k_r** with k_f pinned.
- **RP ↔ BTEC is 1:1:** every data-bearing column carries BOTH a BTEC (22–56 pts, ragged) and a 10-pt RP.
- **⚠ Header-only (empty) columns — headers present, NO data (MEASURED 2026-08-10; don't go looking for it):** GB Tong **BR** (Favorable, 0.5 µm, 8 m/day), **CB** (Favorable, 1.0 µm, 8 m/day), **BX** (Unfavorable, 0.5 µm, 8 m/day — perturbation). Consequence: the **favorable 8 m/day size series is missing its middle** (only 0.1 / 0.2 / 2.0 µm + Li 0.98 µm); the **4 m/day favorable size series is complete** (0.2 / 0.5 / 1.0 µm) and is the only clean look at intermediate (0.5–1.0 µm) sizes.

## 4b. Detection limit & placeholder floors — do NOT fit to noise (MEASURED, 2026-08-10)

**LOD ≈ 1×10⁻⁵ in C/C₀ (blank-based), NOT 1×10⁻⁴.** Pre-breakthrough baselines and genuine rising-limb points sit at ~10⁻⁵ (e.g., GB Li 0.98 µm 4 m/d has a real rising-limb point at PV 0.70 = −4.96), so sub-1E-4 concentrations ARE measured. Glass and quartz blanks are both ~10⁻⁵.

**⚠ Placeholder fills — never real measurements, never fit them:** `−6.00`, `−9.94`, `−15.33` (and similar) are software fills for "below detection / zero," used where breakthrough was undetectable or a computed log of ≈0. Whole columns of −6 mark saturated non-detects (e.g., favorable small colloids with near-total removal: GB Tong 0.1 / 0.2 µm 8 m/d). A BTEC "plateau" read off a −6 column is a lower bound, not a value.

**The favorable washout tail (~10⁻⁴) is REAL, not the floor.** Favorable BTECs decline from the plateau and flatten at ~10⁻⁴·² — **~0.7–0.8 log (5–6×) ABOVE the ~10⁻⁵ blank.** So even under favorable a small fraction (~1 % of breakthrough) lingers in the near-surface and elutes slowly: **hydrodynamic reentrainment (α_single slightly < 1), NOT barrier-controlled reversibility** (no detachment under constant IS/flow — §6z canon). ⇒ the "favorable = pure k_f, no tail" idealization holds for the **RP slope and plateau** but **not the tail**; reproducing the favorable tail needs α_single ≈ 0.99, not exactly 1 (verified: the engine with a_s=1 gives 0 % near-surface mass and no tail).

**Unfavorable tails — mostly safe, ONE fitted condition is not.** PV > 5 tails are ~10⁻² to 10⁻³ for GB (all IS), low-IS quartz, and Tong — well above the floor. BUT high-IS quartz dips low: **Qz Li 20 mM (0.02 M) ~4×10⁻⁵, DI ~4×10⁻⁵, Qz Tong 0.5 µm 8 m/d ~4×10⁻⁵** — real but only ~0.5–0.6 log above blank. **⚠ Of the four fitted conditions, Qtz 20 mM has its tail near the floor (~4×10⁻⁵); the tail-slope objective (W_TSLOPE = 16) there rests on near-detection data — low-confidence, and consistent with Qtz 20 mM being the flakiest in the §6z-T identifiability run.**

**Fitting rule (both media, favorable & unfavorable):** treat C/C₀ ≲ 10⁻⁵ as at/below detection (**left-censored** — the model may predict below it; do not penalize); **exclude −6 / −9.94 / −15.33 placeholders** from any fit; and **flag/down-weight any tail within ~0.5 log of the blank** (Qtz 20 mM) rather than fitting its slope as signal.

### 4b.1 ⚠ The rule above was only half implemented — MODEL-side substitution added 2026-08-28 (W.P.J.)

Excluding the placeholders was implemented. **What was NOT implemented is any constraint in the region those placeholders occupied**, so on a column whose whole elution limb is padded the fit is unconstrained there and can sit decades above the limit with nothing to stop it.

**The case that exposed it: `Li-Qtz-4m/d-1.1µm-20mM-ColM`.** Its five padded points (3.92, 3.99, 4.86, 6.94, 9.90 PV at −6.004) were dropped, leaving it the **only one of the 29 fitted unfavorable columns with ZERO BTEC points past the 4.2 PV tail mask** — its `tail_level` and `tail_slope` are exactly 0.00 in every fit. A free-α_mg fit then put the modelled effluent at **10⁻²·⁸ at 9.9 PV, more than three decades above a non-detect**, and inflated f_x 170× (0.0005 → 0.086) to do it.

**Rule now applied:** at PV ≥ 4.5, a padded point becomes a **`BTEC_ND`** row carrying its real TIME and the standard statistical substitution **0.5 × QL = 5×10⁻⁶ (log₁₀ = −5.301)** — *"in performing statistical analyses that include data below detection we replace those values with 0.5·QL"* (W.P.J.). Emitted by `Data/extract_tidy_data.py` under a separate curve name, so readers selecting `curve in ("BTEC","RP")` are unaffected.

### CSV REGENERATED 2026‑08‑28 — verified additions‑only

The workbook was supplied as a chat upload and `extract_tidy_data.py` was re‑run. **Verification before trusting it:** the sandbox baseline CSV was confirmed byte‑identical to the Box copy first, then diffed against the new output — **0 removals, 44 additions, every addition a `BTEC_ND` row, and every pre‑existing BTEC/RP row byte‑identical.** The filter restructure (`if b<0.5 and not isp(b)` → `if b<0.5: if isp(b) … else …`) had no side effect. **1486 → 1529 rows** (1 header + 1528).

**44 non‑detect points across 8 columns — and MOST OF THEM ARE FAVORABLE** (W.P.J. predicted this: *"remember the favorable condition column BTECs will also drop below QL"*):

| column | chem | µm / m·d⁻¹ / mM | ND pts | PVs |
|---|---|---|---|---|
| Tong glass ColAU | favorable | 0.1 / 8 / 50 | 7 | 4.69 – 9.90 |
| Tong glass ColB | favorable | 0.2 / 4 / 50 | 7 | 4.69 – 9.90 |
| Tong glass ColBB | favorable | 0.2 / 8 / 50 | 7 | 4.69 – 9.90 |
| Tong quartz ColO | favorable | 0.5 / 8 / 50 | 7 | 4.69 – 9.90 |
| Tong glass ColL | favorable | 0.5 / 4 / 50 | 6 | 5.52 – 9.90 |
| Li quartz ColB | favorable | 0.98 / 2 / 10 | 6 | 4.71 – 9.11 |
| **Li quartz ColM** | **unfavorable** | 1.1 / 4 / 20 | **3** | 4.86, 6.94, 9.90 |
| **Tong quartz ColR** | **unfavorable** | 0.5 / 8 / 50 | **1** | 9.90 |

**AU and BB are exactly the "favorable small colloids with near‑total removal, GB Tong 0.1 / 0.2 µm 8 m/d" that §4b predicted** would be saturated non‑detects. Five of the six favorable are 50 mM.

**Two corrections to the pre‑run estimate:**
1. **ColM yields 3 ND rows, not 5** — the 4.5 PV cutoff excludes its 3.92 and 3.99 PV points exactly as designed. ("5 padded cells" ≠ "5 emitted rows".)
2. **`Tong quartz ColR` is newly affected and IS in the fitted 29.** Unlike ColM it already has **7 real tail points out to 9.06 PV**, so its single ND point at 9.90 adds a constraint **beyond** its data rather than filling a gap. Its tail sits at ~4×10⁻⁵ — the third column §4b flags as near‑blank — and it evidently fell under the QL by 9.90 PV. **So applying `BTEC_ND` to the master will touch TWO of the 29, not one.**

**⚠ The favorable columns matter for Table 5.** `favorable_both_models.py` selects `curve in ("BTEC","RP")`, so it is unaffected as it stands. But §4b's argument that the favorable washout tail (~10⁻⁴·²) is REAL and above the blank clearly does **not** hold for these six: their effluent went below the QL. Any future use of the favorable tail — including the α_single ≈ 0.99 reasoning — must exclude or censor them.

* **Why PV ≥ 4.5.** ColM's first two padded points sit at 3.92 and 3.99 PV, and honouring them would demand the effluent fall **2.6 decades in 0.07 PV** (from −3.39 at 3.854 PV), which no elution curve does. The 4.5 PV cutoff excludes them without a special case.
* **Cost: none.** With the substitution imposed, ColM's fits stay at cost 0.72–0.74 and the modelled effluent tracks −5.30 instead of −2.8; f_x returns to 0.0008.
* **⚠ Optimiser note.** A one-sided form of this penalty is flat below the target, so the Jacobian is singular there and **cold starts stall** (observed: cost 38.98 reported where a 0.72 solution existed). Warm-start from the uncensored solution. The two-sided substitution does not have this problem and is what is adopted.

**Audit of the other 28 (2026-08-28):** **no column fits sub-detection data as signal** — zero surviving tail points below 10⁻⁵ anywhere. ColM is not a counterexample to that count; it is the reason the count is clean, since its below-QL points were removed before they could be counted. So this rule is a **no-op for 28 of 29** and binds only on ColM.

**Two numbers in 4b that the audit refines:**
1. The measured tail minima for Qtz Li 20 mM are **ColP −4.86 (1.4×10⁻⁵) and ColS −4.54 (2.9×10⁻⁵)**, i.e. lower than 4b's "~4×10⁻⁵". Both are still **above** the QL, but ColP has 5 of its 7 tail points inside the 0.5-log near-blank band, so 4b's concern is if anything understated. **ColP's tail slope is still fitted at full weight (W_TSLOPE = 16) — down-weighting remains an open decision.**
2. `unfav_master_fit.py` floors data and model at log₁₀ C/C₀ = **−6** and calls it "detection limit". That is **a decade below the measured QL of −5**. It is inert in practice (no data reaches it), so it is a comment error rather than a fitting error — but the label should be corrected.

**NOT yet applied to `unfav_master_fit.py`.** Doing so changes ColM's master fit (cost 0.72 → 0.74, f_x 0.0005 → 0.0047) and would require regenerating `UnfavorableMaster.xlsx` and everything downstream of it. Deliberately deferred.

## 4c. Column-specific corrections & exclusions — GB Tong (W.P.J., 2026-08-10)

**⚠ +1 PV injection-start offset — SUBTRACT 1 PV.** GB Tong columns **AN** (1.1 µm, 4 m/d), **BK** (0.2 µm, 8 m/d), **CL** (2.0 µm, 8 m/d) have PV axes starting ~1 PV late (breakthrough ~2 PV, washout ~5 PV, vs the normal ~1 / ~4). **Injection began at 1 PV for these runs**, so **subtract 1 PV** from their PV vector to align with the rest. (On the printed grid the offset isn't a uniform additive — these were sampled on a different time grid — but the physical correction is −1 PV.) Left uncorrected, AN reads a spurious "heavy tail" (its washout falls inside a PV 5–9 window) and BK/CL misregister against their replicates.

**⚠ EXCLUDE — downgradient (series-connected) columns.** **THREE** Tong stripes are the **downgradient** column of a connected pair, so they received a population **already filtered by the upgradient column**, not fresh influent. **These are exactly the three +1-PV-offset columns above** — a downgradient column's injection effectively begins ~1 PV late because it receives the upgradient column's effluent, which is *why* they carry the +1 PV shift:
- **AN–AP** (1.1 µm, 4 m/d) — downgradient. ⚠ **Added 2026-08-11 (W.P.J.):** previously flagged only for the +1 PV offset; it is downgradient and must be **excluded**, like BK and CL.
- **BK–BM** (0.2 µm, 8 m/d) — downgradient of **BH–BJ**
- **CL–CN** (2.0 µm, 8 m/d) — downgradient of **CI–CK**

Their RPs are anomalously **flat** vs the single-column runs. **Remove all three from single-column analysis.** After removal, the standalone unfavorable elution-normal replicates are: **1.1 µm 4 m/d = AQ** (with the Li GB 20 mM 1.1 µm run as the matched anchor); **0.2 µm 8 m/d = BE / BH / BN**; **2.0 µm 8 m/d = CI / CO / CV**. *(Rule of thumb: the three +1-PV columns AN / BK / CL are the downgradient set — exclude them all.)*

**Note for posterity — α-heterogeneity in the colloid population (NOT invoked; model does well without it).** Series-connection theory says the downgradient RP should differ from the upgradient only in **magnitude, not shape** — yet these downgradient RPs are markedly **flatter**. That points to a **distribution of attachment efficiency across the colloid population**: the upgradient column preferentially retains the "stickier" colloids, so the downgradient column receives a **less-sticky, more uniform** subpopulation (→ flatter RP). This population α-heterogeneity cannot be discounted, but the current model reproduces the data well without it, so it is **recorded for posterity only, not used.** (Relates to Li's 2-k_f a1 = 0.01 subpopulation, §5, and the small real favorable tail, §4b.)

## 4d. ✅ NOT AN ERROR — GB Tong **AB** and GB Li **E** are the SAME experiment (W.P.J., 2026-09-08)

**The two columns carry byte-identical data.** BTEC (26 points) and RP (10 points) agree exactly, as do C₀ (1.31E7) and every fitted quantity in Table 5 of `Favorable_data_and_sim.xlsx` — r_s 30.2 /m, seed 23.1, α_s 0.9745, α_m 0.2463, f_x 0.0069, tail RMS 0.156, RP RMS 0.037. Their *headers* differ on four fields:

| | `Microspheres Glass Beads Li` col **E** | `Microspheres Glass Beads Tong` col **AB** |
|---|---|---|
| label | Favorable | Favorable (pH 2) |
| IS | 0.01 M | 0.05 M |
| size | 0.98 micron | 1.0 micron |
| velocity | 4 m/day | 4 m/day |

**Provenance (W.P.J., 2026-09-08): Li ran the experiment; Tong reproduced it in her own publications.** The duplication is in the source workbook and is *intentional* — it is one dataset appearing under both authors' sheets, not a transcription error and not two independent runs. **Do not "fix" it, and do not delete either column.** W.P.J. has flagged the redundancy in the manuscript figure caption.

**What it means for counts.** The favorable set is **13 columns → 10 fitted (Model 2) → 9 independent experiments.** The 13→10 step drops GB Tong **B**, **AU**, **BB**, whose BTECs are unfittable (see §4b): all seven of their points sit at exactly −5.301, the 5E-6 detection floor, between PV 4.7 and 9.9 — nothing broke through, so they are RP-only and get k_f only. The 10→9 step is this duplicate pair. **Any statistic taken over the 10 fitted favorable columns double-counts this experiment**; use n = 9 for distributional claims, n = 10 only when describing the table's row count.

**What it means for the r_s anchors.** Both columns fall in the glass / 1.1 size class / 4 m/day anchor group, which pins Li **O**, **L**, **R** and Tong **AE**, **AK**, **AQ**. Because the data are identical the pinned value is unaffected whichever column is selected — but the two anchors are one measurement, not two, and should not be described as independent confirmation.

**Where the IS discrepancy stands.** The 0.01 M vs 0.05 M header conflict is unresolved and is *not* consequential for the fits (favorable r_s does not read IS), so it is recorded and left alone.

## 5. Prior tailing models — the manuscript's counterfactual (right-hand columns)

Columns **AI→EI** (Glass Li) and **BH→HW** (Quartz Li) are earlier attempts to explain the tail, corresponding to **Johnson et al. 2018**: `kfvar random number` (lognormal k_f), `2kf model`, `2-kf 2-layer model`, `old 2 layer model with reentrainment`, `1 layer model`.

Their own annotations: `only kf 0.01 exited!`, **`can force tailing by making fir…`**, `Can make work using two indep…`, `negated by fir = 1.0`, `negated by kf_flag = 0`, and on quartz **`2k fabricated quartz1/2/3`**.

Quantitatively the 2-kf model needs `a1 = 0.01` — **1% of the population assigned kf2 = 0.0333/hr, ~115× below the bulk kf = 3.84/hr**: an invented, nearly-non-attaching subpopulation whose size is tuned. This is *an* alternative hypothesis the interception-history model displaces, and the words "fabricated" and "force tailing" are the author's own — useful framing **against the 2-kf model**.

**⚠ BUT SEE §11: this is NOT the real competitor.** The `2-layer model with reentrainment` columns in these same sheets are the **binomial / Hilpert 2017-2018 model** — principled, parameterized from first-principle pore-scale simulations, no fabricated subpopulation, and it already produces *both* the extended tail (Hilpert 2017) and peaked RPs (H&J 2018). Framing the counterfactual as "fabricated vs measured" attacks the weaker of the two prior models and leaves the stronger one unaddressed. The honest discriminator is **δ-dwell vs heavy-tailed dwell** (§11).

## 6. Constants recovered from Johnson 2018 SI — and conflicts with current scripts

> **↪ PARTLY REDISTRIBUTED (2026-07-17).** The a-priori reconciliation of these constants now lives in **Part 2** (`part2_apriori_alpha_machinery.md`): A₁₃₂ = 7.17e-21 (glass) drives the DLVO |U_sec| chain (§1.1a), and W₁₃₂ = −58.4 mJ/m² is carried as the Johnson-2018 alternative to the van Oss −22.7 (§3.3, raises v_mob ~3.5×, conclusion unaffected). The zeta table below feeds the DLVO forward chain (0.05 M extrapolated). Retained here as the data-asset record; Part 2 is canonical for how they enter the machinery.

**Table SI-1** (pH 6.72), zeta potentials (V):

| IS (mol/m³) | 3 | 6 | 20 |
|---|---|---|---|
| CML | −6.8e−2 | −6.4e−2 | −5.0e−2 |
| Glass | — | −7.0e−2 | −5.1e−2 |
| Quartz | −9.3e−2 | −8.3e−2 | −6.9e−2 |

**Combined Hamaker A₁₃₂ (CML-collector-water):** glass **7.17e−21 J**, quartz **1.96e−20 J**.
**Table SI-2 (constant):** a₁ = 5.0e−7 m; a₂ = 2.55e−4 m; Born σ_C = 5.0e−10 m; h₀ = 1.58e−10 m; T = 293.2 K; λ_vdW = 1.0e−7 m; λ_AB = 1.0e−9 m; λ_Ste = 1.4e−10 m; ε_r = 80; z = 1; **W₁₃₂ = −5.839e−02 J/m²**; **a_cont = 3.13e−08 m**.
Heterodomains: **Pareto-distributed 120 & 240 nm radii** (Pazmiño 21).

### ⚠ Conflicts to resolve

| quantity | Johnson 2018 SI | current script | ratio |
|---|---|---|---|
| Hamaker A₁₃₂ (glass) | **7.17e−21 J** | `A = 3.84e-21` (`p_contact_reproduce.py`, "record §4a") | **1.9×** |
| Work of adhesion W₁₃₂ | **−5.839e−02 J/m²** | −0.0227 J/m² (`vmob_build.py`, van Oss w/ *standard* glass values) | **2.6×** |
| contact radius a_cont | **3.13e−08 m** | 31.1 nm (1.1 µm colloid) | ~1.01× ✓ |
| heterodomain radius | **Pareto 120 & 240 nm** | `R_HET = 90e-9` (`p_contact_reproduce.py`, "Pazmino 2014") | ~1.3–2.7× |

**§4d's flagged W uncertainty can be retired** — it warned *"the SI cites a pH-dependent table (Hamadi et al.) not reproduced in it; used standard van Oss glass values… treat W to ±~50%."* The 2018 SI gives W₁₃₂ directly. Since v_mob ∝ W^(4/3), the correction raises v_mob ~3.5× — the **v_mob ≫ v_contact conclusion is unaffected** (1800× headroom), but the absolute number should be restated. a_cont agreeing to ~1% indicates the rest of the JKR machinery is sound.
A₁₃₂ enters τ_descent linearly ⇒ v_contact scales with it; recheck §4c numbers against 7.17e−21.

## 7. Code

> **⚠ TODO — script audit (not yet done; no doc covers this).** For each script, record: **what it establishes**, **why it was built that way**, **what would break if an assumption failed**, and **which results are load-bearing for the manuscript vs scaffolding**. Natural grouping:
> - **The a-priori gates** — `p_contact_reproduce.py`, `vmob_build.py` (gates 2 and 3, and the v_mob ≫ v_contact separation). *Happel-free; unaffected by the 2026-07-15 retraction.*
> - **The extraction engine** — `alpha_extract.py`, `transient_cascade_v2.py`, `btec_closedform.py` (forward model, transient version, and its independent validator). *Happel-free; only `li_extract.py`'s rate anchor was contaminated.*
> - **The RTD seam** — `gp_held_probe.py`, `alpha_dwell_distribution.py` (the same GP distribution entering Part 1 and Part 2 from opposite sides).

In project knowledge: `transient_cascade_v2.py` (engine; **rebuilt 2026-07-14** after loss — validated against `btec_closedform.py`: plateau 0.3534 vs 0.3533, no-dwell tail reldiff 0.0%, GP-dwell 66.5%), `btec_closedform.py`, `gp_held_probe.py` (**imports `transient_cascade_v2` — upload both together**), `alpha_dwell_distribution.py`, `alpha_extract.py`, `p_contact_reproduce.py`, `vmob_build.py`.

**`Li_extract.py`** (canonical reproducer; W.P.J. saved the reconciled rerun 2026-07-16) — reproducer for the Part-1 extraction: α_single and P = α_mult·r_mult from the Li glass RPs, amplitude fixed at the eq-(4) nominal; includes the model-free mass balance, the Al-Zghoul Eqn-15 check, and the Table-1 cross-check. **r_s is read from the medium's own favorable BREAKTHROUGH plateau in the data (glass → 22.9 /m, quartz → 41.5 /m)** — not a hardcoded Happel k_f. Glass results FINAL (0.400/0.133/0.0171, P 1.751/0.981/0.042); quartz provisional. Canonical method + numbers in Part 1 §8–§9. Needs `Data/DataFromLi&Tong.xlsx` + `alpha_extract.py` + `btec_closedform.py`.
> **⚠ SUPERSEDED — the older `li_extract.py` (lowercase, built 2026-07-14)** hardcoded `KF_GLASS = 3.838` / `KF_QUARTZ = 7.677` and "scanned both r_s branches"; its RESULTS were retracted 2026-07-15 (workbook-route rate). It is superseded by `Li_extract.py` above (r_s from the favorable plateau; glass reinstated). See the §0 breadcrumb.

**Minimum upload set for the identifiability test:** `transient_cascade_v2.py` + `btec_closedform.py` + `gp_held_probe.py` + `DataFromLi_Tong.xlsx`.
**Minimum upload set to reproduce the extraction:** `li_extract.py` + `alpha_extract.py` + `btec_closedform.py` + `DataFromLi_Tong.xlsx`.

## 8. Papers still wanted

**All previously requested references were delivered** and are on the local device in **`Papers/`** *(⚠ de-staled 2026-07-17: the old `/mnt/project/` online-project-knowledge path is obsolete — this is now a local-device workflow, files are real binaries in `Papers/` and `Data/`)*: Al-Zghoul 2025 (see §10), Hilpert & Johnson WRR 2018, Johnson & Hilpert WRR 2013, Li et al. EST 2004, Li & Johnson EST 2005, Volponi et al. 2024 + SI.

**Still wanted / not yet read:**

1. ~~**Hilpert & Johnson, WRR 2018**~~ — **READ 2026-07-14, see §11.** A binomial model over collector encounters with per-encounter probabilities (p_pa = α₁, p_na = α₂, p_np = α_reentrain, p_nn = α_RFSZ·α_trans) that **emergently predicts peaked RPs**. Structurally very close to the interception-history cascade (binomial over encounters vs Poisson/gamma cascade over interception counts; both give peaked RPs from per-encounter probabilities with no fabricated subpopulation). *"How is this different from Hilpert & Johnson 2018?" is a first-round reviewer question.* Needed for positioning.
2. **Johnson & Hilpert, WRR 2013** (`JohnsonandHilpertWRR2013.docx`) — **IN PROJECT, NOT YET READ.** The upscaling behind Johnson-2018 eqs (2)–(3), i.e. behind k_f, k_f2, and hence r_s — and hence behind the 2× favorable ambiguity.
2b. **Hilpert, Rasmuson & Johnson, WRR 2017** (`HilpertetalWRR2016-2016-11-13.rtf`, the 2016 draft) — **IN PROJECT, structure read (§11); full read outstanding.** *Emergent prediction of EXTENDED TAILING* — the direct precursor to the manuscript's tail claim.
3. **Li et al. EST 2004** (`LietalEST2004.pdf`) and **Li & Johnson EST 2005** (`LiJohnsonEST2005.pdf`) — **IN PROJECT, NOT YET READ.** Should pin C₀, segment volume V, t₀, and the favorable convention directly, and may settle the 2× favorable fork outright.
4. **Volponi et al. 2024 + SI** (`Volponietal2024-Re-Re-Revised-Clean.docx`) — **IN PROJECT, NOT YET READ.** The ξ ≈ 0.31 GP shape.
5. **Pazmiño et al. 2014** (Johnson-2018 ref 21) — **still not supplied.** Needed to settle 90 nm vs Pareto 120/240 nm heterodomain radii (§6 conflict).

**Retired:** Johnson 2018 **Table 1** — recovered, transcribed in §3a. The 3 PV / 7 PV durations — confirmed in Johnson 2018 main text. **Al-Zghoul** — delivered and read (§10).

---

## 9. ⚠⚠ THE α₁/α₂ NAME COLLISION — read this before using any α₁/α₂

> **↪ REDISTRIBUTED (2026-07-17).** Canonical home for this discipline is now the **overview glossary** (`overview.md` §3), where it is cross-cutting. Retained below for provenance (the full proof table); the overview carries the working statement.

**Two papers in this project's own bibliography use the symbols α₁ and α₂ for different physical objects. They are NOT interchangeable, and substituting one for the other produces a demonstrably wrong prediction (proof below).**

| source | α₁ means | α₂ means |
|---|---|---|
| **Al-Zghoul 2025** (Eqns 12–15) | attachment fraction at interception **1** — i.e. **α_single** | attachment fraction at interception **2** — i.e. **α_mult** |
| **Johnson 2018** (Table 1, eq 1) | **fast-arrest fate fraction** (= *p_pa*, "attachment from bulk fluid" in Hilpert & Johnson) | **slow-arrest fate fraction** (= *p_na*, "attachment from near surface") |
| **the working record** | *uses Al-Zghoul's notation while sourcing Johnson-2018's values* — "the α_single/α_mult targets α₁/α₂" from "Happel Table 1" | |

Al-Zghoul's α_j indexes **interception order** (α_j varies as j = 1, 2, 3…, one channel).
Johnson 2018's α₁/α₂ are **two channels available at every near-surface entry**, summing with α_reentrain and α_RFSZ to 1 (eq 1). Different cut entirely.

**✅ VERIFIED AT BOTH SOURCES 2026-07-15** (both PDFs now readable on disk): **Al-Zghoul 2025 Eqn 14–15** indexes α by *interception order*; **Hilpert & Johnson 2018 §2.2 eq (1)–(2)** defines `p_pa = η₀·α` (attach from bulk) and `p_na = α` (attach from NSFD), the fate channels. The proof below reproduces numerically from the raw data.

⚠ **Normalization caveat.** §0 identifies α₁ with `p_pa`, but `p_pa = η₀·α` is **per-injected colloid**, whereas Table 1's α's are **per-interceptor** (§3a: denominators 1538 / 386). The identification is loose by a factor of η₀ — fine as a label, but do not use it to convert between the two.

**Also from H&J 2018 §2.2, worth knowing:** the paper explicitly permits `γ_r` and `α` in eq (2) to differ from eq (1), "because colloids entering a unit cell can behave differently depending on whether they emanate from bulk pore water or the NSFD." **That is the α_single ≠ α_mult statement, in the prior literature** — consistent with §11's honest-novelty framing. Do not present α_single ≠ α_mult as new.

### PROOF that they are not interchangeable

Al-Zghoul **Eqn 15** gives the RP slope at the inlet:
```
dC_att(x)/dx |_{x=0} = C₀ (k_f/⟨v⟩) ( α₂(1−α₁) − α₁ )
```
⇒ **peaked ⟺ α₂ > α₁/(1−α₁)**; exponential/multi-exponential otherwise. (If α₁ ≥ 0.5, always exponential/multi-exp.)

Substituting **Johnson 2018 Table 1's** α₁/α₂ (§3a) into Al-Zghoul's Eqn 15:

| case | α₁ | α₂ | α₁/(1−α₁) | Eqn-15 predicts | **OBSERVED** |
|---|---|---|---|---|---|
| glass 6 mM | 0.00325 | 0.00910 | 0.00326 | peaked | **hyper-exponential** ❌ |
| glass 20 mM | 0.0100 | 0.0650 | 0.0101 | peaked | **hyper-exponential** ❌ |
| quartz 3 mM | 0.00528 | 0.01319 | 0.00530 | peaked | peaked ✓ |
| quartz 6 mM | 0.00510 | 0.02570 | 0.00513 | peaked | peaked ✓ |
| quartz 20 mM | 0.0169 | 0.1460 | 0.0172 | peaked | peaked ✓ |

**Eqn 15 predicts peaked glass beads. Glass beads are hyper-exponential — the central observation of Johnson 2018.** Quartz "passes" only because it is peaked anyway, so it cannot discriminate. **Do not feed Johnson-2018 α₁/α₂ into Al-Zghoul expressions.**

### Actions
- **Manuscript:** make the α_single/α_mult ⇄ α₁/α₂ bridge explicit, and say which paper's α₁/α₂ is meant at every use. A reviewer who knows either paper will read the symbols their way.
- **Extraction:** the α_single/α_mult "targets" cannot simply be read off Johnson-2018 Table 1. What Table 1 legitimately supports is the **total** attachment probability α₁+α₂ per near-surface entry (validated in §3a against the plateaus), not the per-interception-order split.

---

## 10. Al-Zghoul 2025 — the foundation paper (Eqn 11 / Eqn 14)

> **↪ REDISTRIBUTED (2026-07-17).** The **equations** (Eqn 8/11/14/15) now live in **Part 1** (`part1_extraction.md` §2, "Foundation kernel"), where the cascade specializes them; the **degeneracy-is-our-extension** and **k_f-invariance** framing is in Part 1 §2/§6 and **overview** §2/§4. Retained below for provenance (the verified restatement + the SCOPE/2D-3D and three-explanations notes).

**Al-Zghoul, B.M.; Johnson, W.P.; Bolster, D.** *A Paradigm Shift in Colloid Filtration: Upscaling from Grain to Darcy Scale.* **ARC Geophysical Research (2025) 1, 9.** *(In project knowledge as `AlZghouletalArchGeophysRes2025UpscalingInterception.pdf`.)*

**Definition to state in the manuscript:** an **interception** = a colloid entering the near-surface zone **within 200 nm** of a collector. This is what makes "interception count" well-posed.

### The equations — VERIFIED against the doc set's restatement

```
Eqn 8   C_att(x,n)/C_n^att = [ (k_f x/⟨v⟩)^(n−1) / (n−1)! ] · exp(−k_f x/⟨v⟩)          [the gamma/Erlang per-order kernel]
Eqn 11  C_att(x) = α C₀ exp( −α k_f x/⟨v⟩ )                                            [constant α ⇒ exponential, shallower by α]
Eqn 14  C_att(x) = C₀ exp(−k_f x/⟨v⟩) · Σ_{n=1..Ni} [ (k_f x/⟨v⟩)^(n−1)/(n−1)! ] · α_n · Π_{j=1..n} (1−α_{j−1})
Eqn 15  dC_att/dx|_{x=0} = C₀ (k_f/⟨v⟩) ( α₂(1−α₁) − α₁ )                              [see §9]
```
Eqn 11 is the Ni→∞ limit of Eqn 10 via the Taylor series; constant α in Eqn 14 recovers Eqn 11.

**Amplitude convention (benign, but real):** Al-Zghoul's Eqn 11 amplitude is **αC₀**; `alpha_extract.py` uses **α·r·C₀** (r = k_f/⟨v⟩) — the mass-conserving form, consistent with Johnson 2018 eq (4), which also carries the k_f factor. `alpha_extract.py`'s comment already flags this ("up to the kf/v amplitude convention"). Constant offset only.

### ⚠ SCOPE — Al-Zghoul is 2D SIMULATION, not the Li columns

Validation cases come from ref [3] (**Al-Zghoul, Johnson & Bolster**, *A training trajectory random walk model…*, Adv. Water Resour. 2025): **pore-assembly trajectory simulations** in *The One Piece for Particle Tracking*, on a **2D domain** — grains **200 µm**, porosity **0.54** (a 2D disc packing), colloids 1.1 µm. **SCOV = 0.15–0.45%** with α = 0.96/0.25/0.13/0.11 (Al-Zghoul Table 1).

Compare the Happel/Li work: **SCOV = 1e−5 = 0.001%** — **150–450× lower** — with Johnson-2018 Table 1 α's of 0.003–0.15, i.e. ~10–100× below Al-Zghoul's. Consistent with the SCOV gap, but **reconcile before quoting α's from the two sources in the same breath**. (The working record already flags the related point that column SCOV is ~40× below the impinging-jet 0.04% ⇒ ρ is collector-geometry-dependent.)

So the lineage is **2D pore-assembly sims → Eqn 11/14 → applied to 3D columns** (510 µm glass beads / quartz sand). Same 2D→3D jump the project already tracks for the RTD (`gp_held_probe.py` scales Volponi-2D ~11 s to Li-3D ~130 s).

### ⚠ Al-Zghoul has NO rate change — the degeneracy is OUR extension

**Eqn 14 carries a single k_f.** α_j varies with interception order; the delivery rate does not. There is no η_mult and no r_m in Al-Zghoul. Therefore:
- The manuscript's two-state model (r_s, r_m, α_s, α_m) is a genuine **extension** of Al-Zghoul.
- **The α_mult·η_mult degeneracy does not exist in Al-Zghoul — it is created by our extension.** Frame §3 accordingly: the degeneracy is the price of testing an assumption Al-Zghoul made, not an inherited defect.

### The k_f-invariance assumption — an educated guess, and Johnson 2026 refutes it (2D, with 3D-Happel exit-focusing)

Al-Zghoul §4 argues:
> While the spatial variation of α is primarily driven by the physics inside the NSZ, **k_f is less likely to vary across the transport domain** due to its dependence on bulk fluid delivery… this effect is expected to diminish downstream after a few grains, **particularly in the 2D geometry used in their study**… we **propose** that spatial variability in α constitutes a plausible, **although not necessarily exclusive**, mechanism.

**This is an educated guess, not a measurement** (confirmed by W.P.J., 2026-07-14), and the paper hedges it throughout ("less likely," "expected to," "propose," "not necessarily exclusive").

**Johnson 2026 measures — in 2D experiments/simulations (with 3D-Happel single-grain corroboration) — that η is ~2× higher for multiple interceptors.** So the guess is refuted **in the very geometry where Al-Zghoul expected it to hold most strongly**. The manuscript is not contradicting a result; it is reporting that an explicitly provisional assumption failed when tested. Al-Zghoul left the door open ("not necessarily exclusive").

**Where the real exposure is:** η_mult is measured **once, in 2D** (Johnson 2026), imported into a **3D** column model, and is **degenerate against α_mult in every steady observable** (extraction-model §3). So the imported scalar cannot be checked against the data it is applied to. *That* is why the BTEC tail is a workstream — it is the only observable that can separate them. **Do not defend the extension with "3D geometry is richer than 2D"** — neither paper supports that, and the focusing evidence is itself 2D.

### Three competing explanations for non-exponential RPs now live in this doc set

| paper | mechanism |
|---|---|
| **Johnson 2018** | grain-contact geometry (angularity, grain-to-grain contacts) → α_trans (0.25 glass vs 0.5 quartz) → translation |
| **Al-Zghoul 2025** | α varies across interceptions; k_f does **not** |
| **this manuscript (2026)** | **both** — α_mult *and* η_mult (focusing) |

The manuscript is the only one claiming both. Address the tension explicitly rather than leaving it to a reviewer.


---

## 11. ⚠⚠ THE LINEAGE — what is actually new in this manuscript

> **↪ REDISTRIBUTED (2026-07-17).** Canonical home is now **overview** §2 (the novelty legs, the exact δ-dwell↔heavy-tailed one-liner, the NOT-novel list) and §4 (the lineage chain). The **KEY-FIGURE forward-predictive recipe** and the **generalization/wedge** gates are in **Part 1** §6/§10. The strategy-summary boundary-rule box below is obsolete (that doc dissolved into the overview, which now owns the accessibility argument). Retained below for provenance (the H&J-2018 binomial correspondence table + the precedent note).

**Read before writing any novelty or positioning claim.** Both of the manuscript's headline anomalies — the extended BTEC tail and the peaked RP — **already have near-surface-residence explanations inside this program's own prior work.** This is a lineage (W.P.J. is an author throughout), not a priority dispute, but a reviewer will ask "what is new here?" and the answer must be precise.

### The chain

| paper | contribution | in project? |
|---|---|---|
| **Johnson & Hilpert, WRR 2013** | upscaling framework; FFSZ/RFSZ, grain-network intersection | `JohnsonandHilpertWRR2013.docx` — **unread** |
| **Hilpert, Rasmuson & Johnson, WRR 2017** (53, 5626–5644) *"…Emergent prediction of extended tailing"* | binomial network → RTD → **EXTENDED TAILING from NSFD residence**. Mechanism: *"Inter-grain transport of colloids in the near surface fluid domain can cause extended tailing."* | `HilpertetalWRR2016-2016-11-13.rtf` (2016 draft) ✓ |
| **Hilpert & Johnson, WRR 2018** (54, 46–60) *"…Emergent prediction of nonmonotonic retention profiles"* | binomial network → **PEAKED RPs**; α may differ by origin | `HilpertJohnsonWRR2018NonmonotonicProfiles.pdf` ✓ |
| **Johnson, Rasmuson, Pazmiño & Hilpert, ES&T 2018** | trajectory-sim RTDs → hyper-exponential RPs via two subpopulations (α₁/α₂ fate partition) | ✓ (§3a, §6) |
| **Al-Zghoul, Johnson & Bolster 2025** | interception-order cascade, Erlang kernel, variable α_j, **single k_f** | ✓ (§10) |
| **Johnson 2026** (in review) | interception focusing, **2D experiments + 2D and 3D-Happel sims**, η_mult ≈ 2× | ✓ |
| **this manuscript** | see below | — |

### The Hilpert & Johnson 2018 binomial model (structure)

1-D network of Happel unit cells; three states **p** (bulk pore water), **n** (NSFD), **a** (attached, irreversible); six transfer probabilities each with a characteristic transfer time (tpp, tpn, tpa, tnp, tnn, tna):

```
ppp = 1−η₀+η₀ηr     ppn = η₀(1−ηr−α)     ppa = η₀α        [from bulk]
pnp = ηr            pnn = 1−ηr−α         pna = α          [from NSFD]
```

**Their own words, immediately after eq (2):**
> We note that in equation (2) one can potentially use *ηr* and *α* that **differ from those used in equation (1)**. This is because **colloids entering a unit cell can behave differently depending on whether they emanate from bulk pore water or the NSFD.**

**That is α_single ≠ α_mult, stated in 2018.** The correspondence:

| Hilpert & Johnson 2018 | this manuscript |
|---|---|
| ppa = η₀·α — bulk-origin colloid attaches | **α_single** |
| pna = α — NSFD-origin colloid attaches | **α_mult** |
| "one can use α that differs" between (1) and (2) | the α_single ≠ α_mult claim |
| pnn — NSFD→NSFD transfer to the next cell | the delivery advantage of multiple interceptors ≈ **η_mult** |
| tnn, tna — characteristic transfer times | **the near-surface dwell** |
| binomial over unit cells → RTD | gamma/Erlang cascade over interception counts → BTEC |

Peaked criterion (H&J 2018): *"those cases where interception, η₀, is sufficiently large relative to attachment, α, as well as reentrainment, ηr, to maintain an NSFD colloid population."* — **a different criterion from Al-Zghoul Eqn 15 (α₂ > α₁/(1−α₁)) for the same phenomenon.** Worth reconciling.

### ✅ THE EXACT DELTA — δ-dwell vs heavy-tailed dwell

Hilpert 2017 builds its RTD by **enumerating permutations**: each permutation's residence time is the *deterministic* sum of fixed characteristic times (count of each transition × its time); permutations are then grouped and merged by identical residence time. **The tail comes entirely from the combinatorics over permutations — NOT from a dwell distribution.**

Therefore, in this project's own `btec_closedform.py` notation the relationship is **exact**:

```
Hilpert 2017      :  C(L,t) = Σ_n W_n ⊗ δ(t − t_nn)        [one characteristic near-surface time]
this manuscript   :  C(L,t) = Σ_n W_n ⊗ f^{*n}(t − L/⟨v⟩)  [f = measured heavy-tailed GP, ξ≈0.31]
```

**Same survivor weights W_n, same combinatorial skeleton. The manuscript replaces the delta with the measured distribution — it is a strict generalization of Hilpert 2017 in the dwell kernel.** (`btec_closedform.py` reproduces Hilpert 2017 by setting `mix=[(1.0, t_nn)]`.) **This one line is the cleanest available statement of what the manuscript adds.**

### What IS novel — TWO legs, state them this narrowly

**Leg 1 — SCIENTIFIC: the dwell is a measured heavy-tailed DISTRIBUTION, not a characteristic time.**
GP ξ≈0.31 (tail index ~3.2, infinite variance), shape from Volponi, magnitude from Johnson 2025. Exact, one line: Σ_n W_n ⊗ δ(t−t_nn) → Σ_n W_n ⊗ f^{*n}. The prior form *could not represent* a dwell distribution at all.

**Leg 2 — ACCESSIBILITY: the physics is recast in a tractable, standard form. THIS IS THE POINT OF THE PROGRAM, not a secondary benefit.**

> ### ⚠ BOUNDARY RULE — `interception_history_paper_strategy_summary.md` OWNS THIS ARGUMENT
> **That document is CANONICAL for adoption strategy, the tool, the target audience, and the wedge.** It is the project's first conversation and its whole thesis is accessibility. **Do not restate its argument here or in the manuscript — read it and point to it.** (v6 of this inventory restated it, worse, as though it were a new finding. Do not repeat that.)
> Its load-bearing claims, for orientation only:
> - *"A framework that changes understanding but not workflow loses to one that changes workflow — every time, regardless of correctness."*
> - The twenty-year base rate since Li & Johnson 2005: *"A twenty-year stall isn't broken by one more good entry in the series; it's broken by delivering the thing the series has promised. This paper is the experimental prerequisite to that thing — not that thing."*
> - **The wedge:** *"Reproducing the same fitted tail as HYDRUS adds nothing… the **forward-predicted location of downstream maxima** (via v/k_f) from conditions alone, before any data is supplied. Curve-fitting has no forward peak prediction; it needs the data first. That is the wedge."*
> - *"Forward-predictive, not descriptive. If it needs the RP to produce the RP, it's another regression and it loses."*
> - **The strategic gate:** *"the edifice rests on the pre-calibration generalizing… **The first money should go to the generalization test, not the interface.**"*

**What this inventory adds (new, not in the strategy summary): WHY the binomial model specifically did not propagate — it is structural, not incidental.** Hilpert 2017 builds its RTD by **enumerating permutations** of the state sequence, then grouping by identical residence time and merging probabilities. In their own words: *"Construction of a breakthrough curve is therefore computationally only tractable if the permutations are organized into groups that have the same residence time and the same probability to occur."* Exact, correct — and unusable by a practitioner and undroppable into an existing transport code.

**The cascade is the same physics as a linear ODE system with advection** — `dC_j/dx = −r_j C_j + (1−α_{j−1}) r_{j−1} C_{j−1}` — which is the native language of every transport code including HYDRUS. Combinatorial enumeration over permutations vs. an ODE system: one is a paper, the other is a module.

**And the heavy-tailed dwell reduces to machinery HYDRUS already has.** The hyperexponential representation of the GP **is a multi-site kinetic model**: `gp_held_probe.py` NNLS-fits the GP survival to 4–6 exponential components; `transient_cascade_v2.py` runs them as held states H_{j,k} releasing at g_k = 1/τ_k. That is exactly a **multi-site mobile–immobile formulation with kinetic exchange**, standard in HYDRUS for years — with the site rate constants coming from a **measured distribution** rather than being fitted. So the accessibility claim is not aspirational; the demonstration already exists in this project's code.

**⭐ PRECEDENT — accessibility already counted as NEW in this program (W.P.J., 2026-07-14; not in any document).**
**Al-Zghoul 2025 is also related to the Hilpert papers — same physics lineage — and was accepted as new because conceptually it is more accessible.** Direct evidence that recasting the Hilpert physics in tractable form is a publishable contribution in this field/venue. This manuscript stands in the same relation to Hilpert and goes further: greater accessibility **plus** the dwell distribution the earlier forms could not carry. **Without this precedent the §11 lineage table reads as a novelty problem; with it, it reads as an established pattern.**

**Leg 3 (supporting) — the BTEC tail as an IDENTIFIABILITY CHANNEL.** Separating η_mult from α_mult. H&J never face this degeneracy (they never parameterize focusing); Al-Zghoul never faces it (single k_f). **The degeneracy is created by this manuscript's extension** (§10); the tail is its resolution.

**Leg 4 (supporting) — the a priori α program** (three gates: find / contact / arrest) predicting α's *level* from physics. Nothing upstream does this.

*(Continuous x + the Erlang kernel are **Al-Zghoul's** contribution, not this manuscript's.)*

### The positioning that follows

Do **not** claim to have discovered that the tail comes from near-surface residence — Hilpert 2017 did, and it is that paper's title. **Claim instead:** the demonstration was correct but unusable; this form is usable, *and* it carries the measured dwell distribution the earlier form could not represent. That is defensible, honest, has precedent (Al-Zghoul 2025), and converts Hilpert 2017/2018 from a threat into the setup.

### ⚠ NOT novel — do not claim

- That α depends on interception history (**H&J 2018, explicit**).
- That multiple interceptors are delivered more readily than fresh bulk colloids (**H&J's pnn**).
- That the extended BTEC tail arises from near-surface residence (**Hilpert 2017, the paper's title**).
- That peaked RPs arise from NSFD accumulation (**H&J 2018**; *"To the best of our knowledge, this is the first model to a priori predict the transition from monotonic to nonmonotonic profiles."*).

### ⚠ THE COUNTERFACTUAL FRAMING IS CURRENTLY WRONG (see §5)

§5 frames the alternative as the **2-kf model** with its fabricated subpopulation (`a1 = 0.01`, kf2 ~115× below kf; annotations *"can force tailing by making fir…"*, *"2k fabricated quartz"*). That argument works against the 2-kf model. **It does NOT work against the binomial / 2-layer model**, which is principled, parameterized from first-principle pore-scale simulations, and already produces both anomalies. The `2-layer model with reentrainment` columns in `DataFromLi_Tong` **are** that approach (i.e. Hilpert 2017/2018).

**So the real competitor is not the fabricated model — it is this program's own 2017/2018 binomial model, and the honest discriminator is δ-dwell vs heavy-tailed dwell (plus accessibility), not fabricated vs measured.** Reframe accordingly.

### ✅ Markus Hilpert's binomial code is NOT needed

For positioning or for the comparison figure. **`btec_closedform.py` with `mix=[(1.0, t_nn)]` gives the δ-dwell limit of this manuscript's own model** — the fair comparison: same survivor weights W_n, same skeleton, one kernel swapped. Obtaining his implementation would validate *his* paper, not test this one.

**⚠ Caveat to state carefully:** the δ-limit of the cascade is **structurally** Hilpert's model, not **byte-identically** so. He indexes by **unit cell** and tracks bulk transit times (tpp, tpn, tnp) separately; the cascade indexes by **interception count** and lumps transit into L/⟨v⟩. Say "setting f = δ recovers the Hilpert form" as a statement about *form*, not exact reproduction — a reviewer who knows the binomial model will check.

### ▶ THE KEY FIGURE — must be FORWARD-PREDICTIVE, not tail-matching

**⚠ Do NOT frame this as "fit two dwells to the tail."** The strategy summary rules that out by name: *"Reproducing the same fitted tail as HYDRUS adds nothing"* and *"If it needs the RP to produce the RP, it's another regression and it loses."*

**The defensible construction — zero free tail parameters:**
1. Fit the **steady RP** for α_single and the product P = α_mult·r_mult (amplitude **FIXED** per §0; r_s ⚠ **re-derive from the paper's k_f = 8.636/hr — NOT the retracted 23.0/m**).
2. **Import** the dwell — GP shape ξ≈0.31 (Volponi), magnitude ≈90–130 s (Johnson 2025). **Not fitted.**
3. **Predict** the transient tail. Steady data in ⇒ transient prediction out, nothing tuned to the tail.
4. **δ-dwell is the CONTROL**, not the point: same forward machinery, kernel swapped to `mix=[(1.0, t_nn)]` (= the Hilpert 2017 form).

This is exactly the strategy summary's demo — *"users see an **un-fit** prediction land on their own data"* — and it is the honest test of Leg 1. Everything needed is in hand: `btec_closedform.py`, `transient_cascade_v2.py`, `gp_held_probe.py`, `DataFromLi_Tong.xlsx`, §0's conditions (3 PV injection, 7 PV elution).

**The bigger prize, per the strategy summary's wedge:** the **forward-predicted position of the downstream maximum**. Note the extraction-model result that the peak position `ln(r_s/P)/(r_s−P)` depends **only** on the product P — and that **H&J 2018 also derives closed-form peak positions** (their eqs 26, 33). So forward peak prediction is not unique to this form; **accessibility is what differentiates it** (Leg 2). Do not claim the peak prediction itself as novel.

**And the strategic gate above all of it (strategy summary §3):** the generalization test — does one calibration predict a *different published experiment* on the same material pair? *"The first money should go to the generalization test, not the interface."*

### Convergence worth noting (supports a design choice)

H&J 2018's stated limitation:
> it assumes the same average pore water velocity in each unit cell, thus neglecting the effects of hydrodynamic dispersion; **however, at the same time, this allows separating the effects of hydrodynamic dispersion from those of colloid interactions with the NSFD**

This is the same reasoning behind pinning **Courant = 1** in the rebuilt `transient_cascade_v2.py` (exact one-cell advective shift ⇒ zero numerical dispersion ⇒ the tail cannot be an artifact). The design choice has precedent in the lineage.


---

*Maintenance: update when data is added, when the Happel α₁/α₂ defect or the favorable-reference ambiguity is resolved, or when a file moves between project knowledge and per-chat upload. Delete the superseded version from project knowledge — knowledge files do not auto-update. Provenance and status remain canonical in the working record §6a/§6b.*
