"""Item (c): the noise amplitude of arXiv:2401.08530 appendix D (P0:1034-1076) in slow roll
and in ultra-slow roll, against a numerical solution of the Mukhanov-Sasaki equation.

P0:1071-1072: with a Heaviside window W = Theta(sigma a H - k) and the integration by parts
P0:1050, the variance per e-fold of S = S_R/H^2 is
    D = |f(k_sigma)|^2 / (6 pi^2) d(sigma a H)^3/dN,   f = R' + (3 - eps1 - eps2) R,
and P0 approximates sqrt(D) ~ 3 H / (2 pi sqrt(2 eps1) M) "in SR (eps1, eps2 ~ 0) or USR
(eps2 ~ 6)". This script integrates the background and the MS equation in e-folds
(P0:718 form: R'' + (3 - eps1 - eps2) R' + (k/aH)^2 R = 0, Launay sign eps2 = -dln eps1/dN)
from Bunch-Davies data, evaluates f at the crossing k = sigma a H for several sigma, and
compares sqrt(D) with the printed value. Units M = 1. Writes noise_amp.json and
fig_noise_amp.png into --out.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
N_LO = -8.0      # background starts here (e-folds; a = e^N)
sys.path.insert(0, HERE)


def background(case, N_end):
    """Background in e-folds from N = 0: returns dense solution of (phi, phi')."""
    if case == 'SR':
        # quadratic potential V = m^2 phi^2 / 2; eps1 = 2/phi^2 on the attractor -> 0.01
        m = 1e-5 * np.sqrt(6.0) / 20.0   # sets H ~ 1e-5 at phi = 20 (only ratios matter)
        V = lambda p: 0.5 * m * m * p * p          # noqa: E731
        dV = lambda p: m * m * p                   # noqa: E731
        phi0 = np.sqrt(20.0 ** 2 - 4.0 * N_LO)    # attractor phi^2 = phi(0)^2 - 4 N
        dphi0 = -2.0 / phi0                         # slow-roll attractor dphi/dN = -2/phi
    else:
        # USR: flat plateau V = V0 (as P0 section V before phi_c), field nearly stopping
        V0 = 3.0e-10
        V = lambda p: V0 + 0.0 * p                 # noqa: E731
        dV = lambda p: 0.0 * p                     # noqa: E731
        phi0 = 0.0
        dphi0 = -np.sqrt(2.0 * 1e-2)                # eps1 = 1e-2 at N_LO, decays as e^-6N

    # variables (phi, u = ln|phi'|): robust when phi' decays as e^{-3N} (USR)
    sgn = np.sign(dphi0)

    def rhs(N, y):
        p, u = y
        dp = sgn * np.exp(u)
        e1 = 0.5 * dp * dp
        H2 = V(p) / (3.0 - e1)
        return [dp, -(3.0 - e1) - dV(p) / (H2 * dp)]

    sol = solve_ivp(rhs, (N_LO, N_end), [phi0, np.log(abs(dphi0))], method='DOP853',
                    rtol=1e-12, atol=1e-13, dense_output=True)

    def bg(N):
        p, u = sol.sol(N)
        dp = sgn * np.exp(u)
        e1 = 0.5 * dp * dp
        H = np.sqrt(V(p) / (3.0 - e1))
        dlndp = -(3.0 - e1) - dV(p) / (H ** 2 * dp)
        e2 = -2.0 * dlndp          # -dln eps1/dN
        return H, e1, e2
    return bg


def mode(bg, k, N_start, N_end):
    """MS mode in e-folds with Bunch-Davies data at N_start (a = e^N)."""
    H, e1, e2 = bg(N_start)
    a = np.exp(N_start)
    z = a * np.sqrt(2 * e1)
    # de Sitter-corrected Bunch-Davies: v = e^{-ik tau}(1 - i/(k tau))/sqrt(2k), tau = -1/(aH)
    tau = -1.0 / (a * H * (1 - e1))
    v = np.exp(-1j * k * tau) * (1 - 1j / (k * tau)) / np.sqrt(2 * k)
    dv = np.exp(-1j * k * tau) * (-1j * k * (1 - 1j / (k * tau)) + 1j / (k * tau ** 2)) / np.sqrt(2 * k)
    R = v / z
    dlnz = 1.0 - e2 / 2.0
    dR = dv / (a * H * z) - R * dlnz

    def rhs(N, y):
        Hh, ee1, ee2 = bg(N)
        r = y[0] + 1j * y[1]
        dr = y[2] + 1j * y[3]
        ddr = -(3 - ee1 - ee2) * dr - (k / (np.exp(N) * Hh)) ** 2 * r
        return [dr.real, dr.imag, ddr.real, ddr.imag]

    sol = solve_ivp(rhs, (N_start, N_end), [R.real, R.imag, dR.real, dR.imag],
                    method='DOP853', rtol=1e-11, atol=1e-30, dense_output=True)
    return sol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    sigmas = np.array([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    out = {}
    for case in ('SR', 'USR'):
        N_end = 9.0
        bg = background(case, N_end + 1)
        H0 = bg(0.0)[0]
        # one mode that crosses k = aH at N = 2 (k in units with a(0) = 1)
        Nh = 2.0
        k = np.exp(Nh) * bg(Nh)[0]
        # start where k/(aH) = 300 (deep inside)
        Ns = brentq(lambda N: k / (np.exp(N) * bg(N)[0]) - 300.0, N_LO + 0.1, Nh)
        sol = mode(bg, k, Ns, N_end)
        rows = []
        for s in sigmas:
            Nc = brentq(lambda N: s * np.exp(N) * bg(N)[0] - k, Nh - 1, N_end - 0.01)
            H, e1, e2 = bg(Nc)
            y = sol.sol(Nc)
            R = y[0] + 1j * y[1]
            dR = y[2] + 1j * y[3]
            f_ibp = dR + (3 - e1 - e2) * R           # P0:1054 (after integration by parts)
            f_R = (3 - e1 - e2) * R                  # P0:1071 first line (dR dropped)
            g_full = 2 * dR + (3 - e1 - e2) * R      # coefficient of W' in P0:1037
            dks3 = 3 * k ** 3 * (1 - e1)             # d(sigma a H)^3/dN at the crossing
            amp = lambda f: np.sqrt(abs(f) ** 2 * dks3 / (6 * np.pi ** 2))  # noqa: E731
            printed = 3 * H / (2 * np.pi * np.sqrt(2 * e1))
            Ran = H / np.sqrt(4 * e1 * k ** 3) * np.sqrt(1 + s * s)   # |R| of P0:1059
            rows.append({'sigma': float(s), 'N_cross': float(Nc), 'eps1': float(e1),
                         'eps2': float(e2), 'H': float(H),
                         'absR_num': float(abs(R)), 'absR_P0_1059': float(Ran),
                         'dR_over_R': [float((dR / R).real), float((dR / R).imag)],
                         'amp_ibp_over_printed': float(amp(f_ibp) / printed),
                         'amp_Ronly_over_printed': float(amp(f_R) / printed),
                         'amp_Wprime_coef_over_printed': float(amp(g_full) / printed)})
        out[case] = {'k': float(k), 'H0': float(H0), 'N_start': float(Ns), 'rows': rows}
        for r in rows:
            print(case, 'sigma=%.3f eps1=%.3e eps2=%.3f |R|/|R_P0|=%.4f ibp=%.4e Ronly=%.4f'
                  % (r['sigma'], r['eps1'], r['eps2'], r['absR_num'] / r['absR_P0_1059'],
                     r['amp_ibp_over_printed'], r['amp_Ronly_over_printed']))
    with open(os.path.join(args.out, 'noise_amp.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    # figure
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
    for ax, case in zip(axes, ('SR', 'USR')):
        rows = out[case]['rows']
        s = [r['sigma'] for r in rows]
        ax.loglog(s, [r['amp_ibp_over_printed'] for r in rows], 'o-',
                  label=r"$R'+(3-\epsilon_1-\epsilon_2)R$ (P0 eq. after ibp)")
        ax.loglog(s, [r['amp_Ronly_over_printed'] for r in rows], 's--',
                  label=r"$(3-\epsilon_1-\epsilon_2)R$ ($R'$ dropped)")
        ax.loglog(s, [r['absR_num'] / r['absR_P0_1059'] for r in rows], '^:',
                  label=r"$|R|$ numerical / P0 form")
        if case == 'USR':
            ss = np.array(s)
            ax.loglog(ss, ss ** 2 / 3, 'k-', lw=0.8, label=r"$\sigma^2/3$")
        ax.axhline(1.0, color='0.5', lw=0.6)
        ax.set_xlabel(r'$\sigma$')
        ax.set_title('%s (numerical MS)' % case)
    axes[0].set_ylabel('amplitude / printed $3H/(2\\pi\\sqrt{2\\epsilon_1}M)$')
    axes[1].legend(fontsize=6, loc='lower right')
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, 'fig_noise_amp.png'), dpi=150)
    print('wrote', args.out)


if __name__ == '__main__':
    main()
