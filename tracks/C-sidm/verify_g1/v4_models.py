"""V4 (second part): the track's model files against my own equilibria, after my thresholds
were computed (run C-20261121-080313-84094f1).

Reads only the model files (*.json, *.nrp) of runs C-sidm-20261115-120610-b4592be and
C-20261115-170742-84990ed. For each King (b = 1), truncated-MB (b = 0.1) and k = 0.5 polytrope
model: my equilibrium at the model's y0, compared in M_ADM = 1 units. Then:
- the k = 0.5 polytrope E_b maximum (2009.08163 Table, line 954: 0.298);
- the Juttner onset with Gamma_1 at the energy-matched temperature (<E>_MJ(T) = rho/n), the
  definition named in the role field of the model files, beside my Tolman-temperature one;
- the radial distribution of the 1e5 particles of the King and b = 0.1 threshold models against
  my enclosed rest mass as a function of the isotropic radius (KS distance).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy import integrate, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import lib  # noqa: E402
import v4_ev  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
RUNS = ["C-sidm-20261115-120610-b4592be", "C-20261115-170742-84990ed"]
V4RUN = "C-20261121-080313-84094f1"


def theta_em(e_per_n):
    """Temperature of the Maxwell-Juttner gas with the same mean energy per particle."""
    if e_per_n - 1 < 1e-7:
        return (e_per_n - 1)/1.5 if e_per_n > 1 else 1e-12
    return optimize.brentq(lambda t: lib.mean_w(t) - e_per_n, 1e-9, 50.0, xtol=1e-15, rtol=1e-14)


def omega_em(y0, b, J=200):
    eq, sol = v4_ev.solve(y0, b, dense=True)
    bg = v4_ev.background(eq, sol, b, J)
    Tem = np.array([theta_em(r/n) for r, n in zip(bg["rho"], bg["n"])])
    g = np.array([v4_ev.gamma1_mj(t) for t in Tem])
    lam, rq1, _ = v4_ev.fem_lowest(bg, g)
    return lam, rq1, eq, float(Tem[0])


def onset_em(b, kind, lo, hi):
    idx = 0 if kind == "FEM" else 1
    y = optimize.brentq(lambda t: omega_em(t, b)[idx], lo, hi, xtol=1e-10)
    lam, rq1, eq, T0 = omega_em(y, b)
    lam4 = omega_em(y, b, J=400)[0]
    return dict(eq, kind=kind, omega2=lam, omega2K1=rq1, omega2_J400=lam4, T_em_c=T0,
                T_tolman_c=(b*np.exp(y) if not isinstance(b, str) else None))


def isotropic_cdf(y0, b):
    """Enclosed rest mass fraction against the isotropic radius rbar (units of M)."""
    eq, sol = v4_ev.solve(y0, b, dense=True)
    R, M, N = eq["R"], eq["M"], eq["N"]
    r = np.linspace(R*1e-6, R, 40001)
    S = sol.sol(r)
    m, Nr = S[0], S[2]
    # d ln rbar/dr = 1/(r sqrt(1 - 2m/r)); match rbar at R to the exterior r = rbar (1 + M/2rbar)^2
    rbs = 0.5*(R - M + np.sqrt(R*R - 2*M*R))
    integrand = 1/(r*np.sqrt(1 - 2*m/r))
    # integral over decreasing r is -int_r^R, so ln rbar(r) = ln rbar_s - int_r^R = ln rbar_s + that
    lnrb = np.log(rbs) + (integrate.cumulative_trapezoid(integrand[::-1], r[::-1], initial=0.0))[::-1]
    rb = np.exp(lnrb)
    return rb/M, Nr/N, rbs/M, eq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v4m")
    os.makedirs(out, exist_ok=True)
    res = dict(models=[])
    for run in RUNS:
        for f in sorted(glob.glob(f"{SCR}/{run}/*.json")):
            if f.endswith("index.json"):
                continue
            d = json.load(open(f))
            fam = d.get("family")
            if fam == "king":
                b = 1.0
            elif fam == "tmb":
                b = float(d["b"])
            elif fam == "poly" and d.get("tag", "").startswith("poly05"):
                b = "poly0.5"
            else:
                res["models"].append(dict(file=os.path.basename(f), run=run, skipped=fam))
                continue
            y0 = float(d["y0"])
            eq = v4_ev.solve(y0, b)[0]
            M = eq["M"]
            mine = dict(Eb=eq["Eb"], C=eq["C"], Zc=eq["Z0"], M_paper=M, R_M=eq["R"]/M,
                        M0=eq["N"]/M)
            n0, rho0, p0 = v4_ev.moments(y0, b)
            mine.update(n_c=n0*M*M, rho_c=rho0*M*M, p_c=p0*M*M)
            theirs = dict(Eb=d["Eb_over_M0"], C=d["compactness_M_over_R"], Zc=d["Zc_infinity"],
                          M_paper=d["paper_units_length_per_M"], R_M=d["R_areal"], M0=d["M0"],
                          n_c=d["n_c"], rho_c=d["rho_c"], p_c=d["p_c"])
            row = dict(file=os.path.basename(f), run=run, family=fam, b=b, y0=y0, role=d.get("role"))
            row["rel"] = {k: mine[k]/theirs[k] - 1 for k in mine}
            row["mine"] = mine
            row["theirs"] = theirs
            res["models"].append(row)
            print(row["file"], json.dumps(row["rel"], default=float))
    # k = 0.5 polytrope E_b maximum
    yp = optimize.minimize_scalar(lambda t: -v4_ev.solve(t, "poly0.5")[0]["Eb"], bounds=(0.2, 0.4),
                                  method="bounded", options=dict(xatol=1e-8)).x
    yz = optimize.brentq(lambda t: v4_ev.solve(t, "poly0.5")[0]["Eb"], 0.5, 0.9, xtol=1e-10)
    res["poly05"] = dict(y_Ebmax=float(yp), y_Ebzero=float(yz), paper_max=0.298, paper_zero=0.693)
    print("poly05", res["poly05"])
    # energy-matched-temperature Juttner onsets
    v4 = json.load(open(f"{SCR}/{V4RUN}/v4_ev.json"))
    em = {}
    for fam, b, lo, hi in [("f21", 0.1, 0.30, 0.444), ("king", 1.0, 0.03, 0.40)]:
        ys = np.linspace(lo, hi, 15)
        vals = [omega_em(t, b) for t in ys]
        em[fam + "_scan"] = [dict(y0=float(t), Z0=v[2]["Z0"], omega2=v[0], omega2K1=v[1], T_em_c=v[3])
                             for t, v in zip(ys, vals)]
        for kind, idx in [("FEM", 0), ("K1", 1)]:
            w = np.array([v[idx] for v in vals])
            k = np.where((w[:-1] > 0) & (w[1:] <= 0))[0]
            if len(k) == 0:
                em[f"{fam}_{kind}"] = dict(none=True, first=float(w[0]), last=float(w[-1]))
                print("em onset", fam, kind, "none in", lo, hi, w[0], w[-1])
                continue
            o = onset_em(b, kind, ys[k[0]], ys[k[0] + 1])
            em[f"{fam}_{kind}"] = o
            print("em onset", fam, kind, json.dumps({x: o[x] for x in ["y0", "Z0", "w0", "C", "Eb", "omega2", "omega2K1", "omega2_J400", "T_em_c", "T_tolman_c"]}, default=float))
    res["energy_matched"] = em
    # particle samples of the two threshold models: isotropic radius distribution
    ks = []
    for run, tag, b in [("C-20261115-170742-84990ed", "king_y0p33403_stratified_N100000_s1", 1.0),
                        ("C-20261115-170742-84990ed", "tmb01_Z0p5404_stratified_N100000_s1", 0.1),
                        ("C-20261115-170742-84990ed", "tmb01_Z0p6348_stratified_N100000_s1", 0.1)]:
        d = json.load(open(f"{SCR}/{run}/{tag}.json"))
        P = lib.read_nrp(f"{SCR}/{run}/{tag}.nrp")
        com = np.sum(P["m"][:, None]*P["x"], axis=0)/np.sum(P["m"])
        rb = np.sqrt(np.sum((P["x"])**2, axis=1))
        rbc = np.sqrt(np.sum((P["x"] - com)**2, axis=1))
        rgrid, cdf, rbs, eq = isotropic_cdf(float(d["y0"]), b)
        srt = np.sort(rb)
        emp = np.arange(1, len(srt) + 1)/len(srt)
        model = np.interp(srt, rgrid, cdf)
        D = float(np.max(np.abs(emp - model)))
        Dc = float(np.max(np.abs(emp - np.interp(np.sort(rbc), rgrid, cdf))))
        ks.append(dict(tag=tag, N=int(P["n"]), D=D, D_about_com=Dc, D_random_95=1.36/np.sqrt(P["n"]),
                       rbar_s_mine=rbs, rbar_s_theirs=d["rbar_s"], r_max_particles=float(srt[-1]),
                       sum_m=float(np.sum(P["m"])), M0_mine=eq["N"]/eq["M"], com=com.tolist()))
        print("sample", json.dumps(ks[-1], default=float))
        res.setdefault("_cdf", {})[tag] = (srt[::200].tolist(), emp[::200].tolist(), rgrid[::100].tolist(), cdf[::100].tolist())
    res["samples"] = ks
    cdfs = res.pop("_cdf")
    lib.save_json(os.path.join(out, "v4_models.json"), res)
    figures(out, res, cdfs, v4)
    v4_ev.figures(out, v4)   # V4 figure redrawn with the right axis inside the frame


def figures(out, res, cdfs, v4):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.2, top=0.88, wspace=0.35)
    rows = [r for r in res["models"] if "rel" in r]
    keys = ["Eb", "C", "Zc", "M_paper", "R_M", "M0", "n_c", "rho_c", "p_c"]
    for i, k in enumerate(keys):
        vals = [abs(r["rel"][k]) + 1e-17 for r in rows]
        ax[0].semilogy(np.full(len(vals), i) + np.linspace(-0.3, 0.3, len(vals)), vals, "o", ms=3,
                       color=figstyle.SERIES[i % 5])
    ax[0].set_xticks(range(len(keys)))
    ax[0].set_xticklabels(keys, rotation=60, fontsize=7)
    ax[0].set_ylabel("|mine / model file - 1|")
    ax[0].set_title("%d model files (King, b = 0.1, k = 0.5)" % len(rows), fontsize=8)
    for tag, col in zip(cdfs, [P["blue"], P["red"], P["green"]]):
        srt, emp, rg, cdf = cdfs[tag]
        ax[1].plot(srt, np.array(emp) - np.interp(srt, rg, cdf), color=col, lw=1, label=tag[:12])
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].axhspan(-1.36/np.sqrt(1e5), 1.36/np.sqrt(1e5), color="grey", alpha=0.15)
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"isotropic radius $\bar r/M$")
    ax[1].set_ylabel("sample CDF - my CDF")
    ax[1].legend(fontsize=6)
    em = res["energy_matched"]
    sc = em["f21_scan"]
    ax[2].plot([s["Z0"] for s in sc], [s["omega2"] for s in sc], "o-", ms=3, color=P["orange"],
               label=r"$\Gamma_1(T_{em})$, exact")
    ax[2].plot([s["Z0"] for s in sc], [s["omega2K1"] for s in sc], "s--", ms=3, mfc="none",
               color=P["orange"], lw=1, label=r"$\Gamma_1(T_{em})$, $\xi = r e^\Phi$")
    s4 = [s for s in v4["scans"]["f21"] if 0.3 <= s["Z0"] <= 0.75]
    ax[2].plot([s["Z0"] for s in s4], [s["omega2_mj"] for s in s4], color=P["red"], lw=1,
               label=r"$\Gamma_1(T_{Tolman})$, exact")
    ax[2].plot([s["Z0"] for s in s4], [s["omega2_f21"] for s in s4], color=P["green"], lw=1,
               label=r"$1 + p/u$, exact")
    ax[2].axhline(0, color="k", lw=0.8)
    ax[2].set_yscale("symlog", linthresh=0.1)
    ax[2].set_xlabel(r"$Z(0)$ (F21, $b$ = 0.1)")
    ax[2].set_ylabel(r"$\omega_0^2$")
    ax[2].legend(fontsize=6)
    fig.savefig(os.path.join(out, "v4_models.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
