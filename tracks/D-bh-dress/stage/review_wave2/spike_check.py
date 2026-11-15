#!/usr/bin/env python3
"""Lead's wave-2 re-check of the Kerr spike package (JOURNAL.md, lead-wave2 prediction W5).

Reads only the AthenaK snapshots of run D-bh-dress-20261115-172611-1e40191 (12 processes,
48000 particles, a = 0.8, analytic Kerr-Schild metric, 20000 M) with my own reader, my own
Boyer-Lindquist radius from Kerr-Schild Cartesian coordinates and my own L_z = x u_y - y u_x;
none of the helper's analysis code. Also C_V from the Carter radial potential, written here.
Writes spike_check.json and spike_check.png into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172611-1e40191"
A = 0.8
EDGES = [0.0, 4.0, 6.0, 10.0, 16.0, 40.0]


def read_snap(path):
    with open(path, "rb") as fh:
        assert fh.read(8) == b"NRPSNAP1"
        t = float(np.frombuffer(fh.read(8), "<f8")[0])
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        _cyc = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(fh.read(4 * n), "<i4")
    return t, rec, tag


def r_bl(x, y, z, a=A):
    rho2 = x * x + y * y + z * z
    b = rho2 - a * a
    return np.sqrt(0.5 * (b + np.sqrt(b * b + 4 * a * a * z * z)))


def CV(r, E, Lz, a):
    D = r * r - 2 * r + a * a
    return (E * (r * r + a * a) - a * Lz) ** 2 / D - r * r + 2 * a * E * Lz - a * a * E * E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    dirs = sorted(glob.glob(os.path.join(RUN, "kerr_*")), key=lambda p: int(p.rsplit("_", 1)[1]))
    nsnap = len(glob.glob(os.path.join(dirs[0], "kerr.part.*.bin")))
    times = np.zeros(nsnap)
    counts = np.zeros((nsnap, len(EDGES) - 1))
    lzsum = np.zeros((nsnap, len(EDGES) - 1))
    lz2sum = np.zeros((nsnap, len(EDGES) - 1))
    ntot = np.zeros(nsnap, int)
    rmin = np.inf
    for k in range(nsnap):
        for d in dirs:
            t, rec, _ = read_snap(os.path.join(d, f"kerr.part.{k:05d}.bin"))
            x, y, z, ux, uy, uz = rec[:, :6].T
            r = r_bl(x, y, z)
            lz = x * uy - y * ux
            rmin = min(rmin, float(r.min()))
            idx = np.digitize(r, EDGES) - 1
            ok = (idx >= 0) & (idx < len(EDGES) - 1)
            counts[k] += np.bincount(idx[ok], minlength=len(EDGES) - 1)
            lzsum[k] += np.bincount(idx[ok], weights=lz[ok], minlength=len(EDGES) - 1)
            lz2sum[k] += np.bincount(idx[ok], weights=lz[ok] ** 2, minlength=len(EDGES) - 1)
            ntot[k] += len(r)
        times[k] = t
    early = times <= 0.5 * times[-1]
    late = ~early
    ratio = counts[late].mean(0) / counts[early].mean(0)
    lzmean = lzsum / counts
    lzstd = np.sqrt(lz2sum / counts - lzmean ** 2)
    lzse = lzstd / np.sqrt(counts)
    labels = [f"{EDGES[i]:g}-{EDGES[i + 1]:g} Gm" for i in range(len(EDGES) - 1)]
    out = dict(nsnap=nsnap, t_end=float(times[-1]), n_particles=sorted(set(ntot.tolist())),
               r_min_all=rmin,
               counts_t0=dict(zip(labels, counts[0].tolist())),
               late_over_early=dict(zip(labels, ratio.tolist())),
               poisson_sigma_single=dict(zip(labels, (1 / np.sqrt(counts[0])).tolist())),
               lz_mean_t0=dict(zip(labels, lzmean[0].tolist())),
               lz_mean_late=dict(zip(labels, lzmean[late].mean(0).tolist())),
               lz_maxdev_in_se=dict(zip(labels, (np.abs(lzmean - lzmean[0]) / lzse).max(0).tolist())))
    # C_V check (FdRW crit_orbit caption: 10.3 for a = 0.75, E = 0.97, Lz = 2)
    a = 0.75
    rp = 1 + np.sqrt(1 - a * a)
    rr = np.linspace(rp + 1e-6, 30.0, 2000001)
    cv = CV(rr, 0.97, 2.0, a)
    # local minimum above the horizon (C_V -> +inf at r_+)
    i = np.argmin(cv[: np.searchsorted(rr, 6.0)])
    out["Ccrit_a0.75_E0.97_Lz2"] = dict(local_min=float(cv[i]), r_u=float(rr[i]),
                                        CV_at_30=float(CV(30.0, 0.97, 2.0, a)),
                                        CV_at_15=float(CV(15.0, 0.97, 2.0, a)))
    with open(os.path.join(args.out, "spike_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(8, 5.0), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.1, top=0.97, hspace=0.05)
    cols = fs.series_colors(len(labels))
    for j, lab in enumerate(labels):
        axs[0].plot(times, counts[:, j] / counts[0, j], color=cols[j], lw=1.0, label=lab)
        axs[1].plot(times, lzmean[:, j], color=cols[j], lw=1.0)
        fs.band(axs[1], times, lzmean[:, j] - lzse[:, j], lzmean[:, j] + lzse[:, j], cols[j])
    axs[0].set_ylabel(r"$N(t)/N(0)$ in range")
    axs[0].legend(frameon=False, ncol=3)
    axs[1].set_ylabel(r"mean $L_z$ [Gm]")
    axs[1].set_xlabel(r"$t$ [Gm]", labelpad=-2)
    fs.save(fig, os.path.join(args.out, "spike_check"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
