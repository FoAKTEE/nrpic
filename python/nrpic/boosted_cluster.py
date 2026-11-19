"""Equilibrium clusters with a bulk momentum: reference solutions, tables and particles
for the table components of the problem generator nrpic_cf that carry a boost table
(``athenak/src/pgen/nrpic/nrpic_clump_table.hpp``; interface
``tracks/core/interfaces/moving_clumps.md``, second pass).

Static cluster (``st_cluster.STModel``): ds^2 = -alpha_0^2 dt^2 + psi_0^4 dx^2, energy
density rho, isotropic pressure P, every particle with E = -u_t = alpha_0 W. To first
order in the velocity V the moving cluster is the same spacetime on the slice
t~ = t + T(x), T -> V.x at infinity. The slice is conformally flat with psi_0, and
maximal (K = 0) if

    d_i (A d_i T) = 0,   A = (alpha_0 psi_0)^2,   T = (V.n) F(r),
    (r^2 A F')' = 2 A F,   F ~ r at the centre,   F/r -> 1 at infinity;

outside the matter F = F_1 + kappa F_2 with F_1 = r + m + m^2/r, F_2 = 1/(r (r - m)),
m = M/2. With w_i = d_i T = V_i w_a + n_i (V.n) w_b, w_a = F/r, w_b = F' - F/r:

    momentum density   Stilde_i = psi_0^6 (rho + P) alpha_0 w_i,
    curvature          K_ij = psi^-2 Abar_ij,
      Abar_ij = 3 Q/(2 r^2) [V_i n_j + V_j n_i - (delta_ij - n_i n_j) V.n]
              + I4/(2 r^4)  [V_i n_j + V_j n_i + (delta_ij - 5 n_i n_j) V.n],
      Q(r)  = 4 pi int_0^r g (2 w_a + F')/3 r'^2 dr',
      I4(r) = 4 pi int_0^r g (2 w_a - F') r'^4 dr',     g = psi_0^6 (rho + P) alpha_0,
    comoving shift     beta^i = -(V^i - alpha_0^2 psi_0^-4 w^i)
                               = -(V^i b_a + n^i (V.n) b_b),

and the total momentum is Q(inf) V (= M V). The two lines for Abar_ij hold for any
polar l = 1 momentum density V_i s_a(r) + n_i (V.n) s_b(r) with
Q = 4 pi int (s_a + s_b/3) r^2, I4 = 4 pi int (s_a - s_b) r^4.

Particles (:meth:`BoostedST.boost_particles`): a static sample (x, u^s_i = psi_0^2 q_i,
m_0) becomes

    u~_i = u^s_i + E w_i(x),          E = alpha_0 W,
    m~   = m_0 (1 + w.xdot),          xdot^i = alpha_0 q^i/(psi_0^2 W),

whose momentum density is the one above for any isotropic static distribution.

Second order (:meth:`BoostedST.correction`): psi = psi_0 + V^2 [y_0(r) + y_2(r) P_2(mu)],
mu the cosine of the angle to V,

    lap dpsi - 2 pi psi_0^4 (rho + 6 P) dpsi
        = -pi psi_0^5 (rho + P) (alpha_0/psi_0^2)^2 |w|^2 - psi_0^-7 Abar_ij Abar_ij/8,

which removes the Hamiltonian residual of the rule above to O(V^4).

A cluster in the nearly constant conformal factor Lambda of other bodies is the isolated
one in the coordinates x^ = Lambda^2 x (``lam``): u(r) = Lambda u^(Lambda^2 r),
Q(r) = Q^(Lambda^2 r), I4(r) = I4^(Lambda^2 r)/Lambda^4, covariant momenta Lambda^2 u^_i,
coordinate velocity V^/Lambda^2, rest masses unchanged.

Derivation, predictions and checks: tracks/core/JOURNAL-clump2.md,
tracks/core/analysis/clump2/. Units G = c = 1. Nothing here evolves anything.
"""

import math

import numpy as np
from scipy.integrate import cumulative_simpson, solve_ivp
from scipy.interpolate import CubicSpline

from . import st_cluster as stc

__all__ = ["BoostedST", "BoostedClusters", "lorentz"]


def lorentz(v):
    """Lorentz factor of the velocity vector v."""
    v2 = float(np.sum(np.asarray(v, dtype=float) ** 2))
    if v2 >= 1.0:
        raise ValueError("speed must be below 1")
    return 1.0 / math.sqrt(1.0 - v2)


