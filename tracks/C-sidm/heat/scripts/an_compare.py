#!/usr/bin/env python3
"""Comparisons built on the outputs of an_mode.py (heat package, wave 3 round 1).

    an_compare.py cardcpu OUTDIR T7JSON [T7JSON ...]
    an_compare.py eps     OUTDIR T7JSON_A GROUP_A T7JSON_B GROUP_B
    an_compare.py t8      OUTDIR --noise T7JSON GROUP T8JSON [T8JSON ...]

Inputs are T7.json / T8.json written by `an_mode.py T7|T8` into registered run directories
(a run id resolves to scratch/C-sidm/<id>/T7.json). f is the conductivity in units of
kappa_1(T) with the finite-amplitude bias removed (an_mode.py: f_S, entropy-mode fit).

Noise model (stated before the runs, JOURNAL 2026-11-20 22:30): the variance of f of one
run is s2/N (N particles; the equilibrium entropy-mode noise var A_S = 2 c_p/N, design run
C-20261119-144117-37b2328) times (0.2/eps)^2 for the amplitude eps; s2 ("unit variance")
is estimated per (theta, eps, k lambda) from the seed scatter as
s2 = sum_i N_i (f_i - f_w)^2/(n - 1), f_w = sum N_i f_i/sum N_i (weights 1/variance).

cardcpu  per group and k lambda: card seeds (case names T7c_) against processor seeds
         (T7_): z = (f_card - mean_cpu)/sqrt(se_cpu^2 + s2_cpu/N_card), s2_cpu from the
         processor seeds alone; pass |z| < 3. Also the weighted pooled f_w, its standard
         error sqrt(s2/sum N) and the extrapolation of f_w linearly in (k lambda)^2.
eps      rows of GROUP_A (e.g. T7_th0.003_e0.05) against GROUP_B (T7_th0.003_e0.2) at the
         same k lambda: delta = f_A - f_B, expected se from GROUP_B's unit variance scaled
         to N and eps of A; pass |delta| < 3 se_expected; the measured seed se is reported.
t8       variants of T8.json (one or more seeds, each seed one particle file for all its
         variants): per seed the relative change of f between neighbouring values of dt,
         pmax and dx (others at the base 0.1, 0.1, 0.25); expected sd of a change
         sqrt(2 s2/N) (independent runs; an upper bound, the variants share the initial
         sample) with s2 of GROUP of the noise file at k lambda = 0.2.
Writes <cmd>.json and a figure into OUTDIR ("-": the registered run's directory).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def resolve(p, fname):
    if os.path.isabs(p) or os.path.exists(p):
        return p if p.endswith(".json") else os.path.join(p, fname)
    return os.path.join(hl.MAIN, "scratch", "C-sidm", p, fname)


def case_n(rundirs, name):
    for r in rundirs:
        cj = os.path.join(r, name, "case.json")
        if os.path.exists(cj):
            P = json.load(open(cj))
            return int(P["n"]), P
    raise FileNotFoundError(name)


def weighted(f, N):
    f, N = np.asarray(f, float), np.asarray(N, float)
    fw = float(np.sum(N * f) / np.sum(N))
    if len(f) < 2:
        return fw, float("nan"), float("nan")
    s2 = float(np.sum(N * (f - fw) ** 2) / (len(f) - 1))
    return fw, float(np.sqrt(s2 / np.sum(N))), s2


def extrapolate(kl, f, se):
    x = np.asarray(kl, float) ** 2
    w = 1.0 / np.asarray(se, float) ** 2
    A = np.vstack([np.ones_like(x), x]).T
    C = np.linalg.inv(A.T @ (A * w[:, None]))
    p = C @ (A.T @ (w * np.asarray(f, float)))
    chi2 = float(np.sum(w * (np.asarray(f) - A @ p) ** 2))
    return dict(f0=float(p[0]), f0_se=float(np.sqrt(C[0, 0])), b=float(p[1]),
                b_se=float(np.sqrt(C[1, 1])), chi2=chi2, dof=len(x) - 2)


def seeds_of(T7, gname):
    """[(k_lambda, [dict(name, seed, f, N, card)])] of one group."""
    g = T7["groups"][gname]
    out = []
    for r in g["rows"]:
        seeds = []
        for ft in r["fits"]:
            N, P = case_n(T7["rundirs"], ft["name"])
            seeds.append(dict(name=ft["name"], seed=ft["seed"], f=ft["f_S"], f_N=ft["f_N"],
                              N=N, card=ft["name"].startswith("T7c_"), eps=P["eps"]))
        out.append((r["k_lambda"], seeds))
    return g, out


def cmd_cardcpu(outdir, paths):
    res = dict(inputs=paths, groups={}, skipped=[])
    fs.use_style()
    for p in paths:
        T7 = json.load(open(resolve(p, "T7.json")))
        for gname in sorted(T7["groups"]):
            g, rows = seeds_of(T7, gname)
            # only groups that pool card and processor seeds (a T7 run over a card job
            # also holds that job's other temperatures, card seeds alone: skipped)
            if not any(sum(not s["card"] for s in ss) >= 2 and any(s["card"] for s in ss)
                       for _, ss in rows):
                res["skipped"].append(f"{os.path.basename(p.rstrip('/'))}:{gname}")
                continue
            G = dict(theta=g["theta"], eps=g["eps"], source=p, rows=[])
            for kl, ss in rows:
                cpu = [s for s in ss if not s["card"]]
                card = [s for s in ss if s["card"]]
                fw, sew, s2 = weighted([s["f"] for s in ss], [s["N"] for s in ss])
                row = dict(k_lambda=kl, n_seeds=len(ss), f_w=fw, f_w_se=sew, s2_all=s2,
                           seeds=ss)
                if len(cpu) >= 2:
                    fc = np.array([s["f"] for s in cpu])
                    Nc = np.array([s["N"] for s in cpu], float)
                    _, _, s2c = weighted(fc, Nc)
                    mc, sec = float(fc.mean()), float(fc.std(ddof=1) / np.sqrt(len(fc)))
                    row.update(cpu_mean=mc, cpu_se=sec, cpu_n=len(cpu), s2_cpu=s2c,
                               cpu_N=sorted(set(int(x) for x in Nc)))
                    row["card"] = []
                    for s in card:
                        sd_card = float(np.sqrt(s2c / s["N"]))
                        z = (s["f"] - mc) / np.sqrt(sec ** 2 + sd_card ** 2)
                        row["card"].append(dict(name=s["name"], seed=s["seed"], N=s["N"],
                                                f=s["f"], sd_expected=sd_card,
                                                z=float(z), pass_3se=bool(abs(z) < 3)))
                G["rows"].append(row)
            ok = [r for r in G["rows"] if np.isfinite(r["f_w_se"]) and r["f_w_se"] > 0]
            if len(ok) >= 2:
                G["extrapolation_weighted"] = extrapolate([r["k_lambda"] for r in ok],
                                                          [r["f_w"] for r in ok],
                                                          [r["f_w_se"] for r in ok])
            res["groups"][gname] = G
            # figure: every seed (card filled, processor open), weighted means, line
            fig = plt.figure(figsize=(fs.COLUMN_WIDTH * 1.25, 3.0))
            ax = fig.add_axes([0.17, 0.16, 0.78, 0.74])
            for r in G["rows"]:
                x = r["k_lambda"] ** 2
                for s in r["seeds"]:
                    off = 0.0004 if s["card"] else -0.0004
                    ax.plot(x + off, s["f"], "o" if s["card"] else "s", ms=3.5,
                            mfc=fs.PAL["red"] if s["card"] else "none",
                            color=fs.PAL["red"] if s["card"] else fs.PAL["blue"],
                            alpha=0.85)
                ax.errorbar(x, r["f_w"], yerr=r["f_w_se"] if np.isfinite(r["f_w_se"]) else 0,
                            fmt="D", color="k", ms=4, capsize=2, zorder=5)
            if "extrapolation_weighted" in G:
                e = G["extrapolation_weighted"]
                xx = np.linspace(0, max(r["k_lambda"] for r in G["rows"]) ** 2 * 1.08, 40)
                ax.plot(xx, e["f0"] + e["b"] * xx, **fs.REF_LINE)
                fs.band(ax, [0.0, 0.006], [e["f0"] - e["f0_se"]] * 2,
                        [e["f0"] + e["f0_se"]] * 2, fs.PAL["red"])
            ax.plot([], [], "o", ms=3.5, color=fs.PAL["red"], label="card seeds")
            ax.plot([], [], "s", ms=3.5, mfc="none", color=fs.PAL["blue"],
                    label="processor seeds")
            ax.plot([], [], "D", ms=4, color="k", label=r"pooled, weights $\propto N$")
            if g["theta"] == 0.003:
                ax.axhspan(0.99, 1.06, color="grey", alpha=0.12, lw=0)
            ax.axhline(1.0, **fs.MASK_LINE)
            ax.set_xlabel(r"$(k\lambda)^2$")
            ax.set_ylabel(r"$f=\kappa/\kappa_1$")
            ax.set_title(rf"$\theta={g['theta']:g}$, $\epsilon={g['eps']:g}$: card and "
                         "processor seeds", fontsize=9)
            ax.legend(loc="best", fontsize=7)
            fs.save(fig, os.path.join(outdir, f"cardcpu_{gname}"))
            plt.close(fig)
    with open(os.path.join(outdir, "cardcpu.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    short = {k: dict(extrap=v.get("extrapolation_weighted"),
                     rows=[dict(kl=r["k_lambda"], f_w=r["f_w"], se=r["f_w_se"],
                                cpu=(r.get("cpu_mean"), r.get("cpu_se"), r.get("cpu_n")),
                                card=[(c["seed"], c["N"], round(c["f"], 4), round(c["z"], 2))
                                      for c in r.get("card", [])])
                           for r in v["rows"]])
             for k, v in res["groups"].items()}
    print(json.dumps(short, indent=1, default=float))


def cmd_eps(outdir, pa, ga, pb, gb):
    TA = json.load(open(resolve(pa, "T7.json")))
    TB = json.load(open(resolve(pb, "T7.json")))
    gA, rowsA = seeds_of(TA, ga)
    gB, rowsB = seeds_of(TB, gb)
    B = {kl: ss for kl, ss in rowsB}
    out = dict(A=dict(path=pa, group=ga), B=dict(path=pb, group=gb), rows=[])
    for kl, ssA in rowsA:
        if kl not in B:
            continue
        ssB = B[kl]
        fB, seB, s2B = weighted([s["f"] for s in ssB], [s["N"] for s in ssB])
        fA_i = np.array([s["f"] for s in ssA])
        NA = np.array([s["N"] for s in ssA], float)
        fA = float(np.mean(fA_i))
        se_meas = float(fA_i.std(ddof=1) / np.sqrt(len(fA_i))) if len(fA_i) > 1 else np.nan
        scale = (gB["eps"] / gA["eps"]) ** 2
        se_exp = float(np.sqrt(np.sum(s2B * scale / NA)) / len(NA))
        d = fA - fB
        se_d = float(np.sqrt(se_exp ** 2 + seB ** 2))
        out["rows"].append(dict(k_lambda=kl, f_A=fA, f_A_seeds=fA_i.tolist(),
                                f_A_se_measured=se_meas, f_A_se_expected=se_exp,
                                f_B=fB, f_B_se=seB, n_B=len(ssB), delta=d,
                                delta_se_expected=se_d, z=d / se_d,
                                pass_3se=bool(abs(d) < 3 * se_d)))
    if out["rows"]:
        w = np.array([1 / r["delta_se_expected"] ** 2 for r in out["rows"]])
        dd = np.array([r["delta"] for r in out["rows"]])
        out["delta_weighted"] = float(np.sum(w * dd) / np.sum(w))
        out["delta_weighted_se"] = float(1 / np.sqrt(np.sum(w)))
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH * 1.25, 3.0))
    ax = fig.add_axes([0.17, 0.16, 0.78, 0.74])
    for r in out["rows"]:
        x = r["k_lambda"] ** 2
        ax.plot([x - 0.0015] * len(r["f_A_seeds"]), r["f_A_seeds"], "o", ms=3, mfc="none",
                color=fs.PAL["red"], alpha=0.8)
        ax.errorbar(x - 0.0015, r["f_A"], yerr=r["f_A_se_expected"], fmt="o",
                    color=fs.PAL["red"], ms=4, capsize=2)
        ax.errorbar(x + 0.0015, r["f_B"], yerr=r["f_B_se"], fmt="s", color=fs.PAL["blue"],
                    ms=4, capsize=2)
    ax.plot([], [], "o", color=fs.PAL["red"], ms=4,
            label=rf"$\epsilon={gA['eps']:g}$ (seeds, mean $\pm$ expected se)")
    ax.plot([], [], "s", color=fs.PAL["blue"], ms=4,
            label=rf"$\epsilon={gB['eps']:g}$ (pooled $\pm$ se)")
    ax.axhspan(0.99, 1.06, color="grey", alpha=0.12, lw=0)
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$(k\lambda)^2$")
    ax.set_ylabel(r"$f=\kappa/\kappa_1$")
    ax.set_title(rf"$\theta={gA['theta']:g}$: amplitude $\epsilon$ against "
                 rf"$\epsilon={gB['eps']:g}$", fontsize=9)
    ax.legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(outdir, f"eps_{ga}_vs_{gb}"))
    plt.close(fig)
    with open(os.path.join(outdir, "eps.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


PARS = (("dt_frac", r"$\Delta t/t_{\rm coll}$"), ("pmax", r"$P_{\max}$"),
        ("dx_frac", r"$\Delta x/\lambda$"))
BASE = dict(dt_frac=0.1, pmax=0.1, dx_frac=0.25)


def cmd_t8(outdir, noise_path, noise_group, paths):
    TN = json.load(open(resolve(noise_path, "T7.json")))
    _, rowsN = seeds_of(TN, noise_group)
    s2 = None
    for kl, ss in rowsN:
        if abs(kl - 0.2) < 1e-9:
            s2 = weighted([s["f"] for s in ss], [s["N"] for s in ss])[2]
    out = dict(noise=dict(path=noise_path, group=noise_group, s2_kl02=s2), inputs=paths,
               sets=[])
    rows = []
    for p in paths:
        T8 = json.load(open(resolve(p, "T8.json")))
        for r in T8["rows"]:
            r = dict(r)
            r["source"] = p
            rows.append(r)
    for key in sorted({(r["source"], r["seed"], r["n"]) for r in rows}):
        src, seed, n = key
        rs = [r for r in rows if (r["source"], r["seed"], r["n"]) == key]
        sd_change = float(np.sqrt(2 * s2 / n)) if s2 else float("nan")
        S = dict(source=src, seed=seed, n=n, sd_change_expected=sd_change, params={})
        for par, _ in PARS:
            sel = sorted([r for r in rs if all(r[q] == BASE[q] for q in BASE if q != par)],
                         key=lambda r: r[par])
            vals = [r[par] for r in sel]
            f = [r["f_S"] for r in sel]
            fb = [r["f_S"] for r in sel if r[par] == BASE[par]]
            ch = [(vals[i], vals[i + 1], (f[i] - f[i + 1]) / f[i + 1])
                  for i in range(len(sel) - 1)]
            S["params"][par] = dict(values=vals, f=f, f_base=fb[0] if fb else None,
                                    changes=ch,
                                    finest_change=ch[0][2] if ch else None,
                                    finest_z=ch[0][2] / sd_change if ch else None,
                                    max_neighbour_change=max(abs(c[2]) for c in ch)
                                    if ch else None,
                                    pass_2pc=bool(abs(ch[0][2]) < 0.02) if ch else None,
                                    nsub=[r["mean_nsub"] for r in sel],
                                    max_P=[r["max_P"] for r in sel],
                                    max_dx_mfp=[r["max_dx_mfp"] for r in sel],
                                    min_N=[r["min_N"] for r in sel],
                                    n_trunc=[r["n_trunc"] for r in sel])
        out["sets"].append(S)
    # processor seeds pooled: mean of the per-seed finest changes
    by_n = {}
    for S in out["sets"]:
        by_n.setdefault(S["n"], []).append(S)
    out["pooled"] = {}
    for n, Ss in by_n.items():
        P = {}
        for par, _ in PARS:
            c = [S["params"][par]["finest_change"] for S in Ss
                 if S["params"][par]["finest_change"] is not None]
            mx = [S["params"][par]["max_neighbour_change"] for S in Ss
                  if S["params"][par]["max_neighbour_change"] is not None]
            if c:
                P[par] = dict(finest_change_mean=float(np.mean(c)), n_seeds=len(c),
                              sd_mean_expected=Ss[0]["sd_change_expected"] / np.sqrt(len(c)),
                              max_neighbour_change=float(max(mx)))
        out["pooled"][str(n)] = P
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"], fs.PAL["yellow"]]
    for i, (par, lab) in enumerate(PARS):
        ax = fig.add_axes([0.07 + 0.325 * i, 0.17, 0.25, 0.70])
        for j, S in enumerate(sorted(out["sets"], key=lambda S: (-S["n"], S["seed"]))):
            q = S["params"][par]
            if not q["values"] or q["f_base"] is None:
                continue
            rel = 100 * (np.array(q["f"]) / q["f_base"] - 1)
            ax.errorbar(q["values"], rel, yerr=100 * S["sd_change_expected"],
                        fmt="o-", ms=3.5, capsize=2, color=cols[j % len(cols)],
                        label=f"N={S['n']:.0e}, seed {S['seed']}")
        ax.axhspan(-2, 2, color="grey", alpha=0.12, lw=0)
        ax.axhline(0, **fs.MASK_LINE)
        ax.set_xscale("log")
        ax.set_xlabel(lab)
        if i == 0:
            ax.set_ylabel(r"$f/f_{\rm base}-1$ [%]")
            ax.legend(loc="best", fontsize=6.5)
    fig.suptitle(r"T8 at $\theta=0.003$, $k\lambda=0.2$, $\epsilon=0.2$: change of "
                 r"$\kappa$ against the base variant (bars: expected sd of a change)",
                 fontsize=8.5)
    fs.save(fig, os.path.join(outdir, "t8_changes"))
    plt.close(fig)
    with open(os.path.join(outdir, "t8.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    short = [dict(n=S["n"], seed=S["seed"], sd=S["sd_change_expected"],
                  **{par: (S["params"][par]["values"],
                           [round(x, 4) for x in S["params"][par]["f"]],
                           S["params"][par]["finest_change"], S["params"][par]["finest_z"])
                     for par, _ in PARS}) for S in out["sets"]]
    print(json.dumps(dict(sets=short, pooled=out["pooled"]), indent=1, default=float))


def main():
    cmd, outdir = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    if outdir == "-":
        outdir = hl.outdir("compare")
    os.makedirs(outdir, exist_ok=True)
    if cmd == "cardcpu":
        cmd_cardcpu(outdir, args)
    elif cmd == "eps":
        cmd_eps(outdir, *args)
    elif cmd == "t8":
        assert args[0] == "--noise"
        cmd_t8(outdir, args[1], args[2], args[3:])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
