"""Readers and measures of the fresh G2 verifier of Track B (written from the file formats,
not from the lead's code).

Mesh dumps: athenak/src/outputs/binary.cpp (version 1.1: text pre-header, parameter dump,
then per meshblock 10 int32 [ois oie ojs oje oks oke lx1 lx2 lx3 level], 6 Real
[x1min x1max x2min x2max x3min x3max], then nvar blocks of cells, i fastest).
Particle snapshots: docs/FORMATS.md (NRPSNAP1, float64 t, int64 N, int64 cycle, N x 7
float64 (x1 x2 x3 u1 u2 u3 m), N int32 tags, N int32 species, N float64 tau).
History files: whitespace columns, comment lines start with '#', a restart may repeat rows.
"""
import re

import numpy as np


# --------------------------------------------------------------------------------- mesh
def read_mesh_header(fn):
    with open(fn, "rb") as f:
        head = f.read(4096)
    txt = head.decode("latin-1")
    lines = txt.split("\n")
    info = {}
    pos = 0
    for ln in lines:
        pos += len(ln) + 1
        s = ln.strip()
        if s.startswith("time="):
            info["time"] = float(s[5:])
        elif s.startswith("cycle="):
            info["cycle"] = int(s[6:])
        elif s.startswith("size of location="):
            info["loc_size"] = int(s.split("=")[1])
        elif s.startswith("size of variable="):
            info["var_size"] = int(s.split("=")[1])
        elif s.startswith("number of variables="):
            info["nvar"] = int(s.split("=")[1])
        elif s.startswith("variables:"):
            info["vars"] = s[len("variables:"):].split()
        elif s.startswith("header offset="):
            info["param_size"] = int(s.split("=")[1])
            info["data_start"] = pos + info["param_size"]
            break
    return info


def read_mesh(fn, names):
    """Global arrays [k, j, i] (z, y, x) of the variables in names, plus the header.
    Uniform meshes only (one refinement level)."""
    h = read_mesh_header(fn)
    ls, vs, nv = h["loc_size"], h["var_size"], h["nvar"]
    dt = np.float64 if vs == 8 else np.float32
    lt = np.float64 if ls == 8 else np.float32
    idx = [h["vars"].index(n) for n in names]
    raw = np.memmap(fn, dtype=np.uint8, mode="r", offset=h["data_start"])
    i4 = np.frombuffer(raw[:40].tobytes(), dtype=np.int32)
    nx, ny, nz = i4[1] - i4[0] + 1, i4[3] - i4[2] + 1, i4[5] - i4[4] + 1
    cells = nx*ny*nz
    bsize = 40 + 6*ls + cells*nv*vs
    nblk = raw.shape[0]//bsize
    assert nblk*bsize == raw.shape[0], (fn, raw.shape[0], bsize)
    blocks = []
    for b in range(nblk):
        o = b*bsize
        lv = np.frombuffer(raw[o:o+40].tobytes(), dtype=np.int32)
        assert lv[9] == 0, "refined mesh not supported"
        xb = np.frombuffer(raw[o+40:o+40+6*ls].tobytes(), dtype=lt)
        blocks.append((o, lv[6:9].copy(), xb.copy()))
    lx = np.array([bl[1] for bl in blocks])
    NB = lx.max(0) + 1
    N = (NB[0]*nx, NB[1]*ny, NB[2]*nz)
    out = {n: np.empty((N[2], N[1], N[0]), dtype=np.float64) for n in names}
    for o, l, xb in blocks:
        d0 = o + 40 + 6*ls
        for n, iv in zip(names, idx):
            s = d0 + iv*cells*vs
            arr = np.frombuffer(raw[s:s+cells*vs].tobytes(), dtype=dt).reshape(nz, ny, nx)
            out[n][l[2]*nz:(l[2]+1)*nz, l[1]*ny:(l[1]+1)*ny, l[0]*nx:(l[0]+1)*nx] = arr
    x1 = [bl[2][0] for bl in blocks]
    x2 = [bl[2][1] for bl in blocks]
    h["x1min"], h["x1max"] = min(x1), max(x2)
    x3 = [bl[2][2] for bl in blocks]
    x4 = [bl[2][3] for bl in blocks]
    x5 = [bl[2][4] for bl in blocks]
    x6 = [bl[2][5] for bl in blocks]
    h["box"] = ((min(x1), max(x2)), (min(x3), max(x4)), (min(x5), max(x6)))
    h["N"] = N
    return out, h


# ---------------------------------------------------------------------------- particles
def read_snapshot(fn, fields=True):
    with open(fn, "rb") as f:
        magic = f.read(8)
        assert magic == b"NRPSNAP1", magic
        t = np.frombuffer(f.read(8), np.float64)[0]
        n = int(np.frombuffer(f.read(8), np.int64)[0])
        cyc = int(np.frombuffer(f.read(8), np.int64)[0])
        if not fields:
            return t, n, cyc
        rec = np.frombuffer(f.read(56*n), np.float64).reshape(n, 7)
        tag = np.frombuffer(f.read(4*n), np.int32)
        spec = np.frombuffer(f.read(4*n), np.int32)
        tau = np.frombuffer(f.read(8*n), np.float64)
    return {"t": float(t), "n": n, "cycle": cyc, "x": rec[:, 0:3].copy(),
            "u": rec[:, 3:6].copy(), "m": rec[:, 6].copy(), "tag": tag.copy(),
            "species": spec.copy(), "tau": tau.copy()}


