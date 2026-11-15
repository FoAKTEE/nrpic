"""Replay of one collision step from the "before" part of a collision dump (TESTS.md T0b).

Written from the text of coord/INTERFACES/collisions.md (sections 3.1-3.7, 4, 5) and the
track's specification, with the track's kinematics oracle
(collide/REFERENCES/kinematics.py) and the random-number twin python/nrpic/rng.py; it does
not use core's Python twin python/nrpic/collide.py. Equal masses, constant cross-section
and the Cholesky or symmetric triad of a constant-per-cell metric are supported (the
box tests); `nanbu` and `cutoff` are refused.

replay(dump, mesh, key_cycle) -> dict with the replayed cell indices, n_sub, momenta,
updates per particle, and the totals n_tested, n_coll, sum_P, sum_W, max_P.
mesh = dict(xmin=(3,), xmax=(3,), n=(3,) cells per direction on the root level).
"""
import math

import numpy as np

import boxlib as bl  # noqa: F401  (paths)
import kinematics as kin
from nrpic import rng


def left_edge(i, n, xmin, xmax):
    """Face positions as the mesh computes block edges (coordinates/cell_locations.hpp)."""
    x = np.asarray(i, dtype=float) / float(n)
    return (x * xmax - x * xmin) - (0.5 * xmax - 0.5 * xmin) + (0.5 * xmin + 0.5 * xmax)


def cell_index(x, xmin, xmax, n):
    """Global cell index on the root level: floor of the fraction, corrected by one so
    that face(I) <= x < face(I + 1). Positions are wrapped into the periodic mesh."""
    L = xmax - xmin
    xw = xmin + np.mod(x - xmin, L)
    I = np.floor((xw - xmin) / L * n).astype(np.int64)
    I = np.clip(I, 0, n - 1)
    lo = left_edge(I, n, xmin, xmax)
    hi = left_edge(I + 1, n, xmin, xmax)
    I = np.where(xw < lo, I - 1, np.where(xw >= hi, I + 1, I))
    return np.mod(I, n)


def triad(gam6, kind):
    """S with S S^T = gamma (kind 1: Cholesky lower triangular; 0: symmetric root)."""
    g = np.array([[gam6[0], gam6[1], gam6[2]], [gam6[1], gam6[3], gam6[4]],
                  [gam6[2], gam6[4], gam6[5]]])
    if np.array_equal(g, np.eye(3)):
        return None
    if kind == 1:
        return np.linalg.cholesky(g)
    w, v = np.linalg.eigh(g)
    return (v * np.sqrt(w)) @ v.T


def replay(d, mesh, key_cycle):
    if d["weights"] != 0 or d["model"] != 0:
        raise ValueError("replay supports coll_weights = equal and the constant model only")
    n = d["n"]
    f = d["f"]
    seed = d["seed"]
    s_pair = rng.stream(rng.STREAM_COLLISIONS, 0)
    s_acc = rng.stream(rng.STREAM_COLLISIONS, 1)
    s_dir = rng.stream(rng.STREAM_COLLISIONS, 2)
    idx = np.stack([cell_index(d["x"][:, k], mesh["xmin"][k], mesh["xmax"][k], mesh["n"][k])
                    for k in range(3)], axis=1)
    cidx = idx // f
    u = d["u0"].copy()
    nupd = np.zeros(n, dtype=np.int64)
    nsub_r = np.zeros(n, dtype=np.int64)
    tot = dict(n_tested=0, n_coll=0, sum_P=0.0, sum_W=0.0, max_P=0.0, n_trunc=0,
               n_cells=0, cells_odd=0)
    sumP_terms, sumW_terms = [], []
    key = cidx[:, 0] + (1 << 21) * (cidx[:, 1] + (1 << 21) * cidx[:, 2])
    order = np.argsort(key, kind="stable")
    bounds = np.flatnonzero(np.diff(key[order])) + 1
    groups = np.split(order, bounds)
    for g in groups:
        N = g.size
        if N < 2:
            nsub_r[g] = 0
            continue
        tot["n_cells"] += 1
        alpha = d["alpha"][g[0]]
        V = d["vol"][g[0]]
        S = triad(d["gam"][g[0]], d["triad"])
        uh = u[g] if S is None else np.linalg.solve(S, u[g].T).T
        M = d["m"][g]
        Mmax = M.max()
        # sub-steps (measured): two largest speeds of the cell in its frame
        Wc = np.sqrt(1.0 + np.sum(uh * uh, 1))
        v = np.sqrt(np.sum(uh * uh, 1)) / Wc
        if d["subcycle"] == 0:
            vs = np.sort(v)
            vb = min(vs[-1] + vs[-2], 2.0)
        else:
            vb = 2.0
        Pb = (N - 1) * d["sigma"] * Mmax * vb * alpha * d["dt"] / V
        nsub = int(min(max(math.ceil(Pb / d["pmax"]), 1), d["nsub_max"]))
        nsub_r[g] = nsub
        tags = d["tag"][g].astype(np.uint64)
        for s in range(nsub):
            w = rng.bits(seed, s_pair, tags, key_cycle, s)
            o = np.lexsort((tags, w))          # sort by (word, tag)
            pairs = []
            if N % 2 == 1:
                tot["cells_odd"] += 1
                a3 = o[:3]
                pairs += [(a3[0], a3[1], 0.5), (a3[1], a3[2], 0.5), (a3[2], a3[0], 0.5)]
                rest = o[3:]
            else:
                rest = o
            pairs += [(rest[2 * k], rest[2 * k + 1], 1.0) for k in range(rest.size // 2)]
            for (i, j, h) in pairs:
                ti, tj = int(tags[i]), int(tags[j])
                if ti > tj:
                    i, j, ti, tj = j, i, tj, ti
                ua, ub = uh[i], uh[j]
                g1 = float(kin.gamma_rel_m1(ua, ub))
                Wa = math.sqrt(1.0 + float(ua @ ua))
                Wb = math.sqrt(1.0 + float(ub @ ub))
                vm = math.sqrt(g1 * (g1 + 2.0)) / (Wa * Wb)
                wgt = (N - 1) * d["sigma"] * max(M[i], M[j]) * alpha * d["dt"] / (nsub * V) * h
                P = wgt * vm
                tot["n_tested"] += 1
                sumP_terms.append(P)
                sumW_terms.append(wgt)
                tot["max_P"] = max(tot["max_P"], P)
                if P > 1.0:
                    tot["n_trunc"] += 1
                U = float(rng.uniform4(seed, s_acc, ti, key_cycle, s, entity_hi=tj)[0, 0])
                if U < P:
                    nh = rng.direction(seed, s_dir, ti, key_cycle, s, entity_hi=tj)[0]
                    a2, b2 = kin.scatter(ua, ub, 1.0, 1.0, nh)
                    uh[i], uh[j] = a2, b2
                    nupd[g[i]] += 1
                    nupd[g[j]] += 1
                    tot["n_coll"] += 1
        u[g] = uh if S is None else (S @ uh.T).T
    tot["sum_P"] = math.fsum(sumP_terms)
    tot["sum_W"] = math.fsum(sumW_terms)
    return dict(idx=idx, cidx=cidx, nsub=nsub_r, u=u, nupd=nupd, tot=tot)
