#!/usr/bin/env python3
"""Is the apparent-horizon finder of the case t7_ah_exc_dep sensitive to rounding on ONE
rank?  (work package mpi, journal entry 27)

    python3 finder_sensitivity.py --ref <t7_ah_exc_dep output>/np1 [--out DIR] [--nlim 8]
                                  [extra athena arguments ...]

Runs problems/tests/mpi_puncture_exc.athinput on one rank twice, side by side:
  same      the particle file of the test (must reproduce the reference run bit for bit)
  reversed  the same particles written in the opposite order: the tags and the order of
            the additions of the deposit change, nothing else (a change of the sources
            at the level of rounding)
With --flow-perturb EPS the second run is instead
  perturbed the particle file of the test, and the constant of the finder's flow
            (<fastflow> flow_alpha_beta_const_0, the bare mass squared by default) times
            1 + EPS: a change at the level of rounding inside the finder, which acts on
            nothing else until a particle is removed differently
(both runs then get the constant written into a copy of the input file).  It prints, per search of the finder, the result of both and of the reference, and the
number of removed particles per cycle.  Writes sensitivity.json.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mpi_tests as mt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--nlim", type=int, default=8)
    ap.add_argument("--exe", default=mt.DEFAULT_EXE)
    ap.add_argument("--rmin", type=float, default=0.3)
    ap.add_argument("--rmax", type=float, default=2.5)
    ap.add_argument("--flow-perturb", type=float, default=0.0)
    ap.add_argument("--flow-const", type=float, default=1.0,
                    help="unperturbed flow constant (bare mass squared)")
    ap.add_argument("extra", nargs="*")
    a = ap.parse_args()
    out = os.path.abspath(a.out or os.environ.get("NRPIC_RUN_DIR", os.getcwd()))
    os.makedirs(out, exist_ok=True)
    from nrpic.io import read_nrp, write_nrp
    same = os.path.join(out, "infall.nrp")
    mt.make_infall(same, rmin=a.rmin, rmax=a.rmax)
    x, u, m, sp = read_nrp(same)
    rev = os.path.join(out, "infall_reversed.nrp")
    write_nrp(rev, x[::-1].copy(), u[::-1].copy(), m[::-1].copy(),
              None if sp is None else sp[::-1].copy())
    inp0 = os.path.join(mt.REPO, mt.PUNC)
    second = "perturbed" if a.flow_perturb else "reversed"
    procs = []
    for name, pf in (("same", same), (second, same if a.flow_perturb else rev)):
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        inp = inp0
        if a.flow_perturb:
            c = a.flow_const*(1.0 + (a.flow_perturb if name == "perturbed" else 0.0))
            inp = os.path.join(out, name + ".athinput")
            mt.input_with(inp0, inp, {"fastflow": ["flow_alpha_beta_const_0 = %.17g" % c]})
        cmd = [mt.MPIRUN, "--bind-to", "none", "-np", "1", a.exe, "-i", inp, "-d", d,
               "particles/particle_file=" + pf, "time/nlim=%d" % a.nlim] + a.extra
        log = open(os.path.join(d, "run.log"), "w")
        procs.append((name, d, subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                                env=dict(os.environ, OMP_NUM_THREADS="1")), log))
    res = {}
    for name, d, p, log in procs:
        rc = p.wait()
        log.close()
        print("%s exit=%d" % (name, rc), flush=True)
        res[name] = dict(exit=rc)
    tabs = {"reference": a.ref, "same": os.path.join(out, "same"),
            second: os.path.join(out, second)}
    hs = {k: mt.read_table(os.path.join(d, "px.horizon_summary_0.txt")) for k, d in tabs.items()}
    hh = {k: mt.read_table(os.path.join(d, "px.nrpic.hst")) for k, d in tabs.items()}
    n = min(len(v) for v in hs.values())
    print("search  time    " + "  ".join("%-34s" % k for k in tabs))
    rows = []
    for i in range(n):
        row = dict(time=float(hs["same"][i, 1]))
        txt = []
        for k in tabs:
            row[k] = dict(mass=float(hs[k][i, 2]), hrms=float(hs[k][i, 8]),
                          minradius=float(hs[k][i, 11]))
            txt.append("M=%.12f rmin=%.9f hrms=%.3f" % (hs[k][i, 2], hs[k][i, 11], hs[k][i, 8]))
        rows.append(row)
        print("%2d  %7.4f  %s" % (i, row["time"], "  ".join(txt)))
    nc = min(len(v) for v in hh.values())
    exc = {k: [int(v) for v in hh[k][:nc, 16]] for k in tabs}
    for k in tabs:
        print("removed per cycle, %-9s %s" % (k, exc[k]))
    for k in tabs:
        if k != "reference":
            res[k]["tracker_identical_to_reference_rows"] = bool(np.array_equal(
                mt.read_table(os.path.join(tabs[k], "px.co_0.txt")),
                mt.read_table(os.path.join(a.ref, "px.co_0.txt"))[:nc - 1]))
    ident = all(mt.sha256(os.path.join(tabs["same"], f)) == mt.sha256(os.path.join(a.ref, f))
                for f in ("px.horizon_summary_0.txt",)) if n == len(hs["reference"]) else None
    same_rows = bool(np.array_equal(hs["same"][:n], hs["reference"][:n], equal_nan=True))
    res.update(searches=rows, removed=exc, same_equals_reference_rows=same_rows,
               summary_file_identical=ident)
    print("same == reference in all %d searches: %s" % (n, same_rows))
    with np.errstate(invalid="ignore"):
        rel = np.abs(hs[second][:n, 11] - hs["same"][:n, 11])/np.abs(hs["same"][:n, 11])
        relm = np.abs(hs[second][:n, 2] - hs["same"][:n, 2])/np.abs(hs["same"][:n, 2])
    res[second + "_rel_minradius"] = [float(v) for v in rel]
    res[second + "_rel_mass"] = [float(v) for v in relm]
    res["second"] = second
    res["flow_perturb"] = a.flow_perturb
    print(second + " against same, relative difference of the smallest radius per search:",
          " ".join("%.1e" % v for v in rel))
    print(second + " against same, relative difference of the mass per search:",
          " ".join("%.1e" % v for v in relm))
    with open(os.path.join(out, "sensitivity.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
