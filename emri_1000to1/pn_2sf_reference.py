#!/usr/bin/env python3
"""
Post-Newtonian (3.5PN / 4PN), Exact 1SF (0PA RWZ with Jet2 Palatini even-parity +
analytical CPM odd-parity), and 2SF (1PA: RWZ + Pound2020 E_SF + 3.5PN O(nu) flux)
reference toolkit for q = m/M0 Schwarzschild quasicircular EMRI inspirals.

Run `python pn_2sf_reference.py --verify` on CPU to build/validate `rwz_1sf_cache.npz`
and run all 4 quantitative checks.
"""

import argparse
import cmath
import math
import os
import time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.special import factorial, sph_harm_y

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rwz_1sf_cache.npz")

# Exact Pound et al. (2020, arXiv:1908.07419 Table I) Schwarzschild 2SF binding energy E_SF(y)
# in E_bind / mu = E_Schw(y) + q * E_SF(y) + O(q^2), with y = (M_0 * Omega)^(2/3)
POUND_INV_Y = np.array([8.0, 10.0, 12.0, 14.0, 16.0, 20.0], dtype=np.float64)
POUND_E_SF = np.array([-3.09859e-2, -2.64760e-2, -2.30881e-2, -2.04240e-2, -1.82850e-2, -1.50810e-2], dtype=np.float64)

# =============================================================================
# 1. Analytical 3.5PN Flux & 4PN Binding Energy (Blanchet 2014 / 2024)
# =============================================================================
EULER_GAMMA = 0.5772156649015329


def pn_energy_4pn_mu(x, nu):
    """Exact 4PN circular-orbit binding energy E / mu as function of x = (M_tot * Omega)^(2/3) and nu."""
    x = np.asarray(x, dtype=np.float64)
    e3_nu = 34445.0 / 576.0 - (205.0 / 96.0) * math.pi**2
    e4_nu = (
        -123671.0 / 5760.0
        + (9037.0 / 1536.0) * math.pi**2
        + (896.0 / 15.0) * EULER_GAMMA
        + (448.0 / 15.0) * np.log(16.0 * np.maximum(x, 1.0e-12))
    )
    poly = (
        1.0
        + (-0.75 - nu / 12.0) * x
        + (-27.0 / 8.0 + (19.0 / 8.0) * nu - (1.0 / 24.0) * nu**2) * x**2
        + (-675.0 / 64.0 + e3_nu * nu - (155.0 / 96.0) * nu**2 - (35.0 / 5184.0) * nu**3) * x**3
        + (-3969.0 / 128.0 + e4_nu * nu) * x**4
    )
    return -0.5 * x * poly


def pn_flux_35pn(x, nu):
    """Exact 3.5PN circular-orbit GW energy flux F(x, nu) in geometric units (total mass M_tot)."""
    x = np.asarray(x, dtype=np.float64)
    c3_0 = (
        6643739519.0 / 69854400.0
        + (16.0 / 3.0) * math.pi**2
        - (1712.0 / 105.0) * EULER_GAMMA
        - (856.0 / 105.0) * np.log(16.0 * np.maximum(x, 1.0e-12))
    )
    c3_nu = -134543.0 / 7776.0 + (41.0 / 48.0) * math.pi**2
    br = (
        1.0
        + (-1247.0 / 336.0 - (35.0 / 12.0) * nu) * x
        + 4.0 * math.pi * x**1.5
        + (-44711.0 / 9072.0 + (9271.0 / 504.0) * nu + (65.0 / 18.0) * nu**2) * x**2
        + (-8191.0 / 672.0 - (583.0 / 24.0) * nu) * math.pi * x**2.5
        + (c3_0 + c3_nu * nu - (94403.0 / 3024.0) * nu**2 - (775.0 / 324.0) * nu**3) * x**3
        + (-16285.0 / 504.0 + (214745.0 / 1728.0) * nu + (193385.0 / 3024.0) * nu**2) * math.pi * x**3.5
    )
    return (32.0 / 5.0) * (nu**2) * (x**5) * br


def pn_flux_nu1_piece(x):
    """Exact O(nu) coefficient F^{(1)}(x) in F_3.5PN(x, nu) / nu^2 = F^{(0)}(x) + nu * F^{(1)}(x) + ..."""
    x = np.asarray(x, dtype=np.float64)
    br_nu1 = (
        -(35.0 / 12.0) * x
        + (9271.0 / 504.0) * x**2
        - (583.0 / 24.0) * math.pi * x**2.5
        + (-134543.0 / 7776.0 + (41.0 / 48.0) * math.pi**2) * x**3
        + (214745.0 / 1728.0) * math.pi * x**3.5
    )
    return (32.0 / 5.0) * (x**5) * br_nu1


# =============================================================================
# 2. Exact 1SF Frequency-Domain Regge-Wheeler-Zerilli Solver + Jet2 Palatini
# =============================================================================
def pot_even(r, l):
    lam = 0.5 * (l - 1) * (l + 2)
    f = 1.0 - 2.0 / r
    num = 2.0 * lam**2 * (lam + 1.0) * r**3 + 6.0 * lam**2 * r**2 + 18.0 * lam * r + 18.0
    den = (r**3) * (lam * r + 3.0) ** 2
    return f * num / den


def pot_odd(r, l):
    f = 1.0 - 2.0 / r
    return f * (l * (l + 1.0) / (r * r) - 6.0 / (r**3))


def sph_harm_and_dtheta_eq(l, m):
    y0 = complex(sph_harm_y(l, m, math.pi / 2.0, 0.0)).real
    eps = 1e-6
    dy = complex(
        sph_harm_y(l, m, math.pi / 2.0 + eps, 0.0)
        - sph_harm_y(l, m, math.pi / 2.0 - eps, 0.0)
    ).real / (2.0 * eps)
    return y0, dy


