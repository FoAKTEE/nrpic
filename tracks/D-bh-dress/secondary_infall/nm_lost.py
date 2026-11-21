#!/usr/bin/env python3
"""Lost-particle diagnostic of a Newtonian-mode infall run (analysis of AthenaK output only;
decision 0010): which particles leave the isolated box, from where and when.

For a run of nm_run.py:
  - per snapshot: number and mass of particles alive; largest dust radius and its 99.9 %
    radius, against the closed-form radial Kepler orbit of the dust edge (central mass = all
    the mass inside R_edge, i.e. the total mass) and the box half-width L;
  - for every lost particle: kind (clump or dust), initial radius r0 and whether r0 > r_last
    (the shell that turns around at a_end), the snapshot after which it is gone, whether it
    ever had v_r < 0 or reached the other side of the centre, its last radius, |x_i|max/L,
    radial velocity;
  - the exact Newtonian expectation: E0 = v0^2/2 - M(<r0)/r0 per unit mass at t = 0 with the
    seed and the lattice dust inside r0, apocentre r_max = M(<r0)/|E0| (no shell crossing
    outside r_last); a particle reaches a face if r_max max_i |n_i| > L. The run's lost set
    is compared with this expected set.
Writes nm_lost.json and the figure nm_lost.

Usage: python3 nm_lost.py --run RUNDIR --out DIR
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle   # noqa: E402
from nrpic import newton as nw     # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    p = json.load(open(os.path.join(a.run, "setup.json")))
    meta = json.load(open(os.path.join(a.run, "nm_run.json")))
    L = float(meta["L"])
    n_tot, (c0, c1), (d0, d1) = p["n_total"], p["tag_clump"], p["tag_dust"]
    sh = np.asarray(p.get("shift", [0, 0, 0]))
    files = sorted(glob.glob(os.path.join(a.run, "infall.part.*.bin")))
    t0, _, x, u, m, tag = nw.read_snapshot(files[0])
    X0 = np.full((n_tot, 3), np.nan)
    U0 = np.full((n_tot, 3), np.nan)
    M = np.zeros(n_tot)
    X0[tag], U0[tag], M[tag] = x - sh, u, m
    r0 = np.sqrt((X0 ** 2).sum(1))
    # exact Newtonian energy and apocentre at t = 0 (seed + lattice mass inside r0)
    order = np.argsort(r0)
    menc = np.empty(n_tot)
    menc[order] = np.cumsum(M[order]) - 0.5 * M[order]
    v0 = np.sqrt((U0 ** 2).sum(1))
    E0 = 0.5 * v0 ** 2 - menc / np.maximum(r0, 1e-12)
    rmax = np.where(E0 < 0, menc / np.maximum(-E0, 1e-300), np.inf)
    nmax = np.abs(X0).max(1) / np.maximum(r0, 1e-12)
    expect_out = rmax * nmax > L
    dust = np.zeros(n_tot, bool)
    dust[d0:d1] = True
    # per snapshot
    alive_prev = np.isfinite(X0[:, 0])
    last_seen = np.full(n_tot, -1)
    last_x = np.full((n_tot, 3), np.nan)
    last_vr = np.full(n_tot, np.nan)
    turned = np.zeros(n_tot, bool)
    crossed = np.zeros(n_tot, bool)
    rows = []
    for k, fn in enumerate(files):
        t, cyc, x, u, m, tag = nw.read_snapshot(fn)
        X = np.full((n_tot, 3), np.nan)
        U = np.full((n_tot, 3), np.nan)
        X[tag], U[tag] = x - sh, u
        al = np.isfinite(X[:, 0])
        r = np.sqrt((X ** 2).sum(1))
        with np.errstate(invalid="ignore", divide="ignore"):
            vr = (X * U).sum(1) / r
        turned |= al & (vr < 0)
        crossed |= al & ((X * X0).sum(1) < 0)
        last_seen[al] = k
        last_x[al] = X[al]
        last_vr[al] = vr[al]
        rd = r[al & dust]
        rows.append(dict(k=k, t=float(t), a=float(((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0)),
                         n_alive=int(al.sum()), mass_alive=float(M[al].sum()),
                         r_dust_max=float(rd.max()), r_dust_999=float(np.percentile(rd, 99.9)),
                         xmax_over_L=float(np.abs(X[al]).max() / L)))
    nlast = len(files) - 1
    lost = np.isfinite(X0[:, 0]) & (last_seen < nlast)
    # closed-form edge orbit (central mass = total mass), at the snapshot times
    Mtot = float(M.sum())
    Re = p["r_edge"]
    ts = np.array([r_["t"] for r_ in rows])
    sol = solve_ivp(lambda tt, y: [y[1], -Mtot / y[0] ** 2], [0.0, ts[-1]], [Re, p["eps"] * Re],
                    t_eval=ts, rtol=1e-10, atol=1e-10)
    E_edge = 0.5 * (p["eps"] * Re) ** 2 - Mtot / Re
    res = dict(run=a.run, L=L, n_lost=int(lost.sum()), mass_lost=float(M[lost].sum()),
               n_lost_clump=int((lost & ~dust).sum()), n_lost_dust=int((lost & dust).sum()),
               first_loss_a=float(rows[int(np.min(last_seen[lost])) + 1]["a"]) if lost.any() else None,
               edge=dict(R_edge=Re, r_last=p["r_last"], E_per_mass=float(E_edge), M_inside=Mtot,
                         r_max_closed_form=float(Mtot / -E_edge) if E_edge < 0 else None,
                         kinetic=float(0.5 * (p["eps"] * Re) ** 2), potential=float(-Mtot / Re)),
               expected_out=dict(n=int((expect_out & np.isfinite(X0[:, 0])).sum()),
                                 mass=float(M[expect_out & np.isfinite(X0[:, 0])].sum())),
               lost_and_expected=int((lost & expect_out).sum()))
    if lost.any():
        lr0 = r0[lost]
        res["lost"] = dict(
            r0_percentiles=[float(v) for v in np.percentile(lr0, [0, 5, 50, 95, 100])],
            frac_r0_above_r_last=float(np.mean(lr0 > p["r_last"])),
            frac_mass_r0_above_r_last=float(M[lost & (r0 > p["r_last"])].sum() / M[lost].sum()),
            frac_turned=float(np.mean(turned[lost])), frac_crossed=float(np.mean(crossed[lost])),
            E0_percentiles=[float(v) for v in np.percentile(E0[lost], [0, 5, 50, 95, 100])],
            rmax_closed_percentiles=[float(v) for v in np.percentile(np.where(np.isfinite(rmax[lost]), rmax[lost], 1e9),
                                                                      [0, 5, 50, 95, 100])],
            nmax_percentiles=[float(v) for v in np.percentile(nmax[lost], [0, 5, 50, 95, 100])],
            last_xmax_over_L_percentiles=[float(v) for v in np.percentile(np.abs(last_x[lost]).max(1) / L,
                                                                          [0, 5, 50, 95, 100])],
            last_vr_percentiles=[float(v) for v in np.percentile(last_vr[lost], [0, 5, 50, 95, 100])])
        # dust of the same initial radius band that stayed: its E0 and r_max for comparison
        band = dust & ~lost & (r0 >= lr0.min()) & np.isfinite(X0[:, 0])
        res["stayed_same_r0_band"] = dict(n=int(band.sum()),
                                          rmax_closed_percentiles=[float(v) for v in np.percentile(rmax[band], [0, 50, 100])]
                                          if band.any() else None)
    res["rows"] = rows
    with open(os.path.join(a.out, "nm_lost.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))

    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 7.6))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.07, top=0.98, hspace=0.38)
    av = np.array([r_["a"] for r_ in rows])
    axs[0].plot(av, [r_["r_dust_max"] for r_ in rows], color=fs.PAL["red"], label="run: largest dust radius")
    axs[0].plot(av, [r_["r_dust_999"] for r_ in rows], "--", color=fs.PAL["red"], label="run: 99.9 % radius")
    axs[0].plot(av, [r_["xmax_over_L"] * L for r_ in rows], ":", color=fs.PAL["orange"], label=r"run: $L\,\max|x_i|/L$")
    axs[0].plot(av, sol.y[0], color=fs.PAL["blue"], label="closed form: dust edge")
    axs[0].axhline(L, **fs.GUIDE, label=f"box half-width {L:g} $M$")
    axs[0].set_xscale("log")
    axs[0].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[0].set_ylabel(r"radius [$GM/c^2$]")
    axs[0].legend(fontsize=6.5, loc="upper left")
    axs[1].plot(av, [M.sum() - r_["mass_alive"] for r_ in rows], color=fs.PAL["red"])
    axs[1].set_xscale("log")
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[1].set_ylabel(r"mass lost [$M$]")
    dd = dust & np.isfinite(X0[:, 0])
    bins = np.linspace(p["r_w"], Re * 1.02, 40)
    axs[2].hist(r0[dd], bins=bins, weights=M[dd], histtype="step", color="k", label="all dust")
    if lost.any():
        axs[2].hist(r0[lost & dust], bins=bins, weights=M[lost & dust], histtype="stepfilled", alpha=0.6,
                    color=fs.PAL["red"], label="lost")
        axs[2].hist(r0[expect_out & dd], bins=bins, weights=M[expect_out & dd], histtype="step",
                    color=fs.PAL["blue"], ls="--", label="expected out (exact gravity)")
    axs[2].axvline(p["r_last"], **fs.MASK_LINE)
    axs[2].set_yscale("log")
    axs[2].set_xlabel(r"initial radius $r_0$ [$GM/c^2$]")
    axs[2].set_ylabel(r"mass per bin [$M$]")
    axs[2].legend(fontsize=7, loc="upper left")
    fs.save(fig, os.path.join(a.out, "nm_lost"))


if __name__ == "__main__":
    main()
