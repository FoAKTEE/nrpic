"""K3: particle number a self-gravitating run needs to resolve the Kerr spike (a = 0.8)
inside ten horizon radii (r < 10 r_+ = 16 Gm), with equal-mass particles drawn from the
adiabatically grown Hernquist DF truncated at E <= E_cut (m = 4e6 Msun, M = 1e12 Msun,
r_s = 20 kpc, as in K1/K2).

Total number with E <= E_cut: the Kerr and Schwarzschild DFs differ only near the hole, so
    N_tot,Kerr = N_tot,Schw - N_Schw(< r_c) + N_Kerr(< r_c),  r_c = 40 Gm,
with N_Schw from spike_lib (4 pi r^2 rho / sqrt(1 - 2/r), to the largest apocentre) and
N_Kerr(< r_c) from kerr_lib on a (ln r, |cos theta|) grid. [JUDGEMENT: beyond 40 Gm the
spin changes the density by < 1 %, K1 curves.] Both in the same units (n x Af).

Criteria:
 counting: 8 logarithmic bins in 4-16 Gm (2.5-10 r_+, as wave 1 used 5-20 Gm = 2.5-10 r_+)
   times 3 bands of |cos theta|; 100 (10 %) or 400 (5 %) expected particles in the least
   populated bin;
 deposit: relative noise of the deposited density 0.26 at 1.1 particles per occupied cell
   with two filter passes, falling as N^-1/2 (docs/results_cluster_test.md, section (d)):
   5 % needs 1.1 (0.26/0.05)^2 = 30 particles per cell; required in every cell between 4
   and 16 Gm, i.e. at the lowest coordinate number density there, for dx = 0.25 and
   0.125 Gm.

usage: python3 kerr_budget.py --out DIR [--np 4]
"""
import argparse
import json
import multiprocessing as mp
import os
import shutil
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from kerr_lib import Kerr, KerrHernquist  # noqa: E402
from spike_lib import SpikeModel, HernquistInverse  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
A = 0.8
_H = None


def _init():
    global _H
    os.environ["OMP_NUM_THREADS"] = "1"
    _H = KerrHernquist(m_sun=4e6)


