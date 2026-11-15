"""Schematic: architecture of Track D's calculation in three states (note v0).

Exists = in this repository now (AthenaK release core-v0.3 on main, or the track's
reference and analysis code); to be ported = exists for another setting and has to be
carried over; new = to be written (inside AthenaK by core, decision 0010, or outside it by
the track). Sources of the classification: stage/G0/REPORT.md sections 2 and 6,
stage/G1/STATUS.md, stage/G0/OPEN.md, the outbox requests of the track
(outbox/20261115T1510Z__to-core__*), core's message on format 2 and punctures
(tracks/core/outbox/20261115T1510Z__to-D-bh-dress__ball-and-puncture-combined.md) and
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
    column(ax, 0.2, "Initial data", "track generators, AthenaK readers", [
        ("vacuum bubble in expanding dust + puncture", EXISTS),
        ("lattice dust and tracer particles", EXISTS),
        ("spinning or moving puncture with a table", EXISTS),
        ("vacuum control: same slice without dust", NEW),
        ("dust filled to the black hole (LTB)", NEW),
        ("warm dust: velocity dispersion", NEW),
        ("puncture in a periodic dust box", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK, release core-v0.3", [
        ("Z4c with particles, moving-puncture gauge", EXISTS),
        ("horizon finder, removal inside the horizon", EXISTS),
        ("geodesics on analytic Kerr", EXISTS),
        ("tracer push on the cards", PORT),
        ("Newtonian mode with a point mass", PORT),
        ("lapse for a black hole in expanding dust", NEW),
        ("accretion diagnostics at a sphere", NEW),
        ("excision with an analytic metric", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("exact bubble: wall, tracers, constant mass", EXISTS),
        ("probe-limit spike, Schwarzschild", EXISTS),
        ("self-similar infall, shells, capture", EXISTS),
        ("horizon-mass floor of a vacuum puncture", EXISTS),
        ("probe-limit spike, Kerr", NEW),
        ("tracer areal radius and proper time", PORT),
        ("accreted energy, two definitions", NEW),
        ("coupling exponent and its upper limit", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.0), (x1, 9.0), lw=1.2, head=8)
    labels = ["growth law of the black hole", "spike in the strong field",
              "null test of coupling", "dressed binaries"]
    widths = [8.0, 7.0, 6.2, 5.2]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S4", size=7.5, italic=True, ha="left")
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"), (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
