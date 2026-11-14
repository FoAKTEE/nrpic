"""Initial data of East, Wojtak & Pretorius (arXiv:1908.05683) for the NRPIC code.

    python3 make_east.py --delta 0.01 --n 64 --ppc 1 --out DIR [--nfilter 0]

Newtonian input (arXiv:1711.06681, Sec. III A; a = 1, H = H0, k = 2 pi / L = pi H0 / 2):

    delta_N = sum_i d_i sin(k x_i),   d = delta (1, 0.9, 1.1),
    v^i     = H d_i cos(k x_i) / k                      (Zel'dovich, growing mode),
    psi_N   = -(3/2) (H/k)^2 delta_N                    (lap psi_N = 4 pi rho_0 delta_N).

Dictionary (Chisari & Zaldarriaga; Green & Wald):

    ds^2 = -(1 + 2 psi_N) dt^2 + (1 - 2 psi_N) dx^2,
    rho  = rho_0 [1 + (1 + 3 (H/k)^2) delta_N],     K = -3 H (1 - psi_N),
    alpha = sqrt(1 + 2 psi_N),    u^a = u^t (1, v^i).

Particles: a lattice aligned with the mesh, displaced by xi_i = c d_i cos(k q_i)/k. With
c = 1 (default) the positions are those of the Newtonian reference; with
c = 1 + (15/2) (H/k)^2 (--displacement number) the coordinate number density has the
contrast delta_N - 5 psi_N of rho W psi^6 to linear order. The masses carry the rest of
the density in either case, with the exact Jacobian of the displacement. The conformal factor and the traceless extrinsic
curvature then follow from the constraints for these particles (cosmo_id.solve). The
momenta u_i = psi^4 W v^i / alpha use the solved psi; the masses are set from the target
density with the solved psi, at fixed total rest mass (the density then has the target
shape; its normalization is fixed by the Hamiltonian constraint).

Writes DIR/particles.nrp, DIR/fields.bin, DIR/id.json. Coordinates: box [0, L)^3; the
overdensity peak is at x_i = L/4, the underdensity at x_i = 3L/4.
"""
import argparse
import json
import os

import numpy as np

import cosmo_id as cid
import ray_ic as ry
from nrp_io import write_fields, write_particles


def newtonian_fields(x, y, z, k, H, d):
    """delta_N, psi_N and the three velocity components at the given points."""
    s = [np.sin(k*x), np.sin(k*y), np.sin(k*z)]
    c = [np.cos(k*x), np.cos(k*y), np.cos(k*z)]
    dN = d[0]*s[0] + d[1]*s[1] + d[2]*s[2]
    psiN = -1.5*(H/k)**2*dN
    v = [H*d[i]*c[i]/k for i in range(3)]
    return dN, psiN, v


