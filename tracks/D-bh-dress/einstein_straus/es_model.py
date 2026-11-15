"""Black hole in a vacuum bubble inside an expanding dust ball (Einstein-Straus type):
exact initial data on one slice, the format-2 table plus puncture for `nrpic_cf`, dust
particles at rest in the slice, and the exact evolution of every shell.

Derivation: DERIVATION.md of this directory (sym/*.py check it). Units G = c = 1; the code's
sign, expansion has K < 0. Areal radius R, isotropic radius rbar, K^i_j = diag(KL, KT, KT).

Slice (outer sheet, R > 2M):
    KT = -f(R) sqrt(2 m(R)/R^3),      KL = d(R KT)/dR  (momentum constraint, S_i = 0),
    (dR/dl)^2 = W^2 = 1 - 2m(1 - f^2)/R,   dm/dR = 4 pi R^2 rho  (Hamiltonian constraint),
    d ln rbar / d ln R = 1/W,   psi^2 = R/rbar.
f = 0 for R <= R0 (> 2M): time-symmetric Schwarzschild, psi = a + b/rbar, 2ab = M, through
the throat (R = 2M at rbar = b/a) to the second asymptotic end at rbar -> 0;
f rises with a C-infinity step to 1 at R1 <= R_in (inner edge of the dust) and stays 1:
from R1 outwards the slice is flat (W = 1), psi = 1, rbar = R, and the dust is marginally
bound Lemaitre-Tolman-Bondi dust at rest in the slice (v = sqrt(2m/R)).

Code form: psi = 1 + u(rbar) + m_p/(2 rbar) with m_p = 2b = M/a and u regular,
u = a - 1 for rbar <= rbar(R0), u = -m_p/(2 rbar) for rbar >= R1.

Dust: density rising with the same C-infinity step over [Rw - w_in, Rw + w_in] and
falling over [Rb - w_out, Rb + w_out]; with matched = True the plateau density rho_0 is
chosen so that m = 4 pi rho_0 R^3/3 on the plateau (exact Einstein-de Sitter between the
edges, H^2 = 8 pi rho_0/3; for w_in -> 0 this is M = 4 pi rho_0 Rw^3/3, the Einstein-Straus
matching). w_in = 0 or w_out = 0 gives a sharp edge (a break of the table).
"""
import json
import math
import struct

import numpy as np
from scipy.integrate import cumulative_simpson, quad
from scipy.interpolate import make_interp_spline

__all__ = ["smooth_step", "EinsteinStrausBH", "ltb_radius", "write_tab2", "read_tab2",
           "Tab2", "write_nrp"]


# ------------------------------------------------------------------ C-infinity step
def smooth_step(x):
    """S(x) = 0 (x <= 0), 1 (x >= 1), 1/(1 + exp(1/x - 1/(1-x))) between: C-infinity."""
    x = np.asarray(x, dtype=float)
    out = np.where(x >= 1.0, 1.0, 0.0)
    mid = (x > 0.0) & (x < 1.0)
    xm = x[mid]
    g = 1.0 / xm - 1.0 / (1.0 - xm)
    out = out.astype(float)
    out[mid] = 0.5 * (1.0 - np.tanh(0.5 * g))         # = 1/(1 + e^g), overflow-safe
    return out


