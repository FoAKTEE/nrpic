"""verifier3's own readers and diagnostics (written from the format and the formulas, not
from gw_diag or waves/wlib).

Array layout: fields are indexed [i, j, k] = (x, y, z) after reading (array axis a is the
coordinate direction a); tensors T[a, b, i, j, k]. Cell centres x_i = xmin + (i + 1/2) h.

- read_bin(path): AthenaK binary mesh output (`Athena binary output version=1.1`), single
  or double precision (header "size of variable"), uniform mesh (level 0), any number of
  MeshBlocks; returns dict(time, cycle, vars{name: array}, grid, header, params).
- z4c_to_adm(d): gamma_ij, K_ij, alpha from the Z4c variables (chi_psi_power = -4:
  chi = det(gamma)^(-1/3), gt = chi gamma, At = chi (K_ij - gamma_ij K/3), K = Khat + 2 Theta;
  athenak/src/z4c/z4c_adm.cpp lines 72-99 and 216-234).
- tt_project(T, grid): Lambda_ij,lm = P_il P_jm - P_ij P_lm/2 mode by mode (k = 0 and the
  Nyquist planes removed).
- mode_coeff(f, grid, m): c with f = c exp(i K.x) + c.c. + other modes, K = 2 pi m / L.
- weyl_EB(gamma, K, grid): E_ij = TF[R_ij + K K_ij - K_ik K^k_j], B_ij = sym(eps_i^kl D_k K_lj)
  with spectral derivatives (no matter term: dust at rest has S_ij = 0 at first order).
- psi4(E, B, gamma, n): triad (n, u, v) of the fixed direction n, Gram-Schmidt with gamma in
  that order, mbar = (u - i v)/sqrt 2, Psi_4 = -(E - i B)_ij mbar^i mbar^j.
"""
import re

import numpy as np

import exact


# ------------------------------------------------------------------ reader
class Grid:
    def __init__(self, n, L, xmin):
        self.n = tuple(int(v) for v in n)
        self.L = np.asarray(L, float)
        self.xmin = np.asarray(xmin, float)
        self.h = self.L / np.asarray(self.n)

    def coords(self):
        ax = [self.xmin[a] + (np.arange(self.n[a]) + 0.5) * self.h[a] for a in range(3)]
        return np.meshgrid(*ax, indexing="ij")

    def kvecs(self, real=False):
        ks = []
        for a in range(3):
            if real and a == 2:
                k = 2 * np.pi * np.fft.rfftfreq(self.n[a], d=self.h[a])
            else:
                k = 2 * np.pi * np.fft.fftfreq(self.n[a], d=self.h[a])
            ks.append(k)
        return np.meshgrid(*ks, indexing="ij")


def _parse_params(text):
    params, block = {}, None
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"^<(.+)>$", line)
        if m:
            block = m.group(1)
            params.setdefault(block, {})
            continue
        if "=" in line and block is not None:
            k, v = line.split("=", 1)
            params[block][k.strip()] = v.strip()
    return params


