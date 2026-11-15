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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_GPU)
    ap.add_argument("--tlim", type=float, default=150.0)
    ap.add_argument("--kn", default="30,3")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--snap-dt", type=float, default=10.0)
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
    with open(deck_coll, "w") as fp:
        fp.write(text.replace(anchor, anchor + coll_block))
    base = [f"particles/particle_file={os.path.join(ic, 'st.nrp')}",
            f"problem/comp0_file={os.path.join(ic, 'st.tab')}", f"time/tlim={args.tlim}",
            f"particles/snap_dt={args.snap_dt}", "job/rng_seed=4242"]
    runs = {"off": (DECK, base), "sigma0": (deck_coll, base)}
    sig = {}
    for kn in kns:
        sig[kn] = 1.0/(rho0_c*radius*kn)
        runs[f"kn{kn:g}"] = (deck_coll, base + [f"particles/coll_sigma={sig[kn]!r}"])
    summary = {"model": {k: model[k] for k in ("yc", "M0", "R_areal", "rho0_c", "alpha_c")},
               "tlim": args.tlim, "n": args.n, "sigma": {f"kn{k:g}": v for k, v in sig.items()},
               "exe": args.exe, "exe_sha256": common.sha256(args.exe), "runs": {}}
    ok = True
    for name, (deck, ov) in runs.items():
        code, wall = common.run_athena(args.exe, deck, os.path.join(out, name), ov)
        summary["runs"][name] = {"exit": code, "wall_s": round(wall, 1)}
        ok = ok and code == 0

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
        if name != "off":
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
                     energy_hist_vs_coll_hist=float(np.max(np.abs(
                         c["sum_MW_particles"] - h["sum_mW"][1:len(c["time"]) + 1])
                         / h["sum_mW"][0])) if len(h["time"]) > len(c["time"]) else None,
                     count_z=float((c["n_coll"].sum() - c["sum_P"].sum())
                                   / np.sqrt(max(c["sum_P"].sum(), 1e-300)))
                     if c["sum_P"].sum() > 0 else 0.0)
    # null: operator on with zero cross-section against operator absent
    s_off = common.snapshots(os.path.join(out, "off"), "st")
    s_sig = common.snapshots(os.path.join(out, "sigma0"), "st")
    summary["null_snapshots_identical"] = bool(
        len(s_off) == len(s_sig) and all(filecmp.cmp(a, b, shallow=False)
                                         for a, b in zip(s_off, s_sig)))
    summary["null_history_identical"] = bool(filecmp.cmp(
        os.path.join(out, "off", "st.nrpic.hst"), os.path.join(out, "sigma0", "st.nrpic.hst"),
        shallow=False))
    good = summary["null_snapshots_identical"]
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

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.27,
                        hspace=0.24)
    cols = dict(zip(runs, ["k", fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"],
                           fs.PAL["green"]]))
    for name in runs:
        h = hst[name]
        ls = ":" if name == "sigma0" else "-"
        axs[0, 0].plot(h["time"], h["alpha_probe"], color=cols[name], ls=ls, lw=1.2,
                       label=name)
        tt = np.array([s["time"] for s in snaps[name]])
        rr = np.array([mass_radii(s) for s in snaps[name]])
        for j in range(3):
            axs[0, 1].plot(tt, rr[:, j], color=cols[name], ls=ls, lw=1.2)
        if name != "off":
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
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
