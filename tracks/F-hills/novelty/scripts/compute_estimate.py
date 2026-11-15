#!/usr/bin/env python3
"""Measured cost of this repository's black-hole runs, and the cost of the Hills runs.

Usage: python3 -I compute_estimate.py <outdir> <repo_root> <scale_results.json>

Reads (read-only):
  runs/jeans/n1e4_v19/chain/seg*.log, events.log   two black holes in a cluster, M/64
                                                   (notes/results_brief_selfgravity.md D)
  runs/puncture/{headon_v4,single_v3,hcal/dx16,hcal/dx8_fixed}/athena.*.log   vacuum
  scratch/core/core-20261115-120834-d08c476/athena.log   three punctures, q = 10 (core)
  runs/cosmo/dav_c704_n64_k/athena.20261114-033334.log   particle push rate
Cost model (AthenaK has one global time step, dt = cfl * min cell width over all
MeshBlocks: athenak/src/mesh/mesh.cpp 595-666, z4c/z4c_newdt.cpp 45-58):
  card-seconds = N_MB * (T / (cfl * h_min)) / R,   R = MeshBlock-cycles per second.
Writes results.json, fig_cost.png/pdf to <outdir>.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime

import numpy as np

OUT, ROOT, SCALE = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

os.makedirs(OUT, exist_ok=True)
RES = {}


def parse_log(path):
    t = open(path, errors="replace").read()
    g = lambda pat: (re.search(pat, t).group(1) if re.search(pat, t) else None)  # noqa: E731
    cyc = re.findall(r"elapsed=([0-9.e+-]+) cycle=(\d+) time=([0-9.e+-]+) dt=([0-9.e+-]+)", t)
    d = {"path": path,
         "mb_cycles": int(g(r"MeshBlock-cycles = (\d+)")) if g(r"MeshBlock-cycles = (\d+)") else None,
         "cpu_s": float(g(r"cpu time used  = ([0-9.e+-]+)")) if g(r"cpu time used  = ([0-9.e+-]+)") else None,
         "zcps": float(g(r"zone-cycles/cpu_second = ([0-9.e+-]+)")) if g(r"zone-cycles/cpu_second = ([0-9.e+-]+)") else None,
         "pups": float(g(r"particle-updates/cpu_second = ([0-9.e+-]+)")) if g(r"particle-updates/cpu_second = ([0-9.e+-]+)") else None,
         "nmb_start": int(g(r"Total number of MeshBlocks = (\d+)")) if g(r"Total number of MeshBlocks = (\d+)") else None,
         "nmb_end": int(g(r"Current number of MeshBlocks = (\d+)")) if g(r"Current number of MeshBlocks = (\d+)") else None,
         "levels": (int(re.findall(r"Number of physical levels of refinement = \d+ \((\d+) levels total\)", t)[0])
                    if re.findall(r"Number of physical levels of refinement = \d+ \((\d+) levels total\)", t) else None),
         "peak_mem_MiB": int(g(r"gpu_mem_peak_MiB=(\d+)")) if g(r"gpu_mem_peak_MiB=(\d+)") else None}
    if cyc:
        d["t_first"], d["t_last"] = float(cyc[0][2]), float(cyc[-1][2])
        d["dt"] = float(cyc[-1][3])
        d["cycles_seen"] = int(cyc[-1][1]) - int(cyc[0][1])
    if d["mb_cycles"] and d["cpu_s"]:
        d["R_mbcyc_per_s"] = d["mb_cycles"] / d["cpu_s"]
    return d


# ------------------------------------------------------------ two black holes in a cluster
v19 = os.path.join(ROOT, "runs/jeans/n1e4_v19/chain")
segs = [parse_log(p) for p in sorted(glob.glob(os.path.join(v19, "seg*.log")))]
ev = open(os.path.join(v19, "events.log")).read().splitlines()
t0 = datetime.strptime(ev[0][:19], "%Y-%m-%d %H:%M:%S")
end_line = [l for l in open(os.path.join(v19, "latest.log")).read().splitlines() if l.startswith("# exit")]
t1 = datetime.strptime(re.search(r"end=(\S+?)-0\d:00", end_line[-1]).group(1), "%Y-%m-%dT%H:%M:%S")
cpu_total = sum(s["cpu_s"] for s in segs)
RES["v19"] = {"segments": len(segs), "cpu_s_total": cpu_total, "card_hours_compute": cpu_total / 3600,
              "wall_start": str(t0), "wall_end": str(t1),
              "card_hours_wall_including_queue": (t1 - t0).total_seconds() / 3600,
              "t_final": segs[-1]["t_last"], "dt": segs[0]["dt"], "h_min": 1.0 / 64,
              "R_per_segment": [s["R_mbcyc_per_s"] for s in segs],
              "nmb_start_per_segment": [s["nmb_start"] for s in segs],
              "peak_mem_MiB": max(s["peak_mem_MiB"] or 0 for s in segs),
              "card_hours_per_M": cpu_total / 3600 / 100.0}

# ------------------------------------------------------------ vacuum runs
vac_paths = {"headon_v4": "runs/puncture/headon_v4/athena.20261113-062239.log",
             "single_v3": "runs/puncture/single_v3/athena.20261113-043413.log",
             "hcal_dx16": "runs/puncture/hcal/dx16/athena.20261113-051024.log",
             "hcal_dx8_fixed": "runs/puncture/hcal/dx8_fixed/athena.20261113-062219.log",
             "core_t3_three_bh": "scratch/core/core-20261115-120834-d08c476/athena.log"}
vac = {k: parse_log(os.path.join(ROOT, p)) for k, p in vac_paths.items()}
RES["vacuum"] = vac
Rv = np.array([v["R_mbcyc_per_s"] for v in vac.values()])
RES["R_vacuum"] = {"min": float(Rv.min()), "median": float(np.median(Rv)), "max": float(Rv.max())}
t3 = vac["core_t3_three_bh"]
t3_nmb_mean = 0.5 * (t3["nmb_start"] + t3["nmb_end"])
RES["core_t3"] = {"card_hours": t3["cpu_s"] / 3600, "t_end": 16.0, "heavy_mass": 10.0,
                  "card_hours_per_M_heavy": t3["cpu_s"] / 3600 / (16.0 / 10.0),
                  "nmb_mean": t3_nmb_mean, "h_light_over_m": 8.0}

part = parse_log(os.path.join(ROOT, "runs/cosmo/dav_c704_n64_k/athena.20261114-033334.log"))
RES["particle_push_rate"] = part["pups"]

# ------------------------------------------------------------ Hills runs, cost model
S = json.load(open(SCALE))
pas = S["passages"]


def T_run(q, ab, rp, f0=4.0):
    for p in pas:
        if p["q"] == q and p["ab"] == ab and p["rp"] == rp and p["r0_over_rt"] == f0:
            return p["run_time_in_out"]
    raise KeyError((q, ab, rp, f0))


CFL = 0.25
R_med = RES["R_vacuum"]["median"]
R_lo = RES["R_vacuum"]["min"]
NMB_CAP = 2400          # card limit: 26 MB per MeshBlock slot (core JOURNAL-mp l. 331-333)
DN_LEVEL = 2 * 190      # one more level around two separated light holes (core interface s. 4)
DN_DOMAIN = 150         # one more coarse level for r0 = 4 r_t instead of 1 r_t [JUDGEMENT]


def card_hours(T, h_min, nmb, R):
    return nmb * (T / (CFL * h_min)) / R / 3600.0


cases = []
for q, ab, mlight, rp in ((10., 30., 0.05, 6.0), (10., 30., 0.05, 10.0), (4., 20., 0.125, 6.0)):
    T = T_run(q, ab, rp)
    for res in (8, 16, 32):
        nlev = int(round(np.log2(res / 8)))
        nmb = t3_nmb_mean + DN_DOMAIN + nlev * DN_LEVEL
        h = mlight / res
        cases.append({"q": q, "ab": ab, "rp": rp, "m_light": mlight, "res_m_over_h": res,
                      "h_min": h, "T_run": T, "nmb": nmb, "fits_one_card": bool(nmb <= NMB_CAP),
                      "card_hours_median_R": card_hours(T, h, nmb, R_med),
                      "card_hours_slowest_R": card_hours(T, h, nmb, R_lo)})
RES["cases"] = cases

# calibration check: the model applied to core's test 3 itself
t3_model = card_hours(16.0, 0.5 / 8, t3_nmb_mean, t3["R_mbcyc_per_s"])
RES["model_check_core_t3"] = {"model_card_hours": t3_model, "measured_card_hours": t3["cpu_s"] / 3600}

# programme totals at q = 10, a_b = 30, m/8 unless stated
c8 = [c for c in cases if c["q"] == 10. and c["rp"] == 6.0 and c["res_m_over_h"] == 8][0]
c16 = [c for c in cases if c["q"] == 10. and c["rp"] == 6.0 and c["res_m_over_h"] == 16][0]
c32 = [c for c in cases if c["q"] == 10. and c["rp"] == 6.0 and c["res_m_over_h"] == 32][0]
per_run = c8["card_hours_median_R"]
RES["programme"] = {
    "G1_one_vacuum_passage_m8": per_run,
    "G2_convergence_one_rp_m8_m16_m32": c8["card_hours_median_R"] + c16["card_hours_median_R"] + c32["card_hours_median_R"],
    "scan_line_6rp_2orient_1phase_m8": 12 * per_run,
    "scan_line_6rp_2orient_4phase_m8": 48 * per_run,
    "allotment_F_hills_GPU_hours": 40.0,
}

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(RES, f, indent=1)

# ------------------------------------------------------------ figure
fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
ax = fig.add_axes([0.08, 0.15, 0.34, 0.80])
mid = [0.5 * (s["t_first"] + s["t_last"]) for s in segs]
ax.plot(mid, RES["v19"]["R_per_segment"], "o-", color=fs.PAL["red"], ms=4,
        label="n1e4_v19 segments (BHs + particles)")
for k, v in vac.items():
    ax.axhline(v["R_mbcyc_per_s"], color=fs.PAL["blue"] if k != "core_t3_three_bh" else fs.PAL["green"],
               lw=1.0, ls="--" if k != "core_t3_three_bh" else "-")
ax.plot([], [], color=fs.PAL["blue"], lw=1.0, ls="--", label="vacuum puncture runs (4)")
ax.plot([], [], color=fs.PAL["green"], lw=1.0, label="core three-BH run")
ax2 = ax.twinx()
ax2.plot(mid, RES["v19"]["nmb_start_per_segment"], "s", color="grey", alpha=0.6, ms=4)
ax2.set_ylabel("MeshBlocks at segment start", color="grey")
ax2.set_ylim(0, 2500)
ax.set_xlabel(r"$t/M$ (n1e4_v19)")
ax.set_ylabel("MeshBlock-cycles per second")
ax.set_ylim(0, 2600)
ax.legend(loc="lower left", fontsize=7)

ax = fig.add_axes([0.63, 0.15, 0.35, 0.80])
cols = {(10., 6.0): fs.PAL["red"], (10., 10.0): fs.PAL["orange"], (4., 6.0): fs.PAL["blue"]}
for key, c in cols.items():
    sel = [x for x in cases if (x["q"], x["rp"]) == key]
    ax.plot([x["res_m_over_h"] for x in sel], [x["card_hours_median_R"] for x in sel], "o-", color=c,
            label=rf"$q={int(key[0])}$, $r_p={key[1]:.0f}\,r_g$")
    ax.fill_between([x["res_m_over_h"] for x in sel], [x["card_hours_median_R"] for x in sel],
                    [x["card_hours_slowest_R"] for x in sel], color=c, alpha=0.2, lw=0)
ax.axhline(40.0, **fs.GUIDE)
ax.text(8.3, 46, "F allotment to next gate (40 GPU-h)", fontsize=7)
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xticks([8, 16, 32])
ax.set_xticklabels(["m/8", "m/16", "m/32"])
ax.set_xlabel("cells at the light holes")
ax.set_ylabel("card-hours per passage")
ax.legend(loc="upper left", fontsize=7)
fs.save(fig, os.path.join(OUT, "fig_cost"))
plt.close(fig)

print(json.dumps({k: RES[k] for k in ("v19", "R_vacuum", "core_t3", "model_check_core_t3",
                                       "programme", "particle_push_rate")}, indent=1))
for c in cases:
    print(c)
