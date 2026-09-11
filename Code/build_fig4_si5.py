#!/usr/bin/env python3
"""Build Figure 4 and SI-5 as native openpyxl Excel charts, in the Figure 1 template style.
Series: measured (black circles) + k_f-only (red dashed) + IHOP/Model2 (blue dashed).
Data source: Manuscript/FigsExcelsFavorable/Favorable_data_and_sim.xlsx (already-computed fits;
no new fitting performed here).
"""
import openpyxl
from openpyxl.chart import ScatterChart, Series, Reference
from openpyxl.chart.marker import Marker
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText, Text as ChartText
from openpyxl.chart.title import Title
from openpyxl.chart.legend import Legend, LegendEntry
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import (RichTextProperties, Paragraph, ParagraphProperties,
                                    CharacterProperties, Font as DrawFont, RegularTextRun)
from openpyxl.chart.data_source import NumDataSource, NumRef

SRC = "../Manuscript/FigsExcelsFavorable/Favorable_data_and_sim.xlsx"   # run from Code/
OUTDIR = "../Manuscript/FigsExcelsFavorable"

APTOS = "Aptos"

def rich_run(text, sz=1800, bold=True, baseline=None, latin=True):
    cp = CharacterProperties(sz=sz, b=bold)
    if latin:
        cp.latin = DrawFont(typeface=APTOS)
    if baseline is not None:
        cp.baseline = baseline
    return RegularTextRun(rPr=cp, t=text)

def make_title(text, x, y, w, h, sz=1800):
    para = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=sz, b=True)),
                      r=[rich_run(text, sz=sz)])
    rt = RichText(bodyPr=RichTextProperties(), p=[para])
    t = Title(tx=ChartText(rich=rt))
    t.overlay = True
    t.layout = Layout(manualLayout=ManualLayout(xMode="edge", yMode="edge", x=x, y=y, w=w, h=h))
    return t

def axis_title(main_text, sub_text=None, x=0.001, y=0.2):
    runs = [rich_run(main_text, sz=1800, bold=True)]
    if sub_text:
        runs.append(rich_run(sub_text, sz=1800, bold=True, baseline=-25000))
    para = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1800, b=True)), r=runs)
    rt = RichText(bodyPr=RichTextProperties(), p=[para])
    t = Title(tx=ChartText(rich=rt))
    t.overlay = True
    t.layout = Layout(manualLayout=ManualLayout(xMode="edge", yMode="edge", x=x, y=y))
    return t

def style_measured(ser):
    ser.marker = Marker(symbol="circle", size=5)
    ser.marker.graphicalProperties = GraphicalProperties(solidFill="000000")
    ser.marker.graphicalProperties.line = LineProperties(solidFill="000000")
    ser.graphicalProperties = GraphicalProperties()
    ser.graphicalProperties.line = LineProperties(noFill=True)
    ser.smooth = False

def style_line(ser, color, dash="dash"):
    ser.marker = Marker(symbol="none")
    ser.graphicalProperties = GraphicalProperties()
    ser.graphicalProperties.line = LineProperties(solidFill=color, w=19050, prstDash=dash)
    ser.smooth = True

