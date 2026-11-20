"""Processor runs of AthenaK on prepared Szekeres files (particle-number check, JOURNAL
entry 8, P22-P23).

Each member NAME runs in $NRPIC_RUN_DIR/NAME with the files of the preparation run
(--prep DIR/NAME/fields.bin and particles.nrp), the deck inputs/szekeres_geodesic.athinput,
one MeshBlock, OMP_NUM_THREADS = --threads; the members run at the same time.

    python3 scripts/run_cpu_members.py --prep DIR --members N32 N32_ppc8 --tlim 2 \
        --field-times 0.5 1 2 [--exe PATH] [--threads 1]
"""

import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
DECK = os.path.join(common.PKG, "inputs", "szekeres_geodesic.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--members", nargs="+", required=True)
    ap.add_argument("--tlim", type=float, default=2.0)
    ap.add_argument("--field-times", type=float, nargs="*", default=[0.5, 1.0, 2.0])
    ap.add_argument("--exe", default=EXE)
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    rdir = common.run_dir("cpu_members")
    extra = [f"particles/field_time{i + 1}={t}" for i, t in enumerate(a.field_times[:4])]
    extra += [f"particles/field_time{i + 1}={a.tlim * 10}" for i in range(len(a.field_times), 4)]
    jobs = []
    for name in a.members:
        d = os.path.join(rdir, name)
        os.makedirs(d, exist_ok=True)
        N =int(name[1:].split("_")[0])
        cmd = [a.exe, "-i", DECK, "-d", d, f"mesh/nx1={N}", f"mesh/nx2={N}", f"mesh/nx3={N}",
               f"meshblock/nx1={N}", f"meshblock/nx2={N}", f"meshblock/nx3={N}",
               f"problem/id_file={os.path.join(a.prep, name, 'fields.bin')}",
               f"particles/particle_file={os.path.join(a.prep, name, 'particles.nrp')}",
               f"time/tlim={a.tlim}"] + extra
        log = open(os.path.join(d, "athena.log"), "w")
        env = dict(os.environ, OMP_NUM_THREADS=str(a.threads))
        jobs.append(dict(name=name, cmd=cmd, t0=time.time(),
                         proc=subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT, env=env)))
    out = dict(run_id=common.run_id(), commit=common.git_commit(), exe=a.exe, deck=DECK, members={})
    rc = 0
    for j in jobs:
        e = j["proc"].wait()
        rc = rc or e
        out["members"][j["name"]] = dict(exit=e, wall_s=time.time() - j["t0"], cmd=" ".join(j["cmd"]))
        print(j["name"], "exit", e, f"{time.time() - j['t0']:.0f} s", flush=True)
    with open(os.path.join(rdir, "cpu_members.json"), "w") as f:
        json.dump(out, f, indent=1)
    sys.exit(rc)


if __name__ == "__main__":
    main()
