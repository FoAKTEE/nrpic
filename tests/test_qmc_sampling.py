"""Tests for QMC, antipodal, octant-symmetric, and Lebedev S^2 particle samplers."""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from nrpic import clumps as clm  # noqa: E402
from nrpic import oppenheimer_snyder as osn  # noqa: E402
from nrpic import qmc_sampling as qmc  # noqa: E402
from nrpic import sampling  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402


def test_lebedev_cubature_and_halton_so3():
    """S^2 cubature rules satisfy moment isotropy through l=3/5/7 and SO(3) orthogonality."""
    for q in (6, 12, 14, 26):
        dirs, w = qmc.lebedev_unit_vectors(q)
        assert dirs.shape == (q, 3)
        assert np.all(w > 0)
        assert abs(w.sum() - 1.0) < 1e-14
        assert np.max(np.abs(np.sum(dirs * dirs, axis=1) - 1.0)) < 1e-14
        assert np.max(np.abs((w[:, None] * dirs).sum(0))) < 1e-14
        m2 = dirs.T @ (w[:, None] * dirs)
        assert np.max(np.abs(m2 - np.eye(3) / 3.0)) < 1e-14
        if q >= 12:
            assert abs(np.sum(w * dirs[:, 0] ** 4) - 0.2) < 1e-14
            assert abs(np.sum(w * (dirs[:, 0] ** 2) * (dirs[:, 1] ** 2)) - 1.0 / 15.0) < 1e-14
        if q == 26:
            assert abs(np.sum(w * dirs[:, 0] ** 6) - 1.0 / 7.0) < 1e-14
            assert abs(np.sum(w * (dirs[:, 0] ** 4) * (dirs[:, 1] ** 2)) - 1.0 / 35.0) < 1e-14
            assert abs(np.sum(w * (dirs[:, 0] * dirs[:, 1] * dirs[:, 2]) ** 2) - 1.0 / 105.0) < 1e-14
    for idx in (0, 7, 42):
        R = qmc.halton_so3(idx)
        assert np.max(np.abs(R.T @ R - np.eye(3))) < 1e-14
        assert abs(np.linalg.det(R) - 1.0) < 1e-14


def test_st_zero_dipole_isotropy_and_shell_convergence():
    """QMC+Lebedev ST cluster has exact COM=0, P=0, J=0, local stress isotropy, and O(N^{-1}) radial error."""
    model = stc.STModel(0.819)
    for mode in ("qmc_antipodal", "qmc_lebedev"):
        N = 14 * 100 if mode == "qmc_lebedev" else 1400
        x, u, m, sp = sampling.sample_st(model, N, method=mode, seed=3, lebedev_q=14)
        assert len(x) == N and np.all(sp == 0)
        assert abs(m.sum() - model.M0) / model.M0 < 1e-14
        com = (m[:, None] * x).sum(0) / m.sum()
        mom = (m[:, None] * u).sum(0) / m.sum()
        ang = np.cross(x, m[:, None] * u).sum(0) / (m.sum() * model.rbar_s)
        assert np.max(np.abs(com)) < 1e-13
        assert np.max(np.abs(mom)) < 1e-13
        if mode == "qmc_antipodal":
            # Antipodal pairing (-x, -u) also preserves zero total angular momentum J
            assert np.max(np.abs(ang)) < 1e-13

    # Verify exact local velocity stress-tensor isotropy at each site for qmc_lebedev
    q_shell = 14
    n_sites = 40
    x, u, m, _ = sampling.sample_st(model, q_shell * n_sites, method="qmc_lebedev",
                                    seed=1, lebedev_q=q_shell)
    psi = model.psi(np.linalg.norm(x, axis=1))
    q_orth = u / psi[:, None] ** 2
    for s in range(n_sites):
        sl = slice(s * q_shell, (s + 1) * q_shell)
        w_s = m[sl] / m[sl].sum()
        mean_q = (w_s[:, None] * q_orth[sl]).sum(0)
        assert np.max(np.abs(mean_q)) < 1e-13
        P_s = q_orth[sl].T @ (w_s[:, None] * q_orth[sl])
        q2 = float(np.sum(q_orth[s * q_shell] ** 2))
        assert np.max(np.abs(P_s - (q2 / 3.0) * np.eye(3))) < 1e-13

    # Verify exact zero 3D mesh momentum noise & spatial parity asymmetry for QMC
    L = 1.2 * model.rbar_s
    ng = 12
    dx = 2.0 * L / ng
    for meth in ("qmc_antipodal", "qmc_lebedev"):
        xm, um, mm, _ = sampling.sample_st(model, 7000, method=meth, seed=7, lebedev_q=14)
        idx = np.floor((xm + L) / dx).astype(int)
        valid = np.all((idx >= 0) & (idx < ng), axis=1)
        S_dep = np.zeros((ng, ng, ng, 3))
        rho_dep = np.zeros((ng, ng, ng))
        np.add.at(rho_dep, (idx[valid, 0], idx[valid, 1], idx[valid, 2]), mm[valid])
        for a in range(3):
            np.add.at(S_dep[..., a], (idx[valid, 0], idx[valid, 1], idx[valid, 2]),
                      mm[valid] * um[valid, a])
        assert np.max(np.abs(S_dep)) < 1e-14
        assert np.max(np.abs(rho_dep - rho_dep[::-1, ::-1, ::-1])) < 1e-14

    # Cumulative radial mass convergence: QMC beats MC by O(N^{-1}) vs O(N^{-1/2})
    r_eval = np.linspace(0.05 * model.rbar_s, 0.95 * model.rbar_s, 15)
    f_exact = model.F(r_eval)
    errs_mc, errs_qmc = [], []
    Ns = (560, 2240, 8960)
    for N in Ns:
        xm, _, mm, _ = sampling.sample_st(model, N, method="mc", seed=11)
        rm = np.linalg.norm(xm, axis=1)
        f_mc = np.array([mm[rm <= rv].sum() / model.M0 for rv in r_eval])
        errs_mc.append(float(np.max(np.abs(f_mc - f_exact))))

        xq, _, mq, _ = sampling.sample_st(model, N, method="qmc_antipodal", seed=11)
        rq = np.linalg.norm(xq, axis=1)
        f_qmc = np.array([mq[rq <= rv].sum() / model.M0 for rv in r_eval])
        errs_qmc.append(float(np.max(np.abs(f_qmc - f_exact))))
    assert errs_qmc[-1] < 0.1 * errs_mc[-1]
    assert errs_qmc[0] / errs_qmc[-1] > 8.0


