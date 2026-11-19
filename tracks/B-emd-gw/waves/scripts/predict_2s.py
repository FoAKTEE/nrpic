#!/usr/bin/env python3
"""Test of hypothesis H1 (JOURNAL.md, 15:05): the errors of test X follow from the code's
time integrator RK4()4[2S] applied to the uniform background coupled to the mode.

    python3 predict_2s.py <results.json of an analysis run> ...

Writes $NRPIC_RUN_DIR/predict_2s.json and predict_2s.png (copies in ../results, ../figs):
for N = 16, 32, 48, 64 the end-time amplitude and phase errors of three predictors
(exact background with classical RK4; coupled background with classical RK4; coupled
background with the 2S scheme) and the a(t) error of the coupled ones, beside the measured
values of every results.json given (later files override earlier ones per N).
"""
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import PKG  # noqa: E402
from wlib import predict as pr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

KV = np.pi / 2 * np.array([1.0, 1.0, 0.0])
NS = (16, 32, 48, 64)


def main():
    out = os.environ["NRPIC_RUN_DIR"]
    meas = {}
    for f in sys.argv[1:]:
        r = json.load(open(f))
        for n, s in r["exp"].items():
            if n.isdigit():
                meas[int(n)] = {"amp": s["tt"]["amp_p_end"], "phase": s["tt"]["phase_p_end"],
                                "a_err": s["a_rel_err_max"], "source": f}
    res = {}
    for n in NS:
        p0 = pr.predict_flrw(KV, (4, 4, 4), (n, n, n), 10.0, 0.25)
        pc = pr.predict_flrw_coupled(KV, (4, 4, 4), (n, n, n), 10.0, 0.25, scheme="classical")
        p2 = pr.predict_flrw_coupled(KV, (4, 4, 4), (n, n, n), 10.0, 0.25, scheme="2s")
        res[n] = {k: {"amp": float(np.abs(p["ratio"][-1]) - 1), "phase": float(np.angle(p["ratio"][-1]))}
                  for k, p in (("exact_bg_classical", p0), ("coupled_classical", pc), ("coupled_2s", p2))}
        res[n]["coupled_classical"]["a_err"] = float(np.max(np.abs(pc["a_rel_err"])))
        res[n]["coupled_2s"]["a_err"] = float(np.max(np.abs(p2["a_rel_err"])))
        if n in meas:
            res[n]["measured"] = meas[n]
            res[n]["ratio_2s_over_measured"] = {q: res[n]["coupled_2s"][q] / meas[n][q]
                                                for q in ("amp", "phase")}
    with open(os.path.join(out, "predict_2s.json"), "w") as f:
        json.dump(res, f, indent=1)
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    nn = np.array(NS, float)
    for ax, q in zip(axs, ("amp", "phase")):
        for key, c, mk, lab in (("exact_bg_classical", "k", "+", "exact background, classical RK4"),
                                ("coupled_classical", fs.PAL["yellow"], "x", "coupled, classical RK4"),
                                ("coupled_2s", fs.PAL["blue"], "o", "coupled, RK4()4[2S] (code)")):
            ax.loglog(nn, [abs(res[n][key][q]) for n in NS], marker=mk, color=c, ls="-", lw=1.0, label=lab)
        mn = [n for n in NS if n in meas]
        ax.loglog(mn, [abs(meas[n][q]) for n in mn], "s", color=fs.PAL["red"], ms=6, mfc="none",
                  label="measured (TT)")
        ax.set_xlabel("N")
        ax.set_title("|amplitude error| at t = 10" if q == "amp" else "|phase error| (rad) at t = 10")
        ax.legend(loc="lower left", fontsize=7)
    fig.savefig(os.path.join(out, "predict_2s.png"))
    fig.savefig(os.path.join(out, "predict_2s.pdf"))
    shutil.copy(os.path.join(out, "predict_2s.json"), os.path.join(PKG, "results", "predict_2s.json"))
    shutil.copy(os.path.join(out, "predict_2s.png"), os.path.join(PKG, "figs", "predict_2s.png"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
