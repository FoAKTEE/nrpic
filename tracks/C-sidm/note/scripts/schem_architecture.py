"""Schematic: architecture of the S3 calculation, state of gate G1 (note v1, 2026-11-20).

Three states per element. Exists: tested, in the released code or in the track's own
reference and analysis code, each with a registered run. To be ported: exists and is tested
on a branch of the code or for another family or setting, and has to be carried into the
released code or to the science runs. New: still to be written (inside the code by its
maintainers, or outside it by the track). The state of each element and the record it
is taken from are listed in the README of the note (section on the schematics); the plan of the round is not a source.
No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
EXISTS, PORT, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 30.0, 16.0
TOP = 15.2          # top of the column panels
ROW = 1.08          # vertical pitch of the blocks


def column(ax, x, title, sub, items, bottom=3.2):
    pf.panel(ax, x, bottom, 9.4, TOP - bottom, radius=0.9)
    pf.text(ax, x + 4.7, TOP - 0.62, title, size=9.5, bold=True)
    pf.text(ax, x + 4.7, TOP - 1.27, sub, size=7.5, italic=True)
    y = TOP - 2.35
    for label, state in items:
        pf.block(ax, x + 0.4, y - 0.45, 8.6, 0.90, label, fill=state, size=7.0, radius=0.22)
        y -= ROW


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    column(ax, 0.2, "Initial data", "steady states as particles", [
        ("thermal-core, King, monoenergetic sequences", EXISTS),
        ("King particle models", EXISTS),
        ("thermal-core particle models, b = 0.1", EXISTS),
        ("code reads the tables and particle files", EXISTS),
        ("Knudsen number to cross-section, all models", EXISTS),
        ("radial perturbation of a steady state", PORT),
        ("models with a million particles", NEW),
        ("rotating cores", NEW),
    ])
    column(ax, 10.3, "Evolution", "AthenaK: spacetime, particles, collisions", [
        ("Z4c with particles: deposit, push", EXISTS),
        ("excision, apparent-horizon finder", EXISTS),
        ("Monte Carlo collisions, released operator", EXISTS),
        ("box tests T0b-T11 of the released operator", EXISTS),
        ("pair energy at each particle's metric", PORT),
        ("static curved-metric test bed (T12)", EXISTS),
        ("heat conduction T6-T8 on processors", EXISTS),
        ("collisions on refined meshes", NEW),
        ("ADM energy diagnostic", NEW),
    ])
    column(ax, 20.4, "Analysis", "references outside the code", [
        ("rate, relaxation, conduction, entropy", EXISTS),
        ("box analysis; isobaric conduction reference", EXISTS),
        ("exact radial-pulsation onset", EXISTS),
        ("J\u00fcttner fluid onsets, thermal core and King", EXISTS),
        ("cluster histories: lapse, collisions, budgets", EXISTS),
        ("collapse and crossing times", EXISTS),
        ("growth-rate fit, checked on runs", PORT),
        ("threshold scan, three-way convergence", NEW),
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
    pf.arrow(ax, (25.1, 3.2), (25.1, 2.55), lw=1.2, head=8)
    pf.text(ax, 0.6, 0.7, "deliverables of S3", size=7.5, italic=True, ha="left")
    pf.panel(ax, 13.0, 0.22, 16.4, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((13.5, EXISTS, "exists, tested"), (18.75, PORT, "to be ported"),
                         (23.9, NEW, "new")):
        pf.rbox(ax, x0, 0.42, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.70, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))
    print(f"{STEM}: drawn (no data read)")


if __name__ == "__main__":
    main()
