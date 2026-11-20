#!/usr/bin/env python3
"""Regression R2 of the initial-data solver, second pass (journal entry 12): cases of
earlier registered runs are replayed with a new executable (the steps of their run.log,
in a new directory, with the executable replaced) and every file is compared byte for
byte with the old case directory.

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/regress_r2.py
        --exe <new athena> --old-exe <executable named in the old logs>
        --same <old case directory> [...] --changed <old case directory> [...]

--same: cases that must not change. --changed: cases of the branch that was changed (a
puncture with momentum or spin together with the vector part): for them the right side
of the vector equation in the outermost layer of active cells, its sums over spheres and
the far-field line are compared between old and new. Numbers: regress_r2.json; figure
figs/regress_r2.
"""
import argparse
import filecmp
import json
import os
import shlex
import shutil
import subprocess
import sys
import time

import numpy as np

import lib2
from lib2 import idlib
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def replay(old, new, old_exe, new_exe):
    """Run the steps of old/run.log in the directory new with the new executable."""
    os.makedirs(new, exist_ok=True)
    shutil.copyfile(os.path.join(old, "in.athinput"), os.path.join(new, "in.athinput"))
    steps = [shlex.split(ln[2:]) for ln in open(os.path.join(old, "run.log"))
             if ln.startswith("$ ")]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    t0 = time.time()
    rc = 0
    with open(os.path.join(new, "run.log"), "w") as log:
        for argv in steps:
            argv = [new_exe if a == old_exe else a for a in argv]
            log.write("$ " + " ".join(argv) + "\n")
            log.flush()
            rc = subprocess.run(argv, cwd=new, stdout=log, stderr=subprocess.STDOUT,
                                env=env).returncode
            if rc != 0:
                break
    return rc, time.time() - t0, any(old_exe in s for s in steps)


def compare(old, new):
    same, differ = [], []
    names = set()
    for d in (old, new):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    for n in sorted(names):
        if n == "run.log":
            continue
        fa, fb = os.path.join(old, n), os.path.join(new, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ.append(n)
    return same, differ


def layer(d):
    """Right side s_x of the vector equation of a uniform case: sums over spheres, the
    largest value in the outermost layer of active cells and inside it beyond r = 12."""
    import glob
    f = glob.glob(os.path.join(d, "*.idvector.bin"))
    if not f:
        return None
    v = lib2.read_idvector(f[0])
    n, box = v["n"], v["box"]
    x = idlib.centres(n[0], box[0], box[1])
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt(X*X + Y*Y + Z*Z)
    dx = (box[1] - box[0])/n[0]
    edge = np.maximum(np.maximum(np.abs(X), np.abs(Y)), np.abs(Z))
    outer = edge >= box[1] - dx
    s = v["s"][0]
    rec = f[0][:-len(".idvector.bin")] + ".idsolve.txt"
    rows, tail = lib2.summary(rec)
    out = dict(sum_r12=float(s[r < 12.0].sum()*dx**3/(8.0*np.pi)),
               sum_r16=float(s[r < box[1]].sum()*dx**3/(8.0*np.pi)),
               sum_all=float(s.sum()*dx**3/(8.0*np.pi)),
               layer_max=float(np.abs(s[outer]).max()),
               beyond12_inner_max=float(np.abs(s[(r >= 12.0) & ~outer]).max()),
               far=lib2.far_line(rec), outer=int(rows[-1][0]), summary=tail,
               mmax_first=float(rows[0][16]), mmax_last=float(rows[-1][16]))
    j = n[1]//2
    out["x"] = x.tolist()
    out["s_x_axis"] = np.abs(s[:, j, j]).tolist()
    w = v["W"]
    out["W"] = [a for a in w]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--old-exe", required=True)
    ap.add_argument("--same", nargs="*", default=[])
    ap.add_argument("--changed", nargs="*", default=[])
    a = ap.parse_args()
    root = lib2.run_root()
    new_exe = os.path.abspath(a.exe)
    rep = dict(run=lib2.run_id(), exe=new_exe, old_exe=a.old_exe, cases={}, changed={})
    bad = 0
    for kind, dirs in (("same", a.same), ("changed", a.changed)):
        for old in dirs:
            old = old.rstrip("/")
            name = os.path.basename(os.path.dirname(old))[-7:] + "__" + os.path.basename(old)
            new = os.path.join(root, name)
            rc, sec, used = replay(old, new, a.old_exe, new_exe)
            same, differ = compare(old, new)
            e = dict(kind=kind, old=old, exit=rc, wall_s=round(sec, 1), old_exe_in_log=used,
                     identical=same, differ=differ)
            rep["cases"][name] = e
            print("%-28s %-7s exit %d, %3d identical, differing: %s (%.0f s)"
                  % (name, kind, rc, len(same), differ if differ else "none", sec), flush=True)
            if kind == "same" and (rc != 0 or differ or not used or not same):
                bad += 1
            if kind == "changed":
                lo, ln = layer(old), layer(new)
                wo, wn = lo.pop("W"), ln.pop("W")
                wmax = max(np.abs(w).max() for w in wo)
                ln["dW_rel_max"] = float(max(np.abs(p - q).max() for p, q in zip(wo, wn))/wmax)
                rep["changed"][name] = dict(old=lo, new=ln)
                for k in ("sum_r12", "sum_r16", "sum_all", "layer_max", "beyond12_inner_max",
                          "outer", "mmax_last"):
                    print("    %-20s old %.13g  new %.13g" % (k, lo[k], ln[k]))
                print("    far old", lo["far"], "\n    far new", ln["far"],
                      "\n    largest change of W over max|W|: %.3e" % ln["dW_rel_max"])
    rep["all_same_identical"] = (bad == 0)
    out = os.path.join(root, "regress_r2.json")
    lib2.save_json(out, rep)
    # figure: files per case, and the right side along the x axis of the changed case
    fs.use_style()
    names = list(rep["cases"])
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 0.22*len(names) + 1.2))
    y = list(range(len(names)))
    ns = [len(rep["cases"][c]["identical"]) for c in names]
    nd = [len(rep["cases"][c]["differ"]) for c in names]
    axs[0].barh(y, ns, color=fs.PAL["blue"], label="identical")
    axs[0].barh(y, nd, left=ns, color=fs.PAL["red"], label="differing")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(names, fontsize=5)
    axs[0].invert_yaxis()
    axs[0].set_xlabel("files compared (old case against its replay)")
    axs[0].legend(fontsize=5, loc="lower right")
    for name, e in rep["changed"].items():
        axs[1].semilogy(e["old"]["x"], np.maximum(e["old"]["s_x_axis"], 1e-20), "-",
                        color=fs.PAL["red"], label="before")
        axs[1].semilogy(e["new"]["x"], np.maximum(e["new"]["s_x_axis"], 1e-20), "--",
                        color=fs.PAL["blue"], label="after")
    axs[1].set_xlabel("$x$ (cells nearest $y=z=0$)")
    axs[1].set_ylabel("$|s_x|$ of the vector equation")
    if rep["changed"]:
        axs[1].legend(fontsize=5)
    fig.tight_layout()
    p = os.path.join(root, "regress_r2")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
