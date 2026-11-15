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
    logs = sorted(glob.glob(os.path.join(d, "athena.*.log"))) or \
        sorted(glob.glob(os.path.join(d, "athena.log")))
    if not logs:
        return None, None
    txt = open(logs[-1]).read()
    m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    c = re.findall(r"cycle=(\d+)", txt)
    return (float(m.group(1)) if m else None), (int(c[-1]) if c else None)


def mass_radii(snap, m_total, m_removed):
    """Radii enclosing the fractions FRACS of the initial rest mass, the mass removed by
    excision counted at r = 0 (nan if a fraction lies inside the removed mass)."""
    r = np.linalg.norm(snap["x"], axis=1)
    o = np.argsort(r)
    cm = m_removed + np.cumsum(snap["m"][o])
    out = []
    for f in FRACS:
        k = int(np.searchsorted(cm, f * m_total))
        out.append(float(r[o][k]) if f * m_total > m_removed and k < len(r) else float("nan"))
    return out


def analyse_run(name, d, pred, model):
    meta = model["meta"]
    E0 = meta["E0"]
    out = dict(dir=d)
    h = C.read_hst(os.path.join(d, "cc.nrpic.hst"))
    t = h["time"]
    out["t_end"] = float(t[-1])
    out["np_end"] = int(h["np"][-1])
    M0 = float(h["sum_m"][0])
    out["rest_mass_identical"] = bool(np.all(h["sum_m"] == h["sum_m"][0]))
    noexc = h["n_excised"] == 0
    out["rest_mass_identical_before_excision"] = bool(np.all(h["sum_m"][noexc] == h["sum_m"][0]))
    out["rest_mass_budget_rel"] = float(np.max(np.abs(h["sum_m"] + h["m_excised"] + h["m_escaped"]
                                                      - h["sum_m"][0])) / M0)
    exc = np.flatnonzero(h["n_excised"] > 0)
    out["t_first_excision"] = float(t[exc[0]]) if len(exc) else None
    low = np.flatnonzero(h["alpha_min"] < 0.3)
    out["t_alpha_min_below_0p3"] = float(t[low[0]]) if len(low) else None
    out["excised_mass_fraction_end"] = float(h["m_excised"][-1] / M0)
    for tt in (100.0, 200.0, 300.0):
        k = int(np.argmin(np.abs(t - tt)))
        out[f"excised_mass_fraction_t{tt:g}"] = float(h["m_excised"][k] / M0)
    t_c = out["t_alpha_min_below_0p3"] if out["t_alpha_min_below_0p3"] is not None else float(t[-1])
    out["t_collapse_or_end"] = t_c
    # the state turns non-finite after a collapse on this static mesh (alpha_probe NaN, every
    # remaining particle removed in one step, the run still exits with status 0)
    bad = np.flatnonzero(~np.isfinite(h["alpha_probe"]) | (h["alpha_min"] > 1e300))
    out["t_nonfinite"] = float(t[bad[0]]) if len(bad) else None
    if len(exc):
        t_e = float(t[exc[0]])
        for dt_ in (10.0, 20.0, 50.0):
            k = int(np.argmin(np.abs(t - (t_e + dt_))))
            ok = out["t_nonfinite"] is None or t[k] < out["t_nonfinite"]
            out[f"excised_fraction_first_excision_plus{dt_:g}M"] = float(h["m_excised"][k] / M0) if ok else None
    zh_ = os.path.join(d, "cc.z4c.user.hst")
    if os.path.exists(zh_):
        z_ = C.read_hst(zh_)
        for tt in (0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0):
            k = int(np.argmin(np.abs(z_["time"] - tt)))
            out[f"H_norm2_t{tt:g}"] = float(z_["H-norm2"][k])
    out["n_excised"] = int(h["n_excised"][-1])
    out["n_escaped"] = int(h["n_escaped"][-1])
    live = h["sum_mW"] > 0
    out["deposit_identity"] = float(np.max(np.abs(h["int_E"][live] - h["sum_mW"][live]) / h["sum_mW"][live]))
    out["np_zero_from"] = float(t[np.flatnonzero(h["np"] == 0)[0]]) if np.any(h["np"] == 0) else None
    out["push_unconverged"] = int(np.sum(h["push_unconverged"])) if "push_unconverged" in h else None
    a_eq = meta["alpha_c"]
    ap = h["alpha_probe"]
    out["alpha_c_eq"] = a_eq
    out["alpha_c_start"] = float(ap[0])
    out["alpha_c_end"] = float(ap[-1])
    out["alpha_c_min"] = float(np.nanmin(ap))
    out["alpha_c_max"] = float(np.nanmax(ap))
    late = t >= t[-1] - 50.0
    out["alpha_c_mean_last50"] = float(np.nanmean(ap[late]))
    # the probe interpolates the eight cell centres around the origin, so alpha_c(0) is
    # above the model's central lapse; changes are measured from alpha_c(0)
    out["alpha_c_max_dev_from_start"] = float(np.nanmax(np.abs(ap - ap[0])))
    out["alpha_min_grid"] = float(h["alpha_min"].min())
    mW = np.where(live, h["sum_mW"] / np.where(live, h["sum_m"], 1.0), np.nan)
    pre = t <= t_c
    out["mean_lorentz_max_change_before_collapse"] = float(np.max(np.abs(mW[pre] - mW[0])))
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
        k = int(np.argmin(np.abs(t - s["time"])))
        rr.append(mass_radii(s, M0, float(h["m_excised"][k])))
        far.append(float(np.sum(s["m"][np.linalg.norm(s["x"], axis=1) > 2.0 * rs]) / M0))
    ts, rr, far = np.array(ts), np.array(rr).reshape(-1, 3), np.array(far)
    out["radii_t"] = ts.tolist()
    out["radii"] = rr.tolist()
    if len(rr):
        pre_s = ts <= t_c
        out["radii_range_rel_before_collapse"] = [
            float((np.nanmax(rr[pre_s, j]) - np.nanmin(rr[pre_s, j])) / rr[0, j]) for j in range(3)]
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
            f_e0.append(float(np.sum(EK > E0) / len(model["m"])))
            f_unb.append(float(np.sum(EK > 1.0) / len(model["m"])))
            if k == 0:
                hist_e["0"] = EK / E0
            if rec["time"] <= t_c:
                hist_e["last"] = (rec["time"], EK / E0)
    out["EK_t"] = ek_t
    out["EK_sum"] = ek_sum
    out["EK_frac_above_E0"] = f_e0
    out["EK_frac_unbound"] = f_unb
    if ek_sum:
        kpre = [i for i, tt in enumerate(ek_t) if tt <= t_c]
        out["EK_sum_change_before_collapse"] = float(ek_sum[kpre[-1]] - ek_sum[0])
        out["EK_sum_max_dev_before_collapse"] = float(max(abs(ek_sum[i] - ek_sum[0]) for i in kpre))
        out["EK_frac_above_E0_at_collapse_or_end"] = f_e0[kpre[-1]]
        out["EK_frac_unbound_at_collapse_or_end"] = f_unb[kpre[-1]]
        out["EK_t_at_collapse_or_end"] = ek_t[kpre[-1]]
    series = dict(t=t, ap=ap, ts=ts, rr=rr, far=far, mexc=h["m_excised"] / M0, amin=h["alpha_min"], t_c=t_c, ek_t=np.array(ek_t), ek_sum=np.array(ek_sum),
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
        pc = c["time"] <= t_c
        n_pre = float(nc[pc].sum())
        out.update(collisions_before_collapse=n_pre,
                   collisions_before_collapse_rel_to_pred=float(
                       n_pre / (p["collisions_300M_constant_rate"] * t_c / 300.0)),
                   count_z_before_collapse=float((n_pre - c["sum_P"][pc].sum())
                                                 / np.sqrt(max(c["sum_P"][pc].sum(), 1e-300))),
                   dE_particles_before_collapse_rel=float(c["dE_particles"][pc].sum()
                                                          / c["sum_MW_particles"][0]),
                   dE_particles_per_collision_before_collapse=float(
                       c["dE_particles"][pc].sum() / c["sum_MW_particles"][0] / max(n_pre, 1.0)),
                   n_bad_cells_total=int(c["n_bad_cells"].sum()))
        # scatter of the defect of one collision, from the per-step sums of the first 25 M
        # (var of a step's sum = n var(one) for independent collisions)
        w25 = (c["time"] <= 25.0) & (nc > 0)
        e1 = c["dE_particles"][w25] / c["sum_MW_particles"][0]
        sd1 = float(np.sqrt(np.mean(e1 ** 2 / nc[w25]))) if np.any(w25) else float("nan")
        out["dE_particles_sd_one_collision"] = sd1
        for tw in (25.0, 50.0):
            w = c["time"] <= tw
            nw = float(nc[w].sum())
            out[f"collisions_first{tw:g}M_rel_to_pred"] = float(
                nw / (p["collisions_300M_constant_rate"] * tw / 300.0))
            out[f"dE_particles_per_collision_first{tw:g}M"] = float(
                c["dE_particles"][w].sum() / c["sum_MW_particles"][0] / max(nw, 1.0))
            out[f"dE_particles_per_collision_first{tw:g}M_se"] = float(sd1 / np.sqrt(max(nw, 1.0)))
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
            dE_particles_sum_rel=float(np.nansum(c["dE_particles"]) / c["sum_MW_particles"][0]),
            dE_particles_pred_rel=p["dE_particles_per_collision_rel"] * ntot,
            dE_particles_per_collision_rel=float(np.nansum(c["dE_particles"]) / c["sum_MW_particles"][0]
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
            ok = h["sum_mW"][ih] > 0
            ih, ic = ih[ok], ic[ok]
            out["hist_consistency_rel"] = float(np.max(np.abs(c["sum_MW_particles"][ic] - h["sum_mW"][ih])
                                                       / h["sum_mW"][0]))
            out["hist_consistency_cycle_offset"] = 0
            # if the records are offset by one cycle, report that too
            pairs1 = [(idx[int(n) + 1], i) for i, n in enumerate(c["ncycle"]) if int(n) + 1 in idx]
            if pairs1:
                ih1, ic1 = np.array(pairs1).T
                ok1 = h["sum_mW"][ih1] > 0
                ih1, ic1 = ih1[ok1], ic1[ok1]
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

    # F1: central lapse, mass radii, mass removed by excision
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.96, wspace=0.32, hspace=0.08)
    for row, mk in enumerate(("cc1", "cc2")):
        for name, s in ser.items():
            if not name.startswith(mk):
                continue
            k = kn_of(name)
            axs[row, 0].plot(s["t"], s["ap"], color=col[k], lw=1.0, label=lab[k])
            for j, ls in zip(range(3 if len(s["rr"]) else 0), (":", "-", "--")):
                axs[row, 1].plot(s["ts"], s["rr"][:, j] / s["rr"][0, j], color=col[k], ls=ls, lw=1.2,
                                 label=lab[k] if j == 1 else None)
            good = s["t"] < (res[name]["t_nonfinite"] if res[name]["t_nonfinite"] else 1e30)
            axs[row, 2].plot(s["t"][good], s["mexc"][good], color=col[k], lw=1.2, label=lab[k])
            if res[name]["t_nonfinite"]:
                axs[row, 2].axvline(res[name]["t_nonfinite"], color=col[k], lw=1.0, ls=":")
        axs[row, 0].axhline(0.1, **fs.MASK_LINE)
        axs[row, 0].set_ylabel(r"central lapse $\alpha_c$" + f"  ({mk.upper()})")
        axs[row, 1].set_ylabel(r"$r_{10}, r_{50}, r_{90}$ / initial" + f"  ({mk.upper()})")
        axs[row, 2].set_ylabel("rest mass excised / $M_0$" + f"  ({mk.upper()})")
        axs[row, 2].text(0.03, 0.03, "dotted: state non-finite", transform=axs[row, 2].transAxes,
                         fontsize=7)
        axs[row, 0].legend(fontsize=8, loc="center left")
        axs[row, 1].set_ylim(0.0, 2.0)
        axs[row, 2].set_ylim(-0.02, 1.0)
    for ax in axs[1]:
        ax.set_xlabel(r"$t/M$")
    fig.savefig(os.path.join(outdir, "fig_cc_lapse_radii.png"), dpi=200)
    plt.close(fig)

    # F1b: the controls in detail (alpha_c offset from its start)
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.15, top=0.95)
    for name, s in ser.items():
        if name.endswith("kninf"):
            ax.plot(s["t"], s["ap"] - s["ap"][0], color=fs.PAL["red"] if name.startswith("cc1")
                    else fs.PAL["blue"], lw=1.0, label=name[:3].upper() + r", Kn = $\infty$")
    ax.axhline(0.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_c(t) - \alpha_c(0)$")
    ax.legend(fontsize=8, loc="upper left")
    fig.savefig(os.path.join(outdir, "fig_cc_controls.png"), dpi=200)
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
            kk = s["ek_t"] <= s["t_c"]
            axs[2].plot(s["ek_t"][kk], s["ek_sum"][kk] - s["ek_sum"][0], color=col[k], ls=ls, marker=".",
                        label=f"{mk.upper()} {lab[k]}")
        if "dEp" not in s:
            continue
        p = pred[mk]["runs"][name]
        axs[0].plot(s["ct"], s["dEp"], color=col[k], ls=ls, label=f"{mk.upper()} {lab[k]}")
        axs[0].plot(s["ct"], p["dE_particles_per_collision_rel"] * s["ncum"], color="k", lw=1.0, ls=":")
        axs[1].plot(s["ct"][s["nc"] > 0], s["pair_eps"][s["nc"] > 0], ".", ms=1.0, color=col[k],
                    alpha=0.3)
    axs[0].set_yscale("log")
    axs[0].set_ylim(1e-7, 1e-1)
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"$\Sigma\,\Delta(\Sigma MW)_{\rm coll}/\Sigma MW$")
    axs[0].legend(fontsize=7, loc="upper left")
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"cell-frame $|\Delta E|$ per collision / ($2M_p\epsilon$)")
    axs[2].axhline(0.0, **fs.MASK_LINE)
    axs[2].set_xlabel(r"$t/M$")
    axs[2].set_ylabel(r"$\Sigma M E_K - $ initial, before collapse  $[M]$")
    axs[2].legend(fontsize=7, loc="lower left")
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
        if mk == "cc1" and "last" in s["hist_e"]:
            tl, e = s["hist_e"]["last"]
            axs[2].hist(e, bins=np.linspace(0.7, 1.25, 111), histtype="step", color=col[k],
                        lw=1.0, label=lab[k] + f", t = {tl:g} M", weights=np.full(len(e), 1.0 / 1e5))
            if k == "inf":
                e0 = s["hist_e"]["0"]
                axs[2].hist(e0, bins=np.linspace(0.7, 1.25, 111), histtype="step", color="grey", lw=1.0,
                            label=r"$t=0$", weights=np.full(len(e0), 1.0 / 1e5))
    axs[0].set_yscale("log")
    axs[1].set_yscale("log")
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"fraction with $E_K > E_0$")
    axs[0].legend(fontsize=7, loc="lower right")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"fraction with $E_K > 1$")
    axs[2].axvline(1.0, **fs.GUIDE)
    axs[2].set_yscale("log")
    axs[2].set_xlabel(r"$E_K/E_0$ (CC1, last record before collapse)")
    axs[2].set_ylabel("fraction of particles per bin")
    axs[2].legend(fontsize=6, loc="lower left")
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
