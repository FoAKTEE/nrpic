#!/usr/bin/env python3
"""Scouting: the GW diagnostics on the restart dumps of two full-GR cosmology runs of the
cosmology extension (test C of arXiv:1904.07841 in the 256 Mpc/h box, 128^3, 1 particle per
cell; `runs/cosmo/dav_c256_n128_t` quadratic cloud, `..._pcs4bt` cubic cloud with fourth-order
compensation; cosmo/TESTLOG.md).

    RUN_DIR=<out> python3 scripts/cosmo_demo.py <run dir> [<run dir> ...]

Per dump: a = <chi>^(-1/2) (chi = a^-2 for gamma = a^2 delta), proper Hubble rate
H = -<K>/3, rho_bar = 3 H^2/(8 pi), rho_kin and rho_grad of the TT part, the rms of h^TT and of
the non-TT part of tilde gamma - delta. At the last dump of the first run also E, B (order 6)
and Lambda E. Writes results_cosmo.json and figures cosmo_*.{pdf,png}.
"""
import glob
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from gwdiag import tt, weyl, readers  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.environ.get("RUN_DIR", os.path.join(HERE, "..", "figs"))
FIGS = os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)
fs.use_style()
C = fs.PAL
RUNS = sys.argv[1:]
RES = {}


def rms(a):
    return float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", a, a))))


for rd in RUNS:
    name = os.path.basename(rd.rstrip("/"))
    rows = []
    spectra = []
    files = sorted(glob.glob(os.path.join(rd, "rst", "*.rst")))
    for f in files:
        d = readers.read_rst(f)
        g = d["grid"]
        chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
        a = float(np.mean(chi)) ** -0.5
        H = -float(np.mean(trK)) / 3.0
        rho_bar = 3 * H ** 2 / (8 * np.pi)
        hTT, hdTT = tt.tt_from_conformal(gt, At, g)
        h = gt - np.eye(3)[:, :, None, None, None]
        sp = tt.gw_spectrum(hTT, hdTT, g, chi_bar=float(np.mean(chi)))
        rows.append({"file": os.path.basename(f), "t": d["time"], "a": a, "H": H,
                     "rho_bar": rho_bar,
                     "rho_kin/rho_bar": sp["rho_kin_total"] / rho_bar,
                     "rho_grad/rho_bar": sp["rho_grad_total"] / rho_bar,
                     "rms_hTT": rms(hTT), "rms_h_nonTT": rms(h - hTT),
                     # the initial data are conformally flat (tilde gamma = delta): both zero
                     "rms_hTT_over_nonTT": rms(hTT) / rms(h - hTT) if rms(h - hTT) > 0 else None})
        spectra.append({"a": a, "k": sp["k"].tolist(),
                        "drho_dlnk/rho_bar": (sp["drho_dlnk"] / rho_bar).tolist(),
                        "kin_shell/rho_bar": (sp["rho_kin"] / rho_bar).tolist()})
        print(name, rows[-1], flush=True)
    RES[name] = {"rows": rows, "spectra": spectra, "box": g.L, "n": g.n}

# Weyl at the last dump of the first run
d = readers.read_rst(sorted(glob.glob(os.path.join(RUNS[0], "rst", "*.rst")))[-1])
g = d["grid"]
gamma, K, alpha, beta = readers.z4c_to_adm(d)
E, B = weyl.electric_magnetic(gamma, K, g, order=6)
LE = tt.tt_project(E, g)
p4 = weyl.psi4(E, B, gamma, g, direction=(1, 0, 0))
RES["weyl_last_dump"] = {"run": os.path.basename(RUNS[0].rstrip("/")), "t": d["time"],
                         "rms_E": rms(E), "rms_B": rms(B), "rms_Lambda_E": rms(LE),
                         "rms_B/rms_E": rms(B) / rms(E), "rms_LE/rms_E": rms(LE) / rms(E),
                         "rms_psi4_x": float(np.sqrt(np.mean(np.abs(p4) ** 2)))}
print(RES["weyl_last_dump"], flush=True)
with open(os.path.join(OUT, "results_cosmo.json"), "w") as f:
    json.dump(RES, f, indent=1)

# figures
fig = plt.figure(figsize=(8.0, 3.3))
ax1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.5)
ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
cols = [C["red"], C["blue"], C["green"]]
for i, rd in enumerate(RUNS):
    name = os.path.basename(rd.rstrip("/"))
    r = RES[name]["rows"]
    a = np.array([x["a"] for x in r])
    rg = np.array([x["rho_kin/rho_bar"] + x["rho_grad/rho_bar"] for x in r])
    ax1.loglog(a[rg > 0], rg[rg > 0], "o-", ms=3,
               color=cols[i], label=name + r": $\rho_{\rm GW}/\bar\rho$")
    rr = [(x["a"], x["rms_hTT_over_nonTT"]) for x in r if x["rms_hTT_over_nonTT"]]
    ax1.loglog([q[0] for q in rr], [q[1] for q in rr], "s--", ms=3, mfc="none", color=cols[i],
               label=r"rms $h^{\rm TT}$ / rms non-TT")
    sps = RES[name]["spectra"]
    for j, s in enumerate((sps[1], sps[len(sps) // 2], sps[-1])):
        k = np.array(s["k"]) * RES[name]["box"][0] / (2 * np.pi)
        y = np.array(s["drho_dlnk/rho_bar"])
        m = y > 0
        ax2.loglog(k[m], y[m], color=cols[i], ls=["-", "--", ":"][j], lw=1.2,
                   label=f"{name}, a = {s['a']:.0f}" if i == 0 or j == 2 else None)
ax1.set_xlabel(r"scale factor $a$ ($a = 1$ at the start)")
ax1.set_ylabel("ratio")
ax1.legend(loc="upper left", fontsize=6)
ax2.set_xlabel(r"$|k| L / 2\pi$")
ax2.set_ylabel(r"$(d\rho_{\rm GW}/d\ln k)/\bar\rho$")
ax2.legend(loc="lower right", fontsize=6)
files = fs.save(fig, os.path.join(OUT, "cosmo_tt"))
shutil.copy(files[1], os.path.join(FIGS, "cosmo_tt.png"))
