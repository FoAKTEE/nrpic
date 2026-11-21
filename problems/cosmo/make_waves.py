#!/usr/bin/env python3
"""Initial data of East, Wojtak & Pretorius (arXiv:1908.05683) for the NRPIC code on a
box of n1 x n2 x n3 cubic cells: one sine wave per direction, constraint-solved for the
particles of the run. The construction of `cosmo/ic/make_east.py` (which is restricted
to a cube), with two additions asked for by Track B: boxes that are thin in a direction
the waves do not depend on, and a random displacement of the particle lattice.

    python3 problems/cosmo/make_waves.py --delta 0.01 --n 256,256,16 --ratios 1,0.3,0 \
        --ppc 2 --shape pcs --dep-comp-c 0.16666666666666666 \
        --dep-comp-c2 0.4666666666666667 --out DIR
    python3 problems/cosmo/make_waves.py --delta 0.01 --n 64 --ratios 1,0,0 \
        --jitter 0.3 --jitter-axes y,z --seed 7 --out DIR

Box: [0, L) x [0, L n2/n1) x [0, L n3/n1), cells of side h = L/n1 (--L is the length of
the first direction). Newtonian input at a = 1, H = H0, per direction i with wave number
k_i = 2 pi / L_i:

    delta_N = sum_i d_i sin(k_i x_i),   d = delta * ratios,
    v^i     = H d_i cos(k_i x_i) / k_i                    (Zel'dovich, growing mode),
    psi_N   = -(3/2) sum_i (H/k_i)^2 d_i sin(k_i x_i)     (lap psi_N = 4 pi rho_0 delta_N).

Dictionary (as in make_east.py): rho = rho_0 [1 + sum_i (1 + 3 (H/k_i)^2) d_i sin],
K = -3 H (1 - psi_N), alpha = sqrt(1 + 2 psi_N), u_i = psi^4 W v^i / alpha. Particles: a
lattice aligned with the mesh (--ppc per cell and direction; shifted by half a spacing
for odd ppc), displaced by xi_i = d_i cos(k_i q_i)/k_i; the masses carry the rest of the
density with the exact Jacobian. The conformal factor and the traceless extrinsic
curvature follow from the constraints for these particles (nrpic.torus_id.solve), with
the cloud, compensation and filter of the run. With --fd-order 6 the constraints are
solved with the sixth-order differences of the code (nghost = 4) instead of spectral
derivatives: the Hamiltonian constraint as the code evaluates it then holds to the
tolerance of the solve also for a noisy lattice (see nrpic/torus_id.py).

Jitter (--jitter A --jitter-axes y,z --seed N): after the displacement every particle is
moved by A h (2 u - 1) along each named axis, u uniform in (0, 1), before the constraint
solve. The deviates come from the counter-based generator of the code (nrpic.rng):
seed = N, stream = initial data with sub-stream 16, entity = lattice site (its three
indices), step 0, draw = axis. They depend on nothing else: the same site gets the same
displacement in any box and in any order of the particles. Meant for axes along which the
wave amplitudes vanish: the exact solution then keeps its symmetry and the run measures
what the noise of the particle lattice alone does.

Writes DIR/particles.nrp, DIR/fields.bin (NRCOSMO1, n1 x n2 x n3), DIR/fiducial.npz
(with `site`: the lattice indices of every particle in the order of the file) and
DIR/id.json (all arguments, the box with all digits, the residuals). The fiducial
observers (lattice lines through the site nearest to the overdensity peak) come first in
the particle file, x line first. Light rays (make_east.py --rays) are not written.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                "python"))
from nrpic import rng, torus_id as tid  # noqa: E402
from nrpic.io import write_nrp  # noqa: E402

JITTER_SUBSTREAM = 16   # sub-stream of STREAM_INITIAL_DATA (tracks/core/interfaces/rng.md)
AXES = {"x": 0, "y": 1, "z": 2}


def write_fields(path, psi, trk, alpha, ahat=None):
    """NRCOSMO1 field file read by the problem generator nrpic_cosmo (id = file). Arrays
    have shape (n1, n2, n3) indexed [i, j, k]; ahat: the six components xx, xy, xz, yy,
    yz, zz, or None (zero)."""
    psi = np.asarray(psi, dtype=np.float64)
    if ahat is None:
        ahat = [np.zeros_like(psi)]*6
    with open(path, "wb") as f:
        f.write(b"NRCOSMO1")
        f.write(np.array(psi.shape, dtype="<i8").tobytes())
        for a in [psi, trk, alpha] + list(ahat):
            # the code reads the first index fastest: Fortran order of [i, j, k]
            f.write(np.asarray(a, dtype="<f8").ravel(order="F").tobytes())


def jitter_offsets(site, amp_cells, axes, seed, h):
    """Displacements (N, 3) of the lattice sites `site` (N, 3 integer indices)."""
    out = np.zeros(site.shape, dtype=float)
    if amp_cells == 0.0:
        return out
    ent = rng.cell_entity(site[:, 0], site[:, 1], site[:, 2])
    st = rng.stream(rng.STREAM_INITIAL_DATA, JITTER_SUBSTREAM)
    for ax in axes:
        u = rng.uniform(seed=seed, stream=st, entity=ent, step=0, draw=ax)
        out[:, ax] = amp_cells*h*(2.0*u - 1.0)
    return out


def build(delta, n, ppc=1, L=4.0, H=1.0, ratios=(1.0, 0.9, 1.1), dep=None,
          zero_velocity=False, outer=18, verbose=True, stagger=None,
          displacement="newtonian", jitter=0.0, jitter_axes=(), seed=1, fd_order=None):
    dep = tid.Deposit() if dep is None else dep
    n = (n,)*3 if np.isscalar(n) else tuple(int(v) for v in n)
    h = L/n[0]
    Lb = tuple(n[i]*h for i in range(3))
    k = [2.0*np.pi/Lb[i] for i in range(3)]
    rho0 = 3.0*H*H/(8.0*np.pi)
    d = [delta*r for r in ratios]
    hk2 = [(H/k[i])**2 for i in range(3)]
    tor = tid.Torus(n, Lb, fd_order)

    def newtonian_fields(x, y, z):
        """delta_N, psi_N, the density contrast of the dictionary and the velocity."""
        c3 = (x, y, z)
        s = [np.sin(k[i]*c3[i]) for i in range(3)]
        c = [np.cos(k[i]*c3[i]) for i in range(3)]
        dN = d[0]*s[0] + d[1]*s[1] + d[2]*s[2]
        psiN = -1.5*(hk2[0]*d[0]*s[0] + hk2[1]*d[1]*s[1] + hk2[2]*d[2]*s[2])
        dR = ((1.0 + 3.0*hk2[0])*d[0]*s[0] + (1.0 + 3.0*hk2[1])*d[1]*s[1]
              + (1.0 + 3.0*hk2[2])*d[2]*s[2])
        v = [H*d[i]*c[i]/k[i] for i in range(3)]
        return dN, psiN, dR, v

    # mesh fields of the dictionary
    xc = [(np.arange(n[i]) + 0.5)*h for i in range(3)]
    X, Y, Z = np.meshgrid(xc[0], xc[1], xc[2], indexing="ij")
    dN_m, psiN_m, _, _ = newtonian_fields(X, Y, Z)
    K = -3.0*H*(1.0 - psiN_m)
    alpha = np.sqrt(1.0 + 2.0*psiN_m)
    psi_dict = (1.0 - 2.0*psiN_m)**0.25

    # lattice and displacement (comments on the stagger and on the two displacements:
    # cosmo/ic/make_east.py)
    npd = [n[i]*ppc for i in range(3)]
    hq = L/npd[0]
    if stagger is None:
        stagger = (ppc % 2 == 1)
    q1 = [(np.arange(npd[i]) + (1.0 if stagger else 0.5))*hq for i in range(3)]
    Q = np.meshgrid(q1[0], q1[1], q1[2], indexing="ij")
    q = np.stack([a.ravel() for a in Q], axis=1)
    site = np.stack([a.ravel() for a in np.meshgrid(np.arange(npd[0]), np.arange(npd[1]),
                                                    np.arange(npd[2]), indexing="ij")],
                    axis=1)
    if displacement == "newtonian":
        cz = [1.0, 1.0, 1.0]
    else:
        cz = [1.0 + (4.5 if zero_velocity else 7.5)*hk2[i] for i in range(3)]
    xi = np.stack([cz[i]*d[i]*np.cos(k[i]*q[:, i])/k[i] for i in range(3)], axis=1)
    jac = np.prod(1.0 - np.stack([cz[i]*d[i]*np.sin(k[i]*q[:, i]) for i in range(3)],
                                 axis=1), axis=1)
    jit = jitter_offsets(site, jitter, jitter_axes, seed, h)
    if jitter != 0.0:
        x = np.mod(q + xi + jit, np.array(Lb))
    else:
        x = np.mod(q + xi, np.array(Lb))

    # fiducial observers first: the lattice lines through the site nearest to the
    # overdensity peak, x line first
    ic = [int(np.argmin(np.abs(q1[i] - 0.25*Lb[i]))) for i in range(3)]
    on = [(site[:, 1] == ic[1]) & (site[:, 2] == ic[2]),
          (site[:, 0] == ic[0]) & (site[:, 2] == ic[2]),
          (site[:, 0] == ic[0]) & (site[:, 1] == ic[1])]
    centre = on[0] & on[1]
    first = np.concatenate([np.flatnonzero(on[0]), np.flatnonzero(on[1] & ~centre),
                            np.flatnonzero(on[2] & ~centre)])
    rest = np.ones(len(q), dtype=bool)
    rest[first] = False
    order = np.concatenate([first, np.flatnonzero(rest)])
    q, xi, jac, x, site, jit = q[order], xi[order], jac[order], x[order], site[order], \
        jit[order]
    nfid = len(first)
    fid_axis = np.concatenate([np.zeros(npd[0], int), np.ones(npd[1] - 1, int),
                               np.full(npd[2] - 1, 2)])

    # target density and velocity at the particles
    dN_p, psiN_p, dR_p, v_p = newtonian_fields(x[:, 0], x[:, 1], x[:, 2])
    if zero_velocity:
        rho_p = rho0*(1.0 + dN_p)
        v = np.zeros_like(x)
    else:
        rho_p = rho0*(1.0 + dR_p)
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
    tol = max(1e-11, 100.0*np.finfo(float).eps*(np.pi/h)**2)
    psi = psi_dict.copy()
    # outer iteration (masses from the solved psi, psi from the masses) with Aitken
    # extrapolation every third step, as in make_east.py
    d_prev = None
    dpsi = 0.0
    for it in range(outer):
        r = tid.solve(tor, x, u, m, K, dep, psi0=psi, tol=tol, maxit=60)
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
        psi_p = tid.interp(psi, x, Lb)
        u, m, W = particle_state(psi_p)
        m *= mtot/m.sum()
        if verbose:
            print(f"outer {it}: inner iterations {len(r['hist'])}, residual "
                  f"{r['hist'][-1]:.2e}, change of psi {dpsi:.2e}{note}", flush=True)
        if dpsi < 1e-9:
            break
    r = tid.solve(tor, x, u, m, K, dep, psi0=psi, tol=tol, maxit=60)
    ham, mom = tid.residuals(tor, r["psi"], K, r["A"], r["E"], r["S"])
    ham_scale = float(np.abs(2.0*np.pi*r["psi"]**5*r["E"]).max())
    info = {
        "tool": "problems/cosmo/make_waves.py",
        "delta": delta, "ratios": list(ratios), "n": list(n), "ppc": ppc, "L": L,
        "box": list(Lb), "h": h, "H0": H, "k": k, "rho0": rho0,
        "nfilter": dep.nfilter, "compensate": dep.compensate, "shape": dep.shape,
        "dep_comp_c": dep.dep_comp_c, "dep_comp_c2": dep.dep_comp_c2,
        "zero_velocity": zero_velocity, "N": int(len(m)), "stagger": bool(stagger),
        "displacement": displacement, "displacement_factor": cz,
        "jitter": jitter, "jitter_axes": [("x", "y", "z")[a] for a in jitter_axes],
        "seed": seed, "jitter_substream": JITTER_SUBSTREAM, "fd_order": fd_order,
        "dropped_momentum_source_modes": r["rdrop"],
        "max_jitter_over_h": float(np.abs(jit).max()/h),
        "max_displacement_over_h": float(np.abs(xi).max()/h),
        "total_rest_mass": float(m.sum()), "rho0_volume": rho0*Lb[0]*Lb[1]*Lb[2],
        "mass_min_over_mean": float(m.min()/m.mean()),
        "mass_max_over_mean": float(m.max()/m.mean()),
        "max_velocity": float(np.sqrt((v*v).sum(axis=1)).max()),
        "max_abs_psiN": float(np.abs(psiN_m).max()),
        "max_psi_minus_dictionary": float(np.abs(r["psi"] - psi_dict).max()),
        "mean_psi6": float((r["psi"]**6).mean()),
        "max_abs_Ahat": float(max(np.abs(a).max() for a in r["A"])),
        "max_hamiltonian_residual": float(np.abs(ham).max()),
        "max_hamiltonian_term": ham_scale,
        "max_momentum_residual": float(max(np.abs(v_).max() for v_ in mom)),
        "removed_momentum_source_mean": r["rmean"],
        "outer_last_change_of_psi": dpsi,
        "overdensity_point": [0.25*Lb[i] for i in range(3)],
        "underdensity_point": [0.75*Lb[i] for i in range(3)],
        "n_fiducial": int(nfid),
    }
    fid = {"q": q[:nfid], "axis": fid_axis, "q_centre": np.array([q1[i][ic[i]]
                                                                  for i in range(3)]),
           "site": site.astype(np.int32)}
    return x, u, m, r, K, alpha, info, fid


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--delta", type=float, required=True)
    ap.add_argument("--n", default="64", help="cells: one number (cube) or n1,n2,n3")
    ap.add_argument("--ppc", type=int, default=1, help="particles per cell and direction")
    ap.add_argument("--L", type=float, default=4.0, help="length of the first direction")
    ap.add_argument("--H0", type=float, default=1.0)
    ap.add_argument("--ratios", default="1,0.9,1.1",
                    help="amplitudes of the three directions over delta")
    ap.add_argument("--nfilter", type=int, default=0)
    ap.add_argument("--compensate", action="store_true")
    ap.add_argument("--zero-velocity", action="store_true")
    ap.add_argument("--no-stagger", action="store_true")
    ap.add_argument("--displacement", default="newtonian", choices=("newtonian", "number"))
    ap.add_argument("--shape", default="cic", choices=("cic", "tsc", "pcs"),
                    help="cloud of the deposit of the run (<particles> deposit_shape)")
    ap.add_argument("--dep-comp-c", type=float, default=0.0, help="deposit_comp_c")
    ap.add_argument("--dep-comp-c2", type=float, default=0.0, help="deposit_comp_c2")
    ap.add_argument("--jitter", type=float, default=0.0,
                    help="random displacement of every particle, in cells (uniform in "
                         "(-A, A)) along --jitter-axes")
    ap.add_argument("--jitter-axes", default="y,z")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--fd-order", type=int, default=0, choices=(0, 2, 4, 6),
                    help="solve the constraints with the centred differences of the code "
                         "of this order (6 for nghost = 4) instead of spectral "
                         "derivatives; recommended with --jitter")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    n = [int(v) for v in a.n.split(",")]
    n = n*3 if len(n) == 1 else n
    if len(n) != 3:
        ap.error("--n takes one or three numbers")
    ratios = tuple(float(v) for v in a.ratios.split(","))
    axes = tuple(AXES[s] for s in a.jitter_axes.split(",") if s) if a.jitter != 0.0 else ()
    for ax in axes:
        if ratios[ax] != 0.0:
            print(f"warning: jitter along an axis with a wave (ratio {ratios[ax]}): the "
                  "data no longer have the symmetry of the exact solution", flush=True)
    dep = tid.Deposit(shape=a.shape, dep_comp_c=a.dep_comp_c, dep_comp_c2=a.dep_comp_c2,
                      nfilter=a.nfilter, compensate=a.compensate)
    x, u, m, r, K, alpha, info, fid = build(
        a.delta, n, a.ppc, a.L, a.H0, ratios=ratios, dep=dep,
        zero_velocity=a.zero_velocity, stagger=(False if a.no_stagger else None),
        displacement=a.displacement, jitter=a.jitter, jitter_axes=axes, seed=a.seed,
        fd_order=(a.fd_order or None), verbose=not a.quiet)
    os.makedirs(a.out, exist_ok=True)
    write_nrp(os.path.join(a.out, "particles.nrp"), x, u, m)
    write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
    np.savez(os.path.join(a.out, "fiducial.npz"), **fid)
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    for key in ("N", "n", "box", "n_fiducial", "jitter", "max_displacement_over_h",
                "mass_min_over_mean", "mass_max_over_mean", "max_velocity",
                "max_psi_minus_dictionary", "max_abs_Ahat", "max_hamiltonian_residual",
                "max_hamiltonian_term", "max_momentum_residual"):
        print(f"{key}: {info[key]}")


if __name__ == "__main__":
    main()
