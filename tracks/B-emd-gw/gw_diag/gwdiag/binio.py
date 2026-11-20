"""Reader of AthenaK binary mesh output (`file_type = bin`) in single AND double precision.

Wave 3 (2026-11-20): merges the two readers that grew outside gw_diag,
`waves/wlib/measure.read_bin` and `first_source/fslib/binread.read_bin` (G1 OPEN item 9,
first_source request 1 and 8). `readers.read_bin` keeps its old behaviour (values read as
float32 whatever the header says); use this module for every new analysis.

Layout (athenak/src/outputs/binary.cpp; core/requests-b adds `<outputN> double_precision =
true`, lines 78-79 and 222 of that branch, READY item 2):
  text preheader: "Athena binary output version=...", "size of preheader=5", "time=",
  "cycle=", "size of location=<bytes of Real>", ["size of variable=<4|8>" (absent in files
  of the release: 4)], "number of variables=", "variables: <names>", "header offset=<n>";
  then <n> bytes of the parameter dump; then per written MeshBlock: 10 int32 (ois oie ojs
  oje oks oke: the block-local index range written, lx1 lx2 lx3 level), 6 location values
  (x1min x1max x2min x2max x3min x3max of the MeshBlock, "size of location" bytes each), and
  the values var[nvar][n3][n2][n1] ("size of variable" bytes each, i fastest), no ghosts.
Slices (`slice_x1/x2/x3`) and partial outputs write only the MeshBlocks they touch and only
the written index range; the blocks are placed by their logical location and index range.

read_bin(path, strip_prefix=False) -> dict with
  time, cycle, variables (names as in the file), params ({block: {name: value}}),
  var_size, loc_size (bytes), nblocks, index_offset (global cell index of element [0,0,0]
  as (i, j, k)), shape (nz, ny, nx), full_mesh (True when the arrays cover the whole mesh),
  grid (gwdiag Grid when full_mesh, else None), x1v, x2v, x3v (cell centres of the
  assembled arrays), chi_psi_power (when the file has a <z4c> block), and one float64
  array (nz, ny, nx) per variable. strip_prefix=True removes "z4c_" from the names (then
  readers.z4c_tensors and readers.z4c_to_adm take the dict directly); a string removes that
  prefix instead. Single-precision values are converted exactly (float32 -> float64).
Only meshes without refinement are assembled (all blocks on one level).
"""
import numpy as np

from .grid import Grid
from .readers import parse_params


def _header(raw):
    pos, info, names, hoff = 0, {}, None, None
    while True:
        e = raw.index(b"\n", pos)
        line = raw[pos:e].decode(errors="replace")
        pos = e + 1
        if "variables:" in line:
            names = line.split("variables:")[1].split()
        elif "header offset" in line:
            hoff = int(line.split("=")[1])
            break
        elif "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip()
    if names is None or hoff is None:
        raise ValueError("not an AthenaK binary output (no variables or header offset)")
    return info, names, hoff, pos


def read_bin(path, strip_prefix=False):
    with open(path, "rb") as f:
        raw = f.read()
    info, names, hoff, pos = _header(raw)
    params = parse_params(raw[pos:pos + hoff].decode(errors="replace"))
    pos += hoff
    lsize = int(info["size of location"])
    vsize = int(info.get("size of variable", "4"))
    if lsize not in (4, 8) or vsize not in (4, 8):
        raise ValueError(f"{path}: unsupported sizes (location {lsize}, variable {vsize})")
    ltype = np.float64 if lsize == 8 else np.float32
    vtype = np.float64 if vsize == 8 else np.float32
    nvar = len(names)
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos)
        pos += 40
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ii)
        xs = np.frombuffer(raw, ltype, 6, pos).astype(float)
        pos += 6 * lsize
        n1, n2, n3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = n1 * n2 * n3
        if pos + vsize * nvar * cnt > len(raw):
            raise ValueError(f"{path}: truncated MeshBlock data")
        arr = np.frombuffer(raw, vtype, nvar * cnt, pos).reshape(nvar, n3, n2, n1)
        pos += vsize * nvar * cnt
        blocks.append({"lloc": (lx1, lx2, lx3), "level": lev, "o": (ois, ojs, oks),
                       "n": (n1, n2, n3), "xs": xs, "data": arr})
    if not blocks:
        raise ValueError(f"{path}: no MeshBlock data")
    if any(b["level"] != blocks[0]["level"] for b in blocks):
        raise ValueError(f"{path}: refined mesh; only uniform meshes are assembled")
    mesh = params.get("mesh", {})
    mb = params.get("meshblock", {})
    ng = int(mesh.get("nghost", "0"))
    # cells per MeshBlock along each axis (a 2D or 1D mesh has one cell and no ghosts there)
    bn = []
    for a, key in enumerate(("nx1", "nx2", "nx3")):
        if key in mb:
            bn.append(int(mb[key]))
        elif key in mesh and all(b["lloc"][a] == 0 for b in blocks):
            bn.append(int(mesh[key]))
        else:
            bn.append(max(b["n"][a] for b in blocks))
    gh = [ng if v > 1 else 0 for v in bn]
    # global index of the first written cell of each block
    starts = []
    for b in blocks:
        st = []
        for a in range(3):
            loc = b["o"][a] - gh[a]
            if b["n"][a] == bn[a]:
                loc = 0                       # whole block written along this axis
            st.append(b["lloc"][a] * bn[a] + loc)
        starts.append(st)
    lo = [min(s[a] for s in starts) for a in range(3)]
    hi = [max(s[a] + b["n"][a] for s, b in zip(starts, blocks)) for a in range(3)]
    shape = (hi[2] - lo[2], hi[1] - lo[1], hi[0] - lo[0])
    full = np.full((nvar,) + shape, np.nan)
    for s, b in zip(starts, blocks):
        i0, j0, k0 = (s[a] - lo[a] for a in range(3))
        n1, n2, n3 = b["n"]
        full[:, k0:k0 + n3, j0:j0 + n2, i0:i0 + n1] = b["data"]
    if np.isnan(full).any():
        raise ValueError(f"{path}: the written blocks do not tile a box")
    try:
        nmesh = [int(mesh[f"nx{a}"]) for a in (1, 2, 3)]
        xmin = [float(mesh[f"x{a}min"]) for a in (1, 2, 3)]
        xmax = [float(mesh[f"x{a}max"]) for a in (1, 2, 3)]
    except KeyError:
        nmesh = xmin = xmax = None
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "variables": names,
           "params": params, "var_size": vsize, "loc_size": lsize, "nblocks": len(blocks),
           "index_offset": tuple(lo), "shape": shape}
    if nmesh is not None:
        dx = [(b - a) / n for a, b, n in zip(xmin, xmax, nmesh)]
        for a, key in enumerate(("x1v", "x2v", "x3v")):
            out[key] = xmin[a] + (lo[a] + np.arange(hi[a] - lo[a]) + 0.5) * dx[a]
        out["full_mesh"] = (tuple(lo) == (0, 0, 0)
                            and tuple(h - l for h, l in zip(hi, lo)) == tuple(nmesh))
        out["grid"] = (Grid(nmesh, [b - a for a, b in zip(xmin, xmax)], xmin)
                       if out["full_mesh"] else None)
    else:
        out["full_mesh"], out["grid"] = False, None
    if "z4c" in params:
        out["chi_psi_power"] = float(params["z4c"].get("chi_psi_power", "-4.0"))
    pre = "z4c_" if strip_prefix is True else (strip_prefix or "")
    for i, n in enumerate(names):
        key = n[len(pre):] if pre and n.startswith(pre) else n
        out[key] = full[i]
    return out
