"""Readers for the field dumps of this repository's AthenaK, into the layout of grid.py.

No AthenaK code is imported; the layouts are read from the writers:

read_rst(path)      restart file, athenak/src/outputs/restart.cpp (WriteOutputFile). The
                    only full-mesh output in double precision, the one to use for the
                    metric (a diagonal component 1 + h with h ~ 1e-6 is lost in float32).
                    Layout: parameter dump ending in "<par_end>\n"; int32 nmb_total, int32
                    root_level; RegionSize (9 float64: x1min x2min x3min x1max x2max x3max
                    dx1 dx2 dx3); RegionIndcs of the mesh and of a MeshBlock (19 int32 each:
                    ng nx1 nx2 nx3 is ie js je ks ke cnx1 cnx2 cnx3 cis cie cjs cje cks cke);
                    float64 time, float64 dt, int32 ncycle; LogicalLocation[nmb] (4 int32:
                    lx1 lx2 lx3 level); float32 cost[nmb]; float64 z4c last_output_time;
                    3 float64 per compact-object tracker (<z4c> co_<n>_type, n = 0, 1, ...);
                    uint64 data_size; then per MeshBlock (in gid order) float64
                    u0[nz4c][n3][n2][n1] with ghost cells (n = nx + 2 ng), the Z4c variables
                    in the order of the enum in athenak/src/z4c/z4c.hpp. NRPIC particles are
                    in a separate file and do not change this layout. Runs with hydro, MHD,
                    radiation or turbulence driving are refused (other layout).
read_bin(path)      binary mesh output, athenak/src/outputs/binary.cpp: text preheader
                    (time, cycle, variable names, "header offset=<n>"), the parameter dump,
                    then per MeshBlock 6 int32 (ois oie ojs oje oks oke), 4 int32 (lx1 lx2
                    lx3 level), 6 Real (x1min x1max x2min x2max x3min x3max), and float32
                    data[nvar][n3][n2][n1] without ghost cells. Single precision: use it for
                    quantities that vanish in the background (A_ij, Weyl output, constraints).
read_nrfield(path)  NRFIELD dump of the NRPIC module, athenak/src/particles/nrpic_io.cpp
                    (NrpicWriteEnergyField): "NRFIELD1"|"NRFIELD2", float64 time, 3 int64
                    (n1 n2 n3), float32 E[n3][n2][n1], float32 chi[...]; NRFIELD2 adds seven
                    float64 arrays H, Mx, My, Mz, Khat, Theta, alpha. It carries no conformal
                    metric or A_ij, so it is NOT enough for the wave diagnostics (use read_rst).
Only uniform meshes (no refinement) are assembled.
"""
import re

import numpy as np

from .grid import Grid

Z4C_NAMES = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat",
             "Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz", "Gamx", "Gamy", "Gamz",
             "Theta", "alpha", "betax", "betay", "betaz"]
SYMN = {(0, 0): "xx", (0, 1): "xy", (0, 2): "xz", (1, 1): "yy", (1, 2): "yz", (2, 2): "zz"}


def parse_params(text):
    """Parameter dump -> {block: {name: value string}} (comments after # removed)."""
    blocks, cur = {}, None
    for line in text.splitlines():
        s = line.split("#")[0].strip()
        if not s:
            continue
        if s.startswith("<") and s.endswith(">"):
            cur = s[1:-1].strip()
            blocks.setdefault(cur, {})
        elif "=" in s and cur is not None:
            k, v = s.split("=", 1)
            blocks[cur][k.strip()] = v.strip()
    return blocks


def _grid_from_size(msize, nx):
    x1min, x2min, x3min, x1max, x2max, x3max = (float(v) for v in msize[:6])
    return Grid(nx, (x1max - x1min, x2max - x2min, x3max - x3min), (x1min, x2min, x3min))


