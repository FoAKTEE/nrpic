"""Figure: the probe-limit density spike around a Schwarzschild black hole.

Reads the semi-analytic reference of run spike_ref (reference_curves.npz, reference.json)
and the stationarity analysis of the AthenaK geodesic run (spike_ana, analysis.json).
Panel (a): adiabatic spike for a constant distribution function, relativistic against the
Newtonian (Gondolo-Silk) profile cut at 8 Gm and at 4 Gm. Panel (b): spike grown from a
Hernquist cusp for a black hole of 4e6 solar masses, canonical-action and Sadeghian et al.
forms, against the Gondolo-Silk form and the initial cusp. Panel (c): particle counts of
the AthenaK run in four radial shells against the count of the sampled equilibrium, over
20000 M. Numbers to fig_spike_numbers.json.
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

STEM = "fig_spike"


def main():
    out = C.out_dir("figures")
    z = np.load(C.run_file("spike_ref", "reference_curves.npz"))
    ref = C.load_json("spike_ref", "reference.json")
    ana = C.load_json("spike_ana", "analysis.json")
    cz.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.45))
    fig.subplots_adjust(left=0.08, right=0.975, bottom=0.19, top=0.96, wspace=0.42)
    a, b, c = axs

    a.plot(z["r1"], z["rel"], color=cz.PAL["blue"], label="relativistic")
    a.plot(z["r1"], z["gs8"], color="k", ls="--", lw=1.2, label=r"Newtonian, $8Gm$")
    a.plot(z["r1"], z["gs4"], color=cz.PAL["red"], ls=":", lw=1.4, label=r"Newtonian, $4Gm$")
    a.set_xscale("log")
    a.set_xlim(3.5, 100)
    a.set_ylim(0, 1.45)
    a.set_yticks([0, 0.5, 1.0])
    a.set_xlabel(r"$r/Gm$")
    a.set_ylabel(r"$\rho\ [10^8\,{\rm GeV\,cm^{-3}}]$")
    a.legend(frameon=False, loc="upper right", fontsize=7, handlelength=1.6)
    a.text(0.05, 0.9, "(a)", transform=a.transAxes)

    k = "m4e+06"
    b.loglog(z[k + "_r"], z[k + "_can"], color=cz.PAL["blue"], label="relativistic")
    b.loglog(z[k + "_r"], z[k + "_sfw"], color=cz.PAL["yellow"], ls="-.", lw=1.2,
             label="SFW form")
    b.loglog(z[k + "_r"], z[k + "_gs"], color="k", ls="--", lw=1.2, label="Newtonian")
    b.loglog(z[k + "_r"], z[k + "_hern"], color="grey", lw=1.0, label="initial cusp")
    b.set_xlim(3.5, 2e3)
    b.set_ylim(1e9, 1e19)
    b.set_xlabel(r"$r/Gm$")
    b.set_ylabel(r"$\rho\ [{\rm GeV\,cm^{-3}}]$")
    b.legend(frameon=False, loc="lower right", fontsize=7, handlelength=1.6)
    b.text(0.86, 0.9, "(b)", transform=b.transAxes)
    b.set_xticks([10, 100, 1000])

    st = ana["stationarity"]
    nsnap = ana["nsnap"]
    t = np.linspace(0.0, ana["t_end"], nsnap)
    cols = [cz.PAL["red"], cz.PAL["yellow"], cz.PAL["green"], cz.PAL["blue"]]
    nums = {"chi2_median_per_dof": st["chi2_median"] / st["dof"], "dof": st["dof"],
            "chi2_max_per_dof": st["chi2_max"] / st["dof"], "n_particles": ana["n_species0"],
            "t_end": ana["t_end"], "invariants": ana["invariants_species0"],
            "late_half_mean_over_expected": {}}
    for (rng, d), col in zip(st["inner_ranges"].items(), cols):
        ser = np.array(d["series"], float) / d["expected"]
        c.plot(t / 1e3, ser, color=col, lw=0.9, label=rf"${rng.replace('-', '-')}\,Gm$")
        sig = 1 / np.sqrt(d["expected"])
        c.fill_between([0, t[-1] / 1e3], 1 - sig, 1 + sig, color=col, alpha=0.12, lw=0)
        nums["late_half_mean_over_expected"][rng] = d["late_half_mean_over_expected"]
    c.set_xlim(0, t[-1] / 1e3)
    c.set_xticks([0, 5, 10, 15, 20])
    c.set_ylim(0.6, 1.25)
    c.set_xlabel(r"time $t\ [10^3 M]$")
    c.set_ylabel("count / equilibrium count")
    c.legend(frameon=False, loc="lower center", fontsize=7, ncol=2, handlelength=1.2, columnspacing=0.8)
    c.text(0.05, 0.9, "(c)", transform=c.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    cf = ref["constf"]
    nums.update(peak_rel=cf["peak_rel"], peak_rel_sfw_fig1=cf["peak_rel_digitized_sfw_fig1"],
                ratio_peak_rel_over_gs8=cf["ratio_peak_rel_over_gs8"],
                excess_peak_gs4_over_rel=cf["excess_peak_gs4_over_rel"],
                dev_vs_sfw_fig1_rel=cf["dev_vs_sfw_fig1_rel_8.5-95Gm_maxabs"],
                dev_vs_fdrw_rho_a=cf["dev_vs_fdrw_rho_a_5-39Gm_maxabs"],
                zero_rel_Gm=cf["zero_rel_Gm"])
    h4 = ref["hernquist"]["m4e+06"]
    nums["hernquist_m4e6"] = dict(peak_canonical=h4["peak_canonical"],
                                  peak_fdrw_digitized=h4["peak_fdrw_digitized"],
                                  dev_can_vs_fdrw=h4["dev_can_vs_fdrw_fig_rho_hern_5-39Gm"],
                                  dev_sfw_vs_fdrw=h4["dev_sfw_vs_fdrw_fig_rho_hern_5-39Gm"],
                                  peak_ratio_can_over_gs=h4["peak_ratio_can_over_gs"])
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps(nums, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
