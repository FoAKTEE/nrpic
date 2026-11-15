"""Static, spherically symmetric Einstein-Vlasov equilibria f = Phi(E) (L - L0)^l_+ and
their conformally flat, time-symmetric initial data in the formats of docs/FORMATS.md.

Families (E = e^mu eps the Killing energy, eps = (1 + |v|^2)^(1/2), L the squared angular
momentum, particle rest mass 1, G = c = 1):

    'poly'  f = (1 - E/E0)^k_+ (L - L0)^l_+          2009.08163 eq. (Ansatz_Poly), line 631
    'king'  f = (exp(1 - E/E0) - 1)_+ (L - L0)^l_+   2009.08163 eq. (Ansatz_King), line 635
                                                      (the paper uses l = L0 = 0)
gr-qc/0601112 uses f = (E0 - E)^k_+ (L - L0)^l_+ (line 633); for k = 0 it is 'poly' with
k = 0 (Cases 1, 2, 4 of its Tables 1, 2, 4).

Moments (static observer, orthonormal momentum v, w its radial part; 2009.08163 lines
343-355, gr-qc/0601112 lines 271-288, 595-609): with e = e^y = E0 e^{-mu} and
eps_min^2 = 1 + L0/r^2, integrating L analytically,

    n   = 2 pi B(l+1, 1/2) r^{2l} int eps   Phi (eps^2 - eps_min^2)^{l+1/2} deps
    rho = 2 pi B(l+1, 1/2) r^{2l} int eps^2 Phi (eps^2 - eps_min^2)^{l+1/2} deps
    p   = 2 pi B(l+1, 3/2) r^{2l} int       Phi (eps^2 - eps_min^2)^{l+3/2} deps
    p_T =   pi r^{2l} int Phi [ (L0/r^2) B(l+1,1/2) (eps^2 - eps_min^2)^{l+1/2}
                               + B(l+2,1/2) (eps^2 - eps_min^2)^{l+3/2} ] deps,

eps from eps_min to e. n is the number (= rest-mass) density, rho the energy density, p and
p_T the radial and tangential pressures. The eps integrals are done by Gauss-Jacobi
quadrature with the endpoint powers in the weight, so they are exact to round-off for the
polytropes and to spectral accuracy for the King model.

Structure (Schwarzschild coordinates, areal r; 2009.08163 eq. ssdgl, line 671):

    y' = -e^{2 lambda} (m/r^2 + 4 pi r p),  m' = 4 pi r^2 rho,  N' = 4 pi r^2 e^lambda n,
    e^{-2 lambda} = 1 - 2m/r,

from y(0) = y0 (L0 = 0) or from the inner edge r_in = (L0/(e^{2 y0} - 1))^{1/2} of a
shell (L0 > 0), to the outer edge where e^{2y} = eps_min^2 (the innermost shell only, as
in 2009.08163 lines 653-658). E0 = e^{y(R)} (1 - 2M/R)^{1/2} makes e^mu -> 1 at infinity.
The isotropic radius follows from d ln rbar = e^lambda d ln r, carried as
I = int (e^lambda - 1) dr/r, and psi = (r/rbar)^{1/2} (as in python/nrpic/st_cluster.py).

Units of an `Equilibrium`: ADM mass M (default 1); the slice gamma_ij = psi^4 delta_ij,
K_ij = 0, lapse alpha = E0 e^{-y} is the static solution itself (it satisfies the
constraints exactly; no re-solve is needed for the unperturbed models).
"""

import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import roots_jacobi, beta as Beta
from scipy.stats import beta as beta_dist

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "python"))

from nrpic import io as nio  # noqa: E402
from nrpic.sampling import stratified_uniforms, unit_vectors  # noqa: E402
from nrpic.st_cluster import isotropic_from_areal  # noqa: E402

NQ = 64
RTOL = 1e-12
ATOL = 1e-15
FOURPI = 4.0 * math.pi

__all__ = ["Family", "Equilibrium", "sample", "binding_energy", "scan",
           "first_maximum", "first_zero", "lane_emden"]


# ----------------------------------------------------------------------------
# quadrature
# ----------------------------------------------------------------------------
_JAC = {}


