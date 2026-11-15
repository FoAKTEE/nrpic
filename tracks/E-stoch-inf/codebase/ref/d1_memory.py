"""D1 of ../JOURNAL.md: resident memory and throughput of vacuum Z4c in a periodic box
(processor executable), fitted as  M = c0 + a N_interior + b N_shell  with N_shell the
ghost cells of all MeshBlocks; extrapolation to the card-sized meshes of the review.

Usage: python3 -I d1_memory.py <run_dir> <outdir>
  <run_dir> holds the case directories n32mb32, n32mb16, mb64, mb32, mb16 with
  athena.log and time.log (GNU time -v) of the run registered for D1.
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../../python")))
from nrpic import figstyle as fs                 # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402

CASES = {"n32mb32": (32, 32), "n32mb16": (32, 16), "mb64": (64, 64), "mb32": (64, 32),
         "mb16": (64, 16)}
NG = 4


def read_case(d):
    t = open(os.path.join(d, "time.log")).read()
    a = open(os.path.join(d, "athena.log")).read()
    rss_kb = int(re.search(r"Maximum resident set size \(kbytes\): (\d+)", t).group(1))
    zcs = float(re.search(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", a).group(1))
    return rss_kb*1024.0, zcs


def counts(N, b):
    nb = (N//b)**3
    nint = N**3
    nghosted = nb*(b + 2*NG)**3
    return nb, nint, nghosted - nint


def main(run_dir, outdir):
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for name, (N, b) in CASES.items():
        rss, zcs = read_case(os.path.join(run_dir, name))
        nb, nint, nsh = counts(N, b)
        rows.append(dict(case=name, N=N, block=b, nblocks=nb, n_interior=nint,
                         n_shell=nsh, rss_bytes=rss, zone_cycles_per_s=zcs))
    A = np.array([[1.0, r["n_interior"], r["n_shell"]] for r in rows])
    y = np.array([r["rss_bytes"] for r in rows])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    for r, p in zip(rows, pred):
        r["fit_bytes"] = float(p)
        r["fit_rel_err"] = float(p/r["rss_bytes"] - 1.0)
    # single-slope model for comparison (bytes per cell with ghosts)
    A1 = np.array([[1.0, r["n_interior"] + r["n_shell"]] for r in rows])
    coef1, *_ = np.linalg.lstsq(A1, y, rcond=None)
    # extrapolation: vacuum Z4c on uniform meshes, plus the scalar-field additions
    # (2 evolved variables x 3 registers, 10 Tmunu, 6 noise fields = 22 doubles per
    # cell with ghosts, and 2/22 of the per-shell buffer cost)
    extra_cell = 22*8.0
    extra_shell = coef[2]*2.0/22.0
    ext = []
    for N in (64, 128, 256, 512):
        for b in (64, 128):
            if b > N:
                continue
            nb, nint, nsh = counts(N, b)
            vac = coef[0] + coef[1]*nint + coef[2]*nsh
            sf = vac + extra_cell*(nint + nsh) + extra_shell*nsh
            ext.append(dict(N=N, block=b, vacuum_GB=vac/1e9, scalar_field_GB=sf/1e9))
    res = dict(rows=rows, fit=dict(c0_bytes=coef[0], bytes_per_interior_cell=coef[1],
                                   bytes_per_shell_cell=coef[2]),
               single_slope=dict(c0_bytes=coef1[0], bytes_per_cell=coef1[1]),
               extrapolation=ext,
               note="host resident memory of the Kokkos processor build; a proxy for "
                    "the device memory of the card build [JUDGEMENT]")
    print(json.dumps(res, indent=1))
    with open(os.path.join(outdir, "d1.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fig.add_axes([0.08, 0.16, 0.38, 0.78])
    ax2 = fig.add_axes([0.58, 0.16, 0.38, 0.78])
    x = np.array([r["n_interior"] + r["n_shell"] for r in rows])
    ax1.plot(x, y/1e6, "o", color=fs.PAL["red"], label="measured (max RSS)")
    ax1.plot(x, pred/1e6, "x", color=fs.PAL["blue"], ms=8,
             label="fit c0 + a N_int + b N_shell")
    xs = np.linspace(0, x.max()*1.05, 10)
    ax1.plot(xs, (coef1[0] + coef1[1]*xs)/1e6, **fs.GUIDE, label="single slope")
    for r, xi in zip(rows, x):
        ax1.annotate(f"{r['N']}^3/{r['block']}^3", (xi, r["rss_bytes"]/1e6),
                     textcoords="offset points", xytext=(4, -10), fontsize=7)
    ax1.set_xlabel("cells including ghost cells")
    ax1.set_ylabel("resident memory (MB)")
    ax1.legend(fontsize=8, loc="upper left")
    ax2.bar(np.arange(len(rows)), [r["zone_cycles_per_s"] for r in rows],
            color=fs.PAL["red"], alpha=0.8)
    ax2.axhline(1.4e4, **fs.GUIDE)
    ax2.text(0.0, 1.43e4, "Track B, one core", fontsize=8)
    ax2.set_xticks(np.arange(len(rows)))
    ax2.set_xticklabels([f"{r['N']}/{r['block']}" for r in rows], fontsize=8)
    ax2.set_xlabel("N / MeshBlock size")
    ax2.set_ylabel("zone-cycles/s, one core")
    ax2.set_ylim(0, 2e4)
    fs.save(fig, os.path.join(outdir, "d1_memory"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
