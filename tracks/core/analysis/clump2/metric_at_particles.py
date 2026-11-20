#!/usr/bin/env python3
"""Test D of tracks/core/JOURNAL-clump2.md: the spatial metric at the particles of the
moving cluster of test TC, from the restart files of the card runs. Each case is
restarted on a processor without a step (the time limit is already reached), with one
added output block that dumps the Z4c variables; the dump is read with
athenak/vis/python/bin_convert.py and its values are taken at the particles of the
snapshot of the same time (cell that holds the particle, finest level).

    metric_at_particles.py --cases "label=RUN_ID/name:RST:SNAP,..." [--out DIR]
                           [--exe .work/build_cpu/src/athena] [--v label=0.3,...]

RST and SNAP are the numbers of the restart file and of the particle snapshot (the
script checks that their times agree). Per case: mass-weighted means of the conformal
metric g~_xx, g~_yy, g~_zz, of psi = chi^(-1/4), of the lapse and of the shift;
sum m u_x, sum m u_x/gamma_xx^(1/2) (component along the unit vector of the x lines),
sum m W (against the history file); the coordinate speed of the rest-mass centre from
its budget, sum m (alpha gamma^xj u_j/W - beta^x)/sum m; profiles along the x axis.
Writes metric_at_particles.json and fig_metric_at_particles.{pdf,png} into --out. The
second restart file that AthenaK writes at the end of each restart is removed.
"""
import argparse
import glob
import json
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import bin_convert  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

EXTRA = """<output3>
file_type = bin
variable  = z4c
dt        = 1000.0
"""
NAMES = ("chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "alpha", "betax", "betay",
         "betaz", "Khat")


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
    return t, d


def table(path):
    rows = [ln.split() for ln in open(path) if not ln.startswith("#") and ln.strip()]
    n = min(len(r) for r in rows)
    a = np.array([r[:n] for r in rows], dtype=float)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def restart(exe, rst, d):
    """restart without a step; returns the path of the dump of the Z4c variables"""
    os.makedirs(d, exist_ok=True)
    extra = os.path.join(d, "extra.athinput")
    with open(extra, "w") as f:
        f.write(EXTRA)
    with open(os.path.join(d, "athena.log"), "w") as log:
        st = subprocess.run([exe, "-r", rst, "-i", extra, "-d", d], cwd=d, stdout=log,
                            stderr=subprocess.STDOUT,
                            env=dict(os.environ, OMP_NUM_THREADS="1")).returncode
    if st != 0:
        raise RuntimeError(f"restart of {rst} failed with status {st}")
    for fn in glob.glob(os.path.join(d, "rst", "*.rst")) + glob.glob(
            os.path.join(d, "rst", "*.rst.prt")):
        os.remove(fn)                 # the copy of the state this restart wrote
    dumps = sorted(glob.glob(os.path.join(d, "bin", "*.z4c.*.bin")))
    return dumps[-1]


def at_particles(fd, x):
    """values of NAMES in the cell that holds each particle (finest level first)"""
    geo = np.asarray(fd["mb_geometry"], dtype=float)
    lev = np.asarray(fd["mb_logical"])[:, 3]
    n = fd["nx1_out_mb"]
    out = {k: np.full(len(x), np.nan) for k in NAMES}
    todo = np.ones(len(x), dtype=bool)
    data = {k: fd["mb_data"]["z4c_" + k] for k in NAMES}
    for m in np.argsort(-lev):
        g = geo[m]
        inside = (todo & (x[:, 0] >= g[0]) & (x[:, 0] < g[1]) & (x[:, 1] >= g[2])
                  & (x[:, 1] < g[3]) & (x[:, 2] >= g[4]) & (x[:, 2] < g[5]))
        if not np.any(inside):
            continue
        idx = [np.clip(((x[inside, c] - g[2 * c]) / (g[2 * c + 1] - g[2 * c]) * n).astype(int),
                       0, n - 1) for c in range(3)]
        for k in NAMES:
            out[k][inside] = np.asarray(data[k][m])[idx[2], idx[1], idx[0]]
        todo &= ~inside
        if not np.any(todo):
            break
    out["level_min"] = int(lev.max()) if not np.any(todo) else -1
    return out, int(np.count_nonzero(todo))


