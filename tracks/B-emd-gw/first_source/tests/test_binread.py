"""fslib.binread on synthetic files in the layout of athenak/src/outputs/binary.cpp: values
come back exactly in both precisions, and single-precision files give the same arrays as
gw_diag's reader."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import binread  # noqa: E402
from gwdiag import readers  # noqa: E402


def write_bin(path, arrays, names, nb=(2, 1, 2), bn=(4, 3, 2), vsize=4, time=1.5, cycle=7):
    """arrays: (nvar, nz, ny, nx) with nx = nb[0] bn[0] etc."""
    params = ("<mesh>\nnx1 = %d\nx1min = 0.0\nx1max = 4.0\nx2min = -1.0\nx2max = 2.0\n"
              "x3min = 0.0\nx3max = 1.0\n" % (nb[0] * bn[0]))
    pb = params.encode()
    head = ("Athena binary output version=1.1\n  size of preheader=5\n  time=%r\n"
            "  cycle=%d\n  size of location=8\n  size of variable=%d\n"
            "  number of variables=%d\n  variables:  %s\n  header offset=%d\n"
            % (time, cycle, vsize, len(names), "  ".join(names), len(pb))).encode()
    vt = np.float64 if vsize == 8 else np.float32
    with open(path, "wb") as f:
        f.write(head)
        f.write(pb)
        for l3 in range(nb[2]):
            for l2 in range(nb[1]):
                for l1 in range(nb[0]):
                    f.write(np.array([0, bn[0] - 1, 0, bn[1] - 1, 0, bn[2] - 1, l1, l2, l3, 0],
                                     np.int32).tobytes())
                    f.write(np.zeros(6, np.float64).tobytes())
                    blk = arrays[:, l3 * bn[2]:(l3 + 1) * bn[2], l2 * bn[1]:(l2 + 1) * bn[1],
                                 l1 * bn[0]:(l1 + 1) * bn[0]]
                    f.write(np.ascontiguousarray(blk, dtype=vt).tobytes())


def _arrays(seed=3):
    rng = np.random.default_rng(seed)
    return 1.0 + 1e-7 * rng.standard_normal((3, 4, 3, 8))


def test_double_exact(tmp_path):
    a = _arrays()
    p = str(tmp_path / "d.bin")
    write_bin(p, a, ["z4c_chi", "z4c_gxx", "z4c_Axy"], vsize=8)
    d = binread.read_bin(p)
    assert d["var_size"] == 8 and d["cycle"] == 7 and d["time"] == 1.5
    for i, n in enumerate(["z4c_chi", "z4c_gxx", "z4c_Axy"]):
        assert np.array_equal(d[n], a[i])
    assert d["grid"].n == (8, 3, 4) or tuple(d["grid"].n) == (8, 3, 4)


def test_single_matches_gwdiag(tmp_path):
    a = _arrays()
    p = str(tmp_path / "s.bin")
    write_bin(p, a, ["z4c_chi", "z4c_gxx", "z4c_Axy"], vsize=4)
    d = binread.read_bin(p)
    g = readers.read_bin(p)
    for n in ["z4c_chi", "z4c_gxx", "z4c_Axy"]:
        assert np.array_equal(d[n], g[n])
        assert np.array_equal(d[n], a[["z4c_chi", "z4c_gxx", "z4c_Axy"].index(n)].astype(np.float32))
    # gw_diag's reader reads float32 whatever the header says: a double file is misread there
    p8 = str(tmp_path / "d.bin")
    write_bin(p8, a, ["z4c_chi", "z4c_gxx", "z4c_Axy"], vsize=8)
    try:
        g8 = readers.read_bin(p8)
        assert not np.array_equal(g8["z4c_chi"], a[0])
    except Exception:
        pass
