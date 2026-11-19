#!/usr/bin/env python3
"""Checks of the oblate spheroid of the initial-data tools (nrpic.spheroid.OblateSpheroid,
nrpic.sampling.sample_spheroid, problems/ic/make_ic.py oblate).

Run with `python3 -m pytest python/tests/test_oblate_spheroid.py` or directly as a script.
The prolate counterparts are in test_initial_data.py.
"""

import json
import math
import os
import subprocess
import sys
import tempfile

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "python"))

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.integrate import quad  # noqa: E402

from nrpic import io as nio  # noqa: E402
from nrpic import sampling  # noqa: E402
from nrpic import spheroid as sp  # noqa: E402
from nrpic.spheroid import OblateSpheroid, ProlateSpheroid  # noqa: E402


def _IJ_quad(lam, a, b):
    """The defining integrals of the homogeneous spheroid by adaptive quadrature."""
    D = lambda u: (a * a + u) * math.sqrt(b * b + u)
    kw = dict(epsabs=0, epsrel=1e-12, limit=400)
    return (quad(lambda u: 1.0 / D(u), lam, np.inf, **kw)[0],
            quad(lambda u: 1.0 / ((a * a + u) * D(u)), lam, np.inf, **kw)[0],
            quad(lambda u: 1.0 / ((b * b + u) * D(u)), lam, np.inf, **kw)[0])


def test_oblate_integrals_against_quadrature():
    # both branches of _IJ_oblate (series for c/w < 0.3, closed form above) and the
    # neighbourhood of the switch
    for e, a in ((0.9, 10.0), (0.3, 2.0), (0.05, 5.0), (0.999, 3.0)):
        b = a * math.sqrt(1 - e * e)
        c = e * a
        lams = [0.0, 0.3, 5.0, 80.0, 1e4]
        if c / b > 0.3:      # lam at which c/w passes 0.3, and just on either side
            l0 = (c / 0.3) ** 2 - b * b
            lams += [l0 * (1 - 1e-6), l0 * (1 + 1e-6)]
        for lam in lams:
            got = sp._IJ_oblate(np.array([math.sqrt(b * b + lam)]), c)
            ref = _IJ_quad(lam, a, b)
            for g, r in zip(got, ref):
                assert abs(float(g[0]) / r - 1) < 2e-11, (e, a, lam, float(g[0]), r)


def test_oblate_fields():
    sph = OblateSpheroid(0.9, 10.0)
    assert abs(sph.b - 4.358898943540673) < 1e-14 and sph.c == 9.0
    assert abs(sph.a ** 2 * sph.b * (2 * sph.Ja0 + sph.Jb0) - 2) < 1e-13   # Poisson
    # rest mass: closed form of the shells against the potential-energy form and
    # against quadrature
    assert abs(sph.rest_mass() / sph.rest_mass_closed() - 1) < 1e-13
    assert abs(sph.rest_mass() - (1 + 0.6 * math.asin(0.9) / 9.0)) < 1e-13
    M_num = quad(lambda s: 4 * np.pi * sph.a ** 2 * sph.b * s * s * 2 * sph.rhoN *
                 (sph.c0 - (sph.cR * 2 * sph.a ** 2 + sph.cz * sph.b ** 2) * s * s / 3),
                 0, 1)[0]
    assert abs(M_num / sph.rest_mass() - 1) < 1e-12
    # psibar -> 1 + M/(2r): the remainder is the O(r^-3) quadrupole (negative Q)
    Q = 0.5 * (sph.b ** 2 - sph.a ** 2) / 5
    for r in (100.0, 1000.0):
        assert abs((sph.psibar(0, 0, r) - 1 - 0.5 / r) * r ** 3 / Q - 1) < 0.05
        assert abs((sph.psibar(r, 0, 0) - 1 - 0.5 / r) * r ** 3 / (-Q / 2) - 1) < 0.05
    # flat Laplacian by second differences
    h = 1e-3
    rng = np.random.default_rng(0)
    p = rng.uniform(-12, 12, (5000, 3)) * np.array([1.0, 1.0, 0.5])
    f = sph.psibar
    lap = sum(f(*(p + h * e).T) + f(*(p - h * e).T) for e in np.eye(3)) - 6 * f(*p.T)
    lap /= h * h
    s2 = sph.s2(*p.T)
    target = 4 * np.pi * sph.rhoN
    assert np.max(np.abs(lap[s2 < 0.95] + target)) < 1e-5 * target
    assert np.max(np.abs(lap[s2 > 1.05])) < 1e-5 * target
    # continuity at the surface, and the quadratic form inside
    th = np.linspace(0, np.pi, 9)
    xs = np.stack([sph.a * np.sin(th), 0 * th, sph.b * np.cos(th)], axis=1)
    assert np.max(np.abs(f(*(xs * (1 - 1e-10)).T) - f(*(xs * (1 + 1e-10)).T))) < 1e-9
    q = p[s2 < 1]
    quad_form = sph.c0 - sph.cR * (q[:, 0] ** 2 + q[:, 1] ** 2) - sph.cz * q[:, 2] ** 2
    assert np.max(np.abs(f(*q.T) - quad_form)) < 1e-14
    # density: rho_ADM psibar^6 = coordinate density, zero outside
    assert np.all(sph.rho_adm(*p[s2 > 1].T) == 0)
    assert np.allclose(sph.rho_adm(*q.T) * f(*q.T) ** 6, sph.coordinate_density(*q.T))


