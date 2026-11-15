"""Figure: card-hours of one realisation of the two test cases against the lattice size,
at Courant factor 0.25 with the noise synthesised at every stage: the track's model at the
scoping gate (assumed overhead of field and sources over Z4c) and the same step counts with
core's measured card throughput of Z4c with the field and the stochastic sources
(costmodel.py states the inputs and the extrapolation). Horizontal lines: the downgrade
threshold of one realisation and the card-hour allotment of the track to the next gate.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import costmodel  # noqa: E402
import czstyle as cz  # noqa: E402

DOWNGRADE = 5.0     # card-hours per 256^3 realisation, SCOPE.md section 4 item 5
ALLOTMENT = 10.0    # card-hours of E to the next gate, decision 0014


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    rows, meta = costmodel.table()
    fig = plt.figure(figsize=(3.4, 2.75))
    ax = cz.inch_axes(fig, 0.72, 0.48, 2.55, 2.1)
    for j, (case, col, mk, lab) in enumerate((("quadratic", cz.PAL["blue"], "o", "slow roll"),
                                               ("inflection", cz.PAL["red"], "s", "ultra-slow roll"))):
        rr = [r for r in rows if r["case"] == case]
        N = np.array([r["N"] for r in rr], float) * (1.0 + (0.05 if j else -0.05))
        ax.plot(N, [r["model"] for r in rr], mk, mfc="none", color=col, ms=4.5, ls="none")
        lo = np.array([r["measured_lo"] for r in rr])
        hi = np.array([r["measured_hi"] for r in rr])
        ax.errorbar(N, 0.5 * (lo + hi), yerr=0.5 * (hi - lo), fmt=mk, color=col, ms=4.0,
                    lw=1.0, capsize=2, label=lab)
    ax.axhline(DOWNGRADE, **cz.GUIDE)
    ax.axhline(ALLOTMENT, color="k", lw=1.0, ls=(0, (1.5, 1.5)))
    ax.text(52, DOWNGRADE * 0.66, "downgrade threshold", fontsize=7.5, va="center")
    ax.text(52, ALLOTMENT * 1.4, "allotment to the next gate", fontsize=7.5, va="center")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks([64, 128, 256])
    ax.set_xticklabels(["64", "128", "256"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlim(48, 340)
    ax.set_ylim(5e-4, 40)
    ax.set_xlabel("cells per side")
    ax.set_ylabel("card-hours per realisation")
    ax.plot([], [], "o", mfc="none", color="grey", ms=4.5, label="model at scoping")
    ax.plot([], [], "o", color="grey", ms=4.0, label="measured throughput")
    ax.legend(loc="lower right", fontsize=6.8, handletextpad=0.3)
    cz.save(fig, os.path.join(out, "fig_cost"))
    for r in rows:
        print(r)
    print(meta)


if __name__ == "__main__":
    main()
