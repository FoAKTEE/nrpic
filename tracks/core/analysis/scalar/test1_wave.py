#!/usr/bin/env python3
"""Test 1 of the scalar field: Klein-Gordon plane wave of a test field on flat spacetime
(JOURNAL-scalar.md, prediction P1).

  a  dispersion relation and spatial order: meshes N x N x 8, nghost 2, 3, 4, step 1/512
  b  temporal order: N = 16, nghost 4, Courant factors 0.4, 0.2, 0.1, 0.05
  c  Kreiss-Oliger dissipation 0.5, N = 16
  d  potentials: homogeneous field on flat spacetime against ddot phi = -V'(phi)

Usage: test1_wave.py --exe ATHENA [--parts abcd] [--workers 12]   (run in the output
directory; writes summary.json and the figures fig_wave_*.png)
"""
import argparse
import glob
import json
import os

import numpy as np

import common
from common import PROB, mesh_args, run_many
from nrpic import scalar_field as sfr

INP = os.path.join(PROB, "kg_wave.athinput")
MASS, NW = 5.0, (1, 1, 0)
KVEC = 2.0*np.pi*np.array(NW, dtype=float)


def omega_h(n, ng):
    """Frequency of the semi-discrete plane wave on a mesh of spacing 1/n."""
    h = 1.0/n
    return np.sqrt(MASS**2 + sum(sfr.d2_symbol(k*h, ng) for k in KVEC)/h**2)


def mode_amplitude(dump):
    """Complex amplitude a + i b of phi = a cos(k.x) + b sin(k.x) on the mesh."""
    phi = dump["fields"]["phi"]
    n1, n2, n3 = phi.shape
    x = (np.arange(n1) + 0.5)/n1
    y = (np.arange(n2) + 0.5)/n2
    ph = KVEC[0]*x[:, None, None] + KVEC[1]*y[None, :, None] + 0.0*np.zeros(n3)[None, None, :]
    return 2.0*np.mean(phi*np.exp(1j*ph))


