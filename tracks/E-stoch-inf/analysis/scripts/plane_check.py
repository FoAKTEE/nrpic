#!/usr/bin/env python3
"""Constraint estimators of ../sfa.py on real AthenaK output: core's plane perturbation
(problems/scalar/plane.athinput, interface section 8 and test 3) at N = 16 and 32 with
the release executable, double-precision dumps every 0.25. Checks (journal 18:00):
the box statistics of H recomputed from the dumps equal the code's history; the box mean
of [H] per cell (sfa.ham_norm_cells, without At At) equals the code's [H]; the physical
rms of M equals the history; the ratios |H|/[H] and |M|/[M] converge at the order of the
stencils (6) between N = 16 and 32 at the start.

    plane_check.py --exe ATHENA --out DIR
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import sfa  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INP = os.path.join(sfa.REPO, "problems", "scalar", "plane.athinput")


def run(exe, out, n):
    d = os.path.join(out, f"N{n}")
    os.makedirs(d, exist_ok=True)
    args = [exe, "-i", INP, f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n // 2}",
            f"meshblock/nx1={n}", f"meshblock/nx2={n}", f"meshblock/nx3={n // 2}"]
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run(args, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                            env=dict(os.environ, OMP_NUM_THREADS="1")).returncode
    return d, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"runs": {}, "checks": []}
    series = {}
    for n in (16, 32):
        d, rc = run(a.exe, a.out, n)
        res["runs"][n] = rc
        hist = sfa.read_history(d)
        rows = []
        for f in sfa.dump_files(d):
            dd = sfa.read_dump(f)
            c = sfa.constraint_ratios(dd, hist)
            rows.append(c)
        series[n] = rows
    worst = dict(H_l1=0.0, H_rms=0.0, Hn=0.0, M_phys=0.0)
    for n, rows in series.items():
        for c in rows:
            worst["H_l1"] = max(worst["H_l1"], abs(c["H_l1"] / c["H_l1_hist"] - 1))
            worst["H_rms"] = max(worst["H_rms"], abs(c["H_rms"] / c["H_rms_hist"] - 1))
            worst["Hn"] = max(worst["Hn"], abs(c["Hn_mean"] / c["Hn_hist"] - 1))
            worst["M_phys"] = max(worst["M_phys"], abs(c["M_rms_phys"] / c["M_rms_hist"] - 1))
    res["worst_relative_difference_to_history"] = worst
    crit = dict(H_l1=1e-10, H_rms=1e-10, Hn=1e-6, M_phys=1e-6)
    for k, v in worst.items():
        res["checks"].append(dict(name=f"{k} dump vs history", value=v, criterion=crit[k],
                                  passed=bool(v <= crit[k])))
    for key in ("ratio_H_rms", "ratio_M_rms"):
        r16, r32 = series[16][0][key], series[32][0][key]
        order = np.log2(r16 / r32)
        res["checks"].append(dict(name=f"order of {key} at t = 0 (N = 16 to 32)", value=order,
                                  criterion="5 to 6.5", passed=bool(5 <= order <= 6.5)))
        orders_t = [np.log2(a_[key] / b_[key]) for a_, b_ in zip(series[16], series[32])]
        res[f"orders_{key}_per_dump"] = orders_t
    res["series"] = {n: rows for n, rows in series.items()}
    with open(os.path.join(a.out, "plane_check.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    for c in res["checks"]:
        print(f"{'PASS' if c['passed'] else 'FAIL'} {c['name']}: {c['value']:.3e} ({c['criterion']})")
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    cols = {16: fs.PAL["blue"], 32: fs.PAL["red"]}
    for n, rows in series.items():
        t = [c["time"] for c in rows]
        ax[0].semilogy(t, [c["ratio_H_rms"] for c in rows], "o-", color=cols[n],
                       label=f"N = {n}: rms $\\mathcal{{H}}$ / $\\langle[\\mathcal{{H}}]\\rangle$")
        ax[0].semilogy(t, [c["H_rms_hist"] / c["Hn_hist"] for c in rows], "x", color="k", ms=6)
        ax[1].semilogy(t, [c["ratio_M_rms"] for c in rows], "o-", color=cols[n],
                       label=f"N = {n}: rms $\\mathcal{{M}}$ / rms $[\\mathcal{{M}}]$")
    ax[0].plot([], [], "x", color="k", label="code's history")
    ax[0].set_xlabel("$t$")
    ax[1].set_xlabel("$t$")
    ax[0].set_ylabel("Hamiltonian ratio")
    ax[1].set_ylabel("momentum ratio ($[\\mathcal{M}]$ without $\\tilde A$ terms)")
    ax[0].legend(fontsize=7)
    ax[1].legend(fontsize=7)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    fs.save(fig, os.path.join(a.out, "fig_plane_constraint_ratios"))
    nfail = sum(not c["passed"] for c in res["checks"]) + sum(1 for v in res["runs"].values() if v)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
