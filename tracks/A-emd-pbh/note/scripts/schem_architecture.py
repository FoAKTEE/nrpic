"""Schematic: architecture of Track A's calculation in three states (note v0).

Exists = in this repository now (AthenaK release core-v0.3, or the track's reference and
analysis code); to be ported = exists for another setting in this repository and has to
be carried over; new = to be written (by core inside AthenaK, decision 0010, or by the
track outside it). Sources of the classification: stage/G0/OPEN.md item 3,
periodic_threshold/README.md (Requests, T2c, T3c), scope/SCOPE.md sections 4 and 6,
CLAUDE.md (release core-v0.3). No data are read.
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
    column(ax, 0.2, "Initial data", "track and core", [
        ("expanding dust ball, spherical tables", EXISTS),
        ("lattice particles on the cell centres", EXISTS),
        ("deformed ball for the Newtonian mode", EXISTS),
        ("periodic peak, torus constraint solve", PORT),
        ("peak data on a constant-K slice", NEW),
        ("initial velocity dispersion", NEW),
        ("two peaks in one envelope", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK, release core-v0.3", [
        ("Z4c with particles: deposit, push", EXISTS),
        ("geodesic and conformal-time slicing", EXISTS),
        ("Newtonian reference gravity", EXISTS),
        ("apparent-horizon finder, area mass", EXISTS),
        ("finder across periodic box faces", PORT),
        ("refined mesh with periodic particles", PORT),
        ("collapse slicing in a periodic box", NEW),
        ("horizon spin, projected rotation", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("exact shells: cycloid, LTB, trapping", EXISTS),
        ("analytic criteria, prediction table", EXISTS),
        ("Newtonian ellipsoid and top hat", EXISTS),
        ("invariants: areal radius, horizon mass", EXISTS),
        ("waveform against quadrupole", PORT),
        ("outcome rule and threshold bracket", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.0), (x1, 9.0), lw=1.2, head=8)
    # deliverables
    labels = ["threshold line in amplitude and ellipticity", "black-hole mass and growth",
              "spin at formation", "waveform"]
    widths = [10.2, 7.2, 5.6, 4.4]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S1", size=7.5, italic=True, ha="left")
    # legend (drawn by hand: legend_box spaces its labels for the canvas scale 0.5)
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"), (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
