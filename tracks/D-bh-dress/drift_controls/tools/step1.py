#!/usr/bin/env python3
"""Step 1 of drift_controls: decompose the late horizon-mass drift of V-1 and ES-1 from
the outputs that exist (no new simulation), and ask the same questions of the D-pre-4
single-puncture runs.

    python3 step1.py --out DIR [--t0 100] [--run NAME:RUNDIR:BASE ...]

Reads, for every run, <RUNDIR>/<BASE>.horizon_summary_0.txt (columns 1 RK stage, 2 time,
3 mass, 4-7 Sx Sy Sz S, 8 area, 9 hrms, 10 hmean, 11 mean radius, 12 minimum radius;
fastflow.cpp:260-261, 379-390), <BASE>.z4c.user.hst (volume integrals of the squared
constraints over the cells with chi >= excise_chi, outputs/history.cpp:175-250) and
<BASE>.nrpic.hst (lapse at the probes, mesh minimum of the lapse).

Writes DIR/step1.json and the figures DIR/figs/step1_*.png|pdf:
  step1_decompose   drift of the mass from t0, the same from the area alone, the spin
                    term M - M_irr, ES-1 minus V-1
  step1_finder      hrms, mean expansion hmean/area, mean coordinate radius and its rate,
                    asphericity (mean - minimum radius)
  step1_constraints the z4c.user.hst norms against time
  step1_gauge       lapse at the probes near the hole and the mesh minimum of the lapse
  step1_dpre4       D-pre-4 (M/8, M/16, boundary 128 M) beside V-1, drift from t0
"""
import argparse
import json
import math
import os
import sys

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
DEFAULT_RUNS = [
    f"V-1:{S}/D-20261115-172730-c6d151b:v1",
    f"ES-1:{S}/D-20261115-172726-60ba4c2:es",
    f"P-M8:{S}/D-bh-dress-20261115-121313-284ec4f:punc",
    f"P-M16:{S}/D-bh-dress-20261115-121314-284ec4f:punc",
]
SUMCOLS = ["stage", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
           "meanr", "minr"]
NTHETA, LMAX, DX_FINE = 16, 8, 0.125     # production finder grid and M/8 at the hole


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    d = {c: a[:, i] for i, c in enumerate(SUMCOLS)}
    # keep the last row of each time (a restart may repeat a time)
    _, idx = np.unique(d["time"][::-1], return_index=True)
    keep = np.sort(len(d["time"]) - 1 - idx)
    return {c: v[keep] for c, v in d.items()}


def read_hst(path):
    names = None
    rows = []
    for line in open(path):
        if line.startswith("#"):
            if "[1]=" in line:
                parts = line.replace("#", "").split()
                names = [p.split("=", 1)[1] for p in parts if "=" in p]
            continue
        if line.strip():
            rows.append([float(x) for x in line.split()])
    a = np.array(rows)
    # last row of each time
    _, idx = np.unique(a[::-1, 0], return_index=True)
    a = a[np.sort(len(a) - 1 - idx)]
    return {n: a[:, i] for i, n in enumerate(names)}


def at(t, y, tq):
    return float(np.interp(tq, t, y))


def window_stats(t, D, lo, hi):
    m = (t >= lo) & (t <= hi)
    if m.sum() < 3:
        return None
    p = np.polyfit(t[m], D[m], 1)
    return {"min": float(D[m].min()), "max": float(D[m].max()),
            "maxabs": float(np.abs(D[m]).max()), "slope_per_M": float(p[0]),
            "n": int(m.sum())}


def ratio_after_before(t, y, tb, lo, hi):
    a = np.abs(y[(t >= tb) & (t <= hi)])
    b = np.abs(y[(t >= lo) & (t < tb)])
    if len(a) == 0 or len(b) == 0:
        return None
    return float(np.median(a) / np.median(b))


