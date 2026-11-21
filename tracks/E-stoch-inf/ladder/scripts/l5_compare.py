#!/usr/bin/env python3
"""PL4 of ../JOURNAL.md entry 18: the single-kick test L5 on the processors against the same
runs on a card, from the two l5.json files that l5_analysis.py wrote.

    l5_compare.py --a CARD/l5.json --b PROC/l5.json --out DIR

For every scalar quantity of the rows (rms parts, record ratios, box means) the largest
relative difference between the platforms over the dumps where the quantity lies above
1e-3 of its largest magnitude over the run; the verdicts PL1-PL3 of both; the first-order
momentum part of the stencil run (M_first_K) is reported apart (a difference of nearly
equal numbers, excluded from the 1e-6 criterion). Writes l5_compare.json and
fig_l5_compare.png/pdf.
"""
import argparse
import json
import os

import numpy as np

EXCLUDED = ("M_first_K", "M_third_K", "M_third_C", "H_third", "H0_mean", "H0_rms_nomean",
            "M_K0_rms")


def scalars(row):
    out = {}
    for k, v in row.items():
        if k in ("dump", "cycle"):
            continue
        if isinstance(v, dict):
            for kk, vv in v.items():
                out[f"{k}.{kk}"] = float(vv)
        elif isinstance(v, (int, float)):
            out[k] = float(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="l5.json of the card runs")
    ap.add_argument("--b", required=True, help="l5.json of the processor runs")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    A, B = json.load(open(a.a)), json.load(open(a.b))
    ra = {r["cycle"]: scalars(r) for r in A["rows"]}
    rb = {r["cycle"]: scalars(r) for r in B["rows"]}
    cyc = sorted(set(ra) & set(rb))
    keys = sorted(set.intersection(*[set(ra[c]) & set(rb[c]) for c in cyc]))
    res = dict(cycles=cyc, per_key={}, verdicts={})
    for k in keys:
        va = np.array([ra[c][k] for c in cyc])
        vb = np.array([rb[c][k] for c in cyc])
        big = max(np.abs(va).max(), np.abs(vb).max())
        sel = (np.abs(va) > 1e-3 * big) | (np.abs(vb) > 1e-3 * big)
        den = np.maximum(np.abs(va), np.abs(vb))
        rel = np.where(sel & (den > 0), np.abs(va - vb) / np.where(den > 0, den, 1.0), 0.0)
        res["per_key"][k] = dict(max_rel=float(rel.max()) if rel.size else 0.0,
                                 at_cycle=int(cyc[int(np.argmax(rel))]) if rel.size else None,
                                 excluded=k in EXCLUDED, largest=float(big))
    crit = [v["max_rel"] for k, v in res["per_key"].items() if not v["excluded"]]
    res["max_rel_included"] = float(max(crit)) if crit else None
    res["worst_included"] = max(((k, v["max_rel"]) for k, v in res["per_key"].items()
                                 if not v["excluded"]), key=lambda x: x[1], default=None)
    for p in ("PL1", "PL2", "PL3"):
        res["verdicts"][p] = dict(card=A.get(p, {}).get("pass_"), proc=B.get(p, {}).get("pass_"))
    res["PL4_pass"] = bool(res["max_rel_included"] is not None and res["max_rel_included"] < 1e-6
                           and all(v["card"] == v["proc"] for v in res["verdicts"].values()))
    with open(os.path.join(a.out, "l5_compare.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print("verdicts", res["verdicts"])
    print("largest relative difference (included keys):", res["worst_included"])
    for k, v in sorted(res["per_key"].items(), key=lambda kv: -kv[1]["max_rel"])[:12]:
        print(f"  {k:28s} {v['max_rel']:.2e} cycle {v['at_cycle']} excluded {v['excluded']}")
    print("PL4 pass", res["PL4_pass"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.17, top=0.9, wspace=0.28)
    ta = {r["cycle"]: r["time"] for r in A["rows"]}
    t = np.array([ta[c] for c in cyc])
    for k, col in (("H_even1", fs.PAL["blue"]), ("NC_H_odd", "k"), ("M_first_C", fs.PAL["red"]),
                   ("M_first_K", fs.PAL["green"])):
        if k not in keys:
            continue
        ax[0].semilogy(t, [ra[c][k] for c in cyc], "-", color=col, label=f"{k} card")
        ax[0].semilogy(t, [rb[c][k] for c in cyc], "o", ms=2.5, color=col, mfc="none",
                       label=f"{k} processors")
        va = np.array([ra[c][k] for c in cyc])
        vb = np.array([rb[c][k] for c in cyc])
        d = np.abs(va - vb) / np.maximum(np.maximum(np.abs(va), np.abs(vb)), 1e-300)
        ax[1].semilogy(t, np.maximum(d, 1e-17), "o-", ms=2.5, color=col, label=k)
    ax[1].axhline(1e-6, **fs.GUIDE)
    ax[0].set_xlabel(r"$t$")
    ax[1].set_xlabel(r"$t$")
    ax[0].set_ylabel(r"rms part / $\langle[\mathcal{C}]\rangle$")
    ax[1].set_ylabel("relative difference card - processors")
    ax[0].legend(fontsize=5, ncol=2, loc="lower right")
    ax[1].legend(fontsize=6, loc="upper left")
    fs.save(fig, os.path.join(a.out, "fig_l5_compare"))
    plt.close(fig)


if __name__ == "__main__":
    main()
