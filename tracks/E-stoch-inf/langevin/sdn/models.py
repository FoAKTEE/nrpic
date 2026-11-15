"""Inflaton potentials and background initial conditions used by the Langevin package.

Units: reduced Planck mass M_Pl = 1, time = number of e-folds N.

Sources (paper sources under kb-data/raw/arxiv/<id>/<v>/src, read on 2026-11-15):
- Quadratic V = m^2 phi^2 / 2 with "potential-position fixing":
  2610.32592 v1 chap_ICsim.tex lines 63-71 (formula), 195 (eps1 = -eps2/2 = 0.01, H0 = 1e-5);
  2512.14649 v2 PRD_v2.tex lines 403-417 (Table I).
- Higgs-like inflection potential with "H0 fixing":
  2610.32592 v1 chap_ICsim.tex lines 73-74 (fixing), 350-359 (potential, parameters);
  2512.14649 v2 PRD_v2.tex lines 405-417 (Table I).
- Quadratic test of the importance-sampling paper: 2206.11234 v2 demonstration.tex lines
  18-25 (phi_in = sqrt(42), phi_end = sqrt(2), m = 1, 0.1, 0.001).
"""
import numpy as np

SQRT2 = np.sqrt(2.0)


class Quadratic:
    """V = m^2 phi^2 / 2."""

    def __init__(self, m):
        self.m = float(m)
        self.name = "quadratic"

    def V(self, phi):
        return 0.5 * self.m ** 2 * phi ** 2

    def dV(self, phi):
        return self.m ** 2 * phi

    def d2V(self, phi):
        return self.m ** 2 * np.ones_like(np.asarray(phi, dtype=float))


class HiggsInflection:
    """V = Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2) / [3 (3 phi^2 + 2 v^2)^2].

    dV/dphi = 2 Lambda v^5 phi (2 v^2 - phi^2)(sqrt2 phi + 2 v) / (3 phi^2 + 2 v^2)^3
    (derived with sympy in this package, JOURNAL entry 1): an exact inflection point
    (double root of V') at phi = -sqrt(2) v, a maximum at +sqrt(2) v, the minimum at 0.
    """

    def __init__(self, Lam=1.86e-6, v=0.198):
        self.Lam = float(Lam)
        self.v = float(v)
        self.name = "higgs_inflection"

    def V(self, phi):
        L, v = self.Lam, self.v
        return L * v ** 4 * phi ** 2 * (3 * phi ** 2 + 2 * SQRT2 * phi * v + 6 * v ** 2) / (
            3.0 * (3 * phi ** 2 + 2 * v ** 2) ** 2)

    def dV(self, phi):
        L, v = self.Lam, self.v
        return 2 * L * v ** 5 * phi * (2 * v ** 2 - phi ** 2) * (SQRT2 * phi + 2 * v) / (
            3 * phi ** 2 + 2 * v ** 2) ** 3

    def d2V(self, phi, h=1e-6):
        # central difference of the analytic first derivative (only used for the linear modes)
        return (self.dV(phi + h) - self.dV(phi - h)) / (2 * h)


def quadratic_potential_position(eps1=0.01, eps2=-0.02, H0=1e-5):
    """Potential-position fixing for V = lambda phi^p, p = 2 (2610.32592 chap_ICsim.tex 63-71).

    phi0 = -|(3 - eps1) p / (sqrt(2 eps1) (eps2/2 + eps1 - 3))|,
    lambda = |sqrt(2 eps1)(eps2/2 + eps1 - 3) / ((3 - eps1) p)|^p H0^2 (3 - eps1).
    With lambda = m^2 / 2. The field velocity is dphi/dN = +sqrt(2 eps1) (rolling towards
    the minimum from phi0 < 0); eps2 follows from the Klein-Gordon equation (checked in the
    background test). Returns (model, phi0, dphi/dN at N0, H0).
    """
    p = 2
    c = np.sqrt(2 * eps1) * (eps2 / 2 + eps1 - 3) / ((3 - eps1) * p)
    phi0 = -abs(1.0 / c)
    lam = abs(c) ** p * H0 ** 2 * (3 - eps1)
    m = np.sqrt(2 * lam)
    return Quadratic(m), phi0, np.sqrt(2 * eps1), H0


def h0_fixing(model, phi0):
    """H0 fixing (2610.32592 chap_ICsim.tex 73-74): slow-roll velocity dphi/dN = -V'/V at phi0
    (read as a velocity in e-folds; the dphi/dt reading would give dphi/dN ~ 1/H0 >> 1), then
    H0 from the Friedmann constraint H^2 = V / (3 - (dphi/dN)^2 / 2). Returns (dphi/dN, H0)."""
    dphidN = -model.dV(phi0) / model.V(phi0)
    H0 = np.sqrt(model.V(phi0) / (3.0 - 0.5 * dphidN ** 2))
    return dphidN, H0
