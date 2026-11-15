"""Exact and semi-analytic reference solutions of the periodic_z4c tests, and the writer
of the initial-data file read by the nrpic_cosmo problem generator.

1. Linear TT wave (pgen z4c_linear_wave): polarization tensor exactly as in
   athenak/src/pgen/tests/z4c_linear_wave.cpp, solution
     gt_ij = delta_ij + A e_ij sin(phi),  At_ij = pi |k| A e_ij cos(phi),
     phi = 2 pi (k.x - |k| t),  chi = alpha = 1, Khat = Theta = Gamma = beta = 0,
   exact for the linearized Einstein equations in any gauge of the code (the lapse and
   shift are not excited at first order: K = 0 and Gamma^i = -d_j gt^ij = 0).

2. Gauge wave of the Apples-with-Apples suite in the coordinates of the code.
   Flat spacetime, ds^2 = -(1-H) dt^2 + (1-H) dx^2 + dy^2 + dz^2,
   H = A sin(2 pi (x - t)), the form of athenak/src/pgen/z4c/z4c_gauge_wave.cpp (which
   the release executables do not contain: it defines UserProblem). Harmonic slicing,
   zero shift. The nrpic_cosmo pgen accepts only conformally flat slices, so the
   initial slice is written in the proper-length coordinate
     X(x) = int_0^x sqrt(1 - H(s, 0)) ds,  box length L = X(1),
   in which gamma_XX = 1 at t = 0. With zero shift the coordinate lines are the normal
   observers in both systems, so X labels the same worldline at all times and
     gamma_XX(t, X) = (1 - H(x - t)) / (1 - H(x)),   alpha = sqrt(1 - H(x - t)),
     K_XX(t, X) = -H'(x - t) / (2 sqrt(1 - H(x - t)) (1 - H(x))),  x = x(X),
   with gamma_yy = gamma_zz = 1 and every other component zero.

3. Pure-gauge data for the record of the lapse and shift options: flat slice
   (psi = 1), K_xx = kappa sin(k x), alpha = 1, beta = 0. These satisfy both
   constraints exactly (R = 0, K^2 - K_ij K^ij = 0, d_j(K^ij - gamma^ij K) = 0), and
   the spacetime is flat. Linearized about alpha = chi = 1, with
   a = delta alpha = a_s sin kx, K = K_s sin kx, h = delta gamma_xx = h_s sin kx,
   b = beta^x = b_c cos kx, the code's gauge conditions (athenak/src/z4c/z4c_calcrhs.cpp
   lines 682-728 at commit b7b431d) give
     d a_s/dt = -F K_s,          F = lapse_oplog*lapse_harmonicf + lapse_harmonic
                                     + lapse_volume + lapse_kdriver
     d K_s/dt = k^2 a_s
     d h_s/dt = -2 K_s - 2 k b_c
     d b_c/dt = (2/3)(shift_Gamma + shift_alpha2Gamma) k h_s - shift_eta b_c
                - shift_H k (h_s/6 + a_s)
   (Gamma^x = (2/3) dh/dx, chi = 1 - h/3 at first order; the advection terms and the
   constraint-damping terms are of second order or vanish with the constraints.)
"""
import numpy as np
from scipy.integrate import quad
from scipy.linalg import expm

# ---------------------------------------------------------------- 1. linear TT wave


def tt_polarization(kx1, kx2, kx3):
    """e_ij of z4c_linear_wave.cpp, as dict xx, xy, ... and the norm |k|."""
    knorm = np.sqrt(kx1**2 + kx2**2 + kx3**2)
    th = np.arctan2(np.sqrt(kx2**2 + kx1**2), kx3)
    ph = np.arctan2(kx1, kx2)
    e = {"xx": -np.cos(th)**2*np.cos(2*ph) - np.cos(ph)**2*np.sin(th)**2,
         "xy": -0.25*(3 + np.cos(2*th))*np.sin(2*ph),
         "xz": -np.cos(th)*np.sin(th)*np.sin(ph),
         "yy": np.cos(th)**2*np.cos(2*ph) - np.sin(th)**2*np.sin(ph)**2,
         "yz": np.cos(th)*np.sin(th)*np.cos(ph),
         "zz": np.sin(th)**2}
    return e, knorm


def tt_check(kx1, kx2, kx3):
    """Return (trace, |e.k|, e_ij e_ij) of the polarization tensor."""
    e, _ = tt_polarization(kx1, kx2, kx3)
    E = np.array([[e["xx"], e["xy"], e["xz"]], [e["xy"], e["yy"], e["yz"]],
                  [e["xz"], e["yz"], e["zz"]]])
    k = np.array([kx1, kx2, kx3], float)
    return np.trace(E), np.linalg.norm(E @ k), np.sum(E*E)


def tt_exact(x, y, z, t, kx1, kx2, kx3, amp):
    """Exact linear solution in Z4c variables on broadcastable coordinates."""
    e, kn = tt_polarization(kx1, kx2, kx3)
    phi = 2*np.pi*(kx1*x + kx2*y + kx3*z - kn*t)
    s, c = np.sin(phi), np.cos(phi)
    out = {}
    for comp, v in e.items():
        d = 1.0 if comp[0] == comp[1] else 0.0
        out["g" + comp] = d + amp*v*s
        out["A" + comp] = np.pi*kn*amp*v*c
    return out


# ---------------------------------------------------------------- 2. gauge wave

def gw_H(x, t, A):
    return A*np.sin(2*np.pi*(x - t))


def gw_dH(x, t, A):
    """dH/dx"""
    return 2*np.pi*A*np.cos(2*np.pi*(x - t))


