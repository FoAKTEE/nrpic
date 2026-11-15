"""Reference solutions and readers for the Newtonian mode of the particle module
(athenak/src/particles/nrpic_newton.cpp, tracks/core/interfaces/newtonian_mode.md).

Exact solutions (units of the caller; G enters only through the product GM):

- field of a point mass and of a homogeneous ball,
- collapse from rest of a homogeneous pressureless ball (cycloid), with the second
  moment of the mass distribution and its first three time derivatives,
- growth of a plane wave in a matter-dominated background up to shell crossing
  (Zel'dovich solution, exact in plane symmetry), in the variables of the code:
  conformal time t, comoving position x, momentum p = a dx/dt, a = (1 + H t/2)^2.

Readers: the history file ``<base>.newton.hst``, the history ``<base>.nrpic.hst``, and
particle snapshots ``<base>.part.NNNNN.bin``.

The scheme of the code in numpy on a periodic uniform mesh (``scheme_fields``): the
Poisson equation with the seven-point Laplacian and the gradient of the Catmull-Rom
interpolant. It is an analysis tool, used to attribute the difference between the code
and the spectral reference ``cosmo/newton/pm.py``.
"""
import struct

import numpy as np

__all__ = ["point_field", "ball_field", "free_fall_time", "cycloid", "ball_moment",
           "scale_factor", "drift_integral", "zeldovich_wave", "read_newton_hst",
           "read_nrpic_hst", "read_snapshot", "moment_tensor", "quadrupole",
           "quadrupole_luminosity", "hermite_weights", "gather_gradient",
           "scheme_fields", "NEWTON_COLUMNS"]


# ---------------------------------------------------------------------------------------
# exact fields
# ---------------------------------------------------------------------------------------
def point_field(x, x0, gm=1.0):
    """Potential and acceleration of a point mass at x0, at the points x[N,3]."""
    d = np.atleast_2d(x) - np.asarray(x0, dtype=float)
    r = np.sqrt((d*d).sum(axis=1))
    return -gm/r, -gm*d/r[:, None]**3


def ball_field(x, x0, gm=1.0, radius=1.0):
    """Potential and acceleration of a homogeneous ball of the given radius centred on
    x0, at the points x[N,3]."""
    d = np.atleast_2d(x) - np.asarray(x0, dtype=float)
    r = np.sqrt((d*d).sum(axis=1))
    inside = r < radius
    rs = np.where(inside, radius, r)
    phi = np.where(inside, -0.5*gm*(3.0*radius**2 - r**2)/radius**3, -gm/rs)
    g = -gm*d/rs[:, None]**3
    return phi, g


# ---------------------------------------------------------------------------------------
# collapse of a homogeneous ball from rest
# ---------------------------------------------------------------------------------------
def free_fall_time(r0=1.0, gm=1.0):
    """Time at which a homogeneous ball of radius r0 at rest collapses to a point."""
    return 0.5*np.pi*np.sqrt(r0**3/(2.0*gm))


