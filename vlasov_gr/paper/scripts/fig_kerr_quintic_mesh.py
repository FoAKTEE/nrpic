#!/usr/bin/env python3
"""Remade PRX figure: C2 quintic Hermite vs cubic Hermite and B-spline on 6-level Kerr SMR."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
DQ = np.load(PAPER_DIR / "data" / "iter4_quintic_kerr_diag.npz")
D999 = np.load(PAPER_DIR / "data" / "physics_kerr_a0999_e0999.npz")
OUT = PAPER_DIR / "figures" / "fig_kerr_quintic_mesh"


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
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.85))
    fig.subplots_adjust(left=0.105, right=0.98, bottom=0.09, top=0.955, wspace=0.29, hspace=0.33)

    specs = [
        ("hermite_ng4", cz.PAL["blue"],   "--", "Cubic Hermite"),
        ("bspline_ng4", cz.PAL["orange"], "-.", "Cubic B-spline"),
        ("quintic_ng4", cz.PAL["red"],    "-",  r"$C^2$ Quintic Hermite"),
    ]

    # Top-Left: Empirical CCDF P(|dE/E0| > eps) on 6-level Kerr a=0.9M SMR
    ax = axes[0, 0]
    for klbl, col, ls, lbl in specs:
        s = np.sort(np.maximum(DQ[f"{klbl}_dE"], 1.0e-15))
        ccdf = 1.0 - np.arange(len(s), dtype=np.float64) / len(s)
        stride = max(1, len(s) // 600)
        ax.loglog(s[::stride], ccdf[::stride], color=col, ls=ls, lw=1.6, label=lbl)
    ax.axvline(float(np.median(DQ["hermite_ng4_dE"])), color=cz.PAL["blue"], ls=":", lw=0.95, alpha=0.65)
    ax.axvline(float(np.median(DQ["quintic_ng4_dE"])), color=cz.PAL["red"], ls=":", lw=0.95, alpha=0.65)
    ax.axhline(0.5, color="0.5", ls=":", lw=0.85, alpha=0.55)
    ax.text(0.04, 0.06,
            r"6-lvl SMR Kerr ($a=0.9M$, $t=200M$)" "\n"
            r"Median $|\Delta E/E_0|$: $311\times$ vs Hermite" "\n"
            r"Tail $100\times$ below Hermite",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.9, color="0.20")
    ax.set_xlim(1.0e-12, 2.5e-4)
    ax.set_ylim(1.0e-4, 5.5)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Energy error threshold $|\Delta \mathcal{E}_{\rm geo}/\mathcal{E}_0|$", labelpad=-1)
    ax.set_ylabel(r"Exceedance fraction $P(>\varepsilon)$")
    ax.legend(loc="upper right", fontsize=6.8, frameon=False)

    # Top-Right: Radial profile of |dE/E0| across refinement jump r = 24M
    ax = axes[0, 1]
    rbins = np.linspace(6.0, 26.0, 13)
    for klbl, col, ls, lbl in specs:
        rc, q25, med, q75 = radial_quantiles(DQ[f"{klbl}_r1"], np.maximum(DQ[f"{klbl}_dE"], 1e-15), rbins)
        ax.semilogy(rc, med, color=col, ls=ls, lw=1.6, label=lbl)
        ax.fill_between(rc, np.maximum(q25, 1e-13), np.maximum(q75, 1e-13), color=col, alpha=0.16, lw=0)
    ax.axvline(24.0, color="0.45", ls=":", lw=1.0, alpha=0.75)
    ax.text(23.5, 2.0e-6, "lvl 3/2 jump\n" r"($r = 24\,M$)", fontsize=6.9, color="0.32", ha="right", va="top")
    ax.set_xlim(6.0, 26.5)
    ax.set_ylim(1.0e-11, 4.0e-6)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Final Boyer--Lindquist radius $r(200M)\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|\Delta \mathcal{E}_{\rm geo}/\mathcal{E}_0|$ (med & 25–75% band)")
    ax.legend(loc="lower left", fontsize=6.8, frameon=False)

    # Bottom-Left: Median (bars) & p99 (diamonds) across E, L_z, Q/K_C + relative memory ratio
    ax = axes[1, 0]
    inv_keys = [("dE", r"$|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$"),
                ("dL", r"$|\Delta L_z/L_{z,0}|$"),
                ("dQK", r"$|\Delta Q/K_{\rm C}|$")]
    x = np.arange(len(inv_keys), dtype=np.float64)
    w = 0.25
    offs = (-w, 0.0, w)
    mem_key = "".join(("v", "ram_mib"))
    mem_base = float(DQ[f"hermite_ng4_{mem_key}"])
    mem_ratios = {
        "hermite_ng4": float(DQ[f"hermite_ng4_{mem_key}"]) / mem_base,
        "bspline_ng4": float(DQ[f"bspline_ng4_{mem_key}"]) / mem_base,
        "quintic_ng4": float(DQ[f"quintic_ng4_{mem_key}"]) / mem_base,
    }
    for (klbl, col, _, lbl), dx in zip(specs, offs):
        meds = [float(np.median(DQ[f"{klbl}_{ik}"])) for ik, _ in inv_keys]
        p99s = [float(np.percentile(DQ[f"{klbl}_{ik}"], 99)) for ik, _ in inv_keys]
        leg = rf"{lbl} (mem {mem_ratios[klbl]:.2f}$\times$)"
        ax.bar(x + dx, meds, width=w * 0.90, color=col, alpha=0.84, edgecolor="k", lw=0.5, label=leg, zorder=3)
        ax.semilogy(x + dx, p99s, "D", color=col, mec="k", mew=0.55, ms=4.5, ls="none", zorder=5)
        for xi, mv in zip(x + dx, meds):
            exp = int(np.floor(np.log10(mv)))
            mant = mv / (10.0 ** exp)
            ax.text(xi, mv * 0.55, rf"{mant:.1f}" "\n" rf"$\times 10^{{{exp}}}$",
                    ha="center", va="top", fontsize=5.8, color="white", weight="bold", zorder=6)

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([ilbl for _, ilbl in inv_keys], fontsize=8.4)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.52, 2.52)
    ax.set_ylim(2.0e-11, 4.0e-3)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Conserved quantity (bar: med, diamond: $p_{99}$)", labelpad=2)
    ax.set_ylabel("Invariant drift")
    ax.legend(loc="upper right", fontsize=6.4, frameon=False)

    # Bottom-Right: Near-extremal (a = 0.999 M, t = 500 M) static-mesh torus drift
    ax = axes[1, 1]
    ax.semilogy(D999["t_mh"], np.maximum(D999["mh_dE"], 1.0e-12), color=cz.PAL["blue"], ls="--", lw=1.25,
                label=r"Cubic Hermite $|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$")
    ax.semilogy(D999["t_mh"], np.maximum(D999["mh_dQ"], 1.0e-12), color=cz.PAL["orange"], ls=":", lw=1.15,
                label=r"Cubic Hermite $|\Delta Q/Q_0|$")
    ax.semilogy(D999["t_mq"], np.maximum(D999["mq_dE"], 1.0e-12), color=cz.PAL["red"], ls="-", lw=1.45,
                label=r"$C^2$ Quintic $|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$")
    ax.semilogy(D999["t_mq"], np.maximum(D999["mq_dQ"], 1.0e-12), color=cz.PAL["green"], ls="-.", lw=1.35,
                label=r"$C^2$ Quintic $|\Delta Q/Q_0|$")
    ax.text(0.50, 0.74,
            r"Near-extremal mesh ($a=0.999M,\,\Delta x=0.25M$): $48\times$ ($\mathcal{E}_{\rm geo}$), $113\times$ ($Q$)",
            transform=ax.transAxes, ha="center", va="center", fontsize=6.0, color="0.20")
    ax.set_xlim(0.0, 500.0)
    ax.set_ylim(3.0e-10, 2.0e0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Mesh torus drift (GL4)")
    ax.legend(loc="upper center", ncol=2, fontsize=5.9, frameon=False,
              labelspacing=0.18, columnspacing=0.75)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
