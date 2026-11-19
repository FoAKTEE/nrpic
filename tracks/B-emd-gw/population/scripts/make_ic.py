"""Initial data of the halo-population box of Track B (package `population`, G3 design).

    python3 make_ic.py --n 64 --L 4 --nc 3.2 --sigma1 0.0562 --seed 1 --ppc 1 --out DIR [--gr]

Field. Gaussian random density contrast delta_N on the n^3 mesh at a = 1 (start of the
run, Hubble rate 1, units G = c = 1, lengths in initial Hubble radii) drawn with
cosmo/ic/random_field.py (gaussian_field, noise drawn shell by shell, so meshes of
different n share every mode below the cut). Spectrum: the growing mode of an early
matter era for a scale-invariant curvature spectrum P_R = A_s,

    delta_N(k, a) = (2/5) (k / Hc)^2 R_k = (2/5) k^2 a R_k   (code units, Hc = a^(-1/2)),
    P_delta(k, a = 1) = 2 pi^2 (4/25) A_s k,                  Delta^2 = (4/25) A_s k^4,

from Phi = (3/5) R (arXiv:2312.12499 main.tex:324) and the code's Poisson relation
k^2 psi_N = (3/2) delta_N at a = 1 (cosmo/ic/make_field.py:9). [arXiv:2312.12499 writes
(6/5) (a/a_hor) R for the same quantity (main.tex:581); the factor 3 is TO VERIFY; with
their normalization A_s is 9 times smaller for the same field.] Sharp spherical cut at
k_c = nc 2 pi / L (the resolution cut-off of the box, as the Nyquist cut of 2312.12499),
Nyquist planes zeroed (zeldovich displacement exact). The amplitude is given as sigma1,
the ensemble rms of delta_N at a = 1 over the mesh modes; A_s follows.

Particles. Newtonian reference: cosmo/ic/make_field.py newtonian_particles (Zel'dovich
lattice, growing-mode velocities dx/dt = H f xi at a = 1, masses from the target density
and the Jacobian), masses rescaled so that the total is rho_m L^3 with rho_m = 3/(8 pi)
(the Newtonian mode assumes this mean; coord/INTERFACES/newtonian_mode.md section 4).
In the Newtonian mode the momentum slot holds p = a dx/dt = dx/dt at a = 1.
With --gr also the relativistic data of the same field (make_field.build: dictionary of
Chisari-Zaldarriaga and Green-Wald and the constraint solve on the torus), with the
deposit of the production configuration of cosmo/README.md (pcs, compensation 1/6, 7/15).

Writes DIR/particles_newton.nrp, DIR/delta0.npy, DIR/meta.json and with --gr
DIR/particles.nrp, DIR/fields.bin, DIR/id.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cosmo", "ic"))
import cosmo_id as cid          # noqa: E402
import make_field as mf         # noqa: E402
import random_field as rf       # noqa: E402
from nrp_io import write_fields, write_particles   # noqa: E402

RHO_M = 3.0/(8.0*np.pi)


def pk_unit(k):
    """P_delta(k, a = 1) for A_s = 1 (code units)."""
    return 2.0*np.pi**2*(4.0/25.0)*np.asarray(k, dtype=float)


def mesh_sigma2_unit(n, L, kc):
    """Ensemble variance of delta_N over the mesh modes kept (|k| <= kc, Nyquist planes
    zeroed) for A_s = 1: sum_k P(|k|)/L^3."""
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    nyq = (np.abs(np.fft.fftfreq(n)*n) == n//2) if n % 2 == 0 else np.zeros(n, bool)
    kx, ky, kz = np.meshgrid(k1, k1, k1, indexing="ij")
    kk = np.sqrt(kx*kx + ky*ky + kz*kz)
    ok = (kk > 0) & (kk <= kc*(1.0 + 1e-12))
    ok &= ~(nyq[:, None, None] | nyq[None, :, None] | nyq[None, None, :])
    return float(pk_unit(kk[ok]).sum()/L**3), int(ok.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=float, required=True, help="box in initial Hubble radii")
    ap.add_argument("--nc", type=float, required=True, help="cut k_c in units of 2 pi/L")
    ap.add_argument("--sigma1", type=float, required=True,
                    help="ensemble rms of delta_N at a = 1 over the mesh modes")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ppc", type=int, default=1)
    ap.add_argument("--gr", action="store_true", help="also the relativistic data")
    ap.add_argument("--gr-nosolve", action="store_true",
                    help="relativistic data of the dictionary without the constraint "
                         "solve (for timing runs only)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    kf = 2.0*np.pi/a.L
    kc = a.nc*kf
    s2u, nmodes = mesh_sigma2_unit(a.n, a.L, kc)
    As = a.sigma1**2/s2u

    def pk(k):
        return As*pk_unit(k)

    delta = rf.gaussian_field(a.n, a.L, pk, a.seed, kcut=kc, cut="sharp", zero_nyquist=True)
    np.save(os.path.join(a.out, "delta0.npy"), delta.astype(np.float64))
    x, v, m, q = mf.newtonian_particles(delta, a.L, H=1.0, ppc=a.ppc)
    mscale = RHO_M*a.L**3/m.sum()
    m = m*mscale
    write_particles(os.path.join(a.out, "particles_newton.nrp"), x, v, m)
    tor = cid.Torus(a.n, a.L)
    psiN, _ = mf.spectral_fields(tor, delta, 1.0, 1.0)
    meta = {
        "n": a.n, "L": a.L, "nc": a.nc, "k_f": kf, "k_c": kc, "seed": a.seed, "ppc": a.ppc,
        "sigma1_target": a.sigma1, "sigma1_realized": float(delta.std()),
        "delta_max": float(delta.max()), "delta_min": float(delta.min()),
        "A_s": As, "A_s_2312_normalization": As/9.0, "mesh_modes_kept": nmodes,
        "spectrum": "P_delta(k,a=1) = 2 pi^2 (4/25) A_s k, sharp cut at k_c",
        "N_particles": int(len(m)), "mass_rescale": float(mscale),
        "mass_min_over_mean": float(m.min()/m.mean()),
        "mass_max_over_mean": float(m.max()/m.mean()),
        "max_displacement_over_h": float(np.abs(v).max()/(a.L/a.n)),
        "max_velocity": float(np.sqrt((v*v).sum(axis=1)).max()),
        "rms_velocity": float(np.sqrt((v*v).sum(axis=1).mean())),
        "max_abs_psiN": float(np.abs(psiN).max()), "rms_psiN": float(psiN.std()),
        "horizon_entry_a_of_kc": 1.0/kc**2,
    }
    if a.gr_nosolve:
        # timing data only: the dictionary without the constraint solve (conformal factor
        # of the dictionary, Ahat = 0); not a solution of the constraints
        K = -3.0*(1.0 - psiN)                      # growth rate 1: d psi_N/d ln a = 0
        alpha = np.sqrt(1.0 + 2.0*psiN)
        psi = (1.0 - 2.0*psiN)**0.25
        dN_p = cid.interp(delta, x, a.L)
        psiN_p = cid.interp(psiN, x, a.L)
        psi_p = (1.0 - 2.0*psiN_p)**0.25
        alpha_p = np.sqrt(1.0 + 2.0*psiN_p)
        v2 = psi_p**4*(v*v).sum(axis=1)/alpha_p**2
        W = 1.0/np.sqrt(1.0 - v2)
        ug = (psi_p**4*W/alpha_p)[:, None]*v
        # rest-mass weight of make_field.build: rho_m (1 + dN - 2 psiN) W psi^6 jac hq^3
        mg = m/mscale*W*psi_p**6*(1.0 + dN_p - 2.0*psiN_p)/(1.0 + dN_p)
        write_particles(os.path.join(a.out, "particles.nrp"), x, ug, mg)
        write_fields(os.path.join(a.out, "fields.bin"), psi, K, alpha, None)
        meta["gr_nosolve"] = True
    if a.gr:
        cid.SHAPE = "pcs"
        cid.DEP_COMP_C = 1.0/6.0
        cid.DEP_COMP_C2 = 7.0/15.0
        xg, ug, mg, r, K, alpha, info, _ = mf.build(delta, a.L, 1.0, a.ppc)
        write_particles(os.path.join(a.out, "particles.nrp"), xg, ug, mg)
        write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
        with open(os.path.join(a.out, "id.json"), "w") as f:
            json.dump(info, f, indent=1)
        meta["gr"] = {key: info[key] for key in (
            "max_abs_psiN", "max_psi_minus_dictionary", "max_abs_Ahat",
            "max_hamiltonian_residual", "max_momentum_residual",
            "outer_last_change_of_psi", "total_rest_mass", "rho_m_L3")}
    meta["wall_s"] = time.time() - t0
    with open(os.path.join(a.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    for key, val in meta.items():
        print(f"{key}: {val}")


if __name__ == "__main__":
    main()
