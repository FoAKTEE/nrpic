#!/usr/bin/env python3
"""claims5: right-as-worded rate of the cited class T with Clopper-Pearson intervals, beside the
earlier samples; the census of T (claims4's 13 + this package's 131); the new stratified estimate
for the 389 machine-located claims of claims4; LEDGER.tsv; the figure.

    python rates.py --order ORDER_RUN_DIR --apply APPLY_RUN_DIR --claims4 CLAIMS4_RATES_JSON --out DIR

Inputs: work/verdicts_T.tsv (this package), tracks/kb/claims4/work/verdicts_TR.tsv (claims4's T
rows), order.tsv/order.json of the claims4 order run (class sizes, 'lower' flag, track), result.json
of this package's apply run (successor ids), claims4's rates.json (its C, R counts and earlier
samples, copied from their files there). Standard library plus matplotlib for the figure.
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, HERE)


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def cp(k, n, a=0.05):
    """Clopper-Pearson interval by bisection on the binomial tails."""
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
    return [lower, upper]


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def summary(rows):
    k = sum(int(r["right"]) for r in rows)
    n = len(rows)
    kb = sum(1 for r in rows if r["borderline"] == "1" and r["right"] == "1")
    nb = sum(1 for r in rows if r["borderline"] == "1" and r["right"] == "0")
    return {"n": n, "right": k, "rate": k / n, "cp95": cp(k, n),
            "borderline_counted_right": kb, "borderline_counted_not_right": nb,
            "rate_all_borderline_right": (k + nb) / n, "rate_all_borderline_not_right": (k - kb) / n,
            "verdicts": {v: sum(1 for r in rows if r["verdict"] == v) for v in sorted({r["verdict"] for r in rows})}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--apply", required=True)
    ap.add_argument("--claims4", required=True, help="claims4 rates.json")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = read(os.path.join(PKG, "work", "verdicts_T.tsv"))
    c4rows = [r for r in read(os.path.join(WT, "tracks", "kb", "claims4", "work", "verdicts_TR.tsv")) if r["cls"] == "T"]
    meta = {}
    for r in read(os.path.join(a.order, "order.tsv")):
        meta[int(r["claim_id"])] = r
    sizes = json.load(open(os.path.join(a.order, "order.json")))["classes"]
    c4 = json.load(open(a.claims4))
    res = json.load(open(os.path.join(a.apply, "result.json")))
    succ = {x["id"]: x["new"] for x in res["results"] if x["do"] == "supersede"}
    added = [x["new"] for x in res["results"] if x["do"] == "add"]

    out = {"run_inputs": {"order": a.order, "apply": a.apply, "claims4_rates": a.claims4}, "sizes_claims4": sizes}
    out["claims5_T"] = summary(rows)
    census = rows + c4rows
    out["T_census_144"] = summary(census)
    # lower-case flag (Q3) on this package's rows
    for flag in ("0", "1"):
        sel = [r for r in rows if meta[int(r["claim_id"])]["lower"] == flag]
        k = sum(int(r["right"]) for r in sel)
        out[f"lower{flag}"] = {"n": len(sel), "right": k, "rate": (k / len(sel)) if sel else None,
                               "cp95": cp(k, len(sel)) if sel else None}
    # by track
    tracks = sorted({meta[int(r["claim_id"])]["track"] for r in rows})
    out["by_track"] = {}
    for t in tracks:
        sel = [r for r in rows if meta[int(r["claim_id"])]["track"] == t]
        out["by_track"][t] = {"n": len(sel), "right": sum(int(r["right"]) for r in sel),
                              "verdicts": {v: sum(1 for r in sel if r["verdict"] == v) for v in
                                           sorted({r["verdict"] for r in sel})}}
    # earlier samples (from claims4 rates.json, which typed them from their files)
    earlier = {"claims3 WA": (18, 22), "verifier2 M": (10, 13),
               "claims4 C": (c4["classes"]["C"]["right"], c4["classes"]["C"]["n"]),
               "claims4 T": (c4["classes"]["T"]["right"], c4["classes"]["T"]["n"]),
               "claims4 R": (c4["classes"]["R"]["right"], c4["classes"]["R"]["n"])}
    out["earlier"] = {k: {"right": v[0], "n": v[1], "rate": v[0] / v[1], "cp95": cp(*v)} for k, v in earlier.items()}
    # stratified estimate for claims4's 389: C census, T census, R sample (finite-population s.e. from R)
    nr_c = c4["classes"]["C"]["n"] - c4["classes"]["C"]["right"]
    nr_t = out["T_census_144"]["n"] - out["T_census_144"]["right"]
    pr = 1 - c4["classes"]["R"]["rate"]
    Nr, nr = sizes["R"], c4["classes"]["R"]["n"]
    est = nr_c + nr_t + Nr * pr
    se = math.sqrt(Nr ** 2 * (1 - nr / Nr) * pr * (1 - pr) / (nr - 1))
    N = sum(sizes.values())
    out["stratified_389"] = {"N": N, "not_right_est": est, "not_right_se": se, "right_rate_est": 1 - est / N,
                             "right_rate_se": se / N, "C_not_right": nr_c, "T_not_right": nr_t,
                             "R_not_right_est": Nr * pr, "corrected_so_far": nr_c + nr_t + (nr - c4["classes"]["R"]["right"])}
    # Q1 test: does the CP interval of claims5 T exclude 0.75?
    lo, hi = out["claims5_T"]["cp95"]
    out["Q1_excludes_0.75"] = not (lo <= 0.75 <= hi)
    json.dump(out, open(os.path.join(a.out, "rates.json"), "w"), indent=1, default=float)
    # LEDGER
    with open(os.path.join(a.out, "LEDGER.tsv"), "w") as f:
        f.write("k\tcls\tclaim_id\ttrack\tverdict\tright\tborderline\taction\tsuccessor\tnote\n")
        for r in rows:
            cid = int(r["claim_id"])
            f.write("\t".join([r["k"], r["cls"], r["claim_id"], meta[cid]["track"], r["verdict"], r["right"],
                               r["borderline"], r["action"], str(succ.get(cid, "")), r["note"]]) + "\n")
        for n in added:
            f.write("\t".join(["-", "added", str(n), "C-sidm", "-", "-", "-", "add", "",
                               "judgement split off from 230 (Track C's reproduction run)"]) + "\n")
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw={"width_ratios": [1.45, 1]})
    items = [(k, v["right"], v["n"], "grey") for k, v in out["earlier"].items()]
    items.append(("claims5 T", out["claims5_T"]["right"], out["claims5_T"]["n"], fs.PAL["blue"]))
    items.append(("T census", out["T_census_144"]["right"], out["T_census_144"]["n"], fs.PAL["orange"]))
    for i, (name, k, n, col) in enumerate(items):
        r = k / n
        lo_, hi_ = cp(k, n)
        ax1.errorbar(i, r, yerr=[[r - lo_], [hi_ - r]], fmt="o", color=col, capsize=3)
    for i, key in ((len(items) - 2, "claims5_T"), (len(items) - 1, "T_census_144")):
        d = out[key]
        ax1.plot([i + 0.18, i + 0.18], [d["rate_all_borderline_not_right"], d["rate_all_borderline_right"]],
                 color=fs.PAL["blue"] if key == "claims5_T" else fs.PAL["orange"], lw=4, alpha=0.35,
                 solid_capstyle="butt")
    s = out["stratified_389"]
    ax1.axhline(s["right_rate_est"], color=fs.PAL["green"], ls="--", lw=1.0)
    ax1.text(0.1, s["right_rate_est"] - 0.06, f"stratified, 389: {s['right_rate_est']:.2f}", fontsize=7.5,
             color=fs.PAL["green"])
    ax1.axhline(0.75, color="k", ls=":", lw=0.8)
    ax1.text(1.5, 0.765, "predicted 0.75 (Q1)", ha="center", fontsize=7.5)
    ax1.axvline(len(items) - 2.5, **fs.MASK_LINE)
    ax1.set_xticks(range(len(items)))
    ax1.set_xticklabels([f"{n}\n{k}/{m}" for n, k, m, _ in items], fontsize=7)
    ax1.minorticks_off()
    ax1.set_ylim(0, 1.02)
    ax1.set_ylabel("right as worded (CP 95 %)")
    ax1.set_title("(a) earlier samples | claims5 (bar: borderline both ways)", fontsize=9)
    cats = ["right", "right_locator", "fragment", "wrong", "part_unsupported", "wrong_label"]
    ccol = [fs.PAL["green"], "#7FC97F", fs.PAL["red"], "#8B0000", fs.PAL["orange"], fs.PAL["yellow"]]
    bottoms = [0] * len(tracks)
    for cat, col in zip(cats, ccol):
        h = [out["by_track"][t]["verdicts"].get(cat, 0) for t in tracks]
        ax2.bar(range(len(tracks)), h, bottom=bottoms, color=col, label=cat.replace("_", " "), width=0.6)
        bottoms = [b + v for b, v in zip(bottoms, h)]
    ax2.set_xticks(range(len(tracks)))
    ax2.set_xticklabels([t.split("-")[0] for t in tracks])
    ax2.minorticks_off()
    ax2.set_ylabel("claims read")
    ax2.set_title("(b) verdicts by track of the claim (131 read)", fontsize=9)
    ax2.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_claims5_rates"))
    print(json.dumps({k: out[k] for k in ("claims5_T", "T_census_144", "lower0", "lower1", "stratified_389",
                                          "Q1_excludes_0.75", "by_track")}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
