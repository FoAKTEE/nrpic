"""Figure: the geodesic baseline in the set-up of arXiv:2404.16270, against Newton.

Reads s1_summary.json of the geodesic_binary analysis run F-hills-20261115-142554-c10b371
(scan S1: 400 binary phases at each of 100 penetration factors beta = r_t/r_p between 0.1
and 10; binary of total mass 1e-6 M, coplanar prograde and retrograde; Newtonian point mass
and HRNA, black hole fixed). Checks the plotted curves against the values the run printed
at beta = 3, 5, 8, 10. Writes fig_geodesic.{pdf,png} and the numbers.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_geodesic"
BLUE, RED = cz.PAL["blue"], cz.PAL["red"]


def main():
    out = C.out_dir("figures")
    S = C.load_json("s1_an", "s1_summary.json")
    beta = np.array(S["betas"])
    chk = S["checks"]
    for b in (3, 5, 8, 10):
        i = int(np.argmin(np.abs(beta - b)))
        for k in ("pro_newton", "retro_newton", "pro_hrna", "retro_hrna"):
            C.close(S[k]["sf"][i], chk[f"sf_beta{b}"][k], 1e-12, f"sf {k} beta {b}")
            C.close(S[k]["v_mean"][i], chk[f"vmean_kms_beta{b}"][k], 1e-9, f"v {k} beta {b}")
    cz.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(3.4, 4.1), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.96, bottom=0.11, top=0.98, hspace=0.07)
    for k, col, ls, lab in (("pro_newton", BLUE, "-", "Newton, prograde"),
                            ("retro_newton", BLUE, "--", "Newton, retrograde"),
                            ("pro_hrna", RED, "-", "geodesic, prograde"),
                            ("retro_hrna", RED, "--", "geodesic, retrograde")):
        axs[0].plot(beta, S[k]["sf"], color=col, ls=ls, lw=1.3, label=lab)
        v = np.array(S[k]["v_mean"], float)
        axs[1].plot(beta, v / 1e3, color=col, ls=ls, lw=1.3)
    axs[0].set_ylabel("separated fraction")
    axs[0].set_ylim(-0.02, 1.05)
    axs[0].legend(frameon=False, loc="lower right", fontsize=7)
    axs[1].set_ylabel(r"mean $v_\infty$ $[10^3\,{\rm km\,s^{-1}}]$")
    axs[1].set_xlabel(r"penetration factor $\beta=r_t/r_p$")
    axs[1].set_xlim(0, 10)
    nums = {"run": C.RUNS["s1_an"], "n_phases": S["n_phases"], "beta_range": [beta[0], beta[-1]],
            "checks": {k: chk[k] for k in (
                "P1_retro_onset_newton", "P1_retro_onset_hrna", "sf_beta3", "sf_beta5",
                "sf_beta8", "sf_beta10", "vmean_kms_beta5", "digitized_sf_max_abs_dev_pro_hrna",
                "digitized_sf_max_abs_dev_retro_hrna", "digitized_sf_max_abs_dev_pro_newton",
                "digitized_sf_max_abs_dev_retro_newton", "digitized_vmean_max_rel_dev_pro_hrna",
                "digitized_vmean_max_rel_dev_pro_newton", "digitized_vmean_max_rel_dev_retro_hrna",
                "digitized_vmean_max_rel_dev_retro_newton", "alpha_bound_max_beta10",
                "runs_total")}}
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
