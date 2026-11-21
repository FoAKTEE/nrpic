#!/usr/bin/env python3
"""Three-way convergence figure of the coupled module (stage check C9: particle number,
mesh, gauge and boundary), drawn from existing run outputs; no new simulation.

(a) particle number: norm of the Hamiltonian constraint, sqrt(H-norm2) of
    <base>.z4c.user.hst, at t = 0 and averaged over 200-300 M, for the stable cluster
    y_c = 0.819 at N = 1e2, 1e3, 1e4 (Monte Carlo and stratified samples; earlier runs
    /data/haiyangw/nrpic/runs/st/yc0819_{mc_n100,mc_n1000,mc_n10000}_v4 and
    yc0819_{n1e2,n1e3}_v4, yc0819_v4; docs/TESTLOG.md);
(b) mesh: expanding ball (format-2 initial data, smooth edge, conformal-time lapse,
    sources extrapolated), largest |R/R_exact - 1| at tau = 8 M per shell group against
    dx (runs of tracks/core/analysis/id, numbers of the registered analysis
    core-20261115-145804-3629622, analysis/id/test2_numbers.json.gz);
(c) gauge and boundary: the same error, largest over the ball shells, for five gauge and
    surface choices against dx; and the tracers at 2 R_out (24 M) over the whole run with
    the mesh boundary at 32 M and at 48 M (dx = M/2).

    python3 convergence3.py [--out tracks/core/verify/figs/convergence_three_way]
"""
import argparse
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ST = "/data/haiyangw/nrpic/runs/st"
T2 = os.path.join(WT, "tracks", "core", "analysis", "id", "test2_numbers.json.gz")
NSETS = {"Monte Carlo": ["yc0819_mc_n100_v4", "yc0819_mc_n1000_v4", "yc0819_mc_n10000_v4"],
         "stratified": ["yc0819_n1e2_v4", "yc0819_n1e3_v4", "yc0819_v4"]}
NVAL = [1e2, 1e3, 1e4]
GAUGES = [("mp", r"1+log, sharp surface"), ("ct", r"conformal time, sharp"),
          ("mp-edge2", r"1+log, smooth edge"), ("ct-edge2-ext", r"conformal time, smooth"),
          ("gs0-edge2-ext", r"lapse 1, shift 0, smooth")]


def hnorm(run):
    a = np.loadtxt(os.path.join(ST, run, "st.z4c.user.hst"))
    t, h = a[:, 0], np.sqrt(np.abs(a[:, 3]))
    late = (t >= 200.0) & (t <= 300.0)
    return float(h[0]), float(h[late].mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "figs", "convergence_three_way"))
    a = ap.parse_args()
    t2 = json.load(gzip.open(T2))
    res = dict(particle_number={}, mesh={}, gauge={}, boundary={})
    for lab, runs in NSETS.items():
        v = [hnorm(r) for r in runs]
        res["particle_number"][lab] = dict(N=NVAL, runs=runs, H0=[x[0] for x in v],
                                           H_late=[x[1] for x in v])
    fam = "ct-edge2-ext"
    keys = [f"{fam}-n064", f"{fam}-n128", f"{fam}-n256"]
    for g in ("core", "mid", "outer", "surface"):
        res["mesh"][g] = dict(dx=[t2[k]["dx"] for k in keys], run_ids=[t2[k]["run_id"] for k in keys],
                              err=[t2[k]["groups"][g]["tau8"]["maxabs"] for k in keys])
    for f, lab in GAUGES:
        ks = [k for k in t2 if k.rsplit("-n", 1)[0] == f]
        ks.sort(key=lambda k: -t2[k]["dx"])
        res["gauge"][f] = dict(label=lab, dx=[t2[k]["dx"] for k in ks],
                               run_ids=[t2[k]["run_id"] for k in ks],
                               err=[max(t2[k]["groups"][g]["tau8"]["maxabs"]
                                        for g in ("core", "mid", "outer", "surface")) for k in ks])
    for k, lab in (("ct-edge2-n128", "boundary at 32 M"), ("ct-edge2-big-n192", "boundary at 48 M")):
        res["boundary"][lab] = dict(run_id=t2[k]["run_id"], dx=t2[k]["dx"],
                                    tracer2_all=t2[k]["groups"]["tracer2"]["maxabs_all"],
                                    core_tau8=t2[k]["groups"]["core"]["tau8"]["maxabs"])
    print(json.dumps(res, indent=1))
    with open("convergence3.json", "w") as f:
        json.dump(res, f)

    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.90, wspace=0.38)
    N = np.array(NVAL)
    for (lab, v), c in zip(res["particle_number"].items(), (fs.PAL["blue"], fs.PAL["red"])):
        ax[0].loglog(N, v["H0"], "o-", color=c, label=f"{lab}, $t=0$")
        ax[0].loglog(N, v["H_late"], "s--", color=c, mfc="none", label=f"{lab}, 200-300 M")
    ax[0].loglog(N, 1.9 * (N / 100.0) ** -0.5, **fs.GUIDE, label=r"$\propto N^{-1/2}$")
    ax[0].set_xlabel(r"particle number $N$", labelpad=-2)
    ax[0].set_ylabel(r"$\|H\|$ (cluster $y_c=0.819$)")
    ax[0].set_title("particle number", fontsize=10)
    ax[0].legend(fontsize=6.5, loc="lower left")
    dxs = np.array([1.0, 0.5, 0.25])
    for g, c in zip(("core", "mid", "outer", "surface"), fs.SERIES):
        v = res["mesh"][g]
        ax[1].loglog(v["dx"], v["err"], "o-", color=c, label=g)
    ax[1].loglog(dxs, 1.1e-4 * (dxs / 0.5) ** 2, **fs.GUIDE, label=r"$\propto\Delta x^2$")
    ax[1].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[1].set_ylabel(r"largest $|R/R_{\rm exact}-1|$ at $\tau=8\,M$")
    ax[1].set_title("mesh (expanding ball)", fontsize=10)
    ax[1].legend(fontsize=6.5, loc="lower right")
    cols = fs.series_colors(len(GAUGES), cmap="turbo")
    for (f, lab), c in zip(GAUGES, cols):
        v = res["gauge"][f]
        ax[2].loglog(v["dx"], v["err"], "o-", color=c, label=lab, ms=3.5)
    b = res["boundary"]
    ax[2].loglog([0.5], [b["boundary at 32 M"]["tracer2_all"]], "*", color="k", ms=8,
                 label=r"tracers at 24 M, boundary 32 M")
    ax[2].loglog([0.5], [b["boundary at 48 M"]["tracer2_all"]], "*", color="k", mfc="none", ms=8,
                 label=r"same, boundary 48 M")
    ax[2].loglog(dxs, 4e-3 * dxs, color="k", ls=":", lw=1.0, label=r"$\propto\Delta x$")
    ax[2].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[2].set_ylabel(r"largest $|R/R_{\rm exact}-1|$, all shells")
    ax[2].set_title("gauge and boundary", fontsize=10)
    ax[2].legend(fontsize=5.6, loc="upper right", ncol=1)
    ax[2].set_ylim(1e-7, 100.0)
    for x in ax[1:]:
        x.set_xticks([0.25, 0.5, 1.0])
        x.set_xticklabels(["1/4", "1/2", "1"])
        x.xaxis.set_minor_formatter(plt.NullFormatter())
    fs.save(fig, os.path.abspath(a.out))
    print("wrote", os.path.abspath(a.out) + ".png")


if __name__ == "__main__":
    main()
