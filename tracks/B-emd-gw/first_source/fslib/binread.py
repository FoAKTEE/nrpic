"""Reader of AthenaK `bin` mesh output in single and in double precision.

gw_diag's readers.read_bin reads the values as float32 whatever the header says; the
card executable of core/requests-b writes `double_precision = true` files with the header
line "size of variable=8" (layout: athenak/src/outputs/binary.cpp of that branch, lines
78-79 and 222; per MeshBlock 10 int32, 6 location reals of "size of location", then the
variables with "size of variable" bytes each, i fastest). This reader follows the header.
For single-precision files it returns the same arrays as gw_diag's reader (test in
tests/test_binread.py). Returns: time, cycle, variables, params, grid, var_size and one
float64 array (nz, ny, nx) per variable.
"""
import numpy as np

from gwdiag.grid import Grid
from gwdiag.readers import parse_params


def read_bin(path):
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    info, names, hoff = {}, None, None
    while True:
        e = raw.index(b"\n", pos)
        line = raw[pos:e].decode()
        pos = e + 1
        if "variables:" in line:
            names = line.split("variables:")[1].split()
        elif "header offset" in line:
            hoff = int(line.split("=")[1])
            break
        elif "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip()
    params = parse_params(raw[pos:pos + hoff].decode(errors="replace"))
    pos += hoff
    lsize = int(info["size of location"])
    vsize = int(info.get("size of variable", "4"))
    if lsize not in (4, 8) or vsize not in (4, 8):
        raise ValueError(f"{path}: unsupported sizes {lsize}, {vsize}")
    ltype = np.float64 if lsize == 8 else np.float32
    vtype = np.float64 if vsize == 8 else np.float32
    nvar = len(names)
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos)
        pos += 40
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ii)
        pos += 6 * lsize                                   # location of the MeshBlock
        nx1, nx2, nx3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = nx1 * nx2 * nx3
        arr = np.frombuffer(raw, vtype, nvar * cnt, pos).reshape(nvar, nx3, nx2, nx1)
        pos += vsize * nvar * cnt
        blocks.append(((lx1, lx2, lx3, lev), arr))
    if any(b[0][3] != blocks[0][0][3] for b in blocks):
        raise ValueError(f"{path}: refined mesh; only uniform meshes are assembled")
    del ltype
    bn3, bn2, bn1 = blocks[0][1].shape[1:]
    m1 = max(b[0][0] for b in blocks) + 1
    m2 = max(b[0][1] for b in blocks) + 1
    m3 = max(b[0][2] for b in blocks) + 1
    full = np.empty((nvar, m3 * bn3, m2 * bn2, m1 * bn1))
    for (l1, l2, l3, _), arr in blocks:
        full[:, l3 * bn3:(l3 + 1) * bn3, l2 * bn2:(l2 + 1) * bn2, l1 * bn1:(l1 + 1) * bn1] = arr
    mesh = params.get("mesh", {})
    lo = [float(mesh[f"x{a}min"]) for a in (1, 2, 3)]
    hi = [float(mesh[f"x{a}max"]) for a in (1, 2, 3)]
    grid = Grid((m1 * bn1, m2 * bn2, m3 * bn3), [h - l for h, l in zip(hi, lo)], lo)
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "variables": names,
           "params": params, "grid": grid, "var_size": vsize}
    for i, n in enumerate(names):
        out[n] = full[i]
    return out
