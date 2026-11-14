"""Worst-case error of the deposit of a uniform density that is sampled by a compressed
lattice, for B-spline clouds of degree one to three, in one dimension (working paper,
sampling-error figure). The lattice q = (i + o) h / n_pc is displaced by
c cos(k q) / k, the masses carry the exact Jacobian, and the error is the largest
departure of the deposit from one over the mesh and over forty lattice offsets o."""
import os

import numpy as np

from common import DATA


def deposit(x, m, n, L, degree):
    h = L/n
    xi = x/h - 0.5
    out = np.zeros(n)
    if degree == 1:
        i0 = np.floor(xi).astype(int)
        s = xi - i0
        w = [1.0 - s, s]
    elif degree == 2:
        i0 = np.floor(xi + 0.5).astype(int)
        d = xi - i0
        w = [0.5*(0.5 - d)**2, 0.75 - d*d, 0.5*(0.5 + d)**2]
        i0 -= 1
    else:
        i0 = np.floor(xi).astype(int)
        s = xi - i0
        w = [(1 - s)**3/6, (3*s**3 - 6*s**2 + 4)/6, (-3*s**3 + 3*s**2 + 3*s + 1)/6, s**3/6]
        i0 -= 1
    for a, ww in enumerate(w):
        np.add.at(out, (i0 + a) % n, m*ww)
    return out/h


def binomial(f, npass, compensate):
    g = f
    for _ in range(npass):
        g = 0.5*g + 0.25*(np.roll(g, 1) + np.roll(g, -1))
    if compensate and npass:
        c = 0.25*npass
        g = (1 + 2*c)*g - c*(np.roll(g, 1) + np.roll(g, -1))
    return g


n, L = 64, 4.0
h, k = L/n, 2*np.pi/L
cs = np.geomspace(0.01, 0.5, 24)
out = {"c": cs}
for npc in (1, 2, 4):
    for degree in (1, 2, 3):
        raw, fil = [], []
        for c in cs:
            w0 = w1 = 0.0
            for off in np.linspace(0, 1, 40, endpoint=False):
                q = (np.arange(n*npc) + off)*h/npc
                x = np.mod(q + c*np.cos(k*q)/k, L)
                m = (1 - c*np.sin(k*q))*h/npc
                f = deposit(x, m, n, L, degree)
                w0 = max(w0, np.abs(f - 1).max())
                w1 = max(w1, np.abs(binomial(f, 2, True) - 1).max())
            raw.append(w0)
            fil.append(w1)
        out[f"raw_p{degree}_n{npc}"] = np.array(raw)
        out[f"fil_p{degree}_n{npc}"] = np.array(fil)
np.savez(os.path.join(DATA, "shape_error.npz"), **out)
print("wrote", os.path.join(DATA, "shape_error.npz"))
