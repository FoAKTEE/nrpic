#!/usr/bin/env python3
"""Processor checks of amendment A6 (SCOPE_G3.md, 2026-11-28; predictions g3/amend JOURNAL entry 8).

One registered processor run, four cores at most, release core-v0.9 processor build:
  K1  block count and level extents of the A6 decks (g3g6u, n6es, n6v) with `athena -m`
      (check_review.count_blocks, with the v0.9 executable);
  K2  two-cycle smoke tests of g3g6u, n6es and n6v (one core each, in parallel): the input starts,
      456 MeshBlocks, the finder's search at t = 0 in the status file (found or not, its mass);
  K3  build identity: the G-8 deck g3g8.athinput for two cycles with core-v0.9, compared byte for
      byte with the smoke test S-G8 of core-v0.8 (run D-20261128-020622-50e2cb6, same command);
      a file that differs is compared again after its parameter block (up to `<par_end>`), and the
      parameter lines that differ are listed.
Writes m6_smoke.json into the run directory. No figure: integers, flags, two masses and checksums.

Usage: m6_smoke.py [--out DIR]
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v09/src/athena"
DECKS = HERE.parent / "decks"
SG8 = Path("/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261128-020622-50e2cb6")
COMPARE = ["g3g8.acc.hst", "g3g8.horizon_shape_0.txt", "g3g8.horizon_status_0.txt",
           "g3g8.horizon_summary_0.txt", "g3g8.nrpic.hst", "g3g8.part.00000.bin", "g3g8.removed.bin",
           "g3g8.traj.bin", "g3g8.trajmet.bin", "g3g8.z4c.user.hst",
           "bin/g3g8.con.00000.bin", "bin/g3g8.con.00001.bin", "bin/g3g8.tmunu_E.00000.bin",
           "bin/g3g8.tmunu_E.00001.bin", "bin/g3g8.z4c.00000.bin", "bin/g3g8.z4c.00001.bin",
           "rst/g3g8.00000.rst", "rst/g3g8.00000.rst.prt", "rst/g3g8.00001.rst", "rst/g3g8.00001.rst.prt"]


def sha(path, skip=0):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(skip)
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def par_split(path):
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    k = head.find(b"<par_end>")
    if k < 0:
        return None, None
    k = head.index(b"\n", k) + 1
    return k, head[:k].decode("latin-1").splitlines()


def first_search(run, base):
    p = run / f"{base}.horizon_status_0.txt"
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        q = line.split("#")[0].split()
        return dict(cycle=int(q[0]), time=float(q[1]), found=int(q[2]), reason=int(q[3]),
                    flow=int(q[4]), area_mass=float(q[6]), comment=line.split("#")[-1].strip())
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    J = dict(executable=EXE, exe_sha256=sha(EXE))

    # K1 block counts
    check_review.EXE = EXE
    J["K1"] = {}
    for name in ("g3g6u", "n6es", "n6v"):
        J["K1"][name] = check_review.count_blocks(name, (DECKS / f"{name}.athinput").read_text(), out / "K1")

    # K2 + K3: four two-cycle runs in parallel, one core each
    runs = {"g3g6u": DECKS / "g3g6u.athinput", "n6es": DECKS / "n6es.athinput",
            "n6v": DECKS / "n6v.athinput", "g3g8_v09": DECKS / "g3g8.athinput"}
    env = {"OMP_NUM_THREADS": "1", "PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/tmp")}
    procs = {}
    for name, deck in runs.items():
        d = out / name
        d.mkdir(exist_ok=True)
        log = open(d / "run.log", "w")
        procs[name] = (subprocess.Popen([EXE, "-i", str(deck), "-d", str(d), "time/nlim=2"], cwd=d,
                                        stdout=log, stderr=subprocess.STDOUT, env=env), log)
    rc = {}
    for name, (p, log) in procs.items():
        rc[name] = p.wait()
        log.close()
    J["K2"] = {}
    for name, base in (("g3g6u", "g3g6u"), ("n6es", "n6es"), ("n6v", "n6v"), ("g3g8_v09", "g3g8")):
        d = out / name
        txt = (d / "run.log").read_text(errors="replace")
        m = re.search(r"Total number of MeshBlocks = (\d+)", txt)
        J["K2"][name] = dict(returncode=rc[name], n_blocks=int(m.group(1)) if m else None,
                             first_search=first_search(d, base))

    # K3 identity against S-G8 (core-v0.8)
    d9 = out / "g3g8_v09"
    rows = []
    for rel in COMPARE:
        p8, p9 = SG8 / rel, d9 / rel
        if not p9.exists():
            rows.append(dict(file=rel, identical=False, missing_v09=True))
            continue
        same = sha(p8) == sha(p9)
        row = dict(file=rel, identical=same, size_v08=p8.stat().st_size, size_v09=p9.stat().st_size)
        if not same:
            k8, h8 = par_split(p8)
            k9, h9 = par_split(p9)
            if k8 is not None and k9 is not None:
                row["identical_after_parameters"] = sha(p8, k8) == sha(p9, k9)
                row["parameter_lines_only_v08"] = sorted(set(h8) - set(h9))[:40]
                row["parameter_lines_only_v09"] = sorted(set(h9) - set(h8))[:40]
        rows.append(row)
    J["K3"] = dict(reference=str(SG8), files=rows,
                   all_identical=all(r["identical"] for r in rows),
                   all_identical_after_parameters=all(r["identical"] or r.get("identical_after_parameters", False)
                                                      for r in rows))
    with open(out / "m6_smoke.json", "w") as f:
        json.dump(J, f, indent=1)
    print(json.dumps({"K1": {k: (v["n_blocks"], v["finest_dx"], v["finest_half_width"]) for k, v in J["K1"].items()},
                      "K2": J["K2"], "K3": {k: J["K3"][k] for k in ("all_identical", "all_identical_after_parameters")}},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
