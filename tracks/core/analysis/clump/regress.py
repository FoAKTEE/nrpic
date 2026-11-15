#!/usr/bin/env python3
"""Test R of tracks/core/JOURNAL-clump.md: existing set-ups of the problem generator
nrpic_cf run with the release executable and with the executable of this branch, every
output file compared byte by byte (tracks/core/analysis/id/regress_format1.py; mesh
restart headers without their 36 never-set bytes).

    regress.py --base ATHENA_BASE --new ATHENA_NEW [--out DIR] [--cases a,b,..]

Cases:
  regress_cf        problems/tests/regress_cf.athinput: table, Gaussian, spheroid and
                    puncture, no particles, two cycles
  cf_table_regress  problems/tests/cf_table_regress.athinput: Oppenheimer-Snyder table,
                    lattice particles, one refined level
  by_static         problems/puncture/by_static.athinput: Bowen-York puncture with
                    momentum, spin and the closed-form correction, t = 0
  jeans             problems/jeans/jeans.athinput with the command-line overrides of the
                    first paper's run jeans/n1e4_v19 (two Gaussian clumps in a tabulated
                    envelope, 10^4 particles, eight levels), two cycles; its first
                    history record is also compared with the record of that run
Writes regress.json into the output directory; exit status 0 only if all are identical.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
V19 = "/data/haiyangw/nrpic/runs/jeans/n1e4_v19"


def v19_overrides():
    with open(os.path.join(V19, "chain", "config.sh")) as f:
        return re.search(r"EXTRA_ARGS=\((.*)\)", f.read()).group(1).split()


def run(exe, rundir, inp, args):
    os.makedirs(rundir, exist_ok=True)
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-i", inp, "-d", rundir] + args, cwd=rundir, stdout=log,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ, OMP_NUM_THREADS="1"))
    if p.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {p.returncode}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--cases", default="regress_cf,cf_table_regress,by_static,jeans")
    a = ap.parse_args()
    top = a.out
    ic = os.path.join(top, "ic")
    os.makedirs(ic, exist_ok=True)
    py = sys.executable
    subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "mp",
                                     "make_regress_table.py"),
                    os.path.join(ic, "regress.tab")], check=True)
    subprocess.run([py, os.path.join(WT, "problems", "ic", "make_ic.py"), "os", "--N",
                    "10000", "--sampler", "lattice", "--out", ic], check=True,
                   stdout=subprocess.DEVNULL)
    osnrp = sorted(x for x in os.listdir(ic) if x.endswith(".nrp"))[0]
    cases = {
        "regress_cf": ("problems/tests/regress_cf.athinput",
                       [f"problem/comp0_file={ic}/regress.tab"], []),
        "cf_table_regress": ("problems/tests/cf_table_regress.athinput",
                             [f"particles/particle_file={ic}/{osnrp}",
                              f"problem/comp0_file={ic}/{osnrp[:-4]}.tab"], []),
        "by_static": ("problems/puncture/by_static.athinput",
                      ["problem/comp0_s3=0.2", "problem/comp0_corr=approx"], []),
        "jeans": ("problems/jeans/jeans.athinput",
                  v19_overrides() + ["mesh_refinement/max_nmb_per_rank=1100", "time/nlim=2"],
                  [os.path.join(V19, "particles.nrp"), os.path.join(V19, "envelope.tab")]),
    }
    summary = dict(base=a.base, new=a.new, cases={})
    ok = True
    for name in a.cases.split(","):
        inp, args, files = cases[name]
        for lab, exe in (("base", a.base), ("new", a.new)):
            d = os.path.join(top, name, lab)
            os.makedirs(d, exist_ok=True)
            for f in files:
                shutil.copy(f, d)
            run(exe, d, os.path.join(WT, inp), args)
        p = subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "id",
                                             "regress_format1.py"),
                            os.path.join(top, name, "base"), os.path.join(top, name, "new")],
                           capture_output=True, text=True)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-300:]
        summary["cases"][name] = dict(identical=p.returncode == 0, report=last)
        ok = ok and p.returncode == 0
        print(f"R {name}: {last}", flush=True)
        if name == "jeans":
            def first(path):
                with open(path) as f:
                    return next(l for l in f if not l.startswith("#")).split()
            new0 = first(os.path.join(top, name, "new", "jeans.z4c.user.hst"))
            old0 = first(os.path.join(V19, "jeans.z4c.user.hst"))
            summary["cases"][name]["hst0_new"] = new0
            summary["cases"][name]["hst0_run_n1e4_v19"] = old0
            print("  t = 0 record, this executable :", " ".join(new0))
            print("  t = 0 record, run n1e4_v19    :", " ".join(old0))
    with open(os.path.join(top, "regress.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("ALL IDENTICAL" if ok else "DIFFERENCES FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
