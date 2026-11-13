"""How the code was assembled: the hypergraph of the decomposition.

Nodes (rows) are the capabilities taken from existing codes and published methods,
grouped by origin; each component built here is a hyperedge (column) that joins the
capabilities it combines. Two components built here are themselves members of others
(the coupled cycle and the adaptive mesh), so they appear as red rows at the bottom.
Node and edge lists follow the method notes, section "How the code was assembled".

    python3 paper/scripts/fig_hypergraph.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

import figstyle as fs

OUT = HERE.parent / "figures" / "fig_hypergraph"
PT = 9

# origin groups and their capabilities (node numbers as in the method notes)
GROUPS = [
    ("AthenaK", [
        (1, "octree mesh and refinement"),
        (2, "Z4c, moving-puncture gauge"),
        (3, "particle container"),
        (4, "matter-source coupling"),
        (5, "apparent-horizon finder")]),
    ("Kokkos", [
        (6, "performance portability")]),
    ("plasma\nparticle-in-cell", [
        (7, "implicit midpoint push"),
        (8, "Boris rotation"),
        (10, "cloud-in-cell, binomial filter"),
        (11, "single-level deposition (WarpX)")]),
    ("relativity and\nmesh methods", [
        (9, "tetrad form of gravity"),
        (13, "lapse excision"),
        (14, "parabolic constraint relaxation"),
        (12, u"Löhner refinement indicator")]),
    ("published\nreferences", [
        (16, "NRPIC method paper (text)"),
        (15, "exact reference solutions")]),
    ("built here", [
        ("A", "geodesic pushers"),
        ("C", "level-capped deposition")]),
]

# components built here (hyperedges), left to right, with their members
EDGES = [
    ("A", "geodesic pushers", [7, 8, 9, 16, 6]),
    ("B", "metric reconstruction", [1, 16, 6]),
    ("C", "level-capped deposition", [10, 11, 1, 3, 16, 6]),
    ("E", "adaptive mesh", [1, 12, 3, "C"]),
    ("F", "excision, apparent horizons", [13, 5]),
    ("G", "constraint control", [2, 14, 10]),
    ("H", "initial data, validation", [15, 16]),
    ("D", "coupled cycle", [2, 4, "A", "C", 16]),
]
ANGLE = 30.0


def tint(color, f):
    c = to_rgb(color)
    return tuple(1 - f * (1 - x) for x in c)


def make():
    fs.use_style()
    blue, red = fs.PAL["blue"], fs.PAL["red"]
    pitch, gap, head, foot = 0.19, 0.085, 1.25, 0.08
    nrows = sum(len(items) for _, items in GROUPS)
    W = fs.FULL_WIDTH
    H = head + (nrows - 1) * pitch + (len(GROUPS) - 1) * gap + foot + 0.10
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    top = H - head
    x_group, x_label, dx = 0.05, 3.10, 0.55
    x_last = 7.17
    xs = [x_last - dx * (len(EDGES) - 1 - j) for j in range(len(EDGES))]

    # rows: capabilities grouped by origin, then the components reused by others
    row_y, y = {}, top
    for gname, items in GROUPS:
        col = red if gname == "built here" else blue
        # origin label, its first line level with the group's first row
        for k, line in enumerate(gname.split("\n")):
            ax.text(x_group, y - k * 0.15, line, ha="left", va="center", fontsize=PT,
                    color=col)
        for key, text in items:
            row_y[key] = y
            ax.text(x_label, y, text, ha="right", va="center", fontsize=PT, color="0.1")
            ax.plot([x_label + 0.08, x_last + 0.16], [y, y], color="0.86", lw=0.6,
                    zorder=0)
            y -= pitch
        y -= gap

    # hyperedges: one column per component, joining its members
    y_head = top + 0.22
    for x, (key, name, members) in zip(xs, EDGES):
        ys = [row_y[m] for m in members]
        ax.plot([x, x], [max(ys), y_head], color=tint(red, 0.45), lw=0.8, zorder=1)
        ax.plot([x, x], [min(ys), max(ys)], color=red, lw=1.6, zorder=2,
                solid_capstyle="round")
        for m, yy in zip(members, ys):
            c = red if isinstance(m, str) else blue
            ax.plot(x, yy, "o", ms=5.6, mew=0, color=c, zorder=3)
        ax.text(x - 0.04, y_head + 0.03, name, ha="left", va="bottom", fontsize=PT,
                color=red, rotation=ANGLE, rotation_mode="anchor")
    # what the two axes are
    ax.text(x_label, y_head + 0.02, "existing capability", ha="right", va="bottom",
            fontsize=PT, color=blue)
    ax.text(x_label, y_head + 0.24, "component built here", ha="right", va="bottom",
            fontsize=PT, color=red)
    ax.text(x_group, y_head + 0.02, "origin", ha="left", va="bottom", fontsize=PT,
            color=blue)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
