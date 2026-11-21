#!/usr/bin/env python3
"""Reference for the lapse in a homogeneous dust region (centre of the expanding ball).

With zero shift and a lapse that is uniform in the region the 1+log condition with the
relaxation of the excess lapse (athenak/src/z4c/z4c_gauge_ext.hpp) is the ordinary
differential equation

    d ln(alpha)/dt = -2 K(tau) - max(ln(alpha/alpha_0), 0)/T,     d tau/dt = alpha,

with K = -3 (da/dtau)/a of the dust (python/nrpic/expanding_ball.py).  T = infinity is
the plain 1+log condition, alpha = 1 + 6 ln a.  The equation holds at the centre until a
signal from the surface arrives there.

    lapse_ref.py [--Rb 10] [--e0 0] [--RE 10] [--T 1 2 ...] [--tmax 10]

prints t, tau, a, alpha for each T (0 means no relaxation).
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import expanding_ball as eb  # noqa: E402


def central_lapse(ball, T, tmax, dt=1.0e-3, alpha0=1.0, lapse_start=1.0):
    """Arrays t, tau, a, alpha of the centre; T <= 0 switches the relaxation off."""
    def K(tau):
        h = 1.0e-5
        return -3.0 * (math.log(float(ball.scale_factor(tau + h)))
                       - math.log(float(ball.scale_factor(tau - h)))) / (2.0 * h)

    def rhs(y):
        la, tau = y
        leak = max(la - math.log(alpha0), 0.0) / T if T > 0.0 else 0.0
        return np.array([-2.0 * K(tau) - leak, math.exp(la)])

    n = int(round(tmax / dt))
    y = np.array([math.log(lapse_start), 0.0])
    out = np.zeros((n + 1, 4))
    out[0] = (0.0, 0.0, 1.0, lapse_start)
    for i in range(n):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = y + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        out[i + 1] = ((i + 1) * dt, y[1], float(ball.scale_factor(y[1])), math.exp(y[0]))
    return out.T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Rb", type=float, default=10.0)
    ap.add_argument("--e0", type=float, default=0.0)
    ap.add_argument("--RE", type=float, default=None)
    ap.add_argument("--T", type=float, nargs="+", default=[0.0, 1.0, 2.0])
    ap.add_argument("--tmax", type=float, default=10.0)
    ap.add_argument("--every", type=float, default=1.0)
    a = ap.parse_args()
    ball = eb.Ball(M=1.0, Rb=a.Rb, e0=a.e0, RE=a.RE)
    for T in a.T:
        t, tau, sc, al = central_lapse(ball, T, a.tmax)
        print(f"# T = {T:g}   (columns t, tau, a, alpha)")
        step = max(1, int(round(a.every / (t[1] - t[0]))))
        for i in range(0, len(t), step):
            print(f"{t[i]:8.3f} {tau[i]:10.5f} {sc[i]:9.5f} {al[i]:9.5f}")


if __name__ == "__main__":
    main()
