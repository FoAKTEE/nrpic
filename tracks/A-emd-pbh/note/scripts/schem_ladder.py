"""Schematic: the verification ladder of Track A at gate G2 (item C10).

Rungs from the exact references to the threshold line of gate G3; each rung is coloured by
its state at the G2 package (passed / passed with clauses refuted on record / failed on
record with a ruling / next gate). Sources: stage/G2/CHECKLIST.md items C1-C3, C7, C8 and the
journals of conv_ball, threshold_ball, szekeres and periodic_threshold. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder"
PASS, PART, FAIL, NEXT = pf.GREEN_DARK, pf.SLATE, pf.RED, pf.PLUM
W, H = 30.0, 17.0

RUNGS = [  # (label, detail, state)
    ("exact references", "cycloid ball, LTB peak, Szekeres hole, Zel'dovich axes", PASS),
    ("expanding ball against the exact solution", "horizon time and mass: mesh, particles, radius, boundary", PASS),
    ("threshold of the ball", "eight amplitudes; code bracket equals the exact one", PASS),
    ("Szekeres hole in a periodic box", "fourth-order convergence of the non-spherical part", PART),
    ("constraint norms against the bound", "residual of the evolution unexplained (C3)", FAIL),
    ("spherical peak against LTB", "shells follow; horizon finder fails on the slice", FAIL),
    ("triaxial peak, first shell crossing", "lags Zel'dovich; lag scales with amplitude", FAIL),
    ("threshold line in amplitude and ellipticity", "gate G3", NEXT),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    pf.panel(ax, 0.3, 1.6, 29.4, 15.0, radius=0.9)
    y = 1.95
    step = 1.75
    for k, (lab, det, state) in enumerate(RUNGS):
        pf.block(ax, 1.0, y, 11.6, 1.25, lab, fill=state, size=7.4, radius=0.22)
        pf.text(ax, 13.2, y + 0.62, det, size=7.2, ha="left", italic=True)
        if k + 1 < len(RUNGS):
            pf.arrow(ax, (6.8, y + 1.25), (6.8, y + step), lw=1.0, head=6)
        y += step
    pf.panel(ax, 1.0, 0.2, 28.0, 1.0, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((1.6, PASS, "passed"), (6.6, PART, "passed, clauses refuted on record"),
                         (17.6, FAIL, "failed on record, ruled"), (25.0, NEXT, "next gate")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.2, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
