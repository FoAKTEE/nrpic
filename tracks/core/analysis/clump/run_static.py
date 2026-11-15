#!/usr/bin/env python3
"""Tests T1 to T4 and T6 of tracks/core/JOURNAL-clump.md: one Gaussian clump with momentum
or spin, constraint residuals at t = 0 with and without the smeared Bowen-York curvature
(problems/tests/clump_static.athinput), on processors. Meant to run as one registered
run:

    harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 8 --purpose "..." \
        -- python3 tracks/core/analysis/clump/run_static.py --set t1

Writes into $NRPIC_RUN_DIR (or --out): ic/<name>.{nrp,json} (particles of
problems/ic/make_ic.py clumps), <label>/ (one AthenaK run each), cases.json (label ->
parameters, history row at t = 0, exit status). The second, identical dump that AthenaK
writes at the end of a run without steps is removed.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
INPUT = os.path.join(WT, "problems", "tests", "clump_static.athinput")
MAKE_IC = os.path.join(WT, "problems", "ic", "make_ic.py")
EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))

MASS, SIGMA = 0.2, 1.0
# particle sets: name -> arguments of make_ic.py clumps
ICS = {
    "latP0.06": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--sampler", "lattice",
                 "--lattice-h", "0.125"],
    "latP0.04": ["--gaussian", "0.2,1,0,0,0,0.04,0,0", "--sampler", "lattice",
                 "--lattice-h", "0.125"],
    "latP0.02": ["--gaussian", "0.2,1,0,0,0,0.02,0,0", "--sampler", "lattice",
                 "--lattice-h", "0.125"],
    "latS0.04": ["--gaussian", "0.2,1,0,0,0,0,0,0,0,0,0.04", "--sampler", "lattice",
                 "--lattice-h", "0.125"],
    "latV0.06": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--sampler", "lattice",
                 "--lattice-h", "0.125", "--clump-momentum-rule", "velocity"],
    "lat4P0.06": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--sampler", "lattice",
                  "--lattice-h", "0.25"],
    "strN1e4": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--N", "10000", "--seed", "1"],
    "strN1e5": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--N", "100000", "--seed", "1"],
    "strN1e6": ["--gaussian", "0.2,1,0,0,0,0.06,0,0", "--N", "1000000", "--seed", "1"],
}
NOFILT = ["particles/nfilter=0", "particles/filter_compensate=false"]


def res(n):
    return [f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}"]


def cases(which):
    """list of (label, particle set, athena arguments, cores weight)"""
    out = []
    if which in ("t1", "all"):
        for n in (32, 64, 128):
            out.append((f"t1_n{n}_none", "latP0.06", res(n)))
            out.append((f"t1_n{n}_curv", "latP0.06", res(n) + ["problem/comp0_p1=0.06"]))
            out.append((f"t1_n{n}_none_f0", "latP0.06", res(n) + NOFILT))
            out.append((f"t1_n{n}_curv_f0", "latP0.06",
                        res(n) + NOFILT + ["problem/comp0_p1=0.06"]))
        out.append(("t1_n64_wrong", "latP0.06", res(64) + ["problem/comp0_p1=-0.06"]))
        for P in ("0.02", "0.04"):
            out.append((f"t1_n128_P{P}_none", f"latP{P}", res(128)))
            out.append((f"t1_n128_P{P}_curv", f"latP{P}", res(128) + [f"problem/comp0_p1={P}"]))
        for N in ("1e4", "1e5", "1e6"):
            out.append((f"t1_n64_str{N}_none", f"strN{N}", res(64)))
            out.append((f"t1_n64_str{N}_curv", f"strN{N}", res(64) + ["@P"]))
    if which in ("t3", "all"):
        for n in (32, 64, 128):
            out.append((f"t3_n{n}_none", "latS0.04", res(n)))
            out.append((f"t3_n{n}_curv", "latS0.04", res(n) + ["problem/comp0_s3=0.04"]))
    if which in ("t4", "all"):
        for n in (32, 64, 128):
            out.append((f"t4_n{n}_none", "latV0.06", res(n)))
            out.append((f"t4_n{n}_curv", "latV0.06", res(n) + ["problem/comp0_p1=0.06"]))
    if which in ("t6", "all"):
        ev = res(64) + ["time/nlim=-1", "time/tlim=2.0"]
        out.append(("t6_none", "lat4P0.06", ev))
        out.append(("t6_curv", "lat4P0.06", ev + ["problem/comp0_p1=0.06"]))
    return out


def hst_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                rows.append([float(v) for v in line.split()])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="all", choices=["t1", "t3", "t4", "t6", "all"])
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if not a.out:
        ap.error("no output directory: run through nrpic-run or give --out")
    os.makedirs(os.path.join(a.out, "ic"), exist_ok=True)
    todo = cases(a.set)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")

    # particles
    meta = {}
    for name in sorted({c[1] for c in todo}):
        subprocess.run([sys.executable, MAKE_IC, "clumps", *ICS[name], "--out",
                        os.path.join(a.out, "ic"), "--prefix", name], check=True, env=env,
                       stdout=subprocess.DEVNULL)
        with open(os.path.join(a.out, "ic", name + ".json")) as f:
            meta[name] = json.load(f)

    def run(case):
        label, ic, args = case
        d = os.path.join(a.out, label)
        os.makedirs(d, exist_ok=True)
        link = os.path.join(d, "particles.nrp")
        if not os.path.exists(link):
            os.symlink(os.path.join("..", "ic", ic + ".nrp"), link)
        P = meta[ic]["athenak"]["problem"]
        # "@P": the momentum the particles of this set carry (all three components)
        full = []
        for s in args:
            if s == "@P":
                full += [f"problem/comp0_p{c}={P[f'comp0_p{c}']!r}" for c in (1, 2, 3)]
            else:
                full.append(s)
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", INPUT, "-d", d, *full], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT, env=env).returncode
        rows = hst_rows(os.path.join(d, "clump.z4c.user.hst")) if st == 0 else []
        if "time/nlim=-1" not in full:
            for v in ("con",):
                dup = os.path.join(d, "bin", f"clump.{v}.00001.bin")
                if os.path.exists(dup):
                    os.remove(dup)
        return label, dict(ic=ic, args=full, status=st, wall=time.time() - t0,
                           hst0=rows[0] if rows else None, particles=meta[ic]["particles"],
                           problem=P)

    with ThreadPoolExecutor(a.jobs) as ex:
        results = dict(ex.map(run, todo))
    with open(os.path.join(a.out, f"cases_{a.set}.json"), "w") as f:
        json.dump(dict(exe=EXE, input=INPUT, cases=results), f, indent=1)
    bad = [k for k, v in results.items() if v["status"] != 0]
    for k, v in results.items():
        h = v["hst0"]
        print(f"{k:24s} status {v['status']}  wall {v['wall']:6.1f} s  "
              + (f"H-norm2 {h[3]:.6e}  M-norm2 {h[4]:.6e}  Mx {h[6]:.6e}" if h else ""))
    if bad:
        print("FAILED:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
