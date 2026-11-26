#!/usr/bin/env python3
"""Histories of the full-GR population legs (batch 23): largest K of the box, Hr_mean and
Mr_mean of pop.cstat.hst against a, for the 0.014 box at 128^3 (zero shift, base), 256^3 (zero
shift, mesh leg, guard stop), 128^3 with 8 particles per cell (cut run and its continuation),
128^3 with the Gamma-driver shift (gauge leg), and the 0.028 box with zero shift (guard stop)
and with the Gamma-driver shift from t = 8. One figure, pop_leg_histories.png (PDF beside), and
leg_histories.json with the numbers that judge M1, M4, P8C2, Q1 (constraint part) and S1
(JOURNAL.md, entries of 2026-11-24 06:10, 2026-11-25 04:00 and 18:35).

    python3 fig_leg_histories.py SCRATCH OUTDIR

SCRATCH is scratch/B-emd-gw; the run ids are fixed below (registered runs).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

RUNS = {   # name: (directories in order, label)
    "base": (["B-20261123-014847-f295ab4"], r"$128^3$, zero shift"),
    "m256": (["B-20261125-093500-242d3a3"], r"$256^3$, zero shift"),
    "p8": (["B-20261124-223926-33194d9", "B-20261125-221742-5100a22/p8_cont"],
           r"$128^3$, 8 per cell, zero shift"),
    "gd": (["B-20261124-210431-6bf48af"], r"$128^3$, Gamma driver"),
    "s028": (["B-20261123-035002-bcc82bd"], r"$\sigma_1 = 0.028$, zero shift"),
    "s028gd": (["B-20261123-035002-bcc82bd", "B-20261126-011415-449c8ce/s028_gd"],
               r"$\sigma_1 = 0.028$, Gamma driver from $t = 8$"),
}
COL = {"t": 0, "K_max": 4, "Hr_mean": 11, "Mr_mean": 15}


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


def rows(fn):
    return np.loadtxt(fn, ndmin=2)


def keep_last(r):
    out = []
    for x in r:
        while out and out[-1][0] >= x[0]:
            out.pop()
        out.append(x)
    return np.array(out)


def history(scr, dirs, cut=None):
    """Concatenated cstat rows (later directory wins at equal or later t). For s028gd the
    zero-shift rows are kept only to t = 8, where the shifted run restarts."""
    parts = []
    for i, d in enumerate(dirs):
        r = rows(os.path.join(scr, d, "pop.cstat.hst"))
        parts.append(r)
    return keep_last(np.concatenate(parts))


def at(h, col, a0):
    a = scale(h[:, 0])
    j = int(np.argmin(np.abs(np.log(a/a0))))
    return float(h[j, COL[col]]), float(a[j])


def main():
    scr, od = sys.argv[1], sys.argv[2]
    os.makedirs(od, exist_ok=True)
    H = {k: history(scr, v[0]) for k, v in RUNS.items()}
    out = {"runs": {k: v[0] for k, v in RUNS.items()}}
    # M1 and the stop of the mesh leg
    g = open(os.path.join(scr, RUNS["m256"][0][0], "pop.guard.txt")).read().splitlines()[0]
    hm = H["m256"]
    pos = np.nonzero(hm[:, COL["K_max"]] > 0)[0]
    out["M1"] = {"guard": g, "t_end_hst": float(hm[-1, 0]), "a_end_hst": float(scale(hm[-1, 0])),
                 "t_first_Kmax_pos": float(hm[pos[0], 0]) if len(pos) else None,
                 "a_first_Kmax_pos": float(scale(hm[pos[0], 0])) if len(pos) else None,
                 "Kmax_last": float(hm[-1, COL["K_max"]])}
    hb = H["base"]
    out["base_Kmax_max_after_t9"] = float(hb[hb[:, 0] > 9, COL["K_max"]].max())
    hg = H["gd"]
    out["gd_Kmax_max_after_t9"] = float(hg[hg[:, 0] > 9, COL["K_max"]].max())
    # M4 at equal a (the written a = 141 is not reached by the mesh leg)
    out["M4"] = []
    for a0 in (36, 49, 64, 81, 90, 100):
        hb_, ab = at(hb, "Hr_mean", a0)
        hm_, am = at(hm, "Hr_mean", a0)
        mb, _ = at(hb, "Mr_mean", a0)
        mm, _ = at(hm, "Mr_mean", a0)
        out["M4"].append({"a": a0, "a_base": ab, "a_m256": am, "Hr_base": hb_, "Hr_m256": hm_,
                          "Hr_ratio_base_over_m256": hb_/hm_, "Mr_base": mb, "Mr_m256": mm,
                          "Mr_ratio_base_over_m256": mb/mm})
    # P8C2: rows of the continuation against the cut run at 16.0 <= t <= 17.48
    cut = keep_last(rows(os.path.join(scr, RUNS["p8"][0][0], "pop.cstat.hst")))
    con = keep_last(rows(os.path.join(scr, RUNS["p8"][0][1], "pop.cstat.hst")))
    p8c2 = []
    for r in con:
        if r[0] > cut[-1, 0] + 1e-9:
            break
        j = np.nonzero(np.abs(cut[:, 0] - r[0]) < 1e-6)[0]
        if not len(j):
            continue
        c = cut[j[0]]
        p8c2.append({"t": float(r[0]),
                     "dHr_rel": float(abs(r[COL["Hr_mean"]] - c[COL["Hr_mean"]])/abs(c[COL["Hr_mean"]])),
                     "dKmax_rel": float(abs(r[COL["K_max"]] - c[COL["K_max"]])/abs(c[COL["K_max"]])),
                     "dMr_rel": float(abs(r[COL["Mr_mean"]] - c[COL["Mr_mean"]])/abs(c[COL["Mr_mean"]]))})
    out["P8C2"] = {"rows": p8c2, "max_rel": max(max(x["dHr_rel"], x["dKmax_rel"], x["dMr_rel"])
                                                for x in p8c2) if p8c2 else None}
    # Q1, constraint part: Mr_mean of 8 per cell against one per cell at a = 141 (t = 21.727)
    hp = H["p8"]
    out["Q1_constraints"] = []
    for a0 in (25, 49, 81, 100, 121, 141):
        mp, ap = at(hp, "Mr_mean", a0)
        mb, ab = at(hb, "Mr_mean", a0)
        hp_, _ = at(hp, "Hr_mean", a0)
        hb_, _ = at(hb, "Hr_mean", a0)
        out["Q1_constraints"].append({"a": a0, "a_p8": ap, "a_base": ab, "Mr_p8": mp, "Mr_base": mb,
                                      "Mr_ratio_base_over_p8": mb/mp, "Hr_p8": hp_, "Hr_base": hb_,
                                      "Hr_ratio_base_over_p8": hb_/hp_})
    # S1: the 0.028 box with the shift from t = 8 to the end
    hs = H["s028gd"]
    hz = H["s028"]
    out["S1"] = {"t_end": float(hs[-1, 0]), "a_end": float(scale(hs[-1, 0])),
                 "Hr_mean_end": float(hs[-1, COL["Hr_mean"]]), "Mr_mean_end": float(hs[-1, COL["Mr_mean"]]),
                 "Hr_mean_max": float(hs[hs[:, 0] > 8, COL["Hr_mean"]].max()),
                 "Kmax_max_after_t8_5": float(hs[hs[:, 0] > 8.5, COL["K_max"]].max()),
                 "zero_shift_t_end": float(hz[-1, 0]),
                 "guard": os.path.exists(os.path.join(scr, RUNS["s028gd"][0][1], "pop.guard.txt"))}
    with open(os.path.join(od, "leg_histories.json"), "w") as f:
        json.dump(out, f, indent=1)
    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6), constrained_layout=True)
    style = {"base": ("k", "-"), "m256": ("C3", "-"), "p8": ("C0", "--"), "gd": ("C2", "-"),
             "s028": ("0.5", ":"), "s028gd": ("C1", "-.")}
    for k, h in H.items():
        a = scale(h[:, 0])
        c, ls = style[k]
        lab = RUNS[k][1]
        K = h[:, COL["K_max"]]
        axs[0].plot(a, np.sign(K)*np.log10(1 + np.abs(K)/1e-4), color=c, ls=ls, lw=0.9, label=lab)
        axs[1].semilogy(a, h[:, COL["Hr_mean"]], color=c, ls=ls, lw=0.9)
        axs[2].semilogy(a, h[:, COL["Mr_mean"]], color=c, ls=ls, lw=0.9)
    for ax in axs:
        ax.set_xscale("log")
        ax.set_xlabel(r"$a$")
    axs[0].axhline(0, color="0.7", lw=0.5)
    axs[0].set_ylabel(r"$\mathrm{sgn}(K_{\max})\log_{10}(1 + |K_{\max}|/10^{-4})$")
    axs[1].set_ylabel(r"$\langle |H| \rangle$ relative")
    axs[2].set_ylabel(r"$\langle |M| \rangle$ relative")
    axs[0].set_title("largest $K$ of the box", fontsize=7)
    axs[1].set_title("Hamiltonian constraint", fontsize=7)
    axs[2].set_title("momentum constraint", fontsize=7)
    axs[0].legend(fontsize=5, loc="lower left", frameon=False)
    fs.save(fig, os.path.join(od, "pop_leg_histories"))
    plt.close(fig)
    print(json.dumps({k: v for k, v in out.items() if k != "P8C2"}, indent=1))
    print("P8C2 max rel", out["P8C2"]["max_rel"], "rows", len(p8c2))


if __name__ == "__main__":
    main()
