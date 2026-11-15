#!/usr/bin/env python3
"""Replay of single collision steps with the Python twin (python/nrpic/collide.py):
the code dumps the state before and after the collision step of one cycle
(<particles> coll_dump_cycle); the twin repeats the step from the "before" state
(pairing words, order in the cell, sub-steps, probabilities, acceptances, directions,
scattering, Nanbu-Yonemura rule) and must reproduce the "after" state.

  run_replay.py OUTDIR [--exe ATHENA] [--n 20000] [--nproc 6]

Cases: flat box (analytic metric) with sub-cycling; with coll_cell_factor = 2; with the
velocity-dependent cross-section; with unequal masses (nanbu); the homogeneous curved
metric on the mesh with the symmetric and with the Cholesky triad (Boris pusher).
"""
import argparse
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

DECK_CURVED = os.path.join(common.REPO, "problems", "tests", "coll_box_curved.athinput")
GMAT = np.array([[1.44, 0.3, -0.2], [0.3, 0.81, 0.15], [-0.2, 0.15, 1.21]])
ALPHA0 = 0.7
CYCLE = 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--nproc", type=int, default=6)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, nx, dt = args.n, 8, 0.01
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    theta_eq = collide.mj_theta_from_w(0.5*(collide.mj_mean_w(0.6) + collide.mj_mean_w(0.2)))
    sig = 0.2/dt/float(collide.mj_vmol(theta_eq))      # Gamma dt = 0.2: sub-cycling
    ic_flat = os.path.join(out, "flat.nrp")
    ic_uneq = os.path.join(out, "unequal.nrp")
    ic_curv = os.path.join(out, "curved.nrp")
    common.make_box(ic_flat, "twotemp", n, seed=51, theta=0.6, theta2=0.2)
    common.make_box(ic_uneq, "unequal", n, seed=52, theta=0.6, theta2=0.2, mass_ratio=4.0)
    common.make_box(ic_curv, "twotemp", n, seed=53, theta=0.6, theta2=0.2, gmat=GMAT)
    base = mesh + [f"particles/dt={dt}", f"particles/coll_dump_cycle={CYCLE}",
                   f"time/nlim={CYCLE + 1}", "time/tlim=1.0e9", "particles/snap_dt=1.0e9",
                   "job/rng_seed=77"]
    sg = np.sqrt(np.linalg.det(GMAT))
    cases = {
        "flat_subcycled": (common.DECK_BOX, [f"particles/particle_file={ic_flat}",
                                             f"particles/coll_sigma={sig!r}"]),
        "flat_factor2": (common.DECK_BOX, [f"particles/particle_file={ic_flat}",
                                           f"particles/coll_sigma={sig!r}",
                                           "particles/coll_cell_factor=2"]),
        "flat_conservative": (common.DECK_BOX, [f"particles/particle_file={ic_flat}",
                                                f"particles/coll_sigma={sig!r}",
                                                "particles/coll_subcycle=conservative"]),
        "flat_cutoff": (common.DECK_BOX, [f"particles/particle_file={ic_flat}",
                                          f"particles/coll_sigma={2.0*sig!r}",
                                          "particles/coll_sigma_model=cutoff",
                                          "particles/coll_sigma_w=0.5"]),
        "flat_nanbu": (common.DECK_BOX, [f"particles/particle_file={ic_uneq}",
                                         f"particles/coll_sigma={sig!r}",
                                         "particles/coll_weights=nanbu"]),
        "curved_symmetric": (DECK_CURVED, [f"particles/particle_file={ic_curv}",
                                           f"particles/coll_sigma={sig/ALPHA0!r}",
                                           "particles/triad=symmetric"]),
        "curved_cholesky_boris": (DECK_CURVED, [f"particles/particle_file={ic_curv}",
                                                f"particles/coll_sigma={sig/ALPHA0!r}",
                                                "particles/triad=cholesky",
                                                "particles/pusher=boris"]),
    }
    res = common.run_many([(args.exe, deck, os.path.join(out, k), base + ov)
                           for k, (deck, ov) in cases.items()], args.nproc)
    ok = all(r[0] == 0 for r in res)
    summary = {"n": n, "exe": args.exe, "exe_sha256": common.sha256(args.exe),
               "exit": [r[0] for r in res], "cases": {}}
    errs = {}
    for name in cases:
        rd = os.path.join(out, name)
        d = collide.read_dump(os.path.join(rd, f"box.coll_dump.{CYCLE}.bin"))
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        rec = {k: v[h["ncycle"] == CYCLE + 1][0] for k, v in h.items()}
        u_twin, info = collide.replay(d)
        f = int(d["f"])
        # cell assignment recomputed from the positions (uniform periodic mesh)
        xw = (d["x"] - common.BOX_MIN) % common.BOX_LEN
        cell = np.minimum((xw*nx).astype(np.int64), nx - 1)//f
        scale = np.maximum(1.0, np.max(np.abs(d["u0"]), axis=1))
        err = np.max(np.abs(u_twin - d["u1"]), axis=1)/scale
        untouched = d["nupd"] == 0
        c = dict(particles=int(d["n"]), cell_factor=f,
                 cells_agree=bool(np.array_equal(cell, d["cell"]) and np.all(d["level"] == 0)),
                 nsub_agree=bool(np.array_equal(info["nsub"], d["nsub"])),
                 max_nsub=int(d["nsub"].max()),
                 updates_per_particle_agree=bool(np.array_equal(info["nupd"], d["nupd"])),
                 n_tested=[info["n_tested"], int(rec["n_tested"])],
                 n_coll=[info["n_coll"], int(rec["n_coll"])],
                 n_updated=[info["n_upd"], int(rec["n_updated"])],
                 sum_P_rel_diff=float(abs(info["sum_p"]/rec["sum_P"] - 1.0)),
                 max_P=[info["max_p"], float(rec["max_P"])],
                 max_err_u=float(err.max()),
                 untouched_bit_identical=bool(np.array_equal(d["u0"][untouched],
                                                             d["u1"][untouched])),
                 updated_particles=int(np.count_nonzero(~untouched)),
                 masses_unchanged=True)
        c["pass"] = bool(c["cells_agree"] and c["nsub_agree"]
                         and c["updates_per_particle_agree"]
                         and c["n_tested"][0] == c["n_tested"][1]
                         and c["n_coll"][0] == c["n_coll"][1]
                         and c["n_updated"][0] == c["n_updated"][1]
                         and c["sum_P_rel_diff"] < 1e-11 and c["max_err_u"] < 1e-13
                         and c["untouched_bit_identical"])
        ok = ok and c["pass"]
        summary["cases"][name] = c
        errs[name] = err[~untouched]
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(4.0, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.96)
    cols = fs.series_colors(len(errs))
    bins = np.logspace(-18, -12, 49)
    for col, (name, e) in zip(cols, errs.items()):
        ax.hist(np.maximum(e, 1.2e-18), bins=bins, histtype="step", color=col, lw=1.0,
                label=name.replace("_", " "))
    ax.axvline(1e-13, **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$|u'_{\rm twin} - u'_{\rm code}|$ / max(1, $|u|$)")
    ax.set_ylabel("updated particles")
    ax.legend(fontsize=6, loc="upper left")
    fig.savefig(os.path.join(out, "fig_replay.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
