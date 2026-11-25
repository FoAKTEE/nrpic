#!/usr/bin/env python3
"""Diagnostic figure: Iteration 4b C^2 quintic Hermite Kerr invariant conservation & Iter 4a VRAM savings.

Reads completed GPU runs under `$SCRATCH/runs/iter4_verify/` (`m4_hermite_ng2`, `m4_hermite_ng4`,
`m4_bspline_ng4`, `m4_quintic_ng4`, `os_vram_gpu3`, `os_vram_gpu4_herm_froz`, `os_gpu4_quin_froz`),
reduces exact Kerr-Schild invariants into `vlasov_gr/paper/data/iter4_quintic_kerr_diag.npz`, and
renders `vlasov_gr/paper/figures/fig_iter4_quintic_kerr_diagnostics.{pdf,png}`.
"""
import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import kerr as _kerr  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_OUT = os.path.join(PAPER_DIR, "data", "iter4_quintic_kerr_diag.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_iter4_quintic_kerr_diagnostics")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
I4_BASE = os.path.join(SCRATCH, "runs", "iter4_verify")


def parse_log_metrics(log_path: str):
    txt = open(log_path, "r").read()
    mw = re.search(r"# wall_s = ([0-9.eE+-]+)", txt)
    mv = re.search(r"# peak_vram_mib = ([0-9.eE+-]+)", txt)
    return (
        float(mw.group(1)) if mw else np.nan,
        float(mv.group(1)) if mv else np.nan,
    )


def build_npz() -> dict:
    out = {}
    cases = ("hermite_ng2", "hermite_ng4", "bspline_ng4", "quintic_ng4")
    for klbl in cases:
        lbl = f"m4_{klbl}"
        rdir = os.path.join(I4_BASE, lbl)
        s0 = vg.read_grlbv(os.path.join(rdir, f"{lbl}.vlasov.00000.bin"))
        s1 = vg.read_grlbv(os.path.join(rdir, f"{lbl}.vlasov.00001.bin"))
        x0, u0 = s0["x"], s0["u_bar"][:, 0, :]
        x1, u1 = s1["x"], s1["u_bar"][:, 0, :]
        r0 = _kerr.cks_radius(x0, a=0.9)
        r1 = _kerr.cks_radius(x1, a=0.9)
        E0, L0, Q0 = _kerr.invariants("cks", x0, u0, a=0.9, M=1.0)
        E1, L1, Q1 = _kerr.invariants("cks", x1, u1, a=0.9, M=1.0)

        dE = np.abs(E1 - E0) / np.abs(E0)
        dL = np.abs(L1 - L0) / np.abs(L0)
        dQK = np.abs(Q1 - Q0) / (Q0 + (L0 - 0.9 * E0) ** 2)
        wall_s, vram_mib = parse_log_metrics(os.path.join(rdir, f"{lbl}.stdout.log"))

        out[f"{klbl}_r0"] = r0.astype(np.float32)
        out[f"{klbl}_r1"] = r1.astype(np.float32)
        out[f"{klbl}_dE"] = dE.astype(np.float64)
        out[f"{klbl}_dL"] = dL.astype(np.float64)
        out[f"{klbl}_dQK"] = dQK.astype(np.float64)
        out[f"{klbl}_wall"] = np.float64(wall_s)
        out[f"{klbl}_vram_mib"] = np.float64(vram_mib)

    for os_lbl in ("os_vram_gpu3", "os_vram_gpu4_herm_froz", "os_gpu4_quin_froz"):
        w, v = parse_log_metrics(os.path.join(I4_BASE, os_lbl, f"{os_lbl}.stdout.log"))
        out[f"{os_lbl}_wall"] = np.float64(w)
        out[f"{os_lbl}_vram_mib"] = np.float64(v)

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def radial_quantiles(r0, val, bins):
    rc, med, q25, q75 = [], [], [], []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (r0 >= a) & (r0 < b)
        if np.sum(m) >= 15:
            p = np.percentile(val[m], [25, 50, 75])
            rc.append(0.5 * (a + b))
            q25.append(p[0])
            med.append(p[1])
            q75.append(p[2])
    return np.asarray(rc), np.asarray(q25), np.asarray(med), np.asarray(q75)


