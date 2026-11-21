#!/usr/bin/env python3
"""T13 of the work package cosmo-amr: the compact-object tracker in mode `walk' (it follows
the minimum of the lapse) with and without <z4c> tracker_walk_tol (prediction:
tracks/core/JOURNAL-cosmo-amr.md).

    t13_walk.py --new NEW_EXE --rel REL_EXE --out DIR [--cores N]

  Wd    homogeneous universe of t2_flrw.py (uniform 24^3, root cell 0.25), tracker at
        (0.1, 0.1, 0.1), tracker_mode = walk, 16 cycles: the first of equal neighbours
        wins
  Wdrel the same with the release
  Wt    Wd with tracker_walk_tol = 1e-6: stays in its cell
  Wp    the peak of t9_peak.py (32^3, cell 0.625, no refinement), tracker at
        (2.5, 1.25, 0.0), walk with tracker_walk_tol = 1e-6, 10 cycles
  Wpn   Wp without the tolerance
  Ex    the example input problems/cosmo_amr/flrw_tracker.athinput, 12 cycles
Writes DIR/t13_summary.json and DIR/fig_t13_walk.{pdf,png}."""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

import amrlib as A
import t2_flrw as T2
import t9_peak as T9


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--ic", default=T9.DEF_IC)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=5)
    a = ap.parse_args()
    a.out, a.new, a.rel = (os.path.abspath(v) for v in (a.out, a.new, a.rel))
    os.makedirs(a.out, exist_ok=True)
    ic1 = os.path.join(a.out, "ic1")
    if not os.path.exists(os.path.join(ic1, "particles.nrp")):
        subprocess.run([sys.executable, os.path.join(A.ROOT, "cosmo/ic/make_lattice.py"),
                        "--n", str(T2.N), "--ppc", "1", "--L", str(T2.L), "--xmin",
                        str(-T2.L/2), "--out", ic1], check=True, stdout=subprocess.DEVNULL)
    cs = {}
    w = T2.base(ic1).set("time", nlim=16, tlim=100.0)
    w.drop("particles", "region_dcycle", "region_radius1")
    w.set("z4c", co_0_type="BH", co_0_x=0.1, co_0_y=0.1, co_0_z=0.1, tracker_mode="walk")
    cs["Wd"] = w
    cs["Wdrel"] = w.copy()
    cs["Wt"] = w.copy().set("z4c", tracker_walk_tol=1e-6)
    p = T9.base(a.ic).drop("particles_amr").drop("mesh_refinement")
    p.drop("amr_criterion0").drop("z4c_amr")
    p.set("time", nlim=10)
    p.set("z4c", co_0_type="BH", co_0_x=2.5, co_0_y=1.25, co_0_z=0.0, tracker_mode="walk",
          tracker_walk_tol=1e-6)
    cs["Wp"] = p
    cs["Wpn"] = p.copy().drop("z4c", "tracker_walk_tol")
    # the example input of the moving tracker, as published, for 12 cycles
    ex = A.Inp(os.path.join(A.ROOT, "problems/cosmo_amr/flrw_tracker.athinput"))
    ex.set("particles", particle_file=os.path.join(ic1, "particles.nrp"))
    ex.set("time", nlim=12)
    cs["Ex"] = ex
    names = list(cs)
    base = {n: ("peak" if n.startswith("Wp") else "flrw") for n in names}
    rcs = A.run_many([((a.rel if n.endswith("rel") else a.new), cs[n],
                       os.path.join(a.out, n), base[n], (), None) for n in names], a.cores)
    res, trk = {}, {}
    for n, rc in zip(names, rcs):
        d = os.path.join(a.out, n)
        f = os.path.join(d, f"{base[n]}.co_0.txt")
        r = dict(exit=rc[0])
        if os.path.exists(f):
            t = np.loadtxt(f, ndmin=2)
            trk[n] = t
            r.update(first=t[0, 2:5].tolist(), last=t[-1, 2:5].tolist(), records=len(t),
                     steps=np.round(np.diff(t[:, 2:5], axis=0), 12).tolist()[:6])
        if n.startswith("Wp"):
            # cell of the smallest lapse at the end, from the history of the module
            pass
        res[n] = r
        print(n, r, flush=True)
    with open(os.path.join(a.out, "t13_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.28)
    cols = fs.SERIES + ["k"]
    for i, n in enumerate([m for m in ("Wd", "Wdrel", "Wt") if m in trk]):
        ax[0].plot(trk[n][:, 1], trk[n][:, 2], "o-" if n != "Wdrel" else "x--", ms=3,
                   color=cols[i], label=f"{n}: x")
    ax[0].set_xlabel("time")
    ax[0].set_ylabel("tracker x (homogeneous universe)")
    ax[0].legend(frameon=False, fontsize=8)
    for i, n in enumerate([m for m in ("Wp", "Wpn") if m in trk]):
        r = np.sqrt(np.sum(trk[n][:, 2:5]**2, axis=1))
        ax[1].plot(trk[n][:, 1], r, "o-", ms=3, color=cols[i], label=n)
    ax[1].axhline(0.625, **fs.GUIDE)
    ax[1].set_xlabel("time")
    ax[1].set_ylabel("tracker distance from the peak centre")
    ax[1].legend(frameon=False, fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_t13_walk"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
