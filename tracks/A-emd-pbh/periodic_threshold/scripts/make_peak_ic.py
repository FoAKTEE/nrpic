"""Single curvature peak of arXiv:2609.14218 in a periodic box, built with the
repository's own tool cosmo/ic/make_field.py (JOURNAL.md T1; DESIGN.md section 1).

    python3 make_peak_ic.py --mu 0.5 --e 0.2 [--p 0] --eps-i 1 --n 64 --out DIR
                            [--boxk 20] [--ppc 1] [--shape cic] [--nfilter 2 --compensate]

Units of cosmo/README.md: G = c = 1, a_i = 1, H_i = 1; k = eps_i = k/(a_i H_i).
Profile (MDPBH.tex:839): zeta = 2 ln Psi = mu exp(-k^2 r^2/6) [1 + (k^2/6)(p(2X^2 - Y^2 - Z^2)
+ 3e(Y^2 - Z^2))], peak at the box centre. Linear growing mode in the matter era
[BACKGROUND]: psi_N = -(3/5) zeta, delta_N = (2/3) lap(psi_N)/(a H)^2 = -(2/5) lap(zeta);
make_field.build(delta_N) then makes the Zel'dovich lattice, the Newtonian-gauge
dictionary and the nonlinear constraint solve for the particles, unchanged.

The particles are shifted by -L/2 so that the mesh is [-L/2, L/2)^3 with the peak at the
origin (the field file is indexed by cell and needs no change).

Also evaluated on the same mesh, for comparison only (not written to the field file): the
gradient-expansion data of the paper on its constant-mean-curvature slice
(MDPBH.tex:515-543): q, p_ij, the non-conformally-flat part (4/5) p_ij/(aH)^2 of the
conformal metric that the file format NRCOSMO1 cannot carry, and the transverse-traceless
fraction of p_ij (absent from the conformally flat solve, whose Ahat is longitudinal).
"""
import argparse
import json
import os
import sys

import numpy as np

REPO = "/data/haiyangw/nrpic/wt/A-emd-pbh"
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
import cosmo_id as cid          # noqa: E402
import make_field as mf         # noqa: E402
from nrp_io import write_fields, write_particles   # noqa: E402


def zeta_field(n, L, k, mu, e, p):
    h = L/n
    xc = (np.arange(n) + 0.5)*h - 0.5*L
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    r2 = X*X + Y*Y + Z*Z
    ang = 1.0 + (k*k/6.0)*(p*(2*X*X - Y*Y - Z*Z) + 3*e*(Y*Y - Z*Z))
    return mu*np.exp(-k*k*r2/6.0)*ang


