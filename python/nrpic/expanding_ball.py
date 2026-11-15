"""Expanding dust ball on a slice of constant dust proper time: reference initial data
with extrinsic curvature (table format 2) and the exact evolution.

Lemaitre-Tolman-Bondi dust in the coordinates (tau, R), tau the proper time of the dust
and R the areal radius,

    ds^2 = -dtau^2 + (dR - v dtau)^2 / (1 + 2E) + R^2 dOmega^2,   v = sqrt(2m/R + 2E) > 0,

with the Misner-Sharp mass m(R) and the energy function E(R) given on the slice tau = 0.
On that slice (units G = c = 1; expansion has K < 0):

    3-metric   dR^2/(1 + 2E) + R^2 dOmega^2 = psi^4 (drbar^2 + rbar^2 dOmega^2),
               d ln rbar / dR = 1/(R sqrt(1 + 2E)),  psi^2 = R/rbar,  rbar = R where E = 0,
    K^i_j      = diag(KL, KT, KT),  KT = -v/R,  KL = -dv/dR  (derivative along the slice),
    lapse 1,   shift beta^R = -v, that is beta^rbar = -v rbar/(R sqrt(1 + 2E)),
    matter     dust at rest with respect to the normal observers, u_i = 0,
               energy density rho = (dm/dR)/(4 pi R^2).

The constraints hold identically: with (3)R = -4 (E R)'/R^2 and
4 KL KT + 2 KT^2 = 2 (R v^2)'/R^2 the Hamiltonian constraint reads 4 m'/R^2 = 16 pi rho,
and the momentum constraint is d KT/d ln R = KL - KT.

The model (class `Ball`): a homogeneous ball of areal radius Rb and density
rho_0 = 3M/(4 pi Rb^3),

    m = M (R/Rb)^3,  E = -e0 (R/Rb)^2,  v = H R,  H^2 = 2M/Rb^3 - 2 e0/Rb^2   (R <= Rb),

in vacuum (m = M_tot) outside.  e0 = 0 is the marginally bound ball: flat slice, psi = 1,
rbar = R, exterior of Painleve-Gullstrand form (KT = -sqrt(2M/R^3), KL = -KT/2), which
expands for ever, a(tau) = (1 + 3 H tau/2)^(2/3) for every shell.  e0 > 0 is a bound ball
(the time reverse of Oppenheimer-Snyder collapse, started while it expands): the vacuum
slice outside carries E(R) rising smoothly from -e0 at Rb to 0 at RE, and every shell
follows the cycloid, turning around at a_max = M/(e0 Rb).  With `edge` = w > 0 (only for
e0 = 0) the density falls from rho_0 to 0 with a quintic step over [Rb - w, Rb + w]; the
data are still exact marginally bound data and the total mass is m(Rb + w).

Exact evolution of a shell with initial areal radius R0, mass inside m, energy E:

    E = 0:  R(tau) = (R0^(3/2) + (3/2) sqrt(2m) tau)^(2/3),
    E < 0:  R = (m/(-2E)) (1 - cos eta),  tau = (m/(-2E)^(3/2)) (eta - sin eta) - tau_0,
            eta_0 = arccos(1 + 2 E R0/m) on the expanding branch.
"""

import math

import numpy as np
from numpy.polynomial import polynomial as npoly

from . import io as nio

__all__ = ["Ball", "ltb_radius", "ltb_turnaround", "residuals_1d", "lattice_sites"]


# quintic step S(x) = 10 x^3 - 15 x^4 + 6 x^5 on [0, 1] (two continuous derivatives)
_STEP = np.array([0.0, 0.0, 0.0, 10.0, -15.0, 6.0])


