"""Figure: Newtonian secondary infall onto a seed in a matter era and capture.

Reads the self-similar solution of run selfsim (selfsimilar_profile.npz, selfsimilar.txt
values via selfsimilar.json) and the shell calculations of run shells_ana (analysis.json).
Panel (a): density of the self-similar solution compensated by the frozen-in power law
lambda^(-9/4), lambda = r / r_ta. Panel (b): turned-around mass, black-hole mass for
radially infalling dust absorbed at the horizon, and the mass that passed the centre once
(dress) for dust allowed to pass, against the scale factor. Panel (c): fraction of the
collapsed dust captured by the black hole at a/a_i = 4 against the initial velocity
dispersion. Numbers to fig_infall_numbers.json.
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

STEM = "fig_infall"
COEF = (4.0 / (3.0 * np.pi)) ** (2.0 / 3.0)   # asymptotic turnaround coefficient


def series(g, key, q):
    d = g[key]
    a = np.array([float(k[1:]) for k in d])
    v = np.array([d[k][q] for k in d])
    o = np.argsort(a)
    return a[o], v[o]


def main():
    out = C.out_dir("figures")
    z = np.load(C.run_file("selfsim", "selfsimilar_profile.npz"))
    ss = C.load_json("selfsim", "selfsimilar.json")
    sh = C.load_json("shells_ana", "analysis.json")
    lead = C.load_json("infall_lead", "lead_infall_recheck.json")
    cz.use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.0, 2.45))
    fig.subplots_adjust(left=0.075, right=0.98, bottom=0.19, top=0.96, wspace=0.42)

    lam, rho = z["rc"], z["rho"]
    a.semilogx(lam, rho * lam**2.25, color=cz.PAL["red"])
    a.axvline(ss.get("lambda1", 0.3553170500034671), **cz.MASK_LINE)
    a.axhline(1.0, **cz.GUIDE)
    a.set_xlim(1e-5, 1)
    a.set_ylim(0, 4)
    a.set_xlabel(r"$\lambda=r/r_{\rm ta}$")
    a.set_ylabel(r"$\lambda^{9/4}\rho/\rho_b$")
    a.text(2e-5, 1.15, "frozen-in", fontsize=8)
    a.text(0.05, 0.9, "(a)", transform=a.transAxes)

    g = sh["growth"]
    aa, mta = series(g, "pass_e0.1_s0.5_a100", "mta")
    _, dress = series(g, "pass_e0.1_s0.5_a100", "dress")
    ab, mbh = series(g, "absorb_e0.01", "mbh")
    b.loglog(aa, mta - 1, "o-", color=cz.PAL["blue"], ms=3, label=r"$M_{\rm ta}-M$")
    b.loglog(aa, dress, "s-", color=cz.PAL["green"], ms=3, label="dress (passing)")
    b.loglog(ab, mbh - 1, "^-", color=cz.PAL["red"], ms=3.5, label=r"$M_{\rm BH}-M$ (absorbing)")
    x = np.array([1.5, 100])
    b.loglog(x, COEF * x, **cz.GUIDE, label=r"$(4/3\pi)^{2/3}\,a/a_i$")
    b.set_xlim(1.4, 110)
    b.set_ylim(1e-2, 1e2)
    b.set_xlabel(r"$a/a_i$")
    b.set_ylabel(r"mass $/M$")
    b.legend(frameon=False, loc="lower right", fontsize=6.5, handlelength=1.6)
    b.text(0.05, 0.9, "(b)", transform=b.transAxes)

    am = sh["angmom"]
    sig = np.array([am[k]["sigma"] for k in am])
    frac = np.array([am[k]["captured_fraction"] for k in am])
    c.plot(sig, frac, "o-", color=cz.PAL["red"], ms=4)
    c.set_xlim(0, 0.22)
    c.set_ylim(0.6, 1.04)
    c.set_xlabel(r"initial dispersion $\sigma_i$")
    c.set_ylabel("captured fraction")
    c.text(0.05, 0.06, "(c)", transform=c.transAxes)
    cz.save(fig, os.path.join(out, STEM))

    pick = lambda d, k: {kk: d[k][kk] for kk in ("M_ta", "M_c", "coef")}  # noqa: E731
    nums = dict(selfsim=dict(lambda1=ss.get("lambda1"), m_at_lambda1=ss.get("m_at_lambda1"),
                             slope_m_1em4_1em3=ss["slope_m_1em4_1em3"],
                             slope_m_3em3_3em2=ss["slope_m_3em3_3em2"],
                             rho_lam94_innermost=float(np.mean((rho * lam**2.25)[lam < 1e-4]))),
                shells=dict(f_passed=sh["selfsim"]["f_passed"], tau_c1=sh["selfsim"]["tau_c1"],
                            mta_a2=sh["checks"]["a2"]["mta"], mta_a4=sh["checks"]["a4"]["mta"],
                            mbh_a2=sh["checks"]["a2"]["mbh"], mbh_a4=sh["checks"]["a4"]["mbh"],
                            mbh_doubling_a=sh["mbh_doubling_a"],
                            captured_fraction={str(s): f for s, f in zip(sig, frac)}),
                lead={a_: pick(lead["0.01"], a_) for a_ in ("2", "4", "8", "100")},
                coef_limit=COEF)
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps(nums, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
