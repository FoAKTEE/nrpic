#!/usr/bin/env python3
"""Regression G: Kerr geodesic passage (e = 0.99, a = 0.9 M) on processors.

Reruns, with the processor release executable and the current input
problems/kerr/geodesic.athinput, the passage runs of the earlier campaign
(runs/geodesic/kerr_passage/<name>/run.json gives the exact overrides): the three pushers
on the analytic spherical Kerr-Schild metric at dt = 0.02, 0.01, 0.005 M (order in dt),
and midpoint and Boris-Cholesky on the Hermite lattice at dt = 0.01 M (the four
configurations of the published table). Serial; about one second per run.

    python3 run.py                 # new run id, registers the manifest, runs all
    python3 judge.py <run_id>      # judges it

No build: the executable is /data/haiyangw/nrpic/.work/build_cpu_c1/src/athena.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

CASES = [f"{p}_ks_dt{dt}" for p in ("mid", "bsym", "bchol") for dt in ("0.02", "0.01", "0.005")]
CASES += ["mid_lat_dt0.01", "bchol_lat_dt0.01"]
INPUT = lib.WT / "problems" / "kerr" / "geodesic.athinput"
OLD = lib.OLD_RUNS / "geodesic" / "kerr_passage"


def main():
    lib.env_threads(1)
    run_id = lib.new_run_id()
    out = lib.run_dir(run_id)
    cmds = []
    for name in CASES:
        meta = json.loads((OLD / name / "run.json").read_text())
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        cmd = [str(lib.EXE_CPU), "-i", str(INPUT), "-d", str(d)] + meta["overrides"]
        (d / "run.json").write_text(json.dumps(dict(name=name, meta=meta["meta"],
                                                    overrides=meta["overrides"],
                                                    source=str(OLD / name / "run.json")),
                                               indent=1))
        cmds.append(dict(name=name, cmd=cmd, dir=str(d)))
    lib.write_manifest(
        run_id, kind="scouting", test="G geodesic passage",
        purpose="C3 regression: Kerr e=0.99 passage invariants and dt order with the "
                "processor release executable against the earlier campaign",
        command=[" ".join(c["cmd"]) for c in cmds], cwd=str(out),
        executable=lib.exe_record(lib.EXE_CPU),
        inputs=[lib.file_record(INPUT)] + [lib.file_record(OLD / n / "run.json") for n in CASES],
        resources=dict(device="processor", cores=1, card_hours=0.0),
        status="running")
    t0 = time.time()
    rcs = {}
    for c in cmds:
        with open(Path(c["dir"]) / "athena.log", "w") as log:
            ts = time.time()
            rc = subprocess.run(c["cmd"], cwd=c["dir"], stdout=log, stderr=subprocess.STDOUT).returncode
            log.write(f"\n# exit={rc} wall_s={time.time() - ts:.3f}\n")
        rcs[c["name"]] = rc
        print(f"{c['name']:20s} rc={rc}", flush=True)
    wall = time.time() - t0
    lib.write_manifest(run_id, wall_time_s=round(wall, 2), exit_codes=rcs,
                       status="finished" if all(v == 0 for v in rcs.values()) else "failed")
    print(run_id)


if __name__ == "__main__":
    main()
