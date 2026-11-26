#!/usr/bin/env python3
"""Entry 16 of threshold_ball (C3-F): the constraint floor in the first 0.25 M.

    c3_first_step.py --out DIR NAME=RUNDIR [NAME=RUNDIR ...]

For each run directory (a member with tab/ball.con.*.tab, tab/ball.tmunu.*.tab and ball.z4c.user.hst):
  - section-3 line ratio ||H|| / ||16 pi E|| on the positive x line (weight x^2 dx), as edge_compare.py;
  - the same for the momentum constraint, ||M_x|| / ||8 pi S_x|| (con_Mx against tmunu_Sx);
  - the volume norms H-norm2 and M-norm2 of the history.
Writes DIR/c3_first_step.json and DIR/fig_c3_first_step.{pdf,png}.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from constraint_conv import load  # noqa: E402


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def lines(rd):
    by_t = {}
    for f in sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab"))):
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        _, m = read_tab(g)
        x = c["x1v"]
        o = np.argsort(x)
        sel = x[o] > 0
        x = x[o][sel]
        H, Mx = c["con_H"][o][sel], c["con_Mx"][o][sel]
        E, Sx = m["tmunu_E"][o][sel], m["tmunu_Sx"][o][sel]
        w = x ** 2 * np.gradient(x)

        def nrm(a):
            return math.sqrt(np.nansum(w * a ** 2))
        rec = dict(t=t, ratio_H=nrm(H) / nrm(16 * math.pi * E) if nrm(E) > 0 else float("nan"),
                   ratio_M=nrm(Mx) / nrm(8 * math.pi * Sx) if nrm(Sx) > 0 else float("nan"),
                   normH=nrm(H), normMx=nrm(Mx), norm16piE=nrm(16 * math.pi * E), norm8piSx=nrm(8 * math.pi * Sx),
                   file=os.path.basename(f))
        rec["_x"], rec["_H"], rec["_Mx"], rec["_E"], rec["_Sx"] = x, H, Mx, E, Sx
        by_t[round(t, 9)] = rec
    return [by_t[k] for k in sorted(by_t)]


def hist(rd):
    p = os.path.join(rd, "ball.z4c.user.hst")
    if not os.path.isfile(p):
        return None
    cz, z = load(p)
    t = z[:, 0]
    _, idx = np.unique(np.round(t, 9), return_index=True)
    z = z[idx]
    return dict(t=z[:, 0].tolist(), H=z[:, cz.index("H-norm2")].tolist(), M=z[:, cz.index("M-norm2")].tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile-t", type=float, default=None,
                    help="also draw |H| and 16 pi E on the x line at this time (panel d)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for spec in a.members:
        name, rd = spec.split("=", 1)
        ln = lines(rd)
        res[name] = dict(dir=rd, line=[{k: v for k, v in r.items() if not k.startswith("_")} for r in ln],
                         hist=hist(rd), _ln=ln)
    for name, r in res.items():
        print("==", name)
        for q in r["line"]:
            print("  t=%.6f  H/16piE=%.4g  Mx/8piSx=%.4g  |H|=%.3e |Mx|=%.3e" % (
                q["t"], q["ratio_H"], q["ratio_M"], q["normH"], q["normMx"]))
        h = r["hist"]
        if h:
            for t, H, M in zip(h["t"], h["H"], h["M"]):
                print("  hst t=%.6f H-norm2=%.5e M-norm2=%.5e" % (t, H, M))
    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    nax = 4 if a.profile_t is not None else 3
    fig, ax = plt.subplots(1, nax, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.88, wspace=0.45)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    for i, (name, r) in enumerate(res.items()):
        c = cols[i % len(cols)]
        t = [q["t"] for q in r["line"]]
        ax[0].plot(t, [q["ratio_H"] for q in r["line"]], color=c, marker="o", ms=3, label=name + r": $H$")
        ax[0].plot(t, [q["ratio_M"] for q in r["line"]], color=c, marker="s", ms=3, ls="--",
                   label=name + r": $M_x$")
        h = r["hist"]
        if h:
            ax[1].plot(h["t"], h["H"], color=c, marker="o", ms=3, label=name + r": $\|H\|_2$")
            ax[1].plot(h["t"], h["M"], color=c, marker="s", ms=3, ls="--", label=name + r": $\|M\|_2$")
        ln = r["_ln"]
        if ln:
            q = ln[0]
            ax[2].plot(q["_x"], q["_Mx"], color=c, label=name + r": $M_x$, t = %.2f" % q["t"])
            ax[2].plot(q["_x"], 8 * math.pi * q["_Sx"], color=c, ls="--", label=name + r": $8\pi S_x$")
    if a.profile_t is not None:
        prof = {}
        for i, (name, r) in enumerate(res.items()):
            c = cols[i % len(cols)]
            q = min(r["_ln"], key=lambda q: abs(q["t"] - a.profile_t))
            ax[3].semilogy(q["_x"], np.abs(q["_H"]) + 1e-12, color=c, label=name + r": $|H|$, t = %.2f" % q["t"])
            ax[3].semilogy(q["_x"], 16 * math.pi * np.abs(q["_E"]) + 1e-12, color=c, ls="--", label=name + r": $16\pi E$")
            prof[name] = dict(t=q["t"], x=q["_x"].tolist(), H=q["_H"].tolist(), E=q["_E"].tolist())
        ax[3].set_xlabel("x / M"); ax[3].set_title("(d) profiles", fontsize=8)
        ax[3].legend(loc="best", fontsize=5)
        with open(os.path.join(a.out, "profiles.json"), "w") as f:
            json.dump(prof, f)
    ax[0].axhline(0.1, **fs.MASK_LINE)
    ax[0].set_yscale("log"); ax[0].set_xlabel("t / M"); ax[0].set_ylabel("x-line ratio")
    ax[0].set_title("(a) constraint / source on the x line", fontsize=8)
    ax[1].set_yscale("log"); ax[1].set_xlabel("t / M"); ax[1].set_ylabel("volume norm")
    ax[1].set_title("(b) volume norms (history)", fontsize=8)
    ax[2].set_xlabel("x / M"); ax[2].set_ylabel("value on the x line")
    ax[2].set_title("(c) momentum constraint at the first record", fontsize=8)
    for k in range(3):
        ax[k].legend(loc="best", fontsize=6)
    fs.no_minor_labels(ax[0]); fs.no_minor_labels(ax[1])
    figs = fs.save(fig, os.path.join(a.out, "fig_c3_first_step"))
    for r in res.values():
        r.pop("_ln")
    with open(os.path.join(a.out, "c3_first_step.json"), "w") as f:
        json.dump(dict(members=res, figures=figs), f, indent=1)


if __name__ == "__main__":
    main()
