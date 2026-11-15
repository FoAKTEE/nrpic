#!/usr/bin/env python3
"""Offline checks of the near-threshold equilibria (JOURNAL.md, Tests 1 and 2), the
counterparts of the monoenergetic checks in python/tests/test_initial_data.py.

    python3 check_equilibria.py --ic DIR_OF_make_equilibria --out DIR

Writes DIR/checks.json (every number, a pass flag per check) and DIR/figdata.npz (arrays
for figures.py). Exit status 0 when every check of Tests 1-7 passes (Test 8, the rows of
gr-qc/0601112, is recorded, not enforced).
"""

import argparse
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.integrate import quad  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

import evstatic as ev  # noqa: E402
import models  # noqa: E402
import paper_values as pv  # noqa: E402
from evstatic import nio  # noqa: E402
from nrpic.st_cluster import radial_laplacian  # noqa: E402

RES = {}
FIG = {}


def record(group, name, value, ok=None, **kw):
    d = dict(value=value, **kw)
    if ok is not None:
        d["pass"] = bool(ok)
    RES.setdefault(group, {})[name] = d
    flag = "" if ok is None else ("PASS" if ok else "FAIL")
    print(f"[{group}] {name}: {value} {flag}", flush=True)


def fam_of(kind, k=0.0, l=0.0, L0=0.0):
    return ev.Family(kind, k=k, l=l, L0=L0)


# ----------------------------------------------------------------------------
# Test 1 and 8: the papers
# ----------------------------------------------------------------------------
def check_binding_table():
    out = []
    for row in pv.BINDING_TABLE:
        fam = fam_of(row["kind"], row["k"], row["l"], row["L0"])
        ym, ebm = ev.first_maximum(fam, 0.05, 1.0, 40)
        yz = ev.first_zero(fam, ym, 2.0, 40)
        for key, ours in (("y_max", ym), ("y_zero", yz)):
            ps = row[key]
            dev = ours - float(ps)
            record("paper_2009.08163", f"{row['name']} {key}", round(ours, 6),
                   ok=abs(dev) <= 1e-3, paper=ps, deviation=dev,
                   within_half_unit=bool(abs(dev) <= pv.half_unit(ps) + 1e-12),
                   locator=row["locator"])
        out.append(dict(name=row["name"], y_max=ym, Eb_max=ebm, y_zero=yz))
        ys = np.linspace(0.02, 1.2, 120)
        FIG[f"eb_{row['name']}_y"] = ys
        FIG[f"eb_{row['name']}_Eb"] = np.array([ev.binding_energy(fam, v) for v in ys])
        FIG[f"eb_{row['name']}_ours"] = np.array([ym, ebm, yz])
    return out


def _y_of_Zc(fam, Z, ys, Zs):
    j = np.nonzero((Zs[:-1] - Z) * (Zs[1:] - Z) <= 0)[0]
    if len(j) == 0:
        return None
    j = j[0]
    return brentq(lambda v: ev.integrate(fam, v)["Zc_infinity"] - Z, ys[j], ys[j + 1], xtol=1e-13)


