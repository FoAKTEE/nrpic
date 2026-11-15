#!/usr/bin/env python3
"""Particle files for the first Newtonian-mode runs of secondary infall (RUNS.md section 3,
wave 2). Writes no simulation code: positions, velocities and masses for AthenaK's
Newtonian mode (`<particles> pusher = newton`, coord/INTERFACES/newtonian_mode.md), and a
JSON file with every derived parameter of the run.

Set-up (units G = 1, M = 1 the hole, eps = H_i M, t_i = 2/(3 eps); a = 1 in the code, so the
code works in physical coordinates and its time t is t_cosmic - t_i):
  hole   a compact CLUMP of n_clump equal-mass particles of total mass 1, cold, on a cubic
         lattice inside r < r_clump (the release executable has no fixed point mass; the
         request newtonian-mode-point-mass is open). Tags 0 .. n_clump - 1.
  dust   uniform density rho_i = 3 eps^2/(8 pi) for R_w <= r < R_edge, Hubble flow
         v = eps x, cold, equal masses on the cubic lattice x = (i + 1/2) h (symmetric
         under every reflection and axis permutation, so the system keeps the octahedral
         symmetry and the clump feels no net force but rounding). Tags follow the clump.
  R_edge = edge_fac * r_last, r_last the initial radius of the shell that turns around
         at a/a_i = a_end (closed form, common.kepler_radial); by Birkhoff's theorem dust
         farther out does not act on the inside.
  tracers (kind field): massless particles, log-uniform in r on [rmin, rmax], isotropic,
         at rest, after the massive ones; one step of the code gives the acceleration.

kind infall : clump + dust
kind field  : clump + tracers (calibrates the mesh-softened field of the clump)
kind fieldfull : clump + dust + tracers (the field of the whole set-up at t = 0)

Usage: python3 nm_ic.py --out DIR --kind infall --eps 0.03 --aend 4 [options]
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import kepler_radial  # noqa: E402
from nrpic import io as nio      # noqa: E402


def lattice_ball(h, rmin, rmax):
    """Nodes (i + 1/2) h of a cubic lattice with rmin <= |x| < rmax."""
    n = int(np.ceil(rmax / h)) + 1
    g = (np.arange(-n, n) + 0.5) * h
    out = []
    Y, Z = np.meshgrid(g, g, indexing="ij")
    for gx in g:                      # slab by slab: bounded memory
        r2 = gx * gx + Y * Y + Z * Z
        k = (r2 >= rmin * rmin) & (r2 < rmax * rmax)
        if k.any():
            out.append(np.stack([np.full(k.sum(), gx), Y[k], Z[k]], axis=1))
    return np.concatenate(out) if out else np.zeros((0, 3))


def spacing_for(n_target, rmin, rmax):
    vol = 4.0 * np.pi / 3.0 * (rmax**3 - rmin**3)
    return (vol / n_target) ** (1.0 / 3.0)


def derived(a):
    eps = a.eps
    t_i = 2.0 / (3.0 * eps)
    rho_i = 3.0 * eps**2 / (8.0 * np.pi)
    T = t_i * a.aend**1.5

    def menc(r):
        return 1.0 + 4.0 * np.pi / 3.0 * rho_i * (r**3 - a.rw**3)

    r_last = brentq(lambda r: kepler_radial(r, eps * r, menc(r), t_i)["t_ta"] - T,
                    1.01 * a.rw, 1e4)
    r_edge = a.edge_fac * r_last
    sol = solve_ivp(lambda t, y: [y[1], -menc(r_edge) / y[0]**2], [t_i, T],
                    [r_edge, eps * r_edge], rtol=1e-11, atol=1e-12)
    r_edge_T = float(sol.y[0, -1])
    L = a.L if a.L > 0 else float(np.ceil(a.box_fac * r_edge_T))
    return dict(eps=eps, t_i=t_i, rho_i=rho_i, a_end=a.aend, t_end_cosmic=T,
                tlim=T - t_i, r_w=a.rw, r_last=r_last, edge_fac=a.edge_fac, r_edge=r_edge,
                r_edge_end=r_edge_T, L=L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kind", choices=("infall", "field", "fieldfull"), default="infall")
    ap.add_argument("--eps", type=float, default=0.03)
    ap.add_argument("--aend", type=float, default=4.0)
    ap.add_argument("--rw", type=float, default=3.0, help="vacuum core radius (M)")
    ap.add_argument("--edge_fac", type=float, default=1.2)
    ap.add_argument("--box_fac", type=float, default=1.12,
                    help="box half-width / radius of the dust edge at a_end")
    ap.add_argument("--L", type=float, default=0.0, help="box half-width (overrides)")
    ap.add_argument("--ndust", type=float, default=5e5, help="target number of dust particles")
    ap.add_argument("--nclump", type=float, default=2e4, help="target number in the clump")
    ap.add_argument("--rclump", type=float, default=0.3)
    ap.add_argument("--ntracer", type=int, default=3000)
    ap.add_argument("--rmin", type=float, default=0.05)
    ap.add_argument("--rmax", type=float, default=30.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--shift", type=float, nargs=3, default=[0.0, 0.0, 0.0],
                    help="displacement of the whole configuration (e.g. to a cell centre)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    p = derived(a)

    hc = spacing_for(a.nclump, 0.0, a.rclump)
    xc = lattice_ball(hc, 0.0, a.rclump)
    mc = np.full(len(xc), 1.0 / len(xc))
    xs, us, ms = [xc], [np.zeros_like(xc)], [mc]
    p.update(clump_spacing=hc, n_clump=len(xc), r_clump=a.rclump,
             clump_rms=float(np.sqrt((xc**2).sum(1).mean())))
    if a.kind in ("infall", "fieldfull"):
        hd = spacing_for(a.ndust, a.rw, p["r_edge"])
        xd = lattice_ball(hd, a.rw, p["r_edge"])
        md = np.full(len(xd), p["rho_i"] * hd**3)
        xs.append(xd)
        us.append(a.eps * xd)
        ms.append(md)
        p.update(dust_spacing=hd, n_dust=len(xd), m_dust_particle=float(md[0]),
                 m_dust=float(md.sum()),
                 m_dust_continuum=float(4.0 * np.pi / 3.0 * p["rho_i"]
                                        * (p["r_edge"]**3 - a.rw**3)))
    else:
        p.update(n_dust=0, m_dust=0.0)
    if a.kind in ("field", "fieldfull"):
        rng = np.random.default_rng(a.seed)
        r = np.exp(rng.uniform(np.log(a.rmin), np.log(a.rmax), size=a.ntracer))
        d = rng.normal(size=(a.ntracer, 3))
        d /= np.sqrt((d * d).sum(1))[:, None]
        xt = r[:, None] * d
        xs.append(xt)
        us.append(np.zeros_like(xt))
        ms.append(np.zeros(a.ntracer))
        p.update(n_tracer=a.ntracer, tracer_rmin=a.rmin, tracer_rmax=a.rmax, seed=a.seed)
    else:
        p.update(n_tracer=0)
    x, u, m = np.concatenate(xs), np.concatenate(us), np.concatenate(ms)
    x = x + np.asarray(a.shift)[None, :]
    p["shift"] = list(a.shift)
    nio.write_nrp(os.path.join(a.out, "particles.nrp"), x, u, m)
    p.update(kind=a.kind, n_total=len(m), tag_clump=[0, p["n_clump"]],
             tag_dust=[p["n_clump"], p["n_clump"] + p["n_dust"]],
             tag_tracer=[p["n_clump"] + p["n_dust"], len(m)],
             total_mass=float(m.sum()))
    with open(os.path.join(a.out, "setup.json"), "w") as f:
        json.dump(p, f, indent=1)
        f.write("\n")
    print(json.dumps(p, indent=1))


if __name__ == "__main__":
    main()
