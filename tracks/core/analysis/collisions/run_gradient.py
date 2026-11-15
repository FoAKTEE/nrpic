#!/usr/bin/env python3
"""G1, G2: one collision step on frozen particles in the static conformal metric with a
gradient (problems/tests/coll_box_static.athinput), for the operator of core-v0.3
(coll_energy = cell) and for the kinematics with the metric at each particle
(coll_energy = particle), against the Monte Carlo reference of the pair model
(gradient_ref.py, scbox.pair_reference), which reads no file of the code.

  run_gradient.py OUT --ref REF.json [--exe ATHENA] [--n 8000000] [--nproc 6]
                  [--cases a,b,...] [--keep-dumps]

Per case and mode: particle file (scbox.make_particles), one step of dt = 1e-6 with a
cross-section that gives a mean pair probability of about 0.08 and one sub-step, dump of
the step. Measured per collision and unit rest mass: the change of the sum of W and of
H = alpha W - beta^x u_x with the metric at each particle, from the history columns
dE_particles, dH_particles and again from the dump (metric at the particles as dumped);
the regression slope of the change of H of a particle on cos(phi) minus its cell mean;
the change of sum M u_i (exact sums). Writes summary.json and fig_gradient.png.

  run_gradient.py OUT --ref REF.json --regrade OLD/summary.json

grades the code numbers of an earlier run (its summary.json) against other reference
files without running the code again (the dumps of that run are gone; the numbers
graded are those analyse() stored).
"""
import argparse
import json
import os
import sys

import numpy as np

import common
import gradient_ref
import scbox
from nrpic import collide

DECK = os.path.join(common.REPO, "problems", "tests", "coll_box_static.athinput")
DT = 1.0e-6
PTARGET = 0.08
LENGTHS = [1.0, 0.25, 0.25]
NCELL = 16*4*4


# the numbers analyse() returns (kept in summary.json; --regrade grades them again)
ANALYSED = ("n_coll", "sum_P", "max_P", "max_nsub", "n_trunc", "n_noroot", "max_dlam",
            "n_balance", "dW_hist", "dH_hist", "dW_dump", "dH_dump", "slope",
            "dP_over_scale", "untouched_identical", "pair_dE_hist", "pair_abs_dE_hist")


