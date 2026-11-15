#!/usr/bin/env python3
"""P11: the stable monoenergetic relativistic cluster of the first paper (y_c = 0.819,
problems/st/st_cluster.athinput, Z4c with particle sources) with and without collisions.

  run_cluster.py OUTDIR [--exe ATHENA] [--tlim 150] [--kn 30,3] [--n 10000]

Runs: "off" (no collision option), "sigma0" (operator on, cross-section zero),
"knXX" (cross-section per unit mass sigma = 1/(rho0_c R Kn) with the central rest-mass
density and the areal radius of the model). Collision cells are blocks of 4^3 mesh cells
(2 M wide where the mesh has dx = M/2). Compared: central lapse, radii enclosing 10, 50
and 90 percent of the rest mass, rest mass, the deposit identity, the pair defects and
the change of the particle energy caused by the collision steps.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys

import numpy as np

import common
from nrpic import collide

DECK = os.path.join(common.REPO, "problems", "st", "st_cluster.athinput")
MAKE_IC = os.path.join(common.REPO, "problems", "ic", "make_ic.py")
EPS = 2.0**-52


def read_nrpic_hst(path):
    rows = {}
    with open(path) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            if len(v) < 32:
                continue
            rows[int(v[1])] = [float(s) for s in v[:32]]
    a = np.array([rows[k] for k in sorted(rows)])
    names = ["time", "ncycle", "np", "sum_m", "sum_mW", "sum_mux", "sum_muy", "sum_muz",
             "int_E", "int_Sx", "int_Sy", "int_Sz", "alpha_probe", "E_probe", "tau_probe",
             "alpha_min", "n_excised", "m_excised", "n_escaped", "m_escaped"]
    return {nm: a[:, i] for i, nm in enumerate(names)}


def mass_radii(snap, fracs=(0.1, 0.5, 0.9)):
    r = np.sort(np.linalg.norm(snap["x"], axis=1))
    return [float(r[int(f*len(r))]) for f in fracs]


def make_figure(out, runs, hst, snaps, model):
    """Central lapse, mass radii, cumulative collisions and the cumulative change of the
    particle energy by the collision steps, for all runs."""
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.27,
                        hspace=0.24)
    palette = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    cols = {"off": "k", "off2": "grey", "sigma0": fs.PAL["blue"]}
    for name in runs:
        if name not in cols:
            cols[name] = palette[(len(cols) - 3) % len(palette)]
    for name in runs:
        h = hst[name]
        ls = ":" if name in ("sigma0", "off2") else "-"
        axs[0, 0].plot(h["time"], h["alpha_probe"], color=cols[name], ls=ls, lw=1.2,
                       label=name)
        tt = np.array([s["time"] for s in snaps[name]])
        rr = np.array([mass_radii(s) for s in snaps[name]])
        for j in range(3):
            axs[0, 1].plot(tt, rr[:, j], color=cols[name], ls=ls, lw=1.2)
        if name not in ("off", "off2"):
            c = collide.read_history(os.path.join(out, name, "st.coll.hst"))
            axs[1, 0].plot(c["time"], np.cumsum(c["n_coll"]), color=cols[name], ls=ls, lw=1.2)
            axs[1, 1].plot(c["time"], np.cumsum(c["dE_particles"])/c["sum_MW_particles"][0],
                           color=cols[name], ls=ls, lw=1.2)
    axs[0, 0].axhline(model["alpha_c"], **fs.GUIDE)
    axs[0, 0].set_ylabel("central lapse")
    axs[0, 1].set_ylabel("radii of 10, 50, 90 percent of the rest mass")
    axs[1, 0].set_ylabel("collisions (cumulative)")
    axs[1, 1].set_ylabel(r"cumulative $\Delta(\Sigma MW)$ of the collision steps / $\Sigma MW$")
    for ax in axs.ravel():
        ax.set_xlabel(r"$t/M$")
    axs[0, 0].legend(fontsize=8, ncol=2)
    fig.savefig(os.path.join(out, "fig_cluster.png"), dpi=200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_GPU)
    ap.add_argument("--tlim", type=float, default=150.0)
    ap.add_argument("--kn", default="30,3")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--snap-dt", type=float, default=10.0)
    ap.add_argument("--factors", default="4",
                    help="coll_cell_factor of the collisional runs, comma separated")
    ap.add_argument("--skip-null", action="store_true",
                    help="do not run the repeated baseline and the run with sigma = 0")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    ic = os.path.join(out, "ic")
    subprocess.run([sys.executable, MAKE_IC, "st", "--yc", "0.819", "--N", str(args.n),
                    "--sampler", "stratified", "--seed", "1", "--out", ic, "--prefix",
                    "st"], check=True, stdout=subprocess.DEVNULL)
    model = json.load(open(os.path.join(ic, "st.json")))
    rho0_c, radius = model["rho0_c"], model["R_areal"]
    kns = [float(k) for k in args.kn.split(",") if k]
    text = open(DECK).read()
    anchor = "particle_file  = particles.nrp\n"
    assert anchor in text
    coll_block = ("collisions       = true\ncoll_sigma       = 0.0\ncoll_pmax        = 0.1\n"
                  "coll_cell_factor = 4\ncoll_hist_dcycle = 1\ncoll_budget      = true\n")
    deck_coll = os.path.join(out, "st_cluster_coll.athinput")
    job = "basename  = st\n"
    assert job in text
    with open(deck_coll, "w") as fp:
        fp.write(text.replace(anchor, anchor + coll_block)
                 .replace(job, job + "rng_seed  = 4242\n"))
    factors = [int(f) for f in args.factors.split(",") if f]
    base = [f"particles/particle_file={os.path.join(ic, 'st.nrp')}",
            f"problem/comp0_file={os.path.join(ic, 'st.tab')}", f"time/tlim={args.tlim}",
            f"particles/snap_dt={args.snap_dt}"]
    # "off2" repeats "off": on a card the deposit adds with atomic operations in an
    # order that changes from run to run, so two runs of the same input differ at
    # rounding level; the null run "sigma0" is judged against that difference
    runs = {"off": (DECK, base)}
    if not args.skip_null:
        runs.update({"off2": (DECK, base), "sigma0": (deck_coll, base)})
    sig = {}
    for kn in kns:
        sig[kn] = 1.0/(rho0_c*radius*kn)
        for f in factors:
            name = f"kn{kn:g}" if f == 4 else f"kn{kn:g}_f{f}"
            runs[name] = (deck_coll, base + [f"particles/coll_sigma={sig[kn]!r}",
                                             f"particles/coll_cell_factor={f}"])
    summary = {"model": {k: model[k] for k in ("yc", "M0", "R_areal", "rho0_c", "alpha_c")},
               "tlim": args.tlim, "n": args.n, "sigma": {f"kn{k:g}": v for k, v in sig.items()},
               "exe": args.exe, "exe_sha256": common.sha256(args.exe), "runs": {}}
    ok = True
    for name, (deck, ov) in runs.items():
        code, wall = common.run_athena(args.exe, deck, os.path.join(out, name), ov)
        summary["runs"][name] = {"exit": code, "wall_s": round(wall, 1)}
        ok = ok and code == 0
    if not ok:
        with open(os.path.join(out, "summary.json"), "w") as fp:
            summary["ok"] = False
            json.dump(summary, fp, indent=1)
        print(json.dumps(summary, indent=1))
        sys.exit(1)

    hst = {k: read_nrpic_hst(os.path.join(out, k, "st.nrpic.hst")) for k in runs}
    snaps = {k: [collide.read_snapshot(p) for p in common.snapshots(os.path.join(out, k), "st")]
             for k in runs}
    ref = hst["off"]
    t_dyn = float(np.sqrt(radius**3/model["M0"]))
    summary["dynamical_time"] = t_dyn
    for name in runs:
        h, r = hst[name], summary["runs"][name]
        nmin = min(len(h["time"]), len(ref["time"]))
        r.update(steps=int(len(h["time"]) - 1), particles_end=int(h["np"][-1]),
                 n_excised=int(h["n_excised"][-1]), n_escaped=int(h["n_escaped"][-1]),
                 rest_mass_identical=bool(np.all(h["sum_m"] == h["sum_m"][0])),
                 lapse_min=float(h["alpha_probe"].min()), lapse_max=float(h["alpha_probe"].max()),
                 lapse_end=float(h["alpha_probe"][-1]),
                 lapse_max_diff_to_off=float(np.max(np.abs(h["alpha_probe"][:nmin]
                                                           - ref["alpha_probe"][:nmin]))),
                 deposit_identity=float(np.max(np.abs(h["int_E"] - h["sum_mW"])/h["sum_mW"])),
                 energy_rel_change=float(h["sum_mW"][-1]/h["sum_mW"][0] - 1.0),
                 energy_max_rel_diff_to_off=float(np.max(np.abs(h["sum_mW"][:nmin]
                                                               - ref["sum_mW"][:nmin]))
                                                  / ref["sum_mW"][0]),
                 radii_end=mass_radii(snaps[name][-1]),
                 radii_start=mass_radii(snaps[name][0]))
        rr = np.array([mass_radii(s) for s in snaps[name]])
        r0 = np.array([mass_radii(s) for s in snaps["off"]])
        k = min(len(rr), len(r0))
        r["radii_max_rel_diff_to_off"] = float(np.max(np.abs(rr[:k]/r0[:k] - 1.0)))
        sa, sb = snaps[name][-1], snaps["off"][-1]
        if len(sa["tag"]) == len(sb["tag"]):
            ia, ib = np.argsort(sa["tag"]), np.argsort(sb["tag"])
            r["end_max_dx_to_off"] = float(np.max(np.abs(sa["x"][ia] - sb["x"][ib])))
            r["end_max_du_to_off"] = float(np.max(np.abs(sa["u"][ia] - sb["u"][ib])))
        if name not in ("off", "off2"):
            c = collide.read_history(os.path.join(out, name, "st.coll.hst"))
            nc = np.maximum(c["n_coll"], 1.0)
            mp = float(snaps[name][0]["m"][0])
            r.update(collisions=int(c["n_coll"].sum()), sum_P=float(c["sum_P"].sum()),
                     particles_updated_fraction=float(c["n_updated"].sum()/args.n),
                     n_trunc=int(c["n_trunc"].sum()), n_bad_cells=int(c["n_bad_cells"].max()),
                     max_nsub=int(c["max_nsub"].max()), max_P=float(c["max_P"].max()),
                     mean_N=float(np.mean(c["mean_N"])), min_N=int(c["min_N"].min()),
                     n_part_min=int(c["n_part"].min()),
                     max_dx_mfp=float(c["max_dx_mfp"].max()),
                     pair_dE_eps=float(np.max(c["abs_dE"]/nc)/(EPS*2.0*mp)),
                     pair_dE_sum_rel=float(np.abs(c["dE"].sum())/c["sum_MW"][0]),
                     dE_particles_sum_rel=float(c["dE_particles"].sum()/c["sum_MW_particles"][0]),
                     dE_particles_abs_sum_rel=float(np.abs(c["dE_particles"]).sum()
                                                    / c["sum_MW_particles"][0]),
                     dE_particles_per_collision=float(
                         c["dE_particles"].sum()/c["sum_MW_particles"][0]
                         / max(c["n_coll"].sum(), 1.0)),
                     energy_hist_vs_coll_hist=float(np.max(np.abs(
                         c["sum_MW_particles"] - h["sum_mW"][1:len(c["time"]) + 1])
                         / h["sum_mW"][0])) if len(h["time"]) > len(c["time"]) else None,
                     count_z=float((c["n_coll"].sum() - c["sum_P"].sum())
                                   / np.sqrt(max(c["sum_P"].sum(), 1e-300)))
                     if c["sum_P"].sum() > 0 else 0.0)
    if args.skip_null:
        good = True
        for name, r in summary["runs"].items():
            good = good and r["rest_mass_identical"] and r["n_excised"] == 0 \
                and r["n_escaped"] == 0 and r["deposit_identity"] < 1e-12
            if name.startswith("kn"):
                good = good and r["pair_dE_eps"] < 8.0 and r["n_trunc"] == 0 \
                    and r["n_bad_cells"] == 0 and abs(r["count_z"]) < 4.0
        summary["ok"] = bool(ok and good)
        with open(os.path.join(out, "summary.json"), "w") as fp:
            json.dump(summary, fp, indent=1)
        print(json.dumps(summary, indent=1))
        make_figure(out, runs, hst, snaps, model)
        sys.exit(0 if summary["ok"] else 1)
    # null: operator on with zero cross-section against operator absent
    s_off = common.snapshots(os.path.join(out, "off"), "st")
    s_sig = common.snapshots(os.path.join(out, "sigma0"), "st")
    summary["null_snapshots_identical"] = bool(
        len(s_off) == len(s_sig) and all(filecmp.cmp(a, b, shallow=False)
                                         for a, b in zip(s_off, s_sig)))
    summary["null_history_identical"] = bool(filecmp.cmp(
        os.path.join(out, "off", "st.nrpic.hst"), os.path.join(out, "sigma0", "st.nrpic.hst"),
        shallow=False))
    s_off2 = common.snapshots(os.path.join(out, "off2"), "st")
    summary["baseline_twice_snapshots_identical"] = bool(
        len(s_off) == len(s_off2) and all(filecmp.cmp(a, b, shallow=False)
                                          for a, b in zip(s_off, s_off2)))
    # the null run must be as close to the baseline as the baseline is to itself:
    # identical if the baseline is reproducible, otherwise within ten times the
    # difference between its two runs
    r0, r2 = summary["runs"]["sigma0"], summary["runs"]["off2"]
    if summary["baseline_twice_snapshots_identical"]:
        good = summary["null_snapshots_identical"]
    else:
        good = (r0["lapse_max_diff_to_off"] <= 10.0*r2["lapse_max_diff_to_off"] + 1e-14
                and r0["end_max_dx_to_off"] <= 10.0*r2["end_max_dx_to_off"] + 1e-12)
    summary["null_ok"] = bool(good)
    for name, r in summary["runs"].items():
        good = good and r["rest_mass_identical"] and r["n_excised"] == 0 \
            and r["n_escaped"] == 0 and r["deposit_identity"] < 1e-12
        if name.startswith("kn"):
            good = good and r["pair_dE_eps"] < 8.0 and r["n_trunc"] == 0 \
                and r["n_bad_cells"] == 0 and abs(r["count_z"]) < 4.0
    kmax = f"kn{max(kns):g}" if kns else None
    if kmax:
        r = summary["runs"][kmax]
        good = good and r["lapse_max_diff_to_off"] < 0.017 \
            and r["radii_max_rel_diff_to_off"] < 0.10 \
            and abs(r["dE_particles_sum_rel"]) < 1e-4
    summary["ok"] = bool(ok and good)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    make_figure(out, runs, hst, snaps, model)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
