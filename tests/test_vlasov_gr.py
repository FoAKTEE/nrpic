"""Unit and physics validation suite for python/nrpic/vlasov_gr.py."""

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import integrate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from nrpic import geodesic as _geo
from nrpic import kerr as _kerr
from nrpic import vlasov_gr as vg


def _direct_3d_tophat_flux(D_star, u_bar, Sigma, beta_F):
    """Brute-force 3D quadrature over the Top-Hat ellipsoid u = u_bar + L @ xi,
    xi in [-sqrt(3), sqrt(3)]^3, to verify the 1D-sliced + 2D-cubature formula."""
    L = vg.chol3_safe(Sigma)
    sq3 = math.sqrt(3.0)
    # Use high-order 24^3 Gauss-Legendre in xi
    gx, gw = np.polynomial.legendre.leggauss(24)
    xi_1d = sq3 * gx
    w_1d = 0.5 * gw
    x0, x1, x2 = np.meshgrid(xi_1d, xi_1d, xi_1d, indexing="ij")
    w3 = (w_1d[:, None, None] * w_1d[None, :, None] * w_1d[None, None, :]).ravel()
    xi = np.stack([x0.ravel(), x1.ravel(), x2.ravel()], axis=-1)
    u = u_bar[None, :] + xi @ L.T
    W = np.sqrt(1.0 + np.sum(u * u, axis=1))
    vrel = u[:, 0] / W - beta_F
    mask = vrel > 0.0
    if not np.any(mask):
        return 0.0, np.zeros(3), np.zeros((3, 3)), 0.0
    wm = w3[mask] * D_star * vrel[mask]
    um = u[mask]
    Wm = W[mask]
    Fm = float(np.sum(wm))
    FP = np.sum(wm[:, None] * um, axis=0)
    FPi = np.einsum("q,qi,qj->ij", wm, um, um)
    FE = float(np.sum(wm * Wm))
    return Fm, FP, FPi, FE


def test_newtonian_limit_matches_hopkins():
    """Verify relativistic one-sided flux reduces to Hopkins (2026) Eq. (44)-(45)
    when |u| << 1 and |beta_F| << 1 (exact when S is aligned/uncorrelated with normal)."""
    eps = 1e-5
    rho = 1.7
    v_bar = eps * np.array([0.8, -0.5, 0.3])
    S_nr = (eps * eps) * np.array([
        [1.2, 0.0, 0.0],
        [0.0, 0.9, 0.15],
        [0.0, 0.15, 0.7],
    ])
    A = np.array([1.0, 0.0, 0.0])
    for bF_fac in (-2.5, -0.3, 0.0, 0.4, 2.5):
        v_F = eps * bF_fac
        fm_nr, fp_nr, fT_nr = vg.onesided_flux_newtonian_tophat(rho, v_bar, S_nr, A, v_F)
        fm_gr, fp_gr, fP_gr, _ = vg.onesided_flux_tetrad(rho, v_bar, S_nr, v_F, n_perp=3)
        # Relative error is O(eps^2) ~ 1e-10 from relativistic gamma corrections
        if fm_nr > 0:
            assert abs(fm_gr - fm_nr) / fm_nr < 1e-7
            assert np.linalg.norm(fp_gr - fp_nr) / np.linalg.norm(fp_nr) < 1e-7
            assert np.linalg.norm(fP_gr - fT_nr) / np.linalg.norm(fT_nr) < 1e-7
        else:
            assert abs(fm_gr) < 1e-20


