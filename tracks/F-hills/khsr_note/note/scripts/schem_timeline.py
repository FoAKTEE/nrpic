"""Schematic: stage timeline of F-hills (note v1; state of wave 3, round 1).

Gates: coord/CHARTER.md 9.2 (G0-G4) and 9.9 (criteria of Track F), decision 0013 (mass
ratio four for the convergence study and the first scan line; the first clump-binary passage
right after the first black-hole passage), decision 0014 (50 card-hours to the next gate).
Content per gate: stage/G0/SCOPING.md section 5 (exit criteria) and 9 (compute); state:
stage/G0/OPEN.md, stage/G1/STATUS.md, nr_first/JOURNAL.md (wave 2), PLAN-wave3.md round 1
(G0 lacks only the verifier's report; G1: the first passage running). Gate positions are
evenly spaced; no dates are claimed. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "waves 1-2", pf.GREEN_DARK,
     "novelty, ranges, criteria;\nboth baselines reproduce\nthe literature; note"),
    ("G1 baseline", "waves 2-3", pf.SLATE,
     "start-state constraints,\nmember junk and gauge;\none vacuum passage, q = 4"),
    ("G2 capability", "from wave 3", pf.RED,
     "three resolutions at q = 4;\nwide passages return to\nthe references; clump at rest"),
    ("G3 science", "waves 4-5", pf.RED,
     "scan lines (a) and (b),\nthree-way convergence,\nseparation boundary"),
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
    pf.text(ax, 0.9, 10.9, "now: wave 3; G0 awaits its verifier, G1 data and members measured, "
            "the first passage running", size=7.5, ha="left", italic=True)
    xn = 10.6
    ax.add_patch(pf.Polygon([(xn - 0.2, 5.75), (xn + 0.2, 5.75), (xn, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, xn, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "several black holes released;\nreaders; card time of one passage",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "card time beyond the allotment;\nmember gauge; moving clumps\n"
            "and clump models", size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "two cards or larger blocks;\nseveral hundred card-hours;\n"
            "phase sampling", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "comparison with both\nreferences; null results", size=7.0,
            color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
