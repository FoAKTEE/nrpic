#!/usr/bin/env python3
"""Regression M1 of the initial-data solver, second pass, against a release that holds
the first pass (core-v0.4, core-v0.5; journal entry 15): the example inputs of the first
pass (problems/idsolve/gaussian, gaussian_boost, ball, torus) at 32 cells, run by the
release executable as they are and by the executable of this branch

  robin    with <particles> id_far = robin (the fill of the first pass): what must not
           change (matter at rest), or changes at round-off (moving matter: the term
           4 pi psi S of the Jacobian is new),
  default  with no new option: what a user of the release sees change (the far field is
           on by default on a mesh with no periodic face; on the torus nothing).

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/regress_m1.py
        --base <release athena> --new <athena of this branch> [--jobs N]

Every file of a case directory except run.log and in.athinput is compared byte for byte
with the release's; psi (and W) of the dumps are compared in the largest difference.
Numbers: regress_m1.json; figure figs/regress_m1.
"""
import argparse
import filecmp
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PROB = os.path.join(lib2.WT, "problems", "idsolve")
N, MB = 32, 16
# name: input, basename of the outputs, steps that write the particle file (and table),
# options of every run, name of the particle file
SETUPS = {
    "gauss": dict(inp="gaussian.athinput", base="gauss",
                  ic=[lib2.py(lib2.MAKE_IC, "gaussian", "--h", "0.5", "--out", ".")],
                  sets={"particles/particle_file": "gauss_h0p5.nrp",
                        "particles/id_residual": "code"}),
    "gboost": dict(inp="gaussian_boost.athinput", base="gboost",
                   ic=[lib2.py(lib2.MAKE_IC, "gaussian", "--h", "0.5", "--out", "."),
                       lib2.py(lib2.MAKE_IC, "boost", "--in", "gauss_h0p5.nrp", "--u", "0.1",
                               "--out", ".", "--prefix", "boost")],
                   sets={"particles/particle_file": "boost.nrp"}),
    "ball": dict(inp="ball.athinput", base="ball",
                 ic=[lib2.py(lib2.MAKE_BALL, "--Rb", "10", "--h", "1.0", "--edge", "2.0",
                             "--tracers", "", "--sample", "0", "--out", ".", "--prefix",
                             "ball")],
                 sets={"particles/particle_file": "ball.nrp", "problem/comp0_file": "ball.tab",
                       "particles/id_residual": "code", "particles/nfilter": 0}),
    "torus": dict(inp="torus.athinput", base="torus",
                  ic=[lib2.py(lib2.MAKE_IC, "wave", "--n", str(N), "--ppc", "1", "--out", ".",
                              "--prefix", "wave")],
                  sets={"particles/particle_file": "wave.nrp",
                        "particles/id_residual": "code"}),
}
VARIANTS = ("base", "robin", "default")


def build_cases(root, base_exe, new_exe):
    cases = []
    for name, s in SETUPS.items():
        for var in VARIANTS:
            d = os.path.join(root, "%s_%s" % (name, var))
            os.makedirs(d, exist_ok=True)
            sets = dict(lib2.mesh(N, MB))
            sets.update(s["sets"])
            if var == "robin":
                sets["particles/id_far"] = "robin"
            lib2.make_input(os.path.join(PROB, s["inp"]), os.path.join(d, "in.athinput"), sets)
            exe = base_exe if var == "base" else new_exe
            cases.append(dict(name="%s_%s" % (name, var), dir=d,
                              steps=list(s["ic"]) + [[exe, "-i", "in.athinput"]]))
    return cases


