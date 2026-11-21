#!/usr/bin/env python3
"""C5b: where in the core are the large shell errors? |R/R_exact - 1| of the tracked core
particles at tau = 3.3716 and 9.0 against the distance of their label from the core edge,
R1 - R_i (follow-up of run A-20261121-125646-166ae06: the largest errors sit at the edge).

Reports the largest |eps| over core particles with R1 - R_i > d for d = 0, 0.02, 0.05, 0.1,
0.2, 0.4 M, and the 99th percentile. Writes c5b_edge.json and fig_c5b_edge.{png,pdf}.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import partdata as PD          # noqa: E402
from c5_shells import interp_at_tau   # noqa: E402
from ltb import TableLTB       # noqa: E402

RUNS = ["bh_smr", "bh_n256", "bh_n192", "bh_n128"]
TAUS = (3.3716, 9.0)
DS = (0.0, 0.02, 0.05, 0.1, 0.2, 0.4)


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    T = TableLTB(P.TABLE)
    b1, _ = np.sort(T.breaks)
    R1 = float(T.slice(np.array([b1]), side="in")["R"][0])
    res, plots = dict(R1=R1), {}
    for run in RUNS:
        pd = PD.load(run, T)
        eps = pd["R"] / PD.r_exact_at_own_tau(pd) - 1.0
        core = np.nonzero(pd["rbar_i"] < b1)[0]
        dist = R1 - pd["sh"].R_i[core]
        res[run] = dict(n_core=int(len(core)), min_distance=float(dist.min()))
        for tq in TAUS:
            e = np.array([interp_at_tau(pd["tau"][:, j], eps[:, j], tq) for j in core])
            rows = {}
            for dmin in DS:
                s = np.isfinite(e) & (dist > dmin)
                rows[f"d>{dmin:g}"] = dict(n=int(s.sum()), max_abs=float(np.max(np.abs(e[s]))) if s.any() else None,
                                          p99_abs=float(np.percentile(np.abs(e[s]), 99)) if s.any() else None)
            res[run][f"tau{tq:g}"] = rows
            plots[(run, tq)] = (dist, e)
    with open(os.path.join(out, "c5b_edge.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    fs.use_style()
    import matplotlib.pyplot as plt
    lab = {"bh_smr": "BH-1R (M/16)", "bh_n256": "BH-1 M/8", "bh_n192": "BH-1 M/6", "bh_n128": "BH-1 M/4"}
    cols = {"bh_smr": fs.PAL["red"], "bh_n256": fs.PAL["blue"], "bh_n192": fs.PAL["green"], "bh_n128": fs.PAL["orange"]}
    claim = {3.3716: {"bh_smr": 1.5e-3, "bh_n256": 2e-3}, 9.0: {"bh_n256": 2e-2}}
    fig = plt.figure(figsize=(8.0, 3.7))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.90, wspace=0.28)
    for j, tq in enumerate(TAUS):
        ax = fig.add_subplot(1, 2, 1 + j)
        for run in RUNS:
            dist, e = plots[(run, tq)]
            ax.loglog(np.maximum(dist, 1e-4), np.abs(e) + 1e-9, ".", ms=2.5, color=cols[run], label=lab[run])
        for run, v in claim[tq].items():
            ax.axhline(v, color=cols[run], lw=0.9, ls="--")
        ax.set_xlabel(r"distance from the core edge $R_1-R_i\,/M$")
        ax.set_ylabel(rf"$|R/R_{{\rm exact}}-1|$ at $\tau$ = {tq:g}")
        ax.set_ylim(1e-7, 2e-1)
        ax.set_title(r"dashed: claimed bounds of C5", fontsize=10)
        if j == 0:
            ax.legend(fontsize=7, frameon=False, markerscale=3, loc="lower left")
    fs.save(fig, os.path.join(out, "fig_c5b_edge"))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
