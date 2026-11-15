"""Minimal reader of AthenaK mesh binary output, written for the lead's wave-2 review.

Independent of gw_diag's reader: the layout is taken from athenak/src/outputs/binary.cpp
(lines 125-232: per MeshBlock 10 int32, 6 Real, then nvar * cells values of the size given
by the header line "size of variable"), and the blocks are placed by their coordinate
bounds (x1min, x2min, x3min), not by their logical location.
"""
import numpy as np


def read(path, want=None):
    """Return dict with time, cycle, names, L (box lengths), xmin, n (nx1, nx2, nx3) and
    one float64 array [k, j, i] per requested variable (all if want is None)."""
    raw = np.fromfile(path, dtype=np.uint8).tobytes()
    pos, info, names = 0, {}, None
    while True:
        e = raw.index(b"\n", pos)
        line = raw[pos:e].decode()
        pos = e + 1
        if "variables:" in line:
            names = line.split("variables:")[1].split()
        elif "header offset=" in line:
            hoff = int(line.split("=")[1])
            break
        elif "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip()
    pos += hoff
    lsize = int(info["size of location"])
    vsize = int(info["size of variable"])
    rt = np.float64 if lsize == 8 else np.float32
    vt = np.float64 if vsize == 8 else np.float32
    nvar = len(names)
    want = names if want is None else list(want)
    idx = [names.index(w) for w in want]
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos); pos += 40
        ois, oie, ojs, oje, oks, oke = (int(v) for v in ii[:6])
        lev = int(ii[9])
        xs = np.frombuffer(raw, rt, 6, pos); pos += 6 * lsize
        n1, n2, n3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = n1 * n2 * n3
        arr = np.frombuffer(raw, vt, nvar * cnt, pos).reshape(nvar, n3, n2, n1)
        pos += vsize * nvar * cnt
        blocks.append((lev, xs, arr[idx]))
    if len({b[0] for b in blocks}) != 1:
        raise ValueError("refined mesh: not supported")
    x1lo = min(b[1][0] for b in blocks); x1hi = max(b[1][1] for b in blocks)
    x2lo = min(b[1][2] for b in blocks); x2hi = max(b[1][3] for b in blocks)
    x3lo = min(b[1][4] for b in blocks); x3hi = max(b[1][5] for b in blocks)
    b3, b2, b1 = blocks[0][2].shape[1:]
    w1 = blocks[0][1][1] - blocks[0][1][0]
    w2 = blocks[0][1][3] - blocks[0][1][2]
    w3 = blocks[0][1][5] - blocks[0][1][4]
    m1 = int(round((x1hi - x1lo) / w1)); m2 = int(round((x2hi - x2lo) / w2))
    m3 = int(round((x3hi - x3lo) / w3))
    full = np.empty((len(want), m3 * b3, m2 * b2, m1 * b1))
    for _, xs, arr in blocks:
        i = int(round((xs[0] - x1lo) / w1)); j = int(round((xs[2] - x2lo) / w2))
        k = int(round((xs[4] - x3lo) / w3))
        full[:, k * b3:(k + 1) * b3, j * b2:(j + 1) * b2, i * b1:(i + 1) * b1] = arr
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "names": names,
           "L": (x1hi - x1lo, x2hi - x2lo, x3hi - x3lo), "xmin": (x1lo, x2lo, x3lo),
           "n": (m1 * b1, m2 * b2, m3 * b3), "vsize": vsize}
    for w, a in zip(want, full):
        out[w] = a
    return out
