"""Spherical top-hat in an Einstein-de Sitter background: the exact cycloid.

Reference solution for the Newtonian precursor scan of track A (A-pre-3, decision 0010).
Code units of arXiv:2605.04487 (its Eq. code_units, source line 2159): G = c = 1, length
unit c/H_k, so H_k = 1, t_k = 2/(3 H_k) = 2/3, a(t) = (t/t_k)^(2/3) with a(t_k) = 1, the
mass of the Lagrangian unit sphere M = M_k = 1/2 and its Schwarzschild radius r_g = 1.

A homogeneous sphere of mass M, radius R0 and radial velocity V0 at time t0 moves on
    R = A (1 - cos th),  t = t_off + B (th - sin th),  A = GM/(-2E),  B = sqrt(A^3/(GM)),
with E = V0^2/2 - GM/R0 < 0 (bound). Turnaround at th = pi, collapse at th = 2 pi.

Zel'dovich data (growing mode D = a, eigenvalue lambda, Lagrangian radius R_L):
    R0 = a0 (1 - a0 lambda) R_L,  V0 = H0 a0 (1 - 2 a0 lambda) R_L.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

G = 1.0
T_K = 2.0 / 3.0          # horizon-entry time, H_k = 1
M_K = 0.5                # mass of the unit Lagrangian sphere at background density
R_G = 2.0 * G * M_K      # Schwarzschild radius of M_K (= 1)

# closed-form EdS top-hat constants [BACKGROUND; computed here from the cycloid]
DELTA_L_TA = 3.0 / 20.0 * (6.0 * np.pi) ** (2.0 / 3.0)    # 1.0624
DELTA_L_C = 3.0 / 20.0 * (12.0 * np.pi) ** (2.0 / 3.0)    # 1.6865
ONE_PLUS_DELTA_TA = 9.0 * np.pi ** 2 / 16.0                # 5.5517


def a_of_t(t):
    return (np.asarray(t) / T_K) ** (2.0 / 3.0)


def t_of_a(a):
    return T_K * np.asarray(a) ** 1.5


def hubble(t):
    return 2.0 / (3.0 * np.asarray(t))


def rho_b(t):
    """Background density 3 H^2/(8 pi G) = 1/(6 pi G t^2)."""
    return 1.0 / (6.0 * np.pi * G * np.asarray(t) ** 2)


def za_sphere(lam, a0, RL=1.0):
    """Zel'dovich radius, velocity and time at scale factor a0 for eigenvalue lam."""
    t0 = float(t_of_a(a0))
    H0 = float(hubble(t0))
    return a0 * (1.0 - a0 * lam) * RL, H0 * a0 * (1.0 - 2.0 * a0 * lam) * RL, t0


def cycloid(R0, V0, t0, M=M_K):
    """Cycloid through (t0, R0, V0). Returns a dict with A, B, t_off, th0, t_ta, t_c,
    R_max. Raises for unbound data."""
    E = 0.5 * V0 ** 2 - G * M / R0
    if E >= 0.0:
        raise ValueError("unbound sphere: E >= 0")
    A = G * M / (-2.0 * E)
    B = np.sqrt(A ** 3 / (G * M))
    c = np.clip(1.0 - R0 / A, -1.0, 1.0)
    th0 = np.arccos(c)
    if V0 < 0.0:
        th0 = 2.0 * np.pi - th0
    t_off = t0 - B * (th0 - np.sin(th0))
    return dict(E=E, A=A, B=B, th0=th0, t_off=t_off, t_ta=t_off + np.pi * B,
                t_c=t_off + 2.0 * np.pi * B, R_max=2.0 * A)


def cycloid_R(cyc, t):
    """Radius on the cycloid at time t, 0 <= th <= 2 pi (bracketed root of th - sin th)."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.empty_like(t)
    for k, tk in enumerate(t):
        x = (tk - cyc["t_off"]) / cyc["B"]          # th - sin th, in [0, 2 pi]
        x = min(max(x, 0.0), 2.0 * np.pi)
        th = brentq(lambda u: u - np.sin(u) - x, 0.0, 2.0 * np.pi, xtol=1e-15, rtol=1e-15)
        out[k] = cyc["A"] * (1.0 - np.cos(th))
    return out


def integrate_sphere(R0, V0, t0, t1, M=M_K, rtol=1e-12, atol=1e-14, rstop=1e-3):
    """Direct integration of R'' = -GM/R^2 (reference check of the closed form).
    Stops at turnaround (event 0, not terminal) and when R falls below rstop R0 on the
    way in (event 1, terminal)."""
    def rhs(t, y):
        return [y[1], -G * M / y[0] ** 2]

    def ev_ta(t, y):
        return y[1]
    ev_ta.direction = -1

    def ev_in(t, y):
        return y[0] - rstop * R0
    ev_in.terminal = True
    ev_in.direction = -1
    return solve_ivp(rhs, (t0, t1), [R0, V0], method="DOP853", rtol=rtol, atol=atol,
                     events=[ev_ta, ev_in], dense_output=True)


def za_tophat_summary(lam, a0=None):
    """Turnaround and collapse of the Zel'dovich-started sphere; a0 defaults to the
    turnaround start of 2605.04487, a0 = 1/(2 lam) (its Eq. turn_time, line 1053)."""
    if a0 is None:
        a0 = 0.5 / lam
    R0, V0, t0 = za_sphere(lam, a0)
    cyc = cycloid(R0, V0, t0)
    a_c = float(a_of_t(cyc["t_c"]))
    a_ta = float(a_of_t(cyc["t_ta"]))
    return dict(lam=lam, a0=a0, t0=t0, R0=R0, V0=V0, t_ta=cyc["t_ta"], t_c=cyc["t_c"],
                a_ta=a_ta, a_c=a_c, R_max=cyc["R_max"],
                deltaL_ta=3.0 * lam * a_ta, deltaL_c=3.0 * lam * a_c,
                t_ta_over_tk=cyc["t_ta"] / T_K, t_c_over_tk=cyc["t_c"] / T_K,
                t_c_za_over_tk=float(t_of_a(1.0 / lam)) / T_K)
