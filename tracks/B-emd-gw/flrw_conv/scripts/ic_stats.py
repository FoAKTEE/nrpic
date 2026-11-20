"""Deposited density contrast of a particle file with the cloud and compensation of the
production configuration (cosmo/ic/cosmo_id.py: cic_deposit with shape pcs, then
compensate_density with c = 1/6, c2 = 7/15, as <particles> deposit_comp_c, _c2).

    python3 ic_stats.py <ic dir> <n> <L>      writes <ic dir>/ic_stats.json

On the initial slice of leg F (psi = 1, a = 1) the energy density of particles at rest is
the deposit itself, so delta = deposit / rho_0 - 1 is the contrast the code starts from.
Also: the potential of that contrast, Phi_k = -(3/2) delta_k / k^2 (initial Hubble rate 1;
the Newtonian Poisson equation, [JUDGEMENT] adequate at the cell scale, k/H >= 4.65),
which sets the size of the local lapse and conformal-factor perturbations to expect.
"""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "cosmo", "ic"))
import cosmo_id as cid  # noqa: E402


def read_particles(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        n, = struct.unpack("q", f.read(8))
        rec = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
    return rec[:, 0:3], rec[:, 3:6], rec[:, 6]


def stats(d, n, L):
    x, u, m = read_particles(os.path.join(d, "particles.nrp"))
    rho0 = 3.0/(8.0*np.pi)
    dep = cid.cic_deposit(x, m, n, L, shape="pcs")
    comp = cid.compensate_density([dep], 1.0/6.0, 0.0, 7.0/15.0)[0]
    out = {"n": n, "L": L, "N_particles": int(len(m)), "ppc": float(len(m))/n**3,
           "mass_sum_over_rho0_L3": float(m.sum()/(rho0*L**3)),
           "max_abs_u": float(np.abs(u).max())}
    for name, f in (("raw", dep), ("compensated", comp)):
        dl = f/rho0 - 1.0
        out[f"delta_{name}_mean"] = float(dl.mean())
        out[f"delta_{name}_rms"] = float(dl.std())
        out[f"delta_{name}_max_abs"] = float(np.abs(dl).max())
    dl = comp/rho0 - 1.0
    kx = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    KX, KY, KZ = np.meshgrid(kx, kx, kx, indexing="ij")
    k2 = KX**2 + KY**2 + KZ**2
    k2[0, 0, 0] = 1.0
    dk = np.fft.fftn(dl)
    phik = -1.5*dk/k2
    phik[0, 0, 0] = 0.0
    phi = np.real(np.fft.ifftn(phik))
    out["phi_rms"] = float(phi.std())
    out["phi_max_abs"] = float(np.abs(phi).max())
    out["delta_times_phi_mean"] = float((dl*phi).mean())
    with open(os.path.join(d, "ic_stats.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    return out


if __name__ == "__main__":
    d, n, L = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    s = stats(d, n, L)
    print(json.dumps(s))
