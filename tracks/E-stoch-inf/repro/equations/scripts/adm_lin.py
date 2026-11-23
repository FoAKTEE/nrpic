"""Linearisation of the nonlinear ADM left-hand sides of arXiv:2401.08530 (P0:128-169) about
flat FLRW with a scalar field, for one plane wave exp(i k x), alpha_b = 1.

Time derivatives act on "jets": each time-dependent quantity is a symbol with a rate. The
background is parametrised by H(t) and p(t) = phidot_b / M (M the reduced Planck mass), with
dH/dt = -p^2/2 (Raychaudhuri), da/dt = a H; V, V', V'' follow from the Friedmann and
Klein-Gordon equations, so the background is exact for any H(t), p(t).

Conventions of P0 section II: ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i - beta^i dt)(dx^j - beta^j dt),
K_ij = -(1/2 alpha)(d_t gamma_ij + beta_i|j + beta_j|i), Pi = (phidot + beta^i d_i phi)/alpha,
alpha = 1 + Psi, beta_i = -a^2 B_,i, gamma_ij = a^2[(1 - 2 Phi) delta_ij + 2 E_,ij].
No downloaded file is read by this module.
"""
import sympy as sp

eps, x = sp.symbols('epsilon x', real=True)
k, M, H, a = sp.symbols('k M H a', positive=True)
NJ = 7
P = sp.symbols('p0:%d' % NJ)          # p_n = d^n p / dt^n, p = phidot_b / M
EX = sp.exp(sp.I * k * x)

BASE_RATES = {H: -P[0] ** 2 / 2, a: a * H}
for _n in range(NJ - 1):
    BASE_RATES[P[_n]] = P[_n + 1]


def jets(name, n=NJ):
    return sp.symbols('%s0:%d' % (name, n))


def add_jet_rates(rates, J):
    for i in range(len(J) - 1):
        rates[J[i]] = J[i + 1]
    return rates


def Dt(e, rates):
    """Total time derivative of an expression of jet symbols."""
    e = sp.sympify(e)
    out = 0
    for s in e.free_symbols:
        if s in rates:
            out += sp.diff(e, s) * rates[s]
    return out


# ----------------------------------------------------------------------------- background
phid = M * P[0]
eps1 = P[0] ** 2 / (2 * H ** 2)
eps2 = sp.simplify(-Dt(eps1, BASE_RATES) / (H * eps1))
eps3 = sp.simplify(-Dt(eps2, BASE_RATES) / (H * eps2))
V0 = 3 * M ** 2 * H ** 2 - phid ** 2 / 2
V1 = sp.expand(-(Dt(phid, BASE_RATES) + 3 * H * phid))
V2 = sp.simplify(Dt(V1, BASE_RATES) / phid)
sq2e1M = M * P[0] / H                  # sqrt(2 eps1) M_Pl, phidot_b > 0 (P0:920)

# ------------------------------------------------------------- perturbation amplitudes
PHI, PSI, BB, EE, DPHI = (jets(n) for n in ('Phi', 'Psi', 'B', 'E', 'dphi'))
PERT = {'Phi': PHI, 'Psi': PSI, 'B': BB, 'E': EE, 'dphi': DPHI}


def pert_rates():
    r = dict(BASE_RATES)
    for J in PERT.values():
        add_jet_rates(r, J)
    return r


def lin(e):
    """Truncate to first order in eps."""
    e = sp.expand(e)
    return e.subs(eps, 0) + eps * sp.diff(e, eps).subs(eps, 0)


def first_order(e):
    """First-order coefficient divided by exp(i k x)."""
    e1 = sp.diff(sp.expand(e), eps).subs(eps, 0)
    return sp.expand(sp.simplify(e1 / EX))


def zeroth_order(e):
    return sp.simplify(sp.expand(e).subs(eps, 0))


