"""Order-of-magnitude estimates for the scope of Track B (check 3 and the compute table).

    python3 regime_estimates.py OUTDIR

(3A) Junk TT radiation of conformally flat initial data: the TT mode of wave number G
starts at h = h' = 0 while its quasi-static value is h_s; integrate
h'' + 2 Hc h' + G^2 h = G^2 h_s in conformal time with a = (1 + t/2)^2, Hc = 1/(1 + t/2)
(the units of cosmo/README.md), and measure the envelope of h - h_s.
(3B) Virial GW frequency at the collapse epoch against the lowest box wave numbers for
the single-wavelength boxes of cosmo/ (box of 2, 4, 8 initial Hubble radii).
(3C) Card time of the planned runs from the measured throughput of two runs of cosmo/.

Writes OUTDIR/regime_estimates.json and OUTDIR/regime_estimates.png.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import argrelextrema

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

# measured throughput and memory (zone-cycles per second on one A100, 1 particle per cell)
# runs/cosmo/east_d0.01_n64_pcs4b/athena.20261114-072656.log: 64^3, 1404 cycles, 63.8 s
# runs/cosmo/dav_c256_n128_pcs4bt/athena.20261114-021442.log: 128^3, 1301.8 s
RATE = {64: 5.770348e6, 128: 4.467127e6}
MEM_MIB = {64: 1685, 128: 5083}
DELTA_VIR = 18*np.pi**2        # spherical-collapse overdensity [BACKGROUND]


def junk(G, hs=1.0, a_end=200.0):
    t_end = 2*(np.sqrt(a_end) - 1)

    def rhs(t, y):
        Hc = 1.0/(1.0 + 0.5*t)
        return [y[1], -2*Hc*y[1] - G*G*(y[0] - hs)]
    t = np.linspace(0, t_end, 200001)
    sol = solve_ivp(rhs, (0, t_end), [0.0, 0.0], t_eval=t, rtol=1e-11, atol=1e-14,
                    method="DOP853")
    a = (1 + 0.5*sol.t)**2
    dev = np.abs(sol.y[0] - hs)
    i = argrelextrema(dev, np.greater)[0]
    return a, sol.y[0], a[i], dev[i]


def cost(n, a_end, L=4.0, cfl=0.25, nz=None):
    nz = n if nz is None else nz
    t_end = 2*(np.sqrt(a_end) - 1)
    steps = int(np.ceil(t_end/(cfl*L/n)))
    cells = n*n*nz
    rate = RATE[64] if cells <= 64**3 else RATE[128]
    sec = steps*cells/rate
    c = (MEM_MIB[128] - MEM_MIB[64])/(128**3 - 64**3)
    mem = MEM_MIB[64] + c*(cells - 64**3)
    return {"n": n, "nz": nz, "a_end": a_end, "steps": steps, "cells": cells,
            "card_hours": sec/3600.0, "memory_GiB_estimate": mem/1024.0}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {}
    # (3A)
    G = np.sqrt(2.0)*np.pi/2.0          # (k, k, 0) of the box of four Hubble radii
    a, h, ap, env = junk(G)
    sel = (ap > 10) & (ap < 100)
    prod = env[sel]*ap[sel]
    slope = np.polyfit(np.log(ap[sel]), np.log(env[sel]), 1)[0]
    res["3A"] = {"G": G, "envelope_times_a_min": float(prod.min()),
                 "envelope_times_a_max": float(prod.max()),
                 "spread_of_envelope_times_a": float(prod.max()/prod.min() - 1),
                 "log_slope_10_100": float(slope),
                 "envelope_at_a_60_over_hs": float(np.interp(60.0, ap, env))}
    # (3B)
    deltas = np.logspace(np.log10(1e-3), np.log10(0.1), 60)
    res["3B"] = {}
    for L in (2.0, 4.0, 8.0):
        k1 = 2*np.pi/L
        ac = 0.56/deltas                 # Newtonian infall law, cosmo/TESTLOG.md line 139
        Hc = ac**-0.5
        w = 2*np.sqrt(DELTA_VIR/2)*Hc
        res["3B"][f"L{L:g}"] = {"delta": deltas.tolist(), "omega_over_ck1": (w/k1).tolist(),
                                "phi_lin_peak": (4.5*(1/k1)**2*deltas).tolist()}
    meas = {"0.01": 58.07, "0.05": 13.44}  # relativistic infall a_p, TESTLOG lines 1709, 1845
    res["3B"]["measured_infall_L4"] = {d: {"a_p": ap_, "omega_over_ck1":
                                           float(2*np.sqrt(DELTA_VIR/2)*ap_**-0.5/(np.pi/2))}
                                       for d, ap_ in meas.items()}
    r4 = np.array(res["3B"]["L4"]["omega_over_ck1"])
    m = (deltas >= 0.0025) & (deltas <= 0.05)
    res["3B"]["L4_ratio_range_0.0025_0.05"] = [float(r4[m].min()), float(r4[m].max())]
    # (3C)
    rows = []
    for d, aend in ((0.01, 140.0), (0.0025, 560.0)):
        for n in (64, 128, 256):
            rows.append(dict(cost(n, aend), delta=d))
        rows.append(dict(cost(256, aend, nz=16), delta=d))
    res["3C"] = rows
    with open(os.path.join(out, "regime_estimates.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    ax.loglog(a, np.abs(h - 1.0), color=fs.PAL["red"], lw=0.8,
              label=r"$|h-h_s|/h_s$, ODE")
    ax.loglog(ap, env, "o", color=fs.PAL["red"], ms=2.5)
    aa = np.logspace(0, np.log10(200), 50)
    ax.loglog(aa, prod.mean()/aa, **fs.GUIDE, label=r"$\propto 1/a$")
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel(r"oscillating TT part over static part")
    ax.set_xlim(1, 200)
    ax.set_ylim(1e-3, 2)
    ax.legend(loc="lower left")
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    for col, L in zip((fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]), (2.0, 4.0, 8.0)):
        ax2.loglog(deltas, res["3B"][f"L{L:g}"]["omega_over_ck1"], color=col,
                   label=f"box {L:g} initial Hubble radii")
    for i, (d, v) in enumerate(res["3B"]["measured_infall_L4"].items()):
        ax2.loglog(float(d), v["omega_over_ck1"], "s", color=fs.PAL["red"], ms=4,
                   label=("measured infall, box 4" if i == 0 else None))
    for s in (1.0, np.sqrt(2), np.sqrt(3)):
        ax2.axhline(s, **fs.MASK_LINE)
    ax2.text(1.1e-3, 1.9, r"$|\mathbf{n}|=1,\sqrt{2},\sqrt{3}$", color="grey", fontsize=8)
    ax2.set_xlabel(r"wave amplitude $\delta$")
    ax2.set_ylabel(r"$\omega_{\rm vir}/(c\,k_1)$ at collapse")
    ax2.legend(loc="lower right")
    fs.save(fig, os.path.join(out, "regime_estimates"))
    print(json.dumps({k: v for k, v in res.items() if k != "3B"}, indent=1))
    print("3B L4 ratio range for delta 0.0025-0.05:", res["3B"]["L4_ratio_range_0.0025_0.05"])
    print("3B measured:", res["3B"]["measured_infall_L4"])


if __name__ == "__main__":
    main()
