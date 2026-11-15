#!/usr/bin/env python3
"""Card check of work package clump (test G of tracks/core/JOURNAL-clump.md), to be run
inside a Slurm job that holds one card (card_check_job.sh):

  1. byte regression, release card executable against this branch's, on set-ups without
     deposit: problems/tests/regress_cf.athinput and problems/puncture/by_static.athinput
     (card runs with deposit are not reproducible from run to run);
  2. the new curvature on the card: problems/tests/clump_static.athinput at 64 cells
     without and with the curvature, 128 cells with it, and the spin case at 64 cells;
     the history records at t = 0 are compared with the processor runs (--t1, --t3).

    card_check.py --base ATHENA_GPU_BASE --new ATHENA_GPU_NEW --t1 RUN_ID --t3 RUN_ID --out DIR
Writes card_check.json; exit status 0 if the regression is identical and the card
records agree with the processor records to 1e-6 (the history prints six digits).
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
PUBLISHED = os.path.join(SCRATCH, "exe", "core_clump-curvature")
sys.path.insert(0, HERE)
import run_static as rs  # noqa: E402


def run(exe, d, inp, args):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "athena.log"), "w") as log:
        st = subprocess.run([exe, "-i", os.path.join(WT, inp), "-d", d] + args, cwd=d,
                            stdout=log, stderr=subprocess.STDOUT).returncode
    if st != 0:
        raise RuntimeError(f"{d}: exit status {st}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("--t3", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    top = a.out
    ic = os.path.join(top, "ic")
    os.makedirs(ic, exist_ok=True)
    py = sys.executable
    out = dict(base=a.base, new=a.new, regression={}, curvature={})
    ok = True
    subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "mp",
                                     "make_regress_table.py"),
                    os.path.join(ic, "regress.tab")], check=True)
    for name, inp, args in (
            ("regress_cf", "problems/tests/regress_cf.athinput",
             [f"problem/comp0_file={ic}/regress.tab"]),
            ("by_static", "problems/puncture/by_static.athinput",
             ["problem/comp0_s3=0.2", "problem/comp0_corr=approx"])):
        for lab, exe in (("base", a.base), ("new", a.new)):
            run(exe, os.path.join(top, name, lab), inp, args)
        p = subprocess.run([py, os.path.join(WT, "tracks", "core", "analysis", "id",
                                             "regress_format1.py"),
                            os.path.join(top, name, "base"), os.path.join(top, name, "new")],
                           capture_output=True, text=True)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-300:]
        out["regression"][name] = dict(identical=p.returncode == 0, report=last)
        ok = ok and p.returncode == 0
        print(f"card regression {name}: {last}", flush=True)

    cpu = {}
    for rid, which in ((a.t1, "t1"), (a.t3, "t3")):
        with open(os.path.join(SCRATCH, rid, f"cases_{which}.json")) as f:
            cpu.update(json.load(f)["cases"])
    for name in ("latP0.06", "latS0.04"):
        subprocess.run([py, rs.MAKE_IC, "clumps", *rs.ICS[name], "--out", ic, "--prefix",
                        name], check=True, stdout=subprocess.DEVNULL)
    for label, icn, args in (
            ("t1_n64_none", "latP0.06", rs.res(64)),
            ("t1_n64_curv", "latP0.06", rs.res(64) + ["problem/comp0_p1=0.06"]),
            ("t1_n128_curv", "latP0.06", rs.res(128) + ["problem/comp0_p1=0.06"]),
            ("t3_n64_curv", "latS0.04", rs.res(64) + ["problem/comp0_s3=0.04"])):
        d = os.path.join(top, label)
        os.makedirs(d, exist_ok=True)
        if not os.path.exists(os.path.join(d, "particles.nrp")):
            os.symlink(os.path.join(ic, icn + ".nrp"), os.path.join(d, "particles.nrp"))
        run(a.new, d, "problems/tests/clump_static.athinput", args)
        g = rs.hst_rows(os.path.join(d, "clump.z4c.user.hst"))[0]
        c = cpu[label]["hst0"]
        rel = max(abs(g[i] / c[i] - 1.0) for i in (3, 4, 6))
        out["curvature"][label] = dict(card=g, processor=c, max_rel_diff_H2_M2_Mx2=rel)
        ok = ok and rel < 1.0e-6
        print(f"card {label}: H2 {g[3]:.5e} M2 {g[4]:.5e} Mx2 {g[6]:.5e}; processor "
              f"H2 {c[3]:.5e} M2 {c[4]:.5e} Mx2 {c[6]:.5e}; max rel diff {rel:.1e}",
              flush=True)
    with open(os.path.join(top, "card_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("CARD CHECK PASSED" if ok else "CARD CHECK FAILED")
    # the published executables (decision 0013): leave the verdict beside them
    if os.path.isdir(PUBLISHED):
        import hashlib
        import time
        with open(a.new, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        with open(os.path.join(PUBLISHED, "CARD_CHECK"), "w") as f:
            f.write(("PASSED" if ok else "FAILED") + " " + time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n"
                f"card executable tested: {a.new}\nsha256 {sha} (compare with athena_gpu)\n"
                f"output: {top}/card_check.json\n")
            for k, v in out["regression"].items():
                f.write(f"regression {k} against {a.base}: {v['report']}\n")
            for k, v in out["curvature"].items():
                f.write(f"{k}: card and processor records at t = 0 differ by "
                        f"{v['max_rel_diff_H2_M2_Mx2']:.1e} (relative)\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
