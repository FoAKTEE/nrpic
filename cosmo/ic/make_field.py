"""Relativistic initial data for the NRPIC code from a Newtonian density field on the
mesh (cosmo/PLAN.md, C5 test C and C6): the generalization of make_east.py from three
sine waves to any periodic field, for example a Gaussian random field drawn from a
power spectrum (random_field.py).

Input (code units G = c = 1, a = 1 and Hubble rate H at the start, box [0, L)^3):
    delta_N on the n^3 mesh, growing mode, growth rate f = d ln D / d ln a.
Newtonian quantities (matter density parameter omega_m at the start):
    lap psi_N = (3/2) omega_m H^2 delta_N,
    displacement xi = -grad lap^-1 delta_N           (Zel'dovich approximation),
    velocity  dx/dt = H f xi  at a = 1 (conformal and cosmic time agree there),
    d psi_N / d ln a = (f - 1) psi_N                 (potential of the growing mode).
Dictionary (Chisari & Zaldarriaga; Green & Wald), as in make_east.py:
    rho / rho_m = 1 + delta_N - 2 psi_N - 2 d psi_N / d ln a,
    K = -3 H (1 - psi_N - d psi_N / d ln a),   alpha = sqrt(1 + 2 psi_N),
    conformal factor psi from the constraints for the particles (cosmo_id.solve).
Particles: lattice with lattice points on the cell corners (odd number per cell and
direction) displaced by xi(q); velocities of the growing mode; masses from the target
density at the particle with the Jacobian of the displacement. The Newtonian reference
uses the same positions and velocities.

build() returns the same tuple as make_east.build(); main() writes the same files.
"""
import argparse
import json
import os

import numpy as np

import cosmo_id as cid
from nrp_io import write_fields, write_particles


def spectral_fields(tor, delta, H, omega_m):
    """psi_N on the mesh, and the Fourier coefficients of lap^-1 delta."""
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    Fk = -tor.fft(delta)/k2
    Fk[0, 0, 0] = 0.0
    psiN = 1.5*omega_m*H*H*tor.ifft(Fk)
    return psiN, Fk


def shifted(tor, Fk, shift):
    """Inverse transform of Fk evaluated at the mesh points displaced by shift (three
    numbers): Fourier interpolation, exact for a band-limited field."""
    ph = np.exp(1j*(tor.k[0]*shift[0] + tor.k[1]*shift[1] + tor.k[2]*shift[2]))
    return tor.ifft(Fk*ph)


def lattice_fields(tor, Fk, ppc, stagger):
    """Lattice points q (npd^3, 3), displacement xi(q) and its Jacobian
    det(delta_ij + d_j xi_i) there. The lattice has ppc points per cell and direction;
    the fields are evaluated by Fourier interpolation on each of the ppc^3 sub-lattices."""
    n, L = tor.n, tor.L
    npd = n*ppc
    hq = L/npd
    off = 1.0 if stagger else 0.5
    q1 = (np.arange(npd) + off)*hq
    xi = np.empty((npd, npd, npd, 3))
    jac = np.empty((npd, npd, npd))
    kd = tor.kd
    xc0 = 0.5*tor.h                      # first cell centre
    for a in range(ppc):
        for b in range(ppc):
            for c in range(ppc):
                # points q = centre + shift, with q1[a + ppc*i] = (a + off) hq + i h
                sh = [(s + off)*hq - xc0 for s in (a, b, c)]
                d = [shifted(tor, -1j*kd[i]*Fk, sh) for i in range(3)]     # xi_i
                g = [[shifted(tor, kd[i]*kd[j]*Fk, sh) for j in range(3)] for i in range(3)]
                # d_j xi_i = -d_j d_i lap^-1 delta: Fourier factor (-i k_i)(i k_j) -> k_i k_j
                m00, m11, m22 = 1.0 + g[0][0], 1.0 + g[1][1], 1.0 + g[2][2]
                det = (m00*(m11*m22 - g[1][2]*g[2][1]) - g[0][1]*(g[1][0]*m22 - g[1][2]*g[2][0])
                       + g[0][2]*(g[1][0]*g[2][1] - m11*g[2][0]))
                for i in range(3):
                    xi[a::ppc, b::ppc, c::ppc, i] = d[i]
                jac[a::ppc, b::ppc, c::ppc] = det
    Q = np.meshgrid(q1, q1, q1, indexing="ij")
    q = np.stack([x.ravel() for x in Q], axis=1)
    return q, xi.reshape(-1, 3), jac.ravel(), q1


