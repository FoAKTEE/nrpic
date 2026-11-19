#!/usr/bin/env python3
"""T8, second part: T2(b) at max P = 0.5 with and without sub-cycling.

Maxwell-Juttner box (make_box.py mj), theta = 0.1, N = 1e6, unit box at x0 = 10 with
32^3 cells (about 30 particles per cell), dt = 0.03. A probe of 2 steps with
coll_nsub_max = 1 gives max P at sigma = 1; sigma is then scaled so that max P = 0.5
without sub-cycling. Two runs of 200 steps on the same particles and seed:
  nosub  coll_nsub_max = 1 (one sub-step whatever P),
  sub    coll_subcycle = measured, coll_nsub_max = 1000 (the default).
Per run (TESTS.md T2): (a) accepted collisions against sum_P (Poisson, 4 sqrt(sum_P));
(b) sum_P per step against (1/2) N rho0 sigma <v_Mol>(theta) dt, theta from <W - 1> of the
initial sample (TESTS.md 2a), within 4 standard errors of the step-to-step scatter and
within 0.5 percent; n_trunc reported. Writes t2nosub.json and t2nosub.png.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import mj                     # noqa: E402
import rate                   # noqa: E402
import snap                   # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def hist(d):
    head, h = snap.read_history(os.path.join(d, f"{hl.BASE}.coll.hst"))
    ci = snap.history_columns(head)
    return {k: np.atleast_2d(h)[:, i] for k, i in ci.items()}


def main():
    root = hl.outdir("t2nosub")
    th, N, dt, nst = 0.1, 1000000, 0.03, 200
    box, nx = [1.0, 1.0, 1.0], [32, 32, 32]
    pdir = os.path.join(root, "pfile")
    hl.make_box(pdir, "mj", n=N, box=box, theta=th, sigma=1.0, seed=7)
    pf = os.path.join(pdir, hl.BASE + ".nrp")
    ini = snap.read_nrp(pf)
    th_gas = float(mj.theta_from_kinetic(float(np.mean(hl.kin_flat(ini["u"])))))
    extra = [f"particles/particle_file={pf}"]
    # probe
    d = os.path.join(root, "probe")
    os.makedirs(d, exist_ok=True)
    r = hl.run_athena(d, hl.overrides(box, nx, dt, 2 * dt * (1 + 1e-9), 1e9, 1.0, 1,
                                      nsub_max=1, extra=extra))
    assert r["rc"] == 0, r
    maxP1 = float(np.max(hist(d)["max_P"]))
    sigma = 0.5 / maxP1
    out = dict(theta_nominal=th, theta_gas=th_gas, N=N, dt=dt, steps=nst,
               probe_maxP_sigma1=maxP1, sigma=sigma)
    vm = float(rate.vmol_mean(th_gas))
    expect = 0.5 * N * 1.0 * sigma * vm * dt
    out["expected_per_step"] = expect
    from concurrent.futures import ThreadPoolExecutor
    runs = {"nosub": dict(nsub_max=1), "sub": dict(nsub_max=1000)}

    def go(name):
        dd = os.path.join(root, name)
        os.makedirs(dd, exist_ok=True)
        rr = hl.run_athena(dd, hl.overrides(box, nx, dt, nst * dt * (1 + 1e-9), 1e9, sigma, 1,
                                            extra=extra, **runs[name]))
        return name, rr

    with ThreadPoolExecutor(2) as ex:
        res = dict(ex.map(go, runs))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 3.2))
    ax = fig.add_axes([0.18, 0.15, 0.78, 0.76])
    for name, col in (("nosub", fs.PAL["red"]), ("sub", fs.PAL["blue"])):
        assert res[name]["rc"] == 0, res[name]
        h = hist(os.path.join(root, name))
        sP = h["sum_P"][1:]
        nc = h["n_coll"][1:]
        ratio = sP / expect
        m = float(ratio.mean())
        se = float(ratio.std(ddof=1) / np.sqrt(len(ratio)))
        za = float((nc.sum() - sP.sum()) / np.sqrt(sP.sum()))
        out[name] = dict(sumP_over_expected=m, se=se, z_b=(m - 1) / se,
                         pass_b=bool(abs(m - 1) < 0.005 and abs(m - 1) < 4 * se),
                         z_a=za, pass_a=bool(abs(za) < 4),
                         n_trunc=float(h["n_trunc"].sum()), max_P=float(h["max_P"].max()),
                         mean_nsub=float(h["mean_nsub"].mean()),
                         max_nsub=float(h["max_nsub"].max()), wall=res[name]["wall"],
                         n_coll=float(nc.sum()), sum_P=float(sP.sum()))
        ax.plot(h["ncycle"][1:], ratio, "-", color=col, lw=1.0,
                label=f"{name}: {m:.5f} $\\pm$ {se:.5f}")
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_xlabel("cycle")
    ax.set_ylabel(r"sum$_P$ per step / analytic")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title(r"T2(b) at max $P=0.5$, $\theta=0.1$", fontsize=10)
    fs.save(fig, os.path.join(root, "t2nosub"))
    with open(os.path.join(root, "t2nosub.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