def analyse_run(name, rundir, base, t0):
    out = {"name": name, "rundir": rundir, "base": base}
    s = read_summary(os.path.join(rundir, f"{base}.horizon_summary_0.txt"))
    t = s["time"]
    ok = np.isfinite(s["mass"])
    out["n_rows"] = int(len(t))
    out["n_not_found"] = int((~ok).sum())
    t, s = t[ok], {c: v[ok] for c, v in s.items()}
    mirr = np.sqrt(s["area"] / (16 * math.pi))
    spin = s["mass"] - mirr
    M0 = at(t, s["mass"], t0)
    A0 = at(t, s["area"], t0)
    D = s["mass"] / M0 - 1
    DA = np.sqrt(s["area"] / A0) - 1
    out["t_range"] = [float(t[0]), float(t[-1])]
    out["M_t0"] = M0
    out["max_abs_spin_term_after_5M"] = float(np.abs(spin[t > 5]).max())
    out["max_abs_S_after_5M"] = float(np.abs(s["S"][t > 5]).max())
    out["max_abs_D_minus_DA"] = float(np.abs(D - DA)[t >= t0].max())
    tend = float(t[-1])
    wins = {}
    for lo, hi in [(t0, 165.0), (t0, 200.0), (165.0, 200.0), (t0, 210.0), (t0, 255.0),
                   (t0, 340.0), (t0, 500.0)]:
        if hi <= tend + 0.6:
            w = window_stats(t, D, lo, hi)
            if w:
                wins[f"{lo:g}-{hi:g}"] = w
    out["drift_windows"] = wins
    out["D_at"] = {f"{tq:g}": at(t, D, tq) for tq in (150, 165, 175, 185, 199.5, 250, 300,
                                                       340, 400, 499.5) if tq <= tend}
    # finder residuals and geometry
    hexp = s["hmean"] / s["area"]
    asph = s["meanr"] - s["minr"]
    out["finder"] = {
        "hrms_median_100_165": float(np.median(s["hrms"][(t >= t0) & (t < 165)])),
        "hrms_median_165_200": float(np.median(s["hrms"][(t >= 165) & (t <= 200)]))
        if tend >= 170 else None,
        "hrms_ratio_after_before_165": ratio_after_before(t, s["hrms"], 165, t0, 200),
        "mean_expansion_median_100_165": float(np.median(hexp[(t >= t0) & (t < 165)])),
        "mean_expansion_ratio_after_before_165": ratio_after_before(t, hexp, 165, t0, 200),
        "asphericity_max_after_t0": float(asph[t >= t0].max()),
        "asphericity_at": {f"{tq:g}": at(t, asph, tq) for tq in (t0, 165, 199.5)
                           if tq <= tend},
        "meanr_at": {f"{tq:g}": at(t, s["meanr"], tq) for tq in (25, t0, 150, 165, 199.5)
                     if tq <= tend},
        "angular_spacing_at_t0_M": at(t, s["meanr"], t0) * math.pi / NTHETA,
        "angular_spacing_in_cells_of_M8": at(t, s["meanr"], t0) * math.pi / NTHETA / DX_FINE,
        "shortest_wavelength_lmax_M": 2 * math.pi * at(t, s["meanr"], t0) / LMAX,
    }
    # rate of the coordinate radius, smoothed over 5 M
    if len(t) > 20:
        dt = np.median(np.diff(t))
        k = max(1, int(round(5.0 / dt)))
        rs = np.convolve(s["meanr"], np.ones(k) / k, mode="same")
        drdt = np.gradient(rs, t)
        out["finder"]["dr_dt_median_100_165"] = float(np.median(drdt[(t >= t0) & (t < 165)]))
        if tend >= 170:
            out["finder"]["dr_dt_median_165_195"] = float(
                np.median(drdt[(t >= 165) & (t <= 195)]))
    series = {"t": t, "D": D, "DA": DA, "spin": spin, "S": s["S"], "hrms": s["hrms"],
              "hexp": hexp, "meanr": s["meanr"], "asph": asph}
    # constraint norms
    z = read_hst(os.path.join(rundir, f"{base}.z4c.user.hst"))
    zt = z["time"]
    cons = {}
    for key in ("C-norm2", "H-norm2", "M-norm2", "Z-norm2", "Theta-norm"):
        if key not in z:
            continue
        y = z[key]
        rec = {f"{tq:g}": at(zt, y, tq) for tq in (0, 50, t0, 150, 165, 200, 250, 300, 500)
               if tq <= zt[-1]}
        for lo, hi in [(t0, 165), (165, 200)]:
            m = (zt >= lo) & (zt <= hi) & (y > 0)
            if m.sum() > 3:
                rec[f"dlog_dt_{lo:g}_{hi:g}"] = float(np.polyfit(zt[m], np.log(y[m]), 1)[0])
        cons[key] = rec
    out["constraints"] = cons
    series["z"] = z
    # lapse near the hole
    n = read_hst(os.path.join(rundir, f"{base}.nrpic.hst"))
    gauge = {}
    for key in ("alpha_min", "alpha_probe1", "alpha_probe2", "alpha_probe"):
        if key in n:
            gauge[key] = {f"{tq:g}": at(n["time"], n[key], tq)
                          for tq in (25, 50, t0, 150, 165, 200, 300, 500) if tq <= n["time"][-1]}
    out["gauge"] = gauge
    series["n"] = n
    return out, series


