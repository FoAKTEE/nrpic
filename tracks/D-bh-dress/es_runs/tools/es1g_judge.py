#!/usr/bin/env python3
"""Numbers for judging ES-1G against JOURNAL entry 5 that es_extra.py does not give (es_runs,
Track D; JOURNAL entry 9).

    es1g_judge.py --run NAME:DIR:BASE [--run ...] --data <make_data run dir> [--out DIR]
                  [--t0 100]

Run names used: ES-1G (lapse_leak, T = 2 M), ES-1 (1+log), V-1 (vacuum control, 1+log),
core-ES (core's 30 M lapse_leak run on the same table, core-20261115-202901-b4430da). All
runs share the tracer groups of the ES data (tags 0-139, ten groups of 14). For every run:
 A. lapse at the tracers of the groups R0 = 36 (wall), 40 (inner dust edge), 48 (plateau),
    56 M (outer part of the dust) against the homogeneous lapse_leak model (es1g_model.py,
    T = 2 M): max |alpha/alpha_model - 1| over 10 <= t <= t_end, the start-up window
    0 <= t <= 10 M, smallest and largest lapse at any time; the tracers' Lorentz factor
    against the normal observers, W = alpha dt/dtau, and v = (1 - 1/W^2)^(1/2);
 B. history (<base>.nrpic.hst): mesh maximum of the lapse (column 30) after t = 10 M; mesh
    minimum (column 16) against alpha_exc = 0.05: intervals with alpha_min > 0.05;
    finiteness, particle count, escapes, rest mass, unconverged pushes;
 C. probes (x = 1, 4, 20, 36, 46, 56, 80, 152 M, if the run has them): lapse at fixed times,
    rms of the detrended d alpha/dt (probe_fronts.py) over t = 10-40 M, first time the lapse
    differs from V-1's at the same probe by more than 1e-3;
 D. horizon (finder summary): M_AH at 10, 30, 100, 165 M and the last time, drift windows
    from t0 ([t0,165], [t0,end]) with a straight-line slope, mean coordinate radius;
 E. wall tracers (tags 56-69) by class (axis, diagonal): max |R/R_exact - 1| over the whole
    run and over tau <= 200 M.
Writes DIR/es1g_judge.json and DIR/figs/judge_*.png,pdf.
"""
import argparse
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
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
import es_model as em  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from make_data import GEOM  # noqa: E402
from analyse import read_horizon, read_named_hst, tracer_tracks, areal_and_tau, exact_groups  # noqa: E402
from es1g_model import integrate  # noqa: E402
from probe_fronts import PROBES, detrended_rate  # noqa: E402

ALPHA_EXC = 0.05


def on_axis(x0):
    return int(np.count_nonzero(np.abs(x0) > 1e-6)) == 1


