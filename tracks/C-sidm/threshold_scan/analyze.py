#!/usr/bin/env python3
"""Analysis of the first collisional cluster runs CC1/CC2 (card batches of nrpic-run) against
the predictions of predict.py (run C-20261115-170404-af74c6d) and JOURNAL.md entry 3.

    python3 analyze.py [--out DIR] RUN_ID [RUN_ID ...]

Each RUN_ID is a batch run of nrpic-run; its subdirectories cc1_kninf, cc1_kn10, ... are
the AthenaK runs. Read: <name>/cc.nrpic.hst, cc.coll.hst, cc.part.*.bin, cc.traj.bin,
cc.trajmet.bin, cc.z4c.user.hst, athena.log. Writes summary.json and fig_cc_*.png.
"""
import argparse
import glob
import json
import os
import re
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

PRED_RUN = "C-20261115-170404-af74c6d"
EPS = 2.0 ** -52
FRACS = (0.1, 0.5, 0.9)


def find_runs(run_ids):
    found = {}
    for rid in run_ids:
        for d in sorted(glob.glob(os.path.join(C.SCRATCH, rid, "cc*_kn*"))):
            if os.path.isfile(os.path.join(d, "cc.nrpic.hst")):
                found[os.path.basename(d)] = d
    return found


def wall_of(d):
    """Wall seconds and cycles from the AthenaK log (cpu time used, last cycle)."""
    logs = sorted(glob.glob(os.path.join(d, "athena.*.log")))
    if not logs:
        return None, None
    txt = open(logs[-1]).read()
    m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    c = re.findall(r"cycle=(\d+)", txt)
    return (float(m.group(1)) if m else None), (int(c[-1]) if c else None)


def mass_radii(snap):
    r = np.sort(np.linalg.norm(snap["x"], axis=1))
    return [float(r[int(f * len(r))]) for f in FRACS]