def check_ar_tables():
    summary = {}
    for case, tb in pv.AR_TABLES.items():
        fam = fam_of("poly", tb["k"], tb["l"], pv.AR_L0["value"])
        ys = np.linspace(0.03, 1.6, 90)
        rows = ev.scan(fam, ys)
        Zs = np.array([d["Zc_infinity"] for d in rows])
        Ebs = np.array([d["Eb"] for d in rows])
        FIG[f"ar{case}_Zc"] = Zs
        FIG[f"ar{case}_Eb"] = Ebs
        FIG[f"ar{case}_sqrtZc"] = np.array([d["Zc_sqrt"] for d in rows])
        ym, ebm = ev.first_maximum(fam, 0.05, 1.2, 40)
        Zmax = ev.integrate(fam, ym)["Zc_infinity"]
        res = []
        for Zs_str, Eb_str, st_lo, st_hi in tb["rows"]:
            Z, hZ = float(Zs_str), pv.half_unit(Zs_str)
            vals = []
            for Zt in np.linspace(Z - hZ, Z + hZ, 7):
                y = _y_of_Zc(fam, Zt, ys, Zs)
                if y is not None:
                    vals.append(ev.integrate(fam, y)["Eb"])
            y_mid = _y_of_Zc(fam, Z, ys, Zs)
            eb_mid = ev.integrate(fam, y_mid)["Eb"]
            lo, hi = min(vals), max(vals)
            hE = pv.half_unit(Eb_str)
            Eb = float(Eb_str)
            outside = max(0.0, (lo - hE) - Eb, Eb - (hi + hE))
            res.append(dict(Zc=Zs_str, Eb_paper=Eb_str, Eb_ours_at_Zc=eb_mid,
                            Eb_range_over_Zc_rounding=[lo, hi], outside_by=outside,
                            ok=outside == 0.0, stable_A_lt_1=st_lo, stable_A_gt_1=st_hi))
        nok = sum(r["ok"] for r in res)
        # stability change (A > 1) against the computed maximum
        last_stable = max(float(r[0]) for r in tb["rows"] if r[3])
        first_unst = min(float(r[0]) for r in tb["rows"] if not r[3])
        record("paper_gr-qc/0601112", f"case {case} rows within rounding", f"{nok}/{len(res)}",
               ok=None, rows=res, locator=tb["locator"])
        record("paper_gr-qc/0601112", f"case {case} Z_c at E_b maximum", round(Zmax, 5),
               ok=None, Eb_max=ebm, y_max=ym,
               table_last_stable_Zc_A_gt_1=last_stable, table_first_unstable_Zc_A_gt_1=first_unst,
               consistent_with_table=bool(last_stable - 0.005 <= Zmax <= first_unst + 0.005))
        FIG[f"ar{case}_max"] = np.array([Zmax, ebm])
        FIG[f"ar{case}_table"] = np.array([[float(a), float(b)] for a, b, _, _ in tb["rows"]])
        summary[case] = dict(Zc_max=Zmax, Eb_max=ebm, rows_ok=nok, rows=len(res))
    return summary


def check_newtonian_limit():
    for k in (0.5, 1.0, 1.5):
        fam = fam_of("poly", k)
        d = ev.integrate(fam, 1e-3)
        n_c = float(fam.moments(1e-3, 0.0)["n"])
        ratio = n_c / (3 * d["N"] / (4 * math.pi * d["R"] ** 3))
        le = ev.lane_emden(k + 1.5)
        rel = ratio / le["rhoc_over_rhomean"] - 1
        record("newtonian_limit", f"k={k} rho_c/rho_mean (y0=1e-3)", round(ratio, 5),
               ok=abs(rel) < 0.01, lane_emden_index=k + 1.5,
               lane_emden=le["rhoc_over_rhomean"], xi1=le["xi1"], rel_diff=rel)


def check_turning_point(ymax_king):
    fam = fam_of("king")
    ys = np.linspace(0.02, 3.0, 300)
    rows = ev.scan(fam, ys)
    M = np.array([d["M"] for d in rows])
    R = np.array([d["R"] for d in rows])
    i = next(j for j in range(1, len(ys) - 1) if M[j] >= M[j - 1] and M[j] >= M[j + 1])
    from scipy.optimize import minimize_scalar
    y_M = minimize_scalar(lambda v: -ev.integrate(fam, v)["M"], bounds=(ys[i - 1], ys[i + 1]),
                          method="bounded", options=dict(xatol=1e-9)).x
    record("king_mass_radius", "y0 of first M maximum", round(float(y_M), 5),
           ok=y_M < ymax_king, y_max_binding=ymax_king,
           claim="2009.08163 lines 1160-1167: the y_max point lies 'to the left of the first "
                 "turning point' of the mass-radius spiral; states stay stable past the turning "
                 "point, i.e. the first M maximum comes before the E_b maximum along y0")
    FIG["king_MR_y"] = ys
    FIG["king_MR_M"] = M
    FIG["king_MR_R"] = R
    FIG["king_MR_marks"] = np.array([ymax_king, y_M])


