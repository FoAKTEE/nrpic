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
    """Records of scaling.py. Before commit of 2026-11-19 08:10 the calls of one phase that
    ran side by side wrote one file and kept only the last call's records; the runs whose
    record is missing are read back from their directories (case/<tag>_t<N>..._r<k>/run.log;
    executable S for the tag 'serial', else O3)."""
    sys.path.insert(0, HERE)
    import omplib as L
    recs = []
    for d in dirs:
        seen = set()
        for f in sorted(glob.glob(os.path.join(d, "scaling*.json"))):
            for r in json.load(open(f)):
                r["run_id"] = os.path.basename(os.path.normpath(d))
                seen.add(os.path.normpath(r["rundir"]))
                recs.append(r)
        for log in sorted(glob.glob(os.path.join(d, "*", "*", "run.log"))):
            rd = os.path.normpath(os.path.dirname(log))
            if rd in seen:
                continue
            name = os.path.basename(rd)
            m = re.match(r"(?:(\w+?)_)?t(\d+)(p?)_", name)
            if not m:
                continue
            r = L.parse_log(log)
            if "loop_s" not in r or not r.get("ncycle"):
                continue
            r.update(case=os.path.basename(os.path.dirname(rd)), threads=int(m.group(2)),
                     tag=m.group(1) or "", mode="priv" if m.group(3) else "", exit=0,
                     exe_label="S" if (m.group(1) or "").startswith("serial") else "O3",
                     rundir=rd, run_id=os.path.basename(os.path.normpath(d)),
                     reconstructed=True)
            r["s_per_step"] = r["loop_s"]/r["ncycle"]
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
    axs[0].plot([], [], "s", mfc="none", color="0.3", label="serial build, one thread")
    if card:
        axs[0].plot([], [], ":", color="0.3", label="one A100 card")
    h, lab = axs[0].get_legend_handles_labels()
    axs[1].legend(h, lab, loc="upper left", fontsize=8)
    fs.save(fig, a.out)
    print("wrote", a.out + ".png")
    for case in best:
        print(case, {k: round(v[0], 4) for k, v in sorted(best[case].items())},
              "serial", serial.get(case, {}).get(1, (None,))[0], "card", card.get(case))


