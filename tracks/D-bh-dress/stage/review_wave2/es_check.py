#!/usr/bin/env python3
"""Lead's wave-2 re-check of the es_runs package (JOURNAL.md, lead-wave2 predictions W1-W4).

Independent of the helper's analysis code: the closed forms are written here from the
slice definition (es_model.py module text: dR/dtau = f sqrt(2m/R), m = M inside the bubble);
only f(R) is taken from es_model so that the same slice is meant. Reads the registered data
run D-20261115-170213-d2c2131 (particle files, json) and the smoke run D-20261115-172413-6412daf
(log). Writes es_check.json and es_check.png into --out.
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "einstein_straus"))
sys.path.insert(0, os.path.normpath(os.path.join(TRACK, "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
DATA = os.path.join(SCR, "D-20261115-170213-d2c2131")
SMOKE = os.path.join(SCR, "D-20261115-172413-6412daf")


def smooth_step(x):
    # same definition as es_model.smooth_step (C-infinity step), written again here
    x = float(x)
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    g = 1.0 / x - 1.0 / (1.0 - x)
    return 0.5 * (1.0 - math.tanh(0.5 * g))


def crossing_time(R0, M=1.0, R0f=4.0, R1f=36.0, Rend=2.0):
    """Proper time from R0 (moving outward with f sqrt(2M/R0)) to R = Rend, around M."""
    f = smooth_step((R0 - R0f) / (R1f - R0f))
    E = -M * (1.0 - f * f) / R0          # (dR/dtau)^2/2 - M/R
    A = M / (-2.0 * E)                    # R = A (1 - cos eta)
    T = M / (-2.0 * E) ** 1.5             # tau = T (eta - sin eta)
    eta0 = math.acos(1.0 - R0 / A)        # expanding branch
    eta1 = 2.0 * math.pi - math.acos(1.0 - Rend / A)
    return T * ((eta1 - math.sin(eta1)) - (eta0 - math.sin(eta0))), 2.0 * A


def read_nrp(path):
    with open(path, "rb") as fh:
        magic = fh.read(8)
        assert magic == b"NRPIC001", magic
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        sp = np.frombuffer(fh.read(4 * n), "<i4")
    return rec, sp


def leaf_blocks(half_root=192.0, nroot=96, nb=24, regions=((1, 95.9), (2, 47.9), (5, 1.5))):
    """Leaf MeshBlocks of a static nest of cubes centred on 0 with 2:1 balance."""
    # block size per level, refine a block if it overlaps a region of a higher level, or
    # (2:1 balance) if it touches a block two levels finer
    blocks = {}
    nper = nroot // nb
    size0 = 2 * half_root / nper
    want = {}
    for lev, h in regions:
        want[lev] = h
    # target level of a point-sized block at centre c: highest region containing the block
    def target(lo, hi):
        t = 0
        for lev, h in regions:
            if hi[0] > -h and lo[0] < h and hi[1] > -h and lo[1] < h and hi[2] > -h and lo[2] < h:
                t = max(t, lev)
        return t
    leaves = []

    def split(lo, size, lev):
        hi = lo + size
        if lev < target(lo, hi):
            for i in (0, 1):
                for j in (0, 1):
                    for k in (0, 1):
                        split(lo + 0.5 * size * np.array([i, j, k]), 0.5 * size, lev + 1)
        else:
            leaves.append((lev, tuple(lo), size))
    for i in range(nper):
        for j in range(nper):
            for k in range(nper):
                split(np.array([-half_root + i * size0, -half_root + j * size0,
                                -half_root + k * size0]), size0, 0)
    # 2:1 balance: refine leaves adjacent (face, edge or corner) to leaves two levels finer
    changed = True
    while changed:
        changed = False
        new = []
        arr = leaves
        for (lev, lo, size) in arr:
            lo = np.array(lo)
            hi = lo + size
            need = False
            for (l2, lo2, s2) in arr:
                if l2 >= lev + 2:
                    lo2 = np.array(lo2)
                    hi2 = lo2 + s2
                    if np.all(lo2 <= hi + 1e-9) and np.all(hi2 >= lo - 1e-9):
                        need = True
                        break
            if need:
                changed = True
                for i in (0, 1):
                    for j in (0, 1):
                        for k in (0, 1):
                            new.append((lev + 1, tuple(lo + 0.5 * size * np.array([i, j, k])), 0.5 * size))
            else:
                new.append((lev, tuple(lo), size))
        leaves = new
    counts = {}
    for lev, _, _ in leaves:
        counts[lev] = counts.get(lev, 0) + 1
    return len(leaves), dict(sorted(counts.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    out = {}
    with open(os.path.join(DATA, "predictions.json")) as fh:
        pred = json.load(fh)
    # W1 crossings and wall
    w1 = {}
    for g, R0 in ((0, 6.0), (1, 10.0), (2, 20.0)):
        tau, rmax = crossing_time(R0)
        key = f"group{g}_R0={int(R0)}"
        w1[key] = dict(lead=tau, Rmax=rmax, helper=pred["tau_reach_2M_es"][key],
                       helper_v1=pred["tau_reach_2M_v1"][key],
                       diff=tau - pred["tau_reach_2M_es"][key])
    for t in (50, 100, 150, 200):
        Rw = (36.0 ** 1.5 + 1.5 * math.sqrt(2.0) * t) ** (2.0 / 3.0)
        w1[f"Rwall_tau={t}"] = dict(lead=Rw, helper=pred["R_wall"][f"tau={t}"],
                                    diff=Rw - pred["R_wall"][f"tau={t}"])
    out["W1"] = w1
    # W2 homogeneous 1+log model
    H0 = pred["es_summary"]["H"]

    def rhs(t, y):
        a, al, tau = y
        H = H0 * a ** -1.5
        return [al * H * a, 6.0 * al * H, al]
    ts = np.linspace(0.0, 200.0, 2001)
    sol = solve_ivp(rhs, (0.0, 200.0), [1.0, 1.0, 0.0], t_eval=ts, rtol=1e-11, atol=1e-12)
    a, al, tau = sol.y
    w2 = {}
    for t in (25, 50, 100, 150, 200):
        i = int(round(t * 10))
        h = pred["plateau_1plog_zero_shift"].get(f"t={t}")
        w2[f"t={t}"] = dict(a=a[i], alpha=al[i], tau=tau[i], alpha_check=1 + 6 * math.log(a[i]),
                            helper_alpha=h["alpha"] if h else None, helper_tau=h["tau"] if h else None,
                            rel_alpha=(al[i] / h["alpha"] - 1) if h else None,
                            rel_tau=(tau[i] / h["tau"] - 1) if h else None)
    # areal radius of the outer dust edge (60 M) and of the plateau's outer end (52 M)
    w2["areal_R_52_at_t200"] = 52.0 * a[-1]
    w2["areal_R_60_at_t200_if_plateau"] = 60.0 * a[-1]
    out["W2"] = w2
    # W3 particle files
    rec, sp = read_nrp(os.path.join(DATA, "es", "es.nrp"))
    m = rec[:, 6]
    trac = m == 1e-30
    rec1, _ = read_nrp(os.path.join(DATA, "v1", "v1.nrp"))
    out["W3"] = dict(n_es=int(len(m)), n_tracers=int(trac.sum()),
                     tracer_masses=sorted(set(m[trac].tolist())), n_zero_mass=int((m == 0).sum()),
                     dust_mass=float(m[~trac].sum()), M_dust_json=pred["es_summary"]["M_dust"],
                     n_v1=int(len(rec1)), v1_masses=sorted(set(rec1[:, 6].tolist())),
                     tracer_pos_maxdiff=float(np.abs(rec1[:, :3] - rec[trac][:, :3]).max())
                     if len(rec1) == trac.sum() else None,
                     dust_r_min=float(np.sqrt((rec[~trac, :3] ** 2).sum(1)).min()),
                     dust_r_max=float(np.sqrt((rec[~trac, :3] ** 2).sum(1)).max()),
                     dust_u_max=float(np.abs(rec[~trac, 3:6]).max()))
    # W4 MeshBlocks
    nleaf, per = leaf_blocks()
    log = open(os.path.join(SMOKE, "run.log")).read()
    mm = re.search(r"Total number of MeshBlocks = (\d+)", log)
    out["W4"] = dict(lead_leaf_count=nleaf, per_level=per, athenak_log=int(mm.group(1)))
    with open(os.path.join(args.out, "es_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    # figure: the homogeneous 1+log model and the closed-form tracer curves
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.95, wspace=0.28)
    ax = axs[0]
    ax.plot(ts, al, color=fs.PAL["red"], label=r"$\alpha$ (lead ODE)")
    ax.plot(ts, a, color=fs.PAL["yellow"], label=r"$a$ (lead ODE)")
    ht = [25, 50, 100, 150, 200]
    ax.plot(ht, [pred["plateau_1plog_zero_shift"][f"t={t}"]["alpha"] for t in ht], "o",
            mfc="none", color=fs.PAL["blue"], label=r"$\alpha$ (helper)")
    ax.set_xlabel(r"coordinate time $t/M$")
    ax.set_ylabel("plateau value")
    ax.legend(frameon=False)
    ax = axs[1]
    tt = np.linspace(0, 260, 1000)
    import es_model as em
    ES = em.EinsteinStrausBH(Rb=56.0, w_out=4.0, ngrid=2001)
    for g, R0 in ((0, 6.0), (1, 10.0), (2, 20.0)):
        f = smooth_step((R0 - 4.0) / 32.0)
        E = -(1 - f * f) / R0
        R = em.ltb_radius(np.full_like(tt, R0), tt, np.ones_like(tt), np.full_like(tt, E))
        ax.plot(tt, R, color=fs.series_colors(3)[g], label=f"$R_0 = {int(R0)}M$")
        ax.axvline(out["W1"][f"group{g}_R0={int(R0)}"]["lead"], color="k", lw=0.8, ls=":")
    ax.axhline(2.0, color="k", ls="--", lw=1.0)
    ax.set_xlabel(r"proper time $\tau/M$")
    ax.set_ylabel(r"areal radius $R/M$")
    ax.set_yscale("log")
    ax.legend(frameon=False)
    fs.save(fig, os.path.join(args.out, "es_check"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
