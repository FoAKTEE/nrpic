"""V2: null test N of g2long entry 1 from the finder summaries, own reader.

python3 v2_null.py --scratch <scratch/D-bh-dress> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vio  # noqa: E402
import figstyle as fs  # noqa: E402

RUNS = {  # label: (run id, base)
    "V-1L": ("D-20261121-203124-a34cf1f", "v1l"),
    "ES-1L": ("D-20261121-203131-8ee2a49", "es1l"),
    "V-1L16": ("D-20261121-203151-37e7b2d", "v1l16"),
    "ES-1L16": ("D-20261121-203151-59c54fb", "es1l16"),
    "V-1L4": ("D-20261123-022715-ab5d983", "v1l4"),
    "ES-1L4": ("D-20261123-022726-1b133af", "es1l4"),
    "ES-FL": ("D-20261121-203150-15f2bad", "esfl"),
    "FK": ("D-20261123-022725-a553496", "esflk"),
    "FF4": ("D-20261123-022727-1c17e73", "esfl4"),
    "FN4": ("D-20261124-134157-b17938b", "esflk4n"),
    "FNQ": ("D-20261124-172725-2f426b6", "esflkq"),
    "FL16": ("D-20261124-172745-72472ed", "esfl16"),
    "ES-F": ("D-20261121-144631-aa7ce9b", "esf"),
}
PAIRS = [("M/8", "ES-1L", "V-1L", 500.0), ("M/16", "ES-1L16", "V-1L16", 300.0),
         ("M/4", "ES-1L4", "V-1L4", 300.0)]


def summary(scr, lab):
    rid, base = RUNS[lab]
    p = os.path.join(scr, rid, f"{base}.horizon_summary_0.txt")
    a, bad = vio.read_summary(p)
    return a, bad, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"failure_signature": {}, "null": {}}
    for lab in RUNS:
        try:
            s, bad, p = summary(a.scratch, lab)
        except FileNotFoundError:
            res["failure_signature"][lab] = "missing"
            continue
        t = s[:, 1]
        res["failure_signature"][lab] = dict(
            n=int(len(t)), t_end=float(t[-1]), dt_median=float(np.median(np.diff(t))),
            failed_total=int(bad.sum()), failed_after_20=int((bad & (t > 20)).sum()),
            failed_times_le_20=[float(x) for x in t[bad & (t <= 20)]][:20],
            failed_times_gt_20=[float(x) for x in t[bad & (t > 20)]][:20],
            nonfinite=int((~np.isfinite(s[:, 2])).sum()))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 5.2))
    axs = [fig.add_axes([0.1, 0.56, 0.86, 0.4]), fig.add_axes([0.1, 0.08, 0.86, 0.38])]
    cols = {"M/8": fs.PAL["red"], "M/16": fs.PAL["blue"], "M/4": fs.PAL["green"]}
    for mesh, es, v, T in PAIRS:
        se, be, _ = summary(a.scratch, es)
        sv, bv, _ = summary(a.scratch, v)
        common, ie, iv = np.intersect1d(se[:, 1], sv[:, 1], return_indices=True)
        Me, Mv = se[ie, 2], sv[iv, 2]
        i100 = np.where(common == 100.0)[0][0]
        De, Dv = Me - Me[i100], Mv - Mv[i100]
        w = (common >= 100.0) & (common <= T)
        diff = De - Dv
        FV = float(np.max(np.abs(Dv[w])))
        bound = max(2 * FV, 1e-4)
        mx = float(np.max(np.abs(diff[w])))
        imax = int(np.argmax(np.abs(diff[w])))
        # refutation clause: |diff| > 3 max(F_V, 5e-5) over a window longer than 50 M
        thr = 3 * max(FV, 5e-5)
        over = np.abs(diff[w]) > thr
        tw = common[w]
        longest = 0.0
        start = None
        for k in range(len(tw)):
            if over[k] and start is None:
                start = tw[k]
            if (not over[k] or k == len(tw) - 1) and start is not None:
                end = tw[k] if over[k] else tw[k - 1]
                longest = max(longest, end - start)
                start = None
        # same with failed searches dropped
        ok = ~(be[ie] | bv[iv])
        mx_ok = float(np.max(np.abs(diff[w & ok])))
        res["null"][mesh] = dict(pair=[es, v], window=[100.0, T], n_common=int(w.sum()),
                                 F_V=FV, bound=bound, max_diff=mx,
                                 t_of_max=float(tw[imax]), holds=bool(mx <= bound),
                                 refute_threshold=thr, longest_over_threshold=longest,
                                 max_diff_failed_dropped=mx_ok,
                                 M_ES_100=float(Me[i100]), M_V_100=float(Mv[i100]),
                                 M_ES_end=float(Me[w][-1]), M_V_end=float(Mv[w][-1]))
        axs[0].plot(common, diff, color=cols[mesh], label=f"{mesh}: $D_{{ES}}-D_V$")
        axs[0].axhline(bound, color=cols[mesh], ls="--", lw=1)
        axs[0].axhline(-bound, color=cols[mesh], ls="--", lw=1)
        axs[1].plot(common, Dv, color=cols[mesh], ls="-", label=f"{mesh} vacuum $D_V$")
        axs[1].plot(common, De, color=cols[mesh], ls=":", label=f"{mesh} bubble $D_{{ES}}$")
    axs[0].set_xlim(100, 500)
    axs[0].set_ylim(-1.2e-3, 1.2e-3)
    axs[0].set_ylabel(r"$D_{\rm ES}-D_{\rm V}$ [M]")
    axs[0].legend(loc="lower left", ncol=3)
    axs[0].text(0.99, 0.92, "dashed: bound max(2 F_V, 1e-4); M/4 leaves the panel",
                transform=axs[0].transAxes, ha="right", fontsize=8)
    axs[1].set_xlim(100, 500)
    axs[1].set_ylim(-1e-3, 1e-3)
    axs[1].set_xlabel("t [M]")
    axs[1].set_ylabel(r"$M(t)-M(100\,M)$")
    axs[1].legend(loc="lower left", ncol=3, fontsize=8)
    fs.save(fig, os.path.join(a.out, "v2_null"))
    json.dump(res, open(os.path.join(a.out, "v2_null.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
