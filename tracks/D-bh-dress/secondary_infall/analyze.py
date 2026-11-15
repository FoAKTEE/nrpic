#!/usr/bin/env python3
"""Analysis of tests 2 and 3 of secondary_infall, and the parameters of the AthenaK runs.

Inputs: the output directories of the shell runs (shells.py) and of the self-similar run
(selfsimilar.py); the cost model of the scoping run (../scope/scoping_estimates.py,
part_c, measured AthenaK throughput).

Usage: python3 analyze.py --out <dir> --ss <selfsimilar run dir> --shells <dir> [<dir> ...]
Writes analysis.json, run_plan.txt and the figures growth, profiles, selfsim_check,
phase_space, angular_momentum.
"""
import argparse
import glob
import importlib.util
import json
import math
import os

import numpy as np

from common import HERE, KAPPA, C_TA, PI, load_figstyle, sha256
import selfsimilar as SS

SCOPE = os.path.join(HERE, "..", "scope", "scoping_estimates.py")


def load_shells(dirs):
    runs = {}
    for d in dirs:
        for f in glob.glob(os.path.join(d, "shells_*.npz")):
            z = np.load(f)
            r = {k: z[k] for k in z.files}
            r["cfg"] = json.loads(str(z["cfg"]))
            r["name"] = os.path.basename(f)[len("shells_"):-4]
            r["dir"] = d
            r["file"] = f
            runs[r["name"]] = r
    return runs


def ta_radius(r, t):
    """Turnaround radius at time t from the shells' first-turnaround events."""
    ok = ~np.isnan(r["t_ta"])
    tt, rr = r["t_ta"][ok], r["r_ta"][ok]
    o = np.argsort(tt)
    return float(np.exp(np.interp(t, tt[o], np.log(rr[o]))))


def growth(r):
    m0 = r["m0"]
    ts = r["snap_t"]
    out = dict(a=r["snap_a"], t=ts)
    out["mta"] = np.array([1.0 + m0[r["t_ta"] <= t].sum() for t in ts])
    out["mta_cf"] = np.array([1.0 + m0[r["cf_t_ta"] <= t].sum() for t in ts])
    passed = (r["snap_ncross"] > 0) & r["snap_alive"]
    out["dress"] = np.sum(np.where(passed, r["snap_m"], 0.0), axis=1)
    out["mbh"] = r["snap_mbh"]
    if np.any(~np.isnan(r["cf_t_abs"])):
        out["mbh_cf"] = np.array([1.0 + m0[r["cf_t_abs"] <= t].sum() for t in ts])
    out["rta"] = np.array([ta_radius(r, t) for t in ts])
    # outermost radius of dust that has passed the centre (splashback) at each snapshot
    rs = []
    for k in range(ts.size):
        sel = passed[k]
        rs.append(float(np.max(np.abs(r["snap_r"][k][sel]))) if sel.any() else np.nan)
    out["rsp"] = np.array(rs)
    return out


def at(g, key, a):
    return float(np.interp(math.log(a), np.log(g["a"]), g[key]))


def density_hist(rr, mm, edges):
    h, _ = np.histogram(np.abs(rr), bins=edges, weights=mm)
    vol = 4.0 * PI / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3)
    return h / vol


def density_lagr(rr, mm):
    """Single-stream density between neighbouring shells (no crossing)."""
    o = np.argsort(np.abs(rr))
    r_, m_ = np.abs(rr)[o], mm[o]
    rc = 0.5 * (r_[1:] + r_[:-1])
    rho = 0.5 * (m_[1:] + m_[:-1]) / (4.0 * PI / 3.0 * (r_[1:] ** 3 - r_[:-1] ** 3))
    return rc, rho


