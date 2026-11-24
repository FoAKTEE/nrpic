#!/usr/bin/env python3
"""Full relativity against the Newtonian mode with the same particles (predictions N2-N4,
JOURNAL.md 2026-11-24 05:48): halo by halo at equal scale factor (sigma1 = 0.014), the
amplitude scaling between the two Newtonian runs (0.028 at a against 0.014 at 2a), and the
quasi-static GW measure of the GR particles against the Newtonian particles.

    python3 compare_newton.py --gr analysis_gr_s014.json --newton analysis_n128.json \
        [--gr028 analysis_gr_s028.json] [--out $NRPIC_RUN_DIR]

analysis_gr_*.json: scripts/analyze_gr.py (one run each); analysis_n128.json:
scripts/analyze.py on the two Newtonian cases (names newton_s014, newton_s028). Writes
compare_newton.json and fig_gr_newton (PDF, PNG).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs                       # noqa: E402

L = 8.0
NMIN_MASS = None


def pdist(x, y):
    d = np.mod(np.asarray(x) - np.asarray(y) + 0.5*L, L) - 0.5*L
    return float(np.sqrt((d*d).sum()))


def nearest_cat(cats, a, tol=0.04):
    av = np.array([c["a"] for c in cats])
    k = int(np.argmin(np.abs(np.log(av/a))))
    return cats[k] if abs(np.log(av[k]/a)) < tol else None


def match(cat_n, cat_g, nmax=10, rmax=0.1):
    out = []
    for i in range(min(nmax, len(cat_n["masses"]))):
        xn = cat_n["x"][i]
        dd = [pdist(xn, y) for y in cat_g["x"]] if cat_g["x"] else []
        if not dd:
            break
        j = int(np.argmin(dd))
        out.append({"M_N": cat_n["masses"][i], "M_GR": cat_g["masses"][j], "dist": dd[j],
                    "matched": dd[j] <= rmax, "ratio": cat_g["masses"][j]/cat_n["masses"][i]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gr", required=True)
    ap.add_argument("--gr028", default=None)
    ap.add_argument("--newton", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    gr = json.load(open(a.gr))
    nw = {r["name"]: r for r in json.load(open(a.newton))}
    n14 = nw["newton_s014"]["catalogs"]
    res = {"N2": [], "N3": [], "N4": []}
    for cat in gr["halos"]:
        if cat["a"] < 20:
            continue
        cn = nearest_cat(n14, cat["a"])
        if cn is None:
            continue
        mt = match(cn, cat)
        ratios = [m["ratio"] for m in mt if m["matched"]]
        res["N2"].append({"a_GR": cat["a"], "a_N": cn["a"], "n_GR": cat["n_halos_100"],
                          "n_N": cn["n_halos"], "band": 2*np.sqrt(max(cn["n_halos"], 1)) + 2,
                          "matched": sum(m["matched"] for m in mt), "of": len(mt),
                          "median_abs_dM": float(np.median(np.abs(np.array(ratios) - 1))) if ratios else None,
                          "ratios": ratios,
                          "M1_GR": max(cat["masses"]) if cat["masses"] else None,
                          "M1_N": max(cn["masses"]) if cn["masses"] else None})
    if "newton_s028" in nw:
        n28 = nw["newton_s028"]["catalogs"]
        for c28 in n28:
            if not 25 <= c28["a"] <= 72:
                continue
            c14 = nearest_cat(n14, 2*c28["a"])
            if c14 is None:
                continue
            res["N3"].append({"a_028": c28["a"], "a_014": c14["a"], "n_028": c28["n_halos"],
                              "n_014": c14["n_halos"],
                              "band": 2*np.sqrt(max(c14["n_halos"], 1)) + 2,
                              "M1_028": max(c28["masses"]) if c28["masses"] else None,
                              "M1_014": max(c14["masses"]) if c14["masses"] else None})
    gw = nw["newton_s014"].get("gw")
    if gw:
        rows = np.array(gw["rows"])
        for d in gr["dumps"]:
            if "Omega_qs_part" not in d:
                continue
            k = int(np.argmin(np.abs(rows[:, 0] - d["t"])))
            if abs(rows[k, 0] - d["t"]) < 0.05:
                res["N4"].append({"a": d["a"], "Omega_qs_GRpart": d["Omega_qs_part"],
                                  "Omega_qs_Npart": float(rows[k, 9]),
                                  "ratio": d["Omega_qs_part"]/float(rows[k, 9]),
                                  "Omega_rad_N": float(rows[k, 8]),
                                  "Omega_metric_cor": d.get("Omega_cor")})
    with open(os.path.join(a.out, "compare_newton.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.93, wspace=0.38)
    if res["N2"]:
        aa = [r["a_GR"] for r in res["N2"]]
        axs[0].plot(aa, [r["n_GR"] for r in res["N2"]], "o-", color=fs.SERIES[0], label="GR")
        axs[0].errorbar(aa, [r["n_N"] for r in res["N2"]], yerr=[r["band"] for r in res["N2"]],
                        fmt="s--", color=fs.SERIES[1], capsize=1.5, label="Newton (same particles)")
        for r in res["N2"]:
            axs[1].plot([r["a_GR"]]*len(r["ratios"]), np.array(r["ratios"]) - 1, "o",
                        color=fs.SERIES[0], ms=2.5)
        axs[1].axhspan(-0.05, 0.05, color="0.9")
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"FoF halos ($\geq 100$ particles)")
    axs[0].legend(fontsize=6.5)
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"$M_{\rm GR}/M_{\rm N} - 1$, ten largest")
    if res["N4"]:
        axs[2].semilogx([r["a"] for r in res["N4"]], [r["ratio"] for r in res["N4"]], "o-",
                        color=fs.SERIES[0], label=r"$\Omega_{\rm qs}$ GR particles / Newton")
        axs[2].semilogx([r["a"] for r in res["N4"]],
                        [r["Omega_metric_cor"]/r["Omega_qs_Npart"] if r["Omega_metric_cor"] else np.nan
                         for r in res["N4"]], "s--", color=fs.SERIES[1],
                        label=r"metric (corrected) / Newton")
        axs[2].axhspan(0.9, 1.1, color="0.9")
    axs[2].set_xlabel(r"$a$")
    axs[2].set_ylabel("ratio")
    axs[2].legend(fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig_gr_newton"))
    plt.close(fig)


if __name__ == "__main__":
    main()
