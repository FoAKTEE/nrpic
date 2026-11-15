"""Reproducible random numbers: the NumPy twin of ``athenak/src/utils/rng.hpp``.

Every draw is a pure function of its key (seed, stream, entity, step, draw); for
identical keys the functions below return the same bits as the C++ header does inside
the code, on processors and on a card. All arguments broadcast against each other, so a
whole array of tags or cells is drawn in one call::

    from nrpic import rng
    key = dict(seed=1, stream=rng.stream(rng.STREAM_TESTS), entity=tags, step=ncycle)
    u = rng.uniform(draw=0, **key)            # in (0,1)
    z1, z2 = rng.normal2(draw=1, **key)       # two independent normal deviates
    n = rng.direction(draw=2, **key)          # shape (..., 3), isotropic unit vectors

The generator is Philox-4x64 with ten rounds, the function behind
``numpy.random.Philox``: ``words`` equals ``numpy.random.Philox(counter=c - 1,
key=k).random_raw(4)`` (NumPy increments the counter before it generates). Key and
counter layout, as in the header::

    key     = (seed, stream)
    counter = (entity, entity_hi, step, draw * 256 + kind * 16 + block)

The derived draws use only integer arithmetic, exact conversions and single correctly
rounded operations, in the same order as the header, and no library logarithm or
trigonometric function; see the header for the reasons. Rules for users and the registry
of streams: ``docs/RNG.md``.
"""
import numpy as np

# registry of streams (upper 32 bits of the stream word)
STREAM_INITIAL_DATA = 1
STREAM_COLLISIONS = 2
STREAM_STOCHASTIC = 3
STREAM_TESTS = 4

KIND_BITS = 0
KIND_NORMAL = 1
KIND_DIRECTION = 2

_M0 = np.uint64(0xD2E7470EE14C6C93)
_M1 = np.uint64(0xCA5A826395121157)
_W0 = np.uint64(0x9E3779B97F4A7C15)
_W1 = np.uint64(0xBB67AE8584CAA73B)
_MASK32 = np.uint64(0xFFFFFFFF)
_S32 = np.uint64(32)
_PI_HALF = float.fromhex("0x1.921fb54442d18p+0")
_LN2_32 = float.fromhex("0x1.62e42fefa39efp+4")
_MAX_BLOCK = 16


def _u64(x):
    """Unsigned 64-bit array (at least one dimension) of non-negative integers."""
    a = np.asarray(x)
    if a.dtype == np.uint64:
        return np.atleast_1d(a)
    if a.dtype == object or a.dtype.kind not in "iub":
        return np.atleast_1d(np.array(x, dtype=np.uint64))
    if a.dtype.kind == "i" and a.size and a.min() < 0:
        raise ValueError("a field of a random-number key is negative")
    return np.atleast_1d(a.astype(np.uint64))


def stream(ident, sub=0):
    """Stream word: registered identifier in the upper 32 bits, sub-stream below."""
    return (_u64(ident) << _S32) | _u64(sub)


def cell_entity(i, j, k):
    """Entity of a cell from its global indices on its own refinement level (each
    below 2**21); the level relative to the root mesh belongs in ``entity_hi``."""
    return _u64(i) | (_u64(j) << np.uint64(21)) | (_u64(k) << np.uint64(42))


def mulhi64(a, b):
    """Upper 64 bits of the 128-bit product of unsigned 64-bit integers."""
    a = _u64(a)
    b = _u64(b)
    a0 = a & _MASK32
    a1 = a >> _S32
    b0 = b & _MASK32
    b1 = b >> _S32
    p00 = a0 * b0
    p01 = a0 * b1
    p10 = a1 * b0
    p11 = a1 * b1
    mid = (p00 >> _S32) + (p01 & _MASK32) + (p10 & _MASK32)
    return p11 + (p01 >> _S32) + (p10 >> _S32) + (mid >> _S32)


def philox4x64(c0, c1, c2, c3, k0, k1):
    """Philox-4x64-10 of the counter (c0..c3) under the key (k0, k1): four arrays."""
    x0, x1, x2, x3, k0, k1 = np.broadcast_arrays(*(_u64(v) for v in
                                                   (c0, c1, c2, c3, k0, k1)))
    k0 = k0.copy()
    k1 = k1.copy()
    with np.errstate(over="ignore"):
        for n in range(10):
            if n > 0:
                k0 += _W0
                k1 += _W1
            hi0 = mulhi64(_M0, x0)
            lo0 = _M0 * x0
            hi1 = mulhi64(_M1, x2)
            lo1 = _M1 * x2
            x0, x1, x2, x3 = hi1 ^ x1 ^ k0, lo1, hi0 ^ x3 ^ k1, lo0
    return x0, x1, x2, x3


def words(seed, stream, entity, step, draw, entity_hi=0, kind=KIND_BITS, block=0):
    """The four 64-bit words of one generator call: array of shape (..., 4)."""
    draw = _u64(draw)
    if draw.size and int(draw.max()) >= 1 << 56:
        raise ValueError("draw index must be below 2**56")
    last = (draw << np.uint64(8)) | (_u64(kind) << np.uint64(4)) | _u64(block)
    return np.stack(philox4x64(entity, entity_hi, step, last, seed, stream), axis=-1)


def bits4(seed, stream, entity, step, draw, entity_hi=0):
    """Four independent raw words of the draw: uint64 array of shape (..., 4)."""
    return words(seed, stream, entity, step, draw, entity_hi)


