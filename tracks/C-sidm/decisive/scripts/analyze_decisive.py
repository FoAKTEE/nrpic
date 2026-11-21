#!/usr/bin/env python3
"""Analysis of the decisive collisional cluster runs D1 and D3 (JOURNAL.md entries 2, 4) from
the AthenaK histories, against the wave-2 controls and cell-mode runs.

    python3 analyze_decisive.py [--out DIR] [--batch RUN_ID ...] [--no-wave2]

Runs are named <model>_kn<Kn>_<mode>_s<seed> (model cc1, cc2, d3; mode part or cell) or
<model>_kninf (control). The wave-2 runs of threshold_scan enter under these names:
    cc1_kninf         C-20261115-171058-c26cfad/cc1_kninf
    cc1_kn1_cell_s1   C-20261115-171058-c26cfad/cc1_kn1
    cc1_kn10_cell_s1  C-20261115-171059-4b70228/cc1_kn10
    cc2_kninf         C-20261115-171059-4b70228/cc2_kninf
    cc2_kn10_cell_s1  C-20261115-171059-35441e3/cc2_kn10
    cc2_kn1_cell_s1   C-20261115-171059-35441e3/cc2_kn1
--batch adds every subdirectory <name>/ of scratch/C-sidm/<RUN_ID>/ with a cc.nrpic.hst
(smoke_* runs are skipped). Quantities per run (histories cc.nrpic.hst, cc.coll.hst):
  t_c          first time with alpha_min < 0.3; t_exc first excision
  dalpha(t)    alpha_c(control) - alpha_c(run), alpha_c = alpha_probe, control of the model;
               D50, D100 = means over 45-55 and 95-105 M; t(dalpha >= 0.01)
  collisions per particle before t_c (2 n_coll / N), count z against sum_P
  budget       cell: summed dE_particles / sum_MW_particles(0) to t_c; particle: summed
               dH_particles / sum_MH_particles(0) (largest |.| before the first excision),
               n_noroot, n_balance / n_coll, max_dlam
  seed scatter |X(s1) - X(s2)| per (model, Kn, mode) group; mode difference of the group
               means with sigma_pooled^2 = (s_part^2 + s_cell^2)/4
Writes summary.json and fig_*.png into DIR.
"""
import argparse
import glob
import json
import os
import re
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TR, "threshold_scan"))
import common as C  # noqa: E402

WAVE2 = {
    "cc1_kninf": "C-20261115-171058-c26cfad/cc1_kninf",
    "cc1_kn1_cell_s1": "C-20261115-171058-c26cfad/cc1_kn1",
    "cc1_kn10_cell_s1": "C-20261115-171059-4b70228/cc1_kn10",
    "cc2_kninf": "C-20261115-171059-4b70228/cc2_kninf",
    "cc2_kn10_cell_s1": "C-20261115-171059-35441e3/cc2_kn10",
    "cc2_kn1_cell_s1": "C-20261115-171059-35441e3/cc2_kn1",
}
NAME = re.compile(r"^(?P<model>cc1|cc2|d3)_kn(?P<kn>inf|[0-9.]+)(?:_(?P<mode>part|cell)_s(?P<seed>\d+))?$")
N_PART = 100000


def parse(name):
    m = NAME.match(name)
    if not m:
        return None
    d = m.groupdict()
    return dict(model=d["model"], kn=d["kn"], mode=d["mode"], seed=int(d["seed"]) if d["seed"] else None)


def wall_of(d):
    logs = sorted(glob.glob(os.path.join(d, "athena.*.log"))) or sorted(glob.glob(os.path.join(d, "athena.log")))
    if not logs:
        return None
    m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", open(logs[-1]).read())
    return float(m.group(1)) if m else None


def window_mean(t, y, a, b):
    k = (t >= a) & (t <= b) & np.isfinite(y)
    return float(np.mean(y[k])) if np.any(k) else None


def f_cos(t, A, P, c):
    """Excursion form of drift/scripts/controls.py (copied): A (1 - cos 2 pi t/P) + c."""
    return A * (1.0 - np.cos(2.0 * np.pi * t / P)) + c


