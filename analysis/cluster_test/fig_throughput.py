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
        if d.startswith(("mesh_", "ana_", "plunge_", "thr_", "tim_")) and C.exists(d):
            info = C.log_info(d)
            if "pups" not in info:
                continue
            h = C.history(d)
            info["np0"] = int(h[0, H["np"]])
            info["np_end"] = int(h[-1, H["np"]])
            info["ncycle"] = int(h[-1, H["ncycle"]])
            info["ms_per_cycle"] = 1e3 * info["cpu"] / max(info["ncycle"], 1)
            res[d] = info
    fig, axes = plt.subplots(1, 3, figsize=(8.0, 3.2),
                             gridspec_kw=dict(width_ratios=[1, 1, 0.8]))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.80, wspace=0.42)
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
    for ax in axes[:2]:
        ax.set_xlim(50, 3e4)
        fs.no_minor_labels(ax, "x")
    axes[0].set_xlabel("particles $N$")
    axes[0].set_ylabel("particle updates per second")
    axes[1].set_xlabel("particles $N$")
    axes[1].set_ylabel("wall time per cycle [ms]")
    # cost breakdown of one mesh-run cycle (a = 0.9, N = 1e4, 1000 cycles, outputs off)
    bars = [("thr_a0.9_prod", "mesh,\nnfilter = 2"), ("thr_a0.9_nf0", "mesh,\nnfilter = 0"),
            ("ana_a0.9_mid", "analytic")]
    vals = [(lab, res[k]["ms_per_cycle"]) for k, lab in bars if k in res]
    if vals:
        y = np.arange(len(vals))
        axes[2].barh(y, [v for _, v in vals], height=0.6,
                     color=[fs.PAL["blue"] if lab.startswith("analytic") else fs.PAL["red"]
                            for lab, _ in vals])
        axes[2].set_yticks(y)
        axes[2].set_yticklabels([lab for lab, _ in vals], fontsize=8)
        axes[2].invert_yaxis()
        axes[2].set_xscale("log")
        axes[2].set_xlabel("ms per cycle")
        axes[2].minorticks_off()
        axes[2].tick_params(axis="y", which="both", right=False)
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
