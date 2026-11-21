#!/usr/bin/env python3
"""Test D2 of drift/JOURNAL.md entry 13: diffusion of the Killing energy of every particle.

    python3 diffusion.py --out DIR LABEL=DIR[,DIR...] [...] [--ratio LABEL_A/LABEL_B ...]

Every control writes all particles with the metric at their positions every 25 M
(`traj_ntrack = 100000`, files cc.traj.bin and cc.trajmet.bin). For each particle (matched by
tag) dE(t) = E_K(t) - E_K(0) with E_K = alpha W - beta.u (threshold_scan/common.killing_energy).
Coherent part: the mean of dE in 200 cells of (decile of E_K(0)) x (decile of the initial
coordinate radius) x (sign of x.u at t = 0); incoherent part: the rest, with variance s2(t).
Fits s2 = a + D t over 25 M <= t <= 300 M (and over 25-75 M, before the pulsation of the M/4
controls is large); t_D = var(E_K(0)) / D. --ratio a/b reports D(a)/D(b) for both fit ranges.

Writes DIR/diffusion.json and DIR/fig_diffusion.png.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import controls as K  # noqa: E402

import numpy as np  # noqa: E402

C = K.C
NB = 10


def deciles(v):
    q = np.quantile(v, np.linspace(0.0, 1.0, NB + 1))
    return np.clip(np.searchsorted(q, v, side="right") - 1, 0, NB - 1)


def linfit(t, y):
    b, a = np.polyfit(t, y, 1)
    res = y - (a + b * t)
    r2 = 1.0 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2) if len(y) > 2 else float("nan")
    return float(a), float(b), float(r2)


def analyse(dirs):
    recs = K.traj_records(dirs)
    r0 = recs[0]
    o0 = np.argsort(r0["tag"])
    tag0 = r0["tag"][o0]
    E0 = C.killing_energy(r0)[0][o0]
    x0, u0 = r0["x"][o0], r0["u"][o0]
    cell = (deciles(E0) * NB + deciles(np.linalg.norm(x0, axis=1))) * 2 + (np.sum(x0 * u0, axis=1) > 0)
    ncell = np.bincount(cell, minlength=2 * NB * NB)
    t, s2, s2tot, mde = [], [], [], []
    for rec in recs:
        o = np.argsort(rec["tag"])
        if not np.array_equal(rec["tag"][o], tag0):
            raise SystemExit(f"particle tags change at t = {rec['time']}")
        dE = C.killing_energy(rec)[0][o] - E0
        cm = np.bincount(cell, weights=dE, minlength=len(ncell)) / np.maximum(ncell, 1)
        d = dE - cm[cell]
        t.append(rec["time"])
        s2.append(float(np.var(d)))
        s2tot.append(float(np.var(dE)))
        mde.append(float(np.mean(dE)))
    t, s2 = np.array(t), np.array(s2)
    out = dict(dirs=dirs, n=int(len(tag0)), t=t.tolist(), s2=s2.tolist(), s2_total=s2tot, mean_dE=mde,
               var_E0=float(np.var(E0)), mean_E0=float(np.mean(E0)), cells_min_max=[int(ncell.min()), int(ncell.max())])
    for name, (t0, t1) in {"full": (25.0, 300.0), "early": (25.0, 75.0)}.items():
        k = (t >= t0 - 1e-6) & (t <= t1 + 1e-6)
        if k.sum() >= 2:
            a, D, r2 = linfit(t[k], s2[k])
            out[f"fit_{name}"] = dict(range=[t0, t1], a=a, D=D, r2=r2, t_D=float(out["var_E0"] / D) if D > 0 else None)
    k = t > 300.0 + 1e-6
    if k.sum() >= 2:   # a continuation beyond 300 M
        a, D, r2 = linfit(t[k], s2[k])
        out["fit_late"] = dict(range=[float(t[k][0]), float(t[k][-1])], a=a, D=D, r2=r2,
                               t_D=float(out["var_E0"] / D) if D > 0 else None)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("series", nargs="+")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--ratio", action="append", default=[])
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for spec in a.series:
        label, dirs = spec.split("=", 1)
        res[label] = analyse(dirs.split(","))
        r = res[label]
        print(label, json.dumps({k: r[k] for k in r if k.startswith("fit_") or k in ("var_E0", "mean_E0", "n", "cells_min_max")}),
              flush=True)
    ratios = {}
    for rq in a.ratio:
        p, q = rq.split("/")
        ratios[rq] = {f: res[p][f"fit_{f}"]["D"] / res[q][f"fit_{f}"]["D"]
                      for f in ("full", "early") if f"fit_{f}" in res[p] and f"fit_{f}" in res[q]}
        print("ratio", rq, json.dumps(ratios[rq]), flush=True)
    res["_ratios"] = ratios
    with open(os.path.join(a.out, "diffusion.json"), "w") as fp:
        json.dump(res, fp, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    for j, (label, r) in enumerate((k, v) for k, v in res.items() if not k.startswith("_")):
        c = fs.SERIES[j % len(fs.SERIES)]
        t = np.array(r["t"])
        f = r.get("fit_full", {})
        lab = label + (f": D = {f['D']:.2e}/M" if f else "")
        axs[0].plot(t, r["s2"], color=c, marker=".", lw=1.2, label=lab)
        if f:
            tt = np.linspace(25.0, 300.0, 2)
            axs[0].plot(tt, f["a"] + f["D"] * tt, color=c, ls="--", lw=0.8)
        axs[1].plot(t, r["mean_dE"], color=c, marker=".", lw=1.2, label=label)
    axs[0].set_yscale("log")
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"incoherent var$(E_K(t)-E_K(0))$")
    axs[0].legend(fontsize=6, frameon=False, loc="lower right")
    axs[1].axhline(0.0, **fs.MASK_LINE)
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"mean of $E_K(t)-E_K(0)$")
    axs[1].legend(fontsize=6, frameon=False)
    fs.save(fig, os.path.join(a.out, "fig_diffusion"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