def test_os_prolate_and_jeans_qmc_symmetries():
    """OS (qmc_octant), Prolate (qmc_octant), and Jeans (qmc_lebedev) preserve exact moments."""
    # 1. OS qmc_octant: zero COM and exact isotropic quadrupole tensor (exact for N % 24 == 0)
    Mrest = osn.rest_mass(5.0, 1.0)
    x, u, m, _ = sampling.sample_os(N=4800, method="qmc_octant", seed=5)
    assert np.all(u == 0.0)
    assert abs(m.sum() - Mrest) < 1e-14
    assert np.max(np.abs((m[:, None] * x).sum(0))) < 1e-13
    Qxx = np.sum(m * x[:, 0] ** 2)
    Qyy = np.sum(m * x[:, 1] ** 2)
    Qzz = np.sum(m * x[:, 2] ** 2)
    Qxy = np.sum(m * x[:, 0] * x[:, 1])
    assert abs(Qxx - Qyy) < 1e-13 and abs(Qxx - Qzz) < 1e-13 and abs(Qxy) < 1e-13

    # 2. Prolate spheroid qmc_octant
    xp, up, mp, _ = sampling.sample_spheroid(4000, e=0.9, b=10.0, seed=2, method="qmc_octant")
    assert np.all(up == 0.0)
    assert np.max(np.abs((mp[:, None] * xp).sum(0))) < 1e-13
    assert abs(np.sum(mp * xp[:, 0] ** 2) - np.sum(mp * xp[:, 1] ** 2)) < 1e-13
    assert abs(np.sum(mp * xp[:, 0] * xp[:, 2])) < 1e-13

    # 3. Jeans model qmc_lebedev + continuum comparison
    J = clm.JeansModel()
    cont = J.continuum()["total"]
    xj, uj, mj, spj = J.sample(10000, seed=1, method="qmc_lebedev", lebedev_q=14)
    summ = J.particle_summary(xj, uj, mj, spj)["total"]
    assert abs(summ["sum_m"] - cont["rest_mass"]) / cont["rest_mass"] < 5e-4
    assert abs(summ["sum_mW"] - cont["sum_mW"]) / cont["sum_mW"] < 5e-4
    assert np.max(np.abs(summ["sum_m_u"])) < 1e-12
    assert np.max(np.abs(summ["centre_mW"])) < 1e-12
