"""Universal function of pressureless collapse with simultaneous bang time.

Every dust element of an LTB or quasi-spherical Szekeres model obeys
Rdot^2 = 2M/R - k (Lambda = 0) with R = 0 at t = 0 (bang time t_B = 0), so by scaling

    R(t, r) = M^(1/3) t^(2/3) g(lambda),   lambda = k t^(2/3) / M^(2/3),

with one function g of one variable. lambda > 0 is bound (cycloid angle eta in (0, 2 pi)):
    lambda = (eta - sin eta)^(2/3),   g = (1 - cos eta) / lambda,
turnaround at eta = pi (lambda = pi^(2/3)), crunch at eta = 2 pi (lambda = (2 pi)^(2/3)).
lambda < 0 is unbound (mu = -lambda):
    mu = (sinh eta - eta)^(2/3),      g = (cosh eta - 1) / mu.
g(0) = (9/2)^(1/3) is Einstein-de Sitter. This module returns l = ln g and its first two
derivatives: a Taylor series in lambda for |lambda| < LAM_SERIES (coefficients from
sym/gen_series.py, mpmath, 50 digits) and the parametric forms beyond. Because lambda of a
shell grows as t^(2/3) (lambda = lambda_i (t/t_i)^(2/3)), the whole evolution follows:
see model.py.
"""

import math

import numpy as np

__all__ = ["L_COEF", "L0", "LAM_SERIES", "LAM_TA", "LAM_CRUNCH", "ell", "ell_inverse", "solve_eta"]

# l(lambda) = sum_n L_COEF[n] lambda^n  (sym/gen_series.py 40)
L_COEF = (
    5.0135913225875802446e-1,
    -1.6509636244473133419e-1,
    -2.5309893971590516677e-2,
    -5.0714285714285714286e-3,
    -1.1336591362769132825e-3,
    -2.6912860406357752536e-4,
    -6.6379342596179330873e-5,
    -1.6811456209299169052e-5,
    -4.3413547726586921337e-6,
    -1.1379365749767731134e-6,
    -3.0180835705303981567e-7,
    -8.0816040388328311879e-8,
    -2.1812271983471973365e-8,
    -5.9264714412942531631e-9,
    -1.6194175283699847411e-9,
    -4.4468405593473691511e-10,
    -1.2263148360721215286e-10,
    -3.3945870149168795032e-11,
    -9.428037496391218124e-12,
    -2.6263326663123325479e-12,
    -7.3356850504892315074e-13,
    -2.0539113064340591996e-13,
    -5.7633621448734671508e-14,
    -1.6204637822508954153e-14,
    -4.5645564359227593626e-15,
    -1.2879210164593464974e-15,
    -3.6396060087550569157e-16,
    -1.0300149057627928013e-16,
    -2.9188488966240164078e-17,
    -8.2816785210217156792e-18,
    -2.3524886368874019104e-18,
    -6.6896964957396498472e-19,
    -1.9042563277769935856e-19,
    -5.4257231125013987596e-20,
    -1.5473144502028860968e-20,
    -4.4163745278419712103e-21,
    -1.2615343412471039818e-21,
    -3.6062788481497264751e-22,
    -1.0316425726842168959e-22,
    -2.9532006183676561791e-23,
)
L0 = L_COEF[0]                     # l(0) = ln (9/2)^(1/3)
_C = np.array((0.0,) + L_COEF[1:])  # l - l(0): no cancellation for small lambda
_C1 = np.array([n * c for n, c in enumerate(L_COEF)][1:])
_C2 = np.array([n * (n - 1) * c for n, c in enumerate(L_COEF)][2:])

LAM_SERIES = 0.5
LAM_TA = math.pi ** (2.0 / 3.0)
LAM_CRUNCH = (2.0 * math.pi) ** (2.0 / 3.0)


def _horner(c, x):
    out = np.zeros_like(x)
    for a in c[::-1]:
        out = out * x + a
    return out


def _x_minus_sin(x):
    x = np.asarray(x, dtype=float)
    out = x - np.sin(x)
    s = np.abs(x) < 0.5
    xs = x[s]
    acc = np.zeros_like(xs)
    for k in range(12, 0, -1):
        acc = acc * (-xs * xs) + 1.0 / math.factorial(2 * k + 1)
    out[s] = xs ** 3 * acc
    return out


def _sinh_minus_x(x):
    x = np.asarray(x, dtype=float)
    out = np.sinh(x) - x
    s = np.abs(x) < 0.5
    xs = x[s]
    acc = np.zeros_like(xs)
    for k in range(12, 0, -1):
        acc = acc * (xs * xs) + 1.0 / math.factorial(2 * k + 1)
    out[s] = xs ** 3 * acc
    return out