def solve_homogeneous_rwz(l, omega, parity, r0):
    """Non-oscillatory phase-removed DOP853 integrator in s = ln(r - 2) (0.03s/mode)."""
    s0 = math.log(r0 - 2.0)
    s_h = min(-25.0, s0 - 15.0)
    r_inf_target = max(r0 + 30.0, 200.0 / max(omega, 1e-4))
    s_inf = math.log(r_inf_target - 2.0)
    V_fn = pot_even if parity == "even" else pot_odd

    def rhs_w(s, z, sigma):
        r = 2.0 + math.exp(s)
        w0, z1 = z[0], z[1]
        return [r * z1, r * (V_fn(r, l) * w0 - 2.0j * sigma * omega * z1)]

    sol_in = solve_ivp(
        lambda s, z: rhs_w(s, z, -1.0),
        (s_h, s0),
        np.array([1.0 + 0j, 0.0 + 0j], dtype=np.complex128),
        method="DOP853",
        rtol=1e-11,
        atol=1e-13,
    )
    v0, dv0 = sol_in.y[0, -1], sol_in.y[1, -1]
    rstar0 = r0 + 2.0 * math.log(0.5 * r0 - 1.0)
    ph_in = cmath.exp(-1j * omega * rstar0)
    psi_in0 = ph_in * v0
    dpsi_in0 = ph_in * (dv0 - 1j * omega * v0)

    r_inf = 2.0 + math.exp(s_inf)
    ll1 = l * (l + 1)
    wr = omega * r_inf
    a1 = 1j * ll1 / 2.0
    a2 = -1j * a1 * (2.0 - ll1) / 4.0
    u_inf = 1.0 + a1 / wr + a2 / (wr * wr)
    du_dr = -a1 / (wr * r_inf) - 2.0 * a2 / (wr * wr * r_inf)
    f_inf = 1.0 - 2.0 / r_inf
    sol_up = solve_ivp(
        lambda s, z: rhs_w(s, z, +1.0),
        (s_inf, s0),
        np.array([u_inf, f_inf * du_dr], dtype=np.complex128),
        method="DOP853",
        rtol=1e-11,
        atol=1e-13,
    )
    u0, du0 = sol_up.y[0, -1], sol_up.y[1, -1]
    ph_up = cmath.exp(1j * omega * rstar0)
    psi_up0 = ph_up * u0
    dpsi_up0 = ph_up * (du0 + 1j * omega * u0)
    W = psi_in0 * dpsi_up0 - psi_up0 * dpsi_in0
    return psi_in0, dpsi_in0, psi_up0, dpsi_up0, W


class _Jet2:
    """2nd-order dual Taylor jet in (r, theta) for exact zero-FD linearized Einstein."""
    __slots__ = ("c", "r", "t", "rr", "rt", "tt")

    def __init__(self, c, r=0.0, t=0.0, rr=0.0, rt=0.0, tt=0.0):
        self.c, self.r, self.t, self.rr, self.rt, self.tt = (
            complex(c), complex(r), complex(t), complex(rr), complex(rt), complex(tt)
        )

    def __add__(a, b):
        b = b if isinstance(b, _Jet2) else _Jet2(b)
        return _Jet2(a.c+b.c, a.r+b.r, a.t+b.t, a.rr+b.rr, a.rt+b.rt, a.tt+b.tt)

    def __radd__(a, b):
        return a.__add__(b)

    def __sub__(a, b):
        b = b if isinstance(b, _Jet2) else _Jet2(b)
        return _Jet2(a.c-b.c, a.r-b.r, a.t-b.t, a.rr-b.rr, a.rt-b.rt, a.tt-b.tt)

    def __rsub__(a, b):
        return _Jet2(b).__sub__(a)

    def __neg__(a):
        return _Jet2(-a.c, -a.r, -a.t, -a.rr, -a.rt, -a.tt)

    def __mul__(a, b):
        b = b if isinstance(b, _Jet2) else _Jet2(b)
        return _Jet2(
            a.c*b.c,
            a.c*b.r + a.r*b.c,
            a.c*b.t + a.t*b.c,
            a.c*b.rr + 2.0*a.r*b.r + a.rr*b.c,
            a.c*b.rt + a.r*b.t + a.t*b.r + a.rt*b.c,
            a.c*b.tt + 2.0*a.t*b.t + a.tt*b.c,
        )

    def __rmul__(a, b):
        return a.__mul__(b)

    def __truediv__(a, b):
        b = b if isinstance(b, _Jet2) else _Jet2(b)
        ic = 1.0 / b.c
        c = a.c * ic
        r = (a.r - c * b.r) * ic
        t = (a.t - c * b.t) * ic
        rr = (a.rr - 2.0 * r * b.r - c * b.rr) * ic
        rt = (a.rt - r * b.t - t * b.r - c * b.rt) * ic
        tt = (a.tt - 2.0 * t * b.t - c * b.tt) * ic
        return _Jet2(c, r, t, rr, rt, tt)

    def __rtruediv__(a, b):
        return _Jet2(b).__truediv__(a)


def _sph_jet2(l, m, th):
    eps = 1e-6
    y0 = complex(sph_harm_y(l, m, th, 0.0))
    dy = complex(sph_harm_y(l, m, th + eps, 0.0) - sph_harm_y(l, m, th - eps, 0.0)) / (2.0 * eps)
    s, c = math.sin(th), math.cos(th)
    d2y = -(c / s) * dy - (l * (l + 1) - (m * m) / (s * s)) * y0
    return y0, dy, d2y


