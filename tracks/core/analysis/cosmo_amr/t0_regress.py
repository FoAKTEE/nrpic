#!/usr/bin/env python3
"""T0 of the work package cosmo-amr: with the new options absent, the executable of this
branch reproduces the release byte for byte.

    t0_regress.py --rel REL_EXE --new NEW_EXE --out DIR [--cores N] [--cases a,b,...]

Cases geo, boris, dep, east, os are those of tracks/core/tools/regress_relativistic.py
(same inputs, arguments and initial data under scratch/core/regress/ic/); flrw is the
homogeneous universe of problems/cosmo/flrw.athinput (8 cycles); punc is a unit puncture
on a statically refined periodic mesh with the horizon finder and tracers (2 cycles).
Every output file of the two runs is compared byte by byte; for restart files the
number of differing bytes is reported (36 never-set header bytes may differ)."""
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys

import amrlib as A

IC = "/data/haiyangw/nrpic/scratch/core/regress/ic"
OS = "os_R5_lattice_N2176_s1"
PER = ["mesh/ix%d_bc=periodic" % d for d in (1, 2, 3)] + \
      ["mesh/ox%d_bc=periodic" % d for d in (1, 2, 3)]
CASES = {
    "geo": dict(inp="problems/kerr/geodesic.athinput", files=[],
                args=["time/tlim=20.0", "particles/hist_dcycle=100"]),
    "boris": dict(inp="problems/kerr/geodesic.athinput", files=[],
                  args=["time/tlim=20.0", "particles/hist_dcycle=100",
                        "particles/pusher=boris", "particles/metric=lattice"]),
    "dep": dict(inp="problems/tests/deposit_smr.athinput", files=[IC + "/random.nrp"],
                args=["time/tlim=2.0", "particles/deposit_max_level=1"]),
    "east": dict(inp="problems/cosmo/east.athinput",
                 files=[IC + "/east16/particles.nrp", IC + "/east16/fields.bin"],
                 args=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                       "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=20",
                       "particles/snap_dt=0.2", "particles/traj_ntrack=46"]),
    "os": dict(inp="problems/os/os_smr_dev.athinput",
               files=[IC + "/os/%s.nrp" % OS, IC + "/os/%s.tab" % OS],
               args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=16",
                     "meshblock/nx2=16", "meshblock/nx3=16", "time/nlim=3",
                     "particles/particle_file=%s.nrp" % OS,
                     "problem/comp0_file=%s.tab" % OS, "particles/snap_dt=0.05",
                     "output2/dt=0.1"]),
    "flrw": dict(inp="problems/cosmo/flrw.athinput", files=["@lattice32"],
                 args=["time/nlim=8"]),
    "punc": dict(inp="problems/cosmo_amr/punc_box16.athinput", files=[],
                 args=["time/nlim=2", "fastflow/find_every=1"] + PER),
}
SKIP = ("run.log",)


def run(exe, case, d, out):
    c = CASES[case]
    os.makedirs(d, exist_ok=True)
    deck = os.path.join(d, os.path.basename(c["inp"]))
    shutil.copy(os.path.join(A.ROOT, c["inp"]), deck)
    for f in c["files"]:
        if f == "@lattice32":
            f = os.path.join(out, "ic_lattice32", "particles.nrp")
        dst = os.path.join(d, os.path.basename(f))
        if not os.path.exists(dst):
            os.symlink(f, dst)
    with open(os.path.join(d, "run.log"), "w") as log:
        p = subprocess.run([exe, "-i", os.path.basename(deck)] + c["args"], cwd=d,
                           stdout=log, stderr=subprocess.STDOUT)
    return p.returncode


def compare(da, db):
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    same, differ, rst = [], [], {}
    for n in sorted(names):
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if n in SKIP or os.path.islink(fa):
            continue
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        elif n.endswith(".rst"):
            a, b = open(fa, "rb").read(), open(fb, "rb").read()
            nd = sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
            first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), -1)
            rst[n] = dict(differing_bytes=nd, first_offset=first, size=len(a))
        else:
            differ.append(n)
    return same, differ, rst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rel", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--cases", default="geo,boris,dep,east,os,flrw,punc")
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    a.new, a.rel = os.path.abspath(a.new), os.path.abspath(a.rel)
    os.makedirs(a.out, exist_ok=True)
    cases = a.cases.split(",")
    if "flrw" in cases:
        subprocess.run([sys.executable, os.path.join(A.ROOT, "cosmo/ic/make_lattice.py"),
                        "--n", "32", "--L", "4", "--out",
                        os.path.join(a.out, "ic_lattice32")], check=True,
                       stdout=subprocess.DEVNULL)
    import concurrent.futures
    jobs = [(exe, c, os.path.join(a.out, c, lab), a.out)
            for c in cases for lab, exe in (("rel", a.rel), ("new", a.new))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.cores) as ex:
        rcs = list(ex.map(lambda j: run(*j), jobs))
    report, bad = {}, 0
    for n, c in enumerate(cases):
        same, differ, rst = compare(os.path.join(a.out, c, "rel"),
                                    os.path.join(a.out, c, "new"))
        report[c] = dict(exit_rel=rcs[2*n], exit_new=rcs[2*n+1], identical=same,
                         differ=differ, restart_files=rst)
        bad += len(differ) + (0 if same else 1) + (rcs[2*n] != rcs[2*n+1])
        print("%-6s exit %d/%d  identical files: %3d  differing: %s  restart: %s"
              % (c, rcs[2*n], rcs[2*n+1], len(same), differ if differ else "none",
                 {k: v["differing_bytes"] for k, v in rst.items()} if rst else "none"))
    report["executables"] = dict(rel=a.rel, new=a.new, rel_sha256=A.sha256(a.rel),
                                 new_sha256=A.sha256(a.new))
    with open(os.path.join(a.out, "t0_report.json"), "w") as f:
        json.dump(report, f, indent=1)
        f.write("\n")
    print("T0:", "PASS" if bad == 0 else "FAIL (%d)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
