"""Table format 2 of coord/INTERFACES/spherical_id_format2.md: writer, reader, evaluation.

Rows rbar_k = k drbar (k = 0 .. N-1) with columns rbar u KL KT alpha betar, u = psi - 1.
Beyond the last row: u = u_N rbar_N/rbar; with exterior = pg, KL and KT continue as
rbar^(-3/2), betar as rbar^(-1/2), alpha stays (exact for a Painleve-Gullstrand vacuum with
psi = 1, which is what the ball has outside its matter: E = 0 there, so rbar = R).

The evaluation inside the table uses the four-point Lagrange interpolation of the code's
format-1 tables (athenak/src/pgen/nrpic/nrpic_cf.cpp, CFCubic); the format-2 reader of the
code is not written yet (core/id-extrinsic), so this is an assumption to be checked then.
"""

import numpy as np

__all__ = ["COLUMNS", "write_format2", "read_format2", "lagrange4", "Format2Table"]

COLUMNS = ("rbar", "u", "KL", "KT", "alpha", "betar")


def write_format2(path, ball, drbar, rbar_max=None, exterior="pg", shift="ltb", header=None):
    """Write the slice of `ball` as a format-2 table. rbar_max defaults to 1.5 times the
    isotropic radius of the matter edge; the last row must lie in vacuum for exterior = pg.
    shift = 'ltb' writes betar = -v/(psi^2 sqrt(1+2E)) (the shift of the dust's proper-time
    slicing); 'zero' writes betar = 0."""
    rmat = ball.matter_rbar()
    rbar_max = rbar_max or 1.5 * rmat
    if rbar_max <= rmat:
        raise ValueError("the table must extend beyond the matter")
    N = int(np.ceil(rbar_max / drbar)) + 1
    rb = drbar * np.arange(N)
    f = ball.fields(rb, ("u", "KL", "KT", "betar"))
    alpha = np.ones(N)
    betar = f["betar"] if shift == "ltb" else np.zeros(N)
    rows = np.column_stack([rb, f["u"], f["KL"], f["KT"], alpha, betar])
    with open(path, "w") as fh:
        fh.write("# format = 2\n")
        fh.write("# columns = " + " ".join(COLUMNS) + "\n")
        fh.write(f"# exterior = {exterior}\n")
        for k, v in (header or {}).items():
            fh.write(f"# {k} = {v}\n")
        fh.write(f"# N = {N}\n# drbar = {float(drbar)!r}\n# rbar_last = {float(rb[-1])!r}\n")
        fh.write(f"# shift = {shift}\n")
        for r in rows:
            fh.write(" ".join(f"{x:.17e}" for x in r) + "\n")
    return rows


def read_format2(path):
    """Return (dict of columns, dict of header keys)."""
    hdr, data = {}, []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                if "=" in s:
                    k, v = s[1:].split("=", 1)
                    hdr[k.strip()] = v.strip()
                continue
            data.append([float(t) for t in s.split()])
    a = np.array(data)
    cols = hdr.get("columns", " ".join(COLUMNS)).split()
    if hdr.get("format") != "2":
        raise ValueError(f"{path}: not a format-2 table")
    return {c: a[:, i] for i, c in enumerate(cols)}, hdr


def lagrange4(tab, dr, r):
    """Four-point Lagrange interpolation in a uniform table starting at r = 0, the stencil
    clamped to [1, n-3] exactly as CFCubic in nrpic_cf.cpp."""
    n = len(tab)
    xi = np.asarray(r, dtype=float) / dr
    i = np.clip(np.floor(xi).astype(np.int64), 1, n - 3)
    s = xi - i
    wm = -s * (s - 1.0) * (s - 2.0) / 6.0
    w0 = (s + 1.0) * (s - 1.0) * (s - 2.0) / 2.0
    w1 = -(s + 1.0) * s * (s - 2.0) / 2.0
    w2 = (s + 1.0) * s * (s - 1.0) / 6.0
    return wm * tab[i - 1] + w0 * tab[i] + w1 * tab[i + 1] + w2 * tab[i + 2]


class Format2Table:
    """Evaluate a format-2 table as the problem generator is expected to."""

    def __init__(self, path_or_cols, hdr=None):
        if isinstance(path_or_cols, str):
            cols, hdr = read_format2(path_or_cols)
        else:
            cols = path_or_cols
        self.c = cols
        self.hdr = hdr or {}
        rb = cols["rbar"]
        self.dr = rb[1] - rb[0]
        if abs(rb[0]) > 0 or np.max(np.abs(rb - self.dr * np.arange(len(rb)))) > 1e-9 * rb[-1]:
            raise ValueError("table must be uniform starting at rbar = 0")
        self.rlast = rb[-1]
        self.ext = self.hdr.get("exterior", "pg")

    def __call__(self, r, keys=("u", "KL", "KT", "alpha", "betar")):
        r = np.asarray(r, dtype=float)
        out = {}
        inside = r < self.rlast
        rr = np.where(inside, r, self.rlast)
        for k in keys:
            val = lagrange4(self.c[k], self.dr, rr)
            last = self.c[k][-1]
            if k == "u":
                cont = last * self.rlast / np.where(inside, 1.0, r)
            elif k in ("KL", "KT"):
                cont = last * (self.rlast / np.where(inside, 1.0, r)) ** 1.5 \
                    if self.ext == "pg" else 0.0 * r
            elif k == "betar":
                cont = last * (self.rlast / np.where(inside, 1.0, r)) ** 0.5 \
                    if self.ext == "pg" else 0.0 * r
            else:
                cont = last + 0.0 * r
            out[k] = np.where(inside, val, cont)
        return out
