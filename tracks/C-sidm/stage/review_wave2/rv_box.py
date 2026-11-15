#!/usr/bin/env python3
"""Lead's recheck L8 of the box_tests package (wave 2) from its registered outputs.

Own readers and Maxwell-Juttner functions (rvlib.py). The track's references of
collide/REFERENCES/ are used only where TESTS.md names them (relax.dtheta_dt for T4).
T0b reruns the helper's own replay (box_tests/scripts/t0b.check) on the six registered
dumps: that is a rerun of the analysis, not an independent replay.
Output: $NRPIC_RUN_DIR/rv_box.json, rv_box.{png,pdf}.
"""
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

TR = os.path.join(rv.WT, "tracks", "C-sidm")
sys.path.insert(0, os.path.join(TR, "collide", "REFERENCES"))
sys.path.insert(0, os.path.join(rv.WT, "python"))

S = rv.SCR
R_T2 = os.path.join(S, "C-20261115-165500-c67e036")
R_T0B = os.path.join(S, "C-20261115-170155-13ff01f")
R_T10 = os.path.join(S, "C-20261115-165902-f9b1c8f")
R_T345 = os.path.join(S, "C-20261115-170539-28432c3")
R_T1L = os.path.join(S, "C-20261115-170741-248af65")
R_T9 = os.path.join(S, "C-20261115-170814-8a54b43")
R_T11 = os.path.join(S, "C-20261115-174651-0ad8612")


def t1_record(h):
    sw = h["sum_MW"]
    dE = np.abs(h["dE"]) / sw
    dP = np.max(np.abs(np.stack([h["dP1"], h["dP2"], h["dP3"]])), 0) / sw
    bound = 1e-14 * np.sqrt(h["n_coll"] + 1)
    return dict(max_dE_rel=float(dE.max()), max_dP_rel=float(dP.max()),
                max_ratio_to_bound=float(np.max(np.maximum(dE, dP) / bound)),
                n_trunc=float(h["n_trunc"].sum()), n_coll=float(h["n_coll"].sum()))


def t2():
    out = {}
    for name in sorted(os.listdir(R_T2)):
        rd = os.path.join(R_T2, name)
        if not (name.startswith("T2_") and os.path.isdir(rd)) or "_off_" in name:
            continue
        box = json.load(open(os.path.join(rd, "box.json")))
        _, dt = rv.wall_dt(rd)
        h = rv.read_hist(os.path.join(rd, "box.coll.hst"))
        sn = rv.snaps(rd)
        s0, s1 = rv.read_snap(sn[0]), rv.read_snap(sn[-1])
        W0 = np.sqrt(1 + np.sum(s0["u"] ** 2, 1))
        W1 = np.sqrt(1 + np.sum(s1["u"] ** 2, 1))
        th0, se0 = rv.theta_and_se(W0)
        th1, _ = rv.theta_and_se(W1)
        N = s0["n"]
        rho0 = float(s0["m"].sum()) / float(np.prod(box["box"]))
        expect = 0.5 * N * rho0 * box["sigma"] * rv.vmol(th0) * dt
        sp = h["sum_P"]
        mean, se = float(sp.mean()), float(sp.std(ddof=1) / math.sqrt(sp.size))
        za = float((h["n_coll"].sum() - sp.sum()) / math.sqrt(sp.sum()))
        e0, e1 = rv.fsum_mW(s0), rv.fsum_mW(s1)
        out[name] = dict(theta_nominal=box["theta"], theta_sample=th0, theta_end=th1,
                         theta_change=th1 / th0 - 1, steps=int(sp.size), dt=dt,
                         expect=expect, ratio=mean / expect, z_b=(mean - expect) / se,
                         ratio_nominal=mean / (0.5 * N * rho0 * box["sigma"]
                                               * rv.vmol(box["theta"]) * dt),
                         z_a=za, max_P=float(h["max_P"].max()),
                         mean_nsub=float(h["mean_nsub"].mean()),
                         max_nsub=float(h["max_nsub"].max()),
                         exact_sum_MW_equal=bool(e0 == e1), sum_MW_rel=(e1 - e0) / e0,
                         T1=t1_record(h))
        print(name, f"ratio {out[name]['ratio']:.6f} z_b {out[name]['z_b']:+.2f} z_a {za:+.2f}",
              flush=True)
    # processor cost: per step with collisions minus without, per tested pair
    cost = {}
    for th in ("0.1", "10.0"):
        off = os.path.join(R_T2, f"T2_th{th}_off_s1")
        w_off = json.load(open(os.path.join(off, "wall.json")))["wall"]
        for var in ("plain", "sub"):
            rd = os.path.join(R_T2, f"T2_th{th}_{var}_s1")
            w = json.load(open(os.path.join(rd, "wall.json")))["wall"]
            h = rv.read_hist(os.path.join(rd, "box.coll.hst"))
            cost[f"{th}_{var}"] = dict(wall=w, wall_off=w_off,
                                       s_per_pair=(w - w_off) / h["n_tested"].sum(),
                                       s_per_step=w / h["n_tested"].size,
                                       s_per_step_off=w_off / h["n_tested"].size)
    return out, cost


