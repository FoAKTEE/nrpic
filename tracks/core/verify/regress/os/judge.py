#!/usr/bin/env python3
"""Judge regression O (Oppenheimer-Snyder collapse) of run <run_id> against the earlier
run runs/os/nocap_sc and the published order of the horizon-mass error.

Earlier result: docs/TESTLOG.md "Dust collapse with corrected initial data, cloud at the
finest level" (first horizon 16.39 M, mass 1.00035; 1.0003, 1.0001, 1.0000 at 18, 20,
22 M); paper/sections/tables/tab_outcomes.tex (tab:outcomes_dust). Published:
Delta M / M_ADM <~ 1e-3 (refs/arxiv_2611.12831/src/main.tex line 945).
Tolerances: criteria.json, key "O".

    python3 judge.py <run_id>
    python3 judge.py --measure <dir>      # print the measured quantities of any run dir
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

OLD = lib.OLD_RUNS / "os" / "nocap_sc"


def read_horizon(d):
    a = np.loadtxt(Path(d) / "os.horizon_summary_0.txt", comments="#", ndmin=2)
    t, m = a[:, 1], a[:, 2]
    # de-duplicate (restarts) by time, keep the last
    _, idx = np.unique(t[::-1], return_index=True)
    idx = len(t) - 1 - idx
    t, m = t[idx], m[idx]
    return t, m


def read_z4c(d):
    z = np.loadtxt(Path(d) / "os.z4c.user.hst", ndmin=2)
    return dict(t=z[:, 0], H=np.sqrt(np.maximum(z[:, 3], 0.0)), Volume=z[:, 10])


def measure(d, t_end=None):
    d = Path(d)
    h = read_history(d / "os.nrpic.hst")
    th, mh = read_horizon(d)
    z = read_z4c(d)
    if t_end is not None:
        sel = th <= t_end + 1e-9
        th, mh = th[sel], mh[sel]
        zs = z["t"] <= t_end + 1e-9
        z = {k: v[zs] for k, v in z.items()}
        hs = h["time"] <= t_end + 1e-9
        h = {k: v[hs] for k, v in h.items()}
    found = np.isfinite(mh)
    t_found, m_found = th[found], mh[found]
    alive = h["np"] > 0
    ident = np.abs(h["int_E"][alive] / h["sum_mW"][alive] - 1.0)
    i_empty = np.where(h["np"] == 0)[0]
    win = (t_found >= 18.0) & (t_found <= 25.0 + 1e-9)
    win22 = (t_found >= 18.0) & (t_found <= 22.0 + 1e-9)
    near = lambda tq: float(m_found[np.argmin(np.abs(t_found - tq))]) if len(t_found) else np.nan
    return dict(
        t_last=float(h["time"][-1]),
        t_first_ah=float(t_found[0]) if len(t_found) else None,
        m_first_ah=float(m_found[0]) if len(t_found) else None,
        m_at={f"{tq:g}": near(tq) for tq in (18.0, 20.0, 22.0, 25.0)},
        max_abs_m_minus_1=float(np.max(np.abs(m_found - 1.0))) if len(t_found) else None,
        median_m_18_25=float(np.median(m_found[win])) if win.any() else None,
        median_m_18_22=float(np.median(m_found[win22])) if win22.any() else None,
        n_searches_found=int(found.sum()),
        t_all_removed=float(h["time"][i_empty[0]]) if len(i_empty) else None,
        n_particles_start=int(h["np"][0]),
        max_deposit_identity=float(ident.max()) if ident.size else None,
        push_unconverged_total=int(np.sum(h["push_unconverged"])),
        max_H=float(z["H"].max()), t_max_H=float(z["t"][np.argmax(z["H"])]),
        H_end=float(z["H"][-1]),
        min_alpha_probe=float(h["alpha_probe"].min()),
    ), h, (th, mh), z


def lapse_difference(hn, ho, t_max):
    """max |alpha_probe(new) - alpha_probe(old)| on the records of the new run up to t_max
    (old interpolated; both histories are written every cycle)."""
    sel = hn["time"] <= t_max
    ao = np.interp(hn["time"][sel], ho["time"], ho["alpha_probe"])
    return float(np.max(np.abs(hn["alpha_probe"][sel] - ao)))


def judge(run_id):
    crit = lib.load_criteria()["O"]
    out = lib.SCRATCH / run_id
    info = lib.athena_log_info(out)
    new, hn, ahn, zn = measure(out)
    old, ho, aho, zo = measure(OLD, t_end=new["t_last"])
    checks = [lib.verdict_line("run ended on its time limit (1 = yes)", int(info.get("ok", False)),
                               lo=1, fmt="{:d}")]
    checks.append(lib.verdict_line("last record time", new["t_last"], lo=crit["t_end"] - 0.05))
    if new["t_first_ah"] is None:
        checks.append(dict(name="first apparent horizon", ok=False,
                           line="FAIL  no apparent horizon found"))
    else:
        checks += [
            lib.verdict_line("first AH time - earlier", abs(new["t_first_ah"] - old["t_first_ah"]),
                             hi=crit["t_first_ah_abs_tol"]),
            lib.verdict_line("|M_AH(first) - 1|", abs(new["m_first_ah"] - 1.0),
                             hi=crit["published_mass_error"]),
            lib.verdict_line("|M_AH(first) - earlier|", abs(new["m_first_ah"] - old["m_first_ah"]),
                             hi=crit["m_abs_tol_vs_earlier"]),
            lib.verdict_line("max |M_AH - 1| over all searches to t_end", new["max_abs_m_minus_1"],
                             hi=crit["published_mass_error"]),
            lib.verdict_line("|median M_AH(18..25 M) - earlier|",
                             abs(new["median_m_18_25"] - old["median_m_18_25"]),
                             hi=crit["m_abs_tol_vs_earlier"]),
        ]
    tl = new["t_first_ah"] if new["t_first_ah"] is not None else new["t_last"]
    dal = lapse_difference(hn, ho, tl)
    dal_all = lapse_difference(hn, ho, new["t_last"])
    checks += [
        lib.verdict_line("max |alpha_c - earlier| before the first AH", dal,
                         hi=crit["alpha_abs_tol_before_ah"]),
        lib.verdict_line("deposition identity max |int E / sum m W - 1|", new["max_deposit_identity"],
                         hi=crit["deposit_identity_tol"]),
        lib.verdict_line("unconverged pusher steps", new["push_unconverged_total"], hi=0, fmt="{:d}"),
        lib.verdict_line("particles at start", new["n_particles_start"], lo=9328, hi=9328, fmt="{:d}"),
    ]
    if new["t_all_removed"] is not None and old["t_all_removed"] is not None:
        checks.append(lib.verdict_line("time all particles removed - earlier",
                                       abs(new["t_all_removed"] - old["t_all_removed"]),
                                       hi=crit["t_removed_abs_tol"]))
    else:
        checks.append(dict(name="all particles removed", ok=False,
                           line="FAIL  particles left at the end"))
    checks.append(lib.verdict_line("max ||H|| / earlier - 1", abs(new["max_H"] / old["max_H"] - 1.0),
                                   hi=crit["max_H_rel_tol"]))
    ok = all(c["ok"] for c in checks)
    wall = info.get("wall_time_s")
    summary = dict(run_id=run_id, test="O", passed=ok, n_checks=len(checks),
                   n_failed=sum(not c["ok"] for c in checks), new=new, earlier=old,
                   alpha_diff_before_ah=dal, alpha_diff_all=dal_all, log=info, checks=checks)
    (out / "judge.json").write_text(json.dumps(summary, indent=1) + "\n")
    for c in checks:
        print(c["line"])
    print(f"O {'PASSED' if ok else 'FAILED'}: {summary['n_failed']} of {len(checks)} checks failed")
    figure(run_id, hn, ho, ahn, aho, zn, zo)
    lib.write_manifest(run_id, status="finished" if info.get("ok") else "failed",
                       wall_time_s=wall, slurm_job=info.get("slurm_job"),
                       resources=dict(device="A100 card", cores=1,
                                      card_hours=round(wall / 3600.0, 4) if wall else None),
                       verdict=dict(passed=ok, n_checks=len(checks), n_failed=summary["n_failed"],
                                    judge=str(out / "judge.json")))
    return 0 if ok else 1


def figure(run_id, hn, ho, ahn, aho, zn, zo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    tmax = hn["time"][-1]
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, hspace=0.06, wspace=0.28)
    ax = axs[0, 0]
    so = aho[0] <= tmax
    ax.plot(aho[0][so], aho[1][so], color=fs.PAL["blue"], label="earlier (runs/os/nocap_sc)")
    ax.plot(ahn[0], ahn[1], color=fs.PAL["red"], ls="--", label="this run")
    ax.axhspan(1 - 1e-3, 1 + 1e-3, color="grey", alpha=0.15, lw=0)
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_ylim(0.997, 1.003)
    ax.set_ylabel(r"$M_{\rm AH}/M$")
    ax.legend(loc="lower right")
    ax = axs[0, 1]
    so = ho["time"] <= tmax
    ax.plot(ho["time"][so], ho["alpha_probe"][so], color=fs.PAL["blue"])
    ax.plot(hn["time"], hn["alpha_probe"], color=fs.PAL["red"], ls="--")
    ax.set_yscale("log")
    ax.set_ylabel(r"central lapse $\alpha_c$")
    ax = axs[1, 0]
    ao = np.interp(hn["time"], ho["time"], ho["alpha_probe"])
    ax.plot(hn["time"], np.abs(hn["alpha_probe"] - ao) + 1e-17, color=fs.PAL["red"])
    ax.set_yscale("log")
    ax.set_ylabel(r"$|\alpha_c-\alpha_c^{\rm earlier}|$")
    ax.set_xlabel(r"$t/M$", labelpad=-2)
    ax = axs[1, 1]
    sz = zo["t"] <= tmax
    ax.plot(zo["t"][sz], zo["H"][sz], color=fs.PAL["blue"])
    ax.plot(zn["t"], zn["H"], color=fs.PAL["red"], ls="--")
    ax.set_yscale("log")
    ax.set_ylabel(r"$\|\mathcal{H}\|$")
    ax.set_xlabel(r"$t/M$", labelpad=-2)
    ax.set_xlim(0, tmax)
    fs.save(fig, str(lib.FIGS / f"regress_os_{run_id}"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id", nargs="?")
    ap.add_argument("--measure")
    ap.add_argument("--t-end", type=float)
    a = ap.parse_args()
    if a.measure:
        print(json.dumps(measure(a.measure, a.t_end)[0], indent=1))
        sys.exit(0)
    sys.exit(judge(a.run_id))
