"""
paperfig.py — architecture/workflow figure style extracted from
Behrouz, Hashemi, Javanmard, Mirrokni (2026), "Language Models Need Sleep"
(arXiv:2606.03979), figures Sleep-states / Consolidation / selected_params2 / frequency2.

Pure matplotlib. Coordinates are data units on an axis with equal aspect
and no frame; y grows upward (so "stacks" are drawn bottom -> top).

Usage:
    import paperfig as pf
    fig, ax = pf.canvas(28, 10)          # width, height in data units
    pf.pill(ax, 2, 8, 8, 1.4, "Low Frequency FFN", pf.GREEN_LIGHT)
    pf.arrow(ax, (6, 7.0), (6, 8.0))
    pf.save(fig, "out/figure")           # writes out/figure.png (+ .svg)
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Circle, Rectangle
from matplotlib import font_manager

# ------------------------------------------------------------------ palette
# Sampled from the paper's PNGs; names follow the LaTeX \definecolor's in main.tex
GREEN_DARK  = "#6C7869"   # c7 / mydarkgreen : primary structural block, arrows, tokens
GREEN_MID   = "#919A8F"   # tint of GREEN_DARK: second level
GREEN_LIGHT = "#B5BBB4"   # tint of GREEN_DARK: third (slowest/outermost) level
SLATE       = "#76768D"   # ~mydarkpurple (65657E): the "core" computation block
RED         = "#9B5353"   # c5 / mydarkred : projections, routers, emphasis bar
RED_SHADOW  = "#CFADAD"   # offset shadow copy of RED trapezoids
PLUM        = "#7B576F"   # ~c3: experts / active parameters
PLUM_DARK   = "#6C445F"
PLUM_LIGHT  = "#9F8496"
LAVENDER    = "#D9CFD6"   # fill for hatched (inactive) parameters
OLIVE       = "#8A8463"   # second callout bar colour
ROSE        = "#B57F7F"   # timeline labels
ROSE_LINE   = "#C9A8A8"   # pink dashed panel border / braces
CREAM       = "#FFF9E5"   # panel fill (LaTeX myblue = FDF5E0)
CREAM_EDGE  = "#C6C5CB"   # dashed border of cream panels
CREAM_LEG   = "#F5EFDE"   # legend box fill
GREY_FILL   = "#EDECE6"   # LaTeX mygray : callout fill / title bands
GREY_BAND   = "#E2E0DC"
GREY_LINE   = "#AEAEAE"   # inactive dashed arrows
INK         = "#1F1F1F"   # text and active arrows
WHITE       = "#FFFFFF"

# ------------------------------------------------------------------ typography
_PREFERRED = ["Linux Libertine O", "Libertinus Serif", "Liberation Serif", "DejaVu Serif"]
_available = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in _PREFERRED if f in _available), "serif")
plt.rcParams.update({
    "font.family": FONT,
    "mathtext.fontset": "stix",     # serif math, close to newtxmath/libertine
    "text.color": INK,
    "axes.edgecolor": INK,
})

def canvas(width: float, height: float, scale: float = 0.5):
    """Create a frameless equal-aspect axis spanning [0,width]x[0,height] data units."""
    fig = plt.figure(figsize=(width * scale, height * scale))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    return fig, ax

def save(fig, stem: str, dpi: int = 300, svg: bool = True):
    fig.savefig(stem + ".png", dpi=dpi, facecolor=WHITE)
    if svg:
        fig.savefig(stem + ".svg", facecolor=WHITE)
    plt.close(fig)

# ------------------------------------------------------------------ primitives
def text(ax, x, y, s, size=11, color=INK, bold=False, italic=False, ha="center", va="center", rot=0, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, rotation=rot,
                   fontweight="bold" if bold else "normal",
                   fontstyle="italic" if italic else "normal", zorder=6, **kw)

def rbox(ax, x, y, w, h, fill=CREAM, edge=CREAM_EDGE, lw=1.0, dashed=False, radius=0.5, z=1, alpha=1.0):
    """Rounded rectangle. radius in data units. dashed -> the paper's container panels."""
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                       fc=fill, ec=edge, lw=lw, zorder=z, alpha=alpha,
                       linestyle=(0, (4, 2.5)) if dashed else "solid")
    ax.add_patch(p)
    return p

