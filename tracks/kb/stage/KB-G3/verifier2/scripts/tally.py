#!/usr/bin/env python3
"""Rates with Clopper-Pearson intervals, stratum-weighted estimates and the figures (verifier 2).

    python tally.py --draw DRAW_RUN_DIR --verdicts VERDICT_DIR --out DIR

Reads strata.json of the draw run, verdicts/sample_verdicts.tsv and verdicts/item1.tsv (mine),
and, for comparison only, the per-stratum counts of claims3's SAMPLE_VERDICTS.tsv (WA versus
the rest). Writes tally.json, fig_sample.{png,pdf}, fig_item1.{png,pdf}.
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
C3 = os.path.join(WT, "tracks", "kb", "claims3", "SAMPLE_VERDICTS.tsv")


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp(k, n, alpha=0.05):
    """Clopper-Pearson interval by bisection on the binomial tails (standard library only)."""
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid):
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)
    lo = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < alpha / 2)
    hi = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > alpha / 2)
    return lo, hi


def weighted(rates, sizes):
    tot = sum(sizes[s] for s in rates)
    est = sum(sizes[s] * rates[s][0] / rates[s][1] for s in rates) / tot
    var = sum((sizes[s] / tot) ** 2 * (rates[s][0] / rates[s][1]) * (1 - rates[s][0] / rates[s][1])
              / max(rates[s][1] - 1, 1) * (1 - rates[s][1] / sizes[s]) for s in rates)
    return est, math.sqrt(var)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    strata = json.load(open(os.path.join(a.draw, "strata.json")))
    sizes = strata["strata_sizes"]
    rows = list(csv.DictReader(open(os.path.join(a.verdicts, "sample_verdicts.tsv")), delimiter="\t"))
    drawn = {int(r["claim_id"]) for r in csv.DictReader(open(os.path.join(a.draw, "sample.tsv")), delimiter="\t")}
    assert drawn == {int(r["claim_id"]) for r in rows}, "verdict file does not match the draw"
    out = {"sizes": sizes, "strata": {}, "lenient": {}, "strict": {}}
    for mode in ("main", "lenient", "strict"):
        rates = {}
        for s in ("P", "M", "Q"):
            rs = [r for r in rows if r["stratum"] == s]
            if mode == "main":
                k = sum(int(r["right"]) for r in rs)
            elif mode == "lenient":   # every borderline counted right
                k = sum(1 for r in rs if int(r["right"]) or int(r["borderline"]))
            else:                     # every borderline counted not right
                k = sum(1 for r in rs if int(r["right"]) and not int(r["borderline"]))
            rates[s] = (k, len(rs))
        key = "strata" if mode == "main" else mode
        for s, (k, n) in rates.items():
            lo, hi = cp(k, n)
            out[key][s] = {"right": k, "n": n, "rate": k / n, "cp95": [lo, hi]}
        w_est, w_se = weighted({s: rates[s] for s in ("M", "Q")}, sizes)
        all_est, all_se = weighted(rates, sizes)
        out[key]["W_weighted"] = {"rate": w_est, "se": w_se}
        out[key]["all_weighted"] = {"rate": all_est, "se": all_se}
        kM = rates["M"][0] + rates["Q"][0]
        nM = rates["M"][1] + rates["Q"][1]
        out[key]["W_pooled_unweighted"] = {"right": kM, "n": nM, "cp95": list(cp(kM, nM))}
    # claims3's sample, read only for comparison (its own verdicts, not mine)
    c3 = list(csv.DictReader(open(C3), delimiter="\t"))
    c3wa = [r for r in c3 if r["stratum"] == "WA"]
    c3q = [r for r in c3 if r["stratum"] != "WA"]
    k_wa, n_wa = sum(int(r["right"]) for r in c3wa), len(c3wa)
    k_q, n_q = sum(int(r["right"]) for r in c3q), len(c3q)
    out["claims3_for_comparison"] = {"WA": [k_wa, n_wa], "WQ+WB+WM": [k_q, n_q]}
    kM, nM = out["strata"]["M"]["right"], out["strata"]["M"]["n"]
    out["pooled_machine_located"] = {"right": kM + k_wa, "n": nM + n_wa,
                                    "rate": (kM + k_wa) / (nM + n_wa), "cp95": list(cp(kM + k_wa, nM + n_wa))}
    kQ, nQ = out["strata"]["Q"]["right"], out["strata"]["Q"]["n"]
    out["pooled_rest_of_weak"] = {"right": kQ + k_q, "n": nQ + n_q, "rate": (kQ + k_q) / (nQ + n_q),
                                  "cp95": list(cp(kQ + k_q, nQ + n_q))}
    # expected not right among the unread weak class (my sizes M, Q), from the pooled rates
    exp_bad = sizes["M"] * (1 - out["pooled_machine_located"]["rate"]) + sizes["Q"] * (1 - out["pooled_rest_of_weak"]["rate"])
    exp_lo = sizes["M"] * (1 - out["pooled_machine_located"]["cp95"][1]) + sizes["Q"] * (1 - out["pooled_rest_of_weak"]["cp95"][1])
    exp_hi = sizes["M"] * (1 - out["pooled_machine_located"]["cp95"][0]) + sizes["Q"] * (1 - out["pooled_rest_of_weak"]["cp95"][0])
    out["expected_not_right_in_W"] = {"point": exp_bad, "range_from_cp": [exp_lo, exp_hi]}
    item1 = list(csv.DictReader(open(os.path.join(a.verdicts, "item1.tsv")), delimiter="\t"))
    counts = {}
    for r in item1:
        counts.setdefault(r["group"], {}).setdefault(r["verdict"], 0)
        counts[r["group"]][r["verdict"]] += 1
    out["item1"] = {"n": len(item1), "by_group": counts,
                    "fail": [int(r["claim_id"]) for r in item1 if r["verdict"] in ("NOT SUPPORTED", "LOCATOR WRONG", "TAKEN OUT WRONGLY")]}
    with open(os.path.join(a.out, "tally.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    figures(out, a.out)
    return 0


def figures(out, d):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        import figstyle
        figstyle.use_style()
    except Exception as e:  # the figure must still be made
        print("figstyle not applied:", e)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    labels, ys, los, his, cols = [], [], [], [], []
    entries = [("P checked by a person\n(this sample, n=14)", out["strata"]["P"], "C0"),
               ("M machine-located\n(this sample, n=13)", out["strata"]["M"], "C3"),
               ("Q rest of weak class\n(this sample, n=13)", out["strata"]["Q"], "C2"),
               ("M pooled with claims3 WA\n(n=%d)" % out["pooled_machine_located"]["n"], out["pooled_machine_located"], "C3"),
               ("Q pooled with claims3 rest\n(n=%d)" % out["pooled_rest_of_weak"]["n"], out["pooled_rest_of_weak"], "C2")]
    for i, (lab, e, c) in enumerate(entries):
        rate = e["rate"]
        ax.errorbar([rate * 100], [i], xerr=[[100 * (rate - e["cp95"][0])], [100 * (e["cp95"][1] - rate)]],
                    fmt="o" if i < 3 else "s", color=c, capsize=3, mfc="white" if i >= 3 else c)
        ax.text(101, i, "%d/%d" % (e["right"], e["n"]), va="center", fontsize=8)
        labels.append(lab)
    ax.axvline(86.5, color="0.5", ls="--", lw=0.8)
    ax.text(86.0, 4.45, "claims3 estimate 86.5 %", ha="right", fontsize=7, color="0.4")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(40, 108)
    ax.set_xlabel("right as worded [%] (Clopper-Pearson 95 %)")
    ax.set_title("KB-G3 verifier 2: sample of 40 on kb-20261125-2f97258 (seed 20261126)", fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(d, "fig_sample." + ext), dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    groups = ["A_new", "B_superseded_withdrawn", "C_siblings", "D_seeds_named"]
    names = {"A_new": "862-881 new", "B_superseded_withdrawn": "superseded/withdrawn",
             "C_siblings": "siblings of --to", "D_seeds_named": "seeds and named"}
    kinds = [("SUPPORTED", "C2"), ("TAKEN OUT RIGHTLY", "C0"), ("PROCESSED RIGHTLY", "C9"),
             ("NOT SUPPORTED", "C3"), ("LOCATOR WRONG", "C1")]
    left = [0] * len(groups)
    for kname, c in kinds:
        vals = [out["item1"]["by_group"].get(g, {}).get(kname, 0) for g in groups]
        ax.barh(range(len(groups)), vals, left=left, color=c, label=kname.lower())
        left = [l + v for l, v in zip(left, vals)]
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([names[g] for g in groups], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("claims re-read at their locators (item 1, 61 claims)")
    ax.legend(fontsize=7, loc="lower right", frameon=False)
    ax.set_title("verdicts per group; the one failure is claim 781", fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(d, "fig_item1." + ext), dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
