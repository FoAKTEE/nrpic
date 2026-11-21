#!/usr/bin/env python3
"""Tests L1 and L2 of the work package "gauge": the expanding ball with the old and the
new lapse (tracks/core/JOURNAL-gauge.md, entry 1).

Initial data from scratch/core/id/ic_ball (made by problems/ic/make_ball.py when
missing, as in tracks/core/analysis/id/test2_runs.py); every run is registered through
grun.py with tag g-<case> (processors) or gc-<case> (--gpu, one card).

    ball_runs.py [--only SUBSTRING[,SUBSTRING]] [--exact] [--jobs 4] [--gpu] [--dry]
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball"
INPUT = os.path.join(WT, "problems/ball/ball_leak.athinput")
# card executable of this package, copied from .work/build_gpu when it was built, and the
# commit its source equals
GPU_EXE = os.environ.get("GAUGE_GPU_EXE",
                         "/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_gpu_b4430da")
SRC_COMMIT = os.environ.get("GAUGE_SRC_COMMIT", "b4430da")

# lapse: old 1+log (leak off), relaxation times T = 1/lapse_leak
LAPSE = {
    "mp": ["z4c/lapse_leak=0.0"],
    "leak0125": ["z4c/lapse_leak=8.0"],
    "leak025": ["z4c/lapse_leak=4.0"],
    "leak05": ["z4c/lapse_leak=2.0"],
    "leak1": ["z4c/lapse_leak=1.0"],
    "leak2": ["z4c/lapse_leak=0.5"],
    "leak4": ["z4c/lapse_leak=0.25"],
    # conformal-time lapse of wave 1 (reference of JOURNAL-id.md)
    "ct": ["z4c/lapse_leak=0.0", "z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333"],
}
SHARP = ["--Rb", "10"]
EDGE2 = ["--Rb", "10", "--edge", "2"]
BOUND = ["--Rb", "5", "--e0", "0.16", "--RE", "10"]

# name: (cells, half-width, ball arguments, lapse, tlim, extra)
CASES = {}
for lap in ("mp", "leak1", "leak2"):
    for n in (64, 128):
        CASES[f"{lap}-n{n:03d}"] = (n, 32.0, SHARP, lap, 10.0, [])
        CASES[f"{lap}-edge2-n{n:03d}"] = (n, 32.0, EDGE2, lap, 10.0, [])
CASES["leak05-n064"] = (64, 32.0, SHARP, "leak05", 10.0, [])
CASES["leak025-n064"] = (64, 32.0, SHARP, "leak025", 10.0, [])
CASES["leak0125-n064"] = (64, 32.0, SHARP, "leak0125", 10.0, [])
CASES["leak4-n064"] = (64, 32.0, SHARP, "leak4", 10.0, [])
CASES["leak1-n256"] = (256, 32.0, SHARP, "leak1", 10.0, [])
# bound ball to its turnaround
for lap in ("mp", "ct", "leak0125", "leak025", "leak05", "leak1", "leak2"):
    CASES[f"bound-{lap}-n080"] = (80, 20.0, BOUND, lap, 12.0, [])
    CASES[f"bound-{lap}-n160"] = (160, 20.0, BOUND, lap, 12.0, [])


def ic_stem(ball, h):
    tag = "sharp"
    if "--edge" in ball:
        tag = "edge" + ball[ball.index("--edge") + 1]
    if "--e0" in ball:
        tag = "bound"
    return f"t2_{tag}_h" + f"{h:g}".replace(".", "p")


def make_ic(case):
    n, half, ball = case[0], case[1], case[2]
    h = 2.0 * half / n
    stem = ic_stem(ball, h)
    if not os.path.exists(os.path.join(IC, stem + ".json")):
        cmd = [sys.executable, os.path.join(WT, "problems/ic/make_ball.py"), *ball,
               "--h", repr(h), "--out", IC, "--prefix", stem]
        subprocess.run(cmd, check=True, capture_output=True)
    return stem


def run(name, gpu=False, dry=False):
    n, half, ball, lapse, tlim, extra = CASES[name]
    stem = os.path.join(IC, make_ic(CASES[name]))
    with open(stem + ".json") as f:
        meta = json.load(f)
    dx = 2.0 * half / n
    mb = {80: 40, 160: 40, 320: 64}.get(n, 64 if n >= 192 else 32)
    dcyc = max(1, int(round(1.0 / dx)))            # trajectory records every 0.25 M
    cmd = [sys.executable, os.path.join(HERE, "grun.py"),
           "--purpose", f"expanding ball with the old and the new lapse: {name} (cells {n}, "
                        f"half-width {half:g}, lapse {lapse}, ball {' '.join(ball)})",
           "--tag", f"{'gc' if gpu else 'g'}-{name}",
           "--inputs", stem + ".nrp", stem + ".tab", stem + ".json"]
    if gpu:
        cmd += ["--gpu", "--exe", GPU_EXE, "--source-commit", SRC_COMMIT,
                "--time", "00:20:00"]
    elif os.environ.get("GAUGE_CPU_EXE"):
        cmd += ["--exe", os.environ["GAUGE_CPU_EXE"], "--source-commit", SRC_COMMIT]
    cmd += ["--athinput", INPUT,
            f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
            f"mesh/x1min={-half}", f"mesh/x1max={half}", f"mesh/x2min={-half}",
            f"mesh/x2max={half}", f"mesh/x3min={-half}", f"mesh/x3max={half}",
            f"meshblock/nx1={mb}", f"meshblock/nx2={mb}", f"meshblock/nx3={mb}",
            f"time/tlim={tlim}", f"particles/traj_dcycle={dcyc}",
            f"particles/traj_ntrack={meta['traj_ntrack']}",
            f"particles/particle_file={stem}.nrp", f"problem/comp0_file={stem}.tab",
            "problem/shift=zero"] + LAPSE[lapse] + list(extra)
    if dry:
        print(" ".join(cmd))
        return name, 0, ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    return name, r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--exact", action="store_true", help="--only names are exact")
    a = ap.parse_args()
    sel = a.only.split(",")
    names = [k for k in CASES if (k in sel if a.exact else any(s in k for s in sel))]
    os.makedirs(IC, exist_ok=True)
    for k in names:
        make_ic(CASES[k])
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for res in ex.map(lambda k: run(k, a.gpu, a.dry), names):
            print(*res, flush=True)


if __name__ == "__main__":
    main()
