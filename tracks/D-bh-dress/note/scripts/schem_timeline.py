"""Schematic: stage timeline of Track D (note v1, state of wave 3 round 1, 2026-11-20).

Gates and indicative times: coord/CHARTER.md section 9.2 (line 66); track criteria: brief
sheet 9.7 (line 779) as made concrete in stage/G0/REPORT.md section 3; state: PLAN-wave3.md
round 1 (G0 package complete for review, not signed in coord/GATES.md), stage/G1/CHECKLIST.md
(open items C7: the profile criterion of the Newtonian infall, ruling requested from orch;
C9: this architecture schematic; C17: a fresh-context verifier), stage/G1/STATUS.md, and the
round's packages (relaxed-lapse run analysed, late-drift controls, matter run). Gate
positions are evenly spaced; the time labels give the charter's targets. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "week 2", pf.GREEN_DARK,
     "complete; package ready\nfor review: questions, null-\ntest wording, criteria, cost"),
    ("G1 baseline", "week 8", pf.OLIVE,
     "met: bubble data, floor, spike\n(Schwarzschild, Kerr), infall\ngrowth; open: two items"),
    ("G2 capability", "month 4", pf.SLATE,
     "first bubble run and control\ndone; relaxed lapse ran;\nmatter run, drift controls"),
    ("G3 science", "month 9", pf.RED,
     "growth law and spike, three-\nway convergence; upper limit\non the coupling exponent"),
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
    pf.text(ax, 0.9, 10.9, "now: G0 complete for review; G1 open for the infall profile criterion "
            "and a fresh verifier; first G2 runs under way", size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(10.2, 5.75), (10.6, 5.75), (10.4, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 10.4, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "ruling on the infall profile\ncriterion; a fresh verifier",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "gauge for expanding dust; cause\nof the late drift; dust to the\n"
            "black hole, growth against flux", size=7.0, color=pf.ROSE)
    pf.brace(ax, 15.6, 20.8, 3.6, "", below=True)
    pf.text(ax, 18.2, 2.0, "convergence at finer cells;\nwarm dust and spin; puncture\n"
            "in a periodic box; card time", size=7.0, color=pf.ROSE)
    pf.brace(ax, 21.6, 26.6, 3.6, "", below=True)
    pf.text(ax, 24.1, 2.25, "wording of the null result;\ncomparison with the literature",
            size=7.0, color=pf.ROSE)
    pf.text(ax, 0.6, 0.55, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
