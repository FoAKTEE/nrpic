"""K2 control: the slice of the sampling. Compares the inner counts of two AthenaK runs drawn
from the same DF, one sampled on the KS slice (exact) and one on the BL slice without the
Jacobian (wave-1 scheme), from the *_series.npz files of analyze_kerr.py.

For each r range: counts relative to their own t = 0 value, and the running mean over a
window of W M with its Poisson sigma (sqrt(N)/N/sqrt(n_window) is NOT used: snapshots are
correlated; the conservative sigma of one snapshot is shown).

usage: python3 compare_slice.py --ks <dir>/ks_series.npz --bl <dir>/bl_series.npz --out DIR [--w 100]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "python"))
from nrpic import figstyle  # noqa: E402

RANGES = ["0-4", "4-6", "6-10", "10-16", "16-40"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ks", required=True)
    ap.add_argument("--bl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--w", type=float, default=100.0)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    res = {}
    S = {k: np.load(p) for k, p in (("ks", args.ks), ("bl", args.bl))}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, axs = plt.subplots(len(RANGES[:4]), 1, figsize=(4.0, 6.4), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.97, bottom=0.08, hspace=0.0)
    for i, rn in enumerate(RANGES[:4]):
        ax = axs[i]
        for key, col in (("ks", P["red"]), ("bl", P["blue"])):
            d = S[key]
            t, c = d["t"], d["rc"][:, i]
            dt = np.median(np.diff(t))
            nw = max(1, int(round(args.w / dt)))
            run = np.convolve(c, np.ones(nw) / nw, mode="valid")
            tr = t[nw - 1:] - 0.5 * (nw - 1) * dt
            rel = c / c[0]
            sig = 1 / np.sqrt(c[0])
            zrun = (run - c[0]) / np.sqrt(c[0])
            zall = (c - c[0]) / np.sqrt(c[0])
            res[f"{key}:{rn}"] = {"N_t0": int(c[0]), "sigma_rel": float(sig),
                                  "max_|z|_snapshot": float(np.max(np.abs(zall))),
                                  "max_|z|_running_mean": float(np.max(np.abs(zrun))),
                                  "running_mean_rel_minmax": [float(run.min() / c[0]),
                                                              float(run.max() / c[0])],
                                  "late_mean_rel": float(c[len(c) // 2:].mean() / c[0])}
            ax.plot(t, rel, color=col, lw=0.4, alpha=0.5)
            ax.plot(tr, run / c[0], color=col, lw=1.4,
                    label=f"{key.upper()} slice ({int(c[0])})" if i == 0 else None)
            ax.axhspan(1 - sig, 1 + sig, color=col, alpha=0.06)
        ax.axhline(1, **figstyle.THIN)
        ax.set_ylabel(f"{rn} Gm", fontsize=9)
        ax.set_ylim(0.9, 1.1)
    axs[0].legend(loc="upper right", fontsize=7, title=f"counts / t=0 counts, running mean "
                  f"{args.w:.0f} M", title_fontsize=7)
    axs[-1].set_xlabel(r"$t/Gm$", labelpad=-2)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"slice_control.{ext}")
    plt.close(fig)
    shutil.copy(out / "slice_control.png", HERE / "figs" / "slice_control.png")
    (out / "slice_control.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
