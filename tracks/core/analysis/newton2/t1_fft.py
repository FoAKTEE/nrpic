#!/usr/bin/env python3
"""Test T1 of work package newton2: the Fourier Poisson solver of the Newtonian mode.

    t1_fft.py --run RUNDIR_OF_cases.py_t1 --out DIR

T1a  fft7 (newton_fft_symbol = seven_point) against mg (multigrid, threshold = 0): the
     plane wave of problems/newton, N = 32; positions and momenta at every snapshot,
     K, W, Phi_min, Phi_max of the history.
T1b  fftsp (spectral) against the scheme of the code in numpy with the spectral symbol
     (python/nrpic/newton.py scheme_fields, gather_gradient; stepping of
     cosmo/newton/pm.py), same particle file, mesh, cloud and step.
T1c  mixed radix, 48 x 80 x 112 cells: acceleration of 2000 massive particles after one
     step of 1e-6 against the numpy scheme on the same mesh, both symbols.
Writes DIR/t1_fft.json and DIR/t1_fft.{png,pdf}.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, os.path.join(ROOT, "cosmo", "newton"))
sys.path.insert(0, os.path.join(ROOT, "cosmo", "ic"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import cosmo_id as cid  # noqa: E402
import pm  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402


class PMSpectral(pm.PM):
    """pm.PM with the gather of the code and the Poisson symbol of the Fourier solver."""
    symbol = "spectral"

    def fields(self):
        rho = cid.cic_deposit(self.x, self.m, self.n, self.L, self.shape)
        self.delta = rho/self.mean - 1.0
        self.phi = nw.scheme_fields(self.delta, self.L, four_pi_g=1.0, symbol=self.symbol)
        self.g = nw.gather_gradient(self.phi, self.x, self.L)[1]


def snapshots(rundir):
    out = []
    for f in sorted(glob.glob(os.path.join(rundir, "*.part.*.bin"))):
        t, cyc, x, u, m, tag = nw.read_snapshot(f)
        xo, uo = np.empty_like(x), np.empty_like(u)
        xo[tag], uo[tag] = x, u
        out.append((t, xo, uo))
    return out


def wrapdiff(a, b, L):
    d = a - b
    return d - L*np.round(d/L)


def cic_general(x, m, nn, box):
    """Cloud-in-cell density on a mesh of nn cells in a periodic box of sides box."""
    h = box/np.array(nn)
    xi = x/h[None, :] - 0.5
    i0 = np.floor(xi).astype(np.int64)
    s = xi - i0
    rho = np.zeros(nn)
    for a in (0, 1):
        wx = s[:, 0] if a else 1.0 - s[:, 0]
        ix = (i0[:, 0] + a) % nn[0]
        for b in (0, 1):
            wy = s[:, 1] if b else 1.0 - s[:, 1]
            iy = (i0[:, 1] + b) % nn[1]
            for c in (0, 1):
                wz = s[:, 2] if c else 1.0 - s[:, 2]
                iz = (i0[:, 2] + c) % nn[2]
                np.add.at(rho, (ix, iy, iz), m*wx*wy*wz)
    return rho/np.prod(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    R = a.run
    res = {}
    L, dt, hub = 4.0, 0.005, 1.0

    # ---- T1a
    sm, s7 = snapshots(os.path.join(R, "mg")), snapshots(os.path.join(R, "fft7"))
    dx7 = [float(np.abs(wrapdiff(p[1], q[1], L)).max()/L) for p, q in zip(sm, s7)]
    du7 = [float(np.abs(p[2] - q[2]).max()/max(np.abs(p[2]).max(), 1e-300))
           for p, q in zip(sm, s7)]
    hm = nw.read_newton_hst(os.path.join(R, "mg", "newton.newton.hst"))
    h7 = nw.read_newton_hst(os.path.join(R, "fft7", "newton.newton.hst"))
    hs = nw.read_newton_hst(os.path.join(R, "fftsp", "newton.newton.hst"))

    def rdiff(key):
        sc = np.max(np.abs(hm[key]))
        return float(np.max(np.abs(hm[key] - h7[key]))/sc)

    res["T1a"] = dict(times=[p[0] for p in sm], dx_over_L=dx7, du_rel=du7,
                      dx_max=max(dx7), du_max=max(du7),
                      K_rel=rdiff("K"), W_rel=rdiff("W"), Phi_min_rel=rdiff("Phi_min"),
                      Phi_max_rel=rdiff("Phi_max"),
                      mg_cycles_mean=float(np.mean(hm["mg_cycles"][1:])),
                      mg_defect_max=float(np.max(hm["mg_defect"])),
                      fft_cycles_max=float(np.max(h7["mg_cycles"])),
                      spectral_vs_seven_point_W_rel=float(
                          np.max(np.abs(hs["W"] - h7["W"]))/np.max(np.abs(h7["W"]))))

    # ---- T1b
    ss = snapshots(os.path.join(R, "fftsp"))
    x0, p0, m, _ = nio.read_nrp(os.path.join(R, "ic", "wave32.nrp"))
    steps = [int(round(p[0]/dt)) for p in ss]
    out = {}
    for sym in ("spectral", "seven_point"):
        PMSpectral.symbol = sym
        sim = PMSpectral(x0, p0, m, 32, L, H0=hub, shape="cic")
        xs, ps, done = [], [], 0
        for s in steps:
            for _ in range(s - done):
                sim.step(dt)
            done = s
            xs.append(sim.x.copy())
            ps.append(sim.p.copy())
        out[sym] = (xs, ps)
    dxs = [float(np.abs(wrapdiff(p[1], q, L)).max()/L) for p, q in zip(ss, out["spectral"][0])]
    dus = [float(np.abs(p[2] - q).max()/max(np.abs(q).max(), 1e-300))
           for p, q in zip(ss, out["spectral"][1])]
    dx7n = [float(np.abs(wrapdiff(p[1], q, L)).max()/L)
            for p, q in zip(s7, out["seven_point"][0])]
    dxmn = [float(np.abs(wrapdiff(p[1], q, L)).max()/L)
            for p, q in zip(sm, out["seven_point"][0])]
    dsp7 = [float(np.abs(wrapdiff(p[1], q[1], L)).max()/L) for p, q in zip(ss, s7)]
    res["T1b"] = dict(times=[p[0] for p in ss], dx_over_L=dxs, du_rel=dus, dx_max=max(dxs),
                      du_max=max(dus), fft7_vs_numpy_dx_max=max(dx7n),
                      mg_vs_numpy_dx_max=max(dxmn), spectral_vs_seven_point_dx=dsp7)

    # ---- T1c
    xr, _, mr, _ = nio.read_nrp(os.path.join(R, "ic", "random.nrp"))
    nn, box = (48, 80, 112), np.array([3.0, 5.0, 7.0])
    rho = cic_general(xr, mr, nn, box)
    res["T1c"] = {}
    for case, sym in (("mixed_sp", "spectral"), ("mixed_7", "seven_point")):
        snap = snapshots(os.path.join(R, case))
        t1, _, u1 = snap[-1]
        acc = u1/t1                               # momentum after one step over the step
        phi = nw.scheme_fields(rho, box, four_pi_g=4.0*np.pi, symbol=sym)
        g = -nw.gather_gradient(phi, xr, box)[1]
        amax = np.abs(g).max()
        res["T1c"][sym] = dict(step=float(t1), acc_max=float(amax),
                               rel_diff_max=float(np.abs(acc - g).max()/amax),
                               rel_diff_rms=float(np.sqrt(np.mean((acc - g)**2))/amax))
    with open(os.path.join(a.out, "t1_fft.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if not isinstance(vv, list)}
                      for k, v in res.items()}, indent=1))

    # ---- figure
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.42)
    aa = nw.scale_factor(np.array(res["T1a"]["times"]), hub)
    floor = 1e-17
    ax = axs[0]
    ax.semilogy(aa, np.maximum(dx7, floor), "o-", ms=3, color=fs.PAL["red"],
                label="seven_point $-$ multigrid")
    ax.semilogy(aa, np.maximum(dxs, floor), "s-", ms=3, color=fs.PAL["blue"],
                label="spectral $-$ numpy scheme")
    ax.semilogy(aa, np.maximum(dx7n, floor), "^--", ms=3, color=fs.PAL["green"],
                label="seven_point $-$ numpy scheme")
    ax.semilogy(aa, np.maximum(dsp7, floor), "d:", ms=3, color=fs.PAL["yellow"],
                label="spectral $-$ seven_point")
    ax.axvline(4.0, color="0.5", alpha=0.4, lw=1.0)
    ax.set_xlabel(r"$a$", labelpad=-1)
    ax.set_ylabel(r"max $|\Delta x|/L$")
    ax.set_ylim(1e-17, 1e-1)
    ax.legend(loc="center right", fontsize=7)
    ax = axs[1]
    for key, col, lab in (("K", fs.PAL["red"], "K"), ("W", fs.PAL["blue"], "W"),
                          ("Phi_min", fs.PAL["green"], r"$\Phi_{\min}$")):
        d = np.abs(hm[key] - h7[key])/np.max(np.abs(hm[key]))
        ax.semilogy(hm["a"], np.maximum(d, floor), color=col, label=lab)
    ax.axvline(4.0, color="0.5", alpha=0.4, lw=1.0)
    ax.set_xlabel(r"$a$", labelpad=-1)
    ax.set_ylabel("seven_point $-$ multigrid, relative")
    ax.set_ylim(1e-17, 1e-8)
    ax.legend(loc="upper left", fontsize=8)
    ax = axs[2]
    for case, sym, col in (("mixed_sp", "spectral", fs.PAL["blue"]),
                           ("mixed_7", "seven_point", fs.PAL["red"])):
        snap = snapshots(os.path.join(R, case))
        acc = snap[-1][2]/snap[-1][0]
        phi = nw.scheme_fields(rho, box, four_pi_g=4.0*np.pi, symbol=sym)
        g = -nw.gather_gradient(phi, xr, box)[1]
        d = np.sqrt(((acc - g)**2).sum(axis=1))/np.abs(g).max()
        ax.semilogy(np.sqrt((g*g).sum(axis=1)), np.maximum(d, floor), ".", ms=2, color=col,
                    label=sym, rasterized=True)
    ax.set_xlabel(r"$|g|$ (numpy scheme)", labelpad=-1)
    ax.set_ylabel(r"$|g_{\rm code} - g_{\rm numpy}|/\max|g|$")
    ax.set_ylim(1e-17, 1e-8)
    ax.legend(loc="upper left", fontsize=8, markerscale=4)
    fs.save(fig, os.path.join(a.out, "t1_fft"))


if __name__ == "__main__":
    main()
