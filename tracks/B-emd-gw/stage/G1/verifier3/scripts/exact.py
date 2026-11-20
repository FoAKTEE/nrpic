"""Exact linear solutions of tests F and X (verifier3, my own derivation; JOURNAL entry 1).

Conventions (numpy, used by every script of this package):
- polarization basis of a direction n: u = theta-hat, v = phi-hat (theta from +z, azimuth
  from +x), e+ = uu - vv, ex = uv + vu; h_+ = (1/2) e+:h, h_x = (1/2) ex:h (e:e = 2);
- a mode coefficient c of a real field f is defined by f = c exp(i K.x) + c.c. + ...
  (absolute coordinates; see diag.mode_coeff).

Test F (flat, z4c_linear_wave): h = A_+ e+ sin(K.x - w t) + A_x ex sin(K.x - w t + phi_x),
w = |K|; complex amplitude 2 i c_+ = A_+ exp(-i w t), 2 i c_x = A_x exp(i (phi_x - w t)).
Test X (EdS, conformal time t, a = (1 + t/2)^2): h_+ = eps_+ T(t) cos(K.x),
h_x = eps_x T(t) cos(K.x + phi_x); 2 c_+ = eps_+ T, 2 c_x = eps_x T exp(i phi_x).
"""
import numpy as np
from scipy.special import spherical_jn, spherical_yn


def sph_basis(n):
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    th = np.arccos(np.clip(n[2], -1.0, 1.0))
    ph = np.arctan2(n[1], n[0])
    u = np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    v = np.array([-np.sin(ph), np.cos(ph), 0.0])
    return n, u, v


def pol_tensors(n):
    n, u, v = sph_basis(n)
    ep = np.outer(u, u) - np.outer(v, v)
    ex = np.outer(u, v) + np.outer(v, u)
    return ep, ex, n, u, v


def generator_tensors(kx1, kx2, kx3):
    """(axx..azz), (bxx..bzz) of z4c_linear_wave.cpp (core/requests-b), as 3x3 arrays."""
    theta = np.arctan2(np.sqrt(kx2 * kx2 + kx1 * kx1), kx3)
    phi = np.arctan2(kx1, kx2)
    c, s = np.cos, np.sin
    axx = -c(theta) ** 2 * c(2 * phi) - c(phi) ** 2 * s(theta) ** 2
    axy = 0.25 * (3 + c(2 * theta)) * s(2 * phi)
    axz = -c(theta) * s(theta) * s(phi)
    ayy = c(theta) ** 2 * c(2 * phi) - s(theta) ** 2 * s(phi) ** 2
    ayz = -c(theta) * s(theta) * c(phi)
    azz = s(theta) ** 2
    bxx = -c(theta) * s(2 * phi)
    bxy = -c(theta) * c(2 * phi)
    bxz = s(theta) * c(phi)
    byy = c(theta) * s(2 * phi)
    byz = -s(theta) * s(phi)
    bzz = 0.0
    A = np.array([[axx, axy, axz], [axy, ayy, ayz], [axz, ayz, azz]])
    B = np.array([[bxx, bxy, bxz], [bxy, byy, byz], [bxz, byz, bzz]])
    return A, B


# ---------------------------------------------------------------- test F
class FlatWave:
    def __init__(self, k_cycles=(1.0, 1.0, 1.0), amp=1e-6, amp_x=5e-7, phi_x=1.0):
        self.kc = np.asarray(k_cycles, float)
        self.K = 2 * np.pi * self.kc
        self.w = np.linalg.norm(self.K)
        self.amp, self.amp_x, self.phi_x = amp, amp_x, phi_x
        self.ep, self.ex, self.n, self.u, self.v = pol_tensors(self.K)

    def complex_amp(self, t):
        """(2 i c_+, 2 i c_x) of h at time t."""
        return (self.amp * np.exp(-1j * self.w * t),
                self.amp_x * np.exp(1j * (self.phi_x - self.w * t)))

    def fields(self, X, t):
        """h_ij and d_t h_ij on coordinate arrays X = (x, y, z)."""
        P = self.K[0] * X[0] + self.K[1] * X[1] + self.K[2] * X[2] - self.w * t
        h = (self.amp * self.ep[:, :, None, None, None] * np.sin(P)
             + self.amp_x * self.ex[:, :, None, None, None] * np.sin(P + self.phi_x))
        hd = -self.w * (self.amp * self.ep[:, :, None, None, None] * np.cos(P)
                        + self.amp_x * self.ex[:, :, None, None, None] * np.cos(P + self.phi_x))
        return h, hd


