"""extract_tidy_data.py -- extract every USABLE experimental BTEC/RP column from DataFromLi&Tong.xlsx into one
tidy long-format CSV with full metadata + provenance. Plain text, format-independent, diff-able.
Point DATA at your local DataFromLi&Tong.xlsx.  Canonical data description: Records/data_inventory.md.

Inclusion rule (W.P.J.): keep only PRIMARY, elution-normal columns. DROP:
  * downgradient (series-connected) columns  -- flagged "downgradient" in the C0 cell (these are also the
    +1-PV-offset columns; data_inventory §4c);
  * DI (deionized) columns  -- no defined ionic strength;
  * perturbation-elution columns  -- elution cell is not "normal" (2 PV, MQ, pH 11, 0.0002 M ...).

Layout handled correctly (data_inventory §4):
  * Header/labels read across the WHOLE 3-column stripe (col c AND c+1) -- some Tong condition labels sit in
    the middle column, row 1 (would be missed by a first-column-only scan).
  * C0 row: 14 for Glass Beads Li, 8 for the other three sheets (read the cell, never scrape header text).
    Two favorable Tong cols have no C0 in the sheet -> RP-implied override (CS 1.157e6, O 5.762e6).
  * IS parses BOTH "mM" and "M" (millimolar vs molar); DI -> no IS.
  * RP rows are per sheet: Glass Beads Li 47-56, Quartz Sand Li 41-50, Tong 68-77.  (The old code read 41-50
    for both Li sheets, truncating Glass-Beads-Li RP to 4 points -- fixed.)

** THREE CURVE TYPES ARE EMITTED (BTEC_ND added 2026-08-28) **
  BTEC     measured breakthrough, log10 C/C0 vs PV
  RP       retention profile, log10 spheres vs distance_m
  BTEC_ND  ** NON-DETECT ** breakthrough points at PV >= 4.5: the TIME is real, the VALUE is the standard
           substitution 0.5*QL = 5e-6 (log10 -5.301), NOT a measurement.  Readers that select
           curve in ("BTEC","RP") are UNAFFECTED -- opt in explicitly if you want these.
           Rationale and the ColM case that motivated it: see the ND block below, and
           Records/data_inventory.md section 4b.
"""
import numpy as np, openpyxl, re, csv, functools
from openpyxl.utils import get_column_letter
print = functools.partial(print, flush=True)
DATA = "DataFromLi&Tong.xlsx"
PLACE = {-6.0, -9.94, -15.33}; isp = lambda v: any(abs(v - p) < 0.05 for p in PLACE)

# ---- NON-DETECT (censored) BTEC points -- added 2026-08-28 (W.P.J.) ----
# The placeholder fills above are software fills for "below detection", NOT measurements, so they must
# never be fitted as values (data_inventory.md section 4b).  Dropping them silently, however, THREW AWAY
# THE INFORMATION THAT THE EFFLUENT WAS BELOW DETECTION AT THAT TIME -- and on a column whose whole
# elution limb is padded, the fit is then completely unconstrained there and can sit DECADES above the
# limit with nothing to stop it.  That is exactly what happened to Li quartz 1.1 um 4 m/d 20 mM ColM:
# its five padded points were dropped, leaving ZERO tail points, and a free-alpha_mg fit put the
# modelled effluent at 10^-2.8 -- more than three decades above a non-detect.
#
# So the padded points are now emitted under a SEPARATE curve name, "BTEC_ND", carrying their PV and the
# SUBSTITUTED value 0.5 * QL.  Readers that select curve in ("BTEC","RP") are completely unaffected;
# only code that opts in sees them.
#   QL   = 1e-5 in C/C0, blank-based, both media  (data_inventory.md section 4b -- MEASURED 2026-08-10;
#          NOT 1e-4, and NOT the -6 placeholder value, which is a decade below the real limit)
#   value = 0.5 * QL = 5e-6  -> log10 = -5.301, the standard substitution for below-detection data in
#          statistical analysis (W.P.J., 2026-08-28)
#   PV cutoff = 4.5.  Padded points EARLIER than this are still dropped: ColM's first two sit at 3.92
#          and 3.99 PV, and honouring them would demand the effluent fall 2.6 decades in 0.07 PV, which
#          no elution curve does.  The 4.5 PV cutoff excludes them without a special case.
ND_QL = 1e-5; ND_VALUE = round(np.log10(0.5 * ND_QL), 4); ND_MIN_PV = 4.5
wb = openpyxl.load_workbook(DATA, data_only=True)
# C0 overrides (RP-implied / mass-balance): CS & O had no C0 in-sheet; R had the same bad placeholder 3.36E5 as O
# (its unfavorable twin). R and O are the same run (quartz 0.5 um, 8 m/d, 50 mM; pH 6.75 vs 2) -> same C0 = 8.2e6.
C0_OVERRIDE = {("Microspheres Glass Beads Tong", "CS"): 1.157e6,
               ("Microspheres Quartz Sand Tong", "O"): 8.2e6,
               ("Microspheres Quartz Sand Tong", "R"): 8.2e6}


