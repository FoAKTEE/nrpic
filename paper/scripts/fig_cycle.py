"""The particle-mesh cycle: five stages on a closed loop, each arrow labelled by what it
passes, with the regrid as a side branch. Blue stages act on the mesh, red stages on the
macroparticles.

    python3 paper/scripts/fig_cycle.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import figstyle as fs

OUT = HERE.parent / "figures" / "fig_cycle"
FIG_H = 3.55
TITLE_PT, SUB_PT, LABEL_PT = 10, 9, 9
INK = "0.15"


def tint(color, f):
    """Mix a colour with white: f = 0 white, f = 1 the colour."""
    c = to_rgb(color)
    return tuple(1 - f * (1 - x) for x in c)


class Box:
    def __init__(self, ax, xy, w, h, title, sub, color, dashed=False):
        self.x, self.y, self.w, self.h = xy[0], xy[1], w, h
        ax.add_patch(FancyBboxPatch((self.x - w / 2, self.y - h / 2), w, h,
                                    boxstyle="round,pad=0,rounding_size=0.07",
                                    fc=tint(color, 0.10), ec=color, lw=1.0,
                                    ls="--" if dashed else "-", zorder=2))
        dy = 0.11 if sub else 0.0
        ax.text(self.x, self.y + dy, title, ha="center", va="center", color=color,
                fontsize=TITLE_PT, zorder=3)
        if sub:
            ax.text(self.x, self.y - 0.12, sub, ha="center", va="center", color=INK,
                    fontsize=SUB_PT, zorder=3)

    def edge(self, side, f=0.0):
        """Point on the box edge; f in [-1, 1] slides along the side."""
        if side == "top":
            return (self.x + f * self.w / 2, self.y + self.h / 2)
        if side == "bottom":
            return (self.x + f * self.w / 2, self.y - self.h / 2)
        if side == "left":
            return (self.x - self.w / 2, self.y + f * self.h / 2)
        return (self.x + self.w / 2, self.y + f * self.h / 2)


def arrow(ax, a, b, rad=0.0, dashed=False, color=INK):
    ax.add_patch(FancyArrowPatch(a, b, connectionstyle=f"arc3,rad={rad}",
                                 arrowstyle="-|>,head_length=5,head_width=2.6",
                                 lw=1.0, color=color, ls="--" if dashed else "-",
                                 shrinkA=1.5, shrinkB=1.5, zorder=1))


def label(ax, xy, text, ha="center", va="center", color=INK):
    ax.text(xy[0], xy[1], text, ha=ha, va=va, fontsize=LABEL_PT, color=color,
            linespacing=1.25)


def make():
    fs.use_style()
    blue, red = fs.PAL["blue"], fs.PAL["red"]
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, FIG_H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, fs.COLUMN_WIDTH)
    ax.set_ylim(0, FIG_H)
    ax.set_aspect("equal")
    ax.axis("off")

    W, H = 1.62, 0.52
    S = Box(ax, (2.0, 3.10), W, H, "Spacetime advance", "Z4c, four RK stages", blue)
    R = Box(ax, (3.13, 2.05), W, H, "Reconstruction", "cubic Hermite", blue)
    P = Box(ax, (3.08, 0.55), W, 0.66, "Geodesic push",
            "implicit midpoint or\nspacetime Boris", red)
    X = Box(ax, (0.92, 0.55), W, 0.66, "Excision", "lapse threshold,\nblock ownership", red)
    D = Box(ax, (0.87, 2.05), W, H, "Deposition", "cloud-in-cell, filter", red)
    G = Box(ax, (2.06, 1.30), 1.30, 0.50, "Regrid", r"indicator of $\alpha\chi^{-7/4}$", blue,
            dashed=True)

    # main loop, clockwise
    arrow(ax, S.edge("right"), R.edge("top", 0.25), rad=-0.30)
    arrow(ax, R.edge("bottom", -0.25), P.edge("top", -0.20), rad=-0.12)
    arrow(ax, P.edge("left"), X.edge("right"), rad=0.0)
    arrow(ax, X.edge("top", 0.20), D.edge("bottom", 0.25), rad=-0.12)
    arrow(ax, D.edge("top", -0.25), S.edge("left"), rad=-0.30)
    # side branch: regrid between deposition and the next advance
    arrow(ax, D.edge("bottom", 0.78), G.edge("left", 0.0), rad=0.45, dashed=True, color=blue)
    arrow(ax, G.edge("top", -0.09), S.edge("bottom", 0.0), rad=0.0, dashed=True, color=blue)

    # what each arrow passes
    label(ax, (3.95, 2.92), r"$\alpha,\ \beta^i,\ \gamma_{ij}$" "\n" r"at $t^n,\ t^{n+1}$",
          ha="right")
    label(ax, (3.95, 1.32), r"$\bar\alpha,\ \bar\beta^i,\ \bar\gamma_{ij}$" "\nand gradients",
          ha="right")
    label(ax, (2.0, 0.75), r"$x_p^i,\ u_{i,p}$")
    label(ax, (0.05, 1.32), "surviving\nparticles", ha="left")
    label(ax, (0.05, 2.92), r"$E,\ S_i,\ S_{ij}$", ha="left")
    label(ax, (2.07, 2.55), "new mesh", ha="left", color=blue)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
