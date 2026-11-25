#!/usr/bin/env python3
"""The GR and the Newtonian particles of the population box at equal t, matched by tag
(predictions VC1, VC2, JOURNAL.md 2026-11-25 09:03, 09:05): rms velocity (GR u/(a W), Newton p/a),
their correlation, rms position difference in cells, and Omega_qs of both sets through one
estimator (analyze.TTBox at ng = 64).

    python3 vel_check.py --gr GRDIR --newton NDIR --pairs 1:16,4:64,7:112,10:160 [--out DIR]

GRDIR holds pop.part.NNNNN.bin, NDIR newton.part.NNNNN.bin. Writes vel_check.json and
fig_vel_check (PDF, PNG).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze as an                                   # noqa: E402
from analyze import RHO_C, scale, cic                  # noqa: E402
from nrpic.newton import read_snapshot                 # noqa: E402
from nrpic import figstyle as fs                       # noqa: E402

L = 8.0
NCELL = 128


def omega_qs(box, x, v, m, a):
    F = box.source(x, a*v, m, a)
    qs = np.zeros(box.k2.shape)
    for key in F:
        mult = 1.0 if key[0] == key[1] else 2.0
        qs += mult*np.abs(F[key])**2/box.k2s
    qs *= box.w/(32*np.pi)
    return float(qs[box.ok].sum())/(a*RHO_C)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gr", required=True)
    ap.add_argument("--newton", required=True)
    ap.add_argument("--pairs", default="1:16,4:64,7:112,10:160")
    ap.add_argument("--ng", type=int, default=64)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    box = an.TTBox(a.ng, L)
    rows = []
    for pr in a.pairs.split(","):
        ig, inw = (int(s) for s in pr.split(":"))
        tg, _, xg, ug, mg, tagg = read_snapshot(os.path.join(a.gr, "pop.part.%05d.bin" % ig))
        tn, _, xn, pn, mn, tagn = read_snapshot(os.path.join(a.newton, "newton.part.%05d.bin" % inw))
        og, on = np.argsort(tagg), np.argsort(tagn)
        assert np.array_equal(tagg[og], tagn[on])
        xg, ug, mg = xg[og], ug[og], mg[og]
        xn, pn, mn = xn[on], pn[on], mn[on]
        ag, anw = float(scale(tg)), float(scale(tn))
        W = np.sqrt(1.0 + (ug*ug).sum(1)/ag**2)
        vg = ug/(ag*W[:, None])
        vn = pn/anw
        dx = np.mod(xg - xn + 0.5*L, L) - 0.5*L
        rv = float(np.sqrt((vg*vg).sum(1).mean())/np.sqrt((vn*vn).sum(1).mean()))
        corr = float((vg*vn).sum()/np.sqrt((vg*vg).sum()*(vn*vn).sum()))
        # least-squares factor and the residual of v_GR against v_N
        lam = float((vg*vn).sum()/(vn*vn).sum())
        res = float(np.sqrt(((vg - lam*vn)**2).sum()/(vn*vn).sum()))
        og_ = omega_qs(box, xg, vg, mg, ag)
        on_ = omega_qs(box, xn, vn, mn, anw)
        # the two terms separately for the GR set: velocities zeroed
        og_phi = omega_qs(box, xg, 0*vg, mg, ag)
        on_phi = omega_qs(box, xn, 0*vn, mn, anw)
        # VC2: GR positions with the Newtonian masses, and the spread of the masses
        og_phi_mN = omega_qs(box, xg, 0*vg, mn, ag)
        og_mN = omega_qs(box, xg, vg, mn, ag)
        row = {"gr_snap": ig, "newton_snap": inw, "t_GR": tg, "t_N": tn, "a_GR": ag, "a_N": anw,
               "m_ratio": float(mg.sum()/mn.sum()), "rms_v_ratio": rv, "v_corr": corr,
               "v_lsq_factor": lam, "v_residual": res,
               "dx_rms_cells": float(np.sqrt((dx*dx).sum(1).mean())*NCELL/L),
               "dx_max_cells": float(np.sqrt((dx*dx).sum(1)).max()*NCELL/L),
               "Omega_qs_GR": og_, "Omega_qs_N": on_, "ratio": og_/on_,
               "Omega_qs_phi_only_GR": og_phi, "Omega_qs_phi_only_N": on_phi,
               "ratio_phi_only": og_phi/on_phi, "W_max": float(W.max()),
               "ratio_phi_only_GRpos_Nmass": og_phi_mN/on_phi, "ratio_GRpos_Nmass": og_mN/on_,
               "m_rel_spread_GR": float(mg.std()/mg.mean()), "m_rel_spread_N": float(mn.std()/mn.mean()),
               "m_GR_over_N_rel_spread": float((mg/mn).std()/(mg/mn).mean())}
        rows.append(row)
        print(json.dumps(row))
    with open(os.path.join(a.out, "vel_check.json"), "w") as f:
        json.dump(rows, f, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.6))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.18, top=0.93, wspace=0.3)
    aa = [r["a_GR"] for r in rows]
    axs[0].semilogx(aa, [r["rms_v_ratio"] for r in rows], "o-", color=fs.SERIES[0],
                    label=r"rms $v_{\rm GR}$ / rms $v_{\rm N}$")
    axs[0].semilogx(aa, [r["v_lsq_factor"] for r in rows], "s--", color=fs.SERIES[1],
                    label=r"least-squares factor $v_{\rm GR} \approx \lambda v_{\rm N}$")
    axs[0].semilogx(aa, [r["v_residual"] for r in rows], "^:", color=fs.SERIES[2],
                    label="residual / rms $v_{\\rm N}$")
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel("velocity, GR against Newton")
    axs[0].legend(fontsize=6)
    axs[1].semilogx(aa, [r["ratio"] for r in rows], "o-", color=fs.SERIES[0],
                    label=r"$\Omega_{\rm qs}$, one estimator, full source")
    axs[1].semilogx(aa, [r["ratio_phi_only"] for r in rows], "s--", color=fs.SERIES[1],
                    label=r"$\Omega_{\rm qs}$, potential term only")
    axs[1].semilogx(aa, [r["ratio_GRpos_Nmass"] for r in rows], "^:", color=fs.SERIES[2],
                    label="GR positions and velocities, Newtonian masses")
    axs[1].set_yscale("log")
    axs[1].axhspan(0.9, 1.1, color="0.9")
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel("GR particles / Newtonian particles")
    axs[1].legend(fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig_vel_check"))
    plt.close(fig)


if __name__ == "__main__":
    main()
