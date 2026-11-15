#!/usr/bin/env python3
"""T4: junk radiation and constraint violation of Bowen-York punctures, from core's card
runs of test 1b (read only; AthenaK output under scratch/core/):
  A core-20261115-121046-0c197fb  m = 1, P = 0.3, closed-form correction (approx)
  B core-20261115-121049-0c197fb  same, no correction
  C core-20261115-121047-0c197fb  stock z4c_boosted_puncture, v = 0.2844 (exact slice)
  E core-20261115-121050-0c197fb  m = 1, P = 0.043, S = 0.3, approx
Each starts at x = -4 and moves along +x; spheres about the origin at r = 10 and 14;
r psi4 modes l = 2..8 every 0.25 M (z4c_wave_extr.cpp; the factor r is applied in
z4c_calculate_weyl_scalars.cpp lines 409-410).

Radiated energy [BACKGROUND formula]: dE/dt = (1/16 pi) sum_lm |int_0^t r psi4_lm dt'|^2.
The hole is off the sphere's centre, so r psi4 carries a slowly varying non-radiative
part (Coulomb field seen in an origin-centred tetrad). Two estimates per run:
  raw  - no subtraction (contains the drift of the static part: an upper bound),
  hp   - a quadratic in t fitted to each mode outside the pulse window
         [r - 6, r + 14] and subtracted before integrating (the pulse alone).
Constraint norms: <H^2> = H-norm2 / Volume of the history (core's definition, test 3).
Usage: python3 junk_energy.py <outdir>
"""
import json
import os
import shutil
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
SC = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

OUT = sys.argv[1]
FIG = os.path.join(WT, "tracks/F-hills/three_punctures/figures")
RUNS = {
    "A": ("core-20261115-121046-0c197fb", "byb", "BY P=0.3 approx"),
    "B": ("core-20261115-121049-0c197fb", "byb", "BY P=0.3 none"),
    "C": ("core-20261115-121047-0c197fb", "bref", "boosted slice v=0.284"),
    "E": ("core-20261115-121050-0c197fb", "byb", "BY P=0.043 S=0.3 approx"),
}
RADII = (10, 14)


def load_modes(run, r):
    re_ = np.loadtxt(os.path.join(SC, run, "waveforms", f"rpsi4_real_{r:04d}.txt"))
    im_ = np.loadtxt(os.path.join(SC, run, "waveforms", f"rpsi4_imag_{r:04d}.txt"))
    with open(os.path.join(SC, run, "waveforms", f"rpsi4_real_{r:04d}.txt")) as f:
        head = f.readline().split()[2:]
    labels = [h.split(":")[1] for h in head]
    t = re_[:, 0]
    z = re_[:, 1:] + 1j * im_[:, 1:]
    return t, z[:, :len(labels)], labels


def energy(t, z):
    """Cumulative radiated energy and its rate from r psi4 modes z (nt, nmodes)."""
    dt = np.diff(t)
    news = np.zeros_like(z)
    news[1:] = np.cumsum(0.5 * (z[1:] + z[:-1]) * dt[:, None], axis=0)
    rate = np.sum(np.abs(news) ** 2, axis=1) / (16 * np.pi)
    e = np.zeros_like(t)
    e[1:] = np.cumsum(0.5 * (rate[1:] + rate[:-1]) * dt)
    return e, rate


def highpass(t, z, r):
    """Subtract a quadratic fitted outside the pulse window [r - 6, r + 14]."""
    out = (t < r - 6) | (t > r + 14)
    zz = np.empty_like(z)
    for k in range(z.shape[1]):
        for part in (np.real, np.imag):
            c = np.polyfit(t[out], part(z[out, k]), 2)
            if part is np.real:
                zz[:, k] = z[:, k].real - np.polyval(c, t)
            else:
                zz[:, k] = zz[:, k] + 1j * (z[:, k].imag - np.polyval(c, t))
    return zz


