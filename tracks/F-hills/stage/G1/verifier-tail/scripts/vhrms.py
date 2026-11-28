"""Accepted horizon searches by their residual: for A (F-20261121-203144-b2cf16b) and A2
(F-20261124-210400-902c650), finders 0, 1, 2, the searches the summary signature accepts, split by
the summary's hrms (column 9, area mean of the squared expansion) into classes, before the capture
(t < 137.5 M) and after; the lower-mass episodes of the member finders with their hrms.

Run: python vhrms.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "verifier", "scripts")))
import vread  # noqa: E402
sys.path.insert(0, HERE)
import figstyle  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
RUNS = {"A": os.path.join(SCR, "F-20261121-203144-b2cf16b"), "A2": os.path.join(SCR, "F-20261124-210400-902c650")}
T_CAP = 137.5
EDGES = [0, 1e-6, 1e-4, 1e-2, np.inf]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, series = {}, {}
    for tag, rd in RUNS.items():
        for n in (0, 1, 2):
            d = vread.read_horizon_summary(os.path.join(rd, f"hills.horizon_summary_{n}.txt"))
            if tag == "A2":   # A2 starts where A's kept record ends (A's rows after 61.8 M are cut attempts)
                pass
            acc = ~d["failed"]
            t, m, h = d["t"][acc], d["mass"][acc], d["hrms"][acc]
            series[(tag, n)] = (t, m, h)
            pre = t < T_CAP
            blk = {"n_accepted": int(acc.sum()), "n_before_capture": int(pre.sum())}
            cls = {}
            for lo, hi in zip(EDGES[:-1], EDGES[1:]):
                s = pre & (h >= lo) & (h < hi)
                cls[f"[{lo:g},{hi:g})"] = int(s.sum())
            blk["hrms_classes_before_capture"] = cls
            hi_ = pre & (h >= 1e-2)
            if hi_.any():
                # mass of the high-hrms rows against the median of the low-hrms rows within 1 M
                dm = []
                for tt, mm in zip(t[hi_], m[hi_]):
                    near = pre & (np.abs(t - tt) < 1.0) & (h < 1e-3)
                    if near.any():
                        dm.append(mm - np.median(m[near]))
                # episodes: runs of high-hrms rows separated by less than 0.2 M
                th = t[hi_]
                starts = [th[0]]
                ends = []
                for x, y in zip(th[:-1], th[1:]):
                    if y - x > 0.2:
                        ends.append(x)
                        starts.append(y)
                ends.append(th[-1])
                blk["high_hrms_before_capture"] = {
                    "n": int(hi_.sum()), "fraction": float(hi_.sum() / pre.sum()),
                    "hrms_min_max": [float(h[hi_].min()), float(h[hi_].max())],
                    "mass_minus_neighbours_median": float(np.median(dm)) if dm else None,
                    "mass_minus_neighbours_min_max": [float(min(dm)), float(max(dm))] if dm else None,
                    "episodes": [[float(s_), float(e_)] for s_, e_ in zip(starts, ends)][:30],
                    "n_episodes": len(starts)}
            low = pre & (h < 1e-3)
            blk["low_hrms_mass_median"] = float(np.median(m[low])) if low.any() else None
            res[f"{tag}_{n}"] = blk

    figstyle.use_style()
    import matplotlib.pyplot as plt
    P = figstyle.PAL
    fig, ax = plt.subplots(1, 3, figsize=(8, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.93, wspace=0.38)
    for n, a_ in zip((0, 1, 2), ax):
        for tag, col in (("A", P["blue"]), ("A2", P["red"])):
            t, m, h = series[(tag, n)]
            s = t < (61.8125 if tag == "A" else T_CAP)
            a_.semilogy(t[s], h[s], ".", ms=0.8, color=col, label=tag)
        a_.set_xlabel("t [M]"); a_.set_ylabel(f"hrms, finder {n}")
        a_.set_title(f"finder {n}, accepted, t < 137.5 M", fontsize=8)
        a_.legend(fontsize=7, loc="lower right")
    figstyle.save(fig, os.path.join(a.out, "fig_t_hrms"))
    with open(os.path.join(a.out, "vhrms.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res)[:3500])


if __name__ == "__main__":
    main()
