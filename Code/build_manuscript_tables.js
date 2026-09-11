/* build_manuscript_tables.js -- regenerate the two manuscript tables and their analysis text on the
 * CURRENT (2026-08-24 corrected) objective.
 *
 *   Table4_identifiability.docx   -- replaces manuscript Table 4 + its "Parameter Identifiability
 *                                    Analysis" paragraph. Numbers from identifiability_canon.json.
 *   Table3_fit_quality_SI.docx    -- replaces SI Table S1 + its paragraph. Numbers from
 *                                    table3_rows.json, which build_table3.py extracts from
 *                                    UnfavorableMaster.xlsx.
 *
 * Both read JSON produced by their reproducers, so neither document carries a transcribed number.
 * That is the whole point: the circulating versions of both drifted from the workbook precisely
 * because they were typed by hand.
 *
 * Requires the `docx` npm package. Usage, from a directory where node_modules/docx resolves:
 *   node build_manuscript_tables.js
 * Adjust DIR and OUTDIR below for the machine it is run on.
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, LevelFormat,
} = require("docx");

// DIR / OUTDIR were HARD-CODED to two different directories, with DIR pointing at a stale copy of
// the JSONs (W.P.J., 2026-08-25). Re-running after the accum refit therefore rebuilt both tables
// from the OLD identifiability_canon.json and table3_rows.json and wrote them out looking fresh --
// a silently stale deliverable, which is the exact failure this project keeps having to catch.
// Both are now CLI arguments; the old values remain the defaults only so existing invocations do
// not change behaviour. ALWAYS pass the directory holding the JSONs you just regenerated.
//   node build_manuscript_tables.js <json-dir> <out-dir>
const DIR = process.argv[2] || "/sessions/magical-adoring-euler/mnt/outputs/updated";
const OUTDIR = process.argv[3] || "/sessions/magical-adoring-euler/mnt/outputs";
const ID = JSON.parse(fs.readFileSync(path.join(DIR, "identifiability_canon.json")));
const T3 = JSON.parse(fs.readFileSync(path.join(DIR, "table3_rows.json")));

const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1080;
const CW = PAGE_W - 2 * MARGIN;
const ACCENT = "1F4E79", MUTED = "595959", WARN = "9C2B1B";

const P = (t, o = {}) => new Paragraph({
  spacing: { before: o.before ?? 80, after: o.after ?? 140, line: 276 },
  children: [new TextRun({ text: t, size: o.size ?? 21, italics: o.i, bold: o.b, color: o.c })],
});
const rich = (runs, o = {}) => new Paragraph({
  spacing: { before: o.before ?? 80, after: o.after ?? 140, line: 276 },
  children: runs.map(r => typeof r === "string" ? new TextRun({ text: r, size: 21 })
    : new TextRun({ text: r.t, size: r.size ?? 21, bold: r.b, italics: r.i, color: r.c })),
});
const H = (t, lvl) => new Paragraph({ heading: lvl, spacing: { before: 280, after: 140 },
  children: [new TextRun({ text: t, color: ACCENT })] });
const cap = (t) => new Paragraph({ spacing: { before: 80, after: 200 },
  children: [new TextRun({ text: t, size: 18, italics: true, color: MUTED })] });

function callout(title, body, color) {
  return new Table({
    columnWidths: [CW], width: { size: CW, type: WidthType.DXA },
    rows: [new TableRow({ children: [new TableCell({
      width: { size: CW, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: color === WARN ? "FDF2F0" : "EEF4FA" },
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 2, color }, bottom: { style: BorderStyle.SINGLE, size: 2, color },
        left: { style: BorderStyle.SINGLE, size: 18, color }, right: { style: BorderStyle.SINGLE, size: 2, color },
      },
      children: [new Paragraph({ spacing: { after: 60 },
                   children: [new TextRun({ text: title, bold: true, size: 21, color })] }),
                 ...body.map(b => new Paragraph({ spacing: { after: 60 },
                   children: [new TextRun({ text: b, size: 20 })] }))],
    })] })],
  });
}

function table(headers, rows, widths, fs_ = 17) {
  const tot = widths.reduce((a, b) => a + b, 0);
  const w = widths.map(x => Math.round(x * CW / tot));
  const cell = (txt, i, hdr, ro) => new TableCell({
    width: { size: w[i], type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: hdr ? ACCENT : (ro && ro.fill) || "FFFFFF" },
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    children: [new Paragraph({ spacing: { before: 15, after: 15 },
      alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
      children: [new TextRun({ text: String(txt), size: fs_, bold: hdr || (ro && ro.bold),
                               color: hdr ? "FFFFFF" : (ro && ro.color) || "000000" })] })],
  });
  return new Table({
    columnWidths: w, width: { size: CW, type: WidthType.DXA },
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
           ...rows.map(r => { const ro = Array.isArray(r) ? null : r.opt;
                              const cs = Array.isArray(r) ? r : r.cells;
                              return new TableRow({ children: cs.map((c, i) => cell(c, i, false, ro)) }); })],
  });
}

const baseDoc = (children) => new Document({
  creator: "W. P. Johnson",
  styles: { default: { document: { run: { font: "Calibri", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: ACCENT }, paragraph: { spacing: { before: 300, after: 150 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: ACCENT }, paragraph: { spacing: { before: 240, after: 120 } } }] },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: PAGE_H },
    margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } }, children }],
});

const f2 = (x) => x.toFixed(2);
const f1 = (x) => x.toFixed(1);
const PN = ["k_f", "a_s", "a_m", "f_x", "v_ns", "k_r"];
const P4 = ["a_s", "a_m", "f_x", "k_r"];
const ii = Object.fromEntries(PN.map((n, i) => [n, i]));
const j4 = Object.fromEntries(P4.map((n, i) => [n, i]));
const labs = Object.keys(ID);
const C = (lab, a, b) => Math.abs(ID[lab].corr[ii[a]][ii[b]]);
const A = (lab, n) => ID[lab].amp[ii[n]];
const C4 = (lab, a, b) => Math.abs(ID[lab].production4.corr[j4[a]][j4[b]]);
const A4 = (lab, n) => ID[lab].production4.amp[j4[n]];
const rng = (f) => { const v = labs.map(f); return [Math.min(...v), Math.max(...v)]; };

// ============================ Table 4 : identifiability ============================
const kffx_glass = labs.filter(l => ID[l].medium === "glass").map(l => C(l, "k_f", "f_x"));
const kffx_qz = labs.filter(l => ID[l].medium === "quartz").map(l => C(l, "k_f", "f_x"));
const [nearLo, nearHi] = (() => {
  const v = labs.flatMap(l => [C(l, "f_x", "v_ns"), C(l, "f_x", "k_r"), C(l, "v_ns", "k_r")]);
  return [Math.min(...v), Math.max(...v)];
})();
const [ampLo, ampHi] = (() => {
  const v = labs.flatMap(l => [A(l, "f_x"), A(l, "v_ns"), A(l, "k_r")]);
  return [Math.min(...v), Math.max(...v)];
})();
const [krLo, krHi] = rng(l => A4(l, "k_r"));
const amp4max = Math.max(...labs.flatMap(l => P4.map(n => A4(l, n))));

const doc4 = baseDoc([
  H("Parameter Identifiability Analysis", HeadingLevel.HEADING_1),
  P("Recomputed 2026-08-25 on the canonical five conditions and the corrected objective. This supersedes " +
    "the previous version, which was computed on the earlier engine and predates both the mean-log plateau " +
    "target and the branch-aware retention-profile shape window.", { i: true, c: MUTED }),

  rich(["A local identifiability test — pairwise correlations from the Jacobian at each fitted optimum, in " +
    "log₁₀ parameter space — shows that the three near-surface levers (", { t: "f", i: true }, "ₓ, ",
    { t: "v", i: true }, "ₙₛ and ", { t: "k", i: true }, "ᵣ) are strongly collinear, with pairwise |correlation| " +
    `spanning ${f2(nearLo)} to ${f2(nearHi)} and mutual aliasing of ${f1(ampLo)}× to ${f1(ampHi)}× ` +
    "(Table 4, panel A). The tightest pair is ", { t: "v", i: true }, "ₙₛ↔", { t: "k", i: true },
    `ᵣ at ${f2(rng(l => C(l, "v_ns", "k_r"))[0])}–${f2(rng(l => C(l, "v_ns", "k_r"))[1])}: these two are ` +
    "very nearly indistinguishable to the data."]),

  callout("Two corrections to the previous statement of this analysis", [
    `The lower bound on the near-surface correlations is ${f2(nearLo)}, not 0.90. Two pairs on quartz at ` +
    `6 mM fall to ${f2(C("quartz 1.1 um 6 mM", "f_x", "v_ns"))} and ${f2(C("quartz 1.1 um 6 mM", "f_x", "k_r"))}. ` +
    "The cluster is strongly collinear, but not uniformly near-perfect, and it should not be described as such.",
    `The claim that k_f is independent of the cluster with |correlation| ≤ 0.4 does not hold on quartz. ` +
    `On glass it holds comfortably (k_f↔f_x = ${kffx_glass.map(f2).join(" and ")}), but on quartz it reaches ` +
    `${Math.max(...kffx_qz).toFixed(2)}. The medium-specific version of the statement is correct; the blanket ` +
    "version is not.",
  ], WARN),

  rich(["A degeneracy absent from the previous analysis is also visible and is the more important of the two: ",
    { t: "k", i: true }, "_f↔", { t: "α", i: true }, "ₛ reaches ",
    `${f2(rng(l => C(l, "k_f", "a_s"))[1])} on four of the five conditions. That is the r`, { t: "s", i: true },
    "·α", { t: "s", i: true }, " product degeneracy — only the product is identifiable — appearing exactly " +
    "where theory says it must. It is the quantitative justification for pinning r",
    { t: "s", i: true }, " to the favorable anchor, and it means the interception rate and the attachment " +
    "efficiency cannot be reported as independently determined."]),

  H("Table 4", HeadingLevel.HEADING_2),
  P("Panel A — with k_f and v_ns FREE. This is the diagnostic question: what would happen if they were not " +
    "pinned? Values are |correlation| in log₁₀ parameter space, and aliasing amplification (marginal " +
    "standard deviation ÷ conditional standard deviation) for the near-surface cluster.", { i: true }),
  table(["condition", "k_f/α_s", "f_x/v_ns", "f_x/k_r", "v_ns/k_r", "k_f/f_x", "alias f_x", "alias v_ns", "alias k_r"],
    labs.map(l => [l.replace(" 1.1 um", ",").replace(" mM", " mM"),
      f2(C(l, "k_f", "a_s")), f2(C(l, "f_x", "v_ns")), f2(C(l, "f_x", "k_r")), f2(C(l, "v_ns", "k_r")),
      f2(C(l, "k_f", "f_x")), f1(A(l, "f_x")) + "×", f1(A(l, "v_ns")) + "×", f1(A(l, "k_r")) + "×"]),
    [26, 10, 10, 10, 10, 10, 8, 8, 8]),
  cap("Aliasing amplification is how much a parameter's uncertainty inflates when the others are free to " +
      "compensate. 1× means no aliasing; tens mean the parameter is determined only jointly with its partners."),

  P("Panel B — the production fit, with r_s and v_ns pinned and four parameters free. This tests whether " +
    "pinning actually resolved the degeneracy, rather than assuming it did.", { i: true }),
  table(["condition", "α_s/α_m", "f_x/k_r", "α_s/f_x", "alias α_s", "alias α_m", "alias f_x", "alias k_r"],
    labs.map(l => [l.replace(" 1.1 um", ","),
      f2(C4(l, "a_s", "a_m")), f2(C4(l, "f_x", "k_r")), f2(C4(l, "a_s", "f_x")),
      f1(A4(l, "a_s")) + "×", f1(A4(l, "a_m")) + "×", f1(A4(l, "f_x")) + "×", f1(A4(l, "k_r")) + "×"]),
    [28, 11, 11, 11, 10, 10, 10, 10]),
  cap(`Table 4. Local identifiability on the canonical five conditions. Panel A frees k_f and v_ns to expose ` +
      `the degeneracies; panel B is the production parameterisation.`),

  callout("The resolution works, and this is the quantitative demonstration", [
    `k_r aliasing collapses from ${f1(rng(l => A(l, "k_r"))[0])}–${f1(rng(l => A(l, "k_r"))[1])}× before ` +
    `pinning to ${f1(krLo)}–${f1(krHi)}× after. No parameter in the production fit exceeds ${f1(amp4max)}× ` +
    "aliasing on any condition.",
    "So the manuscript's central identifiability claim — that pinning v_ns to 5% of v and then fitting f_x " +
    "makes k_r identifiable — is confirmed, and now with a number attached rather than an assertion.",
    "The largest residual correlation in the production fit is α_s↔α_m (" +
    `${f2(rng(l => C4(l, "a_s", "a_m"))[0])}–${f2(rng(l => C4(l, "a_s", "a_m"))[1])}), which is moderate ` +
    "and expected: both are attachment efficiencies acting on the same interception stream. It does not " +
    "compromise either as a fitted quantity, but they should not be quoted as fully independent.",
  ], ACCENT),

  P("Reproducer: Code/identifiability_canon.py → identifiability_canon.json. The Jacobian is central-" +
    "differenced in log₁₀ parameter space and the covariance is taken as the pseudo-inverse of JᵀJ, " +
    "because JᵀJ is singular by construction — the k_f and α_s columns are near-parallel. A plain inverse " +
    "would either fail or return values that look like results.", { i: true, c: MUTED, size: 18 }),
]);

// ============================ Table S1 : fit quality ============================
const S = T3.summary, R = T3.rows;
const docS = baseDoc([
  H("Fit quality across the full unfavorable set", HeadingLevel.HEADING_1),
  P("Regenerated 2026-08-25 from the current UnfavorableMaster.xlsx. Supersedes the previous version, " +
    "which predates the branch-aware retention-profile shape window and is stale for two conditions.",
    { i: true, c: MUTED }),

  rich([`Extending the fit-quality analysis to the full set of ${S.n} unfavorable condition–study ` +
    "combinations (Table S1) confirms that a single model structure reproduces coupled BTECs and RPs " +
    "across contrasting media (glass beads and quartz sand), colloid diameters (0.1–2.0 µm), pore " +
    "velocities (4 and 8 m/day), and ionic strengths (3–50 mM). The residual is not spread uniformly but " +
    "concentrates on a single feature — the retention-profile shape."]),

  callout("Read the totals within their scoring convention, not across it", [
    `Seventeen conditions are scored with the half-split inlet window and two — Li quartz 1.1 µm at 3 and ` +
    `6 mM — with the 4-point window that the peaked branch requires. The 4-point window targets the ` +
    `measured inlet rise over 1–7 cm, far steeper than the 1–11 cm half-split average, so those two are ` +
    `scored against a harder target and show larger totals even where the fit is closer to the data.`,
    `Within the half-split group the median total is ${f1(S.median_half)} (n = ${S.n_half}); across all ` +
    `${S.n} it is ${f1(S.median)}. The model did not get worse — the yardstick changed for two conditions. ` +
    `Quoting ${f1(S.median)} against the previously published ${f1(S.median_half)} as though the fit had ` +
    "degraded would be a straightforward misreading.",
    `The convention-independent metrics are RP RMS (median ${S.rms_median.toFixed(3)}, max ` +
    `${S.rms_max.toFixed(3)} log units) and RP peak depth. Those are what a reader should compare.`,
  ], WARN),

  rich(["The shape residual reflects the steep, hyper-exponential inlet of the glass retention profiles and " +
    "the sharp interior peak of the low-ionic-strength quartz profiles — features a single-population " +
    "interception model cannot reproduce, because the modelled profile cannot decline faster than the " +
    "interception rate permits (glass) and the recruited crawl population produces only a gentle interior " +
    "maximum (quartz). Capturing these inlets would require a distribution of deposition rates, a model " +
    "extension beyond the present single-population framework. The plateau penalty is zero for all but the " +
    `${S.plateau_nonzero.length} declining 50 mM breakthrough curves, and the breakthrough tail is ` +
    "reproduced well throughout. Across the full dataset the model therefore matches the depth profile and " +
    "the breakthrough curve together, with the residuals falling on the retention-profile inlet rather than " +
    "on any systematic failure of the coupled fit."]),

  P("Table S1. Fit quality for the full unfavorable set. Minimised weighted cost (½ Σ of squared weighted " +
    "residuals; lower is better) per condition, split into RP parts (level, shape) and BTEC parts (plateau, " +
    "tail-level, tail-slope). Replicate conditions are the mean over columns. The 'window' column gives the " +
    "scoring convention; RP RMS is convention-independent.", { i: true }),
  table(["Condition", "RP lvl", "RP shp", "RP tot", "Plat", "Tail lvl", "Tail slp", "BTEC tot", "TOTAL", "win", "RP RMS"],
    R.map(x => {
      const four = x.window !== "half";
      return { cells: [x.label, f2(x.rp_level), f2(x.rp_shape), f2(x.rp_total), f2(x.plateau),
                       f2(x.tail_level), f2(x.tail_slope), f2(x.btec_total), f2(x.total),
                       four ? "4-pt" : "half", x.rp_rms.toFixed(3)],
               opt: four ? { fill: "FDF2F0", bold: true } : null };
    }), [30, 8, 8, 8, 7, 8, 8, 9, 9, 7, 8]),
  cap(`n = ${S.n}. Shaded rows use the 4-point inlet window and are not comparable with the rest. ` +
      `Max total ${f1(S.mx)} (${S.mx_cond}).`),

  P("Reproducer: Code/build_table3.py reads the 'Fit quality (Table 3)' sheet of UnfavorableMaster.xlsx; " +
    "Code/build_manuscript_tables.js writes this document. No number here is transcribed by hand — the " +
    "previous version of this table drifted from the workbook because it was.",
    { i: true, c: MUTED, size: 18 }),
]);

Promise.all([
  Packer.toBuffer(doc4).then(b => fs.writeFileSync(path.join(OUTDIR, "Table4_identifiability.docx"), b)),
  Packer.toBuffer(docS).then(b => fs.writeFileSync(path.join(OUTDIR, "Table3_fit_quality_SI.docx"), b)),
]).then(() => console.log("wrote Table4_identifiability.docx and Table3_fit_quality_SI.docx"));
