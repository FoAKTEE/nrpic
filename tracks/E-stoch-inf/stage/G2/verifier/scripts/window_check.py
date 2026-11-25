"""U-W recomputed from the window scan output (card job E-20261120-222424-0eb754b, 128^3,
nmax2 = 1024, last dump): odd-part shell power of each window against the baseline
(s = 5, sigma = 1) and against the own linear reference with the same alpha.

python3 window_check.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

SCAN = os.path.join(vlib.SCRATCH, "E-20261120-222424-0eb754b")
WINDOWS = {"b": (5.0, 1.0), "s25": (2.5, 1.0), "s10": (10.0, 1.0), "g05": (5.0, 0.5), "g2": (5.0, 2.0)}
L32 = vlib.L_BOX ** -1.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    deck = os.path.join(vlib.TRACK, "window", "inputs", "usr_256.athinput")
    dd = vlib.read_deck(deck)
    n = vlib.hemisphere(1024)
    n2 = (n ** 2).sum(1)
    last = max(int(f.split(".")[2]) for f in os.listdir(os.path.join(SCAN, "b_p")) if f.endswith(".dump"))
    times = {}
    C = {}
    for w in WINDOWS:
        for sgn in ("p", "m"):
            p = os.path.join(SCAN, f"{w}_{sgn}", f"usr.sf.{last:05d}.dump")
            r = vlib.rnr_from_dump(p, n)
            C[f"{w}_{sgn}"] = r["c"]
            times[f"{w}_{sgn}"] = r["time"]
    t = times["b_p"]
    res = {"last_dump": last, "t": t, "max_dt": max(abs(v - t) for v in times.values()),
           "deck_tlim": float(dd["time/tlim"]), "seed": dd["job/rng_seed"]}
    mf = os.path.join(vlib.TRACK, "usr", "inputs", "modes_usr_n4096.txt")
    q2all = vlib.read_mode_file(mf)[0]
    nsh = int(np.searchsorted(q2all, 1024, side="right"))
    ref = vlib.Reference(deck, mf, t, rtol=1e-12, nshell=nsh, t_eval=[t])
    R, _ = ref.modes(t)
    sh = np.searchsorted(ref.q2, n2)
    assert np.all(ref.q2[sh] == n2)
    alpha = vlib.alpha_modes(int(dd["job/rng_seed"]), n)
    res["cN_last"] = float(ref.background(t)["N"])
    P = {}
    qs = None
    out = {}
    for w, (s, sig) in WINDOWS.items():
        W = ref.window(t, np.sqrt(n2.astype(float)), s=s, sigma=sig)
        pred = L32 * W * R[sh] * alpha
        O = 0.5 * (C[f"{w}_p"] - C[f"{w}_m"])
        Pw = np.bincount(n2, weights=np.abs(O) ** 2, minlength=1025)
        Pr = np.bincount(n2, weights=np.abs(pred) ** 2, minlength=1025)
        qs = np.nonzero(Pr > 0)[0]
        P[w] = (Pw[qs], Pr[qs])
        out[w] = {"W_min": float(W.min()),
                  "max_D_k_le_16": float(np.abs(O / pred - 1)[n2 <= 256].max()),
                  "max_D_all": float(np.abs(O / pred - 1).max())}
    devb = P["b"][0] / P["b"][1] - 1
    for w in WINDOWS:
        if w == "b":
            continue
        devw = P[w][0] / P[w][1] - 1
        shift = P[w][0] / P["b"][0] - 1
        h = qs <= 256
        out[w] |= {"max_shift_k_le_16": float(np.abs(shift[h]).max()),
                   "max_shift_k_le_32": float(np.abs(shift).max()),
                   "shells_shift_gt_dev_b": int((np.abs(shift) > np.abs(devb)).sum()),
                   "shells_shift_gt_sum_bound": int((np.abs(shift) > np.abs(devb) + np.abs(devw)).sum()),
                   "n_shells": int(len(qs))}
    res["windows"] = out
    res["U-W"] = {"max_shift_k_le_16": max(out[w]["max_shift_k_le_16"] for w in out if w != "b"),
                  "max_shift_k_le_32": max(out[w]["max_shift_k_le_32"] for w in out if w != "b")}
    res["U-W"]["pass_thresholds"] = (res["U-W"]["max_shift_k_le_16"] <= 1e-3 and
                                     res["U-W"]["max_shift_k_le_32"] <= 2e-2)
    json.dump(res, open(os.path.join(a.out, "window_check.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    cols = figstyle.series_colors(5)
    for c, w in zip(cols, WINDOWS):
        devw = P[w][0] / P[w][1] - 1
        ax[0].semilogy(np.sqrt(qs), np.abs(devw) + 1e-18, ".", ms=2, color=c, label=w)
        if w != "b":
            ax[1].semilogy(np.sqrt(qs), np.abs(P[w][0] / P["b"][0] - 1) + 1e-18, ".", ms=2,
                           color=c, label=f"{w} vs b")
    ax[0].set_ylabel("|P_odd / P_ref - 1| per shell")
    ax[1].set_ylabel("|P_w / P_b - 1| per shell (odd parts)")
    for x in ax:
        x.set_xlabel("k / dk")
        x.axvline(16, color="0.5", ls=":", lw=0.8)
        x.legend(fontsize=6, markerscale=4)
    ax[1].axhline(1e-3, color="k", ls="--", lw=0.8)
    ax[1].axhline(2e-2, color="k", ls=":", lw=0.8)
    ax[0].set_title(f"NR vs own reference, last dump (cN = {res['cN_last']:.2f})", fontsize=8)
    ax[1].set_title("U-W: shift against the baseline window", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_window.png"), dpi=150)


if __name__ == "__main__":
    main()
