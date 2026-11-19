#!/usr/bin/env python3
"""Temperature-step runs of T6 (heat package), processors.

    run_step.py --part a|b|c --seeds S [S ...] [--n N] [--nproc P]

Box L = 1 along x, left slab [x0, x0 + L/2) at theta_1 = 0.02, right slab at
theta_2 = 0.01, equal pressure, mean rest-mass density 1 (make_box.py step);
lambda = 1/sigma. Snapshots every 0.1 L/<|v|>_2 (parts a, c; <|v|>_2 = sqrt(8 theta_2/pi))
or every 0.25 (part b), reduced to slab sums and x profiles while the run goes on.
  a  lambda/L = 1000 and 100, box 1 x 1/8 x 1/8, 32 x 4 x 4 cells, to 5 L/<|v|>_2,
     dt = 0.01 L/<|v|>_2 (collisions negligible per step);
  c  lambda/L = 10, 1, 0.1, same box, cells <= lambda/4 (64 x 8 x 8 at 0.1), same span,
     dt = min(0.01 L/<|v|>_2, 0.1 t_coll of the cold slab);
  b  lambda/L = 0.01, cells lambda/4 (400 along x) and a transverse box lambda x lambda
     with 4 x 4 cells (the problem is one-dimensional; TESTS.md asks for L/8, which at
     dx = lambda/4 would need 2e7 particles), dt = 0.1 t_coll of the cold slab, to
     1.1 x 2/(chi(kappa_1) k_1^2) at the mean temperature.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import isobaric as iso        # noqa: E402
import rate                   # noqa: E402
import snap                   # noqa: E402

L, TH1, TH2 = 1.0, 0.02, 0.01


def cases(part, seeds, n):
    vbar2 = float(np.sqrt(8 * TH2 / np.pi))
    tcross = L / vbar2
    p0 = 2.0 / (1 / TH1 + 1 / TH2)
    n2 = p0 / TH2
    out = []
    lams = {"a": [1000.0, 100.0], "c": [10.0, 1.0, 0.1], "b": [0.01]}[part]
    for lam in lams:
        sig = 1.0 / lam
        tc_cold = 1.0 / (n2 * sig * float(rate.vmol_mean(TH2)))
        if part in ("a", "c"):
            box = [L, L / 8, L / 8]
            nx = [32, 4, 4] if lam >= 0.125 else [64, 8, 8]     # dx <= lambda/4
            dt = min(0.01 * tcross, 0.1 * tc_cold)
            t_end = 5 * tcross
            snap_dt = 0.1 * tcross
            nn = n if n else (2000000 if part == "a" else 1000000)
        else:
            nxx = int(np.ceil(4 * L / lam - 1e-9))
            box = [L, lam, lam]
            nx = [nxx, 4, 4]
            dt = 0.1 * tc_cold
            chi1 = iso.chi_kappa1(0.5 * (TH1 + TH2), 1.0, sig)
            t_end = 1.1 * 2.0 / (chi1 * (2 * np.pi / L) ** 2)
            snap_dt = 0.25
            nn = n if n else 160000
        nsteps = int(np.ceil(t_end / dt - 1e-9))
        t_end = nsteps * dt
        nsnap = int(round(t_end / snap_dt))
        snap_dt = t_end / nsnap
        for s in seeds:
            out.append(dict(name=f"step_{part}_lam{lam:g}_s{s}", part=part, lam_over_L=lam,
                            sigma=sig, seed=s, n=nn, box=box, nx=nx, dt=dt, t_end=t_end,
                            nsteps=nsteps, snap_dt=snap_dt, tcross=tcross,
                            t_coll_cold=tc_cold, theta1=TH1, theta2=TH2))
    return out


def run_case(root, P):
    d = os.path.join(root, P["name"])
    os.makedirs(d, exist_ok=True)
    meta = hl.make_box(d, "step", n=P["n"], box=P["box"], theta=TH1, theta2=TH2,
                       sigma=P["sigma"], seed=P["seed"])
    P["make_box_meta"] = {k: meta[k] for k in ("n_left", "n_right", "theta1", "theta2")}
    with open(os.path.join(d, "case.json"), "w") as fh:
        json.dump(P, fh, indent=1)
    ovr = hl.overrides(P["box"], P["nx"], P["dt"], P["t_end"] * (1 + 1e-9),
                       P["snap_dt"] * (1 - 1e-9), P["sigma"], P["seed"])
    u0 = snap.read_nrp(os.path.join(d, hl.BASE + ".nrp"))["u"]
    red = hl.SnapReducer(d, hl.step_fun(L, nbins=64 if P["part"] != "b" else 200, u0=u0))
    r = hl.run_athena(d, ovr, reducer=red)
    summ = dict(name=P["name"], rc=r["rc"], wall=r["wall"])
    if r["rc"] == 0:
        summ["coll"] = hl.coll_summary(d)
    with open(os.path.join(d, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ), flush=True)
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["a", "b", "c"], required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--nproc", type=int, default=1)
    a = ap.parse_args()
    root = hl.outdir("step")
    cs = cases(a.part, a.seeds, a.n)
    cs.sort(key=lambda P: -P["n"] * P["nsteps"])
    with ThreadPoolExecutor(a.nproc) as ex:
        res = list(ex.map(lambda P: run_case(root, P), cs))
    with open(os.path.join(root, "summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    sys.exit(1 if any(r["rc"] != 0 for r in res) else 0)


if __name__ == "__main__":
    main()
