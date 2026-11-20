"""Tests of the references of the shear package (SPEC.md; predictions P1, P2)."""
import os
import sys

import numpy as np
import pytest
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
import shear_ref as sr  # noqa: E402

HLS = [2.0**n for n in range(-7, 3)]


# ---------------------------------------------------------------------------------------
# symbolic checks (P2)

def _sym():
    y, b, L, H = sp.symbols("y b L H", positive=True)
    c, s = sp.cos(2*sp.pi*y/L), sp.sin(2*sp.pi*y/L)
    f1 = b/(H*L)*c
    g = sp.Matrix([[1, f1, 0], [f1, 1 + f1**2, 0], [0, 0, 1]])          # draft.tex:149-152
    K = -sp.Matrix([[H, b/(4*L)*c, 0], [b/(4*L)*c, H - b**2/(2*H*L**2)*c**2, 0],
                    [0, 0, H]])                                          # draft.tex:154-158
    Q = 16*H**2*L**2 - 3*b**2*c**2
    R = Q**2 - 64*sp.pi**2*b**2*s**2
    rho0 = 3*R/(128*sp.pi*L**2*Q)                                        # draft.tex:177
    ux = -8*sp.pi*b*s/sp.sqrt(R)                                         # draft.tex:180
    return y, b, L, H, c, s, g, K, Q, R, rho0, ux


def _christoffel(g, X):
    gi = g.inv()
    n = 3
    G = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                G[i][j][k] = sp.simplify(sum(gi[i, l]*(sp.diff(g[l, j], X[k])
                                         + sp.diff(g[l, k], X[j]) - sp.diff(g[j, k], X[l]))
                                         for l in range(n))/2)
    return G


def test_sheared_slice_symbolic():
    y, b, L, H, c, s, g, K, Q, R, rho0, ux = _sym()
    x, z = sp.symbols("x z")
    X = (x, y, z)
    G = _christoffel(g, X)
    # Ricci tensor of the 3-metric (in 3D it vanishes iff Riemann does)
    Ric = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            Ric[i, j] = sp.simplify(sum(sp.diff(G[k][i][j], X[k]) - sp.diff(G[k][i][k], X[j])
                                        + sum(G[k][k][l]*G[l][i][j] - G[k][j][l]*G[l][i][k]
                                              for l in range(3)) for k in range(3)))
    assert Ric == sp.zeros(3, 3)
    # the coordinate change x = x' - F(y'): gamma' = delta, K' as in SPEC section 2
    F1 = b/(H*L)*c
    J = sp.Matrix([[1, -F1, 0], [0, 1, 0], [0, 0, 1]])   # J[k, i] = d x^k / d x'^i
    gp = sp.simplify(J.T*g*J)
    Kp = sp.simplify(J.T*K*J)
    assert gp == sp.eye(3)
    assert sp.simplify(Kp - (-H*sp.eye(3) + sp.Matrix([[0, 3*b/(4*L)*c, 0],
                                                       [3*b/(4*L)*c, 0, 0],
                                                       [0, 0, 0]]))) == sp.zeros(3, 3)
    # constraints in the paper's coordinates (alpha = 1, u^0 = W): draft.tex:171-172
    gi = g.inv()
    Kup = sp.simplify(gi*K*gi)
    trK = sp.simplify(sum(gi[i, j]*K[i, j] for i in range(3) for j in range(3)))
    assert sp.simplify(trK + 3*H) == 0
    W = Q/sp.sqrt(R)
    ham = trK**2 - sum(K[i, j]*Kup[i, j] for i in range(3) for j in range(3)) \
        - 16*sp.pi*rho0*W**2
    assert sp.simplify(ham) == 0
    T = sp.simplify(Kup - gi*trK)
    for i in range(3):
        divT = sum(sp.diff(T[i, j], X[j]) for j in range(3)) \
            + sum(G[i][j][k]*T[k, j] + G[j][j][k]*T[i, k] for j in range(3) for k in range(3))
        u_up = [ux, 0, 0][i]
        assert sp.simplify(divT - 8*sp.pi*rho0*u_up*W) == 0
    # mass shell with the flat metric of the code coordinates: W^2 = 1 + (u_x)^2
    assert sp.simplify(W**2 - 1 - ux**2) == 0
    # momentum constraint in the code coordinates: d_y K'^{xy} = 8 pi rho0 W u^x
    assert sp.simplify(sp.diff(Kp[0, 1], y) - 8*sp.pi*rho0*W*ux) == 0
    # rho_ADM (draft.tex:515) and W (draft.tex:520)
    assert sp.simplify(rho0*W**2 - (3*H**2/(8*sp.pi) - 9*b**2*c**2/(128*sp.pi*L**2))) == 0


