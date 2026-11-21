"""Readers and extraction for the card runs of the USR case (package tracks/E-stoch-inf/usr,
JOURNAL entry 9). usr_lib.py stays as the earlier analyses used it; this module adds:

- `read_fields`: NRSFDMP2 dumps read sequentially (seek + numpy.fromfile per variable and
  MeshBlock, in file order; no memory map), so that a 2.95 GB dump at 256^3 is streamed once
  while it is still in the page cache;
- `Extractor`: the Fourier coefficients of R^NR on the injected modes, in the linear form of
  P1:522-526 with the factors of usr_lib.curvature (chi part c[chi]/(2<chi>)) and in a
  logarithmic variant (chi part c[ln chi]/2), and the full-lattice field R^NR(x) for the
  one-point statistics;
- `ShellReference`: the code-time Mukhanov-Sasaki reference integrated per shell (|n|^2)
  and expanded to the modes, L^-3/2 W(k, t) R_k(t) alpha_n;
- `synth_field`: the real-space field of given coefficients on the hemisphere (inverse of
  Extractor.coeff), used for the linear realisation field;
- `read_con`: the constraint record with the columns of con_signed (core_scalar-3).
"""
import os
import struct

import numpy as np
from scipy import fft as sfft

import usr_lib as ul

CURV = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]
CONS = ["H", "Mx", "My", "Mz"]
GPAIRS = (("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
          ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0))
# columns of <basename>.sf.con.hst (0-based; header of the file, con_signed = true)
C = dict(t=0, cycle=1, efolds=2, H_ratio=3, H_ratio_max=4, M_ratio=6, M_ratio_max=7,
         Hmag=9, Mmag=10, absH=11, absM=12, rmsH=13, rmsM=14, phi=16, Pi=17, K=18, alpha=19,
         H_mean=20, Mx_mean=21, My_mean=22, Mz_mean=23, Hp_ratio=24, Hp_ratio_max=25,
         Hp_rms=26)


def read_con(path):
    d = np.loadtxt(path)
    return np.atleast_2d(d)


def read_fields(path, names):
    """Sequential reader: returns (header, {name: array (n3, n2, n1)})."""
    h = ul.read_header(path)
    nx1, nx2, nx3 = h["nx"]
    cells = nx1 * nx2 * nx3
    blk = 32 + 48 + 8 * h["nvar"] * cells
    order = sorted(names, key=lambda n: h["names"].index(n))
    out = {}
    with open(path, "rb") as fp:
        blocks = []
        for b in range(h["nmb"]):
            fp.seek(h["data_offset"] + b * blk)
            lev, lx1, lx2, lx3 = struct.unpack("<4q", fp.read(32))
            if lev != 0:
                raise ValueError("refined meshes are not handled")
            blocks.append((lx1, lx2, lx3))
        n1 = (max(b[0] for b in blocks) + 1) * nx1
        n2 = (max(b[1] for b in blocks) + 1) * nx2
        n3 = (max(b[2] for b in blocks) + 1) * nx3
        for name in order:
            out[name] = np.empty((n3, n2, n1))
        for b, (lx1, lx2, lx3) in enumerate(blocks):
            for name in order:
                v = h["names"].index(name)
                fp.seek(h["data_offset"] + b * blk + 80 + 8 * v * cells)
                a = np.fromfile(fp, dtype="<f8", count=cells)
                if a.size != cells:
                    raise IOError(f"{path}: short read of {name}")
                out[name][lx3 * nx3:(lx3 + 1) * nx3, lx2 * nx2:(lx2 + 1) * nx2,
                          lx1 * nx1:(lx1 + 1) * nx1] = a.reshape(nx3, nx2, nx1)
    return h, out


def dump_list(rundir, base="usr"):
    return ul.dump_list(rundir, base)


