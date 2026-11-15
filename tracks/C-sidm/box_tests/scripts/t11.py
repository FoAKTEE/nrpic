#!/usr/bin/env python3
"""T11 of collide/TESTS.md: Lorentz covariance in a drifting gas.

    python3 t11.py [--n 1000000] [--seeds 1,2] [--nproc 4] [--exe PATH] [--design-only]

Lab frame = the box frame of the code (normal observer). rho_0 of make_box is the lab
rest-mass density (rest-frame density rho_0/gamma_b), sigma = 1, 32^3 cells, dt = 0.08.
(a, b) `make_box.py boosted`, theta = 1, beta = 0.6 along x, 200 steps (16.0 lab time,
10 lab collision times). (c) drifting two-temperature start, written here from the
track's sampler (`mj.sample_u_boosted`, the same as make_box's boosted kind): tags
[0, N/2) at theta_1 = 3, the rest at theta_2 = 1, both drifting with beta = 0.6; 470 steps
(37.6 lab time = 15 tau_rel(rest) gamma_b).

Criteria, declared before the run (TESTS.md gives (a) "within 4 sigma", (b) "unchanged
within 4 sigma", (c) "relaxes to the drifting Maxwell-Juttner gas at theta_eq of the rest
frame"):
(a) total accepted collisions within 4 sqrt(E) of E = sum over steps of
    (1/2) N (rho_lab/gamma) sigma <v_Mol>(theta) dt / gamma, with (theta, beta) of the
    sample solved from its lab means <W> = gamma h - theta/gamma, <u_x> = gamma beta h
    (h = <W>_rest + theta); the T2-style comparison of the mean sum_P per step is reported.
(b) <W>, <u_x>, <u_x^2/W>, <u_y^2/W> of the lab frame at the end equal those at the start
    within 4 standard errors of the mean (sample se of the per-particle quantity).
(c) the end state is the drifting MJ gas (theta_f, beta_f) fixed by the conserved lab
    means of the initial sample (same two equations): <u_x^2/W> = gamma beta^2 h +
    theta/gamma and <u_y^2/W>, <u_z^2/W> = theta/gamma within 4 se, and two-sample KS of
    the lab u_x and of |u_perp| against 2e6 draws of mj.sample_u_boosted(theta_f, beta_f)
    with p > 1e-3. [JUDGEMENT, own derivation: the code conserves the lab-frame sums over
    a lab-homogeneous box, which fix theta_f and a drift beta_f that differs from 0.6 by
    the pressure term; both are printed.]
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import optimize, stats

import boxlib as bl
import mj
import rate

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

BETA, DT, SIG = 0.6, 0.08, 1.0


def lab_means_mj(theta, beta):
    g = 1.0 / np.sqrt(1.0 - beta * beta)
    h = float(mj.enthalpy(theta))
    return dict(W=g * h - theta / g, ux=g * beta * h, uxx=g * beta * beta * h + theta / g,
                uyy=theta / g)


def solve_theta_beta(W, ux, guess=(1.0, 0.6)):
    def f(p):
        th, b = np.exp(p[0]), np.tanh(p[1])
        m = lab_means_mj(th, b)
        return [m["W"] / W - 1.0, m["ux"] / ux - 1.0]
    sol = optimize.fsolve(f, [np.log(guess[0]), np.arctanh(guess[1])], xtol=1e-14)
    return float(np.exp(sol[0])), float(np.tanh(sol[1]))


def lab_moments(u):
    W = bl.W(u)
    q = dict(W=W, ux=u[:, 0], uxx=u[:, 0] ** 2 / W, uyy=u[:, 1] ** 2 / W, uzz=u[:, 2] ** 2 / W)
    return {k: (float(v.mean()), float(v.std() / np.sqrt(v.size))) for k, v in q.items()}


def make_twotemp_boosted(path, n, th1, th2, beta, seed):
    rng = np.random.default_rng(seed)
    x = bl.X0 + rng.uniform(0.0, 1.0, (n, 3))
    n1 = n // 2
    u1 = mj.sample_u_boosted(n1, th1, np.array([beta, 0, 0]), rng)
    u2 = mj.sample_u_boosted(n - n1, th2, np.array([beta, 0, 0]), rng)
    u = np.concatenate([u1, u2])
    m = np.full(n, 1.0 / n)
    sp = np.concatenate([np.zeros(n1, np.int32), np.ones(n - n1, np.int32)])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bl.snap.write_nrp(path, x, u, m, sp)
    meta = dict(kind="boosted_twotemp", n=n, theta1=th1, theta2=th2, beta=beta, seed=seed,
                rho0=1.0, sigma=SIG, n_pop1=n1, box=[1.0, 1.0, 1.0], x0=bl.X0)
    with open(path.replace(".nrp", ".json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    return meta


def design():
    g = 1 / np.sqrt(1 - BETA ** 2)
    out = {}
    # (c): conserved lab means of the two-temperature start (exact expectation)
    m1, m2 = lab_means_mj(3.0, BETA), lab_means_mj(1.0, BETA)
    W, ux = 0.5 * (m1["W"] + m2["W"]), 0.5 * (m1["ux"] + m2["ux"])
    thf, bf = solve_theta_beta(W, ux, (2.0, BETA))
    # alternative reading: drift fixed at 0.6, theta from the lab energy only
    th_alt = optimize.brentq(lambda t: lab_means_mj(t, BETA)["W"] - W, 0.1, 10.0)
    out["c"] = dict(W=W, ux=ux, theta_f=thf, beta_f=bf, theta_alt_beta_fixed=th_alt,
                    uxx_f=lab_means_mj(thf, bf)["uxx"], uyy_f=lab_means_mj(thf, bf)["uyy"],
                    uxx_alt=lab_means_mj(th_alt, BETA)["uxx"],
                    uyy_alt=lab_means_mj(th_alt, BETA)["uyy"],
                    uxx_start=0.5 * (m1["uxx"] + m2["uxx"]),
                    uyy_start=0.5 * (m1["uyy"] + m2["uyy"]))
    vm = float(rate.vmol_mean(1.0))
    out["ab"] = dict(gamma_b=g, coll_per_particle_per_lab_time=vm / g ** 2,
                     expected_total_200=0.5 * 1e6 * vm / g ** 2 * DT * 200,
                     lab_means=lab_means_mj(1.0, BETA))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--seeds", default="1,2")
    ap.add_argument("--nproc", type=int, default=4)
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    ap.add_argument("--design-only", action="store_true")
    a = ap.parse_args()
    out = bl.outdir()
    des = design()
    bl.save_json(os.path.join(out, "t11_design.json"), des)
    print(json.dumps(des, indent=1))
    if a.design_only:
        return 0
    jobs, cases = [], []
    for seed in [int(s) for s in a.seeds.split(",")]:
        rd = os.path.join(out, f"T11ab_s{seed}")
        meta = bl.make_box(rd, "boosted", n=a.n, theta=1.0, beta=BETA, sigma=SIG, seed=seed)
        jobs.append((rd, bl.mesh_overrides(32) + [
            f"particles/dt={DT!r}", "time/nlim=200", f"particles/coll_sigma={SIG!r}",
            f"particles/snap_dt={100 * DT * (1 - 1e-9)!r}", f"job/rng_seed={seed}"],
            dict(exe=a.exe)))
        cases.append(("ab", rd, seed, meta))
        rd = os.path.join(out, f"T11c_s{seed}")
        meta = make_twotemp_boosted(os.path.join(rd, "box.nrp"), a.n, 3.0, 1.0, BETA, seed)
        jobs.append((rd, bl.mesh_overrides(32) + [
            f"particles/dt={DT!r}", "time/nlim=470", f"particles/coll_sigma={SIG!r}",
            f"particles/snap_dt={235 * DT * (1 - 1e-9)!r}", f"job/rng_seed={seed}"],
            dict(exe=a.exe)))
        cases.append(("c", rd, seed, meta))
    rr = bl.run_many(jobs, a.nproc)
    res = dict(design=des, cases={})
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax1 = fig.add_axes([0.08, 0.15, 0.25, 0.78])
    ax2 = fig.add_axes([0.42, 0.15, 0.25, 0.78])
    ax3 = fig.add_axes([0.76, 0.15, 0.22, 0.78])
    rs = np.random.default_rng(99)
    for (kind, rd, seed, meta), r0 in zip(cases, rr):
        name = os.path.basename(rd)
        c = dict(rc=r0["rc"], wall=r0["wall"])
        if r0["rc"]:
            c["failed"] = True
            res["cases"][name] = c
            continue
        files = bl.snapshots(rd)
        s0 = bl.snap.read_snapshot(files[0])
        s1 = bl.snap.read_snapshot(files[-1])
        m0, m1 = lab_moments(s0["u"]), lab_moments(s1["u"])
        th_s, b_s = solve_theta_beta(m0["W"][0], m0["ux"][0],
                                     (1.0 if kind == "ab" else 2.0, BETA))
        g_s = 1 / np.sqrt(1 - b_s ** 2)
        h = bl.coll_history(rd)
        c.update(theta_sample=th_s, beta_sample=b_s, t_end=s1["time"], steps=int(h["ncycle"][-1]),
                 collisions=float(h["n_coll"].sum()), sum_P=float(h["sum_P"].sum()),
                 n_trunc=float(h["n_trunc"].sum()), max_nsub=float(h["max_nsub"].max()),
                 m_start=m0, m_end=m1)
        if kind == "ab":
            N = int(h["n_part"][0])
            dt = float(np.diff(np.concatenate([[0.0], h["time"]])).mean())
            per = 0.5 * N * (meta["rho0"] / g_s) * SIG * float(rate.vmol_mean(th_s)) * dt / g_s
            E = per * h["n_coll"].size
            per_nom = 0.5 * N * (meta["rho0"] / 1.25) * SIG * float(rate.vmol_mean(1.0)) * dt / 1.25
            se = float(h["sum_P"].std(ddof=1) / np.sqrt(h["sum_P"].size))
            c.update(expected_total=E, expected_per_step=per, expected_per_step_nominal=per_nom,
                     z_a=float((c["collisions"] - E) / np.sqrt(E)),
                     ratio_a=float(c["collisions"] / E),
                     sumP_ratio=float(h["sum_P"].mean() / per),
                     sumP_z=float((h["sum_P"].mean() - per) / se),
                     z_count_vs_sumP=float((c["collisions"] - c["sum_P"]) / np.sqrt(c["sum_P"])))
            c["pass_a"] = bool(abs(c["z_a"]) < 4)
            zb = {k: (m1[k][0] - m0[k][0]) / np.hypot(m0[k][1], m1[k][1])
                  for k in ("W", "ux", "uxx", "uyy")}
            c["z_b"] = zb
            c["pass_b"] = bool(all(abs(v) < 4 for v in zb.values()))
            # sample against analytic drifting MJ (diagnostic of the generator)
            an = lab_means_mj(th_s, b_s)
            c["start_vs_analytic_z"] = {k: (m0[k][0] - an[k]) / m0[k][1] for k in ("uxx", "uyy")}
            ls = "-" if seed == 1 else "--"
            ax1.plot(h["ncycle"], h["n_coll"] / per, ls=ls, lw=0.6, color=fs.PAL["red"],
                     label=f"seed {seed}")
        else:
            thf, bf = solve_theta_beta(m0["W"][0], m0["ux"][0], (2.0, BETA))
            an = lab_means_mj(thf, bf)
            zc = {k: (m1[k][0] - an[k]) / m1[k][1] for k in ("uxx", "uyy")}
            zc["uzz"] = (m1["uzz"][0] - an["uyy"]) / m1["uzz"][1]
            ref = mj.sample_u_boosted(2_000_000, thf, np.array([bf, 0, 0]), rs)
            ks_x = stats.ks_2samp(s1["u"][:, 0], ref[:, 0]).pvalue
            uperp = np.hypot(s1["u"][:, 1], s1["u"][:, 2])
            ks_p = stats.ks_2samp(uperp, np.hypot(ref[:, 1], ref[:, 2])).pvalue
            th_alt = optimize.brentq(lambda t: lab_means_mj(t, BETA)["W"] - m0["W"][0], 0.1, 10)
            an_alt = lab_means_mj(th_alt, BETA)
            c.update(theta_f=thf, beta_f=bf, z_c=zc, ks_ux=float(ks_x), ks_uperp=float(ks_p),
                     theta_alt=th_alt,
                     z_c_alt={k: (m1[k][0] - an_alt[k]) / m1[k][1] for k in ("uxx", "uyy")},
                     z_start_vs_final_uxx=(m0["uxx"][0] - an["uxx"]) / m0["uxx"][1])
            c["pass_c"] = bool(all(abs(v) < 4 for v in zc.values()) and ks_x > 1e-3 and
                               ks_p > 1e-3)
            if seed == 1:
                bins = np.linspace(-2, 12, 120)
                ax3.hist(s1["u"][:, 0], bins=bins, density=True, histtype="step",
                         color=fs.PAL["red"], label="end state (c)")
                ax3.hist(ref[:, 0], bins=bins, density=True, histtype="step",
                         color=fs.PAL["blue"], label=r"MJ($\theta_f,\beta_f$)")
                ax3.hist(s0["u"][:, 0], bins=bins, density=True, histtype="step",
                         color="grey", alpha=0.6, label="start (c)")
        res["cases"][name] = c
    # panel 2: z-scores
    k = 0
    labels = []
    for name, c in res["cases"].items():
        if c.get("failed"):
            continue
        zs = ([c["z_a"]] + list(c["z_b"].values())) if "z_a" in c else list(c["z_c"].values())
        ax2.plot([k] * len(zs), zs, "o", ms=4, color=fs.PAL["red"] if "z_a" in c else fs.PAL["blue"])
        labels.append(name.replace("T11", "")); k += 1
    ax2.axhspan(-4, 4, color="grey", alpha=0.15); ax2.axhline(0, **fs.GUIDE)
    ax2.set_xticks(range(k)); ax2.set_xticklabels(labels, fontsize=7)
    ax2.set_ylabel("z (a: count; b: moments; c: moments vs MJ)", fontsize=8)
    ax1.axhline(1, **fs.GUIDE)
    ax1.set_xlabel("step"); ax1.set_ylabel(r"$n_{\rm coll}$ per step / expected")
    ax1.legend(loc="upper right", fontsize=7)
    ax3.set_xlabel(r"lab $u_x$"); ax3.set_ylabel("density"); ax3.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(out, f"t11_drift_{a.tag}"))
    plt.close(fig)
    ok = [c for c in res["cases"].values() if not c.get("failed")]
    res["pass"] = bool(len(ok) == len(cases) and all(
        c.get("pass_a", True) and c.get("pass_b", True) and c.get("pass_c", True) for c in ok))
    bl.save_json(os.path.join(out, f"t11_{a.tag}.json"), res)
    print(json.dumps({n: {k: v for k, v in c.items() if k not in ("m_start", "m_end")}
                      for n, c in res["cases"].items()}, indent=1, default=float))
    print("pass", res["pass"])


if __name__ == "__main__":
    sys.exit(main())