def build(delta_variant='gamma'):
    """Nonlinear ADM LHS of P0 (field, K, Kt_ij, H, M_i) to first order.

    delta_variant: 'gamma' uses gamma_ij in (1/3) alpha^|k_|k gamma_ij of the Kt equation;
    'delta' uses delta_ij literally as printed (P0:138, P1:346).
    Returns dict of first-order coefficients (jet expressions) and zeroth-order values.
    """
    r = pert_rates()
    f = lambda J: eps * J[0] * EX  # noqa: E731
    Phi, Psi, B, E, dphi = (f(J) for J in (PHI, PSI, BB, EE, DPHI))
    X = [x, None, None]

    def d(e, i):          # spatial derivative, only x dependence
        return sp.diff(e, x) if i == 0 else sp.S(0)

    def dt(e):
        return Dt(e, r)

    alpha = 1 + Psi
    g = sp.zeros(3, 3)
    for i in range(3):
        g[i, i] = a ** 2 * (1 - 2 * Phi)
    g[0, 0] += a ** 2 * 2 * d(d(E, 0), 0)
    g = g.applyfunc(lin)
    gi = sp.zeros(3, 3)
    for i in range(3):          # diagonal metric: inverse to first order
        gi[i, i] = lin(sp.series(1 / g[i, i], eps, 0, 2).removeO())
    beta_l = [lin(-a ** 2 * d(B, i)) for i in range(3)]
    beta_u = [lin(sum(gi[i, j] * beta_l[j] for j in range(3))) for i in range(3)]
    # Christoffels Gamma^l_ij
    Gam = [[[lin(sum(gi[l, m] * (d(g[j, m], i) + d(g[i, m], j) - d(g[i, j], m))
                     for m in range(3)) / 2) for j in range(3)] for i in range(3)]
           for l in range(3)]

    def cov_dd(s):     # D_i D_j of a scalar
        return [[lin(d(d(s, i), j) - sum(Gam[l][i][j] * d(s, l) for l in range(3)))
                 for j in range(3)] for i in range(3)]

    # Ricci R_ij
    Ric = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            e = 0
            for l in range(3):
                e += d(Gam[l][i][j], l) - d(Gam[l][i][l], j)
                for m in range(3):
                    e += Gam[l][l][m] * Gam[m][i][j] - Gam[l][j][m] * Gam[m][i][l]
            Ric[i, j] = lin(e)
    Rs = lin(sum(gi[i, j] * Ric[i, j] for i in range(3) for j in range(3)))
    # extrinsic curvature
    Db = [[lin(d(beta_l[j], i) - sum(Gam[l][i][j] * beta_l[l] for l in range(3)))
           for j in range(3)] for i in range(3)]
    inv_al = lin(sp.series(1 / alpha, eps, 0, 2).removeO())
    Kdd = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            Kdd[i, j] = lin(-inv_al / 2 * (dt(g[i, j]) + Db[i][j] + Db[j][i]))
    Ktr = lin(sum(gi[i, j] * Kdd[i, j] for i in range(3) for j in range(3)))
    Kt = (Kdd - g * Ktr / 3).applyfunc(lin)
    Ktu = (gi * Kt).applyfunc(lin)        # Kt^i_j
    # scalar field
    phidot_full = phid + dt(dphi)
    Pi = lin(inv_al * (phidot_full + sum(beta_u[i] * d(dphi, i) for i in range(3))))
    Vf = V0 + V1 * dphi
    dVf = V1 + V2 * dphi
    rho = lin(Pi ** 2 / 2 + Vf)                 # gradient squared is second order
    Ssc = lin(sp.Rational(3, 2) * Pi ** 2 - 3 * Vf)
    J = [lin(-Pi * d(dphi, i)) for i in range(3)]
    DDal = cov_dd(alpha)
    lap_al = lin(sum(gi[i, j] * DDal[i][j] for i in range(3) for j in range(3)))
    DDphi = cov_dd(dphi)
    lap_phi = lin(sum(gi[i, j] * DDphi[i][j] for i in range(3) for j in range(3)))
    # field equation P0:128
    field = lin(inv_al * (dt(Pi) + sum(beta_u[i] * d(Pi, i) for i in range(3))) - Ktr * Pi
                - lap_phi + dVf)      # alpha^|i phi_|i / alpha is second order
    # K equation P0:135-136 (beta^i K_,i second order)
    Keq = lin(dt(Ktr) + lap_al - alpha * (Rs + Ktr ** 2)
              - alpha / M ** 2 * (Ssc / 2 - sp.Rational(3, 2) * rho))
    # trace-free equation P0:137-139 (quadratic terms and beta terms are second order)
    Rt = (Ric - g * Rs / 3).applyfunc(lin)
    Kteq = {}
    for (i, j) in ((0, 0), (1, 1)):
        trace_term = (g[i, j] if delta_variant == 'gamma' else sp.KroneckerDelta(i, j))
        Kteq[(i, j)] = lin(dt(Kt[i, j]) + DDal[i][j] - lap_al * trace_term / 3
                           - alpha * (Rt[i, j] + Ktr * Kt[i, j] / 3))
    # constraints P0:165-166
    KtKt = lin(sum(Kt[i, j] * Ktu[j, i] * 0 for i in range(3) for j in range(3)))
    Ham = lin(Rs + sp.Rational(2, 3) * Ktr ** 2 - 2 / M ** 2 * rho)   # Kt Kt second order
    # momentum: Kt^j_i|j = d_j Kt^j_i + Gam^j_jl Kt^l_i - Gam^l_ji Kt^j_l (Kt first order)
    Mx = lin(sum(d(Ktu[j, 0], j) for j in range(3))
             + sum(Gam[j][j][l] * Ktu[l, 0] - Gam[l][j][0] * Ktu[j, l]
                   for j in range(3) for l in range(3))
             - sp.Rational(2, 3) * d(Ktr, 0) - J[0] / M ** 2)
    # pieces for BSSN checks
    detg = lin(g[0, 0] * g[1, 1] * g[2, 2])
    Xc = lin(sp.series(detg ** sp.Rational(-1, 3), eps, 0, 2).removeO())
    out = {
        'field': first_order(field), 'K': first_order(Keq),
        'Kt_xx': first_order(Kteq[(0, 0)]), 'Kt_yy': first_order(Kteq[(1, 1)]),
        'Ham': first_order(Ham), 'Mx': first_order(Mx),
        'bg_field': zeroth_order(field), 'bg_K': zeroth_order(Keq), 'bg_Ham': zeroth_order(Ham),
        # extras
        '_Ktr': Ktr, '_Kt': Kt, '_g': g, '_gi': gi, '_Kdd': Kdd, '_X': Xc, '_rho': rho,
        '_S': Ssc, '_J': J, '_Pi': Pi, '_alpha': alpha, '_lap_al': lap_al, '_Ric': Ric,
        '_Rs': Rs, '_DDal': DDal, '_rates': r, '_Gam': Gam,
    }
    return out