# ----------------------------------------------------------------------------
# Test 2: per-model checks
# ----------------------------------------------------------------------------
def _shell_integral(md, r1, r2, keys, n=400):
    """int_{r1}^{r2} 4 pi r^2 e^lambda g dr (areal r) for g in keys and for g = 1."""
    x, w = np.polynomial.legendre.leggauss(n)
    r = 0.5 * (r2 - r1) * x + 0.5 * (r1 + r2)
    w = 0.5 * (r2 - r1) * w
    y, m, N, I = md._state(r)
    el = 1.0 / np.sqrt(1.0 - 2.0 * m / r)
    dv = 4 * math.pi * r * r * el * w
    mo = md.matter_areal(r)
    out = {k: float(np.sum(mo[k] * dv)) for k in keys}
    out["V"] = float(np.sum(dv))
    return out


def energy_cdf(md, nx=1500, nr=6000):
    """Continuum CDF of x = E/E0 over the whole model (shape only; paper units)."""
    fam = md.fam
    s = md.Mscale
    r = np.linspace(md.r_in, md.R, nr + 2)[1:-1]
    y, m, N, I = md._state(r)
    rp = r / s
    el = 1.0 / np.sqrt(1.0 - 2.0 * m / r)
    em2 = 1.0 + fam.L0 / (rp * rp) if fam.L0 else np.ones_like(rp)
    ey = np.exp(y)
    xmin = float(np.min(np.sqrt(em2) / ey))
    xs = np.linspace(xmin, 1.0, nx)
    pdf = np.empty(nx)
    wr = 4 * math.pi * rp * rp * el * (rp ** (2 * fam.l) if fam.l else 1.0)
    for i, xv in enumerate(xs):
        eps = xv * ey
        g = np.clip(eps * eps - em2, 0.0, None) ** (fam.l + 0.5)
        pdf[i] = np.trapezoid(wr * ey * eps * g, rp) * float(fam.phi(xv))
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (pdf[1:] + pdf[:-1]) * np.diff(xs))])
    return xs, pdf / cdf[-1], cdf / cdf[-1]


def _particle_q(md, x, u):
    rb = np.linalg.norm(x, axis=1)
    nh = x / rb[:, None]
    ps = md.psi(rb)
    q = u / ps[:, None] ** 2
    eps = np.sqrt(1.0 + np.sum(q * q, axis=1))
    w = np.sum(q * nh, axis=1)
    vt2 = np.sum(q * q, axis=1) - w * w
    return rb, eps, w, vt2


def _ecdf_dev(samples, cdf):
    s = np.sort(samples)
    n = len(s)
    F = cdf(s)
    return float(max(np.max(np.arange(1, n + 1) / n - F), np.max(F - np.arange(n) / n)))


