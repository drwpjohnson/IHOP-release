"""check_consistency.py -- re-derive every headline number from its source of truth, then hunt the
tree for SUPERSEDED values being asserted as current.

WHY THIS EXISTS (W.P.J., 2026-08-25). On 2026-08-25 five separate drift defects were found, all by a
human reading carefully:
  * build_manuscript_tables.js had its input directory hard-coded to a stale copy, so it rebuilt
    Tables 3 and 4 from OLD JSONs and wrote them out looking current;
  * hydeq_fit.py's comment said Li.AE's cost was ~38 while its own cached table said 48.11;
  * CLAUDE.md's headline block was captioned "do not quote older ones" and then quoted older ones;
  * model_doc.md carried pre-refit alphas with nothing marking them;
  * fx_trend.xlsx's "usable for closure?" flag applied a different test from the closure itself.
Reading does not scale and nearly did not work. This script does the mechanical part.

TWO CHECKS, and the second is the one that matters.

  DERIVE -- read each headline number from the artefact that owns it (JSON where one exists, the
  delivered workbook otherwise, so the check runs against what was actually shipped). Report it.
  If a source is missing, say MISSING; never guess, and never fall back to a literal.

  SCAN -- walk Records/*.md and the code, looking for the SUPERSEDED value of each claim. A record
  is *supposed* to quote old numbers: retraction notes, stage histories and audit trails are this
  project's strength and must not be flagged. A hit is excused three ways, each deliberately narrow:
    (1) a supersession marker on the SAME LINE as the number, or
    (2) the number sits under a Markdown heading that declares its block superseded / audit trail,
    (3) the file carries a DATED SNAPSHOT stamp in its first 25 lines (a frozen reproducer).
  An UNEXCUSED hit is a stale number presented as current -- precisely the defect class above.

  ** Both excuse rules were tightened after testing against the real tree. ** The first version
  excused on a +/-2-line window and on loose words (`old`, `was`, `earlier`). That combination
  green-lit two genuinely stale lines: CLAUDE.md's item 5 (excused because the line above mentioned
  "the old window") and hydeq_comparison_record.md's KR_MED note (excused by "the old objective").
  A checker that passes a real defect is worse than no checker, so: same-line only, strong markers
  only, plus explicit section-level marking.

  ** A heading must not describe a DIFFERENT block as superseded. ** "STATE AS OF 08-25 -- the 08-24
  block below is superseded" would mark the *current* block as audit trail and excuse every number
  in it. Put such statements in the body. (CLAUDE.md carries a note to this effect.)

Exit status is 1 if any claim FAILS, so this can gate a commit.

TO ADD A CLAIM: append to CLAIMS with a `derive` spec and the regexes for the values it REPLACES.
Leaving `stale` empty is fine -- the value is then reported but not policed.

Usage:  python3 check_consistency.py [--root <repo root>] [--verbose]
        Run from anywhere; --root defaults to the directory containing Records/ and Code/.
"""
import argparse, json, os, re, sys

