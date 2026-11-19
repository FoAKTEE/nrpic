"""Initial data of the Szekeres hole for AthenaK's periodic problem generator `nrpic_cosmo`.

The model is exactly Einstein-de Sitter outside label radius R2 (and psi = 1 there in the
coordinates of confmap.py), so the hole tiles a periodic box of side 2 Lh > 2 R2.
Two files (DESIGN.md section 3):

* the field file of `<problem> id = file` (athenak/src/pgen/nrpic/nrpic_cosmo.cpp lines
  12-19, 108-130): 8 bytes "NRCOSMO1", 3 int64 (n1, n2, n3), then 9 arrays of n3 n2 n1
  doubles, first index fastest, at the cell centres of the root mesh: psi, K, alpha,
  Ahat_xx, Ahat_xy, Ahat_xz, Ahat_yy, Ahat_yz, Ahat_zz, with
  K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K, i.e.
  K = KL + 2 KT and Ahat_ij = psi^6 (KL - KT)(N_i N_j - delta_ij/3);
* the particle file (python/nrpic/io.py, docs/FORMATS.md): one particle per cell at the
  cell centre, at rest (u_i = 0), rest mass m = rho psi^6 h^3. With the cloud-in-cell
  deposit a particle at a cell centre gives its whole mass to that cell, so the code's
  energy density E = sum m / (h^3 psi^6) equals rho at every cell centre: no sampling
  noise and no cloud smoothing [JUDGEMENT from the CIC weights; checked in the run].
"""

import os
import sys

import numpy as np

__all__ = ["cell_centres", "slice_on_mesh", "write_nrcosmo", "write_particles", "particles_arrays"]

_REPO_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "python", "nrpic")


def cell_centres(N, Lh):
    h = 2.0 * Lh / N
    return -Lh + (np.arange(N) + 0.5) * h, h


def slice_on_mesh(cm, N, Lh, chunk=1 << 18):
    """Fields of the slice of ConformalMap cm at the cell centres of [-Lh, Lh]^3 (N cells per
    side), arrays indexed [i, j, k] (x, y, z)."""
    c, h = cell_centres(N, Lh)
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    keys = ("psi", "rho", "KL", "KT", "r", "bn", "Theta", "Sigma", "W")
    out = {k: np.empty(len(pts)) for k in keys}
    out["N"] = np.empty((len(pts), 3))
    for s in range(0, len(pts), chunk):
        f = cm.fields(pts[s:s + chunk])
        for k in keys:
            out[k][s:s + chunk] = f[k]
        out["N"][s:s + chunk] = f["N"]
    sh = X.shape
    res = {k: v.reshape(sh) for k, v in out.items() if k != "N"}
    res["N"] = out["N"].reshape(sh + (3,))
    res["x"], res["h"] = c, h
    return res


def _fileorder(F):
    """[i, j, k] array -> flat array with i (x) fastest."""
    return np.ascontiguousarray(np.asarray(F, dtype="<f8").transpose(2, 1, 0)).ravel()


def write_nrcosmo(path, f):
    psi, KL, KT, Nv = f["psi"], f["KL"], f["KT"], f["N"]
    n = psi.shape[0]
    K = KL + 2.0 * KT
    w = psi ** 6 * (KL - KT)
    A = {}
    for a, (i, j) in zip(("xx", "xy", "xz", "yy", "yz", "zz"),
                         ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))):
        A[a] = w * (Nv[..., i] * Nv[..., j] - (1.0 / 3.0 if i == j else 0.0))
    with open(path, "wb") as fh:
        fh.write(b"NRCOSMO1")
        fh.write(np.array([n, n, n], dtype="<i8").tobytes())
        for arr in (psi, K, np.ones_like(psi), A["xx"], A["xy"], A["xz"], A["yy"], A["yz"], A["zz"]):
            fh.write(_fileorder(arr).tobytes())


def write_particles(path, f):
    """One particle per cell at the cell centre, u_i = 0, m = rho psi^6 h^3, written with
    the writer of python/nrpic/io.py (loaded by path under another module name)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("nrpic_io", os.path.join(os.path.abspath(_REPO_PY), "io.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    x, u, m = particles_arrays(f)
    mod.write_nrp(path, x, u, m)
    return len(m)


def particles_arrays(f):
    c, h = f["x"], f["h"]
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    x = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    m = (f["rho"] * f["psi"] ** 6).ravel() * h ** 3
    return x, np.zeros_like(x), m