def test_relativistic_flux_vs_3d_quadrature():
    """Verify exact 1D-sliced + 2D-cubature flux against 24^3 brute-force 3D quadrature
    on the matching conditional parallelogram, and 1D antiderivative vs scipy.integrate.quad."""
    D = 2.3
    u_bar = np.array([1.4, -0.8, 0.6])
    Sig = np.array([
        [1.5, 0.4, -0.25],
        [0.4, 0.9, 0.2],
        [-0.25, 0.2, 0.6],
    ])
    perm = [1, 2, 0]
    L_p = vg.chol3_safe(Sig[np.ix_(perm, perm)])
    gx, gw = np.polynomial.legendre.leggauss(24)
    xi1 = gx * math.sqrt(3.0); w1 = 0.5 * gw
    x0, x1, x2 = np.meshgrid(xi1, xi1, xi1, indexing="ij")
    w3 = (w1[:, None, None] * w1[None, :, None] * w1[None, None, :]).ravel()
    xi3 = np.stack([x0.ravel(), x1.ravel(), x2.ravel()], axis=-1)
    u_perm = u_bar[perm][None, :] + xi3 @ L_p.T
    u_ref = np.stack([u_perm[:, 2], u_perm[:, 0], u_perm[:, 1]], axis=-1)
    W_ref = np.sqrt(1.0 + np.sum(u_ref * u_ref, axis=1))

    for beta_F in (-1.2, -0.8, 0.0, 0.55, 0.95, 1.15):
        fm_ex, fp_ex, fpi_ex, fe_ex = vg.onesided_flux_tetrad(D, u_bar, Sig, beta_F, n_perp=3)
        vrel = u_ref[:, 0] / W_ref - beta_F
        mask = vrel > 0.0
        wm = w3[mask] * D * vrel[mask]
        um = u_ref[mask]
        fm_q = float(np.sum(wm))
        fp_q = np.sum(wm[:, None] * um, axis=0) if np.any(mask) else np.zeros(3)
        fpi_q = np.einsum("q,qi,qj->ij", wm, um, um) if np.any(mask) else np.zeros((3, 3))
        fe_q = float(np.sum(wm * W_ref[mask])) if np.any(mask) else 0.0
        scale_m = max(abs(fm_q), 1.0)
        scale_p = max(float(np.linalg.norm(fp_q)), 1.0)
        scale_pi = max(float(np.linalg.norm(fpi_q)), 1.0)
        tol = 5e-4 if abs(beta_F) > 1.0 else 5e-3
        assert abs(fm_ex - fm_q) / scale_m < tol
        assert np.linalg.norm(fp_ex - fp_q) / scale_p < tol
        assert np.linalg.norm(fpi_ex - fpi_q) / scale_pi < tol
        assert abs(fe_ex - fe_q) / max(abs(fe_q), 1.0) < tol

    # Verify exact 1D antiderivative vs quadrature at fixed transverse u_perp (zero kink error!)
    for m_perp in (1.0, 2.5):
        for bF in (-1.3, -0.4, 0.0, 0.7, 0.99, 1.2):
            for mu, sp in ((0.2, 0.05), (1.8, 1.5), (-3.0, 2.5), (0.8, 0.0)):
                i0, i1, i2, ie = vg._slice_tophat_1d_vec(np.array([mu]), sp, np.array([m_perp]), bF)
                i0, i1, i2, ie = float(i0[0]), float(i1[0]), float(i2[0]), float(ie[0])
                if sp == 0.0:
                    continue
                hw = math.sqrt(3.0) * sp
                a, b = mu - hw, mu + hw
                if bF >= 1.0:
                    u_lo = b + 1.0
                elif bF <= -1.0:
                    u_lo = a
                else:
                    u_lo = max(a, bF * m_perp / math.sqrt(1.0 - bF * bF))
                if u_lo >= b:
                    assert (i0, i1, i2, ie) == (0.0, 0.0, 0.0, 0.0)
                else:
                    q0, _ = integrate.quad(lambda u: (u / math.sqrt(m_perp**2 + u**2) - bF) / (2 * hw), u_lo, b, epsabs=1e-13, epsrel=1e-13)
                    q1, _ = integrate.quad(lambda u: u * (u / math.sqrt(m_perp**2 + u**2) - bF) / (2 * hw), u_lo, b, epsabs=1e-13, epsrel=1e-13)
                    q2, _ = integrate.quad(lambda u: u * u * (u / math.sqrt(m_perp**2 + u**2) - bF) / (2 * hw), u_lo, b, epsabs=1e-13, epsrel=1e-13)
                    qe, _ = integrate.quad(lambda u: math.sqrt(m_perp**2 + u**2) * (u / math.sqrt(m_perp**2 + u**2) - bF) / (2 * hw), u_lo, b, epsabs=1e-13, epsrel=1e-13)
                    assert abs(i0 - q0) < 1e-12
                    assert abs(i1 - q1) < 1e-12
                    assert abs(i2 - q2) < 1e-12
                    assert abs(ie - qe) < 1e-12


