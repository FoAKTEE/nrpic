#!/usr/bin/env python3
"""Test T11 of work package newton2: judgement of the builds of the merged source
(releases core-v0.4 and core-v0.5 plus this package).

    t11_merged.py --t11 RUNDIR_OF_cases.py_t11 --rel RUNDIR_OF_regress_v04.py
                  [--card CARD_RUNDIR --t1 T1_RUNDIR] [--out DIR]

T11a: the merged processor build against release core-v0.5 with the options of this
package absent: summary.json of analysis/release/regress_v04.py (twelve set-ups) and part
"a" of t11.json (the Newtonian set-ups and mesh_static).  T11b: part "b" of t11.json
(cases of T1 and T3 with the Fourier solver and the groups against the files of the
pre-merge build).  Classes of a pair of files as in the release regression: identical;
a: restart file differing in the 36 never-set bytes of the mesh header; b: parameter
dump differing in last_time lines; other.  A part passes if no file is of class other,
every case compared at least one file, and every run ended with exit status 0.
T11c (with --card): the card twins chk_mg, chk_fft7, chk_fftsp of the merged card build
against the processor cases mg, fft7, fftsp of T1 (card_judge.compare): passes within
1e-9 of the box in the positions and 1e-8 in K and W.
Writes DIR/t11_merged.json and DIR/t11_merged.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402

CLASSES = ("identical", "a", "b", "a+b", "other")


def counts(r):
    return {c: len(r[c]) for c in CLASSES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t11", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--card", default="")
    ap.add_argument("--t1", default="")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    rel = json.load(open(os.path.join(a.rel, "summary.json")))
    t11 = json.load(open(os.path.join(a.t11, "t11.json")))
    runs = json.load(open(os.path.join(a.t11, "cases.json")))
    exits = {c["name"]: c["exit"] for c in runs["cases"]}
    res = {"exe_new_sha256": runs["exe_sha256"], "exe_rel_sha256": runs["exe_rel_sha256"],
           "release_driver": {"base_sha256": rel["sha256"]["base"],
                              "new_sha256": rel["sha256"]["new"], "verdict": rel["verdict"]},
           "a": {}, "b": {}}
    ok_a = rel["verdict"] == "PASS" and rel["sha256"]["new"] == runs["exe_sha256"] \
        and rel["sha256"]["base"] == runs["exe_rel_sha256"]
    for case, r in rel["cases"].items():
        res["a"][case] = dict(counts(r), compared=r["compared"], exit=r["exit"],
                              details={f: r["details"][f] for f in r["a"] + r["b"] + r["a+b"]
                                       + r["other"] if f in r["details"]})
        ok_a = ok_a and not r["other"] and r["compared"] > 0 and r["exit"] == [0, 0]
    for case, r in t11["a"].items():
        ex = [exits["%s/rel" % case], exits["%s/new" % case]]
        res["a"][case] = dict(counts(r), compared=r["compared"], exit=ex,
                              details={f: r["details"][f] for f in r["a"] + r["b"] + r["a+b"]
                                       + r["other"] if f in r["details"]})
        ok_a = ok_a and not r["other"] and r["compared"] > 0 and ex == [0, 0]
    ok_b = True
    for case, r in t11["b"].items():
        ex = [exits["%s/new" % case]]
        res["b"][case] = dict(counts(r), compared=r["compared"], exit=ex,
                              reference=r["reference"],
                              details={f: r["details"][f] for f in r["a"] + r["b"] + r["a+b"]
                                       + r["other"] if f in r["details"]})
        ok_b = ok_b and not r["other"] and r["compared"] > 0 and ex == [0]
    res["pass_a"], res["pass_b"] = bool(ok_a), bool(ok_b)
    twins = {}
    if a.card:
        import card_judge as cj
        for c, p in cj.TWINS:
            dc = os.path.join(a.card, c)
            if os.path.exists(os.path.join(dc, "newton.newton.hst")):
                twins[c + "-" + p] = cj.compare(dc, os.path.join(a.t1, p))
        if all(os.path.exists(os.path.join(a.card, c, "newton.newton.hst"))
               for c in ("chk_fft7", "chk_mg")):
            twins["chk_fft7-chk_mg"] = cj.compare(os.path.join(a.card, "chk_fft7"),
                                                  os.path.join(a.card, "chk_mg"))
        res["c"] = twins
        res["pass_c"] = bool(len(twins) == 4 and all(
            v["dx_max"] < 1e-9 and v["K_rel"] < 1e-8 and v["W_rel"] < 1e-8
            and v["nsnap"][0] == v["nsnap"][1] for v in twins.values()))

    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0),
                            gridspec_kw=dict(width_ratios=[16, 3.6, 9]))
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.25, top=0.9, wspace=0.3)
    colc = {"identical": fs.PAL["blue"], "a": fs.PAL["yellow"], "b": fs.PAL["green"],
            "a+b": fs.PAL["orange"], "other": fs.PAL["red"]}
    labc = {"identical": "identical", "a": "a: unset bytes of a restart header",
            "b": "b: last_time of a parameter dump", "a+b": "a and b", "other": "other"}
    for ax, part, title in ((axs[0], "a", "against release core-v0.5, new options absent"),
                            (axs[1], "b", "against the pre-merge build")):
        names = list(res[part])
        x = np.arange(len(names))
        bottom = np.zeros(len(names))
        for c in CLASSES:
            y = np.array([res[part][n][c] for n in names], dtype=float)
            if y.any() or c in ("identical", "other"):
                ax.bar(x, y, 0.7, bottom=bottom, color=colc[c], label=labc[c])
            bottom += y
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=40, ha="right", fontsize=7)
        ax.set_title(title, fontsize=7.5)
        ax.set_xlim(-0.7, len(names) - 0.3)
    axs[0].set_ylabel("output files compared")
    axs[0].legend(loc="upper left", fontsize=6.5)
    ax = axs[2]
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"]]
    for (k, v), col in zip(twins.items(), cols):
        y = np.maximum(np.array(v["dx_over_L"]), 1e-17)
        ax.semilogy(v["times"], y, "o-", ms=3, color=col, label=k.replace("-", " vs "))
    if twins:
        ax.axhline(1e-9, color="k", lw=1.0, ls=":")
        ax.set_ylim(1e-17, 1e-8)
        ax.legend(loc="center right", fontsize=6.5)
    else:
        ax.text(0.5, 0.5, "card twins: not run", transform=ax.transAxes, ha="center",
                fontsize=8)
    ax.set_xlabel(r"time $t$")
    ax.set_title(r"card twins: max $|x_{\rm card} - x_{\rm proc}|/L$", fontsize=7.5)
    fs.save(fig, os.path.join(a.out, "t11_merged"))
    with open(os.path.join(a.out, "t11_merged.json"), "w") as f:
        json.dump(res, f, indent=1)
    tot = {p: {c: sum(v[c] for v in res[p].values()) for c in CLASSES} for p in ("a", "b")}
    short = {k: {kk: vv for kk, vv in v.items() if kk not in ("times", "dx_over_L", "du_rel")}
             for k, v in twins.items()}
    print(json.dumps(dict(pass_a=res["pass_a"], pass_b=res["pass_b"],
                          pass_c=res.get("pass_c"), totals=tot, twins=short,
                          not_identical={p: {n: v["details"] for n, v in res[p].items()
                                             if v["details"]} for p in ("a", "b")}), indent=1))


if __name__ == "__main__":
    main()
