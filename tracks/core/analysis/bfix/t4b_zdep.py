#!/usr/bin/env python3
"""T4b: where the z dependence of the thin box 256 x 256 x 16 of T4 sits (prediction P9 of
tracks/core/JOURNAL-bfix.md). Reads the dumps of a run directory (default: the stage big of
T4) and measures, per variable of the z4c, tmunu and con dumps, the largest departure of
any z-layer from layer 0, relative to the largest value and to the x-y variation of layer 0.

    python3 t4b_zdep.py --rundir DIR [--label NAME] [--out DIR]
"""
import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import athena_bin, fs  # noqa: E402

GROUPS = ("z4c", "tmunu", "con")
GW = ("z4c_chi", "z4c_alpha", "z4c_Khat", "z4c_gxx", "z4c_gxy", "z4c_gyy", "z4c_gzz",
      "z4c_Axx", "z4c_Axy", "z4c_Ayy", "z4c_Azz")


def zstats(a):
    """a: array (nz, ny, nx). Departure of the layers from layer 0."""
    a0 = a[:1]
    dev = np.abs(a - a0)
    fmax = float(np.abs(a).max())
    xyvar = float(a0.max() - a0.min())
    absdev = float(dev.max())
    return {"absdev": absdev, "fmax": fmax, "xyvar": xyvar,
            "rel_max": absdev/fmax if fmax > 0 else 0.0,
            "rel_xyvar": absdev/xyvar if xyvar > 0 else (0.0 if absdev == 0 else np.inf),
            "rms_dev": float(np.sqrt(np.mean((a - a.mean(axis=0, keepdims=True))**2)))}


def analyse(rundir):
    res = {}
    for g in GROUPS:
        for p in sorted(glob.glob(os.path.join(rundir, "bin", f"*.{g}.0*.bin"))):
            d = athena_bin.read_bin(p)
            key = f"{g}@{d['time']:.6g}"
            res[key] = {"file": os.path.relpath(p, rundir), "time": d["time"],
                        "cycle": d["cycle"], "var_size": d["var_size"],
                        "vars": {v: zstats(np.asarray(d[v], float)) for v in d["variables"]}}
    return res


def figure(res, rundir, out, label):
    fs.use_style()
    last = {}
    for key, r in res.items():
        g, t = key.split("@")
        if g not in last or r["time"] > last[g]["time"]:
            last[g] = r
    names, relx, relm = [], [], []
    for g in GROUPS:
        if g not in last:
            continue
        for v, s in last[g]["vars"].items():
            names.append(v)
            relx.append(max(s["rel_xyvar"], 1e-20) if np.isfinite(s["rel_xyvar"]) else 1e2)
            relm.append(max(s["rel_max"], 1e-20))
    order = np.argsort(relx)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(fs.PAGE_WIDTH, 5.6),
                                  gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(left=0.13, right=0.95, bottom=0.09, top=0.95, wspace=0.35)
    y = np.arange(len(names))
    ax.semilogx(np.array(relx)[order], y, "o", color=fs.PAL["red"],
                label="relative to the x-y variation of layer 0")
    ax.semilogx(np.array(relm)[order], y, "s", mfc="none", color=fs.PAL["blue"],
                label="relative to the largest value")
    ax.set_yticks(y)
    ax.set_yticklabels([names[i] for i in order], fontsize=6)
    ax.axvline(1e-9, color="k", lw=0.8, ls="--")
    ax.set_xlabel(f"largest departure of a z-layer from layer 0, t = {last['z4c']['time']:.3g}")
    ax.legend(loc="lower right", fontsize=6)
    ax.set_xlim(1e-20, 1e2)
    # map of the worst variable of z4c: layer nz/2 minus layer 0
    zv = last["z4c"]["vars"]
    worst = max(zv, key=lambda v: zv[v]["rel_max"])
    d = athena_bin.read_bin(os.path.join(rundir, last["z4c"]["file"]))
    a = np.asarray(d[worst], float)
    diff = a[a.shape[0]//2] - a[0]
    lim = max(np.abs(diff).max(), 1e-300)
    im = ax2.imshow(diff, origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim,
                    extent=[d["x1v"][0], d["x1v"][-1], d["x2v"][0], d["x2v"][-1]])
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_title(f"{worst}: layer {a.shape[0]//2} minus layer 0", fontsize=8)
    cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cb.ax.tick_params(labelsize=6)
    return fs.save(fig, os.path.join(out, f"t4b_zdep_{label}")), worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rundir", required=True)
    ap.add_argument("--label", default="big")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    res = analyse(a.rundir)
    summ = {}
    for key, r in res.items():
        vs = r["vars"]
        gw = {v: vs[v] for v in GW if v in vs}
        summ[key] = {"worst_rel_max": max(vs, key=lambda v: vs[v]["rel_max"]),
                     "worst_rel_max_value": max(s["rel_max"] for s in vs.values()),
                     "gw_fields_worst_rel_xyvar": max((s["rel_xyvar"] for s in gw.values()),
                                                      default=None),
                     "gw_fields_worst_rel_max": max((s["rel_max"] for s in gw.values()),
                                                    default=None)}
        print(key, summ[key])
        for v, s in sorted(vs.items(), key=lambda kv: -kv[1]["rel_max"])[:8]:
            print(f"   {v:12s} absdev {s['absdev']:.3e} max {s['fmax']:.3e} xyvar "
                  f"{s['xyvar']:.3e} rel_max {s['rel_max']:.3e} rel_xyvar {s['rel_xyvar']:.3e}")
    figs, worst = figure(res, a.rundir, out, a.label)
    print("figures:", figs, "worst:", worst)
    bc.save_json({"meta": {"rundir": a.rundir, "commit": bc.git_rev()}, "dumps": res,
                  "summary": summ}, os.path.join(out, f"results_t4b_{a.label}.json"))


if __name__ == "__main__":
    main()
