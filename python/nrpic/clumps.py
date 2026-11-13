"""Relativistic cluster with two Gaussian overdensities ("Jeans" problem; Wu & Most,
Sec. "Jeans collapse and binary evolution in a relativistic cluster", paper lines
1335-1338).

Conformally flat, time-symmetric slice, gamma_ij = psi^4 delta_ij, K_ij = 0, with

    psi_tot(x) = 1 + u_env(|x|) + u_A(|x - x_A|) + u_B(|x - x_B|),
    Lap u_k = -2 pi rho~_k      (flat Laplacian, conformal source rho~_k),

so that psi_tot solves the Hamiltonian constraint Lap psi = -2 pi rho psi^5 for the
energy density rho = (rho~_env + rho~_A + rho~_B) psi_tot^-5. The ADM mass is the
sum of the conformal masses int rho~_k d^3x = M_env + 2 m_c.

Envelope   monoenergetic equilibrium cluster (st_cluster.STModel) of gravitational
           mass M_env (its ADM mass in isolation): u_env = psi_env - 1 in the
           isotropic radius, rho~_env = rho_env psi_env^5.
Clumps     rho~ = m_c (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2)),
           u = (m_c/2) erf(r/(sqrt(2) sigma))/r, centred at x_A = (-d, 0, 0) and
           x_B = (+d, 0, 0), bulk orthonormal velocities v_A = (0, -v, 0) and
           v_B = (0, +v, 0) (static = normal observers, beta = 0).

Particles. The deposited energy density is E = sum_p m_p W_p delta^3(x - x_p)/psi^6,
so the coordinate density of m W of each component k must be rho~_k psi_tot:
  species 0  envelope: positions and orthonormal velocities q exactly as the
             isolated-cluster sampler draws them (sampling.sample_st), then
             u_i = psi_tot^2 q_i and m = (M0_env/N_env) psi_tot/psi_env, with M0_env
             the rest mass of the isolated envelope.
  species 1  clump A: isotropic Gaussian positions about x_A, stratified in r,
             cos(theta), phi; cold, q = W v_A, u_i = psi_tot^2 q_i,
             m = (m_c/N_c) psi_tot/W, W = (1 - v^2)^(-1/2).
  species 2  clump B: as A about x_B with v_B. By default (mirror=True) its
             positions are the images of clump A's under the pi rotation about z,
             (x, y, z) -> (-x, -y, z), which maps x_A -> x_B, v_A -> v_B and leaves
             psi_tot invariant; the clump pair then has exactly zero net momentum and
             centre of mass at the origin. The image of a stratified Gaussian sample
             is again a stratified Gaussian sample (phi -> phi + pi).

Continuum values (for checks; `continuum`): for component k with Lorentz factor
W_k (W_env = y^(-1/2) of the isolated model, W for the clumps),
    conformal mass  int rho~_k d^3x
    sum m W         int rho~_k psi_tot d^3x
    rest mass       int rho~_k psi_tot / W_k d^3x
The integrals use the axisymmetry of psi_tot about the x axis: Gauss-Legendre in
the cosine mu of the angle to the x axis on spheres about the component centre,
and Gauss-Legendre in the radius (with s = r_max - r_max t^2 for the envelope, so
that its rho ~ (rbar_s - r)^(1/2) surface behaviour is integrated exactly).

Note: with K_ij = 0 the momentum constraint D_j K^j_i = 8 pi S_i is not satisfied
by the moving clumps (S ~ rho W v); the data are exact for the Hamiltonian
constraint only, as in the paper.
"""

import math
from functools import lru_cache

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar
from scipy.special import erf

from . import sampling
from . import st_cluster as stc

__all__ = ["gaussian_u", "gaussian_rho", "split_counts", "JeansModel", "DEFAULTS"]

DEFAULTS = dict(M_env=0.76, R_env=30.0, m_clump=0.12, sigma=0.70, d=3.0,
                v=0.133215, split=(3, 1, 1))

_SQRT2 = math.sqrt(2.0)


