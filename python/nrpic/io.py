"""Readers and writers for the particle (`*.nrp`) and radial-table (`*.tab`)
formats of docs/FORMATS.md.

Particle file, little-endian:
    8 bytes  ASCII magic b"NRPIC001"
    8 bytes  int64 N
    56 N     float64 records (x, y, z, u_x, u_y, u_z, m)
    4 N      int32 species id

Radial table, text: '#' comment lines, then rows "r u alpha" on the uniform grid
r_k = k dr starting at r = 0, u = psi - 1.
"""

import numpy as np

MAGIC = b"NRPIC001"

__all__ = ["write_nrp", "read_nrp", "write_tab", "read_tab", "MAGIC"]


def write_nrp(path, x, u, m, species=None):
    """Write N particles: positions x[N,3], covariant u_i[N,3], rest masses m[N],
    species[N] (int32, default 0)."""
    x = np.asarray(x, dtype=np.float64).reshape(-1, 3)
    u = np.asarray(u, dtype=np.float64).reshape(-1, 3)
    m = np.asarray(m, dtype=np.float64).reshape(-1)
    n = len(m)
    if x.shape[0] != n or u.shape[0] != n:
        raise ValueError("x, u and m must describe the same number of particles")
    sp = np.zeros(n, dtype="<i4") if species is None else np.asarray(species).astype("<i4")
    if sp.shape != (n,):
        raise ValueError("species must have shape (N,)")
    rec = np.empty((n, 7), dtype="<f8")
    rec[:, 0:3] = x
    rec[:, 3:6] = u
    rec[:, 6] = m
    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(np.array([n], dtype="<i8").tobytes())
        f.write(rec.tobytes(order="C"))
        f.write(sp.tobytes(order="C"))


def read_nrp(path):
    """Return (x[N,3], u[N,3], m[N], species[N]) from a `.nrp` file."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != MAGIC:
            raise ValueError(f"{path}: bad magic {magic!r}")
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        sp = np.frombuffer(f.read(4 * n), dtype="<i4")
        if len(sp) != n or f.read(1):
            raise ValueError(f"{path}: size does not match N = {n}")
    return rec[:, 0:3].copy(), rec[:, 3:6].copy(), rec[:, 6].copy(), sp.copy()


def write_tab(path, r, u, alpha, header=()):
    """Write a radial table. r must be the uniform grid k dr starting at 0."""
    r = np.asarray(r, dtype=float)
    u = np.asarray(u, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    if r[0] != 0.0:
        raise ValueError("table must start at r = 0")
    dr = r[1] - r[0]
    if np.max(np.abs(r - dr * np.arange(len(r)))) > 1e-12 * r[-1]:
        raise ValueError("table grid must be uniform, r_k = k dr")
    with open(path, "w") as f:
        for line in header:
            f.write("# " + str(line) + "\n")
        f.write(f"# N = {len(r)}  dr = {float(dr)!r}  r_max = {float(r[-1])!r}\n")
        f.write(f"# vacuum continuation: M = 2 r_N u(r_N) = {float(2 * r[-1] * u[-1])!r}\n")
        f.write("#          r                        u = psi - 1               alpha\n")
        for row in zip(r, u, alpha):
            f.write("%.17e %.17e %.17e\n" % row)


def read_tab(path):
    """Return (r, u, alpha, comments) from a `.tab` file."""
    comments = []
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                comments.append(s[1:].strip())
            else:
                rows.append([float(t) for t in s.split()[:3]])
    a = np.array(rows)
    return a[:, 0], a[:, 1], a[:, 2], comments
