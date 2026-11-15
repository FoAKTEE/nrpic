"""R2, R3: kinematics oracle (JOURNAL.md)."""
import os
import json
import numpy as np
import pytest
import mpmath as mp

import kinematics as kin
import mj

HERE = os.path.dirname(os.path.abspath(__file__))


def random_pairs(n, rng, log_theta=(-8, 6), log_gamma=(0, 4), unequal=False):
    th = 10.0 ** rng.uniform(*log_theta, n)
    gb = 10.0 ** rng.uniform(*log_gamma, n)
    d = rng.normal(size=(n, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    bulk = np.sqrt(gb * gb - 1)[:, None] * d
    sc = (np.sqrt(th) * (1 + np.sqrt(th)))[:, None]
    ua = bulk + sc * rng.normal(size=(n, 3))
    ub = bulk + sc * rng.normal(size=(n, 3))
    nh = rng.normal(size=(n, 3)); nh /= np.linalg.norm(nh, axis=1)[:, None]
    ma = np.ones(n)
    mb = 10.0 ** rng.uniform(-1, 1, n) if unequal else np.ones(n)
    return ua, ub, ma, mb, nh


def test_against_mpmath():
    rng = np.random.default_rng(1)
    n = 20000
    ua, ub, ma, mb, nh = random_pairs(n, rng)
    a2, b2 = kin.scatter(ua, ub, ma, mb, nh)
    worst = 0.0
    for i in range(n):
        ra, rb = kin.mp_scatter(ua[i], ub[i], ma[i], mb[i], nh[i])
        scale = max(1.0, float(np.max(np.abs(ua[i]))), float(np.max(np.abs(ub[i]))))
        err = max(max(abs(float(ra[k]) - a2[i, k]) for k in range(3)),
                  max(abs(float(rb[k]) - b2[i, k]) for k in range(3))) / scale
        worst = max(worst, err)
    assert worst < 1e-14, worst


def test_against_mpmath_unequal_masses():
    rng = np.random.default_rng(2)
    n = 3000
    ua, ub, ma, mb, nh = random_pairs(n, rng, log_theta=(-6, 3), log_gamma=(0, 2),
                                      unequal=True)
    a2, b2 = kin.scatter(ua, ub, ma, mb, nh)
    worst = 0.0
    for i in range(n):
        ra, rb = kin.mp_scatter(ua[i], ub[i], ma[i], mb[i], nh[i])
        scale = max(1.0, float(np.max(np.abs(ua[i]))), float(np.max(np.abs(ub[i]))))
        err = max(max(abs(float(ra[k]) - a2[i, k]) for k in range(3)),
                  max(abs(float(rb[k]) - b2[i, k]) / max(1.0, 1.0) for k in range(3)))
        worst = max(worst, err / scale)
    assert worst < 1e-12, worst


def test_four_momentum_conservation():
    rng = np.random.default_rng(3)
    n = 200000
    ua, ub, ma, mb, nh = random_pairs(n, rng)
    a2, b2 = kin.scatter(ua, ub, ma, mb, nh)
    P0 = ma[:, None] * ua + mb[:, None] * ub
    P1 = ma[:, None] * a2 + mb[:, None] * b2
    E0 = ma * kin.W_of(ua) + mb * kin.W_of(ub)
    E1 = ma * kin.W_of(a2) + mb * kin.W_of(b2)
    eps = np.finfo(float).eps
    assert np.max(np.abs(P1 - P0).max(1) / E0) < 4 * eps
    assert np.max(np.abs(E1 - E0) / E0) < 8 * eps
    # invariant relative speed unchanged (elastic)
    g0 = kin.gamma_rel_m1(ua, ub)
    g1 = kin.gamma_rel_m1(a2, b2)
    rel = np.abs(g1 - g0) / np.maximum(g0, 1e-300)
    # relative change of gamma - 1 is ill-conditioned only through rounding of the
    # outputs; bound it by the conditioning W^2 eps / (gamma - 1)
    Wmax = np.maximum(kin.W_of(ua), kin.W_of(ub))
    assert np.all(rel <= 64 * eps * (1 + Wmax ** 2 / np.maximum(g0, 1e-300)))


def test_kinetic_energy_in_nr_regime():
    """At theta = 1e-8 the kinetic energy (W - 1) of the pair is conserved to a relative
    1e-8 of itself (the error is eps relative to the rest energy)."""
    rng = np.random.default_rng(4)
    n = 10000
    ua, ub, ma, mb, nh = random_pairs(n, rng, log_theta=(-8, -8), log_gamma=(0, 0))
    a2, b2 = kin.scatter(ua, ub, ma, mb, nh)
    K0 = mj.kinetic(ua) + mj.kinetic(ub)
    K1 = mj.kinetic(a2) + mj.kinetic(b2)
    assert np.max(np.abs(K1 - K0) / K0) < 1e-7


def test_mean_energy_identity():
    """R3: direction average of E_a' equals (E_a + E_b)/2 for equal masses."""
    rng = np.random.default_rng(5)
    ua = np.array([[0.7, -0.2, 0.4]])
    ub = np.array([[-1.5, 0.3, 2.0]])
    n = 400000
    nh = mj.isotropic_dirs(n, rng)
    a2, _ = kin.scatter(np.repeat(ua, n, 0), np.repeat(ub, n, 0), 1.0, 1.0, nh)
    Ea = kin.W_of(a2)
    target = 0.5 * (kin.W_of(ua)[0] + kin.W_of(ub)[0])
    assert abs(Ea.mean() - target) < 4 * Ea.std() / np.sqrt(n)
    # and the post-collision directions of a are isotropic in the CM frame by
    # construction; the CM energy of a is sqrt(s)/2 for every direction
    P = ua + ub
    E = kin.W_of(ua) + kin.W_of(ub)
    s = E[0] ** 2 - P[0] @ P[0]
    Ecm = (E[0] * Ea - a2 @ P[0]) / np.sqrt(s)       # energy of a in the CM frame
    assert np.max(np.abs(Ecm - np.sqrt(s) / 2)) < 1e-12 * E[0]


def test_metric_triad():
    rng = np.random.default_rng(6)
    A = rng.normal(size=(3, 3))
    gam = A @ A.T + 3 * np.eye(3)
    ginv = np.linalg.inv(gam)
    ua = rng.normal(size=3)
    ub = rng.normal(size=3)
    nh = mj.isotropic_dirs(1, rng)[0]
    a2, b2 = kin.scatter_metric(ua, ub, gam, nh)
    # covariant momentum conserved, energy W = sqrt(1 + g^ij u_i u_j) conserved
    assert np.max(np.abs(a2 + b2 - ua - ub)) < 1e-14 * 10
    W = lambda u: np.sqrt(1 + u @ ginv @ u)
    assert abs(W(a2) + W(b2) - W(ua) - W(ub)) < 1e-13 * (W(ua) + W(ub))


def test_vmol_against_mpmath():
    rng = np.random.default_rng(8)
    ua, ub, *_ = random_pairs(3000, rng)
    v = kin.vmol(ua, ub)
    for i in range(3000):
        ref = float(kin.mp_vmol(ua[i], ub[i]))
        assert abs(v[i] - ref) <= 1e-12 * max(ref, 1e-300) + 1e-300 or \
            abs(v[i] / ref - 1) < 1e-11


def test_test_vectors_roundtrip(tmp_path):
    path = tmp_path / "vec.json"
    nc = kin.make_test_vectors(str(path), n_random=50)
    d = json.load(open(path))
    assert len(d["cases"]) == nc
    for c in d["cases"]:
        ua = np.array([float.fromhex(x) for x in c["ua"]])
        ub = np.array([float.fromhex(x) for x in c["ub"]])
        nh = np.array([float.fromhex(x) for x in c["nhat"]])
        a2, b2 = kin.scatter(ua, ub, float.fromhex(c["ma"]), float.fromhex(c["mb"]), nh)
        sc = max(1.0, np.abs(ua).max(), np.abs(ub).max())
        assert np.max(np.abs(a2 - c["ua_out"])) / sc < 1e-13, c["label"]
        assert np.max(np.abs(b2 - c["ub_out"])) / sc < 1e-13, c["label"]
