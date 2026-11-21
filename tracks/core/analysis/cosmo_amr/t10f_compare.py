#!/usr/bin/env python3
"""T10f of the work package cosmo-amr against T10e: the S1 data to t = 3.5 with the lapse
ladder and the fine-shape deposit of the linear cloud in its first-order form (T10e, case
a5, source 3c44b74) and in its integral form (T10f, source 1548d49), with the uniform
spreading (a5c) and without refinement (u5).  Nothing is run here.

    t10f_compare.py --t10e RUNDIR --t10f RUNDIR --out DIR

Writes DIR/t10f_summary.json and DIR/fig_t10f_compare.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t10e", required=True)
    ap.add_argument("--t10f", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    cases = [("u5", a.t10e, "u5", "no refinement"),
             ("a5old", a.t10e, "a5", "ladder, fine shape, first-order form (3c44b74)"),
             ("a5c", a.t10e, "a5c", "ladder, uniform spreading"),
             ("a5new", a.t10f, "a5", "ladder, fine shape, integral form (1548d49)")]
    res, keep = {}, {}
    for key, rd, sub, lab in cases:
        d = os.path.join(rd, sub)
        s = A.read_hst(os.path.join(d, "peak.cstat.hst"))
        g = A.read_hst(os.path.join(d, "peak.region.hst"))
        h = A.read_hst(os.path.join(d, "peak.nrpic.hst"))
        nmb = h["nmb"].astype(int)
        ch = np.where(np.diff(nmb) != 0)[0] + 1
        i0 = int(ch[0]) if len(ch) else 33
        qr = s["Hr_max"][i0+1:]/s["Hr_max"][i0:-1]
        qa = s["H_max"][i0+1:]/s["H_max"][i0:-1]
        res[key] = {"label": lab, "records": int(len(s["time"])),
                    "Hr_max_largest": float(np.max(s["Hr_max"])),
                    "Hr_max_end": float(s["Hr_max"][-1]),
                    "H_max_end": float(s["H_max"][-1]),
                    "largest_cycle_ratio_Hr_from_record_%d" % i0: float(np.max(qr)),
                    "largest_cycle_ratio_H_from_record_%d" % i0: float(np.max(qa)),
                    "H2_over_E2_in_s1_end": float(g["H2_in_s1"][-1]/g["E2_in_s1"][-1]),
                    "region_time_end": float(g["time"][-1]),
                    "E_min_smallest": float(np.min(h["E_min"])),
                    "identity_max": float(np.max(np.abs(h["int_E"]/h["sum_mW"] - 1.0)))}
        for c in (52, 53, 54, 55):
            if c < len(s["time"]):
                res[key]["cycle_%d" % c] = [float(s["time"][c]), float(s["Hr_max"][c]),
                                            float(s["H_max"][c])]
        keep[key] = (s, g)
        print(key, json.dumps(res[key]), flush=True)
    with open(os.path.join(a.out, "t10f_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.9))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.30, top=0.95, wspace=0.30)
    sty = {"u5": "-", "a5old": "-", "a5c": "--", "a5new": "-"}
    for i, (key, _, _, lab) in enumerate(cases):
        s, g = keep[key]
        ax[0].semilogy(s["time"], s["Hr_max"], sty[key], color=fs.SERIES[i], label=lab)
        ax[1].semilogy(s["time"], s["H_max"], sty[key], color=fs.SERIES[i])
        ax[2].semilogy(g["time"], g["H2_in_s1"]/g["E2_in_s1"], sty[key], color=fs.SERIES[i])
    ax[0].set_ylabel(r"largest relative $|H|$")
    ax[1].set_ylabel(r"largest $|H|$")
    ax[2].set_ylabel(r"$\|H\|_2/\|16\pi E\|_2$ inside $r=2.45$")
    for q in ax:
        q.set_xlabel("conformal time")
        q.set_xlim(1.8, 3.55)
        q.axvline(2.205, color="grey", lw=0.5, ls=":")
    ax[0].set_ylim(3e-3, 0.3)
    ax[1].set_ylim(3e-4, 1e-2)
    ax[2].set_ylim(2e-3, 6e-2)
    ax[0].legend(frameon=False, fontsize=7.5, ncol=2, loc="upper left",
                 bbox_to_anchor=(0.0, -0.22))
    fs.save(fig, os.path.join(a.out, "fig_t10f_compare"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