def _jacobi01(a, b, n=NQ):
    """Nodes t in (0,1) and weights W with sum W g(t) = int_0^1 g(t) t^b (1-t)^a dt."""
    key = (float(a), float(b), n)
    if key not in _JAC:
        x, w = roots_jacobi(n, a, b)          # weight (1-x)^a (1+x)^b on [-1, 1]
        _JAC[key] = (0.5 * (1.0 + x), w / 2.0 ** (a + b + 1.0))
    return _JAC[key]


class Family:
    """Ansatz f = Phi(E) (L - L0)^l_+, Phi = (1 - E/E0)^k_+ ('poly') or
    (exp(1 - E/E0) - 1)_+ ('king')."""

    def __init__(self, kind, k=0.0, l=0.0, L0=0.0, name=None):
        if kind not in ("poly", "king"):
            raise ValueError(f"unknown family {kind!r}")
        if kind == "king" and k:
            raise ValueError("king has no k")
        self.kind, self.k, self.l, self.L0 = kind, float(k), float(l), float(L0)
        self.name = name or (f"king_l{l:g}_L0{L0:g}" if kind == "king"
                             else f"poly_k{k:g}_l{l:g}_L0{L0:g}")
        self.a = self.k if kind == "poly" else 0.0     # power of (1 - t) in the weight
        self.B1 = Beta(self.l + 1.0, 0.5)
        self.B3 = Beta(self.l + 1.0, 1.5)
        self.B2 = Beta(self.l + 2.0, 0.5)

    def describe(self):
        if self.kind == "poly":
            s = f"f = (1 - E/E0)^{self.k:g}_+"
        else:
            s = "f = (exp(1 - E/E0) - 1)_+"
        if self.l or self.L0:
            s += f" (L - {self.L0:g})^{self.l:g}_+"
        return s

    def phi(self, E_over_E0):
        x = np.asarray(E_over_E0, float)
        if self.kind == "poly":
            return np.where(x < 1.0, np.clip(1.0 - x, 0.0, None) ** self.k, 0.0)
        return np.where(x < 1.0, np.expm1(1.0 - x), 0.0)

    def moments(self, y, r, which=("n", "rho", "p")):
        """Moments at (y, r) (arrays broadcast). Returns dict of arrays."""
        y = np.asarray(y, float)
        r = np.asarray(r, float)
        y, r = np.broadcast_arrays(y, r)
        e = np.exp(y)
        with np.errstate(divide="ignore", invalid="ignore"):
            em2 = np.where(r > 0, 1.0 + self.L0 / np.where(r > 0, r * r, 1.0),
                           1.0 if self.L0 == 0 else np.inf)
        emin = np.sqrt(em2)
        ok = e > emin
        D = np.where(ok, e - np.where(np.isfinite(emin), emin, 0.0), 0.0)
        emin = np.where(np.isfinite(emin), emin, 1.0)
        rl = r ** (2.0 * self.l) if self.l else np.ones_like(r)
        out = {}
        l = self.l
        b1, b3 = l + 0.5, l + 1.5
        if self.kind == "poly":
            pref = np.where(ok, (D / e) ** self.k, 0.0)
        else:
            pref = np.where(ok, 1.0, 0.0)

        def quad(b, fn):
            t, W = _jacobi01(self.a, b)
            eps = emin[..., None] + D[..., None] * t
            g = fn(eps) * (eps + emin[..., None]) ** b
            if self.kind == "king":
                g = g * np.expm1((D / e)[..., None] * (1.0 - t))
            return np.sum(g * W, axis=-1)

        if "n" in which:
            out["n"] = 2 * math.pi * self.B1 * rl * pref * D ** (l + 1.5) * quad(b1, lambda s: s)
        if "rho" in which:
            out["rho"] = 2 * math.pi * self.B1 * rl * pref * D ** (l + 1.5) * quad(b1, lambda s: s * s)
        if "p" in which or "pT" in which:
            J3 = pref * D ** (l + 2.5) * quad(b3, lambda s: np.ones_like(s))
            if "p" in which:
                out["p"] = 2 * math.pi * self.B3 * rl * J3
            if "pT" in which:
                J1 = pref * D ** (l + 1.5) * quad(b1, lambda s: np.ones_like(s))
                with np.errstate(divide="ignore", invalid="ignore"):
                    L0r2 = np.where(r > 0, self.L0 / np.where(r > 0, r * r, 1.0), 0.0)
                out["pT"] = math.pi * rl * (L0r2 * self.B1 * J1 + self.B2 * J3)
        for kx in out:
            out[kx] = np.where(ok, out[kx], 0.0)
        return out

    def eps_density(self, eps, y, r):
        """Unnormalised density in eps of the particles at (y, r): eps Phi (eps^2 -
        eps_min^2)^{l+1/2} (for the momentum sampler and its checks)."""
        e = math.exp(y)
        em2 = 1.0 + self.L0 / (r * r) if self.L0 else 1.0
        eps = np.asarray(eps, float)
        return np.where((eps < e) & (eps * eps > em2),
                        eps * self.phi(eps / e) * np.clip(eps * eps - em2, 0, None) ** (self.l + 0.5),
                        0.0)


