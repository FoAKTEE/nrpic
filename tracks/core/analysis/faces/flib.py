"""Reading and region statistics of AthenaK field dumps (.bin) for the package faces.

A dump is read with athenak/vis/python/bin_convert.py (read_binary).  Every MeshBlock
of a dump is a leaf of the mesh, so sums over the blocks with the cell volume as weight
are sums over the mesh, also with static refinement.

Regions (L: half-width of the cubic mesh, d = L - max(|x|, |y|, |z|) the distance of a
cell centre to the nearest face, r its distance to the origin):
    faces     d < w_face
    interior  r_in0 <= r < r_in1
    all       every cell (r >= r_exc when a puncture sits at the origin)
"""

import glob
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "athenak", "vis", "python"))
sys.path.insert(0, os.path.join(ROOT, "python"))

import bin_convert  # noqa: E402


def dumps(rundir, var, base=None):
    """sorted list of the dumps bin/<base>.<var>.NNNNN.bin of a run directory"""
    pat = os.path.join(rundir, "bin", f"{base or '*'}.{var}.*.bin")
    return sorted(glob.glob(pat))


class Dump:
    """cells of one dump: x, y, z (centres), dv (cell volume), data[var], all flat,
    plus the block structure (for comparisons between runs)"""

    def __init__(self, path):
        fd = bin_convert.read_binary(path)
        self.time = fd["time"]
        self.cycle = fd["cycle"]
        self.names = fd["var_names"]
        self.L = fd["x1max"]
        self.xmin = fd["x1min"]
        self.blocks = []
        geo = fd["mb_geometry"]
        for b in range(fd["n_mbs"]):
            x1i, x2i, x3i, dx1, dx2, dx3 = geo[b]
            arr = {v: np.asarray(fd["mb_data"][v][b], dtype=np.float64)
                   for v in self.names}
            n3, n2, n1 = arr[self.names[0]].shape
            self.blocks.append({"x0": (x1i, x2i, x3i), "dx": (dx1, dx2, dx3),
                                "n": (n1, n2, n3), "data": arr})

    def block_coords(self, b):
        x0, dx, n = b["x0"], b["dx"], b["n"]
        x = x0[0] + (np.arange(n[0]) + 0.5) * dx[0]
        y = x0[1] + (np.arange(n[1]) + 0.5) * dx[1]
        z = x0[2] + (np.arange(n[2]) + 0.5) * dx[2]
        return np.meshgrid(z, y, x, indexing="ij")  # arrays indexed (k, j, i)

    def flat(self, var):
        """x, y, z, dv, value of every cell"""
        xs, ys, zs, dvs, vs = [], [], [], [], []
        for b in self.blocks:
            Z, Y, X = self.block_coords(b)
            xs.append(X.ravel())
            ys.append(Y.ravel())
            zs.append(Z.ravel())
            dvs.append(np.full(X.size, b["dx"][0] * b["dx"][1] * b["dx"][2]))
            vs.append(b["data"][var].ravel())
        return (np.concatenate(xs), np.concatenate(ys), np.concatenate(zs),
                np.concatenate(dvs), np.concatenate(vs))

    def uniform(self, var):
        """3D array (k, j, i) of a uniform mesh, with the cell-centre coordinate axis"""
        dx = self.blocks[0]["dx"][0]
        n = int(round((self.L - self.xmin) / dx))
        out = np.full((n, n, n), np.nan)
        for b in self.blocks:
            i0 = int(round((b["x0"][0] - self.xmin) / dx))
            j0 = int(round((b["x0"][1] - self.xmin) / dx))
            k0 = int(round((b["x0"][2] - self.xmin) / dx))
            n1, n2, n3 = b["n"]
            out[k0:k0 + n3, j0:j0 + n2, i0:i0 + n1] = b["data"][var]
        x = self.xmin + (np.arange(n) + 0.5) * dx
        return x, out

    def key(self, b):
        return tuple(int(round(v * 4096)) for v in b["x0"]) + (int(round(b["dx"][0] * 4096)),)


def region_stats(d, var, r_in0=0.0, r_in1=8.0, w_face=4.0, r_exc=0.0, L=None):
    """volume-weighted mean and L2 of |var| and its maximum over the regions"""
    x, y, z, dv, v = d.flat(var)
    L = d.L if L is None else L
    r = np.sqrt(x * x + y * y + z * z)
    dface = L - np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
    a = np.abs(v)
    ok = np.isfinite(a) & (r >= r_exc) & (dface > 0)
    out = {}
    for name, m in (("all", ok),
                    ("interior", ok & (r >= r_in0) & (r < r_in1)),
                    ("faces", ok & (dface < w_face)),
                    ("bulk", ok & (dface >= w_face))):
        w = dv[m]
        if w.size == 0:
            out[name] = {"mean": np.nan, "l2": np.nan, "max": np.nan, "vol": 0.0}
            continue
        out[name] = {"mean": float(np.sum(w * a[m]) / np.sum(w)),
                     "l2": float(np.sqrt(np.sum(w * a[m] ** 2) / np.sum(w))),
                     "max": float(a[m].max()), "vol": float(np.sum(w)),
                     "integral": float(np.sum(w * a[m]))}
    return out


def history(rundir, var="con_H", dumpvar="con", **kw):
    """region statistics of every dump of a run: dict of arrays keyed 'region.stat'"""
    rows = []
    for p in dumps(rundir, dumpvar):
        d = Dump(p)
        s = region_stats(d, var, **kw)
        row = {"time": d.time}
        for reg, st in s.items():
            for k, val in st.items():
                row[f"{reg}.{k}"] = val
        rows.append(row)
    if not rows:
        return {}
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def difference(da, db, var):
    """|var_a - var_b| on the blocks the two dumps share (same origin and cell size):
    x, y, z, dv, a, b flat over the shared blocks"""
    kb = {db.key(b): b for b in db.blocks}
    xs, ys, zs, dvs, va, vb = [], [], [], [], [], []
    for b in da.blocks:
        o = kb.get(da.key(b))
        if o is None or o["n"] != b["n"]:
            continue
        Z, Y, X = da.block_coords(b)
        xs.append(X.ravel())
        ys.append(Y.ravel())
        zs.append(Z.ravel())
        dvs.append(np.full(X.size, b["dx"][0] * b["dx"][1] * b["dx"][2]))
        va.append(b["data"][var].ravel())
        vb.append(o["data"][var].ravel())
    return tuple(np.concatenate(q) for q in (xs, ys, zs, dvs, va, vb))


def axis_line(d, var, tol=None):
    """values along the line nearest to the x axis (y, z the smallest positive cell
    centres of each block): sorted x, value, cell size"""
    xs, vs, hs = [], [], []
    for b in d.blocks:
        dx = b["dx"]
        y0, z0 = b["x0"][1], b["x0"][2]
        n1, n2, n3 = b["n"]
        # block contains the line y = z = 0+ if its range covers (0, dx)
        if not (y0 <= 0.0 < y0 + n2 * dx[1] - 1e-12 and z0 <= 0.0 < z0 + n3 * dx[2] - 1e-12):
            continue
        j = int(np.floor((0.0 - y0) / dx[1] + 1e-9))
        k = int(np.floor((0.0 - z0) / dx[2] + 1e-9))
        x = b["x0"][0] + (np.arange(n1) + 0.5) * dx[0]
        xs.append(x)
        vs.append(b["data"][var][k, j, :])
        hs.append(np.full(n1, dx[0]))
    x = np.concatenate(xs)
    o = np.argsort(x)
    return x[o], np.concatenate(vs)[o], np.concatenate(hs)[o]
