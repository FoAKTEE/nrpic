"""Homogeneous universe: a lattice of particles at rest, one or more per cell.

    python3 make_lattice.py --n 32 --ppc 1 --L 4 --H0 1 --out DIR

Writes DIR/particles.nrp. The masses give the density rho_0 = 3 H0^2 / (8 pi) on a slice
with psi = 1; the lattice of ppc^3 particles per cell is centred in the cells, so the
cloud-in-cell deposit is exactly uniform."""
import argparse
import os

import numpy as np

import ray_ic as ry
from nrp_io import write_particles

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=32, help="mesh cells per side")
ap.add_argument("--ppc", type=int, default=1, help="particles per cell per direction")
ap.add_argument("--L", type=float, default=4.0)
ap.add_argument("--H0", type=float, default=1.0)
ap.add_argument("--xmin", type=float, default=0.0)
ap.add_argument("--centred", action="store_true",
                help="particles at cell centres for odd ppc (default: shifted by half a "
                     "particle spacing, see make_east.py)")
ap.add_argument("--noise-x", type=float, default=0.0,
                help="white noise on the positions: uniform in (-A, A) per component")
ap.add_argument("--noise-u", type=float, default=0.0,
                help="white noise on the covariant momenta per unit mass")
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--rays", default="",
                help="comma-separated scale factors at which light rays leave the points "
                     "(L/4, L/4, L/4) and (3L/4, 3L/4, 3L/4) towards each other")
ap.add_argument("--cfl", type=float, default=0.25)
ap.add_argument("--ray-eps", type=float, default=1e-4)
ap.add_argument("--out", required=True)
a = ap.parse_args()

npd = a.n*a.ppc
h = a.L/npd
off = 0.5 if (a.centred or a.ppc % 2 == 0) else 1.0
q = a.xmin + np.mod((np.arange(npd) + off)*h, a.L)
X, Y, Z = np.meshgrid(q, q, q, indexing="ij")
x = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
rho0 = 3.0*a.H0**2/(8.0*np.pi)
m = np.full(len(x), rho0*h**3)
os.makedirs(a.out, exist_ok=True)
u = np.zeros_like(x)
if a.noise_x > 0.0 or a.noise_u > 0.0:
    rng = np.random.default_rng(a.seed)
    x = np.mod(x + a.noise_x*rng.uniform(-1.0, 1.0, x.shape) - a.xmin, a.L) + a.xmin
    u = a.noise_u*rng.uniform(-1.0, 1.0, x.shape)
if a.rays:
    # rays first in the file: the code records the particles with the lowest tags
    dt = a.cfl*a.L/a.n
    t_emit = [dt*round(2.0*(np.sqrt(float(v)) - 1.0)/a.H0/dt) for v in a.rays.split(",")]
    xr, cr, mr, meta = ry.bundles(t_emit, a.L, a.ray_eps)
    meta["tag"] = np.arange(len(mr))
    np.savez(os.path.join(a.out, "rays.npz"), **meta)
    x, u, m = np.concatenate([xr, x]), np.concatenate([cr, u]), np.concatenate([mr, m])
    print(f"{len(mr)} rays, emission times {t_emit}: set traj_ntrack = {len(mr)}")
write_particles(os.path.join(a.out, "particles.nrp"), x, u, m)
print(f"{len(x)} particles, mass each {m[-1]:.6e}, total {m[m > 0].sum():.6e}, rho0 {rho0:.6e}")
