#!/usr/bin/env python3
"""LEDGER, counts and figures of package claims3 from its committed inputs and its runs.

    python3 ledger.py --runs W2=RUN W3=RUN W1=RUN W4=RUN W5=RUN DRAW=RUN [--out DIR]

Inputs: plans/plan_item{1..4}.json, SAMPLE_VERDICTS.tsv, the draw run's weak_draw.json and
weak_sample.tsv, the write runs' before.tsv / after.tsv / result.json / others.json, the
item-5 run's downloads_item5.json (all under scratch/kb/<run_id>/). Writes into --out (the run
directory; the package copies them after the run): LEDGER.tsv (one row per claim touched or
created), counts.json (rates, Clopper-Pearson intervals, stratum-weighted estimate, action
counts), fig_weak_sample.{png,pdf}, fig_actions.{png,pdf}.
Needs numpy, scipy, matplotlib (the worktree's .venv).
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
SCRATCH = "/data/haiyangw/nrpic/scratch/kb"
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def tsv(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    if not a.out:
        ap.error("no output directory (run under nrpic-run or give --out)")
    os.makedirs(a.out, exist_ok=True)
    runs = dict(x.split("=", 1) for x in a.runs)
    # ---------------------------------------------------------------- sample rate
    ver = tsv(os.path.join(PKG, "SAMPLE_VERDICTS.tsv"))
    draw = json.load(open(os.path.join(SCRATCH, runs["DRAW"], "weak_draw.json")))
    sample_ids = {int(r["claim_id"]) for r in tsv(os.path.join(SCRATCH, runs["DRAW"], "weak_sample.tsv"))}
    assert sample_ids == {int(r["claim_id"]) for r in ver}, "verdicts do not cover the drawn sample"
    n = len(ver)
    k = sum(int(r["right"]) for r in ver)
    strata = draw["strata"]
    W = sum(strata.values())
    per = {}
    for s in sorted(strata):
        rs = [r for r in ver if r["stratum"] == s]
        ks = sum(int(r["right"]) for r in rs)
        per[s] = {"N": strata[s], "n": len(rs), "right": ks, "cp95": cp(ks, len(rs)) if rs else None}
    weighted = sum(strata[s] / W * per[s]["right"] / per[s]["n"] for s in per if per[s]["n"])
    # stratified variance (finite-population correction) of the weighted proportion
    var = 0.0
    for s in per:
        ns, Ns = per[s]["n"], strata[s]
        if ns > 1:
            p = per[s]["right"] / ns
            var += (Ns / W) ** 2 * p * (1 - p) / (ns - 1) * (1 - ns / Ns)
    kinds = {}
    for r in ver:
        kinds[r["verdict"]] = kinds.get(r["verdict"], 0) + 1
    # ---------------------------------------------------------------- ledger
    item_of = {"W2": "2 supersede (first case)", "W3": "3 weak-class sample", "W1": "1 brief seeds 803, 805",
               "W4": "4 fragments"}
    rows, actions = [], {}
    for w in ("W2", "W3", "W1", "W4"):
        rid = runs[w]
        plan = json.load(open(os.path.join(PKG, "plans", f"plan_item{w[1]}.json")))
        res = json.load(open(os.path.join(SCRATCH, rid, "result.json")))
        oth = json.load(open(os.path.join(SCRATCH, rid, "others.json")))
        assert oth["agree"], f"{w}: other claims changed"
        before = {int(r["claim_id"]): r for r in tsv(os.path.join(SCRATCH, rid, "before.tsv"))}
        after = {int(r["claim_id"]): r for r in tsv(os.path.join(SCRATCH, rid, "after.tsv"))}
        acts = plan["actions"]
        for x, r in zip(acts, res["results"]):
            do = x["do"]
            if do == "supersede":
                do = "supersede (new claim)" if "text" in x else "supersede (existing)"
            actions.setdefault(w, {}).setdefault(do, 0)
            actions[w][do] += 1
            cid = x.get("id", r.get("new"))
            succ = r.get("new", "") if x["do"] in ("supersede", "add") else ""
            b, f = before.get(cid, {}), after.get(cid, {})
            rows.append({"claim_id": cid, "item": item_of[w], "action": do,
                         "label_before": b.get("label", ""), "status_before": b.get("status", ""),
                         "label_after": f.get("label", ""), "status_after": f.get("status", ""),
                         "successor": succ if succ != cid else "",
                         "loc_rows": f.get("loc_rows", ""), "loc_resolved": f.get("loc_resolved", ""),
                         "locator": f.get("locator", ""), "evidence": x.get("evidence", "")[:400].replace("\t", " "),
                         "run_id": rid})
            if x["do"] in ("supersede", "add") and r.get("new") and (x.get("text") or x["do"] == "add"):
                g = after.get(r["new"], {})
                rows.append({"claim_id": r["new"], "item": item_of[w], "action": "new claim",
                             "label_before": "", "status_before": "", "label_after": g.get("label", ""),
                             "status_after": g.get("status", ""), "successor": "",
                             "loc_rows": g.get("loc_rows", ""), "loc_resolved": g.get("loc_resolved", ""),
                             "locator": g.get("locator", ""), "evidence": (x.get("text") or "")[:400],
                             "run_id": rid})
    cols = ("claim_id", "item", "action", "label_before", "status_before", "label_after", "status_after",
            "successor", "loc_rows", "loc_resolved", "locator", "evidence", "run_id")
    with open(os.path.join(a.out, "LEDGER.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    dl = json.load(open(os.path.join(SCRATCH, runs["W5"], "downloads_item5.json")))
    counts = {"sample": {"n": n, "right": k, "rate": k / n, "cp95": cp(k, n), "kinds": kinds, "strata": per,
                         "W": W, "weighted_rate": weighted, "weighted_se": var ** 0.5,
                         "not_right_cp95": cp(n - k, n)},
              "actions": actions, "ledger_rows": len(rows),
              "downloads": {k2: dl[k2] for k2 in ("rows_before", "rows_after", "ids_after", "files_unchanged",
                                                   "problem_rows_after", "predictions_hold")},
              "runs": runs}
    json.dump(counts, open(os.path.join(a.out, "counts.json"), "w"), indent=1)
    # ---------------------------------------------------------------- figures
    fs.use_style()
    figdir = a.out
    order = ["WA", "WQ", "WB", "WM"]
    cats = [("right", "right", fs.PAL["blue"]), ("right_locator", "right, locator extended", "#8fb3d9"),
            ("fragment", "fragment", fs.PAL["red"]), ("part_unsupported", "part unsupported", fs.PAL["orange"]),
            ("wrong_label", "cut text, wrong label", fs.PAL["yellow"])]
    fig = plt.figure(figsize=(8, 3.2))
    ax = fig.add_axes([0.08, 0.17, 0.50, 0.72])
    x = np.arange(len(order))
    bottom = np.zeros(len(order))
    for key, lab, col in cats:
        v = np.array([sum(1 for r in ver if r["stratum"] == s and r["verdict"] == key) for s in order], float)
        ax.bar(x, v, 0.6, bottom=bottom, color=col, label=lab)
        bottom += v
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n(N = {strata[s]})" for s in order])
    ax.set_ylabel("claims in the sample")
    ax.set_title("Weak class: 30 claims re-read at their locators")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    ax2 = fig.add_axes([0.68, 0.17, 0.29, 0.72])
    lo, hi = cp(k, n)
    ax2.errorbar([0], [k / n], yerr=[[k / n - lo], [hi - k / n]], fmt="o", color=fs.PAL["red"], capsize=4,
                 label=f"sample {k}/{n}")
    se = var ** 0.5
    ax2.errorbar([1], [weighted], yerr=[[1.96 * se], [min(1.96 * se, 1 - weighted)]], fmt="s", color=fs.PAL["blue"],
                 capsize=4, label="stratum-weighted")
    ax2.set_xlim(-0.6, 1.6)
    ax2.set_ylim(0.5, 1.02)
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["CP 95 %", "+-1.96 s.e."])
    ax2.set_ylabel("fraction right as worded")
    ax2.legend(frameon=False, loc="lower left", fontsize=8)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(figdir, f"fig_weak_sample.{ext}"), dpi=150)
    plt.close(fig)
    kinds_order = ["verify", "relocate", "annotate", "add", "supersede (new claim)", "supersede (existing)",
                   "withdraw"]
    colors = [fs.PAL["blue"], "#8fb3d9", "0.6", fs.PAL["green"], fs.PAL["red"], fs.PAL["orange"], "k"]
    ws = ["W2", "W3", "W1", "W4"]
    fig = plt.figure(figsize=(8, 3.0))
    ax = fig.add_axes([0.08, 0.2, 0.62, 0.68])
    bottom = np.zeros(len(ws))
    for kd, col in zip(kinds_order, colors):
        v = np.array([actions.get(w, {}).get(kd, 0) for w in ws], float)
        if v.any():
            ax.bar(np.arange(len(ws)), v, 0.6, bottom=bottom, color=col, label=kd)
            bottom += v
    ax.set_xticks(np.arange(len(ws)))
    ax.set_xticklabels(["2: 682 -> 862", "3: sample", "1: seeds", "4: fragments"])
    ax.set_ylabel("actions")
    ax.set_title("Writes of claims3 (registered runs W2, W3, W1, W4)")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(figdir, f"fig_actions.{ext}"), dpi=150)
    plt.close(fig)
    print(json.dumps(counts["sample"], indent=1))
    print(json.dumps(actions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
