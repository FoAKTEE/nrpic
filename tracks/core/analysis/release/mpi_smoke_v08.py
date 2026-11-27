#!/usr/bin/env python3
"""Smoke test of the MPI build of release core-v0.8 (batch 27).

Runs problems/tests/restart_outputs.athinput (periodic 16^3, particles acting on Z4c, a
tracker, conservation record every 4 cycles) three times: the serial build, the MPI build
started without mpirun (one rank), and the MPI build on two ranks.  Predictions (journal of
core, entry of 2026-11-26T11:55Z):
  M1  the MPI build on one rank writes the output files of the serial build byte for byte
      (logs and restart files excluded: the logs name the executable, restart headers carry
      never-set bytes, OPEN.md item 15)
  M2  two ranks: status 0, the same number of records in cons.hst, the tracker file and the
      mesh history as on one rank, every column within 1e-6 relative (rounding of the
      deposit in shared cells; mpi.md section 7)
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DECK = os.path.join(REPO, "problems", "tests", "restart_outputs.athinput")
MPIRUN = "/home/emost/codes/openmpi/bin/mpirun"


def run(cmd, d):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "athena.log"), "w") as f:
        r = subprocess.run(cmd, cwd=d, stdout=f, stderr=subprocess.STDOUT)
    return r.returncode


def table(path):
    rows = []
    for ln in open(path, errors="replace"):
        if ln.strip() and not ln.startswith("#"):
            try:
                rows.append([float(v) for v in ln.split()])
            except ValueError:
                pass
    return np.array(rows)


def outputs(d):
    out = {}
    for p in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        rel = os.path.relpath(p, d)
        if os.path.isdir(p) or rel.endswith(".log") or "/rst/" in "/" + rel or rel.startswith("rst"):
            continue
        out[rel] = p
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", required=True)
    ap.add_argument("--mpi", required=True)
    ap.add_argument("--particles", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    pf = "particles/particle_file=" + os.path.abspath(a.particles)
    env_cmd = {
        "serial": [a.serial, "-i", DECK, "-d", os.path.join(out, "serial"), pf],
        "mpi1": [a.mpi, "-i", DECK, "-d", os.path.join(out, "mpi1"), pf],
        "mpi2": [MPIRUN, "--bind-to", "none", "-np", "2", a.mpi, "-i", DECK, "-d",
                 os.path.join(out, "mpi2"), pf],
    }
    rc = {k: run(c, os.path.join(out, k)) for k, c in env_cmd.items()}
    res = {"status": rc}
    ck = {}
    s1, m1 = outputs(os.path.join(out, "serial")), outputs(os.path.join(out, "mpi1"))
    diff = sorted(k for k in s1 if k not in m1 or open(s1[k], "rb").read() != open(m1[k], "rb").read())
    res["mpi1_files"] = len(m1)
    res["mpi1_differs_from_serial"] = diff
    ck["M1: MPI build on one rank, %d files, identical to the serial build (differ: %s)"
       % (len(s1), diff)] = rc["serial"] == 0 and rc["mpi1"] == 0 and not diff and len(s1) > 0
    rel = {}
    for name in ("rso.cons.hst", "rso.co_0.txt", "rso.z4c.user.hst"):
        p1, p2 = os.path.join(out, "mpi1", name), os.path.join(out, "mpi2", name)
        if not (os.path.exists(p1) and os.path.exists(p2)):
            rel[name] = None
            continue
        t1, t2 = table(p1), table(p2)
        if t1.shape != t2.shape:
            rel[name] = ("shape", list(t1.shape), list(t2.shape))
            continue
        den = np.maximum(np.abs(t1), 1e-300)
        r = np.abs(t2 - t1) / den
        r[(np.abs(t1) < 1e-12) & (np.abs(t2) < 1e-12)] = 0.0
        rel[name] = float(np.nanmax(r))
    res["mpi2_vs_mpi1_max_relative"] = rel
    ck["M2: two ranks, status %d, records as on one rank, columns within 1e-6 relative (%s)"
       % (rc["mpi2"], rel)] = rc["mpi2"] == 0 and all(isinstance(v, float) and v < 1e-6 for v in rel.values())

    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.95, wspace=0.32)
    for k, col, ls, mk in (("serial", fs.PAL["blue"], "-", "o"), ("mpi1", fs.PAL["red"], "--", ""),
                           ("mpi2", fs.PAL["green"], "none", "x")):
        p = os.path.join(out, k, "rso.cons.hst")
        if os.path.exists(p):
            t = table(p)
            axs[0].plot(t[:, 0], np.abs(t[:, 1]), color=col, ls=ls, marker=mk, ms=3,
                        label={"serial": "serial build", "mpi1": "MPI build, one rank",
                               "mpi2": "MPI build, two ranks"}[k])
    axs[0].set_yscale("log"); axs[0].set_xlabel("t"); axs[0].set_ylabel("|column 2 of cons.hst|")
    axs[0].legend(loc="best", fontsize=7)
    p1, p2 = os.path.join(out, "mpi1", "rso.cons.hst"), os.path.join(out, "mpi2", "rso.cons.hst")
    if os.path.exists(p1) and os.path.exists(p2):
        t1, t2 = table(p1), table(p2)
        if t1.shape == t2.shape:
            for j in range(1, t1.shape[1]):
                d = np.abs(t2[:, j] - t1[:, j]) / np.maximum(np.abs(t1[:, j]), 1e-300)
                axs[1].semilogy(t1[:, 0], np.maximum(d, 1e-17), marker=".", lw=0.8, label="column %d" % (j + 1))
    axs[1].axhline(1e-6, **fs.MASK_LINE)
    axs[1].set_xlabel("t"); axs[1].set_ylabel("two ranks - one rank, relative (floor 1e-17)")
    axs[1].legend(loc="best", fontsize=6, ncol=2)
    figs = fs.save(fig, os.path.join(out, "fig_mpi_smoke"))
    summary = dict(checks=ck, results=res, figures=figs, all_ok=all(ck.values()))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
