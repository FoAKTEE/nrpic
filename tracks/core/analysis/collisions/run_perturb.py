#!/usr/bin/env python3
"""S: the perturbing radial force <particles> perturb_gamma
(athenak/src/particles/nrpic_perturb.cpp) in flat space, problems/tests/perturb_flat.athinput.

  run_perturb.py OUT [--exe ATHENA]

Particle 0 starts at rest at distance 13 from the centre: its momentum after the
interval must be gamma T_pert x/r to rounding for steps that do and do not divide the
interval. Particle 1 crosses the radial direction: its state at t = 1 is compared with
an independent integration (scipy, relative tolerance 1e-13) for a sequence of steps;
the error of the splitting must fall as the square of the step for steps of which the
ends of the interval are boundaries (for other steps the last partial kick adds an
error of the same order with an irregular coefficient). With perturb_gamma = 0
the snapshot must be byte-identical to that of a deck without the options.
"""
import argparse
import filecmp
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

import common
from nrpic import collide

DECK = os.path.join(common.REPO, "problems", "tests", "perturb_flat.athinput")
GAMMA, TP, T0 = 0.25, 0.37, 0.1
CEN = np.array([100.0, 100.0, 100.0])
X0 = np.array([[103.0, 104.0, 112.0], [101.0, 100.5, 99.0]])
U0 = np.array([[0.0, 0.0, 0.0], [0.3, -0.8, 0.5]])


def reference(x0, u0, tend):
    def rhs(t, y):
        x, u = y[:3], y[3:]
        w = np.sqrt(1.0 + u @ u)
        d = x - CEN
        on = 1.0 if T0 <= t < T0 + TP else 0.0
        return np.concatenate((u/w, on*GAMMA*d/np.linalg.norm(d)))
    y = np.concatenate((x0, u0))
    t = 0.0
    for t1 in (T0, T0 + TP, tend):               # the force is discontinuous at these
        s = solve_ivp(rhs, (t, t1 - 1e-15 if t1 < tend else t1), y, rtol=1e-13, atol=1e-15,
                      method="DOP853")
        y, t = s.y[:, -1], t1
    return y[:3], y[3:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    # 0.05, 0.037, 0.02: the interval [0.1, 0.47] does not end on a step boundary;
    # 0.01, 0.005, 0.0025: it does (the order of the splitting is taken from these)
    dts = [0.05, 0.037, 0.02, 0.01, 0.005, 0.0025]
    jobs = [(args.exe, DECK, os.path.join(out, f"dt{dt}"), [f"particles/dt={dt!r}"])
            for dt in dts]
    # null: gamma = 0 against a deck without the options
    nodeck = os.path.join(out, "perturb_flat_off.athinput")
    with open(DECK) as fp, open(nodeck, "w") as fo:
        for line in fp:
            if not line.startswith("perturb_"):
                fo.write(line)
    jobs.append((args.exe, DECK, os.path.join(out, "gamma0"), ["particles/perturb_gamma=0.0"]))
    jobs.append((args.exe, nodeck, os.path.join(out, "off"), []))
    res = common.run_many(jobs, 4)
    if any(r[0] != 0 for r in res):
        print("a run failed:", [r[0] for r in res])
        sys.exit(1)
    xr, ur = reference(X0[1], U0[1], 1.0)
    d0 = X0[0] - CEN
    uexp = GAMMA*TP*d0/np.linalg.norm(d0)
    rows = []
    for dt in dts:
        s = collide.read_snapshot(common.snapshots(os.path.join(out, f"dt{dt}"), "pert")[-1])
        i0, i1 = int(np.nonzero(s["tag"] == 0)[0][0]), int(np.nonzero(s["tag"] == 1)[0][0])
        rows.append(dict(dt=dt, time=s["time"],
                         rest_err=float(np.max(np.abs(s["u"][i0] - uexp))/np.linalg.norm(uexp)),
                         moving_err_u=float(np.max(np.abs(s["u"][i1] - ur))),
                         moving_err_x=float(np.max(np.abs(s["x"][i1] - xr)))))
    f_a = common.snapshots(os.path.join(out, "gamma0"), "pert")
    f_b = common.snapshots(os.path.join(out, "off"), "pert")
    null_same = bool(len(f_a) == len(f_b) and all(filecmp.cmp(a, b, shallow=False)
                                                  for a, b in zip(f_a, f_b)))
    # order of the splitting from the three steps that divide the end time
    e = {r["dt"]: r["moving_err_u"] for r in rows}
    order = [float(np.log2(e[0.01]/e[0.005])), float(np.log2(e[0.005]/e[0.0025]))]
    summary = dict(gamma=GAMMA, t_pert=TP, t_start=T0, expected_u_rest=uexp.tolist(),
                   reference_u=ur.tolist(), reference_x=xr.tolist(), rows=rows,
                   order=order, null_byte_identical=null_same, exe=args.exe,
                   exe_sha256=common.sha256(args.exe))
    ok = (all(r["rest_err"] < 1e-14 for r in rows) and all(1.8 < o < 2.2 for o in order)
          and null_same and all(abs(r["time"] - 1.0) < 0.06 for r in rows))
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(3.6, 2.9))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.17, top=0.96)
    dd = np.array([r["dt"] for r in rows])
    ax.loglog(dd, [max(r["rest_err"], 1e-17) for r in rows], "o", color=fs.PAL["blue"],
              ms=4, label="particle at rest: $|u - \\gamma T x/r|/|u|$")
    sel = [r for r in rows if r["dt"] in (0.01, 0.005, 0.0025)]
    oth = [r for r in rows if r["dt"] not in (0.01, 0.005, 0.0025)]
    ax.loglog([r["dt"] for r in oth], [r["moving_err_u"] for r in oth], "s",
              color=fs.PAL["red"], ms=4, mfc="none",
              label="moving particle, interval not on step boundaries")
    ax.loglog([r["dt"] for r in sel], [r["moving_err_u"] for r in sel], "s-",
              color=fs.PAL["red"], ms=4, lw=1.0, label="moving particle: $|u - u_{\\rm ref}|$")
    ax.loglog(dd, sel[0]["moving_err_u"]*(dd/sel[0]["dt"])**2, **fs.GUIDE)
    ax.set_xlabel("step")
    ax.set_ylabel("error at $t = 1$")
    ax.legend(fontsize=6.5, loc="center right")
    fig.savefig(os.path.join(out, "fig_perturb.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