def cos_fit(t, y):
    """Least-squares fit of f_cos with drift's starting values; y = alpha_c - alpha_c(0) of a control."""
    from scipy.optimize import curve_fit
    ok = np.isfinite(y)
    t, y = t[ok], y[ok]
    try:
        p, cov = curve_fit(f_cos, t, y, p0=(0.5 * np.nanmax(y), 2.0 * t[np.nanargmax(y)], 0.0), maxfev=20000)
    except Exception as e:  # noqa: BLE001
        return dict(error=str(e))
    res = y - f_cos(t, *p)
    return dict(A=float(p[0]), P=float(p[1]), c=float(p[2]), sd=[float(v) for v in np.sqrt(np.diag(cov))],
                rms=float(np.sqrt(np.mean(res ** 2))))


def crossing(t, y, level):
    """First time y falls below level, linear between the two records around it."""
    i = np.flatnonzero(y < level)
    if not len(i):
        return None
    i = int(i[0])
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (level - y[i - 1]) * (t[i] - t[i - 1]) / (y[i] - y[i - 1]))


def analyse(name, d, ctrl):
    h = C.read_hst(os.path.join(d, "cc.nrpic.hst"))
    t, ap = h["time"], h["alpha_probe"].copy()
    out = dict(dir=d, t_end=float(t[-1]))
    exc = np.flatnonzero(h["n_excised"] > 0)
    out["t_exc"] = float(t[exc[0]]) if len(exc) else None
    low = np.flatnonzero(h["alpha_min"] < 0.3)
    out["t_c"] = float(t[low[0]]) if len(low) else None
    # sub-cadence crossing times of alpha_min (history every 4 cycles = 0.25 M)
    out["t_c_interp"] = crossing(t, h["alpha_min"], 0.3)
    out["t_amin_0p5"] = crossing(t, h["alpha_min"], 0.5)
    out["t_amin_0p4"] = crossing(t, h["alpha_min"], 0.4)
    bad = np.flatnonzero(~np.isfinite(h["alpha_probe"]) | (h["alpha_min"] > 1e300))
    out["t_nonfinite"] = float(t[bad[0]]) if len(bad) else None
    noexc = h["n_excised"] == 0
    out["rest_mass_identical_before_excision"] = bool(np.all(h["sum_m"][noexc] == h["sum_m"][0]))
    M0 = float(h["sum_m"][0])
    out["rest_mass_budget_rel"] = float(np.max(np.abs(h["sum_m"] + h["m_excised"] + h["m_escaped"] - M0)) / M0)
    live = h["sum_mW"] > 0
    out["deposit_identity"] = float(np.max(np.abs(h["int_E"][live] - h["sum_mW"][live]) / h["sum_mW"][live]))
    out["alpha_c_start"] = float(ap[0])
    wall = wall_of(d)
    out["wall_s"] = wall
    out["s_per_M"] = wall / t[-1] if wall and t[-1] > 0 else None
    ser = dict(t=t, ap=ap, amin=h["alpha_min"])
    if ctrl is not None and ctrl is not h:
        ac = np.interp(t, ctrl["time"], ctrl["alpha_probe"], left=np.nan, right=np.nan)
        dal = ac - ap
        good = np.isfinite(dal) & (h["alpha_min"] > 0.1)
        dal = np.where(good, dal, np.nan)
        ser["dal"] = dal
        out["D25"] = window_mean(t, dal, 20.0, 30.0)
        out["D50"] = window_mean(t, dal, 45.0, 55.0)
        out["D100"] = window_mean(t, dal, 95.0, 105.0)
        out["D150"] = window_mean(t, dal, 145.0, 155.0)
        k = np.flatnonzero(np.nan_to_num(dal, nan=-1.0) >= 0.01)
        out["t_dalpha_0p01"] = float(t[k[0]]) if len(k) else None
        k = np.flatnonzero(np.nan_to_num(dal, nan=-1.0) >= 0.03)
        out["t_dalpha_0p03"] = float(t[k[0]]) if len(k) else None
        # early contraction rate: least-squares slope of dalpha over 0-100 M
        w = (t <= 100.0) & np.isfinite(dal)
        if np.sum(w) > 10:
            out["rate_0_100"] = float(np.polyfit(t[w], dal[w], 1)[0])
    else:
        out["alpha_c_max_dev_from_start"] = float(np.nanmax(np.abs(ap - ap[0])))
        out["alpha_c_dev_t100"] = window_mean(t, ap - ap[0], 95.0, 105.0)
        out["alpha_c_max_rise"] = float(np.nanmax(ap - ap[0]))
        out["t_alpha_c_max_rise"] = float(t[int(np.nanargmax(ap - ap[0]))])
        out["cos_fit"] = cos_fit(t, ap - ap[0])
        ser["cosfit"] = out["cos_fit"]
    ch = os.path.join(d, "cc.coll.hst")
    if os.path.exists(ch):
        c = C.read_hst(ch)
        nc = c["n_coll"]
        tc = out["t_c"] if out["t_c"] is not None else float(t[-1])
        pre = c["time"] <= tc
        n_pre = float(nc[pre].sum())
        out["collisions_per_particle_before_tc"] = 2.0 * n_pre / N_PART
        out["collisions_per_particle_t100"] = 2.0 * float(nc[c["time"] <= 100.0].sum()) / N_PART
        out["count_z_before_tc"] = float((n_pre - c["sum_P"][pre].sum()) / np.sqrt(max(c["sum_P"][pre].sum(), 1e-300)))
        k1 = int(np.argmin(c["ncycle"]))
        out["sumP_step1"] = float(c["sum_P"][k1])
        out["ncoll_step1"] = int(nc[k1])
        out["n_trunc"] = int(c["n_trunc"].sum())
        out["max_P"] = float(c["max_P"].max())
        out["max_nsub"] = int(c["max_nsub"].max())
        texc = out["t_exc"] if out["t_exc"] is not None else 1e30
        bx = c["time"] < texc
        mw0 = float(c["sum_MW_particles"][0])
        dEp = np.cumsum(np.nan_to_num(c["dE_particles"])) / mw0
        out["dE_particles_rel_to_tc"] = float(dEp[pre][-1]) if np.any(pre) else None
        w25 = (c["time"] <= 25.0)
        out["dE_particles_per_collision_first25M"] = float(
            np.nansum(c["dE_particles"][w25]) / mw0 / max(nc[w25].sum(), 1.0))
        ser.update(ct=c["time"], ncum=np.cumsum(nc), dEp=dEp)
        if "dH_particles" in c:
            mh0 = float(c["sum_MH_particles"][0])
            dH = np.cumsum(np.nan_to_num(c["dH_particles"]))
            ser.update(dH=dH / mh0, MH=c["sum_MH_particles"] / mh0 - 1.0)
            out["dH_rel_max_before_exc"] = float(np.max(np.abs(dH[bx]))) / mh0 if np.any(bx) else None
            out["dH_rel_end"] = float(dH[-1] / mh0)
            nbx = float(nc[bx].sum())
            out["dH_per_collision_before_exc_M"] = float(dH[bx][-1] / max(nbx, 1.0)) if np.any(bx) else None
            out["dH_per_collision_first25M_M"] = float(np.nansum(c["dH_particles"][w25]) / max(nc[w25].sum(), 1.0))
            out["dH_monotone_nondecreasing_before_exc"] = bool(np.all(np.diff(dH[bx]) >= 0.0))
            out["n_noroot_before_exc"] = int(c["n_noroot"][bx].sum())
            out["n_balance_before_exc"] = int(c["n_balance"][bx].sum())
            out["n_balance_frac_before_exc"] = float(c["n_balance"][bx].sum() / max(nbx, 1.0))
            out["max_dlam_before_exc"] = float(np.nanmax(c["max_dlam"][bx])) if np.any(bx) else None
            out["sum_MH_particles_change_before_exc"] = float(c["sum_MH_particles"][bx][-1] / mh0 - 1.0)
            out["sum_MH_particles_maxdev_before_exc"] = float(np.max(np.abs(c["sum_MH_particles"][bx] / mh0 - 1.0)))
            # the same up to the collapse criterion t_c (the excision record of cc.nrpic.hst comes
            # every 4 cycles, so "before excision" can include the steps of the blow-up)
            bt = pre
            nbt = float(nc[bt].sum())
            out["dH_rel_max_before_tc"] = float(np.max(np.abs(dH[bt]))) / mh0
            out["dH_per_collision_before_tc_M"] = float(dH[bt][-1] / max(nbt, 1.0))
            out["dH_negative_steps_before_tc"] = int(np.sum(c["dH_particles"][bt] < 0.0))
            out["dH_min_step_before_tc_M"] = float(np.min(c["dH_particles"][bt]))
            out["dH_max_step_before_tc_M"] = float(np.max(c["dH_particles"][bt]))
            out["dH_cumulative_min_before_tc_M"] = float(np.min(dH[bt]))
            out["n_noroot_before_tc"] = int(c["n_noroot"][bt].sum())
            nr = np.flatnonzero(c["n_noroot"] > 0)
            out["t_first_noroot"] = float(c["time"][nr[0]]) if len(nr) else None
            out["n_balance_frac_before_tc"] = float(c["n_balance"][bt].sum() / max(nbt, 1.0))
            for T in (100.0, 150.0):
                k = c["time"] <= T
                out[f"n_balance_frac_t{int(T)}"] = float(c["n_balance"][k].sum() / max(nc[k].sum(), 1.0))
                out[f"max_dlam_t{int(T)}"] = float(np.nanmax(c["max_dlam"][k]))
            out["max_dlam_before_tc"] = float(np.nanmax(c["max_dlam"][bt]))
            out["sum_MH_particles_change_t100"] = float(np.interp(100.0, c["time"], c["sum_MH_particles"]) / mh0 - 1.0)
            out["sum_MH_particles_change_before_tc"] = float(c["sum_MH_particles"][bt][-1] / mh0 - 1.0)
            out["sum_MH_particles_0"] = mh0
            ser["tc_coll"] = tc
    return out, ser


