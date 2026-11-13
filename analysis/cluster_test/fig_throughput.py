#!/usr/bin/env python3
"""(f) GPU throughput: particle updates per second (AthenaK's
"particle-updates/cpu_second" = sum over cycles of the particle count / wall time of the
cycle loop, outputs included) for every run, and the wall time per cycle.

Figure: figs/throughput.{pdf,png}
Numbers: results/throughput.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

import ct_common as C
from nrpic import figstyle as fs

H = C.dc.H


def main():
    fs.use_style()
    res = {}
    for d in sorted(os.listdir(C.RUNS)):
        if d.startswith(("mesh_", "ana_", "plunge_")) and C.exists(d):
            info = C.log_info(d)
            if "pups" not in info:
                continue
            h = C.history(d)
            info["np0"] = int(h[0, H["np"]])
            info["np_end"] = int(h[-1, H["np"]])
            info["ncycle"] = int(h[-1, H["ncycle"]])
            info["ms_per_cycle"] = 1e3 * info["cpu"] / max(info["ncycle"], 1)
            res[d] = info
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.16, top=0.84, wspace=0.28)
    groups = [("mesh", "_mid", "mesh, midpoint", fs.PAL["red"], "o"),
              ("mesh", "_boris", "mesh, Boris", fs.PAL["green"], "s"),
              ("plunge", "_mid", "mesh, midpoint, plunging", fs.PAL["red"], "x"),
              ("ana", "_mid", "analytic, midpoint", fs.PAL["blue"], "o"),
              ("ana", "_boris", "analytic, Boris", fs.PAL["yellow"], "s"),
              ("ana", "_bchol", "analytic, Boris Cholesky", fs.PAL["orange"], "^")]
    for pre, suf, lab, col, mk in groups:
        for a, fill in ((0.0, "none"), (0.9, col)):
            pts = [(v["np0"], v["pups"], v["ms_per_cycle"]) for k, v in res.items()
                   if k.startswith(f"{pre}_a{a}") and k.endswith(suf)]
            if not pts:
                continue
            pts = np.array(sorted(pts))
            kw = dict(color=col, marker=mk, mfc=fill, ms=6, ls="-" if len(pts) > 1 else "")
            axes[0].loglog(pts[:, 0], pts[:, 1], label=lab if a == 0.9 else None, **kw)
            axes[1].loglog(pts[:, 0], pts[:, 2], **kw)
    axes[0].set_xlabel("particles $N$")
    axes[0].set_ylabel("particle updates per second")
    axes[1].set_xlabel("particles $N$")
    axes[1].set_ylabel("wall time per cycle [ms]")
    axes[0].plot([], [], "o", color="k", mfc="none", label=r"$a = 0$ (open)")
    h0, l0 = axes[0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=4, fontsize=8, frameon=False,
               bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "throughput"))
    plt.close(fig)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    with open(os.path.join(C.HERE, "results", "throughput.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(f"{k:26s} N={v['np0']:6d}->{v['np_end']:6d} cycles={v['ncycle']} "
              f"wall={v['cpu']:.1f}s  {v['pups']:.3e} upd/s  {v['ms_per_cycle']:.2f} ms/cycle "
              f"gpu_peak={v.get('gpu_peak')} job={v['job']}")


if __name__ == "__main__":
    main()
