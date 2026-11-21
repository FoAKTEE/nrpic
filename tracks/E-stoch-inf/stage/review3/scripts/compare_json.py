#!/usr/bin/env python3
"""Lead review of wave 3 (E-stoch-inf): compare JSON outputs leaf by leaf.

    compare_json.py --out DIR name="NEW|REGISTERED|COMMITTED" [...]

For each item: NEW (the lead's rerun) against REGISTERED (the helper's run directory), and
COMMITTED (the copy in the package) against REGISTERED.  Numeric leaves: relative
difference |a - b| / max(|a|, |b|) (0 when both are 0; NaN equal to NaN); other leaves:
equality.  Leaves whose key holds a path or a run directory ("run", "dir", "path", ...) are
listed separately, since a rerun writes other paths.  Writes compare.json and
fig_rerun.png/pdf (largest relative difference per item).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PATHLIKE = ("run", "dir", "path", "file", "out", "res", "rundir", "exe", "date", "time_utc")


def leaves(x, pre=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{pre}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{pre}[{i}]")
    else:
        yield pre, x


def pathlike(key):
    last = key.rsplit("/", 1)[-1].split("[")[0].lower()
    return any(last == p or last.endswith("_" + p) or last.startswith(p + "_") for p in PATHLIKE)


def compare(a, b):
    la, lb = dict(leaves(a)), dict(leaves(b))
    only_a = sorted(set(la) - set(lb))
    only_b = sorted(set(lb) - set(la))
    nnum = ndiff_num = nother = ndiff_other = 0
    maxrel, maxkey = 0.0, None
    diffs_other, diffs_path = [], []
    for k in sorted(set(la) & set(lb)):
        x, y = la[k], lb[k]
        if isinstance(x, bool) or isinstance(y, bool) or not (
                isinstance(x, (int, float)) and isinstance(y, (int, float))):
            nother += 1
            if x != y:
                (diffs_path if pathlike(k) else diffs_other).append([k, str(x)[:80], str(y)[:80]])
                if not pathlike(k):
                    ndiff_other += 1
            continue
        nnum += 1
        if (isinstance(x, float) and math.isnan(x)) and (isinstance(y, float) and math.isnan(y)):
            continue
        if x == y:
            continue
        den = max(abs(x), abs(y))
        rel = abs(x - y) / den if den > 0 else 0.0
        if math.isnan(rel) or math.isinf(rel):
            rel = float("inf")
        ndiff_num += 1
        if rel > maxrel:
            maxrel, maxkey = rel, k
    return dict(numeric_leaves=nnum, numeric_differing=ndiff_num, max_rel=maxrel,
                max_rel_key=maxkey, other_leaves=nother, other_differing=ndiff_other,
                other_diffs=diffs_other[:10], path_diffs=len(diffs_path),
                path_diff_examples=diffs_path[:3], only_in_first=only_a[:10],
                only_in_second=only_b[:10], n_only_first=len(only_a), n_only_second=len(only_b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("items", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for it in a.items:
        name, spec = it.split("=", 1)
        new, reg, com = spec.split("|")
        J = {}
        for tag, p in (("new", new), ("registered", reg), ("committed", com)):
            J[tag] = json.load(open(p)) if os.path.exists(p) else None
        r = dict(files=dict(new=new, registered=reg, committed=com))
        if J["new"] is not None and J["registered"] is not None:
            r["new_vs_registered"] = compare(J["new"], J["registered"])
        else:
            r["new_vs_registered"] = "missing file"
        if J["committed"] is not None and J["registered"] is not None:
            r["committed_vs_registered"] = compare(J["committed"], J["registered"])
        else:
            r["committed_vs_registered"] = "missing file"
        res[name] = r
        nv = r["new_vs_registered"]
        cv = r["committed_vs_registered"]
        def fmt(c):
            if isinstance(c, str):
                return c
            return (f"num {c['numeric_differing']}/{c['numeric_leaves']} differ, max rel "
                    f"{c['max_rel']:.3g} ({c['max_rel_key']}); other {c['other_differing']}/"
                    f"{c['other_leaves']}; paths {c['path_diffs']}; keys only "
                    f"{c['n_only_first']}/{c['n_only_second']}")
        print(f"{name}: new vs registered: {fmt(nv)}")
        print(f"{' ' * len(name)}  committed vs registered: {fmt(cv)}")
    with open(os.path.join(a.out, "compare.json"), "w") as fp:
        json.dump(res, fp, indent=1)

    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    names = list(res)
    floor = 1e-18

    def val(c):
        if isinstance(c, str):
            return np.nan
        return max(c["max_rel"], floor)
    v_new = [val(res[n]["new_vs_registered"]) for n in names]
    v_com = [val(res[n]["committed_vs_registered"]) for n in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 0.45 * fs.FULL_WIDTH))
    ax.bar(x - 0.2, v_new, 0.4, label="lead's rerun vs registered output")
    ax.bar(x + 0.2, v_com, 0.4, label="committed copy vs registered output")
    ax.set_yscale("log")
    ax.set_ylim(floor / 3, 1.0)
    ax.axhline(1e-12, color="0.5", ls=":", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("largest relative difference\n(bars at 1e-18 = identical)")
    ax.set_title("Wave-3 review: reruns of g1verify and ladder analyses")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_rerun"))


if __name__ == "__main__":
    main()
