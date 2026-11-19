#!/usr/bin/env python3
"""Card job of work package newton2 (cases.py card): the card twins of T1 against the
processor runs, and the throughput cases (T9).

    card_judge.py --card CARD_RUNDIR --t1 T1_RUNDIR [--out DIR]

Card twins (plane wave of problems/newton, N = 32, to t = 3): chk_mg, chk_fft7, chk_fftsp
against the processor cases mg, fft7, fftsp of T1: positions (wrapped, in units of the
box) and momenta (relative to the largest) at every snapshot, K and W of every record of
the history (relative to the largest |value|); and chk_fft7 against chk_mg on the card.
Throughput: seconds per step (cpu time used over the cycles, from athena.log), V cycles
per step (history column), particle updates per second, peak card memory
(athena.*.gpumem.csv), for bench_*.  The pancake east64 and the group history chk_sin32
are judged by t2_pancake.py --card and t3_groups.py --card.
Writes DIR/card_judge.json and DIR/card_judge.{png,pdf}.
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402

L = 4.0
TWINS = (("chk_mg", "mg"), ("chk_fft7", "fft7"), ("chk_fftsp", "fftsp"))
BENCH = ("bench_per256_fft", "bench_per256_mg", "bench_iso256_mg", "bench_per384_fft",
         "bench_iso384_mg")


def snapshots(rundir):
    out = []
    for f in sorted(glob.glob(os.path.join(rundir, "*.part.*.bin"))):
        t, cyc, x, u, m, tag = nw.read_snapshot(f)
        xo, uo = np.empty_like(x), np.empty_like(u)
        xo[tag], uo[tag] = x, u
        out.append((t, xo, uo))
    return out


def compare(da, db):
    sa, sb = snapshots(da), snapshots(db)
    n = min(len(sa), len(sb))
    dx, du, ts = [], [], []
    for p, q in zip(sa[:n], sb[:n]):
        d = p[1] - q[1]
        d -= L*np.round(d/L)
        dx.append(float(np.abs(d).max()/L))
        du.append(float(np.abs(p[2] - q[2]).max()/max(np.abs(q[2]).max(), 1e-300)))
        ts.append(float(p[0]))
    ha = nw.read_newton_hst(os.path.join(da, "newton.newton.hst"))
    hb = nw.read_newton_hst(os.path.join(db, "newton.newton.hst"))
    m = min(len(ha["K"]), len(hb["K"]))
    rel = {}
    for key in ("K", "W"):
        sc = np.max(np.abs(hb[key][:m]))
        rel[key] = float(np.max(np.abs(ha[key][:m] - hb[key][:m]))/sc)
    return dict(nsnap=(len(sa), len(sb)), nrec=(len(ha["K"]), len(hb["K"])), times=ts,
                dx_over_L=dx, du_rel=du, dx_max=max(dx) if dx else None,
                du_max=max(du) if du else None, K_rel=rel["K"], W_rel=rel["W"])


def log_numbers(d):
    path = os.path.join(d, "athena.log")
    if not os.path.exists(path):
        return None
    txt = open(path, errors="replace").read()
    out = {}
    for key, pat in (("cpu_s", r"cpu time used\s*=\s*([0-9.eE+-]+)"),
                     ("cycles", r"time=\S+ cycle=(\d+)\s*\ntlim"),
                     ("particle_updates_per_s", r"particle-updates/cpu_second\s*=\s*([0-9.eE+-]+)")):
        mm = re.findall(pat, txt)
        if mm:
            out[key] = float(mm[-1])
    out["terminated"] = "Terminating on" in txt
    mem = sorted(glob.glob(os.path.join(d, "athena.*.gpumem.csv")))
    if mem:
        vals = []
        for line in open(mem[-1]):     # timestamp, memory.used [MiB], utilization [%]
            parts = [s.strip() for s in line.split(",")]
            if line.startswith("#") or len(parts) < 2 or not parts[1].isdigit():
                continue
            vals.append(int(parts[1]))
        out["gpu_mem_peak_mib"] = max(vals) if vals else None
    h = os.path.join(d, "newton.newton.hst")
    if os.path.exists(h):
        hh = nw.read_newton_hst(h)
        out["mg_cycles_mean"] = float(np.mean(hh["mg_cycles"][1:])) if len(hh["mg_cycles"]) > 1 else None
    if "cpu_s" in out and out.get("cycles"):
        out["s_per_step"] = out["cpu_s"]/out["cycles"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    res = {"twins": {}, "bench": {}}
    for c, p in TWINS:
        dc = os.path.join(a.card, c)
        if os.path.exists(os.path.join(dc, "newton.newton.hst")):
            res["twins"][c + "-" + p] = compare(dc, os.path.join(a.t1, p))
    if all(os.path.exists(os.path.join(a.card, c, "newton.newton.hst"))
           for c in ("chk_fft7", "chk_mg")):
        res["twins"]["chk_fft7-chk_mg"] = compare(os.path.join(a.card, "chk_fft7"),
                                                  os.path.join(a.card, "chk_mg"))
    for b in BENCH:
        d = os.path.join(a.card, b)
        if os.path.isdir(d):
            res["bench"][b] = log_numbers(d)
    for name in ("east64", "chk_sin32"):
        d = os.path.join(a.card, name)
        if os.path.isdir(d):
            res[name] = log_numbers(d)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.95, wspace=0.32)
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"]]
    for (k, v), col in zip(res["twins"].items(), cols):
        t = np.array(v["times"])
        y = np.maximum(np.array(v["dx_over_L"]), 1e-17)
        axs[0].semilogy(t, y, "o-", ms=3, color=col, label=k.replace("-", " vs "))
    axs[0].axvline(2.0, color="k", lw=1.0, ls=":")
    axs[0].set_xlabel(r"time $t$ (shell crossing at $t = 2$)")
    axs[0].set_ylabel(r"max $|x_{\rm card} - x_{\rm proc}|/L$")
    axs[0].legend(loc="upper left", fontsize=7)
    names = [b for b in BENCH if res["bench"].get(b) and res["bench"][b].get("s_per_step")]
    if names:
        sps = [res["bench"][b]["s_per_step"] for b in names]
        axs[1].bar(range(len(names)), sps, color=fs.PAL["blue"])
        axs[1].set_xticks(range(len(names)))
        axs[1].set_xticklabels([b.replace("bench_", "") for b in names], rotation=25,
                               fontsize=7)
        axs[1].set_ylabel(r"seconds per step ($2\times10^6$ particles)")
    fs.save(fig, os.path.join(a.out, "card_judge"))
    with open(os.path.join(a.out, "card_judge.json"), "w") as f:
        json.dump(res, f, indent=1)
    short = {k: {kk: vv for kk, vv in v.items() if kk not in ("times", "dx_over_L", "du_rel")}
             for k, v in res["twins"].items()}
    print(json.dumps(dict(twins=short, bench=res["bench"],
                          east64=res.get("east64"), chk_sin32=res.get("chk_sin32")), indent=1))


if __name__ == "__main__":
    main()
