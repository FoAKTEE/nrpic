#!/usr/bin/env python3
"""End-to-end check on AthenaK output (JOURNAL.md, P6): the z4c_linear_wave dumps of run
B-emd-gw-20261115-113218-0ea0f74 (k along x, A = 1e-6, 32^3, t = 0..2, every 1/16).

    RUN_DIR=<out> python3 scripts/validate_athenak.py [<run dir of the dumps>]

Writes results_athenak.json and figures athenak_*.{pdf,png} into $RUN_DIR.
"""
import glob
import importlib.util
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from gwdiag import tt, weyl, readers, analytic  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/data/haiyangw/nrpic/scratch/B-emd-gw/B-emd-gw-20261115-113218-0ea0f74"
OUT = os.environ.get("RUN_DIR", os.path.join(HERE, "..", "figs"))
FIGS = os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)
fs.use_style()
C = fs.PAL
A = 1.0e-6          # <problem> amp of the input deck (checked below against the dump)
RES = {"source_run": os.path.basename(SRC)}


def save(fig, name):
    files = fs.save(fig, os.path.join(OUT, name))
    shutil.copy(files[1], os.path.join(FIGS, name + ".png"))
    plt.close(fig)


def mx(a):
    return float(np.abs(a).max())


rst = sorted(glob.glob(os.path.join(SRC, "rst", "*.rst")))
wbin = sorted(glob.glob(os.path.join(SRC, "bin", "*.weyl.*.bin")))
RES["n_rst"] = len(rst)
RES["n_weyl"] = len(wbin)

# ---- reader cross-check against the independently written periodic_z4c reader
spec = importlib.util.spec_from_file_location(
    "athena_dumps", os.path.join(HERE, "..", "..", "periodic_z4c", "analysis", "athena_dumps.py"))
other = importlib.util.module_from_spec(spec)
spec.loader.exec_module(other)
d1 = readers.read_rst(rst[5])
d2 = other.read_rst(rst[5])
RES["reader_crosscheck"] = {"file": os.path.basename(rst[5]),
                            "identical": bool(all(np.array_equal(d1[n], d2[n])
                                                  for n in readers.Z4C_NAMES)),
                            "time": [d1["time"], d2["time"]]}
amp_in = float(d1["params"]["problem"]["amp"])
kx = float(d1["params"]["problem"]["kx1"])
RES["deck"] = {"amp": amp_in, "kx1": kx, "pgen": d1["params"]["problem"]["pgen_name"]}
assert amp_in == A and kx == 1.0

# ---- per dump: TT part, polarization, energy, d_tau h
nh = np.array([1.0, 0.0, 0.0])
rho_ref = (2 * np.pi) ** 2 * A ** 2 / (32 * np.pi)
rows = []
hTT_list, hd_list, times = [], [], []
for f in rst:
    d = readers.read_rst(f)
    g = d["grid"]
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    hTT, hdTT = tt.tt_from_conformal(gt, At, g)
    h = gt - np.eye(3)[:, :, None, None, None]
    hp, hx = tt.polarization_along(hTT, nh)
    x = g.axes()[0]
    prof = hp.mean(axis=(0, 1))
    t = d["time"]
    # least squares h_+ = a sin(2 pi x) + b cos(2 pi x); expected a + i b = A exp(-2 pi i t)
    M = np.array([np.sin(2 * np.pi * x), np.cos(2 * np.pi * x)]).T
    a, b = np.linalg.lstsq(M, prof, rcond=None)[0]
    z = (a + 1j * b) / (A * np.exp(-2j * np.pi * t))
    sp = tt.gw_spectrum(hTT, hdTT, g, chi_bar=float(chi.mean()))
    rows.append({"t": t, "amp_ratio": float(abs(z)), "phase_err": float(np.angle(z)),
                 "hx_over_A": mx(hx) / A, "nonTT_over_A": mx(h - hTT) / A,
                 "rho_kin/ref": sp["rho_kin_total"] / rho_ref,
                 "rho_grad/ref": sp["rho_grad_total"] / rho_ref,
                 "rho_tot/ref": (sp["rho_kin_total"] + sp["rho_grad_total"]) / rho_ref,
                 "yz_variation_over_A": float(np.abs(hp - prof).max() / A)})
    hTT_list.append(hTT)
    hd_list.append(hdTT)
    times.append(t)
times = np.array(times)
dt = times[1] - times[0]
RES["per_dump"] = rows

# d_tau h^TT (lapse = 1 + O(A^2) here, so d_t = d_tau) against time differences
td = []
for n in range(2, len(times) - 2):
    c2 = (hTT_list[n + 1] - hTT_list[n - 1]) / (2 * dt)
    c4 = (-hTT_list[n + 2] + 8 * hTT_list[n + 1] - 8 * hTT_list[n - 1] + hTT_list[n - 2]) / (12 * dt)
    ref = hd_list[n]
    td.append({"t": float(times[n]), "err2": mx(c2 - ref) / mx(ref), "err4": mx(c4 - ref) / mx(ref)})
