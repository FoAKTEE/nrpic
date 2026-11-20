"""Fourier symbol of the whole linearized Z4c system of this repository's AthenaK about
flat space (alpha = chi = 1, zero shift), for one mode exp(i k.x) on the mesh.

Why (wave 3, round 1): for a direction whose discrete divergence does not vanish
(k = 2 pi (1, 2, 0)), the continuum-TT data of `z4c_linear_wave` are not divergence-free
for the code's first-derivative stencil. The two-variable predictor of predict.py
(h, At only) then misses the coupling to Gamma^i, Theta, Khat, chi and alpha. This module
keeps all of them (19 complex amplitudes):

    y = [h_ab (3x3 symmetric, stored in full), A_ab (3x3), Gamma^a (3), Khat, Theta,
         chi - 1, alpha - 1],

with the right-hand sides of athenak/src/z4c/z4c_calcrhs.cpp linearized (line numbers of
that file on main = core/requests-b, which does not change it):
    d_t h_ab   = -2 A_ab                                              (line 670)
    d_t A_ab   = TF[-D_a D_b alpha + R_ab + Rphi_ab]                  (lines 674-677)
    R_ab       = (1/2)(d_b Gamma_a + d_a Gamma_b) - (1/2) sum_c d_c d_c h_ab    (436-442)
    Rphi_ab    = -2 d_a d_b phi - 2 delta_ab lap phi,  phi = -(chi - 1)/4      (477-481)
    d_t Gamma^a = -(2/3) d_a (2 Khat + Theta) - 2 kappa1 (Gamma^a - Gamma_d^a),
                  Gamma_d^a = d_b h_ab - (1/2) d_a h_bb                       (551, 656-658)
    d_t Khat   = -lap alpha + kappa1 Theta                            (627-629)
    d_t Theta  = (1/2) R - 2 kappa1 Theta,  R = tr(R_ab + Rphi_ab)    (568, 646-647)
    d_t chi    = (2/3)(Khat + 2 Theta)                                (chi_psi_power = -4)
    d_t alpha  = -(1/3) Khat   (lapse_harmonic = 1/3 times alpha, lines 694-699)
plus Kreiss-Oliger dissipation -d y on every variable (lines 768-779). Derivatives by the
stencils of athenak/src/utils/finite_diff.hpp at nghost = 4: d_a -> i s_a with the
sixth-order first derivative, d_a d_a -> -q_a with the sixth-order second derivative,
d_a d_b (a != b) -> -s_a s_b (Dxy is the product of two first-derivative stencils).
The algebraic constraints (det = 1, tr A = 0) act at second order only: the linear system
keeps tr h = tr A = 0.

Time integration: the code's rk4 (RK4()4[2S]) has the classical stability polynomial on a
linear autonomous system (predict.py), so a step is sum_{j<=4} (dt M)^j / j!.
"""
import numpy as np

from .predict import symbol_d2, step_times, output_times

NV = 25          # 9 + 9 + 3 + 4 (h and A stored as full 3x3)
IH, IA, IG, IK, ITH, ICHI, IAL = 0, 9, 18, 21, 22, 23, 24
C1 = ((1, 3.0 / 4.0), (2, -3.0 / 20.0), (3, 1.0 / 60.0))


def symbols(kvec, dx, ng=4, sigma=0.5):
    """s_a (first derivative: d_a -> i s_a), q_a (d_a d_a -> -q_a), KO rate d."""
    kvec = np.asarray(kvec, float)
    dx = np.asarray(dx, float)
    th = kvec * dx
    s = np.array([2.0 * sum(c * np.sin(m * t) for m, c in C1) for t in th]) / dx
    q = -symbol_d2(ng, th) / dx ** 2
    d = float(np.sum(sigma * 2.0 ** (-2 * ng) * (2 * np.sin(th / 2)) ** (2 * ng) / dx))
    return s, q, d


