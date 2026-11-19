#!/usr/bin/env python3
"""Newtonian collapse of a cold homogeneous spheroid: the semi-analytic reference for
the predictions of the oblate-collapse test (tracks/core/JOURNAL-oblate.md).

A homogeneous spheroid of mass M with semi-axes a (x, y) and b (z), at rest, has the
interior potential Phi = -(3M/4) [I - R^2 J_a - z^2 J_b] (python/nrpic/spheroid.py, with
the mass M instead of M/2), so every particle obeys a linear force law and the spheroid
stays homogeneous (Lin, Mestel and Shu 1965 [BACKGROUND]):

    d^2 a/dt^2 = -(3M/2) J_a(a, |b|) a,     d^2 b/dt^2 = -(3M/2) J_b(a, |b|) b.

For collisionless matter the solution continues through b = 0 (oblate: every particle
crosses the equatorial plane at the same instant, the "pancake") with b -> -b: the
mirror image is again a homogeneous spheroid with semi-axis |b|, and the force on b is
finite there, J_b b -> 2 sign(b)/a^2. In the same way a prolate spheroid passes a = 0
(the spindle; J_a a diverges logarithmically there, the velocity stays finite).

    python3 newton_spheroid.py [--out DIR]

prints the event times for the oblate case e = 0.9, a = 10 M and the prolate case
e = 0.9, b = 10 M (the calibration against the existing run), and writes
newton_spheroid.json and figs/newton_spheroid.{png,pdf}.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import spheroid as sph  # noqa: E402


def JaJb(a, b):
    """J_a, J_b at the surface (lam = 0) of the spheroid with semi-axes a, b > 0."""
    if a >= b:
        _, Ja, Jb = sph._IJ_oblate(np.array([b]), math.sqrt(a * a - b * b))
    else:
        _, Ja, Jb = sph._IJ(np.array([b]), math.sqrt(b * b - a * a))
    return float(Ja[0]), float(Jb[0])


def rhs(t, y, M):
    a, b, va, vb = y
    aa, bb = max(abs(a), 1e-9), max(abs(b), 1e-9)
    Ja, Jb = JaJb(aa, bb)
    return [va, vb, -1.5 * M * Ja * a, -1.5 * M * Jb * b]


def evolve(a0, b0, M=1.0, tmax=80.0, amin=0.02):
    """a(t), b(t) from rest; stops when the equatorial semi-axis falls below amin
    (oblate: the end of the radial collapse) or at tmax."""
    stop = lambda t, y, M: abs(y[0]) - amin
    stop.terminal = True
    zb = lambda t, y, M: y[1]
    za = lambda t, y, M: y[0]
    sol = solve_ivp(rhs, (0.0, tmax), [a0, b0, 0.0, 0.0], args=(M,), method="DOP853",
                    rtol=1e-10, atol=1e-12, max_step=0.02, events=[stop, zb, za],
                    dense_output=False)
    return sol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", HERE))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    e = 0.9
    q = math.sqrt(1 - e * e)
    res = {}
    # oblate, a = 10, b = 4.359; prolate, a = 4.359, b = 10 (stopped at the spindle)
    so = evolve(10.0, 10.0 * q, amin=0.02)
    sp = evolve(10.0 * q, 10.0, amin=0.02)
    tff = lambda R, M=1.0: 0.5 * math.pi * math.sqrt(R ** 3 / (2.0 * M))
    res["oblate"] = dict(a0=10.0, b0=10.0 * q,
                         t_pancakes=[float(t) for t in so.t_events[1]],
                         a_at_pancakes=[float(y[0]) for y in so.y_events[1]],
                         va_at_pancakes=[float(y[2]) for y in so.y_events[1]],
                         vb_at_pancakes=[float(y[3]) for y in so.y_events[1]],
                         t_end=float(so.t[-1]), a_end=float(so.y[0, -1]),
                         b_end=float(so.y[1, -1]))
    res["prolate"] = dict(a0=10.0 * q, b0=10.0, t_spindle=float(sp.t[-1]),
                          b_at_spindle=float(sp.y[1, -1]), vb_at_spindle=float(sp.y[3, -1]))
    res["free_fall_sphere"] = dict(R10=tff(10.0), note="(pi/2) sqrt(R^3/(2M))")
    # times at which the oblate equatorial semi-axis passes given values
    for val in (5.0, 3.0, 2.0, 1.0, 0.5):
        k = np.argmax(np.abs(so.y[0]) < val)
        res["oblate"][f"t_a_{val:g}"] = float(so.t[k])
        res["oblate"][f"b_at_a_{val:g}"] = float(abs(so.y[1, k]))
    for val in (2.0, 1.0, 0.5):
        k = np.argmax(np.abs(sp.y[0]) < val)
        res["prolate"][f"t_a_{val:g}"] = float(sp.t[k])
        res["prolate"][f"b_at_a_{val:g}"] = float(abs(sp.y[1, k]))
    with open(os.path.join(a.out, "newton_spheroid.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    np.savetxt(os.path.join(a.out, "newton_oblate_track.txt"),
               np.column_stack([so.t, so.y[0], so.y[1], so.y[2], so.y[3]]),
               header="t a b da/dt db/dt  (Newtonian homogeneous oblate spheroid, M = 1)")

    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.90, wspace=0.05)
    for axx, s, ttl in ((ax[0], so, "oblate, $a_0=10M$, $e=0.9$"),
                        (ax[1], sp, "prolate, $b_0=10M$, $e=0.9$")):
        axx.plot(s.t, np.abs(s.y[0]), color=fs.PAL["blue"], label="equatorial semi-axis $a$")
        axx.plot(s.t, np.abs(s.y[1]), color=fs.PAL["red"], label="polar semi-axis $|b|$")
        axx.set_xlabel("$t/M$", labelpad=-2)
        axx.set_title(ttl)
        axx.set_xlim(0, 45)
        axx.set_ylim(0, 10.5)
    for t in so.t_events[1]:
        ax[0].axvline(t, **fs.MASK_LINE)
    ax[0].set_ylabel("semi-axis [$M$]")
    ax[0].legend(fontsize=8)
    out = os.path.join(HERE, "figs", "newton_spheroid")
    fs.save(fig, out)
    print("figure", out + ".png")


if __name__ == "__main__":
    main()
