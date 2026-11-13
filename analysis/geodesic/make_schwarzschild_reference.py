#!/usr/bin/env python3
"""Design the three Schwarzschild (a = 0) single-particle orbits and their exact solutions.

Writes problems/schwarzschild/ref/orbits.json with, per orbit: the initial state in spherical
Kerr-Schild ('ks', particle coordinates r, theta, phi) and Cartesian Kerr-Schild ('cks', x, y, z),
the invariants, t_end, and exact states at checkpoints (every `dt_check` M and at t_end) in both
systems.  t_end and the checkpoints are multiples of 0.08 M, so they fall on the step grids of
all dt values used (0.08 ... 0.005 M).

Orbits
  circ    circular, r = 8 M, equatorial.  Exact: r = 8, phi = Omega t, Omega = sqrt(M/r^3).
  ecc     eccentric bound, p = 8 M, e = 0.3 (6.154 M <= r <= 11.43 M), orbital plane inclined by
          30 deg, starts at pericentre on the equator.  Exact: nrpic.kerr.MinoOrbit at a = 0
          (Mino-time quadrature, mpmath 30 digits).
  plunge  E = 0.99, L = 3.9 M (L below the critical value 3.92 M for this E: no turning point),
          plane inclined by 45 deg, starts inbound at r = 10 M, whirls about twice near the
          potential peak at r = 4.11 M, crosses the horizon at t = 75.07 M and is stopped at
          t_end = 77.52 M (r = 1.01 M), before the singularity.  Exact: quadrature in r of
          dt_KS/dr and dpsi/dr written in a form that is regular at r = 2M (mpmath 30 digits).

Each exact solution is also checked against a free-running DOP853 integration of the 3+1
equations (nrpic.geodesic, rtol = atol = 2.5e-14); the deviations are stored under `check`.

Usage: python3 analysis/geodesic/make_schwarzschild_reference.py
"""

from __future__ import annotations

import time

import mpmath as mp
import numpy as np

from geo_common import SCHW_REF_JSON, save_json, kerr  # noqa: F401  (sets sys.path)
from nrpic import geodesic

A = 0.0
M = 1.0
DPS = 30


def mpf(v):
    return mp.mpf(float(v)) if not isinstance(v, mp.mpf) else v


# ------------------------------------------------------------------------------------------
# initial states
# ------------------------------------------------------------------------------------------

def bl_to_ks_cks(x_bl, u_bl):
    _, x_ks, u_ks = kerr.convert_state(0.0, np.array(x_bl), np.array(u_bl), "bl", "ks", A, M)
    _, x_cks, u_cks = kerr.convert_state(0.0, x_ks, u_ks, "ks", "cks", A, M)
    return x_ks, u_ks, x_cks, u_cks


def design():
    orbs = {}
    # circular, r = 8 M, equatorial
    r = 8.0
    E = (1 - 2 * M / r) / np.sqrt(1 - 3 * M / r)
    L = np.sqrt(M * r) / np.sqrt(1 - 3 * M / r)
    x_ks = np.array([r, np.pi / 2, 0.0])
    u_ks = np.array([2 * M * E / (r - 2 * M), 0.0, L])
    _, x_cks, u_cks = kerr.convert_state(0.0, x_ks, u_ks, "ks", "cks", A, M)
    orbs["circ"] = dict(
        description="circular orbit, r = 8 M, equatorial plane",
        params=dict(r=r, E=E, L=L, inclination_deg=0.0),
        t_end=1000.0, dt_check=50.0, x_ks=x_ks, u_ks=u_ks, x_cks=x_cks, u_cks=u_cks)
    # eccentric bound, p = 8, e = 0.3, inclined 30 deg, from pericentre
    p, e, inc = 8.0, 0.3, np.deg2rad(30.0)
    L = np.sqrt(p * p * M * M / (p - 3 - e * e))
    E = np.sqrt(((p - 2) ** 2 - 4 * e * e) / (p * (p - 3 - e * e)))
    rp = p * M / (1 + e)
    x_ks, u_ks, x_cks, u_cks = bl_to_ks_cks([rp, np.pi / 2, 0.0],
                                            [0.0, -L * np.sin(inc), L * np.cos(inc)])
    orbs["ecc"] = dict(
        description="eccentric bound orbit, p = 8 M, e = 0.3, orbital plane inclined by 30 deg, "
                    "starts at pericentre",
        params=dict(p=p, e=e, E=E, L=L, inclination_deg=30.0, r_peri=rp, r_apo=p * M / (1 - e)),
        t_end=1000.0, dt_check=50.0, x_ks=x_ks, u_ks=u_ks, x_cks=x_cks, u_cks=u_cks)
    # plunge
    E, L, inc, r0 = 0.99, 3.9, np.deg2rad(45.0), 10.0
    R0 = np.sqrt(E * E - (1 - 2 * M / r0) * (1 + L * L / r0 ** 2))
    x_ks, u_ks, x_cks, u_cks = bl_to_ks_cks([r0, np.pi / 2, 0.0],
                                            [-R0 / (1 - 2 * M / r0), -L * np.sin(inc),
                                             L * np.cos(inc)])
    orbs["plunge"] = dict(
        description="plunging orbit, E = 0.99, L = 3.9 M, plane inclined by 45 deg, starts inbound "
                    "at r = 10 M, crosses the horizon, stopped at r ~ 1 M",
        params=dict(E=E, L=L, inclination_deg=45.0, r0=r0),
        t_end=77.52, dt_check=4.0, x_ks=x_ks, u_ks=u_ks, x_cks=x_cks, u_cks=u_cks)
    return orbs


