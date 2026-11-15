#!/usr/bin/env python3
"""Test 4 of the scalar field: the stochastic sources (JOURNAL-scalar.md, P4).

  A  generic model (power) on a test field in flat spacetime, 32^3: amplitudes and
     synthesized fields against the Python twin, spectrum, independence of the MeshBlock
     layout and of a restart, frozen against white in time, the sources in one step
  B  Mukhanov-Sasaki model on a homogeneous slow-roll background, 16^3: lockstep
     integration against SciPy, fields against the prescription, layout and restart,
     constraints with the two projectors and with the sign of the Pi kick flipped

Usage: test4_noise.py --exe ATHENA [--parts AB]   (run in the output directory)
"""
import argparse
import filecmp
import glob
import json
import os

import numpy as np

import common
from common import PROB, mesh_args, run_many
from nrpic import scalar_field as sfr

INP_A = os.path.join(PROB, "noise_power.athinput")
INP_B = os.path.join(PROB, "noise_ms.athinput")
SEED_A, NMAX2_A, N_A, L_A = 20261115, 100, 32, 1.0
PAR_A = dict(amp=1.0, tilt=0.0, ksigma0=3.0, hubble=2.0)
SEED_B, NMAX2_B, N_B, L_B = 7, 36, 16, 10.0
MASS, PHI0, PI0 = 0.1, 3.0, -0.016286750396764


def same_fields(d1, d2):
    """Names of the fields that differ in any bit between two dumps."""
    return [k for k in d1["names"] if not np.array_equal(d1["fields"][k], d2["fields"][k])]


def shell_stats(c, cref, n2):
    """Per shell: number of modes, mean of |c|^2/|cref|^2 and its deviation from 1 in
    units of 1/sqrt(M) (|alpha|^2 is an exponential deviate)."""
    out = []
    for s in np.unique(n2):
        sel = (n2 == s) & (np.abs(cref) > 0)
        m = int(sel.sum())
        if m == 0:
            continue
        r = float(np.mean(np.abs(c[sel])**2/np.abs(cref[sel])**2))
        out.append((int(s), m, r, (r - 1.0)*np.sqrt(m)))
    return np.array(out)


