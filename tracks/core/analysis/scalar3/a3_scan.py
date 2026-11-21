#!/usr/bin/env python3
"""Test A, part D again (tracks/core/JOURNAL-scalar3.md, entry 12): the resolution at
which the first-order constraint part of the late entry falls below the second-order
part, from the rows of an a1_twin.py summary (whose own derived keys
cells_for_*_second were computed wrongly before the fix of scan_crossings).

    python3 a3_scan.py --summary FILE [--out DIR]

Writes OUT/summary.json (crossings, slopes, the largest ratios per resolution) and
OUT/fig_scan.png (largest ratio in time against cells per shortest wavelength; the
ratio in time for every resolution)."""
import argparse
import json
import os

import s3
from s3 import common, np
from a1_twin import scan_crossings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    src = json.load(open(a.summary))
    scan = src["scan"]
    for r in scan:      # the keys exist in the summary; recomputed here from the rows
        for k in ("H", "M"):
            r[k + "_first_over_second_max"] = max(x[k + "_first_over_second"]
                                                  for x in r["rows"])
            r[k + "_first_code_over_second_max"] = max(
                x[k + "_first_code_over_second"] for x in r["rows"])
    summ = dict(source=os.path.abspath(a.summary), **scan_crossings(scan))
    summ["per_resolution"] = [dict(
        N=r["N"], cells=r["cells_per_shortest_wavelength"], kmax_dx=r["kmax_dx"],
        H_max=r["H_first_over_second_max"], M_max=r["M_first_over_second_max"],
        H_code_max=r["H_first_code_over_second_max"],
        M_code_max=r["M_first_code_over_second_max"],
        rnr_dev_end=r["rows"][-1]["rnr_dev_all"]) for r in scan]
    summ["symbols_sixth_order"] = src.get("symbols_sixth_order")
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.16, top=0.95, wspace=0.3)
    cw = np.array([r["cells_per_shortest_wavelength"] for r in scan])
    ax[0].loglog(cw, [r["H_first_over_second_max"] for r in scan], "o-",
                 color=fs.PAL["blue"], label=r"$\mathcal{H}$")
    ax[0].loglog(cw, [r["M_first_over_second_max"] for r in scan], "s--",
                 color=fs.PAL["red"], mfc="none", label=r"$|\mathcal{M}|$")
    ax[0].loglog(cw, [r["H_first_code_over_second_max"] for r in scan], "+",
                 color=fs.PAL["blue"], label=r"$\mathcal{H}$, with the time integration")
    ax[0].loglog(cw, [r["rows"][-1]["rnr_dev_all"] for r in scan], "^-",
                 color=fs.PAL["green"],
                 label=r"$|R^{\rm NR}_n/(WR\alpha_n)-1|$, largest, last dump")
    for lev in (1.0, 0.1):
        ax[0].axhline(lev, **fs.MASK_LINE)
    xx = np.array([4.0, 24.0])
    ax[0].loglog(xx, scan[0]["H_first_over_second_max"]*(xx/4.0)**-6, ":",
                 color="0.5", label=r"$\propto$ cells$^{-6}$")
    ax[0].set_xlabel("cells per shortest wavelength of the sources")
    ax[0].set_ylabel("first-order part / second-order part")
    ax[0].legend(fontsize=6, loc="lower left")
    cm = plt.get_cmap("viridis")
    for i, r in enumerate(scan):
        t = [x["time"] for x in r["rows"]]
        ax[1].semilogy(t, [x["H_first_over_second"] for x in r["rows"]], "-",
                       color=cm(i/max(len(scan) - 1, 1)),
                       label=f"{r['cells_per_shortest_wavelength']:.0f} cells (N = {r['N']})")
    ax[1].axhline(1.0, **fs.MASK_LINE)
    ax[1].set_xlabel(r"$t$ (e-folds within 6 percent)")
    ax[1].set_ylabel(r"$\mathcal{H}$: first-order / second-order part")
    ax[1].legend(fontsize=6, loc="upper left", ncol=2)
    fig.savefig(os.path.join(out, "fig_scan.png"), dpi=200)
    print("A scan done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
