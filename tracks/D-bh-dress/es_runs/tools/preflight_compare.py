#!/usr/bin/env python3
"""Compare the two processor pre-flight runs of the ES-1G input (es_runs, JOURNAL entry 8).

    preflight_compare.py --gauge <run dir> --release <run dir> [--out DIR]

Reads <dir>/es.nrpic.hst (history every cycle) and <dir>/run.log of both runs; reports
the "not used" warnings of each log, the t = 0 rows, and the differences of the lapse at
every probe and of alpha_min / alpha_max at cycles 1 and 2. Writes DIR/preflight.json
and DIR/figs/preflight.png (gauge minus release lapse at the probes against x).
"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, PKG)
from nrpic import figstyle as fs  # noqa: E402
from analyse import read_named_hst  # noqa: E402

PROBES = [("alpha_probe1", 1.0), ("alpha_probe2", 4.0), ("alpha_probe3", 20.0), ("alpha_probe4", 36.0),
          ("alpha_probe", 46.0), ("alpha_probe5", 56.0), ("alpha_probe6", 80.0), ("alpha_probe7", 152.0)]


def warnings(path):
    if not os.path.exists(path):
        return None
    return [ln.strip() for ln in open(path, errors="replace") if re.search("not used", ln, re.I)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gauge", required=True)
    ap.add_argument("--release", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    G = read_named_hst(os.path.join(a.gauge, "es.nrpic.hst"))
    R = read_named_hst(os.path.join(a.release, "es.nrpic.hst"))
    res = {"warnings_gauge": warnings(os.path.join(a.gauge, "run.log")),
           "warnings_release": warnings(os.path.join(a.release, "run.log")),
           "cycles_gauge": [int(c) for c in G["ncycle"]], "cycles_release": [int(c) for c in R["ncycle"]],
           "rows": []}
    keys = ["np", "sum_m", "alpha_min", "alpha_max"] + [k for k, _ in PROBES]
    n = min(len(G["time"]), len(R["time"]))
    for i in range(n):
        row = {"cycle": int(G["ncycle"][i]), "time": float(G["time"][i])}
        for k in keys:
            if k in G and k in R:
                row[k] = dict(gauge=float(G[k][i]), release=float(R[k][i]), diff=float(G[k][i] - R[k][i]))
        res["rows"].append(row)
    with open(os.path.join(a.out, "preflight.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.96)
    cc = fs.series_colors(max(n, 2))
    for i in range(n):
        xs = [x for k, x in PROBES if k in G]
        d = [abs(G[k][i] - R[k][i]) for k, _ in PROBES if k in G]
        ax.plot(xs, np.maximum(d, 1e-18), "o-", color=cc[i], ms=3, label=f"cycle {int(G['ncycle'][i])}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"probe position $x/M$")
    ax.set_ylabel(r"$|\alpha_{\rm gauge}-\alpha_{\rm release}|$ (floor $10^{-18}$)")
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "figs", "preflight"))
    plt.close(fig)


if __name__ == "__main__":
    main()
