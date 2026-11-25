"""Schematic: the verification ladder of the ultra-slow-roll lattice.

From the bottom up: what was fixed before any run (background and mode functions at N*, the
criteria, two seeds, three amplitudes with both signs), the runs on the release build of the code
(eleven runs: one seed at three amplitudes, a second seed, a finer lattice, a control with the
momentum source flipped), two independent readers of the dumps, the nine criteria grouped by what
they test, and the outcome: every criterion holds except the scaling of the momentum constraint at
one record time, which stays a failure as written; the reading with three amplitudes stands beside
it as a finding made after the data. No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_ladder"
W, H = 30.0, 15.6
BH = 1.55


def box(ax, x, y, w, label, fill, h=BH, size=6.8):
    pf.block(ax, x, y, w, h, label, fill=fill, size=size, radius=0.2)


def rung(ax, y0, h, title):
    pf.panel(ax, 0.2, y0, W - 0.4, h, radius=0.6)
    pf.text(ax, 0.7, y0 + h - 0.42, title, size=8.2, bold=True, ha="left")


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    INP, CODE, ANA, OK, BAD, AFTER = pf.SLATE, pf.GREEN_DARK, pf.OLIVE, pf.GREEN_MID, pf.RED, pf.PLUM
    # rung 1: fixed before the runs
    y = 0.75
    rung(ax, y, 2.75, "1  Fixed before the runs")
    xs = [0.7, 7.95, 15.2, 22.45]
    for x, lab in zip(xs, ["background and mode\nfunctions at $N_*$",
                           "nine criteria with\ntheir thresholds",
                           "two seeds of the\nrandom amplitudes",
                           "amplitudes $\\lambda = \\pm1, \\pm\\frac{1}{2}, \\pm\\frac{1}{4}$\n(even and odd parts)"]):
        box(ax, x, y + 0.35, 6.85, lab, INP)
    # rung 2: runs
    y = 4.0
    rung(ax, y, 2.75, "2  Runs on the release build of the code (cards)")
    for x, lab in zip(xs, ["$256^3$, first seed,\nthree amplitudes",
                           "$256^3$, second seed,\nfull amplitude",
                           "$320^3$, first seed,\nfull amplitude",
                           "$256^3$ control:\nmomentum source flipped"]):
        box(ax, x, y + 0.35, 6.85, lab, CODE)
    pf.arrow(ax, (W / 2, 3.5), (W / 2, 4.0 + 0.35), lw=1.1, head=7)
    # rung 3: readers
    y = 7.25
    rung(ax, y, 2.75, "3  Two readers of the dumps and records")
    box(ax, 0.7, y + 0.35, 14.1, "the track's analysis: curvature perturbation per mode,\n"
        "constraint parts, records", ANA)
    box(ax, 15.2, y + 0.35, 14.1, "a fresh verifier: own reader, own extraction, own\n"
        "background and Mukhanov-Sasaki reference", ANA)
    pf.arrow(ax, (W / 2, 6.75), (W / 2, 7.25 + 0.35), lw=1.1, head=7)
    # rung 4: criteria and outcome
    y = 10.5
    rung(ax, y, 4.6, "4  Criteria and outcome")
    crit = [("background\nlandmarks, means", OK), ("spectrum per mode,\nboth seeds", OK),
            ("freezing\nafter the crossing", OK), ("constraints: records,\ncontrol, floor", OK),
            ("resolution\n$256^3$ against $320^3$", OK), ("second seed,\none-point width", OK),
            ("coarse-graining\nwindow", OK)]
    cw, gap = 3.82, 0.24
    for k, (lab, col) in enumerate(crit):
        box(ax, 0.7 + k * (cw + gap), y + 2.15, cw, lab, col, size=6.2)
    box(ax, 0.7, y + 0.3, 14.1, "scaling of the momentum constraint with the amplitude:\n"
        "fails at one record time of eleven (stays failed as written)", BAD)
    box(ax, 15.2, y + 0.3, 14.1, "three amplitudes: the miss comes from the noise-level\n"
        "estimator fixed in advance (a finding made after the data)", AFTER)
    pf.arrow(ax, (14.8, y + 0.3 + BH / 2), (15.2, y + 0.3 + BH / 2), lw=1.1, head=7, dashed=True)
    pf.arrow(ax, (W / 2, 10.0), (W / 2, 10.5 + 0.3), lw=1.1, head=7)
    # legend
    pf.panel(ax, 0.2, 0.0, W - 0.4, 0.55, radius=0.25, fill=pf.CREAM_LEG)
    for x0, col, lab in ((0.8, INP, "fixed in advance"), (6.0, CODE, "evolution"),
                         (10.4, ANA, "analysis"), (14.2, OK, "criterion holds"),
                         (19.0, BAD, "criterion fails"), (23.6, AFTER, "after the data")):
        pf.rbox(ax, x0, 0.12, 0.9, 0.32, fill=col, edge="none", radius=0.08, z=3)
        pf.text(ax, x0 + 1.15, 0.28, lab, size=7.2, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