def smooth_step_d(x):
    """dS/dx."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x, dtype=float)
    mid = (x > 0.0) & (x < 1.0)
    xm = x[mid]
    g = 1.0 / xm - 1.0 / (1.0 - xm)
    s = 0.5 * (1.0 - np.tanh(0.5 * g))
    out[mid] = s * (1.0 - s) * (1.0 / xm ** 2 + 1.0 / (1.0 - xm) ** 2)
    return out


# ------------------------------------------------------------------ exact shell motion
def ltb_radius(R0, tau, m, E=0.0, iters=100):
    """Areal radius at proper time tau of the dust shell (or radial geodesic) that starts
    at areal radius R0 moving outward with energy E (2E = v0^2 - 2m/R0) around mass m.
    E = 0: (R0^(3/2) + 1.5 sqrt(2m) tau)^(2/3); E < 0: cycloid, through turnaround and
    infall (returns nan after R reaches 0)."""
    R0, tau, m, E = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (R0, tau, m, E)))
    out = np.empty(R0.shape)
    flat = np.abs(E) < 1e-300
    if np.any(flat):
        q = R0[flat] ** 1.5 + 1.5 * np.sqrt(2.0 * m[flat]) * tau[flat]
        out[flat] = np.where(q > 0, np.abs(q), np.nan) ** (2.0 / 3.0)
    bnd = E < 0
    if np.any(bnd):
        mb, Eb, Rb, tb = m[bnd], E[bnd], R0[bnd], tau[bnd]
        amp = mb / (-2.0 * Eb)
        tsc = mb / (-2.0 * Eb) ** 1.5
        eta0 = np.arccos(np.clip(1.0 - Rb / amp, -1.0, 1.0))      # expanding branch
        target = tb / tsc + eta0 - np.sin(eta0)
        lo, hi = np.zeros_like(target), np.full_like(target, 2.0 * math.pi)
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            below = mid - np.sin(mid) < target
            lo, hi = np.where(below, mid, lo), np.where(below, hi, mid)
        eta = 0.5 * (lo + hi)
        o = amp * (1.0 - np.cos(eta))
        o[target >= 2.0 * math.pi] = np.nan
        out[bnd] = o
    unb = E > 0
    if np.any(unb):
        raise NotImplementedError("unbound shells (E > 0) do not occur in this model")
    return out


class EinsteinStrausBH:
    """See the module text. Lengths in units of the black-hole mass when M = 1.

    M      black-hole (Misner-Sharp) mass inside the vacuum bubble
    Rw     Schuecking radius: centre of the inner edge of the dust
    w_in   half-width of the inner edge (0: sharp wall at Rw)
    Rb     centre of the outer edge (surface) of the dust ball
    w_out  half-width of the outer edge (0: sharp surface at Rb)
    R0     f = 0 for R <= R0 (must exceed 2M)
    R1     f = 1 for R >= R1 (default: inner end of the dust, Rw - w_in)
    matched  plateau density from the Einstein-Straus matching (else rho0 must be given)
    """

    def __init__(self, M=1.0, Rw=40.0, w_in=4.0, Rb=100.0, w_out=6.0, R0=4.0, R1=None,
                 matched=True, rho0=None, ngrid=400001):
        self.M, self.Rw, self.w_in, self.Rb, self.w_out = map(float, (M, Rw, w_in, Rb, w_out))
        self.R0 = float(R0)
        self.Rin = self.Rw - self.w_in                   # innermost dust shell (the wall)
        self.R1 = float(R1) if R1 is not None else self.Rin
        self.Rout = self.Rb + self.w_out                 # outermost dust shell
        if not 2.0 * self.M < self.R0 < self.R1 <= self.Rin:
            raise ValueError("need 2M < R0 < R1 <= Rw - w_in")
        if not self.Rw + self.w_in < self.Rb - self.w_out:
            raise ValueError("the two edges overlap")
        self.matched = bool(matched)
        # cumulative edge integrals int S R^2 dR (Simpson on a fine grid, quintic spline)
        self._build_edges()
        J_in = self._edge_integral_in(self.Rw + self.w_in)      # int S R^2 dR over the inner edge
        if self.matched:
            self.rho0 = self.M / (4.0 * math.pi * ((self.Rw + self.w_in) ** 3 / 3.0 - J_in))
        else:
            if rho0 is None:
                raise ValueError("matched = False needs rho0")
            self.rho0 = float(rho0)
        self._J_in = J_in
        self._m_plateau0 = self.M + 4.0 * math.pi * self.rho0 * J_in   # m(Rw + w_in)
        self.H = math.sqrt(8.0 * math.pi * self.rho0 / 3.0)            # plateau Hubble rate
        self.Mtot = float(self.mass(np.array([self.Rout]))[0])
        self._build_isotropic(ngrid)

    # -------------------------------------------------------------- radial profiles in R
    def f(self, R):
        return smooth_step((np.asarray(R, float) - self.R0) / (self.R1 - self.R0))

    def df(self, R):
        return smooth_step_d((np.asarray(R, float) - self.R0) / (self.R1 - self.R0)) / (self.R1 - self.R0)

    def _s_in(self, R):
        if self.w_in == 0.0:
            return np.where(np.asarray(R, float) >= self.Rw, 1.0, 0.0)
        return smooth_step((np.asarray(R, float) - (self.Rw - self.w_in)) / (2.0 * self.w_in))

    def _s_out(self, R):
        if self.w_out == 0.0:
            return np.where(np.asarray(R, float) <= self.Rb, 1.0, 0.0)
        return 1.0 - smooth_step((np.asarray(R, float) - (self.Rb - self.w_out)) / (2.0 * self.w_out))

    def density(self, R):
        """Energy density (= rest-mass density, dust at rest in the slice)."""
        R = np.asarray(R, float)
        return self.rho0 * self._s_in(R) * self._s_out(R)

    def _build_edges(self, n=40001):
        self._spl_in = self._spl_out = None
        if self.w_in > 0.0:
            a, b = self.Rw - self.w_in, self.Rw + self.w_in
            Rg = np.linspace(a, b, n)
            c = cumulative_simpson(self._s_in(Rg) * Rg * Rg, x=Rg, initial=0.0)
            self._spl_in = make_interp_spline(Rg, c, k=5)
        if self.w_out > 0.0:
            a, b = self.Rb - self.w_out, self.Rb + self.w_out
            Rg = np.linspace(a, b, n)
            c = cumulative_simpson(self._s_out(Rg) * Rg * Rg, x=Rg, initial=0.0)
            self._spl_out = make_interp_spline(Rg, c, k=5)

    def _edge_integral_in(self, R):
        """int_{Rw - w_in}^{R} S_in R'^2 dR' for R up to the end of the inner edge."""
        R = np.asarray(R, float)
        if self.w_in == 0.0:
            return np.where(R > self.Rw, (np.maximum(R, self.Rw) ** 3 - self.Rw ** 3) / 3.0, 0.0)
        a, b = self.Rw - self.w_in, self.Rw + self.w_in
        return np.where(R <= a, 0.0, self._spl_in(np.clip(R, a, b)))

    def _edge_integral_out(self, R):
        """int_{Rb - w_out}^{R} S_out R'^2 dR' for R up to the end of the outer edge."""
        R = np.asarray(R, float)
        a = self.Rb - self.w_out
        if self.w_out == 0.0:
            return np.where(R > a, (np.clip(R, a, self.Rb) ** 3 - a ** 3) / 3.0, 0.0)
        b = self.Rb + self.w_out
        return np.where(R <= a, 0.0, self._spl_out(np.clip(R, a, b)))

    def mass(self, R):
        """Misner-Sharp mass m(R) on the slice (outer sheet; m = M inside the bubble)."""
        R = np.atleast_1d(np.asarray(R, float))
        p0, p1 = self.Rw + self.w_in, self.Rb - self.w_out
        four_pi_rho = 4.0 * math.pi * self.rho0
        m_edge_in = self.M + four_pi_rho * self._edge_integral_in(np.minimum(R, p0))
        m_plat = self._m_plateau0 + four_pi_rho * (np.clip(R, p0, p1) ** 3 - p0 ** 3) / 3.0
        m_p1 = self._m_plateau0 + four_pi_rho * (p1 ** 3 - p0 ** 3) / 3.0
        m_edge_out = m_p1 + four_pi_rho * self._edge_integral_out(R)
        return np.where(R <= self.Rin, self.M, np.where(R < p0, m_edge_in,
                        np.where(R <= p1, m_plat, m_edge_out)))

    def W(self, R, m=None):
        R = np.asarray(R, float)
        m = self.mass(R) if m is None else m
        with np.errstate(invalid="ignore"):
            return np.sqrt(1.0 - 2.0 * m * (1.0 - self.f(R) ** 2) / R)

    def curvature(self, R, m=None):
        """(KL, KT) at areal radius R on the outer sheet."""
        R = np.asarray(R, float)
        m = self.mass(R) if m is None else m
        fR, dfR = self.f(R), self.df(R)
        v = np.sqrt(2.0 * m / R)                               # sqrt(2m/R)
        dv = (4.0 * math.pi * R * self.density(R) - m / R ** 2) / v
        KT = -fR * v / R
        KL = -(dfR * v + fR * dv)
        return KL, KT

    # -------------------------------------------------------------- isotropic radius
    def _build_isotropic(self, ngrid):
        """ln(rbar/R) = -int_R^{R1} (1/W - 1) dR'/R' on [Rlo, R1 + 1] (vacuum, m = M);
        quintic spline of R against rbar; time-symmetric constants a, b."""
        M = self.M
        Rlo = self.R0 - 0.25 * (self.R0 - 2.0 * M)
        Rhi = self.R1 + 1.0                  # f = 1 exactly beyond R1: integrand zero there
        Rg = np.linspace(Rlo, Rhi, ngrid)
        Wg = np.sqrt(1.0 - 2.0 * M * (1.0 - self.f(Rg) ** 2) / Rg)
        integ = (1.0 / Wg - 1.0) / Rg
        # cumulative from the top (Rhi, where the integrand vanishes identically if Rhi >= R1)
        c = cumulative_simpson(integ, x=Rg, initial=0.0)        # int_{Rlo}^{R}
        q = c - c[-1]                                           # ln(rbar/R) = -int_R^{Rhi}
        rbg = Rg * np.exp(q)
        self._Rg, self._rbg = Rg, rbg
        self._R_of_rbar = make_interp_spline(rbg, Rg, k=5)
        self._lnq_of_R = make_interp_spline(Rg, q, k=5)
        r_iso0 = 0.5 * (self.R0 - M + math.sqrt(self.R0 ** 2 - 2.0 * M * self.R0))
        self.rbar0 = float(self.R0 * math.exp(self._lnq_of_R(self.R0)))
        self.a = math.sqrt(r_iso0 / self.rbar0)
        self.b = M / (2.0 * self.a)
        self.m_p = 2.0 * self.b                                  # bare puncture mass M/a
        self.u0 = self.a - 1.0                                   # u(0)
        self.rbar_throat = self.b / self.a
        self.rbar1 = self.R1                                     # flat from here on
        # consistency of the time-symmetric form with the quadrature below R0
        Rc = np.linspace(Rlo, self.R0, 5)
        rb_q = Rc * np.exp(self._lnq_of_R(Rc))
        rb_ts = 0.5 * (Rc - M + np.sqrt(Rc ** 2 - 2.0 * M * Rc)) / self.a ** 2
        self.ts_consistency = float(np.max(np.abs(rb_q / rb_ts - 1.0)))

    def areal(self, rbar):
        """Areal radius R(rbar) (both sheets)."""
        rbar = np.asarray(rbar, float)
        out = np.empty_like(rbar)
        inner = rbar <= self.rbar0
        rs = np.where(rbar > 0, rbar, 1.0)
        psi_ts = self.a + self.b / rs
        out[inner] = (psi_ts ** 2 * rs)[inner]
        out[rbar <= 0] = np.inf
        flat = rbar >= self.R1
        out[flat] = rbar[flat]
        mid = ~inner & ~flat
        if np.any(mid):
            out[mid] = self._R_of_rbar(rbar[mid])
        return out

    def isotropic(self, R):
        """rbar(R) on the outer sheet (R >= 2M)."""
        R = np.asarray(R, float)
        out = R.copy()
        ts = R <= self.R0
        with np.errstate(invalid="ignore"):
            out[ts] = 0.5 * (R[ts] - self.M + np.sqrt(R[ts] ** 2 - 2.0 * self.M * R[ts])) / self.a ** 2
        mid = (R > self.R0) & (R < self.R1)
        out[mid] = R[mid] * np.exp(self._lnq_of_R(R[mid]))
        return out

    def profiles(self, rbar):
        """Fields of the slice at isotropic radii rbar >= 0: dict with psi (full conformal
        factor), u (regular part: psi = 1 + u + m_p/(2 rbar)), KL, KT, alpha (= psi^-2),
        betar (= alpha rbar KT / W: areal radius frozen at t = 0), R, rho, m, f,
        W (= dR/dl along increasing rbar, negative on the inner sheet), sheet."""
        rbar = np.asarray(rbar, float)
        R = self.areal(rbar)
        inner = rbar <= self.rbar0
        flat = rbar >= self.R1
        Rs = np.where(np.isfinite(R), R, 1.0)
        m = np.full_like(rbar, self.M)
        out_matter = rbar > self.Rin
        if np.any(out_matter):
            m[out_matter] = self.mass(rbar[out_matter])
        KL, KT = self.curvature(Rs, m)
        KL = np.where(inner, 0.0, KL)
        KT = np.where(inner, 0.0, KT)
        rs = np.where(rbar > 0, rbar, 1.0)
        psi = np.where(inner, self.a + self.b / rs, np.sqrt(Rs / rs))
        psi = np.where(flat, 1.0, psi)
        u = np.where(inner, self.u0, psi - 1.0 - 0.5 * self.m_p / rs)
        u = np.where(flat, -0.5 * self.m_p / rs, u)
        alpha = np.where(rbar > 0, 1.0 / psi ** 2, 0.0)
        # W = dR/dl along increasing rbar: -sqrt(1 - 2M/R) on the inner sheet
        with np.errstate(invalid="ignore"):
            Wts = np.sqrt(np.maximum(1.0 - 2.0 * self.M / Rs, 0.0))
        Wv = np.where(inner, np.where(rbar < self.rbar_throat, -Wts, Wts), self.W(Rs, m))
        betar = np.where(inner, 0.0, alpha * rbar * KT / np.where(inner, 1.0, Wv))
        rho = np.where(rbar > self.Rin, self.density(Rs), 0.0)
        fR = np.where(inner, 0.0, self.f(Rs))
        sheet = np.where(rbar < self.rbar_throat, -1, 1)
        return dict(psi=psi, u=u, KL=KL, KT=KT, alpha=alpha, betar=betar, R=R, rho=rho, m=m,
                    f=fR, W=Wv, sheet=sheet)

    # -------------------------------------------------------------- expansions
    def expansions(self, rbar):
        """(theta_plus, theta_minus) of the spheres rbar = const, plus = towards larger rbar:
        theta_pm = (2/R)(pm dR/dl - R KT), dR/dl = W on the outer sheet, -W' inside."""
        p = self.profiles(rbar)
        R = p["R"]
        Rs = np.where(np.isfinite(R), R, 1.0)
        Rl = p["W"]                       # dR/dl along increasing rbar (negative on the inner sheet)
        thp = 2.0 / Rs * (Rl - Rs * p["KT"])
        thm = 2.0 / Rs * (-Rl - Rs * p["KT"])
        return thp, thm

    # -------------------------------------------------------------- summary
    def summary(self):
        Rhub = 1.0 / self.H
        return dict(model="einstein_straus_bh", M=self.M, Rw=self.Rw, w_in=self.w_in,
                    Rb=self.Rb, w_out=self.w_out, R0=self.R0, R1=self.R1, Rin=self.Rin,
                    Rout=self.Rout, matched=self.matched, rho0=self.rho0, H=self.H,
                    hubble_radius=Rhub, H_Rb=self.H * self.Rb, H_Rout=self.H * self.Rout,
                    H_Rw=self.H * self.Rw, M_total=self.Mtot, M_dust=self.Mtot - self.M,
                    compactness_2Mtot_over_Rout=2.0 * self.Mtot / self.Rout,
                    wall_over_rs=self.Rin / (2.0 * self.M), a=self.a, b=self.b, m_p=self.m_p,
                    u0=self.u0, rbar0=self.rbar0, rbar_throat=self.rbar_throat,
                    R_throat=2.0 * self.M, expansion_time_1_over_H=1.0 / self.H,
                    ts_consistency=self.ts_consistency)

    # -------------------------------------------------------------- the table
    def table(self, drbar=0.02, rmax_factor=1.15):
        """Rows of the format-2 table: rbar_k = k drbar up to rmax_factor Rout (and at least
        8 rows beyond Rout). Sharp edges become breaks midway between rows: drbar is
        adjusted so that Rw (sharp wall) sits midway; a sharp surface Rb is required to sit
        midway too (ValueError otherwise; choose Rb accordingly)."""
        breaks = []
        if self.w_in == 0.0:
            n = round(self.Rw / drbar - 0.5)
            drbar = self.Rw / (n + 0.5)
            breaks.append(self.Rw)
        if self.w_out == 0.0:
            k = self.Rb / drbar - 0.5
            if abs(k - round(k)) > 1e-6:
                raise ValueError(f"sharp surface Rb = {self.Rb} is not midway between rows "
                                 f"(drbar = {drbar}); use Rb = {(round(k) + 0.5) * drbar!r}")
            breaks.append(self.Rb)
        rmax = max(rmax_factor * self.Rout, self.Rout + 8 * drbar)
        n = int(math.ceil(rmax / drbar)) + 1
        rbar = drbar * np.arange(n)
        p = self.profiles(rbar)
        # sharp edges: rows hold the values of their own side (density is one-sided there)
        return Tab2(rbar, p["u"], p["KL"], p["KT"], p["alpha"], p["betar"], exterior="pg",
                    breaks=breaks)

    # -------------------------------------------------------------- particles
    def lattice(self, h, shift=0.0):
        """Dust at rest in the slice on the cubic lattice (k + 1/2 + shift) h, restricted
        to the dust (rho > 0); m_p = rho h^3 (psi = 1 in the dust). Returns x[N,3], m[N]."""
        nmax = int(math.ceil(self.Rout / h)) + 2
        k = (np.arange(-nmax, nmax) + 0.5 + shift) * h
        xs = []
        ms = []
        for xi in k:                                  # slab by slab to keep memory low
            Y, Z = np.meshgrid(k, k, indexing="ij")
            r = np.sqrt(xi * xi + Y * Y + Z * Z)
            sel = (r > self.Rin) & (r < self.Rout)
            if not np.any(sel):
                continue
            rr = r[sel]
            rho = self.density(rr)
            keep = rho > 0
            xs.append(np.stack([np.full(np.count_nonzero(keep), xi), Y[sel][keep], Z[sel][keep]], axis=1))
            ms.append(rho[keep] * h ** 3)
        return np.concatenate(xs), np.concatenate(ms)

    def tracer_radii(self):
        """Areal radii of massless tracers: inside the transition (bound, fall back),
        at the wall, at the Schuecking radius, on the plateau, outside the ball."""
        tr = [1.5 * self.R0, 2.5 * self.R0, 0.5 * (self.R0 + self.R1), 0.25 * self.R0 + 0.75 * self.R1,
              self.Rin, self.Rw, 0.5 * (self.Rw + self.Rb), self.Rb, 1.1 * self.Rout, 1.3 * self.Rout]
        return np.array(tr)

    def shell_energy(self, R0):
        """(m, E) of the radial geodesic of a particle at rest in the slice at R0:
        v0 = f sqrt(2m/R0), 2E = v0^2 - 2m/R0 = -(1 - f^2) 2m/R0."""
        R0 = np.asarray(R0, float)
        m = self.mass(R0)
        E = -(1.0 - self.f(R0) ** 2) * m / R0
        return m, np.where(np.abs(E) < 1e-300, 0.0, E)

    def radius(self, R0, tau):
        m, E = self.shell_energy(R0)
        return ltb_radius(R0, tau, m, E)

    def scale_factor(self, tau):
        return (1.0 + 1.5 * self.H * np.asarray(tau, float)) ** (2.0 / 3.0)


