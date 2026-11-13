"""Homogeneous prolate spheroid of the cold-collapse test (Wu & Most, Sec. IV C;
construction of Yoo et al. 2017, Shapiro & Teukolsky 1991).

Semi-axes a (equatorial, x and y) < b (polar, z), a = b sqrt(1 - e^2), focal
half-distance c = sqrt(b^2 - a^2) = e b. Auxiliary uniform density
rho_N = 3M/(8 pi a^2 b) inside, so the Newtonian source mass is M/2. Its
potential (G = 1, nabla^2 Phi_N = 4 pi rho_N) is the classical ellipsoid result

    Phi_N = -pi rho_N a^2 b [ I(lam) - (x^2 + y^2) J_a(lam) - z^2 J_b(lam) ],

with lam = 0 inside and, outside, lam the positive root of
(x^2 + y^2)/(a^2 + lam) + z^2/(b^2 + lam) = 1. For a prolate spheroid, with
w = sqrt(b^2 + lam) and t = atanh(c/w),

    I   = (2/c) t,
    J_a = w / (c^2 (w^2 - c^2)) - t / c^3,
    J_b = 2 t / c^3 - 2 / (c^2 w)

(series in (c/w)^2 are used for c/w < 0.3 to avoid cancellation). The
conformal factor is psibar = 1 - Phi_N -> 1 + M/(2r), so the ADM mass is M; the
energy density is rho_ADM = 2 rho_N psibar^(-5) and, with the particles at rest,
the coordinate rest-mass density is rho_ADM psibar^6 = 2 rho_N psibar.
Inside, psibar = c0 - cR (x^2 + y^2) - cz z^2 is quadratic, so the rest mass and
the cumulative distribution in the spheroidal radius
s^2 = (x^2 + y^2)/a^2 + z^2/b^2 are closed-form:

    M_rest(<s) = 2 rho_N V [c0 s^3 - (cR 2a^2/5 + cz b^2/5) s^5],  V = 4 pi a^2 b / 3.
"""

import math

import numpy as np

__all__ = ["ProlateSpheroid"]


def _series_terms(e2, kind, nterms=40):
    k = np.arange(nterms)
    if kind == "I":      # atanh(e)/e = sum e^{2k}/(2k+1)
        coef = 1.0 / (2 * k + 1)
    elif kind == "Ja":   # sum_{k>=1} e^{2k-2} 2k/(2k+1)
        kk = k + 1
        coef = 2.0 * kk / (2 * kk + 1)
    else:                # Jb: sum_{k>=1} e^{2k-2}/(2k+1)
        kk = k + 1
        coef = 1.0 / (2 * kk + 1)
    e2 = np.asarray(e2, float)
    out = np.zeros_like(e2)
    for cf in coef[::-1]:
        out = out * e2 + cf
    return out


def _IJ(w, c):
    """I, J_a, J_b at w = sqrt(b^2 + lam) for focal distance c (vectorised)."""
    w = np.asarray(w, dtype=float)
    eps = c / w
    small = eps < 0.3
    e2 = np.where(small, eps * eps, 0.0)
    I_s = (2.0 / w) * _series_terms(e2, "I")
    Ja_s = _series_terms(e2, "Ja") / w ** 3
    Jb_s = 2.0 * _series_terms(e2, "Jb") / w ** 3
    epsb = np.where(small, 0.5, eps)
    wb = np.where(small, 2.0 * c, w)
    t = np.arctanh(epsb)
    I_c = 2.0 * t / c
    Ja_c = wb / (c * c * (wb * wb - c * c)) - t / c ** 3
    Jb_c = 2.0 * t / c ** 3 - 2.0 / (c * c * wb)
    return (np.where(small, I_s, I_c), np.where(small, Ja_s, Ja_c),
            np.where(small, Jb_s, Jb_c))


