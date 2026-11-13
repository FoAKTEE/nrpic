"""Colour / line-style mapping of the geodesic-campaign figures, on top of the project style
python/nrpic/figstyle.py (``use_style``, palette, ``GUIDE``, ``save``).

Mapping used in every figure of analysis/geodesic (stated in docs/results_geodesic.md):
  colour  = method:  blue   reference (exact solution, published value)
                     red    implicit midpoint
                     yellow Boris (DGREM), symmetric triad
                     green  Boris (DGREM), Cholesky triad
                     orange CPU executable (CPU-GPU comparison only)
  line style = metric input:  solid  analytic metric, spherical coordinates (KS or BL)
                              dashed analytic Cartesian Kerr-Schild
                              dotted Cartesian Kerr-Schild reconstructed with cubic Hermite
                                     interpolation (virtual lattice or AthenaK mesh)
  ordered families (several dt or dx of one method): shades of the method colour, light =
  large step, dark = small step.
  black dashed: analytic expectation / power-law guide; grey: neutral markers (pericentre
  time, horizon radius).
"""

from __future__ import annotations

import numpy as np
from matplotlib.colors import to_rgb

from geo_common import FIG_DIR, HERE
from nrpic import figstyle
from nrpic.figstyle import COLUMN_WIDTH, FULL_WIDTH, GUIDE, MASK_LINE, PAL, REF_LINE, THIN  # noqa

FIGS = HERE / "figs"

COLOR = {"ref": PAL["blue"], "mid": PAL["red"], "bsym": PAL["yellow"], "bchol": PAL["green"],
         "cpu": PAL["orange"]}
LS = {"ks": "-", "bl": "-", "cks": "--", "lat": ":", "mesh": ":"}
MARKER = {"mid": "o", "bsym": "^", "bchol": "s"}
PUSHER_NAME = {"mid": "midpoint", "bsym": "Boris sym.", "bchol": "Boris Chol."}
METRIC_NAME = {"ks": "analytic sph. KS", "bl": "analytic BL", "cks": "analytic Cart. KS",
               "lat": "Hermite lattice", "mesh": "Hermite mesh"}


def use_style():
    figstyle.use_style()


def style(pusher, metric, **kw):
    """Line kwargs for a (pusher, metric) series."""
    d = dict(color=COLOR[pusher], ls=LS[metric])
    d.update(kw)
    return d


def label(pusher, metric):
    return f"{PUSHER_NAME[pusher]}, {METRIC_NAME[metric]}"


def shades(pusher, n):
    """n shades of the method colour, light (first) to dark (last)."""
    c = np.array(to_rgb(COLOR[pusher]))
    out = []
    for f in np.linspace(-0.55, 0.45, n):
        if f < 0:
            out.append(tuple(c + (1 - c) * (-f)))      # towards white
        else:
            out.append(tuple(c * (1 - f)))             # towards black
    return out


def save_paper(fig, name):
    """Vector PDF in paper/figures (exact size) and a PNG copy in analysis/geodesic/figs."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    figstyle.save(fig, str(FIG_DIR / name), png=False)
    fig.savefig(str(FIGS / f"{name}.png"), dpi=200)
    return [str(FIG_DIR / f"{name}.pdf"), str(FIGS / f"{name}.png")]


def save_diag(fig, name):
    """PDF and PNG in analysis/geodesic/figs."""
    FIGS.mkdir(parents=True, exist_ok=True)
    return figstyle.save(fig, str(FIGS / name))


def black_hole_disk(ax, r_plus, r_ergo=None, zorder=1):
    from matplotlib.patches import Circle
    if r_ergo is not None:
        ax.add_patch(Circle((0, 0), r_ergo, color="0.75", lw=0, zorder=zorder))
    ax.add_patch(Circle((0, 0), r_plus, color="black", lw=0, zorder=zorder + 1))


def log_time_axis(ax, ylabel, xlabel=r"$t/M$", labelpad=-2):
    ax.set_yscale("log")
    ax.set_xlabel(xlabel, labelpad=labelpad)
    ax.set_ylabel(ylabel)