def group_stats(res):
    """Seed scatter per (model, kn, mode) and mode comparison per (model, kn)."""
    groups = {}
    for name, r in res.items():
        p = parse(name)
        if p is None or p["mode"] is None:
            continue
        groups.setdefault((p["model"], p["kn"], p["mode"]), []).append(name)
    keys = ("t_c", "t_c_interp", "t_amin_0p5", "t_amin_0p4", "D25", "D50", "D100", "D150", "rate_0_100",
            "t_dalpha_0p01", "t_dalpha_0p03", "collisions_per_particle_before_tc")
    out = {}
    for (mo, kn, mode), names in groups.items():
        g = dict(runs=sorted(names))
        for k in keys:
            v = [res[n].get(k) for n in sorted(names)]
            v = [x for x in v if x is not None]
            g[k] = v
            if len(v) >= 2:
                g[f"{k}_mean"] = float(np.mean(v))
                g[f"{k}_seed_diff"] = float(abs(v[0] - v[1])) if len(v) == 2 else float(np.ptp(v))
            elif len(v) == 1:
                g[f"{k}_mean"] = float(v[0])
        out[f"{mo}_kn{kn}_{mode}"] = g
    comp = {}
    for (mo, kn) in {(a, b) for (a, b, _) in groups}:
        gp, gc = out.get(f"{mo}_kn{kn}_part"), out.get(f"{mo}_kn{kn}_cell")
        if not (gp and gc):
            continue
        cc = {}
        for k in keys:
            if f"{k}_mean" in gp and f"{k}_mean" in gc:
                diff = gp[f"{k}_mean"] - gc[f"{k}_mean"]
                sp, sc = gp.get(f"{k}_seed_diff"), gc.get(f"{k}_seed_diff")
                sig = None
                if sp is not None and sc is not None:
                    sig = float(np.sqrt((sp ** 2 + sc ** 2) / 4.0))
                elif sp is not None or sc is not None:
                    s = sp if sp is not None else sc
                    sig = float(s / np.sqrt(2.0))
                cc[k] = dict(part_minus_cell=float(diff), sigma_pooled=sig,
                             z=float(diff / sig) if sig else None)
        comp[f"{mo}_kn{kn}"] = cc
    return out, comp