def axis_profile(fd, xc):
    """the Z4c variables along the x axis: mean of the four lines of cells next to
    y = z = 0 on the finest level"""
    geo = np.asarray(fd["mb_geometry"], dtype=float)
    lev = np.asarray(fd["mb_logical"])[:, 3]
    n = fd["nx1_out_mb"]
    rows = {}
    for m in np.where(lev == lev.max())[0]:
        g = geo[m]
        dx = (g[1] - g[0]) / n
        yc = g[2] + (np.arange(n) + 0.5) * (g[3] - g[2]) / n
        zc = g[4] + (np.arange(n) + 0.5) * (g[5] - g[4]) / n
        jy = np.where(np.abs(yc) < dx)[0]
        kz = np.where(np.abs(zc) < dx)[0]
        if len(jy) == 0 or len(kz) == 0:
            continue
        xs = g[0] + (np.arange(n) + 0.5) * dx
        for k in ("chi", "gxx", "gyy", "alpha", "betax", "Khat"):
            a = np.asarray(fd["mb_data"]["z4c_" + k][m], dtype=float)
            line = a[np.ix_(kz, jy, np.arange(n))].mean(axis=(0, 1))
            for xv, val in zip(xs, line):
                rows.setdefault(float(xv), {}).setdefault(k, []).append(float(val))
    xs = np.array(sorted(rows))
    prof = {k: np.array([np.mean(rows[xv][k]) for xv in xs])
            for k in ("chi", "gxx", "gyy", "alpha", "betax", "Khat")}
    prof["x"] = xs - xc
    return prof


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--v", default="", help="label=speed,... (for the ratios to v)")
    ap.add_argument("--exe", default=os.path.join(WT, ".work", "build_cpu", "src", "athena"))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    speed = dict((kv.split("=")[0], float(kv.split("=")[1])) for kv in a.v.split(",") if kv)
    res, profs = {}, {}
    for item in a.cases.split(","):
        label, spec = item.split("=", 1)
        path, irst, isnap = spec.split(":")
        top = os.path.join(SCRATCH, path)
        rst = glob.glob(os.path.join(top, "rst", f"*.{int(irst):05d}.rst"))[0]
        snap = glob.glob(os.path.join(top, f"*.part.{int(isnap):05d}.bin"))[0]
        dump = restart(os.path.abspath(a.exe), rst, os.path.join(a.out, label))
        fd = bin_convert.read_binary(dump)
        t, d = read_snapshot(snap)
        if abs(t - fd["time"]) > 1e-9:
            raise RuntimeError(f"{label}: snapshot at {t}, restart at {fd['time']}")
        x, u, m = d[:, 0:3], d[:, 3:6], d[:, 6]
        f, missing = at_particles(fd, x)
        chi = f["chi"]
        gt = np.empty((len(m), 3, 3))
        gt[:, 0, 0], gt[:, 1, 1], gt[:, 2, 2] = f["gxx"], f["gyy"], f["gzz"]
        gt[:, 0, 1] = gt[:, 1, 0] = f["gxy"]
        gt[:, 0, 2] = gt[:, 2, 0] = f["gxz"]
        gt[:, 1, 2] = gt[:, 2, 1] = f["gyz"]
        gu = np.linalg.inv(gt) * chi[:, None, None]          # gamma^ij
        uu = np.einsum("pij,pj->pi", gu, u)                  # u^i (spatial part raised)
        W = np.sqrt(1.0 + np.einsum("pi,pi->p", uu, u))
        gam_xx = f["gxx"] / chi
        M0 = m.sum()
        mean = lambda q: float(np.sum(m * q) / M0)            # noqa: E731
        xc = (m[:, None] * x).sum(0) / M0
        o = dict(time=float(t), dump=os.path.relpath(dump, a.out), particles=int(len(m)),
                 particles_outside_finest_search=missing, xc=[float(c) for c in xc],
                 mean_gt_xx=mean(f["gxx"]), mean_gt_yy=mean(f["gyy"]),
                 mean_gt_zz=mean(f["gzz"]), mean_gt_xy=mean(f["gxy"]),
                 mean_psi=mean(chi ** -0.25), mean_alpha=mean(f["alpha"]),
                 mean_beta_x=mean(f["betax"]), mean_Khat=mean(f["Khat"]),
                 sum_m=float(M0), sum_mW=float(np.sum(m * W)),
                 sum_mux=float(np.sum(m * u[:, 0])),
                 sum_mux_orthonormal=float(np.sum(m * u[:, 0] / np.sqrt(gam_xx))),
                 budget_speed=mean(f["alpha"] * uu[:, 0] / W - f["betax"]),
                 budget_speed_matter=mean(f["alpha"] * uu[:, 0] / W),
                 bulk_speed_normal_frame=float(np.sum(m * u[:, 0] / np.sqrt(gam_xx))
                                               / np.sum(m * W)))
        h = table(glob.glob(os.path.join(top, "*.nrpic.hst"))[0])
        i = int(np.argmin(np.abs(h[:, 0] - t)))
        o["hst_sum_mW"], o["hst_sum_mux"] = float(h[i, 4]), float(h[i, 5])
        o["sum_mW_over_hst"] = o["sum_mW"] / o["hst_sum_mW"]
        # measured speed of the centre from the neighbouring snapshots
        snaps = sorted(glob.glob(os.path.join(top, "*.part.[0-9]*.bin")))
        j = snaps.index(snap)
        j0, j1 = (j, j + 1) if j == 0 else (j - 1, j)
        (t0, d0), (t1, d1) = read_snapshot(snaps[j0]), read_snapshot(snaps[j1])
        c0 = (d0[:, 6] * d0[:, 0]).sum() / d0[:, 6].sum()
        c1 = (d1[:, 6] * d1[:, 0]).sum() / d1[:, 6].sum()
        o["measured_speed"], o["measured_speed_interval"] = float((c1 - c0) / (t1 - t0)), [t0, t1]
        v = speed.get(label)
        if v:
            o["v"] = v
            o["budget_speed_over_v"] = o["budget_speed"] / v
            o["measured_speed_over_v"] = o["measured_speed"] / v
        res[label] = o
        profs[label] = axis_profile(fd, xc[0])
        print(label, json.dumps(o), flush=True)

    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.9, wspace=0.36)
    cols = fs.series_colors(max(len(profs), 2))
    for c, (label, p) in zip(cols, profs.items()):
        w = np.abs(p["x"]) < 16.0
        ax[0].plot(p["x"][w], p["gxx"][w] - 1.0, color=c, label=label)
        ax[0].plot(p["x"][w], p["gyy"][w] - 1.0, color=c, ls="--")
        ax[1].plot(p["x"][w], p["betax"][w], color=c)
        ax[2].plot(p["x"][w], p["Khat"][w], color=c)
    ax[0].set_ylabel(r"$\tilde g_{xx} - 1$ (solid), $\tilde g_{yy} - 1$ (dashed)")
    ax[1].set_ylabel(r"$\beta^x$")
    ax[2].set_ylabel(r"$\hat K$")
    for a_ in ax:
        a_.set_xlabel(r"$(x - x_c)/M$ on the axis of motion")
    ax[0].legend(loc="best", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_metric_at_particles"))
    with open(os.path.join(a.out, "metric_at_particles.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
