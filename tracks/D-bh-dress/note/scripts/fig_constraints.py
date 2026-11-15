"""Figure: constraint residuals of the Einstein-Straus data against the grid spacing.

Panel (a): one-dimensional radial check (fourth-order differences of the exact fields) in
the regions of the slice (run es_offline, offline_check.json, check_1d). Panel (b): the
three-dimensional check in cubic sub-boxes (same run, check_3d, exact fields), and the
residuals that AthenaK itself computes at t = 0 from the format-2 table plus the puncture
in the same boxes at dx = 1 and 1/2 M (run es_t0, code_t0.json). Orders between the two
finest spacings go to fig_constraints_numbers.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401

STEM = "fig_constraints"


def order(h, e):
    return float(np.log(e[-2] / e[-1]) / np.log(h[-2] / h[-1]))


def main():
    out = C.out_dir("figures")
    off = C.load_json("es_offline", "offline_check.json")
    code = C.load_json("es_t0", "code_t0.json")
    nums = {"1d": {}, "3d": {}, "code": {}, "code_regions": code["orders"]}
    cz.use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.75))
    fig.subplots_adjust(left=0.095, right=0.975, bottom=0.17, top=0.97, wspace=0.3)

    reg = off["check_1d"]["regions"]
    sel = [("curvature transition", "H", cz.PAL["blue"], "-", "transition, $H$"),
           ("curvature transition", "M", cz.PAL["blue"], "--", "transition, $M_r$"),
           ("inner dust edge", "M", cz.PAL["red"], "--", "inner dust edge, $M_r$"),
           ("outer dust edge", "M", cz.PAL["yellow"], "--", "outer dust edge, $M_r$")]
    for name, q, c, ls, lab in sel:
        h = np.array(reg[name]["h"])
        e = np.array(reg[name][q]["max_abs"])
        a.loglog(h, e, ls=ls, color=c, marker="o", ms=3.5, label=lab)
        nums["1d"][f"{name} {q}"] = dict(h=h.tolist(), max_abs=e.tolist(),
                                         orders=reg[name][q]["order"])
    hh = np.array([0.1, 0.8])
    a.loglog(hh, 6e-7 * (hh / 0.8) ** 4, label=r"$\propto h^4$", **cz.GUIDE)
    a.set_xticks([0.1, 0.2, 0.4, 0.8])
    a.set_xticklabels(["0.1", "0.2", "0.4", "0.8"])
    a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    a.set_xlabel(r"radial spacing $h/M$")
    a.set_ylabel("largest constraint residual")
    a.set_ylim(1e-12, 1e-4)
    a.legend(loc="upper left", fontsize=7.5, handlelength=1.8)
    a.text(0.92, 0.06, "(a)", transform=a.transAxes)

    boxes = [("start of transition", cz.PAL["green"]), ("mid transition", cz.PAL["blue"]),
             ("inner dust edge", cz.PAL["red"])]
    for name, c in boxes:
        bx = off["check_3d"][name]
        h = np.array(bx["h"])
        H = np.array([e["H_max"] for e in bx["exact"]])
        Mm = np.array([e["M_max"] for e in bx["exact"]])
        b.loglog(h, H, "-", color=c, marker="o", ms=3.5, mfc="white")
        b.loglog(h, Mm, "--", color=c, marker="s", ms=3.0, mfc="white")
        nums["3d"][name] = dict(h=h.tolist(), H_max=H.tolist(), M_max=Mm.tolist(),
                                order_H=order(h, H), order_M=order(h, Mm))
        hc = np.array([1.0, 0.5])
        Hc = np.array([code["dx=1"]["boxes"][name]["H_max"], code["dx=0.5"]["boxes"][name]["H_max"]])
        Mc = np.array([code["dx=1"]["boxes"][name]["M_max"], code["dx=0.5"]["boxes"][name]["M_max"]])
        b.loglog(hc, Hc, "-", color=c, marker="o", ms=4.5, lw=2.2)
        b.loglog(hc, Mc, "--", color=c, marker="s", ms=4.0, lw=2.2)
        nums["code"][name] = dict(dx=hc.tolist(), H_max=Hc.tolist(), M_max=Mc.tolist(),
                                  order_H=order(hc, Hc), order_M=order(hc, Mc))
    for name, c in boxes:
        b.plot([], [], color=c, label=name)
    b.plot([], [], "o", color="grey", mfc="white", ms=3.5, label="offline")
    b.plot([], [], "o", color="grey", ms=4.5, label="AthenaK at $t=0$")
    b.plot([], [], "-", color="grey", label="Hamiltonian")
    b.plot([], [], "--", color="grey", label="momentum")
    b.set_xlabel(r"grid spacing $h/M$")
    b.set_ylabel("largest residual in the box")
    b.set_ylim(1e-11, 10.0)
    b.legend(loc="upper left", fontsize=7.0, handlelength=1.6, ncol=2, columnspacing=0.8)
    b.text(0.92, 0.06, "(b)", transform=b.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps({k: v for k, v in nums.items() if k != "1d"}, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
