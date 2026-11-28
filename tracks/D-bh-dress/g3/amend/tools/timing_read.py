#!/usr/bin/env python3
"""Reader of the card timing runs T-12u and T-16u (g3/amend JOURNAL entry 3; SCOPE_G3 amendment A1)
beside G-8's rate from EG8's segment logs, and the cost of the mesh leg (A1, A5).

Reads: <timing>/t12u, <timing>/t16u (athena.log, gpumem csv, horizon status), <eg8>/chain/seg*.log and
seg*.gpumem.csv. Writes timing_read.json and timing_read.png into the run directory.

Usage: timing_read.py --timing RUNDIR --eg8 RUNDIR
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle  # noqa: E402

CARD_MIB = 81920.0
T_SCOPE = 400.0      # tlim of every G3 member (SCOPE_G3 section 3)
OVERHEAD = 1.15      # preemption overhead of A1
NG = 4               # ghost zones (decks: nghost = 4)
NBLK = 456


def peak_mib(paths):
    pk = 0
    for f in paths:
        for line in open(f):
            if line.startswith("#"):
                continue
            p = line.split(",")
            try:
                pk = max(pk, int(p[1].split()[0]))
            except (IndexError, ValueError):
                pass
    return pk


def read_log(path):
    txt = open(path).read()
    d = dict(log=path)
    m = re.search(r"elapsed=([0-9.eE+-]+) cycle=0", txt)
    d["init_s"] = float(m.group(1)) if m else None
    m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    d["cpu_s"] = float(m.group(1)) if m else None
    m = re.findall(r"time=([0-9.eE+-]+) cycle=(\d+)", txt)
    d["t_last"], d["cycle_last"] = (float(m[-1][0]), int(m[-1][1])) if m else (None, None)
    m = re.search(r"# exit=(\d+)", txt)
    d["exit"] = int(m.group(1)) if m else None
    m = re.search(r"Total number of MeshBlocks = (\d+)", txt)
    d["blocks"] = int(m.group(1)) if m else None
    m = re.search(r"failed to allocate ([0-9.]+) GiB \(label=\"(\w+)\"\)", txt)
    d["alloc_fail"] = (float(m.group(1)), m.group(2)) if m else None
    m = re.search(r"gpu_mem_peak_MiB=(\d+)", txt)
    d["peak_MiB_log"] = int(m.group(1)) if m else None
    return d


def first_search(path):
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        p = line.split("#")[0].split()
        return dict(time=float(p[1]), found=int(p[2]), reason=int(p[3]), flow=int(p[4]), mass=float(p[6]))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", required=True)
    ap.add_argument("--eg8", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    J = {}

    # G-8 from EG8: segments that advanced more than 20 M (rate free of start-up)
    segs = []
    for f in sorted(glob.glob(os.path.join(a.eg8, "chain", "seg*.log"))):
        txt = open(f).read()
        ts = re.findall(r"time=([0-9.eE+-]+) cycle=(\d+)", txt)
        cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        init = re.search(r"elapsed=([0-9.eE+-]+) cycle=", txt)
        if len(ts) < 1 or not cpu:
            continue
        t0 = float(ts[0][0])
        t1 = float(ts[-1][0])
        segs.append(dict(log=os.path.basename(f), t0=t0, t1=t1, cpu_s=float(cpu.group(1)),
                         init_s=float(init.group(1)) if init else 0.0))
    long_ = [s for s in segs if s["t1"] - s["t0"] > 20]
    rates = [(s["cpu_s"] - s["init_s"]) / (s["t1"] - s["t0"]) for s in long_]
    g8 = dict(segments=long_, s_per_M=rates, s_per_M_mean=float(np.mean(rates)),
              peak_MiB=peak_mib(glob.glob(os.path.join(a.eg8, "chain", "seg*.gpumem.csv"))),
              cells_per_block=(24 + 2 * NG) ** 3, steps_per_M=32)
    J["G-8"] = g8

    out = {}
    for name, sub, nb, spm in (("G-12u", "t12u", 36, 48), ("G-16u", "t16u", 48, 64)):
        d = read_log(os.path.join(a.timing, sub, "athena.log"))
        d["peak_MiB"] = peak_mib(glob.glob(os.path.join(a.timing, sub, "athena.*.gpumem.csv")))
        d["cells_per_block"] = (nb + 2 * NG) ** 3
        d["steps_per_M"] = spm
        st = glob.glob(os.path.join(a.timing, sub, "*.horizon_status_0.txt"))
        d["search_t0"] = first_search(st[0]) if st else None
        if d["exit"] == 0 and d["t_last"]:
            d["s_per_M"] = (d["cpu_s"] - d["init_s"]) / d["t_last"]
            d["ratio_to_G8"] = d["s_per_M"] / g8["s_per_M_mean"]
        out[name] = d
    J.update(out)

    # memory model: peak = c0 + c1 * cells_per_block (fit through G-8 and G-12u, both measured)
    x = np.array([g8["cells_per_block"], out["G-12u"]["cells_per_block"]], float)
    y = np.array([g8["peak_MiB"], out["G-12u"]["peak_MiB"]], float)
    c1 = (y[1] - y[0]) / (x[1] - x[0])
    c0 = y[0] - c1 * x[0]
    pred16 = c0 + c1 * out["G-16u"]["cells_per_block"]
    bmax = int(np.floor((0.97 * CARD_MIB - c0) / c1) ** (1 / 3) - 2 * NG)
    J["memory_model"] = dict(c0_MiB=c0, c1_MiB_per_cell_per_block=c1, bytes_per_cell=c1 * 2**20 / NBLK,
                             G16u_predicted_MiB=pred16, G16u_cards_of_memory=pred16 / CARD_MIB,
                             largest_block_on_one_card_at_97pct=bmax)

    # costs to 400 M (A1: measured s/M x 400 x 1.15); G-16u from cells x steps scaled by G-12u's efficiency
    eff = out["G-12u"]["ratio_to_G8"] / ((out["G-12u"]["cells_per_block"] / g8["cells_per_block"]) * 1.5)
    r16 = (out["G-16u"]["cells_per_block"] / g8["cells_per_block"]) * 2.0 * eff
    cost = {}
    for name, spm in (("G-8", g8["s_per_M_mean"]), ("G-12u", out["G-12u"]["s_per_M"]),
                      ("G-16u (estimate)", g8["s_per_M_mean"] * r16)):
        cost[name] = dict(s_per_M=spm, card_hours_400M=spm * T_SCOPE * OVERHEAD / 3600.0)
    cost["G-16u (estimate)"]["ratio_to_G8"] = r16
    cost["G-16u (estimate)"]["t_16_at_20_card_hours"] = min(T_SCOPE, 20.0 * 3600.0 / (cost["G-16u (estimate)"]["s_per_M"] * OVERHEAD))
    cost["efficiency_G12u_vs_cells_x_steps"] = eff
    J["cost"] = cost

    # entry 3 / P-A1 judgements
    m12 = out["G-12u"]["search_t0"]["mass"]
    J["judge"] = dict(
        T12u_fits=bool(out["G-12u"]["exit"] == 0 and out["G-12u"]["peak_MiB"] < CARD_MIB),
        T12u_blocks=out["G-12u"]["blocks"] == NBLK,
        T12u_found_t0=bool(out["G-12u"]["search_t0"]["found"] == 1),
        T12u_mass_in_entry3_band=bool(abs(m12 - 0.9990) <= 0.0007),
        T12u_A1_rule=bool(-1e-4 <= 1 - m12 <= 1 - 0.9915147),
        T12u_ratio_in_band=bool(2.7 <= out["G-12u"]["ratio_to_G8"] <= 6.6),
        T16u_fits=bool(out["G-16u"]["exit"] == 0),
        T16u_blocks=out["G-16u"]["blocks"] == NBLK)
    with open(os.path.join(a.out, "timing_read.json"), "w") as f:
        json.dump(J, f, indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
    A = ax[0]
    xx = np.linspace(20000, 190000, 50)
    A.plot(xx / 1e3, (c0 + c1 * xx) / 1024, color="0.5", lw=1, ls="--", label="line through G-8 and G-12u")
    A.plot([g8["cells_per_block"] / 1e3], [g8["peak_MiB"] / 1024], "o", color="C0", label="G-8 (EG8, measured peak)")
    A.plot([out["G-12u"]["cells_per_block"] / 1e3], [out["G-12u"]["peak_MiB"] / 1024], "s", color="C2",
           label="G-12u (T-12u, measured peak)")
    f16 = out["G-16u"]
    A.plot([f16["cells_per_block"] / 1e3], [f16["peak_MiB"] / 1024], "v", color="C3",
           label="G-16u: used when it failed")
    if f16["alloc_fail"]:
        A.plot([f16["cells_per_block"] / 1e3], [(f16["peak_MiB"] + 1024 * f16["alloc_fail"][0]) / 1024], "^",
               color="C3", mfc="none", label=f"+ the refused '{f16['alloc_fail'][1]}' ({f16['alloc_fail'][0]} GiB)")
    A.plot([f16["cells_per_block"] / 1e3], [pred16 / 1024], "x", color="C3", ms=9, label="G-16u from the line")
    A.axhline(CARD_MIB / 1024, color="k", lw=0.8, label="one A100 (80 GiB)")
    A.set_xlabel("cells per block with ghost zones [10^3] (456 blocks)")
    A.set_ylabel("card memory [GiB]")
    A.legend(fontsize=7, loc="upper left")
    A.set_title("(a) memory of the uniform family", fontsize=9)
    B = ax[1]
    names = ["G-8", "G-12u", "G-16u (estimate)"]
    ch = [cost[n]["card_hours_400M"] for n in names]
    B.bar(range(3), ch, color=["C0", "C2", "C3"], alpha=0.8)
    for i, c in enumerate(ch):
        B.text(i, c + 0.4, f"{c:.1f}", ha="center", fontsize=8)
    B.plot([-0.4, 0.4], [3.5, 3.5], "k:", lw=1)
    B.plot([0.6, 1.4], [11, 11], "k:", lw=1)
    B.plot([1.6, 2.4], [20, 20], "k:", lw=1, label="caps of A5")
    B.set_xticks(range(3))
    B.set_xticklabels(["G-8", "G-12u", "G-16u\n(two cards; estimate)"])
    B.set_ylabel("card-hours to 400 M (x 1.15)")
    B.legend(fontsize=7)
    B.set_title("(b) cost to 400 M from measured seconds per M", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "timing_read.png"), dpi=130)
    print(json.dumps(dict(judge=J["judge"], cost=cost, memory=J["memory_model"]), indent=1, default=float))


if __name__ == "__main__":
    main()