def panel(ax, x, y, w, h, radius=1.2, fill=CREAM, edge=CREAM_EDGE, z=0):
    """Cream dashed container panel (Consolidation / frequency2 style)."""
    return rbox(ax, x, y, w, h, fill=fill, edge=edge, lw=1.1, dashed=True, radius=radius, z=z)

def rose_panel(ax, x, y, w, h, radius=1.2, z=0):
    """White panel with pink dashed border (Sleep-states top row)."""
    return rbox(ax, x, y, w, h, fill=WHITE, edge=ROSE_LINE, lw=1.1, dashed=True, radius=radius, z=z)

def pill(ax, x, y, w, h, label, fill=GREEN_DARK, tcolor=WHITE, size=11, z=3, bold=False):
    """Fully rounded block (the FFN memory layers)."""
    rbox(ax, x, y, w, h, fill=fill, edge="none", radius=h / 2, z=z)
    text(ax, x + w / 2, y + h / 2, label, size=size, color=tcolor, bold=bold)

def block(ax, x, y, w, h, label, fill=SLATE, tcolor=WHITE, size=11, radius=0.25, z=3, bold=False, edge="none", lw=0):
    """Rounded rectangle block (Sequence Layer / MLP)."""
    rbox(ax, x, y, w, h, fill=fill, edge=edge, lw=lw, radius=radius, z=z)
    if label:
        text(ax, x + w / 2, y + h / 2, label, size=size, color=tcolor, bold=bold)

def trapezoid(ax, cx, cy, w, h, label="", fill=RED, tcolor=WHITE, size=9, flip=False,
              shadow=False, z=4, edge="none", hatch=None, lw=0.8, taper=0.55):
    """Trapezoid; default narrow TOP (a 'Linear' projection). flip=True -> narrow bottom (Router).
    shadow=True draws the pink offset copy used for the q/k/v projections."""
    wt, wb = (w * taper, w) if not flip else (w, w * taper)
    pts = [(cx - wb / 2, cy - h / 2), (cx + wb / 2, cy - h / 2), (cx + wt / 2, cy + h / 2), (cx - wt / 2, cy + h / 2)]
    if shadow:
        sh = [(px + 0.12 * w, py + 0.10 * h) for px, py in pts]
        ax.add_patch(Polygon(sh, closed=True, fc=RED_SHADOW, ec="none", zorder=z - 1))
    ax.add_patch(Polygon(pts, closed=True, fc=fill, ec=edge, lw=lw, zorder=z, hatch=hatch))
    if label:
        text(ax, cx, cy, label, size=size, color=tcolor, bold=True)
    return pts

def bowtie(ax, cx, cy, w, h, active=True, z=4, gap=0.06):
    """Two trapezoids tip-to-tip = a parameter block. active -> solid plum; else hatched lavender."""
    kw = dict(fill=PLUM if active else LAVENDER, edge=PLUM if not active else "none",
              hatch=None if active else "////", lw=0.6, z=z)
    trapezoid(ax, cx, cy + h / 4 + gap, w, h / 2, flip=True, **kw)    # top piece: narrow side down
    trapezoid(ax, cx, cy - h / 4 - gap, w, h / 2, flip=False, **kw)   # bottom piece: narrow side up

def tokens(ax, x, y, n=10, cell=0.42, h=0.5, fill=GREEN_DARK, z=3):
    """Row of small cells (the input token strip)."""
    for i in range(n):
        ax.add_patch(Rectangle((x + i * cell, y), cell, h, fc=fill, ec=INK, lw=0.5, zorder=z))
    return x + n * cell

