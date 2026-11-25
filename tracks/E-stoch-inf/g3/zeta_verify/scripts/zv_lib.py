"""Independent zeta reader of g3/zeta_verify (helper of E-stoch-inf, 2026-11-25).

Written without reading zeta/zeta_reader.py.  Everything here is my own: the parser of the
NRSFDMP1/2 dumps (format: athenak/src/scalar_field/scalar_field_io.cpp lines 10-17 and
scalar_field_diag.cpp WriteDumpExtended), the homogeneous Friedmann-Klein-Gordon (FKG)
integrator in e-folds, its first and second variational equations, the end-surface map and
its second-order expansion.

Units: G = c = 1 (G_munu = 8 pi T_munu), the code units of the deck.  State (phi, y), y =
dphi/dN.  With L(phi) = V'/V the FKG system is
    H^2 = (8 pi/3) V / (1 - 4 pi y^2/3),
    phi' = y,
    y'   = -(3 - 4 pi y^2) y - V'/H^2 = -3 y + 4 pi y^3 - (3/(8 pi)) L (1 - 4 pi y^2/3),
so only L = dln V/dphi enters (the overall scale of V drops out of N).

Arithmetic in numpy.longdouble (x86 80-bit, eps 1.1e-19) unless dtype=float64 is asked for.
The integrator is the classical fourth-order Runge-Kutta scheme with a fixed step in N; the
end surface phi = phi_e is located by a last Runge-Kutta step of variable length solved by
Newton's method, so the map is a smooth function of the initial state (no step-size control).
"""
import struct

import numpy as np

LD = np.longdouble
PI_LD = LD("3.14159265358979323846264338327950288")
SQRT2_CODE = 1.4142135623730951       # the constant of scalar_field.hpp (double), kept exact


# ----------------------------------------------------------------------------- dumps
def read_dump(path):
    """Fields of a scalar-field dump as arrays [k, j, i] (x fastest), plus a header dict."""
    with open(path, "rb") as fh:
        buf = fh.read()
    magic = buf[:8].decode()
    if magic not in ("NRSFDMP1", "NRSFDMP2"):
        raise ValueError(f"{path}: unknown magic {magic!r}")
    nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack_from("<7q", buf, 8)
    (time,) = struct.unpack_from("<d", buf, 64)
    off = 72
    if magic == "NRSFDMP2":
        names = []
        for _ in range(nvar):
            names.append(buf[off:off + 16].split(b"\0", 1)[0].decode())
            off += 16
    else:
        names = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx", "My", "Mz", "E"]
        names += [f"noise{n}" for n in range(nnoise)]
    ncell = nx1 * nx2 * nx3
    blocks = []
    for _ in range(nmb):
        level, lx1, lx2, lx3 = struct.unpack_from("<4q", buf, off)
        off += 32
        ext = struct.unpack_from("<6d", buf, off)
        off += 48
        arr = np.frombuffer(buf, dtype="<f8", count=nvar * ncell, offset=off)
        off += 8 * nvar * ncell
        blocks.append(((level, lx1, lx2, lx3), ext, arr.reshape(nvar, nx3, nx2, nx1)))
    if off != len(buf):
        raise ValueError(f"{path}: {len(buf) - off} bytes left over")
    if any(b[0][0] != 0 for b in blocks):
        raise ValueError("refined meshes are not handled")
    mx1 = 1 + max(b[0][1] for b in blocks)
    mx2 = 1 + max(b[0][2] for b in blocks)
    mx3 = 1 + max(b[0][3] for b in blocks)
    full = np.empty((nvar, mx3 * nx3, mx2 * nx2, mx1 * nx1))
    for (lev, l1, l2, l3), _ext, a in blocks:
        full[:, l3 * nx3:(l3 + 1) * nx3, l2 * nx2:(l2 + 1) * nx2, l1 * nx1:(l1 + 1) * nx1] = a
    fields = {nm: full[v] for v, nm in enumerate(names)}
    head = dict(magic=magic, nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar, cycle=cycle,
                nnoise=nnoise, time=time, names=names,
                box=(blocks[0][1][0], blocks[-1][1][1]))
    return fields, head


def read_modes_header(path):
    """Lockstep background of a .modes file (the '#' lines at its top)."""
    out = {}
    with open(path) as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            tok = line[1:].split()
            for i in range(len(tok) - 1):
                try:
                    out.setdefault(tok[i], float(tok[i + 1]))
                except ValueError:
                    pass
    return out


