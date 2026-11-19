"""Quasi-spherical Szekeres dust with simultaneous bang time (Lambda = 0, G = c = 1).

Metric (arXiv:1708.09143 eq. (ds2), signature (-,+,+,+); sym/sym_szekeres.py checks it):

    ds^2 = -dt^2 + (R' - R Ecal'/Ecal)^2/(1 - k) dr^2 + R^2/Ecal^2 (dp^2 + dq^2),
    Ecal = ((p - P)^2 + (q - Q)^2)/(2S) + S/2,   Rdot^2 = 2M/R - k.

The dust is at rest in (r, p, q); t is its proper time. On the unit sphere of directions n
(stereographic image of (p, q) with centre (P, Q) and scale S),

    Ecal'/Ecal = b(r).n,     b = -(P', Q', S')/S       (sym check E),

so every effect of the dipole enters through the scalar bn = b.n in [-|b|, |b|].

Radial label: r = areal radius R on the initial slice t = t_i = 2/(3H) (as `expball`).
LTB functions from a profile of the mean density contrast Delta(r) inside r:
    M = (H^2/2) r^3 (1 + Delta),  l(lambda_i) - l(0) = -(1/3) ln(1 + Delta),
    k = lambda_i (M/t_i)^(2/3)
(universal.py: R = M^(1/3) t^(2/3) g(lambda), lambda = k t^(2/3)/M^(2/3), l = ln g).
With a = (t/t_i)^(2/3) and lambda = lambda_i a:
    R       = r a exp(l(lambda) - l(lambda_i))
    R'/R    = 1/r + lambda_i' (a l'(lambda) - l'(lambda_i))
    Rdot/R  = (2/(3t)) (1 + lambda l'(lambda))
    Rdot'/R = (Rdot/R)(R'/R) + (2/(3t)) lambda_i' a (l'(lambda) + lambda l''(lambda)).
Fluid scalars and the 3+1 quantities on t = const (lapse 1, shift 0, K_ij = -(1/2) d_t g_ij):
    rho     = M/(4 pi R^3) (M'/M - 3 bn)/(R'/R - bn)                      (szrho)
    K^r_r   = KL = -(Rdot'/R - (Rdot/R) bn)/(R'/R - bn),  K^p_p = K^q_q = KT = -Rdot/R
    Theta   = -(KL + 2 KT)                                                 (sztht)
    Sigma   = -(1/3)(Rdot'/R - (Rdot/R)(R'/R))/(R'/R - bn)                 (szshr)
    W       = M/(3R^3) (3R'/R - M'/M)/(R'/R - bn)                          (szwey)
    gamma_rr = R^2 (R'/R - bn)^2/(1 - k),  gamma_pp = gamma_qq = R^2/Ecal^2.
Regularity: rho > 0 needs M'/(3M) > |b| (density), no shell crossing needs R'/R > |b| at
every time before the shell's crunch.
"""

import math

import numpy as np

from .universal import LAM_CRUNCH, LAM_TA, ell, ell_inverse

__all__ = ["SmoothTopHat", "Flat", "Dipole", "NoDipole", "Szekeres", "bump", "sinf", "dsinf"]


# --------------------------------------------------------------------- profiles
def sinf(u):
    """C-infinity step: 0 for u <= 0, 1 for u >= 1."""
    u = np.asarray(u, dtype=float)
    uc = np.clip(u, 1e-300, 1 - 1e-16)
    with np.errstate(over="ignore"):
        s = 1.0 / (1.0 + np.exp(1.0 / uc - 1.0 / (1.0 - uc)))
    return np.where(u <= 0, 0.0, np.where(u >= 1, 1.0, s))


def dsinf(u):
    u = np.asarray(u, dtype=float)
    s = sinf(u)
    uc = np.clip(u, 1e-300, 1 - 1e-16)
    with np.errstate(over="ignore", invalid="ignore"):
        d = s * (1 - s) * (1.0 / uc ** 2 + 1.0 / (1.0 - uc) ** 2)
    return np.where((u <= 0) | (u >= 1) | ~np.isfinite(d), 0.0, d)


def bump(u):
    """C-infinity bump on (0, 1), maximum 1 at u = 1/2: exp(1 - 1/(1 - (2u - 1)^2))."""
    u = np.asarray(u, dtype=float)
    x = 2 * u - 1
    inside = np.abs(x) < 1
    xc = np.where(inside, x, 0.0)
    return np.where(inside, np.exp(1.0 - 1.0 / (1.0 - xc * xc)), 0.0)


