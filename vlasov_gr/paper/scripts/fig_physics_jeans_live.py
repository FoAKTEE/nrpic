#!/usr/bin/env python3
"""Physics & diagnostic figure: Live 8-level AMR Jeans binary black hole formation and inspiral.

Safely reduces live outputs in `$SCRATCH/runs/repro_wave4c/jeans_10k_strat_mid/`
into `vlasov_gr/paper/data/physics_jeans_live.npz` and renders
`vlasov_gr/paper/figures/fig_physics_jeans_live.{pdf,png}`.
"""
from math import factorial
import glob
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
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_jeans_live.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_jeans_live")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
JDIR = os.path.join(SCRATCH, "runs", "repro_wave4c", "jeans_10k_strat_mid")
PREF = "jeans_10k_strat_mid"
QDIR = os.path.join(SCRATCH, "runs", "repro_wave4c", "jeans_10k_qmc_hyb")
QPREF = "jeans_10k_qmc_hyb"


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
    return cx + rr * np.cos(phi), cy + rr * np.sin(phi)


def split_species(d, tag, sp):
    if len(sp) and np.max(sp) >= 2:
        return sp
    out = np.zeros(len(tag), dtype=np.int32)
    out[(tag >= 6000) & (tag < 8000)] = 1
    out[tag >= 8000] = 2
    return out


