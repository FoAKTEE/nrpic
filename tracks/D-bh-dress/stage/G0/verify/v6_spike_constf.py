#!/usr/bin/env python3
"""Verifier check C6 (D-pre-2 reference): density of bound, non-captured particles with a
constant distribution function f0 around a Schwarzschild hole (G = c = m = 1), by my own
quadrature over momenta in the static orthonormal frame:

    n(r) = 2 pi f0 int_0^pmax p^2 dp int_-1^1 dcos(alpha) [allowed]
    E = sqrt(1 - 2/r) sqrt(1 + p^2) < 1,   L = r p sin(alpha) >= L_min(E, r),
    L_min = max(L_c(E), L_u(r)),  L_c(E): V_max(L) = E^2 (2 sqrt 3 below E^2 = 8/9),
    L_u(r)^2 = r^2/(r - 3) for 3 < r < 6 (inside the barrier peak the orbit plunges);
    n = 0 for r <= 3 (every orbit there is inside its barrier peak).

(SFW's rho = sqrt(-g00) J^0 is the rest-mass density in the static frame, which is this
n for unit mass.) L_c from my own root of the effective potential, compared with SFW
eq. (Lcrit) (1305.2619 SFWpaper.tex:380). Then: zero at r <= 4, peak ratios against
Gondolo-Silk (8 Gm) and the 4 Gm variant (SFWpaper.tex:443: GS a factor three below the
relativistic peak; the 4 Gm variant 15 percent above it), and the track's rho_constf_rel.

Usage: v6_spike_constf.py [--out DIR] [--figdir DIR]
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def Vmax(L):
    ru = (L * L / 2) * (1 - math.sqrt(max(0.0, 1 - 12 / (L * L))))
    return (1 - 2 / ru) * (1 + L * L / ru ** 2)


def Lc(E):
    if E * E <= 8 / 9:
        return math.sqrt(12)
    return brentq(lambda L: Vmax(L) - E * E, math.sqrt(12), 1e3, xtol=1e-14)


def Lc_sfw(E):
    return math.sqrt(32 / (36 * E ** 2 - 27 * E ** 4 - 8 + E * (9 * E ** 2 - 8) ** 1.5))


# fast L_c(E): the critical orbit is the unstable circular orbit r_u in [4, 6]:
# L^2 = r_u^2/(r_u - 3), E^2 = V = (r_u - 2)^2/(r_u (r_u - 3)) (from V and dV/dr = 0);
# tabulated densely and interpolated in E, checked against the root finder Lc above.
_RU = np.linspace(4.0, 6.0, 200001)
_EC = (_RU - 2) / np.sqrt(_RU * (_RU - 3))
_LC = _RU / np.sqrt(_RU - 3)
_O = np.argsort(_EC)
_EC, _LC = _EC[_O], _LC[_O]


def Lc_fast(E):
    E = np.asarray(E, float)
    out = np.interp(E, _EC, _LC)
    out = np.where(E * E <= 8 / 9, math.sqrt(12), out)
    return np.where(E >= 1, 4.0, out)


_GL = {}


def _gl(n):
    if n not in _GL:
        _GL[n] = np.polynomial.legendre.leggauss(n)
    return _GL[n]


def n_constf(r, npts=4000):
    if r <= 3:          # inside the photon sphere every orbit plunges (r < r_u for all L)
        return 0.0
    pmax = math.sqrt(2 / (r - 2))
    # Gauss-Legendre in s with p = pmax (1 - (1 - s)^2) clustering near pmax
    xs, ws = _gl(npts)
    s = 0.5 * (xs + 1)
    w = 0.5 * ws
    p = pmax * (1 - (1 - s) ** 2)
    jac = pmax * 2 * (1 - s)
    E = math.sqrt(1 - 2 / r) * np.sqrt(1 + p * p)
    Lu = math.sqrt(r * r / (r - 3)) if 3 < r < 6 else 0.0
    Lmin = np.maximum(Lc_fast(np.minimum(E, 1.0)), Lu)
    x = Lmin / (r * p)
    cstar = np.sqrt(np.clip(1 - x * x, 0, None))
    cstar[x >= 1] = 0.0
    return float(4 * math.pi * np.sum(w * jac * p * p * cstar))


def gs(r, rc):
    return 4 * math.pi / 3 * (2 / r) ** 1.5 * max(0.0, 1 - rc / r) ** 1.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    Es = np.linspace(0.9429, 0.99999, 30)
    res["Lc_vs_sfw_max_rel"] = float(max(abs(Lc(e) / Lc_sfw(e) - 1) for e in Es))
    res["Lc_E1"] = Lc(1.0)
    res["Lc_fast_vs_root_max_rel"] = float(max(abs(float(Lc_fast(e)) / Lc(e) - 1) for e in Es))
    r = np.concatenate([np.linspace(3.0, 4.0, 11), np.linspace(4.02, 12, 400), np.logspace(math.log10(12.1), 3, 120)])
    n1 = np.array([n_constf(x, 2000) for x in r])
    n2 = np.array([n_constf(x, 4000) for x in r])
    res["quadrature_conv_max_rel"] = float(np.max(np.abs(n1 - n2)[n2 > 0] / n2[n2 > 0]))
    res["n_at_r_le_4_max"] = float(np.max(n2[r <= 4.0]))
    res["n_at_4.02"] = float(n2[r > 4][0])
    g8 = np.array([gs(x, 8.0) for x in r])
    g4 = np.array([gs(x, 4.0) for x in r])
    newt = 4 * math.pi / 3 * (2 / r) ** 1.5
    i = np.argmax(n2)
    res["peak_rel"] = {"r": float(r[i]), "n": float(n2[i])}
    res["peak_gs8"] = {"r": float(r[np.argmax(g8)]), "n": float(g8.max())}
    res["peak_gs4"] = {"r": float(r[np.argmax(g4)]), "n": float(g4.max())}
    res["ratio_peak_rel_over_gs8"] = float(n2.max() / g8.max())
    res["ratio_peak_gs4_over_rel"] = float(g4.max() / n2.max())
    res["n_over_newton_at_1000"] = float(n2[-1] / newt[-1])
    # the track's implementation
    try:
        sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "spike")))
        import spike_lib as sl
        rt = sl.rho_constf_rel(r)
        m = n2 > 1e-3 * n2.max()
        res["track_rho_constf_rel_max_rel_diff"] = float(np.max(np.abs(rt[m] / n2[m] - 1)))
        res["track_rho_constf_rel_at_r_le_4"] = float(np.max(np.abs(rt[r <= 4.0])))
        res["track_rho_constf_rel_at_4.02"] = float(rt[r > 4][0])
    except Exception as e:  # noqa: BLE001
        res["track_error"] = repr(e)
        rt = None
    with open(os.path.join(a.out, "v6_spike_constf.json"), "w") as f:
        json.dump(res, f, indent=1)
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    for x in ax:
        x.plot(r, n2, color=fs.PAL["red"], lw=2.0, label="verifier quadrature (relativistic)")
        if rt is not None:
            x.plot(r, rt, color=fs.PAL["blue"], lw=1.0, ls="--", label="track rho_constf_rel")
        x.plot(r, g8, color="k", lw=1.0, label="GS (8 Gm)")
        x.plot(r, g4, color="grey", lw=1.0, ls=":", label="GS with 4 Gm")
        x.axvline(4.0, **fs.MASK_LINE)
        x.set_xlabel(r"$r/Gm$")
    ax[0].set_xlim(3, 40); ax[0].set_ylabel(r"$\rho / f_0$")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlim(3, 1000); ax[1].set_ylim(1e-4, 3)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v6_spike_constf"))
    shutil.copy(files[1], a.figdir)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