def read_bin(path, want=None):
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    header = {}
    lines = []
    # text pre-header: lines until the 'variables:' line, then 'header offset=' line
    while True:
        e = raw.index(b"\n", pos)
        line = raw[pos:e].decode("ascii")
        pos = e + 1
        lines.append(line)
        if line.strip().startswith("header offset="):
            break
        if len(lines) > 20:
            raise ValueError(f"{path}: no 'header offset' line in the pre-header")
    if not lines[0].startswith("Athena binary output version=1.1"):
        raise ValueError(f"{path}: unknown format line {lines[0]!r}")
    for line in lines[1:]:
        s = line.strip()
        if s.startswith("variables:"):
            header["variables"] = s.split(":", 1)[1].split()
        elif "=" in s:
            k, v = s.split("=", 1)
            header[k.strip()] = v.strip()
    hoff = int(header["header offset"])
    partext = raw[pos:pos + hoff].decode("latin1")
    pos += hoff
    params = _parse_params(partext)
    loc = int(header["size of location"])
    var = int(header["size of variable"])
    nvar = int(header["number of variables"])
    names = header["variables"]
    if len(names) != nvar:
        raise ValueError(f"{path}: {nvar} variables announced, {len(names)} named")
    if loc != 8 or var not in (4, 8):
        raise ValueError(f"{path}: size of location {loc}, of variable {var}")
    mesh, mb = params["mesh"], params["meshblock"]
    n = [int(mesh[f"nx{a}"]) for a in (1, 2, 3)]
    xmin = [float(mesh[f"x{a}min"]) for a in (1, 2, 3)]
    xmax = [float(mesh[f"x{a}max"]) for a in (1, 2, 3)]
    nb = [int(mb[f"nx{a}"]) for a in (1, 2, 3)]
    cells = nb[0] * nb[1] * nb[2]
    bsize = 10 * 4 + 6 * 8 + cells * nvar * var
    rest = len(raw) - pos
    if rest % bsize != 0:
        raise ValueError(f"{path}: {rest} data bytes are not a multiple of the block size {bsize}")
    nblocks = rest // bsize
    expect = (n[0] // nb[0]) * (n[1] // nb[1]) * (n[2] // nb[2])
    if nblocks != expect:
        raise ValueError(f"{path}: {nblocks} blocks, a uniform mesh has {expect}")
    dt = np.dtype("<f4") if var == 4 else np.dtype("<f8")
    sel = names if want is None else [v for v in names if v in want]
    out = {v: np.full(n, np.nan) for v in sel}
    hcell = [(xmax[a] - xmin[a]) / n[a] for a in range(3)]
    for b in range(nblocks):
        p = pos + b * bsize
        ints = np.frombuffer(raw, "<i4", 10, p)
        xs = np.frombuffer(raw, "<f8", 6, p + 40)
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ints)
        if lev != 0:
            raise ValueError(f"{path}: refined block (level {lev}); only uniform meshes")
        if (oie - ois + 1, oje - ojs + 1, oke - oks + 1) != tuple(nb):
            raise ValueError(f"{path}: block extents differ from <meshblock>")
        # position from the coordinates (checked against the logical location)
        i0 = [int(round((xs[2 * a] - xmin[a]) / hcell[a])) for a in range(3)]
        if i0 != [lx1 * nb[0], lx2 * nb[1], lx3 * nb[2]]:
            raise ValueError(f"{path}: block {b}: coordinates and logical location disagree")
        data = np.frombuffer(raw, dt, cells * nvar, p + 88).reshape(nvar, nb[2], nb[1], nb[0])
        for iv, name in enumerate(names):
            if name in out:
                out[name][i0[0]:i0[0] + nb[0], i0[1]:i0[1] + nb[1], i0[2]:i0[2] + nb[2]] = \
                    data[iv].transpose(2, 1, 0)
    for v, arr in out.items():
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{path}: variable {v} not fully covered or not finite")
    grid = Grid(n, [xmax[a] - xmin[a] for a in range(3)], xmin)
    return {"time": float(header["time"]), "cycle": int(header["cycle"]), "vars": out,
            "grid": grid, "header": header, "params": params, "var_size": var,
            "nblocks": nblocks}


SYM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
CMP = ["xx", "xy", "xz", "yy", "yz", "zz"]


def sym_from(vars_, prefix):
    a0 = vars_[prefix + "xx"]
    T = np.empty((3, 3) + a0.shape)
    for (a, b), c in zip(SYM, CMP):
        T[a, b] = vars_[prefix + c]
        T[b, a] = T[a, b]
    return T


def z4c_to_adm(d):
    v = d["vars"]
    p = d["params"].get("z4c", {})
    if float(p.get("chi_psi_power", "-4")) != -4.0:
        raise ValueError("chi_psi_power other than -4 not supported")
    chi = v["z4c_chi"]
    gt = sym_from(v, "z4c_g")
    At = sym_from(v, "z4c_A")
    trK = v["z4c_Khat"] + 2.0 * v["z4c_Theta"]
    gam = gt / chi
    K = At / chi + gam * trK / 3.0
    return gam, K, v["z4c_alpha"], chi, gt, At, trK


# ------------------------------------------------------------------ Fourier tools
def mode_coeff(f, grid, m):
    """c in f = c exp(i K.x) + c.c. + ..., K = 2 pi m / L (absolute coordinates)."""
    F = np.fft.fftn(f, axes=(-3, -2, -1))
    idx = tuple(int(m[a]) % grid.n[a] for a in range(3))
    K = 2 * np.pi * np.asarray(m, float) / grid.L
    x0 = grid.xmin + 0.5 * grid.h
    return F[(Ellipsis,) + idx] / np.prod(grid.n) * np.exp(-1j * np.dot(K, x0))


def tt_project(T, grid):
    """Lambda projection of a symmetric tensor field T[a,b,...] (real)."""
    kx, ky, kz = grid.kvecs(real=True)
    k2 = kx ** 2 + ky ** 2 + kz ** 2
    kk = [kx, ky, kz]
    Tk = np.fft.rfftn(T, axes=(-3, -2, -1))
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(k2 > 0, 1.0 / k2, 0.0)
    P = np.empty((3, 3) + k2.shape)
    for a in range(3):
        for b in range(3):
            P[a, b] = (1.0 if a == b else 0.0) - kk[a] * kk[b] * inv
    # (P T P)_ij - (1/2) P_ij (P_lm T_lm)
    PT = np.einsum("il...,lj...->ij...", P, Tk)
    PTP = np.einsum("il...,lj...->ij...", PT, P)
    tr = np.einsum("lm...,lm...->...", P, Tk)
    out = PTP - 0.5 * P * tr
    # remove k = 0 and Nyquist planes
    mask = k2 > 0
    for a, n in enumerate(grid.n):
        if n % 2 == 0:
            kny = np.pi / grid.h[a]
            mask &= ~np.isclose(np.abs(kk[a]), kny)
    out = out * mask
    return np.fft.irfftn(out, s=grid.n, axes=(-3, -2, -1))