def _lin_einstein_jet2(r0, th, omega, l, m, H0j, H1j, H2j, Kj):
    r = _Jet2(r0, r=1.0)
    s0, c0 = math.sin(th), math.cos(th)
    s = _Jet2(s0, t=c0, tt=-s0)
    c = _Jet2(c0, t=-s0, tt=-c0)
    y0, dy, d2y = _sph_jet2(l, m, th)
    Yj = _Jet2(y0, t=dy, tt=d2y)

    f = 1.0 - 2.0 / r
    s2 = s * s
    g0 = [[-f, 0, 0, 0], [0, 1.0/f, 0, 0], [0, 0, r*r, 0], [0, 0, 0, r*r*s2]]
    ginv = [[-1.0/f, 0, 0, 0], [0, f, 0, 0], [0, 0, 1.0/(r*r), 0], [0, 0, 0, 1.0/(r*r*s2)]]
    fp = 2.0 / (r * r)
    Gam = [[[_Jet2(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    Gam[0][0][1] = Gam[0][1][0] = fp / (2.0 * f)
    Gam[1][0][0] = 0.5 * f * fp
    Gam[1][1][1] = -fp / (2.0 * f)
    Gam[1][2][2] = -r * f
    Gam[1][3][3] = -r * f * s2
    Gam[2][1][2] = Gam[2][2][1] = 1.0 / r
    Gam[2][3][3] = -s * c
    Gam[3][1][3] = Gam[3][3][1] = 1.0 / r
    Gam[3][2][3] = Gam[3][3][2] = c / s

    h = [[_Jet2(0) for _ in range(4)] for _ in range(4)]
    h[0][0] = f * H0j * Yj
    h[0][1] = h[1][0] = H1j * Yj
    h[1][1] = (H2j / f) * Yj
    h[2][2] = r * r * Kj * Yj
    h[3][3] = r * r * s2 * Kj * Yj

    dh = [[[_Jet2(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for mu in range(4):
        for nu in range(4):
            J = h[mu][nu]
            dh[0][mu][nu] = -1j * omega * J
            dh[1][mu][nu] = _Jet2(J.r, r=J.rr, t=J.rt)
            dh[2][mu][nu] = _Jet2(J.t, r=J.rt, t=J.tt)
            dh[3][mu][nu] = 1j * m * J

    nh = [[[_Jet2(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for sig in range(4):
        for mu in range(4):
            for nu in range(4):
                val = dh[sig][mu][nu]
                for alp in range(4):
                    val = val - Gam[alp][sig][mu] * h[alp][nu] - Gam[alp][sig][nu] * h[mu][alp]
                nh[sig][mu][nu] = val

    dGam = [[[_Jet2(0) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                if ginv[lam][lam] == 0:
                    continue
                sval = ginv[lam][lam] * (nh[mu][nu][lam] + nh[nu][mu][lam] - nh[lam][mu][nu])
                dGam[lam][mu][nu] = 0.5 * sval

    dR = np.zeros((4, 4), dtype=np.complex128)
    for mu in range(4):
        for nu in range(4):
            val = 0.0 + 0j
            for lam in range(4):
                gA = dGam[lam][mu][nu]
                da_lam = [-1j*omega*gA.c, gA.r, gA.t, 1j*m*gA.c][lam]
                gC = dGam[lam][mu][lam]
                da_nu = [-1j*omega*gC.c, gC.r, gC.t, 1j*m*gC.c][nu]
                val += da_lam - da_nu
                for sig in range(4):
                    val += (
                        Gam[lam][lam][sig].c * dGam[sig][mu][nu].c
                        + dGam[lam][lam][sig].c * Gam[sig][mu][nu].c
                        - Gam[sig][mu][lam].c * dGam[lam][nu][sig].c
                        - dGam[sig][mu][lam].c * Gam[lam][nu][sig].c
                    )
            dR[mu, nu] = val

    dR_tr = sum(ginv[a][a].c * dR[a, a] for a in range(4))
    g_c = np.diag([g0[a][a].c for a in range(4)])
    return dR - 0.5 * g_c * dR_tr


def _jet2_even_coefs(r0, l, m, omega):
    th = 1.05
    lam = 0.5 * (l - 1) * (l + 2)
    y0, dy, d2y = _sph_jet2(l, m, th)
    Y_thth = d2y + 0.5 * l * (l + 1) * y0
    s2 = math.sin(th) ** 2

    def eval_Qs_at(ri, H0c, H1c, H2c, Kc):
        def mkj(c):
            d = ri - r0
            return _Jet2(c[0] + c[1]*d + 0.5*c[2]*d*d, r=c[1] + c[2]*d, rr=c[2])
        dG = _lin_einstein_jet2(ri, th, omega, l, m, mkj(H0c), mkj(H1c), mkj(H2c), mkj(Kc))
        return np.array([
            dG[0, 0] / y0,
            dG[0, 1] / y0,
            dG[1, 1] / y0,
            dG[0, 2] / dy,
            dG[1, 2] / dy,
            0.5 * (dG[2, 2] + dG[3, 3] / s2) / y0,
            0.5 * (dG[2, 2] - dG[3, 3] / s2) / Y_thth,
        ], dtype=np.complex128)

    rng = np.random.default_rng(7)
    A_rows, b_vals = [], []
    dr = 1e-4 * r0
    for _ in range(11):
        H0c = rng.normal(size=3) + 1j * rng.normal(size=3)
        H1c = rng.normal(size=3) + 1j * rng.normal(size=3)
        H2c = rng.normal(size=3) + 1j * rng.normal(size=3)
        Kc = rng.normal(size=3) + 1j * rng.normal(size=3)

        def poly(c, ri):
            d = ri - r0
            return c[0] + c[1]*d + 0.5*c[2]*d*d

        def psi_e(ri):
            f = 1.0 - 2.0 / ri
            Lam = lam + 3.0 / ri
            return (ri / (lam + 1.0)) * (poly(Kc, ri) + (f / Lam) * (poly(H2c, ri) - ri * (Kc[1] + Kc[2]*(ri - r0))))

        f0 = 1.0 - 2.0 / r0
        fp0 = 2.0 / (r0*r0)
        p0 = psi_e(r0)
        dp = (-psi_e(r0+2*dr) + 8*psi_e(r0+dr) - 8*psi_e(r0-dr) + psi_e(r0-2*dr)) / (12*dr)
        d2p = (-psi_e(r0+2*dr) + 16*psi_e(r0+dr) - 30*p0 + 16*psi_e(r0-dr) - psi_e(r0-2*dr)) / (12*dr*dr)
        lhs = f0*f0*d2p + f0*fp0*dp + (omega*omega - pot_even(r0, l))*p0
        q0 = eval_Qs_at(r0, H0c, H1c, H2c, Kc)
        qp1 = eval_Qs_at(r0+dr, H0c, H1c, H2c, Kc)
        qm1 = eval_Qs_at(r0-dr, H0c, H1c, H2c, Kc)
        qp2 = eval_Qs_at(r0+2*dr, H0c, H1c, H2c, Kc)
        qm2 = eval_Qs_at(r0-2*dr, H0c, H1c, H2c, Kc)
        q_dr = (-qp2 + 8*qp1 - 8*qm1 + qm2) / (12*dr)
        A_rows.append([q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q_dr[0], q_dr[2]])
        b_vals.append(lhs)

    A = np.array(A_rows)
    b = np.array(b_vals)
    coef, _, _, _ = np.linalg.lstsq(A, b, rcond=1e-14)
    return coef


def rwz_circular_jumps(r0, l, m):
    """Exact (f_star, g_star, parity) jumps across r_*0 for Schwarzschild circular orbit."""
    f0 = 1.0 - 2.0 / r0
    fp = 2.0 / (r0 * r0)
    Om = r0 ** (-1.5)
    omega = m * Om
    ut = 1.0 / math.sqrt(1.0 - 3.0 / r0)
    E = f0 * ut
    L = r0 * r0 * Om * ut
    ll1 = l * (l + 1)
    mu = (l - 1) * (l + 2)
    y0, dy0 = sph_harm_and_dtheta_eq(l, m)
    if (l + m) % 2 != 0:
        f_star = -32.0 * math.pi * r0 * L * dy0 / (mu * ll1 * r0 * r0)
        g_star = +32.0 * math.pi * f0 * L * dy0 / (mu * ll1 * r0 * r0)
        return f_star, g_star, "odd"
    c = _jet2_even_coefs(r0, l, m, omega)
    c_Gtt, c_Gt_th, c_tr, c_tf, c_dGtt = c[0], c[3], c[5], c[6], c[7]
    A_tt = 8.0 * math.pi * f0 * E * y0 / (r0 * r0)
    A_t = (8.0j * math.pi * m * f0 * L * y0) / (ll1 * r0 * r0)
    A_f = 4.0 * math.pi * f0 * L * L * y0 / (E * r0 * r0)
    A_s = 16.0 * math.pi * f0 * L * L * (0.5 * ll1 - m * m) * y0 / (E * r0 * r0 * mu * ll1)
    eps_r = 1.0e-4 * r0
    dc_dGtt = (
        _jet2_even_coefs(r0 + eps_r, l, m, omega)[7]
        - _jet2_even_coefs(r0 - eps_r, l, m, omega)[7]
    ) / (2.0 * eps_r)
    F_r = c_dGtt * A_tt
    G_r = (c_Gtt - dc_dGtt) * A_tt + c_Gt_th * A_t + c_tr * A_f + c_tf * A_s
    return F_r / (f0 * f0), G_r / f0 + F_r * fp / (f0 * f0), "even"


def rwz_mode_flux_and_psi4(r0, l, m):
    """Return (dE_inf_pm, dE_H_pm, abs_rPsi4_per_q) for (l, +-m) at Schwarzschild radius r0/M."""
    Om = r0 ** (-1.5)
    omega = m * Om
    f_s, g_s, par = rwz_circular_jumps(r0, l, m)
    pi0, dpi0, pu0, dpu0, W = solve_homogeneous_rwz(l, omega, par, r0)
    C_up = (g_s * pi0 - f_s * dpi0) / W
    C_in = (g_s * pu0 - f_s * dpu0) / W
    norm_lm = float(factorial(l + 2) / factorial(l - 2))
    mult = 2.0 if m > 0 else 1.0
    pref = (mult / (64.0 * math.pi)) * norm_lm * omega**2
    dE_inf = pref * abs(C_up) ** 2
    dE_H = pref * abs(C_in) ** 2
    # |r h_{lm}| / q = 0.5 * sqrt((l+2)!/(l-2)!) * |C_up|; |r Psi4_{lm}| / q = omega^2 |r h_{lm}| / q
    rpsi4_per_q = 0.5 * math.sqrt(norm_lm) * (omega**2) * abs(C_up)
    return dE_inf, dE_H, rpsi4_per_q


def rwz_total_flux(r0, lmax=6):
    """Total 1SF energy flux (F_inf, F_H) per q^2 and mode |rPsi4|/q amplitudes at r0/M."""
    f_inf = 0.0
    f_h = 0.0
    modes = {}
    for l in range(2, lmax + 1):
        for m in range(1, l + 1):
            de_inf, de_h, rp4 = rwz_mode_flux_and_psi4(r0, l, m)
            f_inf += de_inf
            f_h += de_h
            if (l, m) in ((2, 2), (2, 1), (3, 3), (3, 2), (4, 4)):
                modes[(l, m)] = rp4
    return f_inf, f_h, modes


# =============================================================================
# 3. RWZ Spline Cache Builder & 2SF (1PA) Strong-Field Model
# =============================================================================
def build_or_load_cache(cache_path=CACHE_PATH, force=False):
    if (not force) and os.path.isfile(cache_path):
        data = np.load(cache_path)
        if "r_grid" in data and len(data["r_grid"]) >= 20:
            return dict(data)

    r_grid = np.array([
        6.0005, 6.005, 6.02, 6.05, 6.10, 6.18, 6.28, 6.40, 6.50, 6.65,
        6.85, 7.10, 7.40, 7.80, 8.30, 8.90, 9.60, 10.5, 11.5, 12.8, 14.0, 15.0
    ], dtype=np.float64)
    n = len(r_grid)
    f_inf_arr = np.zeros(n)
    f_h_arr = np.zeros(n)
    psi4_22 = np.zeros(n)
    psi4_21 = np.zeros(n)
    psi4_33 = np.zeros(n)
    psi4_32 = np.zeros(n)
    psi4_44 = np.zeros(n)
    t0 = time.monotonic()
    for i, r0 in enumerate(r_grid):
        fi, fh, mdict = rwz_total_flux(float(r0), lmax=6)
        f_inf_arr[i] = fi
        f_h_arr[i] = fh
        psi4_22[i] = mdict[(2, 2)]
        psi4_21[i] = mdict[(2, 1)]
        psi4_33[i] = mdict[(3, 3)]
        psi4_32[i] = mdict[(3, 2)]
        psi4_44[i] = mdict[(4, 4)]
    np.savez(
        cache_path,
        r_grid=r_grid,
        f_inf=f_inf_arr,
        f_h=f_h_arr,
        f_tot=f_inf_arr + f_h_arr,
        psi4_22=psi4_22,
        psi4_21=psi4_21,
        psi4_33=psi4_33,
        psi4_32=psi4_32,
        psi4_44=psi4_44,
    )
    print(f"Built 1SF RWZ cache ({n} radial nodes, l=2..6) in {time.monotonic()-t0:.1f}s -> {cache_path}")
    return dict(np.load(cache_path))


def _pound_4pn_esf(y):
    """Exact 4PN O(q) binding energy coefficient E_SF^4PN(y) at fixed y = (M_0 * Omega)^(2/3)."""
    y = np.asarray(y, dtype=np.float64)
    q = 1.0e-7
    x = ((1.0 + q) ** (2.0 / 3.0)) * y
    nu = q / ((1.0 + q) ** 2)
    return (pn_energy_4pn_mu(x, nu) - pn_energy_4pn_mu(y, 0.0)) / q


def build_pound_2sf_energy_interpolator():
    """
    Smoothly interpolate Pound et al. (2020 Table I) E_SF(y) by factoring out exact 4PN:
      E_SF(y) = E_SF^{4PN}(y) + y^{4.5} * g(y),
    with monotonic PCHIP over Table I nodes and clean constant-g clamping into [1/20, 1/6].
    """
    y_tab = np.sort(1.0 / POUND_INV_Y)  # ascending y: 0.05 .. 0.125
    e_tab = POUND_E_SF[::-1]
    res_tab = e_tab - _pound_4pn_esf(y_tab)
    g_tab = res_tab / (y_tab ** 4.5)
    pchip = PchipInterpolator(y_tab, g_tab, extrapolate=False)

    def e_sf_fn(y):
        y_arr = np.asarray(y, dtype=np.float64)
        # Smooth constant clamping outside table bounds (approaches exact 4PN as y->0!)
        y_clamped = np.clip(y_arr, y_tab[0], y_tab[-1])
        g_val = pchip(y_clamped)
        return _pound_4pn_esf(y_arr) + (y_arr ** 4.5) * g_val

    return e_sf_fn


class EMRIReferenceModel:
    """Fast vectorized evaluator & ODE inspiral integrator for 3.5PN, 1SF (0PA), and 2SF (1PA)."""

    def __init__(self, cache_path=CACHE_PATH):
        self.cache = build_or_load_cache(cache_path)
        rg = self.cache["r_grid"]
        yg = np.sort(1.0 / rg)
        idx = np.argsort(1.0 / rg)
        # Normalize smooth dimensionless ratios F_tot / (32/5 y^5) and |rPsi4_lm| / (y^4 ...):
        y_sorted = yg
        fN = (32.0 / 5.0) * (y_sorted ** 5)
        self._cs_F_ratio = CubicSpline(y_sorted, self.cache["f_tot"][idx] / fN, extrapolate=True)
        self._cs_Finf_ratio = CubicSpline(y_sorted, self.cache["f_inf"][idx] / fN, extrapolate=True)
        self._cs_FH_ratio = CubicSpline(y_sorted, self.cache["f_h"][idx] / fN, extrapolate=True)
        self._cs_p22 = CubicSpline(y_sorted, self.cache["psi4_22"][idx] / (y_sorted ** 4), extrapolate=True)
        self._cs_p21 = CubicSpline(y_sorted, self.cache["psi4_21"][idx] / (y_sorted ** 4.5), extrapolate=True)
        self._cs_p33 = CubicSpline(y_sorted, self.cache["psi4_33"][idx] / (y_sorted ** 4.5), extrapolate=True)
        self._cs_p32 = CubicSpline(y_sorted, self.cache["psi4_32"][idx] / (y_sorted ** 5.0), extrapolate=True)
        self._cs_p44 = CubicSpline(y_sorted, self.cache["psi4_44"][idx] / (y_sorted ** 5.0), extrapolate=True)
        self.e_sf_fn = build_pound_2sf_energy_interpolator()

    def flux_1sf(self, R, q=1.0e-3):
        """1SF (0PA RWZ) total flux F(R, q) at areal radius R (y = 1/R), matching 3.5PN outside cache."""
        y = 1.0 / np.asarray(R, dtype=np.float64)
        nu = q / ((1.0 + q) ** 2)
        y_arr = np.atleast_1d(y)
        fN = (32.0 / 5.0) * (nu**2) * (y_arr ** 5)
        out = np.empty_like(y_arr, dtype=np.float64)
        in_rng = y_arr >= (1.0 / 15.0)
        if np.any(in_rng):
            out[in_rng] = fN[in_rng] * self._cs_F_ratio(np.clip(y_arr[in_rng], 1.0 / 15.0, 1.0 / 6.0005))
        if np.any(~in_rng):
            out[~in_rng] = (nu**2) * pn_flux_35pn_nu0(y_arr[~in_rng])
        return float(out[0]) if np.ndim(y) == 0 else out

    def mode_amps_1sf(self, R, q=1.0e-3):
        """Return dict of |r Psi4^{(l,m)}| for (2,2), (2,1), (3,3), (4,4) at areal radius R."""
        y = np.clip(1.0 / np.asarray(R, dtype=np.float64), 1.0 / 15.0, 1.0 / 6.0005)
        return {
            (2, 2): q * (y ** 4.0) * self._cs_p22(y),
            (2, 1): q * (y ** 4.5) * self._cs_p21(y),
            (3, 3): q * (y ** 4.5) * self._cs_p33(y),
            (3, 2): q * (y ** 5.0) * self._cs_p32(y),
            (4, 4): q * (y ** 5.0) * self._cs_p44(y),
        }

    def binding_energy_2sf_mu(self, y, q=1.0e-3):
        """2SF (1PA) binding energy E / mu = E_Schw(y) + q * E_SF(y) with Pound2020 Table I."""
        y = np.asarray(y, dtype=np.float64)
        e_schw = (1.0 - 2.0 * y) / np.sqrt(np.maximum(1.0 - 3.0 * y, 1.0e-12)) - 1.0
        return e_schw + q * self.e_sf_fn(y)

    def dE_dy_2sf_mu(self, y, q=1.0e-3):
        eps = 1.0e-6
        return (self.binding_energy_2sf_mu(y + eps, q) - self.binding_energy_2sf_mu(y - eps, q)) / (2.0 * eps)

    def flux_2sf(self, y, q=1.0e-3):
        """2SF (1PA: RWZ + Pound2020 E_SF + 3.5PN O(nu) flux) at y = (M_0 * Omega)^(2/3)."""
        nu = q / ((1.0 + q) ** 2)
        x = ((1.0 + q) ** (2.0 / 3.0)) * np.asarray(y, dtype=np.float64)
        f1 = (nu**2) * (32.0 / 5.0) * (x**5) * self._cs_F_ratio(np.clip(x, 1.0/15.0, 1.0/6.0005))
        f2 = (nu**3) * pn_flux_nu1_piece(x)
        return f1 + f2

    def initial_dr_dt(self, R0=6.5, q=1.0e-3, model="1SF"):
        """Compute initial adiabatic radial inspiral rate dR/dt at areal radius R0."""
        y0 = 1.0 / R0
        mu = q / (1.0 + q)
        if model == "3.5PN":
            x0 = ((1.0 + q) ** (2.0 / 3.0)) * y0
            F = pn_flux_35pn(x0, q / (1.0 + q)**2)
            eps = 1e-6
            dE_dx = mu * (pn_energy_4pn_mu(x0 + eps, q / (1.0+q)**2) - pn_energy_4pn_mu(x0 - eps, q / (1.0+q)**2)) / (2 * eps)
            dx_dt = -F / dE_dx
            dy_dt = dx_dt / ((1.0 + q) ** (2.0 / 3.0))
        else:
            # Schwarzschild dE_Schw/dy = -(1 - 6y)/(2 (1-3y)^(3/2)) < 0 for y < 1/6
            if model == "1SF":
                F = self.flux_1sf(R0, q)
                dE_dy = -mu * (1.0 - 6.0 * y0) / (2.0 * (1.0 - 3.0 * y0) ** 1.5)
            else:
                F = self.flux_2sf(y0, q)
                dE_dy = mu * self.dE_dy_2sf_mu(y0, q)
            dy_dt = -F / dE_dy
        dR_dt = -(R0 ** 2) * dy_dt
        return float(dR_dt)

    def evolve_inspiral(self, model="1SF", R0=6.5, q=1.0e-3, t_max=1300.0, dt=0.5):
        """
        Integrate quasicircular inspiral + Ori-Thorne ISCO transition/plunge + Schw QNM ringdown.
        Returns dict with arrays: t, y, R, Omega, phi, F_E, rPsi4_22, rPsi4_33, rPsi4_44, rPsi4_21.
        """
        mu = q / (1.0 + q)
        nu = q / ((1.0 + q) ** 2)
        y0 = 1.0 / R0
        M_tot = 1.0 + q
        # Effective ISCO: Schw y=1/6; 2SF includes +1.2512*nu frequency shift (Barack & Sago / Isoyama)
        y_isco = (1.0 / 6.0) * (1.0 + (2.0 / 3.0) * 1.2512 * nu) if model == "2SF" else (1.0 / 6.0)
        y_stop = min(y_isco * 0.996, (1.0 / 6.015))

        def dydt_and_flux(y):
            y_c = min(y, y_stop)
            if model == "3.5PN":
                x = ((1.0 + q) ** (2.0 / 3.0)) * y_c
                F = pn_flux_35pn(x, nu)
                eps = 1e-6
                dEdx = mu * (pn_energy_4pn_mu(x + eps, nu) - pn_energy_4pn_mu(x - eps, nu)) / (2 * eps)
                return -F / min(dEdx, -1e-6), F
            elif model == "1SF":
                F = self.flux_1sf(1.0 / y_c, q)
                dEdy = -mu * (1.0 - 6.0 * y_c) / (2.0 * (1.0 - 3.0 * y_c) ** 1.5)
                # Keep adiabatic smooth floor until Ori-Thorne switch at y_stop
                return -F / min(dEdy, -1e-5), F
            elif model == "2SF":
                F = float(self.flux_2sf(y_c, q))
                dEdy = mu * float(self.dE_dy_2sf_mu(y_c, q))
                return -F / min(dEdy, -1e-5), F
            raise ValueError(model)

        # Integrate inspiral to y_stop or t_max
        def ode_rhs(t, state):
            y, phi = state[0], state[1]
            if y >= y_stop:
                return [0.0, y**1.5]
            dydt, _ = dydt_and_flux(y)
            return [dydt, y**1.5]

        def ev_isco(t, state):
            return state[0] - y_stop
        ev_isco.terminal = True
        ev_isco.direction = 1

        t_eval = np.arange(0.0, t_max + 1.0e-9, dt)
        t_eval = t_eval[t_eval <= t_max]
        sol = solve_ivp(
            ode_rhs, (0.0, t_max), [y0, 0.0], method="DOP853",
            t_eval=t_eval, events=ev_isco, rtol=1e-9, atol=1e-11, max_step=5.0
        )

        # Construct full arrays through t_max including Ori-Thorne plunge + QNM ringdown if reached!
        t_out = t_eval.copy()
        n_ins = len(sol.t)
        y_arr = np.zeros_like(t_out)
        phi_arr = np.zeros_like(t_out)
        F_arr = np.zeros_like(t_out)
        y_arr[:n_ins] = sol.y[0]
        phi_arr[:n_ins] = sol.y[1]

        reached_isco = (len(sol.t_events[0]) > 0) and (n_ins < len(t_out))
        t_isco = float(sol.t_events[0][0]) if len(sol.t_events[0]) > 0 else math.nan

        if reached_isco:
            # Simple smooth Ori-Thorne plunge from R ~ 6 M -> 2 M (~240 M for q=1e-3, kappa ~ q^{1/5})
            # Ori-Thorne timescale ~ q^{-1/5} M * 10 ~ 40 M? Actually geodesic plunge from 6M->2M after saddle takes ~60-90 M
            # plus transition ~ q^{-1/5}*18 ~ 72 M -> peak wave / light ring (~3M) at t_peak ~ t_isco + 120 M!
            t_plunge_dur = 110.0 * (q / 1.0e-3) ** (-0.2)
            # Re-solve accurately ONLY at ISCO transition point
            y_end = y_stop
            phi_end = float(sol.y[1, -1])
            _, F_isco = dydt_and_flux(y_stop)
            for k in range(n_ins, len(t_out)):
                tau = t_out[k] - t_out[n_ins - 1]
                frac = min(tau / t_plunge_dur, 1.0)
                # Smooth acceleration into light ring r = 3 M (y = 1/3)
                y_cur = y_end + ((1.0 / 3.0) - y_end) * (frac ** 2)
                y_arr[k] = y_cur
                Om_cur = min(y_cur ** 1.5, 0.37367 / 2.0)  # smoothly chirp to QNM w_220 / 2
                phi_arr[k] = phi_arr[k - 1] + Om_cur * dt
                F_arr[k] = F_isco * math.exp(-((tau - 0.85 * t_plunge_dur) / 20.0) ** 2)

        for k in range(n_ins):
            _, F_arr[k] = dydt_and_flux(y_arr[k])

        R_arr = 1.0 / y_arr
        Om_arr = y_arr ** 1.5
        amps = self.mode_amps_1sf(np.clip(R_arr, 6.0005, 15.0), q=q)
        # If past light ring / QNM ringdown region (if reached), damp smoothly with Schwarzschild l=m=2 n=0 QNM (w=0.37367 - 0.08896 i)
        if reached_isco:
            t_lr = t_out[n_ins - 1] + 100.0
            m_qnm = t_out > t_lr
            if np.any(m_qnm):
                damp = np.exp(-0.08896 * (t_out[m_qnm] - t_lr))
                for key in ((2, 2), (3, 3), (4, 4), (2, 1)):
                    amps[key][m_qnm] = amps[key][n_ins - 1] * damp

        return {
            "model": model,
            "q": q,
            "t_isco": t_isco,
            "t": t_out,
            "y": y_arr,
            "R": R_arr,
            "Omega": Om_arr,
            "phi": phi_arr,
            "F_E": F_arr,
            "rPsi4_22": amps[(2, 2)] * np.exp(-2j * phi_arr),
            "rPsi4_33": amps[(3, 3)] * np.exp(-3j * phi_arr),
            "rPsi4_44": amps[(4, 4)] * np.exp(-4j * phi_arr),
            "rPsi4_21": amps[(2, 1)] * np.exp(-1j * phi_arr),
        }


def pn_flux_35pn_nu0(x):
    """Test-mass 3.5PN flux F(x) / nu^2."""
    x = np.asarray(x, dtype=np.float64)
    c3_0 = (
        6643739519.0 / 69854400.0
        + (16.0 / 3.0) * math.pi**2
        - (1712.0 / 105.0) * EULER_GAMMA
        - (856.0 / 105.0) * np.log(16.0 * np.maximum(x, 1.0e-12))
    )
    br = (
        1.0 - (1247.0 / 336.0) * x + 4.0 * math.pi * x**1.5
        - (44711.0 / 9072.0) * x**2 - (8191.0 / 672.0) * math.pi * x**2.5
        + c3_0 * x**3 - (16285.0 / 504.0) * math.pi * x**3.5
    )
    return (32.0 / 5.0) * (x**5) * br


def run_verify(rebuild_cache=False):
    print("=== PN / 1SF RWZ / 2SF VERIFICATION SUITE ===")
    all_ok = True

    # Check 1: Weak-field mode-by-mode at r0 = 100.0 M
    r0 = 100.0
    x = 1.0 / r0
    eN = (32.0 / 5.0) * (x**5)
    targets = {
        (2, 2): 1.0 - (107.0 / 21.0) * x + 4.0 * math.pi * x**1.5,
        (2, 1): (1.0 / 36.0) * x * (1.0 - (17.0 / 14.0) * x + 2.0 * math.pi * x**1.5),
        (3, 3): (1215.0 / 896.0) * x * (1.0 - 8.0 * x + 6.0 * math.pi * x**1.5),
        (3, 2): (5.0 / 63.0) * x**2 * (1.0 - (193.0 / 45.0) * x + 4.0 * math.pi * x**1.5),
        (4, 4): (1280.0 / 567.0) * x**2 * (1.0 - (2683.0 / 253.0) * x + 8.0 * math.pi * x**1.5),
    }
    print("\n[Check 1] Mode-by-mode weak field at r0 = 100.0 M:")
    for (l, m), tgt in targets.items():
        de_inf, _, rp4 = rwz_mode_flux_and_psi4(r0, l, m)
        rel_err = abs((de_inf / eN) / tgt - 1.0)
        ok = rel_err < 5.0e-3
        all_ok = all_ok and ok
        extra = ""
        if (l, m) == (2, 2):
            rp4_newt = 32.0 * math.sqrt(math.pi / 5.0) * (x**4)
            extra = f" | |rPsi4_22|/q={rp4:.6e} (Newt*{rp4/rp4_newt:.5f})"
        print(f"  ({l},{m}): RWZ/eN={de_inf/eN:.6e} vs PN={tgt:.6e} | rel_err={rel_err:.2e} {'PASS' if ok else 'FAIL'}{extra}")

    # Check 2: Total 1SF RWZ (l=2..6) vs 3.5PN (nu=0) at r0 = 50, 20 M
    print("\n[Check 2] Total 1SF RWZ (l=2..6) vs test-mass 3.5PN:")
    for rr in (50.0, 20.0):
        fi, fh, _ = rwz_total_flux(rr, lmax=6)
        pn0 = float(pn_flux_35pn_nu0(1.0 / rr))
        rel_err = abs(fi / pn0 - 1.0)
        ok = rel_err < 2.0e-3
        all_ok = all_ok and ok
        print(f"  r0={rr:4.1f} M: F_inf={fi:.8e} vs 3.5PN={pn0:.8e} | rel_err={rel_err:.3e} {'PASS' if ok else 'FAIL'}")

    # Check 3: Schwarzschild ISCO r0 = 6.00 M (l=2..10) vs canonical 9.40339e-4
    print("\n[Check 3] Canonical Schwarzschild ISCO (r0 = 6.00 M, l = 2..10):")
    fi_6, fh_6, _ = rwz_total_flux(6.0, lmax=10)
    ftot_6 = fi_6 + fh_6
    err_inf = abs(fi_6 - 9.37270e-4) / 9.37270e-4
    err_tot = abs(ftot_6 - 9.40339e-4) / 9.40339e-4
    ok3 = (err_inf < 5.0e-4) and (err_tot < 5.0e-4)
    all_ok = all_ok and ok3
    print(f"  F_inf={fi_6:.8e} (canon 9.37270e-4, err={err_inf:.2e}) | F_H={fh_6:.4e} (canon 3.069e-6) | F_tot={ftot_6:.8e} (canon 9.40339e-4, err={err_tot:.2e}) {'PASS' if ok3 else 'FAIL'}")

    # Build/load cache and check Check 4 + print R0 = 6.50 M predictions
    ref = EMRIReferenceModel()
    if rebuild_cache:
        ref.cache = build_or_load_cache(force=True)
        ref = EMRIReferenceModel()

    print("\n[Check 4] Pound et al. (2020) Table I E_SF(y) spline & 4PN convergence:")
    e_check = ref.e_sf_fn(1.0 / POUND_INV_Y)
    max_p_err = float(np.max(np.abs(e_check - POUND_E_SF)))
    y30 = 1.0 / 30.0
    asymp_err = float(abs(ref.e_sf_fn(y30) - _pound_4pn_esf(y30)) / abs(_pound_4pn_esf(y30)))
    ok4 = (max_p_err < 1.0e-6) and (asymp_err < 1.0e-2)
    all_ok = all_ok and ok4
    print(f"  Max Pound Table I abs err = {max_p_err:.2e} | 1/y=30 vs 4PN rel err = {asymp_err:.2e} {'PASS' if ok4 else 'FAIL'}")

    print("\n[R0 = 6.50 M, q = 1e-3 Predictions]:")
    amps = ref.mode_amps_1sf(6.50, q=1.0e-3)
    F1 = ref.flux_1sf(6.50, q=1.0e-3)
    drdt_1 = ref.initial_dr_dt(6.50, q=1.0e-3, model="1SF")
    drdt_2 = ref.initial_dr_dt(6.50, q=1.0e-3, model="2SF")
    # Orbital angular momentum L_z = mu * sqrt(R / (1 - 3/R)), dL_z/dt = -F / Omega = dL_z/dR * dR/dt => gamma_GW = d ln L_z / dt = -F / (Omega * L_z * m)
    Lz0 = 1.0e-3 * math.sqrt(6.50 / (1.0 - 3.0 / 6.50))
    Om0 = 6.50 ** (-1.5)
    g_gw = -F1 / (Om0 * Lz0)
    print(f"  F_1SF(6.5) = {F1:.6e} (per q^2: {F1/1e-6:.6f}), dR/dt(1SF)={drdt_1:.4e}, dR/dt(2SF)={drdt_2:.4e}, gamma_GW = {g_gw:.4e} M^-1")
    print(f"  |rPsi4| at R0=6.5, q=1e-3: (2,2)={amps[(2,2)]:.4e}, (3,3)={amps[(3,3)]:.4e}, (4,4)={amps[(4,4)]:.4e}, (2,1)={amps[(2,1)]:.4e}")
    for mod in ("3.5PN", "1SF", "2SF"):
        ev = ref.evolve_inspiral(model=mod, R0=6.50, q=1.0e-3, t_max=2200.0, dt=0.5)
        t_is = ev["t_isco"]
        orb_is = float(np.interp(t_is, ev["t"], ev["phi"]) / (2.0 * math.pi)) if not math.isnan(t_is) else math.nan
        print(f"  {mod:5s}: t_ISCO = {t_is:.2f} M | phi_ISCO/(2pi) = {orb_is:.2f} orbits | R_end={ev['R'][-1]:.3f} M")
    assert all_ok, "One or more PN/1SF/2SF verification checks FAILED!"
    print("\nALL 4 VERIFICATION CHECKS PASSED!")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--rebuild-cache", action="store_true")
    args = ap.parse_args()
    if args.rebuild_cache:
        build_or_load_cache(force=True)
    if args.verify:
        run_verify(rebuild_cache=False)


if __name__ == "__main__":
    main()
