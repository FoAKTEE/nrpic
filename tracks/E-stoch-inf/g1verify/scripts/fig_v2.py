"""Figure V2: R^NR per mode against W R alpha (my MS), and the shell spectrum against the
slow-roll power at crossing.

usage: fig_v2.py V123_RUN_DIR OUT_BASENAME
Top left: max over k <= k_max/2 of |R^NR/(W R alpha) - 1| against e-folds, every rung.
Top right: per shell at the last dump, max (solid) and median (dotted) of the same.
Bottom: Delta(k)/Delta_SR(crossing) at the last dump of P256: alpha-normalised NR, raw NR,
my full MS.
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
show = [k for k in ("L32p", "L64p", "L128p", "L256p", "Q64p", "Q128p", "P256") if f"v2_{k}_vs_t" in d.files]
cols = fs.series_colors(len(show))
fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.0))
a1 = fig.add_axes([0.08, 0.57, 0.40, 0.38])
a2 = fig.add_axes([0.58, 0.57, 0.40, 0.38])
a3 = fig.add_axes([0.08, 0.08, 0.90, 0.36])
for k, c in zip(show, cols):
    N, mx, _ = d[f"v2_{k}_vs_t"]
    ok = np.isfinite(mx)
    a1.semilogy(N[ok], mx[ok], "o-", ms=2.5, color=c, lw=1.0, label=k)
    ks, smax, smed = d[f"v2_{k}_shell"]
    a2.loglog(ks, smax, color=c, lw=1.0, label=k)
    a2.loglog(ks, smed, color=c, lw=1.0, ls=":")
for a in (a1, a2):
    a.axhline(0.02, **fs.GUIDE)
a1.set_xlabel("e-folds N - N*")
a1.set_ylabel(r"max$_{k\leq k_{max}/2}$ |R$^{NR}$/(W R $\alpha$) - 1|")
a1.set_ylim(1e-7, 1)
a1.legend(ncol=2, fontsize=7, loc="upper right")
a2.set_xlabel("|n| = k/dk")
a2.set_ylabel("per shell at the last dump")
a2.set_ylim(1e-7, 1)
k = "P256"
ks, raw, nrm, ms, M = d[f"v2_{k}_spec"]
a3.semilogx(ks, raw, ".", color=fs.PAL["yellow"], ms=3, label="NR raw (cosmic variance)")
a3.semilogx(ks, nrm, "-", color=fs.PAL["red"], lw=1.5, label=r"NR / |$\alpha$|$^2$")
a3.semilogx(ks, ms, "--", color=fs.PAL["blue"], lw=1.5, label="my full MS")
a3.axhline(1.0, **fs.THIN)
a3.axvline(32, **fs.MASK_LINE)
a3.set_xlabel("|n| = k/dk")
a3.set_ylabel(r"$\Delta_R(N_f)/\Delta_{SR}$(crossing)")
a3.set_ylim(0.5, 1.6)
a3.set_title("P256 at the last dump (N_f - N* = 8.10); grey: k_max/2", fontsize=9)
a3.legend(ncol=3, fontsize=8, loc="upper left")
fs.save(fig, sys.argv[2])
