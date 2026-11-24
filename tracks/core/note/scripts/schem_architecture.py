#!/usr/bin/env python3
"""Architecture of the shared implementation by release (core-v0.1 to core-v0.6, and
what is open for core-v0.7), with the gate timeline of core. State 2026-11-21.
Style: paperfig.py (copied unchanged from harness/style/).

Content sources: CLAUDE.md "What exists"; tracks/core/CHANGELOG.md sections core-v0.3
to core-v0.6 ("What is merged"); tracks/core/interfaces/REQUESTS_WAVE3.md sections 5,
5a, 5b (W22, W24, W26, W27, W30, W31); tracks/core/stage/G2/OPEN.md (items u, v); git
tags core-v0.1 to core-v0.6; coord/CHARTER.md (gates G0-G4).

    schem_architecture.py OUTDIR   (writes OUTDIR/figures/schem_architecture.{png,svg})
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paperfig as pf  # noqa: E402

COLS = [
    ("v0.1, v0.2: base", pf.GREEN_DARK, [
        "Z4c, refinement,\nhorizon finder (upstream)", "midpoint and\nspacetime Boris pushers",
        "metric at the particles\n(Catmull-Rom, spline)", "cloud deposit, filter,\nacross levels",
        "coupling to Z4c,\nexcision, restart", "periodic domain,\nconformal-time lapse"]),
    ("v0.3: wave 1", pf.SLATE, [
        "counter-based\nrandom numbers", "Monte Carlo\ncollisions", "scalar field,\nstochastic sources",
        "spherical data with\nextrinsic curvature", "Bowen-York\npunctures", "Newtonian mode\n(multigrid)"]),
    ("v0.4: wave 2", pf.SLATE, [
        "linear waves, double-\nprecision mesh output", "lapse relaxation,\nshift damping",
        "initial slice of\nstochastic inflation", "clumps with momentum\nand spin",
        "elliptic initial data\non the mesh", "tracers, accretion,\nexternal point mass"]),
    ("v0.5, v0.6: wave 3", pf.SLATE, [
        "threaded build,\nseveral MPI ranks", "adaptive refinement\nin the periodic box",
        "guard, light-speed step,\nregion norms", "Fourier Poisson solver\n(Newtonian mode)",
        "outer faces of Z4c\n(fall-off, radiative)", "solver: far field,\nrefinement, punctures"]),
    ("open (v0.7 and later)", pf.RED, [
        "lapse relaxation away\nfrom a hole (mitigation)", "step limit with the\ngauge speeds",
        "exact restart of the\nrefined mesh state", "oblate spheroid data\n(ladder row 3)",
        "clumps from tables\nwith momentum", "collisions on\nseveral ranks"]),
]
TRACKS = [("A", "PBHs, early matter era"), ("B", "GWs, early matter era"),
          ("C", "SIDM core collapse"), ("D", "BH dress"), ("E", "stochastic inflation"),
          ("F", "Hills mechanism")]


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(os.path.join(outdir, "figures"), exist_ok=True)
    W, H = 52.0, 23.5
    fig, ax = pf.canvas(W, H, scale=0.135)   # 7.0 in wide: sizes in pt are final

    # gate timeline and releases (top)
    pf.rose_panel(ax, 0.6, 16.6, W - 1.2, 6.3)
    pf.text(ax, W / 2, 22.3, "Gates of core and releases (state 2026-11-21)", size=8.5)
    pf.timeline(ax, 2.0, W - 2.0, 18.9)
    gx = [5.0, 12.0, 28.0, 38.5, 47.0]
    gl = ["G0 scoping", "G1 interfaces", "G2 verified capability", "G3 science runs", "G4 paper"]
    for x, l, done in zip(gx, gl, (True, True, False, False, False)):
        pf.rbox(ax, x - 0.32, 18.58, 0.64, 0.64, fill=pf.GREEN_DARK if done else pf.WHITE,
                edge=pf.GREEN_DARK, radius=0.32, z=4)
        pf.text(ax, x, 17.9, l, size=7, bold=True)
    pf.brace(ax, 3.0, 14.0, 19.45, "passed", below=False, size=7)
    pf.brace(ax, 24.0, 33.0, 19.45, "open: ladder rows 3, 4; three-way convergence", below=False,
             size=7)
    for x, tag in ((8.5, "v0.1"), (15.5, "v0.2"), (17.2, "v0.3"), (19.6, "v0.4"),
                   (21.3, "v0.5"), (23.0, "v0.6")):
        pf.arrow(ax, (x, 17.4), (x, 18.6), color=pf.RED, lw=1.0, head=8)
        pf.text(ax, x, 17.0, tag, size=6.5, color=pf.RED, bold=True)

    # architecture by release (bottom)
    for lx, fill, lab in ((4.0, pf.GREEN_DARK, "base, verified on the ladder (rows 1, 2)"),
                          (19.0, pf.SLATE, "released, tested by its package"),
                          (32.0, pf.RED, "open")):
        pf.block(ax, lx, 15.25, 1.2, 0.75, "", fill=fill, radius=0.12)
        pf.text(ax, lx + 1.6, 15.62, lab, size=7, ha="left")
    pf.panel(ax, 0.6, 0.6, 41.2, 14.0, radius=1.0)
    pf.text(ax, 21.2, 14.05, "AthenaK of this repository (one code base)", size=7.5, italic=True)
    w, gap, x0 = 7.6, 0.5, 1.2
    for i, (title, fill, items) in enumerate(COLS):
        x = x0 + i * (w + gap)
        pf.text(ax, x + w / 2, 13.25, title, size=7.5, bold=True)
        y = 12.55
        for it in items:
            h = 1.62
            y -= h
            pf.block(ax, x, y, w, h, it, fill=fill, tcolor=pf.WHITE, size=6.3, radius=0.2)
            y -= 0.26
        if i < len(COLS) - 1:
            pf.arrow(ax, (x + w + 0.02, 7.2), (x + w + gap - 0.02, 7.2), lw=1.1,
                     dashed=(i == len(COLS) - 2), color=pf.INK if i < len(COLS) - 2 else pf.GREY_LINE)
    pf.text(ax, 46.9, 14.05, "tracks (users)", size=7.5, bold=True)
    for i, (tid, lab) in enumerate(TRACKS):
        y = 12.3 - i * 1.85
        pf.pill(ax, 42.6, y, 8.7, 1.25, f"{tid}  {lab}", fill=pf.GREEN_MID, size=6.8)
    pf.arrow(ax, (41.8, 7.2), (42.5, 7.2), lw=1.3)
    pf.text(ax, 46.9, 1.4, "a track specifies, supplies\nreferences and checks;\ncore builds",
            size=6.5, italic=True)
    stem = os.path.join(outdir, "figures", "schem_architecture")
    pf.save(fig, stem)
    print("font:", pf.FONT, "->", stem + ".png")


if __name__ == "__main__":
    main()
