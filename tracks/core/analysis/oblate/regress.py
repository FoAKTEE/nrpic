#!/usr/bin/env python3
"""Test T2 of tracks/core/JOURNAL-oblate.md: existing set-ups of nrpic_cf give the same
bytes with the executable of this branch as with the release executable (processors).

    regress.py --base ATHENA_RELEASE --new ATHENA_BRANCH [--out DIR]
               [--cases NAME ...] [--nlim-table N] [--nlim-prolate N]

Cases (each run with both executables in <out>/<case>/{base,new}):
  regress_cf        problems/tests/regress_cf.athinput: table, Gaussian, prolate
                    spheroid, puncture, no particles, two steps, all fields written
  cf_table_regress  problems/tests/cf_table_regress.athinput: table with 10^4 lattice
                    particles, one refined level, twelve steps
  prolate_start     problems/prolate/prolate_amr.athinput with the options of the
                    ladder runs, finest cells M/4 (num_levels = 5), 16 steps, 10^4
                    particles: the prolate spheroid with deposition, filter, refinement
Compared with tracks/core/analysis/id/regress_format1.py (every file but the logs; 36
never-set bytes of the restart headers left out).  Writes regress.json; exit status 1 if
any case differs.  The two executables of a case run side by side (two cores).
--nlim-table and --nlim-prolate shorten the two cases with particles (defaults 12 and
16 steps; on the loaded machine a step of the prolate start takes minutes).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def start(exe, rundir, inp, args):
    os.makedirs(rundir, exist_ok=True)
    log = open(os.path.join(rundir, "athena.log"), "w")
    return subprocess.Popen([exe, "-i", inp, "-d", rundir] + args, cwd=rundir,
                            stdout=log, stderr=subprocess.STDOUT), log, time.time()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", os.getcwd()))
    ap.add_argument("--cases", nargs="+",
                    default=["regress_cf", "cf_table_regress", "prolate_start"])
    ap.add_argument("--nlim-table", type=int, default=12)
    ap.add_argument("--nlim-prolate", type=int, default=16)
    a = ap.parse_args()
    top = os.path.abspath(a.out)
    a.base, a.new = os.path.abspath(a.base), os.path.abspath(a.new)   # runs change directory
    ic = os.path.join(top, "ic")
    os.makedirs(ic, exist_ok=True)
    py = sys.executable
    mk = os.path.join(WT, "problems", "ic", "make_ic.py")
    subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "mp",
                                     "make_regress_table.py"),
                    os.path.join(ic, "regress.tab")], check=True)
    subprocess.run([py, mk, "os", "--N", "10000", "--sampler", "lattice", "--out", ic],
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run([py, mk, "prolate", "--e", "0.9", "--b", "10", "--N", "10000",
                    "--seed", "1", "--out", ic], check=True, stdout=subprocess.DEVNULL)
    osnrp = sorted(x for x in os.listdir(ic) if x.startswith("os_") and x.endswith(".nrp"))[0]
    ostab = osnrp[:-4] + ".tab"
    cases = {
        "regress_cf": (os.path.join(WT, "problems", "tests", "regress_cf.athinput"),
                       [f"problem/comp0_file={ic}/regress.tab"]),
        "cf_table_regress": (os.path.join(WT, "problems", "tests", "cf_table_regress.athinput"),
                             [f"particles/particle_file={ic}/{osnrp}",
                              f"problem/comp0_file={ic}/{ostab}",
                              f"time/nlim={a.nlim_table}"]),
        "prolate_start": (os.path.join(WT, "problems", "prolate", "prolate_amr.athinput"),
                          ["mesh_refinement/num_levels=5",
                           "mesh_refinement/max_nmb_per_rank=2000", "particles/nfilter=4",
                           "particles/filter_compensate=true",
                           f"time/nlim={a.nlim_prolate}",
                           f"particles/particle_file={ic}/prolate_e0p9_b10_N10000_s1.nrp"]),
    }
    res = {"base": a.base, "new": a.new, "cases": {}}
    ok = True
    for name, (inp, args) in cases.items():
        if name not in a.cases:
            continue
        wall = {}
        procs = {lab: start(exe, os.path.join(top, name, lab), inp, args)
                 for lab, exe in (("base", a.base), ("new", a.new))}
        for lab, (p, log, t0) in procs.items():
            rc = p.wait()
            log.close()
            wall[lab] = time.time() - t0
            if rc != 0:
                raise RuntimeError(f"{name}/{lab}: exit status {rc}")
        p = subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "id",
                                             "regress_format1.py"),
                            os.path.join(top, name, "base"), os.path.join(top, name, "new")],
                           capture_output=True, text=True)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr.strip()
        res["cases"][name] = dict(identical=(p.returncode == 0), report=last, wall_s=wall,
                                  args=args)
        ok &= (p.returncode == 0)
        print(f"{name}: {last}  (wall {wall['base']:.0f} s, {wall['new']:.0f} s)", flush=True)
    res["all_identical"] = bool(ok)
    with open(os.path.join(top, "regress.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("ALL IDENTICAL" if ok else "DIFFERENCES FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
