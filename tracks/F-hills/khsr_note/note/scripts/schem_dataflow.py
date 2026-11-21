"""Schematic: data flow of one full-relativity passage (note v1, gate G1).

From the input of the passage through AthenaK on one card in chained segments, the output
streams (trackers, horizon summaries, wave modes on the extraction spheres, history, restart
trees), the readers that join the segments, the analyses and their comparison with the
reference models started from the same state, to the figures and the ledger of the note. Two
rows, read left to right; the connector carries the outputs from the end of the first row to
the readers. Colours as in schem_architecture.py (exists / to be ported / new as of release
core-v0.3). Sources: nr_first/README.md (P1 input, chain command, wrapper, readers E4, passage
analysis E9, junk of the three black holes not yet measured, found flag requested of core),
nr_first/scripts/nrread.py header (file formats, restart behaviour of each stream),
nr_first/JOURNAL.md E11 (restart trees against the rule model), harness/RULES.md section
nrpic-run (registered runs, checksums), PLAN-wave3.md round 1 (preempted segment not
resubmitted). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_dataflow"
EXISTS, PORT, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 33.0, 18.0
GAP = 0.7
BH, STEP, SIZE = 0.8, 0.95, 7.0


def stage(ax, x, y0, w, h, title, sub):
    pf.panel(ax, x, y0, w, h, radius=0.7)
    pf.text(ax, x + w / 2, y0 + h - 0.6, title, size=9.5, bold=True)
    pf.text(ax, x + w / 2, y0 + h - 1.18, sub, size=7.2, italic=True)
    return y0 + h - 2.0          # centre of the first block


def blocks(ax, x, w, y, items, size=SIZE):
    for label, state in items:
        pf.block(ax, x + 0.3, y - BH / 2, w - 0.6, BH, label, fill=state, size=size,
                 radius=0.18)
        y -= STEP
    return y


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    r1y, r1h = 10.15, 7.6         # first row
    r2y, r2h = 1.55, 7.0          # second row
    wa = [8.6, 13.0, 9.6]
    wb = [9.6, 13.0, 8.6]
    xa = [0.2, 0.2 + wa[0] + GAP, 0.2 + wa[0] + wa[1] + 2 * GAP]
    xb = [0.2, 0.2 + wb[0] + GAP, 0.2 + wb[0] + wb[1] + 2 * GAP]

    # ---- first row: input, AthenaK, output streams
    y = stage(ax, xa[0], r1y, wa[0], r1h, "Input", "one file per passage")
    blocks(ax, xa[0], wa[0], y, [
        ("three punctures with momenta", EXISTS),
        ("Newtonian state at four tidal radii", EXISTS),
        ("three refinement nests, a wave zone", EXISTS),
        ("gauge, horizon finders, four spheres", EXISTS),
        ("start state on a relativistic parabola", NEW),
    ])
    x, w = xa[1], wa[1]
    y = stage(ax, x, r1y, w, r1h, "AthenaK on one card", "chained segments, each under an hour")
    segs = ["segment 1", "segment 2", "$\\cdots$", "segment $n$"]
    sw, sg = 2.45, 0.6
    sx = x + (w - (4 * sw + 3 * sg)) / 2
    for k, lab in enumerate(segs):
        pf.pill(ax, sx + k * (sw + sg), y - 0.4, sw, 0.8, lab, fill=EXISTS, size=SIZE)
        if k < 3:
            pf.arrow(ax, (sx + k * (sw + sg) + sw + 0.03, y), (sx + (k + 1) * (sw + sg) - 0.03, y),
                     lw=0.9, head=6)
    pf.text(ax, x + w / 2, y - 0.85, "a restart file every five units of time joins two segments",
            size=6.6, italic=True)
    blocks(ax, x + 1.2, w - 2.4, y - 1.85, [
        ("evolution, refinement, finders, extraction", EXISTS),
        ("wrapper keeps the tracker files of each segment", PORT),
        ("resubmission after a preemption", NEW),
    ])
    y = stage(ax, xa[2], r1y, wa[2], r1h, "Output streams", "appended by every segment")
    blocks(ax, xa[2], wa[2], y, [
        ("trackers: positions and speeds", EXISTS),
        ("horizons: mass, spin, residual", EXISTS),
        ("waves: $r\\psi_4$ modes on the spheres", EXISTS),
        ("history: constraint norms", EXISTS),
        ("restart files: the mesh tree", EXISTS),
        ("found flag of each horizon search", NEW),
    ])
    ym1 = r1y + r1h / 2 + 0.3
    for k in range(2):
        x0 = xa[k] + wa[k]
        pf.arrow(ax, (x0 + 0.03, ym1), (x0 + GAP - 0.03, ym1), lw=1.1, head=7)

    # ---- connector from the first row to the second
    yc = 0.5 * (r1y + r2y + r2h)
    xo = xa[2] + wa[2] / 2
    xr = xb[0] + wb[0] / 2
    pf.line(ax, (xo, r1y), (xo, yc), color=pf.INK, lw=1.1, dashed=False, z=5)
    pf.line(ax, (xo, yc), (xr, yc), color=pf.INK, lw=1.1, dashed=False, z=5)
    pf.arrow(ax, (xr, yc), (xr, r2y + r2h + 0.02), lw=1.1, head=7)
    pf.text(ax, 0.5 * (xo + xr), yc + 0.33,
            "every step is a registered run: manifest, checksums of inputs and outputs, run id",
            size=7.0, italic=True, color=pf.ROSE)

    # ---- second row: readers, analyses with the reference models, note
    y = stage(ax, xb[0], r2y, wb[0], r2h, "Readers", "outside the code")
    blocks(ax, xb[0], wb[0], y, [
        ("segments joined, last row of each time", EXISTS),
        ("failed horizon searches as missed", EXISTS),
        ("wave modes to radiated energy", EXISTS),
        ("members against the barycentre", EXISTS),
        ("trees against the rule model", EXISTS),
    ])
    x, w = xb[1], wb[1]
    y = stage(ax, x, r2y, w, r2h, "Analyses", "measured against the predictions")
    hw = (w - 0.3) / 2
    blocks(ax, x, hw + 0.15, y, [
        ("which member leaves", EXISTS),
        ("energies of the members", EXISTS),
        ("junk and burst energy", NEW),
    ])
    blocks(ax, x + hw - 0.15, hw + 0.15, y, [
        ("captured orbit, closest approach", EXISTS),
        ("horizon masses and drift", EXISTS),
        ("constraint growth", EXISTS),
    ])
    ry = y - 3 * STEP - 0.15
    pf.rbox(ax, x + 0.3, r2y + 0.25, w - 0.6, ry - r2y - 0.25, fill=pf.GREY_FILL,
            edge=pf.CREAM_EDGE, lw=0.9, dashed=True, radius=0.3, z=1)
    pf.text(ax, x + w / 2, ry - 0.35, "reference models from the same start state", size=6.8,
            italic=True)
    pw = (w - 1.2) / 3
    for k, lab in enumerate(("Newtonian", "geodesic", "post-Newtonian")):
        pf.pill(ax, x + 0.45 + k * (pw + 0.15), r2y + 0.45, pw, 0.7, lab, fill=EXISTS,
                size=SIZE)
    y = stage(ax, xb[2], r2y, wb[2], r2h, "Note", "this document")
    blocks(ax, xb[2], wb[2], y, [
        ("one script per figure", EXISTS),
        ("ledger: every number, its run", EXISTS),
        ("journal: prediction first", EXISTS),
    ])
    ym2 = r2y + r2h / 2 + 0.3
    for k in range(2):
        x0 = xb[k] + wb[k]
        pf.arrow(ax, (x0 + 0.03, ym2), (x0 + GAP - 0.03, ym2), lw=1.1, head=7)

    # ---- legend
    pf.panel(ax, W - 15.2, 0.1, 15.0, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((W - 14.6, EXISTS, "exists"), (W - 10.3, PORT, "to be ported"),
                         (W - 4.6, NEW, "new")):
        pf.rbox(ax, x0, 0.3, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.58, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
