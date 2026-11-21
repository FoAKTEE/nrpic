"""Lead's re-check of the runs_ball package of batch 2b (predictions L10-L13, tracks/A-emd-pbh/
JOURNAL.md entry 2026-11-21T07:55Z, section "Predictions L10-L13").

L10, L11: the commands of the registered analyses A-20261121-080558-02c3188 and
A-20261121-081153-b92c08c are taken from their manifests and run again with the output and the
figure directory pointed into this run directory; their JSON outputs are compared value by value
with the registered ones. L12, L13: own reading of the finder summaries of BH-1R and of BH-1 at
uniform M/8. Writes review_runs_ball.json and fig_review_runs_ball.{pdf,png} into $NRPIC_RUN_DIR
(style python/nrpic/figstyle.py).
"""
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TR))
SCR = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
OUT = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not OUT:
    sys.exit("no output directory")
os.makedirs(OUT, exist_ok=True)
RTOL = 1e-9
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)


def compare(a, b):
    st = {"numbers": 0, "diff": 0, "max_rel": 0.0, "first": []}

    def rec(x, y, p):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                if k in ("wall_s", "run_id", "commit", "date_utc", "out", "figdir"):
                    continue
                if k not in x or k not in y:
                    st["diff"] += 1
                    st["first"].append(f"{p}/{k}: one side only")
                    continue
                rec(x[k], y[k], f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                st["diff"] += 1
                st["first"].append(f"{p}: length {len(x)} vs {len(y)}")
            for i, (u, v) in enumerate(zip(x, y)):
                rec(u, v, f"{p}[{i}]")
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            st["numbers"] += 1
            fx, fy = float(x), float(y)
            if (math.isnan(fx) and math.isnan(fy)) or fx == fy:
                return
            rel = abs(fx - fy) / max(abs(fx), abs(fy), 1e-300)
            st["max_rel"] = max(st["max_rel"], rel)
            if rel > RTOL and abs(fx - fy) > 1e-14:
                st["diff"] += 1
                if len(st["first"]) < 8:
                    st["first"].append(f"{p}: {fx!r} vs {fy!r}")
        elif x != y:
            if isinstance(x, str) and isinstance(y, str) and ("/scratch/" in x or "/figs" in x):
                return
            st["diff"] += 1
            if len(st["first"]) < 8:
                st["first"].append(f"{p}: {str(x)[:60]!r} vs {str(y)[:60]!r}")

    rec(a, b, "")
    st["identical"] = st["diff"] == 0
    return st


def rerun(run_id, sub):
    m = json.load(open(os.path.join(TR, "runs", run_id, "manifest.json")))
    cmd = m["command"][2] if isinstance(m["command"], list) else m["command"]
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    cmd = cmd.replace("--figdir tracks/A-emd-pbh/runs_ball/figs", "--figdir $O")
    env = dict(os.environ, NRPIC_RUN_DIR=d)
    t0 = time.time()
    rc = subprocess.call(["bash", "-c", cmd], cwd=WT, env=env)
    log(f"{sub}: rerun of {run_id} exit {rc} in {time.time() - t0:.0f} s")
    return rc, d


R = {"parts": {}}
CMPS = []
for key, run_id, files in (("L10", "A-20261121-080558-02c3188", ["bh_smr_numbers.json"]),
                           ("L11", "A-20261121-081153-b92c08c",
                            ["excision.json", "bd/turnaround.json", "bh_smr_numbers.json"])):
    rc, d = rerun(run_id, key)
    res = []
    for f in files:
        st = compare(json.load(open(os.path.join(d, f))), json.load(open(os.path.join(SCR, run_id, f))))
        st["file"] = f
        res.append(st)
        CMPS.append((f"{key}:{f}", st["max_rel"], st["identical"]))
        log(f"  {f}: numbers {st['numbers']}, differences {st['diff']}, max rel {st['max_rel']:.2e}"
            + ("" if st["identical"] else f"; first {st['first'][:3]}"))
    R["parts"][key] = {"exit": rc, "compare": res, "holds": rc == 0 and all(s["identical"] for s in res)}


def summary(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(v) for v in line.split()])
    return np.array(rows)