# ----------------------------------------------------------------------------
# structure equations
# ----------------------------------------------------------------------------
def _rhs(r, s, fam):
    y, m, N, I = s
    mo = fam.moments(y, r)
    eps2 = 2.0 * m / r
    f = 1.0 - eps2
    sf = math.sqrt(f)
    lm1 = eps2 / (sf * (1.0 + sf))           # e^lambda - 1
    dy = -(m / (r * r) + FOURPI * r * float(mo["p"])) / f
    return [dy, FOURPI * r * r * float(mo["rho"]),
            FOURPI * r * r * (1.0 + lm1) * float(mo["n"]), lm1 / r]


def _edge_event(fam):
    def ev(r, s, *a):
        return math.exp(2.0 * s[0]) - 1.0 - fam.L0 / (r * r)
    ev.terminal = True
    ev.direction = -1
    return ev


def integrate(fam, y0, dense=False):
    """Integrate the structure equations of family `fam` from y(0) = y0 (paper units:
    amplitude 1, rest mass 1). Returns a dict with the surface values and, with dense,
    the OdeSolution `sol` of (y, m, N, I) on [r_start, R]."""
    y0 = float(y0)
    if y0 <= 0.0:
        raise ValueError("y0 must be positive")
    if fam.L0 > 0.0:
        r_in = math.sqrt(fam.L0 / math.expm1(2.0 * y0))
        r0 = r_in * (1.0 + 1e-13)
        s0 = [y0, 0.0, 0.0, 0.0]
        scale = r_in
    else:
        r_in = 0.0
        mo = fam.moments(y0, 0.0 if fam.l == 0 else 1e-300)
        rho_c, p_c, n_c = (float(mo[k]) for k in ("rho", "p", "n"))
        if rho_c > 0:
            Lc = math.sqrt(p_c / (FOURPI * rho_c * rho_c))
        else:
            Lc = 1.0
        r0 = 1e-7 * Lc
        s0 = [y0 - (2 * math.pi / 3) * (rho_c + 3 * p_c) * r0 * r0,
              FOURPI / 3 * rho_c * r0 ** 3, FOURPI / 3 * n_c * r0 ** 3,
              (2 * math.pi / 3) * rho_c * r0 * r0]
        scale = Lc
    sol = solve_ivp(_rhs, (r0, 1e8 * scale), s0, method="DOP853", rtol=RTOL, atol=ATOL,
                    args=(fam,), events=_edge_event(fam), dense_output=dense)
    if sol.status != 1:
        raise RuntimeError(f"{fam.name} y0={y0}: outer edge not reached: {sol.message}")
    R = float(sol.t_events[0][0])
    yR, M, N, IR = (float(v) for v in sol.y_events[0][0])
    E0 = math.exp(yR) * math.sqrt(1.0 - 2.0 * M / R)
    alpha_c = E0 * math.exp(-y0)
    return dict(y0=y0, r_in=r_in, r_start=r0, R=R, yR=yR, M=M, N=N, IR=IR, E0=E0,
                alpha_c=alpha_c, Eb=(N - M) / N, zc_boundary=math.expm1(y0),
                Zc_infinity=1.0 / alpha_c - 1.0, Zc_sqrt=1.0 / math.sqrt(alpha_c) - 1.0,
                compactness=M / R, sol=sol.sol if dense else None, nfev=sol.nfev)


