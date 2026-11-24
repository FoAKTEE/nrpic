#!/usr/bin/env python3
"""Physics figure: Shapiro-Teukolsky relativistic cluster four physical fates & N-convergence.

Reduces Wave 4B M5c datasets into `vlasov_gr/paper/data/physics_st_fates.npz`
and renders `vlasov_gr/paper/figures/fig_physics_st_four_fates.{pdf,png}`.
"""
import glob
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/analysis")
import czstyle as cz  # noqa: E402
from nrpic.vlasov_gr import read_grlbv  # noqa: E402
from diag.common import read_snapshot  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_st_fates.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_st_four_fates")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
M5C_BASE = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5c")


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


def weighted_r50(r: np.ndarray, m: np.ndarray) -> float:
    if len(r) == 0:
        return np.nan
    idx = np.argsort(r)
    rs = r[idx]
    ms = np.maximum(m[idx], 0.0)
    mtot = float(np.sum(ms))
    if mtot <= 0.0:
        return float(np.median(rs))
    cdf = np.cumsum(ms) / mtot
    return float(rs[np.searchsorted(cdf, 0.5)])


def extract_r50_series(run_dir: str, prefix: str, is_hyb: bool):
    times, r50s = [], []
    if is_hyb:
        files = sorted(glob.glob(os.path.join(run_dir, f"{prefix}.vlasov.*.bin")))
        for f in files:
            s = read_grlbv(f)
            x = s["x"]
            m = s["m"]
            r = np.linalg.norm(x, axis=1)
            times.append(float(s["time"]))
            r50s.append(weighted_r50(r, m))
    else:
        files = sorted(glob.glob(os.path.join(run_dir, f"{prefix}.part.*.bin")))
        for f in files:
            t, d, _, _ = read_snapshot(f)
            if len(d) == 0:
                continue
            r = np.linalg.norm(d[:, :3], axis=1)
            times.append(float(t))
            r50s.append(weighted_r50(r, d[:, 6]))
    return np.asarray(times, dtype=np.float64), np.asarray(r50s, dtype=np.float64)


