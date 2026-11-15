#!/usr/bin/env python3
"""Diagnostic of T11(a): where does the mean sum_P per step of the drifting gas differ
from (1/2) N (rho/gamma) sigma <v_Mol> dt / gamma? Splits sum_P = sum_W x (mean Moller
speed of the tested pairs) and compares
  sum_W per step      with (1/2) N rho_lab sigma dt          (cell occupation),
  sum_P / sum_W       with <v_Mol>_rest(theta_s) / gamma_s^2  (tested pairs),
  random pairs of the initial snapshot (lab-frame Moller speed, 4e6 pairs, Monte Carlo)
                      with the same value                      (the sample itself).
Standard errors from the step-to-step scatter (history) and the pair scatter (MC).

    python3 t11diag.py T11_RUN_DIR
"""
import argparse
import json
import os
import sys

import numpy as np

import boxlib as bl
import kinematics as kin
import rate
import t11


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    a = ap.parse_args()
    out = bl.outdir()
    res = {}
    rs = np.random.default_rng(7)
    for seed in (1, 2):
        rd = os.path.join(a.rundir, f"T11ab_s{seed}")
        h = bl.coll_history(rd)
        s0 = bl.snap.read_snapshot(bl.snapshots(rd)[0])
        m0 = t11.lab_moments(s0["u"])
        th, b = t11.solve_theta_beta(m0["W"][0], m0["ux"][0], (1.0, 0.6))
        g2 = 1.0 / (1.0 - b * b)
        vref = float(rate.vmol_mean(th)) / g2
        N = int(h["n_part"][0])
        dt = float(np.diff(np.concatenate([[0.0], h["time"]])).mean())
        w0 = 0.5 * N * 1.0 * t11.SIG * dt
        sw = h["sum_W"] / w0
        vt = h["sum_P"] / h["sum_W"] / vref
        i = rs.integers(0, N, 4_000_000)
        j = rs.integers(0, N, 4_000_000)
        ok = i != j
        vm = kin.vmol(s0["u"][i[ok]], s0["u"][j[ok]])
        res[f"s{seed}"] = dict(
            theta_s=th, beta_s=b, vref=vref,
            sumW_ratio=float(sw.mean()), sumW_se=float(sw.std(ddof=1) / np.sqrt(sw.size)),
            vtested_ratio=float(vt.mean()), vtested_se=float(vt.std(ddof=1) / np.sqrt(vt.size)),
            sumP_ratio=float((h["sum_P"] / (w0 * vref)).mean()),
            mc_pairs_ratio=float(vm.mean() / vref),
            mc_pairs_se=float(vm.std() / np.sqrt(vm.size) / vref))
        r = res[f"s{seed}"]
        r["z_sumW"] = (r["sumW_ratio"] - 1) / r["sumW_se"]
        r["z_vtested"] = (r["vtested_ratio"] - 1) / r["vtested_se"]
        r["z_mc"] = (r["mc_pairs_ratio"] - 1) / r["mc_pairs_se"]
    bl.save_json(os.path.join(out, "t11diag.json"), res)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    sys.exit(main())