def paper_linear():
    """The linear equations as printed in P0:231-251 (Fourier: Delta -> -k^2/a^2)."""
    r = pert_rates()
    Phi, Psi, B, E, dphi = PHI[0], PSI[0], BB[0], EE[0], DPHI[0]
    Lap = -k ** 2 / a ** 2
    chi = -a ** 2 * (B - Dt(E, r))
    kappa = 3 * (Dt(Phi, r) + H * Psi) - Lap * chi
    drho = phid * Dt(dphi, r) + V1 * dphi - phid ** 2 * Psi
    dP = phid * Dt(dphi, r) - V1 * dphi - phid ** 2 * Psi
    Kp = Dt(kappa, r) + 2 * H * kappa + (Lap + 3 * BASE_RATES[H]) * Psi - (drho + 3 * dP) / (2 * M ** 2)
    S_tf = Dt(chi, r) + H * chi - Psi + Phi       # times (Delta/3 delta_ij - d_i d_j)
    Kt_xx = (-k ** 2 / 3 + k ** 2) * S_tf          # (1/3 delta nabla^2 - d_i d_j) -> k_i k_j - k^2/3
    Kt_yy = (-k ** 2 / 3) * S_tf
    fieldp = (Dt(Dt(dphi, r), r) + 3 * H * Dt(dphi, r) - Lap * dphi + V2 * dphi
              - phid * (kappa + Dt(Psi, r) - 3 * H * Psi) + 2 * Psi * V1)
    Hamp = 4 * Lap * Phi - 4 * H * kappa - 2 * drho / M ** 2
    Mxp = -2 * sp.I * k * (Lap * chi + kappa - sp.Rational(3, 2) * phid * dphi / M ** 2)
    return {'field': sp.expand(fieldp), 'K': sp.expand(Kp), 'Kt_xx': sp.expand(Kt_xx),
            'Kt_yy': sp.expand(Kt_yy), 'Ham': sp.expand(Hamp), 'Mx': sp.expand(Mxp),
            '_kappa': kappa, '_chi': chi, '_drho': drho}


def substitute_pert(expr, fields, rates, nmax=4):
    """Replace perturbation jets by expressions (and their time derivatives)."""
    sub = {}
    for name, J in PERT.items():
        e = fields[name]
        for n in range(nmax):
            sub[J[n]] = e
            e = Dt(e, rates)
    return sp.expand(sp.sympify(expr).xreplace(sub))


def ms_rule(Rj, Sj=None, rates=None, nmax=5):
    """Substitution R_n -> expression in (R0, R1, S jets) from the (sourced) MS equation
    Rddot + H (3 - eps2) Rdot + k^2/a^2 R = S (P0:277, P0:570)."""
    S0 = Sj[0] if Sj is not None else 0
    rr = dict(rates)
    rr[Rj[0]] = Rj[1]
    R2 = -H * (3 - eps2) * Rj[1] - k ** 2 / a ** 2 * Rj[0] + S0
    rr[Rj[1]] = R2
    sub = {Rj[2]: R2}
    e = R2
    for n in range(3, nmax + 1):
        e = sp.expand(Dt(e, rr))
        sub[Rj[n]] = e
    return sub, rr


def reduce_ms(expr, sub, nmax=5):
    e = sp.sympify(expr)
    for n in range(nmax, 1, -1):
        e = e.xreplace(sub)
    return e


def is_zero(e):
    e = sp.cancel(sp.together(sp.expand(e)))
    return e == 0, e
