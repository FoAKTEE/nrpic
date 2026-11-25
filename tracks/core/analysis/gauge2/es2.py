#!/usr/bin/env python3
"""Tests ES and L3 of the gauge package with the candidates of the second pass (source item
gauge-2): Track D's Einstein-Straus data for 100 M and the collapse of the bound ball,
analysed with the functions of the first pass (tracks/core/analysis/gauge/
es_collapse_analysis.py) and compared with its numbers.

    es2.py --out DIR [--es NAME=RUNDIR ...] [--collapse NAME=RUNDIR ...]
           [--ref NAME=HORIZON_SUMMARY ...]

The exact curves of the Einstein-Straus data are read from the copy of the data with the
reference to tau = 140 M (run core-20261121-180109-bcbd0d2; table and particles are
byte-identical with the first pass, whose reference ended at 60 M).  Writes
DIR/es2_numbers.json, DIR/es_g2_<name>.png|pdf (four panels of the first pass),
DIR/es2_horizon.png|pdf (radius and mass of the horizons of all runs, with --ref drawn
thin), DIR/collapse_g2_<name>.png|pdf.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/gauge"))
sys.path.insert(0, HERE)

import es_collapse_analysis as eca             # noqa: E402
from vanalysis import horizon, at              # noqa: E402
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

ESIC = "/data/haiyangw/nrpic/scratch/core/core-20261121-180109-bcbd0d2"
BALLIC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball/t2_bound_h0p25.json"


def horizon_numbers(h, windows=((40.0, 100.0), (10.0, 100.0))):
    rec = dict(t_first=float(h[0, 0]), t_last=float(h[-1, 0]), searches=int(len(h)),
               at={f"{t:g}": dict(mass=at(h, t, 1), radius=at(h, t, 2))
                   for t in (10.0, 25.0, 50.0, 75.0, 100.0) if at(h, t, 1) is not None})
    for lo, hi in windows:
        w = (h[:, 0] >= lo) & (h[:, 0] <= hi)
        if w.sum() > 3 and h[-1, 0] >= hi - 1.5:
            rec[f"mass_spread_{lo:g}_{hi:g}"] = float(h[w, 1].max() - h[w, 1].min())
            rec[f"mass_min_{lo:g}_{hi:g}"] = float(h[w, 1].min())
            rec[f"mass_max_{lo:g}_{hi:g}"] = float(h[w, 1].max())
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--es", action="append", default=[])
    ap.add_argument("--collapse", action="append", default=[])
    ap.add_argument("--ref", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    eca.FIGS = a.out
    fs.use_style()
    res = dict(es={}, collapse={})
    hz = {}
    for spec in a.es:
        name, rundir = spec.split("=", 1)
        man = dict(output_directory=rundir, run_id=name, command=[], wall_time_s=None,
                   card_hours=None, inputs=[dict(path=os.path.join(ESIC, "es.json"))])
        r = eca.analyse_es("g2", name, man)
        h = horizon(os.path.join(rundir, "es.horizon_summary_0.txt"))
        hz[name] = h
        r["horizon2"] = horizon_numbers(h)
        res["es"][name] = r
        g = r["groups"]
        print(f"\n{name}: T = {r['T']:g} M, to t = {r['t_end']:g} M; particles {r['np_start']} -> "
              f"{r['np_end']}, removed {r['n_excised']}")
        print("   tracer groups, largest |R/R_exact - 1| until the end (tau_end): "
              + ", ".join(f"R0={k}: {v['maxabs_eps']:.2e} ({v['tau_end']:.0f})"
                          for k, v in g.items()))
        if "plateau" in r:
            print(f"   lapse at the dust tracers (48 M) within {r['plateau']['max_dev']:.3f} of the "
                  f"homogeneous model; largest lapse on the mesh {r['alpha_max']:.3f}; "
                  f"smallest lapse at the end {r['alpha_min_end']:.3f}")
        if "dust" in r:
            print(f"   dust: smallest coordinate radius {r['dust']['r_coord_min']:.2f} at "
                  f"t = {r['dust']['snapshot_time']:g}; wall tracers at coordinate radius "
                  f"{g['36']['r_coord_end_min']:.2f} to mean {g['36']['r_coord_end_mean']:.2f}")
        h2 = r["horizon2"]
        print("   horizon (t: mass, radius): " + "; ".join(
            f"{t}: {v['mass']:.6f}, {v['radius']:.3f}" for t, v in h2["at"].items()))
        for k in h2:
            if k.startswith("mass_spread"):
                print(f"   {k}: {h2[k]:.2e}")
    for spec in a.collapse:
        name, rundir = spec.split("=", 1)
        man = dict(output_directory=rundir, run_id=name, command=[], wall_time_s=None,
                   card_hours=None, inputs=[dict(path=BALLIC)])
        r = eca.analyse_collapse("g2", name, man)
        r.pop("history", None)
        res["collapse"][name] = r
        print(f"\n{name}:")
        print(json.dumps({k: v for k, v in r.items() if not isinstance(v, (list,))}, indent=1)[:3000])

    if hz:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.3)
        cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
        for (name, h), c in zip(hz.items(), cols):
            ax[0].plot(h[:, 0], h[:, 2], color=c, label=name)
            ax[1].plot(h[:, 0], h[:, 1] - 1.0, color=c)
        for spec, ls in zip(a.ref, (":", "--", "-.")):
            name, path = spec.split("=", 1)
            h = horizon(path)
            h = h[h[:, 0] <= max(v[-1, 0] for v in hz.values()) + 1.0]
            ax[0].plot(h[:, 0], h[:, 2], color="0.45", lw=0.9, ls=ls, label=name)
            ax[1].plot(h[:, 0], h[:, 1] - 1.0, color="0.45", lw=0.9, ls=ls)
        ax[0].set_ylabel(r"horizon radius (coordinate) $/M$")
        ax[1].set_ylabel(r"horizon mass $M_{\rm AH}/M-1$")
        ax[1].set_ylim(-1.0e-3, 2.5e-3)
        for k in (0, 1):
            ax[k].set_xlabel(r"coordinate time $t/M$", labelpad=1)
        ax[0].legend(fontsize=6.5)
        fs.save(fig, os.path.join(a.out, "es2_horizon"))
        plt.close(fig)
    with open(os.path.join(a.out, "es2_numbers.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
