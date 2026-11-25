#!/usr/bin/env python3
"""Importance-sampled tail of the G3 reference at nu = 4 (SCOPE 4d.9 A9).

    NRPIC_REF_NLAT=32 python3 ref_tilt.py NREAL [--pilot 100000] [--direct <samples.npz>]

Same system as the variant s0.01_lattice of ref_spec.py (128^3 band, sigma = 0.01, lattice density of
states, dN = 2e-3, end surfaces phi_bg(N_f), phi_bg(N_e)), with the bias of sdn/langevin.fpt_phase_space:
a shift c0 sqrt(p(N)/int p) of the standard-normal pair along the dominant noise direction during the
window (p: share of the linear variance; the constant shift of A9 as written failed its smoke test, see
PROFILE below), c0 > 0 against the roll (towards F_+), c0 < 0 with the roll (towards F_-). Path weight w = exp(logw).
Stage 1 (pilot, fixed rule written before the run, g3/amend/JOURNAL.md entry 7): per side, pilots of
--pilot paths at |c0| = 3, 3.5, 4, 4.5, 5, 5.5; the median of the tilted x = (dN - m)/s is interpolated
linearly in c to 4.0 (+4 for F_+, -4 for F_-); a confirmation pilot at that c must give a median within
[3.5, 4.5] in magnitude, else the grid point whose median is closest to 4 is used.
Stage 2: NREAL paths per side at the chosen c. Estimator F(nu) = mean(w 1[x > nu]) (plain, unbiased),
standard error sd(w 1)/sqrt(n); also the self-normalised form and mean(w) (should be 1).
Standardisation: m, s = mean and sqrt(var_lattice_Ne) of the direct reference (latsig, the A1 form); and
the direct run's own standard deviation (own); both are reported.
Validation at nu = 3: F_pm(3) of each tilted run against direct sampling (--direct: the npz of the 4e6
run E-20261125-152832-c301e92) within two combined standard errors.
"""
import argparse
import json
import os
import sys
import zlib

ap = argparse.ArgumentParser()
ap.add_argument("nreal", type=int)
ap.add_argument("--pilot", type=int, default=100_000)
ap.add_argument("--direct", required=True)
ap.add_argument("--direct-json", required=True)
args = ap.parse_args()
sys.argv = [sys.argv[0], "inflection"]
import ref_spec as R  # noqa: E402  (module set-up of the inflection case, band NLAT)
import common  # noqa: E402
from common import np, figstyle, pmap, seeds, save_results, savefig  # noqa: E402
from sdn import langevin, linear  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SIG = 0.01
TAB = R.table(SIG, "modes")
VF = R.lattice_factor_fn(SIG)[0]
DJ = json.load(open(args.direct_json))
M_REF = DJ["s0.01_lattice"]["Ne"]["mean"]
S_LAT = float(np.sqrt(DJ["linear"]["var_lattice_Ne"]))
S_OWN = float(np.sqrt(DJ["s0.01_lattice"]["Ne"]["var"]))
NUS = (2.0, 3.0, 4.0, 4.5, 5.0)
# Shift profile (batch 20, g3/amend/JOURNAL.md entry 8): c(N) = c0 sqrt(p(N) / int p dN), p(N) = P_R(k = sigma aH(N))
# at N_e times the lattice factor: the share of the linear delta-N variance that the noise of the step at N carries.
# The constant shift of A9 as written spent its likelihood budget evenly over the window and gave weights of
# log-variance c^2 W (about 39 in the smoke test, mean weight 0.01 at 3200 paths); with the profile the shift
# c0 moves the linear delta N by c0 sigma and the weight log-variance is c0^2.
_KS = R.KMIN * np.exp(np.linspace(0.0, np.log(R.NLAT), 121))
_PR = linear.PR_late(R.BG, _KS, R.P["Ne"])
_LN = np.log(_KS / R.KMIN)


def prof(N):
    return float(np.interp(np.log(SIG * R.BG.aH(N) / R.KMIN), _LN, _PR, left=0.0, right=0.0)) * VF(N)


