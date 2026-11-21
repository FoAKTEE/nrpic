"""Checks of individual claims read after the blind verdicts (VERIFIER.md):
(1) total collisions 385554 of the T10 runs (release C-20261115-165902-f9b1c8f and
    collisions-2 C-20261119-143041-f94e350), and the release T10 snapshots bit-identical;
(2) the King sequence's first mass maximum at y0 = 0.0982 (REVIEW-wave2.md section 3), with
    the King ansatz at fixed amplitude (my v4_ev solver);
(3) T6(b) literal statistic with chi_1 at theta = 0.015 instead of the final temperature;
(4) the Chapman-Enskog ratios quoted from my V1a at theta = 0.1 and 1.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import lib  # noqa: E402
from lib import COLL  # noqa: E402
import v4_ev  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v6")
    os.makedirs(out, exist_ok=True)
    res = {}
    # (1)
    t10 = {}
    for run in ["C-20261115-165902-f9b1c8f", "C-20261119-143041-f94e350"]:
        d = f"{SCR}/{run}"
        row = {}
        for c in ["mb1", "mb8", "mb64", "seed8"]:
            h = lib.read_hist(f"{d}/{c}/box.coll.hst")
            row[c + "_ncoll_total"] = int(h[:, COLL["n_coll"]].sum())
            row[c + "_records"] = int(h.shape[0])
        ref = open(f"{d}/mb1/box.part.00001.bin", "rb").read()
        for c in ["mb8", "mb64", "rst0", "rst1", "rst2", "seed8"]:
            p = f"{d}/{c}/box.part.00001.bin"
            row[c + "_snapshot_bytes_equal_mb1"] = (open(p, "rb").read() == ref) if os.path.exists(p) else None
        t10[run] = row
        print(run, json.dumps(row))
    res["T10_counts"] = t10
    # (2) King mass along y0 at fixed amplitude (f = exp(1 - E/E0) - 1)
    ys = np.linspace(0.01, 0.9, 90)
    M = np.array([v4_ev.solve(t, 1.0)[0]["M"] for t in ys])
    i = int(np.argmax(M))
    ymax = optimize.minimize_scalar(lambda t: -v4_ev.solve(t, 1.0)[0]["M"], bounds=(ys[max(i - 1, 0)], ys[min(i + 1, len(ys) - 1)]),
                                    method="bounded", options=dict(xatol=1e-8)).x
    N = np.array([v4_ev.solve(t, 1.0)[0]["N"] for t in ys])
    j = int(np.argmax(N))
    ynmax = optimize.minimize_scalar(lambda t: -v4_ev.solve(t, 1.0)[0]["N"], bounds=(ys[max(j - 1, 0)], ys[min(j + 1, len(ys) - 1)]),
                                     method="bounded", options=dict(xatol=1e-8)).x
    res["king_mass_max"] = dict(y0_M_max=float(ymax), M_max=float(v4_ev.solve(ymax, 1.0)[0]["M"]),
                                y0_N_max=float(ynmax), claim=0.0982)
    print("King M max", res["king_mass_max"])
    # (3) T6(b) literal statistic at theta = 0.015
    st = json.load(open(os.path.join(HERE, "results", "v1_step.json")))
    conv = []
    for r in st["rows"]:
        th_f, cp_f, chi1_f = r["theta_f"], r["c_p_f"], r["chi1"]
        cp15 = 1 + lib.c_v(0.015)
        chi1_15 = chi1_f*np.sqrt(0.015/th_f)*cp_f/cp15
        conv.append(dict(case=r["case"], mine_final_T=r["chi_ratio_linear"], chi1_ratio=chi1_15/chi1_f,
                         mine_at_0p015=r["chi_ratio_linear"]*chi1_f/chi1_15))
    res["T6b_literal_at_0p015"] = conv
    print("T6b", conv)
    # (4) CE ratios of V1a
    ce = json.load(open(os.path.join(HERE, "results", "ce_kappa.json")))
    k1 = 75*np.sqrt(np.pi)/64
    res["CE_ratio_order4"] = {str(r["theta"]): dict(ratio=r["orders"][-1]["kappa"]/k1, se=r["orders"][-1]["se"]/k1)
                              for r in ce["rel"]}
    print("CE", res["CE_ratio_order4"])
    lib.save_json(os.path.join(out, "v6_claims.json"), res)
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.9)
    ax.plot(ys, M, color=figstyle.PAL["blue"], label="M (ADM)")
    ax.plot(ys, N, color=figstyle.PAL["red"], label="N (rest mass)")
    ax.axvline(ymax, **figstyle.GUIDE)
    ax.axvline(0.0982, color=figstyle.PAL["green"], lw=1, ls=":")
    ax.set_xlabel(r"$y_0$ (King, $b$ = 1, fixed amplitude)")
    ax.set_ylabel("mass (G = c = 1)")
    ax.set_title("max of M at y0 = %.4f (dashed); claim 0.0982 (dotted)" % ymax, fontsize=8)
    ax.legend(fontsize=7)
    fig.savefig(os.path.join(out, "v6_king_mass.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