def build_npz() -> dict:
    out = {}
    runs = [
        ("st_yc0819_vp01_100k_hyb", True),
        ("st_yc0819_vp01_10k_anti", True),
        ("st_yc0819_vp01_10k_mid",  False),
        ("st_yc0500_mig_10k_hyb",   True),
        ("st_yc0500_mig_10k_mid",   False),
        ("st_yc0500_vp01_100k_hyb", True),
        ("st_yc0500_vp01_100k_mid", False),
        ("st_yc0500_vp01_10k_hyb",  True),
        ("st_yc0500_vp01_10k_mid",  False),
        ("st_yc0605_vp01_10k_hyb",  True),
        ("st_yc0605_vp01_10k_mid",  False),
        ("st_yc0756_dp10_10k_hyb",  True),
        ("st_yc0756_dp10_10k_mid",  False),
        ("st_yc0283_vp01_100k_hyb", True),
        ("st_yc0283_vp01_100k_mid", False),
    ]
    for lbl, is_hyb in runs:
        rdir = os.path.join(M5C_BASE, lbl)
        nh = safe_loadtxt(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        stride = max(1, len(nh) // 450)
        nh_s = nh[::stride]
        t_h = nh_s[:, 0]
        m0 = max(float(nh[0, 3]), 1e-30)
        p_norm = np.sqrt(nh_s[:, 5]**2 + nh_s[:, 6]**2 + nh_s[:, 7]**2) / m0
        out[f"{lbl}_t"] = t_h
        out[f"{lbl}_ac"] = nh_s[:, 12]
        out[f"{lbl}_P"] = p_norm

        tr, r5 = extract_r50_series(rdir, lbl, is_hyb)
        out[f"{lbl}_r50_t"] = tr
        out[f"{lbl}_r50"] = r5

        ahp = os.path.join(rdir, f"{lbl}.horizon_summary_0.txt")
        if os.path.isfile(ahp):
            ah = safe_loadtxt(ahp)
            ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
            if len(ah):
                out[f"{lbl}_tah"] = np.float64(ah[0, 1])
                out[f"{lbl}_mah"] = np.float64(ah[-1, 2])

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def main():
    cz.use_style()
    D = build_npz()

    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.8))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.095, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: Central lapse alpha_c(t) spanning all 4 fates
    ax = axes[0, 0]
    fate_specs = [
        ("st_yc0819_vp01_100k_hyb", cz.PAL["blue"],   "-",  r"Stable ($y_c=0.819$, $10^5$)"),
        ("st_yc0500_mig_10k_hyb",   cz.PAL["orange"], "-",  r"Migrate ($y_c=0.500$ mig)"),
        ("st_yc0283_vp01_100k_hyb", cz.PAL["green"],  "-",  r"Disperse ($y_c=0.283$, $10^5$)"),
        ("st_yc0605_vp01_10k_hyb",  cz.PAL["red"],    "--", r"Collapse ($y_c=0.605$, $10^4$)"),
        ("st_yc0500_vp01_100k_hyb", "0.20",           "-",  r"Collapse ($y_c=0.500$, $10^5$)"),
    ]
    for lbl, col, ls, leg in fate_specs:
        ax.plot(D[f"{lbl}_t"], D[f"{lbl}_ac"], color=col, ls=ls, lw=1.45, label=leg)
    ax.set_xlim(0.0, 300.0)
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.legend(loc="center right", bbox_to_anchor=(0.98, 0.56), fontsize=6.5, frameon=False)

    # Top-Right: Snapshot half-mass radius r_50(t) across all 4 regimes
    ax = axes[0, 1]
    r50_specs = [
        ("st_yc0283_vp01_100k_hyb", cz.PAL["green"],  "o-",  r"Disperse ($0.283 \to 76.9M$)"),
        ("st_yc0500_mig_10k_hyb",   cz.PAL["orange"], "s-",  r"Migrate ($0.500 \to 9.78M$)"),
        ("st_yc0819_vp01_100k_hyb", cz.PAL["blue"],   "^-",  r"Stable ($0.819 \to 5.79M$)"),
        ("st_yc0605_vp01_10k_hyb",  cz.PAL["red"],    "D--", r"Collapse ($0.605$, excised)"),
        ("st_yc0500_vp01_100k_hyb", "0.20",           "v-",  r"Collapse ($0.500$, excised)"),
    ]
    for lbl, col, fmt, leg in r50_specs:
        tr = D[f"{lbl}_r50_t"]
        rr = D[f"{lbl}_r50"]
        if len(tr):
            ax.semilogy(tr, rr, fmt, color=col, ms=4.2, lw=1.4, label=leg)
    ax.set_xlim(-8.0, 308.0)
    ax.set_ylim(0.70, 160.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Live-matter half-mass radius $r_{50}\,[M]$")
    ax.legend(loc="lower right", fontsize=6.1, frameon=False, labelspacing=0.20)

    # Bottom-Left: Total momentum / COM symmetry preservation |P(t)|/M_0
    ax = axes[1, 0]
    mom_specs = [
        ("st_yc0500_vp01_10k_mid",  cz.PAL["blue"],   "--", r"$y_c=0.500$, $10^4$ MC"),
        ("st_yc0500_vp01_100k_mid", cz.PAL["green"],  "--", r"$y_c=0.500$, $10^5$ MC"),
        ("st_yc0819_vp01_10k_mid",  cz.PAL["orange"], ":",  r"$y_c=0.819$, $10^4$ MC"),
        ("st_yc0500_vp01_100k_hyb", "0.20",           "-",  r"$y_c=0.500$, $10^5$ Anti QMC (AMR)"),
        ("st_yc0500_mig_10k_hyb",   cz.PAL["red"],    "-",  r"$y_c=0.500$ mig, $10^4$ Anti QMC"),
        ("st_yc0819_vp01_10k_anti", "#9467BD",        "-",  r"$y_c=0.819$, $10^4$ Anti QMC"),
    ]
    for lbl, col, ls, leg in mom_specs:
        t = D[f"{lbl}_t"]
        p = np.maximum(D[f"{lbl}_P"], 1.0e-18)
        ax.semilogy(t[1:], p[1:], color=col, ls=ls, lw=1.35, label=leg)
    ax.set_xlim(0.0, 300.0)
    ax.set_ylim(1.0e-18, 2.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Linear momentum drift $|\mathbf{P}|/M_0$")
    ax.legend(loc="center right", bbox_to_anchor=(0.985, 0.44), ncol=1, fontsize=6.1, frameon=False)

    # Bottom-Right: Collapse-time t_AH accuracy (MC vs Antipodal QMC) & final M_AH/M
    ax = axes[1, 1]
    cases = [
        ("y_c=0.500\n10k",  "st_yc0500_vp01_10k_mid",  "st_yc0500_vp01_10k_hyb"),
        ("y_c=0.500\n100k", "st_yc0500_vp01_100k_mid", "st_yc0500_vp01_100k_hyb"),
        ("y_c=0.605\n10k",  "st_yc0605_vp01_10k_mid",  "st_yc0605_vp01_10k_hyb"),
        ("y_c=0.756\n10k",  "st_yc0756_dp10_10k_mid",  "st_yc0756_dp10_10k_hyb"),
    ]
    x = np.arange(len(cases))
    w = 0.36
    off = 0.205
    t_mid = [float(D[f"{m}_tah"]) for _, m, _ in cases]
    t_hyb = [float(D[f"{h}_tah"]) for _, _, h in cases]
    m_mid = [float(D[f"{m}_mah"]) for _, m, _ in cases]
    m_hyb = [float(D[f"{h}_mah"]) for _, _, h in cases]

    ax.bar(x - off, t_mid, width=w, color=cz.PAL["blue"], alpha=0.90, label="Stratified MC + Mid")
    ax.bar(x + off, t_hyb, width=w, color=cz.PAL["red"],  alpha=0.90, label="Antipodal QMC + GL4")
    for xi, tm, th, mm, mh in zip(x, t_mid, t_hyb, m_mid, m_hyb):
        ax.text(xi - off, tm + 3.0, f"{tm:.1f}", ha="center", va="bottom", fontsize=6.2, color=cz.PAL["blue"])
        ax.text(xi + off, th + 3.0, f"{th:.1f}", ha="center", va="bottom", fontsize=6.2, color=cz.PAL["red"])
        ax.text(xi - off, 0.50 * tm, f"{mm:.3f}", ha="center", va="center", rotation=90,
                fontsize=6.2, color="white", fontweight="bold")
        ax.text(xi + off, 0.50 * th, f"{mh:.3f}", ha="center", va="center", rotation=90,
                fontsize=6.2, color="white", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([r"$y_c=0.50$" "\n" r"$10^4$", r"$y_c=0.50$" "\n" r"$10^5$",
                        r"$y_c=0.61$" "\n" r"$10^4$", r"$y_c=0.76$" "\n" r"$10^4$"], fontsize=8.0)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.58, 3.58)
    ax.set_ylim(0.0, 232.0)
    ax.set_ylabel(r"Horizon formation time $t_{\rm AH}\,[M]$")
    ax.legend(loc="upper left", fontsize=6.5, frameon=False)
    ax.text(0.04, 0.77, r"Inside bars: $M_{\rm AH}/M$",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.4, color="0.25")

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
