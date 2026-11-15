#!/usr/bin/env python3
"""Particle files of the newton_tests package (Track B, Newtonian mode of AthenaK).

    make_particles.py pancake-east --n 64 --delta 0.05 --L 1 --out DIR
    make_particles.py pancake-sin  --n 32 --delta 0.05 --L 1 --out DIR
    make_particles.py ellipsoid    --n 64 --half 12 --ppd 2 --alpha 0.11122237 \
                                   [--ratios 1,0.60089,0.19730] --out DIR

pancake-east  the particles of the verify_cosmo pancake (cosmo/newton/pm.py east_particles
              with ratios (1, 0, 0), used unchanged as a library): lattice q = (i + 1) h,
              x = q + (d/k) cos(k q_x), p = dx/dt = (d/k) cos(k x_x) at a = 1, masses that
              make the density contrast d sin(k x_x). The n sheets of the x line through
              the first lattice point in y and z come first, ordered by q_x, so that the
              trajectory output (tag < n) records one particle per sheet.
pancake-sin   an equal-mass Zel'dovich lattice: q = (i + 1/2) h, x = q + psi(q_x),
              psi = (d/k) sin(k q), p = psi (growing mode at a = 1, H = 1). The particles
              move towards x = L/2 and never wrap before shell crossing (a = 1/d), so the
              second moment about the origin is defined; exact solution x = q + a psi.
ellipsoid     the Zel'dovich ellipsoid of baseline/scripts/ellipsoid.py at the turnaround
              of its first axis, t_turn = (2 alpha)^-3/2 t_k (G = c = t_k = 1, M = 3/4,
              R_L = 3/2): equal-mass particles on a cubic lattice of spacing
              2 half/(n ppd) with nodes at (j + 1/2) spacing (symmetric about the
              origin), kept inside the ellipsoid of semi-axes R_i(t_turn), velocity
              v_i = (V_i/R_i) x_i. The run's time 0 is t_turn.

Each call writes DIR/particles.nrp and DIR/particles.json (parameters, the numbers the
analysis needs).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "cosmo", "newton"))
sys.path.insert(0, os.path.join(WT, "tracks", "B-emd-gw", "baseline", "scripts"))

import numpy as np  # noqa: E402

from nrpic import io as nio  # noqa: E402

# shape of the 2605.04487 benchmark (baseline/scripts/run_baseline.py line 26)
B2605 = np.array([0.11122237, 0.06683367, 0.02194397])


def pancake_east(a):
    import pm as P
    x, v, m, q = P.east_particles(a.delta, a.n, 1, a.L, ratios=(1.0, 0.0, 0.0))
    L = a.L
    line = np.flatnonzero((np.abs(q[:, 1] - q[0, 1]) < 1e-12*L)
                          & (np.abs(q[:, 2] - q[0, 2]) < 1e-12*L))
    line = line[np.argsort(q[line, 0])]
    rest = np.setdiff1d(np.arange(len(m)), line)
    order = np.concatenate([line, rest])
    x, v, m, q = x[order], v[order], m[order], q[order]
    nio.write_nrp(os.path.join(a.out, "particles.nrp"), x, v, m)
    return dict(kind="pancake-east", n=a.n, L=L, delta=a.delta, ntrack=len(line),
                nparticle=len(m), q_line=q[:len(line), 0].tolist(),
                x0_line=x[:len(line), 0].tolist(), v0_line=v[:len(line), 0].tolist(),
                m_line=m[:len(line)].tolist(), mass_total=float(m.sum()))


def pancake_sin(a):
    L, n = a.L, a.n
    k = 2.0*np.pi/L
    h = L/n
    q1 = (np.arange(n) + 0.5)*h
    Q = np.meshgrid(q1, q1, q1, indexing="ij")
    q = np.stack([f.ravel() for f in Q], axis=1)
    psi = (a.delta/k)*np.sin(k*q[:, 0])
    x = q.copy()
    x[:, 0] += psi
    u = np.zeros_like(x)
    u[:, 0] = psi
    rho0 = 3.0/(8.0*np.pi)
    m = np.full(len(x), rho0*h**3)
    nio.write_nrp(os.path.join(a.out, "particles.nrp"), x, u, m)
    # sums of the exact second moment I(a) = c0 + c1 a + c2 a^2 (per component)
    S = {}
    for i in range(3):
        for j in range(i, 3):
            qi, qj = q[:, i], q[:, j]
            pi = psi if i == 0 else 0.0*psi
            pj = psi if j == 0 else 0.0*psi
            S["%d%d" % (i, j)] = [float((m*qi*qj).sum()),
                                  float((m*(qi*pj + pi*qj)).sum()),
                                  float((m*pi*pj).sum())]
    return dict(kind="pancake-sin", n=n, L=L, delta=a.delta, nparticle=len(m),
                mass_total=float(m.sum()), moment_coeffs=S, a_cross=1.0/a.delta)


def ellipsoid(a):
    import ellipsoid as el
    ratios = np.array([float(s) for s in a.ratios.split(",")])
    lam = a.alpha*ratios
    t0, R0, V0 = el.initial_state(lam)
    s = 2.0*a.half/(a.n*a.ppd)
    nh = int(np.ceil(R0.max()/s)) + 1
    g = (np.arange(-nh, nh) + 0.5)*s
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    keep = (X/R0[0])**2 + (Y/R0[1])**2 + (Z/R0[2])**2 < 1.0
    x = np.stack([X[keep], Y[keep], Z[keep]], axis=1)
    npart = len(x)
    m = np.full(npart, el.MASS/npart)
    u = x*(V0/R0)[None, :]
    nio.write_nrp(os.path.join(a.out, "particles.nrp"), x, u, m)
    I0 = [[float((m*x[:, i]*x[:, j]).sum()) for j in range(3)] for i in range(3)]
    return dict(kind="ellipsoid", n=a.n, half=a.half, ppd=a.ppd, spacing=s,
                alpha=a.alpha, ratios=ratios.tolist(), lam=lam.tolist(), t_turn=t0,
                R0=R0.tolist(), V0=V0.tolist(), mass=el.MASS, nparticle=npart,
                I0=I0, I0_continuum=[el.MASS*r**2/5.0 for r in R0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("pancake-east", "pancake-sin", "ellipsoid"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--delta", type=float, default=0.05)
    ap.add_argument("--half", type=float, default=12.0)
    ap.add_argument("--ppd", type=int, default=2)
    ap.add_argument("--alpha", type=float, default=float(B2605[0]))
    ap.add_argument("--ratios", default=",".join("%.17g" % r for r in B2605/B2605[0]))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = {"pancake-east": pancake_east, "pancake-sin": pancake_sin,
            "ellipsoid": ellipsoid}[a.kind](a)
    meta["argv"] = sys.argv[1:]
    with open(os.path.join(a.out, "particles.json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s: %d particles" % (os.path.join(a.out, "particles.nrp"),
                                      meta["nparticle"]))


if __name__ == "__main__":
    main()
