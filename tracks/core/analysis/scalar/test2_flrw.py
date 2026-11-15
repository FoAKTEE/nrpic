#!/usr/bin/env python3
"""Test 2 of the scalar field: homogeneous slow roll in a quadratic potential with the
evolved metric, against the Friedmann and Klein-Gordon ordinary differential equations
in the same gauge (JOURNAL-scalar.md, prediction P2).

Gauges: conformal time (d_t alpha = -(1/3) alpha^2 K, to t = 1.2) and geodesic slicing
(alpha = 1, to t = 8).  Mesh 8^3 with box 0.5 (cell size 1/16); Courant factors 0.5, 0.25,
0.125.

Usage: test2_flrw.py --exe ATHENA   (run in the output directory)
"""
import argparse
import json
import os

import numpy as np

import common
from common import PROB, mesh_args, run_many
from nrpic import scalar_field as sfr

INP = os.path.join(PROB, "flrw_slowroll.athinput")
MASS, PHI0 = 0.1, 3.0
H0SR = float(np.sqrt(4.0*np.pi/3.0)*MASS*PHI0)
PI0 = float(-MASS**2*PHI0/(3.0*H0SR))
CFLS = [0.5, 0.25, 0.125]
GAUGES = {"conformal": (["z4c/lapse_harmonic=0.3333333333333333"], 1.2),
          "geodesic": (["z4c/lapse_harmonic=0.0"], 8.0)}