def _step(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (10.0 + x * (-15.0 + 6.0 * x))


def _dstep(x):
    x = np.clip(x, 0.0, 1.0)
    return 30.0 * x * x * (1.0 - x) ** 2


def ltb_radius(R0, tau, m, E=0.0, iters=80):
    """Areal radius at proper time tau of the dust shell that starts at R0 with mass m
    inside and energy E <= 0, on the expanding branch at tau = 0 (arrays broadcast)."""
    R0, tau, m, E = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (R0, tau, m, E)))
    flat = (R0 ** 1.5 + 1.5 * np.sqrt(2.0 * m) * tau)
    out = np.where(flat > 0.0, np.abs(flat), 0.0) ** (2.0 / 3.0)
    bound = E < 0.0
    if np.any(bound):
        mb, Eb, Rb, tb = m[bound], E[bound], R0[bound], tau[bound]
        amp = mb / (-2.0 * Eb)
        tsc = mb / (-2.0 * Eb) ** 1.5
        eta0 = np.arccos(np.clip(1.0 - Rb / amp, -1.0, 1.0))
        target = tb / tsc + eta0 - np.sin(eta0)
        lo = np.zeros_like(target)
        hi = np.full_like(target, 2.0 * math.pi)
        for _ in range(iters):                       # eta - sin(eta) is increasing
            mid = 0.5 * (lo + hi)
            below = mid - np.sin(mid) < target
            lo = np.where(below, mid, lo)
            hi = np.where(below, hi, mid)
        eta = 0.5 * (lo + hi)
        out = out.copy()
        out[bound] = amp * (1.0 - np.cos(eta))
    return out


def ltb_turnaround(R0, m, E):
    """(tau, R) at the turnaround of a bound shell (E < 0) that expands at tau = 0."""
    R0, m, E = (np.asarray(a, dtype=float) for a in (R0, m, E))
    amp = m / (-2.0 * E)
    eta0 = np.arccos(np.clip(1.0 - R0 / amp, -1.0, 1.0))
    return m / (-2.0 * E) ** 1.5 * (math.pi - eta0 + np.sin(eta0)), 2.0 * amp


def lattice_sites(h, rmax):
    """Sites (k + 1/2) h of the cubic lattice with |x| <= rmax, as x[N,3], sorted by
    the integer triple; symmetric about the origin and about the centres of the cells of
    any mesh whose cell size is a multiple of h and has a cell boundary at the origin."""
    n = int(math.ceil(rmax / h)) + 1
    k = 2 * np.arange(-n, n, dtype=np.int64) + 1          # coordinates in units of h/2
    I, J, K = np.meshgrid(k, k, k, indexing="ij")
    r2 = (I * I + J * J + K * K).astype(float) * (0.5 * h) ** 2
    keep = r2 <= rmax * rmax
    return 0.5 * h * np.stack([I[keep], J[keep], K[keep]], axis=-1).astype(float)


