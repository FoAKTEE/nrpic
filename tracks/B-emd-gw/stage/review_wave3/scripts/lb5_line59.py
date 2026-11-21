"""Lead check of batch 5 (B-emd-gw): ledger line 59 and the a = 10 values of line 56, read with
my own reader from the cstat histories of the wave-1 pancake runs (L1, 64 cells, one and two
particles per cell and direction). Independent of the verifier's pancake.py and of the track's
analyze_pancake.py: only the column names of the file header and a(t) = (1 + t/2)^2 are used.

    python3 lb5_line59.py OUTDIR

Writes OUTDIR/lb5_line59.json and OUTDIR/lb5_line59.png.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = {"one per cell": f"{S}/B-emd-gw-20261115-115217-69ab1db/L1_n64/east.cstat.hst",
        "two per cell and direction": f"{S}/B-emd-gw-20261115-115902-a3207d7/L1_n64_p2/east.cstat.hst"}
DUMPS = (22.0, 25.0, 30.0, 35.0, 41.9)


def cols(path):
    with open(path) as f:
        head = [ln for ln in f if ln.startswith("# [")][0]
    names = [w.split("=", 1)[1] for w in head[1:].split()]
    data = np.loadtxt(path)
    return {n: data[:, i] for i, n in enumerate(names)}


def main(out):
    os.makedirs(out, exist_ok=True)
    res = {}
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    for (label, path), c in zip(RUNS.items(), ("C0", "C3")):
        d = cols(path)
        a = (1.0 + 0.5*d["time"])**2
        h = d["Hr_mean"]
        sel = (a >= 22.0) & (a <= 42.0)
        near = {f"{x:g}": float(h[np.argmin(abs(a - x))]) for x in DUMPS}
        res[label] = {
            "max_all_records_22_42": float(h[sel].max()),
            "a_of_max": float(a[sel][np.argmax(h[sel])]),
            "max_at_records_nearest_dumps": max(near.values()),
            "at_records_nearest_dumps": near,
            "nearest_a10": float(a[np.argmin(abs(a - 10.0))]),
            "Hr_mean_nearest_a10": float(h[np.argmin(abs(a - 10.0))]),
            "Hr_mean_interp_a10": float(np.interp(10.0, a, h)),
            "n_records_22_42": int(sel.sum()),
        }
        ax.semilogy(a, h, color=c, lw=1.0, label=label)
        ax.semilogy(list(map(float, near)), list(near.values()), "o", color=c, ms=4)
    ax.axvspan(22.0, 42.0, color="0.85", zorder=0)
    ax.set_xlim(1, 45)
    ax.set_xlabel("scale factor $a$")
    ax.set_ylabel(r"mean $|\mathcal{H}|$ relative")
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "lb5_line59.png"), dpi=150)
    with open(os.path.join(out, "lb5_line59.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
