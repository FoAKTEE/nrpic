#!/usr/bin/env python3
"""Second-look analysis of the ES runs (es_runs, Track D; JOURNAL entries 6 and 7).

    es_extra.py --run NAME:DIR:BASE:KIND [--run ...] --data <make_data run dir>
                [--model <es1g_model.json>] [--out DIR] [--t0 100]

KIND is es (dust; exact model es_model.EinsteinStrausBH) or v1 (VacuumBubble). For every
run it measures
 1. wall (R0 = 36 M) on the axis and diagonal tracers at tau = 50, 100, 150, 200 M against
    the exact curve; the coordinate time at which each group's error first exceeds 2e-3;
 2. turnaround radius and time of the group R0 = 20 M against the exact LTB curve;
 3. lapse at the tracers of the plateau groups (R0 = 40, 48 M) against the homogeneous
    models (1+log and lapse_leak, from --model), and their proper time;
 4. K = Khat + 2 Theta on the x axis at the coordinate radius of the +x tracer of each
    plateau group (z = 0 slices of z4c) against -3H(tau) of the plateau;
 5. dust inside the wall along each particle's direction: the wall tracers' coordinate
    radius is fitted per snapshot as r_w(n) = a + b (n_x^4 + n_y^4 + n_z^4) (exact for the
    two classes axis/diagonal), and min(r - r_w(n)) over the dust is reported;
 6. space-time diagrams (x axis against t) of alpha, K and log10|H|;
 7. horizon mass of all runs, drift windows [t0, 165] and [165, end].
Writes DIR/es_extra.json and DIR/figs/extra_*.png,pdf.
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "D-bh-dress", "einstein_straus"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
import es_model as em  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from make_data import GEOM, VacuumBubble  # noqa: E402
from analyse import (read_horizon, read_named_hst, tracer_tracks, areal_and_tau, read_snapshot,  # noqa: E402
                     exact_groups, crossing, NTR)
from es1g_model import integrate  # noqa: E402

TAUS = (50.0, 100.0, 150.0, 200.0)


def axis_profile_series(run, base, kind, var_list):
    """Values along the positive x axis (cells next to y = 0 in the z = 0 slice; finest cell
    at each x, the two cells at y = +-dy/2 averaged) for every output of <base>.<kind>.*.bin."""
    import bin_convert
    files = sorted(glob.glob(os.path.join(run, "bin", f"{base}.{kind}.[0-9]*.bin")))
    out = []
    for p in files:
        fd = bin_convert.read_binary(p)
        rows = []
        nmb = (fd["nx1_mb"], fd["nx2_mb"], fd["nx3_mb"])
        for b in range(fd["n_mbs"]):
            g = fd["mb_geometry"][b]
            ix = fd["mb_index"][b]
            dxs = [(g[2 * k + 1] - g[2 * k]) / nmb[k] for k in range(3)]
            q0 = np.asarray(fd["mb_data"][var_list[0]][b], dtype=float)
            n3, n2, n1 = q0.shape
            xc = g[0] + (ix[0] + np.arange(n1) + 0.5) * dxs[0]
            yc = g[2] + (ix[2] + np.arange(n2) + 0.5) * dxs[1]
            jsel = np.where(np.abs(np.abs(yc) - 0.5 * dxs[1]) < 1e-9 * max(1.0, dxs[1]))[0]
            isel = np.where(xc > 0)[0]
            if len(jsel) == 0 or len(isel) == 0:
                continue
            for j in jsel:
                vals = [np.asarray(fd["mb_data"][v][b], dtype=float)[0, j, isel] for v in var_list]
                for k, i in enumerate(isel):
                    rows.append([xc[i], dxs[0]] + [vv[k] for vv in vals])
        if not rows:
            continue
        a = np.array(rows)
        keep = {}
        for row in a:
            key = round(row[0], 9)
            if key not in keep or row[1] < keep[key][0][1] - 1e-12:
                keep[key] = [row]
            elif abs(row[1] - keep[key][0][1]) < 1e-12:
                keep[key].append(row)
        ks = sorted(keep)
        vals = np.array([np.mean(keep[k], axis=0) for k in ks])
        # a coarse cell whose centre lies inside the span of finer cells is dropped
        x, dx = vals[:, 0], vals[:, 1]
        ok = np.ones(len(x), bool)
        for i in range(len(x)):
            finer = dx < dx[i] - 1e-12
            if finer.any() and np.any(np.abs(x[finer] - x[i]) < 0.5 * dx[i]):
                ok[i] = False
        vals = vals[ok]
        out.append(dict(time=float(fd["time"]), x=vals[:, 0], dx=vals[:, 1],
                        **{v: vals[:, 2 + i] for i, v in enumerate(var_list)}))
    return out


def on_axis(x0):
    return int(np.count_nonzero(np.abs(x0) > 1e-6)) == 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--t0", type=float, default=100.0)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    es_info = json.load(open(os.path.join(a.data, "es", "es.json")))
    esm = em.EinsteinStrausBH(**GEOM)
    vm = VacuumBubble(**GEOM)
    H0 = esm.H
    tm1, al1, tau1 = integrate(H0, None, 200.0, n=40001)
    tm2, al2, tau2 = integrate(H0, 2.0, 200.0, n=40001)
    models = {"1+log": (tm1, al1, tau1), "lapse_leak T=2M": (tm2, al2, tau2)}
    res = {"t0": a.t0, "runs": {}}
    data = {}
    for spec in a.run:
        name, d, base, kind = spec.split(":")
        model = esm if kind == "es" else vm
        groups = exact_groups(model, es_info["tracers"])
        tracks = tracer_tracks(d, base)
        per = {}
        for g in groups:
            for tag in g["tags"]:
                if tag not in tracks:
                    continue
                q = tracks[tag]
                R, tau, _, _, _ = areal_and_tau(q)
                Rex = em.ltb_radius(np.full_like(tau, g["R0"]), tau, g["m"], g["E"])
                per[tag] = dict(t=q["t"], tau=tau, R=R, rel=R / Rex - 1.0, alpha=q["alpha"], x=q["x"],
                                axis=on_axis(q["x"][0]), group=g["index"], R0=g["R0"])
        r = {}
        # 1. wall table and onset of the error growth
        wall = [g for g in groups if abs(g["R0"] - 36.0) < 1e-9][0]
        rows = {}
        for cls in ("axis", "diagonal"):
            tg = [t for t in wall["tags"] if t in per and per[t]["axis"] == (cls == "axis")]
            rows[cls] = {}
            for T in TAUS:
                v = [float(np.interp(T, per[t]["tau"], per[t]["R"])) for t in tg if per[t]["tau"][-1] >= T]
                rv = [float(np.interp(T, per[t]["tau"], per[t]["rel"])) for t in tg if per[t]["tau"][-1] >= T]
                if v:
                    rows[cls][f"tau={T:g}"] = dict(R_mean=float(np.mean(v)), rel_min=min(rv), rel_max=max(rv))
        rows["exact"] = {f"tau={T:g}": float(em.ltb_radius(np.array([36.0]), np.array([T]), wall["m"], wall["E"])[0])
                         for T in TAUS}
        r["wall"] = rows
        onset = []
        for g in groups:
            for cls in ("axis", "diagonal"):
                tg = [t for t in g["tags"] if t in per and per[t]["axis"] == (cls == "axis")]
                ts, taus, rs = [], [], []
                for t in tg:
                    p = per[t]
                    s = np.where((np.abs(p["rel"]) > 2e-3) & (p["R"] > 2.2))[0]
                    if len(s):
                        ts.append(float(p["t"][s[0]]))
                        taus.append(float(p["tau"][s[0]]))
                        rs.append(float(np.linalg.norm(p["x"][s[0]])))
                onset.append(dict(R0=g["R0"], cls=cls, n=len(tg), n_exceed=len(ts),
                                  t_onset=(float(np.median(ts)) if ts else None),
                                  tau_onset=(float(np.median(taus)) if taus else None),
                                  r_coord_onset=(float(np.median(rs)) if rs else None)))
        r["onset_2e-3"] = onset
        # 2. turnaround of the group R0 = 20 M
        g2 = [g for g in groups if abs(g["R0"] - 20.0) < 1e-9][0]
        te = np.linspace(0, 240, 240001)
        Re = em.ltb_radius(np.full_like(te, 20.0), te, g2["m"], g2["E"])
        tr = []
        for t in g2["tags"]:
            if t in per:
                i = int(np.argmax(per[t]["R"]))
                tr.append((float(per[t]["R"][i]), float(per[t]["tau"][i])))
        r["turnaround_R0_20"] = dict(R_max_exact=float(Re.max()), tau_max_exact=float(te[np.argmax(Re)]),
                                     R_max=[min(x[0] for x in tr), max(x[0] for x in tr)] if tr else None,
                                     tau_at_max=[min(x[1] for x in tr), max(x[1] for x in tr)] if tr else None)
        # 3. lapse and proper time at the plateau tracers
        plat = {}
        for R0 in (40.0, 48.0):
            g = [g for g in groups if abs(g["R0"] - R0) < 1e-9][0]
            tg = [t for t in g["tags"] if t in per]
            rec = {}
            for T in (10.0, 25.0, 50.0, 100.0, 150.0, 200.0):
                al = [float(np.interp(T, per[t]["t"], per[t]["alpha"])) for t in tg if per[t]["t"][-1] >= T - 1e-9]
                ta = [float(np.interp(T, per[t]["t"], per[t]["tau"])) for t in tg if per[t]["t"][-1] >= T - 1e-9]
                if al:
                    rec[f"t={T:g}"] = dict(alpha=[min(al), max(al)], tau=[min(ta), max(ta)],
                                           **{f"alpha_model[{k}]": float(np.interp(T, m[0], m[1])) for k, m in models.items()},
                                           **{f"tau_model[{k}]": float(np.interp(T, m[0], m[2])) for k, m in models.items()})
            plat[f"R0={R0:g}"] = rec
        r["plateau_tracers"] = plat
        # 4. K at the +x tracer of the plateau groups, from the z = 0 slices
        prof = axis_profile_series(d, base, "z4c", ("z4c_alpha", "z4c_Khat", "z4c_Theta"))
        con = axis_profile_series(d, base, "con", ("con_H",))
        kt = {}
        for R0 in (40.0, 48.0):
            g = [g for g in groups if abs(g["R0"] - R0) < 1e-9][0]
            tx = [t for t in g["tags"] if t in per and per[t]["axis"] and per[t]["x"][0][0] > 0]
            if not tx:
                continue
            p = per[tx[0]]
            rows_k = []
            for pr in prof:
                T = pr["time"]
                if T > p["t"][-1] + 1e-9:
                    continue
                xp = float(np.interp(T, p["t"], p["x"][:, 0]))
                taup = float(np.interp(T, p["t"], p["tau"]))
                K = float(np.interp(xp, pr["x"], pr["z4c_Khat"] + 2.0 * pr["z4c_Theta"]))
                alx = float(np.interp(xp, pr["x"], pr["z4c_alpha"]))
                Hp = H0 / (1.0 + 1.5 * H0 * taup)
                rows_k.append(dict(t=T, x=xp, tau=taup, K=K, minus3H=-3.0 * Hp, K_over_minus3H=K / (-3.0 * Hp),
                                   alpha_slice=alx))
            kt[f"R0={R0:g}"] = rows_k
        r["K_at_plateau_tracer"] = kt
        # 5. dust inside the wall, direction by direction
        dw = []
        wall_tags = [t for t in wall["tags"] if t in per]
        for pth in sorted(glob.glob(os.path.join(d, f"{base}.part.[0-9]*.bin"))):
            s = read_snapshot(pth)
            if s is None:
                continue
            T, rec, tags = s
            dust = tags >= NTR
            if not dust.any():
                continue
            xw, s4w = [], []
            for t in wall_tags:
                q = per[t]
                if q["t"][0] - 1e-9 <= T <= q["t"][-1] + 1e-9:
                    xx = np.array([np.interp(T, q["t"], q["x"][:, k]) for k in range(3)])
                    rr = np.linalg.norm(xx)
                    xw.append(rr)
                    s4w.append(float(np.sum((xx / rr) ** 4)))
            if len(xw) < 3:
                continue
            A = np.vstack([np.ones(len(xw)), s4w]).T
            coef, *_ = np.linalg.lstsq(A, np.array(xw), rcond=None)
            fit_res = float(np.max(np.abs(A @ coef - np.array(xw))))
            xd = rec[dust, :3]
            rd = np.linalg.norm(xd, axis=1)
            s4 = np.sum((xd / rd[:, None]) ** 4, axis=1)
            margin = rd - (coef[0] + coef[1] * s4)
            i = int(np.argmin(margin))
            dw.append(dict(t=float(T), wall_a=float(coef[0]), wall_b=float(coef[1]), wall_fit_residual=fit_res,
                           margin_min=float(margin[i]), margin_q001=float(np.quantile(margin, 1e-3)),
                           n_inside=int(np.sum(margin < 0.0)), n_inside_1M=int(np.sum(margin < -1.0)),
                           x_of_min=[float(v) for v in xd[i]]))
        r["dust_wall_directional"] = dw
        # 7. horizon mass
        S = read_horizon(os.path.join(d, f"{base}.horizon_summary_0.txt"))
        Hh = read_named_hst(os.path.join(d, f"{base}.nrpic.hst"))
        if S is not None and S["time"][-1] >= a.t0:
            M0 = float(np.interp(a.t0, S["time"], S["mass"]))
            wins = {}
            for lo, hi in ((a.t0, 165.0), (165.0, 1e9), (a.t0, 1e9), (25.0, 50.0)):
                s_ = (S["time"] >= lo) & (S["time"] <= hi)
                if s_.any():
                    dd = S["mass"][s_] / M0 - 1.0
                    wins[f"[{lo:g},{min(hi, S['time'][-1]):g}]"] = [float(dd.min()), float(dd.max())]
            r["horizon"] = dict(M_t0=M0, offset=M0 - 1.0, drift_windows=wins, t_last=float(S["time"][-1]))
        if Hh is not None:
            r["hst"] = dict(t_last=float(Hh["time"][-1]), alpha_max_after_10=float(np.max(Hh["alpha_max"][Hh["time"] >= 10.0])),
                            alpha_max_overall=float(np.max(Hh["alpha_max"])),
                            alpha_min_range=[float(Hh["alpha_min"].min()), float(Hh["alpha_min"].max())],
                            np_last=int(Hh["np"][-1]), n_excised_last=int(Hh["n_excised"][-1]),
                            n_escaped_last=int(Hh["n_escaped"][-1]), sum_m_first=float(Hh["sum_m"][0]),
                            sum_m_last=float(Hh["sum_m"][-1]), push_unconverged_max=int(np.max(Hh["push_unconverged"])),
                            finite=bool(np.all(np.isfinite(Hh["sum_mW"]))))
        res["runs"][name] = r
        data[name] = dict(per=per, groups=groups, prof=prof, con=con, S=S, H=Hh, kind=kind)
    with open(os.path.join(a.out, "es_extra.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1)[:20000])
    figures(a, data, res, models, H0)


def figures(a, data, res, models, H0):
    fs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    figs = os.path.join(a.out, "figs")
    names = list(data)
    pal = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"], fs.PAL.get("green", "k")]
    col = {n: pal[i % len(pal)] for i, n in enumerate(names)}

    # A. tracer error against coordinate time
    fig, axs = plt.subplots(len(names), 1, figsize=(fs.COLUMN_WIDTH * 1.6, 2.6 * len(names)), sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.08, top=0.98, hspace=0.06)
    for j, n in enumerate(names):
        ax = axs[j, 0]
        d = data[n]
        cc = fs.series_colors(len(d["groups"]))
        for g, c in zip(d["groups"], cc):
            first = True
            for tag in g["tags"]:
                p = d["per"].get(tag)
                if p is None:
                    continue
                s = p["R"] > 2.2
                ax.plot(p["t"][s], p["rel"][s], color=c, lw=0.9 if p["axis"] else 0.5, ls="-" if p["axis"] else ":",
                        label=(f"$R_0={g['R0']:g}M$" if first else None))
                first = False
        ax.axhline(2e-3, **fs.GUIDE)
        ax.axhline(-2e-3, **fs.GUIDE)
        ax.set_ylim(-0.02, 0.02)
        ax.set_ylabel(r"$R/R_{\rm exact}-1$")
        ax.text(0.02, 0.88, n + "; solid: axes, dotted: diagonals", transform=ax.transAxes, fontsize=8)
        if j == 0:
            ax.legend(loc="lower left", ncol=4, fontsize=6)
    axs[-1, 0].set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "extra_tracers_vs_t"))
    plt.close(fig)

    # B. space-time diagrams along x
    for n in names:
        d = data[n]
        prof, con = d["prof"], d["con"]
        if not prof:
            continue
        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
        fig.subplots_adjust(left=0.07, right=0.97, bottom=0.15, top=0.90, wspace=0.08)
        xg = np.logspace(np.log10(0.1), np.log10(190.0), 300)

        def grid(series, fn):
            T = np.array([p["time"] for p in series])
            Z = np.array([np.interp(xg, p["x"], fn(p)) for p in series])
            return T, Z
        T, Z = grid(prof, lambda p: p["z4c_alpha"])
        m0 = axs[0].pcolormesh(xg, T, Z, shading="nearest", cmap="viridis", norm=LogNorm(vmin=0.01, vmax=2.5))
        fig.colorbar(m0, ax=axs[0], orientation="horizontal", location="top", pad=0.02, label=r"$\alpha$")
        T, Z = grid(prof, lambda p: p["z4c_Khat"] + 2 * p["z4c_Theta"])
        m1 = axs[1].pcolormesh(xg, T, Z, shading="nearest", cmap="RdBu_r", vmin=-0.03, vmax=0.03)
        fig.colorbar(m1, ax=axs[1], orientation="horizontal", location="top", pad=0.02, label=r"$K\,M$")
        if con:
            T, Z = grid(con, lambda p: np.log10(np.abs(p["con_H"]) + 1e-30))
            m2 = axs[2].pcolormesh(xg, T, Z, shading="nearest", cmap="magma", vmin=-12, vmax=-4)
            fig.colorbar(m2, ax=axs[2], orientation="horizontal", location="top", pad=0.02, label=r"$\log_{10}|H|$")
        for ax in axs:
            ax.set_xscale("log")
            ax.set_xlabel(r"$x/M$")
            for xx in (36.0, 60.0, 192.0):
                ax.axvline(xx, **fs.MASK_LINE)
        axs[0].set_ylabel(r"$t/M$ (" + n + ")")
        fs.save(fig, os.path.join(figs, f"extra_spacetime_{n}"))
        plt.close(fig)

    # C. plateau: lapse at the tracers, proper time, K at the +x tracer
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.96, wspace=0.32)
    for k, (t, al, tau) in models.items():
        axs[0].plot(t, al, **dict(fs.GUIDE, color="k" if k == "1+log" else "0.5", label=f"model {k}"))
        axs[1].plot(t, tau, **dict(fs.GUIDE, color="k" if k == "1+log" else "0.5"))
    for n in names:
        d = data[n]
        first = True
        for tag, p in d["per"].items():
            if abs(p["R0"] - 48.0) < 1e-9:
                axs[0].plot(p["t"], p["alpha"], color=col[n], lw=0.7, label=(n if first else None))
                axs[1].plot(p["t"], p["tau"], color=col[n], lw=0.7)
                first = False
        kt = res["runs"][n].get("K_at_plateau_tracer", {}).get("R0=48", [])
        if kt:
            axs[2].plot([r_["t"] for r_ in kt], [r_["K"] for r_ in kt], "o-", color=col[n], ms=3, label=f"{n}: $K$")
            axs[2].plot([r_["t"] for r_ in kt], [r_["minus3H"] for r_ in kt], "--", color=col[n], lw=0.8,
                        label=f"{n}: $-3H(\\tau)$")
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"$\alpha$ at the tracers $R_0=48M$")
    axs[1].set_ylabel(r"proper time $\tau/M$")
    axs[2].set_ylabel(r"$K\,M$ at the $+x$ tracer $R_0=48M$")
    for ax in axs:
        ax.set_xlabel(r"coordinate time $t/M$")
    axs[0].legend(loc="upper left", fontsize=7)
    axs[2].legend(loc="lower right", fontsize=6)
    fs.save(fig, os.path.join(figs, "extra_plateau"))
    plt.close(fig)

    # D. dust against the wall, direction by direction
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.97)
    for n in names:
        dw = res["runs"][n]["dust_wall_directional"]
        if dw:
            ax.plot([r_["t"] for r_ in dw], [r_["margin_min"] for r_ in dw], "o-", color=col[n], ms=3, label=f"{n}: min")
            ax.plot([r_["t"] for r_ in dw], [r_["margin_q001"] for r_ in dw], "s--", color=col[n], ms=3, lw=0.8,
                    label=f"{n}: 0.1% quantile")
    ax.axhline(0.0, **fs.MASK_LINE)
    ax.set_xlabel(r"coordinate time $t/M$")
    ax.set_ylabel(r"$r_{\rm dust}-r_{\rm wall}(\hat n)$ $(M)$")
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(figs, "extra_dust_wall"))
    plt.close(fig)

    # E. horizon masses
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.0), sharex=True)
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.09, top=0.98, hspace=0.06)
    for n in names:
        S = data[n]["S"]
        if S is None:
            continue
        axs[0].plot(S["time"], S["mass"] - 1.0, color=col[n], label=n)
        if S["time"][-1] >= a.t0:
            M0 = np.interp(a.t0, S["time"], S["mass"])
            s = S["time"] >= 20.0
            axs[1].plot(S["time"][s], S["mass"][s] / M0 - 1.0, color=col[n], label=n)
    axs[0].set_ylim(5e-4, 1.4e-3)
    axs[0].set_ylabel(r"$M_{\rm AH}/M-1$")
    axs[0].legend(loc="lower left", ncol=3)
    axs[1].axvline(a.t0, **fs.MASK_LINE)
    axs[1].axvline(165.0, **fs.MASK_LINE)
    axs[1].set_ylim(-4e-4, 4e-4)
    axs[1].set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(%g\,M)-1$" % a.t0)
    axs[1].set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "extra_horizon"))
    plt.close(fig)


if __name__ == "__main__":
    main()
