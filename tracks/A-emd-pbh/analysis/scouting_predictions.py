#!/usr/bin/env python3
"""Predictions for the first two full-relativity scouting runs of Track A (G1 package,
prediction L8 of tracks/A-emd-pbh/JOURNAL.md). Reference arithmetic only.

Data: data set 2t (expball smoothed top-hat core, Delta = 1 inside R1 = 2.4 M, compensated
at R2 = 6 M, Einstein-de Sitter envelope with H R_b = 0.5, C^4 edge taper of half width
1.5 M; M ~ 1.01). The invariant predictions (proper times along dust world lines) come
from expball/exact.py; this script adds what depends on the code's gauge:

  SR-1, geodesic slicing (lapse 1, shift 0 held fixed): t = tau for every particle; the
        radial coordinate speed of light in the homogeneous core is R_i/R(tau) (comoving
        coordinates), so the step must shrink: cfl <= C_max R/R_i with C_max = 0.618
        (von Neumann limit with diss = 0.5, gauge T2, run A-emd-pbh-20261115-113755-cac3c4b).
  SR-2, conformal-time lapse (d_t alpha = -(1/3) alpha^2 K): in the homogeneous core
        alpha = R/R_i, so coordinate time t = int dtau R_i/R; the Einstein-de Sitter
        envelope has alpha = a too; coordinate speed of light ~1.

Cost from core's measured card time per cell and step (run core-20261115-040406-1311b8e:
192^3 cells, dx = M/2, cfl 0.25, t = 10 M, 0.01278 card-hours, lattice of one site per cell).

Usage: python3 tracks/A-emd-pbh/analysis/scouting_predictions.py --out <dir>
"""

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "expball"))
sys.path.insert(0, os.path.join(REPO, "python"))
from expball import exact as XE, model as XM   # noqa: E402
from nrpic import figstyle as fs                 # noqa: E402