# --------------------------------------------------------------------------------------------
# Each claim: how to DERIVE the current value, and which SUPERSEDED literals to hunt for.
# `stale` entries are regexes. Keep them specific enough not to collide with unrelated numbers --
# a bare "2.13" would match anything; "2\.13\s*(x|×)" will not.
# --------------------------------------------------------------------------------------------
CLAIMS = [
    # 5.58e-5 and 1.87e-5 were REMOVED from these stale lists on 2026-09-08 (W.P.J.), for exactly the
    # reason the kr_ratio note below gives: they collide with live values playing other roles. Both
    # are still current as (a) the multistart SEEDS in unfav_master_fit.py and its derivatives, and
    # (b) the per-medium k_r PIN in the favorable fits; 5.58e-5 is additionally the glass shared
    # constant from the size-series joint fit that anchors the Kramers curve in Figure 9 -- a
    # different fitted object from the 29-column trend constant this claim derives. Flagging those as
    # stale fired on five shipped files every run and trained the reader to ignore the checker.
    # W.P.J.'s judgment on the substance: k_r proved an UNNECESSARY parameter for this dataset -- the
    # necessity test costs only +1.7% total to drop it -- so the analyses of k_r itself are on thin
    # ice regardless. Where these constants appear, k_r is being PINNED so that the OTHER parameters
    # can be extracted (favorable_both_models.py pins it precisely so f_x becomes identifiable). The
    # exact pin is therefore not load-bearing for those extractions, and reconciling which constant
    # was used where is not worth the effort. 4.46e-5 and 2.09e-5 stay: those are the superseded
    # 08-24 headline values and have no other live role.
    dict(key="kr_glass", label="k_r constant, glass (/s)", unit="",
         derive=("xlsx", "k_r_trend.xlsx", "reference constants", 6, 2),
         fmt="{:.3e}", stale=[r"4\.46e-0?5"]),
    dict(key="kr_quartz", label="k_r constant, quartz (/s)", unit="",
         derive=("xlsx", "k_r_trend.xlsx", "reference constants", 8, 2),
         fmt="{:.3e}", stale=[r"2\.09e-0?5"]),
    dict(key="kr_ratio", label="k_r glass/quartz ratio", unit="x",
         derive=("xlsx", "k_r_trend.xlsx", "reference constants", 9, 2),
         # NOTE r"3\.1\s*(x|×)" was tried and REMOVED: it collided with an unrelated "IHOP advantage
         # 3.1x" and with a 3.1x column in the working record. A stale-value regex that fires on a
         # different quantity trains the reader to ignore the checker, which is the one failure
         # mode it cannot survive. Anchor the collision-prone ones to the word "ratio".
         fmt="{:.2f}", stale=[r"2\.13\s*(x|×)", r"2\.81\s*(x|×)", r"ratio\D{0,8}3\.1\s*(x|×)"]),
    dict(key="fx_fmax", label="f_x closure f_max", unit="",
         derive=("xlsx", "fx_trend.xlsx", "f_x(Usec) closure", 6, 3),
         # 0.0036 is ANCHORED, for the same reason the k_r ratio literals are (see the note above):
         # it collides with a legitimately CURRENT value. fx_trend_analysis.md's leave-one-out table
         # reports f_max = 0.0036 for the fit with Tong.B removed -- a live sensitivity result, not a
         # superseded headline -- and a bare literal flagged it every run. Anchoring to an f_max
         # context costs the ability to catch a bare stale 0.0036 elsewhere; that is the accepted
         # trade, because a checker that cries wolf on a correct line gets ignored. (2026-09-08)
         fmt="{:.4f}", stale=[r"0\.0047", r"f_?max\D{0,20}0\.0036"]),
    dict(key="fx_ustar", label="f_x closure U* (kT)  [report as a RANGE]", unit="kT",
         derive=("xlsx", "fx_trend.xlsx", "f_x(Usec) closure", 6, 4),
         fmt="{:.2f}", stale=[r"0\.80\s*kT", r"0\.52\s*kT", r"U\\?\*\s*=\s*0\.8\b"]),
    dict(key="t3_median", label="fit-quality median", unit="",
         derive=("json_expr", "table3_rows.json",
                 lambda d: __import__("statistics").median(r["total"] for r in d["rows"])),
         fmt="{:.2f}", stale=[r"median\s+12\.42", r"12\.42"]),
    dict(key="ihop_rms_worst", label="IHOP worst RP RMS, full set (log10)", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json",
                 lambda d: d["structures"]["IHOP"]["rms_worst"]),
         fmt="{:.3f}", stale=[]),
    dict(key="ihop_col_total", label="IHOP per-column total cost, full set", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json",
                 lambda d: d["structures"]["IHOP"]["col_total"]),
         fmt="{:.1f}", stale=[]),
    dict(key="h7_col_total", label="Hydeq7 per-column total cost, full set", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json",
                 lambda d: d["structures"]["M7_all"]["col_total"]),
         fmt="{:.1f}", stale=[]),
    dict(key="eq15", label="eq-15 margin: columns on the correct side", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json",
                 lambda d: d["eq15"]["correct"]),
         fmt="{:.0f}", stale=[]),
    # Reported, not policed: the counting question that came up on 2026-08-26. n_conditions is 18
    # because sizeclass() merges Li and Tong glass 1.1/4/20 ACROSS STUDIES; by condition_id the same
    # 29 columns give 19. Printing both stops the pair reading as drift. See hydeq_comparison_record
    # section 8d, "How the experiments count".
    dict(key="n_columns", label="unfavorable columns fitted (replicates counted)", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json", lambda d: d["n_columns"]),
         fmt="{:.0f}", stale=[]),
    dict(key="n_conditions", label="unfavorable conditions (size-class grouping; 19 by study)", unit="",
         derive=("json_expr", "hydeq_fullset_stats.json", lambda d: d["n_conditions"]),
         fmt="{:.0f}", stale=[]),
    dict(key="kr_excess", label="k_r removal, total excess cost (%)", unit="%",
         derive=("json_expr", "canon_nokr_stats.json", lambda d: d["total_excess_pct"]),
         fmt="{:+.1f}", stale=[r"\+2\.5\s*%"]),
]

