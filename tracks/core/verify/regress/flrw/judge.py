#!/usr/bin/env python3
"""Judge regression F (homogeneous universe) of run <run_id> against the exact solution
and the earlier run runs/cosmo/flrw_n32_cpu_sd.

Exact solution (cosmo/TESTLOG.md, C0; cosmo/README.md "Units and gauge"): conformal time
t, a = (1 + t/2)^2, lapse alpha = a, energy density rho_0 a^-3 with rho_0 = 3/(8 pi),
K = -3 H_0 a^(-3/2), proper volume L^3 a^3 = 64 a^3, proper time of a comoving observer
(2/3) (a^(3/2) - 1). Earlier result (cosmo/TESTLOG.md lines 65-72): lapse 1.9e-7,
density 1.1e-6, K 3.8e-7, volume 1.1e-6, history column H-norm2 below 3.7e-10, Theta below
1.1e-11, probe proper time 1.7e-5. Tolerances: criteria.json, key "F".

    python3 judge.py <run_id>
    python3 judge.py --measure <dir>
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

sys.path.insert(0, str(lib.WT / "cosmo" / "ic"))
sys.path.insert(0, str(lib.WT / "python"))
from nrp_io import read_history  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

OLD = lib.OLD_RUNS / "cosmo" / "flrw_n32_cpu_sd"
RHO0 = 3.0 / (8.0 * np.pi)
QUANTS = ("lapse", "density", "mean_K", "proper_volume", "tau_probe")


def exact(t):
    a = (1.0 + 0.5 * t) ** 2
    return dict(a=a, lapse=a, density=RHO0 / a ** 3, mean_K=-3.0 * a ** -1.5,
                proper_volume=64.0 * a ** 3, tau_probe=(2.0 / 3.0) * (a ** 1.5 - 1.0))


def measure(d):
    d = Path(d)
    h = read_history(d / "flrw.nrpic.hst")
    z = np.loadtxt(d / "flrw.z4c.user.hst", ndmin=2)
    t = h["time"]
    ex = exact(t)
    got = dict(lapse=h["alpha_probe"], density=h["E_probe"], mean_K=h["mean_K"],
               proper_volume=h["proper_volume"], tau_probe=h["tau_probe"])
    err = {}
    for q in QUANTS:
        if q == "tau_probe":
            s = t > 0
            err[q] = np.abs(got[q][s] / ex[q][s] - 1.0)
        else:
            err[q] = np.abs(got[q] / ex[q] - 1.0)
    m = {f"max_rel_err_{q}": float(err[q].max()) for q in QUANTS}
    # the largest proper-time error sits at the first record (trapezoidal first step,
    # relative error dt^2 a''/(12 a) = 4.07e-5 at dt = 1/32); the end value shows the order
    m["rel_err_tau_probe_end"] = float(err["tau_probe"][-1])
    m.update(t_last=float(t[-1]), a_last=float(ex["a"][-1]),
             np_min=int(h["np"].min()), np_max=int(h["np"].max()),
             max_density_spread=float(np.max(h["E_max"] / h["E_min"] - 1.0)),
             max_H_norm2=float(z[:, 3].max()), max_theta=float(np.abs(z[:, 9]).max()),
             max_deposit_identity=float(np.max(np.abs(h["int_E"] / h["sum_mW"] - 1.0))))
    return m, h, z, err


def judge(run_id):
    crit = lib.load_criteria()["F"]
    out = lib.SCRATCH / run_id
    info = lib.athena_log_info(out)
    new, hn, zn, en = measure(out)
    old, ho, zo, eo = measure(OLD)
    checks = [lib.verdict_line("run ended on its time limit (1 = yes)", int(info.get("ok", False)),
                               lo=1, fmt="{:d}"),
              lib.verdict_line("last record time", new["t_last"], lo=1.999, hi=2.001)]
    fac, floor = crit["factor_vs_earlier"], crit["floor"]
    for q in QUANTS:
        k = f"max_rel_err_{q}"
        hi = max(fac * old[k], floor)
        if q == "tau_probe":
            hi = crit["tau_probe_max"]
        checks.append(lib.verdict_line(f"{k}", new[k], hi=hi))
    checks.append(lib.verdict_line("rel_err_tau_probe_end (t = 2)", new["rel_err_tau_probe_end"],
                                   hi=crit["tau_probe_end_max"]))
    checks += [
        lib.verdict_line("max H-norm2 (history column)", new["max_H_norm2"],
                         hi=max(fac * old["max_H_norm2"], floor)),
        lib.verdict_line("max |Theta|", new["max_theta"], hi=max(fac * old["max_theta"], floor)),
        lib.verdict_line("particles kept (min)", new["np_min"], lo=32768, hi=32768, fmt="{:d}"),
        lib.verdict_line("density spread max E_max/E_min - 1", new["max_density_spread"],
                         hi=crit["density_spread_max"]),
        lib.verdict_line("deposition identity max |int E / sum m W - 1|", new["max_deposit_identity"],
                         hi=crit["deposit_identity_tol"]),
    ]
    ok = all(c["ok"] for c in checks)
    wall = info.get("wall_time_s")
    summary = dict(run_id=run_id, test="F", passed=ok, n_checks=len(checks),
                   n_failed=sum(not c["ok"] for c in checks), new=new, earlier=old, log=info,
                   checks=checks)
    (out / "judge.json").write_text(json.dumps(summary, indent=1) + "\n")
    for c in checks:
        print(c["line"])
    print(f"F {'PASSED' if ok else 'FAILED'}: {summary['n_failed']} of {len(checks)} checks failed")
    figure(run_id, hn, ho, en, eo, zn, zo)
    lib.write_manifest(run_id, status="finished" if info.get("ok") else "failed",
                       wall_time_s=wall, slurm_job=info.get("slurm_job"),
                       resources=dict(device="A100 card", cores=1,
                                      card_hours=round(wall / 3600.0, 4) if wall else None),
                       verdict=dict(passed=ok, n_checks=len(checks), n_failed=summary["n_failed"],
                                    judge=str(out / "judge.json")))
    return 0 if ok else 1


def figure(run_id, hn, ho, en, eo, zn, zo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.96, wspace=0.28)
    ax = axs[0]
    labels = dict(lapse=r"$\alpha$", density=r"$E$", mean_K=r"$\langle K\rangle$",
                  proper_volume="volume", tau_probe=r"$\tau$")
    for i, q in enumerate(QUANTS):
        tn = hn["time"] if q != "tau_probe" else hn["time"][hn["time"] > 0]
        to = ho["time"] if q != "tau_probe" else ho["time"][ho["time"] > 0]
        c = fs.SERIES[i]
        ax.plot(tn, en[q] + 1e-17, color=c, label=labels[q])
        ax.plot(to, eo[q] + 1e-17, color=c, ls=":", lw=1.0)
    ax.set_yscale("log")
    ax.set_ylim(1e-12, 1e-3)
    ax.set_xlabel(r"conformal time $t\,H_0$")
    ax.set_ylabel("relative error against exact")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax = axs[1]
    ax.plot(zn[:, 0], np.sqrt(np.maximum(zn[:, 3], 1e-40)), color=fs.PAL["red"], label=r"$\|\mathcal{H}\|$, this run")
    ax.plot(zo[:, 0], np.sqrt(np.maximum(zo[:, 3], 1e-40)), color=fs.PAL["blue"], ls=":", label="earlier")
    ax.plot(zn[:, 0], np.abs(zn[:, 9]) + 1e-20, color=fs.PAL["yellow"], label=r"$|\Theta|$, this run")
    ax.plot(zo[:, 0], np.abs(zo[:, 9]) + 1e-20, color=fs.PAL["green"], ls=":", label="earlier")
    ax.set_yscale("log")
    ax.set_xlabel(r"conformal time $t\,H_0$")
    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, str(lib.FIGS / f"regress_flrw_{run_id}"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id", nargs="?")
    ap.add_argument("--measure")
    a = ap.parse_args()
    if a.measure:
        print(json.dumps(measure(a.measure)[0], indent=1))
        sys.exit(0)
    sys.exit(judge(a.run_id))
