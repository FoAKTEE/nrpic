#!/usr/bin/env python3
"""claims4: right-as-worded rates per class with Clopper-Pearson intervals, the stratified
estimate for the 389 unread machine-located claims, the earlier samples beside them, LEDGER.tsv
and the figure.

    python rates.py --order ORDER_RUN_DIR --apply APPLY_RUN_DIR --out DIR

Inputs: work/verdicts_C.tsv, work/verdicts_TR.tsv (this package), order.json of the order run,
result.json of the apply run. Earlier samples (counts typed from their files, cited in the
output): claims3 SAMPLE_VERDICTS.tsv (WA 18/22; all 26/30), verifier2 tally (M 10/13),
pooled machine-located 28/35 (VERIFIER2.md section 2).
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp(k, n, a=0.05):
    """Clopper-Pearson interval by bisection on the binomial tails (standard library)."""
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < a / 2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > a / 2)
    return lower, upper


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--apply", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = read(os.path.join(PKG, "work", "verdicts_C.tsv")) + read(os.path.join(PKG, "work", "verdicts_TR.tsv"))
    order = json.load(open(os.path.join(a.order, "order.json")))
    lower = {}
    with open(os.path.join(a.order, "order.tsv")) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            lower[int(r["claim_id"])] = int(r["lower"])
    sizes = order["classes"]
    res = json.load(open(os.path.join(a.apply, "result.json")))
    succ = {}
    for x in res["results"]:
        if x["do"] == "supersede":
            succ[x["id"]] = x["new"]
    out = {"run_inputs": {"order": a.order, "apply": a.apply}, "classes": {}, "sizes": sizes}
    for c in "CTR":
        rr = [r for r in rows if r["cls"] == c]
        k = sum(int(r["right"]) for r in rr)
        n = len(rr)
        kb_ = sum(1 for r in rr if r["borderline"] == "1" and r["right"] == "1")
        nb_ = sum(1 for r in rr if r["borderline"] == "1" and r["right"] == "0")
        lo, hi = cp(k, n)
        out["classes"][c] = {"n": n, "right": k, "rate": k / n, "cp95": [lo, hi],
                             "borderline_counted_right": kb_, "borderline_counted_not_right": nb_,
                             "rate_all_borderline_right": (k + nb_) / n,
                             "rate_all_borderline_not_right": (k - kb_) / n,
                             "verdicts": {v: sum(1 for r in rr if r["verdict"] == v) for v in
                                          sorted({r["verdict"] for r in rr})}}
    tr = [r for r in rows if r["cls"] in "TR"]
    k = sum(int(r["right"]) for r in tr)
    out["TR_pooled"] = {"n": len(tr), "right": k, "rate": k / len(tr), "cp95": cp(k, len(tr))}
    # lower-case-start flag (P3), on T and R
    for flag in (0, 1):
        sel = [r for r in tr if lower.get(int(r["claim_id"])) == flag]
        kk = sum(int(r["right"]) for r in sel)
        out[f"TR_lower{flag}"] = {"n": len(sel), "right": kk, "rate": (kk / len(sel)) if sel else None}
    # stratified estimate for the 389: C census, T and R samples with finite-population variance
    est_wrong, var = 0.0, 0.0
    for c in "CTR":
        d = out["classes"][c]
        Nh, nh, ph = sizes[c], d["n"], 1 - d["rate"]
        est_wrong += Nh * ph
        if nh < Nh and nh > 1:
            var += Nh ** 2 * (1 - nh / Nh) * ph * (1 - ph) / (nh - 1)
    Ntot = sum(sizes.values())
    out["stratified_389"] = {"N": Ntot, "not_right_est": est_wrong, "not_right_se": math.sqrt(var),
                             "right_rate_est": 1 - est_wrong / Ntot, "right_rate_se": math.sqrt(var) / Ntot,
                             "already_corrected_here": sum(1 for r in rows if r["right"] == "0")}
    earlier = {"claims3 WA (auto) 18/22": (18, 22), "verifier2 M 10/13": (10, 13),
               "pooled machine-located 28/35": (28, 35), "claims3 weak class 26/30": (26, 30)}
    out["earlier"] = {k_: {"right": v[0], "n": v[1], "rate": v[0] / v[1], "cp95": cp(*v)} for k_, v in earlier.items()}
    # combined machine-located random samples: claims3 WA + verifier2 M + this package's T and R
    kk, nn = 28 + out["TR_pooled"]["right"], 35 + out["TR_pooled"]["n"]
    out["pooled_random_machine_located"] = {"right": kk, "n": nn, "rate": kk / nn, "cp95": cp(kk, nn)}
    json.dump(out, open(os.path.join(a.out, "rates.json"), "w"), indent=1, default=float)
    # LEDGER
    with open(os.path.join(a.out, "LEDGER.tsv"), "w") as f:
        f.write("k\tcls\tclaim_id\tverdict\tright\tborderline\taction\tsuccessor\tnote\n")
        for r in rows:
            cid = int(r["claim_id"])
            f.write("\t".join([r["k"], r["cls"], r["claim_id"], r["verdict"], r["right"], r["borderline"],
                               r["action"], str(succ.get(cid, "")), r["note"]]) + "\n")
        for x in res["results"]:
            cid = x.get("id")
            if cid is None or any(int(r["claim_id"]) == cid for r in rows):
                continue
            f.write("\t".join(["-", "named", str(cid), "-", "-", "-", x["do"], str(x.get("new", "")),
                               "sibling or VERIFIER2 leftover (plan P1)"]) + "\n")
        for x in res["results"]:
            if x["do"] == "add":
                f.write("\t".join(["-", "named", str(x["new"]), "-", "-", "-", "add", "",
                                   "judgement split off from 877"]) + "\n")
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.6), gridspec_kw={"width_ratios": [1.35, 1]})
    labels, vals, los, his, cols = [], [], [], [], []
    for name, (kk_, nn_) in [("claims3 WA", (18, 22)), ("verifier2 M", (10, 13)), ("pooled 28/35", (28, 35))]:
        lo, hi = cp(kk_, nn_)
        labels.append(f"{name}\n{kk_}/{nn_}"); vals.append(kk_ / nn_); los.append(lo); his.append(hi)
        cols.append("grey")
    for c, name, col in (("T", "T cited", fs.PAL["blue"]), ("R", "R rest", fs.PAL["green"]), ("C", "C cut", fs.PAL["red"])):
        d = out["classes"][c]
        labels.append(f"{name}\n{d['right']}/{d['n']}"); vals.append(d["rate"]); los.append(d["cp95"][0])
        his.append(d["cp95"][1]); cols.append(col)
    d = out["TR_pooled"]
    labels.append(f"T+R\n{d['right']}/{d['n']}"); vals.append(d["rate"]); los.append(d["cp95"][0]); his.append(d["cp95"][1])
    cols.append(fs.PAL["orange"])
    x = list(range(len(vals)))
    for i in x:
        ax1.errorbar(i, vals[i], yerr=[[vals[i] - los[i]], [his[i] - vals[i]]], fmt="o", color=cols[i], capsize=3)
    s = out["stratified_389"]
    ax1.axhspan(s["right_rate_est"] - s["right_rate_se"], s["right_rate_est"] + s["right_rate_se"],
                color=fs.PAL["orange"], alpha=0.15, lw=0)
    ax1.axhline(s["right_rate_est"], color=fs.PAL["orange"], ls="--", lw=1.0)
    ax1.text(len(vals) - 0.6, s["right_rate_est"] + 0.015, "stratified, 389 unread", ha="right", fontsize=8,
             color=fs.PAL["orange"])
    ax1.axvline(2.5, **fs.MASK_LINE)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=7.5)
    ax1.minorticks_off()
    ax1.set_ylim(0, 1.02)
    ax1.set_ylabel("right as worded (CP 95 %)")
    ax1.set_title("(a) earlier samples | claims4", fontsize=10)
    cats = ["right", "right_locator", "fragment", "wrong", "part_unsupported", "wrong_label"]
    ccol = [fs.PAL["green"], "#7FC97F", fs.PAL["red"], "#8B0000", fs.PAL["orange"], fs.PAL["yellow"]]
    bottoms = [0, 0, 0]
    for cat, col in zip(cats, ccol):
        h = [out["classes"][c]["verdicts"].get(cat, 0) for c in "CTR"]
        ax2.bar([0, 1, 2], h, bottom=bottoms, color=col, label=cat.replace("_", " "), width=0.6)
        bottoms = [b + v for b, v in zip(bottoms, h)]
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels([f"C ({sizes['C']})", f"T ({sizes['T']})", f"R ({sizes['R']})"])
    ax2.minorticks_off()
    ax2.set_ylabel("claims read")
    ax2.set_title("(b) verdicts per class (class size)", fontsize=10)
    ax2.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_claims4_rates"))
    print(json.dumps({k_: out[k_] for k_ in ("classes", "TR_pooled", "stratified_389",
                                              "pooled_random_machine_located", "TR_lower0", "TR_lower1")},
                     indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
