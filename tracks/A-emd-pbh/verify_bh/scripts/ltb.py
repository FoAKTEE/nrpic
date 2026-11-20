"""Exact Lemaitre-Tolman-Bondi dust solution reconstructed from a format-2 radial table
alone (verifier verify_bh; my own derivation of the formulas, not expball's code).

On the initial slice (alpha = 1, dust at rest relative to the normal observers):
  psi = 1 + u,  R = psi^2 rbar,  dR/drbar = psi^2 + 2 psi psi' rbar,
  |DR|^2 = (dR/drbar)^2 / psi^4 = 1 + 2E,
  v = dR/dtau = -R KT            (code sign: K^theta_theta = -v/R for expansion),
  m = (R/2) (1 + v^2 - |DR|^2)   (Misner-Sharp mass, g^ab dR dR = 1 - 2m/R),
  16 pi rho = -8 psi^-5 (psi'' + 2 psi'/rbar) + 4 KL KT + 2 KT^2   (Hamiltonian constraint),
  KL = -dv/dR                    (momentum constraint, checked, not assumed).
Each shell keeps (m, E) until shells cross; with E < 0 it follows the cycloid
  R = A (1 - cos eta), t = T0 (eta - sin eta), A = m/(-2E), T0 = m/(-2E)^(3/2),
t measured from the shell's own bang; the starting eta_i follows from R(0) = R_i with
dR/dtau > 0. Turnaround eta = pi, marginal trapping R = 2m on the collapsing branch
(cos eta = 1 + 4E), crunch eta = 2 pi. E = 0: R^(3/2) = R_i^(3/2) + (3/2) sqrt(2m) tau.
"""
import numpy as np
from scipy.interpolate import CubicSpline

from vbio import read_tab2

TWO_PI = 2.0 * np.pi


