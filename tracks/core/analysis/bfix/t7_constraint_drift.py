#!/usr/bin/env python3
"""T7: does the constraint level that the evolution restores depend on the time step?
(prediction P8 of tracks/core/JOURNAL-bfix.md). Initial data plane4_fd and jit4_fd of
T3 (constraints solved with the code's differences), run to t = 0.3 with two steps.

    python3 t7_constraint_drift.py --exe EXE --t3-dir DIR [--out DIR]
"""
import argparse
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs  # noqa: E402
import t3_thin_jitter as t3  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--t3-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    with open(os.path.join(a.t3_dir, "results_t3.json")) as f:
        dirs = json.load(f)["ic_dirs"]
    with open(os.path.join(bc.REPO, "problems", "cosmo", "east.athinput")) as f:
        txt = f.read()
    inp = os.path.join(out, "drift.athinput")
    with open(inp, "w") as f:
        f.write(txt.replace("dt        = 0.1", "dt        = 0.02"))
    d = t3.DEP
    jobs = {}
    for name in ("plane4_fd", "jit4_fd"):
        info = json.load(open(os.path.join(dirs[name], "id.json")))
        n, box = info["n"], info["box"]
        for dte in ("0.01", "0.0025"):
            rd = os.path.join(out, f"{name}_dt{dte}")
            os.makedirs(rd, exist_ok=True)
            for fn in ("particles.nrp", "fields.bin"):
                if not os.path.exists(os.path.join(rd, fn)):
                    os.symlink(os.path.join(dirs[name], fn), os.path.join(rd, fn))
            ov = [f"mesh/nx{i+1}={n[i]}" for i in range(3)] \
                + [f"mesh/x{i+1}max={box[i]!r}" for i in range(3)] \
                + [f"meshblock/nx{i+1}={min(8, n[i])}" for i in range(3)] \
                + ["time/tlim=0.3", "z4c/damp_kappa1=0.5", "z4c/damp_kappa1_over_alpha=true",
                   "particles/deposit_shape=pcs", f"particles/deposit_comp_c={d['dep_comp_c']!r}",
                   f"particles/deposit_comp_c2={d['dep_comp_c2']!r}",
                   "particles/interp=bspline", f"particles/dt_expansion={dte}",
                   "particles/nfilter=0", "particles/filter_compensate=false",
                   "particles/snap_dt=1.0", f"particles/traj_ntrack={info['n_fiducial']}"] \
                + [f"particles/probe_x{i+1}={info['overdensity_point'][i]!r}" for i in range(3)] \
                + [f"particles/probe1_x{i+1}={info['underdensity_point'][i]!r}"
                   for i in range(3)]
            jobs[f"{name}_dt{dte}"] = (os.path.abspath(a.exe), inp, rd, ov)
    recs = bc.run_many(jobs, 4)
    res = {"meta": {"exe": os.path.abspath(a.exe), "commit": bc.git_rev(), "t3_dir": a.t3_dir}}
    for name, rec in recs.items():
        _, h = bc.read_hst(glob.glob(os.path.join(rec["rundir"], "*.z4c.user.hst"))[0])
        ok = h[:, 10] > 0
        res[name] = {"t": h[ok, 0].tolist(), "dt": h[ok, 1].tolist(),
                     "H_rms": np.sqrt(h[ok, 3]/h[ok, 10]).tolist(),
                     "M_rms": np.sqrt(h[ok, 4]/h[ok, 10]).tolist()}
    summ = {}
    for lat in ("plane4_fd", "jit4_fd"):
        a1, a2 = res[f"{lat}_dt0.01"], res[f"{lat}_dt0.0025"]
        row = {}
        for tq in (0.02, 0.04, 0.1, 0.2, 0.3):
            i1 = int(np.argmin(np.abs(np.array(a1["t"]) - tq)))
            i2 = int(np.argmin(np.abs(np.array(a2["t"]) - tq)))
            row[str(tq)] = {"t": [a1["t"][i1], a2["t"][i2]],
                            "H_rms": [a1["H_rms"][i1], a2["H_rms"][i2]],
                            "ratio_small_over_large_step": a2["H_rms"][i2]/a1["H_rms"][i1],
                            "M_rms": [a1["M_rms"][i1], a2["M_rms"][i2]]}
        summ[lat] = row
        print(lat, json.dumps(row))
    res["summary"] = summ
    bc.save_json(res, os.path.join(out, "results_t7.json"))
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 0.6, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.95)
    for lat, col in (("plane4_fd", fs.PAL["blue"]), ("jit4_fd", fs.PAL["red"])):
        for dte, ls in (("0.01", "-"), ("0.0025", "--")):
            r = res[f"{lat}_dt{dte}"]
            ax.semilogy(r["t"], r["H_rms"], color=col, ls=ls,
                        label=f"{'plain' if lat == 'plane4_fd' else 'jittered'} lattice, "
                              f"dt_expansion = {dte}")
    ax.set_xlabel("conformal time")
    ax.set_ylabel("rms of H")
    ax.set_ylim(1e-9, 1e2)
    ax.legend(loc="upper right", fontsize=7)
    print("figures:", fs.save(fig, os.path.join(out, "t7_constraint_drift")))


if __name__ == "__main__":
    main()