def c0cell(ws, c, r):
    m = re.search(r'([\d.]+)\s*E\s*([+-]?\d+)', str(ws.cell(r, c).value)); return float(m.group(1)) * 10 ** int(m.group(2)) if m else None


def stripeH(ws, c, nr):  # header text over the whole stripe (cols c AND c+1), catches offset labels
    return " || ".join(str(ws.cell(r, cc).value) for r in range(1, nr) for cc in (c, c + 1) if isinstance(ws.cell(r, cc).value, str))


def elut(ws, c, erow):  # elution-condition cell (col c or c+1)
    for cc in (c, c + 1):
        v = ws.cell(erow, cc).value
        if isinstance(v, str) and re.search(r'elut', v, re.I): return v
    return ""


def parse(H, elution):
    hl = H.lower()
    chem = ("unfavorable" if re.search(r'unfavor|unfav', hl) else ("favorable" if ("favor" in hl and not re.search(r'favvia|fav via|reference', hl)) else "?"))
    sm = re.search(r'([\d.]+)\s*micron', hl); size = float(sm.group(1)) if sm else None
    vm = re.search(r'([\d.]+)\s*m/day', hl); vel = float(vm.group(1)) if vm else None
    mm = re.search(r'([\d.]+)\s*mM\b', H); Mm = re.search(r'([\d.]+)\s*M\b', H)
    if mm: IS = float(mm.group(1))
    elif Mm: IS = float(Mm.group(1)) * 1000
    elif re.search(r'\bDI\b', H): IS = "DI"
    else: IS = None
    if "downgradient" in hl: role = "downgradient"
    elif IS == "DI": role = "DI"
    elif elution and "normal" not in elution.lower(): role = "perturbation"
    else: role = "primary"
    return dict(chem=chem, size=size, vel=vel, IS=IS, role=role)


rows = []
def add(src, med, m, C0, tab, col, curve, xtype, pts):
    IS = m['IS'] if isinstance(m['IS'], (int, float)) else None
    cid = f"{med}_{src}_{m['size']}um_{int(m['vel']) if m['vel'] else '?'}mday_{int(IS) if IS is not None else '?'}mM_{m['chem'][:5]}"
    for x, v in pts:
        rows.append([src, med, m['size'], m['vel'], IS, m['chem'], cid, curve, round(x, 5), xtype, round(v, 4), C0, "primary", tab, col])


