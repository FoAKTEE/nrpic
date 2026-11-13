"""Z4c throughput benchmark: zone-cycles per second against MeshBlock size for each
number of ghost zones (finite-difference order 2 (nghost - 1)).

    python3 bench.py [<benchdir>] [--out NAME]

<benchdir> (default runs/dev/bench) holds one directory per run named ng<G>_mb<N>,
each with an athena.log. Markers: the code's own zone-cycles/cpu_second
(whole run). The steady-state value from the elapsed-time lines between the first
reported cycle after cycle 0 and the last one is printed and its largest deviation
quoted in the panel.
"""
import glob
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, parse_cli, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], defaults=["bench=runs/dev/bench"], options=("out",))
out = opts.get("out", "z4c_bench")
root = run_path(runs[0][1])

rows = []
for d in sorted(glob.glob(os.path.join(root, "ng*_mb*"))):
    m = re.match(r"ng(\d+)_mb(\d+)", os.path.basename(d))
    log = os.path.join(d, "athena.log")
    if not m or not os.path.exists(log):
        continue
    txt = open(log).read()
    zc = re.findall(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", txt)
    if not zc:
        print(f"{d}: no zone-cycles line (run incomplete?)")
        continue
    ng, mb = int(m.group(1)), int(m.group(2))
    nx = [int(v) for v in re.findall(r"^nx1\s*=\s*(\d+)", open(
        os.path.join(d, "z4c_bench.athinput")).read(), re.M)][:1] if os.path.exists(
        os.path.join(d, "z4c_bench.athinput")) else [128]
    ncell = nx[0] ** 3
    el = [(int(c), float(e)) for e, c in re.findall(r"elapsed=([0-9.eE+-]+) cycle=(\d+)", txt)]
    el = sorted(set(el))
    ss = np.nan
    if len(el) >= 3:
        (c0, e0), (c1, e1) = el[1], el[-1]
        ss = (c1 - c0) * ncell / (e1 - e0)
    nmb = re.search(r"Total number of MeshBlocks = (\d+)", txt)
    gpu = re.search(r"# 0, ([^,]+),", txt)
    rows.append(dict(ng=ng, mb=mb, zc=float(zc[-1]), ss=ss, nmb=int(nmb.group(1)) if nmb
                     else 0, gpu=gpu.group(1) if gpu else "?"))
    print(f"ng={ng} mb={mb:3d}^3 nmb={rows[-1]['nmb']:4d}: zone-cycles/s = {float(zc[-1]):.3e}"
          f", steady state {ss:.3e}  ({rows[-1]['gpu']})")

fs.use_style()
fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.97)
ngs = sorted({r["ng"] for r in rows})
cols = {2: fs.PAL["yellow"], 3: fs.PAL["green"], 4: fs.PAL["red"]}
for ng in ngs:
    rr = sorted([r for r in rows if r["ng"] == ng], key=lambda r: r["mb"])
    mb = np.array([r["mb"] for r in rr])
    c = cols.get(ng, fs.PAL["orange"])
    ax.plot(mb, [r["zc"] / 1e7 for r in rr], marker="o", color=c, lw=1.0,
            label=f"nghost = {ng} (order {2 * (ng - 1)})")
    for r in rr:
        ax.annotate(f"{r['zc'] / 1e7:.2f}", (r["mb"], r["zc"] / 1e7), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize="small", color=c)
dev = max(abs(r["ss"] / r["zc"] - 1) for r in rows if np.isfinite(r["ss"]))
ax.set_xscale("log", base=2)
ax.set_xticks([16, 32, 64, 128])
ax.set_xticklabels(["16", "32", "64", "128"])
ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_xlim(12, 170)
ax.set_ylim(0, 4.2)
ax.set_xlabel(r"MeshBlock size $N^3$ (128$^3$ cells in total)")
ax.set_ylabel(r"zone-cycles / s $[10^7]$")
ax.legend(loc="upper right", fontsize="small")
gpus = sorted({r["gpu"].replace("NVIDIA ", "").replace(" 80GB PCIe", "") for r in rows})
ax.text(0.03, 0.05, f"Z4c, RK4, one {'/'.join(gpus)}, 20 cycles\n"
        f"cycles 5-20 alone: within {100 * dev:.1f}%", transform=ax.transAxes,
        fontsize="small")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