def fig_diff(a):
    """Left: largest difference over the largest number of the file (rel_max of omplib),
    per case (rows) and configuration: filled circles N threads against one thread of the
    same executable, open squares two runs of one configuration; marks at the left edge:
    every file byte-identical. Right: conservation identity of the deposit,
    max_t |int_E - sum_mW|/sum_mW, per configuration. Reads summary_floor.json of
    recompare.py."""
    order = ["geo", "boris", "dep", "east", "os", "jeans", "binary", "newton", "coll", "kg",
             "noise", "bench", "punc"]
    cfg_style = {"4": (fs.SERIES[0], "4 threads"), "16": (fs.SERIES[1], "16 threads"),
                 "4p": (fs.SERIES[3], "4 threads, private"),
                 "16p": (fs.SERIES[4], "16 threads, private"),
                 "1p": (fs.SERIES[2], "1 thread, private")}
    floor = 1.0e-19

    def norm(cfg):
        c = cfg.split("#")[0].replace("O3:", "").replace(":::priv", "p")
        return c

    pts, idn = [], []
    for d in a.runs:
        s = json.load(open(os.path.join(d, "summary_floor.json")))
        for case, c in s["cases"].items():
            for key, r in c["comparisons"].items():
                y, x = key.split(" vs ")
                if norm(x) not in ("1",) and norm(x) != norm(y):
                    continue              # cross comparisons (atomic vs private) left out
                kind = "repeat" if norm(x) == norm(y) else "vs1"
                ident = len(r["differ"]) == 0 or all(
                    v.get("kind") == "log" for v in r["differ"].values())
                val = r.get("worst_rel_max", r.get("worst_rel_file", 0.0))
                pts.append((case, norm(y), kind, val, ident and val == 0.0))
            for cfg, v in c.get("identity", {}).items():
                if v and case in ("dep", "east", "os", "newton"):
                    idn.append((case, norm(cfg), v["E"]))
    cases = [c for c in order if any(p[0] == c for p in pts)]
    yi = {c: i for i, c in enumerate(cases)}
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.2), sharey=True,
                            gridspec_kw={"width_ratios": [2.2, 1.0]})
    fig.subplots_adjust(left=0.09, right=0.78, bottom=0.13, top=0.97, wspace=0.08)
    ax = axs[0]
    cfgs = [k for k in cfg_style if any(p[1] == k for p in pts)]
    for n, cfg in enumerate(cfgs):
        col, lab = cfg_style[cfg]
        dy = (n - 0.5*(len(cfgs) - 1))*0.16
        for kind, mk, mfc in (("vs1", "o", None), ("repeat", "s", "none")):
            sel = [p for p in pts if p[1] == cfg and p[2] == kind]
            if not sel:
                continue
            xs = [max(p[3], floor) for p in sel]
            ys = [yi[p[0]] + dy for p in sel]
            ax.plot(xs, ys, mk, color=col, mfc=mfc if mfc else col, ms=5,
                    label=lab if kind == "vs1" else None)
    ax.plot([], [], "s", color="0.3", mfc="none", label="two runs, same threads")
    ax.plot([], [], "o", color="0.3", label="against one thread")
    ax.axvline(a.tol, **fs.GUIDE)
    ax.axvline(floor, **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_xlim(floor/5, 1.0e-6)
    ax.set_xticks([1e-18, 1e-15, 1e-12, 1e-9])
    ax.set_xlabel("largest difference / largest number of the file")
    ax.text(floor*1.6, -0.9, "identical", fontsize=8, color="0.4")
    ax.set_yticks(range(len(cases)))
    ax.set_yticklabels(cases, fontsize=9)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(len(cases) - 0.5, -1.2)
    ax = axs[1]
    icfg = ["1", "4", "16", "1p", "4p", "16p"]
    colors = {"1": "0.2", "4": fs.SERIES[0], "16": fs.SERIES[1], "1p": fs.SERIES[2],
              "4p": fs.SERIES[3], "16p": fs.SERIES[4]}
    for n, cfg in enumerate(icfg):
        sel = [p for p in idn if p[1] == cfg]
        if not sel:
            continue
        dy = (n - 2.5)*0.12
        ax.plot([max(p[2], floor) for p in sel], [yi[p[0]] + dy for p in sel], "D",
                color=colors[cfg], ms=4, label="1 thread" if cfg == "1" else None)
    ax.set_xscale("log")
    ax.set_xlim(1.0e-17, 1.0e-6)
    ax.set_xticks([1e-16, 1e-12, 1e-8])
    ax.set_xlabel(r"$\max_t |\int E - \sum mW| / \sum mW$")
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    h, lab = axs[0].get_legend_handles_labels()
    h2, lab2 = axs[1].get_legend_handles_labels()
    axs[1].legend(h + h2, lab + lab2, loc="upper left", bbox_to_anchor=(1.03, 1.0),
                  fontsize=7)
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


def table(a):
    """Markdown table: best seconds per step per case and thread count, speed-up over one
    thread, parallel efficiency, the serial build, one card (from --card, or the values
    given with --card-values case=seconds,...), and the card time below which a run is
    cheaper on 16 threads than waiting --wait hours for a card."""
    recs = load_scaling(a.runs)
    best = best_by(recs, exe=a.exe)
    serial = best_by(recs, exe="S")
    card = card_times(a.card)
    for kv in [x for x in a.card_values.split(",") if x]:
        k, v = kv.split("=")
        card.setdefault(k, float(v))
    ths = sorted({t for c in best.values() for t in c})
    lines = ["| case | " + " | ".join("%d thr" % t for t in ths)
             + " | serial | card | 16 thr / card | speed-up 16 | efficiency 16 |",
             "|---" * (len(ths) + 6) + "|"]
    for case in [c for c in ORDER + ["bench"] if c in best]:
        b = best[case]
        row = ["%.3g" % b[t][0] if t in b else "-" for t in ths]
        s1 = b.get(1, (None,))[0]
        s16 = b.get(16, (None,))[0]
        ser = serial.get(case, {}).get(1, (None,))[0]
        cd = card.get(case)
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            case, " | ".join(row), "%.3g" % ser if ser else "-",
            "%.3g" % cd if cd else "pending",
            "%.0f" % (s16/cd) if (s16 and cd) else "-",
            "%.1f" % (s1/s16) if (s1 and s16) else "-",
            "%.2f" % (s1/s16/16) if (s1 and s16) else "-"))
    text = "\n".join(lines) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["scaling", "diff", "kernels", "placement", "table"])
    ap.add_argument("--card-values", default="", help="case=seconds per step on one card")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--card", default="")
    ap.add_argument("--exe", default="O3")
    ap.add_argument("--tol", type=float, default=1.0e-8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    {"scaling": fig_scaling, "diff": fig_diff, "kernels": fig_kernels,
     "placement": fig_placement, "table": table}[a.what](a)


if __name__ == "__main__":
    main()
