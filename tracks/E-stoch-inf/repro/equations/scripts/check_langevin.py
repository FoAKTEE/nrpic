"""Item (d): the Langevin pair of arXiv:2401.08530 section V (P0:782-830) in the
uniform-field gauge, derived with sympy, and a Monte Carlo test of the Ito term.

1. dN/dN_b from the long-wavelength Hamiltonian constraint (P0:802-808).
2. Lapse equation from the field equation (P0:812) with Z = phidot_b / alpha, Ito's lemma for
   alpha = f(Z) = phidot_b / Z (P0:814-821), conversion to N_b (P0:823-829).
3. Monte Carlo: dZ = (phidot/Z) sigma dW (drift-free, phidot constant), Euler-Maruyama in the
   Ito sense on Z, many paths; the mean drift of alpha = phidot/Z over a short time is
   compared with alpha^5 sigma^2/phidot^2 (Ito's lemma) and alpha^3 sigma^2/phidot^2 (P0:817).
Writes langevin.json and fig_langevin_ito.png into --out.
"""
import argparse
import json
import os
import sys

import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))


def symbolic():
    res = {}
    t = sp.Symbol('t')
    al, Hb, e1, e2, M = sp.symbols('alpha H epsilon_1 epsilon_2 M', positive=True)
    pd = sp.sqrt(2 * e1) * M * Hb                 # phidot_b (P0:909)
    V = M ** 2 * Hb ** 2 * (3 - e1)               # background Friedmann
    # long-wavelength Hamiltonian constraint P0:802: 6 (dN/dt)^2/alpha^2 = (2/M^2)(pd^2/(2 alpha^2) + V)
    dNdt = sp.sqrt(sp.Rational(1, 3) / M ** 2 * (pd ** 2 / 2 + al ** 2 * V))
    dNdNb = sp.simplify(dNdt / Hb)
    printed = sp.sqrt(1 + (al ** 2 - 1) * (1 - e1 / 3))
    res['D1 dN/dN_b = sqrt(1+(alpha^2-1)(1-eps1/3)) (P0:806)'] = bool(
        sp.simplify(dNdNb ** 2 - printed ** 2) == 0)
    # Ito: Z = pd/alpha, alpha = f(Z) = pd/Z
    Z, sig, dW = sp.symbols('Z sigma dW', positive=True)
    f = pd / Z
    fZ = sp.diff(f, Z)
    fZZ = sp.diff(f, Z, 2)
    alZ = pd / Z
    # dZ = A dt + alpha sigma dW  (noise alpha S_Pi as in P0:812)
    ito = sp.simplify((fZZ / 2 * (alZ * sig) ** 2).subs(Z, pd / al))
    res['D3 Ito term with noise alpha*S in dZ = alpha^5 sigma^2/phidot^2'] = bool(
        sp.simplify(ito - al ** 5 * sig ** 2 / pd ** 2) == 0)
    res['D3 Ito term with noise alpha*S in dZ = alpha^3 sigma^2/phidot^2 (P0:817)'] = bool(
        sp.simplify(ito - al ** 3 * sig ** 2 / pd ** 2) == 0)
    noise_coef = sp.simplify((fZ * alZ * sig).subs(Z, pd / al))
    res['D3 noise term of the alpha equation = -alpha^3 sigma/phidot (P0:818, sign immaterial)'] = \
        bool(sp.simplify(noise_coef + al ** 3 * sig / pd) == 0)
    ito1 = sp.simplify((fZZ / 2 * sig ** 2).subs(Z, pd / al))
    noise1 = sp.simplify((fZ * sig).subs(Z, pd / al))
    res['D3 with noise S (no alpha) in dZ: Ito = alpha^3 sigma^2/phidot^2, noise = -alpha^2 sigma/phidot'] = \
        bool(sp.simplify(ito1 - al ** 3 * sig ** 2 / pd ** 2) == 0
             and sp.simplify(noise1 + al ** 2 * sig / pd) == 0)
    # drift: d alpha/dt = (phiddot/phidot) alpha - alpha^2/phidot (-3 (pd/alpha) dN/dt - alpha V')
    # phiddot/phidot = -H (eps1 + eps2/2), V' = -(phiddot + 3 H pd)
    pdd = -Hb * (e1 + e2 / 2) * pd
    Vp = -(pdd + 3 * Hb * pd)
    drift_t = pdd / pd * al - al ** 2 / pd * (-3 * pd / al * dNdt - al * Vp)
    drift_N = sp.simplify(drift_t / Hb)
    printed_drift = 3 * al * (printed - 1) + (-3 + e1 + e2 / 2) * al * (al ** 2 - 1)
    res['D2 drift of P0:825-826 follows from P0:812'] = bool(
        sp.simplify(drift_N - printed_drift) == 0)
    # background attractor alpha = 1 is a fixed point of the drift
    res['D2 alpha = 1 is a fixed point of the drift'] = bool(
        sp.simplify(printed_drift.subs(al, 1)) == 0)
    # linearisation: alpha = 1 + d, dN/dN_b = 1 + delta: matches CPT (P0:830)? record the
    # linear drift coefficient
    d = sp.Symbol('d')
    lin = sp.series(printed_drift.subs(al, 1 + d), d, 0, 2).removeO()
    res['_linear_drift_coefficient'] = str(sp.simplify(lin / d))
    # CPT: in the comoving (uniform-field) gauge Psi = alpha - 1 = -Rdot/H (P0:318); on
    # super-Hubble scales R'' = -(3 - eps1 - eps2) R' (P0:718 with k -> 0), so
    # Psi' = -R'' = (eps1 + eps2 - 3) Psi in e-folds
    res['D4 linearised lapse drift = (eps1 + eps2 - 3) of super-Hubble CPT (P0:830)'] = bool(
        sp.simplify(lin / d - (e1 + e2 - 3)) == 0)
    return res


