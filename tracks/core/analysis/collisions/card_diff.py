#!/usr/bin/env python3
"""How large are the byte differences between two card runs of the same collisional box
test (new executable against the release one, options absent)?

  card_diff.py OUT SUMMARY.json [--tests rate,relax,repro,conv_dt,curved]

SUMMARY.json is the file `rerun_wave1.py --card --base ...` writes: for every test the
run id of the new executable ("run_id"), that of the release executable ("wave1_run")
and the list of files that differ. For every differing file:
  particle snapshot  particles matched by tag; number that differ; largest |dx| and
                     largest |du|/max(1, |u|)
  collision history  every integer column (counts) compared row by row; for the
                     floating-point columns the largest difference relative to the
                     column's scale
  NRPIC history      largest difference of every column relative to its scale
Also: the index of the first differing snapshot of each run (the snapshot 0 is the
initial state, written before any step). Writes OUT/card_diff.json and
OUT/fig_card_diff.png. Exit status 0 if every integer column agrees and every
snapshot difference is below 1e-12 (the bound of the prediction in JOURNAL-coll2.md,
2026-11-19).
"""
import argparse
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

SCRATCH = "/data/haiyangw/nrpic/scratch/core"
INT_COLS = ["ncycle", "n_part", "n_cells", "n_tested", "n_coll", "n_updated", "n_trunc",
            "max_nsub", "min_N", "n_bad_cells"]
BOUND = 1e-12


def table(path):
    rows = []
    with open(path) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            rows.append([float(v) for v in line.split()])
    return np.array(rows)


def cmp_snapshot(pa, pb):
    a, b = collide.read_snapshot(pa), collide.read_snapshot(pb)
    if a["n"] != b["n"]:
        return dict(n_a=int(a["n"]), n_b=int(b["n"]), same_count=False)
    ia, ib = np.argsort(a["tag"]), np.argsort(b["tag"])
    same_tags = bool(np.array_equal(a["tag"][ia], b["tag"][ib]))
    dx = np.abs(a["x"][ia] - b["x"][ib]).max(axis=1)
    scale = np.maximum(1.0, np.linalg.norm(b["u"][ib], axis=1))
    du = np.abs(a["u"][ia] - b["u"][ib]).max(axis=1)/scale
    differ = (dx > 0) | (du > 0) | (a["m"][ia] != b["m"][ib])
    return dict(same_count=True, same_tags=same_tags, n=int(a["n"]),
                n_differ=int(np.count_nonzero(differ)), max_dx=float(dx.max()),
                max_du_rel=float(du.max()), time=float(a["time"]))


def cmp_coll_hst(pa, pb):
    a, b = collide.read_history(pa), collide.read_history(pb)
    out = dict(rows=[len(a["time"]), len(b["time"])], int_columns_differ=[],
               float_columns={})
    for k in a:
        if k not in b or len(a[k]) != len(b[k]):
            out["int_columns_differ"].append(k + " (missing or length)")
            continue
        if k in INT_COLS:
            if not np.array_equal(a[k], b[k]):
                out["int_columns_differ"].append(k)
        elif not np.array_equal(a[k], b[k]):
            scale = max(float(np.max(np.abs(b[k]))), 1e-300)
            out["float_columns"][k] = float(np.max(np.abs(a[k] - b[k]))/scale)
    return out


