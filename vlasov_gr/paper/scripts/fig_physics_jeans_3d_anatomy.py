#!/usr/bin/env python3
"""Physics figure: 3D orbital & meridional anatomy of Jeans binary BH formation & MC vertical kick.

Reads `$SCRATCH/runs/repro_wave4c/jeans_10k_strat_mid/` snapshots (`t = 10, 30, 55 M`),
horizon centroids (`co_{0,1}.txt`), and spherical-harmonic shapes (`horizon_shape_{0,1}.txt`),
saving compact data to `vlasov_gr/paper/data/physics_jeans_3d.npz` and rendering a 2x3
equatorial (x,y) + meridional (x,z) overview in `vlasov_gr/paper/figures/fig_physics_jeans_3d_anatomy.{pdf,png}`.
"""
from math import factorial
import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/analysis")
import czstyle as cz  # noqa: E402
from diag.common import read_snapshot  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_jeans_3d.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_jeans_3d_anatomy")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
JDIR = os.path.join(SCRATCH, "runs", "repro_wave4c", "jeans_10k_strat_mid")
PREF = "jeans_10k_strat_mid"


def safe_loadtxt(path: str) -> np.ndarray:
    rows = []
    ncols = None
    with open(path, "r") as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            if ncols is None:
                ncols = len(vals)
            if len(vals) == ncols:
                rows.append(vals)
    return np.asarray(rows, dtype=np.float64)


def ylm(l: int, m: int, theta: np.ndarray, phi: np.ndarray):
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += (
            ((-1.0) ** k)
            * (c ** (2 * l + m - 2 * k))
            * (s ** (2 * k - m))
            / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m))
        )
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_radius(coef: np.ndarray, theta: np.ndarray, phi: np.ndarray, lmax: int = 8) -> np.ndarray:
    r, i = np.zeros_like(theta, dtype=float), 0
    for l in range(lmax + 1):
        re_, _ = ylm(l, 0, theta, phi)
        r += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, theta, phi)
            r += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return r


def read_shapes(path: str) -> dict:
    out, t = {}, None
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", line)
                if m:
                    t = float(m.group(1))
            elif line.strip() and t is not None:
                out[t] = np.array(line.split(), dtype=float)
    return out


def eq_outline(shapes: dict, t_target: float, cx: float, cy: float):
    if not shapes:
        return np.array([]), np.array([])
    ts = np.array(sorted(shapes.keys()))
    tc = float(ts[np.argmin(np.abs(ts - t_target))])
    if abs(tc - t_target) > 1.0:
        return np.array([]), np.array([])
    phi = np.linspace(0.0, 2.0 * np.pi, 181)
    th = np.full_like(phi, 0.5 * np.pi)
    rr = horizon_radius(shapes[tc], th, phi)
    return (cx + rr * np.cos(phi)).astype(np.float32), (cy + rr * np.sin(phi)).astype(np.float32)


def mer_outline(shapes: dict, t_target: float, cx: float, cz_bh: float):
    if not shapes:
        return np.array([]), np.array([])
    ts = np.array(sorted(shapes.keys()))
    tc = float(ts[np.argmin(np.abs(ts - t_target))])
    if abs(tc - t_target) > 1.0:
        return np.array([]), np.array([])
    th_p = np.linspace(0.0, np.pi, 91)
    r_p = horizon_radius(shapes[tc], th_p, np.zeros_like(th_p))
    x_p = cx + r_p * np.sin(th_p)
    z_p = cz_bh + r_p * np.cos(th_p)
    th_m = np.linspace(np.pi, 0.0, 91)
    r_m = horizon_radius(shapes[tc], th_m, np.full_like(th_m, np.pi))
    x_m = cx - r_m * np.sin(th_m)
    z_m = cz_bh + r_m * np.cos(th_m)
    return np.concatenate([x_p, x_m]).astype(np.float32), np.concatenate([z_p, z_m]).astype(np.float32)


def split_species(tag, sp):
    if len(sp) and np.max(sp) >= 2:
        return sp
    out = np.zeros(len(tag), dtype=np.int8)
    out[(tag >= 6000) & (tag < 8000)] = 1
    out[tag >= 8000] = 2
    return out


