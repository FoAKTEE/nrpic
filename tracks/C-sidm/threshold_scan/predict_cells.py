#!/usr/bin/env python3
"""How the energy defect of the collision step and the occupation of the collision cells
depend on the cell size, for the King threshold model (CC1) at N = 10^5: uniform cubic
cells of side h = M/8, M/4, M/2, M (the choices of coll_cell_factor 1, 2, 4 on the M/4 mesh,
and one finer), all centred on the static metric of the equilibrium as in predict.py.
Per collision: the change of sum M W with W at each particle's metric and of the Killing
energy; expected collisions per step per unit sigma_m; mean and central occupation. Cells
with more than NMAX particles contribute a random subset of their pairs, reweighted.

    python3 predict_cells.py [--out DIR] [--K 8]
"""
import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
from predict import scatter, vmol  # noqa: E402

NMAX = 64
SIZES = (0.125, 0.25, 0.5, 1.0)


def run(h, md, K, rng):
    x, u, m = md["x"], md["u"], md["m"]
    M = float(m[0])
    r = np.linalg.norm(x, axis=1)
    psi_p, alp_p = C.psi_alpha(md, r)
    Wp = np.sqrt(1.0 + np.sum(u * u, 1) / psi_p ** 4)
    idx = np.floor(x / h).astype(np.int64)
    key = (idx[:, 0] * 4096 + idx[:, 1]) * 4096 + idx[:, 2]
    order = np.argsort(key, kind="stable")
    sk = key[order]
    st = np.flatnonzero(np.r_[True, sk[1:] != sk[:-1]])
    en = np.r_[st[1:], len(sk)]
    occ = en - st
    ia, ib, wt, cid = [], [], [], []
    for c, (s0, s1) in enumerate(zip(st, en)):
        n = s1 - s0
        if n < 2:
            continue
        mem = order[s0:s1]
        a, b = np.triu_indices(n, 1)
        w = 1.0
        if n > NMAX:
            npair = len(a)
            pick = rng.choice(npair, NMAX * (NMAX - 1) // 2, replace=False)
            a, b = a[pick], b[pick]
            w = npair / len(a)
        ia.append(mem[a]); ib.append(mem[b]); wt.append(np.full(len(a), w)); cid.append(np.full(len(a), c))
    ia, ib, wt, cid = map(np.concatenate, (ia, ib, wt, cid))
    centre = (idx[order[st]] + 0.5) * h
    psi_c, alp_c = C.psi_alpha(md, np.linalg.norm(centre, axis=1))
    V = psi_c ** 6 * h ** 3
    dt = 0.0625
    pa = u[ia] / psi_c[cid, None] ** 2
    pb = u[ib] / psi_c[cid, None] ** 2
    w1 = wt * M * alp_c[cid] * dt / V[cid] * vmol(pa, pb)
    dW = np.zeros(len(ia))
    dE = np.zeros(len(ia))
    for _ in range(K):
        n = rng.normal(size=(len(ia), 3))
        n /= np.linalg.norm(n, axis=1)[:, None]
        qa, qb = scatter(pa, pb, n)
        ua, ub = qa * psi_c[cid, None] ** 2, qb * psi_c[cid, None] ** 2
        Wa = np.sqrt(1.0 + np.sum(ua * ua, 1) / psi_p[ia] ** 4)
        Wb = np.sqrt(1.0 + np.sum(ub * ub, 1) / psi_p[ib] ** 4)
        dW += M * (Wa + Wb - Wp[ia] - Wp[ib])
        dE += M * (alp_p[ia] * (Wa - Wp[ia]) + alp_p[ib] * (Wb - Wp[ib]))
    dW /= K
    dE /= K
    S = w1.sum()
    # standard error of the weighted mean from the per-pair spread
    mean_dW = float(np.sum(w1 * dW) / S)
    sd_dW = float(np.sqrt(np.sum(w1 * (dW - mean_dW) ** 2) / S))
    neff = S ** 2 / np.sum(w1 ** 2)
    central = occ[np.linalg.norm(centre, axis=1) < 1.0]
    return dict(h=h, sum_w_per_sigma=float(S), occupied_cells=int(len(st)),
                mean_occupation=float(occ.mean()), central_occupation=float(central.mean()) if len(central) else None,
                dW_per_collision=mean_dW, dW_per_collision_rel=mean_dW / float(np.sum(M * Wp)),
                dW_per_collision_se=float(sd_dW / np.sqrt(neff)),
                dEK_per_collision=float(np.sum(w1 * dE) / S))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    md = C.load_model(C.MODELS["cc1"]["tag"])
    res = [run(h, md, a.K, rng) for h in SIZES]
    for r in res:
        print(json.dumps(r), flush=True)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "cells.json"), "w") as f:
        json.dump(dict(model="cc1", sizes=res, K=a.K, NMAX=NMAX), f, indent=1)
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    h = np.array([r["h"] for r in res])
    d = np.array([r["dW_per_collision_rel"] for r in res])
    se = np.array([r["dW_per_collision_se"] for r in res]) / np.array(
        [r["dW_per_collision"] / r["dW_per_collision_rel"] for r in res])
    axs[0].errorbar(h, d, yerr=se, fmt="o", color=fs.PAL["red"], label="predicted defect per collision")
    ref = d[1] * (h / h[1]) ** 2
    axs[0].plot(h, ref, **fs.GUIDE, label=r"$\propto h^2$ through $M/4$")
    axs[0].set_xscale("log"); axs[0].set_yscale("log")
    axs[0].set_xlabel(r"collision cell side $h/M$")
    axs[0].set_ylabel(r"$\Delta(\Sigma MW)/\Sigma MW$ per collision")
    axs[0].legend(fontsize=8, loc="upper left")
    axs[1].plot(h, [r["mean_occupation"] for r in res], "o-", color=fs.PAL["blue"], label="mean, occupied cells")
    axs[1].plot(h, [r["central_occupation"] for r in res], "s-", color=fs.PAL["red"], label=r"cells within $r < M$")
    axs[1].axhline(100.0, **fs.MASK_LINE)
    axs[1].set_xscale("log"); axs[1].set_yscale("log")
    axs[1].set_xlabel(r"collision cell side $h/M$")
    axs[1].set_ylabel("particles per collision cell")
    axs[1].legend(fontsize=8, loc="upper left")
    fig.savefig(os.path.join(a.out, "fig_pred_cellsize.png"), dpi=200)
    return 0


if __name__ == "__main__":
    sys.exit(main())
