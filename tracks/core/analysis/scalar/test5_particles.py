#!/usr/bin/env python3
"""Test 5 of the scalar field: sources of particles and field together.

A dust universe of NRPIC particles (problems/cosmo/flrw.athinput, density-form sources,
conformal-time lapse) with a vacuum energy, supplied in two ways:
  lam    by the particle module, <particles> lambda = Lambda (no scalar field)
  field  by a scalar field at rest with the constant potential v_offset = Lambda/(8 pi)
  zero   scalar field present with v_offset = 0, against the particle run with lambda = 0
The pairs solve the same equations with different arithmetic (the sources of the second
member go through Tmunu::tmunu_tot); their histories must agree to rounding.

Usage: test5_particles.py --exe ATHENA --particles FILE   (run in the output directory)
"""
import argparse
import json
import os

import numpy as np

import common
from common import PROB, REPO, run_many


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--particles", required=True)
    ap.add_argument("--lam", type=float, default=0.6)
    args = ap.parse_args()
    top = os.getcwd()
    base = os.path.join(REPO, "problems", "cosmo", "flrw.athinput")
    fld = os.path.join(PROB, "flrw_dust_field.athinput")
    com = [f"particles/particle_file={os.path.abspath(args.particles)}", "time/tlim=0.5"]
    cases = [
        (os.path.join(top, "lam"), base, com + [f"particles/lambda={args.lam}"]),
        (os.path.join(top, "field"), fld, com + ["particles/lambda=0.0",
                                                 f"scalar_field/v_offset={args.lam/(8.0*np.pi)!r}"]),
        (os.path.join(top, "lam0"), base, com + ["particles/lambda=0.0"]),
        (os.path.join(top, "zero"), fld, com + ["particles/lambda=0.0"]),
    ]
    wall = run_many(args.exe, cases, 4)
    res = {"exe": os.path.abspath(args.exe), "lambda": args.lam, "wall_s": wall}
    # columns of <basename>.nrpic.hst: 13 alpha at the probe, 15 proper time of the probe,
    # 28 proper volume; of <basename>.cstat.hst: all columns
    for a, b, name in (("lam", "field", "vacuum_energy"), ("lam0", "zero", "field_at_zero")):
        ha = np.loadtxt(os.path.join(top, a, "flrw.nrpic.hst"))
        hb = np.loadtxt(os.path.join(top, b, "flrwsf.nrpic.hst"))
        out = {"steps": int(ha[-1, 1])}
        for col, label in ((12, "alpha_probe"), (14, "tau_probe"), (27, "proper_volume"),
                           (8, "int_E")):
            out[label] = float(np.max(np.abs(ha[:, col] - hb[:, col])
                                      / np.maximum(np.abs(ha[:, col]), 1e-300)))
        out["volume_end"] = [float(ha[-1, 27]), float(hb[-1, 27])]
        res[name] = out
    # effect of the vacuum energy itself: lam against lam0 (the test is not vacuous)
    h1 = np.loadtxt(os.path.join(top, "lam", "flrw.nrpic.hst"))
    h0 = np.loadtxt(os.path.join(top, "lam0", "flrw.nrpic.hst"))
    res["effect_of_lambda_on_volume"] = float(abs(h1[-1, 27]/h0[-1, 27] - 1.0))
    # constraints of the run with the field: the scalar module's history (all sources)
    sf = np.loadtxt(os.path.join(top, "field", "flrwsf.sf.hst"))
    res["field_run_H_rms_over_norm"] = [float(sf[0, 11]/sf[0, 16]), float(sf[-1, 11]/sf[-1, 16])]
    res["field_run_E_mean"] = [float(sf[0, 9]), float(sf[-1, 9])]
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.15, top=0.95, wspace=0.32)
    hf = np.loadtxt(os.path.join(top, "field", "flrwsf.nrpic.hst"))
    ax[0].plot(h0[:, 0], h0[:, 27]/h0[0, 27], color=fs.PAL["yellow"], label="dust alone")
    ax[0].plot(h1[:, 0], h1[:, 27]/h1[0, 27], color=fs.PAL["blue"],
               label=r"dust and $\Lambda$ of the particle module")
    ax[0].plot(hf[:, 0], hf[:, 27]/hf[0, 27], color=fs.PAL["red"], ls="--",
               label="dust and a field at rest, constant potential")
    ax[0].set_xlabel("conformal time")
    ax[0].set_ylabel("proper volume / initial")
    ax[0].legend(loc="upper left", fontsize=8)
    d = np.abs(h1[:, 27] - hf[:, 27])/h1[:, 27]
    ax[1].semilogy(h1[1:, 0], np.maximum(d[1:], 1e-18), color=fs.PAL["red"], label="proper volume")
    d = np.abs(h1[:, 12] - hf[:, 12])/h1[:, 12]
    ax[1].semilogy(h1[1:, 0], np.maximum(d[1:], 1e-18), color=fs.PAL["blue"], label="lapse at the probe")
    ax[1].set_xlabel("conformal time")
    ax[1].set_ylabel("relative difference of the two runs")
    ax[1].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(top, "fig_particles_field"))
    plt.close(fig)


if __name__ == "__main__":
    main()
