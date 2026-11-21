"""Figure V7: bit-identity across MeshBlock layouts and restart; card against processor.

usage: fig_v7.py V7_RUN_DIR OUT_BASENAME
Left: per comparison, the number of differing 64-bit words summed over all variables (all
fields and the two noise fields) and dumps, with the number compared (bars at zero are
drawn as a marker on the axis).
Right (information, not A7): max |difference| of the perturbations (box mean removed),
relative to their maximum, of the slow-roll L64p on the card against the processors.
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
r = json.load(open(os.path.join(sys.argv[1], "v7.json")))
labels, diff, comp = [], [], []
for u in ("U2", "U3"):
    s = sum(sum(row[f"U1_vs_{u}_differing"].values()) for row in r["layouts"].values())
    n = sum(row[f"U1_vs_{u}_ncells"] * row["nvar"] for row in r["layouts"].values())
    labels.append(f"card U1 vs {u}\n(1 vs {list(r['layouts'].values())[0]['nmb'][u]} MB)")
    diff.append(s)
    comp.append(n)
for lab in ("proc", "card"):
    rr = r["restart"][lab]
    s = sum(sum(x["differing"].values()) for x in rr.values())
    n = 2 * 64 ** 3 * 12
    labels.append(f"{lab} U2 vs U4\n(restart)")
    diff.append(s)
    comp.append(n)
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
a1 = fig.add_axes([0.08, 0.22, 0.40, 0.70])
a2 = fig.add_axes([0.58, 0.14, 0.40, 0.78])
x = np.arange(len(labels))
a1.bar(x, diff, color=fs.PAL["red"])
a1.plot(x, np.zeros(len(x)), "o", color=fs.PAL["red"])
for xi, d, n in zip(x, diff, comp):
    a1.text(xi, 0.15, f"{d} of\n{n:.2e}", ha="center", fontsize=7)
a1.set_xticks(x)
a1.set_xticklabels(labels, fontsize=7)
a1.set_ylim(-0.1, 1)
a1.set_ylabel("differing 64-bit words")
a1.set_title("A7: noise unit test (release core-v0.3)", fontsize=9)
sr = r["cross_platform"]["L64p card vs proc"]
names = ["phi", "Pi", "chi", "K", "gxx", "Axx"]
cols = fs.series_colors(len(names))
# the processor run stops at tlim = 4.5 after a shortened step: its last dump has the cycle
# but not the time of the card dump (t = 4.516), so it is left out
rows = [v for v in sr.values() if 0 < v["time"] < 4.4]
t = np.array([v["time"] for v in rows])
for n, c in zip(names, cols):
    y = np.array([v["max_reldiff_of_perturbation"][n] for v in rows])
    a2.semilogy(t, y, "o-", ms=3, lw=1.0, color=c, label=n)
a2.set_xlabel("code time t")
a2.set_ylabel("max|card - proc| / max|perturbation|")
a2.set_title("L64p: card vs processor (not bit-identical)", fontsize=9)
a2.legend(ncol=3, fontsize=7, loc="upper left")
a2.set_ylim(1e-10, 1e-5)
fs.save(fig, sys.argv[2])
