#!/usr/bin/env python3
"""Tests 2 and 3 of the work package "id": the evolved expanding ball against the exact
solution.

For every registered run with tag t2-* or t3-* (test2_runs.py):
  - areal radius R = r sqrt(g_T) of the tracked particles from the metric reconstructed
    at them (.trajmet.bin) against their own proper time, compared with the exact
    Lemaitre-Tolman-Bondi radius of their shell: eps = R/R_exact - 1, by group of shells
    (initial areal radius in units of the outer radius of the matter) and at fixed proper
    times;
  - constraint statistics in time (.cstat.hst) and by region from the field dumps;
  - gauge: lapse at the centre against the homogeneous laws, lapse profiles, coordinate
    speed of light alpha/sqrt(g_rr) and coordinate radius of the particles, shift.
Writes test2_numbers.json and figs/t2_*.png|pdf (t3_* for the bound ball).

    test2_evolution.py [--prefix t2]
"""
import argparse
import glob
import json
import math
import os

import numpy as np

import idlib
from nrpic import expanding_ball as eb
from nrpic import figstyle as fs
import matplotlib.pyplot as plt

GROUPS = [("core", 0.0, 0.5), ("mid", 0.5, 0.75), ("outer", 0.75, 0.95), ("surface", 0.95, 1.0001)]
TAUS = (2.0, 4.0, 6.0, 8.0, 10.0, 12.0)


def load(man):
    meta = idlib.run_meta(man)
    out = man["output_directory"]
    ball = eb.Ball(M=meta["M"], Rb=meta["Rb"], e0=meta["e0"], RE=meta.get("RE"), edge=meta["edge"])
    args = {a.split("=")[0]: a.split("=")[1] for a in man["command"] if "=" in a and "/" in a.split("=")[0]}
    n = int(args["mesh/nx1"])
    half = float(args["mesh/x1max"])
    tr = idlib.read_traj(out)
    nt = meta["n_tracers"]
    r0 = np.sqrt(np.sum(tr["x"][0] ** 2, axis=-1))
    R0, m, E = ball.shell(r0)
    R, r, grr = idlib.areal_radius(tr["x"], tr["g"])
    Rex = eb.ltb_radius(R0[None, :], tr["tau"], m[None, :], E[None, :])
    eps = R / Rex - 1.0
    frac = R0 / ball.Rout
    groups = {}
    for name, lo, hi in GROUPS:
        groups[name] = np.nonzero((np.arange(len(r0)) >= nt) & (frac >= lo) & (frac < hi))[0]
    for i, f in enumerate(meta["tracer_factors"]):
        groups[f"tracer{f:g}"] = np.arange(i * 26, (i + 1) * 26)
    nhat = tr["x"] / r[..., None]
    d = dict(man=man, meta=meta, ball=ball, n=n, half=half, dx=2.0 * half / n, out=out,
             t=tr["time"], tau=tr["tau"], R=R, r=r, grr=grr, eps=eps, R0=R0, r0=r0,
             alpha=tr["alpha"], betar=np.sum(tr["beta"] * nhat, axis=-1), groups=groups,
             hst=idlib.read_hst(os.path.join(out, "ball.nrpic.hst")),
             cstat=idlib.read_hst(os.path.join(out, "ball.cstat.hst")))
    return d


def eps_at_tau(d, idx, tau):
    """eps of the particles idx at proper time tau (per-particle interpolation); NaN
    for particles that do not reach it."""
    out = np.full(len(idx), np.nan)
    for j, p in enumerate(idx):
        tp = d["tau"][:, p]
        if tp[-1] >= tau:
            out[j] = np.interp(tau, tp, d["eps"][:, p])
    return out


def group_numbers(d):
    res = {}
    for g, idx in d["groups"].items():
        if len(idx) == 0:
            continue
        res[g] = dict(n=int(len(idx)))
        for tau in TAUS:
            e = eps_at_tau(d, idx, tau)
            e = e[np.isfinite(e)]
            if len(e):
                res[g][f"tau{tau:g}"] = dict(mean=float(e.mean()), rms=float(np.sqrt(np.mean(e * e))),
                                             maxabs=float(np.abs(e).max()), n=int(len(e)))
        res[g]["maxabs_all"] = float(np.nanmax(np.abs(d["eps"][:, idx])))
        res[g]["tau_end_mean"] = float(d["tau"][-1, idx].mean())
        res[g]["R_end_over_R0"] = float((d["R"][-1, idx] / d["R0"][idx]).mean())
        res[g]["r_end_over_r0"] = float((d["r"][-1, idx] / d["r0"][idx]).mean())
    return res


