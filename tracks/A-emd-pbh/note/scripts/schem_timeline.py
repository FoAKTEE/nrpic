"""Schematic: stage timeline of Track A (note v0; state updated for note v1, 2026-11-20).

Gates and indicative times: coord/CHARTER.md section 9.2; track criteria: charter 9.4 as
made concrete in scope/SCOPE.md section 7; state and order: SCOPE.md 10.2, 10.7, 10.8,
stage/G1/STATUS.md, decision 0013 (threshold line in the periodic box, G1 scan design
accepted on the reference-based design), decision 0014 (card-time allotment); G0 passed on
2026-11-19 (coord/GATES.md); the G1 needs after wave 2: note Sec. V.
Gate positions are evenly spaced; the time labels give the charter's targets. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "week 2", pf.GREEN_DARK,
     "problem, ranges, exit criteria\nreferences, risks, compute\nnote and schematics"),
    ("G1 baseline", "week 8", pf.GREEN_DARK,
     "initial-data constraints\nconverge; criteria table;\nscan design from references"),
    ("G2 capability", "month 4", pf.SLATE,
     "spherical ball: times converge\nin N, h and ball radius;\nhorizon mass; one box run"),
    ("G3 science", "month 9", pf.RED,
     "threshold line, converged;\nhypotheses H1-H4 decided;\nmass, spin, one waveform"),
    ("G4 paper", "month 12", pf.RED,
     "manuscript and\nreproduction package"),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    y0 = 5.2
    pf.timeline(ax, 0.3, 29.7, y0, color=pf.GREEN_DARK, lw=2.2, fade_in=True, head=9)
    xs = [3.2, 9.2, 15.2, 21.2, 27.0]
    for x, (title, when, col, body) in zip(xs, GATES):
        ax.add_patch(pf.Circle((x, y0), 0.32, fc=col, ec=pf.WHITE, lw=1.0, zorder=7))
        pf.text(ax, x, y0 - 0.85, when, size=7.5, color=pf.ROSE, italic=True)
        cw = 5.4
        pf.callout(ax, x - cw / 2 + 0.1, 6.3, cw, 3.6, title, body, bar=col, size=7.0,
                   title_size=8.0, band=0.8)
        pf.line(ax, (x, y0 + 0.35), (x, 6.3), color=pf.GREY_LINE)
    # now
    pf.text(ax, 0.9, 10.9, "now: wave 3 of the program; G0 passed, G1 at its review",
            size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(9.8, 5.75), (10.2, 5.75), (10.0, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 10.0, 6.05, "now", size=7.0, color=pf.RED)
    # what each step waits for
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "done in waves 1-2: offline references,\ninitial data, predictions",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "slicing that reaches trapping;\nresolved first trapped sphere;\nconvergence runs, card time",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "peak data on a constant-K slice,\ncollapse slicing in the box,\n"
            "finder across faces, more card time", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "comparison with the\nliterature; null results", size=7.0,
            color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