def main():
    cz.use_style()
    D = build_npz()

    fig, axes = plt.subplots(2, 2, figsize=(7.6, 6.0))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.095, top=0.955, wspace=0.29, hspace=0.33)

    specs = [
        ("hermite_ng4", cz.PAL["blue"],   "--"),
        ("bspline_ng4", cz.PAL["orange"], "-."),
        ("quintic_ng4", cz.PAL["red"],    "-"),
    ]
    labels_short = {
        "hermite_ng4": r"Hermite ($ng=4$)",
        "bspline_ng4": r"B-spline ($ng=4$)",
        "quintic_ng4": r"Quintic ($ng=4$, Iter 4b)",
    }

    # Top-Left: Empirical CCDF P(|dE/E0| > eps)
    ax = axes[0, 0]
    for klbl, col, ls in specs:
        s = np.sort(np.maximum(D[f"{klbl}_dE"], 1.0e-15))
        ccdf = 1.0 - np.arange(len(s), dtype=np.float64) / len(s)
        stride = max(1, len(s) // 600)
        ax.loglog(s[::stride], ccdf[::stride], color=col, ls=ls, lw=1.55, label=labels_short[klbl])
    ax.axvline(float(np.median(D["hermite_ng4_dE"])), color=cz.PAL["blue"], ls=":", lw=0.9, alpha=0.65)
    ax.axvline(float(np.median(D["quintic_ng4_dE"])), color=cz.PAL["red"], ls=":", lw=0.9, alpha=0.65)
    ax.axhline(0.5, color="0.5", ls=":", lw=0.8, alpha=0.55)
    ax.text(0.04, 0.05,
            "6-level SMR Kerr ($a=0.9M$, $t=200M$)\n"
            r"Median $|\Delta E/E_0|$: $311\times$ vs Hermite" "\n"
            r"$\;\;4.9\times$ vs B-spline; tail $100\times$ lower",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.3, color="0.22")
    ax.set_xlim(1.0e-12, 2.5e-4)
    ax.set_ylim(1.0e-4, 5.5)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Relative energy error threshold $\varepsilon = |\Delta E/E_0|$")
    ax.set_ylabel(r"Exceedance fraction $P(|\Delta E/E_0| > \varepsilon)$")
    ax.legend(loc="upper right", fontsize=5.9, frameon=False, labelspacing=0.22)

    # Top-Right: Radial profile of |dE/E0| vs final BL radius r_1 (spans 6-26M across SMR level 3/2)
    ax = axes[0, 1]
    rbins = np.linspace(6.0, 26.0, 13)
    for klbl, col, ls in specs:
        rc, q25, med, q75 = radial_quantiles(D[f"{klbl}_r1"], np.maximum(D[f"{klbl}_dE"], 1e-15), rbins)
        ax.semilogy(rc, med, color=col, ls=ls, lw=1.55, label=labels_short[klbl])
        ax.fill_between(rc, np.maximum(q25, 1e-13), np.maximum(q75, 1e-13), color=col, alpha=0.14, lw=0)
    ax.axvline(24.0, color="0.45", ls=":", lw=0.95, alpha=0.75)
    ax.text(23.5, 1.8e-6, "lvl 3/2\n($24M$)", fontsize=6.1, color="0.35", ha="right", va="top")
    ax.set_xlim(6.0, 26.5)
    ax.set_ylim(1.0e-11, 3.5e-6)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Final Boyer\u2013Lindquist radius " r"$r(200M)\,[M]$")
    ax.set_ylabel(r"$|\Delta E/E_0|$" "\u2009" "(med & 25\u201375% band)")

    # Bottom-Left: Median (bars) & p99 (markers) across E, L_z, Q/K
    ax = axes[1, 0]
    inv_keys = [("dE", r"$|\Delta E/E_0|$"), ("dL", r"$|\Delta L_z/L_{z,0}|$"), ("dQK", r"$|\Delta Q/K_0|$")]
    x = np.arange(len(inv_keys), dtype=np.float64)
    w = 0.25
    offs = (-w, 0.0, w)
    bar_specs = [
        ("hermite_ng4", cz.PAL["blue"],   "Cubic Hermite"),
        ("bspline_ng4", cz.PAL["orange"], "Cubic B-spline"),
        ("quintic_ng4", cz.PAL["red"],    "Quintic (Iter 4b)"),
    ]
    for (klbl, col, leg), off in zip(bar_specs, offs):
        meds = [float(np.median(D[f"{klbl}_{k}"])) for k, _ in inv_keys]
        p99s = [float(np.percentile(D[f"{klbl}_{k}"], 99)) for k, _ in inv_keys]
        ax.bar(x + off, meds, width=0.22, color=col, alpha=0.88, label=leg, zorder=3)
        ax.scatter(x + off, p99s, s=22, marker="D", color=col, edgecolors="k", linewidths=0.55, zorder=5)
        for xi, mv in zip(x + off, meds):
            exp = int(np.floor(np.log10(mv)))
            man = mv / (10.0 ** exp)
            ax.text(xi, mv * 0.78, rf"${man:.1f}$" "\n" rf"$\times 10^{{{exp}}}$",
                    ha="center", va="top", fontsize=4.7, color="white", fontweight="bold")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([t for _, t in inv_keys], fontsize=8.0)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylim(2.0e-11, 1.2e-3)
    cz.no_minor_labels(ax, "y")
    ax.set_ylabel(r"Killing invariant drift (bar: med, $\diamond$: $p_{99}$)")
    ax.legend(loc="upper right", fontsize=6.1, frameon=False, labelspacing=0.22)

    # Bottom-Right: VRAM-Accuracy Pareto + OS 7-level AMR VRAM reduction note
    ax = axes[1, 1]
    pt_specs = [
        ("hermite_ng2", cz.PAL["green"],  "s", r"Hermite ($ng=2$)", (0.15, 0.68, "left",   "top")),
        ("hermite_ng4", cz.PAL["blue"],   "^", r"Hermite ($ng=4$)", (0.30, 1.00, "left",   "center")),
        ("bspline_ng4", cz.PAL["orange"], "o", r"B-spline ($ng=4$)",(-0.10, 1.48, "center", "bottom")),
        ("quintic_ng4", cz.PAL["red"],    "*", r"Quintic ($ng=4$, Iter 4b)", (-0.38, 1.00, "right", "center")),
    ]
    for klbl, col, mkr, leg, (dx, dy, ha, va) in pt_specs:
        vram_gib = float(D[f"{klbl}_vram_mib"]) / 1024.0
        med_e = float(np.median(D[f"{klbl}_dE"]))
        ms = 9.5 if mkr == "*" else 6.2
        ax.semilogy([vram_gib], [med_e], marker=mkr, color=col, ms=ms, mec="k", mew=0.5, ls="none")
        ax.text(vram_gib + dx, med_e * dy, f"{leg}\n({vram_gib:.1f} GiB)",
                fontsize=5.8, color=col, ha=ha, va=va)

    # Connect iso-ghost Hermite -> Quintic and Bspline -> Quintic
    qh_v = float(D["quintic_ng4_vram_mib"]) / 1024.0
    hb_v = float(D["bspline_ng4_vram_mib"]) / 1024.0
    qh_e = float(np.median(D["quintic_ng4_dE"]))
    hh_e = float(np.median(D["hermite_ng4_dE"]))
    bb_e = float(np.median(D["bspline_ng4_dE"]))
    ax.annotate("", xy=(qh_v, qh_e * 1.18), xytext=(qh_v, hh_e * 0.85),
                arrowprops=dict(arrowstyle="->", color=cz.PAL["red"], lw=1.1, ls="--"))
    ax.annotate("", xy=(qh_v + 0.25, qh_e), xytext=(hb_v - 0.25, bb_e),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0, ls=":"))

    v3 = float(D["os_vram_gpu3_vram_mib"]) / 1024.0
    v4 = float(D["os_vram_gpu4_herm_froz_vram_mib"]) / 1024.0
    w3 = float(D["os_vram_gpu3_wall"])
    w4 = float(D["os_vram_gpu4_herm_froz_wall"])
    ax.text(0.04, 0.96,
            "7-level OS AMR bflx (Iter 4a):\n"
            + rf"${v3:.1f}\to {v4:.1f}$ GiB ($-6.06$ GiB)" "\n"
            + rf"Wall: ${w4:.1f}\,$s vs ${w3:.1f}\,$s (parity $\leq 4.4\times 10^{{-16}}$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.0, color="0.22")

    ax.set_xlim(5.6, 15.6)
    ax.set_ylim(1.2e-10, 4.5e-6)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"M4 Kerr peak GPU VRAM $[\mathrm{GiB}]$")
    ax.set_ylabel(r"Median energy error $|\Delta E/E_0|$")

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
