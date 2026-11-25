"""Floor of the even parts from three amplitudes (JOURNAL entry 3), from constraints.json.

E(s) = s^2 A + F_s with F_s independent between the pairs and of equal rms sigma:
rms(D1)^2 = rms(D2)^2 = 17 sigma^2. The halving with sigma removed is compared with the
halving with the SCOPE 4c floor f (from the odd parts).

python3 floor3.py --cons <constraints run dir> --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def ratio(e1, e2, s2):
    a, b = e1 ** 2 - s2, e2 ** 2 - s2
    return float(np.sqrt(a / b)) if a > 0 and b > 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cons", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = json.load(open(os.path.join(a.cons, "constraints.json")))["rows"]
    out = {"rows": []}
    for r in rows:
        row = {"dump": r["dump"], "cN": r["cN"]}
        for g in ("H", "M"):
            x = r[g]
            e1, eh, eq = x["e"]["1.0"], x["e"]["0.5"], x["e"]["0.25"]
            s1 = x["rms_D1"] ** 2 / 17.0
            s2 = x["rms_D2"] ** 2 / 17.0
            sig2 = 0.5 * (s1 + s2)
            sig = np.sqrt(sig2)
            row[g] = {"sigma_D1": float(np.sqrt(s1)), "sigma_D2": float(np.sqrt(s2)),
                      "sigma_D1_over_D2": float(np.sqrt(s1 / s2)),
                      "f_4c_1h": x["f_1_h"], "f_4c_hq": x["f_h_q"],
                      "f_4c_1h_over_sigma": x["f_1_h"] / sig, "f_4c_hq_over_sigma": x["f_h_q"] / sig,
                      "ratio_4c": x["ratio_1_h"], "judged_4c": x["judged_1_h"],
                      "ratio_sigma_1h": ratio(e1, eh, sig2), "judged_sigma_1h": bool(eh > 3 * sig),
                      "ratio_sigma_hq": ratio(eh, eq, sig2), "judged_sigma_hq": bool(eq > 3 * sig),
                      "corr_D1_D2": x["corr_D1_D2"], "D2_over_D1": x["D2_over_D1"]}
        out["rows"].append(row)
    for g in ("H", "M"):
        for tag in ("1h", "hq"):
            jd = [r for r in out["rows"] if r[g][f"judged_sigma_{tag}"] and r[g][f"ratio_sigma_{tag}"] is not None]
            dev = [abs(r[g][f"ratio_sigma_{tag}"] - 4) for r in jd]
            out[f"{g}_{tag}"] = {"judged": [r["dump"] for r in jd], "max_dev": max(dev) if dev else None,
                                 "worst": jd[int(np.argmax(dev))]["dump"] if dev else None,
                                 "outside": [(r["dump"], r[g][f"ratio_sigma_{tag}"]) for r in jd
                                             if abs(r[g][f"ratio_sigma_{tag}"] - 4) > 0.05]}
        out[f"{g}_dump13"] = out["rows"][13][g]
        out[f"{g}_sigma_agreement_1_13_max"] = max(abs(r[g]["sigma_D1_over_D2"] - 1) for r in out["rows"][1:14])
    json.dump(out, open(os.path.join(a.out, "floor3.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    cN = np.array([r["cN"] for r in out["rows"]])
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for x, g in zip(ax, ("H", "M")):
        for key, lab, mk in (("ratio_4c", "1 -> 1/2, floor f of 4c", "o"),
                             ("ratio_sigma_1h", "1 -> 1/2, floor sigma (three amplitudes)", "s"),
                             ("ratio_sigma_hq", "1/2 -> 1/4, floor sigma", "^")):
            jkey = {"ratio_4c": "judged_4c", "ratio_sigma_1h": "judged_sigma_1h",
                    "ratio_sigma_hq": "judged_sigma_hq"}[key]
            y = np.array([r[g][key] if (r[g][key] is not None and r[g][jkey]) else np.nan
                          for r in out["rows"]])
            x.plot(cN, y, "-" + mk, ms=3.5, lw=0.8, label=lab)
        x.axhspan(3.95, 4.05, color="0.88")
        x.set_ylim(3.85, 4.15)
        x.set_xlabel("cN")
        x.set_title(f"{g}: even-part halving at judged dumps only", fontsize=8)
        x.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_floor3.png"), dpi=150)


if __name__ == "__main__":
    main()
