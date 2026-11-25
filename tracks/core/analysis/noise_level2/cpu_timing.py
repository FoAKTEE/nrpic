#!/usr/bin/env python3
"""T5 on processors (the card smoke waits for the queue): the four inputs of the card
list (inputs/card/{sr,usr}64_l{0,2}.athinput, 64^3, nmax2 = 256) with the threaded
processor build, nlim cycles each, one after another on the same threads; wall time per
cycle, the box means at the end (finite), and a figure.

    cpu_timing.py --exe ATHENA_OMP --out DIR [--threads 6] [--nlim 30]
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402
import numpy as np             # noqa: E402

CASES = ["sr64_l0", "sr64_l2", "usr64_l0", "usr64_l2"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--nlim", type=int, default=30)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    res = {}
    for c in CASES:
        rd = os.path.join(out, c)
        os.makedirs(rd, exist_ok=True)
        inp = os.path.join(HERE, "inputs", "card", c + ".athinput")
        env = dict(os.environ, OMP_NUM_THREADS=str(a.threads), OMP_PROC_BIND="spread",
                   OMP_PLACES="cores")
        t0 = time.time()
        with open(os.path.join(rd, "log.txt"), "w") as fo:
            rc = subprocess.run([os.path.abspath(a.exe), "-i", inp, f"time/nlim={a.nlim}",
                                 "scalar_field/dump_dt=-1.0"], cwd=rd, stdout=fo,
                                stderr=subprocess.STDOUT, env=env).returncode
        wall = time.time() - t0
        hst = [f for f in os.listdir(rd) if f.endswith(".sf.hst")]
        h = np.loadtxt(os.path.join(rd, hst[0])) if hst else None
        zc = None
        for ln in open(os.path.join(rd, "log.txt")):
            if ln.startswith("zone-cycles/cpu_second"):
                zc = float(ln.split("=")[1])
        res[c] = dict(exit=rc, wall_s=round(wall, 2), wall_per_cycle=wall/a.nlim,
                      zone_cycles_per_cpu_s=zc,
                      finite=bool(h is not None and np.all(np.isfinite(h[-1]))),
                      last_time=float(h[-1, 0]) if h is not None else None,
                      rms_phi=float(h[-1, 7]) if h is not None else None)
    for s in ("sr", "usr"):
        res[f"{s}_l2_over_l0"] = res[f"{s}64_l2"]["wall_s"]/res[f"{s}64_l0"]["wall_s"]
    nl2.dump_json(dict(exe=os.path.abspath(a.exe), threads=a.threads, nlim=a.nlim,
                       cases=res), os.path.join(out, "summary.json"))
    import matplotlib
    matplotlib.use("Agg")
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COL_WIDTH if hasattr(fs, "COL_WIDTH") else 3.4, 2.6))
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.2, top=0.88)
    x = np.arange(len(CASES))
    ax.bar(x, [res[c]["wall_per_cycle"] for c in CASES],
           color=[fs.PAL["blue"], fs.PAL["red"]]*2)
    ax.set_xticks(x)
    ax.set_xticklabels(["SR L0", "SR L2", "USR L0", "USR L2"])
    ax.set_ylabel("wall time per cycle (s)")
    ax.set_title(f"64$^3$, nmax2 = 256, {a.threads} threads; L2/L0: SR "
                 f"{res['sr_l2_over_l0']:.3f}, USR {res['usr_l2_over_l0']:.3f}", fontsize=7)
    fig.savefig(os.path.join(out, "fig_timing.png"), dpi=200)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
