"""K1: the Kerr spike of FdRW (arXiv:1707.06302) recomputed by their method (kerr_lib.py)
and compared with what they print: numbers in the text and captions, and the curves of
fig_rho_a, fig_rho_theta, fig_rho_hern, fig_angle_hern, figequator1, figemin (digitized
by kerr_curves.py from the PGF sources).

usage: python3 kerr_reference.py --out <scratch run dir> [--kb <kb-data/raw/arxiv>] [--np 8]
Writes kerr_reference.json, kerr_curves_ours.npz and figures into --out, copies the PNGs
to figs/.
"""
import argparse
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from kerr_lib import Kerr, KerrHernquist, equatorial_planar, gl  # noqa: E402
from spike_lib import (KMS, MSUN_PC3_TO_GEV_CM3, SpikeModel, rho_constf_rel,  # noqa: E402
                       HernquistInverse, Emin_sfw)

warnings.simplefilter("ignore", RuntimeWarning)
GEV = MSUN_PC3_TO_GEV_CM3
F0 = 0.3 / (2 * np.pi * (100.0 * KMS) ** 2) ** 1.5      # FdRW line 763 (= SFW)
_H = None


def _init():
    global _H
    os.environ["OMP_NUM_THREADS"] = "1"
    _H = KerrHernquist(M_sun=1e12, a_pc=2.0e4, m_sun=4e6)


def job(arg):
    kind, a, r, th = arg
    K = Kerr(a)
    t0 = time.time()
    if kind == "planar":
        rho, jt, em = equatorial_planar(K, r)
        return {"kind": kind, "a": a, "r": r, "th": th, "rho": rho, "J_t": jt, "Emin": em,
                "wall": time.time() - t0}
    m = K.moments(r, th, fmodel=None if kind == "constf" else _H)
    m.update({"kind": kind, "a": a, "wall": time.time() - t0})
    return {k: (float(v) if isinstance(v, (np.floating, float, int, np.integer)) else v)
            for k, v in m.items()}


def r_min(K, th, lo=None, hi=12.0, n=34):
    """Inner edge of the spike: smallest r with a bound non-plunging orbit through it."""
    lo = K.rp + 1e-3 if lo is None else lo
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if K.Emin(mid, th) < 1.0:
            hi = mid
        else:
            lo = mid
    return hi


def peak(x, y):
    i = int(np.nanargmax(y))
    if 0 < i < len(y) - 1:
        c = np.polyfit(x[i - 1:i + 2], y[i - 1:i + 2], 2)
        xp = -c[1] / (2 * c[0])
        return float(xp), float(np.polyval(c, xp))
    return float(x[i]), float(y[i])


def interp_curve(xq, x, y):
    x = np.asarray(x); y = np.asarray(y)
    o = np.argsort(x)
    return np.interp(xq, x[o], y[o], left=np.nan, right=np.nan)