def newtonian_particles(delta, L, H=1.0, ppc=1, growth_rate=1.0, omega_m=1.0, stagger=None):
    """Positions, velocities dx/dt at a = 1, masses and lattice points of the Newtonian
    reference for the density field delta (as pm.east_particles for the sine waves)."""
    n = delta.shape[0]
    tor = cid.Torus(n, L)
    _, Fk = spectral_fields(tor, delta, H, omega_m)
    if stagger is None:
        stagger = (ppc % 2 == 1)
    q, xi, jac, _ = lattice_fields(tor, Fk, ppc, stagger)
    x = np.mod(q + xi, L)
    rho_m = omega_m*3.0*H*H/(8.0*np.pi)
    dN = cid.interp(delta, x, L)
    m = rho_m*(1.0 + dN)*jac*(L/(n*ppc))**3
    return x, H*growth_rate*xi, m, q


def build(delta, L, H=1.0, ppc=1, growth_rate=1.0, omega_m=1.0, nfilter=0,
          compensate=False, outer=18, verbose=True, stagger=None):
    """Relativistic data for the density field delta (n^3 array). Returns x, u, m, r, K,
    alpha, info, fid as make_east.build (fid: lattice points only)."""
    n = delta.shape[0]
    tor = cid.Torus(n, L)
    rho_m = omega_m*3.0*H*H/(8.0*np.pi)
    psiN_m, Fk = spectral_fields(tor, delta, H, omega_m)
    dpsi_m = (growth_rate - 1.0)*psiN_m                 # d psi_N / d ln a
    K = -3.0*H*(1.0 - psiN_m - dpsi_m)
    alpha = np.sqrt(1.0 + 2.0*psiN_m)
    psi_dict = (1.0 - 2.0*psiN_m)**0.25
    if stagger is None:
        stagger = (ppc % 2 == 1)
    q, xi, jac, q1 = lattice_fields(tor, Fk, ppc, stagger)
    hq = L/(n*ppc)
    x = np.mod(q + xi, L)
    v = H*growth_rate*xi
    dN_p = cid.interp(delta, x, L)
    psiN_p = cid.interp(psiN_m, x, L)
    rho_p = rho_m*(1.0 + dN_p - 2.0*psiN_p - 2.0*(growth_rate - 1.0)*psiN_p)
    alpha_p = np.sqrt(1.0 + 2.0*psiN_p)

    def particle_state(psi_at_p):
        v2 = psi_at_p**4*(v*v).sum(axis=1)/alpha_p**2
        W = 1.0/np.sqrt(1.0 - v2)
        u = (psi_at_p**4*W/alpha_p)[:, None]*v
        m = rho_p*W*psi_at_p**6*jac*hq**3
        return u, m, W

    tol = max(1e-11, 100.0*np.finfo(float).eps*(np.pi*n/L)**2)
    psi_p = (1.0 - 2.0*psiN_p)**0.25
    u, m, W = particle_state(psi_p)
    mtot = m.sum()
    psi = psi_dict.copy()
    d_prev, dpsi = None, np.nan
    for it in range(outer):
        r = cid.solve(tor, x, u, m, K, psi0=psi, nfilter=nfilter, compensate=compensate,
                      tol=tol, maxit=60)
        d_now = r["psi"] - psi
        dpsi = float(np.abs(d_now).max())
        psi = r["psi"]
        note = ""
        if d_prev is not None and it % 3 == 2:
            ratio = float((d_now*d_prev).sum()/(d_prev*d_prev).sum())
            if 0.0 < ratio < 0.95:
                psi = psi + d_now*ratio/(1.0 - ratio)
                note = f", extrapolated with ratio {ratio:.3f}"
                d_now = None
        d_prev = d_now
        psi_p = cid.interp(psi, x, L)
        u, m, W = particle_state(psi_p)
        m *= mtot/m.sum()
        if verbose:
            print(f"outer {it}: inner iterations {len(r['hist'])}, residual "
                  f"{r['hist'][-1]:.2e}, change of psi {dpsi:.2e}{note}", flush=True)
        if dpsi < 1e-9:
            break
    r = cid.solve(tor, x, u, m, K, psi0=psi, nfilter=nfilter, compensate=compensate,
                  tol=tol, maxit=60)
    ham, mom = cid.residuals(tor, r["psi"], K, r["A"], r["E"], r["S"])
    info = {
        "n": n, "ppc": ppc, "L": L, "H0": H, "rho_m": rho_m, "omega_m": omega_m,
        "growth_rate": growth_rate, "nfilter": nfilter, "compensate": compensate,
        "N": int(len(m)), "stagger": bool(stagger), "shape": cid.SHAPE,
        "delta_rms": float(delta.std()), "delta_max": float(np.abs(delta).max()),
        "max_displacement_over_h": float(np.abs(xi).max()/tor.h),
        "jacobian_min": float(jac.min()),
        "total_rest_mass": float(m.sum()), "rho_m_L3": rho_m*L**3,
        "mass_min_over_mean": float(m.min()/m.mean()),
        "mass_max_over_mean": float(m.max()/m.mean()),
        "max_velocity": float(np.sqrt((v*v).sum(axis=1)).max()),
        "max_abs_psiN": float(np.abs(psiN_m).max()),
        "max_psi_minus_dictionary": float(np.abs(r["psi"] - psi_dict).max()),
        "max_abs_Ahat": float(max(np.abs(a).max() for a in r["A"])),
        "max_hamiltonian_residual": float(np.abs(ham).max()),
        "max_momentum_residual": float(max(np.abs(v_).max() for v_ in mom)),
        "removed_momentum_source_mean": r["rmean"],
        "outer_last_change_of_psi": dpsi,
    }
    fid = {"q": q[:0], "axis": np.zeros(0, int), "q_centre": q1[0]}
    return x, u, m, r, K, alpha, info, fid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta-file", required=True,
                    help=".npy file with delta_N on the mesh, shape (n, n, n)")
    ap.add_argument("--L", type=float, required=True, help="box size in code units")
    ap.add_argument("--H0", type=float, default=1.0)
    ap.add_argument("--ppc", type=int, default=1)
    ap.add_argument("--growth-rate", type=float, default=1.0)
    ap.add_argument("--omega-m", type=float, default=1.0)
    ap.add_argument("--nfilter", type=int, default=0)
    ap.add_argument("--compensate", action="store_true")
    ap.add_argument("--shape", default="cic", choices=("cic", "tsc", "pcs"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cid.SHAPE = a.shape
    delta = np.load(a.delta_file)
    x, u, m, r, K, alpha, info, fid = build(delta, a.L, a.H0, a.ppc, a.growth_rate,
                                            a.omega_m, a.nfilter, a.compensate)
    os.makedirs(a.out, exist_ok=True)
    write_particles(os.path.join(a.out, "particles.nrp"), x, u, m)
    write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    for key in ("N", "delta_rms", "delta_max", "max_displacement_over_h", "jacobian_min",
                "mass_min_over_mean", "mass_max_over_mean", "max_velocity", "max_abs_psiN",
                "max_psi_minus_dictionary", "max_abs_Ahat", "max_hamiltonian_residual",
                "max_momentum_residual", "outer_last_change_of_psi"):
        print(f"{key}: {info[key]}")
