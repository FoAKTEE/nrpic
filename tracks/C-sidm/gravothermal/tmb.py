"""Relativistic truncated Maxwell-Boltzmann cores (arXiv:2108.11967, "F21").

Reference solution (an ordinary differential equation and quadratures, no simulation) for
the equilibrium sequence and the instability criteria that F21 uses and that
arXiv:2601.17117 ("G26") cites for the onset of the dynamical instability.

Equations, with locators in kb-data/raw/arxiv/2108.11967/v2/src/main.tex:

    f(eps <= eps_c) = e^{mu/kT} (e^{-eps/kT} - e^{-eps_c/kT})            main.tex:111-116
    w = eps_c/kT,  alpha = mu/kT,  b = kT(R)/mc^2,  w(r) = alpha(r) - alpha(R),
    T(r) = T(R)/(1 - b w(r))                                               main.tex:118
    n, rho, u, p  = 4 sqrt2 pi g m^k (c/h)^3 e^{alpha(R)} {I_n, I_rho, I_u, (2/3) I_p}
                                                                           main.tex:122-129
    I_n, I_rho, I_u, I_p (b, w)                                            main.tex:131-139
    dM/dr = 4 pi r^2 rho,
    dw/dr = -(G/rc^2) ((1 - b w)/b) (4 pi p r^3 + M c^2)/(r c^2 - 2 G M)  main.tex:143-145
    r = zeta r^,  rho = (c^2/G zeta^2) rho^, ...,  M = (c^2 zeta/G) M^    main.tex:147-153
    v = sqrt(3p/rho) = c sqrt(2 I_p/I_rho),  gamma = 1 + p/u = 1 + (2/3) I_p/I_u
                                                                           main.tex:172-175
    <gamma> and gamma_cr (Chandrasekhar trial function xi = r e^Phi)      main.tex:208-219,
                                                                           main.tex:454-462
    E = M c^2, E_rest = int m n c^2 (1 - 2GM/rc^2)^{-1/2} d^3r, B = E_rest - E,
    eps = B/E_rest                                                         main.tex:242-250
    Z(r) = (1 + eps_c/mc^2)(1 - 2GM(R)/c^2 R)^{-1/2} - 1                  main.tex:255-257

Units. In the hatted units of main.tex:153 (G = c = 1, lengths in zeta) the TOV system is

    dM^/dr^ = 4 pi r^2 rho^,   dw/dr^ = -((1 - b w)/b) (4 pi p^ r^3 + M^)/(r^ (r^ - 2 M^)),

with rho^ = 4 sqrt2 pi I_rho, n^ = 4 sqrt2 pi I_n, u^ = 4 sqrt2 pi I_u, p^ = (8/3) sqrt2 pi I_p
(derived from main.tex:124-129 and :149 with h^3 = 8 pi^3 hbar^3; the derivation is in
README.md). The lapse follows from Tolman's law, e^{Phi(r)} = (1 - b w(r)) (1 - 2M^/R^)^{1/2};
it is consistent with dw/dr, since d ln(1 - b w)/dr = Phi'. (F21's printed expression for
e^{2 Phi}, main.tex:197, has the sign of the exponent and a factor 2 wrong; it is not used.)

Integration. A regular centre series at r0 = 1e-6 L, then DOP853 in r^ until w = w0/2,
then in s = w^{1/2} down to s = 0: in s every right-hand side is analytic at the surface
(rho ~ s^5, p ~ s^7), so R^ is located exactly. The quadratures (E_rest and the five
integrals of <gamma> and gamma_cr) are carried as extra components.

Integrals I(b, w): Gauss-Legendre in sigma with x = w sigma^2 (removes the x^{1/2} endpoint
singularity), n = 96 nodes; `integrals_quad` is the adaptive check.
"""

import math

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq, minimize_scalar

K4 = 4.0 * math.sqrt(2.0) * math.pi          # 4 sqrt2 pi
RTOL = 1e-12
ATOL = 1e-30