# A hit is EXCUSED when it is plainly part of an audit trail. Three mechanisms:
#
#   LINE-LOCAL -- a strong supersession marker on the SAME LINE as the number. Not a window of
#   nearby lines: a ±2-line window let an unrelated body sentence ("the 08-24 block below is
#   superseded") excuse a stale number two lines later. Every legitimate retraction in these records
#   puts the marker on the number's own line -- "was 2.13x", "superseded by ...", "12.42 -> 12.49",
#   "| 3 | 0.0047 | superseded |" -- so same-line is both stricter AND sufficient.
#   ** Keep this list TIGHT. ** The first version included `old\b`, `was\s`, `were\s`, `earlier`
#   and `former`, which fire on ordinary prose: CLAUDE.md's stale item 5 was excused because the
#   line above it happened to mention "the old window", and hydeq_comparison_record.md's stale
#   KR_MED line was excused by "the old objective" two lines up. Both were genuinely stale and both
#   were let through for an unrelated reason. A loose excuse list is worse than none -- it produces
#   a green check over a real defect.
EXCUSE = re.compile(
    r"supersed|retire[sd]?\b|retract|audit trail|stage\s*[123]\b|previously|no longer|predate"
    r"|not current|withdrawn|historical|for continuity|->|→|\bwas\s+(retired|superseded|wrong)",
    re.I)

# SECTION-LEVEL -- a Markdown heading that declares its whole block superseded excuses everything
# under it, until a heading of the same or higher level that does not. This is how the records
# actually work (CLAUDE.md keeps an entire dated block; fx_trend_analysis.md keeps stage histories),
# and it is more honest than hoping a nearby word happens to match.
SUPERSEDED_HEADING = re.compile(
    r"^\s{0,3}(#{1,6})\s.*(supersed|retired|audit trail|no longer current|kept for)", re.I)
ANY_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s")

# FILE-LEVEL -- a whole file can be a DATED SNAPSHOT: the reproducer for a deliverable that was
# correct on its date and is not meant to track later refits (build_summary_docx.js builds
# FindingsSummary_2026-08-24.docx; model_doc.md carries the same kind of stamp). Every number in
# such a file is history by construction, and re-marking them line by line would be noise. The
# stamp must appear in the first 25 lines, so it is the first thing a reader sees -- a marker
# buried on line 300 would be an excuse nobody reads. Do NOT stamp a file that is still the source
# of a live number; that turns the checker off for exactly the file it exists to police.
FROZEN_FILE = re.compile(r"DATED SNAPSHOT|FROZEN REPRODUCER|numbers are those of its date", re.I)
FROZEN_SCAN_LINES = 25

SKIP_DIRS = {"archive", "__pycache__", ".git", "deliver", "baseline", "updated", "boxcheck",
             "boxverify", "r2", "Data"}
SCAN_EXT = {".md", ".py", ".js"}


def find_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(p, "Records")) and os.path.isdir(os.path.join(p, "Code")):
            return p
        nxt = os.path.dirname(p)
        if nxt == p:
            return os.path.abspath(start)
        p = nxt


def locate(root, name):
    """Find an artefact by name, preferring a delivered copy, then the tree."""
    for sub in ("deliver", "", "Manuscript", "Manuscript/HYDEQ", "Code", "Code/HYDEQ"):
        c = os.path.join(root, sub, name) if sub else os.path.join(root, name)
        if os.path.isfile(c):
            return c
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if name in files:
            return os.path.join(dirpath, name)
    return None


