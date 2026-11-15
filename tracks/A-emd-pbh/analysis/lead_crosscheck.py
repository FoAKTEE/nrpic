#!/usr/bin/env python3
"""Lead's independent cross-checks of the expanding-ball package (predictions L2-L6 of
tracks/A-emd-pbh/JOURNAL.md). Reference arithmetic and comparison only, no simulation.

L2  expball `Ball` against core's `python/nrpic/expanding_ball.Ball` (branch
    core/id-extrinsic, written independently): sharp marginally bound ball, M = 1, R_b = 8.
L3  core's format-2 evaluator (`nrpic.io.Table2`, the rule of the C++ reader) against
    expball's `lagrange4` on expball's data-set-1 table.
L4  turnaround, apparent-horizon and crunch proper times of core's bound test ball
    (M = 1, R_b = 5, e0 = 0.16) from three codes: expball `exact.Shells` (through an
    adapter), core `ltb_turnaround` / `ltb_radius`, and the closed-form cycloid below.
L5  the homogeneous core of data set 2 (Delta = 1, H = 1/16) by closed forms written here.
L6  trace K of the vacuum exterior of expball's ball against -(3/2) sqrt(2M/R^3).

Usage (worktree root):
    python3 tracks/A-emd-pbh/analysis/lead_crosscheck.py --core-python <dir with nrpic/> --out <dir>
"""

import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.special import hyp2f1

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(TRACK, "..", ".."))
DS1 = "/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-121749-90764e1"


def cycloid_times(m, E, R_i):
    """Closed-form proper times from the slice (shell at R_i expanding) for E < 0:
    turnaround, R = 2m on the way in, crunch; and R_max."""
    A = m / (-2.0 * E)                      # R = A (1 - cos eta)
    T0 = m / (-2.0 * E) ** 1.5              # t = T0 (eta - sin eta)
    eta_i = math.acos(1.0 - R_i / A)        # expanding branch
    t_i = T0 * (eta_i - math.sin(eta_i))
    eta_ah = 2.0 * math.pi - math.acos(1.0 - 2.0 * m / A)
    return dict(tau_ta=T0 * math.pi - t_i, tau_ah=T0 * (eta_ah - math.sin(eta_ah)) - t_i,
                tau_c=2.0 * math.pi * T0 - t_i, R_max=2.0 * A)


