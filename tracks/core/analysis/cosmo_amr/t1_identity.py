#!/usr/bin/env python3
"""T1 of the work package cosmo-amr: the deposition identity on a refined periodic mesh
(prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t1_identity.py --new NEW_EXE --out DIR [--cores N]

4096 particles with random positions, momenta (|u_i| < 0.5) and masses in the box
[-3, 3)^3 of the homogeneous universe, root 24^3, MeshBlocks 8^3.  Static refinement:
level 1 on the central block, level 2 on its octant [-1, 0]^3; the neighbour rule then
refines the seven root blocks on the negative sides, so that the periodic faces x, y, z
= +-3 separate root blocks from level-1 blocks.  Cases: cloud cic, tsc, pcs; cloud level
finest, capped at the root, adaptive; deposit_fine_shape off and on; filter off; plus a
uniform mesh, and the filter on the refined and on the uniform mesh.  Four cycles.
The identity: mesh integral of the deposited sqrt(gamma) E equals the particle sum of
m W, and the same for the three momentum components (columns of .nrpic.hst)."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A

L, N, NB = 6.0, 24, 8


def base(ic, refined=True):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo/flrw.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": N, f"x{d}min": -L/2, f"x{d}max": L/2})
        b.set("meshblock", **{f"nx{d}": NB})
    b.set("time", tlim=10.0, nlim=4)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"), snap_dt=-1.0,
          probe_x1=0.01, probe_x2=0.01, probe_x3=0.01, cstat_dcycle=1, hist_dcycle=1)
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    b.set("output1", file_type="hst", dt=0.5)
    if refined:
        b.set("mesh_refinement", refinement="static", max_nmb_per_rank=256)
        b.set("refined_region1", level=1, x1min=-0.5, x1max=0.5, x2min=-0.5, x2max=0.5,
              x3min=-0.5, x3max=0.5)
        b.set("refined_region2", level=2, x1min=-0.4, x1max=-0.1, x2min=-0.4, x2max=-0.1,
              x3min=-0.4, x3max=-0.1)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--np", type=int, default=4096)
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    os.makedirs(a.out, exist_ok=True)
    from nrp_io import write_particles
    ic = os.path.join(a.out, "ic")
    os.makedirs(ic, exist_ok=True)
    rng = np.random.default_rng(20261119)
    x = rng.uniform(-L/2, L/2, (a.np, 3))
    u = rng.uniform(-0.5, 0.5, (a.np, 3))
    rho0 = 3.0/(8.0*np.pi)
    m = rho0*L**3/a.np*rng.uniform(0.5, 1.5, a.np)
    write_particles(os.path.join(ic, "particles.nrp"), x, u, m)

    cs = {}
    for shape in ("cic", "tsc", "pcs"):
        for mode in ("finest", "root", "adapt"):
            for fine in (False, True):
                b = base(ic)
                b.set("particles", deposit_shape=shape, nfilter=0, filter_compensate=False,
                      deposit_adaptive=(mode == "adapt"),
                      deposit_max_level=(0 if mode == "root" else 31))
                if fine:
                    b.set("particles", deposit_fine_shape=True)
                cs[f"{shape}-{mode}-{'lin' if fine else 'const'}"] = b
    u0 = base(ic, refined=False)
    u0.set("particles", nfilter=0, filter_compensate=False)
    cs["uniform-cic"] = u0
    cs["uniform-cic-filter"] = base(ic, refined=False).set(
        "particles", nfilter=2, filter_compensate=True)
    cs["cic-root-lin-filter"] = base(ic).set(
        "particles", nfilter=2, filter_compensate=True, deposit_max_level=0,
        deposit_fine_shape=True)
    cs["cic-root-const-filter"] = base(ic).set(
        "particles", nfilter=2, filter_compensate=True, deposit_max_level=0)
    names = list(cs)
    rcs = A.run_many([(a.new, cs[n], os.path.join(a.out, n), "flrw", (), None)
                      for n in names], a.cores)
    res = {}
    for n, rc in zip(names, rcs):
        h = A.read_hst(os.path.join(a.out, n, "flrw.nrpic.hst"))
        smw = h["sum_mW"]
        r = dict(exit=rc[0], wall=round(rc[1], 1), nmb=int(h["nmb"][0]),
                 records=len(smw), np=int(h["np"][-1]),
                 n_escaped=int(h["n_escaped"][-1]), n_excised=int(h["n_excised"][-1]),
                 cells=int(h["nmb"][0])*NB**3,
                 id_E=float(np.max(np.abs(h["int_E"]/smw - 1.0))),
                 id_S=float(max(np.max(np.abs(h["int_S" + c] - h["sum_mu" + c])/smw)
                                for c in "xyz")),
                 idf_E=float(np.max(np.abs(h["int_E_filtered"]/smw - 1.0))),
                 idf_S=float(max(np.max(np.abs(h["int_S%s_filtered" % c]
                                                - h["sum_mu" + c])/smw) for c in "xyz")),
                 E_min_over_max=float(np.min(h["E_min"]/h["E_max"])))
        res[n] = r
        print(f"{n:24s} exit {rc[0]} nmb {r['nmb']:4d} id_E {r['id_E']:.2e} id_S "
              f"{r['id_S']:.2e} filtered {r['idf_E']:.2e} {r['idf_S']:.2e} "
              f"Emin/Emax {r['E_min_over_max']:.2e}")
    with open(os.path.join(a.out, "t1_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(8.0, 4.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.36, top=0.96)
    xs = np.arange(len(names))
    floor = 1e-17
    ax.semilogy(xs, [max(res[n]["id_E"], floor) for n in names], "o", color=fs.PAL["red"],
                label=r"$|\int\!E\sqrt{\gamma}\,dV/\sum mW-1|$")
    ax.semilogy(xs, [max(res[n]["id_S"], floor) for n in names], "s", mfc="none",
                color=fs.PAL["blue"], label=r"$\max_i|\int\!S_i\sqrt{\gamma}\,dV-\sum mu_i|/\sum mW$")
    ax.semilogy(xs, [max(res[n]["idf_E"], floor) for n in names], "x",
                color=fs.PAL["green"], label="energy after the source filter")
    ax.axhline(1e-13, **fs.GUIDE)
    ax.semilogy(xs, [res[n]["cells"]*1.1e-16 for n in names], "-", color="grey", lw=1.0,
                label=r"cells $\times\,1.1\times10^{-16}$ (running sum)")
    ax.set_xticks(xs)
    ax.set_xticklabels(names, rotation=90, fontsize=7)
    ax.set_ylabel("departure from the identity")
    ax.set_ylim(1e-17, 1e-1)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_t1_identity"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
