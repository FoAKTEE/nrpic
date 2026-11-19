#!/usr/bin/env python3
"""Second reading of the regression runs of work package omp: every comparison that
regress.py recorded in a summary.json is made again with the current omplib (measure
rel_floor: each number against itself, with a floor of 1e-6 of the largest number of its
file), and the conservation identity of the deposit is read from each run's history.

    recompare.py DIR [DIR ...] [--tol 1e-8]

DIR holds a summary.json of regress.py (for example scratch/core/<run_id>/atomic).
Writes DIR/summary_floor.json with, per case: the comparisons (worst_rel_floor,
worst_rel_file, files identical and differing) and, per configuration, the largest
|int_E - sum_mW|/sum_mW and |int_S_i - sum_mu_i|/sum_mW over the history (columns 9 and
5, 10-12 and 6-8 of <base>.nrpic.hst): a lost update of the deposit breaks this identity
at the size of the weight of one cloud corner, rounding leaves it near 1e-15.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omplib as L  # noqa: E402


def identity_defect(rundir):
    files = glob.glob(os.path.join(rundir, "*.nrpic.hst"))
    if not files:
        return None
    try:
        h = np.loadtxt(files[0], comments="#", ndmin=2)
    except ValueError:
        return None
    if h.shape[1] < 12:
        return None
    smw = np.abs(h[:, 4])
    smw = np.where(smw > 0, smw, 1.0)
    de = np.abs(h[:, 8] - h[:, 4])/smw
    ds = np.max(np.abs(h[:, 9:12] - h[:, 5:8]), axis=1)/smw
    return {"E": float(de.max()), "S": float(ds.max()), "rows": int(h.shape[0])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--tol", type=float, default=1.0e-8)
    a = ap.parse_args()
    bad = 0
    for d in a.dirs:
        s = json.load(open(os.path.join(d, "summary.json")))
        out = {"source": os.path.join(d, "summary.json"), "tol": a.tol, "floor": L.FLOOR,
               "ref": s["ref"], "cases": {}}
        for case, c in s["cases"].items():
            runs = c["runs"]
            comps = {}
            for key in c["comparisons"]:
                y, x = key.split(" vs ")
                r = L.compare_dirs(runs[x]["rundir"], runs[y]["rundir"])
                comps[key] = r
                flag = r["structural_difference"] or r["worst_rel_floor"] > a.tol
                bad += int(flag)
                print("%-7s %-26s vs %-16s identical %2d differ %2d  rel_floor %.2e  "
                      "rel_file %.2e%s" % (case, y, x, len(r["identical"]), len(r["differ"]),
                                           r["worst_rel_floor"], r["worst_rel_file"],
                                           "  FAIL" if flag else ""))
            ident = {cfg: identity_defect(rr["rundir"]) for cfg, rr in runs.items()}
            for cfg, v in ident.items():
                if v:
                    print("          identity %-22s |int_E - sum_mW| %.2e  |int_S - sum_mu| "
                          "%.2e  (%d rows)" % (cfg, v["E"], v["S"], v["rows"]))
            out["cases"][case] = {"comparisons": comps, "identity": ident,
                                  "runs": {k: {kk: v.get(kk) for kk in
                                               ("rundir", "threads", "exe", "mode", "wall_s",
                                                "exit", "loop_s", "zcps", "ncycle")}
                                           for k, v in runs.items()}}
        L.dump(out, os.path.join(d, "summary_floor.json"))
    print("failures: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
