#!/usr/bin/env python3
"""Tests of the review of branch core/noise-level2 (tracks/core/JOURNAL-noise-level2.md,
entries 7 and 8): what the choices that the paper leaves open change, and a lapse that
is not 1.

    review_tests.py --exe ATHENA --out DIR [--workers 5] [--analyse-only [--from DIR]]

All runs: problems/scalar/sr_stochastic.athinput (slow roll, 32^3, nmax2 = 64, the
perturbed slice at N*), dumps with the metric and the per-mode record of the projections.

R2, R3 (t = 0 .. 3.2, dumps every 0.4), amplitude 1 and, where named, 1e-2
(noise_mode_scale; slice and sources scale with it):
  s2m, s2m_a    level 2 as it is: psi^-4 gt^ij d_i d_j R, window and kicks from the means
  s2c, s2c_a    noise_level2_laplacian = covariant (D^i D_i R)
  s2f, s2f_a    noise_level2_laplacian = flat (psi^-4 delta^ij d_i d_j R)
  s2w           noise_level2_background = friedmann
  s1m, s1m_a    level 1 on the mesh
  s0m           level 0 on the mesh
R4 (homogeneous slice, kicks off; conformal-time lapse d_t alpha = -(1/3) alpha^2 K
through <z4c> lapse_harmonic = 1/3; t = 0 .. 0.85, dumps every 0.085):
  c2, c1        level 2, level 1 on the mesh, lapse = a
  g1            level 1 on the mesh with geodesic slicing, t = 0 .. 2.0, dumps every 0.2
                (the reference of the mesh-against-shells deviation at equal ln a)
Writes DIR/review.json, DIR/fig_readings.png, DIR/fig_lapse.png."""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpu_tests as ct                      # noqa: E402
import nl2                                  # noqa: E402
import numpy as np                          # noqa: E402
from nrpic import scalar_field as sf        # noqa: E402

BASE = dict(ct.BASE)
L2, L1M, L0M, OFF, HOM = ct.L2, ct.L1M, ct.L0M, ct.OFF, ct.HOM
AMP = {"scalar_field/noise_mode_scale": 1e-2}
CONF = {"z4c/lapse_harmonic": 1.0/3.0, "time/tlim": 0.85, "scalar_field/dump_dt": 0.085}
GEO = {"time/tlim": 2.0, "scalar_field/dump_dt": 0.2}


def cases():
    lap = "scalar_field/noise_level2_laplacian"
    c = {
        "s2m": {**L2}, "s2c": {**L2, lap: "covariant"}, "s2f": {**L2, lap: "flat"},
        "s2w": {**L2, "scalar_field/noise_level2_background": "friedmann"},
        "s1m": {**L1M}, "s0m": {**L0M},
        "s2m_a": {**L2, **AMP}, "s2c_a": {**L2, lap: "covariant", **AMP},
        "s2f_a": {**L2, lap: "flat", **AMP}, "s1m_a": {**L1M, **AMP},
        "c2": {**HOM, **L2, **OFF, **CONF}, "c1": {**HOM, **L1M, **OFF, **CONF},
        "g1": {**HOM, **L1M, **OFF, **GEO},
    }
    return {k: {**BASE, **v} for k, v in c.items()}


def run_all(exe, out, workers):
    walls, rcs = {}, {}

    def one(name, par):
        inp = nl2.write_input(ct.INP, os.path.join(out, name + ".athinput"), par)
        t0 = time.time()
        rc = nl2.run(exe, os.path.join(out, name), inp)
        return name, rc, round(time.time() - t0, 2)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for f in [pool.submit(one, k, v) for k, v in cases().items()]:
            k, rc, w = f.result()
            rcs[k], walls[k] = rc, w
    return rcs, walls


def coef_pairs(out, a, b):
    """per dump: rms and max over the modes of |c_a/c_b - 1| of the projected R."""
    rows = []
    for k in range(min(ct.ndumps(os.path.join(out, a)), ct.ndumps(os.path.join(out, b)))):
        ha, _, _, ra, da = ct.modes_at(os.path.join(out, a), k)
        _, _, _, rb, db = ct.modes_at(os.path.join(out, b), k)
        d = ct.rel(ra, rb)
        dd = ct.rel(da, db)
        rows.append(dict(time=ha["time"], rms=float(np.sqrt(np.mean(d*d))),
                         max=float(d.max()), rms_dR=float(np.sqrt(np.mean(dd*dd)))))
    return rows