# ----------------------------------------------------------------------------
# Gaussian component
# ----------------------------------------------------------------------------
def gaussian_u(r, m, sigma):
    """u(r) = (m/2) erf(r/(sqrt 2 sigma))/r, with the limit m/(sqrt(2 pi) sigma) at 0."""
    r = np.abs(np.asarray(r, dtype=float))
    t = r / (_SQRT2 * sigma)
    small = t < 1e-6
    rs = np.where(small, 1.0, r)
    u0 = m / (math.sqrt(2.0 * math.pi) * sigma)
    return np.where(small, u0 * (1.0 - t * t / 3.0), 0.5 * m * erf(t) / rs)


def gaussian_rho(r, m, sigma):
    """Conformal source m (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2))."""
    r = np.asarray(r, dtype=float)
    return m * (2.0 * math.pi * sigma * sigma) ** -1.5 * np.exp(-0.5 * (r / sigma) ** 2)


def split_counts(N, split=(3, 1, 1)):
    """Particle numbers (N_env, N_A, N_B) for the ratio split (3:1:1 -> 6000, 2000,
    2000 for N = 10^4); the clump counts are rounded, the envelope takes the rest."""
    tot = float(sum(split))
    na = int(round(N * split[1] / tot))
    nb = int(round(N * split[2] / tot))
    return N - na - nb, na, nb


@lru_cache(maxsize=16)
def _leggauss(n):
    return np.polynomial.legendre.leggauss(n)


def _gl01(n, panels=1):
    """Composite Gauss-Legendre nodes and weights on [0, 1]."""
    x, w = _leggauss(n)
    edges = np.linspace(0.0, 1.0, panels + 1)
    h = np.diff(edges)
    t = (edges[:-1, None] + 0.5 * h[:, None] * (x[None, :] + 1.0)).ravel()
    wt = (0.5 * h[:, None] * w[None, :]).ravel()
    return t, wt


