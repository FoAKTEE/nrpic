"""Readers: round trip through files written in the AthenaK layouts (synthetic), and,
when present, the real dumps named by environment variables:
  GWDIAG_RST     an AthenaK Z4c restart file
  GWDIAG_NRFIELD an NRFIELD dump
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gwdiag import readers  # noqa: E402

TMP = os.environ.get("GWDIAG_TMP", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp")


def write_fake_rst(path, nmb_x=(2, 1, 2), bn=(4, 6, 3), ng=2, nco=1, seed=0):
    """A restart file in the layout of athenak/src/outputs/restart.cpp."""
    rng = np.random.default_rng(seed)
    nv = len(readers.Z4C_NAMES)
    gn = [b * m for b, m in zip(bn, nmb_x)]
    full = rng.normal(size=(nv, gn[2], gn[1], gn[0]))
    par = "<job>\nbasename = fake\n<mesh>\nnx1 = %d\n<z4c>\nchi_psi_power = -4.0\n" % gn[0]
    for c in range(nco):
        par += f"co_{c}_type = BH\n"
    par += "<par_end>\n"
    nmb = nmb_x[0] * nmb_x[1] * nmb_x[2]
    n1, n2, n3 = (b + 2 * ng for b in bn)
    with open(path, "wb") as f:
        f.write(par.encode())
        f.write(np.array([nmb, 0], np.int32).tobytes())
        f.write(np.array([-1, -2, -3, 1, 2, 3, 2 / gn[0], 4 / gn[1], 6 / gn[2]], np.float64).tobytes())
        mi = [ng] + gn + [0] * 15
        bi = [ng] + list(bn) + [0] * 15
        f.write(np.array(mi, np.int32).tobytes())
        f.write(np.array(bi, np.int32).tobytes())
        f.write(np.array([1.25, 0.01], np.float64).tobytes())
        f.write(np.array([77], np.int32).tobytes())
        locs = [(i, j, k, 0) for k in range(nmb_x[2]) for j in range(nmb_x[1])
                for i in range(nmb_x[0])]
        f.write(np.array(locs, np.int32).tobytes())
        f.write(np.zeros(nmb, np.float32).tobytes())
        f.write(np.array([0.5], np.float64).tobytes())
        f.write(np.zeros(3 * nco, np.float64).tobytes())
        f.write(np.array([nv * n1 * n2 * n3 * 8], np.uint64).tobytes())
        for (i, j, k, _) in locs:
            u = rng.normal(size=(nv, n3, n2, n1))       # ghosts filled with noise
            u[:, ng:ng + bn[2], ng:ng + bn[1], ng:ng + bn[0]] = \
                full[:, k * bn[2]:(k + 1) * bn[2], j * bn[1]:(j + 1) * bn[1], i * bn[0]:(i + 1) * bn[0]]
            f.write(u.tobytes())
    return full


def test_rst_roundtrip():
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, "fake_test.rst")
    full = write_fake_rst(p)
    d = readers.read_rst(p)
    assert d["time"] == 1.25 and d["cycle"] == 77 and d["nco"] == 1
    for i, n in enumerate(readers.Z4C_NAMES):
        assert np.array_equal(d[n], full[i])
    g = d["grid"]
    assert g.n == (8, 6, 6) and np.allclose(g.L, (2, 4, 6)) and np.allclose(g.xmin, (-1, -2, -3))
    os.remove(p)


def test_nrfield_roundtrip():
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, "fake_test.field.bin")
    rng = np.random.default_rng(1)
    n1, n2, n3 = 5, 4, 3
    E = rng.normal(size=(n3, n2, n1)).astype(np.float32)
    chi = rng.normal(size=(n3, n2, n1)).astype(np.float32)
    extra = rng.normal(size=(7, n3, n2, n1))
    with open(p, "wb") as f:
        f.write(b"NRFIELD2")
        f.write(np.array([3.5]).tobytes())
        f.write(np.array([n1, n2, n3], np.int64).tobytes())
        f.write(E.tobytes())
        f.write(chi.tobytes())
        f.write(extra.tobytes())
    d = readers.read_nrfield(p, L=(1, 1, 1))
    assert d["time"] == 3.5 and d["n"] == (5, 4, 3)
    assert np.array_equal(d["E"], E.astype(float)) and np.array_equal(d["alpha"], extra[6])
    os.remove(p)


@pytest.mark.skipif("GWDIAG_RST" not in os.environ, reason="no real restart file given")
def test_real_rst():
    d = readers.read_rst(os.environ["GWDIAG_RST"])
    gamma, K, alpha, beta = readers.z4c_to_adm(d)
    assert gamma.shape[:2] == (3, 3) and np.all(np.isfinite(gamma))
    assert np.all(d["chi"] > 0)


@pytest.mark.skipif("GWDIAG_NRFIELD" not in os.environ, reason="no real NRFIELD dump given")
def test_real_nrfield():
    d = readers.read_nrfield(os.environ["GWDIAG_NRFIELD"])
    assert np.all(np.isfinite(d["E"])) and np.all(d["chi"] > 0)