def analyse_run(name, d, pred, model):
    meta = model["meta"]
    E0 = meta["E0"]
    out = dict(dir=d)
    h = C.read_hst(os.path.join(d, "cc.nrpic.hst"))
    t = h["time"]
    out["t_end"] = float(t[-1])
    out["np_end"] = int(h["np"][-1])
    out["rest_mass_identical"] = bool(np.all(h["sum_m"] == h["sum_m"][0]))
    out["rest_mass_budget"] = float(np.max(np.abs(h["sum_m"] + h["m_excised"] + h["m_escaped"]
                                                  - h["sum_m"][0])))
    out["n_excised"] = int(h["n_excised"][-1])
    out["n_escaped"] = int(h["n_escaped"][-1])
    out["deposit_identity"] = float(np.max(np.abs(h["int_E"] - h["sum_mW"]) / h["sum_mW"]))
    out["push_unconverged"] = int(np.sum(h["push_unconverged"])) if "push_unconverged" in h else None
    a_eq = meta["alpha_c"]
    ap = h["alpha_probe"]
    out["alpha_c_eq"] = a_eq
    out["alpha_c_start"] = float(ap[0])
    out["alpha_c_end"] = float(ap[-1])
    out["alpha_c_min"] = float(ap.min())
    out["alpha_c_max"] = float(ap.max())
    late = t >= t[-1] - 50.0
    out["alpha_c_mean_last50"] = float(np.mean(ap[late]))
    out["alpha_min_grid"] = float(h["alpha_min"].min())
    mW = h["sum_mW"] / h["sum_m"]
    out["mean_lorentz_max_change"] = float(np.max(np.abs(mW - mW[0])))
    wall, cyc = wall_of(d)
    out["wall_s"] = wall
    out["cycles"] = cyc
    out["s_per_M"] = (wall / t[-1]) if wall and t[-1] > 0 else None
    zh = os.path.join(d, "cc.z4c.user.hst")
    if os.path.exists(zh):
        z = C.read_hst(zh)
        out["H_norm2_start_end"] = [float(z["H-norm2"][0]), float(z["H-norm2"][-1])]
    # snapshots: mass radii, matter far out
    snaps = sorted(glob.glob(os.path.join(d, "cc.part.*.bin")))
    ts, rr, far = [], [], []
    rs = meta["rbar_s"]
    for p in snaps:
        s = C.read_snapshot(p)
        ts.append(s["time"])
        rr.append(mass_radii(s))
        far.append(float(np.sum(s["m"][np.linalg.norm(s["x"], axis=1) > 2.0 * rs]) / np.sum(s["m"])))
    ts, rr, far = np.array(ts), np.array(rr), np.array(far)
    out["radii_t"] = ts.tolist()
    out["radii"] = rr.tolist()
    out["radii_range_rel"] = [float((rr[:, j].max() - rr[:, j].min()) / rr[0, j]) for j in range(3)]
    out["radii_end_rel"] = [float(rr[-1, j] / rr[0, j] - 1.0) for j in range(3)]
    out["mass_frac_beyond_2rs"] = far.tolist()
    # trajectories with the metric: Killing energies
    tj, tm = os.path.join(d, "cc.traj.bin"), os.path.join(d, "cc.trajmet.bin")
    ek_t, ek_sum, f_e0, f_unb, hist_e = [], [], [], [], {}
    if os.path.exists(tj) and os.path.exists(tm):
        recs = C.read_traj(tj, tm)
        Mp = float(model["m"][0])
        for k, rec in enumerate(recs):
            EK, W = C.killing_energy(rec)
            ek_t.append(rec["time"])
            ek_sum.append(float(Mp * np.sum(EK)))
            f_e0.append(float(np.mean(EK > E0)))
            f_unb.append(float(np.mean(EK > 1.0)))
            if k == 0 or k == len(recs) - 1:
                hist_e[f"{rec['time']:g}"] = EK / E0
    out["EK_t"] = ek_t
    out["EK_sum"] = ek_sum
    out["EK_frac_above_E0"] = f_e0
    out["EK_frac_unbound"] = f_unb
    if ek_sum:
        out["EK_sum_change"] = float(ek_sum[-1] - ek_sum[0])
    series = dict(t=t, ap=ap, ts=ts, rr=rr, far=far, ek_t=np.array(ek_t), ek_sum=np.array(ek_sum),
                  f_e0=np.array(f_e0), f_unb=np.array(f_unb), hist_e=hist_e)
    # collisions
    ch = os.path.join(d, "cc.coll.hst")
    if os.path.exists(ch):
        c = C.read_hst(ch)
        p = pred["runs"][name]
        nc = c["n_coll"]
        ntot, ptot = float(nc.sum()), float(c["sum_P"].sum())
        Mp = float(model["m"][0])
        k1 = int(np.argmin(c["ncycle"]))
        out.update(
            coll_records=int(len(nc)), coll_cycles_first_last=[int(c["ncycle"][0]), int(c["ncycle"][-1])],
            collisions=ntot, sum_P=ptot, count_z=float((ntot - ptot) / np.sqrt(max(ptot, 1e-300))),
            collisions_pred_constant_rate=p["collisions_300M_constant_rate"] * t[-1] / 300.0,
            collisions_rel_to_pred=float(ntot / (p["collisions_300M_constant_rate"] * t[-1] / 300.0)),
            sumP_step1=float(c["sum_P"][k1]), sumP_step1_pred=p["sumP_step1_expected"],
            sumP_step1_sd=p["sumP_step1_pairing_sd"],
            n_trunc=int(c["n_trunc"].sum()), max_P=float(c["max_P"].max()),
            max_nsub=int(c["max_nsub"].max()), mean_nsub=float(np.mean(c["mean_nsub"])),
            n_bad_cells=int(c["n_bad_cells"].max()), mean_N=float(np.mean(c["mean_N"])),
            max_dx_mfp=float(c["max_dx_mfp"].max()), n_part_min=int(c["n_part"].min()),
            pair_dE_eps=float(np.max(c["abs_dE"] / np.maximum(nc, 1.0)) / (EPS * 2.0 * Mp)),
            pair_dE_sum_rel=float(np.abs(c["dE"].sum()) / c["sum_MW"][0]),
            dP_sum=float(np.max(np.abs([c["dP1"].sum(), c["dP2"].sum(), c["dP3"].sum()]))),
            dE_particles_sum_rel=float(c["dE_particles"].sum() / c["sum_MW_particles"][0]),
            dE_particles_pred_rel=p["dE_particles_per_collision_rel"] * ntot,
            dE_particles_per_collision_rel=float(c["dE_particles"].sum() / c["sum_MW_particles"][0]
                                                 / max(ntot, 1.0)),
            dE_particles_per_collision_pred=p["dE_particles_per_collision_rel"],
            tail_E0_pred_linear=p["tail_E0_per_collision"] * ntot / len(model["m"]),
            unbound_pred_linear=p["unbound_per_collision"] * ntot / len(model["m"]))
        # the two histories describe the same energy: sum_MW_particles of coll.hst after the
        # collision step of cycle n and sum_mW of nrpic.hst at the end of cycle n
        cyc_h = h["ncycle"].astype(int)
        idx = {n: i for i, n in enumerate(cyc_h)}
        pairs = [(idx[int(n)], i) for i, n in enumerate(c["ncycle"]) if int(n) in idx]
        if pairs:
            ih, ic = np.array(pairs).T
            out["hist_consistency_rel"] = float(np.max(np.abs(c["sum_MW_particles"][ic] - h["sum_mW"][ih])
                                                       / h["sum_mW"][0]))
            out["hist_consistency_cycle_offset"] = 0
            # if the records are offset by one cycle, report that too
            pairs1 = [(idx[int(n) + 1], i) for i, n in enumerate(c["ncycle"]) if int(n) + 1 in idx]
            if pairs1:
                ih1, ic1 = np.array(pairs1).T
                out["hist_consistency_rel_offset1"] = float(
                    np.max(np.abs(c["sum_MW_particles"][ic1] - h["sum_mW"][ih1]) / h["sum_mW"][0]))
        series.update(ct=c["time"], ncum=np.cumsum(nc), pcum=np.cumsum(c["sum_P"]), sumP=c["sum_P"],
                      dEp=np.cumsum(c["dE_particles"]) / c["sum_MW_particles"][0],
                      pair_eps=c["abs_dE"] / np.maximum(nc, 1.0) / (EPS * 2.0 * Mp), nc=nc)
    return out, series


