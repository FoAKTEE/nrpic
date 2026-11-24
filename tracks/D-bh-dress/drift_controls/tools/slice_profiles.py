#!/usr/bin/env python3
"""Part B of drift_controls (JOURNAL entry 1, B1-B2): finder-independent horizon mass and
the Misner-Sharp mass profile m(R) of the slices in the restart dumps of V-1 and ES-1,
with analysis/diag/slicemass.py (rst_open, analyse; its docstring defines R, m, the
shells, the crossing 2m/R = 1 and the uncertainties).

    python3 slice_profiles.py --out DIR [--run NAME:RUNDIR:BASE ...] [--dumps 0 1 2 3 4]

Per dump: time, M_H = R_H/2 at the outermost crossing of 2m/R = 1 (16 shells per factor
2), its two uncertainties (shells, spread of m), the finder row at the dump time, the
asymptotic mass m_inf, and the profile m(R) (8 shells per factor 2: medians of R, m and
the 16-84 half-width of m). Writes DIR/slice_profiles.json and figures
DIR/figs/slice_mR_<run>.png|pdf (top: m(R) - M_H(t = 100 M) on a symmetric log scale,
one curve per dump; bottom: the change m(R, t) - m(R, 150 M) for the dumps after 150 M,
against the change of the finder mass) and DIR/figs/slice_MH.png (M_H and the finder
mass against time, both relative to their values at 100 M).
"""
import argparse
import json
import os
import sys

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "analysis", "diag"))
from nrpic import figstyle  # noqa: E402
import slicemass as sm  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
DEFAULT_RUNS = [f"V-1:{S}/D-20261115-172730-c6d151b:v1",
                f"ES-1:{S}/D-20261115-172726-60ba4c2:es"]


def one_dump(path, finder):
    h = sm.rst_open(path, strict=True)
    A = sm.analyse(h, finder=finder)
    X = A["X"][sm.NPER2_H]
    P = A["P"][sm.NPER2_FIG]
    sh = sm.outer_sheet(P)
    rec = dict(path=path, time=float(A["time"]), ncycle=int(A["ncycle"]),
               m_inf=float(A["m_inf"]), flat=bool(A["flat"]),
               RH=float(X["RH"]) if X is not None else None,
               MH=float(X["RH"]) / 2 if X is not None else None,
               dMH_shell=float(A.get("dMH_shell", np.nan)),
               dMH_spread=float(A.get("dMH_spread", np.nan)),
               finder=A["finder"],
               prof=dict(r=P["r"][sh].tolist(), R=P["R"][sh].tolist(), m=P["m"][sh].tolist(),
                         s68=(0.5 * (P["m84"][sh] - P["m16"][sh])).tolist()))
    if rec["finder"]:
        rec["finder"] = {k: float(v) for k, v in rec["finder"].items()}
    return rec


