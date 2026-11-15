#!/usr/bin/env python3
"""Lead check L-B (independent of spec/ref/ms_reference.py): the two backgrounds of
arXiv:2512.14649 (PRD_v2.tex lines 405-424) from the printed parameters, and the
super-horizon behaviour of one mode with and without metric perturbations.

Units Mpl = 1, e-folds N, Launay signs (eps2 = -d ln eps1/dN). Background in e-folds:
  phi_NN = -(3 - eps1) phi_N - (3 - eps1) V'/V,   eps1 = phi_N^2/2,   H^2 = V/(3 - eps1).
Quadratic: phi_N = +sqrt(2 eps1) at N0 and eps2 = -0.02 fix phi0 through
  eps2 = 2 (3 - eps1) [1 + V'/(V phi_N)]   (derived here from the equations above),
and H0 = 1e-5 fixes m. Inflection: phi0 = -1.2, phi_N = -V'/V, H0 from H^2 = V/(3 - eps1).

Perturbations in flat gauge, cosmic time written in e-folds (k in units with a(N*) = 1):
  dphi_NN + (3 - eps1) dphi_N + [(k/aH)^2 + V''/H^2 - M] dphi = 0,
  M = (1/(a^3 H^2)) d/dt(a^3 phidot^2/H) / ... (metric term; 0 for the "deformed" FLRW
  lattice of arXiv:2606.14853 lines 177-212), written as
  M = 2 eps1 (3 - eps1 + phi_NN/phi_N) ... evaluated below from the background,
  R = dphi / phi_N. Bunch-Davies at k/aH = 200.
Outputs: lead_bg.json, fig_lead_bg.png (background), fig_lead_ms.png (one mode, both).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "python"))
from nrpic import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

LAM, VEV = 1.86e-6, 0.198


def pot(case):
    if case == "quadratic":
        return None
    v = VEV

    def V(p):
        return LAM * v**4 * p**2 * (3 * p**2 + 2 * np.sqrt(2) * p * v + 6 * v**2) / (3 * (3 * p**2 + 2 * v**2) ** 2)

    def dV(p, h=1e-30):
        # complex-step derivative: exact to rounding
        return np.imag(V(np.asarray(p, dtype=complex) + 1j * h)) / h

    def d2V(p, h=1e-5):
        return (dV(p + h) - dV(p - h)) / (2 * h)
    return V, dV, d2V


def background(case, n_before, n_after):
    if case == "quadratic":
        e1, e2, H0 = 0.01, -0.02, 1e-5
        pn = np.sqrt(2 * e1)
        # eps2 = 2 (3 - eps1)(1 + 2/(phi phi_N)) for V = m^2 phi^2/2
        phi0 = 2.0 / (pn * (e2 / (2 * (3 - e1)) - 1))
        m = H0 * np.sqrt(2 * (3 - e1)) / abs(phi0)
        V = lambda p: 0.5 * m**2 * p**2
        dV = lambda p: m**2 * p
        d2V = lambda p: m**2 + 0 * p
        y0 = [phi0, pn]
        extra = {"phi0": phi0, "m": m, "phiN0": pn}
    else:
        V, dV, d2V = pot(case)
        phi0 = -1.2
        pn = -dV(phi0) / V(phi0)
        y0 = [phi0, pn]
        extra = {"phi0": phi0, "phiN0": pn}

    def rhs(N, y):
        p, q = y
        e1 = 0.5 * q * q
        return [q, -(3 - e1) * q - (3 - e1) * dV(p) / V(p)]
    N = np.linspace(0, n_before + n_after, 20001)
    s = solve_ivp(rhs, (0, N[-1]), y0, t_eval=N, rtol=1e-12, atol=1e-14, method="DOP853")
    p, q = s.y
    e1 = 0.5 * q * q
    H = np.sqrt(V(p) / (3 - e1))
    qn = np.gradient(q, N)
    e2 = -2 * qn / q
    extra["H0"] = float(H[0])
    return dict(N=N - n_before, phi=p, phiN=q, eps1=e1, eps2=e2, H=H, V=V(p), d2V=d2V(p),
                extra=extra, fns=(V, dV, d2V))


def mode(bg, k_over_aH_at_Nstar_exit, n_exit, metric):
    """One mode leaving the horizon at N = n_exit (relative to N*); returns N, P_R."""
    V, dV, d2V = bg["fns"]
    Ng = bg["N"]
    # a = exp(N) (a* = 1); k chosen so that k = a H at n_exit
    Hx = np.interp(n_exit, Ng, bg["H"])
    k = np.exp(n_exit) * Hx
    # start where k/aH = 200
    aH = np.exp(Ng) * bg["H"]
    i0 = np.argmax(k / aH < 200.0)
    N0 = Ng[i0]

    def bgat(N):
        p = np.interp(N, Ng, bg["phi"])
        q = np.interp(N, Ng, bg["phiN"])
        return p, q

    def rhs(N, y):
        p, q = bgat(N)
        e1 = 0.5 * q * q
        H2 = V(p) / (3 - e1)
        qN = -(3 - e1) * q - (3 - e1) * dV(p) / V(p)
        # metric term of the flat-gauge equation in e-folds:
        # (1/(a^3 H^2)) d/dt (a^3 phidot^2 / H) = (1/a^3 H) d/dN (a^3 H q^2)
        #   = q^2 (3 - e1) + 2 q qN
        Mterm = (q * q * (3 - e1) + 2 * q * qN) if metric else 0.0
        a = np.exp(N)
        w2 = (k / (a * np.sqrt(H2))) ** 2 + d2V(p) / H2 - Mterm
        dre, dim_, vre, vim = y
        return [vre, vim, -(3 - e1) * vre - w2 * dre, -(3 - e1) * vim - w2 * dim_]
    p0, q0 = bgat(N0)
    e10 = 0.5 * q0 * q0
    H0 = np.sqrt(V(p0) / (3 - e10))
    a0 = np.exp(N0)
    # Bunch-Davies in flat gauge: dphi = e^{-ik tau}/(a sqrt(2k)), tau ~ -1/(aH) (deep inside)
    amp = 1.0 / (a0 * np.sqrt(2 * k))
    # d/dN dphi = (1/(aH)) d/dtau dphi ... = -(1 + i k/(aH)) dphi to leading order
    x = k / (a0 * H0)
    d = amp + 0j
    dN = -(1 + 1j * x) * d
    Nend = Ng[-1]
    s = solve_ivp(rhs, (N0, Nend), [d.real, d.imag, dN.real, dN.imag], rtol=1e-10, atol=1e-30,
                  method="DOP853", dense_output=True, max_step=0.01)
    Ns = np.linspace(N0, Nend, 4000)
    dr, di, _, _ = s.sol(Ns)
    q = np.interp(Ns, Ng, bg["phiN"])
    P = k**3 / (2 * np.pi**2) * (dr**2 + di**2) / q**2
    e1x = np.interp(n_exit, Ng, bg["eps1"])
    P0 = Hx**2 / (8 * np.pi**2 * e1x)
    return Ns, P / P0, k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    figstyle.use_style()
    res = {}
    bgs = {}
    for case, nb, na in (("quadratic", 5.0, 8.0), ("inflection", 3.0, 10.0)):
        bg = background(case, nb, na)
        bgs[case] = bg
        N = bg["N"]
        i = np.argmin(abs(N))
        r = {k: float(v) for k, v in bg["extra"].items()}
        r.update(H_star=float(bg["H"][i]), eps1_star=float(bg["eps1"][i]),
                 eps2_star=float(bg["eps2"][i]), V_star_Mpl100=float(bg["V"][i] * 1e8),
                 eps1_end=float(bg["eps1"][-1]), eps2_end=float(bg["eps2"][-1]))
        usr = (bg["eps2"] > 3) & (N > 0)
        if usr.any():
            r["usr_from"] = float(N[usr][0])
            r["usr_to"] = float(N[usr][-1])
            r["eps2_max"] = float(bg["eps2"][N > 0].max())
            j = np.argmin(np.where(N > 0, bg["eps1"], 1))
            r["eps1_min"] = float(bg["eps1"][j])
            r["N_eps1_min"] = float(N[j])
        res[case] = r
    # one slow-roll mode, exit at N* + 1.5, with and without metric perturbations
    bg = bgs["quadratic"]
    Nf, Pf, k = mode(bg, None, 1.5, True)
    Nd, Pd, _ = mode(bg, None, 1.5, False)
    sel = (Nf > 1.5 + 3) & (Nf < 1.5 + 6)
    slope_full = np.polyfit(Nf[sel], np.log(Pf[sel]), 1)[0]
    slope_def = np.polyfit(Nd[sel], np.log(Pd[sel]), 1)[0]
    e1m = np.interp(Nf[sel], bg["N"], bg["eps1"]).mean()
    res["sr_mode"] = dict(n_exit=1.5, P_full_end_over_SR=float(Pf[-1]),
                          P_def_end_over_SR=float(Pd[-1]), ratio_def_full_end=float(Pd[-1] / Pf[-1]),
                          slope_full=float(slope_full), slope_def=float(slope_def),
                          minus4eps1=float(-4 * e1m))
    # USR mode leaving before the USR onset
    bg = bgs["inflection"]
    Nf2, Pf2, _ = mode(bg, None, 0.7, True)
    Nd2, Pd2, _ = mode(bg, None, 0.7, False)
    res["usr_mode"] = dict(n_exit=0.7, ratio_def_full_end=float(Pd2[-1] / Pf2[-1]),
                           P_full_end_over_exit=float(Pf2[-1]))
    with open(os.path.join(a.out, "lead_bg.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    # figures
    fig, ax = plt.subplots(2, 2, figsize=(figstyle.FULL_WIDTH, 5.0), sharex="col")
    for c, case in enumerate(("quadratic", "inflection")):
        bg = bgs[case]
        N = bg["N"]
        m = N >= 0
        ax[0, c].semilogy(N[m], bg["eps1"][m], color=figstyle.PAL["blue"], label=r"$\varepsilon_1$")
        ax[0, c].set_ylabel(r"$\varepsilon_1$")
        ax[1, c].plot(N[m], bg["eps2"][m], color=figstyle.PAL["red"])
        ax[1, c].axhline(3, **figstyle.MASK_LINE)
        ax[1, c].set_ylabel(r"$\varepsilon_2$")
        ax[1, c].set_xlabel(r"$\mathcal{N}-\mathcal{N}^\circledast$")
        ax[0, c].set_title(case)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_lead_bg"))
    plt.close(fig)
    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.2))
    ax[0].semilogy(Nf, Pf, color=figstyle.PAL["blue"], label="with metric perturbations (MS)")
    ax[0].semilogy(Nd, Pd, color=figstyle.PAL["red"], label="without (FLRW lattice)")
    ax[0].axvline(1.5, **figstyle.MASK_LINE)
    ax[0].set_xlabel(r"$\mathcal{N}-\mathcal{N}^\circledast$")
    ax[0].set_ylabel(r"$\Delta_\mathcal{R} / [H^2/(8\pi^2\varepsilon_1)]_\mathrm{exit}$")
    ax[0].set_ylim(0.3, 30)
    ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_title("quadratic, exit at 1.5")
    ax[1].semilogy(Nf2, Pf2, color=figstyle.PAL["blue"])
    ax[1].semilogy(Nd2, Pd2, color=figstyle.PAL["red"])
    ax[1].axvline(0.7, **figstyle.MASK_LINE)
    ax[1].set_xlabel(r"$\mathcal{N}-\mathcal{N}^\circledast$")
    ax[1].set_title("inflection, exit at 0.7")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_lead_ms"))
    plt.close(fig)


if __name__ == "__main__":
    main()