def gw_box_length(A):
    return quad(lambda s: np.sqrt(1 - gw_H(s, 0.0, A)), 0.0, 1.0,
                epsabs=1e-15, epsrel=1e-15, limit=200)[0]


def gw_X_of_x(x, A):
    """X(x) = int_0^x sqrt(1 - A sin 2 pi s) ds, vectorized (periodic extension)."""
    x = np.asarray(x, float)
    L = gw_box_length(A)
    n = np.floor(x)
    f = x - n
    out = np.array([quad(lambda s: np.sqrt(1 - gw_H(s, 0.0, A)), 0.0, fi,
                         epsabs=1e-15, epsrel=1e-15, limit=200)[0]
                    for fi in np.atleast_1d(f)])
    return (n + out.reshape(np.shape(x))) if np.ndim(x) else n + out[0]


def gw_x_of_X(X, A, tol=1e-15):
    """Invert X(x) by Newton iteration (dX/dx = sqrt(1 - H) > 0)."""
    X = np.atleast_1d(np.asarray(X, float))
    L = gw_box_length(A)
    x = X/L
    for _ in range(50):
        F = gw_X_of_x(x, A) - X
        dx = F/np.sqrt(1 - gw_H(x, 0.0, A))
        x = x - dx
        if np.max(np.abs(dx)) < tol:
            break
    return x


def gw_exact_X(X, t, A, x_of_X=None):
    """Exact gauge wave in the X coordinates at time t. Returns gamma_XX, alpha, K_XX
    (and the Z4c variables chi, gxx, gyy, Khat, Axx, Ayy)."""
    x = gw_x_of_X(X, A) if x_of_X is None else x_of_X
    H0 = gw_H(x, 0.0, A)
    Ht = gw_H(x, t, A)
    gXX = (1 - Ht)/(1 - H0)
    alpha = np.sqrt(1 - Ht)
    KXX = -gw_dH(x, t, A)/(2*np.sqrt(1 - Ht)*(1 - H0))
    K = KXX/gXX
    chi = gXX**(-1.0/3.0)
    return {"gamma_XX": gXX, "alpha": alpha, "K_XX": KXX, "K": K, "chi": chi,
            "gxx": chi*gXX, "gyy": chi, "gzz": chi, "Khat": K,
            "Axx": chi*(KXX - gXX*K/3), "Ayy": chi*(-K/3), "Azz": chi*(-K/3)}


def gw_initial_fields(N, A):
    """Cell-centre fields on N cells of [0, L): psi, K, alpha, Ahat (6)."""
    L = gw_box_length(A)
    X = (np.arange(N) + 0.5)*L/N
    ex = gw_exact_X(X, 0.0, A)
    K = ex["K"]
    zero = np.zeros(N)
    # psi = 1: Ahat_ij = K_ij - delta_ij K / 3, K_ij = diag(K_XX, 0, 0)
    ahat = [ex["K_XX"] - K/3, zero, zero, -K/3, zero, -K/3]
    return L, X, np.ones(N), K, ex["alpha"], ahat


# ---------------------------------------------------------------- 3. pure-gauge data

def gauge_F(opts):
    return (opts.get("lapse_oplog", 2.0)*opts.get("lapse_harmonicf", 1.0)
            + opts.get("lapse_harmonic", 0.0) + opts.get("lapse_volume", 0.0)
            + opts.get("lapse_kdriver", 0.0))


def gauge_matrix(opts, k=2*np.pi):
    """Linear system d/dt (a_s, K_s, h_s, b_c) = M (a_s, K_s, h_s, b_c)."""
    F = gauge_F(opts)
    muS = opts.get("shift_Gamma", 1.0) + opts.get("shift_alpha2Gamma", 0.0)
    eta = opts.get("shift_eta", 2.0)
    muH = opts.get("shift_H", 0.0)
    return np.array([[0.0, -F, 0.0, 0.0],
                     [k*k, 0.0, 0.0, 0.0],
                     [0.0, -2.0, 0.0, -2.0*k],
                     [-muH*k, 0.0, (2.0/3.0)*muS*k - muH*k/6.0, -eta]])


def gauge_linear(opts, t, kappa, k=2*np.pi):
    """Mode amplitudes (a_s, K_s, h_s, b_c) at the times t for K_s(0) = kappa."""
    M = gauge_matrix(opts, k)
    y0 = np.array([0.0, kappa, 0.0, 0.0])
    return np.array([expm(M*ti) @ y0 for ti in np.atleast_1d(t)])


def gauge_eigen(opts, k=2*np.pi):
    return np.linalg.eigvals(gauge_matrix(opts, k))


# ---------------------------------------------------------------- id file writer

def write_nrcosmo(path, psi, K, alpha, ahat, n):
    """Write the NRCOSMO1 file of athenak/src/pgen/nrpic/nrpic_cosmo.cpp:
    8 bytes magic, 3 int64 (n1, n2, n3), 9 float64 arrays of n3*n2*n1 values, first
    index fastest: psi, K, alpha, Ahat_xx, xy, xz, yy, yz, zz. The 1D profiles given
    here (length n1) are copied along x2 and x3."""
    n1, n2, n3 = n
    with open(path, "wb") as f:
        f.write(b"NRCOSMO1")
        np.array([n1, n2, n3], dtype=np.int64).tofile(f)
        for arr in [psi, K, alpha] + list(ahat):
            a = np.asarray(arr, float)
            full = np.broadcast_to(a[None, None, :], (n3, n2, n1))
            np.ascontiguousarray(full).astype(np.float64).tofile(f)
