"""Plane-wave linear mode over a thousandfold expansion (cosmo/PLAN.md, C5; test B of
Daverio, Dirian & Mitsou, arXiv:1904.07841, Figs. 7 and 8).

    python3 daverio_b.py [--runs runs/cosmo] [--cases dav_b_n32,dav_b_n32_c01,dav_b_n64]

From the fields recorded along the x line: the potential phi = (a^2 chi - 1)/2, which
must stay constant, and the density contrast E a^3 / rho_0 - 1 against linear theory,
    delta = -2 [1 + k^2 / (3 H_c^2)] phi_0 sin(k x),   H_c = 1/sqrt(a) (conformal Hubble
rate in the units of this code), phi_0 = -(3/2) A / k^2;
    delta_delta = max |delta_num - delta_an| / max |delta_an|.
From the constraint statistics: the largest relative Hamiltonian constraint.
Conformal time of the source paper: t / 0.0105535 Mpc/h.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs  # noqa: E402

HC0, LBOX, AMP = 0.0105535, 1.35085, 1e-7
RHO0 = 3.0/(8.0*np.pi)
K = 2.0*np.pi/LBOX
PHI0 = -1.5*AMP/K**2
TREF = (100.0, 1000.0, 3000.0, 5806.0)
PAPER = {"phi_initial_final_e-9": {32: (6.868, 7.202), 64: (6.918, 6.988), 128: (6.931, 6.948)},
         "delta_delta": {32: (2.5e-3, 1.81e-2, 2.89e-2, 3.57e-2),
                         64: (6.2e-4, 4.55e-3, 7.3e-3, 9.10e-3),
                         128: (1.55e-4, 1.14e-3, 1.85e-3, 2.35e-3)},
         "Hr_max_end": {32: 4.6e-9, 64: 2.3e-8, 128: 1.1e-7}}


def load(rundir):
    ftxt = os.path.join(rundir, "east.line.txt")
    if not os.path.exists(ftxt):
        return None
    x = np.loadtxt(ftxt, skiprows=2)
    n = len(x)
    r = np.fromfile(os.path.join(rundir, "east.line.bin"))
    r = r[:(len(r)//(1 + 5*n))*(1 + 5*n)].reshape(-1, 1 + 5*n)
    t = r[:, 0]
    a = (1.0 + 0.5*t)**2
    chi, E = r[:, 1:1+n], r[:, 1+3*n:1+4*n]
    phi = 0.5*(a[:, None]**2*chi - 1.0)
    dnum = E*a[:, None]**3/RHO0 - 1.0
    dan = -2.0*(1.0 + K**2*a[:, None]/3.0)*PHI0*np.sin(K*x)[None, :]
    s = np.sin(K*x)
    out = {"n": n, "x": x, "t": t/HC0, "a": a, "phi": phi,
           "phi_amp": 2.0*(phi*s[None, :]).mean(axis=1),
           "phi_mean": phi.mean(axis=1),
           "dd": np.abs(dnum - dan).max(axis=1)/np.abs(dan).max(axis=1),
           # the same with the mean over the line removed: the error of the homogeneous
           # background (time integration) exceeds a contrast of 1e-7 at early times
           "dd0": np.abs(dnum - dnum.mean(axis=1)[:, None] - dan).max(axis=1)
           / np.abs(dan).max(axis=1),
           "bg": dnum.mean(axis=1),
           "d_amp_ratio": 2.0*(dnum*s[None, :]).mean(axis=1)/(-2.0*(1.0 + K**2*a/3.0)*PHI0)}
    c = np.loadtxt(os.path.join(rundir, "east.cstat.hst"))
    out["ct"] = c[:, 0]/HC0
    out["Hr_max"], out["Hr_mean"] = c[:, 10], c[:, 11]
    out["Mr_max"] = c[:, 14]
    return out


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    cases = opt.get("cases", "dav_b_n32,dav_b_n32_c01,dav_b_n64,dav_b_n128").split(",")
    data = {c: load(os.path.join(runs, c)) for c in cases}
    data = {c: d for c, d in data.items() if d is not None}
    if not data:
        sys.exit("no run found")
    fs.use_style()
    cols = [fs.PAL["blue"], fs.PAL["orange"], fs.PAL["green"], fs.PAL["red"]]
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.95, wspace=0.36)
    summ = {}
    for col, (c, d) in zip(cols, data.items()):
        lab = c.replace("dav_b_", "").replace("_c01", ", step 0.1").replace("n", r"$N_g=$")
        axs[0].plot(d["x"]/LBOX, 1e9*d["phi"][0], color=col, lw=0.6, ls=":")
        axs[0].plot(d["x"]/LBOX, 1e9*d["phi"][-1], color=col, lw=1.0, label=lab)
        axs[1].semilogy(d["t"][1:], d["dd"][1:], color=col, lw=0.6, ls=":")
        axs[1].semilogy(d["t"][1:], d["dd0"][1:], color=col)
        axs[2].semilogy(d["ct"][1:], d["Hr_max"][1:], color=col)
        s = {"n": int(d["n"]), "t_end": float(d["t"][-1]),
             "phi_amp_start_e-9": float(1e9*d["phi_amp"][0]),
             "phi_amp_end_e-9": float(1e9*d["phi_amp"][-1]),
             "phi_amp_change": float(d["phi_amp"][-1]/d["phi_amp"][0] - 1.0),
             "phi_mean_end_e-9": float(1e9*d["phi_mean"][-1]),
             "delta_delta": {f"{t:g}": float(np.interp(t, d["t"], d["dd"])) for t in TREF
                             if t <= d["t"][-1]*1.001},
             "delta_delta_mean_removed": {f"{t:g}": float(np.interp(t, d["t"], d["dd0"]))
                                          for t in TREF if t <= d["t"][-1]*1.001},
             "background_density_error_end": float(d["bg"][-1]),
             "background_density_error_max": float(np.abs(d["bg"]).max()),
             "delta_amp_over_linear_end": float(d["d_amp_ratio"][-1]),
             "Hr_max_end": float(d["Hr_max"][-1]), "Hr_max_max": float(d["Hr_max"].max()),
             "Mr_max_end": float(d["Mr_max"][-1])}
        summ[c] = s
    axs[0].set_xlabel(r"$x/L$")
    axs[0].set_ylabel(r"$\phi \times 10^{9}$ (dotted: start)")
    axs[0].legend(frameon=False, fontsize=6, loc="upper left")
    axs[1].set_xlabel(r"conformal time (Mpc/$h$)")
    axs[1].set_ylabel(r"$\delta_\delta$ (dotted: with the error of the mean)")
    axs[2].set_xlabel(r"conformal time (Mpc/$h$)")
    axs[2].set_ylabel(r"largest $H_r$")
    figdir = os.path.join(HERE, "figs")
    fs.save(fig, os.path.join(figdir, "daverio_b"))
    with open(os.path.join(HERE, "daverio_b.json"), "w") as fp:
        json.dump(summ, fp, indent=1)
    print(f"analytic phi amplitude {1e9*PHI0:.4f}e-9")
    for c, s in summ.items():
        dd = " ".join(f"t={k}:{v:.2e}" for k, v in s["delta_delta"].items())
        print(f"== {c} (n = {s['n']}, end t = {s['t_end']:.0f})")
        print(f"   phi amplitude {s['phi_amp_start_e-9']:.4f}e-9 -> {s['phi_amp_end_e-9']:.4f}e-9 "
              f"(change {100*s['phi_amp_change']:+.2f} percent); mean of phi at the end "
              f"{s['phi_mean_end_e-9']:+.4f}e-9")
        dd0 = " ".join(f"t={k}:{v:.2e}" for k, v in s["delta_delta_mean_removed"].items())
        print(f"   delta_delta {dd}; density amplitude over linear theory at the end "
              f"{s['delta_amp_over_linear_end']:.4f}")
        print(f"   delta_delta with the mean removed {dd0}; error of the mean density: "
              f"largest {s['background_density_error_max']:.2e}, end "
              f"{s['background_density_error_end']:+.2e}")
        print(f"   largest H_r: end {s['Hr_max_end']:.2e}, over the run {s['Hr_max_max']:.2e}; "
              f"largest M_r at the end {s['Mr_max_end']:.2e}")
    print("source paper:", json.dumps(PAPER))
    print(os.path.join(figdir, "daverio_b.png"))


if __name__ == "__main__":
    main()