def bits(seed, stream, entity, step, draw, entity_hi=0):
    """First raw word of the draw."""
    return words(seed, stream, entity, step, draw, entity_hi)[..., 0]


def to_uniform(w):
    """(n + 1/2) 2**-52 with n the upper 52 bits of the word: exact, in (0,1)."""
    return ((_u64(w) >> np.uint64(12)).astype(np.float64) + 0.5) * 2.0**-52


def uniform(seed, stream, entity, step, draw, entity_hi=0):
    """Uniform deviate in the open interval (0,1)."""
    return to_uniform(bits(seed, stream, entity, step, draw, entity_hi))


def uniform4(seed, stream, entity, step, draw, entity_hi=0):
    """Four independent uniform deviates in (0,1): array of shape (..., 4)."""
    return to_uniform(words(seed, stream, entity, step, draw, entity_hi))


def index(seed, stream, entity, step, draw, n, entity_hi=0):
    """Integer in [0, n) (multiply-shift of the first word of the draw)."""
    return mulhi64(bits(seed, stream, entity, step, draw, entity_hi), n)


def _disk(seed, stream, entity, step, draw, entity_hi, kind):
    """First accepted lattice point of the rejection step for every key: integers
    v1, v2 (odd, |v| < 2**26) and s = v1**2 + v2**2 < 2**52, and the common shape."""
    arrs = np.broadcast_arrays(*(_u64(v) for v in (seed, stream, entity, step, draw,
                                                   entity_hi)))
    shape = arrs[0].shape
    seed, stream, entity, step, draw, entity_hi = (a.ravel() for a in arrs)
    n = seed.size
    v1 = np.zeros(n, dtype=np.int64)
    v2 = np.zeros(n, dtype=np.int64)
    s = np.zeros(n, dtype=np.int64)
    todo = np.arange(n)
    half = np.int64(1) << np.int64(26)
    for block in range(_MAX_BLOCK):
        if todo.size == 0:
            break
        w = words(seed[todo], stream[todo], entity[todo], step[todo], draw[todo],
                  entity_hi[todo], kind, block)
        pending = np.ones(todo.size, dtype=bool)
        for m in range(4):
            wm = w[:, m]
            a = 2 * (wm >> np.uint64(38)).astype(np.int64) + 1 - half
            b = 2 * ((wm >> np.uint64(12)) & np.uint64(0x3FFFFFF)).astype(np.int64) \
                + 1 - half
            ss = a * a + b * b
            ok = pending & (ss < (np.int64(1) << np.int64(52)))
            v1[todo[ok]] = a[ok]
            v2[todo[ok]] = b[ok]
            s[todo[ok]] = ss[ok]
            pending &= ~ok
        todo = todo[pending]
    return v1, v2, s, todo, shape


def neg_log52(s):
    """-ln(s 2**-52) for integers 0 < s < 2**52 from the arithmetic-geometric mean,
    with the operations of ``NegLog52`` in the header."""
    a = np.ones(np.shape(s), dtype=np.float64)
    b = np.asarray(s).astype(np.float64) * 2.0**-82
    for _ in range(10):
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    big = _PI_HALF / a
    val = big - _LN2_32
    return np.where(val > 0.0, val, 0.0)


def normal2(seed, stream, entity, step, draw, entity_hi=0):
    """Two independent standard normal deviates per key (polar Box-Muller)."""
    v1, v2, s, failed, shape = _disk(seed, stream, entity, step, draw, entity_hi,
                                     KIND_NORMAL)
    s[failed] = 2            # placeholder, overwritten below (probability 1e-43)
    f = np.sqrt((2.0 * neg_log52(s)) / s.astype(np.float64))
    z1 = v1.astype(np.float64) * f
    z2 = v2.astype(np.float64) * f
    z1[failed] = 0.0
    z2[failed] = 0.0
    return z1.reshape(shape), z2.reshape(shape)


def normal(seed, stream, entity, step, draw, entity_hi=0):
    """One standard normal deviate per key (the first of the pair of the draw)."""
    return normal2(seed, stream, entity, step, draw, entity_hi)[0]


def direction(seed, stream, entity, step, draw, entity_hi=0):
    """Isotropic unit vectors: array of shape (..., 3)."""
    v1, v2, s, failed, shape = _disk(seed, stream, entity, step, draw, entity_hi,
                                     KIND_DIRECTION)
    sr = s.astype(np.float64) * 2.0**-52
    h = np.sqrt(1.0 - sr)
    n = np.empty((s.size, 3), dtype=np.float64)
    n[:, 0] = (v1.astype(np.float64) * 2.0**-25) * h
    n[:, 1] = (v2.astype(np.float64) * 2.0**-25) * h
    n[:, 2] = 1.0 - 2.0 * sr
    n[failed] = (0.0, 0.0, 1.0)
    return n.reshape(shape + (3,))


def numpy_philox_words(c, k):
    """The same four words from ``numpy.random.Philox`` (an independent implementation),
    for one counter c (four integers) and one key k (two integers)."""
    cint = sum(int(v) << (64 * i) for i, v in enumerate(c))
    cint = (cint - 1) % (1 << 256)
    carr = np.array([(cint >> (64 * i)) & ((1 << 64) - 1) for i in range(4)],
                    dtype=np.uint64)
    bg = np.random.Philox(counter=carr, key=np.array([int(v) for v in k],
                                                      dtype=np.uint64))
    return bg.random_raw(4)
