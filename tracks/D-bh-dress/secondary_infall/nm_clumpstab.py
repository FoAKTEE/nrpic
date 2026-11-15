#!/usr/bin/env python3
"""Motion of the clump (the stand-in for the hole) in the mesh: centre of mass, its
velocity, the total momentum of the history, against time, for one or more runs of
nm_run.py (analysis of AthenaK output only). Fits the exponential growth rate of the
displacement while it is below 0.1 dx. Writes nm_clumpstab.json and a figure.

Usage: python3 nm_clumpstab.py --run LABEL:RUNDIR [--run ...]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle  # noqa: E402
from nrpic import newton as nw   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--run", action="append", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 5.0), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.1, top=0.97, hspace=0.05)
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    summary = {}
    for i, spec in enumerate(a.run):
        lab, d = spec.split(":", 1)
        with open(os.path.join(d, "setup.json")) as f:
            p = json.load(f)
        with open(os.path.join(d, "nm_run.json")) as f:
            meta = json.load(f)
        dx = meta["dx"]
        # the reference point: the vertex or cell centre the configuration was centred on
        nx = meta["nx"]
        sc = np.asarray(meta["args"].get("shift_cells", [0, 0, 0]), float)
        ref = np.round(sc * 2) / 2 * dx      # the vertex (0) or cell centre (1/2) nearest the start
        c0, c1 = p["tag_clump"]
        ts, com, vcom, r90 = [], [], [], []
        for fn in sorted(glob.glob(os.path.join(d, "*.part.*.bin"))):
            t, _, x, u, m, tag = nw.read_snapshot(fn)
            k = (tag >= c0) & (tag < c1)
            mc = m[k]
            cm = (mc[:, None] * x[k]).sum(0) / mc.sum()
            ts.append(t)
            com.append(cm - ref)
            vcom.append((mc[:, None] * u[k]).sum(0) / mc.sum())
            r90.append(np.percentile(np.sqrt(((x[k] - cm) ** 2).sum(1)), 90))
        ts, com, vcom, r90 = map(np.array, (ts, com, vcom, r90))
        disp = np.sqrt((com ** 2).sum(1)) / dx
        h = nw.read_newton_hst(glob.glob(os.path.join(d, "*.newton.hst"))[0])
        P = np.sqrt(h["P_x"] ** 2 + h["P_y"] ** 2 + h["P_z"] ** 2)
        k = (disp > 0) & (disp < 0.1) & (ts > 0)
        rate = None
        if k.sum() >= 3:
            rate = float(np.polyfit(ts[k], np.log(disp[k]), 1)[0])
        summary[lab] = dict(run=d, dx=dx, nx=nx, ref_point=ref.tolist(), disp0_cells=float(disp[0]),
                            disp_max_cells=float(disp.max()), disp_end_cells=float(disp[-1]),
                            com_end_cells=(com[-1] / dx).tolist(), growth_rate=rate,
                            efold=None if not rate else float(1.0 / rate),
                            vcom_max=float(np.sqrt((vcom ** 2).sum(1)).max()),
                            r90_max_cells=float(r90.max() / dx), P_max=float(P.max()))
        c = cols[i % len(cols)]
        axs[0].plot(ts, disp + 1e-17, "o-", ms=2, color=c, label=lab)
        axs[1].plot(h["time"], P + 1e-20, color=c)
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"clump displacement / $\Delta x$")
    axs[0].legend(fontsize=8)
    axs[1].set_yscale("log")
    axs[1].set_ylabel(r"$|\sum m\mathbf{v}|$ [$Mc$]")
    axs[1].set_xlabel(r"$t$ [$GM/c^3$]", labelpad=-2)
    fs.save(fig, os.path.join(a.out, "nm_clumpstab"))
    with open(os.path.join(a.out, "nm_clumpstab.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