class Flat:
    """Delta = 0: Einstein-de Sitter."""
    R1 = R2 = 0.0

    def Delta(self, r):
        return np.zeros_like(np.asarray(r, dtype=float))

    def dDelta(self, r):
        return np.zeros_like(np.asarray(r, dtype=float))

    def summary(self):
        return dict(profile="flat")


class SmoothTopHat:
    """Delta = delta_c (1 - sinf((r - R1)/(R2 - R1))): homogeneous closed core r <= R1,
    C-infinity transition, Einstein-de Sitter for r >= R2 (compensated). Same definition as
    `expball.model.SmoothTopHat` (written again here; the LTB test compares the two)."""

    def __init__(self, delta_c, R1, R2):
        self.dc, self.R1, self.R2 = float(delta_c), float(R1), float(R2)

    def Delta(self, r):
        return self.dc * (1.0 - sinf((np.asarray(r, dtype=float) - self.R1) / (self.R2 - self.R1)))

    def dDelta(self, r):
        return -self.dc * dsinf((np.asarray(r, dtype=float) - self.R1) / (self.R2 - self.R1)) / (self.R2 - self.R1)

    def summary(self):
        return dict(profile="smooth_tophat", delta_c=self.dc, R1=self.R1, R2=self.R2)


class NoDipole:
    """b = 0: the LTB limit."""
    support = (0.0, 0.0)

    def b(self, r):
        r = np.atleast_1d(np.asarray(r, dtype=float))
        return np.zeros(r.shape + (3,))

    def db(self, r):
        return self.b(r)

    def summary(self):
        return dict(dipole="none")


class Dipole:
    """b(r) = (eps / r) h(u) e(u), u = (r - r1)/(r2 - r1), h the C-infinity bump (max 1),
    e(u) a unit vector. kind='axis': e = z (axisymmetric, one Killing vector);
    kind='twist': e = (sin th cos ph, sin th sin ph, cos th), th = (pi/2) u, ph = pi u, so
    P', Q', S' all vary and the model has no symmetry [BACKGROUND: Bonnor, Sulaiman and
    Tomimura (1977): Szekeres space-times have no Killing vector in general]."""

    def __init__(self, eps, r1, r2, kind="twist"):
        self.eps, self.r1, self.r2, self.kind = float(eps), float(r1), float(r2), kind
        self.support = (self.r1, self.r2)

    def _dir(self, u):
        if self.kind == "axis":
            z = np.zeros_like(u)
            return np.stack([z, z, np.ones_like(u)], -1)
        th, ph = 0.5 * math.pi * u, math.pi * u
        return np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1)

    def b(self, r):
        r = np.atleast_1d(np.asarray(r, dtype=float))
        u = (r - self.r1) / (self.r2 - self.r1)
        amp = self.eps * bump(u) / np.where(r > 0, r, 1.0)
        return amp[..., None] * self._dir(np.clip(u, 0, 1))

    def summary(self):
        return dict(dipole=self.kind, eps=self.eps, r1=self.r1, r2=self.r2)


