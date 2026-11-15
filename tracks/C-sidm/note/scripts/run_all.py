"""Run every figure, schematic and ledger script of the note into one directory.

    python run_all.py [--out DIR]

DIR defaults to $NRPIC_RUN_DIR (set by nrpic-run for a registered run) or ../build.
Writes DIR/figures/*, DIR/tables/*, DIR/log.txt and DIR/sha256sums.txt. Stops at the first
script that fails. Copy DIR/figures and DIR/tables into the note after a registered run.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = ["fig_sequences", "fig_knudsen", "fig_collisions", "fig_box_step",
        "schem_architecture", "schem_timeline"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR") or
                    os.path.join(os.path.dirname(HERE), "build"))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, "figures"), exist_ok=True)
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               MPLBACKEND="Agg")
    log = open(os.path.join(out, "log.txt"), "w")
    jobs = [(s, os.path.join(out, "figures")) for s in FIGS] + [("ledger", os.path.join(out, "tables"))]
    for stem, dest in jobs:
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(HERE, f"{stem}.py"), "--out", dest],
                           env=env, capture_output=True, text=True)
        log.write(f"## {stem} (rc {r.returncode}, {time.time() - t0:.1f} s)\n{r.stdout}{r.stderr}\n")
        log.flush()
        print(f"{stem}: rc {r.returncode}")
        if r.returncode != 0:
            print(r.stdout, r.stderr)
            sys.exit(r.returncode)
    log.close()
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        for root, _, files in os.walk(out):
            for name in sorted(files):
                if name == "sha256sums.txt":
                    continue
                p = os.path.join(root, name)
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                f.write(f"{h}  {os.path.relpath(p, out)}\n")


if __name__ == "__main__":
    main()