def rhs_matrix(kvec, dx, kappa1, ng=4, sigma=0.5):
    """M with d_t y = M y for the mode exp(i k.x)."""
    s, q, d = symbols(kvec, dx, ng, sigma)
    Q = float(np.sum(q))
    Dd = -np.outer(s, s)
    for a in range(3):
        Dd[a, a] = -q[a]
    I3 = np.eye(3)

    def rhs(y):
        h = y[IH:IH + 9].reshape(3, 3)
        A = y[IA:IA + 9].reshape(3, 3)
        G = y[IG:IG + 3]
        Kh, Th, chi, al = y[IK], y[ITH], y[ICHI], y[IAL]
        R = 0.5j * (np.outer(G, s) + np.outer(s, G)) + 0.5 * Q * h
        Rphi = 0.5 * Dd * chi - 0.5 * Q * chi * I3
        X = -Dd * al + R + Rphi
        trX = np.trace(X)
        dA = X - I3 * trX / 3.0
        Rs = np.trace(R + Rphi)
        Gd = 1j * (h @ s) - 0.5j * s * np.trace(h)
        dG = -(2.0 / 3.0) * 1j * s * (2.0 * Kh + Th) - 2.0 * kappa1 * (G - Gd)
        out = np.empty(NV, complex)
        out[IH:IH + 9] = (-2.0 * A).ravel()
        out[IA:IA + 9] = dA.ravel()
        out[IG:IG + 3] = dG
        out[IK] = Q * al + kappa1 * Th
        out[ITH] = 0.5 * Rs - 2.0 * kappa1 * Th
        out[ICHI] = (2.0 / 3.0) * (Kh + 2.0 * Th)
        out[IAL] = -(1.0 / 3.0) * Kh
        return out - d * y

    M = np.empty((NV, NV), complex)
    for j in range(NV):
        e = np.zeros(NV, complex)
        e[j] = 1.0
        M[:, j] = rhs(e)
    return M


def rk4_step_matrix(M, dt):
    Z = dt * M
    out = np.eye(len(M), dtype=complex)
    term = np.eye(len(M), dtype=complex)
    for j in range(1, 5):
        term = term @ Z / j
        out = out + term
    return out


def lambda_projector(khat):
    """Lambda_ab,cd as a (9, 9) matrix acting on h stored in full (row-major)."""
    P = np.eye(3) - np.outer(khat, khat)
    L = np.einsum("ac,bd->abcd", P, P) - 0.5 * np.einsum("ab,cd->abcd", P, P)
    L = 0.5 * (L + np.einsum("abcd->abdc", L))
    return L.reshape(9, 9)


def evolve_linear_wave(kvec, L, N, tlim, dt_out, amp, amp_x, ph_x, cfl=0.25, kappa1=0.02,
                       ng=4, sigma=0.5):
    """State at +k at the output times for the data of z4c_linear_wave (core/requests-b):
    h = amp e+ sin(P) + amp_x ex sin(P + ph_x), A = (|k|/2)[amp e+ cos(P) + ...],
    everything else zero. kvec angular. Returns t, ys (n_out, 25), and the measures of
    waves/wlib/refs.py conventions: P, X (from Lambda h), P', X' (from -2 Lambda A),
    the non-TT fraction at +k, |Gamma|, Theta, Khat."""
    from .refs import basis
    kvec = np.asarray(kvec, float)
    kn = float(np.linalg.norm(kvec))
    dx = np.asarray(L, float) / np.asarray(N, float)
    ep, ex, _, _ = basis(kvec)
    y0 = np.zeros(NV, complex)
    h0 = amp * ep / 2j + amp_x * np.exp(1j * ph_x) * ex / 2j
    A0 = (kn / 2.0) * (amp * ep / 2.0 + amp_x * np.exp(1j * ph_x) * ex / 2.0)
    y0[IH:IH + 9] = h0.ravel()
    y0[IA:IA + 9] = A0.ravel()
    M = rhs_matrix(kvec, dx, kappa1, ng, sigma)
    ts = step_times(tlim, lambda t: cfl * dx.min())
    idx = set(output_times(ts, dt_out).tolist())
    G_full = rk4_step_matrix(M, ts[1] - ts[0])
    ys, tout, y = [], [], y0.copy()
    for i in range(len(ts)):
        if i in idx:
            ys.append(y.copy())
            tout.append(ts[i])
        if i + 1 < len(ts):
            dt = ts[i + 1] - ts[i]
            Gs = G_full if abs(dt - (ts[1] - ts[0])) < 1e-14 else rk4_step_matrix(M, dt)
            y = Gs @ y
    ys = np.array(ys)
    Lam = lambda_projector(kvec / kn)
    h = ys[:, IH:IH + 9]
    A = ys[:, IA:IA + 9]
    hTT = h @ Lam.T
    hdTT = -2.0 * (A @ Lam.T)
    P = 0.5 * hTT @ ep.ravel()
    X = 0.5 * hTT @ ex.ravel()
    Pd = 0.5 * hdTT @ ep.ravel()
    Xd = 0.5 * hdTT @ ex.ravel()
    nonTT = np.linalg.norm(h - hTT, axis=1) / np.linalg.norm(hTT, axis=1)
    return {"t": np.array(tout), "y": ys, "P": P, "X": X, "Pd": Pd, "Xd": Xd,
            "nonTT_mode": nonTT, "Gamma": ys[:, IG:IG + 3], "Theta": ys[:, ITH],
            "Khat": ys[:, IK], "nsteps": len(ts) - 1,
            "div_rel": float(np.linalg.norm(h0 @ symbols(kvec, dx, ng, sigma)[0])
                             / (kn * np.linalg.norm(h0)))}
