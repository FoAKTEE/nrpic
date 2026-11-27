#!/usr/bin/env python3
"""Schematic: the G2 verification ladder of Track D (checklist C9 of stage/G2), state of the
signed G2 package (lead of batch 34, 2026-11-27; first drawn in batch 11b, 2026-11-24). Each rung is one test on the code paths D uses, from the
pusher up to the dust-filled bubble; the pill on the right gives its state with the run ids in
stage/G2/LADDER.md and g2long/JOURNAL.md entries 5, 11, 12, 14 and 17. No data are read: the numbers in
the boxes are copied from those entries.

    schem_ladder.py [--out DIR]       writes schem_ladder.png/.svg (paperfig style)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder"
W, H = 30.0, 19.0
DONE, PART, OPEN = pf.GREEN_DARK, pf.OLIVE, pf.RED

# bottom to top: (title, body, state label, state colour)
RUNGS = [
    ("Particles on a mesh metric (core, G1)",
     "geodesics in Kerr to the published digits; Kerr spike a = 0.8 stationary in AthenaK",
     "passed", DONE),
    ("Vacuum puncture: horizon-mass floor (M/4, M/8, M/16, faces +-768 M)",
     "production finder: plateaus 1.3e-4 apart from 230 M on, the finder's stopping rule (FP2, FP3);\n"
     "converged finder: drift within 1.8e-5 (M/8, to 500 M) and 3.9e-6 (M/16, to 300 M)",
     "cause found", DONE),
    ("Vacuum bubble in expanding dust: null test N",
     "run's finder: 2.28e-4 (M/8, 500 M), 1.99e-4 (M/16, 300 M); converged finder: <= 7.3e-5\n"
     "(M/8), <= 5.5e-5 (M/16), a dip of the bubble's mass at 100 M, no trend; M/4 fails (outside the regime)",
     "holds, 2 meshes", DONE),
    ("Dust filling the bubble: growth against exact dust and flux (G)",
     "M/8 to 500 M: every 10 M bin within 0.62 per cent of exact LTB;\n"
     "M/16 to 300 M: within 0.49 per cent; excision kept on (FK): within 0.25 per cent; M/4 outside the regime",
     "holds, 2 meshes", DONE),
    ("Particle number and relaxation (N/4, N, 4N)",
     "N/4, N, 4N to 400 M: every bin within 0.29 per cent; differences fall as N^-1/2 (window ratios 1.9-3.1)",
     "converges", DONE),
    ("Constraints outside the horizon",
     "plane norms of H and M outside 1.2 r_AH bounded to 500 M (XC1);\n"
     "with dust 100 times the vacuum residual, lower with more particles per cell",
     "bounded", PART),
]


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.27)
    x0, w, h, gap = 4.2, 19.6, 2.2, 0.45
    # rails of the ladder
    ytop = 1.2 + len(RUNGS) * (h + gap)
    for xr in (2.9, 3.4):
        pf.line(ax, (xr, 0.8), (xr, ytop + 0.4), color=pf.GREY_LINE, dashed=False, lw=1.4)
    for k, (title, body, state, col) in enumerate(RUNGS):
        y = 1.2 + k * (h + gap)
        pf.line(ax, (2.9, y + h / 2), (x0 - 0.15, y + h / 2), color=pf.GREY_LINE, dashed=False, lw=1.4)
        pf.callout(ax, x0, y, w, h, title, body, bar=col, size=6.6, title_size=7.6, band=0.75)
        pf.pill(ax, x0 + w + 0.5, y + h / 2 - 0.45, 4.6, 0.9, state, fill=col, size=7.0)
    yt = ytop + 0.3
    pf.block(ax, x0, yt, w, 1.1, "G3: growth law and spike at three resolutions; upper limit on a coupling M ~ a^k",
             fill=pf.GREY_FILL, tcolor=pf.INK, size=7.2)
    pf.text(ax, x0 + w + 2.8, yt + 0.55, "next gate", size=7.0, italic=True, color=pf.ROSE)
    pf.text(ax, 1.0, ytop + 0.5, "G2", size=9, bold=True, rot=90)
    pf.text(ax, x0, 0.45, "release core-v0.6, plain 1+log with Gamma-driver shift, cfl 0.25, no lapse_leak; "
            "boundary member: faces +-192/384/768 M; gauge member: lapse_leak 0.5 (G1)",
            size=6.3, ha="left", italic=True)
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
