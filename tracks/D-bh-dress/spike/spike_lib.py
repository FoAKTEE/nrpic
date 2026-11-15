"""Semi-analytic reference for the dark-matter spike of an adiabatically grown
Schwarzschild black hole (Sadeghian, Ferrer & Will 2013, arXiv:1305.2619, "SFW").

Everything here is a reference solution (decision 0010): ordinary quadratures and
root finding, no time evolution.  Units inside the black-hole functions are
G = c = m_BH = 1 ("BH units").  The Hernquist halo uses G = M = a = 1 ("H units")
plus the compactness kappa = G M / (a c^2).

Conventions (SFW section III.B):
  E      relativistic specific energy, -u_t
  L      specific angular momentum, u_phi of the equatorial orbit
  V(r)   = E^2 - (1 - 2/r)(1 + L^2/r^2) = (dr/dtau)^2
  L_c(E) capture angular momentum, SFW eq. (3.15)
  rho    rest-mass density measured by the static observer, rho = sqrt(-g_00) J^0

Radial action.  The canonical adiabatic invariant is I_r = oint u_r dr with the covariant
u_r = sqrt(V)/(1 - 2/r).  SFW eq. (3.19) and its dimensionless form (4.13) omit the factor
1/(1 - 2/r); 1707.06302 (kerrdm.tex, footnote in sec. "Growth from a cuspy Hernquist
profile") says so.  Both versions are provided: action="canonical" (correct) and
action="sfw" (as printed in SFW, to reproduce their curves).
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import RegularGridInterpolator

# ------------------------------------------------------------------------------------
# physical constants (SI / IAU nominal values)
GM_SUN = 1.32712440018e20          # m^3 s^-2
C_SI = 299792458.0                 # m s^-1
PC_M = 3.0856775814913673e16       # m
GEV_J = 1.602176634e-10            # J
RG_SUN_PC = GM_SUN / C_SI**2 / PC_M            # G M_sun / c^2 in pc
MSUN_KG = GM_SUN / 6.6743e-11
MSUN_PC3_TO_GEV_CM3 = MSUN_KG * C_SI**2 / GEV_J / (PC_M * 100.0) ** 3
KMS = 1.0e3 / C_SI                 # 1 km/s in units of c

_GL_N = 96
_GL_X, _GL_W = leggauss(_GL_N)
_ETA = 0.5 * np.pi * (_GL_X + 1.0)           # nodes on [0, pi]
_ETA_W = 0.5 * np.pi * _GL_W
_SIN2 = np.sin(_ETA) ** 2


# ------------------------------------------------------------------------------------
# Schwarzschild geodesics (BH units)
def Lc2(E):
    """Capture (separatrix) angular momentum squared, SFW eq. (3.15); E in [sqrt(8/9), 1]."""
    E = np.asarray(E, dtype=float)
    q = np.clip(9.0 * E * E - 8.0, 0.0, None)
    return 32.0 / (36.0 * E**2 - 27.0 * E**4 - 8.0 + E * q**1.5)


def Emin_sfw(r):
    """SFW eq. (3.17): lowest energy of a non-captured bound particle at radius r."""
    r = np.asarray(r, dtype=float)
    return np.where(r >= 6.0, (1 + 2 / r) / np.sqrt(1 + 6 / r), (1 - 2 / r) / np.sqrt(1 - 3 / r))


def Lmax2(r, E):
    """L^2 at which V(r) = 0."""
    return r * r * (E * E / (1.0 - 2.0 / r) - 1.0)


def Ls2(E):
    """L^2 of the stable circular orbit of energy E (largest L of a bound orbit)."""
    # circular orbits: E^2 = (1-2u)^2/(1-3u), L^2 = 1/(u(1-3u)); stable branch u < 1/6
    E = np.asarray(E, dtype=float)
    lo = np.zeros_like(E) + 1e-300
    hi = np.full_like(E, 1.0 / 6.0)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        Ec2 = (1 - 2 * mid) ** 2 / (1 - 3 * mid)        # decreasing in u on the stable branch
        go = Ec2 > E * E
        lo = np.where(go, mid, lo)
        hi = np.where(go, hi, mid)
    u = 0.5 * (lo + hi)
    return 1.0 / (u * (1 - 3 * u))


def bh_roots(E, L2):
    """Turning points r_a >= r_p >= r_3 of V = 0 for a bound, non-captured orbit.

    V(1/u) = p(u) = 2 L^2 u^3 - L^2 u^2 + 2u - (1 - E^2).  Roots u_a < u_p < u_3 found by
    vectorized bisection between the extrema of p (no Newton polish: it is unstable at
    the double root of the separatrix orbit).
    Returns (r_a, r_p, r_3, ok) with ok False where the orbit is captured or unbound.
    """
    E = np.asarray(E, dtype=float)
    L2 = np.asarray(L2, dtype=float)
    E, L2 = np.broadcast_arrays(E, L2)
    b = 1.0 - E * E
    disc = L2 * L2 - 12.0 * L2
    ok = (disc > 0) & (b > 0)
    sd = np.sqrt(np.where(ok, disc, 0.0))
    L2s = np.where(ok, L2, 1.0)
    um = (L2s - sd) / (6.0 * L2s)
    up = (L2s + sd) / (6.0 * L2s)

    def p(u):
        return 2 * L2s * u**3 - L2s * u**2 + 2 * u - b

    ok &= (p(um) > 0) & (p(up) < 0)

    def bisect(lo, hi, rising):
        lo = lo.copy(); hi = hi.copy()
        for _ in range(110):
            mid = 0.5 * (lo + hi)
            s = p(mid)
            pos = (s > 0) if rising else (s < 0)
            hi = np.where(pos, mid, hi)
            lo = np.where(pos, lo, mid)
        return 0.5 * (lo + hi)

    ua = bisect(np.zeros_like(um), um, True)
    upp = bisect(um, up, False)
    u3 = bisect(up, np.maximum(up * 4.0, 1.0), True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 / ua, 1.0 / upp, 1.0 / u3, ok


def bh_action_period(E, L2, action="canonical"):
    """Radial action I_r = oint u_r dr (BH units) and coordinate-time radial period T_r.

    action = "canonical": u_r = sqrt(V)/(1-2/r);  "sfw": sqrt(V) (SFW eq. 3.19 as printed).
    """
    ra, rp, r3, ok = bh_roots(E, L2)
    ra = np.where(ok, ra, 10.0); rp = np.where(ok, rp, 5.0); r3 = np.where(ok, r3, 1.0)
    E = np.broadcast_to(E, ra.shape)
    half = 0.5 * (ra - rp)
    r = rp[..., None] + half[..., None] * (1.0 - np.cos(_ETA))
    b = (1.0 - E * E)[..., None]
    g = np.sqrt(b * (r - r3[..., None]) / r**3)            # sqrt(V)/sqrt((ra-r)(r-rp))
    lapse2 = 1.0 - 2.0 / r
    if action == "canonical":
        Iint = (_SIN2 * g / lapse2) @ _ETA_W
    elif action == "sfw":
        Iint = (_SIN2 * g) @ _ETA_W
    else:
        raise ValueError(action)
    I = 2.0 * half**2 * Iint
    T = 2.0 * E * ((1.0 / (lapse2 * g)) @ _ETA_W)          # 2 int E dr/((1-2/r) sqrt V)
    return np.where(ok, I, np.nan), np.where(ok, T, np.nan), ok


def newton_action(eps, L):
    """Kepler radial action 2 pi (1/sqrt(2 eps) - L), BH units, eps = binding energy."""
    return 2.0 * np.pi * (1.0 / np.sqrt(2.0 * eps) - L)


# ------------------------------------------------------------------------------------
# Hernquist halo (H units: G = M = a = 1)
def hernquist_ftilde_delta(delta):
    """Dimensionless ergodic Hernquist DF f~(eps) of SFW eq. (4.3), as a function of
    delta = 1 - eps (accurate for delta -> 0 and for eps -> 0)."""
    d = np.asarray(delta, dtype=float)
    e = 1.0 - d
    out = np.zeros_like(d)
    small = e < 1e-3
    big = (~small) & (d > 0)
    eb, db = e[big], d[big]
    asn = np.arctan2(np.sqrt(eb), np.sqrt(db))          # arcsin(sqrt(eps))
    br = (1 - 2 * eb) * (8 * eb**2 - 8 * eb - 3) + 3 * asn / np.sqrt(eb * db)
    out[big] = np.sqrt(eb) / db**2 * br
    es = np.clip(e[small], 0.0, None)
    out[small] = np.sqrt(es) * (25.6 * es**2 - (16.0 - 48.0 / 35.0) * es**3) / (1 - es) ** 2
    return out


def hernquist_orbit_from_La(L, xa):
    """Hernquist orbit with angular momentum L and apocentre xa (H units).
    Returns delta = 1 - eps, pericentre xp, third (negative) root xn and I_r."""
    L = np.asarray(L, dtype=float); xa = np.asarray(xa, dtype=float)
    L2 = L * L
    delta = xa / (1 + xa) + L2 / (2 * xa * xa)
    eps = 1.0 - delta
    S = L2 * (1 + xa) / (2 * xa * xa * eps)                 # x_p + x_n
    P = -L2 / (2 * eps * xa)                                # x_p * x_n
    xp = 0.5 * (S + np.sqrt(S * S - 4 * P))
    xn = P / xp
    half = 0.5 * (xa - xp)
    x = xp[..., None] + half[..., None] * (1.0 - np.cos(_ETA))
    g = np.sqrt(2 * eps[..., None] * (x - xn[..., None]) / (x * x * (1 + x)))
    I = 2.0 * half**2 * ((_SIN2 * g) @ _ETA_W)
    return delta, xp, xn, I


def hernquist_xc(L):
    """Circular-orbit radius for angular momentum L: x^{3/2} = L (1 + x) (monotonic),
    by bisection in ln x."""
    L = np.asarray(L, dtype=float)
    lo = np.full_like(L, -80.0); hi = np.full_like(L, 60.0)
    lnL = np.log(L)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        h = 1.5 * mid - np.log1p(np.exp(mid)) - lnL
        hi = np.where(h > 0, mid, hi)
        lo = np.where(h > 0, lo, mid)
    return np.exp(0.5 * (lo + hi))


class HernquistInverse:
    """Table of delta(L, I_r) for the Hernquist potential: the inverse of the radial
    action at fixed angular momentum, built from orbits parametrized by (L, x_a)."""

    def __init__(self, logL_range=(-12.0, 0.0), nL=481, nS=900, logs_range=(-9.0, 13.0),
                 logI_range=(-14.0, 3.0), nI=1400, xa_max=1.0e10):
        self.logL = np.linspace(*logL_range, nL)
        L = 10.0**self.logL
        xc = hernquist_xc(L)
        s = 10.0 ** np.linspace(*logs_range, nS)
        xa = np.minimum(xc[:, None] * (1.0 + s[None, :]), xa_max)
        delta, xp, xn, I = hernquist_orbit_from_La(np.broadcast_to(L[:, None], xa.shape), xa)
        self.logI = np.linspace(*logI_range, nI)
        tab = np.full((nL, nI), np.nan)
        lI = np.log10(I)
        ld = np.log10(delta)
        for k in range(nL):
            good = np.isfinite(lI[k]) & np.isfinite(ld[k]) & (delta[k] < 1.0 - 1e-13)
            li, dd = lI[k][good], ld[k][good]
            if not np.all(np.diff(li) > 0):
                order = np.argsort(li); li, dd = li[order], dd[order]
            inside = (self.logI >= li[0]) & (self.logI <= li[-1])
            tab[k, inside] = np.interp(self.logI[inside], li, dd)
        self.tab = tab
        self.Irange = (lI.min(axis=1), lI.max(axis=1))
        self.interp = RegularGridInterpolator((self.logL, self.logI), tab, method="cubic",
                                              bounds_error=False, fill_value=np.nan)
        self.interp_lin = RegularGridInterpolator((self.logL, self.logI), tab,
                                                  method="linear", bounds_error=False,
                                                  fill_value=np.nan)

    def delta(self, L, I, method="cubic"):
        pts = np.stack([np.log10(L), np.log10(I)], axis=-1)
        f = self.interp if method == "cubic" else self.interp_lin
        return 10.0 ** f(pts)


def hernquist_delta_direct(L, I, tol=1e-14):
    """Direct inversion of I_r(L, x_a) = I by bisection in log x_a (scalar check)."""
    xc = float(hernquist_xc(np.array([L]))[0])
    lo, hi = np.log(xc * (1 + 1e-12)), np.log(xc * 1e16)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        _, _, _, Im = hernquist_orbit_from_La(np.array([L]), np.array([np.exp(mid)]))
        if Im[0] > I:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    d, _, _, _ = hernquist_orbit_from_La(np.array([L]), np.array([np.exp(0.5 * (lo + hi))]))
    return float(d[0])


# ------------------------------------------------------------------------------------
class SpikeModel:
    """Adiabatic growth of a black hole of mass m inside a Hernquist halo (M, a).

    final DF:  f(E, L) = A f~_H(eps'(E, L)),  A = M / (sqrt2 (2pi)^3 (G M a)^{3/2}),
    eps' from I_r^H(eps', L) = I_r^BH(E, L) (L conserved), SFW section IV.
    """

    def __init__(self, M_sun=1e12, a_pc=2.0e4, m_sun=4e6, table=None):
        self.M, self.a, self.m = M_sun, a_pc, m_sun
        self.kappa = M_sun * RG_SUN_PC / a_pc               # G M / (a c^2)
        self.mt = m_sun / M_sun
        self.rg_pc = m_sun * RG_SUN_PC                      # G m / c^2
        self.conv = np.sqrt(self.kappa) * self.mt           # BH action units -> H units
        self.table = table if table is not None else HernquistInverse()
        # rho = P * Integral / (r - 2) in BH units, P in Msun/pc^3
        self.P = M_sun / (np.sqrt(2.0) * (2 * np.pi) ** 2 * self.kappa**1.5 * a_pc**3)

    # ---- DF ------------------------------------------------------------------------
    def ftilde_rel(self, E, L2, action="canonical"):
        I, _, ok = bh_action_period(E, L2, action)
        L = np.sqrt(L2) * self.conv
        d = self.table.delta(L, np.where(ok, I, 1.0) * self.conv)
        return np.where(ok, hernquist_ftilde_delta(d), 0.0)

    def ftilde_newton(self, eps, L2):
        I = newton_action(eps, np.sqrt(L2))
        d = self.table.delta(np.sqrt(L2) * self.conv, I * self.conv)
        return hernquist_ftilde_delta(d)

    # ---- densities (Msun / pc^3) ------------------------------------------------------
    def rho_rel(self, r, action="canonical", Eup=1.0, nE=64, nw=48):
        """SFW eq. (4.10) with the capture limits (3.15)-(3.17); r in units G m / c^2."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        out = np.zeros_like(r)
        xs, ws = leggauss(nE)
        s = 0.5 * (xs + 1); ws = 0.5 * ws
        xw, ww = leggauss(nw)
        w = 0.5 * (xw + 1); ww = 0.5 * ww
        for k, rk in enumerate(r):
            if rk <= 4.0:
                continue
            Em = float(Emin_root(rk))
            if Em >= Eup:
                continue
            E = Em + (Eup - Em) * s**2
            jac = 2 * s * (Eup - Em) * ws
            lc2 = Lc2(E)
            lm2 = Lmax2(rk, E)
            span = np.clip(lm2 - lc2, 0.0, None)
            L2 = lm2[:, None] - (w[None, :] ** 2) * span[:, None]
            F = self.ftilde_rel(np.broadcast_to(E[:, None], L2.shape), L2, action)
            inner = 2.0 * np.sqrt(span) * (F @ ww)
            out[k] = self.P * np.sum(jac * E * inner) / (rk - 2.0)
        return out

    def rho_newton_gs(self, r, nE=64, nw=48, Lmin=4.0, rcap=8.0, eps_lo=0.0):
        """Newtonian adiabatic growth with the GS capture ansatz (L >= 4 G m, SFW eq. 4.5)."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        out = np.zeros_like(r)
        xs, ws = leggauss(nE)
        s = 0.5 * (xs + 1); ws = 0.5 * ws
        xw, ww = leggauss(nw)
        w = 0.5 * (xw + 1); ww = 0.5 * ww
        for k, rk in enumerate(r):
            emax = 1.0 / rk - Lmin**2 / (2 * rk * rk)
            if emax <= eps_lo:
                continue
            # binding energy eps in [eps_lo, emax]; span vanishes like sqrt at emax
            eps = emax - (emax - eps_lo) * s**2
            jac = 2 * s * (emax - eps_lo) * ws
            lm2 = 2 * rk * rk * (1.0 / rk - eps)
            span = np.clip(lm2 - Lmin**2, 0.0, None)
            L2 = lm2[:, None] - (w[None, :] ** 2) * span[:, None]
            F = self.ftilde_newton(np.broadcast_to(eps[:, None], L2.shape), L2)
            inner = 2.0 * np.sqrt(span) * (F @ ww)
            out[k] = self.P * np.sum(jac * inner) / rk
        return out

    def rho_hernquist(self, r):
        """Initial Hernquist density at r (BH units) in Msun/pc^3."""
        x = np.asarray(r) * self.rg_pc / self.a
        return self.M / (2 * np.pi * self.a**3) / (x * (1 + x) ** 3)


def Emin_root(r):
    """Lowest E of a bound, non-captured particle at radius r: SFW eq. (3.17).

    For r >= 6 it is the E where L_max(r, E) = L_c(E); for 4 < r < 6 the circular-orbit
    energy at r (the particle must lie outside the potential peak).  Checked by brute
    force against bh_roots in spike_reference.py."""
    if r <= 4.0:
        return 1.0
    return float(Emin_sfw(r))


def Emin_bruteforce(r, nE=4000, nL=400):
    """Smallest E on a grid for which some L^2 in [L_c^2, L_max^2] gives a non-captured
    orbit with r_p <= r <= r_a (independent check of Emin_root)."""
    E = np.linspace(np.sqrt(8.0 / 9.0), 1.0 - 1e-9, nE)
    lc2 = Lc2(E); lm2 = Lmax2(r, E)
    w = np.linspace(0.0, 1.0, nL)
    L2 = lc2[:, None] + w[None, :] * (lm2 - lc2)[:, None]
    ra, rp, r3, ok = bh_roots(np.broadcast_to(E[:, None], L2.shape), L2)
    good = ok & (lm2 > lc2)[:, None] & (rp <= r * (1 + 1e-12)) & (ra >= r * (1 - 1e-12))
    rows = np.where(good.any(axis=1))[0]
    return E[rows[0]] if len(rows) else 1.0


# ------------------------------------------------------------------------------------
# constant distribution function (SFW section III.C)
def rho_constf_rel(r, f0=1.0, nE=200):
    """SFW eq. (3.21) with the limits (3.15)-(3.17); returns rho / f0 if f0 = 1."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    out = np.zeros_like(r)
    xs, ws = leggauss(nE)
    s = 0.5 * (xs + 1); ws = 0.5 * ws
    for k, rk in enumerate(r):
        if rk <= 4.0:
            continue
        Em = Emin_root(rk)
        E = Em + (1 - Em) * s**2
        jac = 2 * s * (1 - Em) * ws
        arg = np.clip(E * E - (1 - 2 / rk) * (1 + Lc2(E) / rk**2), 0, None)
        out[k] = 4 * np.pi * f0 / (1 - 2 / rk) ** 1.5 * np.sum(jac * np.sqrt(arg) * E)
    return out


def rho_constf_gs(r, f0=1.0, rcut=8.0):
    """GS eq. (6) as quoted in SFW eq. (3.22); rcut = 8 G m (GS) or 4 G m (variant)."""
    r = np.asarray(r, dtype=float)
    return 4 * np.pi * f0 / 3 * (2 / r) ** 1.5 * np.clip(1 - rcut / r, 0, None) ** 1.5