# ------------------------------------------------------------------------------------------
# exact solutions
# ------------------------------------------------------------------------------------------

class Circular:
    def __init__(self, x_ks, u_ks):
        self.r = float(x_ks[0])
        self.u = np.array(u_ks)
        self.Omega = np.sqrt(M / self.r ** 3)

    def state(self, t):
        x = np.array([self.r, np.pi / 2, self.Omega * t])
        u = self.u.copy()
        _, xc, uc = kerr.convert_state(t, x, u, "ks", "cks", A, M)
        return x, u, xc, uc


class Plunge:
    """Exact Schwarzschild plunge in Kerr-Schild time, r monotonic (no turning point)."""

    def __init__(self, x_ks, u_ks):
        with mp.workdps(DPS + 10):
            r, th, ph = (mpf(v) for v in x_ks)
            ur, uth, uph = (mpf(v) for v in u_ks)
            self.E = kerr._mp_energy_ks(r, th, (ur, uth, uph), mpf(A), mpf(M))
            self.Lz = uph
            self.Q = uth ** 2 + mp.cos(th) ** 2 * self.Lz ** 2 / mp.sin(th) ** 2
            self.L = mp.sqrt(self.Q + self.Lz ** 2)
            self.r0 = r
            # orbital plane: e1 = initial radial direction, e2 = initial tangential direction
            st, ct = mp.sin(th), mp.cos(th)
            self.e1 = [st, mp.mpf(0), ct]
            v = [uth * ct, uph / st, -uth * st]
            nv = mp.sqrt(sum(c * c for c in v))
            self.e2 = [c / nv for c in v]
        self.M = mpf(M)

    def R(self, r):
        return mp.sqrt(self.E ** 2 - (1 - 2 * self.M / r) * (1 + self.L ** 2 / r ** 2))

    def gt(self, r):
        """-dt_KS/dr (> 0), regular at r = 2M."""
        R = self.R(r)
        num = self.E ** 2 * (r + 2 * self.M) + 4 * self.M ** 2 / r * (1 + self.L ** 2 / r ** 2)
        return num / ((2 * self.M * R + self.E * r) * R)

    def gpsi(self, r):
        return self.L / (r * r * self.R(r))

    def _pts(self, r):
        pts = [r]
        for c in (1.5, 2.0, 3.0, 4.11, 6.0):
            if r < c < self.r0:
                pts.append(mp.mpf(c))
        pts.append(self.r0)
        return pts

    def t_of_r(self, r):
        with mp.workdps(DPS):
            return mp.quad(self.gt, self._pts(mpf(r)))

    def psi_of_r(self, r):
        with mp.workdps(DPS):
            return mp.quad(self.gpsi, self._pts(mpf(r)))

    def r_of_t(self, t, guess):
        with mp.workdps(DPS):
            t = mpf(t)
            if t == 0:
                return self.r0
            r = mpf(guess)
            for _ in range(60):
                f = self.t_of_r(r) - t
                rn = r + f / self.gt(r)        # d t/d r = -gt
                if abs(rn - r) < mp.mpf(10) ** (-(DPS - 4)):
                    return rn
                r = rn
            raise RuntimeError("r(t) did not converge")

    def state(self, t, guess):
        with mp.workdps(DPS):
            r = self.r_of_t(t, guess)
            psi = self.psi_of_r(r)
            cp, sp = mp.cos(psi), mp.sin(psi)
            n = [cp * a + sp * b for a, b in zip(self.e1, self.e2)]
            th = mp.acos(n[2])
            ph = mp.atan2(n[1], n[0])
            ph = ph + 2 * mp.pi * mp.nint((psi - ph) / (2 * mp.pi))   # continuous azimuth
            R = self.R(r)
            E, L, Mm = self.E, self.L, self.M
            ur = -(E ** 2 * (r + 2 * Mm) - r - L ** 2 / r) / (2 * Mm * E + R * r)
            # u_theta = L dtheta/dpsi, theta = acos(n_z)
            dnz = -sp * self.e1[2] + cp * self.e2[2]
            uth = -L * dnz / mp.sin(th)
            x = np.array([float(r), float(th), float(ph)])
            u = np.array([float(ur), float(uth), float(self.Lz)])
        _, xc, uc = kerr.convert_state(t, x, u, "ks", "cks", A, M)
        return x, u, xc, uc