def solve_eta(target, bound):
    """eta with eta - sin eta = target (bound, eta in [0, 2 pi]) or sinh eta - eta = target
    (unbound); safeguarded Newton, vectorized."""
    y = np.asarray(target, dtype=float)
    if bound:
        lo, hi = np.zeros_like(y), np.full_like(y, 2 * math.pi)
        f, df = _x_minus_sin, lambda e: 1.0 - np.cos(e)
        e = np.clip(np.cbrt(6 * y), 0, 2 * math.pi)
        e = np.where(y > 1.0, np.clip(y + 0.0, 0.1, 2 * math.pi), e)
    else:
        lo = np.zeros_like(y)
        hi = np.maximum(np.cbrt(6 * y), np.arcsinh(y + 1) + 1) + 1.0
        f, df = _sinh_minus_x, lambda e: np.cosh(e) - 1.0
        e = np.where(y < 1, np.cbrt(6 * y), np.arcsinh(y) + 0.5)
    for _ in range(200):
        res = f(e) - y
        lo = np.where(res < 0, e, lo)
        hi = np.where(res > 0, e, hi)
        conv = (np.abs(res) <= 4e-16 * np.maximum(np.abs(y), 1e-300)) | \
               (hi - lo <= 4e-16 * np.maximum(np.abs(e), 1e-300))
        if np.all(conv):
            break
        d = df(e)
        en = e - res / np.where(d > 0, d, 1.0)
        bad = (en < lo) | (en > hi) | ~np.isfinite(en) | (d <= 0)
        en = np.where(bad, 0.5 * (lo + hi), en)
        en = np.where(conv, e, en)                 # converged entries never move again
        if np.all(en == e):                        # stagnation at round-off
            break
        e = en
    return e


def ell(lam):
    """(l - l(0), l', l'') at lambda (array), l = ln g, l(0) = L0 = ln (9/2)^(1/3); the
    first entry is the difference l - L0 so that small lambda loses no digits.
    Valid for lambda < (2 pi)^(2/3)."""
    lam = np.asarray(lam, dtype=float)
    l0 = np.empty_like(lam)
    l1 = np.empty_like(lam)
    l2 = np.empty_like(lam)
    s = np.abs(lam) < LAM_SERIES
    if np.any(s):
        x = lam[s]
        l0[s] = _horner(_C, x)
        l1[s] = _horner(_C1, x)
        l2[s] = _horner(_C2, x)
    b = (~s) & (lam > 0)
    if np.any(b):
        if np.any(lam[b] >= LAM_CRUNCH):
            raise ValueError("lambda beyond the crunch")
        x = lam[b]
        eta = solve_eta(x ** 1.5, True)
        ph = 2.0 * np.sin(0.5 * eta) ** 2
        sn, cs = np.sin(eta), np.cos(eta)
        l0[b] = np.log(ph) - np.log(x) - L0
        l1[b] = 1.5 * np.sqrt(x) * sn / ph ** 2 - 1.0 / x
        l2[b] = 0.75 / np.sqrt(x) * sn / ph ** 2 + 2.25 * x * (cs * ph - 2 * sn ** 2) / ph ** 4 + 1.0 / x ** 2
    u = (~s) & (lam < 0)
    if np.any(u):
        mu = -lam[u]
        eta = solve_eta(mu ** 1.5, False)
        ph = 2.0 * np.sinh(0.5 * eta) ** 2
        sh, ch = np.sinh(eta), np.cosh(eta)
        l0[u] = np.log(ph) - np.log(mu) - L0
        dl = 1.5 * np.sqrt(mu) * sh / ph ** 2 - 1.0 / mu
        l1[u] = -dl
        l2[u] = 0.75 / np.sqrt(mu) * sh / ph ** 2 + 2.25 * mu * (ch * ph - 2 * sh ** 2) / ph ** 4 + 1.0 / mu ** 2
    return l0, l1, l2


def ell_inverse(target, lam_max=LAM_TA):
    """lambda in (-inf, lam_max) with l(lambda) - L0 = target (l decreases monotonically)."""
    y = np.asarray(target, dtype=float)
    lo = np.full_like(y, -1e3)
    hi = np.full_like(y, lam_max * (1 - 1e-14))
    x = np.zeros_like(y)
    for _ in range(200):
        l0, l1, _ = ell(x)
        res = l0 - y
        # l decreasing: res > 0 -> root at larger lambda
        lo = np.where(res > 0, x, lo)
        hi = np.where(res < 0, x, hi)
        conv = (np.abs(res) <= 4e-16 * np.abs(y)) | \
               (hi - lo <= 4e-16 * np.maximum(np.abs(x), 1e-300))
        if np.all(conv):
            break
        xn = x - res / l1
        bad = (xn < lo) | (xn > hi) | ~np.isfinite(xn)
        xn = np.where(bad, 0.5 * (lo + hi), xn)
        xn = np.where(conv, x, xn)                 # converged entries never move again
        if np.all(xn == x):                        # stagnation at round-off
            break
        x = xn
    return x
