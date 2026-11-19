"""Recompute the numbers of brief lines 201, 208 and 214 from the numbers printed in the sources.

Work package s35 (kb brief check). Every input below is transcribed from a TeX source of the
knowledge-base store; the locator is given next to it (`<id>/<v>/src/<file>:<line>` under
/data/haiyangw/nrpic/kb-data/raw/arxiv). Nothing under kb-data is read, executed or imported by
this script: it only uses the transcribed numbers.

Checks
  1. arXiv:2608.13206, "a factor of about 94" fewer coarse-level steps (brief line 201):
     ratio of the two step counts printed in the paper.
  2. arXiv:2508.10070, abundance "about 19 times the earlier prediction" (brief line 208):
     ratio of beta/sigma^5 of the monochromatic case to the coefficient of arXiv:1609.01588.
  3. arXiv:2609.14218, dust "about twice" and particles "about an order of magnitude below" the
     earlier analytic estimate (brief line 214): the analytic criterion of the paper,
     mu > h(e, p) * 6 a^2 H^2 / k^2 with aH = k/sqrt(6), evaluated at e = 0.2, p = 0, against the
     dust bound (no horizon before the crash for mu <= 0.95) and the particle bracket (horizon
     for mu >= 0.05, none for mu <= 0.045) printed for e = 0.2.

Writes numbers.json and fig_numbers.{pdf,png} into $NRPIC_RUN_DIR (or the first argument).
Exit status 1 if a recomputed ratio falls outside the band preregistered in JOURNAL.md entry 3.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.special import ellipe  # noqa: E402  (argument: parameter m = k^2)

# ---- numbers transcribed from the sources -------------------------------------------------
# 2608.13206/v3/src/PRD.tex:402 -- mu = 0.825 to t/t_H ~ 266.8: 1092 coarse-level advances with
# the scaled driver, 102436 with the standard driver, "a reduction by a factor of approximately 94"
STEPS_SCALED, STEPS_STANDARD, QUOTED_94 = 1092, 102436, 94.0
# 2608.13206/v3/src/PRD.tex:402 -- dt/t_H: 2.60e-3 (standard cap) and 0.520 (scaled, end of run),
# "a factor of approximately 200"
DT_STANDARD, DT_SCALED_END, QUOTED_200 = 2.60e-3, 0.520, 200.0
# 2508.10070/v1/src/main.tex:657-659 -- beta ~ 1.08 sigma_h^5 (monochromatic), "19 times the
# result reported in" Harada et al. 2016; 1609.01588/v2/src/apj_nonsphericalpbh.tex:764 --
# beta_0 ~ 0.05556 sigma^5
COEF_YE, COEF_HARADA, QUOTED_19 = 1.08, 0.05556, 19.0
# 2609.14218/v1/src/MDPBH.tex:912-916 -- mu > hhat(e,p) * 6 a^2 H^2 / k^2,
#   hhat(e,p) = (15/pi) e / (1+3e+p)^2 * E( sqrt(1 - (e+p)^2/(4 e^2)) );
# MDPBH.tex:987, 1147 -- the comparison line uses aH = k/sqrt(6), i.e. the factor is 1.
# MDPBH.tex:1084-1086 -- e = 0.2: the dust calculation "breaks down before horizon formation for
#   mu <= 0.95"; MDPBH.tex:1101-1102 -- particles, e = 0.2: horizon for mu >= 0.05, none for
#   mu <= 0.045; MDPBH.tex:174, 177 -- "by a factor of 2", "by an order of magnitude".
E_CHECK, P_CHECK = 0.2, 0.0
DUST_NO_HORIZON_MAX = 0.95
PART_LO, PART_HI = 0.045, 0.05
QUOTED_DUST, QUOTED_PART = 2.0, 10.0
# The simulated ellipticities with p = 0 (MDPBH.tex:965), drawn on the analytic line
E_SIM = [0.01, 0.03, 0.05, 0.1, 0.15, 0.2, 0.25]

# ---- bands written in JOURNAL.md entry 3 before the run ------------------------------------
BANDS = {"steps_ratio": (90.0, 98.0), "dt_ratio": (190.0, 210.0),
         "abundance_ratio": (18.0, 21.0), "hhat_02": (0.40, 0.47),
         "dust_ratio_min": (1.8, 2.5), "particle_ratio_lo": (8.0, 11.5),
         "particle_ratio_hi": (8.0, 11.5)}


def hhat(e, p, convention="modulus"):
    """Analytic criterion of 2609.14218 (aH = k/sqrt 6). The argument of E is an eccentricity
    (modulus k), as for the circumference of an ellipse, C = 4 a E(k); scipy's ellipe takes
    m = k^2. The 'parameter' convention (m = the printed argument) is evaluated as a bracket."""
    k = math.sqrt(1.0 - (e + p) ** 2 / (4.0 * e ** 2))
    m = k * k if convention == "modulus" else k
    return 15.0 / math.pi * e / (1.0 + 3.0 * e + p) ** 2 * float(ellipe(m))


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)

    res = {}
    res["steps_ratio"] = STEPS_STANDARD / STEPS_SCALED
    res["dt_ratio"] = DT_SCALED_END / DT_STANDARD
    res["abundance_ratio"] = COEF_YE / COEF_HARADA
    h_mod = hhat(E_CHECK, P_CHECK, "modulus")
    h_par = hhat(E_CHECK, P_CHECK, "parameter")
    res["hhat_02"] = h_mod
    res["hhat_02_parameter_convention"] = h_par
    res["dust_ratio_min"] = DUST_NO_HORIZON_MAX / h_mod
    res["dust_ratio_min_parameter_convention"] = DUST_NO_HORIZON_MAX / h_par
    res["particle_ratio_lo"] = h_mod / PART_HI   # threshold at the upper end of the bracket
    res["particle_ratio_hi"] = h_mod / PART_LO   # threshold at the lower end
    res["particle_ratio_parameter_convention"] = [h_par / PART_HI, h_par / PART_LO]
    fails = [k for k, (lo, hi) in BANDS.items() if not (lo <= res[k] <= hi)]
    res["bands"] = BANDS
    res["outside_band"] = fails
    with open(os.path.join(out, "numbers.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    # ---- figure ----
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.6))
    ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.72])
    ax2 = fig.add_axes([0.66, 0.15, 0.31, 0.72])

    e_grid = np.linspace(0.005, 1.0 / 3.0, 300)
    h_grid = [hhat(e, 0.0) for e in e_grid]
    ax1.plot(e_grid, h_grid, color=fs.PAL["blue"], lw=1.4,
             label=r"analytic $\hat h(e,0)$ (Zel'dovich + hoop)")
    ax1.plot(E_SIM, [hhat(e, 0.0) for e in E_SIM], "o", ms=3.5, color=fs.PAL["blue"],
             mfc="white", mew=1.0)
    ax1.annotate("", xy=(E_CHECK, 1.6), xytext=(E_CHECK, DUST_NO_HORIZON_MAX),
                 arrowprops=dict(arrowstyle="->", color=fs.PAL["red"], lw=1.2))
    ax1.plot([E_CHECK], [DUST_NO_HORIZON_MAX], "v", color=fs.PAL["red"], ms=6,
             label=r"dust: no horizon before crash, $\mu\leq0.95$")
    ax1.fill_between([E_CHECK - 0.006, E_CHECK + 0.006], PART_LO, PART_HI,
                     color=fs.PAL["green"], alpha=0.9,
                     label=r"particles: threshold in $(0.045, 0.05]$")
    ax1.set_yscale("log")
    ax1.set_xlim(0.0, 0.34)
    ax1.set_ylim(0.01, 2.0)
    ax1.set_xlabel(r"ellipticity $e$ ($p=0$)")
    ax1.set_ylabel(r"initial amplitude $\mu$")
    ax1.text(E_CHECK + 0.012, 0.62, r"$\times%.1f$" % res["dust_ratio_min"],
             color=fs.PAL["red"], fontsize=8)
    ax1.text(E_CHECK + 0.012, 0.11, r"$\div%.1f$ to $\div%.1f$"
             % (res["particle_ratio_lo"], res["particle_ratio_hi"]),
             color="black", fontsize=8)
    ax1.legend(loc="lower right", fontsize=6.5, frameon=False)
    ax1.set_title("arXiv:2609.14218 at $e=0.2$", fontsize=8)

    items = [
        ("2608.13206 coarse steps", QUOTED_94, res["steps_ratio"], None),
        ("2608.13206 step size", QUOTED_200, res["dt_ratio"], None),
        ("2508.10070 abundance", QUOTED_19, res["abundance_ratio"], None),
        ("2609.14218 dust (min.)", QUOTED_DUST, res["dust_ratio_min"], None),
        ("2609.14218 particles", QUOTED_PART, 0.5 * (res["particle_ratio_lo"] + res["particle_ratio_hi"]),
         (res["particle_ratio_lo"], res["particle_ratio_hi"])),
    ]
    y = list(range(len(items)))[::-1]
    for yi, (name, q, c, rng) in zip(y, items):
        ax2.plot([q], [yi], "o", mfc="white", mec="black", ms=6, mew=1.0)
        if rng:
            ax2.plot(list(rng), [yi, yi], "-", color=fs.PAL["red"], lw=2.0)
        ax2.plot([c], [yi], "x", color=fs.PAL["red"], ms=6, mew=1.4)
    ax2.set_yticks(y)
    ax2.set_yticklabels([it[0] for it in items], fontsize=7)
    ax2.tick_params(axis="y", which="minor", left=False, right=False)
    ax2.set_xscale("log")
    ax2.set_xlim(1.0, 400.0)
    ax2.set_xlabel("ratio")
    ax2.plot([], [], "o", mfc="white", mec="black", label="as stated in the paper")
    ax2.plot([], [], "x", color=fs.PAL["red"], label="recomputed from body")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.45, 1.2), ncol=2, fontsize=6.5,
               frameon=False)
    fs.save(fig, os.path.join(out, "fig_numbers"))
    plt.close(fig)
    if fails:
        print("outside the preregistered band:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
