"""Analysis of the slow-roll ladder of Track E (package tracks/E-stoch-inf/ladder).

Written by this package, independently of core's readers and references:
- `read_dump`: the double-precision dump layout NRSFDMP2 of `scalar_field_diag.cpp`
  (layout as documented in tracks/core/interfaces/scalar_field_2.md section 4 on branch
  core/scalar-2), read variable by variable through a memory map;
- `Modes`: the hemisphere of wave vectors 0 < |n|^2 <= nmax2 of NOISE_SPEC (n_x > 0, or
  n_x = 0 and n_y > 0, or n_x = n_y = 0 and n_z > 0), coefficients
  c_n[f] = N^-3 sum_x f(x) exp(-i n.x) on the cell centres x = (j + 1/2) h of [0, 2 pi)^3;
- `curvature`: R^NR_n = c_n[chi]/(2 <chi>) + (1/4) nhat_i nhat_j c_n[gt_ij]
  + (H_b/Pi_b) c_n[phi], H_b = -<K>/(3 <alpha>), Pi_b = <Pi> (arXiv:2512.14649
  PRD_v2.tex:522-526 with the factors of arXiv:2610.32592 appendix.tex:513-522; SPEC 9 E6);
- `LinearReference`: Friedmann background and Mukhanov-Sasaki mode functions in the
  units of the code (G = 1, time unit 1/H*, a* = 1), started at t = 0 from (phi0, pi0)
  and from the rows of the mode file; window W = (1 + tanh[s ln(sigma a H/k)])/2;
- amplitudes alpha_n from Track E's own Philox re-implementation
  (tracks/E-stoch-inf/noise/ref/philox_ref.py, written from rng.md, not from core's twin).
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "noise", "ref")))
from philox_ref import mode_alpha  # noqa: E402

L_BOX = 2.0 * np.pi
SEED = 20261115
MASS = 1.82877655899024605e-01          # code units (inputs/sr_base.athinput)
PHI0 = -2.66679478988261254e+00
PI0 = 2.97300406808996935e-02
H_STAR_PLANCK = 9.4869151038149e-06     # H*/Mpl (case.json of run E-20261115-171633-f574079)
SHARPNESS = 5.0
SIGMA = 1.0


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
    """Fields `names` of a dump as arrays [z, y, x] (x fastest in memory) on the whole
    root mesh; returns (header, dict)."""
    h = read_header(path)
    nx1, nx2, nx3 = h["nx"]
    cells = nx1 * nx2 * nx3
    blk_bytes = 32 + 48 + 8 * h["nvar"] * cells
    with open(path, "rb") as fp:
        fp.seek(h["data_offset"])
        blocks = []
        for b in range(h["nmb"]):
            fp.seek(h["data_offset"] + b * blk_bytes)
            lev, lx1, lx2, lx3 = struct.unpack("<4q", fp.read(32))
            if lev != 0:
                raise ValueError("refined meshes are not handled")
            blocks.append((lx1, lx2, lx3))
    n1 = (max(b[0] for b in blocks) + 1) * nx1
    n2 = (max(b[1] for b in blocks) + 1) * nx2
    n3 = (max(b[2] for b in blocks) + 1) * nx3
    mm = np.memmap(path, dtype="<f8", mode="r", offset=h["data_offset"],
                   shape=(h["nmb"] * blk_bytes // 8,))
    out = {}
    for name in names:
        v = h["names"].index(name)
        arr = np.empty((n3, n2, n1))
        for b, (lx1, lx2, lx3) in enumerate(blocks):
            start = (b * blk_bytes + 80) // 8 + v * cells
            sub = np.asarray(mm[start:start + cells]).reshape(nx3, nx2, nx1)
            arr[lx3 * nx3:(lx3 + 1) * nx3, lx2 * nx2:(lx2 + 1) * nx2,
                lx1 * nx1:(lx1 + 1) * nx1] = sub
        out[name] = arr
    del mm
    return h, out


def dump_list(rundir, base="sr"):
    files = sorted(f for f in os.listdir(rundir) if f.startswith(base + ".sf.")
                   and f.endswith(".dump"))
    return [os.path.join(rundir, f) for f in files]


def read_con(rundir, base="sr"):
    """The constraint record <basename>.sf.con.hst as an array (columns of
    scalar_field_2.md section 3, zero-based: 0 time, 1 cycle, 2 efolds, 3 <|H|/[H]>,
    4 max, 5 <|H|>/<[H]>, 6 <|M|/[M]>, 7 max, 8 <|M|>/<[M]>, 9 <[H]>, 10 <[M]>,
    11 <|H|>, 12 <|M|>, 13 rms H, 14 rms |M|, 15 rms |M_bssn - M_adm|, 16 <phi>,
    17 <Pi>, 18 <K>, 19 <alpha>)."""
    return np.loadtxt(os.path.join(rundir, base + ".sf.con.hst"))


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
        self.k = np.sqrt(self.n2.astype(float))              # code units, L = 2 pi
        self.nhat = self.n / self.k[:, None]
        self.M = self.n.shape[0]
        # index into rfftn of an array [z, y, x]: last axis x has n_x >= 0 only
        self.iz = self.n[:, 2] % self.N
        self.iy = self.n[:, 1] % self.N
        self.ix = self.n[:, 0]
        self.shift = np.exp(-1j * np.pi * self.n.sum(axis=1) / self.N)   # cell centres
        self.shell_n2, self.shell_of = np.unique(self.n2, return_inverse=True)

    def coeff(self, f):
        from scipy import fft
        F = fft.rfftn(f, workers=8)
        return F[self.iz, self.iy, self.ix] * self.shift / self.N**3

    def alpha(self, seed=SEED, dof=0, epoch=0):
        return mode_alpha(seed, dof, epoch, self.n)


CURV_VARS = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]


def curvature(modes, fields):
    """R^NR_n of one dump (fields from read_dump with CURV_VARS)."""
    chi_m = fields["chi"].mean()
    hb = -fields["K"].mean() / (3.0 * fields["alpha"].mean())
    pib = fields["Pi"].mean()
    r = modes.coeff(fields["chi"]) / (2.0 * chi_m) + (hb / pib) * modes.coeff(fields["phi"])
    nh = modes.nhat
    pairs = [("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
             ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0)]
    aniso = np.zeros(modes.M, dtype=complex)
    for name, i, j, w in pairs:
        aniso += w * nh[:, i] * nh[:, j] * modes.coeff(fields[name])
    return r + 0.25 * aniso, aniso * 0.25, dict(chi=chi_m, H=hb, Pi=pib)


# ------------------------------------------------------------------- linear reference
def potential(phi):
    return 0.5 * MASS**2 * phi**2, MASS**2 * phi


class LinearReference:
    """Background (phi, Pi, ln a) and the Mukhanov-Sasaki modes
    d2R/dt2 + (3 - eps2) H dR/dt + (k/a)^2 R = 0, eps1 = 4 pi Pi^2/H^2,
    eps2 = -dln eps1/dN = 6 + 2 V'/(H Pi) - 2 eps1, in code time from t = 0."""

    def __init__(self, k_shell, r0, dr0, t_end, k2_shell=None, rtol=1e-12, t_eval=None):
        """t_eval: the times at which the modes are wanted (then no dense output of the
        modes is kept, which would hold several GB for the 3414 shells of nmax2 = 4096);
        without it the modes have a dense output."""
        from scipy.integrate import solve_ivp
        self.k = np.asarray(k_shell, float)
        self.k2 = self.k**2 if k2_shell is None else np.asarray(k2_shell, float)
        m = self.k.size
        self.m = m
        self.bg = solve_ivp(lambda t, y: self._rhs_bg(y), (0.0, t_end), [PHI0, PI0, 0.0],
                            method="DOP853", rtol=1e-13, atol=1e-15, dense_output=True)
        y0 = np.concatenate([[PHI0, PI0, 0.0], r0.real, r0.imag, dr0.real, dr0.imag])
        scale = np.concatenate([[1.0, 1.0, 1.0], np.full(4 * m, 1e-5)])
        if t_eval is None:
            self.sol = solve_ivp(self._rhs, (0.0, t_end), y0, method="DOP853", rtol=rtol,
                                 atol=1e-14 * scale, dense_output=True)
            self.t_eval = None
        else:
            self.t_eval = np.asarray(sorted(set(float(x) for x in t_eval)))
            self.sol = solve_ivp(self._rhs, (0.0, t_end), y0, method="DOP853", rtol=rtol,
                                 atol=1e-14 * scale, t_eval=self.t_eval)
        if self.sol.status != 0 or self.bg.status != 0:
            raise RuntimeError(self.sol.message)

    def _rhs_bg(self, y):
        phi, pi = y[0], y[1]
        v, dv = potential(phi)
        hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))
        return [pi, -3.0 * hub * pi - dv, hub]

    @staticmethod
    def hubble(phi, pi):
        v, _ = potential(phi)
        return np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))

    def _rhs(self, t, y):
        m = self.m
        phi, pi, lna = y[0], y[1], y[2]
        v, dv = potential(phi)
        hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))
        eps1 = 4.0 * np.pi * pi * pi / (hub * hub)
        eps2 = 6.0 + 2.0 * dv / (hub * pi) - 2.0 * eps1
        a2 = np.exp(2.0 * lna)
        rr, ri = y[3:3 + m], y[3 + m:3 + 2 * m]
        dr, di = y[3 + 2 * m:3 + 3 * m], y[3 + 3 * m:3 + 4 * m]
        fr = (3.0 - eps2) * hub
        w2 = self.k2 / a2
        out = np.empty_like(y)
        out[0] = pi
        out[1] = -3.0 * hub * pi - dv
        out[2] = hub
        out[3:3 + m] = dr
        out[3 + m:3 + 2 * m] = di
        out[3 + 2 * m:3 + 3 * m] = -fr * dr - w2 * rr
        out[3 + 3 * m:3 + 4 * m] = -fr * di - w2 * ri
        return out

    def background(self, t):
        y = self.bg.sol(t)
        phi, pi, lna = y[0], y[1], y[2]
        v, dv = potential(phi)
        hub = self.hubble(phi, pi)
        eps1 = 4.0 * np.pi * pi * pi / (hub * hub)
        eps2 = 6.0 + 2.0 * dv / (hub * pi) - 2.0 * eps1
        return dict(phi=phi, Pi=pi, lna=lna, a=np.exp(lna), H=hub, K=-3.0 * hub,
                    eps1=eps1, eps2=eps2)

    def modes(self, t):
        if self.t_eval is None:
            y = self.sol.sol(t)
        else:
            i = int(np.argmin(np.abs(self.t_eval - t)))
            if abs(self.t_eval[i] - t) > 1e-12:
                raise ValueError(f"time {t} not among t_eval")
            y = self.sol.y[:, i]
        m = self.m
        return y[3:3 + m] + 1j * y[3 + m:3 + 2 * m], \
            y[3 + 2 * m:3 + 3 * m] + 1j * y[3 + 3 * m:3 + 4 * m]

    def window(self, t, k):
        b = self.background(t)
        x = SHARPNESS * np.log(SIGMA * b["a"] * b["H"] / k)
        return 0.5 * (1.0 + np.tanh(x))

    def crossing(self, k, t_end):
        """Time, e-fold, H and eps1 where k = a H on the reference background (k >= 1);
        t = 0 where a H >= k already at the start."""
        from scipy.optimize import brentq
        k = np.atleast_1d(np.asarray(k, float))
        tk = np.zeros(k.size)
        for i, kk in enumerate(k):
            f = lambda t: np.log(self.background(t)["a"] * self.background(t)["H"] / kk)
            tk[i] = 0.0 if f(0.0) >= 0.0 else brentq(f, 0.0, t_end, xtol=1e-12)
        b = self.background(tk)
        return tk, b["lna"], b["H"], b["eps1"]

    def crossing_efold(self, k, t_end):
        return self.crossing(k, t_end)[1]

    def efold_time(self, n_target, t_end):
        from scipy.optimize import brentq
        return brentq(lambda t: self.background(t)["lna"] - n_target, 0.0, t_end)


