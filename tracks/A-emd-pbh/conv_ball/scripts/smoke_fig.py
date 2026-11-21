#!/usr/bin/env python3
"""Figure of the processor smoke test (package conv_ball; JOURNAL.md entry 3, prediction S):
the conformal factor psi^4 that AthenaK set up at t = 0 on the line y = z = h_l/2 through the
nested levels of the decks nest16_L16, nest32_L16 and nest64_L16, against expball's exact
slice at the same points, and the cell width of each line point (which also checks the
line-point reader common.line_points_levels used by compare.py --nest).

    smoke_fig.py --smoke <smoke run dir> --prep <prep dir of data set 3> --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C            # noqa: E402
import nested as NS           # noqa: E402

CASES = (("s16", 16), ("s32", 32), ("s64", 64))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", required=True)
    ap.add_argument("--prep", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    ball = C.ball_from_spec(ex["spec"])
    rm = ball.matter_rbar()
    res = {}
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9.0, 3.4))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.15, top=0.88, wspace=0.32)
    axs = [fig.add_subplot(1, 3, k + 1) for k in range(3)]
    cols = fs.series_colors(3, "viridis") if hasattr(fs, "series_colors") else [None] * 3
    for c_, (case, hinv) in zip(cols, CASES):
        recs = C.read_tab_series([os.path.join(a.smoke, case)], "adm")
        rec = recs[0]
        lev = NS.nest_levels(1.0 / hinv, 16.0)
        x = C.line_points_levels(rec, lev)
        r = np.sqrt(np.sum(x * x, axis=1))
        h = 2.0 * x[:, 1]
        psi4 = rec["adm_psi4"]
        u = ball.fields(np.minimum(r, 1.5 * rm), ("u",))["u"]
        ex4 = np.where(r < 1.5 * rm, (1.0 + u) ** 4, np.nan)
        err = psi4 / ex4 - 1.0
        inside = (r < rm - 0.5) & np.isfinite(err)
        res[case] = dict(n_points=int(len(r)), h_min=float(h.min()), h_max=float(h.max()),
                         maxabs_rel_err_psi4_inside=float(np.nanmax(np.abs(err[inside]))),
                         median_abs_rel_err_psi4_inside=float(np.nanmedian(np.abs(err[inside]))),
                         gxx_minus_psi4_maxabs=float(np.nanmax(np.abs(rec["adm_gxx"] - psi4))))
        o = np.argsort(x[:, 0])
        axs[0].plot(x[o, 0], psi4[o], color=c_, lw=1.0, label=f"nest{hinv}: AthenaK")
        axs[1].semilogy(x[o, 0], np.abs(err[o]) + 1e-17, ".", color=c_, ms=2.5, label=f"nest{hinv}")
        axs[2].step(x[o, 0], h[o], where="mid", color=c_, lw=1.2, label=f"nest{hinv}")
    rr = np.linspace(-6, 6, 2001)
    uu = ball.fields(np.abs(rr), ("u",))["u"]
    axs[0].plot(rr, (1 + uu) ** 4, color="k", lw=0.8, ls=":", label="exact (expball)")
    axs[0].set_xlim(-6, 6)
    axs[0].set_xlabel(r"$x\,/M$")
    axs[0].set_ylabel(r"$\psi^4$ at $t=0$")
    axs[0].legend(fontsize=6)
    axs[1].set_xlim(-6, 6)
    axs[1].set_xlabel(r"$x\,/M$")
    axs[1].set_ylabel(r"$|\psi^4/\psi^4_{\rm exact}-1|$")
    axs[1].legend(fontsize=6)
    axs[2].set_yscale("log", base=2)
    axs[2].set_xlabel(r"$x\,/M$")
    axs[2].set_ylabel("cell width of the line point $/M$")
    axs[2].legend(fontsize=6)
    for ax, t in zip(axs, ("initial conformal factor", "against the exact slice", "levels on the line")):
        ax.set_title(t, fontsize=9)
    fs.save(fig, os.path.join(a.out, "fig_smoke"))
    with open(os.path.join(a.out, "smoke_fig.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