def derive(root, spec):
    kind = spec[0]
    if kind == "json_expr":
        _, fname, fn = spec
        p = locate(root, fname)
        if not p:
            return None, f"MISSING {fname}"
        try:
            return float(fn(json.load(open(p)))), os.path.relpath(p, root)
        except Exception as e:
            return None, f"ERROR reading {fname}: {e}"
    if kind == "xlsx":
        _, fname, sheet, row, col = spec
        p = locate(root, fname)
        if not p:
            return None, f"MISSING {fname}"
        try:
            import openpyxl
            wb = openpyxl.load_workbook(p, data_only=True)
            if sheet not in wb.sheetnames:
                return None, f"ERROR {fname}: no sheet {sheet!r}"
            v = wb[sheet].cell(row, col).value
            if not isinstance(v, (int, float)):
                return None, f"ERROR {fname}!{sheet} r{row}c{col} is {v!r}, not numeric"
            return float(v), os.path.relpath(p, root)
        except ImportError:
            return None, "ERROR openpyxl not available"
        except Exception as e:
            return None, f"ERROR reading {fname}: {e}"
    return None, f"ERROR unknown derive kind {kind!r}"


def scan(root, patterns):
    """-> (unexcused, excused) lists of (relpath, lineno, line)."""
    unex, exc = [], []
    rx = [re.compile(p) for p in patterns]
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1] not in SCAN_EXT:
                continue
            fp = os.path.join(dirpath, f)
            try:
                lines = open(fp, encoding="utf-8", errors="replace").read().split("\n")
            except Exception:
                continue
            if FROZEN_FILE.search("\n".join(lines[:FROZEN_SCAN_LINES])):
                for i, line in enumerate(lines):        # dated snapshot: all of it is history
                    if any(r.search(line) for r in rx):
                        exc.append((os.path.relpath(fp, root), i + 1, line.strip()[:120]))
                continue
            in_superseded = 0        # heading level of the superseded block we are inside, 0 = none
            for i, line in enumerate(lines):
                m = ANY_HEADING.match(line)
                if m:
                    lvl = len(m.group(1))
                    if SUPERSEDED_HEADING.match(line):
                        in_superseded = lvl
                    elif in_superseded and lvl <= in_superseded:
                        in_superseded = 0        # same or higher level, not marked -> block ends
                if not any(r.search(line) for r in rx):
                    continue
                excused = bool(in_superseded) or bool(EXCUSE.search(line))
                (exc if excused else unex).append(
                    (os.path.relpath(fp, root), i + 1, line.strip()[:120]))
    return unex, exc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true", help="also list excused (audit-trail) hits")
    args = ap.parse_args()
    root = find_root(args.root)
    print(f"root: {root}\n")

    print("=" * 100)
    print("DERIVED HEADLINE NUMBERS  (read from the artefact that owns them)")
    print("=" * 100)
    print(f"{'claim':46s}{'value':>14s}   source")
    vals = {}
    n_missing = 0
    for c in CLAIMS:
        v, src = derive(root, c["derive"])
        vals[c["key"]] = v
        if v is None:
            n_missing += 1
            print(f"{c['label']:46s}{'--':>14s}   {src}")
        else:
            print(f"{c['label']:46s}{c['fmt'].format(v):>14s}   {src}")

    print()
    print("=" * 100)
    print("STALE-VALUE SCAN  (superseded literals asserted as current)")
    print("=" * 100)
    fails = 0
    for c in CLAIMS:
        if not c["stale"]:
            continue
        unex, exc = scan(root, c["stale"])
        if unex:
            fails += 1
            print(f"\nFAIL  {c['label']} -- {len(unex)} unexcused, {len(exc)} excused")
            for rp, ln, txt in unex[:12]:
                print(f"        {rp}:{ln}: {txt}")
            if len(unex) > 12:
                print(f"        ... and {len(unex) - 12} more")
        else:
            print(f"ok    {c['label']:44s} 0 unexcused, {len(exc)} in audit trail")
            if args.verbose:
                for rp, ln, txt in exc[:6]:
                    print(f"        (excused) {rp}:{ln}: {txt}")

    print()
    print("=" * 100)
    if n_missing:
        print(f"{n_missing} source artefact(s) missing -- those claims were NOT checked.")
    if fails:
        print(f"RESULT: {fails} claim(s) FAILED. A superseded value is being presented as current.")
        print("Fix by updating the number, or by marking the context as superseded if it is history.")
        sys.exit(1)
    print("RESULT: no superseded value is asserted as current.")
    if n_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
