#!/usr/bin/env python3
"""Data of the amplitude scan of package threshold_ball: runs conv_ball's prep_bh.py (copied
from runs_ball at 9cddbfc6) once per core contrast delta_c, with the nested lattices that the
scan's meshes need, and once for the ball-radius member C-R1.25 of conv_ball (lam = 1.25 with
the nestC lattice; arguments of conv_ball run A-20261121-075401-1412a08). Processes run in
parallel (--jobs); each writes <out>/<name>/ and <out>/<name>/run.log.

    python3 tracks/A-emd-pbh/threshold_ball/scripts/prep_scan.py --out DIR [--jobs 4]
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PREP = os.path.join(HERE, "..", "..", "conv_ball", "scripts", "prep_bh.py")

# name: (extra prep_bh.py arguments, nested lattices)
SETS = {
    "dc1p0": (["--dc", "1.0"], ["nestB:32:16:1"]),
    "dc0p7": (["--dc", "0.7"], ["nestB:32:16:1"]),
    "dc0p5": (["--dc", "0.5"], ["nestB:32:16:1"]),
    "dc0p45": (["--dc", "0.45"], ["nestB:32:16:1"]),
    "dc0p42": (["--dc", "0.42"], ["nestA:16:16:1", "nestB:32:16:1", "nestC:64:16:1"]),
    "dc0p4": (["--dc", "0.4"], ["nestA:16:16:1", "nestB:32:16:1"]),
    "dc0p35": (["--dc", "0.35"], ["nestB:32:16:1"]),
    "dc0p2": (["--dc", "0.2"], ["nestB:32:16:1"]),
    "R1p25": (["--HRb", "0.875", "--M", "1.953125", "--R1", "0.52", "--R2", "0.76",
               "--edge-w", "0.16836734693877542"], ["nestC:64:16:1"]),
}


def one(name, out):
    args, nested = SETS[name]
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    cmd = [sys.executable, PREP, "--out", d] + args + ["--nlat", "--nested"] + nested
    with open(os.path.join(d, "run.log"), "w") as log:
        log.write(" ".join(cmd) + "\n")
        log.flush()
        r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    return name, r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    names = a.only or list(SETS)
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        res = list(ex.map(lambda n: one(n, a.out), names))
    summary = {}
    for name, rc in res:
        d = os.path.join(a.out, name)
        ent = dict(rc=rc)
        try:
            with open(os.path.join(d, "exact.json")) as f:
                e = json.load(f)
            ent.update(stem=e["stem"], tau_ta=e["core"]["tau_ta"], tau_c=e["core"]["tau_c"],
                       tau_AH=e["first_trapped"]["tau"], m_AH=e["first_trapped"]["m"])
            with open(os.path.join(d, "lattices.json")) as f:
                ent["lattices"] = json.load(f)
        except (OSError, KeyError, ValueError) as exc:
            ent["error"] = repr(exc)
        summary[name] = ent
        print(name, json.dumps({k: v for k, v in ent.items() if k != "lattices"}))
    with open(os.path.join(a.out, "prep_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return 0 if all(rc == 0 for _, rc in res) else 1


if __name__ == "__main__":
    sys.exit(main())
