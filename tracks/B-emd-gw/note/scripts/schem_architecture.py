"""Schematic: architecture of Track B's calculation in three states (note v0).

Exists = in this repository now (AthenaK release core-v0.3 on main, the cosmology tools
under cosmo/, or the track's own reference and analysis code); to be ported = exists for
another setting in this repository and has to be carried over; new = to be written (by core
inside AthenaK, decision 0010, or by the track outside it). Sources of the classification:
stage/G0/OPEN.md items 2, 6-10; stage/G1/STATUS.md; the outbox requests
outbox/20261115T1340Z__to-core__*; CLAUDE.md (release core-v0.3: the Newtonian mode with its
quadrupole history is on main, coord/INTERFACES/newtonian_mode.md); the linear-wave
generator athenak/src/pgen/tests/z4c_linear_wave.cpp lines 107-112 (sign not yet fixed on
main). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
EXISTS, PORT, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 15.2


def column(ax, x, title, sub, items):
    pf.panel(ax, x, 3.3, 9.4, 11.5, radius=0.9)
    pf.text(ax, x + 4.7, 14.15, title, size=9.5, bold=True)
    pf.text(ax, x + 4.7, 13.45, sub, size=7.5, italic=True)
    y = 12.25
    for label, state in items:
        pf.block(ax, x + 0.4, y - 0.47, 8.6, 0.95, label, fill=state, size=7.2, radius=0.22)
        y -= 1.12
    return y


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial data", "constraint-solved, periodic", [
        ("scalar modes on the torus, spectral solve", EXISTS),
        ("crossed waves (1, eps, 0), plane-wave null", EXISTS),
        ("lattice, two particles per cell and direction", EXISTS),
        ("expanding-box wave of known decay", PORT),
        ("jittered lattice for the noise null", NEW),
        ("data with a transverse-traceless part", NEW),
        ("isolated triaxial patch, halo population", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK, release core-v0.3", [
        ("Z4c with particles in a periodic box", EXISTS),
        ("conformal-time lapse, zero shift", EXISTS),
        ("harmonic and 1+log slicing (gauge leg)", EXISTS),
        ("Newtonian gravity, quadrupole history", EXISTS),
        ("oblique linear wave (polarization sign)", PORT),
        ("thin periodic boxes with particles", PORT),
        ("TT spectra written during the run", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("Fourier TT projection, energy, spectra", EXISTS),
        ("Weyl E, B; fixed-direction Psi_4", EXISTS),
        ("exact Zel'dovich plane wave", EXISTS),
        ("Zel'dovich ellipsoid, quadrupole formula", EXISTS),
        ("second-order strain in the code's gauge", NEW),
        ("York TT part on the curved slice", NEW),
        ("planar dust reference in full GR", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.0), (x1, 9.0), lw=1.2, head=8)
    labels = ["burst of a pancake through shell crossing", "spectrum of a halo box",
              "relativistic minus Newtonian, per k"]
    widths = [10.4, 6.6, 9.6]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S2", size=7.5, italic=True, ha="left")
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"), (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
