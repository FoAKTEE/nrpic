"""Shared figure style for every diagnostic and paper figure of this project.

Call ``use_style()`` first in every plotting script. The style follows the figure
conventions the project owner asked for (the look of Guo, Stone, Quataert & Springel
2025, arXiv:2504.16802):

- DejaVu Serif for text and math, no LaTeX rendering, 10 pt everywhere (12 pt titles,
  8 pt legends only in dense grids); Type 3 fonts in PDF.
- Ticks inward on all four sides, minor ticks on.
- Data lines 1.5 pt, annotation lines 1.0 pt.
- Colour says which run or method, line style says which component:
  blue ``PAL["blue"]`` is the reference (analytic or published result), red
  ``PAL["red"]`` is the method under test; yellow, green, orange for further series.
  Solid = total, dashed and dotted = components.
- Analytic expectations: black dashed (``GUIDE``); fits and characteristic values: black
  solid (``REF_LINE``); neutral markers: grey, alpha 0.4 (``MASK_LINE``).
- Uncertainty or spread: ``band`` (fill, alpha 0.2); averaging window: ``average_window``
  (axvspan, alpha 0.1), both in the series colour.
- Legends without a frame, inside the axes, two columns when it fits.
- No panel letters; captions say "Top left", "Bottom right".
- Figure width 8 in (full page) or 4 in (one column); margins set explicitly with
  ``subplots_adjust``; saved at the exact figure size (no ``bbox_inches="tight"``).
- Images: square, touching panels, ``aspect="equal"``, rasterized, no interpolation;
  density-like quantities in magma truncated to [0.2, 1] with a log norm; signed or
  ratio quantities in ``RdBu_r`` centred on the physical threshold.
- x-labels pulled in with ``labelpad=-2`` in stacked strips and grids.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

RC = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Bitstream Vera Serif", "Computer Modern Roman",
                   "New Century Schoolbook", "Times New Roman", "Times", "serif"],
    "mathtext.fontset": "dejavuserif",
    "text.usetex": False,
    "font.size": 10,
    "axes.titlesize": "large",
    "legend.fontsize": "medium",
    "xtick.top": True, "ytick.right": True,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "xtick.major.size": 3.5, "ytick.major.size": 3.5,
    "xtick.minor.size": 2.0, "ytick.minor.size": 2.0,
    "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "xtick.minor.width": 0.6, "ytick.minor.width": 0.6,
    "axes.linewidth": 0.8,
    "axes.grid": False, "axes.grid.axis": "both", "axes.grid.which": "both",
    "lines.linewidth": 1.5,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "savefig.dpi": 300,
    "pdf.fonttype": 3,
}

# full-page and one-column figure widths in inches
FULL_WIDTH = 8.0
COLUMN_WIDTH = 4.0


def use_style():
    """Apply the project figure style."""
    mpl.rcParams.update(RC)


# ---- colours ----
PAL = {"blue": "#3369E8", "red": "#EA4335", "yellow": "#FBBC05",
       "green": "#009925", "orange": "#FF7F0E"}
PAL2 = {"blue": "#0466C8", "sky": "#0496FF", "red": "#D00000", "orange": "#F48C06"}
#: default colour order: reference, method under test, then further series
SERIES = [PAL["blue"], PAL["red"], PAL["yellow"], PAL["green"], PAL["orange"]]
MASK_LINE = dict(color="grey", lw=1.5, alpha=0.4)   # neutral markers (radii, times)
REF_LINE = dict(color="k", lw=1.5)                  # fits, characteristic values
GUIDE = dict(color="k", lw=1.5, ls="--")            # analytic expectation
THIN = dict(color="k", lw=1.0)                      # annotation lines


# ---- colormaps ----
def truncate_cmap(name, lo=0.0, hi=1.0, n=256):
    cmap = plt.get_cmap(name)
    return LinearSegmentedColormap.from_list(f"trunc({name},{lo:.2f},{hi:.2f})",
                                             cmap(np.linspace(lo, hi, n)))


CMAP = {"dens": truncate_cmap("magma", 0.2, 1.0), "diverging": "RdBu_r",
        "temp": "RdYlBu_r"}


def series_colors(n, cmap=None):
    """n colours for an ordered family of curves (times, levels): the main palette
    for up to five curves, a truncated sequential map beyond that."""
    if n <= len(SERIES) and cmap is None:
        return SERIES[:n]
    cm = truncate_cmap(cmap or "viridis", 0.05, 0.92)
    return [cm(x) for x in np.linspace(0.0, 1.0, n)]


# ---- layout helpers ----
def inch_axes(fig, x0, y0, w, h):
    """Axes placed in inches from the bottom-left corner of the figure."""
    W, H = fig.get_size_inches()
    return fig.add_axes([x0 / W, y0 / H, w / W, h / H])


def slice_mosaic(nrows, ncols, panel=1.585, gap=0.06, left=1.37, bottom=0.36,
                 fig_w=8.0, top_pad=0.04, cbar="left", cbar_w=0.08, cbar_gap=0.585):
    """Touching square image panels plus one tall colorbar."""
    fig_h = bottom + nrows * panel + (nrows - 1) * gap + top_pad
    fig = plt.figure(figsize=(fig_w, fig_h))
    axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            y = bottom + (nrows - 1 - i) * (panel + gap)
            axes[i, j] = inch_axes(fig, left + j * (panel + gap), y, panel, panel)
    span = nrows * panel + (nrows - 1) * gap
    if cbar == "left":
        cax = inch_axes(fig, left - cbar_gap - cbar_w, bottom, cbar_w, span)
    else:
        cax = inch_axes(fig, left + ncols * (panel + gap), bottom, cbar_w, span)
    return fig, axes, cax


def slice_ticks(ax, half, show_x=True, show_y=True):
    """Ticks at -L/2, 0, +L/2 so labels never collide at touching panel edges."""
    t = [-half / 2, 0, half / 2]
    ax.set_xticks(t)
    ax.set_yticks(t)
    if not show_x:
        ax.xaxis.set_major_formatter(mpl.ticker.NullFormatter())
    if not show_y:
        ax.yaxis.set_major_formatter(mpl.ticker.NullFormatter())


def zoom_marker(ax, half_prev, half_this, connect="left"):
    """Black box = previous panel's extent; dotted magnification lines."""
    s, L = half_prev, half_this
    ax.plot([-s, s, s, -s, -s], [-s, -s, s, s, -s], color="k", lw=1.0)
    if connect in ("left", "both"):
        ax.plot([-L, -s], [L, s], color="k", lw=1.0, ls=":")
        ax.plot([-L, -s], [-L, -s], color="k", lw=1.0, ls=":")
    if connect in ("right", "both"):
        ax.plot([L, s], [L, s], color="k", lw=1.0, ls=":")
        ax.plot([L, s], [-L, -s], color="k", lw=1.0, ls=":")
    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)