def cycloid(t, r0=1.0, gm=1.0):
    """s = r/r0 of every shell of a homogeneous ball released from rest, and its first
    three time derivatives, at the times t (0 <= t < free-fall time):
        s = (1 + cos th)/2,   t = sqrt(r0^3/(8 GM)) (th + sin th).
    Returns (s, ds/dt, d2s/dt2, d3s/dt3)."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    w = np.sqrt(8.0*gm/r0**3)
    y = w*t
    # Newton iteration for th + sin th = y, starting from the small-th and the
    # near-collapse limits; th in [0, pi)
    th = np.where(y < 2.0, 0.5*y, np.pi - np.cbrt(6.0*np.maximum(np.pi - y, 0.0)))
    for _ in range(60):
        f = th + np.sin(th) - y
        fp = 1.0 + np.cos(th)
        th = np.clip(th - f/np.maximum(fp, 1e-300), 0.0, np.pi)
    s = 0.5*(1.0 + np.cos(th))
    c = gm/r0**3
    with np.errstate(divide="ignore", invalid="ignore"):
        ds = -np.sqrt(np.maximum(2.0*c*(1.0/s - 1.0), 0.0))
        d2s = -c/s**2
        d3s = 2.0*c*ds/s**3
    return s, ds, d2s, d3s


def ball_moment(t, i0, r0=1.0, gm=1.0):
    """Second moment I(t) = i0 s^2 of a homologously collapsing ball and its first three
    time derivatives; i0 is any component of sum m x_i x_j at t = 0."""
    s, ds, d2s, d3s = cycloid(t, r0, gm)
    return (i0*s*s, 2.0*i0*s*ds, 2.0*i0*(ds*ds + s*d2s), 2.0*i0*(3.0*ds*d2s + s*d3s))


# ---------------------------------------------------------------------------------------
# prescribed background of the code: a = (1 + H t/n)^n in conformal time t
# ---------------------------------------------------------------------------------------
def scale_factor(t, hubble=1.0, n=2.0):
    return (1.0 + hubble*np.asarray(t, dtype=float)/n)**n


def drift_integral(t1, t2, hubble=1.0, n=2.0):
    """Integral of dt/a from t1 to t2."""
    s1, s2 = 1.0 + hubble*t1/n, 1.0 + hubble*t2/n
    if n == 1.0:
        return np.log(s2/s1)/hubble
    return (n/(hubble*(1.0 - n)))*(s2**(1.0 - n) - s1**(1.0 - n))


def zeldovich_wave(q, a, amp, k, hubble=1.0):
    """Plane wave along x in a matter-dominated background (a = 1 and Hubble rate
    `hubble` at t = 0): comoving position and momentum p = a dx/dt of the particle with
    Lagrangian coordinate q at the scale factor a,
        x = q + a (amp/k) cos(k q),     p = hubble a^(3/2) (amp/k) cos(k q).
    The density contrast is 1/(1 - a amp sin(k q)) - 1; shell crossing at a amp = 1."""
    psi = (amp/k)*np.cos(k*np.asarray(q, dtype=float))
    return q + a*psi, hubble*a**1.5*psi


# ---------------------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------------------
NEWTON_COLUMNS = (
    ["time", "ncycle", "a", "mass", "K", "W", "W_mesh", "C", "int_K_da",
     "P_x", "P_y", "P_z", "L_x", "L_y", "L_z", "X_x", "X_y", "X_z"]
    + ["%s_%s" % (p, c) for p in ("I", "dI", "d2I", "d3I")
       for c in ("xx", "xy", "xz", "yy", "yz", "zz")]
    + ["time_d3I", "Phi_min", "Phi_max", "p_max", "g_max", "mg_defect", "dt",
       "mg_cycles"])


def _dedup(data):
    """Keep the last record of each cycle (restarts append)."""
    last = {}
    for i, c in enumerate(data[:, 1].astype(np.int64)):
        last[int(c)] = i
    return data[[last[c] for c in sorted(last)]]


def read_newton_hst(path):
    """The history of the Newtonian mode as a dict of arrays keyed by NEWTON_COLUMNS."""
    data = _dedup(np.atleast_2d(np.loadtxt(path)))
    return {name: data[:, i] for i, name in enumerate(NEWTON_COLUMNS)}


def read_nrpic_hst(path):
    """The history of the particle module as a 2d array (docs/FORMATS.md); in the
    Newtonian mode column 13 (index 12) is the potential at the probe, column 14 the
    deposited rest-mass density there, and columns 33 + 3n, 34 + 3n those of probe n."""
    return _dedup(np.atleast_2d(np.loadtxt(path)))


def read_snapshot(path):
    """Return (time, cycle, x[N,3], u[N,3], m[N], tag[N]) of a particle snapshot."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRPSNAP1":
            raise ValueError(f"{path}: bad magic")
        t, = struct.unpack("<d", f.read(8))
        n, = struct.unpack("<q", f.read(8))
        cyc, = struct.unpack("<q", f.read(8))
        rec = np.frombuffer(f.read(56*n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4*n), dtype="<i4")
    return t, cyc, rec[:, 0:3].copy(), rec[:, 3:6].copy(), rec[:, 6].copy(), tag.copy()


