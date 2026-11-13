"""Monoenergetic Shapiro-Teukolsky equilibrium clusters (Wu & Most, Sec. IV C 1).

Static, spherically symmetric, isotropic Einstein-Vlasov equilibria with the
distribution function f(E) = K delta(E - E_0), where E = -u_t = alpha W is the
conserved Killing energy and E_0 equals the surface lapse.

Dimensionless structure equations (paper Eqs. st-dimensionless .. st-redshift):

    y = exp[2 (Phi - Phi_s)],  x = r_s / L,  zeta = P_c / rho_c = (1 - y_c) / 3,
    L = (P_c / (4 pi rho_c^2))^(1/2),  v = m rho_c / (L P_c),  v_0 = m_0 rho_c / (L P_c),

    g(y)        = (1/y - 1) / (1/y_c - 1)
    rhobar      = (y/y_c)^(-3/2) g^(1/2)
    rhobar_0    = y_c^(1/2) (y/y_c)^(-1) g^(1/2)
    Pbar        = (y/y_c)^(-1/2) g^(3/2)

    dy/dx   = 2 zeta (y/x^2) (v + zeta x^3 Pbar) / (1 - 2 zeta v/x)
    dv/dx   = x^2 rhobar
    dv_0/dx = x^2 rhobar_0 (1 - 2 zeta v/x)^(-1/2)

    R/M = x_s / (zeta v_s),  E_b/M_0 = 1 - v_s/v_0s,
    z_c = [y_c (1 - 2M/R)]^(-1/2) - 1.

Here rho_0 = -n_mu J^mu is the rest-mass density measured by the static
observers, rho = E their energy density, and P the isotropic pressure; for this
distribution every particle at radius r has W = E_0/alpha = y^(-1/2) and
orthonormal speed |q| = (1/y - 1)^(1/2), so rho = W rho_0 exactly.

Integration. From a regular centre series at x_0 = 1e-5 the system is advanced
in x (DOP853, rtol = 1e-13) until y = 1 - (1 - y_c)/4, and then in the variable
s = (1 - y)^(1/2) down to s = 0. In s every right-hand side is analytic at the
surface (rho ~ s, P ~ s^3), so the surface y = 1 is reached exactly with full
order. The isotropic radius follows from d ln rbar / d ln r_s = (1 - 2m/r_s)^(-1/2),
carried as I(x) = int_0^x [(1 - 2 zeta v/x')^(-1/2) - 1] dx'/x', so that
ln A = ln A_s + I_s - I with A = r_s/rbar and A_s = (1 + M/(2 rbar_s))^2 from
the exterior isotropic Schwarzschild metric. The conformal factor is psi = A^(1/2).

All profiles of `STModel` are scaled to the ADM mass M (default 1) and are
functions of the isotropic coordinate radius rbar.
"""

import math
from functools import lru_cache

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar

RTOL = 1e-13
ATOL = 1e-16
X0 = 1e-5            # start of the integration in x (centre series below)
SWITCH = 0.5         # switch to the s variable at s = SWITCH * s_c

__all__ = [
    "closures", "st_surface", "st_global", "eb_over_m0", "STModel",
    "binding_energy_maximum", "migration_target", "yc_from_zc",
    "yc_from_R_over_M", "radial_laplacian", "table_arrays", "write_table",
    "isotropic_from_areal",
]


# ----------------------------------------------------------------------------
# closures and right-hand sides
# ----------------------------------------------------------------------------
def closures(y, yc):
    """Return (rhobar, rho0bar, Pbar) of Eq. st-closures; zero where y >= 1."""
    y = np.asarray(y, dtype=float)
    g = np.clip(1.0 / y - 1.0, 0.0, None) / (1.0 / yc - 1.0)
    r = y / yc
    sg = np.sqrt(g)
    return r ** -1.5 * sg, math.sqrt(yc) * sg / r, g * sg / np.sqrt(r)


def _local(y, g, x, v, yc, zeta):
    """Common pieces of the right-hand side at (x, y, v) with g = g(y)."""
    sg = math.sqrt(g)
    r = y / yc
    rhob = sg / (r * math.sqrt(r))
    rho0b = math.sqrt(yc) * sg / r
    pb = g * sg / math.sqrt(r)
    eps = 2.0 * zeta * v / x                  # 2m/r_s
    f = 1.0 - eps
    sf = math.sqrt(f)
    bm1 = eps / (sf * (1.0 + sf))             # B - 1, B = (1 - 2m/r_s)^(-1/2)
    dydx = 2.0 * zeta * y * (v + zeta * x ** 3 * pb) / (x * x * f)
    return dydx, x * x * rhob, x * x * rho0b * (1.0 + bm1), bm1 / x