def phase_series(rundir):
    t, c = [], []
    for f in sorted(glob.glob(os.path.join(rundir, "kg.sf.*.dump"))):
        d = sfr.read_dump(f)
        t.append(d["time"])
        c.append(mode_amplitude(d))
    t, c = np.array(t), np.array(c)
    return t, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--parts", default="abcd")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--reuse", default=None,
                    help="analyse the case directories of an earlier run instead of running")
    args = ap.parse_args()
    out = os.getcwd()
    top = os.path.abspath(args.reuse) if args.reuse else out

    def run_or_reuse(cases, workers):
        if args.reuse:
            return [0.0]*len(cases)
        return run_many(args.exe, cases, workers)
    summary = {"exe": os.path.abspath(args.exe)}
    omega = np.sqrt(MASS**2 + KVEC @ KVEC)

    # ---------------------------------------------------------------- a: dispersion
    if "a" in args.parts:
        ns, ngs, dt = [8, 12, 16, 24], [2, 3, 4], 1.0/512.0
        cases = []
        for ng in ngs:
            for n in ns:
                cases.append((os.path.join(top, f"a_ng{ng}_n{n}"), INP,
                              mesh_args(n, n, 8) + [f"mesh/nghost={ng}",
                                                    f"time/cfl_number={dt*n}",
                                                    "time/tlim=1.0",
                                                    "scalar_field/dump_dt=0.125"]))
        wall = run_or_reuse(cases, args.workers)
        res = {}
        from scipy.optimize import least_squares
        for (rd, _, _), w in zip(cases, wall):
            t, c = phase_series(rd)
            ph = np.unwrap(np.angle(c))
            om_phase = np.polyfit(t, ph, 1)[0]
            # The data phi = cos(k.x), Pi = omega sin(k.x) with the continuum omega are a
            # travelling wave plus a small standing wave on the mesh: the amplitude is
            # cos(Omega t) + i r sin(Omega t), r = omega/Omega.  A straight line through
            # the phase is biased by the standing part; fit Omega and r instead.
            fit = least_squares(
                lambda p: np.concatenate([c.real - np.cos(p[0]*t),
                                          c.imag - p[1]*np.sin(p[0]*t)]),
                [om_phase, 1.0], xtol=1e-15, ftol=1e-15, gtol=1e-15)
            om = fit.x[0]
            name = os.path.basename(rd)
            ng, n = int(name.split("_")[1][2:]), int(name.split("_")[2][1:])
            res[name] = dict(ng=ng, n=n, omega_meas=om, omega_phase_fit=om_phase,
                             ratio_fit=fit.x[1], fit_residual=float(np.abs(fit.fun).max()),
                             omega_h=omega_h(n, ng), omega=omega, amp_end=abs(c[-1]),
                             wall_s=w)
        orders = {}
        for ng in ngs:
            hh = np.array([1.0/n for n in ns])
            err = np.array([abs(res[f"a_ng{ng}_n{n}"]["omega_meas"] - omega) for n in ns])
            orders[ng] = float(np.polyfit(np.log(hh), np.log(err), 1)[0])
        summary["a"] = dict(cases=res, spatial_order=orders, dt=dt,
                            temporal_bound=3.0*omega*(omega*dt)**4/120.0)

    # ------------------------------------------------------------------ b: temporal
    if "b" in args.parts:
        cfls, n, ng = [0.4, 0.2, 0.1, 0.05], 16, 4
        cases = [(os.path.join(top, f"b_cfl{c}"), INP,
                  mesh_args(n, n, 8) + [f"time/cfl_number={c}", "time/tlim=1.0",
                                        "scalar_field/dump_dt=1.0"]) for c in cfls]
        wall = run_or_reuse(cases, args.workers)
        oh = omega_h(n, ng)
        res = {}
        for (rd, _, _), w, c in zip(cases, wall, cfls):
            d = sfr.read_dump(sorted(glob.glob(os.path.join(rd, "kg.sf.*.dump")))[-1])
            phi = d["fields"]["phi"]
            x = (np.arange(n) + 0.5)/n
            ph = KVEC[0]*x[:, None, None] + KVEC[1]*x[None, :, None] + np.zeros(8)[None, None, :]
            t = d["time"]
            # exact solution of the semi-discrete equations for the initial data
            # phi = cos(k.x), Pi = omega sin(k.x)
            ex = np.cos(ph)*np.cos(oh*t) + (omega/oh)*np.sin(ph)*np.sin(oh*t)
            # amplitude loss of the integrator alone (no dissipation): the travelling
            # part exp(i omega_h t) of the amplitude, against (omega_h dt)^6/144 per step
            amp = mode_amplitude(d)
            trav = abs(amp.real + 1j*amp.imag*oh/omega)
            res[str(c)] = dict(cfl=c, dt=c/n, time=t, err_l2=float(np.sqrt(np.mean((phi - ex)**2))),
                               amp_loss=float(1.0 - trav),
                               amp_loss_rk4=float((oh*c/n)**6/144.0*t/(c/n)), wall_s=w)
        e = np.array([res[str(c)]["err_l2"] for c in cfls])
        summary["b"] = dict(cases=res, omega_h=oh,
                            order=float(np.polyfit(np.log(cfls), np.log(e), 1)[0]),
                            order_pairs=[float(np.log2(e[i]/e[i+1])) for i in range(3)],
                            classical_rk4_estimate=[float(omega*1.0*(omega*c/n)**4/120.0/np.sqrt(2.0))
                                                    for c in cfls])

    # --------------------------------------------------------------- c: dissipation
    if "c" in args.parts:
        n, ng, diss = 16, 4, 0.5
        rd = os.path.join(top, "c_diss")
        wall = run_or_reuse([(rd, INP, mesh_args(n, n, 8) + [
            "time/tlim=2.0", f"scalar_field/diss={diss}", "scalar_field/dump_dt=0.125"])], 1)
        t, c = phase_series(rd)
        oh = omega_h(n, ng)
        trav = np.abs(c.real + 1j*c.imag*oh/omega)     # travelling part of the amplitude
        rate = -np.polyfit(t, np.log(trav), 1)[0]
        pred = sum(sfr.diss_rate(k/n, 1.0/n, diss, ng) for k in KVEC)
        dtc = 0.25/n
        rk = (oh*dtc)**6/144.0/dtc                     # amplitude loss of RK4 per time
        summary["c"] = dict(rate_meas=float(rate), rate_pred=float(pred),
                            ratio=float(rate/pred), rate_rk4=float(rk),
                            ratio_with_rk4=float(rate/(pred + rk)), wall_s=wall[0],
                            t=t.tolist(), amp=trav.tolist())

    # ---------------------------------------------------------------- d: potentials
    if "d" in args.parts:
        tab = os.path.join(out, "quartic_table.txt")
        vq, dvq = sfr.potential("quartic", mass=1.0, lam=3.0)
        xs = np.linspace(-2.0, 2.0, 2001)
        np.savetxt(tab, np.column_stack([xs, vq(xs), dvq(xs)]), fmt="%.17e",
                   header="phi V dV/dphi: quartic, mass 1, lambda 3")
        pots = {
            "quadratic": (["scalar_field/potential=quadratic", "scalar_field/mass=2.0"],
                          sfr.potential("quadratic", mass=2.0)),
            "quartic": (["scalar_field/potential=quartic", "scalar_field/mass=1.0",
                         "scalar_field/lambda=3.0"], (vq, dvq)),
            "plateau": (["scalar_field/potential=plateau", "scalar_field/v0=2.0",
                         "scalar_field/mu=1.5"], sfr.potential("plateau", v0=2.0, mu=1.5)),
            "inflection": (["scalar_field/potential=inflection", "scalar_field/lambda=5.0",
                            "scalar_field/vev=1.0"],
                           sfr.potential("inflection", lam=5.0, vev=1.0)),
            "table": (["scalar_field/potential=table", f"scalar_field/table_file={tab}"],
                      (vq, dvq)),
        }
        cases, keys = [], []
        for name, (pa, _) in pots.items():
            for cfl in (0.25, 0.125):
                keys.append((name, cfl))
                cases.append((os.path.join(top, f"d_{name}_cfl{cfl}"), INP,
                              mesh_args(8, 8, 8) + pa + [
                                  "problem/amp=0.0", "problem/phi0=1.0", "problem/pi0=0.3",
                                  f"time/cfl_number={cfl}", "time/tlim=10.0",
                                  "scalar_field/dump_dt=-1.0"]))
        wall = run_or_reuse(cases, args.workers)
        res = {}
        for (name, cfl), (rd, _, _), w in zip(keys, cases, wall):
            h = sfr.read_history(os.path.join(rd, "kg.sf.hst"))
            phi, pi = sfr.flat_oscillator(pots[name][1][1], 1.0, 0.3, h["time"][1:])
            scale = np.max(np.abs(phi))
            res[f"{name}_{cfl}"] = dict(
                potential=name, cfl=cfl,
                max_err_phi=float(np.max(np.abs(h["phi"][1:] - phi))/scale),
                max_err_pi=float(np.max(np.abs(h["Pi"][1:] - pi))/np.max(np.abs(pi))),
                rms_inhomog=float(np.max(h["rms_phi"])), wall_s=w)
        # table against the analytic quartic it tabulates, same step
        ht = sfr.read_history(os.path.join(top, "d_table_cfl0.25", "kg.sf.hst"))
        hq = sfr.read_history(os.path.join(top, "d_quartic_cfl0.25", "kg.sf.hst"))
        summary["d"] = dict(cases=res,
                            table_minus_quartic=float(np.max(np.abs(ht["phi"] - hq["phi"]))),
                            order={n: float(np.log2(res[f"{n}_0.25"]["max_err_phi"]
                                                    / res[f"{n}_0.125"]["max_err_phi"]))
                                   for n in pots})

    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    figures(out, summary)


