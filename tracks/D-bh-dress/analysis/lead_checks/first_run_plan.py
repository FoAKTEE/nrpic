#!/usr/bin/env python3
"""Predicted observables and cost of the first full-relativity run of Track D (the
Einstein-Straus data set of D-pre-1 evolved in AthenaK after core/id-extrinsic is merged).

Exact references from es_reference.csv of run D-bh-dress-20261115-043445-b782009 (areal
radius against dust proper time of the wall, the outer dust edge, the tracers; scale
factor of the EdS plateau; mass inside the wall). Lapse estimate for 1+log slicing in the
homogeneous plateau with zero shift: d alpha/dt = -2 alpha K, K = -3H, d tau = alpha dt,
hence alpha = 1 + 6 ln a (not exp(6 H t), which holds only while alpha ~ 1).
Cost: the scoping model of scope/scoping_estimates.py (part_c, measured throughput).
Output: first_run_plan.json, first_run_plan.png.
"""
import argparse
import importlib.util
import json
import math
import os
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/D-bh-dress"
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle  # noqa: E402

DS = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-043445-b782009"
RHO0 = 3.718183334770104e-06      # es.json summary.rho0
FLOOR_M16 = 2.5e-5                # D-pre-4, M/16, windows from 50 M ending before 210 M
FLOOR_M8_T100 = 2.8e-5            # D-pre-4, M/8, from t0 = 100 M, before 210 M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = np.loadtxt(os.path.join(DS, "es_reference.csv"), delimiter=",")
    tau, Rw, Rsch, Rout, ap_, minw = d[:, 0], d[:, 1], d[:, 2], d[:, 3], d[:, 4], d[:, 5]
    trc = d[:, 6:]
    res = dict(dataset="D-bh-dress-20261115-043445-b782009")
    for T in (50.0, 100.0, 150.0, 200.0):
        res[f"tau={T:g}"] = dict(R_wall=float(np.interp(T, tau, Rw)),
                                 R_wall_ratio=float(np.interp(T, tau, Rw) / Rw[0]),
                                 a_plateau=float(np.interp(T, tau, ap_)),
                                 R_outer=float(np.interp(T, tau, Rout)),
                                 alpha_1plog_plateau=float(1 + 6 * math.log(np.interp(T, tau, ap_))))
    res["m_inside_wall_maxdev"] = float(np.max(np.abs(minw - 1.0)))
    cross = {}
    for k in range(trc.shape[1]):
        below = np.where(trc[:, k] <= 2.0)[0]
        cross[f"tracer{k}_R0={trc[0, k]:.1f}"] = float(tau[below[0]]) if len(below) else None
    res["tau_reach_R=2M"] = cross
    # truncated variant: outer dust edge at 60 M (sharp estimate of the enclosed mass)
    m60 = 1.0 + 4 * math.pi / 3 * RHO0 * (60.0 ** 3 - 40.0 ** 3)
    res["variant_outer60"] = dict(m_enclosed=m60, R_outer_tau200=(60.0 ** 1.5 + 1.5 * math.sqrt(2 * m60) * 200.0) ** (2 / 3),
                                  N_hp1=4 * math.pi / 3 * (60.0 ** 3 - 36.0 ** 3))
    # cost model of the scoping package
    spec = importlib.util.spec_from_file_location("se", os.path.join(WT, "tracks/D-bh-dress/scope/scoping_estimates.py"))
    se = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(se)
    cwd = os.getcwd()
    os.chdir(WT)
    C = se.part_c()
    os.chdir(cwd)
    cost = C["cost"]
    rz = C["rz_amr"]
    rows = []
    for name, T, dx, Rb, dxb, N in [
        ("as generated (dust to 106 M), M/16, dx_ball 2M, hp 1M", 200.0, 1 / 16, res["tau=200"]["R_outer"], 2.0, 4.746e6),
        ("as generated, M/8, dx_ball 2M, hp 1M", 200.0, 1 / 8, res["tau=200"]["R_outer"], 2.0, 4.746e6),
        ("outer edge 60 M, M/16, dx_ball 2M, hp 1M", 200.0, 1 / 16, res["variant_outer60"]["R_outer_tau200"], 2.0, res["variant_outer60"]["N_hp1"]),
        ("outer edge 60 M, M/8, dx_ball 2M, hp 1M", 200.0, 1 / 8, res["variant_outer60"]["R_outer_tau200"], 2.0, res["variant_outer60"]["N_hp1"]),
        ("outer edge 60 M, M/8, dx_ball 2M, hp 2M (scouting)", 200.0, 1 / 8, res["variant_outer60"]["R_outer_tau200"], 2.0, res["variant_outer60"]["N_hp1"] / 8),
    ]:
        c = cost(T, dx, ball_half=1.25 * Rb, dx_ball=dxb, npart=N, rz=rz)
        c["name"] = name
        rows.append({k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in c.items()})
    res["cost"] = rows
    res["floor"] = dict(M16_50_210=FLOOR_M16, M8_100_210=FLOOR_M8_T100)
    with open(os.path.join(a.out, "first_run_plan.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    figstyle.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8))
    ax = axs[0]
    ax.plot(tau, Rw / Rw[0], label=r"wall $R_w/R_w(0)$")
    ax.plot(tau, ap_, ls="--", label=r"plateau $a(\tau)$")
    ax.axvspan(50, 200, color="0.9")
    ax.set_xlim(0, 400)
    ax.set_xlabel(r"dust proper time $\tau/M$")
    ax.set_ylabel("expansion factor")
    ax.legend(frameon=False)
    ax = axs[1]
    ax.axhline(0, color="k", lw=0.8, label="exact (Birkhoff)")
    ax.fill_between([50, 200], -FLOOR_M16, FLOOR_M16, color="C0", alpha=0.3, label=r"D-pre-4 floor, $M/16$")
    ax.fill_between([100, 200], -FLOOR_M8_T100, FLOOR_M8_T100, color="C1", alpha=0.3, label=r"D-pre-4 floor, $M/8$ from 100 $M$")
    ax.set_xlim(0, 250)
    ax.set_ylim(-1e-4, 1e-4)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"predicted $M_{\rm AH}(t)/M_{\rm AH}(t_0)-1$")
    ax.legend(frameon=False, fontsize=8)
    ax = axs[2]
    ax.plot(tau, 1 + 6 * np.log(ap_), label=r"1+log: $1+6\ln a$")
    ax.plot(tau, np.exp(6 * 5.5812e-3 * tau), ls=":", label=r"$e^{6Ht}$ (linearized)")
    ax.set_ylim(0, 12)
    ax.set_xlim(0, 400)
    ax.set_xlabel(r"$\tau/M$")
    ax.set_ylabel(r"lapse in the dust plateau")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "first_run_plan.png"), dpi=150)


if __name__ == "__main__":
    main()
