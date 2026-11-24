#!/usr/bin/env python3
"""Where the finite-duration threshold (t_end = 45 in the core edge's proper time) lies on each
mesh: linear interpolation in delta_c of the proper time at first detection, tau_det, between the
bracket members, against the same interpolation of the exact tau_AH (threshold_ball entry 4/8).

    python -I threshold_interp.py --analysis DIR [--analysis DIR ...] --out DIR

Reads threshold.json of each analysis run (members with tau_det); later runs override earlier ones
for the same member. No prediction: arithmetic on judged numbers (entry 4); T7 judges mesh C.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T_END = 45.0


def cross(d, tau):
    """delta_c where tau(delta_c) crosses T_END, linear between the two bracketing points."""
    o = np.argsort(d)
    d, tau = np.asarray(d)[o], np.asarray(tau)[o]
    for i in range(len(d) - 1):
        if (tau[i] - T_END) * (tau[i + 1] - T_END) <= 0:
            w = (tau[i] - T_END) / (tau[i] - tau[i + 1])
            return float(d[i] + w * (d[i + 1] - d[i])), [float(d[i]), float(d[i + 1])]
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mem = {}
    for p in a.analysis:
        mem.update(json.load(open(os.path.join(p, "threshold.json")))["members"])
    res = {}
    meshes = sorted({n.split("-")[0] for n in mem if n[0] in "ABC" and n != "C-R1.25"})
    ex_d, ex_t = [], []
    for mesh in meshes:
        d, t = [], []
        for n, r in mem.items():
            if n.startswith(mesh + "-d") and r.get("tau_det") is not None:
                d.append(r["delta_c"])
                t.append(r["tau_det"])
            if n.startswith(mesh + "-d") and r["exact"]["tau_AH"] is not None:
                ex_d.append(r["delta_c"])
                ex_t.append(r["exact"]["tau_AH"])
        dc, br = cross(d, t)
        res[mesh] = dict(delta_c_threshold=dc, bracket=br, points=sorted(zip(d, t)))
    u = sorted(set(zip(ex_d, ex_t)))
    dc, br = cross([q[0] for q in u], [q[1] for q in u])
    res["exact"] = dict(delta_c_threshold=dc, bracket=br)
    json.dump(res, open(os.path.join(a.out, "threshold_interp.json"), "w"), indent=1)
    print(json.dumps({k: (v["delta_c_threshold"], v["bracket"]) for k, v in res.items()}, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH / 2, 3.0))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.16, top=0.9)
    ax.plot([q[0] for q in u], [q[1] for q in u], "k--", lw=1, label="exact")
    cs = {"A": fs.PAL["blue"], "B": fs.PAL["red"], "C": fs.PAL["yellow"]}
    for mesh in meshes:
        p = res[mesh]["points"]
        if p:
            ax.plot([q[0] for q in p], [q[1] for q in p], "o", color=cs.get(mesh, "k"), ms=4,
                    label="mesh %s (threshold %s)" % (mesh, "%.4f" % res[mesh]["delta_c_threshold"]
                                                      if res[mesh]["delta_c_threshold"] else "-"))
    ax.axhline(T_END, **fs.MASK_LINE)
    ax.set_xlim(0.33, 0.52)
    ax.set_ylim(33, 60)
    ax.set_xlabel(r"$\delta_c$")
    ax.set_ylabel(r"$\tau$ at the core edge's trapping")
    ax.set_title("threshold at $t_{\\rm end}=45$", fontsize=9)
    ax.legend(fontsize=7)
    fig.savefig(os.path.join(a.out, "fig_threshold_interp.png"), dpi=150)


if __name__ == "__main__":
    main()
