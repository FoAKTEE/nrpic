#!/usr/bin/env python3
"""V5b: particle module on 1, 2, 4 MPI ranks (core-v0.5), periodic cosmology with Z4c.

Run core-20261119-163641-ddb47b0, case t6_cosmo_east (claim, interfaces/mpi.md row 6:
positions 1.6e-14, sources at particles 1.3e-14, identity 1e-14 on 1, 2, 4 ranks).
Own readers: snapshots (v7a_point.read_snap), trajmet records of 17 float64 (docs/FORMATS.md
line 122: time, tag, alpha, beta^i, gamma_ij (6), proper time, E, S_x, S_y, S_z), history
columns by name.
- positions: largest |x(np) - x(np1)| over all particles and snapshots, matched by tag,
  periodic difference in a box of side 4 (input x1min = 0, x1max = 4);
- sources at particles: largest relative difference of E, S_i in trajmet;
- deposition identity per rank count: max |int_E / sum_mW - 1| over the history.

usage: v5_mpi.py CASEDIR OUTDIR
"""
import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v7a_point import read_snap  # noqa: E402

L = 4.0


def read_hst(path):
    names = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") and "[1]=" in line:
                names = [m.group(1) for m in re.finditer(r"\[\d+\]=(\S+)", line)]
                break
    d = np.loadtxt(path, comments="#", ndmin=2)
    return {n: d[:, i] for i, n in enumerate(names)}


def main():
    cd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    snaps1 = sorted(glob.glob(os.path.join(cd, "np1", "east.part.*.bin")))
    tm1 = np.fromfile(os.path.join(cd, "np1", "east.trajmet.bin"), "<f8").reshape(-1, 17)
    series = {}
    for np_ in (1, 2, 4):
        h = read_hst(os.path.join(cd, f"np{np_}", "east.nrpic.hst"))
        ident = np.abs(h["int_E"] / h["sum_mW"] - 1)
        entry = {"identity_max": float(ident.max()), "n_hist": int(len(ident))}
        series[np_] = (h["time"], ident)
        if np_ > 1:
            dx_max, per_snap = 0.0, []
            for s1 in snaps1:
                sn = os.path.join(cd, f"np{np_}", os.path.basename(s1))
                t1, _, r1, g1, _, _ = read_snap(s1)
                tn, _, rn, gn, _, _ = read_snap(sn)
                assert abs(t1 - tn) < 1e-12
                o1, on = np.argsort(g1), np.argsort(gn)
                assert np.array_equal(g1[o1], gn[on])
                d = rn[on, :3] - r1[o1, :3]
                d -= L * np.round(d / L)
                m = float(np.abs(d).max())
                per_snap.append((float(t1), m))
                dx_max = max(dx_max, m)
            tmn = np.fromfile(os.path.join(cd, f"np{np_}", "east.trajmet.bin"), "<f8").reshape(-1, 17)
            k1 = np.lexsort((tm1[:, 1], tm1[:, 0]))
            kn = np.lexsort((tmn[:, 1], tmn[:, 0]))
            a, b = tm1[k1], tmn[kn]
            assert np.array_equal(a[:, :2], b[:, :2])
            src = a[:, 13:17]
            scale = np.maximum(np.abs(src).max(axis=0), 1e-300)
            rel_src = float((np.abs(b[:, 13:17] - src) / scale).max())
            mscale = np.maximum(np.abs(a[:, 2:12]).max(axis=0), 1e-300)
            rel_met = float((np.abs(b[:, 2:12] - a[:, 2:12]) / mscale).max())
            entry.update({"positions_max_abs": dx_max, "positions_per_snapshot": per_snap,
                          "sources_at_particles_max_rel_to_column_max": rel_src,
                          "metric_at_particles_max_rel_to_column_max": rel_met, "n_traj_records": int(len(a))})
        res[f"np{np_}"] = entry
    with open(os.path.join(outdir, "v5_mpi.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "positions_per_snapshot"} for k, v in res.items()}, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    for i, np_ in enumerate((1, 2, 4)):
        t, ident = series[np_]
        axs[0].semilogy(t, np.maximum(ident, 1e-17), color=fs.SERIES[i], lw=1, label=f"{np_} rank(s)")
        if np_ > 1:
            ps = np.array(res[f"np{np_}"]["positions_per_snapshot"])
            axs[1].semilogy(ps[:, 0], np.maximum(ps[:, 1], 1e-18), "o-", color=fs.SERIES[i], ms=3, lw=1,
                            label=f"{np_} ranks vs 1")
    axs[0].set_xlabel("t")
    axs[0].set_ylabel(r"$|\int E / \sum mW - 1|$")
    axs[0].legend(fontsize=7)
    axs[1].set_xlabel("t")
    axs[1].set_ylabel(r"max $|\Delta x|$ of the particles")
    axs[1].legend(fontsize=7)
    fig.suptitle("V5b: periodic cosmology on 1, 2, 4 MPI ranks, run core-20261119-163641-ddb47b0", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v5_mpi"))


if __name__ == "__main__":
    main()
