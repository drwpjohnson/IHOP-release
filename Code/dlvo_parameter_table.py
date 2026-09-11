"""dlvo_parameter_table.py -- the physicochemical parameter table behind |U_sec| and Kramers escape,
for every colloid size and ionic strength in the Li/Tong set.

Asked for by W.P.J. 2026-08-26 while working on a-priori prediction of the IHOP parameters: one sheet
that lays out every constant, zeta potential and Hamaker constant that feeds |U_sec| and the Kramers
escape rate, across all sizes and all ionic strengths, so the inputs can be inspected and varied.

WHERE THE PHYSICS COMES FROM -- NOT RE-IMPLEMENTED.
  * |U_sec| : the h-grid, the h > 8 nm mask and the two energy terms are copied verbatim from
    `fx_vs_usec.usec()`, which `fx_trend.py` imports as the single source. This script reproduces
    that function's result exactly AND additionally returns h_sec, which the original discards.
    A self-check against the imported function runs on every build and aborts on any mismatch.
    (Measured 2026-08-26: 35 cases, max |diff| = 0.0e+00 kT.)
  * Kramers: `dlvo_kramers_size.py` -- D = kT/(6 pi mu a), k_r = D * kappa^2 * exp(-|U_sec|/kT).
  * zeta and Hamaker: `fx_trend.py` ZETA_COLLOID / ZETA_COLLECTOR / A_HAM, from Johnson 2018 Table
    SI-1 (provenance in data_inventory section 6).

** THE TWO ZETA GAPS ARE REAL AND ARE LEFT BLANK. ** Table SI-1 gives colloid and collector zeta at
6 / 20 / 50 mM and the QUARTZ collector at 6 / 20 mM only. So there is no zeta at 1, 3 or 10 mM for
anything, and none for quartz collector at 50 mM. Those rows carry no |U_sec| and no Kramers rate.
Do NOT invent values to fill the grid -- the 3 mM gap matters because 3 mM is in the manuscript, and
it needs a measured or interpolated zeta, flagged as such. (fx_trend.py docstring, "TWO ZETA GAPS".)

FORMULAS, NOT PASTED NUMBERS. Every derived quantity in the workbook is a live Excel formula reading
the constants and lookups, so changing a zeta or a Hamaker constant updates the sheet. The ONE
exception is h_sec, the separation at which the secondary minimum sits: finding it is a numerical
minimisation over a 70 000-point grid, which a cell formula cannot do. h_sec is therefore written as
a value, in blue, and every energy in that row is a formula evaluated AT that h. If you change a
zeta materially, h_sec shifts a little and should be re-derived by re-running this script.

VERIFIED 2026-08-26: 813 formulas, 0 error cells, and the workbook's |U_sec| column agrees with this
file's Python computation to 2.8e-14 kT on all 35 evaluable rows. The workbook reproduces the two
published results it should: |U_sec| 0.178 -> 3.552 kT over 0.1-2.0 um at 20 mM glass, and a 584x
anchored-Kramers size swing against a fitted k_r that is flat in size.

NOTE ON RECALCULATION. The xlsx skill's `recalc.py` hangs on this workbook (LibreOffice itself opens
and converts it in 0.3 s, so it is the UNO path, not the file). Recalculate instead with a plain
round-trip, which caches every value and preserves formulas and formatting:
    soffice --headless --norestore --convert-to xlsx DLVO_Kramers_parameters.xlsx --outdir out/

Usage:  python3 dlvo_parameter_table.py [--outdir .]
Writes DLVO_Kramers_parameters.xlsx (5 sheets: Constants, Zeta_Hamaker, Usec_grid, Kramers, Equations).
"""
import argparse, os, sys
import numpy as np
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------- physics, mirroring fx_vs_usec.py
e = 1.602e-19; kB = 1.381e-23; T = 293.2; kT = kB * T
eps0 = 8.854e-12; epsr = 80.0; NA = 6.022e23; z = 1.0; lam = 100e-9
mu = 1.0e-3                                    # water dynamic viscosity, Pa s (dlvo_kramers_size.py)
_h = np.linspace(2e-9, 140e-9, 70000)          # identical grid to fx_vs_usec.usec()
H_MIN = 8e-9                                   # secondary minimum searched beyond 8 nm

