#!/usr/bin/env python3
"""Outcome of test T5 of tracks/core/JOURNAL-clump.md: the two-overdensity data of the
first paper at t = 0 with and without the smeared Bowen-York curvature of the clumps.
Reads the run of run_jeans_t0.py and the regression run (first record of the unchanged
input), writes jeans_t0_check.json and figs/fig_clump_jeans_t0.{pdf,png}.

    jeans_t0_check.py --t5 RUN_ID --regress RUN_ID

Projection of the y component of the momentum constraint on the smooth field
T = -8 pi psi^-6 Stilde_y (continuum momentum density of the clumps, for the rule of the
particles): A = <M_y, T>/<T, T>, <f, g> = sum over cells of f g psi^6 dV. A = 1 if the
smooth part of the residual is the uncorrected one, 0 if it is removed.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mp_common import read_bin  # noqa: E402
from nrpic import clumps as clm  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import smeared_bowen_york as sby  # noqa: E402

COLS = dict(H2=3, M2=4, Mx2=6, My2=7, Mz2=8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t5", required=True)
    ap.add_argument("--regress", required=True)
    a = ap.parse_args()
    top = os.path.join(SCRATCH, a.t5)
    with open(os.path.join(top, "cases_t5.json")) as f:
        cs = json.load(f)
    with open(os.path.join(SCRATCH, a.regress, "regress.json")) as f:
        reg = json.load(f)["cases"]["jeans"]
    with open(os.path.join(HERE, "predict.json")) as f:
        pred = json.load(f)["two_overdensities"]
    out = dict(runs=dict(t5=a.t5, regress=a.regress), predicted=pred)
    out["record_t0"] = dict(
        run_n1e4_v19=[float(v) for v in reg["hst0_run_n1e4_v19"]],
        unchanged_input_this_executable=[float(v) for v in reg["hst0_new"]],
        columns="time dt C-norm2 H-norm2 M-norm2 Z-norm2 Mx-norm2 My-norm2 Mz-norm2 "
                "Theta-norm2 Volume")
    rows = {k: {c: v["hst0"][i] for c, i in COLS.items()} for k, v in cs["cases"].items()}
    out["norms2"] = rows
    out["change_with_curvature"] = {
        "run particles (rule velocity)": {c: rows["curv"][c] - rows["none"][c] for c in COLS},
        "rule gaussian": {c: rows["gauss_curv"][c] - rows["gauss_none"][c] for c in COLS}}

    # ---- fields
    J = clm.JeansModel(yc=0.907)
    Pg = [[float(s.split("=")[1]) for s in cs["momenta_gaussian_rule"][3 * k:3 * k + 3]]
          for k in (0, 1)]
    fields = {}
    proj = {}
    geom = None
    for lab in ("none", "curv", "gauss_none", "gauss_curv"):
        t, par, x, y, z, dx, var = read_bin(os.path.join(top, lab, "bin",
                                                         "jeans.con.00000.bin"))
        if geom is None:
            X = np.stack([x, y, z], axis=-1)
            psi = np.empty(len(x))
            for i0 in range(0, len(x), 500000):       # the envelope spline, in chunks
                psi[i0:i0 + 500000] = J.psi(X[i0:i0 + 500000])
            w = psi ** 6 * dx ** 3
            g = [sby.gaussian(np.sqrt(np.sum((X - J.centres[k]) ** 2, axis=-1)), J.sigma)
                 for k in (1, 2)]
            Tv = -8 * math.pi * psi ** -6 * sum(J.m_c * psi ** 3 * g[k] * J.velocities[k][1]
                                                for k in (0, 1))
            Tg = -8 * math.pi * psi ** -6 * sum(Pg[k][1] * g[k] for k in (0, 1))
            geom = True
            out["cells"] = int(len(x))
            out["smooth_field_norm2"] = dict(rule_velocity=float(np.sum(w * Tv ** 2)),
                                             rule_gaussian=float(np.sum(w * Tg ** 2)))
        T = Tg if lab.startswith("gauss") else Tv
        my = var["con_My"]
        proj[lab] = dict(
            A=float(np.sum(w * my * T) / np.sum(w * T * T)),
            My_norm2_from_dump=float(np.sum(w * my ** 2)),
            My_norm2_history=rows[lab]["My2"])
        fields[lab] = my
    out["projection_on_smooth_field"] = proj
    with open(os.path.join(HERE, "jeans_t0_check.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---- figure: M_y averaged over cubes of 0.5 M in the slab |z| < 0.5 M
    fs.use_style()
    half, nb = 6.0, 24
    hb = 2 * half / nb
    sel = (np.abs(z) < 0.5) & (np.abs(x) < half) & (np.abs(y) < half)
    ix = np.floor((x[sel] + half) / hb).astype(int)
    iy = np.floor((y[sel] + half) / hb).astype(int)
    vol = dx[sel] ** 3

    def coarse(f):
        num = np.zeros((nb, nb))
        den = np.zeros((nb, nb))
        np.add.at(num, (iy, ix), f[sel] * vol)
        np.add.at(den, (iy, ix), vol)
        return num / den

    panels = [("smooth field $T$ (closed form)", coarse(Tv)),
              (r"$K_{ij}=0$ (as run)", coarse(fields["none"])),
              ("smeared Bowen-York curvature", coarse(fields["curv"])),
              ("curvature, equal momentum per particle", coarse(fields["gauss_curv"]))]
    vmax = np.abs(panels[0][1]).max() * 1.5
    fig, ax = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.6), sharey=True)
    for axx, (title, img) in zip(ax, panels):
        im = axx.imshow(img, origin="lower", extent=(-half, half, -half, half),
                        cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        axx.set_title(title, fontsize=7.5)
        axx.set_xlabel("$x/M$")
    ax[0].set_ylabel("$y/M$")
    fig.colorbar(im, ax=ax, shrink=0.85, pad=0.015,
                 label=r"$\langle\mathcal{M}_y\rangle$ over $(0.5\,M)^2\times 1\,M$")
    fs.save(fig, os.path.join(HERE, "figs", "fig_clump_jeans_t0"))
    plt.close(fig)

    print("record at t = 0, run n1e4_v19      :", reg["hst0_run_n1e4_v19"])
    print("unchanged input, this executable   :", reg["hst0_new"])
    for k, v in rows.items():
        print(f"{k:11s} " + "  ".join(f"{c} {v[c]:.6e}" for c in COLS))
    for k, v in out["change_with_curvature"].items():
        print(f"change with curvature, {k}: " + "  ".join(f"{c} {v[c]:+.4e}" for c in COLS))
    print("predicted smooth part: My-norm2", pred["My_norm2_smooth"], "M-norm2",
          pred["M_norm2_smooth"], "; on the cells:", out["smooth_field_norm2"])
    for k, v in proj.items():
        print(f"projection {k:11s} A = {v['A']:+.4f}   My-norm2 dump {v['My_norm2_from_dump']:.6e} "
              f"history {v['My_norm2_history']:.6e}")


if __name__ == "__main__":
    main()
