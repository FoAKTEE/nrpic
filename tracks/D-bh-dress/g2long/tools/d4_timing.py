#!/usr/bin/env python3
"""D4 timing split at t_rem = 219 M (g2long entry 23, test T).

D4 = tau_rem - tau_H(R0) per removed dust particle (reasons 2, 3; tags >= 140), the proper time
at removal minus the exact LTB proper time at which its shell crosses the horizon (esf_labels.npz,
as g2runs/tools/esf_criteria.py reads it). Before 219 M ES-FL and FK remove by the same rule
(horizon excision inside 0.8 rr_min); after it ES-FL removes by the lapse rule. The script gives
D4 before and after the split, by removal reason, and per 10 M bin of t_rem.

Usage: d4_timing.py --out DIR [--split 219] LABEL=RUNDIR:BASE:DATADIR ...
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "flux_tools"))
import figstyle  # noqa: E402
import fluxio  # noqa: E402


def stats(x):
    if x.size == 0:
        return dict(n=0)
    return dict(n=int(x.size), frac_below_0=float(np.mean(x < 0)), min=float(x.min()),
                median=float(np.median(x)), p05=float(np.percentile(x, 5)), n_below_minus1=int(np.sum(x < -1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--split", type=float, default=219.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    J, D = {}, {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base, data = rest.split(":")
        rem = fluxio.read_removed(os.path.join(rd, base + ".removed.bin"))
        if np.any(np.diff(rem["time"]) < 0.0):
            rem, _ = fluxio.drop_overlaps(rem, fluxio.restart_times(os.path.join(rd, "rst")))
        lab = np.load(os.path.join(data, "esf_labels.npz"))
        sel = np.isin(rem["reason"], (2, 3)) & (rem["tag"] >= 140)
        tag, trem, tau, rs = rem["tag"][sel], rem["time"][sel], rem["tau"][sel], rem["reason"][sel]
        dtau = tau - lab["tauH"][tag]
        early, late = trem <= a.split, trem > a.split
        o = dict(dir=rd, all=stats(dtau), before=stats(dtau[early]), after=stats(dtau[late]))
        for r in (2, 3):
            o[f"after_reason{r}"] = stats(dtau[late & (rs == r)])
            o[f"before_reason{r}"] = stats(dtau[early & (rs == r)])
        edges = np.arange(0.0, trem.max() + 10.0, 10.0)
        k = np.digitize(trem, edges) - 1
        o["bins"] = [dict(t0=float(edges[i]), n=int(np.sum(k == i)),
                          frac_below_0=float(np.mean(dtau[k == i] < 0)) if np.any(k == i) else None)
                     for i in range(len(edges) - 1)]
        J[name] = o
        D[name] = (trem, dtau, rs)
    with open(os.path.join(a.out, "d4_timing.json"), "w") as f:
        json.dump(J, f, indent=1)

    figstyle.use_style()
    import matplotlib.pyplot as plt
    cols = figstyle.series_colors(len(D))
    fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.6))
    bins = np.linspace(-1.0, 3.0, 81)
    for i, (n, (trem, dtau, rs)) in enumerate(D.items()):
        axs[0].hist(dtau[trem <= a.split], bins=bins, histtype="step", color=cols[i], label=n, density=True)
        axs[1].hist(dtau[trem > a.split], bins=bins, histtype="step", color=cols[i], label=n, density=True)
        b = J[n]["bins"]
        x = [r["t0"] + 5 for r in b if r["n"] >= 20]
        y = [100 * r["frac_below_0"] for r in b if r["n"] >= 20]
        axs[2].plot(x, y, "o-", ms=2.5, lw=0.8, color=cols[i], label=n)
    for ax, ttl in ((axs[0], rf"(a) $t_{{\rm rem}}\leq {a.split:g}M$"), (axs[1], rf"(b) $t_{{\rm rem}}>{a.split:g}M$")):
        ax.axvline(0, color="k", lw=0.7, ls="--")
        ax.set_xlabel(r"$\tau_{\rm rem}-\tau_H(R_0)$ [$M$]")
        ax.set_ylabel("density")
        ax.set_title(ttl, loc="left", fontsize=9)
        ax.set_yscale("log")
        ax.legend(fontsize=7)
    axs[2].axvline(a.split, color="k", lw=0.7, ls=":")
    axs[2].set_xlabel(r"$t_{\rm rem}/M$")
    axs[2].set_ylabel("removed before the exact crossing (%)")
    axs[2].set_title("(c) per 10 M bin of removal time", loc="left", fontsize=9)
    axs[2].legend(fontsize=7)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, "d4_timing." + ext), dpi=150)
    print(json.dumps({n: {k: v for k, v in o.items() if k != "bins"} for n, o in J.items()}, indent=1))


if __name__ == "__main__":
    main()
