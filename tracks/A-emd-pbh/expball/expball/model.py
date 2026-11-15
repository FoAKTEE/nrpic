"""Initial slice of the expanding dust ball (DERIVATION.md, sections 3 and 4).

Lemaitre-Tolman-Bondi dust on the slice t = t_i of the dust's proper time, labelled by the
areal radius R. The data are fixed by the Misner-Sharp mass m(R) and the bound energy E(R):

    v  = sqrt(2m/R + 2E)               (dR/dtau of the shell, expanding)
    KT = -v/R,  KL = -dv/dR            (mixed components, code sign, total derivative)
    rho = m'/(4 pi R^2)                (rest-mass = energy density, dust at rest, u_i = 0)
    gamma = dR^2/(1+2E) + R^2 dOmega^2 = psi^4 (drbar^2 + rbar^2 dOmega^2),
    ln(R/rbar) = int_R^{R_2} (1/sqrt(1+2E) - 1) dR'/R',  psi^2 = R/rbar,
    alpha = 1, beta^R = -v, i.e. betar = beta^rbar = -v/(psi^2 sqrt(1+2E)).

Regions (R_2 the support of the core perturbation, R_b the ball radius, w the optional
edge taper):
    core      R < R_2: simultaneous bang time t_B = 0, t_i = 2/(3H), m = (H^2/2) R^3 (1+Delta),
              E = -y m/R with F(y) = sqrt(1+Delta), F = 2F1(1/2,3/2;5/2;.) (pure growing mode)
    envelope  R_2 <= R <= R_b - w: Einstein-de Sitter, E = 0, v = H R
    taper     |R - R_b| < w: E = 0, rho = rho_b T((R - R_b)/w), T a C^4 smoothstep
    exterior  R > R_b + w: vacuum, m = M, E = 0, v = sqrt(2M/R) (outgoing Painleve-Gullstrand)
Delta(R) is the mean density contrast inside R on the slice; it vanishes for R >= R_2
(compensated profile), so psi = 1 and rbar = R from R_2 outwards.
"""

import math

import numpy as np
from scipy.special import hyp2f1

__all__ = ["Fm1", "dF", "y_of_Delta", "Flat", "TopHat", "Smooth", "SmoothTopHat", "Ball", "PanelCheb",
           "clenshaw", "smoothstep4"]

# --------------------------------------------------------------------- F(y) = 2F1(1/2,3/2;5/2;y)
_NSER = 90
_FC = np.empty(_NSER)
_FC[0] = 1.0
for _k in range(1, _NSER):
    _FC[_k] = _FC[_k - 1] * (0.5 + _k - 1) * (1.5 + _k - 1) / ((2.5 + _k - 1) * _k)


def Fm1(y):
    """F(y) - 1 without cancellation for small |y| (power series for |y| < 1/2)."""
    y = np.asarray(y, dtype=float)
    out = np.empty_like(y)
    s = np.abs(y) < 0.5
    ys = y[s]
    acc = np.zeros_like(ys)
    for c in _FC[:0:-1]:
        acc = acc * ys + c
    out[s] = acc * ys
    out[~s] = hyp2f1(0.5, 1.5, 2.5, y[~s]) - 1.0
    return out


def dF(y):
    """F'(y) = (3/10) 2F1(3/2, 5/2; 7/2; y)."""
    return 0.3 * hyp2f1(1.5, 2.5, 3.5, np.asarray(y, dtype=float))


DELTA_MAX = 9.0 * math.pi ** 2 / 16.0 - 1.0   # F(1)^2 - 1: the shell is at turnaround


