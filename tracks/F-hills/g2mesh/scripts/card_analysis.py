#!/usr/bin/env python3
"""G2M-3 of g2mesh: analysis of the card batch job of G2M-2 (run F-20261120-222810-e408386).

For each case directory <card run>/<name>/ (the latest athena.<ts>.log and its .gpumem.csv,
written by scripts/_athena_job.sh): exit status, slots (max_nmb_per_rank of the command line),
block size, MeshBlocks at the start and at the end, MeshBlock-cycles, cpu time of the main
loop, zone-cycles/s, set-up time (elapsed at cycle 0), peak card memory, the memory plateau
after allocation, and the error lines of a failed start.

Memory per slot: a 16^3 slot from the measured case against E7's point (2700 slots,
70847 MiB) when both are 16^3; any slot as (peak - F) / slots with the fixed part
F = 70847 - 2700 x 25.65 = 1592.5 MiB (E7 and core's slope, core_requests-adf READY MEMORY)
[JUDGEMENT: the fixed part does not depend on the block size]. Slot limit of one card:
(81920 - F - reserve) / (MiB per slot), reserve 1024 MiB [JUDGEMENT].
Rates: MeshBlock-cycles per second and zone-cycles per second (cells of a block x the former);
problem time per wall hour = dt x cycles / cpu time x 3600.
Usage: card_analysis.py <card run dir> <out dir>
Writes <out>/card_analysis.json (key 'slot_limit' is read by fig_blocks_time.py).
"""
import glob
import json
import os
import re
import sys

import numpy as np

CARD_MIB = 81920.0
E7 = dict(slots=2700, peak=70847.0, rate=2057.0, block=16, src="E7, run F-20261115-174602-c6879fe")
CORE_SLOPE = 25.65
FIXED = E7["peak"] - E7["slots"] * CORE_SLOPE
RESERVE = 1024.0


def arg(cmd, key, default=None):
    m = re.search(r"(?:^|\s)" + re.escape(key) + r"=(\S+)", cmd)
    return m.group(1) if m else default


def read_case(d):
    logs = sorted(glob.glob(os.path.join(d, "athena.*.log")))
    if not logs:
        return None
    lg = logs[-1]
    s = open(lg, errors="replace").read()
    cmd = re.search(r"^# cmd: (.*)$", s, re.M).group(1)
    r = dict(dir=d, log=os.path.basename(lg), cmd=cmd)
    m = re.search(r"# exit=(\d+)", s)
    r["exit"] = int(m.group(1)) if m else None
    m = re.search(r"gpu_mem_peak_MiB=(\d+)", s)
    r["peak_MiB"] = float(m.group(1)) if m else None
    r["slots"] = int(float(arg(cmd, "mesh_refinement/max_nmb_per_rank", "nan"))) \
        if arg(cmd, "mesh_refinement/max_nmb_per_rank") else None
    r["block"] = int(arg(cmd, "meshblock/nx1", "16"))
    r["num_levels"] = arg(cmd, "mesh_refinement/num_levels")
    m = re.search(r"Total number of MeshBlocks = (\d+)", s)
    r["n_start"] = int(m.group(1)) if m else None
    m = re.search(r"Current number of MeshBlocks = (\d+)", s)
    r["n_end"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+) MeshBlocks created, (\d+) deleted", s)
    r["created_deleted"] = [int(m.group(1)), int(m.group(2))] if m else None
    m = re.search(r"MeshBlock-cycles = (\d+)", s)
    r["mb_cycles"] = int(m.group(1)) if m else None
    m = re.search(r"cpu time used\s*=\s*([0-9.e+-]+)", s)
    r["cpu_s"] = float(m.group(1)) if m else None
    m = re.search(r"zone-cycles/cpu_second = ([0-9.e+-]+)", s)
    r["zone_cycles_per_s_log"] = float(m.group(1)) if m else None
    m = re.search(r"elapsed=([0-9.e+-]+) cycle=0 ", s)
    r["setup_s"] = float(m.group(1)) if m else None
    m = re.search(r"cycle=\d+ time=[0-9.e+-]+ dt=([0-9.e+-]+)", s)
    r["dt"] = float(m.group(1)) if m else None
    m = re.search(r"time=([0-9.e+-]+) cycle=(\d+)\s*\n\s*tlim", s)
    r["cycles"] = int(m.group(2)) if m else None
    r["errors"] = [ln.strip() for ln in s.splitlines()
                   if re.search(r"FATAL|rror|emory|Abort|terminate|exceed", ln)][:12]
    gm = lg[:-4] + ".gpumem.csv"
    if os.path.exists(gm):
        a = []
        for ln in open(gm):
            if ln.startswith("#"):
                continue
            p = [q.strip() for q in ln.split(",")]
            try:
                a.append((float(p[1]), float(p[2])))
            except (ValueError, IndexError):
                pass
        a = np.array(a) if a else np.zeros((0, 2))
        if len(a):
            r["mem_series_MiB"] = a[:, 0].tolist()
            r["mem_median_after_peak_MiB"] = float(np.median(a[np.argmax(a[:, 0]):, 0]))
            r["util_median"] = float(np.median(a[:, 1]))
    ok = r["exit"] == 0 and r["mb_cycles"]
    if ok:
        r["rate_mb_cycles_per_s"] = r["mb_cycles"] / r["cpu_s"]
        r["rate_zone_cycles_per_s"] = r["rate_mb_cycles_per_s"] * r["block"] ** 3
        r["mean_nmb"] = r["mb_cycles"] / r["cycles"] if r["cycles"] else None
        r["s_per_cycle"] = r["cpu_s"] / r["cycles"] if r["cycles"] else None
        r["M_per_wall_hour"] = r["dt"] * r["cycles"] / r["cpu_s"] * 3600 if r["dt"] else None
    if r["peak_MiB"] and r["slots"]:
        r["MiB_per_slot_fixed_removed"] = (r["peak_MiB"] - FIXED) / r["slots"]
        r["MiB_per_slot_total"] = r["peak_MiB"] / r["slots"]
    return r


