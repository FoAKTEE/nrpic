"""Shared pieces of the G0 verifier's scripts (independent of the track's reference code).

Background of the two test cases of arXiv:2512.14649 (P1, Table I at PRD_v2.tex:405-424),
integrated in cosmic time t with the variables (phi, dphi/dt, ln a) and H from the Friedmann
constraint 3 H^2 = dphi/dt^2/2 + V (reduced Planck mass Mpl = 1). Conventions of P1
(PRD_v2.tex:171 via SPEC.md 1): eps1 = -dlnH/dN, eps2 = -dln(eps1)/dN.
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
sys.path.insert(0, os.path.join(REPO, "python"))


def quadratic():
    """Potential-position fixing, P2 (2502.06783 v3) main_V2PRD.tex:399-405 with p = 2, solved
    here from the three conditions eps1, eps2, H at N0 by hand: V'/(H phidot) = eps2/2 + eps1 - 3,
    V = H^2 (3 - eps1), phidot = +H sqrt(2 eps1) (field rolls to positive phi)."""
    e1, e2, H0 = 0.01, -0.02, 1e-5
    phidot0 = H0 * np.sqrt(2 * e1)
    V0 = H0**2 * (3 - e1)
    dV0 = (e2 / 2 + e1 - 3) * H0 * phidot0
    phi0 = 2 * V0 / dV0                       # V = m^2 phi^2/2: V/V' = phi/2
    m2 = dV0 / phi0
    V = lambda f: 0.5 * m2 * f**2
    dV = lambda f: m2 * f
    d2V = lambda f: m2 + 0.0 * f
    return dict(name="SR", V=V, dV=dV, d2V=d2V, phi0=phi0, phidot0=phidot0, H0=H0,
                m=np.sqrt(m2), dNstar=5.0, dNsim=8.0)


def inflection(reading="dN"):
    """H0 fixing, P2 main_V2PRD.tex:408: phi0 given, velocity -Mpl^2 V'/V read as dphi/dN
    (reading='dN') or as dphi/dt (reading='dt'); H0 from the Friedmann constraint."""
    Lam, v = 1.86e-6, 0.198
    s2 = np.sqrt(2.0)

    def V(f):
        return Lam * v**4 * f**2 * (3 * f**2 + 2 * s2 * f * v + 6 * v**2) / (
            3 * (3 * f**2 + 2 * v**2) ** 2)

    def _dV_exact(f):
        num = f**2 * (3 * f**2 + 2 * s2 * f * v + 6 * v**2)
        dnum = 2 * f * (3 * f**2 + 2 * s2 * f * v + 6 * v**2) + f**2 * (6 * f + 2 * s2 * v)
        den = 3 * (3 * f**2 + 2 * v**2) ** 2
        dden = 3 * 2 * (3 * f**2 + 2 * v**2) * 6 * f
        return Lam * v**4 * (dnum * den - num * dden) / den**2

    def d2V(f, h=1e-5):
        return (_dV_exact(f + h) - _dV_exact(f - h)) / (2 * h)

    phi0 = -1.2
    u = -_dV_exact(phi0) / V(phi0)
    if reading == "dN":
        # dphi/dN = u: H^2 = V/(3 - u^2/2)
        H0 = np.sqrt(V(phi0) / (3 - 0.5 * u**2))
        phidot0 = u * H0
    else:
        phidot0 = u
        H0 = np.sqrt((0.5 * u**2 + V(phi0)) / 3)
    return dict(name="USR" if reading == "dN" else "USR_dt", V=V, dV=_dV_exact, d2V=d2V,
                phi0=phi0, phidot0=phidot0, H0=H0, u=u, dNstar=3.0, dNsim=10.0)


class Background:
    """Cosmic-time background; N = ln a with N = 0 at N0 (Bunch-Davies time)."""

    def __init__(self, mdl, Nend=None):
        self.m = mdl
        if Nend is None:
            Nend = mdl["dNstar"] + mdl["dNsim"] + 0.5
        H0 = mdl["H0"]
        self.T = 1.0 / H0                    # time unit
        y0 = [mdl["phi0"], mdl["phidot0"] * self.T, 0.0]    # phidot in units of H0

        def rhs(tau, y):                      # tau = H0 t
            f, fd, lna = y
            Vt = mdl["V"](f) * self.T**2
            H = np.sqrt((0.5 * fd**2 + Vt) / 3.0)
            return [fd, -3 * H * fd - mdl["dV"](f) * self.T**2, H]

        def ev(tau, y):
            return y[2] - Nend
        ev.terminal = True
        sol = solve_ivp(rhs, (0.0, 50.0 * Nend), y0, method="DOP853", rtol=1e-13,
                        atol=[1e-15, 1e-17, 1e-15], dense_output=True, events=ev,
                        max_step=0.02)
        assert sol.status == 1, sol.message
        self.sol = sol
        self.rhs = rhs
        self.tau_end = sol.t[-1]

    def at_tau(self, tau):
        f, fd, lna = self.sol.sol(tau)
        Vt = self.m["V"](f) * self.T**2
        H = np.sqrt((0.5 * fd**2 + Vt) / 3.0)
        fdd = -3 * H * fd - self.m["dV"](f) * self.T**2
        eps1 = 0.5 * fd**2 / H**2
        eps2 = -2 * fdd / (H * fd) - 2 * eps1
        return dict(phi=f, phidot=fd / self.T, N=lna, H=H / self.T, eps1=eps1, eps2=eps2,
                    V=self.m["V"](f), tau=tau)

    def tau_of_N(self, N):
        from scipy.optimize import brentq
        return brentq(lambda t: self.sol.sol(t)[2] - N, 0.0, self.tau_end, xtol=1e-14)

    def at_N(self, N):
        return self.at_tau(self.tau_of_N(N))

    def grid(self, n=4000):
        tau = np.linspace(0.0, self.tau_end, n)
        d = [self.at_tau(t) for t in tau]
        return {k: np.array([x[k] for x in d]) for k in d[0]}


def save_json(path, obj):
    import json

    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=conv)
