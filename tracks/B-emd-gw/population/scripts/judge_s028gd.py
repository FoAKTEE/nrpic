#!/usr/bin/env python3
"""The 0.028 box in the Gamma-driver gauge (q0044, from t = 8) against the 0.014 gauge leg at
the same stage, sigma1 a (P4): 0.028 at a against 0.014 at a' = 2a. Predictions S2, S3
(JOURNAL.md 2026-11-25 04:00), judged as fixed on 2026-11-25 18:35 (same stage, a' = 2a; the
written parenthesis a' = 4a reported beside it). One figure pop_s028gd.png (PDF beside) and
judge_s028gd.json.

    python3 judge_s028gd.py S028GD.json GDHALOS.json GDDUMPS.json OUTDIR

S028GD.json   analyze_gr.py --equal-mass on the 0.028 shifted run (halos and dumps)
GDHALOS.json  analyze_gr.py --equal-mass --halos-only on the 0.014 gauge leg (halos)
GDDUMPS.json  analyze_gr.py on the 0.014 gauge leg (dumps: raw and corrected strain rms)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

RHO_C = 3.0/(8.0*np.pi)
L = 8.0
MLIM = 100*RHO_C*L**3/64**3          # 100 fidL8 particle masses, the common limit


def load(fn):
    d = json.load(open(fn))
    return d[0] if isinstance(d, list) else d


def counts(run):
    a, n, m1 = [], [], []
    for c in run["halos"]:
        big = [M for M in c["masses"] if M >= MLIM]
        a.append(c["a"])
        n.append(len(big))
        m1.append(max(big) if big else np.nan)
    o = np.argsort(a)
    return np.array(a)[o], np.array(n)[o], np.array(m1)[o]


def interp_log(a, y, a0):
    if a0 < a.min()*0.999 or a0 > a.max()*1.001:
        return np.nan
    return float(np.interp(np.log(a0), np.log(a), y))


def main():
    s28, gdh, gdd, od = load(sys.argv[1]), load(sys.argv[2]), load(sys.argv[3]), sys.argv[4]
    os.makedirs(od, exist_ok=True)
    a28, n28, m28 = counts(s28)
    agd, ngd, mgd = counts(gdh)
    out = {"S2": [], "S3": [], "S2_as_written_4a": [], "S3_as_written_4a": []}
    for fac, key2 in ((2.0, "S2"), (4.0, "S2_as_written_4a")):
        for a, n, m in zip(a28, n28, m28):
            if a < 25:
                continue
            nr = interp_log(agd, ngd, fac*a)
            mr = interp_log(agd, mgd, fac*a)
            if np.isnan(nr):
                continue
            band = 2*np.sqrt(max(nr, 0)) + 2
            out[key2].append({"a": float(a), "a_ref": fac*a, "n": int(n), "n_ref": nr,
                              "inside": bool(abs(n - nr) <= band), "M1": float(m), "M1_ref": mr,
                              "M1_ratio": float(m/mr) if mr == mr and mr > 0 else None})
    d28 = sorted([x for x in s28["dumps"] if x["t"] > 8.0], key=lambda x: x["a"])
    dgd = sorted([x for x in gdd["dumps"] if x["t"] > 0], key=lambda x: x["a"])
    ag = np.array([x["a"] for x in dgd])
    rg = np.array([x["rms_raw"] for x in dgd])
    cg = [(x["a"], x["rms_cor"]) for x in dgd if "rms_cor" in x]
    acg = np.array([v[0] for v in cg])
    rcg = np.array([v[1] for v in cg])
    for fac, key3 in ((2.0, "S3"), (4.0, "S3_as_written_4a")):
        for x in d28:
            r = interp_log(ag, rg, fac*x["a"])
            if np.isnan(r):
                continue
            row = {"a": x["a"], "a_ref": fac*x["a"], "rms_raw": x["rms_raw"], "rms_raw_ref": r,
                   "ratio_raw": x["rms_raw"]/r}
            if "rms_cor" in x:
                rc = interp_log(acg, rcg, fac*x["a"])
                if rc == rc:
                    row.update({"rms_cor": x["rms_cor"], "rms_cor_ref": rc, "ratio_cor": x["rms_cor"]/rc})
            out[key3].append(row)
    with open(os.path.join(od, "judge_s028gd.json"), "w") as f:
        json.dump(out, f, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6), constrained_layout=True)
    st28, stgd = a28*0.028/0.0562, agd*0.014/0.0562
    axs[0].plot(stgd, ngd, "o-", ms=2.5, lw=0.8, color="C2", label=r"$\sigma_1 = 0.014$")
    fs.band(axs[0], stgd, ngd - (2*np.sqrt(ngd) + 2), ngd + (2*np.sqrt(ngd) + 2), "C2")
    axs[0].plot(st28, n28, "s-", ms=2.5, lw=0.8, color="C1", label=r"$\sigma_1 = 0.028$")
    axs[0].set_ylabel("halos above the common mass limit")
    axs[1].plot(stgd, mgd, "o-", ms=2.5, lw=0.8, color="C2")
    axs[1].plot(st28, m28, "s-", ms=2.5, lw=0.8, color="C1")
    axs[1].set_ylabel("largest halo mass")
    s3 = out["S3"]
    axs[2].plot([r["a"]*0.028/0.0562 for r in s3], [r["ratio_raw"] for r in s3], "-", lw=0.9,
                color="k", label="raw, same stage")
    sc = [r for r in s3 if "ratio_cor" in r]
    axs[2].plot([r["a"]*0.028/0.0562 for r in sc], [r["ratio_cor"] for r in sc], "o", ms=2.5,
                color="C3", label="corrected, same stage")
    s34 = out["S3_as_written_4a"]
    axs[2].plot([r["a"]*0.028/0.0562 for r in s34], [r["ratio_raw"] for r in s34], "--", lw=0.8,
                color="0.5", label=r"raw, $a' = 4a$ (as written)")
    fs.band(axs[2], np.array([3, 40.0]), np.array([3.0, 3.0]), np.array([5.5, 5.5]), "grey")
    axs[2].set_ylabel(r"rms strain, $0.028$ over $0.014$")
    for ax in axs:
        ax.set_xscale("log")
        ax.set_xlabel(r"stage $\sigma_1 a/0.0562$")
    axs[0].legend(fontsize=6, frameon=False)
    axs[2].legend(fontsize=5, frameon=False)
    fs.save(fig, os.path.join(od, "pop_s028gd"))
    plt.close(fig)
    for k in ("S2", "S2_as_written_4a"):
        print(k)
        for r in out[k]:
            print(f"  a {r['a']:6.1f} ref {r['a_ref']:6.1f}: n {r['n']} ref {r['n_ref']:.1f} inside {r['inside']}"
                  f"  M1 {r['M1']:.4f} ref {r['M1_ref']:.4f} ratio {r['M1_ratio']}")
    for k in ("S3", "S3_as_written_4a"):
        print(k)
        for r in out[k]:
            s = f"  a {r['a']:6.2f} ref {r['a_ref']:6.1f}: raw ratio {r['ratio_raw']:.3f}"
            if "ratio_cor" in r:
                s += f"  cor ratio {r['ratio_cor']:.3f}"
            print(s)


if __name__ == "__main__":
    main()
