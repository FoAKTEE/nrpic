#!/usr/bin/env python3
"""Test T6 of tracks/core/JOURNAL-scalar2.md: the scalar-field inputs of wave 1 with the
executable of release core-v0.3 and with the new one; every output file is compared byte
by byte.

    python3 t6_regress.py --base EXE --new EXE --out DIR [--workers 6]

Cases (inputs under problems/scalar/):
  flrw    flrw_slowroll.athinput, conformal-time lapse, 40 steps
  flrwg   the same in geodesic slicing, 40 steps
  plane   plane.athinput, 20 steps, dumps
  wave    kg_wave.athinput, test field, 32 steps, dumps
  smr     kg_wave_smr.athinput, statically refined mesh, 8 steps
  power   noise_power.athinput, 64 steps, dumps and restart files at cycle 32 and 64
  powerm  the same with noise_scheme = markov
  ms      noise_ms.athinput (mode file of this script), 26 steps, restart files
  msr     ms restarted from the restart file of cycle 13 of each executable
  msnk    ms with the three kicks off (the synthesis of a stage is then skipped)
In a mesh restart file the 36 bytes of the nine coarse-mesh indices of Mesh::mesh_indcs
are never set (tracks/core/analysis/scalar/check_rst_diff.py); they are masked.
Writes DIR/summary.json; exit status 1 if a file differs."""
import argparse
import filecmp
import glob
import os
import sys

import common
from common import inf, np


def rst_equal(fa, fb):
    a = np.fromfile(fa, dtype=np.uint8)
    b = np.fromfile(fb, dtype=np.uint8)
    if a.size != b.size:
        return False, "sizes differ"
    diff = np.nonzero(a != b)[0]
    if diff.size == 0:
        return True, "identical"
    head = bytes(a[:400000])
    p = head.find(b"<par_end>\n") + len(b"<par_end>\n")
    lo = p + 4 + 4 + 9*8 + 10*4
    hi = lo + 9*4
    if diff.min() >= lo and diff.max() < hi:
        return True, f"{diff.size} bytes differ, all inside the unset range {lo}-{hi - 1}"
    return False, f"{diff.size} bytes differ, first {diff.min()}, last {diff.max()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    exes = dict(base=os.path.abspath(a.base), new=os.path.abspath(a.new))
    # mode file of the Mukhanov-Sasaki unit test: any smooth mode functions will do
    n2 = inf.shells(36)
    q = np.sqrt(n2.astype(float))
    modes = os.path.join(out, "modes.txt")
    inf.write_mode_file(modes, n2, 1e-3*np.exp(1j*q)/q**1.5, 1e-3*(0.3 - 0.2j)/q**0.5)
    P = common.PROB
    geo = ["z4c/lapse_harmonic=0.0"]
    ms = [f"scalar_field/noise_mode_file={modes}"]
    spec = {
        "flrw": (P + "/flrw_slowroll.athinput", ["time/nlim=40"]),
        "flrwg": (P + "/flrw_slowroll.athinput", ["time/nlim=40"] + geo),
        "plane": (P + "/plane.athinput", ["time/nlim=20", "scalar_field/dump_dt=0.05"]),
        "wave": (P + "/kg_wave.athinput", ["time/nlim=32", "scalar_field/dump_dt=0.05"]),
        "smr": (P + "/kg_wave_smr.athinput", ["time/nlim=8"]),
        "power": (P + "/noise_power.athinput", []),
        "powerm": (P + "/noise_power.athinput", ["scalar_field/noise_scheme=markov"]),
        "ms": (P + "/noise_ms.athinput", ["time/nlim=26", "scalar_field/dump_dt=0.5"]
               + ms),
        "msnk": (P + "/noise_ms.athinput", ["time/nlim=26", "scalar_field/dump_dt=0.5",
                                            "scalar_field/noise_kick_pi=false",
                                            "scalar_field/noise_kick_k=false",
                                            "scalar_field/noise_kick_a=false"] + ms),
    }
    walls = {}
    for lab, exe in exes.items():
        cases = [(os.path.join(out, k, lab), inp, args) for k, (inp, args) in spec.items()]
        w = common.run_many(exe, cases, a.workers)
        walls[lab] = dict(zip(spec, w))
        # restart of the Mukhanov-Sasaki case from cycle 13
        rst = sorted(glob.glob(os.path.join(out, "ms", lab, "rst", "*.00001.rst")))
        common.run_case(exe, os.path.join(out, "msr", lab), rst[0], [])
    summ = dict(exes=exes, wall_s=walls, cases={})
    ok = True
    for k in list(spec) + ["msr"]:
        da, db = os.path.join(out, k, "base"), os.path.join(out, k, "new")
        names = set()
        for d in (da, db):
            for root, _, files in os.walk(d):
                for f in files:
                    names.add(os.path.relpath(os.path.join(root, f), d))
        res = dict(identical=[], masked=[], differ=[])
        for n in sorted(names):
            if n == "athena.log":
                continue
            fa, fb = os.path.join(da, n), os.path.join(db, n)
            if not (os.path.exists(fa) and os.path.exists(fb)):
                res["differ"].append(n + " (missing in one run)")
            elif filecmp.cmp(fa, fb, shallow=False):
                res["identical"].append(n)
            elif n.endswith(".rst"):
                same, why = rst_equal(fa, fb)
                (res["masked"] if same else res["differ"]).append(f"{n}: {why}")
            else:
                res["differ"].append(n)
        summ["cases"][k] = dict(files=len(names) - 1, identical=len(res["identical"]),
                                masked=res["masked"], differ=res["differ"])
        ok = ok and not res["differ"]
    summ["ok"] = ok
    common.dump_json(summ, os.path.join(out, "summary.json"))
    for k, v in summ["cases"].items():
        print(k, v["files"], "files,", v["identical"], "identical,", len(v["masked"]),
              "masked,", len(v["differ"]), "differ", v["differ"][:4])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