# ----------------------------------------------------------------------------
# model
# ----------------------------------------------------------------------------
class JeansModel:
    """Envelope + two Gaussian clumps on the conformally flat time-symmetric slice.

    M_env, R_env   gravitational mass and areal surface radius of the isolated
                   envelope (y_c = yc_from_R_over_M(R_env/M_env)); give `yc` to
                   select the envelope by its central y_c instead (R_env ignored).
    m_clump, sigma conformal mass and Gaussian width of each clump.
    d, v           clump centres (-d, 0, 0), (d, 0, 0); bulk orthonormal speeds
                   v^y = -v (A) and +v (B).
    Component indices: 0 envelope, 1 clump A, 2 clump B (= particle species).
    """

    names = ("envelope", "clump_A", "clump_B")

    def __init__(self, M_env=DEFAULTS["M_env"], R_env=DEFAULTS["R_env"], yc=None,
                 m_clump=DEFAULTS["m_clump"], sigma=DEFAULTS["sigma"], d=DEFAULTS["d"],
                 v=DEFAULTS["v"], n_nodes=4000):
        if yc is None:
            yc = stc.yc_from_R_over_M(R_env / M_env)
        self.env = stc.STModel(float(yc), M=float(M_env), n_nodes=n_nodes)
        self.yc = self.env.yc
        self.M_env = float(M_env)
        self.m_c = float(m_clump)
        self.sigma = float(sigma)
        self.d = float(d)
        self.v = float(v)
        if not 0.0 <= abs(self.v) < 1.0:
            raise ValueError("clump speed must satisfy |v| < 1")
        self.W = 1.0 / math.sqrt(1.0 - self.v * self.v)
        self.centres = np.array([[0.0, 0.0, 0.0], [-self.d, 0.0, 0.0], [self.d, 0.0, 0.0]])
        self.velocities = np.array([[0.0, -self.v, 0.0], [0.0, self.v, 0.0]])
        self.M_adm = self.M_env + 2.0 * self.m_c
        self._m_env_spl = CubicSpline(self.env.rbar, self.env.m)

    # -- radial profiles of the components -------------------------------------
    def u_radial(self, k, r):
        """Conformal-factor excess u_k as a function of the distance to its centre."""
        if k == 0:
            return self.env.psi(r) - 1.0
        return gaussian_u(r, self.m_c, self.sigma)

    def rho_tilde_radial(self, k, r):
        """Conformal source rho~_k (rho_env psi_env^5 for the envelope)."""
        if k == 0:
            return self.env.rho(r) * self.env.psi(r) ** 5
        return gaussian_rho(r, self.m_c, self.sigma)

    def W_radial(self, k, r):
        """Lorentz factor of the component's particles (static observers)."""
        if k == 0:
            return self.env.W(r)
        return np.full_like(np.asarray(r, dtype=float), self.W)

    # -- fields at arbitrary points x[..., 3] ----------------------------------
    def _dist(self, x, k):
        x = np.asarray(x, dtype=float)
        return np.sqrt(np.sum((x - self.centres[k]) ** 2, axis=-1))

    def parts(self, x):
        """(u_env, u_A, u_B) at the points x[..., 3]."""
        return tuple(self.u_radial(k, self._dist(x, k)) for k in range(3))

    def psi_env(self, x):
        return self.env.psi(self._dist(x, 0))

    def psi(self, x):
        """psi_tot = 1 + u_env + u_A + u_B at the points x[..., 3]."""
        ue, ua, ub = self.parts(x)
        return 1.0 + ue + ua + ub

    def lapse(self, x):
        """Suggested initial lapse (2 - psi_tot)/psi_tot (isotropic-Schwarzschild form)."""
        p = self.psi(x)
        return (2.0 - p) / p

    def rho_tilde(self, x):
        """Total conformal source rho~_env + rho~_A + rho~_B at x[..., 3]."""
        return sum(self.rho_tilde_radial(k, self._dist(x, k)) for k in range(3))

    def energy_density(self, x):
        """Physical energy density rho = rho~ psi_tot^-5 seen by the static observers."""
        return self.rho_tilde(x) / self.psi(x) ** 5

    def lorentz_factor(self, x, u):
        """W = (1 + psi_tot^-4 |u|^2)^(1/2) of particles at x with covariant u_i."""
        p = self.psi(x)
        return np.sqrt(1.0 + np.sum(np.asarray(u) ** 2, axis=-1) / p ** 4)

    # -- quadrature over shells about a component centre ----------------------
    def _rmax(self, k):
        return self.env.rbar_s if k == 0 else 12.0 * self.sigma

    def shell_integral(self, k, g, r1=0.0, r2=None, n_r=32, panels=16, n_mu=128):
        """int rho~_k(s) g(x, s) d^3x over the shell r1 <= s < r2 about centre k.

        g(x, s) takes points x[n_r, n_mu, 3] and their distance s[n_r, 1] to the
        centre; g must be axisymmetric about the x axis (any function of psi_tot,
        of the component radii, or of the distances to the three centres is)."""
        rmax = self._rmax(k)
        r2 = rmax if r2 is None else min(float(r2), rmax)
        r1 = float(r1)
        if r2 <= r1:
            return 0.0
        t, wt = _gl01(n_r, panels)
        if k == 0:                       # s = r2 - (r2 - r1) t^2
            s = r2 - (r2 - r1) * t * t
            ws = 2.0 * (r2 - r1) * t * wt
        else:
            s = r1 + (r2 - r1) * t
            ws = (r2 - r1) * wt
        mu, wm = _leggauss(n_mu)
        n = np.stack([mu, np.sqrt(1.0 - mu * mu), np.zeros_like(mu)], axis=-1)
        pts = self.centres[k] + s[:, None, None] * n[None, :, :]
        vals = np.broadcast_to(g(pts, s[:, None]), pts.shape[:2])
        avg = 0.5 * (vals @ wm)
        return float(np.sum(ws * 4.0 * math.pi * s * s * self.rho_tilde_radial(k, s) * avg))

    def shell_values(self, k, r1=0.0, r2=None, **kw):
        """(conformal mass, sum m W, rest mass) of component k in the shell [r1, r2)."""
        conf = self.shell_integral(k, lambda x, s: 1.0, r1, r2, **kw)
        mW = self.shell_integral(k, lambda x, s: self.psi(x), r1, r2, **kw)
        rest = self.shell_integral(k, lambda x, s: self.psi(x) / self.W_radial(k, s),
                                   r1, r2, **kw)
        return conf, mW, rest

    def continuum(self):
        """Continuum conformal mass, sum m W and rest mass of each component and in
        total (dict keyed by component name and 'total')."""
        out = {}
        tot = np.zeros(3)
        for k, name in enumerate(self.names):
            v = np.array(self.shell_values(k))
            tot += v
            out[name] = dict(conformal_mass=v[0], sum_mW=v[1], rest_mass=v[2])
        out["total"] = dict(conformal_mass=tot[0], sum_mW=tot[1], rest_mass=tot[2])
        return {a: {b: float(c) for b, c in d.items()} for a, d in out.items()}

    # -- characteristic numbers -----------------------------------------------
    def psi_axis_extremum(self):
        """Maximum of psi_tot on the x axis near clump A: (x, psi, lapse)."""
        f = lambda s: -float(self.psi(np.array([s, 0.0, 0.0])))
        a = -self.d - 3.0 * self.sigma
        b = -self.d + 3.0 * self.sigma
        res = minimize_scalar(f, bounds=(a, b), method="bounded",
                              options=dict(xatol=1e-10))
        p = -res.fun
        return float(res.x), p, (2.0 - p) / p

    def areal_radius_composite(self, n_mu=256):
        """Areal radius sqrt(A/4pi) of the coordinate sphere rbar_s (the envelope's
        surface) in the composite metric psi_tot^4 delta_ij."""
        mu, wm = _leggauss(n_mu)
        rb = self.env.rbar_s
        pts = rb * np.stack([mu, np.sqrt(1 - mu * mu), 0 * mu], axis=-1)
        return float(rb * math.sqrt(0.5 * np.sum(wm * self.psi(pts) ** 4)))

    def envelope_mass_inside(self, r):
        """(gravitational m, rest m0, conformal) envelope mass inside isotropic r."""
        r = float(r)
        m = float(self._m_env_spl(r)) if r < self.env.rbar_s else self.M_env
        m0 = float(self.env.M0 * self.env.F(r))
        conf = self.shell_integral(0, lambda x, s: 1.0, 0.0, r)
        return m, m0, conf

    def newtonian_circular_speed(self):
        """Leading-order circular speed of a clump at radius d:
            v^2 = m_env(<d)/d + m_c d/(2d)^2 = m_env(<d)/d + m_c/(4 d),
        the envelope's gravitational mass function m(r_s) at the isotropic radius d
        (shell theorem) plus the pull of the other clump at distance 2d, both
        directed to the origin. Variants with the envelope rest mass and conformal
        mass inside d are returned for comparison."""
        d = self.d
        m, m0, conf = self.envelope_mass_inside(d)
        other = self.m_c / (4.0 * d)
        return dict(formula="v^2 = m_env(<d)/d + m_c/(4 d)", d=d,
                    m_env_inside=m, m0_env_inside=m0, conf_env_inside=conf,
                    other_clump_term=other,
                    v_circ=math.sqrt(m / d + other),
                    v_circ_rest_mass=math.sqrt(m0 / d + other),
                    v_circ_conformal_mass=math.sqrt(conf / d + other),
                    v_envelope_only=math.sqrt(m / d), v_clump_only=math.sqrt(other),
                    v_set=self.v, ratio_v_set_over_v_circ=self.v / math.sqrt(m / d + other))

    def summary(self):
        """JSON-serialisable description of the model (no particles)."""
        env = self.env.summary()
        env.pop("M_ADM")
        env = dict(note="isolated-envelope model values (STModel scaled to M_env), "
                        "except R_areal_composite",
                   M_env=self.M_env, R_over_M_env=self.env.R / self.M_env, **env,
                   R_areal_composite=self.areal_radius_composite())
        o = np.zeros(3)
        xa = self.centres[1]
        xm, pm, am = self.psi_axis_extremum()
        return dict(
            model="st_envelope_two_gaussian_clumps", M_ADM=self.M_adm,
            envelope=env,
            clumps=dict(m_c=self.m_c, sigma=self.sigma, x_A=list(self.centres[1]),
                        x_B=list(self.centres[2]), separation=2.0 * self.d,
                        v_A=list(self.velocities[0]), v_B=list(self.velocities[1]),
                        W=self.W, q_y=self.W * self.v,
                        circular_speed_check=self.newtonian_circular_speed()),
            psi_tot=dict(origin=float(self.psi(o)), x_A=float(self.psi(xa)),
                         x_B=float(self.psi(self.centres[2])),
                         axis_max=pm, axis_max_at_x=xm),
            lapse_isotropic=dict(formula="(2 - psi_tot)/psi_tot",
                                 origin=float(self.lapse(o)), x_A=float(self.lapse(xa)),
                                 axis_min=am),
            continuum=self.continuum(),
        )

    # -- particles --------------------------------------------------------------
    def sample(self, N, seed=0, method="stratified", split=DEFAULTS["split"],
               mirror=True):
        """Particles (x[N,3], u[N,3], m[N], species[N]) of envelope (0), clump A (1)
        and clump B (2), in this order; counts split_counts(N, split)."""
        rng = sampling._rng(seed)
        n_env, n_a, n_b = split_counts(N, split)
        if mirror and n_a != n_b:
            raise ValueError("mirror=True needs equal clump particle numbers")
        # envelope: the isolated-cluster sampler, then corrected for the clumps
        x0, u0, _, _ = sampling.sample_st(self.env, n_env, method, rng)
        r0 = np.sqrt(np.sum(x0 * x0, axis=1))
        pe = self.env.psi(r0)
        q0 = u0 / pe[:, None] ** 2
        pt = self.psi(x0)
        xs, us, ms = [x0], [pt[:, None] ** 2 * q0], [(self.env.M0 / n_env) * pt / pe]
        # clumps
        xa = sampling.sample_gaussian_positions(n_a, self.sigma, self.centres[1], method, rng)
        if mirror:
            xb = xa * np.array([-1.0, -1.0, 1.0])
        else:
            xb = sampling.sample_gaussian_positions(n_b, self.sigma, self.centres[2],
                                                    method, rng)
        for xc, vel, n in ((xa, self.velocities[0], n_a), (xb, self.velocities[1], n_b)):
            pt = self.psi(xc)
            xs.append(xc)
            us.append(pt[:, None] ** 2 * (self.W * vel)[None, :])
            ms.append((self.m_c / n) * pt / self.W)
        sp = np.concatenate([np.full(n, k, dtype=np.int32)
                             for k, n in enumerate((n_env, n_a, n_b))])
        return np.concatenate(xs), np.concatenate(us), np.concatenate(ms), sp

    def particle_summary(self, x, u, m, sp):
        """Per-species sums: N, sum m, sum m W, sum m u_i, J_z = sum m (x u_y - y u_x),
        centre of m W."""
        W = self.lorentz_factor(x, u)
        out = {}
        for k, name in enumerate(self.names + ("total",)):
            sel = (sp == k) if k < 3 else np.ones(len(m), bool)
            mw = m[sel] * W[sel]
            mu_ = m[sel, None] * u[sel]
            out[name] = dict(
                N=int(sel.sum()), sum_m=float(m[sel].sum()), sum_mW=float(mw.sum()),
                sum_m_u=[float(c) for c in mu_.sum(0)],
                J_z=float(np.sum(x[sel, 0] * mu_[:, 1] - x[sel, 1] * mu_[:, 0])),
                centre_mW=[float(c) for c in (mw[:, None] * x[sel]).sum(0) / mw.sum()],
                m_min=float(m[sel].min()), m_max=float(m[sel].max()))
        return out