A_HAM = {"glass": 7.17e-21, "quartz": 1.96e-20}
ZETA_COLLOID = {6.0: -0.064, 20.0: -0.050, 50.0: -0.040}
ZETA_COLLECTOR = {"glass": {6.0: -0.070, 20.0: -0.051, 50.0: -0.038},
                  "quartz": {6.0: -0.083, 20.0: -0.069}}

SIZES = [0.1, 0.2, 0.5, 0.98, 1.0, 1.1, 2.0]   # every colloid diameter in the Li/Tong set, um
IS_ALL = [1.0, 3.0, 6.0, 10.0, 20.0, 50.0]     # every ionic strength in the set, mM
MEDIA = ["glass", "quartz"]

# (medium, diameter_um, IS_mM) actually present in Data/LiTong_experimental_data_tidy.csv
IN_SET = {
    ("glass", 0.1, 20.0), ("glass", 0.1, 50.0), ("glass", 0.2, 20.0), ("glass", 0.2, 50.0),
    ("glass", 0.5, 20.0), ("glass", 0.5, 50.0), ("glass", 0.98, 10.0), ("glass", 1.0, 20.0),
    ("glass", 1.0, 50.0), ("glass", 1.1, 6.0), ("glass", 1.1, 20.0), ("glass", 1.1, 50.0),
    ("glass", 2.0, 20.0), ("glass", 2.0, 50.0),
    ("quartz", 0.5, 20.0), ("quartz", 0.5, 50.0), ("quartz", 0.98, 10.0), ("quartz", 1.1, 1.0),
    ("quartz", 1.1, 3.0), ("quartz", 1.1, 6.0), ("quartz", 1.1, 20.0),
}

KR_GLASS_ANCHOR = 5.58e-5      # glass shared k_r /s, the anchor in dlvo_kramers_size.py
ANCHOR_D_UM = 1.1              # anchored at 1.1 um


def kappa_of(I_mM):
    return np.sqrt(2 * NA * e**2 * float(I_mM) / (eps0 * epsr * kT))


def usec_and_h(a, A, z1, z2, I_mM):
    """|U_sec|/kT and the separation h_sec (m) where it occurs. Same grid/mask as fx_vs_usec.usec()."""
    kap = kappa_of(I_mM)
    U = ((-A * a / (6 * _h)) / (1 + 14 * _h / lam)
         + 64 * np.pi * eps0 * epsr * a * (kT / (z * e))**2
         * np.tanh(z * e * z1 / (4 * kT)) * np.tanh(z * e * z2 / (4 * kT)) * np.exp(-kap * _h)) / kT
    m = _h > H_MIN
    i = np.where(m)[0][0] + np.argmin(U[m])
    return max(-U[i], 0.0), float(_h[i])