def _rhs_x(x, s_, yc, zeta, kc):
    y, v, v0, _ = s_
    g = max(1.0 / y - 1.0, 0.0) * kc
    dydx, dv, dv0, di = _local(y, g, x, v, yc, zeta)
    return [dydx, dv, dv0, di]


def _rhs_s(s, z_, yc, zeta, kc):
    x, v, v0, _ = z_
    y = 1.0 - s * s
    g = s * s / y * kc
    dydx, dv, dv0, di = _local(y, g, x, v, yc, zeta)
    dxds = -2.0 * s / dydx
    return [dxds, dv * dxds, dv0 * dxds, di * dxds]


def _centre(x, yc, zeta):
    """Centre series of (y, v, v0, I) to the order needed at x = X0."""
    y = yc * (1.0 + zeta * (1.0 / 3.0 + zeta) * x * x)
    return [y, x ** 3 / 3.0, math.sqrt(yc) * x ** 3 / 3.0, zeta * x * x / 6.0]


def _integrate(yc, dense=False):
    if not 0.0 < yc < 1.0:
        raise ValueError("y_c must lie in (0, 1)")
    zeta = (1.0 - yc) / 3.0
    kc = 1.0 / (1.0 / yc - 1.0)
    sc = math.sqrt(1.0 - yc)
    s_sw = SWITCH * sc
    y_sw = 1.0 - s_sw * s_sw

    def ev(x, s_, *a):
        return s_[0] - y_sw
    ev.terminal = True
    ev.direction = 1

    s1 = solve_ivp(_rhs_x, (X0, 1e6), _centre(X0, yc, zeta), method="DOP853",
                   rtol=RTOL, atol=ATOL, args=(yc, zeta, kc), events=ev,
                   dense_output=dense)
    if s1.status != 1:
        raise RuntimeError("phase 1 did not reach the switch point: " + s1.message)
    x_sw = s1.t_events[0][0]
    st = s1.y_events[0][0]
    s2 = solve_ivp(_rhs_s, (s_sw, 0.0), [x_sw, st[1], st[2], st[3]],
                   method="DOP853", rtol=RTOL, atol=ATOL, args=(yc, zeta, kc),
                   dense_output=dense)
    if s2.status != 0:
        raise RuntimeError("phase 2 failed: " + s2.message)
    xs, vs, v0s, Is = s2.y[:, -1]
    return dict(yc=yc, zeta=zeta, x_sw=x_sw, s_sw=s_sw, xs=xs, vs=vs, v0s=v0s,
                Is=Is, sol1=s1.sol if dense else None,
                sol2=s2.sol if dense else None)


def isotropic_from_areal(R, M=1.0):
    """Isotropic radius of the Schwarzschild sphere of areal radius R."""
    return 0.5 * R * (1.0 - M / R + math.sqrt(1.0 - 2.0 * M / R))


def _globals(sv):
    yc, zeta = sv["yc"], sv["zeta"]
    R_over_M = sv["xs"] / (zeta * sv["vs"])
    alpha_s = math.sqrt(1.0 - 2.0 / R_over_M)
    alpha_c = alpha_s * math.sqrt(yc)
    return dict(yc=yc, zeta=zeta, xs=sv["xs"], vs=sv["vs"], v0s=sv["v0s"],
                R_over_M=R_over_M, M0_over_M=sv["v0s"] / sv["vs"],
                Eb_over_M0=1.0 - sv["vs"] / sv["v0s"], alpha_s=alpha_s,
                alpha_c=alpha_c, zc=1.0 / alpha_c - 1.0,
                rbar_s_over_M=isotropic_from_areal(R_over_M, 1.0))


@lru_cache(maxsize=4096)
def st_surface(yc):
    """Surface values (x_s, v_s, v_0s, I_s) of the dimensionless integration."""
    sv = _integrate(float(yc), dense=False)
    return sv["xs"], sv["vs"], sv["v0s"], sv["Is"]


def st_global(yc):
    """Scale-free global quantities of the model y_c.

    Returns a dict with R_over_M, M0_over_M, Eb_over_M0, zc, alpha_c (central
    lapse), alpha_s (surface lapse = E_0), rbar_s_over_M, and the raw surface
    values xs, vs, v0s.
    """
    xs, vs, v0s, Is = st_surface(float(yc))
    return _globals(dict(yc=float(yc), zeta=(1.0 - yc) / 3.0, xs=xs, vs=vs,
                         v0s=v0s, Is=Is))


