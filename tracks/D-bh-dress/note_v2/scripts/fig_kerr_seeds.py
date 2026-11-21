"""Figure: Kerr spike (a = 0.8) on the analytic metric, two independent sampler seeds.

Reads the stationarity analyses of the two AthenaK runs (kerr_ana: seed 1, the run of note
v1; kerr2_ana: seed 2, note v2, JOURNAL N1 of this package), both made by the same analysis
script against the same reference grid (kerr_expected), and the seed comparison kerr_seeds
(compare_seeds.json: the pre-registered test of N1) and the diagnosis of the one particle
that crossed r_+ in seed 2 (kerr_plunger, plunger.json; JOURNAL N4). Panel (a): time-averaged count over the
expected count minus one in the five radial ranges, each seed with the error of a time
average over independent orbit draws, and the inverse-variance mean of the two. Panel (b):
running time average of count over expected in the three inner ranges, both seeds.
Numbers into fig_kerr_seeds_numbers.json (read by ledger.py).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_kerr_seeds"
INNER = ("0-4", "4-6", "6-10")


def main():
    out = C.out_dir("figures")
    A = C.load_json("kerr_ana", "kerr_main_analysis.json")
    B = C.load_json("kerr2_ana", "kerr_seed2_analysis.json")
    S = C.load_json("kerr_seeds", "compare_seeds.json")
    P = C.load_json("kerr_plunger", "plunger.json")
    # second reading (JOURNAL N4): the one particle that crossed r_+ is counted in 0-4 M at r = 0.4 M
    # after its plunge (no excision on the analytic metric); remove its post-plunge snapshots
    r2 = {k: dict(d=S["ranges"][k]["seed2"]["d"], sig=S["ranges"][k]["seed2"]["sig"]) for k in S["ranges"]}
    r2["0-4"]["d"] = P["tavg04_seed2_without_plunged"] - 1.0
    corr = {}
    for k in S["ranges"]:
        s1, d1 = S["ranges"][k]["seed1"]["sig"], S["ranges"][k]["seed1"]["d"]
        w1, w2 = 1 / s1 ** 2, 1 / r2[k]["sig"] ** 2
        m = (w1 * d1 + w2 * r2[k]["d"]) / (w1 + w2)
        corr[k] = dict(seed2_d=r2[k]["d"], seed2_z=r2[k]["d"] / r2[k]["sig"], mean_d=m,
                       mean_sig=(w1 + w2) ** -0.5)
    Z2c = sum(corr[k]["seed2_z"] for k in INNER)
    Zmc = sum(corr[k]["mean_d"] / corr[k]["mean_sig"] for k in INNER) / np.sqrt(3)
    keys = list(A["ranges"].keys())
    if keys != list(B["ranges"].keys()):
        raise SystemExit("the two analyses use different ranges")
    for k in keys:   # the comparison read these same analyses
        if abs(S["ranges"][k]["seed2"]["d"] - (B["ranges"][k]["time_avg_over_expected"] - 1)) > 1e-12:
            raise SystemExit(f"compare_seeds.json does not match the seed-2 analysis in {k}")
    nums = {"ranges": S["ranges"], "test": S["test"], "side": S["side"],
            "plunger": {k: P[k] for k in ("n_bad", "tavg04_seed2", "tavg04_seed2_without_plunged")}
            | {"particle": P["particles"][0] if P["particles"] else None},
            "without_plunged": {"ranges": corr, "Z2_inner_sum": Z2c, "two_seed_inner_combined_z": Zmc}}
    cz.use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.0, 1.3]})
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.18, top=0.95, wspace=0.28)
    x = np.arange(len(keys))
    for lab, R, col, dx in (("first sample", A, cz.PAL["blue"], -0.2), ("second sample", B, cz.PAL["red"], 0.0)):
        d = [100 * (R["ranges"][k]["time_avg_over_expected"] - 1) for k in keys]   # per cent from 1
        e = [100 * R["ranges"][k]["time_avg_sigma_rel"] for k in keys]
        a.errorbar(x + dx, d, yerr=e, fmt="o", ms=3.5, color=col, capsize=2, lw=1.0, label=lab)
    a.errorbar(x + 0.2, [100 * S["ranges"][k]["mean_d"] for k in keys],
               yerr=[100 * S["ranges"][k]["mean_sig"] for k in keys], fmt="s", ms=3.5, color="k",
               mfc="white", capsize=2, lw=1.0, label="mean of both")
    a.plot([0.08], [100 * corr["0-4"]["seed2_d"]], "o", ms=4.5, mfc="white", mec=cz.PAL["red"], mew=1.0,
           label="second, without the plunged particle")
    a.axhline(0, color="k", lw=0.8)
    a.set_xticks(x)
    a.set_xticklabels(keys)
    a.set_xlabel(r"range of $r/M$")
    a.set_ylabel(r"time average$/$expected $-1$ [per cent]", fontsize=8)
    a.legend(frameon=False, loc="lower right", fontsize=6.0)
    a.text(0.92, 0.92, "(a)", transform=a.transAxes)
    t = np.linspace(0.0, B["t_end"], B["nsnap"])
    n = np.arange(1, t.size + 1)
    for k, col in zip(INNER, (cz.PAL["blue"], cz.PAL["red"], cz.PAL["green"])):
        for R, ls, lw in ((A, "--", 0.9), (B, "-", 1.3)):
            ser = np.asarray(R["ranges"][k]["series"], float) / R["ranges"][k]["expected"]
            b.plot(t, np.cumsum(ser) / n, color=col, ls=ls, lw=lw,
                   label=rf"$r/M$ in {k}" if R is B else None)
    b.axhline(1, color="k", lw=0.8)
    b.set_ylim(0.85, 1.15)
    b.set_xlabel(r"$t/M$")
    b.set_ylabel("running mean / expected")
    b.legend(frameon=False, loc="upper right", fontsize=6.5, ncol=3)
    b.text(0.04, 0.06, "(b)  solid: second sample; dashed: first", transform=b.transAxes, fontsize=7)
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps(S["test"], indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