def y_of_Delta(D):
    """Solve F(y) = sqrt(1 + Delta) for y = -E R/m (y < 1). Vectorized, safeguarded Newton."""
    D = np.asarray(D, dtype=float)
    if np.any(D <= -1.0) or np.any(D >= DELTA_MAX):
        raise ValueError("Delta must lie in (-1, 9 pi^2/16 - 1): shell not yet at turnaround")
    target = D / (1.0 + np.sqrt(1.0 + D))          # sqrt(1+D) - 1 without cancellation
    # Newton in w = sqrt(1 - y): g(w) = F(1 - w^2) - 1 - target is regular at the
    # turnaround (w -> 0) where F'(y) diverges like (1 - y)^(-1/2); g decreases with w.
    shape = D.shape
    tg = target.ravel()
    w = np.sqrt(1.0 - np.clip(5.0 * D.ravel() / 3.0, -50.0, 0.95))
    lo = np.zeros_like(w)
    hi = np.full_like(w, 1e5)
    act = np.arange(w.size)
    for _ in range(100):
        if act.size == 0:
            break
        wa, ta = w[act], tg[act]
        ya = 1.0 - wa * wa
        r = Fm1(ya) - ta
        conv = np.abs(r) <= 4e-16 * np.maximum(np.abs(ta), 1e-300)
        lo[act] = np.where(r > 0, wa, lo[act])   # g > 0: root at larger w
        hi[act] = np.where(r < 0, wa, hi[act])
        d = -2.0 * wa * dF(ya)
        wn = wa - r / d
        l, h = lo[act], hi[act]
        bad = (wn < l) | (wn > h) | ~np.isfinite(wn)
        wn = np.where(bad, 0.5 * (l + h), wn)
        step_done = np.abs(wn - wa) <= 2e-16 * wa
        w[act] = np.where(conv, wa, wn)
        act = act[~(conv | step_done)]
    y = 1.0 - w * w
    # polish in y where the relative precision of 1 - w^2 is poor (|y| small, F' ~ 0.3)
    sm = np.abs(y) < 0.5
    for _ in range(3):
        ys = y[sm]
        y[sm] = ys - (Fm1(ys) - tg[sm]) / dF(ys)
    return y.reshape(shape)


def smoothstep4(u):
    """C^4 smoothstep: S(0) = 0, S(1) = 1, derivatives 1..4 vanish at both ends."""
    u = np.clip(u, 0.0, 1.0)
    return u ** 5 * (126.0 + u * (-420.0 + u * (540.0 + u * (-315.0 + 70.0 * u))))


# --------------------------------------------------------------------- profiles of Delta(R)
class Flat:
    """No perturbation: the homogeneous, marginally bound ball."""
    name = "flat"
    R2 = 0.0
    breaks = ()

    def Delta(self, R):
        return np.zeros_like(np.asarray(R, dtype=float))

    def dDelta(self, R):
        return np.zeros_like(np.asarray(R, dtype=float))

    def summary(self):
        return dict(profile="flat")


class TopHat:
    """Compensated top-hat in density: delta_c inside R1, delta_u = -delta_c R1^3/(R2^3 - R1^3)
    in R1 < R < R2, so that Delta(R2) = 0. Delta is continuous, Delta' jumps at R1 and R2."""
    name = "tophat"

    def __init__(self, delta_c, R1, R2):
        if not 0 < R1 < R2:
            raise ValueError("need 0 < R1 < R2")
        self.dc, self.R1, self.R2 = float(delta_c), float(R1), float(R2)
        self.breaks = (self.R1,)
        self.delta_u = -self.dc * R1 ** 3 / (R2 ** 3 - R1 ** 3)
        self.delta_min = min(self.dc, self.delta_u)
        if self.delta_u <= -1.0:
            raise ValueError("compensating shell would need negative density")

    def Delta(self, R):
        R = np.asarray(R, dtype=float)
        c = self.dc * self.R1 ** 3 / (self.R2 ** 3 - self.R1 ** 3)
        ring = c * (self.R2 ** 3 - R ** 3) / np.where(R > 0, R, 1.0) ** 3
        return np.where(R <= self.R1, self.dc, np.where(R < self.R2, ring, 0.0))

    def dDelta(self, R):
        R = np.asarray(R, dtype=float)
        c = self.dc * self.R1 ** 3 / (self.R2 ** 3 - self.R1 ** 3)
        ring = -3.0 * c * self.R2 ** 3 / np.where(R > 0, R, 1.0) ** 4
        return np.where(R <= self.R1, 0.0, np.where(R < self.R2, ring, 0.0))

    def summary(self):
        return dict(profile="tophat", delta_c=self.dc, R1=self.R1, R2=self.R2,
                    delta_u=self.delta_u)