def read_rst(path, keep_ghosts=False):
    """Read a Z4c restart file. Returns dict: time, dt, cycle, params, grid (Grid),
    chi_psi_power, one float64 array (nz, ny, nx) per name of Z4C_NAMES, and with
    keep_ghosts the raw MeshBlocks as list of (logical location, array with ghosts)."""
    with open(path, "rb") as f:
        raw = f.read()
    end = raw.find(b"<par_end>")
    if end < 0:
        raise ValueError(f"{path}: no <par_end> in the header")
    off = end + len(b"<par_end>\n")
    params = parse_params(raw[:end].decode(errors="replace"))
    for b in ("hydro", "mhd", "radiation", "turb_driving"):
        if b in params:
            raise ValueError(f"{path}: block <{b}> present; this layout is not handled")
    if "z4c" not in params:
        raise ValueError(f"{path}: no <z4c> block")
    nco = 0
    while f"co_{nco}_type" in params["z4c"]:
        nco += 1
    nmb, _root = (int(v) for v in np.frombuffer(raw, np.int32, 2, off)); off += 8
    msize = np.frombuffer(raw, np.float64, 9, off); off += 72
    mind = np.frombuffer(raw, np.int32, 19, off); off += 76
    bind = np.frombuffer(raw, np.int32, 19, off); off += 76
    time, dt = (float(v) for v in np.frombuffer(raw, np.float64, 2, off)); off += 16
    ncycle = int(np.frombuffer(raw, np.int32, 1, off)[0]); off += 4
    lloc = np.frombuffer(raw, np.int32, 4 * nmb, off).reshape(nmb, 4); off += 16 * nmb
    off += 4 * nmb                       # cost of each MeshBlock (float32)
    off += 8                             # z4c last_output_time
    off += 24 * nco                      # compact-object tracker positions
    data_size = int(np.frombuffer(raw, np.uint64, 1, off)[0]); off += 8
    ng = int(bind[0])
    bn = [int(v) for v in bind[1:4]]
    n1, n2, n3 = (v + 2 * ng if v > 1 else 1 for v in bn)
    nv = len(Z4C_NAMES)
    if data_size != nv * n1 * n2 * n3 * 8:
        raise ValueError(f"{path}: data_size {data_size} != {nv}*{n3}*{n2}*{n1}*8")
    if off + nmb * data_size != len(raw):
        raise ValueError(f"{path}: size {len(raw)} != header {off} + {nmb}*{data_size}")
    if np.any(lloc[:, 3] != lloc[0, 3]):
        raise ValueError(f"{path}: refined mesh; only uniform meshes are assembled")
    gn = [int(v) for v in mind[1:4]]
    full = np.empty((nv, gn[2], gn[1], gn[0]))
    g1 = ng if bn[0] > 1 else 0
    g2 = ng if bn[1] > 1 else 0
    g3 = ng if bn[2] > 1 else 0
    blocks = []
    for m in range(nmb):
        u = np.frombuffer(raw, np.float64, nv * n1 * n2 * n3, off + m * data_size)
        u = u.reshape(nv, n3, n2, n1)
        lx1, lx2, lx3 = (int(v) for v in lloc[m, :3])
        full[:, lx3 * bn[2]:(lx3 + 1) * bn[2], lx2 * bn[1]:(lx2 + 1) * bn[1],
             lx1 * bn[0]:(lx1 + 1) * bn[0]] = u[:, g3:g3 + bn[2], g2:g2 + bn[1], g1:g1 + bn[0]]
        if keep_ghosts:
            blocks.append((tuple(int(v) for v in lloc[m]), u.copy()))
    out = {"time": time, "dt": dt, "cycle": ncycle, "params": params,
           "grid": _grid_from_size(msize, gn),
           "chi_psi_power": float(params["z4c"].get("chi_psi_power", "-4.0")),
           "nmb": nmb, "nco": nco}
    for i, n in enumerate(Z4C_NAMES):
        out[n] = full[i]
    if keep_ghosts:
        out["blocks"] = blocks
    return out