_NGL = 96
_sg, _wg = np.polynomial.legendre.leggauss(_NGL)
_SG = 0.5 * (_sg + 1.0)
_WG = 0.5 * _wg


# ---------------------------------------------------------------------------- equation of state
def integrals(b, w, scaled=False):
    """I_n, I_rho, I_u, I_p of main.tex:131-139 at a scalar w >= 0.

    scaled=True returns e^{-w} times the four integrals (the shape functions of the
    ratio quantities v and gamma for large w, without overflow)."""
    if w <= 0.0:
        return 0.0, 0.0, 0.0, 0.0
    beta = b / (1.0 - b * w)
    x = w * _SG * _SG
    jac = 2.0 * w * _SG * _WG                 # dx = 2 w sigma dsigma
    g = (np.exp(-x) - math.exp(-w)) if scaled else np.expm1(w - x)
    a = 1.0 + 0.5 * beta * x
    c = 1.0 + beta * x
    sa = np.sqrt(a)
    sx = np.sqrt(x)
    In = beta ** 1.5 * np.dot(jac, g * sa * c * sx)
    Ir = beta ** 1.5 * np.dot(jac, g * sa * c * c * sx)
    Iu = beta ** 2.5 * np.dot(jac, g * sa * c * x * sx)
    Ip = beta ** 2.5 * np.dot(jac, g * a * sa * x * sx)
    return In, Ir, Iu, Ip


def integrals_quad(b, w, scaled=False):
    """Adaptive-quadrature version of `integrals` (for tests)."""
    if w <= 0.0:
        return 0.0, 0.0, 0.0, 0.0
    beta = b / (1.0 - b * w)

    def g(x):
        return (math.exp(-x) - math.exp(-w)) if scaled else math.expm1(w - x)

    def fn(x):
        return g(x) * math.sqrt(1 + 0.5 * beta * x) * (1 + beta * x) * math.sqrt(x)

    def fr(x):
        return g(x) * math.sqrt(1 + 0.5 * beta * x) * (1 + beta * x) ** 2 * math.sqrt(x)

    def fu(x):
        return g(x) * math.sqrt(1 + 0.5 * beta * x) * (1 + beta * x) * x ** 1.5

    def fp(x):
        return g(x) * (1 + 0.5 * beta * x) ** 1.5 * x ** 1.5

    kw = dict(epsabs=0.0, epsrel=1e-13, limit=400)
    return (beta ** 1.5 * quad(fn, 0, w, **kw)[0], beta ** 1.5 * quad(fr, 0, w, **kw)[0],
            beta ** 2.5 * quad(fu, 0, w, **kw)[0], beta ** 2.5 * quad(fp, 0, w, **kw)[0])


def local(b, w):
    """Hatted n, rho, u, p and gamma = 1 + p/u at cutoff w (zero matter for w <= 0)."""
    In, Ir, Iu, Ip = integrals(b, max(w, 0.0))
    n, rho, u, p = K4 * In, K4 * Ir, K4 * Iu, (2.0 / 3.0) * K4 * Ip
    gam = 1.0 + (2.0 / 3.0) * Ip / Iu if Iu > 0 else 5.0 / 3.0
    return n, rho, u, p, gam


def v_over_c(b, w):
    """3D velocity dispersion sqrt(3p/rho)/c = sqrt(2 I_p/I_rho) (main.tex:172)."""
    _, Ir, _, Ip = integrals(b, w, scaled=True)
    return math.sqrt(2.0 * Ip / Ir)


def gamma_local(b, w):
    """gamma = 1 + (2/3) I_p/I_u (main.tex:173-175)."""
    _, _, Iu, Ip = integrals(b, w, scaled=True)
    return 1.0 + (2.0 / 3.0) * Ip / Iu


# ---------------------------------------------------------------------------- TOV system
NQ = 6   # quadratures: E_rest, P0, Pgamma, T1, T2, T3


