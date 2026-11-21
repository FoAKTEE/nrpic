#!/usr/bin/env python3
"""Item (a) of wave 3 (JOURNAL entries 12 and 15): compares the time-matched pairs and
verdicts (results/final2) with those of waves 2 and 2b (results/final).

    compare_final2.py --old DIR --new DIR --out DIR [--reader-check DUMP]

- every pair present in both: rows matched by the dump index of the s = +1 run; largest
  relative difference of each quantity; rows present only in the old file (dropped);
- summary.json: every verdict (pass_), every maximum of A4 and of the negative control, the
  halving lists (entries matched by time) and A5;
- --reader-check: the sequential reader against the memory-map reader of waves 2-2b on one
  dump (largest absolute difference of every variable);
- figure fig_halving_fix.png: the halving factors of the parts of H, old and new.
"""
import argparse
import glob
import json
import os

import numpy as np

import ladder_lib as LL

KEYS = ("H_odd", "H_even", "H_even_mean", "M_odd", "M_even", "ratio_H_p", "ratio_H_m",
        "ratio_M_p", "ratio_M_m", "Hmag", "Mmag", "efolds", "time")


def rel(a, b):
    a, b = float(a), float(b)
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


def compare_pairs(old, new):
    out = {}
    for f in sorted(glob.glob(os.path.join(new, "pair_*.json"))):
        name = os.path.basename(f)[5:-5]
        fo = os.path.join(old, os.path.basename(f))
        if not os.path.isfile(fo):
            continue
        rn = json.load(open(f))
        ro = json.load(open(fo))
        new_by = {r["dump"]: r for r in rn["rows"]}
        diffs = {k: 0.0 for k in KEYS}
        dropped_old = []
        for r in ro["rows"]:
            q = new_by.get(r["dump"])
            if q is None:
                dropped_old.append(dict(dump=r["dump"], time=r["time"], cycle=r["cycle"],
                                        H_even=r["H_even"], H_odd=r["H_odd"]))
                continue
            for k in KEYS:
                diffs[k] = max(diffs[k], rel(r[k], q[k]))
        out[name] = dict(rows_old=len(ro["rows"]), rows_new=len(rn["rows"]),
                         max_rel_diff=diffs, dropped_rows_of_old=dropped_old,
                         dropped_in_new=rn.get("dropped", []))
    return out


def walk(a, b, path=""):
    """Leaves of two nested dicts that differ (numbers by relative difference)."""
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                diffs.append(dict(key=f"{path}/{k}", old=a.get(k, "absent"),
                                  new=b.get(k, "absent")))
            else:
                diffs += walk(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(dict(key=path, old=a, new=b, note="length differs"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diffs += walk(x, y, f"{path}[{i}]")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        if rel(a, b) > 1e-12:
            diffs.append(dict(key=path, old=a, new=b, rel=rel(a, b)))
    elif a != b:
        diffs.append(dict(key=path, old=a, new=b))
    return diffs


PAIR_OF = {"N32": "L32p_L32m", "N64": "Q64p_Q64m", "N128": "Q128p_Q128m"}


def figure(old_s, new_s, olddir, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    col = {"N32": fs.PAL["yellow"], "N64": fs.PAL["green"], "N128": fs.PAL["blue"]}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.9, wspace=0.22)
    for tag, c in col.items():
        o, n = old_s["A4"].get(tag, {}), new_s["A4"].get(tag, {})
        if "halving_even_H" not in o or "halving_even_H" not in n:
            continue
        rows_old = json.load(open(os.path.join(olddir, f"pair_{PAIR_OF[tag]}.json")))["rows"]
        xo = [rows_old[i]["time"] for i in range(1, len(o["halving_even_H"]) + 1)]
        axs[0].plot(xo, o["halving_even_H"], "x:", color=c, ms=5, label=f"{tag} waves 2-2b")
        axs[0].plot(n["halving_times"], n["halving_even_H"], "s-", color=c, ms=3,
                    label=f"{tag} time-matched")
        axs[1].plot(xo, o["halving_odd_H"], "x:", color=c, ms=5)
        axs[1].plot(n["halving_times"], n["halving_odd_H"], "o-", color=c, ms=3)
    axs[0].axhline(4, **fs.GUIDE)
    axs[1].axhline(2, **fs.GUIDE)
    axs[0].set_ylim(0, 17)
    axs[0].set_ylabel(r"even part of $\mathcal{H}$: factor $s=1$ / $s=1/2$")
    axs[1].set_ylabel(r"odd part of $\mathcal{H}$: factor $s=1$ / $s=1/2$")
    for ax in axs:
        ax.set_xlabel(r"time $t$ of the $s=1$ run")
    axs[0].legend(fontsize=6, ncol=2, loc="upper left")
    axs[0].set_title("crosses: paired by index (waves 2-2b); lines: by time", fontsize=8)
    fs.save(fig, os.path.join(outdir, "fig_halving_fix"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reader-check")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(pairs=compare_pairs(a.old, a.new))
    old_s = json.load(open(os.path.join(a.old, "summary.json")))
    new_s = json.load(open(os.path.join(a.new, "summary.json")))
    res["summary_differences"] = walk(old_s, new_s)
    res["verdicts"] = {k: dict(old=old_s[k].get("pass_") if isinstance(old_s[k], dict) else None,
                               new=new_s[k].get("pass_") if isinstance(new_s[k], dict) else None)
                       for k in ("A1",)}
    for key in ("A2", "A3"):
        res["verdicts"][key] = {r: dict(old=old_s[key][r].get("pass_"),
                                        new=new_s[key][r].get("pass_"))
                                for r in old_s[key]}
    if a.reader_check:
        h = LL.read_header(a.reader_check)
        _, f1 = LL.read_dump(a.reader_check, h["names"])
        _, f2 = LL.read_dump_memmap(a.reader_check, h["names"])
        res["reader_check"] = dict(dump=a.reader_check, max_abs_diff={
            n: float(np.abs(f1[n] - f2[n]).max()) for n in h["names"]})
    with open(os.path.join(a.out, "compare.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=float)
    figure(old_s, new_s, a.old, a.out)
    for name, p in res["pairs"].items():
        print(f"pair {name}: rows {p['rows_old']} -> {p['rows_new']}, max rel diff "
              + ", ".join(f"{k} {v:.1e}" for k, v in p["max_rel_diff"].items() if v)
              + f"; dropped rows of the old file {[(d['time'], d['cycle']) for d in p['dropped_rows_of_old']]}"
              + f"; dropped in new {[(d['run'], d['time']) for d in p['dropped_in_new']]}")
    print(f"summary.json: {len(res['summary_differences'])} differing leaves")
    for d in res["summary_differences"]:
        print("  ", d)
    if "reader_check" in res:
        print("reader check:", max(res["reader_check"]["max_abs_diff"].values()))


if __name__ == "__main__":
    main()