def binding_energy(fam, y0):
    return integrate(fam, y0)["Eb"]


def scan(fam, y0s):
    out = []
    for y0 in y0s:
        d = integrate(fam, y0)
        d.pop("sol")
        out.append(d)
    return out


def first_maximum(fam, y_lo=0.02, y_hi=1.2, n=60):
    """First local maximum of E_b(y0) met as y0 increases from y_lo."""
    from scipy.optimize import minimize_scalar
    ys = np.linspace(y_lo, y_hi, n)
    eb = [binding_energy(fam, v) for v in ys]
    for i in range(1, n - 1):
        if eb[i] >= eb[i - 1] and eb[i] >= eb[i + 1]:
            break
    else:
        raise RuntimeError("no maximum in the scan range")
    res = minimize_scalar(lambda v: -binding_energy(fam, v), bounds=(ys[i - 1], ys[i + 1]),
                          method="bounded", options=dict(xatol=1e-9))
    return float(res.x), float(-res.fun)


def first_zero(fam, y_start, y_hi=3.0, n=60):
    """First zero of E_b(y0) for y0 > y_start (E_b > 0 at y_start)."""
    from scipy.optimize import brentq
    ys = np.linspace(y_start, y_hi, n)
    prev = binding_energy(fam, ys[0])
    for a, b in zip(ys[:-1], ys[1:]):
        cur = binding_energy(fam, b)
        if prev > 0 >= cur:
            return float(brentq(lambda v: binding_energy(fam, v), a, b, xtol=1e-12))
        prev = cur
    raise RuntimeError("no zero in the scan range")


def lane_emden(n_index, xi_max=50.0):
    """Lane-Emden polytrope of index n: first zero xi_1 and rho_c/rho_mean =
    xi_1^3 / (3 |theta'(xi_1)| xi_1^2)."""
    def rhs(x, s):
        th, dth = s
        return [dth, -np.clip(th, 0, None) ** n_index - 2.0 * dth / x]
    x0 = 1e-6
    s0 = [1 - x0 * x0 / 6, -x0 / 3]
    ev = lambda x, s: s[0]
    ev.terminal = True
    ev.direction = -1
    sol = solve_ivp(rhs, (x0, xi_max), s0, method="DOP853", rtol=1e-12, atol=1e-14, events=ev)
    x1 = float(sol.t_events[0][0])
    d1 = float(sol.y_events[0][0][1])
    return dict(xi1=x1, dtheta1=d1, rhoc_over_rhomean=x1 / (3.0 * abs(d1)))


