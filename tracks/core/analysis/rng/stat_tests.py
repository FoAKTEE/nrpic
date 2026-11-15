#!/usr/bin/env python3
"""Statistical checks of the reproducible random numbers (docs/RNG.md).

Part 1 draws with the Python twin ``nrpic.rng`` (identical, key by key, to the header
used in the code): moments, chi-square of the uniform deviates, correlation along every
field of the key, between streams, between the words of a call and between kinds of
draw, the normal pair and the direction.
Part 2 reads the sums and histograms that the problem generator ``rng_test`` accumulated
inside the code (files <basename>.rng_stat.txt of a processor run and of a card run)
and turns them into the same kind of statistics.

Every test yields a p-value (two-sided for a mean or a correlation, upper tail for a
chi-square). Output: stat_tests.json, stat_tests.txt and the figures fig_rng_*.png in
the current directory.

Usage: stat_tests.py [--n 10000000] [--stat label=FILE ...]
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import rng  # noqa: E402
from nrpic import figstyle  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SEED = 20261115
CHUNK = 1 << 20
RESULTS = []


def add_z(name, value, expected, se, n, group):
    z = (value - expected) / se
    RESULTS.append({"name": name, "group": group, "kind": "z", "value": value,
                    "expected": expected, "se": se, "z": z, "n": n,
                    "p": float(2.0 * stats.norm.sf(abs(z)))})
    return z


def add_chi2(name, chi2, dof, n, group):
    RESULTS.append({"name": name, "group": group, "kind": "chi2", "chi2": float(chi2),
                    "dof": int(dof), "n": n, "p": float(stats.chi2.sf(chi2, dof))})


def add_p(name, p, n, group, extra=None):
    r = {"name": name, "group": group, "kind": "p", "n": n, "p": float(p)}
    if extra:
        r.update(extra)
    RESULTS.append(r)


def add_check(name, ok, n, group, extra):
    r = {"name": name, "group": group, "kind": "check", "n": n, "ok": bool(ok)}
    r.update(extra)
    RESULTS.append(r)


def chunks(n):
    for lo in range(0, n, CHUNK):
        yield lo, min(n, lo + CHUNK)


def draw_uniform(n, **key):
    """Uniform deviates for entity = 0 .. n-1 (or the field given as an offset)."""
    out = np.empty(n)
    base = dict(seed=SEED, stream=rng.stream(rng.STREAM_TESTS, 1), step=7, draw=0,
                entity_hi=0)
    base.update(key)
    eoff = base.pop("entity_offset", 0)
    for lo, hi in chunks(n):
        out[lo:hi] = rng.uniform(entity=np.arange(lo, hi, dtype=np.uint64)
                                 + np.uint64(eoff), **base)
    return out


def corr_z(a, b, mean_a, mean_b, var_a, var_b):
    """z-score of the covariance of two samples with known means and variances."""
    n = a.size
    cov = float(np.mean((a - mean_a) * (b - mean_b)))
    return cov, math.sqrt(var_a * var_b / n)


def chi2_counts(counts, expected, min_expected=10.0):
    """Chi-square of counts against expected counts; cells with small expectation are
    merged into one cell."""
    counts = np.asarray(counts, dtype=np.float64).ravel()
    expected = np.asarray(expected, dtype=np.float64).ravel()
    small = expected < min_expected
    if small.any():
        counts = np.concatenate([counts[~small], [counts[small].sum()]])
        expected = np.concatenate([expected[~small], [expected[small].sum()]])
    return float(np.sum((counts - expected) ** 2 / expected)), counts.size - 1


# ------------------------------------------------------------------------------------
def twin_uniform(n, fig):
    g = "twin uniform"
    u = draw_uniform(n)
    d = u - 0.5
    add_z("uniform mean", float(u.mean()), 0.5, math.sqrt(1 / 12 / n), n, g)
    add_z("uniform variance", float(np.mean(d * d)), 1 / 12, math.sqrt(1 / 180 / n), n, g)
    add_z("uniform third central moment", float(np.mean(d ** 3)), 0.0,
          math.sqrt(1 / 448 / n), n, g)
    add_z("uniform fourth central moment", float(np.mean(d ** 4)), 1 / 80,
          math.sqrt((1 / 2304 - 1 / 6400) / n), n, g)
    hist = np.bincount((u * 1024).astype(np.int64), minlength=1024)
    c2, dof = chi2_counts(hist, np.full(1024, n / 1024))
    add_chi2("uniform, 1024 bins", c2, dof, n, g)
    ks = stats.kstest(u[: min(n, 5_000_000)], "uniform")
    add_p("uniform, Kolmogorov-Smirnov", ks.pvalue, min(n, 5_000_000), g,
          {"statistic": float(ks.statistic)})
    add_check("uniform, smallest and largest value in (0,1)",
              u.min() > 0.0 and u.max() < 1.0, n, g,
              {"min": float(u.min()), "max": float(u.max())})
    # pairs of consecutive entities
    pair = np.bincount((u[:-1] * 64).astype(np.int64) * 64 + (u[1:] * 64).astype(np.int64),
                       minlength=4096)
    c2, dof = chi2_counts(pair, np.full(4096, (n - 1) / 4096))
    add_chi2("pairs of consecutive entities, 64 x 64 bins", c2, dof, n - 1, g)
    # frequency of every bit of the four words, pairs of words of one call
    nb = min(n, 4_000_000)
    ones = np.zeros((4, 64))
    w01 = np.zeros(4096)
    u4 = np.empty((nb, 4))
    for lo, hi in chunks(nb):
        w = rng.bits4(seed=SEED, stream=rng.stream(rng.STREAM_TESTS, 1),
                      entity=np.arange(lo, hi, dtype=np.uint64), step=7, draw=0)
        for b in range(64):
            ones[:, b] += ((w >> np.uint64(b)) & np.uint64(1)).sum(axis=0)
        u4[lo:hi] = rng.to_uniform(w)
    zbit = (ones - nb / 2) / math.sqrt(nb / 4)
    add_chi2("frequency of each of the 256 bits of a call", float(np.sum(zbit ** 2)),
             256, nb, g)
    for a, b in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]:
        cov, se = corr_z(u4[:, a], u4[:, b], 0.5, 0.5, 1 / 12, 1 / 12)
        add_z(f"covariance of words {a} and {b} of a call", cov, 0.0, se, nb, g)
    w01 = np.bincount((u4[:, 0] * 64).astype(np.int64) * 64
                      + (u4[:, 1] * 64).astype(np.int64), minlength=4096)
    c2, dof = chi2_counts(w01, np.full(4096, nb / 4096))
    add_chi2("pairs of words 0 and 1 of a call, 64 x 64 bins", c2, dof, nb, g)

    # correlation with the deviate of the key in which one field is larger by one
    g = "twin correlations"
    st = rng.stream(rng.STREAM_TESTS, 1)
    partners = {
        "entity": dict(entity_offset=1),
        "entity_hi": dict(entity_hi=1),
        "step": dict(step=8),
        "draw": dict(draw=1),
        "sub-stream": dict(stream=st + np.uint64(1)),
        "stream": dict(stream=rng.stream(rng.STREAM_TESTS + 1, 1)),
        "seed": dict(seed=SEED + 1),
    }
    lag_z = {}
    for name, kw in partners.items():
        v = draw_uniform(n, **kw)
        cov, se = corr_z(u, v, 0.5, 0.5, 1 / 12, 1 / 12)
        lag_z[name] = add_z(f"covariance with {name} + 1", cov, 0.0, se, n, g)
    # autocorrelation along the entity and along the step up to lag 16
    acf_e = []
    for lag in range(1, 17):
        cov = float(np.mean(d[:-lag] * d[lag:]))
        acf_e.append(cov / math.sqrt(1 / 144 / (n - lag)))
    add_chi2("autocorrelation along the entity, lags 1 to 16",
             float(np.sum(np.square(acf_e))), 16, n, g)
    ns = min(n, 4_000_000)
    us = np.empty(ns)
    for lo, hi in chunks(ns):
        us[lo:hi] = rng.uniform(seed=SEED, stream=st, entity=12345,
                                step=np.arange(lo, hi, dtype=np.uint64), draw=0)
    ds = us - 0.5
    acf_s = []
    for lag in range(1, 17):
        cov = float(np.mean(ds[:-lag] * ds[lag:]))
        acf_s.append(cov / math.sqrt(1 / 144 / (ns - lag)))
    add_chi2("autocorrelation along the step (one entity), lags 1 to 16",
             float(np.sum(np.square(acf_s))), 16, ns, g)
    # the registered streams against each other
    nst = min(n, 4_000_000)
    us = []
    for ident in (rng.STREAM_INITIAL_DATA, rng.STREAM_COLLISIONS, rng.STREAM_STOCHASTIC,
                  rng.STREAM_TESTS):
        us.append(draw_uniform(nst, stream=rng.stream(ident, 0)))
    for a in range(4):
        for b in range(a + 1, 4):
            cov, se = corr_z(us[a], us[b], 0.5, 0.5, 1 / 12, 1 / 12)
            add_z(f"covariance of streams {a + 1} and {b + 1}", cov, 0.0, se, nst, g)

    fig["uniform_hist"] = hist
    fig["lag_z"] = lag_z
    fig["acf_e"] = acf_e
    fig["acf_s"] = acf_s
    return u


def twin_normal(n, fig):
    g = "twin normal"
    z1 = np.empty(n)
    z2 = np.empty(n)
    u = np.empty(n)
    st = rng.stream(rng.STREAM_TESTS, 2)
    for lo, hi in chunks(n):
        e = np.arange(lo, hi, dtype=np.uint64)
        z1[lo:hi], z2[lo:hi] = rng.normal2(seed=SEED, stream=st, entity=e, step=7, draw=0)
        u[lo:hi] = rng.uniform(seed=SEED, stream=st, entity=e, step=7, draw=0)
    dfact = [1, 1, 3, 15, 105, 945, 10395, 135135, 2027025]     # (2k-1)!!
    for m, z in ((1, z1), (2, z2)):
        for k in range(1, 9):
            ex = 0.0 if k % 2 else float(dfact[k // 2])
            se = math.sqrt((dfact[k] - ex * ex) / n)
            add_z(f"normal {m}, moment {k}", float(np.mean(z ** k)), ex, se, n, g)
        ks = stats.kstest(z[: min(n, 5_000_000)], "norm")
        add_p(f"normal {m}, Kolmogorov-Smirnov", ks.pvalue, min(n, 5_000_000), g,
              {"statistic": float(ks.statistic)})
        cnt = np.bincount(np.minimum((stats.norm.cdf(z) * 256).astype(np.int64), 255),
                          minlength=256)
        c2, dof = chi2_counts(cnt, np.full(256, n / 256))
        add_chi2(f"normal {m}, 256 bins of equal probability", c2, dof, n, g)
        for thr in (3.0, 4.0, 5.0):
            k = int(np.count_nonzero(np.abs(z) > thr))
            mu = n * 2.0 * stats.norm.sf(thr)
            p = min(1.0, 2.0 * min(stats.poisson.cdf(k, mu), stats.poisson.sf(k - 1, mu)))
            add_p(f"normal {m}, number beyond {thr:.0f}", p, n, g,
                  {"count": k, "expected": mu})
    cov, se = corr_z(z1, z2, 0.0, 0.0, 1.0, 1.0)
    add_z("covariance of the two members of a pair", cov, 0.0, se, n, g)
    cov, se = corr_z(z1 * z1, z2 * z2, 1.0, 1.0, 2.0, 2.0)
    add_z("covariance of the squares of the two members", cov, 0.0, se, n, g)
    cov, se = corr_z(z1, u, 0.0, 0.5, 1.0, 1 / 12)
    add_z("covariance of a normal and the uniform of the same draw index", cov, 0.0,
          se, n, g)
    # the angle of the pair is uniform
    phi = np.arctan2(z2, z1)
    cnt = np.bincount(np.minimum(((phi / (2 * np.pi) + 0.5) * 256).astype(np.int64), 255),
                      minlength=256)
    c2, dof = chi2_counts(cnt, np.full(256, n / 256))
    add_chi2("angle of the normal pair, 256 bins", c2, dof, n, g)
    # as used in the code: tags times steps
    ntag, nstep = 4096, max(8, min(1024, n // 4096))
    tags = np.arange(ntag, dtype=np.uint64)[:, None]
    steps = np.arange(nstep, dtype=np.uint64)[None, :]
    zz = rng.normal(seed=SEED, stream=rng.stream(rng.STREAM_TESTS, 16), entity=tags,
                    step=steps, draw=0)
    add_chi2("means over the steps of each tag", float(np.sum(zz.mean(axis=1) ** 2)
                                                         * nstep), ntag, zz.size, g)
    add_chi2("means over the tags of each step", float(np.sum(zz.mean(axis=0) ** 2)
                                                        * ntag), nstep, zz.size, g)
    cov = float(np.mean(zz[:, :-1] * zz[:, 1:]))
    add_z("covariance of consecutive steps of a tag", cov, 0.0,
          1.0 / math.sqrt(zz[:, 1:].size), zz[:, 1:].size, g)
    cov = float(np.mean(zz[:-1, :] * zz[1:, :]))
    add_z("covariance of consecutive tags of a step", cov, 0.0,
          1.0 / math.sqrt(zz[1:, :].size), zz[1:, :].size, g)
    fig["normal_hist"] = np.histogram(np.concatenate([z1, z2]),
                                      bins=np.linspace(-8, 8, 257))[0]
    fig["normal_n"] = 2 * n


def twin_direction(n, fig):
    g = "twin direction"
    d = np.empty((n, 3))
    st = rng.stream(rng.STREAM_TESTS, 3)
    for lo, hi in chunks(n):
        d[lo:hi] = rng.direction(seed=SEED, stream=st,
                                 entity=np.arange(lo, hi, dtype=np.uint64), step=7, draw=0)
    names = "xyz"
    for a in range(3):
        add_z(f"direction, mean of n_{names[a]}", float(d[:, a].mean()), 0.0,
              math.sqrt(1 / 3 / n), n, g)
        add_z(f"direction, mean of n_{names[a]}^2", float(np.mean(d[:, a] ** 2)), 1 / 3,
              math.sqrt(4 / 45 / n), n, g)
    for a, b in [(0, 1), (0, 2), (1, 2)]:
        add_z(f"direction, mean of n_{names[a]} n_{names[b]}",
              float(np.mean(d[:, a] * d[:, b])), 0.0, math.sqrt(1 / 15 / n), n, g)
    add_z("direction, mean of n_z^4", float(np.mean(d[:, 2] ** 4)), 1 / 5,
          math.sqrt((1 / 9 - 1 / 25) / n), n, g)
    hz = np.bincount(np.minimum(((d[:, 2] + 1.0) * 128).astype(np.int64), 255),
                     minlength=256)
    c2, dof = chi2_counts(hz, np.full(256, n / 256))
    add_chi2("direction, n_z in 256 bins", c2, dof, n, g)
    phi = np.arctan2(d[:, 1], d[:, 0])
    bp = np.minimum(((phi / (2 * np.pi) + 0.5) * 256).astype(np.int64), 255)
    hp = np.bincount(bp, minlength=256)
    c2, dof = chi2_counts(hp, np.full(256, n / 256))
    add_chi2("direction, azimuth in 256 bins", c2, dof, n, g)
    joint = np.bincount(np.minimum(((d[:, 2] + 1.0) * 16).astype(np.int64), 31) * 32
                        + bp // 8, minlength=1024)
    c2, dof = chi2_counts(joint, np.full(1024, n / 1024))
    add_chi2("direction, n_z and azimuth in 32 x 32 bins", c2, dof, n, g)
    dev = float(np.abs(np.sum(d * d, axis=1) - 1.0).max())
    add_check("direction, largest deviation of |n|^2 from 1 below 1e-15",
              dev < 1.0e-15, n, g, {"max_deviation": dev})
    fig["dir_hz"] = hz
    fig["dir_hp"] = hp
    fig["dir_n"] = n


def twin_index(n, fig):
    g = "twin index"
    st = rng.stream(rng.STREAM_TESTS, 5)
    for m in (7, 1000):
        cnt = np.zeros(m)
        for lo, hi in chunks(n):
            k = rng.index(seed=SEED, stream=st, entity=np.arange(lo, hi, dtype=np.uint64),
                          step=7, draw=0, n=m)
            cnt += np.bincount(k.astype(np.int64), minlength=m)
        c2, dof = chi2_counts(cnt, np.full(m, n / m))
        add_chi2(f"index in [0, {m})", c2, dof, n, g)


# ------------------------------------------------------------------------------------
def read_stat(path):
    out = {}
    with open(path) as fp:
        for line in fp:
            if line.startswith("#"):
                continue
            f = line.split()
            if f[0].startswith("hist_"):
                out[f[0]] = np.array(f[1:], dtype=np.int64)
            else:
                out[f[0]] = float(f[1])
    return out


def device_stats(label, path, fig):
    s = read_stat(path)
    n = int(s["nstat"])
    g = f"code ({label}) uniform"
    add_z("uniform mean", 0.5 + s["u_m1"] / n, 0.5, math.sqrt(1 / 12 / n), n, g)
    add_z("uniform variance", s["u_m2"] / n, 1 / 12, math.sqrt(1 / 180 / n), n, g)
    add_z("uniform third central moment", s["u_m3"] / n, 0.0, math.sqrt(1 / 448 / n),
          n, g)
    add_z("uniform fourth central moment", s["u_m4"] / n, 1 / 80,
          math.sqrt((1 / 2304 - 1 / 6400) / n), n, g)
    c2, dof = chi2_counts(s["hist_u"], np.full(1024, n / 1024))
    add_chi2("uniform, 1024 bins", c2, dof, n, g)
    g = f"code ({label}) correlations"
    lag_z = {}
    for key, name in [("u_lag_entity", "entity"), ("u_lag_entity_hi", "entity_hi"),
                      ("u_lag_step", "step"), ("u_lag_draw", "draw"),
                      ("u_lag_substream", "sub-stream"), ("u_lag_stream", "stream"),
                      ("u_lag_seed", "seed")]:
        lag_z[name] = add_z(f"covariance with {name} + 1", s[key] / n, 0.0,
                            math.sqrt(1 / 144 / n), n, g)
    for k in (1, 2, 3):
        add_z(f"covariance of words 0 and {k} of a call", s[f"u_word0{k}"] / n, 0.0,
              math.sqrt(1 / 144 / n), n, g)
    add_z("covariance of uniform and normal of the same draw index", s["u_normal"] / n,
          0.0, math.sqrt(1 / 12 / n), n, g)
    add_z("covariance of uniform and n_z of the same draw index", s["u_dirz"] / n, 0.0,
          math.sqrt(1 / 36 / n), n, g)
    add_z("covariance of normal and n_z of the same draw index", s["normal_dirz"] / n,
          0.0, math.sqrt(1 / 3 / n), n, g)
    g = f"code ({label}) normal"
    dfact = [1, 1, 3, 15, 105, 945, 10395, 135135, 2027025]
    edges = np.linspace(-8, 8, 257)
    pexp = np.diff(stats.norm.cdf(edges))
    pexp[0] += stats.norm.cdf(-8.0)
    pexp[-1] += stats.norm.sf(8.0)
    for m in (1, 2):
        for k in range(1, 9):
            ex = 0.0 if k % 2 else float(dfact[k // 2])
            add_z(f"normal {m}, moment {k}", s[f"z{m}_m{k}"] / n, ex,
                  math.sqrt((dfact[k] - ex * ex) / n), n, g)
        for thr in (3, 4, 5, 6):
            k = int(round(s[f"z{m}_gt{thr}"]))
            mu = n * 2.0 * stats.norm.sf(thr)
            p = min(1.0, 2.0 * min(stats.poisson.cdf(k, mu), stats.poisson.sf(k - 1, mu)))
            add_p(f"normal {m}, number beyond {thr}", p, n, g,
                  {"count": k, "expected": mu})
        c2, dof = chi2_counts(s[f"hist_z{m}"], n * pexp)
        add_chi2(f"normal {m}, bins of width 1/16", c2, dof, n, g)
    add_z("covariance of the two members of a pair", s["z_z1z2"] / n, 0.0,
          math.sqrt(1 / n), n, g)
    add_z("covariance of the squares of the two members", s["z_z1sqz2sq"] / n - 1.0,
          0.0, math.sqrt(8 / n), n, g)
    g = f"code ({label}) direction"
    for a, c in enumerate("xyz"):
        add_z(f"direction, mean of n_{c}", s[f"d_{c}"] / n, 0.0, math.sqrt(1 / 3 / n),
              n, g)
        add_z(f"direction, mean of n_{c}^2", s[f"d_{c}{c}"] / n, 1 / 3,
              math.sqrt(4 / 45 / n), n, g)
    for c in ("xy", "xz", "yz"):
        add_z(f"direction, mean of n_{c[0]} n_{c[1]}", s[f"d_{c}"] / n, 0.0,
              math.sqrt(1 / 15 / n), n, g)
    add_z("direction, mean of n_z^4", s["d_zzzz"] / n, 1 / 5,
          math.sqrt((1 / 9 - 1 / 25) / n), n, g)
    c2, dof = chi2_counts(s["hist_dz"], np.full(256, n / 256))
    add_chi2("direction, n_z in 256 bins", c2, dof, n, g)
    c2, dof = chi2_counts(s["hist_dphi"], np.full(256, n / 256))
    add_chi2("direction, azimuth in 256 bins", c2, dof, n, g)
    add_check("direction, largest deviation of |n|^2 from 1 below 1e-15",
              s["d_norm_dev_max"] < 1.0e-15, n, g,
              {"max_deviation": s["d_norm_dev_max"]})
    add_check("normal, largest modulus below 8.5", s["z_max"] < 8.5, n,
              f"code ({label}) normal",
              {"z_max": s["z_max"]})
    fig.setdefault("device", {})[label] = {
        "n": n, "hist_u": s["hist_u"], "hist_z": s["hist_z1"] + s["hist_z2"],
        "hist_dz": s["hist_dz"], "hist_dphi": s["hist_dphi"], "lag_z": lag_z,
        "z_max": s["z_max"]}


# ------------------------------------------------------------------------------------
def figures(fig, n):
    figstyle.use_style()
    pal = figstyle.PAL
    dev = fig.get("device", {})
    cols = {"twin": pal["blue"]}
    for lab, c in zip(dev, [pal["red"], pal["green"], pal["orange"]]):
        cols[lab] = c

    # uniform: residuals of the 1024 bins and the correlations
    f, ax = plt.subplots(2, 1, figsize=(8.0, 6.0))
    f.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.97, hspace=0.25)
    x = (np.arange(1024) + 0.5) / 1024
    res = (fig["uniform_hist"] - n / 1024) / math.sqrt(n / 1024)
    ax[0].plot(x, res, lw=0.6, color=cols["twin"], label=f"Python twin, N = {n:.0e}")
    for lab, dd in dev.items():
        r = (dd["hist_u"] - dd["n"] / 1024) / math.sqrt(dd["n"] / 1024)
        ax[0].plot(x, r, lw=0.6, color=cols[lab], alpha=0.8,
                   label=f"code, {lab}, N = {dd['n']:.0e}")
    for y in (-3, 3):
        ax[0].axhline(y, **figstyle.GUIDE)
    ax[0].set_xlim(0, 1)
    ax[0].set_ylim(-5.5, 8.5)
    ax[0].set_xlabel("uniform deviate $u$")
    ax[0].set_ylabel("bin count, deviation / $\\sigma$")
    ax[0].legend(ncol=2, loc="upper center")
    names = list(fig["lag_z"].keys())
    xx = np.arange(len(names))
    wdt = 0.8 / (1 + len(dev))
    ax[1].bar(xx - 0.4 + wdt / 2, [fig["lag_z"][k] for k in names], wdt,
              color=cols["twin"], label="Python twin")
    for i, (lab, dd) in enumerate(dev.items()):
        ax[1].bar(xx - 0.4 + wdt * (i + 1.5), [dd["lag_z"][k] for k in names], wdt,
                  color=cols[lab], label=f"code, {lab}")
    for y in (-3, 3):
        ax[1].axhline(y, **figstyle.GUIDE)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xticks(xx)
    ax[1].set_xticklabels(names)
    ax[1].tick_params(axis="x", which="minor", bottom=False, top=False)
    ax[1].set_ylim(-5.5, 8.5)
    ax[1].set_ylabel("covariance of $u$ with partner / $\\sigma$")
    ax[1].set_xlabel("field of the key that is larger by one in the partner")
    ax[1].legend(ncol=2, loc="upper center")
    f.savefig("fig_rng_uniform.png", dpi=200)
    plt.close(f)

    # normal: density on a logarithmic scale and residuals
    f, ax = plt.subplots(2, 1, figsize=(8.0, 6.0), sharex=True,
                         gridspec_kw={"height_ratios": [2, 1]})
    f.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, hspace=0.05)
    edges = np.linspace(-8, 8, 257)
    xc = 0.5 * (edges[1:] + edges[:-1])
    pexp = np.diff(stats.norm.cdf(edges))
    series = [("Python twin", fig["normal_hist"], fig["normal_n"], cols["twin"])]
    for lab, dd in dev.items():
        series.append((f"code, {lab}", dd["hist_z"], 2 * dd["n"], cols[lab]))
    ax[0].plot(xc, pexp * 16, label="normal density", **figstyle.GUIDE)
    for lab, h, nn, c in series:
        ok = h > 0
        ax[0].plot(xc[ok], h[ok] / nn * 16, ".", ms=3, color=c,
                   label=f"{lab}, N = {nn:.0e}")
        ex = nn * pexp
        big = ex > 25
        ax[1].plot(xc[big], (h[big] - ex[big]) / np.sqrt(ex[big]), lw=0.7, color=c)
    ax[0].set_yscale("log")
    ax[0].set_ylim(1e-12, 2)
    ax[0].set_ylabel("probability density")
    ax[0].legend(loc="lower center")
    for y in (-3, 3):
        ax[1].axhline(y, **figstyle.GUIDE)
    ax[1].set_ylim(-5.5, 5.5)
    ax[1].set_xlim(-8, 8)
    ax[1].set_xlabel("normal deviate $z$")
    ax[1].set_ylabel("deviation / $\\sigma$")
    f.savefig("fig_rng_normal.png", dpi=200)
    plt.close(f)

    # direction: n_z and azimuth
    f, ax = plt.subplots(2, 1, figsize=(8.0, 5.0))
    f.subplots_adjust(left=0.09, right=0.98, bottom=0.12, top=0.97, hspace=0.38)
    xz = (np.arange(256) + 0.5) / 128 - 1
    xp = ((np.arange(256) + 0.5) / 256 - 0.5) * 2 * np.pi
    nn = fig["dir_n"]
    ax[0].plot(xz, (fig["dir_hz"] - nn / 256) / math.sqrt(nn / 256), lw=0.7,
               color=cols["twin"], label=f"Python twin, N = {nn:.0e}")
    ax[1].plot(xp, (fig["dir_hp"] - nn / 256) / math.sqrt(nn / 256), lw=0.7,
               color=cols["twin"])
    for lab, dd in dev.items():
        ax[0].plot(xz, (dd["hist_dz"] - dd["n"] / 256) / math.sqrt(dd["n"] / 256), lw=0.7,
                   color=cols[lab], label=f"code, {lab}, N = {dd['n']:.0e}")
        ax[1].plot(xp, (dd["hist_dphi"] - dd["n"] / 256) / math.sqrt(dd["n"] / 256),
                   lw=0.7, color=cols[lab])
    for a in ax:
        for y in (-3, 3):
            a.axhline(y, **figstyle.GUIDE)
        a.set_ylim(-5.5, 5.5)
        a.set_ylabel("deviation / $\\sigma$")
    ax[0].set_ylim(-5.5, 9.5)
    ax[0].set_xlim(-1, 1)
    ax[1].set_xlim(-np.pi, np.pi)
    ax[0].set_xlabel("$n_z$")
    ax[1].set_xlabel("azimuth of $(n_x, n_y)$")
    ax[0].legend(ncol=2, loc="upper center")
    f.savefig("fig_rng_direction.png", dpi=200)
    plt.close(f)

    # all p-values against the uniform expectation
    f, ax = plt.subplots(1, 2, figsize=(8.0, 3.6))
    f.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    groups = {}
    for r in RESULTS:
        if r["kind"] == "check":
            continue
        key = "Python twin" if r["group"].startswith("twin") else \
            "code, " + r["group"].split("(")[1].split(")")[0]
        groups.setdefault(key, []).append(r["p"])
    for (lab, ps), c in zip(groups.items(), [pal["blue"], pal["red"], pal["green"],
                                             pal["orange"]]):
        ps = np.sort(ps)
        q = (np.arange(ps.size) + 0.5) / ps.size
        ax[0].plot(q, ps, ".", ms=4, color=c)
        ax[1].plot(q, ps, ".", ms=4, color=c, label=f"{lab} ({ps.size} tests)")
    for a in ax:
        a.plot([1e-6, 1], [1e-6, 1], **figstyle.GUIDE)
        a.set_xlabel("expected quantile")
        a.set_ylabel("p-value")
    ax[0].set_xlim(0, 1)
    ax[0].set_ylim(0, 1)
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlim(1e-3, 1)
    ax[1].set_ylim(1e-6, 1)
    ax[1].legend(loc="lower right")
    f.savefig("fig_rng_pvalues.png", dpi=200)
    plt.close(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10_000_000)
    ap.add_argument("--stat", action="append", default=[])
    args = ap.parse_args()
    fig = {}
    twin_uniform(args.n, fig)
    twin_normal(args.n, fig)
    twin_direction(args.n, fig)
    twin_index(args.n, fig)
    for item in args.stat:
        label, path = item.split("=", 1)
        device_stats(label, path, fig)
    figures(fig, args.n)

    pv = np.array([r["p"] for r in RESULTS if r["kind"] != "check"])
    checks = [r for r in RESULTS if r["kind"] == "check"]
    zs = np.array([abs(r["z"]) for r in RESULTS if r["kind"] == "z"])
    summary = {
        "n_twin": args.n,
        "tests_with_p_value": int(pv.size),
        "smallest_p": float(pv.min()),
        "smallest_p_test": [r["group"] + ": " + r["name"] for r in RESULTS
                            if r.get("p") == pv.min()][0],
        "p_below_1e-2": int(np.count_nonzero(pv < 1e-2)),
        "p_below_1e-3": int(np.count_nonzero(pv < 1e-3)),
        "p_below_1e-4": int(np.count_nonzero(pv < 1e-4)),
        "largest_abs_z": float(zs.max()),
        "ks_of_p_values": float(stats.kstest(pv, "uniform").pvalue),
        "pass_fail_checks": len(checks),
        "pass_fail_failed": [r["group"] + ": " + r["name"] for r in checks
                             if not r["ok"]],
    }
    summary["ok"] = bool(summary["smallest_p"] >= 1e-6 and summary["largest_abs_z"] < 5.0
                         and not summary["pass_fail_failed"]
                         and summary["ks_of_p_values"] >= 1e-3)
    with open("stat_tests.json", "w") as fp:
        json.dump({"summary": summary, "results": RESULTS}, fp, indent=1)
    with open("stat_tests.txt", "w") as fp:
        for r in RESULTS:
            if r["kind"] == "z":
                det = f"value {r['value']:.9g} expected {r['expected']:.9g} z {r['z']:+.2f}"
            elif r["kind"] == "chi2":
                det = f"chi2 {r['chi2']:.1f} dof {r['dof']}"
            else:
                det = " ".join(f"{k} {v}" for k, v in r.items()
                               if k not in ("name", "group", "kind", "n", "p", "ok"))
            last = f"p {r['p']:.4g}" if "p" in r else ("ok" if r["ok"] else "FAILED")
            fp.write(f"{r['group']:28s} | {r['name']:62s} | N {r['n']:.3g} | {det} | "
                     f"{last}\n")
    print(json.dumps(summary, indent=1))
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
