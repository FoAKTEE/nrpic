"""Figure V5: spatial order of the odd part of H on the L ladder, and the floor against N.

usage: fig_v5.py V45_RUN_DIR CONSTRAINTS_RUN_DIR OUT_BASENAME
Left: log2(odd_N/odd_2N) of H at equal times for 32->64, 64->128, 128->256 (solid), of the
in-band part (dashed); grey band 4-6 (A5). Points where the finer odd part is within three
times its floor are hollow.
Middle: floor (out band of the odd part, over <[H]>) against N at t ~ 0.5, 2, 4, L and P set-ups,
with N^2 and N^2.5 guides.
Right: shell spectrum of the odd part of H at the last common dump for L64, L128, L256
(mean |c_n|^2 per shell), showing where the floor lies in k.
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
spec = np.load(os.path.join(sys.argv[2], "constraints_spec.npz"))
con = json.load(open(os.path.join(sys.argv[2], "constraints.json")))
A5 = r["a5"]
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
ax = [fig.add_axes(b) for b in ([0.07, 0.16, 0.25, 0.76], [0.41, 0.16, 0.24, 0.76], [0.75, 0.16, 0.24, 0.76])]
pairs = [("L32", "L64"), ("L64", "L128"), ("L128", "L256")]
cols = fs.series_colors(3)
for (c_, f_), col in zip(pairs, cols):
    for qty, ls in (("oddH", "-"), ("inbH", "--")):
        k = f"{qty}_{c_}_{f_}"
        if k not in A5:
            continue
        d = A5[k]
        t, p = np.array(d["time"]), np.array(d["order"])
        good = np.array(d["fine"]) > 3 * np.array(d["fine_floor"])
        ax[0].plot(t, p, ls, color=col, lw=1.0, label=f"{c_}->{f_}" if qty == "oddH" else None)
        ax[0].plot(t[good], p[good], "o", ms=3, color=col)
        ax[0].plot(t[~good], p[~good], "o", ms=3, mfc="none", color=col)
ax[0].axhspan(4, 6, color="grey", alpha=0.15)
ax[0].set_ylim(-2, 9)
ax[0].set_xlabel("code time t")
ax[0].set_ylabel("spatial order (odd part of H)")
ax[0].legend(fontsize=6.5, loc="upper right")
fl = A5["floor"]
for tag, mk in (("L", "o"), ("P", "s")):
    for tq, col in zip((0.5, 2.0, 4.0), cols):
        k = f"{tag}_t{tq}"
        if k in fl:
            ax[1].loglog(fl[k]["N"], fl[k]["floor_odd"], mk + "-", ms=4, color=col, lw=1.0,
                         mfc="none" if tag == "P" else col, label=f"{tag} t={tq}")
N = np.array([32, 256])
ax[1].loglog(N, 3e-17 * (N / 32.0) ** 2, **fs.GUIDE)
ax[1].loglog(N, 3e-17 * (N / 32.0) ** 2.5, color="k", lw=1.0, ls=":")
ax[1].text(150, 2.2e-15, "N^2 (dashed), N^2.5 (dotted)", fontsize=6.5, ha="right")
ax[1].set_xticks([32, 64, 128, 256])
ax[1].set_xticklabels(["32", "64", "128", "256"])
ax[1].xaxis.set_minor_formatter(plt.NullFormatter())
ax[1].set_xlabel("N")
ax[1].set_ylabel("floor of H / <[H]>")
ax[1].legend(fontsize=6, ncol=2, loc="upper left")
for k, col in zip(("L64", "L128", "L256"), cols):
    if k not in con:
        continue
    rows = con[k]["rows"]
    for row, ls in ((min(rows, key=lambda x: abs(x["time"] - 2.5)), "-"), (rows[-1], ":")):
        key = f"{k}_c{row['cycle']}_odd"
        if key in spec.files:
            s = spec[key]
            q = np.arange(len(s))
            m = s > 0
            ax[2].loglog(q[m], s[m], ls, color=col, lw=1.0, label=f"{k} t={row['time']:.2f}")
ax[2].axvline(8, **fs.MASK_LINE)
ax[2].axvline(24, **fs.MASK_LINE)
ax[2].set_xlabel("|n| (shell)")
ax[2].set_ylabel("mean |c_n|^2 of odd H", labelpad=1)
ax[2].legend(fontsize=6, loc="lower left", ncol=1)
fs.save(fig, sys.argv[3])