def otimes(ax, cx, cy, r=0.32, z=5):
    ax.add_patch(Circle((cx, cy), r, fc=WHITE, ec=INK, lw=1.0, zorder=z))
    text(ax, cx, cy - 0.02, r"$\otimes$", size=11, color=INK)

def arrow(ax, p0, p1, color=INK, lw=1.2, dashed=False, rad=0.0, head=11, z=5, dotted=False, both=False):
    """Arrow from p0 to p1. rad != 0 bends it (positive = counter-clockwise bulge).
    dashed + color=GREY_LINE reproduces the 'inactive' path."""
    style = "<|-|>" if both else "-|>"
    ls = (0, (3, 2)) if dashed else ((0, (1, 1.6)) if dotted else "solid")
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=head, lw=lw, color=color,
                        connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=z,
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    return a

def line(ax, p0, p1, color=GREY_LINE, lw=0.9, dashed=True, z=2):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw,
            linestyle=(0, (3, 2)) if dashed else "solid", zorder=z, solid_capstyle="round")

def zoom_lines(ax, src_box, dst_box, color=GREY_LINE):
    """Dashed 'zoom' guide lines from a block (x,y,w,h) to its expanded panel (x,y,w,h)."""
    sx, sy, sw, sh = src_box
    dx, dy, dw, dh = dst_box
    line(ax, (sx + sw, sy + sh), (dx, dy + dh), color=color)
    line(ax, (sx + sw, sy), (dx, dy), color=color)

def timeline(ax, x0, x1, y, color=GREEN_DARK, lw=3.0, fade_in=False, z=3, head=14):
    """Thick arrow; fade_in draws the gradient-from-white start used in the paper."""
    if fade_in:
        n = 40
        for i in range(n):
            a = (i + 1) / n
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            ax.plot([xa, xb], [y, y], color=color, lw=lw, alpha=a, zorder=z, solid_capstyle="butt")
        arrow(ax, (x1 - 0.01, y), (x1, y), color=color, lw=lw, head=head, z=z + 1)
    else:
        arrow(ax, (x0, y), (x1, y), color=color, lw=lw, head=head, z=z)

def brace(ax, x0, x1, y, label="", below=True, color=ROSE_LINE, tcolor=ROSE, size=11, tick=0.35, gap=0.55):
    """Dashed rose bracket with end ticks and a centre tick, label beyond it."""
    s = -1 if below else 1
    ls = (0, (2.5, 2))
    ax.plot([x0, x1], [y, y], color=color, lw=1.1, linestyle=ls, zorder=3)
    for xx in (x0, x1):
        ax.plot([xx, xx], [y, y - s * tick], color=color, lw=1.1, linestyle=ls, zorder=3)
    xm = (x0 + x1) / 2
    ax.plot([xm, xm], [y, y + s * tick], color=color, lw=1.1, linestyle=ls, zorder=3)
    if label:
        text(ax, xm, y + s * (tick + gap), label, size=size, color=tcolor)

def callout(ax, x, y, w, h, title, body, bar=RED, size=9.5, title_size=10.5, band=0.75, z=2):
    """Text callout: light fill, title band, coloured bar on the left (Sleep-states centre column)."""
    ax.add_patch(Rectangle((x, y), w, h, fc="#FAF8F7", ec="none", zorder=z))
    ax.add_patch(Rectangle((x, y + h - band), w, band, fc=GREY_FILL, ec="none", zorder=z + 0.1))
    ax.add_patch(Rectangle((x - 0.12, y), 0.12, h, fc=bar, ec="none", zorder=z + 0.2))
    text(ax, x + 0.3, y + h - band / 2, title, size=title_size, bold=True, ha="left")
    text(ax, x + 0.3, y + (h - band) / 2, body, size=size, ha="left", va="center", linespacing=1.35)