def cmp_table(pa, pb):
    a, b = table(pa), table(pb)
    if a.shape != b.shape:
        return dict(shape=[list(a.shape), list(b.shape)])
    cols = {}
    for j in range(a.shape[1]):
        if not np.array_equal(a[:, j], b[:, j]):
            scale = max(float(np.max(np.abs(b[:, j]))), 1e-300)
            cols[str(j + 1)] = float(np.max(np.abs(a[:, j] - b[:, j]))/scale)
    return dict(shape=list(a.shape), columns_differ=cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("summary")
    ap.add_argument("--tests", default="rate,relax,repro,conv_dt,curved")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    summ = json.load(open(args.summary))
    res, ok = {}, True
    curves = {}
    for t in args.tests.split(","):
        key = f"{t}_vs_release"
        s = summ[key]
        new, base = (os.path.join(SCRATCH, s["run_id"]), os.path.join(SCRATCH, s["wave1_run"]))
        r = dict(new=s["run_id"], base=s["wave1_run"], files_differ=len(s["files_differ"]),
                 snapshots={}, coll_hst={}, nrpic_hst={}, other=[])
        for f in s["files_differ"]:
            pa, pb = os.path.join(new, f), os.path.join(base, f)
            if ".part." in f and f.endswith(".bin"):
                r["snapshots"][f] = cmp_snapshot(pa, pb)
            elif f.endswith(".coll.hst"):
                r["coll_hst"][f] = cmp_coll_hst(pa, pb)
            elif f.endswith(".nrpic.hst"):
                r["nrpic_hst"][f] = cmp_table(pa, pb)
            else:
                r["other"].append(f)
        # first differing snapshot per run directory
        first = {}
        for f in r["snapshots"]:
            d, b = os.path.split(f)
            idx = int(b.split(".")[-2])
            first[d] = min(first.get(d, idx), idx)
        r["first_differing_snapshot"] = first
        snap = list(r["snapshots"].values())
        r["max_dx"] = max([v.get("max_dx", 0.0) for v in snap], default=0.0)
        r["max_du_rel"] = max([v.get("max_du_rel", 0.0) for v in snap], default=0.0)
        r["int_columns_differ"] = sorted({c for v in r["coll_hst"].values()
                                          for c in v["int_columns_differ"]})
        r["max_float_rel"] = {}
        for v in r["coll_hst"].values():
            for c, x in v["float_columns"].items():
                r["max_float_rel"][c] = max(r["max_float_rel"].get(c, 0.0), x)
        r["counts_identical"] = not r["int_columns_differ"]
        r["all_tags_same"] = all(v.get("same_tags", False) for v in snap)
        r["ok"] = bool(r["counts_identical"] and r["all_tags_same"]
                       and r["max_dx"] < BOUND and r["max_du_rel"] < BOUND)
        ok = ok and r["ok"]
        res[t] = r
        curves[t] = sorted((v["time"], v["max_du_rel"]) for v in snap)
        print(f"{t:8s} differ {r['files_differ']:4d}  counts identical {r['counts_identical']}  "
              f"max |dx| {r['max_dx']:.2e}  max |du|/max(1,|u|) {r['max_du_rel']:.2e}  "
              f"float columns {sorted(r['max_float_rel'])}  other {r['other'][:3]}")
    res["ok"] = bool(ok)
    with open(os.path.join(out, "card_diff.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print("ok:", ok)

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.95, wspace=0.32)
    pal = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["yellow"]]
    allc = sorted({c for t in curves for c in res[t]["max_float_rel"]})
    for k, t in enumerate(curves):
        v = np.array([x[1] for x in curves[t]])
        if v.size:
            axs[0].hist(np.log10(np.maximum(v, 1e-20)), bins=np.linspace(-20, -10, 41),
                        histtype="step", color=pal[k % len(pal)], label=t)
        cols = res[t]["max_float_rel"]
        if cols:
            axs[1].plot([allc.index(c) + 0.1*(k - 2) for c in cols],
                        [np.log10(max(cols[c], 1e-30)) for c in cols],
                        "o", color=pal[k % len(pal)], ms=3, label=t)
    axs[0].axvline(np.log10(BOUND), **fs.GUIDE)
    axs[0].set_xlabel(r"$\log_{10}$ max $|\Delta u|/\max(1,|u|)$ of a snapshot")
    axs[0].set_ylabel("differing snapshots")
    axs[0].legend(fontsize=7)
    axs[1].set_ylabel(r"$\log_{10}$ max rel. difference")
    axs[1].set_xticks(np.arange(len(allc)))
    axs[1].set_xticklabels(allc, rotation=60, ha="right", fontsize=5)
    fig.subplots_adjust(bottom=0.3)
    fig.savefig(os.path.join(out, "fig_card_diff.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