def test_oblate_sphere_and_prolate_limits():
    # e = 0: the homogeneous sphere of Newtonian mass M/2
    s = OblateSpheroid(0.0, 3.0)
    r = np.array([0.0, 0.5, 2.9, 3.0, 3.1, 40.0])
    u = np.where(r < 3, 0.5 * (3 - r * r / 9) / 6, 0.5 / np.maximum(r, 1e-300))
    assert np.max(np.abs(s.psibar(r, 0 * r, 0 * r) - 1 - u)) < 1e-15
    assert np.max(np.abs(s.psibar(0 * r, 0 * r, r) - 1 - u)) < 1e-15
    assert abs(s.rest_mass() - (1 + 0.6 / 3.0)) < 1e-14
    # e -> 0 from both sides meets the sphere: the two classes join continuously
    ob, pr = OblateSpheroid(1e-4, 3.0), ProlateSpheroid(1e-4, 3.0)
    pts = np.array([[0.3, 0.2, 0.1], [1.0, -2.0, 0.5], [4.0, 1.0, 2.0], [0.0, 0.0, 9.0]])
    assert np.max(np.abs(ob.psibar(*pts.T) - s.psibar(*pts.T))) < 1e-8
    assert np.max(np.abs(pr.psibar(*pts.T) - s.psibar(*pts.T))) < 1e-8
    try:
        OblateSpheroid(1.0, 3.0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for e = 1")


def test_sampler_oblate():
    sph = OblateSpheroid(0.9, 10.0)
    for N in (100, 10000):
        x, u, m, spc = sampling.sample_spheroid(N, seed=2, spheroid=sph)
        assert len(m) == N and np.all(u == 0) and np.all(sph.s2(*x.T) <= 1 + 1e-12)
        assert abs(m.sum() / sph.rest_mass() - 1) < 1e-14
        n4 = N // 4
        b = x[:n4]
        assert np.allclose(x[n4:2 * n4], b * [1, 1, -1])
        assert np.allclose(x[2 * n4:3 * n4], b * [-1, -1, 1])
        assert np.allclose(x[3 * n4:], -b)
        assert np.max(np.abs(x.mean(0))) < 1e-12
        assert stats.kstest(np.sqrt(sph.s2(*b.T)), sph.F_s).pvalue > 1e-3
        assert stats.kstest(b[:, 2] / sph.b, sph.F_z).pvalue > 1e-3
    # the particle form of the constraint: sum m/psibar = M up to the sampling error
    x, u, m, spc = sampling.sample_spheroid(10000, seed=1, spheroid=sph)
    assert abs(np.sum(m / sph.psibar(*x.T)) - sph.M) < 1e-3
    # the flattening is that of the spheroid: <z^2>/<x^2 + y^2> = b^2/(2 a^2) for a
    # uniform density, a little less here because psibar weights the centre more
    ratio = np.mean(x[:, 2] ** 2) / np.mean(x[:, 0] ** 2 + x[:, 1] ** 2)
    assert abs(ratio / (sph.b ** 2 / (2 * sph.a ** 2)) - 1) < 0.05


def test_make_ic_oblate_cli():
    mk = os.path.join(_ROOT, "problems", "ic", "make_ic.py")
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([sys.executable, mk, "oblate", "--e", "0.9", "--a", "10", "--N", "2000",
                        "--seed", "3", "--out", d], check=True, stdout=subprocess.DEVNULL)
        stem = "oblate_e0p9_a10_N2000_s3"
        x, u, m, spc = nio.read_nrp(os.path.join(d, stem + ".nrp"))
        meta = json.load(open(os.path.join(d, stem + ".json")))
        sph = OblateSpheroid(0.9, 10.0)
        assert len(m) == 2000 and np.all(u == 0)
        assert meta["model"] == "oblate_spheroid" and meta["symmetrize"] is True
        assert abs(meta["M_rest"] - sph.rest_mass()) < 1e-14
        prob = meta["athenak"]["problem"]
        assert prob["comp0_type"] == "spheroid" and prob["comp0_a"] == 10.0
        assert abs(prob["comp0_b"] - sph.b) < 1e-15 and prob["comp0_a"] > prob["comp0_b"]
        assert np.all(sph.s2(*x.T) <= 1 + 1e-12)
        assert not os.path.exists(os.path.join(d, stem + ".tab"))


if __name__ == "__main__":
    import time
    failed = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        t0 = time.time()
        try:
            fn()
            print(f"PASS {name} ({time.time() - t0:.1f} s)")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {exc!r}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
