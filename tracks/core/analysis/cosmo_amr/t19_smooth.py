#!/usr/bin/env python3
"""T19 of the work package cosmo-amr: how well the leaf cells of a refined patch hold a
smooth density when the clouds are one level coarser (prediction:
tracks/core/JOURNAL-cosmo-amr.md, entry of T19).

    t19_smooth.py --new EXE --pub EXE --out DIR [--ppx P] [--cores N] [--analyse-only]

Box [-3, 3)^3 of the homogeneous-universe deck, root N^3 (N = 24, 48), static level 1 on
[-1, 1]^3, clouds on the root level, no filter, no step.  P particles per root cell along
x (default 4; one along y and z: T19 had P = 1, where the aliasing of the lattice in the
cloud hides the leaf cells) on a lattice displaced along x, x = q + (delta/k) sin(k q), k = pi (wavelength 2, the width of
the patch), delta = 0.3, so that the density is rho_0/(1 + delta cos(k q)); the lattice
is offset by (0.37, 0.3, 0.2) root cells from the cell centres.  Table of tmunu_E along
the x line through the origin's leaf row.  Cases: uniform spreading ("const"),
deposit_fine_shape with the new executable ("new") and with the published one ("pub"),
linear cloud; and the quadratic cloud with fine shape ("tsc", new executable).
Measured on the leaf cells with |x| < 0.75: the rms and the largest departure of
E/rho_0 from the exact density at the centre of the leaf cell.
Writes DIR/t19_summary.json and DIR/fig_t19_smooth.{pdf,png}."""
import argparse
import glob
import json
import os
import sys

import numpy as np

import amrlib as A

L, NB = 6.0, 8
KW, DELTA = np.pi, 0.3
OFF = (0.37, 0.3, 0.2)
NS = (24, 48)
MP = 1e-6
PPX = 4


def exact(x):
    """rho/rho_0 at position x of the displaced lattice (Newton iteration for q)."""
    q = np.array(x, dtype=float)
    for _ in range(60):
        q -= (q + DELTA/KW*np.sin(KW*q) - x)/(1.0 + DELTA*np.cos(KW*q))
    return 1.0/(1.0 + DELTA*np.cos(KW*q))


def base(ic, n):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo/flrw.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": n, f"x{d}min": -L/2, f"x{d}max": L/2})
        b.set("meshblock", **{f"nx{d}": NB})
    b.set("time", tlim=10.0, nlim=0)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"), snap_dt=-1.0,
          probe_x1=0.01, probe_x2=0.01, probe_x3=0.01, cstat_dcycle=1, hist_dcycle=1,
          nfilter=0, filter_compensate=False, deposit_max_level=0, deposit_adaptive=False)
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    h = L/n
    b.set("output1", file_type="hst", dt=0.5)
    b.set("output2", file_type="tab", variable="tmunu_E", dt=100.0, slice_x2=0.25*h,
          slice_x3=0.25*h, data_format="%24.16e")
    b.set("mesh_refinement", refinement="static", max_nmb_per_rank=512)
    b.set("refined_region1", level=1, x1min=-0.5, x1max=0.5, x2min=-0.5, x2max=0.5,
          x3min=-0.5, x3max=0.5)
    return b


