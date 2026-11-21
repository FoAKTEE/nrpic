#!/usr/bin/env python3
"""Outcome of tests T1 to T4 and T6 of tracks/core/JOURNAL-clump.md: reads the runs of
run_static.py, compares with predict.json and the closed forms, writes
static_check.json and the figures fig_clump_*.{pdf,png} next to this file.

    static_check.py --t1 RUN_ID --t3 RUN_ID --t4 RUN_ID --t6 RUN_ID
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mp_common import read_bin, read_hst, read_table_file  # noqa: E402
from nrpic import clumps as clm  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import smeared_bowen_york as sby  # noqa: E402

G = clm.GaussianClumps([dict(mass=0.2, sigma=1.0)])
NS = (32, 64, 128)


def load(run_id, which):
    with open(os.path.join(SCRATCH, run_id, f"cases_{which}.json")) as f:
        return json.load(f)["cases"]


def norms(case):
    h = case["hst0"]
    return dict(H=math.sqrt(h[3]), M=math.sqrt(h[4]), Mx=math.sqrt(h[6]),
                My=math.sqrt(h[7]), Mz=math.sqrt(h[8]))


def con(run_id, label, k=0):
    """constraint fields of dump k of a case: dict with x, y, z, dx and the variables"""
    t, par, x, y, z, dx, var = read_bin(os.path.join(SCRATCH, run_id, label, "bin",
                                                     f"clump.con.{k:05d}.bin"))
    return dict(t=t, x=x, y=y, z=z, dx=dx, **var)


def order(a, b):
    return math.log(a / b) / math.log(2.0)


RIN = 7.0     # interior: the outermost cells next to the outflow boundary are left out


def interior(run_id, label):
    """M-norm over the cells with r < RIN and over the rest, from the dump (the layer of
    cells at the outflow boundary carries a residual of its own: the ghost cells there
    are copies, so the derivative of K_ij is one-sided)"""
    d = con(run_id, label)
    X = np.stack([d["x"], d["y"], d["z"]], axis=-1)
    w = G.psi(X) ** 6 * d["dx"] ** 3 * d["con_M"]
    r = np.sqrt(np.sum(X * X, axis=-1))
    return float(math.sqrt(np.sum(w[r < RIN]))), float(math.sqrt(np.sum(w[r >= RIN])))


def curvature_term(run_id, lab_with, lab_without):
    """norm int psi^6 (M_x(with) - M_x(without))^2 of the curvature term alone, r < RIN"""
    d1, d0 = con(run_id, lab_with), con(run_id, lab_without)
    X = np.stack([d0["x"], d0["y"], d0["z"]], axis=-1)
    r = np.sqrt(np.sum(X * X, axis=-1))
    w = (G.psi(X) ** 6 * d0["dx"] ** 3 * (d1["con_Mx"] - d0["con_Mx"]) ** 2)[r < RIN]
    return float(math.sqrt(np.sum(w)))


def main():
    ap = argparse.ArgumentParser()
    for k in ("t1", "t3", "t4", "t6"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    with open(os.path.join(HERE, "predict.json")) as f:
        pred = json.load(f)
    c1, c3, c4, c6 = (load(getattr(a, k), k) for k in ("t1", "t3", "t4", "t6"))
    out = dict(runs=dict(t1=a.t1, t3=a.t3, t4=a.t4, t6=a.t6))
    ps = pred["single_clump"]

    # ---------------------------------------------------------------- T1 (a), (b)
    t1 = {}
    for filt, suf in (("filter4c", ""), ("filter0", "_f0")):
        rows = {}
        for n in NS:
            no, cu = norms(c1[f"t1_n{n}_none{suf}"]), norms(c1[f"t1_n{n}_curv{suf}"])
            ino, bno = interior(a.t1, f"t1_n{n}_none{suf}")
            icu, bcu = interior(a.t1, f"t1_n{n}_curv{suf}")
            rows[n] = dict(M_none=no["M"], M_curv=cu["M"], ratio=cu["M"] / no["M"],
                           Mx_none=no["Mx"], Mx_curv=cu["Mx"],
                           M_none_interior=ino, M_curv_interior=icu,
                           M_curv_boundary_layer=bcu, ratio_interior=icu / ino,
                           predicted_ratio=pred["lattice_deposit_error_over_field"][filt][f"n={n}"])
        t1[filt] = dict(rows=rows,
                        order_32_64=order(rows[32]["M_curv_interior"],
                                          rows[64]["M_curv_interior"]),
                        order_64_128=order(rows[64]["M_curv_interior"],
                                           rows[128]["M_curv_interior"]))
    t1["M_none_predicted"] = ps["by_momentum"]["P=0.06"]["M_norm_uncorrected"]
    t1["wrong_sign_over_none"] = (norms(c1["t1_n64_wrong"])["M"]
                                  / norms(c1["t1_n64_none"])["M"])
    # the curvature term by itself: sign and normalisation, independent of the deposit
    t1["curvature_term_Mx_norm"] = {
        "n=64": curvature_term(a.t1, "t1_n64_curv", "t1_n64_none"),
        "n=64 wrong sign": curvature_term(a.t1, "t1_n64_wrong", "t1_n64_none"),
        "n=128": curvature_term(a.t1, "t1_n128_curv", "t1_n128_none"),
        "predicted": ps["by_momentum"]["P=0.06"]["Mx_norm_uncorrected"]}
    sc = {}
    for P in ("0.02", "0.04"):
        sc[P] = dict(
            none_over_P006=norms(c1[f"t1_n128_P{P}_none"])["M"] / norms(c1["t1_n128_none"])["M"],
            curv_over_P006=norms(c1[f"t1_n128_P{P}_curv"])["M"] / norms(c1["t1_n128_curv"])["M"],
            expected=float(P) / 0.06)
    t1["scaling_with_P"] = sc
    nz = {}
    for N in ("1e4", "1e5", "1e6"):
        no, cu = norms(c1[f"t1_n64_str{N}_none"]), norms(c1[f"t1_n64_str{N}_curv"])
        key = f"N={int(float(N))}"
        nz[N] = dict(M_none=no["M"], M_curv=cu["M"],
                     poisson=pred["shot_noise_M_norm_dx0.25_P0.06"]["by_N"][key]["filter4c"],
                     sum_m_u=c1[f"t1_n64_str{N}_curv"]["particles"]["sum_m_u"])
    t1["equal_mass_samples_n64"] = nz
    out["T1"] = t1

    # ---------------------------------------------------------------- T2
    t2 = {}
    lines = {}
    for P in ("0.02", "0.04", "0.06"):
        tag = "" if P == "0.06" else f"_P{P}"
        d0 = con(a.t1, f"t1_n128{tag}_none")
        d1 = con(a.t1, f"t1_n128{tag}_curv")
        X = np.stack([d0["x"], d0["y"], d0["z"]], axis=-1)
        psi = G.psi(X)
        cf = -psi ** -12 * sby.abar2(X, [((0, 0, 0), 1.0, (float(P), 0, 0), (0, 0, 0))])
        diff = d1["con_H"] - d0["con_H"]
        dV = d0["dx"] ** 3
        t2[P] = dict(
            H_none_norm=norms(c1[f"t1_n128{tag}_none"])["H"],
            H_curv_norm=norms(c1[f"t1_n128{tag}_curv"])["H"],
            diff_norm=float(math.sqrt(np.sum(psi ** 6 * diff ** 2 * dV))),
            closed_form_norm=float(math.sqrt(np.sum(psi ** 6 * cf ** 2 * dV))),
            predicted_norm=ps["by_momentum"][f"P={float(P)}"]["H_norm_second_order"],
            max_abs_diff_minus_closed_form=float(np.abs(diff - cf).max()),
            closed_form_peak=float(np.abs(cf).max()),
            H_none_max=float(np.abs(d0["con_H"]).max()))
        sel = (np.abs(d0["y"] - 0.0625) < 1e-6) & (np.abs(d0["z"] - 0.0625) < 1e-6)
        o = np.argsort(d0["x"][sel])
        lines[P] = (d0["x"][sel][o], diff[sel][o], cf[sel][o], d0["con_H"][sel][o])
    out["T2"] = t2

    # ---------------------------------------------------------------- T3, T4
    for name, cs, key in (("T3", c3, "t3"), ("T4", c4, "t4")):
        rows = {}
        for n in NS:
            no, cu = norms(cs[f"{key}_n{n}_none"]), norms(cs[f"{key}_n{n}_curv"])
            ino, _ = interior(getattr(a, key), f"{key}_n{n}_none")
            icu, _ = interior(getattr(a, key), f"{key}_n{n}_curv")
            rows[n] = dict(M_none=no["M"], M_curv=cu["M"], ratio=cu["M"] / no["M"],
                           M_none_interior=ino, M_curv_interior=icu,
                           ratio_interior=icu / ino)
        out[name] = dict(rows=rows)
    out["T3"]["M_none_predicted"] = ps["spin"]["M_norm_uncorrected"]
    out["T4"]["predicted_ratio_n128"] = ps["velocity_rule_residual_over_uncorrected"]

    # ---------------------------------------------------------------- T6
    t6 = {}
    ev = {}
    for lab in ("t6_none", "t6_curv"):
        d = os.path.join(SCRATCH, a.t6, lab)
        h = read_hst(os.path.join(d, "clump.z4c.user.hst"))
        p = read_table_file(os.path.join(d, "clump.nrpic.hst"))
        ev[lab] = (h, p)
        tt = h["time"]
        t6[lab] = dict(
            t=[float(v) for v in tt], M_norm=[float(math.sqrt(v)) for v in h["M-norm2"]],
            H_norm=[float(math.sqrt(v)) for v in h["H-norm2"]],
            sum_mux_start=float(p[0, 5]), sum_mux_end=float(p[-1, 5]),
            t_end=float(p[-1, 0]), np_end=int(p[-1, 2]))
    r = np.array(t6["t6_curv"]["M_norm"]) / np.array(t6["t6_none"]["M_norm"])
    tt = np.array(t6["t6_none"]["t"])
    t6["ratio_curv_over_none_max_first_M"] = float(r[tt <= 1.0 + 1e-9].max())
    t6["ratio_curv_over_none_at_2M"] = float(r[-1])
    out["T6"] = t6

    with open(os.path.join(HERE, "static_check.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ================================================================ figures
    fs.use_style()
    blue, red, yel, grn, orange = fs.SERIES
    dxs = np.array([16.0 / n for n in NS])

    # ---- figure 1: residual against resolution, and against particle number
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.3))
    r4, r0 = t1["filter4c"]["rows"], t1["filter0"]["rows"]
    ax[0].plot(dxs, [r4[n]["M_none"] for n in NS], "o-", color=blue,
               label=r"$K_{ij}=0$")
    ax[0].plot(dxs, [r4[n]["M_curv_interior"] for n in NS], "s-", color=red,
               label="curvature, 4 passes + comp.")
    ax[0].plot(dxs, [r4[n]["predicted_ratio"] * t1["M_none_predicted"] for n in NS], "s",
               mfc="none", color=red, ms=10, label="predicted")
    ax[0].plot(dxs, [r0[n]["M_curv_interior"] for n in NS], "^-", color=yel,
               label="curvature, no filter")
    ax[0].plot(dxs[:2], [r0[n]["predicted_ratio"] * t1["M_none_predicted"] for n in NS[:2]],
               "^", mfc="none", color=yel, ms=10)
    ax[0].plot(dxs, [out["T4"]["rows"][n]["M_curv_interior"] for n in NS], "D-", color=grn,
               label="one velocity (first paper's rule)")
    ax[0].plot(dxs, [out["T3"]["rows"][n]["M_curv_interior"] for n in NS], "v--", color=orange,
               label="spin, curvature")
    ax[0].plot(dxs, [out["T3"]["rows"][n]["M_none"] for n in NS], "v:", color=orange,
               label=r"spin, $K_{ij}=0$")
    xx = np.array([0.27, 0.5])
    ax[0].plot(xx, 4e-6 * (xx / 0.27) ** 2, **fs.THIN)
    ax[0].plot(xx, 4e-7 * (xx / 0.27) ** 4, **fs.THIN)
    ax[0].text(0.52, 1.1e-5, r"$\Delta x^2$", fontsize=9)
    ax[0].text(0.52, 3.5e-6, r"$\Delta x^4$", fontsize=9)
    ax[0].set_xlim(0.105, 0.68)
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xticks(dxs)
    ax[0].set_xticklabels(["0.5", "0.25", "0.125"])
    ax[0].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax[0].set_xlabel(r"cell size $\Delta x/\sigma$")
    ax[0].set_ylabel(r"momentum-constraint norm $\|\mathcal{M}\|$")
    fig.legend(*ax[0].get_legend_handles_labels(), fontsize=8, loc="lower center",
               ncol=4, frameon=False)
    Ns = np.array([1e4, 1e5, 1e6])
    ax[1].plot(Ns, [nz[k]["M_none"] for k in ("1e4", "1e5", "1e6")], "o-", color=blue,
               label=r"$K_{ij}=0$")
    ax[1].plot(Ns, [nz[k]["M_curv"] for k in ("1e4", "1e5", "1e6")], "s-", color=red,
               label="curvature")
    ax[1].plot(Ns, [nz[k]["poisson"] for k in ("1e4", "1e5", "1e6")], **fs.GUIDE,
               label="Poisson noise (predicted)")
    ax[1].axhline(r4[64]["M_curv_interior"], **fs.MASK_LINE)
    ax[1].text(1.2e4, r4[64]["M_curv_interior"] * 0.78,
               "lattice particles (continuum part)", fontsize=8)
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("equal-mass particles $N$")
    ax[1].set_ylabel(r"$\|\mathcal{M}\|$ at $\Delta x=0.25\,\sigma$")
    ax[1].legend(fontsize=8, frameon=False, loc="center right")
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fs.save(fig, os.path.join(HERE, "figs", "fig_clump_convergence"))
    plt.close(fig)

    # ---- figure 2: slices of M_x
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9), sharey=True)
    panels = (("t1_n64_none", 1.0, r"$K_{ij}=0$"), ("t1_n64_curv", 1.0, "curvature"),
              ("t1_n64_curv", 20.0, r"curvature, $\times 20$"))
    vmax = None
    for axx, (lab, fac, title) in zip(ax, panels):
        d = con(a.t1, lab)
        sel = np.abs(d["z"] - 0.125) < 1e-6
        n1 = int(round(math.sqrt(sel.sum())))
        o = np.lexsort((d["x"][sel], d["y"][sel]))
        img = d["con_Mx"][sel][o].reshape(n1, n1) * fac
        if vmax is None:
            vmax = np.abs(img).max()
        im = axx.imshow(img, origin="lower", extent=(-8, 8, -8, 8), cmap="RdBu_r",
                        vmin=-vmax, vmax=vmax)
        axx.set_xlim(-5, 5)
        axx.set_ylim(-5, 5)
        axx.set_title(title, fontsize=10)
        axx.set_xlabel(r"$x/\sigma$")
    ax[0].set_ylabel(r"$y/\sigma$")
    fig.colorbar(im, ax=ax, shrink=0.85, label=r"$\mathcal{M}_x$", pad=0.02)
    fs.save(fig, os.path.join(HERE, "figs", "fig_clump_slices"))
    plt.close(fig)

    # ---- figure 3: Hamiltonian residual at second order
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for P, col in zip(("0.02", "0.04", "0.06"), (blue, yel, red)):
        x, diff, cf, h0 = lines[P]
        ax[0].plot(x, cf, color=col, lw=1.2, label=f"closed form, $P={P}$")
        ax[0].plot(x[::2], diff[::2], "o", color=col, ms=2.5)
    x, diff, cf, h0 = lines["0.06"]
    ax[0].plot(x, h0, color="grey", lw=1.0, ls=":", label=r"$\mathcal{H}$ with $K_{ij}=0$")
    ax[0].set_xlim(-6, 6)
    ax[0].set_ylim(-9.0e-4, 1.3e-3)
    ax[0].set_xlabel(r"$x/\sigma$ (line $y=z=\Delta x/2$)")
    ax[0].set_ylabel(r"$\mathcal{H}(\mathrm{curvature})-\mathcal{H}(K_{ij}=0)$")
    ax[0].legend(fontsize=7, frameon=False, loc="upper left", ncol=2)
    Pv = np.array([0.02, 0.04, 0.06])
    ax[1].plot(Pv, [t2[k]["diff_norm"] for k in ("0.02", "0.04", "0.06")], "o", color=red,
               label="measured")
    ax[1].plot(Pv, [t2[k]["predicted_norm"] for k in ("0.02", "0.04", "0.06")], "s",
               mfc="none", color="k", ms=10, label="predicted")
    pp = np.linspace(0.015, 0.075, 50)
    ax[1].plot(pp, t2["0.06"]["predicted_norm"] * (pp / 0.06) ** 2, **fs.GUIDE,
               label=r"$\propto P^2$")
    ax[1].axhline(t2["0.06"]["H_none_norm"], **fs.MASK_LINE)
    ax[1].text(0.016, t2["0.06"]["H_none_norm"] * 0.68,
               r"$\|\mathcal{H}\|$ with $K_{ij}=0$ (cloud and filter)", fontsize=8)
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xticks([0.02, 0.04, 0.06])
    ax[1].set_xticklabels(["0.02", "0.04", "0.06"])
    ax[1].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax[1].set_ylim(3.0e-4, 3.0e-2)
    ax[1].set_xlabel("momentum $P$ ($m=0.2$, $\\sigma=1$)")
    ax[1].set_ylabel(r"$\|\mathcal{H}(\mathrm{curv.})-\mathcal{H}(K_{ij}=0)\|$")
    ax[1].legend(fontsize=8, frameon=False, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(HERE, "figs", "fig_clump_hamiltonian"))
    plt.close(fig)

    # ---- figure 4: evolution
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    for lab, col, name in (("t6_none", blue, r"$K_{ij}=0$"), ("t6_curv", red, "curvature")):
        h, p = ev[lab]
        ax[0].plot(h["time"], np.sqrt(h["M-norm2"]), color=col, label=name)
        ax[1].plot(h["time"], np.sqrt(h["H-norm2"]), color=col, label=name)
        ax[2].plot(p[:, 0], p[:, 5] / p[0, 5] - 1.0, color=col, label=name)
    ax[0].set_yscale("log")
    ax[1].set_yscale("log")
    for axx, yl in zip(ax, (r"$\|\mathcal{M}\|$", r"$\|\mathcal{H}\|$",
                            r"$\sum m u_x/P - 1$")):
        axx.set_xlabel("$t$")
        axx.set_ylabel(yl)
    ax[0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(HERE, "figs", "fig_clump_evolution"))
    plt.close(fig)

    # ---------------------------------------------------------------- report
    print("T1 momentum constraint, P = 0.06 (predicted uncorrected norm "
          f"{t1['M_none_predicted']:.4f})")
    for filt in ("filter4c", "filter0"):
        for n in NS:
            r_ = t1[filt]["rows"][n]
            print(f"  {filt:8s} n={n:3d}  none {r_['M_none']:.5e}  curv {r_['M_curv']:.5e}  "
                  f"ratio {r_['ratio']:.3e}  interior: curv {r_['M_curv_interior']:.5e} "
                  f"ratio {r_['ratio_interior']:.3e} (boundary layer "
                  f"{r_['M_curv_boundary_layer']:.3e})  predicted {r_['predicted_ratio']:.3e}")
        print(f"  {filt:8s} orders {t1[filt]['order_32_64']:.2f}, "
              f"{t1[filt]['order_64_128']:.2f}")
    print(f"  wrong sign / none at n=64: {t1['wrong_sign_over_none']:.5f}")
    print("  curvature term alone, Mx-norm:", t1["curvature_term_Mx_norm"])
    for P, v in sc.items():
        print(f"  P={P}: none/none(0.06) {v['none_over_P006']:.5f}, curv/curv(0.06) "
              f"{v['curv_over_P006']:.5f}, expected {v['expected']:.5f}")
    for N, v in nz.items():
        print(f"  N={N}: none {v['M_none']:.5e} curv {v['M_curv']:.5e} "
              f"Poisson {v['poisson']:.5e}")
    print("T2 Hamiltonian residual")
    for P, v in t2.items():
        print(f"  P={P}: diff norm {v['diff_norm']:.5e} closed form {v['closed_form_norm']:.5e} "
              f"predicted {v['predicted_norm']:.5e}; max|diff - cf| "
              f"{v['max_abs_diff_minus_closed_form']:.2e} of peak {v['closed_form_peak']:.4e}; "
              f"H none {v['H_none_norm']:.4e}, H curv {v['H_curv_norm']:.4e}")
    for name in ("T3", "T4"):
        print(name, {k: v for k, v in out[name].items() if k != "rows"})
        for n in NS:
            r_ = out[name]["rows"][n]
            print(f"  n={n:3d} none {r_['M_none']:.5e} curv {r_['M_curv']:.5e} "
                  f"ratio {r_['ratio']:.3e}; interior curv {r_['M_curv_interior']:.5e} "
                  f"ratio {r_['ratio_interior']:.3e}")
    print("T6", {k: v for k, v in t6.items() if not k.startswith("t6_")})
    for lab in ("t6_none", "t6_curv"):
        v = t6[lab]
        print(f"  {lab}: M-norm at t = 0, 0.5, 1, 2: "
              + ", ".join(f"{v['M_norm'][i]:.4e}" for i in (0, 4, 8, len(v["M_norm"]) - 1))
              + f"; sum m u_x {v['sum_mux_start']:.6e} -> {v['sum_mux_end']:.6e} "
              f"(t = {v['t_end']:.3f}, np = {v['np_end']})")


if __name__ == "__main__":
    main()