# ------------------------------------------------------------------ table format 2
class Tab2:
    """Rows of a format-2 table and the evaluation rule of nrpic_cf.cpp (branch
    core/id-extrinsic, CFPieceStencil and CFSetExtrinsic), re-implemented here."""

    def __init__(self, rbar, u, KL, KT, alpha, betar, exterior="pg", breaks=()):
        self.rbar = np.asarray(rbar, float)
        self.cols = dict(u=np.asarray(u, float), KL=np.asarray(KL, float),
                         KT=np.asarray(KT, float), alpha=np.asarray(alpha, float),
                         betar=np.asarray(betar, float))
        self.exterior = exterior
        self.breaks = list(breaks)
        self.dr = self.rbar[1] - self.rbar[0]
        n = len(self.rbar)
        self.pieces = []
        first = 0
        for b in self.breaks:
            k = first
            while k < n and self.rbar[k] < b:
                k += 1
            self.pieces.append((first, k - 1))
            first = k
        self.pieces.append((first, n - 1))

    def _stencil(self, r):
        p = np.zeros(r.shape, dtype=int)
        for ib, b in enumerate(self.breaks):
            p = np.where(r >= b, ib + 1, p)
        klo = np.array([pc[0] for pc in self.pieces])[p]
        khi = np.array([pc[1] for pc in self.pieces])[p]
        xi = r / self.dr
        i = np.floor(xi).astype(int)
        i = np.maximum(i, klo + 1)
        i = np.minimum(i, khi - 2)
        s = xi - i
        w = np.stack([-s * (s - 1.0) * (s - 2.0) / 6.0, (s + 1.0) * (s - 1.0) * (s - 2.0) / 2.0,
                      -(s + 1.0) * s * (s - 2.0) / 2.0, (s + 1.0) * s * (s - 1.0) / 6.0])
        return i, w

    def evaluate(self, r):
        """dict of the five columns at radii r, with the continuation beyond the last row."""
        r = np.asarray(r, float)
        rl = self.rbar[-1]
        inside = r < rl
        ri = np.where(inside, r, 0.0)
        i, w = self._stencil(ri)
        out = {}
        for key, col in self.cols.items():
            v = sum(w[q] * col[i - 1 + q] for q in range(4))
            out[key] = v
        rs = np.where(r > 0, r, 1.0)
        q = rl / rs
        last = {k: c[-1] for k, c in self.cols.items()}
        out["u"] = np.where(inside, out["u"], last["u"] * q)
        if self.exterior == "pg":
            out["KL"] = np.where(inside, out["KL"], last["KL"] * q ** 1.5)
            out["KT"] = np.where(inside, out["KT"], last["KT"] * q ** 1.5)
            out["betar"] = np.where(inside, out["betar"], last["betar"] * np.sqrt(q))
        else:
            for k in ("KL", "KT", "betar"):
                out[k] = np.where(inside, out[k], 0.0)
        out["alpha"] = np.where(inside, out["alpha"], last["alpha"])
        return out