def test_face_triad_and_energy_conditions():
    """Verify metric-orthonormal face triad and stress-energy conditions over 500 random states."""
    rng = np.random.default_rng(42)
    for _ in range(200):
        M = rng.normal(size=(3, 3))
        g = M @ M.T + 0.3 * np.eye(3)
        gi, det = vg.inv3_sym(g)
        A = rng.normal(size=3)
        normA, e_up, e_dn = vg.face_triad(g, A)
        assert np.allclose(e_up @ g @ e_up.T, np.eye(3), atol=1e-12)
        assert np.allclose(e_dn @ gi @ e_dn.T, np.eye(3), atol=1e-12)
        assert np.allclose(e_up[0], (gi @ A) / normA, atol=1e-12)
        assert np.linalg.det(e_up) > 0.0

        # Random SPD covariance and mass
        Ms = rng.normal(size=(3, 3))
        Sig = Ms @ Ms.T + 1e-3 * np.eye(3)
        u_bar = rng.normal(scale=3.0, size=3)
        m = 1.5
        E, P, Sij = vg.basis_stress_energy(m, u_bar, Sig, gi, n_q=3)
        assert E > m
        P2 = float(P @ gi @ P)
        trS = float(np.sum(gi * Sij))
        assert E * E - P2 > 0.0       # Dominant energy condition
        assert 0.0 <= trS < E          # Subluminality & trace bound
        assert E - trS > 0.0           # Strong energy condition (rho + 3p -> E - S_tr > 0)


def test_kerr_cubature_geodesic_push():
    """Verify cubature geodesic push in Kerr-Schild matches exact Kerr invariants
    in the cold limit and tracks a 2000-particle Monte Carlo cloud in the warm limit."""
    a = 0.9
    M = 1.0
    x0 = np.array([10.0, 0.0, 0.0])
    adm_k = _kerr.adm("cks", x0, a, M)
    adm_st = vg.AdmState(adm_k.alpha, adm_k.beta, adm_k.gamma,
                         adm_k.dalpha, adm_k.dbeta, adm_k.dgamma)
    # Near-circular prograde momentum
    u0 = np.array([0.0, 3.8, 0.4])
    # Cold limit: 1-step kick vs exact geodesic rhs at fixed x0
    u_kicked = vg.geodesic_kick_point(adm_st, None, 0.01, u0)
    _, du_dt = _geo.rhs("cks", x0, u0, a, M)
    assert np.linalg.norm(u_kicked - (u0 + 0.01 * du_dt)) < 1e-5

    # Warm cloud push at fixed x0: compare cubature mean & covariance vs 10^4 MC samples
    Sig0 = np.diag([0.08, 0.05, 0.03])
    u_new, Sig_new = vg.cubature_geodesic_kick(u0, Sig0, adm_st, None, 0.1, n_q=3)
    rng = np.random.default_rng(7)
    L0 = vg.chol3_safe(Sig0)
    # Sample uniform cube [-sqrt(3), sqrt(3)]^3 matching Top-Hat moments
    xi_mc = rng.uniform(-math.sqrt(3.0), math.sqrt(3.0), size=(20000, 3))
    u_mc = u0[None, :] + xi_mc @ L0.T
    u_mc_new = np.array([vg.geodesic_kick_point(adm_st, None, 0.1, um) for um in u_mc])
    u_mc_mean = np.mean(u_mc_new, axis=0)
    Sig_mc_new = np.cov(u_mc_new, rowvar=False, bias=True)
    assert np.linalg.norm(u_new - u_mc_mean) < 3e-3
    assert np.linalg.norm(Sig_new - Sig_mc_new) < 3e-3


