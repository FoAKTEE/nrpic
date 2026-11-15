"""Schematic: stage timeline of Track E (note v0).

Gates and indicative times: spec/scope/SCOPE.md section 10 (charter 9.2); content of each
gate: the track sheet (brief 798, charter 9.8) as made concrete in SCOPE.md section 4 and
stage/G1/STATUS.md; the ruling of decision 0013 (continue to G1 and G2, scope of G3 decided
at G2); the card-hour allotment of decision 0014; what each step waits for: the outbox
requests of 2026-11-15T14:10Z and core's answer (scalar-field-merged message).
Gate positions are evenly spaced; the labels give the indicative times. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_timeline"
W, H = 30.0, 12.4
GATES = [
    ("G0 feasibility", "week 2", pf.GREEN_DARK,
     "specification, code base,\ncompute estimate; group:\ncontinue, shrink, downgrade"),
    ("G1 slow roll", "week 8", pf.GREEN_DARK,
     "spectrum per mode, freezing,\nconstraints converge;\nbackground, order, noise"),
    ("G2 ultra-slow roll", "month 4", pf.SLATE,
     "USR case reproduced;\nwindow, Courant factor\nand resolution varied"),
    ("G3 tail statistics", "month 9", pf.RED,
     "many realisations against\ndelta-N; compaction\nfunction to Track A"),
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
    pf.text(ax, 0.9, 11.3, "now: wave 2; G0 submitted, the group's decision pending "
            "(ruling: continue to G1 and G2)", size=7.5, ha="left", italic=True)
    ax.add_patch(pf.Polygon([(4.6, 5.95), (5.0, 5.95), (4.8, 5.65)], closed=True,
                            fc=pf.RED, ec="none", zorder=8))
    pf.text(ax, 4.8, 6.25, "now", size=7.0, color=pf.RED)
    needs = [
        (3.6, 8.8, "initial slice at the start,\nmode and transfer tables,\n"
                   "analysis of the output"),
        (9.6, 14.8, "slow-roll runs at 256 cells\nand the ladder; about one\n"
                    "card-hour"),
        (15.6, 20.8, "cost of one realisation\nmeasured; scope of G3\n"
                     "decided by the group"),
        (21.6, 26.6, "hundreds of card-hours\nor smaller boxes and\nimportance sampling"),
    ]
    for x0, x1, txt in needs:
        pf.brace(ax, x0, x1, 3.75, "", below=True)
        pf.text(ax, 0.5 * (x0 + x1), 2.15, txt, size=7.0, color=pf.ROSE)
    pf.text(ax, 0.6, 0.45, "needs between gates", size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