# ----------------------------------------------------------------------------
# equilibrium model in units of its ADM mass
# ----------------------------------------------------------------------------
class Equilibrium:
    """Steady state of `fam` with central (or inner-edge) value y0, scaled to ADM mass M.

    Areal radius r, isotropic radius rbar; profiles are evaluated from the dense ODE
    solution (no splines of the matter), so they carry the integration tolerance.
    """

    def __init__(self, fam, y0, M=1.0):
        d = integrate(fam, y0, dense=True)
        self.fam = fam
        self.raw = d
        self.y0 = d["y0"]
        self.Mscale = s = float(M) / d["M"]     # length (and mass) scale factor raw -> M units
        self.M = float(M)
        self.R = d["R"] * s
        self.r_in = d["r_in"] * s
        self.r_start = d["r_start"] * s
        self.N = d["N"] * s                      # rest mass M0 (number of unit-mass particles)
        self.M0 = self.N
        self.E0 = d["E0"]
        self.alpha_c = d["alpha_c"]
        self.Eb = d["Eb"]
        self.rbar_s = isotropic_from_areal(self.R, self.M)
        self.ln_As = math.log(self.R / self.rbar_s)
        self.IR = d["IR"]
        self._sol = d["sol"]
        # inner vacuum (shell): I = 0 there, A = A(r_in)
        self.A_in = math.exp(self.ln_As + self.IR - 0.0)
        self.rbar_in = self.r_in / self.A_in

    # -- raw solution in M units ------------------------------------------------
    def _state(self, r):
        """(y, m, N, I) at areal radius r (M units), vectorised; inner vacuum and
        exterior handled."""
        r = np.atleast_1d(np.asarray(r, float))
        s = self.Mscale
        y = np.empty_like(r)
        m = np.empty_like(r)
        N = np.empty_like(r)
        I = np.empty_like(r)
        inside = (r >= self.r_start) & (r <= self.R)
        if np.any(inside):
            Z = self._sol(r[inside] / s)
            y[inside], m[inside], N[inside], I[inside] = Z[0], Z[1] * s, Z[2] * s, Z[3]
        low = r < self.r_start
        y[low], m[low], N[low], I[low] = self.y0, 0.0, 0.0, 0.0
        # below r_start (regular centre: 1e-7 of the core scale; shell: inner vacuum)
        # m, N, I are set to zero
        out = r > self.R
        if np.any(out):
            # vacuum: e^{2 mu} = 1 - 2M/r, y = ln E0 - mu; I is not continued (not needed)
            ro = r[out]
            y[out] = math.log(self.E0) - 0.5 * np.log1p(-2.0 * self.M / ro)
            m[out], N[out], I[out] = self.M, self.N, np.nan
        return y, m, N, I

    def lnA(self, r):
        """ln(r/rbar) at areal radius r."""
        y, m, N, I = self._state(r)
        return self.ln_As + self.IR - I

    def rbar_of(self, r):
        r = np.atleast_1d(np.asarray(r, float))
        return r * np.exp(-self.lnA(r))

    def areal_of(self, rbar, iters=64):
        """Areal radius of isotropic radius rbar (matter region and inner vacuum)."""
        rb = np.atleast_1d(np.asarray(rbar, float))
        out = np.empty_like(rb)
        ext = rb >= self.rbar_s
        out[ext] = rb[ext] * (1.0 + self.M / (2.0 * rb[ext])) ** 2
        vac = rb <= self.rbar_in
        out[vac] = rb[vac] * self.A_in
        mid = ~(ext | vac)
        if np.any(mid):
            t = rb[mid]
            lo = np.full_like(t, max(self.r_in, 0.0))
            hi = np.full_like(t, self.R)
            for _ in range(iters):
                c = 0.5 * (lo + hi)
                below = self.rbar_of(c) < t
                lo = np.where(below, c, lo)
                hi = np.where(below, hi, c)
            out[mid] = 0.5 * (lo + hi)
        return out

    # -- profiles as functions of the isotropic radius ------------------------------
    def psi(self, rbar):
        rb = np.atleast_1d(np.asarray(rbar, float))
        out = 1.0 + self.M / (2.0 * np.where(rb > 0, rb, 1.0))
        ins = rb < self.rbar_s
        if np.any(ins):
            out[ins] = np.exp(0.5 * self.lnA(self.areal_of(rb[ins])))
        return out

    def alpha(self, rbar):
        rb = np.atleast_1d(np.asarray(rbar, float))
        h = self.M / (2.0 * np.where(rb > 0, rb, 1.0))
        out = (1.0 - h) / (1.0 + h)
        ins = rb < self.rbar_s
        if np.any(ins):
            y, *_ = self._state(self.areal_of(rb[ins]))
            out[ins] = self.E0 * np.exp(-y)
        return out

    def matter_areal(self, r, which=("n", "rho", "p", "pT")):
        """Moments at areal radius r, in M units (densities scale as 1/length^2)."""
        r = np.atleast_1d(np.asarray(r, float))
        y, *_ = self._state(r)
        mo = self.fam.moments(y, r / self.Mscale, which)
        inside = (r >= self.r_in) & (r <= self.R)
        return {k: np.where(inside, v / self.Mscale ** 2, 0.0) for k, v in mo.items()}

    def matter(self, rbar, which=("n", "rho", "p", "pT")):
        return self.matter_areal(self.areal_of(rbar), which)

    def enclosed_fraction_areal(self, r):
        """N(<r)/N."""
        y, m, N, I = self._state(r)
        return np.clip(N / self.N, 0.0, 1.0)

    def summary(self):
        f = self.fam
        g = dict(family=f.kind, k=f.k, l=f.l, L0_paper_units=f.L0, ansatz=f.describe(),
                 y0=self.y0, zc_boundary=math.expm1(self.y0),
                 Zc_infinity=1.0 / self.alpha_c - 1.0, Eb_over_M0=self.Eb,
                 M_ADM=self.M, M0=self.M0, R_areal=self.R, rbar_s=self.rbar_s,
                 r_in_areal=self.r_in, rbar_in=self.rbar_in, E0=self.E0,
                 alpha_c=self.alpha_c, alpha_s=math.sqrt(1 - 2 * self.M / self.R),
                 psi_c=float(self.psi(0.0)[0]), psi_s=1.0 + self.M / (2 * self.rbar_s),
                 compactness_M_over_R=self.M / self.R,
                 paper_units_length_per_M=1.0 / self.Mscale)
        mc = self.matter_areal(max(self.r_in, self.r_start) * (1 + 1e-9))
        g.update({f"{k}_inner_edge" if f.L0 else f"{k}_c": float(v[0]) for k, v in mc.items()})
        return {k: (float(v) if isinstance(v, (float, int, np.floating)) else v) for k, v in g.items()}

    # -- radial table ---------------------------------------------------------------
    def table_arrays(self, n_matter=4000, rmax_factor=1.5):
        dr = self.rbar_s / n_matter
        n = int(math.ceil(rmax_factor * n_matter)) + 1
        r = dr * np.arange(n)
        return r, self.psi(r) - 1.0, self.alpha(r)

    def write_table(self, path, n_matter=4000, rmax_factor=1.5):
        r, u, a = self.table_arrays(n_matter, rmax_factor)
        hdr = [f"static Einstein-Vlasov equilibrium {self.fam.describe()}, conformally flat "
               "time-symmetric slice (exact static solution)",
               "columns: r (isotropic)  u = psi - 1  alpha (static lapse E0 e^{-y})"]
        hdr += [f"{k} = {v!r}" for k, v in self.summary().items()]
        nio.write_tab(path, r, u, a, header=hdr)
        return r, u, a