def t0b():
    sys.path.insert(0, os.path.join(TR, "box_tests", "scripts"))
    import t0b as T  # helper's driver: check() replays one registered dump
    res = {}
    for var, nx, f in (("plain", 4, 1), ("sub", 4, 1), ("f2", 8, 2)):
        for seed in (1, 2):
            name = f"T0b_{var}_s{seed}"
            o, best = T.check(os.path.join(R_T0B, name), nx, f)
            t = best[0]
            res[name] = dict(pass_=o["pass"], key_cycle=t["key_cycle"], n_tested=t["n_tested"],
                             n_coll=t["n_coll"], hst_n_tested=t.get("hst_n_tested"),
                             hst_n_coll=t.get("hst_n_coll"), sumP_rel=t.get("sumP_rel"),
                             max_du=t["max_du_collided"],
                             untouched=t["untouched_bit_identical"])
            print(name, res[name], flush=True)
    return res


def t10():
    ref = rv.read_snap(rv.snaps(os.path.join(R_T10, "mb1"))[-1])
    order = np.argsort(ref["tag"])
    res = dict(final_time=ref["t"], n=ref["n"])
    for v in ("mb8", "mb64", "rst0", "rst1", "rst2", "seed8"):
        rd = os.path.join(R_T10, v)
        sn = [p for p in rv.snaps(rd) if abs(rv.read_snap(p)["t"] - ref["t"]) < 1e-12]
        if not sn:
            res[v] = dict(missing=True)
            continue
        s = rv.read_snap(sn[-1])
        o = np.argsort(s["tag"])
        same_bytes = s["raw_records"] == ref["raw_records"]
        du = np.any(s["u"][o] != ref["u"][order], 1)
        dx = np.any(s["x"][o] != ref["x"][order], 1)
        res[v] = dict(bytes_identical=bool(same_bytes),
                      frac_particles_differing=float(np.mean(du | dx)))
    h1 = rv.read_hist(os.path.join(R_T10, "mb1", "box.coll.hst"))
    res["collisions_mb1"] = float(h1["n_coll"].sum())
    return res