class Smooth:
    """Delta(R) = delta_c (1 - x^(2p))^n, x = R/R2 < 1: flat-topped for p >= 2 (the crunch
    time is stationary at the centre to order x^(2p)), C^(n-1) at R2."""
    name = "smooth"

    def __init__(self, delta_c, R2, n=8, p=2):
        self.dc, self.R2, self.n, self.p = float(delta_c), float(R2), int(n), int(p)
        self.breaks = ()
        x = np.linspace(0.0, 1.0, 20001)
        q = x ** (2 * self.p)
        dloc = self.dc * (1 - q) ** (self.n - 1) * ((1 - q) - (2 * self.p * self.n / 3.0) * q)
        self.delta_min = float(dloc.min())
        if self.delta_min <= -1.0:
            raise ValueError("profile would need negative density")

    def Delta(self, R):
        x = np.asarray(R, dtype=float) / self.R2
        return np.where(x < 1.0, self.dc * np.clip(1.0 - x ** (2 * self.p), 0, 1) ** self.n, 0.0)

    def dDelta(self, R):
        x = np.asarray(R, dtype=float) / self.R2
        q = np.clip(1.0 - x ** (2 * self.p), 0, 1)
        val = -self.dc * self.n * q ** (self.n - 1) * 2 * self.p * x ** (2 * self.p - 1) / self.R2
        return np.where(x < 1.0, val, 0.0)

    def summary(self):
        return dict(profile="smooth", delta_c=self.dc, R2=self.R2, n=self.n, p=self.p,
                    local_delta_min=self.delta_min)


def _sinf(u):
    """C-infinity step: 0 for u <= 0, 1 for u >= 1, e^(-1/u)/(e^(-1/u) + e^(-1/(1-u)))."""
    u = np.asarray(u, dtype=float)
    uc = np.clip(u, 1e-300, 1 - 1e-16)
    a = -1.0 / uc
    b = -1.0 / (1.0 - uc)
    with np.errstate(over="ignore"):
        S = 1.0 / (1.0 + np.exp(b - a))
    return np.where(u <= 0, 0.0, np.where(u >= 1, 1.0, S))


def _dsinf(u):
    u = np.asarray(u, dtype=float)
    S = _sinf(u)
    uc = np.clip(u, 1e-3, 1 - 1e-3)
    d = S * (1 - S) * (1.0 / uc ** 2 + 1.0 / (1.0 - uc) ** 2)
    return np.where((u <= 0) | (u >= 1), 0.0, d)


class SmoothTopHat:
    """Homogeneous core Delta = delta_c for R <= R1 joined to Delta = 0 at R2 by a
    C-infinity step: Delta = delta_c (1 - S((R - R1)/(R2 - R1))). The core is an exact closed
    FLRW region (all its shells crunch together, as in Oppenheimer-Snyder) and the data are
    smooth everywhere inside the ball."""
    name = "smooth_tophat"

    def __init__(self, delta_c, R1, R2):
        if not 0 < R1 < R2:
            raise ValueError("need 0 < R1 < R2")
        self.dc, self.R1, self.R2 = float(delta_c), float(R1), float(R2)
        self.breaks = (self.R1,)       # smooth there, but panels split for accuracy
        R = np.linspace(R1, R2, 20001)
        self.delta_min = float(np.min(self.Delta(R) + R * self.dDelta(R) / 3.0))
        if self.delta_min <= -1.0:
            raise ValueError("profile would need negative density")

    def Delta(self, R):
        u = (np.asarray(R, dtype=float) - self.R1) / (self.R2 - self.R1)
        return self.dc * (1.0 - _sinf(u))

    def dDelta(self, R):
        u = (np.asarray(R, dtype=float) - self.R1) / (self.R2 - self.R1)
        return -self.dc * _dsinf(u) / (self.R2 - self.R1)

    def summary(self):
        return dict(profile="smooth_tophat", delta_c=self.dc, R1=self.R1, R2=self.R2,
                    local_delta_min=self.delta_min)


