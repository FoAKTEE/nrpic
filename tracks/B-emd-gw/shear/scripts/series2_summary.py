#!/usr/bin/env python3
"""Series 2 of the shear package (batch 11): L2 (beta = 0.5, HL = 4) with tlim = 10 at
N_y = 32, 64, 128 against the codes of arXiv:2003.08014 (draft.tex:360: CosmoGRaPH -0.8183
+- 0.0004, gevolution -0.619, GRAMSES -0.68), and S3 (beta = 0.005, HL = 4) over
N_y = 32, 64, 128 (series 1) and 256 (series 2). Predictions P9', P7': JOURNAL.md, entry of
2026-11-24 05:35.

    python3 series2_summary.py <series 1 run dir> <series 2 run dir> [<out dir>]

Writes series2.json and fig_series2 (PDF, PNG).
"""
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
from summarize_series import richardson  # noqa: E402

CODES = {"CosmoGRaPH": -0.8183, "gevolution": -0.619, "GRAMSES": -0.68}   # draft.tex:360


def rays(d, name):
    p = os.path.join(d, name, "rays.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def main():
    s1, s2 = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.environ["NRPIC_RUN_DIR"]
    res = {"L2": {}, "S3": {}}
    for n in (32, 64, 128):
        r = rays(s2, f"L2_n{n}")
        res["L2"][str(n)] = None if r is None else {
            "Delta": r.get("Delta"), "Delta_quad": r.get("Delta_quad"), "cos": r.get("cos"),
            "t_A": r.get("t_A"), "t_B": r.get("t_B"), "a_end": r.get("a_end"),
            "ok_A": r["shoot_A"].get("ok"), "ok_B": r["shoot_B"].get("ok"),
            "reason_A": r["shoot_A"].get("reason"), "reason_B": r["shoot_B"].get("reason"),
            "n_cross_A": len(r["shoot_A"].get("s", [])), "n_cross_B": len(r["shoot_B"].get("s", []))}
    L2 = [res["L2"][str(n)] for n in (32, 64, 128)]
    if all(x and x["Delta"] is not None for x in L2):
        c = [1.0 + x["Delta"] for x in L2]            # cos/cos_lin
        p, p_use, ext = richardson(c)
        res["L2"]["richardson"] = {"p_obs": p, "p_used": p_use, "Delta_ext": ext - 1.0,
                                   "err_128": c[2] - ext,
                                   "diff_32_64": c[0] - c[1], "diff_64_128": c[1] - c[2]}
        res["L2"]["distance_to_codes"] = {k: (ext - 1.0) - v for k, v in CODES.items()}
    S3 = {}
    for n, d in ((32, s1), (64, s1), (128, s1), (256, s2)):
        r = rays(d, f"S3_n{n}")
        S3[str(n)] = None if r is None else r.get("Delta")
    res["S3"]["Delta"] = S3
    v = [S3[str(n)] for n in (32, 64, 128, 256)]
    if all(x is not None for x in v):
        dif = [v[i] - v[i + 1] for i in range(3)]
        res["S3"]["differences"] = dif
        res["S3"]["orders"] = [math.log2(dif[i]/dif[i + 1]) if dif[i]*dif[i + 1] > 0 else None
                               for i in range(2)]
    with open(os.path.join(out, "series2.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.92, wspace=0.32)
    ny = np.array([32, 64, 128])
    if all(x and x["Delta"] is not None for x in L2):
        axs[0].plot(1.0/ny**2, [x["Delta"] for x in L2], "o-", color=fs.SERIES[0], lw=1.0,
                    label="this code, L2")
        rr = res["L2"]["richardson"]
        axs[0].plot([0.0], [rr["Delta_ext"]], "*", color=fs.SERIES[0], ms=8, label="extrapolated")
    for (k, val), col in zip(CODES.items(), fs.SERIES[1:]):
        axs[0].axhline(val, color=col, lw=1.0, ls="--", label=k + " (draft.tex:360)")
    axs[0].set_xlabel(r"$1/N_y^2$")
    axs[0].set_ylabel(r"$\Delta = \cos\theta/\cos\theta_{\rm lin} - 1$")
    axs[0].set_title(r"L2: $\beta = 0.5$, $HL = 4$", fontsize=8)
    axs[0].legend(fontsize=6, loc="best")
    if all(x is not None for x in v):
        n4 = np.array([32, 64, 128, 256])
        axs[1].loglog(n4, np.abs(v), "o-", color=fs.SERIES[0], lw=1.0, label=r"$|\Delta|$")
        axs[1].loglog(n4[:3], np.abs(dif), "s--", color=fs.SERIES[1], lw=1.0,
                      label=r"$|\Delta(N) - \Delta(2N)|$")
        axs[1].loglog(n4, 3e-5*(32.0/n4)**2, **{**fs.GUIDE, "lw": 0.8}, label=r"$N^{-2}$")
    axs[1].axhline(3e-4, color="0.5", lw=0.8, ls=":", label=r"$3\times10^{-4}$ (P7)")
    axs[1].set_xlabel(r"$N_y$")
    axs[1].set_ylabel("S3 (HL = 4, beta = 0.005)")
    axs[1].legend(fontsize=6, loc="best")
    fs.save(fig, os.path.join(out, "fig_series2"))
    plt.close(fig)


if __name__ == "__main__":
    main()