def read_hist_last(path):
    """Last record of <basename>.sf.hst as a dict by column name."""
    names, last = None, None
    with open(path) as fh:
        for line in fh:
            if line.startswith("# [1]"):
                names = [t.split("=", 1)[1] for t in line[1:].split()]
            elif not line.startswith("#") and line.strip():
                last = line
    vals = [float(t) for t in last.split()]
    return dict(zip(names, vals))


# ------------------------------------------------------------------------ potentials
class Inflection:
    """V = lambda v^4 phi^2 P/(3 Q^2), P = 3 phi^2 + 2 s2 v phi + 6 v^2, Q = 3 phi^2 + 2 v^2
    (scalar_field.hpp lines 56-60, 84-94; s2 the double constant of the code)."""

    def __init__(self, lam, vev):
        self.lam = lam
        self.v = vev

    def V(self, phi):
        v = self.v
        p = 3 * phi * phi + 2 * SQRT2_CODE * phi * v + 6 * v * v
        q = 3 * phi * phi + 2 * v * v
        return self.lam * v ** 4 / 3 * phi * phi * p / (q * q)

    def dV(self, phi):
        v = self.v
        p = 3 * phi * phi + 2 * SQRT2_CODE * phi * v + 6 * v * v
        q = 3 * phi * phi + 2 * v * v
        dp = 6 * phi + 2 * SQRT2_CODE * v
        dq = 6 * phi
        c = self.lam * v ** 4 / 3
        return c * ((2 * phi * p + phi * phi * dp) / (q * q) - 2 * phi * phi * p * dq / q ** 3)

    def L(self, phi):
        """L, L', L'' with L = dln V/dphi = 2/phi + P'/P - 2 Q'/Q."""
        v = self.v
        p = 3 * phi * phi + 2 * SQRT2_CODE * phi * v + 6 * v * v
        q = 3 * phi * phi + 2 * v * v
        p1, p2 = 6 * phi + 2 * SQRT2_CODE * v, 6
        q1, q2 = 6 * phi, 6
        a, b = p1 / p, q1 / q
        L0 = 2 / phi + a - 2 * b
        L1 = -2 / phi ** 2 + p2 / p - a * a - 2 * (q2 / q - b * b)
        L2 = 4 / phi ** 3 + (-3 * p1 * p2 / p ** 2 + 2 * a ** 3) \
            - 2 * (-3 * q1 * q2 / q ** 2 + 2 * b ** 3)
        return L0, L1, L2


class Exponential:
    """V = V0 exp(-lam phi): L = -lam (closed-form test P1)."""

    def __init__(self, lam, V0=1.0):
        self.lam = lam
        self.V0 = V0

    def V(self, phi):
        return self.V0 * np.exp(-self.lam * phi)

    def dV(self, phi):
        return -self.lam * self.V(phi)

    def L(self, phi):
        z = phi * 0
        return z - self.lam, z, z


class HamiltonJacobi:
    """H(phi) = H0 exp(beta phi^2/2): V = H^2 (3 - beta^2 phi^2/(4 pi))/(8 pi); the attractor
    y = -H'/(4 pi H) = -beta phi/(4 pi) is an exact FKG solution (closed-form test P2)."""

    def __init__(self, beta, H0=1.0):
        self.beta = beta
        self.H0 = H0

    def V(self, phi):
        b = self.beta
        return self.H0 ** 2 * np.exp(b * phi * phi) * (3 - b * b * phi * phi / (4 * PI_LD)) / (8 * PI_LD)

    def dV(self, phi):
        return self.V(phi) * self.L(phi)[0]

    def L(self, phi):
        b = self.beta
        c = b * b / (4 * PI_LD)
        g = 3 - c * phi * phi           # ln V = b phi^2 + ln g + const
        g1 = -2 * c * phi
        g2 = -2 * c
        L0 = 2 * b * phi + g1 / g
        L1 = 2 * b + g2 / g - (g1 / g) ** 2
        L2 = -3 * g1 * g2 / g ** 2 + 2 * (g1 / g) ** 3
        return L0, L1, L2


def hubble2(pot, phi, y):
    return 8 * PI_LD / 3 * pot.V(phi) / (1 - 4 * PI_LD * y * y / 3)


