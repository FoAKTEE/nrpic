#!/usr/bin/env python3
"""Verifier check C4: secondary infall of cold collisionless dust onto a point-mass seed in
Einstein-de Sitter, by my own radial-shell code (Newtonian, shell crossing allowed, radial
orbits through the centre), and the logarithmic slope of the density inside the
turnaround radius against the self-similar value -9/4.

Set-up (G = M = 1): at t_i = 2/(3 eps) N equal-mass shells of uniform background density
3 eps^2/(8 pi) in the unperturbed Hubble flow v = eps r, enclosed background mass from
Mb_min to Mb_max; seed of mass 1 at the centre. Shell k feels
    a_k = -(1 + m(<k) + dm/2) r_k / (r_k^2 + s^2)^(3/2)
(Plummer softening s for everything), m(<k) from the radial order; radial orbits pass
through the centre (reflection r -> -r, v -> -v). Kick-drift-kick with a global step
eta * min_k sqrt((r_k^2 + s^2)^(3/2) / M_enc,k). Dust outside the last shell does not act
(Birkhoff). The density at a_f is the time average of the shells' mass over the last
fraction `avg` of the run in log bins, compared with the turnaround radius r_ta(a_f)
of the closed form (v3_turnaround_capture.py) and fitted for its slope.

Usage: v4_shells.py [--out DIR] [--N 3000] [--af 100] [--eps 0.01] [--soft 2] [--eta 0.05]
"""
import argparse
import json
import math
import os
import shutil
import sys
import time

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def a_ta_of_Mb(Mb):
    mu = 1.0 / Mb
    A = (1 + mu) / (2 * mu)
    B = math.sqrt(2 * A ** 3 / (1 + mu))
    th = math.acos(1 - 1 / A)
    tau = B * math.pi - B * (th - math.sin(th))
    return (1 + 1.5 * tau) ** (2 / 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    ap.add_argument("--N", type=int, default=3000)
    ap.add_argument("--af", type=float, default=100.0)
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--soft", type=float, default=2.0)
    ap.add_argument("--eta", type=float, default=0.05)
    ap.add_argument("--Mbmin", type=float, default=0.3)
    ap.add_argument("--avg", type=float, default=0.1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    eps, N, s2 = a.eps, a.N, a.soft ** 2
    Mb_ta_f = brentq(lambda lm: a_ta_of_Mb(math.exp(lm)) - a.af, -20, 20)
    Mb_ta_f = math.exp(Mb_ta_f)
    Mbmax = 1.6 * Mb_ta_f
    edges = np.linspace(a.Mbmin, Mbmax, N + 1)
    dm = edges[1] - edges[0]
    Mb = 0.5 * (edges[1:] + edges[:-1])
    r = (2 * Mb / eps ** 2) ** (1 / 3)
    v = eps * r
    seed_inner = a.Mbmin    # dust inside the first shell, kept as part of the seed
    Mc = 1.0 + seed_inner
    ti = 2 / (3 * eps)
    tf = ti * a.af ** 1.5
    t = ti
    ri_ta = None

    def accel(r):
        ar = np.abs(r)
        order = np.argsort(ar, kind="stable")
        menc = np.empty(N)
        menc[order] = Mc + dm * np.arange(N) + 0.5 * dm
        rr2 = r * r + s2
        return -menc * r / rr2 ** 1.5, menc, rr2

    acc, menc, rr2 = accel(r)
    nstep = 0
    t_avg0 = tf - a.avg * (tf - ti)
    bins = np.logspace(0, math.log10(r.max() * 3), 160)
    hist = np.zeros(len(bins) - 1)
    wsum = 0.0
    t0 = time.time()
    while t < tf:
        dt = a.eta * float(np.min(np.sqrt(rr2 ** 1.5 / menc)))
        dt = min(dt, tf - t)
        v += 0.5 * dt * acc
        r += dt * v
        neg = r < 0
        r[neg] = -r[neg]
        v[neg] = -v[neg]
        acc, menc, rr2 = accel(r)
        v += 0.5 * dt * acc
        t += dt
        nstep += 1
        if t >= t_avg0:
            h, _ = np.histogram(r, bins=bins)
            hist += h * dt
            wsum += dt
    wall = time.time() - t0
    mass_hist = hist / wsum * dm
    rc = np.sqrt(bins[1:] * bins[:-1])
    vol = 4 / 3 * math.pi * (bins[1:] ** 3 - bins[:-1] ** 3)
    rho = mass_hist / vol
    rho_b = 1 / (6 * math.pi * tf ** 2)   # EdS background density at t_f (G = 1)
    # turnaround radius at a_f: closed form for the shell that turns around at a_f
    mu = 1 / Mb_ta_f
    r_ta = (2 * Mb_ta_f / eps ** 2) ** (1 / 3) * (1 + mu) / mu
    # shells beyond turnaround: the outermost local maximum of r among shells moving in?
    fits = {}
    for lo, hi in ((0.03, 0.3), (0.05, 0.3), (0.1, 0.4), (0.02, 0.1)):
        m = (rc > lo * r_ta) & (rc < hi * r_ta) & (rho > 0)
        if m.sum() > 4:
            p = np.polyfit(np.log(rc[m]), np.log(rho[m]), 1)
            fits[f"{lo}-{hi}"] = float(p[0])
    # enclosed-mass slope (smoother): d ln M / d ln r -> 3 + slope
    order = np.sort(r)
    Menc = Mc + dm * np.arange(1, N + 1)
    mfit = {}
    for lo, hi in ((0.03, 0.3), (0.05, 0.3), (0.1, 0.4)):
        m = (order > lo * r_ta) & (order < hi * r_ta)
        if m.sum() > 10:
            p = np.polyfit(np.log(order[m]), np.log(Menc[m] - Mc), 1)
            mfit[f"{lo}-{hi}"] = float(p[0] - 3)
    res = {"args": vars(a), "Mb_ta_at_af": Mb_ta_f, "Mbmax": Mbmax, "dm": dm, "r_ta_af": r_ta,
           "t_i": ti, "t_f": tf, "steps": nstep, "wall_s": wall, "density_slope_fits": fits,
           "slope_from_enclosed_dust_mass": mfit,
           "M_dust_inside_r_ta_final": float(dm * np.sum(r < r_ta)),
           "seed_plus_inner": Mc}
    with open(os.path.join(a.out, "v4_shells.json"), "w") as f:
        json.dump(res, f, indent=1)
    np.savez(os.path.join(a.out, "v4_shells.npz"), rc=rc, rho=rho, r=r, v=v, Mb=Mb)
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    m = rho > 0
    ax[0].loglog(rc[m] / r_ta, rho[m] / rho_b, color=fs.PAL["red"], lw=1.2, label="verifier shells (time average)")
    xr = np.array([0.03, 0.3])
    k = (rc > 0.05 * r_ta) & (rc < 0.3 * r_ta) & m
    norm = np.exp(np.mean(np.log(rho[k] / rho_b) + 2.25 * np.log(rc[k] / r_ta)))
    ax[0].loglog(xr, norm * xr ** -2.25, **fs.GUIDE, label=r"$\propto r^{-9/4}$")
    ax[0].axvline(1.0, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$r/r_{\rm ta}(a_f)$"); ax[0].set_ylabel(r"$\rho/\rho_b(t_f)$")
    ax[0].set_xlim(1e-3, 3)
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].plot(r / r_ta, v / (r_ta / tf), ".", ms=1.5, color=fs.PAL["blue"])
    ax[1].set_xscale("log"); ax[1].set_xlim(1e-3, 3)
    ax[1].set_xlabel(r"$r/r_{\rm ta}(a_f)$"); ax[1].set_ylabel(r"$v_r\,t_f/r_{\rm ta}$")
    ax[1].axvline(1.0, **fs.MASK_LINE)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v4_shells"))
    shutil.copy(files[1], a.figdir)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
