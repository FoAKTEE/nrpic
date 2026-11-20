"""Figure: heat conduction by the collision operator (gate G1, criterion "heat conduction at
the long and the short mean-free-path end").

(a) temperature step at a mean free path of one hundredth of the box: rest mass of the
    initially hot half against time in collision times, two seeds, with the nonlinear
    isobaric reference at the first Chapman-Enskog conductivity (f = 1);
(b) the code minus the reference at the conductivity factor f fitted to each seed;
(c) conductivity from the decay of the isobaric (entropy) mode against (k lambda)^2: each
    seed, the seed mean with its standard error, and the extrapolation to k lambda -> 0.
Reads runs t6b (reduced slab sums), t6ban (fitted f, window, collision time), t7an (mode
fits) and, for the seed counts, the summaries of t7a and t7b (common.RUNS). The reference is
recomputed with the heat package's module isobaric.py, unchanged.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
sys.path.insert(0, os.path.join(cm.TRACK, "heat", "scripts"))
import isobaric as iso  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_heat"
CASES = ("step_b_lam0.01_s1", "step_b_lam0.01_s2")


def main():
    out = cm.out_dir("figures")
    an = cm.load_json("t6ban", "T6b.json")
    anw = cm.load_json("t6bw", "T6b_w300-1374.json")
    t7 = cm.load_json("t7an", "T7.json")
    g = t7["groups"]["T7_th0.003_e0.2"]
    nseed = 0
    for key in ("t7a", "t7b"):
        nseed += len(cm.load_json(key, "summary.json"))

    series, P0 = [], None
    for c in CASES:
        P = cm.load_json("t6b", f"{c}/case.json")
        R = np.load(cm.run_file("t6b", f"{c}/reduced.npz"))
        area = P["box"][1] * P["box"][2]
        series.append(dict(seed=P["seed"], t=R["time"], X=R["slab_M"] / area))
        P0 = P0 or P
    L, th1, th2, sig = P0["box"][0], P0["theta1"], P0["theta2"], P0["sigma"]
    t = series[0]["t"]
    tcoll = an["s1"]["t_coll"]
    win = an["s1"]["window"]
    w = (t >= win[0]) & (t <= win[1])
    ref1 = iso.step_reference(L, 1.0, th1, th2, sig, t, f=1.0, nm=1200)[0][:, 0]
    reff = {}
    for s in series:
        f = an[f"s{s['seed']}"]["f"]
        reff[s["seed"]] = iso.step_reference(L, 1.0, th1, th2, sig, t, f=round(f, 5), nm=1200)[0][:, 0]
        rms = float(np.sqrt(np.mean((s["X"][w] - reff[s["seed"]][w]) ** 2)))
        s["rms"], s["f"] = rms, f

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.9))
    axa = fig.add_axes([0.095, 0.45, 0.36, 0.48])
    axb = fig.add_axes([0.095, 0.17, 0.36, 0.25])
    axc = fig.add_axes([0.6, 0.17, 0.37, 0.76])
    cols = {1: cz.PAL["red"], 2: cz.PAL["yellow"]}
    for s in series:
        axa.plot(t / tcoll, s["X"], "o", ms=1.6, color=cols[s["seed"]], label=f"seed {s['seed']}")
        axb.plot(t / tcoll, (s["X"] - reff[s["seed"]]) * 1e3, "o", ms=1.4, color=cols[s["seed"]])
    axa.plot(t / tcoll, ref1, color=cz.PAL["blue"], lw=1.3, label=r"isobaric, $f=1$")
    for a in (axa, axb):
        cz.average_window(a, win[0] / tcoll, win[1] / tcoll)
        a.set_xscale("log")
        a.set_xlim(5, 2e3)
    axa.set_xticklabels([])
    axa.set_ylabel("rest mass, hot half")
    axa.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.2, borderaxespad=0.2,
               bbox_to_anchor=(0.08, 1.0))
    axa.text(0.02, 0.88, "(a)", transform=axa.transAxes, fontsize=8.5)
    axb.axhline(0, color="k", lw=0.6)
    axb.set_ylim(-9, 9)
    axb.set_xlabel(r"time $t/t_{\rm coll}$")
    axb.set_ylabel(r"residual ($10^{-3}$)", fontsize=8)
    axb.text(0.02, 0.76, "(b)", transform=axb.transAxes, fontsize=8.5)

    # (c) conductivity against (k lambda)^2
    x2 = []
    for r in g["rows"]:
        kl2 = r["k_lambda"] ** 2
        fs_ = [ft["f_S"] for ft in r["fits"]]
        axc.plot(np.full(len(fs_), kl2) + np.linspace(-0.002, 0.002, len(fs_)), fs_, "o",
                 ms=2.4, mfc="none", mec="0.55", mew=0.6)
        axc.errorbar([kl2], [r["f_S"][0]], yerr=[r["f_S"][1]], fmt="o", ms=4.5,
                     color=cz.PAL["red"], elinewidth=1.0, capsize=0)
        x2.append(kl2)
    xx = np.linspace(0, max(x2) * 1.1, 50)
    axc.plot(xx, g["f0"] + g["slope_b"] * xx, color="k", lw=1.2)
    axc.errorbar([0], [g["f0"]], yerr=[g["f0_se"]], fmt="s", ms=4.5, mfc="white", mec="k",
                 color="k", elinewidth=1.0, capsize=0)
    axc.axhspan(0.99, 1.06, color="0.85", alpha=0.5, lw=0)
    axc.axhline(1.0, color="0.4", lw=0.7, ls=":")
    axc.set_xlim(-0.01, max(x2) * 1.12)
    axc.set_ylim(0.96, 1.10)
    axc.set_xlabel(r"$(k\lambda)^2$")
    axc.set_ylabel(r"conductivity $\kappa/\kappa_1$")
    axc.text(0.04, 0.93, "(c)", transform=axc.transAxes, fontsize=8.5)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    for s in series:
        a = an[f"s{s['seed']}"]
        print(f"{STEM}: T6(b) seed {s['seed']}: f {a['f']:.4f} (late window "
              f"{anw['s%d' % s['seed']]['f']:.4f}), literal {a['literal_ratio']:.4f}; rms residual "
              f"recomputed {s['rms']:.6e} vs analysis {a['rms_resid_f']:.6e} "
              f"(rel. diff {abs(s['rms'] / a['rms_resid_f'] - 1):.1e})")
    print(f"{STEM}: T6(b) mean f {an['combined']['f_mean']:.4f} +- {an['combined']['f_se']:.4f}")
    for r in g["rows"]:
        print(f"{STEM}: T7 k lambda {r['k_lambda']}: f_S {r['f_S'][0]:.4f} +- {r['f_S'][1]:.4f} "
              f"({r['n_seeds']} seeds of {r['n_per_seed']}); number mode {r['f_N'][0]:.3f}")
    print(f"{STEM}: T7 extrapolated {g['f0']:.4f} +- {g['f0_se']:.4f}, pass {g['pass_T7']}; "
          f"processor cases in the two run summaries: {nseed}")


if __name__ == "__main__":
    main()
