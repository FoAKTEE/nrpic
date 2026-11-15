"""Analysis of the scouting runs S1/S2 (JOURNAL.md): histories, profiles along the three
axes through the peak, finder output; figures and a JSON summary.

    python3 analyse_scouting.py --run LABEL=DIR [--run LABEL=DIR ...] --eps-i 1 --out DIR

DIR is the AthenaK run directory (contains peak.nrpic.hst, peak.cstat.hst, tab/).
Background time: the coordinate time is conformal time of the homogeneous solution,
a = (1 + tau/2)^2 (cosmo/README.md), t/t_H = (a/a_H)^(3/2) with a_H = 6/eps_i^2 (P0).
Away from the peak the lapse condition keeps this relation [JUDGEMENT; the K-driver
references the largest lapse and the proper-volume mean of K].
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def read_cols(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("# [1]="):
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    a = np.genfromtxt(path, comments="#", invalid_raise=False)
    a = np.atleast_2d(a)
    # drop records superseded by a restart (time not increasing)
    keep = np.ones(len(a), dtype=bool)
    tmin = np.inf
    for i in range(len(a) - 1, -1, -1):
        if a[i, 0] >= tmin:
            keep[i] = False
        else:
            tmin = a[i, 0]
    a = a[keep]
    return {n: a[:, i] for i, n in enumerate(names) if i < a.shape[1]}


def read_tab(path):
    t = None
    with open(path) as f:
        lines = f.readlines()
    m = re.search(r"time=([0-9.eE+-]+)", lines[0])
    if m:
        t = float(m.group(1))
    hdr = [ln for ln in lines if ln.startswith("# gid")][0][1:].split()
    rows = [ln.split() for ln in lines if not ln.startswith("#") and ln.strip()]
    d = {h: np.array([float(r[i]) for r in rows]) for i, h in enumerate(hdr)}
    d["time"] = t
    return d


def tab_series(run, var, axis):
    """Tab files of one variable along one axis, sorted by index."""
    out = []
    for p in sorted(glob.glob(os.path.join(run, "tab", f"peak.{var}.*.tab"))):
        d = read_tab(p)
        key = {"x": "x1v", "y": "x2v", "z": "x3v"}[axis]
        if key not in d:
            continue
        out.append(d)
    return out


def t_over_tH(tau, eps):
    a = (1.0 + 0.5*np.asarray(tau))**2
    return (a/(6.0/eps**2))**1.5


def horizon(run):
    p = os.path.join(run, "peak.horizon_summary_0.txt")
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return np.zeros((0, 12))
    a = np.genfromtxt(p, comments="#")
    return np.atleast_2d(a)


def summarise(label, run, eps):
    s = {"label": label, "dir": run}
    log = os.path.join(run, "athena.log")
    if os.path.exists(log):
        txt = open(log, errors="replace").read().splitlines()
        s["log_tail"] = txt[-8:]
        cyc = [ln for ln in txt if ln.startswith("cycle=") or "cycle=" in ln]
        s["last_cycle_line"] = cyc[-1] if cyc else None
    hp = os.path.join(run, "peak.nrpic.hst")
    if os.path.exists(hp):
        h = read_cols(hp)
        s["t_end"] = float(h["time"][-1])
        s["t_end_over_tH"] = float(t_over_tH(h["time"][-1], eps))
        s["ncycle"] = int(h["ncycle"][-1])
        for k in ("alpha_min", "n_excised", "m_excised", "nmb", "push_unconverged",
                  "np"):
            if k in h:
                s[k + "_end"] = float(h[k][-1])
    cp = os.path.join(run, "peak.cstat.hst")
    if os.path.exists(cp):
        c = read_cols(cp)
        s["cstat_end"] = {k: float(v[-1]) for k, v in c.items()}
        s["Hr_max_max"] = float(np.nanmax(c["Hr_max"]))
        for thr in (1e-2, 1e-1):
            i = np.flatnonzero(c["Hr_max"] > thr)
            s[f"tau_Hr_max_above_{thr:g}"] = float(c["time"][i[0]]) if len(i) else None
    hz = horizon(run)
    found = hz[np.isfinite(hz[:, 2])] if len(hz) else hz
    s["finder_calls"] = int(len(hz))
    s["horizons"] = [dict(time=float(r[1]), mass=float(r[2]), area=float(r[7]),
                          hrms=float(r[8]), meanradius=float(r[10]), minradius=float(r[11]))
                     for r in found]
    return s


def figures(runs, eps, out, sums):
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"]]
    fig = plt.figure(figsize=(8, 7.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.07, top=0.98, hspace=0.08)
    axs = [fig.add_subplot(4, 1, i + 1) for i in range(4)]
    for (label, run), col in zip(runs, cols):
        hp = os.path.join(run, "peak.nrpic.hst")
        cp = os.path.join(run, "peak.cstat.hst")
        if os.path.exists(cp):
            c = read_cols(cp)
            x = t_over_tH(c["time"], eps)
            Ebar = c["E_min"]*0 + 3.0/(8.0*np.pi)/(1.0 + 0.5*c["time"])**6
            axs[0].loglog(x, c["E_max"]/Ebar, color=col, label=label)
            axs[2].loglog(x, np.maximum(c["Hr_max"], 1e-12), color=col)
            axs[2].loglog(x, np.maximum(c["Hr_mean"], 1e-12), color=col, ls="--")
            axs[3].loglog(x, np.maximum(c["Theta_max"], 1e-14), color=col)
        if os.path.exists(hp):
            h = read_cols(hp)
            x = t_over_tH(h["time"], eps)
            a = (1.0 + 0.5*h["time"])**2
            axs[1].semilogx(x, h["alpha_min"]/a, color=col)
            if "alpha_probe" in h:
                axs[1].semilogx(x, h["alpha_probe"]/a, color=col, ls="--")
        hz = horizon(run)
        if len(hz):
            ok = np.isfinite(hz[:, 2])
            if ok.any():
                axs[0].plot(t_over_tH(hz[ok, 1], eps), np.full(ok.sum(), 1.0), "v",
                            color=col)
    for ax in axs:
        for tz, ls in ((1.95, ":"), (3.95, ":"), (15.6, ":"), (7.47, "--")):
            ax.axvline(tz, color=cols[0], lw=1.0, ls=ls, alpha=0.4)
        for tz in (132.9, 269.0):
            ax.axvline(tz, color=cols[1], lw=1.0, ls=":", alpha=0.4)
    axs[0].set_ylabel(r"$E_{\max}/\bar E$")
    axs[0].legend(frameon=False, loc="upper left")
    axs[1].set_ylabel(r"$\alpha/a$ (min; dashed: centre)")
    axs[2].set_ylabel(r"$H_r$ max (mean dashed)")
    axs[3].set_ylabel(r"$\Theta_{\max}$")
    axs[3].set_xlabel(r"$t/t_H$ (background)")
    for ax in axs[:-1]:
        ax.tick_params(labelbottom=False)
    fs.save(fig, os.path.join(out, "fig_scouting_histories"))

    # profiles along the three axes at the last few dumps
    for label, run in runs:
        fig = plt.figure(figsize=(8, 5.4))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, wspace=0.28,
                            hspace=0.3)
        series = [("tmunu_E", "x", 4), ("tmunu_E", "y", 6), ("tmunu_E", "z", 9),
                  ("adm_alpha", "x", None), ("adm_alpha", "y", 5), ("adm_alpha", "z", 8)]
        for j, (var, axn, _) in enumerate(series):
            ax = fig.add_subplot(2, 3, j + 1)
            vv = var if var != "adm_alpha" or axn != "x" else "adm"
            sers = tab_series(run, vv, axn)
            if not sers:
                continue
            pick = sers[::max(1, len(sers)//6)] + [sers[-1]]
            cc = fs.series_colors(len(pick))
            key = {"x": "x1v", "y": "x2v", "z": "x3v"}[axn]
            for d, cl in zip(pick, cc):
                o = np.argsort(d[key])
                a = (1.0 + 0.5*d["time"])**2
                if var == "tmunu_E":
                    y = d["tmunu_E"][o]/(3/(8*np.pi)/a**3)
                    ax.semilogy(d[key][o], y, color=cl, lw=1.0,
                                label=f"{t_over_tH(d['time'], eps):.3g}")
                else:
                    y = d["adm_alpha"][o]/a
                    ax.plot(d[key][o], y, color=cl, lw=1.0)
            ax.set_xlim(-4, 4)
            ax.set_xlabel(f"{axn} (through the peak)")
            ax.set_ylabel(r"$E/\bar E$" if var == "tmunu_E" else r"$\alpha/a$")
            if j == 0:
                ax.legend(frameon=False, fontsize=7, title=r"$t/t_H$", title_fontsize=7)
        fs.save(fig, os.path.join(out, f"fig_scouting_profiles_{label}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="LABEL=DIR")
    ap.add_argument("--eps-i", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = [tuple(r.split("=", 1)) for r in a.run]
    sums = [summarise(lab, d, a.eps_i) for lab, d in runs]
    with open(os.path.join(a.out, "scouting_summary.json"), "w") as f:
        json.dump(sums, f, indent=1)
    for s in sums:
        print(json.dumps({k: v for k, v in s.items() if k not in ("cstat_end",)},
                         indent=1)[:3000])
    figures(runs, a.eps_i, a.out, sums)


if __name__ == "__main__":
    main()