def eb_over_m0(yc):
    """Fractional binding energy E_b/M_0 = 1 - M/M_0 of the model y_c."""
    _, vs, v0s, _ = st_surface(float(yc))
    return 1.0 - vs / v0s


# ----------------------------------------------------------------------------
# full model with radial profiles
# ----------------------------------------------------------------------------
class STModel:
    """Monoenergetic equilibrium y_c with profiles scaled to ADM mass M.

    Node arrays (sorted in rbar, first node at the centre, last at the surface):
        rbar, rs, m, m0, y, alpha, rho, rho0, P, psi, A, W, q
    Scalars: yc, M, R (areal surface radius), rbar_s, M0, Eb_over_M0, zc,
        alpha_c, alpha_s (= E_0), psi_c, rho_c, P_c, L (length unit).
    Callables of the isotropic radius r (vectorised; vacuum values outside):
        psi(r), alpha(r), rho(r), rho0(r), P(r), W(r), q(r), y(r), rs_of(r),
        F(r) = m0(<r)/M0, Finv(U).
    """

    def __init__(self, yc, M=1.0, n_nodes=4000):
        sv = _integrate(float(yc), dense=True)
        g = _globals(sv)
        self.yc = float(yc)
        self.M = float(M)
        self.zeta = zeta = sv["zeta"]
        self.R = g["R_over_M"] * M
        self.M0 = g["M0_over_M"] * M
        self.Eb_over_M0 = g["Eb_over_M0"]
        self.zc = g["zc"]
        self.alpha_c = g["alpha_c"]
        self.alpha_s = self.E0 = g["alpha_s"]
        self.rbar_s = isotropic_from_areal(self.R, M)
        self.L = L = M / (zeta * sv["vs"])
        self.rho_c = zeta / (4.0 * math.pi * L * L)
        self.P_c = zeta * self.rho_c
        self.globals = g

        # phase-1 nodes (uniform in x) and phase-2 nodes (uniform in s)
        x1 = np.linspace(X0, sv["x_sw"], n_nodes)
        Y1 = sv["sol1"](x1)
        s2 = np.linspace(sv["s_sw"], 0.0, n_nodes)[1:]
        Z2 = sv["sol2"](s2)
        x = np.concatenate([[0.0], x1, Z2[0]])
        y = np.concatenate([[self.yc], Y1[0], 1.0 - s2 ** 2])
        v = np.concatenate([[0.0], Y1[1], Z2[1]])
        v0 = np.concatenate([[0.0], Y1[2], Z2[2]])
        I = np.concatenate([[0.0], Y1[3], Z2[3]])
        y[-1] = 1.0
        x[-1], v[-1], v0[-1], I[-1] = sv["xs"], sv["vs"], sv["v0s"], sv["Is"]

        A_s = self.R / self.rbar_s
        lnA = math.log(A_s) + sv["Is"] - I
        self.A = np.exp(lnA)
        self.psi_nodes = np.sqrt(self.A)
        self.psi_c = self.psi_nodes[0]
        self.rs = L * x
        self.rbar = self.rs / self.A
        self.m = zeta * L * v
        self.m0 = zeta * L * v0
        self.y_nodes = y
        rb, r0b, pb = closures(y, self.yc)
        self.rho_nodes = self.rho_c * rb
        self.rho0_nodes = self.rho_c * r0b
        self.P_nodes = self.P_c * pb
        self.alpha_nodes = np.sqrt((1.0 - 2.0 * M / self.R) * y)
        self.W_nodes = 1.0 / np.sqrt(y)
        self.q_nodes = np.sqrt(np.clip(1.0 / y - 1.0, 0.0, None))
        self.F_nodes = v0 / sv["v0s"]

        # splines in rbar (even functions: zero slope at the centre)
        r = self.rbar
        even = ((1, 0.0), "not-a-knot")
        self._psi = CubicSpline(r, self.psi_nodes, bc_type=even)
        self._alpha = CubicSpline(r, self.alpha_nodes, bc_type=even)
        self._y = CubicSpline(r, y, bc_type=even)
        self._rho = CubicSpline(r, self.rho_nodes, bc_type=even)
        self._rho0 = CubicSpline(r, self.rho0_nodes, bc_type=even)
        self._P = CubicSpline(r, self.P_nodes, bc_type=even)
        self._rs = CubicSpline(r, self.rs)
        self._F = CubicSpline(r, self.F_nodes, bc_type=((1, 0.0), "not-a-knot"))

    # -- profiles as functions of the isotropic radius -------------------------
    def _split(self, r):
        r = np.abs(np.asarray(r, dtype=float))
        return r, r <= self.rbar_s

    def psi(self, r):
        r, ins = self._split(r)
        out = 1.0 + self.M / (2.0 * np.where(ins, 1.0, r))
        return np.where(ins, self._psi(np.minimum(r, self.rbar_s)), out)

    def alpha(self, r):
        r, ins = self._split(r)
        h = self.M / (2.0 * np.where(ins, 1.0, r))
        return np.where(ins, self._alpha(np.minimum(r, self.rbar_s)),
                        (1.0 - h) / (1.0 + h))

    def _inside_only(self, spl, r, outside=0.0):
        r, ins = self._split(r)
        return np.where(ins, spl(np.minimum(r, self.rbar_s)), outside)

    def y(self, r):
        return np.clip(self._inside_only(self._y, r, 1.0), None, 1.0)

    def rho(self, r):
        return np.clip(self._inside_only(self._rho, r), 0.0, None)

    def rho0(self, r):
        return np.clip(self._inside_only(self._rho0, r), 0.0, None)

    def P(self, r):
        return np.clip(self._inside_only(self._P, r), 0.0, None)

    def W(self, r):
        """Lorentz factor E_0/alpha = y^(-1/2) of every particle at radius r."""
        return 1.0 / np.sqrt(self.y(r))

    def q(self, r):
        """Orthonormal speed |q| = (W^2 - 1)^(1/2) at radius r."""
        return np.sqrt(np.clip(1.0 / self.y(r) - 1.0, 0.0, None))

    def rs_of(self, r):
        """Areal radius as a function of the isotropic radius."""
        r, ins = self._split(r)
        out = r * (1.0 + self.M / (2.0 * np.where(ins, 1.0, r))) ** 2
        return np.where(ins, self._rs(np.minimum(r, self.rbar_s)), out)

    def F(self, r):
        """Cumulative rest-mass fraction m0(<r)/M0 inside isotropic radius r."""
        r, ins = self._split(r)
        return np.where(ins, np.clip(self._F(np.minimum(r, self.rbar_s)), 0, 1), 1.0)

    def Finv(self, U, iters=60):
        """Inverse of F by vectorised bisection (accurate to the F spline)."""
        U = np.asarray(U, dtype=float)
        lo = np.zeros_like(U)
        hi = np.full_like(U, self.rbar_s)
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            below = self._F(mid) < U
            lo = np.where(below, mid, lo)
            hi = np.where(below, hi, mid)
        return 0.5 * (lo + hi)

    def summary(self):
        """JSON-serialisable scalar description of the model."""
        d = dict(yc=self.yc, M_ADM=self.M,
                 M0=self.M0, Eb_over_M0=self.Eb_over_M0,
                 R_areal=self.R, rbar_s=self.rbar_s, zc=self.zc,
                 alpha_c=self.alpha_c, alpha_s=self.alpha_s, E0=self.E0,
                 psi_c=self.psi_c, psi_s=1.0 + self.M / (2 * self.rbar_s),
                 rho_c=self.rho_c, P_c=self.P_c,
                 rho0_c=self.rho0_nodes[0], zeta=self.zeta, L=self.L)
        return dict(model="st_monoenergetic", **{k: float(v) for k, v in d.items()})


