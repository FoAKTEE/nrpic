"""Verifier of B-emd-gw, claim C8: sigma scaling of the Zel'dovich GW spectrum of
arXiv:2403.15126 (source pII_GW_Vir_C2_Arx.tex lines 1005, 1031, 1052-1062, 1074),
evaluated with an implementation of my own (mpmath), independent of baseline/scripts.

    python3 v6_za_scaling.py [OUTDIR]

Per configuration (alpha, beta, gamma) = s (0.111, 0.0668, 0.0219) (the shape of the
representative case of arXiv:2605.04487, main_v3.tex line 2275), t_k = 1,
t_col = alpha^(-3/2) (first axis: 1 - alpha (t/t_k)^(2/3) = 0), the spectral shape of
eq. (result_OmZ) at emission,
    F(w) = w S |E_(1/3)(i w t_k) - (t_col/t_k)^(2/3) E_(1/3)(i w t_col)|^2,
    S = alpha^4 + beta^4 + gamma^4 - alpha^2 beta^2 - alpha^2 gamma^2 - beta^2 gamma^2,
with E_n(z) = z^(n-1) Gamma(1-n, z). Measured: the exponents of max F and of w_peak in s.
Also the same peak divided by (1 + z_e) proportional to t_col^(-2/3) (emission during the
matter era at the collapse time, as in result_OmZ where w_0 (1 + z_e) is the emitted
frequency): the scaling of the peak of Omega_GW today if z_e is taken at t_col.

Writes OUTDIR/v6_za_scaling.json and OUTDIR/v6_za_scaling.png.
"""
import json
import os
import sys

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

SHAPE = np.array([0.111, 0.0668, 0.0219])


def En(n, z):
    return z**(n - 1)*mp.gammainc(1 - n, z)


def F(w, lam):
    a, b, g = lam
    S = a**4 + b**4 + g**4 - a*a*b*b - a*a*g*g - b*b*g*g
    tc = a**-1.5
    W = En(mp.mpf(1)/3, 1j*w) - tc**(2.0/3.0)*En(mp.mpf(1)/3, 1j*w*tc)
    return float(w*S*abs(W)**2)


def peak(lam):
    tc = lam[0]**-1.5
    ws = np.logspace(np.log10(0.03/tc), np.log10(30/tc), 121)
    y = np.array([F(w, lam) for w in ws])
    j = int(np.argmax(y))
    ws2 = np.logspace(np.log10(ws[max(j - 1, 0)]), np.log10(ws[min(j + 1, len(ws) - 1)]), 41)
    y2 = np.array([F(w, lam) for w in ws2])
    k = int(np.argmax(y2))
    return ws2[k], y2[k], tc, ws, y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    mp.mp.dps = 20
    s = np.logspace(np.log10(0.02), np.log10(2.0), 9)
    wp, Fp, tcs, curves = [], [], [], []
    for si in s:
        w, f, tc, ws, y = peak(si*SHAPE)
        wp.append(w)
        Fp.append(f)
        tcs.append(tc)
        curves.append((ws, y))
    wp, Fp, tcs = map(np.array, (wp, Fp, tcs))
    ls = np.log(s)
    slope = lambda v: float(np.polyfit(ls, np.log(v), 1)[0])  # noqa: E731
    local = lambda v: (np.diff(np.log(v))/np.diff(ls)).tolist()  # noqa: E731
    today = Fp*tcs**(2.0/3.0)          # divide by (1 + z_e) ~ t_col^(-2/3)
    res = {"s": s.tolist(), "alpha": (s*SHAPE[0]).tolist(), "omega_peak": wp.tolist(),
           "peak": Fp.tolist(), "slope_peak": slope(Fp), "slope_omega_peak": slope(wp),
           "local_slopes_peak": local(Fp), "local_slopes_omega_peak": local(wp),
           "slope_peak_over_1plusz_at_tcol": slope(today),
           "omega_peak_tcol": (wp*tcs).tolist()}
    with open(os.path.join(out, "v6_za_scaling.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if "slope" in k}, indent=1))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    cols = fs.series_colors(len(s))
    for c, (ws, y), si in zip(cols, curves, s):
        ax.loglog(ws, y, color=c, lw=1)
    ax.loglog(wp, Fp, "o", color="k", ms=3, label="peaks")
    ax.set_xlabel(r"$\omega\,t_k$")
    ax.set_ylabel(r"$\omega S |W|^2$ (arb.)")
    ax.legend(loc="lower right", fontsize=8)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    a = s*SHAPE[0]
    ax2.loglog(a, Fp/Fp[0], "o", color=fs.PAL["red"], ms=4, label="peak at emission")
    ax2.loglog(a, (s/s[0])**3.5, **fs.GUIDE, label=r"$\propto s^{7/2}$, $s^{3/2}$")
    ax2.loglog(a, wp/wp[0], "s", color=fs.PAL["blue"], ms=4, label=r"$\omega_{\rm peak}$")
    ax2.loglog(a, (s/s[0])**1.5, **fs.GUIDE)
    ax2.loglog(a, today/today[0], "^", color=fs.PAL["yellow"], ms=4,
               label=r"peak$/(1+z_e)$, $z_e$ at $t_{\rm col}$")
    ax2.loglog(a, (s/s[0])**2.5, color="k", lw=1, ls=":", label=r"$\propto s^{5/2}$")
    ax2.set_xlabel(r"$\alpha$ (largest eigenvalue)")
    ax2.set_ylabel("relative to the smallest $\\alpha$")
    ax2.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(out, "v6_za_scaling"))


if __name__ == "__main__":
    main()
