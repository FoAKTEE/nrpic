#!/usr/bin/env python3
"""Outcome of test TE of tracks/core/JOURNAL-clump2.md: two equilibrium clusters on a
quasi-circular orbit (problems/clump/cluster_binary.athinput). Reads the particle
snapshots (centre, radii and momentum of each cluster from its species) and the two
history files, prints the measured numbers next to the predicted bands and writes
binary_evolution_check.json and fig_binary_evolution*.{pdf,png} into --out.

    binary_evolution_check.py --dir SCRATCH_RELATIVE_RUN_DIR [--out DIR] [--tmin 40]
                              [--tmax T] [--tag TAG]

--tmax cuts the snapshots and histories at T (to compare a longer run with a shorter
one over the same interval); --tag is appended to the names of the files written.
"""
import argparse
import glob
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

FRACS = (0.10, 0.25, 0.50, 0.75, 0.90)
# two point masses of ADM mass 1 at coordinate separation 30 (input file header)
MTOT, NU, R0 = 2.0, 0.25, 30.0
OMEGA_N = math.sqrt(MTOT / R0 ** 3)
OMEGA_1PN = OMEGA_N * math.sqrt(1.0 - (3.0 - NU) * MTOT / R0)
P_1PN = 0.5 * math.sqrt(MTOT / R0) * (1.0 + 2.0 * MTOT / R0)


def read_snapshot(path):
    """time and the arrays (x, u, m, species) of one NRPSNAP1 file"""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRPSNAP1":
            raise ValueError(f"{path}: not a snapshot")
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
        np.fromfile(f, dtype=np.int32, count=n)            # tags
        sp = np.fromfile(f, dtype=np.int32, count=n)
    return t, d, sp


