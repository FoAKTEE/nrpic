#!/usr/bin/env python3
"""J2: tests of junk_lib.py on synthetic modes with a known answer (no AthenaK data).

T1 orthonormality of the -2Y_lm port on the quadrature grid (l <= 8).
T2 energy: modes r psi4_lm = dN_lm/dt with N_lm = c_lm g(t), g a Gaussian-modulated wave
   (omega = 0.4, sigma = 6, centre 45; the S2g pulse at R = 40 has a half period of about 8 m),
   plus a slow offset that switches on after the pulse (-6e-4 (1 + tanh((t - 60) / 5)) / 2 in
   (2,0), the size seen in S2g, fig_single_junk of F-20261120-222415-137ada9) and white noise
   1e-6; exact window energy sum |c|^2 / 16 pi int g^2 over [30, 75]. FFI (w0 = 0.1, 0.2, 0.3)
   and the time-domain method are compared with it.
T3 momentum: random complex c_lm (seeded), quadrature against the coupling formula of Ruiz et
   al.; and |dP/dt| <= dE/dt pointwise.
Writes test_junk_lib.json and fig_test_junk_lib.{png,pdf}.
Usage: test_junk_lib.py <out | - for $NRPIC_RUN_DIR>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import junk_lib as jl  # noqa: E402
import figstyle as fs  # noqa: E402


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    res = {}
    sph = jl.Sphere()
    res["T1_orthonormality_max_error"] = sph.orthonormality_error()

    # T2
    t = np.arange(0, 90.0 + 1e-9, 0.25)
    w, sig, tc = 0.4, 6.0, 45.0
    g = np.exp(-0.5 * ((t - tc) / sig) ** 2) * np.cos(w * (t - tc))
    gd = np.gradient(g, t, edge_order=2)
    # exact derivative (avoid finite-difference error in the test data)
    gd = (-(t - tc) / sig ** 2 * np.cos(w * (t - tc)) - w * np.sin(w * (t - tc))) \
        * np.exp(-0.5 * ((t - tc) / sig) ** 2)
    c = {(2, 0): 0.010, (2, 2): 0.008 + 0.004j, (2, -2): 0.008 - 0.004j, (3, 0): 0.002}
    rng = np.random.default_rng(20261120)
    psi = {}
    for k in sph.keys:
        z = c.get(k, 0.0) * gd + 1e-6 * (rng.standard_normal(len(t)) + 1j * rng.standard_normal(len(t)))
        if k == (2, 0):
            z = z - 6e-4 * 0.5 * (1 + np.tanh((t - 60.0) / 5.0))
        psi[k] = z
    win = (30.0, 75.0)
    tf = np.linspace(0, 90, 90001)
    gf = np.exp(-0.5 * ((tf - tc) / sig) ** 2) * np.cos(w * (tf - tc))
    sel = (tf >= win[0]) & (tf <= win[1])
    E_exact = sum(abs(v) ** 2 for v in c.values()) / (16 * np.pi) * np.trapezoid(gf[sel] ** 2, tf[sel])
    res["T2_E_exact"] = E_exact
    curves = {}
    for w0 in (0.1, 0.2, 0.3):
        N = {k: jl.ffi(t, z, w0) for k, z in psi.items()}
        dE, dP = sph.flux(N)
        E = jl.window_integral(t, dE, *win)
        res[f"T2_E_ffi_w0_{w0}"] = E
        res[f"T2_ratio_ffi_w0_{w0}"] = E / E_exact
        curves[f"FFI $\\omega_0$={w0}"] = jl.cumulative(t, dE)
    Ntd = {k: jl.td_quad(t, z, win, win[0] - 0.25 * (win[1] - win[0])) for k, z in psi.items()}
    dE, _ = sph.flux(Ntd)
    E = jl.window_integral(t, dE, *win)
    res["T2_E_td"] = E
    res["T2_ratio_td"] = E / E_exact
    curves["time domain"] = jl.cumulative(t, dE)
    # the same without the slow offset and noise (the method's own error)
    psi0 = {k: c.get(k, 0.0) * gd for k in sph.keys}
    N0 = {k: jl.ffi(t, z, 0.2) for k, z in psi0.items()}
    dE0, _ = sph.flux(N0)
    res["T2_ratio_ffi_0.2_clean"] = jl.window_integral(t, dE0, *win) / E_exact

    # T3
    Nr = {k: (rng.standard_normal(5) + 1j * rng.standard_normal(5)) for k in sph.keys}
    dEq, dPq = sph.flux(Nr)
    dPc = jl.momentum_coupling(Nr)
    res["T3_dE_quad_vs_modesum_max_rel"] = float(np.max(np.abs(
        dEq - sum(np.abs(v) ** 2 for v in Nr.values()) / (16 * np.pi)) / dEq))
    scale = np.max(np.abs(dPq))
    res["T3_dP_quad_minus_coupling_max_rel"] = [float(np.max(np.abs(dPq[i] - dPc[i])) / scale)
                                               for i in range(3)]
    res["T3_dP_quad_plus_coupling_max_rel"] = [float(np.max(np.abs(dPq[i] + dPc[i])) / scale)
                                              for i in range(3)]
    res["T3_max_|dP|/dE"] = float(np.max(np.linalg.norm(dPq, axis=0) / dEq))
    # single pair (2,0) + (3,0) real: P along z only
    Nz = {(2, 0): np.array([1.0 + 0j]), (3, 0): np.array([0.5 + 0j])}
    _, dPz = sph.flux(Nz)
    res["T3_pair20_30_dP"] = dPz[:, 0].tolist()
    res["T3_pair20_30_dP_coupling"] = jl.momentum_coupling(Nz)[:, 0].tolist()
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(out, "test_junk_lib.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    ax[0].plot(t, psi[(2, 0)].real, color=fs.PAL["blue"], lw=1.1, label=r"Re $r\psi_4^{20}$ (test data)")
    ax[0].plot(t, (c[(2, 0)] * gd).real, color=fs.PAL["red"], lw=0.8, ls="--", label="pulse alone")
    ax[0].axvspan(*win, color="grey", alpha=0.12, lw=0)
    ax[0].set_xlabel(r"$t$")
    ax[0].legend(frameon=False, fontsize=7)
    cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["yellow"], fs.PAL["red"]]
    for (lab, E), col in zip(curves.items(), cols):
        ax[1].plot(t, E / E_exact, color=col, lw=1.1, label=lab)
    ax[1].axhline(1.0, **fs.REF_LINE)
    ax[1].axvspan(*win, color="grey", alpha=0.12, lw=0)
    ax[1].set_ylim(0, 1.4)
    ax[1].set_xlabel(r"$t$")
    ax[1].set_ylabel(r"$E(t)/E_{\rm exact}$ (window)")
    ax[1].legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_test_junk_lib")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
