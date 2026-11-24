"""Schematic: the two reproductions of the note side by side.

Top lane, the lattice paper (arXiv:2512.14649): background and mode functions at N*, the
coarse-grained initial slice, the evolution with Z4c, an inflaton and the stochastic sources at
every Runge-Kutta stage, the dumps and the constraint record, the analysis, and the comparison
with the Mukhanov-Sasaki solution and with the paper's printed statements.
Bottom lane, the one-patch paper (arXiv:2401.08530): background, the Langevin pair for the lapse
and the e-folds, the paths in two stochastic readings, their statistics, and the comparison with
the paper's figures and statements. Middle: the computer-algebra check of the equations feeds
both lanes. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_pipeline"
W, H = 30.0, 12.4
BH = 1.5


def box(ax, x, y, w, label, fill, h=BH, size=6.8):
    pf.block(ax, x, y, w, h, label, fill=fill, size=size, radius=0.2)


def lane(ax, y0, h, title, sub):
    pf.panel(ax, 0.2, y0, W - 0.4, h, radius=0.7)
    pf.text(ax, 0.7, y0 + h - 0.45, title, size=8.6, bold=True, ha="left")
    pf.text(ax, W - 0.7, y0 + h - 0.45, sub, size=7.0, italic=True, ha="right")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    INP, CODE, ANA, CMP = pf.SLATE, pf.GREEN_DARK, pf.OLIVE, pf.PLUM
    # lattice lane
    y1 = 7.6
    lane(ax, y1 - 0.5, 4.6, "Lattice: stochastic numerical relativity",
         "slow roll and ultra-slow roll, up to 256 cells per side")
    xs = [0.7, 5.6, 10.5, 15.4, 20.3, 25.2]
    labels = [("background and\nmode functions at $N_*$", INP),
              ("coarse-grained\ninitial slice", INP),
              ("Z4c + inflaton,\nsources at every stage", CODE),
              ("dumps and\nconstraint record", CODE),
              ("spectra, contrasts,\nconstraints, shear", ANA),
              ("linear solution and\nprinted statements", CMP)]
    for x, (lab, col) in zip(xs, labels):
        box(ax, x, y1 + 0.6, 4.2, lab, col)
    for a, b in zip(xs[:-1], xs[1:]):
        pf.arrow(ax, (a + 4.2, y1 + 0.6 + BH / 2), (b, y1 + 0.6 + BH / 2), lw=1.1, head=7)
    # one-patch lane
    y2 = 1.2
    lane(ax, y2 - 0.5, 4.6, "One patch: Langevin pair in the uniform-field gauge",
         "fifty thousand paths per variant")
    labels2 = [("background:\nEuler step or converged", INP),
               ("noise amplitude\non the background", INP),
               ("lapse and e-folds,\nItô or Stratonovich", CODE),
               ("paths at the\nrecord times", CODE),
               ("widths, skewness,\nkurtosis, tails", ANA),
               ("printed figures\nand statements", CMP)]
    for x, (lab, col) in zip(xs, labels2):
        box(ax, x, y2 + 0.6, 4.2, lab, col)
    for a, b in zip(xs[:-1], xs[1:]):
        pf.arrow(ax, (a + 4.2, y2 + 0.6 + BH / 2), (b, y2 + 0.6 + BH / 2), lw=1.1, head=7)
    # middle: the equations
    box(ax, 9.0, 5.25, 12.0, "computer algebra: sources, constraints, gauge families, misprints",
        pf.RED, h=1.0, size=7.0)
    pf.arrow(ax, (12.6, 6.25), (12.6, y1 + 0.6), lw=1.0, head=6, dashed=True)
    pf.arrow(ax, (17.4, 5.25), (17.4, y2 + 0.6 + BH), lw=1.0, head=6, dashed=True)
    # legend
    pf.panel(ax, 0.2, 0.0, W - 0.4, 0.55, radius=0.25, fill=pf.CREAM_LEG)
    for x0, col, lab in ((1.0, INP, "input fixed before the run"), (8.6, CODE, "evolution"),
                         (14.2, ANA, "analysis of the outputs"), (21.2, CMP, "comparison")):
        pf.rbox(ax, x0, 0.12, 0.9, 0.32, fill=col, edge="none", radius=0.08, z=3)
        pf.text(ax, x0 + 1.15, 0.28, lab, size=7.2, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
