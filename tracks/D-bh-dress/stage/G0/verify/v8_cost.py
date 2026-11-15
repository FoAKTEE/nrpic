#!/usr/bin/env python3
"""Verifier check C8: the compute estimate of SCOPE.md section 7 against what the D-pre-4
card runs used, with the anchors re-read from the logs by my own parser, and the
throughput formula re-evaluated by my own code:

  card-seconds = blocks * 4096 * cycles / R + N * cycles * c_p,  cycles = T / (0.25 dx_min)

Anchors: runs/puncture/hcal/{dx4,dx8_tight,dx16}/athena.log (main checkout, untracked):
MeshBlock-cycles, cpu time, tlim 60 M. Measured D-pre-4: manifests of
D-bh-dress-20261115-121313-284ec4f (M/8) and -121314- (M/16).
Also the blocks of the finest level against the horizon's coordinate radius
(D-pre-4 finder output), for the resolutions M/16, M/32, M/64 of the plan.

Usage: v8_cost.py [--out DIR]
"""
import argparse
import json
import math
import os
import re

import numpy as np

RUNS = "/data/haiyangw/nrpic/runs/puncture/hcal"
TRK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"


def parse(p):
    s = open(p).read()
    bc = float(re.findall(r"MeshBlock-cycles = (\S+)", s)[-1])
    cpu = float(re.findall(r"cpu time used\s*=\s*(\S+)", s)[-1])
    zc = float(re.findall(r"zone-cycles/cpu_second = (\S+)", s)[-1])
    return bc, cpu, zc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"anchors": {}}
    for name, dx in (("dx4", 0.25), ("dx8_tight", 0.125), ("dx16", 0.0625)):
        bc, cpu, zc = parse(os.path.join(RUNS, name, "athena.log"))
        cyc = 60.0 / (0.25 * dx)
        res["anchors"][name] = {"dx": dx, "block_cycles": bc, "cpu_s": cpu, "blocks": bc / cyc,
                                "s_per_M": cpu / 60.0, "zone_cycles_per_s": zc}
    R = float(np.mean([v["zone_cycles_per_s"] for v in res["anchors"].values()]))
    res["R_smr_mean"] = R
    meas = {}
    for name, rid in (("M/8", "D-bh-dress-20261115-121313-284ec4f"), ("M/16", "D-bh-dress-20261115-121314-284ec4f")):
        m = json.load(open(os.path.join(TRK, "runs", rid, "manifest.json")))
        meas[name] = {"card_hours": m["resources"]["card_hours"], "walltime_s": m["resources"]["walltime_s"],
                      "exe": m["command"][1]}
    res["measured"] = meas

    def blocks(dx, grow_to=None):
        nb = 288.0 + 56.0 * math.log2(0.25 / dx)
        if grow_to:
            nb += 56.0 * math.ceil(max(0.0, math.log2(grow_to / 128.0)))
        return nb

    pred = {}
    for name, dx in (("M/8", 0.125), ("M/16", 0.0625)):
        T = 500.0
        cyc = T / (0.25 * dx)
        for tag, L in (("domain_128", None), ("domain_grown_0.71T", 0.71 * T)):
            nb = blocks(dx, L)
            w = nb * 4096 * cyc / R
            pred.setdefault(name, {})[tag] = {"blocks": nb, "card_hours": w / 3600.0,
                                              "measured_over_model": meas[name]["card_hours"] / (w / 3600.0)}
        # the simplest predictor: the anchor's seconds per M times T
        an = res["anchors"]["dx8_tight" if name == "M/8" else "dx16"]
        pred[name]["anchor_s_per_M_times_T_h"] = an["s_per_M"] * T / 3600.0
    res["predicted_D_pre_4"] = pred
    # G2 vacuum bubble, eps = 0.03, a x 2, M/16, 1e6 particles, rates of SCOPE.md 7
    eps, af, dx = 0.03, 2.0, 0.0625
    T = (2 / (3 * eps)) * (af ** 1.5 - 1)
    cyc = T / (0.25 * dx)
    R_amr, c_p = 6.4e6, 1.2e-7
    nb = blocks(dx)
    res["G2_bubble_eps0.03_M16"] = {"T": T, "cycles": cyc, "blocks": nb,
                                     "mesh_h": nb * 4096 * cyc / R_amr / 3600, "particles_h": 1e6 * cyc * c_p / 3600,
                                     "total_h": (nb * 4096 * cyc / R_amr + 1e6 * cyc * c_p) / 3600}
    # finest level extent against the horizon's coordinate radius
    hs = np.loadtxt(os.path.join(SCR, "D-bh-dress-20261115-121314-284ec4f", "punc.horizon_summary_0.txt"))
    t, rmean = hs[:, 1], hs[:, 10]
    ext = {}
    for inv in (16, 32, 64):
        bw = 16.0 / inv                       # block width in M
        edge = math.ceil(1.5 / bw - 1e-12) * bw  # blocks overlapping |x| < 1.5 M
        tcross = t[np.argmax(rmean > edge)] if np.any(rmean > edge) else None
        ext[f"M/{inv}"] = {"block_width": bw, "finest_edge_on_axis": edge,
                           "horizon_rmean_max": float(rmean.max()),
                           "t_horizon_reaches_edge": None if tcross is None else float(tcross),
                           "margin_cells_at_t500": (edge - float(rmean[-1])) * inv}
    res["finest_level_vs_horizon"] = ext
    with open(os.path.join(a.out, "v8_cost.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
