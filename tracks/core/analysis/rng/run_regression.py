#!/usr/bin/env python3
"""Regression of the existing behaviour: the executable with the random-number
interface against the executable built from the unmodified source.

Each case is an existing input file, run for a short time by the baseline executable
(twice, to show that the run itself is reproducible) and by the new executable, with
identical arguments; every output file except the log is compared byte by byte.

  c1  problems/cluster_test/cluster_analytic.athinput   analytic metric, 2000 particles
  c2  problems/tests/mesh_static.athinput               mesh metric, deposit, filter
  c3  problems/cluster_test/cluster_mesh.athinput       refined mesh, deposit, excision
  c4  problems/cosmo/flrw.athinput                      Z4c with particle sources
  c5  problems/tests/rng_kick_mesh.athinput, kick off   restart files, removal

Usage: run_regression.py --base ATHENA --new ATHENA [--cases c1,c2,...]
Writes summary.json in the current directory; exit status 0 unless a file differs
between the baseline and the new executable that is identical between the two runs of
the baseline (verdict "differs"). A case whose baseline is not reproducible run to run
is reported as such and gives no verdict.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def run(exe, rundir, args):
    os.makedirs(rundir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        proc = subprocess.run([exe] + args + ["-d", rundir], cwd=rundir, stdout=log,
                              stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {proc.returncode}")
    return round(time.time() - t0, 2)


def files(top):
    out = []
    for root, _, names in os.walk(top):
        for nm in names:
            if nm == "athena.log":
                continue
            out.append(os.path.relpath(os.path.join(root, nm), top))
    return sorted(out)


def compare(a, b):
    fa, fb = files(a), files(b)
    differ = [f for f in fa if f not in fb or not filecmp.cmp(os.path.join(a, f),
                                                              os.path.join(b, f),
                                                              shallow=False)]
    differ += [f for f in fb if f not in fa]
    return {"files": len(fa), "differing": differ}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--cases", default="c1,c2,c3,c4,c5")
    args = ap.parse_args()
    top = os.getcwd()
    base = os.path.abspath(args.base)
    new = os.path.abspath(args.new)
    py = sys.executable
    ic = os.path.join(top, "ic")
    os.makedirs(ic, exist_ok=True)
    mk = os.path.join(REPO, "problems", "cluster_test", "make_cluster.py")
    subprocess.run([py, mk, "--N", "2000", "--a", "0.9", "--bound_only", "--out",
                    os.path.join(ic, "bound.nrp")], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([py, mk, "--N", "2000", "--a", "0.0", "--fL", "0.3", "--out",
                    os.path.join(ic, "plunge.nrp")], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([py, os.path.join(REPO, "cosmo", "ic", "make_lattice.py"), "--n", "32",
                    "--ppc", "1", "--noise-x", "0.01", "--noise-u", "0.001", "--out", ic],
                   check=True, stdout=subprocess.DEVNULL,
                   cwd=os.path.join(REPO, "cosmo", "ic"))
    prob = os.path.join(REPO, "problems")
    cases = {
        "c1": ["-i", os.path.join(prob, "cluster_test", "cluster_analytic.athinput"),
               f"particles/particle_file={ic}/bound.nrp", "particles/bh_spin=0.9",
               "time/tlim=10.0"],
        "c2": ["-i", os.path.join(prob, "tests", "mesh_static.athinput"),
               "time/tlim=5.0"],
        "c3": ["-i", os.path.join(prob, "cluster_test", "cluster_mesh.athinput"),
               f"particles/particle_file={ic}/plunge.nrp", "time/tlim=0.5"],
        "c4": ["-i", os.path.join(prob, "cosmo", "flrw.athinput"),
               f"particles/particle_file={ic}/particles.nrp", "time/tlim=0.5"],
        "c5": ["-i", os.path.join(prob, "tests", "rng_kick_mesh.athinput"),
               f"particles/particle_file={ic}/plunge.nrp", "particles/test_kick=false",
               "time/tlim=40.0", "particles/snap_dt=20.0", "output1/dt=20.0"],
    }
    summary = {"base": base, "new": new, "cases": {}}
    ok = True
    for name in args.cases.split(","):
        cdir = os.path.join(top, name)
        wall = [run(base, os.path.join(cdir, "base"), cases[name]),
                run(base, os.path.join(cdir, "base2"), cases[name]),
                run(new, os.path.join(cdir, "new"), cases[name])]
        rep = compare(os.path.join(cdir, "base"), os.path.join(cdir, "base2"))
        res = compare(os.path.join(cdir, "base"), os.path.join(cdir, "new"))
        # a file that already differs between two runs of the baseline (a run that is
        # not reproducible, for example sums in parallel on a card) cannot show a
        # regression either way
        if not res["differing"]:
            verdict = "identical"
        elif set(res["differing"]) <= set(rep["differing"]):
            verdict = "not reproducible run to run, no verdict"
        else:
            verdict = "differs"
        summary["cases"][name] = {"args": cases[name], "wall_time_s": wall,
                                  "baseline_twice": rep, "baseline_vs_new": res,
                                  "verdict": verdict}
        ok = ok and verdict != "differs"
        print(f"  {name}: {res['files']} files, baseline twice differing "
              f"{len(rep['differing'])}, baseline vs new differing "
              f"{len(res['differing'])}: {verdict}  ({wall} s)", flush=True)
    summary["ok"] = ok
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
