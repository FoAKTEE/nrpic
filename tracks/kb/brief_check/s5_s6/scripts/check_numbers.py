"""Recompute the numbers of brief lines 410 (S5) and 426 (S6) from the sources.

Work package s5_s6 (kb brief check). Inputs are transcribed from TeX sources of the
knowledge-base store; the locator is given next to each (`<key>/<v>/src/<file>:<line>` under
/data/haiyangw/nrpic/kb-data/raw/arxiv). Nothing under kb-data is read, executed or imported by
this script. Physical constants are CODATA values [BACKGROUND].

Checks
  1. Line 410, "neutrinos make up forty to fifty per cent of the radiation energy density":
     share f_nu = rho_nu / (rho_gamma + rho_e + rho_nu) against the photon temperature T, for
     instantaneous neutrino decoupling at T_d (1 MeV, 1906.08217 main.tex:98; also 2 MeV) and
     entropy conservation of the photon-electron-positron plasma afterwards (Fermi-Dirac
     integrals with the electron mass). Limits: 5.25/10.75 before annihilation; with
     T_nu/T -> (4/11)^(1/3) after it, compared with f_nu(0) = 0.40523 of astro-ph/0306304
     (main.tex:328-329) and with (3.36 - 2)/3.36 from g* = 3.36 of 1906.08217 main.tex:98.
  2. Line 410, "the horizon mass is of order 1e5 solar masses" at neutrino decoupling (about
     1 MeV): M_H = c^3 t / G with t = 0.738 (g*/10.75)^(-1/2) (T/1 MeV)^(-2) s and
     M_H = 2.03e5 (t/1 s) M_sun (2002.12778 CKSY2021.tex:276-291), recomputed from the Friedmann
     equation; the rougher normalisation 1 M_sun (T/100 MeV)^(-2) (g/10.75)^(-1/2) of
     astro-ph/0608642 (ms.tex:196-200) is drawn for comparison.
  3. Line 426, "c/v ... two to three orders of magnitude": arithmetic of a [JUDGEMENT] for
     v = 100 to 3000 km/s (no source number).

Writes numbers.json and fig_numbers.{pdf,png} into $NRPIC_RUN_DIR (or the first argument).
Exit status 1 if a number falls outside the band preregistered in JOURNAL.md entry 1 (R1).
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
from scipy.integrate import quad  # noqa: E402

# ---- numbers transcribed from the sources -------------------------------------------------
# 1906.08217/v4/src/main.tex:98: g* = 10.75 after the muons; "e+e- annihilation and neutrino
# decoupling at around 1 MeV, when it drops to g* = 3.36"
GSTAR_BEFORE, GSTAR_AFTER, T_DEC_MEV = 10.75, 3.36, 1.0
# astro-ph_0306304/v2/src (Weinberg): "for 3 neutrino flavors f_nu takes the constant value
# f_nu(0) = 0.40523" (lines 328-329)
FNU_WEINBERG = 0.40523
# 2002.12778/v2/src/CKSY2021.tex:276-280: t ~ 0.738 (g*/10.75)^(-1/2) (T/1 MeV)^(-2) s
# CKSY2021.tex:284-291: M = gamma M_H = gamma c^3 t / G ~ 2.03e5 gamma (t/1 s) M_sun
T_COEF_S, MH_PER_S = 0.738, 2.03e5
# astro-ph_0608642/v1/src/ms.tex:196-200: M_H(T) ~ 1 M_sun (T/100 MeV)^(-2) (g_eff/10.75)^(-1/2)
MACK_MSUN_AT_100MEV = 1.0

# ---- constants [BACKGROUND] (CODATA 2018, IAU nominal solar mass) --------------------------
G = 6.67430e-11
C = 2.99792458e8
HBAR = 1.054571817e-34
MEV = 1.602176634e-13
MSUN = 1.98847e30
ME_MEV = 0.51099895

# preregistered bands (JOURNAL.md entry 1, R1)
BAND_SHARE = (0.40, 0.50)
BAND_MH_1MEV = (3e4, 3e5)


def fermi_rho_p(T, m, g):
    """energy density and pressure (MeV^4) of a fermion species of mass m, dof g, mu = 0."""
    if T <= 0:
        return 0.0, 0.0
    x = m / T

    def rho_int(u):  # u = p/T
        e = math.sqrt(u * u + x * x)
        return u * u * e / (math.exp(e) + 1.0) if e < 700 else 0.0

    def p_int(u):
        e = math.sqrt(u * u + x * x)
        return u ** 4 / (3.0 * e) / (math.exp(e) + 1.0) if e < 700 else 0.0

    rho = g / (2 * math.pi ** 2) * T ** 4 * quad(rho_int, 0, 60, limit=200)[0]
    p = g / (2 * math.pi ** 2) * T ** 4 * quad(p_int, 0, 60, limit=200)[0]
    return rho, p


def plasma(T):
    """photons (g = 2) plus electrons and positrons (g = 4): rho, entropy density."""
    rg = 2 * math.pi ** 2 / 30 * T ** 4
    pg = rg / 3
    re, pe = fermi_rho_p(T, ME_MEV, 4)
    return rg, re, (rg + pg + re + pe) / T


def share_curve(T_dec, temps):
    """f_nu(T) for instantaneous decoupling at T_dec (MeV); also T_nu/T."""
    _, _, s_dec = plasma(T_dec)
    out_f, out_r = [], []
    for T in temps:
        rg, re, s = plasma(T)
        if T >= T_dec:
            Tnu = T
        else:
            # entropy of the plasma conserved: s a^3 = const, a_dec/a = (s/s_dec)^(1/3)
            Tnu = T_dec * (s / s_dec) ** (1.0 / 3.0)
        rnu = 3 * 2 * 7 / 8 * math.pi ** 2 / 30 * Tnu ** 4
        out_f.append(rnu / (rg + re + rnu))
        out_r.append(Tnu / T)
    return np.array(out_f), np.array(out_r)


def horizon_mass_first_principles(T_mev, gstar):
    """M_H = c^3 t / G, t = 1/(2H), H^2 = 8 pi G rho / (3 c^2), rho = pi^2/30 g* T^4/(hbar c)^3."""
    kT = T_mev * MEV
    u = math.pi ** 2 / 30 * gstar * kT ** 4 / (HBAR * C) ** 3  # J m^-3
    H = math.sqrt(8 * math.pi * G * u / (3 * C ** 2))
    t = 1 / (2 * H)
    return t, C ** 3 * t / G / MSUN


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    res, fails = {}, []

    # 1. neutrino share
    temps = np.logspace(math.log10(10.0), math.log10(0.003), 160)
    f1, r1 = share_curve(1.0, temps)
    f2, r2 = share_curve(2.0, temps)
    f_before = 21 / 4 / GSTAR_BEFORE
    f_after_g = (GSTAR_AFTER - 2) / GSTAR_AFTER
    k = 3 * 7 / 8 * (4 / 11) ** (4 / 3)
    f_after_exact = k / (1 + k)
    res["share"] = {
        "before_annihilation_21over4_over_10.75": f_before,
        "after_from_gstar_3.36": f_after_g,
        "after_exact_(4/11)^(4/3)": f_after_exact,
        "weinberg_f_nu0": FNU_WEINBERG,
        "curve_Tdec1MeV_at_10MeV": float(f1[0]), "curve_Tdec1MeV_at_3keV": float(f1[-1]),
        "curve_Tdec1MeV_max": float(f1.max()), "curve_Tdec1MeV_min": float(f1.min()),
        "curve_Tdec2MeV_max": float(f2.max()), "curve_Tdec2MeV_min": float(f2.min()),
        "Tnu_over_T_final_Tdec1MeV": float(r1[-1]),
        "Tnu_over_T_expected": (4 / 11) ** (1 / 3),
    }
    for name, v in (("before", f_before), ("after_exact", f_after_exact),
                    ("curve_max", f1.max()), ("curve_min", f1.min())):
        if not BAND_SHARE[0] <= v <= BAND_SHARE[1]:
            fails.append("share %s = %.4f outside %s" % (name, v, BAND_SHARE))
    if abs(f_after_exact - FNU_WEINBERG) > 5e-4:
        fails.append("exact share %.5f differs from Weinberg %.5f" % (f_after_exact, FNU_WEINBERG))
    if abs(r1[-1] - (4 / 11) ** (1 / 3)) > 2e-3:
        fails.append("T_nu/T final %.4f differs from (4/11)^(1/3)" % r1[-1])

    # 2. horizon mass
    t_cksy = T_COEF_S
    mh_cksy = MH_PER_S * t_cksy
    t_fp, mh_fp = horizon_mass_first_principles(1.0, 10.75)
    mh_mack = MACK_MSUN_AT_100MEV * (1.0 / 100.0) ** -2
    res["horizon_mass_at_1MeV"] = {
        "cksy_t_s": t_cksy, "cksy_MH_Msun": mh_cksy,
        "first_principles_t_s": t_fp, "first_principles_MH_Msun": mh_fp,
        "cksy_c3_over_G_Msun_per_s": C ** 3 / G / MSUN,
        "mack_MH_Msun": mh_mack,
        "at_2MeV_cksy_MH_Msun": mh_cksy / 4, "at_0.5MeV_cksy_MH_Msun": mh_cksy * 4,
    }
    if not BAND_MH_1MEV[0] <= mh_cksy <= BAND_MH_1MEV[1]:
        fails.append("M_H(1 MeV) CKSY = %.3g outside %s" % (mh_cksy, BAND_MH_1MEV))
    if abs(mh_fp / mh_cksy - 1) > 0.02:
        fails.append("first-principles M_H %.4g differs from CKSY %.4g by > 2%%" % (mh_fp, mh_cksy))

    # 3. c / v
    vs = np.array([100.0, 200.0, 300.0, 1000.0, 3000.0])
    res["c_over_v"] = {"%g km/s" % v: C / (v * 1e3) for v in vs}

    res["bands"] = {"share": BAND_SHARE, "MH_1MeV": BAND_MH_1MEV}
    res["fails"] = fails
    with open(os.path.join(out, "numbers.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    # ---- figure ----
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.35, 3.4))
    ax = axs[0]
    fs.band(ax, temps, BAND_SHARE[0], BAND_SHARE[1], "grey", alpha=0.15)
    ax.plot(temps, f1, color=fs.PAL["blue"], label=r"$T_d = 1$ MeV")
    ax.plot(temps, f2, color=fs.PAL["red"], ls="--", label=r"$T_d = 2$ MeV")
    ax.axhline(FNU_WEINBERG, **fs.MASK_LINE)
    ax.axhline(f_before, **fs.MASK_LINE)
    ax.text(0.004, FNU_WEINBERG - 0.008, "0.40523 (astro-ph/0306304)", fontsize=7, va="top")
    ax.text(0.004, f_before + 0.004, "21/4 / 10.75 = 0.488", fontsize=7, va="bottom")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_ylim(0.37, 0.53)
    ax.set_xlabel(r"photon temperature $T$ [MeV]")
    ax.set_ylabel(r"$\rho_\nu / \rho_{\rm rad}$")
    ax.set_title("(a) neutrino share (line 410)", fontsize=9)
    ax.legend(loc="lower left", fontsize=7, frameon=False)

    ax = axs[1]
    Tg = np.logspace(-1, 1, 100)
    ax.plot(Tg, MH_PER_S * T_COEF_S * Tg ** -2, color=fs.PAL["blue"],
            label="2002.12778 (CKSY)")
    fp = [horizon_mass_first_principles(T, 10.75)[1] for T in Tg]
    ax.plot(Tg, fp, color=fs.PAL["yellow"], ls=":", lw=2.5, label="Friedmann, $g_*=10.75$")
    ax.plot(Tg, MACK_MSUN_AT_100MEV * (Tg / 100.0) ** -2, color=fs.PAL["red"], ls="--",
            label="astro-ph/0608642")
    ax.axhspan(BAND_MH_1MEV[0], BAND_MH_1MEV[1], color="grey", alpha=0.15)
    ax.axvline(1.0, **fs.MASK_LINE)
    ax.plot([1.0], [mh_cksy], "o", color=fs.PAL["blue"], ms=5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.invert_xaxis()
    ax.set_xlabel(r"$T$ [MeV]")
    ax.set_ylabel(r"horizon mass $M_H$ [$M_\odot$]")
    ax.set_title("(b) horizon mass (line 410)", fontsize=9)
    ax.legend(loc="upper left", fontsize=7, frameon=False)

    ax = axs[2]
    vv = np.logspace(1.7, 3.7, 50)
    ax.plot(vv, C / (vv * 1e3), color=fs.PAL["blue"])
    ax.axhspan(1e2, 1e3, color="grey", alpha=0.15)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"particle speed $v$ [km/s]")
    ax.set_ylabel(r"$c/v$")
    ax.set_title("(c) step ratio c/v (line 426)", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_numbers"))
    if fails:
        print("FAIL:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
