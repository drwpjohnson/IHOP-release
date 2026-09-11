#!/usr/bin/env python3
"""Build Figure 8 as a native openpyxl Excel chart: f_x vs |U_sec| (secondary-minimum depth),
the saturating closure f_x = fmax*(1-exp(-|U_sec|/U*)) plus its multiplicative band, medium-coded
(glass=circle, quartz=triangle), with three status tiers per point: used in the closure (filled),
excluded on cost (open grey), excluded as not-identifiable/degenerate (open red, larger, labeled).

Data source: Manuscript/FigsExcelsUnfav/fx_trend.xlsx -- 'f_x vs Usec (DLVO)' sheet for the 29
unfavorable-column points (25 with a defined |U_sec|; 4 have no zeta at that ionic strength and are
not plotted) and 'f_x(Usec) closure' sheet for the REPORTED closure curve (per-column, uniform rule,
row 6: fmax=0.00595, U*=0.994 kT, n=16) and its 40-point curve/band table (rows 22-61).

** FLAG, NOT SILENTLY FIXED: the embedded Figure 8 image currently in the manuscript
(word/media/image13.png, rId23) is STALE relative to this data. It labels "Tong.U" as the excluded/
degenerate (red-ringed) point; in the current fx_trend.xlsx, Tong.U is status "yes" (used, f_x=0.0372,
cost=10.06) and the actual degenerate point is Li.M (quartz, 1.1um, 20mM, f_x=0.00055, cost=0.72,
flagged "no (f_x not identifiable)"). The reported closure numbers themselves (fmax~0.0060, U*~0.99 kT)
DO match between image title and spreadsheet, so only the point-classification annotation is out of
date, not the fitted curve. This script builds from the current spreadsheet, so the new chart's
excluded/degenerate point will show as Li.M, not Tong.U, per the up-to-date data. **

Run from Code/.
"""
import numpy as np
import openpyxl
from openpyxl.chart import ScatterChart, Series, Reference
from openpyxl.chart.marker import Marker
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText, Text as ChartText
from openpyxl.chart.title import Title
from openpyxl.chart.legend import Legend
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import (RichTextProperties, Paragraph, ParagraphProperties,
                                    CharacterProperties, Font as DrawFont, RegularTextRun)

SRC = "../Manuscript/FigsExcelsUnfav/fx_trend.xlsx"   # run from Code/
OUTDIR = "../Manuscript/Figures"
APTOS = "Aptos"

GLASS_COLOR = "1F77B4"   # matches build_figure7.py / alpha_trends.py convention
QUARTZ_COLOR = "7B2D8B"
GREY = "999999"
RED = "C0392B"


def rich_run(text, sz=1400, bold=True, italic=False):
    cp = CharacterProperties(sz=sz, b=bold, i=italic)
    cp.latin = DrawFont(typeface=APTOS)
    return RegularTextRun(rPr=cp, t=text)


def axis_title(text, x, y):
    para = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1400, b=True)),
                      r=[rich_run(text, sz=1400)])
    rt = RichText(bodyPr=RichTextProperties(), p=[para])
    t = Title(tx=ChartText(rich=rt))
    t.overlay = True
    t.layout = Layout(manualLayout=ManualLayout(xMode="edge", yMode="edge", x=x, y=y))
    return t