# ----------------------------------------------------------------------------
# sequence utilities
# ----------------------------------------------------------------------------
@lru_cache(maxsize=8)
def binding_energy_maximum(y_hi=0.995, y_lo=0.10, n_scan=90):
    """First maximum of E_b/M_0 met when y_c decreases from y_hi.

    Returns dict(yc, zc, Eb_over_M0, R_over_M, M0_over_M).
    """
    ys = np.linspace(y_hi, y_lo, n_scan)
    eb = np.array([eb_over_m0(v) for v in ys])
    for i in range(1, n_scan - 1):
        if eb[i] >= eb[i - 1] and eb[i] >= eb[i + 1]:
            break
    else:
        raise RuntimeError("no maximum of E_b/M_0 found in the scan range")
    res = minimize_scalar(lambda v: -eb_over_m0(v), bounds=(ys[i + 1], ys[i - 1]),
                          method="bounded", options=dict(xatol=1e-10))
    g = st_global(res.x)
    return dict(yc=float(res.x), zc=g["zc"], Eb_over_M0=g["Eb_over_M0"],
                R_over_M=g["R_over_M"], M0_over_M=g["M0_over_M"])


def migration_target(yc):
    """Other member of the sequence with the same E_b/M_0 (and hence the same
    M_0/M), on the opposite side of the first binding-energy maximum.

    Returns dict(yc, alpha_c, zc, Eb_over_M0, R_over_M, M0_over_M).
    """
    ymax = binding_energy_maximum()["yc"]
    target = eb_over_m0(yc)
    f = lambda v: eb_over_m0(v) - target
    if yc < ymax:
        lo, hi = ymax, 1.0 - 1e-6
    else:
        grid = np.linspace(ymax, 0.02, 200)
        vals = [f(v) for v in grid]
        k = next((j for j in range(1, len(grid)) if vals[j] < 0), None)
        if k is None:
            raise RuntimeError("no member with equal binding fraction found")
        lo, hi = grid[k], grid[k - 1]
    yt = brentq(f, lo, hi, xtol=1e-14, rtol=1e-13)
    g = st_global(yt)
    return dict(yc=yt, alpha_c=g["alpha_c"], zc=g["zc"],
                Eb_over_M0=g["Eb_over_M0"], R_over_M=g["R_over_M"],
                M0_over_M=g["M0_over_M"])


