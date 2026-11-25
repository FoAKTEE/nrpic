#!/usr/bin/env python3
"""The stop of pop_s028_gr: the four restarts X0-X3 from t = 8 (card batch of run
B-20261124-210432-6c4d005; predictions JOURNAL.md, entry of 2026-11-24 05:58).

    python3 analyze_stop028.py --base DIR_OF_pop_s028_gr --cases DIR_OF_BATCH_RUN

For the base run and each case directory (x0_ctrl, x1_cfl125, x2_gd, x3_f1): the guard stop
(pop.guard.txt: time, cycle), the exit line of athena.log, and the histories of the box
(pop.cstat.hst: K_max, chi_min, Hr_mean, Mr_mean; pop.nrpic.hst: smallest lapse, mean K).
Writes $NRPIC_RUN_DIR/stop028.json and the figure pop_stop028.png (PDF beside).
Units: conformal time t, a = (1 + t/2)^2 (analyze_gr.py).
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

CASES = ["x0_ctrl", "x1_cfl125", "x2_gd", "x3_f1"]
LABEL = {"base": "base run (zero shift)", "x0_ctrl": "X0 same", "x1_cfl125": "X1 cfl 0.125",
         "x2_gd": "X2 Gamma-driver shift", "x3_f1": "X3 f = 1"}


def read_hst(fn):
    """Rows of a history file, the last row of each time kept (restarts repeat rows)."""
    rows = np.atleast_2d(np.loadtxt(fn))
    out = []
    for r in rows:
        while out and out[-1][0] >= r[0]:
            out.pop()
        out.append(r)
    return np.array(out)


def one(d):
    r = {"dir": d}
    g = os.path.join(d, "pop.guard.txt")
    if os.path.exists(g):
        txt = open(g).read()
        m = re.search(r"stops at time ([0-9.eE+-]+), cycle (\d+), dt ([0-9.eE+-]+)", txt)
        r["stop_t"], r["stop_cycle"], r["stop_dt"] = float(m.group(1)), int(m.group(2)), float(m.group(3))
        r["stop_reason"] = txt.splitlines()[2] if len(txt.splitlines()) > 2 else ""
    log = os.path.join(d, "athena.log")
    if os.path.exists(log):
        lines = open(log).read().splitlines()
        r["exit_line"] = next((x for x in reversed(lines) if x.startswith("# exit=")), None)
        r["fatal"] = next((x for x in lines if "FATAL" in x or "not found" in x), None)
        fat = [i for i, x in enumerate(lines) if "FATAL" in x]
        if fat:
            r["fatal"] = " ".join(lines[fat[0]:fat[0] + 2])
    c = os.path.join(d, "pop.cstat.hst")
    if os.path.exists(c) and os.path.getsize(c) > 0:
        c = read_hst(c)
        r["cstat"] = {"t": c[:, 0].tolist(), "chi_min": c[:, 1].tolist(), "K_max": c[:, 4].tolist(),
                      "K_min": c[:, 3].tolist(), "Hr_mean": c[:, 11].tolist(), "Mr_mean": c[:, 15].tolist()}
    h = os.path.join(d, "pop.nrpic.hst")
    if os.path.exists(h) and os.path.getsize(h) > 0:
        h = read_hst(h)
        r["nrpic"] = {"t": h[:, 0].tolist(), "alpha_min": h[:, 15].tolist(), "mean_K": h[:, 28].tolist()}
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    args = ap.parse_args()
    R = {"base": one(args.base)}
    for c in CASES:
        R[c] = one(os.path.join(args.cases, c))
    with open(os.path.join(args.out, "stop028.json"), "w") as f:
        json.dump(R, f, indent=1)

    for k, r in R.items():
        s = f"{k:10s} stop_t {r.get('stop_t')} cycle {r.get('stop_cycle')} dt {r.get('stop_dt')}"
        if "cstat" in r:
            c = r["cstat"]
            s += (f" | t_last {c['t'][-1]:.4f} K_max_last {c['K_max'][-1]:.4e} chi_min_last {c['chi_min'][-1]:.3e}"
                  f" Hr_mean_last {c['Hr_mean'][-1]:.3e} Mr_mean_last {c['Mr_mean'][-1]:.3e}")
        if "nrpic" in r:
            s += f" | alpha_min_last {r['nrpic']['alpha_min'][-1]:.3f} t {r['nrpic']['t'][-1]:.4f}"
        s += f" | exit {r.get('exit_line')} | fatal {r.get('fatal')}"
        print(s)
        if "cstat" in r and k != "base":
            for t, km, hr in zip(r["cstat"]["t"], r["cstat"]["K_max"], r["cstat"]["Hr_mean"]):
                print(f"   t {t:.4f} a {(1 + t/2)**2:6.2f} K_max {km: .4e} Hr_mean {hr:.3e}")

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6))
    col = {"base": "k", "x0_ctrl": fs.PAL["blue"], "x1_cfl125": fs.PAL["orange"],
           "x2_gd": fs.PAL["green"], "x3_f1": fs.PAL["red"]}
    ls = {"base": "-", "x0_ctrl": "--", "x1_cfl125": ":", "x2_gd": "-", "x3_f1": "-"}
    for k, r in R.items():
        if "cstat" not in r:
            continue
        c = r["cstat"]
        t = np.array(c["t"])
        sel = t >= 6.0
        axs[0].plot(t[sel], np.array(c["K_max"])[sel], color=col[k], ls=ls[k], label=LABEL[k])
        axs[2].semilogy(t[sel], np.array(c["Hr_mean"])[sel], color=col[k], ls=ls[k])
        if "nrpic" in r:
            n = r["nrpic"]
            tn = np.array(n["t"])
            s2 = tn >= 6.0
            axs[1].plot(tn[s2], np.array(n["alpha_min"])[s2], color=col[k], ls=ls[k])
        if r.get("stop_t"):
            for ax in axs:
                ax.axvline(r["stop_t"], color=col[k], ls=ls[k], lw=0.8, alpha=0.6)
    axs[0].axhline(0.0, **fs.THIN)
    axs[0].set_ylabel(r"largest $K$ of the box")
    axs[1].set_ylabel(r"smallest lapse $\alpha$")
    axs[2].set_ylabel(r"mean relative $|H|$")
    for ax in axs:
        ax.set_xlabel(r"conformal time $t$")
        ax.set_xlim(6.0, 10.2)
    axs[0].legend(fontsize=6, loc="upper left", frameon=False)
    axs[0].set_title("thin vertical lines: guard stops", fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(args.out, "pop_stop028"))
    plt.close(fig)


if __name__ == "__main__":
    main()