def dspec(f, grid, a):
    """spectral first derivative along axis a (Nyquist zeroed)."""
    kv = grid.kvecs(real=True)[a]
    F = np.fft.rfftn(f, axes=(-3, -2, -1))
    k = kv.copy()
    if grid.n[a] % 2 == 0:
        k[np.isclose(np.abs(k), np.pi / grid.h[a])] = 0.0
    return np.fft.irfftn(1j * k * F, s=grid.n, axes=(-3, -2, -1))


def dfd6(f, grid, a):
    """sixth-order centred first derivative along axis a (periodic)."""
    c = (3.0 / 4.0, -3.0 / 20.0, 1.0 / 60.0)
    ax = f.ndim - 3 + a
    out = np.zeros_like(f)
    for s, cs in enumerate(c, start=1):
        out += cs * (np.roll(f, -s, axis=ax) - np.roll(f, s, axis=ax))
    return out / grid.h[a]


def inv3(g):
    a, b, c = g[0, 0], g[0, 1], g[0, 2]
    d, e, f = g[1, 1], g[1, 2], g[2, 2]
    det = a * (d * f - e * e) - b * (b * f - e * c) + c * (b * e - d * c)
    gi = np.empty_like(g)
    gi[0, 0] = (d * f - e * e) / det
    gi[0, 1] = gi[1, 0] = (c * e - b * f) / det
    gi[0, 2] = gi[2, 0] = (b * e - c * d) / det
    gi[1, 1] = (a * f - c * c) / det
    gi[1, 2] = gi[2, 1] = (b * c - a * e) / det
    gi[2, 2] = (a * d - b * b) / det
    return gi, det


LC = np.zeros((3, 3, 3))
LC[0, 1, 2] = LC[1, 2, 0] = LC[2, 0, 1] = 1.0
LC[0, 2, 1] = LC[2, 1, 0] = LC[1, 0, 2] = -1.0


def weyl_EB(gam, K, grid, deriv="spectral"):
    D = dspec if deriv == "spectral" else dfd6
    gi, det = inv3(gam)
    dg = np.array([D(gam, grid, c) for c in range(3)])          # dg[c,a,b] = d_c g_ab
    # Gamma^k_ij = 1/2 g^kl (d_i g_lj + d_j g_li - d_l g_ij)
    Gl = 0.5 * (np.einsum("ilj...->lij...", dg) + np.einsum("jli...->lij...", dg) - dg)
    G = np.einsum("kl...,lij...->kij...", gi, Gl)
    dG = np.array([D(G, grid, c) for c in range(3)])            # dG[c,k,i,j]
    R = (np.einsum("kkij...->ij...", dG) - np.einsum("jkik...->ij...", dG)
         + np.einsum("kkl...,lij...->ij...", G, G) - np.einsum("kjl...,lik...->ij...", G, G))
    Kud = np.einsum("ik...,kj...->ij...", gi, K)
    trK = np.einsum("ii...->...", Kud)
    KK = np.einsum("ik...,kj...->ij...", K, Kud)
    M = R + trK * K - KK
    trM = np.einsum("ij...,ij...->...", gi, M)
    E = M - gam * trM / 3.0
    dK = np.array([D(K, grid, c) for c in range(3)])            # dK[k,l,j] = d_k K_lj
    DK = dK - np.einsum("mkl...,mj...->klj...", G, K) - np.einsum("mkj...,lm...->klj...", G, K)
    sq = np.sqrt(det)
    # eps_i^kl = g_im eps^mkl, eps^mkl = [mkl]/sqrt(g)
    eps_up = LC[:, :, :, None, None, None] / sq
    eps_i = np.einsum("im...,mkl...->ikl...", gam, eps_up)
    Bm = np.einsum("ikl...,klj...->ij...", eps_i, DK)
    B = 0.5 * (Bm + np.swapaxes(Bm, 0, 1))
    return E, B


def psi4(E, B, gam, n):
    """fixed-direction Psi_4 with the triad (n, theta-hat, phi-hat) of n, Gram-Schmidt in gamma."""
    nn, u, v = exact.sph_basis(n)
    shp = gam.shape[2:]
    vecs = [np.broadcast_to(w[:, None, None, None], (3,) + shp).astype(float) for w in (nn, u, v)]

    def dot(p, q):
        return np.einsum("i...,ij...,j...->...", p, gam, q)

    e = []
    for w in vecs:
        w = w.copy()
        for q in e:
            w = w - dot(w, q) * q
        w = w / np.sqrt(dot(w, w))
        e.append(w)
    mbar = (e[1] - 1j * e[2]) / np.sqrt(2.0)
    C = E - 1j * B
    return -np.einsum("ij...,i...,j...->...", C, mbar, mbar)


def pol_components(T, n):
    """(1/2) e+:T and (1/2) ex:T with the constant basis of direction n."""
    ep, ex, _, _, _ = exact.pol_tensors(n)
    return (0.5 * np.einsum("ab,ab...->...", ep, T), 0.5 * np.einsum("ab,ab...->...", ex, T))