def hubble2_from_pi(pot, phi, Pi):
    """Friedmann in proper time: H^2 = (8 pi/3) (Pi^2/2 + V)."""
    return 8 * PI_LD / 3 * (Pi * Pi / 2 + pot.V(phi))


# ---------------------------------------------------------------------- FKG and RK4
def rhs(pot, phi, y):
    """Right-hand side; float64 arithmetic throughout when phi is float64 (precision tests)."""
    P = PI_LD if np.asarray(phi).dtype == LD else np.float64(np.pi)
    L0 = pot.L(phi)[0]
    fy = -3 * y + 4 * P * y ** 3 - 3 / (8 * P) * L0 * (1 - 4 * P * y * y / 3)
    return y, fy


def rk4_step(pot, phi, y, h):
    k1p, k1y = rhs(pot, phi, y)
    k2p, k2y = rhs(pot, phi + h / 2 * k1p, y + h / 2 * k1y)
    k3p, k3y = rhs(pot, phi + h / 2 * k2p, y + h / 2 * k2y)
    k4p, k4y = rhs(pot, phi + h * k3p, y + h * k3y)
    return (phi + h / 6 * (k1p + 2 * k2p + 2 * k3p + k4p),
            y + h / 6 * (k1y + 2 * k2y + 2 * k3y + k4y))


def integrate_to_N(pot, phi0, y0, dN, h, dtype=LD):
    """(phi, y) after dN e-folds from (phi0, y0), fixed step close to h."""
    n = max(1, int(np.ceil(float(dN) / h)))
    hh = dtype(dN) / n
    phi, y = dtype(phi0), dtype(y0)
    for _ in range(n):
        phi, y = rk4_step(pot, phi, y, hh)
    return phi, y


def efolds_to_surface(pot, phi0, y0, phi_e, h, nmax=10 ** 7, dtype=LD, newton_iter=8):
    """e-folds from (phi0, y0) (arrays allowed) to the first crossing of phi = phi_e, with a
    fixed step h and a last step of variable length found by Newton's method."""
    phi = np.asarray(phi0, dtype=dtype).copy()
    y = np.asarray(y0, dtype=dtype).copy()
    phi_e = dtype(phi_e)
    h = dtype(h)
    sgn = np.sign(phi_e - phi)
    N = np.zeros_like(phi)
    active = sgn * (phi_e - phi) > 0
    for _ in range(nmax):
        if not active.any():
            break
        pn, yn = rk4_step(pot, phi, y, h)
        cross = active & (sgn * (phi_e - pn) <= 0)
        go = active & ~cross
        phi = np.where(go, pn, phi)
        y = np.where(go, yn, y)
        N = np.where(go, N + h, N)
        if cross.any():
            idx = np.nonzero(cross)[0] if phi.ndim else None
            p0 = phi[idx] if phi.ndim else phi
            q0 = y[idx] if phi.ndim else y
            d = (phi_e - p0) / q0                       # first guess of the last step
            for _ in range(newton_iter):
                pd, yd = rk4_step(pot, p0, q0, d)
                d = d - (pd - phi_e) / yd
            if phi.ndim:
                N[idx] = N[idx] + d
                active[idx] = False
            else:
                N = N + d
                active = np.zeros_like(active)
    else:
        raise RuntimeError("end surface not reached")
    return N


# -------------------------------------------------------------- variational equations
def rhs_var(pot, Z):
    """Z = (phi, y, J (2x2, J[a, b] = dZ_a/dZ0_b), S (2x2x2)) -> dZ/dN."""
    phi, y, J, S = Z
    L0, L1, L2 = pot.L(phi)
    c = 3 / (8 * PI_LD)
    fy = -3 * y + 4 * PI_LD * y ** 3 - c * L0 * (1 - 4 * PI_LD * y * y / 3)
    A = np.array([[LD(0), LD(1)],
                  [-c * L1 * (1 - 4 * PI_LD * y * y / 3),
                   -3 + 12 * PI_LD * y * y + c * L0 * 8 * PI_LD * y / 3]], dtype=LD)
    B = np.zeros((2, 2, 2), dtype=LD)
    B[1, 0, 0] = -c * L2 * (1 - 4 * PI_LD * y * y / 3)
    B[1, 0, 1] = B[1, 1, 0] = c * L1 * 8 * PI_LD * y / 3
    B[1, 1, 1] = 24 * PI_LD * y + c * L0 * 8 * PI_LD / 3
    dJ = A @ J
    dS = np.einsum("ad,dbc->abc", A, S) + np.einsum("ade,db,ec->abc", B, J, J)
    return (y, fy, dJ, dS)


