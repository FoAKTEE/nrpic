"""Exact initial data of the shearing-dust test (arXiv:2003.08014, draft.tex:142-182) in
the code's conformally flat form (SPEC.md section 2), in the existing file formats of
cosmo/ic/nrp_io.py: fields.bin (NRCOSMO1: psi = 1, K = -3H, alpha = 1,
Ahat_xy = (3b/(4L)) cos(2 pi y/L)) and particles.nrp (NRPIC001).

File order of the particles (the code tags them in file order and records the tags below
traj_ntrack):
  1. tracers (mass 1e-30 of the mean particle mass; comoving with the dust): the
     observer at O = (0, 0, 0) and four more at y = L/8, L/4, 3L/8, -L/4 (x = z = 0);
  2. light rays emitted at O at t = 0 (mass -1e-30, cosmo/ic/ray_ic.py convention):
     fan A, coordinate directions (1, s, 0); fan B, directions (s, 1, 0);
  3. the dust: a lattice of ppc_xz x ppc_y x ppc_xz particles per cell in the box
     [-L/2, L/2]^3 (positions at the centres of the sub-cells), masses
     m = D(y) Delta V with D = sqrt(gamma) rho0 W the rest-mass density per coordinate
     volume, covariant momenta per unit rest mass u = (u*^x(y), 0, 0).

Units G = c = H = 1, so L = HL and b = beta (HL)^2.

    python3 make_shear_ic.py --beta 0.005 --HL 1 --ny 64 [--nxz 4] [--ppc-y 1]
        [--fanA c,w,n] [--fanB c,w,n] --out DIR
Fans: centre c (default: first-order slope), half width w (relative to |c| if --fan-rel,
default) and number n of rays. DIR receives fields.bin, particles.nrp, meta.json
(written into $NRPIC_RUN_DIR when --out is not given).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, HERE)
from nrp_io import write_fields, write_particles  # noqa: E402
import shear_ref as sr  # noqa: E402

TRACER_Y = (0.0, 0.125, 0.25, 0.375, -0.25)      # in units of L


def build(beta, HL, ny, nxz=4, ppc_y=1, ppc_xz=1, fanA=None, fanB=None, fan_rel=True):
    L = float(HL)
    b = beta*HL**2
    if not b < sr.b_max(HL):
        raise ValueError("b outside the physical range")
    dy, dx = L/ny, L/nxz
    # ---- fields at the cell centres, arrays [i, j, k]
    yc = -0.5*L + (np.arange(ny) + 0.5)*dy
    shape = (nxz, ny, nxz)
    d_c = sr.initial_data(yc, b, L)
    ahxy = np.broadcast_to(d_c["Ahat_xy"][None, :, None], shape).copy()
    zero = np.zeros(shape)
    fields = {"psi": np.ones(shape), "K": -3.0*np.ones(shape), "alpha": np.ones(shape),
              "ahat": [zero, ahxy, zero, zero, zero, zero]}
    # ---- dust lattice
    npx, npy = nxz*ppc_xz, ny*ppc_y
    qx = -0.5*L + (np.arange(npx) + 0.5)*(L/npx)
    qy = -0.5*L + (np.arange(npy) + 0.5)*(L/npy)
    dV = (L/npx)*(L/npy)*(L/npx)
    d_p = sr.initial_data(qy, b, L)
    X, Y, Z = np.meshgrid(qx, qy, qx, indexing="ij")
    J = np.broadcast_to(np.arange(npy)[None, :, None], X.shape)
    xd = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    md = (d_p["D"]*dV)[J.ravel()]
    ud = np.zeros_like(xd)
    ud[:, 0] = d_p["ux"][J.ravel()]
    mmean = md.mean()
    # ---- tracers
    ty = np.array(TRACER_Y)*L
    d_t = sr.initial_data(ty, b, L)
    xt = np.stack([np.zeros_like(ty), ty, np.zeros_like(ty)], axis=1)
    ut = np.zeros_like(xt)
    ut[:, 0] = d_t["ux"]
    mt = np.full(len(ty), 1e-30*mmean)
    # ---- rays
    sA, sB, _, cl = sr.first_order_parts(b, L)
    fans = {}
    for name, fan, s0 in (("A", fanA, sA), ("B", fanB, sB)):
        c, w, n = (s0, 0.1, 9) if fan is None else fan
        half = w*abs(c) if fan_rel else w
        fans[name] = c + half*np.linspace(-1.0, 1.0, int(n))
    cr = [np.stack([np.ones_like(fans["A"]), fans["A"], np.zeros_like(fans["A"])], axis=1),
          np.stack([fans["B"], np.ones_like(fans["B"]), np.zeros_like(fans["B"])], axis=1)]
    cr = np.concatenate(cr)
    xr = np.zeros_like(cr)
    mr = np.full(len(cr), -1e-30)
    x = np.concatenate([xt, xr, xd])
    u = np.concatenate([ut, cr, ud])
    m = np.concatenate([mt, mr, md])
    nt, nr = len(mt), len(mr)
    meta = {"beta": beta, "HL": HL, "L": L, "b": b, "H": 1.0, "ny": ny, "nxz": nxz,
            "ppc_y": ppc_y, "ppc_xz": ppc_xz, "n_dust": int(len(md)),
            "n_tracers": nt, "tracer_y": ty.tolist(), "tracer_tags": list(range(nt)),
            "rays_A_tags": list(range(nt, nt + len(fans["A"]))),
            "rays_B_tags": list(range(nt + len(fans["A"]), nt + nr)),
            "fan_A": fans["A"].tolist(), "fan_B": fans["B"].tolist(),
            "slope_A_lin": sA, "slope_B_lin": sB, "cos_lin": cl,
            "cos_lin_closed": sr.cos_lin(b, HL), "traj_ntrack": nt + nr,
            "box": [[-0.5*L, 0.5*L]]*3, "m_mean": float(mmean),
            "total_rest_mass": float(md.sum())}
    return fields, (x, u, m), meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--beta", type=float, required=True)
    ap.add_argument("--HL", type=float, required=True)
    ap.add_argument("--ny", type=int, required=True)
    ap.add_argument("--nxz", type=int, default=4)
    ap.add_argument("--ppc-y", type=int, default=1)
    ap.add_argument("--ppc-xz", type=int, default=1)
    ap.add_argument("--fanA", default=None, help="centre,halfwidth,n")
    ap.add_argument("--fanB", default=None, help="centre,halfwidth,n")
    ap.add_argument("--fan-abs", action="store_true",
                    help="half widths are absolute, not relative to |centre|")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    def fan(s):
        if s is None:
            return None
        c, w, n = s.split(",")
        return float(c), float(w), int(n)
    out = a.out or os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    fields, (x, u, m), meta = build(a.beta, a.HL, a.ny, a.nxz, a.ppc_y, a.ppc_xz,
                                    fan(a.fanA), fan(a.fanB), not a.fan_abs)
    write_fields(os.path.join(out, "fields.bin"), fields["psi"], fields["K"],
                 fields["alpha"], fields["ahat"])
    write_particles(os.path.join(out, "particles.nrp"), x, u, m)
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps({k: meta[k] for k in ("beta", "HL", "b", "ny", "n_dust",
                                           "traj_ntrack", "slope_A_lin", "slope_B_lin",
                                           "cos_lin")}))
    return meta


if __name__ == "__main__":
    main()
