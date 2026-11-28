#!/usr/bin/env python3
"""Card memory and card time of the population member 256^3 at eight particles per cell
(decision 0048 item 3), from the measured peaks and wall times of three members.

Reads, per run directory, the job logs of `scripts/_athena_job.sh` (lines
`# host=... start=<iso>` and `# exit=... end=<iso> ... gpu_mem_peak_MiB=<M>`; the card name
and total memory from the `nvidia-smi` header line) and the cycle count of the last row of
`pop.nrpic.hst`. Models of the peak card memory, unknowns fitted exactly to three members:
  plain:  M = c + m N_cells           + p N_particles
  ghosts: M = c + m n_blocks (n_b+2g)^3 + p N_particles   (g = nghost = 4 of the deck)
The member wanted has the mesh of the 256^3 one-per-cell member (same blocks) and eight times
its particles, so M(256, 8) = M(256, 1) + 7 p N(256, 1); p from the fit, and as a bound the
largest p allowed by the 128^3 eight-per-cell peak alone (all of it charged to particles).
Card time: seconds per cycle split the same way (mesh at fixed blocks, particles linear).

  mem_fit.py --scratch DIR --out DIR
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

# name, run directories (a run and its continuation), mesh n, particles per cell, gauge
MEMBERS = [
    ("64^3, 8 ppc (ZS)", ["B-20261127-232258-37c6773"], 64, 8, "zero shift"),
    ("128^3, 8 ppc (ZS)", ["B-20261124-223926-33194d9", "B-20261125-221742-5100a22/p8_cont"],
     128, 8, "zero shift"),
    ("256^3, 1 ppc (GD)", ["B-20261126-105021-6343c13"], 256, 1, "Gamma driver"),
]
TIME_EXTRA = [("128^3, 1 ppc (GD)", ["B-20261124-210431-6bf48af"], 128, 1, "Gamma driver")]
NGHOST = 4
NBLOCKS = 8          # every member: meshblock n/2, eight blocks


def logs_of(d):
    return sorted(glob.glob(os.path.join(d, "chain", "seg*.log"))) + \
        sorted(glob.glob(os.path.join(d, "athena.*.log")))


def read_member(scr, dirs):
    peak, wall, card, total = 0.0, 0.0, None, None
    for d in dirs:
        for f in logs_of(os.path.join(scr, d)):
            if f.endswith("gpumem.csv"):
                continue
            start = end = None
            for line in open(f, errors="replace"):
                if line.startswith("# host="):
                    m = re.search(r"start=(\S+)", line)
                    start = datetime.fromisoformat(m.group(1)) if m else None
                elif line.startswith("# exit="):
                    m = re.search(r"end=(\S+)", line)
                    end = datetime.fromisoformat(m.group(1)) if m else None
                    m = re.search(r"gpu_mem_peak_MiB=([0-9.]+)", line)
                    if m:
                        peak = max(peak, float(m.group(1)))
                elif line.startswith("# 0, NVIDIA") and card is None:
                    p = [x.strip() for x in line[2:].split(",")]
                    card, total = p[1], float(p[3].split()[0])
            if start and end:
                wall += (end - start).total_seconds()
    cyc = None
    for d in dirs:
        h = os.path.join(scr, d, "pop.nrpic.hst")
        if os.path.exists(h):
            rows = [ln.split() for ln in open(h) if ln.strip() and not ln.startswith("#")]
            cyc = max(cyc or 0, int(float(rows[-1][1])))
    return dict(peak_MiB=peak, wall_s=wall, cycles=cyc, card=card, total_MiB=total)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    rows = []
    for name, dirs, n, ppc, gauge in MEMBERS + TIME_EXTRA:
        r = read_member(a.scratch, dirs)
        nb = n // 2
        r.update(name=name, dirs=dirs, n=n, ppc=ppc, gauge=gauge, cells=n ** 3,
                 ghosted=NBLOCKS * (nb + 2 * NGHOST) ** 3, particles=ppc * n ** 3)
        rows.append(r)
        print(f"{name:20s} peak {r['peak_MiB']:8.0f} MiB  wall {r['wall_s']:7.0f} s  "
              f"cycles {r['cycles']}  card {r['card']} ({r['total_MiB']} MiB)")
    mem = rows[:3]
    y = np.array([r["peak_MiB"] for r in mem])
    fits = {}
    for model, key in (("plain", "cells"), ("ghosts", "ghosted")):
        A = np.array([[1.0, r[key], r["particles"]] for r in mem])
        c, m, p = np.linalg.solve(A, y)
        n256 = mem[2]["particles"]
        pred = mem[2]["peak_MiB"] + 7 * p * n256
        fits[model] = dict(c_MiB=c, m_MiB_per_cell=m, p_bytes_per_particle=p * 2 ** 20,
                           predicted_256_8ppc_MiB=pred)
        print(f"{model:7s}: c {c:6.0f} MiB, m {m * 2**20:7.1f} B/cell, "
              f"p {p * 2**20:6.1f} B/particle -> M(256, 8 ppc) = {pred:7.0f} MiB")
    p_max = mem[1]["peak_MiB"] / mem[1]["particles"]
    bound = mem[2]["peak_MiB"] + 7 * p_max * mem[2]["particles"]
    total = mem[2]["total_MiB"]
    print(f"bound (all of the 128^3/8 ppc peak charged to particles): {bound:7.0f} MiB "
          f"of {total:.0f} MiB")

    # card time: seconds per cycle; particle cost per particle-cycle from 128^3 8 vs 1 ppc
    t = {r["name"]: r["wall_s"] / r["cycles"] for r in rows}
    s128_8, s128_1 = t["128^3, 8 ppc (ZS)"], t["128^3, 1 ppc (GD)"]
    s256_1 = t["256^3, 1 ppc (GD)"]
    per_pc = (s128_8 - s128_1) / (7 * 128 ** 3)
    s256_8 = s256_1 + 7 * per_pc * 256 ** 3
    cyc256 = rows[2]["cycles"]
    ch = s256_8 * cyc256 / 3600.0
    print(f"s/cycle: 128/8 {s128_8:.3f}, 128/1 {s128_1:.3f}, 256/1 {s256_1:.3f}; particle "
          f"{per_pc:.3e} s per particle-cycle -> 256/8 {s256_8:.2f} s/cycle, "
          f"{cyc256} cycles, {ch:.2f} card-h (wall, incl. writes)")

    res = dict(members=rows, fits=fits, bound_MiB=bound, card_total_MiB=total,
               card=mem[2]["card"], seconds_per_cycle=t, particle_s_per_particle_cycle=per_pc,
               predicted_256_8ppc_s_per_cycle=s256_8, predicted_256_8ppc_card_h=ch,
               cycles_256=cyc256)
    with open(os.path.join(a.out, "mem_fit.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)

    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.6), constrained_layout=True)
    ax = axs[0]
    xs = np.arange(len(mem) + 1)
    lab = [r["name"].replace(" (", "\n(") for r in mem] + ["256^3, 8 ppc\n(wanted)"]
    ax.bar(xs[:3], y / 1024, color="0.55", label="measured peak")
    for k, (model, mk) in enumerate((("plain", "o"), ("ghosts", "s"))):
        ax.plot([3 + 0.15 * (2 * k - 1)], [fits[model]["predicted_256_8ppc_MiB"] / 1024], mk,
                color=f"C{k}", label=f"model '{model}'")
    ax.errorbar([3], [bound / 1024], yerr=[[bound / 1024 - y[2] / 1024], [0]], fmt="v",
                color="C3", capsize=3, label="bound")
    ax.axhline(total / 1024, color="k", lw=0.8, ls="--")
    ax.text(0.0, total / 1024 * 0.93, f"card: {total / 1024:.0f} GiB", fontsize=7)
    ax.set_xticks(xs)
    ax.set_xticklabels(lab, fontsize=6)
    ax.set_ylabel("peak card memory [GiB]")
    ax.legend(fontsize=6, loc="center left")
    ax = axs[1]
    names = list(t)
    ax.bar(np.arange(len(names)), [t[k] for k in names], color="0.55")
    ax.bar([len(names)], [s256_8], color="C0")
    ax.set_xticks(np.arange(len(names) + 1))
    ax.set_xticklabels([k.replace(" (", "\n(") for k in names] + ["256^3, 8 ppc\n(predicted)"],
                       fontsize=6)
    ax.set_ylabel("wall seconds per cycle")
    ax.text(0.02, 0.92, f"256^3, 8 ppc: {ch:.1f} card-h for {cyc256} cycles",
            transform=ax.transAxes, fontsize=7)
    fs.save(fig, os.path.join(a.out, "mem_fit"))
    plt.close(fig)


if __name__ == "__main__":
    main()
