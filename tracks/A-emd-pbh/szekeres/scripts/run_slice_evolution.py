"""The reference Szekeres model (eps = 0.1, twisted dipole in the transition shell of expball
data set 2): slices in conformally flat coordinates and the proper-time evolution of dust
elements (P9 margins). Writes slice_evolution.json, fig_slice_maps, fig_evolution.

    python3 scripts/run_slice_evolution.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402
from szekeres.mesh import plane_fields  # noqa: E402

TAUS = (0.0, 30.0)
HALF = 6.5
NPIX = 260


def main():
    rdir = common.run_dir("slice_evolution")
    ltb, szk = common.models()
    out = dict(run_id=common.run_id(), commit=common.git_commit(), model=szk.summary())
    tc_core = float(szk.crunch_time(np.array([1.0]))[0])
    out["t_i"] = szk.t_i
    out["tau_crunch_core"] = tc_core - szk.t_i
    maps = {}
    for tau in TAUS:
        t = szk.t_i + tau
        for name, mdl in (("szk", szk), ("ltb", ltb)):
            cm = ConformalMap(mdl, t=t)
            u, f = plane_fields(cm, NPIX, HALF, axis=1, value=0.0)
            maps[name, tau] = (u, f, cm)
        a = (t / szk.t_i) ** (2 / 3)
        rho_b = szk.rho_b / a ** 3
        fs_, fl = maps["szk", tau][1], maps["ltb", tau][1]
        out[f"slice_tau{tau:g}"] = dict(
            rho_over_rhob_min=float(fs_["rho"].min() / rho_b), rho_over_rhob_max=float(fs_["rho"].max() / rho_b),
            psi_min=float(fs_["psi"].min()), psi_max=float(fs_["psi"].max()),
            max_abs_rho_minus_ltb_over_rhob=float(np.abs(fs_["rho"] - fl["rho"]).max() / rho_b),
            max_abs_psi_minus_ltb=float(np.abs(fs_["psi"] - fl["psi"]).max()),
            centre_of_r1_sphere=maps["szk", tau][2].radial_table(np.array([1.0]))["C"][:, 0].tolist(),
            hyperboloid_drift=maps["szk", tau][2].hyper_drift)
    # evolution of dust elements along +b and -b
    shells = np.array([2.8, 3.4, 4.0, 4.6, 5.2, 5.8])
    bb = np.linalg.norm(szk.dip.b(shells), axis=-1)
    tcs = szk.crunch_time(shells)
    ev = {}
    for k, rr in enumerate(shells):
        tend = min(tcs[k], 4 * tc_core) * (1 - 1e-3) if np.isfinite(tcs[k]) else 4 * tc_core
        tt = szk.t_i + np.linspace(0, tend - szk.t_i, 400)
        rows = {}
        for lab, bn in (("plus", bb[k]), ("ltb", 0.0), ("minus", -bb[k])):
            f = szk.fields(tt, np.full_like(tt, rr), np.full_like(tt, bn))
            rows[lab] = dict(rho=f["rho"], Theta=f["Theta"], W=f["W"], Sigma=f["Sigma"])
        ev[rr] = (tt, rows)
    # margins against shell crossing over the whole transition shell
    rgrid = np.linspace(2.41, 5.99, 600)
    tgrid = szk.t_i + np.linspace(0, 0.995 * tc_core - szk.t_i, 300)
    mcross = np.array([np.min(szk.margins(t, rgrid)[0]) for t in tgrid])
    mdens = float(np.min(szk.margins(szk.t_i, rgrid)[1]))
    out["margin_shell_crossing_min"] = float(mcross.min())
    out["margin_shell_crossing_at_tau"] = float(tgrid[int(np.argmin(mcross))] - szk.t_i)
    out["margin_density_min"] = mdens
    out["elements"] = {f"r={rr:g}": dict(
        tau_crunch=float(tcs[k] - szk.t_i),
        rho_ratio_plus_minus_at_end=float(ev[rr][1]["plus"]["rho"][-1] / ev[rr][1]["minus"]["rho"][-1]),
        rho_ratio_plus_minus_at_start=float(ev[rr][1]["plus"]["rho"][0] / ev[rr][1]["minus"]["rho"][0]))
        for k, rr in enumerate(shells)}
    common.dump(os.path.join(rdir, "slice_evolution.json"), out)
    print(out)

    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    import figstyle as fs
    fs.use_style()
    # ---- slice maps: rows tau, columns rho/rho_b, psi - 1, (rho - rho_LTB)/rho_b
    fig, axes, cax = fs.slice_mosaic(2, 3, cbar="right", left=0.62, fig_w=6.55, bottom=0.42)
    levels = [2.4, 3.0, 3.6, 4.2, 4.8, 5.4, 6.0]
    for i, tau in enumerate(TAUS):
        u, f, cm = maps["szk", tau]
        _, fl, _ = maps["ltb", tau]
        t = szk.t_i + tau
        rho_b = szk.rho_b / (t / szk.t_i) ** 2
        ext = [-HALF, HALF, -HALF, HALF]
        im0 = axes[i, 0].imshow((f["rho"] / rho_b).T, origin="lower", extent=ext, cmap=fs.CMAP["dens"],
                                norm=LogNorm(0.2, 20), interpolation="none", rasterized=True)
        d = (f["psi"] - 1)
        axes[i, 1].imshow(d.T, origin="lower", extent=ext, cmap=fs.CMAP["dens"], vmin=0, vmax=max(d.max(), 1e-6),
                          interpolation="none", rasterized=True)
        dd = (f["rho"] - fl["rho"]) / rho_b
        v = np.abs(dd).max()
        axes[i, 2].imshow(dd.T, origin="lower", extent=ext, cmap="RdBu_r", vmin=-v, vmax=v,
                          interpolation="none", rasterized=True)
        for j in range(3):
            axes[i, j].contour(u, u, f["r"].T, levels=levels, colors="w" if j < 2 else "k", linewidths=0.6)
            fs.slice_ticks(axes[i, j], HALF, show_x=(i == 1), show_y=(j == 0))
            axes[i, j].text(0.03, 0.95, ["$\\rho/\\bar\\rho$", "$\\psi - 1$", "$(\\rho - \\rho_{LTB})/\\bar\\rho$"][j]
                            + f"\n$\\tau = {tau:g}$" + (f", max {v:.2f}" if j == 2 else
                                                       (f", max {d.max():.3f}" if j == 1 else "")),
                            transform=axes[i, j].transAxes, va="top", fontsize=7,
                            color="w" if j < 2 else "k")
        axes[i, 0].set_ylabel("z", labelpad=-2)
    for j in range(3):
        axes[1, j].set_xlabel("x")
    fig.colorbar(im0, cax=cax, label=r"$\rho/\bar\rho$ (left column)")
    common.save_fig(fig, "fig_slice_maps", rdir)
    plt.close(fig)
    # ---- evolution of elements
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.9, wspace=0.36)
    cols = fs.series_colors(len(shells))
    for k, rr in enumerate(shells):
        tt, rows = ev[rr]
        tau = tt - szk.t_i
        rho_b = szk.rho_b * (szk.t_i / tt) ** 2
        for lab, ls in (("plus", "-"), ("ltb", ":"), ("minus", "--")):
            axs[0].semilogy(tau, rows[lab]["rho"] / rho_b, color=cols[k], ls=ls, lw=1.2,
                            label=f"$r = {rr:g}$" if lab == "plus" else None)
            axs[1].plot(tau, rows[lab]["Theta"] * tt, color=cols[k], ls=ls, lw=1.2)
    axs[0].axvline(tc_core - szk.t_i, **fs.MASK_LINE)
    axs[1].axvline(tc_core - szk.t_i, **fs.MASK_LINE)
    axs[0].set_xlabel(r"proper time $\tau$")
    axs[0].set_ylabel(r"$\rho/\bar\rho$ of the element")
    axs[0].legend(fontsize=7, ncol=2, loc="upper left")
    axs[0].set_title(r"solid $+\hat b$, dashed $-\hat b$, dotted LTB", fontsize=8)
    axs[1].set_xlabel(r"proper time $\tau$")
    axs[1].set_ylabel(r"$\Theta\, t$")
    axs[1].set_ylim(-6, 3)
    axs[2].plot(tgrid - szk.t_i, mcross, color=fs.PAL["red"])
    axs[2].axhline(1.0, **fs.GUIDE)
    axs[2].set_yscale("log")
    axs[2].set_xlabel(r"proper time $\tau$")
    axs[2].set_ylabel(r"$\min_r (R'/R)/|b|$")
    axs[2].set_title("shell crossing at 1", fontsize=8)
    common.save_fig(fig, "fig_evolution", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
