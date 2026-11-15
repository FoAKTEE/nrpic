"""Schematic: architecture of the C-sidm calculation in three states (note v0).

Exists = in this repository now (AthenaK release core-v0.3, or the track's reference and
analysis code, each with a registered run); to be ported = exists for another family or
setting in this repository and has to be carried over; new = still to be written (inside
AthenaK by core, decision 0010, or outside it by the track). Sources of the
classification: CLAUDE.md (release core-v0.3), stage/G0/OPEN.md items 6-12,
stage/G1/STATUS.md sections 1 and 4, stage/G0/REPORT.md sections 2 and 4, the outbox
requests of 2026-11-15 to core (perturbation recipe, static curved metric). No data are read.
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
    column(ax, 0.2, "Initial data", "steady states as particles", [
        ("thermal-core and King sequences", EXISTS),
        ("King, polytrope, shell particle models", EXISTS),
        ("code reads the tables and particles", EXISTS),
        ("Knudsen number to cross-section", EXISTS),
        ("thermal-core particle models", PORT),
        ("radial perturbation of a steady state", NEW),
        ("rotating cores", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK: spacetime, particles, collisions", [
        ("Z4c with particles: deposit, push", EXISTS),
        ("excision, apparent-horizon finder", EXISTS),
        ("Monte Carlo collisions in mesh cells", EXISTS),
        ("counter-based random numbers", EXISTS),
        ("collision kernels checked (T0)", EXISTS),
        ("collisions checked in the box (T0b-T11)", PORT),
        ("static curved metric for test T12", NEW),
        ("conservation budgets in curved spacetime", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("rate, relaxation, conduction, entropy", EXISTS),
        ("box analysis: slab sums, relaxation", EXISTS),
        ("exact radial-pulsation onset", EXISTS),
        ("onset with the Juttner index", PORT),
        ("growth rate of the radial mode", NEW),
        ("collapsed mass fraction at the horizon", NEW),
    ])
    for x0, x1 in ((9.6, 10.3), (19.7, 20.4)):
        pf.arrow(ax, (x0, 9.0), (x1, 9.0), lw=1.2, head=8)
    labels = ["collisionless threshold, three families", "mass fraction against Kn",
              "fluid limit as anchor"]
    widths = [10.4, 7.6, 6.6]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.55, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (25.1, 3.3), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S3", size=7.5, italic=True, ha="left")
    pf.panel(ax, 15.8, 0.22, 13.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((16.4, EXISTS, "exists"), (20.6, PORT, "to be ported"),
                         (25.8, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
