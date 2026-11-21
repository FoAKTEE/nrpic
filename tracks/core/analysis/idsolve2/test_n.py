#!/usr/bin/env python3
"""Test N of the initial-data solver, second pass (journal entry 17): the region norms
of release core-v0.5 (<particles> region_dcycle, region_radius1..4) on solved data. A
case of an earlier run is run again with the region options added to its input; every
other file must be byte-identical to the old case, and the record <basename>.region.hst
is compared with the same norms formed from the field dumps.

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_n.py
        --exe <athena> --old-exe <executable named in the old log> --case <old case dir>

Numbers: test_n_numbers.json; figure figs/test_n.
"""
import argparse
import filecmp
import glob
import os
import shlex
import subprocess
import sys

import numpy as np

import lib2
from lib2 import idlib
import test_b
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RADII = (7.0, 13.5)


def read_region(path):
    """<basename>.region.hst -> dict column name -> array."""
    names = None
    for ln in open(path):
        if ln.startswith("# [1]="):
            names = [tok.split("=", 1)[1] for tok in ln[1:].split()]
    a = np.atleast_2d(np.loadtxt(path))
    return {n: a[:, k] for k, n in enumerate(names)}


def from_dump(path):
    """Proper volumes and sqrt(<H^2>) inside the two spheres, in the shell between them
    and outside the second, from a field dump (weight chi^-3/2 dV, cell centres)."""
    d = idlib.read_field(path)
    n = d["n"]
    x = idlib.centres(n[0], -test_b.HALF, test_b.HALF)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    r2 = X*X + Y*Y + Z*Z
    w = d["chi"].astype(np.float64)**-1.5*(2.0*test_b.HALF/n[0])**3
    h2 = d["H"]**2
    out = dict(time=float(d["time"]))
    for key, mk in (("in1", r2 < RADII[0]**2), ("in2", r2 < RADII[1]**2),
                    ("out2", ~(r2 < RADII[1]**2)),
                    ("shell", (r2 < RADII[1]**2) & ~(r2 < RADII[0]**2))):
        v = w[mk].sum()
        out["V_" + key] = float(v)
        out["H2_" + key] = float(np.sqrt((h2[mk]*w[mk]).sum()/v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--old-exe", required=True)
    ap.add_argument("--case", required=True)
    a = ap.parse_args()
    root = lib2.run_root()
    old = a.case.rstrip("/")
    name = os.path.basename(old).split("__")[-1] + "_region"
    new = os.path.join(root, name)
    os.makedirs(new, exist_ok=True)
    lib2.make_input(os.path.join(old, "in.athinput"), os.path.join(new, "in.athinput"),
                    {"particles/region_dcycle": 1, "particles/region_radius1": RADII[0],
                     "particles/region_radius2": RADII[1]})
    steps = [shlex.split(ln[2:]) for ln in open(os.path.join(old, "run.log"))
             if ln.startswith("$ ")]
    steps = [[os.path.abspath(a.exe) if t == a.old_exe else t for t in argv] for argv in steps]
    status = lib2.run_cases([dict(name=name, dir=new, steps=steps)], 1)
    res = dict(run=lib2.run_id(), exe=os.path.abspath(a.exe), old=old, status=status)
    # (a) every other file byte-identical
    same, differ = [], []
    names = set(os.listdir(old)) | set(os.listdir(new))
    for f in sorted(names - {"run.log", "in.athinput"}):
        fa, fb = os.path.join(old, f), os.path.join(new, f)
        if not os.path.exists(fa):
            differ.append(f + " (new)")
        elif not os.path.exists(fb):
            differ.append(f + " (missing)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(f)
        else:
            differ.append(f)
    res.update(identical=same, differ=differ)
    print("identical:", len(same), "differing or new:", differ, flush=True)
    # (b), (c) the record against the field dumps
    base = os.path.basename(glob.glob(os.path.join(new, "*.region.hst"))[0])[:-len(".region.hst")]
    reg = read_region(os.path.join(new, base + ".region.hst"))
    res["columns"] = list(reg)
    res["records"] = int(len(reg["time"]))
    v1, v2 = reg["V_in_s1"], reg["V_in_s2"]
    shell = np.sqrt(np.maximum(v2*reg["H2_in_s2"]**2 - v1*reg["H2_in_s1"]**2, 0.0)/(v2 - v1))
    rows = []
    for p in sorted(glob.glob(os.path.join(new, base + ".field.*.bin"))):
        d = from_dump(p)
        k = int(np.argmin(np.abs(reg["time"] - d["time"])))
        rec = dict(V_in1=reg["V_in_s1"][k], V_in2=reg["V_in_s2"][k], V_out2=reg["V_out_s2"][k],
                   H2_in1=reg["H2_in_s1"][k], H2_in2=reg["H2_in_s2"][k],
                   H2_out2=reg["H2_out_s2"][k], H2_shell=shell[k])
        row = dict(dump=os.path.basename(p), time=d["time"], record_time=float(reg["time"][k]),
                   cycle=int(reg["ncycle"][k]))
        for key, val in rec.items():
            dv = d.get(key, d.get(key.replace("V_", "V_").replace("H2_", "H2_")))
            row[key] = dict(record=float(val), dump=float(dv),
                            rel=float(abs(val - dv)/max(abs(dv), 1e-300)))
        rows.append(row)
        print("t = %.3f (cycle %d):" % (row["time"], row["cycle"]),
              {k: "%.3e (rel %.1e)" % (row[k]["record"], row[k]["rel"])
               for k in ("H2_in1", "H2_shell", "H2_out2", "V_in1")}, flush=True)
    res["rows"] = rows
    out = os.path.join(root, "test_n_numbers.json")
    lib2.save_json(out, res)
    # figure: the record in time, the dumps as symbols
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    t = reg["time"]
    for y, key, lab, c in ((reg["H2_in_s1"], "H2_in1", r"$r<7$", fs.PAL["blue"]),
                           (shell, "H2_shell", r"$7\leq r<13.5$", fs.PAL["red"]),
                           (reg["H2_out_s2"], "H2_out2", r"$r\geq13.5$", fs.PAL["green"])):
        ax.semilogy(t, np.maximum(y, 1e-16), "-", color=c, label=lab + ", record")
        ax.semilogy([r["time"] for r in rows], [max(r[key]["dump"], 1e-16) for r in rows],
                    "o", color=c, mfc="none", ms=6, label=lab + ", field dump")
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$\sqrt{\langle H^2\rangle}$ of the region")
    ax.legend(fontsize=5, ncol=2, loc="lower right")
    fig.tight_layout()
    p = os.path.join(root, "test_n")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
