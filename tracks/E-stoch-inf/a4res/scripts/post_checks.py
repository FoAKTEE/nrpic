#!/usr/bin/env python3
"""Post-hoc checks of package a4res (JOURNAL entry 4; written after the analysis
E-20261121-151643-c2c0f5a was seen, labelled post hoc wherever quoted).

    python3 post_checks.py --ana A4RES_JSON --out DIR

1. Q6 failed at one dump only (t = 0.147, the first after t = 0): is that the log-linear
   time interpolation of the 128^3 even part onto the 64^3 dump time? Compares
   E_A(N64q64)/E_A(N128q64) with linear and quadratic (three-point) interpolation of
   log E_128 in t, and at t = 0, where both runs have a dump at the same time.
   Refuted (the interpolation is not the cause) if the quadratic ratio at t = 0.147 is
   still outside 1 +- 0.05 or the t = 0 ratio is.
2. A4'(b) had no dump with O_B > 10 f_o in N64q16, N128q100, N128q64: the halving of the
   odd part at the relaxed threshold O_B > 5 f_o (post hoc).
Writes DIR/post.json and DIR/fig_post.png."""
import argparse
import json
import os

import numpy as np


def quad_interp(t, tt, yy):
    i = int(np.clip(np.searchsorted(tt, t) - 1, 0, len(tt) - 3))
    x, y = tt[i:i+3], np.log(yy[i:i+3])
    return float(np.exp(np.polyval(np.polyfit(x, y, 2), t)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ana", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = json.load(open(a.ana))
    S = {s["name"]: s for s in d["setups"]}
    lo, hi = S["N64q64"]["rows"], S["N128q64"]["rows"]
    th = np.array([r["time"] for r in hi])
    out = dict(source=a.ana, q6=[], halving_odd_5f={})
    for X in ("H", "M"):
        eh = np.array([r[f"E_A_{X}"] for r in hi])
        out[f"t0_ratio_{X}"] = lo[0][f"E_A_{X}"]/hi[0][f"E_A_{X}"]
    for r in lo[1:9]:
        row = dict(time=r["time"])
        for X in ("H", "M"):
            eh = np.array([x[f"E_A_{X}"] for x in hi])
            lin = float(np.exp(np.interp(r["time"], th, np.log(eh))))
            row[f"lin_{X}"] = r[f"E_A_{X}"]/lin
            row[f"quad_{X}"] = r[f"E_A_{X}"]/quad_interp(r["time"], th, eh)
        out["q6"].append(row)
    for name in ("N64q16", "N128q100", "N128q64"):
        rr = S[name]["rows"]
        res = {}
        for X in ("H", "M"):
            q = [(r["time"], r[f"O_A_{X}"]/r[f"O_B_{X}"]) for r in rr
                 if r["time"] > 0 and r[f"O_B_{X}"] > 5*r[f"f_o_{X}"]]
            res[X] = dict(n=len(q), min=min((x for _, x in q), default=None),
                          max=max((x for _, x in q), default=None),
                          largest_OB_over_fo=max(r[f"O_B_{X}"]/r[f"f_o_{X}"] for r in rr
                                                 if r["time"] > 0))
        out["halving_odd_5f"][name] = res
    r0 = out["q6"][0]
    out["q6_interpolation_explains"] = bool(abs(r0["quad_H"] - 1) <= 0.05 and
                                            abs(r0["quad_M"] - 1) <= 0.05 and
                                            abs(out["t0_ratio_H"] - 1) <= 0.05 and
                                            abs(out["t0_ratio_M"] - 1) <= 0.05)
    with open(os.path.join(a.out, "post.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps(out, indent=1))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.16, top=0.92, wspace=0.3)
    t = [r["time"] for r in out["q6"]]
    for X, mk in (("H", "o"), ("M", "^")):
        ax[0].plot(t, [r[f"lin_{X}"] for r in out["q6"]], mk, color=fs.PAL["red"],
                   label=f"log-linear in $t$, ${X}$")
        ax[0].plot(t, [r[f"quad_{X}"] for r in out["q6"]], mk, mfc="none",
                   color=fs.PAL["blue"], label=f"three-point quadratic, ${X}$")
        ax[0].plot([0.0], [out[f"t0_ratio_{X}"]], mk, color="k",
                   label=f"$t=0$ (same time), ${X}$")
    fs.band(ax[0], [0, 1.05], [0.95, 0.95], [1.05, 1.05], "grey", 0.2)
    ax[0].set_xlabel("$t$")
    ax[0].set_ylabel(r"$E_A$(N64q64) / $E_A$(N128q64)")
    ax[0].legend(fontsize=5)
    ax[0].set_title("(a) post hoc: Q6 at the first dumps", loc="left", fontsize=8)
    for i, (name, res) in enumerate(out["halving_odd_5f"].items()):
        rr = S[name]["rows"]
        for X, mk in (("H", "o"), ("M", "^")):
            tt = [r["time"] for r in rr if r["time"] > 0]
            y = [r[f"O_A_{X}"]/r[f"O_B_{X}"] for r in rr if r["time"] > 0]
            ok = [r[f"O_B_{X}"] > 5*r[f"f_o_{X}"] for r in rr if r["time"] > 0]
            c = fs.SERIES[i]
            ax[1].plot([x for x, k in zip(tt, ok) if k], [x for x, k in zip(y, ok) if k], mk,
                       color=c, label=f"{name}, ${X}$")
            ax[1].plot([x for x, k in zip(tt, ok) if not k],
                       [x for x, k in zip(y, ok) if not k], mk, mfc="none", color=c, alpha=0.4)
    fs.band(ax[1], [0, 4.6], [1.95, 1.95], [2.05, 2.05], "grey", 0.3)
    ax[1].set_ylim(1.0, 2.2)
    ax[1].set_xlabel("$t$")
    ax[1].set_ylabel(r"$O_A/O_B$ (filled: $O_B > 5 f_o$)")
    ax[1].legend(fontsize=5, loc="lower center", ncol=2)
    ax[1].set_title("(b) post hoc: odd halving at 5 floors", loc="left", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_post.png"), dpi=200)


if __name__ == "__main__":
    main()
