"""Schematic: stage timeline of C-sidm (note v0; state updated for note v1, 2026-11-21).

Gates: coord/CHARTER.md 9.2 (G0-G4) and 9.6 (criteria of Track C), decision 0013 (G2
wording: the collisionless threshold located with three-way convergence and compared with
the turning-point criterion), decision 0014 (45 card-hours to the next gate).
Content per gate: stage/G0/REPORT.md sections 4 and 9; state: stage/G0/OPEN.md,
stage/G1/STATUS.md, stage/G1/CHECKLIST.md, OPEN.md and VERIFIER.md, stage/REVIEW-wave3.md
sections 2-4 (2026-11-21). Gate positions are evenly spaced; no dates are claimed. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "wave 1", pf.GREEN_DARK,
     "problem, ranges, criteria\nreferences, risks, compute\nnote and schematics"),
    ("G1 baseline", "waves 2-3", pf.SLATE,
     "spherical baseline (met);\nbox tests pass on the code's\noperator; heat conduction"),
    ("G2 capability", "waves 3-4", pf.RED,
     "collisionless threshold,\nthree-way convergence;\ncurved-spacetime budgets"),
    ("G3 science", "waves 4-5", pf.RED,
     "mass fraction against Kn,\nconverged in N and step;\nfluid-limit anchor"),
    ("G4 paper", "after G3", pf.RED,
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
    pf.text(ax, 0.9, 10.9, "now: wave 3; G1 results in this note, checked by an independent verifier",
            size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(7.9, 5.75), (8.3, 5.75), (8.1, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 8.1, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "operator in the code, box and\nconduction tests (done)",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "finer mesh for the controls;\nthree seeds near the threshold;\n"
            "card time for the scans", size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "particle number for small Kn;\ncost per collision measured;\n"
            "card time beyond the allotment", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "comparison with the\nfluid models; null results", size=7.0,
            color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