# ----------------------------------------------------------------------------
# sampler
# ----------------------------------------------------------------------------
def _eps_R(fam, tt, D, e, emin):
    """Smooth part R(t) of the conditional eps density (rows: particles)."""
    b = fam.l + 0.5
    eps = emin[:, None] + D[:, None] * tt
    g = eps * (eps + emin[:, None]) ** b
    if fam.kind == "king":
        g = g * np.expm1((D / e)[:, None] * (1.0 - tt))
    return g


def _eps_cdf(fam, t, D, e, emin):
    """CDF in t (eps = emin + D t) of the conditional eps density at fixed (y, r), each
    argument an array over particles. Density in t: t^b (1-t)^a R(t), b = l + 1/2,
    R = eps (eps + emin)^b [* expm1(D(1-t)/e) for king]. Below t = 1/2 the integral from 0
    is taken with t' = t s (Gauss-Jacobi weight s^b), above it the integral to 1 with
    t' = 1 - (1-t) s (weight s^a), so each partial integrand is smooth."""
    b = fam.l + 0.5
    a = fam.a
    tq, Wt = _jacobi01(a, b)
    total = np.sum(_eps_R(fam, np.broadcast_to(tq, (len(D), len(tq))), D, e, emin) * Wt, axis=1)
    out = np.empty_like(t)
    lo = t < 0.5
    if np.any(lo):
        s, Ws = _jacobi01(0.0, b)
        tl = t[lo][:, None]
        g = (1.0 - tl * s) ** a * _eps_R(fam, tl * s, D[lo], e[lo], emin[lo])
        out[lo] = t[lo] ** (b + 1.0) * np.sum(g * Ws, axis=1) / total[lo]
    hi = ~lo
    if np.any(hi):
        s, Ws = _jacobi01(0.0, a)
        th = t[hi][:, None]
        tp = 1.0 - (1.0 - th) * s
        g = tp ** b * _eps_R(fam, tp, D[hi], e[hi], emin[hi])
        out[hi] = 1.0 - (1.0 - t[hi]) ** (a + 1.0) * np.sum(g * Ws, axis=1) / total[hi]
    return out


