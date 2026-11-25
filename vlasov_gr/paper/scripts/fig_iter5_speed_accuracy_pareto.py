#!/usr/bin/env python3
"""Iteration 5 speed-accuracy Pareto & profiling figure on NVIDIA B200.

Reads `speed_profile_cfl.npz`, `iter5_speed_verify.npz`, `iter4_stagea_curves.npz`,
plus the ST central-lapse and momentum time series of `st10k_rk3_040_dir4c_s2`, saves a
self-contained reduced archive `vlasov_gr/paper/data/iter5_pareto_curves.npz`, and
renders `vlasov_gr/paper/figures/fig_iter5_speed_accuracy_pareto.{pdf,png}`.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PAPER_DIR, "data")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_iter5_speed_accuracy_pareto")
DATA_OUT = os.path.join(DATA_DIR, "iter5_pareto_curves.npz")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)


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


def downsample_series(x, y, max_pts=450):
    stride = max(1, len(x) // max_pts)
    xs, ys = x[::stride], y[::stride]
    if xs[-1] != x[-1]:
        xs = np.append(xs, x[-1])
        ys = np.append(ys, y[-1])
    return xs.astype(np.float64), ys.astype(np.float64)


def build_data() -> dict:
    sp = dict(np.load(os.path.join(DATA_DIR, "speed_profile_cfl.npz"), allow_pickle=False))
    i5 = dict(np.load(os.path.join(DATA_DIR, "iter5_speed_verify.npz"), allow_pickle=False))
    i4s = dict(np.load(os.path.join(DATA_DIR, "iter4_stagea_curves.npz"), allow_pickle=False))

    out = {}
    out.update(sp)
    out.update(i5)
    for k in ("st_quin_stgA_t", "st_quin_stgA_ac", "st_quin_stgA_wall",
              "st_quin_stgA_t_AH", "st_quin_stgA_M_AH", "st_quin_stgA_pt", "st_quin_stgA_pnorm"):
        if k in i4s:
            out[k] = i4s[k]

    st_hst = os.path.join(
        SCRATCH, "runs", "iter5_speed_verify",
        "st10k_rk3_040_dir4c_s2", "st10k_rk3_040_dir4c_s2.nrpic.hst"
    )
    if os.path.exists(st_hst):
        nh = safe_loadtxt(st_hst)
        ts, acs = downsample_series(nh[:, 0], nh[:, 12])
        m0 = max(float(nh[0, 3]), 1.0e-30)
        pmag = np.sqrt(nh[:, 5] ** 2 + nh[:, 6] ** 2 + nh[:, 7] ** 2) / m0
        pts, ps = downsample_series(nh[:, 0], pmag)
        out["st5_t"] = ts
        out["st5_ac"] = acs
        out["st5_pt"] = pts
        out["st5_pnorm"] = ps

    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def main():
    cz.use_style()
    D = build_data()

    fig, axes = plt.subplots(2, 2, figsize=(8.1, 6.0))
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.095, top=0.955, wspace=0.28, hspace=0.34)

    # ------------------------------------------------------------------
    # Top-Left: M4 Kerr 6-level SMR speedup & B200 per-cycle filter share
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    kerr_names = [
        "Dir. mcons\n" r"($n_{\rm f}=2$, Iter 4)",
        "Unsplit mcons\n" r"($n_{\rm f}=2$, Iter 5a)",
        "Unsplit mcons\n" r"($n_{\rm f}=1$, Iter 5a)",
    ]
    kerr_walls = [
        209.3,
        float(D["m4_uns_nf2_wall"]),
        float(D["m4_uns_nf1_wall"]),
    ]
    cols_tl = ["0.55", cz.PAL["blue"], cz.PAL["red"]]
    x_pos = np.arange(len(kerr_walls))
    bars = ax.bar(x_pos, kerr_walls, width=0.55, color=cols_tl, edgecolor="k", linewidth=0.7)
    for b, w in zip(bars, kerr_walls):
        sp = 209.3 / w
        ax.text(b.get_x() + 0.5 * b.get_width(), w + 5.0,
                f"{w:.1f} s\n({sp:.2f}" r"$\times$)",
                ha="center", va="bottom", fontsize=6.5, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(kerr_names, fontsize=6.4)
    ax.set_ylim(0.0, 265.0)
    ax.set_ylabel(r"M4 Kerr $t=200M$ wall time $[\mathrm{s}]$")
    ax.text(0.96, 0.94,
            "6-lvl SMR (1128 blocks, quintic)\n"
            r"Dir. filter share: $58.6\%$ of cycle" "\n"
            r"$|\Delta E/E_0|_{\rm med} = 3.38\times 10^{-10}$ (all 3)" "\n"
            r"Mass drift $\leq 9.8\times 10^{-16}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.0, color="0.20")

    # ------------------------------------------------------------------
    # Top-Right: OS R0=5M CFL & RK3+Multirate Scaling
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    cfl_rk4 = np.array([0.25, 0.35, 0.40, 0.45, 0.50])
    w_rk4 = np.array([float(D[f"cfl_rk4_{s}_wall"]) for s in ("025", "035", "04", "045", "05")])
    cfl_rk3 = np.array([0.25, 0.35, 0.40, 0.45])
    w_rk3 = np.array([float(D[f"cfl_rk3_{s}_wall"]) for s in ("025", "035", "04", "045")])

    ax.plot(cfl_rk4, w_rk4, "s--", color=cz.PAL["blue"], lw=1.55, ms=5.5,
            label=r"RK4 ($\nu_{\rm CFL} \leq 0.50$)")
    ax.plot(cfl_rk3, w_rk3, "o-", color=cz.PAL["green"], lw=1.65, ms=5.8,
            label=r"RK3 + Dir ($K_m=1$)")
    # Unstable marker for rk3 cfl=0.50
    ax.plot([0.50], [65.5], "X", color="0.35", ms=7.2, label=r"RK3 $\nu=0.50$ unstable")

    # Iter 5b multirate points on RK3
    cfl_mr = np.array([0.40, 0.45])
    w_dir_s2 = np.array([float(D["os10k_rk3_040_dir1_s2_wall"]),
                         float(D["os10k_rk3_045_dir1_s2_wall"])])
    w_uns_s2 = np.array([float(D["os10k_rk3_040_uns1_s2_wall"]),
                         float(D["os10k_rk3_045_uns1_s2_wall"])])
    ax.plot(cfl_mr, w_dir_s2, "D-", color=cz.PAL["orange"], lw=1.5, ms=5.6,
            label=r"RK3 + Dir ($K_m=2$)")
    ax.plot(cfl_mr, w_uns_s2, "^-", color=cz.PAL["red"], lw=1.5, ms=6.2,
            label=r"RK3 + Unsplit ($K_m=2$)")

    ax.annotate(f"{float(D['os10k_rk3_045_dir1_s2_wall']):.1f} s (2.75" r"$\times$)",
                xy=(0.45, w_dir_s2[1]), xytext=(0.355, 42.0),
                fontsize=6.2, color=cz.PAL["orange"], ha="center",
                arrowprops=dict(arrowstyle="->", color=cz.PAL["orange"], lw=0.9))
    ax.set_xlim(0.23, 0.52)
    ax.set_ylim(30.0, 180.0)
    ax.set_xlabel(r"Courant number $\nu_{\rm CFL}$")
    ax.set_ylabel(r"OS $10^4$ collapse wall time $[\mathrm{s}]$")
    ax.legend(loc="upper right", fontsize=5.8, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Left: OS 10^4 & 10^5 Pareto Frontier (Wall Time vs Horizon Mass Err)
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    pts_10k = [
        ("os10k_rk4_025_dir1",    "s", "0.40",        r"$10^4$ Iter 4 RK4 (0.25)"),
        ("os10k_rk3_040_dir1_s1", "o", cz.PAL["blue"], r"$10^4$ RK3+Dir (0.40, $K_m=1$)"),
        ("os10k_rk3_040_dir1_s2", "D", cz.PAL["green"], r"$10^4$ RK3+Dir (0.40, $K_m=2$)"),
        ("os10k_rk3_040_dir1_s4", "P", cz.PAL["orange"], r"$10^4$ RK3+Dir (0.40, $K_m=4$)"),
        ("os10k_rk3_045_dir1_s2", "*", "#8E24AA", r"$10^4$ RK3+Dir (0.45, $K_m=2$)"),
    ]
    pts_100k = [
        ("os100k_rk4_025_dir_s1",  "s", "k",           r"$10^5$ Iter 4 RK4 (0.25)"),
        ("os100k_rk3_040_dir1_s2", "o", cz.PAL["red"], r"$10^5$ RK3+Dir (0.40, $K_m=2$)"),
        ("os100k_rk3_040_uns3_s2", "^", "#008B8B",     r"$10^5$ RK3+Uns$_3$ (0.40, $K_m=2$)"),
        ("os100k_rk3_040_dir1_s4", "D", "#D48800",     r"$10^5$ RK3+Dir (0.40, $K_m=4$)"),
    ]
    for key, mk, col, lab in pts_10k:
        w = float(D[f"{key}_wall"])
        merr = max(abs(float(D[f"{key}_M_AH"]) - 1.0), 1.0e-5)
        ax.semilogy([w], [merr], marker=mk, color=col, ms=6.2 if mk != "*" else 8.0,
                    ls="none", mec="k", mew=0.45, label=lab)
    for key, mk, col, lab in pts_100k:
        w = float(D[f"{key}_wall"])
        merr = max(abs(float(D[f"{key}_M_AH"]) - 1.0), 1.0e-5)
        ax.semilogy([w], [merr], marker=mk, color=col, ms=6.5, ls="none",
                    mec="k", mew=0.7, fillstyle="full", label=lab)

    # Highlight 100k speedup arrow
    w100_0 = float(D["os100k_rk4_025_dir_s1_wall"])
    m100_0 = abs(float(D["os100k_rk4_025_dir_s1_M_AH"]) - 1.0)
    w100_u = float(D["os100k_rk3_040_uns3_s2_wall"])
    m100_u = abs(float(D["os100k_rk3_040_uns3_s2_M_AH"]) - 1.0)
    ax.annotate("", xy=(w100_u, m100_u), xytext=(w100_0, m100_0),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0, ls="--"))
    ax.text(0.5 * (w100_0 + w100_u), 6.2e-4, r"$2.24\times$ faster ($10^5$)",
            ha="center", va="top", fontsize=6.1, color="0.25")

    ax.set_xlim(48.0, 195.0)
    ax.set_ylim(2.0e-4, 3.5e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"OS collapse $t=25M$ wall time $[\mathrm{s}]$")
    ax.set_ylabel(r"Horizon mass error $|M_{\rm AH}/M_0 - 1|$")
    ax.legend(loc="upper right", ncol=2, columnspacing=0.6, fontsize=5.15, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Right: ST yc=0.500 9-level AMR (Iter 4 vs Iter 5b)
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    ax.plot(D["st_quin_stgA_t"], D["st_quin_stgA_ac"], "--", color=cz.PAL["blue"], lw=1.55,
            label=rf"Iter 4 RK4 (754.5 s, $M_{{\rm AH}}={float(D['st_quin_stgA_M_AH']):.5f}M$)")
    if "st5_t" in D:
        ax.plot(D["st5_t"], D["st5_ac"], "-", color=cz.PAL["red"], lw=1.65,
                label=rf"Iter 5 RK3+$K_m=2$ (314.7 s, $M_{{\rm AH}}={float(D['st10k_rk3_040_dir4c_s2_M_AH']):.5f}M$)")
    tah4 = float(D["st_quin_stgA_t_AH"])
    tah5 = float(D["st10k_rk3_040_dir4c_s2_t_AH"])
    ax.plot([tah4, tah4], [-0.03, 0.52], color=cz.PAL["blue"], ls=":", lw=1.0, alpha=0.65)
    ax.plot([tah5, tah5], [-0.03, 0.52], color=cz.PAL["red"], ls=":", lw=1.0, alpha=0.75)

    ax.text(0.04, 0.24,
            "ST $y_c=0.500$ ($10^4$ Anti QMC, 9-lvl AMR):\n"
            r"$754.5\,\mathrm{s} \to 314.7\,\mathrm{s}$ ($2.40\times$ speedup)" "\n"
            r"$|\mathbf{P}|/M_0$: $1.43\times 10^{-14} \to 3.93\times 10^{-15}$" "\n"
            r"Filter mass drift $= 9.25\times 10^{-16}$",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=5.9, color="0.20")
    ax.set_xlim(0.0, 90.0)
    ax.set_ylim(-0.03, 0.65)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.legend(loc="lower left", fontsize=5.6, frameon=False)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