def t345():
    import relax
    import mj as MJ
    res = {}
    for th in ("0.001", "1.0"):
        for seed in (1, 2):
            base = os.path.join(R_T345, f"T345_th{th}_s{seed}")
            snA = rv.snaps(base + "_A")
            snB = rv.snaps(base + "_B")
            sA = [rv.read_snap(p) for p in snA[:17]]
            s0 = sA[0]
            pop1 = s0["species"] == 0
            n1 = n2 = 0.5
            t1_0 = MJ.theta_from_kinetic(float(np.mean(np.sqrt(1 + np.sum(s0["u"][pop1] ** 2, 1)) - 1)))
            t2_0 = MJ.theta_from_kinetic(float(np.mean(np.sqrt(1 + np.sum(s0["u"][~pop1] ** 2, 1)) - 1)))
            d1, d2 = relax.dtheta_dt(n1, n2, 1.0, t1_0, t2_0)
            exact = d1 - d2
            tau = (t1_0 - t2_0) / abs(exact)
            ts, dth = [], []
            for s in sA:
                p1 = s["species"] == 0
                W = np.sqrt(1 + np.sum(s["u"] ** 2, 1))
                k1 = float(np.mean(W[p1] - 1))
                k2 = float(np.mean(W[~p1] - 1))
                ts.append(s["t"])
                dth.append(MJ.theta_from_kinetic(k1) - MJ.theta_from_kinetic(k2))
            ts, dth = np.array(ts), np.array(dth)
            fits = {}
            for lab, tmax in (("sample_tau", 0.15 * tau * (1 + 1e-9)),
                              ("design_tau_16pts", ts[15] * (1 + 1e-9))):
                sel = ts <= tmax
                X = np.vander(ts[sel], 3, increasing=True)
                coef, rss, *_ = np.linalg.lstsq(X, dth[sel], rcond=None)
                dof = sel.sum() - 3
                s2 = float(rss[0]) / dof
                cov = s2 * np.linalg.inv(X.T @ X)
                fits[lab] = dict(npts=int(sel.sum()), slope=float(coef[1]),
                                 se=float(math.sqrt(cov[1, 1])), ratio=float(coef[1] / exact),
                                 ratio_se=float(math.sqrt(cov[1, 1]) / abs(exact)))
            send = rv.read_snap(snB[-1])
            Wend = np.sqrt(1 + np.sum(send["u"] ** 2, 1))
            th_eq = relax.theta_eq(n1, n2, t1_0, t2_0)
            cdf = rv.mj_speed_cdf(th_eq)
            ks = stats.kstest(np.sqrt(np.sum(send["u"] ** 2, 1)), cdf)
            e0, e1 = rv.fsum_mW(s0), rv.fsum_mW(send)
            res[f"{th}_s{seed}"] = dict(theta1_0=t1_0, theta2_0=t2_0, exact_slope=exact,
                                        tau_rel=tau, fits=fits, t_end_over_tau=send["t"] / tau,
                                        theta_end=rv.theta_from_W(float(Wend.mean())),
                                        theta_eq=th_eq, ks_p=float(ks.pvalue),
                                        exact_sum_MW_equal=bool(e0 == e1))
            print(th, seed, fits, ks.pvalue, flush=True)
    return res


def t1long():
    res = {}
    for seed in (1, 2):
        rd = os.path.join(R_T1L, f"T1long_s{seed}")
        sn = rv.snaps(rd)
        e = [rv.fsum_mW(rv.read_snap(p)) for p in sn]
        h = rv.read_hist(os.path.join(rd, "box.coll.hst"))
        res[f"s{seed}"] = dict(n_snap=len(sn), all_equal=bool(all(x == e[0] for x in e)),
                               steps=int(h["n_coll"].size), T1=t1_record(h))
    return res


def t9():
    res, drifts = {}, []
    for seed in range(1, 9):
        rd = os.path.join(R_T9, f"T9_s{seed}")
        sn = rv.snaps(rd)
        s0, s1 = rv.read_snap(sn[0]), rv.read_snap(sn[-1])
        m = s1["m"]
        light = m < 0.5 * (m.min() + m.max())
        W = np.sqrt(1 + np.sum(s1["u"] ** 2, 1))
        thA, seA = rv.theta_and_se(W[light])
        thB, seB = rv.theta_and_se(W[~light])
        W0 = np.sqrt(1 + np.sum(s0["u"] ** 2, 1))
        ekin0 = math.fsum((s0["m"] * (W0 - 1)).tolist())
        dE = (rv.fsum_mW(s1) - rv.fsum_mW(s0)) / ekin0
        drifts.append(dE)
        res[f"s{seed}"] = dict(theta_A=thA, theta_B=thB, z=(thA - thB) / math.hypot(seA, seB),
                               dE_over_Ekin=dE, rest_mass_equal=bool(math.fsum(s0["m"].tolist())
                                                                    == math.fsum(m.tolist())))
    d = np.array(drifts)
    res["energy_drift_mean"] = float(d.mean())
    res["energy_drift_se"] = float(d.std(ddof=1) / math.sqrt(d.size))
    res["energy_drift_z"] = res["energy_drift_mean"] / res["energy_drift_se"]
    return res