def test_relativistic_bgk_conservation_and_synge():
    """Verify relativistic Maxwell-Juttner BGK conserves (m, P_i, E) to machine precision
    in curved metric with non-zero bulk velocity and anisotropic multi-basis DF."""
    g = np.array([[1.4, 0.12, -0.05], [0.12, 1.2, 0.08], [-0.05, 0.08, 1.1]])
    adm = vg.AdmState(0.85, np.array([0.1, -0.05, 0.02]), g,
                      np.zeros(3), np.zeros((3, 3)), np.zeros((3, 3, 3)))
    gi, _ = vg.inv3_sym(g)
    m = np.array([0.4, 0.35, 0.25])
    u_bar = np.array([[1.2, 0.3, -0.2], [-0.8, 0.5, 0.4], [0.1, -0.6, 0.2]])
    Sig = np.array([
        np.diag([0.3, 0.1, 0.05]),
        np.diag([0.15, 0.4, 0.2]),
        np.diag([0.08, 0.08, 0.25]),
    ])
    E0 = sum(vg.basis_stress_energy(m[a], u_bar[a], Sig[a], gi)[0] for a in range(3))
    P0 = sum(vg.basis_stress_energy(m[a], u_bar[a], Sig[a], gi)[1] for a in range(3))

    u1, S1 = vg.mj_bgk_relax_cell(m, u_bar, Sig, V_a=0.5, adm=adm, sigma_over_mu=10.0, dt=0.5)
    E1 = sum(vg.basis_stress_energy(m[a], u1[a], S1[a], gi)[0] for a in range(3))
    P1 = sum(vg.basis_stress_energy(m[a], u1[a], S1[a], gi)[1] for a in range(3))

    assert abs(E1 - E0) / E0 < 1e-13
    assert np.linalg.norm(P1 - P0) / np.linalg.norm(P0) < 1e-13


def test_1d_mfm_twostream_and_convergence():
    """Run 1D relativistic two-stream and density wave tests in Python twin."""
    # (A) Relativistic boosted two-stream: u = u_boosted of +/-1.2 boosted by v0 = 0.5
    N, L = 32, 1.0
    x = (np.arange(N) + 0.5) * (L / N)
    # Boost +/- 1.2 along x by beta = 0.5 (gam = 2/sqrt(3)): u' = gam*(u + beta*W)
    gam = 1.0 / math.sqrt(1.0 - 0.25)
    W_base = math.sqrt(1.0 + 1.2 * 1.2)
    u_p = gam * (1.2 + 0.5 * W_base)
    u_m = gam * (-1.2 + 0.5 * W_base)
    D = np.full((N, 2), 0.5)
    u = np.zeros((N, 2, 3))
    u[:, 0, 0] = u_p
    u[:, 1, 0] = u_m
    Sig = np.broadcast_to(1e-14 * np.eye(3), (N, 2, 3, 3)).copy()
    st = vg.init_mfm_1d(x, D, u, Sig, L)
    M0, P0, E0 = vg.total_invariants_1d(st)
    m_cell0 = np.sum(st.m, axis=1).copy()

    dt = 0.005
    for _ in range(40):
        vg.step_1d_mfm(st, dt)

    M1, P1, E1 = vg.total_invariants_1d(st)
    assert abs(M1 - M0) / M0 < 1e-13
    assert np.linalg.norm(P1 - P0) / np.linalg.norm(P0) < 1e-13
    assert abs(E1 - E0) / E0 < 1e-12
    assert np.max(np.abs(np.sum(st.m, axis=1) / m_cell0 - 1.0)) < 1e-12
    assert np.max(np.abs(st.u_bar[:, 0, 0] - u_p)) < 1e-11
    assert np.max(np.abs(st.u_bar[:, 1, 0] - u_m)) < 1e-11

    # (B) Relativistic density-wave convergence (N = 16 -> 32 -> 64)
    errs = []
    u_wave = 1.0
    v_wave = u_wave / math.sqrt(1.0 + u_wave * u_wave)
    t_end = 0.25
    for Nx in (16, 32, 64):
        xx = (np.arange(Nx) + 0.5) * (L / Nx)
        mod = 1.0 + 0.2 * np.cos(2.0 * math.pi * xx / L)
        DD = np.stack([0.5 * mod, 0.5 * mod], axis=-1)
        uu = np.zeros((Nx, 2, 3))
        uu[:, 0, 0] = +u_wave
        uu[:, 1, 0] = -u_wave
        SS = np.broadcast_to(1e-14 * np.eye(3), (Nx, 2, 3, 3)).copy()
        s = vg.init_mfm_1d(xx, DD, uu, SS, L)
        nsteps = 2 * Nx
        dt_w = t_end / nsteps
        for _ in range(nsteps):
            vg.step_1d_mfm(s, dt_w)
        exact_p = 0.5 * (1.0 + 0.2 * np.cos(2.0 * math.pi * (s.x - v_wave * t_end) / L))
        l1 = float(np.mean(np.abs(s.D[:, 0] - exact_p)))
        errs.append(l1)
    order = math.log2(errs[1] / errs[2])
    assert order > 1.75, f"Expected ~2nd order convergence, got errs={errs}, order={order:.2f}"


