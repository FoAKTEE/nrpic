#!/usr/bin/env python3
"""Tests TB of tracks/core/JOURNAL-clump2.md: one equilibrium cluster (y_c = 0.819) with a
bulk velocity, constraint residuals at t = 0 with and without the curvature of the boost
table and the correction of psi (problems/tests/clump_table_static.athinput), on
processors. Meant to run as one registered run:

    harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 8 --purpose "..." \
        -- python3 tracks/core/analysis/clump2/run_boost_static.py

Writes into $NRPIC_RUN_DIR (or --out): ic/<name>.{nrp,json} and tables (particles of
problems/ic/make_ic.py boosted), <label>/ (one AthenaK run each), cases.json (label ->
particle set, arguments, history row at t = 0, exit status). The second, identical dump
that AthenaK writes at the end of a run without steps is removed.
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
INPUT = os.path.join(WT, "problems", "tests", "clump_table_static.athinput")
MAKE_IC = os.path.join(WT, "problems", "ic", "make_ic.py")
EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))

YC = "0.819"
QUIET = ["--sampler", "quiet", "--lattice-h", "0.25"]
# particle sets: name -> arguments of make_ic.py boosted
ICS = {
    "q0": ["--cluster", f"{YC},1,0,0,0,0,0,0", *QUIET],
    "q0.1": ["--cluster", f"{YC},1,0,0,0,0.1,0,0", *QUIET],
    "q0.3": ["--cluster", f"{YC},1,0,0,0,0.3,0,0", *QUIET],
    "s0": ["--cluster", f"{YC},1,0,0,0,0,0,0", "--N", "10000", "--seed", "1"],
    "s0.3": ["--cluster", f"{YC},1,0,0,0,0.3,0,0", "--N", "10000", "--seed", "1"],
}
# extra dumps for the comparison of the fields with the reference (TB5)
FIELDS = """
<output4>
file_type = bin
variable  = adm
dt        = 1.0

<output5>
file_type = bin
variable  = z4c
dt        = 1.0
"""


def res(n):
    return [f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}"]


def cases(ns):
    """list of (label, particle set, tables of, athena arguments, extra dumps)"""
    out = []
    for n in ns:
        out.append((f"q0_n{n}", "q0", "q0.3", res(n), False))
        for v in ("0.1", "0.3"):
            ic = f"q{v}"
            out.append((f"q{v}_n{n}_none", ic, ic, res(n), False))
            out.append((f"q{v}_n{n}_curv", ic, ic, res(n) + ["@P"], False))
            out.append((f"q{v}_n{n}_corr", ic, ic,
                        res(n) + ["@P", "problem/comp0_corr=table",
                                  "problem/comp0_boost_shift=true"],
                        n == 64 and v == "0.3"))
    if 64 in ns:
        out.append(("s0_n64", "s0", "s0.3", res(64), False))
        out.append(("s0.3_n64_none", "s0.3", "s0.3", res(64), False))
        out.append(("s0.3_n64_curv", "s0.3", "s0.3", res(64) + ["@P"], False))
        out.append(("s0.3_n64_corr", "s0.3", "s0.3",
                    res(64) + ["@P", "problem/comp0_corr=table"], False))
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
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--n", default="32,64,128")
    a = ap.parse_args()
    if not a.out:
        ap.error("no output directory: run through nrpic-run or give --out")
    icd = os.path.join(a.out, "ic")
    os.makedirs(icd, exist_ok=True)
    todo = cases([int(v) for v in a.n.split(",")])
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    with open(INPUT) as f:
        template = f.read()

    meta = {}
    for name in sorted({c[1] for c in todo} | {c[2] for c in todo}):
        subprocess.run([sys.executable, MAKE_IC, "boosted", *ICS[name], "--out", icd,
                        "--prefix", name], check=True, env=env, stdout=subprocess.DEVNULL)
        with open(os.path.join(icd, name + ".json")) as f:
            meta[name] = json.load(f)

    def run(case):
        label, ic, tabs, args, fields = case
        d = os.path.join(a.out, label)
        os.makedirs(d, exist_ok=True)
        links = {"particles.nrp": ic + ".nrp", "cluster_c0.tab": tabs + "_c0.tab",
                 "cluster_c0.bst": tabs + "_c0.bst",
                 "cluster_c0_corr.tab": tabs + "_c0_corr.tab"}
        for dst, src in links.items():
            link = os.path.join(d, dst)
            if not os.path.lexists(link):
                os.symlink(os.path.join("..", "ic", src), link)
        inp = os.path.join(d, "input.athinput")
        with open(inp, "w") as f:
            f.write(template + (FIELDS if fields else ""))
        P = meta[ic]["athenak"]["problem"]
        full = []
        for s in args:
            if s == "@P":       # the momentum the particles of this set carry
                full += [f"problem/comp0_p{c}={P[f'comp0_p{c}']!r}" for c in (1, 2, 3)]
            else:
                full.append(s)
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", inp, "-d", d, *full], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT, env=env).returncode
        rows = hst_rows(os.path.join(d, "clump.z4c.user.hst")) if st == 0 else []
        bind = os.path.join(d, "bin")
        if os.path.isdir(bind):
            for fn in sorted(os.listdir(bind)):
                if fn.endswith(".00001.bin"):
                    os.remove(os.path.join(bind, fn))
        return label, dict(ic=ic, tables=tabs, args=full, status=st,
                           wall=time.time() - t0, hst0=rows[0] if rows else None)

    # the largest meshes first, so that the pool stays full
    todo.sort(key=lambda c: -int(c[0].split("_n")[1].split("_")[0]))
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        results = dict(ex.map(run, todo))
    with open(os.path.join(a.out, "cases.json"), "w") as f:
        json.dump(dict(exe=EXE, input=INPUT, ic=meta, cases=results), f, indent=1)
    bad = [k for k, v in results.items() if v["status"] != 0]
    for k, v in sorted(results.items()):
        h = v["hst0"]
        print(f"{k:22s} status {v['status']} wall {v['wall']:6.1f} s"
              + (f"  H-norm2 {h[3]:.6e} M-norm2 {h[4]:.6e}" if h else ""))
    print("FAILED: " + ", ".join(bad) if bad else "all cases ran")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