def region_constraints(d):
    """Constraint norms by region from the field dumps: interior and exterior cells
    further than four cells from the matter surface (coordinate radius of the outermost
    ball particle in the snapshot of the same time); the exterior region ends at 0.56 of
    the half-width of the mesh (r < 18 M for half-width 32 M), which a signal from the
    mesh boundary does not reach before t = 10 M at 1.4 times the speed of light; the
    region "boundary" is the layer between 0.7 of the half-width and four cells from
    the boundary."""
    out = []
    nt = d["meta"]["n_tracers"]
    snaps = {}
    for f in sorted(glob.glob(os.path.join(d["out"], "ball.part.*.bin"))):
        s = idlib.read_snapshot(f)
        snaps[round(s["time"], 6)] = s
    for f in sorted(glob.glob(os.path.join(d["out"], "ball.field.*.bin"))):
        fld = idlib.read_field(f)
        key = min(snaps, key=lambda t: abs(t - fld["time"])) if snaps else None
        if key is None or abs(key - fld["time"]) > 0.6 * d["dx"]:
            continue
        s = snaps[key]
        ballp = s["tag"] >= nt
        rp = np.sqrt(np.sum(s["x"][ballp] ** 2, axis=1))
        rs = float(rp.max())
        r = idlib.cell_radius(fld["n"], d["half"])
        dx = d["dx"]
        # |M| with the conformally flat inverse metric (chi delta^ij): exact at the
        # start, an approximation later
        mabs = np.sqrt(fld["chi"] * (fld["Mx"] ** 2 + fld["My"] ** 2 + fld["Mz"] ** 2))
        reg = dict(interior=r < rs - 4.0 * dx - 2.0 * d["meta"]["edge"],
                   surface=(r >= rs - 4.0 * dx - 2.0 * d["meta"]["edge"]) & (r <= rs + 4.0 * dx),
                   exterior=(r > rs + 4.0 * dx) & (r < 0.56 * d["half"]),
                   boundary=(r > 0.7 * d["half"]) & (r < d["half"] - 4.0 * dx))
        rec = dict(time=fld["time"], r_surface=rs)
        for name, mask in reg.items():
            if not mask.any():
                rec[name] = dict(H_rms=float("nan"), H_max=float("nan"), M_rms=float("nan"),
                                 M_max=float("nan"), Theta_max=float("nan"))
                continue
            rec[name] = dict(H_rms=float(np.sqrt(np.mean(fld["H"][mask] ** 2))),
                             H_max=float(np.abs(fld["H"][mask]).max()),
                             M_rms=float(np.sqrt(np.mean(mabs[mask] ** 2))),
                             M_max=float(mabs[mask].max()),
                             Theta_max=float(np.abs(fld["Theta"][mask]).max()))
        # radial profiles (shell means) of the lapse, chi and K
        edges = np.arange(0.0, d["half"] - 4.0 * dx + 0.5 * dx, dx)
        idx = np.digitize(r.ravel(), edges) - 1
        ok = (idx >= 0) & (idx < len(edges) - 1)
        cnt = np.maximum(np.bincount(idx[ok], minlength=len(edges) - 1), 1)
        rec["profile"] = dict(
            r=(0.5 * (edges[1:] + edges[:-1])).tolist(),
            alpha=(np.bincount(idx[ok], weights=fld["alpha"].ravel()[ok], minlength=len(edges) - 1) / cnt).tolist(),
            chi=(np.bincount(idx[ok], weights=fld["chi"].ravel()[ok], minlength=len(edges) - 1) / cnt).tolist(),
            K=(np.bincount(idx[ok], weights=(fld["Khat"] + 2.0 * fld["Theta"]).ravel()[ok],
                           minlength=len(edges) - 1) / cnt).tolist(),
            H=np.sqrt(np.bincount(idx[ok], weights=fld["H"].ravel()[ok] ** 2, minlength=len(edges) - 1) / cnt).tolist())
        out.append(rec)
    return out