class BoostedST:
    """First-order boost of a static cluster ``model`` (st_cluster.STModel) on the
    maximal conformally flat slice, in the constant background conformal factor ``lam``.

    Radii passed to the methods are coordinate radii of the run (r^ = lam^2 r is the
    isolated model's radius). Velocities V are coordinate velocities far from the
    cluster, in the linear rule (V = W_v v for a clump that is to move at the speed v);
    V^ = lam^2 V is the velocity of the isolated solution.

    slice='maximal' (default) or 'plain' (F = r, the Lorentz boost of the isotropic
    coordinates, which is not maximal: for comparison only).
    """

    def __init__(self, model, lam=1.0, slice="maximal"):
        if slice not in ("maximal", "plain"):
            raise ValueError(f"unknown slice {slice!r}")
        self.model = md = model
        self.lam = float(lam)
        self.slice = slice
        self.m = m = 0.5 * md.M
        r = md.rbar
        self.r_nodes = r
        self.rs = rs = float(md.rbar_s)
        psi, alp = md.psi_nodes, md.alpha_nodes
        A = (alp * psi) ** 2
        if slice == "maximal":
            def rhs(rr, y):
                a = float(md._alpha(rr) * md._psi(rr)) ** 2
                return [y[1] / (rr * rr * a), 2.0 * a * y[0]]
            sol = solve_ivp(rhs, (r[1], r[-1]), [r[1], r[1] * r[1] * A[1]],
                            t_eval=r[1:], method="DOP853", rtol=1e-12, atol=1e-20)
            if sol.status != 0:
                raise RuntimeError("slice equation: " + sol.message)
            F = np.concatenate([[0.0], sol.y[0]])
            dF = np.concatenate([[1.0], sol.y[1] / (r[1:] ** 2 * A[1:])])
            # match to C1 F_1 + C2 F_2 at the surface, then normalise C1 = 1
            f1, d1 = rs + m + m * m / rs, 1.0 - m * m / (rs * rs)
            f2 = 1.0 / (rs * (rs - m))
            d2 = -(2.0 * rs - m) / (rs * rs * (rs - m) ** 2)
            c1, c2 = np.linalg.solve([[f1, f2], [d1, d2]], [F[-1], dF[-1]])
            F /= c1
            dF /= c1
            self.kappa = float(c2 / c1)
        else:
            F = r.copy()
            dF = np.ones_like(r)
            self.kappa = None
        self.F_nodes, self.dF_nodes = F, dF
        self._F = CubicSpline(r, F)
        self._dF = CubicSpline(r, dF)
        # (rho + P)/rho_0 = W + zeta g y^(1/2)/y_c (st_cluster.closures), finite at the
        # surface
        y = md.y_nodes
        gy = np.clip(1.0 / y - 1.0, 0.0, None) / (1.0 / md.yc - 1.0)
        hr = 1.0 / np.sqrt(y) + md.zeta * gy * np.sqrt(y) / md.yc
        wa = np.concatenate([[dF[0]], F[1:] / r[1:]])
        self.wa_nodes, self.wb_nodes = wa, dF - wa
        # moments per unit velocity of the isolated solution, by quadrature over the
        # rest-mass shells (dm0 = 4 pi rho_0 psi^6 r^2 dr), exact at the surface
        self.QV_nodes = stc._shell_integral(md, hr * alp * (2.0 * wa + dF) / 3.0)
        self.I4V_nodes = stc._shell_integral(md, hr * alp * (2.0 * wa - dF) * r * r)
        self.pmass_iso = float(self.QV_nodes[-1])
        self.i4_iso = float(self.I4V_nodes[-1])
        self._QV = CubicSpline(r, self.QV_nodes)
        self._I4V = CubicSpline(r, self.I4V_nodes)
        self._corr = None

    # -- scaling ---------------------------------------------------------------
    @property
    def pmass(self):
        """Momentum per unit coordinate velocity, P_i = pmass V_i (lam^4 Q^(inf))."""
        return self.lam ** 4 * self.pmass_iso

    @property
    def conformal_mass(self):
        """2 lim r u(r) of the cluster's own component, M/lam."""
        return self.model.M / self.lam

    def _rh(self, r):
        return self.lam ** 2 * np.abs(np.asarray(r, dtype=float))

    # -- radial functions of the isolated solution ----------------------------
    def F_iso(self, rh):
        """(F, F') of the isolated solution at the model radius rh."""
        rh = np.asarray(rh, dtype=float)
        ins = rh <= self.rs
        ri = np.minimum(rh, self.rs)
        ro = np.where(ins, 2.0 * self.rs, rh)
        m = self.m
        if self.slice == "maximal":
            Fo = ro + m + m * m / ro + self.kappa / (ro * (ro - m))
            dFo = (1.0 - m * m / (ro * ro)
                   - self.kappa * (2.0 * ro - m) / (ro * ro * (ro - m) ** 2))
        else:
            Fo, dFo = ro, np.ones_like(ro)
        return np.where(ins, self._F(ri), Fo), np.where(ins, self._dF(ri), dFo)

    def w_ab_iso(self, rh):
        """(w_a, w_b) = (F/r, F' - F/r) of the isolated solution."""
        rh = np.asarray(rh, dtype=float)
        F, dF = self.F_iso(rh)
        small = rh < 1.0e-9 * self.rs
        wa = np.where(small, self.dF_nodes[0], F / np.where(small, 1.0, rh))
        return wa, dF - wa

    def moments(self, r):
        """Normalised moments (Q, I4) at the run radius r: enclosed fraction of the
        momentum and enclosed second moment per unit momentum (the table columns)."""
        rh = self._rh(r)
        ri = np.minimum(rh, self.rs)
        return (self._QV(ri) / self.pmass_iso,
                self._I4V(ri) / self.pmass_iso / self.lam ** 4)

    def shift_ab(self, r):
        """(b_a, b_b) of the comoving shift beta^i = -(V^i b_a + n^i (V.n) b_b)."""
        rh = self._rh(r)
        wa, wb = self.w_ab_iso(rh)
        c2 = self.model.alpha(rh) ** 2 / self.model.psi(rh) ** 4
        return 1.0 - c2 * wa, -c2 * wb

    # -- fields at points -------------------------------------------------------
    @staticmethod
    def _disp(x, centre):
        d = np.asarray(x, dtype=float) - np.asarray(centre, dtype=float)
        r = np.sqrt(np.sum(d * d, axis=-1))
        rs = np.where(r > 0.0, r, 1.0)
        return d, r, d / rs[..., None]

    def abar(self, x, centre, P):
        """Conformal curvature Abar_ij[..., 3, 3] at x[..., 3] for the momentum P (the
        sum m u_i of the cluster's particles, in the coordinates of the run)."""
        P = np.asarray(P, dtype=float)
        d, r, n = self._disp(x, centre)
        q, i4 = self.moments(r)
        rs = np.where(r > 0.0, r, 1.0)
        ca = np.where(r > 0.0, 1.5 * q / rs ** 2, 0.0)[..., None, None]
        cb = np.where(r > 0.0, 0.5 * i4 / rs ** 4, 0.0)[..., None, None]
        pn = np.sum(P * n, axis=-1)[..., None, None]
        eye = np.eye(3)
        nn = n[..., :, None] * n[..., None, :]
        pnn = P[:, None] * n[..., None, :] + n[..., :, None] * P[None, :]
        return ca * (pnn - (eye - nn) * pn) + cb * (pnn + (eye - 5.0 * nn) * pn)

    def momentum_density(self, x, centre, P):
        """Stilde_i[..., 3], the coordinate density of the covariant momentum that the
        curvature solves the momentum constraint for."""
        P = np.asarray(P, dtype=float)
        d, r, n = self._disp(x, centre)
        rh = self._rh(r)
        md = self.model
        g = md.psi(rh) ** 6 * (md.rho(rh) + md.P(rh)) * md.alpha(rh)
        wa, wb = self.w_ab_iso(rh)
        Vh = P / (self.lam ** 2 * self.pmass_iso)          # velocity of the isolated one
        pn = np.sum(Vh * n, axis=-1)[..., None]
        return self.lam ** 8 * g[..., None] * (Vh * wa[..., None] + n * pn * wb[..., None])

    def shift(self, x, centre, V):
        """Comoving shift beta^i[..., 3] for the coordinate velocity V."""
        V = np.asarray(V, dtype=float)
        d, r, n = self._disp(x, centre)
        ba, bb = self.shift_ab(r)
        vn = np.sum(V * n, axis=-1)[..., None]
        return -(V * ba[..., None] + n * vn * bb[..., None])

    def psi_own(self, x, centre):
        """lam psi_0^(lam^2 r): the conformal factor near the cluster without the
        second-order correction (the cluster's component plus the background lam)."""
        _, r, _ = self._disp(x, centre)
        return self.lam * self.model.psi(self._rh(r))

    # -- particles ----------------------------------------------------------------
    def boost_particles(self, d_iso, u_iso, m0, V_iso):
        """Rule of the module docstring for the isolated cluster: displacements d_iso
        from its centre, static covariant momenta u_iso = psi_0^2 q, rest masses m0,
        velocity V_iso of the linear rule. Returns (u~_iso, m~, W~) with W~ the Lorentz
        factor in psi_0."""
        md = self.model
        V = np.asarray(V_iso, dtype=float)
        r = np.sqrt(np.sum(d_iso * d_iso, axis=1))
        n = d_iso / np.where(r > 0.0, r, 1.0)[:, None]
        p0, a0 = md.psi(r), md.alpha(r)
        q = u_iso / p0[:, None] ** 2
        W = np.sqrt(1.0 + np.sum(q * q, axis=1))
        wa, wb = self.w_ab_iso(r)
        w = V[None, :] * wa[:, None] + n * (n @ V)[:, None] * wb[:, None]
        un = u_iso + (a0 * W)[:, None] * w
        wgt = 1.0 + a0 * np.sum(q * w, axis=1) / (p0 * p0 * W)
        if np.any(wgt <= 0.0):
            raise ValueError("boost too large: a slice-crossing weight is not positive")
        Wn = np.sqrt(1.0 + np.sum(un * un, axis=1) / p0 ** 4)
        return un, m0 * wgt, Wn

    def quiet_sample(self, h):
        """Noise-free static sample for tests: the points h (i + 1/2) inside the surface
        with rest masses rho_0 psi_0^6 h^3, six particles each with the orthonormal
        velocities +-q(r) e_k (exact first and second moments of the isotropic
        distribution at every point). Returns (d_iso, u_iso, m0)."""
        md = self.model
        nh = int(math.ceil(self.rs / h))
        c = (np.arange(-nh, nh) + 0.5) * h
        d = np.stack(np.meshgrid(c, c, c, indexing="ij"), axis=-1).reshape(-1, 3)
        r = np.sqrt(np.sum(d * d, axis=1))
        keep = r < self.rs
        d, r = d[keep], r[keep]
        mass = md.rho0(r) * md.psi(r) ** 6 * h ** 3 / 6.0
        qm = md.q(r) * md.psi(r) ** 2
        ds, us, ms = [], [], []
        for k in range(3):
            for sgn in (1.0, -1.0):
                u = np.zeros_like(d)
                u[:, k] = sgn * qm
                ds.append(d)
                us.append(u)
                ms.append(mass)
        return np.concatenate(ds), np.concatenate(us), np.concatenate(ms)

    # -- second order -------------------------------------------------------------
    def correction(self, r_end=1.0e5, n_out=6000, tol=1.0e-13, maxit=400):
        """Radial functions y_0, y_2 of dpsi = V^^2 [y_0(r^) + y_2(r^) P_2(mu)] of the
        isolated solution per unit V^^2 (V^ the velocity of the linear rule). Returns a
        dict: r (model nodes without the centre, then a geometric grid to r_end rbar_s),
        y0, y2, y0_centre, monopole (lim r y_0), iterations, S0, S2, sigma."""
        if self._corr is not None:
            return self._corr
        md = self.model
        rin = self.r_nodes[1:]
        rout = self.rs * np.geomspace(1.0, r_end, n_out + 1)[1:]
        r = np.concatenate([rin, rout])
        nin = len(rin)
        psi = md.psi(r)
        psi[:nin] = md.psi_nodes[1:]
        alp = md.alpha(r)
        alp[:nin] = md.alpha_nodes[1:]
        rho = np.zeros_like(r)
        prs = np.zeros_like(r)
        rho[:nin] = md.rho_nodes[1:]
        prs[:nin] = md.P_nodes[1:]
        wa, wb = self.w_ab_iso(r)
        wa[:nin], wb[:nin] = self.wa_nodes[1:], self.wb_nodes[1:]
        qv = np.full_like(r, self.pmass_iso)
        i4 = np.full_like(r, self.i4_iso)
        qv[:nin], i4[:nin] = self.QV_nodes[1:], self.I4V_nodes[1:]
        a2, a4 = 1.5 * qv / r ** 2, 0.5 * i4 / r ** 4
        a, b, c = a2 + a4, -a2 + a4, a2 - 5.0 * a4
        # |w|^2 = wa^2 + mu^2 (2 wa wb + wb^2); Abar^2 = 2 a^2 + mu^2 k2
        k2 = 2 * a * a + 4 * a * b + 4 * a * c + 3 * b * b + 2 * b * c + c * c
        mat = math.pi * psi ** 5 * (rho + prs) * alp ** 2 / psi ** 4
        cur = 0.125 / psi ** 7
        c0 = mat * wa * wa + cur * 2.0 * a * a
        cm = mat * (2.0 * wa * wb + wb * wb) + cur * k2
        S = {0: c0 + cm / 3.0, 2: 2.0 * cm / 3.0}
        sigma = 2.0 * math.pi * psi ** 4 * (rho + 6.0 * prs)
        rr = np.concatenate([[0.0], r])
        y = {0: np.zeros_like(r), 2: np.zeros_like(r)}
        info = {}
        it = 0
        for l in (0, 2):
            for it in range(1, maxit + 1):
                g = S[l] - sigma * y[l]
                f1 = np.concatenate([[0.0], r ** (l + 2) * g])
                f2 = np.concatenate([[0.0], r ** (1 - l) * g])
                if l == 0:
                    f2[0] = 0.0     # s g -> 0 at the centre
                i1 = cumulative_simpson(f1, x=rr, initial=0.0)[1:]
                c2 = cumulative_simpson(f2, x=rr, initial=0.0)
                i2 = c2[-1] - c2[1:]
                new = (r ** (-(l + 1)) * i1 + r ** l * i2) / (2 * l + 1)
                err = float(np.max(np.abs(new - y[l])))
                y[l] = new
                if err < tol * max(1.0, float(np.max(np.abs(new)))):
                    break
            else:
                raise RuntimeError(f"correction l = {l}: no convergence ({err:.2e})")
            info[l] = dict(iterations=it, i1_end=float(i1[-1]), centre=float(c2[-1]))
        self._corr = dict(r=r, y0=y[0], y2=y[2], y0_centre=info[0]["centre"],
                          monopole=info[0]["i1_end"], iterations=(info[0]["iterations"],
                                                                  info[2]["iterations"]),
                          S0=S[0], S2=S[2], sigma=sigma, n_inside=nin)
        return self._corr

    def correction_at(self, d_iso, V_iso):
        """dpsi^ of the isolated solution at the displacements d_iso for the velocity
        V_iso of the linear rule."""
        co = self.correction()
        V = np.asarray(V_iso, dtype=float)
        v2 = float(np.sum(V * V))
        r = np.sqrt(np.sum(d_iso * d_iso, axis=-1))
        if v2 == 0.0:
            return np.zeros_like(r)
        mu = np.sum(d_iso * V, axis=-1) / (np.where(r > 0.0, r, 1.0) * math.sqrt(v2))
        lr = np.log(np.maximum(r, co["r"][0]))
        y0 = np.interp(lr, np.log(co["r"]), co["y0"])
        y2 = np.interp(lr, np.log(co["r"]), co["y2"])
        return v2 * (y0 + y2 * 0.5 * (3.0 * mu * mu - 1.0))

    def second_order_mass(self, V_iso):
        """ADM mass that the correction adds to the isolated cluster, 2 monopole V^2."""
        V = np.asarray(V_iso, dtype=float)
        return 2.0 * self.correction()["monopole"] * float(np.sum(V * V))

    # -- tables ---------------------------------------------------------------------
    def radial_table(self, n_matter=4000, rmax_factor=1.5):
        """(r, u, alpha) of the cluster's component in the coordinates of the run:
        u = lam (psi_0^(lam^2 r) - 1), alpha = alpha_0^(lam^2 r), on r_k = k dr with
        dr = rbar_s/(lam^2 n_matter)."""
        dr = self.rs / self.lam ** 2 / n_matter
        n = int(math.ceil(rmax_factor * n_matter)) + 1
        r = dr * np.arange(n)
        rh = self._rh(r)
        return r, self.lam * (self.model.psi(rh) - 1.0), self.model.alpha(rh)

    def boost_table(self, n_matter=4000, rmax_factor=1.5):
        """(r, Q, I4, ba, bb) on the grid of :meth:`radial_table`."""
        r, _, _ = self.radial_table(n_matter, rmax_factor)
        q, i4 = self.moments(r)
        ba, bb = self.shift_ab(r)
        return r, q, i4, ba, bb

    def write_radial_table(self, path, n_matter=4000, rmax_factor=1.5):
        from . import io as nio
        r, u, a = self.radial_table(n_matter, rmax_factor)
        hdr = ["monoenergetic Shapiro-Teukolsky cluster in the background conformal "
               f"factor lam = {self.lam!r}: u = lam (psi_0(lam^2 r) - 1)",
               "columns: r  u  alpha (static lapse of the isolated cluster at lam^2 r)"]
        hdr += [f"{k} = {v!r}" for k, v in self.model.summary().items()]
        nio.write_tab(path, r, u, a, header=hdr)
        return r, u, a

    def write_boost_table(self, path, n_matter=4000, rmax_factor=1.5):
        """Write the boost table (format bst1) read by nrpic_clump_table.hpp."""
        if self.slice != "maximal":
            raise ValueError("the boost table is written for the maximal slice only")
        r, q, i4, ba, bb = self.boost_table(n_matter, rmax_factor)
        lam = self.lam
        with open(path, "w") as f:
            f.write("# nrpic boost table of a table component "
                    "(python/nrpic/boosted_cluster.py)\n")
            f.write("# format = bst1\n")
            f.write(f"# pmass = {self.pmass:.17g}\n")
            f.write(f"# ext_m = {self.m / lam ** 2:.17g}\n")
            f.write(f"# ext_kappa = {self.kappa / lam ** 6:.17g}\n")
            f.write(f"# lam = {lam:.17g}\n# yc = {self.model.yc:.17g}\n"
                    f"# mass = {self.model.M:.17g}\n"
                    f"# i4_last = {float(i4[-1]):.17g}\n")
            f.write("# columns = r Q I4 ba bb\n")
            for row in zip(r, q, i4, ba, bb):
                f.write("%.17e %.17e %.17e %.17e %.17e\n" % row)
        return r, q, i4, ba, bb

    def write_correction_table(self, path, V, dr=None, rlast=None):
        """Write the second-order correction of psi for the coordinate velocity V of the
        linear rule (a table of format mp1, multipoles 0 and 2 about V):
        dpsi(x) = lam dpsi^(lam^2 x) with V^ = lam^2 V."""
        from . import bowen_york as by
        V = np.asarray(V, dtype=float)
        lam = self.lam
        vh2 = lam ** 4 * float(np.sum(V * V))
        if vh2 == 0.0:
            raise ValueError("no correction for a cluster at rest")
        co = self.correction()
        sol = dict(r=co["r"] / lam ** 2, lvals=[0, 2],
                   ul=lam * vh2 * np.array([co["y0"], co["y2"]]),
                   u0_centre=lam * vh2 * co["y0_centre"], m=self.conformal_mass,
                   P=self.pmass * math.sqrt(float(np.sum(V * V))), S=0.0,
                   nonlinear=False,
                   m_adm=self.conformal_mass + 2.0 * vh2 * co["monopole"] / lam)
        dr = self.rs / lam ** 2 / 1000.0 if dr is None else dr
        rlast = 8.0 * self.rs / lam ** 2 if rlast is None else rlast
        return by.write_table(path, sol, dr, rlast, axis=V / math.sqrt(float(np.sum(V * V))),
                              comment="second-order correction of a boosted cluster "
                                      "(python/nrpic/boosted_cluster.py); mass = conformal "
                                      "mass of the component, momentum = pmass |V|")