def ge_diagnostics(tor, zeta, aH=1.0):
    """Gradient-expansion quantities of MDPBH.tex:515-543 on the torus (flat f_ij)."""
    Psi = np.exp(0.5*zeta)
    F = tor.fft(Psi)
    kd = tor.kd
    d1 = [tor.ifft(1j*kk*F) for kk in kd]
    d2 = {}
    for a in range(3):
        for b in range(a, 3):
            d2[(a, b)] = tor.ifft(-kd[a]*kd[b]*F)
    lap = d2[(0, 0)] + d2[(1, 1)] + d2[(2, 2)]
    grad2 = d1[0]**2 + d1[1]**2 + d1[2]**2
    q = -(4.0/3.0)*lap/Psi**5
    pij = {}
    for a in range(3):
        for b in range(a, 3):
            dab = 1.0 if a == b else 0.0
            pij[(a, b)] = Psi**-4*(-(2.0/Psi)*(d2[(a, b)] - dab*lap/3.0)
                                   + (6.0/Psi**2)*(d1[a]*d1[b] - dab*grad2/3.0))
    pmax = max(float(np.abs(v).max()) for v in pij.values())
    # transverse-traceless part of p_ij
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    P = {}
    for a in range(3):
        for b in range(3):
            P[(a, b)] = (1.0 if a == b else 0.0) - kd[a]*kd[b]/k2

    def comp(a, b):
        return pij[(min(a, b), max(a, b))]
    Pk = {(a, b): tor.fft(comp(a, b)) for a in range(3) for b in range(3)}
    tt_norm2, all_norm2 = 0.0, 0.0
    for i in range(3):
        for j in range(3):
            acc = 0.0
            for kk_ in range(3):
                for ll in range(3):
                    lam = P[(i, kk_)]*P[(j, ll)] - 0.5*P[(i, j)]*P[(kk_, ll)]
                    acc = acc + lam*Pk[(kk_, ll)]
            tt = tor.ifft(acc)
            tt_norm2 += float((tt*tt).sum())
            all_norm2 += float((comp(i, j)**2).sum())
    return {
        "Psi_max": float(Psi.max()),
        "q_centre_max": float(q.max()),
        "delta_cmc_max_at_start": float(q.max()/aH**2),
        "max_abs_gamma_tilde_minus_delta": 0.8*pmax/aH**2,
        "max_abs_A_tilde": 0.4*pmax/aH**2,
        "tt_fraction_of_p_ij_L2": float(np.sqrt(tt_norm2/max(all_norm2, 1e-300))),
        "psi_ge_minus_Psi_max": float(np.abs(Psi*q/(6.0*aH**2)).max()),
        "alpha_ge_min": float((1.0 - q/(3.0*aH**2)).min()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mu", type=float, required=True)
    ap.add_argument("--e", type=float, default=0.0)
    ap.add_argument("--p", type=float, default=0.0)
    ap.add_argument("--eps-i", type=float, default=1.0, help="k/(a_i H_i)")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--boxk", type=float, default=20.0, help="box side times k")
    ap.add_argument("--ppc", type=int, default=1)
    ap.add_argument("--shape", default="cic", choices=("cic", "tsc", "pcs"))
    ap.add_argument("--nfilter", type=int, default=2)
    ap.add_argument("--compensate", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cid.SHAPE = a.shape
    k = a.eps_i
    L = a.boxk/k
    n = a.n
    tor = cid.Torus(n, L)
    zeta = zeta_field(n, L, k, a.mu, a.e, a.p)
    psiN = -0.6*zeta
    delta = -0.4*tor.lap(zeta)          # (2/3) lap psi_N at a = H = 1
    x, u, m, r, K, alpha, info, _ = mf.build(delta, L, H=1.0, ppc=a.ppc,
                                             growth_rate=1.0, omega_m=1.0,
                                             nfilter=a.nfilter, compensate=a.compensate)
    # the tool's own psi_N (spectral) against -(3/5) zeta: a check of the normalisation
    psiN_tool, _ = mf.spectral_fields(tor, delta, 1.0, 1.0)
    psi_dict = (1.0 - 2.0*psiN_tool)**0.25
    xs = np.mod(x + 0.5*L, L) - 0.5*L
    info.update({
        "mu": a.mu, "e": a.e, "p": a.p, "eps_i": a.eps_i, "k": k, "boxk": a.boxk,
        "box_side": L, "r_m": float(np.sqrt(6.0)/k), "peak_at": [0.0, 0.0, 0.0],
        "mesh": [-0.5*L, 0.5*L],
        "max_abs_psiN_minus_minus0p6zeta": float(np.abs(psiN_tool - psiN).max()),
        "zeta_max": float(zeta.max()), "delta_N_max": float(delta.max()),
        "delta_N_min": float(delta.min()),
        "max_abs_psi_dict_minus_1": float(np.abs(psi_dict - 1.0).max()),
        "solve_change_over_dictionary_c": float(np.abs(r["psi"] - psi_dict).max()
                                                / np.abs(psi_dict - 1.0).max()),
        "ge": ge_diagnostics(tor, zeta, aH=1.0),
        "E_over_rho_m_max": float(r["E"].max()/info["rho_m"]),
        "alpha_min": float(alpha.min()), "K_max": float(K.max()), "K_min": float(K.min()),
    })
    os.makedirs(a.out, exist_ok=True)
    write_particles(os.path.join(a.out, "particles.nrp"), xs, u, m)
    write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
    c = n//2
    np.savez(os.path.join(a.out, "slices.npz"), zeta=zeta[:, :, c], delta=delta[:, :, c],
             psi=r["psi"][:, :, c], psi_dict=psi_dict[:, :, c], E=r["E"][:, :, c],
             zeta_line_x=zeta[:, c, c], zeta_line_y=zeta[c, :, c],
             psi_line=r["psi"][:, c, c], psi_dict_line=psi_dict[:, c, c],
             E_line=r["E"][:, c, c], L=L, n=n)
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    for key in ("N", "zeta_max", "delta_N_max", "max_displacement_over_h", "jacobian_min",
                "mass_min_over_mean", "mass_max_over_mean", "max_velocity", "alpha_min",
                "max_abs_psiN_minus_minus0p6zeta", "max_abs_psi_dict_minus_1",
                "max_psi_minus_dictionary", "solve_change_over_dictionary_c",
                "max_hamiltonian_residual", "max_momentum_residual",
                "outer_last_change_of_psi", "E_over_rho_m_max"):
        print(f"{key}: {info[key]}")
    print("ge:", json.dumps(info["ge"]))


if __name__ == "__main__":
    main()
