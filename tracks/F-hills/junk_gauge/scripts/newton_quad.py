#!/usr/bin/env python3
"""J4 reference: Newtonian point-mass track of P1's three holes (bare masses and the momenta of
the input, tracks/F-hills/nr_first/inputs/p1_q4.athinput) and its quadrupole luminosity
    L(t) = (1/5) sum_jk (d^3 Q_jk / dt^3)^2,  Q_jk = sum_a m_a (x_j x_k - delta_jk r^2 / 3)
[BACKGROUND: the quadrupole formula, G = c = 1]; the third derivative from the exact jerk of the
Newtonian accelerations. An ordinary differential equation solved with scipy (DOP853), a
semi-analytic reference outside AthenaK (decision 0010). Gives the time profile of the physical
emission (the binary's own and the passage burst) against which the junk window of P1 is cut.
Writes newton_quad.json and newton_quad_track.npz.
Usage: newton_quad.py <out | -> [<athinput>] [--tend=280]
"""
import json
import os
import re
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def read_input(path):
    txt = open(path).read()
    # the block header on a line of its own (the file's comments also name "<problem>")
    blk = re.split(r"^<problem>\s*$", txt, flags=re.M)[1]
    blk = re.split(r"^<\w+>\s*$", blk, flags=re.M)[0]
    val = dict(re.findall(r"^\s*(\w+)\s*=\s*([-+0-9.eE]+)", blk, re.M))
    n = int(val["ncomp"])
    m = np.array([float(val[f"comp{i}_mass"]) for i in range(n)])
    x = np.array([[float(val[f"comp{i}_x{j}"]) for j in (1, 2, 3)] for i in range(n)])
    p = np.array([[float(val[f"comp{i}_p{j}"]) for j in (1, 2, 3)] for i in range(n)])
    return m, x, p / m[:, None]


def acc_jerk(m, x, v):
    n = len(m)
    a = np.zeros_like(x)
    j = np.zeros_like(x)
    for i in range(n):
        for k in range(n):
            if i == k:
                continue
            r = x[k] - x[i]
            w = v[k] - v[i]
            d = np.linalg.norm(r)
            a[i] += m[k] * r / d ** 3
            j[i] += m[k] * (w / d ** 3 - 3 * r * np.dot(r, w) / d ** 5)
    return a, j


def rhs(t, y, m):
    n = len(m)
    x = y[:3 * n].reshape(n, 3)
    v = y[3 * n:].reshape(n, 3)
    a, _ = acc_jerk(m, x, v)
    return np.concatenate([v.ravel(), a.ravel()])


def lum(m, x, v):
    a, j = acc_jerk(m, x, v)
    Q3 = np.zeros((3, 3))
    for i in range(len(m)):
        Q3 += m[i] * (np.outer(j[i], x[i]) + 3 * np.outer(a[i], v[i]) + 3 * np.outer(v[i], a[i])
                      + np.outer(x[i], j[i]))
    Q3 -= np.eye(3) * np.trace(Q3) / 3
    return float(np.sum(Q3 * Q3) / 5)


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    inp = os.path.join(WT, "tracks/F-hills/nr_first/inputs/p1_q4.athinput")
    tend = 280.0
    for a in sys.argv[2:]:
        if a.startswith("--tend="):
            tend = float(a[7:])
        else:
            inp = a
    m, x0, v0 = read_input(inp)
    n = len(m)
    y0 = np.concatenate([x0.ravel(), v0.ravel()])
    t = np.arange(0, tend + 1e-9, 0.25)
    sol = solve_ivp(rhs, (0, tend), y0, args=(m,), method="DOP853", rtol=1e-11, atol=1e-12,
                    t_eval=t)
    X = sol.y[:3 * n].T.reshape(-1, n, 3)
    V = sol.y[3 * n:].T.reshape(-1, n, 3)
    L = np.array([lum(m, X[i], V[i]) for i in range(len(t))])
    E = np.concatenate([[0], np.cumsum(0.5 * (L[1:] + L[:-1]) * np.diff(t))])
    # energy check of the integration
    def energy(xx, vv):
        ke = 0.5 * np.sum(m[:, None] * vv ** 2)
        pe = sum(-m[i] * m[k] / np.linalg.norm(xx[i] - xx[k]) for i in range(n) for k in range(i + 1, n))
        return ke + pe
    En = np.array([energy(X[i], V[i]) for i in range(0, len(t), 40)])
    iM = int(np.argmax(m))
    mem = [i for i in range(n) if i != iM]
    r12 = np.linalg.norm(X[:, mem[0]] - X[:, mem[1]], axis=1)
    xc = (m[mem[0]] * X[:, mem[0]] + m[mem[1]] * X[:, mem[1]]) / (m[mem[0]] + m[mem[1]])
    rcm = np.linalg.norm(xc - X[:, iM], axis=1)
    L0 = float(np.median(L[t <= 20]))
    i2 = np.where(L > 2 * L0)[0]
    i10 = np.where(L > 10 * L0)[0]
    res = dict(input=os.path.relpath(inp, WT), masses=m.tolist(), success=bool(sol.success),
               energy_rel_drift=float(np.max(np.abs(En - En[0])) / abs(En[0])),
               L_binary_t0_20_median=L0,
               t_L_above_2x=float(t[i2[0]]) if len(i2) else None,
               t_L_above_10x=float(t[i10[0]]) if len(i10) else None,
               t_L_max=float(t[np.argmax(L)]), L_max=float(L.max()),
               t_cm_pericentre=float(t[np.argmin(rcm)]), r_cm_min=float(rcm.min()),
               E_quad_0_to={str(tt): float(np.interp(tt, t, E)) for tt in (40, 60, 80, 100, 120, 150, 200, 280)},
               max_dist_from_origin_t0=float(np.max(np.linalg.norm(x0, axis=1))),
               r12_t0=float(r12[0]))
    a_b = r12[0]
    mb = m[mem[0]] + m[mem[1]]
    mu = m[mem[0]] * m[mem[1]] / mb
    Om = np.sqrt(mb / a_b ** 3)
    res["L_circular_binary_formula"] = float(32 / 5 * mu ** 2 * a_b ** 4 * Om ** 6)
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(out, "newton_quad.json"), "w"), indent=1)
    np.savez(os.path.join(out, "newton_quad_track.npz"), t=t, X=X, V=V, L=L, E=E, rcm=rcm, r12=r12)


if __name__ == "__main__":
    main()
