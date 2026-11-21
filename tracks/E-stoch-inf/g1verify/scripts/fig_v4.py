"""Figure V4: odd and even parts of H (rms over <[H]>), halving factors, negative controls.

usage: fig_v4.py V45_RUN_DIR OUT_BASENAME
Top left: paper's set-up Q64, Q128, P256: odd (solid), even without mean (dashed), floor
(dotted); vertical marks where k_max enters.
Top right: L set-up L32, L64, L128, L256, same lines.
Bottom left: halving factors of the odd (expect 2) and even (expect 4) parts of H for L32,
Q64, Q128 where above ten times the floor; record halving factor F_H (thin).
Bottom right: negative controls NC32, NC64, NC128 against their proper runs (odd part).
"""
import sys
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
r = json.load(open(os.path.join(sys.argv[1], "v45.json")))
S = r["sets"]
fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.4))
ax = [fig.add_axes(b) for b in ([0.08, 0.56, 0.40, 0.40], [0.58, 0.56, 0.40, 0.40],
                                 [0.08, 0.07, 0.40, 0.40], [0.58, 0.07, 0.40, 0.40])]
for a, keys in ((ax[0], ("Q64", "Q128", "P256")), (ax[1], ("L32", "L64", "L128", "L256"))):
    cols = fs.series_colors(len(keys))
    for k, c in zip(keys, cols):
        if k not in S:
            continue
        o = S[k]
        t = np.array(o["time"])
        a.semilogy(t[1:], np.array(o["oddH"])[1:], "-", color=c, lw=1.3, label=f"{k} odd")
        a.semilogy(t[1:], np.array(o["evenH"])[1:], "--", color=c, lw=1.3, label="even")
        a.semilogy(t[1:], np.array(o["floorH"])[1:], ":", color=c, lw=1.0)
        a.axvline(o["t_kmax_enters"], color=c, lw=0.8, alpha=0.5)
    a.set_xlabel("code time t")
    a.set_ylabel("rms part of H / <[H]>")
    a.set_ylim(1e-17, 1e-8)
    a.legend(ncol=2, fontsize=6.5, loc="lower right")
ax[0].set_title("paper's set-up (k_max = N/4); dotted: floor", fontsize=9)
ax[1].set_title("L set-up (k_max = 8 dk)", fontsize=9)
cols = fs.series_colors(3)
for k, c in zip(("L32", "Q64", "Q128"), cols):
    if k not in S or "F_oddH" not in S[k]:
        continue
    o = S[k]
    t = np.array(o["time"])
    fo, fe = np.array(o["F_oddH"]), np.array(o["F_evenH"])
    mo, me = np.array(o["above_floor_odd"]), np.array(o["above_floor_even"])
    mo[0] = me[0] = False
    ax[2].plot(t[mo], fo[mo], "o-", ms=3, color=c, lw=1.0, label=f"{k} odd")
    ax[2].plot(t[me], fe[me], "s--", ms=3, mfc="none", color=c, lw=1.0, label=f"{k} even")
    key = f"{k}_recF"
    if key in r["figdata"]:
        th, FH, FM = (np.array(x) for x in r["figdata"][key])
        ax[2].plot(th[th > 0.3], FH[th > 0.3], "-", color=c, lw=0.6, alpha=0.6)
for y in (2.0, 4.0):
    ax[2].axhline(y, **fs.GUIDE)
ax[2].set_ylim(1.0, 5.0)
ax[2].set_xlabel("code time t")
ax[2].set_ylabel("halving factor C(s=1)/C(s=1/2)")
ax[2].legend(ncol=2, fontsize=6.5, loc="lower left")
ax[2].set_title("thin: record <|H|/[H]> factor", fontsize=9)
for (ncs, prop), c in zip((("NC32", "L32"), ("NC64", "Q64"), ("NC128", "Q128")), cols):
    if ncs not in S or prop not in S:
        continue
    a, b = S[ncs], S[prop]
    n = min(len(a["time"]), len(b["time"]))
    t = np.array(a["time"][1:n])
    ax[3].semilogy(t, np.array(a["oddH"][1:n]), "-", color=c, lw=1.3, label=f"{ncs} odd")
    ax[3].semilogy(t, np.array(b["oddH"][1:n]), "--", color=c, lw=1.3, label=f"{prop} odd")
ax[3].set_xlabel("code time t")
ax[3].set_ylabel("rms odd part of H / <[H]>")
ax[3].set_title("negative controls (noise_pi_sign = -1)", fontsize=9)
ax[3].legend(ncol=2, fontsize=6.5, loc="lower right")
ax[3].set_ylim(1e-15, 1e-3)
fs.save(fig, sys.argv[2])
