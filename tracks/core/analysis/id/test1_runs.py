#!/usr/bin/env python3
"""Test 1 of the work package "id": constraint residuals at the start (no step taken).

Generates the initial data of each case with problems/ic/make_ball.py and starts the
registered runs through nrun.py (tag t1-<case>).  Cases up to 128 cells per direction
run on processors, several at a time; larger ones on a card, one after the other.

    test1_runs.py [--only SUBSTRING] [--cpu-jobs 6] [--dry]

Ball: marginally bound, R_b = 10 M, mesh half-width 32 M.  q = dx/h is the number of
lattice sites per cell and direction.
"""
import argparse
import concurrent.futures as cf
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball"
HALF = 32.0

# (name, cells per direction, q = dx/h, edge half-width, lattice shift in units of h,
#  extra arguments of the run)
CASES = [
    # sharp surface, one site per cell: resolution sequence
    ("sharp-n064-q1", 64, 1.0, 0.0, 0.0, []),
    ("sharp-n096-q1", 96, 1.0, 0.0, 0.0, []),
    ("sharp-n128-q1", 128, 1.0, 0.0, 0.0, []),
    ("sharp-n192-q1", 192, 1.0, 0.0, 0.0, []),
    ("sharp-n256-q1", 256, 1.0, 0.0, 0.0, []),
    # particle number at fixed mesh, lattice dividing the cell
    ("sharp-n128-q2", 128, 2.0, 0.0, 0.0, []),
    ("sharp-n128-q4", 128, 4.0, 0.0, 0.0, []),
    # lattices that do not match the mesh (one binomial pass, as in all cases above)
    ("sharp-n128-q1p25", 128, 1.25, 0.0, 0.0, []),
    ("sharp-n128-q2p25", 128, 2.25, 0.0, 0.0, []),
    ("sharp-n128-q3p25", 128, 3.25, 0.0, 0.0, []),
    ("sharp-n128-q1p5", 128, 1.5, 0.0, 0.0, []),
    ("sharp-n128-q1-s0p25", 128, 1.0, 0.0, 0.25, []),
    ("sharp-n064-q1p25", 64, 1.25, 0.0, 0.0, []),
    ("sharp-n256-q1p25", 256, 1.25, 0.0, 0.0, []),
    # ... and without the binomial pass
    ("sharp-n128-q1p25-nf0", 128, 1.25, 0.0, 0.0, ["particles/nfilter=0"]),
    ("sharp-n128-q1p5-nf0", 128, 1.5, 0.0, 0.0, ["particles/nfilter=0"]),
    ("sharp-n128-q1-nf0", 128, 1.0, 0.0, 0.0, ["particles/nfilter=0"]),
    # smooth edge of half-width 2 M and 1 M
    ("edge2-n064-q1", 64, 1.0, 2.0, 0.0, []),
    ("edge2-n128-q1", 128, 1.0, 2.0, 0.0, []),
    ("edge2-n256-q1", 256, 1.0, 2.0, 0.0, []),
    ("edge2-n128-q2", 128, 2.0, 2.0, 0.0, []),
    ("edge1-n064-q1", 64, 1.0, 1.0, 0.0, []),
    ("edge1-n128-q1", 128, 1.0, 1.0, 0.0, []),
    ("edge1-n256-q1", 256, 1.0, 1.0, 0.0, []),
]


def stem(name):
    return "t1_" + name.replace("-", "_")


def make_ic(case):
    name, n, q, edge, shift, _ = case
    h = 2.0 * HALF / n / q
    cmd = [sys.executable, os.path.join(WT, "problems/ic/make_ball.py"), "--Rb", "10",
           "--h", repr(h), "--edge", repr(edge), "--shift", repr(shift), "--tracers", "",
           "--sample", "0", "--out", IC, "--prefix", stem(name)]
    subprocess.run(cmd, check=True, capture_output=True)


def run(case, dry=False):
    name, n, q, edge, shift, extra = case
    s = os.path.join(IC, stem(name))
    gpu = n > 128
    mb = 64 if n >= 192 else 32
    cmd = [sys.executable, os.path.join(HERE, "nrun.py"),
           "--purpose", f"test 1, constraints at the start: {name} (cells {n}, q = {q:g}, "
                        f"edge {edge:g}, lattice shift {shift:g})",
           "--tag", "t1-" + name, "--inputs", s + ".nrp", s + ".tab", s + ".json"]
    if gpu:
        cmd += ["--gpu", "--exe", os.path.join(WT, ".work/build_gpu/src/athena"),
                "--time", "00:10:00"]
    cmd += ["--athinput", os.path.join(WT, "problems/ball/ball.athinput"),
            f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
            f"meshblock/nx1={mb}", f"meshblock/nx2={mb}", f"meshblock/nx3={mb}",
            "time/nlim=0", "particles/field_time1=1.0e9", "particles/traj_dcycle=0",
            "particles/snap_dt=-1.0", f"particles/particle_file={s}.nrp",
            f"problem/comp0_file={s}.tab"] + list(extra)
    if dry:
        print(" ".join(cmd))
        return name, 0, ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    return name, r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--cpu-jobs", type=int, default=6)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    cases = [c for c in CASES if a.only in c[0]]
    os.makedirs(IC, exist_ok=True)
    for c in cases:
        make_ic(c)
    cpu = [c for c in cases if c[1] <= 128]
    gpu = [c for c in cases if c[1] > 128]
    with cf.ThreadPoolExecutor(max_workers=a.cpu_jobs) as ex:
        futs = [ex.submit(run, c, a.dry) for c in cpu]
        gfut = ex.submit(lambda: [run(c, a.dry) for c in gpu])
        for f in futs:
            print(*f.result(), flush=True)
        for res in gfut.result():
            print(*res, flush=True)


if __name__ == "__main__":
    main()
