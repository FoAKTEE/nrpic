#!/usr/bin/env python3
"""Initial data for the test-particle cluster validation (docs/results_cluster_test.md).

A compact cluster of N equal-mass test particles near the equatorial plane of a Kerr
black hole (mass M, spin a), written as a particle file (docs/FORMATS.md) in Cartesian
Kerr-Schild coordinates (the coordinates of the AthenaK runs).

Construction (everything exact for the given a, nothing linearised):

1. Centre-of-mass orbit.  An equatorial geodesic (Q = 0) with a radial turning point at
   Kerr-Schild (= Boyer-Lindquist) radius r_0, prograde, with axial angular momentum
   L = f_L * L_circ(r_0); the energy follows from R(r_0) = 0, the larger root.  f_L = 1
   gives the circular orbit (E, L) of Bardeen, Press & Teukolsky (1972); f_L < 1 an
   eccentric orbit with apocentre r_0.  The state (u_r^BL = 0, u_theta = 0, u_phi = L)
   is converted BL -> Cartesian KS with nrpic.kerr.convert_state and then rotated about
   the z axis (an isometry of Cartesian KS) so that the centre sits on the +x axis,
   x_c = (sqrt(r_0^2 + a^2), 0, 0), with covariant u_i^c.
2. Positions.  x_p = x_c + sigma_x * eta_p with eta_p ~ N(0, 1)^3: an isotropic Gaussian
   in the Cartesian KS coordinate offsets.
3. Momenta.  Orthonormal frame of the normal (Eulerian) observers: the triad
   e^i_(a) = (gamma^{-1/2})^{ia}, with gamma^{1/2} the symmetric positive square root of
   the spatial metric gamma_ij (eigen-decomposition), so the frame components of the
   spatial four-velocity are uhat_(a) = (gamma^{-1/2})_(a)^i u_i and
   u_i = (gamma^{1/2})_(i a) uhat_(a).  Each particle gets
       uhat_p = gamma^{-1/2}(x_c) u^c  +  sigma_v * xi_p,     xi_p ~ N(0, 1)^3,
       u_i(p) = gamma^{1/2}(x_p) uhat_p,
   i.e. the frame components of the centre's four-velocity are carried unchanged to
   the particle's position (the symmetric triad varies smoothly, so this is the
   "same velocity relative to the local normal observer" prescription) and an
   isotropic Gaussian of width sigma_v is added to the spatial four-velocity
   W v_(a) measured by the local normal observer.  (For sigma_v << 1 this is a
   dispersion sigma_v of the three-velocity, up to factors W ~ 1.06 at r_0 = 10 M.)
4. Masses.  m_p = m_tot / N (default m_tot = 1e-6 M; it only scales deposited fields).

The script also classifies every particle with the exact radial potential
R(r) = [E (r^2 + a^2) - a L]^2 - Delta [r^2 + (L - a E)^2 + Q]: "plunge" if the
allowed region R > 0 that contains the particle's radius reaches the outer horizon
(and the particle does not escape outward first), "escape" if it extends to infinity
(E > 1) and the particle is moving out or bounces, "bound" otherwise.  The numbers are
written to <out>.json next to the particle file.

Usage:
  make_cluster.py --N 10000 --a 0.9 --bound_only --out runs/cluster_test/ic/bound_a0.9_n10000.nrp
  make_cluster.py --N 10000 --a 0.0 --fL 0.96 --out ...      (plunging family)

With the nominal r_0 = 10 M, sigma_x = 0.5 M, sigma_v = 0.02 about 20 percent of a
Schwarzschild cluster is on plunging orbits (low-L tail: particles displaced inward keep
the centre's velocity); --bound_only redraws those, which conditions the Gaussian on
bound orbits.  For a = 0.9 M no particle is redrawn.
"""
import argparse
import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import kerr  # noqa: E402
from nrpic.io import write_nrp  # noqa: E402


# ----------------------------------------------------------------------------------------
# equatorial orbits
# ----------------------------------------------------------------------------------------
def circular_EL(r, a, M=1.0):
    """Prograde circular equatorial geodesic (Bardeen, Press & Teukolsky 1972)."""
    sq = np.sqrt(M * r)
    den = r ** 0.75 * np.sqrt(r ** 1.5 - 3 * M * np.sqrt(r) + 2 * a * np.sqrt(M))
    E = (r ** 1.5 - 2 * M * np.sqrt(r) + a * np.sqrt(M)) / den
    L = np.sqrt(M) * (r * r - 2 * a * sq + a * a) / den
    return E, L


