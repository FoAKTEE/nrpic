#!/usr/bin/env python3
"""T12 of collide/TESTS.md: collisions in a static, homogeneous, non-flat metric.

    python3 t12.py DESIGN_JSON [--n 1000000] [--steps 200] [--nproc 8] [--exe PATH]
                   [--thetas 0.1,1.0] [--tag cpu] [--from RUN_DIR]

--from: analyse the run directories of an earlier run of this script instead of running
AthenaK again (figure and JSON written anew).

Metric: constant lapse alpha0 = 0.8 and conformal factor psi0 = 1.1, zero shift
(inputs/box_static.athinput: nrpic_geodesic, metric_kind = static_conformal, amplitudes 0,
mesh metric with Hermite reconstruction), executable of core/collisions-2.

For each theta in {0.1, 1} and seeds (1, 1), (2, 2):
  curved   box [10, 11)^3, 32^3 cells, N particles of the T2 generator (make_box mj, rest
           mass 1/N each) with covariant momenta u_i = sqrt(psi4) uhat_i, uhat the
           orthonormal-frame momenta of the generator (psi4 = (psi0 psi0)(psi0 psi0) as
           the problem generator forms it); coll_energy = particle; dt and sigma of the
           T2 design (plain variant).
  flat     its twin in Minkowski space (inputs/box_c2.athinput, analytic flat metric):
           the same particles at proper positions x_f = 10 + s (x - 10), s = sqrt(psi4),
           momenta uhat, box [10, 10 + s)^3 on 32^3 cells, step alpha0 dt, same sigma.
           Same proper density (proper box volume psi0^6), same temperature, same
           proper-time step: per coordinate volume and coordinate time the curved box must
           collide alpha0 psi0^6 times as often as its twin.
  cell     (theta = 0.1, seed 1 only) the curved run with coll_energy = cell.
Pass (TESTS.md T12 with the T2 clauses, both seeds):
  (R) rate: mean sum_P per step of the curved run equal to
      alpha0 psi0^6 (1/2) (rho_p/M) rho_p sigma <v_Mol>(theta_s) dt (V_coord = 1, rho_p
      the proper rest-mass density, theta_s from <W - 1> of the orthonormal momenta of the
      initial snapshot) within 4 standard errors of its step-to-step scatter [criterion];
      also the ratio to that value and (a): sum n_coll within 4 sqrt(sum sum_P) of sum
      sum_P [reported with the same 4-sigma rule];
  (F) twin: per coordinate volume and coordinate time, collisions(curved)/collisions(flat)
      = alpha0 psi0^6 within 4 sigma (Poisson of both) [criterion]; the step-by-step
      tested pairs and collisions of the two are compared and reported;
  (C) conservation as in T1 for the covariant sum M u_i: per step |dP_i|/sum_MW and
      |dE|/sum_MW below 1e-14 sqrt(n_coll + 1), n_trunc = 0 [criterion]; exactly rounded
      sums of M u_i and of M W (W with the metric) of the first and last snapshots
      reported; n_noroot, n_balance, max_dlam reported (expected 0, 0, rounding).
Writes t12_<tag>.json and t12_<tag>.png into $NRPIC_RUN_DIR.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

import boxlib as bl
import mj
import rate

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

ALPHA0, PSI0 = 0.8, 1.1
PSI4 = (PSI0 * PSI0) * (PSI0 * PSI0)
S = math.sqrt(PSI4)                  # proper length of one coordinate unit
PSI6 = PSI4 * (PSI0 * PSI0)
DECK_STATIC = os.path.join(bl.PKG, "inputs", "box_static.athinput")
DECK_FLAT = os.path.join(bl.PKG, "inputs", "box_c2.athinput")
SEEDS = (1, 2)


def theta_of(uhat):
    k = bl.snap.kinetic_flat(uhat)
    th = float(mj.theta_from_kinetic(float(k.mean())))
    return th, float(k.std() / np.sqrt(k.size)) / float(mj.c_v(th))


def first_last(rd):
    f = bl.snapshots(rd)
    return bl.snap.read_snapshot(f[0]), bl.snap.read_snapshot(f[-1])


def analyse(rd, kind, N, dt, sig):
    h = bl.coll_history(rd)
    s0, s1 = first_last(rd)
    scale = S if kind != "flat" else 1.0       # covariant -> orthonormal momenta
    th0, se0 = theta_of(s0["u"] / scale)
    th1, se1 = theta_of(s1["u"] / scale)
    M = float(s0["m"][0])
    Vp = 1.0 * PSI6 if kind != "flat" else S ** 3          # proper volume of the box
    rho_p = float(math.fsum(s0["m"])) / Vp
    vm = float(rate.vmol_mean(th0))
    if kind == "flat":
        exp = 0.5 * N * rho_p * sig * vm * dt                # flat: alpha = 1
    else:                                                    # V_coord = 1
        exp = ALPHA0 * PSI6 * 0.5 * (rho_p / M) * rho_p * sig * vm * dt
    sP, nc = h["sum_P"], h["n_coll"]
    se_step = float(sP.std(ddof=1) / np.sqrt(sP.size))
    smw = h["sum_MW"]
    bound = 1e-14 * np.sqrt(nc + 1)
    relE = np.abs(h["dE"]) / smw
    relP = np.max(np.abs(np.stack([h["dP1"], h["dP2"], h["dP3"]])), axis=0) / smw
    W0 = np.sqrt(1.0 + np.sum(s0["u"] ** 2, 1) / (PSI4 if kind != "flat" else 1.0))
    W1 = np.sqrt(1.0 + np.sum(s1["u"] ** 2, 1) / (PSI4 if kind != "flat" else 1.0))
    e0 = math.fsum(s0["m"] * W0)
    e1 = math.fsum(s1["m"] * W1)
    p0 = bl.fsum_cols(s0["m"][:, None] * s0["u"])
    p1 = bl.fsum_cols(s1["m"][:, None] * s1["u"])
    r = dict(run=rd, kind=kind, N=N, dt=dt, sigma=sig, steps=int(nc.size),
             theta0=th0, theta0_se=se0, theta_end=th1, theta_end_se=se1,
             rho_proper=rho_p, M=M, vmol_ref=vm, expected_per_step=exp,
             sumP_per_step=float(sP.mean()), sumP_per_step_se=se_step,
             ratio=float(sP.mean() / exp), z_rate=float((sP.mean() - exp) / se_step),
             collisions=float(nc.sum()), sum_P=float(sP.sum()),
             z_a=float((nc.sum() - sP.sum()) / np.sqrt(sP.sum())),
             max_P=float(h["max_P"].max()), max_nsub=float(h["max_nsub"].max()),
             n_trunc=float(h["n_trunc"].sum()), n_bad_cells=float(h["n_bad_cells"].sum()),
             T1_max_relE=float(relE.max()), T1_max_relP=float(relP.max()),
             T1_max_relE_over_bound=float((relE / bound).max()),
             T1_max_relP_over_bound=float((relP / bound).max()),
             exact_dE_rel=float((e1 - e0) / e0),
             exact_dP_rel=float(np.max(np.abs(p1 - p0)) / e0),
             mass_identical=bool(np.array_equal(s0["m"], s1["m"])),
             series=dict(n_tested=h["n_tested"].tolist(), n_coll=nc.tolist(),
                         sumP=(sP / exp).tolist(), relE=relE.tolist(), relP=relP.tolist(),
                         bound=bound.tolist()))
    r["pass_rate"] = bool(abs(r["z_rate"]) < 4)
    r["pass_a"] = bool(abs(r["z_a"]) < 4)
    r["pass_T1"] = bool((relE < bound).all() and (relP < bound).all() and r["n_trunc"] == 0)
    if "n_noroot" in h:
        r.update(n_noroot=float(h["n_noroot"].sum()), n_balance=float(h["n_balance"].sum()),
                 max_dlam=float(h["max_dlam"].max()))
        if "dH_particles" in h:
            r["max_abs_dH_particles_rel"] = float(np.max(np.abs(h["dH_particles"]) /
                                                         np.abs(h["sum_MH_particles"])))
            r["max_abs_dE_particles_rel"] = float(np.max(np.abs(h["dE_particles"]) /
                                                         np.abs(h["sum_MW_particles"])))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--exe", default=bl.EXE_CPU_C2)
    ap.add_argument("--thetas", default="0.1,1.0")
    ap.add_argument("--tag", default="cpu")
    ap.add_argument("--from", dest="src", default=None)
    a = ap.parse_args()
    des = json.load(open(a.design))["T2"]
    out = bl.outdir()
    base = a.src if a.src else out
    jobs, runs = [], []
    for th in a.thetas.split(","):
        d = des[th]
        dt, sig = float(d["dt"]), float(d["sigma"])
        for seed in SEEDS:
            gen = os.path.join(base, f"gen_th{th}_s{seed}")
            if not a.src:
                bl.make_box(gen, "mj", n=a.n, theta=float(th), sigma=sig, seed=seed)
            p = bl.snap.read_nrp(os.path.join(gen, "box.nrp"))
            common = [f"time/nlim={a.steps}", f"particles/coll_sigma={sig!r}",
                      f"job/rng_seed={seed}", "particles/coll_budget=true"]
            kinds = ["curved", "flat"] + (["cell"] if (th == "0.1" and seed == 1) else [])
            for kind in kinds:
                rd = os.path.join(base, f"T12_th{th}_{kind}_s{seed}")
                os.makedirs(rd, exist_ok=True)
                if kind == "flat":
                    x = bl.X0 + S * (p["x"] - bl.X0)
                    if not a.src:
                        bl.snap.write_nrp(os.path.join(rd, "box.nrp"), x, p["u"], p["m"])
                    dtk = ALPHA0 * dt
                    ov = [f"mesh/x{k}max={bl.X0 + S!r}" for k in (1, 2, 3)] + [
                        "particles/coll_energy=particle"]
                    deck = DECK_FLAT
                else:
                    if not a.src:
                        bl.snap.write_nrp(os.path.join(rd, "box.nrp"), p["x"], S * p["u"], p["m"])
                    dtk = dt
                    ov = [f"particles/coll_energy={'cell' if kind == 'cell' else 'particle'}"]
                    deck = DECK_STATIC
                ov += bl.mesh_overrides(32) + common + [
                    f"particles/dt={dtk!r}",
                    f"particles/snap_dt={a.steps * dtk * (1 - 1e-9)!r}"]
                jobs.append((rd, ov, dict(exe=a.exe, deck=deck)))
                runs.append((th, seed, kind, rd, dtk, sig))
    if a.src:
        rr = []
        for j in jobs:
            with open(os.path.join(j[0], "wall.json")) as fh:
                w = json.load(fh)
            rr.append(dict(rc=w["rc"], wall=w["wall"]))
    else:
        rr = bl.run_many(jobs, a.nproc)
    res = {}
    for (th, seed, kind, rd, dtk, sig), r0 in zip(runs, rr):
        name = os.path.basename(rd)
        if r0["rc"] != 0:
            res[name] = dict(rc=r0["rc"], failed=True, wall=r0["wall"])
            continue
        r = analyse(rd, kind, a.n, dtk, sig)
        r.update(rc=0, wall=r0["wall"], theta=th, seed=seed)
        res[name] = r
    # twin comparison: per coordinate volume and coordinate time
    twins = {}
    for th in a.thetas.split(","):
        for seed in SEEDS:
            c = res.get(f"T12_th{th}_curved_s{seed}")
            f = res.get(f"T12_th{th}_flat_s{seed}")
            if not c or not f or c.get("failed") or f.get("failed"):
                continue
            Vc, Vf = 1.0, S ** 3
            rc_ = c["collisions"] / (Vc * c["dt"] * c["steps"])
            rf_ = f["collisions"] / (Vf * f["dt"] * f["steps"])
            ratio = rc_ / rf_
            sd = ratio * math.sqrt(1.0 / c["collisions"] + 1.0 / f["collisions"])
            t = dict(rate_ratio=ratio, expected=ALPHA0 * PSI6,
                     z=(ratio - ALPHA0 * PSI6) / sd, sd=sd,
                     sumP_ratio=(c["sum_P"] / (Vc * c["dt"])) / (f["sum_P"] / (Vf * f["dt"])) /
                     (ALPHA0 * PSI6),
                     n_tested_identical=bool(np.array_equal(c["series"]["n_tested"],
                                                            f["series"]["n_tested"])),
                     steps_ncoll_differ=int(np.sum(np.array(c["series"]["n_coll"]) !=
                                                   np.array(f["series"]["n_coll"]))))
            t["pass"] = bool(abs(t["z"]) < 4)
            # curved snapshots against the twin mapped back to coordinates
            sc = first_last(c["run"])[1]
            sf = first_last(f["run"])[1]
            # positions modulo the period (the snapshots of the two runs need not wrap a
            # particle at the same time; a whole number of periods is the same point)
            d = (sf["x"] - bl.X0) / S - (sc["x"] - bl.X0)
            dx_raw = np.max(np.abs(d))
            dx = np.max(np.abs(d - np.round(d)))
            du = np.max(np.abs(sf["u"] - sc["u"] / S), 1) / np.maximum(
                1.0, np.sqrt(np.sum(sf["u"] ** 2, 1)))
            t.update(final_max_dx_coord=float(dx), final_max_dx_coord_raw=float(dx_raw),
                     final_max_du_rel=float(du.max()),
                     final_frac_du_gt_1e12=float((du > 1e-12).mean()))
            twins[f"th{th}_s{seed}"] = t
    cell = {}
    rc_, rp_ = res.get("T12_th0.1_cell_s1"), res.get("T12_th0.1_curved_s1")
    if rc_ and rp_ and not rc_.get("failed") and not rp_.get("failed"):
        s_c = first_last(rc_["run"])[1]
        s_p = first_last(rp_["run"])[1]
        cell = dict(counts_identical=bool(
            np.array_equal(rc_["series"]["n_coll"], rp_["series"]["n_coll"]) and
            np.array_equal(rc_["series"]["n_tested"], rp_["series"]["n_tested"])),
            final_max_du=float(np.max(np.abs(s_c["u"] - s_p["u"]))),
            x_identical=bool(np.array_equal(s_c["x"], s_p["x"])))
    crit = [v for k, v in res.items() if "_curved_" in k and not v.get("failed")]
    summ = dict(exe=a.exe, source=base, alpha0=ALPHA0, psi0=PSI0, psi4=PSI4, psi6=PSI6,
                runs={k: {kk: vv for kk, vv in v.items() if kk != "series"}
                      for k, v in res.items()},
                twins=twins, cell_vs_particle=cell,
                pass_rate=bool(crit and all(v["pass_rate"] for v in crit)),
                pass_a=bool(crit and all(v["pass_a"] for v in crit)),
                pass_T1=bool(crit and all(v["pass_T1"] for v in crit)),
                pass_twin=bool(twins and all(t["pass"] for t in twins.values())),
                any_failed_run=any(v.get("failed") for v in res.values()))
    summ["pass"] = bool(summ["pass_rate"] and summ["pass_T1"] and summ["pass_twin"] and
                        len(crit) == 2 * len(a.thetas.split(",")) and
                        not summ["any_failed_run"])
    bl.save_json(os.path.join(out, f"t12_{a.tag}.json"), summ)
    figure(res, twins, out, a.tag)
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"}, indent=1))
    for k, v in summ["runs"].items():
        print(k, {kk: v.get(kk) for kk in ("ratio", "z_rate", "z_a", "pass_T1",
                                             "T1_max_relP_over_bound", "n_noroot",
                                             "n_balance", "max_dlam", "wall")})


def figure(res, twins, out, tag):
    fs.use_style()
    cols = {"0.1": fs.PAL["red"], "1.0": fs.PAL["yellow"]}
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax1 = fig.add_axes([0.08, 0.15, 0.24, 0.78])
    ax2 = fig.add_axes([0.42, 0.15, 0.22, 0.78])
    ax3 = fig.add_axes([0.75, 0.15, 0.23, 0.78])
    for name, r in sorted(res.items()):
        if r.get("failed") or r["kind"] == "cell":
            continue
        c = cols.get(r["theta"], "k")
        if r["kind"] == "curved" and r["seed"] == 1:
            ax1.plot(np.arange(1, r["steps"] + 1), r["series"]["sumP"], color=c, lw=0.7,
                     label=rf"$\theta={r['theta']}$")
        if r["kind"] == "curved":
            b = np.array(r["series"]["bound"])
            ax3.semilogy(np.maximum(np.array(r["series"]["relP"]), 1e-30) / b,
                         color=c, lw=0.6, ls="-" if r["seed"] == 1 else "--")
    ax1.axhline(1, **fs.GUIDE)
    ax1.set_xlabel("step")
    ax1.set_ylabel(r"curved: $\Sigma P$ per step / expected", fontsize=8)
    ax1.legend(loc="lower right", fontsize=7)
    k = 0
    xs, labels = [], []
    for key, t in sorted(twins.items()):
        th = key.split("_")[0][2:]
        seed = key.split("_")[1]
        c = cols.get(th, "k")
        ax2.errorbar(k, t["rate_ratio"] / t["expected"] - 1, yerr=t["sd"] / t["expected"],
                     fmt="o", color=c, ms=4, mfc=c if seed == "s1" else "none",
                     label="twin (Poisson sd)" if k == 0 else None)
        r = res[f"T12_th{th}_curved_{seed}"]
        ax2.errorbar(k + 0.3, r["ratio"] - 1, yerr=r["sumP_per_step_se"] / r["expected_per_step"],
                     fmt="s", color="grey", ms=3, label="analytic (se)" if k == 0 else None)
        xs.append(k + 0.15); labels.append(f"{th}\n{seed}")
        k += 1
    ax2.axhline(0, **fs.GUIDE)
    ax2.set_xticks(xs); ax2.set_xticklabels(labels, fontsize=7)
    ax2.set_ylabel(r"rate / ($\alpha_0\psi_0^6\times$flat) $-$ 1", fontsize=8)
    ax2.legend(loc="lower left", fontsize=6)
    ax3.axhline(1, **fs.GUIDE)
    ax3.set_xlabel("step")
    ax3.set_ylabel(r"curved: $\max_i|dP_i|/\Sigma MW$ / bound", fontsize=8)
    ax3.set_ylim(1e-12, 10)
    fs.save(fig, os.path.join(out, f"t12_{tag}"))
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
