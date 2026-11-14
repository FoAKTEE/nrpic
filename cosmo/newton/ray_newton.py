"""Light rays in the effective spacetime of a Newtonian particle-mesh run (cosmo/PLAN.md,
C3), the counterpart of the null particles of the relativistic code.

The dictionary metric is ds^2 = a^2 [-(1 + 2 psi) dtau^2 + (1 - 2 psi) dx^2]. Null
geodesics do not depend on the conformal factor a^2, so the rays are integrated in the
metric in brackets with Hamilton's equations for the covariant momentum k_i,

    dx^i/dtau = f k_i / |k|,    dk_i/dtau = -|k| f'(psi) d_i psi,
    f = sqrt((1 + 2 psi) / (1 - 2 psi)),

with |k| the Euclidean norm, by fourth-order Runge-Kutta at the step of the particle-
mesh run; the potential and its gradient are interpolated with cubic splines in space
and linearly in time across the step.

A bundle (cosmo/ic/ray_ic.py) leaves the overdensity or the underdensity when the proper
time of the observer there reaches a given value, which is taken from the relativistic
run, so that the two calculations emit at the same proper time. The records have the
layout of the relativistic tracks and go through the same analysis
(cosmo/analysis/ray_obs.py): physical metric a^2 (1 - 2 psi) delta_ij, covariant momentum,
and the covariant velocity of the matter seen by the normal observer,
v_i = a (1 - 2 psi) v^i / sqrt(1 + 2 psi) with v^i = dx^i/dtau the mass-weighted mean of
the particles on the mesh.
"""
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ic"))
import cosmo_id as cid  # noqa: E402
import ray_ic as ry  # noqa: E402
from pm import scale_factor  # noqa: E402


class Field:
    """A periodic cell-centred field prepared for repeated cubic interpolation."""

    def __init__(self, f, L):
        self.n, self.L = f.shape[0], L
        self.c = ndimage.spline_filter(f, order=3, mode="grid-wrap")

    def __call__(self, x):
        return ndimage.map_coordinates(self.c, (x/(self.L/self.n) - 0.5).T, order=3,
                                       mode="grid-wrap", prefilter=False)


class Potential:
    """psi and its gradient on the mesh at one time."""

    def __init__(self, tor, psi):
        self.psi = Field(psi, tor.L)
        F = tor.fft(psi)
        self.grad = [Field(tor.ifft(1j*kd*F), tor.L) for kd in tor.kd]

    def at(self, x):
        return self.psi(x), np.stack([g(x) for g in self.grad], axis=1)