def _quad_rates(r, M, w, b, loc):
    n, rho, u, p, gam = loc
    e2L = 1.0 / (1.0 - 2.0 * M / r)
    eL = math.sqrt(e2L)
    eP3 = (1.0 - b * max(w, 0.0)) ** 3        # e^{3 Phi} up to a constant factor
    wt = eP3 * eL * r * r
    return np.array([
        4.0 * math.pi * r * r * n * eL,                                   # E_rest
        wt * p,                                                           # P0
        wt * gam * p,                                                     # P_gamma
        wt * (16.0 * p + (e2L - 1.0) * (rho + p)) * (e2L - 1.0),          # T1
        eP3 * eL ** 3 * (8.0 * p + (e2L + 1.0) * (rho + p)) * p * r ** 4,  # T2
        eP3 * eL ** 5 * (rho + p) * p * p * r ** 6,                       # T3
    ])


def _dwdr(r, M, w, b, p):
    return -((1.0 - b * w) / b) * (4.0 * math.pi * p * r ** 3 + M) / (r * (r - 2.0 * M))


def _rhs_r(r, y, b):
    M, w = y[0], y[1]
    loc = local(b, w)
    dM = 4.0 * math.pi * r * r * loc[1]
    dw = _dwdr(r, M, w, b, loc[3])
    return np.concatenate(([dM, dw], _quad_rates(r, M, w, b, loc)))


def _rhs_s(s, y, b):
    r, M = y[0], y[1]
    w = s * s
    loc = local(b, w)
    dwdr = _dwdr(r, M, w, b, loc[3])
    drds = 2.0 * s / dwdr
    dM = 4.0 * math.pi * r * r * loc[1] * drds
    return np.concatenate(([drds, dM], _quad_rates(r, M, w, b, loc) * drds))


def solve(b, w0, dense=False):
    """Equilibrium of the sequence (b, w0). Returns a dict of the F21 table columns.

    With dense=True the dict also holds the two dense solutions for profiles."""
    n0, rho0, u0, p0, g0 = local(b, w0)
    k = ((1.0 - b * w0) / b) * (2.0 * math.pi / 3.0) * (rho0 + 3.0 * p0)   # w = w0 - k r^2
    L = math.sqrt(w0 / k)
    r0 = 1e-6 * L
    y0 = np.zeros(2 + NQ)
    y0[0] = 4.0 * math.pi / 3.0 * rho0 * r0 ** 3
    y0[1] = w0 - k * r0 * r0
    y0[2:] = _quad_rates(r0, y0[0], y0[1], b, (n0, rho0, u0, p0, g0)) * r0 / 3.0

    def ev_half(r, y, b):
        return y[1] - 0.5 * w0
    ev_half.terminal = True
    ev_half.direction = -1
    s1 = solve_ivp(_rhs_r, (r0, 1e6 * L), y0, method="DOP853", args=(b,), rtol=RTOL,
                   atol=ATOL, events=ev_half, dense_output=dense)
    if s1.status != 1:
        raise RuntimeError(f"no surface found for b={b}, w0={w0}: {s1.message}")
    yh = s1.y_events[0][0]
    z0 = np.concatenate(([s1.t_events[0][0], yh[0]], yh[2:]))
    sh = math.sqrt(yh[1])
    s2 = solve_ivp(_rhs_s, (sh, 0.0), z0, method="DOP853", args=(b,), rtol=RTOL, atol=ATOL,
                   dense_output=dense)
    R, M = s2.y[0, -1], s2.y[1, -1]
    Er, P0, Pg, T1, T2, T3 = s2.y[2:, -1]
    C = M / R
    gcr = (4.0 / 3.0 + T1 / (36.0 * P0) + (4.0 * math.pi / 9.0) * T2 / P0
           + (16.0 * math.pi ** 2 / 9.0) * T3 / P0)
    out = dict(b=b, w0=w0, E=M, Erest=Er, B=Er - M, eps=(Er - M) / Er, R=R, C=C,
               Z0=(1.0 / (1.0 - b * w0)) / math.sqrt(1.0 - 2.0 * C) - 1.0,
               ec0=b * w0 / (1.0 - b * w0), rho0=rho0, p0=p0, v0=math.sqrt(3.0 * p0 / rho0),
               gavg=Pg / P0, gcr=gcr, gamma0=g0)
    if dense:
        out["_sol"] = (s1, s2)
    return out


