"""Schematic: data flow of Track B's G1 calculations (note v1).

From the initial data through the code to the figures and the ledger of the note, as run in
wave 2: initial data of the crossed waves (cosmo/ic/make_east.py through
first_source/scripts/build_ic.sh; particle files of newton_tests/scripts/make_particles.py),
AthenaK in full GR and in its Newtonian mode (first_source/inputs/crossed.athinput,
newton_tests/inputs/*.athinput), outputs (z4c `bin` every 0.1 in tau, restart dumps,
newton.newton.hst), analysis (gw_diag and first_source/fslib: modes.py, gauge.py;
newton_tests/scripts/analyze_*.py), references (fslib/reference.py and this note's g1data.py,
verify_cosmo/scripts/zeldovich.py, the ellipsoid ODE of baseline/), and the note's scripts.
Every arrow is a registered run (manifest under tracks/B-emd-gw/runs/: command, commit,
inputs with sha256, outputs with sha256). Project names stay out of the figure (writing guide).
No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_dataflow"
W, H = 30.0, 11.6
COLS = [
    ("Initial data", "on the torus", pf.GREEN_DARK, [
        "potential of the\ncrossed waves",
        "spectral solve of\nthe constraints",
        "particle lattice,\nZel'dovich displacement"]),
    ("Evolution", "AthenaK", pf.SLATE, [
        "Z4c with particles,\nfull relativity",
        "same particles,\nNewtonian gravity"]),
    ("Outputs", "written during the run", pf.GREEN_MID, [
        "metric, single precision,\nevery tenth of a time unit",
        "full state,\ndouble precision",
        "history of the\nquadrupole moments"]),
    ("Analysis", "outside the code", pf.RED, [
        "flat TT projection,\nbox-mode amplitudes",
        "spatial-gauge piece\nof the projection",
        "Weyl electric and\nmagnetic parts",
        "quadrupole energy"]),
    ("Comparison", "with references", pf.PLUM, [
        "second-order strain\nwith its junk solution",
        "exact Zel'dovich sheets",
        "ellipsoid equations"]),
]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    cw, gap, x0 = 5.5, 0.55, 0.2
    top, bottom = 11.3, 3.2
    for j, (title, sub, col, items) in enumerate(COLS):
        x = x0 + j * (cw + gap)
        pf.panel(ax, x, bottom, cw, top - bottom, radius=0.7)
        pf.text(ax, x + cw / 2, top - 0.6, title, size=9.0, bold=True)
        pf.text(ax, x + cw / 2, top - 1.2, sub, size=7.0, italic=True)
        n = len(items)
        bh, bg = 1.25, 0.32
        span = n * bh + (n - 1) * bg
        y = (top - 1.7 + bottom) / 2 + span / 2
        for lab in items:
            pf.block(ax, x + 0.3, y - bh, cw - 0.6, bh, lab, fill=col, size=6.6, radius=0.2)
            y -= bh + bg
        if j < len(COLS) - 1:
            xa = x + cw
            pf.arrow(ax, (xa + 0.02, 7.0), (xa + gap - 0.02, 7.0), lw=1.2, head=8)
    # the record of every step
    pf.rose_panel(ax, 0.2, 0.25, 21.6, 2.2, radius=0.6)
    pf.text(ax, 11.0, 1.62, "every arrow is a registered run", size=7.5, bold=True, color=pf.ROSE)
    pf.text(ax, 11.0, 0.95, "command, code version, inputs and outputs with checksums",
            size=7.0, italic=True, color=pf.ROSE)
    xl = x0 + 4 * (cw + gap) + cw / 2
    pf.arrow(ax, (xl, bottom), (xl, 2.45), lw=1.2, head=8)
    pf.pill(ax, 22.6, 1.0, 7.2, 1.4, "figures and ledger of the note", fill=pf.INK, size=7.2)
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