# ------------------------------------------------------------------------------ history
def read_hst(fn, cols=None):
    """cols: column names to use when the file has no header line (a continuation)."""
    rows = []
    with open(fn) as f:
        for ln in f:
            if ln.startswith("#"):
                if "[1]=" in ln:
                    cols = [c.split("=", 1)[1] for c in re.findall(r"\[\d+\]=\S+", ln)]
                continue
            p = ln.split()
            if p:
                rows.append([float(v) for v in p])
    a = np.array(rows)
    assert cols is not None and len(cols) == a.shape[1], (fn, cols, a.shape)
    # a restart may repeat times: keep the last row of each time, in time order
    t = a[:, 0]
    keep = np.ones(len(t), bool)
    seen = {}
    for i, tv in enumerate(t):
        if tv in seen:
            keep[seen[tv]] = False
        seen[tv] = i
    a = a[keep]
    a = a[np.argsort(a[:, 0], kind="stable")]
    return {c: a[:, i] for i, c in enumerate(cols)}


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


# ------------------------------------------------------------------------------- TT
def kgrid(N, L, real=True):
    """Integer wave vectors (nx, ny, nz) of an rfftn over arrays [z, y, x]."""
    nz, ny, nx = N[2], N[1], N[0]
    kz = np.fft.fftfreq(nz, 1.0/nz)
    ky = np.fft.fftfreq(ny, 1.0/ny)
    kx = np.fft.rfftfreq(nx, 1.0/nx) if real else np.fft.fftfreq(nx, 1.0/nx)
    KZ, KY, KX = np.meshgrid(kz, ky, kx, indexing="ij")
    return KX, KY, KZ


COMP = (("xx", 0, 0), ("xy", 0, 1), ("xz", 0, 2), ("yy", 1, 1), ("yz", 1, 2), ("zz", 2, 2))


def tt_project(Fh, KX, KY, KZ):
    """Flat TT projection Lambda_ij,kl h_kl of Fourier coefficients Fh[(a, b)] (3x3 dict of
    arrays, symmetric). Returns a dict of the 6 independent components."""
    k = [KX, KY, KZ]
    k2 = KX**2 + KY**2 + KZ**2
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(k2 > 0, 1.0/k2, 0.0)
    P = [[(1.0 if i == j else 0.0) - k[i]*k[j]*inv for j in range(3)] for i in range(3)]
    H = [[Fh[min(i, j), max(i, j)] for j in range(3)] for i in range(3)]
    # Ph = P h P ; trace part tr(P h) P / 2
    PH = [[sum(P[i][l]*H[l][j] for l in range(3)) for j in range(3)] for i in range(3)]
    PHP = [[sum(PH[i][l]*P[l][j] for l in range(3)) for j in range(3)] for i in range(3)]
    tr = sum(P[i][j]*H[j][i] for i in range(3) for j in range(3))
    out = {}
    for _, i, j in COMP:
        v = PHP[i][j] - 0.5*P[i][j]*tr
        out[i, j] = np.where(k2 > 0, v, 0.0)
    return out


def rfft_weights(N):
    nx = N[0]
    w = np.full(nx//2 + 1, 2.0)
    w[0] = 1.0
    if nx % 2 == 0:
        w[-1] = 1.0
    return w


def tt_power(fields, L):
    """fields: dict (i, j) -> real array h_ij [z, y, x]. Returns (p, KX, KY, KZ, nyq) where
    p = sum_ab |h^TT_ab(k)|^2 w / Ntot^2 on the rfft half grid, so that sum(p) is the
    box mean of sum_ab (h^TT_ab)^2."""
    N = fields[0, 0].shape[::-1]
    KX, KY, KZ = kgrid(N, L)
    Fh = {key: np.fft.rfftn(fields[key]) for key in fields}
    T = tt_project(Fh, KX, KY, KZ)
    del Fh
    Ntot = float(np.prod(N))
    w = rfft_weights(N)[None, None, :]
    p = np.zeros(KX.shape)
    for _, i, j in COMP:
        mult = 1.0 if i == j else 2.0
        p += mult*np.abs(T[i, j])**2
    p *= w/Ntot**2
    nyq = (np.abs(KX) == N[0]//2) | (np.abs(KY) == N[1]//2) | (np.abs(KZ) == N[2]//2)
    return p, KX, KY, KZ, nyq


# ------------------------------------------------------------------------------ FoF
def fof(x, L, link):
    """Friends-of-friends labels with periodic box L and linking length link."""
    from scipy.spatial import cKDTree
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    xx = np.mod(x, L)
    xx[xx >= L] -= L
    tree = cKDTree(xx, boxsize=L)
    pairs = tree.query_pairs(link, output_type="ndarray")
    n = len(x)
    g = coo_matrix((np.ones(len(pairs), np.int8), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    ncomp, lab = connected_components(g, directed=False)
    return lab


def halo_counts(x, m, L, link, nmin):
    lab = fof(x, L, link)
    cnt = np.bincount(lab)
    msum = np.bincount(lab, weights=m)
    ids = np.nonzero(cnt >= nmin)[0]
    order = ids[np.argsort(-msum[ids])]
    return cnt[order], msum[order], lab, order