def profiles(b, w0, n=400):
    """Radial profiles r^, w, M^, rho^, p^, n^, v/c, gamma, kT/mc^2, eps_c/mc^2, e^Phi."""
    eq = solve(b, w0, dense=True)
    s1, s2 = eq["_sol"]
    ra = np.linspace(s1.t[0], s1.t[-1], n // 2)
    ya = s1.sol(ra)
    sb = np.linspace(s2.t[0], 0.0, n // 2 + 1)[1:]
    yb = s2.sol(sb)
    r = np.concatenate((ra, yb[0]))
    M = np.concatenate((ya[0], yb[1]))
    w = np.concatenate((ya[1], sb * sb))
    w = np.clip(w, 0.0, None)
    loc = np.array([local(b, wi) for wi in w])
    rho, p, nn, gam = loc[:, 1], loc[:, 3], loc[:, 0], loc[:, 4]
    with np.errstate(invalid="ignore", divide="ignore"):
        v = np.sqrt(np.where(rho > 0, 3.0 * p / np.where(rho > 0, rho, 1.0), 0.0))
    ePhi = (1.0 - b * w) * math.sqrt(1.0 - 2.0 * eq["C"])
    return dict(r=r, M=M, w=w, rho=rho, p=p, n=nn, v=v, gamma=gam, kT=b / (1.0 - b * w),
                ec=b * w / (1.0 - b * w), ePhi=ePhi, eq=eq)


# ---------------------------------------------------------------------------- sequence criteria
def maximum(b, key, lo, hi):
    """w0 in [lo, hi] maximising key (E, B or eps) at fixed b; returns the equilibrium."""
    res = minimize_scalar(lambda w0: -solve(b, w0)[key], bounds=(lo, hi), method="bounded",
                          options=dict(xatol=1e-9))
    return solve(b, res.x)


def gamma_root(b, lo, hi, target=None):
    """w0 where <gamma> = gamma_cr (target None) or gamma_cr = target (e.g. 5/3)."""
    if target is None:
        f = lambda w0: (lambda e: e["gavg"] - e["gcr"])(solve(b, w0))
    else:
        f = lambda w0: solve(b, w0)["gcr"] - target
    return solve(b, brentq(f, lo, hi, xtol=1e-12, rtol=1e-12))


def bracket_max(b, key, grid):
    vals = [solve(b, w)[key] for w in grid]
    i = int(np.argmax(vals))
    if i == 0 or i == len(grid) - 1:
        raise RuntimeError(f"maximum of {key} at the edge of the grid for b={b}")
    return grid[i - 1], grid[i + 1]


def bracket_root(fun, grid):
    vals = [fun(w) for w in grid]
    for i in range(len(grid) - 1):
        if vals[i] * vals[i + 1] <= 0:
            return grid[i], grid[i + 1]
    raise RuntimeError("no sign change on the grid")


# ---------------------------------------------------------------------------- Killing-energy form
def phase_space_moments(b, w):
    """n^, rho^, p^ by direct momentum integration of f(E) = e^{-E/b} - e^{-1/b}, E <= 1.

    Units mc^2 = 1, lapse normalised to e^{Phi(R)} = 1, so E_c = 1 and kT_inf = b; at a
    radius with cutoff w the lapse is e^Phi = 1 - b w and E = e^Phi (1 + p^2)^{1/2}.
    F21's distribution e^{alpha(R)} (e^{w-x} - 1) equals e^{alpha(R) + 1/b} f(E), so the
    moments must equal K4 I_n, K4 I_rho, (2/3) K4 I_p times e^{-1/b}."""
    ePhi = 1.0 - b * w
    pmax = math.sqrt((1.0 / ePhi) ** 2 - 1.0)

    def f(q):
        return math.exp(-ePhi * math.sqrt(1 + q * q) / b) - math.exp(-1.0 / b)

    kw = dict(epsabs=0.0, epsrel=1e-13, limit=400)
    nn = 4 * math.pi * quad(lambda q: f(q) * q * q, 0, pmax, **kw)[0]
    rho = 4 * math.pi * quad(lambda q: f(q) * math.sqrt(1 + q * q) * q * q, 0, pmax, **kw)[0]
    p = 4 * math.pi / 3 * quad(lambda q: f(q) * q ** 4 / math.sqrt(1 + q * q), 0, pmax, **kw)[0]
    return nn, rho, p


# ---------------------------------------------------------------------------- radial pulsation
def local_vec(b, w):
    """Vectorised `local`: hatted rho, p, gamma at an array of cutoffs w (w <= 0: vacuum)."""
    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    beta = (b / (1.0 - b * w))[:, None]
    ww = w[:, None]
    x = ww * _SG * _SG
    jac = 2.0 * ww * _SG * _WG
    g = np.expm1(ww - x)
    a = 1.0 + 0.5 * beta * x
    c = 1.0 + beta * x
    sx = np.sqrt(x)
    Ir = beta[:, 0] ** 1.5 * np.sum(jac * g * np.sqrt(a) * c * c * sx, axis=1)
    Iu = beta[:, 0] ** 2.5 * np.sum(jac * g * np.sqrt(a) * c * x * sx, axis=1)
    Ip = beta[:, 0] ** 2.5 * np.sum(jac * g * a * np.sqrt(a) * x * sx, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        gam = np.where(Iu > 0, 1.0 + (2.0 / 3.0) * Ip / np.where(Iu > 0, Iu, 1.0), 5.0 / 3.0)
    return K4 * Ir, (2.0 / 3.0) * K4 * Ip, gam


def structure(b, w0, n1=4000, n2=4000):
    """Fine table (r, M, w) of the equilibrium from both dense solutions, r ascending."""
    eq = solve(b, w0, dense=True)
    s1, s2 = eq["_sol"]
    ra = np.linspace(s1.t[0], s1.t[-1], n1)
    ya = s1.sol(ra)
    sb = np.linspace(s2.t[0], 0.0, n2)[1:]
    yb = s2.sol(sb)
    r = np.concatenate(([0.0], ra, yb[0]))
    M = np.concatenate(([0.0], ya[0], yb[1]))
    w = np.concatenate(([w0], ya[1], sb * sb))
    keep = np.concatenate(([True], np.diff(r) > 0))
    return eq, r[keep], M[keep], w[keep]


def fem_lowest(nodes, coeff, nmodes=1):
    """Rayleigh-Ritz (finite elements) for Chandrasekhar's radial pulsation equation.

    Sturm-Liouville form with zeta = r^2 e^{-Phi} xi (G = c = 1):
        -(P zeta')' + Q zeta = omega^2 W zeta,
        P = e^{3Phi+Lambda} gamma p / r^2,  W = e^{3Lambda+Phi} (rho + p) / r^2,
        Q = e^{3Phi+Lambda} [4 p'/r + 8 pi e^{2Lambda} p (rho + p) - p'^2/(rho + p)] / r^2,
    obtained by multiplying F21 main.tex:202-204 by e^{2Phi+Lambda} with xi = e^Phi zeta/r^2.
    zeta = r^3 eta(r), eta piecewise linear on the nodes (free at both ends: xi(0) = 0 is
    built in, Delta p = 0 at the surface is natural). eta = 1 is F21's trial function
    xi = r e^Phi. coeff(r) returns (M, rho, p, gamma, e^Phi) at the radii r (e^Phi up to a
    constant factor). Returns (omega^2 of the lowest nmodes, eigenvectors, trial Rayleigh
    quotient, Rayleigh(eta = 1)/(9 P0) = <gamma> - gamma_cr)."""
    from scipy.linalg import eigh
    xg, wg = np.polynomial.legendre.leggauss(5)
    h = np.diff(nodes)
    rq = (nodes[:-1, None] + 0.5 * h[:, None] * (xg[None, :] + 1.0)).ravel()
    wq = (0.5 * h[:, None] * wg[None, :]).ravel()
    tq = np.tile(0.5 * (xg + 1.0), len(h))            # local coordinate in [0, 1]
    el = np.repeat(np.arange(len(h)), len(xg))
    M, rho, p, gam, eP = coeff(rq)
    e2L = 1.0 / (1.0 - 2.0 * M / rq)
    eL = np.sqrt(e2L)
    dp = -(rho + p) * (M + 4 * np.pi * p * rq ** 3) / (rq * (rq - 2 * M))
    with np.errstate(invalid="ignore", divide="ignore"):
        q3 = np.where(rho + p > 0, dp ** 2 / np.where(rho + p > 0, rho + p, 1.0), 0.0)
    Pc = eP ** 3 * eL * gam * p / rq ** 2
    Wc = eL ** 3 * eP * (rho + p) / rq ** 2
    Qc = eP ** 3 * eL * (4 * dp / rq + 8 * np.pi * e2L * p * (rho + p) - q3) / rq ** 2
    n = len(nodes)
    A = np.zeros((n, n))
    B = np.zeros((n, n))
    hq = h[el]
    phi = (1.0 - tq, tq)                              # hats of the left and right node
    dphi = (-1.0 / hq, 1.0 / hq)
    for a in (0, 1):
        za = 3 * rq ** 2 * phi[a] + rq ** 3 * dphi[a]
        for c in (0, 1):
            zc = 3 * rq ** 2 * phi[c] + rq ** 3 * dphi[c]
            np.add.at(A, (el + a, el + c), wq * (Pc * za * zc + Qc * rq ** 6 * phi[a] * phi[c]))
            np.add.at(B, (el + a, el + c), wq * (Wc * rq ** 6 * phi[a] * phi[c]))
    one = np.ones(n)
    trial = one @ A @ one / (one @ B @ one)
    P0 = np.sum(wq * eP ** 3 * eL * p * rq ** 2)
    ev, vec = eigh(A, B, subset_by_index=[0, nmodes - 1])
    return ev, vec, trial, (one @ A @ one) / (9.0 * P0)


def pulsation(b, w0, N=600, gamma_mode="F21", nmodes=1):
    """Lowest omega^2 of the radial pulsation equation (main.tex:201-206) for the F21 model
    (b, w0), with gamma = 1 + p/u ("F21") or a fixed number (e.g. 5/3); see `fem_lowest`.
    Nodes: half uniform in r, half uniform in enclosed mass. Returns dict(omega2, trial,
    check = <gamma> - gamma_cr from the Rayleigh quotient of eta = 1, eq, eta)."""
    from scipy.interpolate import CubicSpline
    eq, rt, Mt, wt = structure(b, w0)
    R = eq["R"]
    Msp = CubicSpline(rt, Mt)
    wsp = CubicSpline(rt, wt)
    mf = Mt / Mt[-1]
    nodes = np.unique(np.concatenate((np.linspace(0.0, R, N // 2 + 1),
                                      np.interp(np.linspace(0.0, 1.0, N // 2 + 1), mf, rt))))

    def coeff(rq):
        w = np.clip(wsp(rq), 0.0, None)
        rho, p, gam = local_vec(b, w)
        if gamma_mode != "F21":
            gam = np.full_like(gam, float(gamma_mode))
        return Msp(rq), rho, p, gam, 1.0 - b * w

    ev, vec, trial, check = fem_lowest(nodes, coeff, nmodes)
    return dict(omega2=ev, trial=trial, check=check, eq=eq,
                eta=(nodes, vec[:, 0] / vec[np.argmax(np.abs(vec[:, 0])), 0]))
