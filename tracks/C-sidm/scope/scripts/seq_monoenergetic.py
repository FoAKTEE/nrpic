#!/usr/bin/env python3
"""Monoenergetic (Shapiro-Teukolsky) cluster sequence: binding energy, redshift and
compactness against y_c, the first binding-energy maximum, and the five models of the
first paper of this repository (paper/sections/self_gravity.tex) and of Wu and Most.

Uses python/nrpic/st_cluster.py (the reference module the cluster runs were built from).
Output (in $NRPIC_RUN_DIR): seq_monoenergetic.json, fig_seq_monoenergetic.{pdf,png}.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import st_cluster as st          # noqa: E402
from nrpic import figstyle as fs           # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", ".")

# Table tab:st-suite of arXiv:2611.12831 (kb-data/raw/arxiv/2611.12831/v1/src/main.tex,
# lines 1024-1028): y_c, z_c, R/M, M_0/M, outcome
WM = [(0.900, 0.125, 16.4282, 1.019453, "stable"),
      (0.819, 0.236, 9.9642, 1.030106, "stable"),
      (0.605, 0.592, 5.7502, 1.035171, "collapse"),
      (0.500, 0.817, 5.0758, 1.023830, "collapse"),
      (0.283, 1.504, 4.5846, 0.961732, "disperse")]
NEAR = 0.756          # near-critical model of both papers


def main():
    ys = np.concatenate([np.linspace(0.985, 0.30, 140), np.linspace(0.30, 0.22, 9)[1:]])
    rows = []
    for y in ys:
        g = st.st_global(float(y))
        rows.append(dict(yc=float(y), zc=g["zc"], Eb_over_M0=g["Eb_over_M0"],
                         R_over_M=g["R_over_M"], M0_over_M=g["M0_over_M"],
                         compactness=1.0 / g["R_over_M"]))
    bmax = st.binding_energy_maximum()
    # first zero of E_b
    zs = [r for r in rows if r["Eb_over_M0"] < 0]
    from scipy.optimize import brentq
    y_zero = brentq(lambda v: st.eb_over_m0(v), zs[0]["yc"], bmax["yc"], xtol=1e-12)
    g0 = st.st_global(y_zero)
    check = []
    for yc, zc, RM, M0M, fate in WM + [(NEAR, None, None, None, "near-critical")]:
        g = st.st_global(yc)
        check.append(dict(yc=yc, fate=fate, zc=g["zc"], zc_WM=zc, R_over_M=g["R_over_M"],
                          R_over_M_WM=RM, M0_over_M=g["M0_over_M"], M0_over_M_WM=M0M,
                          Eb_over_M0=g["Eb_over_M0"], compactness=1.0 / g["R_over_M"],
                          side="stable" if yc > bmax["yc"] else "unstable"))
    res = dict(binding_energy_maximum=dict(**bmax, compactness=1.0 / bmax["R_over_M"]),
               binding_energy_zero=dict(yc=y_zero, zc=g0["zc"], R_over_M=g0["R_over_M"]),
               models=check, sequence=rows)
    with open(os.path.join(OUT, "seq_monoenergetic.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.1))
    a1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.4)
    a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.4)
    zc = np.array([r["zc"] for r in rows])
    eb = np.array([r["Eb_over_M0"] for r in rows])
    yc = np.array([r["yc"] for r in rows])
    cm = np.array([r["compactness"] for r in rows])
    a1.plot(zc, eb, color=fs.PAL["blue"], label="equilibrium sequence")
    a1.axvline(bmax["zc"], ls=":", **fs.THIN)
    a1.axhline(0.0, **fs.MASK_LINE)
    mk = {"stable": dict(marker="o", mfc="white"), "collapse": dict(marker="s"),
          "disperse": dict(marker="^"), "near-critical": dict(marker="D", mfc="white")}
    off = {0.900: (5, -10), 0.819: (5, -10), 0.756: (-12, 7), 0.605: (5, -11),
           0.500: (5, -10), 0.283: (4, 5)}
    for c in check:
        a1.plot(c["zc"], c["Eb_over_M0"], ls="none", ms=6, color=fs.PAL["red"],
                mec=fs.PAL["red"], label=c["fate"] if c["fate"] != "near-critical"
                else "near-critical (0.756)", **mk[c["fate"]])
        a1.annotate(f"{c['yc']:.3f}", (c["zc"], c["Eb_over_M0"]), textcoords="offset points",
                    xytext=off[c["yc"]], fontsize=8)
    h, lab = a1.get_legend_handles_labels()
    keep = {l: hh for hh, l in zip(h, lab)}
    a1.legend(keep.values(), keep.keys(), loc="lower left", fontsize=8)
    a1.set_xlim(0, 1.6)
    a1.set_xlabel(r"central redshift $z_c$")
    a1.set_ylabel(r"$E_b/M_0$")
    a1.text(bmax["zc"] + 0.02, 0.002, f"maximum\n$y_c$={bmax['yc']:.4f}", fontsize=8)
    a2.plot(yc, cm, color=fs.PAL["blue"])
    a2.axvline(bmax["yc"], ls=":", **fs.THIN)
    for c in check:
        a2.plot(c["yc"], c["compactness"], ls="none", ms=6, color=fs.PAL["red"],
                mec=fs.PAL["red"], **mk[c["fate"]])
    a2.set_xlim(1.0, 0.2)
    a2.set_xlabel(r"$y_c=(\alpha_c/\alpha_s)^2$")
    a2.set_ylabel(r"compactness $M/R$ (areal)")
    fs.save(fig, os.path.join(OUT, "fig_seq_monoenergetic"))
    print(json.dumps(res["binding_energy_maximum"], indent=1))
    print(json.dumps(res["binding_energy_zero"], indent=1))
    for c in check:
        print(c)


if __name__ == "__main__":
    main()
