#!/usr/bin/env python3
"""Verifier's own expected collision rate of a D2 run at t = 0 (V4.c).

From the particles at t = 0 (positions and covariant momenta u_i of cc.traj.bin, the metric at
each particle of cc.trajmet.bin, masses of the snapshot cc.part.00000.bin; every particle is
tracked in these N = 1e5 runs) and the deck (coll_sigma, coll_cell_factor f, static refined
regions), the expected number of collisions per unit coordinate time is

    Gamma = sum over collision cells c of sigma_m M alpha_c / (sqrt(gamma_c) V_c) sum_{i<j in c} v_Mol,ij

(equation 1 of coord/INTERFACES/collisions.md summed over the N/2 random pairs the operator
tests, whose expectation is the sum over all pairs; equal masses M). v_Mol,ij =
sqrt(g_rel^2 - 1)/(W_i W_j), g_rel = W_i W_j - gamma^kl u_ik u_jl, W = sqrt(1 + gamma^kl u_k u_l),
with the cell metric taken as the mean of its particles' metric. Collision cells: f mesh cells
of the level of the particle's MeshBlock; level 7 (dx = M/8) inside |x|_inf < 4 M, level 6
(M/4) inside 8 M (the refined regions of the deck rounded out to MeshBlocks of 16 cells), level
5 (M/2) assumed beyond; the share of Gamma from outside 8 M is printed so that this assumption
can be judged.

Compared with the code's own expectation sum_P (column 6 of cc.coll.hst) summed over the first
steps, and with the collisions counted there.

Tests first: the Moller speed against the closed form sqrt(|v1 - v2|^2 - |v1 x v2|^2) in flat
space; the per-cell pair sum against a brute-force double loop.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def inv3(g):
    """g: (n, 6) xx, xy, xz, yy, yz, zz -> inverse (n, 3, 3) and sqrt(det)."""
    G = np.empty((len(g), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2] = g[:, 0], g[:, 1], g[:, 2]
    G[:, 1, 0], G[:, 1, 1], G[:, 1, 2] = g[:, 1], g[:, 3], g[:, 4]
    G[:, 2, 0], G[:, 2, 1], G[:, 2, 2] = g[:, 2], g[:, 4], g[:, 5]
    return np.linalg.inv(G), np.sqrt(np.linalg.det(G))


def vmol_pairs(u, ginv):
    """u: (n, 3) covariant; ginv (3, 3) common metric. Returns the sum over i<j of v_Mol."""
    gu = u @ ginv
    W = np.sqrt(1.0 + np.einsum("ik,ik->i", gu, u))
    dot = gu @ u.T
    grel = np.outer(W, W) - dot
    v = np.sqrt(np.clip(grel**2 - 1.0, 0.0, None)) / np.outer(W, W)
    iu = np.triu_indices(len(u), 1)
    return v[iu].sum(), len(iu[0])


def test_vmol(rng):
    n = 50
    vel = rng.uniform(-0.6, 0.6, (n, 3))
    vel = vel[np.linalg.norm(vel, axis=1) < 0.95]
    W = 1 / np.sqrt(1 - (vel**2).sum(1))
    u = vel * W[:, None]
    s, _ = vmol_pairs(u, np.eye(3))
    ref = 0.0
    for i in range(len(vel)):
        for j in range(i + 1, len(vel)):
            d = vel[i] - vel[j]
            c = np.cross(vel[i], vel[j])
            ref += np.sqrt(d @ d - c @ c)
    return abs(s / ref - 1)


REGIONS = [(6, 7.9), (7, 3.9)]  # (level, half-width) of the deck; replaced per run in main()


def level_of(x):
    """Level of the MeshBlock holding x: the deepest refined region (rounded out to MeshBlocks
    of 16 cells of that level, root dx = 16 M) that contains x; level 5 beyond (assumed)."""
    r = np.max(np.abs(x), axis=1)
    lev = np.full(len(x), 5)
    for L, w in sorted(REGIONS):
        blk = 16 * 16.0 / 2.0**L
        wr = np.ceil(w / blk - 1e-12) * blk
        lev = np.where(r < wr, L, lev)
    return lev


def expected_rate(x, u, alpha, g6, m, sigma, f):
    lev = level_of(x)
    cell = 32.0 / 2.0**lev * f / 2.0  # f mesh cells of dx = 16/2^lev
    key = np.floor(x / cell[:, None]).astype(np.int64)
    rate = 0.0
    rate_out = 0.0
    npairs = 0
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0], lev))
    ks = np.column_stack([lev, key])[order]
    brk = np.where(np.any(np.diff(ks, axis=0) != 0, axis=1))[0] + 1
    groups = np.split(order, brk)
    occ = []
    for gi in groups:
        if len(gi) < 2:
            occ.append(len(gi))
            continue
        occ.append(len(gi))
        ginv, sdet = inv3(g6[gi].mean(0)[None, :])
        sv, npr = vmol_pairs(u[gi], ginv[0])
        V = sdet[0] * cell[gi[0]]**3
        r = sigma * m[gi].max() * alpha[gi].mean() / V * sv
        rate += r
        npairs += npr
        if lev[gi[0]] <= 5:
            rate_out += r
    return rate, rate_out, npairs, np.array(occ)


def test_cells(rng):
    x = rng.uniform(-1, 1, (300, 3))
    u = rng.normal(0, 0.2, (300, 3))
    g6 = np.tile([1.2, 0, 0, 1.2, 0, 1.2], (300, 1))
    a = np.full(300, 0.8)
    m = np.full(300, 1e-5)
    r, _, _, _ = expected_rate(x, u, a, g6, m, 2.0, 2)
    # brute force: same cells (level 7, cell M/4)
    key = np.floor(x / 0.25).astype(int)
    tot = 0.0
    for i in range(300):
        for j in range(i + 1, 300):
            if np.all(key[i] == key[j]):
                gi = np.linalg.inv(np.eye(3) * 1.2)
                Wi = np.sqrt(1 + u[i] @ gi @ u[i])
                Wj = np.sqrt(1 + u[j] @ gi @ u[j])
                gr = Wi * Wj - u[i] @ gi @ u[j]
                tot += np.sqrt(gr**2 - 1) / (Wi * Wj)
    ref = 2.0 * 1e-5 * 0.8 / (1.2**1.5 * 0.25**3) * tot
    return abs(r / ref - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("runs", nargs="+", help="name=run_id")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(20261127)
    res = {"test_vmol_rel_err": float(test_vmol(rng)), "test_cells_rel_err": float(test_cells(rng))}
    print(res)
    if res["test_vmol_rel_err"] > 1e-12 or res["test_cells_rel_err"] > 1e-12:
        json.dump(res, open(os.path.join(a.out, "collrate.json"), "w"), indent=1)
        sys.exit(1)
    for spec in a.runs:
        name, rid = spec.split("=")
        d = os.path.join(SCR, rid)
        deck = open(os.path.join(d, "chain", "input.athinput")).read()
        sigma = float(re.search(r"^coll_sigma\s*=\s*([0-9.eE+-]+)", deck, re.M).group(1))
        f = int(re.search(r"^coll_cell_factor\s*=\s*(\d+)", deck, re.M).group(1))
        regions = re.findall(r"<refined_region\d>\s*\nlevel\s*=\s*(\d+).*?\nx1min\s*=\s*([-0-9.]+)", deck, re.S)
        global REGIONS
        REGIONS = [(int(L), abs(float(w))) for L, w in regions]
        with open(os.path.join(d, "cc.part.00000.bin"), "rb") as fh:
            assert fh.read(8) == b"NRPSNAP1"
            t0, N, _cyc = np.frombuffer(fh.read(24), dtype=[("t", "<f8"), ("n", "<i8"), ("c", "<i8")])[0]
            rec = np.frombuffer(fh.read(56 * N), dtype="<f8").reshape(N, 7)
            tags = np.frombuffer(fh.read(4 * N), dtype="<i4")
        tr = np.fromfile(os.path.join(d, "cc.traj.bin"), dtype="<f8", count=8 * N).reshape(N, 8)
        tm = np.fromfile(os.path.join(d, "cc.trajmet.bin"), dtype="<f8", count=17 * N).reshape(N, 17)
        assert np.all(tr[:, 0] == 0) and np.all(tm[:, 0] == 0)
        assert np.all(tr[:, 1] == tm[:, 1])
        # masses by tag from the snapshot
        mt = np.empty(N)
        mt[tags] = rec[:, 6]
        tg = tr[:, 1].astype(int)
        x, u = tr[:, 2:5], tr[:, 5:8]
        # positions of the snapshot and of the trajectory file agree at t = 0
        xs = np.empty((N, 3))
        xs[tags] = rec[:, 0:3]
        dx_max = float(np.abs(xs[tg] - x).max())
        rate, rate_out, npairs, occ = expected_rate(x, u, tm[:, 2], tm[:, 6:12], mt[tg], sigma, f)
        c = np.array([[float(v) for v in ln.split()] for ln in open(os.path.join(d, "cc.coll.hst"))
                      if ln.strip() and not ln.startswith("#")][:400])
        dt = np.diff(np.concatenate([[0.0], c[:, 0]]))
        out = {"sigma": sigma, "f": f, "regions": regions, "N": int(N), "x_snapshot_vs_traj": dx_max,
               "expected_per_M": float(rate), "share_outside_8M": float(rate_out / rate),
               "pairs_in_cells": int(npairs), "max_occupation": int(occ.max())}
        for nsteps in (1, 8, 32, 320):
            out[f"code_sumP_per_M_first{nsteps}"] = float(c[:nsteps, 5].sum() / dt[:nsteps].sum())
            out[f"code_ncoll_per_M_first{nsteps}"] = float(c[:nsteps, 6].sum() / dt[:nsteps].sum())
        out["ratio_code_sumP_first32_to_verifier"] = out["code_sumP_per_M_first32"] / rate
        res[name] = out
        print(name, json.dumps(out))
    json.dump(res, open(os.path.join(a.out, "collrate.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