def _invert_eps(fam, U, D, e, emin, iters=56):
    lo = np.zeros_like(U)
    hi = np.ones_like(U)
    for _ in range(iters):
        c = 0.5 * (lo + hi)
        below = _eps_cdf(fam, c, D, e, emin) < U
        lo = np.where(below, c, lo)
        hi = np.where(below, hi, c)
    return emin + D * 0.5 * (lo + hi)


def _perp_basis(n):
    a = np.where(np.abs(n[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
    e1 = np.cross(n, a)
    e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(n, e1)
    return e1, e2


def sample(model, N, method="stratified", seed=1, species=0, chunk=2000):
    """N equal-mass particles of `model`: (x[N,3], u[N,3], m[N], species[N], aux).

    Six coordinates per particle, randomized stratification U_pd = (pi_d(p) + xi_pd)/N
    (paper App. B eq. app_stratified, extended from five to six coordinates) or plain
    Monte Carlo: d = 1 areal radius by the inverse rest-mass CDF; d = 2, 3 position angles;
    d = 4 eps by the inverse conditional CDF at that radius; d = 5 the signed radial
    momentum fraction c = w/(eps^2 - eps_min^2)^{1/2} with density (1 - c^2)^l on [-1, 1]
    (uniform for l = 0, which with L0 = 0 is the isotropic direction cosine); d = 6 the
    azimuth of the tangential momentum. Orthonormal momentum q = w rhat + v_t that,
    lowered as u_i = psi^2 q_i; positions x = rbar rhat."""
    fam = model.fam
    rng = np.random.default_rng(seed)
    if method == "stratified":
        U = stratified_uniforms(N, 6, rng)
    elif method == "mc":
        U = rng.random((N, 6))
    else:
        raise ValueError(method)
    # radius: bisection on N(<r)/N
    lo = np.full(N, max(model.r_in, 0.0))
    hi = np.full(N, model.R)
    for _ in range(64):
        c = 0.5 * (lo + hi)
        below = model.enclosed_fraction_areal(c) < U[:, 0]
        lo = np.where(below, c, lo)
        hi = np.where(below, hi, c)
    r = 0.5 * (lo + hi)
    y, *_ = model._state(r)
    rp = r / model.Mscale                       # paper units for the eps limits
    e = np.exp(y)
    emin = np.sqrt(1.0 + fam.L0 / (rp * rp)) if fam.L0 else np.ones_like(r)
    D = np.clip(e - emin, 0.0, None)
    eps = np.empty(N)
    for i0 in range(0, N, chunk):
        sl = slice(i0, min(N, i0 + chunk))
        eps[sl] = _invert_eps(fam, U[sl, 3], D[sl], e[sl], emin[sl])
    if fam.l == 0:
        cfr = 2.0 * U[:, 4] - 1.0
    else:
        cfr = 2.0 * beta_dist.ppf(U[:, 4], fam.l + 1.0, fam.l + 1.0) - 1.0
    d2 = np.clip(eps * eps - emin * emin, 0.0, None)
    w = cfr * np.sqrt(d2)
    vt = np.sqrt(np.clip(emin * emin - 1.0 + d2 * (1.0 - cfr * cfr), 0.0, None))
    nh = unit_vectors(U[:, 1], U[:, 2])
    e1, e2 = _perp_basis(nh)
    ph = 2.0 * math.pi * U[:, 5]
    q = w[:, None] * nh + vt[:, None] * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2)
    lnA = model.lnA(r)
    rbar = r * np.exp(-lnA)
    x = rbar[:, None] * nh
    u = np.exp(lnA)[:, None] * q                 # psi^2 = A
    m = np.full(N, model.M0 / N)
    aux = dict(r_areal=r, eps=eps, w=w, vt=vt, y=y)
    return x, u, m, np.full(N, species, dtype=np.int32), aux
