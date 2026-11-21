#!/usr/bin/env python3
"""Architecture of core (exists / built in wave 1 / to be built) and its gate timeline,
for stage check C13. Style: /sleep-paper-figure-style (paperfig.py, copied here).

Content sources: CLAUDE.md "What exists"; tracks/core/CHANGELOG.md (core-v0.3);
tracks/core/STATUS.md "next" and stage/G2/OPEN.md (to be built); git tags core-v0.1,
v0.2, v0.3; coord/CHARTER.md (gates G0-G4).

    python3 schem_architecture.py [--out tracks/core/verify/figs/schem_architecture]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paperfig as pf  # noqa: E402

EXISTS = ["Z4c, AMR, horizon finder\n(AthenaK upstream)", "pushers: midpoint,\nspacetime Boris",
          "metric at particles\n(Catmull-Rom, spline)", "deposit CIC/TSC/PCS,\nfilter, refinement",
          "coupling to Z4c (tmunu),\nexcision, restart",
          "periodic domain,\ncosmological lapse"]
WAVE1 = ["counter-based\nrandom numbers", "Monte Carlo\ncollisions", "scalar field,\nstochastic sources",
         "spherical data with\nextrinsic curvature", "Bowen-York\npunctures", "Newtonian\nreference mode"]
TODO = ["lapse condition against\nthe surface front (A, D)", "mass-scaled shift\ndamping (F)",
        "collision pair-energy\ncorrection (C)", "initial slice at N* (E)",
        "elliptic initial data\non the mesh (0010)", "oblate spheroid data\n(ladder row 3)"]
TRACKS = [("A", "PBHs, early matter era"), ("B", "GWs, early matter era"),
          ("C", "SIDM core collapse"), ("D", "BH dress"), ("E", "stochastic inflation"),
          ("F", "Hills mechanism")]


def column(ax, x, y_top, w, title, items, fill, tcolor=pf.WHITE, h=1.25, gap=0.3):
    pf.text(ax, x + w / 2, y_top + 0.55, title, size=11.5, bold=True)
    y = y_top - h
    boxes = []
    for it in items:
        pf.block(ax, x, y, w, h, it, fill=fill, tcolor=tcolor, size=9.6, radius=0.2)
        boxes.append((x, y, w, h))
        y -= h + gap
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "figs", "schem_architecture"))
    a = ap.parse_args()
    fig, ax = pf.canvas(44, 21.5)

    # ---- gate timeline (top)
    pf.rose_panel(ax, 0.6, 15.3, 42.8, 5.7)
    pf.text(ax, 31.5, 20.3, "Gates of core and releases (state 2026-11-15)", size=12.5)
    pf.timeline(ax, 2.0, 41.5, 17.6)
    gx = [4.0, 11.0, 20.5, 29.5, 37.5]
    gl = ["G0 scoping", "G1 interfaces", "G2 verified capability", "G3 science runs", "G4 paper"]
    for x, l, done in zip(gx, gl, (True, True, False, False, False)):
        pf.rbox(ax, x - 0.32, 17.28, 0.64, 0.64, fill=pf.GREEN_DARK if done else pf.WHITE,
                edge=pf.GREEN_DARK, radius=0.32, z=4)
        pf.text(ax, x, 16.6, l, size=10, bold=True)
    pf.brace(ax, 2.6, 13.0, 18.15, "passed (interfaces accepted, decision 0011)", below=False,
             size=10)
    pf.brace(ax, 14.0, 26.5, 18.15, "open: ladder rows 3-4, figures, verifier report", below=False,
             size=10)
    for x, tag in ((7.5, "core-v0.1"), (14.6, "core-v0.2"), (16.6, "core-v0.3")):
        pf.arrow(ax, (x, 16.1), (x, 17.3), color=pf.RED, lw=1.0, head=8)
        pf.text(ax, x, 15.8, tag, size=9, color=pf.RED, bold=True)
    pf.text(ax, 33.5, 18.8, "wave-2 source items  ->  core-v0.4", size=10, italic=True)

    # ---- architecture (bottom)
    pf.legend_box(ax, 6.0, 13.75, 32.0, 1.1,
                  [("block:" + pf.GREEN_DARK, "exists, verified (v0.1, v0.2)"),
                   ("block:" + pf.SLATE, "built in wave 1 (v0.3, G2 open)"),
                   ("block:" + pf.RED, "to be built (wave 2)")], size=9.2)
    pf.panel(ax, 0.6, 0.6, 31.0, 12.7, radius=1.0)
    pf.text(ax, 16.1, 12.75, "AthenaK of this repository (one code base, decision 0010)",
            size=10.5, italic=True)
    w = 9.2
    b1 = column(ax, 1.3, 11.3, w, "exists", EXISTS, pf.GREEN_DARK)
    b2 = column(ax, 11.4, 11.3, w, "wave 1 (core-v0.3)", WAVE1, pf.SLATE)
    b3 = column(ax, 21.5, 11.3, w, "to be built", TODO, pf.RED)
    pf.arrow(ax, (10.5, 6.5), (11.4, 6.5), lw=1.3)
    pf.arrow(ax, (20.6, 6.5), (21.5, 6.5), lw=1.3, dashed=True, color=pf.GREY_LINE)
    # consumers
    pf.text(ax, 37.6, 12.75, "tracks (users)", size=10.5, bold=True)
    for i, (tid, lab) in enumerate(TRACKS):
        y = 11.2 - i * 1.75
        pf.pill(ax, 33.2, y, 8.9, 1.2, f"{tid}  {lab}", fill=pf.GREEN_MID, size=10)
    pf.arrow(ax, (31.6, 6.5), (33.1, 6.5), lw=1.3)
    pf.text(ax, 37.6, 0.95, "a track specifies, supplies reference\nsolutions and checks; core builds",
            size=9.5, italic=True)
    pf.save(fig, os.path.abspath(a.out))
    print("font:", pf.FONT, "->", os.path.abspath(a.out) + ".png")


if __name__ == "__main__":
    main()
