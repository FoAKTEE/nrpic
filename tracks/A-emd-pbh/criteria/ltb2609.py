"""Spherical Lemaitre-Tolman-Bondi test profile of arXiv:2609.14218, in two forms.

1. `Profile2609`: the closed forms of the paper, in its own conventions (G = c = 1), coded
   from the TeX source (kb-data/raw/arxiv/2609.14218/v1/src/MDPBH.tex, line numbers below):
     metric  ds^2 = -dt^2 + (d_r R)^2/(1 - ktilde r^2) dr^2 + R^2 dOmega^2          564
     (d_t R)^2 = -ktilde r^2 + m r^3/(3R),  Misner-Sharp mass M = m r^3/6           573, 586
     R = r m^(1/3) (t - t_b)^(2/3) S(x),  x = ktilde ((t - t_b)/m)^(2/3),  S of     593-619
     t_b = 0 (decaying modes excluded)                                              625
     matching to the long-wavelength data ds^2 = -dt^2 + a^2 Psi^4 (dr^2 + r^2 dOmega^2),
     a = (t/t_i)^(2/3), a_i = 1:  m(r) = 4 Psi^6/(3 t_i^2),                         673-680
                                  ktilde(r) = [1 - (1 + 2 r d_r ln Psi)^2]/r^2       695
     profile  ln Psi = (mu/2) exp(-k^2 r^2/6),  so zeta = 2 ln Psi = mu e^(-(r/r_m)^2)  704
     compaction radius k^2 r_m^2 = 6; horizon entry k^2/(aH)^2 = 6, i.e. a H r_m = 1  709-714
     singularity t_s(r) = (pi/3) m ktilde^(-3/2)                                     743
   r is the isotropic comoving radius of the long-wavelength metric (637).

   THRESHOLD STATEMENT (read at the source): "for mu = 0.33 ... the spacetime structure is
   locally naked, and the singularity is hidden by the event horizon from the asymptotic
   observers"; "for mu = 0.32, the spacetime structure is globally naked" (766-768), with
   "We may safely say PBH forms if the singularity is locally naked but not globally naked"
   (752-753). So the LTB threshold of this profile is mu_c in (0.32, 0.33] [VERIFIED as
   read]. It is the spherical (e = p = 0) end of the paper's Fig. thre_p0 (red arrows,
   976). It is a statement about the causal structure of the exact dust solution, not about
   an apparent horizon on a slice: the paper notes that slices of a locally naked case can
   touch the singularity before an apparent horizon appears (778-779, 794-798).

2. `LTBPeak2609`: the same spacetime as a profile object of the expanding-ball package
   (`tracks/A-emd-pbh/expball`, `expball/model.py`): attributes name, R2, breaks,
   delta_min, methods Delta(R), dDelta(R), summary(), where Delta(R) is the mean density
   contrast inside the areal radius R on the slice of simultaneous bang time and Delta = 0
   for R >= R2. The slice is the paper's reference slice t_i with a_i = 1 and H = 2/(3 t_i)
   (expball's H); the comoving compaction radius Rm (isotropic r_m in code units) fixes
   k = sqrt(6)/Rm. The paper's profile has a Gaussian tail; expball needs compact support,
   so Delta is multiplied by a C-infinity step from 1 at R_a = cut[0] Rm to 0 at
   R2 = cut[1] Rm [JUDGEMENT: at cut[0] = 3 the exact Delta is ~1e-4 of its central value].
   Inside R_a the data are the exact LTB data of the paper's profile.

   Construction. For the shell r: rhat = r Psi^2 (comoving areal radius, 656),
   M = (H^2/2) rhat^3 (from 680 and 586), E = -ktilde r^2/2 (573). On the slice, with
   expball's y = -E R/M and F = 2F1(1/2, 3/2; 5/2; .), the simultaneous bang time gives
   F(y) = sqrt(1 + Delta) and y = kappa (1 + Delta)^(-1/3), kappa = ktilde/(H^2 Psi^4); so
   y solves y F(y)^(2/3) = kappa (one root in [0, 1) for 0 <= kappa < (3 pi/4)^(2/3)),
   Delta = F(y)^2 - 1, R = rhat (1 + Delta)^(-1/3). A shell with kappa >= (3pi/4)^(2/3) is
   past its turnaround on the slice and cannot be represented (expball's construction is
   on the expanding branch): `max_mu_on_slice` gives the largest mu a slice holds.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXPBALL_DIR = os.path.normpath(os.path.join(HERE, "..", "expball"))
if EXPBALL_DIR not in sys.path:
    sys.path.insert(0, EXPBALL_DIR)
from expball.model import Fm1, dF  # noqa: E402  (F - 1 and F' of expball)

MU_GLOBALLY_NAKED = 0.32
MU_LOCALLY_NAKED = 0.33
THRESHOLD_LOCATOR = "2609.14218 v1 MDPBH.tex:766-768 (criterion 752-753, procedure 748-751)"
KAPPA_TURN = (3.0 * math.pi / 4.0) ** (2.0 / 3.0)     # y = 1: shell at turnaround on the slice


# ------------------------------------------------------------------- cycloid helpers (own)
def _s_minus_sin(s):
    s0 = np.asarray(s, dtype=float)
    s = np.atleast_1d(s0).copy()
    out = s - np.sin(s)
    sm = np.abs(s) < 0.3
    x = s[sm]
    x2 = x * x
    out[sm] = x * x2 / 6.0 * (1 - x2 / 20.0 * (1 - x2 / 42.0 * (1 - x2 / 72.0 * (1 - x2 / 110.0))))
    return out.reshape(s0.shape)


def solve_s(q):
    """s in [0, 2 pi] with s - sin s = q (q in [0, 2 pi]); bisection-safeguarded Newton."""
    q = np.atleast_1d(np.asarray(q, dtype=float))
    lo = np.zeros_like(q)
    hi = np.full_like(q, 2.0 * math.pi)
    s = np.clip(np.cbrt(6.0 * q), 0.0, 2.0 * math.pi)
    for _ in range(200):
        f = _s_minus_sin(s) - q
        lo = np.where(f < 0, s, lo)
        hi = np.where(f > 0, s, hi)
        d = 2.0 * np.sin(0.5 * s) ** 2
        sn = np.where(d > 0, s - f / np.where(d > 0, d, 1.0), 0.5 * (lo + hi))
        bad = (sn <= lo) | (sn >= hi) | ~np.isfinite(sn)
        sn = np.where(bad, 0.5 * (lo + hi), sn)
        if np.all(np.abs(sn - s) <= 1e-15 * np.maximum(s, 1e-300)):
            s = sn
            break
        s = sn
    return s


# ------------------------------------------------------------------- the paper's closed forms
class Profile2609:
    """LTB solution of MDPBH.tex:560-768 for ln Psi = (mu/2) exp(-k^2 r^2/6), t_b = 0,
    reference time t_i with a(t_i) = 1."""

    def __init__(self, mu, k, t_i):
        self.mu, self.k, self.t_i = float(mu), float(k), float(t_i)
        self.r_m = math.sqrt(6.0) / self.k                         # 709
        self.H_i = 2.0 / (3.0 * self.t_i)
        # horizon entry of r_m, a H r_m = 1 (714): t_H = t_i (H_i r_m)^3 (718 for H_i = 5k)
        self.t_H = self.t_i * (self.H_i * self.r_m) ** 3

    def zeta(self, r):
        return self.mu * np.exp(-(self.k * np.asarray(r, float)) ** 2 / 6.0)

    def rzeta1(self, r):
        """r zeta'(r) = 2 r d_r ln Psi."""
        u = (self.k * np.asarray(r, float)) ** 2 / 6.0
        return -2.0 * self.mu * u * np.exp(-u)

    def psi(self, r):
        return np.exp(0.5 * self.zeta(r))

    def m(self, r):
        return 4.0 * self.psi(r) ** 6 / (3.0 * self.t_i ** 2)       # 680

    def ktilde(self, r):
        """[1 - (1 + r zeta')^2]/r^2 = -(x/r^2)(2 + x), x = r zeta', regular at r = 0 (695)."""
        u = (self.k * np.asarray(r, float)) ** 2 / 6.0
        x_over_r2 = -self.mu * self.k ** 2 / 3.0 * np.exp(-u)
        x = -2.0 * self.mu * u * np.exp(-u)
        return -x_over_r2 * (2.0 + x)

    def M(self, r):
        r = np.asarray(r, float)
        return self.m(r) * r ** 3 / 6.0                              # 586

    def compaction(self, r):
        """Nonlinear compaction (3/5) ktilde r^2 = (3/5)(1 - (1 + r zeta')^2): 2507.18312
        Main.tex:198-205 for dust with 1 - K r^2 = 1 - ktilde r^2 (the same invariant)."""
        r = np.asarray(r, float)
        return 0.6 * self.ktilde(r) * r * r

    def t_s(self, r):
        """Singularity (crunch) time of shell r, (pi/3) m ktilde^(-3/2) (743)."""
        return math.pi / 3.0 * self.m(r) * self.ktilde(r) ** -1.5

    def S(self, x):
        """S(x) of 600-619 for 0 < x < (pi/3)^(2/3) (both branches of the bound shell are
        covered by s in (0, 2 pi)); with s - sin s = 6 x^(3/2): S = (1 - cos s)/(6 x)."""
        x = np.asarray(x, float)
        s = solve_s(6.0 * x ** 1.5)
        return 2.0 * np.sin(0.5 * s) ** 2 / (6.0 * x)

    def R(self, t, r):
        """Areal radius r m^(1/3) t^(2/3) S(ktilde (t/m)^(2/3)) (593), bound shells."""
        t, r = np.broadcast_arrays(np.asarray(t, float), np.asarray(r, float))
        m = self.m(r)
        x = self.ktilde(r) * (t / m) ** (2.0 / 3.0)
        return r * m ** (1.0 / 3.0) * t ** (2.0 / 3.0) * self.S(x)

    def t_ah(self, r):
        """Time at which the sphere of shell r is marginally trapped, R = 2M on the
        collapsing branch: 1 - cos s = 2 ktilde r^2, t = M (s - sin s)/(ktilde r^2)^(3/2)."""
        r = np.asarray(r, float)
        kr2 = self.ktilde(r) * r * r
        s = 2.0 * math.pi - np.arccos(1.0 - 2.0 * kr2)
        return self.M(r) * _s_minus_sin(s) / kr2 ** 1.5

    def first_trapped(self, rmax_over_rm=3.0, n=4001):
        """Earliest marginally trapped sphere (minimum of t_ah over the shells)."""
        r = np.linspace(1e-4, rmax_over_rm, n) * self.r_m
        t = self.t_ah(r)
        j = int(np.argmin(t))
        lo, hi = r[max(j - 1, 0)], r[min(j + 1, n - 1)]
        from scipy.optimize import minimize_scalar
        res = minimize_scalar(lambda x: float(self.t_ah(x)), bounds=(lo, hi), method="bounded",
                              options=dict(xatol=1e-12 * self.r_m))
        rs = float(res.x)
        return dict(r=rs, r_over_rm=rs / self.r_m, t=float(self.t_ah(rs)),
                    t_over_tH=float(self.t_ah(rs)) / self.t_H, M=float(self.M(rs)),
                    M_over_M_rm=float(self.M(rs) / self.M(self.r_m)))

    def summary(self):
        fh = self.first_trapped()
        return dict(mu=self.mu, k=self.k, r_m=self.r_m, t_i=self.t_i, t_H=self.t_H,
                    C_max=float(self.compaction(self.r_m)),
                    t_s0_over_tH=float(self.t_s(0.0) / self.t_H),
                    t_s_rm_over_tH=float(self.t_s(self.r_m) / self.t_H),
                    first_trapped=fh, M_rm=float(self.M(self.r_m)))


