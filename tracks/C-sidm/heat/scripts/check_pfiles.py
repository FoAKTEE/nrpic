#!/usr/bin/env python3
"""Integrity of the particle files of the mode runs (heat package).

    check_pfiles.py OUTDIR RUNDIR [RUNDIR ...] [--pairs A:B ...]

1. For every case directory of each RUNDIR (case.json present) whose first snapshot
   heat.part.00000.bin exists: the snapshot's x, u, m (sorted by tag) are compared byte
   for byte with the particle file the case names (case.json `particle_file`), i.e. the
   run started from a complete copy of the intended sample (a case that read a
   half-written file, as in the race of 2026-11-19, would differ or have stopped).
2. --pairs A:B compares two particle files (sha256 and size), e.g. a regenerated file
   with the shared one of an earlier run (same n, theta, eps, seed, sigma, box).
Writes OUTDIR/check_pfiles.json and prints it. "-" for OUTDIR: the registered run's own
output directory. No figure: the result is a list of booleans (each listed).
"""
import glob
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import snap                   # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def check_case(d):
    P = json.load(open(os.path.join(d, "case.json")))
    s0 = os.path.join(d, hl.BASE + ".part.00000.bin")
    out = dict(case=os.path.basename(d), particle_file=P["particle_file"])
    if not os.path.exists(s0):
        out["status"] = "no first snapshot (run did not start)"
        return out
    ini = snap.read_nrp(P["particle_file"])
    s = snap.read_snapshot(s0)
    same_n = len(s["m"]) == len(ini["m"])
    out["n"] = int(len(s["m"]))
    out["time0"] = float(s["time"])
    if not same_n:
        out["status"] = "particle count differs"
        out["identical"] = False
        return out
    tags_ok = bool(np.array_equal(s["tag"], np.arange(len(s["m"]))))
    ident = dict(x=bool(np.array_equal(s["x"], ini["x"])),
                 u=bool(np.array_equal(s["u"], ini["u"])),
                 m=bool(np.array_equal(s["m"], ini["m"])))
    out.update(tags_are_file_positions=tags_ok, identical_fields=ident,
               identical=bool(tags_ok and all(ident.values())),
               max_abs_dx=float(np.max(np.abs(s["x"] - ini["x"]))),
               max_abs_du=float(np.max(np.abs(s["u"] - ini["u"]))))
    out["status"] = "ok" if out["identical"] else "DIFFERS"
    return out


def main():
    args = sys.argv[1:]
    pairs = []
    if "--pairs" in args:
        i = args.index("--pairs")
        pairs = args[i + 1:]
        args = args[:i]
    outdir, rundirs = args[0], args[1:]
    if outdir == "-":
        outdir = hl.outdir("check_pfiles")
    rundirs = [r if os.path.isabs(r) else os.path.join(hl.MAIN, "scratch", "C-sidm", r)
               for r in rundirs]
    res = dict(rundirs=rundirs, cases=[], pairs=[])
    for r in rundirs:
        for cj in sorted(glob.glob(os.path.join(r, "*", "case.json"))):
            c = check_case(os.path.dirname(cj))
            c["rundir"] = os.path.basename(r)
            res["cases"].append(c)
            print(c["rundir"], c["case"], c["status"], flush=True)
    for p in pairs:
        a, b = p.split(":")
        a = a if os.path.isabs(a) else os.path.join(hl.MAIN, "scratch", "C-sidm", a)
        b = b if os.path.isabs(b) else os.path.join(hl.MAIN, "scratch", "C-sidm", b)
        ha, hb = sha256(a), sha256(b)
        row = dict(a=a, b=b, sha256_a=ha, sha256_b=hb, size_a=os.path.getsize(a),
                   size_b=os.path.getsize(b), identical=ha == hb)
        res["pairs"].append(row)
        print("pair", a, b, "identical" if ha == hb else "DIFFER", flush=True)
    started = [c for c in res["cases"] if "identical" in c]
    res["summary"] = dict(n_cases=len(res["cases"]), n_started=len(started),
                          n_identical=sum(c["identical"] for c in started),
                          n_pairs=len(pairs),
                          n_pairs_identical=sum(p["identical"] for p in res["pairs"]))
    with open(os.path.join(outdir, "check_pfiles.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res["summary"], indent=1))


if __name__ == "__main__":
    main()
