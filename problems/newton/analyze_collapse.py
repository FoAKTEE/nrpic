#!/usr/bin/env python3
"""Test T3 of the Newtonian mode: cold collapse of a homogeneous ball from rest against
the cycloid (problems/newton/README.md).

    analyze_collapse.py --run LABEL:ICSTEM:RUNDIR [--run ...] --out DIR [--name collapse]

ICSTEM is the particle file without extension (ICSTEM.nrp, ICSTEM.json of make_ic.py).
The reference is the homogeneous ball that the lattice samples: mass M, density
M/(N h^3), every shell follows s(t) = r/r_0 of python/nrpic/newton.py (cycloid).
Writes DIR/<name>.png and DIR/<name>.json: deviation of r/r_0 from the cycloid (mean,
spread, inner and outer particles), energy, the second moment and its three time
derivatives against the exact ones, and the consistency of the history columns.
"""
import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def at(tt, t, y):
    """y(t) at the times tt by linear interpolation."""
    return np.interp(tt, t, y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="collapse")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    cols = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]

    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.97, wspace=0.36,
                        hspace=0.27)
    res = {}
    for irun, spec in enumerate(a.run):
        label, stem, rundir = spec.split(":", 2)
        meta = json.load(open(stem + ".json"))
        x0, _, m, _ = nio.read_nrp(stem + ".nrp")
        c = np.array(meta["center"])
        gm = meta["mass"]
        reff = (3.0*meta["nmassive"]*meta["spacing"]**3/(4.0*np.pi))**(1.0/3.0)
        tff = nw.free_fall_time(reff, gm)
        r0 = np.sqrt(((x0 - c)**2).sum(axis=1))
        inner, outer = r0 < 0.8*meta["radius"], r0 > 0.9*meta["radius"]
        col = cols[irun]

        # ---- particles against the cycloid
        ts, mean, lo, hi, dev, dev_in, dev_out, spread_in = [], [], [], [], [], [], [], []
        for f in sorted(glob.glob(os.path.join(rundir, "*.part.*.bin"))):
            t, _, x, u, _, tag = nw.read_snapshot(f)
            if t >= tff:
                continue
            assert len(tag) == len(r0), "particles were lost"
            q = np.empty(len(tag))
            q[tag] = np.sqrt(((x - c)**2).sum(axis=1))
            ratio = q/r0
            s = nw.cycloid(t, reff, gm)[0][0]
            ts.append(t)
            mean.append(ratio.mean())
            lo.append(np.percentile(ratio, 5))
            hi.append(np.percentile(ratio, 95))
            dev.append(ratio.mean()/s - 1.0)
            dev_in.append(ratio[inner].mean()/s - 1.0)
            dev_out.append(ratio[outer].mean()/s - 1.0)
            spread_in.append(ratio[inner].std()/s)
        ts = np.array(ts)

        # ---- history
        h = nw.read_newton_hst(glob.glob(os.path.join(rundir, "*.newton.hst"))[0])
        t = h["time"]
        e = h["K"] + h["W"]
        de = (e - e[0])/abs(e[0])
        em = h["K"] + h["W_mesh"]
        dem = (em - em[0])/abs(em[0])
        i0 = h["I_xx"][0]
        ex = nw.ball_moment(t, i0, reff, gm)
        exm = nw.ball_moment(h["time_d3I"], i0, reff, gm)
        with np.errstate(divide="ignore", invalid="ignore"):
            rI = h["I_xx"]/ex[0] - 1.0
            rdI = h["dI_xx"]/ex[1] - 1.0
            rd2I = h["d2I_xx"]/ex[2] - 1.0
            rd3I = h["d3I_xx"]/exm[3] - 1.0
        # The difference quotient of d2I carries the fluctuation of the mesh force at the
        # rate at which the particles cross cells; its average over a window of 2 nsm + 1
        # steps (about a tenth of the free-fall time) is compared as well.
        nsm = max(1, int(round(0.05*tff/np.median(np.diff(t)))))
        ker = np.ones(2*nsm + 1)/(2*nsm + 1)
        d3s = np.convolve(h["d3I_xx"][1:], ker, mode="valid")
        tsm = np.convolve(h["time_d3I"][1:], ker, mode="valid")
        d3x = np.convolve(exm[3][1:], ker, mode="valid")
        rd3s = d3s/d3x - 1.0
        # consistency of the columns: centred differences (uniform step)
        dt = np.diff(t)
        uni = np.allclose(dt, dt[0], rtol=1e-9)
        fdI = (h["I_xx"][2:] - h["I_xx"][:-2])/(t[2:] - t[:-2])
        fddI = (h["dI_xx"][2:] - h["dI_xx"][:-2])/(t[2:] - t[:-2])
        c1 = np.max(np.abs(fdI - h["dI_xx"][1:-1]))/np.max(np.abs(h["dI_xx"]))
        c2 = np.max(np.abs(fddI - h["d2I_xx"][1:-1]))/np.max(np.abs(h["d2I_xx"]))
        q3 = np.diff(h["d2I_xx"])/dt
        c3 = np.max(np.abs(q3 - h["d3I_xx"][1:]))/np.max(np.abs(h["d3I_xx"]))
        pscale = gm*np.sqrt(gm/reff)
        thalf, tend = 0.5*tff, ts[-1]
        res[label] = dict(
            rundir=rundir, N_particles=int(len(r0)), reference_radius=reff,
            free_fall_time=tff, t_end=float(t[-1]), t_end_over_tff=float(t[-1]/tff),
            steps=int(len(t) - 1), uniform_step=bool(uni),
            dev_mean_half=float(at(thalf, ts, dev)), dev_mean_end=float(dev[-1]),
            dev_inner_half=float(at(thalf, ts, dev_in)), dev_inner_end=float(dev_in[-1]),
            dev_outer_half=float(at(thalf, ts, dev_out)), dev_outer_end=float(dev_out[-1]),
            spread_inner_end=float(spread_in[-1]), t_last_snapshot=float(tend),
            energy0=float(e[0]), energy_rel_half=float(at(thalf, t, de)),
            energy_rel_end=float(de[-1]), energy_rel_max=float(np.max(np.abs(de))),
            energy_mesh_rel_end=float(dem[-1]),
            I_rel_half=float(at(thalf, t, rI)), I_rel_end=float(rI[-1]),
            dI_rel_half=float(at(thalf, t[1:], rdI[1:])), dI_rel_end=float(rdI[-1]),
            d2I_rel_half=float(at(thalf, t, rd2I)), d2I_rel_end=float(rd2I[-1]),
            d3I_rel_half=float(at(thalf, h["time_d3I"][1:], rd3I[1:])),
            d3I_rel_end=float(rd3I[-1]),
            d3I_rel_rms=float(np.sqrt(np.mean(rd3I[1:]**2))),
            d3I_averaged_window_steps=int(2*nsm + 1),
            d3I_averaged_rel_half=float(at(thalf, tsm, rd3s)),
            d3I_averaged_rel_end=float(rd3s[-1]),
            d3I_averaged_rel_max=float(np.max(np.abs(rd3s))),
            columns_dI_vs_difference_of_I=float(c1),
            columns_d2I_vs_difference_of_dI=float(c2),
            columns_d3I_vs_quotient_of_d2I=float(c3),
            momentum_max=float(max(np.max(np.abs(h["P_%s" % k])) for k in "xyz")/pscale),
            angular_momentum_max=float(max(np.max(np.abs(h["L_%s" % k]))
                                           for k in "xyz")/(pscale*reff)),
            mg_cycles_mean=float(np.mean(h["mg_cycles"][1:])),
            mg_defect_max=float(np.max(h["mg_defect"])))

        # ---- figure
        ax = axs[0, 0]
        if irun == 0:
            tt = np.linspace(0.0, 0.999*tff, 400)
            ax.plot(tt/tff, nw.cycloid(tt, reff, gm)[0], color=fs.PAL["blue"],
                    label="cycloid")
        ax.fill_between(ts/tff, lo, hi, color=col, alpha=0.2, lw=0)
        ax.plot(ts/tff, mean, "o", ms=3, color=col, label=label)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel(r"$r/r_0$")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.05)
        ax.legend(loc="lower left")
        ax = axs[0, 1]
        ax.plot(ts/tff, 100.0*np.array(dev), "-", color=col, label=label + ", all")
        ax.plot(ts/tff, 100.0*np.array(dev_in), "--", color=col, label=r"$r_0<0.8$")
        ax.plot(ts/tff, 100.0*np.array(dev_out), ":", color=col, label=r"$r_0>0.9$")
        ax.axhline(0.0, **fs.MASK_LINE)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel(r"$\langle r/r_0\rangle/s(t)-1$  [%]")
        ax.set_xlim(0, 1)
        ax.legend(loc="upper left", fontsize=7, ncol=1)
        ax = axs[0, 2]
        ax.plot(t/tff, 100.0*de, "-", color=col, label=label + r", $K+W$")
        ax.plot(t/tff, 100.0*dem, "--", color=col, label=r"$K+W_{\rm mesh}$")
        ax.axhline(0.0, **fs.MASK_LINE)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel(r"$(E-E_0)/|E_0|$  [%]")
        ax.set_xlim(0, 1)
        ax.legend(loc="upper left", fontsize=7)
        ax = axs[1, 0]
        if irun == 0:
            names = [r"$I$", r"$dI/dt$", r"$d^2I/dt^2$", r"$d^3I/dt^3$"]
            for k in range(4):
                tt = np.linspace(0.0, t[-1], 300)
                ax.plot(tt/tff, nw.ball_moment(tt, i0, reff, gm)[k]/i0,
                        color=fs.series_colors(4)[k], lw=1.0, label=names[k])
        st = max(1, len(t)//40)
        for k, key in enumerate(("I_xx", "dI_xx", "d2I_xx")):
            ax.plot(t[::st]/tff, h[key][::st]/i0, "o", ms=2.5, mfc="none", color=col)
        ax.plot(h["time_d3I"][1::st]/tff, h["d3I_xx"][1::st]/i0, "o", ms=2.5, mfc="none",
                color=col)
        ax.set_ylim(-6, 4)
        ax.set_xlim(0, 1)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel(r"$I_{xx}$ and derivatives / $I_{xx}(0)$")
        ax.legend(loc="lower left", fontsize=7, ncol=2)
        ax = axs[1, 1]
        ax.plot(t/tff, np.abs(rI), "-", color=col, label=label + r", $I$")
        ax.plot(t[1:]/tff, np.abs(rdI[1:]), "--", color=col, label=r"$dI/dt$")
        ax.plot(t/tff, np.abs(rd2I), "-.", color=col, label=r"$d^2I/dt^2$")
        ax.plot(h["time_d3I"][1:]/tff, np.abs(rd3I[1:]), ":", color=col, lw=0.8,
                label=r"$d^3I/dt^3$")
        ax.plot(tsm/tff, np.abs(rd3s), "-", color=col, lw=0.8,
                label=r"$d^3I/dt^3$, averaged")
        ax.set_yscale("log")
        ax.set_ylim(1e-6, 1)
        ax.set_xlim(0, 1)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel("relative deviation from exact")
        ax.legend(loc="lower right", fontsize=7, ncol=2)
        ax = axs[1, 2]
        ax.plot(t[1:]/tff, h["mg_cycles"][1:], "-", color=col, label=label)
        ax.set_xlim(0, 1)
        ax.set_xlabel(r"$t/t_{\rm ff}$", labelpad=-1)
        ax.set_ylabel("V cycles per step")
        ax.legend(loc="upper left", fontsize=8)
    for ax in axs.ravel():
        ax.set_xticks([0.0, 0.25, 0.5, 0.75])
    fig.savefig(os.path.join(a.out, a.name + ".png"), dpi=200)
    with open(os.path.join(a.out, a.name + ".json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
