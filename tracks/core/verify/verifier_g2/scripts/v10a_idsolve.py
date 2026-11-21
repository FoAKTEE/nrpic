#!/usr/bin/env python3
"""V10a: elliptic initial-data solver (core-v0.4), test T1: Gaussian at K = 0.

Claim (tracks/core/interfaces/id_solver.md, T1): error of psi - 1 at the centre
-9.10e-3, -2.43e-3, -6.17e-4 (residual 'stencil') and -1.92e-2, -5.22e-3, -1.33e-3
(residual 'code', nghost 4) at dx = 1, 0.5, 0.25, second order.
Own reader of <base>.idsolve.bin (docs/FORMATS.md line 208: "NRIDSOL1", 3 int64, 6
float64, int64 nfields, fields of n3*n2*n1 float64, first index fastest; psi first).
Own reference: the continuum psi of a Gaussian conformal source of mass M = 1 and width
sigma = 2 (lap psi = -2 pi rho~, rho~ = M exp(-r^2/2 sigma^2)/(2 pi sigma^2)^(3/2)):
psi = 1 + M erf(r / (sqrt 2 sigma)) / (2 r), derived here, not taken from the code.
Reader checks: K field zero; psi at the face centres against the reference.
Centre: the eight cells around the origin (their mean error; spread reported).

usage: v10a_idsolve.py OUTDIR RUNDIR...   (rundir names carry the case in runs.json)
"""
import json
import os
import struct
import sys

import numpy as np
from scipy.special import erf

M, SIG = 1.0, 2.0
CASES = {  # name: (run id, dx, residual)
    "stencil_n32": ("core-20261115-155048-87e189e", 1.0, "stencil"),
    "stencil_n64": ("core-20261115-155050-87e189e", 0.5, "stencil"),
    "stencil_n128": ("core-20261115-155053-87e189e", 0.25, "stencil"),
    "code_n32": ("core-20261115-160207-87e189e", 1.0, "code"),
    "code_n64": ("core-20261115-155051-87e189e", 0.5, "code"),
    "code_n128": ("core-20261115-155054-87e189e", 0.25, "code"),
}
SCR = "/data/haiyangw/nrpic/scratch/core"


def read_idsolve(path):
    b = open(path, "rb").read()
    assert b[:8] == b"NRIDSOL1"
    n1, n2, n3 = struct.unpack_from("<3q", b, 8)
    ext = struct.unpack_from("<6d", b, 32)
    (nf,) = struct.unpack_from("<q", b, 80)
    off = 88
    n = n1 * n2 * n3
    assert len(b) == off + 8 * nf * n, (len(b), off + 8 * nf * n)
    f = np.frombuffer(b, "<f8", nf * n, off).reshape(nf, n3, n2, n1)
    return (n1, n2, n3), ext, f


def psi_ref(r):
    q = r / (np.sqrt(2) * SIG)
    return 1 + 0.5 * M * erf(q) / r


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for name, (rid, dx, mode) in CASES.items():
        (n1, n2, n3), ext, f = read_idsolve(os.path.join(SCR, rid, "gauss.idsolve.bin"))
        x = ext[0] + (np.arange(n1) + 0.5) * (ext[1] - ext[0]) / n1
        y = ext[2] + (np.arange(n2) + 0.5) * (ext[3] - ext[2]) / n2
        z = ext[4] + (np.arange(n3) + 0.5) * (ext[5] - ext[4]) / n3
        Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
        r = np.sqrt(X * X + Y * Y + Z * Z)
        err = f[0] - psi_ref(r)
        c = [n1 // 2 - 1, n1 // 2]
        ce = err[np.ix_(c, c, c)]
        face = err[n3 // 2, n2 // 2, 0]
        res[name] = {"run": rid, "dx_meta": dx, "dx_file": (ext[1] - ext[0]) / n1, "mode": mode,
                     "n": n1, "nfields": int(f.shape[0]), "max_abs_K": float(np.abs(f[1]).max()),
                     "centre_err_mean": float(ce.mean()), "centre_err_spread": float(ce.max() - ce.min()),
                     "centre_rel_err_of_psi_minus_1": float(ce.mean() / (psi_ref(r[n3 // 2, n2 // 2, n1 // 2]) - 1)),
                     "centre_r": float(r[n3 // 2, n2 // 2, n1 // 2]),
                     "face_centre_err": float(face), "max_abs_err": float(np.abs(err).max()),
                     "max_abs_H_monitor_last": float(np.abs(f[4]).max())}
    for mode in ("stencil", "code"):
        e = [res[f"{mode}_n{n}"]["centre_rel_err_of_psi_minus_1"] for n in (32, 64, 128)]
        res[f"order_{mode}"] = [float(np.log2(e[0] / e[1])), float(np.log2(e[1] / e[2]))]
    with open(os.path.join(outdir, "v10a_idsolve.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for k, v in res.items():
        print(k, v if not isinstance(v, dict) else {kk: v[kk] for kk in ("centre_rel_err_of_psi_minus_1", "centre_err_mean", "centre_err_spread", "max_abs_K", "face_centre_err", "max_abs_H_monitor_last")})

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    dxs = np.array([1.0, 0.5, 0.25])
    claims = {"stencil": [-9.10e-3, -2.43e-3, -6.17e-4], "code": [-1.92e-2, -5.22e-3, -1.33e-3]}
    for i, mode in enumerate(("stencil", "code")):
        e = -np.array([res[f"{mode}_n{n}"]["centre_rel_err_of_psi_minus_1"] for n in (32, 64, 128)])
        ax.loglog(dxs, e, "o-", color=fs.SERIES[i], lw=1, ms=4, label=f"{mode} (own)")
        ax.loglog(dxs, -np.array(claims[mode]), "x", color="k", ms=6)
    ax.loglog(dxs, 5e-3 * dxs ** 2, **fs.GUIDE, label=r"$\propto dx^2$")
    ax.set_xlabel("dx")
    ax.set_ylabel(r"$-(\psi-\psi_{\rm ex})/(\psi_{\rm ex}-1)$, centre cells")
    ax.legend(fontsize=7, title="x: claimed", title_fontsize=7)
    ax.set_title("V10a: initial-data solver T1, Gaussian (runs of core-v0.4 branch)", fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v10a_idsolve"))


if __name__ == "__main__":
    main()