C_MAX = 0.618            # gauge T2, scalar mode, diss = 0.5, RK4
COST_PER_CELL_STEP = 0.01278 * 3600.0 / (192 ** 3 * (10.0 / (0.25 * 0.5)))   # card-s per cell-step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    ball = XM.Ball.from_HRb(0.5, 1.0, XM.SmoothTopHat(1.0, 2.4, 6.0), edge_width=1.5)
    # invariant predictions, shells refined around the first trapped sphere
    Ri = np.concatenate([np.linspace(0.01, 2.4, 240), np.linspace(2.401, 3.4, 2000),
                         np.linspace(3.41, ball.R_out, 600)])
    sh = XE.Shells(ball, Ri)
    fh = sh.first_horizon()
    core = XE.Shells(ball, np.array([1.0]))
    T0 = float(core.T0[0])
    tau_ta, tau_c = float(core.tau_ta[0]), float(core.tau_c[0])
    A_over_Ri = float(core.R_max[0]) / 2.0          # R = A (1 - cos eta), per unit R_i
    age_i = float(core.age_i[0])
    eta_i = math.acos(1.0 - 1.0 / A_over_Ri)

    def eta_of_tau(tau):
        q = (age_i + np.asarray(tau, dtype=float)) / T0
        return XE._solve_eta(np.clip(q, 0, 2 * math.pi), True)

    def a_core(tau):
        return A_over_Ri * (1.0 - np.cos(eta_of_tau(tau)))

    # SR-1 geodesic slicing: t = tau; step limit
    taus = np.linspace(0.0, fh["tau_ah"] + 0.02, 20001)
    acore = a_core(taus)
    cfl_needed = C_MAX * np.minimum(acore, 1e9)
    i_040 = int(np.argmax(acore < 0.25 / C_MAX)) if np.any(acore < 0.25 / C_MAX) else None
    # staged plan: cfl_k = 0.25 / 2^k; stage k lasts while C_MAX a_core >= cfl_k
    stages = []
    t0, cfl = 0.0, 0.25
    t_end = fh["tau_ah"] + 0.02
    while t0 < t_end - 1e-9:
        bad = taus[(taus > t0) & (cfl_needed < cfl)]
        t1 = min(float(bad.min()) if bad.size else t_end, t_end)
        if t1 > t0:
            stages.append(dict(t_from=round(t0, 4), t_to=round(t1, 4), cfl=cfl))
        t0, cfl = t1, 0.5 * cfl
    dx = 0.5
    cells_sr1 = 256 ** 3                          # half-width 64 M, dx = M/2
    steps_sr1 = sum((s["t_to"] - s["t_from"]) / (s["cfl"] * dx) for s in stages)
    card_sr1 = steps_sr1 * cells_sr1 * COST_PER_CELL_STEP / 3600.0

    # SR-2 conformal-time lapse: coordinate time of the core
    eta_ta, eta_ah_core = math.pi, float(eta_of_tau(np.array([fh["tau_ah"]]))[0])
    tc_scale = T0 / A_over_Ri                      # t = (T0 R_i/A) Delta eta
    t_coord = dict(core_turnaround=tc_scale * (eta_ta - eta_i),
                   core_at_first_trapped_tau=tc_scale * (eta_ah_core - eta_i),
                   core_crunch=tc_scale * (2 * math.pi - eta_i))
    steps_sr2 = (t_coord["core_at_first_trapped_tau"] + 2.0) / (0.25 * dx)
    card_sr2 = steps_sr2 * cells_sr1 * COST_PER_CELL_STEP / 3600.0
    # envelope (Einstein-de Sitter shells) and the ball edge
    H = ball.H
    edge_R = lambda tau: ball.R_out * (1.0 + 1.5 * H * tau) ** (2.0 / 3.0)   # noqa: E731

    out = dict(
        data="expball SmoothTopHat(delta_c = 1, R1 = 2.4, R2 = 6), H R_b = 0.5, R_b = 8, taper w = 1.5 M",
        M_total=ball.M, rbar_matter=ball.matter_rbar(), t_i=ball.t_i, H=H,
        invariant=dict(core_tau_turnaround=tau_ta, core_R_max_over_R_i=2 * A_over_Ri,
                       first_trapped=dict(tau=fh["tau_ah"], R_i=fh["R_i"], m=fh["m"], R_AH=2 * fh["m"],
                                          rbar_i=float(ball.rbar_of_R(np.array([fh["R_i"]]))[0])),
                       core_edge_trapped_tau=float(XE.Shells(ball, np.array([2.4])).tau_ah[0]),
                       core_crunch_tau=tau_c,
                       core_R_over_R_i_at_first_trapped=float(a_core(np.array([fh["tau_ah"]]))[0]),
                       ball_edge_R_at_first_trapped=edge_R(fh["tau_ah"])),
        SR1_geodesic=dict(t_equals_tau=True,
                          tau_where_cfl_0p25_reaches_limit=(float(taus[i_040]) if i_040 is not None else None),
                          cfl_stages=stages, steps=steps_sr1, cells=cells_sr1,
                          card_hours=card_sr1),
        SR2_conformal_time=dict(coordinate_times=t_coord, steps=steps_sr2, cells=cells_sr1,
                                card_hours=card_sr2, alpha_core_at_turnaround=2 * A_over_Ri),
        cost_per_cell_step_card_s=COST_PER_CELL_STEP,
        L8_estimates=dict(core_turnaround=13.8, core_at_first_trapped_tau=49.5, core_crunch=54.9,
                          cfl0p25_limit_tau=42.0),
    )
    rel = {k: abs(t_coord[k] / out["L8_estimates"][k] - 1) for k in t_coord}
    out["L8_rel_dev"] = rel
    out["L8_pass"] = all(v < 0.01 for v in rel.values())
    with open(os.path.join(a.out, "scouting_predictions.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)

    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.92, wspace=0.30)
    ax = fig.add_subplot(1, 2, 1)
    tt = np.linspace(0, 46, 2000)
    Rs = sh.R(tt)
    for Rlab, c in ((1.0, fs.PAL["blue"]), (2.4, fs.PAL["red"]), (fh["R_i"], fs.PAL["yellow"]),
                    (4.0, fs.PAL["green"] if "green" in fs.PAL else "g"), (6.0, "grey")):
        k = int(np.argmin(np.abs(Ri - Rlab)))
        ax.plot(tt, Rs[k], color=c, label=fr"$R_i={Ri[k]:.2f}$")
        ax.plot(tt, 2 * sh.m[k] + 0 * tt, color=c, ls=":", lw=1.0)
    ax.axvline(tau_ta, **fs.MASK_LINE)
    ax.axvline(fh["tau_ah"], **fs.GUIDE)
    ax.set_xlabel(r"proper time $\tau\,/M$")
    ax.set_ylabel(r"areal radius $R\,/M$")
    ax.set_ylim(0, 9)
    ax.legend(ncol=2, loc="upper left", fontsize=8)
    ax.set_title("invariant: shells (dotted: 2m)", fontsize=10)
    ax = fig.add_subplot(1, 2, 2)
    ax.semilogy(taus, acore, color=fs.PAL["blue"], label=r"$R/R_i$ (core)")
    ax.semilogy(taus, cfl_needed, color=fs.PAL["red"], label=r"largest cfl, geodesic slicing")
    for s in stages:
        ax.plot([s["t_from"], s["t_to"]], [s["cfl"], s["cfl"]], color="k", lw=1.5)
    ax.axvline(fh["tau_ah"], **fs.GUIDE)
    ax.set_xlabel(r"$t=\tau\,/M$ (geodesic slicing)")
    ax.set_ylabel(r"$R/R_i$ and cfl")
    ax.set_ylim(1e-3, 3)
    ax.legend(loc="lower left")
    ax.set_title("SR-1 step plan (black: cfl stages)", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_scouting_predictions"))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
