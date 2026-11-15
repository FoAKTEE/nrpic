#!/usr/bin/env python3
"""End-to-end check of a written data set, from its files (registered as a run):

(a) the format-2 table, evaluated as the problem generator would (four-point Lagrange,
    pg continuation), with the density of the model: FD residuals (order 4) on the octant
    for N = 64 and 128, against the residuals of the exact fields;
(b) the 3+1 fields of the mesh file (.npz), residuals by FD (order 4) directly from the
    stored gamma_ij = psi^4 delta_ij, K_ij and E, without the radial machinery;
(c) the particle files: u_i = 0, total rest mass, extent, and the CIC-deposited density
    on the mesh of (b): rms of (rho - rho_dep)/rho_b inside 0.8 rbar_m.

    check_dataset.py <dataset directory>
"""

import argparse
import glob
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_PKG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, _PKG)
sys.path.insert(0, os.path.join(_PKG, "scripts"))

import numpy as np  # noqa: E402

from expball import mesh, particles, runlog, table  # noqa: E402
from make_dataset import build_ball  # noqa: E402


def npz_residuals(d, H, order=4, rmax=None, band=None, edges=()):
    """Order-4 residuals from the stored arrays (full cube, cell centred)."""
    x = d["x"]
    h = x[1] - x[0]
    psi = d["psi"]
    names = "xyz"
    Km = {}
    for i in range(3):
        for j in range(3):
            a, b = sorted((i, j))
            Km[i, j] = d["K" + names[a] + names[b]] / psi ** 4
    trK = Km[0, 0] + Km[1, 1] + Km[2, 2]
    g = order // 2
    st1, st2 = mesh.D1[order], mesh.D2[order]
    lap = sum(mesh._apply(psi, a, st2, g) for a in range(3)) / h ** 2
    I = lambda f: mesh._interior(f, g)  # noqa: E731
    KK = sum(I(Km[i, j]) ** 2 for i in range(3) for j in range(3))
    Hr = -8 * I(psi) ** -5 * lap + I(trK) ** 2 - KK - 16 * math.pi * I(d["E"])
    lnpsi = np.log(psi)
    dl = [mesh._apply(lnpsi, a, st1, g) / h for a in range(3)]
    M2 = 0.0
    for i in range(3):
        s = sum(mesh._apply(Km[j, i], j, st1, g) for j in range(3)) / h
        s = s + 6 * sum(I(Km[l, i]) * dl[l] for l in range(3)) - 2 * I(trK) * dl[i] \
            - mesh._apply(trK, i, st1, g) / h
        M2 = M2 + s ** 2
    xi = x[g:-g]
    X, Y, Z = np.meshgrid(xi, xi, xi, indexing="ij")
    rb = np.sqrt(X * X + Y * Y + Z * Z)
    sel = np.ones_like(rb, dtype=bool)
    for e in edges:
        sel &= np.abs(rb - e) > band
    norm = 6 * H ** 2
    return dict(H_L2=float(np.sqrt(np.mean(Hr[sel] ** 2)) / norm),
                M_L2=float(np.sqrt(np.mean(M2[sel])) / norm), ncell=int(sel.sum()), h=float(h))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("dir")
    a = p.parse_args(argv)
    js = glob.glob(os.path.join(a.dir, "*.json"))
    js = [j for j in js if not j.endswith("check.json")]
    meta = json.load(open(js[0]))
    files = {k: os.path.join(a.dir, v) for k, v in meta["files"].items()}
    args = argparse.Namespace(**meta["args"])
    ball = build_ball(args)
    with runlog.Run(f"A-pre-1: end-to-end check of data set {meta['run_id']} from its files",
                    kind="production", cores=4,
                    inputs=[js[0]] + [files[k] for k in ("table", "particles_stratified",
                                                         "particles_lattice", "mesh")]) as run:
        out = dict(dataset=meta["run_id"])
        Rb, H = ball.Rb, ball.H
        band = 0.1 * Rb
        edges = [ball.Rb] + ([ball.prof.R1, ball.prof.R2] if args.model == "tophat" else [])
        ed = ball.rbar_of_R(np.array(edges))
        regs = {"smooth": lambda r: np.min(np.abs(r[..., None] - ed), axis=-1) > band}
        T = table.Format2Table(files["table"])
        L = 1.25 * Rb
        res_a = {}
        for N in (64, 128):
            rt = mesh.residuals(mesh.radial_source(ball, T), N, L, (4,), regs, norm=6 * H ** 2)[4]["smooth"]
            re = mesh.residuals(mesh.radial_source(ball), N, L, (4,), regs, norm=6 * H ** 2)[4]["smooth"]
            res_a[N] = dict(table=rt, exact=re, H_ratio=rt["H_L2"] / re["H_L2"] if re["H_L2"] else None,
                            M_ratio=rt["M_L2"] / re["M_L2"])
        out["a_table_residuals"] = res_a
        d = dict(np.load(files["mesh"]))
        out["b_mesh_file_residuals"] = npz_residuals(d, H, 4, band=band, edges=ed)
        # (c) particles
        x_ = d["x"]
        Nm = len(x_)
        hm = x_[1] - x_[0]
        Lm = -x_[0] + 0.5 * hm
        X, Y, Z = np.meshgrid(x_, x_, x_, indexing="ij")
        rbc = np.sqrt(X * X + Y * Y + Z * Z)
        rm = ball.matter_rbar()
        reg = rbc < 0.8 * rm
        M0 = ball.rest_mass()
        res_c = {}
        for key in ("particles_stratified", "particles_lattice"):
            xp, up, mp, sp = particles.nio.read_nrp(files[key])
            dep = mesh.deposit_cic(xp, mp, Nm, Lm) / (d["psi"] ** 6 * hm ** 3)
            dH = (d["E"] - dep) / ball.rho_b
            nc = len(mp) * (d["E"] * d["psi"] ** 6 * hm ** 3)[reg].mean() / M0
            res_c[key] = dict(N=int(len(mp)), max_abs_u=float(np.abs(up).max()),
                              sum_m_over_M0=float(mp.sum() / M0),
                              r_max_over_rbar_m=float(np.sqrt((xp ** 2).sum(1)).max() / rm),
                              rms_dH=float(np.sqrt(np.mean(dH[reg] ** 2))),
                              mean_dH=float(np.mean(dH[reg])),
                              poisson=float(math.sqrt((2 / 3) ** 3 / nc)))
        out["c_particles"] = res_c
        with open(os.path.join(run.out, "check.json"), "w") as fh:
            json.dump(out, fh, indent=1, default=float)
        run.results = out
        print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
