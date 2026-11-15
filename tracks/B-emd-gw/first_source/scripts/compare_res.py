#!/usr/bin/env python3
"""P8 of JOURNAL.md: the scan at 32^3 (processors) against 64^3 (cards).

    python3 compare_res.py <dir with the 32^3 case JSON> <dir(s) with the 64^3 case JSON>

Interpolates c_+(K1) of each case of the coarse run to the dump times of the fine run and
writes res_compare.json and res_compare.{png,pdf} to $NRPIC_RUN_DIR.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import reference as ref  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

EPS = {"cw_eps0p1": 0.1, "cw_eps0p3": 0.3, "cw_eps1": 1.0, "cw_eps1_gd": 1.0}


def load(dirs):
    out = {}
    for d in dirs:
        for f in glob.glob(os.path.join(d, "cw_*.json")):
            c = json.load(open(f))
            rows = [r for r in c["rows"] if r.get("kind") == "bin" and "error" not in r]
            rows.sort(key=lambda r: r["time"])
            out[c["case"]] = rows
    return out


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    coarse = load([sys.argv[1]])
    fine = load(sys.argv[2:])
    s1 = ref.static_amplitude(0.01, 1.0)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    col = {"cw_eps0p1": fs.PAL["yellow"], "cw_eps0p3": fs.PAL["red"], "cw_eps1": fs.PAL["blue"],
           "cw_eps1_gd": fs.PAL["green"]}
    res = {}
    for name, e in EPS.items():
        if name not in coarse or name not in fine:
            continue
        tc = np.array([r["time"] for r in coarse[name]])
        cc = np.array([r["h_K1_plus"][0] for r in coarse[name]])
        tf = np.array([r["time"] for r in fine[name]])
        cf = np.array([r["h_K1_plus"][0] for r in fine[name]])
        sel = (tf > 0.05) & (tf <= tc.max())
        a = ref.a_of_tau(tf[sel])
        cci = np.interp(tf[sel], tc, cc)
        rel = cci / cf[sel] - 1
        lab = r"$\epsilon=%g$" % e + (" (Gamma driver)" if name.endswith("_gd") else "")
        ax[0].semilogx(a, cci / (s1 * e), color=col[name], lw=1.0, ls="--")
        ax[0].semilogx(a, cf[sel] / (s1 * e), color=col[name], lw=1.5, label=lab)
        ax[1].semilogx(a, rel, color=col[name], label=lab)
        res[name] = {"max_abs_rel_a_le_20": float(np.max(np.abs(rel[a <= 20]))) if np.any(a <= 20) else None,
                     "rel_at_a": {str(av): float(np.interp(av, a, rel)) for av in (5, 10, 20, 40, 60, 80, 100, 140)
                                  if av <= a.max()}}
        # non-TT part and null quantities at both resolutions
        nc = np.array([r["rms_nonTT"] for r in coarse[name]])
        nf = np.array([r["rms_nonTT"] for r in fine[name]])
        res[name]["nonTT_ratio_32_over_64_at_a"] = {
            str(av): float(np.interp(av, ref.a_of_tau(tc), nc) / np.interp(av, ref.a_of_tau(tf), nf))
            for av in (10, 40, 100, 140) if av <= a.max()}
    ax[0].set_ylabel(r"$c_+(K_1)/(s\epsilon)$: $64^3$ solid, $32^3$ dashed")
    ax[1].set_ylabel(r"$c_+(32^3)/c_+(64^3)-1$")
    ax[1].set_ylim(-0.2, 0.2)
    ax[1].axhline(0, **fs.MASK_LINE)
    for x in ax:
        x.set_xlabel(r"$a$")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "res_compare"))
    with open(os.path.join(out, "res_compare.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
