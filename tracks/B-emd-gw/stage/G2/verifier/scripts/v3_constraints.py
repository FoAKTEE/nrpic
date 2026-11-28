#!/usr/bin/env python3
"""V5 (constraints, C3) and V6 (the stop of the 256^3 zero-shift box) from the cstat
histories, with my own interpolation (linear in t of log q onto the times of the member
named first; no extrapolation).

    python3 v3_constraints.py OUTDIR SCRATCH
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402
import figstyle as fs  # noqa: E402

out, S = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
R = {
    "p8_64": "B-20261127-232258-37c6773",
    "p8_128_cut": "B-20261124-223926-33194d9",
    "p8_128_cont": "B-20261125-221742-5100a22/p8_cont",
    "zs_128": "B-20261123-014847-f295ab4",
    "zs_256": "B-20261125-093500-242d3a3",
    "gd_128": "B-20261124-210431-6bf48af",
    "gd_256": "B-20261126-105021-6343c13",
}
H = {}
for k, v in R.items():
    if k != "p8_128_cont":
        H[k] = vlib.read_hst(os.path.join(S, v, "pop.cstat.hst"))
# the continuation's history has no header line: the columns of the cut run (same build)
H["p8_128_cont"] = vlib.read_hst(os.path.join(S, R["p8_128_cont"], "pop.cstat.hst"),
                                 cols=list(H["p8_128_cut"].keys()))
res = {"runs": R}

# continuation against the cut run on their common times
cut, con = H["p8_128_cut"], H["p8_128_cont"]
common = np.intersect1d(cut["time"], con["time"])
dmax = 0.0
for c in ("Hr_mean", "Mr_mean", "H_mean", "M_mean"):
    i1 = np.searchsorted(cut["time"], common)
    i2 = np.searchsorted(con["time"], common)
    d = np.abs(con[c][i2]/cut[c][i1] - 1)
    dmax = max(dmax, float(d.max()))
res["continuation"] = {"n_common": int(len(common)), "t_common": [float(common.min()), float(common.max())] if len(common) else None,
                       "max_rel_diff": dmax}
# joined 8-per-cell 128^3 history: cut run up to the first time of the continuation
t0c = con["time"][0]
joined = {c: np.concatenate([cut[c][cut["time"] < t0c], con[c]]) for c in cut}
H["p8_128"] = joined


def ratio(num, den, col):
    """q_num/q_den at the times of num inside the time range of den."""
    tn, td = H[num]["time"], H[den]["time"]
    m = (tn >= td.min()) & (tn <= td.max())
    qd = np.exp(np.interp(tn[m], td, np.log(H[den][col])))
    return tn[m], H[num][col][m]/qd


def extremes(t, r, amin, amax=1e9):
    a = vlib.scale(t)
    m = (a >= amin) & (a <= amax)
    if not m.any():
        return None
    return {"min": float(r[m].min()), "max": float(r[m].max()), "a_min": float(a[m][np.argmin(r[m])]),
            "a_max": float(a[m][np.argmax(r[m])]), "a_range": [float(a[m].min()), float(a[m].max())]}


pairs = {"p8_64_over_128": ("p8_64", "p8_128"), "zs_128_over_256": ("zs_128", "zs_256"),
         "gd_128_over_256": ("gd_128", "gd_256"), "ppc1_over_ppc8_128": ("zs_128", "p8_128")}
series = {}
for name, (a_, b_) in pairs.items():
    res[name] = {}
    for col in ("Hr_mean", "Mr_mean", "H_mean"):
        t, r = ratio(a_, b_, col)
        series[name, col] = (t, r)
        res[name][col] = {"25-141": extremes(t, r, 25, 141), "36-": extremes(t, r, 36), "49-": extremes(t, r, 49),
                          "36-100": extremes(t, r, 36, 100), "le31": extremes(t, r, 1.01, 31),
                          "at_a25": float(np.interp(25.0, vlib.scale(t), r)),
                          "last": {"a": float(vlib.scale(t[-1])), "r": float(r[-1])}}
# sensitivity to the pairing: the other direction (times of den, num interpolated) and
# nearest records without interpolation
def ratio_rev(num, den, col):
    tn, td = H[num]["time"], H[den]["time"]
    m = (td >= tn.min()) & (td <= tn.max())
    qn = np.exp(np.interp(td[m], tn, np.log(H[num][col])))
    return td[m], qn/H[den][col][m]


def ratio_nearest(num, den, col):
    tn, td = H[num]["time"], H[den]["time"]
    j = np.array([int(np.argmin(np.abs(td - x))) for x in tn])
    ok = np.abs(td[j] - tn) < 0.13
    return tn[ok], H[num][col][ok]/H[den][col][j[ok]]


res["pairing_sensitivity"] = {}
for name, (a_, b_) in pairs.items():
    for col in ("Hr_mean", "Mr_mean"):
        for lab, fn in (("reverse", ratio_rev), ("nearest", ratio_nearest)):
            t, r = fn(a_, b_, col)
            res["pairing_sensitivity"][f"{name}:{col}:{lab}"] = {
                "25-141": extremes(t, r, 25, 141), "36-100": extremes(t, r, 36, 100), "49-": extremes(t, r, 49)}
# last record against last record (the particle leg ends at different a in the two runs)
for col in ("Hr_mean", "Mr_mean"):
    res["ppc1_over_ppc8_128"][col]["last_vs_last"] = {
        "a1": float(vlib.scale(H["zs_128"]["time"][-1])), "a8": float(vlib.scale(H["p8_128"]["time"][-1])),
        "r": float(H["zs_128"][col][-1]/H["p8_128"][col][-1])}
# where the 8-per-cell ratio is below 1 before a = 31
t, r = series["p8_64_over_128", "Hr_mean"]
a_ = vlib.scale(t)
res["p8_64_over_128"]["Hr_mean"]["below1_a"] = a_[(r < 1) & (a_ > 1.01)].tolist()
# the particle leg at a = 141
for col in ("Hr_mean", "Mr_mean"):
    t, r = series["ppc1_over_ppc8_128", col]
    res["ppc1_over_ppc8_128"][col]["at_a141"] = float(np.interp(141.0, vlib.scale(t), r))
res["p8_64_last_a"] = float(vlib.scale(H["p8_64"]["time"][-1]))
res["p8_128_last_a"] = float(vlib.scale(H["p8_128"]["time"][-1]))

# V6: the zero-shift 256^3 stop
z = H["zs_256"]
a = vlib.scale(z["time"])
fin = np.isfinite(z["K_max"])
pos = np.nonzero(fin & (z["K_max"] > 0))[0]
i0 = pos[0] if len(pos) else None
stop = {"a_last_record": float(a[fin][-1]), "K_max_last": float(z["K_max"][fin][-1]),
        "t_last_record": float(z["time"][fin][-1])}
if i0 is not None and i0 > 0:
    # linear crossing of K_max = 0 between the two records
    k1, k2 = z["K_max"][i0-1], z["K_max"][i0]
    stop["a_first_positive_record"] = float(a[i0])
    stop["a_K_max_zero_interp"] = float(a[i0-1] + (a[i0]-a[i0-1])*(-k1)/(k2-k1))
    # does it stay positive afterwards?
    stop["K_max_positive_after_first"] = bool(np.all(z["K_max"][i0:][fin[i0:]] > 0))
g = os.path.join(S, R["zs_256"], "pop.guard.txt")
stop["guard"] = open(g).read().strip().splitlines()[:2] if os.path.exists(g) else None
res["stop_zs256"] = stop
gd = H["gd_256"]
res["gd_256_Kmax_after_t9"] = float(gd["K_max"][gd["time"] > 9].max())
res["gd_128_Kmax_after_t9"] = float(H["gd_128"]["K_max"][H["gd_128"]["time"] > 9].max())
res["gd_256_last_a"] = float(vlib.scale(gd["time"][-1]))

json.dump(res, open(os.path.join(out, "v3_constraints.json"), "w"), indent=1)
print(json.dumps({k: res[k] for k in ("continuation", "stop_zs256")}, indent=1))
for name in pairs:
    for col in ("Hr_mean", "Mr_mean"):
        print(name, col, res[name][col]["25-141"], res[name][col]["49-"])

# figure: ratio of the mean constraints when the spacing halves, both samplings
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, axs = plt.subplots(1, 2, figsize=(8, 3.2), sharey=True)
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.92, wspace=0.05)
for ax, col, lab in ((axs[0], "Hr_mean", "Hamiltonian"), (axs[1], "Mr_mean", "momentum")):
    for name, c, ls, txt in (("p8_64_over_128", fs.PAL["red"], "-", r"8 per cell: $64^3/128^3$, zero shift"),
                             ("zs_128_over_256", fs.PAL["blue"], "-", r"1 per cell: $128^3/256^3$, zero shift"),
                             ("gd_128_over_256", fs.PAL["blue"], "--", r"1 per cell: $128^3/256^3$, Gamma driver"),
                             ("ppc1_over_ppc8_128", fs.PAL["yellow"], ":", r"$128^3$: 1 over 8 per cell")):
        t, r = series[name, col]
        m = vlib.scale(t) >= 2.0          # the t = 0 ratio is that of the initial-data residuals
        ax.plot(vlib.scale(t)[m], r[m], color=c, ls=ls, label=txt)
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.axhspan(1.6, 2.3, color=fs.PAL["red"], alpha=0.08)
    ax.axhspan(1.05, 1.4, color=fs.PAL["blue"], alpha=0.08)
    ax.set_xscale("log")
    ax.set_ylim(0.8, 5.0)
    ax.set_xlabel(r"$a$")
    ax.set_title(f"mean relative {lab} constraint", fontsize=10)
axs[0].set_ylabel("ratio of the means (bands: the claims)")
axs[0].legend(loc="upper left", fontsize=8, frameon=False)
fs.save(fig, os.path.join(out, "v3_constraints"))
