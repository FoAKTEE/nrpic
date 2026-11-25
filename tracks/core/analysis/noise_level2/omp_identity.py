#!/usr/bin/env python3
"""Review test R6 (journal entry 9): the threaded processor executables before and after
the review give the same bytes at level 2.

    omp_identity.py --old ATHENA_OMP --new ATHENA_OMP --out DIR [--threads 3] [--nlim 12]

The two level-2 decks of the card list (inputs/card/{sr,usr}64_l2.athinput, 64^3,
nmax2 = 256) with dumps and the per-mode record every nlim/2 cycles; old and new run side
by side with the same number of threads, without binding.  Byte comparison of every
.dump, .modes, .rmodes, .hst.  Writes DIR/summary.json; exit status 1 on a difference."""
import argparse
import concurrent.futures as cf
import filecmp
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402

CASES = ["sr64_l2", "usr64_l2"]
SUFFIX = (".dump", ".modes", ".rmodes", ".hst")


def run(exe, rd, inp, threads):
    os.makedirs(rd, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false")
    with open(os.path.join(rd, "log.txt"), "w") as fo:
        return subprocess.run([os.path.abspath(exe), "-i", inp], cwd=rd, stdout=fo,
                              stderr=subprocess.STDOUT, env=env).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--nlim", type=int, default=12)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    res = dict(old=os.path.abspath(a.old), new=os.path.abspath(a.new), threads=a.threads,
               nlim=a.nlim, cases={})
    bad = False
    for c in CASES:
        inp = nl2.write_input(os.path.join(HERE, "inputs", "card", c + ".athinput"),
                              os.path.join(out, c + ".athinput"),
                              {"time/nlim": a.nlim, "scalar_field/dump_dt": -1.0,
                               "scalar_field/dump_dcycle": a.nlim//2,
                               "scalar_field/noise_rmodes_dump": "true"})
        with cf.ThreadPoolExecutor(max_workers=2) as pool:
            fo = pool.submit(run, a.old, os.path.join(out, c, "old"), inp, a.threads)
            fn = pool.submit(run, a.new, os.path.join(out, c, "new"), inp, a.threads)
            rco, rcn = fo.result(), fn.result()
        da, db = os.path.join(out, c, "old"), os.path.join(out, c, "new")
        names = sorted(f for f in os.listdir(da) if f.endswith(SUFFIX))
        same = [f for f in names if os.path.exists(os.path.join(db, f))
                and filecmp.cmp(os.path.join(da, f), os.path.join(db, f), shallow=False)]
        differ = [f for f in names if f not in same]
        res["cases"][c] = dict(exit_old=rco, exit_new=rcn, files=len(names),
                               identical=len(same), differ=differ)
        bad = bad or differ or rco != 0 or rcn != 0 or not names
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
