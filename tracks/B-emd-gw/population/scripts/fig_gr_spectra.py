#!/usr/bin/env python3
"""Shell spectra of the TT near-field measure of the full-GR box (risk R22): where in k the
metric's TT energy leaves the particles' weak-field near field after halo formation.

    python3 fig_gr_spectra.py --json analysis_gr.json [--run s014] [--out $NRPIC_RUN_DIR]

Reads the per-dump shell sums spec_raw, spec_cor (metric) and spec_qs (particles, S^TT/k^2) of
`analyze_gr.py` (Omega per |k| shell of width k_f, the shells summing to Omega_qs) and plots them
at chosen scale factors, with the ratio metric/particles per shell. Writes pop_gr_spectra.png/.pdf
and spectra.json (the ratio per shell and the shell where the corrected metric first exceeds the
particles by a factor 3).
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

A_SHOW = (9.0, 25.0, 49.0, 81.0, 121.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--run", default="s014")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    R = {r["name"]: r for r in json.load(open(a.json))}
    r = R[a.run]
    D = [d for d in r["dumps"] if "spec_cor" in d and "spec_qs" in d]
    av = np.array([d["a"] for d in D])
    out = {"run": a.run, "rows": []}
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.92, wspace=0.3)
    cols = fs.series_colors(len(A_SHOW)) if hasattr(fs, "series_colors") else fs.SERIES
    for at, col in zip(A_SHOW, cols):
        i = int(np.argmin(np.abs(np.log(av/at))))
        d = D[i]
        sc, sq = np.array(d["spec_cor"]), np.array(d["spec_qs"])
        n = np.arange(len(sc))
        m = (n > 0) & (sq > 0)
        ratio = np.where(m, sc/np.where(sq > 0, sq, 1.0), np.nan)
        first3 = next((int(k) for k in n[m] if ratio[k] > 3.0), None)
        out["rows"].append({"a": d["a"], "Omega_cor": d["Omega_cor"], "Omega_qs_part": d["Omega_qs_part"],
                            "ratio_by_shell": [None if not np.isfinite(x) else float(x) for x in ratio],
                            "first_shell_ratio_above_3": first3,
                            "fraction_of_Omega_cor_above_shell_16": float(sc[17:].sum()/sc.sum()) if sc.sum() > 0 else None})
        axs[0].loglog(n[m], sc[m], color=col, lw=1.0, label=r"$a = %.0f$" % d["a"])
        axs[0].loglog(n[m], sq[m], color=col, lw=0.8, ls="--")
        axs[1].loglog(n[m], ratio[m], color=col, lw=1.0)
    axs[0].set_xlabel(r"$|k|/k_f$")
    axs[0].set_ylabel(r"$\Omega_{\rm qs}$ per shell: metric (solid), particles (dashed)")
    axs[0].legend(fontsize=6.5, loc="lower left")
    axs[1].axhline(1.0, **fs.GUIDE)
    axs[1].set_xlabel(r"$|k|/k_f$")
    axs[1].set_ylabel("metric / particles per shell")
    fs.save(fig, os.path.join(a.out, "pop_gr_spectra"))
    plt.close(fig)
    with open(os.path.join(a.out, "spectra.json"), "w") as f:
        json.dump(out, f, indent=1)
    for row in out["rows"]:
        print(f"a {row['a']:.1f}: Omega cor {row['Omega_cor']:.3e} part {row['Omega_qs_part']:.3e}; "
              f"first shell ratio > 3: {row['first_shell_ratio_above_3']}; "
              f"fraction above shell 16: {row['fraction_of_Omega_cor_above_shell_16']:.3f}")


if __name__ == "__main__":
    main()