def job(arg):
    r, mu, eup = arg
    K = Kerr(A)
    th = np.arccos(mu)
    if K.Delta(r) <= A * A * np.sin(th) ** 2:
        return 0.0
    m = K.moments(r, th, fmodel=_H, Eup=eup)
    return 2 * np.pi * r * m.get("n_over_sin", 0.0)       # per (d ln r, d mu), both phi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--np", type=int, default=4)
    ap.add_argument("--nx", type=int, default=25)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rc = 40.0
    cuts = (1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
    x = np.linspace(np.log(2.05), np.log(rc), args.nx)
    mu = np.linspace(0.0, 1.0, 7)                    # band edges at nodes 0, 2, 4, 6
    jobs = [(float(np.exp(xx)), float(m), 1.0 - c) for c in cuts for xx in x for m in mu]
    with mp.Pool(args.np, initializer=_init) as pool:
        vals = np.array(pool.map(job, jobs, chunksize=1)).reshape(len(cuts), x.size, mu.size)
    H = KerrHernquist(m_sun=4e6)
    sm = SpikeModel(m_sun=4e6, table=HernquistInverse())
    rows, curves = [], {}
    rp = 1 + np.sqrt(1 - A * A)
    edges = np.logspace(np.log10(4.0), np.log10(16.0), 9)
    nde = 0.26 ** 2 * 1.1 / 0.05 ** 2                  # particles per cell for 5 %
    for ic, c in enumerate(cuts):
        ecut = 1.0 - c
        nx = vals[ic] * H.Af * 2                       # both hemispheres (mu in [0, 1])
        # Schwarzschild totals
        rmax = 2.0 / (1 - ecut * ecut) * 1.02 + 10
        rg = np.unique(np.concatenate([4.0 + np.logspace(-3, np.log10(6.0), 60),
                                       np.logspace(1.0, np.log10(rmax), 160)]))
        rho = sm.rho_rel(rg, "canonical", Eup=ecut, nE=48, nw=32)
        dNdr = 4 * np.pi * rg ** 2 * rho / np.sqrt(1 - 2 / rg)
        cdf = np.concatenate([[0], np.cumsum(0.5 * (dNdr[1:] + dNdr[:-1]) * np.diff(rg))])
        NS_tot, NS_rc = cdf[-1], np.interp(rc, rg, cdf)
        # Kerr inside rc
        nxr = np.trapezoid(nx, mu, axis=1)              # per d ln r
        cK = np.concatenate([[0], np.cumsum(0.5 * (nxr[1:] + nxr[:-1]) * np.diff(x))])
        NK_rc = cK[-1]
        NK_tot = NS_tot - NS_rc + NK_rc
        # counting bins: 8 log bins in 4-16 Gm x 3 bands
        bins = np.zeros((8, 3))
        xf = np.linspace(x[0], x[-1], 2000)
        for j in range(3):
            nb = np.trapezoid(nx[:, 2 * j:2 * j + 3], mu[2 * j:2 * j + 3], axis=1)
            cb = np.concatenate([[0], np.cumsum(0.5 * (nb[1:] + nb[:-1]) * np.diff(x))])
            bins[:, j] = np.diff(np.interp(np.log(edges), x, cb))
        pmin = bins.min() / NK_tot
        # deposit: particles per unit coordinate volume = n_x / (2 pi Sigma r) (CKS volume
        # element Sigma sin dr dtheta dphi), lowest value between 4 and 16 Gm
        R_, MU_ = np.meshgrid(np.exp(x), mu, indexing="ij")
        Sig = R_ ** 2 + A * A * MU_ ** 2
        nvol = nx / (2 * np.pi * Sig * R_) / 2          # per hemisphere-normalized mu grid
        sel = (R_ >= 4.0) & (R_ <= 16.0)
        nvol_min = nvol[sel].min() / NK_tot
        f16 = np.interp(np.log(16.0), x, cK) / NK_tot
        row = {"E_cut": ecut, "r_apo_max_Gm": float(rmax), "N_tot_over_Schw": NK_tot / NS_tot,
               "frac_inside_16Gm": float(f16), "frac_inside_40Gm": float(NK_rc / NK_tot),
               "min_bin_fraction": float(pmin),
               "N_total_count_10pc": float(100 / pmin), "N_total_count_5pc": float(400 / pmin),
               "N_inside_16Gm_count_5pc": float(400 / pmin * f16),
               "lowest_volume_fraction_4-16Gm_per_Gm3": float(nvol_min),
               "N_total_deposit_5pc_dx0.25": float(nde / (nvol_min * 0.25 ** 3)),
               "N_total_deposit_5pc_dx0.125": float(nde / (nvol_min * 0.125 ** 3)),
               "N_inside_16Gm_deposit_5pc_dx0.25": float(nde / (nvol_min * 0.25 ** 3) * f16),
               "N_inside_16Gm_deposit_5pc_dx0.125": float(nde / (nvol_min * 0.125 ** 3) * f16)}
        rows.append(row)
        rr = np.concatenate([np.exp(x), rg[rg > rc]])
        cc = np.concatenate([cK, NK_rc + (cdf[rg > rc] - NS_rc)]) / NK_tot
        curves[c] = (rr, cc)
    res = {"a": A, "r_plus": rp, "ten_r_plus": 10 * rp, "rows": rows,
           "deposit_particles_per_cell_for_5pc": nde, "wall_s": time.time() - t0,
           "bins_edges_Gm": edges.tolist()}
    (out / "kerr_budget.json").write_text(json.dumps(res, indent=1))
    np.savez(out / "kerr_budget_grid.npz", x=x, mu=mu, vals=vals, cuts=np.array(cuts))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    a_ = axs[0]
    for (k, (rr, cc)), col in zip(curves.items(), figstyle.SERIES):
        a_.loglog(rr, cc, color=col, label=rf"$1-E_{{\rm cut}} = 10^{{{np.log10(k):.0f}}}$")
    a_.axvline(16.0, **figstyle.MASK_LINE)
    a_.set_xlabel(r"$r/Gm$"); a_.set_ylabel(r"$N(<r)/N$, $a = 0.8$")
    a_.set_ylim(1e-7, 1.2); a_.legend(loc="lower right", fontsize=7)
    b_ = axs[1]
    xa = [r["r_apo_max_Gm"] for r in rows]
    P = figstyle.PAL
    b_.loglog(xa, [r["N_total_count_10pc"] for r in rows], "o-", color=P["red"],
              label="counts: 10 % per bin")
    b_.loglog(xa, [r["N_total_count_5pc"] for r in rows], "s--", color=P["red"],
              label="counts: 5 % per bin")
    b_.loglog(xa, [r["N_total_deposit_5pc_dx0.25"] for r in rows], "^-", color=P["blue"],
              label=r"deposit: 5 %, $dx = 0.25\,Gm$")
    b_.loglog(xa, [r["N_total_deposit_5pc_dx0.125"] for r in rows], "v--", color=P["blue"],
              label=r"deposit: 5 %, $dx = 0.125\,Gm$")
    b_.set_xlabel(r"largest apocentre of the sampled DF [$Gm$]")
    b_.set_ylabel(r"total $N$ (equal masses)")
    b_.legend(loc="upper left", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"kerr_budget.{ext}")
    plt.close(fig)
    shutil.copy(out / "kerr_budget.png", HERE / "figs" / "kerr_budget.png")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