def legend_box(ax, x, y, w, h, items, size=10, z=2):
    """items: list of (kind, label) with kind in {'bowtie_active','bowtie_inactive','solid','dashed','dotted',
    'pill:<colour>', 'block:<colour>', 'trap'}; drawn left->right inside a cream dashed box."""
    panel(ax, x, y, w, h, radius=0.5, fill=CREAM_LEG, z=z)
    cx = x + 0.9
    cy = y + h / 2
    for kind, label in items:
        if kind == "bowtie_active":
            bowtie(ax, cx, cy, 0.8, 0.7, active=True, z=z + 2); cx += 0.65
        elif kind == "bowtie_inactive":
            bowtie(ax, cx, cy, 0.8, 0.7, active=False, z=z + 2); cx += 0.65
        elif kind == "solid":
            ax.plot([cx - 0.4, cx + 0.4], [cy, cy], color=INK, lw=1.3, zorder=z + 2); cx += 0.6
        elif kind == "dashed":
            ax.plot([cx - 0.4, cx + 0.4], [cy, cy], color=GREY_LINE, lw=1.3, linestyle=(0, (3, 2)), zorder=z + 2); cx += 0.6
        elif kind == "dotted":
            ax.plot([cx - 0.4, cx + 0.4], [cy, cy], color=INK, lw=1.3, linestyle=(0, (1, 1.6)), zorder=z + 2); cx += 0.6
        elif kind.startswith("pill:"):
            rbox(ax, cx - 0.5, cy - 0.28, 1.0, 0.56, fill=kind.split(":", 1)[1], edge="none", radius=0.28, z=z + 2); cx += 0.75
        elif kind.startswith("block:"):
            rbox(ax, cx - 0.5, cy - 0.28, 1.0, 0.56, fill=kind.split(":", 1)[1], edge="none", radius=0.12, z=z + 2); cx += 0.75
        elif kind.startswith("hatch:"):
            rbox(ax, cx - 0.5, cy - 0.28, 1.0, 0.56, fill=LAVENDER, edge=kind.split(":", 1)[1], radius=0.12, z=z + 2)
            ax.add_patch(Rectangle((cx - 0.5, cy - 0.28), 1.0, 0.56, fc="none", ec=kind.split(":", 1)[1], hatch="////", lw=0, zorder=z + 2.1)); cx += 0.75
        elif kind == "trap":
            trapezoid(ax, cx, cy, 0.9, 0.55, fill=RED, z=z + 2); cx += 0.65
        t = text(ax, cx, cy, label, size=size, bold=True, ha="left")
        # advance by an estimate of the label width (0.115 data units per char at size 10)
        cx += 0.125 * size / 10 * len(label) + 1.1

def stack(ax, x, y0, w, h, labels, fills, gap=0.55, size=11, bold=False, arrows=True, top_arrow=True):
    """Vertical stack of pills drawn bottom->top with upward arrows. Returns list of (x,y,w,h)."""
    boxes = []
    y = y0
    for i, (lab, fc) in enumerate(zip(labels, fills)):
        pill(ax, x, y, w, h, lab, fill=fc, size=size, bold=bold)
        boxes.append((x, y, w, h))
        if arrows and (i < len(labels) - 1 or top_arrow):
            arrow(ax, (x + w / 2, y + h), (x + w / 2, y + h + gap), lw=1.3)
        y += h + gap
    return boxes

def sub_box(ax, x, y, w, h, label, size=9.5, rot=90, fill=WHITE, z=2, bold=False):
    """Narrow white dashed sub-box with rotated label (selected_params2 style)."""
    rbox(ax, x, y, w, h, fill=fill, edge=CREAM_EDGE, lw=0.9, dashed=True, radius=min(w, h) * 0.3, z=z)
    text(ax, x + w / 2, y + h / 2, label, size=size, rot=rot, bold=bold)

def hop_arrows(ax, xs, y, labels=None, size=9):
    """Small curved hops between consecutive x positions with counter labels above (1, 2, ..., N)."""
    for i in range(len(xs) - 1):
        arrow(ax, (xs[i], y), (xs[i + 1], y), rad=-0.45, lw=1.0, head=8)
    if labels:
        for xx, lab in zip(xs, labels):
            text(ax, xx, y + 0.55, lab, size=size, bold=True)