KEYS = ["a", "phi", "Pi", "K", "alpha"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    top = os.getcwd()
    v, dv = sfr.potential("quadratic", mass=MASS)
    cases, keys = [], []
    for g, (ga, tend) in GAUGES.items():
        for c in CFLS:
            keys.append((g, c))
            cases.append((os.path.join(top, f"{g}_cfl{c}"), INP,
                          mesh_args(8, 8, 8) + ga + [
                              "mesh/x1max=0.5", "mesh/x2max=0.5", "mesh/x3max=0.5",
                              f"time/cfl_number={c}", f"time/tlim={tend}",
                              f"problem/pi0={PI0!r}", f"problem/phi0={PHI0}"]))
    wall = run_many(args.exe, cases, args.workers)
    summary = {"exe": os.path.abspath(args.exe), "pi0": PI0, "cases": {}}
    series = {}
    for (g, c), (rd, _, _), w in zip(keys, cases, wall):
        h = sfr.read_history(os.path.join(rd, "sr.sf.hst"))
        ref = sfr.friedmann(v, dv, PHI0, PI0, h["time"][1:], gauge=g)
        code = dict(a=h["chi"][1:]**-0.5, phi=h["phi"][1:], Pi=h["Pi"][1:], K=h["K"][1:],
                    alpha=h["alpha"][1:])
        refd = dict(a=np.exp(ref["ln_a"]), phi=ref["phi"], Pi=ref["Pi"], K=ref["K"],
                    alpha=ref["alpha"])
        err = {k: np.abs(code[k]/refd[k] - 1.0) for k in KEYS}
        eps1 = 4.0*np.pi*code["Pi"]**2/(code["K"]/3.0)**2
        series[(g, c)] = dict(t=h["time"][1:], err=err, code=code, ref=refd,
                              hrel=h["H_rms"][1:]/h["H_norm"][1:], hrel0=h["H_rms"][0]/h["H_norm"][0],
                              mrms=h["M_rms"], rms_phi=h["rms_phi"])
        summary["cases"][f"{g}_{c}"] = dict(
            gauge=g, cfl=c, steps=int(h["cycle"][-1]), t_end=float(h["time"][-1]),
            a_end=float(code["a"][-1]), efolds=float(np.log(code["a"][-1])),
            err_end={k: float(err[k][-1]) for k in KEYS},
            err_max={k: float(err[k].max()) for k in KEYS},
            eps1_end=float(eps1[-1]), eps1_slowroll_end=float(1.0/(4.0*np.pi*code["phi"][-1]**2)),
            eps1_ratio_range=[float((eps1*4.0*np.pi*code["phi"]**2).min()),
                              float((eps1*4.0*np.pi*code["phi"]**2).max())],
            H_rel_start=float(h["H_rms"][0]/h["H_norm"][0]),
            H_rel_end=float(h["H_rms"][-1]/h["H_norm"][-1]),
            H_rel_max=float((h["H_rms"]/h["H_norm"]).max()),
            M_rms_max=float(h["M_rms"].max()), rms_phi_max=float(h["rms_phi"].max()),
            wall_s=w)
    # convergence: ratio of the errors at the end between successive Courant factors
    for g in GAUGES:
        summary[f"ratio_{g}"] = {
            k: [summary["cases"][f"{g}_{CFLS[i]}"]["err_end"][k]
                / summary["cases"][f"{g}_{CFLS[i+1]}"]["err_end"][k] for i in range(2)]
            for k in KEYS}
        summary[f"ratio_H_{g}"] = [summary["cases"][f"{g}_{CFLS[i]}"]["H_rel_end"]
                                   / summary["cases"][f"{g}_{CFLS[i+1]}"]["H_rel_end"]
                                   for i in range(2)]
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = {0.5: fs.PAL["yellow"], 0.25: fs.PAL["red"], 0.125: fs.PAL["blue"]}
    for g in GAUGES:
        fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
        fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, wspace=0.28,
                            hspace=0.25)
        s = series[(g, 0.25)]
        ax[0, 0].plot(s["t"], s["code"]["a"], color=fs.PAL["red"], label="scale factor, code")
        ax[0, 0].plot(s["t"], s["ref"]["a"], **fs.GUIDE, label="Friedmann and Klein-Gordon")
        ax[0, 0].plot(s["t"], s["code"]["alpha"], color=fs.PAL["red"], ls=":", label="lapse, code")
        ax[0, 0].set_yscale("log")
        ax[0, 0].set_xlabel("coordinate time")
        ax[0, 0].set_ylabel("scale factor, lapse")
        ax[0, 0].legend(loc="upper left")
        ax[0, 1].plot(s["t"], s["code"]["phi"]/PHI0, color=fs.PAL["red"], label=r"$\phi/\phi_0$, code")
        ax[0, 1].plot(s["t"], s["ref"]["phi"]/PHI0, **fs.GUIDE)
        ax[0, 1].plot(s["t"], s["code"]["Pi"]/PI0, color=fs.PAL["blue"], label=r"$\Pi/\Pi_0$, code")
        ax[0, 1].plot(s["t"], s["ref"]["Pi"]/PI0, **fs.GUIDE)
        ax[0, 1].plot(s["t"], s["code"]["K"]/s["code"]["K"][0], color=fs.PAL["yellow"],
                      label=r"$K/K_0$, code")
        ax[0, 1].plot(s["t"], s["ref"]["K"]/s["ref"]["K"][0], **fs.GUIDE)
        ax[0, 1].set_xlabel("coordinate time")
        ax[0, 1].set_ylabel("field, momentum, mean curvature")
        ax[0, 1].legend(loc="lower left")
        for c in CFLS:
            s = series[(g, c)]
            ax[1, 0].semilogy(s["t"], np.maximum(s["err"]["a"], 1e-18), color=cols[c],
                              label=f"a, Courant {c}")
            ax[1, 0].semilogy(s["t"], np.maximum(s["err"]["phi"], 1e-18), color=cols[c], ls="--")
            ax[1, 1].semilogy(s["t"], np.maximum(s["hrel"], 1e-18), color=cols[c],
                              label=f"Courant {c}")
        ax[1, 0].set_xlabel("coordinate time")
        ax[1, 0].set_ylabel("relative difference to the reference")
        ax[1, 0].legend(loc="lower right", fontsize=8)
        ax[1, 1].set_xlabel("coordinate time")
        ax[1, 1].set_ylabel(r"rms $H$ / $\langle[H]\rangle$")
        ax[1, 1].legend(loc="lower right", fontsize=8)
        fs.save(fig, os.path.join(top, f"fig_flrw_{g}"))
        plt.close(fig)


if __name__ == "__main__":
    main()
