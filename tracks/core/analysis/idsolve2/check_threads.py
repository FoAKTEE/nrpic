#!/usr/bin/env python3
"""Test T of the initial-data solver, second pass (journal entry 15): cases of a serial
run are replayed with the threaded processor build (scripts/build_cpu_omp.sh) and
compared with the serial case directories; one case is replayed twice to see whether
the threaded build repeats itself at a fixed thread count.

    nrpic-run submit ... --cores N -- python3 tracks/core/analysis/idsolve2/check_threads.py
        --exe <threaded athena> --serial-exe <executable named in the serial logs>
        --threads N --cases <serial case directory> [...] [--twice <serial case directory>]

Per case: outer iterations and linear steps of the two records, max|H| (and max|M|) of
the constraint monitor after the solve, the largest difference of psi and W over their
maxima, the far-field line, the region means of |H| of the last field dump of an
evolution, and the wall time of the replay (its steps that write the particle file
included). Numbers: check_threads.json; figure
figs/check_threads.
"""
import argparse
import filecmp
import glob
import os
import sys

import numpy as np

import lib2
import analyze_k
import regress_r2
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def residuals(d):
    rec = glob.glob(os.path.join(d, "*.idsolve.txt"))[0]
    rows, _ = lib2.summary(rec)
    out = dict(H_first=float(rows[0][4]), H_last=float(rows[-1][4]))
    if rows.shape[1] > 16:
        out.update(M_first=float(rows[0][16]), M_last=float(rows[-1][16]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--serial-exe", required=True)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--cases", nargs="*", default=[])
    ap.add_argument("--twice", default="")
    a = ap.parse_args()
    root = lib2.run_root()
    exe = os.path.abspath(a.exe)
    rep = dict(run=lib2.run_id(), exe=exe, serial_exe=a.serial_exe, threads=a.threads,
               cases={}, repeat={})
    bad = 0
    for old in a.cases:
        old = old.rstrip("/")
        name = os.path.basename(old).split("__")[-1]
        new = os.path.join(root, name)
        rc, sec, used = regress_r2.replay(old, new, a.serial_exe, exe, a.threads)
        e = dict(exit=rc, wall_s=round(sec, 1), serial_exe_in_log=used, serial_dir=old)
        if rc == 0:
            e.update(analyze_k.one(new, old))     # "card" keys hold the threaded run
            e["threaded"], e["serial"] = residuals(new), residuals(old)
        else:
            bad += 1
        rep["cases"][name] = e
        print(name, {k: e.get(k) for k in ("exit", "wall_s", "outer_card", "outer_proc",
                                           "dpsi_rel", "dW_rel", "threaded", "serial")},
              flush=True)
    if a.twice:
        old = a.twice.rstrip("/")
        name = os.path.basename(old).split("__")[-1]
        first, second = os.path.join(root, name), os.path.join(root, name + "_again")
        rc, sec, _ = regress_r2.replay(old, second, a.serial_exe, exe, a.threads)
        same, differ = regress_r2.compare(first, second)
        rep["repeat"] = dict(case=name, exit=rc, identical=same, differ=differ)
        print("repeat of %s with %d threads: %d identical, differing: %s"
              % (name, a.threads, len(same), differ if differ else "none"), flush=True)
        if rc != 0:
            bad += 1
    out = os.path.join(root, "check_threads.json")
    lib2.save_json(out, rep)
    # figure: differences of the fields, and the residuals each build reaches
    fs.use_style()
    names = [n for n in rep["cases"] if rep["cases"][n]["exit"] == 0]
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.6))
    x = np.arange(len(names))
    floor = 1e-18
    for k, (key, lab, c) in enumerate((("dpsi_rel", r"$\psi$", fs.PAL["blue"]),
                                        ("dW_rel", r"$W$", fs.PAL["red"]))):
        v = [max(rep["cases"][n].get(key) or 0.0, floor) if key in rep["cases"][n] else np.nan
             for n in names]
        axs[0].bar(x + 0.35*k - 0.17, v, 0.35, color=c, label=lab)
    axs[0].set_yscale("log")
    axs[0].set_ylim(1e-17, 1e-1)
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(names, fontsize=6, rotation=15)
    axs[0].set_ylabel("largest difference over the maximum")
    axs[0].set_title("%d threads against the serial build" % a.threads, fontsize=7)
    axs[0].legend(fontsize=6)
    for key, mk, lab in (("H_last", "o", r"$\max|H|$ after the solve"),
                         ("M_last", "s", r"$\max|M|$ after the solve")):
        vs = [rep["cases"][n]["serial"].get(key, np.nan) for n in names]
        vt = [rep["cases"][n]["threaded"].get(key, np.nan) for n in names]
        axs[1].plot(x - 0.12, vs, mk, color=fs.PAL["blue"], ms=5, label=lab + ", serial")
        axs[1].plot(x + 0.12, vt, mk, color=fs.PAL["red"], ms=5, mfc="none",
                    label=lab + ", %d threads" % a.threads)
    axs[1].set_yscale("log")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(names, fontsize=6, rotation=15)
    axs[1].set_xlim(-0.6, len(names) - 0.4)
    axs[1].set_ylabel("constraint monitor of the record")
    axs[1].legend(fontsize=5, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    fig.tight_layout()
    p = os.path.join(root, "check_threads")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