def energy_at_turning_point(r, L, a, M=1.0):
    """E of the equatorial orbit (Q = 0) with angular momentum L and R(r) = 0."""
    A = r * r + a * a
    D = r * r - 2 * M * r + a * a
    c2 = A * A - D * a * a
    c1 = -2.0 * (a * L * A - D * a * L)
    c0 = a * a * L * L - D * (r * r + L * L)
    disc = c1 * c1 - 4 * c2 * c0
    return (-c1 + np.sqrt(disc)) / (2 * c2)


def radial_potential(r, E, L, Q, a, M=1.0):
    D = r * r - 2 * M * r + a * a
    return (E * (r * r + a * a) - a * L) ** 2 - D * (r * r + (L - a * E) ** 2 + Q)


def centre_state(r0, a, M=1.0, fL=1.0):
    """Cartesian KS position and covariant u_i of the centre-of-mass orbit."""
    Ec, Lc = circular_EL(r0, a, M)
    L = fL * Lc
    E = Ec if fL == 1.0 else energy_at_turning_point(r0, L, a, M)
    x_bl = np.array([r0, np.pi / 2, 0.0])
    u_bl = np.array([0.0, 0.0, L])
    _, x_c, u_c = kerr.convert_state(0.0, x_bl, u_bl, "bl", "cks", a, M, u_t=-E)
    # rotate about z so that the centre lies on the +x axis (axisymmetry of Kerr)
    ph = np.arctan2(x_c[1], x_c[0])
    c, s = np.cos(-ph), np.sin(-ph)
    R = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    x_c = R @ x_c
    u_c = R @ u_c
    x_c[1] = 0.0
    x_c[2] = 0.0
    u_c[2] = 0.0
    return x_c, u_c, E, L, Ec, Lc


# ----------------------------------------------------------------------------------------
# normal-observer frames
# ----------------------------------------------------------------------------------------
def sym_sqrt(g):
    """Symmetric square root and its inverse of SPD matrices g[..., 3, 3]."""
    w, V = np.linalg.eigh(g)
    s = np.sqrt(w)
    S = np.einsum("...ij,...j,...kj->...ik", V, s, V)
    Si = np.einsum("...ij,...j,...kj->...ik", V, 1.0 / s, V)
    return S, Si


def frame_momentum(x, u, a, M=1.0):
    """uhat_(a) = (gamma^{-1/2})_(a)^i u_i at x."""
    g = kerr.adm("cks", x, a, M, derivs=False).gamma
    _, Si = sym_sqrt(g)
    return np.einsum("...ij,...j->...i", Si, u)


def covariant_from_frame(x, uhat, a, M=1.0):
    g = kerr.adm("cks", x, a, M, derivs=False).gamma
    S, _ = sym_sqrt(g)
    return np.einsum("...ij,...j->...i", S, uhat)


# ----------------------------------------------------------------------------------------
# classification
# ----------------------------------------------------------------------------------------
def classify(x, u, a, M=1.0, rmax=1.0e4, ngrid=4000):
    """Return (labels, E, L, Q, r) with labels 0 = bound, 1 = plunge, 2 = escape."""
    E, L, Q = kerr.invariants("cks", x, u, a, M)
    r = kerr.cks_radius(x, a)
    rp, _ = kerr.horizon_radii(a, M)
    # dr/dt sign from the 3+1 velocity
    m = kerr.adm("cks", x, a, M, derivs=False)
    U = np.einsum("...ij,...j->...i", m.gamma_inv, u)
    W = np.sqrt(1 + np.einsum("...i,...i->...", u, U))
    xdot = (m.alpha / W)[..., None] * U - m.beta
    rdot = kerr.dr_dt("cks", x, xdot, a)
    s = np.linspace(0.0, 1.0, ngrid)[1:-1]
    inner = rp + (r[:, None] - rp) * s[None, :]
    R_in = radial_potential(inner, E[:, None], L[:, None], Q[:, None], a, M)
    open_in = np.all(R_in > 0.0, axis=1)
    lg = np.exp(np.log(r[:, None]) + (np.log(rmax) - np.log(r[:, None])) * s[None, :])
    R_out = radial_potential(lg, E[:, None], L[:, None], Q[:, None], a, M)
    open_out = np.all(R_out > 0.0, axis=1) & (E >= 1.0)
    lab = np.zeros(len(r), dtype=int)
    lab[open_in & ~open_out] = 1
    lab[open_in & open_out & (rdot < 0)] = 1
    lab[open_in & open_out & (rdot >= 0)] = 2
    lab[~open_in & open_out] = 2
    return lab, E, L, Q, r


