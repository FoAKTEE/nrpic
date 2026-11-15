"""Exact evolution of the shells of the dust ball (DERIVATION.md, section 5).

Every shell keeps its Misner-Sharp mass m and bound energy E until shells cross, and its
areal radius obeys (dR/dtau)^2 = 2m/R + 2E, tau the proper time of the dust measured from
the initial slice. With t the time since the shell's own bang (t = age_i + tau):

    E < 0:  R = A (1 - cos eta),  t = T0 (eta - sin eta),   A = m/(-2E), T0 = m/(-2E)^(3/2)
    E = 0:  R = (9 m/2)^(1/3) t^(2/3)
    E > 0:  R = A (cosh eta - 1), t = T0 (sinh eta - eta),  A = m/(2E),  T0 = m/(2E)^(3/2)

turnaround t_ta = pi T0 (R = m/(-E)), crunch t_c = 2 pi T0, and the sphere of the shell is
marginally trapped (R = 2m, collapsing branch) at cos(eta_AH) = 1 + 4E,
t_AH = 2 t_ta - (4/3) m F(-2E). The age on the initial slice is
age_i = (2/3) R_i^(3/2) (2m)^(-1/2) F(-E R_i/m), F = 2F1(1/2, 3/2; 5/2; .); for the core and
the Einstein-de Sitter envelope it equals t_i = 2/(3H) (simultaneous bang time).

These proper times are invariants of the spacetime (the proper time along a dust world line
between the initial slice and an event defined by the round sphere through it), so they
can be compared with any slicing of the evolution code, through the particles' proper time.
"""

import math

import numpy as np

from .model import Fm1

__all__ = ["t_expanding", "Shells"]


def t_expanding(R, m, E):
    """Time since the bang along the expanding branch at areal radius R."""
    R, m, E = (np.asarray(a, dtype=float) for a in (R, m, E))
    return (2.0 / 3.0) * R ** 1.5 / np.sqrt(2.0 * m) * (1.0 + Fm1(-E * R / m))


def _x_minus_sin(x):
    x = np.asarray(x, dtype=float)
    out = x - np.sin(x)
    s = np.abs(x) < 0.5
    xs = x[s]
    x2 = xs * xs
    acc = np.zeros_like(xs)
    for k in range(10, 0, -1):          # x^3/3! - x^5/5! + ... (10 terms)
        acc = acc * (-x2) + 1.0 / math.factorial(2 * k + 1)
    out[s] = xs ** 3 * acc
    return out


def _sinh_minus_x(x):
    x = np.asarray(x, dtype=float)
    out = np.sinh(x) - x
    s = np.abs(x) < 0.5
    xs = x[s]
    x2 = xs * xs
    acc = np.zeros_like(xs)
    for k in range(10, 0, -1):
        acc = acc * x2 + 1.0 / math.factorial(2 * k + 1)
    out[s] = xs ** 3 * acc
    return out


def _solve_eta(q, bound):
    """eta - sin eta = q on [0, 2 pi] (bound) or sinh eta - eta = q (unbound), Newton with
    a bisection safeguard; q may be any array."""
    q = np.asarray(q, dtype=float)
    if bound:
        lo, hi = np.zeros_like(q), np.full_like(q, 2 * math.pi)
        eta = np.where(q < 1.0, np.cbrt(6.0 * q), np.clip(q, 0, 2 * math.pi))
        fun, der = _x_minus_sin, lambda e: 2.0 * np.sin(0.5 * e) ** 2
    else:
        lo, hi = np.zeros_like(q), np.maximum(np.cbrt(6.0 * q), np.log(2 * q + 2)) + 1.0
        eta = np.where(q < 1.0, np.cbrt(6.0 * q), np.log(2 * q + 1) + 1.0)
        fun, der = _sinh_minus_x, lambda e: 2.0 * np.sinh(0.5 * e) ** 2
    eta = np.clip(eta, lo, hi)
    for _ in range(200):
        r = fun(eta) - q
        conv = np.abs(r) <= 4e-16 * np.maximum(np.abs(q), 1e-300)
        if np.all(conv):
            break
        lo = np.where(r < 0, eta, lo)
        hi = np.where(r > 0, eta, hi)
        d = der(eta)
        en = np.where(d > 0, eta - r / np.where(d > 0, d, 1.0), 0.5 * (lo + hi))
        en = np.where((en < lo) | (en > hi) | ~np.isfinite(en), 0.5 * (lo + hi), en)
        step_done = np.abs(en - eta) <= 4e-16 * np.maximum(eta, 1e-300)
        eta = np.where(conv, eta, en)   # converged entries are never moved again
        if np.all(conv | step_done):
            break
    return eta