RES["time_differences"] = {"dt": float(dt), "rows": td,
                           "median_err2": float(np.median([r["err2"] for r in td])),
                           "median_err4": float(np.median([r["err4"] for r in td])),
                           "predicted_err2": float((2 * np.pi * dt) ** 2 / 6),
                           "predicted_err4": float((2 * np.pi * dt) ** 4 / 30)}

# ---- Weyl: my Psi_4 (fixed direction +x, and AthenaK's radial triad) vs analytic and AthenaK
wrows = []
keep = {}
for f in rst:
    d = readers.read_rst(f)
    g = d["grid"]
    t = d["time"]
    gamma, K, alpha, beta = readers.z4c_to_adm(d)
    E, B = weyl.electric_magnetic(gamma, K, g, order=6)
    p4x = weyl.psi4(E, B, gamma, g, direction=nh)
    X, Y, Z = g.mesh()
    ana = -(2 * np.pi) ** 2 * A * np.sin(2 * np.pi * (X - t))
    row = {"t": t, "psi4x_err_vs_analytic": mx(p4x - ana) / mx(ana),
           "psi4x_imag_over_max": mx(p4x.imag) / mx(ana)}
    idx = int(round(t / dt))
    wf = [w for w in wbin if w.endswith(f".{idx:05d}.bin")]
    if wf and t > 0:
        wb = readers.read_bin(wf[0])
        if abs(wb["time"] - t) < 1e-12:
            p4r = weyl.psi4(E, B, gamma, g, direction=None)
            r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
            mine = r * p4r
            ath = wb["weyl_rpsi4"] + 1j * wb["weyl_ipsi4"]
            row.update({"athenak_time": wb["time"],
                        "radial_vs_athenak_max_rel": mx(mine - ath) / mx(ath),
                        "radial_vs_athenak_max_rel_neg": mx(-mine - ath) / mx(ath),
                        "corr_re": float(np.corrcoef(mine.real.ravel(), ath.real.ravel())[0, 1])})
            if idx == 5:
                keep = {"mine": mine, "ath": ath, "x": X, "y": Y, "z": Z, "t": t}
    if idx == 5:
        keep_x = {"p4x": p4x, "ana": ana, "x": g.axes()[0], "t": t}
    wrows.append(row)
RES["weyl"] = wrows

# ---- timing of AthenaK's weyl output: fit the time t* at which the analytic wave (through
# gwdiag, radial triad, 6th order) matches the file written at t_n; the step is
# dt = 1/128 (tlim, cfl and nx of the deck; checked from the restart header below)
dstep = readers.read_rst(rst[1])["dt"]
g = readers.read_rst(rst[0])["grid"]
X, Y, Z = g.mesh()
r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)


def ana_radial(t):
    w = [analytic.Wave((1, 0, 0), -1j * A, 0.0)]      # h = A e_+ sin(2 pi (x - t))
    gm, Km, _ = analytic.wave_adm(w, g, t=t)
    E, B = weyl.electric_magnetic(gm, Km, g, order=6)
    return r * weyl.psi4(E, B, gm, g, direction=None)


fit = []
for n in (2, 5, 9, 16, 23, 31):
    wb = readers.read_bin(wbin[n])
    ath = wb["weyl_rpsi4"] + 1j * wb["weyl_ipsi4"]
    offs = np.arange(-10, 3)              # in steps
    errs = [mx(ana_radial(wb["time"] + o * dstep) - ath) / mx(ath) for o in offs]
    i = int(np.argmin(errs))
    fine = np.linspace(offs[i] - 0.5, offs[i] + 0.5, 41)
    ef = [mx(ana_radial(wb["time"] + o * dstep) - ath) / mx(ath) for o in fine]
    j = int(np.argmin(ef))
    fit.append({"n": n, "file_time": wb["time"], "best_offset_steps": float(fine[j]),
                "err_at_best": float(ef[j]), "err_at_offset0": float(errs[list(offs).index(0)]),
                "err_at_integer_best": float(errs[i]), "integer_best": int(offs[i])})
RES["weyl_output_timing"] = {"dt_step": float(dstep), "fits": fit}
with open(os.path.join(OUT, "results_athenak.json"), "w") as f:
    json.dump(RES, f, indent=1)

# ================================================================= figures
fig = plt.figure(figsize=(8.0, 3.3))
ax1 = fs.inch_axes(fig, 0.7, 0.55, 3.0, 2.5)
ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
t_arr = np.array([r["t"] for r in rows])
ax1.plot(t_arr, [r["amp_ratio"] - 1 for r in rows], "o-", ms=3, color=C["red"],
         label=r"$|h_+|/A - 1$")
ax1.plot(t_arr, [r["phase_err"] for r in rows], "s--", ms=3, color=C["yellow"], mfc="none",
         label="phase error [rad]")