def vline(ax, x=165.0):
    ax.axvline(x, **figstyle.MASK_LINE)


def figures(res, ser, outdir, t0):
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(outdir, "figs")
    os.makedirs(fd, exist_ok=True)
    col = {"V-1": figstyle.PAL["blue"], "ES-1": figstyle.PAL["red"],
           "P-M8": figstyle.PAL["green"], "P-M16": figstyle.PAL["orange"]}

    # decomposition
    fig, axs = plt.subplots(3, 1, figsize=(figstyle.FULL_WIDTH, 7.0), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.08, hspace=0.08)
    for nm in ("V-1", "ES-1"):
        if nm not in ser:
            continue
        s = ser[nm]
        m = s["t"] >= 50
        axs[0].plot(s["t"][m], s["D"][m] * 1e4, color=col[nm], label=f"{nm}: $M/M(t_0)-1$")
        axs[0].plot(s["t"][m], s["DA"][m] * 1e4, color=col[nm], ls="--", lw=1.0,
                    label=f"{nm}: $(A/A(t_0))^{{1/2}}-1$")
        axs[1].semilogy(s["t"][m], np.abs(s["spin"][m]) + 1e-20, color=col[nm],
                        label=f"{nm}: $|M-M_{{\\rm irr}}|$")
        axs[1].semilogy(s["t"][m], np.abs(s["S"][m]), color=col[nm], ls=":",
                        label=f"{nm}: $|S|$")
    if "V-1" in ser and "ES-1" in ser:
        a, b = ser["ES-1"], ser["V-1"]
        tt = a["t"][a["t"] >= 50]
        axs[2].plot(tt, (np.interp(tt, a["t"], a["D"]) - np.interp(tt, b["t"], b["D"])) * 1e4,
                    color="k", lw=1.0, label="ES-1 $-$ V-1 (drift from $t_0$)")
    axs[0].axhline(0, **figstyle.THIN)
    axs[0].set_ylabel(r"drift from $t_0=%g\,M$ [$10^{-4}$]" % t0)
    axs[1].set_ylabel("spin term, $|S|$")
    axs[2].set_ylabel(r"difference [$10^{-4}$]")
    axs[2].set_xlabel(r"$t\,[M]$")
    for ax in axs:
        vline(ax)
        ax.legend(ncol=2, loc="best", fontsize=8)
    figstyle.save(fig, os.path.join(fd, "step1_decompose"))
    plt.close(fig)

    # finder residuals and geometry
    fig, axs = plt.subplots(4, 1, figsize=(figstyle.FULL_WIDTH, 8.0), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.07, hspace=0.08)
    for nm in ("V-1", "ES-1"):
        if nm not in ser:
            continue
        s = ser[nm]
        m = s["t"] >= 5
        axs[0].semilogy(s["t"][m], s["hrms"][m], color=col[nm], label=f"{nm}: hrms")
        axs[1].semilogy(s["t"][m], np.abs(s["hexp"][m]), color=col[nm],
                        label=f"{nm}: $|h_{{\\rm mean}}|/A$")
        axs[2].plot(s["t"][m], s["meanr"][m], color=col[nm], label=f"{nm}: mean radius")
        axs[3].semilogy(s["t"][m], np.abs(s["asph"][m]) + 1e-16, color=col[nm],
                        label=f"{nm}: mean $-$ min radius")
    axs[0].set_ylabel("hrms")
    axs[1].set_ylabel("mean expansion")
    axs[2].set_ylabel(r"$\bar r_{\rm AH}\,[M]$")
    axs[3].set_ylabel(r"asphericity $[M]$")
    axs[3].set_xlabel(r"$t\,[M]$")
    for ax in axs:
        vline(ax)
        ax.legend(ncol=2, loc="best", fontsize=8)
    figstyle.save(fig, os.path.join(fd, "step1_finder"))
    plt.close(fig)

    # constraints
    keys = ["H-norm2", "M-norm2", "Z-norm2", "Theta-norm"]
    fig, axs = plt.subplots(len(keys), 1, figsize=(figstyle.FULL_WIDTH, 8.0), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.07, hspace=0.08)
    for nm, s in ser.items():
        z = s["z"]
        for ax, k in zip(axs, keys):
            if k in z:
                ax.semilogy(z["time"], z[k], color=col.get(nm, "k"), label=nm,
                            lw=1.0 if nm.startswith("P") else 1.5)
    for ax, k in zip(axs, keys):
        ax.set_ylabel(k)
        vline(ax)
        ax.legend(ncol=4, loc="best", fontsize=8)
    axs[-1].set_xlabel(r"$t\,[M]$")
    axs[-1].set_xlim(0, 500)
    figstyle.save(fig, os.path.join(fd, "step1_constraints"))
    plt.close(fig)

    # gauge near the hole
    fig, axs = plt.subplots(3, 1, figsize=(figstyle.FULL_WIDTH, 6.5), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.08, hspace=0.08)
    for nm in ("V-1", "ES-1"):
        if nm not in ser:
            continue
        n = ser[nm]["n"]
        m = n["time"] >= 50
        axs[0].plot(n["time"][m], n["alpha_probe1"][m], color=col[nm], label=f"{nm}: x = 1 M")
        axs[1].plot(n["time"][m], n["alpha_probe2"][m], color=col[nm], label=f"{nm}: x = 4 M")
        axs[2].plot(n["time"][m], n["alpha_min"][m], color=col[nm], label=f"{nm}: mesh minimum")
    axs[0].set_ylabel(r"$\alpha(x=1\,M)$")
    axs[1].set_ylabel(r"$\alpha(x=4\,M)$")
    axs[2].set_ylabel(r"$\min\alpha$")
    axs[2].set_xlabel(r"$t\,[M]$")
    for ax in axs:
        vline(ax)
        ax.legend(ncol=2, loc="best", fontsize=8)
    figstyle.save(fig, os.path.join(fd, "step1_gauge"))
    plt.close(fig)

    # D-pre-4 beside V-1
    fig, axs = plt.subplots(2, 1, figsize=(figstyle.FULL_WIDTH, 5.5), sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
    for nm in ("V-1", "ES-1", "P-M8", "P-M16"):
        if nm not in ser:
            continue
        s = ser[nm]
        m = s["t"] >= 50
        axs[0].plot(s["t"][m], s["D"][m] * 1e4, color=col[nm], label=nm,
                    lw=1.0 if nm.startswith("P") else 1.5)
        if nm.startswith("P"):
            z = s["z"]
            axs[1].semilogy(z["time"], z["H-norm2"], color=col[nm], label=f"{nm} H-norm2")
        else:
            z = s["z"]
            axs[1].semilogy(z["time"], z["H-norm2"], color=col[nm], label=f"{nm} H-norm2")
    for x in (165, 220, 255, 300, 340):
        for ax in axs:
            ax.axvline(x, **figstyle.MASK_LINE)
    axs[0].axhline(0, **figstyle.THIN)
    axs[0].set_ylabel(r"drift from $t_0=%g\,M$ [$10^{-4}$]" % t0)
    axs[1].set_ylabel("H-norm2")
    axs[1].set_xlabel(r"$t\,[M]$")
    axs[0].legend(ncol=4, loc="best", fontsize=8)
    axs[1].legend(ncol=2, loc="best", fontsize=8)
    axs[1].set_xlim(50, 500)
    figstyle.save(fig, os.path.join(fd, "step1_dpre4"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--t0", type=float, default=100.0)
    ap.add_argument("--run", action="append", default=None,
                    help="NAME:RUNDIR:BASE (default: V-1, ES-1, D-pre-4 M/8 and M/16)")
    a = ap.parse_args()
    runs = a.run or DEFAULT_RUNS
    os.makedirs(a.out, exist_ok=True)
    res, ser = {}, {}
    for r in runs:
        nm, d, b = r.split(":")
        res[nm], ser[nm] = analyse_run(nm, d, b, a.t0)
    figures(res, ser, a.out, a.t0)
    with open(os.path.join(a.out, "step1.json"), "w") as f:
        json.dump({"t0": a.t0, "runs": res}, f, indent=1)
    for nm, r in res.items():
        print(f"== {nm}: rows {r['n_rows']} not found {r['n_not_found']} "
              f"t {r['t_range']} M(t0) {r['M_t0']:.9f}")
        print(f"   spin term max {r['max_abs_spin_term_after_5M']:.2e}  |S| max "
              f"{r['max_abs_S_after_5M']:.2e}  |D - DA| max {r['max_abs_D_minus_DA']:.2e}")
        for k, w in r["drift_windows"].items():
            print(f"   window {k}: min {w['min']:+.3e} max {w['max']:+.3e} "
                  f"slope {w['slope_per_M']:+.2e}/M")
        print("   D at", {k: f"{v:+.2e}" for k, v in r["D_at"].items()})
        print("   finder", json.dumps(r["finder"]))
        for k, c in r["constraints"].items():
            print(f"   {k}", {kk: f"{vv:.3e}" for kk, vv in c.items()})
        print("   gauge", json.dumps(r["gauge"]))


if __name__ == "__main__":
    main()
