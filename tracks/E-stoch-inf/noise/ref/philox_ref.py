"""Independent re-implementation of the draws of the random-number interface (E-pre-4).

Written from the interface document of core (`tracks/core/interfaces/rng.md` on branch
`core/rng`, sections 2 and 3), not from core's twin `python/nrpic/rng.py`:

  key     = (seed, stream),  stream = (identifier << 32) | sub-stream
  counter = (entity, entity_hi, step, draw * 256 + kind * 16 + block)

The four 64-bit words of one call come from `numpy.random.Philox` (Philox-4x64-10), which
rng.md names as an independent implementation: NumPy increments the counter before it
generates, so the generator is started at counter - 1, and consecutive entities are
consecutive counters (entity is the lowest counter word), which lets one generator object
produce a whole row of modes.

Normal pair (kind 1): for each word w in order, v1 = 2 (w >> 38) + 1 - 2^26,
v2 = 2 ((w >> 12) & (2^26 - 1)) + 1 - 2^26, accepted if s = v1^2 + v2^2 < 2^52; the four
words of a call are tried in order, then block 1, 2, ...;  z_i = v_i sqrt(2 L / s),
L = -ln(s 2^-52). Two ways of computing L: "agm", the documented arithmetic-geometric
mean (ten steps on (1, s 2^-82), pi/2 over the mean minus 32 ln 2, clamped at zero), and
"libm", NumPy's logarithm (for the cross-check only).

Keys of the noise (NOISE_SPEC.md, section 4): stream = (3 << 32) | (1 << 16) | dof,
entity = (nx + 2^20) | (ny + 2^20) << 21 | (nz + 2^20) << 42, entity_hi = 0, step = epoch,
draw = 0.
"""
import numpy as np

STREAM_STOCHASTIC = 3
MODE_FLAG = 1 << 16
OFFSET = 1 << 20
KIND_NORMAL = 1
MAX_BLOCK = 16
_PI_HALF = float.fromhex("0x1.921fb54442d18p+0")    # pi/2 correctly rounded
_LN2_32 = float.fromhex("0x1.62e42fefa39efp+4")     # 32 ln 2 correctly rounded
_M26 = (1 << 26) - 1


def stream_word(ident, sub):
    return (int(ident) << 32) | int(sub)


def noise_stream(dof):
    """Stream word of the mode amplitudes of degree of freedom `dof`."""
    if not 0 <= dof < MODE_FLAG:
        raise ValueError("dof out of range")
    return stream_word(STREAM_STOCHASTIC, MODE_FLAG | dof)


def mode_entity(n):
    """Entity word of integer wave vectors n (array (..., 3), |n_i| < 2^20)."""
    n = np.asarray(n, dtype=np.int64)
    if np.any(np.abs(n) >= OFFSET):
        raise ValueError("wave number beyond 2^20")
    u = (n + OFFSET).astype(np.uint64)
    return u[..., 0] | (u[..., 1] << np.uint64(21)) | (u[..., 2] << np.uint64(42))


def _words_row(seed, stream, c0_start, count, c1, c2, c3):
    """Words of `count` consecutive counters (c0_start + i, c1, c2, c3): (count, 4)."""
    if c0_start < 1:
        raise ValueError("entity 0 needs a borrow; not used by the noise keys")
    bg = np.random.Philox(counter=np.array([c0_start - 1, c1, c2, c3], dtype=np.uint64),
                          key=np.array([seed, stream], dtype=np.uint64))
    return bg.random_raw(4 * count).reshape(count, 4)


def words(seed, stream, entity, step, draw, kind, block, entity_hi=0):
    """Four words for every entity of a 1-d uint64 array (any order): (len, 4).
    Runs of consecutive entities are produced by one generator object."""
    entity = np.asarray(entity, dtype=np.uint64)
    order = np.argsort(entity, kind="stable")
    e = entity[order]
    out = np.empty((e.size, 4), dtype=np.uint64)
    c3 = (int(draw) << 8) | (int(kind) << 4) | int(block)
    if e.size:
        brk = np.nonzero(np.diff(e) != 1)[0] + 1
        starts = np.concatenate([[0], brk])
        ends = np.concatenate([brk, [e.size]])
        for a, b in zip(starts, ends):
            out[a:b] = _words_row(int(seed), int(stream), int(e[a]), int(b - a),
                                  int(entity_hi), int(step), c3)
    res = np.empty_like(out)
    res[order] = out
    return res


def neg_log52(s, method="agm"):
    """L = -ln(s 2^-52) for integers 0 < s < 2^52."""
    s = np.asarray(s)
    if method == "libm":
        return -np.log(s.astype(np.float64) * 2.0**-52)
    a = np.ones(s.shape, dtype=np.float64)
    b = s.astype(np.float64) * 2.0**-82
    for _ in range(10):
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    val = _PI_HALF / a - _LN2_32
    return np.where(val > 0.0, val, 0.0)


def normal2(seed, stream, entity, step, draw=0, entity_hi=0, log="agm"):
    """Two standard normal deviates per entity (polar method on the lattice disk)."""
    entity = np.atleast_1d(np.asarray(entity, dtype=np.uint64))
    n = entity.size
    v1 = np.zeros(n, dtype=np.int64)
    v2 = np.zeros(n, dtype=np.int64)
    s = np.zeros(n, dtype=np.int64)
    todo = np.arange(n)
    half = np.int64(1) << np.int64(26)
    for block in range(MAX_BLOCK):
        if todo.size == 0:
            break
        w = words(seed, stream, entity[todo], step, draw, KIND_NORMAL, block, entity_hi)
        pending = np.ones(todo.size, dtype=bool)
        for m in range(4):
            wm = w[:, m]
            a = 2 * (wm >> np.uint64(38)).astype(np.int64) + 1 - half
            b = 2 * ((wm >> np.uint64(12)) & np.uint64(_M26)).astype(np.int64) + 1 - half
            ss = a * a + b * b
            ok = pending & (ss < (np.int64(1) << np.int64(52)))
            v1[todo[ok]] = a[ok]
            v2[todo[ok]] = b[ok]
            s[todo[ok]] = ss[ok]
            pending &= ~ok
        todo = todo[pending]
    if todo.size:
        raise RuntimeError("rejection failed 64 times (probability 1e-43)")
    f = np.sqrt((2.0 * neg_log52(s, log)) / s.astype(np.float64))
    return v1.astype(np.float64) * f, v2.astype(np.float64) * f


def mode_alpha(seed, dof, epoch, n, log="agm"):
    """Complex unit Gaussian alpha = (z1 + i z2)/sqrt(2) for wave vectors n (M, 3)."""
    z1, z2 = normal2(seed, noise_stream(dof), mode_entity(n), epoch, 0, 0, log)
    return (z1 + 1j * z2) / np.sqrt(2.0)
