#!/usr/bin/env python3
"""Reads the runs of mg_cause.sh (journal entry 18, prediction P15) and judges them.

    mg_cause.py DIR [--floor 2e-11] [--out DIR]

DIR/probe/<mb8|mb32>/<O3|plain|ordered|comp>_t<N>/run.log: the printed defects (sum of
squares of the defect after every V cycle; two solves of five V cycles in the one cycle
of the probe). DIR/jeans20/<mode>_t<N>/: the 20-cycle Jeans case, mesh outputs compared
between 1 and 4 threads with omplib.compare_dirs.
Writes mg_cause.json and figs/mg_cause.{png,pdf}; exit status 1 if a part of P15 fails.
"""
import argparse
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import omplib as L  # noqa: E402

MODES = ("plain", "ordered", "comp")
NV = 5                       # V cycles per solve (niteration of the deck)


def defects(log):
    """The printed defects as text (digit for digit) and as numbers, in order."""
    txt = []
    with open(log, errors="replace") as f:
        for ln in f:
            m = re.match(r"MG (initial defect|iteration \d+: defect) = (\S+)", ln)
            if m:
                txt.append(m.group(2))
    return txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--floor", type=float, default=2.0e-11)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    out = a.out or a.dir
    os.makedirs(os.path.join(out, "figs"), exist_ok=True)
    res = {"dir": a.dir, "floor_bound": a.floor, "probe": {}, "jeans20": {}, "verdict": {}}
    fail = {"a": [], "b": [], "c": []}
    for mb in ("mb8", "mb32"):
        runs = {}
        for d in sorted(glob.glob(os.path.join(a.dir, "probe", mb, "*_t*"))):
            name = os.path.basename(d)
            runs[name] = defects(os.path.join(d, "run.log"))
        res["probe"][mb] = runs
        ths = sorted(int(k.split("_t")[1]) for k in runs if k.startswith("plain_t"))
        res["threads"] = ths
        # a: the diagnostic executable without the variable is the threaded build
        for n in [t for t in ths if "O3_t%d" % t in runs]:
            x, o = runs.get("plain_t%d" % n), runs.get("O3_t%d" % n)
            if not x or x != o:
                fail["a"].append("%s t%d" % (mb, n))
        if not any(k.startswith("O3_t") for k in runs):
            fail["a"].append("%s: no run of the threaded build" % mb)
        # b, c: the same digits at every thread count
        for mode in ("ordered", "comp"):
            ref = runs.get("%s_t1" % mode)
            if len(ths) < 2:
                fail["b" if mode == "ordered" else "c"].append("%s: one thread count" % mb)
            for n in ths[1:]:
                x = runs.get("%s_t%d" % (mode, n))
                if not ref or x != ref:
                    nd = sum(p != q for p, q in zip(x or [], ref or []))
                    fail["b" if mode == "ordered" else "c"].append(
                        "%s %s t%d differs from t1 in %d of %d defects" % (
                            mb, mode, n, nd, len(ref or [])))
        # how the plain sum behaves, for the record
        ref = runs.get("plain_t1")
        res["probe"][mb + "_plain_differs"] = {
            "t%d" % n: sum(p != q for p, q in zip(runs.get("plain_t%d" % n, []), ref or []))
            for n in ths[1:]}
    # floors: the last V cycle of each solve
    floors = {}
    for mb in ("mb8", "mb32"):
        for name, txt in res["probe"][mb].items():
            if not isinstance(txt, list) or not txt:
                continue
            v = np.array([float(x) for x in txt])
            ns = len(v)//(NV + 1)
            fl = [float(v[(s + 1)*(NV + 1) - 1]) for s in range(ns)]
            floors["%s/%s" % (mb, name)] = fl
    res["floors"] = floors
    for key, fl in floors.items():
        if "/comp_" in key and max(fl) > a.floor:
            fail["c"].append("floor of %s: %.3e above %.1e" % (key, max(fl), a.floor))
    f8, f32 = floors.get("mb8/comp_t1"), floors.get("mb32/comp_t1")
    if f8 and f32:
        ratio = max(max(f8)/max(f32), max(f32)/max(f8))
        res["comp_floor_ratio_mb"] = ratio
        if ratio > 2.0:
            fail["c"].append("floors of the MeshBlock sizes differ by %.2f" % ratio)
    # the 20-cycle case: files at 4 threads against one thread, per mode
    for mode in MODES:
        dd = sorted(glob.glob(os.path.join(a.dir, "jeans20", "%s_t*" % mode)),
                    key=lambda d: int(d.rsplit("_t", 1)[1]))
        if len(dd) >= 2:
            d1, d4 = dd[0], dd[-1]
            res.setdefault("jeans20_threads", [int(d.rsplit("_t", 1)[1]) for d in dd])
            r = L.compare_dirs(d1, d4)
            r["defects_identical"] = defects(os.path.join(d1, "run.log")) == \
                defects(os.path.join(d4, "run.log"))
            res["jeans20"][mode] = r
            data = {k: v for k, v in r["differ"].items() if v.get("kind") != "log"}
            if mode != "plain" and (data or not r["defects_identical"]):
                fail["b" if mode == "ordered" else "c"].append(
                    "jeans20 %s: %d files differ between the thread counts (rel_max %.2e), "
                    "defects identical: %s" % (mode, len(data), r["worst_rel_max"],
                                               r["defects_identical"]))
    for k in "abc":
        res["verdict"][k] = {"holds": not fail[k], "failures": fail[k]}
    L.dump(res, os.path.join(out, "mg_cause.json"))
    # ---- table
    for mb in ("mb8", "mb32"):
        print("MeshBlocks %s: defects after V cycles 3, 4, 5 of solve 1 and of solve 2" % mb)
        for name, txt in sorted(res["probe"][mb].items()):
            if isinstance(txt, list) and len(txt) >= 2*(NV + 1):
                print("  %-12s %s | %s" % (name, " ".join(txt[3:6]), " ".join(txt[9:12])))
    for mode, r in res["jeans20"].items():
        data = {k: v for k, v in r["differ"].items() if v.get("kind") != "log"}
        print("jeans20 %-8s %s threads: %2d files identical, %2d differ, rel_max "
              "%.2e, defects identical: %s" % (mode, res.get("jeans20_threads"),
                                             len(r["identical"]), len(data),
                                             r["worst_rel_max"], r["defects_identical"]))
    for k in "abc":
        print("P15%s: %s %s" % (k, "HOLDS" if not fail[k] else "FAILS", "; ".join(fail[k])))
    figure(res, os.path.join(out, "figs", "mg_cause"))
    return 1 if any(fail.values()) else 0


