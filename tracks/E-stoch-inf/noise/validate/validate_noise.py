#!/usr/bin/env python3
"""Validation of a noise field written by the code (NOISE_SPEC.md, section 10).

    python3 validate_noise.py --run U1 [--blocks8 U2] [--blocks64 U3] [--restart U4]
        [--res-lo U5a --res-hi U5b] [--seed2 U8] [--card U9] --out DIR

Each argument is a run directory of AthenaK `bin` files (or an `.npz` of the self-test).
The single-run tests A0-A10 run on --run; the comparisons A11-A15 on the pairs given.
Writes validation.json (one record per test, with the worst value and the criterion),
summary.txt and figures fig_val_*.png/pdf, and exits with status 1 if a test fails.
The reference is ref/noise_ref.py with the draws of ref/philox_ref.py.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ref"))
import noise_ref as nr                                    # noqa: E402
import athenak_io as aio                                  # noqa: E402

FW = 1e-3                        # family-wise false-alarm probability per validation
P_FA = 1e-4                      # level used in the first (counting) pass only
Z_FA = stats.norm.isf(P_FA / 2)
# current per-decision level and number of decisions made (validate_single sets the level
# to FW / D after counting the D statistical decisions of the validation)
STATE = {"p": P_FA, "z": Z_FA, "count": 0}


def dp(p):
    """One statistical decision on a two-sided p-value."""
    STATE["count"] += 1
    return p >= STATE["p"]


def dz(z):
    """One statistical decision on a standard-normal statistic."""
    STATE["count"] += 1
    return abs(z) <= STATE["z"]


def set_level(p):
    STATE["p"] = p
    STATE["z"] = float(stats.norm.isf(p / 2))
    STATE["count"] = 0
ACTIVE = 1e-6                    # active modes: |G| > ACTIVE max|G|
WHITE = 1e-3                     # whitened-amplitude tests: |G| > WHITE max|G|
A9_TOL = 1e-6
NEFF_MIN = 100                   # normal approximations need this many effective modes
Z4_MIN = 1000                    # modes needed for the fourth-moment z-test of A3


def neff(w):
    """Effective number of modes (sum w)^2 / sum w^2 of non-negative weights."""
    w = np.asarray(w, dtype=np.float64)
    s2 = float((w**2).sum())
    return float(w.sum()**2 / s2) if s2 > 0 else 0.0


def tolerances(prec):
    return (1e-11, 1e-10) if prec == "double" else (1e-5, 1e-5)


def rec(tid, name, passed, value, criterion, detail=""):
    """One test record; passed is True, False or None (not applicable), as Python bool."""
    return dict(id=tid, name=name, passed=None if passed is None else bool(passed),
                value=value, criterion=criterion, detail=detail)


def gamma_p(x, m):
    """Two-sided p of the sum of m Exp(1) variables."""
    return float(min(1.0, 2.0 * min(stats.gamma.cdf(x, m), stats.gamma.sf(x, m))))


def norm_p(z):
    return float(2.0 * stats.norm.sf(abs(z)))


class Analysed:
    """Code output of one run, transformed, with the reference transfer functions."""

    def __init__(self, run, log="agm"):
        self.run = run
        self.p = dict(run["params"])
        self.lat = nr.Lattice(run["N"], run["L"], self.p["nmax2"])
        self.cycles = sorted(run["outputs"])
        self.eps_x, self.eps_m = tolerances(run["precision"])
        self.coef, self.full, self.G = {}, {}, {}
        for cyc in self.cycles:
            for v, f in run["outputs"][cyc]["fields"].items():
                c, Fh = nr.analyse(self.lat, np.asarray(f, dtype=np.float64))
                self.coef[(v, cyc)] = c
                self.full[(v, cyc)] = Fh
                if v.startswith("stoch_c"):
                    self.G[(v, cyc)] = nr.transfer(self.lat, int(v[-1]), cyc, self.p)
                elif v == "stoch_acc0":
                    self.G[(v, cyc)] = nr.acc_transfer(self.lat, cyc, self.p)
        self.ref = nr.reference_outputs(self.lat, self.p, self.cycles, log=log)

    def keys(self, prefix="stoch_c"):
        return [k for k in self.coef if k[0].startswith(prefix)]

    def rms_m(self, key):
        return float(np.sqrt(np.mean(np.abs(self.coef[key])**2)))

    def field(self, key):
        return np.asarray(self.run["outputs"][key[1]]["fields"][key[0]], dtype=np.float64)


# ------------------------------------------------------------------ single-run tests
def test_A0(a):
    p, run = a.p, a.run
    bad = []
    for cyc in a.cycles:
        o = run["outputs"][cyc]
        miss = [v for v in run.get("expected_vars", aio.NOISE_VARS) if v not in o["fields"]]
        if miss:
            bad.append(f"cycle {cyc}: missing {miss}")
        for v, f in o["fields"].items():
            if np.shape(f) != (run["N"],) * 3:
                bad.append(f"{v}@{cyc}: shape {np.shape(f)}")
        t = o["time"]
        if t is None or abs(t - nr.out_time(cyc, p)) > 1e-12 * max(1.0, abs(t)):
            bad.append(f"cycle {cyc}: time {t} != t0 + cycle dt = {nr.out_time(cyc, p)}")
    for k in ("seed", "scheme", "amplitudes", "nmax2", "window", "ksigma0", "hubble",
              "amp", "phase1", "dt", "N", "L", "x0"):
        if p.get(k) is None:
            bad.append(f"parameter {k} missing")
    return rec("A0", "format", not bad, len(bad), "no inconsistency", "; ".join(bad[:5]))


def test_A1(a, data):
    worst, where = 0.0, ""
    for key, cref in a.ref.items():
        if key not in a.coef:
            continue
        if key[0] == "stoch_acc0" and a.p["scheme"] == "frozen":
            continue                                       # A9
        fref, _ = nr.synthesise(a.lat, cref)
        d = float(np.abs(a.field(key) - fref).max())
        rms = float(np.sqrt(np.mean(fref**2)))
        e = d / rms if rms > 0 else (0.0 if d == 0.0 else np.inf)
        data.setdefault("A1", {})[f"{key[0]}@{key[1]}"] = e
        if e > worst:
            worst, where = e, f"{key[0]}@{key[1]}"
    return rec("A1", "exact reconstruction from the keys", worst <= a.eps_x, worst,
               f"max|xi - xi_ref| / rms <= {a.eps_x:g}", f"worst {where}")


def shell_test(u, q, label):
    """Gamma test per integer shell of the whitened powers u (one per active mode)."""
    s = np.floor(q + 0.5).astype(int)
    shells = np.unique(s)
    ps, ratios, ms = [], [], []
    for sh in shells:
        m = s == sh
        x = float(u[m].sum())
        ps.append(gamma_p(x, int(m.sum())))
        ratios.append(x / m.sum())
        ms.append(int(m.sum()))
    ps = np.array(ps)
    zpool = float((u.mean() - 1.0) * np.sqrt(u.size))
    return dict(label=label, shells=shells.tolist(), ratio=ratios, M=ms,
                pmin_bonf=float(ps.min() * ps.size), zpool=zpool)


def test_A2(a, data):
    keys = a.keys("stoch_c") + ([k for k in a.coef if k[0] == "stoch_acc0"]
                                if a.p["scheme"] == "markov" else [])
    worst_p, worst_z, fails = 1.0, 0.0, []
    out = data.setdefault("A2", {})
    for key in keys:
        G = a.G[key]
        if np.abs(G).max() == 0.0:
            continue
        act = np.abs(G) > ACTIVE * np.abs(G).max()
        u = np.abs(a.coef[key][act])**2 / np.abs(G[act])**2
        r = shell_test(u, a.lat.q[act], f"{key[0]}@{key[1]}")
        out[r["label"]] = r
        tests = [r]
        if key[0] == "stoch_c3":
            mu = a.lat.mu2[act]
            b = np.minimum((mu * 5).astype(int), 4)
            r2 = shell_test(u, b.astype(float), r["label"] + " mu2 bins")
            out[r2["label"]] = r2
            tests.append(r2)
        for t in tests:
            worst_p = min(worst_p, t["pmin_bonf"])
            if abs(t["zpool"]) > abs(worst_z):
                worst_z = t["zpool"]
            ok1, ok2 = dp(t["pmin_bonf"]), dz(t["zpool"])
            if not (ok1 and ok2):
                fails.append(t["label"])
    return rec("A2", "spectrum per shell (and mu bins of c3)", not fails,
               dict(min_p_bonferroni=worst_p, max_abs_zpool=worst_z),
               f"min p * shells >= {STATE['p']:.2g}, |z_pool| <= {STATE['z']:.2f}",
               "fails: " + ", ".join(fails[:6]))


def test_A3(a, data):
    fails, worst = [], dict(p_mod=1.0, p_arg=1.0, z4=0.0)
    out = data.setdefault("A3", {})
    for key in a.keys("stoch_c"):
        G = a.G[key]
        if np.abs(G).max() == 0.0:
            continue
        sel = np.abs(G) > WHITE * np.abs(G).max()
        if sel.sum() < 50:
            continue
        w = a.coef[key][sel] / G[sel]
        m2 = np.abs(w)**2
        p_mod = float(stats.kstest(m2, "expon").pvalue)
        p_arg = float(stats.kstest(np.angle(w) / (2 * np.pi) + 0.5, "uniform").pvalue)
        z4 = (float((np.mean(m2**2) - 2.0) / np.sqrt(20.0 / m2.size))
              if m2.size >= Z4_MIN else 0.0)
        lab = f"{key[0]}@{key[1]}"
        out[lab] = dict(p_mod=p_mod, p_arg=p_arg, z4=z4, M=int(sel.sum()),
                        w2=m2.tolist() if key == (a.keys("stoch_c")[0]) else None)
        worst["p_mod"] = min(worst["p_mod"], p_mod)
        worst["p_arg"] = min(worst["p_arg"], p_arg)
        worst["z4"] = z4 if abs(z4) > abs(worst["z4"]) else worst["z4"]
        ok = [dp(p_mod), dp(p_arg)] + ([dz(z4)] if m2.size >= Z4_MIN else [])
        if not all(ok):
            fails.append(lab)
    return rec("A3", "Gaussian amplitudes", not fails, worst,
               f"KS p >= {STATE['p']:.2g} (|w|^2 ~ Exp(1), arg uniform), |z4| <= {STATE['z']:.2f}",
               "fails: " + ", ".join(fails[:6]))


def test_A4(a, data):
    lags = nr.standard_lags(a.lat.N)
    fails, worst = [], 1.0
    out = data.setdefault("A4", {})
    N = a.lat.N
    for key in a.keys("stoch_c") + [k for k in a.coef if k[0] == "stoch_acc0"]:
        G = a.G[key]
        if np.abs(G).max() == 0.0:
            continue
        if neff(np.abs(G)**2) < NEFF_MIN:
            data.setdefault("A4_skipped", []).append(f"{key[0]}@{key[1]}")
            continue
        Fh = a.full[key]
        corr = np.real(np.fft.ifftn(np.abs(Fh)**2)) * N**3
        meas = corr[lags[:, 0] % N, lags[:, 1] % N, lags[:, 2] % N]
        exp, var = nr.expected_corr(a.lat, G, lags)
        ok = var > 0
        z = (meas[ok] - exp[ok]) / np.sqrt(var[ok])
        pmin = float(min(1.0, 2 * stats.norm.sf(np.abs(z).max()) * ok.sum()))
        lab = f"{key[0]}@{key[1]}"
        out[lab] = dict(lags=lags.tolist(), meas=meas.tolist(), exp=exp.tolist(),
                        sd=np.sqrt(var).tolist(), pmin_bonf=pmin)
        worst = min(worst, pmin)
        if not dp(pmin):
            fails.append(lab)
    return rec("A4", "correlation function", not fails, worst,
               f"min p * lags >= {STATE['p']:.2g}", "fails: " + ", ".join(fails[:6]))


def test_A5(a, data):
    worst, info = 0.0, {}
    for key in a.coef:
        f = a.field(key)
        rms = np.sqrt(np.mean(f**2))
        if rms == 0:
            continue
        m = abs(float(f.mean())) / rms
        worst = max(worst, m)
        info[f"{key[0]}@{key[1]}"] = dict(mean_over_rms=m, skew=float(stats.skew(f.ravel())),
                                          exkurt=float(stats.kurtosis(f.ravel())))
    data["A5"] = info
    return rec("A5", "one-point: zero mean (skewness, kurtosis reported)",
               worst <= a.eps_x, worst, f"|mean| / rms <= {a.eps_x:g}")


def ratio_dev(cb, ca, r, rms_b, rms_a):
    """max over modes of |cb - r ca| / (rms_b + |r| rms_a): rounding-scaled deviation."""
    return float((np.abs(cb - r * ca) / (rms_b + np.abs(r) * rms_a)).max())


def test_A6(a, data):
    worst, fails, stat = 0.0, [], {}
    for cyc in a.cycles:
        k0 = ("stoch_c0", cyc)
        if k0 not in a.coef:
            continue
        G0 = a.G[k0]
        if np.abs(G0).max() == 0.0:
            continue
        act = np.abs(G0) > ACTIVE * np.abs(G0).max()
        for c in (1, 3):
            kc = (f"stoch_c{c}", cyc)
            if kc not in a.coef:
                continue
            if a.p["amplitudes"] == "pair" and c == 1:
                if neff(np.abs(G0[act])**2) < NEFF_MIN:
                    continue
                x1, x0 = a.coef[kc][act], a.coef[k0][act]
                t = x1 * np.conj(x0)
                mean = (np.abs(G0[act])**2) * np.cos(a.p["phase1"])
                zr = float((t.real.sum() - mean.sum()) / np.sqrt(((t.real - mean)**2).sum()))
                zi = float(t.imag.sum() / np.sqrt((t.imag**2).sum()))
                stat[f"c1@{cyc}"] = dict(z_re=zr, z_im=zi)
                ok1, ok2 = dz(zr), dz(zi)
                if not (ok1 and ok2):
                    fails.append(f"c1@{cyc} z=({zr:.1f},{zi:.1f})")
                continue
            r = a.G[kc][act] / G0[act]
            e = ratio_dev(a.coef[kc][act], a.coef[k0][act], r, a.rms_m(kc), a.rms_m(k0))
            stat[f"c{c}@{cyc}"] = e
            worst = max(worst, e)
            if e > a.eps_m:
                fails.append(f"c{c}@{cyc} dev {e:.2e}")
    data["A6"] = stat
    return rec("A6", "components of one degree of freedom share the amplitudes",
               not fails, worst, f"deviation <= {a.eps_m:g} (pair, c1: |z| <= {STATE['z']:.2f})",
               "fails: " + ", ".join(fails[:6]))


def indep_z(xa, xb, Ga, Gb):
    """z of Re and Im of sum xa conj(xb) for independent unit amplitudes (G real or
    phase-corrected): variance sum |Ga|^2 |Gb|^2 / 2 per part."""
    ph = np.conj(Ga) * Gb
    ph = np.where(np.abs(ph) > 0, ph / np.abs(ph), 1.0)
    s = np.sum(xa * np.conj(xb) * ph)
    sd = np.sqrt(np.sum(np.abs(Ga)**2 * np.abs(Gb)**2) / 2.0)
    return float(s.real / sd), float(s.imag / sd)


def test_A7(a, data):
    fails, worst, stat = [], 0.0, {}
    for cyc in a.cycles:
        k0, k2 = ("stoch_c0", cyc), ("stoch_c2", cyc)
        if k0 not in a.coef or k2 not in a.coef:
            continue
        G0, G2 = a.G[k0], a.G[k2]
        act = (np.abs(G0) > ACTIVE * max(np.abs(G0).max(), 1e-300)) & \
              (np.abs(G2) > ACTIVE * max(np.abs(G2).max(), 1e-300))
        if neff(np.abs(G0[act]) * np.abs(G2[act])) < NEFF_MIN:
            continue
        zr, zi = indep_z(a.coef[k2][act], a.coef[k0][act], G2[act], G0[act])
        stat[str(cyc)] = (zr, zi)
        worst = max(worst, abs(zr), abs(zi))
        ok1, ok2 = dz(zr), dz(zi)
        if not (ok1 and ok2):
            fails.append(f"{cyc}: z=({zr:.1f},{zi:.1f})")
    data["A7"] = stat
    return rec("A7", "independent degrees of freedom are uncorrelated", not fails, worst,
               f"|z| <= {STATE['z']:.2f}", "; ".join(fails[:6]))


def output_pairs(cycles):
    pairs = [(cycles[i], cycles[i + 1]) for i in range(len(cycles) - 1)]
    if len(cycles) >= 3:
        pairs.append((cycles[0], cycles[2]))
    return pairs


def test_A8(a, data):
    fails, worst, stat, napp = [], 0.0, {}, 0
    for ca, cb in output_pairs(a.cycles):
        ka, kb = ("stoch_c0", ca), ("stoch_c0", cb)
        Ga, Gb = a.G[ka], a.G[kb]
        if np.abs(Ga).max() == 0 or np.abs(Gb).max() == 0:
            stat[f"{ca}-{cb}"] = "n/a"
            continue
        if a.p["scheme"] == "frozen":
            sel = (np.abs(Ga) > WHITE * np.abs(Ga).max()) & (np.abs(Gb) > WHITE * np.abs(Gb).max())
            if sel.sum() < 30:
                stat[f"{ca}-{cb}"] = "n/a"
                continue
            e = ratio_dev(a.coef[kb][sel], a.coef[ka][sel], Gb[sel] / Ga[sel],
                          a.rms_m(kb), a.rms_m(ka))
            stat[f"{ca}-{cb}"] = e
            napp += 1
            worst = max(worst, e)
            if e > a.eps_m:
                fails.append(f"{ca}-{cb} dev {e:.2e}")
        else:
            sel = (np.abs(Ga) > ACTIVE * np.abs(Ga).max()) & (np.abs(Gb) > ACTIVE * np.abs(Gb).max())
            if neff(np.abs(Ga[sel]) * np.abs(Gb[sel])) < NEFF_MIN:
                stat[f"{ca}-{cb}"] = "n/a"
                continue
            zr, zi = indep_z(a.coef[kb][sel], a.coef[ka][sel], Gb[sel], Ga[sel])
            stat[f"{ca}-{cb}"] = (zr, zi)
            napp += 1
            worst = max(worst, abs(zr), abs(zi))
            ok1, ok2 = dz(zr), dz(zi)
            if not (ok1 and ok2):
                fails.append(f"{ca}-{cb} z=({zr:.1f},{zi:.1f})")
    data["A8"] = stat
    crit = (f"frozen: deviation <= {a.eps_m:g}" if a.p["scheme"] == "frozen"
            else f"markov: |z| <= {STATE['z']:.2f}")
    passed = (not fails) if napp else None
    return rec("A8", "between outputs", passed, worst, crit,
               ("; ".join(fails[:6])) if napp else "not applicable: no common active modes")


def test_A9(a, data):
    if a.p["scheme"] != "frozen":
        return rec("A9", "integrated field", None, None, "markov: covered by A1 and A2",
                   "not applicable")
    if not any(k[0] == "stoch_acc0" for k in a.coef):
        return rec("A9", "integrated field", None, None, "needs stoch_acc0",
                   "not applicable: no integrated field in the output")
    tol = max(A9_TOL, a.eps_x)
    worst, stat = 0.0, {}
    for cyc in a.cycles:
        key = ("stoch_acc0", cyc)
        if key not in a.coef:
            continue
        fref, _ = nr.synthesise(a.lat, a.ref[key])
        e = float(np.abs(a.field(key) - fref).max() / np.sqrt(np.mean(fref**2)))
        stat[str(cyc)] = e
        worst = max(worst, e)
    data["A9"] = stat
    return rec("A9", "integrated field equals the telescoped window", worst <= tol, worst,
               f"max|a - a_ref| / rms <= {tol:g}")


def test_A10(a, data):
    mask_in = a.lat.in_set_mask()
    worst, where = 0.0, ""
    for key, Fh in a.full.items():
        G = a.G[key]
        scale = float(np.sqrt(np.mean(np.abs(G)**2)))
        out_max = float(np.abs(Fh[~mask_in]).max())
        zero_max = float(np.abs(a.coef[key][G == 0]).max()) if np.any(G == 0) else 0.0
        m = max(out_max, zero_max)
        if scale == 0.0:
            e = 0.0 if m == 0.0 else np.inf
        else:
            e = m / scale
        if e > worst:
            worst, where = e, f"{key[0]}@{key[1]}"
    data["A10"] = worst
    return rec("A10", "band limit: nothing outside the mode set or where G = 0",
               worst <= a.eps_m, worst, f"max |xi_n| / rms_G <= {a.eps_m:g}",
               f"worst {where}")


def _tests(a, data):
    return [test_A0(a), test_A1(a, data), test_A2(a, data), test_A3(a, data),
            test_A4(a, data), test_A5(a, data), test_A6(a, data), test_A7(a, data),
            test_A8(a, data), test_A9(a, data), test_A10(a, data)]


def validate_single(run, log="agm"):
    """Tests A0-A10. First pass counts the D statistical decisions; the second decides
    each at the level FW / D (Bonferroni: family-wise false alarm <= FW per validation)."""
    a = Analysed(run, log)
    set_level(P_FA)
    _tests(a, {})
    D = max(STATE["count"], 1)
    set_level(FW / D)
    data = {"decisions": D, "level": FW / D}
    res = _tests(a, data)
    set_level(P_FA)
    return res, data, a


# ------------------------------------------------------------------ comparisons
def compare_fields(ra, rb, tid, name, mode, eps=None):
    common = [(v, c) for c in ra["outputs"] if c in rb["outputs"]
              for v in ra["outputs"][c]["fields"] if v in rb["outputs"][c]["fields"]]
    if not common:
        return rec(tid, name, False, None, "common outputs", "no common outputs")
    worst, bitwise = 0.0, True
    for v, c in common:
        fa = np.asarray(ra["outputs"][c]["fields"][v])
        fb = np.asarray(rb["outputs"][c]["fields"][v])
        if fa.shape != fb.shape:
            return rec(tid, name, False, None, "same shape", f"{v}@{c} shapes differ")
        if not np.array_equal(fa.view(np.uint8), fb.view(np.uint8)):
            bitwise = False
        rms = float(np.sqrt(np.mean(fa.astype(np.float64)**2)))
        d = float(np.abs(fa.astype(np.float64) - fb).max())
        worst = max(worst, d / rms if rms > 0 else (0.0 if d == 0 else np.inf))
    if mode == "bitwise":
        passed = bitwise
        crit = "bit-identical"
        det = f"{len(common)} fields; bitwise {bitwise}; max rel diff {worst:.2e}"
        if not bitwise and worst <= 1e-13:
            det += " (within 1e-13: passes only with a stated reason)"
    else:
        passed = worst <= eps
        crit = f"max rel diff <= {eps:g}"
        det = f"{len(common)} fields; bitwise {bitwise}"
    return rec(tid, name, passed, worst, crit, det)


def compare_resolution(ra, rb, log="agm"):
    aa, ab = Analysed(ra, log), Analysed(rb, log)
    worst = 0.0
    for key in aa.coef:
        if key in ab.coef:
            d = float(np.abs(aa.coef[key] - ab.coef[key]).max())
            s = max(aa.rms_m(key), 1e-300)
            worst = max(worst, d / s)
    eps = max(aa.eps_m, ab.eps_m)
    return rec("A13", "resolution: same coefficients at N and 2N", worst <= eps, worst,
               f"max |xi_n(N) - xi_n(2N)| / rms <= {eps:g}",
               f"N = {ra['N']} and {rb['N']}")


def compare_seeds(ra, rb, log="agm"):
    aa, ab = Analysed(ra, log), Analysed(rb, log)
    worst, fails = 0.0, []
    keys = [k for k in aa.keys("stoch_c0") if k in ab.coef]
    set_level(FW / max(2 * len(keys), 1))
    for key in keys:
        if key not in ab.coef:
            continue
        G = aa.G[key]
        act = np.abs(G) > ACTIVE * max(np.abs(G).max(), 1e-300)
        if neff(np.abs(G[act])**2) < NEFF_MIN:
            continue
        zr, zi = indep_z(aa.coef[key][act], ab.coef[key][act], G[act], G[act])
        worst = max(worst, abs(zr), abs(zi))
        ok1, ok2 = dz(zr), dz(zi)
        if not (ok1 and ok2):
            fails.append(f"{key[1]}: ({zr:.1f},{zi:.1f})")
    same = ra["params"]["seed"] == rb["params"]["seed"]
    crit = f"|z| <= {STATE['z']:.2f}, seeds differ"
    set_level(P_FA)
    return rec("A15", "different seeds give independent amplitudes",
               (not fails) and not same, worst, crit,
               "; ".join(fails) + (" same seed" if same else ""))


# ------------------------------------------------------------------ figures
def plot_validation(data, a, outdir, tag):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.35, 3.2))
    # spectrum ratio per shell for c0 at each output
    cols = fs.series_colors(len(a.cycles))
    rs = [data["A2"].get(f"stoch_c0@{cyc}") for cyc in a.cycles]
    widest = max((r for r in rs if r is not None), key=lambda r: len(r["shells"]), default=None)
    if widest is not None:                       # +-1/sqrt(M) band of the widest output
        sh, M = np.array(widest["shells"]), np.array(widest["M"])
        ax[0].fill_between(sh, 1 - 1 / np.sqrt(M), 1 + 1 / np.sqrt(M), color="grey",
                           alpha=0.15, lw=0)
    for i, (cyc, r) in enumerate(zip(a.cycles, rs)):
        if r is None:
            continue
        sh, ra = np.array(r["shells"]), np.array(r["ratio"])
        ax[0].plot(sh + 0.08 * i, ra, "o", ms=3, color=cols[i], label=f"cycle {cyc}")
    ax[0].axhline(1.0, **fs.GUIDE)
    ax[0].set_xlabel(r"shell $|n|$")
    ax[0].set_ylabel(r"$\langle|\xi_n|^2/|G_n|^2\rangle_{\rm shell}$")
    ax[0].legend(loc="upper right", fontsize=7)
    ax[0].set_title("A2 spectrum, c0", fontsize=10)
    # correlation function at the second output
    cyc = a.cycles[min(2, len(a.cycles) - 1)]
    r = data["A4"].get(f"stoch_c0@{cyc}")
    if r is not None:
        lags = np.array(r["lags"])
        meas, exp, sd = np.array(r["meas"]), np.array(r["exp"]), np.array(r["sd"])
        h = a.lat.L / a.lat.N
        for j, (lab, sel) in enumerate([("x", (lags[:, 1] == 0) & (lags[:, 2] == 0)),
                                        ("diagonal", (lags[:, 0] == lags[:, 1]) &
                                         (lags[:, 1] == lags[:, 2]))]):
            d = np.linalg.norm(lags[sel], axis=1) * h
            o = np.argsort(d)
            c0 = exp[0]
            ax[1].plot(d[o], exp[sel][o] / c0, "-", color=fs.SERIES[j], label=f"expected, {lab}")
            ax[1].errorbar(d[o], meas[sel][o] / c0, yerr=sd[sel][o] / c0, fmt="o", ms=2.5,
                           color=fs.SERIES[j], lw=0.8, label=f"measured, {lab}")
        ax[1].axhline(0.0, **fs.THIN)
        ax[1].set_xlabel(r"separation $r$")
        ax[1].set_ylabel(r"$C(r)/C(0)$")
        ax[1].legend(loc="upper right", fontsize=7)
        ax[1].set_title(f"A4 correlation, c0 at cycle {cyc}", fontsize=10)
    # whitened amplitudes
    first = next((v for v in data["A3"].values() if v.get("w2") is not None), None)
    if first is not None:
        w2 = np.array(first["w2"])
        bins = np.linspace(0, 8, 41)
        ax[2].hist(w2, bins=bins, density=True, histtype="step", lw=1.5,
                   color=fs.PAL["blue"], label="measured")
        xx = np.linspace(0, 8, 200)
        ax[2].plot(xx, np.exp(-xx), **fs.GUIDE, label="Exp(1)")
        ax[2].set_yscale("log")
        ax[2].set_xlabel(r"$|\xi_n/G_n|^2$")
        ax[2].set_ylabel("density")
        ax[2].legend(loc="upper right", fontsize=7)
        ax[2].set_title(f"A3 amplitudes (M = {first['M']})", fontsize=10)
    for x in ax[1:]:
        if not x.lines and not x.patches:
            x.text(0.5, 0.5, "not applicable:\nfewer than 100 effective modes",
                   ha="center", va="center", transform=x.transAxes, fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, f"fig_val_{tag}"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    for k in ("blocks8", "blocks64", "restart", "res-lo", "res-hi", "seed2", "card"):
        ap.add_argument(f"--{k}")
    ap.add_argument("--input", help="input file of NRSFDMP1 dump runs (core's power model);"
                    " all runs given then use it, with the seed of --seed2-input for U8")
    ap.add_argument("--seed2-input")
    ap.add_argument("--res-lo-input", help="input file of U5a (its nmax2 differs from U1's)")
    ap.add_argument("--res-hi-input", help="input file of U5b")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="run")
    a_ = ap.parse_args()
    _read = aio.read_run
    aio.read_run = lambda path, inp=a_.input: _read(path, inp)
    base = aio.read_run(a_.run)
    res, data, an = validate_single(base)
    if a_.blocks8:
        res.append(compare_fields(base, aio.read_run(a_.blocks8), "A11",
                                  "MeshBlocks: 1 against 8", "bitwise"))
    if a_.blocks64:
        res.append(compare_fields(base, aio.read_run(a_.blocks64), "A11",
                                  "MeshBlocks: 1 against 64", "bitwise"))
    if a_.restart:
        ref = aio.read_run(a_.blocks8) if a_.blocks8 else base
        res.append(compare_fields(ref, aio.read_run(a_.restart), "A12", "restart",
                                  "bitwise"))
    if a_.res_lo and a_.res_hi:
        res.append(compare_resolution(aio.read_run(a_.res_lo, a_.res_lo_input or a_.input),
                                      aio.read_run(a_.res_hi, a_.res_hi_input or a_.input)))
    if a_.seed2:
        res.append(compare_seeds(base, aio.read_run(a_.seed2, a_.seed2_input or a_.input)))
    if a_.card:
        res.append(compare_fields(base, aio.read_run(a_.card), "A14", "card", "tol", 1e-12))
    os.makedirs(a_.out, exist_ok=True)
    with open(os.path.join(a_.out, "validation.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    plot_validation(data, an, a_.out, a_.tag)
    nfail = sum(1 for r in res if r["passed"] is False)
    lines = [f"{r['id']} {'PASS' if r['passed'] else ('n/a' if r['passed'] is None else 'FAIL')}"
             f" {r['name']}: {r['value']} ({r['criterion']}) {r['detail']}" for r in res]
    with open(os.path.join(a_.out, "summary.txt"), "w") as f:
        f.write("\n".join(lines) + f"\nfailed: {nfail}\n")
    print("\n".join(lines))
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
