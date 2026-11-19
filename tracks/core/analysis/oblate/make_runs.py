#!/usr/bin/env python3
"""Initial data and the card-job list of test T3 (tracks/core/JOURNAL-oblate.md).

    make_runs.py [--out DIR] [--levels 5 6] [--tlim 55] [--walls 00:08:00 00:34:00]

Writes into DIR (default $NRPIC_RUN_DIR):
  ic/oblate_e0p9_a10_N10000_s1.{nrp,json}   make_ic.py oblate --e 0.9 --a 10 --N 10000 --seed 1
  job.list     lines "<name> <athinput> <athena args>" for nrpic-run --launcher batch:
               cf_card (problems/tests/oblate_cf.athinput, no step: the conformal factor
               on the card) and one collapse run per entry of --levels
               (num_levels = 5: finest cells M/4; 6: M/8; 7: M/16), each with a
               wall-clock limit after which AthenaK writes a restart file and stops
  sha256.txt   checksums of the files written
"""
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[4]
MAKE_IC = WT / "problems" / "ic" / "make_ic.py"
INP = WT / "problems" / "oblate" / "oblate_amr.athinput"
INP_CF = WT / "problems" / "tests" / "oblate_cf.athinput"
# the options of the prolate runs of the ladder (verify/ladder2/make_ics.py on core/nrpic)
ARGS = ("mesh_refinement/max_nmb_per_rank=2000 particles/nfilter=4 "
        "particles/filter_compensate=true")
NAME = {5: "oblate_m4", 6: "oblate_m8", 7: "oblate_m16"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--levels", type=int, nargs="+", default=[5, 6])
    ap.add_argument("--tlim", type=float, default=55.0)
    ap.add_argument("--walls", nargs="+", default=["00:08:00", "00:34:00"])
    ap.add_argument("--no-cf", action="store_true", help="leave out the cf_card line")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    ic = out / "ic"
    ic.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(MAKE_IC), "oblate", "--e", "0.9", "--a", "10", "--N", "10000",
           "--seed", "1", "--out", str(ic)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    (ic / "make_ic.out").write_text(" ".join(cmd) + "\n" + r.stdout + r.stderr)
    nrp = sorted(ic.glob("*.nrp"))[0]
    lines = [] if a.no_cf else [f"cf_card {INP_CF}"]
    for lev, wall in zip(a.levels, a.walls):
        lines.append(f"{NAME[lev]} {INP} mesh_refinement/num_levels={lev} {ARGS} "
                     f"time/tlim={a.tlim:g} particles/particle_file={nrp} -t {wall}")
    (out / "job.list").write_text("\n".join(lines) + "\n")
    with open(out / "sha256.txt", "w") as f:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "sha256.txt":
                f.write(f"{sha(p)}  {p.relative_to(out)}\n")
    print(r.stdout)
    print((out / "job.list").read_text())
    print("wrote", out)


if __name__ == "__main__":
    main()
