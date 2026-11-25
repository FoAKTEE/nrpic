#!/usr/bin/env python3
"""Legs of the full-GR population box (sigma1 = 0.014, L = 8) against the base run
B-20261123-014847-f295ab4 (128^3, one particle per cell, zero shift): the gauge leg
(Gamma-driver shift), the particle leg (8 per cell), the mesh leg (256^3). Reads the JSON that
analyze_gr.py wrote for each run. Predictions: JOURNAL.md, entries of 2026-11-24 06:10 (M1-M4,
Q1-Q2) and 06:30 (GD1-GD3).

    python3 compare_legs.py --base BASE.json --leg gd:LEG.json [--leg p8:LEG2.json ...]

Per common time (dumps and snapshots matched in a within 1 per cent):
  halos   counts above the common mass limit (100 fidL8 masses), band 2 sqrt(N) + 2, and the
          ratio of the largest masses;
  strain  band rms |k| <= 8 k_f of the raw and the gauge-corrected metric strain, from the
          per-shell Omega spectrum (rms^2 of a shell = spec/(n k_f)^2 up to a common factor; the
          shell centre stands for its k, so the ratio leg/base is the quantity);
          Omega_cor and Omega_raw above shell 16 (|k| > 16 k_f) and in total;
  constraints Hr_mean, Mr_mean of pop.cstat.hst at the nearest history time.
Writes $NRPIC_RUN_DIR/compare_legs.json and pop_legs.png (PDF beside).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402


def load(fn):
    d = json.load(open(fn))
    return d[0] if isinstance(d, list) else d


def band_rms2(spec, nmax):
    s = np.asarray(spec, float)
    n = np.arange(len(s))
    m = (n >= 1) & (n <= nmax)
    return float((s[m]/n[m]**2).sum())


def above(spec, n0):
    s = np.asarray(spec, float)
    return float(s[np.arange(len(s)) > n0].sum())


def nearest(t, arr, val):
    i = int(np.argmin(np.abs(np.asarray(t) - val)))
    return arr[i]


def compare(base, leg):
    rows = []
    B = {round(x["a"], 1): x for x in base["dumps"] if "spec_cor" in x}
    for x in leg["dumps"]:
        if "spec_cor" not in x:
            continue
        kb = min(B, key=lambda k: abs(k - x["a"])) if B else None
        if kb is None or abs(kb - x["a"]) > 0.01*x["a"]:
            continue
        y = B[kb]
        row = {"a": x["a"], "a_base": y["a"],
               "rms8_cor_ratio": np.sqrt(band_rms2(x["spec_cor"], 8)/band_rms2(y["spec_cor"], 8))
               if band_rms2(y["spec_cor"], 8) > 0 else None,
               "rms8_raw_ratio": np.sqrt(band_rms2(x["spec_raw"], 8)/band_rms2(y["spec_raw"], 8))
               if band_rms2(y["spec_raw"], 8) > 0 else None,
               "Om_cor_gt16": above(x["spec_cor"], 16), "Om_cor_gt16_base": above(y["spec_cor"], 16),
               "Om_raw_gt16": above(x["spec_raw"], 16), "Om_raw_gt16_base": above(y["spec_raw"], 16),
               "Om_cor": x["Omega_cor"], "Om_cor_base": y["Omega_cor"],
               "Om_raw": x["Omega_raw"], "Om_raw_base": y["Omega_raw"],
               "rms_cor": x["rms_cor"], "rms_cor_base": y["rms_cor"],
               "rms_raw": x["rms_raw"], "rms_raw_base": y["rms_raw"],
               "rms_G": x["rms_G"], "rms_G_base": y["rms_G"]}
        if "Omega_qs_part" in x and "Omega_qs_part" in y:
            row["Om_qs_part"] = x["Omega_qs_part"]
            row["Om_qs_part_base"] = y["Omega_qs_part"]
        rows.append(row)
    H = []
    Bh = {round(h["a"], 1): h for h in base["halos"]}
    for h in leg["halos"]:
        kb = min(Bh, key=lambda k: abs(k - h["a"]))
        if abs(kb - h["a"]) > 0.01*h["a"]:
            continue
        g = Bh[kb]
        n0 = g["n_halos_common"]
        M1 = max(h["masses"]) if h["masses"] else 0.0
        M0 = max(g["masses"]) if g["masses"] else 0.0
        H.append({"a": h["a"], "n_leg": h["n_halos_common"], "n_base": n0,
                  "band": 2*np.sqrt(n0) + 2, "inside": abs(h["n_halos_common"] - n0) <= 2*np.sqrt(n0) + 2,
                  "M1_leg": M1, "M1_base": M0, "M1_ratio": M1/M0 if M0 > 0 else None})
    C = []
    cb, cl = base["cstat"], leg["cstat"]
    for a in (25.0, 49.0, 81.0, 100.0, 121.0, 132.0, 141.0):
        t = 2*(np.sqrt(a) - 1)
        if t > cl["t"][-1] + 0.3 or t > cb["t"][-1] + 0.3:
            continue
        C.append({"a": a, "Hr_leg": nearest(cl["t"], cl["Hr_mean"], t), "Hr_base": nearest(cb["t"], cb["Hr_mean"], t),
                  "Mr_leg": nearest(cl["t"], cl["Mr_mean"], t), "Mr_base": nearest(cb["t"], cb["Mr_mean"], t),
                  "t_leg": nearest(cl["t"], cl["t"], t)})
    return {"strain": rows, "halos": H, "constraints": C,
            "t_last": cl["t"][-1], "a_last": (1 + cl["t"][-1]/2)**2, "guard": leg.get("guard")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--leg", action="append", required=True, help="NAME:analysis_gr_<name>.json")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    args = ap.parse_args()
    base = load(args.base)
    R = {}
    for spec in args.leg:
        name, fn = spec.split(":", 1)
        R[name] = compare(base, load(fn))
    with open(os.path.join(args.out, "compare_legs.json"), "w") as f:
        json.dump(R, f, indent=1, default=float)
    for name, r in R.items():
        print(f"== {name}: last t {r['t_last']:.3f} (a = {r['a_last']:.1f}); guard {bool(r['guard'])}")
        for h in r["halos"]:
            if h["n_base"] or h["n_leg"]:
                print(f"halos a {h['a']:6.1f}: leg {h['n_leg']:3d} base {h['n_base']:3d} band {h['band']:.1f}"
                      f" inside {h['inside']}  M1 ratio {h['M1_ratio']}")
        for s in r["strain"]:
            print(f"strain a {s['a']:6.1f}: rms8 cor ratio {s['rms8_cor_ratio']:.3f} raw ratio {s['rms8_raw_ratio']:.3f}"
                  f" | Om_cor>16 {s['Om_cor_gt16']:.3e} base {s['Om_cor_gt16_base']:.3e}"
                  f" | Om_raw>16 {s['Om_raw_gt16']:.3e} base {s['Om_raw_gt16_base']:.3e}"
                  f" | Om_cor {s['Om_cor']:.3e} base {s['Om_cor_base']:.3e}"
                  f" | rms_G {s['rms_G']:.3e} base {s['rms_G_base']:.3e}")
        for c in r["constraints"]:
            print(f"constraints a {c['a']:6.1f}: Hr leg {c['Hr_leg']:.3e} base {c['Hr_base']:.3e}"
                  f" | Mr leg {c['Mr_leg']:.3e} base {c['Mr_base']:.3e}")

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0))
    cols = fs.SERIES
    for i, (name, r) in enumerate(R.items()):
        c = cols[i % len(cols)]
        H = r["halos"]
        a = [h["a"] for h in H]
        axs[0, 0].plot(a, [h["n_leg"] for h in H], "o-", color=c, ms=3, label=name)
        if i == 0:
            nb = np.array([h["n_base"] for h in H], float)
            axs[0, 0].plot(a, nb, "k-", label="base")
            fs.band(axs[0, 0], a, nb - (2*np.sqrt(nb) + 2), nb + (2*np.sqrt(nb) + 2), "grey")
        S = r["strain"]
        a = [s["a"] for s in S]
        axs[0, 1].plot(a, [s["rms8_cor_ratio"] for s in S], "o-", color=c, ms=3, label=f"{name} corrected")
        axs[0, 1].plot(a, [s["rms8_raw_ratio"] for s in S], "s--", color=c, ms=3, label=f"{name} raw")
        axs[1, 0].semilogy(a, [s["Om_cor_gt16"] for s in S], "o-", color=c, ms=3, label=f"{name} corrected")
        axs[1, 0].semilogy(a, [max(s["Om_raw_gt16"], 1e-30) for s in S], "s--", color=c, ms=3, label=f"{name} raw")
        if i == 0:
            axs[1, 0].semilogy(a, [s["Om_cor_gt16_base"] for s in S], "k-", label="base corrected")
            axs[1, 0].semilogy(a, [s["Om_raw_gt16_base"] for s in S], "k--", label="base raw")
            qs = [s.get("Om_qs_part_base") for s in S]
            if all(q is not None for q in qs):
                axs[1, 0].semilogy(a, qs, "k:", label=r"base particles $S^{TT}/k^2$ (all $k$)")
        C = r["constraints"]
        a = [x["a"] for x in C]
        axs[1, 1].semilogy(a, [x["Mr_leg"] for x in C], "o-", color=c, ms=3, label=f"{name} Mr")
        axs[1, 1].semilogy(a, [x["Hr_leg"] for x in C], "s--", color=c, ms=3, label=f"{name} Hr")
        if i == 0:
            axs[1, 1].semilogy(a, [x["Mr_base"] for x in C], "k-", label="base Mr")
            axs[1, 1].semilogy(a, [x["Hr_base"] for x in C], "k--", label="base Hr")
    axs[0, 0].set_ylabel("halos above 100 fidL8 masses")
    axs[0, 1].axhline(1.0, **fs.THIN)
    axs[0, 1].axhspan(0.8, 1.2, color="grey", alpha=0.15)
    axs[0, 1].set_ylabel(r"band rms $|k|\leq 8k_f$: leg / base")
    axs[1, 0].set_ylabel(r"$\Omega_{qs}$ above $16k_f$")
    axs[1, 1].set_ylabel("mean relative constraint")
    for ax in axs.flat:
        ax.set_xlabel(r"scale factor $a$")
        ax.legend(fontsize=5.5, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(args.out, "pop_legs"))
    plt.close(fig)


if __name__ == "__main__":
    main()
