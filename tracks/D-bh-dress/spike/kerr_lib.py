"""Semi-analytic reference for the dark-matter spike of an adiabatically grown Kerr black
hole, by the method of Ferrer, da Rosa & Will 2017 (arXiv:1707.06302, "FdRW"; source
kb-data/raw/arxiv/1707.06302/v2/src/kerrdm.tex).

Decision 0010: a reference solution (quadratures, root finding), no time evolution.
Units G = c = m_BH = 1, Boyer-Lindquist (r, theta) (the same r, theta as Kerr-Schild).

FdRW conventions (kerrdm.tex lines 328-370, their Sigma^2 is our S = r^2 + a^2 cos^2):
  E  = -u_t,  Lz = u_phi,  C = u_theta^2 + Lz^2/sin^2 + a^2 cos^2 (1 - E^2)  (= Q + Lz^2)
  r^4 V = P(E, Lz; r) - Delta C,  P = (r^4 + a^2 r^2 + 2 a^2 r) E^2 - Delta r^2
                                       + a^2 Lz^2 - 4 a E Lz r                    (eq. 370)
  U = C - C_U,  C_U = Lz^2/sin^2 + a^2 (1 - E^2) cos^2                            (eq. 360)
  J_t   = -2/(r^2 sin) int dE dC dLz E f/(sqrt V sqrt U)                          (eq. 397)
  J_phi =  2/(r^2 sin) int dE dC dLz Lz f/(sqrt V sqrt U)
  rho   = sqrt(-g^{mu nu} J_mu J_nu)                                              (eq. 413)

Capture (FdRW criteria, lines 462-473): the orbit through r with (E, C, Lz) does not plunge
iff R(r') = r'^4 V(r') < 0 somewhere in (r_+, r), i.e. iff C > C_crit(E, Lz; r) with
    C_crit = min_{r_+ < r' <= r} C_V(r'),   C_V = P/Delta,
because R is linear in C. (FdRW find the boundary by testing turning points; this closed
form of the same criterion is ours.) With V >= 0 (C <= C_V(r)) and U >= 0 (C >= C_U) the
integration domain at (r, theta) is C in [max(C_U, C_crit), C_V(r)].

Change of variables (ours): Lz = l sin(theta), C = C_U + (C_V - C_U)(1 - cos phi)/2. Then
dC dLz/(sqrt V sqrt U) = r^2 sin/sqrt(Delta) dl dphi and
    J_t = -(2/sqrt Delta) int dE dl int_{phi_lo}^{pi} dphi E f,
    J_phi = sin * (2/sqrt Delta) int dE dl dphi l f,
    n = sqrt(-g) J^t (particles per dr dtheta dphi on a t = const slice)
      = (2 sin/Delta^{3/2}) int dE dl dphi f (A E - 2 a r Lz),
    A = (r^2 + a^2)^2 - a^2 Delta sin^2.
Adiabatic growth (FdRW eqs. 526-549): f(E, C, Lz) = f_H(eps'), L = |Lz| + I_theta/(2 pi),
I_r^H(eps', L) = I_r(E, C, Lz) with the canonical I_r = oint u_r dr = oint sqrt(R)/Delta dr.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss

from spike_lib import HernquistInverse, hernquist_ftilde_delta, RG_SUN_PC


def gl(n, a=0.0, b=1.0):
    x, w = leggauss(n)
    return a + (b - a) * 0.5 * (x + 1.0), 0.5 * (b - a) * w


_ETA, _ETA_W = gl(64, 0.0, np.pi)
_SIN2ETA = np.sin(_ETA) ** 2
_PSI, _PSI_W = gl(32, 0.0, 0.5 * np.pi)
_S2PSI = np.sin(_PSI) ** 2
_C2PSI = np.cos(_PSI) ** 2


def _bisect(f, lo, hi, n=64):
    """Vectorized bisection; f(lo) and f(hi) of opposite sign (not checked)."""
    lo = np.array(lo, dtype=float, copy=True)
    hi = np.array(hi, dtype=float, copy=True)
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        same = (fm > 0) == (flo > 0)
        lo = np.where(same, mid, lo)
        flo = np.where(same, fm, flo)
        hi = np.where(same, hi, mid)
    return 0.5 * (lo + hi)


class Kerr:
    """Bound, non-plunging geodesics of a Kerr hole of unit mass and spin a."""

    def __init__(self, a):
        self.a = float(a)
        self.rp = 1.0 + np.sqrt(1.0 - self.a ** 2)

    # ---- potentials ------------------------------------------------------------------
    def Delta(self, r):
        return r * r - 2.0 * r + self.a ** 2

    def P(self, E, Lz, r):
        a = self.a
        return ((r ** 4 + a * a * r * r + 2 * a * a * r) * E * E - self.Delta(r) * r * r
                + a * a * Lz * Lz - 4.0 * a * E * Lz * r)

    def CV(self, E, Lz, r):
        return self.P(E, Lz, r) / self.Delta(r)

    def CU(self, E, Lz, th):
        return Lz * Lz / np.sin(th) ** 2 + self.a ** 2 * (1 - E * E) * np.cos(th) ** 2

    def R(self, x, E, C, Lz):
        """r^4 V as a polynomial in x (Horner)."""
        a = self.a
        c4 = E * E - 1.0
        c2 = a * a * (E * E - 1.0) - C
        c1 = 2 * a * a * E * E - 4 * a * E * Lz + 2 * C
        c0 = a * a * (Lz * Lz - C)
        return (((c4 * x + 2.0) * x + c2) * x + c1) * x + c0

    def ccrit(self, E, Lz, r, ngrid=128, niter=50):
        """C_crit = min over r_+ < r' <= r of C_V(r') and the minimizer r_u.

        E, Lz arrays (same shape), r scalar or array of that shape. Grid search uniform in
        r' on [r_+ + 1e-4 (r - r_+), r] then golden section on the bracket of the grid
        minimum. Returns (C_crit, r_u, at_end) with at_end True where the minimum is at r
        itself (then no non-plunging orbit passes through r)."""
        E = np.asarray(E, dtype=float)
        Lz = np.asarray(Lz, dtype=float)
        E, Lz = np.broadcast_arrays(E, Lz)
        r = np.broadcast_to(np.asarray(r, dtype=float), E.shape)
        t = np.linspace(1e-4, 1.0, ngrid)
        uu = self.rp + (r[..., None] - self.rp) * t
        cv = self.CV(E[..., None], Lz[..., None], uu)
        k = np.argmin(cv, axis=-1)
        lo = np.take_along_axis(uu, np.maximum(k - 1, 0)[..., None], -1)[..., 0]
        hi = np.take_along_axis(uu, np.minimum(k + 1, ngrid - 1)[..., None], -1)[..., 0]
        g = 0.5 * (np.sqrt(5.0) - 1.0)

        def F(u):
            return self.CV(E, Lz, u)

        for _ in range(niter):
            c = hi - g * (hi - lo); d = lo + g * (hi - lo)
            left = F(c) < F(d)
            hi = np.where(left, d, hi); lo = np.where(left, lo, c)
        um = 0.5 * (lo + hi)
        cm = F(um)
        cend = self.CV(E, Lz, r)
        Cc = np.minimum(cm, cend)
        # a minimum that the search puts within 1e-7 (r - r_+) of r is the endpoint
        at_end = (cend <= cm) | (r - um < 1e-7 * (r - self.rp))
        return Cc, um, at_end

    # ---- turning points and actions ----------------------------------------------------
    def radial_roots(self, E, C, Lz, r, ru):
        """r1 >= r2 > r3 >= r4 of R for a bound non-plunging orbit through r (R(r) >= 0)
        with R(ru) < 0 at ru in (r_+, r)."""
        f = lambda x: self.R(x, E, C, Lz)  # noqa: E731
        top = 2.0 / (1.0 - E * E) + 1.0
        r1 = _bisect(f, np.broadcast_to(r, E.shape), top)
        r2 = _bisect(f, ru, np.broadcast_to(r, E.shape))
        r3 = _bisect(f, np.full(E.shape, self.rp), ru)
        Q = np.clip(C - Lz * Lz, 0.0, None)
        r4 = self.a ** 2 * Q / ((1.0 - E * E) * r1 * r2 * r3)
        return r1, r2, r3, r4

    def I_r(self, E, r1, r2, r3, r4):
        """Canonical radial action oint u_r dr = 2 int_{r2}^{r1} sqrt(R)/Delta dr."""
        h = 0.5 * (r1 - r2)
        x = r2[..., None] + h[..., None] * (1.0 - np.cos(_ETA))
        g = np.sqrt((x - r3[..., None]) * (x - r4[..., None])) / self.Delta(x)
        return 2.0 * h * h * np.sqrt(1.0 - E * E) * ((_SIN2ETA * g) @ _ETA_W)

    def I_theta(self, E, C, Lz):
        """Polar action oint u_theta dtheta = 4 u_- int_0^{pi/2} sqrt(w_+ - w_- sin^2 psi)
        cos^2 psi/(1 - u_- sin^2 psi) dpsi (cos theta = sqrt(u_-) sin psi)."""
        Q = np.clip(C - Lz * Lz, 0.0, None)
        beta = self.a ** 2 * (1.0 - E * E)
        S = C + beta
        den = S + np.sqrt(np.clip(S * S - 4 * beta * Q, 0.0, None))
        wp = 0.5 * den
        wm = 2 * beta * Q / den
        um = 2 * Q / den
        integ = (np.sqrt(wp[..., None] - wm[..., None] * _S2PSI) * _C2PSI
                 / (_C2PSI + (1.0 - um[..., None]) * _S2PSI))
        return 4.0 * um * (integ @ _PSI_W)

    # ---- domain at a point -------------------------------------------------------------
    def l_bounds(self, E, r, th):
        """Interval of l = Lz/sin(theta) with C_V(r) >= C_U (V >= 0 and U >= 0 possible)."""
        a = self.a
        s, c = np.sin(th), np.cos(th)
        D = self.Delta(r)
        K0 = r ** 4 + a * a * r * r + 2 * a * a * r
        A2 = a * a * s * s / D - 1.0
        A1 = -4 * a * E * r * s / D
        A0 = (K0 * E * E - D * r * r) / D - a * a * (1 - E * E) * c * c
        disc = A1 * A1 - 4 * A2 * A0
        ok = disc > 0
        sq = np.sqrt(np.where(ok, disc, 0.0))
        l1 = (-A1 + sq) / (2 * A2); l2 = (-A1 - sq) / (2 * A2)
        return np.minimum(l1, l2), np.maximum(l1, l2), ok & (A2 < 0)

    def allowed_measure(self, E, r, th, nl=257):
        """max over an l grid of C_V(r) - max(C_U, C_crit) (> 0: some orbit is allowed)."""
        E = np.atleast_1d(np.asarray(E, dtype=float))
        lo, hi, ok = self.l_bounds(E, r, th)
        t = 0.5 * (1.0 - np.cos(np.pi * np.arange(1, nl - 1) / (nl - 1)))   # dense at the ends
        l = lo[:, None] + (hi - lo)[:, None] * t
        EE = np.broadcast_to(E[:, None], l.shape)
        Lz = l * np.sin(th)
        Cc, _, end = self.ccrit(EE, Lz, r)
        cv = self.CV(EE, Lz, r)
        cu = l * l + self.a ** 2 * (1 - EE * EE) * np.cos(th) ** 2
        m = np.where(end, -np.inf, cv - np.maximum(cu, Cc))
        return np.where(ok, m.max(axis=1), -np.inf)

    def Emin(self, r, th, Elo=0.5, Ehi=1.0, n=44):
        """Lowest E of a bound non-plunging orbit through (r, theta) (bisection; assumes the
        allowed set in E is an interval [Emin, 1), checked by brute force in the tests)."""
        if self.allowed_measure(np.array([Ehi - 1e-12]), r, th)[0] <= 0:
            return 1.0
        lo, hi = Elo, Ehi - 1e-12
        for _ in range(n):
            mid = 0.5 * (lo + hi)
            if self.allowed_measure(np.array([mid]), r, th)[0] > 0:
                hi = mid
            else:
                lo = mid
        return hi

    # ---- the integrals -----------------------------------------------------------------
    def moments(self, r, th, fmodel=None, Eup=1.0, nE=48, npan=48, npn=4, nphi=20,
                Emin=None):
        """J_t, J~_phi = J_phi/sin(theta), rho, n (per dr dtheta dphi) at (r, theta) for
        f = 1 (fmodel None: constant DF, phi integral analytic) or f = fmodel(E, C, Lz,
        actions...) (a KerrHernquist). Returns a dict (all zero where no orbit exists)."""
        a = self.a
        s, c = np.sin(th), np.cos(th)
        D = self.Delta(r)
        S = r * r + a * a * c * c
        A = (r * r + a * a) ** 2 - a * a * D * s * s
        if D <= a * a * s * s:
            raise ValueError("point inside the ergoregion: not handled")
        Em = self.Emin(r, th) if Emin is None else Emin
        out = {"r": r, "th": th, "Emin": Em, "J_t": 0.0, "Jphit": 0.0, "rho": 0.0, "n": 0.0,
               "Lz_mean": np.nan, "nan_f": 0}
        if Em >= Eup:
            return out
        sE, wE = gl(nE)
        E = Em + (Eup - Em) * sE ** 2
        wE = wE * 2 * sE * (Eup - Em)
        lo, hi, ok = self.l_bounds(E, r, th)
        # l = l_mid - l_half cos(psi): nodes dense at both ends of the l interval, where
        # the most bound orbits (planar ones at the equator) and 1/sqrt edges sit
        xp, wp = gl(npn)
        edges = np.linspace(0.0, np.pi, npan + 1)
        tl = (edges[:-1, None] + np.diff(edges)[:, None] * xp[None, :]).ravel()
        wl0 = (np.diff(edges)[:, None] * wp[None, :]).ravel() * np.sin(tl) * 0.5
        tl = 0.5 * (1.0 - np.cos(tl))
        l = lo[:, None] + (hi - lo)[:, None] * tl[None, :]
        wl = np.where(ok, hi - lo, 0.0)[:, None] * wl0[None, :]
        EE = np.broadcast_to(E[:, None], l.shape)
        Lz = l * s
        Cc, ru, end = self.ccrit(EE, Lz, r)
        cv = self.CV(EE, Lz, r)
        cu = l * l + a * a * (1 - EE * EE) * c * c
        good = (~end) & (cv > np.maximum(cu, Cc)) & ok[:, None]
        cosl = np.clip(1.0 - 2.0 * np.clip(Cc - cu, 0.0, None) / np.where(good, cv - cu, 1.0),
                       -1.0, 1.0)
        philo = np.arccos(cosl)
        W = np.where(good, wE[:, None] * wl, 0.0)
        if fmodel is None:
            F = np.where(good, np.pi - philo, 0.0)
            nanf = 0
        else:
            idx = np.nonzero(good)
            sp, wph = gl(nphi)
            pl = philo[idx]
            ph = pl[:, None] + (np.pi - pl)[:, None] * sp[None, :]
            wph = (np.pi - pl)[:, None] * wph[None, :]
            Eg = EE[idx][:, None] * np.ones_like(ph)
            Lg = Lz[idx][:, None] * np.ones_like(ph)
            cug, cvg = cu[idx][:, None], cv[idx][:, None]
            Cg = cug + (cvg - cug) * 0.5 * (1.0 - np.cos(ph))
            rug = ru[idx][:, None] * np.ones_like(ph)
            fv = fmodel(self, Eg.ravel(), Cg.ravel(), Lg.ravel(), r, rug.ravel()).reshape(ph.shape)
            nanf = int(np.sum(~np.isfinite(fv)))
            fv = np.where(np.isfinite(fv), fv, 0.0)
            F = np.zeros(l.shape)
            F[idx] = np.sum(fv * wph, axis=1)
        Jt = -(2.0 / np.sqrt(D)) * np.sum(W * EE * F)
        Jp = (2.0 / np.sqrt(D)) * np.sum(W * l * F)
        n = (2.0 * s / D ** 1.5) * np.sum(W * F * (A * EE - 2 * a * r * Lz))
        nt = (2.0 / D ** 1.5) * np.sum(W * F * (A * EE - 2 * a * r * Lz))   # n / sin
        rho2 = (A * Jt * Jt + 4 * a * r * s * Jt * Jp - (D - a * a * s * s) * Jp * Jp) / (S * D)
        out.update({"J_t": Jt, "Jphit": Jp, "rho": np.sqrt(max(rho2, 0.0)), "n": n,
                    "n_over_sin": nt, "Lz_mean": np.sum(W * F * Lz * (A * EE - 2 * a * r * Lz))
                    / max(np.sum(W * F * (A * EE - 2 * a * r * Lz)), 1e-300),
                    "nan_f": nanf, "frac_good": float(good.mean())})
        return out


class KerrHernquist:
    """f = f~_H(eps') of the Hernquist halo (M, a_H) after adiabatic growth of a hole of
    mass m (FdRW sec. IV, SFW sec. IV); callable as fmodel(kerr, E, C, Lz, r, ru)."""

    def __init__(self, M_sun=1e12, a_pc=2.0e4, m_sun=4e6, table=None):
        self.M, self.a_pc, self.m = M_sun, a_pc, m_sun
        self.kappa = M_sun * RG_SUN_PC / a_pc
        self.conv = np.sqrt(self.kappa) * m_sun / M_sun
        self.rg_pc = m_sun * RG_SUN_PC
        self.table = table if table is not None else HernquistInverse()
        # rho [Msun/pc^3] = Af * (moments with f = f~); f = M/(sqrt2 (2pi)^3 (G M a)^{3/2}) f~
        self.Af = M_sun / (np.sqrt(2.0) * (2 * np.pi) ** 3 * self.kappa ** 1.5 * a_pc ** 3)

    def actions(self, kerr, E, C, Lz, r, ru):
        r1, r2, r3, r4 = kerr.radial_roots(E, C, Lz, r, ru)
        Ir = kerr.I_r(E, r1, r2, r3, r4)
        Ith = kerr.I_theta(E, C, Lz)
        return Ir, Ith, (r1, r2, r3, r4)

    def __call__(self, kerr, E, C, Lz, r, ru):
        Ir, Ith, _ = self.actions(kerr, E, C, Lz, r, ru)
        L = np.abs(Lz) + Ith / (2 * np.pi)
        d = self.table.delta(L * self.conv, Ir * self.conv)
        return hernquist_ftilde_delta(d)


# ---------------------------------------------------------------------------------------
# orbits confined to the equatorial plane (FdRW sec. III.A and appendix B)
def equatorial_planar(kerr, r, Eup=1.0, nE=64):
    """rho/f_eq of planar orbits at theta = pi/2 (FdRW eq. 584): J_t = -8 f/sqrt(r) int E
    I_t dE, J_phi = 8 f/sqrt(r) int I_phi dE, with I_t = int dLz/sqrt(V_x) over the
    non-plunging Lz (C = Lz^2), evaluated here with Lz = Lmid + Lhalf cos psi (so
    dLz/sqrt(V_x) = dpsi/sqrt(x-2)) and the capture edges Lc+-: Lz^2 = C_crit(E, Lz).
    Returns (rho/f, J_t/f, Emin_planar)."""
    a = kerr.a
    x = r
    if x <= 2.0:
        raise ValueError("planar formula used outside the ergosphere only")

    def lpm(E):
        # roots of V_x(Lz) = (2-x) Lz^2 - 4 a E Lz + [E^2 (x^3 + a^2 (2+x)) + (2-x) x^2 - a^2 x]
        A2, A1 = 2.0 - x, -4 * a * E
        A0 = E * E * (x ** 3 + a * a * (2 + x)) + (2 - x) * x * x - a * a * x
        disc = A1 * A1 - 4 * A2 * A0
        sq = np.sqrt(np.clip(disc, 0.0, None))
        l1 = (-A1 + sq) / (2 * A2); l2 = (-A1 - sq) / (2 * A2)
        return np.maximum(l1, l2), np.minimum(l1, l2), disc > 0

    def g(Lz, E):
        Cc, _, end = kerr.ccrit(E, Lz, r)
        return np.where(end, -1.0, Lz * Lz - Cc)

    def arcs(E):
        E = np.atleast_1d(E)
        Lp, Lm, ok = lpm(E)
        gp, gm = g(Lp * (1 - 1e-12), E), g(Lm * (1 - 1e-12), E)
        z = np.zeros_like(E)
        Lcp = _bisect(lambda L: g(L, E), z + 1e-9, Lp * (1 - 1e-12), 60)
        Lcm = _bisect(lambda L: g(L, E), Lm * (1 - 1e-12), z - 1e-9, 60)
        mid, half = 0.5 * (Lp + Lm), 0.5 * (Lp - Lm)
        psi = lambda L: np.arccos(np.clip((L - mid) / half, -1, 1))  # noqa: E731
        co = np.where(ok & (gp > 0), psi(Lcp), 0.0)              # arc [0, psi(Lc+)]
        ct = np.where(ok & (gm > 0), np.pi - psi(Lcm), 0.0)      # arc [psi(Lc-), pi]
        It = (co + ct) / np.sqrt(x - 2)
        # int Lz dpsi over the arcs
        Ip = (mid * co + half * np.sin(co) + mid * ct - half * np.sin(ct)) / np.sqrt(x - 2)
        return It, Ip

    # planar Emin by bisection on "some arc nonempty"
    def nonempty(E):
        E = np.array([E])
        Lp, Lm, ok = lpm(E)
        return bool(ok[0] and (g(Lp * (1 - 1e-12), E)[0] > 0 or g(Lm * (1 - 1e-12), E)[0] > 0))
    if not nonempty(Eup - 1e-12):
        return 0.0, 0.0, 1.0
    lo, hi = 0.5, Eup - 1e-12
    for _ in range(44):
        mid = 0.5 * (lo + hi)
        if nonempty(mid):
            hi = mid
        else:
            lo = mid
    Em = hi
    sE, wE = gl(nE)
    E = Em + (Eup - Em) * sE ** 2
    wE = wE * 2 * sE * (Eup - Em)
    It, Ip = arcs(E)
    Jt = -8.0 / np.sqrt(x) * np.sum(wE * E * It)
    Jp = 8.0 / np.sqrt(x) * np.sum(wE * Ip)
    D = kerr.Delta(x)
    A = (x * x + a * a) ** 2 - a * a * D
    S = x * x
    rho2 = (A * Jt * Jt + 4 * a * x * Jt * Jp - (D - a * a) * Jp * Jp) / (S * D)
    return np.sqrt(max(rho2, 0.0)), Jt, Em