def table(path):
    rows = [ln.split() for ln in open(path) if not ln.startswith("#") and ln.strip()]
    n = min(len(r) for r in rows)
    a = np.array([r[:n] for r in rows], dtype=float)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def cluster_state(d, sel):
    """rest-mass centre, radii of FRACS about it, sum m u_i of the particles sel"""
    a = d[sel]
    m = a[:, 6]
    c = (m[:, None] * a[:, 0:3]).sum(0) / m.sum()
    dx = a[:, 0:3] - c
    r = np.sqrt(np.sum(dx * dx, axis=1))
    o = np.argsort(r)
    cm = np.cumsum(m[o]) / m.sum()
    rad = [float(r[o][min(np.searchsorted(cm, f), len(r) - 1)]) for f in FRACS]
    pu = (m[:, None] * a[:, 3:6]).sum(0)
    # axis ratios of the second moment (tidal deformation)
    q = np.einsum("p,pi,pj->ij", m, dx, dx) / m.sum()
    ev = np.sort(np.linalg.eigvalsh(q))
    return c, rad, pu, float(math.sqrt(ev[0] / ev[2])), len(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="run directory relative to scratch/core")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--tmin", type=float, default=40.0,
                    help="start of the fits (after the gauge transient)")
    ap.add_argument("--tmax", type=float, default=None)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    top = os.path.join(SCRATCH, a.dir)
    os.makedirs(a.out, exist_ok=True)
    snaps = sorted(glob.glob(os.path.join(top, "*.part.[0-9]*.bin")))
    ts, cs, rads, pus, axr, nps = [], [], [], [], [], []
    for p in snaps:
        t, d, sp = read_snapshot(p)
        if a.tmax is not None and t > a.tmax + 1e-9:
            break
        row_c, row_r, row_p, row_a, row_n = [], [], [], [], []
        for k in (0, 1):
            c, rad, pu, ar, n = cluster_state(d, sp == k)
            row_c.append(c)
            row_r.append(rad)
            row_p.append(pu)
            row_a.append(ar)
            row_n.append(n)
        ts.append(t)
        cs.append(row_c)
        rads.append(row_r)
        pus.append(row_p)
        axr.append(row_a)
        nps.append(row_n)
    t = np.array(ts)
    c = np.array(cs)                 # (nt, 2, 3)
    rad = np.array(rads)             # (nt, 2, 5)
    pu = np.array(pus)               # (nt, 2, 3)
    axr = np.array(axr)              # (nt, 2)
    sep = c[:, 1] - c[:, 0]
    D = np.sqrt(np.sum(sep ** 2, axis=1))
    phi = np.unwrap(np.arctan2(sep[:, 1], sep[:, 0]))
    phi -= phi[0]
    com = 0.5 * (c[:, 0] + c[:, 1])

    h = table(glob.glob(os.path.join(top, "*.nrpic.hst"))[0])
    z = table(glob.glob(os.path.join(top, "*.z4c.user.hst"))[0])
    if a.tmax is not None:
        h, z = h[h[:, 0] <= a.tmax + 1e-9], z[z[:, 0] <= a.tmax + 1e-9]
    ht, alpha_min, sum_mu, np_h = h[:, 0], h[:, 15], h[:, 5:8], h[:, 2]
    zt, Hn, Mn = z[:, 0], np.sqrt(z[:, 3]), np.sqrt(z[:, 4])

    w = t >= a.tmin
    res = dict(dir=a.dir, t_end=float(t[-1]), n_snapshots=int(len(t)), tmin_fit=a.tmin,
               omega_newton=OMEGA_N, omega_1pn=OMEGA_1PN, P_1pn=P_1PN,
               particles_start=[int(x) for x in nps[0]], particles_end=[int(x) for x in nps[-1]],
               np_hst_start=float(np_h[0]), np_hst_end=float(np_h[-1]),
               D_start=float(D[0]), D_end=float(D[-1]), D_min=float(D.min()),
               D_max=float(D.max()))
    if np.count_nonzero(w) >= 3:
        res["D_min_after_tmin"] = float(D[w].min())
        res["D_max_after_tmin"] = float(D[w].max())
        res["dDdt_fit_after_tmin"] = float(np.polyfit(t[w], D[w], 1)[0])
        om = np.polyfit(t[w], phi[w], 1)[0]
        res["omega_fit_after_tmin"] = float(om)
        res["omega_fit_over_1pn"] = float(om / OMEGA_1PN)
        res["omega_fit_over_newton"] = float(om / OMEGA_N)
    for tq in (50.0, 125.0):
        if t[-1] >= tq - 1e-9:
            res[f"D_{tq:g}"] = float(np.interp(tq, t, D))
            res[f"phase_{tq:g}"] = float(np.interp(tq, t, phi))
            res[f"phase_{tq:g}_1pn"] = OMEGA_1PN * tq
    if t[-1] >= 50.0:
        res["omega_0_50_over_1pn"] = float(np.interp(50.0, t, phi) / 50.0 / OMEGA_1PN)
    res["phase_end"] = float(phi[-1])
    res["phase_end_1pn"] = float(OMEGA_1PN * t[-1])
    res["phase_end_newton"] = float(OMEGA_N * t[-1])
    res["omega_mean_0_end"] = float(phi[-1] / t[-1]) if t[-1] > 0 else None
    res["com_max_abs"] = float(np.max(np.abs(com)))
    rr = rad / rad[0][None, :, :]
    res["radii_start"] = rad[0].tolist()
    res["radii_ratio_min"] = rr.min(0).tolist()
    res["radii_ratio_max"] = rr.max(0).tolist()
    res["radii_ratio_end"] = rr[-1].tolist()
    res["axis_ratio_start"] = axr[0].tolist()
    res["axis_ratio_min"] = axr.min(0).tolist()
    Pmag = np.sqrt(np.sum(pu ** 2, axis=2))
    res["P_cluster_start"] = Pmag[0].tolist()
    res["P_cluster_rel_min"] = (Pmag.min(0) / Pmag[0] - 1.0).tolist()
    res["P_cluster_rel_max"] = (Pmag.max(0) / Pmag[0] - 1.0).tolist()
    res["P_cluster_rel_end"] = (Pmag[-1] / Pmag[0] - 1.0).tolist()
    res["sum_mu_total_start"] = sum_mu[0].tolist()
    res["sum_mu_total_max_abs"] = float(np.max(np.abs(sum_mu)))
    res["alpha_min"] = [float(alpha_min[0]), float(alpha_min.min()), float(alpha_min.max()),
                        float(alpha_min[-1])]
    i5 = zt >= 5.0
    res["H_norm"] = [float(Hn[0]), float(Hn.max()), float(Hn[-1])]
    res["M_norm"] = [float(Mn[0]), float(Mn.max()), float(Mn[-1])]
    if np.any(i5):
        h5, m5 = float(np.interp(5.0, zt, Hn)), float(np.interp(5.0, zt, Mn))
        res["H_over_t5_max_after_5"] = float(np.max(Hn[i5]) / h5)
        res["M_over_t5_max_after_5"] = float(np.max(Mn[i5]) / m5)

    # ---- figures
    fs.use_style()
    col = (fs.PAL["blue"], fs.PAL["red"])
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28,
                        hspace=0.27)
    tt = np.linspace(0.0, t[-1], 200)
    for k in (0, 1):
        ax[0, 0].plot(c[:, k, 0], c[:, k, 1], color=col[k], label=f"cluster {k}")
        s = 1 if k == 1 else -1
        ax[0, 0].plot(s * 15.0 * np.cos(OMEGA_1PN * tt), s * 15.0 * np.sin(OMEGA_1PN * tt),
                      **fs.GUIDE)
    ax[0, 0].set_aspect("equal")
    ax[0, 0].set_xlabel(r"$x/M$")
    ax[0, 0].set_ylabel(r"$y/M$")
    ax[0, 0].legend(loc="center", fontsize=8)
    ax[0, 1].plot(t, phi, color="k", label="measured")
    ax[0, 1].plot(tt, OMEGA_1PN * tt, color=fs.PAL["green"], ls="--",
                  label="first post-Newtonian")
    ax[0, 1].plot(tt, OMEGA_N * tt, color=fs.PAL["orange"], ls=":", label="Newtonian")
    ax[0, 1].set_xlabel(r"$t/M$")
    ax[0, 1].set_ylabel(r"orbital phase (rad)")
    ax[0, 1].legend(loc="upper left", fontsize=8)
    ax[1, 0].plot(t, D, color="k")
    ax[1, 0].axhline(R0, **fs.GUIDE)
    ax[1, 0].set_xlabel(r"$t/M$")
    ax[1, 0].set_ylabel(r"coordinate separation $D/M$")
    for k in (0, 1):
        for j, ls in ((0, ":"), (2, "-"), (4, "--")):
            ax[1, 1].plot(t, rr[:, k, j], color=col[k], ls=ls,
                          label=(f"cluster {k}" if j == 2 else None))
    ax[1, 1].set_xlabel(r"$t/M$")
    ax[1, 1].set_ylabel(r"radii of 10, 50, 90 per cent$/$start")
    ax[1, 1].legend(loc="best", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_binary_evolution" + a.tag))

    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.38)
    ax[0].plot(ht, alpha_min, color="k")
    ax[0].set_ylabel("minimum lapse")
    for k in (0, 1):
        ax[1].plot(t, Pmag[:, k] / P_1PN, color=col[k], label=f"cluster {k}")
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_ylabel(r"$|\sum m u_i| / P_{\rm 1PN}$")
    ax[1].legend(loc="best", fontsize=8)
    ax[2].plot(zt, Hn, color=fs.PAL["blue"], label="$H$")
    ax[2].plot(zt, Mn, color=fs.PAL["red"], label="$M$")
    ax[2].set_yscale("log")
    ax[2].set_ylabel("constraint norms")
    ax[2].legend(loc="best", fontsize=8)
    for a_ in ax:
        a_.set_xlabel(r"$t/M$")
    fs.save(fig, os.path.join(a.out, "fig_binary_evolution_history" + a.tag))

    with open(os.path.join(a.out, "binary_evolution_check" + a.tag + ".json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
