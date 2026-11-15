#!/usr/bin/env python3
"""Keys for the agreement test of the random-number interface.

Writes the key file read by the problem generator ``rng_test`` (8 bytes "NRRNGKY1",
int64 N, N records of 6 uint64: seed, stream, entity, entity_hi, step, draw): edge cases
of every field, runs of consecutive values of every field, the registered streams, and
random keys.

Usage: make_keys.py <out.bin> [number of random keys = 200000]
"""
import sys

import numpy as np

MAX = (1 << 64) - 1
DRAW_MAX = (1 << 56) - 1


def main():
    out = sys.argv[1]
    nrand = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    keys = []
    # all fields zero, all fields at their largest value
    keys.append([0, 0, 0, 0, 0, 0])
    keys.append([MAX, MAX, MAX, MAX, MAX, DRAW_MAX])
    # one field at a time: 1, the top bit, the largest value, every single bit
    for f in range(6):
        top = DRAW_MAX if f == 5 else MAX
        nbit = 56 if f == 5 else 64
        for v in [1, 1 << (nbit - 1), top] + [1 << b for b in range(nbit)]:
            k = [0, 0, 0, 0, 0, 0]
            k[f] = v
            keys.append(k)
    # runs of 256 consecutive values of each field around a typical key
    base = [20261115, (4 << 32) | 0, 1000, 0, 500, 0]
    for f in range(6):
        for v in range(256):
            k = list(base)
            k[f] = base[f] + v
            keys.append(k)
    # the registered streams with sub-streams
    for ident in range(1, 9):
        for sub in range(16):
            keys.append([1, (ident << 32) | sub, 12345, 0, 0, 0])
    # 32-bit boundaries of the entity and the step (tags and cycle numbers are int)
    for v in [2**31 - 1, 2**31, 2**32 - 1, 2**32, 2**32 + 1]:
        keys.append([1, 4 << 32, v, 0, 0, 0])
        keys.append([1, 4 << 32, 0, 0, v, 0])
    keys = np.array(keys, dtype=np.uint64)
    gen = np.random.default_rng(20261115)
    rnd = gen.integers(0, 1 << 64, size=(nrand, 6), dtype=np.uint64, endpoint=False)
    rnd[:, 5] &= np.uint64(DRAW_MAX)
    # half of the random keys with small fields, as in a run
    small = gen.integers(0, 1 << 20, size=(nrand // 2, 6), dtype=np.uint64)
    small[:, 1] = (np.uint64(4) << np.uint64(32)) | (small[:, 1] & np.uint64(15))
    small[:, 3] = 0
    small[:, 5] &= np.uint64(15)
    rnd[: nrand // 2] = small
    keys = np.concatenate([keys, rnd])
    with open(out, "wb") as fp:
        fp.write(b"NRRNGKY1")
        fp.write(np.int64(keys.shape[0]).tobytes())
        fp.write(np.ascontiguousarray(keys).tobytes())
    print(f"wrote {keys.shape[0]} keys to {out}")


if __name__ == "__main__":
    main()
