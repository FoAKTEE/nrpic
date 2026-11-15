"""P2e: crossing-time offsets of the loss-cone probes for two time steps (runs B, B2).

usage: python3 compare_dt.py --a <analysis dir dt=0.05> --b <analysis dir dt=0.025> --out DIR
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "python"))
from nrpic import figstyle  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    A = np.load(Path(args.a) / "crossing.npz"); B = np.load(Path(args.b) / "crossing.npz")
    assert np.array_equal(A["gid"], B["gid"])
    oa = A["tmeas"] - A["tpred"]; ob = B["tmeas"] - B["tpred"]
    q = np.abs(A["q"])
    ratio = oa / ob
    bins = [1e-4, 1e-3, 1e-2, 1e-1]
    res = {"n": int(q.size), "median_offset_dt0.05": float(np.median(oa)),
           "median_offset_dt0.025": float(np.median(ob)),
           "min_offset_dt0.05": float(oa.min()), "min_offset_dt0.025": float(ob.min()),
           "median_ratio": float(np.median(ratio))}
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (q >= lo) & (q < hi)
        res[f"|q| {lo:g}-{hi:g}"] = {"n": int(m.sum()), "median_ratio": float(np.median(ratio[m])),
                                     "median_offset_dt0.05": float(np.median(oa[m])),
                                     "median_offset_dt0.025": float(np.median(ob[m]))}
    (out / "compare_dt.json").write_text(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    a = axs[0]
    a.loglog(q, np.abs(oa), ".", ms=3, color=P["red"], label=r"$\Delta t = 0.05\,Gm$")
    a.loglog(q, np.abs(ob), ".", ms=3, color=P["blue"], label=r"$\Delta t = 0.025\,Gm$")
    a.set_xlabel(r"$|q|$"); a.set_ylabel(r"$|t_{\rm cross} - t_{\rm pred}|$ [$Gm$]")
    a.legend(loc="upper right", fontsize=7, markerscale=3)
    b = axs[1]
    b.semilogx(q, ratio, ".", ms=3, color=P["red"])
    b.axhline(4.0, **figstyle.GUIDE, label="second order (ratio 4)")
    b.set_ylim(0, 8); b.set_xlabel(r"$|q|$"); b.set_ylabel("offset(0.05) / offset(0.025)")
    b.legend(loc="upper right", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"crossing_dt.{ext}")
    plt.close(fig)
    shutil.copy(out / "crossing_dt.png", HERE / "figs" / "crossing_dt.png")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