# --------------------------------------------------------------------- the model
class Szekeres:
    """Quasi-spherical Szekeres model with simultaneous bang time, embedded in
    Einstein-de Sitter for r >= profile.R2 (compensated profile, b = 0 there): outside that
    radius the spacetime is exactly Einstein-de Sitter (a Swiss-cheese hole), or, if the
    caller says so, matched to vacuum as in `expball` (only the LTB functions are used)."""

    def __init__(self, H, profile, dipole=None):
        self.H = float(H)
        self.t_i = 2.0 / (3.0 * self.H)
        self.rho_b = 3.0 * self.H ** 2 / (8.0 * math.pi)
        self.prof = profile
        self.dip = dipole or NoDipole()

    # ---------------------------------------------------------------- radial functions
    def radial(self, r):
        """M, M'/M, k, k', lambda_i, lambda_i', l(lambda_i), l'(lambda_i), Delta at r."""
        r = np.asarray(r, dtype=float)
        D = self.prof.Delta(r)
        dD = self.prof.dDelta(r)
        target = -np.log1p(D) / 3.0                           # l(lambda_i) - l(0)
        lam_i = ell_inverse(target)
        l0, l1, _ = ell(lam_i)
        dlam = -dD / (3.0 * (1.0 + D) * l1)                    # from ln(1+D) = ln(9/2) - 3 l
        M = 0.5 * self.H ** 2 * r ** 3 * (1.0 + D)
        dlnM = 3.0 / r + dD / (1.0 + D)
        c = (M / self.t_i) ** (2.0 / 3.0)
        k = lam_i * c
        dk = c * (dlam + (2.0 / 3.0) * lam_i * dlnM)
        return dict(M=M, dlnM=dlnM, k=k, dk=dk, lam_i=lam_i, dlam=dlam, l_i=l0, dl_i=l1,
                    Delta=D, dDelta=dD)

    def crunch_time(self, r):
        """t (since the bang) of the crunch of shell r; inf if not bound."""
        lam_i = self.radial(r)["lam_i"]
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(lam_i > 0, self.t_i * (LAM_CRUNCH / lam_i) ** 1.5, np.inf)

    def turnaround_time(self, r):
        lam_i = self.radial(r)["lam_i"]
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(lam_i > 0, self.t_i * (LAM_TA / lam_i) ** 1.5, np.inf)

    def horizon_time(self, r):
        """t at which R = 2M on the collapsing branch (the LTB apparent horizon of shell r;
        whether the Szekeres apparent horizon is this surface was not checked here
        [TO VERIFY])."""
        c = self.radial(r)
        k, M = c["k"], c["M"]
        out = np.full_like(np.asarray(r, dtype=float), np.inf)
        b = (k > 0) & (2 * k < 2)
        eta = 2 * math.pi - np.arccos(1.0 - 2.0 * k[b])
        out[b] = M[b] / k[b] ** 1.5 * (eta - np.sin(eta))
        return out

    # ---------------------------------------------------------------- evolution
    def shell(self, t, r):
        """R, R'/R, Rdot/R, Rdot'/R at time t (since the bang) for labels r (broadcast)."""
        t = np.asarray(t, dtype=float)
        c = self.radial(r)
        a = (t / self.t_i) ** (2.0 / 3.0)
        lam = c["lam_i"] * a
        if np.any(lam >= LAM_CRUNCH):
            raise ValueError("a shell has crunched")
        l0, l1, l2 = ell(lam)
        r = np.asarray(r, dtype=float)
        R = r * a * np.exp(l0 - c["l_i"])
        RpR = 1.0 / r + c["dlam"] * (a * l1 - c["dl_i"])
        RdR = (2.0 / (3.0 * t)) * (1.0 + lam * l1)
        RdpR = RdR * RpR + (2.0 / (3.0 * t)) * c["dlam"] * a * (l1 + lam * l2)
        return dict(R=R, RpR=RpR, RdR=RdR, RdpR=RdpR, lam=lam, **c)

    def fields(self, t, r, bn):
        """Fluid scalars and 3+1 quantities at (t, r) and dipole scalar bn = b.n."""
        s = self.shell(t, r)
        den = s["RpR"] - bn
        R3 = s["R"] ** 3
        rho = s["M"] / (4.0 * math.pi * R3) * (s["dlnM"] - 3.0 * bn) / den
        KT = -s["RdR"]
        KL = -(s["RdpR"] - s["RdR"] * bn) / den
        Theta = -(KL + 2.0 * KT)
        Sigma = -(s["RdpR"] - s["RdR"] * s["RpR"]) / (3.0 * den)
        W = s["M"] / (3.0 * R3) * (3.0 * s["RpR"] - s["dlnM"]) / den
        grr = s["R"] ** 2 * den ** 2 / (1.0 - s["k"])
        return dict(rho=rho, KL=KL, KT=KT, K=KL + 2 * KT, Theta=Theta, Sigma=Sigma, W=W,
                    grr=grr, den=den, **s)

    def margins(self, t, r):
        """(R'/R)/|b| and (M'/(3M))/|b| (> 1 means regular for every direction)."""
        s = self.shell(t, r)
        bb = np.linalg.norm(self.dip.b(r), axis=-1)
        with np.errstate(divide="ignore"):
            return s["RpR"] / bb, s["dlnM"] / (3.0 * bb)

    def summary(self):
        return dict(H=self.H, t_i=self.t_i, rho_b=self.rho_b, **self.prof.summary(),
                    **self.dip.summary())
