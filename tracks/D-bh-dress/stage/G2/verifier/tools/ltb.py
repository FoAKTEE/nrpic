"""Exact reference of the G2 growth criterion (verifier's own): dust shells with LTB energy
E = -M/R0 falling into a Schwarzschild hole of mass M (units M = 1).

(dR/dtau)^2 = 2 m / R - 2 M / R0, m = m(R0) Misner-Sharp mass inside the shell.
Cycloid: R = A (1 - cos eta), tau = T (eta - sin eta) + c, A = m R0 / (2 M),
T = A^(3/2) / m^(1/2). Start at R0 on the expanding branch (1 - cos eta0 = 2M/m), cross
R = 2m on the collapsing branch (1 - cos etaH = 4M/R0).
"""
import numpy as np

MBH = 1.0


def tau_horizon(R0, m, M=MBH):
    R0 = np.asarray(R0, float)
    m = np.asarray(m, float)
    A = m * R0 / (2.0 * M)
    T = A ** 1.5 / np.sqrt(m)
    eta0 = np.arccos(np.clip(1.0 - 2.0 * M / m, -1.0, 1.0))
    etaH = 2.0 * np.pi - np.arccos(np.clip(1.0 - 4.0 * M / R0, -1.0, 1.0))
    return T * ((etaH - np.sin(etaH)) - (eta0 - np.sin(eta0)))


def radius_at_tau(tau, R0, m, M=MBH):
    """Areal radius of the shell at its proper time tau (from the start), by inverting
    the cycloid with Newton iterations on eta."""
    A = m * R0 / (2.0 * M)
    T = A ** 1.5 / np.sqrt(m)
    eta0 = np.arccos(np.clip(1.0 - 2.0 * M / m, -1.0, 1.0))
    target = np.asarray(tau, float) / T + (eta0 - np.sin(eta0))
    eta = np.full_like(target, np.pi)
    for _ in range(100):
        f = eta - np.sin(eta) - target
        eta = eta - f / np.maximum(1.0 - np.cos(eta), 1e-14)
        eta = np.clip(eta, 1e-12, 2.0 * np.pi)
    return A * (1.0 - np.cos(eta))


def areal_radius(rbar, M=MBH):
    """Isotropic coordinate radius of the time-symmetric Schwarzschild slice -> areal."""
    return rbar * (1.0 + M / (2.0 * rbar)) ** 2


def lattice_reference(x, m_rest, ntrac=140, M=MBH):
    """From the particle file: per particle R0, E_K = (1 - 2M/R0)^(1/2), m(R0) (M plus the
    cumulative lattice sum of m E_K over particles with R0' <= R0, tracers excluded),
    tau_H. Returns dict of arrays indexed like the file, and the growth curve (tau_H
    sorted, m) of the dust."""
    rbar = np.sqrt(np.sum(x ** 2, axis=1))
    R0 = areal_radius(rbar, M)
    EK = np.sqrt(1.0 - 2.0 * M / R0)
    dm = m_rest * EK
    dust = np.arange(len(R0)) >= ntrac
    order = np.argsort(R0[dust], kind="stable")
    Rd = R0[dust][order]
    cum = np.cumsum(dm[dust][order])
    # inclusive: equal R0 share the value of the last of them
    last = np.searchsorted(Rd, Rd, side="right") - 1
    mdisc_sorted = M + cum[last]
    mdisc = np.empty(len(R0))
    mdisc_d = np.empty(dust.sum())
    mdisc_d[order] = mdisc_sorted
    mdisc[dust] = mdisc_d
    # tracers: the dust mass inside their radius
    if ntrac:
        it = np.searchsorted(Rd, R0[~dust], side="right") - 1
        mdisc[~dust] = M + np.where(it >= 0, cum[np.maximum(it, 0)], 0.0)
    tauH = tau_horizon(R0, mdisc, M)
    tH_d = tauH[dust][order]
    curve = (tH_d, mdisc_sorted)
    return dict(R0=R0, EK=EK, mdisc=mdisc, tauH=tauH, dust=dust), curve


def lattice_mid(R0, dm, dust):
    """Mass inside each dust particle with half weight for the particles on its own
    radius (a discrete shell feels half of itself)."""
    Rd = R0[dust]
    order = np.argsort(Rd, kind="stable")
    Rs = Rd[order]
    cs = np.concatenate([[0.0], np.cumsum(dm[dust][order])])
    lo = np.searchsorted(Rs, Rs, side="left")
    hi = np.searchsorted(Rs, Rs, side="right")
    mid = MBH + cs[lo] + 0.5 * (cs[hi] - cs[lo])
    out = np.full(len(R0), np.nan)
    tmp = np.empty(len(Rd))
    tmp[order] = mid
    out[dust] = tmp
    return out


def table_mass(tab_path, M=MBH):
    """Continuum m(R) from a format-2 table of the ES-F slice: K_T^2 = 2 D / R^3."""
    a = np.loadtxt(tab_path, comments="#")
    rbar, KT = a[:, 0], a[:, 3]
    ok = rbar > 0
    rbar, KT = rbar[ok], KT[ok]
    R = areal_radius(rbar, M)
    return R, M + 0.5 * R ** 3 * KT ** 2


def growth_from_curve(curve, tau):
    """M_LTB(tau): the largest m among shells with tau_H <= tau (monotonic tau_H:
    interpolation on the lattice curve)."""
    tH, m = curve
    return np.interp(tau, tH, m, left=MBH)
