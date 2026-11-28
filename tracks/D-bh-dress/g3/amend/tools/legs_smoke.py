#!/usr/bin/env python3
"""Processor smoke tests of the particle-leg and gauge-leg decks of G3 (g3g84n, g3g8e1; A1's rule for decks
of at most twice G-8's cells; predictions g3/amend JOURNAL entry 11). Two cycles each, one core each, in
parallel, release core-v0.9 processor build. Reports exit status, MeshBlocks, particles read, the search at
t = 0 (found, reason, flow iterations, area mass) and the peak resident memory. No figure: integers, flags
and two masses. Writes legs_smoke.json.

Usage: legs_smoke.py [--out DIR]
"""
import argparse
import json
import os
import re
import resource
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from m6_smoke import first_search, sha  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v09/src/athena"
DECKS = HERE.parent / "decks"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    env = {"OMP_NUM_THREADS": "1", "PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/tmp")}
    procs = {}
    for name in ("g3g84n", "g3g8e1"):
        d = out / name
        d.mkdir(exist_ok=True)
        log = open(d / "run.log", "w")
        cmd = ["/usr/bin/time", "-v", EXE, "-i", str(DECKS / f"{name}.athinput"), "-d", str(d), "time/nlim=2"]
        procs[name] = (subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT, env=env), log)
    J = dict(executable=EXE, exe_sha256=sha(EXE))
    for name, (p, log) in procs.items():
        rc = p.wait()
        log.close()
        txt = (out / name / "run.log").read_text(errors="replace")
        nb = re.search(r"Total number of MeshBlocks = (\d+)", txt)
        npart = re.search(r"NRPIC: read (\d+) particles", txt)
        rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", txt)
        J[name] = dict(returncode=rc, n_blocks=int(nb.group(1)) if nb else None,
                       particles_read=int(npart.group(1)) if npart else None,
                       peak_rss_gib=int(rss.group(1)) / 2**20 if rss else None,
                       first_search=first_search(out / name, name))
    with open(out / "legs_smoke.json", "w") as f:
        json.dump(J, f, indent=1)
    print(json.dumps(J, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
