#!/usr/bin/env python3
"""Numbers predicted before the tests of work package clump run (tracks/core/
JOURNAL-clump.md, "Predictions"). No simulation: quadratures of the closed forms of
python/nrpic/smeared_bowen_york.py and a one-dimensional emulation of the deposit
(linear cloud, binomial passes, compensation) of lattice particles.

Norms as the code's history writes them (outputs/history.cpp):
    M-norm2 = int gamma^ij M_i M_j sqrt(gamma) d^3x = int psi^2 (M_x^2+M_y^2+M_z^2) d^3x,
    Mx-norm2 = int M_x^2 psi^6 d^3x,   H-norm2 = int H^2 psi^6 d^3x,
with M_i = D_j K^j_i - 8 pi S_i (covariant). Without curvature M_i = -8 pi psi^-6 Stilde_i.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import clumps as clm  # noqa: E402
from nrpic import smeared_bowen_york as sby  # noqa: E402

out = {}


def grid(half, n):
    c = (np.arange(n) + 0.5) * (2.0 * half / n) - half
    X = np.stack(np.meshgrid(c, c, c, indexing="ij"), axis=-1)
    return X, (2.0 * half / n) ** 3


# ---------------------------------------------------------------- single clump (T1-T4)
M, SIG = 0.2, 1.0
G = clm.GaussianClumps([dict(mass=M, sigma=SIG)])
X, dV = grid(8.0, 160)
psi = G.psi(X)
r = np.sqrt(np.sum(X * X, axis=-1))
g = sby.gaussian(r, SIG)
t1 = {}
for P in (0.02, 0.04, 0.06):
    St = sby.momentum_density(X, (0, 0, 0), SIG, (P, 0, 0))
    m2 = (8 * math.pi) ** 2 * np.sum(psi ** -10 * np.sum(St ** 2, axis=-1)) * dV
    mx2 = (8 * math.pi) ** 2 * np.sum(psi ** -6 * St[..., 0] ** 2) * dV
    A2 = sby.abar2(X, [((0, 0, 0), SIG, (P, 0, 0), (0, 0, 0))])
    h2 = np.sum(psi ** -18 * A2 ** 2) * dV          # (psi^-12 A2)^2 psi^6
    t1[f"P={P}"] = dict(M_norm_uncorrected=math.sqrt(m2), Mx_norm_uncorrected=math.sqrt(mx2),
                        H_norm_second_order=math.sqrt(h2),
                        A2_psi12_max=float((psi ** -12 * A2).max()))
E16 = 16 * math.pi * M * g * psi ** -5
out["single_clump"] = dict(mass=M, sigma=SIG, psi_centre=float(G.psi(np.zeros(3))),
                           H_matter_term_norm=math.sqrt(np.sum(E16 ** 2 * psi ** 6) * dV),
                           H_matter_term_max=float(E16.max()), by_momentum=t1)
# spin
Ssp = 0.04
St = sby.momentum_density(X, (0, 0, 0), SIG, (0, 0, 0), (0, 0, Ssp))
out["single_clump"]["spin"] = dict(
    S=Ssp, M_norm_uncorrected=math.sqrt((8 * math.pi) ** 2
                                        * np.sum(psi ** -10 * np.sum(St ** 2, axis=-1)) * dV),
    v_at_sigma=Ssp / (2 * SIG * M))
# rule 'velocity' with the curvature of P = sum m u: residual 8 pi (psi^3/<psi^3> - 1) P g
p3 = psi ** 3
mean3 = np.sum(p3 * g) * dV
res = (p3 / mean3 - 1.0) * g
out["single_clump"]["velocity_rule_residual_over_uncorrected"] = math.sqrt(
    np.sum(psi ** -10 * res ** 2) / np.sum(psi ** -10 * (p3 / mean3 * g) ** 2))


# ------------------------------------------------ deposit of lattice particles, 1D
def deposit_1d(n, half, h, nfilter, comp, sigma=SIG):
    """one-dimensional Gaussian sampled on the lattice h (i + 1/2), deposited with the
    linear cloud on n cells of [-half, half], then nfilter binomial passes and, if comp,
    the pass (-c, 1 + 2c, -c) with c = nfilter/4; returns (deposit, exact) at the cells"""
    dx = 2.0 * half / n
    xc = (np.arange(n) + 0.5) * dx - half
    xp = (np.arange(-int(6 * sigma / h), int(6 * sigma / h)) + 0.5) * h
    w = np.exp(-0.5 * (xp / sigma) ** 2) / math.sqrt(2 * math.pi) / sigma * h
    d = np.zeros(n)
    s = (xp + half) / dx - 0.5
    i0 = np.floor(s).astype(int)
    f = s - i0
    np.add.at(d, i0, w * (1 - f) / dx)
    np.add.at(d, i0 + 1, w * f / dx)
    for _ in range(nfilter):
        d = 0.25 * np.roll(d, 1) + 0.5 * d + 0.25 * np.roll(d, -1)
    if comp and nfilter > 0:
        c = nfilter / 4.0
        d = -c * np.roll(d, 1) + (1 + 2 * c) * d - c * np.roll(d, -1)
    return d, np.exp(-0.5 * (xc / sigma) ** 2) / math.sqrt(2 * math.pi) / sigma, dx


dep = {}
for label, nf, comp in (("filter4c", 4, True), ("filter0", 0, False)):
    row = {}
    for n in (32, 64, 128):
        d, e, dx = deposit_1d(n, 8.0, 0.125, nf, comp)
        a2, ae, e2 = np.sum(d * d) * dx, np.sum(d * e) * dx, np.sum(e * e) * dx
        # three-dimensional product: || d d d - e e e ||^2 / || e e e ||^2
        row[f"n={n}"] = math.sqrt(max(a2 ** 3 - 2 * ae ** 3 + e2 ** 3, 0.0) / e2 ** 3)
    dep[label] = row
out["lattice_deposit_error_over_field"] = dep

# -------------------------------------------- shot noise of equal-mass samples (dx=0.25)
th = np.linspace(-math.pi, math.pi, 20001)
s = np.sin(th / 2) ** 2
F = (1 - s) ** 4 * (1 + 4 * s)
kap1 = np.trapz(F ** 2 * (1 - 2 * s / 3), th) / (2 * math.pi)
kap0 = np.trapz((1 - 2 * s / 3), th) / (2 * math.pi)
psi10 = float(np.sum(psi ** -10 * g) * dV)
noise = {}
for N in (10 ** 4, 10 ** 5, 10 ** 6):
    noise[f"N={N}"] = dict(
        filter4c=math.sqrt(N * (8 * math.pi * 0.06 / N) ** 2 * psi10 * kap1 ** 3 / 0.25 ** 3),
        filter0=math.sqrt(N * (8 * math.pi * 0.06 / N) ** 2 * psi10 * kap0 ** 3 / 0.25 ** 3))
out["shot_noise_M_norm_dx0.25_P0.06"] = dict(kappa_1d_filter4c=kap1, kappa_1d_filter0=kap0,
                                             mean_psi_m10=psi10, by_N=noise)

# -------------------------------------------- two overdensities of the first paper (T5)
J = clm.JeansModel(yc=0.907)
x, u, m, sp = J.sample(10000, 1)
u = u - (m[:, None] * u).sum(0) / m.sum()           # as make_ic.py does
Pk = [(m[sp == k, None] * u[sp == k]).sum(0) for k in (1, 2)]
Lz = float(np.sum(m * (x[:, 0] * u[:, 1] - x[:, 1] * u[:, 0])))
Xj, dVj = grid(8.0, 200)
pj = J.psi(Xj)
Sv = np.zeros(Xj.shape)          # momentum density of the rule 'velocity', continuum
Sg = np.zeros(Xj.shape)          # momentum density the curvature solves for
for k in (1, 2):
    rk = np.sqrt(np.sum((Xj - J.centres[k]) ** 2, axis=-1))
    gk = sby.gaussian(rk, J.sigma)
    Sv += (J.m_c * pj ** 3 * gk)[..., None] * J.velocities[k - 1]
    Sg += gk[..., None] * Pk[k - 1]
c = (8 * math.pi) ** 2
out["two_overdensities"] = dict(
    clump_momenta=[[float(v) for v in p] for p in Pk],
    L_z_particles=Lz,
    L_z_clumps=float(sum(np.cross(J.centres[k], Pk[k - 1])[2] for k in (1, 2))),
    My_norm2_smooth=float(c * np.sum(pj ** -6 * Sv[..., 1] ** 2) * dVj),
    M_norm2_smooth=float(c * np.sum(pj ** -10 * np.sum(Sv ** 2, -1)) * dVj),
    smooth_residual_with_curvature_over_smooth=float(math.sqrt(
        np.sum(pj ** -6 * (Sv - Sg)[..., 1] ** 2) / np.sum(pj ** -6 * Sv[..., 1] ** 2))),
    second_order_mass=float(2 * sby.second_order_mass(
        J.sigma, P=float(np.linalg.norm(Pk[0])), psi=float(J.psi(J.centres[1])))),
    kinetic_energy_clumps=float(2 * J.m_c * (1 - 1 / J.W)),
    psi_at_clump=float(J.psi(J.centres[1])))
print(json.dumps(out, indent=1))
with open(os.path.join(HERE, "predict.json"), "w") as f:
    json.dump(out, f, indent=1)
