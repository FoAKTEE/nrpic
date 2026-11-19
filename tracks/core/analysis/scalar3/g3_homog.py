#!/usr/bin/env python3
"""Test G3 of tracks/core/JOURNAL-scalar3.md: a homogeneous slow-roll universe under
four lapse conditions, at the step of the 32^3 stochastic runs.

    python3 g3_homog.py --exe EXE --exe-gauge EXE_OF_CORE_GAUGE [--out DIR]
                        [--analyse-only --data DIR]

  geo    geodesic slicing, to t = 8.44 (8 e-folds)
  conf   lapse_harmonic = 1/3 (conformal time), to t = 0.999 or until the run fails
  log    lapse_oplog = 2 (1+log), to t = 0.75 or until the run fails
  leak   lapse_oplog = 2, lapse_leak = 10 on the executable of branch core/gauge, to
         t = 4.7 (8 e-folds at a lapse of 1.8)
A run that ends with a non-zero exit status or with non-finite numbers is a result
here, not an error.  Compares <phi>, <Pi>, <K> of <basename>.sf.hst as functions of the
proper time of the mean lapse with the Friedmann solution (nrpic.scalar_field.
ms_reference without modes), and <K>, <Pi> and the e-folds as functions of the field
value (independent of the time coordinate).  Writes DIR/summary.json and DIR/fig_gauge_homog.png."""
import argparse
import os
import subprocess

import s3
from s3 import common, np, sf

INP = os.path.join(s3.HERE, "inputs", "flrw_gauge.athinput")
SPEC = {
    "geo": (False, ["time/tlim=8.44"]),
    "conf": (False, ["z4c/lapse_harmonic=0.3333333333333333", "time/tlim=0.999"]),
    "log": (False, ["z4c/lapse_oplog=2.0", "time/tlim=0.75"]),
    "leak": (True, ["z4c/lapse_oplog=2.0", "z4c/lapse_leak=10.0", "time/tlim=4.7"]),
}


