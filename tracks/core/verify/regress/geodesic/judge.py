#!/usr/bin/env python3
"""Judge regression G (Kerr geodesic passage) of run <run_id>.

Earlier result: problems/kerr/results/kerr_summary.json (written by
analysis/geodesic/analyze_kerr.py from runs/geodesic/kerr_passage*, docs/TESTLOG.md
"Pusher kernels"); published values: refs/arxiv_2611.12831/src/main.tex lines 824-833.
Tolerances: criteria.json, key "G".

    python3 judge.py <run_id> [--old]     # --old: judge the earlier runs themselves

Writes scratch/core/<run_id>/judge.json, the figure tracks/core/verify/figs/
regress_geodesic_<run_id>.{pdf,png}, and the verdict into the manifest.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

sys.path.insert(0, str(lib.WT / "analysis" / "geodesic"))
sys.path.insert(0, str(lib.WT / "python"))
import geo_common as gc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

A = 0.9
SUMMARY = lib.WT / "problems" / "kerr" / "results" / "kerr_summary.json"


def analyse(d, meta, fin):
    tr = gc.read_traj(d)
    inv = gc.invariant_errors(meta["system"], tr["x"], tr["u"], A)
    efin, _ = gc.final_position_error(meta["system"], tr, fin, A)
    r = gc.radius(meta["system"], tr["x"], A)
    tp, rp = gc.local_extrema(tr["t"], r, "min")
    k = int(np.argmin(rp))
    h = gc.hist_summary(d)
    return dict(max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
                final_pos_err=efin, r_peri=float(rp[k]), t_peri=float(tp[k]),
                t_last=float(tr["t"][-1]), n_records=len(tr["t"]),
                n_unconverged_steps=h["n_unconverged_steps"]), tr, inv


def rel(a, b):
    if b == 0.0:
        return abs(a)
    return abs(a / b - 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    a = ap.parse_args()
    crit = lib.load_criteria()["G"]
    old = json.loads(SUMMARY.read_text())
    oldruns = old["C"]["runs"]
    kr = gc.kerr_ref()
    fin = np.array(kr["ks_passage"]["final_state"]["ks"]["x"])
    out = lib.SCRATCH / a.run_id
    res, checks, hist = {}, [], {}
    for d in sorted(p for p in out.iterdir() if (p / "run.json").exists()):
        rj = json.loads((d / "run.json").read_text())
        name = rj["name"]
        new, tr, inv = analyse(d, rj["meta"], fin)
        ref = oldruns[f"kerr_passage/{name}"]
        res[name] = dict(new=new, old={k: ref[k] for k in ("max_dE", "max_dLz", "max_dQ",
                                                          "final_pos_err", "r_peri", "t_peri")})
        hist[name] = (tr, inv)
        for q in ("max_dE", "max_dLz", "max_dQ", "final_pos_err"):
            if ref[q] == 0.0:
                checks.append(lib.verdict_line(f"{name} {q} (earlier exactly 0)", new[q],
                                               hi=crit["abs_tol_when_zero"]))
            else:
                checks.append(lib.verdict_line(f"{name} {q} / earlier - 1", rel(new[q], ref[q]),
                                               hi=crit["rel_tol_vs_earlier"]))
        checks.append(lib.verdict_line(f"{name} r_peri - earlier", abs(new["r_peri"] - ref["r_peri"]),
                                       hi=crit["r_peri_abs_tol"]))
        checks.append(lib.verdict_line(f"{name} unconverged pusher steps", new["n_unconverged_steps"],
                                       hi=0, fmt="{:d}"))
        checks.append(lib.verdict_line(f"{name} last record time", new["t_last"],
                                       lo=229.999, hi=230.001))
    # published values (main.tex 824-833), two significant digits
    for key, pub in crit["published"].items():
        if key not in res:
            continue
        for q, v in zip(("max_dE", "max_dLz", "max_dQ"), pub):
            if v is None:
                continue
            checks.append(lib.verdict_line(f"{key} {q} / published - 1", rel(res[key]["new"][q], v),
                                           hi=crit["rel_tol_vs_published"]))
    # order in dt, analytic metric
    orders = {}
    for p in ("mid", "bsym", "bchol"):
        names = [f"{p}_ks_dt{dt}" for dt in ("0.005", "0.01", "0.02")]
        if not all(n in res for n in names):
            continue
        dts = np.array([0.005, 0.01, 0.02])
        err = np.array([res[n]["new"]["final_pos_err"] for n in names])
        pw = gc.pairwise_orders(dts, err)
        orders[p] = pw
        oc = old["C"]["dt_convergence_ks"][p]
        opw = gc.pairwise_orders(np.array(oc["dt"][:3]), np.array(oc["err"][:3]))
        for i, (o_new, o_old) in enumerate(zip(pw, opw)):
            checks.append(lib.verdict_line(f"{p} ks pairwise order {i} - earlier", abs(o_new - o_old),
                                           hi=crit["order_abs_tol"]))
            checks.append(lib.verdict_line(f"{p} ks pairwise order {i}", o_new,
                                           lo=crit["order_range"][0], hi=crit["order_range"][1]))
    # trajectory against the earlier processor runs (same kind of build)
    traj_cmp = {}
    for name in ("mid_ks_dt0.01", "bchol_lat_dt0.01"):
        oldd = lib.OLD_RUNS / "geodesic" / "kerr_passage_cpu" / name
        if name not in res or not (oldd / "geo.traj.bin").exists():
            continue
        to, tn = gc.read_traj(oldd), hist[name][0]
        n = min(len(to["t"]), len(tn["t"]))
        dx = float(np.max(np.abs(to["x"][:n] - tn["x"][:n])))
        du = float(np.max(np.abs(to["u"][:n] - tn["u"][:n])))
        ident = bool(np.array_equal(to["x"][:n], tn["x"][:n]) and np.array_equal(to["u"][:n], tn["u"][:n]))
        traj_cmp[name] = dict(max_abs_dx=dx, max_abs_du=du, bitwise_identical=ident,
                              n_old=len(to["t"]), n_new=len(tn["t"]))
        checks.append(lib.verdict_line(f"{name} max|x_new - x_earlier_cpu|", dx, hi=crit["traj_abs_tol"]))
        checks.append(lib.verdict_line(f"{name} max|u_new - u_earlier_cpu|", du, hi=crit["traj_abs_tol"]))
    ok = all(c["ok"] for c in checks)
    summary = dict(run_id=a.run_id, test="G", passed=ok, n_checks=len(checks),
                   n_failed=sum(not c["ok"] for c in checks), results=res, orders=orders,
                   trajectory_vs_earlier_cpu=traj_cmp, checks=checks)
    (out / "judge.json").write_text(json.dumps(summary, indent=1) + "\n")
    for c in checks:
        print(c["line"])
    print(f"G {'PASSED' if ok else 'FAILED'}: {summary['n_failed']} of {len(checks)} checks failed")
    figure(a.run_id, hist, res, old)
    lib.write_manifest(a.run_id, verdict=dict(passed=ok, n_checks=len(checks),
                                              n_failed=summary["n_failed"],
                                              judge=str(out / "judge.json")))
    return 0 if ok else 1


def figure(run_id, hist, res, old):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, hspace=0.28, wspace=0.27)
    ax = axs[0, 0]
    tr, _ = hist["mid_ks_dt0.01"]
    r = gc.radius("ks", tr["x"], A)
    ax.plot(tr["t"], r, color=fs.PAL["red"], label="this run")
    ax.set_yscale("log")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$r/M$")
    ax.legend(loc="upper center")
    for ax, q, lab in ((axs[0, 1], "dE", r"$|\Delta E/E|$"), (axs[1, 0], "dQ", r"$|\Delta Q/Q|$")):
        for i, name in enumerate(("mid_ks_dt0.01", "bsym_ks_dt0.01", "mid_lat_dt0.01",
                                  "bchol_lat_dt0.01")):
            tr, inv = hist[name]
            ax.plot(tr["t"][::10], np.abs(inv[q][::10]) + 1e-18, color=fs.SERIES[i], lw=1.0,
                    label=name.replace("_dt0.01", ""))
            ax.axhline(res[name]["old"]["max_" + q], color=fs.SERIES[i], lw=1.0, ls="--")
        ax.set_yscale("log")
        ax.set_ylim(1e-12, 3e-4)
        ax.set_xlabel(r"$t/M$")
        ax.set_ylabel(lab)
    axs[0, 1].legend(loc="upper left", ncol=2, fontsize=8)
    ax = axs[1, 1]
    for i, p in enumerate(("mid", "bsym", "bchol")):
        dts = [0.005, 0.01, 0.02]
        e = [res[f"{p}_ks_dt{dt:g}"]["new"]["final_pos_err"] for dt in dts]
        oc = old["C"]["dt_convergence_ks"][p]
        ax.plot(oc["dt"], oc["err"], "o", mfc="none", color=fs.SERIES[i], ms=7)
        ax.plot(dts, e, "x-", color=fs.SERIES[i], label=p)
    dd = np.array([0.004, 0.1])
    ax.plot(dd, 4.487e-4 * (dd / 0.01) ** 2, **fs.GUIDE, label=r"$\propto\Delta t^2$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$\Delta t/M$")
    ax.set_ylabel("final position error")
    ax.legend(loc="upper left")
    fs.save(fig, str(lib.FIGS / f"regress_geodesic_{run_id}"))


if __name__ == "__main__":
    sys.exit(main())