class Ball:
    """Homogeneous expanding dust ball; see the module text.

    M     mass scale: rho_0 = 3M/(4 pi Rb^3) (the total mass when edge = 0)
    Rb    areal radius of the surface (centre of the edge when edge > 0)
    e0    binding: E = -e0 (R/Rb)^2 inside; 0 for the marginally bound ball
    RE    areal radius beyond which the vacuum slice has E = 0 (e0 > 0 only)
    edge  half-width w of the smooth edge of the density (e0 = 0 only)
    """

    def __init__(self, M=1.0, Rb=10.0, e0=0.0, RE=None, edge=0.0):
        self.M, self.Rb, self.e0, self.edge = float(M), float(Rb), float(e0), float(edge)
        if self.e0 < 0.0:
            raise ValueError("e0 must not be negative (unbound balls are not implemented)")
        if self.e0 > 0.0 and self.edge > 0.0:
            raise ValueError("the smooth edge is implemented for e0 = 0 only")
        if not 0.0 <= self.edge < self.Rb:
            raise ValueError("edge must lie in [0, Rb)")
        self.RE = float(RE) if RE is not None else 2.0 * self.Rb
        if self.e0 > 0.0 and self.RE <= self.Rb:
            raise ValueError("RE must exceed Rb")
        self.rho0 = 3.0 * self.M / (4.0 * math.pi * self.Rb ** 3)
        h2 = 2.0 * self.M / self.Rb ** 3 - 2.0 * self.e0 / self.Rb ** 2
        if h2 <= 0.0:
            raise ValueError("the surface does not expand: need e0 < M/Rb")
        self.H = math.sqrt(h2)
        # mass through the edge: m = m(Rb - w) + 4 pi rho_0 int (1 - S(x)) R^2 dR,
        # R = a + 2 w x; the integrand is a polynomial in x
        if self.edge > 0.0:
            a, w2 = self.Rb - self.edge, 2.0 * self.edge
            one_minus = -_STEP.copy()
            one_minus[0] += 1.0
            integrand = npoly.polymul(one_minus, npoly.polymul([a, w2], [a, w2])) * w2
            self._medge = npoly.polyint(integrand)
            self._min = 4.0 * math.pi * self.rho0 * a ** 3 / 3.0
            self.Mtot = self._min + 4.0 * math.pi * self.rho0 * npoly.polyval(1.0, self._medge)
        else:
            self.Mtot = self.M
        self.Rout = self.Rb + self.edge            # outer radius of the matter
        if self.e0 > 0.0:
            R = np.linspace(self.Rb, self.RE, 2001)
            if np.min(2.0 * self.M / R + 2.0 * self.energy(R)) <= 0.0:
                raise ValueError("v^2 <= 0 on the vacuum slice: increase RE or reduce e0")
            self._build_rbar()

    # ------------------------------------------------------------------ slice functions
    def density(self, R):
        """Energy density rho(R) on the slice."""
        R = np.asarray(R, dtype=float)
        if self.edge > 0.0:
            return self.rho0 * (1.0 - _step((R - (self.Rb - self.edge)) / (2.0 * self.edge)))
        return np.where(R <= self.Rb, self.rho0, 0.0)

    def mass(self, R):
        """Misner-Sharp mass m(R)."""
        R = np.asarray(R, dtype=float)
        if self.edge > 0.0:
            x = np.clip((R - (self.Rb - self.edge)) / (2.0 * self.edge), 0.0, 1.0)
            inner = 4.0 * math.pi * self.rho0 * np.minimum(R, self.Rb - self.edge) ** 3 / 3.0
            return inner + 4.0 * math.pi * self.rho0 * npoly.polyval(x, self._medge)
        return self.M * np.minimum(R / self.Rb, 1.0) ** 3

    def energy(self, R):
        """Energy function E(R) of the slice."""
        R = np.asarray(R, dtype=float)
        if self.e0 == 0.0:
            return np.zeros_like(R)
        inner = -self.e0 * (np.minimum(R, self.Rb) / self.Rb) ** 2
        return np.where(R <= self.Rb, inner,
                        -self.e0 * (1.0 - _step((R - self.Rb) / (self.RE - self.Rb))))

    def denergy(self, R):
        """dE/dR along the slice (one-sided values at Rb: inner for R <= Rb)."""
        R = np.asarray(R, dtype=float)
        if self.e0 == 0.0:
            return np.zeros_like(R)
        outer = self.e0 * _dstep((R - self.Rb) / (self.RE - self.Rb)) / (self.RE - self.Rb)
        return np.where(R <= self.Rb, -2.0 * self.e0 * R / self.Rb ** 2, outer)

    def velocity(self, R):
        """v = dR/dtau of the dust (of the slice observers in vacuum)."""
        R = np.asarray(R, dtype=float)
        Rs = np.where(R > 0.0, R, 1.0)
        return np.where(R > 0.0, np.sqrt(2.0 * self.mass(Rs) / Rs + 2.0 * self.energy(Rs)), 0.0)

    def curvature(self, R):
        """(KL, KT) at areal radius R; at R = Rb the values of the matter side."""
        R = np.asarray(R, dtype=float)
        Rs = np.where(R > 0.0, R, 1.0)
        v = self.velocity(Rs)
        dm = 4.0 * math.pi * self.density(Rs) * Rs * Rs
        dv = (dm / Rs - self.mass(Rs) / Rs ** 2 + self.denergy(Rs)) / v
        return np.where(R > 0.0, -dv, -self.H), np.where(R > 0.0, -v / Rs, -self.H)

    # ------------------------------------------------------------ isotropic coordinate
    def _build_rbar(self):
        """rbar(R) for e0 > 0: closed form inside, quadrature through the vacuum
        transition, rbar = R beyond RE."""
        from scipy.integrate import solve_ivp
        from scipy.interpolate import CubicSpline

        def rhs(R, y):
            return [(1.0 / math.sqrt(1.0 + 2.0 * float(self.energy(R))) - 1.0) / R]

        # y = ln(rbar/R), zero at RE, integrated inwards to Rb
        sol = solve_ivp(rhs, [self.RE, self.Rb], [0.0], method="DOP853", rtol=1e-13,
                        atol=1e-15, dense_output=True, max_step=(self.RE - self.Rb) / 400.0)
        self._lnq_out = sol.sol
        self._lnq_b = float(sol.y[0, -1])
        # inside: rbar = c R/(1 + sqrt(1 - k R^2)), k = 2 e0/Rb^2, matched at Rb
        self._k = 2.0 * self.e0 / self.Rb ** 2
        self._c = math.exp(self._lnq_b) * (1.0 + math.sqrt(1.0 - self._k * self.Rb ** 2))
        # inverse through a dense spline of R against rbar
        Rg = np.concatenate([np.linspace(0.0, self.Rb, 20001)[:-1],
                             np.linspace(self.Rb, self.RE, 20001)])
        self._Rofrbar = CubicSpline(self.isotropic(Rg), Rg)

    def isotropic(self, R):
        """Isotropic radius rbar of the areal radius R on the slice."""
        R = np.asarray(R, dtype=float)
        if self.e0 == 0.0:
            return R.copy()
        inner = self._c * R / (1.0 + np.sqrt(np.maximum(1.0 - self._k * np.minimum(R, self.Rb) ** 2, 0.0)))
        mid = R * np.exp(self._lnq_out(np.clip(R, self.Rb, self.RE))[0])
        return np.where(R <= self.Rb, inner, np.where(R < self.RE, mid, R))

    def areal(self, rbar, iters=3):
        """Areal radius R of the isotropic radius rbar (Newton-polished spline inverse)."""
        rbar = np.asarray(rbar, dtype=float)
        if self.e0 == 0.0:
            return rbar.copy()
        rE = float(self.isotropic(self.RE))
        R = np.where(rbar < rE, self._Rofrbar(np.minimum(rbar, rE)), rbar)
        for _ in range(iters):
            Rs = np.where(R > 0.0, R, 1.0)
            f = self.isotropic(Rs) - rbar
            df = self.isotropic(Rs) / (Rs * np.sqrt(1.0 + 2.0 * self.energy(Rs)))
            R = np.where((R > 0.0) & (rbar < rE), Rs - f / df, R)
        return R

    @property
    def rbar_b(self):
        """Isotropic radius of the surface Rb."""
        return float(self.isotropic(self.Rb))

    @property
    def rbar_out(self):
        """Isotropic radius of the outer edge of the matter."""
        return float(self.isotropic(self.Rout))

    # --------------------------------------------------------------- initial-data table
    def profiles(self, rbar):
        """dict(u, KL, KT, alpha, betar, R, rho) at isotropic radii rbar."""
        rbar = np.asarray(rbar, dtype=float)
        R = self.areal(rbar)
        Rs = np.where(R > 0.0, R, 1.0)
        rs = np.where(rbar > 0.0, rbar, 1.0)
        if self.e0 == 0.0:
            psi = np.ones_like(rbar)
        else:
            psi0 = math.sqrt(2.0 / self._c)
            psi = np.where(rbar > 0.0, np.sqrt(Rs / rs), psi0)
        KL, KT = self.curvature(R)
        betar = -self.velocity(Rs) * rs / (Rs * np.sqrt(1.0 + 2.0 * self.energy(Rs)))
        return dict(u=psi - 1.0, KL=KL, KT=KT, alpha=np.ones_like(rbar),
                    betar=np.where(rbar > 0.0, betar, 0.0), R=R, rho=self.density(R))

    def table(self, n_matter=4000, rmax_factor=1.25):
        """`Table2` with n_matter rows across the matter, reaching rmax_factor times the
        outer radius of the matter (and at least RE when e0 > 0).  A sharp surface is a
        break, placed midway between two rows; rows beyond it hold the vacuum values."""
        rb = self.rbar_out
        sharp = self.edge == 0.0
        dr = rb / (n_matter + 0.5) if sharp else rb / n_matter
        rmax = rmax_factor * rb
        if self.e0 > 0.0:
            rmax = max(rmax, 1.02 * float(self.isotropic(self.RE)))
        n = int(math.ceil(rmax / dr)) + 1
        rbar = dr * np.arange(n)
        p = self.profiles(rbar)
        breaks = [rb] if sharp else []
        if self.e0 > 0.0:
            breaks.append(float(self.isotropic(self.RE)))     # third derivatives jump
        return nio.Table2(rbar, p["u"], p["KL"], p["KT"], p["alpha"], p["betar"],
                          exterior="pg", breaks=breaks)

    def summary(self):
        d = dict(model="expanding_ball", M=self.M, Rb=self.Rb, e0=self.e0, edge=self.edge,
                 M_total=float(self.Mtot), rho0=self.rho0, H=self.H, H_Rb=self.H * self.Rb,
                 compactness_2M_over_Rb=2.0 * float(self.Mtot) / self.Rb,
                 rest_mass=float(self.rest_mass()),
                 rbar_b=self.rbar_b, rbar_out=self.rbar_out)
        if self.e0 > 0.0:
            tta, Rmax = ltb_turnaround(self.Rb, self.M, -self.e0)
            d.update(RE=self.RE, a_max=float(Rmax) / self.Rb, tau_turnaround=float(tta),
                     psi_centre=math.sqrt(2.0 / self._c))
        return d

    def write_table(self, path, n_matter=4000, rmax_factor=1.25, header=()):
        """Write the format-2 table and return it."""
        t = self.table(n_matter, rmax_factor)
        hdr = ["expanding dust ball on a slice of constant dust proper time "
               "(python/nrpic/expanding_ball.py)"]
        hdr += [f"{k} = {v!r}" for k, v in self.summary().items()]
        hdr += list(header)
        return nio.write_tab2(path, t.rbar, t.u, t.KL, t.KT, t.alpha, t.betar,
                              exterior=t.exterior, breaks=t.breaks, header=hdr)

    # ------------------------------------------------------------------------ particles
    def lattice(self, h, mass_rule="surface"):
        """Dust at rest in the slice on the cubic lattice of spacing h in the isotropic
        coordinates: (x[N,3], u_i[N,3] = 0, m[N]).

        m_p = rho(R_p) psi_p^6 h^3 (the proper volume of a lattice cell times the
        density).  mass_rule: 'volume' keeps that rule; 'surface' (sharp surface only)
        rescales the sites within one lattice spacing of the surface so that the total is
        the continuum rest mass; 'normalize' rescales all sites to that total.
        """
        x = lattice_sites(h, self.rbar_out)
        r = np.sqrt(np.sum(x * x, axis=1))
        R = self.areal(r)
        psi = np.sqrt(np.where(r > 0.0, R / np.where(r > 0.0, r, 1.0), 1.0))
        m = self.density(R) * psi ** 6 * h ** 3
        keep = m > 0.0
        x, r, m = x[keep], r[keep], m[keep]
        total = self.rest_mass()
        if mass_rule == "surface":
            if self.edge > 0.0:
                raise ValueError("mass_rule 'surface' is for the sharp surface")
            layer = r > self.rbar_out - h
            m[layer] *= (total - m[~layer].sum()) / m[layer].sum()
        elif mass_rule == "normalize":
            m *= total / m.sum()
        elif mass_rule != "volume":
            raise ValueError(f"unknown mass_rule {mass_rule!r}")
        return x, np.zeros_like(x), m

    def rest_mass(self):
        """Continuum rest mass, int rho dV = int dm/sqrt(1 + 2E)."""
        if self.e0 == 0.0:
            return self.Mtot
        # int_0^Rb 4 pi rho0 R^2 dR / sqrt(1 - k R^2)
        k, Rb = self._k, self.Rb
        s = math.sqrt(k) * Rb
        return 4.0 * math.pi * self.rho0 * (math.asin(s) - s * math.sqrt(1.0 - s * s)) / (2.0 * k ** 1.5)

    def tracers(self, factors=(1.25, 1.5, 2.0), mass=1.0e-30):
        """Test particles at rest in the slice outside the ball, at the areal radii
        factors * Rout along 26 directions: (x[N,3], u_i[N,3] = 0, m[N]).  They follow
        `ltb_radius` with m = M_total and the energy of the slice at their radius."""
        d = np.array([(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)
                      if (i, j, k) != (0, 0, 0)], dtype=float)
        d /= np.sqrt(np.sum(d * d, axis=1))[:, None]
        x = np.concatenate([float(self.isotropic(f * self.Rout)) * d for f in factors])
        return x, np.zeros_like(x), np.full(len(x), mass)

    # ------------------------------------------------------------------- exact solution
    def shell(self, rbar0):
        """(R0, m, E) of the shells that start at isotropic radii rbar0."""
        R0 = self.areal(np.asarray(rbar0, dtype=float))
        return R0, self.mass(R0), self.energy(R0)

    def radius(self, rbar0, tau):
        """Exact areal radius at proper time tau of the shells starting at rbar0."""
        R0, m, E = self.shell(rbar0)
        return ltb_radius(R0, tau, m, E)

    def scale_factor(self, tau):
        """a(tau) = R/R0 of the homogeneous part."""
        tau = np.asarray(tau, dtype=float)
        return ltb_radius(self.Rb, tau, self.M, -self.e0) / self.Rb


