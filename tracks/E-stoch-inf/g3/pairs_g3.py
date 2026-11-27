#!/usr/bin/env python3
"""Pair statistics of the G3 baseline against the one-patch reference of the 128 band (SCOPE 4d with 4d.9;
g3/JOURNAL.md entries 4 and 15).

    pairs_g3.py OUT --read <reading run dir> [--read ...] --ref <direct run dir> [--ref ...] --tilt <tilt json>
                [--pairs 0-70]

Inputs: the per-member files of read_pilot.py (<label>.json, <label>_hist.npz, and with --save-fields
<label>_zeta.npy, <label>_R.npy); the pilot's b00i are the + members p00i of pairs 0-9. The reference: the
samples of the lattice variant (s0.01_lattice, column 1 = N at N_e) of each direct run, and the importance-
sampled tail (own-sigma values) of the tilted run.
Estimator (A5): the pair is the unit; per pair the mean of its two members' fractions and moments; mean and
standard error (sd / sqrt(n_pairs)) over the pairs. A(nu) from the pair means of F_pm, error by jackknife over
pairs. Reference: batch means over blocks of 1e5 samples (each block standardised by its own sd, as each box
is), pooled over the direct runs; nu = 4 from the sampler.
Judged (A2): (V) var_NR/var_ref - 1; (T) skewness, excess kurtosis, F_pm(3), F_pm(4) at the own sd, A(3), A(4),
each with the number of combined standard errors. Reported: r(nu) at fixed nu sigma_lin; the even part of A5
(a_zeta, a_R regressed per pair from the two members' fields; F_+(+) - F_-(-)); the mirroring gain (P15-3).
Writes OUT/pairs.json, OUT/fig_g3_onepoint.{png,pdf}, OUT/fig_g3_tails.{png,pdf}, OUT/fig_g3_pairs.{png,pdf}.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(TRK, "repro", "figs", "figures"))
import figstyle as fs  # noqa: E402

Q3, Q4 = float(norm.sf(3.0)), float(norm.sf(4.0))
VAR_LAT_NE_KEY = ("linear", "var_lattice_Ne")
BLOCK = 100000
SPOT_BAR = 1e-8                      # g3/JOURNAL.md entry 12 (ii)


def parse_pairs(s):
    a, b = s.split("-")
    return list(range(int(a), int(b) + 1))


def load_members(dirs):
    mem = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            name = os.path.basename(f)[:-5]
            if name in ("pilot",) or not (name[0] in "pmb" and name[1:].isdigit()):
                continue
            r = json.load(open(f))
            lab = "p" + name[1:] if name[0] == "b" else name
            r["_dir"], r["_file"] = d, name
            mem[lab] = r
    return mem


def usable(r):
    h = r["health"]
    why = []
    if not h["finite"]:
        why.append("non-finite record")
    if r["n_cells_rolling_back"] > 0:
        why.append("v <= 0")
    if r["table"]["spot_max_abs"] > SPOT_BAR:
        why.append("spot check above 1e-8")
    if h["max_Hp"] >= 1e-9 or h["max_M"] >= 0.1:
        why.append("constraint record above the bar")
    if abs(h["t_last"] - r["time"]) > 1e-6 * r["time"]:
        why.append("did not reach tlim")
    return why


def moments(x):
    c = x - x.mean()
    v = float(np.mean(c ** 2))
    return v, float(np.mean(c ** 3) / v ** 1.5), float(np.mean(c ** 4) / v ** 2 - 3.0)


def reference(ref_dirs, tilt, var_lat):
    stats = []
    pooled = []
    for d in ref_dirs:
        x = np.load(os.path.join(d, "ref_inflection_samples.npz"))["s0.01_lattice"][:, 1]
        x = x[np.isfinite(x)]
        pooled.append(x - x.mean())
        nb = x.size // BLOCK
        for b in range(nb):
            y = x[b * BLOCK:(b + 1) * BLOCK]
            v, sk, ku = moments(y)
            s = np.sqrt(v)
            c = y - y.mean()
            row = dict(var=v, skew=sk, exkurt=ku)
            for nu in (3.0, 4.0):
                row[f"Fp{nu:g}"] = float(np.mean(c > nu * s))
                row[f"Fm{nu:g}"] = float(np.mean(c < -nu * s))
                row[f"Lp{nu:g}"] = float(np.mean(c > nu * np.sqrt(var_lat)))
                row[f"Lm{nu:g}"] = float(np.mean(c < -nu * np.sqrt(var_lat)))
            stats.append(row)
    keys = stats[0].keys()
    out = {k: (float(np.mean([r[k] for r in stats])),
               float(np.std([r[k] for r in stats], ddof=1) / np.sqrt(len(stats)))) for k in keys}
    out["n_blocks"] = len(stats)
    out["n_samples"] = int(len(stats) * BLOCK)
    out["var_over_lattice"] = (out["var"][0] / var_lat, out["var"][1] / var_lat)
    fp, fm = np.array([r["Fp3"] for r in stats]), np.array([r["Fm3"] for r in stats])
    out["A3"] = jack_A(fp, fm)
    T = json.load(open(tilt))
    for side, key in (("+", "Fp4_is"), ("-", "Fm4_is")):
        e = T["sides"][side]["own"]["4.0"]
        out[key] = (float(e["F"]), float(e["se"]))
        e = T["sides"][side]["latsig"]["4.0"]
        out[key.replace("F", "L")] = (float(e["F"]), float(e["se"]))
    a, b = out["Fp4_is"], out["Fm4_is"]
    A = (a[0] - b[0]) / (a[0] + b[0])
    dA = 2.0 / (a[0] + b[0]) ** 2 * np.hypot(b[0] * a[1], a[0] * b[1])
    out["A4_is"] = (float(A), float(dA))
    allx = np.concatenate(pooled)
    sd = allx.std()
    edges = np.linspace(-8.0, 8.0, 161)
    out["_hist"] = np.histogram(allx / sd, bins=edges)[0]
    out["_tail_nu"] = np.linspace(0.0, 5.5, 56)
    out["_tail_p"] = np.array([np.mean(allx > t * sd) for t in out["_tail_nu"]])
    out["_tail_m"] = np.array([np.mean(allx < -t * sd) for t in out["_tail_nu"]])
    out["_tilt"] = T
    return out


def jack_A(fp, fm):
    n = len(fp)
    A = (fp.mean() - fm.mean()) / (fp.mean() + fm.mean())
    sp, sm = fp.sum(), fm.sum()
    Aj = np.array([((sp - fp[i]) - (sm - fm[i])) / ((sp - fp[i]) + (sm - fm[i])) for i in range(n)])
    return float(A), float(np.sqrt((n - 1) / n * np.sum((Aj - Aj.mean()) ** 2)))


def even_part(rp, rm):
    out = {}
    for tag in ("zeta", "R"):
        a = np.load(os.path.join(rp["_dir"], f"{rp['_file']}_{tag}.npy")).astype(np.float64).ravel()
        b = np.load(os.path.join(rm["_dir"], f"{rm['_file']}_{tag}.npy")).astype(np.float64).ravel()
        O = 0.5 * (a - b)
        E = 0.5 * (a + b)
        E -= E.mean()
        O2 = O * O - np.mean(O * O)
        out[f"a_{tag}"] = float(np.sum(E * O2) / np.sum(O2 * O2))
        out[f"rmsE_{tag}"] = float(np.sqrt(np.mean(E * E)))
        out[f"rmsO_{tag}"] = float(np.sqrt(np.mean(O * O)))
        out[f"corr_{tag}"] = float(np.corrcoef(E, O2)[0, 1])
    return out


def ms(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(v.size)), float(v.std(ddof=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--read", action="append", required=True)
    ap.add_argument("--ref", action="append", required=True)
    ap.add_argument("--tilt", required=True)
    ap.add_argument("--pairs", default="0-70")
    ap.add_argument("--no-fields", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mem = load_members(a.read)
    first = json.load(open(glob.glob(os.path.join(a.ref[0], "*.json"))[0]))
    var_lat = float(first["linear"]["var_lattice_Ne"])
    pairs, dropped = [], {}
    for i in parse_pairs(a.pairs):
        p, m = mem.get(f"p{i:03d}"), mem.get(f"m{i:03d}")
        if p is None or m is None:
            dropped[i] = "member missing"
            continue
        why = usable(p) + usable(m)
        if why:
            dropped[i] = "; ".join(why)
            continue
        pairs.append((i, p, m))
    n = len(pairs)
    res = dict(n_pairs=n, pairs=[i for i, _, _ in pairs], dropped=dropped, n_members_read=len(mem),
               sigma_lin=sorted(set(round(r["sigma_lin"], 12) for _, p, m in pairs for r in (p, m))))
    # per pair: means of the two members
    keys = ["zeta_skew", "zeta_exkurt", "zeta_Fp3", "zeta_Fm3", "zeta_Fp4", "zeta_Fm4",
            "zetalin_Fp3", "zetalin_Fm3", "zetalin_Fp4", "zetalin_Fm4",
            "R_skew", "R_exkurt", "R_Fp3", "R_Fm3", "R_Fp4", "R_Fm4"]
    P = {k: np.array([0.5 * (p[k] + m[k]) for _, p, m in pairs]) for k in keys}
    P["var"] = np.array([0.5 * ((p["zeta_ratio"] * p["sigma_lin"]) ** 2 + (m["zeta_ratio"] * m["sigma_lin"]) ** 2)
                         for _, p, m in pairs])
    P["varR"] = np.array([0.5 * ((p["R_ratio"] * p["sigma_lin"]) ** 2 + (m["R_ratio"] * m["sigma_lin"]) ** 2)
                          for _, p, m in pairs])
    nr = {k: ms(v) for k, v in P.items()}
    nr["A3"] = jack_A(P["zeta_Fp3"], P["zeta_Fm3"])
    nr["A4"] = jack_A(P["zeta_Fp4"], P["zeta_Fm4"])
    nr["R_A3"] = jack_A(P["R_Fp3"], P["R_Fm3"])
    members = [r for _, p, m in pairs for r in (p, m)]
    nr["member_skew"] = ms([r["zeta_skew"] for r in members])
    res["nr"] = nr
    ref = reference(a.ref, a.tilt, var_lat)
    res["ref"] = {k: v for k, v in ref.items() if not k.startswith("_")}
    res["var_lattice_Ne"] = var_lat

    def comp(x, dx, y, dy):
        c = float(np.hypot(dx, dy))
        return dict(nr=x, nr_se=dx, ref=y, ref_se=dy, diff=x - y, comb_se=c, n_se=(x - y) / c if c > 0 else None)

    V = nr["var"]
    vr, dvr = V[0] / ref["var"][0], V[0] / ref["var"][0] * np.hypot(V[1] / V[0], ref["var"][1] / ref["var"][0])
    res["V"] = dict(ratio_minus_1=float(vr - 1), se=float(dvr), n_se=float((vr - 1) / dvr),
                    nr_var_over_lattice=float(V[0] / var_lat), nr_var_over_lattice_se=float(V[1] / var_lat),
                    ref_var_over_lattice=ref["var_over_lattice"],
                    holds_bar_0p01=bool(abs(vr - 1) < 0.01), holds_3se=bool(abs(vr - 1) < 3 * dvr))
    T = {}
    T["skew"] = comp(*nr["zeta_skew"][:2], *ref["skew"])
    T["exkurt"] = comp(*nr["zeta_exkurt"][:2], *ref["exkurt"])
    for nu, side, kref in ((3, "p", "Fp3"), (3, "m", "Fm3"), (4, "p", "Fp4_is"), (4, "m", "Fm4_is")):
        k = f"zeta_F{side}{nu}"
        x, dx, _ = nr[k]
        y, dy = ref[kref]
        c = comp(x, dx, y, dy)
        c.update(r=x / y - 1, r_se=(x / y) * np.hypot(dx / x, dy / y) if x > 0 else None, nr_Q=x / (Q3 if nu == 3 else Q4),
                 ref_Q=y / (Q3 if nu == 3 else Q4))
        T[f"F{side}{nu}"] = c
    T["A3"] = comp(*nr["A3"], *ref["A3"])
    T["A4"] = comp(*nr["A4"], *ref["A4_is"])
    for k in T:
        T[k]["differs"] = bool(T[k]["n_se"] is not None and abs(T[k]["n_se"]) > 3.0)
    res["T"] = T
    # r(nu) at fixed nu sigma_lin (reported, not judged)
    rl = {}
    for nu, side, kref in ((3, "p", "Lp3"), (3, "m", "Lm3"), (4, "p", "Lp4_is"), (4, "m", "Lm4_is")):
        x, dx, _ = nr[f"zetalin_F{side}{nu}"]
        y, dy = ref[kref]
        rl[f"{side}{nu}"] = dict(r=x / y - 1, se=(x / y) * np.hypot(dx / x, dy / y))
    res["r_fixed_sigma_lin"] = rl
    # entry 4 bands
    res["bands_entry4"] = dict(
        skew_in_0p015_0p032=bool(0.015 <= nr["zeta_skew"][0] <= 0.032),
        A3_in_0p05_0p16=bool(0.05 <= nr["A3"][0] <= 0.16),
        Fp4Q_in_1p1_1p8=bool(1.1 <= nr["zeta_Fp4"][0] / Q4 <= 1.8),
        Fm4Q_in_0p5_1p0=bool(0.5 <= nr["zeta_Fm4"][0] / Q4 <= 1.0),
        R_skew_in_0_0p002=bool(0.0 <= nr["R_skew"][0] <= 0.002),
        R_Fp4Q_in_0p85_1p2=bool(0.85 <= nr["R_Fp4"][0] / Q4 <= 1.2),
        R_Fm4Q_in_0p85_1p2=bool(0.85 <= nr["R_Fm4"][0] / Q4 <= 1.2))
    # A5 even part and mirroring
    res["mirror"] = dict(member_skew_se=nr["member_skew"][1], pair_skew_se=nr["zeta_skew"][1],
                         gain=nr["member_skew"][1] / nr["zeta_skew"][1])
    fpm = np.array([(p["zeta_Fp3"] - m["zeta_Fm3"]) / Q3 for _, p, m in pairs])
    fpm4 = np.array([(p["zeta_Fp4"] - m["zeta_Fm4"]) / Q4 for _, p, m in pairs])
    res["A5"] = dict(Fp_plus_minus_Fm_minus_3_Q=ms(fpm), Fp_plus_minus_Fm_minus_4_Q=ms(fpm4))
    if not a.no_fields:
        ev = [even_part(p, m) for _, p, m in pairs]
        for k in ev[0]:
            res["A5"][k] = ms([e[k] for e in ev])
        res["A5"]["per_pair_a_zeta"] = [e["a_zeta"] for e in ev]
        res["A5"]["per_pair_a_R"] = [e["a_R"] for e in ev]
    res["cost_note"] = "card time per run: batch status of each card run (read_pilot.py pilot.json 'cost')"
    with open(os.path.join(a.out, "pairs.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    figures(a.out, pairs, ref, res)
    print(json.dumps(dict(n_pairs=n, dropped=dropped, V=res["V"], T={k: (round(v["nr"], 6), round(v["ref"], 6),
                     round(v["n_se"], 2)) for k, v in T.items()}, bands=res["bands_entry4"], mirror=res["mirror"],
                     A5={k: v for k, v in res["A5"].items() if not k.startswith("per_pair")}), indent=1, default=float))


def figures(out, pairs, ref, res):
    fs.use_style()
    import matplotlib.pyplot as plt
    edges = np.linspace(-8.0, 8.0, 161)
    c = 0.5 * (edges[1:] + edges[:-1])
    dx = edges[1] - edges[0]
    hz = sum(np.load(os.path.join(p["_dir"], f"{p['_file']}_hist.npz"))["zeta"] +
             np.load(os.path.join(m["_dir"], f"{m['_file']}_hist.npz"))["zeta"] for _, p, m in pairs)
    hr = ref["_hist"]
    # one-point density with its tail
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    for hh, lab, col, mk in ((hr, r"one-patch $\delta N$ (8$\times10^6$ paths)", fs.PAL["blue"], "s"),
                             (hz, rf"NR $\zeta$ ({len(pairs)} pairs, {2 * len(pairs)} boxes)", fs.PAL["red"], "o")):
        p = hh / (hh.sum() * dx)
        ok = hh > 0
        err = np.sqrt(hh[ok]) / (hh.sum() * dx)
        ax[0].semilogy(c[ok], p[ok], mk, ms=2.5, color=col, mfc="none" if mk == "s" else col, label=lab)
        ax[1].errorbar(c[ok], p[ok] / norm.pdf(c[ok]), yerr=err / norm.pdf(c[ok]), fmt=mk, ms=2.5, color=col,
                       mfc="none" if mk == "s" else col, lw=0.8, label=lab)
    ax[0].plot(c, norm.pdf(c), **fs.GUIDE, label="Gaussian")
    ax[0].set_xlim(-6, 6)
    ax[0].set_ylim(1e-9, 1.0)
    ax[0].set_xlabel(r"$x/\sigma_{\rm own}$")
    ax[0].set_ylabel("probability density")
    ax[0].legend(fontsize=6.5, frameon=False, loc="lower center")
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_xlim(-5.6, 5.6)
    ax[1].set_ylim(0.3, 3.0)
    ax[1].set_yscale("log")
    fs.no_minor_labels(ax[1])
    ax[1].set_yticks([0.5, 1, 2])
    ax[1].set_yticklabels(["0.5", "1", "2"])
    ax[1].set_xlabel(r"$x/\sigma_{\rm own}$")
    ax[1].set_ylabel("density / Gaussian")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_g3_onepoint"))
    plt.close(fig)
    # tail fractions against the threshold
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    nus = ref["_tail_nu"]
    tot = hz.sum()
    cum_p = np.array([hz[c - 0.5 * dx >= t - 1e-9].sum() / tot for t in nus])
    cum_m = np.array([hz[c + 0.5 * dx <= -t + 1e-9].sum() / tot for t in nus])
    Q = norm.sf(nus)
    for arr, lab, col, mk in ((ref["_tail_p"], r"$F_+$ one-patch", fs.PAL["blue"], "-"),
                              (ref["_tail_m"], r"$F_-$ one-patch", fs.PAL["blue"], "--"),
                              (cum_p, r"$F_+$ NR", fs.PAL["red"], "-"), (cum_m, r"$F_-$ NR", fs.PAL["red"], "--")):
        ok = arr > 0
        ax[0].semilogy(nus[ok], arr[ok], mk, color=col, lw=1.2, label=lab)
        ax[1].plot(nus[ok], arr[ok] / Q[ok], mk, color=col, lw=1.2, label=lab)
    ax[0].semilogy(nus, Q, **fs.GUIDE, label="Gaussian")
    T = res["T"]
    for nu, kp, km in ((3, "Fp3", "Fm3"), (4, "Fp4", "Fm4")):
        for k, mk in ((kp, "o"), (km, "v")):
            t = T[k]
            q = norm.sf(nu)
            ax[1].errorbar(nu + 0.06, t["nr"] / q, yerr=3 * t["nr_se"] / q, fmt=mk, color=fs.PAL["red"], ms=3.5,
                           capsize=2)
            ax[1].errorbar(nu - 0.06, t["ref"] / q, yerr=3 * t["ref_se"] / q, fmt=mk, color=fs.PAL["blue"], ms=3.5,
                           mfc="none", capsize=2)
    ax[0].set_xlim(0, 5.5)
    ax[0].set_ylim(1e-8, 1)
    ax[0].set_xlabel(r"threshold $\nu$ (units of $\sigma_{\rm own}$)")
    ax[0].set_ylabel(r"$F_\pm(\nu)$")
    ax[0].legend(fontsize=6.5, frameon=False, loc="lower left")
    ax[1].axhline(1.0, color="k", lw=0.8, ls=":")
    ax[1].set_xlim(0, 5.0)
    ax[1].set_ylim(0.4, 1.8)
    ax[1].set_xlabel(r"threshold $\nu$ (units of $\sigma_{\rm own}$)")
    ax[1].set_ylabel(r"$F_\pm(\nu)/Q(\nu)$ (points: judged, bars $3\sigma$)")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_g3_tails"))
    plt.close(fig)
    # per pair: skewness of members and pairs, the even part
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.7))
    idx = np.array([i for i, _, _ in pairs])
    ax[0].plot(idx, [p["zeta_skew"] for _, p, _ in pairs], ".", color=fs.PAL["yellow"], ms=3, label="+ member")
    ax[0].plot(idx, [m["zeta_skew"] for _, _, m in pairs], ".", color=fs.PAL["green"], ms=3, label="- member")
    ax[0].plot(idx, [0.5 * (p["zeta_skew"] + m["zeta_skew"]) for _, p, m in pairs], "o", ms=3, color=fs.PAL["red"],
               label="pair mean")
    y, dy = ref["skew"]
    ax[0].axhspan(y - 3 * dy, y + 3 * dy, color=fs.PAL["blue"], alpha=0.2, lw=0, label=r"one-patch $\pm 3\sigma$")
    ax[0].set_xlabel("pair (seed 20262000 + i)")
    ax[0].set_ylabel(r"skewness of $\zeta$")
    ax[0].legend(fontsize=6, frameon=False, ncol=2)
    if "per_pair_a_zeta" in res["A5"]:
        ax[1].plot(idx, res["A5"]["per_pair_a_zeta"], "o", ms=3, color=fs.PAL["red"], label=r"$a_\zeta$")
        ax[1].plot(idx, res["A5"]["per_pair_a_R"], "s", ms=3, color=fs.PAL["orange"], label=r"$a_{\mathcal{R}}$")
        ax[1].axhspan(6.5e-3, 7.4e-3, color=fs.PAL["red"], alpha=0.12, lw=0, label="P15-2 band")
        ax[1].axhline(0.0, color="k", lw=0.8, ls=":")
        ax[1].set_xlabel("pair")
        ax[1].set_ylabel("even-part coefficient")
        ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_g3_pairs"))
    plt.close(fig)


if __name__ == "__main__":
    main()
