#!/usr/bin/env python3
"""Figure of Test 2 (processor smoke, run C-20261115-172003-6422b6a): the expected number of
collisions per step (history column sum_P) and the collisions of the first four cycles of
cc1_kn10 and cc1_kn1, against the prediction of run C-20261115-170404-af74c6d with its
spread over pairings.

    python3 fig_smoke.py [--smoke RUN_ID] [--out DIR]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", default="C-20261115-172003-6422b6a")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    pred = json.load(open(os.path.join(C.SCRATCH, "C-20261115-170404-af74c6d", "predictions.json")))
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    out = {}
    for ax, name, col in zip(axs, ("cc1_kn10", "cc1_kn1"), (fs.PAL["blue"], fs.PAL["red"])):
        c = C.read_hst(os.path.join(C.SCRATCH, a.smoke, name, "cc.coll.hst"))
        p = pred["cc1"]["runs"][name]
        mu, sd = p["sumP_step1_expected"], p["sumP_step1_pairing_sd"]
        cyc = c["ncycle"]
        fs.band(ax, [0.5, 4.5], [mu - 3 * sd] * 2, [mu + 3 * sd] * 2, fs.PAL["blue"])
        ax.axhline(mu, **fs.GUIDE, label="predicted (all pairs), 3 sd of pairings")
        ax.plot(cyc, c["sum_P"], "o-", color=col, label="sum$_P$ of the code")
        ax.errorbar(cyc, c["n_coll"], yerr=np.sqrt(c["sum_P"]), fmt="s", color="k", ms=4,
                    mfc="none", label=r"collisions ($\pm\sqrt{{\rm sum}_P}$)")
        ax.set_xlabel("cycle")
        ax.set_ylabel(f"per step, {name}")
        ax.set_xlim(0.5, 4.5)
        ax.legend(fontsize=7, loc="lower right")
        out[name] = dict(sumP=c["sum_P"].tolist(), n_coll=c["n_coll"].tolist(), pred=mu, sd=sd,
                         z_counts=float((c["n_coll"].sum() - c["sum_P"].sum())
                                        / np.sqrt(c["sum_P"].sum())))
    os.makedirs(a.out, exist_ok=True)
    fig.savefig(os.path.join(a.out, "fig_smoke_sumP.png"), dpi=200)
    with open(os.path.join(a.out, "fig_smoke.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
