"""Schematic: stage timeline of Track E, state of 2026-11-24 (wave 3, batch 15).

Gates and indicative times: spec/scope/SCOPE.md section 10 (charter 9.2). State of each gate
(coord/GATES.md): G0 passed 2026-11-20 (continue to G1 and G2); G1 passed with reservations
2026-11-21; G2 (the ultra-slow-roll case against the criteria of SCOPE 4c) has its package
complete with one criterion failed on record (U-A4'(a); rulings 0030 item 2, 0036 item 2) and
goes to independent review; G3 and G4 ahead. Gate positions are evenly spaced; the labels give
the indicative times. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.8
PASSED, NOW, AHEAD = pf.GREEN_DARK, pf.SLATE, pf.RED
GATES = [
    ("G0 feasibility", "week 2", PASSED,
     "specification, code base,\ncost; passed: continue\nto G1 and G2"),
    ("G1 slow roll", "week 8", PASSED,
     "spectrum, freezing and\nconstraints met as ruled;\npassed with reservations"),
    ("G2 ultra-slow roll", "month 4", NOW,
     "eight of nine criteria met;\none failure on record;\nready for review"),
    ("G3 tail statistics", "month 9", AHEAD,
     "many realisations against\ndelta N; compaction\nfunction to Track A"),
    ("G4 paper", "month 12", AHEAD,
     "manuscript and\nreproduction package"),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    y0 = 5.4
    pf.timeline(ax, 0.3, 29.7, y0, color=pf.GREEN_DARK, lw=2.2, fade_in=True, head=9)
    xs = [3.2, 9.2, 15.2, 21.2, 27.0]
    for x, (title, when, col, body) in zip(xs, GATES):
        ax.add_patch(pf.Circle((x, y0), 0.32, fc=col, ec=pf.WHITE, lw=1.0, zorder=7))
        pf.text(ax, x, y0 - 0.85, when, size=7.5, color=pf.ROSE, italic=True)
        cw = 5.5
        pf.callout(ax, x - cw / 2 + 0.1, 6.5, cw, 3.7, title, body, bar=col, size=7.0,
                   title_size=8.0, band=0.8)
        pf.line(ax, (x, y0 + 0.35), (x, 6.5), color=pf.GREY_LINE)
    pf.text(ax, 0.9, 11.75, "now: 24 November 2026; G0 and G1 passed, G2 package ready for review",
            size=7.5, ha="left", italic=True)
    xn = 14.0
    ax.add_patch(pf.Polygon([(xn - 0.2, 5.95), (xn + 0.2, 5.95), (xn, 5.65)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, xn, 6.25, "now", size=7.0, color=pf.RED)
    needs = [
        (3.6, 8.8, "done: slow-roll ladder,\nindependent check,\ngate review"),
        (9.6, 14.8, "done: release runs at\nthree amplitudes, 320 cells,\nwindow scan, fresh check"),
        (15.6, 20.8, "scope of G3 decided at G2;\nhundreds of card-hours or\nimportance sampling"),
        (21.6, 26.6, "tail statistics written\nup; hand-over to\nthe particle runs"),
    ]
    for x0, x1, txt in needs:
        pf.brace(ax, x0, x1, 3.75, "", below=True)
        pf.text(ax, 0.5 * (x0 + x1), 2.15, txt, size=7.0, color=pf.ROSE)
    pf.text(ax, 0.6, 0.45, "needs between gates", size=7.5, italic=True, ha="left")
    pf.panel(ax, 17.6, 0.12, 11.8, 0.9, radius=0.35, fill=pf.CREAM_LEG)
    for x0, col, lab in ((18.0, PASSED, "passed"), (21.6, NOW, "in progress"),
                         (26.0, AHEAD, "ahead")):
        ax.add_patch(pf.Circle((x0 + 0.3, 0.57), 0.25, fc=col, ec="none", zorder=4))
        pf.text(ax, x0 + 0.8, 0.57, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
