"""Newtonian N-body reference of the verifier (G = 1), written for this package.

State: masses m[i], positions x[i] (3-vectors), velocities v[i]. Integrator: scipy's DOP853
with rtol = atol = 1e-12 (tested in vtest.py on a Kepler ellipse and on the energy and angular
momentum of a three-body run). The initial data of a deck are read from its <problem> block:
comp<c>_mass, comp<c>_x1..3, comp<c>_p1..3 (Bowen-York momenta), so v = p / m with the bare mass.
"""
import re

import numpy as np
from scipy.integrate import solve_ivp


def deck_state(path):
    txt = open(path).read()
    vals = {}
    for k, v in re.findall(r"^\s*(comp\d+_(?:mass|x[123]|p[123]))\s*=\s*([-+0-9.eE]+)", txt, re.M):
        vals[k] = float(v)
    n = max(int(k.split("_")[0][4:]) for k in vals) + 1
    m = np.array([vals[f"comp{c}_mass"] for c in range(n)])
    x = np.array([[vals[f"comp{c}_x{d}"] for d in (1, 2, 3)] for c in range(n)])
    p = np.array([[vals[f"comp{c}_p{d}"] for d in (1, 2, 3)] for c in range(n)])
    return m, x, p / m[:, None]


def rhs(t, y, m):
    n = len(m)
    x = y[:3 * n].reshape(n, 3)
    v = y[3 * n:].reshape(n, 3)
    a = np.zeros_like(x)
    for i in range(n):
        for j in range(n):
            if i != j:
                d = x[j] - x[i]
                a[i] += m[j] * d / np.linalg.norm(d) ** 3
    return np.concatenate([v.ravel(), a.ravel()])


def integrate(m, x0, v0, t_end, dt_out=0.01, rtol=1e-12, atol=1e-12):
    y0 = np.concatenate([np.asarray(x0, float).ravel(), np.asarray(v0, float).ravel()])
    t_eval = np.arange(0.0, t_end + 0.5 * dt_out, dt_out)
    t_eval = t_eval[t_eval <= t_end]
    sol = solve_ivp(rhs, (0.0, t_end), y0, method="DOP853", rtol=rtol, atol=atol,
                    t_eval=t_eval, args=(np.asarray(m, float),), dense_output=True)
    n = len(m)
    X = sol.y[:3 * n].T.reshape(-1, n, 3)
    V = sol.y[3 * n:].T.reshape(-1, n, 3)
    return sol.t, X, V, sol


def energy(m, X, V):
    n = len(m)
    ke = 0.5 * (m[None, :, None] * V ** 2).sum(axis=(1, 2))
    pe = np.zeros(X.shape[0])
    for i in range(n):
        for j in range(i + 1, n):
            pe -= m[i] * m[j] / np.linalg.norm(X[:, i] - X[:, j], axis=1)
    return ke + pe


def angmom(m, X, V):
    return (m[None, :, None] * np.cross(X, V)).sum(axis=1)


def two_body_energy(mi, mj, xi, xj, vi, vj):
    """Energy of the pair (i, j) in its own centre-of-mass frame: mu |dv|^2 / 2 - mi mj / r."""
    mu = mi * mj / (mi + mj)
    dv = vi - vj
    r = np.linalg.norm(xi - xj, axis=-1)
    return 0.5 * mu * (dv ** 2).sum(-1) - mi * mj / r