def main():
    run, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    cases = {}
    for d in sorted(glob.glob(os.path.join(run, "*", ""))):
        r = read_case(d.rstrip("/"))
        if r:
            cases[os.path.basename(d.rstrip("/"))] = r
    res = dict(run=run, e7=E7, core_slope_MiB=CORE_SLOPE, fixed_MiB=FIXED, reserve_MiB=RESERVE,
               card_MiB=CARD_MIB, cases=cases)
    status = os.path.join(run, "batch.list.status")
    if os.path.exists(status):
        res["status_lines"] = open(status).read().splitlines()
    # memory per slot by block size
    per = {16: CORE_SLOPE, 32: None}
    src = {16: "core's slope (assumed)", 32: "none measured"}
    for name, r in cases.items():
        if not r.get("peak_MiB") or not r.get("slots") or r["exit"] != 0:
            continue
        if r["block"] == 16 and r["slots"] != E7["slots"]:
            per[16] = (r["peak_MiB"] - E7["peak"]) / (r["slots"] - E7["slots"])
            src[16] = f"{name} against E7"
        if r["block"] == 32:
            per[32] = r["MiB_per_slot_fixed_removed"]
            src[32] = f"{name}, fixed part {FIXED:.0f} MiB removed"
    res["MiB_per_slot"] = {str(k): v for k, v in per.items()}
    res["MiB_per_slot_source"] = {str(k): v for k, v in src.items()}
    res["slot_limit"] = {str(k): (CARD_MIB - FIXED - RESERVE) / v for k, v in per.items() if v}
    res["slot_limit_no_reserve"] = {str(k): (CARD_MIB - FIXED) / v for k, v in per.items() if v}
    for name, r in cases.items():
        print("%-15s exit %s slots %s block %d start %s end %s peak %s MiB  rate %s MB-c/s  %s z-c/s  %s M/h  setup %s s"
              % (name, r["exit"], r["slots"], r["block"], r["n_start"], r["n_end"], r["peak_MiB"],
                 "%.0f" % r["rate_mb_cycles_per_s"] if r.get("rate_mb_cycles_per_s") else "-",
                 "%.3g" % r["rate_zone_cycles_per_s"] if r.get("rate_zone_cycles_per_s") else "-",
                 "%.3f" % r["M_per_wall_hour"] if r.get("M_per_wall_hour") else "-", r["setup_s"]))
        if r["exit"] != 0:
            print("   errors:", r["errors"][:5])
    print("MiB per slot:", res["MiB_per_slot"], res["MiB_per_slot_source"])
    print("slot limit (1 GiB reserve):", res["slot_limit"], "no reserve:", res["slot_limit_no_reserve"])
    json.dump(res, open(os.path.join(out, "card_analysis.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
