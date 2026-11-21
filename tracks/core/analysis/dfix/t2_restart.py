#!/usr/bin/env python3
"""Test T2 of work package dfix: the output schedule across a restart.

    runreg.py --purpose "..." --cores 1 -- python3 tracks/core/analysis/dfix/t2_restart.py \
        --old <release athena> --new <corrected athena> [--fig PREFIX]

Runs problems/tests/restart_schedule.athinput (restart dumps every 50 M, tables every
25 M, 300 M) in $NRPIC_RUN_DIR for each executable:
  u        uninterrupted
  c        stopped at the cycle limit nlim = 1234 (t = 123.4), continued from the restart
           file written at the stop
  w        stopped at the wall clock limit (-t 00:00:02, with the particle step 1e-4 M so
           that the run lasts about half a minute), continued
and lists the times of the restart files and tables each case wrote. Writes
t2_restart.json into the run directory and the figure PREFIX.png.
"""
import argparse
import glob
import json
import os
import re
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
INPUT = os.path.join(REPO, "problems", "tests", "restart_schedule.athinput")


def rst_time(path):
    """time stored in the header of a mesh restart file"""
    blob = open(path, "rb").read(1 << 20)
    k = blob.index(b"<par_end>\n") + len(b"<par_end>\n")
    off = k + 4 + 4 + 72 + 76 + 76      # nmb, root level, RegionSize, 2 x RegionIndcs
    return struct.unpack("d", blob[off:off + 8])[0]


def tab_time(path):
    with open(path) as fp:
        head = fp.readline()
    return float(re.search(r"time=\s*([-+0-9.eE]+)", head).group(1))


def athena(exe, d, args, log):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, log), "w") as fp:
        return subprocess.run([exe] + args + ["-d", d], cwd=d, stdout=fp,
                              stderr=subprocess.STDOUT).returncode


def last_message(d, log):
    for line in open(os.path.join(d, log)):
        if line.startswith("Terminating on"):
            return line.strip()
    return "no termination message"


def collect(d):
    rst = sorted(glob.glob(os.path.join(d, "rst", "rsch.*.rst")))
    tab = sorted(glob.glob(os.path.join(d, "tab", "rsch.adm_alpha.*.tab")))
    tr = np.fromfile(os.path.join(d, "rsch.traj.bin")).reshape(-1, 8)
    return {"rst_times": [round(rst_time(p), 9) for p in rst],
            "tab_times": [round(tab_time(p), 9) for p in tab],
            "final_state": [float(x) for x in tr[-1]]}


def figure(res, out):
    sys.path.insert(0, os.path.join(REPO, "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.24, right=0.98, bottom=0.16, top=0.96)
    names = [("old_u", "release, uninterrupted"),
             ("old_c", "release, cycle limit"),
             ("old_w", "release, wall clock"),
             ("new_u", "corrected, uninterrupted"),
             ("new_c", "corrected, cycle limit"),
             ("new_w", "corrected, wall clock")]
    for k, (c, lab) in enumerate(names):
        v = res["cases"][c]
        y = len(names) - 1 - k
        col = fs.PAL["blue"] if c.startswith("old") else fs.PAL["red"]
        ax.plot(v["rst_times"], [y + 0.15]*len(v["rst_times"]), "s", color=col, ms=6)
        ax.plot(v["tab_times"], [y - 0.15]*len(v["tab_times"]), "|", color=col, ms=9, mew=1.5)
        ax.plot(v["rst_missing"], [y + 0.15]*len(v["rst_missing"]), "s", mfc="none", mec="k", ms=9)
        ax.plot(v["tab_missing"], [y - 0.15]*len(v["tab_missing"]), "o", mfc="none", mec="k", ms=9)
        if "stop_time" in v:
            ax.plot([v["stop_time"]]*2, [y - 0.4, y + 0.4], **fs.MASK_LINE)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n[1] for n in names][::-1])
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_xlim(-8, 308)
    ax.set_xlabel(r"time of the output, $t/M$")
    ax.plot([], [], "s", color="grey", ms=6, label="restart file")
    ax.plot([], [], "|", color="grey", ms=9, mew=1.5, label="table")
    ax.plot([], [], "s", mfc="none", mec="k", ms=8, label="scheduled, not written")
    ax.plot([], [], color="grey", lw=1.5, alpha=0.4, label="stop")
    ax.set_ylim(-0.6, len(names) + 0.3)
    ax.legend(loc="upper center", ncol=4, fontsize=8)
    fs.save(fig, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--fig")
    ap.add_argument("--replot", help="run directory of an earlier run: only redraw the figure")
    args = ap.parse_args()
    if args.replot:
        res = json.load(open(os.path.join(args.replot, "t2_restart.json")))
        figure(res, args.fig)
        return 0
    run = os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("NRPIC_RUN_DIR is not set (start through runreg.py)")
    res = {"schedule_rst": [50.0*k for k in range(7)], "schedule_tab": [25.0*k for k in range(13)],
           "cases": {}}
    for tag, exe in (("old", args.old), ("new", args.new)):
        d = os.path.join(run, tag + "_u")
        athena(exe, d, ["-i", INPUT], "athena.log")
        res["cases"][tag + "_u"] = dict(collect(d), stop=last_message(d, "athena.log"))
        d = os.path.join(run, tag + "_c")
        athena(exe, d, ["-i", INPUT, "time/nlim=1234"], "athena1.log")
        newest = sorted(glob.glob(os.path.join(d, "rst", "rsch.*.rst")))[-1]
        stop_t = rst_time(newest)
        athena(exe, d, ["-r", newest, "time/nlim=-1"], "athena2.log")
        res["cases"][tag + "_c"] = dict(collect(d), stop=last_message(d, "athena1.log"),
                                        stop_time=stop_t, restart_file=os.path.basename(newest),
                                        stop2=last_message(d, "athena2.log"))
    for tag, exe in (("old", args.old), ("new", args.new)):
        d = os.path.join(run, tag + "_w")
        athena(exe, d, ["-i", INPUT, "particles/dt=0.0001", "particles/traj_dcycle=10000",
                        "particles/hist_dcycle=10000", "-t", "00:00:02"], "athena1.log")
        newest = sorted(glob.glob(os.path.join(d, "rst", "rsch.*.rst")))[-1]
        stop_t = rst_time(newest)
        athena(exe, d, ["-r", newest], "athena2.log")
        res["cases"][tag + "_w"] = dict(collect(d), stop=last_message(d, "athena1.log"),
                                        stop_time=stop_t, restart_file=os.path.basename(newest),
                                        stop2=last_message(d, "athena2.log"))

    def missing(times, sched):
        return [s for s in sched if not any(abs(t - s) < 0.11 for t in times)]

    for c, v in res["cases"].items():
        v["rst_missing"] = missing(v["rst_times"], res["schedule_rst"])
        v["tab_missing"] = missing(v["tab_times"], res["schedule_tab"])
    u, c = res["cases"]["new_u"]["final_state"], res["cases"]["new_c"]["final_state"]
    res["new_c_final_state_equals_new_u"] = (u == c)
    res["new_c_final_state_maxdiff"] = float(np.max(np.abs(np.array(u) - np.array(c))))
    with open(os.path.join(run, "t2_restart.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    for c, v in res["cases"].items():
        print(c, "| stop:", v["stop"], "| stop time", v.get("stop_time"), "| rst", v["rst_times"],
              "| missing rst", v["rst_missing"], "| missing tab", v["tab_missing"])
    print("final state of new_c equals new_u:", res["new_c_final_state_equals_new_u"],
          res["new_c_final_state_maxdiff"])

    if args.fig:
        figure(res, args.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
