"""Figure V3: freezing of super-horizon modes.

usage: fig_v3.py V123_RUN_DIR OUT_BASENAME
Left: |R_n|^2 against e-folds for |n| = 1, 2, 7 of P256: NR (red), my full MS (blue dashed),
my deformed (FLRW-lattice) MS (yellow); crossing marked.
Right: for every mode with N_f - N_k >= 6 of every t = 8.5 rung, the NR power ratio between
N_k + 4 and N_f over the full-MS ratio, minus 1, and the deformed-equation ratio for scale.
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
d = np.load(os.path.join(sys.argv[1], "v123_fig.npz"))
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
a1 = fig.add_axes([0.08, 0.14, 0.40, 0.78])
a2 = fig.add_axes([0.58, 0.14, 0.40, 0.78])
for q, mk in zip((1, 2, 7), ("o", "s", "^")):
    key = f"v3_P256_mode{q}"
    if key not in d.files:
        continue
    N, pN, pM, pD, Nk = d[key]
    s = pM[-1]
    a1.semilogy(N, pN / s, mk, ms=3, mfc="none", color=fs.PAL["red"], label=f"NR |n| = {q}")
    a1.semilogy(N, pM / s, "--", color=fs.PAL["blue"], lw=1.2)
    late = N >= Nk[0] + 1.0          # the deformed curve carries no window: shown once W ~ 1
    a1.semilogy(N[late], pD[late] / s, "-", color=fs.PAL["yellow"], lw=1.2)
    a1.axvline(Nk[0], **fs.MASK_LINE)
a1.plot([], [], "--", color=fs.PAL["blue"], label="my full MS")
a1.plot([], [], "-", color=fs.PAL["yellow"], label="deformed MS (FLRW lattice)")
a1.set_xlabel("e-folds N - N*")
a1.set_ylabel(r"|R$_n$|$^2$ / full MS at N$_f$")
a1.set_ylim(0.5, 1.5)
a1.set_yscale("linear")
a1.set_xlim(0, 9.2)
a1.legend(fontsize=7, loc="upper right", ncol=2)
keys = [k for k in ("L32p", "L64p", "L128p", "Q64p", "Q128p", "P256") if f"v3_{k}" in d.files]
cols = fs.series_colors(len(keys))
for k, c in zip(keys, cols):
    r = d[f"v3_{k}"]
    a2.semilogy(r[0], np.abs(r[3] / r[4] - 1), "o", ms=3, color=c, label=k, alpha=0.8)
r = d["v3_P256"]
a2.semilogy(r[0], np.abs(r[5] / r[4] - 1), "s", ms=3, mfc="none", color="k", label="deformed/full - 1")
a2.axhline(0.01, **fs.GUIDE)
a2.set_xlabel("|n| = k/dk (modes with N_f - N_k >= 6)")
a2.set_ylabel(r"|ratio$_{NR}$/ratio$_{MS}$ - 1|, N$_k$+4 to N$_f$")
a2.set_ylim(1e-9, 1)
a2.legend(ncol=2, fontsize=7, loc="center right")
fs.save(fig, sys.argv[2])
