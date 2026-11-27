#!/usr/bin/env python3
"""C3 of gate G2 (decision 0046 item 2b): the mesh pair at a fixed eight particles per cell.

Reads pop.cstat.hst of the 64^3 member (q0070) and of the 128^3 member (the cut run and its
continuation), both zero shift, sigma1 = 0.014, the same realization (initial data
B-20261126-222552-2e44186 and B-20261124-135029-3fe13f6, 146 modes each). Writes c3.json with
the ratios that judge C3a and C3b (population/JOURNAL 2026-11-26 14:25):
  C3a  Hr_mean(64^3)/Hr_mean(128^3) in 1.5-4 at every common time with a = 25-141;
       refuted below 1.2 at any a >= 49;
  C3b  Mr_mean ratio 64/128 at least 1.2 at a = 49-141;
  side the run reaches a = 143 without a guard stop; K_max < 0 after t = 9.
For comparison the one-per-cell pair 128^3/256^3 with zero shift (M4, cut at a = 102 by the
256^3 stop) is drawn beside it. One figure, c3_mesh_pair.png (PDF beside).

    python3 judge_c3.py SCRATCH RUN64 OUTDIR

SCRATCH is scratch/B-emd-gw, RUN64 the run id of the 64^3 member.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

P8_128 = ["B-20261124-223926-33194d9", "B-20261125-221742-5100a22/p8_cont"]
BASE_128 = ["B-20261123-014847-f295ab4"]          # one per cell, zero shift
M256 = ["B-20261125-093500-242d3a3"]              # one per cell, zero shift, stops at a = 102
COL = {"t": 0, "K_max": 4, "Hr_mean": 11, "Mr_mean": 15}
A_LIST = (25, 36, 49, 64, 81, 100, 121, 141)


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


def keep_last(r):
    out = []
    for x in r:
        while out and out[-1][0] >= x[0]:
            out.pop()
        out.append(x)
    return np.array(out)


def history(scr, dirs):
    parts = [np.loadtxt(os.path.join(scr, d, "pop.cstat.hst"), ndmin=2) for d in dirs]
    return keep_last(np.concatenate(parts))


def interp(h, col, a):
    """log-log interpolation of a history column at scale factors a."""
    ah = scale(h[:, 0])
    return np.exp(np.interp(np.log(a), np.log(ah), np.log(np.abs(h[:, COL[col]]))))


def main():
    scr, run64, od = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(od, exist_ok=True)
    h64 = history(scr, [run64])
    h128 = history(scr, P8_128)
    hb = history(scr, BASE_128)
    hm = history(scr, M256)
    a64 = scale(h64[:, 0])
    out = {"run64": run64, "run128": P8_128, "t_end_64": float(h64[-1, 0]), "a_end_64": float(a64[-1]),
           "guard_64": os.path.exists(os.path.join(scr, run64, "pop.guard.txt")),
           "Kmax_max_after_t9_64": float(h64[h64[:, 0] > 9, COL["K_max"]].max()),
           "Kmax_max_after_t9_128": float(h128[h128[:, 0] > 9, COL["K_max"]].max()),
           "rows": []}
    # ratios at the 64^3 history times (the 128^3 history interpolated in log a, log value)
    sel = (a64 >= 25) & (a64 <= min(141.0, scale(h128[-1, 0])))
    rH = h64[sel, COL["Hr_mean"]]/interp(h128, "Hr_mean", a64[sel])
    rM = h64[sel, COL["Mr_mean"]]/interp(h128, "Mr_mean", a64[sel])
    late = a64[sel] >= 49
    out["Hr_ratio_min_25_141"] = float(rH.min())
    out["Hr_ratio_max_25_141"] = float(rH.max())
    out["Hr_ratio_min_49_141"] = float(rH[late].min())
    out["Mr_ratio_min_49_141"] = float(rM[late].min())
    out["Mr_ratio_max_49_141"] = float(rM[late].max())
    out["n_rows_25_141"] = int(sel.sum())
    out["C3a_holds"] = bool(rH.min() >= 1.5 and rH.max() <= 4.0)
    out["C3a_refuted"] = bool(rH[late].min() < 1.2)
    out["C3b_holds"] = bool(rM[late].min() >= 1.2)
    for a0 in A_LIST:
        j = int(np.argmin(np.abs(np.log(a64/a0))))
        row = {"a": a0, "a_64": float(a64[j]), "Hr_64": float(h64[j, COL["Hr_mean"]]),
               "Mr_64": float(h64[j, COL["Mr_mean"]])}
        row["Hr_128"] = float(interp(h128, "Hr_mean", a64[j:j+1])[0])
        row["Mr_128"] = float(interp(h128, "Mr_mean", a64[j:j+1])[0])
        row["Hr_ratio_64_over_128"] = row["Hr_64"]/row["Hr_128"]
        row["Mr_ratio_64_over_128"] = row["Mr_64"]/row["Mr_128"]
        if a0 <= scale(hm[-1, 0]):
            row["Hr_ratio_1ppc_128_over_256"] = float(interp(hb, "Hr_mean", np.array([a0]))[0]
                                                      / interp(hm, "Hr_mean", np.array([a0]))[0])
            row["Mr_ratio_1ppc_128_over_256"] = float(interp(hb, "Mr_mean", np.array([a0]))[0]
                                                      / interp(hm, "Mr_mean", np.array([a0]))[0])
        out["rows"].append(row)
    with open(os.path.join(od, "c3.json"), "w") as f:
        json.dump(out, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8), constrained_layout=True)
    ax = axs[0]
    for h, c, ls, lab in ((h64, "C3", "-", r"$64^3$, 8 per cell"), (h128, "C0", "-", r"$128^3$, 8 per cell"),
                          (hb, "0.45", ":", r"$128^3$, 1 per cell"), (hm, "0.2", "--", r"$256^3$, 1 per cell")):
        a = scale(h[:, 0])
        ax.loglog(a, h[:, COL["Hr_mean"]], color=c, ls=ls, lw=1.0, label=lab)
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel(r"$\langle |H| \rangle$ relative")
    ax.set_title("(a) zero shift, $\\sigma_1 = 0.014$", fontsize=7)
    ax.legend(fontsize=5.5, loc="lower right", frameon=False)
    ax = axs[1]
    am = a64[sel]
    ax.axhspan(1.5, 4.0, color="0.9", lw=0)
    ax.axhline(1.2, color="0.5", lw=0.6, ls=":")
    ax.semilogx(am, rH, color="C3", lw=1.0, label=r"$H$: $64^3$ over $128^3$, 8 per cell")
    ax.semilogx(am, rM, color="C3", lw=1.0, ls="--", label=r"$M$: $64^3$ over $128^3$, 8 per cell")
    ab = scale(hm[:, 0])
    ab = ab[(ab >= 25) & (ab <= scale(hm[-1, 0]))]
    ax.semilogx(ab, interp(hb, "Hr_mean", ab)/interp(hm, "Hr_mean", ab), color="0.3", lw=0.9,
                label=r"$H$: $128^3$ over $256^3$, 1 per cell")
    ax.semilogx(ab, interp(hb, "Mr_mean", ab)/interp(hm, "Mr_mean", ab), color="0.3", lw=0.9, ls="--",
                label=r"$M$: $128^3$ over $256^3$, 1 per cell")
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel("coarse over fine")
    from matplotlib.ticker import NullFormatter
    ax.set_xticks([25, 50, 100])
    ax.set_xticklabels(["25", "50", "100"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_title("(b) grey band: C3a predicted; dotted: refutation", fontsize=7)
    ax.legend(fontsize=5.5, loc="upper right", frameon=False)
    fs.save(fig, os.path.join(od, "c3_mesh_pair"))
    plt.close(fig)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in out["rows"]:
        print(r)


if __name__ == "__main__":
    main()