class NewtonRays:
    """emit: list of (kind, tau_e): kind 0 leaves the overdensity (probe 0) towards the
    underdensity, kind 1 the reverse; tau_e is the proper time of the emitter."""

    def __init__(self, pm, emit, eps=1e-4):
        self.pm, self.L, self.eps = pm, pm.L, eps
        self.pending = [dict(kind=int(k), tau_e=float(t), bundle=i)
                        for i, (k, t) in enumerate(emit)]
        self.active = []
        self.pot0 = None

    # ---- geodesic right-hand side at fraction s of the step
    def rhs(self, x, k, s, pot0, pot1):
        p0, g0 = pot0.at(x)
        p1, g1 = pot1.at(x)
        psi = (1.0 - s)*p0 + s*p1
        grad = (1.0 - s)*g0 + s*g1
        kn = np.sqrt((k*k).sum(axis=1))
        f = np.sqrt((1.0 + 2.0*psi)/(1.0 - 2.0*psi))
        fp = 2.0/(np.sqrt(1.0 + 2.0*psi)*(1.0 - 2.0*psi)**1.5)
        return (f/kn)[:, None]*k, -(kn*fp)[:, None]*grad

    def advance(self, x, k, s0, dtau, pot0, pot1):
        """From fraction s0 of the step to its end."""
        h = (1.0 - s0)*dtau
        ds = 1.0 - s0
        k1x, k1k = self.rhs(x, k, s0, pot0, pot1)
        k2x, k2k = self.rhs(x + 0.5*h*k1x, k + 0.5*h*k1k, s0 + 0.5*ds, pot0, pot1)
        k3x, k3k = self.rhs(x + 0.5*h*k2x, k + 0.5*h*k2k, s0 + 0.5*ds, pot0, pot1)
        k4x, k4k = self.rhs(x + h*k3x, k + h*k3k, 1.0, pot0, pot1)
        return (x + h*(k1x + 2.0*k2x + 2.0*k3x + k4x)/6.0,
                k + h*(k1k + 2.0*k2k + 2.0*k3k + k4k)/6.0)

    def matter_velocity(self, x):
        """Mass-weighted mean of dx/dtau of the particles at the points x, from the
        filtered mesh sums as in the relativistic code."""
        pm = self.pm
        if self._vel is None:
            v = pm.velocity()
            rho = cid.binomial(cid.cic_deposit(pm.x, pm.m, pm.n, pm.L, pm.shape),
                               pm.nfilter, pm.compensate)
            mom = [cid.binomial(cid.cic_deposit(pm.x, pm.m*v[:, i], pm.n, pm.L, pm.shape),
                                pm.nfilter, pm.compensate) for i in range(3)]
            self._vel = (rho, mom)
        rho, mom = self._vel
        r = cid.interp(rho, x, pm.L, order=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.stack([np.where(r > 0.0, cid.interp(m_, x, pm.L, order=1)/r, 0.0)
                             for m_ in mom], axis=1)

    def record(self, b, tau, pot):
        a = scale_factor(tau, self.pm.H0)
        psi, _ = pot.at(b["x"])
        v = self.matter_velocity(b["x"])
        b["rec"]["t"].append(tau)
        b["rec"]["x"].append(b["x"].copy())
        b["rec"]["k"].append(b["k"].copy())
        b["rec"]["g"].append(a*a*(1.0 - 2.0*psi))
        b["rec"]["v"].append((a*(1.0 - 2.0*psi)/np.sqrt(1.0 + 2.0*psi))[:, None]*v)

    def __call__(self, pm, tau0, psi0, tp0, r0, psi1, tp1, r1):
        dtau = pm.tau - tau0
        pot0 = self.pot0 if self.pot0 is not None else Potential(pm.tor, psi0)
        pot1 = Potential(pm.tor, psi1)
        self._vel = None
        for b in self.active:
            b["x"], b["k"] = self.advance(b["x"], b["k"], 0.0, dtau, pot0, pot1)
            self.record(b, pm.tau, pot1)
        for b in list(self.pending):
            i = b["kind"]
            if not (tp0[i] <= b["tau_e"] < tp1[i]):
                continue
            # proper time within the step: t_p0 + dtau [s r0 + s^2 (r1 - r0) / 2]
            A, B, C = 0.5*(r1[i] - r0[i]), r0[i], -(b["tau_e"] - tp0[i])/dtau
            s = -C/B if abs(A) < 1e-14*abs(B) else (-B + np.sqrt(B*B - 4.0*A*C))/(2.0*A)
            s = min(max(s, 0.0), 1.0)
            pt = 0.25*self.L if i == 0 else 0.75*self.L
            x = np.full((5, 3), pt)
            c = ry.directions(1.0 if i == 0 else -1.0, self.eps)
            tau_l = tau0 + s*dtau
            a_l = scale_factor(tau_l, pm.H0)
            p0, _ = pot0.at(x[:1])
            p1, _ = pot1.at(x[:1])
            psi_l = float((1.0 - s)*p0[0] + s*p1[0])
            g_l = a_l*a_l*(1.0 - 2.0*psi_l)
            # unit frequency for the normal observer of the physical metric
            k = np.sqrt(g_l)*c/np.sqrt((c*c).sum(axis=1))[:, None]
            # velocity of the matter at the emitter (zero by symmetry): take the end of
            # the step, the nearest deposit
            v_l = self.matter_velocity(x[:1])[0]*a_l*(1.0 - 2.0*psi_l)/np.sqrt(1.0 + 2.0*psi_l)
            b.update(x=x, k=k, c=c, tau_launch=tau_l, a_launch=a_l, psi_launch=psi_l,
                     g_launch=g_l, v_launch=v_l,
                     rec={"t": [], "x": [], "k": [], "g": [], "v": []})
            b["x"], b["k"] = self.advance(b["x"], b["k"], s, dtau, pot0, pot1)
            self.record(b, pm.tau, pot1)
            self.pending.remove(b)
            self.active.append(b)
        self.pot0 = pot1

    def results(self):
        """Per bundle: arrays in the layout of cosmo/analysis/ray_obs.bundle_observables."""
        out = []
        for b in sorted(self.active, key=lambda q: q["bundle"]):
            g = np.array(b["rec"]["g"])
            out.append({"bundle": b["bundle"], "kind": b["kind"], "tau_emit": b["tau_e"],
                        "tau_launch": b["tau_launch"], "a_launch": b["a_launch"],
                        "t": np.array(b["rec"]["t"]), "x": np.array(b["rec"]["x"]),
                        "k": np.array(b["rec"]["k"]),
                        "g": g[:, :, None, None]*np.eye(3),
                        "v": np.array(b["rec"]["v"]),
                        "c": b["c"], "g_launch": b["g_launch"]*np.eye(3),
                        "v_launch": b["v_launch"], "eps": self.eps})
        return out


def observables(res, L=4.0, H0=1.0):
    """Redshift and distances of the bundles of results(), with the shared analysis."""
    here = os.path.dirname(os.path.abspath(__file__))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ray_obs", os.path.join(here, "..", "analysis", "ray_obs.py"))
    ar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ar)
    out = []
    for b in res:
        nt = len(b["t"])
        o = ar.bundle_observables(b["t"], b["x"], b["k"], b["g"], np.ones((nt, 5)),
                                  b["v"], b["c"], b["g_launch"], 1.0, b["v_launch"],
                                  b["eps"], L, -1)
        o.update({"bundle": b["bundle"], "kind": b["kind"], "tau_emit": b["tau_emit"],
                  "a_emit": (1.0 + 1.5*H0*b["tau_emit"])**(2.0/3.0),
                  "D_FRW": ar.frw_distance(o["z"], b["tau_emit"], H0)})
        out.append(o)
    return out