def build_npz() -> dict:
    co0 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.co_0.txt"))
    co1 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.co_1.txt"))
    n_co = min(len(co0), len(co1))
    co0, co1 = co0[:n_co], co1[:n_co]
    stride = max(1, n_co // 450)
    co0s, co1s = co0[::stride], co1[::stride]
    if co0s[-1, 1] != co0[-1, 1]:
        co0s = np.vstack([co0s, co0[-1:]])
        co1s = np.vstack([co1s, co1[-1:]])

    sh0 = read_shapes(os.path.join(JDIR, f"{PREF}.horizon_shape_0.txt"))
    sh1 = read_shapes(os.path.join(JDIR, f"{PREF}.horizon_shape_1.txt"))

    def bh_at(co, t):
        k = int(np.argmin(np.abs(co[:, 1] - t)))
        return float(co[k, 2]), float(co[k, 3]), float(co[k, 4])

    out = {
        "co_t": co0s[:, 1].astype(np.float64),
        "co0_xyz": co0s[:, 2:5].astype(np.float32),
        "co1_xyz": co1s[:, 2:5].astype(np.float32),
    }

    snap_indices = (2, 6, 11)  # t = 10M, 30M, 55M
    for idx in snap_indices:
        fn = os.path.join(JDIR, f"{PREF}.part.{idx:05d}.bin")
        t, d, tag, sp = read_snapshot(fn)
        sp_s = split_species(tag, sp)
        c0 = bh_at(co0, t)
        c1 = bh_at(co1, t)
        hx0_xy, hy0_xy = eq_outline(sh0, t, c0[0], c0[1])
        hx1_xy, hy1_xy = eq_outline(sh1, t, c1[0], c1[1])
        hx0_xz, hz0_xz = mer_outline(sh0, t, c0[0], c0[2])
        hx1_xz, hz1_xz = mer_outline(sh1, t, c1[0], c1[2])

        tag_s = f"s{idx}"
        out[f"{tag_s}_t"] = np.float64(t)
        out[f"{tag_s}_xyz"] = d[:, :3].astype(np.float32)
        out[f"{tag_s}_sp"] = sp_s.astype(np.int8)
        out[f"{tag_s}_hx0_xy"], out[f"{tag_s}_hy0_xy"] = hx0_xy, hy0_xy
        out[f"{tag_s}_hx1_xy"], out[f"{tag_s}_hy1_xy"] = hx1_xy, hy1_xy
        out[f"{tag_s}_hx0_xz"], out[f"{tag_s}_hz0_xz"] = hx0_xz, hz0_xz
        out[f"{tag_s}_hx1_xz"], out[f"{tag_s}_hz1_xz"] = hx1_xz, hz1_xz

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def plot_proj(ax, pts, sp, cx, cy, co0_xy, co1_xy, co_t, t_s, hx0, hy0, hx1, hy1,
              xlim, ylim, is_xz: bool, label_txt: str):
    env = sp == 0
    cA = sp == 1
    cB = sp == 2
    ax.scatter(pts[env, cx], pts[env, cy], s=0.85, c="0.62", alpha=0.36, linewidths=0,
               rasterized=True, label="Envelope")
    if np.any(cA):
        ax.scatter(pts[cA, cx], pts[cA, cy], s=1.35, c=cz.PAL["blue"], alpha=0.58, linewidths=0,
                   rasterized=True, label="Clump A")
    if np.any(cB):
        ax.scatter(pts[cB, cx], pts[cB, cy], s=1.35, c=cz.PAL["red"], alpha=0.58, linewidths=0,
                   rasterized=True, label="Clump B")
    if is_xz:
        ax.axhline(0.0, color="0.4", lw=0.8, ls="--", alpha=0.55)
    m = co_t <= t_s + 1e-6
    if np.any(m):
        ax.plot(co0_xy[m, cx], co0_xy[m, cy], color=cz.PAL["blue"], lw=1.35, zorder=4)
        ax.plot(co1_xy[m, cx], co1_xy[m, cy], color=cz.PAL["red"], lw=1.35, zorder=4)
    if len(hx0):
        ax.plot(hx0, hy0, color="k", lw=1.15, zorder=6)
    if len(hx1):
        ax.plot(hx1, hy1, color="k", lw=1.15, zorder=6)
    ax.text(0.04, 0.94, label_txt, transform=ax.transAxes, ha="left", va="top", fontsize=7.2)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")


def main():
    cz.use_style()
    D = build_npz()

    xlim = (-12.5, 12.5)
    ylim_xy = (-12.5, 12.5)
    zlim_xz = (-7.5, 7.5)

    fig, axes = plt.subplots(
        2, 3, figsize=(8.4, 5.4),
        gridspec_kw={"height_ratios": [25.0, 15.0], "hspace": 0.14, "wspace": 0.08},
    )
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.095, top=0.965)

    co_t = D["co_t"]
    co0 = D["co0_xyz"]
    co1 = D["co1_xyz"]

    for col, sidx in enumerate((2, 6, 11)):
        k = f"s{sidx}"
        t_s = float(D[f"{k}_t"])
        xyz = D[f"{k}_xyz"]
        sp = D[f"{k}_sp"]
        sep = float(np.linalg.norm(co0[np.argmin(np.abs(co_t - t_s))] - co1[np.argmin(np.abs(co_t - t_s))]))
        zb0 = float(co0[np.argmin(np.abs(co_t - t_s)), 2])

        ax_top = axes[0, col]
        plot_proj(
            ax_top, xyz, sp, 0, 1, co0, co1, co_t, t_s,
            D[f"{k}_hx0_xy"], D[f"{k}_hy0_xy"], D[f"{k}_hx1_xy"], D[f"{k}_hy1_xy"],
            xlim, ylim_xy, is_xz=False,
            label_txt=rf"$t = {t_s:.0f}\,M$" "\n" rf"($N_{{\rm live}}={len(xyz)},\; d_{{AB}}={sep:.2f}M$)",
        )
        ax_top.tick_params(labelbottom=False)
        if col == 0:
            ax_top.set_ylabel(r"$y\,[M]$")
            ax_top.legend(loc="lower right", fontsize=6.4, markerscale=3.0, frameon=False)
        else:
            ax_top.tick_params(labelleft=False)

        ax_bot = axes[1, col]
        plot_proj(
            ax_bot, xyz, sp, 0, 2, co0, co1, co_t, t_s,
            D[f"{k}_hx0_xz"], D[f"{k}_hz0_xz"], D[f"{k}_hx1_xz"], D[f"{k}_hz1_xz"],
            xlim, zlim_xz, is_xz=True,
            label_txt=rf"$z_{{\rm BH,0}} = {zb0:+.2f}\,M$",
        )
        ax_bot.set_xlabel(r"$x\,[M]$")
        if col == 0:
            ax_bot.set_ylabel(r"$z\,[M]$")
        else:
            ax_bot.tick_params(labelleft=False)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
