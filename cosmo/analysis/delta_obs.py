"""Observer density contrast at the overdensity and the underdensity: relativistic run
against the Newtonian reference and linear theory (cosmo/PLAN.md, C1 and C2).

    python3 delta_obs.py <gr rundir> [--newton FILE.npz] [--delta D] [--out NAME]

The relativistic run supplies, at the two probes, the lapse, the deposited energy
density and the proper time of the normal observer, who is comoving with the matter at
these points by symmetry. The proper time is integrated again here from the recorded
lapse with Simpson's rule. With a_p = (1 + 3 H0 tau / 2)^(2/3),

    delta_obs = (E / rho_0) a_p^3 - 1.

Linear theory for the growing mode of the single-wavelength data (cosmo/TESTLOG.md):
delta_obs = +-3 delta [a_p + 3 (H0/k)^2 a_p^(-3/2)], times the window of the probe.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_simpson

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrp_io import read_history  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def gr_probes(rundir, base="east", H0=1.0):
    """a_p and delta_obs at the two probes of a relativistic run."""
    h = read_history(os.path.join(rundir, base + ".nrpic.hst"))
    rho0 = 3.0*H0**2/(8.0*np.pi)
    t = h["time"]
    out = {"t": t}
    for i, (ka, ke) in enumerate((("alpha_probe", "E_probe"),
                                  ("alpha_probe1", "E_probe1"))):
        tau = cumulative_simpson(h[ka], x=t, initial=0.0)
        a_p = (1.0 + 1.5*H0*tau)**(2.0/3.0)
        out[f"tau_{i}"] = tau
        out[f"a_p_{i}"] = a_p
        out[f"delta_obs_{i}"] = h[ke]/rho0*a_p**3 - 1.0
        out[f"alpha_{i}"] = h[ka]
    return out, h


def linear(a_p, delta, sign, H0=1.0, L=4.0, n=None):
    k = 2.0*np.pi/L
    win = 1.0
    if n is not None:
        x = 0.5*k*L/n
        win = np.cos(x)*np.sin(x)/x
    return sign*3.0*delta*win*(a_p + 3.0*(H0/k)**2*a_p**-1.5)


if __name__ == "__main__":
    args = sys.argv[1:]
    rundir = args[0]
    opt = {args[i][2:]: args[i+1] for i in range(1, len(args) - 1, 2)}
    delta = float(opt.get("delta", "1e-4"))
    n = int(opt.get("n", "32"))
    out = opt.get("out", "delta_obs")
    g, h = gr_probes(rundir)
    nw = np.load(opt["newton"]) if "newton" in opt else None

    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, wspace=0.26,
                        hspace=0.06)
    names = ("overdensity", "underdensity")
    for i, sign in ((0, 1.0), (1, -1.0)):
        ap = g[f"a_p_{i}"]
        lin = linear(ap, delta, sign, n=n)
        ax = axs[0, i]
        ax.loglog(ap, np.abs(g[f"delta_obs_{i}"]), color=fs.PAL["red"],
                  label="general relativity")
        if nw is not None:
            ax.loglog(nw[f"a_p_{i}"], np.abs(nw[f"delta_obs_{i}"]), color=fs.PAL["blue"],
                      ls="--", label="Newtonian")
        ax.loglog(ap, np.abs(lin), label="linear theory", **fs.GUIDE)
        ax.set_ylabel(r"$|\delta_{\rm obs}|$, " + names[i])
        ax.legend(frameon=False, loc="upper left")
        ax = axs[1, i]
        ax.semilogx(ap, g[f"delta_obs_{i}"]/lin - 1.0, color=fs.PAL["red"])
        if nw is not None:
            ax.semilogx(nw[f"a_p_{i}"], nw[f"delta_obs_{i}"]
                        / linear(nw[f"a_p_{i}"], delta, sign, n=n) - 1.0,
                        color=fs.PAL["blue"], ls="--")
        ax.axhline(0.0, **fs.THIN)
        ax.set_ylim(-0.05, 0.05)
        ax.set_ylabel(r"$\delta_{\rm obs}/\delta_{\rm lin} - 1$")
        ax.set_xlabel(r"$a_p$", labelpad=-2)
    figdir = os.path.join(HERE, "figs")
    os.makedirs(figdir, exist_ok=True)
    fs.save(fig, os.path.join(figdir, out))
    print(os.path.join(figdir, out + ".png"))

    # numbers
    for i, sign in ((0, 1.0), (1, -1.0)):
        ap = g[f"a_p_{i}"]
        r = g[f"delta_obs_{i}"]/linear(ap, delta, sign, n=n)
        line = " ".join(f"a_p={ap[j]:.1f}:{r[j]:.4f}"
                        for j in [int(np.argmin(np.abs(ap - v)))
                                  for v in (1, 1.5, 2, 3, 5, 10, 30, 60, 100) if v <= ap[-1]*1.01])
        print(f"{names[i]}: relativistic / linear: {line}")
        if nw is not None:
            apn = nw[f"a_p_{i}"]
            gi = np.interp(apn, ap, g[f"delta_obs_{i}"])
            ok = apn <= ap[-1]
            d = gi[ok]/nw[f"delta_obs_{i}"][ok] - 1.0
            print(f"{names[i]}: relativistic / Newtonian - 1: largest {np.abs(d).max():.3e}, "
                  f"at the end {d[-1]:+.3e}")
    z = np.loadtxt(os.path.join(rundir, "east.z4c.user.hst"))
    print(f"constraint norms (sqrt of the history columns): Hamiltonian start "
          f"{np.sqrt(z[0, 3]):.2e}, largest {np.sqrt(z[:, 3].max()):.2e}, end "
          f"{np.sqrt(z[-1, 3]):.2e}; momentum largest {np.sqrt(z[:, 4].max()):.2e}")