def run(exe, rundir, args):
    os.makedirs(rundir, exist_ok=True)
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-i", INP] + args + ["-d", rundir], cwd=rundir,
                           stdout=log, stderr=subprocess.STDOUT,
                           env=dict(os.environ, OMP_NUM_THREADS="1"))
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--exe-gauge", required=True)
    ap.add_argument("--out")
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--data", help="with --analyse-only: directory of the runs of an "
                    "earlier execution")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    data = os.path.abspath(a.data) if a.data else out
    summ = dict(exe=os.path.abspath(a.exe), exe_gauge=os.path.abspath(a.exe_gauge),
                runs={})
    case = s3.case("sr", 1)
    v, dv, phi0, pi0 = s3.inf.code_background(case)
    res = {}
    for k, (gauge_exe, args) in SPEC.items():
        rd = os.path.join(data, k)
        code = None
        if not a.analyse_only:
            code = run(os.path.abspath(a.exe_gauge if gauge_exe else a.exe), rd, args)
        h = sf.read_history(os.path.join(rd, "hg.sf.hst"))
        ok = np.isfinite(h["phi"]) & np.isfinite(h["K"]) & np.isfinite(h["alpha"]) \
            & np.isfinite(h["chi"]) & (h["chi"] > 0.0)
        nok = int(np.argmin(ok)) if not ok.all() else ok.size
        t, al = h["time"][:nok], h["alpha"][:nok]
        # proper time of the mean lapse (trapezoid rule on the record of every step;
        # the lapse is smooth, so the rule is accurate to (dt)^2 d2alpha/dt2)
        tau = np.concatenate([[0.0], np.cumsum(0.5*(al[1:] + al[:-1])*np.diff(t))])
        nef = -0.5*np.log(h["chi"][:nok])
        ref = sf.ms_reference(v, dv, phi0, pi0, [1], [0j], [0j], s3.LENGTH,
                              np.maximum(tau, 0.0))
        r = dict(exit=code, steps=int(h["time"].size - 1), finite_steps=nok - 1,
                 t_end=float(t[-1]), tau_end=float(tau[-1]), efolds_end=float(nef[-1]),
                 alpha_end=float(al[-1]), alpha_max=float(al.max()))
        for q, key in (("phi", "phi"), ("Pi", "Pi"), ("K", "K")):
            refq = ref[q] if q != "K" else -3.0*ref["H"]
            err = np.abs(h[key][:nok]/refq - 1.0)
            r["err_" + q] = float(err.max())
            r["err_" + q + "_first_half"] = float(err[:max(nok//2, 1)].max())
        r["err_efolds"] = float(np.abs(nef - ref["ln_a"]).max())
        # independent of the time coordinate: K, Pi and the e-folds as functions of the
        # field value (phi rises monotonically), against the Friedmann solution on a
        # fine grid.  The comparison at equal proper time above is limited by the
        # trapezoid rule for int <alpha> dt when the lapse changes within a few steps.
        fine = sf.ms_reference(v, dv, phi0, pi0, [1], [0j], [0j], s3.LENGTH,
                               np.linspace(0.0, 9.5, 19001))
        ph = h["phi"][:nok]
        inr = ph <= fine["phi"][-1]
        r["err_K_at_phi"] = float(np.abs(
            h["K"][:nok][inr]/(-3.0*np.interp(ph[inr], fine["phi"], fine["H"])) - 1.0
        ).max())
        r["err_Pi_at_phi"] = float(np.abs(
            h["Pi"][:nok][inr]/np.interp(ph[inr], fine["phi"], fine["Pi"]) - 1.0).max())
        r["err_efolds_at_phi"] = float(np.abs(
            nef[inr] - np.interp(ph[inr], fine["phi"], fine["ln_a"])).max())
        half = inr & (np.arange(nok) <= nok//2)
        r["err_efolds_at_phi_first_half"] = float(np.abs(
            nef[half] - np.interp(ph[half], fine["phi"], fine["ln_a"])).max())
        # step in e-folds of the last finite step
        r["H_alpha_dt_end"] = float(ref["H"][-1]*al[-1]*(t[-1] - t[-2])) if nok > 1 else 0
        if k == "leak":
            # settled lapse against exp(6 H T) with the Friedmann H at the same proper
            # time, T = 0.1
            eq = np.exp(6.0*ref["H"]*0.1)
            late = tau > 1.0
            r["alpha_over_eq_max_dev_late"] = float(np.abs(al[late]/eq[late] - 1.0).max())
            r["alpha_eq_first"] = float(eq[0])
        if k == "log":
            # 1 + 6 N
            r["alpha_over_1p6N_max_dev"] = float(
                np.abs(al/(1.0 + 6.0*ref["ln_a"]) - 1.0)[nef < 3.0].max())
        if k == "conf":
            r["alpha_over_a_max_dev"] = float(
                np.abs(al*np.sqrt(h["chi"][:nok]) - 1.0)[nef < 3.0].max())
        summ["runs"][k] = r
        res[k] = dict(tau=tau, nef=nef, al=al, ref=ref, h=h, nok=nok)
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.95, wspace=0.33)
    cols = dict(geo=fs.PAL["blue"], conf=fs.PAL["orange"], log=fs.PAL["green"],
                leak=fs.PAL["red"])
    labs = dict(geo="geodesic", conf="conformal time", log="1+log",
                leak="1+log, relaxed")
    for k, r in res.items():
        ax[0].plot(r["nef"], r["al"], color=cols[k], label=labs[k])
        hd = r["ref"]["H"]*r["al"]*np.gradient(r["h"]["time"][:r["nok"]])
        ax[1].plot(r["nef"], hd, color=cols[k])
        err = np.abs(r["h"]["Pi"][:r["nok"]]/r["ref"]["Pi"] - 1.0)
        ax[2].plot(r["nef"][1:], np.maximum(err[1:], 1e-16), color=cols[k])
    ax[0].set_yscale("log")
    ax[0].set_xlabel("e-folds")
    ax[0].set_ylabel(r"mean lapse $\langle\alpha\rangle$")
    ax[0].legend(loc="upper left", fontsize=7)
    ax[1].set_yscale("log")
    ax[1].axhline(2.785/2.0, **fs.MASK_LINE)
    ax[1].set_xlabel("e-folds")
    ax[1].set_ylabel(r"step in e-folds, $H\langle\alpha\rangle\Delta t$")
    ax[2].set_yscale("log")
    ax[2].set_xlabel("e-folds")
    ax[2].set_ylabel(r"$|\langle\Pi\rangle/\Pi_{\rm F}(\tau)-1|$")
    fig.savefig(os.path.join(out, "fig_gauge_homog.png"), dpi=200)
    print("G3 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
