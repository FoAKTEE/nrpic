"""Schematic: verification ladder of Track B toward gate G2 (state of 2026-11-24).

Each rung is a test of the code paths the track uses, from analytic waves at the bottom to the
population box at the top, with its reference and its state as judged in the package journals
(stage/G2/CHECKLIST.md and OPEN.md hold the evidence and run ids). Three states: passed (dark
green), partly passed or values without convergence (olive), open (grey). Project names stay out
of the figure (writing guide). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder"
W, H = 29.0, 17.6
PASS, PART, OPEN = pf.GREEN_DARK, pf.OLIVE, pf.GREY_LINE
# bottom to top: (test, reference, state, note)
RUNGS = [
    ("Linear waves in a periodic box", "analytic solution", PASS,
     "TT projection and Weyl parts agree"),
    ("Dust universe and linear growth", "exact background, linear theory", PASS,
     "sub-percent, converging in mesh and particles"),
    ("Two crossed waves to second order", "second-order strain", PASS,
     "box modes to a fraction of a per cent"),
    ("Newtonian pancake and ellipsoid", "Zel'dovich sheets, ellipsoid equations", PASS,
     "the scaling laws of the literature"),
    ("Shearing dust, small amplitude", "linear ray tracing", PASS,
     "within 1e-5 after extrapolation"),
    ("Shearing dust, large amplitude", "three other codes", PART,
     "beside the relativistic code, not converged"),
    ("Population: full GR against Newtonian", "same field, rescaled", PART,
     "halos, near field agree; stop at 2x amplitude"),
    ("Population: mesh, particle and gauge legs", "the run above", OPEN,
     "queued"),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    x0, w = 1.2, 25.4
    rh, gap = 1.35, 0.32
    y = 1.1
    # rails of the ladder
    pf.line(ax, (x0 - 0.5, 0.6), (x0 - 0.5, y + len(RUNGS) * (rh + gap) + 0.2),
            color=pf.INK, lw=1.4, dashed=False)
    pf.line(ax, (x0 + w + 0.5, 0.6), (x0 + w + 0.5, y + len(RUNGS) * (rh + gap) + 0.2),
            color=pf.INK, lw=1.4, dashed=False)
    for test, ref, col, note in RUNGS:
        pf.block(ax, x0, y, 9.6, rh, test, fill=col, size=7.0, radius=0.2)
        pf.rbox(ax, x0 + 9.9, y, 6.2, rh, radius=0.2)
        pf.text(ax, x0 + 13.0, y + rh / 2, ref, size=6.6, italic=True)
        pf.text(ax, x0 + 16.4, y + rh / 2, note, size=6.6, ha="left")
        y += rh + gap
    pf.text(ax, x0 + 4.8, y + 0.35, "test", size=8.0, bold=True)
    pf.text(ax, x0 + 13.0, y + 0.35, "reference", size=8.0, bold=True)
    pf.text(ax, x0 + 19.5, y + 0.35, "state", size=8.0, bold=True)
    # legend of the three states
    pf.legend_box(ax, x0 + 0.2, y + 1.0, 19.0, 1.0, [], size=7)
    for xx, lab, c in ((x0 + 0.8, "passed", PASS), (x0 + 5.0, "partly, or not converged", PART),
                       (x0 + 13.6, "open", OPEN)):
        pf.block(ax, xx, y + 1.22, 0.9, 0.56, "", fill=c, radius=0.1)
        pf.text(ax, xx + 1.2, y + 1.5, lab, size=7.0, bold=True, ha="left")
    pf.arrow(ax, (x0 + w + 1.3, 1.1), (x0 + w + 1.3, y - 0.3), lw=1.2, head=9)
    pf.text(ax, x0 + w + 1.75, (1.1 + y) / 2, "closer to the science runs", size=7.0, rot=90,
            italic=True)
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
