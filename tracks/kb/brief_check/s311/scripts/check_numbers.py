"""Recompute the numbers behind brief lines 269 and 275 from numbers printed in the sources.

Work package s311 (kb brief check). Every input is transcribed from a TeX source of the
knowledge-base store; the locator is given next to it (`<id>/<v>/src/<file>:<line>` under
/data/haiyangw/nrpic/kb-data/raw/arxiv). Nothing under kb-data is read, executed or imported:
the script only uses the transcribed numbers. Constants [BACKGROUND]: GM_sun = 1.3271244e20
m^3 s^-2 (IAU 2015 Resolution B3, nominal), au = 1.495978707e11 m (IAU 2012 Resolution B2),
c exact (SI), Julian year 3.15576e7 s.

Checks (bands preregistered in JOURNAL.md entry 3)
  X1. Hills' rms ejection speed as reported by Yu and Tremaine (astro-ph/0309084 ms.tex:516-526):
      v' = 130 to 160 km/s in v_ej = v' (M/m*)^(1/6) (a_b/0.1 au * Msun/m*)^(-1/2); written as
      v_ej = k v_b q^(1/6) with v_b = sqrt(G m_b/a_b), m_b = 2 m*, q = M/m_b: k = v'/(2^(1/3) V0),
      V0 = sqrt(G Msun/0.1 au). Band for k: [0.7, 1.5] predicted, [0.5, 2] refutes.
  X2. Their quoted speeds: about 5e3 and 0.9e3 km/s for M = 3.5e6 Msun, m* = 1 Msun,
      a_b = 0.01 and 0.3 au (ms.tex:549-555), recomputed with v' = 130 and 160; band 0.8-1.3.
  X3. arXiv:2404.16270: r_t = 101.3 r_g for M = 1e6 Msun, m_b = 1 Msun, a_0 = 0.01 au
      (article.tex:168-176) and beta_max = 25.3 (article.tex:209-212) from r_t/r_g =
      (a_0/r_gb) q^(-2/3) and beta_max = r_t/(4 r_g); bands 0.1 and 0.3 per cent.
  X4. Peters as quoted by arXiv:1805.09593 (revised_version.tex:128, 202-205):
      tau = (5/256) c^5 a^4/(G^3 m1 m2 m); equal masses give 5/64 (exact); 6.0e3 Gyr for
      m = 60 Msun, a = 1 au (band 2 per cent); the brief's "about 6x10^3 GM/c^3" for
      a_b = 30 r_gb, q = 10 against (5/64) 30^4 / q.
Writes numbers.json and fig_numbers.{pdf,png} into $NRPIC_RUN_DIR (or the first argument).
Exit status 1 if a recomputed number falls outside its band.
"""
import json
import math
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GMSUN = 1.3271244e20        # m^3 s^-2
C = 299792458.0             # m/s
AU = 1.495978707e11         # m
YR = 3.15576e7              # s
RG_SUN = GMSUN / C**2       # m
TG_SUN = GMSUN / C**3       # s


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    res, fails = {}, []

    # X1: prefactor k of v_ej = k v_b q^(1/6) from Hills' v' (Yu and Tremaine)
    v0 = math.sqrt(GMSUN / (0.1 * AU)) / 1e3          # km/s
    vprime = (130.0, 160.0)                            # ms.tex:522-526
    k = [vp / (2 ** (1.0 / 3.0) * v0) for vp in vprime]
    res["X1"] = {"V0_kms": v0, "vprime_kms": vprime, "k": k, "band_pred": [0.7, 1.5],
                 "band_refute": [0.5, 2.0]}
    if not all(0.5 <= x <= 2.0 for x in k):
        fails.append("X1 k outside [0.5, 2]: %s" % k)

    # X2: Yu and Tremaine's quoted speeds
    M, ms = 3.5e6, 1.0
    x2 = {}
    for ab, quoted in ((0.01, 5.0e3), (0.3, 0.9e3)):   # ms.tex:549-555
        v = [vp * (M / ms) ** (1 / 6.0) * math.sqrt(0.1 / ab * ms) for vp in vprime]
        ratio = [x / quoted for x in v]
        x2["a_b=%g au" % ab] = {"recomputed_kms": v, "quoted_kms": quoted, "ratio": ratio}
        if not (min(ratio) <= 1.3 and max(ratio) >= 0.8):
            fails.append("X2 a_b=%g: ratio %s does not overlap [0.8, 1.3]" % (ab, ratio))
    res["X2"] = x2

    # X3: 2404.16270 tidal radius and maximal impact parameter
    Mbh, mb, a0 = 1e6, 1.0, 0.01 * AU
    rt_over_rg = (a0 / (mb * RG_SUN)) * (Mbh / mb) ** (-2.0 / 3.0)
    beta_max = rt_over_rg / 4.0
    r_rt, r_b = rt_over_rg / 101.3, beta_max / 25.3
    res["X3"] = {"rt_over_rg": rt_over_rg, "quoted_rt": 101.3, "ratio_rt": r_rt,
                 "beta_max": beta_max, "quoted_beta_max": 25.3, "ratio_beta": r_b}
    if abs(r_rt - 1) > 1e-3:
        fails.append("X3 r_t ratio %.5f" % r_rt)
    if abs(r_b - 1) > 3e-3:
        fails.append("X3 beta_max ratio %.5f" % r_b)

    # X4: Peters merger time as quoted by 1805.09593
    coef = Fraction(5, 256) * Fraction(1, 1) / (Fraction(1, 2) * Fraction(1, 2) * 1)
    m = 60.0
    tau = float(coef) * (AU / (m * RG_SUN)) ** 4 * m * TG_SUN / YR / 1e9   # Gyr
    r_tau = tau / 6.0e3
    peters_brief = float(coef) * 30.0 ** 4 / 10.0                           # GM/c^3
    res["X4"] = {"coef_equal_mass": str(coef), "tau_Gyr_60Msun_1au": tau, "quoted_Gyr": 6.0e3,
                 "ratio": r_tau, "brief_ab30_q10_GMc3": peters_brief, "brief_value": 6.0e3,
                 "ratio_brief": peters_brief / 6.0e3}
    if coef != Fraction(5, 64):
        fails.append("X4 coefficient %s" % coef)
    if abs(r_tau - 1) > 0.02:
        fails.append("X4 tau ratio %.4f" % r_tau)

    res["fails"] = fails
    with open(os.path.join(out, "numbers.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    # figure: left, stated against recomputed; right, v_ej / v_b against q
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.6))
    ax1 = fig.add_axes([0.30, 0.16, 0.30, 0.74])
    ax2 = fig.add_axes([0.72, 0.16, 0.26, 0.74])
    items = [
        ("2404.16270  r_t = 101.3 r_g", [r_rt]),
        ("2404.16270  beta_max = 25.3", [r_b]),
        ("1805.09593  tau = 6.0e3 Gyr", [r_tau]),
        ("brief l.275  6e3 GM/c^3", [peters_brief / 6.0e3]),
        ("0309084  5e3 km/s (0.01 au)", x2["a_b=0.01 au"]["ratio"]),
        ("0309084  0.9e3 km/s (0.3 au)", x2["a_b=0.3 au"]["ratio"]),
    ]
    y = list(range(len(items)))[::-1]
    for yy, (lab, vals) in zip(y, items):
        if len(vals) == 1:
            ax1.plot(vals[0], yy, "o", color=fs.PAL["blue"], ms=6)
        else:
            ax1.plot(vals, [yy, yy], "-", color=fs.PAL["red"], lw=3, solid_capstyle="butt")
    ax1.axvline(1.0, **fs.GUIDE)
    ax1.set_yticks(y)
    ax1.set_yticklabels([it[0] for it in items])
    ax1.tick_params(axis="y", which="minor", left=False, right=False)
    ax1.set_xlim(0.7, 1.4)
    ax1.set_xlabel("recomputed / stated")
    ax1.set_title("numbers at the sources", fontsize=10)

    q = [10 ** (i / 20.0) for i in range(0, 141)]          # 1 to 1e7
    ax2.plot(q, [x ** (1 / 6.0) for x in q], color=fs.PAL["blue"],
             label="0911.1136: k = 1")
    ax2.fill_between(q, [k[0] * x ** (1 / 6.0) for x in q], [k[1] * x ** (1 / 6.0) for x in q],
                     color=fs.PAL["red"], alpha=0.3, lw=0,
                     label="Hills via 0309084: k = %.2f-%.2f" % (k[0], k[1]))
    ax2.axvline(10.0, **fs.MASK_LINE)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("q = M / m_b")
    ax2.set_ylabel("v_ej / v_b")
    ax2.set_title("v_ej = k v_b q^(1/6)", fontsize=10)
    ax2.legend(loc="upper left", fontsize=7, frameon=False)
    fs.save(fig, os.path.join(out, "fig_numbers"))
    plt.close(fig)
    if fails:
        print("FAIL:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
