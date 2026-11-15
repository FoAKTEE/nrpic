#!/usr/bin/env python3
"""Analysis of the card runs of inputs/card_T2.list: cost per collision pair on one A100
and T10b (processor and card statistics of T2 agree within 4 sigma; not bitwise).

    python3 card.py CARD_RUN_DIR CPU_RUN_DIR [--tag gpu]

CARD_RUN_DIR: scratch/C-sidm/<card run id> (one sub-directory per list entry);
CPU_RUN_DIR: the processor T2 run (same particle files, overrides and seeds).
Per-step times from the `elapsed=` lines AthenaK prints every 100 cycles (start-up
excluded); processor per-step times from the same lines of the processor runs.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

import boxlib as bl
import t1t2

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def elapsed(rd):
    txt = open(os.path.join(rd, "athena.log"), errors="replace").read()
    pts = [(int(c), float(e)) for e, c in re.findall(r"elapsed=([0-9.eE+-]+) cycle=(\d+)", txt)]
    return dict(pts)


def per_step(rd, c0=100, c1=None):
    e = elapsed(rd)
    c1 = max(e) if c1 is None else c1
    return (e[c1] - e[c0]) / (c1 - c0), e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card")
    ap.add_argument("cpu")
    ap.add_argument("--tag", default="gpu")
    a = ap.parse_args()
    out = bl.outdir()
    res = {}
    for name in sorted(os.listdir(a.card)):
        rd = os.path.join(a.card, name)
        if not os.path.isdir(rd) or not name.startswith("c_"):
            continue
        th = name.split("_")[1][2:]
        var = name.split("_")[2]
        cpu_name = f"T2_th{th}_{var}_s1"
        cpu_rd = os.path.join(a.cpu, cpu_name)
        meta = json.load(open(os.path.join(cpu_rd, "box.json")))
        r = dict(name=name, theta=th, var=var)
        try:
            r["sec_per_step"], e = per_step(rd)
            r["last_cycle"] = max(e)
            r["startup_s"] = e.get(0, float("nan"))
            r["total_elapsed_s"] = e[max(e)]
        except Exception as ex:      # noqa: BLE001
            r["error"] = repr(ex)
            res[name] = r
            continue
        if var != "off":
            h = bl.coll_history(rd)
            r["tested_per_step"] = float(h["n_tested"].mean())
            r["collisions"] = float(h["n_coll"].sum())
            r["mean_nsub"] = float(h["mean_nsub"].mean())
        if not name.endswith("long") and var != "off":
            an = t1t2.analyse(rd, meta, 200)
            hc = bl.coll_history(cpu_rd)
            r.update({k: an[k] for k in ("T2a_z", "T2a_pass", "T2b_z", "T2b_pass", "T2c_z",
                                         "T2c_pass", "T1_step_pass", "ratio_b", "max_P",
                                         "n_trunc", "exact_dE_rel")})
            n_card, n_cpu = h["n_coll"].sum(), hc["n_coll"].sum()
            r["T10b_z_collisions"] = float((n_card - n_cpu) / np.sqrt(n_card + n_cpu))
            r["collisions_identical_per_step"] = bool(np.array_equal(h["n_coll"], hc["n_coll"]))
            r["tested_identical_per_step"] = bool(np.array_equal(h["n_tested"], hc["n_tested"]))
            r["sumP_max_rel_diff"] = float(np.max(np.abs(h["sum_P"] / hc["sum_P"] - 1)))
            s_card = bl.snap.read_snapshot(bl.snapshots(rd)[-1])
            s_cpu = bl.snap.read_snapshot(bl.snapshots(cpu_rd)[-1])
            r["final_max_du"] = float(np.abs(s_card["u"] - s_cpu["u"]).max())
            r["final_bit_identical"] = bool(np.array_equal(s_card["u"], s_cpu["u"]))
            r["T10b_pass"] = bool(abs(r["T10b_z_collisions"]) < 4 and an["T2a_pass"] and
                                  an["T2b_pass"] and an["T2c_pass"])
            r["cpu_sec_per_step"], _ = per_step(cpu_rd)
        res[name] = r
    # cost per pair: (with - without collisions) per step / tested pairs per step
    for name, r in res.items():
        if r.get("var") in ("plain", "sub") and "sec_per_step" in r:
            off = res.get("c_th0.1_off_long" if name.endswith("long") else "c_th0.1_off_s1")
            if off and "sec_per_step" in off:
                r["card_cost_per_tested_pair_s"] = (r["sec_per_step"] - off["sec_per_step"]) / \
                    r["tested_per_step"]
                r["card_cost_per_particle_step_s"] = (r["sec_per_step"] - off["sec_per_step"]) / 1e6
            if "cpu_sec_per_step" in r:
                off_cpu, _ = per_step(os.path.join(a.cpu, "T2_th0.1_off_s1")) \
                    if r["theta"] == "0.1" else per_step(os.path.join(a.cpu, "T2_th10.0_off_s1"))
                r["cpu_cost_per_tested_pair_s"] = (r["cpu_sec_per_step"] - off_cpu) / \
                    r["tested_per_step"]
                r["speedup_collision_part"] = r["cpu_cost_per_tested_pair_s"] / \
                    r["card_cost_per_tested_pair_s"]
    bl.save_json(os.path.join(out, f"card_{a.tag}.json"), res)
    print(json.dumps(res, indent=1, default=float))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 3.3))
    ax = fig.add_axes([0.2, 0.15, 0.76, 0.78])
    names = [n for n in res if "card_cost_per_tested_pair_s" in res[n]]
    ax.plot(range(len(names)), [res[n]["card_cost_per_tested_pair_s"] for n in names], "o",
            color=fs.PAL["red"], label="card (A100)")
    ax.plot(range(len(names)), [res[n].get("cpu_cost_per_tested_pair_s", np.nan) for n in names],
            "s", color=fs.PAL["blue"], label="processor (1 core)")
    ax.set_yscale("log")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n[2:].replace("_", "\n") for n in names], fontsize=6)
    ax.set_ylabel("seconds per tested pair")
    ax.legend(loc="center right", fontsize=7)
    fs.save(fig, os.path.join(out, f"cost_{a.tag}"))
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
