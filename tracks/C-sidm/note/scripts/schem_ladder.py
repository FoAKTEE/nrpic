"""Schematic (gate G2): the verification ladder of C-sidm, state of 2026-11-27.

Rungs from the bottom: what each test establishes, the evidence that decides it (no numbers:
they are in Tables III-VI of the note), and its state. States: passed; passed with a failure on
record (the failure stays in JOURNAL.md and stage/G2/CHECKLIST.md with its ruling); next gate.
Sources of the states: stage/G1/CHECKLIST.md (signed, coord/GATES.md 2026-11-21),
stage/G2/CHECKLIST.md items C1-C4, C7-C9, JOURNAL.md entries 2026-11-24T13:12Z,
2026-11-26T12:20Z and 2026-11-27 (outcomes B20.1, B20.3). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder"
PASS, REC, NEXT = pf.GREEN_DARK, pf.OLIVE, pf.RED
W, H = 30.0, 15.0
# (rung, evidence, state, state label); bottom first
RUNGS = [
    ("collision operator in a flat box", "rate, relaxation, entropy, replay, conduction at both ends",
     PASS, "passed"),
    ("pair energy at each particle's metric", "static curved test bed;\nfirst-step energy of the King model",
     PASS, "passed"),
    ("steady state held by the control", "turning-point model holds at a million particles;\n"
     "with fewer particles it collapses by noise", REC, "passed;\nfailures on record"),
    ("collisionless threshold bracketed", "kicked members either side of the turning point\n"
     "keep their fates: two N, two meshes, two gauges", PASS, "passed"),
    ("collisional collapse and its budgets", "Kn = 10 on three meshes and in two gauges;\nenergy of the collisions conserved to rounding",
     REC, "passed; one\nfailure on record"),
    ("collapsed mass fraction against Kn", "converged in collision step and particle number",
     NEXT, "next gate"),
]
GATE_SPANS = [("G1", 0, 1), ("G2", 2, 4), ("G3", 5, 5)]


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    x0, x1 = 3.2, 27.0
    y0, pitch, hgt = 1.6, 2.05, 1.45
    pf.panel(ax, x0 - 0.5, y0 - 0.6, x1 - x0 + 1.0, len(RUNGS) * pitch + 0.5, radius=0.8)
    for k, (rung, ev, col, lab) in enumerate(RUNGS):
        y = y0 + k * pitch
        pf.block(ax, x0, y, 8.4, hgt, rung, fill=col, size=7.0, radius=0.22)
        pf.text(ax, x0 + 8.9, y + hgt / 2, ev, size=6.6, ha="left")
        pf.pill(ax, x1 - 4.6, y + 0.1, 4.6, hgt - 0.2, lab, fill=col, size=6.4)
        if k + 1 < len(RUNGS):
            pf.arrow(ax, (x0 + 4.2, y + hgt), (x0 + 4.2, y + pitch), lw=1.0, head=7)
    for g, a, b in GATE_SPANS:
        ya = y0 + a * pitch + 0.1
        yb = y0 + b * pitch + hgt - 0.1
        pf.line(ax, (1.9, ya), (1.9, yb), color=pf.ROSE_LINE, lw=1.4, dashed=False)
        pf.text(ax, 1.0, (ya + yb) / 2, g, size=8.5, bold=True, color=pf.ROSE)
    pf.text(ax, x0, y0 + len(RUNGS) * pitch + 0.35,
            "verification ladder of the S3 calculation; collapse is the lapse marker throughout",
            size=7.5, italic=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))
    print(f"{STEM}: drawn (no data read)")


if __name__ == "__main__":
    main()
