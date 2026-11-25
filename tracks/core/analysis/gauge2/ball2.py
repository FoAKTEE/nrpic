#!/usr/bin/env python3
"""Tests L1 and L2 of the gauge package with the corrected condition (source item gauge-2):
the expanding ball against the exact Lemaitre-Tolman-Bondi solution, with the functions of
the first pass (tracks/core/analysis/id/test2_evolution.py, tracks/core/analysis/gauge/
lapse_ref.py) and its numbers for comparison.

    ball2.py --out DIR --tag NAME NAME=RUNDIR:CELLS:HALFWIDTH:STEM:RATE[:FIRSTKEY] ...

STEM names the initial data in scratch/core/id/ic_ball, RATE is lapse_leak, FIRSTKEY a
key of tracks/core/analysis/gauge/ball_numbers_gc.json (the card run of the first pass
on the same mesh).  Writes DIR/ball2_<tag>.json and DIR/ball2_<tag>.png|pdf.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/id"))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/gauge"))
sys.path.insert(0, os.path.join(WT, "python"))

import idlib                                   # noqa: E402,F401
import test2_evolution as t2                   # noqa: E402
from lapse_ref import central_lapse            # noqa: E402
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

IC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball"
GROUPS = ("core", "mid", "outer", "surface")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(WT, "tracks/core/analysis/gauge/ball_numbers_gc.json")) as f:
        first = json.load(f)

    res, data = {}, {}
    for spec in a.runs:
        name, rest = spec.split("=", 1)
        w = rest.split(":")
        rundir, n, half, stem, rate = w[0], int(w[1]), float(w[2]), w[3], float(w[4])
        key = w[5] if len(w) > 5 else None
        man = dict(output_directory=rundir, run_id=name,
                   command=[f"mesh/nx1={n}", f"mesh/x1max={half}"],
                   inputs=[dict(path=f"{IC}/{stem}.json")])
        d = t2.load(man)
        g = t2.gauge_numbers(d)
        t = np.array(g["t"])
        rt, rtau, ra, ral = central_lapse(d["ball"], 1.0 / rate, float(t[-1]), dt=0.01)
        ref = np.interp(t, rt, ral)
        rel = np.abs(np.array(g["alpha_centre"]) / ref - 1.0)
        grp = t2.group_numbers(d)
        rec = dict(cells=n, dx=2.0 * half / n, T=1.0 / rate, t_end=float(t[-1]),
                   groups={k: grp[k]["maxabs_all"] for k in GROUPS if k in grp},
                   turnaround={k: grp[k].get("turnaround") for k in GROUPS if k in grp},
                   alpha_dev=float(rel.max()), t_alpha_dev=float(t[int(np.argmax(rel))]),
                   alpha_max=float(max(g["alpha_max"])),
                   light_speed_max=float(max(g["light_speed_max"])))
        print(f"{name}: cells {n}, T = {1.0 / rate:g} M, to t = {t[-1]:g} M")
        print("   largest |eps|: " + ", ".join(f"{k} {v:.2e}" for k, v in rec["groups"].items()))
        if key:
            fg = {k: first[key]["groups"][k]["maxabs_all"] for k in GROUPS}
            rec["first"] = dict(key=key, run_id=first[key]["run_id"], groups=fg)
            rec["ratio"] = {k: rec["groups"][k] / fg[k] for k in GROUPS}
            print(f"   first pass ({first[key]['run_id']}): "
                  + ", ".join(f"{k} {v:.2e}" for k, v in fg.items()))
            print("   ratio: " + ", ".join(f"{k} {v:.2f}" for k, v in rec["ratio"].items()))
            fa = np.array(first[key]["gauge"]["alpha_centre"])
            fr = first[key].get("alpha_ref")
            if fr is not None:
                rec["first"]["alpha_dev"] = float(np.max(np.abs(fa / np.array(fr) - 1.0)))
        print(f"   central lapse within {rec['alpha_dev']:.3f} of the homogeneous value "
              f"(at t = {rec['t_alpha_dev']:.2f}"
              + (f"; first pass {rec['first']['alpha_dev']:.3f}" if key and "alpha_dev" in rec["first"] else "")
              + f"); largest lapse on the mesh {rec['alpha_max']:.3f}; "
              f"largest coordinate light speed at the particles {rec['light_speed_max']:.3f}")
        for k, v in rec["turnaround"].items():
            if v:
                print(f"   turnaround {k}: R/R_0 = {v['a_max_mean']:.4f} at tau = {v['tau_mean']:.3f}")
        res[name] = rec
        data[name] = (d, g, ref, key)

    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.955, wspace=0.36, hspace=0.3)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    for (name, (d, g, ref, key)), c in zip(data.items(), cols):
        ax[0, 0].plot(g["t"], g["alpha_centre"], color=c, label=name)
        ax[0, 0].plot(g["t"], ref, color=c, ls=":", lw=0.8)
        ax[0, 1].plot(g["t"], g["alpha_max"], color=c)
        if key:
            ax[0, 0].plot(first[key]["gauge"]["t"], first[key]["gauge"]["alpha_centre"],
                          color=c, ls="--", lw=0.9)
            ax[0, 1].plot(first[key]["gauge"]["t"], first[key]["gauge"]["alpha_max"],
                          color=c, ls="--", lw=0.9)
        reg = t2.region_constraints(d)
        if reg:
            ax[0, 2].plot(reg[-1]["profile"]["r"], reg[-1]["profile"]["alpha"], color=c)
            ax[0, 2].axvline(reg[-1]["r_surface"], color=c, lw=0.6, alpha=0.5)
            if key and first[key].get("regions"):
                fr = first[key]["regions"][-1]
                ax[0, 2].plot(fr["profile"]["r"], fr["profile"]["alpha"], color=c, ls="--", lw=0.9)
        for axx, grp in zip(ax[1], ("core", "outer", "surface")):
            idx = d["groups"][grp]
            axx.plot(d["tau"][:, idx].mean(axis=1), np.abs(d["eps"][:, idx]).max(axis=1), color=c)
            if key:
                axx.axhline(first[key]["groups"][grp]["maxabs_all"], color=c, ls="--", lw=0.9)
    ax[0, 0].plot([], [], color="k", ls=":", lw=0.8, label="homogeneous")
    ax[0, 0].plot([], [], color="k", ls="--", lw=0.9, label="first pass (everywhere)")
    ax[0, 0].legend(fontsize=6.5)
    ax[0, 0].set_ylabel("lapse at the centre")
    ax[0, 1].set_ylabel("largest lapse on the mesh")
    ax[0, 2].set_ylabel("lapse at the last dump (shell means)")
    ax[0, 2].set_xlabel(r"coordinate radius $r/M$", labelpad=1)
    for k in (0, 1):
        ax[0, k].set_xlabel(r"coordinate time $t/M$", labelpad=1)
    for axx, grp in zip(ax[1], ("core", "outer", "surface")):
        axx.set_yscale("log")
        axx.set_ylim(1e-5, 1.0)
        axx.set_xlabel(r"proper time $\tau/M$", labelpad=1)
        axx.set_title(f"{grp} shells (dashed: largest of the first pass)", fontsize=7.5)
    ax[1, 0].set_ylabel(r"largest $|R/R_{\rm exact}-1|$")
    fs.save(fig, os.path.join(a.out, f"ball2_{a.tag}"))
    plt.close(fig)
    with open(os.path.join(a.out, f"ball2_{a.tag}.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