def max_mu_on_slice(H_rm):
    """Largest mu whose central shell is still expanding on a slice where H r_m = H_rm:
    kappa(0) = 4 mu e^(-2 mu)/(H r_m)^2 < (3 pi/4)^(2/3) (ktilde(0) = 4 mu/r_m^2, Psi(0)^4 =
    e^(2 mu)); the centre binds for mu < 1/2 (kappa decreases outwards)."""
    from scipy.optimize import brentq
    rhs = KAPPA_TURN * H_rm ** 2 / 4.0
    if rhs >= 0.5 / math.e:               # max of mu e^(-2mu) is 1/(2e) at mu = 1/2
        return 0.5
    return brentq(lambda mu: mu * math.exp(-2 * mu) - rhs, 0.0, 0.5, xtol=1e-14)


# ------------------------------------------------------------------- C-infinity step (own)
def _step(u):
    u = np.asarray(u, dtype=float)
    uc = np.clip(u, 1e-300, 1 - 1e-16)
    with np.errstate(over="ignore"):
        S = 1.0 / (1.0 + np.exp(1.0 / uc - 1.0 / (1.0 - uc)))
    return np.where(u <= 0, 0.0, np.where(u >= 1, 1.0, S))


def _dstep(u):
    u = np.asarray(u, dtype=float)
    S = _step(u)
    uc = np.clip(u, 1e-3, 1 - 1e-3)
    d = S * (1 - S) * (1.0 / uc ** 2 + 1.0 / (1.0 - uc) ** 2)
    return np.where((u <= 0) | (u >= 1), 0.0, d)


