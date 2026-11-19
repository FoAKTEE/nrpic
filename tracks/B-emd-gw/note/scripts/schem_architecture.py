"""Schematic: architecture of Track B's calculation at gate G1 (note v1).

Each box is classified by evidence, not by authorship:
  verified (green)   used by the track in a registered run that passed its test;
  on a branch (slate) exists on a tested branch of the code (core/requests-b, executables
                     scratch/core/exe/core_requests-b/, READY) and has not been run by the track;
  to be written (red).
Evidence of the green boxes (run ids under tracks/B-emd-gw/runs/; journals named):
  spectral constraint solve on the torus, crossed waves and the plane-wave null:
    B-20261115-161656-03d75e1, -164104-886798f (initial data), scan B-20261115-164059-d802e82,
    -165353-b592d43, analyses -174722-ba1048d, -180834-c77a132 (first_source/JOURNAL.md P0-P6);
  two particles per cell and direction: the same runs and B-emd-gw-20261115-115902-a3207d7;
  Z4c with particles, conformal-time lapse with zero shift: the same scan runs;
  Gamma-driver shift in the expanding box: B-20261115-165353-b592d43 (case cw_eps1_gd, P6a);
  harmonic and 1+log slicing in the vacuum box: wave-1 gauge record (periodic_z4c, L2 check f,
    B-emd-gw-20261115-131027-03b1119);
  Newtonian gravity with the quadrupole history: B-20261115-173904-a7297e3,
    -174405-af11300 (newton_tests/JOURNAL.md P1, P2, N1, N3);
  flat TT projection, energy, spectra; Weyl E, B; fixed-direction Psi_4: wave-1 runs
    B-emd-gw-20261115-120128-7dfaa38 and the scan analyses;
  spatial-gauge piece G_tot: T0 B-20261115-164221-6a6b779 and the second gauge (P6c);
  second-order strain s g(tau): the scan (P2);
  exact Zel'dovich plane wave, Zel'dovich and homogeneous ellipsoid: B-emd-gw-20261115-123852-ea4475c,
    B-emd-gw-20261115-115752-840e994, B-20261115-174405-af11300.
Slate boxes: oblique-wave polarization, double-precision mesh output and the time label of
Psi_4 (READY items 1-3), thin periodic boxes and the lattice jitter (READY item 4).
Red boxes: stage/G1/OPEN.md items 7-12, newton_tests requests 1-2, scope/SCOPE.md. No data
are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
DONE, BRANCH, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 15.0


def column(ax, x, title, sub, items):
    pf.panel(ax, x, 3.3, 9.4, 11.3, radius=0.9)
    pf.text(ax, x + 4.7, 13.95, title, size=9.5, bold=True)
    pf.text(ax, x + 4.7, 13.25, sub, size=7.5, italic=True)
    y = 12.05
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
    column(ax, 0.2, "Initial data", "constraint-solved on the torus", [
        ("scalar modes, spectral solve of the constraints", DONE),
        ("crossed waves (1, eps, 0), plane-wave null", DONE),
        ("lattice, two particles per cell and direction", DONE),
        ("isolated ellipsoid, Newtonian", DONE),
        ("jittered lattice for the noise floor", BRANCH),
        ("thin periodic boxes", BRANCH),
        ("data with a TT part in the expanding box", NEW),
        ("halo population in a small box", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK", [
        ("Z4c with particles in a periodic box", DONE),
        ("conformal-time lapse, zero shift", DONE),
        ("driven shift in the expanding box", DONE),
        ("harmonic and 1+log slicing, vacuum box", DONE),
        ("Newtonian gravity, quadrupole history", DONE),
        ("oblique wave, double-precision dumps", BRANCH),
        ("quadrupole history of one species", NEW),
        ("fourth-order Newtonian force", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("flat TT projection, energy, spectra", DONE),
        ("Weyl E, B; fixed-direction Psi_4", DONE),
        ("spatial-gauge piece of the projection", DONE),
        ("second-order strain of the crossed waves", DONE),
        ("Zel'dovich sheets and ellipsoid ODE", DONE),
        ("slicing part of the second-order gauge", NEW),
        ("York TT part on the curved slice", NEW),
        ("planar dust reference in full GR", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 8.4), (x1, 8.4), lw=1.2, head=8)
    labels = ["burst of a pancake through shell crossing", "spectrum of a halo box",
              "relativistic minus Newtonian, per k"]
    widths = [10.4, 6.6, 9.6]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S2", size=7.5, italic=True, ha="left")
    pf.panel(ax, 12.2, 0.22, 17.2, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((12.7, DONE, "verified in a run"), (18.6, BRANCH, "on a tested branch"),
                         (24.5, NEW, "to be written")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.6, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