def curve_scatter(res, ser):
    """Instantaneous scatter of dalpha(t) between two runs of one (model, Kn): rms and largest |difference|
    over windows; pairs of seeds of one mode, and every run against the cell-mode seed 1."""
    out = {}
    names = sorted(n for n in ser if parse(n) and parse(n)["mode"] and "dal" in ser[n])
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = parse(a), parse(b)
            if (pa["model"], pa["kn"]) != (pb["model"], pb["kn"]):
                continue
            sa, sb = ser[a], ser[b]
            dd = np.interp(sa["t"], sb["t"], sb["dal"], left=np.nan, right=np.nan) - sa["dal"]
            tend = min(res[a].get("t_c") or 300.0, res[b].get("t_c") or 300.0) - 10.0
            r = {}
            for lo, hi in ((0.0, 100.0), (100.0, tend), (0.0, tend)):
                k = (sa["t"] >= lo) & (sa["t"] <= hi) & np.isfinite(dd)
                if np.sum(k) > 10:
                    r[f"rms_{int(lo)}_{int(hi)}"] = float(np.sqrt(np.mean(dd[k] ** 2)))
                    r[f"maxabs_{int(lo)}_{int(hi)}"] = float(np.max(np.abs(dd[k])))
                    r[f"mean_{int(lo)}_{int(hi)}"] = float(np.mean(dd[k]))
            out[f"{b} - {a}"] = r
    return out