# ------------------------------------------------------------------- expball profile
class LTBPeak2609:
    """Profile of `expball.model.Ball` for the LTB solution of 2609.14218 (module doc).

    mu    amplitude of MDPBH.tex:704
    Rm    comoving compaction radius r_m on the slice (isotropic, a = 1), code units
    H     Hubble rate of the background on the slice (expball's Ball.H)
    cut   (q_a, q_b): Delta tapered to 0 between q_a Rm and q_b Rm (areal radius)
    """
    name = "ltb2609"

    def __init__(self, mu, Rm, H, cut=(3.0, 4.0), ntab=6001):
        self.mu, self.Rm, self.H = float(mu), float(Rm), float(H)
        self.cut = (float(cut[0]), float(cut[1]))
        if not 0 < self.cut[0] < self.cut[1]:
            raise ValueError("need 0 < cut[0] < cut[1]")
        self.k = math.sqrt(6.0) / self.Rm
        self.t_i = 2.0 / (3.0 * self.H)
        self.P = Profile2609(self.mu, self.k, self.t_i)
        self.Ra, self.R2 = self.cut[0] * self.Rm, self.cut[1] * self.Rm
        self.breaks = (self.Ra,)
        k0 = float(self._kappa(np.array([0.0]))[0])
        if k0 >= KAPPA_TURN:
            raise ValueError(f"mu = {mu} with H r_m = {H * Rm:.4g}: the central shell is past "
                             f"turnaround on the slice (mu_max = {max_mu_on_slice(H * Rm):.4g})")
        # table r -> R for the starting values of the inversion
        r = np.linspace(0.0, 1.5 * self.R2, ntab)
        Rr = self.R_of_r(r)
        if np.any(np.diff(Rr) <= 0):
            raise ValueError("R(r) not increasing on the slice (shell crossing)")
        self._rt, self._Rt = r, Rr
        Rg = np.linspace(1e-6 * self.R2, self.R2, 4001)
        self.delta_min = float(np.min(self.Delta(Rg) + Rg * self.dDelta(Rg) / 3.0))

    # ---- shells labelled by the isotropic r
    def _kappa(self, r):
        return self.P.ktilde(r) / (self.H ** 2 * self.P.psi(r) ** 4)

    def y_of_r(self, r):
        """Root of y F(y)^(2/3) = kappa(r) in [0, 1) (bracketed Newton)."""
        # Newton in w = sqrt(1 - y) (as expball's y_of_Delta): F'(y) ~ (1-y)^(-1/2) makes the
        # y-derivative infinite at the turnaround, the w-derivative stays finite. G(w) =
        # y F(y)^(2/3) - kappa decreases with w; bracket [0, wmax].
        r0 = np.asarray(r, float)
        kap = np.atleast_1d(self._kappa(np.abs(r0))).ravel()
        if np.any(kap >= KAPPA_TURN):
            raise ValueError("a shell is past turnaround on the slice")
        y0 = np.clip(kap / (1.0 + 0.2 * kap), -50.0, 0.99)    # y F^(2/3) ~ y (1 + y/5)
        w = np.sqrt(1.0 - y0)
        lo = np.zeros_like(kap)
        hi = np.sqrt(1.0 - np.minimum(kap, 0.0) + 1.0) + 1.0
        act = np.arange(kap.size)
        for _ in range(100):
            if act.size == 0:
                break
            wa, ka = w[act], kap[act]
            ya = 1.0 - wa * wa
            F = 1.0 + Fm1(ya)
            g = ya * F ** (2.0 / 3.0) - ka
            lo[act] = np.where(g > 0, wa, lo[act])     # g > 0: y too large, w too small
            hi[act] = np.where(g < 0, wa, hi[act])
            with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
                dg = -2.0 * wa * (F ** (2.0 / 3.0)
                                  + ya * (2.0 / 3.0) * F ** (-1.0 / 3.0) * dF(ya))
                wn = wa - g / dg
            l, h = lo[act], hi[act]
            bad = (wn < l) | (wn > h) | ~np.isfinite(wn)     # strict: wn == l is converged
            wn = np.where(bad, 0.5 * (l + h), wn)
            done = ((np.abs(wn - wa) <= 4e-16 * np.maximum(wa, 1e-300))
                    | (np.abs(g) <= 2e-16 * np.maximum(np.abs(ka), 1e-300))
                    | (h - l <= 4e-16 * np.maximum(wa, 1e-300)))
            w[act] = wn
            act = act[~done]
        y = 1.0 - w * w
        # polish in y where 1 - w^2 loses relative precision (|y| small, F' ~ 0.3)
        sm = np.abs(y) < 0.5
        for _ in range(3):
            ys = y[sm]
            F = 1.0 + Fm1(ys)
            g = ys * F ** (2.0 / 3.0) - kap[sm]
            y[sm] = ys - g / (F ** (2.0 / 3.0) + ys * (2.0 / 3.0) * F ** (-1.0 / 3.0) * dF(ys))
        return y.reshape(r0.shape) if r0.ndim else y

    def Delta_of_r(self, r):
        f = Fm1(self.y_of_r(r))
        return f * (2.0 + f)                                     # F^2 - 1 without cancellation

    def R_of_r(self, r):
        r = np.asarray(r, float)
        rhat = np.abs(r) * self.P.psi(r) ** 2
        return np.sign(r) * rhat * (1.0 + self.Delta_of_r(r)) ** (-1.0 / 3.0)

    def r_of_R(self, R):
        R = np.atleast_1d(np.asarray(R, float))
        r = np.interp(R, self._Rt, self._rt)
        h = 1e-6 * self.Rm
        for _ in range(40):
            f = self.R_of_r(r) - R
            d = (self.R_of_r(r + h) - self.R_of_r(r - h)) / (2 * h)
            rn = r - f / d
            # quadratic convergence: a step below 1e-13 leaves an error far below round-off
            done = np.abs(rn - r) <= 1e-13 * np.maximum(np.abs(r), self.Rm * 1e-12)
            r = rn
            if np.all(done):
                break
        return r

    def _dDelta_dR_exact(self, R):
        """dDelta/dR = (dDelta/dr)/(dR/dr), five-point differences in r (Delta even, R odd)."""
        r = self.r_of_R(R)
        h = 2e-4 * self.Rm
        st = np.array([-2, -1, 1, 2]) * h
        w = np.array([1, -8, 8, -1]) / (12 * h)
        dD = sum(wi * self.Delta_of_r(r + si) for wi, si in zip(w, st))
        dR = sum(wi * self.R_of_r(r + si) for wi, si in zip(w, st))
        return dD / dR

    # ---- expball protocol
    def Delta_exact(self, R):
        return self.Delta_of_r(self.r_of_R(R))

    def Delta(self, R):
        R = np.asarray(R, float)
        u = (R - self.Ra) / (self.R2 - self.Ra)
        out = self.Delta_exact(np.minimum(R, self.R2)) * (1.0 - _step(u))
        return np.where(R >= self.R2, 0.0, out).reshape(R.shape)

    def dDelta(self, R):
        R = np.asarray(R, float)
        Rc = np.minimum(R, self.R2)
        u = (R - self.Ra) / (self.R2 - self.Ra)
        out = (self._dDelta_dR_exact(Rc) * (1.0 - _step(u))
               - self.Delta_exact(Rc) * _dstep(u) / (self.R2 - self.Ra))
        return np.where(R >= self.R2, 0.0, out).reshape(R.shape)

    def summary(self):
        return dict(profile="ltb2609", mu=self.mu, Rm=self.Rm, H=self.H, H_Rm=self.H * self.Rm,
                    a_slice_over_a_H=(self.H * self.Rm) ** -2, cut=self.cut,
                    local_delta_min=self.delta_min,
                    threshold=dict(mu_globally_naked=MU_GLOBALLY_NAKED,
                                   mu_locally_naked=MU_LOCALLY_NAKED,
                                   locator=THRESHOLD_LOCATOR))


def make_ball(mu, q=4.5, HRb=0.9, cut=(3.0, 4.0), edge_width=0.0, M=1.0):
    """expball Ball (sharp-edge mass M, H R_b = HRb) holding the profile with r_m = R_b/q."""
    from expball.model import Ball
    Rb = 2.0 * M / HRb ** 2
    H = HRb / Rb
    prof = LTBPeak2609(mu, Rb / q, H, cut=cut)
    return Ball(H, Rb, prof, edge_width=edge_width), prof
