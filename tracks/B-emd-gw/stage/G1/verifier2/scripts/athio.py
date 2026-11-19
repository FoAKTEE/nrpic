"""Readers of AthenaK outputs written for this verification (verifier2), from the writers
athenak/src/outputs/binary.cpp and restart.cpp and docs/FORMATS.md; no other reader used.

read_bin(path)       -> dict(time, cycle, names, var[name] = array [ix, iy, iz] float64)
read_rst_z4c(path)   -> dict(time, cycle, var[name] = array [ix, iy, iz] float64), uniform mesh,
                        z4c the only evolved field (the particles are in <path>.prt)
read_snap(path)      -> dict(time, cycle, x[N,3], u[N,3], m[N], tag[N], species[N])
read_traj(path)      -> array of records (time, tag, x1, x2, x3, u1, u2, u3)
"""
import re
import struct

import numpy as np

Z4C_NAMES = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat", "Axx", "Axy", "Axz",
             "Ayy", "Ayz", "Azz", "Gamx", "Gamy", "Gamz", "Theta", "alpha", "betax", "betay",
             "betaz"]


def _par(text, block, key):
    m = re.search(r"<%s>(.*?)(?=\n<|\Z)" % block, text, re.S)
    v = re.search(r"^\s*%s\s*=\s*([^#\s]+)" % key, m.group(1), re.M)
    return v.group(1)


def read_bin(path):
    with open(path, "rb") as f:
        raw = f.read()
    # text pre-header up to "header offset=N\n", then N bytes of parameter dump
    i = raw.index(b"header offset=")
    j = raw.index(b"\n", i)
    hoff = int(raw[i + len(b"header offset="):j])
    pre = raw[:j].decode()
    par = raw[j + 1:j + 1 + hoff].decode()
    p = j + 1 + hoff
    time = float(re.search(r"time=(\S+)", pre).group(1))
    cycle = int(re.search(r"cycle=(\S+)", pre).group(1))
    sloc = int(re.search(r"size of location=(\d+)", pre).group(1))
    svar = int(re.search(r"size of variable=(\d+)", pre).group(1))
    nvar = int(re.search(r"number of variables=(\d+)", pre).group(1))
    names = re.search(r"variables:\s+(.*)", pre).group(1).split()
    assert len(names) == nvar and sloc == 8 and svar == 4
    nx = [int(_par(par, "mesh", f"nx{d}")) for d in (1, 2, 3)]
    xmin = [float(_par(par, "mesh", f"x{d}min")) for d in (1, 2, 3)]
    xmax = [float(_par(par, "mesh", f"x{d}max")) for d in (1, 2, 3)]
    dx = [(xmax[d] - xmin[d])/nx[d] for d in range(3)]
    out = {n: np.empty(nx, dtype=np.float64) for n in names}
    filled = np.zeros(nx, dtype=np.int32)
    while p < len(raw):
        ii = struct.unpack_from("<10i", raw, p); p += 40
        xx = struct.unpack_from("<6d", raw, p); p += 48
        n1, n2, n3 = ii[1] - ii[0] + 1, ii[3] - ii[2] + 1, ii[5] - ii[4] + 1
        assert ii[9] == 0, "uniform mesh only"
        o = [int(round((xx[2*d] - xmin[d])/dx[d])) for d in range(3)]
        cells = n1*n2*n3
        data = np.frombuffer(raw, dtype="<f4", count=cells*nvar, offset=p).reshape(
            nvar, n3, n2, n1)
        p += 4*cells*nvar
        for v, name in enumerate(names):
            out[name][o[0]:o[0]+n1, o[1]:o[1]+n2, o[2]:o[2]+n3] = data[v].transpose(2, 1, 0)
        filled[o[0]:o[0]+n1, o[1]:o[1]+n2, o[2]:o[2]+n3] += 1
    assert (filled == 1).all(), "blocks do not tile the mesh exactly once"
    return {"time": time, "cycle": cycle, "names": names, "var": out, "nx": nx,
            "xmin": xmin, "xmax": xmax, "dx": dx}


def read_rst_z4c(path, nvar=22):
    with open(path, "rb") as f:
        raw = f.read()
    end = raw.index(b"<par_end>\n", raw.rindex(b"PAR_DUMP"))
    par = raw[:end + len(b"<par_end>\n")].decode()
    ng = int(_par(par, "mesh", "nghost"))
    nx = [int(_par(par, "mesh", f"nx{d}")) for d in (1, 2, 3)]
    nb = [int(_par(par, "meshblock", f"nx{d}")) for d in (1, 2, 3)]
    nmb = (nx[0]//nb[0])*(nx[1]//nb[1])*(nx[2]//nb[2])
    no = [n + 2*ng for n in nb]
    dsz = no[0]*no[1]*no[2]*nvar*8
    start = len(raw) - nmb*dsz
    assert struct.unpack_from("<Q", raw, start - 8)[0] == dsz, "data size field mismatch"
    time, dt = struct.unpack_from("<2d", raw, start - 196)
    cycle = struct.unpack_from("<i", raw, start - 180)[0]
    lloc = np.frombuffer(raw, dtype="<i4", count=4*nmb, offset=start - 176).reshape(nmb, 4)
    assert struct.unpack_from("<2i", raw, len(par))[0] == nmb
    out = {n: np.empty(nx, dtype=np.float64) for n in Z4C_NAMES}
    for m in range(nmb):
        d = np.frombuffer(raw, dtype="<f8", count=dsz//8, offset=start + m*dsz).reshape(
            nvar, no[2], no[1], no[0])
        o = [lloc[m, q]*nb[q] for q in range(3)]
        assert lloc[m, 3] == lloc[0, 3]
        for v, name in enumerate(Z4C_NAMES):
            blk = d[v, ng:ng+nb[2], ng:ng+nb[1], ng:ng+nb[0]].transpose(2, 1, 0)
            out[name][o[0]:o[0]+nb[0], o[1]:o[1]+nb[1], o[2]:o[2]+nb[2]] = blk
    return {"time": time, "dt": dt, "cycle": cycle, "var": out, "nx": nx}


def read_snap(path):
    with open(path, "rb") as f:
        raw = f.read()
    assert raw[:8] == b"NRPSNAP1"
    time = struct.unpack_from("<d", raw, 8)[0]
    n, cycle = struct.unpack_from("<2q", raw, 16)
    rec = np.frombuffer(raw, dtype="<f8", count=7*n, offset=32).reshape(n, 7)
    tag = np.frombuffer(raw, dtype="<i4", count=n, offset=32 + 56*n)
    sp = np.frombuffer(raw, dtype="<i4", count=n, offset=32 + 60*n)
    return {"time": time, "cycle": cycle, "x": rec[:, :3], "u": rec[:, 3:6], "m": rec[:, 6],
            "tag": tag, "species": sp}


def read_traj(path):
    return np.fromfile(path, dtype="<f8").reshape(-1, 8)