def compare(da, db):
    same, differ = [], []
    names = set()
    for d in (da, db):
        names.update(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    for n in sorted(names - {"run.log", "in.athinput"}):
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ.append(n)
    return same, differ


def fields(d, base):
    out = {}
    p = os.path.join(d, base + ".idsolve.bin")
    if os.path.exists(p):
        out["psi"] = idlib.read_idsolve_bin(p)["psi"]
    p = os.path.join(d, base + ".idvector.bin")
    if os.path.exists(p):
        out["W"] = lib2.read_idvector(p)["W"]
    rec = os.path.join(d, base + ".idsolve.txt")
    rows, tail = lib2.summary(rec)
    out["outer"] = int(rows[-1][0])
    out["H_first"], out["H_last"] = float(rows[0][4]), float(rows[-1][4])
    out["far"] = lib2.far_line(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    root = lib2.run_root()
    status = lib2.run_cases(build_cases(root, os.path.abspath(a.base), os.path.abspath(a.new)),
                            a.jobs)
    rep = dict(run=lib2.run_id(), base=a.base, new=a.new, cells=N, status=status, pairs={})
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    for name, s in SETUPS.items():
        db = os.path.join(root, name + "_base")
        fb = fields(db, s["base"])
        for var in VARIANTS[1:]:
            dn = os.path.join(root, "%s_%s" % (name, var))
            same, differ = compare(db, dn)
            fn = fields(dn, s["base"])
            e = dict(identical=same, differ=differ, outer=[fb["outer"], fn["outer"]],
                     H_last=[fb["H_last"], fn["H_last"]], far=fn["far"])
            if "psi" in fb and "psi" in fn:
                e["dpsi_max"] = float(np.abs(fb["psi"] - fn["psi"]).max())
                e["u_max"] = float(np.abs(fb["psi"] - 1.0).max())
            if "W" in fb and "W" in fn:
                wmax = max(np.abs(w).max() for w in fb["W"])
                e["dW_rel_max"] = float(max(np.abs(p - q).max()
                                            for p, q in zip(fb["W"], fn["W"]))/wmax)
            rep["pairs"]["%s_%s" % (name, var)] = e
            print("%-15s identical %2d, differing %s; outer %s; max|dpsi| %s; dW/max|W| %s"
                  % (name + "_" + var, len(same), differ if differ else "none", e["outer"],
                     "%.3e" % e["dpsi_max"] if "dpsi_max" in e else "-",
                     "%.3e" % e["dW_rel_max"] if "dW_rel_max" in e else "-"), flush=True)
    rep["failed_cases"] = bad
    out = os.path.join(root, "regress_m1.json")
    lib2.save_json(out, rep)
    # figure: files per pair, and the largest change of psi (and W) per pair
    fs.use_style()
    names = list(rep["pairs"])
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 0.24*len(names) + 1.1))
    y = np.arange(len(names))
    ns = [len(rep["pairs"][c]["identical"]) for c in names]
    nd = [len(rep["pairs"][c]["differ"]) for c in names]
    axs[0].barh(y, ns, color=fs.PAL["blue"], label="identical")
    axs[0].barh(y, nd, left=ns, color=fs.PAL["red"], label="differing")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(names, fontsize=6)
    axs[0].invert_yaxis()
    axs[0].set_xlabel("files compared with the release's case")
    axs[0].legend(fontsize=5, loc="lower right")
    floor = 1e-17
    dp = [max(rep["pairs"][c].get("dpsi_max", 0.0), floor) for c in names]
    dw = [max(rep["pairs"][c].get("dW_rel_max", 0.0), floor) for c in names]
    axs[1].barh(y - 0.2, dp, height=0.4, color=fs.PAL["blue"], label=r"$\max|\Delta\psi|$")
    axs[1].barh(y + 0.2, dw, height=0.4, color=fs.PAL["orange"],
                label=r"$\max|\Delta W|/\max|W|$")
    axs[1].set_xscale("log")
    axs[1].set_xlim(floor, 1.0)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels([])
    axs[1].invert_yaxis()
    axs[1].set_xlabel("largest change against the release (bar at $10^{-17}$: none)")
    axs[1].legend(fontsize=5, loc="lower right")
    fig.tight_layout()
    p = os.path.join(root, "regress_m1")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