def shell_power(out, lab, nn, nn2):
    """shell means of |R^NR_n|^2 at the last dump, and the window of every shell."""
    row = ct.t2rnr_complex(os.path.join(out, lab), nn, nn2)[-1]
    sh = np.unique(nn2)
    p = np.array([np.mean(np.abs(row["rnr"][nn2 == s])**2) for s in sh])
    w = np.array([row["w"][nn2 == s][0] for s in sh])
    return sh, p, w


def analyse(out):
    s = {}
    pairs = {"L2-L1m": ("s2m", "s1m"), "L2-L0m": ("s2m", "s0m"), "L1m-L0m": ("s1m", "s0m"),
             "cov-metric": ("s2c", "s2m"), "flat-metric": ("s2f", "s2m"),
             "friedmann-means": ("s2w", "s2m"),
             "L2-L1m_a": ("s2m_a", "s1m_a"), "cov-metric_a": ("s2c_a", "s2m_a"),
             "flat-metric_a": ("s2f_a", "s2m_a")}
    s["coef"] = {k: coef_pairs(out, a, b) for k, (a, b) in pairs.items()}
    last = {k: v[-1] for k, v in s["coef"].items()}
    ref = last["L2-L1m"]["rms"]
    s["R2"] = dict(
        level2_effect_rms=ref,
        cov_over_level2=last["cov-metric"]["rms"]/ref,
        flat_over_level2=last["flat-metric"]["rms"]/ref,
        # second order: the relative difference falls with the amplitude
        scaling_level2=last["L2-L1m_a"]["rms"]/ref,
        scaling_cov=last["cov-metric_a"]["rms"]/last["cov-metric"]["rms"],
        scaling_flat=last["flat-metric_a"]["rms"]/last["flat-metric"]["rms"],
        worst_ratio_all_dumps=dict(
            cov=float(max(a["rms"]/b["rms"] for a, b in
                          zip(s["coef"]["cov-metric"][1:], s["coef"]["L2-L1m"][1:]))),
            flat=float(max(a["rms"]/b["rms"] for a, b in
                           zip(s["coef"]["flat-metric"][1:], s["coef"]["L2-L1m"][1:])))))
    s["R3"] = dict(
        friedmann_over_level2=last["friedmann-means"]["rms"]/ref,
        level1_over_level2=last["L1m-L0m"]["rms"]/ref,
        friedmann_over_level1=last["friedmann-means"]["rms"]/last["L1m-L0m"]["rms"])
    # the quantity of P1 Fig. 9: relative difference of the shell power of R^NR
    nn, nn2 = sf.mode_set(ct.NMAX2)
    pw = {lab: shell_power(out, lab, nn, nn2) for lab in ("s2m", "s2c", "s2f", "s2w",
                                                          "s1m", "s0m")}
    sh, p0, w = pw["s0m"]
    ent = w > 0.5
    fig9 = {}
    for name, a, b in (("L2/L0m", "s2m", "s0m"), ("L1m/L0m", "s1m", "s0m"),
                       ("cov/metric", "s2c", "s2m"), ("flat/metric", "s2f", "s2m"),
                       ("friedmann/means", "s2w", "s2m")):
        d = pw[a][1]/pw[b][1] - 1.0
        fig9[name] = dict(max_abs=float(np.abs(d[ent]).max()),
                          rms=float(np.sqrt(np.mean(d[ent]**2))), per_shell=d.tolist())
    s["shell_power"] = dict(shells=sh.tolist(), entered=ent.tolist(), pairs=fig9)

    # ---- R4: conformal-time lapse, homogeneous slice, kicks off
    r4 = dict(l2_vs_l1=coef_pairs(out, "c2", "c1"))
    for lab in ("c1", "c2", "g1"):
        rd = os.path.join(out, lab)
        rows = []
        for k in range(ct.ndumps(rd)):
            h, n, n2, r, dr = ct.modes_at(rd, k)
            head, rs, drs = ct.shells_at(rd, k, n2)
            hst = hist_at(rd, h["time"])
            rows.append(dict(time=h["time"], ln_a=float(np.log(head["a"])),
                             alpha=hst["alpha"],
                             cut=float(ct.rel(r, rs)[n2 == ct.NMAX2].max()),
                             le48=float(ct.rel(r, rs)[n2 <= 48].max()),
                             dR_cut=float(ct.rel(dr, drs)[n2 == ct.NMAX2].max()),
                             dR_le48=float(ct.rel(dr, drs)[n2 <= 48].max())))
        r4[lab] = rows
    # at equal ln a: the conformal run's deviation over the geodesic one's (interpolated)
    xa = np.array([r["ln_a"] for r in r4["g1"]])
    cmp_ = []
    for r in r4["c1"][1:]:
        if r["ln_a"] > xa[-1]:
            continue
        g_cut = float(np.interp(r["ln_a"], xa, [q["cut"] for q in r4["g1"]]))
        g_48 = float(np.interp(r["ln_a"], xa, [q["le48"] for q in r4["g1"]]))
        cmp_.append(dict(ln_a=r["ln_a"], alpha=r["alpha"], cut_conf=r["cut"],
                         cut_geo=g_cut, le48_conf=r["le48"], le48_geo=g_48))
    r4["equal_ln_a"] = cmp_
    s["R4"] = r4
    return s


