"""Item (e): the formulas of athenak/src/scalar_field/ (read only), transcribed by hand with
their line numbers, checked with sympy against the equations of arXiv:2512.14649 (P1) and
arXiv:2401.08530 (P0). Units of the code: G = c = 1, so M_Pl^-2 = 8 pi; K = -3H on the
background; Pi = n.d phi; Khat = K - 2 Theta; At_ij = chi Kt_ij (chi = X of the papers).
Writes code_map.json into --out.
"""
import argparse
import json
import os

import sympy as sp

RES = {}


def rec(key, ok, detail=''):
    RES[key] = {'pass': bool(ok), 'detail': str(detail)[:400]}
    print('%-80s %s %s' % (key, 'PASS' if ok else 'FAIL', str(detail)[:120]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t = sp.Symbol('t')
    H = sp.Function('H')(t)
    a = sp.Function('a')(t)
    Pi = sp.Function('Pi')(t)            # Pi_b of the code = phidot_b (alpha_b = 1)
    phi = sp.Function('phi')(t)
    Vp = sp.Function('Vp')(t)            # V'(phi_b(t))
    Mpl = 1 / sp.sqrt(8 * sp.pi)         # G = 1
    s, sig, k = sp.symbols('s sigma k', positive=True)
    # background equations of the code (scalar_field_noise.cpp:520-523, alpha_b = 1)
    bg = {sp.Derivative(a, t): a * H, sp.Derivative(Pi, t): -3 * H * Pi - Vp,
          sp.Derivative(H, t): -4 * sp.pi * Pi ** 2}     # dH/dt = -phidot^2/(2 Mpl^2)

    def D(e, n=1):
        for _ in range(n):
            e = sp.diff(e, t).subs(bg)
        return sp.simplify(e)
    eps1_def = Pi ** 2 / (2 * Mpl ** 2 * H ** 2)                 # P0:909
    eps1_code = 4 * sp.pi * Pi ** 2 / H ** 2                     # noise.cpp:496
    rec('eps1: code 4 pi Pi^2/H^2 (noise.cpp:496) = phidot^2/(2 Mpl^2 H^2) (P0:909)',
        sp.simplify(eps1_def - eps1_code) == 0)
    eps2_def = -D(eps1_code) / (H * eps1_code)                    # P1:171, P0:919
    eps2_code = 6 + 2 * Vp / (H * Pi) - 2 * eps1_code            # noise.cpp:497
    rec('eps2: code 6 + 2V\'/(H Pi) - 2 eps1 (noise.cpp:497) = -dln eps1/dN (P1:171)',
        sp.simplify(eps2_def - eps2_code) == 0)
    # Friedmann of the code: H = sqrt((8 pi/3)(Pi^2/2 + V)) (noise.cpp:488)
    rec('dH/dt = -eps1 H^2 (P0:910) with the code background', sp.simplify(
        D(H) + eps1_code * H ** 2) == 0)
    # window P1:503-505 and its derivatives (noise.cpp:533-534, 546-552)
    x = s * sp.log(sig * a * H / k)
    W = (1 + sp.tanh(x)) / 2
    W1 = D(W)
    W2 = D(W, 2)
    eps1c, eps2c = eps1_code, eps2_code
    dlnks = H * (1 - eps1c)                                       # noise.cpp:533
    d2lnks = H ** 2 * eps1c * (eps2c - 1 + eps1c)                 # noise.cpp:534
    sech2 = 1 / sp.cosh(x) ** 2
    w1 = sp.Rational(1, 2) * s * sech2 * dlnks                    # noise.cpp:549
    w2 = sp.Rational(1, 2) * sech2 * (s * d2lnks - 2 * s ** 2 * sp.tanh(x) * dlnks ** 2)  # :550
    d1 = sp.simplify((W1 - w1).rewrite(sp.exp))
    d2 = sp.simplify((W2 - w2).rewrite(sp.exp))
    rec('window first derivative (noise.cpp:549) = dW/dt of P1:504', d1 == 0, d1)
    rec('window second derivative (noise.cpp:550) = d2W/dt2 of P1:504', d2 == 0, d2)
    # d ln k_sigma/dt and its derivative
    rec('d ln(sigma a H)/dt = H (1 - eps1) (noise.cpp:533)',
        sp.simplify(D(sp.log(sig * a * H)) - dlnks) == 0)
    rec('d2 ln(sigma a H)/dt2 = H^2 eps1 (eps2 - 1 + eps1) (noise.cpp:534)',
        sp.simplify(D(sp.log(sig * a * H), 2) - d2lnks) == 0)
    # source S_R (P1:193, noise.cpp:551-552): R w2 + (2 R' + (3 - eps2) H R) w1, and the
    # sourced MS equation for W R (P1:188)
    R = sp.Function('R')(t)
    ms = {sp.Derivative(R, (t, 2)): -(3 - eps2c) * H * sp.Derivative(R, t) - k ** 2 / a ** 2 * R}
    WR = W * R
    lhs = sp.diff(WR, t, 2) + (3 - eps2c) * H * sp.diff(WR, t) + k ** 2 / a ** 2 * WR
    lhs = lhs.subs(ms)
    SR = R * sp.diff(W, t, 2) + (2 * sp.diff(R, t) + (3 - eps2c) * H * R) * sp.diff(W, t)
    rec('MS of W R = S_R (P1:188-193) [the residual used by the code]',
        sp.simplify((lhs - SR).subs(bg)) == 0)
    # kick factors (noise.cpp:557-559) against the BSSN sources P1:685-687 in G = 1 units
    Ps, Hs = sp.symbols('P H_s', positive=True)
    kp = (Pi / H).subs({Pi: Ps, H: Hs})
    e1s = eps1_code.subs({Pi: Ps, H: Hs})
    rec('kick Pi: Pi_b/H (noise.cpp:557) = sqrt(2 eps1) Mpl (P1:299, P1:687) for Pi_b > 0',
        sp.simplify(kp - sp.sqrt(2 * e1s) * Mpl) == 0)
    kn = (Pi / H).subs({Pi: -Ps, H: Hs})
    e1n = eps1_code.subs({Pi: -Ps, H: Hs})
    rec('kick Pi for Pi_b < 0 equals -sqrt(2 eps1) Mpl (code follows phidot_b/H of TH, not P1:299)',
        sp.simplify(kn + sp.sqrt(2 * e1n) * Mpl) == 0)
    RES['_note'] = ('kick K = -alpha_b eps1 (noise.cpp:558) = alpha_b S_K/S_R (P1:371, P1:685); '
                    'kick At = alpha_b eps1 (delta_ij/3 - qh_i qh_j/qh^2) (noise.cpp:559, 737-753) '
                    '= alpha_b S_A^BSSN/S_R (P1:686) with S_A = X_b S_Kt; Khat = K - 2 Theta '
                    '(rhs.cpp:137), Theta = 0 in the runs (use_z4c = false)')
    with open(os.path.join(args.out, 'code_map.json'), 'w') as fh:
        json.dump(RES, fh, indent=1)


if __name__ == '__main__':
    main()