def test_exact_taub_shock_formula():
    """Cross-check exact_taub_double_shock satisfies all relativistic Rankine-Hugoniot jumps."""
    res = vg.exact_taub_double_shock(u0=1.2, rho0=1.0)
    W0, v0, Vs, D2, p2, e2 = (
        res["W0"], res["v0"], res["shock_speed"], res["D2"], res["p2"], res["e2"]
    )
    # Incoming right stream: D_1 = 1, u_1 = -1.2, v_1 = -v0, T^{00}_1 = W0, T^{0x}_1 = -u0, T^{xx}_1 = u0*v0
    # Downstream (rest): D_2 = D2, v_2 = 0, T^{00}_2 = e2, T^{0x}_2 = 0, T^{xx}_2 = p2
    assert abs(1.0 * (-v0 - Vs) - D2 * (0.0 - Vs)) < 1e-13
    assert abs((1.2 * v0 - (-1.2) * Vs) - p2) < 1e-13
    # Exact Taub shock check (above) + empty-slot & collisional 1D MFM tests
    assert abs((-1.2 - W0 * Vs) - (-e2 * Vs)) < 1e-13


def test_1d_mfm_empty_slot_and_collisional_taub():
    """Test (C) empty-basis relativistic stream injection and (D) colliding streams
    in collisionless vs strongly collisional Taub double-shock limits."""
    # (C) Empty-basis stream injection: u_x in {+1, 0, -1, -2}, inject +3.0 near x=0.5
    N, L, Nb = 48, 1.0, 4
    x = (np.arange(N) + 0.5) * (L / N)
    pi = 0.5 * np.exp(-((x - 0.5) / 0.06) ** 2)
    inj = pi > 1e-6
    D = np.zeros((N, Nb))
    u = np.zeros((N, Nb, 3))
    u[:, 0, 0] = 1.0; u[:, 1, 0] = 0.0; u[:, 2, 0] = -1.0; u[:, 3, 0] = -2.0
    D[:, 0] = 0.49; D[:, 1] = 0.02; D[:, 2] = 0.49; D[:, 3] = 1e-8
    u[inj, 3, 0] = 3.0
    D[inj, 3] = pi[inj]
    scale = (1.0 - pi[inj]) / (D[inj, 0] + D[inj, 1] + D[inj, 2])
    D[inj, :3] *= scale[:, None]
    Sig = np.broadcast_to(1e-8 * np.eye(3), (N, Nb, 3, 3)).copy()
    st_eb = vg.init_mfm_1d(x, D, u, Sig, L)
    # Also run velocity-only pairing for contrast
    st_vo = vg.init_mfm_1d(x, D, u, Sig, L)
    v_fast = 3.0 / math.sqrt(1.0 + 9.0)
    t_end = 0.12
    dt = 0.004
    for _ in range(int(round(t_end / dt))):
        vg.step_1d_mfm(st_eb, dt, pairing_mode="eb")
        vg.step_1d_mfm(st_vo, dt, pairing_mode="v_only")
    # Injected fast stream should advance past x=0.5 + v_fast*t_end ~ 0.614 in 'eb'
    fast_mass_ahead = np.sum(st_eb.m[(st_eb.x > 0.58) & (st_eb.u_bar[:, :, 0].max(axis=1) > 2.2)])
    assert fast_mass_ahead > 0.02

    # (D) Colliding relativistic streams: u = +/-1.0 in left/right halves of box [0, 1)
    Nc = 64
    xc = (np.arange(Nc) + 0.5) * (L / Nc)
    left = xc < 0.5
    Dc = np.full((Nc, 2), 1e-8)
    uc = np.zeros((Nc, 2, 3))
    uc[:, 0, 0] = 1.0
    uc[:, 1, 0] = -1.0
    Dc[left, 0] = 1.0 - 1e-8
    Dc[~left, 1] = 1.0 - 1e-8
    Sigc = np.broadcast_to(1e-10 * np.eye(3), (Nc, 2, 3, 3)).copy()

    st_cl = vg.init_mfm_1d(xc, Dc, uc, Sigc, L)
    st_hydro = vg.init_mfm_1d(xc, Dc, uc, Sigc, L)
    M0, P0, E0 = vg.total_invariants_1d(st_hydro)
    t_end_c = 0.15
    t_cl = 0.0
    while t_cl < t_end_c - 1e-14:
        dt_step = min(t_end_c - t_cl, 0.0025, 0.25 * float(np.min(st_cl.V)))
        vg.step_1d_mfm(st_cl, dt_step, sigma_over_mu=0.0)
        t_cl += dt_step

    t_hy = 0.0
    while t_hy < t_end_c - 1e-14:
        dt_step = min(t_end_c - t_hy, 0.0025, 0.25 * float(np.min(st_hydro.V)))
        vg.step_1d_mfm(st_hydro, dt_step, sigma_over_mu=500.0)
        t_hy += dt_step

    M1, P1, E1 = vg.total_invariants_1d(st_hydro)
    assert abs(M1 - M0) / M0 < 1e-12
    assert abs(E1 - E0) / E0 < 1e-11
    # Collisionless center (|x - 0.5| < 0.08) has D ~ 2.0 (interpenetrating streams)
    cen_cl = np.abs(st_cl.x - 0.5) < 0.06
    assert abs(np.mean(np.sum(st_cl.D[cen_cl], axis=1)) - 2.0) < 0.05

    # Collisional center (|x - 0.5| < 0.04) matches exact Taub double-shock post-shock density & energy
    ex_taub = vg.exact_taub_double_shock(u0=1.0, rho0=1.0)
    cen_hy = np.abs(st_hydro.x - 0.5) < 0.03
    D_cen_hy = float(np.mean(np.sum(st_hydro.D[cen_hy], axis=1)))
    D_min_hy = float(np.min(np.sum(st_hydro.D[np.abs(st_hydro.x - 0.5) < 0.025], axis=1)))
    assert abs(D_cen_hy - ex_taub["D2"]) / ex_taub["D2"] < 0.05
    assert D_min_hy > 0.94 * ex_taub["D2"]

    # Intermediate collisionality sigma/mu = 15 preserves exact cell mass (Bug 2 regression)
    st_mid = vg.init_mfm_1d(xc, Dc, uc, Sigc, L)
    m_mid0 = np.sum(st_mid.m, axis=1).copy()
    t_mid = 0.0
    while t_mid < t_end_c - 1e-14:
        dt_step = min(t_end_c - t_mid, 0.0025, 0.25 * float(np.min(st_mid.V)))
        vg.step_1d_mfm(st_mid, dt_step, sigma_over_mu=15.0)
        t_mid += dt_step
    assert np.max(np.abs(np.sum(st_mid.m, axis=1) / m_mid0 - 1.0)) < 1e-12


