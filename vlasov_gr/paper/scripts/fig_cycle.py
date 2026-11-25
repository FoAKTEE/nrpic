#!/usr/bin/env python3
"""Schematic diagram of one coupled multi-rate general-relativistic kinetic cycle."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG_OUT = HERE.parent / "figures" / "fig_cycle"

FIG_W = 4.00
FIG_H = 3.75
TITLE_PT = 8.4
SUB_PT = 6.9
LABEL_PT = 6.7
INK = "0.15"


def tint(color: str, f: float):
    c = to_rgb(color)
    return tuple(1.0 - f * (1.0 - x) for x in c)


class Box:
    def __init__(self, ax, xy, w, h, title, sub, color, dashed=False):
        self.x, self.y, self.w, self.h = xy[0], xy[1], w, h
        ax.add_patch(
            FancyBboxPatch(
                (self.x - w / 2.0, self.y - h / 2.0),
                w,
                h,
                boxstyle="round,pad=0,rounding_size=0.07",
                fc=tint(color, 0.11),
                ec=color,
                lw=1.05,
                ls="--" if dashed else "-",
                zorder=2,
            )
        )
        if sub:
            ax.text(self.x, self.y + 0.11, title, ha="center", va="center",
                    color=color, fontsize=TITLE_PT, weight="bold", zorder=3)
            ax.text(self.x, self.y - 0.105, sub, ha="center", va="center",
                    color=INK, fontsize=SUB_PT, linespacing=1.16, zorder=3)
        else:
            ax.text(self.x, self.y, title, ha="center", va="center",
                    color=color, fontsize=TITLE_PT, weight="bold", zorder=3)

    def edge(self, side: str, f: float = 0.0):
        if side == "top":
            return (self.x + f * self.w / 2.0, self.y + self.h / 2.0)
        if side == "bottom":
            return (self.x + f * self.w / 2.0, self.y - self.h / 2.0)
        if side == "left":
            return (self.x - self.w / 2.0, self.y + f * self.h / 2.0)
        return (self.x + self.w / 2.0, self.y + f * self.h / 2.0)


def arrow(ax, a, b, rad=0.0, dashed=False, color=INK):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=4.8,head_width=2.5",
            lw=1.0,
            color=color,
            ls="--" if dashed else "-",
            shrinkA=1.8,
            shrinkB=1.8,
            zorder=1,
        )
    )


def make():
    cz.use_style()
    blue = cz.PAL["blue"]
    red = cz.PAL["red"]
    green = cz.PAL["green"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0.0, FIG_W)
    ax.set_ylim(0.0, FIG_H)
    ax.set_aspect("equal")
    ax.axis("off")

    cx = 0.5 * FIG_W
    bw, bh = 1.44, 0.62

    S = Box(ax, (cx, 3.29), 1.92, 0.58,
            "Spacetime advance", "Z4c (SSP-RK3 / RK4),\ncausal $(d_0, d_1)$ stages", blue)
    R = Box(ax, (3.19, 2.13), bw, bh,
            "Metric reconstruction", r"3-level $\mathcal{O}(\Delta t^3)$ time," "\n" r"$C^2$ quintic Hermite", blue)
    P = Box(ax, (3.19, 0.64), bw, bh,
            "Kinetic step", r"GL4 ($\varepsilon\in\{0,1\}$), Cell-BGK," "\n" "or AP finite volume", red)
    X = Box(ax, (0.81, 0.64), bw, bh,
            "Excision & blocks", "Lapse / horizon check,\nblock ownership", red)
    D = Box(ax, (0.81, 2.13), bw, bh,
            "Deposition & filter", "AMR B-spline, harmonic\nflux filter + reflux", green)
    G = Box(ax, (cx, 1.38), 1.24, 0.48,
            "AMR regrid", r"Monitor $q_{\rm AMR}=\alpha\chi^{-7/4}$", blue, dashed=True)

    # Main clockwise cycle
    arrow(ax, S.edge("right"), R.edge("top", 0.20), rad=-0.26)
    arrow(ax, R.edge("bottom", 0.0), P.edge("top", 0.0), rad=0.0)
    arrow(ax, P.edge("left"), X.edge("right"), rad=0.0)
    arrow(ax, X.edge("top", 0.0), D.edge("bottom", 0.0), rad=0.0)
    arrow(ax, D.edge("top", -0.20), S.edge("left"), rad=-0.26)

    # Clean AMR regrid side branch well separated from corners
    arrow(ax, D.edge("bottom", 0.35), G.edge("left", 0.0), rad=0.22, dashed=True, color=blue)
    arrow(ax, G.edge("top", 0.0), S.edge("bottom", 0.0), rad=0.0, dashed=True, color=blue)

    # Mask behind G->S midpoint label inside open channel [1.53, 2.47]
    ax.add_patch(Rectangle((cx - 0.42, 2.18), 0.84, 0.28, fc="white", ec="none", alpha=0.96, zorder=3))
    ax.text(cx, 2.32, "Rebuilt blocks\n& sources", ha="center", va="center",
            fontsize=6.3, color=blue, linespacing=1.14, zorder=4)

    # Outer annotations
    ax.text(3.93, 3.12, r"$\alpha,\,\beta^i,\,\gamma_{ij}$" "\n" r"at $t^{n-1},t^n,t^{n+1}$",
            ha="right", va="center", fontsize=LABEL_PT, color=INK, linespacing=1.15)
    ax.text(3.26, 1.38, "Stage metrics &\n" r"$\partial_i(\alpha,\beta^j,\gamma_{kl})$",
            ha="left", va="center", fontsize=LABEL_PT, color=INK, linespacing=1.15)
    ax.text(cx, 0.16, r"$(x_p^i,\,u_{i,p})$ or basis moments",
            ha="center", va="center", fontsize=LABEL_PT, color=INK)
    ax.text(0.74, 1.38, "Surviving\npackets",
            ha="right", va="center", fontsize=LABEL_PT, color=INK, linespacing=1.15)
    ax.text(0.07, 3.12, r"$(d_0,\,d_1)$ for" "\n" r"$(E,\,S_i,\,S_{ij})$",
            ha="left", va="center", fontsize=LABEL_PT, color=INK, linespacing=1.15)

    return fig


if __name__ == "__main__":
    fig = make()
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    print(f"Saved {FIG_OUT}.{{pdf,png}}")
