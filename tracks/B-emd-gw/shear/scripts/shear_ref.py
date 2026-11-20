"""Exact and semi-analytic references of the shearing-dust test of Adamek et al.,
arXiv:2003.08014 v2 (source: kb-data/raw/arxiv/2003.08014/v2/src/draft.tex, cited as
draft.tex:<line>). Specification: ../SPEC.md.

Units: G = c = 1. H is the Hubble rate H_* of the reference Einstein-de Sitter model on
the initial slice; the code uses H = 1. tau is the paper's conformal time, tau_* = 2/H,
a = (tau/tau_*)^2; the code's clock is t_c = tau - tau_*.

Coordinates: 'paper' are those of draft.tex:149-158 (sheared); 'code' are
x' = x + (b/(2 pi H)) sin(2 pi y/L), in which the initial 3-metric is delta_ij (SPEC
section 2).
"""
import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

PI = np.pi


# ---------------------------------------------------------------------------------------
# closed-form linear prediction of the observable (draft.tex:262)

def cos_lin(b, HL):
    """cos(theta_lin) of draft.tex:262 (b dimensionless, HL = H_* L)."""
    integ, _ = quad(lambda xi: np.cos(xi)/(4.0*PI + HL*xi)**3, 0.0, 2.0*PI,
                    epsabs=0.0, epsrel=1e-13, limit=400)
    return b*((HL + 6.0)/(HL + 2.0)**3 + 32.0*PI**2/HL*integ)


def first_order_parts(b, L, H=1.0, coords="code"):
    """Independent first-order evaluation (my derivation, SPEC section 4 and JOURNAL):
    straight rays perturbed by the linear metric. Ray A (towards +x along y = 0) needs the
    launch slope s_A = (1/L) Int h(tau, 0) dtau, ray B (towards +y along x = 0)
    s_B = (1/L) Int h(tau, tau - tau_*) dtau, both over tau_* ... tau_* + L, and
    cos(theta) = s_A + s_B - h(tau_* + L, 0). Returns (s_A, s_B, h_end, cos)."""
    ts = 2.0/H
    sA = quad(lambda t: h_lin(t, 0.0, b, L, H, coords), ts, ts + L,
              epsabs=0.0, epsrel=1e-13, limit=400)[0]/L
    sB = quad(lambda t: h_lin(t, t - ts, b, L, H, coords), ts, ts + L,
              epsabs=0.0, epsrel=1e-13, limit=400)[0]/L
    he = h_lin(ts + L, 0.0, b, L, H, coords)
    return sA, sB, he, sA + sB - he


# ---------------------------------------------------------------------------------------
# initial data (draft.tex:149-182, 515, 520) and their form in the code's coordinates

def initial_data(y, b, L, H=1.0):
    """Fields of the initial slice at the positions y (array). Returns a dict with the
    paper's rho0, u^x, W, rho_ADM and the code-coordinate data: Ahat_xy, K, the rest-mass
    density per coordinate volume D = sqrt(gamma) rho0 W, the momentum density
    S_x = rho0 W u_x, and F(y) of the coordinate change."""
    y = np.asarray(y, dtype=float)
    k = 2.0*PI/L
    c, s = np.cos(k*y), np.sin(k*y)
    Q = 16.0*H**2*L**2 - 3.0*b**2*c**2
    R = Q**2 - 64.0*PI**2*b**2*s**2
    if np.any(R <= 0.0) or np.any(Q <= 0.0):
        raise ValueError("b outside the physical range (draft.tex:184)")
    rho0 = 3.0*R/(128.0*PI*L**2*Q)
    ux = -8.0*PI*b*s/np.sqrt(R)
    W = Q/np.sqrt(R)
    D = 3.0*np.sqrt(R)/(128.0*PI*L**2)
    rho_adm = 3.0*H**2/(8.0*PI) - 9.0*b**2*c**2/(128.0*PI*L**2)
    return {"c": c, "s": s, "Q": Q, "R": R, "rho0": rho0, "ux": ux, "W": W, "D": D,
            "rho_adm": rho_adm, "Sx": rho0*W*ux, "Ahat_xy": 3.0*b/(4.0*L)*c,
            "K": -3.0*H*np.ones_like(y), "F": b/(2.0*PI*H)*s}


def b_max(HL):
    """Upper end of the physical range of b at H = 1 (draft.tex:184)."""
    bm = 2.0*HL**2/PI
    if HL > PI*np.sqrt(2.0/3.0):
        bm = min(bm, 4.0*np.sqrt(3.0*HL**2 - PI**2)/3.0)
    return bm


# ---------------------------------------------------------------------------------------
# linear solution (draft.tex:235-241) in both coordinate systems

def scale_factor(tau, H=1.0):
    return (tau*H/2.0)**2


def h_lin(tau, y, b, L, H=1.0, coords="code"):
    """gamma_xy / a^2 of the linear solution (harmonic slicing alpha = a, zero shift).
    paper: (b tau/(2L)) cos / a^2 = (b/(H L)) (tau_*/tau)^3 cos (draft.tex:238);
    code:  (b/(H L)) [(tau_*/tau)^3 - 1] cos (SPEC section 3)."""
    ts = 2.0/H
    r3 = (ts/tau)**3
    amp = b/(H*L)*(r3 - (1.0 if coords == "code" else 0.0))
    return amp*np.cos(2.0*PI*y/L)


