"""Own reader of the NRSFDMP2 dumps and of the .sf.con.hst / .sf.hst records (g1verify).

Written from the layout in core/scalar-2:tracks/core/interfaces/scalar_field_2.md section 4:
8 bytes 'NRSFDMP2'; int64 nmb, nx1, nx2, nx3, nvar, cycle, nnoise; double time; nvar names
of 16 bytes; then per MeshBlock int64 level, lx1, lx2, lx3, six doubles (bounds), and nvar
arrays of nx3 x nx2 x nx1 doubles (first index fastest = C order (nx3, nx2, nx1)).

Reads are sequential (open, seek, np.fromfile per variable): no memmap (I/O trap of the
package brief).  Independent of python/nrpic/scalar_field.py; checked against it in
check_reader.py.
"""
import os
import struct
import numpy as np

MAGIC = b"NRSFDMP2"


MAGIC1 = b"NRSFDMP1"
# NRSFDMP1 (release core-v0.3, athenak/src/scalar_field/scalar_field_io.cpp:13-17): the same
# header without names; fixed order phi, Pi, chi, K, alpha, H, M_x, M_y, M_z, E, noise0, ...
NAMES1 = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx", "My", "Mz", "E"]


def header(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic not in (MAGIC, MAGIC1):
            raise ValueError(f"{path}: magic {magic!r}, not NRSFDMP2/1")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        (time,) = struct.unpack("<d", f.read(8))
        if magic == MAGIC:
            names = [f.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        else:
            names = NAMES1 + [f"noise{i}" for i in range(nnoise)]
            if len(names) != nvar:
                raise ValueError(f"{path}: NRSFDMP1 with nvar {nvar} != {len(names)}")
    hbytes = 8 + 56 + 8 + (16 * nvar if magic == MAGIC else 0)
    ncell = nx1 * nx2 * nx3
    mbbytes = 32 + 48 + 8 * nvar * ncell
    size = os.path.getsize(path)
    if size != hbytes + nmb * mbbytes:
        raise ValueError(f"{path}: size {size} != {hbytes + nmb * mbbytes} from header")
    return dict(nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar, cycle=cycle, nnoise=nnoise,
                time=time, names=names, hbytes=hbytes, mbbytes=mbbytes, ncell=ncell)


def meshblocks(path, h=None):
    """Level, logical location and bounds of every MeshBlock."""
    h = h or header(path)
    out = []
    with open(path, "rb") as f:
        for m in range(h["nmb"]):
            f.seek(h["hbytes"] + m * h["mbbytes"])
            lev, l1, l2, l3 = struct.unpack("<4q", f.read(32))
            b = struct.unpack("<6d", f.read(48))
            out.append(dict(level=lev, lx=(l1, l2, l3), bounds=b))
    return out


def read(path, names, h=None, assemble=True):
    """Return {name: array}.  One MeshBlock: array (nx3, nx2, nx1).  Several MeshBlocks of
    level 0: assembled into the global array by logical location (assemble=True), else a
    list per MeshBlock.  Variables are read in file order (sequential I/O)."""
    h = h or header(path)
    idx = sorted((h["names"].index(n), n) for n in names)
    nx1, nx2, nx3 = h["nx"]
    mbs = meshblocks(path, h) if h["nmb"] > 1 else [dict(level=0, lx=(0, 0, 0))]
    res = {n: [] for n in names}
    with open(path, "rb") as f:
        for m in range(h["nmb"]):
            base = h["hbytes"] + m * h["mbbytes"] + 80
            for v, n in idx:
                f.seek(base + 8 * v * h["ncell"])
                a = np.fromfile(f, dtype="<f8", count=h["ncell"])
                if a.size != h["ncell"]:
                    raise IOError(f"{path}: short read of {n} in MeshBlock {m}")
                res[n].append(a.reshape(nx3, nx2, nx1))
    if h["nmb"] == 1:
        return {n: res[n][0] for n in names}
    if not assemble:
        return res, mbs
    if any(mb["level"] != 0 for mb in mbs):
        raise ValueError("refined MeshBlocks: assemble not supported")
    L = np.array([mb["lx"] for mb in mbs])
    n1, n2, n3 = L[:, 0].max() + 1, L[:, 1].max() + 1, L[:, 2].max() + 1
    out = {}
    for n in names:
        g = np.empty((n3 * nx3, n2 * nx2, n1 * nx1))
        for m, mb in enumerate(mbs):
            l1, l2, l3 = mb["lx"]
            g[l3 * nx3:(l3 + 1) * nx3, l2 * nx2:(l2 + 1) * nx2, l1 * nx1:(l1 + 1) * nx1] = res[n][m]
        out[n] = g
    return out


def read_hashed(path, names, chunk=1 << 26):
    """Read the whole file once, sequentially, hash it (sha256) and return
    ({name: array} of a single-MeshBlock dump, hexdigest, header)."""
    import hashlib
    h = header(path)
    if h["nmb"] != 1:
        raise ValueError("read_hashed: single MeshBlock only")
    size = os.path.getsize(path)
    buf = bytearray(size)
    mv = memoryview(buf)
    hs = hashlib.sha256()
    pos = 0
    with open(path, "rb") as f:
        while pos < size:
            n = f.readinto(mv[pos:pos + chunk])
            if not n:
                raise IOError(f"{path}: short read")
            hs.update(mv[pos:pos + n])
            pos += n
    nx1, nx2, nx3 = h["nx"]
    base = h["hbytes"] + 80
    out = {}
    for n in names:
        v = h["names"].index(n)
        a = np.frombuffer(buf, dtype="<f8", count=h["ncell"], offset=base + 8 * v * h["ncell"])
        out[n] = a.reshape(nx3, nx2, nx1)
    return out, hs.hexdigest(), h


def read_record(path):
    """A .hst record: (column names from the second comment line, data array)."""
    cols = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                cols = [c.split("=", 1)[1] for c in line[1:].split()]
                break
    data = np.loadtxt(path, comments="#", ndmin=2)
    return cols, data


def dumps(rundir, base="sr"):
    """Sorted list of the dump files of one run directory."""
    fs = sorted(x for x in os.listdir(rundir) if x.startswith(base + ".sf.") and x.endswith(".dump"))
    return [os.path.join(rundir, x) for x in fs]