class ProlateSpheroid:
    """Uniform prolate spheroid initial data; lengths in units of M."""

    def __init__(self, e=0.9, b=10.0, M=1.0):
        if not 0.0 < e < 1.0:
            raise ValueError("eccentricity must lie in (0, 1)")
        self.e = float(e)
        self.b = float(b)
        self.M = float(M)
        self.a = b * math.sqrt(1.0 - e * e)
        self.c = e * b
        self.rhoN = 3.0 * M / (8.0 * math.pi * self.a ** 2 * self.b)
        self.V = 4.0 * math.pi * self.a ** 2 * self.b / 3.0
        I0, Ja0, Jb0 = (float(v[0]) for v in _IJ(np.array([self.b]), self.c))
        self.I0, self.Ja0, self.Jb0 = I0, Ja0, Jb0
        k = math.pi * self.rhoN * self.a ** 2 * self.b
        self.c0 = 1.0 + k * I0           # psibar = c0 - cR R^2 - cz z^2 inside
        self.cR = k * Ja0
        self.cz = k * Jb0

    # -- geometry -------------------------------------------------------------
    def s2(self, x, y, z):
        """Squared spheroidal radius (x^2 + y^2)/a^2 + z^2/b^2."""
        return (np.asarray(x) ** 2 + np.asarray(y) ** 2) / self.a ** 2 + np.asarray(z) ** 2 / self.b ** 2

    def inside(self, x, y, z):
        return self.s2(x, y, z) <= 1.0

    def lam(self, x, y, z):
        """Ellipsoidal coordinate lambda (0 inside)."""
        R2 = np.asarray(x, float) ** 2 + np.asarray(y, float) ** 2
        z2 = np.asarray(z, float) ** 2
        a2, b2 = self.a ** 2, self.b ** 2
        B = a2 + b2 - R2 - z2
        C = a2 * b2 - b2 * R2 - a2 * z2          # < 0 outside
        disc = np.sqrt(np.maximum(B * B - 4.0 * C, 0.0))
        with np.errstate(divide="ignore", invalid="ignore"):
            lam = np.where(B > 0, -2.0 * C / (B + disc), 0.5 * (disc - B))
        return np.where(C < 0, np.maximum(lam, 0.0), 0.0)

    # -- fields ---------------------------------------------------------------
    def phiN(self, x, y, z):
        """Newtonian potential of the uniform spheroid, nabla^2 Phi = 4 pi rho_N."""
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        z = np.asarray(z, float)
        lam = self.lam(x, y, z)
        I, Ja, Jb = _IJ(np.sqrt(self.b ** 2 + lam), self.c)
        return -math.pi * self.rhoN * self.a ** 2 * self.b * (I - (x * x + y * y) * Ja - z * z * Jb)

    def psibar(self, x, y, z):
        """Conformal factor psibar = 1 - Phi_N."""
        return 1.0 - self.phiN(x, y, z)

    def rho_adm(self, x, y, z):
        """Energy density 2 rho_N psibar^-5 inside, 0 outside."""
        return np.where(self.inside(x, y, z), 2.0 * self.rhoN * self.psibar(x, y, z) ** -5, 0.0)

    def coordinate_density(self, x, y, z):
        """Rest mass per coordinate volume, 2 rho_N psibar inside."""
        return np.where(self.inside(x, y, z), 2.0 * self.rhoN * self.psibar(x, y, z), 0.0)

    # -- integrals ------------------------------------------------------------
    def rest_mass_inside_s(self, s):
        """Rest mass inside spheroidal radius s (closed form)."""
        s = np.clip(np.asarray(s, float), 0.0, 1.0)
        q = self.cR * 2.0 * self.a ** 2 / 5.0 + self.cz * self.b ** 2 / 5.0
        return 2.0 * self.rhoN * self.V * (self.c0 * s ** 3 - q * s ** 5)

    def rest_mass(self):
        """Continuum rest mass int 2 rho_N psibar d^3x over the spheroid."""
        return float(self.rest_mass_inside_s(1.0))

    def F_s(self, s):
        """Cumulative rest-mass fraction in the spheroidal radius s."""
        return self.rest_mass_inside_s(s) / self.rest_mass()

    def F_z(self, zeta):
        """Cumulative rest-mass fraction in zeta = z/b in [-1, 1] (closed form):
        dM/dzeta = 2 rho_N b pi a^2 [ (c0 - cz b^2 zeta^2) w - cR a^2 w^2/2 ],
        w = 1 - zeta^2."""
        zt = np.clip(np.asarray(zeta, float), -1.0, 1.0)
        a2, b2 = self.a ** 2, self.b ** 2
        # integrate the polynomial in zeta from -1 to zt
        c0, cR, cz = self.c0, self.cR, self.cz
        # p(zeta) = c0 (1 - zeta^2) - cz b^2 zeta^2 (1 - zeta^2) - cR a^2 (1 - zeta^2)^2 / 2
        coeff = np.array([  # coefficients of zeta^0, zeta^2, zeta^4
            c0 - cR * a2 / 2.0,
            -c0 - cz * b2 + cR * a2,
            cz * b2 - cR * a2 / 2.0])
        P = lambda t: coeff[0] * t + coeff[1] * t ** 3 / 3.0 + coeff[2] * t ** 5 / 5.0
        tot = P(1.0) - P(-1.0)
        return (P(zt) - P(-1.0)) / tot

    def summary(self):
        return dict(model="prolate_spheroid", M_ADM=self.M, e=self.e,
                    a=self.a, b=self.b, c_focal=self.c, rhoN=self.rhoN,
                    M_rest=self.rest_mass(), psibar_c=self.c0,
                    psibar_coeffs_inside=dict(c0=self.c0, cR=self.cR, cz=self.cz),
                    I0=self.I0, Ja0=self.Ja0, Jb0=self.Jb0,
                    note=("psibar = 1 - Phi_N; inside psibar = c0 - cR (x^2+y^2) - cz z^2; "
                          "rho_ADM = 2 rho_N psibar^-5; u_i = 0; lapse 1"))
