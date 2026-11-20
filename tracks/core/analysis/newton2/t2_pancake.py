#!/usr/bin/env python3
"""Test T2 of work package newton2: Track B's plane-wave pancake with the Fourier
solver of the Newtonian mode, judged with the track's own analysis script.

    t2_pancake.py --run RUNDIR_OF_cases.py_t2 [--card DIR_OF_east64 PARTDIR] [--out DIR]

Runs tracks/B-emd-gw/newton_tests/scripts/analyze_pancake.py (taken from the track's
branch into RUNDIR/refs by cases.py) on the spectral cases together with the track's
pm.py records (scratch/B-emd-gw/B-emd-gw-20261115-115239-69ab1db), and once more on the
seven-point case.  Writes DIR/spectral/pancake.json, DIR/seven_point/pancake.json (the
track's output), the figure DIR/t2_pancake.{png,pdf} and DIR/t2_pancake.json: the
largest sheet error against the Zel'dovich continuum in units of the displacement
(a - 1) d/k next to the track's published numbers for the seven-point multigrid solve
and for pm.py.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
PM = "/data/haiyangw/nrpic/scratch/B-emd-gw/B-emd-gw-20261115-115239-69ab1db"

# newton_tests/README.md of track/B-emd-gw, table P1 (analysis B-20261115-173904-a7297e3)
TRACK_MG = {16: {2: 5.64e-3, 5: 1.16e-2, 10: 1.84e-2, 15: 2.48e-2},
            32: {2: 1.39e-3, 5: 2.99e-3, 10: 4.42e-3, 15: 5.76e-3},
            64: {2: 3.51e-4, 5: 7.42e-4, 10: 1.20e-3, 15: 1.41e-3}}
TRACK_PM = {32: {2: 1.1e-4, 5: 6.1e-4, 10: 2.1e-3, 15: 1.7e-3},
            64: {2: 4.8e-5, 5: 3.3e-4, 10: 1.0e-3, 15: 8.3e-4}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--card", nargs=2, default=None, metavar=("CASEDIR", "PARTDIR"))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    script = os.path.join(a.run, "refs", "B-emd-gw", "tracks", "B-emd-gw", "newton_tests",
                          "scripts", "analyze_pancake.py")
    env = dict(os.environ, MPLBACKEND="Agg", OMP_NUM_THREADS="1",
               PYTHONPATH=os.pathsep.join([os.path.join(ROOT, "python"),
                                           os.path.join(ROOT, "cosmo", "newton"),
                                           os.path.join(ROOT, "cosmo", "ic")]))
    east = ["--east", "16:" + os.path.join(a.run, "east16"),
            "--east", "32:" + os.path.join(a.run, "east32")]
    pm = ["--pm", "32:" + os.path.join(PM, "n32")]
    if a.card:
        east += ["--east", "64:%s:%s" % (a.card[0], a.card[1])]
        pm += ["--pm", "64:" + os.path.join(PM, "n64")]
    for sub, args in (("spectral", east + pm),
                      ("seven_point", ["--east", "32:" + os.path.join(a.run, "east32_7pt")]
                       + ["--pm", "32:" + os.path.join(PM, "n32")])):
        d = os.path.join(a.out, sub)
        os.makedirs(d, exist_ok=True)
        subprocess.run([sys.executable, script, "--out", d] + args, check=True, env=env)
    sp = json.load(open(os.path.join(a.out, "spectral", "pancake.json")))
    s7 = json.load(open(os.path.join(a.out, "seven_point", "pancake.json")))
    res = {"spectral": {}, "seven_point_n32": {}, "track_multigrid": TRACK_MG,
           "track_pm": TRACK_PM}
    for n in (16, 32, 64):
        key = "P1_athenak_n%d" % n
        if key not in sp:
            continue
        e = sp[key]
        row = {"a_cross": e["a_cross"]}
        for ac in (2, 5, 10, 15):
            row["ex_cont_a%d" % ac] = e["ex_cont_a%d" % ac]
            row["ratio_to_track_multigrid_a%d" % ac] = e["ex_cont_a%d" % ac]/TRACK_MG[n][ac]
        mk = "P1_athenak_minus_pm_n%d" % n
        if mk in sp:
            for ac in (2, 5, 10, 15):
                row["minus_pm_a%d" % ac] = sp[mk]["diff_a%d" % ac]
                row["pm_ex_cont_a%d" % ac] = sp[mk]["pm_ex_cont_a%d" % ac]
        res["spectral"][str(n)] = row
    e = s7["P1_athenak_n32"]
    for ac in (2, 5, 10, 15):
        res["seven_point_n32"]["ex_cont_a%d" % ac] = e["ex_cont_a%d" % ac]
        res["seven_point_n32"]["ratio_to_track_multigrid_a%d" % ac] = \
            e["ex_cont_a%d" % ac]/TRACK_MG[32][ac]
        res["seven_point_n32"]["minus_pm_a%d" % ac] = \
            s7["P1_athenak_minus_pm_n32"]["diff_a%d" % ac]
    res["seven_point_n32"]["a_cross"] = e["a_cross"]
    with open(os.path.join(a.out, "t2_pancake.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    # figure: error against Zel'dovich at the check points, per solver
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.15, top=0.95, wspace=0.28)
    acs = np.array([2, 5, 10, 15])
    cols = {16: fs.PAL["orange"], 32: fs.PAL["red"], 64: fs.PAL["yellow"]}
    ax = axs[0]
    for n in (16, 32, 64):
        ax.semilogy(acs, [TRACK_MG[n][c] for c in acs], "o--", ms=4, color=cols[n], lw=1.0,
                    label="multigrid (track), n = %d" % n)
        if str(n) in res["spectral"]:
            ax.semilogy(acs, [res["spectral"][str(n)]["ex_cont_a%d" % c] for c in acs], "s-",
                        ms=4, color=cols[n], label="Fourier, spectral, n = %d" % n)
        if n in TRACK_PM:
            ax.semilogy(acs, [TRACK_PM[n][c] for c in acs], "x:", ms=5, color=cols[n], lw=1.0,
                        label="pm.py (track), n = %d" % n)
    ax.semilogy(acs, [res["seven_point_n32"]["ex_cont_a%d" % c] for c in acs], "k+", ms=8,
                label="Fourier, seven_point, n = 32")
    ax.set_xlabel(r"scale factor $a$", labelpad=-1)
    ax.set_ylabel(r"max$|x - x_{\rm Zel}|\,/\,[(a-1)\,d/k]$")
    ax.set_ylim(1e-8, 1e-1)
    ax.legend(fontsize=6.5, ncol=2, loc="lower right")
    ax = axs[1]
    for n in (32, 64):
        if str(n) in res["spectral"] and "minus_pm_a2" in res["spectral"][str(n)]:
            ax.semilogy(acs, [res["spectral"][str(n)]["minus_pm_a%d" % c] for c in acs], "s-",
                        ms=4, color=cols[n], label="spectral $-$ pm.py, n = %d" % n)
    ax.semilogy(acs, [res["seven_point_n32"]["minus_pm_a%d" % c] for c in acs], "k+--", ms=8,
                lw=1.0, label="seven_point $-$ pm.py, n = 32")
    ax.set_xlabel(r"scale factor $a$", labelpad=-1)
    ax.set_ylabel(r"max$|x - x_{\rm pm}|\,/\,[(a-1)\,d/k]$")
    ax.set_ylim(1e-7, 1e-1)
    ax.legend(fontsize=8, loc="lower right")
    fs.save(fig, os.path.join(a.out, "t2_pancake"))


if __name__ == "__main__":
    main()
