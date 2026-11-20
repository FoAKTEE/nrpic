#!/usr/bin/env python3
"""Item (d) of wave 3 (JOURNAL entries 16 and later): a second realisation of P256 (another
<job> rng_seed, same executable core/scalar-2 a58e95b) against the first
(E-20261115-172618-f948386, analysed in E-20261115-194633-9e04ed8).

    seed2_compare.py --old-res DIR --new-res DIR --old NAME --new NAME --out DIR

Each res directory holds what `ladder_analysis.py extract` and `judge` wrote for the run
(NAME.json, NAME.npz, NAME_judge.json, NAME_judge_spec.npz). Writes seed2.json and
fig_seed2.png/pdf: A1-A3 and the spectrum of both realisations side by side, the ratio of
the A2 maxima, per-|n| statistics of D_n, the constraint records.
"""
import argparse
import json
import os

import numpy as np


def load(d, name):
    j = json.load(open(os.path.join(d, f"{name}.json")))
    jj = json.load(open(os.path.join(d, f"{name}_judge.json")))
    z = np.load(os.path.join(d, f"{name}.npz"))
    s = np.load(os.path.join(d, f"{name}_judge_spec.npz"))
    return j, jj, z, s


def shell_stats(z):
    d = np.abs(z["rnr"][-1] / z["lin"][-1] - 1.0)
    sh = z["shell_of"]
    ns = z["kshell"].size
    mx = np.zeros(ns)
    np.maximum.at(mx, sh, d)
    cnt = np.bincount(sh, minlength=ns)
    med = np.array([np.median(d[sh == i]) if cnt[i] else np.nan for i in range(ns)])
    return d, mx, med


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-res", required=True)
    ap.add_argument("--new-res", required=True)
    ap.add_argument("--old", default="P256")
    ap.add_argument("--new", default="P256s2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}
    for tag, d, name in (("seed1", a.old_res, a.old), ("seed2", a.new_res, a.new)):
        j, jj, z, s = load(d, name)
        d_all, mx, med = shell_stats(z)
        k = np.sqrt(z["n2"].astype(float))
        con = z["con"]
        R[tag] = dict(name=name, seed=j.get("seed", 20261115), N_f=jj["N_f"], A1=j["A1_max"],
                      A2={k_: v for k_, v in jj["A2"].items() if k_ != "stencil_reference"},
                      A3=jj["A3"], spectrum=jj["spectrum"],
                      record_max_H=float(con[:, 3].max()), record_max_M=float(con[:, 6].max()),
                      D_median_k_le_8=float(np.median(d_all[k <= 8])),
                      D_median_k_le_32=float(np.median(d_all[k <= 32])),
                      D_p99_k_le_32=float(np.percentile(d_all[k <= 32], 99)),
                      _z=z, _s=s, _mx=mx, _med=med)
    alpha1, alpha2 = R["seed1"]["_z"]["alpha"], R["seed2"]["_z"]["alpha"]
    corr = float(np.abs(np.vdot(alpha1, alpha2)) / np.sqrt(np.vdot(alpha1, alpha1).real *
                                                           np.vdot(alpha2, alpha2).real))
    res = {t: {k: v for k, v in R[t].items() if not k.startswith("_")} for t in R}
    res["amplitude_correlation"] = corr
    res["A2_half_ratio_seed2_over_seed1"] = R["seed2"]["A2"]["max_D_half"] / R["seed1"]["A2"]["max_D_half"]
    res["A2_all_ratio_seed2_over_seed1"] = R["seed2"]["A2"]["max_D_all"] / R["seed1"]["A2"]["max_D_all"]
    res["D_median_ratio_k_le_32"] = R["seed2"]["D_median_k_le_32"] / R["seed1"]["D_median_k_le_32"]
    a3o, a3n = R["seed1"]["A3"], R["seed2"]["A3"]
    res["A3_drift_lin_equal"] = abs(a3o["max_abs_drift_lin"] - a3n["max_abs_drift_lin"])
    s2 = R["seed2"]
    res["verdicts_seed2"] = dict(
        A1=bool(max(s2["A1"]["phi"], s2["A1"]["Pi"], s2["A1"]["K"]) < 1e-4),
        A2=bool(s2["A2"]["pass_"]), A3=bool(s2["A3"].get("pass_", False)),
        A2_same_order=bool(0.25 <= res["A2_half_ratio_seed2_over_seed1"] <= 4.0))
    with open(os.path.join(a.out, "seed2.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    figure(R, a.out)


def figure(R, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    col = {"seed1": fs.PAL["red"], "seed2": fs.PAL["blue"]}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    for t, c in col.items():
        z, s = R[t]["_z"], R[t]["_s"]
        lab = f"{R[t]['name']} (seed {R[t]['seed']})"
        ax[0, 0].loglog(z["kshell"], R[t]["_mx"], "-", color=c, lw=1.0, label=lab + ", shell max")
        ax[0, 0].loglog(z["kshell"], R[t]["_med"], ":", color=c, lw=1.0, label=lab + ", shell median")
        nd = z["efolds_ref"]
        d = np.abs(z["rnr"] / z["lin"] - 1.0)
        sel = z["n2"] <= z["n2"].max() / 4.0
        hist = [np.nanmax(np.where((z["w"][i] > 0.5) & sel, d[i], np.nan))
                if ((z["w"][i] > 0.5) & sel).any() else np.nan for i in range(len(nd))]
        ax[0, 1].semilogy(nd, hist, "o-", color=c, ms=3, label=lab)
        ax[1, 0].plot(s["k"], s["d_nr"] / s["d_ens"], ".", color=c, ms=2, label=lab + ": NR / ensemble")
        ax[1, 0].plot(s["k"], s["d_nr"] / s["d_lin"], "-", color=c, lw=0.8)
        con = z["con"]
        ax[1, 1].semilogy(con[:, 2], con[:, 3], "-", color=c, label=r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$, " + t)
        ax[1, 1].semilogy(con[:, 2], con[:, 6], "--", color=c, label=r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$, " + t)
    s = R["seed1"]["_s"]
    fs.band(ax[1, 0], s["k"], 1 - 1 / np.sqrt(s["cnt"]), 1 + 1 / np.sqrt(s["cnt"]), "0.6")
    ax[0, 0].axhline(0.02, **fs.GUIDE)
    ax[0, 0].axvline(32, **fs.MASK_LINE)
    ax[0, 0].set_xlabel(r"$|n|$")
    ax[0, 0].set_ylabel(r"$D_n$ at $\mathcal{N}_f$")
    ax[0, 0].legend(fontsize=6, loc="upper left")
    ax[0, 1].axhline(0.02, **fs.GUIDE)
    ax[0, 1].set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    ax[0, 1].set_ylabel(r"max $D_n$, $|n|\leq32$, $W>1/2$")
    ax[0, 1].legend(fontsize=7, loc="lower right")
    ax[1, 0].set_xscale("log")
    ax[1, 0].set_ylim(0.0, 2.0)
    ax[1, 0].axhline(1.0, **fs.MASK_LINE)
    ax[1, 0].set_xlabel(r"$k/k_\sigma^*$")
    ax[1, 0].set_ylabel(r"shell spectrum ratio at $\mathcal{N}_f$")
    ax[1, 0].legend(fontsize=6, loc="upper left")
    ax[1, 1].set_xlabel(r"e-folds $-\ln\langle\chi\rangle/2$")
    ax[1, 1].set_ylabel("constraint record")
    ax[1, 1].legend(fontsize=6, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_seed2"))
    plt.close(fig)


if __name__ == "__main__":
    main()