def analyse(rd, met, f, theta0):
    h = collide.read_history(os.path.join(rd, "box.coll.hst"))
    d = collide.read_dump(os.path.join(rd, "box.coll_dump.0.bin"))
    ncoll = float(h["n_coll"][0])
    mass = float(d["m"][0])
    # energies with the metric at each particle, from the dumped metric
    gv = d["own_ginv"]

    def en(u):
        usq = (gv[:, 0]*u[:, 0]*u[:, 0] + gv[:, 3]*u[:, 1]*u[:, 1] + gv[:, 5]*u[:, 2]*u[:, 2]
               + 2.0*(gv[:, 1]*u[:, 0]*u[:, 1] + gv[:, 2]*u[:, 0]*u[:, 2]
                      + gv[:, 4]*u[:, 1]*u[:, 2]))
        w = np.sqrt(1.0 + usq)
        return w, d["own_alpha"]*w - np.sum(d["own_beta"]*u, axis=1)

    w0, h0 = en(d["u0"])
    w1, h1 = en(d["u1"])
    hit = d["nupd"] > 0
    dw_dump = common.exact_sum((w1 - w0)[hit])/ncoll
    dh_dump = common.exact_sum((h1 - h0)[hit])/ncoll
    # regression of the change of H on cos(phi) - cell mean
    k = 2.0*np.pi/met.length
    hc = met.dx*f
    x0 = met.xmin + d["cell"][:, 0]*hc
    cbar = (np.sin(k*(x0 + hc - met.xmin)) - np.sin(k*(x0 - met.xmin)))/(k*hc)
    xc = np.cos(k*(d["x"][:, 0] - met.xmin)) - cbar
    slope = float(np.sum(((h1 - h0)*xc)[hit])/np.sum((xc*xc)[hit]))
    pscale = common.exact_sum(d["m"]*np.linalg.norm(d["u0"], axis=1))
    dp = [(common.exact_sum(d["m"]*d["u1"][:, i]) - common.exact_sum(d["m"]*d["u0"][:, i]))
          / pscale for i in range(3)]
    untouched = bool(np.array_equal(d["u0"][~hit], d["u1"][~hit]))
    return dict(n_coll=int(ncoll), sum_P=float(h["sum_P"][0]), max_P=float(h["max_P"][0]),
                max_nsub=int(h["max_nsub"][0]), n_trunc=int(h["n_trunc"][0]),
                n_noroot=int(h["n_noroot"][0]), max_dlam=float(h["max_dlam"][0]),
                n_balance=int(h["n_balance"][0]),
                dW_hist=float(h["dE_particles"][0])/(mass*ncoll),
                dH_hist=float(h["dH_particles"][0])/(mass*ncoll),
                dW_dump=dw_dump, dH_dump=dh_dump, slope=slope,
                dP_over_scale=[float(v) for v in dp], untouched_identical=untouched,
                pair_dE_hist=float(h["dE"][0])/(mass*ncoll),
                pair_abs_dE_hist=float(h["abs_dE"][0])/(mass*ncoll))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--ref", required=True, action="append",
                    help="reference file of gradient_ref.py (may be given several times)")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=8000000)
    ap.add_argument("--nproc", type=int, default=6)
    ap.add_argument("--cases", default="")
    ap.add_argument("--keep-dumps", action="store_true")
    ap.add_argument("--regrade", default="",
                    help="summary.json of an earlier run: grade its code numbers only")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    ref = None
    for path in args.ref:
        with open(path) as fp:
            r = json.load(fp)
        if ref is None:
            ref = r
        else:
            ref["results"].update(r["results"])
    old = None
    if args.regrade:
        with open(args.regrade) as fp:
            old = json.load(fp)
    names = [c for c in args.cases.split(",") if c] or (
        list(old["cases"]) if old else list(ref["results"]))
    jobs, meta = [], {}
    for k, name in enumerate(names):
        if old is not None:
            meta[name] = {q: old["cases"][name][q] for q in ("case", "particles", "sigma")}
            continue
        aa, apsi, ash, sa, sp, f = gradient_ref.CASES[name]
        met = gradient_ref.metric(name)
        ic = os.path.join(out, name + ".nrp")
        theta0 = gradient_ref.theta_of(name)
        info = scbox.make_particles(ic, met, args.n, 500 + k, theta0, sa, sp, LENGTHS)
        # P = (N_c - 1) sigma M v alpha dt/(psi^6 dV): mean over the cells about PTARGET
        ncc = args.n/(NCELL/f**3)
        mass = LENGTHS[0]*LENGTHS[1]*LENGTHS[2]/args.n
        vol = LENGTHS[0]*LENGTHS[1]*LENGTHS[2]/(NCELL/f**3)
        sigma = PTARGET*vol/(ncc*mass*float(collide.mj_vmol(theta0))*DT)
        meta[name] = dict(case=gradient_ref.CASES[name], particles=info, sigma=sigma)
        for mode in ("cell", "particle"):
            rd = os.path.join(out, name + "_" + mode)
            ov = met.problem_block() + [
                f"particles/particle_file={ic}", f"particles/dt={DT!r}", "time/nlim=1",
                "time/tlim=1.0e9", f"particles/coll_sigma={sigma!r}",
                "particles/coll_pmax=0.95", "particles/coll_subcycle=conservative",
                f"particles/coll_cell_factor={f}", f"particles/coll_energy={mode}",
                "particles/coll_dump_cycle=0", "particles/snap_dt=-1.0",
                f"job/rng_seed={900 + k}"]
            jobs.append((args.exe, DECK, rd, ov))
    if old is None:
        res = common.run_many(jobs, args.nproc)
        if any(r[0] != 0 for r in res):
            print("a run failed:", [r[0] for r in res])
            sys.exit(1)
        summary = dict(n=args.n, dt=DT, theta0=ref["theta0"], hot=ref.get("hot"),
                       exe=args.exe, exe_sha256=common.sha256(args.exe),
                       ref=[os.path.abspath(pth) for pth in args.ref],
                       wall_s=[round(r[1], 1) for r in res], cases={})
    else:
        summary = dict(n=old["n"], dt=old["dt"], theta0=ref["theta0"], hot=ref.get("hot"),
                       exe=old["exe"], exe_sha256=old["exe_sha256"],
                       ref=[os.path.abspath(pth) for pth in args.ref],
                       regraded_from=os.path.abspath(args.regrade),
                       wall_s=old["wall_s"], cases={})
    ok = True
    for name in names:
        f = gradient_ref.CASES[name][5]
        met = gradient_ref.metric(name)
        entry = dict(meta[name])
        for mode in ("cell", "particle"):
            rd = os.path.join(out, name + "_" + mode)
            if old is None:
                r = analyse(rd, met, f, gradient_ref.theta_of(name))
            else:
                r = {q: old["cases"][name][mode][q] for q in ANALYSED}
            rf = ref["results"][name][mode]
            # rejected collisions: share of the proposals, against the reference
            nprop = r["n_coll"] + r["n_balance"] + r["n_noroot"]
            r["rejected"] = r["n_balance"]/nprop
            r["rejected_ref"] = rf["rejected"]
            r["rejected_z"] = float((r["n_balance"] - rf["rejected"]*nprop)
                                    / np.sqrt(max(rf["rejected"]*nprop, 1.0)))
            nc = r["n_coll"]
            for q in ("dW", "dH", "slope"):
                se = np.hypot(rf[q + "_sd"]/np.sqrt(nc), rf[q + "_se"])
                val = r[q + "_hist"] if q != "slope" else r["slope"]
                r[q + "_ref"] = rf[q]
                r[q + "_se"] = float(se)
                r[q + "_z"] = float((val - rf[q])/se) if se > 0.0 else 0.0
            # history budget against the dump
            r["budget_vs_dump"] = [abs(r["dW_hist"] - r["dW_dump"]),
                                   abs(r["dH_hist"] - r["dH_dump"])]
            entry[mode] = r
            if old is None and not args.keep_dumps:
                os.remove(os.path.join(rd, "box.coll_dump.0.bin"))
        c, p = entry["cell"], entry["particle"]
        homog_space = (gradient_ref.CASES[name][1] == 0.0)
        checks = {
            # G1: operator of core-v0.3 against the pair model
            "G1_dW": bool(abs(c["dW_hist"]) < 1e-13) if homog_space
            else bool(abs(c["dW_z"]) < 4.0),
            "G1_dH": bool(abs(c["dH_z"]) < 4.0),
            "G1_slope": bool(abs(c["slope_z"]) < 4.0),
            # G2: metric at each particle
            "G2a_dH": bool(abs(p["dH_hist"]) < 1e-15),
            "G2b_dP": bool(max(abs(v) for v in p["dP_over_scale"]) < 1e-14),
            "G2c_noroot": bool(p["n_noroot"] == 0),
            "G2d_slope": bool(abs(p["slope_z"]) < 4.0),
            "G2d_rejected": bool(abs(p["rejected_z"]) < 4.0 and c["n_balance"] == 0),
            "budget_dump": bool(max(c["budget_vs_dump"] + p["budget_vs_dump"]) < 1e-12),
            "one_substep": bool(c["max_nsub"] == 1 and p["max_nsub"] == 1
                                and c["n_trunc"] == 0 and p["n_trunc"] == 0),
            "untouched": bool(c["untouched_identical"] and p["untouched_identical"]),
        }
        entry["checks"] = checks
        ok = ok and all(checks.values())
        summary["cases"][name] = entry
    cs = summary["cases"]
    extra = {}
    if "psi_inverted" in cs:
        c = cs["psi_inverted"]["cell"]
        extra["G1b_inverted_negative"] = bool(c["dW_hist"] < -4.0*c["dW_se"])
    if "psi_null" in cs and "psi_iso" in cs:
        extra["G1b_null_small"] = bool(abs(cs["psi_null"]["cell"]["dW_hist"])
                                       < 0.25*cs["psi_iso"]["cell"]["dW_hist"])
    for a, b in (("psi_iso_f2", "psi_iso"), ("psi_iso_f4", "psi_iso"),
                 ("psi_iso", "psi_iso_half")):
        if a in cs and b in cs:
            ca, cb = cs[a]["cell"], cs[b]["cell"]
            ratio = ca["dW_hist"]/cb["dW_hist"]
            rr = ca["dW_ref"]/cb["dW_ref"]
            se = ratio*np.hypot(ca["dW_se"]/ca["dW_hist"], cb["dW_se"]/cb["dW_hist"])
            extra[f"G1c_ratio_{a}_over_{b}"] = dict(code=float(ratio), reference=float(rr),
                                                    se=float(se),
                                                    ok=bool(abs(ratio - rr) < 4.0*se))
            ok = ok and extra[f"G1c_ratio_{a}_over_{b}"]["ok"]
    for kk in ("G1b_inverted_negative", "G1b_null_small"):
        if kk in extra:
            ok = ok and extra[kk]
    eq = [n for n in ("psi_iso", "psi_iso_f2", "psi_iso_f4", "psi_iso_half", "lapse_tolman",
                      "well_tolman", "well_tolman_f2", "psi_iso_hot", "well_tolman_hot",
                      "well_tolman_hot_f2") if n in cs]
    extra["G2d_equilibria_slope_zero"] = {n: bool(abs(cs[n]["particle"]["slope"])
                                                  < 4.0*cs[n]["particle"]["slope_se"])
                                          for n in eq}
    ok = ok and all(extra["G2d_equilibria_slope_zero"].values())
    summary["extra"] = extra
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    for name in names:
        e = cs[name]
        print(f"{name:15s} cell: dW {e['cell']['dW_hist']:+.3e} (ref {e['cell']['dW_ref']:+.3e},"
              f" z {e['cell']['dW_z']:+.1f}) dH {e['cell']['dH_hist']:+.3e} (z "
              f"{e['cell']['dH_z']:+.1f}) slope {e['cell']['slope']:+.3e} (z "
              f"{e['cell']['slope_z']:+.1f}) | particle: dH {e['particle']['dH_hist']:+.1e}"
              f" slope {e['particle']['slope']:+.3e} (ref {e['particle']['slope_ref']:+.3e},"
              f" z {e['particle']['slope_z']:+.1f}) noroot {e['particle']['n_noroot']}"
              f" rejected {e['particle']['rejected']:.2e} (z {e['particle']['rejected_z']:+.1f})"
              f" {'ok' if all(e['checks'].values()) else 'FAIL ' + str([k for k, v in e['checks'].items() if not v])}")
    print("extra:", json.dumps(extra))
    print("ok:", ok)

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(9.0, 3.3))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.33, top=0.92, wspace=0.36)
    xs = np.arange(len(names))
    sc = 1.0e4
    for ax, q, lab in ((axs[0], "dW", r"$\Delta\sum W$ per collision [$10^{-4}$]"),
                       (axs[1], "dH", r"$\Delta\sum H$ per collision [$10^{-4}$]"),
                       (axs[2], "slope", r"energy handed along $\cos\phi$ [$10^{-2}$]")):
        s = sc if q != "slope" else 1.0e2
        for mode, col, off in (("cell", fs.PAL["red"], -0.12), ("particle", fs.PAL["blue"], 0.12)):
            val = np.array([cs[n][mode][q + "_hist"] if q != "slope" else cs[n][mode]["slope"]
                            for n in names])
            rf = np.array([cs[n][mode][q + "_ref"] for n in names])
            se = np.array([cs[n][mode][q + "_se"] for n in names])
            ax.errorbar(xs + off, s*val, yerr=s*se, fmt="o", ms=3.5, color=col, lw=0.8,
                        label=f"code, coll_energy = {mode}")
            ax.plot(xs + off, s*rf, ls="none", marker="_", ms=11, mew=1.3, color="k",
                    label="pair model" if mode == "cell" else None)
        ax.axhline(0.0, **fs.GUIDE)
        ax.set_xticks(xs)
        ax.set_xticklabels([n.replace("_", " ") for n in names], rotation=60, ha="right",
                           fontsize=6.5)
        ax.set_ylabel(lab)
    axs[0].legend(fontsize=6.5, loc="upper left")
    fig.savefig(os.path.join(out, "fig_gradient.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