def read_bin(path):
    """Read a binary mesh output on a uniform mesh. Returns dict: time, cycle, variables,
    params, grid, one float64 array (nz, ny, nx) per variable (values are float32)."""
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    info, names = {}, None
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
    rtype = np.float64 if lsize == 8 else np.float32
    nvar = len(names)
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos); pos += 40
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ii)
        xs = np.frombuffer(raw, rtype, 6, pos); pos += 6 * lsize
        nx1, nx2, nx3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = nx1 * nx2 * nx3
        arr = np.frombuffer(raw, np.float32, nvar * cnt, pos).reshape(nvar, nx3, nx2, nx1)
        pos += 4 * nvar * cnt
        blocks.append(((lx1, lx2, lx3, lev), xs, arr))
    if any(b[0][3] != blocks[0][0][3] for b in blocks):
        raise ValueError(f"{path}: refined mesh; only uniform meshes are assembled")
    bn3, bn2, bn1 = blocks[0][2].shape[1:]
    m1 = max(b[0][0] for b in blocks) + 1
    m2 = max(b[0][1] for b in blocks) + 1
    m3 = max(b[0][2] for b in blocks) + 1
    full = np.empty((nvar, m3 * bn3, m2 * bn2, m1 * bn1))
    for (l1, l2, l3, _), _, arr in blocks:
        full[:, l3 * bn3:(l3 + 1) * bn3, l2 * bn2:(l2 + 1) * bn2, l1 * bn1:(l1 + 1) * bn1] = arr
    mesh = params.get("mesh", {})
    try:
        lo = [float(mesh[f"x{a}min"]) for a in (1, 2, 3)]
        hi = [float(mesh[f"x{a}max"]) for a in (1, 2, 3)]
        grid = Grid((m1 * bn1, m2 * bn2, m3 * bn3), [h - l for h, l in zip(hi, lo)], lo)
    except KeyError:
        grid = None
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]), "variables": names,
           "params": params, "grid": grid}
    for i, n in enumerate(names):
        out[n] = full[i]
    return out


def read_nrfield(path, L=None, xmin=None):
    """Read an NRFIELD1/NRFIELD2 dump. Returns dict: magic, time, n (n1, n2, n3), E, chi
    and, for NRFIELD2, H, Mx, My, Mz, Khat, Theta, alpha; grid if the box size L is given
    (the dump does not store it)."""
    with open(path, "rb") as f:
        raw = f.read()
    magic = raw[:8]
    if magic not in (b"NRFIELD1", b"NRFIELD2"):
        raise ValueError(f"{path}: magic {magic!r}")
    time = float(np.frombuffer(raw, np.float64, 1, 8)[0])
    n1, n2, n3 = (int(v) for v in np.frombuffer(raw, np.int64, 3, 16))
    nc = n1 * n2 * n3
    off = 40
    out = {"magic": magic.decode(), "time": time, "n": (n1, n2, n3)}
    for name in ("E", "chi"):
        out[name] = np.frombuffer(raw, np.float32, nc, off).reshape(n3, n2, n1).astype(float)
        off += 4 * nc
    if magic == b"NRFIELD2":
        for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
            out[name] = np.frombuffer(raw, np.float64, nc, off).reshape(n3, n2, n1).copy()
            off += 8 * nc
    if off != len(raw):
        raise ValueError(f"{path}: {len(raw) - off} trailing bytes")
    if L is not None:
        out["grid"] = Grid((n1, n2, n3), L, xmin)
    return out


# ----------------------------------------------------------------------------------------
# Z4c -> the arrays of gwdiag

def z4c_tensors(d):
    """chi, tilde gamma_ij (3, 3, ...), tilde A_ij, trK = Khat + 2 Theta, alpha, beta^i
    from a dict with the Z4c names (read_rst, or read_bin of variable = z4c)."""
    shp = d["chi"].shape
    gt = np.empty((3, 3) + shp)
    At = np.empty((3, 3) + shp)
    for (a, b), s in SYMN.items():
        gt[a, b] = gt[b, a] = d["g" + s]
        At[a, b] = At[b, a] = d["A" + s]
    trK = d["Khat"] + 2.0 * d["Theta"]
    beta = np.array([d["betax"], d["betay"], d["betaz"]])
    return d["chi"], gt, At, trK, d["alpha"], beta


def z4c_to_adm(d):
    """gamma_ij and K_ij as in Z4c::Z4cToADM (athenak/src/z4c/z4c_adm.cpp):
    psi^4 = chi^(4/chi_psi_power), gamma = psi^4 tilde gamma,
    K_ij = psi^4 tilde A_ij + (Khat + 2 Theta) gamma_ij / 3."""
    chi, gt, At, trK, alpha, beta = z4c_tensors(d)
    p = d.get("chi_psi_power", -4.0)
    psi4 = chi ** (4.0 / p)
    gamma = psi4 * gt
    K = psi4 * At + trK * gamma / 3.0
    return gamma, K, alpha, beta
