"""czstyle: matplotlib style of Guo, Stone, Quataert & Springel (2025), arXiv:2504.16802."""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

RC = {
    # the first author's public "mg" style sheet
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Bitstream Vera Serif", "Computer Modern Roman",
                   "New Century Schoolbook", "Times New Roman", "Times", "serif"],
    "mathtext.fontset": "dejavuserif",
    "text.usetex": False,
    "xtick.top": True, "ytick.right": True,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "axes.grid.axis": "both", "axes.grid.which": "both",
    # matplotlib defaults the paper relies on, pinned so another style cannot move them
    "font.size": 10, "axes.titlesize": "large", "legend.fontsize": "medium",
    "xtick.major.size": 3.5, "ytick.major.size": 3.5,
    "xtick.minor.size": 2.0, "ytick.minor.size": 2.0,
    "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "xtick.minor.width": 0.6, "ytick.minor.width": 0.6,
    "axes.linewidth": 0.8, "lines.linewidth": 1.5,
    "axes.grid": False, "legend.frameon": False,
    "figure.facecolor": "white", "savefig.dpi": 300, "pdf.fonttype": 3,
}

def use_style():
    mpl.rcParams.update(RC)

def write_mplstyle(path="cyclic_zoom.mplstyle"):
    """Same settings as a style sheet, for plt.style.use(path)."""
    with open(path, "w") as f:
        for k, v in RC.items():
            f.write(f"{k}: {', '.join(v) if isinstance(v, list) else v}\n")