def axis_closed_form(K, r, nE=400):
    """FdRW eq. (825): on the axis J_t = 4 pi f0/sqrt(Delta) int dE E sqrt(C_max - C_crit),
    rho = |J_t| sqrt((r^2 + a^2)/Delta); f0 = 1. Independent 1D quadrature in E."""
    D = K.Delta(r)
    Em = K.Emin(r, 0.0)
    s, w = gl(nE)
    E = Em + (1 - Em) * s ** 2
    w = w * 2 * s * (1 - Em)
    Cc, _, end = K.ccrit(E, np.zeros_like(E), r)
    Cmax = K.CV(E, np.zeros_like(E), r)
    lo = np.maximum(Cc, K.a ** 2 * (1 - E * E))       # U >= 0 on the axis: C >= a^2 (1-E^2)
    val = np.where(end, 0.0, np.sqrt(np.clip(Cmax - lo, 0.0, None)))
    Jt = 4 * np.pi / np.sqrt(D) * np.sum(w * E * val)
    return Jt * np.sqrt((r * r + K.a ** 2) / D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kb", default="/data/haiyangw/nrpic/kb-data/raw/arxiv")
    ap.add_argument("--np", type=int, default=8)
    ap.add_argument("--nr", type=int, default=44)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = {"f0_GeV_cm3": F0}

    subprocess.run([sys.executable, "-I", str(HERE / "kerr_curves.py"), args.kb, str(out)],
                   check=True)
    dig = json.loads((out / "kerr_curves.json").read_text())

    # ---- building-block checks ----------------------------------------------------------
    chk = {}
    K0 = Kerr(0.0)
    chk["a0_Emin_vs_SFW_3.17"] = [[r, K0.Emin(r, np.pi / 2), float(Emin_sfw(r))]
                                  for r in (4.05, 4.2, 5.0, 6.0, 8.0, 20.0, 40.0)]
    # brute-force check of the assumption that the allowed E set is an interval [Emin, 1)
    bf = []
    for a, r, th in ((0.8, 3.0, np.pi / 2), (0.8, 10.0, np.pi / 3), (0.5, 6.0, 0.2),
                     (0.8, 4.0, 0.0)):
        K = Kerr(a)
        Eg = np.linspace(0.8, 0.999999, 600)
        mm = K.allowed_measure(Eg, r, th) > 0
        first = Eg[np.argmax(mm)] if mm.any() else 1.0
        holes = int(np.sum(~mm[np.argmax(mm):])) if mm.any() else 0
        bf.append({"a": a, "r": r, "th": th, "Emin_bisect": K.Emin(r, th),
                   "Emin_scan_first": float(first), "scan_step": float(Eg[1] - Eg[0]),
                   "forbidden_points_above_first": holes})
    chk["Emin_interval_bruteforce"] = bf
    # FdRW fig. crit_orbit caption (kerrdm.tex line 497): C_crit = 10.3 for a = 0.75,
    # E = 0.97, Lz = 2 (minimum of C_V over the unstable orbit region)
    K75 = Kerr(0.75)
    Cc, ru, end = K75.ccrit(np.array([0.97]), np.array([2.0]), 30.0)
    chk["Ccrit_a0.75_E0.97_Lz2"] = {"ours": float(Cc[0]), "r_unst": float(ru[0]),
                                    "FdRW_caption": 10.3}
    # FdRW fig. viterate caption (line 1508): x = 10, E0 = 0.9997, Lz^max = 4.829 by eq.
    # (lmax); the spin is not stated; eq. (lmax) as printed has a^2 - x(x-2) under the root
    x, E0 = 10.0, 0.9997
    vit = {}
    for a in (0.5, 0.7, 0.72, 0.75, 0.8):
        printed = x * (a * a - x * (x - 2)) * (2 - (1 - E0 ** 2) * x)
        fixed = x * (a * a + x * (x - 2)) * (2 - (1 - E0 ** 2) * x)
        vit[f"a={a}"] = {"Lmax_printed_form": None if printed < 0 else
                         (-2 * a * E0 + np.sqrt(printed)) / (x - 2),
                         "Lmax_with_a2+x(x-2)": (-2 * a * E0 + np.sqrt(fixed)) / (x - 2)}
    chk["viterate_Lmax"] = vit
    # FdRW eq. (mborbit): planar co-/counter-rotating edges 2 -+ a + 2 sqrt(1 -+ a)
    mb = {}
    for a in (0.5, 0.8):
        K = Kerr(a)
        mb[f"a={a}"] = {"r_min_equator_ours": r_min(K, np.pi / 2),
                        "r_mb+_closed_form": 2 - a + 2 * np.sqrt(1 - a),
                        "r_mb-_closed_form": 2 + a + 2 * np.sqrt(1 + a),
                        "r_min_axis_ours": r_min(K, 0.0),
                        "r_min_pi/3_ours": r_min(K, np.pi / 3)}
    chk["edges"] = mb
    # on-axis closed form (FdRW eq. 825) against the general routine at theta = 0
    K8 = Kerr(0.8)
    ax = []
    for r in (4.5, 7.0, 15.0):
        g = K8.moments(r, 0.0)
        ax.append([r, g["rho"], axis_closed_form(K8, r)])
    chk["axis_closed_form_vs_general_a0.8"] = ax
    res["checks"] = chk
    print("checks done", time.time() - t0, flush=True)

    # ---- curves -----------------------------------------------------------------------
    jobs, keys = [], []
    grids = {}
    specs = [("constf", 0.0, np.pi / 2), ("constf", 0.5, np.pi / 2), ("constf", 0.8, np.pi / 2),
             ("constf", 0.8, 0.0), ("constf", 0.8, np.pi / 3),
             ("hern", 0.0, np.pi / 2), ("hern", 0.5, np.pi / 2), ("hern", 0.8, np.pi / 2),
             ("hern", 0.8, 0.0), ("hern", 0.8, np.pi / 3),
             ("planar", 0.0, np.pi / 2), ("planar", 0.5, np.pi / 2), ("planar", 0.8, np.pi / 2)]
    edges = {}
    for kind, a, th in specs:
        key = (a, round(th, 6))
        if key not in edges:
            edges[key] = r_min(Kerr(a), th)
    res["r_min"] = {f"a={a},th={th}": v for (a, th), v in edges.items()}
    for kind, a, th in specs:
        rm = edges[(a, round(th, 6))]
        rmax = 16.0 if kind == "planar" else 40.0
        nr = 26 if kind == "planar" else args.nr
        k = np.arange(1, nr + 1)
        rg = rm + (rmax - rm) * (k / nr) ** 2
        if kind == "planar":
            rg = rg[rg > 2.0 + 1e-6]
        name = f"{kind}_a{a}_th{th:.4f}"
        grids[name] = rg
        for r in rg:
            jobs.append((kind, a, float(r), th)); keys.append(name)
    with mp.Pool(args.np, initializer=_init) as pool:
        outs = pool.map(job, jobs, chunksize=1)
    curves = {}
    for name, o in zip(keys, outs):
        curves.setdefault(name, []).append(o)
    res["wall_curves_s"] = time.time() - t0
    nanf = sum(int(o.get("nan_f", 0)) for o in outs)
    res["nan_f_total"] = nanf

    # ---- a = 0 against the wave-1 Schwarzschild references -----------------------------
    sm = SpikeModel(m_sun=4e6, table=HernquistInverse())
    H = KerrHernquist(m_sun=4e6)
    c = curves["constf_a0.0_th1.5708"]
    rr = np.array([o["r"] for o in c])
    ours = np.array([o["rho"] for o in c])
    ref = rho_constf_rel(rr, 1.0)
    h = curves["hern_a0.0_th1.5708"]
    oh = np.array([o["rho"] for o in h]) * H.Af
    rh = sm.rho_rel(rr, "canonical")
    sel = rr > 4.05
    res["a0_vs_wave1"] = {"constf_maxrel": float(np.max(np.abs(ours[sel] / ref[sel] - 1))),
                          "hern_maxrel": float(np.max(np.abs(oh[sel] / rh[sel] - 1))),
                          "r_range": [float(rr[sel][0]), float(rr[-1])]}

    # ---- comparisons with the digitized curves ------------------------------------------
    def arr(name, scale):
        cc = curves[name]
        return np.array([o["r"] for o in cc]), np.array([o["rho"] for o in cc]) * scale

    cmp_ = {}
    pairs = [("constf_a0.0_th1.5708", "fig_rho_a", "a=0", F0 / 1e8),
             ("constf_a0.5_th1.5708", "fig_rho_a", "a=0.5", F0 / 1e8),
             ("constf_a0.8_th1.5708", "fig_rho_a", "a=0.8", F0 / 1e8),
             ("constf_a0.8_th0.0000", "fig_rho_theta", "theta=0", F0 / 1e8),
             ("constf_a0.8_th1.0472", "fig_rho_theta", "theta=pi/3", F0 / 1e8),
             ("constf_a0.8_th1.5708", "fig_rho_theta", "theta=pi/2", F0 / 1e8),
             ("hern_a0.0_th1.5708", "fig_rho_hern", "a=0", H.Af * GEV / 1e18),
             ("hern_a0.5_th1.5708", "fig_rho_hern", "a=0.5", H.Af * GEV / 1e18),
             ("hern_a0.8_th1.5708", "fig_rho_hern", "a=0.8", H.Af * GEV / 1e18),
             ("hern_a0.8_th0.0000", "fig_angle_hern", "theta=0", H.Af * GEV / 1e18),
             ("hern_a0.8_th1.0472", "fig_angle_hern", "theta=pi/3", H.Af * GEV / 1e18),
             ("hern_a0.8_th1.5708", "fig_angle_hern", "theta=pi/2", H.Af * GEV / 1e18),
             ("planar_a0.0_th1.5708", "figequator1", "a=0", 1.0),
             ("planar_a0.5_th1.5708", "figequator1", "a=0.5", 1.0),
             ("planar_a0.8_th1.5708", "figequator1", "a=0.8", 1.0)]
    for ours_name, fig, ck, scale in pairs:
        r_, y_ = arr(ours_name, scale)
        d = dig[fig]["curves"][ck]
        pk_o, pk_d = peak(r_, y_), peak(np.array(d["x"]), np.array(d["y"]))
        dense = np.linspace(r_[0], r_[-1], 2000)
        yo = np.interp(dense, r_, y_)
        pk_o = peak(dense, yo)
        yd = interp_curve(dense, d["x"], d["y"])
        # compare where the digitized curve is above 10 % of its peak and inside its range
        m = np.isfinite(yd) & (yd > 0.1 * pk_d[1]) & (dense < 39.0)
        rel = yo[m] / yd[m] - 1
        e = {"peak_ours": pk_o, "peak_digitized": pk_d,
             "peak_value_ratio": pk_o[1] / pk_d[1], "peak_r_diff": pk_o[0] - pk_d[0],
             "maxabs_rel_dev": float(np.max(np.abs(rel))), "median_rel_dev": float(np.median(rel)),
             "range": [float(dense[m][0]), float(dense[m][-1])],
             "inner_zero_ours": float(r_[0]) if True else None,
             "inner_end_digitized": float(min(d["x"]))}
        if fig == "figequator1":
            # normalization: ratio of the curves at their peaks; shape after rescaling
            sc = pk_d[1] / pk_o[1]
            rel2 = yo[m] * sc / yd[m] - 1
            e["scale_digitized_over_ours"] = sc
            e["shape_maxabs_rel_dev_after_scale"] = float(np.max(np.abs(rel2)))
        cmp_[f"{fig}:{ck}"] = e
    res["digitized"] = cmp_

    # E_min(10 Gm) vs a (figemin)
    d = dig["figemin"]["curves"]["Emin(10Gm)"]
    aa = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99])
    em = np.array([Kerr(a).Emin(10.0, np.pi / 2) for a in aa])
    emd = interp_curve(aa, d["x"], d["y"])
    res["figemin"] = {"a": aa.tolist(), "ours": em.tolist(), "digitized": emd.tolist(),
                      "maxabs_diff": float(np.nanmax(np.abs(em - emd)))}

    # text claims
    p = lambda key: cmp_[key]["peak_ours"][1]  # noqa: E731
    q = lambda key: cmp_[key]["peak_digitized"][1]  # noqa: E731
    res["text_claims"] = {
        "constf_peak_a0.8_over_a0 (FdRW line 213: 20%)": [p("fig_rho_a:a=0.8") / p("fig_rho_a:a=0"),
                                                          q("fig_rho_a:a=0.8") / q("fig_rho_a:a=0")],
        "constf_peak_a0.8_over_a0.5 (line 931: ~20%)": [p("fig_rho_a:a=0.8") / p("fig_rho_a:a=0.5"),
                                                         q("fig_rho_a:a=0.8") / q("fig_rho_a:a=0.5")],
        "hern_peak_a0.8_over_a0.5 (line 929: ~35%)": [p("fig_rho_hern:a=0.8") / p("fig_rho_hern:a=0.5"),
                                                       q("fig_rho_hern:a=0.8") / q("fig_rho_hern:a=0.5")],
        "hern_peak_a0.8_over_a0 (line 199: ~70%)": [p("fig_rho_hern:a=0.8") / p("fig_rho_hern:a=0"),
                                                     q("fig_rho_hern:a=0.8") / q("fig_rho_hern:a=0")],
        "order": "[ours, digitized]"}
    res["wall_s"] = time.time() - t0
    (out / "kerr_reference.json").write_text(json.dumps(res, indent=1, default=float))
    np.savez(out / "kerr_curves_ours.npz",
             **{f"{n}_{k}": np.array([o[k] for o in c]) for n, c in curves.items()
                for k in ("r", "rho", "J_t", "Emin")},
             **{f"{n}_n": np.array([o.get("n", np.nan) for o in c]) for n, c in curves.items()},
             **{f"{n}_Lzmean": np.array([o.get("Lz_mean", np.nan) for o in c])
                for n, c in curves.items()})

    # ---- figures ------------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    P = figstyle.PAL
    figdir = HERE / "figs"; figdir.mkdir(exist_ok=True)
    cols = {"a=0": P["blue"], "a=0.5": P["yellow"], "a=0.8": P["red"],
            "theta=0": P["green"], "theta=pi/3": P["orange"], "theta=pi/2": P["red"]}

    def panel_pair(axt, axb, fig, items, scale, ylab, ylim):
        for ours_name, ck, lab in items:
            r_, y_ = arr(ours_name, scale)
            d = dig[fig]["curves"][ck]
            col = cols[ck]
            axt.plot(d["x"], d["y"], color=col, lw=3.0, alpha=0.35)
            axt.plot(r_, y_, color=col, label=lab)
            dense = np.linspace(r_[0], 39.0, 600)
            yd = interp_curve(dense, d["x"], d["y"])
            yo = np.interp(dense, r_, y_)
            mm = np.isfinite(yd) & (yd > 0.1 * np.nanmax(yd))
            axb.plot(dense[mm], (yo[mm] / yd[mm] - 1) * 100, color=col)
        axt.set_xlim(0, 40); axt.set_ylim(*ylim); axt.tick_params(labelbottom=False)
        axt.set_ylabel(ylab)
        axt.legend(loc="upper right", fontsize=8, title="thin: ours, thick: FdRW",
                   title_fontsize=7)
        axb.axhline(0, **figstyle.THIN)
        axb.set_xlim(0, 40); axb.set_ylim(-6, 6)
        axb.set_xlabel(r"$r/Gm$ (Boyer-Lindquist)", labelpad=-2)
        axb.set_ylabel("ours/FdRW $-$ 1 [%]")

    for kind, figA, figB, scale, ylab, ylim, fname in (
            ("constf", "fig_rho_a", "fig_rho_theta", F0 / 1e8,
             r"$\rho$ [$10^8$ GeV cm$^{-3}$]", (-0.02, 1.15), "kerr_ref_constf"),
            ("hern", "fig_rho_hern", "fig_angle_hern", H.Af * GEV / 1e18,
             r"$\rho$ [$10^{18}$ GeV cm$^{-3}$]", (-0.05, 4.4), "kerr_ref_hernquist")):
        fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.0), gridspec_kw=dict(height_ratios=[3, 1.3]))
        fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.10, hspace=0.0, wspace=0.25)
        panel_pair(axs[0, 0], axs[1, 0], figA,
                   [(f"{kind}_a0.0_th1.5708", "a=0", r"$a=0$"),
                    (f"{kind}_a0.5_th1.5708", "a=0.5", r"$a=0.5$"),
                    (f"{kind}_a0.8_th1.5708", "a=0.8", r"$a=0.8$")], scale, ylab, ylim)
        axs[0, 0].set_title(f"equator, {'constant f' if kind == 'constf' else 'Hernquist'}",
                            fontsize=10)
        panel_pair(axs[0, 1], axs[1, 1], figB,
                   [(f"{kind}_a0.8_th0.0000", "theta=0", r"$\theta=0$"),
                    (f"{kind}_a0.8_th1.0472", "theta=pi/3", r"$\theta=\pi/3$"),
                    (f"{kind}_a0.8_th1.5708", "theta=pi/2", r"$\theta=\pi/2$")], scale, ylab, ylim)
        axs[0, 1].set_title(r"$a=0.8$, three polar angles", fontsize=10)
        for ext in ("pdf", "png"):
            fig.savefig(out / f"{fname}.{ext}")
        plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.15, wspace=0.28)
    a_ = axs[0]
    for ck in ("a=0", "a=0.5", "a=0.8"):
        name = f"planar_a{float(ck[2:])}_th1.5708"
        r_, y_ = arr(name, 1.0)
        sc = cmp_[f"figequator1:{ck}"]["scale_digitized_over_ours"]
        d = dig["figequator1"]["curves"][ck]
        a_.plot(d["x"], d["y"], color=cols[ck], lw=3.0, alpha=0.35)
        a_.plot(r_, y_ * sc, color=cols[ck], label=f"{ck}, ours x {sc:.3f}")
    a_.set_xlim(0, 16); a_.set_xlabel(r"$r/Gm$"); a_.set_ylabel(r"$\rho/f_{\rm eq}$ (planar orbits)")
    a_.legend(loc="upper right", fontsize=8)
    a_.set_title("FdRW figequator1 (thick) and ours", fontsize=10)
    b_ = axs[1]
    dm =dig["figemin"]["curves"]["Emin(10Gm)"]
    b_.plot(dm["x"], dm["y"], color=P["blue"], lw=3.0, alpha=0.35, label="FdRW figemin")
    b_.plot(aa, em, "o-", color=P["red"], ms=3, label="ours (bisection)")
    b_.set_xlabel(r"$\tilde a$"); b_.set_ylabel(r"$\mathcal{E}_{\min}(r=10\,Gm,\ \theta=\pi/2)$")
    b_.legend(loc="upper right", fontsize=8)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"kerr_ref_checks.{ext}")
    plt.close(fig)
    for f in ("kerr_ref_constf.png", "kerr_ref_hernquist.png", "kerr_ref_checks.png"):
        shutil.copy(out / f, figdir / f)
    print(json.dumps({k: v for k, v in res.items() if k not in ("digitized",)}, indent=1,
                     default=float))
    for k, v in cmp_.items():
        print(k, {kk: vv for kk, vv in v.items() if kk in ("peak_ours", "peak_digitized",
                                                          "maxabs_rel_dev", "median_rel_dev",
                                                          "range", "scale_digitized_over_ours",
                                                          "shape_maxabs_rel_dev_after_scale")})


if __name__ == "__main__":
    main()