def read_source(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["f_x vs Usec (DLVO)"]
    hdr = [ws.cell(4, c).value for c in range(1, 14)]
    rows = []
    r = 5
    while ws.cell(r, 1).value is not None:
        row = {h: ws.cell(r, c).value for c, h in enumerate(hdr, 1)}
        rows.append(row)
        r += 1

    wc = wb["f_x(Usec) closure"]
    fmax, ustar, band = wc.cell(6, 3).value, wc.cell(6, 4).value, wc.cell(6, 6).value
    curve = []
    r = 22
    while wc.cell(r, 1).value is not None:
        curve.append((wc.cell(r, 1).value, wc.cell(r, 2).value, wc.cell(r, 3).value, wc.cell(r, 4).value))
        r += 1
    return rows, dict(fmax=fmax, ustar=ustar, band=band), curve


def write_data_sheet(ws, rows, closure_params, curve):
    plottable = [r for r in rows if r["|U_sec|_kT"] is not None]
    def sel(medium, status_pred):
        return [(r["|U_sec|_kT"], r["f_x"], r["col"]) for r in plottable
                if r["medium"] == medium and status_pred(r["in closure?"])]

    glass_used = sel("glass", lambda s: s == "yes")
    glass_cost = sel("glass", lambda s: s == "no (cost)")
    quartz_used = sel("quartz", lambda s: s == "yes")
    quartz_cost = sel("quartz", lambda s: s == "no (cost)")
    quartz_deg = sel("quartz", lambda s: s == "no (f_x not identifiable)")

    blocks = [
        (1, "glass, used in closure", glass_used),
        (4, "glass, excluded (cost > 15)", glass_cost),
        (7, "quartz, used in closure", quartz_used),
        (10, "quartz, excluded (cost > 15)", quartz_cost),
        (13, "quartz, excluded (f_x not identifiable)", quartz_deg),
    ]
    for c0, label, pts in blocks:
        ws.cell(1, c0, f"{label}: |U_sec| (kT)"); ws.cell(1, c0 + 1, "f_x"); ws.cell(1, c0 + 2, "identifier (study.col)")
        for i, (x, y, ident) in enumerate(pts, start=2):
            ws.cell(i, c0, x); ws.cell(i, c0 + 1, y); ws.cell(i, c0 + 2, ident)

    c0 = 16
    ws.cell(1, c0, "closure |U_sec| (kT)"); ws.cell(1, c0 + 1, "predicted f_x")
    ws.cell(1, c0 + 2, "band low"); ws.cell(1, c0 + 3, "band high")
    for i, (x, y, lo, hi) in enumerate(curve, start=2):
        ws.cell(i, c0, x); ws.cell(i, c0 + 1, y); ws.cell(i, c0 + 2, lo); ws.cell(i, c0 + 3, hi)

    ws.cell(1, 21, "REPORTED CLOSURE: fmax={:.4f}, U*={:.2f} kT, band x/{:.2f} (per column, uniform rule, n=16)".format(
        closure_params["fmax"], closure_params["ustar"], closure_params["band"]))

    for col in ("C", "F", "I", "L", "O"):
        ws.column_dimensions[col].width = 26
    return dict(glass_used=len(glass_used), glass_cost=len(glass_cost), quartz_used=len(quartz_used),
                quartz_cost=len(quartz_cost), quartz_deg=len(quartz_deg), curve=len(curve))


def build_chart(ws, n):
    ch = ScatterChart()
    ch.style = 2
    ch.scatterStyle = "marker"
    ch.varyColors = False

    def colref(c, r1, r2):
        return Reference(ws, min_col=c, min_row=r1, max_col=c, max_row=r2)

    def add_line(xcol, ycol, count, title, color, dash="solid", w=19050):
        if count == 0: return
        xref = colref(xcol, 2, 1 + count); yref = colref(ycol, 2, 1 + count)
        s = Series(values=yref, xvalues=xref, title=title)
        s.marker = Marker(symbol="none")
        s.graphicalProperties = GraphicalProperties()
        s.graphicalProperties.line = LineProperties(solidFill=color, w=w, prstDash=dash)
        s.smooth = True
        ch.series.append(s)

    def add_points(c0, count, title, symbol, size, fill_color, line_color, filled=True):
        if count == 0: return
        xref = colref(c0, 2, 1 + count); yref = colref(c0 + 1, 2, 1 + count)
        s = Series(values=yref, xvalues=xref, title=title)
        s.marker = Marker(symbol=symbol, size=size)
        if filled:
            s.marker.graphicalProperties = GraphicalProperties(solidFill=fill_color)
        else:
            s.marker.graphicalProperties = GraphicalProperties(noFill=True)
        s.marker.graphicalProperties.line = LineProperties(solidFill=line_color, w=9525 if filled else 15875)
        s.graphicalProperties = GraphicalProperties()
        s.graphicalProperties.line = LineProperties(noFill=True)
        s.smooth = False
        ch.series.append(s)

    # band and curve first (drawn under the points); all three share the x-column (P, |U_sec|)
    add_line(16, 18, n["curve"], "band low", GREY, dash="sysDash", w=9525)
    add_line(16, 19, n["curve"], "band high", GREY, dash="sysDash", w=9525)
    add_line(16, 17, n["curve"], "reported closure", "000000", dash="solid", w=22225)

    add_points(1, n["glass_used"], "glass, used", "circle", 7, GLASS_COLOR, "000000", filled=True)
    add_points(4, n["glass_cost"], "glass, excluded (cost)", "circle", 6, None, GREY, filled=False)
    add_points(7, n["quartz_used"], "quartz, used", "triangle", 8, QUARTZ_COLOR, "000000", filled=True)
    add_points(10, n["quartz_cost"], "quartz, excluded (cost)", "triangle", 7, None, GREY, filled=False)
    add_points(13, n["quartz_deg"], "quartz, excluded (not identifiable)", "triangle", 10, None, RED, filled=False)

    ch.x_axis.scaling.min = 0.1
    ch.x_axis.scaling.max = 20
    ch.x_axis.scaling.logBase = 10
    ch.x_axis.delete = False
    ch.x_axis.axPos = "b"
    ch.x_axis.crossAx = 20
    ch.x_axis.majorTickMark = "out"
    ch.x_axis.minorTickMark = "none"
    ch.x_axis.tickLblPos = "nextTo"
    ch.x_axis.numFmt = "0.0"
    ch.x_axis.spPr = GraphicalProperties()
    ch.x_axis.spPr.line = LineProperties(solidFill="000000", w=12700)
    ch.x_axis.title = axis_title("|Usec| (kT)", 0.42, 0.90)

    ch.y_axis.scaling.min = 1e-4
    ch.y_axis.scaling.max = 0.1
    ch.y_axis.scaling.logBase = 10
    ch.y_axis.delete = False
    ch.y_axis.axPos = "l"
    ch.y_axis.crossAx = 10
    ch.y_axis.majorTickMark = "out"
    ch.y_axis.minorTickMark = "none"
    ch.y_axis.tickLblPos = "nextTo"
    ch.y_axis.numFmt = "0.0000"
    ch.y_axis.spPr = GraphicalProperties()
    ch.y_axis.spPr.line = LineProperties(solidFill="000000", w=12700)
    ch.y_axis.title = axis_title("f_x", 0.01, 0.40)

    ch.x_axis.majorGridlines = None
    ch.y_axis.majorGridlines = None

    ch.layout = Layout(manualLayout=ManualLayout(
        layoutTarget="inner", xMode="edge", yMode="edge",
        x=0.11, y=0.04, w=0.62, h=0.90))

    ch.legend = Legend()
    ch.legend.position = "r"
    ch.legend.overlay = False
    ch.legend.layout = Layout(manualLayout=ManualLayout(
        xMode="edge", yMode="edge", x=0.76, y=0.06, w=0.24, h=0.88))
    legpara = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1000, b=False)))
    legpara.pPr.defRPr.latin = DrawFont(typeface=APTOS)
    ch.legend.txPr = RichText(bodyPr=RichTextProperties(), p=[legpara])

    ch.graphical_properties = GraphicalProperties()
    ch.graphical_properties.line = LineProperties(noFill=True)
    ch.graphical_properties.noFill = True

    top_para = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1400, b=True)))
    top_para.pPr.defRPr.latin = DrawFont(typeface=APTOS)
    ch.textProperties = RichText(bodyPr=RichTextProperties(), p=[top_para])

    ch.width = 19
    ch.height = 13
    return ch


def build_workbook(out_name):
    rows, closure_params, curve = read_source(SRC)
    wb = openpyxl.Workbook()
    del wb["Sheet"]
    ws_data = wb.create_sheet("Data")
    n = write_data_sheet(ws_data, rows, closure_params, curve)
    ws_fig = wb.create_sheet("Figure")
    ch = build_chart(ws_data, n)
    ws_fig.add_chart(ch, "A1")
    ws_fig.sheet_view.zoomScale = 100
    ws_fig.sheet_view.zoomScaleNormal = 100
    ws_fig.page_setup.orientation = "landscape"
    ws_fig.page_setup.fitToPage = True
    ws_fig.page_setup.fitToWidth = 1
    ws_fig.page_setup.fitToHeight = 1
    ws_fig.sheet_properties.pageSetUpPr.fitToPage = True
    wb.move_sheet("Figure", offset=-1 * wb.sheetnames.index("Figure"))
    wb.active = 0
    out_path = f"{OUTDIR}/{out_name}"
    wb.save(out_path)
    print("saved", out_path, n)


if __name__ == "__main__":
    build_workbook("Figure8_FxClosure.xlsx")