def overflow(fig, tol=0.02):
    """{axes index: {side: inches}} for tick labels, axis labels or titles cut by the figure edge."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    W, H = fig.get_size_inches()
    out = {}
    for k, ax in enumerate(fig.axes):
        b = ax.get_tightbbox(renderer).transformed(fig.dpi_scale_trans.inverted())
        over = dict(left=-b.x0, bottom=-b.y0, right=b.x1 - W, top=b.y1 - H)
        over = {side: round(float(v), 2) for side, v in over.items() if v > tol}
        if over:
            out[k] = over
    return out

def save(fig, stem, preview_dpi=200):
    """Vector PDF at the exact figsize (no tight bbox) plus a PNG preview to look at."""
    fig.savefig(f"{stem}.pdf")
    fig.savefig(f"{stem}.png", dpi=preview_dpi)
    for k, over in overflow(fig).items():
        print(f"czstyle: labels of fig.axes[{k}] are cut at the figure edge, inches: {over}")

# ---- colours ----
PAL = {"blue": "#3369E8", "red": "#EA4335", "yellow": "#FBBC05",
       "green": "#009925", "orange": "#FF7F0E"}
PAL2 = {"blue": "#0466C8", "sky": "#0496FF", "red": "#D00000", "orange": "#F48C06"}
MASK_LINE = dict(color="grey", lw=1.5, alpha=0.4)   # radii where the method acts
REF_LINE = dict(color="k", lw=1.5)                  # characteristic radius, fitted curve
GUIDE = dict(color="k", lw=1.5, ls="--")            # analytic expectation

# ---- colormaps ----
def truncate_cmap(name, lo=0.0, hi=1.0, n=256):
    cmap = plt.get_cmap(name)
    return LinearSegmentedColormap.from_list(f"trunc({name},{lo:.2f},{hi:.2f})",
                                             cmap(np.linspace(lo, hi, n)))

CMAP = {"dens": truncate_cmap("magma", 0.2, 1.0), "beta": "RdBu_r",
        "temp": "RdYlBu_r", "Brr2": "RdBu_r"}

def lognorm_about(center=1.0, decades=3.0):
    """Log norm symmetric about a physical threshold, so the colormap midpoint lands on it."""
    return LogNorm(center * 10.0**-decades, center * 10.0**decades)

# ---- layout ----
def inch_axes(fig, x0, y0, w, h):
    """Axes placed in inches from the bottom-left corner of the figure."""
    W, H = fig.get_size_inches()
    return fig.add_axes([x0 / W, y0 / H, w / W, h / H])

def slice_mosaic(nrows, ncols, fig_w=8.0, gap=0.06, cbar="left", cbar_w=0.08,
                 left=None, right=None, bottom=0.36, top=0.08):
    """Touching square image panels sized to fill fig_w, plus one colorbar spanning all rows.

    cbar="left" is the layout of Figs 4 and 6: the colorbar sits outside the y tick labels.
    cbar="right" puts it 0.05 in from the last column. left, right, bottom, top are the margins
    in inches; shrink left and bottom when scale bars replace the tick labels.
    Returns fig, axes[nrows, ncols], cax.
    """
    d_left, d_right = (1.37, 0.11) if cbar == "left" else (0.62, 0.86)
    left = d_left if left is None else left
    right = d_right if right is None else right
    panel = (fig_w - left - right - (ncols - 1) * gap) / ncols
    span = nrows * panel + (nrows - 1) * gap
    fig = plt.figure(figsize=(fig_w, bottom + span + top))
    axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            axes[i, j] = inch_axes(fig, left + j * (panel + gap),
                                   bottom + (nrows - 1 - i) * (panel + gap), panel, panel)
    x_cbar = left - 0.585 - cbar_w if cbar == "left" else fig_w - right + 0.05
    return fig, axes, inch_axes(fig, x_cbar, bottom, cbar_w, span)

def tall_colorbar(fig, im, cax, label, side="left"):
    """Colorbar for slice_mosaic. Ticks and label both go on the outer side, so nothing
    competes with the panel tick labels in the gap between colorbar and panels."""
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(label)
    cax.yaxis.set_ticks_position(side)
    cax.yaxis.set_label_position(side)
    return cb

def side_colorbar(fig, ax, im, label, size="4%", pad=0.02):
    """Thin colorbar glued to a single image panel (Figs 2, 3)."""
    cax = make_axes_locatable(ax).append_axes("right", size=size, pad=pad)
    return fig.colorbar(im, cax=cax, label=label)

# ---- image-panel annotations ----
def slice_ticks(ax, half, show_x=True, show_y=True):
    """Ticks at -half/2, 0, +half/2 so labels never collide at touching panel edges."""
    t = [-half / 2, 0, half / 2]
    ax.set_xticks(t)
    ax.set_yticks(t)
    if not show_x:
        ax.xaxis.set_major_formatter(mpl.ticker.NullFormatter())
    if not show_y:
        ax.yaxis.set_major_formatter(mpl.ticker.NullFormatter())

def zoom_marker(ax, half_prev, half_this, connect="left", color="k"):
    """Box = extent of the neighbouring smaller panel; dotted lines show the magnification."""
    s, L = half_prev, half_this
    ax.plot([-s, s, s, -s, -s], [-s, -s, s, s, -s], color=color, lw=1.0)
    for side, sign in (("left", -1), ("right", 1)):
        if connect in (side, "both"):
            ax.plot([sign * L, sign * s], [L, s], color=color, lw=1.0, ls=":")
            ax.plot([sign * L, sign * s], [-L, -s], color=color, lw=1.0, ls=":")
    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)

def run_label(ax, text, on_dark=False):
    """Run name in the top-left corner: white on dark images, black on light ones, no box."""
    ax.text(0.05, 0.95, text, transform=ax.transAxes, va="top", color="w" if on_dark else "k")

def scale_bar(ax, length, label, color="white", frac_y=0.12):
    """Horizontal scale bar used instead of tick labels (Figs 1, 10)."""
    y0, y1 = ax.get_ylim()
    y = y0 + frac_y * (y1 - y0)
    ax.plot([-length / 2, length / 2], [y, y], color=color, lw=1.5)
    ax.text(0, y + 0.03 * (y1 - y0), label, color=color, ha="center", va="bottom")

# ---- line-plot elements ----
def band(ax, x, lo, hi, color, alpha=0.2):
    """10-90 percentile band in the colour of its curve."""
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, lw=1.0)

def average_window(ax, t0, t1, color=PAL["blue"]):
    """Shade the interval used for time averages."""
    ax.axvspan(t0, t1, color=color, alpha=0.1, lw=0)

def no_minor_labels(ax, axis="y"):
    """Hide matplotlib's '2x10^-1'-style minor labels on short log ranges."""
    getattr(ax, f"{axis}axis").set_minor_formatter(mpl.ticker.NullFormatter())

def violin(ax, data, positions, color, width=0.5):
    """Alpha-0.5 violins drawn over an opaque mean dot."""
    ax.plot(positions, [np.mean(d) for d in data], "o", color=color, ms=8, zorder=1)
    parts = ax.violinplot(data, positions=positions, widths=width,
                          showextrema=False, showmeans=False)
    for pc in parts["bodies"]:
        pc.set_facecolor(color)
        pc.set_edgecolor(color)
        pc.set_alpha(0.5)
        pc.set_linewidth(1.0)
        pc.set_zorder(2)
    return parts
