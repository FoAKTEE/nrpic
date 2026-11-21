#!/usr/bin/env python3
"""Figure of J4/J4b: energy in the window against 1/R at P1's four spheres, with the straight
lines E_inf + a/R through all radii (solid) and through 70 and 90 M (dotted). Left: J4b (window
[-35, 6], record cut at 14) for FFI 0.1, 0.2, 0.3 and the time domain. Right: FFI 0.2 for J4's
windows [-35, 12] and [-35, 50] (whole record) and J4b. Also writes p1_extrap.json (both fits).
Usage: fig_p1_extrap.py <dir | -> [--tags=P1b,P1w12,P1w50]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def fit(R, E):
    A = np.vstack([np.ones(len(R)), 1.0 / np.asarray(R, float)]).T
    c, *_ = np.linalg.lstsq(A, np.asarray(E, float), rcond=None)
    return float(c[0]), float(c[1])


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    tags = ["P1b", "P1w12", "P1w50"]
    for a in sys.argv[2:]:
        if a.startswith("--tags="):
            tags = a[7:].split(",")
    J = {t: json.load(open(os.path.join(d, f"{t}_junk.json"))) for t in tags}
    out = {}
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    x = np.linspace(0, 1 / 38, 50)

    def panel(a, tag, key, col, lab):
        rs = sorted(int(r) for r in J[tag]["radii"])
        rs = [r for r in rs if J[tag]["radii"][str(r)]["complete"]]
        E = [J[tag]["radii"][str(r)][key]["E"] for r in rs]
        a.plot(1 / np.array(rs, float), E, "o", color=col, ms=4, label=lab)
        f_all = fit(rs, E)
        a.plot(x, f_all[0] + f_all[1] * x, color=col, lw=0.9)
        outer = [r for r in rs if r >= 70]
        f_out = fit(outer, [J[tag]["radii"][str(r)][key]["E"] for r in outer]) if len(outer) == 2 \
            else (np.nan, np.nan)
        a.plot(x, f_out[0] + f_out[1] * x, color=col, lw=0.9, ls=":")
        out[f"{tag}/{key}"] = dict(radii=rs, E=E, all=dict(E_inf=f_all[0], a=f_all[1]),
                                   outer=dict(E_inf=f_out[0], a=f_out[1]))

    for key, col, lab in (("ffi0.1", fs.PAL["yellow"], "FFI 0.1"), ("ffi0.2", fs.PAL["blue"], "FFI 0.2"),
                          ("ffi0.3", fs.PAL["green"], "FFI 0.3"), ("td", fs.PAL["red"], "time domain")):
        panel(ax[0], "P1b", key, col, lab)
    for tag, col, lab in (("P1b", fs.PAL["blue"], "J4b [-35, 6], cut 14"),
                          ("P1w12", fs.PAL["red"], "J4 [-35, 12]"),
                          ("P1w50", fs.PAL["green"], "J4 [-35, 50]")):
        if tag in J:
            panel(ax[1], tag, "ffi0.2", col, lab)
    for a in ax:
        a.axhline(0, color="grey", lw=0.6)
        a.set_xlabel(r"$1/R$ [$M^{-1}$]")
        a.set_xlim(0, 1 / 38)
        a.legend(frameon=False, fontsize=7)
    ax[0].set_ylabel(r"$E$ in the window [$M$]")
    ax[0].set_title("J4b, four methods", fontsize=9)
    ax[1].set_title("FFI 0.2, three windows", fontsize=9)
    ax[1].set_yscale("symlog", linthresh=1e-7)
    ax[0].set_yscale("symlog", linthresh=1e-7)
    fig.tight_layout()
    json.dump(out, open(os.path.join(d, "p1_extrap.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    for pth in fs.save(fig, os.path.join(d, "fig_p1_extrap")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
