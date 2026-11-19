#!/usr/bin/env python3
"""Test T4 of tracks/core/JOURNAL-oblate.md (entry 7): the Newtonian reference of the
oblate collapse in AthenaK (pusher = newton) with the particles of T3, against the
homogeneous spheroid of newton_spheroid.py.

    newton_mode.py --run n64=DIR --run n128=DIR [--out DIR] [--figdir DIR]

Per run, from the files of the code:
  obl.part.NNNNN.bin   rms height z_rms, rms cylindrical radius R_rms, fraction of the
                       particles on the other side of the equatorial plane from where
                       they started (by tag); time t_p of the smallest z_rms
  obl.newton.hst       energy K + W (particle sum of W), Poisson defect, V cycles
  athena.log           processor time
Reference: the homogeneous spheroid with the total rest mass of the particles as the
Newtonian mass (times scale with M^(-1/2)); z_rms = |b|/sqrt(5), R_rms = a sqrt(2/5).
Writes newton_mode.json into --out (default $NRPIC_RUN_DIR) and the figure
figs/oblate_newton.{png,pdf}.
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from nrpic import figstyle as fs  # noqa: E402
from nrpic.newton import read_newton_hst  # noqa: E402
import collapse_analysis as ca  # noqa: E402  (particle_history, BASE = "obl")
import newton_spheroid as newt  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LABEL = {"n64": r"$64^3$, cells $M/2$", "n128": r"$128^3$, cells $M/4$"}
COLOR = {"n64": fs.PAL["yellow"], "n128": fs.PAL["red"]}
A0, E = 10.0, 0.9
B0 = A0 * math.sqrt(1.0 - E * E)


def cpu_time(d):
    p = os.path.join(d, "athena.log")
    if not os.path.exists(p):
        return None
    m = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", open(p, errors="replace").read())
    return float(m[-1]) if m else None


def crossing_times(files):
    """First snapshot time at which each particle is on the other side of z = 0 from
    where it started (nan: never), its starting height over the local half-thickness of
    the spheroid, |z_0|/(b sqrt(1 - R_0^2/a^2)), and its starting cylindrical radius R_0,
    in the order of the first snapshot."""
    t0, d0, tag0, _ = ca.read_snapshot(files[0])
    n = tag0.max() + 1
    z0 = np.full(n, np.nan)
    z0[tag0] = d0[:, 2]
    R0 = np.full(n, np.nan)
    R0[tag0] = np.hypot(d0[:, 0], d0[:, 1])
    tc = np.full(n, np.nan)
    for p in files[1:]:
        t, d, tag, _ = ca.read_snapshot(p)
        new = (np.sign(d[:, 2]) != np.sign(z0[tag])) & ~np.isfinite(tc[tag])
        tc[tag[new]] = t
    half = B0 * np.sqrt(np.clip(1.0 - (R0 / A0) ** 2, 1e-6, None))
    return tc[tag0], (np.abs(z0) / half)[tag0], R0[tag0]


def reference(M):
    sol = newt.evolve(A0, B0, M=M, tmax=40.0, amin=0.02)
    t = sol.t
    a, b = np.abs(sol.y[0]), np.abs(sol.y[1])
    return dict(t=t, zr=b / B0, Rr=a / A0, t_p=float(sol.t_events[1][0]),
                a_p=float(sol.y_events[1][0][0]), vb_p=float(sol.y_events[1][0][3]))


def analyse(name, d, ref):
    ph, files = ca.particle_history(d)
    t, n, zr, Rr, cr = ph[:, 0], ph[:, 1], ph[:, 2], ph[:, 3], ph[:, 4]
    z0, R0 = zr[0], Rr[0]
    k = int(np.argmin(zr))
    t_p = float(t[k])
    h = read_newton_hst(os.path.join(d, "obl.newton.hst"))
    th, Et = h["time"], h["K"] + h["W"]
    W0 = abs(h["W"][0])
    dE = (Et - Et[0]) / W0
    before = th <= t_p - 1.0
    upto2 = th <= t_p + 2.0
    def at(tt, arr):
        j = int(np.argmin(np.abs(t - tt)))
        return float(arr[j]), float(t[j])
    cr1, tc1 = at(t_p + 1.0, cr)
    # the second moment of the history (every hist_dcycle cycles): t_p on a finer grid
    jz = int(np.argmin(h["I_zz"]))
    # first crossing time of every particle (by tag, on the snapshot grid), and how it
    # depends on the starting height |z_0| (quartiles of |z_0| / local half-thickness)
    tc, z0n, R0p = crossing_times(files)
    def by_bins(v):
        """10th, 50th, 90th percentile of the crossing time in the bins of v cut at its
        10, 25, 50, 75, 90 per cent quantiles."""
        q = np.quantile(v, [0.1, 0.25, 0.5, 0.75, 0.9])
        b = np.digitize(v, q)
        return dict(edges=[float(x) for x in q],
                    t_cross_10_50_90=[[float(x) for x in np.nanquantile(tc[b == i], [0.1, 0.5, 0.9])]
                                      for i in range(6)])
    out = dict(
        dir=d, snapshots=len(files), particles_first=int(n[0]), particles_last=int(n[-1]),
        z_rms0=float(z0), R_rms0=float(R0),
        z_rms0_homogeneous=B0 / math.sqrt(5.0), R_rms0_homogeneous=A0 * math.sqrt(0.4),
        t_p=t_p, t_p_reference=ref["t_p"], t_p_minus_reference=t_p - ref["t_p"],
        z_rms_min_over_initial=float(zr[k] / z0), z_rms_min=float(zr[k]),
        R_rms_at_t_p_over_initial=float(Rr[k] / R0),
        R_ratio_reference_at_pancake=ref["a_p"] / A0,
        crossed_at_t_p_plus_1=cr1, time_of_that_snapshot=tc1,
        crossed_max=float(np.max(cr)),
        t_p_history_Izz=float(h["time"][jz]),
        t_cross_10_50_90=[float(v) for v in np.nanquantile(tc, [0.1, 0.5, 0.9])],
        never_crossed=int(np.sum(~np.isfinite(tc))),
        crossing_by_z0_over_halfthickness=by_bins(z0n),
        crossing_by_R0=by_bins(R0p),
        z_rms_last_over_initial=float(zr[-1] / z0), R_rms_last_over_initial=float(Rr[-1] / R0),
        t_last=float(t[-1]),
        W0=float(h["W"][0]), mass=float(h["mass"][0]),
        dE_over_W0_max_before_t_p_minus_1=float(np.max(np.abs(dE[before]))),
        dE_over_W0_max_to_t_p_plus_2=float(np.max(np.abs(dE[upto2]))),
        dE_over_W0_max_all=float(np.max(np.abs(dE))), dE_over_W0_last=float(dE[-1]),
        mg_defect_max=float(np.max(h["mg_defect"])) if "mg_defect" in h else None,
        cpu_time_s=cpu_time(d))
    series = dict(t=t, zr=zr / z0, Rr=Rr / R0, cr=cr, th=th, dE=dE)
    return out, series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="name=DIR")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--figdir", default=os.path.join(HERE, "figs"))
    a = ap.parse_args()
    runs = [r.split("=", 1) for r in a.run]
    # the Newtonian mass is the rest mass of the particles, read from the first history
    M = read_newton_hst(os.path.join(runs[0][1], "obl.newton.hst"))["mass"][0]
    ref = reference(M)
    res = dict(reference=dict(M=float(M), t_p=ref["t_p"], a_at_pancake=ref["a_p"],
                              vb_at_pancake=ref["vb_p"],
                              note="homogeneous spheroid, newton_spheroid.py, M = sum m"),
               runs={})
    ser = {}
    for name, d in runs:
        res["runs"][name], ser[name] = analyse(name, d, ref)
        print(name, json.dumps(res["runs"][name], indent=1))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "newton_mode.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.88, wspace=0.45)
    ax[0].plot(ref["t"], ref["zr"], **fs.GUIDE, label="homogeneous")
    ax[0].plot(ref["t"], ref["Rr"], color="k", lw=1.0, ls=":")
    for name, s in ser.items():
        ax[0].plot(s["t"], s["zr"], color=COLOR.get(name), label=LABEL.get(name, name))
        ax[0].plot(s["t"], s["Rr"], color=COLOR.get(name), ls=":")
        ax[1].plot(s["t"], s["cr"], color=COLOR.get(name), label=LABEL.get(name, name))
        ax[2].plot(s["th"], 1e3 * s["dE"], color=COLOR.get(name), label=LABEL.get(name, name))
    for x in ax:
        x.axvline(ref["t_p"], **fs.MASK_LINE)
        x.set_xlabel("$t/M$", labelpad=-2)
        x.set_xlim(0, 24)
    ax[0].set_ylabel("rms / initial value")
    ax[0].set_ylim(0, 1.05)
    ax[0].legend(fontsize=7, loc="lower left")
    ax[0].set_title(r"$z_{\rm rms}$ (solid), $R_{\rm rms}$ (dotted)", fontsize=10)
    ax[1].set_ylabel("fraction across $z = 0$")
    ax[1].set_ylim(-0.02, 1.02)
    ax[1].set_xlim(15, 24)
    ax[1].set_title("plane crossing", fontsize=10)
    ax[2].set_ylabel(r"$10^3\,\Delta E/|W(0)|$")
    ax[2].set_title("energy $K + W$", fontsize=10)
    ax[2].legend(fontsize=7)
    os.makedirs(a.figdir, exist_ok=True)
    fs.save(fig, os.path.join(a.figdir, "oblate_newton"))

    # particles of the finest run in the x-z plane at four times
    name, d = runs[-1]
    files = ca.particle_history(d)[1]
    times = [0.0, ref["t_p"] - 2.0, res["runs"][name]["t_p"], 23.0]
    fig, ax = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 1.75), sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.25, top=0.88, wspace=0.06)
    snaps = [ca.read_snapshot(p) for p in files]
    ts = np.array([s[0] for s in snaps])
    for x, tt in zip(ax, times):
        t, dd, tag, _ = snaps[int(np.argmin(np.abs(ts - tt)))]
        sel = np.abs(dd[:, 1]) < 1.0
        x.scatter(dd[sel, 0], dd[sel, 2], s=1.0, color=fs.PAL["blue"], lw=0)
        x.set_title(f"$t = {t:.2f}M$", fontsize=9)
        x.set_xlim(-11, 11)
        x.set_ylim(-5.5, 5.5)
        x.set_aspect("equal")
        x.set_xlabel("$x/M$", labelpad=-2)
    ax[0].set_ylabel("$z/M$ ($|y| < M$)")
    fs.save(fig, os.path.join(a.figdir, "oblate_newton_particles"))
    print("wrote", os.path.join(a.out, "newton_mode.json"))


if __name__ == "__main__":
    main()