# --------------------------------------------------------------------- Chebyshev panels
def clenshaw(C, p, t):
    """Sum_j C[p, j] T_j(t) for panel indices p and local coordinates t (arrays)."""
    b1 = np.zeros_like(t)
    b2 = np.zeros_like(t)
    for j in range(C.shape[1] - 1, 0, -1):
        b1, b2 = 2.0 * t * b1 - b2 + C[p, j], b1
    return t * b1 - b2 + C[p, 0]


class PanelCheb:
    """Piecewise Chebyshev interpolation of several functions on panels [e_k, e_k+1]."""

    def __init__(self, edges, deg, func, keys):
        self.e = np.asarray(edges, dtype=float)
        self.n = deg + 1
        k = np.arange(self.n)
        self.tk = np.cos(np.pi * (k + 0.5) / self.n)
        a, b = self.e[:-1, None], self.e[1:, None]
        X = 0.5 * (a + b) + 0.5 * (b - a) * self.tk[None, :]
        vals = func(X.ravel())
        T = np.cos(np.outer(k, np.pi * (k + 0.5) / self.n))       # T_j(t_k)
        self.coef = {}
        for key in keys:
            V = np.asarray(vals[key]).reshape(X.shape)
            c = (2.0 / self.n) * V @ T.T
            c[:, 0] *= 0.5
            self.coef[key] = c
        self.keys = tuple(keys)

    def _locate(self, x):
        p = np.clip(np.searchsorted(self.e, x, side="right") - 1, 0, len(self.e) - 2)
        a, b = self.e[p], self.e[p + 1]
        return p, (2.0 * x - a - b) / (b - a)

    def __call__(self, x, keys=None, chunk=1 << 20):
        x = np.asarray(x, dtype=float)
        keys = keys or self.keys
        shp = x.shape
        xf = x.ravel()
        out = {k: np.empty(xf.size) for k in keys}
        for s in range(0, xf.size, chunk):
            p, t = self._locate(xf[s:s + chunk])
            for key in keys:
                out[key][s:s + chunk] = clenshaw(self.coef[key], p, t)
        return {k: v.reshape(shp) for k, v in out.items()}

    def integral_table(self, key):
        """Cumulative integral of `key` from e_0 to each panel edge, and the per-panel
        antiderivative coefficients (for cumulative evaluation at arbitrary x)."""
        from numpy.polynomial import chebyshev as C
        half = 0.5 * (self.e[1:] - self.e[:-1])
        anti = np.array([C.chebint(c, lbnd=-1) * h for c, h in zip(self.coef[key], half)])
        tot = np.array([C.chebval(1.0, a) for a in anti])
        cum = np.concatenate([[0.0], np.cumsum(tot)])
        return cum, anti


# --------------------------------------------------------------------- the ball
_GLX, _GLW = np.polynomial.legendre.leggauss(24)
_GLX8, _GLW8 = np.polynomial.legendre.leggauss(8)