def gauge_numbers(d):
    h = d["hst"]
    t, alpha_c, tau_c = h[:, 0], h[:, 12], h[:, 14]
    a_c = d["ball"].scale_factor(tau_c)
    ballp = np.concatenate([d["groups"][g[0]] for g in GROUPS])
    c = d["alpha"] / np.sqrt(d["grr"])
    res = dict(t=t.tolist(), alpha_centre=alpha_c.tolist(), tau_centre=tau_c.tolist(),
               a_centre=a_c.tolist(), alpha_min=h[:, 15].tolist(), alpha_max=h[:, 29].tolist(),
               light_speed_max=np.max(c[:, ballp], axis=1).tolist(),
               light_speed_time=d["t"].tolist(),
               betar_surface=np.mean(d["betar"][:, d["groups"]["surface"]], axis=1).tolist())
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="t2")
    a = ap.parse_args()
    pre = a.prefix
    mans = idlib.manifests(pre + "-")
    runs = {tag[len(pre) + 1:]: load(m) for tag, m in sorted(mans.items())}
    numbers = {}
    for k, d in runs.items():
        cs = d["cstat"]
        numbers[k] = dict(run_id=d["man"]["run_id"], cells=d["n"], dx=d["dx"], half=d["half"],
                          card_hours=d["man"]["card_hours"], t_end=float(d["t"][-1]),
                          groups=group_numbers(d), gauge=gauge_numbers(d),
                          regions=region_constraints(d),
                          cstat=dict(t=cs[:, 0].tolist(), H_max=cs[:, 8].tolist(),
                                     H_mean=cs[:, 9].tolist(), M_max=cs[:, 12].tolist(),
                                     M_mean=cs[:, 13].tolist(), Theta_max=cs[:, 7].tolist(),
                                     chi_min=cs[:, 1].tolist(), K_min=cs[:, 3].tolist(),
                                     K_max=cs[:, 4].tolist()))
    with open(os.path.join(idlib.HERE, f"test{pre[1:]}_numbers.json"), "w") as f:
        json.dump(numbers, f)
        f.write("\n")

    # ---- table
    gl = ["core", "mid", "outer", "surface"] + [g for g in next(iter(runs.values()))["groups"] if g.startswith("tracer")]
    for tau in (4.0, 8.0) if pre == "t2" else (4.0, 8.0, 12.0):
        print(f"\nmean and largest |eps| at tau = {tau:g} M by group")
        print("%-16s %6s" % ("case", "dx") + "".join(" %19s" % g for g in gl))
        for k, v in numbers.items():
            row = "%-16s %6.3f" % (k, v["dx"])
            for g in gl:
                e = v["groups"].get(g, {}).get(f"tau{tau:g}")
                row += " %+9.2e %9.2e" % (e["mean"], e["maxabs"]) if e else " %19s" % "-"
            print(row)
    print("\ngauge and constraints at the end")
    print("%-16s %6s %8s %8s %8s %8s %9s %9s %9s %9s %9s %9s" % (
        "case", "t_end", "alpha_c", "tau_c", "a_max", "c_max", "Hmean0", "Hmean_e", "Mmean0", "Mmean_e", "Theta_e", "card_h"))
    for k, v in numbers.items():
        g, c = v["gauge"], v["cstat"]
        print("%-16s %6.2f %8.3f %8.3f %8.3f %8.3f %9.2e %9.2e %9.2e %9.2e %9.2e %9.4f" % (
            k, v["t_end"], g["alpha_centre"][-1], g["tau_centre"][-1], max(g["alpha_max"]),
            max(g["light_speed_max"]), c["H_mean"][0], c["H_mean"][-1], c["M_mean"][0],
            c["M_mean"][-1], c["Theta_max"][-1], v["card_hours"]))

    os.makedirs(idlib.FIGS, exist_ok=True)
    fs.use_style()
    figures(pre, runs, numbers)


