"""Shared pieces of the figure scripts of package repro/figs (reproduction of arXiv:2512.14649).

Readers: dumps (NRSFDMP2) through `ladder/scripts/ladder_lib.py` (sequential reads, Track E's own
layout reader), the lockstep `.modes` files, the records `.sf.con.hst` / `.sf.hst`. Lattice shells and
binning with the hemisphere count of independent modes (P1:454 "more than 10 realisations"). Units of
P1 (Mpl = 100) for the axes that carry units. Track E's own Philox for alpha_n (noise/ref).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # tracks/E-stoch-inf
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "ladder", "scripts"))
sys.path.insert(0, os.path.join(TRACK, "noise", "ref"))
sys.path.insert(0, os.path.join(REPO, "python"))

import ladder_lib as ll  # noqa: E402
from philox_ref import mode_alpha  # noqa: E402

L_BOX = 2.0 * np.pi
SHARP, SIGMA = 5.0, 1.0
QUANT = np.array([0.0, 0.5, 2.5, 16.0, 50.0, 84.0, 97.5, 99.5, 100.0])   # percentiles kept
SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"

# H*/Mpl (reduced Planck mass) at N*: SR ladder_lib.H_STAR_PLANCK (case.json of run
# E-20261115-171633-f574079); USR usr/results/usr_reference.json T1.H_star
HSTAR = {"sr": 9.4869151038149e-06, "usr": 9.36231877388068e-06}
MPL_P1 = 100.0                      # P1:519 units

# deck parameters (repro/scope/inputs/{sr,usr}_paper.athinput)
DECK = {
    "sr": dict(potential="quadratic", mass=1.82877655899024605e-01,
               phi0=-2.66679478988261254e+00, pi0=2.97300406808996935e-02, tlim=8.5),
    "usr": dict(potential="inflection", lam=5.33317648526340374e+05, vev=3.94952857597418439e-02,
                phi0=-1.64328188347202975e-01, pi0=3.23658652791244811e-02,
                tlim=10.437508874065651),
}


def k_p1(n, case):
    """Comoving wave number in P1's units (Mpl = 100, a* = 1, sigma = 1): |n| H* 100/Mpl."""
    return np.asarray(n, float) * HSTAR[case] * MPL_P1


def rate_p1(case):
    """Factor that turns a code rate (unit H*) into P1's units: K_P1 = K_code * rate_p1."""
    return HSTAR[case] * MPL_P1


def potential_code(case, phi):
    """V and V' in code units (G = 1, time 1/H*), as coded in AthenaK (scalar_field.hpp)."""
    d = DECK[case]
    if d["potential"] == "quadratic":
        m2 = d["mass"] ** 2
        return 0.5 * m2 * phi * phi, m2 * phi
    lam, vev = d["lam"], d["vev"]
    s2 = np.sqrt(2.0)
    phi2 = phi * phi
    pp = 3.0 * phi2 + 2.0 * s2 * phi * vev + 6.0 * vev * vev
    qq = 3.0 * phi2 + 2.0 * vev * vev
    dpp = 6.0 * phi + 2.0 * s2 * vev
    dqq = 6.0 * phi
    c = lam * vev ** 4 / 3.0
    v = c * phi2 * pp / (qq * qq)
    dv = c * ((2.0 * phi * pp + phi2 * dpp) / (qq * qq) - 2.0 * phi2 * pp * dqq / qq ** 3)
    return v, dv


def v_to_p1(case, v_code):
    """V in P1's units: V_planck = V_code 8 pi H*^2 (Mpl = 1), times Mpl_P1^4."""
    return np.asarray(v_code) * 8.0 * np.pi * HSTAR[case] ** 2 * MPL_P1 ** 4


def rolls(case, phi, pi, hub):
    """eps1 = 4 pi Pi^2/H^2, eps2 = -dln eps1/dN = 6 + 2 V'/(H Pi) - 2 eps1 (code units, G = 1)."""
    _, dv = potential_code(case, phi)
    eps1 = 4.0 * np.pi * pi * pi / (hub * hub)
    return eps1, 6.0 + 2.0 * dv / (hub * pi) - 2.0 * eps1