def intervals_above(t, y, level):
    """[t_start, t_end, max] of every maximal run of samples with y > level."""
    out = []
    above = y > level
    i = 0
    n = len(t)
    while i < n:
        if above[i]:
            j = i
            while j + 1 < n and above[j + 1]:
                j += 1
            out.append([float(t[i]), float(t[j]), float(np.max(y[i:j + 1]))])
            i = j + 1
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--t0", type=float, default=100.0)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    es_info = json.load(open(os.path.join(a.data, "es", "es.json")))
    esm = em.EinsteinStrausBH(**GEOM)
    tm, alm, taum = integrate(esm.H, 2.0, 200.0, n=40001)        # lapse_leak, T = 2 M
    tm1, alm1, _ = integrate(esm.H, None, 200.0, n=40001)        # 1+log
    groups = exact_groups(esm, es_info["tracers"])
    res = {"t0": a.t0, "alpha_exc": ALPHA_EXC, "runs": {}}
    data = {}
    for spec in a.run:
        name, d, base = spec.split(":")
        tracks = tracer_tracks(d, base)
        H = read_named_hst(os.path.join(d, f"{base}.nrpic.hst"))
        S = read_horizon(os.path.join(d, f"{base}.horizon_summary_0.txt"))
        r = {"dir": d}
        t_end = float(H["time"][-1])
        # A. lapse at the tracers against the lapse_leak model
        lap = {}
        per = {}
        for g in groups:
            for tag in g["tags"]:
                if tag in tracks:
                    q = tracks[tag]
                    R, tau, _, _, _ = areal_and_tau(q)
                    Rex = em.ltb_radius(np.full_like(tau, g["R0"]), tau, g["m"], g["E"])
                    per[tag] = dict(t=q["t"], alpha=q["alpha"], tau=tau, R=R, rel=R / Rex - 1.0,
                                    axis=on_axis(q["x"][0]), R0=g["R0"])
        for R0 in (36.0, 40.0, 48.0, 56.0):
            g = [g for g in groups if abs(g["R0"] - R0) < 1e-9][0]
            tg = [t for t in g["tags"] if t in per]
            rec = dict(n=len(tg))
            late, early, amin, amax = [], [], [], []
            wv = {}
            for t in tg:
                p = per[t]
                ratio = p["alpha"] / np.interp(p["t"], tm, alm) - 1.0
                s = p["t"] >= 10.0
                if s.any():
                    k = int(np.argmax(np.abs(ratio[s])))
                    late.append((float(np.abs(ratio[s])[k]), float(ratio[s][k]), float(p["t"][s][k])))
                s0 = p["t"] <= 10.0
                if s0.any():
                    early.append((float(ratio[s0].min()), float(ratio[s0].max())))
                k1 = int(np.argmin(p["alpha"]))
                k2 = int(np.argmax(p["alpha"]))
                amin.append((float(p["alpha"][k1]), float(p["t"][k1])))
                amax.append((float(p["alpha"][k2]), float(p["t"][k2])))
                # Lorentz factor of the tracer against the normal observers, W = alpha dt/dtau
                W = p["alpha"] / np.gradient(p["tau"], p["t"])
                for T in (10.0, 25.0, 50.0, 100.0, 150.0, 200.0):
                    if p["t"][0] <= T <= p["t"][-1] + 1e-9:
                        Wt = float(np.interp(T, p["t"], W))
                        wv.setdefault(f"t={T:g}", []).append(Wt)
            if late:
                w = max(late)
                rec["max_abs_ratio_minus1_t>=10"] = w[0]
                rec["signed_at_max"] = w[1]
                rec["t_at_max"] = w[2]
            if early:
                rec["ratio_minus1_t<=10"] = [min(e[0] for e in early), max(e[1] for e in early)]
            if amin:
                rec["alpha_min"] = list(min(amin))
                rec["alpha_max"] = list(max(amax))
            rec["W"] = {k: [min(v), max(v)] for k, v in wv.items()}
            rec["v_rel"] = {k: [float(np.sqrt(max(0.0, 1.0 - 1.0 / min(v) ** 2))),
                                float(np.sqrt(max(0.0, 1.0 - 1.0 / max(v) ** 2)))] for k, v in wv.items()}
            lap[f"R0={R0:g}"] = rec
        r["tracer_lapse_vs_leak_model"] = lap
        # B. history
        t = H["time"]
        r["hst"] = dict(t_last=t_end, np_first=int(H["np"][0]), np_last=int(H["np"][-1]),
                        n_excised_last=int(H["n_excised"][-1]), n_escaped_last=int(H["n_escaped"][-1]),
                        sum_m_first=float(H["sum_m"][0]), sum_m_last=float(H["sum_m"][-1]),
                        push_unconverged_max=int(np.max(H["push_unconverged"])),
                        finite=bool(np.all(np.isfinite(H["sum_mW"])) and np.all(np.isfinite(H["alpha_min"]))),
                        alpha_max_after_10=float(np.max(H["alpha_max"][t >= 10.0])),
                        t_of_alpha_max_after_10=float(t[t >= 10.0][np.argmax(H["alpha_max"][t >= 10.0])]),
                        alpha_max_overall=float(np.max(H["alpha_max"])),
                        t_of_alpha_max_overall=float(t[np.argmax(H["alpha_max"])]),
                        alpha_max_at={f"t={T:g}": float(np.interp(T, t, H["alpha_max"])) for T in (5, 10, 30, 50, 100, 200)
                                      if T <= t_end},
                        alpha_min_at={f"t={T:g}": float(np.interp(T, t, H["alpha_min"])) for T in (5, 10, 30, 50, 100, 200)
                                      if T <= t_end},
                        alpha_min_range=[float(np.min(H["alpha_min"])), float(np.max(H["alpha_min"]))])
        iv = intervals_above(t, H["alpha_min"], ALPHA_EXC)
        r["alpha_min_above_exc"] = dict(n_intervals=len(iv), total_time=float(sum(x[1] - x[0] for x in iv)),
                                        intervals=iv[:20],
                                        after_50=[x for x in iv if x[1] >= 50.0][:20])
        # C. probes
        if "alpha_probe1" in H:
            pr = {}
            for key, x in PROBES:
                tg_, y = detrended_rate(t, H[key])
                s = (tg_ >= 10.0) & (tg_ <= 40.0)
                pr[f"x={x:g}"] = dict(at={f"t={T:g}": float(np.interp(T, t, H[key])) for T in (0, 5, 10, 25, 50, 100, 150, 200)
                                          if T <= t_end},
                                      rms_detrended_rate_10_40=float(np.sqrt(np.mean(y[s] ** 2))))
            r["probes"] = pr
        # D. horizon
        if S is not None:
            hz = dict(t_first=float(S["time"][0]), t_last=float(S["time"][-1]), n=int(len(S["time"])))
            hz["M_at"] = {f"t={T:g}": float(np.interp(T, S["time"], S["mass"])) for T in (10, 20, 30, 100, 165)
                          if T <= S["time"][-1]}
            hz["M_last"] = float(S["mass"][-1])
            hz["meanradius_at"] = {f"t={T:g}": float(np.interp(T, S["time"], S["meanradius"]))
                                   for T in (0, 10, 25, 50, 100, 165, 200) if T <= S["time"][-1] + 0.5}
            if S["time"][-1] >= 30.0:
                hz["M30_over_M10_minus1"] = hz["M_at"]["t=30"] / hz["M_at"]["t=10"] - 1.0
                s = (S["time"] >= 0.0) & (S["time"] <= 30.0)
                hz["range_0_30"] = [float(S["mass"][s].min()), float(S["mass"][s].max())]
            if S["time"][-1] >= a.t0:
                M0 = float(np.interp(a.t0, S["time"], S["mass"]))
                hz["M_t0"] = M0
                wins = {}
                for lo, hi in ((a.t0, 165.0), (a.t0, 1e9), (165.0, 1e9)):
                    s = (S["time"] >= lo) & (S["time"] <= hi)
                    dd = S["mass"][s] / M0 - 1.0
                    sl = float(np.polyfit(S["time"][s], dd, 1)[0]) if s.sum() > 2 else None
                    wins[f"[{lo:g},{min(hi, S['time'][-1]):g}]"] = dict(min=float(dd.min()), max=float(dd.max()),
                                                                         end=float(dd[-1]), slope_per_M=sl)
                hz["drift_windows"] = wins
            r["horizon"] = hz
        # E. wall by class
        wall = [g for g in groups if abs(g["R0"] - 36.0) < 1e-9][0]
        wr = {}
        for cls in ("axis", "diagonal"):
            tg = [x for x in wall["tags"] if x in per and per[x]["axis"] == (cls == "axis")]
            best, best200 = (0.0, None, None), (0.0, None, None)
            for x in tg:
                p = per[x]
                ok = np.isfinite(p["rel"])
                k = int(np.argmax(np.abs(p["rel"][ok])))
                v = (float(np.abs(p["rel"][ok])[k]), float(p["t"][ok][k]), float(p["tau"][ok][k]))
                best = max(best, v, key=lambda z: z[0])
                s = ok & (p["tau"] <= 200.0)
                if s.any():
                    k = int(np.argmax(np.abs(p["rel"][s])))
                    v = (float(np.abs(p["rel"][s])[k]), float(p["t"][s][k]), float(p["tau"][s][k]))
                    best200 = max(best200, v, key=lambda z: z[0])
            wr[cls] = dict(n=len(tg), max_abs_rel=best[0], t_at=best[1], tau_at=best[2],
                           max_abs_rel_tau_le_200=best200[0], tau_end=[float(min(per[x]["tau"][-1] for x in tg)),
                                                                        float(max(per[x]["tau"][-1] for x in tg))])
        r["wall_by_class"] = wr
        res["runs"][name] = r
        data[name] = dict(per=per, H=H, S=S)
    # C'. probe departures from V-1
    if "V-1" in data and "alpha_probe1" in data["V-1"]["H"]:
        Hv = data["V-1"]["H"]
        for n in data:
            Hn = data[n]["H"]
            if n == "V-1" or "alpha_probe1" not in Hn:
                continue
            dep = {}
            for key, x in PROBES:
                tc = Hn["time"][Hn["time"] <= Hv["time"][-1]]
                da = np.abs(np.interp(tc, Hn["time"], Hn[key]) - np.interp(tc, Hv["time"], Hv[key]))
                i3 = np.where(da > 1e-3)[0]
                i6 = np.where(da > 1e-6)[0]
                dep[f"x={x:g}"] = {"t_first_1e-3": (float(tc[i3[0]]) if len(i3) else None),
                                   "t_first_1e-6": (float(tc[i6[0]]) if len(i6) else None)}
            res["runs"][n]["probe_departure_from_V1"] = dep
    with open(os.path.join(a.out, "es1g_judge.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1)[:30000])
    figures(a, data, res, (tm, alm, tm1, alm1))


def figures(a, data, res, models):
    fs.use_style()
    import matplotlib.pyplot as plt
    tm, alm, tm1, alm1 = models
    figs = os.path.join(a.out, "figs")
    pal = {"ES-1G": fs.PAL["red"], "ES-1": fs.PAL["blue"], "V-1": fs.PAL["yellow"], "core-ES": "k"}
    lsg = {36.0: (0, (1, 1)), 40.0: ":", 48.0: "-", 56.0: "--"}

    # 1. lapse in the dust against the model, and the mesh maximum
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.95, wspace=0.45)
    axs[0].plot(tm, alm, color="0.4", lw=1.6, label="model, lapse_leak $T=2M$")
    axs[0].plot(tm1, alm1, **dict(fs.GUIDE, color="0.6", label="model, 1+log"))
    for n in ("ES-1G", "ES-1"):
        if n not in data:
            continue
        seen = set()
        for tag, p in data[n]["per"].items():
            if p["R0"] in (40.0, 48.0, 56.0) and (n == "ES-1G" or p["R0"] == 48.0):
                lab = f"{n} $R_0={p['R0']:g}M$" if (p["R0"] not in seen) else None
                seen.add(p["R0"])
                axs[0].plot(p["t"], p["alpha"], color=pal[n], lw=0.6, ls=lsg[p["R0"]], label=lab)
                if n == "ES-1G":
                    axs[1].plot(p["t"], p["alpha"] / np.interp(p["t"], tm, alm) - 1.0, color=pal[n], lw=0.6,
                                ls=lsg[p["R0"]], label=lab)
    axs[0].set_ylim(0.9, 2.2)
    axs[0].set_ylabel(r"$\alpha$ at the dust tracers")
    axs[0].legend(loc="upper right", fontsize=6)
    for y in (0.03, -0.03):
        axs[1].axhline(y, **fs.GUIDE)
    axs[1].axhline(0.0, **fs.MASK_LINE)
    axs[1].set_ylim(-0.12, 0.12)
    axs[1].set_ylabel(r"ES-1G: $\alpha/\alpha_{\rm model}-1$ (lapse_leak)")
    axs[1].legend(loc="lower right", fontsize=6)
    for n in ("ES-1G", "ES-1", "V-1"):
        if n in data:
            H = data[n]["H"]
            axs[2].plot(H["time"], H["alpha_max"], color=pal[n], lw=0.9, label=n)
    for y in (1.2, 1.3):
        axs[2].axhline(y, **fs.GUIDE)
    axs[2].set_ylabel(r"largest $\alpha$ on the mesh")
    axs[2].legend(loc="upper right", fontsize=7)
    for ax in axs:
        ax.set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "judge_lapse"))
    plt.close(fig)

    # 2. near the hole: mesh minimum of the lapse, probes, detrended rates
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.95, wspace=0.34)
    for n in ("ES-1G", "ES-1", "V-1"):
        if n in data:
            H = data[n]["H"]
            axs[0].plot(H["time"], H["alpha_min"], color=pal[n], lw=0.8, label=n)
    axs[0].axhline(ALPHA_EXC, **fs.GUIDE)
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"smallest $\alpha$ on the mesh")
    axs[0].legend(loc="upper right", fontsize=7)
    sty = {"ES-1G": "-", "ES-1": "--", "V-1": ":"}
    cx = {"alpha_probe1": fs.PAL["red"], "alpha_probe2": fs.PAL["blue"], "alpha_probe3": fs.PAL["yellow"]}
    for n in ("ES-1G", "ES-1", "V-1"):
        if n not in data or "alpha_probe1" not in data[n]["H"]:
            continue
        H = data[n]["H"]
        s = H["time"] <= 60.0
        for key, x in PROBES[:3]:
            axs[1].plot(H["time"][s], H[key][s], color=cx[key], ls=sty[n], lw=0.8,
                        label=(f"$x={x:g}M$" if n == "ES-1G" else None))
        for key, x in PROBES[1:3]:
            tg, y = detrended_rate(H["time"], H[key])
            s2 = tg <= 60.0
            axs[2].plot(tg[s2], y[s2], color=cx[key], ls=sty[n], lw=0.8,
                        label=(f"{n} $x={x:g}M$"))
    axs[1].set_ylabel(r"$\alpha$ at the probes (solid ES-1G, dashed ES-1, dotted V-1)", fontsize=7)
    axs[1].legend(loc="lower right", fontsize=7)
    axs[2].set_ylabel(r"detrended $d\alpha/dt$ $(1/M)$")
    axs[2].legend(loc="upper right", fontsize=5)
    for ax in axs:
        ax.set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "judge_hole"))
    plt.close(fig)

    # 3. horizon: mass, drift from t0, coordinate radius (axes scaled to the data)
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 7.0), sharex=True)
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.07, top=0.98, hspace=0.07)
    for n in ("ES-1G", "ES-1", "V-1", "core-ES"):
        if n not in data or data[n]["S"] is None:
            continue
        S = data[n]["S"]
        axs[0].plot(S["time"], S["mass"] - 1.0, color=pal[n], lw=0.9, label=n)
        if S["time"][-1] >= a.t0:
            M0 = np.interp(a.t0, S["time"], S["mass"])
            s = S["time"] >= a.t0
            axs[1].plot(S["time"][s], S["mass"][s] / M0 - 1.0, color=pal[n], lw=0.9, label=n)
        axs[2].plot(S["time"], S["meanradius"], color=pal[n], lw=0.9, label=n)
    axs[0].set_ylabel(r"$M_{\rm AH}/M-1$")
    axs[0].set_yscale("symlog", linthresh=1e-4)
    axs[0].legend(loc="upper left", fontsize=7)
    axs[1].axvline(165.0, **fs.MASK_LINE)
    axs[1].axhline(0.0, **fs.MASK_LINE)
    axs[1].set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(%g\,M)-1$" % a.t0)
    axs[1].set_yscale("symlog", linthresh=1e-4)
    axs[2].set_ylabel(r"horizon mean coordinate radius $(M)$")
    axs[2].set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "judge_horizon"))
    plt.close(fig)

    # 4. overlap with core's 30 M run
    if "core-ES" in data:
        fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0), sharex=True)
        fig.subplots_adjust(left=0.11, right=0.98, bottom=0.10, top=0.97, wspace=0.28, hspace=0.08)
        for n in ("ES-1G", "core-ES", "ES-1", "V-1"):
            if n not in data:
                continue
            S, H = data[n]["S"], data[n]["H"]
            lw = 1.0 if n in ("ES-1G", "core-ES") else 0.6
            if S is not None:
                s = S["time"] <= 30.0
                axs[0, 0].plot(S["time"][s], S["mass"][s] - 1.0, color=pal[n], lw=lw, label=n)
            s = H["time"] <= 30.0
            axs[0, 1].plot(H["time"][s], H["alpha_max"][s], color=pal[n], lw=lw, label=n)
            axs[1, 1].plot(H["time"][s], H["alpha_min"][s], color=pal[n], lw=lw, label=n)
            if n in ("ES-1G", "core-ES"):
                seen = set()
                for tag, p in data[n]["per"].items():
                    if p["R0"] in (40.0, 48.0, 56.0):
                        s = p["t"] <= 30.0
                        lab = f"{n} $R_0={p['R0']:g}M$" if p["R0"] not in seen else None
                        seen.add(p["R0"])
                        axs[1, 0].plot(p["t"][s], p["alpha"][s], color=pal[n], lw=0.6, ls=lsg[p["R0"]], label=lab)
        s = tm <= 30.0
        axs[1, 0].plot(tm[s], alm[s], color="0.5", lw=1.6, alpha=0.6, label="model lapse_leak")
        axs[0, 0].set_ylabel(r"$M_{\rm AH}/M-1$")
        axs[0, 0].legend(loc="lower right", fontsize=7)
        axs[0, 1].set_ylabel(r"largest $\alpha$ on the mesh")
        axs[0, 1].set_ylim(0.95, 2.6)
        axs[1, 0].set_ylabel(r"$\alpha$ at the dust tracers")
        axs[1, 0].set_ylim(0.98, 1.2)
        axs[1, 0].legend(loc="upper right", fontsize=5, ncol=2)
        axs[1, 1].axhline(ALPHA_EXC, **fs.GUIDE)
        axs[1, 1].set_yscale("log")
        axs[1, 1].set_ylabel(r"smallest $\alpha$ on the mesh")
        for ax in axs[1]:
            ax.set_xlabel(r"coordinate time $t/M$")
        fs.save(fig, os.path.join(figs, "judge_core30"))
        plt.close(fig)

    # 5. wall tracers against the exact curve, by class, whole run
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.0))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.16, top=0.97)
    for n in ("ES-1G", "ES-1", "V-1"):
        if n not in data:
            continue
        first = True
        for tag, p in data[n]["per"].items():
            if p["R0"] == 36.0:
                ax.plot(p["tau"], p["rel"], color=pal[n], lw=0.8 if p["axis"] else 0.5, ls="-" if p["axis"] else ":",
                        label=(n if first else None))
                first = False
    for y in (3e-3, -3e-3):
        ax.axhline(y, **fs.GUIDE)
    ax.set_ylim(-0.02, 0.02)
    ax.set_xlabel(r"proper time of the wall tracers $\tau/M$")
    ax.set_ylabel(r"$R/R_{\rm exact}-1$ (solid axes, dotted diagonals)", fontsize=7)
    ax.legend(loc="lower left", fontsize=7)
    fs.save(fig, os.path.join(figs, "judge_wall"))
    plt.close(fig)


if __name__ == "__main__":
    main()