def figures(res, outdir):
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(outdir, "figs")
    os.makedirs(fd, exist_ok=True)
    for name, recs in res.items():
        recs = sorted(recs, key=lambda x: x["time"])
        ref = [x for x in recs if abs(x["time"] - 100) < 1e-6]
        ref150 = [x for x in recs if abs(x["time"] - 150) < 1e-6]
        if not ref:
            continue
        M0 = ref[0]["MH"]
        fig, axs = plt.subplots(2, 1, figsize=(figstyle.FULL_WIDTH, 6.5), sharex=True)
        fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.08, hspace=0.08)
        cols = figstyle.series_colors(len(recs))
        for x, c in zip(recs, cols):
            R, m = np.array(x["prof"]["R"]), np.array(x["prof"]["m"])
            ok = np.isfinite(R) & np.isfinite(m) & (R > 1.5)
            axs[0].plot(R[ok], m[ok] - M0, color=c, lw=1.2, label=f"t = {x['time']:g} M")
        axs[0].set_yscale("symlog", linthresh=1e-5)
        axs[0].set_ylabel(r"$m(R)-M_H(100\,M)$")
        axs[0].legend(ncol=3, fontsize=8)
        if ref150:
            R0, m0 = np.array(ref150[0]["prof"]["R"]), np.array(ref150[0]["prof"]["m"])
            ok0 = np.isfinite(R0) & np.isfinite(m0)
            for x, c in zip(recs, cols):
                if x["time"] <= 150:
                    continue
                R, m = np.array(x["prof"]["R"]), np.array(x["prof"]["m"])
                ok = np.isfinite(R) & np.isfinite(m) & (R > 1.5)
                dm = m[ok] - np.interp(R[ok], R0[ok0], m0[ok0])
                axs[1].plot(R[ok], dm, color=c, lw=1.2, label=f"t = {x['time']:g} M")
                if x["finder"] and ref150[0]["finder"]:
                    axs[1].axhline(x["finder"]["M"] - ref150[0]["finder"]["M"], color=c,
                                   ls="--", lw=1.0, label="finder mass change")
            axs[1].set_yscale("symlog", linthresh=1e-5)
            axs[1].set_ylabel(r"$m(R,t)-m(R,150\,M)$")
            axs[1].legend(ncol=2, fontsize=8)
        axs[1].set_xscale("log")
        axs[1].set_xlabel(r"areal radius $R\,[M]$")
        for ax in axs:
            ax.axvline(2.0, **figstyle.MASK_LINE)
        figstyle.save(fig, os.path.join(fd, f"slice_mR_{name}"))
        plt.close(fig)
    fig, ax = plt.subplots(1, 1, figsize=(figstyle.FULL_WIDTH, 3.5))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.95, bottom=0.14)
    pal = {"V-1": figstyle.PAL["blue"], "ES-1": figstyle.PAL["red"]}
    for name, recs in res.items():
        recs = sorted(recs, key=lambda x: x["time"])
        ref = [x for x in recs if abs(x["time"] - 100) < 1e-6]
        if not ref:
            continue
        t = np.array([x["time"] for x in recs])
        MH = np.array([x["MH"] for x in recs])
        err = np.array([max(x["dMH_shell"], x["dMH_spread"]) for x in recs])
        Mf = np.array([x["finder"]["M"] if x["finder"] else np.nan for x in recs])
        ax.errorbar(t, (MH / ref[0]["MH"] - 1) * 1e4, yerr=err / ref[0]["MH"] * 1e4,
                    color=pal.get(name, "k"), marker="o", lw=1.0, capsize=3,
                    label=f"{name}: slice $M_H$")
        if ref[0]["finder"]:
            ax.plot(t, (Mf / ref[0]["finder"]["M"] - 1) * 1e4, color=pal.get(name, "k"),
                    ls="--", marker="s", lw=1.0, label=f"{name}: finder")
    ax.axhline(0, **figstyle.THIN)
    ax.set_xlabel(r"$t\,[M]$")
    ax.set_ylabel(r"change from $t=100\,M$ [$10^{-4}$]")
    ax.legend(ncol=2, fontsize=8)
    figstyle.save(fig, os.path.join(fd, "slice_MH"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", action="append", default=None)
    ap.add_argument("--dumps", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for spec in a.run or DEFAULT_RUNS:
        name, rundir, base = spec.split(":")
        finder = sm.read_finder(os.path.join(rundir, f"{base}.horizon_summary_0.txt"))
        res[name] = []
        for k in a.dumps:
            p = os.path.join(rundir, "rst", f"{base}.{k:05d}.rst")
            if not os.path.exists(p):
                continue
            rec = one_dump(p, finder)
            res[name].append(rec)
            f = rec["finder"] or {}
            print(f"{name} t={rec['time']:7.2f} M_H={rec['MH']:.8f} "
                  f"(shells {rec['dMH_shell']:.1e}, spread {rec['dMH_spread']:.1e}) "
                  f"finder M={f.get('M', float('nan')):.8f} m_inf={rec['m_inf']:.6f}",
                  flush=True)
        with open(os.path.join(a.out, "slice_profiles.json"), "w") as fo:
            json.dump(res, fo, indent=1)
    figures(res, a.out)


if __name__ == "__main__":
    main()
