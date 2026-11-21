#!/usr/bin/env python3
"""Summary numbers for the C6 verdict of the heat package (post hoc arithmetic on results
of registered runs; no new fit of simulation data).

    summary_c6.py OUTDIR     ("-": the registered run's directory)

Reads (scratch/C-sidm/<run id>/...):
  C-20261119-161930-acd257b/T7.json   T7 theta 0.003, processor seeds only
  C-20261120-223001-eb81eb7/T7.json   T7 pooled, unweighted (theta 0.003); card seeds alone (0.1, 1)
  C-20261120-222954-b1a06ed/T7.json   T7 pooled, unweighted (theta 0.1, 1)
  C-20261120-223203-b38a7d7/cardcpu.json   N-weighted extrapolations (theta 0.003, 0.1, 1)
  C-20261120-222702-e2e02df/T7.json   T7 at eps 0.05 (card)
  C-20261120-223208-4ca3110/eps.json  expected standard errors at eps 0.05
  C-20261120-223321-3d088d4/t8.json   cell-size fits of T8 (card set)
  C-20261120-222423-519f12b/ce_kappa.json   relativistic Chapman-Enskog conductivity of
                                      isotropic hard spheres (verify_g1 V1a, own Monte Carlo
                                      of the collision brackets; Eckart frame)
  C-20261121-025837-8b5b9ee/seedpairs.json  seed pairs of the same executable
  ../results/design_C-20261119-144117-37b2328.json  design Monte Carlo (fit_rel_sd at
                                      eps 0.2, N 4e6), the alternative noise model of S-pairs
Writes summary_c6.json and summary_c6.png/pdf.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

SC = os.path.join(hl.MAIN, "scratch", "C-sidm")
HERE = os.path.dirname(os.path.abspath(__file__))


def load(run, fname):
    return json.load(open(os.path.join(SC, run, fname)))


def main():
    out = sys.argv[1]
    if out == "-":
        out = hl.outdir("summary_c6")
    os.makedirs(out, exist_ok=True)
    res = dict(inputs={})

    # --- relativistic Chapman-Enskog reference (V1a), in units of kappa_1 (nonrel, first)
    ce = load("C-20261120-222423-519f12b", "ce_kappa.json")
    k1 = ce["first_approx_exact"]
    ref = {}
    for r in ce["rel"]:
        o1, o4 = r["orders"][0], r["orders"][-1]
        ref[r["theta"]] = dict(order1=o1["kappa"] / k1, order1_se=o1["se"] / k1,
                               order4=o4["kappa"] / k1, order4_se=o4["se"] / k1)
    nr4 = ce["nonrel"][-1]
    ref["nonrel"] = dict(order4=nr4["kappa"] / k1, order4_se=nr4["se"] / k1)
    res["ce_reference"] = ref
    res["inputs"]["ce"] = "C-20261120-222423-519f12b"

    # --- measured extrapolations kappa/kappa_1 (k lambda -> 0) per theta
    cpu = load("C-20261119-161930-acd257b", "T7.json")["groups"]["T7_th0.003_e0.2"]
    pool3 = load("C-20261120-223001-eb81eb7", "T7.json")["groups"]
    pool13 = load("C-20261120-222954-b1a06ed", "T7.json")["groups"]
    cc = load("C-20261120-223203-b38a7d7", "cardcpu.json")["groups"]
    est = {
        0.003: dict(processor=(cpu["f0"], cpu["f0_se"], "C-20261119-161930-acd257b"),
                    pooled_unweighted=(pool3["T7_th0.003_e0.2"]["f0"],
                                       pool3["T7_th0.003_e0.2"]["f0_se"],
                                       "C-20261120-223001-eb81eb7"),
                    pooled_weighted=(cc["T7_th0.003_e0.2"]["extrapolation_weighted"]["f0"],
                                     cc["T7_th0.003_e0.2"]["extrapolation_weighted"]["f0_se"],
                                     "C-20261120-223203-b38a7d7")),
        0.1: dict(card_only=(pool3["T7_th0.1_e0.2"]["f0"], pool3["T7_th0.1_e0.2"]["f0_se"],
                             "C-20261120-223001-eb81eb7"),
                  pooled_unweighted=(pool13["T7_th0.1_e0.2"]["f0"],
                                     pool13["T7_th0.1_e0.2"]["f0_se"],
                                     "C-20261120-222954-b1a06ed"),
                  pooled_weighted=(cc["T7_th0.1_e0.2"]["extrapolation_weighted"]["f0"],
                                   cc["T7_th0.1_e0.2"]["extrapolation_weighted"]["f0_se"],
                                   "C-20261120-223203-b38a7d7")),
        1.0: dict(card_only=(pool3["T7_th1_e0.2"]["f0"], pool3["T7_th1_e0.2"]["f0_se"],
                             "C-20261120-223001-eb81eb7"),
                  pooled_unweighted=(pool13["T7_th1_e0.2"]["f0"],
                                     pool13["T7_th1_e0.2"]["f0_se"],
                                     "C-20261120-222954-b1a06ed"),
                  pooled_weighted=(cc["T7_th1_e0.2"]["extrapolation_weighted"]["f0"],
                                   cc["T7_th1_e0.2"]["extrapolation_weighted"]["f0_se"],
                                   "C-20261120-223203-b38a7d7")),
    }
    # chi^2-scaled se of the weighted extrapolations (1 dof each)
    for th, g in ((0.003, "T7_th0.003_e0.2"), (0.1, "T7_th0.1_e0.2"), (1.0, "T7_th1_e0.2")):
        e = cc[g]["extrapolation_weighted"]
        s = max(1.0, np.sqrt(e["chi2"] / max(e["dof"], 1)))
        est[th]["pooled_weighted_chi2scaled"] = (e["f0"], e["f0_se"] * s,
                                                 "C-20261120-223203-b38a7d7")
    comp = {}
    for th, d in est.items():
        R = ref[th]
        comp[str(th)] = {}
        for name, (f0, se, run) in d.items():
            diff = f0 - R["order4"]
            sed = float(np.hypot(se, R["order4_se"]))
            comp[str(th)][name] = dict(f0=f0, se=se, run=run, ce_order4=R["order4"],
                                       diff=diff, rel_diff=diff / R["order4"],
                                       z=diff / sed)
    res["T7_vs_CE"] = comp

    # --- cell-size bias at the T7 cell size (card T8 set, dx_frac fits)
    t8 = load("C-20261120-223321-3d088d4", "t8.json")
    card = [S for S in t8["sets"] if S["n"] > 1e6][0]
    fd = card["params"]["dx_frac"]["fit_dx"]
    f3 = est[0.003]
    corr = {}
    for form in ("quadratic", "linear"):
        b, bse = fd[form]["bias_at_T7_dx"], fd[form]["bias_at_T7_dx_se"]
        corr[form] = {}
        for name, (f0, se, run) in f3.items():
            fc = f0 * (1.0 - b)          # bias is relative (f/f0 - 1 at dx 0.245 lambda)
            sec = float(np.hypot(se, f0 * bse))
            corr[form][name] = dict(f0_dx0=fc, se=sec, run=run, bias=b, bias_se=bse,
                                    in_interval=bool(0.99 <= fc <= 1.06),
                                    diff_ce=fc - ref[0.003]["order4"],
                                    z_ce=(fc - ref[0.003]["order4"]) /
                                    float(np.hypot(sec, ref[0.003]["order4_se"])))
    res["T7_theta0.003_dx_corrected"] = corr
    res["inputs"]["t8"] = "C-20261120-223321-3d088d4"

    # --- eps 0.05 alone: two-point extrapolation with the expected standard errors
    T5 = load("C-20261120-222702-e2e02df", "T7.json")["groups"]["T7_th0.003_e0.05"]
    E = load("C-20261120-223208-4ca3110", "eps.json")
    se_exp = {r["k_lambda"]: r["f_A_se_expected"] for r in E["rows"]}
    rows = {r["k_lambda"]: r["f_S"][0] for r in T5["rows"]}
    x1, x2 = 0.2 ** 2, 0.4 ** 2
    a1, a2 = x2 / (x2 - x1), -x1 / (x2 - x1)
    f0 = a1 * rows[0.2] + a2 * rows[0.4]
    se0 = float(np.hypot(a1 * se_exp[0.2], a2 * se_exp[0.4]))
    res["T7_eps0.05_alone"] = dict(f_kl02=rows[0.2], f_kl04=rows[0.4], f0=f0,
                                   f0_se_expected=se0, f0_se_two_seeds=T5["f0_se"],
                                   z_to_lower_edge=(f0 - 0.99) / se0,
                                   runs=["C-20261120-222702-e2e02df",
                                         "C-20261120-223208-4ca3110"])

    # --- S-pairs with the design Monte Carlo noise (per theta, k lambda)
    design = json.load(open(os.path.join(HERE, "..", "results",
                                         "design_C-20261119-144117-37b2328.json")))
    sp = load("C-20261121-025837-8b5b9ee", "seedpairs.json")
    zz = []
    for q in sp["pairs"]:
        th = {"T7_th0.1_e0.2": "0.1", "T7_th1_e0.2": "1.0",
              "T7_th0.003_e0.2": "0.003"}[q["group"]]
        key = f"theta={th},kl={q['k_lambda']:g}"
        rs = design["T7"][key]["fit_rel_sd_eps0p2_N4e6"]
        s2d = rs ** 2 * 4e6
        sd = float(np.sqrt(2 * s2d / q["N"]))
        zz.append(dict(group=q["group"], k_lambda=q["k_lambda"], card=q["card"],
                       diff=q["diff"], z_measured_noise=q["z_pair"],
                       s2_design=s2d, z_design_noise=q["diff"] / sd))
    zd = np.array([q["z_design_noise"] for q in zz])
    s2d01 = design["T7"]["theta=0.003,kl=0.1"]["fit_rel_sd_eps0p2_N4e6"] ** 2 * 4e6
    s2m01 = [r for r in cc["T7_th0.003_e0.2"]["rows"] if r["k_lambda"] == 0.1][0]["s2_cpu"]
    res["seedpairs_design_noise"] = dict(pairs=zz, chi2=float(np.sum(zd ** 2)), n=len(zd),
                                         s2_design_th0003_kl01=s2d01,
                                         s2_measured_th0003_kl01_4seeds=s2m01,
                                         runs=["C-20261121-025837-8b5b9ee",
                                               "C-20261119-144117-37b2328",
                                               "C-20261120-223203-b38a7d7"])

    with open(os.path.join(out, "summary_c6.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    # --- figure: kappa/kappa_1 against theta, measured and the CE reference
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax = fig.add_axes([0.08, 0.16, 0.40, 0.72])
    th_ref = sorted(t for t in ref if t != "nonrel")
    # the reference exists only at these temperatures: markers, no interpolating line
    ax.plot(th_ref, [ref[t]["order1"] for t in th_ref], "_", ms=16, mew=1.5,
            color="grey", label="CE, first order (V1a)")
    ax.plot(th_ref, [ref[t]["order4"] for t in th_ref], "_", ms=16, mew=2.0,
            color="k", label="CE, order 4 (V1a)")
    marks = dict(processor=("s", fs.PAL["blue"]), card_only=("^", fs.PAL["orange"]),
                 pooled_unweighted=("o", fs.PAL["green"]),
                 pooled_weighted=("D", fs.PAL["red"]))
    labels = dict(processor="processor seeds", card_only="card seeds",
                  pooled_unweighted="pooled, unweighted", pooled_weighted=r"pooled, $\propto N$")
    used = set()
    for th, d in est.items():
        for j, name in enumerate(["processor", "card_only", "pooled_unweighted",
                                  "pooled_weighted"]):
            if name not in d:
                continue
            f0, se, _ = d[name]
            m, c = marks[name]
            ax.errorbar(th * (1 + 0.12 * (j - 1.5)), f0, yerr=se, fmt=m, color=c, ms=4,
                        capsize=2, label=None if name in used else labels[name])
            used.add(name)
    ax.set_xscale("log")
    ax.set_xlim(1.5e-3, 2.0)
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel(r"$\kappa/\kappa_1$ ($k\lambda\to 0$)")
    ax.set_title("T7: measured against relativistic Chapman-Enskog", fontsize=8.5)
    ax.set_ylim(0.925, 1.125)
    ax.legend(loc="upper left", fontsize=6.0, ncol=2)
    # right: theta = 0.003 in detail, with the cell-size correction of T8
    ax2 = fig.add_axes([0.58, 0.16, 0.40, 0.72])
    names = ["processor", "pooled_unweighted", "pooled_weighted"]
    for i, name in enumerate(names):
        f0, se, _ = f3[name]
        m, c = marks[name]
        ax2.errorbar(i, f0, yerr=se, fmt=m, color=c, ms=4.5, capsize=2)
        for k, (form, dx) in enumerate((("quadratic", 0.2), ("linear", 0.36))):
            q = corr[form][name]
            ax2.errorbar(i + dx, q["f0_dx0"], yerr=q["se"], fmt=m, color=c, ms=4.5,
                         capsize=2, mfc="none")
    ax2.axhspan(0.99, 1.06, color="grey", alpha=0.12, lw=0)
    ax2.axhline(ref[0.003]["order4"], **fs.REF_LINE)
    ax2.axhline(ref["nonrel"]["order4"], **fs.GUIDE)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(["processor", "pooled", r"pooled $\propto N$"])
    ax2.set_xlim(-0.4, 2.7)
    ax2.set_ylabel(r"$\kappa/\kappa_1$ at $\theta=0.003$")
    ax2.set_title(r"filled: $\Delta x=\lambda/4$; open: $\Delta x\to 0$ (quadratic, linear)",
                  fontsize=8)
    ax2.plot([], [], **fs.REF_LINE, label="CE order 4, relativistic")
    ax2.plot([], [], **fs.GUIDE, label="CE order 4, non-relativistic")
    ax2.legend(loc="lower left", fontsize=6.5)
    fs.save(fig, os.path.join(out, "summary_c6"))
    plt.close(fig)
    print(json.dumps({k: v for k, v in res.items() if k != "seedpairs_design_noise"},
                     indent=1, default=float))
    print("seedpairs with design noise: chi2 =", res["seedpairs_design_noise"]["chi2"],
          "for", res["seedpairs_design_noise"]["n"], "pairs")
    for q in zz:
        print(q["group"], q["k_lambda"], "card" if q["card"] else "cpu",
              round(q["z_measured_noise"], 2), round(q["z_design_noise"], 2))


if __name__ == "__main__":
    main()