ax1.plot(t_arr, [r["rho_tot/ref"] - 1 for r in rows], "^:", ms=3, color=C["green"],
         label=r"$\rho_{\rm GW}/\rho_{\rm ref} - 1$")
ax1.axhline(0, **fs.GUIDE)
ax1.set_xlabel(r"$t$ (wave periods)")
ax1.set_ylabel("deviation")
ax1.legend(loc="lower left", fontsize=7)
ax2.semilogy(t_arr, [r["hx_over_A"] + 1e-30 for r in rows], "o-", ms=3, color=C["red"],
             label=r"$\max|h_\times|/A$")
ax2.semilogy(t_arr, [r["nonTT_over_A"] for r in rows], "s--", ms=3, color=C["yellow"],
             mfc="none", label=r"$\max|h - h^{\rm TT}|/A$")
ax2.semilogy([r["t"] for r in td], [r["err2"] for r in td], "^-", ms=3, color=C["green"],
             label=r"$\partial_\tau h^{\rm TT}$: 2nd-order diff.")
ax2.semilogy([r["t"] for r in td], [r["err4"] for r in td], "d-", ms=3, color=C["blue"],
             label=r"$\partial_\tau h^{\rm TT}$: 4th-order diff.")
ax2.axhline(RES["time_differences"]["predicted_err2"], color=C["green"], lw=1.0, ls=":")
ax2.axhline(RES["time_differences"]["predicted_err4"], color=C["blue"], lw=1.0, ls=":")
ax2.set_xlabel(r"$t$ (wave periods)")
ax2.set_ylabel("relative")
ax2.legend(loc="center right", fontsize=7)
save(fig, "athenak_tt")

fig = plt.figure(figsize=(8.0, 3.3))
ax1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.5)
ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
ax1.plot(keep_x["x"], keep_x["ana"][0, 0] / A, color=C["blue"], label=r"$\ddot h_+$ analytic")
ax1.plot(keep_x["x"], keep_x["p4x"].real[0, 0] / A, "o", ms=3, color=C["red"],
         label=r"Re $\Psi_4(\hat x)$, AthenaK dump")
ax1.plot(keep_x["x"], keep_x["p4x"].imag[0, 0] / A, "s", ms=3, mfc="none", color=C["yellow"],
         label=r"Im $\Psi_4(\hat x)$")
ax1.set_xlabel(r"$x$")
ax1.set_ylabel(r"$\Psi_4 / A$")
ax1.set_title(f"t = {keep_x['t']:.4f}", fontsize=10)
ax1.legend(loc="lower left", fontsize=7)
ax1.set_ylim(-60, 75)
if keep:
    m = ana_radial(keep["t"] - 7 * dstep).ravel()
    m0 = keep["mine"].ravel()
    a = keep["ath"].ravel()
    ax2.plot(a.real / A, m0.real / A, ".", ms=1.0, color="grey", alpha=0.4,
             label=r"vs dump at $t_n$ (real)", rasterized=True)
    ax2.plot(a.real / A, m.real / A, ".", ms=1.5, color=C["red"], label="real part", rasterized=True)
    ax2.plot(a.imag / A, m.imag / A, ".", ms=1.5, color=C["blue"], label="imaginary part",
             rasterized=True)
    lim = 1.05 * max(np.abs(a.real).max(), np.abs(a.imag).max()) / A
    ax2.plot([-lim, lim], [-lim, lim], **fs.GUIDE, label="equality")
    ax2.set_xlabel(r"AthenaK $r\Psi_4 / A$ (weyl output)")
    ax2.set_ylabel(r"gwdiag $r\Psi_4 / A$ (radial triad)")
    ax2.set_title(f"file of $t_n$ = {keep['t']:.4f} vs gwdiag at $t_n - 7\,dt$", fontsize=9)
    ax2.legend(loc="upper left", fontsize=7)
save(fig, "athenak_psi4")
summ = {"reader": RES["reader_crosscheck"],
        "amp_ratio_range": [min(r["amp_ratio"] for r in rows), max(r["amp_ratio"] for r in rows)],
        "phase_err_range": [min(r["phase_err"] for r in rows), max(r["phase_err"] for r in rows)],
        "rho_tot_range": [min(r["rho_tot/ref"] for r in rows), max(r["rho_tot/ref"] for r in rows)],
        "hx_max": max(r["hx_over_A"] for r in rows), "nonTT_max": max(r["nonTT_over_A"] for r in rows),
        "td": {k: v for k, v in RES["time_differences"].items() if k != "rows"},
        "psi4x_err_range": [min(w["psi4x_err_vs_analytic"] for w in wrows),
                            max(w["psi4x_err_vs_analytic"] for w in wrows)],
        "radial_vs_athenak": [w.get("radial_vs_athenak_max_rel") for w in wrows],
        "radial_vs_athenak_neg": [w.get("radial_vs_athenak_max_rel_neg") for w in wrows],
        "weyl_output_timing": RES["weyl_output_timing"]}
print(json.dumps(summ, indent=1))
