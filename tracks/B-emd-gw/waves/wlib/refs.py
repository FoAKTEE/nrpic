"""Exact references of the two linear-wave tests.

Conventions (gw_diag): h_ij = tilde gamma_ij - delta_ij (conformal metric), polarization
basis tt.pol_basis(khat) (u = theta-hat, v = phi-hat, e+ = uu - vv, ex = uv + vu). For a
field f on the mesh the mode coefficient at the angular wavevector k is
    c_k[f] = (1/N) sum_cells f(x) exp(-i k.x)        (x = cell centres, explicit),
and the polarization amplitudes of a symmetric tensor field are
    P = (1/2) e+_ij c_k[h_ij],   X = (1/2) ex_ij c_k[h_ij].
A primed amplitude is the derivative with respect to the coordinate time t of the run.

Test F (flat, oblique). Problem generator z4c_linear_wave of core/requests-b
(athenak/src/pgen/tests/z4c_linear_wave.cpp, header lines 15-20 on that branch):
    h = amp e+ sin(Phi) + amp_cross ex sin(Phi + phase_cross),
    Phi = k.x - |k| t,  k = 2 pi (kx1, kx2, kx3)  (kx in cycles per unit length),
so at +k:  P = amp/(2i) e^{-i|k|t},  X = amp_cross e^{i phase_cross}/(2i) e^{-i|k|t},
P' = -i|k| P, X' = -i|k| X.

Test X (expanding box, matter at rest). Background of cosmo/README.md ("Units and gauge"):
G = c = 1, H = 1 at a = 1, matter only, lapse d_t alpha = -(1/3) alpha^2 K, zero shift, so
t is conformal time, alpha = a = (1 + t/2)^2, calH = a'/a = 1/(1 + t/2). With s = t + 2 a
tensor mode obeys
    h'' + (4/s) h' + k^2 h = 0,     solutions j_1(ks)/(ks), y_1(ks)/(ks).
The initial slice is conformally flat (h = 0 at t = 0) with h' = sum_p eps_p e^p
cos(k.x + phi_p), so h = T(s) sum_p eps_p e^p cos(k.x + phi_p) with T(2) = 0, T'(2) = 1:
    P = T eps_+ e^{i phi_+}/2,  X = T eps_x e^{i phi_x}/2,  P' = T' eps_+ e^{i phi_+}/2, ...
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn, spherical_yn

from . import HERE  # noqa: F401  (sets sys.path for gwdiag)
from gwdiag.tt import pol_basis


# ---------------------------------------------------------------------------------------
# mode coefficients

def mode_coeff(f, grid, kvec):
    """c_k[f] = (1/N) sum f exp(-i k.x) over the trailing (nz, ny, nx) axes."""
    X, Y, Z = grid.mesh()
    ph = np.exp(-1j * (kvec[0] * X + kvec[1] * Y + kvec[2] * Z))
    return np.tensordot(f, ph, axes=([-3, -2, -1], [0, 1, 2])) / grid.ncell


def basis(kvec):
    """e+, ex (3, 3) for the direction of kvec."""
    kh = np.asarray(kvec, float) / np.linalg.norm(kvec)
    ep, ex, u, v = pol_basis(kh.reshape(3, 1, 1, 1))
    return ep[..., 0, 0, 0], ex[..., 0, 0, 0], u[:, 0, 0, 0], v[:, 0, 0, 0]


def pol_amplitudes(h, grid, kvec):
    """(P, X) of a symmetric tensor field at +k."""
    C = mode_coeff(h, grid, kvec)            # (3, 3) complex
    ep, ex, _, _ = basis(kvec)
    return 0.5 * np.sum(ep * C), 0.5 * np.sum(ex * C)


def tensor_field(P, X, grid, kvec):
    """Real symmetric field 2 Re[(P e+ + X ex) exp(i k.x)] (its amplitudes at +k are P, X)."""
    ep, ex, _, _ = basis(kvec)
    Xg, Yg, Zg = grid.mesh()
    ph = np.exp(1j * (kvec[0] * Xg + kvec[1] * Yg + kvec[2] * Zg))
    C = P * ep + X * ex
    return 2.0 * np.real(C[:, :, None, None, None] * ph)


# ---------------------------------------------------------------------------------------
# test F: flat travelling wave

def flat_amplitudes(t, kn, amp, amp_x, ph_x):
    """(P, X, P', X') at +k of the z4c_linear_wave solution; kn = |k| (angular)."""
    e = np.exp(-1j * kn * np.asarray(t, float))
    P = amp / 2j * e
    X = amp_x * np.exp(1j * ph_x) / 2j * e
    return P, X, -1j * kn * P, -1j * kn * X


# ---------------------------------------------------------------------------------------
# test X: matter-dominated background and the tensor mode

def background(t):
    """a, calH = a'/a, alpha (= a) of the matter-dominated background in conformal time."""
    t = np.asarray(t, float)
    a = (1.0 + 0.5 * t) ** 2
    return a, 1.0 / (1.0 + 0.5 * t), a