def part_a(exe, top, workers):
    n, n2 = sfr.mode_set(NMAX2_A)
    dt = 0.25/N_A
    base = ["scalar_field/noise_scheme=frozen"]
    cases = {
        "frozen_b32": mesh_args(32, 32, 32) + base,
        "frozen_b16": mesh_args(32, 32, 32, 16, 16, 16) + base,
        "frozen_b8": mesh_args(32, 32, 32, 8, 8, 8) + base,
        "markov_b16": mesh_args(32, 32, 32, 16, 16, 16) + ["scalar_field/noise_scheme=markov"],
        "markov_b8": mesh_args(32, 32, 32, 8, 8, 8) + ["scalar_field/noise_scheme=markov"],
        "heaviside_b16": mesh_args(32, 32, 32, 16, 16, 16) + [
            "scalar_field/noise_scheme=markov", "scalar_field/noise_window=heaviside"],
        "onestep": mesh_args(32, 32, 32, 16, 16, 16) + base + [
            "time/nlim=1", "scalar_field/dump_dcycle=1", "scalar_field/mass=3.0"],
    }
    lst = [(os.path.join(top, "A_" + k), INP_A, a) for k, a in cases.items()]
    wall = run_many(exe, lst, workers)
    # restarts from cycle 32 of the frozen and the white-in-time runs
    rst = [(os.path.join(top, "A_frozen_b16_restart"),
            os.path.join(top, "A_frozen_b16", "rst", "np.00001.rst"), []),
           (os.path.join(top, "A_markov_b16_restart"),
            os.path.join(top, "A_markov_b16", "rst", "np.00001.rst"), [])]
    wall += run_many(exe, rst, workers)
    res = {"wall_s": wall}

    def dump(case, num):
        return sfr.read_dump(os.path.join(top, "A_" + case, f"np.sf.{num:05d}.dump"))

    # (a) amplitudes and fields against the twin, (b) spectrum
    twin = {}
    for case, scheme, window in (("frozen_b16", "frozen", "tanh"),
                                 ("markov_b16", "markov", "tanh"),
                                 ("heaviside_b16", "markov", "heaviside")):
        for num in (1, 2):
            d = dump(case, num)
            t1 = d["time"]
            g = sfr.power_shell_factor(n2, t1 - dt, t1, L_A, scheme=scheme, window=window,
                                       **PAR_A)
            epoch = 0 if scheme == "frozen" else d["cycle"]
            for f in (0, 1):
                cref = g*sfr.mode_alpha(SEED_A, f, epoch, n)
                fld = d["fields"][f"noise{f}"]
                c, fh = sfr.analyse(fld, n)
                rms = np.sqrt(np.mean(fld**2))
                mask = np.ones(fh.shape, bool)
                mask[n[:, 0] % N_A, n[:, 1] % N_A, n[:, 2] % N_A] = False
                mask[(-n[:, 0]) % N_A, (-n[:, 1]) % N_A, (-n[:, 2]) % N_A] = False
                st = shell_stats(c, cref, n2)
                twin[f"{case}_cycle{d['cycle']}_field{f}"] = dict(
                    rms=float(rms), coef_err_over_rms=float(np.abs(c - cref).max()/rms),
                    outside_ball_over_rms=float(np.abs(fh[mask]).max()/rms),
                    modes_nonzero=int((np.abs(cref) > 0).sum()),
                    shells=int(len(st)),
                    worst_shell_sigma=float(np.abs(st[:, 3]).max()) if len(st) else 0.0,
                    mean_power_ratio=float(np.mean(np.abs(c[np.abs(cref) > 0])**2
                                                   / np.abs(cref[np.abs(cref) > 0])**2)))
    res["twin"] = twin
    # shells of the white-in-time field against the prescription (for the figure): the
    # code's coefficients divided by the shell factor are the alphas
    d = dump("markov_b16", 2)
    g = sfr.power_shell_factor(n2, d["time"] - dt, d["time"], L_A, scheme="markov", **PAR_A)
    c, _ = sfr.analyse(d["fields"]["noise0"], n)
    sel = g > 1e-12*g.max()
    res["shell_table"] = shell_stats(c[sel], g[sel].astype(complex), n2[sel]).tolist()

    # (c) layout and restart
    res["layout"] = {
        "frozen_b32_vs_b16": [same_fields(dump("frozen_b32", k), dump("frozen_b16", k))
                              for k in (1, 2)],
        "frozen_b8_vs_b16": [same_fields(dump("frozen_b8", k), dump("frozen_b16", k))
                             for k in (1, 2)],
        "markov_b8_vs_b16": [same_fields(dump("markov_b8", k), dump("markov_b16", k))
                             for k in (1, 2)]}
    res["restart"] = {
        s: filecmp.cmp(os.path.join(top, f"A_{s}_b16", "np.sf.00002.dump"),
                       os.path.join(top, f"A_{s}_b16_restart", "np.sf.00002.dump"),
                       shallow=False) for s in ("frozen", "markov")}

    # (d) correlation between the increments of two steps (cycles 32 and 64)
    corr = {}
    for case in ("frozen_b16", "markov_b16"):
        c1, _ = sfr.analyse(dump(case, 1)["fields"]["noise0"], n)
        c2, _ = sfr.analyse(dump(case, 2)["fields"]["noise0"], n)
        # modes whose shell factor is appreciable in both steps
        w = np.abs(c1)*np.abs(c2)
        sel = w > 1e-6*w.max()
        a1 = c1[sel]/np.sqrt(np.mean(np.abs(c1[sel])**2))
        a2 = c2[sel]/np.sqrt(np.mean(np.abs(c2[sel])**2))
        corr[case] = dict(modes=int(sel.sum()),
                          corr=float(np.real(np.mean(a1*np.conj(a2)))),
                          band=float(4.0/np.sqrt(sel.sum())))
    res["correlation"] = corr

    # one step with the sources: exact response of the Runge-Kutta polynomial per mode,
    # (1 + dt A/2 + (dt A)^2/6 + (dt A)^3/24)(c_phi xi0, c_pi xi1), A = ((0, 1), (-w2, 0))
    d = dump("onestep", 1)
    h = L_A/N_A
    w2 = 3.0**2 + sum(sfr.d2_symbol(2.0*np.pi*n[:, i]/N_A, 4) for i in range(3))/h**2
    x0, _ = sfr.analyse(d["fields"]["noise0"], n)
    x1, _ = sfr.analyse(d["fields"]["noise1"], n)
    e0, e1 = 1.0*x0, 0.5*x1
    z = w2*dt*dt
    phi_ref = e0*(1.0 - z/6.0) + e1*dt*(0.5 - z/24.0)
    pi_ref = e1*(1.0 - z/6.0) - e0*w2*dt*(0.5 - z/24.0)
    cp, _ = sfr.analyse(d["fields"]["phi"], n)
    cq, _ = sfr.analyse(d["fields"]["Pi"], n)
    res["onestep"] = dict(phi_err=float(np.abs(cp - phi_ref).max()/np.abs(phi_ref).max()),
                          pi_err=float(np.abs(cq - pi_ref).max()/np.abs(pi_ref).max()),
                          naive_phi_err=float(np.abs(cp - e0).max()/np.abs(e0).max()))
    return res


