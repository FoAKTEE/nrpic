"""Figure: the first collisional King clusters (scouting runs, one seed each; released collision
operator; N = 1e5; static mesh).

(a) central lapse of each collisional run minus that of its collisionless control (same
    model, same mesh, interpolated to the same times), up to the first excision; crosses: the
    smallest lapse on the mesh falls below 0.3; dashed line: a drop of 0.01;
(b) central lapse of the two controls minus its first value: the slow outward excursion that
    limits what the collisional runs can show.
CC1 is the King model at the collisionless binding-energy maximum, CC2 a less compact one.
Reads the histories of the card runs cc_a, cc_b, cc_c (common.RUNS, common.CC_RUN).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_cluster"
DROP = 0.01


def hist(case):
    return cm.read_hist(cm.run_file(cm.CC_RUN[case], f"{case}/cc.nrpic.hst"))


def main():
    out = cm.out_dir("figures")
    H = {c: hist(c) for c in cm.CC_RUN}
    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.6))
    axa = fig.add_axes([0.1, 0.17, 0.38, 0.76])
    axb = fig.add_axes([0.59, 0.17, 0.375, 0.76])
    col = {"kn10": cz.PAL["blue"], "kn1": cz.PAL["red"]}
    lab = {"kn10": r"Kn$\,=10$", "kn1": r"Kn$\,=1$"}
    res = {}
    for cc in ("cc1", "cc2"):
        hc = H[f"{cc}_kninf"]
        fc = np.isfinite(hc["alpha_probe"])
        ls = "-" if cc == "cc1" else "--"
        for kn in ("kn10", "kn1"):
            h = H[f"{cc}_{kn}"]
            ok = np.isfinite(h["alpha_probe"]) & (h["n_excised"] == 0)
            t = h["time"][ok]
            d = h["alpha_probe"][ok] - np.interp(t, hc["time"][fc], hc["alpha_probe"][fc])
            i = np.flatnonzero(d < -DROP)
            i3 = np.flatnonzero(h["alpha_min"] < 0.3)
            t3 = float(h["time"][i3[0]]) if i3.size else None
            res[f"{cc}_{kn}"] = dict(t_drop=float(t[i[0]]) if i.size else None, t_03=t3)
            axa.plot(t, d, ls, color=col[kn], lw=1.2,
                     label=f"{cc.upper()}, {lab[kn]}")
            if t3 is not None:
                axa.plot([t3], [np.interp(t3, t, d)], "x", color=col[kn], ms=6, mew=1.4)
        a0 = hc["alpha_probe"][fc]
        axb.plot(hc["time"][fc], a0 - a0[0], ls, color="k", lw=1.2, label=f"{cc.upper()} control")
        res[f"{cc}_kninf"] = dict(max_rise=float(np.max(a0 - a0[0])),
                                  t_max=float(hc["time"][fc][np.argmax(a0 - a0[0])]),
                                  n_end=float(hc["np"][-1]), t_end=float(hc["time"][-1]))
    axa.axhline(-DROP, **cz.GUIDE)
    axa.axhline(0, color="k", lw=0.6)
    axa.set_xlim(0, 230)
    axa.set_ylim(-0.52, 0.08)
    axa.set_xlabel(r"time $t/M$")
    axa.set_ylabel(r"$\alpha_c-\alpha_c^{\rm control}$")
    axa.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.38, 0.0), fontsize=7,
               handlelength=1.8, ncol=1)
    axa.text(0.03, 0.92, "(a)", transform=axa.transAxes, fontsize=8.5)
    axa.text(0.97, 0.92, "scouting runs, one seed each", transform=axa.transAxes, fontsize=7.5,
             ha="right")
    axb.axhline(0, color="k", lw=0.6)
    axb.set_xlim(0, 300)
    axb.set_ylim(-0.005, 0.04)
    axb.set_xlabel(r"time $t/M$")
    axb.set_ylabel(r"control: $\alpha_c(t)-\alpha_c(0)$")
    axb.legend(frameon=False, loc="upper right", fontsize=7, handlelength=1.8)
    axb.text(0.03, 0.9, "(b)", transform=axb.transAxes, fontsize=8.5)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    for k, v in res.items():
        print(f"{STEM}: {k}: {v}")


if __name__ == "__main__":
    main()
