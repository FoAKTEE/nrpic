#!/usr/bin/env python3
"""Test T6 / T7b of TESTS.md: the temperature step in a periodic Minkowski box.

    python3 an_step.py RUNDIR BASE META.json INITIAL.nrp OUTDIR [--sigma S]

Reads the snapshots RUNDIR/BASE.part.*.bin and measures, per unit transverse area, the
rest mass, the energy and the kinetic energy in the left slab [x0, x0 + L/2):
X_L(t) = sum over particles there of M, M W, M (W - 1).
References:
  - collisionless, this sample: every particle moved on x0 + (u/W) t (mod L); the slab
    sums of that motion (deterministic for the sample) and, for sigma = 0, the largest
    position error of the code against it;
  - collisionless, ensemble: conduction.step_collisionless with the sample's slab
    densities and temperatures (exact for an infinite sample);
  - diffusive (sigma > 0 given): conduction.step_diffusive with chi from kappa_1
    (non-relativistic Chapman-Enskog), for comparison when lambda << L.
Writes OUTDIR/step_<BASE>.png and OUTDIR/step_<BASE>.json (verdict for sigma = 0:
position error below 1e-9 L and slab sums of the code equal to the free-streaming sums of
the sample to 1e-12 relative; the ensemble comparison is reported in units of the
sampling noise, estimated from 64 resamplings of the reference distribution).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "REFERENCES"))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))

import matplotlib                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt         # noqa: E402
from nrpic import figstyle as fs        # noqa: E402

import snap                             # noqa: E402
import mj                               # noqa: E402
import conduction as cd                 # noqa: E402


def slab_sums(x, u, M, x0, L):
    xl = np.mod(x[:, 0] - x0, L)
    left = xl < 0.5 * L
    W = snap.W_flat(u)
    K = snap.kinetic_flat(u)
    return np.array([M[left].sum(), (M * W)[left].sum(), (M * K)[left].sum()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir"); ap.add_argument("base"); ap.add_argument("meta")
    ap.add_argument("initial"); ap.add_argument("outdir")
    ap.add_argument("--sigma", type=float, default=0.0)
    a = ap.parse_args()
    meta = json.load(open(a.meta))
    ini = snap.read_nrp(a.initial)
    L = meta["box"][0]
    area = meta["box"][1] * meta["box"][2]
    x0 = meta["x0"]
    files = snap.snapshots(a.rundir, a.base)
    if not files:
        raise SystemExit("no snapshots")
    M = ini["m"]
    v = ini["u"] / snap.W_flat(ini["u"])[:, None]
    lo = np.array([x0, x0, x0])
    box = np.array(meta["box"])
    times, code, free, pos_err, u_err = [], [], [], [], []
    for f in files:
        s = snap.read_snapshot(f)
        assert np.array_equal(s["tag"], np.arange(len(M))), "tags must be file positions"
        t = s["time"]
        xf = lo + np.mod(ini["x"] + v * t - lo, box)
        d = s["x"] - xf
        d -= box * np.round(d / box)              # periodic distance
        pos_err.append(float(np.abs(d).max()))
        u_err.append(float(np.abs(s["u"] - ini["u"]).max()))
        times.append(t)
        code.append(slab_sums(s["x"], s["u"], s["m"], x0, L) / area)
        free.append(slab_sums(xf, ini["u"], M, x0, L) / area)
    times = np.array(times); code = np.array(code); free = np.array(free)
    # ensemble reference from the sample's slab densities and temperatures
    left0 = np.mod(ini["x"][:, 0] - x0, L) < 0.5 * L
    rho1 = M[left0].sum() / (0.5 * L * area)
    rho2 = M[~left0].sum() / (0.5 * L * area)
    th1 = mj.theta_from_kinetic(float(np.average(snap.kinetic_flat(ini["u"][left0]),
                                                 weights=M[left0])))
    th2 = mj.theta_from_kinetic(float(np.average(snap.kinetic_flat(ini["u"][~left0]),
                                                 weights=M[~left0])))
    NL, EL, KL = cd.step_collisionless(times, L, rho1, th1, rho2, th2)
    ens = np.stack([NL, EL, KL], 1)
    # sampling noise of the slab sums: resample the reference state 64 times
    rng = np.random.default_rng(12345)
    n1, n2 = int(left0.sum()), int((~left0).sum())
    Mm = float(M.mean())
    sims = []
    s1, s2 = mj.Sampler(th1), mj.Sampler(th2)
    for r in range(64):
        xa = rng.uniform(0, 0.5 * L, n1); xb = 0.5 * L + rng.uniform(0, 0.5 * L, n2)
        ua = mj.sample_u(n1, th1, rng, s1); ub = mj.sample_u(n2, th2, rng, s2)
        xs = np.concatenate([xa, xb]); us = np.concatenate([ua, ub])
        vs = us[:, 0] / snap.W_flat(us)
        Ws = snap.W_flat(us); Ks = snap.kinetic_flat(us)
        row = []
        for t in times:
            left = np.mod(xs + vs * t, L) < 0.5 * L
            row.append([Mm * left.sum(), Mm * Ws[left].sum(), Mm * Ks[left].sum()])
        sims.append(row)
    sims = np.array(sims) / area
    noise = sims.std(0, ddof=1)
    noise[noise == 0] = np.inf
    dev_sigma = (code - ens) / noise
    rel_free = np.abs(code - free) / np.abs(free)
    res = dict(rundir=a.rundir, n=len(M), L=L, rho1=rho1, rho2=rho2, theta1=th1,
               theta2=th2, sigma=a.sigma, times=times.tolist(),
               max_position_error_over_L=float(np.max(pos_err) / L),
               max_u_change=float(np.max(u_err)),
               max_rel_dev_code_vs_free_sample=float(rel_free.max()),
               max_abs_dev_vs_ensemble_in_noise=[float(np.abs(dev_sigma[1:, k]).max())
                                                 for k in range(3)],
               rms_dev_vs_ensemble_in_noise=[float(np.sqrt(np.mean(dev_sigma[1:, k] ** 2)))
                                             for k in range(3)])
    if a.sigma == 0.0:
        res["pass_collisionless"] = bool(res["max_position_error_over_L"] < 1e-9 and
                                         res["max_rel_dev_code_vs_free_sample"] < 1e-12)
    # figure
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    names = ["rest mass", "energy", "kinetic energy"]
    tc = L / float(np.sqrt(8 * th2 / np.pi))
    for k in range(3):
        ax = fig.add_axes([0.07 + 0.33 * k, 0.15, 0.25, 0.78])
        Xinf = ens[-1, k] if False else None
        ax.plot(times / tc, ens[:, k], color=fs.PAL["blue"], label="exact, ensemble")
        ax.fill_between(times / tc, ens[:, k] - 2 * sims.std(0)[:, k],
                        ens[:, k] + 2 * sims.std(0)[:, k], color=fs.PAL["blue"],
                        alpha=0.2, lw=0)
        ax.plot(times / tc, free[:, k], **fs.GUIDE, label="free streaming, this sample")
        ax.plot(times / tc, code[:, k], "o", ms=3, color=fs.PAL["red"], label="AthenaK")
        if a.sigma > 0:
            lam = 1.0 / (0.5 * (rho1 + rho2) * a.sigma)
            thm = 0.5 * (th1 + th2)
            kap = cd.kappa_ce_nr(thm, a.sigma)          # sigma_tot with m = 1
            ch = cd.chi(kap, 0.5 * (rho1 + rho2), thm)
            tt = np.linspace(0, times[-1], 300)
            ax.plot(tt / tc, cd.step_diffusive(tt, L, ens[0, k], ens[-1, k], ch),
                    color="k", lw=1.0, ls=":", label=r"diffusive, $\kappa_1$")
        ax.set_xlabel(r"$t\,\langle |v|\rangle_2/L$")
        ax.set_title(names[k], fontsize=10)
        if k == 0:
            ax.set_ylabel("left slab, per unit area")
            ax.legend(loc="upper right", fontsize=8)
    os.makedirs(a.outdir, exist_ok=True)
    fs.save(fig, os.path.join(a.outdir, f"step_{a.base}"))
    with open(os.path.join(a.outdir, f"step_{a.base}.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "times"}, indent=1))


if __name__ == "__main__":
    main()
