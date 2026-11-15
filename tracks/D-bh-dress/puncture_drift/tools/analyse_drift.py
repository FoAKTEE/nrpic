#!/usr/bin/env python3
"""Drift of the apparent-horizon mass and spin of a vacuum puncture (D-pre-4).

    analyse_drift.py --out DIR [--run NAME=DIR:INV_DX ...] [--probes JSON ...]
                     [--slices JSON ...] [--res NAME=INV_DX ...] [--t0 50 ...]
                     [--window 20] [--tag NAME]

--run    a run directory with punc.horizon_summary_0.txt and punc.z4c.user.hst (the
         chained card runs); NAME is the run's directory name, INV_DX = M/dx at the hole
--probes probes.json of tools/probe_finder.py (finder re-searches of the dumps)
--slices slices.json of tools/slice_masses.py (Misner-Sharp mass of the dumps)
--res    M/dx of runs that only appear in probes or slices (e.g. dx8_tight=8)

Definitions (fixed in JOURNAL.md before the runs):
  Mbar(t)   running mean of the finder mass over a window W (default 20 M)
  sigma     rms of M - Mbar over [t0, t_end]
  D(T)      Mbar(t0 + T) - Mbar(t0) (production finder, the run itself)
  D_fs      largest |(M_s(t_k) - M_s(t0)) - (M_p(t_k) - M_p(t0))| over the dumps t_k and the
            finder settings s of the probes (p = production setting h0 of A16)
  dM_min(T) = max_{T' <= T} |D(T')| + D_fs + 2 sqrt(2) sigma
Output: DIR/<tag>_drift.json, DIR/<tag>_drift.txt and figures DIR/<tag>_*.png/pdf.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/python")
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

COLS = ["iter", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
        "meanradius", "minradius"]
RES_COL = {4: fs.PAL["yellow"], 8: fs.PAL["red"], 16: fs.PAL["blue"], 32: fs.PAL["green"]}
SETTINGS = [("A16", 0, "production (16 points, tol 1e-5, previous radius)"),
            ("A16", 1, "tol 1e-9"),
            ("A16", 2, "start at 2 M"),
            ("A32", 0, "32 points"),
            ("A32", 1, "32 points, tol 1e-9"),
            ("A32", 2, "32 points, start at 2 M")]
MARK = {("A16", 0): "o", ("A16", 1): "s", ("A16", 2): "^", ("A32", 0): "D",
        ("A32", 1): "v", ("A32", 2): "P"}
# null-test durations (EdS, t_i = 2/(3 eps) M): T = t_i ((a_f/a_i)^(3/2) - 1)
SCEN = [(0.03, 2.0), (0.01, 2.0), (0.03, 4.0), (0.01, 4.0)]


def scen_T(eps, af):
    return 2.0 / (3.0 * eps) * (af ** 1.5 - 1.0)


def read_summary(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    d = {k: a[:, i] for i, k in enumerate(COLS)}
    # one row per search time (a restart repeats the search of its cycle)
    _, idx = np.unique(d["time"], return_index=True)
    return {k: v[idx] for k, v in d.items()}


def read_hst(path):
    with open(path) as f:
        names = None
        for line in f:
            if "[1]=" in line:
                names = [s.split("=")[1] for s in line.split() if "=" in s]
                break
    a = np.loadtxt(path, comments="#", ndmin=2)
    _, idx = np.unique(a[:, 0], return_index=True)
    return {n: a[idx, i] for i, n in enumerate(names)}


def running_mean(t, y, W):
    out = np.full_like(y, np.nan)
    for i, ti in enumerate(t):
        s = np.abs(t - ti) <= W / 2
        if t[0] <= ti - W / 2 + 1e-9 and ti + W / 2 <= t[-1] + 1e-9:
            out[i] = y[s].mean()
    return out


def analyse_run(name, d, inv_dx, t0s, W):
    S = read_summary(os.path.join(d, "punc.horizon_summary_0.txt"))
    t, M = S["time"], S["mass"]
    R = dict(name=name, dir=d, inv_dx=inv_dx, t_end=float(t[-1]), n_searches=int(len(t)))
    R["series"] = S
    hp = os.path.join(d, "punc.z4c.user.hst")
    R["hst"] = read_hst(hp) if os.path.exists(hp) else None
    Mbar = running_mean(t, M, W)
    R["Mbar"] = Mbar
    R["Mirr"] = np.sqrt(S["area"] / (16 * math.pi))
    R["chi"] = S["S"] / M ** 2
    late = t >= 5.0
    R["chi_max_after5"] = float(np.max(np.abs(R["chi"][late]))) if late.any() else None
    R["hrms_max_after5"] = float(np.max(S["hrms"][late])) if late.any() else None
    # outer-boundary window (P4 of JOURNAL.md): residual of a 5 M running mean about a
    # straight line fitted over 150-300 M; peak-to-peak and the times of the extremes
    # inside 170-270 M against the same outside it (150-170 and 270-300 M)
    if t[-1] >= 300.0:
        m5 = running_mean(t, M, 5.0)
        w = (t >= 150.0) & (t <= 300.0) & np.isfinite(m5)
        c = np.polyfit(t[w], m5[w], 1)
        res_ = m5 - np.polyval(c, t)
        win = w & (t >= 170.0) & (t <= 270.0)
        out_ = w & ~win
        R["boundary"] = dict(
            p2p_in=float(res_[win].max() - res_[win].min()),
            p2p_out=float(res_[out_].max() - res_[out_].min()),
            t_max=float(t[win][np.argmax(res_[win])]),
            t_min=float(t[win][np.argmin(res_[win])]),
            slope_150_300=float(c[0]))
    R["per_t0"] = {}
    for spec in t0s:
        t0, tmax = parse_spec(spec)
        if t[-1] < t0 + W:
            continue
        i0 = int(np.argmin(np.abs(t - t0)))
        ok = (t >= t0) & (t <= tmax) & np.isfinite(Mbar)
        sig = float(np.sqrt(np.mean((M[ok] - Mbar[ok]) ** 2)))
        Dt = Mbar - Mbar[i0]
        s = (t >= t0) & (t <= tmax)
        c = np.polyfit(t[s], M[s], 1)
        P = dict(t0=t0, tmax=None if tmax == np.inf else tmax, spec=spec,
                 Mbar_t0=float(Mbar[i0]), sigma=sig, slope=float(c[0]),
                 D_end=float(Dt[ok][-1]), T_end=float(t[ok][-1] - t0))
        if t[-1] >= 250 + W and tmax > 250 + W:
            s2 = (t >= 250) & (t <= tmax)
            P["slope_late"] = float(np.polyfit(t[s2], M[s2], 1)[0])
        P["slopes"] = []
        wins = ([(t0, 100.0)] if t0 < 100.0 else []) + [
            (lo, lo + 100.0) for lo in (100.0, 200.0, 300.0, 400.0) if lo >= t0]
        for lo, hi in wins:
            w = (t >= lo) & (t <= hi)
            if w.sum() > 4 and t[-1] >= hi - 1 and hi <= tmax:
                P["slopes"].append((lo, hi, float(np.polyfit(t[w], M[w], 1)[0])))
        P["T"] = (t[ok] - t0).tolist()
        P["D"] = Dt[ok].tolist()
        P["envD"] = np.maximum.accumulate(np.abs(Dt[ok])).tolist()
        R["per_t0"][spec] = P
    return R


def parse_spec(spec):
    """'50' -> (50, inf); '50:210' -> (50, 210): start of the measurement and its end."""
    a, _, b = str(spec).partition(":")
    return float(a), (float(b) if b else np.inf)


def probe_table(probes):
    """{run: {(variant, horizon): [(t, M, S, hrms, r)]}} sorted in time."""
    tab = {}
    for p in probes:
        if not p.get("found"):
            continue
        k = (p["variant"], p["horizon"])
        tab.setdefault(p["run"], {}).setdefault(k, []).append(
            (p["time_dump"], p["mass"], p["S"], p["hrms"], p["meanradius"]))
    for r in tab.values():
        for k in r:
            r[k].sort()
    return tab


def finder_drift_spread(tab_run, t0, tmax=np.inf):
    """Largest |drift_s - drift_production| over dumps and settings, with t0 the dump
    nearest to t0; None if fewer than two dumps."""
    base = tab_run.get(("A16", 0))
    if not base or len(base) < 2:
        return None, {}
    tb = np.array([b[0] for b in base])
    i0 = int(np.argmin(np.abs(tb - t0)))
    out, worst = {}, 0.0
    for k, rows in tab_run.items():
        tr = np.array([r[0] for r in rows])
        if not np.any(np.isclose(tr, tb[i0])):
            continue
        j0 = int(np.argmin(np.abs(tr - tb[i0])))
        dd = []
        for (tk, mk, *_ ) in rows:
            if tk > tmax + 1e-9:
                continue
            jb = np.isclose(tb, tk)
            if not jb.any():
                continue
            ib = int(np.nonzero(jb)[0][0])
            ds = (mk - rows[j0][1]) - (base[ib][1] - base[i0][1])
            dd.append((tk, ds))
            worst = max(worst, abs(ds))
        out[k] = dd
    return worst, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="drift")
    ap.add_argument("--run", nargs="*", default=[])
    ap.add_argument("--probes", nargs="*", default=[])
    ap.add_argument("--slices", nargs="*", default=[])
    ap.add_argument("--res", nargs="*", default=[])
    ap.add_argument("--label", nargs="*", default=[], help="NAME=TEXT for legends")
    ap.add_argument("--t0", nargs="*", default=["50", "100", "20", "50:210"],
                    help="start of the measurement, optionally :end (e.g. 50:210)")
    ap.add_argument("--window", type=float, default=20.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()

    res = {}
    for s in a.res:
        k, v = s.split("=")
        res[k] = int(v)
    labels = dict(s.split("=", 1) for s in a.label)
    runs = []
    for s in a.run:
        name, rest = s.split("=", 1)
        d, inv = rest.rsplit(":", 1)
        res[name] = int(inv)
        runs.append(analyse_run(name, d, int(inv), a.t0, a.window))
    probes = [p for f in a.probes for p in json.load(open(f))]
    slices = [s for f in a.slices for s in json.load(open(f))]
    ptab = probe_table(probes)
    lines = []
    pr = lambda s="": (lines.append(s), print(s))  # noqa: E731
    out = dict(window=a.window, runs={}, probes={}, slices={}, floors={})

    # ---- probes (finder settings on the same slice)
    pr("Finder settings on the same slices (probe_finder.py): M - 1, and difference to"
       " the production setting (A16 h0)")
    for run, tr in sorted(ptab.items(), key=lambda kv: res.get(kv[0], 0)):
        pr(f"  {run} (M/dx = {res.get(run, '?')}):")
        base = {round(r[0], 6): r[1] for r in tr.get(("A16", 0), [])}
        for k in [(v, h) for v, h, _ in SETTINGS]:
            for (tk, mk, Sk, hk, rk) in tr.get(k, []):
                b = base.get(round(tk, 6))
                pr(f"    t = {tk:7.2f}  {k[0]} h{k[1]}  M - 1 = {mk - 1:+.6e}  "
                   f"diff = {(mk - b) if b is not None else float('nan'):+.2e}  "
                   f"S = {Sk:+.2e}  hrms = {hk:.1e}  r = {rk:.4f}")
        out["probes"][run] = {f"{k[0]}_h{k[1]}": v for k, v in tr.items()}
    pr()
    pr("Slices (Misner-Sharp, slice_masses.py): M_H = R_H/2, m at R = 3, 10 M, m_inf")
    for s in sorted(slices, key=lambda s: (res.get(s["run"], 0), s["time"])):
        pr(f"  {s['run']:>36s} t = {s['time']:7.2f}  M_H - 1 = {s.get('M_H', np.nan) - 1:+.3e}"
           f" +- {s.get('dMH_shell', np.nan):.0e} +- {s.get('dMH_spread', np.nan):.0e}  "
           f"m(3) - 1 = {(s['m_R3'] or np.nan) - 1:+.3e}  m(10) - 1 = "
           f"{(s['m_R10'] or np.nan) - 1:+.3e}  m_inf - 1 = {s['m_inf'] - 1:+.3e}")
        out["slices"].setdefault(s["run"], []).append(s)
    pr()

    # ---- runs
    for R in runs:
        pr(f"Run {R['name']} (M/dx = {R['inv_dx']}): {R['n_searches']} searches to t = "
           f"{R['t_end']:.2f} M; max |S|/M^2 after 5 M = {R['chi_max_after5']:.2e}, max rms "
           f"expansion after 5 M = {R['hrms_max_after5']:.1e}")
        if "boundary" in R:
            B = R["boundary"]
            pr(f"  boundary window 170-270 M (5 M mean, about a line over 150-300 M): "
               f"peak-to-peak {B['p2p_in']:.1e} (outside the window {B['p2p_out']:.1e}), "
               f"maximum at {B['t_max']:.1f} M, minimum at {B['t_min']:.1f} M")
        o = dict(t_end=R["t_end"], chi_max_after5=R["chi_max_after5"],
                 boundary=R.get("boundary"),
                 hrms_max_after5=R["hrms_max_after5"], per_t0={})
        for spec, P in R["per_t0"].items():
            wfs, _ = finder_drift_spread(ptab.get(R["name"], {}), P["t0"],
                                         P["tmax"] if P["tmax"] else np.inf)
            P["D_fs"] = wfs
            pr(f"  t0 = {spec} M: Mbar(t0) - 1 = {P['Mbar_t0'] - 1:+.3e}, sigma = "
               f"{P['sigma']:.1e}, D at T = {P['T_end']:.0f} M = {P['D_end']:+.3e}, linear "
               f"slope {P['slope']:+.2e} per M" + (f", slope over t >= 250 M "
               f"{P['slope_late']:+.2e} per M" if "slope_late" in P else "")
               + (f"; finder-setting spread of the drift D_fs = {wfs:.1e}" if wfs is not None
                  else "; no finder-setting spread (fewer than two probed dumps)"))
            if P["slopes"]:
                pr("    slopes per 100 M window: " + ", ".join(
                    f"{lo:g}-{hi:g}: {sl:+.2e}" for lo, hi, sl in P["slopes"]))
            o["per_t0"][spec] = {k: v for k, v in P.items() if k not in ("T", "D", "envD")}
        out["runs"][R["name"]] = o
    pr()

    # ---- floors
    pr("Smallest detectable mass change dM_min(T) = max|D| + D_fs + 2 sqrt(2) sigma, "
       "(per unit mass; = Delta ln M), and k_floor = dM_min / ln(a_f/a_i)")
    for t0 in a.t0:
        fl = {}
        for R in runs:
            if t0 not in R["per_t0"]:
                continue
            P = R["per_t0"][t0]
            T, env = np.array(P["T"]), np.array(P["envD"])
            add = (P["D_fs"] or 0.0) + 2 * math.sqrt(2) * P["sigma"]
            fl[R["inv_dx"]] = (T, env + add, P)
            for eps, af in SCEN:
                Ts = scen_T(eps, af)
                if Ts <= T[-1]:
                    dm = float(np.interp(Ts, T, env + add))
                    pr(f"  t0 = {t0}, M/{R['inv_dx']}: eps = {eps:g}, a x {af:g} (T = "
                       f"{Ts:.1f} M): dM_min = {dm:.2e}, k_floor = {dm / math.log(af):.2e}")
                    out["floors"].setdefault(str(t0), {}).setdefault(
                        f"M/{R['inv_dx']}", {})[f"eps{eps:g}_a{af:g}"] = dict(
                        T=Ts, dM_min=dm, k_floor=dm / math.log(af))
                else:
                    pr(f"  t0 = {t0}, M/{R['inv_dx']}: eps = {eps:g}, a x {af:g} (T = "
                       f"{Ts:.1f} M): beyond the run (T_max = {T[-1]:.0f} M)")
        if 8 in fl and 16 in fl:
            T8, f8, P8 = fl[8]
            T16, f16, P16 = fl[16]
            Tc = np.linspace(max(T8[1], T16[1], 10.0), min(T8[-1], T16[-1]), 200)
            e8 = np.interp(Tc, T8, np.array(P8["envD"]))
            e16 = np.interp(Tc, T16, np.array(P16["envD"]))
            with np.errstate(divide="ignore", invalid="ignore"):
                p = np.log2(e8 / e16)
            for Tq in (40.0, 120.0, 200.0, 300.0, 450.0):
                if Tq <= Tc[-1]:
                    pq = float(np.interp(Tq, Tc, p))
                    pr(f"  t0 = {t0}: envelope of |D| at T = {Tq:g} M: M/8 "
                       f"{np.interp(Tq, Tc, e8):.2e}, M/16 {np.interp(Tq, Tc, e16):.2e}, "
                       f"ratio {2 ** pq:.1f} (order {pq:.2f})")
                    out["floors"].setdefault(str(t0), {}).setdefault("order", {})[
                        f"T{Tq:g}"] = pq
    pr()
    with open(os.path.join(a.out, f"{a.tag}_drift.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    with open(os.path.join(a.out, f"{a.tag}_drift.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")

    figs = []
    if runs:
        figs += fig_history(runs, ptab, slices, res, labels, a, os.path.join(a.out, f"{a.tag}_history"))
        figs += fig_floor(runs, a, os.path.join(a.out, f"{a.tag}_floor"))
    if ptab:
        figs += fig_finder(ptab, slices, res, labels, os.path.join(a.out, f"{a.tag}_finder"))
    print("\n".join(figs))


def lab(name, res, labels):
    return labels.get(name, f"M/{res.get(name, '?')}")


def fig_history(runs, ptab, slices, res, labels, a, path):
    fig, ax = plt.subplots(5, 1, figsize=(fs.FULL_WIDTH, 10.5), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.98, bottom=0.05, hspace=0.0)
    t0 = a.t0[0]
    t0v = parse_spec(t0)[0]
    for R in runs:
        c = RES_COL.get(R["inv_dx"], "k")
        S = R["series"]
        t = S["time"]
        L = lab(R["name"], res, labels)
        ax[0].plot(t, S["mass"] - 1, color=c, lw=1.0, label=f"{L}, finder (run)")
        ax[0].plot(t, R["Mbar"] - 1, color=c, lw=1.5, ls="--", label=f"{L}, {a.window:g} M mean")
        if t0 in R["per_t0"]:
            P = R["per_t0"][t0]
            ax[1].plot(np.array(P["T"]) + t0v, P["D"], color=c, label=L)
        ax[2].semilogy(t, np.abs(R["chi"]), color=c, label=L)
        ax[3].plot(t, S["meanradius"], color=c, label=f"{L}, mean")
        ax[3].plot(t, S["minradius"], color=c, ls=":", label=f"{L}, minimum")
        h = R["hst"]
        if h is not None:
            ax[4].semilogy(h["time"], h["H-norm2"], color=c, label=f"{L}, H")
            ax[4].semilogy(h["time"], h["M-norm2"], color=c, ls="--", label=f"{L}, M")
        tr = ptab.get(R["name"], {})
        for k, mk in MARK.items():
            rows = tr.get(k, [])
            if rows and k != ("A16", 0):
                ax[0].plot([r[0] for r in rows], [r[1] - 1 for r in rows], ls="none",
                           marker=mk, ms=4, mfc="none", color=c)
        ss = sorted([s for s in slices if s["run"] == R["name"] and "M_H" in s],
                    key=lambda s: s["time"])
        if ss:
            ax[0].errorbar([s["time"] for s in ss], [s["M_H"] - 1 for s in ss],
                           yerr=[s["dMH_shell"] + s["dMH_spread"] for s in ss], ls="none",
                           marker="x", ms=5, color=c, lw=1.0)
    for s in ("A16", 1), ("A32", 1):
        ax[0].plot([], [], ls="none", marker=MARK[s], mfc="none", color="grey",
                   label=dict((k[:2], k[2]) for k in [(v, h, d) for v, h, d in SETTINGS])[s])
    ax[0].plot([], [], ls="none", marker="x", color="grey", label="slice, Misner-Sharp")
    ax[0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    # zoom on t >= 10 M (the first 10 M are the gauge transient)
    ys = np.concatenate([R["series"]["mass"][R["series"]["time"] >= 10.0] - 1 for R in runs])
    if ys.size:
        lo, hi = ys.min(), ys.max()
        pad = 0.15 * (hi - lo) + 1e-6
        ax[0].set_ylim(lo - pad, hi + 2.5 * pad)
    ax[0].legend(ncol=2, fontsize=8, loc="center right")
    ax[1].axhline(0, **fs.MASK_LINE)
    ax[1].axvline(t0v, **fs.MASK_LINE)
    ax[1].set_ylabel(r"$\bar M(t) - \bar M(t_0)$, $t_0=%g\,M$" % t0v)
    ax[1].legend(fontsize=8)
    ax[2].set_ylabel(r"$|S|/M_{\rm AH}^2$")
    ax[2].legend(fontsize=8)
    ax[3].set_ylabel(r"coordinate radius $/M$")
    ax[3].legend(ncol=2, fontsize=8)
    ax[4].set_ylabel("constraint norms")
    ax[4].legend(ncol=2, fontsize=8)
    for x in (180.0, 256.0):
        for k in range(5):
            ax[k].axvline(x, color="grey", lw=0.8, alpha=0.3)
    ax[-1].set_xlabel(r"$t/M$")
    return fs.save(fig, path) if hasattr(fs, "save") else _save(fig, path)


def fig_floor(runs, a, path):
    specs = [sp for sp in ("50", "20") if sp in a.t0] or [a.t0[0]]
    fig, axs = plt.subplots(1, len(specs), figsize=(fs.FULL_WIDTH, 3.6), sharey=True,
                            squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.14, wspace=0.0)
    for ax, sp in zip(axs[0], specs):
        t0 = parse_spec(sp)[0]
        for R in runs:
            if sp not in R["per_t0"]:
                continue
            P = R["per_t0"][sp]
            c = RES_COL.get(R["inv_dx"], "k")
            T = np.array(P["T"])
            env = np.array(P["envD"])
            add = (P["D_fs"] or 0.0) + 2 * math.sqrt(2) * P["sigma"]
            ok = T > 0
            ax.loglog(T[ok], env[ok] + add, color=c,
                      label=fr"$M/{R['inv_dx']}$: $\Delta M_{{\min}}(T)$")
            ax.loglog(T[ok], env[ok], color=c, ls=":", label=fr"$M/{R['inv_dx']}$: $\max|D|$")
        for eps, af in SCEN:
            ax.axvline(scen_T(eps, af), **fs.MASK_LINE)
            ax.text(scen_T(eps, af) * 1.03, 0.98, fr"$\epsilon={eps:g}$, $a\times{af:g}$",
                    rotation=90, va="top", ha="left", fontsize=7,
                    transform=ax.get_xaxis_transform())
        ax.axvline(215.0 - t0, **fs.GUIDE)
        ax.text((215.0 - t0) * 0.97, 0.02, "boundary signal\nat the hole", ha="right",
                va="bottom", fontsize=7, transform=ax.get_xaxis_transform())
        ax.set_xlabel(r"run length $T/M$ from $t_0=%g\,M$" % t0)
        ax.set_xlim(1.0, 600.0)
    axs[0][0].set_ylabel(r"$\Delta M/M$")
    axs[0][0].legend(fontsize=7, loc="upper left", ncol=2)
    return fs.save(fig, path) if hasattr(fs, "save") else _save(fig, path)


def fig_finder(ptab, slices, res, labels, path):
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.15, wspace=0.30)
    seen = set()
    for run, tr in sorted(ptab.items(), key=lambda kv: res.get(kv[0], 0)):
        if run not in res:
            continue
        c = RES_COL.get(res.get(run), "k")
        base = {round(r[0], 6): r[1] for r in tr.get(("A16", 0), [])}
        for (v, h, desc) in SETTINGS:
            rows = tr.get((v, h), [])
            x = [r[0] for r in rows if round(r[0], 6) in base]
            y = [1e4 * (r[1] - base[round(r[0], 6)]) for r in rows if round(r[0], 6) in base]
            if (v, h) != ("A16", 0) and x:
                ax[0].plot(x, y, marker=MARK[(v, h)], mfc="none", color=c, ls="-", lw=0.8)
        if res.get(run) not in seen:
            ax[0].plot([], [], color=c, label=f"$M/{res.get(run)}$")
            seen.add(res.get(run))
        rows = tr.get(("A16", 0), [])
        ax[1].plot([res.get(run) / 1.06] * len(rows), [r[1] - 1 for r in rows], ls="none",
                   marker="o", mfc="none", color=c)
        rows = tr.get(("A32", 1), [])
        ax[1].plot([res.get(run)] * len(rows), [r[1] - 1 for r in rows], ls="none",
                   marker=MARK[("A32", 1)], mfc="none", color=c)
        ss = [s for s in slices if s["run"] == run and "M_H" in s]
        ax[1].plot([res.get(run) * 1.06] * len(ss), [s["M_H"] - 1 for s in ss], ls="none",
                   marker="x", color=c)
    for (v, h, desc) in SETTINGS[1:]:
        ax[0].plot([], [], marker=MARK[(v, h)], mfc="none", color="grey", ls="none", label=desc)
    ax[0].axhline(0, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$t/M$ of the dump")
    ax[0].set_ylabel(r"$(M_{\rm setting} - M_{\rm production})\times10^{4}$")
    ax[0].legend(fontsize=7, loc="upper left", ncol=2, bbox_to_anchor=(0.0, 1.0))
    ax[0].set_ylim(top=ax[0].get_ylim()[1] * 1.45)
    ax[1].set_xscale("log", base=2)
    ax[1].axhline(0, **fs.MASK_LINE)
    ax[1].plot([], [], ls="none", marker="o", mfc="none", color="grey",
               label="finder, production")
    ax[1].plot([], [], ls="none", marker=MARK[("A32", 1)], mfc="none", color="grey",
               label="finder, 32 points, tol 1e-9")
    ax[1].plot([], [], ls="none", marker="x", color="grey", label="slice, Misner-Sharp")
    ax[1].set_xlabel(r"$M/\Delta x$ at the hole")
    ax[1].set_ylabel(r"$M_{\rm AH}/M - 1$")
    ax[1].set_yscale("symlog", linthresh=1e-5)
    ax[1].legend(fontsize=7, loc="lower right")
    return fs.save(fig, path) if hasattr(fs, "save") else _save(fig, path)


def _save(fig, path):
    out = []
    for ext in ("png", "pdf"):
        fig.savefig(f"{path}.{ext}")
        out.append(f"{path}.{ext}")
    plt.close(fig)
    return out


if __name__ == "__main__":
    main()
