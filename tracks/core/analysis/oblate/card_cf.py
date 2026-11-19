#!/usr/bin/env python3
"""Test T1, part e, of tracks/core/JOURNAL-oblate.md: the conformal factor of the oblate
component as the card executable sets it (run cf_card of the card job), against the
reference potential and against the processor dump of the same input.

    card_cf.py --card DIR [--cpu DIR] [--out DIR]

DIR are run directories of problems/tests/oblate_cf.athinput (default case, e = 0.9,
a = 10 M, mesh half-width 48 M); --cpu is P1a/e09 of a cf_check.py run.  Writes
card_cf.json and figs/cf_check_card.{png,pdf}.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cf_check as cc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--cpu", default=None)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", os.getcwd()))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    ref, blob = cc.reference_module(out)
    A, B = 10.0, 10.0 * cc.Q
    x, y, z, vol, fld = cc.load(a.card, "adm")
    p4 = fld["adm_psi4"]
    p4_ref = (1.0 - ref.phi_N(x, y, z, A, B)[0]) ** 4
    d = np.abs(p4.astype(np.float64) - p4_ref)
    bound = 0.5 * cc.ulp32(p4_ref) + 1e-12
    res = dict(card=a.card, reference=dict(branch=cc.REF_BRANCH, path=cc.REF_PATH, blob=blob),
               cells=int(len(x)), max_diff_over_ulp32=float((d / cc.ulp32(p4_ref)).max()),
               cells_above_bound=int(np.sum(d > bound)),
               passed=bool(np.sum(d > bound) == 0))
    _, _, _, _, fc = cc.load(a.card, "con")
    Hc = 32.0 * math.pi * (3.0 / (8.0 * math.pi * A * A * B))
    res["max_abs_H_over_32pi_rhoN"] = float(np.abs(fc["con_H"]).max() / Hc)
    if a.cpu:
        xc, yc, zc, _, fcpu = cc.load(a.cpu, "adm")
        # same mesh, same block order is not assumed: sort both by position
        o1 = np.lexsort((x, y, z))
        o2 = np.lexsort((xc, yc, zc))
        same_pos = bool(np.array_equal(x[o1], xc[o2]) and np.array_equal(y[o1], yc[o2])
                        and np.array_equal(z[o1], zc[o2]))
        diff = p4[o1] != fcpu["adm_psi4"][o2]
        res.update(cpu=a.cpu, same_cell_positions=same_pos,
                   cells_differing_from_processor_dump=int(diff.sum()),
                   largest_difference_from_processor_in_float32_units=float(
                       np.max(np.abs(p4[o1].astype(np.float64)
                                     - fcpu["adm_psi4"][o2].astype(np.float64))
                              / cc.ulp32(p4_ref[o1]))))
    print(json.dumps(res, indent=1))
    with open(os.path.join(out, "card_cf.json"), "w") as f:
        json.dump(res, f, indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.95)
    ax.hist((p4.astype(np.float64) - p4_ref) / cc.ulp32(p4_ref), bins=np.linspace(-0.6, 0.6, 49),
            color=fs.PAL["red"])
    ax.axvline(-0.5, **fs.GUIDE)
    ax.axvline(0.5, **fs.GUIDE)
    ax.set_xlabel(r"$(\psi^4_{\rm card}-\psi^4_{\rm ref})$ / float32 unit", labelpad=-1)
    ax.set_ylabel("cells")
    fs.save(fig, os.path.join(HERE, "figs", "cf_check_card"))


if __name__ == "__main__":
    main()