# ---------------------------------------------------------------- test X
def eds_a(t):
    return (1.0 + 0.5 * np.asarray(t)) ** 2


def eds_calH(t):
    """a'/a in conformal time."""
    return 2.0 / (2.0 + np.asarray(t))


class EdSMode:
    """T(t): T'' + (4/(t+2)) T' + kn^2 T = 0, T(0) = 0, T'(0) = 1."""

    def __init__(self, kn):
        self.kn = kn
        tau0 = 2.0
        x0 = kn * tau0
        M = np.array([[self._f(1, x0), self._f(2, x0)],
                      [kn * self._df(1, x0), kn * self._df(2, x0)]])
        self.c = np.linalg.solve(M, np.array([0.0, 1.0]))

    @staticmethod
    def _f(which, x):
        return (spherical_jn(1, x) if which == 1 else spherical_yn(1, x)) / x

    @staticmethod
    def _df(which, x):
        if which == 1:
            f, df = spherical_jn(1, x), spherical_jn(1, x, derivative=True)
        else:
            f, df = spherical_yn(1, x), spherical_yn(1, x, derivative=True)
        return (df * x - f) / x ** 2

    def T(self, t):
        x = self.kn * (np.asarray(t, float) + 2.0)
        return self.c[0] * self._f(1, x) + self.c[1] * self._f(2, x)

    def dT(self, t):
        x = self.kn * (np.asarray(t, float) + 2.0)
        return self.kn * (self.c[0] * self._df(1, x) + self.c[1] * self._df(2, x))

    def d2T(self, t):
        t = np.asarray(t, float)
        return -(4.0 / (t + 2.0)) * self.dT(t) - self.kn ** 2 * self.T(t)


class ExpandingWave:
    def __init__(self, L=4.0, m=(1, 1, 0), eps_p=2e-6, eps_x=1e-6, phi_x=1.0):
        self.L = L
        self.K = 2 * np.pi / L * np.asarray(m, float)
        self.kn = np.linalg.norm(self.K)
        self.eps_p, self.eps_x, self.phi_x = eps_p, eps_x, phi_x
        self.ep, self.ex, self.n, self.u, self.v = pol_tensors(self.K)
        self.mode = EdSMode(self.kn)

    def coeff(self, t):
        """(2 c_+, 2 c_x) of h, and of h' (conformal-time derivative)."""
        T, dT = self.mode.T(t), self.mode.dT(t)
        ph = np.exp(1j * self.phi_x)
        return (self.eps_p * T, self.eps_x * T * ph), (self.eps_p * dT, self.eps_x * dT * ph)

    def fields(self, X, t):
        """gamma_ij, K_ij, alpha on coordinate arrays X (exact to first order in eps)."""
        ph = self.K[0] * X[0] + self.K[1] * X[1] + self.K[2] * X[2]
        T, dT = self.mode.T(t), self.mode.dT(t)
        shape = (3, 3) + np.shape(X[0])
        base = (self.eps_p * self.ep[:, :, None, None, None] * np.cos(ph)
                + self.eps_x * self.ex[:, :, None, None, None] * np.cos(ph + self.phi_x))
        h, hd = T * base, dT * base
        a = eds_a(t)
        ad = 1.0 + 0.5 * t          # da/dt = (1 + t/2)
        d = np.zeros(shape)
        for i in range(3):
            d[i, i] = 1.0
        gam = a ** 2 * (d + h)
        # K_ij = -(1/2 alpha) d_t gamma_ij, alpha = a
        Kij = -(1.0 / (2 * a)) * (2 * a * ad * (d + h) + a ** 2 * hd)
        return gam, Kij, a
