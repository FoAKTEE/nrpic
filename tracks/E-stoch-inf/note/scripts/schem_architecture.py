"""Schematic: architecture of Track E's calculation (stochastic inflation in numerical
relativity) in three states.

Exists = in this repository now (AthenaK release core-v0.3, or the track's reference and
analysis code); to be ported = exists in this repository for another purpose and has to be
carried over; new = to be written (by core inside AthenaK, decision 0010, or by the track
outside it). Sources of the classification: spec/scope/SCOPE.md sections 6 and 9,
stage/G1/STATUS.md, coord/INTERFACES/scalar_field.md (sections 1, 4, 11 and the request
table), core's message tracks/core/outbox/20261115T1510Z__to-E-stoch-inf__scalar-field-merged.md,
CLAUDE.md (release core-v0.3). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
EXISTS, PORT, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 15.6


def column(ax, x, title, sub, items, w=9.4):
    pf.panel(ax, x, 3.3, w, 11.9, radius=0.9)
    pf.text(ax, x + w / 2, 14.55, title, size=9.5, bold=True)
    pf.text(ax, x + w / 2, 13.85, sub, size=7.5, italic=True)
    y = 12.65
    for label, state in items:
        pf.block(ax, x + 0.4, y - 0.47, w - 0.8, 0.95, label, fill=state, size=7.0, radius=0.22)
        y -= 1.12


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial slice and noise", "track tables, code at the start", [
        ("Friedmann background, both potentials", EXISTS),
        ("Bunch-Davies modes to the start, all shells", EXISTS),
        ("random amplitudes keyed by wave vector", EXISTS),
        ("mode table R and dR/dt at the start", NEW),
        ("transfer coefficients of the slice", NEW),
        ("perturbed geodesic slice, corrected momentum", NEW),
        ("constraint check of the generated slice", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK, release core-v0.3", [
        ("Z4c as BSSN, geodesic slicing, periodic", EXISTS),
        ("scalar field coupled through Tmunu", EXISTS),
        ("modes in lockstep with every stage", EXISTS),
        ("noise synthesis per MeshBlock, no FFT", EXISTS),
        ("kicks to Pi, K and A_ij at stage times", EXISTS),
        ("exact restart, layout-independent noise", EXISTS),
        ("box-mean coefficients (level 1)", PORT),
        ("local coefficients (level 2)", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("full and deformed Mukhanov-Sasaki modes", EXISTS),
        ("stochastic delta-N, both potentials", EXISTS),
        ("noise validator, tests A0-A15", EXISTS),
        ("dump readers, shell spectra", PORT),
        ("constraint ratios with [H] and [M]", PORT),
        ("curvature perturbation from the fields", NEW),
        ("per-mode amplitudes, freezing check", NEW),
        ("compaction function statistics", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.2), (x1, 9.2), lw=1.2, head=8)
    labels = ["slow-roll and USR cases reproduced", "freezing of super-horizon modes",
              "tail statistics against delta-N", "initial conditions to Track A"]
    widths = [8.2, 6.8, 6.8, 6.4]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.0)
        x += w + 0.25
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S11", size=7.5, italic=True, ha="left")
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"), (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
