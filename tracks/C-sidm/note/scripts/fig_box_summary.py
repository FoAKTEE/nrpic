"""Figure: the collision operator in the periodic box, released operator and the operator
with the pair energy taken at each particle's metric (gate G1).

(a) collision rate: summed pair probabilities per step over the Moller-averaged rate of the
    sample, 16 runs per operator (four temperatures, with and without sub-cycling, two
    seeds); (b) largest change of the total energy in one step over the sum of M W, with
    the bound of the test; (c) the same rate in a static curved metric (lapse 0.8, conformal
    factor 1.1) and in its flat twin.
Reads runs t2rel, t2c2 and t12 (common.RUNS); every file is checked against its run's
sha256sums.txt.
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

STEM = "fig_box_summary"
THETAS = (0.001, 0.1, 1.0, 10.0)


def t2_rows(key, name):
    d = cm.load_json(key, name)
    rows = []
    for k, r in d["runs"].items():
        if "ratio_b" not in r:
            continue
        rows.append(dict(name=k, theta=r["theta_nominal"], sub="_sub_" in k,
                         seed=int(k.rsplit("_s", 1)[1]), ratio=r["ratio_b"],
                         se=r["sumP_per_step_se"] / r["expected_per_step"], z=r["T2b_z"],
                         relE=r["T1_max_relE"], over=r["T1_max_relE_over_bound"],
                         n_tested=r["n_tested"], coll=r["collisions"], sumP=r["sum_P"]))
    return d, sorted(rows, key=lambda r: r["name"])


def main():
    out = cm.out_dir("figures")
    drel, rel = t2_rows("t2rel", "t1t2_cpu.json")
    dc2, c2 = t2_rows("t2c2", "t1t2_c2particle.json")
    t12 = cm.load_json("t12", "t12_cpu.json")
    assert [r["name"] for r in rel] == [r["name"] for r in c2]

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.45))
    axa = fig.add_axes([0.085, 0.19, 0.255, 0.70])
    axb = fig.add_axes([0.455, 0.19, 0.22, 0.70])
    axc = fig.add_axes([0.765, 0.19, 0.215, 0.70])
    col = {False: cz.PAL["blue"], True: cz.PAL["red"]}

    # (a) rate
    for rows, filled, lab in ((rel, True, "released"), (c2, False, "energy at each particle")):
        for sub in (False, True):
            rr = [r for r in rows if r["sub"] == sub]
            x = np.array([r["theta"] for r in rr]) * (1.18 if sub else 1 / 1.18) \
                * np.array([1.06 if r["seed"] == 2 else 1 / 1.06 for r in rr])
            y = np.array([(r["ratio"] - 1) * 1e4 for r in rr])
            e = np.array([2 * r["se"] * 1e4 for r in rr])
            kw = dict(ms=4.2 if filled else 6.5, mew=0.9, ls="none",
                      mfc=col[sub] if filled else "none", mec=col[sub] if filled else "k")
            if filled:
                axa.errorbar(x, y, yerr=e, fmt="o", color=col[sub], elinewidth=0.8, capsize=0,
                             **kw, label=("sub-cycled" if sub else "one sub-step"))
            else:
                axa.plot(x, y, "o", **kw, label=(lab if sub else None))
    axa.axhline(0, color="k", lw=0.6)
    axa.set_xscale("log")
    axa.set_xlim(4e-4, 30)
    axa.set_ylim(-3.2, 3.2)
    axa.set_xlabel(r"temperature $\theta$")
    axa.set_ylabel(r"rate / reference $-\,1$  ($10^{-4}$)")
    axa.legend(frameon=False, loc="lower left", fontsize=6.8, handlelength=1.0, ncol=1,
               labelspacing=0.2)
    axa.text(0.04, 0.92, "(a)", transform=axa.transAxes, fontsize=8.5)

    # (b) energy per step
    bound = np.array([r["relE"] / r["over"] for r in rel])
    for rows, filled in ((rel, True), (c2, False)):
        for sub in (False, True):
            rr = [r for r in rows if r["sub"] == sub]
            x = np.array([r["theta"] for r in rr]) * (1.18 if sub else 1 / 1.18) \
                * np.array([1.06 if r["seed"] == 2 else 1 / 1.06 for r in rr])
            y = np.array([r["relE"] for r in rr])
            axb.plot(x, y, "o", ls="none", ms=4.2 if filled else 6.5, mew=0.9,
                     mfc=col[sub] if filled else "none", mec=col[sub] if filled else "k")
    axb.axhline(float(np.median(bound)), **cz.GUIDE)
    axb.text(1.5e-2, float(np.median(bound)) / 30.0, "bound of the test", fontsize=7)
    axb.set_xscale("log")
    axb.set_yscale("log")
    axb.set_xlim(4e-4, 30)
    axb.set_ylim(1e-23, 1e-10)
    axb.set_yticks([1e-22, 1e-18, 1e-14, 1e-10])
    axb.set_xlabel(r"temperature $\theta$")
    axb.set_ylabel(r"largest $|\Delta E|/\sum MW$ in a step")
    axb.text(0.04, 0.92, "(b)", transform=axb.transAxes, fontsize=8.5)

    # (c) static curved metric and its flat twin
    kinds = (("curved", cz.PAL["green"], "curved"), ("flat", "k", "flat twin"))
    for j, (th, s) in enumerate(((0.1, 1), (0.1, 2), (1.0, 1), (1.0, 2))):
        for i, (kind, c, lab) in enumerate(kinds):
            r = t12["runs"][f"T12_th{th}_{kind}_s{s}"]
            y = (r["ratio"] - 1) * 1e4
            e = 2 * r["sumP_per_step_se"] / r["expected_per_step"] * 1e4
            axc.errorbar([j + (0.14 if i else -0.14)], [y], yerr=[e], fmt="o" if i == 0 else "s",
                         ms=4.2, mfc=c if i == 0 else "none", mec=c, color=c, elinewidth=0.8,
                         label=lab if j == 0 else None)
    axc.axhline(0, color="k", lw=0.6)
    axc.set_xticks(range(4))
    axc.set_xticklabels([r"0.1,1", r"0.1,2", r"1,1", r"1,2"], fontsize=7)
    axc.set_xlim(-0.6, 3.6)
    axc.set_ylim(-3.2, 3.2)
    axc.set_xlabel(r"$\theta$, seed")
    axc.set_ylabel(r"rate / reference $-\,1$  ($10^{-4}$)")
    axc.legend(frameon=False, loc="lower left", fontsize=6.8, handlelength=1.0)
    axc.text(0.04, 0.92, "(c)", transform=axc.transAxes, fontsize=8.5)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    # numbers for the journal and the ledger
    for tag, rows in (("released", rel), ("particle", c2)):
        print(f"{STEM}: {tag}: T2(b) ratio {min(r['ratio'] for r in rows):.6f}.."
              f"{max(r['ratio'] for r in rows):.6f}, z {min(r['z'] for r in rows):+.2f}.."
              f"{max(r['z'] for r in rows):+.2f}; T1 max over bound "
              f"{max(r['over'] for r in rows):.3e}")
    dr = max(abs(a["ratio"] - b["ratio"]) / a["ratio"] for a, b in zip(rel, c2))
    same = all(a["n_tested"] == b["n_tested"] and a["coll"] == b["coll"] for a, b in zip(rel, c2))
    print(f"{STEM}: release vs particle: largest relative ratio difference {dr:.2e}; "
          f"tested pairs and collisions equal in all runs: {same}; paired flag "
          f"{dc2.get('paired_counts_identical_all')}")
    tw = t12["twins"]
    print(f"{STEM}: T12 twin ratios " + ", ".join(f"{v['rate_ratio']:.7f}" for v in tw.values())
          + f" (expected {list(tw.values())[0]['expected']:.7f}); curved analytic ratio "
          + ", ".join(f"{t12['runs'][k]['ratio']:.7f}" for k in t12['runs'] if '_curved_' in k)
          + "; |z| <= " + f"{max(abs(t12['runs'][k]['z_rate']) for k in t12['runs']):.2f}")


if __name__ == "__main__":
    main()
