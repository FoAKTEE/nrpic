#!/usr/bin/env python3
"""Schematic diagram of one coupled multi-rate general-relativistic kinetic cycle.

Generates `vlasov_gr/paper/figures/fig_cycle.{pdf,png}` in publication style.
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_cycle")

FIG_W = 4.65
FIG_H = 4.25
TITLE_PT = 9.0
SUB_PT = 7.4
LABEL_PT = 7.2
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
                boxstyle="round,pad=0,rounding_size=0.08",
                fc=tint(color, 0.11),
                ec=color,
                lw=1.1,
                ls="--" if dashed else "-",
                zorder=2,
            )
        )
        if sub:
            ax.text(self.x, self.y + 0.125, title, ha="center", va="center",
                    color=color, fontsize=TITLE_PT, weight="bold", zorder=3)
            ax.text(self.x, self.y - 0.115, sub, ha="center", va="center",
                    color=INK, fontsize=SUB_PT, linespacing=1.18, zorder=3)
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
            arrowstyle="-|>,head_length=5.2,head_width=2.7",
            lw=1.05,
            color=color,
            ls="--" if dashed else "-",
            shrinkA=1.8,
            shrinkB=1.8,
            zorder=1,
        )
    )


def label(ax, xy, text, ha="center", va="center", color=INK, halo=False):
    kw = {}
    if halo:
        kw["bbox"] = dict(boxstyle="square,pad=0.14", fc="white", ec="none", alpha=0.92)
    ax.text(
        xy[0],
        xy[1],
        text,
        ha=ha,
        va=va,
        fontsize=LABEL_PT,
        color=color,
        linespacing=1.18,
        zorder=4,
        **kw,
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
    bw, bh_tall = 1.82, 0.68

    S = Box(ax, (cx, 3.74), 2.15, 0.64,
            "Spacetime advance", "Z4c (SSP-RK3 / RK4),\ncausal $(d_0, d_1)$ stages", blue)
    R = Box(ax, (3.62, 2.40), bw, bh_tall,
            "Metric reconstruction", r"3-level $\mathcal{O}(\Delta t^3)$ time," "\n" r"$C^2$ quintic Hermite", blue)
    P = Box(ax, (3.62, 0.72), bw, bh_tall,
            "Kinetic step", r"GL4 ($\varepsilon\in\{0,1\}$), Cell-BGK," "\n" r"or AP finite volume", red)
    X = Box(ax, (1.03, 0.72), bw, bh_tall,
            "Excision & blocks", "Lapse / horizon check,\nblock ownership", red)
    D = Box(ax, (1.03, 2.40), bw, bh_tall,
            "Deposition & filter", "AMR B-spline, harmonic\nflux filter + reflux", green)
    G = Box(ax, (cx, 1.62), 1.48, 0.54,
            "AMR regrid", r"Monitor $q_{\rm AMR}=\alpha\chi^{-7/4}$", blue, dashed=True)

    # Main clockwise cycle
    arrow(ax, S.edge("right"), R.edge("top", 0.25), rad=-0.26)
    arrow(ax, R.edge("bottom", 0.0), P.edge("top", 0.0), rad=0.0)
    arrow(ax, P.edge("left"), X.edge("right"), rad=0.0)
    arrow(ax, X.edge("top", 0.0), D.edge("bottom", 0.0), rad=0.0)
    arrow(ax, D.edge("top", -0.25), S.edge("left"), rad=-0.26)

    # Side branch: AMR regrid between deposit and spacetime advance
    arrow(ax, D.edge("bottom", 0.62), G.edge("left", -0.10), rad=0.22, dashed=True, color=blue)
    arrow(ax, G.edge("top", 0.0), S.edge("bottom", 0.0), rad=0.0, dashed=True, color=blue)

    # Arrow data annotations kept completely clear of boxes and lines
    label(ax, (4.58, 3.55), r"$\alpha,\,\beta^i,\,\gamma_{ij}$" "\n" r"at $t^{n-1},t^n,t^{n+1}$", ha="right")
    label(ax, (3.72, 1.56), r"Stage metrics &" "\n" r"$\partial_i(\alpha,\beta^j,\gamma_{kl})$", ha="left")
    label(ax, (cx, 0.20), r"$(x_p^i,\,u_{i,p})$ or basis moments", ha="center")
    label(ax, (0.93, 1.56), "Surviving\npackets", ha="right")
    label(ax, (0.07, 3.55), r"$(d_0,\,d_1)$ for" "\n" r"$(E,\,S_i,\,S_{ij})$", ha="left")
    label(ax, (cx, 2.55), "Rebuilt blocks\n& sources", ha="center", color=blue, halo=True)

    return fig


if __name__ == "__main__":
    fig = make()
    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    print(f"Saved {FIG_OUT}.{{pdf,png}}")
