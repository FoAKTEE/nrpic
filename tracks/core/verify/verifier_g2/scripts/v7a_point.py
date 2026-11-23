#!/usr/bin/env python3
"""V7a: Newtonian mode (core-v0.3), force of a point mass on massless tracers.

Own reader of <base>.part.NNNNN.bin (docs/FORMATS.md line 123: "NRPSNAP1", float64
time, int64 N, int64 cycle, N x 7 float64 (x^i, u_i, m), N int32 tags, N int32
species, N float64 proper time). Reader check: the file size must equal the layout, the
snapshot at t = 0 must hold one particle of mass 1 at the centre of point.json and
tracers at rest.
Acceleration of a tracer: (u(t1) - u(t0)) / (t1 - t0) over the single kick-drift-kick
step of dt = 1e-6 from rest. Reference: G = 1, a = -M (x - x_c) / |x - x_c|^3.

usage: v7a_point.py RUNDIR OUTDIR
"""
import json
import os
import struct
import sys

import numpy as np


def read_snap(path):
    with open(path, "rb") as fh:
        b = fh.read()
    assert b[:8] == b"NRPSNAP1"
    (t,) = struct.unpack_from("<d", b, 8)
    n, cyc = struct.unpack_from("<2q", b, 16)
    off = 32
    rec = np.frombuffer(b, "<f8", n * 7, off).reshape(n, 7)
    off += 56 * n
    tags = np.frombuffer(b, "<i4", n, off)
    off += 4 * n
    spec = np.frombuffer(b, "<i4", n, off)
    off += 4 * n
    tau = np.frombuffer(b, "<f8", n, off)
    off += 8 * n
    assert off == len(b), (off, len(b))
    return t, cyc, rec, tags, spec, tau


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    pj = json.load(open(os.path.join(rd, "point.json")))
    xc = np.array(pj["center"])
    mass = pj["mass"]
    res = {}
    plots = {}
    for N in (32, 64):
        t0, c0, r0, g0, s0, _ = read_snap(os.path.join(rd, f"n{N}", "newton.part.00000.bin"))
        t1, c1, r1, g1, s1, _ = read_snap(os.path.join(rd, f"n{N}", "newton.part.00001.bin"))
        o0, o1 = np.argsort(g0), np.argsort(g1)
        r0, r1, g = r0[o0], r1[o1], g0[o0]
        assert np.array_equal(g, g1[o1])
        heavy = r0[:, 6] > 0
        check = {"n_massive": int(heavy.sum()), "massive_m": float(r0[heavy, 6].sum()),
                 "massive_pos_minus_center": float(np.max(np.abs(r0[heavy, :3] - xc))),
                 "max_abs_u_t0": float(np.max(np.abs(r0[:, 3:6]))), "t0": t0, "t1": t1}
        tr = ~heavy
        acc = (r1[tr, 3:6] - r0[tr, 3:6]) / (t1 - t0)
        d = r0[tr, :3] - xc
        r = np.linalg.norm(d, axis=1)
        aref = -mass * d / r[:, None] ** 3
        rel = np.linalg.norm(acc - aref, axis=1) / np.linalg.norm(aref, axis=1)
        far = r >= 0.5
        dx = 4.0 / N
        res[N] = {"reader_check": check, "n_tracers": int(tr.sum()), "n_far": int(far.sum()),
                  "far_rms_rel": float(np.sqrt(np.mean(rel[far] ** 2))),
                  "far_max_rel": float(rel[far].max())}
        plots[N] = (r / dx, rel)
    res["order_far_rms"] = float(np.log2(res[32]["far_rms_rel"] / res[64]["far_rms_rel"]))
    with open(os.path.join(outdir, "v7a_point.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.3, 3.0))
    for i, N in enumerate((32, 64)):
        x, y = plots[N]
        ax.loglog(x, y, ".", ms=2, color=fs.SERIES[i], label=f"N = {N}: far rms {res[N]['far_rms_rel']:.3e}")
    xx = np.logspace(0.5, 1.8, 20)
    ax.loglog(xx, 0.5 / xx ** 2, **fs.GUIDE, label=r"$\propto (dx/r)^2$")
    ax.set_xlabel(r"$r/dx$")
    ax.set_ylabel("relative force error of a tracer")
    ax.legend(fontsize=7)
    ax.set_title("V7a: point mass, run core-20261115-150209-3629622", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v7a_point"))


if __name__ == "__main__":
    main()