def _axpy(Z, h, K):
    return tuple(z + h * k for z, k in zip(Z, K))


def rk4_var(pot, Z, h):
    k1 = rhs_var(pot, Z)
    k2 = rhs_var(pot, _axpy(Z, h / 2, k1))
    k3 = rhs_var(pot, _axpy(Z, h / 2, k2))
    k4 = rhs_var(pot, _axpy(Z, h, k3))
    return tuple(z + h / 6 * (a + 2 * b + 2 * c + d) for z, a, b, c, d in zip(Z, k1, k2, k3, k4))


def map_derivatives(pot, phi0, y0, phi_e, h):
    """N and its first and second derivatives with respect to (phi0, y0) at the end surface
    phi = phi_e, from the variational equations of the same RK4 scheme."""
    Z = (LD(phi0), LD(y0), np.eye(2, dtype=LD), np.zeros((2, 2, 2), dtype=LD))
    phi_e = LD(phi_e)
    h = LD(h)
    sgn = np.sign(phi_e - Z[0])
    N = LD(0)
    while True:
        Zn = rk4_var(pot, Z, h)
        if sgn * (phi_e - Zn[0]) <= 0:
            break
        Z, N = Zn, N + h
    d = (phi_e - Z[0]) / Z[1]
    for _ in range(10):
        Zd = rk4_var(pot, Z, d)
        d = d - (Zd[0] - phi_e) / Zd[1]
    Z = rk4_var(pot, Z, d)
    N = N + d
    phi, y, J, S = Z
    fy = rhs(pot, phi, y)[1]
    Na = -J[0, :] / y
    Nab = -(S[0] + np.outer(J[1], Na) + np.outer(Na, J[1]) + fy * np.outer(Na, Na)) / y
    return N, Na, Nab, dict(phi=phi, y=y, fy=fy)


def to_phi_pi(Na, Nab, Hc):
    """Derivatives with respect to (phi, Pi) at fixed K, y0 = Pi/Hc (Hc = -K/3)."""
    T = np.array([[LD(1), LD(0)], [LD(0), 1 / LD(Hc)]], dtype=LD)
    return T.T @ Na, T.T @ Nab @ T


# ----------------------------------------------------------------- lattice quantities
def curvature_RNR(f):
    """R^NR per cell: the linear extraction of ladder_lib.curvature (lines 175-187) mapped back
    to the cells by the inverse FFT: dchi/(2 <chi>) + (H/<Pi>) dphi + (1/4) nh_i nh_j g_ij."""
    chi_m = f["chi"].mean()
    hb = -f["K"].mean() / (3.0 * f["alpha"].mean())
    pib = f["Pi"].mean()
    n3, n2, n1 = f["phi"].shape
    k3 = np.fft.fftfreq(n3) * n3
    k2 = np.fft.fftfreq(n2) * n2
    k1 = np.fft.fftfreq(n1) * n1
    K3, K2, K1 = np.meshgrid(k3, k2, k1, indexing="ij")
    kk = np.sqrt(K1 ** 2 + K2 ** 2 + K3 ** 2)
    kk[0, 0, 0] = 1.0
    nh = [K1 / kk, K2 / kk, K3 / kk]
    r = np.fft.fftn(f["chi"]) / (2 * chi_m) + (hb / pib) * np.fft.fftn(f["phi"])
    aniso = np.zeros_like(r)
    if "gxx" in f:
        for name, i, j, w in [("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
                              ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0)]:
            aniso += w * nh[i] * nh[j] * np.fft.fftn(f[name])
    tot = r + 0.25 * aniso
    tot[0, 0, 0] = 0.0
    aniso[0, 0, 0] = 0.0
    return np.fft.ifftn(tot).real, np.fft.ifftn(0.25 * aniso).real


def regress(yv, xv):
    """Least-squares slope of y on x, both with their means removed."""
    x = xv - xv.mean()
    y = yv - yv.mean()
    return float((x * y).sum() / (x * x).sum())