def part_b(exe, top, workers):
    n, n2 = sfr.mode_set(NMAX2_B)
    shells = np.unique(n2)
    q = np.sqrt(shells.astype(float))
    v, dv = sfr.potential("quadratic", mass=MASS)
    h0 = np.sqrt((8.0*np.pi/3.0)*(0.5*PI0**2 + v(PHI0)))
    amp = 3.0e-4
    r0 = amp*q**-1.5*(1.0 + 0.5j)
    dr0 = amp*q**-1.5*h0*(-0.3 + 0.2j*q)
    mfile = os.path.join(top, "modes.txt")
    np.savetxt(mfile, np.column_stack([shells, r0.real, r0.imag, dr0.real, dr0.imag]),
               fmt=["%d"] + ["%.17e"]*4, header="n2 Re_R Im_R Re_dR Im_dR at t = 0")
    com = [f"scalar_field/noise_mode_file={mfile}"]
    cases = {
        "cfl0.25": com,
        "cfl0.125": com + ["time/cfl_number=0.125", "output1/dcycle=26"],
        "cfl0.0625": com + ["time/cfl_number=0.0625", "output1/dcycle=52"],
        "b16": com + mesh_args(16, 16, 16),
        "continuum": com + ["scalar_field/noise_projector=continuum"],
        "flip": com + ["scalar_field/noise_pi_sign=-1.0"],
        "level1": com + ["scalar_field/noise_level=1"],
        "nonoise": ["scalar_field/noise=none"],
        # twice the amplitude: second-order constraint violations grow fourfold
    }
    m2 = os.path.join(top, "modes2.txt")
    np.savetxt(m2, np.column_stack([shells, 2*r0.real, 2*r0.imag, 2*dr0.real, 2*dr0.imag]),
               fmt=["%d"] + ["%.17e"]*4, header="n2 Re_R Im_R Re_dR Im_dR at t = 0")
    cases["double"] = [f"scalar_field/noise_mode_file={m2}"]
    cases["double_continuum"] = [f"scalar_field/noise_mode_file={m2}",
                                 "scalar_field/noise_projector=continuum"]
    cases["double_flip"] = [f"scalar_field/noise_mode_file={m2}",
                            "scalar_field/noise_pi_sign=-1.0"]
    lst = [(os.path.join(top, "B_" + k), INP_B, a) for k, a in cases.items()]
    wall = run_many(exe, lst, workers)
    wall += run_many(exe, [(os.path.join(top, "B_cfl0.25_restart"),
                            os.path.join(top, "B_cfl0.25", "rst", "ms.00001.rst"), [])], 1)
    res = {"wall_s": wall, "H0": h0}

    def last(case):
        f = sorted(glob.glob(os.path.join(top, "B_" + case, "ms.sf.*.dump")))[-1]
        return sfr.read_dump(f), sfr.read_modes(f.replace(".dump", ".modes"))

    # (e) lockstep integration against SciPy at the time of the last dump
    lock = {}
    for case in ("cfl0.25", "cfl0.125", "cfl0.0625"):
        d, (head, rows) = last(case)
        ref = sfr.ms_reference(v, dv, PHI0, PI0, shells, r0, dr0, L_B, [d["time"]])
        rc = rows[:, 1] + 1j*rows[:, 2]
        dc = rows[:, 3] + 1j*rows[:, 4]
        sc = rows[:, 5] + 1j*rows[:, 6]
        lock[case] = dict(
            time=d["time"], cycle=d["cycle"],
            R_err=float(np.max(np.abs(rc - ref["R"][0])/np.abs(ref["R"][0]))),
            dR_err=float(np.max(np.abs(dc - ref["dR"][0])/np.abs(ref["dR"][0]))),
            shell_err=float(np.max(np.abs(sc - ref["shell"][0]))/np.max(np.abs(ref["shell"][0]))),
            phi_b_err=float(abs(head["phi_b"]/ref["phi"][0] - 1.0)),
            ln_a_err=float(abs(head["ln_a"] - ref["ln_a"][0])),
            mesh_phi_minus_lockstep=float(abs(np.mean(d["fields"]["phi"]) - head["phi_b"])),
            mesh_lna_minus_lockstep=float(abs(-0.5*np.log(np.mean(d["fields"]["chi"]))
                                              - head["ln_a"])))
    res["lockstep"] = lock
    res["lockstep_order"] = {
        k: [float(np.log2(lock["cfl0.25"][k]/lock["cfl0.125"][k])),
            float(np.log2(lock["cfl0.125"][k]/lock["cfl0.0625"][k]))]
        for k in ("R_err", "dR_err", "shell_err", "phi_b_err", "ln_a_err")}

    # (a) fields against the shell factors of the record, the twin amplitudes and the
    # projector of the stencil
    d, (head, rows) = last("cfl0.25")
    alpha = sfr.mode_alpha(SEED_B, 0, 0, n)
    smap = {int(s): rows[i, 5] + 1j*rows[i, 6] for i, s in enumerate(rows[:, 0])}
    sh = np.array([smap[int(s)] for s in n2])
    qh = np.stack([sfr.d1_symbol(2.0*np.pi*n[:, i]/N_B, 4) for i in range(3)], axis=1)
    q2 = (qh**2).sum(axis=1)
    pr = [np.ones(len(n)), qh[:, 0]**2/q2, qh[:, 0]*qh[:, 1]/q2, qh[:, 0]*qh[:, 2]/q2,
          qh[:, 1]**2/q2, qh[:, 1]*qh[:, 2]/q2]
    fld = {}
    for f in range(6):
        cref = sh*alpha*pr[f]
        c, fh = sfr.analyse(d["fields"][f"noise{f}"], n)
        rms = np.sqrt(np.mean(d["fields"]["noise0"]**2))
        fld[f"field{f}"] = float(np.abs(c - cref).max()/rms)
    res["fields_vs_prescription"] = fld
    res["noise_rms"] = float(np.sqrt(np.mean(d["fields"]["noise0"]**2)))
    st = shell_stats(analyse0(d, n), sh.astype(complex), n2)
    res["shell_table"] = st.tolist()

    # (c) layout and restart
    d1, _ = last("b16")
    res["layout_b16_vs_b8"] = same_fields(d1, d)
    res["restart_identical"] = bool(filecmp.cmp(
        sorted(glob.glob(os.path.join(top, "B_cfl0.25", "ms.sf.*.dump")))[-1],
        sorted(glob.glob(os.path.join(top, "B_cfl0.25_restart", "ms.sf.*.dump")))[-1],
        shallow=False))

    # (f) constraints
    con = {}
    for case in ("nonoise", "cfl0.25", "continuum", "flip", "level1", "double",
                 "double_continuum", "double_flip"):
        hst = sfr.read_history(os.path.join(top, "B_" + case, "ms.sf.hst"))
        con[case] = dict(H_rel_max=float((hst["H_rms"]/hst["H_norm"]).max()),
                         M_rms_max=float(hst["M_rms"].max()),
                         H_rms_max=float(hst["H_rms"].max()),
                         rms_phi_max=float(hst["rms_phi"].max()),
                         t=hst["time"].tolist(), H_rms=hst["H_rms"].tolist(),
                         M_rms=hst["M_rms"].tolist(), rms_phi=hst["rms_phi"].tolist())
    res["constraints"] = con
    return res


