"""Deposition across a refinement boundary, in two dimensions.

Left: cloud-in-cell on a uniform lattice. Middle: the single-level rule at a coarse/fine
boundary, for a cloud on the fine level (its virtual cells over the coarse leaf are summed
into it) and a cloud on the coarse level (its virtual cells over fine leaves are spread
uniformly over them). Right: the same sparse particles on a fine mesh, deposited on the
finest level and on a level capped two levels coarser.

The shading is the deposited density sum_p omega_Cp / dV_C computed below with the
two-dimensional analogue of the leaf-weight rule; the printed numbers are omega_Cp.

    python3 paper/scripts/fig_deposition.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize, to_rgb
from matplotlib.patches import Rectangle

import figstyle as fs

OUT = HERE.parent / "figures" / "fig_deposition"
STATS = {}
NUM_PT = 8          # weights printed inside cells (7 pt at the final page width)
LABEL_PT = 9
GRID = dict(color="0.62", lw=0.5)


# ---------------------------------------------------------------------------
# two-dimensional leaf-weight rule
# ---------------------------------------------------------------------------
class Leaf:
    """A leaf cell of a quadtree mesh: lower-left corner, edge length, level."""

    def __init__(self, x0, y0, size, level):
        self.x0, self.y0, self.size, self.level = x0, y0, size, level

    @property
    def centre(self):
        return self.x0 + self.size / 2, self.y0 + self.size / 2

    @property
    def area(self):
        return self.size ** 2

    def contains(self, x0, y0, size):
        """True when the square (x0, y0, size) lies inside this cell."""
        e = 1e-12
        return (self.x0 - e <= x0 and x0 + size <= self.x0 + self.size + e and
                self.y0 - e <= y0 and y0 + size <= self.y0 + self.size + e)

    def inside(self, x0, y0, size):
        """True when this cell lies inside the square (x0, y0, size)."""
        return Leaf(x0, y0, size, 0).contains(self.x0, self.y0, self.size)


def uniform_leaves(x0, x1, y0, y1, level, h0=1.0):
    h = h0 / 2 ** level
    return [Leaf(x, y, h, level) for x in np.arange(x0, x1 - 1e-9, h)
            for y in np.arange(y0, y1 - 1e-9, h)]


def local_level(xp, leaves):
    """Finest level among the leaves that own the four cell centres nearest x_p
    (the two-dimensional analogue of the eight nearest cell centres)."""
    d = [np.hypot(c.centre[0] - xp[0], c.centre[1] - xp[1]) for c in leaves]
    return max(leaves[i].level for i in np.argsort(d)[:4])


def virtual_cells(xp, level, h0=1.0):
    """The four cells of the level-`level` lattice that receive the cloud-in-cell
    weight of a particle at xp: list of (x0, y0, size, weight)."""
    h = h0 / 2 ** level
    s = np.asarray(xp) / h - 0.5
    i0 = np.floor(s).astype(int)
    f = s - i0
    w = [np.array([1 - f[0], f[0]]), np.array([1 - f[1], f[1]])]
    return [((i0[0] + a) * h, (i0[1] + b) * h, h, w[0][a] * w[1][b])
            for a in (0, 1) for b in (0, 1)]


def leaf_weights(xp, leaves, cap=None, h0=1.0):
    """Leaf-cell weights omega_Cp of one particle under the single-level rule with
    level cap: l_p = min(local level, cap). A virtual cell over a coarser (or equal)
    leaf adds its weight to that leaf; a virtual cell over finer leaves is spread over
    them in proportion to their area."""
    lp = local_level(xp, leaves)
    if cap is not None:
        lp = min(lp, cap)
    omega = np.zeros(len(leaves))
    for (qx, qy, qh, wq) in virtual_cells(xp, lp, h0):
        for k, C in enumerate(leaves):
            if C.level <= lp and C.contains(qx, qy, qh):
                omega[k] += wq
            elif C.level > lp and C.inside(qx, qy, qh):
                omega[k] += wq * C.area / qh ** 2
    return omega, lp


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------
def tint(color, f):
    c = to_rgb(color)
    return tuple(1 - f * (1 - x) for x in c)


CMAP = LinearSegmentedColormap.from_list(
    "deposit", [(0.0, tint(fs.PAL["blue"], 0.08)), (0.4, tint(fs.PAL["blue"], 0.45)),
                (0.75, fs.PAL["blue"]), (1.0, "#0B2466")])


def draw_mesh(ax, leaves, density, norm):
    for C, rho in zip(leaves, density):
        fc = CMAP(norm(rho)) if rho > 0 else "white"
        ax.add_patch(Rectangle((C.x0, C.y0), C.size, C.size, fc=fc, ec=GRID["color"],
                               lw=GRID["lw"], zorder=1))


def text_color(rho, norm):
    return "white" if norm(rho) > 0.55 else "k"


def draw_cloud(ax, xp, lp, h0=1.0, stencil=True, cloud=True, lw=1.2):
    """Particle (dot), its cell-sized cloud (outline) and, optionally, the four virtual
    cells of its level that receive weight (dashed)."""
    red = fs.PAL["red"]
    h = h0 / 2 ** lp
    if stencil:
        for (qx, qy, qh, _) in virtual_cells(xp, lp, h0):
            ax.add_patch(Rectangle((qx, qy), qh, qh, fc="none", ec=red, lw=0.9,
                                   ls=(0, (3, 2)), zorder=3))
    if cloud:
        ax.add_patch(Rectangle((xp[0] - h / 2, xp[1] - h / 2), h, h, fc="none", ec=red,
                               lw=lw, zorder=4))
    ax.plot(*xp, "o", color=red, ms=4.0, mew=0, zorder=5)


def number_spot(C, xp):
    """Where to print a cell's weight: the cell centre, pushed away from the particle
    in cells large enough to leave room."""
    cx, cy = C.centre
    sx = np.sign(cx - xp[0]) or 1.0
    sy = np.sign(cy - xp[1]) or 1.0
    k = 0.22 if C.size >= 1.0 else 0.0
    return cx + k * sx * C.size, cy + k * sy * C.size


def frame(ax, x0, x1, y0, y1):
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="0.35", lw=0.8,
                           zorder=6, clip_on=False))


def print_weights(ax, leaves, omega, xp, norm):
    for C, w in zip(leaves, omega):
        if w > 0:
            ax.text(*number_spot(C, xp), f"{w:.2f}", ha="center", va="center",
                    fontsize=NUM_PT, color=text_color(w / C.area, norm), zorder=7)


def panel_cic(ax):
    leaves = uniform_leaves(0, 3, 0, 4, 0)
    xp = (1.2, 2.1)
    omega, lp = leaf_weights(xp, leaves)
    rho = omega / np.array([C.area for C in leaves])
    norm = Normalize(0, rho.max())
    draw_mesh(ax, leaves, rho, norm)
    draw_cloud(ax, xp, lp, stencil=False)
    print_weights(ax, leaves, omega, xp, norm)
    frame(ax, 0, 3, 0, 4)
    return [omega.sum()]


def panel_boundary(ax):
    leaves = uniform_leaves(0, 2, 0, 4, 0) + uniform_leaves(2, 4, 0, 4, 1)
    # (x_p, cap): both particles sit in coarse cells next to the boundary, so their
    # local level is the fine one; the second is capped at the coarse level
    parts = [((1.95, 3.40), None), ((1.90, 1.30), 0)]
    omegas, levels = [], []
    for xp, cap in parts:
        w, lp = leaf_weights(xp, leaves, cap)
        omegas.append(w)
        levels.append(lp)
    area = np.array([C.area for C in leaves])
    rho = sum(omegas) / area
    norm = Normalize(0, rho.max())
    draw_mesh(ax, leaves, rho, norm)
    ax.plot([2, 2], [0, 4], color="0.25", lw=1.2, zorder=2)
    for (xp, _), lp, w in zip(parts, levels, omegas):
        draw_cloud(ax, xp, lp, cloud=False)
        print_weights(ax, leaves, w, xp, norm)
    assert levels == [1, 0], levels
    lab = {1: r"$\ell_p=\ell+1$", 0: r"$\ell_p=\ell$"}
    red = fs.PAL["red"]
    ax.text(0.5, 3.5, lab[levels[0]], ha="center", va="center", fontsize=LABEL_PT, color=red)
    ax.text(0.5, 1.5, lab[levels[1]], ha="center", va="center", fontsize=LABEL_PT, color=red)
    ax.text(1.0, 4.06, r"level $\ell$", ha="center", va="bottom", fontsize=LABEL_PT)
    ax.text(3.0, 4.06, r"level $\ell+1$", ha="center", va="bottom", fontsize=LABEL_PT)
    frame(ax, 0, 4, 0, 4)
    return [w.sum() for w in omegas]


def panel_cap(ax):
    # the same particles drawn twice: finest level (left half), capped two levels
    # coarser (right half)
    pts = np.array([(0.62, 0.70), (1.35, 1.05), (0.78, 1.72), (1.42, 2.22),
                    (0.58, 2.66), (1.18, 3.05), (0.90, 3.42)])
    fine = 2
    halves = []
    for x_off, cap in ((0.0, None), (2.0, 0)):
        leaves = uniform_leaves(x_off, x_off + 2, 0, 4, fine)
        area = np.array([C.area for C in leaves])
        dep = np.zeros(len(leaves))
        lps = []
        for p in pts:
            w, lp = leaf_weights((p[0] + x_off, p[1]), leaves, cap)
            dep += w
            lps.append(lp)
        assert abs(dep.sum() - len(pts)) < 1e-12      # every cloud lands inside
        halves.append((leaves, dep / area, lps, x_off))
    rho_all = np.concatenate([h[1] for h in halves])
    norm = LogNorm(rho_all[rho_all > 0].min() / 1.5, rho_all.max())
    for leaves, rho, lps, x_off in halves:
        draw_mesh(ax, leaves, rho, norm)
        for p, lp in zip(pts, lps):
            draw_cloud(ax, (p[0] + x_off, p[1]), lp, stencil=False, lw=0.8)
    ax.plot([2, 2], [0, 4], color="0.25", lw=1.2, zorder=6)
    frame(ax, 0, 4, 0, 4)
    STATS["empty cells (finest, capped)"] = [round(float(np.mean(h[1] == 0)), 3)
                                             for h in halves]


def make():
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.62))
    H, gap, x0, y0 = 2.70, 0.25, 0.05, 0.46
    widths = [H * 3 / 4, H, H]
    axes, x = [], x0
    for w in widths:
        axes.append(fs.inch_axes(fig, x, y0, w, H))
        x += w + gap
    sums = panel_cic(axes[0]) + panel_boundary(axes[1])
    assert all(abs(s - 1) < 1e-12 for s in sums), sums
    panel_cap(axes[2])
    for ax, t in zip(axes, ["Cloud-in-cell", "Refinement boundary", "Level cap"]):
        ax.set_title(t, fontsize=fs.RC["font.size"], pad=19)
    one = r"$\sum_{C}\,\omega_{Cp}=1$"
    below = dict(ha="center", va="top", fontsize=LABEL_PT)
    axes[0].text(1.5, -0.16, one, **below)
    axes[1].text(2.0, -0.16, one + " for each particle", **below)
    above = dict(ha="center", va="bottom", fontsize=LABEL_PT)
    axes[0].text(1.5, 4.06, "uniform lattice", **above)
    axes[2].text(1.0, 4.06, "finest level", **above)
    axes[2].text(3.0, 4.06, "capped level", **above)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(STATS)
    print("\n".join(fs.save(fig, str(OUT))))