_NG = np.linspace(*R.window(SIG), 4001)
PNORM = float(np.trapezoid([prof(N) for N in _NG], _NG))


def chunk(n, rng, c):
    Na, Nb = R.window(SIG)
    ps, ws = R.BG.state(R.P["Nstar"])
    ends = [R.BG.state(R.P["Nf"])[0], R.BG.state(R.P["Ne"])[0]]
    r = langevin.fpt_phase_space(R.MODEL, ps, ws, R.P["Nstar"], ends, 2e-3, n, rng, noise=TAB,
                                 window=(Na, Nb), dN_det=0.01, N_max=R.P["Ne"] - R.P["Nstar"] + 60.0,
                                 noise_scale=1.0, var_factor=VF, bias=(lambda N: c * np.sqrt(prof(N) / PNORM)))
    return np.column_stack([r["N"][:, 1], r["logw"]])


def run(c, n, tag):
    nch = 16 if n >= 1600 else 1
    res = pmap(chunk, [(n // nch, rr, c) for rr in seeds(zlib.crc32(f"tilt:{tag}:{c:.6f}".encode()), nch)])
    a = np.concatenate(res, axis=0)
    ok = np.isfinite(a[:, 0])
    return a[ok, 0], np.exp(a[ok, 1]), int((~ok).sum())


def median_x(c, n, tag):
    x, w, _ = run(c, n, tag)
    return float(np.median((x - M_REF) / S_LAT))


def estimate(x, w, s, side):
    d = (x - M_REF) / s
    out = {}
    n = len(d)
    for nu in NUS:
        ind = (d > nu) if side > 0 else (d < -nu)
        y = w * ind
        F = y.mean()
        se = y.std(ddof=1) / np.sqrt(n)
        out[str(nu)] = dict(F=float(F), se=float(se), rel_se=float(se / F) if F > 0 else None,
                            F_selfnorm=float(y.sum() / w.sum()), n_hits=int(ind.sum()))
    return out


def direct(s):
    z = np.load(args.direct)["s0.01_lattice"]
    x = z[:, 1]
    x = x[np.isfinite(x)]
    d = (x - M_REF) / s
    n = len(d)
    out = {}
    for nu in NUS:
        for side, ind in ((1, d > nu), (-1, d < -nu)):
            F = ind.mean()
            out[f"{'+' if side > 0 else '-'}{nu}"] = dict(F=float(F), se=float(np.sqrt(F * (1 - F) / n)))
    return out, n


def main():
    figstyle.use_style()
    out = dict(nreal=args.nreal, pilot=args.pilot, m_ref=M_REF, s_lat=S_LAT, s_own=S_OWN, sides={},
               profile_norm=PNORM, profile_sigma_lin=float(np.sqrt(PNORM)))
    grid = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5)
    figdat = {}
    for side in (+1, -1):
        meds = [median_x(side * g, args.pilot, f"pilot{side:+d}") for g in grid]
        mm = np.array(meds) * side
        print("pilot side", side, dict(zip(grid, meds)), flush=True)
        if mm.min() < 4.0 < mm.max():
            cstar = float(np.interp(4.0, mm, grid)) if np.all(np.diff(mm) > 0) else grid[int(np.argmin(abs(mm - 4)))]
        else:
            cstar = grid[int(np.argmin(abs(mm - 4)))]
        conf = median_x(side * cstar, args.pilot, f"conf{side:+d}") * side
        if not (3.5 <= conf <= 4.5):
            cstar = grid[int(np.argmin(abs(mm - 4)))]
            conf = float(mm[int(np.argmin(abs(mm - 4)))])
        print("side", side, "c* =", cstar, "confirmation median", conf, flush=True)
        x, w, nnan = run(side * cstar, args.nreal, f"main{side:+d}")
        rec = dict(c=side * cstar, pilot_grid=list(grid), pilot_medians=meds, confirmation_median=conf,
                   n=len(x), n_nan=nnan, mean_w=float(w.mean()), se_mean_w=float(w.std(ddof=1) / np.sqrt(len(w))),
                   median_tilted_x=float(np.median((x - M_REF) / S_LAT) * side),
                   latsig=estimate(x, w, S_LAT, side), own=estimate(x, w, S_OWN, side))
        out["sides"]["+" if side > 0 else "-"] = rec
        figdat[side] = (x, w)
        print("side", side, {k: v for k, v in rec.items() if k in ("c", "n", "mean_w", "median_tilted_x")},
              rec["latsig"]["3.0"], rec["latsig"]["4.0"], flush=True)
    for lab, s in (("latsig", S_LAT), ("own", S_OWN)):
        dct, nd = direct(s)
        out[f"direct_{lab}"] = dict(n=nd, **dct)
        val = {}
        for side, key in ((1, "+"), (-1, "-")):
            for nu in ("3.0", "4.0"):
                t = out["sides"][key][lab][nu]
                dd = dct[f"{key}{nu}"]
                comb = float(np.hypot(t["se"], dd["se"]))
                val[f"{key}{nu}"] = dict(tilted=t["F"], direct=dd["F"], diff_over_comb_se=(t["F"] - dd["F"]) / comb,
                                         within_2se=bool(abs(t["F"] - dd["F"]) <= 2 * comb))
        out[f"validation_{lab}"] = val
        print("validation", lab, val, flush=True)
    out["A9_rel_se_nu4"] = {k: out["sides"][k]["latsig"]["4.0"]["rel_se"] for k in ("+", "-")}
    out["A9_rel_se_nu4_own"] = {k: out["sides"][k]["own"]["4.0"]["rel_se"] for k in ("+", "-")}

    # figure: tilted and direct tail fractions per side; weights against x
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 2.9))
    a1 = figstyle.inch_axes(fig, 0.7, 0.5, 3.1, 2.2)
    a2 = figstyle.inch_axes(fig, 4.7, 0.5, 3.1, 2.2)
    from scipy.stats import norm
    nus = np.array(NUS)
    a1.semilogy(nus, norm.sf(nus), **figstyle.GUIDE, label="Gaussian")
    for key, col, mk in (("+", figstyle.PAL["red"], "o"), ("-", figstyle.PAL["blue"], "s")):
        t = out["sides"][key]["latsig"]
        a1.errorbar(nus, [t[str(n)]["F"] for n in NUS], yerr=[2 * t[str(n)]["se"] for n in NUS], fmt=mk,
                    color=col, ms=3.5, label=f"tilted, $F_{key}$")
        dd = out["direct_latsig"]
        fv = np.array([dd[f"{key}{n}"]["F"] for n in NUS])
        okk = fv > 0
        a1.errorbar(nus[okk] + 0.06, fv[okk], yerr=2 * np.array([dd[f"{key}{n}"]["se"] for n in NUS])[okk],
                    fmt=mk, mfc="none", color=col, ms=3.5, label=f"direct 4e6, $F_{key}$")
    a1.set_xlabel(r"$\nu$")
    a1.set_ylabel(r"$F_\pm(\nu)$ (bars: 2 s.e.)")
    a1.legend(loc="lower left", fontsize=6.5)
    for side, col in ((1, figstyle.PAL["red"]), (-1, figstyle.PAL["blue"])):
        x, w = figdat[side]
        d = (x - M_REF) / S_LAT
        sel = np.random.default_rng(1).choice(len(d), size=min(20000, len(d)), replace=False)
        a2.semilogy(d[sel], w[sel], ".", ms=0.6, color=col, alpha=0.4)
    a2.set_xlabel(r"$\delta\mathcal{N}/\sigma_\mathrm{lat}$")
    a2.set_ylabel("path weight $w$")
    savefig(fig, "ref_inflection_n32_tilt")
    plt.close(fig)
    save_results("ref_inflection_n32_tilt", out)


if __name__ == "__main__":
    main()