def monte_carlo(seed=20261122, npaths=400000, alpha0=2.0, phid=1.0, sigma=0.1, T=0.01,
                nsub=200):
    rng = np.random.default_rng(seed)
    Z = np.full(npaths, phid / alpha0)
    dt = T / nsub
    times = [0.0]
    means = [alpha0]
    sems = [0.0]
    for n in range(nsub):
        al = phid / Z
        Z = Z + al * sigma * np.sqrt(dt) * rng.standard_normal(npaths)
        if (n + 1) % 20 == 0:
            a = phid / Z
            times.append((n + 1) * dt)
            means.append(float(a.mean()))
            sems.append(float(a.std() / np.sqrt(npaths)))
    times = np.array(times)
    means = np.array(means)
    sems = np.array(sems)
    pred5 = alpha0 ** 5 * sigma ** 2 / phid ** 2
    pred3 = alpha0 ** 3 * sigma ** 2 / phid ** 2
    slope = float((means[-1] - alpha0) / T)
    return {'seed': seed, 'npaths': npaths, 'alpha0': alpha0, 'phidot': phid, 'sigma': sigma,
            'T': T, 'nsub': nsub, 'times': times.tolist(), 'mean_alpha': means.tolist(),
            'sem': sems.tolist(), 'measured_drift': slope,
            'measured_drift_sem': float(sems[-1] / T),
            'pred_alpha5': pred5, 'pred_alpha3_P0': pred3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    res = symbolic()
    for kk, v in res.items():
        print('%-90s %s' % (kk, v))
    mc = monte_carlo()
    print('MC drift %.4e +- %.1e ; alpha^5 pred %.4e ; alpha^3 pred %.4e'
          % (mc['measured_drift'], mc['measured_drift_sem'], mc['pred_alpha5'],
             mc['pred_alpha3_P0']))
    # the second-order Ito-Taylor correction over T is O(T^2): estimate by halving T
    mc2 = monte_carlo(T=0.005, nsub=100, seed=20261123)
    print('MC drift (T/2) %.4e +- %.1e' % (mc2['measured_drift'], mc2['measured_drift_sem']))
    out = {'symbolic': res, 'mc': mc, 'mc_half_T': mc2}
    with open(os.path.join(args.out, 'langevin.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, HERE)
    import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    t = np.array(mc['times'])
    m = np.array(mc['mean_alpha']) - mc['alpha0']
    e = np.array(mc['sem'])
    ax.errorbar(t, m, yerr=2 * e, fmt='o', ms=3, label='Monte Carlo of $Z$ (2 s.e.)')
    ax.plot(t, mc['pred_alpha5'] * t, '-', label=r'Ito: $\alpha^5\sigma^2/\dot\phi^2$')
    ax.plot(t, mc['pred_alpha3_P0'] * t, '--', label=r'P0:817: $\alpha^3\sigma^2/\dot\phi^2$')
    ax.set_xlabel('$t$')
    ax.set_ylabel(r'$\langle\alpha\rangle-\alpha_0$')
    ax.set_title(r'$\alpha_0=2$, $\sigma=0.1$, $\dot\phi=1$', fontsize=9)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, 'fig_langevin_ito.png'), dpi=150)
    print('wrote', args.out)


if __name__ == '__main__':
    main()