def h_lin_y(tau, y, b, L, H=1.0, coords="code"):
    ts = 2.0/H
    r3 = (ts/tau)**3
    amp = b/(H*L)*(r3 - (1.0 if coords == "code" else 0.0))
    return -amp*(2.0*PI/L)*np.sin(2.0*PI*y/L)


def gamma_xy_lin(t_code, y, b, L, H=1.0):
    """gamma'_xy of the code at code time t_code (first order in b)."""
    tau = t_code + 2.0/H
    return scale_factor(tau, H)**2*h_lin(tau, y, b, L, H, "code")


# ---------------------------------------------------------------------------------------
# geodesic shooting through the linear metric (conformal metric -dtau^2 + (delta + h)),
# null geodesics are conformally invariant; directions at O do not depend on a

def _rhs(tau, Y, kx, b, L, H, coords):
    x, y, ky = Y
    h = h_lin(tau, y, b, L, H, coords)
    hy = h_lin_y(tau, y, b, L, H, coords)
    den = 1.0 - h*h
    gxx = 1.0/den
    gxy = -h/den
    gyy = 1.0/den
    k0 = np.sqrt(gxx*kx*kx + 2.0*gxy*kx*ky + gyy*ky*ky)
    dgxx = 2.0*h*hy/den**2
    dgxy = -hy*(1.0 + h*h)/den**2
    dky = -(dgxx*kx*kx + 2.0*dgxy*kx*ky + dgxx*ky*ky)/(2.0*k0)
    return [(gxx*kx + gxy*ky)/k0, (gxy*kx + gyy*ky)/k0, dky]


def launch_k(c, tau0, y0, b, L, H, coords):
    """k_i = gamma_ij c^j / |c| (the code's launch, nrpic.cpp 455-480), 2D."""
    h = h_lin(tau0, y0, b, L, H, coords)
    g = np.array([[1.0, h], [h, 1.0]])
    kc = g @ np.asarray(c, float)
    return kc/np.sqrt(np.asarray(c, float) @ kc)


def trace(ray, s, b, L, H=1.0, coords="code", rtol=1e-12):
    """Ray 'A' (towards +x from O, direction (1, s)) or 'B' (towards +y, (s, 1)), emitted
    at tau_* from O. Integrates to the crossing of x = L (A) or y = L (B); returns
    (miss, tau_arr, k_arr) with miss the transverse coordinate at the crossing."""
    ts = 2.0/H
    c = (1.0, s) if ray == "A" else (s, 1.0)
    k = launch_k(c, ts, 0.0, b, L, H, coords)
    idx = 0 if ray == "A" else 1

    def ev(tau, Y, *args):
        return Y[idx] - L
    ev.terminal = True
    ev.direction = 1
    scale = max(abs(b)*L, 1e-300)
    sol = solve_ivp(_rhs, (ts, ts + 3.0*L + 10.0), [0.0, 0.0, k[1]],
                    args=(k[0], b, L, H, coords), method="DOP853", rtol=rtol,
                    atol=[1e-13*scale, 1e-13*scale, 1e-13*abs(b) + 1e-300],
                    events=ev, dense_output=False)
    te = float(sol.t_events[0][0])
    Ye = sol.y_events[0][0]
    miss = Ye[1] if ray == "A" else Ye[0]
    return miss, te, np.array([k[0], Ye[2]])


def shoot(ray, b, L, H=1.0, coords="code", s_guess=None):
    """Launch slope s that makes the ray hit the observer at O; returns (s, tau, k)."""
    if s_guess is None:
        sA, sB, _, _ = first_order_parts(b, L, H, coords)
        s_guess = sA if ray == "A" else sB
    w = 0.5*abs(s_guess) + 10.0*abs(b)/max(H*L, 1.0)*1e-3 + 1e-300
    lo, hi = s_guess - w, s_guess + w
    f = lambda s: trace(ray, s, b, L, H, coords)[0]
    flo, fhi = f(lo), f(hi)
    n = 0
    while flo*fhi > 0.0 and n < 30:
        w *= 2.0
        lo, hi = s_guess - w, s_guess + w
        flo, fhi = f(lo), f(hi)
        n += 1
    s = brentq(f, lo, hi, xtol=1e-15*max(abs(s_guess), 1e-300), rtol=1e-15, maxiter=200)
    _, te, k = trace(ray, s, b, L, H, coords)
    return s, te, k


def cos_theta_traced(b, L, H=1.0, coords="code"):
    """cos(theta) at O from the two shot rays; gamma^ij at the later arrival. (The
    parallel transport of the earlier arrival is of third order in b and left out.)"""
    _, tA, kA = shoot("A", b, L, H, coords)
    _, tB, kB = shoot("B", b, L, H, coords)
    tl = max(tA, tB)
    h = h_lin(tl, 0.0, b, L, H, coords)
    gi = np.array([[1.0, -h], [-h, 1.0]])/(1.0 - h*h)
    num = kA @ gi @ kB
    return num/np.sqrt((kA @ gi @ kA)*(kB @ gi @ kB)), tA, tB
