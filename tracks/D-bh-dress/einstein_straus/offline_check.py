#!/usr/bin/env python3
"""Offline constraint check of the Einstein-Straus black-hole data (D-pre-1), with
measured convergence.

    offline_check.py --out DIR [--tab TABLE] [model options as make_es.py]

1D: Hamiltonian and radial momentum residuals of the exact fields (es_model) in the
    conformally flat radial form, fourth-order differences at spacing h = 0.1, 0.05,
    0.025 M (stencils sampled from the model, so only truncation error enters):
        H = -8 psi^-5 (psi'' + 2 psi'/rbar) + 4 KL KT + 2 KT^2 - 16 pi rho
        M = 2 [(2 psi'/psi + 1/rbar)(KL - KT) - KT']
3D: generic 3+1 residuals on Cartesian sub-boxes, gamma_ij = psi^4 delta_ij and
    K_ij = psi^4 [KT delta_ij + (KL - KT) n_i n_j], Christoffels and Ricci tensor by
    fourth-order differences of gamma_ij (the conformal-flatness identity is not used),
        H = (3)R + K^2 - K_ij K^ij - 16 pi rho,   M_i = D_j K^j_i - D_i K,
    with the fields from the exact model ("exact") and from the format-2 table evaluated
    as nrpic_cf evaluates it plus the puncture term ("table"), at h = 1, 1/2, 1/4 M
    (finer near the throat).
Table: interpolation error of the table columns against the exact fields at midpoints.
Writes DIR/offline_check.json and the figures figs/check_1d.(png,pdf), figs/check_3d.(png,pdf).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))
import es_model as em  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

FIGS = os.path.join(HERE, "figs")


def model_from_args(a):
    return em.EinsteinStrausBH(M=a.M, Rw=a.Rw, w_in=a.w_in, Rb=a.Rb, w_out=a.w_out,
                               R0=a.R0, R1=a.R1)


def add_model_args(ap):
    ap.add_argument("--M", type=float, default=1.0)
    ap.add_argument("--Rw", type=float, default=40.0)
    ap.add_argument("--w_in", type=float, default=4.0)
    ap.add_argument("--Rb", type=float, default=100.0)
    ap.add_argument("--w_out", type=float, default=6.0)
    ap.add_argument("--R0", type=float, default=4.0)
    ap.add_argument("--R1", type=float, default=None)


# ------------------------------------------------------------------ 1D
def residual_1d(model, r, h):
    """H, M and their term scales at radii r with stencil spacing h. Differences use
    integer weights on psi - psi(r) and KT - KT(r) before the division by h (round-off)."""
    off = np.arange(-2, 3)
    rr = r[:, None] + h * off[None, :]
    p = model.profiles(rr.ravel())
    psi = p["psi"].reshape(rr.shape)
    KT = p["KT"].reshape(rr.shape)
    psi = psi - psi[:, 2:3]
    KTd = KT - KT[:, 2:3]
    w1 = np.array([1.0, -8.0, 0.0, 8.0, -1.0])
    w2 = np.array([-1.0, 16.0, -30.0, 16.0, -1.0])
    dpsi = (psi @ w1) / (12.0 * h)
    ddpsi = (psi @ w2) / (12.0 * h * h)
    dKT = (KTd @ w1) / (12.0 * h)
    pc = model.profiles(r)
    ps, KL, KTc, rho = pc["psi"], pc["KL"], pc["KT"], pc["rho"]
    lap1, lap2 = -8.0 * ps ** -5 * ddpsi, -16.0 * ps ** -5 * dpsi / r
    kk1, kk2 = 4.0 * KL * KTc, 2.0 * KTc ** 2
    src = 16.0 * math.pi * rho
    H = lap1 + lap2 + kk1 + kk2 - src
    Hs = np.abs(lap1) + np.abs(lap2) + np.abs(kk1) + kk2 + src
    g1 = 2.0 * dpsi / ps * (KL - KTc)
    g2 = (KL - KTc) / r
    M = 2.0 * (g1 + g2 - dKT)
    Ms = 2.0 * (np.abs(g1) + np.abs(g2) + np.abs(dKT) + np.abs(KTc) / r)
    return H, M, Hs, Ms


def regions(model):
    """(name, rbar range, spacings): spacings resolve the local scale of each region."""
    return [("puncture region", 0.3, model.rbar0 - 0.05, (0.04, 0.02, 0.01, 0.005)),
            ("curvature transition", model.rbar0 + 0.05, model.R1 - 0.05, (0.8, 0.4, 0.2, 0.1)),
            ("inner dust edge", model.Rin, model.Rw + model.w_in, (0.8, 0.4, 0.2, 0.1)),
            ("EdS plateau", model.Rw + model.w_in, model.Rb - model.w_out, (0.8, 0.4, 0.2, 0.1)),
            ("outer dust edge", model.Rb - model.w_out, model.Rout, (0.8, 0.4, 0.2, 0.1)),
            ("Schwarzschild exterior", model.Rout, 1.4 * model.Rout, (0.8, 0.4, 0.2, 0.1))]


def check_1d(model):
    out = {"regions": {}}
    curves = {}
    for name, lo, hi, hs in regions(model):
        r = np.linspace(lo, hi, 1500)
        rec = {"range": [lo, hi], "h": list(hs)}
        cur = {h: residual_1d(model, r, h) for h in hs}
        curves[name] = (r, hs, cur)
        for key, idx, sidx in (("H", 0, 2), ("M", 1, 3)):
            scale = float(np.max(cur[hs[0]][sidx]))
            nrm = [float(np.max(np.abs(cur[h][idx]))) for h in hs]
            orders = [math.log2(nrm[i] / nrm[i + 1]) if nrm[i + 1] > 0 else float("inf")
                      for i in range(len(hs) - 1)]
            rec[key] = {"max_abs": nrm, "term_scale": scale,
                        "max_rel": [n / scale if scale > 0 else 0.0 for n in nrm], "order": orders}
        out["regions"][name] = rec
    return out, curves


# ------------------------------------------------------------------ 3D
def d1(f, h, axis):
    return (np.roll(f, 2, axis) - 8.0 * np.roll(f, 1, axis) + 8.0 * np.roll(f, -1, axis)
            - np.roll(f, -2, axis)) / (12.0 * h)


def fields_3d(model, X, Y, Z, source, tab=None):
    r = np.sqrt(X * X + Y * Y + Z * Z)
    if source == "exact":
        p = model.profiles(r.ravel())
        psi = p["psi"].reshape(r.shape)
        KL = p["KL"].reshape(r.shape)
        KT = p["KT"].reshape(r.shape)
    else:
        e = tab.evaluate(r.ravel())
        psi = 1.0 + e["u"].reshape(r.shape) + 0.5 * model.m_p / r
        KL = e["KL"].reshape(r.shape)
        KT = e["KT"].reshape(r.shape)
    rho = model.profiles(r.ravel())["rho"].reshape(r.shape)
    n = np.stack([X / r, Y / r, Z / r])
    psi4 = psi ** 4
    g = np.zeros((3, 3) + r.shape)
    K = np.zeros((3, 3) + r.shape)
    for i in range(3):
        g[i, i] = psi4
        for j in range(3):
            K[i, j] = psi4 * ((KT if i == j else 0.0) + (KL - KT) * n[i] * n[j])
    return g, K, rho


def residual_3d(model, centre, half, h, source, tab=None, ng=4):
    n = int(round(2 * half / h)) + 1
    ax = [centre[d] + h * (np.arange(-ng, n + ng) - (n - 1) / 2.0) for d in range(3)]
    X, Y, Z = np.meshgrid(*ax, indexing="ij")
    g, K, rho = fields_3d(model, X, Y, Z, source, tab)
    sh = X.shape
    gi = np.moveaxis(np.linalg.inv(np.moveaxis(g, (0, 1), (-2, -1))), (-2, -1), (0, 1))
    dg = np.stack([d1(g, h, 2 + k) for k in range(3)])               # dg[k,i,j] = d_k g_ij
    # Gamma^k_ij = 1/2 g^kl (d_i g_lj + d_j g_li - d_l g_ij)
    t = np.einsum("ilj...->lij...", dg) + np.einsum("jli...->lij...", dg) - dg   # [l,i,j]
    Gam = 0.5 * np.einsum("kl...,lij...->kij...", gi, t)
    dGam = np.stack([d1(Gam, h, 3 + m) for m in range(3)])           # dGam[m,k,i,j] = d_m Gamma^k_ij
    Ric = (np.einsum("kkij...->ij...", dGam)
           - np.einsum("jkik...->ij...", dGam)
           + np.einsum("kkl...,lij...->ij...", Gam, Gam)
           - np.einsum("kjl...,lik...->ij...", Gam, Gam))
    Rs = np.einsum("ij...,ij...->...", gi, Ric)
    Km = np.einsum("ik...,kj...->ij...", gi, K)                       # K^i_j
    trK = np.einsum("ii...->...", Km)
    KK = np.einsum("ij...,ji...->...", Km, Km)
    H = Rs + trK ** 2 - KK - 16.0 * math.pi * rho
    Ru = np.einsum("ik...,jl...,kl...->ij...", gi, gi, Ric)            # R^ij
    Hs = np.sqrt(np.abs(np.einsum("ij...,ij...->...", Ric, Ru))) + trK ** 2 + np.abs(KK) \
        + 16.0 * math.pi * rho                                         # |Ric| + K terms + matter
    dKm = np.stack([d1(Km, h, 2 + m) for m in range(3)])             # dKm[m,i,j] = d_m K^i_j
    dtr = np.stack([d1(trK, h, m) for m in range(3)])
    t1 = np.einsum("jji...->i...", dKm)                                # d_j K^j_i
    t2 = np.einsum("jjl...,li...->i...", Gam, Km)                      # Gamma^j_jl K^l_i
    t3 = np.einsum("lji...,jl...->i...", Gam, Km)                      # Gamma^l_ji K^j_l
    Mi = t1 + t2 - t3 - dtr
    Ms = np.abs(t1) + np.abs(t2) + np.abs(t3) + np.abs(dtr)
    sl = (slice(ng, ng + n),) * 3
    H, Hs = H[sl], Hs[sl]
    Mn = np.sqrt(np.sum(Mi[(slice(None),) + sl] ** 2, axis=0))
    Msn = np.sqrt(np.sum(Ms[(slice(None),) + sl] ** 2, axis=0))
    return dict(H_max=float(np.max(np.abs(H))), H_rms=float(np.sqrt(np.mean(H ** 2))),
                Hscale_max=float(np.max(Hs)), M_max=float(np.max(Mn)),
                M_rms=float(np.sqrt(np.mean(Mn ** 2))), Mscale_max=float(np.max(Msn)), n=n)


def boxes(model):
    u = np.array([0.6, 0.64, 0.48])                   # a generic direction, |u| = 1
    rt = model.rbar_throat
    return [("throat", 1.6 * rt * u, 0.5 * rt, (1 / 16, 1 / 32, 1 / 64)),
            ("puncture region", 2.0 * u, 0.75, (1 / 8, 1 / 16, 1 / 32)),
            ("start of transition", (model.rbar0 + 1.5) * u, 1.5, (1 / 4, 1 / 8, 1 / 16)),
            ("mid transition", 0.5 * (model.rbar0 + model.R1) * u, 4.0, (1.0, 0.5, 0.25)),
            ("inner dust edge", model.Rw * u, 4.0, (0.5, 0.25, 0.125)),
            ("outer dust edge", model.Rb * u, 4.0, (0.5, 0.25, 0.125)),
            ("end of table / exterior", 1.17 * model.Rout * u, 8.0, (1.0, 0.5, 0.25))]


def check_3d(model, tab):
    out = {}
    for name, c, half, hs in boxes(model):
        rec = {"centre": list(map(float, c)), "half_width": half, "h": list(hs)}
        for source in ("exact", "table"):
            res = [residual_3d(model, c, half, h, source, tab) for h in hs]
            rec[source] = res
            for key in ("H_max", "M_max", "H_rms", "M_rms"):
                v = [x[key] for x in res]
                rec[source][0].setdefault("orders", {})[key] = [
                    math.log2(v[i] / v[i + 1]) if v[i + 1] > 0 else float("inf") for i in range(len(v) - 1)]
        out[name] = rec
        fmt = lambda v: "[" + ", ".join("%.2e" % x for x in v) + "]"
        ordr = lambda v: "[" + ", ".join("%.2f" % x for x in v) + "]"
        ex, tb = rec["exact"], rec["table"]
        print("3D %-26s exact H_max %s orders %s; M_max %s orders %s" % (
            name, fmt([x["H_max"] for x in ex]), ordr(ex[0]["orders"]["H_max"]),
            fmt([x["M_max"] for x in ex]), ordr(ex[0]["orders"]["M_max"])))
        print("   %-26s table H_max %s orders %s; M_max %s orders %s" % (
            "", fmt([x["H_max"] for x in tb]), ordr(tb[0]["orders"]["H_max"]),
            fmt([x["M_max"] for x in tb]), ordr(tb[0]["orders"]["M_max"])))
    return out


# ------------------------------------------------------------------ table
def check_table(model, tab):
    r = 0.5 * (tab.rbar[:-1] + tab.rbar[1:])
    e = tab.evaluate(r)
    p = model.profiles(r)
    out = {}
    for k in ("u", "KL", "KT", "alpha", "betar"):
        err = np.abs(e[k] - p[k])
        scale = np.max(np.abs(p[k])) if np.max(np.abs(p[k])) > 0 else 1.0
        out[k] = {"max_abs": float(np.max(err)), "max_rel_to_column_max": float(np.max(err) / scale),
                  "at_rbar": float(r[np.argmax(err)])}
    # continuation beyond the last row against the exact exterior
    rx = np.linspace(tab.rbar[-1], 3.0 * tab.rbar[-1], 400)
    e = tab.evaluate(rx)
    p = model.profiles(rx)
    out["exterior"] = {k: float(np.max(np.abs(e[k] - p[k]))) for k in ("u", "KL", "KT", "betar")}
    return out


# ------------------------------------------------------------------ figures
def fig_1d(model, curves):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 6.0), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.09, top=0.96, hspace=0.06)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"]]
    for ax, idx, sidx, lab in ((axs[0], 0, 2, r"$|\mathcal{H}|\,(h_0/h)^4$ / term scale"),
                               (axs[1], 1, 3, r"$|\mathcal{M}_r|\,(h_0/h)^4$ / term scale")):
        for name, (r, hs, cur) in curves.items():
            sc = np.max(cur[hs[0]][sidx])
            if not sc > 0:
                continue
            for k, (h, c) in enumerate(zip(hs, cols)):
                y = np.abs(cur[h][idx]) * (hs[0] / h) ** 4 / sc
                ax.semilogy(r, np.maximum(y, 1e-20), color=c, lw=1.0,
                            label=(f"$h = h_0/{2 ** k}$" if name == "puncture region" else None))
        for x in (model.rbar_throat, model.rbar0, model.R1, model.Rw, model.Rb, model.Rout):
            ax.axvline(x, **fs.MASK_LINE)
        ax.set_xscale("log")
        ax.set_ylabel(lab)
        ax.set_ylim(1e-18, 1e-3)
    h_, l_ = axs[0].get_legend_handles_labels()
    axs[1].legend(h_, l_, loc="lower left", ncol=2)
    axs[1].set_xlabel(r"$\bar r / M$")
    axs[0].text(0.02, 0.9, r"$h_0 = 0.04\,M$ for $\bar r < \bar r_0$, $0.8\,M$ beyond; "
                r"coinciding curves: fourth order", transform=axs[0].transAxes)
    fs.save(fig, os.path.join(FIGS, "check_1d"))


def fig_3d(res3):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.95, wspace=0.25)
    cols = fs.series_colors(len(res3))
    for (name, rec), c in zip(res3.items(), cols):
        hs = np.array(rec["h"])
        for ax, key, skey in ((axs[0], "H_max", "Hscale_max"), (axs[1], "M_max", "Mscale_max")):
            if not all(x[skey] > 0 for x in rec["exact"]):
                continue
            ve = np.array([x[key] / x[skey] for x in rec["exact"]])
            vt = np.array([x[key] / x[skey] for x in rec["table"]])
            ax.loglog(hs, ve, "o-", color=c, label=name)
            ax.loglog(hs, vt, "x--", color=c, lw=1.0)
            ax.loglog(hs, ve[0] * (hs / hs[0]) ** 4, **dict(fs.GUIDE, lw=0.8))
    axs[0].set_ylabel(r"max $|\mathcal{H}|$ / max term")
    axs[1].set_ylabel(r"max $|\mathcal{M}|$ / max term")
    for ax in axs:
        ax.set_xlabel(r"$h / M$")
    axs[0].legend(loc="center left", fontsize=7, ncol=1)
    axs[1].text(0.03, 0.92, "o exact fields, x table + puncture, dashed: $h^4$",
                transform=axs[1].transAxes, fontsize=8)
    fs.save(fig, os.path.join(FIGS, "check_3d"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tab", default=None, help="format-2 table to check (default: generate)")
    ap.add_argument("--drbar", type=float, default=0.02)
    ap.add_argument("--skip3d", action="store_true")
    add_model_args(ap)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    model = model_from_args(a)
    if a.tab:
        tab, _ = em.read_tab2(a.tab)
    else:
        tab = model.table(drbar=a.drbar)
    res = {"model": model.summary()}
    r1, curves = check_1d(model)
    res["check_1d"] = r1
    for name, rec in r1["regions"].items():
        print(f"1D {name:24s} H rel {['%.1e' % v for v in rec['H']['max_rel']]} order "
              f"{['%.2f' % v for v in rec['H']['order']]} | M rel {['%.1e' % v for v in rec['M']['max_rel']]} "
              f"order {['%.2f' % v for v in rec['M']['order']]}")
    fig_1d(model, curves)
    res["table"] = check_table(model, tab)
    print("table interpolation:", json.dumps(res["table"], indent=None))
    if not a.skip3d:
        res["check_3d"] = check_3d(model, tab)
        fig_3d(res["check_3d"])
    with open(os.path.join(a.out, "offline_check.json"), "w") as fo:
        json.dump(res, fo, indent=1)
    print("wrote", os.path.join(a.out, "offline_check.json"))


if __name__ == "__main__":
    main()
