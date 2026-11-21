#!/usr/bin/env python3
"""Processor smoke test of every deck of the series (package conv_ball; JOURNAL.md entry 3,
prediction S): core_gauge/athena_cpu (the processor twin of the card executable of the
series) on the full nested meshes, a few cycles (nlim = 2) for the decks with outer 16 M at
M/16 and M/32 and for the M/16 deck with outer 32 M, initialization only (nlim = 0) for the
others. Each case runs in <out>/<case>/ (the finder writes into the working directory);
at most --jobs processes at a time, one thread each. Writes <out>/smoke.json.

    smoke.py --out DIR [--jobs 6]
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
EXE = "/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_cpu"

# case: (member whose deck and data are used, nlim)
CASES = {"s16": ("A", 2), "s16R135": ("A-R1.35", 2), "s16L32": ("A-L32", 2), "s32": ("B", 2),
         "s32L32": ("B-L32", 0), "s64": ("C", 0), "s64L32": ("C", 0)}


def run(case, out, members):
    name, nlim = CASES[case]
    m = members[name]
    deck = m["deck"]
    if case == "s64L32":
        deck = deck.replace("nest64_L16", "nest64_L32")
    d = os.path.join(out, case)
    os.makedirs(d, exist_ok=True)
    cmd = [EXE, "-i", deck, "-d", d] + m["args"] + [f"time/nlim={nlim}"]
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(d, "athena.log"), "w") as f:
        f.write("# " + " ".join(cmd) + "\n")
        f.flush()
        rc = subprocess.call(cmd, cwd=d, stdout=f, stderr=subprocess.STDOUT, env=env)
    log = open(os.path.join(d, "athena.log")).read()
    nmb = re.findall(r"Number of MeshBlocks\s*=\s*(\d+)|Total number of MeshBlocks\s*=\s*(\d+)|MeshBlocks\s*=\s*(\d+)", log)
    res = dict(case=case, member=name, deck=os.path.basename(deck), nlim=nlim, rc=rc,
               meshblock_lines=[l for l in log.splitlines() if "MeshBlock" in l][:6],
               particle_lines=[l for l in log.splitlines() if "particle" in l.lower()][:6],
               last_lines=log.splitlines()[-8:])
    hst = os.path.join(d, "ball.nrpic.hst")
    if os.path.exists(hst):
        rows = [l.split() for l in open(hst) if l.strip() and not l.startswith("#")]
        res["hst_rows"] = len(rows)
        res["hst_last_finite"] = bool(rows) and all(v.lower() not in ("nan", "inf", "-inf") for v in rows[-1])
        res["hst_last"] = rows[-1][:6] if rows else None
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    members = json.load(open(os.path.join(PKG, "lists", "members.json")))
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run, c, a.out, members): c for c in CASES}
        res = [f.result() for f in cf.as_completed(futs)]
    res.sort(key=lambda r: list(CASES).index(r["case"]))
    with open(os.path.join(a.out, "smoke.json"), "w") as f:
        json.dump(res, f, indent=1)
    for r in res:
        print(r["case"], r["deck"], "nlim", r["nlim"], "rc", r["rc"], "hst rows", r.get("hst_rows"),
              "finite", r.get("hst_last_finite"))
        for l in r["meshblock_lines"][:3]:
            print("   ", l)
    bad = [r["case"] for r in res if r["rc"] != 0]
    print("FAILED:" if bad else "all exit 0", bad)


if __name__ == "__main__":
    main()
