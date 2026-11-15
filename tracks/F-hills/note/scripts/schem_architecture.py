"""Schematic: architecture of the F-hills calculation in three states (note v0).

Exists = in this repository now (AthenaK release core-v0.3, or the track's reference and
analysis code with registered runs); to be ported = exists in another setting or as a
workaround and has to be carried over into the code or the production set-up; new = still to
be written (inside AthenaK by core, decision 0010, or outside it by the track). Sources of
the classification: CLAUDE.md (release core-v0.3: several black holes with momentum and spin,
Newtonian reference gravity), coord/INTERFACES/multi_puncture.md sections 1 and 9,
stage/G0/SCOPING.md sections 2 and 7, stage/G0/OPEN.md items 7, 8, 10, stage/G1/STATUS.md,
nr_first/JOURNAL.md E4-E6 (readers, tracker files across restarts), and the outbox requests
of 2026-11-15 to core (unequal-mass gauge, two cards or larger blocks, pairwise common
horizon, moving clump data) and to C-sidm (clump models). No data are read.
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


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial data", "three bodies at four tidal radii", [
        ("boosted punctures, approximate constraints", EXISTS),
        ("Newtonian start state from ten tidal radii", EXISTS),
        ("passage inputs at mass ratios four and ten", EXISTS),
        ("clump equilibria of Track C, at rest", PORT),
        ("constraint-solved three-body data", NEW),
        ("moving collisionless clumps (object b)", NEW),
        ("dressed black holes (object c)", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK: Z4c, punctures, particles", [
        ("moving punctures, trackers, horizon finders", EXISTS),
        ("refinement around three length scales", EXISTS),
        ("wave extraction on spheres", EXISTS),
        ("self-gravitating particles for clumps", EXISTS),
        ("tracker files kept across restarts", PORT),
        ("gauge damping per black hole mass", NEW),
        ("two cards or larger blocks at m/16", NEW),
        ("common-horizon trigger per pair", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("restricted and full Newtonian three bodies", EXISTS),
        ("geodesic baseline, Schwarzschild and Kerr", EXISTS),
        ("readers: trackers, horizons, energies", EXISTS),
        ("radiated energy from the wave signal", EXISTS),
        ("references restarted from the code's state", PORT),
        ("inclined encounters in Kerr", NEW),
        ("stripping and heating of clump members", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.0), (x1, 9.0), lw=1.2, head=8)
    labels = ["separation boundary in pericentre", "energy split, fate of the captured member",
              "wave burst"]
    widths = [8.8, 10.6, 4.4]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S12", size=7.5, italic=True, ha="left")
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"),
                         (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
