"""Schematic: stage timeline of Track D (note v3, state of wave 3 batch 25, 2026-11-25).

Gates and indicative times: coord/CHARTER.md section 9.2 (line 66); track criteria: brief
sheet 9.7 (line 779) as made concrete in stage/G0/REPORT.md section 3. State: G0 signed PASS
on 2026-11-20 (coord/GATES.md line 11); G1 signed PASS with reservations on 2026-11-21
(coord/GATES.md line 20; stage/G1/GATE_REVIEW.md section 5); first G2 result ES-F (growth
against the flux at one resolution, g2runs/JOURNAL.md entry 10); the relaxed lapse kept out
of the null test (coord/DECISIONS/0022 item 3, 0025 item 3); long runs with the faces at
+-768 M and the M/16 pair on the cards (stage/REVIEW-wave3.md section 12). Gate positions
are evenly spaced; the time labels give the charter's targets. Note v3: the G2 package is
assembled for its fresh verifier and review (stage/G2/OPEN.md; g2long/JOURNAL.md entries
5-26): null test at M/8 and M/16 (M/4 outside the regime, decision 0039 item 4), growth
against the flux at N/4, N, 4N and M/8, M/16. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.0
GATES = [
    ("G0 scoping", "week 2", pf.GREEN_DARK,
     "passed: questions, null-test\nwording, criteria, cost;\nverified by a fresh agent"),
    ("G1 baseline", "week 8", pf.OLIVE,
     "passed with reservations:\ninfall at one resolution;\n9/4 law not tested"),
    ("G2 capability", "month 4", pf.SLATE,
     "package for review: null\ntest M/8, M/16; growth at\nN/4-4N and M/8, M/16"),
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
    pf.text(ax, 0.9, 10.9, "now: G0 and G1 passed (G1 with reservations); G2 package "
            "assembled, waiting for its verifier and review", size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(16.6, 5.75), (17.0, 5.75), (16.8, 5.45)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 16.8, 6.05, "now", size=7.0, color=pf.RED)
    pf.brace(ax, 3.6, 8.8, 3.6, "", below=True)
    pf.text(ax, 6.2, 2.25, "done: infall criterion ruled;\nnote checked by the review",
            size=7.0, color=pf.ROSE)
    pf.brace(ax, 9.6, 14.8, 3.6, "", below=True)
    pf.text(ax, 12.2, 2.0, "done: null test to 500 M off\nthe relaxed lapse; growth in\n"
            "particles and mesh; M/4 out", size=7.0, color=pf.ROSE)
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
