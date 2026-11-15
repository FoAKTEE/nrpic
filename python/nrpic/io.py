"""Readers and writers for the particle (`*.nrp`) and radial-table (`*.tab`)
formats of docs/FORMATS.md.

Particle file, little-endian:
    8 bytes  ASCII magic b"NRPIC001"
    8 bytes  int64 N
    56 N     float64 records (x, y, z, u_x, u_y, u_z, m)
    4 N      int32 species id

Radial table, text: '#' comment lines, then rows "r u alpha" on the uniform grid
r_k = k dr starting at r = 0, u = psi - 1.

Radial table with extrinsic curvature (format 2, tracks/core/interfaces/
spherical_id_format2.md), text: header lines "# key = value" with the keys format,
columns, exterior and optionally breaks, then rows "rbar u KL KT alpha betar" on the
same uniform grid.  `Table2` evaluates such a table with the rule of the problem
generator nrpic_cf (cubic through four rows, never across a break, continuation
beyond the last row).
"""

import numpy as np

MAGIC = b"NRPIC001"

__all__ = ["write_nrp", "read_nrp", "write_tab", "read_tab", "MAGIC",
           "write_tab2", "read_tab2", "Table2", "TAB2_COLUMNS"]


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


# ----------------------------------------------------------------------------
# format 2: spherical initial data with extrinsic curvature
# ----------------------------------------------------------------------------
TAB2_COLUMNS = ("rbar", "u", "KL", "KT", "alpha", "betar")


class Table2:
    """Spherical initial data of table format 2.

    Attributes: rbar, u, KL, KT, alpha, betar (arrays over the rows), exterior
    ("pg" or "zero"), breaks (sorted radii at which the columns may be
    discontinuous), header (dict of the other "key = value" lines), comments.

    Geometry: gamma_ij = psi^4 delta_ij with psi = 1 + u; K^i_j has the radial
    eigenvalue KL and the tangential eigenvalue KT (expansion: K = KL + 2 KT < 0);
    lapse alpha; shift beta^i = betar n^i.
    """

    def __init__(self, rbar, u, KL, KT, alpha, betar, exterior="pg", breaks=(),
                 header=None, comments=()):
        self.rbar = np.asarray(rbar, dtype=float)
        n = len(self.rbar)
        cols = [np.asarray(c, dtype=float) for c in (u, KL, KT, alpha, betar)]
        if any(c.shape != (n,) for c in cols):
            raise ValueError("all columns must have one value per row")
        self.u, self.KL, self.KT, self.alpha, self.betar = cols
        if exterior not in ("pg", "zero"):
            raise ValueError("exterior must be 'pg' or 'zero'")
        self.exterior = exterior
        self.breaks = tuple(sorted(float(b) for b in breaks))
        self.header = dict(header or {})
        self.comments = list(comments)
        if n < 8:
            raise ValueError("a table needs at least 8 rows")
        if self.rbar[0] != 0.0:
            raise ValueError("table must start at rbar = 0")
        self.dr = float(self.rbar[1] - self.rbar[0])
        if np.max(np.abs(self.rbar - self.dr * np.arange(n))) > 1e-8 * self.rbar[-1]:
            raise ValueError("table grid must be uniform, rbar_k = k drbar")
        self.pieces = self._pieces()

    def _pieces(self):
        """Row ranges (klo, khi), inclusive, of the pieces between the breaks.
        A row belongs to the piece outside a break when rbar_k >= break."""
        n = len(self.rbar)
        edges = [0]
        for b in self.breaks:
            if not 0.0 < b < self.rbar[-1]:
                raise ValueError(f"break {b!r} is not inside the table")
            k = int(np.searchsorted(self.rbar, b, side="left"))   # first row >= b
            if abs(self.rbar[k] - b) < 1e-6 * self.dr or abs(self.rbar[k - 1] - b) < 1e-6 * self.dr:
                raise ValueError(f"break {b!r} coincides with a row; move it between rows")
            edges.append(k)
        edges.append(n)
        out = [(edges[i], edges[i + 1] - 1) for i in range(len(edges) - 1)]
        if any(hi - lo + 1 < 4 for lo, hi in out):
            raise ValueError("every piece between breaks needs at least 4 rows")
        return out

    @property
    def rlast(self):
        return float(self.rbar[-1])

    def columns(self):
        return dict(rbar=self.rbar, u=self.u, KL=self.KL, KT=self.KT, alpha=self.alpha,
                    betar=self.betar)

    def __call__(self, r):
        """Return (u, KL, KT, alpha, betar) at radii r, as the problem generator does."""
        r = np.abs(np.asarray(r, dtype=float))
        shape = r.shape
        r = r.ravel()
        xi = r / self.dr
        i = np.floor(xi).astype(np.int64)
        piece = np.searchsorted(np.asarray(self.breaks), r, side="right")
        klo = np.array([p[0] for p in self.pieces])[piece]
        khi = np.array([p[1] for p in self.pieces])[piece]
        i = np.minimum(np.maximum(i, klo + 1), khi - 2)
        s = xi - i
        w = np.stack([-s * (s - 1.0) * (s - 2.0) / 6.0,
                      (s + 1.0) * (s - 1.0) * (s - 2.0) / 2.0,
                      -(s + 1.0) * s * (s - 2.0) / 2.0,
                      (s + 1.0) * s * (s - 1.0) / 6.0])
        out = []
        ext = r >= self.rlast
        q = self.rlast / np.where(ext, r, 1.0)
        for name, col in (("u", self.u), ("KL", self.KL), ("KT", self.KT),
                          ("alpha", self.alpha), ("betar", self.betar)):
            v = sum(w[j] * col[i - 1 + j] for j in range(4))
            if name == "u":
                v = np.where(ext, col[-1] * q, v)
            elif name == "alpha":
                v = np.where(ext, col[-1], v)
            elif self.exterior == "zero":
                v = np.where(ext, 0.0, v)
            elif name == "betar":
                v = np.where(ext, col[-1] * np.sqrt(q), v)
            else:
                v = np.where(ext, col[-1] * q * np.sqrt(q), v)
            out.append(v.reshape(shape))
        return tuple(out)

    def cartesian(self, x, centre=(0.0, 0.0, 0.0), psi=None):
        """K_ij[...,3,3], alpha[...], beta^i[...,3] at Cartesian points x[...,3], with
        psi the full conformal factor (default 1 + u of this table alone)."""
        d = np.asarray(x, dtype=float) - np.asarray(centre, dtype=float)
        r = np.sqrt(np.sum(d * d, axis=-1))
        n = d / np.where(r > 0.0, r, 1.0)[..., None]
        u, kl, kt, alp, br = self(r)
        p4 = (1.0 + u if psi is None else np.asarray(psi, dtype=float)) ** 4
        nn = n[..., :, None] * n[..., None, :]
        kij = p4[..., None, None] * (kt[..., None, None] * np.eye(3)
                                     + (kl - kt)[..., None, None] * nn)
        return kij, alp, br[..., None] * n