def hist_at(rundir, t):
    d = np.loadtxt(os.path.join(rundir, "sr.sf.hst"), comments="#")
    i = int(np.argmin(np.abs(d[:, 0] - t)))
    return dict(time=float(d[i, 0]), alpha=float(d[i, 6]))


def figures(out, s):
    fs = ct.nl2_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.9, wspace=0.4)
    a = ax[0]
    sty = (("L2-L1m", fs.PAL["orange"], "o", "level 2 $-$ level 1"),
           ("cov-metric", fs.PAL["blue"], "s", r"$D^iD_i$ $-$ $\tilde\gamma^{ij}\partial_i\partial_j$"),
           ("flat-metric", fs.PAL["green"], "^", r"$\delta^{ij}\partial_i\partial_j$ $-$ $\tilde\gamma^{ij}\partial_i\partial_j$"),
           ("friedmann-means", fs.PAL["red"], "v", "window: Friedmann $-$ means"),
           ("L1m-L0m", "0.4", "x", "level 1 $-$ level 0"))
    for key, cl, mk, nm in sty:
        rows = s["coef"][key][1:]
        a.semilogy([r["time"] for r in rows], [max(r["rms"], 1e-18) for r in rows],
                   mk + "-", ms=3, color=cl, label=nm)
    a.set_xlabel("$t$ (1/H$_*$)")
    a.set_ylabel(r"rms$_n$ $|c_R^{(1)}/c_R^{(2)}-1|$")
    a.set_title("(a) projected coefficients", fontsize=8)
    a.set_ylim(1e-13, 1e-1)
    a.legend(fontsize=5.5, loc="upper left")
    a = ax[1]
    for key, cl, mk, nm in sty[:3]:
        r1 = s["coef"][key][1:]
        r2 = s["coef"][key + "_a"][1:]
        a.semilogy([r["time"] for r in r1],
                   [q["rms"]/max(r["rms"], 1e-300) for r, q in zip(r1, r2)], mk + "-",
                   ms=3, color=cl, label=nm)
    a.axhline(1e-2, color="0.4", lw=0.8, ls="--")
    a.set_xlabel("$t$ (1/H$_*$)")
    a.set_ylabel("ratio, amplitude $10^{-2}$ over 1")
    a.set_title("(b) order in the amplitude", fontsize=8)
    a.set_ylim(1e-3, 1e-1)
    a.legend(fontsize=5.5, loc="upper right")
    a = ax[2]
    sp = s["shell_power"]
    q = np.sqrt(np.array(sp["shells"], float))
    ent = np.array(sp["entered"])
    for key, cl, mk, nm in (("L2/L0m", fs.PAL["orange"], "o", "level 2 / level 0"),
                            ("L1m/L0m", "0.4", "x", "level 1 / level 0"),
                            ("cov/metric", fs.PAL["blue"], "s", r"$D^iD_i$ / default"),
                            ("flat/metric", fs.PAL["green"], "^", r"$\delta^{ij}$ / default"),
                            ("friedmann/means", fs.PAL["red"], "v", "Friedmann / means")):
        d = np.abs(np.array(sp["pairs"][key]["per_shell"]))
        a.semilogy(q[ent], np.maximum(d[ent], 1e-18), mk, ms=2.5, color=cl, label=nm)
    a.set_xlabel("$|n|$")
    a.set_ylabel(r"$|\Delta P/P|$ of $R^{\rm NR}$ per shell")
    a.set_title("(c) shell power at $t=3.2$, $32^3$", fontsize=8)
    a.set_ylim(1e-14, 1e-1)
    a.legend(fontsize=5.5, loc="lower right", ncol=2)
    fig.savefig(os.path.join(out, "fig_readings.png"), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.9, wspace=0.3)
    a = ax[0]
    r4 = s["R4"]
    for lab, cl, nm in (("c1", fs.PAL["orange"], r"lapse $=a$"),
                        ("g1", fs.PAL["blue"], "geodesic slicing")):
        rows = r4[lab][1:]
        x = [r["ln_a"] for r in rows]
        a.semilogy(x, [r["cut"] for r in rows], "o-", ms=3, color=cl,
                   label=nm + ", $|n|^2=64$")
        a.semilogy(x, [r["le48"] for r in rows], "s--", ms=3, color=cl,
                   label=nm + r", $|n|^2\leq48$")
    a.set_xlabel(r"$\ln a$")
    a.set_ylabel(r"max$_n$ $|R^{\rm mesh}_n/R^{\rm shell}_n-1|$")
    a.set_title("(a) level 1 on the mesh against the shells, kicks off", fontsize=8)
    a.legend(fontsize=6, loc="lower right")
    a = ax[1]
    rows = r4["l2_vs_l1"][1:]
    a.semilogy([r["time"] for r in rows], [max(r["max"], 1e-18) for r in rows], "o-",
               ms=3, color=fs.PAL["orange"], label="$R$")
    a.semilogy([r["time"] for r in rows], [max(r["rms_dR"], 1e-18) for r in rows], "s-",
               ms=3, color=fs.PAL["blue"], label=r"$n\cdot\partial R$ (rms)")
    a2 = a.twinx()
    a2.plot([r["time"] for r in r4["c1"]], [r["alpha"] for r in r4["c1"]], "-",
            color="0.5", lw=0.8)
    a2.set_ylabel(r"$\langle\alpha\rangle$ (grey)")
    a.set_xlabel("conformal time $t$ (1/H$_*$)")
    a.set_ylabel(r"$|c^{L2}/c^{L1}-1|$")
    a.set_title(r"(b) level 2 against level 1, lapse $=a$", fontsize=8)
    a.legend(fontsize=6, loc="upper left")
    fig.subplots_adjust(right=0.93)
    fig.savefig(os.path.join(out, "fig_lapse.png"), dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--from", dest="src")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    src = os.path.abspath(a.src) if a.src else out
    summ = dict(exe=os.path.abspath(a.exe), runs=src)
    if not a.analyse_only:
        summ["exit"], summ["wall_s"] = run_all(os.path.abspath(a.exe), out, a.workers)
    else:
        old = json.load(open(os.path.join(src, "review.json")))
        summ["exit"], summ["wall_s"] = old.get("exit"), old.get("wall_s")
    summ.update(analyse(src))
    nl2.dump_json(summ, os.path.join(out, "review.json"))
    figures(out, summ)
    print(json.dumps({k: summ[k] for k in ("exit", "R2", "R3")}, indent=1))
    print(json.dumps(summ["shell_power"]["pairs"] and
                     {k: {q: v[q] for q in ("max_abs", "rms")}
                      for k, v in summ["shell_power"]["pairs"].items()}, indent=1))
    print(json.dumps(dict(l2_vs_l1=summ["R4"]["l2_vs_l1"][-1],
                          equal_ln_a=summ["R4"]["equal_ln_a"]), indent=1))


if __name__ == "__main__":
    main()
