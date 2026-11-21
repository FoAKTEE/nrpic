#!/usr/bin/env python3
"""Test T5 of tracks/core/JOURNAL-idsolve.md: the initial-data solve on a card against
the same case on a processor.

    analyze_card.py [--case gauss_code_n64]

Reads the run ids from runs.json (processor) and runs_card.json (card), compares the
iteration records (<basename>.idsolve.txt) and the solved fields (<basename>.idsolve.bin),
writes card_numbers.json and figs/card_vs_cpu (PDF and PNG).
"""
import argparse
import os
import sys

import numpy as np

import idlib
from nrpic import figstyle as fs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="gauss_code_n64")
    a = ap.parse_args()
    cpu = idlib.load_json(os.path.join(idlib.HERE, "runs.json"))[a.case]
    gpu = idlib.load_json(os.path.join(idlib.HERE, "runs_card.json"))[a.case + "_card"]
    base = "gauss"
    out = dict(case=a.case, cpu_run=cpu["run_id"], card_run=gpu["run_id"])
    tc, lc = idlib.read_idsolve_txt(os.path.join(idlib.run_dir(cpu["run_id"]),
                                                 base + ".idsolve.txt"))
    tg, lg = idlib.read_idsolve_txt(os.path.join(idlib.run_dir(gpu["run_id"]),
                                                 base + ".idsolve.txt"))
    out["iterations_cpu"] = int(tc.shape[0])
    out["iterations_card"] = int(tg.shape[0])
    out["cg_steps_cpu"] = [int(v) for v in tc[:, 10]]
    out["cg_steps_card"] = [int(v) for v in tg[:, 10]]
    out["v_cycles_cpu"] = [int(v) for v in tc[:, 11]]
    out["v_cycles_card"] = [int(v) for v in tg[:, 11]]
    out["summary_cpu"] = lc
    out["summary_card"] = lg
    n = min(tc.shape[0], tg.shape[0])
    out["rel_residual_cpu"] = [float(v) for v in tc[:, 1]]
    out["rel_residual_card"] = [float(v) for v in tg[:, 1]]
    out["max_rel_diff_residual_history"] = float(
        np.max(np.abs(tc[:n, 1] - tg[:n, 1])/np.abs(tc[:n, 1])))
    dc = idlib.read_idsolve_bin(os.path.join(idlib.run_dir(cpu["run_id"]),
                                             base + ".idsolve.bin"))
    dg = idlib.read_idsolve_bin(os.path.join(idlib.run_dir(gpu["run_id"]),
                                             base + ".idsolve.bin"))
    dpsi = dg["psi"] - dc["psi"]
    out["max_abs_diff_psi"] = float(np.abs(dpsi).max())
    out["max_rel_diff_psi"] = float(np.abs(dpsi/dc["psi"]).max())
    out["max_abs_diff_psi_minus_1_rel"] = float(np.abs(dpsi).max()/np.abs(dc["psi"] - 1).max())
    out["max_abs_diff_E_rel"] = float(np.abs(dg["E"] - dc["E"]).max()/np.abs(dc["E"]).max())
    out["max_H_cpu"] = float(np.abs(dc["H"]).max())
    out["max_H_card"] = float(np.abs(dg["H"]).max())
    idlib.save_json(os.path.join(idlib.HERE, "card_numbers.json"), out)
    for k, v in out.items():
        if not isinstance(v, list):
            print("%-32s %s" % (k, v))

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.3)
    ax = axs[0]
    ax.semilogy(np.arange(tc.shape[0]), tc[:, 1], color="k", marker="o", ms=4,
                label="processor")
    ax.semilogy(np.arange(tg.shape[0]), tg[:, 1], color=fs.PAL["red"], marker="x",
                ls="--", label="card (A100)")
    ax.axhline(1.0e-10, color="0.5", lw=0.8, ls=":")
    ax.set_xlabel("outer iteration")
    ax.set_ylabel(r"max$|F|$ / scale")
    ax.set_title("Gaussian, 64 cells, mode code", fontsize=10)
    ax.legend(fontsize=8)
    ax = axs[1]
    r, dx, _ = idlib.mesh_r(dc)
    ax.semilogy(r.ravel(), np.abs(dpsi).ravel() + 1e-20, ",", color=fs.PAL["blue"])
    ax.set_xlabel(r"$r$")
    ax.set_ylabel(r"$|\psi_{\rm card} - \psi_{\rm processor}|$")
    ax.set_title("solved conformal factor", fontsize=10)
    fs.save(fig, os.path.join(idlib.FIGS, "card_vs_cpu"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