def check_model(spec, ic_dir, N_file, seed):
    fam = models.FAMILIES[spec["family"]]
    md = ev.Equilibrium(fam, spec["y0"])
    tag = spec["tag"]
    g = f"model {tag}"
    iso = fam.l == 0 and fam.L0 == 0
    rs = md.rbar_s
    # 1. matching and rest mass
    dpsi = abs(md.psi(rs)[0] - (1 + 0.5 / rs))
    dal = abs(md.alpha(rs)[0] - (1 - 0.5 / rs) / (1 + 0.5 / rs))
    d = 1e-6 * rs
    slope = (md.psi(rs)[0] - md.psi(rs - d)[0]) / d
    dslope = abs(slope + 0.5 / rs ** 2) / (0.5 / rs ** 2)
    dR = abs(md.areal_of(rs)[0] - md.R)
    record(g, "psi, alpha matching at rbar_s", f"{dpsi:.1e}, {dal:.1e}", ok=dpsi < 1e-12 and dal < 1e-12)
    record(g, "psi slope continuity (rel)", f"{dslope:.2e}", ok=dslope < 1e-5)
    record(g, "areal(rbar_s) - R", f"{dR:.1e}", ok=dR < 1e-10)
    M0_iso = quad(lambda v: 4 * math.pi * v * v * md.psi(v)[0] ** 6 * md.matter(v, ("n",))["n"][0],
                  md.rbar_in, rs, epsabs=0, epsrel=1e-11, limit=400)[0]
    rel = M0_iso / md.M0 - 1
    record(g, "rest mass, isotropic integral / N - 1", f"{rel:.2e}", ok=abs(rel) < 1e-8)
    # 2. pressures and TOV
    r = np.linspace(md.r_in, md.R, 2001)[1:-1]
    r = r[(r > md.r_in + 0.02 * (md.R - md.r_in)) & (r < md.R - 0.02 * (md.R - md.r_in))]
    mo = md.matter_areal(r)
    if iso:
        dpt = float(np.max(np.abs(mo["pT"] - mo["p"]) / np.max(mo["p"])))
        record(g, "isotropic: max |p_T - p| / max p", f"{dpt:.1e}", ok=dpt < 1e-12)
    h = 1e-4 * (md.R - md.r_in)
    pp = md.matter_areal(r + h, ("p",))["p"]
    pm = md.matter_areal(r - h, ("p",))["p"]
    dp = (pp - pm) / (2 * h)
    y, m, N, I = md._state(r)
    mup = (m / r ** 2 + 4 * math.pi * r * mo["p"]) / (1 - 2 * m / r)
    tov = dp + mup * (mo["rho"] + mo["p"]) + 2 * (mo["p"] - mo["pT"]) / r
    scale = float(np.max(np.abs(mup * (mo["rho"] + mo["p"]))))
    tv = float(np.max(np.abs(tov)) / scale)
    record(g, "anisotropic TOV residual (rel)", f"{tv:.1e}", ok=tv < 1e-6)
    # 3. Hamiltonian constraint of the table
    rt, ut, at = md.table_arrays(4000, 1.5)
    psi = 1 + ut
    src = -2 * math.pi * psi ** 5 * md.matter(rt, ("rho",))["rho"]
    res = radial_laplacian(rt, psi) - src
    sc = float(np.max(np.abs(src)))
    band = 0.05 * rs
    ok_rows = np.isfinite(res) & (np.abs(rt - rs) > band)
    if md.rbar_in > 0:
        ok_rows &= np.abs(rt - md.rbar_in) > band
    hc = float(np.max(np.abs(res[ok_rows])) / sc)
    record(g, "HC residual of the table (rel, 4th-order FD)", f"{hc:.2e}", ok=hc < 1e-6,
           rows=int(ok_rows.sum()))
    FIG[f"hc_{tag}_r"] = rt
    FIG[f"hc_{tag}_res"] = np.abs(res) / sc
    gmax = 0.0
    for f_ in (0.25, 0.5, 0.75, 1.0):
        Rb = md.rbar_in + f_ * (rs - md.rbar_in)
        ra = md.areal_of(Rb)[0]
        _, mE, _, _ = md._state(ra)
        lhs = 0.5 * Rb * md.psi(Rb)[0] * (math.sqrt(1 - 2 * mE[0] / ra) - 1)
        rhs = -2 * math.pi * quad(lambda v: md.psi(v)[0] ** 5 * md.matter(v, ("rho",))["rho"][0] * v * v,
                                  md.rbar_in, Rb, epsabs=0, epsrel=1e-11, limit=400)[0]
        gmax = max(gmax, abs(lhs / rhs - 1))
    record(g, "HC Gauss form (rel)", f"{gmax:.1e}", ok=gmax < 1e-6)
    # 4.-5. the production particle file
    stem = f"{tag}_stratified_N{N_file}_s{seed}"
    x, u, m, sp = nio.read_nrp(os.path.join(ic_dir, stem + ".nrp"))
    meta = json.load(open(os.path.join(ic_dir, stem + ".json")))
    x2, u2, m2, sp2, aux = ev.sample(md, N_file, "stratified", seed)
    ubar = np.array(meta["net_momentum_removed"]["mean_u"])
    rt_ok = np.array_equal(x, x2) and np.allclose(u, u2 - ubar, rtol=0, atol=1e-15) and \
        np.array_equal(m, m2) and np.all(sp == 0)
    record(g, "file round trip = regenerated sample", rt_ok, ok=rt_ok,
           mean_u_removed=meta["net_momentum_removed"]["mean_u"])
    tab = nio.read_tab(os.path.join(ic_dir, stem + ".tab"))
    Mlast = 2 * tab[0][-1] * tab[1][-1]
    record(g, "table monopole M = 2 r_N u_N", f"{Mlast:.12f}", ok=abs(Mlast - 1) < 1e-12)
    rb = np.linalg.norm(x, axis=1)
    Fr = lambda v: md.enclosed_fraction_areal(md.areal_of(v))
    dev = _ecdf_dev(rb, Fr)
    devc = _ecdf_dev(x[:, 2] / rb, lambda c: (c + 1) / 2)
    record(g, "stratified radial ECDF deviation * N", f"{dev * N_file:.3f}", ok=dev <= 1 / N_file + 1e-9)
    record(g, "stratified cos(theta) ECDF deviation * N", f"{devc * N_file:.3f}", ok=devc <= 1 / N_file + 1e-9)
    edges = np.array([md.rbar_of(md.R)[0] * 0] + [0.0] * 8)
    # equal-mass shell edges in rbar (bisection on the areal CDF)
    Uq = np.linspace(0, 1, 9)
    ra_edges = np.empty(9)
    for i, U in enumerate(Uq):
        if U == 0:
            ra_edges[i] = md.r_in
        elif U == 1:
            ra_edges[i] = md.R
        else:
            ra_edges[i] = brentq(lambda v: md.enclosed_fraction_areal(v)[0] - U, md.r_in + 1e-15,
                                 md.R, xtol=1e-14)
    edges = md.rbar_of(ra_edges)
    edges[0] = md.rbar_in
    edges[-1] = rs * (1 + 1e-12)
    counts = np.histogram(rb, edges)[0]
    record(g, "stratified equal-mass shell counts", counts.tolist(),
           ok=bool(np.all(counts == N_file // 8)))
    # invariants on the unshifted sample
    ps = md.psi(np.linalg.norm(x2, axis=1))
    W = np.sqrt(1 + np.sum(u2 * u2, axis=1) / ps ** 4)
    E = md.alpha(np.linalg.norm(x2, axis=1)) * W
    L = np.sum(np.cross(x2, u2) ** 2, axis=1)
    L0M = fam.L0 * md.Mscale ** 2
    okE = float(E.max() / md.E0) <= 1 + 1e-12
    okL = (L.min() >= L0M * (1 - 1e-9)) if fam.L0 else True
    record(g, "max E/E0, min L/L0", f"{E.max() / md.E0:.12f}, "
           + (f"{L.min() / L0M:.9f}" if fam.L0 else "n/a"), ok=okE and okL)
    rel = meta["table_constraint"]["rel_diff"]
    record(g, "sum m W/psi - M (file)", f"{rel:+.2e}", ok=abs(rel) < 1e-3)
    # energy distribution of the file sample
    xs, pdf, cdf = energy_cdf(md)
    Ex = E / md.E0
    ks_strat = stats.kstest(Ex, lambda v: np.interp(v, xs, cdf))
    record(g, "stratified file: KS statistic of E/E0", f"{ks_strat.statistic:.4f}",
           pvalue=float(ks_strat.pvalue))
    FIG[f"E_{tag}_x"] = xs
    FIG[f"E_{tag}_pdf"] = pdf
    FIG[f"E_{tag}_sample"] = Ex
    FIG[f"r_{tag}_sample"] = rb
    if fam.L0:
        FIG[f"L_{tag}_sample"] = L / L0M
    # moments, both samplers, N = 2e4
    zall = {}
    for method in ("mc", "stratified"):
        xm, um, mm, _, _ = ev.sample(md, 20000, method, seed=11)
        rbm, eps, w, vt2 = _particle_q(md, xm, um)
        zmax = 0.0
        zs = []
        mom_ok = True
        for i in range(8):
            sel = (rbm >= edges[i]) & (rbm < edges[i + 1])
            ex = _shell_integral(md, ra_edges[i], ra_edges[i + 1], ("n", "rho", "p", "pT"))
            V = ex["V"]
            zrow = []
            for key, gg in (("n", np.ones(sel.sum())), ("rho", eps[sel]),
                            ("p", w[sel] ** 2 / eps[sel]), ("pT", vt2[sel] / (2 * eps[sel]))):
                est = np.sum(mm[sel] * gg) / V
                sig = np.sqrt(np.sum((mm[sel] * gg) ** 2)) / V
                z = abs(est - ex[key] / V) / sig
                zrow.append(z)
                zmax = max(zmax, z)
            zs.append(zrow)
            Sr = np.sum(mm[sel] * w[sel])
            mom_ok &= abs(Sr) < 5 * np.sqrt(np.sum((mm[sel] * w[sel]) ** 2))
        record(g, f"{method} N=2e4: max z of shell moments", f"{zmax:.2f}", ok=zmax < 4.5 and mom_ok,
               radial_momentum_ok=bool(mom_ok))
        zall[method] = np.array(zs)
        if method == "mc":
            ksr = stats.kstest(rbm, Fr)
            psm = md.psi(rbm)
            Em = md.alpha(rbm) * eps / md.E0
            kse = stats.kstest(Em, lambda v: np.interp(v, xs, cdf))
            record(g, "mc N=2e4: KS p-values radius, E/E0",
                   f"{ksr.pvalue:.3f}, {kse.pvalue:.3f}", ok=ksr.pvalue > 1e-3 and kse.pvalue > 1e-3)
    FIG[f"z_{tag}_mc"] = zall["mc"]
    FIG[f"z_{tag}_strat"] = zall["stratified"]
    # profiles for the figure
    rr = np.linspace(0, 1.3 * rs, 700)
    mo = md.matter(rr)
    FIG[f"prof_{tag}_r"] = rr
    for k_ in ("n", "rho", "p", "pT"):
        FIG[f"prof_{tag}_{k_}"] = mo[k_]
    FIG[f"prof_{tag}_psi"] = md.psi(rr)
    FIG[f"prof_{tag}_alpha"] = md.alpha(rr)
    return md


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ic", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--N", type=int, default=10000)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tb = check_binding_table()
    ar = check_ar_tables()
    check_newtonian_limit()
    check_turning_point(next(t["y_max"] for t in tb if t["name"] == "king"))
    specs = models.model_set()
    for spec in specs:
        check_model(spec, a.ic, a.N, a.seed)
    RES["model_set"] = specs
    RES["thresholds"] = dict(binding_table=tb, ar=ar)
    fails = [(g, n) for g, d in RES.items() if isinstance(d, dict)
             for n, v in d.items() if isinstance(v, dict) and v.get("pass") is False]
    RES["failures"] = fails
    with open(os.path.join(a.out, "checks.json"), "w") as f:
        json.dump(RES, f, indent=1, default=float)
    np.savez_compressed(os.path.join(a.out, "figdata.npz"), **FIG)
    print(f"{len(fails)} failed checks: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
