#!/usr/bin/env python3
"""Design input of the package conv_ball (Track A, wave 3): where the matter and the horizon
of a finished collapse run of data set 3 sit in the code's coordinates, so that the static
refinement levels of the convergence series can be placed.

Reads one run directory of AthenaK (BH-1R: run A-20261119-164634-f1fe887, subdirectory
bh_smr) and the prep directory of its lattice (tracked.json, exact.json of prep_bh.py):
  - coordinate radius r = |x| of the tracked particles of each shell group against code time
    (median and range over the 60 particles of a group; <base>.traj.bin),
  - the proper time of each group against the exact trapping time of its shell,
  - the finder's mean and minimum coordinate radius (<base>.horizon_summary_0.txt),
  - the number of particles and the central lapse (<base>.nrpic.hst),
  - memory (gpumem.csv) and cost per cycle (athena.log).
Writes <out>/geometry_numbers.json and <out>/fig_geometry.png (figure style
python/nrpic/figstyle.py). Nothing is evolved here (decision 0010).

    geometry_probe.py --run <run dir> --prep <prep dir>/lat<n> --out <dir> [--label bh_smr]
"""
import argparse
import glob
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--prep", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="bh_smr")
    ap.add_argument("--base", default="ball")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tr = C.load_json(os.path.join(a.prep, "tracked.json"))
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    T = C.read_traj_many([a.run], a.base)
    keep = T["tag"] < tr["n_track"]
    tags = T["tag"][keep]
    x = T["x"][:, keep]
    tau = T["tau"][:, keep]
    t = T["time"]
    r = np.sqrt(np.sum(x * x, axis=-1))
    grp = np.array(tr["group"])[tags]
    tah = np.array(tr["tau_ah"])[tags]
    Ri = np.array(tr["R_i"])[tags]
    res = dict(run=os.path.abspath(a.run), prep=os.path.abspath(a.prep), groups={})
    names = sorted([g for g in set(grp) if g != "sample"], key=lambda s: float(s[1:]))
    for g in names:
        s = grp == g
        rg = r[:, s]
        with np.errstate(invalid="ignore"):
            med = np.nanmedian(rg, axis=1)
            lo, hi = np.nanmin(rg, axis=1), np.nanmax(rg, axis=1)
            dtr = np.nanmedian(tau[:, s] - tah[None, s], axis=1)
        alive = np.isfinite(med)
        pick = [0.0, 4.0, 8.0, 10.0, 10.875, 12.0, 14.0, 16.0]
        rows = {}
        for tq in pick:
            j = int(np.argmin(np.abs(t - tq)))
            if abs(t[j] - tq) < 0.2 and np.isfinite(med[j]):
                rows[f"t{tq:g}"] = dict(t=float(t[j]), r_median=float(med[j]), r_min=float(lo[j]), r_max=float(hi[j]),
                                        tau_minus_tau_ah_median=C.finite_or_none(dtr[j]))
        res["groups"][g] = dict(R_i=float(np.median(Ri[s])), rbar0=float(np.median(np.array(tr["rbar0"])[tags[s]])),
                                tau_ah_exact=float(np.median(tah[s])), r_max_over_run=float(np.nanmax(hi)),
                                t_last_alive=float(t[alive][-1]) if np.any(alive) else None, at=rows)
    # all tracked particles: largest coordinate radius at every time (matter edge)
    with np.errstate(invalid="ignore"):
        rmax_all = np.nanmax(r, axis=1)
    res["r_max_tracked"] = dict(t=t[:: max(1, len(t) // 40)].tolist(), r=rmax_all[:: max(1, len(t) // 40)].tolist(),
                                largest=float(np.nanmax(rmax_all)))
    hz = C.read_horizon([a.run], a.base)
    if len(hz):
        res["finder"] = dict(first_t=float(hz[0, 1]), n=int(len(hz)), mean_radius_first=float(hz[0, 10]),
                             mean_radius_range=[float(hz[:, 10].min()), float(hz[:, 10].max())],
                             min_radius_min=float(hz[:, 11].min()), mass_first=float(hz[0, 2]),
                             mass_last=float(hz[-1, 2]), t_last=float(hz[-1, 1]))
    hst = C.read_hst(os.path.join(a.run, a.base + ".nrpic.hst"))
    res["history"] = dict(n_particles_start=float(hst[0, 2]), n_particles_end=float(hst[-1, 2]),
                          alpha_c_min=float(np.min(hst[:, 12])), t_alpha_c_min=float(hst[int(np.argmin(hst[:, 12])), 0]))
    j = np.nonzero(hst[:, 2] < hst[0, 2])[0]
    res["history"]["t_first_removal"] = float(hst[j[0], 0]) if len(j) else None
    # cost and memory
    logs = sorted(glob.glob(os.path.join(a.run, "athena.*.log")))
    if logs:
        txt = open(logs[-1], errors="replace").read()
        el = [(float(m.group(1)), int(m.group(2))) for m in re.finditer(r"elapsed=([0-9.eE+-]+) cycle=(\d+)", txt)]
        nmb = re.search(r"Total number of MeshBlocks = (\d+)", txt)
        peak = re.search(r"gpu_mem_peak_MiB=(\d+)", txt)
        cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+]+)", txt)
        cyc = re.search(r"time=[0-9.eE+-]+ cycle=(\d+)\s*\ntlim", txt)
        if len(el) > 20:
            e = np.array(el)
            s_per_cycle = float(np.polyfit(e[5:, 1], e[5:, 0], 1)[0])
        else:
            s_per_cycle = None
        res["cost"] = dict(log=logs[-1], meshblocks=int(nmb.group(1)) if nmb else None,
                           gpu_mem_peak_MiB=int(peak.group(1)) if peak else None,
                           cpu_time_s=float(cpu.group(1)) if cpu else None,
                           cycles=int(cyc.group(1)) if cyc else None, s_per_cycle=s_per_cycle)
    C.write_json(os.path.join(a.out, "geometry_numbers.json"), res)

    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.90, wspace=0.28)
    ax = fig.add_subplot(1, 2, 1)
    cols = fs.series_colors(len(names), "viridis") if hasattr(fs, "series_colors") else [None] * len(names)
    for c_, g in zip(cols, names):
        s = grp == g
        with np.errstate(invalid="ignore"):
            med = np.nanmedian(r[:, s], axis=1)
        ax.plot(t, med, color=c_, lw=1.0, label=f"$R_i={float(g[1:]):.2f}$")
    if len(hz):
        ax.plot(hz[:, 1], hz[:, 10], color="k", lw=1.6, label="finder $\\bar r$")
    for yv in (0.5, 1.0, 2.0, 4.0):
        ax.axhline(yv, **fs.GUIDE)
    ax.set_yscale("log")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"coordinate radius $r\,/M$")
    ax.legend(fontsize=5.5, ncol=2, loc="lower left")
    ax.set_title(f"{a.label}: shells in coordinates (median of 60)", fontsize=9)
    ax = fig.add_subplot(1, 2, 2)
    for c_, g in zip(cols, names):
        s = grp == g
        with np.errstate(invalid="ignore"):
            d = np.nanmedian(tau[:, s] - tah[None, s], axis=1)
        ax.plot(t, d, color=c_, lw=1.0)
    ax.axhline(0.0, **fs.GUIDE)
    if len(hz):
        ax.axvline(hz[0, 1], **fs.MASK_LINE)
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"$\tau - \tau_{\rm AH}^{\rm exact}$ of the shell $/M$")
    ax.set_ylim(-12, 4)
    ax.set_title("proper time against own trapping time (line: finder)", fontsize=9)
    fs.save(fig, os.path.join(a.out, "fig_geometry"))
    print(C.json.dumps({k: v for k, v in res.items() if k != "groups"}, indent=1, default=str)[:3000])
    for g, d in res["groups"].items():
        print(g, "rbar0", round(d["rbar0"], 3), "r_max", round(d["r_max_over_run"], 3),
              {k: (round(v["r_median"], 3), v["tau_minus_tau_ah_median"] and round(v["tau_minus_tau_ah_median"], 3))
               for k, v in d["at"].items()})


if __name__ == "__main__":
    main()
