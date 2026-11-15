"""Figure: horizon-mass history of a vacuum puncture, the noise floor of the null test.

Reads the raw finder output punc.horizon_summary_0.txt of the two card runs drift8 (M/8)
and drift16 (M/16), 500 M each, and the helper's floors (drift_ana, drift_drift.json).
Panel (a): apparent-horizon mass minus the bare mass. Panel (b): change of the 20 M running
mean relative to its value at 50 M, with the helper's smallest detectable change at M/16
for windows that start at 50 M and end before 210 M. Check P2 of the note journal: drift
of the running mean from 50 to 490 M, written to fig_floor_numbers.json.
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

STEM = "fig_floor"
W = 20.0


def main():
    out = C.out_dir("figures")
    ana = C.load_json("drift_ana", "drift_drift.json")
    lead = C.load_json("drift_lead", "lead_drift_recheck.json")
    floor16 = ana["floors"]["50:210"]["M/16"]
    nums = {"floor_50_210_M16": {k: v["dM_min"] for k, v in floor16.items()}}
    cz.use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.75))
    fig.subplots_adjust(left=0.09, right=0.975, bottom=0.17, top=0.97, wspace=0.3)
    for key, lab, c in (("drift8", r"$\Delta x=M/8$", cz.PAL["red"]),
                        ("drift16", r"$\Delta x=M/16$", cz.PAL["blue"])):
        t, m, s = C.horizon_series(key)
        rm = C.running_mean(t, m, W)
        rm5 = C.running_mean(t, m, 5.0)
        ok = np.isfinite(rm)
        m50 = float(np.interp(50.0, t[ok], rm[ok]))
        D = rm / m50 - 1
        sel = (t >= 50) & (t <= 210)
        bd = (t >= 220) & (t <= 255)
        nums[key] = dict(run=C.RUNS[key], n=int(t.size), t_last=float(t[-1]),
                         M_minus_1_at_100=float(np.interp(100.0, t, m) - 1),
                         drift_50_490=float(np.interp(490.0, t[ok], rm[ok]) - m50),
                         last_finite_mean_at=float(t[ok][-1]),
                         maxabsD_50_210=float(np.nanmax(np.abs(D[sel]))),
                         p2p_rm5_220_255=float(np.nanmax(rm5[bd]) - np.nanmin(rm5[bd])),
                         max_S_over_M2_after5=float(np.max(np.abs(s[t > 5]) / m[t > 5] ** 2)),
                         lead_drift_50_490=lead[lab.split("=")[1].strip("$")]["drift_50_490"])
        a.plot(t, (m - 1) * 1e3, color=c, lw=0.8, label=lab)
        b.plot(t, D * 1e5, color=c, lw=1.2, label=lab)
    a.axvspan(220, 255, color="grey", alpha=0.15, lw=0)
    b.axvspan(220, 255, color="grey", alpha=0.15, lw=0)
    f = max(nums["floor_50_210_M16"].values())
    b.fill_between([50, 210], [-f * 1e5] * 2, [f * 1e5] * 2, color=cz.PAL["blue"], alpha=0.15, lw=0)
    a.set_xlim(0, 500)
    a.set_ylim(-1.0, 2.0)
    a.set_xlabel(r"coordinate time $t/M$")
    a.set_ylabel(r"$(M_{\rm AH}-M)/M\ [10^{-3}]$")
    a.legend(frameon=False, loc="lower right")
    a.text(0.03, 0.92, "(a)", transform=a.transAxes)
    b.set_xlim(0, 500)
    b.set_ylim(-5, 35)
    b.axhline(0, color="k", lw=0.6)
    b.set_xlabel(r"coordinate time $t/M$")
    b.set_ylabel(r"$\bar M_{\rm AH}(t)/\bar M_{\rm AH}(50M)-1\ [10^{-5}]$")
    b.legend(frameon=False, loc="upper left")
    b.text(0.92, 0.92, "(b)", transform=b.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as fh:
        json.dump(nums, fh, indent=1)
    print(json.dumps(nums, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
