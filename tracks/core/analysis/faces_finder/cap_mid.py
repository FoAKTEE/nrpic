#!/usr/bin/env python3
"""Linear cloud with deposit_fine_shape and a level cap BETWEEN the coarsest and the
finest level (prediction CM of tracks/core/JOURNAL-faces-finder.md): the case in which
the rule of branch core/faces-finder (a cell beside the cloud is visited only if the
cloud lies on the lattice of its cap) differs from a flag "this cloud was capped".

    cap_mid.py --base ATHENA --new ATHENA --out DIR

Set-up as tracks/core/analysis/deposit_levels/dep_levels.py (flat metric, periodic box
x1 in [-16,16], x2, x3 in [-4,4], root cells of 1, blocks of 8^3), with TWO static levels:
level 1 in |x1| < 8, level 2 in |x1| < 4, and deposit_max_level = 1.  Particles at rest on
ONE lattice everywhere, at the centres of the level-1 cells (spacing 1/2), mass rho0/8, so
the density they stand for is rho0 = 1 and every cloud that the cap holds lies on the
lattice of level 1.  E is read on the x1 line through x2 = x3 = 0.1.
Cases: cic, cic_fs (deposit_fine_shape), with both executables.  Writes DIR/summary.json
and DIR/fig_cap_mid.{pdf,png}; exit 0 if CM holds.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "tracks", "core", "analysis", "deposit_levels"))
from nrpic.io import write_nrp  # noqa: E402
import dep_levels as dl  # noqa: E402

REGION2 = """<refined_region2>
level = 2
x1min = -3.9
x1max = 3.9
x2min = -4.0
x2max = 4.0
x3min = -4.0
x3max = 4.0
<time>"""


def run(exe, d, extra):
    os.makedirs(d, exist_ok=True)
    h = 0.5
    x1 = np.arange(-16.0 + 0.5*h, 16.0, h)
    x2 = np.arange(-4.0 + 0.5*h, 4.0, h)
    g1, g2, g3 = np.meshgrid(x1, x2, x2, indexing="ij")
    x = np.stack([g1.ravel(), g2.ravel(), g3.ravel()], axis=1)
    pfile = os.path.join(d, "lattice.nrp")
    write_nrp(pfile, x, np.zeros_like(x), np.full(len(x), h**3))
    deck = dl.DECK.format(name="cap between levels", shape="cic", cap=1, extra=extra,
                          pfile=pfile, s=dl.SLICE).replace("<time>", REGION2, 1)
    with open(os.path.join(d, "dl.athinput"), "w") as f:
        f.write(deck)
    with open(os.path.join(d, "athena.log"), "w") as log:
        st = subprocess.run([exe, "-i", "dl.athinput", "-d", d], cwd=d, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    _, xa, ea = dl.read_tab(d)
    return st, xa, ea


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    res, lines = {}, {}
    for case, extra in (("cic", ""), ("cic_fs", "deposit_fine_shape = true")):
        for tag, exe in (("base", a.base), ("new", a.new)):
            st, xa, ea = run(exe, os.path.join(out, case, tag), extra)
            dev = ea - 1.0
            lines[(case, tag)] = (xa, dev)
            near01 = (np.abs(np.abs(xa) - 8.0) < 2.0)
            near12 = (np.abs(np.abs(xa) - 4.0) < 1.0)
            res[case + "_" + tag] = {
                "status": st, "cells": int(len(xa)),
                "max_abs_dev": float(np.max(np.abs(dev))),
                "max_abs_dev_near_face_0_1": float(np.max(np.abs(dev[near01]))),
                "max_abs_dev_near_face_1_2": float(np.max(np.abs(dev[near12]))),
                "cells_off": [[float(u), float(v)] for u, v in zip(xa, dev)
                              if abs(v) > 1e-12],
                "line_sum": float(np.sum(ea*np.where(np.abs(xa) < 4.0, 0.25,
                                                     np.where(np.abs(xa) < 8.0, 0.5, 1.0)))),
            }
            print(case, tag, json.dumps({k: v for k, v in res[case + "_" + tag].items()
                                         if k != "cells_off"}), flush=True)
    chk = {
        "status": all(r["status"] == 0 for r in res.values()),
        "CM_new_fs_uniform": res["cic_fs_new"]["max_abs_dev"] < 1e-12,
        "CM_new_plain_uniform": res["cic_new"]["max_abs_dev"] < 1e-12,
        "CM_base_fs_dipole_at_0_1_only":
            res["cic_fs_base"]["max_abs_dev_near_face_0_1"] > 1e-3 and
            res["cic_fs_base"]["max_abs_dev_near_face_1_2"] < 1e-12,
        "CM_plain_same_in_both": bool(np.array_equal(lines[("cic", "base")][1],
                                                     lines[("cic", "new")][1])),
    }
    summ = {"cases": res, "checks": chk,
            "verdict": "PASS" if all(chk.values()) else "FAIL"}
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    for k, v in chk.items():
        print(k, "HOLDS" if v else "FAILS")
    print("cells off, cic_fs base:", res["cic_fs_base"]["cells_off"])
    print("cells off, cic_fs new:", res["cic_fs_new"]["cells_off"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(2)
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.3), sharey=True)
    for ax, case, ttl in ((axs[0], "cic", "(a) CIC, cap at level 1"),
                          (axs[1], "cic_fs", "(b) CIC, deposit_fine_shape, cap at level 1")):
        for c, tag, lab in ((cols[0], "base", "core-v0.8"), (cols[1], "new", "this branch")):
            xa, dev = lines[(case, tag)]
            ax.plot(xa, dev, "o-", ms=2.5, lw=0.9, color=c, label=lab)
        for xf in (4.0, 8.0):
            ax.axvline(xf, color="0.6", lw=0.6, ls="--")
        ax.set_xlim(1.0, 12.0)
        ax.set_xlabel(r"$x^1$ (levels 2, 1, 0 from the left; dashed: faces)")
        ax.set_title(ttl, fontsize=8)
        ax.legend(fontsize=7)
    axs[0].set_ylabel(r"$E/\rho_0 - 1$ on the line $x^2 = x^3 = 0.1$")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_cap_mid"))
    print("CAP MID", summ["verdict"])
    return 0 if summ["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
