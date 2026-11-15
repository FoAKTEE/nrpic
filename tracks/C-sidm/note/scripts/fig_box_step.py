"""Figure: AthenaK free streaming between two reservoirs in a periodic Minkowski box.

The collisionless limit of the heat-conduction test (collide/TESTS.md T6 at sigma = 0):
two slabs at theta = 0.02 and 0.01 with equal pressure; left-slab sums of rest mass, energy
and kinetic energy per unit transverse area from the code's snapshots, from moving every
particle of the same sample on a straight line, and the exact ensemble curve with the
sampling noise (64 resamplings of the initial state, as collide/analysis/an_step.py).
Reads run t60 (step.json, step.nrp, step.part.*.bin, checked against its manifest).
Uses the track's readers and references (collide/analysis/snap.py, REFERENCES/mj.py,
REFERENCES/conduction.py).
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as cm  # noqa: E402
sys.path.insert(0, os.path.join(cm.TRACK, "collide", "analysis"))
sys.path.insert(0, os.path.join(cm.TRACK, "collide", "REFERENCES"))
import snap  # noqa: E402
import mj  # noqa: E402
import conduction as cd  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_box_step"


def slab_sums(x, u, M, x0, L):
    left = np.mod(x[:, 0] - x0, L) < 0.5 * L
    return np.array([M[left].sum(), (M * snap.W_flat(u))[left].sum(),
                     (M * snap.kinetic_flat(u))[left].sum()])


def main():
    out = cm.out_dir("figures")
    meta = cm.load_json("t60", "step.json")
    ini = snap.read_nrp(cm.run_file("t60", "step.nrp"))
    rdir = cm.run_dir("t60")
    files = sorted(glob.glob(os.path.join(rdir, "step.part.*.bin")))
    for f in files:
        cm.run_file("t60", os.path.basename(f))
    L = meta["box"][0]
    area = meta["box"][1] * meta["box"][2]
    x0 = meta["x0"]
    M = ini["m"]
    v = ini["u"] / snap.W_flat(ini["u"])[:, None]
    lo = np.array([x0, x0, x0])
    box = np.array(meta["box"])
    times, code, free, perr = [], [], [], []
    for f in files:
        s = snap.read_snapshot(f)
        t = s["time"]
        xf = lo + np.mod(ini["x"] + v * t - lo, box)
        d = s["x"] - xf
        d -= box * np.round(d / box)
        perr.append(float(np.abs(d).max()))
        times.append(t)
        code.append(slab_sums(s["x"], s["u"], s["m"], x0, L) / area)
        free.append(slab_sums(xf, ini["u"], M, x0, L) / area)
    times, code, free = np.array(times), np.array(code), np.array(free)
    left0 = np.mod(ini["x"][:, 0] - x0, L) < 0.5 * L
    rho1 = M[left0].sum() / (0.5 * L * area)
    rho2 = M[~left0].sum() / (0.5 * L * area)
    th1 = mj.theta_from_kinetic(float(np.average(snap.kinetic_flat(ini["u"][left0]),
                                                 weights=M[left0])))
    th2 = mj.theta_from_kinetic(float(np.average(snap.kinetic_flat(ini["u"][~left0]),
                                                 weights=M[~left0])))
    ens = np.stack(cd.step_collisionless(times, L, rho1, th1, rho2, th2), 1)
    rng = np.random.default_rng(12345)
    n1, n2 = int(left0.sum()), int((~left0).sum())
    Mm = float(M.mean())
    s1, s2 = mj.Sampler(th1), mj.Sampler(th2)
    sims = []
    for _ in range(64):
        xs = np.concatenate([rng.uniform(0, 0.5 * L, n1), 0.5 * L + rng.uniform(0, 0.5 * L, n2)])
        us = np.concatenate([mj.sample_u(n1, th1, rng, s1), mj.sample_u(n2, th2, rng, s2)])
        Ws, Ks = snap.W_flat(us), snap.kinetic_flat(us)
        vs = us[:, 0] / Ws
        row = []
        for t in times:
            left = np.mod(xs + vs * t, L) < 0.5 * L
            row.append([Mm * left.sum(), Mm * Ws[left].sum(), Mm * Ks[left].sum()])
        sims.append(row)
    noise = np.array(sims).std(0, ddof=1) / area
    tc = L / float(np.sqrt(8 * th2 / np.pi))
    dev = (code[1:] - ens[1:]) / noise[1:]

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.45))
    names = ["rest mass", "energy", "kinetic energy"]
    for k in range(3):
        ax = fig.add_axes([0.085 + 0.33 * k, 0.19, 0.245, 0.70])
        ax.fill_between(times / tc, ens[:, k] - 2 * noise[:, k], ens[:, k] + 2 * noise[:, k],
                        color=cz.PAL["blue"], alpha=0.2, lw=0)
        ax.plot(times / tc, ens[:, k], color=cz.PAL["blue"], label="exact")
        ax.plot(times / tc, free[:, k], **cz.GUIDE, label="free streaming")
        ax.plot(times / tc, code[:, k], "o", ms=2.8, color=cz.PAL["red"], label="AthenaK")
        ax.set_xlabel(r"$t\,\langle|v|\rangle_2/L$")
        ax.set_title(names[k], fontsize=9.5)
        if k == 0:
            ax.set_ylabel("left slab, per unit area")
        if k == 1:
            ax.legend(frameon=False, loc="lower right", fontsize=7.5, handlelength=1.5)
    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    print(f"{STEM}: snapshots {len(files)}; max position error / L = {max(perr) / L:.3e}; "
          f"max |code - free|/free = {np.max(np.abs(code - free) / np.abs(free)):.3e}")
    print(f"{STEM}: deviation from the ensemble in noise units, max |.| = "
          f"{', '.join(f'{np.abs(dev[:, k]).max():.3f}' for k in range(3))}; rms = "
          f"{', '.join(f'{np.sqrt(np.mean(dev[:, k] ** 2)):.3f}' for k in range(3))}")


if __name__ == "__main__":
    main()