def scale_bar(ax, length, label, color="white", frac_y=0.12):
    """Horizontal scale bar used instead of tick labels."""
    y0, y1 = ax.get_ylim()
    y = y0 + frac_y * (y1 - y0)
    ax.plot([-length / 2, length / 2], [y, y], color=color, lw=1.5)
    ax.text(0, y + 0.03 * (y1 - y0), label, color=color, ha="center", va="bottom")


def side_colorbar(fig, ax, im, label, size="4%", pad=0.02):
    """Thin colorbar glued to a single panel."""
    cax = make_axes_locatable(ax).append_axes("right", size=size, pad=pad)
    return fig.colorbar(im, cax=cax, label=label)


def band(ax, x, lo, hi, color, alpha=0.2):
    """Spread band (for example 10-90 percentile) in the series colour."""
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, lw=1.0)


def average_window(ax, t0, t1, color=PAL["blue"]):
    """Interval used for time averages."""
    ax.axvspan(t0, t1, color=color, alpha=0.1)


def no_minor_labels(ax, axis="y"):
    """Hide '2x10^-1'-style minor labels on short log ranges."""
    getattr(ax, f"{axis}axis").set_minor_formatter(mpl.ticker.NullFormatter())


def save(fig, path_without_ext, png=True):
    """Write the vector PDF at the exact figure size and, by default, a PNG copy for
    inspection. Returns the list of files written."""
    out = [f"{path_without_ext}.pdf"]
    fig.savefig(out[0])
    if png:
        out.append(f"{path_without_ext}.png")
        fig.savefig(out[1], dpi=200)
    return out