# ---- Tong tabs (PV-header scan; BTEC br+1..66 with value<0.5, RP 68..77; C0 row 8; elution row 7) ----
for tab, med in [("Microspheres Glass Beads Tong", "glass"), ("Microspheres Quartz Sand Tong", "quartz")]:
    ws = wb[tab]
    for c in range(1, ws.max_column + 1):
        br = None
        for r in range(6, 13):
            x = ws.cell(r, c).value
            if isinstance(x, str) and x.strip().upper().startswith("PV"): br = r; break
        if br is None: continue
        m = parse(stripeH(ws, c, br), elut(ws, c, 7))
        if m['role'] != "primary": continue                       # DROP downgradient / DI / perturbation
        C0 = C0_OVERRIDE.get((tab, get_column_letter(c))) or c0cell(ws, c, 8)  # override FIRST (R's recorded 3.36E5 is wrong)
        bt = []; rp = []; nd = []
        for r in range(br + 1, 67):
            a = ws.cell(r, c).value; b = ws.cell(r, c + 1).value
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b < 0.5:
                if isp(b):
                    if float(a) >= ND_MIN_PV: nd.append((float(a), ND_VALUE))   # below detection: keep the TIME
                else:
                    bt.append((float(a), float(b)))
        for r in range(68, 78):
            a = ws.cell(r, c).value; b = ws.cell(r, c + 1).value
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isp(b): rp.append((float(a), float(b)))
        # ALL RP data has exactly 10 depth points, always (W.P.J., 2026-09-01) -- assert, don't silently truncate.
        if rp: assert len(rp) == 10, f"RP truncated: {tab} col {get_column_letter(c)} got {len(rp)} points, expected 10"
        if bt: add("Tong", med, m, C0, tab, get_column_letter(c), "BTEC", "PV", bt)
        if rp: add("Tong", med, m, C0, tab, get_column_letter(c), "RP", "distance_m", rp)
        if nd: add("Tong", med, m, C0, tab, get_column_letter(c), "BTEC_ND", "PV", nd)

# ---- Li tabs (per-sheet: header rows, elution row, C0 row, RP rows) ----
for tab, med, nr, erow, c0row, rpr in [
        ("Microspheres Glass Beads Li", "glass", 15, 13, 14, (47, 57)),
        ("Microspheres Quartz Sand Li", "quartz", 9, 7, 8, (41, 51))]:
    ws = wb[tab]
    for c in range(1, ws.max_column + 1):
        Hc = " || ".join(str(ws.cell(r, c).value) for r in range(1, nr) if isinstance(ws.cell(r, c).value, str))
        if not (re.search(r'micron', Hc, re.I) and re.search(r'm/day', Hc, re.I)): continue   # real condition columns only
        m = parse(stripeH(ws, c, nr), elut(ws, c, erow))
        if m['role'] != "primary": continue                       # DROP DI / perturbation (no downgradient in Li)
        C0 = c0cell(ws, c, c0row)
        bt = []; rp = []; nd = []
        for r in range(10, 45):
            a = ws.cell(r, c).value; b = ws.cell(r, c + 1).value
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b < 0.5:
                if isp(b):
                    # placeholder = below detection. Keep the TIME, substitute 0.5*QL for the VALUE.
                    if float(a) >= ND_MIN_PV: nd.append((float(a), ND_VALUE))
                else:
                    bt.append((float(a), float(b)))
        for r in range(*rpr):
            a = ws.cell(r, c).value; b = ws.cell(r, c + 1).value
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b > 0.5 and not isp(b): rp.append((float(a), float(b)))
        # ALL RP data has exactly 10 depth points, always (W.P.J., 2026-09-01) -- assert, don't silently
        # truncate. This is the invariant that motivated the 2026-08-28 rpr fix above in the first place.
        if rp: assert len(rp) == 10, f"RP truncated: {tab} col {get_column_letter(c)} got {len(rp)} points, expected 10"
        if bt: add("Li", med, m, C0, tab, get_column_letter(c), "BTEC", "PV", bt)
        if rp: add("Li", med, m, C0, tab, get_column_letter(c), "RP", "distance_m", rp)
        if nd: add("Li", med, m, C0, tab, get_column_letter(c), "BTEC_ND", "PV", nd)

hdr = ["source", "medium", "colloid_um", "velocity_mday", "IS_mM", "chemistry", "condition_id", "curve", "x", "x_type", "value", "C0_per_mL", "column_role", "workbook_tab", "workbook_col"]
with open("LiTong_experimental_data_tidy.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
nnd = sum(1 for r in rows if r[7] == "BTEC_ND")
ndc = {(r[13], r[14]) for r in rows if r[7] == "BTEC_ND"}
print(f"wrote LiTong_experimental_data_tidy.csv : {len(rows)} rows, {len({r[14] for r in rows})} columns, {len({r[6] for r in rows})} conditions")
print(f"  BTEC_ND (non-detect, value = 0.5*QL = {10**ND_VALUE:.1e}, PV >= {ND_MIN_PV}): {nnd} points across {len(ndc)} column(s)")
for tab, col in sorted(ndc): print(f"    {tab} col {col}")
