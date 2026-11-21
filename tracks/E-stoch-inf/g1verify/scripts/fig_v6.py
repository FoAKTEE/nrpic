"""Figure V6: temporal order from the Courant runs (N = 32, theta = 0.25, 0.125, 0.0625).

usage: fig_v6.py V6_RUN_DIR OUT_BASENAME
Left: Richardson order log2(|D1|/|D2|) (max norm) against time for the odd parts of the
fields and of R^NR (first order), the odd part of H, the box mean of H and of chi.
Right: |D2| = |X(0.125) - X(0.0625)| for H's parts, against the rounding floor.
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
r = json.load(open(os.path.join(sys.argv[1], "v6.json")))
rows = r["rows"][1:]
t = np.array([x["time"] for x in rows])
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
a1 = fig.add_axes([0.08, 0.14, 0.40, 0.78])
a2 = fig.add_axes([0.58, 0.14, 0.40, 0.78])
sel = [("odd_phi", "odd phi"), ("odd_chi", "odd chi"), ("odd_K", "odd K"), ("odd_Axx", "odd A_xx"),
       ("R_odd", "odd R^NR (|n|^2<=8)"), ("odd_H", "odd H"), ("mean_H", "<H> (order s^0)"),
       ("mean_chi", "<chi>")]
cols = fs.series_colors(len(sel))
for (k, lab), c in zip(sel, cols):
    p = np.array([x["orders"][k]["p_max"] if x["orders"][k]["p_max"] is not None else np.nan for x in rows])
    a1.plot(t, p, "o-", ms=3, lw=1.0, color=c, label=lab)
a1.axhspan(3.5, 4.5, color="grey", alpha=0.15)
a1.axhline(4.0, **fs.GUIDE)
a1.set_ylim(-1, 6)
a1.set_xlabel("code time t")
a1.set_ylabel("temporal order")
a1.legend(ncol=2, fontsize=6.5, loc="lower left")
for (k, lab), c in zip([("odd_H", "odd H"), ("evenNM_H", "even H, mean removed"), ("mean_H", "<H>")],
                       fs.series_colors(3)):
    d1 = np.array([x["orders"][k]["D1_max"] for x in rows])
    d2 = np.array([x["orders"][k]["D2_max"] for x in rows])
    sc = np.array([x["orders"][k]["scale"] for x in rows])
    a2.semilogy(t, d1, "o-", ms=3, lw=1.0, color=c, label=f"{lab}: |D1|")
    a2.semilogy(t, d2, "s--", ms=3, lw=1.0, color=c, mfc="none", label="|D2|")
    a2.semilogy(t, sc, ":", lw=1.0, color=c)
a2.axhline(3e-14, **fs.MASK_LINE)
a2.text(0.3, 3.6e-14, "rounding of H at N = 32 (estimate)", fontsize=7)
a2.set_xlabel("code time t")
a2.set_ylabel("max |difference| (dotted: the quantity)")
a2.legend(ncol=1, fontsize=6.5, loc="upper right")
a2.set_ylim(1e-15, 1e-8)
fs.save(fig, sys.argv[2])