def _invert_sequence(key, value, y_hi=1.0 - 1e-6, y_lo=0.02, n=200):
    grid = np.linspace(y_hi, y_lo, n)
    vals = np.array([st_global(v)[key] - value for v in grid])
    k = np.nonzero(np.sign(vals[1:]) != np.sign(vals[:-1]))[0]
    if len(k) == 0:
        raise ValueError(f"{key} = {value} not reached on the sequence")
    j = k[0]
    return brentq(lambda v: st_global(v)[key] - value, grid[j + 1], grid[j],
                  xtol=1e-14, rtol=1e-13)


def yc_from_zc(zc):
    """Equilibrium-equivalent y_c of a central redshift z_c (inverse of
    Eq. st-redshift along the sequence, branch nearest y_c = 1)."""
    return _invert_sequence("zc", zc)


def yc_from_R_over_M(R_over_M):
    """y_c of the model with compactness R/M (branch nearest y_c = 1)."""
    return _invert_sequence("R_over_M", R_over_M)


# ----------------------------------------------------------------------------
# radial table and constraint check
# ----------------------------------------------------------------------------
def radial_laplacian(r, f):
    """Flat Laplacian f'' + 2 f'/r of an even radial function sampled on the
    uniform grid r_k = k dr, by fourth-order central differences with even
    reflection at r = 0 (one-sided at the outer end). At r = 0 it is 3 f''(0)."""
    r = np.asarray(r, float)
    f = np.asarray(f, float)
    dr = r[1] - r[0]
    fe = np.concatenate([f[2:0:-1], f])                 # f(-2dr), f(-dr), f(0), ...
    n = len(f)
    lap = np.full(n, np.nan)
    i = np.arange(n - 2) + 2                             # index into fe
    d2 = (-fe[i - 2] + 16 * fe[i - 1] - 30 * fe[i] + 16 * fe[i + 1] - fe[i + 2]) / (12 * dr * dr)
    d1 = (fe[i - 2] - 8 * fe[i - 1] + 8 * fe[i + 1] - fe[i + 2]) / (12 * dr)
    rr = r[: n - 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        lap[: n - 2] = np.where(rr > 0, d2 + 2.0 * d1 / rr, 3.0 * d2)
    return lap


def table_arrays(model, n_matter=4000, rmax_factor=1.5):
    """Uniform radial table (r, u = psi - 1, alpha) with dr = rbar_s/n_matter,
    extending to rmax_factor * rbar_s (vacuum isotropic Schwarzschild outside)."""
    dr = model.rbar_s / n_matter
    n = int(math.ceil(rmax_factor * n_matter)) + 1
    r = dr * np.arange(n)
    return r, model.psi(r) - 1.0, model.alpha(r)


def write_table(model, path, n_matter=4000, rmax_factor=1.5):
    """Write the `.tab` radial table of docs/FORMATS.md for this model."""
    from . import io as nio
    r, u, a = table_arrays(model, n_matter, rmax_factor)
    s = model.summary()
    hdr = ["monoenergetic Shapiro-Teukolsky cluster, conformally flat time-symmetric slice",
           "columns: r (isotropic)  u = psi - 1  alpha (static lapse, sqrt((1-2M/R) y))"]
    hdr += [f"{k} = {v!r}" for k, v in s.items()]
    nio.write_tab(path, r, u, a, header=hdr)
    return r, u, a
