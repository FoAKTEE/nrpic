#!/usr/bin/env python3
"""N4 band by band: the quasi-static measure of the GR particles (analyze_gr.py, spec_qs on
the GR dump mesh, |k| up to 64 k_f at 128^3) against that of the Newtonian particles
(analyze.py, gw.spectra[...]['qs'] on ng = 64, |k| up to 32 k_f, stored as a^4 rho_qs
per shell and divided here by a rho_c), summed over |k| <= K k_f
for K = 8, 16, 32, at the epochs of the Newtonian spectra (the GR spectrum interpolated per
shell in log a between the two bracketing dumps). Separates a grid difference (the GR mesh
holds the shells 33-64 that ng = 64 does not) from a difference of the particles.

    python3 n4_band.py --newton analysis_n128.json --gr NAME:analysis_gr_X.json ... \
        [--out $NRPIC_RUN_DIR]

Writes n4_band.json and fig_n4_band (PDF, PNG): (a) Omega_qs per shell at a = 19.4 and 97.5,
GR particles of each gauge and Newtonian particles; (b) the band ratio GR/N against a.
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

BANDS = (8, 16, 32)
RHO_C = 3.0/(8.0*np.pi)


def gr_spec_at(dumps, a):
    q = [d for d in dumps if "spec_qs" in d]
    av = np.array([d["a"] for d in q])
    if a < av.min() or a > av.max():
        return None
    k = int(np.searchsorted(av, a))
    if av[k] == a:
        return np.array(q[k]["spec_qs"])
    lo, hi = q[k - 1], q[k]
    w = np.log(a/lo["a"])/np.log(hi["a"]/lo["a"])
    s0, s1 = np.array(lo["spec_qs"]), np.array(hi["spec_qs"])
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where((s0 > 0) & (s1 > 0), np.exp((1 - w)*np.log(np.maximum(s0, 1e-300))
                                                   + w*np.log(np.maximum(s1, 1e-300))),
                       (1 - w)*s0 + w*s1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--newton", required=True)
    ap.add_argument("--gr", action="append", required=True, help="NAME:path")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    nw = {r["name"]: r for r in json.load(open(a.newton))}["newton_s014"]["gw"]["spectra"]
    grs = []
    for s in a.gr:
        name, path = s.split(":", 1)
        grs.append((name, json.load(open(path))["dumps"]))
    res = {"bands": list(BANDS), "epochs": []}
    for key in sorted(nw, key=lambda x: nw[x]["a"]):
        aN = nw[key]["a"]
        sN = np.array(nw[key]["qs"])/(aN*RHO_C)     # analyze.py stores a^4 rho_qs per shell
        row = {"a": aN, "Omega_N": {str(K): float(sN[1:K + 1].sum()) for K in BANDS},
               "Omega_N_all": float(sN.sum()), "gr": {}}
        for name, dumps in grs:
            sG = gr_spec_at(dumps, aN)
            if sG is None:
                continue
            row["gr"][name] = {"ratio": {str(K): float(sG[1:K + 1].sum()/sN[1:K + 1].sum())
                                         for K in BANDS},
                               "ratio_all": float(sG.sum()/sN.sum()),
                               "frac_above_32": float(sG[33:].sum()/sG.sum()),
                               "spec": sG.tolist()}
        row["spec_N"] = sN.tolist()
        res["epochs"].append(row)
    with open(os.path.join(a.out, "n4_band.json"), "w") as f:
        json.dump(res, f, indent=1)
    for r in res["epochs"]:
        line = f"a={r['a']:.2f}"
        for name in r["gr"]:
            g = r["gr"][name]
            line += (f" | {name}: all {g['ratio_all']:.3f} " +
                     " ".join(f"<={K}:{g['ratio'][str(K)]:.3f}" for K in BANDS) +
                     f" above32 {g['frac_above_32']:.3f}")
        print(line)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.17, top=0.93, wspace=0.3)
    ls = {0: "-", 1: "--"}
    for j, target in enumerate((19.42, 97.52)):
        r = min(res["epochs"], key=lambda x: abs(np.log(x["a"]/target)))
        kN = np.arange(len(r["spec_N"]))
        axs[0].loglog(kN[1:], np.array(r["spec_N"])[1:], ls[j], color="k", lw=1.2,
                      label=f"Newton, a = {r['a']:.1f}")
        for i, name in enumerate(r["gr"]):
            sG = np.array(r["gr"][name]["spec"])
            kG = np.arange(len(sG))
            axs[0].loglog(kG[1:], sG[1:], ls[j], color=fs.SERIES[i], lw=0.9,
                          label=f"GR {name}, a = {r['a']:.1f}")
    axs[0].axvline(32, color="0.6", lw=0.6)
    axs[0].set_xlabel(r"$|k|/k_f$")
    axs[0].set_ylabel(r"$\Omega_{\rm qs}$ per shell")
    axs[0].legend(fontsize=5.5, ncol=1)
    mk = {8: "o", 16: "s", 32: "^"}
    for i, (name, _) in enumerate(grs):
        E = [r for r in res["epochs"] if name in r["gr"]]
        aa = [r["a"] for r in E]
        for K in BANDS:
            axs[1].semilogx(aa, [r["gr"][name]["ratio"][str(K)] for r in E], mk[K] + "-",
                            color=fs.SERIES[i], ms=3, lw=0.8,
                            label=f"{name}, |k| <= {K}" if True else None)
        axs[1].semilogx(aa, [r["gr"][name]["ratio_all"] for r in E], "x:", color=fs.SERIES[i],
                        ms=4, lw=0.8, label=f"{name}, all shells")
    axs[1].axhspan(0.9, 1.1, color="0.9")
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"$\Omega_{\rm qs}$ GR particles / Newton particles")
    axs[1].legend(fontsize=5, ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_n4_band"))
    plt.close(fig)


if __name__ == "__main__":
    main()
