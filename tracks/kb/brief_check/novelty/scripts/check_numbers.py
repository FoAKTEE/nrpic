"""Number checks of work package "novelty" (brief lines 410 and 400).

1. Line 410: horizon mass at neutrino decoupling and the neutrino share of the radiation.
   M_H = (4 pi / 3) rho H^-3 with rho = (pi^2 / 30) g_* T^4 and H^2 = 8 pi G rho / 3 (radiation
   era), for T from 0.1 to 10 MeV and g_* = 10.75 (photons, e+e-, three neutrino species;
   2303.07980 PBHs_QCD.tex:357 uses g_nu/g_tot = 5.25/10.75), compared with the scalings printed
   in three papers of the knowledge base:
     1607.00612 paper2.tex:207-218  M_BH = M_H / 3^(3/2) = 40 (g_*/10)^(-1/2) (T / 27 MeV)^(-2) M_sun
     2006.16182 main_journal.tex:955 m_PBH ~ 30 M_sun (T / 40 MeV)^(-2)          ("~ m_P^2 t")
     2109.04896 PBH_formation.tex:249 M ~ 1e5 (1 MeV / T)^2 M_sun                  ("H^-1 M_Pl^2")
   Neutrino share of the radiation energy density: before e+e- annihilation 5.25/10.75
   (2303.07980 PBHs_QCD.tex:357); after it rho_nu/rho_gamma = (7/8)(4/11)^(4/3) N_eff with
   N_eff^SM = 3.045 (2006.16182 main_journal.tex:1046-1048).
2. Line 400: what the vacuum black-hole lattice of 1903.01490 already bounds. Horizon masses
   constant to 0.1 per cent (spinning_BH_v2_CT.tex:654-657) while lengths grow by about e^2
   (:643-644; scale factor a = V^(1/3), :714) give |k| <= ln(1.001) / ln(e^2) for M ~ a^k,
   against k = 3.11 (+1.19, -1.33, 90 per cent) of 2302.07878 (paper_couple_rev.tex:130).
Physical constants: CODATA 2018 / IAU 2015 nominal values (standard, typed in below).
Writes numbers.json and fig_numbers.{pdf,png} into $NRPIC_RUN_DIR (or argv[1]).
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

# constants (SI)
G = 6.67430e-11          # m^3 kg^-1 s^-2 (CODATA 2018)
C = 2.99792458e8         # m s^-1
HBAR = 1.054571817e-34   # J s
MEV = 1.602176634e-13    # J
MSUN = 1.98840987e30     # kg (IAU 2015 nominal GM_sun / G)


def horizon_mass(T_mev, gstar):
    """Hubble-volume mass (4 pi / 3) rho c^-2 (c/H)^3 in solar masses."""
    kT = T_mev * MEV
    rho = (math.pi ** 2 / 30.0) * gstar * kT ** 4 / (HBAR * C) ** 3      # J m^-3
    H = math.sqrt(8.0 * math.pi * G * rho / (3.0 * C ** 2))               # s^-1
    return (4.0 * math.pi / 3.0) * rho / C ** 2 * (C / H) ** 3 / MSUN


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    gstar = 10.75
    res = {}
    for T in (1.0, 1.5, 2.0):
        res["M_H(T=%.1f MeV)" % T] = horizon_mass(T, gstar)
    res["M_H(1 MeV) from 1607.00612 (3^1.5 * 40 * (10.75/10)^-0.5 * 27^2)"] = (
        3 ** 1.5 * 40.0 * (gstar / 10.0) ** -0.5 * 27.0 ** 2)
    res["m_PBH(1 MeV) from 2006.16182 (30 * 40^2)"] = 30.0 * 40.0 ** 2
    res["M(1 MeV) from 2109.04896"] = 1e5
    share_before = 5.25 / 10.75
    ratio_after = (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0) * 3.045
    share_after = ratio_after / (1.0 + ratio_after)
    res["nu share before e+e- annihilation"] = share_before
    res["nu share after e+e- annihilation (N_eff=3.045)"] = share_after
    growth = math.exp(2.0)
    kmax = math.log(1.001) / math.log(growth)
    res["lattice: scale-factor growth"] = growth
    res["lattice: |k| bound from 0.1 per cent"] = kmax
    res["k=3.11 mass factor over the same growth"] = growth ** 3.11
    with open(os.path.join(out, "numbers.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for k, v in res.items():
        print("%-66s %.6g" % (k, v))

    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    T = np.logspace(-1, 1, 200)
    MH = np.array([horizon_mass(t, gstar) for t in T])
    ax1.loglog(T, MH, color=fs.PAL["blue"], label=r"$M_H$, $g_*=10.75$ (this run)")
    ax1.loglog(T, 3 ** 1.5 * 40.0 * (gstar / 10.0) ** -0.5 * (T / 27.0) ** -2,
               color=fs.PAL["red"], ls="--", label=r"$3^{3/2}M_{\rm BH}$, 1607.00612")
    ax1.loglog(T, 30.0 * (T / 40.0) ** -2, color=fs.PAL["yellow"], ls="-.",
               label=r"$m_{\rm PBH}\sim m_P^2 t$, 2006.16182")
    ax1.loglog(T, 1e5 * T ** -2, color=fs.PAL["green"], ls=":",
               label=r"$H^{-1}M_{\rm Pl}^2$, 2109.04896")
    ax1.axvspan(1.0, 2.0, color="grey", alpha=0.2, lw=0)
    ax1.text(1.05, 2e6, "decoupling\n1-2 MeV", fontsize=8)
    ax1.set_xlabel(r"$T$ [MeV]")
    ax1.set_ylabel(r"mass [$M_\odot$]")
    ax1.legend(fontsize=7, loc="lower left")
    a = np.logspace(0, 2, 200)
    for k, col, lab in ((3.11, fs.PAL["red"], r"$k=3.11$ (2302.07878)"),
                        (0.5, fs.PAL["yellow"], r"$k=0.5$"),
                        (0.0, "k", r"$k=0$ (Kerr, GR)")):
        ax2.loglog(a, a ** k, color=col, label=lab)
    # the lattice band |dM/M| <= 1e-3 is far thinner than a line on this scale: drawn as a
    # thick segment over the range of a that the lattice run covers
    ax2.plot([1.0, growth], [1.0, 1.0], color=fs.PAL["blue"], lw=5, alpha=0.7,
             solid_capstyle="butt", zorder=3)
    ax2.text(1.1, 0.8, "NR vacuum lattice (1903.01490):\n"
             + r"$|\Delta M/M|\leq10^{-3}$ for $a/a_i\leq e^2$", fontsize=7,
             color=fs.PAL["blue"], va="top")
    ax2.set_xlabel(r"$a/a_i$")
    ax2.set_ylabel(r"$M/M_i$")
    ax2.set_ylim(0.1, 1e6)
    ax2.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_numbers"))
    plt.close(fig)


if __name__ == "__main__":
    main()
