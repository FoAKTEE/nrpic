"""Reader of AthenaK mesh output of type `bin` (athenak/src/outputs/binary.cpp), in
single precision (the default) and in double precision (`<outputN> double_precision =
true`, docs/FORMATS.md, "Mesh binary output in double precision").

File layout, little-endian:
    text lines   "Athena binary output version=1.1", "  size of preheader=5",
                 "  time=...", "  cycle=...", "  size of location=8",
                 "  size of variable=4" or "=8", "  number of variables=N",
                 "  variables:  name1  name2 ...", "  header offset=H"
    H bytes      parameter dump (text)
    per MeshBlock
        10 int32     ois oie ojs oje oks oke (indices within the MeshBlock, ghost cells
                     counted), lx1 lx2 lx3 (logical location), level above the root
        6 reals      x1min x1max x2min x2max x3min x3max of the MeshBlock
        N arrays     of (oke-oks+1)(oje-ojs+1)(oie-ois+1) values each, i fastest

`read_bin` returns the header and one array per variable; on a uniform mesh the
MeshBlocks are assembled into arrays of shape (nx3, nx2, nx1) (index order k, j, i, as
the code stores them).  The values keep the precision of the file: float32 files are
returned as float32 unless `dtype` is given.
"""
import numpy as np

__all__ = ["read_bin", "parse_params"]


def parse_params(text):
    """The parameter dump as {block: {name: value string}}."""
    blocks, cur = {}, None
    for line in text.splitlines():
        s = line.split("#")[0].strip()
        if not s:
            continue
        if s.startswith("<") and s.endswith(">"):
            cur = s[1:-1]
            blocks.setdefault(cur, {})
        elif "=" in s and cur is not None:
            k, v = s.split("=", 1)
            blocks[cur][k.strip()] = v.strip()
    return blocks


def read_bin(path, dtype=None, assemble=True):
    """Read one `bin` mesh output.

    Returns a dict with: time, cycle, variables (names), var_size (4 or 8), params
    (parameter dump), blocks (list of dicts: lloc, level, bounds, indices, data of shape
    (nvar, n3, n2, n1)), and, with assemble = True on a uniform mesh written without
    ghost cells and without slicing, one array (nx3, nx2, nx1) per variable name together
    with the cell-centre coordinates x1v, x2v, x3v."""
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
    vsize = int(info["size of variable"])
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
        xs = np.frombuffer(raw, ltype, 6, pos).astype(np.float64)
        pos += 6*lsize
        n1, n2, n3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = n1*n2*n3
        arr = np.frombuffer(raw, vtype, nvar*cnt, pos).reshape(nvar, n3, n2, n1)
        pos += vsize*nvar*cnt
        if dtype is not None:
            arr = arr.astype(dtype)
        blocks.append({"lloc": (lx1, lx2, lx3), "level": lev, "bounds": xs,
                       "indices": (ois, oie, ojs, oje, oks, oke), "data": arr})
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "variables": names,
           "var_size": vsize, "params": params, "blocks": blocks}
    if not assemble or not blocks:
        return out
    if any(b["level"] != blocks[0]["level"] for b in blocks):
        return out                         # refined mesh: the blocks are left as they are
    shp = blocks[0]["data"].shape[1:]
    if any(b["data"].shape[1:] != shp for b in blocks):
        return out
    b3, b2, b1 = shp
    m1 = max(b["lloc"][0] for b in blocks) + 1
    m2 = max(b["lloc"][1] for b in blocks) + 1
    m3 = max(b["lloc"][2] for b in blocks) + 1
    if len(blocks) != m1*m2*m3:
        return out                         # a slice or a single MeshBlock of several
    full = np.empty((nvar, m3*b3, m2*b2, m1*b1), dtype=blocks[0]["data"].dtype)
    lo = np.array([np.inf]*3)
    hi = np.array([-np.inf]*3)
    for b in blocks:
        l1, l2, l3 = b["lloc"]
        full[:, l3*b3:(l3 + 1)*b3, l2*b2:(l2 + 1)*b2, l1*b1:(l1 + 1)*b1] = b["data"]
        lo = np.minimum(lo, b["bounds"][0::2])
        hi = np.maximum(hi, b["bounds"][1::2])
    for i, n in enumerate(names):
        out[n] = full[i]
    nn = (m1*b1, m2*b2, m3*b3)
    for a in range(3):
        d = (hi[a] - lo[a])/nn[a]
        out[f"x{a + 1}v"] = lo[a] + (np.arange(nn[a]) + 0.5)*d
    out["xmin"], out["xmax"] = lo, hi
    return out