def ss_solution(ssdir):
    z = np.load(os.path.join(ssdir, "selfsimilar_profile.npz"))
    js = json.load(open(os.path.join(ssdir, "selfsimilar.json")))
    lnm = z["lnm"]
    # first passage through the centre of the self-similar orbit
    mp = SS.MassProfile(lnm)
    sol = SS.orbit(mp, 6.0, js["soft"])
    tt = np.linspace(1.0, 6.0, 200001)
    L = sol.sol(tt)[0]
    k = np.argmax(L < 0)
    tau_c1 = float(tt[k - 1] + (tt[k] - tt[k - 1]) * L[k - 1] / (L[k - 1] - L[k]))
    return dict(lngrid=z["lngrid"], lnm=lnm, rc=z["rc"], rho=z["rho"], js=js,
                tau_c1=tau_c1, f_passed=tau_c1 ** (-2.0 / 3.0))


def load_scope_cost():
    spec = importlib.util.spec_from_file_location("scoping_estimates", SCOPE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    C = mod.part_c()
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ss", required=True)
    ap.add_argument("--shells", nargs="+", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = load_shells(a.shells)
    ss = ss_solution(a.ss)
    G = {k: growth(r) for k, r in runs.items()}
    res = dict(inputs={}, checks={}, growth={}, selfsim={}, angmom={}, plan=[])
    for k, r in runs.items():
        res["inputs"][r["file"]] = sha256(r["file"])
    for f in ("selfsimilar_profile.npz", "selfsimilar.json"):
        p = os.path.join(a.ss, f)
        res["inputs"][p] = sha256(p)
    res["inputs"][os.path.abspath(SCOPE)] = sha256(SCOPE)
    res["inputs"][os.path.join(HERE, "selfsimilar.py")] = sha256(os.path.join(HERE, "selfsimilar.py"))

    # ---------------------------------------------------------------- 3a-3c checks
    gA = G["absorb_e0.01"]
    rA = runs["absorb_e0.01"]
    for av in (2.0, 4.0, 8.0):
        res["checks"][f"a{av:g}"] = dict(
            mta=at(gA, "mta", av), mta_cf=at(gA, "mta_cf", av),
            c_of_a=(at(gA, "mta", av) - 1.0) / av, c_of_a_cf=(at(gA, "mta_cf", av) - 1.0) / av,
            mbh=at(gA, "mbh", av), mbh_cf=at(gA, "mbh_cf", av),
            mbh_minus1_over_a=(at(gA, "mbh", av) - 1.0) / av,
            rta=at(gA, "rta", av))
    # exact values at the snapshot nearest to a = 2 (interpolation of step functions
    # between snapshots is not exact)
    k2 = int(np.argmin(np.abs(gA["a"] - 2.0)))
    res["checks"]["snapshot_a2"] = dict(
        a=float(gA["a"][k2]), mta=float(gA["mta"][k2]), mta_cf=float(gA["mta_cf"][k2]),
        mbh=float(gA["mbh"][k2]), mbh_cf=float(gA["mbh_cf"][k2]),
        c=float((gA["mta"][k2] - 1.0) / gA["a"][k2]))
    res["checks"]["max_rel_mbh_vs_cf"] = float(np.max(np.abs(gA["mbh"] / gA["mbh_cf"] - 1.0)))
    res["checks"]["max_rel_mta_vs_cf"] = float(np.max(np.abs(gA["mta"] / gA["mta_cf"] - 1.0)))

    # ---------------------------------------------------------------- growth summary
    for k, g in G.items():
        res["growth"][k] = {f"a{av:g}": dict(mta=at(g, "mta", av), dress=at(g, "dress", av),
                                              mbh=at(g, "mbh", av), rta=at(g, "rta", av),
                                              rsp=at(g, "rsp", av))
                            for av in (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 30.0, 100.0)
                            if av <= g["a"][-1] * 1.0001}
    res["selfsim"]["tau_c1"] = ss["tau_c1"]
    res["selfsim"]["f_passed"] = ss["f_passed"]
    res["selfsim"]["lambda1"] = ss["js"]["lambda1"]
    res["selfsim"]["A"] = ss["js"]["A"]

    # ---------------------------------------------------------------- 3d self-similarity
    rP = runs["pass_e0.1_s0.5_a100"]
    gP = G["pass_e0.1_s0.5_a100"]
    gP5 = G.get("pass_e0.1_s5_a100")           # softening 5M: sensitivity only
    edges = np.geomspace(10 ** -2.5, 1.2, 36)
    lc = np.sqrt(edges[1:] * edges[:-1])
    stack = {}
    for target in (10.0, 30.0, 100.0):
        ks = [i for i, av in enumerate(rP["snap_a"]) if 0.8 * target <= av <= target * 1.0001]
        rhos, ms = [], []
        for i in ks:
            t = rP["snap_t"][i]
            rt = gP["rta"][i]
            rho_b = 1.0 / (6.0 * PI * t * t)
            al = rP["snap_alive"][i]
            lam = np.abs(rP["snap_r"][i][al]) / rt
            mm = rP["snap_m"][i][al]
            h, _ = np.histogram(lam, bins=edges, weights=mm)
            vol = 4.0 * PI / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3) * rt**3
            rhos.append(h / vol / rho_b)
            mta = gP["mta"][i]
            menc = np.array([(1.0 + mm[lam < x].sum()) / mta for x in edges[1:]])
            ms.append(menc)
        stack[target] = dict(rho=np.mean(rhos, axis=0), m=np.mean(ms, axis=0), n=len(ks),
                             a=[float(rP["snap_a"][i]) for i in ks])
    rho_ss = np.exp(np.interp(np.log(lc), np.log(ss["rc"]), np.log(ss["rho"])))
    m_ss = np.exp(np.interp(np.log(edges[1:]), ss["lngrid"], ss["lnm"]))
    st = stack[100.0]
    sel = (lc > 0.03) & (lc < 0.3)
    res["selfsim"]["a100_rho_ratio_bins"] = (st["rho"][sel] / rho_ss[sel]).tolist()
    res["selfsim"]["a100_lambda_bins"] = lc[sel].tolist()
    res["selfsim"]["a100_rho_ratio_max_dev"] = float(np.max(np.abs(st["rho"][sel] / rho_ss[sel] - 1)))
    res["selfsim"]["a100_m_ratio_max_dev"] = float(np.max(np.abs(st["m"][sel] / m_ss[sel] - 1)))
    fs_ = (lc > 0.02) & (lc < 0.2) & (st["rho"] > 0)
    res["selfsim"]["a100_slope_0.02_0.2"] = float(np.polyfit(np.log(lc[fs_]), np.log(st["rho"][fs_]), 1)[0])
    res["selfsim"]["ss_slope_0.02_0.2"] = float(np.polyfit(np.log(lc[fs_]), np.log(rho_ss[fs_]), 1)[0])
    ksp = [i for i, av in enumerate(rP["snap_a"]) if av >= 80.0]
    res["selfsim"]["a100_lambda_sp"] = float(np.mean(gP["rsp"][ksp] / gP["rta"][ksp]))
    res["selfsim"]["a100_dress_over_mta"] = float(np.mean(gP["dress"][ksp] / gP["mta"][ksp]))
    res["selfsim"]["a100_c"] = float((gP["mta"][-1] - 1.0) / gP["a"][-1])
    res["selfsim"]["a100_mta"] = float(gP["mta"][-1])
    res["selfsim"]["a100_mta_cf"] = float(gP["mta_cf"][-1])
    if gP5 is not None:
        res["selfsim"]["s5_a100_mta"] = float(gP5["mta"][-1])
        res["selfsim"]["s5_a100_mta_cf"] = float(gP5["mta_cf"][-1])
    for nm in ("pass_e0.01_s0.5", "pass_e0.03_s0.5"):
        res["checks"][nm + "_max_rel_mta_vs_cf"] = float(
            np.max(np.abs(G[nm]["mta"] / G[nm]["mta_cf"] - 1.0)))

    # ---------------------------------------------------------------- 3f angular momentum
    for k in sorted(runs):
        if not k.startswith("absorbL"):
            continue
        r = runs[k]
        i = -1
        al = r["snap_alive"][i]
        passed = (r["snap_ncross"][i] > 0) & al
        captured = r["snap_mbh"][i] - 1.0
        surv = float(r["snap_m"][i][passed].sum())
        collapsed = captured + surv
        # mass-weighted fraction with j < 4 among shells whose radial twin collapsed
        res["angmom"][k] = dict(sigma=r["cfg"]["sigma"], a=float(r["snap_a"][i]),
                                captured=float(captured), surviving_dress=surv,
                                collapsed=float(collapsed),
                                captured_fraction=float(captured / collapsed) if collapsed > 0 else None,
                                mta=float(G[k]["mta"][i]))

    # ---------------------------------------------------------------- run plan
    C = load_scope_cost()
    res["cost_model"] = dict(rz_smr=C["rz_smr"], rz_amr=C["rz_amr"], c_p=C["c_p"],
                             inputs=C["inputs"])
    cost = C["cost"]
    g1, gpass = G["absorb_e0.01"], G["pass_e0.01_s0.5"]
    rows = []
    for eps in (0.003, 0.01, 0.03, 0.1):
        t_i = 2.0 / (3.0 * eps)
        for af in (2.0, 4.0, 8.0):
            T = t_i * (af**1.5 - 1.0)
            mta = at(g1, "mta_cf", af)
            mu_end = mta - 1.0
            r_i_end = (2.0 * mu_end / eps**2) ** (1.0 / 3.0)
            Rbi = 1.2 * r_i_end
            Rbf = Rbi * af
            scale = (eps / 0.01) ** (-2.0 / 3.0)
            row = dict(eps=eps, a=af, T=T, t_i=t_i, mta=mta, M_over_Mta=1.0 / mta,
                       rta=at(g1, "rta", af) * scale, rsp=at(gpass, "rsp", af) * scale,
                       dress=at(gpass, "dress", af), mbh=at(g1, "mbh", af),
                       R_ball_i=Rbi, R_ball_f=Rbf, dust_mass=eps**2 * Rbi**3 / 2.0)
            for dxmin, dxb in ((0.0625, 1.0), (0.0625, 2.0), (0.03125, 1.0)):
                c = cost(T, dxmin, ball_half=1.25 * Rbf, dx_ball=dxb, npart=1e6, rz=C["rz_amr"])
                row[f"card_h_dx{int(round(1 / dxmin))}_b{dxb:g}"] = c["card_h"]
                row[f"blocks_dx{int(round(1 / dxmin))}_b{dxb:g}"] = c["blocks"]
            rows.append(row)
    res["plan"] = rows
    # time for the dress to reach a given mass (Newtonian, pass-through, eps = 0.01 run)
    reach = {}
    for target in (0.25, 0.5, 1.0, 2.0):
        d = gpass["dress"]
        if d[-1] >= target:
            k = int(np.argmax(d >= target))
            av = float(np.exp(np.interp(target, d[k - 1:k + 1], np.log(gpass["a"][k - 1:k + 1]))))
            reach[f"{target:g}"] = dict(a=av, T_over_eps_inv=(2.0 / 3.0) * (av**1.5 - 1.0))
    res["dress_reach"] = reach
    kb = int(np.argmax(G["absorb_e0.01"]["mbh"] >= 2.0))
    res["mbh_doubling_a"] = float(G["absorb_e0.01"]["a"][kb])

    with open(os.path.join(a.out, "analysis.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    with open(os.path.join(a.out, "run_plan.txt"), "w") as f:
        keys = list(rows[0].keys())
        f.write(" ".join(keys) + "\n")
        for row in rows:
            f.write(" ".join(f"{row[k]:.4g}" for k in keys) + "\n")
        f.write("dress_reach " + json.dumps(reach) + "\n")
        f.write("mbh_doubling_a " + str(res["mbh_doubling_a"]) + "\n")

    # ================================================================ figures
    fs = load_figstyle()
    import matplotlib.pyplot as plt

    # --- growth
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.96, wspace=0.27)
    ax = axs[0]
    aa = np.geomspace(1.0, 100.0, 200)
    gpa = G["pass_e0.01_s0.5"]
    ax.plot(gA["a"], gA["mta"] - 1.0, color=fs.PAL["blue"], label=r"$M_{\rm ta}-M$")
    ax.plot(gA["a"], gA["mta_cf"] - 1.0, "o", ms=2.5, mfc="none", color=fs.PAL["blue"],
            label="closed form (no crossing)")
    ax.plot(gA["a"], gA["mbh"] - 1.0, color=fs.PAL["red"], label=r"$M_{\rm bh}-M$ (absorbing)")
    ax.plot(gA["a"], gA["mbh_cf"] - 1.0, "s", ms=2.5, mfc="none", color=fs.PAL["red"])
    ax.plot(gpa["a"], gpa["dress"], color=fs.PAL["yellow"], label=r"dress (passed centre), $\epsilon=0.01$")
    ax.plot(G["pass_e0.03_s0.5"]["a"], G["pass_e0.03_s0.5"]["dress"], ls="--",
            color=fs.PAL["yellow"], label=r"dress, $\epsilon=0.03$")
    ax.plot(gP["a"], gP["dress"], ls=":", color=fs.PAL["green"], label=r"dress, $\epsilon=0.1$, $s=0.5M$")
    ax.plot(gP["a"], gP["mta"] - 1.0, ls=":", color=fs.PAL["blue"], lw=1.0)
    if gP5 is not None:
        ax.plot(gP5["a"], gP5["mta"] - 1.0, ls=(0, (1, 3)), color="grey", lw=1.0,
                label=r"$M_{\rm ta}-M$, $\epsilon=0.1$, $s=5M$ (softening too large)")
    ax.plot(aa, C_TA * aa, **fs.GUIDE, label=r"$0.5648\,a/a_i$")
    ax.plot(aa, C_TA * ss["f_passed"] * aa, color="k", lw=1.0, ls="-.",
            label=rf"self-similar dress $={C_TA * ss['f_passed']:.3f}\,a/a_i$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0, 100.0)
    ax.set_ylim(1e-3, 100.0)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"dust mass $/M$")
    ax.legend(loc="upper left", fontsize=6.5)
    ax = axs[1]
    for g, lab, c, ls in ((gpa, r"dress, $\epsilon=0.01$", fs.PAL["yellow"], "-"),
                          (gP, r"dress, $\epsilon=0.1$, $s=0.5M$", fs.PAL["green"], ":"),
                          (gA, r"$M_{\rm bh}-M$", fs.PAL["red"], "-"),
                          (gA, r"$M_{\rm ta}-M$", fs.PAL["blue"], "-")):
        y = g["dress"] if "dress" in lab else (g["mbh"] - 1 if "bh" in lab else g["mta"] - 1)
        ok = y > 0
        sl = np.gradient(np.log(y[ok]), np.log(g["a"][ok]))
        ax.plot(g["a"][ok], sl, color=c, ls=ls, label=lab)
    ax.axhline(1.0, **fs.GUIDE)
    ax.axhline(1.5, color="grey", ls=":", lw=1.0)
    ax.text(1.1, 1.53, r"$a^{3/2}$ of 1805.09034 (main.tex:216-218)", fontsize=7)
    ax.text(1.1, 0.9, "self-similar: 1", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(1.0, 100.0)
    ax.set_ylim(0.0, 6.0)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"$d\ln M/d\ln a$")
    ax.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(a.out, "growth"))

    # --- profiles for the run parameters (eps = 0.01)
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.93, wspace=0.0)
    rPa, rAb = runs["pass_e0.01_s0.5"], runs["absorb_e0.01"]
    redges = np.geomspace(0.5, 400.0, 34)
    rcen = np.sqrt(redges[1:] * redges[:-1])
    prof = {}
    for ax, av in zip(axs, (2.0, 4.0, 8.0)):
        i = int(np.argmin(np.abs(rPa["snap_a"] - av)))
        t = rPa["snap_t"][i]
        rho_b = 1.0 / (6.0 * PI * t * t)
        al = rPa["snap_alive"][i]
        rho_p = density_hist(rPa["snap_r"][i][al], rPa["snap_m"][i][al], redges) / rho_b
        ax.plot(rcen, np.where(rho_p > 0, rho_p, np.nan), color=fs.PAL["yellow"],
                drawstyle="steps-mid", label="passing (Newtonian mode)")
        j = int(np.argmin(np.abs(rAb["snap_a"] - av)))
        tj = rAb["snap_t"][j]
        alj = rAb["snap_alive"][j]
        rc_l, rho_l = density_lagr(rAb["snap_r"][j][alj], rAb["snap_m"][j][alj])
        ax.plot(rc_l, rho_l * 6.0 * PI * tj * tj, color=fs.PAL["red"], lw=1.0,
                label="absorbing at 2M (cold, full GR proxy)")
        rt = ta_radius(rPa, t)
        lam = rcen / rt
        rho_ssp = np.exp(np.interp(np.log(lam), np.log(ss["rc"]), np.log(ss["rho"])))
        ax.plot(rcen, np.where(lam < 1, rho_ssp, np.nan), color=fs.PAL["blue"], lw=1.0,
                label=r"self-similar $F(r/r_{\rm ta})$")
        # infall stream r^-3/2 from the measured accretion rate
        gA_ = G["absorb_e0.01"]
        mdot = np.gradient(gA_["mbh_cf"], gA_["t"])[j]
        mbh = gA_["mbh"][j]
        rr = np.geomspace(2.0, 0.3 * rt, 30)
        ax.plot(rr, mdot / (4 * PI * rr**2 * np.sqrt(2 * mbh / rr)) * 6 * PI * tj * tj,
                **fs.GUIDE, label=r"$\dot M/(4\pi r^2\sqrt{2M_{\rm bh}/r})$")
        ax.axvline(rt, **fs.MASK_LINE)
        ax.axvline(at(G["pass_e0.01_s0.5"], "rsp", av), color="grey", ls=":", lw=1.0)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.5, 400)
        ax.set_ylim(0.3, 3e6)
        ax.set_xlabel(r"$r/M$")
        ax.set_title(rf"$a/a_i={av:g}$, $t={t:.0f}M$", fontsize=9)
        prof[f"a{av:g}"] = dict(r=rcen.tolist(), rho_pass=rho_p.tolist(),
                                rlagr=rc_l.tolist(), rho_absorb=(rho_l * 6 * PI * tj * tj).tolist(),
                                rta=rt, t=float(t))
    axs[0].set_ylabel(r"$\rho/\rho_b(t)$")
    axs[0].legend(loc="lower left", fontsize=6.5)
    axs[2].text(0.97, 0.95, "grey: $r_{\\rm ta}$\ndotted: outermost\ndust that passed $r=0$",
                transform=axs[2].transAxes, ha="right", va="top", fontsize=7)
    fs.save(fig, os.path.join(a.out, "profiles"))
    with open(os.path.join(a.out, "profiles_eps0.01.json"), "w") as f:
        json.dump(prof, f)

    # --- self-similarity check
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 4.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.10, top=0.97, hspace=0.0)
    ax = axs[0]
    ax.plot(ss["rc"], ss["rho"], color=fs.PAL["blue"], label="self-similar (test 2)")
    cols = [fs.PAL["yellow"], fs.PAL["green"], fs.PAL["red"]]
    for c, target in zip(cols, (10.0, 30.0, 100.0)):
        st = stack[target]
        ax.plot(lc, np.where(st["rho"] > 0, st["rho"], np.nan), color=c, drawstyle="steps-mid",
                lw=1.0, label=rf"shells, $a/a_i\approx{target:g}$")
        axs[1].plot(lc, st["rho"] / rho_ss, color=c, drawstyle="steps-mid", lw=1.0)
    ax.plot(lc, lc ** (-2.25), **fs.GUIDE, label=r"frozen-in $\lambda^{-9/4}$")
    ax.axvline(ss["js"]["lambda1"], **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10 ** -2.5, 1.2)
    ax.set_ylim(0.3, 1e7)
    ax.set_ylabel(r"$\rho/\rho_b(t)$")
    ax.legend(loc="upper right", fontsize=7)
    axs[1].axhline(1.0, **fs.GUIDE)
    axs[1].set_ylim(0.0, 2.0)
    axs[1].set_xlabel(r"$\lambda = r/r_{\rm ta}(t)$")
    axs[1].set_ylabel("shells / test 2")
    fs.save(fig, os.path.join(a.out, "selfsim_check"))

    # --- phase space (eps = 0.01)
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.6), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.18, top=0.90, wspace=0.0)
    for ax, (nm, av) in zip(axs, (("pass_e0.01_s0.5", 2.0), ("pass_e0.01_s0.5", 4.0),
                                  ("pass_e0.01_s0.5", 8.0), ("absorb_e0.01", 8.0))):
        r = runs[nm]
        i = int(np.argmin(np.abs(r["snap_a"] - av)))
        al = r["snap_alive"][i]
        rr = r["snap_r"][i][al]
        vv = r["snap_v"][i][al] * np.sign(rr)
        ax.plot(np.abs(rr), vv, ".", ms=1.0, color=fs.PAL["red"] if "absorb" in nm else fs.PAL["yellow"],
                rasterized=True)
        ax.set_xscale("log")
        ax.set_xlim(0.3, 400)
        ax.set_ylim(-1.0, 1.0)
        ax.axvline(ta_radius(r, r["snap_t"][i]), **fs.MASK_LINE)
        ax.set_title(("absorbing" if "absorb" in nm else "passing") + rf", $a/a_i={av:g}$", fontsize=9)
        ax.set_xlabel(r"$r/M$")
    axs[0].set_ylabel(r"$v_r$ ($c$)")
    fs.save(fig, os.path.join(a.out, "phase_space"))

    # --- angular momentum
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.9))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.96)
    sig = [v["sigma"] for v in res["angmom"].values()]
    ax.plot(sig, [v["captured"] for v in res["angmom"].values()], "o-", color=fs.PAL["red"],
            label=r"captured ($L<4M$)")
    ax.plot(sig, [v["surviving_dress"] for v in res["angmom"].values()], "s-",
            color=fs.PAL["yellow"], label="surviving dress (passed pericentre)")
    ax.plot(sig, [v["collapsed"] for v in res["angmom"].values()], "^--", color="grey",
            label="sum")
    ax.set_xscale("log")
    ax.set_xlabel(r"tangential dispersion $\sigma_i$ at $t_i$ ($c$)")
    ax.set_ylabel(r"mass at $a/a_i=4$ $(M)$, $\epsilon=0.01$")
    ax.legend(loc="center left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "angular_momentum"))

    print(json.dumps({k: res[k] for k in ("checks", "selfsim", "angmom", "dress_reach")},
                     indent=1, default=float))
    print(open(os.path.join(a.out, "run_plan.txt")).read())


if __name__ == "__main__":
    main()