class Extractor:
    """R^NR on the modes of a Modes object, and on the whole lattice."""

    def __init__(self, modes, workers=3):
        self.m = modes
        self.N = modes.N
        self.workers = workers

    def rfft(self, f):
        return sfft.rfftn(f, workers=self.workers)

    def at_modes(self, F):
        m = self.m
        return F[m.iz, m.iy, m.ix] * m.shift / self.N**3

    def coeff(self, f):
        return self.at_modes(self.rfft(f))

    def curvature(self, f, full=False):
        """Coefficients of R^NR (linear and log chi part) and the background numbers;
        with full = True also the rfft array of the linear R^NR on the whole lattice."""
        m = self.m
        chi_m = f["chi"].mean()
        hb = -f["K"].mean() / (3.0 * f["alpha"].mean())
        pib = f["Pi"].mean()
        Fchi = self.rfft(f["chi"])
        Fphi = self.rfft(f["phi"])
        lin_chi = self.at_modes(Fchi) / (2.0 * chi_m)
        log_chi = 0.5 * self.coeff(np.log(f["chi"]))
        phi_part = (hb / pib) * self.at_modes(Fphi)
        aniso = np.zeros(m.M, dtype=complex)
        if full:
            N = self.N
            kz = sfft.fftfreq(N, 1.0 / N)[:, None, None]
            ky = sfft.fftfreq(N, 1.0 / N)[None, :, None]
            kx = np.arange(N // 2 + 1, dtype=float)[None, None, :]
            k2 = kx * kx + ky * ky + kz * kz
            k2[0, 0, 0] = 1.0
            Ffull = Fchi / (2.0 * chi_m) + (hb / pib) * Fphi
            kvec = (kx, ky, kz)
        for name, i, j, w in GPAIRS:
            Fg = self.rfft(f[name])
            aniso += w * m.nhat[:, i] * m.nhat[:, j] * self.at_modes(Fg)
            if full:
                Ffull = Ffull + 0.25 * w * (kvec[i] * kvec[j] / k2) * Fg
            del Fg
        out = dict(lin=lin_chi + phi_part + 0.25 * aniso, log=log_chi + phi_part + 0.25 * aniso,
                   chi_part=lin_chi, phi_part=phi_part, aniso=0.25 * aniso,
                   bg=dict(chi=float(chi_m), H=float(hb), Pi=float(pib),
                           phi=float(f["phi"].mean()), K=float(f["K"].mean())))
        if full:
            Ffull[0, 0, 0] = 0.0
            out["F"] = Ffull
        return out

    def field(self, F, nmax2=None):
        """Real-space field of an rfft array; with nmax2 only the band 0 < |n|^2 <= nmax2."""
        if nmax2 is not None:
            N = self.N
            kz = sfft.fftfreq(N, 1.0 / N)[:, None, None]
            ky = sfft.fftfreq(N, 1.0 / N)[None, :, None]
            kx = np.arange(N // 2 + 1, dtype=float)[None, None, :]
            F = np.where(kx * kx + ky * ky + kz * kz <= nmax2, F, 0.0)
        return sfft.irfftn(F, s=(self.N,) * 3, workers=self.workers)


def synth_field(modes, c, workers=3):
    """Real field whose coefficients on the hemisphere modes are c (and zero elsewhere)."""
    N = modes.N
    F = np.zeros((N, N, N // 2 + 1), dtype=complex)
    v = c * N**3 / modes.shift
    F[modes.iz, modes.iy, modes.ix] = v
    zero = modes.ix == 0                     # partner -n lies in the stored plane kx = 0
    F[(-modes.n[zero, 2]) % N, (-modes.n[zero, 1]) % N, 0] = np.conj(v[zero])
    return sfft.irfftn(F, s=(N,) * 3, workers=workers)


class ShellReference:
    """Background and R_k per shell in code time (usr_lib.Reference with k^2 = |n|^2), at
    the times t_eval, for the shells of a mode file with |n|^2 <= nmax2."""

    def __init__(self, ci, modefile, nmax2, t_eval):
        n2f, r0s, dr0s = ul.read_modefile(modefile)
        sel = n2f <= nmax2
        self.n2 = n2f[sel]
        self.ref = ul.Reference(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"],
                                self.n2.astype(float), r0s[sel], dr0s[sel], t_eval)
        self.t = np.asarray(t_eval, float)

    def state(self, i):
        return self.ref.at(i)

    def modes_ref(self, modes, alpha, i):
        """L^-3/2 W R alpha on the modes at t_eval[i], with the background there."""
        st = self.ref.at(i)
        idx = np.searchsorted(self.n2, modes.n2)
        assert np.array_equal(self.n2[idx], modes.n2)
        w = ul.window(modes.k, st["a"], st["H"])
        return ul.L_BOX**-1.5 * w * st["R"][idx] * alpha, st


def moments(x):
    x = np.asarray(x, float).ravel()
    mu = x.mean()
    d = x - mu
    s2 = np.mean(d * d)
    return dict(mean=float(mu), rms=float(np.sqrt(s2)), skew=float(np.mean(d**3) / s2**1.5),
                exkurt=float(np.mean(d**4) / s2**2 - 3.0), max=float(x.max()), min=float(x.min()),
                maxabs=float(np.abs(x).max()))


def athena_cost(rundir):
    """Cycles, cpu time and the peak card memory from the run's athena.log."""
    out = {}
    p = os.path.join(rundir, "athena.log")
    if not os.path.exists(p):
        return out
    for line in open(p, errors="replace"):
        s = line.strip()
        if s.startswith("cpu time used"):
            out["cpu_time_s"] = float(s.split("=")[1])
        elif s.startswith("MeshBlock-cycles"):
            out["meshblock_cycles"] = int(s.split("=")[1])
        elif s.startswith("zone-cycles/cpu_second"):
            out["zone_cycles_per_s"] = float(s.split("=")[1])
        elif s.startswith("# exit="):
            for w in s[1:].split():
                if "=" in w:
                    k, v = w.split("=", 1)
                    out[k] = v
    return out
