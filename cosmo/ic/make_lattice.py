"""Homogeneous universe: a lattice of particles at rest, one or more per cell.

    python3 make_lattice.py --n 32 --ppc 1 --L 4 --H0 1 --out DIR

Writes DIR/particles.nrp. The masses give the density rho_0 = 3 H0^2 / (8 pi) on a slice
with psi = 1; the lattice of ppc^3 particles per cell is centred in the cells, so the
cloud-in-cell deposit is exactly uniform."""
import argparse
import os

import numpy as np

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
write_particles(os.path.join(a.out, "particles.nrp"), x, np.zeros_like(x), m)
print(f"{len(x)} particles, mass each {m[0]:.6e}, total {m.sum():.6e}, rho0 {rho0:.6e}")