def t11():
    res = {}
    for name in ("T11ab_s1", "T11ab_s2", "T11c_s1", "T11c_s2"):
        h = rv.read_hist(os.path.join(R_T11, name, "box.coll.hst"))
        res[name] = dict(n_coll=float(h["n_coll"].sum()), sum_P=float(h["sum_P"].sum()),
                         z=float((h["n_coll"].sum() - h["sum_P"].sum()) / math.sqrt(h["sum_P"].sum())),
                         T1=t1_record(h))
    return res


def figure(r, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH * 1.25, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.2, top=0.88, wspace=0.42)
    t2r = r["T2"]
    for i, (k, v) in enumerate(sorted(t2r.items(), key=lambda kv: (kv[1]["theta_nominal"], kv[0]))):
        c = fs.PAL["blue"] if "plain" in k else fs.PAL["red"]
        mk = "o" if k.endswith("s1") else "s"
        se = (v["ratio"] - 1) / v["z_b"] if v["z_b"] != 0 else 0
        ax[0].errorbar(v["theta_nominal"] * (1.08 if "sub" in k else 0.93), v["ratio"] - 1,
                       yerr=abs(se), fmt=mk, color=c, ms=4, mfc="none" if "s2" in k else c)
        ax[1].plot(v["theta_nominal"] * (1.08 if "sub" in k else 0.93), v["z_a"], mk, color=c,
                   ms=4, mfc="none" if "s2" in k else c)
    for a in ax[:2]:
        a.set_xscale("log")
        a.set_xlabel(r"$\theta$ (nominal)")
    ax[0].axhline(0, **fs.GUIDE)
    ax[0].set_ylabel(r"$\langle\Sigma P\rangle/\mathrm{expect.}-1$")
    ax[0].set_title("T2(b) rate (blue plain, red sub)", fontsize=8)
    ax[1].axhspan(-4, 4, color="0.9")
    ax[1].axhline(0, **fs.GUIDE)
    ax[1].set_ylabel(r"$z$ (accepted vs $\Sigma P$)")
    ax[1].set_title("T2(a) counts", fontsize=8)
    lab = []
    for i, (k, v) in enumerate(sorted(r["T345"].items())):
        f = v["fits"]["sample_tau"]
        ax[2].errorbar(i, f["ratio"], yerr=f["ratio_se"], fmt="o", color=fs.PAL["blue"], ms=4)
        lab.append(k.replace("_", "\n"))
    ax[2].axhline(1.0, **fs.GUIDE)
    ax[2].axhline(1.0025, color="0.5", lw=1, ls=":")
    ax[2].set_xticks(range(len(lab)))
    ax[2].set_xticklabels(lab, fontsize=7)
    ax[2].set_ylabel("T4 slope / exact")
    ax[2].set_title(r"T4 (quadratic fit, $0.15\,\tau_{\rm rel}$)", fontsize=8)
    zs = [r["T9"][f"s{s}"]["z"] for s in range(1, 9)]
    de = [100 * r["T9"][f"s{s}"]["dE_over_Ekin"] for s in range(1, 9)]
    ax[3].plot(range(1, 9), zs, "o", color=fs.PAL["blue"], ms=4, label=r"$z(\theta_A-\theta_B)$")
    ax[3].plot(range(1, 9), de, "s", color=fs.PAL["red"], ms=4, label=r"$100\,\Delta E/E_{\rm kin}$")
    ax[3].axhspan(-4, 4, color="0.92")
    ax[3].axhline(0, **fs.GUIDE)
    ax[3].set_xlabel("seed")
    ax[3].set_title("T9 nanbu, end state", fontsize=8)
    ax[3].legend(fontsize=7, frameon=False, loc="upper left")
    fs.save(fig, os.path.join(out, "rv_box"))


def main():
    out = rv.outdir()
    r = {}
    r["T2"], r["cost"] = t2()
    r["T1long"] = t1long()
    r["T10"] = t10()
    r["T9"] = t9()
    r["T11"] = t11()
    r["T345"] = t345()
    r["T0b"] = t0b()
    json.dump(r, open(os.path.join(out, "rv_box.json"), "w"), indent=1)
    figure(r, out)
    print("done", out)


if __name__ == "__main__":
    main()