class TableLTB:
    def __init__(self, path):
        self.hdr, self.breaks, d = read_tab2(path)
        self.d = d
        self.r = d[:, 0]
        self.dr = self.r[1] - self.r[0]
        edges = np.concatenate([[-1.0], np.sort(self.breaks), [np.inf]])
        self.edges = edges
        self.pieces = []
        for p in range(len(edges) - 1):
            sel = (self.r > edges[p]) & (self.r < edges[p + 1]) if p > 0 else (self.r < edges[p + 1])
            idx = np.nonzero(sel)[0]
            rr = self.r[idx]
            # clamped-free splines per piece (not-a-knot); the centre row r = 0 belongs to piece 0
            sp = {k: CubicSpline(rr, d[idx, c]) for k, c in (("u", 1), ("KL", 2), ("KT", 3), ("alpha", 4),
                                                              ("betar", 5))}
            self.pieces.append(dict(lo=edges[p], hi=edges[p + 1], idx=idx, sp=sp, rmin=rr[0], rmax=rr[-1]))
        self.r_last = self.r[-1]

    # ------------------------------------------------------------ table fields
    def piece_of(self, r):
        r = np.atleast_1d(np.asarray(r, dtype=float))
        return np.searchsorted(self.edges, r, side="right") - 1

    def field(self, name, r, nu=0, side=None):
        """Piecewise spline of a column (nu-th derivative). side = 'in'/'out' forces the
        piece below/above a break when r sits on it."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        p = self.piece_of(r)
        if side is not None:
            for k, b in enumerate(np.sort(self.breaks)):
                on = np.isclose(r, b, rtol=0, atol=1e-12)
                p[on] = k if side == "in" else k + 1
        out = np.empty_like(r)
        for q in np.unique(p):
            s = p == q
            out[s] = self.pieces[q]["sp"][name](r[s], nu)
        # beyond the last row: u ~ 1/r (zero here), KL, KT ~ r^-3/2 (pg); only used for checks
        far = r > self.r_last
        if np.any(far):
            if name == "u":
                uN = self.d[-1, 1]
                x = r[far]
                out[far] = [uN * self.r_last / x, -uN * self.r_last / x ** 2, 2 * uN * self.r_last / x ** 3][nu]
            elif name in ("KL", "KT"):
                c = {"KL": 2, "KT": 3}[name]
                f0 = self.d[-1, c]
                out[far] = f0 * (r[far] / self.r_last) ** -1.5 * [1.0, -1.5 / r[far], 3.75 / r[far] ** 2][nu]
        return out

    def slice(self, r, side=None):
        """Initial-slice quantities at isotropic radius r."""
        r = np.atleast_1d(np.asarray(r, dtype=float))
        u = self.field("u", r, 0, side)
        du = self.field("u", r, 1, side)
        d2u = self.field("u", r, 2, side)
        KL = self.field("KL", r, 0, side)
        KT = self.field("KT", r, 0, side)
        psi = 1.0 + u
        R = psi ** 2 * r
        dRdr = psi ** 2 + 2.0 * psi * du * r
        DR2 = dRdr ** 2 / psi ** 4
        v = -R * KT
        E = 0.5 * (DR2 - 1.0)
        m = 0.5 * R * (1.0 + v ** 2 - DR2)
        with np.errstate(divide="ignore", invalid="ignore"):
            lap = np.where(r > 0, d2u + 2.0 * du / np.where(r > 0, r, 1.0), 3.0 * d2u)
        rho_H = (-8.0 * psi ** -5 * lap + 4.0 * KL * KT + 2.0 * KT ** 2) / (16.0 * np.pi)
        return dict(r=r, psi=psi, R=R, dRdr=dRdr, DR2=DR2, v=v, E=E, m=m, KL=KL, KT=KT, rho_H=rho_H)

    def rest_mass(self, rmax=None, nsub=400):
        """int rho psi^6 4 pi r^2 dr (u_i = 0, W = 1) by Gauss-Legendre per piece."""
        rmax = self.r_last if rmax is None else rmax
        x, w = np.polynomial.legendre.leggauss(8)
        tot = 0.0
        cuts = np.concatenate([[0.0], np.sort(self.breaks), [rmax]])
        for a, b in zip(cuts[:-1], cuts[1:]):
            g = np.linspace(a, b, nsub + 1)
            for lo, hi in zip(g[:-1], g[1:]):
                rr = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
                s = self.slice(rr)
                tot += 0.5 * (hi - lo) * np.sum(w * s["rho_H"] * s["psi"] ** 6 * 4 * np.pi * rr ** 2)
        return tot


# ---------------------------------------------------------------- shell evolution
def _eta_minus_sin(eta):
    small = eta < 1e-3
    out = eta - np.sin(eta)
    e = eta[small]
    out[small] = e ** 3 / 6.0 - e ** 5 / 120.0 + e ** 7 / 5040.0
    return out


class Shells:
    """Shells labelled by (R_i, m, E) with outgoing initial velocity."""

    def __init__(self, R_i, m, E, tolE=1e-11):
        self.R_i = np.asarray(R_i, float)
        self.m = np.asarray(m, float)
        self.E = np.asarray(E, float)
        self.bound = self.E < -tolE
        self.flat = np.abs(self.E) <= tolE
        self.unbound = self.E > tolE
        n = len(self.R_i)
        self.A = np.full(n, np.nan)
        self.T0 = np.full(n, np.nan)
        self.eta_i = np.full(n, np.nan)
        self.age = np.full(n, np.nan)
        b = self.bound
        self.A[b] = self.m[b] / (-2.0 * self.E[b])
        self.T0[b] = self.m[b] / (-2.0 * self.E[b]) ** 1.5
        # 1 - cos eta = 2 sin^2(eta/2) = R/A, expanding branch eta in (0, pi)
        self.eta_i[b] = 2.0 * np.arcsin(np.sqrt(np.clip(self.R_i[b] / (2.0 * self.A[b]), 0, 1)))
        self.age[b] = self.T0[b] * _eta_minus_sin(self.eta_i[b])
        f = self.flat
        self.age[f] = (2.0 / 3.0) * self.R_i[f] ** 1.5 / np.sqrt(2.0 * self.m[f])
        if np.any(self.unbound):
            u = self.unbound
            self.A[u] = self.m[u] / (2.0 * self.E[u])
            self.T0[u] = self.m[u] / (2.0 * self.E[u]) ** 1.5
            self.eta_i[u] = np.arccosh(1.0 + self.R_i[u] / self.A[u])
            self.age[u] = self.T0[u] * (np.sinh(self.eta_i[u]) - self.eta_i[u])
        # events
        self.tau_ta = np.full(n, np.inf)
        self.tau_c = np.full(n, np.inf)
        self.tau_ah = np.full(n, np.inf)
        self.R_max = np.full(n, np.inf)
        self.tau_ta[b] = np.pi * self.T0[b] - self.age[b]
        self.tau_c[b] = TWO_PI * self.T0[b] - self.age[b]
        self.R_max[b] = 2.0 * self.A[b]
        ok = b & (1.0 + 4.0 * self.E >= -1.0)
        eta_ah = TWO_PI - np.arccos(np.clip(1.0 + 4.0 * self.E[ok], -1, 1))
        self.tau_ah[ok] = self.T0[ok] * _eta_minus_sin(eta_ah) - self.age[ok]

    def R(self, tau):
        """R(tau) for every shell (rows) and every tau (columns); 0 after the crunch.
        A 2-d tau of shape (n_shells, k) gives each shell its own proper times."""
        tau = np.asarray(tau, float)
        n = len(self.R_i)
        if tau.ndim <= 1:
            tau = np.broadcast_to(np.atleast_1d(tau)[None, :], (n, np.atleast_1d(tau).size))
        out = np.zeros(tau.shape)
        b = np.nonzero(self.bound)[0]
        if len(b):
            s = (self.age[b][:, None] + tau[b]) / self.T0[b][:, None]      # eta - sin eta
            lo = np.zeros_like(s)
            hi = np.full_like(s, TWO_PI)
            alive = s < TWO_PI
            for _ in range(64):
                mid = 0.5 * (lo + hi)
                f = _eta_minus_sin(mid.ravel()).reshape(mid.shape) - s
                lo = np.where(f < 0, mid, lo)
                hi = np.where(f >= 0, mid, hi)
            eta = 0.5 * (lo + hi)
            Rb = self.A[b][:, None] * 2.0 * np.sin(0.5 * eta) ** 2
            out[b] = np.where(alive, Rb, 0.0)
        f = np.nonzero(self.flat)[0]
        if len(f):
            out[f] = (self.R_i[f][:, None] ** 1.5 + 1.5 * np.sqrt(2.0 * self.m[f])[:, None] * tau[f]) ** (2.0 / 3.0)
        u = np.nonzero(self.unbound)[0]
        if len(u):
            s = (self.age[u][:, None] + tau[u]) / self.T0[u][:, None]
            lo = np.zeros_like(s)
            hi = np.full_like(s, 50.0)
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                fm = np.sinh(mid) - mid - s
                lo = np.where(fm < 0, mid, lo)
                hi = np.where(fm >= 0, mid, hi)
            eta = 0.5 * (lo + hi)
            out[u] = self.A[u][:, None] * (np.cosh(eta) - 1.0)
        return out


def shells_from_table(T, rbar_i, side=None):
    s = T.slice(rbar_i, side=side)
    sh = Shells(s["R"], s["m"], s["E"])
    sh.rbar_i = np.atleast_1d(np.asarray(rbar_i, float))
    sh.slice0 = s
    return sh
