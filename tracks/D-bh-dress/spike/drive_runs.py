"""Run the CPU AthenaK executable on several particle files in parallel (one process per
file, one core each) and wait.  Each run directory gets run_file.txt naming its file.

usage: python3 drive_runs.py --ic <ic dir> --out <dir> --files a.nrp b.nrp ... \
           [--exe <athena>] [-- <extra input overrides>]
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    argv = sys.argv[1:]
    extra = []
    if "--" in argv:
        k = argv.index("--"); extra = argv[k + 1:]; argv = argv[:k]
    ap = argparse.ArgumentParser()
    ap.add_argument("--ic", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--exe", default="/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena")
    args = ap.parse_args(argv)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    procs = []
    t0 = time.time()
    for f in args.files:
        d = Path(args.out) / Path(f).stem
        d.mkdir(parents=True, exist_ok=True)
        (d / "run_file.txt").write_text(f + "\n")
        cmd = [args.exe, "-i", str(HERE / "spike_geodesic.athinput"), "-d", str(d),
               f"particles/particle_file={Path(args.ic).resolve() / f}", *extra]
        (d / "command.txt").write_text(" ".join(cmd) + "\n")
        log = open(d / "athena.log", "w")
        procs.append((d, subprocess.Popen(cmd, cwd=str(d), stdout=log, stderr=subprocess.STDOUT,
                                          env=env), log))
    rc = 0
    for d, p, log in procs:
        r = p.wait(); log.close()
        print(d.name, "exit", r, f"{time.time() - t0:.1f} s", flush=True)
        rc = rc or r
    sys.exit(rc)


if __name__ == "__main__":
    main()
