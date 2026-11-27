"""Schematic: the verification ladder of the tail statistics (gate G3 of the track).

From the bottom up: what was fixed before any production run (the statistic and its thresholds, the
one-patch reference of the same band with its variance gate, the three tests of the delta-N reader, the
pilot), the runs on the release build (mirrored pairs of the baseline, three amplitudes, a finer lattice,
level 2 of the backreaction), the two readers (the tabulated delta-N map checked on every box, the pair
statistics), and the outcome as read so far. The outcome texts are set in OUTCOME below from the pair
reading of the baseline (g3/JOURNAL.md entry 17); no data are read here.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder_g3"
W, H = 30.0, 15.6
BH = 1.55

# (label, kind) with kind in ok, bad, open, after; filled from the reading of the pairs (entry 17)
OUTCOME = [
    ("constraints with three\namplitudes: factor four", "ok"),
    ("finer lattice: odd part\nconverges at high order", "ok"),
    ("tail shape: skewness, tails\nat own width, asymmetry", "ok"),
    ("width: variance against\nthe one-patch reference", "bad"),
    ("level 2 of the\nbackreaction (sensitivity)", "open"),
    ("slicing: geodesic only\n(a stated limitation)", "after"),
]


def box(ax, x, y, w, label, fill, h=BH, size=6.8):
    pf.block(ax, x, y, w, h, label, fill=fill, size=size, radius=0.2)


def rung(ax, y0, h, title):
    pf.panel(ax, 0.2, y0, W - 0.4, h, radius=0.6)
    pf.text(ax, 0.7, y0 + h - 0.42, title, size=8.2, bold=True, ha="left")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    INP, CODE, ANA, OK, BAD, AFTER = pf.SLATE, pf.GREEN_DARK, pf.OLIVE, pf.GREEN_MID, pf.RED, pf.PLUM
    OPEN = pf.SLATE
    col = {"ok": OK, "bad": BAD, "open": OPEN, "after": AFTER}
    xs = [0.7, 7.95, 15.2, 22.45]
    y = 0.75
    rung(ax, y, 2.75, "1  Fixed before the production runs")
    for x, lab in zip(xs, ["statistic, estimator and\nthresholds of the comparison",
                           "one-patch $\\delta N$ of the same\nband, with a variance gate",
                           "three tests of the\n$\\delta N$ reader on small lattices",
                           "pilot of ten seeds:\ncost, health, Gaussian control"]):
        box(ax, x, y + 0.35, 6.85, lab, INP)
    y = 4.0
    rung(ax, y, 2.75, "2  Runs on the release build of the code (cards)")
    for x, lab in zip(xs, ["$128^3$ baseline: mirrored\npairs of seeds, $\\lambda = \\pm1$",
                           "three amplitudes with\nconstraint fields",
                           "$160^3$ against $128^3$\nat the same modes",
                           "level 2 of the backreaction,\nmirrored pairs (queued)"]):
        box(ax, x, y + 0.35, 6.85, lab, CODE)
    pf.arrow(ax, (W / 2, 3.5), (W / 2, 4.0 + 0.35), lw=1.1, head=7)
    y = 7.25
    rung(ax, y, 2.75, "3  Readers of the dumps")
    box(ax, 0.7, y + 0.35, 14.1, "tabulated $\\delta N$ map along the box relation,\n"
        "checked on every box against the full map", ANA)
    box(ax, 15.2, y + 0.35, 14.1, "pair statistics: width, skewness, kurtosis,\n"
        "tails at the own width, asymmetry", ANA)
    pf.arrow(ax, (W / 2, 6.75), (W / 2, 7.25 + 0.35), lw=1.1, head=7)
    y = 10.5
    rung(ax, y, 4.6, "4  Criteria and outcome")
    cw, gap = 4.5, 0.27
    for k, (lab, kind) in enumerate(OUTCOME[:3]):
        box(ax, 0.7 + k * (cw * 2.07 + gap), y + 2.15, cw * 2.07, lab, col[kind], size=6.6)
    for k, (lab, kind) in enumerate(OUTCOME[3:]):
        box(ax, 0.7 + k * (cw * 2.07 + gap), y + 0.3, cw * 2.07, lab, col[kind], size=6.6)
    pf.arrow(ax, (W / 2, 10.0), (W / 2, 10.5 + 0.3), lw=1.1, head=7)
    pf.panel(ax, 0.2, 0.0, W - 0.4, 0.55, radius=0.25, fill=pf.CREAM_LEG)
    for x0, c, lab in ((0.8, INP, "fixed in advance / open"), (7.6, CODE, "evolution"),
                       (12.0, ANA, "analysis"), (15.8, OK, "criterion holds"),
                       (20.6, BAD, "criterion fails"), (25.2, AFTER, "limitation")):
        pf.rbox(ax, x0, 0.12, 0.9, 0.32, fill=c, edge="none", radius=0.08, z=3)
        pf.text(ax, x0 + 1.15, 0.28, lab, size=7.2, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))
    fig.savefig(os.path.join(out, STEM + ".pdf"))


if __name__ == "__main__":
    main()