def build(delta, n, ppc=1, L=4.0, H=1.0, ratios=(1.0, 0.9, 1.1), nfilter=0,
          compensate=False, zero_velocity=False, outer=18, verbose=True, stagger=None,
          displacement="newtonian"):
    k = 2.0*np.pi/L
    rho0 = 3.0*H*H/(8.0*np.pi)
    d = [delta*r for r in ratios]
    hk2 = (H/k)**2
    tor = cid.Torus(n, L)
    h = L/n

    # mesh fields of the dictionary
    xc = (np.arange(n) + 0.5)*h
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    dN_m, psiN_m, _ = newtonian_fields(X, Y, Z, k, H, d)
    K = -3.0*H*(1.0 - psiN_m)
    alpha = np.sqrt(1.0 + 2.0*psiN_m)
    psi_dict = (1.0 - 2.0*psiN_m)**0.25

    # lattice and displacement
    npd = n*ppc
    hq = L/npd
    # A particle at a cell centre sits on the cusp of the cloud-in-cell weight: where
    # the displacement changes sign (density peak and trough) the two neighbours leak
    # into each other's cells and the deposited contrast is half again too large there.
    # With an odd number of particles per cell and direction the lattice is therefore
    # shifted by half a particle spacing (one per cell: particles at the cell corners,
    # each shared equally by eight cells); the deposit of the undisplaced lattice stays
    # exactly uniform and its response to a displacement below half a cell is linear.
    if stagger is None:
        stagger = (ppc % 2 == 1)
    q1 = (np.arange(npd) + (1.0 if stagger else 0.5))*hq
    Q = np.meshgrid(q1, q1, q1, indexing="ij")
    q = np.stack([a.ravel() for a in Q], axis=1)
    # displacement = "number": the lattice carries the whole coordinate density
    # contrast (delta_N - 5 psi_N with growing-mode velocities, delta_N - 3 psi_N with
    # zero velocity) and the masses are nearly equal. displacement = "newtonian": the
    # positions of the Newtonian reference, and the masses carry the rest. The second
    # is the default: for cold matter only the density and velocity fields matter, and
    # the deposit error of a compressed lattice grows with the square of the
    # compression (cosmo/TESTLOG.md, C2 first runs), so the two calculations should
    # start from the same positions.
    if displacement == "newtonian":
        cz = 1.0
    else:
        cz = 1.0 + (4.5 if zero_velocity else 7.5)*hk2
    xi = np.stack([cz*d[i]*np.cos(k*q[:, i])/k for i in range(3)], axis=1)
    jac = np.prod(1.0 - cz*np.stack([d[i]*np.sin(k*q[:, i]) for i in range(3)], axis=1),
                  axis=1)
    x = np.mod(q + xi, L)

    # Fiducial observers come first in the file (the code records the trajectories of
    # the particles with the lowest tags): the lattice particles on the three lines
    # through the lattice point nearest to the overdensity peak, x line first.
    ic = int(np.argmin(np.abs(q1 - 0.25*L)))
    I = [a.ravel() for a in np.meshgrid(np.arange(npd), np.arange(npd), np.arange(npd),
                                        indexing="ij")]
    on = [(I[1] == ic) & (I[2] == ic), (I[0] == ic) & (I[2] == ic),
          (I[0] == ic) & (I[1] == ic)]
    centre = on[0] & on[1]
    first = np.concatenate([np.flatnonzero(on[0]), np.flatnonzero(on[1] & ~centre),
                            np.flatnonzero(on[2] & ~centre)])
    rest = np.ones(len(q), dtype=bool)
    rest[first] = False
    order = np.concatenate([first, np.flatnonzero(rest)])
    q, xi, jac, x = q[order], xi[order], jac[order], x[order]
    nfid = len(first)
    fid_axis = np.concatenate([np.zeros(npd, int), np.ones(npd - 1, int),
                               np.full(npd - 1, 2)])

    # target density and velocity at the particles
    dN_p, psiN_p, v_p = newtonian_fields(x[:, 0], x[:, 1], x[:, 2], k, H, d)
    if zero_velocity:
        rho_p = rho0*(1.0 + dN_p)
        v = np.zeros_like(x)
    else:
        rho_p = rho0*(1.0 + (1.0 + 3.0*hk2)*dN_p)
        v = np.stack(v_p, axis=1)
    alpha_p = np.sqrt(1.0 + 2.0*psiN_p)

    def particle_state(psi_at_p):
        v2 = psi_at_p**4*(v*v).sum(axis=1)/alpha_p**2
        W = 1.0/np.sqrt(1.0 - v2)
        u = (psi_at_p**4*W/alpha_p)[:, None]*v
        m = rho_p*W*psi_at_p**6*jac*hq**3
        return u, m, W

    psi_p = (1.0 - 2.0*psiN_p)**0.25
    u, m, W = particle_state(psi_p)
    mtot = m.sum()
    # tolerance of the constraint solve: not below the rounding error of the Laplacian
    # at the mesh spacing
    tol = max(1e-11, 100.0*np.finfo(float).eps*(np.pi*n/L)**2)
    psi = psi_dict.copy()
    # The outer iteration (masses from the solved psi, psi from the masses) converges
    # geometrically, slowly for long wavelengths: the problem with the density held
    # fixed is marginal. Its error is dominated by one mode, so every third iteration
    # the limit is extrapolated from the last two changes (Aitken).
    d_prev = None
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
        "delta": delta, "ratios": list(ratios), "n": n, "ppc": ppc, "L": L, "H0": H,
        "k": k, "rho0": rho0, "nfilter": nfilter, "compensate": compensate,
        "zero_velocity": zero_velocity, "N": int(len(m)), "stagger": bool(stagger),
        "displacement": displacement,
        "displacement_factor": cz, "max_displacement_over_h": float(np.abs(xi).max()/h),
        "total_rest_mass": float(m.sum()), "rho0_L3": rho0*L**3,
        "mass_min_over_mean": float(m.min()/m.mean()),
        "mass_max_over_mean": float(m.max()/m.mean()),
        "max_velocity": float(np.sqrt((v*v).sum(axis=1)).max()),
        "max_abs_psiN": float(np.abs(psiN_m).max()),
        "max_psi_minus_dictionary": float(np.abs(r["psi"] - psi_dict).max()),
        "mean_psi6": float((r["psi"]**6).mean()),
        "max_abs_Ahat": float(max(np.abs(a).max() for a in r["A"])),
        "max_hamiltonian_residual": float(np.abs(ham).max()),
        "max_momentum_residual": float(max(np.abs(v_).max() for v_ in mom)),
        "removed_momentum_source_mean": r["rmean"],
        "outer_last_change_of_psi": dpsi,
        "overdensity_point": [L/4]*3, "underdensity_point": [3*L/4]*3,
        "n_fiducial": int(nfid),
    }
    fid = {"q": q[:nfid], "axis": fid_axis, "q_centre": q1[ic]}
    return x, u, m, r, K, alpha, info, fid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=float, required=True)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--ppc", type=int, default=1)
    ap.add_argument("--L", type=float, default=4.0)
    ap.add_argument("--H0", type=float, default=1.0)
    ap.add_argument("--nfilter", type=int, default=0)
    ap.add_argument("--compensate", action="store_true")
    ap.add_argument("--zero-velocity", action="store_true")
    ap.add_argument("--no-stagger", action="store_true",
                    help="keep particles at cell centres for odd ppc (shows the cusp)")
    ap.add_argument("--ratios", default="1,0.9,1.1",
                    help="amplitudes of the three directions over delta (1,0,0: plane wave)")
    ap.add_argument("--displacement", default="newtonian", choices=("newtonian", "number"))
    ap.add_argument("--shape", default="cic", choices=("cic", "tsc", "pcs"),
                    help="cloud shape of the deposit of the run (<particles> deposit_shape)")
    ap.add_argument("--rays", default="",
                    help="comma-separated scale factors of the homogeneous solution at "
                         "which light rays leave the two extrema")
    ap.add_argument("--cfl", type=float, default=0.25,
                    help="time step over cell size of the run (emission times are "
                         "rounded to steps)")
    ap.add_argument("--ray-eps", type=float, default=1e-4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cid.SHAPE = a.shape
    x, u, m, r, K, alpha, info, fid = build(a.delta, a.n, a.ppc, a.L, a.H0,
                                            ratios=tuple(float(v) for v in
                                                         a.ratios.split(",")),
                                            nfilter=a.nfilter,
                                            compensate=a.compensate,
                                            zero_velocity=a.zero_velocity,
                                            stagger=(False if a.no_stagger else None),
                                            displacement=a.displacement)
    os.makedirs(a.out, exist_ok=True)
    info["shape"] = a.shape
    if a.rays:
        # the rays follow the fiducial observers in the file, so that the code records
        # both (tags below traj_ntrack = n_fiducial + n_rays)
        dt = a.cfl*a.L/a.n
        a_emit = [float(v) for v in a.rays.split(",")]
        t_emit = [dt*round(2.0*(np.sqrt(v) - 1.0)/a.H0/dt) for v in a_emit]
        xr, cr, mr, meta = ry.bundles(t_emit, a.L, a.ray_eps)
        nf = info["n_fiducial"]
        x = np.concatenate([x[:nf], xr, x[nf:]])
        u = np.concatenate([u[:nf], cr, u[nf:]])
        m = np.concatenate([m[:nf], mr, m[nf:]])
        meta["tag"] = nf + np.arange(len(mr))
        np.savez(os.path.join(a.out, "rays.npz"), **meta)
        info["n_rays"] = int(len(mr))
        info["ray_t_emit"] = t_emit
        info["traj_ntrack"] = int(nf + len(mr))
    write_particles(os.path.join(a.out, "particles.nrp"), x, u, m)
    write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
    np.savez(os.path.join(a.out, "fiducial.npz"), **fid)
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    for key in ("traj_ntrack", "ray_t_emit"):
        if key in info:
            print(f"{key}: {info[key]}")
    for key in ("N", "n_fiducial", "max_displacement_over_h", "mass_min_over_mean", "mass_max_over_mean",
                "max_velocity", "max_abs_psiN", "max_psi_minus_dictionary", "mean_psi6",
                "max_abs_Ahat", "max_hamiltonian_residual", "max_momentum_residual"):
        print(f"{key}: {info[key]}")
