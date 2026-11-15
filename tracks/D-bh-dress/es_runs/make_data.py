#!/usr/bin/env python3
"""Data sets of the first full-relativity runs of Track D: ES-1 (black hole in a vacuum
bubble inside an expanding dust ball, outer dust edge at 60 M) and its vacuum control V-1
(the same slicing function f(R) around a single Schwarzschild hole, no dust).

    make_data.py [--out DIR] [--hp 1.0] [--tau_max 1500]

DIR defaults to $NRPIC_RUN_DIR (nrpic-run). Writes
    es/   the ES data set from tracks/D-bh-dress/einstein_straus/make_es.py with
          --Rw 40 --w_in 4 --Rb 56 --w_out 4 --R0 4 (dust over 36 < R < 60 M) and the
          figures of make_es redirected into es/figs/ (the package of make_es is not
          written)
    v1/   v1.tab (format 2, same f(R), rho = 0: time-symmetric Schwarzschild below 4 M,
          outgoing Painleve-Gullstrand slice of mass M beyond 36 M), v1.nrp (the same 140
          tracers at the same positions, m = 1e-30, u_i = 0), v1_reference.csv (exact
          areal radius of every tracer group against proper time), v1.json
    predictions.json  numbers used in the predictions of JOURNAL.md: exact crossing
          times of R = 2M, wall radius at given proper times, the homogeneous 1+log model
          of the lapse in the dust plateau against coordinate time
    figs/data_compare.(png,pdf)  u, KL, KT of both tables; the plateau lapse model
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ESDIR = os.path.join(WT, "tracks", "D-bh-dress", "einstein_straus")
sys.path.insert(0, ESDIR)
sys.path.insert(0, os.path.join(WT, "python"))
import es_model as em  # noqa: E402
import make_es as mk  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

GEOM = dict(M=1.0, Rw=40.0, w_in=4.0, Rb=56.0, w_out=4.0, R0=4.0)
TRACER_MASS = 1.0e-30            # as make_es.py: positive, so the code pushes timelike geodesics


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


class VacuumBubble(em.EinsteinStrausBH):
    """Same geometry parameters, rho = 0: the f-slice of one Schwarzschild hole."""

    def __init__(self, **kw):
        super().__init__(matched=False, rho0=0.0, **kw)

    def summary(self):
        return dict(model="vacuum_f_slice", M=self.M, R0=self.R0, R1=self.R1, Rin=self.Rin,
                    Rw=self.Rw, Rb=self.Rb, Rout=self.Rout, rho0=0.0, M_total=self.Mtot,
                    a=self.a, b=self.b, m_p=self.m_p, u0=self.u0, rbar0=self.rbar0,
                    rbar_throat=self.rbar_throat, ts_consistency=self.ts_consistency)


def plateau_lapse_model(H0, t_end=200.0, n=200001):
    """1+log slicing (d_t alpha = -2 alpha K) with zero shift in the homogeneous EdS
    plateau: K = -3H(tau), H = H0/(1 + 1.5 H0 tau), d tau/dt = alpha, hence
    alpha = 1 + 6 ln a(tau), a = (1 + 1.5 H0 tau)^(2/3); integrated in coordinate time."""
    t = np.linspace(0.0, t_end, n)
    dt = t[1] - t[0]
    tau = np.zeros_like(t)

    def rate(s):
        a = (1.0 + 1.5 * H0 * s) ** (2.0 / 3.0)
        return 1.0 + 6.0 * math.log(a)
    for i in range(n - 1):                       # RK4 for d tau/dt = 1 + 6 ln a(tau)
        s = tau[i]
        k1 = rate(s)
        k2 = rate(s + 0.5 * dt * k1)
        k3 = rate(s + 0.5 * dt * k2)
        k4 = rate(s + dt * k3)
        tau[i + 1] = s + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    a = (1.0 + 1.5 * H0 * tau) ** (2.0 / 3.0)
    return t, tau, a, 1.0 + 6.0 * np.log(a)


def crossing(tau, R, level=2.0):
    i = np.where(R <= level)[0]
    if len(i) == 0 or i[0] == 0:
        return None
    k = i[0]
    return float(tau[k - 1] + (level - R[k - 1]) * (tau[k] - tau[k - 1]) / (R[k] - R[k - 1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--hp", type=float, default=1.0)
    ap.add_argument("--tau_max", type=float, default=1500.0)
    a = ap.parse_args()
    if not a.out:
        raise SystemExit("--out or NRPIC_RUN_DIR needed")
    out = a.out
    os.makedirs(out, exist_ok=True)

    # ---- ES data set through make_es.py, figures redirected into the run directory
    esd = os.path.join(out, "es")
    os.makedirs(os.path.join(esd, "figs"), exist_ok=True)
    mk.FIGS = os.path.join(esd, "figs")
    argv = ["make_es.py", "--out", esd, "--hp", repr(a.hp), "--tau_max", repr(a.tau_max)]
    for k in ("M", "Rw", "w_in", "Rb", "w_out", "R0"):
        argv += [f"--{k}", repr(GEOM[k])]
    sys.argv = argv
    print("make_es:", " ".join(argv[1:]), flush=True)
    mk.main()
    with open(os.path.join(esd, "es.json")) as f:
        es = json.load(f)

    # ---- V-1: vacuum table with the same f(R)
    v1d = os.path.join(out, "v1")
    os.makedirs(v1d, exist_ok=True)
    vm = VacuumBubble(**GEOM)
    vs = vm.summary()
    tab = vm.table(drbar=0.02)
    ptab = os.path.join(v1d, "v1.tab")
    hdr = ["vacuum control V-1 of the Einstein-Straus run: the slice KT = -f(R) sqrt(2M/R^3) of one "
           "Schwarzschild hole (f as in the ES data), tracks/D-bh-dress/es_runs/make_data.py",
           "add a puncture component of bare mass m_p at the same centre"]
    hdr += [f"{k} = {(float(v) if isinstance(v, (float, np.floating)) else v)!r}" for k, v in vs.items()]
    em.write_tab2(ptab, tab, header=hdr)
    xt, Rt, rbt, mt, Et, _ = mk.tracers(vm)
    pnrp = os.path.join(v1d, "v1.nrp")
    em.write_nrp(pnrp, xt, np.zeros_like(xt), np.full(len(xt), TRACER_MASS))
    tau = np.linspace(0.0, a.tau_max, 6001)
    cols = mk.reference_curves(vm, Rt, tau)
    pref = os.path.join(v1d, "v1_reference.csv")
    keys = list(cols)
    np.savetxt(pref, np.column_stack([cols[k] for k in keys]), delimiter=",",
               header=",".join(keys), comments="# ", fmt="%.15e")
    # the ES tracers must sit at the same places (same f and m = M inside 36 M; psi = 1 beyond)
    es_rbar = np.array([t["rbar0"] for t in es["tracers"]])
    v1 = dict(summary=vs, table=dict(rows=len(tab.rbar), drbar=tab.dr, rbar_last=float(tab.rbar[-1]),
                                     breaks=tab.breaks, exterior=tab.exterior),
              tracers=[dict(index=i, R0=float(Rt[i]), rbar0=float(rbt[i]), m_enclosed=float(mt[i]),
                            E=float(Et[i]), tags=[14 * i, 14 * i + 13]) for i in range(len(Rt))],
              tracer_rbar_max_diff_to_es=float(np.max(np.abs(rbt - es_rbar))),
              files={os.path.basename(p): sha256(p) for p in (ptab, pnrp, pref)})
    with open(os.path.join(v1d, "v1.json"), "w") as f:
        json.dump(v1, f, indent=1, default=float)

    # ---- numbers for the predictions
    esm = em.EinsteinStrausBH(**GEOM)
    tau_r = np.linspace(0.0, a.tau_max, 150001)
    pred = {"es_summary": es["summary"], "v1_summary": vs, "tracer_rbar_max_diff": v1["tracer_rbar_max_diff_to_es"]}
    Rw = esm.radius(np.full_like(tau_r, esm.Rin), tau_r)
    pred["R_wall"] = {f"tau={T:g}": float(np.interp(T, tau_r, Rw)) for T in (50, 100, 150, 200, 400, 800)}
    pred["R_wall_formula"] = "(36^(3/2) + 1.5 sqrt(2 M) tau)^(2/3), M = 1 (both ES-1 and V-1)"
    cr_es, cr_v1 = {}, {}
    for i, R0 in enumerate(Rt):
        cr_es[f"group{i}_R0={R0:g}"] = crossing(tau_r, esm.radius(np.full_like(tau_r, R0), tau_r))
        cr_v1[f"group{i}_R0={R0:g}"] = crossing(tau_r, vm.radius(np.full_like(tau_r, R0), tau_r))
    pred["tau_reach_2M_es"] = cr_es
    pred["tau_reach_2M_v1"] = cr_v1
    t, tau_p, a_p, alp = plateau_lapse_model(esm.H)
    pred["plateau_1plog_zero_shift"] = {f"t={T:g}": dict(tau=float(np.interp(T, t, tau_p)),
                                                          a=float(np.interp(T, t, a_p)),
                                                          alpha=float(np.interp(T, t, alp)))
                                        for T in (25, 50, 100, 150, 200)}
    pred["plateau_H"] = esm.H
    # initial slope of the 1+log lapse at the probe radius 48 M: -2 K
    p48 = esm.profiles(np.array([48.0]))
    q48 = vm.profiles(np.array([48.0]))
    pred["dalpha_dt_t0_at_48M"] = dict(es=float(-2.0 * (p48["KL"][0] + 2 * p48["KT"][0])),
                                       v1=float(-2.0 * (q48["KL"][0] + 2 * q48["KT"][0])))
    with open(os.path.join(out, "predictions.json"), "w") as f:
        json.dump(pred, f, indent=1, default=float)
    print(json.dumps(pred, indent=1, default=float))

    # ---- figure: the two tables and the plateau lapse model
    fs.use_style()
    import matplotlib.pyplot as plt
    ta, _ = em.read_tab2(os.path.join(esd, "es.tab"))
    tb, _ = em.read_tab2(ptab)
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.97, wspace=0.3, hspace=0.3)
    ax = axs[0, 0]
    ax.plot(ta.rbar, ta.cols["u"], color=fs.PAL["red"], label="ES-1")
    ax.plot(tb.rbar, tb.cols["u"], color=fs.PAL["blue"], ls="--", label="V-1")
    ax.set_xlabel(r"$\bar r/M$")
    ax.set_ylabel(r"$u$ (regular part of $\psi$)")
    ax.set_xlim(0, 70)
    ax.legend(loc="lower right")
    ax = axs[0, 1]
    for t_, c, lab in ((ta, fs.PAL["red"], "ES-1"), (tb, fs.PAL["blue"], "V-1")):
        ax.plot(t_.rbar, t_.cols["KL"], color=c, label=f"{lab} $K_L$")
        ax.plot(t_.rbar, t_.cols["KT"], color=c, ls=":", label=f"{lab} $K_T$")
    ax.set_xlabel(r"$\bar r/M$")
    ax.set_ylabel(r"$K^i{}_j$ eigenvalues ($M^{-1}$)")
    ax.set_xlim(0, 70)
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    ax = axs[1, 0]
    r = np.linspace(0.6, 69.0, 3000)
    pe, pv = esm.profiles(r), vm.profiles(r)
    ax.plot(r, pe["m"], color=fs.PAL["red"], label="ES-1")
    ax.plot(r, pv["m"], color=fs.PAL["blue"], ls="--", label="V-1")
    ax.set_xlabel(r"$\bar r/M$")
    ax.set_ylabel(r"Misner-Sharp mass $m/M$")
    ax.legend(loc="upper left")
    ax = axs[1, 1]
    ax.plot(t, alp, color=fs.PAL["red"], label=r"$\alpha = 1 + 6\ln a$")
    ax.plot(t, tau_p / 100.0, color=fs.PAL["yellow"], label=r"$\tau/100M$")
    ax.plot(t, a_p, color=fs.PAL["green"], label=r"$a$")
    ax.set_xlabel(r"coordinate time $t/M$")
    ax.set_ylabel("plateau, 1+log, zero shift")
    ax.legend(loc="upper left")
    os.makedirs(os.path.join(out, "figs"), exist_ok=True)
    fs.save(fig, os.path.join(out, "figs", "data_compare"))
    print("wrote", out)


if __name__ == "__main__":
    main()