def figure(res, out):
    """One panel per way of summing the mean; the printed defect against the V cycle
    (the two solves of the cycle one after the other; 0 and 6 are the defects before the
    first V cycle of a solve), one colour per thread count, full lines MeshBlocks of 8^3,
    dashed 32^3."""
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.3), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.15, top=0.90, wspace=0.06)
    title = {"plain": "plain sum (the code)", "ordered": "fixed order",
             "comp": "fixed order, compensated"}
    cols = {1: "0.15", 2: fs.SERIES[0], 4: fs.SERIES[1], 6: fs.SERIES[3]}
    for ax, mode in zip(axs, MODES):
        for mb, ls in (("mb8", "-"), ("mb32", "--")):
            for n in res.get("threads", [1, 2, 4, 6]):
                txt = res["probe"][mb].get("%s_t%d" % (mode, n))
                if not txt:
                    continue
                v = np.array([float(x) for x in txt])
                ax.plot(np.arange(len(v)), v, ls, color=cols[n], lw=1.3,
                        marker="o" if mb == "mb8" else "s", ms=3.5,
                        mfc=cols[n] if mb == "mb8" else "none",
                        label=("%d thread%s" % (n, "" if n == 1 else "s"))
                        if mb == "mb8" else None)
        ax.set_yscale("log")
        ax.set_title(title[mode], fontsize=9)
        ax.set_xlabel("V cycle (two solves)")
        ax.axvline(NV + 0.5, **fs.MASK_LINE)
        ax.set_xticks(range(0, 2*(NV + 1), 2))
        ax.minorticks_off()
    axs[0].set_ylabel(r"printed defect, $\sum d^2$")
    axs[0].plot([], [], "--", color="0.5", marker="s", mfc="none", ms=3.5,
                label=r"MeshBlocks $32^3$ (full: $8^3$)")
    axs[0].legend(loc="lower left", fontsize=7)
    fs.save(fig, out)
    print("wrote", out + ".png")


if __name__ == "__main__":
    sys.exit(main())
