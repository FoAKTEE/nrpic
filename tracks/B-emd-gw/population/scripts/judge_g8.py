#!/usr/bin/env python3
"""Judge G8a-G8c and W5b/W6 (population/JOURNAL.md, entries 2026-11-27 19:36 and 23:35 PST).

Four 128^3 members of the halo box, sigma1 = 0.014, read through their analysis files
(analyze_gr.py; band power sum_{1<=n<=8} S_n/n^2 of the corrected spectra, as compare_legs.py):
  zs1  one particle per cell, zero shift        (B-20261124-131918-e71996f/analysis_gr_s014.json)
  gd1  one per cell, Gamma driver               (B-20261125-115558-2ab4161/analysis_gr_gd.json)
  zs8  eight per cell, zero shift (q0006)       (B-20261126-022838-27fab1b/analysis_gr_p8u.json)
  gd8  eight per cell, Gamma driver (q0107)     (analysis of this batch, --gd8)
and, with --weyl, the magnetic Weyl statistics of weyl_gauge.py splitx.

  judge_g8.py --gd8 FILE [--weyl weyl_splitx.json] --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))
from compare_legs import band_rms2      # noqa: E402

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
FILES = {"zs1": f"{S}/B-20261124-131918-e71996f/analysis_gr_s014.json",
         "gd1": f"{S}/B-20261125-115558-2ab4161/analysis_gr_gd.json",
         "zs8": f"{S}/B-20261126-022838-27fab1b/analysis_gr_p8u.json"}
A_JUDGE = (49.0, 64.0, 100.0, 132.25)
R1_REVIEW = {64.0: 0.950, 100.0: 0.803, 132.25: 0.643}   # reviewer's run B-20261128-032405-7c4aa64


def load(path):
    r = json.load(open(path))
    return r[0] if isinstance(r, list) else r


def band(r):
    return {x["a"]: np.sqrt(band_rms2(x["spec_cor"], 8)) for x in r["dumps"] if "spec_cor" in x}


def at(B, a):
    k = min(B, key=lambda v: abs(v - a))
    if abs(k - a) > 0.01 * a:
        return None
    return B[k]


def mr_at(r, a):
    c = r["cstat"]
    t = 2.0 * (np.sqrt(a) - 1.0)
    i = int(np.argmin(np.abs(np.asarray(c["t"]) - t)))
    return float(c["Mr_mean"][i]), float(c["Hr_mean"][i]), float(c["t"][i])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gd8", required=True)
    ap.add_argument("--weyl", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    R = {k: load(v) for k, v in FILES.items()}
    R["gd8"] = load(args.gd8)
    B = {k: band(r) for k, r in R.items()}
    out = {"inputs": dict(FILES, gd8=args.gd8, weyl=args.weyl), "band": [], "constraints": [],
           "guard": {k: R[k].get("guard") for k in R},
           "t_last": {k: float(R[k]["cstat"]["t"][-1]) for k in R}}
    for a in A_JUDGE:
        v = {k: at(B[k], a) for k in B}
        row = {"a": a, **{f"rms8_{k}": v[k] for k in v}}
        if None not in v.values():
            row["Pgd"] = v["gd8"] / v["gd1"]          # G8a: particle number, Gamma driver
            row["Pzs"] = v["zs8"] / v["zs1"]          # RC1: particle number, zero shift
            row["R1"] = v["gd1"] / v["zs1"]           # gauge ratio, one per cell
            row["R8"] = v["gd8"] / v["zs8"]           # gauge ratio, eight per cell (corollary)
            row["R1_review"] = R1_REVIEW.get(a)
        out["band"].append(row)
        print(json.dumps({k: (round(x, 4) if isinstance(x, float) else x) for k, x in row.items()}))
    for a in (25.0, 49.0, 81.0, 100.0, 121.0, 132.0, 141.0):
        row = {"a": a}
        for k in R:
            if 2.0 * (np.sqrt(a) - 1.0) <= R[k]["cstat"]["t"][-1] + 0.3:
                row[f"Mr_{k}"], row[f"Hr_{k}"], row[f"t_{k}"] = mr_at(R[k], a)
        out["constraints"].append(row)
        print(json.dumps({k: round(x, 4) for k, x in row.items()}))
    print("guard", out["guard"], "t_last", out["t_last"])
    W = json.load(open(args.weyl)) if args.weyl else None
    with open(os.path.join(args.out, "judge_g8.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(9.0, 7.0))
    lab = {"zs1": "1 ppc, zero shift", "gd1": "1 ppc, Gamma driver",
           "zs8": "8 ppc, zero shift", "gd8": "8 ppc, Gamma driver (q0107)"}
    sty = {"zs1": "o-", "gd1": "s-", "zs8": "o--", "gd8": "s--"}
    a0 = ax[0, 0]
    for k in ("zs1", "gd1", "zs8", "gd8"):
        A = sorted(B[k])
        a0.plot(A, [B[k][x] for x in A], sty[k], ms=3, label=lab[k])
    a0.set_xscale("log"); a0.set_yscale("log")
    a0.set_xlabel("$a$"); a0.set_ylabel(r"band rms, $|k|\leq 8k_f$ (corrected)")
    a0.set_title("(a) band strain of the four $128^3$ members", fontsize=9)
    a0.legend(fontsize=6.5)
    a1 = ax[0, 1]
    for k in ("zs1", "gd1"):
        pass
    A = sorted(x for x in B["gd8"] if at(B["gd1"], x) and at(B["zs8"], x) and at(B["zs1"], x))
    a1.plot(A, [B["gd8"][x] / at(B["gd1"], x) for x in A], "s-", label="8/1 ppc, Gamma driver (G8a)")
    a1.plot(A, [at(B["zs8"], x) / at(B["zs1"], x) for x in A], "o-", label="8/1 ppc, zero shift (RC1)")
    a1.plot(A, [at(B["gd1"], x) / at(B["zs1"], x) for x in A], "^:", label="gauge ratio, 1 ppc")
    a1.plot(A, [B["gd8"][x] / at(B["zs8"], x) for x in A], "v--", label="gauge ratio, 8 ppc")
    a1.axhspan(0.95, 1.05, color="0.9", zorder=0)
    a1.axhline(1.0, color="0.5", lw=0.8)
    a1.set_xlabel("$a$"); a1.set_ylabel("ratio of band rms")
    a1.set_title("(b) particle-number and gauge ratios", fontsize=9)
    a1.legend(fontsize=6.5)
    a2 = ax[1, 0]
    for k in ("zs1", "gd1", "zs8", "gd8"):
        c = R[k]["cstat"]
        a2.plot([(1 + t / 2) ** 2 for t in c["t"]], c["Mr_mean"], sty[k].replace("o", "").replace("s", ""),
                lw=1.0, label=lab[k])
    a2.set_xscale("log"); a2.set_yscale("log")
    a2.set_xlabel("$a$"); a2.set_ylabel("mean relative momentum constraint")
    a2.set_title("(c) momentum constraint (G8b)", fontsize=9)
    a2.legend(fontsize=6.5)
    a3 = ax[1, 1]
    if W:
        T = W["table"]
        Aw = [e["a"] for e in T]
        for key, mk, lb in (("B2_q50", "x", "median"), ("I_B_void", "v", "larger-lapse half"),
                            ("I_B", "s", "mean $I_B$")):
            for p, ls, pl in (("R1", ":", "gauge 1 ppc"), ("R8", "-", "gauge 8 ppc"),
                              ("M", "--", "mesh 256/128")):
                yy = [np.sqrt(e[f"{p}_{key}"]) if f"{p}_{key}" in e else np.nan for e in T]
                a3.plot(Aw, yy, mk + ls, ms=4, label=f"{lb}, {pl}")
        a3.axhspan(0.95, 1.05, color="0.9", zorder=0)
        a3.axhline(1.0, color="0.5", lw=0.8)
    a3.set_xlabel("$a$"); a3.set_ylabel(r"$\sqrt{\mathrm{ratio}}$ of $B_{ij}B^{ij}$ statistic")
    a3.set_title("(d) magnetic Weyl invariant: gauge and mesh ratios", fontsize=9)
    a3.legend(fontsize=5.5, ncol=2)
    fig.tight_layout()
    fn = os.path.join(args.out, "judge_g8.png")
    fig.savefig(fn, dpi=150)
    print(fn)


if __name__ == "__main__":
    main()
