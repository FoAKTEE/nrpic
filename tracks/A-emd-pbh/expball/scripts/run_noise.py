#!/usr/bin/env python3
"""Particle noise of the Hamiltonian constraint: particles deposited with the linear cloud
(CIC) on the cell-centred mesh of [-L, L]^3, against particle number and sampler.

With the geometry of the table (which satisfies the constraint up to the FD error measured
by run_convergence.py), the deposited density changes the Hamiltonian residual by
dH = 16 pi (rho - rho_dep); reported as dH/(6H^2) = (rho - rho_dep)/rho_b, rms and mean
over the cells with rbar < 0.8 rbar_matter.

Poisson prediction for independent positions (mc): rms = sqrt((2/3)^3 / n_c), n_c the
expected number of particles per cell volume ((2/3)^3 = int of the CIC weight squared).
"""

import argparse
import json
import math
import os
import shutil
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_PKG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, _PKG)

import numpy as np  # noqa: E402

from expball import mesh, model as M, particles, runlog  # noqa: E402

REPO = os.path.normpath(os.path.join(_PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RB = 8.0
CORE = dict(delta_c=1.0, R1=0.3 * RB, R2=0.75 * RB)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--Ns", default="10000,30000,100000,300000,1000000")
    p.add_argument("--mesh-N", type=int, default=64)
    p.add_argument("--Lfac", type=float, default=1.25)
    p.add_argument("--seeds", type=int, default=2, help="independent seeds for mc/stratified")
    a = p.parse_args(argv)
    Ns = [int(s) for s in a.Ns.split(",")]
    with runlog.Run(f"A-pre-1: Hamiltonian-constraint noise of CIC-deposited particles vs N "
                    f"(N = {Ns}, mesh {a.mesh_N}^3)", kind="production", cores=4) as run:
        L = a.Lfac * RB
        Nm = a.mesh_N
        h = 2 * L / Nm
        c = -L + (np.arange(Nm) + 0.5) * h
        X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
        rbc = np.sqrt(X * X + Y * Y + Z * Z)
        out = {}
        maps = {}
        for name, b in (("flat", M.Ball.from_HRb(0.5)),
                        ("smooth_tophat", M.Ball.from_HRb(0.5, profile=M.SmoothTopHat(**CORE)))):
            f = b.fields(rbc, ("u", "rho"))
            psi6 = (1 + f["u"]) ** 6
            rho = f["rho"]
            rm = b.matter_rbar()
            reg = rbc < 0.8 * rm
            M0 = b.rest_mass()
            out[name] = {}
            for samp in ("mc", "stratified", "lattice"):
                rows = []
                for N in Ns:
                    seeds = range(1, a.seeds + 1) if samp != "lattice" else [0]
                    for sd in seeds:
                        t0 = time.time()
                        if samp == "lattice":
                            nl = particles.nlat_for(N)
                            x, u, m, sp = particles.lattice(b, nl)
                        else:
                            x, u, m, sp = particles.sample(b, N, samp, seed=sd)
                        dep = mesh.deposit_cic(x, m, Nm, L) / (psi6 * h ** 3)
                        dH = (rho - dep) / b.rho_b
                        nc = len(m) * (rho * psi6 * h ** 3)[reg].mean() / M0
                        rows.append(dict(N=int(len(m)), N_target=N, seed=sd,
                                         rms=float(np.sqrt(np.mean(dH[reg] ** 2))),
                                         mean=float(np.mean(dH[reg])),
                                         n_per_cell=float(nc),
                                         poisson=float(math.sqrt((2 / 3) ** 3 / nc)),
                                         mass_error=float(m.sum() / M0 - 1)))
                        if N == 100000 and sd in (0, 1):
                            maps[(name, samp)] = dH[:, :, Nm // 2]
                        print(f"{name:14s} {samp:10s} N={len(m):8d} s{sd} rms {rows[-1]['rms']:.4e} "
                              f"(Poisson {rows[-1]['poisson']:.4e}) mean {rows[-1]['mean']:+.2e} "
                              f"{time.time() - t0:.1f}s", flush=True)
                out[name][samp] = rows
        with open(os.path.join(run.out, "noise.json"), "w") as fh:
            json.dump(dict(run_id=run.run_id, mesh_N=Nm, L=L, h=h, region="rbar < 0.8 rbar_matter",
                           results=out), fh, indent=1)
        figs = figures(out, maps, run.out, L)
        for fp in figs:
            shutil.copy(fp, os.path.join(_PKG, "figures", os.path.basename(fp)))
        # fitted slopes
        slopes = {}
        for name in out:
            for samp in out[name]:
                r = out[name][samp]
                Nn = np.array([q["N"] for q in r], dtype=float)
                rr = np.array([q["rms"] for q in r])
                slopes[f"{name}/{samp}"] = float(np.polyfit(np.log(Nn), np.log(rr), 1)[0])
        run.results = dict(slopes=slopes, figures=[os.path.basename(f) for f in figs])
        print(json.dumps(run.results, indent=1))
    return 0


def figures(out, maps, d, L):
    fs.use_style()
    files = []
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.3), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.15, top=0.92, wspace=0.06)
    cols = dict(mc=fs.PAL["blue"], stratified=fs.PAL["red"], lattice=fs.PAL["green"])
    for ax, name in zip(axes, out):
        for samp, r in out[name].items():
            Nn = np.array([q["N"] for q in r])
            ax.loglog(Nn, [q["rms"] for q in r], "o-" if samp != "lattice" else "s-", ms=3,
                      color=cols[samp], label=samp)
            if samp == "mc":
                ax.loglog(Nn, [q["poisson"] for q in r], **fs.GUIDE, label="Poisson (CIC)")
        ax.set_title(name.replace("_", " "), fontsize=10)
        ax.set_xlabel("particle number $N$")
    axes[0].set_ylabel(r"rms $\delta H/6H^2$, $\bar r < 0.8\,\bar r_{\rm m}$")
    axes[0].legend(fontsize=8)
    files += fs.save(fig, os.path.join(d, "fig_particle_noise"))
    plt.close(fig)
    if maps:
        keys = [k for k in (("flat", "mc"), ("flat", "stratified"), ("flat", "lattice"),
                            ("smooth_tophat", "stratified")) if k in maps]
        fig, axes = plt.subplots(1, len(keys), figsize=(8.0, 2.5))
        fig.subplots_adjust(left=0.06, right=0.86, bottom=0.17, top=0.88, wspace=0.08)
        for ax, k in zip(axes, keys):
            im = ax.imshow(maps[k].T, origin="lower", extent=[-L / RB, L / RB, -L / RB, L / RB],
                           cmap=fs.CMAP["diverging"], vmin=-1, vmax=1, interpolation="none",
                           rasterized=True)
            ax.set_title(f"{k[0].replace('_', ' ')}, {k[1]}", fontsize=8)
            ax.set_xlabel(r"$x/R_b$", labelpad=-2)
            ax.set_yticks([] if ax is not axes[0] else [-1, 0, 1])
        cax = fig.add_axes([0.875, 0.17, 0.012, 0.71])
        fig.colorbar(im, cax=cax, label=r"$\delta H/6H^2$")
        files += fs.save(fig, os.path.join(d, "fig_particle_noise_maps_N1e5"))
        plt.close(fig)
    return [f for f in files if f.endswith((".png", ".pdf"))]


if __name__ == "__main__":
    sys.exit(main())
