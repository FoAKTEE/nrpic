"""Own generator of the frozen mode amplitudes alpha_n of the stochastic sources (g1verify).

Specification read from coord/INTERFACES/rng.md sections 2-3 and the comments of
core/scalar-2:athenak/src/scalar_field/scalar_field_noise.cpp lines 9-22:
  alpha_n = (z1 + i z2)/sqrt(2), (z1, z2) = Normal2 of key
  {seed = <job> rng_seed, stream = Stream(3, 2^16 + dof), entity = CellEntity(n + 2^20),
   step = epoch = 0}, draw 0.
Philox-4x64-10 is written here vectorised in numpy (64 x 64 -> 128 bit products from
32-bit halves); it is checked against numpy.random.Philox (an independent implementation,
rng.md section 2) in check_infra.py.  The polar Box-Muller transform uses the disk point of
rng.md section 3; the logarithm is taken both with the AGM form of rng.hpp (bit-exact
intent) and with numpy.log (difference reported).
"""
import numpy as np

M32 = np.uint64(0xFFFFFFFF)
PH_M0 = np.uint64(0xD2E7470EE14C6C93)
PH_M1 = np.uint64(0xCA5A826395121157)
PH_W0 = np.uint64(0x9E3779B97F4A7C15)
PH_W1 = np.uint64(0xBB67AE8584CAA73B)


def _mulhilo(a, b):
    a = np.asarray(a, dtype=np.uint64)
    b = np.asarray(b, dtype=np.uint64)
    s32 = np.uint64(32)
    a0, a1 = a & M32, a >> s32
    b0, b1 = b & M32, b >> s32
    p00, p01, p10, p11 = a0 * b0, a0 * b1, a1 * b0, a1 * b1
    mid = (p00 >> s32) + (p01 & M32) + (p10 & M32)
    hi = p11 + (p01 >> s32) + (p10 >> s32) + (mid >> s32)
    lo = a * b
    return hi, lo


def philox4x64(c, k):
    """c: (4, n) uint64 counters, k: (2, n) or (2,) uint64 keys -> (4, n) words."""
    with np.errstate(over="ignore"):
        x0, x1, x2, x3 = [np.array(ci, dtype=np.uint64) for ci in c]
        k0 = np.array(k[0], dtype=np.uint64) + np.zeros_like(x0)
        k1 = np.array(k[1], dtype=np.uint64) + np.zeros_like(x0)
        for r in range(10):
            if r > 0:
                k0 = k0 + PH_W0
                k1 = k1 + PH_W1
            hi0, lo0 = _mulhilo(PH_M0, x0)
            hi1, lo1 = _mulhilo(PH_M1, x2)
            x0, x1, x2, x3 = hi1 ^ x1 ^ k0, lo1, hi0 ^ x3 ^ k1, lo0
    return np.array([x0, x1, x2, x3])


def stream(ident, sub):
    return (np.uint64(ident) << np.uint64(32)) | np.uint64(sub)


def cell_entity(i, j, k):
    i, j, k = (np.asarray(x, dtype=np.uint64) for x in (i, j, k))
    return i | (j << np.uint64(21)) | (k << np.uint64(42))


def neglog52_agm(s):
    """-ln(s 2^-52) by the AGM form of rng.hpp NegLog52 (vectorised)."""
    a = np.ones_like(s, dtype=np.float64)
    b = s.astype(np.float64) * 2.0 ** -82
    for _ in range(10):
        an = 0.5 * (a + b)
        b = np.sqrt(a * b)
        a = an
    big = float.fromhex("0x1.921fb54442d18p+0") / a
    l = big - float.fromhex("0x1.62e42fefa39efp+4")
    return np.where(l > 0.0, l, 0.0)


def normal2(seed, strm, entity, step=0, draw=0, use_agm=True):
    """Two standard normals per entity (vectorised over entity)."""
    entity = np.asarray(entity, dtype=np.uint64)
    n = entity.size
    z0 = np.zeros(n)
    z1 = np.zeros(n)
    done = np.zeros(n, dtype=bool)
    two26 = np.int64(1) << np.int64(26)
    two52 = np.int64(1) << np.int64(52)
    for blk in range(16):
        if done.all():
            break
        c3 = np.uint64((draw << 8) | (1 << 4) | blk)
        c = [entity, np.zeros(n, np.uint64), np.full(n, step, np.uint64), np.full(n, c3, np.uint64)]
        w = philox4x64(c, (np.uint64(seed), strm))
        for m in range(4):
            wm = w[m]
            v1 = 2 * (wm >> np.uint64(38)).astype(np.int64) + 1 - two26
            v2 = 2 * ((wm >> np.uint64(12)) & np.uint64(0x3FFFFFF)).astype(np.int64) + 1 - two26
            s = v1 * v1 + v2 * v2
            ok = (s < two52) & ~done
            if ok.any():
                L = neglog52_agm(s[ok]) if use_agm else -np.log(s[ok].astype(np.float64) * 2.0 ** -52)
                f = np.sqrt((2.0 * L) / s[ok].astype(np.float64))
                z0[ok] = v1[ok].astype(np.float64) * f
                z1[ok] = v2[ok].astype(np.float64) * f
                done |= ok
    return z0, z1


def hemisphere(nmax2):
    """Wave vectors of the half space (n_x > 0, or n_x = 0 and n_y > 0, or n_x = n_y = 0 and
    n_z > 0) with 0 < |n|^2 <= nmax2, ordered by n_x, n_y, n_z."""
    m = int(np.floor(np.sqrt(nmax2)))
    r = np.arange(-m, m + 1)
    nx, ny, nz = np.meshgrid(r, r, r, indexing="ij")
    nx, ny, nz = nx.ravel(), ny.ravel(), nz.ravel()
    n2 = nx * nx + ny * ny + nz * nz
    half = (nx > 0) | ((nx == 0) & (ny > 0)) | ((nx == 0) & (ny == 0) & (nz > 0))
    sel = half & (n2 > 0) & (n2 <= nmax2)
    return np.stack([nx[sel], ny[sel], nz[sel]], axis=1)


def alphas(n, seed, dof=0, epoch=0, use_agm=True):
    """alpha_n = (z1 + i z2)/sqrt(2) for wave vectors n (array (m, 3))."""
    off = 1 << 20
    ent = cell_entity(n[:, 0] + off, n[:, 1] + off, n[:, 2] + off)
    strm = stream(3, (1 << 16) | dof)
    z0, z1 = normal2(seed, strm, ent, step=epoch, draw=0, use_agm=use_agm)
    return (z0 + 1j * z1) * np.sqrt(0.5)
