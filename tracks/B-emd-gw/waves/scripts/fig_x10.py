#!/usr/bin/env python3
"""Figure and summary of the x10 rounding check of test X at N = 64 (JOURNAL.md,
2026-11-19 16:00 and 2026-11-20 22:15): errors of the plus and cross polarization and of
the polarization ratio R = W_x/W_+ against time, at the amplitude of the reference runs
(x1) and at ten times it (x10), with the 2S prediction.

    python3 fig_x10.py <x1 dumps json> <x10 dumps json>

Writes $NRPIC_RUN_DIR/x10_check.{png,pdf,json}; copies the PNG to ../figs and the JSON to
../results.
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

KVEC = 2 * np.pi / 4.0 * np.array([1.0, 1.0, 0.0])


def series(recs, q, key="tt"):
    return np.array([r["time"] for r in recs]), np.array([r[key][q] for r in recs])


def main():
    p1, p10 = sys.argv[1], sys.argv[2]
    out = os.environ["NRPIC_RUN_DIR"]
    r1 = sorted(json.load(open(p1)), key=lambda r: r["time"])
    r10 = sorted(json.load(open(p10)), key=lambda r: r["time"])
    p = pr.predict_flrw_coupled(KVEC, (4.0, 4.0, 4.0), (64, 64, 64), 10.0, 0.25, scheme="2s")
    pa, pp = np.abs(p["ratio"]) - 1, np.angle(p["ratio"])
    summ = {"sources": {"x1": p1, "x10": p10},
            "pred_2s_end": {"amp": float(pa[-1]), "phase": float(pp[-1])}}
    for name, rr in (("x1", r1), ("x10", r10)):
        last = rr[-1]["tt"]
        summ[name] = {q: float(last[q]) for q in ("amp_p", "phase_p", "amp_x", "phase_x",
                                                  "pol_amp", "pol_phase")}
        summ[name]["plus_excess_amp"] = float(last["amp_p"] - pa[-1])
        summ[name]["plus_excess_phase"] = float(last["phase_p"] - pp[-1])
        summ[name]["cross_excess_amp"] = float(last["amp_x"] - pa[-1])
        summ[name]["cross_excess_phase"] = float(last["phase_x"] - pp[-1])
        summ[name]["max_abs_pol_phase"] = float(max(abs(r["tt"]["pol_phase"]) for r in rr))
        summ[name]["spectral_weyl_vs_tt_end"] = float(rr[-1]["weylS"]["vs_tt"])
    summ["ratio_x1_over_x10"] = {
        q: summ["x1"][q] / summ["x10"][q] for q in ("pol_amp", "pol_phase", "plus_excess_amp",
                                                     "plus_excess_phase")}
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.93, wspace=0.27)
    ax = axs[0]
    ax.plot(p["t"][1:], pp[1:], **dict(fs.GUIDE, lw=1.0), label="prediction (2S)")
    for name, rr, c in (("x1", r1, fs.PAL["red"]), ("x10", r10, fs.PAL["green"])):
        t, ph = series(rr, "phase_p")
        _, phx = series(rr, "phase_x")
        ax.plot(t[1:], ph[1:], color=c, label=f"plus, amplitude {name}")
        ax.plot(t[1:], phx[1:], color=c, ls="--", label=f"cross, {name}")
    ax.set_xlabel("t (conformal)")
    ax.set_ylabel("phase error of W (rad), TT")
    ax.set_title("test X, N = 64")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.35 * (hi - lo))
    ax.legend(loc="upper left", ncol=2, fontsize=7)
    ax = axs[1]
    for name, rr, c in (("x1", r1, fs.PAL["red"]), ("x10", r10, fs.PAL["green"])):
        t, rp = series(rr, "pol_phase")
        _, ra = series(rr, "pol_amp")
        ax.semilogy(t[1:], np.abs(rp[1:]) + 1e-18, color=c, label=f"|arg R error|, {name}")
        ax.semilogy(t[1:], np.abs(ra[1:]) + 1e-18, color=c, ls=":", label=f"||R| error|, {name}")
    t, rp = series(r10, "pol_phase")
    ax.semilogy(t[1:], 10 * np.abs(rp[1:]) + 1e-18, color=fs.PAL["blue"], lw=1.0, ls="--",
                label="x10 run times 10")
    ax.set_xlabel("t (conformal)")
    ax.set_ylabel("polarization ratio error")
    ax.set_title("R = W_x / W_+ against 0.5 e^i")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi * (hi / lo) ** 0.35)
    ax.legend(loc="upper left", ncol=2, fontsize=7)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"x10_check.{ext}"))
    plt.close(fig)
    with open(os.path.join(out, "x10_check.json"), "w") as f:
        json.dump(summ, f, indent=1)
    shutil.copy(os.path.join(out, "x10_check.png"), os.path.join(PKG, "figs", "x10_check.png"))
    shutil.copy(os.path.join(out, "x10_check.json"), os.path.join(PKG, "results", "x10_check.json"))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
