"""Readers for the AthenaK outputs of the periodic_z4c runs (no code of AthenaK is
imported; the layouts are read from the writers in athenak/src/outputs/).

Three formats:

read_tab(path)
    Formatted 1D table (file_type = tab, athenak/src/outputs/formatted_table.cpp):
    two comment lines ("# Athena++ data at time=... cycle=...", then the column names),
    then one row per cell. Double precision as printed (data_format = %.16e).

read_rst(path)
    Restart file (file_type = rst, athenak/src/outputs/restart.cpp), the only full-mesh
    output of AthenaK in double precision. Layout, for a run with Z4c and no hydro, MHD,
    radiation, forcing or puncture trackers (checked: the parameter block has no
    <hydro>, <mhd>, <radiation>, <turb_driving>):
      parameter dump, text, ending with "<par_end>\\n"
      int32 nmb_total, int32 root_level
      RegionSize mesh_size   (9 float64: x1min x2min x3min x1max x2max x3max dx1 dx2 dx3)
      RegionIndcs mesh_indcs (19 int32: ng nx1 nx2 nx3 is ie js je ks ke cnx1 cnx2 cnx3
                              cis cie cjs cje cks cke)
      RegionIndcs mb_indcs   (19 int32)
      float64 time, float64 dt, int32 ncycle
      LogicalLocation[nmb_total] (4 int32: lx1 lx2 lx3 level)
      float32 cost[nmb_total]
      float64 z4c last_output_time
      uint64 data_size (bytes per MeshBlock)
      per MeshBlock m, at offset + m*data_size: float64 u0[nz4c][n3][n2][n1], ghost cells
      included (n = nx + 2 ng), C order (Kokkos LayoutRight), variables in the order of
      Z4C_NAMES below (athenak/src/z4c/z4c.hpp, enum I_Z4C_*).
    The MeshBlocks are placed on a uniform root grid by their logical location; mesh
    refinement is refused.

read_bin(path)
    Binary mesh output (file_type = bin, athenak/src/outputs/binary.cpp). The variables
    are float32: a diagonal metric component 1 + h with h ~ 1e-6 is NOT representable
    (float32 resolves 6e-8 relative to 1); use it only for quantities that vanish in
    the background (off-diagonal metric, A_ij, Weyl scalars, constraints).

z4c_to_adm(d)
    gamma_ij = gt_ij / chi, K_ij = (At_ij + gt_ij K / 3) / chi with K = Khat + 2 Theta
    (chi_psi_power = -4, the default of <z4c>).
"""
import re
import numpy as np

Z4C_NAMES = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat",
             "Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz", "Gamx", "Gamy", "Gamz",
             "Theta", "alpha", "betax", "betay", "betaz"]
SYM = ["xx", "xy", "xz", "yy", "yz", "zz"]


def read_tab(path):
    """Return dict: time, cycle, and one float64 array per column (names without the
    'z4c_' prefix as well as with it)."""
    with open(path) as f:
        l1 = f.readline()
        l2 = f.readline()
    m = re.search(r"time=\s*([0-9eE+\-.]+)\s+cycle=\s*(\d+)", l1)
    names = l2.lstrip("#").split()
    data = np.loadtxt(path, comments="#", ndmin=2)
    out = {"time": float(m.group(1)), "cycle": int(m.group(2))}
    for n, col in zip(names, data.T):
        out[n] = col
        if n.startswith("z4c_"):
            out[n[4:]] = col
    return out


def _params(text):
    """Parse the parameter dump into {block: {name: value-string}}."""
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


