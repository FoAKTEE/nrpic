"""Shared pieces of the window package (tracks/E-stoch-inf/window).

Reuses, read-only, the USR package's reader and reference (`../../usr/scripts/usr_lib.py`:
NRSFDMP2 reader, modes of the hemisphere, R^NR extraction, code-time Mukhanov-Sasaki
reference) and adds what the window scan needs:

- the window W = (1 + tanh[s ln(sigma a H/k)])/2 with s and sigma as arguments
  (coord/INTERFACES/scalar_field.md 7.3; the code: scalar_field_noise.cpp:546-555 at a58e95b);
- the five windows of the scan and the two cases (USR 128^3, slow roll 64^3);
- a reference for the quadratic potential of the slow-roll case (same equations as
  usr_lib.Reference, V = m^2 phi^2/2, `../../ladder/scripts/ladder_lib.py` potential);
- Fourier coefficients with at most two threads (the package's core limit).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TRACK, "usr", "scripts"))
import usr_lib as ul  # noqa: E402

L_BOX = ul.L_BOX
SEED = ul.SEED
NTHREADS = 2

# name: (s, sigma); the baseline first (P1 PRD_v2.tex:506, 519; usr_256.athinput:74-75)
WINDOWS = {
    "b": (5.0, 1.0),
    "s25": (2.5, 1.0),
    "s10": (10.0, 1.0),
    "g05": (5.0, 0.5),
    "g2": (5.0, 2.0),
}
LABEL = {"b": "s = 5, sigma = 1 (baseline)", "s25": "s = 2.5", "s10": "s = 10",
         "g05": "sigma = 0.5", "g2": "sigma = 2"}

# USR landmarks (cN = N - N*), ../../usr/results/landmarks.csv (run E-20261119-143905-f2bcde3)
USR_ON, USR_OFF = 2.523421176929555, 6.550319681613715

CASES = {
    "usr": dict(nmesh=128, nmax2=1024, potential="inflection",
                lam=5.33317648526340374e+05, vev=3.94952857597418439e-02,
                phi0=-1.64328188347202975e-01, pi0=3.23658652791244811e-02,
                tlim=10.437508874065651, base="usr",
                modefile=os.path.join(TRACK, "usr", "inputs", "modes_usr_n1024.txt"),
                prefix=""),
    "sr": dict(nmesh=64, nmax2=256, potential="quadratic", mass=1.82877655899024605e-01,
               phi0=-2.66679478988261254e+00, pi0=2.97300406808996935e-02, tlim=8.5,
               base="sr", modefile=os.path.join(TRACK, "ladder", "inputs", "modes_n256.txt"),
               prefix="sr_"),
}


def window(k, a, hub, s, sigma):
    return 0.5 * (1.0 + np.tanh(s * np.log(sigma * a * hub / k)))


class Modes(ul.Modes):
    def coeff(self, f):
        from scipy import fft
        F = fft.rfftn(f, workers=NTHREADS)
        return F[self.iz, self.iy, self.ix] * self.shift / self.N**3


class QuadReference(ul.Reference):
    """usr_lib.Reference with V = m^2 phi^2/2 (code units)."""

    def __init__(self, mass, phi0, pi0, k2, r0, dr0, t_eval, rtol=1e-12):
        self.mass = mass
        super().__init__(0.0, 0.0, phi0, pi0, k2, r0, dr0, t_eval, rtol=rtol)

    def _bg(self, phi, pi):
        v, dv = 0.5 * self.mass**2 * phi**2, self.mass**2 * phi
        hub = np.sqrt((8.0 * np.pi / 3.0) * (0.5 * pi * pi + v))
        eps1 = 4.0 * np.pi * pi * pi / (hub * hub)
        eps2 = 6.0 + 2.0 * dv / (hub * pi) - 2.0 * eps1
        return v, dv, hub, eps1, eps2


def reference(case, k2, r0, dr0, t_eval):
    c = CASES[case]
    if c["potential"] == "inflection":
        return ul.Reference(c["lam"], c["vev"], c["phi0"], c["pi0"], k2, r0, dr0, t_eval)
    return QuadReference(c["mass"], c["phi0"], c["pi0"], k2, r0, dr0, t_eval)


def shells(case):
    """Mode-file rows of the case's cut: n2, R, dR at N* (code units)."""
    c = CASES[case]
    n2, r, dr = ul.read_modefile(c["modefile"])
    sel = n2 <= c["nmax2"]
    return n2[sel], r[sel], dr[sel]
