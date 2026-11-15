#!/usr/bin/env python3
"""Lead's recheck L9 of the models package (wave 2).

(a) The 13 particle files at N = 1e5 (run C-20261115-170742-84990ed) read with rvlib's own
    readers: E = alpha W <= E0, sum m W/psi against the ADM mass, equal masses, net momentum,
    the count inside the core radius.
(b) Fluid onset of the F21 b = 0.1 family with five adiabatic indices, from the verifier's
    Rayleigh-Ritz operator (stage/G0/verifier/v_pulsation.py, kingsolve.py; not the models
    helper's finite elements) and rvlib's own Juttner functions:
    F21 gamma = 1 + p/u; Juttner Gamma_1 = 1 + 1/c_v at the energy-matched temperature
    (<W>_J(theta_E) = rho/n) and at theta = p/n; Juttner 1 + p_J/u = 1 + theta_E/(rho/n - 1);
    fixed 5/3.
(c) Rerun of models/validate_growth.py on the first paper's runs, compared with
    models/results/growth_validation.json.
Output: $NRPIC_RUN_DIR/rv_models.json, rv_models.{png,pdf}.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

TR = os.path.join(rv.WT, "tracks", "C-sidm")
sys.path.insert(0, os.path.join(TR, "stage", "G0", "verifier"))
sys.path.insert(0, os.path.join(rv.WT, "python"))
import kingsolve as ks  # noqa: E402
import v_pulsation as vp  # noqa: E402

R_MOD = os.path.join(rv.SCR, "C-20261115-170742-84990ed")


def particle_checks():
    idx = json.load(open(os.path.join(R_MOD, "index.json")))
    tags = sorted({p.split("_stratified")[0] for p in os.listdir(R_MOD) if p.endswith(".nrp")})
    res = {}
    for tag in tags:
        stem = os.path.join(R_MOD, f"{tag}_stratified_N100000_s1")
        js = json.load(open(stem + ".json"))
        p = rv.read_nrp(stem + ".nrp")
        rg, ug, ag = rv.read_table(stem + ".tab")
        r = np.sqrt(np.sum(p["x"] ** 2, 1))
        psi = 1.0 + rv.interp4(rg, ug, r)
        alpha = rv.interp4(rg, ag, r)
        W = np.sqrt(1.0 + np.sum(p["u"] ** 2, 1) / psi ** 4)
        E = alpha * W
        smWpsi = math.fsum((p["m"] * W / psi).tolist())
        mom = [math.fsum((p["m"] * p["u"][:, i]).tolist()) for i in range(3)]
        cr = js.get("centre_resolution", {})
        rbc = cr.get("rbar_core")
        n_in = int(np.sum(r < rbc)) if rbc else None
        res[tag] = dict(N=p["n"], E_over_E0_max=float(E.max() / js["E0"]),
                        E_over_E0_max_json=js["particle_invariants"]["E_over_E0_max"],
                        sum_mW_over_psi_minus_M=smWpsi / js["M_ADM"] - 1,
                        json_rel_diff=js["table_constraint"]["rel_diff"],
                        masses_equal=bool(np.all(p["m"] == p["m"][0])),
                        sum_m_rel=math.fsum(p["m"].tolist()) / js["M0"] - 1,
                        max_abs_sum_mu=float(max(abs(x) for x in mom)),
                        N_inside_core=n_in, N_inside_core_json=cr.get("N_inside_core"),
                        Z0=js["Zc_infinity"])
        print(tag, res[tag], flush=True)
    return res, idx


def omega2(w0, gam, b=0.1, K=16):
    m = ks.solve(b, w0, dense=True)
    R = m["R"]
    r, wt = vp.nodes(R)
    prof = ks.profile(m, r)
    n, rho, p, u = prof["n"], prof["rho"], prof["p"], prof["u"]
    if gam != "F21":
        g = np.full_like(r, 5.0 / 3.0)
        ok = (n > 1e-300) & (u > 1e-12 * np.maximum(n, 1e-300))
        e = 1.0 + u[ok] / n[ok]          # rho/n without the cancellation of rho - n
        if gam == "J_E":
            g[ok] = 1.0 + 1.0 / rv.c_v(rv.theta_from_W_vec(e))
        elif gam == "J_pn":
            g[ok] = 1.0 + 1.0 / rv.c_v(p[ok] / n[ok])
        elif gam == "J_puE":
            g[ok] = 1.0 + rv.theta_from_W_vec(e) / (e - 1.0)
        elif gam in ("J_T", "J_pu"):
            # Tolman temperature theta_T = b W_c(r) = b E_c / e^{Phi} (kingsolve docstring)
            thT = b * math.sqrt(1 - 2 * m["M"] / R) / prof["ePhi"][ok]
            if gam == "J_T":
                g[ok] = 1.0 + 1.0 / rv.c_v(thT)
            else:
                g[ok] = 1.0 + thT / (rv.mean_W(thT) - 1.0)
        prof["gamma"] = g
    a = r[np.argmin(abs(prof["rho"] - 0.5 * m["rho_c"]))]
    return vp.rr_lowest(prof, wt, R, K, a), m


def onsets():
    res = {}
    grid = np.arange(1.6, 6.01, 0.2)
    for gam in ("F21", "J_E", "J_pn", "J_T", "J_pu", "J_puE", "5/3"):
        f = lambda w: omega2(w, gam)[0]  # noqa: E731
        vals = [f(w) for w in grid]
        sc = [i for i in range(len(grid) - 1) if vals[i] > 0 >= vals[i + 1]]
        if not sc:
            res[gam] = dict(root=None, scan=[list(map(float, grid)), vals])
            continue
        lo, hi = grid[sc[0]], grid[sc[0] + 1]
        w = brentq(f, lo, hi, xtol=1e-7)
        w10 = brentq(lambda x: omega2(x, gam, K=10)[0], lo, hi, xtol=1e-7)
        res[gam] = dict(w0=w, Z0=ks.solve(0.1, w)["Z0"], w0_K10=w10,
                        Z0_K10=ks.solve(0.1, w10)["Z0"])
        print(gam, res[gam], flush=True)
    # E_b (eps) maximum of the same solver, for the comparison
    from scipy.optimize import minimize_scalar
    mx = minimize_scalar(lambda w: -ks.solve(0.1, w)["eps"], bounds=(2.9, 3.4), method="bounded",
                         options=dict(xatol=1e-8)).x
    res["eps_max"] = dict(w0=mx, Z0=ks.solve(0.1, mx)["Z0"])
    curve = []
    for w in np.linspace(2.9, 3.8, 10):
        row = dict(w0=float(w), Z0=float(ks.solve(0.1, w)["Z0"]))
        for gam in ("F21", "J_E", "J_pn"):
            row[gam] = float(omega2(w, gam)[0])
        curve.append(row)
    res["curve"] = curve
    return res


def growth_rerun(out):
    d = os.path.join(out, "validate_growth")
    os.makedirs(d, exist_ok=True)
    cmd = [sys.executable, os.path.join(TR, "models", "validate_growth.py"), "--out", d]
    rc = subprocess.run(cmd, cwd=rv.WT, capture_output=True, text=True)
    new = json.load(open(os.path.join(d, "growth_validation.json")))
    old = json.load(open(os.path.join(TR, "models", "results", "growth_validation.json")))
    g1 = [(a["quantity"], a["run"], a["ours"], b["ours"], a["match"])
          for a, b in zip(new["G1"], old["G1"])]
    return dict(rc=rc.returncode, identical=bool(new == old), G1_pass_new=new.get("G1_pass"),
                G1_rows=len(g1), G1_all_match=all(x[4] for x in g1),
                G1_same_as_committed=all(x[2] == x[3] for x in g1))


def figure(r, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.9, wspace=0.32)
    c = r["onsets"]["curve"]
    z = [q["Z0"] for q in c]
    for gam, col, lab in (("F21", fs.PAL["blue"], r"F21 $1+p/u$"),
                          ("J_E", fs.PAL["red"], r"Jüttner $\Gamma_1(\theta_E)$"),
                          ("J_pn", fs.PAL["yellow"], r"Jüttner $\Gamma_1(p/n)$")):
        ax[0].plot(z, [q[gam] for q in c], "o-", color=col, ms=3, label=lab)
        if r["onsets"][gam].get("Z0"):
            ax[0].axvline(r["onsets"][gam]["Z0"], color=col, lw=1, ls=":")
    ax[0].axvline(r["onsets"]["eps_max"]["Z0"], **fs.GUIDE, label=r"$E_b$ maximum")
    ax[0].axhline(0, color="grey", lw=0.8)
    ax[0].set_yscale("symlog", linthresh=0.1)
    ax[0].set_xlabel(r"$Z(0)$, $b = 0.1$")
    ax[0].set_ylabel(r"lowest $\hat\omega^2$ (Ritz, 16 terms)")
    ax[0].legend(fontsize=7, frameon=False)
    pc = r["particles"]
    tags = sorted(pc, key=lambda t: pc[t]["Z0"])
    ax[1].plot(range(len(tags)), [1e5 * pc[t]["sum_mW_over_psi_minus_M"] for t in tags], "o",
               color=fs.PAL["blue"], ms=4, label="this recheck")
    ax[1].plot(range(len(tags)), [1e5 * pc[t]["json_rel_diff"] for t in tags], "x",
               color=fs.PAL["red"], ms=5, label="model JSON")
    ax[1].set_xticks(range(len(tags)))
    ax[1].set_xticklabels([t.replace("_", "\n") for t in tags], fontsize=5)
    ax[1].set_ylabel(r"$10^5\,(\sum m W/\psi - M)/M$, $N = 10^5$")
    ax[1].axhline(0, **fs.GUIDE)
    ax[1].legend(fontsize=7, frameon=False)
    fs.save(fig, os.path.join(out, "rv_models"))


def main():
    out = rv.outdir()
    r = {}
    r["particles"], _ = particle_checks()
    r["growth_rerun"] = growth_rerun(out)
    print(r["growth_rerun"], flush=True)
    r["onsets"] = onsets()
    json.dump(r, open(os.path.join(out, "rv_models.json"), "w"), indent=1, default=float)
    figure(r, out)
    print("done", out)


if __name__ == "__main__":
    main()