def test_valencia_c2p_and_noh_stationary_contact():
    """Verify exact Valencia Synge C2P round-trip and zero Noh flux on stationary contacts."""
    D_ref, th_ref = 2.4, 0.25
    w_ref, h_ref, _, _ = vg.synge_thermo(th_ref)
    v_ref = np.array([math.sqrt(1.0 - 1.0 / 2.25) * 0.8, 0.25, -0.1])
    U0_ref = 1.0 / math.sqrt(1.0 - float(np.dot(v_ref, v_ref)))
    rho0_ref = D_ref / U0_ref
    p_ref = rho0_ref * th_ref
    E_ref = D_ref * h_ref * U0_ref - p_ref
    P_ref = D_ref * h_ref * U0_ref * v_ref
    th_o, h_o, _, w_o, U0_o, rho0_o, p_o, v_o = vg.valencia_c2p_synge(D_ref, E_ref, P_ref)
    assert abs(th_o - th_ref) < 1e-13
    assert abs(U0_o - U0_ref) < 1e-13
    assert abs(p_o - p_ref) < 1e-13
    assert np.linalg.norm(v_o - v_ref) < 1e-13

    # Cold limit theta = 0
    th_c, h_c, cs2_c, w_c, U0_c, _, p_c, v_c = vg.valencia_c2p_synge(
        D_ref, math.sqrt(D_ref ** 2 + float(np.dot(P_ref, P_ref))), P_ref
    )
    assert th_c == 0.0 and h_c == 1.0 and cs2_c == 0.0 and p_c == 0.0

    # Stationary pressure-balanced contact discontinuity has zero Noh conduction
    wm_l, _, cs2_l, _ = vg.synge_thermo(0.5 / 3.0)
    wm_r, _, cs2_r, _ = vg.synge_thermo(0.5 / 1.0)
    Lc = dict(D=3.0, rho0=3.0, p=0.5, v=np.zeros(3), cs2=cs2_l, w_m=wm_l)
    Rc = dict(D=1.0, rho0=1.0, p=0.5, v=np.zeros(3), cs2=cs2_r, w_m=wm_r)
    assert abs(vg.noh_thermal_conduct_flux(Lc, Rc, 0.5)) < 1e-15