def selfcheck():
    """Abort unless this file reproduces fx_vs_usec.usec() to machine precision on real cases."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from fx_vs_usec import usec as ref
    except Exception as ex:
        print(f"  ! fx_vs_usec.py not importable ({ex}); self-check SKIPPED", flush=True)
        return None
    worst, n = 0.0, 0
    for med in MEDIA:
        for d in SIZES:
            for I in IS_ALL:
                z1 = ZETA_COLLOID.get(I); z2 = ZETA_COLLECTOR[med].get(I)
                if z1 is None or z2 is None:
                    continue
                mine, _ = usec_and_h(d / 2 * 1e-6, A_HAM[med], z1, z2, I)
                theirs = float(ref(d / 2 * 1e-6, A_HAM[med], z1, z2, I))
                worst = max(worst, abs(mine - theirs)); n += 1
    if worst > 1e-12:
        raise SystemExit(f"SELF-CHECK FAILED: |U_sec| differs from fx_vs_usec.usec() by {worst:.3e} kT")
    print(f"  self-check vs fx_vs_usec.usec(): {n} cases, max |diff| = {worst:.1e} kT")
    return n


# ---------------------------------------------------------------------------------- workbook build
FONT = "Arial"
B = Font(name=FONT, bold=True, size=10)
N = Font(name=FONT, size=10)
IT = Font(name=FONT, italic=True, size=9)
BLUE = Font(name=FONT, size=10, color="0000FF")       # hardcoded input
BLUEB = Font(name=FONT, bold=True, size=10, color="0000FF")
TITLE = Font(name=FONT, bold=True, size=12)
HDRFILL = PatternFill("solid", fgColor="DCE6F1")
GAPFILL = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
SCI = "0.000E+00"


def put(ws, r, c, v, font=N, fmt=None, fill=None, border=False):
    cell = ws.cell(r, c, v); cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    if border: cell.border = BOX
    return cell


def header(ws, r, labels, widths=None):
    for j, h in enumerate(labels, 1):
        put(ws, r, j, h, B, fill=HDRFILL, border=True).alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True)
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[r].height = 30


def build(outdir):
    wb = openpyxl.Workbook(); wb.remove(wb.active)

    # ---------------------------------------------------------------- 1. Constants
    ws = wb.create_sheet("Constants")
    put(ws, 1, 1, "Physicochemical constants feeding |U_sec| and Kramers escape", TITLE)
    put(ws, 2, 1, "BLUE = hardcoded input, edit here and every derived cell in this workbook follows. "
                  "Black = formula. Sources named in the last column.", IT)
    header(ws, 4, ["symbol", "quantity", "value", "unit", "source / note"], [12, 40, 16, 14, 74])
    rows = [
        ("e", "elementary charge", e, "C", "CODATA; as used in fx_vs_usec.py"),
        ("k_B", "Boltzmann constant", kB, "J/K", "CODATA; as used in fx_vs_usec.py"),
        ("T", "absolute temperature", T, "K", "293.2 K = 20.05 C. Fixed in fx_vs_usec.py / dlvo_kramers_size.py"),
        ("eps_0", "vacuum permittivity", eps0, "F/m", "CODATA"),
        ("eps_r", "relative permittivity of water", epsr, "-", "80.0 at 20 C, as used throughout"),
        ("N_A", "Avogadro constant", NA, "1/mol", "CODATA"),
        ("z", "counter-ion valence", z, "-", "1 -- all Li/Tong electrolytes are 1:1 (NaCl)"),
        ("lambda", "vdW retardation wavelength", lam, "m", "100 nm; Gregory retardation, matched to Johnson 2018"),
        ("mu", "dynamic viscosity of water", mu, "Pa s", "1.0e-3; Kramers prefactor only (dlvo_kramers_size.py)"),
        ("h_min", "lower bound of the |U_sec| search", H_MIN, "m",
         "8 nm. Below this the primary minimum dominates and the search would find it instead"),
        ("h_grid", "energy-profile grid", 70000, "points",
         "linspace(2e-9, 140e-9, 70000) m -- IDENTICAL to fx_vs_usec.usec(); h_sec is grid-resolved to ~2 pm"),
    ]
    r = 5
    for sym, q, v, u, src in rows:
        put(ws, r, 1, sym, B, border=True)
        put(ws, r, 2, q, N, border=True)
        put(ws, r, 3, v, BLUE, fmt=SCI if (abs(v) < 1e-3 or abs(v) > 1e4) else "0.000", border=True)
        put(ws, r, 4, u, N, border=True)
        put(ws, r, 5, src, IT, border=True)
        r += 1
    put(ws, r + 1, 1, "kT", B)
    put(ws, r + 1, 2, "thermal energy", N)
    ws.cell(r + 1, 3, "=C6*C7").font = N; ws.cell(r + 1, 3).number_format = SCI
    put(ws, r + 1, 4, "J", N)
    put(ws, r + 1, 5, "k_B * T -- the energy unit every |U_sec| in this workbook is divided by.", IT)
    KT_REF = f"Constants!$C${r+1}"
    put(ws, r + 3, 1, "Kramers anchor", B)
    put(ws, r + 3, 2, "glass shared k_r", N)
    put(ws, r + 3, 3, KR_GLASS_ANCHOR, BLUE, fmt=SCI)
    put(ws, r + 3, 4, f"/s at {ANCHOR_D_UM} um", N)
    put(ws, r + 3, 5, "serial3_size_fit.py joint fit. Used ONLY to anchor the Kramers curve so its SIZE "
                      "SLOPE can be compared with the fitted k_r; the absolute Kramers rate is ~1e8x higher. "
                      "NOTE this is the SUPERSEDED constant (current: glass 3.75e-5 /s) -- kept because the "
                      "published anchored curve used it.", IT)
    ANCHOR_REF = "Constants!$C$%d" % (r + 3)

    # ---------------------------------------------------------------- 2. Zeta and Hamaker
    ws = wb.create_sheet("Zeta_Hamaker")
    put(ws, 1, 1, "Zeta potentials and Hamaker constants -- Johnson 2018 Table SI-1", TITLE)
    put(ws, 2, 1, "BLUE = measured input. GREY = NO MEASUREMENT EXISTS. Do not fill a grey cell with an "
                  "invented or silently interpolated value; any column at that ionic strength simply "
                  "carries no |U_sec|.", IT)
    header(ws, 4, ["ionic strength (mM)", "zeta colloid (V)", "zeta collector, glass (V)",
                   "zeta collector, quartz (V)", "note"], [20, 18, 24, 24, 62])
    r = 5
    for I in IS_ALL:
        put(ws, r, 1, I, BLUEB, fmt="0.0", border=True)
        for j, val in enumerate([ZETA_COLLOID.get(I), ZETA_COLLECTOR["glass"].get(I),
                                 ZETA_COLLECTOR["quartz"].get(I)], 2):
            if val is None:
                put(ws, r, j, "no measurement", IT, fill=GAPFILL, border=True)
            else:
                put(ws, r, j, val, BLUE, fmt="0.000", border=True)
        note = ""
        if I in (1.0, 3.0, 10.0):
            note = "Table SI-1 covers 6 / 20 / 50 mM only -- NO colloid zeta at this IS"
            if I == 3.0:
                note += ". 3 mM IS IN THE MANUSCRIPT: this gap must be closed with a measured or " \
                        "explicitly-flagged interpolated value"
        elif I == 50.0:
            note = "quartz COLLECTOR not measured at 50 mM (Table SI-1 gives quartz at 6 / 20 mM)"
        put(ws, r, 5, note, IT, border=True)
        r += 1
    r += 2
    put(ws, r, 1, "Hamaker constant A132 (colloid-water-collector)", B); r += 1
    header(ws, r, ["medium", "A132 (J)", "source"], [20, 18, 62]); r += 1
    for med in MEDIA:
        put(ws, r, 1, med, N, border=True)
        put(ws, r, 2, A_HAM[med], BLUE, fmt=SCI, border=True)
        put(ws, r, 3, "polystyrene-water-glass" if med == "glass" else "polystyrene-water-quartz", IT, border=True)
        r += 1
    A_GLASS_REF, A_QTZ_REF = f"Zeta_Hamaker!$B${r-2}", f"Zeta_Hamaker!$B${r-1}"
    ZROW = {I: 5 + i for i, I in enumerate(IS_ALL)}

    # ---------------------------------------------------------------- 3. Usec grid
    ws = wb.create_sheet("Usec_grid")
    put(ws, 1, 1, "|U_sec| for every colloid size x ionic strength x medium", TITLE)
    put(ws, 2, 1, "|U_sec|/kT = -min over h>8nm of [ U_vdw(h) + U_edl(h) ] / kT, sphere-plate (grain >> colloid). "
                  "Every column here is a FORMULA except h_sec, which needs a numerical minimisation over a "
                  "70,000-point grid and is written as a value (blue). The energies are then evaluated AT that h. "
                  "Change a zeta materially and h_sec should be re-derived by re-running dlvo_parameter_table.py.", IT)
    put(ws, 3, 1, "Rows with no zeta at that ionic strength are greyed and carry no energies. "
                  "'in Li/Tong set?' marks the combinations that are actual experiments; the rest are filled in "
                  "so the parameter space can be inspected for a-priori work.", IT)
    header(ws, 5, ["medium", "diameter (um)", "a_p radius (m)", "IS (mM)", "I (mol/m3)", "A132 (J)",
                   "zeta colloid (V)", "zeta collector (V)", "kappa (1/m)", "Debye length (nm)",
                   "G1 = tanh(ze*z1/4kT)", "G2 = tanh(ze*z2/4kT)", "h_sec (nm)", "U_vdw(h_sec)/kT",
                   "U_edl(h_sec)/kT", "|U_sec| (kT)", "in Li/Tong set?"],
           [9, 13, 13, 9, 12, 12, 13, 14, 13, 14, 16, 16, 12, 15, 15, 13, 14])
    r = 6
    first_data = r
    for med in MEDIA:
        for d in SIZES:
            for I in IS_ALL:
                z1 = ZETA_COLLOID.get(I); z2 = ZETA_COLLECTOR[med].get(I)
                have = z1 is not None and z2 is not None
                fill = None if have else GAPFILL
                put(ws, r, 1, med, N, fill=fill, border=True)
                put(ws, r, 2, d, BLUE, fmt="0.00", fill=fill, border=True)
                ws.cell(r, 3, f"=B{r}/2*1E-6").font = N
                ws.cell(r, 3).number_format = SCI; ws.cell(r, 3).border = BOX
                if fill: ws.cell(r, 3).fill = fill
                put(ws, r, 4, I, BLUE, fmt="0.0", fill=fill, border=True)
                ws.cell(r, 5, f"=D{r}").font = N          # mM == mol/m3 for a 1:1 salt
                ws.cell(r, 5).number_format = "0.0"; ws.cell(r, 5).border = BOX
                if fill: ws.cell(r, 5).fill = fill
                ws.cell(r, 6, f"={A_GLASS_REF if med=='glass' else A_QTZ_REF}").font = N
                ws.cell(r, 6).number_format = SCI; ws.cell(r, 6).border = BOX
                if fill: ws.cell(r, 6).fill = fill
                zr = ZROW[I]
                if have:
                    ws.cell(r, 7, f"=Zeta_Hamaker!$B${zr}").font = N
                    ws.cell(r, 8, f"=Zeta_Hamaker!${'C' if med=='glass' else 'D'}${zr}").font = N
                    for cc in (7, 8):
                        ws.cell(r, cc).number_format = "0.000"; ws.cell(r, cc).border = BOX
                    ws.cell(r, 9, f"=SQRT(2*Constants!$C$10*Constants!$C$5^2*E{r}/"
                                  f"(Constants!$C$8*Constants!$C$9*{KT_REF}))").font = N
                    ws.cell(r, 10, f"=1/I{r}*1E9").font = N
                    ws.cell(r, 11, f"=TANH(Constants!$C$11*Constants!$C$5*G{r}/(4*{KT_REF}))").font = N
                    ws.cell(r, 12, f"=TANH(Constants!$C$11*Constants!$C$5*H{r}/(4*{KT_REF}))").font = N
                    us, hs = usec_and_h(d / 2 * 1e-6, A_HAM[med], z1, z2, I)
                    ws.cell(r, 13, hs * 1e9).font = BLUE
                    ws.cell(r, 14, f"=(-(F{r}*C{r}/(6*M{r}/1E9))/(1+14*(M{r}/1E9)/Constants!$C$12))/{KT_REF}").font = N
                    ws.cell(r, 15, f"=64*PI()*Constants!$C$8*Constants!$C$9*C{r}*"
                                   f"({KT_REF}/(Constants!$C$11*Constants!$C$5))^2*K{r}*L{r}*"
                                   f"EXP(-I{r}*(M{r}/1E9))/{KT_REF}").font = N
                    ws.cell(r, 16, f"=MAX(-(N{r}+O{r}),0)").font = Font(name=FONT, bold=True, size=10)
                    for cc, fm in ((9, SCI), (10, "0.00"), (11, "0.0000"), (12, "0.0000"),
                                   (13, "0.00"), (14, "0.0000"), (15, "0.0000"), (16, "0.000")):
                        ws.cell(r, cc).number_format = fm; ws.cell(r, cc).border = BOX
                else:
                    for cc in range(7, 17):
                        put(ws, r, cc, "no zeta" if cc in (7, 8) else "", IT, fill=GAPFILL, border=True)
                put(ws, r, 17, "yes" if (med, d, I) in IN_SET else "-", N, fill=fill, border=True)
                r += 1
    last_data = r - 1
    put(ws, r + 1, 1, f"{last_data-first_data+1} rows = {len(MEDIA)} media x {len(SIZES)} sizes x "
                      f"{len(IS_ALL)} ionic strengths. |U_sec| is proportional to colloid radius (both energy "
                      f"terms scale with a), so at fixed IS the depth doubles when the diameter doubles.", IT)
    ws.freeze_panes = "A6"

    # ---------------------------------------------------------------- 4. Kramers
    ws2 = wb.create_sheet("Kramers")
    put(ws2, 1, 1, "Kramers escape from the secondary minimum -- the single-colloid prediction", TITLE)
    put(ws2, 2, 1, "D(a) = kT / (6 pi mu a)   [Stokes-Einstein]        k_r,abs = D * kappa^2 * exp(-|U_sec|/kT)", B)
    put(ws2, 3, 1, "Well width taken as the Debye length, so the attempt frequency is D*kappa^2. "
                   "'anchored' rescales the curve to the glass shared constant at 1.1 um so its SIZE SLOPE is "
                   "comparable with the fitted k_r -- the absolute rate is ~1e8x too high, which is the second "
                   "refutation. See dlvo_kramers_size.py and kr_trend_analysis.md.", IT)
    header(ws2, 5, ["medium", "diameter (um)", "IS (mM)", "|U_sec| (kT)", "D (m2/s)", "kappa^2 (1/m2)",
                    "attempt freq D*kappa^2 (1/s)", "exp(-|U_sec|)", "k_r absolute (1/s)",
                    "k_r anchored (1/s)", "in Li/Tong set?"],
            [9, 13, 9, 12, 14, 14, 20, 14, 16, 16, 14])
    # anchor row: glass, 1.1 um, 20 mM -- the condition dlvo_kramers_size.py anchors on
    r2 = 6
    src_rows = []
    rr = first_data
    for med in MEDIA:
        for d in SIZES:
            for I in IS_ALL:
                src_rows.append((med, d, I, rr)); rr += 1
    anchor_src = next(x for x in src_rows if x[0] == "glass" and x[1] == ANCHOR_D_UM and x[2] == 20.0)
    anchor_out_row = 6 + src_rows.index(anchor_src)
    for med, d, I, srow in src_rows:
        have = ZETA_COLLOID.get(I) is not None and ZETA_COLLECTOR[med].get(I) is not None
        fill = None if have else GAPFILL
        put(ws2, r2, 1, med, N, fill=fill, border=True)
        put(ws2, r2, 2, d, N, fmt="0.00", fill=fill, border=True)
        put(ws2, r2, 3, I, N, fmt="0.0", fill=fill, border=True)
        if have:
            ws2.cell(r2, 4, f"=Usec_grid!P{srow}").font = N
            ws2.cell(r2, 5, f"={KT_REF}/(6*PI()*Constants!$C$13*Usec_grid!C{srow})").font = N
            ws2.cell(r2, 6, f"=Usec_grid!I{srow}^2").font = N
            ws2.cell(r2, 7, f"=E{r2}*F{r2}").font = N
            ws2.cell(r2, 8, f"=EXP(-D{r2})").font = N
            ws2.cell(r2, 9, f"=G{r2}*H{r2}").font = N
            ws2.cell(r2, 10, f"={ANCHOR_REF}*I{r2}/$I${anchor_out_row}").font = N
            for cc, fm in ((4, "0.000"), (5, SCI), (6, SCI), (7, SCI), (8, SCI), (9, SCI), (10, SCI)):
                ws2.cell(r2, cc).number_format = fm; ws2.cell(r2, cc).border = BOX
        else:
            for cc in range(4, 11):
                put(ws2, r2, cc, "", IT, fill=GAPFILL, border=True)
        put(ws2, r2, 11, "yes" if (med, d, I) in IN_SET else "-", N, fill=fill, border=True)
        r2 += 1
    put(ws2, r2 + 1, 1, f"Anchor cell for the 'k_r anchored' column is I{anchor_out_row} "
                        f"(glass, {ANCHOR_D_UM} um, 20 mM), matching dlvo_kramers_size.py.", IT)
    put(ws2, r2 + 2, 1, "RESULT this table reproduces: |U_sec| runs ~0.18 -> 3.55 kT over 0.1-2.0 um at 20 mM "
                        "glass, and the anchored escape rate swings ~584x across that range -- against a fitted "
                        "k_r that is flat in size. That swing is the refutation of single-colloid Kramers escape "
                        "as the mechanism behind k_r.", IT)
    ws2.freeze_panes = "A6"

    # ---------------------------------------------------------------- 5. Equations
    ws3 = wb.create_sheet("Equations")
    put(ws3, 1, 1, "Equations, in the exact form implemented", TITLE)
    ws3.column_dimensions["A"].width = 30; ws3.column_dimensions["B"].width = 108
    eqs = [
        ("van der Waals", "U_vdw(h) = -(A132 * a_p) / (6h) * 1 / (1 + 14h/lambda)    [Gregory-retarded, sphere-plate]"),
        ("electrostatic", "U_edl(h) = 64*pi*eps0*eps_r*a_p*(kT/(z*e))^2 * G1*G2 * exp(-kappa*h)    [LSA, constant potential]"),
        ("", "G_i = tanh( z*e*zeta_i / (4kT) )   for i = colloid, collector"),
        ("Debye parameter", "kappa = sqrt( 2*N_A*e^2*I / (eps0*eps_r*kT) ),  I in mol/m3;  Debye length = 1/kappa"),
        ("secondary minimum", "|U_sec| = -min over h > 8 nm of [ U_vdw(h) + U_edl(h) ],  reported in units of kT"),
        ("", "both terms scale linearly with a_p, so |U_sec| is PROPORTIONAL TO COLLOID RADIUS at fixed chemistry"),
        ("diffusivity", "D(a_p) = kT / (6*pi*mu*a_p)    [Stokes-Einstein; ~1/a]"),
        ("Kramers escape", "k_r(a_p) = D * kappa^2 * exp( -|U_sec|/kT )    [overdamped; well width ~ Debye length]"),
    ]
    r3 = 3
    for lbl, txt in eqs:
        put(ws3, r3, 1, lbl, B); put(ws3, r3, 2, txt, N); r3 += 1
    r3 += 1
    put(ws3, r3, 1, "Provenance", B); r3 += 1
    for txt in [
        "|U_sec|: fx_vs_usec.usec(), imported by fx_trend.py as the single copy of this physics. This workbook "
        "reproduces it exactly (self-check on every build) and additionally reports h_sec.",
        "Kramers: dlvo_kramers_size.py.",
        "zeta, Hamaker: fx_trend.py ZETA_COLLOID / ZETA_COLLECTOR / A_HAM, from Johnson 2018 Table SI-1; "
        "provenance in Records/data_inventory.md section 6.",
        "sizes and ionic strengths: every distinct value in Data/LiTong_experimental_data_tidy.csv.",
        "Reproducer for this workbook: Code/dlvo_parameter_table.py.",
    ]:
        put(ws3, r3, 2, txt, IT); r3 += 1
    r3 += 1
    put(ws3, r3, 1, "CAVEATS", BLUEB); r3 += 1
    for txt in [
        "TWO ZETA GAPS, BOTH REAL. No colloid or collector zeta exists at 1, 3 or 10 mM, and no QUARTZ collector "
        "zeta at 50 mM. Those rows are greyed and carry no |U_sec|. 3 mM is in the manuscript, so that gap needs "
        "a measured or explicitly-flagged interpolated zeta -- not a silent fill.",
        "|U_sec| does NOT encode velocity. Size, ionic strength and mineralogy act through it; the sweep side of "
        "trap-vs-sweep capture is a separate, hidden variable.",
        "The 50 mM colloid zeta (-0.040 V) is EXTRAPOLATED beyond the 20 mM end of Table SI-1 -- flagged in "
        "part2_apriori_alpha_machinery.md section 1.1a and carried here unchanged.",
        "The Kramers anchor 5.58e-5 /s is the SUPERSEDED glass constant (current 3.75e-5 /s). It is retained "
        "because the published anchored curve used it; the anchoring affects only the vertical placement of the "
        "curve, never its size slope, which is the refutation.",
        "h_sec is a value, not a formula -- it needs a numerical minimisation. Re-run the reproducer after any "
        "material change to a zeta or Hamaker constant.",
    ]:
        put(ws3, r3, 2, txt, IT); r3 += 1

    out = os.path.join(outdir, "DLVO_Kramers_parameters.xlsx")
    wb.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()
    selfcheck()
    p = build(a.outdir)
    print(f"wrote {p}")
    print(f"{'medium':8}{'d_um':>6}{'IS_mM':>7}{'|Usec|kT':>10}{'h_sec_nm':>10}")
    for med in MEDIA:
        for d in SIZES:
            for I in IS_ALL:
                z1 = ZETA_COLLOID.get(I); z2 = ZETA_COLLECTOR[med].get(I)
                if z1 is None or z2 is None: continue
                u, h = usec_and_h(d / 2 * 1e-6, A_HAM[med], z1, z2, I)
                print(f"{med:8}{d:>6}{I:>7}{u:>10.3f}{h*1e9:>10.2f}")


if __name__ == "__main__":
    main()
