#!/usr/bin/env python3
"""V6b: aligned comparison of the straight (A) and restarted (B) runs of V6.

V6 (run core-20261121-213713-952a0c4) compared files byte for byte from the start; the
restart files of B carry a parameter text of another length, and B's trajectory files
hold only the records after the restart. Here:
- restart files: the parameter texts (up to '<par_end>') are compared line by line; the
  binary parts after it are compared byte for byte and, as float64 words, by value
  (largest absolute and relative difference, number of words that differ);
- trajectory files (records of 8 or 17 float64): B's records against A's records of
  the same time and tag.

usage: v6b_compare.py V6_RUNDIR OUTDIR
"""
import json
import os
import sys

import numpy as np


def split_rst(path):
    b = open(path, "rb").read()
    h = b.find(b"<par_end>") + 10
    return b[:h].decode("latin1"), b[h:]


def cmp_rst(pa, pb):
    ta, da = split_rst(pa)
    tb, db = split_rst(pb)
    la, lb = ta.splitlines(), tb.splitlines()
    only_a = [x for x in la if x not in lb]
    only_b = [x for x in lb if x not in la]
    out = {"param_lines_only_A": only_a[:20], "param_lines_only_B": only_b[:20],
           "binary_sizes": [len(da), len(db)], "binary_identical": da == db}
    if da != db and len(da) == len(db):
        n = len(da) // 8
        a = np.frombuffer(da[:8 * n], "<f8")
        b = np.frombuffer(db[:8 * n], "<f8")
        diff = a != b
        fin = np.isfinite(a) & np.isfinite(b)
        d = np.abs(a - b)[diff & fin]
        rel = (np.abs(a - b) / np.maximum(np.abs(a), 1e-300))[diff & fin]
        out.update({"n_words": int(n), "n_words_differ": int(diff.sum()),
                    "first_word_differ": int(np.argmax(diff)) if diff.any() else None,
                    "max_abs_diff": float(d.max()) if d.size else 0.0,
                    "max_rel_diff": float(rel.max()) if rel.size else 0.0,
                    "median_rel_diff_of_differing": float(np.median(rel)) if rel.size else 0.0})
    return out


def cmp_traj(pa, pb, width):
    a = np.fromfile(pa, "<f8").reshape(-1, width)
    b = np.fromfile(pb, "<f8").reshape(-1, width)
    ka = {(r[0], r[1]): i for i, r in enumerate(a)}
    idx = [ka.get((r[0], r[1])) for r in b]
    found = [i for i in idx if i is not None]
    miss = sum(1 for i in idx if i is None)
    sel = np.array([i is not None for i in idx])
    d = np.abs(a[found] - b[sel])
    return {"records_B": int(len(b)), "matched": int(len(found)), "unmatched": int(miss),
            "identical": bool(len(found) == len(b) and np.all(d == 0)),
            "max_abs_diff": float(d.max()) if d.size else None}


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for case in ("east", "os"):
        A, B = os.path.join(rd, case, "A"), os.path.join(rd, case, "B")
        r = {}
        for name in sorted(os.listdir(os.path.join(B, "rst"))):
            if name.endswith(".rst") and os.path.exists(os.path.join(A, "rst", name)):
                r[name] = cmp_rst(os.path.join(A, "rst", name), os.path.join(B, "rst", name))
        for fn, w in ((f"{case}.traj.bin", 8), (f"{case}.trajmet.bin", 17)):
            if os.path.exists(os.path.join(B, fn)):
                r[fn] = cmp_traj(os.path.join(A, fn), os.path.join(B, fn), w)
        res[case] = r
    with open(os.path.join(outdir, "v6b_compare.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 2.8))
    labels, vals, cols = [], [], []
    for i, (case, r) in enumerate(res.items()):
        for name, c in r.items():
            if "binary_identical" in c:
                v = 1e-18 if c["binary_identical"] else max(c.get("max_rel_diff", 1.0), 1e-18)
                labels.append(f"{case}: {name} (mesh+state)")
            else:
                v = 1e-18 if c["identical"] else max(c["max_abs_diff"] or 1.0, 1e-18)
                labels.append(f"{case}: {name}")
            vals.append(v)
            cols.append(fs.SERIES[i])
    y = np.arange(len(labels))
    ax.barh(y, vals, color=cols)
    ax.set_xscale("log")
    ax.set_xlim(1e-18, 1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel("largest difference restarted vs straight (relative for restart files; 1e-18 = identical)")
    ax.set_title("V6b: restart on release core-v0.6 (run core-20261121-213713-952a0c4), aligned comparison", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v6b_compare"))


if __name__ == "__main__":
    main()