def residuals_1d(table, density, margin=2):
    """Offline check of a format-2 table against the matter it comes with.

    density(rbar) is the energy density of matter at rest in the slice (S_i = 0).
    Returns dict(rbar, H, M, Hscale, Mscale) on the rows that are at least `margin` rows
    away from the ends of their piece (fourth-order differences of the rows, never across
    a break):

        H = -8 psi^-5 (psi'' + 2 psi'/rbar) + 4 KL KT + 2 KT^2 - 16 pi rho,
        M = 2 [ (2 psi'/psi + 1/rbar) (KL - KT) - KT' ]          (radial component),

    Hscale and Mscale are the sums of the absolute values of the terms.
    """
    dr = table.dr
    out = {k: [] for k in ("rbar", "H", "M", "Hscale", "Mscale")}
    for lo, hi in table.pieces:
        k = np.arange(max(lo + margin, 1), hi - margin + 1)
        if len(k) == 0:
            continue
        r = table.rbar[k]
        psi = 1.0 + table.u

        def d1(f):
            return (-f[k + 2] + 8.0 * f[k + 1] - 8.0 * f[k - 1] + f[k - 2]) / (12.0 * dr)

        def d2(f):
            return (-f[k + 2] + 16.0 * f[k + 1] - 30.0 * f[k] + 16.0 * f[k - 1] - f[k - 2]) / (12.0 * dr * dr)

        dpsi, ddpsi, dkt = d1(psi), d2(psi), d1(table.KT)
        p, kl, kt = psi[k], table.KL[k], table.KT[k]
        ricci = -8.0 * p ** -5 * (ddpsi + 2.0 * dpsi / r)
        kterm = 4.0 * kl * kt + 2.0 * kt * kt
        rho = 16.0 * math.pi * np.asarray(density(r), dtype=float)
        geo = (2.0 * dpsi / p + 1.0 / r) * (kl - kt)
        out["rbar"].append(r)
        out["H"].append(ricci + kterm - rho)
        out["Hscale"].append(np.abs(ricci) + np.abs(kterm) + np.abs(rho))
        out["M"].append(2.0 * (geo - dkt))
        out["Mscale"].append(2.0 * (np.abs(geo) + np.abs(dkt)))
    return {k: np.concatenate(v) for k, v in out.items()}