class BoundBallAdapter:
    """The minimum of expball's Ball interface that exact.Shells uses, for core's
    homogeneous bound ball (m = M (R/Rb)^3, E = -e0 (R/Rb)^2 inside)."""

    def __init__(self, M, Rb, e0):
        self.M, self.Rb, self.e0 = M, Rb, e0
        self.R_out = Rb
        self.t_i = float("nan")

    def at(self, R):
        R = np.atleast_1d(np.asarray(R, dtype=float))
        m = self.M * (R / self.Rb) ** 3
        E = -self.e0 * (R / self.Rb) ** 2
        return dict(m=m, E=E, v=np.sqrt(2 * m / R + 2 * E))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--core-python", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sys.path.insert(0, os.path.join(TRACK, "expball"))
    sys.path.insert(0, a.core_python)
    from expball import exact as XE, model as XM, table as XT   # noqa: E402
    from nrpic import expanding_ball as CB, io as CIO           # noqa: E402  (core's copy)
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs                            # noqa: E402
    res = {}

    # ---------------------------------------------------------------- L2
    xb = XM.Ball.from_HRb(0.5, 1.0)                 # Rb = 8, H = 1/16, sharp edge
    cb = CB.Ball(M=1.0, Rb=8.0, e0=0.0)
    r = np.linspace(0.01, 12.0, 6001)
    xf = xb.fields(r, ("u", "KL", "KT", "betar"))
    cf = cb.profiles(r)
    near = np.abs(r - 8.0) < 2e-3
    L2 = {}
    for k in ("u", "KL", "KT", "betar"):
        d = np.abs(xf[k] - cf[k])
        L2[k] = dict(max_away_from_edge=float(d[~near].max()), max_all=float(d.max()))
    L2["H_core"] = cb.H
    L2["H_expball"] = xb.H
    L2["pass"] = all(L2[k]["max_away_from_edge"] < 1e-8 for k in ("u", "KL", "KT", "betar"))
    res["L2"] = L2

    # ---------------------------------------------------------------- L3
    tab = os.path.join(DS1, "expball_flat_HRb0p5.tab")
    cols, hdr = XT.read_format2(tab)
    t_core = CIO.read_tab2(tab)
    rr = np.linspace(0.0, 14.0, 70001)
    xv = XT.Format2Table(cols, hdr)(rr)
    cv = dict(zip(("u", "KL", "KT", "alpha", "betar"), t_core(rr)))
    L3 = {k: float(np.max(np.abs(xv[k] - cv[k]))) for k in ("u", "KL", "KT", "alpha", "betar")}
    L3["breaks_in_header"] = list(t_core.breaks)
    # overshoot of the cubic through the KL jump at the edge (no break line in the file)
    ex = xb.fields(rr, ("KL",))["KL"]
    band = np.abs(rr - 8.0) < 0.01
    L3["KL_overshoot_near_edge"] = float(np.max(np.abs(cv["KL"][band] - ex[band])))
    L3["KL_err_away_from_edge"] = float(np.max(np.abs(cv["KL"][(~band) & (rr < 11.9)]
                                                      - ex[(~band) & (rr < 11.9)])))
    L3["pass"] = max(L3[k] for k in ("u", "KL", "KT", "alpha", "betar")) < 1e-13
    res["L3"] = L3

    # ---------------------------------------------------------------- L4
    M, Rb, e0 = 1.0, 5.0, 0.16
    cyc = cycloid_times(M, -e0, Rb)
    sh = XE.Shells(BoundBallAdapter(M, Rb, e0), np.array([Rb, 0.5 * Rb]))
    tta_core, Rmax_core = CB.ltb_turnaround(Rb, M, -e0)
    # crunch and horizon from core's ltb_radius: R(tau) root finding
    f_ah = lambda tau: float(CB.ltb_radius(np.array([Rb]), np.array([tau]), M, -e0)[0]) - 2.0 * M   # noqa: E731  (0-d input fails in core's ltb_radius)
    tau_ah_core = brentq(f_ah, float(tta_core), cyc["tau_c"] - 1e-9, xtol=1e-13)
    L4 = dict(cycloid=cyc,
              expball=dict(tau_ta=float(sh.tau_ta[0]), tau_ah=float(sh.tau_ah[0]),
                           tau_ah_cycloid=float(sh.tau_ah_cycloid()[0]),
                           tau_c=float(sh.tau_c[0]), R_max=float(sh.R_max[0]),
                           inner_shell_tau_ta=float(sh.tau_ta[1]), inner_shell_tau_c=float(sh.tau_c[1])),
              core=dict(tau_ta=float(tta_core), R_max=float(Rmax_core), tau_ah_by_root=tau_ah_core),
              core_journal_tau_ta=9.542)
    d1 = abs(L4["expball"]["tau_ta"] - cyc["tau_ta"])
    d2 = abs(L4["core"]["tau_ta"] - cyc["tau_ta"])
    d3 = abs(L4["expball"]["tau_ah"] - cyc["tau_ah"])
    d4 = abs(L4["core"]["tau_ah_by_root"] - cyc["tau_ah"])
    d5 = abs(L4["expball"]["tau_c"] - cyc["tau_c"])
    L4["max_disagreement"] = max(d1, d2, d3, d4, d5)
    L4["pass"] = L4["max_disagreement"] < 1e-9
    res["L4"] = L4

    # ---------------------------------------------------------------- L5
    H, Delta = 1.0 / 16.0, 1.0
    y = brentq(lambda yy: hyp2f1(0.5, 1.5, 2.5, yy) - math.sqrt(1.0 + Delta), 0.0, 0.999999, xtol=1e-15)
    # shell R: m = (H^2/2) R^3 (1+Delta), E = -y m/R; age on the slice t_i = 2/(3H)
    Rt = 2.4
    m = 0.5 * H ** 2 * Rt ** 3 * (1 + Delta)
    E = -y * m / Rt
    T0 = m / (-2 * E) ** 1.5
    t_i = 2.0 / (3.0 * H)
    L5 = dict(y=y, R_max_over_R_i=1.0 / y, tau_ta=math.pi * T0 - t_i, tau_c=2 * math.pi * T0 - t_i,
              tau_ah_core_edge=2 * math.pi * T0 - (4.0 / 3.0) * m * hyp2f1(0.5, 1.5, 2.5, -2 * E) - t_i,
              readme=dict(tau_ta=16.894, tau_c=44.454, R_max_over_R_i=1.340, tau_ah_core_edge=44.381))
    L5["pass"] = (round(L5["tau_ta"], 3) == 16.894 and round(L5["tau_c"], 3) == 44.454
                  and round(L5["R_max_over_R_i"], 3) == 1.340)
    # the same with expball's model and exact (data set 2 profile)
    xb2 = XM.Ball.from_HRb(0.5, 1.0, XM.SmoothTopHat(1.0, 0.3 * 8.0, 0.75 * 8.0))
    shells = XE.Shells(xb2, np.linspace(0.02, 8.0, 400))
    fh = shells.first_horizon()
    L5["expball_first_horizon"] = fh
    L5["expball_tau_ta_innermost"] = float(shells.tau_ta[0])
    L5["expball_tau_c_innermost"] = float(shells.tau_c[0])
    # with the C^4 edge taper of the proposed scouting data (w = 0.2 R_b): interior unchanged
    xb2t = XM.Ball.from_HRb(0.5, 1.0, XM.SmoothTopHat(1.0, 0.3 * 8.0, 0.75 * 8.0), edge_width=1.6)
    sh_t = XE.Shells(xb2t, np.linspace(0.02, 8.0, 400))
    L5["taper_w1p6_first_horizon"] = sh_t.first_horizon()
    L5["taper_w1p6_M"] = xb2t.M
    L5["taper_w1p6_rbar_matter"] = xb2t.matter_rbar()
    res["L5"] = L5

    # ---------------------------------------------------------------- L6
    Rv = np.linspace(8.05, 40.0, 500)
    fv = xb.fields(Rv, ("KL", "KT"))
    K = fv["KL"] + 2 * fv["KT"]
    Kex = -1.5 * np.sqrt(2 * xb.M / Rv ** 3)
    inside = xb.fields(np.array([7.99]), ("KL", "KT"))
    L6 = dict(max_rel=float(np.max(np.abs(K / Kex - 1))),
              K_inside_over_H=float((inside["KL"][0] + 2 * inside["KT"][0]) / xb.H),
              K_outside_at_edge_over_H=float(-1.5 * math.sqrt(2 * xb.M / 8.0 ** 3) / xb.H))
    L6["pass"] = L6["max_rel"] < 1e-13
    res["L6"] = L6

    with open(os.path.join(a.out, "crosscheck.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)

    # ---------------------------------------------------------------- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.2))
    fig.subplots_adjust(left=0.10, right=0.97, bottom=0.09, top=0.95, wspace=0.32, hspace=0.38)
    ax = fig.add_subplot(2, 2, 1)
    for k, c in (("KL", fs.PAL["blue"]), ("KT", fs.PAL["red"]), ("betar", fs.PAL["yellow"])):
        d = np.abs(xf[k] - cf[k])
        ax.semilogy(r, np.maximum(d, 1e-18), color=c, label=k)
    ax.axvline(8.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$\bar r\,/M$")
    ax.set_ylabel("|expball - core|")
    ax.set_title("L2: two generators, sharp ball", fontsize=10)
    ax.legend(ncol=3, loc="upper left")
    ax.set_ylim(1e-18, 1e0)

    ax = fig.add_subplot(2, 2, 2)
    zoom = (rr > 7.97) & (rr < 8.03)
    ax.plot(rr[zoom], ex[zoom] / xb.H, color=fs.PAL["blue"], label="exact")
    ax.plot(rr[zoom], cv["KL"][zoom] / xb.H, color=fs.PAL["red"], ls="--", label="table, no break")
    ax.set_xlabel(r"$\bar r\,/M$")
    ax.set_ylabel(r"$K_L/H$")
    ax.set_title("L3: cubic through the edge jump", fontsize=10)
    ax.legend(loc="center right")

    ax = fig.add_subplot(2, 2, 3)
    tau = np.linspace(0.0, cyc["tau_c"], 2000)
    Rc = CB.ltb_radius(Rb, tau, M, -e0)
    adapter = XE.Shells(BoundBallAdapter(M, Rb, e0), np.array([Rb]))
    Rx = adapter.R(tau)[0]
    ax.plot(tau, Rc, color=fs.PAL["blue"], label="core ltb_radius")
    ax.plot(tau, Rx, color=fs.PAL["red"], ls="--", label="expball Shells")
    ax.axhline(2 * M, **fs.GUIDE)
    for key, lab in (("tau_ta", "turnaround"), ("tau_ah", "R = 2M"), ("tau_c", "crunch")):
        ax.axvline(cyc[key], **fs.MASK_LINE)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$R_{\rm surface}\,/M$")
    ax.set_title("L4: bound ball surface shell", fontsize=10)
    ax.legend(loc="lower left")

    ax = fig.add_subplot(2, 2, 4)
    tt = np.linspace(0, 46, 1500)
    sel = [0, 60, 119, 137, 160, 220, 300]
    Rs = shells.R(tt)
    cols = fs.series_colors(len(sel))
    for j, k in enumerate(sel):
        ax.plot(tt, Rs[k], color=cols[j], lw=1.0, label=fr"$R_i={shells.R_i[k]:.2f}$")
    ax.axvline(L5["tau_ta"], **fs.MASK_LINE)
    ax.axvline(fh["tau_ah"], **fs.GUIDE)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$R\,/M$")
    ax.set_title("L5: data set 2 shells", fontsize=10)
    ax.legend(ncol=2, loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_crosscheck"))
    for k in ("L2", "L3", "L4", "L5", "L6"):
        print(k, "pass" if res[k]["pass"] else "FAIL")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
