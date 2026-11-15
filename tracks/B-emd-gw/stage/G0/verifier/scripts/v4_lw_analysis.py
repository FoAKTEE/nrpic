"""Verifier of B-emd-gw, claim C6: analysis of the runs of v4_lw_runs.sh (own reader, own
exact solution; nothing of periodic_z4c/analysis is used).

    python3 v4_lw_analysis.py RUNDIR OUTDIR

Exact linear TT wave of z4c_linear_wave (athenak/src/pgen/tests/z4c_linear_wave.cpp):
    tilde gamma_ij = delta_ij + A e_ij sin(phi),  tilde A_ij = pi |k| A e_ij cos(phi),
    phi = 2 pi (k.x - |k| t),  k in cycles per unit length, A = 1e-6.
k = (1,0,0): e = diag(0,-1,1). k = (1,1,0): the generator sets a_ij = -khat khat + zz
(axy = -1/2), which is not transverse; its TT part is -(1/2)(uu - zz), u = (1,-1,0)/sqrt2,
so the TT wave that should travel has plus amplitude -A/2 in the basis uu - zz.

Writes OUTDIR/v4_lw.json, OUTDIR/v4_lw_convergence.png, OUTDIR/v4_lw_oblique.png.
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

A = 1.0e-6


def read_tab(path):
    with open(path) as fh:
        head = fh.readline()
        cols = fh.readline().lstrip("#").split()
    t = float(re.search(r"time=([0-9.eE+-]+)", head).group(1))
    d = np.loadtxt(path)
    return t, {c: d[:, i] for i, c in enumerate(cols)}


def read_hst(path):
    with open(path) as fh:
        fh.readline()
        names = re.findall(r"\[\d+\]=(\S+)", fh.readline())
    d = np.loadtxt(path)
    return {n: d[:, i] for i, n in enumerate(names)}


def x_wave(run):
    files = sorted(glob.glob(os.path.join(run, "tab", "*.tab")))
    out = []
    for f in files:
        t, d = read_tab(f)
        x = d["x1v"]
        ph = 2*np.pi*(x - t)
        hp = 0.5*(d["z4c_gzz"] - d["z4c_gyy"])        # plus amplitude, exact A sin(ph)
        ap = 0.5*(d["z4c_Azz"] - d["z4c_Ayy"])        # exact pi A cos(ph)
        err_h = np.sqrt(np.mean((hp - A*np.sin(ph))**2))/A
        err_a = np.sqrt(np.mean((ap - np.pi*A*np.cos(ph))**2))/(np.pi*A)
        # amplitude and phase of the numerical wave
        M = np.array([np.sin(2*np.pi*x), np.cos(2*np.pi*x)]).T
        c, *_ = np.linalg.lstsq(M, hp, rcond=None)
        amp = np.hypot(*c)/A
        phase = np.arctan2(-c[1], c[0])                # hp = amp sin(2 pi x - phase)
        dphi = (phase - 2*np.pi*t + np.pi) % (2*np.pi) - np.pi
        # non-TT and off-diagonal components
        other = max(np.abs(d["z4c_gxx"] - 1).max(), np.abs(d["z4c_gxy"]).max(),
                    np.abs(d["z4c_gyz"]).max(), np.abs(d["z4c_gyy"] + d["z4c_gzz"] - 2).max())
        out.append({"t": t, "err_h": err_h, "err_A": err_a, "amp": amp, "dphase": dphi,
                    "max_non_TT_over_A": other/A, "alpha_minus_1": float(
                        np.abs(d["z4c_alpha"] - 1).max())})
    return out


def oblique(run, y0):
    files = sorted(glob.glob(os.path.join(run, "tab", "*.tab")))
    u = np.array([1.0, -1.0, 0.0])/np.sqrt(2)
    z = np.array([0.0, 0.0, 1.0])
    kh = np.array([1.0, 1.0, 0.0])/np.sqrt(2)
    ep = np.outer(u, u) - np.outer(z, z)
    agen = -np.outer(kh, kh) + np.outer(z, z)
    names = [["gxx", "gxy", "gxz"], ["gxy", "gyy", "gyz"], ["gxz", "gyz", "gzz"]]
    out = []
    for f in files:
        t, d = read_tab(f)
        x = d["x1v"]
        h = np.array([[d["z4c_" + names[i][j]] - (1.0 if i == j else 0.0) for j in range(3)]
                      for i in range(3)])
        hplus = np.einsum("ij,ij...->...", ep, h)/2
        hgen = np.einsum("ij,ij...->...", agen, h)/np.sum(agen*agen)
        hlong = np.einsum("i,j,ij...->...", kh, kh, h)
        ph = 2*np.pi*(x + y0 - np.sqrt(2)*t)
        M = np.array([np.sin(2*np.pi*x), np.cos(2*np.pi*x)]).T
        c, *_ = np.linalg.lstsq(M, hplus, rcond=None)
        out.append({"t": t,
                    "hplus_err_vs_minus_half_A": float(
                        np.sqrt(np.mean((hplus + 0.5*A*np.sin(ph))**2))/A),
                    "hplus_amp_over_A": float(np.hypot(*c)/A),
                    "gen_pattern_amp_over_A": float(np.sqrt(2*np.mean(hgen**2))/A),
                    "longitudinal_hkk_rms_over_A": float(np.sqrt(np.mean(hlong**2))/A)})
    return out


def main():
    run, outd = sys.argv[1], sys.argv[2]
    os.makedirs(outd, exist_ok=True)
    res = {"x": {}, "oblique": {}, "hst": {}}
    Ns = [16, 32, 64, 128]
    for N in Ns:
        res["x"][N] = x_wave(os.path.join(run, f"x_N{N}"))
    res["x_long_N32"] = x_wave(os.path.join(run, "x_N32_long"))
    final = {N: res["x"][N][-1] for N in Ns}
    res["x_final"] = final
    res["x_order_err_h"] = {f"{a}-{b}": float(np.log2(final[a]["err_h"]/final[b]["err_h"]))
                            for a, b in zip(Ns[:-1], Ns[1:])}
    res["x_order_amp_loss"] = {f"{a}-{b}": float(np.log2((1 - final[a]["amp"])
                                                         / (1 - final[b]["amp"])))
                               for a, b in zip(Ns[:-1], Ns[1:])
                               if final[b]["amp"] < 1}
    for N in (16, 32):
        res["oblique"][N] = oblique(os.path.join(run, f"ob_N{N}"), 1.5/N)
    for name in ("x_N32", "ob_N32"):
        h = read_hst(glob.glob(os.path.join(run, name, "*.hst"))[0])
        res["hst"][name] = {k: float(v[1]) for k, v in h.items() if "norm" in k}
    with open(os.path.join(outd, "v4_lw.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: res[k] for k in ("x_final", "x_order_err_h", "x_order_amp_loss",
                                           "hst")}, indent=1))
    print("long:", res["x_long_N32"][-1])
    for N in (16, 32):
        print("oblique", N, res["oblique"][N][0], res["oblique"][N][-1])

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    for col, N in zip(fs.SERIES, Ns):
        s = res["x"][N]
        ax.semilogy([q["t"] for q in s], [max(q["err_h"], 1e-16) for q in s], color=col,
                    label=f"$N={N}$")
    ax.set_xlabel("time (box crossings)")
    ax.set_ylabel(r"rms error of $h_+$ / $A$")
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    e = np.array([final[N]["err_h"] for N in Ns])
    ax2.loglog(Ns, e, "o-", color=fs.PAL["red"], label=r"$h_+$ at $t=10$")
    ax2.loglog(Ns, [1 - final[N]["amp"] for N in Ns], "s-", color=fs.PAL["blue"],
               label="amplitude loss")
    ax2.loglog(Ns, [abs(final[N]["dphase"]) for N in Ns], "^-", color=fs.PAL["yellow"],
               label="phase error (rad)")
    Nn = np.array(Ns, float)
    ax2.loglog(Nn, e[0]*(Nn/16)**-4, **fs.GUIDE, label=r"$N^{-4}$")
    ax2.loglog(Nn, e[0]*(Nn/16)**-6, color="k", lw=1, ls=":", label=r"$N^{-6}$")
    ax2.set_xlabel("cells per wavelength $N$")
    ax2.set_ylabel("error after 10 crossings")
    ax2.legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(outd, "v4_lw_convergence"))

    fig = plt.figure(figsize=(fs.COLUMN_WIDTH*1.3, 3.2))
    ax = fig.add_axes([0.16, 0.15, 0.80, 0.78])
    for col, N in zip((fs.PAL["blue"], fs.PAL["red"]), (16, 32)):
        s = res["oblique"][N]
        tt = [q["t"] for q in s]
        ax.plot(tt, [q["hplus_amp_over_A"] for q in s], "o-", color=col, ms=3,
                label=fr"TT plus amplitude, $N={N}$")
        ax.plot(tt, [q["longitudinal_hkk_rms_over_A"] for q in s], "s--", color=col, ms=3,
                label=fr"rms $\hat k\hat k{{:}}h$, $N={N}$")
    ax.axhline(0.5, **fs.GUIDE)
    ax.set_xlabel("time")
    ax.set_ylabel("amplitude / $A$")
    ax.legend(loc="center right", fontsize=7)
    fs.save(fig, os.path.join(outd, "v4_lw_oblique"))


if __name__ == "__main__":
    main()
