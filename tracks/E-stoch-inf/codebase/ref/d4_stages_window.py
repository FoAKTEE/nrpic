"""D4 of ../JOURNAL.md: (a) stage times and effective weights of the low-storage RK4 of
athenak/src/driver/driver.cpp; (b) analytic time derivatives of the window of
arXiv:2512.14649 against finite differences; (c) the number of lattice modes the noise
touches in a 256^3 box as the window rolls (de Sitter estimate, sigma = 1).

Usage: python3 -I d4_stages_window.py <outdir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../../python")))
import synth                                     # noqa: E402
from nrpic import figstyle as fs                 # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {}
    # (a) stage times
    c, b, a0 = synth.lowstorage_tableau()
    res["rk4_2S"] = dict(c=c.tolist(), b=b.tolist(), coef_un=float(a0),
                         moments=[float((b*c**m).sum() - 1.0/(m + 1)) for m in range(6)])
    print("c =", c, "b =", b, "a0 =", a0)
    print("sum b c^m - 1/(m+1):", res["rk4_2S"]["moments"])
    # a non-autonomous check: u' = cos(t) over one unit of time with 10..160 steps,
    # with the source evaluated at the stage times c (right) or at the step start (wrong)
    errs = {"stage": [], "start": []}
    nsteps = [10, 20, 40, 80, 160]
    for ns in nsteps:
        dt = 1.0/ns
        for mode in errs:
            u = 0.0
            for i in range(ns):
                t = i*dt
                tc = t + (c if mode == "stage" else 0.0*c)*dt
                u = a0*u + dt*(b*np.cos(tc)).sum()
            errs[mode].append(abs(u - np.sin(1.0)))
    res["nonautonomous"] = dict(nsteps=nsteps, err=errs)
    print(errs)

    # (b) window derivatives, quasi-de Sitter with constant eps1, eps2 (Launay signs)
    H, eps1, eps2, s = 1.0, 0.01, -0.02, 5.0
    dln = H*(1.0 - eps1)
    d2ln = H*H*eps1*(eps2 - 1.0 + eps1)
    lnks = lambda t: np.log(1.0) + dln*t + 0.5*d2ln*t*t
    k = 1.0
    ts = np.linspace(-1.5, 1.5, 61)
    w1, w2 = synth.window_dt(k, np.exp(lnks(ts)), dln + d2ln*ts, d2ln, s)
    hstep = 1e-4
    W = lambda t: synth.window(k, np.exp(lnks(t)), s)
    w1n = (W(ts + hstep) - W(ts - hstep))/(2*hstep)
    w2n = (W(ts + hstep) - 2*W(ts) + W(ts - hstep))/hstep**2
    res["window"] = dict(
        max_rel_w1=float(np.max(np.abs(w1 - w1n))/np.max(np.abs(w1))),
        max_rel_w2=float(np.max(np.abs(w2 - w2n))/np.max(np.abs(w2))))
    print(res["window"])

    # (c) modes touched in a 256^3 box, |n| <= 64, as k_sigma = e^N k_min rolls
    N = 256
    nmax = N//4
    nb = synth.ball_modes(nmax)
    kk = np.sqrt((nb**2).sum(axis=1))
    efolds = np.linspace(0.0, np.log(nmax) + 1.5, 120)
    thr = 1e-3
    active = []
    for e in efolds:
        u = s*np.log(np.exp(e)/kk)
        active.append(int(np.count_nonzero(1.0/np.cosh(u)**2 > thr)))
    at_kmax = int(np.count_nonzero(1.0/np.cosh(s*np.log(nmax/kk))**2 > thr))
    res["active"] = dict(N=N, nmax=nmax, threshold=thr, modes_in_ball=int(len(nb)),
                         at_kmax=at_kmax, max_active=int(max(active)),
                         efold_of_max=float(efolds[int(np.argmax(active))]))
    print(res["active"])
    with open(os.path.join(outdir, "d4.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    # figure: left, window and its derivatives in time for one mode; middle,
    # non-autonomous convergence; right, active modes against e-folds
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.9))
    ax1 = fig.add_axes([0.07, 0.17, 0.25, 0.75])
    ax2 = fig.add_axes([0.40, 0.17, 0.25, 0.75])
    ax3 = fig.add_axes([0.73, 0.17, 0.25, 0.75])
    ax1.plot(ts, W(ts), color=fs.PAL["blue"], label="W")
    ax1.plot(ts, w1/np.max(np.abs(w1)), color=fs.PAL["red"], label="dW/dt (scaled)")
    ax1.plot(ts, w2/np.max(np.abs(w2)), color=fs.PAL["yellow"],
             label="d2W/dt2 (scaled)")
    ax1.plot(ts[::4], (w2n/np.max(np.abs(w2)))[::4], "o", ms=3, color="k",
             label="finite differences")
    ax1.set_xlabel("H (t - t_cross)")
    ax1.set_ylabel("window, s = 5")
    ax1.legend(fontsize=7, loc="lower left")
    ax2.loglog(nsteps, errs["stage"], "o-", color=fs.PAL["red"],
               label="source at stage times c")
    ax2.loglog(nsteps, errs["start"], "s-", color=fs.PAL["blue"],
               label="source at step start")
    ns = np.array(nsteps, float)
    ax2.loglog(ns, errs["stage"][0]*(ns/ns[0])**-4, **fs.GUIDE, label="slope -4")
    ax2.loglog(ns, errs["start"][0]*(ns/ns[0])**-1, **fs.THIN, ls=":",
               label="slope -1")
    ax2.set_xlabel("steps per unit time")
    ax2.set_ylabel("error of u' = cos t at t = 1")
    ax2.legend(fontsize=7, loc="lower left")
    ax3.plot(efolds, active, color=fs.PAL["red"])
    ax3.axvline(np.log(nmax), **fs.MASK_LINE)
    ax3.axhline(len(nb), **fs.GUIDE)
    ax3.text(0.2, len(nb)*1.15, "all modes |n| <= 64", fontsize=7)
    ax3.set_yscale("log")
    ax3.set_ylim(1, 3e6)
    ax3.set_xlabel("e-folds after first crossing")
    ax3.set_ylabel("modes with sech^2 u > 1e-3")
    fs.save(fig, os.path.join(outdir, "d4_stages_window"))


if __name__ == "__main__":
    main(sys.argv[1])
