#!/usr/bin/env python3
"""T4 on a common window (threshold_ball entry 11): C-d0.42 against B-d0.42 from the numbers
written by analyse.py, on times both meshes share, instead of medians over different windows.

    t4_common.py --ana <analyse.py run dir> --out DIR [--t0 46.75]

(1) line Misner-Sharp mass of the outermost trapped sphere against the exact shell mass at its
    radius, at the line times both meshes have, t >= t0 (past the first-detection transient);
(2) the finder's m_irr of B and C interpolated to common times: their relative difference;
(3) the search interval of each mesh (the quantum of the first-detection time behind ddet).
Writes t4_common.json and fig_t4_common.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load(ana, name):
    j = json.load(open(os.path.join(ana, f"{name}_numbers.json")))
    ent = j["line_horizon"]["entries"]
    line = np.array([(e["t"], e["m"], e["m_exact_shell"]) for e in ent], float)
    rows = j["finder"]["rows"]
    fnd = np.array([(r["t"], r["m_irr"], r.get("m_exact_shell_at_r") or np.nan) for r in rows], float)
    return line, fnd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ana", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--t0", type=float, default=46.75)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L, F = {}, {}
    for n in ("B-d0.42", "C-d0.42"):
        L[n], F[n] = load(a.ana, n)
    tB, tC = np.round(L["B-d0.42"][:, 0], 4), np.round(L["C-d0.42"][:, 0], 4)
    common = np.intersect1d(tB[tB >= a.t0], tC[tC >= a.t0])
    res = dict(t0=a.t0, n_common_line_times=int(len(common)))
    err = {}
    for n, tt in (("B-d0.42", tB), ("C-d0.42", tC)):
        sel = np.isin(tt, common)
        e = L[n][sel, 1] / L[n][sel, 2] - 1.0
        err[n] = (L[n][sel, 0], e)
        res[n] = dict(line_median_rel=float(np.median(e)), line_median_abs=float(np.median(np.abs(e))),
                      line_maxabs=float(np.max(np.abs(e))),
                      search_dt=float(np.median(np.diff(F[n][:, 0]))),
                      first_t=float(F[n][0, 0]), m_irr_first=float(F[n][0, 1]), m_irr_last=float(F[n][-1, 1]),
                      t_last=float(F[n][-1, 0]))
    res["ratio_C_over_B_line_median_abs"] = res["C-d0.42"]["line_median_abs"] / res["B-d0.42"]["line_median_abs"]
    tg = np.arange(max(F["B-d0.42"][0, 0], F["C-d0.42"][0, 0]), min(F["B-d0.42"][-1, 0], F["C-d0.42"][-1, 0]), 0.0625)
    mB = np.interp(tg, F["B-d0.42"][:, 0], F["B-d0.42"][:, 1])
    mC = np.interp(tg, F["C-d0.42"][:, 0], F["C-d0.42"][:, 1])
    d = mC / mB - 1.0
    res["finder_C_over_B"] = dict(median=float(np.median(d)), maxabs=float(np.max(np.abs(d))),
                                  maxabs_after_t0=float(np.max(np.abs(d[tg >= a.t0]))), n=int(len(tg)))
    json.dump(res, open(os.path.join(a.out, "t4_common.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(HERE, "..", "..", "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.32)
    ax = axs[0]
    for n, c in (("B-d0.42", fs.PAL["red"]), ("C-d0.42", fs.PAL["blue"])):
        ax.plot(L[n][:, 0], np.abs(L[n][:, 1] / L[n][:, 2] - 1.0), "o", ms=3, color=c,
                label=f"{n[0]}: M/{'32' if n[0] == 'B' else '64'}")
    ax.axvline(a.t0, color="0.5", lw=0.8, ls=":")
    ax.set_yscale("log")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$|m_{\rm MS,line}/m_{\rm shell}-1|$")
    ax.set_title(r"line MOTS mass against exact shell mass", fontsize=9)
    ax.legend(fontsize=8)
    ax = axs[1]
    ax.plot(tg, d, "-", color=fs.PAL["blue"])
    ax.axhline(0, color="0.5", lw=0.8)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$m_{\rm irr}^{C}/m_{\rm irr}^{B}-1$")
    ax.set_title("finder mass, C against B", fontsize=9)
    fig.savefig(os.path.join(a.out, "fig_t4_common.png"), dpi=150)
    fig.savefig(os.path.join(a.out, "fig_t4_common.pdf"))


if __name__ == "__main__":
    main()
