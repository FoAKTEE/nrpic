#!/usr/bin/env python3
"""Validation of E_ij, B_ij and Psi_4 on analytic fields (JOURNAL.md, P2-P4).

    RUN_DIR=<out> python3 scripts/validate_weyl.py

Writes results_weyl.json and figures weyl_*.{pdf,png} into $RUN_DIR (PNG copies to ../figs).
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, "/data/haiyangw/nrpic/wt/B-emd-gw/python")
from gwdiag import Grid, tt, weyl, analytic  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.environ.get("RUN_DIR", os.path.join(HERE, "..", "figs"))
FIGS = os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)
fs.use_style()
RES = {}
C = fs.PAL


def save(fig, name):
    files = fs.save(fig, os.path.join(OUT, name))
    shutil.copy(files[1], os.path.join(FIGS, name + ".png"))
    plt.close(fig)


def slope(x, y):
    return float(np.polyfit(np.log10(x), np.log10(y), 1)[0])


def mx(a):
    return float(np.abs(a).max())


ORDERS = [2, 4, 6, "spectral"]
NS = [12, 16, 24, 32, 48, 64]

# ---------------------------------------------------------------- A: convergence
A0 = 1e-8
conv = {"N": NS}
for case in ("waves", "gauge", "scalar"):
    conv[case] = {str(o): {"E": [], "B": [], "LE": []} for o in ORDERS}
for N in NS:
    g = Grid((N, N, N), (1.0, 1.0, 1.0))
    waves = analytic.random_waves(g, 8, 1, 2, amp=A0, frac_plus=0.6, seed=7)
    gw, Kw, rw = analytic.wave_adm(waves, g, t=0.21)
    gg, Kg, _, _ = analytic.gauge_mode(g, 1e-3, seed=3)
    gs, Ks, rs = analytic.scalar_mode(g, 1e-6, seed=5)
    # scale of the gauge data: max |d_k d_l gamma_ij| (O(eps); R itself is O(eps^2) here
    # because the linear curvature of a pure gauge vanishes)
    Dsp = weyl.Deriv(g, "spectral")
    scale_g = max(mx(Dsp.d2(gg[a, b], c, e)) for a in range(3) for b in range(3)
                  for c in range(3) for e in range(3))
    for o in ORDERS:
        E, B = weyl.electric_magnetic(gw, Kw, g, order=o)
        conv["waves"][str(o)]["E"].append(mx(E - rw["E_lin"]) / mx(rw["E_lin"]))
        conv["waves"][str(o)]["B"].append(mx(B - rw["B_lin"]) / mx(rw["B_lin"]))
        E, B = weyl.electric_magnetic(gg, Kg, g, order=o)
        conv["gauge"][str(o)]["E"].append(mx(E) / scale_g)
        conv["gauge"][str(o)]["B"].append(mx(B) / scale_g)
        E, B = weyl.electric_magnetic(gs, Ks, g, order=o)
        conv["scalar"][str(o)]["E"].append(mx(E - rs["E_lin"]) / mx(rs["E_lin"]))
        conv["scalar"][str(o)]["B"].append(mx(B) / mx(rs["E_lin"]))
        conv["scalar"][str(o)]["LE"].append(mx(tt.tt_project(E, g)) / mx(rs["E_lin"]))
    print("N", N, "done", flush=True)
fits = {}
Ns = np.array(NS, float)
for case in ("waves", "gauge", "scalar"):
    for o in (2, 4, 6):
        for q in (("E", "B") if case != "scalar" else ("E", "B", "LE")):
            y = np.array(conv[case][str(o)][q])
            floor = np.array(conv[case]["spectral"][q])
            sel = (Ns >= 16) & (y > 20 * floor)
            fits[f"{case}_{o}_{q}"] = -slope(Ns[sel], y[sel]) if sel.sum() >= 2 else None
conv["fitted_orders(N>=16, above 20x the spectral floor)"] = fits
RES["convergence"] = conv

# ---------------------------------------------------------------- B: Psi_4 of a plane wave
g = Grid((32, 32, 32), (1.0, 1.0, 1.0))
m = (1, 1, 0)
k = analytic.lattice_k(g, m)
ap, ax = 0.8 + 0.3j, -0.4 + 0.5j
psi = {}
for A in np.logspace(-8, -2, 7):
    waves = [analytic.Wave(m, A * ap, A * ax)]
    gm, Kt, ref = analytic.wave_adm(waves, g, t=0.1)
    E, B = weyl.electric_magnetic(gm, Kt, g, order="spectral")
    p4 = weyl.psi4(E, B, gm, g, direction=k)
    p0 = weyl.psi0_like(E, B, gm, g, direction=k)
    hp, hx = tt.polarization_along(ref["hdd"], k)
    psi[float(A)] = {"err": mx(p4 - (hp - 1j * hx)) / mx(hp - 1j * hx),
                     "reverse_over_forward": mx(p0) / mx(p4),
                     "E_err": mx(E - ref["E_lin"]) / mx(ref["E_lin"]),
                     "B_err": mx(B - ref["B_lin"]) / mx(ref["B_lin"])}
amps = np.array(sorted(psi))
RES["psi4_plane_wave"] = {"m": m, "amplitudes": psi,
                          "slope_err": slope(amps[amps >= 1e-5],
                                             [psi[a]["err"] for a in amps[amps >= 1e-5]]),
                          "slope_reverse": slope(amps[amps >= 1e-5],
                                                 [psi[a]["reverse_over_forward"] for a in amps[amps >= 1e-5]])}
# profile along the propagation direction (diagonal through the box) for the figure
A = 1e-6
waves = [analytic.Wave(m, A * ap, A * ax)]
gm, Kt, ref = analytic.wave_adm(waves, g, t=0.1)
prof = {}
for o in (2, 4, "spectral"):
    E, B = weyl.electric_magnetic(gm, Kt, g, order=o)
    prof[str(o)] = weyl.psi4(E, B, gm, g, direction=k)[0, np.arange(32), np.arange(32)]
    if o == "spectral":
        prof["reverse"] = weyl.psi0_like(E, B, gm, g, direction=k)[0, np.arange(32), np.arange(32)]
hp, hx = tt.polarization_along(ref["hdd"], k)
prof["ref"] = (hp - 1j * hx)[0, np.arange(32), np.arange(32)]
X, Y, Z = g.mesh()
s_diag = ((X + Y) / np.sqrt(2))[0, np.arange(32), np.arange(32)]

# ---------------------------------------------------------------- C: scalar mode and Psi_4
gs = Grid((32, 32, 32), (1.0, 1.0, 1.0))
eps = 1e-6
zeta = analytic.ModeField(gs, [(2, 0, 0)], [1.0], [0.3], eps)
d = np.eye(3)[:, :, None, None, None]
gam = (1 + 2 * zeta.val()) * d
Ksc = np.zeros_like(gam)
H = zeta.hess()
E_lin = -(H - d * np.einsum("ii...->...", H) / 3.0)
E, B = weyl.electric_magnetic(gam, Ksc, gs, order="spectral")
sc = {}
for name, nvec in (("along k (x)", (1, 0, 0)), ("along y", (0, 1, 0)), ("along (1,1,0)", (1, 1, 0))):
    p4 = weyl.psi4(E, B, gam, gs, direction=nvec)
    u, v, w = weyl.triad(gam, gs, direction=nvec)
    mb = (v - 1j * w) / np.sqrt(2)
    p4lin = -np.einsum("ab...,a...,b...->...", E_lin, mb, mb)
    sc[name] = {"max|Psi4|": mx(p4), "max|Psi4_lin|": mx(p4lin),
                "rel_diff": mx(p4 - p4lin) / max(mx(p4lin), 1e-300)}
sc["max|E_lin|"] = mx(E_lin)
sc["max|B|/max|E_lin|"] = mx(B) / mx(E_lin)
sc["max|Lambda E|/max|E_lin|"] = mx(tt.tt_project(E, gs)) / mx(E_lin)
RES["scalar_psi4"] = sc

with open(os.path.join(OUT, "results_weyl.json"), "w") as f:
    json.dump(RES, f, indent=1, default=str)

# ================================================================= figures
# Figure 1: convergence, three cases
fig = plt.figure(figsize=(8.0, 3.3))
cols = {"2": C["yellow"], "4": C["red"], "6": C["green"], "spectral": C["blue"]}
titles = {"waves": r"waves: $|E-E_{\rm lin}|$, $|B-B_{\rm lin}|$",
          "gauge": r"pure gauge: $|E|$, $|B|$ / $|\partial\partial\gamma|$",
          "scalar": r"scalar: $|B|$, $|\Lambda E|$ / $|E_{\rm lin}|$"}
for i, case in enumerate(("waves", "gauge", "scalar")):
    ax = fs.inch_axes(fig, 0.62 + 2.55 * i, 0.5, 2.0, 2.4)
    for o in ORDERS:
        q1, q2 = ("E", "B") if case != "scalar" else ("B", "LE")
        y1 = np.maximum(conv[case][str(o)][q1], 1e-17)
        y2 = np.maximum(conv[case][str(o)][q2], 1e-17)
        ax.loglog(NS, y1, "o-", color=cols[str(o)], ms=3,
                  label=(f"order {o}" if o != "spectral" else "spectral"))
        ax.loglog(NS, y2, "s--", color=cols[str(o)], ms=3, mfc="none")
    for p in (2, 4, 6):
        y0 = conv[case][str(p)]["E" if case != "scalar" else "B"][2]
        ax.loglog(Ns[2:], y0 * (Ns[2:] / Ns[2]) ** (-p), color="k", lw=0.8, ls=":")
    ax.set_xlabel(r"$N$ (cells per side)", labelpad=-2)
    ax.set_title(titles[case], fontsize=9)
    ax.set_xticks([12, 24, 48])
    ax.set_xticklabels(["12", "24", "48"])
    if i == 0:
        ax.set_ylabel("relative error / residual")
        ax.legend(loc="lower left", fontsize=7)
save(fig, "weyl_convergence")

# Figure 2: Psi_4 profile (left), amplitude scaling (right)
fig = plt.figure(figsize=(8.0, 3.2))
ax1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.5)
ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
o = np.argsort(s_diag)
ax1.plot(s_diag[o], prof["ref"].real[o] / A, color=C["blue"], label=r"Re: $\ddot h_+$")
ax1.plot(s_diag[o], prof["ref"].imag[o] / A, color=C["blue"], ls="--", label=r"Im: $-\ddot h_\times$")
ax1.plot(s_diag[o], prof["spectral"].real[o] / A, "o", color=C["red"], ms=3, label=r"$\Psi_4$ spectral")
ax1.plot(s_diag[o], prof["spectral"].imag[o] / A, "s", color=C["red"], ms=3, mfc="none")
ax1.plot(s_diag[o], prof["2"].real[o] / A, color=C["yellow"], lw=1.0, label=r"$\Psi_4$ order 2")
ax1.plot(s_diag[o], np.abs(prof["reverse"][o]) / A, color=C["green"], lw=1.0,
         label=r"$|\Psi_4|$ along $-\hat k$")
ax1.set_xlabel(r"$(x+y)/\sqrt{2}$ along the diagonal $z = z_0$")
ax1.set_ylabel(r"$\Psi_4 / A$")
ax1.legend(loc="lower left", fontsize=7, ncol=2)
ax2.loglog(amps, [psi[a]["err"] for a in amps], "o-", color=C["red"], label=r"$\Psi_4$ error")
ax2.loglog(amps, [psi[a]["E_err"] for a in amps], "s--", color=C["yellow"], mfc="none", label=r"$E$ error")
ax2.loglog(amps, [psi[a]["B_err"] for a in amps], "^:", color=C["green"], mfc="none", label=r"$B$ error")
ax2.loglog(amps, [psi[a]["reverse_over_forward"] for a in amps], "d-", color=C["blue"],
           label=r"$|\Psi_4(-\hat k)| / |\Psi_4(\hat k)|$")
ax2.loglog(amps, amps, **fs.GUIDE, label=r"$\propto A$")
ax2.set_xlabel(r"amplitude $A$ (spectral derivatives, $32^3$)")
ax2.set_ylabel("relative")
ax2.legend(loc="upper left", fontsize=7)
save(fig, "weyl_psi4")
print(json.dumps({"fits": fits, "psi4": RES["psi4_plane_wave"]["slope_err"],
                  "scalar": sc}, indent=1, default=str))