class BoostedClusters:
    """Several equilibrium clusters with bulk velocities (and optional Brill-Lindquist or
    Bowen-York punctures) for the problem generator nrpic_cf.

    clusters   list of dicts: yc, mass (ADM mass of the isolated cluster), centre,
               v (velocity of the clump far from the others)
    punctures  list of dicts: mass (bare), centre, P, S
    correction True: second-order correction tables of psi are part of the data.

    psi = 1 + sum_c [lam_c (psi^_c(lam_c^2 r_c) - 1) + dpsi_c] + sum_b m_b/(2 r_b); the
    background lam_c of each cluster is 1 plus the conformal potentials of the other
    bodies at its centre (solved self-consistently, the conformal mass of a cluster
    being M_c/lam_c)."""

    def __init__(self, clusters, punctures=(), correction=True, n_nodes=4000):
        def vec(d, key):
            return np.array(d.get(key, (0.0, 0.0, 0.0)), dtype=float)
        self.spec = [dict(yc=float(c["yc"]), mass=float(c.get("mass", 1.0)),
                          centre=vec(c, "centre"), v=vec(c, "v")) for c in clusters]
        self.punctures = [dict(mass=float(b["mass"]), centre=vec(b, "centre"),
                               P=vec(b, "P"), S=vec(b, "S")) for b in punctures]
        if not self.spec:
            raise ValueError("at least one cluster is needed")
        self.with_correction = bool(correction)
        models = {}
        for s in self.spec:
            key = (s["yc"], s["mass"])
            if key not in models:
                models[key] = stc.STModel(s["yc"], M=s["mass"], n_nodes=n_nodes)
            s["model"] = models[key]
        # backgrounds: lam_c = 1 + sum_{j != c} (M_j/lam_j)/(2 d_cj) + punctures
        nc = len(self.spec)
        lam = np.ones(nc)
        for _ in range(200):
            new = np.ones(nc)
            for c, s in enumerate(self.spec):
                for j, o in enumerate(self.spec):
                    if j != c:
                        dist = float(np.linalg.norm(s["centre"] - o["centre"]))
                        new[c] += 0.5 * o["mass"] / lam[j] / dist
                for b in self.punctures:
                    new[c] += 0.5 * b["mass"] / float(np.linalg.norm(s["centre"]
                                                                     - b["centre"]))
            done = np.max(np.abs(new - lam)) < 1e-15
            lam = new
            if done:
                break
        self.lam = lam
        self.boost = []
        cache = {}
        for c, s in enumerate(self.spec):
            key = (id(s["model"]), float(lam[c]))
            if key not in cache:
                cache[key] = BoostedST(s["model"], lam=float(lam[c]))
            self.boost.append(cache[key])
            # velocity of the linear rule: W_v v
            s["V"] = lorentz(s["v"]) * s["v"]
        self.M_adm_first_order = (sum(b.conformal_mass for b in self.boost)
                                  + sum(p["mass"] for p in self.punctures))

    # -- fields ------------------------------------------------------------------
    def psi(self, x, correction=None):
        """Conformal factor of the code at x[..., 3]."""
        x = np.asarray(x, dtype=float)
        corr = self.with_correction if correction is None else correction
        p = np.ones(x.shape[:-1])
        for s, b in zip(self.spec, self.boost):
            d = x - s["centre"]
            r = np.sqrt(np.sum(d * d, axis=-1))
            p = p + b.lam * (b.model.psi(b._rh(r)) - 1.0)
            if corr and np.any(s["V"] != 0.0):
                p = p + b.lam * b.correction_at(b.lam ** 2 * d, b.lam ** 2 * s["V"])
        for q in self.punctures:
            r = np.sqrt(np.sum((x - q["centre"]) ** 2, axis=-1))
            p = p + 0.5 * q["mass"] / r
        return p

    def abar(self, x, momenta):
        """Summed conformal curvature at x for the clusters' momenta (list) and the
        punctures."""
        from . import bowen_york as by
        a = 0.0
        for s, b, P in zip(self.spec, self.boost, momenta):
            a = a + b.abar(x, s["centre"], P)
        for q in self.punctures:
            a = a + by.abar(x, q["centre"], q["P"], q["S"])
        return a

    # -- particles ---------------------------------------------------------------
    def sample(self, N, seed=0, method="stratified", lattice_h=None,
               keep_net_momentum=False):
        """Particles (x, u, m, species) of all clusters, species = index of the cluster.
        method 'stratified' or 'mc': N equal-mass particles per cluster from
        sampling.sample_st (net momentum of the static sample removed unless
        keep_net_momentum); 'quiet': BoostedST.quiet_sample with the spacing lattice_h
        (in the coordinates of the run).
        Each cluster is sampled at rest, boosted with the rule of BoostedST, scaled into
        its background, and every mass is multiplied by the factor that gives the
        particle the m W/psi of the isolated solution in the psi of the code."""
        from . import sampling
        rng = sampling._rng(seed)
        xs, us, ms, sp = [], [], [], []
        parts = []
        for k, (s, b) in enumerate(zip(self.spec, self.boost)):
            lam = b.lam
            if method == "quiet":
                if lattice_h is None:
                    raise ValueError("method 'quiet' needs lattice_h")
                d, u0, m0 = b.quiet_sample(lattice_h * lam ** 2)
            else:
                d, u0, m0, _ = sampling.sample_st(s["model"], N, method, rng)
                if not keep_net_momentum:
                    u0 = u0 - (m0[:, None] * u0).sum(0) / m0.sum()
            Vh = lam ** 2 * s["V"]
            un, mn, Wn = b.boost_particles(d, u0, m0, Vh)
            parts.append((k, s, b, d, un, mn, Wn, Vh))
        for k, s, b, d, un, mn, Wn, Vh in parts:
            lam = b.lam
            x = s["centre"] + d / lam ** 2
            u = lam ** 2 * un
            # m W/psi of the isolated solution in its own (corrected) psi
            r = np.sqrt(np.sum(d * d, axis=1))
            p0 = b.model.psi(r)
            pc = p0.copy()
            if self.with_correction and np.any(Vh != 0.0):
                pc = pc + b.correction_at(d, Vh)
            Wc = np.sqrt(1.0 + np.sum(un * un, axis=1) / pc ** 4)
            pt = self.psi(x)
            Wt = np.sqrt(1.0 + np.sum(u * u, axis=1) / pt ** 4)
            m = mn * (Wc / (lam * pc)) * (pt / Wt)
            xs.append(x)
            us.append(u)
            ms.append(m)
            sp.append(np.full(len(m), k, dtype=np.int32))
        return (np.concatenate(xs), np.concatenate(us), np.concatenate(ms),
                np.concatenate(sp))

    def particle_summary(self, x, u, m, sp):
        """Per cluster: N, sum m, sum m W, sum m u_i (the momentum the curvature is
        given), centre of rest mass, largest orthonormal speed."""
        psi = self.psi(x)
        q2 = np.sum(u * u, axis=1) / psi ** 4
        W = np.sqrt(1.0 + q2)
        out = []
        for k, (s, b) in enumerate(zip(self.spec, self.boost)):
            sel = sp == k
            mu_ = m[sel, None] * u[sel]
            out.append(dict(
                N=int(sel.sum()), sum_m=float(m[sel].sum()),
                sum_mW=float(np.sum(m[sel] * W[sel])),
                sum_m_u=[float(c) for c in mu_.sum(0)],
                continuum_momentum=[float(c) for c in b.pmass * s["V"]],
                centre_m=[float(c) for c in (m[sel, None] * x[sel]).sum(0) / m[sel].sum()],
                v_max=float(np.sqrt(q2[sel] / (1.0 + q2[sel])).max())))
        return out

    def problem_block(self, stem, momenta, lapse=None, boost_shift=False):
        """<problem> block of nrpic_cf (dict) for the files <stem>_c<k>.tab (radial
        table), <stem>_c<k>.bst (boost table), <stem>_c<k>_corr.tab (correction)."""
        ncl = len(self.spec)
        prob = dict(pgen_name="nrpic_cf", ncomp=ncl + len(self.punctures))
        for k, (s, P) in enumerate(zip(self.spec, momenta)):
            pre = f"comp{k}_"
            prob[pre + "type"] = "table"
            prob[pre + "file"] = f"{stem}_c{k}.tab"
            for a in range(3):
                prob[pre + f"x{a + 1}"] = float(s["centre"][a])
            moving = bool(np.any(s["V"] != 0.0))
            if moving:
                prob[pre + "boost_file"] = f"{stem}_c{k}.bst"
                for a in range(3):
                    prob[pre + f"p{a + 1}"] = float(P[a])
                if self.with_correction:
                    prob[pre + "corr"] = "table"
                    prob[pre + "corr_file"] = f"{stem}_c{k}_corr.tab"
                if boost_shift:
                    prob[pre + "boost_shift"] = "true"
        for j, b in enumerate(self.punctures):
            pre = f"comp{ncl + j}_"
            prob[pre + "type"] = "puncture"
            prob[pre + "mass"] = b["mass"]
            for a in range(3):
                prob[pre + f"x{a + 1}"] = float(b["centre"][a])
            if np.any(b["P"] != 0.0) or np.any(b["S"] != 0.0):
                for a in range(3):
                    prob[pre + f"p{a + 1}"] = float(b["P"][a])
                for a in range(3):
                    prob[pre + f"s{a + 1}"] = float(b["S"][a])
        if lapse is None:
            lapse = ("precollapsed" if self.punctures
                     else ("table" if ncl == 1 else "isotropic"))
        prob["lapse"] = lapse
        if lapse == "table":
            prob["lapse_comp"] = 0
        return prob

    def write_tables(self, outdir, stem, n_matter=4000, rmax_factor=1.5):
        """Write the tables of every cluster; returns the list of file names."""
        import os
        names = []
        for k, (s, b) in enumerate(zip(self.spec, self.boost)):
            f = f"{stem}_c{k}.tab"
            b.write_radial_table(os.path.join(outdir, f), n_matter, rmax_factor)
            names.append(f)
            if np.any(s["V"] != 0.0):
                f = f"{stem}_c{k}.bst"
                b.write_boost_table(os.path.join(outdir, f), n_matter, rmax_factor)
                names.append(f)
                if self.with_correction:
                    f = f"{stem}_c{k}_corr.tab"
                    b.write_correction_table(os.path.join(outdir, f), s["V"])
                    names.append(f)
        return names