def friedmann(case, t_eval):
    """Own Friedmann + Klein-Gordon integration from (phi0, pi0) of the deck (geodesic slicing,
    alpha = 1): returns phi, Pi, ln a, H at t_eval."""
    from scipy.integrate import solve_ivp
    d = DECK[case]

    def rhs(t, y):
        v, dv = potential_code(case, y[0])
        hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * y[1] * y[1] + v))
        return [y[1], -3.0 * hub * y[1] - dv, hub]

    sol = solve_ivp(rhs, (0.0, float(np.max(t_eval))), [d["phi0"], d["pi0"], 0.0],
                    method="DOP853", rtol=1e-13, atol=1e-16, t_eval=np.asarray(t_eval, float))
    if sol.status != 0:
        raise RuntimeError(sol.message)
    phi, pi, lna = sol.y
    v, _ = potential_code(case, phi)
    hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))
    return phi, pi, lna, hub


# ------------------------------------------------------------------------------ files
def dump_files(rundir, base):
    return ll.dump_list(rundir, base)


def read_modes_file(path):
    """Lockstep shells of a dump: dict(time, a, H, eps1, eps2, n2, R, dR)."""
    hdr = {}
    with open(path) as fp:
        for line in fp:
            if not line.startswith("#"):
                break
            w = line[1:].split()
            for i in range(len(w) - 1):
                try:
                    hdr.setdefault(w[i], float(w[i + 1]))
                except ValueError:
                    pass
    d = np.atleast_2d(np.loadtxt(path))
    return dict(time=hdr.get("time"), a=hdr["a"], H=hdr["H"], eps1=hdr.get("eps1"),
                eps2=hdr.get("eps2"), n2=d[:, 0].astype(np.int64), R=d[:, 1] + 1j * d[:, 2],
                dR=d[:, 3] + 1j * d[:, 4])


def window(k, a, hub):
    return 0.5 * (1.0 + np.tanh(SHARP * np.log(SIGMA * a * hub / np.asarray(k, float))))


def read_con(path):
    return np.atleast_2d(np.loadtxt(path))


# --------------------------------------------------------------------------- lattice bins
class Shells:
    """Shells |n|^2 = const of the rfft half lattice of an N^3 box, hemisphere only (each
    independent complex mode once), Nyquist planes left out (|n_i| < N/2)."""

    def __init__(self, N):
        self.N = N
        kz = np.fft.fftfreq(N, 1.0 / N).astype(np.int64)[:, None, None]
        ky = np.fft.fftfreq(N, 1.0 / N).astype(np.int64)[None, :, None]
        kx = np.arange(N // 2 + 1, dtype=np.int64)[None, None, :]
        n2 = kx * kx + ky * ky + kz * kz
        hemi = (kx > 0) | ((kx == 0) & (ky > 0)) | ((kx == 0) & (ky == 0) & (kz > 0))
        nyq = (kx == N // 2) | (ky == -N // 2) | (kz == -N // 2)
        mask = hemi & ~nyq & (n2 > 0)
        self.n2_half = n2
        self.flat = np.flatnonzero(mask.ravel())
        n2m = n2.ravel()[self.flat]
        order = np.argsort(n2m, kind="stable")
        self.flat = self.flat[order]
        s = n2m[order]
        self.n2, self.start, self.count = np.unique(s, return_index=True, return_counts=True)
        self.k = np.sqrt(self.n2.astype(float))

    def bin(self, p_half):
        """Mean, min, max over each shell of a real array on the half lattice."""
        v = p_half.ravel()[self.flat]
        return (np.add.reduceat(v, self.start) / self.count,
                np.minimum.reduceat(v, self.start), np.maximum.reduceat(v, self.start))

    def delta_factor(self):
        """4 pi |n|^3 on the half lattice (Delta = 4 pi |n|^3 |c|^2, code units, L = 2 pi)."""
        return 4.0 * np.pi * self.n2_half.astype(float) ** 1.5


def percentiles(x):
    return np.percentile(np.asarray(x).ravel(), QUANT)


def alpha_modes(modes, seed):
    return mode_alpha(seed, 0, 0, modes.n)