def hist(run, base):
    h = np.loadtxt(os.path.join(SC, run, f"{base}.z4c.user.hst"))
    return h[:, 0], h[:, 3] / h[:, 10], h[:, 4] / h[:, 10]     # t, <H^2>, <M^2>


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    curves = {}
    for key, (run, base, lab) in RUNS.items():
        res[key] = {"run": run, "label": lab}
        for r in RADII:
            t, z, labels = load_modes(run, r)
            e_raw, _ = energy(t, z)
            zh = highpass(t, z, r)
            e_hp, rate_hp = energy(t, zh)
            i22 = labels.index("22")
            win = (t >= r - 6) & (t <= r + 14)
            res[key][f"r{r}"] = dict(
                E_raw_total=float(e_raw[-1]), E_hp_total=float(e_hp[-1]),
                E_hp_window=float(e_hp[win][-1] - e_hp[win][0]),
                t_end=float(t[-1]), rpsi4_22_t0=float(abs(z[0, i22])),
                peak_hp_22=float(np.max(np.abs(zh[win, i22]))),
                peak_raw_22=float(np.max(np.abs(z[:, i22]))))
            curves[(key, r)] = (t, z[:, i22], zh[:, i22], e_raw, e_hp,
                                z[:, labels.index("20")], zh[:, labels.index("20")])
        th, h2, m2 = hist(run, base)
        imax = int(np.argmax(h2))
        res[key]["H2_t0"] = float(h2[0])
        res[key]["H2_max"] = float(h2[imax])
        res[key]["t_H2_max"] = float(th[imax])
        res[key]["H2_end"] = float(h2[-1])
        res[key]["M2_t0"] = float(m2[0])
        curves[(key, "h")] = (th, h2, m2)
        print(key, lab, {k: (f"{v:.3e}" if isinstance(v, float) else v)
                         for k, v in res[key].items() if k.startswith("H2") or k == "M2_t0"})
        for r in RADII:
            print("   r =", r, {k: f"{v:.3e}" for k, v in res[key][f"r{r}"].items()})
    with open(os.path.join(OUT, "junk_energy.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, hspace=0.25, wspace=0.28)
    cols = {"A": fs.PAL["red"], "B": fs.PAL["yellow"], "C": fs.PAL["blue"], "E": fs.PAL["green"]}
    ax = axes[0, 0]
    for key in RUNS:
        t, z22, zh22, *_ = curves[(key, 14)]
        ax.plot(t, z22.real, color=cols[key], lw=1.2, label=f"{key}: {RUNS[key][2]}")
        ax.plot(t, zh22.real, color=cols[key], lw=0.8, ls="--")
    ax.axvspan(14 - 6, 14 + 14, color="grey", alpha=0.1)
    ax.set_xlabel("t [M]", labelpad=-1)
    ax.set_ylabel(r"Re $r\psi_4^{22}$ at r = 14 (dashed: background removed)")
    ax.legend(loc="upper right", fontsize=7)
    ax = axes[0, 1]
    for key in RUNS:
        t, z22, zh22, er, eh, z20, zh20 = curves[(key, 14)]
        ax.plot(t, z20.real, color=cols[key], lw=1.2)
        ax.plot(t, zh20.real, color=cols[key], lw=0.8, ls="--")
    ax.axvspan(14 - 6, 14 + 14, color="grey", alpha=0.1)
    ax.set_xlabel("t [M]", labelpad=-1)
    ax.set_ylabel(r"Re $r\psi_4^{20}$ at r = 14")
    ax = axes[1, 0]
    for key in RUNS:
        for r, ls in ((10, ":"), (14, "-")):
            t, z22, zh22, er, eh, *_ = curves[(key, r)]
            ax.plot(t, np.maximum(eh, 1e-14), color=cols[key], ls=ls, lw=1.2)
            if r == 14:
                ax.plot(t, np.maximum(er, 1e-14), color=cols[key], ls="--", lw=0.8)
    ax.set_yscale("log")
    ax.set_ylim(1e-10, 1e-3)
    ax.set_xlabel("t [M]", labelpad=-1)
    ax.set_ylabel(r"$E_{\rm rad}(t)/m$ (solid r=14, dotted r=10; dashed raw)")
    ax = axes[1, 1]
    for key in RUNS:
        th, h2, m2 = curves[(key, "h")]
        ax.plot(th, np.sqrt(h2), color=cols[key], lw=1.2)
        ax.plot(th, np.sqrt(m2), color=cols[key], lw=0.8, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("t [M]", labelpad=-1)
    ax.set_ylabel(r"$\langle H^2\rangle^{1/2}$ (solid), $\langle M^2\rangle^{1/2}$ (dashed)")
    for pth in fs.save(fig, os.path.join(OUT, "fig_junk")):
        if pth.endswith(".png"):
            shutil.copy(pth, FIG)


if __name__ == "__main__":
    main()