def figures(pre, runs, numbers):
    gcol = dict(core=fs.PAL["blue"], mid=fs.PAL["green"], outer=fs.PAL["yellow"],
                surface=fs.PAL["red"])

    fams = {}
    for k in runs:
        fams.setdefault(k.rsplit("-n", 1)[0], []).append(k)
    fams = {f: sorted(v, key=lambda k: -runs[k]["dx"]) for f, v in fams.items() if len(v) >= 2}
    main = "mp" if "mp" in fams else next(iter(fams))
    dxv = runs[fams[main][1]]["dx"]

    # ---- radius against proper time, and its error, for one sequence of resolutions
    for fam, keys in fams.items():
        fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.96, wspace=0.32, hspace=0.24)
        d = runs[keys[-1]]
        tt = np.linspace(0.0, float(np.max(d["tau"])), 300)
        for g, idx in d["groups"].items():
            if not len(idx):
                continue
            c = gcol.get(g, "grey")
            p = idx[np.argsort(d["R0"][idx])[len(idx) // 2]]       # the median shell
            ax[0, 0].plot(d["tau"][:, p], d["R"][:, p], color=c, lw=2.5, alpha=0.5)
            R0, m, E = d["ball"].shell(d["r0"][p])
            ax[0, 0].plot(tt, eb.ltb_radius(R0, tt, m, E), color="k", ls="--", lw=1.0)
        ax[0, 0].set_xlabel(r"proper time of the shell $\tau/M$", labelpad=-2)
        ax[0, 0].set_ylabel(r"areal radius $R/M$")
        ax[0, 0].plot([], [], color="grey", lw=2.5, alpha=0.5, label=r"run, $\Delta x=%g\,M$" % d["dx"])
        ax[0, 0].plot([], [], color="k", ls="--", lw=1.0, label="exact")
        ax[0, 0].legend()
        for k, ls in zip(keys, (":", "--", "-")):
            d = runs[k]
            for g in ("core", "outer", "surface"):
                idx = d["groups"][g]
                ax[0, 1].plot(d["tau"][:, idx].mean(axis=1), d["eps"][:, idx].mean(axis=1),
                              color=gcol[g], ls=ls)
            for g, c in (("tracer1.25", fs.PAL["red"]), ("tracer2", fs.PAL["blue"])):
                if g in d["groups"]:
                    idx = d["groups"][g]
                    ax[1, 0].plot(d["tau"][:, idx].mean(axis=1), d["eps"][:, idx].mean(axis=1),
                                  color=c, ls=ls)
        for g in ("core", "outer", "surface"):
            ax[0, 1].plot([], [], color=gcol[g], label=g)
        for k, ls in zip(keys, (":", "--", "-")):
            ax[0, 1].plot([], [], color="k", ls=ls, label=r"$\Delta x=%g\,M$" % runs[k]["dx"])
        ax[0, 1].legend(ncol=2, fontsize=8)
        ax[0, 1].set_xlabel(r"proper time $\tau/M$", labelpad=-2)
        ax[0, 1].set_ylabel(r"mean of $R/R_{\rm exact}-1$, ball shells")
        ax[1, 0].plot([], [], color=fs.PAL["red"], label=r"tracers at $1.25\,R_{\rm out}$")
        ax[1, 0].plot([], [], color=fs.PAL["blue"], label=r"tracers at $2\,R_{\rm out}$")
        ax[1, 0].legend(fontsize=8)
        ax[1, 0].set_xlabel(r"proper time $\tau/M$", labelpad=-2)
        ax[1, 0].set_ylabel(r"mean of $R/R_{\rm exact}-1$, exterior tracers")
        dx = np.array([runs[k]["dx"] for k in keys])
        ax[0, 1].set_ylabel(r"mean $R/R_{\rm exact}-1$, ball shells")
        ax[1, 0].set_ylabel(r"mean $R/R_{\rm exact}-1$, tracers")
        for g in ("core", "mid", "outer", "surface"):
            for tau, mk in ((4.0, "o"), (8.0, "s")):
                v = [numbers[k]["groups"][g].get(f"tau{tau:g}", {}).get("maxabs", np.nan) for k in keys]
                ax[1, 1].loglog(dx, v, mk + "-", color=gcol[g], mfc="none" if tau == 4.0 else None,
                                label=f"{g}" if tau == 8.0 else None)
        ax[1, 1].loglog(dx, 2e-3 * dx, **fs.GUIDE, label=r"$\propto\Delta x$")
        ax[1, 1].loglog(dx, 2e-4 * dx ** 2, color="k", ls=":", label=r"$\propto\Delta x^2$")
        ax[1, 1].set_xticks(list(dx))
        ax[1, 1].set_xticklabels(["%g" % v for v in dx])
        ax[1, 1].xaxis.set_minor_formatter(plt.NullFormatter())
        ax[1, 1].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
        ax[1, 1].set_ylabel(r"largest $|R/R_{\rm ex}-1|$, $\tau=4$ (open), $8\,M$")
        ax[1, 1].legend(ncol=2, fontsize=8)
        fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_radius_{fam.replace('-', '_')}"))
        plt.close(fig)

    # ---- variants at 128 cells: error of the ball shells against proper time
    var = [k for k in runs if abs(runs[k]["dx"] - dxv) < 1e-9]
    if len(var) > 1:
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0), sharey=False)
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.92, wspace=0.34)
        cols = fs.series_colors(len(var), cmap="turbo")
        for k, c in zip(var, cols):
            d = runs[k]
            for a, g in zip(ax, ("core", "outer", "surface")):
                idx = d["groups"][g]
                a.plot(d["tau"][:, idx].mean(axis=1), np.abs(d["eps"][:, idx]).max(axis=1),
                       color=c, label=k.rsplit("-", 1)[0])
        for a, g in zip(ax, ("core", "outer", "surface")):
            a.set_yscale("log")
            a.set_ylim(1e-6, 0.3)
            a.set_title(f"{g} shells", fontsize=10)
            a.set_xlabel(r"proper time $\tau/M$", labelpad=-2)
        ax[0].set_ylabel(r"largest $|R/R_{\rm exact}-1|$")
        ax[2].legend(fontsize=7, ncol=2, loc="lower right")
        fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_variants"))
        plt.close(fig)

    # ---- constraints in time
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.09, top=0.96, wspace=0.26, hspace=0.06)
    seq = fams[main]
    for k, c in zip(seq, fs.series_colors(max(len(seq), 1))):
        cs = numbers[k]["cstat"]
        lab = r"%s, $\Delta x=%g\,M$" % (k.rsplit("-", 1)[0], numbers[k]["dx"])
        ax[0, 0].semilogy(cs["t"], cs["H_mean"], color=c, label=lab)
        ax[1, 0].semilogy(cs["t"], cs["M_mean"], color=c, label=lab)
    ax[0, 0].legend(fontsize=8)
    for k, c in zip(var, fs.series_colors(len(var), cmap="turbo")):
        cs = numbers[k]["cstat"]
        ax[0, 1].semilogy(cs["t"], cs["H_mean"], color=c, label=k.rsplit("-", 1)[0])
        ax[1, 1].semilogy(cs["t"], cs["M_mean"], color=c)
    ax[0, 1].legend(fontsize=7, ncol=2)
    ax[0, 0].set_ylabel(r"mesh mean of $|H|$")
    ax[1, 0].set_ylabel(r"mesh mean of $|M_i|$")
    ax[1, 0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[1, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_constraints"))
    plt.close(fig)

    # ---- constraints by region (rms) at the dump times
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.92, wspace=0.34)
    for k, c in zip(seq, fs.series_colors(max(len(seq), 1))):
        reg = numbers[k]["regions"]
        t = [r["time"] for r in reg]
        for a, name in zip(ax, ("interior", "surface", "exterior")):
            a.set_ylim(1e-7, 1e-1)
            a.semilogy(t, [np.fmax(r[name]["H_rms"], 1e-20) for r in reg], "o-", color=c,
                       label=r"$H$, $\Delta x=%g$" % numbers[k]["dx"])
            a.semilogy(t, [np.fmax(r[name]["M_rms"], 1e-20) for r in reg], "s--", color=c, mfc="none",
                       label=r"$M_i$, $\Delta x=%g$" % numbers[k]["dx"])
            a.set_title(name, fontsize=10)
            a.set_xlabel(r"coordinate time $t/M$", labelpad=-2)
    ax[0].set_ylabel("rms of the residual in the region")
    ax[0].legend(fontsize=7, ncol=2, loc="lower right")
    fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_constraints_regions"))
    plt.close(fig)

    # ---- radial profile of the Hamiltonian residual: where the violation sits
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.26)
    for k, c in zip(seq, fs.series_colors(max(len(seq), 1))):
        reg = numbers[k]["regions"]
        for rec, ls in zip((reg[2], reg[-1]), (":", "-")):
            ax[0].semilogy(rec["profile"]["r"], np.maximum(rec["profile"]["H"], 1e-20), color=c,
                           ls=ls, label=r"$\Delta x=%g$, $t=%g$" % (numbers[k]["dx"], rec["time"]))
    ax[0].legend(fontsize=7, ncol=2)
    for k, c in zip(var, fs.series_colors(len(var), cmap="turbo")):
        rec = numbers[k]["regions"][-1]
        ax[1].semilogy(rec["profile"]["r"], np.maximum(rec["profile"]["H"], 1e-20), color=c,
                       label=k.rsplit("-", 1)[0])
    ax[1].legend(fontsize=7, ncol=2)
    for a in ax:
        a.set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
        a.set_ylim(1e-9, 1e-1)
    ax[0].set_ylabel(r"rms of $|H|$ in shells")
    ax[1].set_ylabel(r"rms of $|H|$ in shells at the last dump")
    fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_Hprofile"))
    plt.close(fig)

    # ---- gauge
    gk = [k for k in ("mp-n128", "ct-n128", "ct0-n128", "mppg-n128", "mp-n256", "ct-n256",
                      "mp-edge2-n128", "ct-edge2-n128", "bound-mp-n160", "bound-ct-n160",
                      "bound-ct-n320") if k in runs]
    if gk:
        fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
        fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.96, wspace=0.27, hspace=0.24)
        cols = fs.series_colors(len(gk), cmap="turbo")
        for k, c in zip(gk, cols):
            g = numbers[k]["gauge"]
            lab = k
            ax[0, 0].plot(g["t"], g["alpha_centre"], color=c, label=lab)
            a_c = np.array(g["a_centre"])
            law = 1.0 + 6.0 * np.log(a_c) if "mp" in k else a_c
            ax[0, 0].plot(g["t"], law, color=c, ls=":", lw=1.0)
            ax[0, 1].plot(g["light_speed_time"], g["light_speed_max"], color=c, label=lab)
            ax[1, 1].plot(g["light_speed_time"], g["betar_surface"], color=c, label=lab)
        ax[0, 0].plot([], [], color="k", ls=":", lw=1.0, label="homogeneous law")
        ax[0, 0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
        ax[0, 0].set_ylabel("lapse at the centre")
        ax[0, 0].legend(fontsize=7)
        ax[0, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
        ax[0, 1].set_ylabel(r"largest $\alpha/\sqrt{\gamma_{rr}}$ at the ball particles")
        ax[1, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
        ax[1, 1].set_ylabel(r"radial shift $\beta^r$ at the surface shell")
        k0 = gk[0]
        reg = numbers[k0]["regions"]
        for rec, c in zip(reg, fs.series_colors(len(reg), cmap="viridis")):
            ax[1, 0].plot(rec["profile"]["r"], rec["profile"]["alpha"], color=c,
                          label=r"$t=%g\,M$" % rec["time"])
            ax[1, 0].axvline(rec["r_surface"], color=c, lw=0.8, alpha=0.5)
        ax[1, 0].set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
        ax[1, 0].set_ylabel(f"lapse, shell means ({k0})")
        ax[1, 0].legend(fontsize=7, ncol=2)
        fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_gauge"))
        plt.close(fig)

    # ---- profiles of chi, K and the lapse for the two gauges at the last dump
    pk = [k for k in ("mp-n128", "ct-n128", "ct0-n128", "mppg-n128", "bound-ct-n160",
                      "bound-mp-n160") if k in runs]
    if pk:
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
        fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.95, wspace=0.30)
        for k, c in zip(pk, fs.series_colors(len(pk))):
            for rec, ls in zip(numbers[k]["regions"][2::3], ("--", "-")):
                p = rec["profile"]
                lab = r"%s, $t=%g$" % (k.rsplit("-", 1)[0], rec["time"])
                ax[0].plot(p["r"], p["alpha"], color=c, ls=ls, label=lab)
                ax[1].plot(p["r"], p["chi"], color=c, ls=ls)
                ax[2].plot(p["r"], p["K"], color=c, ls=ls)
        ax[0].legend(fontsize=7)
        for a, yl in zip(ax, ("lapse", r"conformal factor $\chi$", r"trace $K$ [$1/M$]")):
            a.set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
            a.set_ylabel(yl)
        fs.save(fig, os.path.join(idlib.FIGS, f"{pre}_profiles"))
        plt.close(fig)


if __name__ == "__main__":
    main()
