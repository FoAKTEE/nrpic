"""Figure: the probe-limit spike around a Kerr black hole, and its equilibrium in AthenaK.

Reads the Kerr reference of run kerr_ref (kerr_curves_ours.npz: our densities by the method
of Ferrer, da Rosa and Will on a radial grid; kerr_curves.json: their published curves,
digitized from the arXiv source by the reference run; kerr_reference.json: peaks and
deviations) and the stationarity analysis kerr_ana of the AthenaK geodesic run kerr_run
(kerr_main_series.npz, kerr_main_analysis.json). The unit conversion of the densities is
that of the reference script (spike/kerr_reference.py): constant f in units of f0 / 1e8
GeV cm^-3, the Hernquist-grown spike in units of Af GeV / 1e18 (spike/kerr_lib.py,
KerrHernquist with the published halo). Panel (a): constant distribution function, equator,
spins 0, 0.5, 0.8. Panel (b): spike grown from a Hernquist cusp, the same spins. Panel (c):
counts of the AthenaK run (spin 0.8) in five radial ranges over the count of the sampled
equilibrium, over 20000 M. Numbers to fig_kerr_numbers.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_kerr"
SPINS = (("0.0", "0", cz.PAL["blue"]), ("0.5", "0.5", cz.PAL["yellow"]), ("0.8", "0.8", cz.PAL["red"]))


def hern_scale():
    """Af * GeV cm^-3 per Msun pc^-3 / 1e18, as kerr_reference.py scales the Hernquist curves."""
    sys.path.insert(0, os.path.join(C.TRACK, "spike"))
    from kerr_lib import KerrHernquist  # noqa: E402
    from spike_lib import MSUN_PC3_TO_GEV_CM3  # noqa: E402
    return KerrHernquist(table=object()).Af * MSUN_PC3_TO_GEV_CM3 / 1e18


def main():
    out = C.out_dir("figures")
    z = np.load(C.run_file("kerr_ref", "kerr_curves_ours.npz"))
    dig = C.load_json("kerr_ref", "kerr_curves.json")
    ref = C.load_json("kerr_ref", "kerr_reference.json")
    ser = np.load(C.run_file("kerr_ana", "kerr_main_series.npz"))
    ana = C.load_json("kerr_ana", "kerr_main_analysis.json")
    sc_c = ref["f0_GeV_cm3"] / 1e8
    sc_h = hern_scale()
    cz.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.45))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.19, top=0.96, wspace=0.40)
    a, b, c = axs
    nums = {"scale_constf": sc_c, "scale_hern": sc_h, "constf": {}, "hern": {}}
    for ax, fam, figkey, sc in ((a, "constf", "fig_rho_a", sc_c), (b, "hern", "fig_rho_hern", sc_h)):
        for spin, lab, col in SPINS:
            k = f"{fam}_a{spin}_th1.5708"
            r, rho = z[k + "_r"], z[k + "_rho"] * sc
            ax.plot(r, rho, color=col, lw=1.4, label=rf"$a={lab}$")
            d = dig[figkey]["curves"][f"a={lab}"]
            xd, yd = np.array(d["x"]), np.array(d["y"])
            step = max(1, len(xd) // 14)
            ax.plot(xd[::step], yd[::step], "o", ms=2.6, mfc="none", mec=col, mew=0.8)
            dd = ref["digitized"][f"{figkey}:a={lab}"]
            nums[fam][f"a={lab}"] = dict(peak_ours=dd["peak_ours"], peak_published=dd["peak_digitized"],
                                         maxabs_rel_dev=dd["maxabs_rel_dev"],
                                         median_rel_dev=dd["median_rel_dev"], range=dd["range"],
                                         grid_peak=float(np.max(rho)))
        ax.set_xlim(0, 40)
        ax.set_xlabel(r"$r/Gm$ (equator)")
    a.plot([], [], "o", ms=2.6, mfc="none", mec="k", mew=0.8, label="published")
    a.set_ylim(0, 1.2)
    a.set_ylabel(r"$\rho\ [10^8\,{\rm GeV\,cm^{-3}}]$")
    a.legend(frameon=False, loc="upper right", fontsize=7, handlelength=1.5)
    a.text(0.05, 0.9, "(a)", transform=a.transAxes)
    b.set_ylim(0, 4.6)
    b.set_ylabel(r"$\rho\ [10^{18}\,{\rm GeV\,cm^{-3}}]$")
    b.text(0.05, 0.9, "(b)", transform=b.transAxes)

    t = ser["t"] / 1e3
    rng = ana["ranges"]
    cols = [cz.PAL["red"], cz.PAL["yellow"], cz.PAL["green"], cz.PAL["blue"], "k"]
    nums["stationarity"] = dict(N=ana["N"], t_end=ana["t_end"], nsnap=ana["nsnap"], dof=ana["dof"],
                                chi2_t0=ana["chi2_t0"], chi2_median=ana["chi2_median"],
                                chi2_min=ana["chi2_min"], chi2_max=ana["chi2_max"],
                                invariants=ana["invariants"], inner=ana["inner"],
                                contrast=ana["contrast_eq_over_pole_r<16"], ranges={})
    for (name, d), col in zip(rng.items(), cols):
        s = np.array(d["series"], float) / d["expected"]
        lo, hi = name.split("-")
        c.plot(t, s, color=col, lw=0.8, label=f"{lo}\u2013{hi}")
        sig = 1 / np.sqrt(d["expected"])
        c.fill_between([0, t[-1]], 1 - sig, 1 + sig, color=col, alpha=0.12, lw=0)
        nums["stationarity"]["ranges"][name] = {k: d[k] for k in (
            "expected", "late_over_early", "late_half_mean_over_expected", "time_avg_z",
            "trend_per_1e4M", "Lz_mean_ref", "Lz_mean_late_half", "z_min", "z_max")}
    c.set_xlim(0, t[-1])
    c.set_xticks([0, 5, 10, 15, 20])
    c.set_ylim(0.45, 1.3)
    c.set_xlabel(r"time $t\ [10^3 M]$")
    c.set_ylabel("count / equilibrium count")
    c.legend(frameon=False, loc="lower center", fontsize=6.5, ncol=3, handlelength=1.1,
             columnspacing=0.8, title=r"radial range [$Gm$]", title_fontsize=6.5)
    c.text(0.05, 0.9, "(c)", transform=c.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    tc = ref["text_claims"]
    nums["peak_ratios"] = {k: v for k, v in tc.items() if k != "order"}
    nums["a0_vs_wave1"] = ref["a0_vs_wave1"]
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps({k: nums[k] for k in ("constf", "hern")}, indent=1))
    st = nums["stationarity"]
    print(f"{STEM}: chi2 median {st['chi2_median']:.1f} for {st['dof']} dof; late/early",
          ", ".join(f"{v['late_over_early']:.3f}" for v in st["ranges"].values()))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