def test_linear_solution_slicing():
    y, b, L, H = sp.symbols("y b L H", positive=True)
    tau = sp.symbols("tau", positive=True)
    ts = 2/H
    c, s = sp.cos(2*sp.pi*y/L), sp.sin(2*sp.pi*y/L)
    a = (tau/ts)**2
    gxy = b*tau/(2*L)*c                                     # draft.tex:238
    g = sp.Matrix([[a**2, gxy, 0], [gxy, a**2, 0], [0, 0, a**2]])
    alpha = a
    # matches the initial slice at first order in b
    eps = sp.symbols("eps")
    gs = g.subs(b, eps*b)
    g0 = sp.Matrix([[1, eps*b/(H*L)*c, 0], [eps*b/(H*L)*c, 1, 0], [0, 0, 1]])
    assert sp.simplify(gs.subs(tau, ts) - g0) == sp.zeros(3, 3)
    Kl = -sp.diff(g, tau)/(2*alpha)
    K0 = -sp.Matrix([[H, b/(4*L)*c, 0], [b/(4*L)*c, H, 0], [0, 0, H]])
    assert sp.simplify(Kl.subs(tau, ts) - K0) == sp.zeros(3, 3)
    # alpha = gamma^(1/6) at first order in b (f = 1/3); gamma^(1/2) = a^3 rules out f = 1
    det = g.det()
    ratio = sp.series((det.subs(b, eps*b))**sp.Rational(1, 6)/alpha, eps, 0, 2).removeO()
    assert sp.simplify(ratio - 1) == 0
    # the transformed linear solution of SPEC section 3
    F1 = b/(H*L)*c
    gpxy = sp.expand(gxy - F1*a**2)
    target = a**2*b/(H*L)*c*((ts/tau)**3 - 1)
    assert sp.simplify(gpxy - target) == 0
    # draft.tex:254 with B_x of draft.tex:246: d_y^2 B_x = d_y d_tau (gamma_xy / alpha^2)
    Bx = -3*b*ts**4/(4*sp.pi*tau**4)*s
    assert sp.simplify(sp.diff(Bx, y, 2) - sp.diff(sp.diff(gxy/alpha**2, tau), y)) == 0


# ---------------------------------------------------------------------------------------
# closed form against the first-order evaluation and the traced rays (P1)

@pytest.mark.parametrize("HL", HLS)
def test_formula_equals_first_order(HL):
    b = 1.0
    for coords in ("code", "paper"):
        _, _, _, c1 = sr.first_order_parts(b, HL, 1.0, coords)
        assert abs(c1/sr.cos_lin(b, HL) - 1.0) < 1e-10


def test_formula_limits():
    assert abs(sr.cos_lin(1.0, 1e-4)/0.75 - 1.0) < 1e-3
    assert abs(sr.cos_lin(1.0, 1e4)*1e8/2.0 - 1.0) < 2e-3


@pytest.mark.parametrize("HL", HLS)
def test_traced_rays_equal_formula(HL):
    b = 1e-7*HL**2      # beta = 1e-7: second-order effects far below the tolerance
    ct, tA, tB = sr.cos_theta_traced(b, HL, 1.0, "code")
    assert abs(ct/sr.cos_lin(b, HL) - 1.0) < 1e-6
    ctp, _, _ = sr.cos_theta_traced(b, HL, 1.0, "paper")
    assert abs(ctp/sr.cos_lin(b, HL) - 1.0) < 1e-6


def test_initial_data_numbers():
    L, b = 1.0, 0.5
    y = np.linspace(-0.5, 0.5, 101)
    d = sr.initial_data(y, b, L)
    assert np.allclose(d["rho0"]*d["W"]**2, d["rho_adm"], rtol=1e-14, atol=0)
    assert np.allclose(d["W"]**2, 1.0 + d["ux"]**2, rtol=1e-14, atol=0)
    assert np.allclose(d["D"], d["rho0"]*d["W"], rtol=1e-14, atol=0)
    assert sr.b_max(4.0) < 2.0*16.0/np.pi and 0.5*16 < sr.b_max(4.0)
    with pytest.raises(ValueError):
        sr.initial_data(y, 0.7, 1.0)
