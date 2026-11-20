#!/usr/bin/env python3
"""Radiated energy and linear momentum from the r psi4 modes of AthenaK (package junk_gauge of
F-hills). Reference solutions and analysis only; nothing here evolves anything.

Formulas [BACKGROUND, Ruiz, Alcubierre, Nunez, Takahashi, arXiv:0707.4654, gwaves.tex lines
585-603 (energy and momentum as sphere integrals), 634-657 (momentum as mode couplings)]:
    N(t, theta, phi) = int r psi4 dt = sum_lm N_lm(t) -2Y_lm(theta, phi)   (the news)
    dE/dt   = (1/16 pi) oint |N|^2 dOmega = (1/16 pi) sum_lm |N_lm|^2
    dP_i/dt = (1/16 pi) oint l_i |N|^2 dOmega,  l = (sin th cos ph, sin th sin ph, cos th)
Spin-weighted harmonics: a port of AthenaK's own swsh (athenak/src/z4c/z4c_wave_extr.cpp lines
45-59, Wigner-d form), so the momentum quadrature needs no assumption about conventions.
Time integration:
    ffi()      fixed-frequency integration [BACKGROUND, Reisswig and Pollney arXiv:1006.1632,
               paper.tex lines 914-928]: N~ = psi4~ / (i w_eff), w_eff = sign(w) max(|w|, w0),
               after a cosine taper of the ends (numpy's FFT convention: d/dt <-> i w)
    td_quad()  time domain: a quadratic in t fitted to each mode outside a window is
               subtracted, then the news is integrated from a start time (as nrread.py)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "F-hills", "nr_first", "scripts"))
import nrread as nr  # noqa: E402


# ----------------------------------------------------------------------------------------
# spin-weighted harmonics (s = -2), port of AthenaK's swsh
# ----------------------------------------------------------------------------------------
def swsh(l, m, theta, phi):
    """-2Y_lm(theta, phi) as in athenak/src/z4c/z4c_wave_extr.cpp lines 47-59."""
    f = math.factorial
    th = np.asarray(theta, dtype=float)
    d = np.zeros_like(th)
    k1 = max(m - 2, 0)
    k2 = min(l + m, l - 2)
    for k in range(k1, k2 + 1):
        d = d + ((-1) ** k * math.sqrt(f(l + m) * f(l - m) * f(l + 2) * f(l - 2))
                 * np.cos(th / 2) ** (2 * l + m - 2 - 2 * k) * np.sin(th / 2) ** (2 * k + 2 - m)
                 / (f(l + m - k) * f(l - 2 - k) * f(k) * f(k + 2 - m)))
    return math.sqrt((2 * l + 1) / (4 * math.pi)) * d * np.exp(1j * m * np.asarray(phi))


def sphere_grid(nth=40, nph=80):
    """Gauss-Legendre in cos(theta) times uniform phi: nodes and weights (sum 4 pi)."""
    x, w = np.polynomial.legendre.leggauss(nth)
    th = np.arccos(x)
    ph = (np.arange(nph) + 0.5) * 2 * np.pi / nph
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    W = np.outer(w, np.full(nph, 2 * np.pi / nph))
    return TH.ravel(), PH.ravel(), W.ravel()


class Sphere:
    """Harmonics on a quadrature grid, for rebuilding N(theta, phi) from its modes."""

    def __init__(self, lmax=8, nth=40, nph=80):
        self.th, self.ph, self.w = sphere_grid(nth, nph)
        self.n = np.stack([np.sin(self.th) * np.cos(self.ph), np.sin(self.th) * np.sin(self.ph),
                           np.cos(self.th)], axis=0)
        self.keys = [(l, m) for l in range(2, lmax + 1) for m in range(-l, l + 1)]
        self.Y = np.stack([swsh(l, m, self.th, self.ph) for l, m in self.keys], axis=0)

    def orthonormality_error(self):
        G = (self.Y * self.w) @ self.Y.conj().T
        return float(np.max(np.abs(G - np.eye(len(self.keys)))))

    def flux(self, Nmodes):
        """Nmodes: dict (l, m) -> complex array (nt,). Returns dE/dt (nt,) and dP/dt (3, nt)
        from the sphere quadrature."""
        Z = np.stack([Nmodes.get(k, np.zeros_like(next(iter(Nmodes.values()))))
                      for k in self.keys], axis=0)                     # (nk, nt)
        F = self.Y.T @ Z                                               # (npts, nt)
        I = np.abs(F) ** 2 * self.w[:, None] / (16 * np.pi)
        return I.sum(axis=0), self.n @ I


# ----------------------------------------------------------------------------------------
# momentum from the closed coupling formula of Ruiz et al. (check of the harmonics' convention)
# ----------------------------------------------------------------------------------------
def _a(l, m):
    return math.sqrt((l - m) * (l + m + 1)) / (l * (l + 1))


def _b(l, m):
    v = (l - 2) * (l + 2) * (l + m) * (l + m - 1) / ((2 * l - 1) * (2 * l + 1))
    return math.sqrt(v) / (2 * l) if v > 0 else 0.0


def _c(l, m):
    return 2 * m / (l * (l + 1))


def _d(l, m):
    v = (l - 2) * (l + 2) * (l - m) * (l + m) / ((2 * l - 1) * (2 * l + 1))
    return math.sqrt(v) / l if v > 0 else 0.0


def momentum_coupling(Nmodes):
    """dP_x/dt, dP_y/dt, dP_z/dt from gwaves.tex lines 634-657 (A^{lm} -> N_lm)."""
    def g(l, m):
        if l < 2 or abs(m) > l or (l, m) not in Nmodes:
            return 0.0
        return Nmodes[(l, m)]
    nt = len(next(iter(Nmodes.values())))
    Pp = np.zeros(nt, dtype=complex)
    Pz = np.zeros(nt, dtype=complex)
    for (l, m), N in Nmodes.items():
        Pp += N * (_a(l, m) * np.conj(g(l, m + 1)) + _b(l, -m) * np.conj(g(l - 1, m + 1))
                   - _b(l + 1, m + 1) * np.conj(g(l + 1, m + 1)))
        Pz += N * (_c(l, m) * np.conj(g(l, m)) + _d(l, m) * np.conj(g(l - 1, m))
                   + _d(l + 1, m) * np.conj(g(l + 1, m)))
    Pp /= 8 * np.pi
    Pz /= 16 * np.pi
    return np.stack([Pp.real, Pp.imag, Pz.real])


# ----------------------------------------------------------------------------------------
# time integration
# ----------------------------------------------------------------------------------------
def taper(t, width):
    """Cosine ramps of the given width at both ends (1 in between)."""
    w = np.ones_like(t)
    if width <= 0:
        return w
    a = (t - t[0]) / width
    b = (t[-1] - t) / width
    w = np.where(a < 1, 0.5 - 0.5 * np.cos(np.pi * np.clip(a, 0, 1)), w)
    w = np.where(b < 1, w * (0.5 - 0.5 * np.cos(np.pi * np.clip(b, 0, 1))), w)
    return w


def ffi(t, z, omega0, taper_width=4.0, pad=2):
    """News N = int z dt by fixed-frequency integration. t uniform. The tapered record is
    zero-padded to pad times its length so that the periodic wrap does not touch it."""
    dt = float(np.median(np.diff(t)))
    n = len(t)
    zz = np.zeros(pad * n, dtype=complex)
    zz[:n] = z * taper(t, taper_width)
    Z = np.fft.fft(zz)
    w = 2 * np.pi * np.fft.fftfreq(pad * n, dt)
    weff = np.where(np.abs(w) < omega0, omega0 * np.where(w < 0, -1.0, 1.0), w)
    return np.fft.ifft(Z / (1j * weff))[:n]


def td_quad(t, z, win, start):
    """News by time-domain integration: subtract a quadratic fitted to z outside win = (t0, t1),
    integrate (trapezoid) from t = start (N = 0 before)."""
    out = (t < win[0]) | (t > win[1])
    cr = np.polyfit(t[out], z.real[out], 2)
    ci = np.polyfit(t[out], z.imag[out], 2)
    zz = (z.real - np.polyval(cr, t)) + 1j * (z.imag - np.polyval(ci, t))
    zz = np.where(t >= start, zz, 0.0)
    N = np.zeros_like(zz)
    N[1:] = np.cumsum(0.5 * (zz[1:] + zz[:-1]) * np.diff(t))
    return N


def cumulative(t, rate):
    E = np.zeros_like(t)
    E[1:] = np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(t))
    return E


def window_integral(t, rate, a, b):
    """int_a^b rate dt on the samples (linear interpolation at the ends)."""
    E = cumulative(t, rate)
    return float(np.interp(b, t, E) - np.interp(a, t, E))


# ----------------------------------------------------------------------------------------
# geometry
# ----------------------------------------------------------------------------------------
def tortoise(R, M):
    """R* of the areal radius of a coordinate sphere R of puncture coordinates (isotropic far
    away: R_a = R (1 + M / 2R)^2) [JUDGEMENT]."""
    Ra = R * (1 + M / (2 * R)) ** 2
    return Ra + 2 * M * math.log(Ra / (2 * M) - 1)


def load_modes(rundir, R):
    """r psi4 modes of the sphere R: (t, {(l, m): complex}); restarts handled by nrread."""
    t, modes = nr.read_rpsi4(rundir, R)
    return t, modes
