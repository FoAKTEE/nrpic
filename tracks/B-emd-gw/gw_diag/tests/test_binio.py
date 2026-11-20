"""binio.read_bin: AthenaK `bin` output in single and double precision (wave 3, round 1).

Synthetic files in the layout of athenak/src/outputs/binary.cpp (several MeshBlocks, both
precisions, a slice) and, when present, two real dumps of registered runs:
  GWDIAG_BIN_DOUBLE  default: run B-20261119-142016-ee73a03, test F at N = 16, t = 0
                     (z4c_linear_wave of core/requests-b, double_precision = true)
  GWDIAG_BIN_SINGLE  default: run B-emd-gw-20261115-113216-0ea0f74, linear wave at 16^3,
                     single precision ("size of variable=4")
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gwdiag import binio, readers, tt  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
REAL_DOUBLE = os.environ.get(
    "GWDIAG_BIN_DOUBLE", f"{SCR}/B-20261119-142016-ee73a03/N16/bin/lwo.z4c.00000.bin")
REAL_SINGLE = os.environ.get(
    "GWDIAG_BIN_SINGLE", f"{SCR}/B-emd-gw-20261115-113216-0ea0f74/bin/lw3.z4c.00001.bin")
NAMES = ["z4c_chi", "z4c_gxx", "z4c_Axy"]


def write_bin(path, arrays, names, nb=(2, 1, 2), bn=(4, 3, 2), ng=2, vsize=4, time=1.5,
              cycle=7, slice_k=None, size_line=True):
    """arrays: (nvar, nz, ny, nx), nx = nb[0] bn[0] etc. slice_k: global k index of a
    slice in x3 (only the blocks that hold it, one layer each)."""
    nx = [n * b for n, b in zip(nb, bn)]
    params = ("<mesh>\nnghost = %d\nnx1 = %d\nnx2 = %d\nnx3 = %d\nx1min = 0.0\nx1max = 4.0\n"
              "x2min = -1.0\nx2max = 2.0\nx3min = 0.0\nx3max = 1.0\n<meshblock>\nnx1 = %d\n"
              "nx2 = %d\nnx3 = %d\n" % (ng, nx[0], nx[1], nx[2], bn[0], bn[1], bn[2]))
    pb = params.encode()
    head = ("Athena binary output version=1.1\n  size of preheader=5\n  time=%r\n"
            "  cycle=%d\n  size of location=8\n" % (time, cycle))
    if size_line:
        head += "  size of variable=%d\n" % vsize
    head += ("  number of variables=%d\n  variables:  %s\n  header offset=%d\n"
             % (len(names), "  ".join(names), len(pb)))
    vt = np.float64 if vsize == 8 else np.float32
    with open(path, "wb") as f:
        f.write(head.encode())
        f.write(pb)
        for l3 in range(nb[2]):
            if slice_k is not None and not (l3 * bn[2] <= slice_k < (l3 + 1) * bn[2]):
                continue
            for l2 in range(nb[1]):
                for l1 in range(nb[0]):
                    if slice_k is None:
                        ks, ke = ng, ng + bn[2] - 1
                        blk = arrays[:, l3 * bn[2]:(l3 + 1) * bn[2]]
                    else:
                        ks = ke = ng + slice_k - l3 * bn[2]
                        blk = arrays[:, slice_k:slice_k + 1]
                    blk = blk[:, :, l2 * bn[1]:(l2 + 1) * bn[1], l1 * bn[0]:(l1 + 1) * bn[0]]
                    f.write(np.array([ng, ng + bn[0] - 1, ng, ng + bn[1] - 1, ks, ke,
                                      l1, l2, l3, 0], np.int32).tobytes())
                    f.write(np.zeros(6, np.float64).tobytes())
                    f.write(np.ascontiguousarray(blk, dtype=vt).tobytes())


def _arrays(seed=3, shape=(4, 3, 8)):
    rng = np.random.default_rng(seed)
    return 1.0 + 1e-7 * rng.standard_normal((3,) + shape)


def test_double_exact_multiblock(tmp_path):
    a = _arrays()
    p = str(tmp_path / "d.bin")
    write_bin(p, a, NAMES, vsize=8)
    d = binio.read_bin(p)
    assert d["var_size"] == 8 and d["loc_size"] == 8 and d["nblocks"] == 4
    assert d["cycle"] == 7 and d["time"] == 1.5 and d["full_mesh"]
    assert d["grid"].n == (8, 3, 4) and np.allclose(d["grid"].L, (4, 3, 1))
    for i, n in enumerate(NAMES):
        assert np.array_equal(d[n], a[i])
    s = binio.read_bin(p, strip_prefix=True)
    assert np.array_equal(s["gxx"], a[1]) and "z4c_gxx" not in s
    assert np.allclose(d["x1v"], (np.arange(8) + 0.5) * 0.5)


def test_single_matches_old_reader(tmp_path):
    a = _arrays()
    for size_line in (True, False):          # release files lack "size of variable"
        p = str(tmp_path / f"s{int(size_line)}.bin")
        write_bin(p, a, NAMES, vsize=4, size_line=size_line)
        d = binio.read_bin(p)
        g = readers.read_bin(p)
        assert d["var_size"] == 4
        for i, n in enumerate(NAMES):
            assert np.array_equal(d[n], g[n])
            assert np.array_equal(d[n], a[i].astype(np.float32).astype(float))
    # the old reader misreads a double file (documented reason for this module)
    p8 = str(tmp_path / "d.bin")
    write_bin(p8, a, NAMES, vsize=8)
    try:
        g8 = readers.read_bin(p8)
        assert not np.array_equal(g8["z4c_chi"], a[0])
    except Exception:
        pass


@pytest.mark.parametrize("vsize", [4, 8])
def test_slice(tmp_path, vsize):
    a = _arrays(seed=5)
    p = str(tmp_path / "slice.bin")
    write_bin(p, a, NAMES, vsize=vsize, slice_k=3)
    d = binio.read_bin(p)
    assert d["shape"] == (1, 3, 8) and d["index_offset"] == (0, 0, 3)
    assert not d["full_mesh"] and d["grid"] is None and d["nblocks"] == 2
    vt = np.float64 if vsize == 8 else np.float32
    for i, n in enumerate(NAMES):
        assert np.array_equal(d[n], a[i, 3:4].astype(vt).astype(float))
    assert np.allclose(d["x3v"], [(3 + 0.5) * 0.25])


def test_truncated_file_refused(tmp_path):
    a = _arrays()
    p = str(tmp_path / "t.bin")
    write_bin(p, a, NAMES, vsize=8)
    raw = open(p, "rb").read()
    open(p, "wb").write(raw[:-16])
    with pytest.raises(ValueError):
        binio.read_bin(p)


@pytest.mark.skipif(not os.path.exists(REAL_DOUBLE), reason="no real double-precision dump")
def test_real_double_dump():
    """test F at t = 0: h = amp e+ sin(k.x) + amp_x ex sin(k.x + 1), k = 2 pi (1,1,1),
    amp = 1e-6, amp_x = 5e-7: the TT amplitudes at +k from the double-precision file equal
    the generator's to <= 1e-10 relative (waves/JOURNAL.md F1: 6e-12); the float32 reader
    of readers.read_bin cannot read this file correctly."""
    d = binio.read_bin(REAL_DOUBLE, strip_prefix=True)
    assert d["var_size"] == 8 and d["full_mesh"] and d["grid"].n == (16, 16, 16)
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    g = d["grid"]
    hTT, _ = tt.tt_from_conformal(gt, At, g)
    kv = 2 * np.pi * np.array([1.0, 1.0, 1.0])
    X, Y, Z = g.mesh()
    ph = np.exp(-1j * (kv[0] * X + kv[1] * Y + kv[2] * Z))
    C = np.tensordot(hTT, ph, axes=([-3, -2, -1], [0, 1, 2])) / g.ncell
    ep, ex, _, _ = tt.pol_basis((kv / np.linalg.norm(kv)).reshape(3, 1, 1, 1))
    P = 0.5 * np.sum(ep[..., 0, 0, 0] * C)
    Xc = 0.5 * np.sum(ex[..., 0, 0, 0] * C)
    assert abs(P / (1e-6 / 2j) - 1) < 1e-10
    assert abs(Xc / (5e-7 * np.exp(1j) / 2j) - 1) < 1e-10
    gamma, K, _, _ = readers.z4c_to_adm(d)
    assert np.all(np.isfinite(gamma)) and d["chi_psi_power"] == -4.0


@pytest.mark.skipif(not os.path.exists(REAL_SINGLE), reason="no real single-precision dump")
def test_real_single_dump_equals_old_reader():
    d = binio.read_bin(REAL_SINGLE)
    g = readers.read_bin(REAL_SINGLE)
    assert d["var_size"] == 4 and d["full_mesh"]
    assert d["grid"].n == g["grid"].n and d["time"] == g["time"] and d["cycle"] == g["cycle"]
    for n in d["variables"]:
        assert np.array_equal(d[n], g[n]), n