def figures(outdir, res, ser):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(C.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    col = {"cell": fs.PAL["red"], "part": fs.PAL["blue"]}
    lsd = {1: "-", 2: "--"}
    models = [m for m in ("cc2", "cc1") if any(n.startswith(m + "_kn10_") for n in ser)]
    # F1: dalpha(t) and alpha_min(t), Kn = 10, per model
    if models:
        fig, axs = plt.subplots(2, len(models), figsize=(fs.FULL_WIDTH, 5.0), sharex=True, squeeze=False)
        fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.95, wspace=0.25, hspace=0.08)
        for j, mo in enumerate(models):
            for name in sorted(ser):
                p = parse(name)
                if p is None or p["model"] != mo or p["kn"] != "10" or p["mode"] is None:
                    continue
                s = ser[name]
                lab = f"{p['mode']} s{p['seed']}"
                if "dal" in s:
                    axs[0, j].plot(s["t"], s["dal"], color=col[p["mode"]], ls=lsd.get(p["seed"], ":"), lw=1.1,
                                   label=lab)
                axs[1, j].semilogy(s["t"], s["amin"], color=col[p["mode"]], ls=lsd.get(p["seed"], ":"), lw=1.1,
                                   label=lab)
                if res[name].get("t_c"):
                    axs[1, j].axvline(res[name]["t_c"], color=col[p["mode"]], ls=lsd.get(p["seed"], ":"), lw=0.6)
            axs[0, j].axhline(0.0, **fs.MASK_LINE)
            axs[0, j].axvspan(95, 105, color="grey", alpha=0.15, lw=0)
            axs[0, j].set_ylim(-0.01, 0.12)
            axs[0, j].set_ylabel(r"$\alpha_c^{\rm control} - \alpha_c$" + f"  ({mo.upper()}, Kn = 10)")
            axs[1, j].axhline(0.3, **fs.GUIDE)
            axs[1, j].set_ylim(0.03, 1.0)
            axs[1, j].set_ylabel(r"$\alpha_{\min}$ on the mesh")
            axs[1, j].set_xlabel(r"$t/M$")
            axs[0, j].legend(fontsize=7, loc="upper left")
        fig.savefig(os.path.join(outdir, "fig_d1_lapse.png"), dpi=200)
        plt.close(fig)
    # F1b: differences between runs of one model (seed and mode), and alpha_min near t_c
    if models:
        fig, axs = plt.subplots(2, len(models), figsize=(fs.FULL_WIDTH, 5.0), squeeze=False)
        fig.subplots_adjust(left=0.1, right=0.985, bottom=0.09, top=0.95, wspace=0.28, hspace=0.32)
        for j, mo in enumerate(models):
            ref = f"{mo}_kn10_cell_s1"
            for name in sorted(ser):
                p = parse(name)
                if p is None or p["model"] != mo or p["kn"] != "10" or p["mode"] is None:
                    continue
                s = ser[name]
                lab = f"{p['mode']} s{p['seed']}"
                if ref in ser and name != ref and "dal" in s:
                    r = ser[ref]
                    dd = s["dal"] - np.interp(s["t"], r["t"], r["dal"], left=np.nan, right=np.nan)
                    axs[0, j].plot(s["t"], dd, color=col[p["mode"]], ls=lsd.get(p["seed"], ":"), lw=1.0,
                                   label=lab + " $-$ cell s1")
                axs[1, j].plot(s["t"], s["amin"], color=col[p["mode"]], ls=lsd.get(p["seed"], ":"), lw=1.1,
                               label=lab)
            axs[0, j].axhline(0.0, **fs.MASK_LINE)
            axs[0, j].axvspan(95, 105, color="grey", alpha=0.15, lw=0)
            axs[0, j].set_xlim(0, 200)
            axs[0, j].set_ylim(-4e-3, 4e-3)
            axs[0, j].set_xlabel(r"$t/M$")
            axs[0, j].set_ylabel(r"$\Delta(\alpha_c^{\rm control}-\alpha_c)$" + f" ({mo.upper()})")
            axs[0, j].legend(fontsize=6, loc="upper left")
            axs[1, j].axhline(0.3, **fs.GUIDE)
            tcs = [res[n]["t_c_interp"] for n in ser if n.startswith(mo + "_kn10_") and res[n].get("t_c_interp")]
            if tcs:
                axs[1, j].set_xlim(min(tcs) - 12, max(tcs) + 4)
            axs[1, j].set_ylim(0.2, 0.6)
            axs[1, j].set_xlabel(r"$t/M$")
            axs[1, j].set_ylabel(r"$\alpha_{\min}$" + f" ({mo.upper()}, Kn = 10)")
            axs[1, j].legend(fontsize=6, loc="upper right")
        fig.savefig(os.path.join(outdir, "fig_d1_diff.png"), dpi=200)
        plt.close(fig)
    # F2: budget (particle: summed dH; cell: summed dE_particles), and cumulative collisions
    if any("dH" in s or "dEp" in s for s in ser.values()):
        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.42)
        for name in sorted(ser):
            p = parse(name)
            s = ser[name]
            if p is None or p["mode"] is None or "ct" not in s or (p["kn"] == "1" and p["model"] != "d3"):
                continue
            c = col[p["mode"]] if p["model"] != "d3" else fs.PAL["green"]
            ls = lsd.get(p["seed"], ":") if p["model"] != "cc1" else ":"
            texc = res[name].get("t_exc") or 1e30
            tcut = min(texc, res[name].get("t_c") or 1e30)
            k = s["ct"] <= tcut
            if p["mode"] == "cell":
                axs[0].semilogy(s["ct"][k], np.abs(s["dEp"][k]) + 1e-30, color=c, ls=ls, lw=1.0, label=name)
            if "dH" in s:
                axs[0].semilogy(s["ct"][k], np.abs(s["dH"][k]) + 1e-30, color=c, ls=ls, lw=1.0, label=name)
                axs[1].plot(s["ct"][k], s["MH"][k], color=c, ls=ls, lw=1.0, label=name)
            axs[2].plot(s["ct"], 2.0 * s["ncum"] / N_PART, color=c, ls=ls, lw=1.0, label=name)
        axs[0].set_ylim(1e-20, 1e-2)
        axs[0].set_xlabel(r"$t/M$")
        axs[0].set_ylabel(r"collision steps: $|\Sigma\Delta|$ / initial sum")
        axs[0].text(0.03, 0.04, "cell: dE_particles (sum MW)\nparticle: dH_particles (sum MH)",
                    transform=axs[0].transAxes, fontsize=6, va="bottom")
        axs[0].legend(fontsize=5, loc="center right")
        axs[1].set_xlabel(r"$t/M$")
        axs[1].set_ylabel(r"$\Sigma M H_p$ / initial $-1$ (push included)")
        axs[1].text(0.03, 0.04, r"to $t_c$ (or the first excision)", transform=axs[1].transAxes, fontsize=6)
        axs[2].set_xlabel(r"$t/M$")
        axs[2].set_ylabel("collisions per particle")
        fig.savefig(os.path.join(outdir, "fig_d1_budget.png"), dpi=200)
        plt.close(fig)
    # F3: D3 against CC2, relative contraction
    if any(n.startswith("d3_") for n in ser):
        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
        fig.subplots_adjust(left=0.07, right=0.99, bottom=0.16, top=0.95, wspace=0.38)
        cmap = {"10": fs.PAL["blue"], "1": fs.PAL["red"], "inf": "k"}
        for name in sorted(ser):
            p = parse(name)
            s = ser[name]
            if p is None or p["model"] not in ("d3", "cc2"):
                continue
            if p["mode"] not in (None, "part") and not (p["mode"] == "cell" and p["seed"] == 1):
                continue
            ls = "-" if p["model"] == "d3" else ":"
            axs[2].semilogy(s["t"], np.where(s["amin"] > 0, s["amin"], np.nan), color=cmap.get(p["kn"], "k"),
                            ls=ls, lw=1.0)
            if "dal" not in s:
                continue
            axs[0].plot(s["t"], s["dal"], color=cmap.get(p["kn"], "k"), ls=ls, lw=1.1,
                        label=f"{p['model'].upper()} Kn = {p['kn']} {p['mode']} s{p['seed']}")
            if "ct" in s:
                cpp = np.interp(s["t"], s["ct"], 2.0 * s["ncum"] / N_PART)
                axs[1].plot(cpp, s["dal"], color=cmap.get(p["kn"], "k"), ls=ls, lw=1.1)
        for ax in axs[:2]:
            ax.axhline(0.0, **fs.MASK_LINE)
            ax.set_ylim(-0.01, 0.1)
            ax.set_ylabel(r"$\alpha_c^{\rm control} - \alpha_c$")
        axs[0].set_xlim(0, 300)
        axs[2].axhline(0.3, **fs.GUIDE)
        axs[2].set_ylim(0.03, 1.0)
        axs[2].set_xlim(0, 300)
        axs[2].set_xlabel(r"$t/M$")
        axs[2].set_ylabel(r"$\alpha_{\min}$ on the mesh")
        axs[2].text(0.03, 0.04, "solid D3, dotted CC2\nblack: Kn = inf", transform=axs[2].transAxes, fontsize=6)
        axs[0].set_xlabel(r"$t/M$")
        axs[1].set_xlabel("collisions per particle")
        axs[1].set_xscale("log")
        axs[1].set_xlim(0.03, 30)
        axs[0].legend(fontsize=6, loc="upper left")
        fig.savefig(os.path.join(outdir, "fig_d3_contraction.png"), dpi=200)
        plt.close(fig)
    # F4: controls
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.9))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.16, top=0.95)
    for name, s in ser.items():
        if name.endswith("_kninf"):
            ln, = ax.plot(s["t"], s["ap"] - s["ap"][0], lw=1.0, label=name)
            fc = s.get("cosfit", {})
            if "P" in fc:
                ax.plot(s["t"], f_cos(s["t"], fc["A"], fc["P"], fc["c"]), color=ln.get_color(), ls="--", lw=0.8,
                        label=f"fit P = {fc['P']:.0f} M")
    ax.axhline(0.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_c(t) - \alpha_c(0)$, controls")
    ax.legend(fontsize=6)
    fig.savefig(os.path.join(outdir, "fig_controls.png"), dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--batch", nargs="*", default=[])
    ap.add_argument("--no-wave2", action="store_true")
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    runs = {} if a.no_wave2 else {n: os.path.join(C.SCRATCH, p) for n, p in WAVE2.items()}
    for rid in a.batch:
        for d in sorted(glob.glob(os.path.join(C.SCRATCH, rid, "*"))):
            n = os.path.basename(d)
            if n.startswith("smoke") or not os.path.isfile(os.path.join(d, "cc.nrpic.hst")):
                continue
            if parse(n) is None:
                print("skipped (name)", n)
                continue
            runs[n] = d
    hists = {n: C.read_hst(os.path.join(d, "cc.nrpic.hst")) for n, d in runs.items() if n.endswith("_kninf")}
    res, ser = {}, {}
    for name in sorted(runs, key=lambda n: (not n.endswith("_kninf"), n)):
        p = parse(name)
        ctrl = hists.get(f"{p['model']}_kninf")
        if name.endswith("_kninf"):
            ctrl = None
        res[name], ser[name] = analyse(name, runs[name], ctrl)
        print(name, json.dumps({k: v for k, v in res[name].items() if not isinstance(v, (list, dict))}), flush=True)
    groups, comp = group_stats(res)
    cs = curve_scatter(res, ser)
    out = dict(runs=res, groups=groups, mode_comparison=comp, curve_scatter=cs,
               inputs=dict(wave2={} if a.no_wave2 else WAVE2, batch=a.batch))
    print(json.dumps(dict(groups=groups, mode_comparison=comp, curve_scatter=cs), indent=1))
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(out, f, indent=1)
    figures(a.out, res, ser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
