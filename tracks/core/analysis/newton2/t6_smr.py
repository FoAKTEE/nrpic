#!/usr/bin/env python3
"""Test T6 of work package newton2: the moving, rotating ball of newtonian_mode.md 5.5
on the uniform 64^3 mesh and on the same mesh with one static refinement level, which
the ball crosses (multigrid solver on a refined mesh).

    t6_smr.py --run RUNDIR_OF_cases.py_t6 [--out DIR]
    t6_smr.py --run RUNDIR_OF_cases.py_t6b --cases spin_in_uni64 spin_in_uni128 spin_in_smr

Runs problems/newton/analyze_conservation.py on both cases (drift of the centre of mass
from uniform motion, of the momentum, of the angular momentum about the centre of mass
and of the energy; consistency of the second-moment columns) and adds the history of the
solver (V cycles, defect) and the number of particles that changed level.  Writes
DIR/spin_uni64.{json,png}, DIR/spin_smr.{json,png}, DIR/t6_smr.json, DIR/t6_smr.{png,pdf}.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--cases", nargs="+", default=["spin_uni64", "spin_smr"])
    ap.add_argument("--fine", type=float, default=1.0,
                    help="half-width of the refined MeshBlocks (particles inside counted)")
    ap.add_argument("--ic", default="", help="JSON of the particle file (default RUN/ic/spin.json)")
    ap.add_argument("--stem", default="", help="name of the summary files")
    ap.add_argument("--labels", nargs="+", default=None, help="legend labels of the cases")
    a = ap.parse_args()
    icjson = a.ic or os.path.join(a.run, "ic", "spin.json")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    res = {}
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.17, top=0.93, wspace=0.34)
    palette = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    cols = {n: palette[i % len(palette)] for i, n in enumerate(a.cases)}
    labs = {n: (r"$64^3$ + one level" if "smr" in n else
                r"uniform $%s^3$" % "".join(ch for ch in n.split("uni")[-1] if ch.isdigit()))
            for n in a.cases}
    if a.labels:
        labs = dict(zip(a.cases, a.labels))
    for name in a.cases:
        d = os.path.join(a.run, name)
        log = open(os.path.join(d, "athena.log")).read()
        hfile = glob.glob(os.path.join(d, "*.newton.hst"))
        if not hfile or "Terminating on" not in log:
            res[name] = dict(completed=False, log_tail=log[-600:])
            continue
        rc = subprocess.run([sys.executable,
                             os.path.join(ROOT, "problems", "newton", "analyze_conservation.py"),
                             "--ic", icjson, "--run", d,
                             "--out", a.out, "--name", name], capture_output=True, text=True)
        out = json.load(open(os.path.join(a.out, name + ".json"))) if rc.returncode == 0 \
            else dict(error=rc.stderr[-800:])
        h = nw.read_newton_hst(hfile[0])
        out.update(completed=True, steps=int(h["ncycle"][-1]),
                   mg_cycles_mean=float(np.mean(h["mg_cycles"][1:])),
                   mg_cycles_max=float(np.max(h["mg_cycles"])),
                   mg_defect_max=float(np.max(h["mg_defect"])),
                   meshblocks=[ln for ln in log.split("\n") if "MeshBlock" in ln][:3])
        # particles inside the refined region |x_i| < 1 at the snapshots
        inside = []
        for f in sorted(glob.glob(os.path.join(d, "*.part.*.bin"))):
            t, cyc, x, u, m, tag = nw.read_snapshot(f)
            ins = np.zeros(len(tag), dtype=bool)
            ins[tag] = (np.abs(x) < a.fine).all(axis=1)
            inside.append(ins)
        if len(inside) > 1:
            out["particles"] = int(len(inside[0]))
            out["inside_fine_region"] = [int(i.sum()) for i in inside]
            out["changed_region_between_snapshots"] = [int((inside[k] != inside[k+1]).sum())
                                                       for k in range(len(inside) - 1)]
            out["changed_region_first_to_last"] = int((inside[0] != inside[-1]).sum())
        res[name] = out
        E = h["K"] + h["W"]
        M = h["mass"][0]
        P = np.stack([h["P_x"], h["P_y"], h["P_z"]], axis=1)
        X = np.stack([h["X_x"], h["X_y"], h["X_z"]], axis=1)
        V0 = P[0]/M
        axs[0].plot(h["time"], 1e3*np.sqrt(((P - P[0])**2).sum(axis=1))/M, color=cols[name],
                    label=labs[name])
        axs[1].plot(h["time"], 1e3*np.sqrt(((X - X[0] - V0[None, :]*h["time"][:, None])**2
                                            ).sum(axis=1)), color=cols[name])
        axs[2].plot(h["time"], 1e3*(E - E[0])/abs(E[0]), color=cols[name])
    axs[0].set_xlabel(r"$t$", labelpad=-1)
    axs[0].set_ylabel(r"$10^3\,|\Delta P|/M$")
    axs[0].legend(loc="best", fontsize=7)
    axs[1].set_xlabel(r"$t$", labelpad=-1)
    axs[1].set_ylabel(r"$10^3\,|X - X_0 - V_0 t|$")
    axs[2].set_xlabel(r"$t$", labelpad=-1)
    axs[2].set_ylabel(r"$10^3\,(E - E_0)/|E_0|$")
    stem = a.stem or ("t6_smr" if a.cases == ["spin_uni64", "spin_smr"] else "t6b_smr")
    fs.save(fig, os.path.join(a.out, stem))
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
