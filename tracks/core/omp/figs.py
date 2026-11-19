#!/usr/bin/env python3
"""Figures of work package omp from the records of its registered runs.

    figs.py scaling  --runs DIR [DIR ...] [--card DIR] --out figs/scaling
    figs.py diff     --runs DIR [DIR ...] --out figs/thread_diff
    figs.py kernels  --runs DIR [DIR ...] --out figs/kernels
    figs.py placement --runs DIR --out figs/placement

DIR is the output directory of a run (scratch/core/<run_id>): the scripts read
scaling*.json (scaling.py) or summary.json (regress.py) there. Style: python/nrpic/
figstyle.py.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

CASE_LABEL = {"punc": "vacuum puncture, refined mesh", "cluster": r"cluster, $10^5$ particles",
              "cosmo": r"$64^3$ cosmology box", "newton": r"Newtonian mode, $128^3$",
              "bench": r"Z4c benchmark, $128^3$"}
ORDER = ["punc", "cluster", "cosmo", "newton"]


def load_scaling(dirs):
    recs = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "scaling*.json"))):
            for r in json.load(open(f)):
                r["run_id"] = os.path.basename(os.path.normpath(d))
                recs.append(r)
    return recs


def best_by(recs, exe=None, mode=""):
    """{case: {threads: (best seconds per step, all values)}}"""
    out = {}
    for r in recs:
        if r.get("exit") != 0 or "s_per_step" not in r:
            continue
        if exe is not None and r.get("exe_label") != exe:
            continue
        if r.get("mode", "") != mode:
            continue
        out.setdefault(r["case"], {}).setdefault(r["threads"], []).append(r["s_per_step"])
    return {c: {t: (min(v), v) for t, v in d.items()} for c, d in out.items()}


def card_times(card_dir):
    """seconds per step of the card runs of card_timing.list: {case: best}"""
    out = {}
    if not card_dir:
        return out
    for log in glob.glob(os.path.join(card_dir, "*", "athena.log")):
        name = os.path.basename(os.path.dirname(log))
        case = name.split("_")[0]
        text = open(log, errors="replace").read()
        m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", text)
        c = re.findall(r"cycle=(\d+)", text)
        if m and c and int(c[-1]) > 0:
            s = float(m.group(1))/int(c[-1])
            out[case] = min(out.get(case, 1e300), s)
    return out


def fig_scaling(a):
    recs = load_scaling(a.runs)
    best = best_by(recs, exe=a.exe)
    serial = best_by(recs, exe="S")
    card = card_times(a.card)
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.15, top=0.95, wspace=0.26)
    cols = fs.SERIES
    for n, case in enumerate([c for c in ORDER if c in best]):
        th = sorted(best[case])
        t = np.array([best[case][k][0] for k in th])
        axs[0].plot(th, t, "o-", color=cols[n], label=CASE_LABEL.get(case, case))
        for k in th:                                  # every repeat, to show the scatter
            axs[0].plot([k]*len(best[case][k][1]), best[case][k][1], ".", color=cols[n],
                        alpha=0.4, ms=4)
        if case in serial and 1 in serial[case]:
            axs[0].plot([1], [serial[case][1][0]], "s", mfc="none", color=cols[n])
        if case in card:
            axs[0].axhline(card[case], color=cols[n], lw=1.0, ls=":")
        if 1 in best[case]:
            axs[1].plot(th, best[case][1][0]/t, "o-", color=cols[n])
    tt = np.array([1, 64])
    axs[1].plot(tt, tt, **fs.GUIDE)
    for ax in axs:
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks([1, 4, 16, 32, 64])
        ax.set_xticklabels(["1", "4", "16", "32", "64"])
        ax.set_xlabel("threads")
        ax.minorticks_off()
    axs[0].set_ylabel("seconds per step")
    axs[1].set_ylabel("speed-up over one thread")
    axs[1].set_yticks([1, 2, 4, 8, 16, 32, 64])
    axs[1].set_yticklabels(["1", "2", "4", "8", "16", "32", "64"])
    axs[0].legend(loc="upper right", fontsize=8)
    fs.save(fig, a.out)
    print("wrote", a.out + ".png")
    for case in best:
        print(case, {k: round(v[0], 4) for k, v in sorted(best[case].items())},
              "serial", serial.get(case, {}).get(1, (None,))[0], "card", card.get(case))


def fig_diff(a):
    """Largest difference of each configuration against its reference, per case."""
    rows = []
    for d in a.runs:
        s = json.load(open(os.path.join(d, "summary.json")))
        for case, c in s["cases"].items():
            for key, r in c["comparisons"].items():
                rows.append((case, key, r["worst_rel_file"], len(r["differ"]),
                             len(r["identical"]), r["structural_difference"]))
    cases = [c for c in ["geo", "boris", "dep", "east", "os", "jeans", "binary", "newton",
                         "coll", "kg", "noise", "bench", "punc"]
             if any(r[0] == c for r in rows)]
    keys = list(dict.fromkeys(r[1] for r in rows))
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.09, right=0.70, bottom=0.14, top=0.95)
    cols = fs.series_colors(len(keys)) if len(keys) > 5 else fs.SERIES
    floor = 1.0e-18
    for n, key in enumerate(keys):
        xs, ys, ident = [], [], []
        for i, case in enumerate(cases):
            for r in rows:
                if r[0] == case and r[1] == key:
                    xs.append(i + (n - 0.5*(len(keys) - 1))*0.8/len(keys))
                    ys.append(max(r[2], floor))
                    ident.append(r[3] == 0)
        xs, ys, ident = np.array(xs), np.array(ys), np.array(ident)
        ax.plot(xs[~ident], ys[~ident], "o", color=cols[n % len(cols)], ms=4, label=key)
        ax.plot(xs[ident], ys[ident], "o", mfc="none", color=cols[n % len(cols)], ms=4)
    ax.axhline(a.tol, **fs.GUIDE)
    ax.axhline(floor, **fs.MASK_LINE)
    ax.set_yscale("log")
    ax.set_ylim(floor/3, 1.0e-6)
    ax.set_xticks(range(len(cases)))
    ax.set_xticklabels(cases, fontsize=8)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylabel("largest difference / largest number of the file")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7)
    fs.save(fig, a.out)
    print("wrote", a.out + ".png")


def fig_kernels(a):
    """Share of the time in kernels per group of kernels, per case and configuration."""
    groups = [("Z4c right-hand side", ("z4c rhs",)),
              ("constraints", ("ADM constraints", "Alg constr")),
              ("mesh boundaries", ("ProlCC", "restrictCC", "SendBuff", "RecvBuff", "z4cbc",
                                   "PackMG", "UnpackMG", "CopyCons")),
              ("dissipation, update", ("K-O", "RK update")),
              ("multigrid", ("Multigrid", "MG::")),
              ("deposit", ("nrpic_deposit", "nrpic_dep_", "nrpic_normalize")),
              ("push, kick", ("nrpic_push", "nrpic_newton_kick", "nrpic_newton_push",
                              "nrpic_assign", "nrpic_compact", "nrpic_count")),
              ("filter, sources", ("nrpic_filter", "nrpic_comp", "nrpic_stepsrc",
                                   "nrpic_sharpen", "nrpic_fillmet", "nrpic_cons")),
              ("zero-fill of new arrays", ("View::initialization",))]
    recs = [r for r in load_scaling(a.runs) if r.get("kernels", {}).get("kernels")]
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.30, right=0.72, bottom=0.14, top=0.95)
    cols = fs.series_colors(len(groups) + 1)
    labels = []
    for i, r in enumerate(recs):
        ker = r["kernels"]["kernels"]
        tot = sum(v[0] for v in ker.values())
        left = 0.0
        used = 0.0
        for g, (name, pats) in enumerate(groups):
            t = sum(v[0] for k, v in ker.items() if any(p in k for p in pats))
            used += t
            ax.barh(i, t/tot, left=left, color=cols[g], label=name if i == 0 else None)
            left += t/tot
        ax.barh(i, (tot - used)/tot, left=left, color="0.8",
                label="other" if i == 0 else None)
        labels.append("%s, %d threads%s (%.2f s/step)" % (
            r["case"], r["threads"], ", private" if r.get("mode") == "priv" else "",
            r.get("s_per_step", float("nan"))))
    ax.set_yticks(range(len(recs)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of the time in kernels")
    ax.invert_yaxis()
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7)
    fs.save(fig, a.out)
    print("wrote", a.out + ".png")


def fig_placement(a):
    recs = load_scaling(a.runs)
    names = {"none": "no binding", "spread": "spread over cores", "close": "close on cores",
             "auto": "least busy cores (omp_places.py)"}
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.30, top=0.95)
    keys = list(names)
    for i, k in enumerate(keys):
        v = [r["s_per_step"] for r in recs if r.get("tag", "").startswith(k)
             and "s_per_step" in r]
        ax.plot([i]*len(v), v, "o", color=fs.SERIES[1])
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([names[k] for k in keys], rotation=20, ha="right", fontsize=8)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.5, len(keys) - 0.5)
    ax.set_ylabel("seconds per step")
    fs.save(fig, a.out)
    print("wrote", a.out + ".png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["scaling", "diff", "kernels", "placement"])
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--card", default="")
    ap.add_argument("--exe", default="O3")
    ap.add_argument("--tol", type=float, default=1.0e-8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    {"scaling": fig_scaling, "diff": fig_diff, "kernels": fig_kernels,
     "placement": fig_placement}[a.what](a)


if __name__ == "__main__":
    main()