def moment_tensor(h, order=0):
    """The second moment I_ij = sum m x_i x_j (order 0) or its first, second or third
    time derivative (order 1, 2, 3) from a history dict, as an array [n, 3, 3]. The third
    derivative belongs to the times h["time_d3I"], the others to h["time"]."""
    pre = ("I", "dI", "d2I", "d3I")[order]
    out = np.empty((len(h["time"]), 3, 3))
    for (i, j), c in zip(((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)),
                         ("xx", "xy", "xz", "yy", "yz", "zz")):
        out[:, i, j] = out[:, j, i] = h["%s_%s" % (pre, c)]
    return out


def quadrupole(h, order=0):
    """Trace-free quadrupole Q_ij = I_ij - delta_ij I_kk/3, or its time derivative of
    the given order, as an array [n, 3, 3]."""
    m = moment_tensor(h, order)
    tr = np.trace(m, axis1=1, axis2=2)/3.0
    return m - tr[:, None, None]*np.eye(3)


def quadrupole_luminosity(h, G=1.0, c=1.0):
    """Quadrupole formula L = (G/5 c^5) d3Q_ij d3Q_ij at the times h["time_d3I"]. The
    third derivative in the history is a difference quotient over one step and carries
    the fluctuation of the mesh force; average it over the time scale of interest before
    squaring when the particle number per cell is low."""
    q3 = quadrupole(h, 3)
    return (G/(5.0*c**5))*np.einsum("nij,nij->n", q3, q3)


# ---------------------------------------------------------------------------------------
# the scheme of the code on a periodic uniform mesh, in numpy
# ---------------------------------------------------------------------------------------
def hermite_weights(s):
    """Catmull-Rom weights and derivative weights of nrpic_kernels.hpp (HermiteWeights)
    for the nodes at offsets -1, 0, 1, 2; s[N] in [0, 1). Shapes (4, N)."""
    s2, s3 = s*s, s*s*s
    w = 0.5*np.array([-s + 2.0*s2 - s3, 2.0 - 5.0*s2 + 3.0*s3, s + 4.0*s2 - 3.0*s3,
                      -s2 + s3])
    dw = 0.5*np.array([-1.0 + 4.0*s - 3.0*s2, -10.0*s + 9.0*s2, 1.0 + 8.0*s - 9.0*s2,
                       -2.0*s + 3.0*s2])
    return w, dw


def gather_gradient(f, x, L):
    """Value and gradient of the Catmull-Rom interpolant of the periodic cell-centred
    field f[n,n,n] (cell centres at (i + 1/2) L/n) at the points x[N,3]."""
    n = f.shape[0]
    h = L/n
    xi = np.asarray(x)/h - 0.5
    i0 = np.floor(xi).astype(np.int64)
    s = xi - i0
    w, dw = [], []
    for d in range(3):
        a, b = hermite_weights(s[:, d])
        w.append(a)
        dw.append(b/h)
    val = np.zeros(len(xi))
    grad = np.zeros((len(xi), 3))
    for a in range(4):
        ix = (i0[:, 0] + a - 1) % n
        for b in range(4):
            iy = (i0[:, 1] + b - 1) % n
            for c in range(4):
                iz = (i0[:, 2] + c - 1) % n
                v = f[ix, iy, iz]
                val += w[0][a]*w[1][b]*w[2][c]*v
                grad[:, 0] += dw[0][a]*w[1][b]*w[2][c]*v
                grad[:, 1] += w[0][a]*dw[1][b]*w[2][c]*v
                grad[:, 2] += w[0][a]*w[1][b]*dw[2][c]*v
    return val, grad


def scheme_fields(rho, L, four_pi_g=4.0*np.pi):
    """Potential of the seven-point Laplacian on the periodic mesh, lap Phi = four_pi_g
    (rho - <rho>), with zero mean."""
    n = rho.shape[0]
    h = L/n
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=h)
    kr = 2.0*np.pi*np.fft.rfftfreq(n, d=h)
    lam1 = (2.0*np.cos(k1*h) - 2.0)/h**2
    lamr = (2.0*np.cos(kr*h) - 2.0)/h**2
    lam = lam1[:, None, None] + lam1[None, :, None] + lamr[None, None, :]
    lam[0, 0, 0] = 1.0
    Fk = four_pi_g*np.fft.rfftn(rho - rho.mean())/lam
    Fk[0, 0, 0] = 0.0
    return np.fft.irfftn(Fk, s=(n, n, n))
