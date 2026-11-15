#!/usr/bin/env python3
"""Tests 2 and 3 of the work package "id": evolution of the expanding ball against the
exact solution, for several gauges, resolutions and settings.

Generates the initial data with problems/ic/make_ball.py (with exterior tracers and a
sample of 2000 tracked ball particles) and starts the registered card runs through
nrun.py (tag t2-<case> or t3-<case>), two at a time.

    test2_runs.py [--only SUBSTRING] [--jobs 2] [--dry]
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

GAUGE = {
    # 1+log with advection, Gamma-driver: the block of problems/ball/ball.athinput
    "mp": [],
    # d_t alpha = beta^i d_i alpha - (1/3) alpha^2 K, same Gamma-driver
    "ct": ["z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333"],
    # ... without advection and with the shift held at zero (gauge of cosmo/)
    "ct0": ["z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333",
            "z4c/lapse_advect=0.0", "z4c/shift_Gamma=0.0", "z4c/shift_eta=0.0",
            "z4c/shift_advect=0.0"],
    # lapse and shift held at their start values: with lapse 1 and shift 0 the slices of
    # constant dust proper time and the comoving coordinates of the exact solution
    "gs0": ["z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.0", "z4c/lapse_advect=0.0",
            "z4c/shift_Gamma=0.0", "z4c/shift_eta=0.0", "z4c/shift_advect=0.0"],
    # 1+log without advection, shift held at zero
    "mp0": ["z4c/lapse_advect=0.0", "z4c/shift_Gamma=0.0", "z4c/shift_eta=0.0",
            "z4c/shift_advect=0.0"],
}

# name: (tag prefix, cells, half-width, ball arguments, q, gauge, start shift, tlim, extra)
SHARP = ["--Rb", "10"]
EDGE2 = ["--Rb", "10", "--edge", "2"]
BOUND = ["--Rb", "5", "--e0", "0.16", "--RE", "10"]
EXT = ["particles/source_density=true", "particles/source_extrap=true"]
PROD = ["particles/source_density=true", "particles/source_extrap=true",
        "particles/deposit_shape=pcs", "particles/deposit_comp_c=0.1666666666666667",
        "particles/deposit_comp_c2=0.4666666666666667", "particles/interp=bspline",
        "particles/nfilter=0"]
CASES = {
    "mp-n064": ("t2", 64, 32.0, SHARP, 1, "mp", "zero", 10.0, []),
    "mp-n128": ("t2", 128, 32.0, SHARP, 1, "mp", "zero", 10.0, []),
    "mp-n256": ("t2", 256, 32.0, SHARP, 1, "mp", "zero", 10.0, []),
    "mppg-n128": ("t2", 128, 32.0, SHARP, 1, "mp", "table", 10.0, []),
    "ct-n064": ("t2", 64, 32.0, SHARP, 1, "ct", "zero", 10.0, []),
    "ct-n128": ("t2", 128, 32.0, SHARP, 1, "ct", "zero", 10.0, []),
    "ct-n256": ("t2", 256, 32.0, SHARP, 1, "ct", "zero", 10.0, []),
    "ct0-n128": ("t2", 128, 32.0, SHARP, 1, "ct0", "zero", 10.0, []),
    "mp-edge2-n064": ("t2", 64, 32.0, EDGE2, 1, "mp", "zero", 10.0, []),
    "mp-edge2-n128": ("t2", 128, 32.0, EDGE2, 1, "mp", "zero", 10.0, []),
    "mp-edge2-n256": ("t2", 256, 32.0, EDGE2, 1, "mp", "zero", 10.0, []),
    "mp-ext-n128": ("t2", 128, 32.0, SHARP, 1, "mp", "zero", 10.0,
                    ["particles/source_density=true", "particles/source_extrap=true"]),
    "mp-nf0-n128": ("t2", 128, 32.0, SHARP, 1, "mp", "zero", 10.0, ["particles/nfilter=0"]),
    "mp-q2-n128": ("t2", 128, 32.0, SHARP, 2, "mp", "zero", 10.0, []),
    "mp-big-n192": ("t2", 192, 48.0, SHARP, 1, "mp", "zero", 10.0, []),
    # smooth edge with the conformal-time lapse
    "ct-edge2-n064": ("t2", 64, 32.0, EDGE2, 1, "ct", "zero", 10.0, []),
    "ct-edge2-n128": ("t2", 128, 32.0, EDGE2, 1, "ct", "zero", 10.0, []),
    "ct-edge2-n256": ("t2", 256, 32.0, EDGE2, 1, "ct", "zero", 10.0, []),
    "ct-edge2-big-n192": ("t2", 192, 48.0, EDGE2, 1, "ct", "zero", 10.0, []),
    # ... and with the sources extrapolated to the middle of the step
    "ct-edge2-ext-n064": ("t2", 64, 32.0, EDGE2, 1, "ct", "zero", 10.0,
                          ["particles/source_density=true", "particles/source_extrap=true"]),
    "ct-edge2-ext-n128": ("t2", 128, 32.0, EDGE2, 1, "ct", "zero", 10.0,
                          ["particles/source_density=true", "particles/source_extrap=true"]),
    "ct-edge2-ext-n256": ("t2", 256, 32.0, EDGE2, 1, "ct", "zero", 10.0,
                          ["particles/source_density=true", "particles/source_extrap=true"]),
    # ... and with the production configuration of cosmo/README.md for lattice starts
    "ct-edge2-prod-n128": ("t2", 128, 32.0, EDGE2, 1, "ct", "zero", 10.0, PROD),
    "ct-edge2-prod-n256": ("t2", 256, 32.0, EDGE2, 1, "ct", "zero", 10.0, PROD),
    # ... and with lapse and shift held fixed (synchronous comoving coordinates)
    "gs0-edge2-ext-n128": ("t2", 128, 32.0, EDGE2, 1, "gs0", "zero", 10.0, EXT),
    "gs0-edge2-ext-n256": ("t2", 256, 32.0, EDGE2, 1, "gs0", "zero", 10.0, EXT),
    "gs0-ext-n128": ("t2", 128, 32.0, SHARP, 1, "gs0", "zero", 10.0, EXT),
    # test 3: bound ball that turns around (R_b = 5 M, a_max = 1.25, tau = 9.54 M)
    "bound-ct-n080": ("t3", 80, 20.0, BOUND, 1, "ct", "zero", 12.0, []),
    "bound-ct-n160": ("t3", 160, 20.0, BOUND, 1, "ct", "zero", 12.0, []),
    "bound-ct-n320": ("t3", 320, 20.0, BOUND, 1, "ct", "zero", 12.0, []),
    "bound-mp-n160": ("t3", 160, 20.0, BOUND, 1, "mp", "zero", 12.0, []),
    "bound-gs0-n160": ("t3", 160, 20.0, BOUND, 1, "gs0", "zero", 12.0, EXT),
}


def ic_stem(ball, h):
    tag = "sharp"
    if "--edge" in ball:
        tag = "edge" + ball[ball.index("--edge") + 1]
    if "--e0" in ball:
        tag = "bound"
    return f"t2_{tag}_h" + f"{h:g}".replace(".", "p")


def make_ic(case):
    _, n, half, ball, q, _, _, _, _ = case
    h = 2.0 * half / n / q
    stem = ic_stem(ball, h)
    if not os.path.exists(os.path.join(IC, stem + ".json")):
        cmd = [sys.executable, os.path.join(WT, "problems/ic/make_ball.py"), *ball,
               "--h", repr(h), "--out", IC, "--prefix", stem]
        subprocess.run(cmd, check=True, capture_output=True)
    return stem


def run(name, dry=False):
    case = CASES[name]
    pre, n, half, ball, q, gauge, shift, tlim, extra = case
    stem = os.path.join(IC, make_ic(case))
    with open(stem + ".json") as f:
        meta = json.load(f)
    dx = 2.0 * half / n
    mb = {80: 40, 160: 40, 320: 64}.get(n, 64 if n >= 192 else 32)
    dcyc = max(1, int(round(1.0 / dx)))            # trajectory records every 0.25 M
    cmd = [sys.executable, os.path.join(HERE, "nrun.py"),
           "--purpose", f"evolution of the expanding ball against the exact solution: {name} "
                        f"(cells {n}, half-width {half:g}, gauge {gauge}, start shift {shift}, "
                        f"q = {q}, ball {' '.join(ball)}, extra {' '.join(extra) or 'none'})",
           "--tag", f"{pre}-{name}", "--inputs", stem + ".nrp", stem + ".tab", stem + ".json",
           "--gpu", "--exe", os.path.join(WT, ".work/build_gpu/src/athena"),
           "--time", "00:40:00",
           "--athinput", os.path.join(WT, "problems/ball/ball.athinput"),
           f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
           f"mesh/x1min={-half}", f"mesh/x1max={half}", f"mesh/x2min={-half}",
           f"mesh/x2max={half}", f"mesh/x3min={-half}", f"mesh/x3max={half}",
           f"meshblock/nx1={mb}", f"meshblock/nx2={mb}", f"meshblock/nx3={mb}",
           f"time/tlim={tlim}", f"particles/traj_dcycle={dcyc}",
           f"particles/traj_ntrack={meta['traj_ntrack']}",
           f"particles/particle_file={stem}.nrp", f"problem/comp0_file={stem}.tab",
           f"problem/shift={shift}"] + GAUGE[gauge] + list(extra)
    if dry:
        print(" ".join(cmd))
        return name, 0, ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    return name, r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    names = [k for k in CASES if any(s in k for s in a.only.split(","))]
    os.makedirs(IC, exist_ok=True)
    for k in names:
        make_ic(CASES[k])
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for res in ex.map(lambda k: run(k, a.dry), names):
            print(*res, flush=True)


if __name__ == "__main__":
    main()