def figures(top, s):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    from nrpic import figstyle as fs
    fs.use_style()
    if "a" in s and "b" in s:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
        fig.subplots_adjust(left=0.11, right=0.98, bottom=0.15, top=0.95, wspace=0.36)
        cols = {2: fs.PAL["yellow"], 3: fs.PAL["blue"], 4: fs.PAL["red"]}
        for ng in (2, 3, 4):
            cs = [c for c in s["a"]["cases"].values() if c["ng"] == ng]
            n = np.array([c["n"] for c in cs])
            e = np.array([abs(c["omega_meas"] - c["omega"])/c["omega"] for c in cs])
            eh = np.array([abs(c["omega_h"] - c["omega"])/c["omega"] for c in cs])
            ax[0].loglog(n, e, "o", color=cols[ng], ms=5,
                         label=f"order {2*ng-2}: fit {s['a']['spatial_order'][ng]:.2f}")
            ax[0].loglog(n, eh, **fs.GUIDE)
        ax[0].set_xlabel("cells per box side N")
        ax[0].set_ylabel(r"$|\omega_{\rm measured}-\omega|/\omega$")
        ax[0].set_xticks([8, 12, 16, 24])
        ax[0].set_xticks([], minor=True)
        ax[0].set_xticklabels(["8", "12", "16", "24"])
        ax[0].legend(loc="lower left")
        b = s["b"]["cases"]
        dt = np.array([c["dt"] for c in b.values()])
        e = np.array([c["err_l2"] for c in b.values()])
        ax[1].loglog(dt, e, "o", color=fs.PAL["red"], ms=5,
                     label=f"code, fitted order {s['b']['order']:.2f}")
        ax[1].loglog(dt, e[0]*(dt/dt[0])**4, **fs.GUIDE, label=r"$\propto \Delta t^4$")
        ax[1].set_xlabel(r"time step $\Delta t$")
        ax[1].set_ylabel(r"rms error of $\phi$")
        ax[1].set_xticks([3e-3, 1e-2, 3e-2])
        ax[1].set_xticklabels(["0.003", "0.01", "0.03"])
        ax[1].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax[1].legend(loc="upper left")
        fs.save(fig, os.path.join(top, "fig_wave_convergence"))
        plt.close(fig)
    if "c" in s and "d" in s:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
        fig.subplots_adjust(left=0.11, right=0.98, bottom=0.15, top=0.95, wspace=0.36)
        t, a = np.array(s["c"]["t"]), np.array(s["c"]["amp"])
        ax[0].semilogy(t, a, "o", color=fs.PAL["red"], ms=4, label="code, dissipation 0.5")
        ax[0].semilogy(t, np.exp(-(s["c"]["rate_pred"] + s["c"]["rate_rk4"])*t), **fs.GUIDE,
                       label="stencil and integrator")
        ax[0].semilogy(t, np.exp(-s["c"]["rate_pred"]*t), color="k", lw=1.0, ls=":",
                       label="stencil alone")
        ax[0].set_xlabel("time")
        ax[0].set_ylabel("amplitude")
        ax[0].set_yscale("linear")
        ax[0].ticklabel_format(axis="y", useOffset=False)
        ax[0].legend(loc="lower left")
        names = ["quadratic", "quartic", "plateau", "inflection", "table"]
        x = np.arange(len(names))
        e1 = [s["d"]["cases"][f"{n}_0.25"]["max_err_phi"] for n in names]
        e2 = [s["d"]["cases"][f"{n}_0.125"]["max_err_phi"] for n in names]
        ax[1].semilogy(x, e1, "o", color=fs.PAL["red"], ms=5, label="Courant 0.25")
        ax[1].semilogy(x, e2, "s", color=fs.PAL["blue"], ms=5, label="Courant 0.125")
        ax[1].set_xticks(x)
        ax[1].set_xticks([], minor=True)
        ax[1].set_xticklabels(names, fontsize=8)
        ax[1].set_ylabel(r"max $|\phi-\phi_{\rm ODE}|$ / max $|\phi|$")
        ax[1].legend(loc="upper right")
        fs.save(fig, os.path.join(top, "fig_wave_diss_potentials"))
        plt.close(fig)


if __name__ == "__main__":
    main()
