#!/usr/bin/env python3
"""A2X follow-up (periodic_threshold JOURNAL, batch 23): is the code's probe clock the proper time of a dust worldline?

The probe of `<particles> probe_x1..3` is a fixed COORDINATE point; column 15 of nrpic.hst is the proper time of the
normal observer there, int alpha dt (athenak/src/particles/nrpic_io.cpp, NrpicProbe). It equals the proper time of the
particle at that point only if the particle stays there (x = const) with W = 1, i.e. u_i = 0 (then dtau = alpha dt).
This script follows the particle nearest the probe at t = 0 through the snapshots: its coordinate offset from the
probe and its covariant |u_i|, against the same quantities for its six lattice neighbours.

    a2_probe_check.py --run DIR --out DIR [--probe 0.001 0.001 0.001] [--tmax 80]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
    return time, rec[:, 0:3].copy(), rec[:, 3:6].copy(), tag.copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--probe", type=float, nargs=3, default=[0.001, 0.001, 0.001])
    ap.add_argument("--tmax", type=float, default=80.0)
    ap.add_argument("--h", type=float, default=20.0 / 64)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.run, "peak.part.*.bin")))
    t0, x0, u0, tag0 = read_snapshot(files[0])
    p = np.array(a.probe)
    i0 = int(np.argmin(np.sum((x0 - p) ** 2, axis=1)))
    ptag = int(tag0[i0])
    d0 = np.sqrt(np.sum((x0 - x0[i0]) ** 2, axis=1))
    nb = np.argsort(d0)[1:7]
    nbtags = tag0[nb]
    rows = []
    for f in files:
        t, x, u, tag = read_snapshot(f)
        if t > a.tmax:
            break
        order = np.argsort(tag)
        k = order[np.searchsorted(tag[order], ptag)]
        kn = order[np.searchsorted(tag[order], nbtags)]
        rows.append(dict(t=t, offset_from_probe=float(np.sqrt(np.sum((x[k] - p) ** 2))),
                         x=[float(v) for v in x[k]], u_abs=float(np.sqrt(np.sum(u[k] ** 2))),
                         u=[float(v) for v in u[k]],
                         neighbours_u_abs=[float(v) for v in np.sqrt(np.sum(u[kn] ** 2, axis=1))]))
        print(f"t {t:7.2f}  offset {rows[-1]['offset_from_probe']:.2e}  |u| {rows[-1]['u_abs']:.2e}  "
              f"neighbours |u| max {max(rows[-1]['neighbours_u_abs']):.3f}", flush=True)
    res = dict(run=os.path.abspath(a.run), probe=list(p), particle_tag=ptag, particle_x0=[float(v) for v in x0[i0]],
               rows=rows, max_offset=max(r["offset_from_probe"] for r in rows),
               max_u_abs=max(r["u_abs"] for r in rows))
    json.dump(res, open(os.path.join(a.out, "a2_probe.json"), "w"), indent=1)
    print("max offset", res["max_offset"], "max |u|", res["max_u_abs"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, HERE)
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(3.6, 2.8))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.17, top=0.9)
    tt = [r["t"] for r in rows]
    ax.semilogy(tt, [max(r["offset_from_probe"], 1e-17) for r in rows], "o-", ms=3, color=fs.PAL["red"],
                label="particle offset from probe")
    ax.semilogy(tt, [max(r["u_abs"], 1e-17) for r in rows], "s-", ms=3, color=fs.PAL["blue"], label="its covariant |u|")
    ax.semilogy(tt, [max(max(r["neighbours_u_abs"]), 1e-17) for r in rows], "^--", ms=3, color="0.5",
                label="neighbours' |u| (max)")
    ax.set_xlabel("coordinate time t")
    ax.set_ylabel("value")
    ax.set_title("S1L: the particle at the probe", fontsize=8)
    ax.legend(fontsize=6)
    fig.savefig(os.path.join(a.out, "fig_a2_probe.png"), dpi=150)


if __name__ == "__main__":
    main()