def build_chart(ws, kind, title_text, xmin, xmax, xmajor, ymin, ymax, ymajor,
                 col0, data_row, n_exp, n_m1, n_m2, bottom_row=False, with_legend=False,
                 legend_labels=("k_f only", "IHOP")):
    """kind: 'BTEC' or 'RP'."""
    ch = ScatterChart()
    ch.style = 2
    ch.scatterStyle = "lineMarker"
    ch.varyColors = True

    def colref(c, r1, r2):
        return Reference(ws, min_col=c, min_row=r1, max_col=c, max_row=r2)

    c0 = col0
    xref = colref(c0, data_row, data_row + n_exp - 1)
    yref = colref(c0 + 1, data_row, data_row + n_exp - 1)
    s_exp = Series(values=yref, xvalues=xref, title="exp")
    style_measured(s_exp)
    ch.series.append(s_exp)

    xref1 = colref(c0 + 2, data_row, data_row + n_m1 - 1)
    yref1 = colref(c0 + 3, data_row, data_row + n_m1 - 1)
    s_m1 = Series(values=yref1, xvalues=xref1, title=legend_labels[0])
    style_line(s_m1, "FF0000")
    ch.series.append(s_m1)

    xref2 = colref(c0 + 4, data_row, data_row + n_m2 - 1)
    yref2 = colref(c0 + 5, data_row, data_row + n_m2 - 1)
    s_m2 = Series(values=yref2, xvalues=xref2, title=legend_labels[1])
    style_line(s_m2, "0000FF")
    ch.series.append(s_m2)

    ch.title = make_title(title_text, 0.54, 0.006, 0.43, 0.12)

    ch.x_axis.scaling.min = xmin
    ch.x_axis.scaling.max = xmax
    ch.x_axis.majorUnit = xmajor
    ch.x_axis.delete = False
    ch.x_axis.axPos = "b"
    ch.x_axis.crossAx = 20
    ch.x_axis.majorTickMark = "out"
    ch.x_axis.minorTickMark = "none"
    ch.x_axis.spPr = GraphicalProperties()
    ch.x_axis.spPr.line = LineProperties(solidFill="000000", w=12700)
    if bottom_row:
        ch.x_axis.tickLblPos = "nextTo"
        xt = "Pore Volumes" if kind == "BTEC" else "Distance (cm)"
        ch.x_axis.title = axis_title(xt, x=0.42, y=0.93)
    else:
        ch.x_axis.tickLblPos = "none"
        ch.x_axis.title = None

    ch.y_axis.scaling.min = ymin
    ch.y_axis.scaling.max = ymax
    ch.y_axis.majorUnit = ymajor
    ch.y_axis.delete = False
    ch.y_axis.axPos = "l"
    ch.y_axis.crossAx = 10
    ch.y_axis.majorTickMark = "out"
    ch.y_axis.minorTickMark = "none"
    ch.y_axis.tickLblPos = "nextTo"
    ch.y_axis.spPr = GraphicalProperties()
    ch.y_axis.spPr.line = LineProperties(solidFill="000000", w=12700)
    if kind == "BTEC":
        ch.y_axis.title = axis_title("Log10 C/C", "0", x=0.0007, y=0.19)
    else:
        ch.y_axis.title = axis_title("Log10 #", x=0.01, y=0.3)

    ch.x_axis.majorGridlines = None
    ch.y_axis.majorGridlines = None

    plot_h = 0.648 if bottom_row else 0.879
    plot_y = 0.061 if bottom_row else 0.060
    plot_w = 0.805 if bottom_row else 0.847
    plot_x = 0.147 if bottom_row else 0.153
    ch.layout = Layout(manualLayout=ManualLayout(
        layoutTarget="inner", xMode="edge", yMode="edge",
        x=plot_x, y=plot_y, w=plot_w, h=plot_h))

    if with_legend:
        ch.legend = Legend()
        ch.legend.position = "r"
        ch.legend.overlay = True
        ch.legend.layout = Layout(manualLayout=ManualLayout(
            xMode="edge", yMode="edge", x=0.60, y=0.13, w=0.38, h=0.55))
        entry0 = LegendEntry(idx=0, delete=True)
        ch.legend.legendEntry = [entry0]
        legpara = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1400, b=True)))
        ch.legend.txPr = RichText(bodyPr=RichTextProperties(), p=[legpara])
    else:
        ch.legend = None

    ch.graphical_properties = GraphicalProperties()
    ch.graphical_properties.line = LineProperties(noFill=True)
    ch.graphical_properties.noFill = True

    top_para = Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=1800, b=True)))
    top_para.pPr.defRPr.latin = DrawFont(typeface=APTOS)
    ch.textProperties = RichText(bodyPr=RichTextProperties(), p=[top_para])

    ch.width = 14.2
    ch.height = 6.4 if bottom_row else 5.0
    return ch

print("module loaded OK")