class Ball:
    """Spherical dust ball on the initial slice; see the module docstring.

    H           Hubble rate of the Einstein-de Sitter envelope on the slice
    Rb          areal radius of the ball edge (middle of the taper when edge_width > 0)
    profile     Flat(), TopHat(...) or Smooth(...): Delta(R) with support in [0, R2]
    edge_width  half width w of the C^4 density taper at the edge (0: sharp edge)
    """

    def __init__(self, H, Rb, profile=None, edge_width=0.0, npan=64):
        self.H, self.Rb = float(H), float(Rb)
        self.prof = profile or Flat()
        self.w = float(edge_width)
        self.rho_b = 3.0 * self.H ** 2 / (8.0 * math.pi)
        self.t_i = 2.0 / (3.0 * self.H)
        self.R_in = self.Rb - self.w
        self.R_out = self.Rb + self.w
        if self.prof.R2 > self.R_in:
            raise ValueError("core support R2 must lie inside the envelope (R2 <= Rb - w)")
        self.M = float(self._m_taper(np.array([self.R_out]))[0]) if self.w > 0 \
            else 0.5 * self.H ** 2 * self.Rb ** 3
        # Gauss-Legendre panels for G(R) = int_R^{R2} (1/sqrt f - 1) dR'/R'
        self.R2 = self.prof.R2
        if self.R2 > 0:
            bk = np.unique(np.concatenate([[0.0], list(self.prof.breaks), [self.R2]]))
            edges = np.unique(np.concatenate([np.linspace(bk[i], bk[i + 1], npan + 1)
                                              for i in range(len(bk) - 1)]))
            self._ge = edges
            I = np.array([self._gl(edges[i], edges[i + 1]) for i in range(len(edges) - 1)])
            self._gcum = np.concatenate([np.cumsum(I[::-1])[::-1], [0.0]])  # from edge k to R2
        self._interp = None

    @classmethod
    def from_HRb(cls, HRb, M=1.0, profile=None, edge_width=0.0, **kw):
        """Ball with H R_b = HRb and sharp-edge mass M = H^2 R_b^3/2 (so R_b = 2M/HRb^2)."""
        Rb = 2.0 * M / HRb ** 2
        return cls(HRb / Rb, Rb, profile, edge_width, **kw)

    # ---------------------------------------------------------------- pieces
    def _m_taper(self, R):
        """m(R) in the taper by 8-point Gauss-Legendre (exact: polynomial integrand)."""
        R = np.asarray(R, dtype=float)
        a = self.R_in
        mid, half = 0.5 * (R + a), 0.5 * (R - a)
        Rn = mid[..., None] + half[..., None] * _GLX8
        T = 1.0 - smoothstep4(((Rn - self.Rb) / self.w + 1.0) / 2.0)
        I = (half[..., None] * _GLW8 * T * Rn ** 2).sum(-1)
        return 0.5 * self.H ** 2 * a ** 3 + 4.0 * math.pi * self.rho_b * I

    def _core(self, R):
        H = self.H
        D = self.prof.Delta(R)
        dD = self.prof.dDelta(R)
        y = y_of_Delta(D)
        h = np.sqrt((1 + D) * (1 - y))
        yD = 1.0 / (2.0 * np.sqrt(1 + D) * dF(y))
        hD = ((1 - y) - (1 + D) * yD) / (2.0 * h)
        m = 0.5 * H ** 2 * R ** 3 * (1 + D)
        dm = 1.5 * H ** 2 * R ** 2 * (1 + D) + 0.5 * H ** 2 * R ** 3 * dD
        E = -0.5 * H ** 2 * R ** 2 * (1 + D) * y
        dE = -0.5 * H ** 2 * (2 * R * (1 + D) * y + R ** 2 * dD * (y + (1 + D) * yD))
        v = H * R * h
        dv = H * (h + R * hD * dD)
        rho = self.rho_b * (1 + D + R * dD / 3.0)
        return dict(m=m, dm=dm, E=E, dE=dE, v=v, dv=dv, rho=rho, KT=-H * h, Delta=D, y=y)

    def at(self, R):
        """All slice functions at areal radius R (array): m, dm, E, dE, f = 1+2E, v, dv,
        rho, KL, KT, Delta, y."""
        R = np.atleast_1d(np.asarray(R, dtype=float))
        H = self.H
        out = {k: np.zeros_like(R) for k in ("m", "dm", "E", "dE", "v", "dv", "rho", "KT",
                                            "Delta", "y")}
        core = R < self.R2
        env = (~core) & (R <= self.R_in)
        tap = (R > self.R_in) & (R <= self.R_out) if self.w > 0 else np.zeros_like(core)
        ext = R > self.R_out
        if np.any(core):
            c = self._core(R[core])
            for k, v in c.items():
                out[k][core] = v
        Re = R[env]
        out["m"][env] = 0.5 * H ** 2 * Re ** 3
        out["dm"][env] = 1.5 * H ** 2 * Re ** 2
        out["v"][env] = H * Re
        out["dv"][env] = H
        out["rho"][env] = self.rho_b
        out["KT"][env] = -H
        for sel, mfun, rhofun in ((tap, self._m_taper,
                                   lambda r: self.rho_b * (1 - smoothstep4(((r - self.Rb) / self.w + 1) / 2))),
                                  (ext, lambda r: np.full_like(r, self.M),
                                   lambda r: np.zeros_like(r))):
            if not np.any(sel):
                continue
            Rs = R[sel]
            m = mfun(Rs)
            rho = rhofun(Rs)
            dm = 4.0 * math.pi * Rs ** 2 * rho
            v = np.sqrt(2.0 * m / Rs)
            out["m"][sel] = m
            out["dm"][sel] = dm
            out["rho"][sel] = rho
            out["v"][sel] = v
            out["dv"][sel] = (dm / Rs - m / Rs ** 2) / v
            out["KT"][sel] = -v / Rs
        out["f"] = 1.0 + 2.0 * out["E"]
        out["KL"] = -out["dv"]
        return out

    # ---------------------------------------------------------------- conformal map
    def _g(self, R):
        """Integrand (1/sqrt f - 1)/R of the conformal map, without cancellation."""
        c = self._core(R)
        f = 1.0 + 2.0 * c["E"]
        if np.any(f <= 0):
            raise ValueError("1 + 2E <= 0: the slice would close")
        sf = np.sqrt(f)
        return (-2.0 * c["E"] / R) / (sf * (1.0 + sf))

    def _gl(self, a, b):
        x = 0.5 * (a + b) + 0.5 * (b - a) * _GLX
        return 0.5 * (b - a) * np.sum(_GLW * self._g(x))

    def G(self, R):
        """ln(R/rbar) = int_R^{R2} (1/sqrt(1+2E) - 1) dR'/R' (zero for R >= R2)."""
        R = np.atleast_1d(np.asarray(R, dtype=float))
        out = np.zeros_like(R)
        if self.R2 <= 0:
            return out
        s = R < self.R2
        Rs = R[s]
        p = np.clip(np.searchsorted(self._ge, Rs, side="right") - 1, 0, len(self._ge) - 2)
        b = self._ge[p + 1]
        mid, half = 0.5 * (Rs + b), 0.5 * (b - Rs)
        X = mid[:, None] + half[:, None] * _GLX[None, :]
        part = half * np.sum(_GLW[None, :] * self._g(X.ravel()).reshape(X.shape), axis=1)
        out[s] = part + self._gcum[p + 1]
        return out

    def rbar_of_R(self, R):
        R = np.atleast_1d(np.asarray(R, dtype=float))
        return R * np.exp(-self.G(R))

    def R_of_rbar(self, rb):
        """Areal radius at isotropic radius rbar (Newton on ln R - G(R) = ln rbar)."""
        rb = np.atleast_1d(np.asarray(rb, dtype=float))
        R = rb.copy()
        if self.R2 <= 0:
            return R
        rb2 = float(self.rbar_of_R(np.array([self.R2]))[0])
        s = (rb < rb2) & (rb > 0)
        if not np.any(s):
            return R
        x = rb[s] * np.exp(self.G(rb[s]))
        x = np.minimum(x, self.R2 * (1 - 1e-15))
        for _ in range(60):
            c = self.at(x)
            phi = np.log(x) - self.G(x) - np.log(rb[s])
            xn = x - phi * x * np.sqrt(c["f"])
            xn = np.clip(xn, 0.5 * x, np.minimum(2.0 * x, self.R2))
            done = np.all((np.abs(xn - x) <= 2e-15 * x) | (np.abs(phi) <= 4e-16))
            x = xn
            if done:
                break
        R[s] = x
        return R

    def rbar_edges(self):
        """Isotropic radii of the non-smooth points of the data (0 excluded)."""
        pts = list(self.prof.breaks) + ([self.R2] if self.R2 > 0 else [])
        pts += [self.R_in, self.R_out] if self.w > 0 else [self.Rb]
        return np.unique(self.rbar_of_R(np.array(pts)))

    # ---------------------------------------------------------------- functions of rbar
    def slice_at_rbar(self, rb):
        """Exact slice functions at isotropic radius rbar (slow: Newton + quadrature)."""
        rb = np.atleast_1d(np.asarray(rb, dtype=float))
        R = self.R_of_rbar(rb)
        out = self.at(R)
        G = self.G(R)
        out["R"] = R
        out["psi"] = np.exp(0.5 * G)
        out["u"] = np.expm1(0.5 * G)
        out["betar"] = -out["v"] / (out["psi"] ** 2 * np.sqrt(out["f"]))
        out["alpha"] = np.ones_like(rb)
        out["dM0drb"] = 4.0 * math.pi * out["rho"] * out["psi"] ** 6 * rb ** 2
        return out

    KEYS = ("R", "u", "psi", "KL", "KT", "rho", "betar", "m", "E", "v", "dM0drb")

    def radial(self, rbar_max=None, npan=48, deg=20):
        """High-accuracy piecewise-Chebyshev interpolant in rbar of the slice functions,
        with panels split at every non-smooth radius. Cached."""
        if self._interp is not None and rbar_max is None:
            return self._interp
        rmax = rbar_max or 1.6 * self.R_out
        br = np.concatenate([[0.0], self.rbar_edges(), [rmax]])
        br = np.unique(br[br <= rmax])
        edges = np.unique(np.concatenate([np.linspace(br[i], br[i + 1], npan + 1)
                                          for i in range(len(br) - 1)]))
        self._interp = PanelCheb(edges, deg, self.slice_at_rbar, self.KEYS)
        self._interp.rbar_max = rmax
        return self._interp

    def fields(self, rb, keys=("u", "KL", "KT", "rho", "betar")):
        """Slice functions at rbar from the interpolant inside rbar_max, exact vacuum
        (psi = 1, outgoing Painleve-Gullstrand) beyond."""
        I = self.radial()
        rb = np.asarray(rb, dtype=float)
        out = {k: np.empty_like(rb) for k in keys}
        inside = rb <= I.rbar_max
        if np.any(inside):
            v = I(rb[inside], keys)
            for k in keys:
                out[k][inside] = v[k]
        if np.any(~inside):
            r = rb[~inside]
            vv = np.sqrt(2.0 * self.M / r)
            vac = dict(R=r, u=0 * r, psi=1 + 0 * r, KL=vv / (2 * r), KT=-vv / r, rho=0 * r,
                       betar=-vv, m=self.M + 0 * r, E=0 * r, v=vv, dM0drb=0 * r)
            for k in keys:
                out[k][~inside] = vac[k]
        return out

    # ---------------------------------------------------------------- rest mass
    def rest_mass_table(self):
        I = self.radial()
        if not hasattr(I, "_m0"):
            I._m0 = I.integral_table("dM0drb")
        return I._m0

    def rest_mass_inside(self, rb):
        """Rest mass inside isotropic radius rbar (Chebyshev antiderivative, vectorized)."""
        I = self.radial()
        cum, anti = self.rest_mass_table()
        rb = np.asarray(rb, dtype=float)
        rr = np.minimum(rb, I.rbar_max).ravel()
        p, t = I._locate(rr)
        return (cum[p] + clenshaw(anti, p, t)).reshape(rb.shape)

    def rest_mass(self):
        return float(self.rest_mass_table()[0][-1])

    def matter_rbar(self):
        """Isotropic radius of the outer edge of the matter."""
        return float(self.rbar_of_R(np.array([self.R_out]))[0])

    def max_compactness(self, n=20001):
        R = np.linspace(1e-6 * self.R_out, 1.5 * self.R_out, n)
        c = self.at(R)
        q = 2 * c["m"] / R
        k = int(np.argmax(q))
        return float(q[k]), float(R[k])

    def summary(self):
        q, Rq = self.max_compactness()
        I = self.radial()
        psi0 = float(np.exp(0.5 * self.G(np.array([0.0]))[0]))
        return dict(H=self.H, Rb=self.Rb, HRb=self.H * self.Rb, edge_width=self.w,
                    M_misner_sharp=self.M, rho_b=self.rho_b, t_i=self.t_i,
                    hubble_radius=1.0 / self.H, rbar_matter=self.matter_rbar(),
                    rest_mass=self.rest_mass(), psi_centre=psi0,
                    max_2m_over_R=q, R_at_max_2m_over_R=Rq,
                    anti_trapped_surface_on_slice=bool(q >= 1.0),
                    interp_rbar_max=float(I.rbar_max), **self.prof.summary())
