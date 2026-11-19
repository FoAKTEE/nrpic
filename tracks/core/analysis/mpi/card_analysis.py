#!/usr/bin/env python3
"""Analysis of the card test of work package mpi (card_job.sh).

    python3 card_analysis.py <outdir of card_job.sh> [--figdir DIR]

Cluster (C1a, C1b one card each, C2 two cards): largest relative differences of the
history columns of the module and of the particle positions, C1b - C1a (the scatter of
card runs) against C2 - C1a. Vacuum meshes (F8a one card, F8b and F16 two cards): number
of MeshBlocks, MeshBlock-cycles per second over the run (from the log of AthenaK), and
the peak memory of each card (gpumem.csv, sampled every 0.5 s, minus the baseline before
the run). Writes card.json and the figure card_test.{pdf,png}.
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
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
import mpi_tests as mt  # noqa: E402


def log_numbers(path):
    out = {}
    txt = open(path, errors="replace").read()
    for key, pat in (("meshblocks", r"Total number of MeshBlocks = (\d+)"),
                     ("mb_cycles", r"MeshBlock-cycles = ([0-9.eE+-]+)"),
                     ("cpu_time", r"cpu time used\s*=\s*([0-9.eE+-]+)"),
                     ("zone_cycles_per_s", r"zone-cycles/cpu_second = ([0-9.eE+-]+)")):
        m = re.findall(pat, txt)
        if m:
            out[key] = float(m[-1])
    out["ranks"] = len(re.findall(r"Rank = \d+:", txt)) or 1
    if "mb_cycles" in out and out.get("cpu_time", 0) > 0:
        out["mb_cycles_per_s"] = out["mb_cycles"]/out["cpu_time"]
    return out


def gpu_memory(path):
    """peak memory used [MiB] per card index during the run, and the first sample"""
    peak, first = {}, {}
    if not os.path.exists(path):
        return {}
    for line in open(path):
        p = [s.strip() for s in line.split(",")]
        if len(p) < 4:
            continue
        try:
            idx, mem = int(p[1]), float(p[2])
        except ValueError:
            continue
        first.setdefault(idx, mem)
        peak[idx] = max(peak.get(idx, 0.0), mem)
    return {str(k): dict(peak_MiB=peak[k], first_MiB=first[k]) for k in sorted(peak)}


def cluster_compare(base, a, b):
    fa = glob.glob(os.path.join(base, a, "*.nrpic.hst"))
    fb = glob.glob(os.path.join(base, b, "*.nrpic.hst"))
    out = {}
    if fa and fb:
        x, y = mt.read_table(fa[0]), mt.read_table(fb[0])
        n = min(len(x), len(y))
        x, y = x[:n], y[:n]
        sc = np.maximum(np.abs(x).max(axis=0), 1e-300)
        rel = np.abs(x - y)/sc
        out["history_max_rel"] = float(rel[:, 2:].max())
        out["history_cols"] = {str(c + 1): float(rel[:, c].max()) for c in (3, 4, 8, 12, 15, 27)}
        out["history_t"] = x[:, 0].tolist()
        out["history_rel_sumE"] = rel[:, 8].tolist()
        out["history_rel_probe"] = rel[:, 12].tolist()
    snaps = sorted(glob.glob(os.path.join(base, a, "*.part.*.bin")))
    ds = []
    for f in snaps:
        g = os.path.join(base, b, os.path.basename(f))
        if os.path.exists(g):
            t1, r1, g1 = mt.read_snapshot(f)
            t2, r2, g2 = mt.read_snapshot(g)
            if np.array_equal(g1, g2) and len(g1):
                ds.append((t1, float(np.abs(r1[:, :3] - r2[:, :3]).max())))
    out["positions"] = ds
    return out


def figure(res, figdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax = fig.add_axes([0.08, 0.16, 0.40, 0.72])
    floor = 1e-18
    for key, col, lab in (("C1b-C1a", fs.PAL["blue"], "1 card, again"),
                          ("C2-C1a", fs.PAL["red"], "2 cards")):
        c = res["cluster"].get(key, {})
        if "history_t" in c:
            ax.semilogy(c["history_t"], np.maximum(c["history_rel_sumE"], floor), color=col,
                        lw=1.0, label=lab + ": int E")
            ax.semilogy(c["history_t"], np.maximum(c["history_rel_probe"], floor), color=col,
                        lw=1.0, ls="--", label=lab + ": lapse at probe")
        if c.get("positions"):
            t, d = zip(*c["positions"])
            ax.semilogy(t, np.maximum(d, floor), "o", color=col, ms=4,
                        label=lab + ": positions (abs.)")
    ax.axhline(2.2e-16, **fs.MASK_LINE)
    ax.set_ylim(floor, 1e-6)
    ax.set_xlabel("t / M")
    ax.set_ylabel("difference from the first one-card run", fontsize=9)
    ax.legend(loc="upper left", fontsize=7)
    ax.set_title("cluster of T3 on the cards", fontsize=10)
    ax2 = fig.add_axes([0.60, 0.16, 0.36, 0.72])
    names = [n for n in ("F8a", "F8b", "F16") if n in res["vacuum"]]
    rates = [res["vacuum"][n].get("mb_cycles_per_s", np.nan) for n in names]
    mems = [max((v["peak_MiB"] - v["first_MiB"]) for v in res["vacuum"][n]["gpu"].values())/1024.0
            if res["vacuum"][n].get("gpu") else np.nan for n in names]
    xs = np.arange(len(names))
    ax2.bar(xs - 0.2, rates, 0.4, color=fs.PAL["blue"], label="MeshBlock-cycles / s")
    ax2.set_ylabel("MeshBlock-cycles per second", fontsize=9, color=fs.PAL["blue"])
    ax3 = ax2.twinx()
    ax3.bar(xs + 0.2, mems, 0.4, color=fs.PAL["orange"], label="peak memory per card")
    ax3.set_ylabel("peak memory per card [GiB]", fontsize=9, color=fs.PAL["orange"])
    ax2.set_xticks(xs)
    ax2.set_xticklabels(["%s\n%d MBs, %d card%s" % (n, res["vacuum"][n].get("meshblocks", 0),
                                                  res["vacuum"][n]["ranks"],
                                                  "" if res["vacuum"][n]["ranks"] == 1 else "s")
                         for n in names], fontsize=8)
    ax2.set_title("Track F's vacuum mesh, 10 cycles", fontsize=10)
    out = []
    for d in figdir:
        os.makedirs(d, exist_ok=True)
        out += fs.save(fig, os.path.join(d, "card_test"))
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--figdir", default=None)
    a = ap.parse_args()
    base = os.path.abspath(a.base)
    res = dict(summary=open(os.path.join(base, "summary.txt")).read().splitlines()
               if os.path.exists(os.path.join(base, "summary.txt")) else [],
               cluster={}, vacuum={})
    res["cluster"]["C1b-C1a"] = cluster_compare(base, "C1a", "C1b")
    res["cluster"]["C2-C1a"] = cluster_compare(base, "C1a", "C2")
    for n in ("C1a", "C1b", "C2", "F8a", "F8b", "F16"):
        d = os.path.join(base, n)
        if not os.path.isdir(d):
            continue
        row = log_numbers(os.path.join(d, "run.log"))
        row["gpu"] = gpu_memory(os.path.join(d, "gpumem.csv"))
        (res["vacuum"] if n.startswith("F") else res["cluster"]).setdefault(n, row)
    with open(os.path.join(base, "card.json"), "w") as f:
        json.dump(res, f, indent=1)
    for line in res["summary"]:
        print(line)
    for key in ("C1b-C1a", "C2-C1a"):
        c = res["cluster"][key]
        print("%s: history max rel %.2e, positions %s" % (
            key, c.get("history_max_rel", float("nan")),
            ", ".join("t=%.3g %.1e" % p for p in c.get("positions", []))))
    for n, v in res["vacuum"].items():
        print("%s: %s MeshBlocks, %s ranks, %.1f MeshBlock-cycles/s, zone-cycles/s %.3g, "
              "memory %s" % (n, v.get("meshblocks"), v.get("ranks"),
                             v.get("mb_cycles_per_s", float("nan")),
                             v.get("zone_cycles_per_s", float("nan")),
                             {k: "%.0f->%.0f MiB" % (g["first_MiB"], g["peak_MiB"])
                              for k, g in v["gpu"].items()}))
    dirs = [os.path.join(base, "figs")] + ([a.figdir] if a.figdir else [])
    for p in figure(res, dirs):
        print("figure", p)


if __name__ == "__main__":
    main()
