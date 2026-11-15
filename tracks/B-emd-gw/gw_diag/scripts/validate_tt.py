#!/usr/bin/env python3
"""Validation of the TT projection and the energy spectrum (JOURNAL.md, P1, P3-P5).

    RUN_DIR=<out> python3 scripts/validate_tt.py

Writes results_tt.json and figures tt_*.{pdf,png} into $RUN_DIR (PNG copies into ../figs).
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, "/data/haiyangw/nrpic/wt/B-emd-gw/python")
from gwdiag import Grid, tt, analytic  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.environ.get("RUN_DIR", os.path.join(HERE, "..", "figs"))
FIGS = os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)
fs.use_style()
RES = {}


def save(fig, name):
    files = fs.save(fig, os.path.join(OUT, name))
    shutil.copy(files[1], os.path.join(FIGS, name + ".png"))
    plt.close(fig)


def slope(x, y):
    return float(np.polyfit(np.log10(x), np.log10(y), 1)[0])


# ---------------------------------------------------------------- A: amplitude scaling
g = Grid((32, 28, 24), (1.0, 0.875, 0.75))
w0 = analytic.random_waves(g, 12, 1, 4, amp=1.0, frac_plus=0.7, seed=21)
amps = np.logspace(-6, -1.5, 10)
eh, ed, er = [], [], []
for A in amps:
    waves = [analytic.Wave(w.m, A * w.ap, A * w.ax) for w in w0]
    gamma, K, ref = analytic.wave_adm(waves, g, t=0.17)
    hT, hdT, chib = tt.tt_from_adm(gamma, K, g)
    eh.append(np.abs(hT - ref["h"]).max() / np.abs(ref["h"]).max())
    ed.append(np.abs(hdT - ref["hd"]).max() / np.abs(ref["hd"]).max())
    sp = tt.gw_spectrum(hT, hdT, g, chi_bar=chib)
    exp = analytic.waves_expected(waves, g)
    er.append(abs((sp["rho_kin_total"] + sp["rho_grad_total"]) / (2 * exp["rho_kin_total"]) - 1))
sel = amps >= 1e-4
RES["amplitude"] = {"A": amps.tolist(), "err_h": eh, "err_hdot": ed, "err_rho": er,
                    "slope_h(A>=1e-4)": slope(amps[sel], np.array(eh)[sel]),
                    "slope_hdot(A>=1e-4)": slope(amps[sel], np.array(ed)[sel]),
                    "slope_rho(A>=1e-4)": slope(amps[sel], np.array(er)[sel])}

# ---------------------------------------------------------------- B: spectrum, helicity
g64 = Grid((64, 64, 64), (1.0, 1.0, 1.0))
A0 = 1e-6
waves = analytic.random_waves(g64, 48, 1, 6, slope=-1.0, amp=A0, frac_plus=0.7, seed=5)
exp = analytic.waves_expected(waves, g64)
gamma, K, ref = analytic.wave_adm(waves, g64, t=0.0)
hT, hdT, chib = tt.tt_from_adm(gamma, K, g64)
sp = tt.gw_spectrum(hT, hdT, g64, chi_bar=chib)
hel = tt.helicity_spectrum(hT, hdT, g64, chi_bar=chib)
edges = np.append(sp["k"] - 0.5 * sp["dk"], sp["k"][-1] + 0.5 * sp["dk"])
ref_shell = np.histogram(exp["k"], edges, weights=2 * exp["rho_kin"])[0]
ref_p = np.histogram(exp["k"], edges, weights=exp["rho_plus"])[0]
ref_m = np.histogram(exp["k"], edges, weights=exp["rho_minus"])[0]
got = sp["rho_kin"] + sp["rho_grad"]
m = ref_shell > 0
RES["spectrum"] = {
    "nmodes": len(waves), "grid": g64.n, "A_per_mode": A0,
    "rho_total_rel_err": abs(got.sum() / ref_shell.sum() - 1),
    "shell_max_rel_err": float(np.max(np.abs(got[m] / ref_shell[m] - 1))),
    "empty_shell_max_over_total": float(np.max(got[~m]) / got.sum()) if np.any(~m) else 0.0,
    "helicity_plus_fraction_in": exp["rho_plus_total"] / (exp["rho_plus_total"] + exp["rho_minus_total"]),
    "helicity_plus_fraction_out": hel["rho_plus_total"] / (hel["rho_plus_total"] + hel["rho_minus_total"]),
    "helicity_plus_rel_err": abs(hel["rho_plus_total"] / exp["rho_plus_total"] - 1),
    "helicity_minus_rel_err": abs(hel["rho_minus_total"] / exp["rho_minus_total"] - 1)}

# ---------------------------------------------------------------- C: time series
g32 = Grid((32, 32, 32), (1.0, 1.0, 1.0))
wts = analytic.random_waves(g32, 48, 1, 6, slope=-1.0, amp=A0, frac_plus=0.7, seed=5)
ets = analytic.waves_expected(wts, g32)
ts = np.linspace(0, 1.0, 41)
rk, rg, rp = [], [], []
for t in ts:
    gm, Kt, _ = analytic.wave_adm(wts, g32, t=t)
    a, b, c = tt.tt_from_adm(gm, Kt, g32)
    s = tt.gw_spectrum(a, b, g32, chi_bar=c)
    hh = tt.helicity_spectrum(a, b, g32, chi_bar=c)
    rk.append(s["rho_kin_total"])
    rg.append(s["rho_grad_total"])
    rp.append(hh["rho_plus_total"])
rk, rg, rp = np.array(rk), np.array(rg), np.array(rp)
norm = 2 * ets["rho_kin_total"]
RES["time_series"] = {"t": ts.tolist(), "rho_kin/ref": (rk / norm).tolist(),
                      "rho_grad/ref": (rg / norm).tolist(),
                      "total_max_rel_dev": float(np.max(np.abs((rk + rg) / norm - 1))),
                      "kin_max_rel_dev": float(np.max(np.abs(2 * rk / norm - 1))),
                      "plus_max_rel_dev": float(np.max(np.abs(rp / ets["rho_plus_total"] - 1)))}

# standing waves: modes at m and -m with equal amplitudes (polarization basis of -k: e_+ the
# same, e_x reversed, so a_x -> -a_x gives the same tensor)
sw = [analytic.Wave((0, 0, 2), A0, 0.0), analytic.Wave((0, 0, -2), A0, 0.0)]
sk, sg = [], []
for t in ts:
    gm, Kt, _ = analytic.wave_adm(sw, g32, t=t)
    a, b, c = tt.tt_from_adm(gm, Kt, g32)
    s = tt.gw_spectrum(a, b, g32, chi_bar=c)
    sk.append(s["rho_kin_total"])
    sg.append(s["rho_grad_total"])
sk, sg = np.array(sk), np.array(sg)
snorm = 2 * analytic.waves_expected(sw, g32)["rho_kin_total"]
RES["standing"] = {"rho_kin/ref": (sk / snorm).tolist(), "rho_grad/ref": (sg / snorm).tolist(),
                   "total_max_rel_dev": float(np.max(np.abs((sk + sg) / snorm - 1))),
                   "kin_min_max": [float(sk.min() / snorm), float(sk.max() / snorm)]}

# ---------------------------------------------------------------- D: d_tau h from time differences
t0 = 0.3
gm, Kt, ref = analytic.wave_adm(wts, g32, t=t0)
_, hd3, _ = tt.tt_from_adm(gm, Kt, g32)
dts = np.array([0.08, 0.04, 0.02, 0.01, 0.005])
edt = []
for d in dts:
    gp, Kp, _ = analytic.wave_adm(wts, g32, t=t0 + d)
    gq, Kq, _ = analytic.wave_adm(wts, g32, t=t0 - d)
    hp, _, _ = tt.tt_from_adm(gp, Kp, g32)
    hq, _, _ = tt.tt_from_adm(gq, Kq, g32)
    edt.append(np.abs((hp - hq) / (2 * d) - hd3).max() / np.abs(hd3).max())
RES["time_difference"] = {"dt": dts.tolist(), "err": edt, "slope": slope(dts, edt)}

# ---------------------------------------------------------------- E: gauge and scalar modes
eps_l = np.logspace(-6, -2, 9)
gm_res = {"eps": eps_l.tolist()}
for name in ("gauge", "scalar"):
    rows = {"h_TT": [], "hd_TT": [], "rho": [], "in_metric": [], "in_K": []}
    for eps in eps_l:
        if name == "gauge":
            gam, Kg, al, be = analytic.gauge_mode(g32, eps, seed=3)
        else:
            gam, Kg, _ = analytic.scalar_mode(g32, eps, seed=5)
        a, b, c = tt.tt_from_adm(gam, Kg, g32)
        s = tt.gw_spectrum(a, b, g32, chi_bar=c)
        rows["h_TT"].append(float(np.abs(a).max()))
        rows["hd_TT"].append(float(np.abs(b).max()))
        rows["rho"].append(s["rho_kin_total"] + s["rho_grad_total"])
        rows["in_metric"].append(float(np.abs(gam - np.eye(3)[:, :, None, None, None]).max()))
        rows["in_K"].append(float(np.abs(Kg).max()))
    for q in ("h_TT", "hd_TT", "rho", "in_metric"):
        rows["slope_" + q] = slope(eps_l, rows[q])
    gm_res[name] = rows
RES["gauge_scalar"] = gm_res

with open(os.path.join(OUT, "results_tt.json"), "w") as f:
    json.dump(RES, f, indent=1)

# ================================================================= figures
C = fs.PAL
# Figure 1: amplitude scaling (left), spectrum (right)
fig = plt.figure(figsize=(8.0, 3.2))
ax1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.5)
ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
ax1.loglog(amps, eh, "o-", color=C["red"], label=r"$h^{\rm TT}$")
ax1.loglog(amps, ed, "s--", color=C["yellow"], label=r"$\partial_\tau h^{\rm TT}$")
ax1.loglog(amps, er, "^:", color=C["green"], label=r"$\rho_{\rm GW}$")
ax1.loglog(amps, 0.3 * amps ** 2, **fs.GUIDE, label=r"$\propto A^2$")
ax1.set_xlabel(r"amplitude $A$")
ax1.set_ylabel("relative error")
ax1.legend(loc="upper left")
k = sp["k"] / (2 * np.pi)
mm = ref_shell > 0
f = sp["k"] / sp["dk"]
ax2.semilogy(k[mm], (ref_shell * f)[mm], "o", mfc="none", color=C["blue"], label="input, total")
ax2.semilogy(k[mm], (got * f)[mm], "-", color=C["red"], label="recovered, total")
ax2.semilogy(k[mm], (ref_p * f)[mm], "s", mfc="none", ms=4, color=C["blue"], label="input, +2")
ax2.semilogy(k[mm], (hel["rho_plus"] * f)[mm], "--", color=C["red"], label="recovered, +2")
ax2.semilogy(k[mm], (ref_m * f)[mm], "^", mfc="none", ms=4, color=C["blue"], label="input, -2")
ax2.semilogy(k[mm], (hel["rho_minus"] * f)[mm], ":", color=C["red"], label="recovered, -2")
ax2.set_xlabel(r"$|k| L / 2\pi$")
ax2.set_xticks(range(1, 7))
ax2.set_ylabel(r"$d\rho_{\rm GW}/d\ln k$  [$G = 1$]")
ax2.legend(loc="upper left", fontsize=7, ncol=2)
ax2.set_ylim(top=ax2.get_ylim()[1] * 8)
save(fig, "tt_amplitude_spectrum")

# Figure 2: standing wave (left), travelling superposition (middle), time differences (right)
fig = plt.figure(figsize=(8.0, 3.2))
ax0 = fs.inch_axes(fig, 0.62, 0.5, 1.8, 2.3)
ax1 = fs.inch_axes(fig, 3.35, 0.5, 1.8, 2.3)
ax2 = fs.inch_axes(fig, 6.05, 0.5, 1.8, 2.3)
ax0.plot(ts, 2 * sk / snorm, color=C["red"], ls="--", label=r"$2\rho_{\rm kin}$")
ax0.plot(ts, 2 * sg / snorm, color=C["yellow"], ls=":", label=r"$2\rho_{\rm grad}$")
ax0.plot(ts, (sk + sg) / snorm, color=C["red"], label=r"$\rho_{\rm kin}+\rho_{\rm grad}$")
ax0.axhline(1.0, **fs.GUIDE)
ax0.set_xlabel(r"$t / L$", labelpad=-2)
ax0.set_ylabel(r"energy / $\rho_{\rm ref}$")
ax0.set_ylim(-0.05, 2.6)
ax0.legend(loc="upper left", fontsize=7, ncol=2)
ax0.set_title("standing wave", fontsize=10)
ax1.semilogy(ts, np.abs((rk + rg) / norm - 1) + 1e-17, color=C["red"], label="total")
ax1.semilogy(ts, np.abs(2 * rk / norm - 1) + 1e-17, color=C["yellow"], ls="--", label=r"$2\rho_{\rm kin}$")
ax1.semilogy(ts, np.abs(rp / ets["rho_plus_total"] - 1) + 1e-17, color=C["green"], ls=":",
             label="helicity +2")
ax1.set_ylim(1e-15, 1e-9)
ax1.set_xlabel(r"$t / L$", labelpad=-2)
ax1.set_ylabel("|energy / input - 1|")
ax1.legend(loc="upper left", fontsize=7)
ax1.set_title("48 travelling waves", fontsize=10)
ax2.loglog(dts, edt, "o-", color=C["red"], label="centred difference")
ax2.loglog(dts, edt[-1] * (dts / dts[-1]) ** 2, **fs.GUIDE, label=r"$\propto \Delta t^2$")
ax2.set_xlabel(r"$\Delta t / L$", labelpad=-2)
ax2.set_ylabel(r"error of $\partial_\tau h^{\rm TT}$")
ax2.legend(loc="upper left", fontsize=7)
ax2.set_title(r"$\partial_\tau h^{\rm TT}$: dumps vs 3+1", fontsize=10)
save(fig, "tt_time")

# Figure 3: gauge and scalar modes
fig = plt.figure(figsize=(8.0, 3.4))
for i, name in enumerate(("gauge", "scalar")):
    ax = fs.inch_axes(fig, 0.75 + 4.0 * i, 0.55, 3.0, 2.5)
    r = gm_res[name]
    ax.loglog(eps_l, r["in_metric"], "o-", color=C["blue"], label=r"input $|\gamma_{ij}-\delta_{ij}|$")
    ax.loglog(eps_l, r["in_K"], "s-", color=C["blue"], mfc="none", label=r"input $|K_{ij}|$")
    ax.loglog(eps_l, r["h_TT"], "o--", color=C["red"], label=r"$|h^{\rm TT}|$")
    ax.loglog(eps_l, r["hd_TT"], "s--", color=C["red"], mfc="none", label=r"$|\partial_\tau h^{\rm TT}|$")
    ax.loglog(eps_l, r["rho"], "^:", color=C["green"], label=r"$\rho_{\rm GW}$")
    ax.loglog(eps_l, r["h_TT"][-1] * (eps_l / eps_l[-1]) ** 2, **fs.GUIDE, label=r"$\propto\epsilon^2$")
    ax.set_xlabel(r"amplitude $\epsilon$")
    ax.set_title("pure gauge (Minkowski)" if name == "gauge" else "scalar perturbation",
                 fontsize=10)
    if i == 0:
        ax.set_ylabel("maximum over the mesh")
    ax.legend(loc="lower right", fontsize=7)
save(fig, "tt_gauge_scalar")
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                                                         if not isinstance(vv, list)})
                  for k, v in RES.items()}, indent=1, default=str))