def check_times(t_end, dt_check):
    n = int(np.floor(t_end / dt_check + 1e-9))
    ts = [k * dt_check for k in range(n + 1)]
    if abs(ts[-1] - t_end) > 1e-9:
        ts.append(t_end)
    return ts


def main():
    T0 = time.time()
    orbs = design()
    out = dict(
        description="Schwarzschild (a = 0) single-particle orbits for the NRPIC pusher tests; "
                    "generated by analysis/geodesic/make_schwarzschild_reference.py",
        a=A, M=M,
        conventions=dict(
            ks="spherical Kerr-Schild (r, theta, phi); u = covariant (u_r, u_theta, u_phi)",
            cks="Cartesian Kerr-Schild (x, y, z) = r (sin th cos ph, sin th sin ph, cos th) for a = 0",
            time="Kerr-Schild coordinate time; runs start at t = 0 at the initial event",
            exact_states="x_ks (phi continuous), u_ks, x_cks, u_cks at each checkpoint time"),
        orbits={})
    for name, o in orbs.items():
        x_ks, u_ks = o["x_ks"], o["u_ks"]
        E, Lz, Q = (float(v) for v in kerr.invariants("ks", x_ks, u_ks, A, M))
        Ec, Lzc, Qc = (float(v) for v in kerr.invariants("cks", o["x_cks"], o["u_cks"], A, M))
        ts = check_times(o["t_end"], o["dt_check"])
        rec = dict(description=o["description"], params=o["params"], t_end=o["t_end"],
                   initial_state=dict(ks=dict(x=x_ks.tolist(), u=u_ks.tolist()),
                                      cks=dict(x=o["x_cks"].tolist(), u=o["u_cks"].tolist())),
                   invariants=dict(E=E, Lz=Lz, Q=Q, L=float(np.sqrt(Q + Lz * Lz))),
                   invariants_cks_state=dict(E=Ec, Lz=Lzc, Q=Qc))
        # DOP853 reference (dense) for guesses and the cross-check
        tr = geodesic.integrate("ks", x_ks, u_ks, o["t_end"], t_eval=np.array(ts), rtol=2.5e-14,
                                atol=2.5e-14, a=A, M=M, max_step=0.1)
        trc = geodesic.integrate("cks", o["x_cks"], o["u_cks"], o["t_end"], t_eval=np.array(ts),
                                 rtol=2.5e-14, atol=2.5e-14, a=A, M=M, max_step=0.1)
        if name == "circ":
            ex = Circular(x_ks, u_ks)
            states = [ex.state(t) for t in ts]
            rec["periods"] = dict(Omega=float(ex.Omega), T_phi=float(2 * np.pi / ex.Omega))
        elif name == "ecc":
            orb = kerr.MinoOrbit.from_state("ks", 0.0, x_ks, u_ks, A, M, DPS)
            states = []
            lam = None
            for t in ts:
                st, lam = orb.states_at_time(t, "ks", ("ks", "cks"), guess=lam)
                states.append((np.array([float(c) for c in st["ks"][1]]),
                               np.array([float(c) for c in st["ks"][2]]),
                               np.array([float(c) for c in st["cks"][1]]),
                               np.array([float(c) for c in st["cks"][2]])))
            per = orb.periods()
            with mp.workdps(DPS):
                lams = orb.pericenter_lambdas(2 * o["t_end"] / per["Gamma"] + 2 * per["Lambda_r"])
                peri_t = [float(orb.time_at_lambda(lm, "ks")) for lm in lams]
            peri_t = [t for t in peri_t if t <= o["t_end"]]
            rec["periods"] = {k: float(v) for k, v in per.items()}
            rec["turning_points"] = dict(r_peri=float(orb.r2), r_apo=float(orb.r1),
                                         r3=float(orb.r3), p=float(orb.p), e=float(orb.e),
                                         theta_min=float(mp.acos(mp.sqrt(orb.zm))))
            rec["pericenter_t"] = peri_t
            rec["periapsis_advance_per_radial_period"] = float(
                per["Omega_phi"] * per["T_r"] - 2 * mp.pi)
        else:
            ex = Plunge(x_ks, u_ks)
            states = [ex.state(t, tr.x[k, 0]) for k, t in enumerate(ts)]
            with mp.workdps(DPS):
                rec["horizon_crossing_t"] = float(ex.t_of_r(2))
                rec["psi_total_at_t_end"] = float(ex.psi_of_r(states[-1][0][0]))
                rmin_R = mp.findroot(lambda r: mp.diff(lambda s: ex.E ** 2 - ex.R(s) ** 2, r), 4.1)
                rec["potential_peak"] = dict(r=float(rmin_R), E2_minus_Vmax=float(ex.R(rmin_R) ** 2))
            rec["r_end"] = float(states[-1][0][0])
        rec["checkpoints"] = dict(
            t=ts, x_ks=[s[0].tolist() for s in states], u_ks=[s[1].tolist() for s in states],
            x_cks=[s[2].tolist() for s in states], u_cks=[s[3].tolist() for s in states])
        rec["final_state"] = dict(t=ts[-1], ks=dict(x=states[-1][0].tolist(), u=states[-1][1].tolist()),
                                  cks=dict(x=states[-1][2].tolist(), u=states[-1][3].tolist()))
        # cross-check exact vs DOP853
        xk = np.array([s[0] for s in states])
        uk = np.array([s[1] for s in states])
        xc = np.array([s[2] for s in states])
        uc = np.array([s[3] for s in states])
        rec["check"] = dict(
            dop853_ks_max_dev_x=float(np.max(np.abs(tr.x - xk))),
            dop853_ks_max_dev_u=float(np.max(np.abs(tr.u - uk))),
            dop853_cks_max_dev_x=float(np.max(np.abs(trc.x - xc))),
            dop853_cks_max_dev_u=float(np.max(np.abs(trc.u - uc))),
            exact_invariants_max_dev=[float(np.max(np.abs(np.array(kerr.invariants("ks", xk, uk, A, M)[i])
                                                          - (E, Lz, Q)[i]))) for i in range(3)])
        out["orbits"][name] = rec
        print(f"[{name}] E={E!r} Lz={Lz!r} Q={Q!r} t_end={o['t_end']} checks={len(ts)} "
              f"DOP853 dev ks {rec['check']['dop853_ks_max_dev_x']:.1e}/"
              f"{rec['check']['dop853_ks_max_dev_u']:.1e} cks {rec['check']['dop853_cks_max_dev_x']:.1e}/"
              f"{rec['check']['dop853_cks_max_dev_u']:.1e}  ({time.time() - T0:.0f} s)", flush=True)
    out["runtime_s"] = time.time() - T0
    save_json(SCHW_REF_JSON, out)
    print("wrote", SCHW_REF_JSON)


if __name__ == "__main__":
    main()