a = summary(os.path.join(SCR, "A-20261119-164634-f1fe887", "bh_smr", "ball.horizon_summary_0.txt"))
ok = np.isfinite(a[:, 2])
i0 = int(np.argmax(ok))
after = ok[i0:]
r12 = {"searches": int(len(a)), "first_t": float(a[i0, 1]), "first_mass": float(a[i0, 2]),
       "first_meanradius": float(a[i0, 10]), "converged_after_first": int(after.sum()),
       "searches_after_first": int(len(after)), "last_t": float(a[-1, 1]),
       "mass_first_4M_median": float(np.median(a[ok & (a[:, 1] <= a[i0, 1] + 4.0), 2])),
       "mass_last": float(a[ok][-1, 2]), "meanradius_range_first_4M":
       [float(a[ok & (a[:, 1] <= a[i0, 1] + 4.0), 10].min()), float(a[ok & (a[:, 1] <= a[i0, 1] + 4.0), 10].max())]}
log("L12", r12)
R["parts"]["L12"] = dict(r12, holds=(r12["first_t"] == 10.875 and abs(r12["first_mass"] - 0.701) < 5e-4
                                     and abs(r12["first_meanradius"] - 0.44) < 0.01
                                     and r12["converged_after_first"] == r12["searches_after_first"]))

b = summary(os.path.join(SCR, "A-20261119-144419-13d5601", "bh_n256", "ball.horizon_summary_0.txt"))
r13 = {"searches": int(len(b)), "converged": int(np.isfinite(b[:, 2]).sum()),
       "iterations_column": sorted(set(int(x) for x in b[:, 0])), "t_range": [float(b[0, 1]), float(b[-1, 1])]}
log("L13", r13)
R["parts"]["L13"] = dict(r13, holds=r13["converged"] == 0)

sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fs.use_style()
fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
a0 = ax[0]
FLOOR = 1e-16
for yi, c in enumerate(CMPS):
    v = max(c[1], FLOOR)
    col = fs.PAL["blue"] if c[2] else fs.PAL["red"]
    a0.plot([FLOOR / 10, v], [yi, yi], color=col, lw=1.0)
    a0.plot([v], [yi], "o", color=col, ms=5)
    a0.text(v * 3, yi, "identical" if c[1] == 0 else f"{c[1]:.1e}", va="center", fontsize=6)
a0.axvline(RTOL, **fs.GUIDE)
a0.set_xscale("log")
a0.set_xlim(1e-17, 1e-3)
a0.set_yticks(range(len(CMPS)))
a0.set_yticklabels([c[0] for c in CMPS], fontsize=6)
a0.invert_yaxis()
a0.set_xlabel("largest relative difference")
a0.set_title("(a) runs_ball analyses rerun", fontsize=8)
a1 = ax[1]
a1.plot(a[ok, 1], a[ok, 2], "o-", color=fs.PAL["blue"], ms=3, label="BH-1R, M/16 level")
a1.axvline(r12["first_t"], **fs.MASK_LINE)
a1.set_xlabel("t / M")
a1.set_ylabel("finder area mass / M")
a1.set_title(f"(b) BH-1R: {r12['converged_after_first']} of {r12['searches_after_first']} searches converge", fontsize=8)
a1.legend(fontsize=6)
a2 = ax[2]
a2.plot(a[ok, 1], a[ok, 10], "o-", color=fs.PAL["blue"], ms=3, label="BH-1R mean radius")
a2.plot(b[:, 1], np.zeros(len(b)), "x", color=fs.PAL["red"], ms=4, label=f"BH-1 M/8: {r13['searches']} searches, none converged")
a2.set_xlabel("t / M")
a2.set_ylabel("mean coordinate radius / M")
a2.set_ylim(-0.05, 0.6)
a2.legend(fontsize=6, loc="lower left")
a2.set_title("(c) finder surfaces", fontsize=8)
fig.tight_layout()
fs.save(fig, os.path.join(OUT, "fig_review_runs_ball"))
R["summary"] = {k: v["holds"] for k, v in R["parts"].items()}
log("summary", R["summary"])
json.dump(R, open(os.path.join(OUT, "review_runs_ball.json"), "w"), indent=1)
open(os.path.join(OUT, "review_runs_ball.log"), "w").write("\n".join(LOG) + "\n")
