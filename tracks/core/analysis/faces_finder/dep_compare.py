#!/usr/bin/env python3
"""dep_levels.py with two executables, and the tables of the two compared byte for byte
(predictions D and C0 of tracks/core/JOURNAL-faces-finder.md).

    dep_compare.py --base ATHENA --new ATHENA --out DIR

Writes DIR/base, DIR/new (outputs of dep_levels.py), DIR/compare.json and
DIR/fig_dep_compare.{pdf,png}; exit 0 if D and C0 hold.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
DL = os.path.join(REPO, "tracks", "core", "analysis", "deposit_levels", "dep_levels.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    st = {}
    for tag, exe in (("base", a.base), ("new", a.new)):
        with open(os.path.join(out, tag + ".log"), "w") as log:
            st[tag] = subprocess.run([sys.executable, DL, "--exe", exe, "--out",
                                      os.path.join(out, tag)], stdout=log,
                                     stderr=subprocess.STDOUT).returncode
    sb = json.load(open(os.path.join(out, "base", "summary.json")))
    sn = json.load(open(os.path.join(out, "new", "summary.json")))
    same, lines = {}, {}
    for name, r in sn["cases"].items():
        fb = os.path.join(out, "base", name, "tab", sb["cases"][name].get("tab", "x"))
        fn = os.path.join(out, "new", name, "tab", r.get("tab", "x"))
        if not os.path.exists(fb):
            fb = os.path.join(out, "base", name, sb["cases"][name].get("tab", "x"))
            fn = os.path.join(out, "new", name, r.get("tab", "x"))
        same[name] = (os.path.exists(fb) and os.path.exists(fn) and
                      open(fb, "rb").read() == open(fn, "rb").read())
        lb = np.loadtxt(os.path.join(out, "base", name, "line.txt"))
        ln = np.loadtxt(os.path.join(out, "new", name, "line.txt"))
        d = ln[:, 1] - lb[:, 1]
        lines[name] = {"cells_changed": [[float(x), float(v)] for x, v in
                                         zip(ln[:, 0], d) if v != 0.0]}
    expect_same = [n for n in same if n not in ("cic_fs", "pcs_comp")]
    pc = lines["pcs_comp"]["cells_changed"]
    chk = {
        "D_cic_fs_inert": sn["checks"]["D4"]["pass"] and not sb["checks"]["D4"]["pass"],
        "D_others_identical": all(same[n] for n in expect_same),
        "C0_line_sum": abs(sn["cases"]["pcs_comp"]["line_mass_sum"] - 32.0) < 1e-12,
        "C0_only_face_cells": sorted(round(abs(x), 3) for x, _ in pc) == [8.5, 8.5],
        "C0_change": all(abs(v + 0.0207) < 1e-3 for _, v in pc) and len(pc) == 2,
    }
    res = {"status": st, "tables_identical": same, "line_changes": lines, "checks": chk,
           "base_checks": sb["checks"], "new_checks": sn["checks"],
           "line_mass_sum_pcs_comp": {"base": sb["cases"]["pcs_comp"]["line_mass_sum"],
                                      "new": sn["cases"]["pcs_comp"]["line_mass_sum"]},
           "gain_over_pcs": {"base": sb["cases"]["pcs_comp"].get("gain_over_pcs"),
                             "new": sn["cases"]["pcs_comp"].get("gain_over_pcs")},
           "verdict": "PASS" if all(chk.values()) else "FAIL"}
    json.dump(res, open(os.path.join(out, "compare.json"), "w"), indent=1)
    for k, v in chk.items():
        print(k, "HOLDS" if v else "FAILS")
    print("line sum pcs_comp", res["line_mass_sum_pcs_comp"], "gain", res["gain_over_pcs"])
    print("cells changed pcs_comp", pc)
    print("cells changed cic_fs", lines["cic_fs"]["cells_changed"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(3)
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.3))
    for ax, name, ttl in ((axs[0], "cic_fs", "(a) CIC, deposit_fine_shape, no cap"),
                          (axs[1], "pcs_comp", "(b) PCS with compensation (c = 1/6, c2 = 0.4667)")):
        for c, tag, lab in ((cols[0], "base", "core-v0.8"), (cols[1], "new", "this branch")):
            l = np.loadtxt(os.path.join(out, tag, name, "line.txt"))
            ax.plot(l[:, 0], l[:, 1] - 1.0, "o-", ms=3, lw=0.9, color=c, label=lab)
        ax.axvline(8.0, color="0.6", lw=0.6, ls="--")
        ax.set_xlim(4.0, 13.0)
        ax.set_xlabel(r"$x^1$ (fine level left of the dashed line)")
        ax.set_title(ttl, fontsize=8)
        ax.legend(fontsize=7)
    axs[0].set_ylabel(r"$E/\rho_0 - 1$ on the line $x^2 = x^3 = 0.1$")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_dep_compare"))
    print("DEP COMPARE", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