# ----------------------------------------------------------------------------------------
def make_cluster(N, a, M=1.0, r0=10.0, sigx=0.5, sigv=0.02, fL=1.0, mtot=1.0e-6, seed=1,
                 bound_only=False):
    """Draw the cluster.  With bound_only, particles whose exact orbit plunges or escapes
    are redrawn (rejection sampling), so the result is the Gaussian cluster conditioned
    on every orbit being bound; the number of redraws is returned in meta."""
    rng = np.random.default_rng(seed)
    x_c, u_c, E_c, L_c, Ec_circ, Lc_circ = centre_state(r0, a, M, fL)
    uh_c = frame_momentum(x_c, u_c, a, M)

    def draw(n):
        x = x_c[None, :] + sigx * rng.standard_normal((n, 3))
        uh = uh_c[None, :] + sigv * rng.standard_normal((n, 3))
        return x, covariant_from_frame(x, uh, a, M)

    x, u = draw(N)
    nrej = 0
    if bound_only:
        for _ in range(100):
            lab = classify(x, u, a, M)[0]
            bad = np.nonzero(lab != 0)[0]
            if len(bad) == 0:
                break
            nrej += len(bad)
            x[bad], u[bad] = draw(len(bad))
        else:
            raise RuntimeError("rejection sampling did not converge")
    m = np.full(N, mtot / N)
    meta = dict(N=N, a=a, M=M, r0=r0, sigx=sigx, sigv=sigv, fL=fL, mtot=mtot, seed=seed,
                bound_only=bool(bound_only), n_redrawn=int(nrej),
                x_c=x_c.tolist(), u_c=u_c.tolist(), uhat_c=uh_c.tolist(),
                E_c=float(E_c), L_c=float(L_c), E_circ=float(Ec_circ),
                L_circ=float(Lc_circ))
    return x, u, m, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--a", type=float, default=0.0)
    ap.add_argument("--M", type=float, default=1.0)
    ap.add_argument("--r0", type=float, default=10.0)
    ap.add_argument("--sigx", type=float, default=0.5)
    ap.add_argument("--sigv", type=float, default=0.02)
    ap.add_argument("--fL", type=float, default=1.0,
                    help="L of the centre orbit in units of the circular L at r0")
    ap.add_argument("--mtot", type=float, default=1.0e-6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bound_only", action="store_true",
                    help="redraw particles whose exact orbit plunges or escapes")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    x, u, m, meta = make_cluster(args.N, args.a, args.M, args.r0, args.sigx, args.sigv,
                                 args.fL, args.mtot, args.seed, args.bound_only)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    write_nrp(args.out, x, u, m)

    lab, E, L, Q, r = classify(x, u, args.a, args.M)
    # check of the centre state: invariants and normalisation
    Ec, Lc, Qc = kerr.invariants("cks", np.array(meta["x_c"]), np.array(meta["u_c"]),
                                 args.a, args.M)
    meta.update(
        check_centre=dict(E=float(Ec), L=float(Lc), Q=float(Qc),
                          dE=float(Ec - meta["E_c"]), dL=float(Lc - meta["L_c"])),
        n_bound=int((lab == 0).sum()), n_plunge=int((lab == 1).sum()),
        n_escape=int((lab == 2).sum()),
        E_pct=np.percentile(E, [0, 10, 50, 90, 100]).tolist(),
        L_pct=np.percentile(L, [0, 10, 50, 90, 100]).tolist(),
        Q_pct=np.percentile(Q, [0, 10, 50, 90, 100]).tolist(),
        r_pct=np.percentile(r, [0, 10, 50, 90, 100]).tolist(),
        z_absmax=float(np.abs(x[:, 2]).max()),
        file=os.path.abspath(args.out))
    with open(os.path.splitext(args.out)[0] + ".json", "w") as f:
        json.dump(meta, f, indent=1)
    np.save(os.path.splitext(args.out)[0] + ".class.npy", lab)
    print(f"{args.out}: N={args.N} a={args.a} E_c={meta['E_c']:.10f} L_c={meta['L_c']:.10f}"
          f" bound={meta['n_bound']} plunge={meta['n_plunge']} escape={meta['n_escape']}")


if __name__ == "__main__":
    main()
