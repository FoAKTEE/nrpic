"""Compare two sampler seeds of the Kerr spike stationarity test (note_v2, JOURNAL N1).

Reads the analysis files of spike/analyze_kerr.py for seed 1 and seed 2 (same DF, same
reference grid, same executable and input; only the sampler seed differs) and evaluates the
pre-registered test of JOURNAL N1:

  d_s   = time average / expected - 1 in each radial range, seed s
  sig_s = error of a time average over independent orbit draws (analyze_kerr's
          time_avg_sigma_rel)
  Z2    = z(0-4) + z(4-6) + z(6-10) of seed 2; H0 (no bias) holds if Z2 > -1.5
  two-seed mean (inverse-variance weights) and its error, the bound on a bias.

Writes compare_seeds.json and fig_kerr_seeds.{pdf,png} into --out.

usage: python3 compare_seeds.py --a <seed-1 analysis json> --b <seed-2 analysis json>
                                --out DIR [--labels "seed 1" "seed 2"]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "python"))
from nrpic import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

INNER = ["0-4", "4-6", "6-10"]


def per_range(an):
    out = {}
    for k, v in an["ranges"].items():
        out[k] = {"expected": v["expected"], "t0": v["t0"],
                  "d": v["time_avg_over_expected"] - 1.0, "sig": v["time_avg_sigma_rel"],
                  "z": v["time_avg_z"], "late_over_early": v["late_over_early"],
                  "t0_over_expected": v["t0"] / v["expected"],
                  "series": np.asarray(v["series"], float) / v["expected"]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels", nargs=2, default=["seed 1", "seed 2"])
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    A = json.load(open(args.a)); B = json.load(open(args.b))
    ra, rb = per_range(A), per_range(B)
    keys = list(ra.keys())
    res = {"inputs": {"a": args.a, "b": args.b}, "labels": args.labels, "ranges": {}}
    for k in keys:
        a, b = ra[k], rb[k]
        w = np.array([1 / a["sig"] ** 2, 1 / b["sig"] ** 2])
        m = float((w[0] * a["d"] + w[1] * b["d"]) / w.sum())
        sm = float(1 / np.sqrt(w.sum()))
        # difference of the two seeds over its error: both are draws of the same quantity
        dz = float((b["d"] - a["d"]) / np.hypot(a["sig"], b["sig"]))
        res["ranges"][k] = {
            "expected": a["expected"],
            "seed1": {kk: a[kk] for kk in ("t0", "d", "sig", "z", "late_over_early",
                                            "t0_over_expected")},
            "seed2": {kk: b[kk] for kk in ("t0", "d", "sig", "z", "late_over_early",
                                            "t0_over_expected")},
            "sig2_over_sig1": b["sig"] / a["sig"],
            "mean_d": m, "mean_sig": sm, "mean_z": m / sm, "seed_difference_z": dz}
    Z2 = float(sum(rb[k]["z"] for k in INNER))
    Z1 = float(sum(ra[k]["z"] for k in INNER))
    Zm = float(sum(res["ranges"][k]["mean_z"] for k in INNER) / np.sqrt(3))
    all_inner_low = all(rb[k]["z"] < -1 for k in INNER)
    res["test"] = {
        "Z1_inner_sum": Z1, "Z2_inner_sum": Z2,
        "H0_holds (Z2 > -1.5)": bool(Z2 > -1.5),
        "bias_indicated (Z2 <= -1.5)": bool(Z2 <= -1.5),
        "strong_bias (Z2 <= -3 or all inner z2 < -1)": bool(Z2 <= -3 or all_inner_low),
        "two_seed_inner_combined_z": Zm,
        "two_seed_bias_bound_2sigma_percent": {k: 100 * (abs(res["ranges"][k]["mean_d"])
                                                          + 2 * res["ranges"][k]["mean_sig"])
                                               for k in keys}}
    side = {}
    for lab, an in (("seed1", A), ("seed2", B)):
        side[lab] = {"N": an["N"], "nsnap": an["nsnap"], "t_end": an["t_end"],
                     "nonfinite_records": an["nonfinite_records"], "dof": an["dof"],
                     "chi2_t0": an["chi2_t0"], "chi2_median": an["chi2_median"],
                     "chi2_min": an["chi2_min"], "chi2_max": an["chi2_max"],
                     "band": an["band_1pm3sqrt(2/dof)"],
                     "dE/E_max": an["invariants"]["dE/E_median_p99_max"][2],
                     "dLz_max": an["invariants"]["dLz_median_p99_max"][2],
                     "dQ_max": an["invariants"]["dQ/max(Q,1)_median_p99_max"][2],
                     "min_r": an["inner"]["min_r_over_snapshots"],
                     "n_below_r_plus": an["inner"]["n_below_r_plus"],
                     "contrast": an["contrast_eq_over_pole_r<16"]}
    res["side"] = side
    json.dump(res, open(out / "compare_seeds.json", "w"), indent=1)

    # ---- figure ------------------------------------------------------------------------
    figstyle.use_style()
    P = figstyle.PAL
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0),
                            gridspec_kw={"width_ratios": [1.0, 1.35]})
    ax = axs[0]
    x = np.arange(len(keys))
    for j, (lab, r, c, dx) in enumerate(((args.labels[0], ra, P["blue"], -0.18),
                                         (args.labels[1], rb, P["red"], 0.0))):
        ax.errorbar(x + dx, [100 * r[k]["d"] for k in keys], yerr=[100 * r[k]["sig"] for k in keys],
                    fmt="o", color=c, ms=5, capsize=2, label=lab)
    ax.errorbar(x + 0.18, [100 * res["ranges"][k]["mean_d"] for k in keys],
                yerr=[100 * res["ranges"][k]["mean_sig"] for k in keys], fmt="s", color="k",
                mfc="white", ms=5, capsize=2, label="mean of both")
    ax.axhline(0, **figstyle.THIN)
    ax.set_xticks(x); ax.set_xticklabels(keys)
    ax.set_xlabel("radial range of $r$ ($M$)")
    ax.set_ylabel("time average / expected $-1$ (%)")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.text(0.03, 0.95, "(a)", transform=ax.transAxes, va="top")
    ax = axs[1]
    t = np.linspace(0.0, A["t_end"], A["nsnap"])
    n = np.arange(1, t.size + 1)
    for k, c in zip(INNER, (P["blue"], P["red"], P["green"])):
        ax.plot(t, np.cumsum(ra[k]["series"]) / n, color=c, lw=1.0, ls="--")
        ax.plot(t, np.cumsum(rb[k]["series"]) / n, color=c, lw=1.5, label=f"{k} $M$")
    ax.axhline(1, **figstyle.THIN)
    ax.set_xlabel("$t$ ($M$)")
    ax.set_ylabel("running mean of count / expected")
    ax.set_ylim(0.85, 1.15)
    ax.legend(loc="upper right", fontsize=7, frameon=False, ncol=3)
    ax.text(0.03, 0.95, "(b)", transform=ax.transAxes, va="top")
    ax.text(0.03, 0.06, f"solid: {args.labels[1]}; dashed: {args.labels[0]}",
            transform=ax.transAxes, fontsize=7)
    fig.tight_layout()
    figstyle.save(fig, str(out / "fig_kerr_seeds"))
    print(json.dumps(res["test"], indent=1))
    for k in keys:
        r = res["ranges"][k]
        print(f"{k:6s} d1 {100 * r['seed1']['d']:+6.2f} +- {100 * r['seed1']['sig']:.2f}  "
              f"d2 {100 * r['seed2']['d']:+6.2f} +- {100 * r['seed2']['sig']:.2f}  "
              f"mean {100 * r['mean_d']:+6.2f} +- {100 * r['mean_sig']:.2f}  "
              f"t0: {r['seed1']['t0_over_expected']:.3f} {r['seed2']['t0_over_expected']:.3f}")


if __name__ == "__main__":
    main()
