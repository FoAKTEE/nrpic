"""Analysis of AthenaK output for the USR case (package tracks/E-stoch-inf/usr).

- `read_dump`: layout NRSFDMP2 (tracks/core/interfaces/scalar_field_2.md section 4 on
  core/scalar-2), same reading as ../../ladder/scripts/ladder_lib.py (written again here so
  that this package does not depend on another package's working files);
- `Modes`: wave vectors of the hemisphere with 0 < |n|^2 <= nmax2 (NOISE_SPEC), Fourier
  coefficients c_n[f] = N^-3 sum_x f(x) exp(-i n.x) on the cell centres of [0, 2 pi)^3;
- `curvature`: R^NR_n = c_n[chi]/(2 <chi>) + (1/4) nhat_i nhat_j c_n[gt_ij]
  + (H_b/Pi_b) c_n[phi], H_b = -<K>/(3 <alpha>), Pi_b = <Pi> (P1 PRD_v2.tex:522-526, factors
  of arXiv:2610.32592 appendix.tex:513-522, SPEC 9 E6);
- `Reference`: background (phi, Pi, ln a) and Mukhanov-Sasaki modes
  d2R/dt2 + (3 - eps2) H dR/dt + (k^2/a^2) R = 0 in code time from the state at N* and the
  rows of the mode file, for the inflection potential in code units; k^2 continuum or the
  symbol of AthenaK's sixth-order second difference;
- `twin_steps`: the RK4()4[2S] twin of a homogeneous run with a given step sequence;
- amplitudes alpha_n from Track E's own Philox re-implementation (../../noise/ref).
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "noise", "ref")))
from philox_ref import mode_alpha  # noqa: E402
from usr_reference import code_potential, z4c_rhs, code_rhs, RK4_2S  # noqa: E402

L_BOX = 2.0 * np.pi
SEED = 20261115
SHARP, SIGMA = 5.0, 1.0


# ------------------------------------------------------------------------------ dumps
def read_header(path):
    with open(path, "rb") as fp:
        magic = fp.read(8)
        if magic != b"NRSFDMP2":
            raise ValueError(f"{path}: layout {magic!r}, expected NRSFDMP2")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", fp.read(56))
        (time,) = struct.unpack("<d", fp.read(8))
        names = [fp.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        off = fp.tell()
    return dict(nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar, cycle=cycle, time=time,
                names=names, data_offset=off)


def read_dump(path, names):
    h = read_header(path)
    nx1, nx2, nx3 = h["nx"]
    cells = nx1 * nx2 * nx3
    blk = 32 + 48 + 8 * h["nvar"] * cells
    blocks = []
    with open(path, "rb") as fp:
        for b in range(h["nmb"]):
            fp.seek(h["data_offset"] + b * blk)
            lev, lx1, lx2, lx3 = struct.unpack("<4q", fp.read(32))
            if lev != 0:
                raise ValueError("refined meshes are not handled")
            blocks.append((lx1, lx2, lx3))
    n1 = (max(b[0] for b in blocks) + 1) * nx1
    n2 = (max(b[1] for b in blocks) + 1) * nx2
    n3 = (max(b[2] for b in blocks) + 1) * nx3
    mm = np.memmap(path, dtype="<f8", mode="r", offset=h["data_offset"],
                   shape=(h["nmb"] * blk // 8,))
    out = {}
    for name in names:
        v = h["names"].index(name)
        arr = np.empty((n3, n2, n1))
        for b, (lx1, lx2, lx3) in enumerate(blocks):
            start = (b * blk + 80) // 8 + v * cells
            arr[lx3 * nx3:(lx3 + 1) * nx3, lx2 * nx2:(lx2 + 1) * nx2,
                lx1 * nx1:(lx1 + 1) * nx1] = np.asarray(mm[start:start + cells]).reshape(
                    nx3, nx2, nx1)
        out[name] = arr
    del mm
    return h, out


def dump_list(rundir, base="usr"):
    fs = sorted(f for f in os.listdir(rundir) if f.startswith(base + ".sf.")
                and f.endswith(".dump"))
    return [os.path.join(rundir, f) for f in fs]


def read_modes_record(path):
    """The lockstep record <basename>.sf.NNNNN.modes: (header dict, n2, R, dR)."""
    hdr = {}
    with open(path) as fp:
        for line in fp:
            if not line.startswith("#"):
                break
            w = line[1:].split()
            for i in range(len(w) - 1):
                try:
                    hdr[w[i]] = float(w[i + 1])
                except ValueError:
                    pass
    d = np.atleast_2d(np.loadtxt(path))
    return hdr, d[:, 0].astype(np.int64), d[:, 1] + 1j * d[:, 2], d[:, 3] + 1j * d[:, 4]


# ------------------------------------------------------------------------------ modes
class Modes:
    def __init__(self, nmesh, nmax2):
        self.N, self.nmax2 = int(nmesh), int(nmax2)
        nmax = int(np.floor(np.sqrt(self.nmax2) + 1e-12))
        if 2 * nmax >= self.N:
            raise ValueError("cut reaches the Nyquist plane")
        r = np.arange(-nmax, nmax + 1)
        nz, ny, nx = np.meshgrid(r, r, r, indexing="ij")
        n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1).astype(np.int64)
        n2 = (n * n).sum(axis=1)
        hemi = (n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) | \
            ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))
        keep = hemi & (n2 >= 1) & (n2 <= self.nmax2)
        self.n = n[keep]
        self.n2 = n2[keep]
        self.k = np.sqrt(self.n2.astype(float))
        self.nhat = self.n / self.k[:, None]
        self.M = self.n.shape[0]
        self.iz = self.n[:, 2] % self.N
        self.iy = self.n[:, 1] % self.N
        self.ix = self.n[:, 0]
        self.shift = np.exp(-1j * np.pi * self.n.sum(axis=1) / self.N)   # cell centres
        self.shell_n2, self.shell_of = np.unique(self.n2, return_inverse=True)

    def coeff(self, f):
        from scipy import fft
        F = fft.rfftn(f, workers=4)
        return F[self.iz, self.iy, self.ix] * self.shift / self.N**3

    def alpha(self, seed=SEED, dof=0, epoch=0):
        return mode_alpha(seed, dof, epoch, self.n)

    def k2_stencil(self):
        th = 2.0 * np.pi * self.n.astype(float) / self.N
        sym = -49.0 / 18.0 + 3.0 * np.cos(th) - 0.3 * np.cos(2 * th) + (2.0 / 90.0) * np.cos(3 * th)
        h = L_BOX / self.N
        return (-sym / h**2).sum(axis=1)


CURV_VARS = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]


def curvature(modes, fields):
    chi_m = fields["chi"].mean()
    hb = -fields["K"].mean() / (3.0 * fields["alpha"].mean())
    pib = fields["Pi"].mean()
    r = modes.coeff(fields["chi"]) / (2.0 * chi_m) + (hb / pib) * modes.coeff(fields["phi"])
    nh = modes.nhat
    aniso = np.zeros(modes.M, dtype=complex)
    for name, i, j, w in (("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
                          ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0)):
        aniso += w * nh[:, i] * nh[:, j] * modes.coeff(fields[name])
    return r + 0.25 * aniso, dict(chi=chi_m, H=hb, Pi=pib, phi=fields["phi"].mean())


# ------------------------------------------------------------------- linear reference
class Reference:
    def __init__(self, lam, vev, phi0, pi0, k2, r0, dr0, t_eval, rtol=1e-12):
        from scipy.integrate import solve_ivp
        self.lam, self.vev = lam, vev
        self.k2 = np.asarray(k2, float)
        m = self.k2.size
        self.m = m
        self.t_eval = np.asarray(t_eval, float)
        y0 = np.concatenate([[phi0, pi0, 0.0], r0.real, r0.imag, dr0.real, dr0.imag])
        sc = np.concatenate([[1.0, 1e-3, 1.0], np.full(2 * m, np.abs(r0).max()),
                             np.full(2 * m, np.abs(dr0).max())])
        self.sol = solve_ivp(self._rhs, (0.0, self.t_eval[-1]), y0, method="DOP853",
                             rtol=rtol, atol=1e-13 * sc, t_eval=self.t_eval)
        if self.sol.status != 0:
            raise RuntimeError(self.sol.message)

    def _bg(self, phi, pi):
        v, dv = code_potential(phi, self.lam, self.vev)
        hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))
        eps1 = 4.0 * np.pi * pi * pi / (hub * hub)
        eps2 = 6.0 + 2.0 * dv / (hub * pi) - 2.0 * eps1
        return v, dv, hub, eps1, eps2

    def _rhs(self, t, y):
        m = self.m
        phi, pi, lna = y[0], y[1], y[2]
        v, dv, hub, eps1, eps2 = self._bg(phi, pi)
        out = np.empty_like(y)
        out[0] = pi
        out[1] = -3.0 * hub * pi - dv
        out[2] = hub
        fr = (3.0 - eps2) * hub
        w2 = self.k2 * np.exp(-2.0 * lna)
        out[3:3 + 2 * m] = y[3 + 2 * m:]
        out[3 + 2 * m:3 + 3 * m] = -fr * y[3 + 2 * m:3 + 3 * m] - w2 * y[3:3 + m]
        out[3 + 3 * m:] = -fr * y[3 + 3 * m:] - w2 * y[3 + m:3 + 2 * m]
        return out

    def at(self, i):
        y = self.sol.y[:, i]
        m = self.m
        v, dv, hub, eps1, eps2 = self._bg(y[0], y[1])
        return dict(phi=y[0], Pi=y[1], lna=y[2], a=np.exp(y[2]), H=hub, K=-3.0 * hub,
                    eps1=eps1, eps2=eps2,
                    R=y[3:3 + m] + 1j * y[3 + m:3 + 2 * m],
                    dR=y[3 + 2 * m:3 + 3 * m] + 1j * y[3 + 3 * m:])


def window(k, a, hub):
    return 0.5 * (1.0 + np.tanh(SHARP * np.log(SIGMA * a * hub / k)))


def read_modefile(path):
    d = np.atleast_2d(np.loadtxt(path))
    return d[:, 0].astype(np.int64), d[:, 1] + 1j * d[:, 2], d[:, 3] + 1j * d[:, 4]


# ------------------------------------------------------------------- homogeneous twin
def twin_steps(lam, vev, phi0, pi0, k0, dts):
    """RK4()4[2S] on the homogeneous Z4c system with the given step sequence; rows:
    initial state and the state after every step, columns phi, Pi, Khat, Theta, chi."""
    f = z4c_rhs(lam, vev)
    c = RK4_2S
    u0 = np.array([phi0, pi0, k0, 0.0, 1.0])
    out = np.empty((len(dts) + 1, 5))
    out[0] = u0
    for n, dt in enumerate(dts):
        u1 = u0.copy()
        for s in range(4):
            if s > 0:
                u1 = u1 + c["delta"][s] * u0
            u0 = c["gam0"][s] * u0 + c["gam1"][s] * u1 + c["beta"][s] * dt * f(0.0, u0)
        out[n + 1] = u0
    return out


def exact_background(lam, vev, phi0, pi0, k0, t):
    """The ADM form in code time integrated to rounding: (phi, Pi, K, ln chi) at times t."""
    from scipy.integrate import solve_ivp
    f = code_rhs(lam, vev)
    s = solve_ivp(f, (0.0, float(np.max(t))), [phi0, pi0, k0, 0.0], method="DOP853",
                  rtol=1e-13, atol=[1e-17, 1e-19, 1e-15, 1e-15], dense_output=True)
    return s.sol(t)