def analyse0(d, n):
    c, _ = sfr.analyse(d["fields"]["noise0"], n)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--parts", default="AB")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    top = os.getcwd()
    summary = {"exe": os.path.abspath(args.exe)}
    if "A" in args.parts:
        summary["A"] = part_a(args.exe, top, args.workers)
    if "B" in args.parts:
        summary["B"] = part_b(args.exe, top, args.workers)
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    figures(top, summary)


def figures(top, s):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    if "A" in s:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
        st = np.array(s["A"]["shell_table"])
        q = np.sqrt(st[:, 0])
        ax[0].errorbar(q, st[:, 2], yerr=1.0/np.sqrt(st[:, 1]), fmt="o", ms=3,
                       color=fs.PAL["red"], lw=1.0, label="shell mean of $|\\xi_n|^2$ / prescription")
        ax[0].axhline(1.0, **fs.GUIDE)
        ax[0].set_xlabel("wave number $|n|$")
        ax[0].set_ylabel("measured / prescribed power")
        ax[0].legend(loc="upper right", fontsize=8)
        keys = sorted(s["A"]["twin"])
        e = [s["A"]["twin"][k]["coef_err_over_rms"] for k in keys]
        o = [max(s["A"]["twin"][k]["outside_ball_over_rms"], 1e-20) for k in keys]
        ax[1].semilogy(e, "o", color=fs.PAL["red"], ms=4, label="coefficients: code - twin")
        ax[1].semilogy(o, "s", color=fs.PAL["blue"], ms=4, label="largest coefficient outside the ball")
        ax[1].axhline(1e-12, **fs.GUIDE)
        ax[1].set_ylim(1e-18, 1e-10)
        ax[1].set_xlabel("case (scheme, window, cycle, field)")
        ax[1].set_ylabel("difference / rms of the field")
        ax[1].legend(loc="upper right", fontsize=8)
        fs.save(fig, os.path.join(top, "fig_noise_power"))
        plt.close(fig)
    if "B" in s:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
        fig.subplots_adjust(left=0.10, right=0.98, bottom=0.15, top=0.95, wspace=0.30)
        lk = s["B"]["lockstep"]
        cf = np.array([0.25, 0.125, 0.0625])
        for key, col, lab in (("R_err", fs.PAL["red"], "mode functions $R_q$"),
                              ("shell_err", fs.PAL["blue"], "source factors $S_R$"),
                              ("ln_a_err", fs.PAL["yellow"], "ln a of the background")):
            e = np.array([lk[f"cfl{c}"][key] for c in (0.25, 0.125, 0.0625)])
            ax[0].loglog(cf, e, "o-", color=col, ms=5, label=lab)
        e0 = lk["cfl0.25"]["R_err"]
        ax[0].loglog(cf, e0*(cf/0.25)**4, **fs.GUIDE, label=r"$\propto\Delta t^4$")
        ax[0].set_xlabel("Courant factor")
        ax[0].set_ylabel("relative difference to SciPy")
        ax[0].legend(loc="upper left", fontsize=8)
        con = s["B"]["constraints"]
        for case, col, ls, lab in (("cfl0.25", fs.PAL["red"], "-", "stencil projector"),
                                   ("continuum", fs.PAL["blue"], "-", "continuum projector"),
                                   ("flip", fs.PAL["yellow"], "-", "sign of the $\\Pi$ kick flipped"),
                                   ("nonoise", "k", ":", "no sources")):
            t = np.array(con[case]["t"])
            ax[1].semilogy(t, np.maximum(con[case]["M_rms"], 1e-20), color=col, ls=ls, label=lab)
            ax[1].semilogy(t, np.maximum(con[case]["H_rms"], 1e-20), color=col, ls="--")
        ax[1].set_xlabel("time")
        ax[1].set_ylabel("rms $|M|$ (solid), rms $H$ (dashed)")
        ax[1].legend(loc="lower right", fontsize=7)
        fs.save(fig, os.path.join(top, "fig_noise_ms"))
        plt.close(fig)


if __name__ == "__main__":
    main()