def write_tab2(path, tab, header=()):
    """Write a format-2 table (coord/INTERFACES/spherical_id_format2.md and the refined
    text of core, tracks/core/interfaces/spherical_id_format2.md on core/id-extrinsic)."""
    with open(path, "w") as fo:
        fo.write("# format = 2\n")
        fo.write("# columns = rbar u KL KT alpha betar\n")
        fo.write(f"# exterior = {tab.exterior}\n")
        if tab.breaks:
            fo.write("# breaks = " + " ".join(repr(float(b)) for b in tab.breaks) + "\n")
        for h in header:
            fo.write(f"# {h}\n")
        c = tab.cols
        for k in range(len(tab.rbar)):
            fo.write(f"{tab.rbar[k]:.17e} {c['u'][k]:.17e} {c['KL'][k]:.17e} {c['KT'][k]:.17e} "
                     f"{c['alpha'][k]:.17e} {c['betar'][k]:.17e}\n")


def read_tab2(path):
    rows, hdr = [], {}
    for line in open(path):
        if line.startswith("#"):
            if "=" in line:
                k, v = line[1:].split("=", 1)
                hdr[k.strip()] = v.strip()
            continue
        if line.strip():
            rows.append([float(z) for z in line.split()])
    a = np.array(rows)
    breaks = [float(z) for z in hdr.get("breaks", "").split()]
    return Tab2(a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5],
                exterior=hdr.get("exterior", "pg"), breaks=breaks), hdr


def write_nrp(path, x, u, m, species=None):
    """Particle file of docs/FORMATS.md: 'NRPIC001', int64 N, N x 7 float64, N int32."""
    x, u, m = np.asarray(x, "<f8"), np.asarray(u, "<f8"), np.asarray(m, "<f8")
    n = len(m)
    sp = np.zeros(n, "<i4") if species is None else np.asarray(species, "<i4")
    rec = np.empty((n, 7), "<f8")
    rec[:, 0:3], rec[:, 3:6], rec[:, 6] = x, u, m
    with open(path, "wb") as fo:
        fo.write(b"NRPIC001")
        fo.write(struct.pack("<q", n))
        fo.write(rec.tobytes())
        fo.write(sp.tobytes())


def dump_json(path, obj):
    with open(path, "w") as fo:
        json.dump(obj, fo, indent=1, sort_keys=False, default=float)