def _u(kn, s):
    x = kn * s
    j, y = spherical_jn(1, x), spherical_yn(1, x)
    jd, yd = spherical_jn(1, x, derivative=True), spherical_yn(1, x, derivative=True)
    u1, u2 = j / x, y / x
    d1 = kn * (jd / x - j / x ** 2)
    d2 = kn * (yd / x - y / x ** 2)
    return u1, u2, d1, d2


def flrw_mode(t, kn, s0=2.0):
    """T(t), T'(t) (derivative in t) with T = 0, T' = 1 at t = 0 (s = s0)."""
    u10, u20, d10, d20 = _u(kn, s0)
    M = np.array([[u10, u20], [d10, d20]])
    c1, c2 = np.linalg.solve(M, [0.0, 1.0])
    u1, u2, d1, d2 = _u(kn, np.asarray(t, float) + s0)
    return c1 * u1 + c2 * u2, c1 * d1 + c2 * d2


def flrw_mode_ode(t_eval, kn, s0=2.0, rtol=1e-12, atol=1e-15):
    """The same mode by direct integration of h'' + (4/s) h' + k^2 h = 0 (check)."""
    def f(t, y):
        s = t + s0
        return [y[1], -4.0 / s * y[1] - kn ** 2 * y[0]]
    sol = solve_ivp(f, (0.0, float(np.max(t_eval))), [0.0, 1.0], t_eval=t_eval,
                    method="DOP853", rtol=rtol, atol=atol)
    return sol.y[0], sol.y[1]


def flrw_amplitudes(t, kn, eps_p, eps_x, ph_p=0.0, ph_x=0.0):
    """(P, X, P', X') at +k of the standing tensor mode of test X."""
    T, Td = flrw_mode(t, kn)
    cp = eps_p * np.exp(1j * ph_p) / 2.0
    cx = eps_x * np.exp(1j * ph_x) / 2.0
    return cp * T, cx * T, cp * Td, cx * Td


# ---------------------------------------------------------------------------------------
# error measures shared by both tests

def wave_measures(P, X, Pd, Xd, kn):
    """Forward and backward combinations W = P + i P'/|k|, P - i P'/|k| (a mode exp(-i|k|t)
    is purely forward) for both polarizations, and the polarization ratio Wx/W+."""
    Wfp, Wbp = P + 1j * Pd / kn, P - 1j * Pd / kn
    Wfx, Wbx = X + 1j * Xd / kn, X - 1j * Xd / kn
    return {"Wf_p": Wfp, "Wb_p": Wbp, "Wf_x": Wfx, "Wb_x": Wbx, "R": Wfx / Wfp}


def compare(meas, exact):
    """Errors of a measurement against the exact solution (dicts of wave_measures):
    amplitude |W/W_ex| - 1 and phase arg(W/W_ex) per polarization, backward error
    |Wb - Wb_ex|/|Wf_ex|, polarization ratio error (modulus and argument)."""
    out = {}
    for p in ("p", "x"):
        r = meas["Wf_" + p] / exact["Wf_" + p]
        out["amp_" + p] = np.abs(r) - 1.0
        out["phase_" + p] = np.angle(r)
        out["back_" + p] = np.abs(meas["Wb_" + p] - exact["Wb_" + p]) / np.abs(exact["Wf_" + p])
    rr = meas["R"] / exact["R"]
    out["pol_amp"] = np.abs(rr) - 1.0
    out["pol_phase"] = np.angle(rr)
    return out
