#!/usr/bin/env python3
"""Tests ES and L3 of the work package "gauge" (tracks/core/JOURNAL-gauge.md).

ES (tag <prefix>-es-*): Track D's Einstein-Straus data evolved with the new lapse:
apparent-horizon mass in time, areal radius of the tracer groups against their proper
time and the exact curves of es_reference.csv, lapse at the tracers of the dust plateau
against the reference of lapse_ref.py, largest lapse on the mesh, smallest areal radius
of the dust.

L3 (tag <prefix>-collapse-*): the bound expanding ball through turnaround and collapse:
areal radius of the tracked shells against proper time and the exact cycloid until they
are removed, lapse at the centre, apparent-horizon mass.

Writes es_numbers_<prefix>.json, collapse_numbers_<prefix>.json and
figs/es_<prefix>_*.png|pdf, figs/collapse_<prefix>_*.png|pdf.

    es_collapse_analysis.py [--prefix gc] [--batch RUN_ID ...]

Runs: the hand-written manifests of 2026-11-15 with tag <prefix>-es-* and
<prefix>-collapse-* that ended with exit status 0, and, with --batch, the
sub-directories es-* and collapse-* of card jobs registered by harness/bin/nrpic-run
(launcher batch: scratch/core/<run_id>/<name>/).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/id"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)

import idlib                                   # noqa: E402
from punc_analysis import manifests, table, batch_manifests     # noqa: E402
from lapse_ref import central_lapse            # noqa: E402
from nrpic import expanding_ball as eb         # noqa: E402
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

FIGS = os.path.join(HERE, "figs")


def read_traj_tags(rundir, base):
    """Tracked particles, also when some are removed during the run:
    {tag: dict(t, x[n,3], alpha, g[n,6], tau)}."""
    a = np.fromfile(os.path.join(rundir, base + ".traj.bin"), dtype="<f8").reshape(-1, 8)
    b = np.fromfile(os.path.join(rundir, base + ".trajmet.bin"), dtype="<f8").reshape(-1, 17)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    out = {}
    tags = a[:, 1].astype(int)
    order = np.lexsort((a[:, 0], tags))
    a, b, tags = a[order], b[order], tags[order]
    cut = np.nonzero(np.diff(tags))[0] + 1
    for ia, ib in zip(np.concatenate([[0], cut]), np.concatenate([cut, [len(tags)]])):
        out[int(tags[ia])] = dict(t=a[ia:ib, 0], x=a[ia:ib, 2:5], alpha=b[ia:ib, 2],
                                  g=b[ia:ib, 6:12], tau=b[ia:ib, 12])
    return out


def ref_plateau(H0, T, a0, tmax, dt=0.01):
    """Reference lapse in an Einstein-de Sitter plateau, start lapse a0 (columns t, tau,
    alpha)."""
    la, tau = math.log(a0), 0.0
    out = []

    def rhs(la, tau):
        H = H0 / (1.0 + 1.5 * H0 * tau)
        return 6.0 * H - (max(la, 0.0) / T if T > 0.0 else 0.0), math.exp(la)
    for i in range(int(round(tmax / dt)) + 1):
        out.append((i * dt, tau, math.exp(la)))
        k1 = rhs(la, tau)
        k2 = rhs(la + 0.5 * dt * k1[0], tau + 0.5 * dt * k1[1])
        k3 = rhs(la + 0.5 * dt * k2[0], tau + 0.5 * dt * k2[1])
        k4 = rhs(la + dt * k3[0], tau + dt * k3[1])
        la += dt * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6.0
        tau += dt * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6.0
    return np.array(out).T


def args_of(man):
    return {a.split("=")[0]: a.split("=", 1)[1] for a in man["command"] if "=" in a}


def leak_T(man, default_rate):
    """Relaxation time of a run: from the command line, else from the copy of the input
    file in the output directory, else from default_rate."""
    rate = args_of(man).get("z4c/lapse_leak")
    if rate is None:
        for f in glob.glob(os.path.join(man["output_directory"], "*.athinput")):
            with open(f) as fh:
                for line in fh:
                    w = line.split("#")[0].split("=")
                    if len(w) == 2 and w[0].strip() == "lapse_leak":
                        rate = w[1].strip()
    rate = float(default_rate if rate is None else rate)
    return 1.0 / rate if rate > 0.0 else 0.0


# ----------------------------------------------------------------------------------------
def analyse_es(pre, name, man):
    out = man["output_directory"]
    icdir = None
    for inp in man["inputs"]:
        if inp["path"].endswith("es.json"):
            icdir = os.path.dirname(inp["path"])
    with open(os.path.join(icdir, "es.json")) as f:
        meta = json.load(f)
    ref = np.genfromtxt(os.path.join(icdir, "es_reference.csv"), delimiter=",", names=True,
                        comments=None)
    rtau = ref[ref.dtype.names[0]]
    T = leak_T(man, 0.25)
    H0 = meta["summary"]["H"]
    tr = read_traj_tags(out, "es")
    hst = idlib.read_hst(os.path.join(out, "es.nrpic.hst"))
    hz = table(os.path.join(out, "es.horizon_summary_0.txt"))
    res = dict(run_id=man["run_id"], T=T, t_end=float(hst[-1, 0]), wall=man["wall_time_s"],
               card_hours=man["card_hours"], np_start=int(hst[0, 2]), np_end=int(hst[-1, 2]),
               n_excised=int(hst[-1, 16]), alpha_max=float(hst[:, 29].max()),
               alpha_min_end=float(hst[-1, 15]), groups={})
    # lapse at the puncture: the probe at the origin and the smallest lapse on the mesh
    res["puncture_lapse"] = {
        f"{tt:g}": dict(probe=float(np.interp(tt, hst[:, 0], hst[:, 12])),
                        smallest=float(np.interp(tt, hst[:, 0], hst[:, 15])))
        for tt in (0.0, 5.0, 10.0, 20.0, 30.0) if hst[-1, 0] >= tt}
    res["alpha_max_t"] = {f"{tt:g}": float(np.interp(tt, hst[:, 0], hst[:, 29]))
                          for tt in (5.0, 10.0, 20.0, 30.0) if hst[-1, 0] >= tt}

    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.96, wspace=0.28, hspace=0.26)
    cols = fs.series_colors(len(meta["tracers"]), cmap="viridis")
    for grp, c in zip(meta["tracers"], cols):
        i = grp["index"]
        tags = range(grp["tags"][0], grp["tags"][1] + 1)
        eps_all, taus, Rs, alphas, t_removed = [], [], [], [], []
        for tag in tags:
            if tag not in tr:
                continue
            p = tr[tag]
            R, r, grr = idlib.areal_radius(p["x"], p["g"])
            Rex = np.interp(p["tau"], rtau, ref[f"R_tracer{i}"])
            ok = np.isfinite(Rex) & (Rex > 2.2)
            eps_all.append(np.abs(R[ok] / Rex[ok] - 1.0).max() if ok.any() else np.nan)
            taus.append(p["tau"])
            Rs.append(R)
            alphas.append(p["alpha"])
            if p["t"][-1] < res["t_end"] - 0.5:
                t_removed.append((float(p["t"][-1]), float(p["tau"][-1]), float(R[-1])))
        if not taus:
            continue
        # group means on the shortest common record
        n = min(len(v) for v in taus)
        tau_m = np.mean([v[:n] for v in taus], axis=0)
        R_m = np.mean([v[:n] for v in Rs], axis=0)
        al_m = np.mean([v[:n] for v in alphas], axis=0)
        Rex_m = np.interp(tau_m, rtau, ref[f"R_tracer{i}"])
        rc_end = [float(np.sqrt(np.sum(tr[tag]["x"][-1] ** 2))) for tag in tags if tag in tr]
        rec = dict(R0=grp["R0"], n=len(taus), maxabs_eps=float(np.nanmax(eps_all)),
                   r_coord_end_min=float(np.min(rc_end)), r_coord_end_mean=float(np.mean(rc_end)),
                   tau_end=float(tau_m[-1]), R_end=float(R_m[-1]),
                   R_exact_end=float(Rex_m[-1]) if np.isfinite(Rex_m[-1]) else None,
                   alpha_end=float(al_m[-1]), removed=len(t_removed),
                   removed_tau_mean=float(np.mean([v[1] for v in t_removed])) if t_removed else None,
                   removed_R_mean=float(np.mean([v[2] for v in t_removed])) if t_removed else None)
        for tt in (10.0, 20.0, 30.0):
            if tau_m[-1] >= tt:
                rec[f"R_tau{tt:g}"] = float(np.interp(tt, tau_m, R_m))
                rec[f"Rex_tau{tt:g}"] = float(np.interp(tt, rtau, ref[f"R_tracer{i}"]))
        # lapse at the group against coordinate time (where on the mesh the lapse is largest)
        t_m = np.mean([tr[tag]["t"][:n] for tag in tags if tag in tr], axis=0)
        rec["alpha_t"] = {f"{tt:g}": float(np.interp(tt, t_m, al_m))
                          for tt in (5.0, 10.0, 20.0, 30.0) if t_m[-1] >= tt}
        rec["R_t"] = {f"{tt:g}": float(np.interp(tt, t_m, R_m))
                      for tt in (5.0, 10.0, 20.0, 30.0) if t_m[-1] >= tt}
        res["groups"][f"{grp['R0']:g}"] = rec
        ax[0, 0].plot(tau_m, R_m, color=c, lw=2.2, alpha=0.6)
        ax[0, 0].plot(rtau, ref[f"R_tracer{i}"], color="k", ls="--", lw=0.8)
        ok = np.isfinite(Rex_m) & (Rex_m > 2.2)
        ax[0, 1].semilogy(tau_m[ok], np.maximum(np.abs(R_m[ok] / Rex_m[ok] - 1.0), 1e-8), color=c,
                          label=r"$R_0=%g$" % grp["R0"])
        if abs(grp["R0"] - 48.0) < 1e-6:
            a0 = float(al_m[0])                 # lapse of the table at the start
            tp = np.mean([tr[tag]["t"][:n] for tag in tags if tag in tr], axis=0)
            rt, rta, ral = ref_plateau(H0, T, a0, res["t_end"])
            dev = np.abs(al_m / np.interp(tp, rt, ral) - 1.0)
            res["plateau"] = dict(alpha_t={f"{tt:g}": float(np.interp(tt, tp, al_m))
                                           for tt in (5.0, 10.0, 15.0, 20.0, 25.0, 30.0)
                                           if tp[-1] >= tt},
                                  alpha_ref={f"{tt:g}": float(np.interp(tt, rt, ral))
                                             for tt in (5.0, 10.0, 15.0, 20.0, 25.0, 30.0)
                                             if rt[-1] >= tt},
                                  max_dev=float(dev.max()))
            ax[1, 1].plot(tp, al_m, color=fs.PAL["red"], label=r"tracers at $48\,M$ (plateau)")
            ax[1, 1].plot(rt, ral, color="k", ls=":", label="homogeneous reference")
    ax[0, 0].set_xlim(0.0, max(1.2 * res["t_end"], 1.0))
    ax[0, 0].set_ylim(0.0, 95.0)
    ax[0, 0].plot([], [], color="grey", lw=2.2, alpha=0.6, label="run (group means)")
    ax[0, 0].plot([], [], color="k", ls="--", lw=0.8, label="exact")
    ax[0, 0].legend(fontsize=8)
    ax[0, 0].set_xlabel(r"proper time $\tau/M$", labelpad=-2)
    ax[0, 0].set_ylabel(r"areal radius of the tracers $R/M$")
    ax[0, 1].set_xlabel(r"proper time $\tau/M$", labelpad=-2)
    ax[0, 1].set_ylabel(r"$|R/R_{\rm exact}-1|$ of the group mean")
    ax[0, 1].set_ylim(1e-7, 1e-1)
    ax[0, 1].legend(fontsize=6, ncol=2)

    if len(hz):
        th, mh = hz[:, 1], hz[:, 2]
        res["horizon"] = dict(searches=int(len(th)), t_first=float(th[0]), t_last=float(th[-1]),
                              mass_first=float(mh[0]), mass_last=float(mh[-1]),
                              mass_t={f"{tt:g}": float(np.interp(tt, th, mh))
                                      for tt in (5.0, 10.0, 15.0, 20.0, 25.0, 30.0)
                                      if th[-1] >= tt})
        sel = th >= 10.0
        if sel.any():
            m10 = float(np.interp(10.0, th, mh))
            res["horizon"].update(mass_10=m10, max_drift_from_10=float(np.abs(mh[sel] / m10 - 1).max()),
                                  min_after_10=float(mh[sel].min()), max_after_10=float(mh[sel].max()))
        ax[1, 0].plot(th, mh - 1.0, color=fs.PAL["red"])
        ax[1, 0].axhline(0.0, color="k", lw=0.6)
    ax[1, 0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1, 0].set_ylabel(r"horizon mass $M_{\rm AH}/M-1$")
    ax[1, 1].plot(hst[:, 0], hst[:, 29], color=fs.PAL["blue"], label="largest lapse on the mesh")
    ax[1, 1].plot(hst[:, 0], hst[:, 15], color=fs.PAL["green"], label="smallest lapse (puncture)")
    ax[1, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1, 1].set_ylabel("lapse")
    ax[1, 1].set_ylim(0.0, 1.25)
    ax[1, 1].legend(fontsize=7)
    fs.save(fig, os.path.join(FIGS, f"es_{pre}_{name}"))
    plt.close(fig)

    # dust and the bubble: smallest areal-like radius of the dust in the last snapshot
    snaps = sorted(glob.glob(os.path.join(out, "es.part.*.bin")))
    if snaps:
        s = idlib.read_snapshot(snaps[-1])
        dust = s["tag"] >= meta["particles"]["n_tracers"]
        rd = np.sqrt(np.sum(s["x"][dust] ** 2, axis=1))
        res["dust"] = dict(snapshot_time=s["time"], n=int(dust.sum()),
                           r_coord_min=float(rd.min()), r_coord_max=float(rd.max()))
    return res


# ----------------------------------------------------------------------------------------
def analyse_collapse(pre, name, man):
    out = man["output_directory"]
    meta = idlib.run_meta(man)
    ball = eb.Ball(M=meta["M"], Rb=meta["Rb"], e0=meta["e0"], RE=meta.get("RE"), edge=meta["edge"])
    T = leak_T(man, 1.0)
    tr = read_traj_tags(out, "ball")
    hst = idlib.read_hst(os.path.join(out, "ball.nrpic.hst"))
    hzf = os.path.join(out, "ball.horizon_summary_0.txt")
    hz = table(hzf) if os.path.exists(hzf) else np.zeros((0, 12))
    nt = meta["n_tracers"]
    res = dict(run_id=man["run_id"], T=T, t_end=float(hst[-1, 0]), wall=man["wall_time_s"],
               card_hours=man["card_hours"], np_start=int(hst[0, 2]), np_end=int(hst[-1, 2]),
               nmb_max=int(hst[:, 22].max()), alpha_centre_min=float(hst[:, 12].min()),
               alpha_min=float(hst[:, 15].min()), alpha_max=float(hst[:, 29].max()), groups={})
    groups = dict(core=(0.0, 0.5), mid=(0.5, 0.75), outer=(0.75, 0.95), surface=(0.95, 1.0001))
    gcol = dict(core=fs.PAL["blue"], mid=fs.PAL["green"], outer=fs.PAL["yellow"],
                surface=fs.PAL["red"])
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.96, wspace=0.28, hspace=0.26)
    per = {g: [] for g in groups}
    for tag, p in tr.items():
        if tag < nt:
            continue
        r0 = float(np.sqrt(np.sum(p["x"][0] ** 2)))
        R0, m, E = ball.shell(np.array([r0]))
        R, r, grr = idlib.areal_radius(p["x"], p["g"])
        Rex = eb.ltb_radius(R0, p["tau"], m, E)
        frac = float(R0[0] / ball.Rout)
        for g, (lo, hi) in groups.items():
            if lo <= frac < hi:
                per[g].append(dict(tau=p["tau"], t=p["t"], R=R, Rex=Rex, R0=float(R0[0]),
                                   m=float(m[0])))
    for g, plist in per.items():
        if not plist:
            continue
        rec = dict(n=len(plist))
        # largest |eps| while the exact areal radius is above x Schwarzschild radii of the
        # mass inside the shell
        for lim, key in ((1.25, "to_2p5m"), (1.5, "to_3m"), (2.0, "to_4m")):
            e = []
            for p in plist:
                ok = p["Rex"] > lim * 2.0 * p["m"]
                if ok.any():
                    e.append(np.abs(p["R"][ok] / p["Rex"][ok] - 1.0).max())
            rec["maxabs_eps_" + key] = float(np.max(e)) if e else None
        rec["tau_last_mean"] = float(np.mean([p["tau"][-1] for p in plist]))
        rec["R_last_over_2m_mean"] = float(np.mean([p["R"][-1] / (2.0 * p["m"]) for p in plist]))
        amax = [p["R"].max() / p["R0"] for p in plist]
        tmax = [p["tau"][int(np.argmax(p["R"]))] for p in plist]
        rec["a_max_mean"] = float(np.mean(amax))
        rec["tau_max_mean"] = float(np.mean(tmax))
        res["groups"][g] = rec
        p = sorted(plist, key=lambda q: q["R0"])[len(plist) // 2]
        ax[0, 0].plot(p["tau"], p["R"], color=gcol[g], lw=2.4, alpha=0.6, label=g)
        ax[0, 0].plot(p["tau"], p["Rex"], color="k", ls="--", lw=0.8)
        ax[0, 0].axhline(2.0 * p["m"], color=gcol[g], lw=0.5, ls=":")
        for q in plist[::max(1, len(plist) // 40)]:
            ok = q["Rex"] > 2.5 * q["m"]
            ax[0, 1].semilogy(q["tau"][ok], np.maximum(np.abs(q["R"][ok] / q["Rex"][ok] - 1), 1e-7),
                              color=gcol[g], lw=0.5, alpha=0.5)
    ax[0, 0].plot([], [], color="k", ls="--", lw=0.8, label="exact cycloid")
    ax[0, 0].legend(fontsize=7)
    ax[0, 0].set_xlabel(r"proper time of the shell $\tau/M$", labelpad=-2)
    ax[0, 0].set_ylabel(r"areal radius $R/M$ (median shell of each group)")
    ax[0, 1].set_xlabel(r"proper time $\tau/M$", labelpad=-2)
    ax[0, 1].set_ylabel(r"$|R/R_{\rm exact}-1|$ while $R_{\rm exact}>2.5\,m$")
    ax[0, 1].set_ylim(1e-6, 1.0)
    t = hst[:, 0]
    ax[1, 0].semilogy(t, np.maximum(hst[:, 12], 1e-6), color=fs.PAL["red"], label="lapse at the centre")
    ax[1, 0].semilogy(t, np.maximum(hst[:, 15], 1e-6), color=fs.PAL["blue"], label="smallest lapse")
    ax[1, 0].semilogy(t, hst[:, 29], color=fs.PAL["yellow"], label="largest lapse")
    rt, rtau, ra, ral = central_lapse(ball, T, min(float(t[-1]), 14.0), dt=0.01)
    ax[1, 0].semilogy(rt, ral, color="k", ls=":", label="homogeneous reference")
    ax[1, 0].set_ylim(1e-4, 5.0)
    ax[1, 0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1, 0].set_ylabel("lapse")
    ax[1, 0].legend(fontsize=7)
    sel = t <= 10.0
    res["alpha_centre_dev_t10"] = float(np.abs(hst[sel, 12] / np.interp(t[sel], rt, ral) - 1.0).max())
    res["alpha_centre_t"] = {f"{tt:g}": float(np.interp(tt, t, hst[:, 12]))
                             for tt in (2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0)
                             if t[-1] >= tt}
    below = np.nonzero(hst[:, 12] < 0.05)[0]
    res["t_alpha_centre_below_0p05"] = float(t[below[0]]) if len(below) else None
    res["history"] = dict(t=t, alpha_c=hst[:, 12], np=hst[:, 2],
                          th=hz[:, 1] if len(hz) else np.zeros(0),
                          mh=hz[:, 2] if len(hz) else np.zeros(0))
    res["tau_centre_end"] = float(hst[-1, 14])
    res["n_excised"] = int(hst[-1, 16])
    if len(hz):
        th, mh = hz[:, 1], hz[:, 2]
        res["horizon"] = dict(searches=int(len(th)), t_first=float(th[0]), t_last=float(th[-1]),
                              mass_first=float(mh[0]), mass_last=float(mh[-1]),
                              mass_max=float(mh.max()))
        last = th >= th[-1] - 5.0
        res["horizon"]["spread_last_5M"] = float(mh[last].max() - mh[last].min())
        res["horizon"]["mass_t"] = {f"{tt:g}": float(np.interp(tt, th, mh))
                                    for tt in (26.0, 28.0, 30.0, 35.0, 40.0, 45.0)
                                    if th[0] <= tt <= th[-1]}
        # coordinate time at which the last particle has been removed, and the mass then
        gone = np.nonzero(hst[:, 2] == 0)[0]
        if len(gone) and th[-1] >= t[gone[0]]:
            res["horizon"]["t_all_removed"] = float(t[gone[0]])
            res["horizon"]["mass_all_removed"] = float(np.interp(t[gone[0]], th, mh))
            aft = th >= t[gone[0]]
            res["horizon"]["max_dev_from_M_after_removed"] = float(
                np.abs(mh[aft] / meta["M"] - 1.0).max())
        ax[1, 1].plot(th, mh, color=fs.PAL["red"])
        ax[1, 1].axhline(meta["M"], color="k", lw=0.6, ls="--")
        # proper time at the centre when the horizon is first found
        res["horizon"]["tau_centre_first"] = float(np.interp(th[0], t, hst[:, 14]))
    else:
        res["horizon"] = None
    ax[1, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1, 1].set_ylabel(r"apparent-horizon mass $/M$")
    fs.save(fig, os.path.join(FIGS, f"collapse_{pre}_{name}"))
    plt.close(fig)
    return res


def compare_collapse(pre, col):
    """Central lapse and horizon mass of the collapse runs in one figure."""
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.40)
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["yellow"]]
    for (name, r), c in zip(sorted(col.items()), cols):
        h = r["history"]
        ax[0].semilogy(h["t"], np.maximum(h["alpha_c"], 1e-6), color=c, label=name[len("collapse-"):])
        ax[1].plot(h["th"], h["mh"], color=c)
        ax[2].plot(h["t"], h["np"], color=c)
    ax[0].axhline(0.05, color="k", lw=0.6, ls=":")
    ax[0].set_ylim(1e-4, 3.0)
    ax[0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[0].set_ylabel("lapse at the centre")
    ax[0].legend(fontsize=7)
    ax[1].axhline(1.0, color="k", lw=0.6, ls="--")
    ax[1].axhspan(0.97, 1.03, color="0.9", zorder=0)
    ax[1].set_ylim(0.9, 1.1)
    ax[1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1].set_ylabel(r"apparent-horizon mass $/M$")
    ax[2].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[2].set_ylabel("particles in the run")
    fs.save(fig, os.path.join(FIGS, f"collapse_{pre}_compare"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="gc")
    ap.add_argument("--batch", nargs="*", default=[],
                    help="run ids of card jobs registered by nrpic-run (launcher batch)")
    a = ap.parse_args()
    pre = a.prefix
    os.makedirs(FIGS, exist_ok=True)
    fs.use_style()
    es, col = {}, {}
    todo = {tag[len(pre) + 1:]: m for tag, m in manifests(pre + "-").items()}
    for rid in a.batch:
        todo.update(batch_manifests(rid))
    for name, m in todo.items():
        if m.get("exit_status") != 0:
            print(f"{name}: run {m['run_id']} ended with exit status {m.get('exit_status')}: skipped")
            continue
        if name.startswith("es-") and os.path.exists(os.path.join(m["output_directory"], "es.traj.bin")):
            es[name] = analyse_es(pre, name, m)
        if name.startswith("collapse-") and os.path.exists(os.path.join(m["output_directory"], "ball.traj.bin")):
            col[name] = analyse_collapse(pre, name, m)
    if len(col) > 1:
        compare_collapse(pre, col)
    for r in col.values():
        r.pop("history", None)
    if es:
        with open(os.path.join(HERE, f"es_numbers_{pre}.json"), "w") as f:
            json.dump(es, f, indent=1)
            f.write("\n")
        print(json.dumps(es, indent=1))
    if col:
        with open(os.path.join(HERE, f"collapse_numbers_{pre}.json"), "w") as f:
            json.dump(col, f, indent=1)
            f.write("\n")
        print(json.dumps(col, indent=1))


if __name__ == "__main__":
    main()