def k2_stencil(n, nmesh):
    """k^2 of the sixth-order centred second difference of AthenaK (NGHOST = 4,
    athenak/src/utils/finite_diff.hpp:218-241) for wave vectors n (M, 3) on an N^3 mesh
    of the box 2 pi: sum over axes of -(c0 + 2 sum_m c_m cos(m theta))/h^2."""
    th = 2.0 * np.pi * np.asarray(n, float) / nmesh
    sym = -49.0 / 18.0 + 3.0 * np.cos(th) - 0.3 * np.cos(2 * th) + (2.0 / 90.0) * np.cos(3 * th)
    h = L_BOX / nmesh
    return (-sym / h**2).sum(axis=1)


def reference_modes_stencil(modes, modefile, t_end, t_eval, sel):
    """Reference for the modes `sel` (indices) with the k^2 of the stencil, one ODE per
    wave vector (initial values of its shell; window with |n|)."""
    n2f, r0, dr0 = read_modefile(modefile)
    idx = np.searchsorted(n2f, modes.n2[sel])
    if not np.array_equal(n2f[idx], modes.n2[sel]):
        raise ValueError("mode file does not cover the shells")
    k2 = k2_stencil(modes.n[sel], modes.N)
    return LinearReference(modes.k[sel], r0[idx], dr0[idx], t_end, k2_shell=k2,
                           t_eval=t_eval)


def read_modefile(path):
    d = np.atleast_2d(np.loadtxt(path))
    return d[:, 0].astype(np.int64), d[:, 1] + 1j * d[:, 2], d[:, 3] + 1j * d[:, 4]


def reference_for(modes, modefile, t_end, t_eval=None):
    """LinearReference on the shells of `modes` from the mode file."""
    n2f, r0, dr0 = read_modefile(modefile)
    idx = np.searchsorted(n2f, modes.shell_n2)
    if not np.array_equal(n2f[idx], modes.shell_n2):
        raise ValueError("mode file does not cover the shells")
    ks = np.sqrt(modes.shell_n2.astype(float))
    return LinearReference(ks, r0[idx], dr0[idx], t_end, t_eval=t_eval)