class Shells:
    """Dust shells labelled by their areal radius R_i on the initial slice of `ball`."""

    def __init__(self, ball, R_i):
        self.ball = ball
        self.R_i = np.atleast_1d(np.asarray(R_i, dtype=float))
        if np.any(self.R_i <= 0) or np.any(self.R_i > ball.R_out):
            raise ValueError("shell labels must lie in (0, R_b + w]")
        c = ball.at(self.R_i)
        self.m, self.E, self.v_i = c["m"], c["E"], c["v"]
        if np.any(self.R_i <= 2 * self.m):
            raise ValueError("a shell is (anti-)trapped on the initial slice")
        self.age_i = t_expanding(self.R_i, self.m, self.E)
        neg = self.E < 0
        self.bound = neg
        T0 = np.full_like(self.m, np.inf)
        T0[neg] = self.m[neg] / (-2.0 * self.E[neg]) ** 1.5
        self.T0 = T0
        self.t_ta = math.pi * T0
        self.t_c = 2.0 * math.pi * T0
        # apparent horizon (R = 2m on the collapsing branch)
        self.t_ah = np.full_like(self.m, np.inf)
        self.t_ah[neg] = 2.0 * self.t_ta[neg] - (4.0 / 3.0) * self.m[neg] * (1.0 + Fm1(-2.0 * self.E[neg]))
        self.tau_ta = self.t_ta - self.age_i
        self.tau_c = self.t_c - self.age_i
        self.tau_ah = self.t_ah - self.age_i
        self.R_max = np.where(neg, self.m / np.where(neg, -self.E, 1.0), np.inf)

    def tau_ah_cycloid(self):
        """Apparent-horizon proper time from the cycloid angle (independent of t_ah)."""
        out = np.full_like(self.m, np.inf)
        b = self.bound
        eta = 2 * math.pi - np.arccos(1.0 + 4.0 * self.E[b])
        out[b] = self.T0[b] * _x_minus_sin(eta) - self.age_i[b]
        return out

    def R(self, tau):
        """Areal radius of every shell at proper time tau (broadcast: shells x times);
        0 after the crunch."""
        tau = np.asarray(tau, dtype=float)
        sh = (self.R_i.size,) + tau.shape
        m = np.broadcast_to(self.m.reshape((-1,) + (1,) * tau.ndim), sh)
        E = np.broadcast_to(self.E.reshape((-1,) + (1,) * tau.ndim), sh)
        T0 = np.broadcast_to(self.T0.reshape((-1,) + (1,) * tau.ndim), sh)
        t = np.broadcast_to(self.age_i.reshape((-1,) + (1,) * tau.ndim), sh) + tau
        out = np.zeros(sh)
        b = E < 0
        z = E == 0
        u = E > 0
        if np.any(b):
            q = t[b] / T0[b]
            eta = _solve_eta(np.clip(q, 0, 2 * math.pi), True)
            A = m[b] / (-2.0 * E[b])
            Rb = 2.0 * A * np.sin(0.5 * eta) ** 2
            Rb[q >= 2 * math.pi] = 0.0
            out[b] = Rb
        if np.any(z):
            out[z] = np.cbrt(4.5 * m[z]) * np.maximum(t[z], 0) ** (2.0 / 3.0)
        if np.any(u):
            T0u = m[u] / (2.0 * E[u]) ** 1.5
            eta = _solve_eta(t[u] / T0u, False)
            out[u] = 2.0 * m[u] / (2.0 * E[u]) * np.sinh(0.5 * eta) ** 2
        return out

    def dRdtau(self, tau):
        """dR/dtau = +-sqrt(2m/R + 2E): + before turnaround, - after."""
        R = self.R(tau)
        tau = np.asarray(tau, dtype=float)
        sh = R.shape
        m = np.broadcast_to(self.m.reshape((-1,) + (1,) * tau.ndim), sh)
        E = np.broadcast_to(self.E.reshape((-1,) + (1,) * tau.ndim), sh)
        tta = np.broadcast_to(self.tau_ta.reshape((-1,) + (1,) * tau.ndim), sh)
        sgn = np.where(tau < tta, 1.0, -1.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            return sgn * np.sqrt(np.maximum(2 * m / R + 2 * E, 0.0))

    def first_horizon(self):
        """Earliest proper time at which a shell's sphere becomes marginally trapped."""
        k = int(np.argmin(self.tau_ah))
        return dict(tau_ah=float(self.tau_ah[k]), R_i=float(self.R_i[k]), m=float(self.m[k]),
                    index=k)

    def shell_crossing(self, tau):
        """Earliest tau of the grid at which two neighbouring shells (sorted by R_i) that
        have not crunched have R non-increasing outward; inf if none."""
        order = np.argsort(self.R_i)
        R = self.R(tau)[order]
        alive = R[:-1] > 0
        bad = (np.diff(R, axis=0) <= 0) & alive
        hit = np.any(bad, axis=0)
        if not np.any(hit):
            return math.inf
        return float(np.asarray(tau)[np.argmax(hit)])

    def summary(self):
        fh = self.first_horizon()
        b = self.bound
        out = dict(n_shells=int(self.R_i.size), t_i=self.ball.t_i,
                   first_horizon=fh)
        if np.any(b):
            k0 = int(np.argmin(self.R_i))
            out.update(tau_ta_innermost=float(self.tau_ta[k0]), tau_c_innermost=float(self.tau_c[k0]),
                       R_i_innermost=float(self.R_i[k0]),
                       tau_ta_min=float(self.tau_ta[b].min()), tau_c_min=float(self.tau_c[b].min()))
        return out