def line(rundir, n):
    fs = sorted(glob.glob(os.path.join(rundir, "tab", "flrw.tmunu_E.*.tab")))
    d, _ = A.read_tab(fs[0])
    xk = [k for k in d if k.startswith("x1")][0]
    x, e = d[xk], d["tmunu_E"]
    o = np.argsort(x)
    x, e = x[o], e[o]
    rho0 = MP*PPX*n**3/L**3
    w = np.abs(x) < 0.75
    return x[w], e[w]/rho0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--pub", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--ppx", type=int, default=4)
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args()
    global PPX
    PPX = a.ppx
    a.out, a.new, a.pub = (os.path.abspath(a.out), os.path.abspath(a.new),
                           os.path.abspath(a.pub))
    os.makedirs(a.out, exist_ok=True)
    from nrp_io import write_particles
    cases = {"const": (a.new, "cic", False), "new": (a.new, "cic", True),
             "pub": (a.pub, "cic", True), "tsc": (a.new, "tsc", True)}
    jobs, keys = [], []
    for n in NS:
        ic = os.path.join(a.out, "ic", f"n{n}")
        h = L/n
        if not a.analyse_only:
            os.makedirs(ic, exist_ok=True)
            g = -L/2 + (np.arange(n) + 0.5)*h
            gx = -L/2 + (np.arange(n*PPX) + 0.5)*h/PPX
            qx, qy, qz = np.meshgrid(gx + OFF[0]*h/PPX, g + OFF[1]*h, g + OFF[2]*h,
                                     indexing="ij")
            x = qx + DELTA/KW*np.sin(KW*qx)
            pos = np.stack([x.ravel(), qy.ravel(), qz.ravel()], axis=1)
            pos = (pos + L/2) % L - L/2
            write_particles(os.path.join(ic, "particles.nrp"), pos, np.zeros_like(pos),
                            np.full(len(pos), MP))
        for name, (exe, shape, fine) in cases.items():
            b = base(ic, n).set("particles", deposit_shape=shape)
            if fine:
                b.set("particles", deposit_fine_shape=True)
            keys.append((name, n))
            jobs.append((exe, b, os.path.join(a.out, f"{name}-n{n}"), "flrw", (), None))
    if not a.analyse_only:
        rcs = A.run_many(jobs, a.cores)
        print("exit", [rc[0] for rc in rcs], "wall", [round(rc[1], 1) for rc in rcs],
              flush=True)
    res, keep = {}, {}
    for key, j in zip(keys, jobs):
        x, r = line(j[2], key[1])
        ex = exact(x)
        keep[key] = (x, r, ex)
        res[f"{key[0]}-n{key[1]}"] = {"cells": int(len(x)),
                                      "rms": float(np.sqrt(np.mean((r - ex)**2))),
                                      "max": float(np.max(np.abs(r - ex))),
                                      "min_density": float(np.min(r))}
    for name in cases:
        r1, r2 = res[f"{name}-n{NS[0]}"], res[f"{name}-n{NS[1]}"]
        res[f"{name}-ratio"] = {"rms": r1["rms"]/r2["rms"], "max": r1["max"]/r2["max"]}
        print(f"{name:6s} rms {r1['rms']:.3e} -> {r2['rms']:.3e} (ratio "
              f"{r1['rms']/r2['rms']:.2f})   max {r1['max']:.3e} -> {r2['max']:.3e} (ratio "
              f"{r1['max']/r2['max']:.2f})", flush=True)
    with open(os.path.join(a.out, "t19_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.30, top=0.92, wspace=0.30)
    lab = {"const": "linear cloud, uniform spreading",
           "pub": "linear cloud, fine shape, first-order form (3c44b74)",
           "new": "linear cloud, fine shape, integral form",
           "tsc": "quadratic cloud, fine shape"}
    order = ("const", "pub", "new", "tsc")
    xf = np.linspace(-0.75, 0.75, 400)
    for ip, n in enumerate(NS):
        q = ax[ip]
        for i, name in enumerate(order):
            x, r, ex = keep[(name, n)]
            q.plot(x, r - ex, "-", lw=0.9, color=fs.SERIES[i], label=lab[name])
        q.axhline(0.0, color="grey", lw=0.5, ls=":")
        q.set_xlabel(r"$x$")
        q.set_title(f"{n//3} root cells per wavelength", fontsize=9)
    ax[0].set_ylabel(r"$E/\rho_0$ minus exact, leaf cells")
    ax[0].legend(frameon=False, fontsize=7.5, ncol=2, loc="upper left",
                 bbox_to_anchor=(0.0, -0.22))
    q = ax[2]
    hs = np.array([L/n for n in NS])
    for i, name in enumerate(order):
        q.loglog(hs, [res[f"{name}-n{n}"]["rms"] for n in NS], "o-", color=fs.SERIES[i],
                 label=lab[name])
    q.loglog(hs, 0.02*(hs/hs[0]), color="grey", lw=0.6, ls="--")
    q.loglog(hs, 0.02*(hs/hs[0])**2, color="grey", lw=0.6, ls=":")
    q.set_xticks(hs)
    q.set_xticklabels([f"{v:g}" for v in hs])
    q.minorticks_off()
    q.set_xlabel("root cell size (dashed, dotted: first and second order)")
    q.set_ylabel("rms departure")
    fs.save(fig, os.path.join(a.out, "fig_t19_smooth"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
