"""Own helpers of the verifier (verify_g1): Maxwell-Juttner functions, sampling, readers.

Written independently of the track's modules (collide/REFERENCES, analysis, heat,
box_tests, ...). File formats: docs/FORMATS.md and the interface text of core/collisions-2
(section 5); `nrpic.collide.read_snapshot` / `read_dump` are used as readers only.

Units: G = c = k_B = 1, particle mass m = 1, theta = T/m, zeta = 1/theta.
"""
import json
import os
import struct

import numpy as np
from scipy import special, integrate

# ------------------------------------------------------------------------------------
# Maxwell-Juttner gas (own formulas, checked against quadrature in check_mj())


def k2e(z):
    """exp(z) K2(z) (scaled, no overflow)."""
    return special.kve(2, z)


def mean_w(theta):
    """<W> = K1/K2 + 3 theta = K3/K2 - theta per particle (units of m)."""
    z = 1.0/theta
    return special.kve(3, z)/special.kve(2, z) - theta


def enthalpy(theta):
    """h = K3/K2 per particle (units of m): <W> + theta."""
    z = 1.0/theta
    return special.kve(3, z)/special.kve(2, z)


def c_v(theta, h=1e-5):
    """d<W>/dtheta, central difference with relative step h (smooth function)."""
    d = h*theta
    return (mean_w(theta + d) - mean_w(theta - d))/(2*d)


def vmol_mean(theta):
    """<v_Mol> = 4 K3(2 zeta)/(zeta K2(zeta)^2), from the Gondolo-Gelmini reduction
    (own algebra; see JOURNAL V2). Scaled Bessel functions: K3(2z)/K2(z)^2 =
    kve(3,2z) e^{-2z} / (kve(2,z)^2 e^{-2z})."""
    z = 1.0/theta
    return 4*special.kve(3, 2*z)/(z*special.kve(2, z)**2)


def vmol_mean_quad(theta):
    """<v_Mol> by direct quadrature of the Gondolo-Gelmini one-dimensional integral
    <v_Mol> = [4 z^4 K2(z)^2]^-1 int_{2z}^inf (x^4 - 4 z^2 x^2) K1(x) dx (scaled)."""
    z = 1.0/theta

    def f(x):
        return (x**4 - 4*z*z*x*x)*special.kve(1, x)*np.exp(-(x - 2*z))
    val, _ = integrate.quad(f, 2*z, 2*z + 200.0, limit=400, epsabs=0, epsrel=1e-12)
    return val/(4*z**4*special.kve(2, z)**2)


class MJSampler:
    """Inverse-CDF sampler of |u| for MJ(theta): density ~ u^2 exp(-(W-1)/theta)."""

    def __init__(self, theta, npts=400001, ymax=80.0):
        self.theta = theta
        wmax = 1.0 + ymax*theta
        umax = np.sqrt(wmax**2 - 1)
        # grid uniform in sqrt(kinetic energy) resolves both ends
        s = np.linspace(0.0, np.sqrt(umax), npts)
        u = s*s
        w = np.sqrt(1 + u*u)
        pdf = u*u*np.exp(-(w - 1)/theta)*2*s         # du = 2 s ds
        cdf = integrate.cumulative_trapezoid(pdf, s, initial=0.0)
        self.u = u
        self.cdf = cdf/cdf[-1]

    def umag(self, uni):
        return np.interp(uni, self.cdf, self.u)

    def sample(self, n, rng):
        um = self.umag(rng.random(n))
        return um[:, None]*isotropic(n, rng)


def isotropic(n, rng):
    mu = 2*rng.random(n) - 1
    ph = 2*np.pi*rng.random(n)
    s = np.sqrt(1 - mu*mu)
    return np.stack([s*np.cos(ph), s*np.sin(ph), mu], axis=1)


def scatter_rel(ua, ub, nhat):
    """Own isotropic elastic scattering of two unit-mass particles (spatial four-velocities
    ua, ub; nhat the direction in the CM frame reached by the pure boost). Returns
    ua', ub', W_a, W_b, v_Mol."""
    wa = np.sqrt(1 + np.einsum("ij,ij->i", ua, ua))
    wb = np.sqrt(1 + np.einsum("ij,ij->i", ub, ub))
    P = ua + ub
    E = wa + wb
    P2 = np.einsum("ij,ij->i", P, P)
    # gamma_rel - 1 = (W_a W_b - ua.ub) - 1 ; s = 2 + 2 gamma_rel
    grel = wa*wb - np.einsum("ij,ij->i", ua, ub)
    s = 2 + 2*grel
    rs = np.sqrt(s)
    pst = np.sqrt(np.maximum(s/4 - 1, 0.0))
    pn = pst[:, None]*nhat
    est = rs/2
    fac = np.einsum("ij,ij->i", pn, P)/(rs*(E + rs)) + est/rs
    uan = pn + P*fac[:, None]
    ubn = P - uan
    vmol = np.sqrt(np.maximum(grel*grel - 1, 0.0))/(wa*wb)
    return uan, ubn, wa, wb, vmol, P2


# ------------------------------------------------------------------------------------
# readers


def read_hist(path):
    """Own reader of <base>.coll.hst (26 to 36 numeric columns; interface section 5).
    Keeps the last record of each cycle. Returns an (n, ncol) array."""
    rows = {}
    ncol = None
    with open(path) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            try:
                vals = [float(s) for s in v]
            except ValueError:
                continue
            if ncol is None:
                ncol = len(vals)
            if len(vals) != ncol:
                continue
            rows[int(vals[1])] = vals
    return np.array([rows[k] for k in sorted(rows)])


COLL = {name: i for i, name in enumerate(
    ["time", "cycle", "n_part", "n_cells", "n_tested", "sum_P", "n_coll", "n_updated",
     "n_trunc", "max_P", "max_nsub", "mean_nsub", "min_N", "mean_N", "max_dx_mfp",
     "sum_MW", "sum_Mu1", "sum_Mu2", "sum_Mu3", "dE", "dP1", "dP2", "dP3", "abs_dE",
     "abs_dP", "n_bad_cells", "sum_W", "sum_MW_species0", "sum_M_species0",
     "sum_MW_particles", "dE_particles", "sum_MH_particles", "dH_particles", "n_noroot",
     "max_dlam", "n_balance"])}


def read_snap(path):
    """Own reader of NRPSNAP1 snapshots (docs/FORMATS.md): time, cycle, x, u, m, tag."""
    with open(path, "rb") as fp:
        if fp.read(8) != b"NRPSNAP1":
            raise ValueError("not a snapshot: " + path)
        t, = struct.unpack("<d", fp.read(8))
        n, cyc = struct.unpack("<2q", fp.read(16))
        r = np.fromfile(fp, dtype="<f8", count=7*n).reshape(n, 7)
        tag = np.fromfile(fp, dtype="<i4", count=n)
    return dict(time=t, cycle=cyc, n=n, x=r[:, :3], u=r[:, 3:6], m=r[:, 6], tag=tag)


def read_nrp(path):
    """Own reader of the particle file NRPIC001 (docs/FORMATS.md)."""
    with open(path, "rb") as fp:
        if fp.read(8) != b"NRPIC001":
            raise ValueError("not a particle file: " + path)
        n, = struct.unpack("<q", fp.read(8))
        r = np.fromfile(fp, dtype="<f8", count=7*n).reshape(n, 7)
    return dict(n=n, x=r[:, :3], u=r[:, 3:6], m=r[:, 6])


def save_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fp:
        json.dump(obj, fp, indent=1, default=float)


def run_dir(default):
    return os.environ.get("NRPIC_RUN_DIR", default)