def read_rst(path, ghosts=False):
    """Read a Z4c-only AthenaK restart file. Returns dict with time, cycle, params,
    mesh (x1min ... dx3, nx1 ...), cell-centre coordinates x, y, z (1D) and one
    float64 array [nx3, nx2, nx1] (k, j, i order, as AthenaK stores it) per Z4c
    variable. With ghosts=True also 'blocks': list of (lloc, u0 with ghosts)."""
    with open(path, "rb") as f:
        raw = f.read()
    end = raw.find(b"<par_end>")
    if end < 0:
        raise ValueError(f"{path}: no <par_end>")
    hdr = end + len(b"<par_end>\n")
    params = _params(raw[:end].decode())
    for b in ("hydro", "mhd", "radiation", "turb_driving"):
        if b in params:
            raise ValueError(f"{path}: block <{b}> present; layout not handled")
    if "z4c" not in params:
        raise ValueError(f"{path}: no <z4c> block")
    off = hdr
    nmb, root_level = np.frombuffer(raw, np.int32, 2, off); off += 8
    msize = np.frombuffer(raw, np.float64, 9, off); off += 72
    mind = np.frombuffer(raw, np.int32, 19, off); off += 76
    bind = np.frombuffer(raw, np.int32, 19, off); off += 76
    time, dt = np.frombuffer(raw, np.float64, 2, off); off += 16
    ncycle = int(np.frombuffer(raw, np.int32, 1, off)[0]); off += 4
    lloc = np.frombuffer(raw, np.int32, 4*nmb, off).reshape(nmb, 4); off += 16*nmb
    off += 4*nmb                                   # cost of each MeshBlock
    off += 8                                       # z4c last_output_time
    data_size = int(np.frombuffer(raw, np.uint64, 1, off)[0]); off += 8
    ng = int(bind[0]); bn1, bn2, bn3 = (int(v) for v in bind[1:4])
    n1, n2, n3 = bn1 + 2*ng, bn2 + 2*ng, bn3 + 2*ng
    nv = len(Z4C_NAMES)
    if data_size != nv*n1*n2*n3*8:
        raise ValueError(f"{path}: data_size {data_size} != {nv}*{n1}*{n2}*{n3}*8")
    if np.any(lloc[:, 3] != lloc[0, 3]):
        raise ValueError(f"{path}: refined mesh; reader handles a uniform mesh only")
    gn1, gn2, gn3 = (int(v) for v in mind[1:4])
    full = np.empty((nv, gn3, gn2, gn1))
    blocks = []
    for m in range(nmb):
        u = np.frombuffer(raw, np.float64, nv*n1*n2*n3, off + m*data_size)
        u = u.reshape(nv, n3, n2, n1)
        lx1, lx2, lx3 = int(lloc[m, 0]), int(lloc[m, 1]), int(lloc[m, 2])
        full[:, lx3*bn3:(lx3+1)*bn3, lx2*bn2:(lx2+1)*bn2, lx1*bn1:(lx1+1)*bn1] = \
            u[:, ng:ng+bn3, ng:ng+bn2, ng:ng+bn1]
        if ghosts:
            blocks.append((tuple(lloc[m]), u.copy()))
    x1min, x2min, x3min, x1max, x2max, x3max = msize[:6]
    mesh = dict(x1min=x1min, x2min=x2min, x3min=x3min, x1max=x1max, x2max=x2max,
                x3max=x3max, nx1=gn1, nx2=gn2, nx3=gn3, ng=ng)
    out = {"time": float(time), "dt": float(dt), "cycle": ncycle, "params": params,
           "mesh": mesh,
           "x": x1min + (np.arange(gn1) + 0.5)*(x1max - x1min)/gn1,
           "y": x2min + (np.arange(gn2) + 0.5)*(x2max - x2min)/gn2,
           "z": x3min + (np.arange(gn3) + 0.5)*(x3max - x3min)/gn3}
    for i, n in enumerate(Z4C_NAMES):
        out[n] = full[i]
    if ghosts:
        out["blocks"] = blocks
    return out


def read_bin(path):
    """Read an AthenaK binary mesh output (float32 variables) on a uniform mesh.
    Returns dict with time, cycle, variable names and arrays [nx3, nx2, nx1]."""
    with open(path, "rb") as f:
        raw = f.read()
    # text lines: version, size of preheader, time, cycle, size of location, size of
    # variable, number of variables, "variables:  a  b ...", "header offset=<n>",
    # then the parameter dump of n bytes, then the MeshBlocks
    pos = 0
    info, varnames = {}, None
    while True:
        e = raw.index(b"\n", pos)
        l = raw[pos:e].decode()
        pos = e + 1
        if "variables:" in l:
            varnames = l.split("variables:")[1].split()
        elif "header offset" in l:
            hoff = int(l.split("=")[1])
            break
        elif "=" in l:
            k, v = l.split("=", 1)
            info[k.strip()] = v.strip()
    params = _params(raw[pos:pos + hoff].decode(errors="replace"))
    pos += hoff
    lsize = int(info["size of location"])
    nvar = len(varnames)
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos); pos += 40
        ois, oie, ojs, oje, oks, oke, lx1, lx2, lx3, lev = (int(v) for v in ii)
        xs = np.frombuffer(raw, np.float64 if lsize == 8 else np.float32, 6, pos)
        pos += 6*lsize
        nx1, nx2, nx3 = oie - ois + 1, oje - ojs + 1, oke - oks + 1
        cnt = nx1*nx2*nx3
        arr = np.frombuffer(raw, np.float32, nvar*cnt, pos).reshape(nvar, nx3, nx2, nx1)
        pos += 4*nvar*cnt
        blocks.append(((lx1, lx2, lx3, lev), xs, arr))
    if any(b[0][3] != blocks[0][0][3] for b in blocks):
        raise ValueError(f"{path}: refined mesh; reader handles a uniform mesh only")
    bn3, bn2, bn1 = blocks[0][2].shape[1:]
    mx1 = max(b[0][0] for b in blocks) + 1
    mx2 = max(b[0][1] for b in blocks) + 1
    mx3 = max(b[0][2] for b in blocks) + 1
    full = np.empty((nvar, mx3*bn3, mx2*bn2, mx1*bn1), dtype=np.float32)
    for (lx1, lx2, lx3, _), _, arr in blocks:
        full[:, lx3*bn3:(lx3+1)*bn3, lx2*bn2:(lx2+1)*bn2, lx1*bn1:(lx1+1)*bn1] = arr
    out = {"time": float(info["time"]), "cycle": int(info["cycle"]),
           "variables": varnames, "params": params}
    for i, n in enumerate(varnames):
        out[n] = full[i]
    return out


def z4c_to_adm(d):
    """ADM metric and extrinsic curvature from the Z4c variables of read_rst / read_tab
    (dict entries chi, gxx..gzz, Axx..Azz, Khat, Theta). Returns dict with g_xx...,
    K_xx..., K (trace)."""
    chi = d["chi"]
    K = d["Khat"] + 2.0*d["Theta"]
    out = {"K": K}
    for c in SYM:
        out["g_" + c] = d["g" + c]/chi
        out["K_" + c] = (d["A" + c] + d["g" + c]*K/3.0)/chi
    return out
