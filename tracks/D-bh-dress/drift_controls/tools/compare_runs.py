#!/usr/bin/env python3
"""Steps 2-3 of drift_controls: judge a control run against V-1 (JOURNAL entry 2 for run
(b), entry 3 for run (a)).

    python3 compare_runs.py --out DIR --ctrl NAME:RUNDIR:BASE [--ref NAME:RUNDIR:BASE]
                            [--t0 100] [--theta]

Reads the finder summaries (<BASE>.horizon_summary_0.txt), z4c.user.hst and nrpic.hst of
the reference (default V-1) and the control. Measures, for both:
  - drift D(t) = M(t)/M(t0) - 1, its range over 100-165 M and 100-200 M, D(199.5 M),
    slopes over 165-200 M;
  - the difference of the masses M_ctrl - M_ref on the common times, and the first time
    after which it exceeds 1e-6 (separation time);
  - median rate of the mean coordinate radius over 100-165 and 165-195 M (5 M mean);
  - the largest asphericity (mean - minimum radius) after 100 M and after 165 M;
  - the Theta norm of z4c.user.hst at 100, 150, 200 M;
  - with --theta: median |Theta| on the +x axis at r = 3-10 M per z4c slice (theta_map.py).
For a restart control (run a) the comparison is on the slices both have (t >= start).
A non-finite run is reported: column 3 of <BASE>.nrpic.hst (np) and the masses are checked
for NaN.

Writes DIR/compare_<ctrl>.json and the figure DIR/figs/compare_<ctrl>.png|pdf: top, the
drift of both from t0; middle, M_ctrl - M_ref; bottom, the coordinate radius rate and
(with --theta) the median |Theta| at r = 3-10 M.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)
from nrpic import figstyle  # noqa: E402
from step1 import read_summary, read_hst, at  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
REF = f"V-1:{S}/D-20261115-172730-c6d151b:v1"


def stats(t, M, meanr, minr, t0):
    out = {}
    M0 = at(t, M, t0) if t[0] <= t0 else M[0]
    tt0 = t0 if t[0] <= t0 else t[0]
    D = M / M0 - 1
    out["t0_used"] = float(tt0)
    for lo, hi in [(tt0, 165.0), (tt0, 200.0), (165.0, 200.0)]:
        m = (t >= lo) & (t <= hi)
        if m.sum() > 2:
            out[f"D_{lo:g}_{hi:g}"] = [float(D[m].min()), float(D[m].max())]
            out[f"slope_{lo:g}_{hi:g}"] = float(np.polyfit(t[m], D[m], 1)[0])
    out["D_end"] = float(D[-1])
    out["t_end"] = float(t[-1])
    dt = np.median(np.diff(t))
    k = max(1, int(round(5.0 / dt)))
    rs = np.convolve(meanr, np.ones(k) / k, mode="same")
    drdt = np.gradient(rs, t)
    for lo, hi in [(tt0, 165.0), (165.0, 195.0)]:
        m = (t >= lo) & (t <= hi)
        if m.sum() > 2:
            out[f"drdt_{lo:g}_{hi:g}"] = float(np.median(drdt[m]))
    asph = meanr - minr
    for lo in (tt0, 165.0):
        m = t >= lo
        if m.any():
            out[f"asph_max_after_{lo:g}"] = float(asph[m].max())
    return out, D, drdt


def theta_near(rundir, base):
    import theta_map as tm
    zser, _, _ = tm.run_series(rundir, base)
    out = []
    for s in zser:
        m = (s["r_ax"] >= 3) & (s["r_ax"] < 10)
        out.append((s["time"], float(np.median(np.abs(s["th_ax"][m]))) if m.any() else np.nan))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ctrl", required=True)
    ap.add_argument("--ref", default=REF)
    ap.add_argument("--t0", type=float, default=100.0)
    ap.add_argument("--theta", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = {}
    for role, spec in (("ref", a.ref), ("ctrl", a.ctrl)):
        name, d, b = spec.split(":")
        s = read_summary(os.path.join(d, f"{b}.horizon_summary_0.txt"))
        n = read_hst(os.path.join(d, f"{b}.nrpic.hst"))
        z = read_hst(os.path.join(d, f"{b}.z4c.user.hst"))
        runs[role] = dict(name=name, dir=d, base=b, s=s, n=n, z=z)
    res = {"t0": a.t0}
    ser = {}
    for role, r in runs.items():
        s = r["s"]
        ok = np.isfinite(s["mass"])
        st, D, drdt = stats(s["time"][ok], s["mass"][ok], s["meanr"][ok], s["minr"][ok], a.t0)
        st["n_rows"] = int(len(s["time"]))
        st["n_nan_mass"] = int((~ok).sum())
        st["np_first_last"] = [float(r["n"]["np"][0]), float(r["n"]["np"][-1])] \
            if "np" in r["n"] else None
        st["np_finite"] = bool(np.all(np.isfinite(r["n"]["np"]))) if "np" in r["n"] else None
        st["theta_norm"] = {f"{tq:g}": at(r["z"]["time"], r["z"]["Theta-norm"], tq)
                            for tq in (100, 150, 165, 200) if r["z"]["time"][0] <= tq <= r["z"]["time"][-1]}
        if a.theta:
            st["theta_med_3_10"] = theta_near(r["dir"], r["base"])
        res[role] = dict(name=r["name"], **st)
        ser[role] = dict(t=s["time"][ok], M=s["mass"][ok], D=D, drdt=drdt)
    # difference on common times
    tr, tc = ser["ref"]["t"], ser["ctrl"]["t"]
    common = np.intersect1d(np.round(tr, 6), np.round(tc, 6))
    Mr = np.interp(common, tr, ser["ref"]["M"])
    Mc = np.interp(common, tc, ser["ctrl"]["M"])
    dM = Mc - Mr
    res["diff"] = {"n_common": int(len(common)),
                   "max_abs": float(np.abs(dM).max()) if len(dM) else None,
                   "at": {f"{tq:g}": float(np.interp(tq, common, dM))
                          for tq in (100, 120, 150, 165, 180, 199.5)
                          if len(common) and common[0] <= tq <= common[-1]}}
    big = np.nonzero(np.abs(dM) > 1e-6)[0]
    res["diff"]["first_time_above_1e-6"] = float(common[big[0]]) if len(big) else None
    # same-slice comparison of drifts from the control's first time (restart runs)
    tstart = float(common[0]) if len(common) else None
    if tstart is not None:
        Dr = Mr / Mr[0] - 1
        Dc = Mc / Mc[0] - 1
        res["diff"]["drift_from_common_start"] = {
            "start": tstart, "ref_end": float(Dr[-1]), "ctrl_end": float(Dc[-1]),
            "ctrl_minus_ref_end": float(Dc[-1] - Dr[-1]),
            "max_abs_ctrl_minus_ref": float(np.abs(Dc - Dr).max())}
    nm = runs["ctrl"]["name"]
    with open(os.path.join(a.out, f"compare_{nm}.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    # figure
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(a.out, "figs")
    os.makedirs(fd, exist_ok=True)
    fig, axs = plt.subplots(3, 1, figsize=(figstyle.FULL_WIDTH, 7.5), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.07, hspace=0.08)
    col = {"ref": figstyle.PAL["blue"], "ctrl": figstyle.PAL["red"]}
    for role in ("ref", "ctrl"):
        t, D = ser[role]["t"], ser[role]["D"]
        m = t >= min(50, t[0])
        axs[0].plot(t[m], D[m] * 1e4, color=col[role], label=runs[role]["name"])
        axs[2].plot(t[m], ser[role]["drdt"][m] * 1e3, color=col[role],
                    label=f"{runs[role]['name']}: $d\\bar r/dt$")
    axs[0].axhline(0, **figstyle.THIN)
    axs[0].set_ylabel(r"$M/M(t_0)-1$ [$10^{-4}$]")
    axs[1].plot(common, dM * 1e6, color="k", lw=1.0)
    axs[1].axhline(0, **figstyle.THIN)
    axs[1].set_ylabel(r"$M_{\rm %s}-M_{\rm %s}$ [$10^{-6}$]" % (runs["ctrl"]["name"],
                                                               runs["ref"]["name"]))
    axs[1].set_yscale("symlog", linthresh=1.0)
    axs[2].set_ylabel(r"$d\bar r_{\rm AH}/dt$ [$10^{-3}$]")
    axs[2].set_ylim(-1, 5)
    if a.theta:
        ax2 = axs[2].twinx()
        for role, ls in (("ref", "--"), ("ctrl", ":")):
            th = np.array(res[role]["theta_med_3_10"])
            ax2.semilogy(th[:, 0], th[:, 1], color=col[role], ls=ls, marker="o", ms=3,
                         lw=1.0, label=f"{runs[role]['name']}: med $|\\Theta|$, r = 3-10 M")
        ax2.set_ylabel(r"$|\Theta|$")
        ax2.legend(loc="upper left", fontsize=7)
    axs[2].set_xlabel(r"$t\,[M]$")
    for ax in axs:
        ax.axvline(165, **figstyle.MASK_LINE)
    axs[0].legend(fontsize=8)
    axs[2].legend(fontsize=7, loc="lower right")
    figstyle.save(fig, os.path.join(fd, f"compare_{nm}"))
    plt.close(fig)


if __name__ == "__main__":
    main()