def test_3d_mfm_twostream_and_ic_builders():
    """Verify 3D periodic MFM conservation + oblique relativistic two-stream and IC builders."""
    nx, ny, nz = 4, 4, 4
    box = np.array([1.0, 1.0, 1.0])
    c = (np.arange(nx) + 0.5) / nx
    gx, gy, gz = np.meshgrid(c, c, c, indexing="ij")
    x = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N = len(x)
    D = np.full((N, 2), 0.5)
    u = np.zeros((N, 2, 3))
    u[:, 0] = np.array([0.8, 0.4, -0.2])
    u[:, 1] = np.array([-0.6, -0.3, 0.3])
    S = np.broadcast_to(1e-12 * np.eye(3), (N, 2, 3, 3)).copy()
    st = vg.init_mfm_3d(x, D, u, S, box)
    M0, P0, E0 = vg.total_invariants_3d(st)
    for _ in range(5):
        vg.step_3d_mfm(st, 0.02, n_perp=2)
    M1, P1, E1 = vg.total_invariants_3d(st)
    assert abs(M1 - M0) / M0 < 1e-13
    assert np.linalg.norm(P1 - P0) / np.linalg.norm(P0) < 1e-13
    assert abs(E1 - E0) / E0 < 1e-12

    xk, mk, uk, Sk = vg.make_ic_kerr_cloud(n_r=2, n_phi=8, n_z=2, Nb=2)
    assert xk.shape[1] == 3 and abs(np.sum(mk) - 1e-4) < 1e-16
    xc, mc, uc, Sc = vg.make_ic_cosmo_wave(n_lat=4, Nb=4)
    assert xc.shape == (64, 3) and mc.shape == (64, 4)
