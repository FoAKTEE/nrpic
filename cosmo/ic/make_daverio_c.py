"""Initial data of the random-field test of Daverio, Dirian & Mitsou (arXiv:1904.07841,
"typical cosmology", runs C704 and C256) for the NRPIC code.

    python3 make_daverio_c.py --box 704 --cut 220 --n 64 --ppc 2 --seed 1 --out DIR

The source paper starts at z = 1000 in a matter-only universe from a field delta_star
drawn from a CLASS spectrum that it does not specify, with all power removed below a
cut-off length. Here (cosmo/TESTLOG.md): the z = 0 spectrum of the Eisenstein-Hu fit
with Planck 2018 parameters, scaled to z = 1000 with the matter-only growth D = a, and a
sharp spherical cut at k = 2 pi / cut. The field is the Newtonian density contrast
delta_N of the dictionary (the gauge-invariant delta_star of the source paper).

Units. Source paper: lengths in Mpc/h, a = 1 at z = 0, H0 = 1/2997.92458 h/Mpc.
This code: a = 1 and Hubble rate 1 at the start, so a comoving length x (Mpc/h) becomes
x Hc0 with Hc0 = H0 sqrt(1001) the conformal Hubble rate at z = 1000, and wave numbers
are divided by Hc0. The power spectrum of the realization is kept in (Mpc/h)^3.

Writes DIR/particles.nrp, DIR/fields.bin, DIR/id.json, DIR/delta0.npy (delta_N on the
mesh) and DIR/meta.json.
"""
import argparse
import json
import os

import numpy as np

import cosmo_id as cid
import make_field as mf
import random_field as rf
import spectrum as sp
from nrp_io import write_fields, write_particles

Z_INIT = 1000.0
H0 = 1.0/sp.HUBBLE_DISTANCE                  # h/Mpc
HC0 = H0*np.sqrt(1.0 + Z_INIT)               # conformal Hubble rate at the start, h/Mpc

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", type=float, required=True, help="box size in Mpc/h")
    ap.add_argument("--cut", type=float, required=True, help="cut-off length in Mpc/h")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--ppc", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--shape", default="tsc", choices=("cic", "tsc", "pcs"))
    ap.add_argument("--nfilter", type=int, default=0)
    ap.add_argument("--dep-comp-c", type=float, default=0.0,
                    help="coefficient c of a compensation pass (-c, 1 + 2c, -c) per "
                         "direction on the deposited density (deposit_comp_c = c in the "
                         "code); 1/12, 1/8, 1/6 cancel the second moment of the linear, "
                         "quadratic and cubic cloud")
    ap.add_argument("--dep-comp-c2", type=float, default=0.0,
                    help="fourth-order term of that pass (deposit_comp_c2 in the code): "
                         "8/45, 37/120, 7/15 for the linear, quadratic, cubic cloud")
    ap.add_argument("--dep-comp-limit", type=float, default=0.0,
                    help="limiter of that pass (deposit_comp_limit in the code)")
    ap.add_argument("--comp-c", type=float, default=-1.0,
                    help="the same pass after the division by sqrt(gamma) "
                         "(filter_compensate = true, filter_comp_c = c in the code)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cid.SHAPE = a.shape
    cid.COMP_C = a.comp_c
    cid.DEP_COMP_C = a.dep_comp_c
    cid.DEP_COMP_LIMIT = a.dep_comp_limit
    cid.DEP_COMP_C2 = a.dep_comp_c2

    def pk(k):
        return sp.linear_power(k, 0.0, sp.PLANCK18)/(1.0 + Z_INIT)**2

    kcut = 2.0*np.pi/a.cut
    delta = rf.gaussian_field(a.n, a.box, pk, a.seed, kcut=kcut, cut="sharp",
                              zero_nyquist=True)
    L = a.box*HC0
    x, u, m, r, K, alpha, info, fid = mf.build(delta, L, 1.0, a.ppc, nfilter=a.nfilter,
                                               compensate=a.comp_c > 0.0)
    os.makedirs(a.out, exist_ok=True)
    write_particles(os.path.join(a.out, "particles.nrp"), x, u, m)
    write_fields(os.path.join(a.out, "fields.bin"), r["psi"], K, alpha, r["A"])
    np.save(os.path.join(a.out, "delta0.npy"), delta.astype(np.float64))
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(info, f, indent=1)
    meta = {"box_mpch": a.box, "cut_mpch": a.cut, "n": a.n, "ppc": a.ppc, "seed": a.seed,
            "shape": a.shape, "z_init": Z_INIT, "Hc0_h_per_mpc": HC0, "L_code": L,
            "kcut_h_per_mpc": kcut, "t_end_code": 2.0*(np.sqrt(1.0 + Z_INIT) - 1.0),
            "parameters": "Planck 2018 (Eisenstein-Hu), z = 0 spectrum scaled by 1/1001^2"}
    with open(os.path.join(a.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    for key in ("N", "delta_rms", "delta_max", "max_displacement_over_h", "jacobian_min",
                "mass_min_over_mean", "mass_max_over_mean", "max_velocity", "max_abs_psiN",
                "max_psi_minus_dictionary", "max_hamiltonian_residual",
                "max_momentum_residual", "outer_last_change_of_psi"):
        print(f"{key}: {info[key]}")
    print("L_code", L)
