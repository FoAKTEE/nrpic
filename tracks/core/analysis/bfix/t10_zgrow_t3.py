#!/usr/bin/env python3
"""T10: history of the mesh-scale z noise in the thin boxes of T3 (processors) and of
their repetition on the card in T4, from a = 1 through the first shell crossing
(prediction P12 of tracks/core/JOURNAL-bfix.md). Reads existing dumps only.

    python3 t10_zgrow_t3.py --t3 DIR --t4 DIR [--out DIR]
"""
import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs  # noqa: E402
from t8_analysis import stage_zgrow  # noqa: E402

CASES = ("cube", "thin8", "thin4", "plane4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t3", required=True)
    ap.add_argument("--t4", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    res = {"meta": {"t3": a.t3, "t4": a.t4, "commit": bc.git_rev()}}
    for src, d in (("cpu", a.t3), ("card", a.t4)):
        for c in CASES:
            rd = os.path.join(d, "run", c)
            if os.path.isdir(rd):
                stage_zgrow(res, rd, key=f"{src}_{c}")
    summ = {}
    for key, r in res.items():
        if key == "meta":
            continue
        t = np.array(r["t"])
        i1 = int(np.argmin(np.abs(t - 1.0)))
        summ[key] = {g: {"t1": r["absdev"][g][i1], "end": r["absdev"][g][-1],
                         "max": max(r["absdev"][g]),
                         "rel_xyvar_max": max(r["rel_xyvar"][g]),
                         "mean_growth_last8": float(np.exp(np.mean(np.log(np.maximum(
                             r["growth_per_dump_last8"][g], 1e-300)))))}
                     for g in ("At", "Axz", "gt", "gxz", "Gam", "Khat", "Theta")}
        print(key, json.dumps({g: {k: f"{v:.2e}" for k, v in s.items()}
                               for g, s in summ[key].items()}))
    res["summary"] = summ
    bc.save_json(res, os.path.join(out, "results_t10.json"))

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.92, wspace=0.08)
    cols = {"cube": "k", "thin8": fs.PAL["blue"], "thin4": fs.PAL["red"],
            "plane4": fs.PAL["green"]}
    for ax, g, title in ((axs[0], "At", "At (largest component)"),
                         (axs[1], "gt", "gt (largest component)")):
        for key, r in res.items():
            if key in ("meta", "summary"):
                continue
            src, c = key.split("_", 1)
            ax.semilogy(r["t"], np.maximum(r["absdev"][g], 1e-22),
                        "-" if src == "cpu" else "--", color=cols[c], marker=".",
                        label=f"{c}, {'processor' if src == 'cpu' else 'card'}")
        ax.set_title(f"largest |f(z) - f(z_0)| of {title}", fontsize=8)
        ax.set_xlabel("conformal time")
    axs[0].set_ylim(1e-22, 1e-8)
    axs[0].legend(fontsize=6, ncol=2, loc="upper left")
    print("figures:", fs.save(fig, os.path.join(out, "t10_zgrow_t3")))


if __name__ == "__main__":
    main()