def write_tab2(path, rbar, u, KL, KT, alpha, betar, exterior="pg", breaks=(), header=()):
    """Write a format-2 table.  `header` is a sequence of "key = value" strings or
    free text lines (written after the required keys), `breaks` the radii at which
    the columns may be discontinuous (each strictly between two rows)."""
    t = Table2(rbar, u, KL, KT, alpha, betar, exterior=exterior, breaks=breaks)
    with open(path, "w") as f:
        f.write("# format = 2\n")
        f.write("# columns = " + " ".join(TAB2_COLUMNS) + "\n")
        f.write(f"# exterior = {t.exterior}\n")
        if t.breaks:
            f.write("# breaks = " + " ".join(repr(b) for b in t.breaks) + "\n")
        f.write(f"# rows = {len(t.rbar)}\n")
        f.write(f"# drbar = {t.dr!r}\n")
        for line in header:
            f.write("# " + str(line) + "\n")
        for row in zip(t.rbar, t.u, t.KL, t.KT, t.alpha, t.betar):
            f.write("%.17e %.17e %.17e %.17e %.17e %.17e\n" % row)
    return t


def read_tab2(path):
    """Return the `Table2` of a format-2 file."""
    header, comments, rows = {}, [], []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                body = s[1:].strip()
                if "=" in body:
                    key, val = body.split("=", 1)
                    header[key.strip()] = val.strip()
                else:
                    comments.append(body)
            else:
                rows.append([float(t) for t in s.split()[:6]])
    if header.get("format") != "2":
        raise ValueError(f"{path}: not a format-2 table (no header line '# format = 2')")
    if tuple(header.get("columns", "").split()) != TAB2_COLUMNS:
        raise ValueError(f"{path}: columns must be {' '.join(TAB2_COLUMNS)}")
    if "exterior" not in header:
        raise ValueError(f"{path}: header line '# exterior = pg | zero' is missing")
    a = np.array(rows)
    if a.ndim != 2 or a.shape[1] != 6:
        raise ValueError(f"{path}: rows must have six values")
    breaks = [float(t) for t in header.get("breaks", "").split()]
    skip = ("format", "columns", "exterior", "breaks")
    return Table2(a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5],
                  exterior=header["exterior"], breaks=breaks,
                  header={k: v for k, v in header.items() if k not in skip},
                  comments=comments)
