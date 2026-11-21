"""Schematic: architecture of the F-hills calculation as of release core-v0.3 (note v1, G1).

States. Exists: in release core-v0.3 (the AthenaK executables named in CLAUDE.md) or in the
track's own reference and analysis code, tested in registered runs. Ported: exists and is
tested elsewhere (a published branch executable of core under scratch/core/exe/, or a
workaround of the track outside the code) and still has to reach a release or the production
set-up. New: still to be written (inside AthenaK by core, decision 0010; or outside it by the
track). Sources of the classification (read 2026-11-20): CLAUDE.md (release core-v0.3);
coord/INTERFACES/multi_puncture.md section 9 (open items: no constraint solve, no automatic
common horizon, one shift damping); scratch/core/exe/*/READY of core_gauge (mass-scaled shift
damping, tested on one and two black holes), core_requests-adf (common horizon of one pair,
test T5), core_clump-curvature (clumps with momentum), core_id-solver-2 (solver inside the
code), core_mpi (two ranks, cards not yet tested); nr_first/README.md (E4 readers, E5 tracker
files truncated on restart and the wrapper that keeps them, requests to core: found flag,
small horizons); PLAN-wave3.md round 1 (a preempted segment that the chain did not resubmit);
newton3/README.md (Jacobi-split energies); geodesic_binary (Schwarzschild, equatorial Kerr;
inclined Kerr open, stage/G1/STATUS.md T2); eih/README.md (first post-Newtonian three bodies,
wave 3a, lead review pending). No data are read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paperfig as pf  # noqa: E402

STEM = "schem_architecture"
EXISTS, PORT, NEW = pf.GREEN_DARK, pf.SLATE, pf.RED
W, H = 33.1, 16.9
CW = 7.55          # column width
GAP = 0.75         # gap between columns
ROWH, ROWS = 0.86, 0.985
TOP = H - 0.25     # top edge of the column panels


def column(ax, x, title, sub, items):
    pf.panel(ax, x, 3.35, CW, TOP - 3.35, radius=0.8)
    pf.text(ax, x + CW / 2, TOP - 0.7, title, size=9.5, bold=True)
    pf.text(ax, x + CW / 2, TOP - 1.3, sub, size=7.3, italic=True)
    y = TOP - 2.25
    for label, state in items:
        pf.block(ax, x + 0.3, y - ROWH / 2, CW - 0.6, ROWH, label, fill=state, size=6.8,
                 radius=0.2)
        y -= ROWS


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    os.makedirs(out, exist_ok=True)
    fig, ax = pf.canvas(W, H, scale=0.24)
    xs = [0.2 + k * (CW + GAP) for k in range(4)]
    column(ax, xs[0], "Initial data", "three black holes at four tidal radii", [
        ("punctures with momentum and spin", EXISTS),
        ("closed-form correction of the data", EXISTS),
        ("Newtonian state from ten tidal radii", EXISTS),
        ("passage input at mass ratio four", EXISTS),
        ("constraint solve inside the code", PORT),
        ("clumps with momentum (object b)", PORT),
        ("start state from a relativistic parabola", NEW),
        ("dressed black holes (object c)", NEW),
    ])
    column(ax, xs[1], "Evolution", "AthenaK on one card, chained", [
        ("moving punctures, Z4c, refinement nests", EXISTS),
        ("a tracker per black hole", EXISTS),
        ("a horizon finder per black hole", EXISTS),
        ("waves on four extraction spheres", EXISTS),
        ("chain of segments with restart files", EXISTS),
        ("wrapper that keeps the tracker files", PORT),
        ("shift damping scaled by the mass", PORT),
        ("common horizon of one pair", PORT),
        ("two cards for the finest resolution", PORT),
        ("resubmission after a preemption", NEW),
        ("found flag of a horizon search", NEW),
    ])
    column(ax, xs[2], "Readers", "the code's output, outside the code", [
        ("trackers merged across segments", EXISTS),
        ("horizons, failed searches as missed", EXISTS),
        ("constraint norms of the history", EXISTS),
        ("wave modes and radiated energy", EXISTS),
        ("member energies, barycentric split", EXISTS),
        ("restart trees against the rule model", EXISTS),
        ("junk energy of three black holes", NEW),
    ])
    column(ax, xs[3], "Reference models", "the same start state, outside the code", [
        ("restricted and full Newtonian problem", EXISTS),
        ("geodesic baseline, Schwarzschild", EXISTS),
        ("geodesic baseline, equatorial Kerr", EXISTS),
        ("first post-Newtonian three bodies", EXISTS),
        ("geodesic baseline, inclined Kerr", NEW),
        ("stripping and heating of clumps", NEW),
    ])
    pf.text(ax, xs[3] + CW / 2, TOP - 2.25 - 6 * ROWS + 0.05, "the post-Newtonian model awaits its review",
            size=6.6, italic=True)
    for k in range(3):
        x0 = xs[k] + CW
        pf.arrow(ax, (x0 + 0.02, 10.0), (x0 + GAP - 0.02, 10.0), lw=1.1, head=7, both=(k == 2))
    labels = ["separation boundary in pericentre", "energy split, fate of the captured member",
              "burst and junk radiation"]
    widths = [8.6, 10.4, 7.0]
    x = 0.6
    for lab, w in zip(labels, widths):
        pf.pill(ax, x, 1.75, w, 0.95, lab, fill=pf.PLUM, size=7.2)
        x += w + 0.55
    pf.arrow(ax, (xs[3] - GAP / 2, 3.35), (xs[3] - GAP / 2, 2.75), lw=1.1, head=7)
    pf.text(ax, 0.6, 0.75, "deliverables of the track", size=7.5, italic=True, ha="left")
    pf.panel(ax, 17.6, 0.27, 14.6, 0.95, radius=0.4, fill=pf.CREAM_LEG)
    for x0, col, lab in ((18.2, EXISTS, "exists"), (22.5, PORT, "to be ported"),
                         (28.2, NEW, "new")):
        pf.rbox(ax, x0, 0.47, 1.3, 0.55, fill=col, edge="none", radius=0.12, z=3)
        pf.text(ax, x0 + 1.7, 0.75, lab, size=7.5, bold=True, ha="left")
    pf.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
