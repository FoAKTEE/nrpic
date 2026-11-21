#!/usr/bin/env python3
"""Compare the machine code of two processor builds, object file by object file.

    compare_objects.py <build dir A> <build dir B> [--out results/x.json] [--fig figs/x]
                       [--jobs 6]

For every object file under <build>/src/CMakeFiles/athena.dir the instructions of the
disassembly (objdump -d) are counted by mnemonic.  Two objects whose histograms agree
have the same instructions up to operands (addresses and member offsets may differ); a
different histogram means the compiler generated other code.  Why this exists: a change
of a header that z4c.hpp includes made g++ compile the right-hand side of
z4c_calcrhs.cpp with two more fused multiply-adds, although that file had not changed,
and every run then differed from the release in the last bits (journal entry 12).

Printed and written: the objects present on one side only, the objects whose histograms
differ with the difference of the instruction count and of the number of fused
multiply-adds (vfmadd*, vfmsub*, vfnmadd*, vfnmsub*).  Exit status 0 always: which
differences are expected (changed source files) is for the reader to judge.
"""

import argparse
import collections
import concurrent.futures as cf
import json
import os
import re
import subprocess

FMA = re.compile(r"^vfn?m(add|sub)")


def objects(build):
    root = os.path.join(build, "src", "CMakeFiles", "athena.dir")
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".o"):
                p = os.path.join(d, f)
                out[os.path.relpath(p, root)] = p
    return out


def histogram(path):
    txt = subprocess.run(["objdump", "-d", "--no-show-raw-insn", path],
                         capture_output=True, text=True, check=True).stdout
    h = collections.Counter()
    for ln in txt.splitlines():
        q = ln.split("\t")
        if len(q) >= 2 and q[1].strip():
            h[q[1].split()[0]] += 1
    return h


def main():
    p = argparse.ArgumentParser()
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--out", default="")
    p.add_argument("--fig", default="")
    p.add_argument("--jobs", type=int, default=6)
    a = p.parse_args()
    oa, ob = objects(a.a), objects(a.b)
    both = sorted(set(oa) & set(ob))
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        ha = dict(zip(both, ex.map(histogram, [oa[k] for k in both])))
        hb = dict(zip(both, ex.map(histogram, [ob[k] for k in both])))
    res = {"a": os.path.abspath(a.a), "b": os.path.abspath(a.b), "compared": len(both),
           "only_a": sorted(set(oa) - set(ob)), "only_b": sorted(set(ob) - set(oa)),
           "different": {}}
    for k in both:
        if ha[k] != hb[k]:
            fa = sum(v for m, v in ha[k].items() if FMA.match(m))
            fb = sum(v for m, v in hb[k].items() if FMA.match(m))
            res["different"][k] = {"insns_a": sum(ha[k].values()),
                                   "insns_b": sum(hb[k].values()), "fma_a": fa, "fma_b": fb}
    print(f"{len(both)} objects compared, {len(res['different'])} with another histogram")
    for k, v in res["different"].items():
        print(f"  {k}: instructions {v['insns_a']} / {v['insns_b']}, "
              f"fused multiply-adds {v['fma_a']} / {v['fma_b']}")
    for side in ("only_a", "only_b"):
        if res[side]:
            print(f"  {side}: " + ", ".join(res[side]))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)
    if a.fig:
        import flib  # noqa: F401  (puts python/ on the path)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from nrpic import figstyle as fs
        fs.use_style()
        names = list(res["different"])
        fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH * 0.7, 1.2 + 0.28 * max(len(names), 1)))
        fig.subplots_adjust(left=0.42, right=0.97, bottom=0.25, top=0.85)
        y = range(len(names))
        di = [res["different"][k]["insns_a"] - res["different"][k]["insns_b"] for k in names]
        df = [res["different"][k]["fma_a"] - res["different"][k]["fma_b"] for k in names]
        ax.barh([q - 0.2 for q in y], di, 0.4, color="0.6", label="instructions, A - B")
        ax.barh([q + 0.2 for q in y], df, 0.4, color=fs.PAL["red"],
                label="fused multiply-adds, A - B")
        ax.set_yticks(list(y))
        ax.set_yticklabels(names, fontsize=7)
        ax.set_xscale("symlog", linthresh=10)
        ax.set_xlabel("difference of counts")
        ax.set_title(f"{len(both)} objects compared, {len(names)} differ", fontsize=9)
        ax.legend(fontsize=7, loc="lower right")
        fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
