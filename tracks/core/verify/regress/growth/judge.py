#!/usr/bin/env python3
"""Judge regression L (linear growth, amplitude 1e-4, 32^3) of run <run_id> against linear
theory and the earlier run runs/cosmo/east_d1e-4_n32_cpu.

Observable (cosmo/analysis/delta_obs.py, imported here): observer density contrast at the
overdensity peak and at the underdensity, delta_obs = (E/rho_0) a_p^3 - 1 with
a_p = (1 + 3 H_0 tau/2)^(2/3), tau integrated from the recorded probe lapse; linear
theory +-3 delta [a_p + 3 (H_0/k)^2 a_p^(-3/2)] times the probe window at 32 cells.
Earlier result (cosmo/TESTLOG.md lines 118-127 and 163-172): within 0.5 percent of linear
theory at both probes up to a_p = 30; code constraint norms at t = 0 of order 1e-9.
Tolerances: criteria.json, key "L".

    python3 judge.py <run_id>
    python3 judge.py --measure <dir> [--ap-max 30]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

sys.path.insert(0, str(lib.WT / "cosmo" / "analysis"))
sys.path.insert(0, str(lib.WT / "python"))
import delta_obs as dob  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

OLD = lib.OLD_RUNS / "cosmo" / "east_d1e-4_n32_cpu"
DELTA, N = 1e-4, 32


def measure(d, ap_max=30.0, t_max=None):
    d = Path(d)
    g, h = dob.gr_probes(str(d))
    z = np.loadtxt(d / "east.z4c.user.hst", ndmin=2)
    m = dict(t_last=float(g["t"][-1]))
    for i, sign in ((0, 1.0), (1, -1.0)):
        ap = g[f"a_p_{i}"]
        sel = ap <= ap_max
        if t_max is not None:
            sel &= g["t"] <= t_max + 1e-9
        r = g[f"delta_obs_{i}"][sel] / dob.linear(ap[sel], DELTA, sign, n=N)
        m[f"probe{i}_a_p_last"] = float(ap[sel][-1])
        m[f"probe{i}_max_abs_ratio_minus_1"] = float(np.max(np.abs(r - 1.0)))
        m[f"probe{i}_ratio_range"] = [float(r.min()), float(r.max())]
        j = int(np.argmin(np.abs(ap - 30.0)))
        m[f"probe{i}_ratio_at_ap30"] = float(g[f"delta_obs_{i}"][j] / dob.linear(ap[j], DELTA, sign, n=N))
    m.update(H_norm_t0=float(np.sqrt(z[0, 3])), M_norm_t0=float(np.sqrt(z[0, 4])),
             H_norm_max=float(np.sqrt(z[:, 3].max())), np_min=int(h["np"].min()),
             push_unconverged_total=int(np.sum(h["push_unconverged"])))
    return m, g, z


def judge(run_id):
    crit = lib.load_criteria()["L"]
    out = lib.SCRATCH / run_id
    info = lib.athena_log_info(out)
    new, gn, zn = measure(out, crit["ap_max"])
    old, go, zo = measure(OLD, crit["ap_max"], t_max=new["t_last"])
    checks = [lib.verdict_line("run ended on its time limit (1 = yes)", int(info.get("ok", False)),
                               lo=1, fmt="{:d}"),
              lib.verdict_line("last record time", new["t_last"], lo=crit["t_end"] - 0.01)]
    diffs = {}
    for i, sign in ((0, 1.0), (1, -1.0)):
        checks.append(lib.verdict_line(f"probe {i}: max |delta_obs/linear - 1| to a_p = {crit['ap_max']:g}",
                                       new[f"probe{i}_max_abs_ratio_minus_1"],
                                       hi=crit["linear_rel_tol"]))
        # against the earlier run at the same coordinate times
        tn = gn["t"]
        sel = tn <= min(tn[-1], go["t"][-1])
        do = np.interp(tn[sel], go["t"], go[f"delta_obs_{i}"])
        lin = dob.linear(gn[f"a_p_{i}"][sel], DELTA, sign, n=N)
        dd = float(np.max(np.abs(gn[f"delta_obs_{i}"][sel] - do) / np.abs(lin)))
        diffs[i] = dd
        checks.append(lib.verdict_line(f"probe {i}: max |delta_obs - earlier| / |linear|", dd,
                                       hi=crit["earlier_rel_tol"]))
    checks += [
        lib.verdict_line("Hamiltonian-constraint norm at t = 0", new["H_norm_t0"],
                         hi=crit["factor_vs_earlier"] * old["H_norm_t0"]),
        lib.verdict_line("momentum-constraint norm at t = 0", new["M_norm_t0"],
                         hi=crit["factor_vs_earlier"] * old["M_norm_t0"]),
        lib.verdict_line("particles kept (min)", new["np_min"], lo=32768, hi=32768, fmt="{:d}"),
        lib.verdict_line("unconverged pusher steps", new["push_unconverged_total"], hi=0, fmt="{:d}"),
    ]
    ok = all(c["ok"] for c in checks)
    wall = info.get("wall_time_s")
    summary = dict(run_id=run_id, test="L", passed=ok, n_checks=len(checks),
                   n_failed=sum(not c["ok"] for c in checks), new=new, earlier=old,
                   diff_vs_earlier=diffs, log=info, checks=checks)
    (out / "judge.json").write_text(json.dumps(summary, indent=1) + "\n")
    for c in checks:
        print(c["line"])
    print(f"L {'PASSED' if ok else 'FAILED'}: {summary['n_failed']} of {len(checks)} checks failed")
    figure(run_id, gn, go, crit["ap_max"])
    lib.write_manifest(run_id, status="finished" if info.get("ok") else "failed",
                       wall_time_s=wall, slurm_job=info.get("slurm_job"),
                       resources=dict(device="A100 card", cores=1,
                                      card_hours=round(wall / 3600.0, 4) if wall else None),
                       verdict=dict(passed=ok, n_checks=len(checks), n_failed=summary["n_failed"],
                                    judge=str(out / "judge.json")))
    return 0 if ok else 1


def figure(run_id, gn, go, ap_max):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, wspace=0.28, hspace=0.06)
    names = ("overdensity", "underdensity")
    for i, sign in ((0, 1.0), (1, -1.0)):
        ap = gn[f"a_p_{i}"]
        apo = go[f"a_p_{i}"]
        so = apo <= ap[-1] * 1.001
        ax = axs[0, i]
        ax.loglog(apo[so], np.abs(go[f"delta_obs_{i}"][so]), color=fs.PAL["blue"], label="earlier")
        ax.loglog(ap, np.abs(gn[f"delta_obs_{i}"]), color=fs.PAL["red"], ls="--", label="this run")
        ax.loglog(ap, np.abs(dob.linear(ap, DELTA, sign, n=N)), label="linear theory", **fs.GUIDE)
        ax.set_ylabel(r"$|\delta_{\rm obs}|$, " + names[i])
        ax.legend(loc="upper left")
        ax = axs[1, i]
        ax.semilogx(apo[so], go[f"delta_obs_{i}"][so] / dob.linear(apo[so], DELTA, sign, n=N) - 1.0,
                    color=fs.PAL["blue"])
        ax.semilogx(ap, gn[f"delta_obs_{i}"] / dob.linear(ap, DELTA, sign, n=N) - 1.0,
                    color=fs.PAL["red"], ls="--")
        ax.axhspan(-0.005, 0.005, color="grey", alpha=0.15, lw=0)
        ax.axhline(0.0, **fs.THIN)
        ax.set_ylim(-0.02, 0.02)
        ax.set_ylabel(r"$\delta_{\rm obs}/\delta_{\rm lin}-1$")
        ax.set_xlabel(r"$a_p$", labelpad=-2)
    fs.save(fig, str(lib.FIGS / f"regress_growth_{run_id}"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id", nargs="?")
    ap.add_argument("--measure")
    ap.add_argument("--ap-max", type=float, default=30.0)
    ap.add_argument("--t-max", type=float)
    a = ap.parse_args()
    if a.measure:
        print(json.dumps(measure(a.measure, a.ap_max, a.t_max)[0], indent=1))
        sys.exit(0)
    sys.exit(judge(a.run_id))