def smooth(y, n):
    if len(y) < n:
        return y
    k = np.ones(n) / n
    return np.convolve(y, k, mode="same")


def figures(outdir, res, ser, pred):
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    col = {"inf": "k", "10": fs.PAL["blue"], "1": fs.PAL["red"]}
    lab = {"inf": r"Kn = $\infty$", "10": "Kn = 10", "1": "Kn = 1"}

    def kn_of(name):
        return name.split("_kn")[1]

    # F1: central lapse and mass radii
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.96, wspace=0.25, hspace=0.08)
    for row, mk in enumerate(("cc1", "cc2")):
        for name, s in ser.items():
            if not name.startswith(mk):
                continue
            k = kn_of(name)
            axs[row, 0].plot(s["t"], s["ap"] - res[name]["alpha_c_eq"], color=col[k], lw=1.0,
                             label=lab[k])
            for j, ls in zip(range(3), (":", "-", "--")):
                axs[row, 1].plot(s["ts"], s["rr"][:, j] / s["rr"][0, j], color=col[k], ls=ls, lw=1.2,
                                 label=lab[k] if j == 1 else None)
        axs[row, 0].axhline(0.0, **fs.MASK_LINE)
        axs[row, 0].set_ylabel(r"$\alpha_c - \alpha_{c,\rm eq}$" + f"  ({mk.upper()})")
        axs[row, 1].set_ylabel(r"$r_{10}, r_{50}, r_{90}$ over initial" + f"  ({mk.upper()})")
        axs[row, 0].legend(fontsize=8, ncol=3, loc="lower left")
    for ax in axs[1]:
        ax.set_xlabel(r"$t/M$")
    fig.savefig(os.path.join(outdir, "fig_cc_lapse_radii.png"), dpi=200)
    plt.close(fig)

    # F2: collisions
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.38)
    for name, s in ser.items():
        if "ncum" not in s:
            continue
        k = kn_of(name)
        mk = name[:3]
        ls = "-" if mk == "cc1" else "--"
        p = pred[mk]["runs"][name]
        axs[0].plot(s["ct"], s["ncum"], color=col[k], ls=ls, label=f"{mk.upper()} {lab[k]}")
        axs[0].plot(s["ct"], p["collisions_300M_constant_rate"] * s["ct"] / 300.0, color="k", lw=1.0, ls=":")
        axs[1].plot(s["ct"], smooth(s["sumP"], 64) / p["sumP_step1_expected"], color=col[k], ls=ls)
        axs[2].plot(s["ct"], (s["ncum"] - s["pcum"]) / np.sqrt(np.maximum(s["pcum"], 1.0)),
                    color=col[k], ls=ls)
    axs[0].set_yscale("log")
    axs[0].set_ylim(10, None)
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel("collisions (cumulative)")
    axs[0].legend(fontsize=7, loc="lower right")
    axs[1].axhline(1.0, **fs.GUIDE)
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"sum$_P$ per step / predicted (4 M mean)")
    for v in (-2, 2):
        axs[2].axhline(v, **fs.MASK_LINE)
    axs[2].set_xlabel(r"$t/M$")
    axs[2].set_ylabel(r"(collisions $-$ $\Sigma$sum$_P$)/$\sqrt{\Sigma{\rm sum}_P}$")
    fig.savefig(os.path.join(outdir, "fig_cc_collisions.png"), dpi=200)
    plt.close(fig)

    # F3: budgets
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.95, wspace=0.42)
    for name, s in ser.items():
        k = kn_of(name)
        mk = name[:3]
        ls = "-" if mk == "cc1" else "--"
        if len(s["ek_t"]):
            axs[2].plot(s["ek_t"], s["ek_sum"] - s["ek_sum"][0], color=col[k], ls=ls, marker=".",
                        label=f"{mk.upper()} {lab[k]}")
        if "dEp" not in s:
            continue
        p = pred[mk]["runs"][name]
        axs[0].plot(s["ct"], s["dEp"], color=col[k], ls=ls, label=f"{mk.upper()} {lab[k]}")
        axs[0].plot(s["ct"], p["dE_particles_per_collision_rel"] * s["ncum"], color="k", lw=1.0, ls=":")
        axs[1].plot(s["ct"][s["nc"] > 0], s["pair_eps"][s["nc"] > 0], ".", ms=1.0, color=col[k],
                    alpha=0.3)
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"$\Sigma\,\Delta(\Sigma MW)_{\rm coll}/\Sigma MW$")
    axs[0].legend(fontsize=7, loc="upper left")
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"cell-frame $|\Delta E|$ per collision / ($2M_p\epsilon$)")
    axs[2].axhline(0.0, **fs.MASK_LINE)
    axs[2].set_xlabel(r"$t/M$")
    axs[2].set_ylabel(r"$\Sigma M E_K - $ initial  $[M]$")
    axs[2].legend(fontsize=7, loc="upper left")
    fig.savefig(os.path.join(outdir, "fig_cc_budget.png"), dpi=200)
    plt.close(fig)

    # F4: energy tail and evaporation
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.38)
    for name, s in ser.items():
        k = kn_of(name)
        mk = name[:3]
        ls = "-" if mk == "cc1" else "--"
        if len(s["ek_t"]):
            axs[0].plot(s["ek_t"], s["f_e0"], color=col[k], ls=ls, marker=".",
                        label=f"{mk.upper()} {lab[k]}")
            axs[1].plot(s["ek_t"], s["f_unb"], color=col[k], ls=ls, marker=".")
        if "ncum" in s:
            p = pred[mk]["runs"][name]
            nn = s["ncum"]
            axs[0].plot(s["ct"], np.minimum(p["tail_E0_per_collision"] * nn / 1e5, 1), color="k", lw=1.0, ls=":")
            axs[1].plot(s["ct"], p["unbound_per_collision"] * nn / 1e5, color="k", lw=1.0, ls=":")
        if mk == "cc1":
            for tk, e in s["hist_e"].items():
                if float(tk) > 0:
                    axs[2].hist(e, bins=np.linspace(0.7, 1.25, 111), histtype="step", color=col[k],
                                density=True, lw=1.0, label=lab[k])
                elif k == "inf":
                    axs[2].hist(e, bins=np.linspace(0.7, 1.25, 111), histtype="step",
                                color="grey", density=True, lw=1.0, label=r"$t=0$")
    axs[0].set_yscale("log")
    axs[1].set_yscale("log")
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"fraction with $E_K > E_0$")
    axs[0].legend(fontsize=7, loc="lower right")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"fraction with $E_K > 1$")
    axs[2].axvline(1.0, **fs.GUIDE)
    axs[2].set_yscale("log")
    axs[2].set_xlabel(r"$E_K/E_0$ (CC1, end of run)")
    axs[2].set_ylabel("density")
    axs[2].legend(fontsize=7, loc="upper right")
    fig.savefig(os.path.join(outdir, "fig_cc_energy_tail.png"), dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_ids", nargs="+")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    pred = json.load(open(os.path.join(C.SCRATCH, PRED_RUN, "predictions.json")))
    runs = find_runs(a.run_ids)
    models = {mk: C.load_model(C.MODELS[mk]["tag"]) for mk in C.MODELS}
    res, ser = {}, {}
    for name, d in runs.items():
        mk = name[:3]
        res[name], ser[name] = analyse_run(name, d, pred[mk], models[mk])
        print(name, json.dumps({k: v for k, v in res[name].items()
                                if not isinstance(v, (list, dict))}), flush=True)
    res["_inputs"] = dict(run_ids=a.run_ids, predictions=PRED_RUN, ic_run=C.IC_RUN)
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    figures(a.out, res, ser, pred)
    return 0


if __name__ == "__main__":
    sys.exit(main())
