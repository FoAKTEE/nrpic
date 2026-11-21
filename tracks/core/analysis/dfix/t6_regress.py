#!/usr/bin/env python3
"""Test T6 of work package dfix: existing set-ups give the same files, byte for byte,
with the release executable and with the changed source.

    python3 tracks/core/analysis/dfix/t6_regress.py --base <release athena> --new <athena>
                                                    [--out REPORT.json]

1. The seven cases of tracks/core/tools/regress_relativistic.py (test particle in Kerr
   with both pushers, deposit on a refined mesh, periodic cosmology with Z4c, dust ball
   with Z4c, two cases of the multigrid gravity of the gas), each a registered run.
2. Three cases of the Newtonian mode (its kick and push carry the hook of the external
   gravity), inputs problems/newton/*.athinput with particle files of
   problems/newton/make_ic.py: cold ball on the isolated domain (50 steps), point mass
   with tracers (20 steps), plane wave in the expanding periodic box (40 steps); and the
   tracer set-up problems/tests/mesh_static.athinput (deposit on a static mesh metric).
   Run in one registered run (runreg.py of this directory sets NRPIC_RUN_DIR), compared
   file by file.
Exit status 0 only if no file differs.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
NEWTON = os.path.join(REPO, "problems", "newton")


def newton_cases(run):
    ic = os.path.join(run, "ic")
    os.makedirs(ic, exist_ok=True)
    mk = [sys.executable, os.path.join(NEWTON, "make_ic.py")]
    subprocess.run(mk + ["ball", "--out", os.path.join(ic, "ball32.nrp"), "--spacing", "0.125",
                         "--ntracer", "0"], check=True, cwd=ic)
    subprocess.run(mk + ["point", "--out", os.path.join(ic, "point.nrp"), "--center", "0.031",
                         "0.017", "-0.011"], check=True, cwd=ic)
    subprocess.run(mk + ["wave", "--out", os.path.join(ic, "wave32.nrp"), "--n", "32"],
                   check=True, cwd=ic)
    iso = os.path.join(NEWTON, "isolated.athinput")
    per = os.path.join(NEWTON, "periodic.athinput")
    small = ["mesh/nx1=32", "mesh/nx2=32", "mesh/nx3=32", "meshblock/nx1=16", "meshblock/nx2=16",
             "meshblock/nx3=16"]
    return {
        "newton_ball": [iso] + small + ["time/nlim=50", "particles/dt=0.002", "particles/snap_dt=0.05",
                                        "particles/particle_file=" + os.path.join(ic, "ball32.nrp"),
                                        "output1/dt=0.05"],
        "newton_point": [iso] + small + ["time/nlim=20", "particles/dt=0.002", "particles/snap_dt=0.02",
                                         "particles/particle_file=" + os.path.join(ic, "point.nrp")],
        "newton_wave": [per, "time/nlim=40", "particles/snap_dt=0.1",
                        "particles/particle_file=" + os.path.join(ic, "wave32.nrp")],
        "mesh_static": [os.path.join(REPO, "problems", "tests", "mesh_static.athinput"),
                        "time/nlim=200"],
    }


def compare(da, db):
    differ, same = [], []
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    for n in sorted(names):
        if n == "athena.log":
            continue
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ.append(n)
    return same, differ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--skip-relativistic", action="store_true")
    a = ap.parse_args()
    run = os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("NRPIC_RUN_DIR is not set (start through runreg.py)")
    report, bad = {}, 0
    if not a.skip_relativistic:
        rj = os.path.join(run, "relativistic.json")
        p = subprocess.run([sys.executable, os.path.join(REPO, "tracks", "core", "tools",
                                                         "regress_relativistic.py"),
                            "--exe-a", a.base, "--exe-b", a.new,
                            "--cases", "geo,boris,dep,east,os,jeans,binary", "--out", rj],
                           capture_output=True, text=True)
        print(p.stdout, p.stderr, flush=True)
        report["relativistic"] = json.load(open(rj)) if os.path.isfile(rj) else {"error": p.stderr}
        bad += p.returncode
    cases = newton_cases(run)
    report["newton"] = {}
    for name, args in cases.items():
        dirs = {}
        for label, exe in (("base", a.base), ("new", a.new)):
            d = os.path.join(run, name, label)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "athena.log"), "w") as log:
                rc = subprocess.run([exe, "-i", args[0], "-d", d] + args[1:], cwd=d, stdout=log,
                                    stderr=subprocess.STDOUT).returncode
            dirs[label] = (d, rc)
        same, differ = compare(dirs["base"][0], dirs["new"][0])
        ok = (not differ) and same and dirs["base"][1] == 0 and dirs["new"][1] == 0
        bad += 0 if ok else 1
        report["newton"][name] = dict(identical=same, differ=differ, exit_base=dirs["base"][1],
                                      exit_new=dirs["new"][1])
        print("%-13s identical files: %d  differing: %s  exit %d %d"
              % (name, len(same), differ if differ else "none", dirs["base"][1], dirs["new"][1]),
              flush=True)
    out = a.out or os.path.join(run, "t6_regress.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=1)
        f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
