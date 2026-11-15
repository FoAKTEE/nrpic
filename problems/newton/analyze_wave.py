#!/usr/bin/env python3
"""Test T4 of the Newtonian mode: growth of a plane wave in a periodic box with a
matter-dominated expansion (problems/newton/README.md), against

  (i)   the Zel'dovich solution (exact in plane symmetry up to shell crossing),
  (ii)  cosmo/newton/pm.py (spectral Poisson solve and gradient, cubic interpolation)
        for the same particle file, mesh, cloud and step,
  (iii) the scheme of the code in numpy (seven-point Laplacian, gradient of the
        Catmull-Rom interpolant; python/nrpic/newton.py) with the stepping of pm.py.

    analyze_wave.py --run LABEL:ICSTEM:RUNDIR [--run ...] --out DIR [--dt 0.005]
                    [--name wave] [--no-python]

Measure: rms over the particles of the difference in x (shortest periodic image),
divided by the rms displacement a A/(k sqrt 2) of the exact solution at that time.
Writes DIR/<name>.png and DIR/<name>.json. The Python references are cached in
DIR/<name>_<label>_pm.npz.
"""
import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "python"))
sys.path.insert(0, os.path.join(_ROOT, "cosmo", "newton"))
sys.path.insert(0, os.path.join(_ROOT, "cosmo", "ic"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import cosmo_id as cid  # noqa: E402
import pm  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402


class PMScheme(pm.PM):
    """pm.PM with the Poisson solve and the gather of the code."""

    def fields(self):
        rho = cid.cic_deposit(self.x, self.m, self.n, self.L, self.shape)
        if cid.DEP_COMP_C > 0.0:
            rho = cid.compensate_density([rho], cid.DEP_COMP_C, 0.0, cid.DEP_COMP_C2)[0]
        rho = cid.binomial(rho, self.nfilter, self.compensate)
        self.delta = rho/self.mean - 1.0
        self.phi = nw.scheme_fields(self.delta, self.L, four_pi_g=1.0)
        self.g = nw.gather_gradient(self.phi, self.x, self.L)[1]


def python_runs(stem, meta, nmesh, dt, steps, cache, nfilter=0, compensate=False,
                shape="cic"):
    """Positions and momenta of pm.PM and of PMScheme after the given numbers of steps."""
    if os.path.exists(cache):
        z = np.load(cache)
        if list(z["steps"]) == list(steps) and float(z["dt"]) == dt:
            return z["x_pm"], z["p_pm"], z["x_sc"], z["p_sc"]
    x0, p0, m, _ = nio.read_nrp(stem + ".nrp")
    out = []
    for cls in (pm.PM, PMScheme):
        sim = cls(x0, p0, m, nmesh, meta["L"], H0=meta["hubble"], nfilter=nfilter,
                  compensate=compensate, shape=shape)
        xs, ps, done = [], [], 0
        for s in steps:
            for _ in range(s - done):
                sim.step(dt)
            done = s
            xs.append(sim.x.copy())
            ps.append(sim.p.copy())
        out += [np.array(xs), np.array(ps)]
    np.savez(cache, steps=np.array(steps), dt=dt, x_pm=out[0], p_pm=out[1], x_sc=out[2],
             p_sc=out[3])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dt", type=float, default=0.005)
    ap.add_argument("--name", default="wave")
    ap.add_argument("--no-python", action="store_true")
    ap.add_argument("--nmesh", type=int, default=0,
                    help="cells per side of the run if not the particles per side")
    ap.add_argument("--shape", default="cic", choices=("cic", "tsc", "pcs"),
                    help="cloud of the run (<particles> deposit_shape)")
    ap.add_argument("--nfilter", type=int, default=0, help="<particles> nfilter")
    ap.add_argument("--compensate", action="store_true",
                    help="<particles> filter_compensate = true")
    ap.add_argument("--dep-comp-c", type=float, default=0.0,
                    help="<particles> deposit_comp_c")
    a = ap.parse_args()
    cid.DEP_COMP_C = a.dep_comp_c
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    cols = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"]]

    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.97, wspace=0.40,
                        hspace=0.27)
    res = {}
    for irun, spec in enumerate(a.run):
        label, stem, rundir = spec.split(":", 2)
        meta = json.load(open(stem + ".json"))
        n, L, amp, hub = meta["n"], meta["L"], meta["amp"], meta["hubble"]
        k = 2.0*np.pi/L
        h = L/n
        ac = 1.0/amp
        col = cols[irun]
        snaps = sorted(glob.glob(os.path.join(rundir, "*.part.*.bin")))
        nmesh = a.nmesh if a.nmesh > 0 else n     # default: one particle per cell
        times, xs, ps = [], [], []
        for f in snaps:
            t, _, x, u, _, tag = nw.read_snapshot(f)
            xo = np.empty_like(x)
            po = np.empty_like(u)
            xo[tag], po[tag] = x, u
            times.append(t)
            xs.append(xo)
            ps.append(po)
        times = np.array(times)
        aa = nw.scale_factor(times, hub)
        steps = [int(round(t/a.dt)) for t in times]
        q = ((np.arange(n**3)//(n*n)) + 0.5)*h           # Lagrangian x of each tag
        rmsd = aa*amp/(k*np.sqrt(2.0))

        def rel(xa, xb, i):
            d = xa - xb
            d -= L*np.round(d/L)
            return float(np.sqrt(np.mean(d*d))/rmsd[i])

        ez, ezp = [], []
        for i in range(len(times)):
            xz, pz = nw.zeldovich_wave(q, aa[i], amp, k, hub)
            ez.append(rel(xs[i][:, 0], xz, i))
            ezp.append(float(np.sqrt(np.mean((ps[i][:, 0] - pz)**2))
                             / np.sqrt(np.mean(pz**2))))
        ez, ezp = np.array(ez), np.array(ezp)
        pre = aa < ac*(1.0 - 1e-9)
        out = dict(rundir=rundir, n=n, times=times.tolist(), a=aa.tolist(),
                   zeldovich_x=ez.tolist(), zeldovich_p=ezp.tolist(),
                   transverse_max=float(max(np.max(np.abs(xs[i][:, 1:] - xs[0][:, 1:]))
                                            for i in range(len(times)))))
        if not a.no_python:
            cache = os.path.join(a.out, "%s_%s_pm.npz" % (a.name, label.replace(" ", "")))
            x_pm, p_pm, x_sc, p_sc = python_runs(stem, meta, nmesh, a.dt, steps, cache,
                                                 a.nfilter, a.compensate, a.shape)
            epm = np.array([rel(xs[i][:, 0], x_pm[i][:, 0], i) for i in range(len(times))])
            esc = np.array([rel(xs[i][:, 0], x_sc[i][:, 0], i) for i in range(len(times))])
            esc3 = np.array([float(np.max(np.abs((xs[i] - x_sc[i])
                                                 - L*np.round((xs[i] - x_sc[i])/L))))
                             for i in range(len(times))])
            ezs = np.array([rel(x_pm[i][:, 0], nw.zeldovich_wave(q, aa[i], amp, k, hub)[0],
                                i) for i in range(len(times))])
            out.update(vs_pm=epm.tolist(), vs_scheme=esc.tolist(),
                       vs_scheme_max_abs=esc3.tolist(), pm_vs_zeldovich=ezs.tolist())

        # ---- history: Layzer-Irvine and momentum
        hst = nw.read_newton_hst(glob.glob(os.path.join(rundir, "*.newton.hst"))[0])
        ah = hst["a"]
        scale = np.max(np.abs(ah*hst["W"]))
        li = (hst["C"] - hst["C"][0])/scale
        prec = ah < ac
        out.update(layzer_irvine_max_before_crossing=float(np.max(np.abs(li[prec]))),
                   layzer_irvine_max=float(np.max(np.abs(li))),
                   layzer_irvine_scale=float(scale),
                   momentum_max=float(max(np.max(np.abs(hst["P_%s" % c])) for c in "xyz")
                                      / (hst["mass"][0]*hub*amp/k)),
                   mg_cycles_mean=float(np.mean(hst["mg_cycles"][1:])),
                   mg_defect_max=float(np.max(hst["mg_defect"])),
                   steps=int(len(ah) - 1))
        res[label] = out

        # ---- figure
        if irun == len(a.run) - 1:
            ax = axs[0, 0]
            sel = [i for i in range(len(times))
                   if abs(times[i] - round(times[i])) < 1e-6]
            cs = fs.series_colors(len(sel), "viridis")
            line = slice(0, n**3, n*n)                     # one particle per q_x
            qq = np.linspace(0.0, L, 400)
            for cc, i in zip(cs, sel):
                if aa[i] < ac*1.0001:
                    xz, pz = nw.zeldovich_wave(qq, aa[i], amp, k, hub)
                    ax.plot(xz, pz, color="k", lw=0.8)
                ax.plot(xs[i][line, 0], ps[i][line, 0], ".", ms=3, color=cc,
                        label="a = %.2f" % aa[i])
            ax.set_xlim(0, L)
            ax.set_xlabel(r"$x$", labelpad=-1)
            ax.set_ylabel(r"$p_x = a\,dx/dt$")
            ax.legend(loc="lower left", fontsize=7, ncol=2, markerscale=2,
                      handletextpad=0.1, columnspacing=0.6)
        ax = axs[0, 1]
        ax.plot(aa[1:][pre[1:]], ez[1:][pre[1:]], "o-", ms=3, color=col,
                label=label + ", position")
        ax.plot(aa[1:][pre[1:]], ezp[1:][pre[1:]], "s--", ms=3, mfc="none", color=col,
                label="momentum")
        ax.set_yscale("log")
        ax.set_xlabel(r"$a$", labelpad=-1)
        ax.set_ylabel("error against Zel'dovich")
        ax.legend(loc="lower right", fontsize=7)
        if not a.no_python:
            ax = axs[0, 2]
            ax.plot(aa[1:], epm[1:], "o-", ms=3, color=col, label=label + r", pm.py")
            ax.axvline(ac, **fs.MASK_LINE)
            ax.set_yscale("log")
            ax.set_xlabel(r"$a$", labelpad=-1)
            ax.set_ylabel("code - pm.py")
            ax.legend(loc="lower right", fontsize=7)
            ax = axs[1, 0]
            ax.plot(aa[1:], np.maximum(esc[1:], 1e-17), "o-", ms=3, color=col, label=label)
            ax.axvline(ac, **fs.MASK_LINE)
            ax.set_yscale("log")
            ax.set_xlabel(r"$a$", labelpad=-1)
            ax.set_ylabel("code - numpy scheme")
            ax.set_ylim(1e-16, 1e-13)
            ax.legend(loc="lower right", fontsize=7)
        ax = axs[1, 1]
        ax.plot(ah, 1e3*li, "-", color=col, label=label)
        ax.axvline(ac, **fs.MASK_LINE)
        ax.axhline(0.0, **fs.MASK_LINE)
        ax.set_xlabel(r"$a$", labelpad=-1)
        ax.set_ylabel(r"$(C-C_0)/\max a|W|$  [$10^{-3}$]")
        ax.legend(loc="lower left", fontsize=7)
        ax = axs[1, 2]
        ax.plot(ah, hst["K"]*ah, "-", color=col, label=label + r", $aK$")
        ax.plot(ah, -hst["W"]*ah, "--", color=col, label=r"$-aW$")
        ax.plot(ah, hst["int_K_da"], ":", color=col, label=r"$\int K\,da$")
        ax.axvline(ac, **fs.MASK_LINE)
        ax.set_xlabel(r"$a$", labelpad=-1)
        ax.set_ylabel("energies")
        ax.legend(loc="upper left", fontsize=7)
    fig.savefig(os.path.join(a.out, a.name + ".png"), dpi=200)
    with open(os.path.join(a.out, a.name + ".json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