def build_npz() -> dict:
    p_files = sorted(glob.glob(os.path.join(JDIR, f"{PREF}.part.*.bin")))
    # Use t=5.0M or t=10.0M for early clump collapse, and latest complete snapshot for late inspiral
    early_file = p_files[min(2, len(p_files) - 1)]  # part.00002.bin (t=10.0M)
    late_file = p_files[-1]

    t_e, d_e, tag_e, sp_e = read_snapshot(early_file)
    t_l, d_l, tag_l, sp_l = read_snapshot(late_file)
    sp_e = split_species(d_e, tag_e, sp_e)
    sp_l = split_species(d_l, tag_l, sp_l)

    co0 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.co_0.txt"))
    co1 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.co_1.txt"))
    n_co = min(len(co0), len(co1))
    co0, co1 = co0[:n_co], co1[:n_co]
    stride_c = max(1, n_co // 450)
    co0s, co1s = co0[::stride_c], co1[::stride_c]
    # Keep final point
    if co0s[-1, 1] != co0[-1, 1]:
        co0s = np.vstack([co0s, co0[-1:]])
        co1s = np.vstack([co1s, co1[-1:]])

    ah0 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.horizon_summary_0.txt"))
    ah1 = safe_loadtxt(os.path.join(JDIR, f"{PREF}.horizon_summary_1.txt"))
    ah0 = ah0[np.isfinite(ah0[:, 2])] if len(ah0) else ah0
    ah1 = ah1[np.isfinite(ah1[:, 2])] if len(ah1) else ah1

    sh0 = read_shapes(os.path.join(JDIR, f"{PREF}.horizon_shape_0.txt"))
    sh1 = read_shapes(os.path.join(JDIR, f"{PREF}.horizon_shape_1.txt"))

    def bh_at(co, t):
        k = int(np.argmin(np.abs(co[:, 1] - t)))
        return float(co[k, 2]), float(co[k, 3])

    hx0_l, hy0_l = eq_outline(sh0, t_l, *bh_at(co0, t_l))
    hx1_l, hy1_l = eq_outline(sh1, t_l, *bh_at(co1, t_l))

    nh = safe_loadtxt(os.path.join(JDIR, f"{PREF}.nrpic.hst"))
    zh = safe_loadtxt(os.path.join(JDIR, f"{PREF}.z4c.user.hst"))
    str_n = max(1, len(nh) // 450)
    nh_s = nh[::str_n]

    out = {
        "t_e": np.float64(t_e),
        "xy_e": d_e[:, :2].astype(np.float32),
        "sp_e": sp_e.astype(np.int8),
        "t_l": np.float64(t_l),
        "xy_l": d_l[:, :2].astype(np.float32),
        "sp_l": sp_l.astype(np.int8),
        "co_t": co0s[:, 1],
        "co0_xyz": co0s[:, 2:5],
        "co1_xyz": co1s[:, 2:5],
        "hx0_l": hx0_l, "hy0_l": hy0_l,
        "hx1_l": hx1_l, "hy1_l": hy1_l,
        "ah0_t": ah0[:, 1] if len(ah0) else np.array([]),
        "ah0_M": ah0[:, 2] if len(ah0) else np.array([]),
        "ah1_t": ah1[:, 1] if len(ah1) else np.array([]),
        "ah1_M": ah1[:, 2] if len(ah1) else np.array([]),
        "nh_t": nh_s[:, 0],
        "nh_mexc": nh_s[:, 17] / max(float(nh[0, 3]), 1e-30),
        "nh_amin": nh_s[:, 15],
        "zh_t": zh[:, 0] if len(zh) else np.array([]),
        "zh_H": np.sqrt(np.maximum(zh[:, 3], 1e-24)) if len(zh) else np.array([]),
    }
    if os.path.isfile(os.path.join(QDIR, f"{QPREF}.co_0.txt")):
        qco0 = safe_loadtxt(os.path.join(QDIR, f"{QPREF}.co_0.txt"))
        qco1 = safe_loadtxt(os.path.join(QDIR, f"{QPREF}.co_1.txt"))
        nq = min(len(qco0), len(qco1))
        qco0, qco1 = qco0[:nq], qco1[:nq]
        qstr = max(1, nq // 250)
        qco0s, qco1s = qco0[::qstr], qco1[::qstr]
        qah0 = safe_loadtxt(os.path.join(QDIR, f"{QPREF}.horizon_summary_0.txt"))
        qah1 = safe_loadtxt(os.path.join(QDIR, f"{QPREF}.horizon_summary_1.txt"))
        qah0 = qah0[np.isfinite(qah0[:, 2])] if len(qah0) else qah0
        qah1 = qah1[np.isfinite(qah1[:, 2])] if len(qah1) else qah1
        qnh = safe_loadtxt(os.path.join(QDIR, f"{QPREF}.nrpic.hst"))
        qstr_n = max(1, len(qnh) // 250)
        qnh_s = qnh[::qstr_n]
        out.update({
            "q_co_t": qco0s[:, 1],
            "q_co0_xyz": qco0s[:, 2:5],
            "q_co1_xyz": qco1s[:, 2:5],
            "q_ah0_t": qah0[:, 1] if len(qah0) else np.array([]),
            "q_ah0_M": qah0[:, 2] if len(qah0) else np.array([]),
            "q_ah1_t": qah1[:, 1] if len(qah1) else np.array([]),
            "q_ah1_M": qah1[:, 2] if len(qah1) else np.array([]),
            "q_nh_t": qnh_s[:, 0],
            "q_nh_mexc": qnh_s[:, 17] / max(float(qnh[0, 3]), 1e-30),
            "q_nh_amin": qnh_s[:, 15],
        })
        qfilt = np.max(np.abs(qnh[:, 23] - qnh[:, 8]) / np.maximum(np.abs(qnh[:, 8]), 1e-30))
        qm0 = float(qnh[0, 3])
        qp = np.max(np.linalg.norm(qnh[:, 5:8], axis=1)) / max(qm0, 1e-30)
        print(f"QMC overlay: t_end={qnh[-1,0]:.3f} filt_max={qfilt:.3e} max|P|/M0={qp:.3e} "
              f"ah0=[{qah0[0,1]:.4f}..{qah0[-1,1]:.4f}, M={qah0[0,2]:.5f}..{qah0[-1,2]:.5f}] "
              f"ah1=[{qah1[0,1]:.4f}..{qah1[-1,1]:.4f}, M={qah1[0,2]:.5f}..{qah1[-1,2]:.5f}]", flush=True)
    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB), t_e={t_e:.2f}, t_l={t_l:.2f}", flush=True)
    return out


def plot_orbit_snapshot(ax, xy, sp, L, title_txt, co0=None, co1=None, hx0=None, hy0=None, hx1=None, hy1=None, t_max=None):
    env = sp == 0
    cA = sp == 1
    cB = sp == 2
    ax.scatter(xy[env, 0], xy[env, 1], s=0.9, c="0.62", alpha=0.38, linewidths=0, rasterized=True, label="Envelope")
    if np.any(cA):
        ax.scatter(xy[cA, 0], xy[cA, 1], s=1.4, c=cz.PAL["blue"], alpha=0.58, linewidths=0, rasterized=True, label="Clump A")
    if np.any(cB):
        ax.scatter(xy[cB, 0], xy[cB, 1], s=1.4, c=cz.PAL["red"], alpha=0.58, linewidths=0, rasterized=True, label="Clump B")
    if co0 is not None and t_max is not None:
        m0 = co0["t"] <= t_max
        ax.plot(co0["xyz"][m0, 0], co0["xyz"][m0, 1], color=cz.PAL["blue"], lw=1.4, zorder=4)
        ax.plot(co1["xyz"][m0, 0], co1["xyz"][m0, 1], color=cz.PAL["red"], lw=1.4, zorder=4)
        k = int(np.argmin(np.abs(co0["t"] - t_max)))
        ax.plot([co0["xyz"][k, 0]], [co0["xyz"][k, 1]], "o", color=cz.PAL["blue"], mec="k", mew=0.6, ms=4.2, zorder=5)
        ax.plot([co1["xyz"][k, 0]], [co1["xyz"][k, 1]], "o", color=cz.PAL["red"], mec="k", mew=0.6, ms=4.2, zorder=5)
    if hx0 is not None and len(hx0):
        ax.plot(hx0, hy0, color="k", lw=1.1, zorder=6)
        ax.plot(hx1, hy1, color="k", lw=1.1, zorder=6)
    ax.text(0.05, 0.94, title_txt, transform=ax.transAxes, ha="left", va="top", fontsize=7.6)
    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$")


def main():
    cz.use_style()
    D = build_npz()

    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.2))
    fig.subplots_adjust(left=0.09, right=0.91, bottom=0.085, top=0.955, wspace=0.50, hspace=0.30)

    t_e = float(D["t_e"])
    t_l = float(D["t_l"])
    co_pack0 = {"t": D["co_t"], "xyz": D["co0_xyz"]}
    co_pack1 = {"t": D["co_t"], "xyz": D["co1_xyz"]}

    # Top-Left: Early clump collapse snapshot (t_e ~ 10M)
    ax = axes[0, 0]
    plot_orbit_snapshot(
        ax, D["xy_e"], D["sp_e"], 14.0,
        rf"Clump collapse $t={t_e:.1f}\,M$" "\n" rf"($N_{{\rm live}}={len(D['xy_e'])}$)",
        co0=co_pack0, co1=co_pack1, t_max=t_e,
    )
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="lower right", fontsize=6.4, markerscale=3.2, frameon=False)

    # Top-Right: Live binary BH inspiral + AH outlines (t_l)
    ax = axes[0, 1]
    plot_orbit_snapshot(
        ax, D["xy_l"], D["sp_l"], 11.5,
        rf"Binary BH orbit $t={t_l:.1f}\,M$" "\n" rf"($N_{{\rm live}}={len(D['xy_l'])}$)",
        co0=co_pack0, co1=co_pack1,
        hx0=D["hx0_l"], hy0=D["hy0_l"],
        hx1=D["hx1_l"], hy1=D["hy1_l"],
        t_max=t_l,
    )
    ax.set_ylabel(r"$y\,[M]$")

    # Bottom-Left: Binary separation d_AB(t) and MC out-of-plane vertical kick |z_BH(t)|
    ax = axes[1, 0]
    tc = D["co_t"]
    sep = np.linalg.norm(D["co0_xyz"] - D["co1_xyz"], axis=1)
    h_sep = []
    l1, = ax.plot(tc, sep, color=cz.PAL["blue"], lw=1.5, label=r"MC+Mid $d_{AB}$")
    h_sep.append(l1)
    if "q_co_t" in D and len(D["q_co_t"]):
        qsep = np.linalg.norm(D["q_co0_xyz"] - D["q_co1_xyz"], axis=1)
        lq, = ax.plot(D["q_co_t"], qsep, color="0.12", lw=1.45, ls="--", zorder=5,
                      label=r"QMC+GL4 $d_{AB}$")
        h_sep.append(lq)
    ax.set_xlim(0.0, max(36.0, float(tc[-1]) * 1.02))
    ax.set_ylim(0.0, 6.8)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Binary separation $d_{AB}\,[M]$", color=cz.PAL["blue"])
    ax.tick_params(axis="y", labelcolor=cz.PAL["blue"])

    ax2 = ax.twinx()
    l2, = ax2.plot(tc, np.abs(D["co0_xyz"][:, 2]), color=cz.PAL["red"], lw=1.35, ls="-", label=r"MC kick $|z_0|$")
    l3, = ax2.plot(tc, np.abs(D["co1_xyz"][:, 2]), color=cz.PAL["orange"], lw=1.35, ls="--", label=r"MC kick $|z_1|$")
    h_sep.extend([l2, l3])
    ax2.set_ylim(-0.02, 0.85)
    ax2.set_ylabel(r"Out-of-plane kick $|z_{\rm BH}|\,[M]$", color=cz.PAL["red"])
    ax2.tick_params(axis="y", labelcolor=cz.PAL["red"])
    ax2.tick_params(which="both", direction="in")
    ax.legend(handles=h_sep, loc="center left", bbox_to_anchor=(0.02, 0.56), fontsize=6.1, frameon=False)

    # Bottom-Right: Individual AH masses M_AH,{0,1}(t) + excised mass & min lapse
    ax = axes[1, 1]
    lines = []
    if len(D["ah0_t"]):
        lines.append(ax.plot(D["ah0_t"], D["ah0_M"], color=cz.PAL["blue"], lw=1.5, label=r"MC $M_{\rm AH,0}$")[0])
    if len(D["ah1_t"]):
        lines.append(ax.plot(D["ah1_t"], D["ah1_M"], color=cz.PAL["red"], lw=1.45, ls="--", label=r"MC $M_{\rm AH,1}$")[0])
    if "q_ah0_t" in D and len(D["q_ah0_t"]):
        lines.append(ax.plot(D["q_ah0_t"], D["q_ah0_M"], color=cz.PAL["orange"], lw=1.7, ls="-", zorder=6,
                             label=r"QMC $M_{\rm AH,0}$")[0])
    if "q_ah1_t" in D and len(D["q_ah1_t"]):
        lines.append(ax.plot(D["q_ah1_t"], D["q_ah1_M"], color="0.12", lw=1.5, ls=":", zorder=6,
                             label=r"QMC $M_{\rm AH,1}$")[0])
    ax.axhline(0.1321, color="grey", lw=0.9, ls=":", alpha=0.7)
    ax.text(float(tc[-1]) * 0.98, 0.1342, r"initial clump $m_A=0.132M$",
            ha="right", va="bottom", fontsize=6.1, color="0.35")
    ax.set_xlim(0.0, max(36.0, float(tc[-1]) * 1.02))
    ax.set_ylim(0.088, 0.212)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Apparent horizon mass $M_{\rm AH}\,[M]$")

    axr = ax.twinx()
    lines.append(axr.plot(D["nh_t"], D["nh_mexc"], color=cz.PAL["green"], lw=1.3, ls="-", label=r"$M_{\rm exc}/M_0$")[0])
    lines.append(axr.plot(D["nh_t"], D["nh_amin"], color="0.35", lw=1.2, ls=":", label=r"$\alpha_{\min}$")[0])
    axr.set_ylim(-0.04, 1.15)
    axr.set_ylabel(r"$M_{\rm exc}/M_0,\;\alpha_{\min}$", color="0.25")
    axr.tick_params(which="both", direction="in")
    ax.legend(handles=lines, loc="upper left", ncol=2, columnspacing=0.55, fontsize=5.8, frameon=False)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
