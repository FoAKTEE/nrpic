#!/usr/bin/env python3
"""Verifier check C1 (D-pre-1): the vacuum-bubble slice, from the format-2 table alone.

Independent of the track's es_model / offline_check: reads only the rows of es.tab and
the bare puncture mass m_p from its header, and recomputes, with its own formulas and
finite differences on the table rows (spacing h = k * drbar, k = 1, 2, 4, 8):

  psi = 1 + u + m_p/(2 rbar);  R = psi^2 rbar;  W = dR/dl = 1 + 2 rbar psi'/psi
  Misner-Sharp mass  m = (R/2) (1 - W^2 + R^2 KT^2)
  density from the Hamiltonian constraint
      16 pi rho_H = -8 psi^-5 (u'' + 2 u'/rbar) + 4 KL KT + 2 KT^2
  radial momentum constraint (S_l = 0: dust at rest in the slice)
      Mom = (KL - KT) (1/rbar + 2 psi'/psi) - dKT/drbar
  expansions theta_pm = (2/R)(pm W - R KT) of the outgoing/ingoing null normals

Negative control: KL replaced by KT in the vacuum transition (a wrong curvature) must
produce a momentum residual that does not converge away.
Also: the exact references of es_reference.csv against my closed forms, and the
Einstein-Straus scales of SCOPE.md section 4.

Usage: v1_es_slice.py --data <run dir of make_es.py> --out <dir> [--figdir DIR]
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def read_tab(path):
    hdr = {}
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                s = line[1:].strip()
                if "=" in s:
                    k, v = s.split("=", 1)
                    hdr[k.strip()] = v.strip()
            elif line.strip():
                rows.append([float(x) for x in line.split()])
    return hdr, np.array(rows)


def d1(f, h):
    """4th-order central first derivative on interior points (NaN at the ends)."""
    g = np.full_like(f, np.nan)
    g[2:-2] = (f[:-4] - 8 * f[1:-3] + 8 * f[3:-1] - f[4:]) / (12 * h)
    return g


def d2(f, h):
    g = np.full_like(f, np.nan)
    g[2:-2] = (-f[:-4] + 16 * f[1:-3] - 30 * f[2:-2] + 16 * f[3:-1] - f[4:]) / (12 * h * h)
    return g


def fields(rb, u, KL, KT, mp, h):
    psi = 1 + u + mp / (2 * rb)
    up, upp = d1(u, h), d2(u, h)
    psip = up - mp / (2 * rb ** 2)
    R = psi ** 2 * rb
    W = 1 + 2 * rb * psip / psi
    m = 0.5 * R * (1 - W ** 2 + R ** 2 * KT ** 2)
    rhoH = (-8 * psi ** -5 * (upp + 2 * up / rb) + 4 * KL * KT + 2 * KT ** 2) / (16 * math.pi)
    mom = (KL - KT) * (1 / rb + 2 * psip / psi) - d1(KT, h)
    thp = (2 / R) * (W - R * KT)
    thm = (2 / R) * (-W - R * KT)
    return dict(psi=psi, R=R, W=W, m=m, rhoH=rhoH, mom=mom, thp=thp, thm=thm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    hdr, T = read_tab(os.path.join(a.data, "es.tab"))
    meta = json.load(open(os.path.join(a.data, "es.json")))["summary"]
    rb_all, u_all, KL_all, KT_all = T[:, 0], T[:, 1], T[:, 2], T[:, 3]
    drb = rb_all[1] - rb_all[0]
    mp = float(meta["m_p"])
    M = float(meta["M"])
    res = {"m_p": mp, "drbar": drb, "rows": len(rb_all)}

    # --- convergence over spacings h = k drbar (subsampled rows, no interpolation) ---
    regions = {}
    levels = {}
    for k in (1, 2, 4, 8):
        sl = slice(0, None, k)
        rb, u, KL, KT = rb_all[sl], u_all[sl], KL_all[sl], KT_all[sl]
        F = fields(rb[1:], u[1:], KL[1:], KT[1:], mp, k * drb)  # drop rbar = 0
        F["rb"] = rb[1:]
        levels[k] = F
    F = levels[1]
    rb = F["rb"]
    R = F["R"]
    ok = np.isfinite(F["m"])
    # where is the matter? (density from the Hamiltonian constraint, finest level)
    rho = F["rhoH"]
    i_th = np.nanargmin(np.where(ok, np.abs(F["W"]), np.inf))
    res["throat"] = {"rbar": float(rb[i_th]), "R": float(R[i_th]), "W": float(F["W"][i_th]),
                     "predicted_rbar_b_over_a": float(meta["b"] / meta["a"])}
    # regions in areal radius R on the outer sheet (rbar > throat)
    outer = ok & (rb > rb[i_th])
    reg_def = {"puncture_inner_sheet": ok & (rb < rb[i_th]) & (rb > 0.1),
               "time_symmetric_outer": outer & (R < 4.0),
               "transition_vacuum": outer & (R > 4.0) & (R < 35.5),
               "inner_dust_edge": outer & (R > 36.5) & (R < 43.5),
               "plateau": outer & (R > 45) & (R < 93),
               "outer_dust_edge": outer & (R > 94) & (R < 106),
               "exterior_in_table": outer & (R > 107)}
    for name, msk in reg_def.items():
        d = {"n": int(msk.sum()), "R_range": [float(np.nanmin(R[msk])), float(np.nanmax(R[msk]))]}
        mm = F["m"][msk]
        d["m_min"], d["m_max"] = float(np.nanmin(mm)), float(np.nanmax(mm))
        d["rhoH_min"], d["rhoH_max"] = float(np.nanmin(rho[msk])), float(np.nanmax(rho[msk]))
        # convergence of the momentum residual and of the Hamiltonian density (Richardson)
        momk, rhok = {}, {}
        for k, Fk in levels.items():
            mk = np.interp(Fk["rb"], rb, msk.astype(float)) > 0.5
            momk[k] = float(np.nanmax(np.abs(Fk["mom"][mk]))) if mk.any() else float("nan")
            rhok[k] = Fk
        d["max_abs_mom"] = momk
        d["mom_order"] = {f"{k}->{k//2}": float(math.log2(momk[k] / momk[k // 2]))
                          for k in (2, 4, 8) if momk[k] > 0 and momk[k // 2] > 0}
        # Richardson differences of rho_H between successive levels on the common rows
        diffs = {}
        for k in (1, 2, 4):
            F1, F2 = levels[k], levels[2 * k]
            r_c = F2["rb"]
            v1 = np.interp(r_c, F1["rb"], F1["rhoH"])
            mk = np.interp(r_c, rb, msk.astype(float)) > 0.5
            dd = np.abs(F2["rhoH"] - v1)[mk]
            diffs[k] = float(np.nanmax(dd)) if mk.any() else float("nan")
        d["rhoH_diff_levels"] = diffs
        d["rhoH_order"] = {f"{2*k}-{k}": float(math.log2(diffs[2 * k] / diffs[k]))
                           for k in (1, 2) if diffs[k] > 0 and diffs[2 * k] > 0}
        regions[name] = d
    res["regions"] = regions

    # --- the plateau: Einstein-de Sitter, H^2 = 8 pi rho0/3 = -KT, m = H^2 R^3/2 -------
    pl = reg_def["plateau"]
    H_KT = float(np.nanmedian(-KT_all[1:][pl]))
    H_KL = float(np.nanmedian(-KL_all[1:][pl]))
    rho0 = float(np.nanmedian(rho[pl]))
    res["plateau"] = {"H_from_KT": H_KT, "H_from_KL": H_KL, "H_from_rho": math.sqrt(8 * math.pi * rho0 / 3),
                      "H_json": meta["H"], "rho0_H": rho0, "rho0_json": meta["rho0"],
                      "max_rel_dev_m_vs_H2R3over2_minus_const": None}
    # in the plateau m(R) = M_eff + (4 pi/3) rho0 R^3 with M_eff the "removed" mass: ES
    # matching says M_eff = 0 (dust mass removed = M), i.e. m = H^2 R^3 / 2 exactly
    m_pl = F["m"][pl]
    Rpl = R[pl]
    res["plateau"]["m_minus_H2R3over2_range"] = [float(np.nanmin(m_pl - H_KT ** 2 * Rpl ** 3 / 2)),
                                                 float(np.nanmax(m_pl - H_KT ** 2 * Rpl ** 3 / 2))]
    res["plateau"]["R_w_eff_from_H"] = (2 * M / H_KT ** 2) ** (1 / 3)
    # anti-trapped spheres: both expansions positive
    both = ok & (F["thp"] > 0) & (F["thm"] > 0)
    res["anti_trapped_rows"] = int(both.sum())
    res["max_2m_over_R_outer_sheet"] = float(np.nanmax((2 * F["m"] / R)[outer & (R > 2.5)]))
    res["sign_KT_plateau_negative"] = bool(H_KT > 0)
    # puncture relation: inner time-symmetric region psi = a + b/rbar
    inner = ok & (rb < 3.0)
    u_in = u_all[1:][inner]
    res["puncture"] = {"u_const_range": [float(u_in.min()), float(u_in.max())],
                       "a_from_u": float(1 + u_in.mean()), "a_json": meta["a"],
                       "M_from_2ab": float(2 * (1 + u_in.mean()) * mp / 2),
                       "M_if_m_p_equal_M": float((1 + u_in.mean()) * M),
                       "m_p_over_M": mp / M}

    # --- negative control: KL := KT in the vacuum transition -------------------------------
    KLbad = KL_all.copy()
    Rrow = np.concatenate([[np.nan], R])
    bad = (Rrow > 6) & (Rrow < 30)
    KLbad[bad] = KT_all[bad]
    neg = {}
    for k in (1, 2, 4, 8):
        sl = slice(0, None, k)
        Fk = fields(rb_all[sl][1:], u_all[sl][1:], KLbad[sl][1:], KT_all[sl][1:], mp, k * drb)
        mk = np.interp(rb_all[sl][1:], rb, (reg_def["transition_vacuum"] & (R > 8) & (R < 28)).astype(float)) > 0.5
        neg[k] = float(np.nanmax(np.abs(Fk["mom"][mk])))
    res["negative_control_KL_eq_KT_max_abs_mom"] = neg

    # --- exact references of the data set ----------------------------------------------
    ref = np.genfromtxt(os.path.join(a.data, "es_reference.csv"), delimiter=",", names=True)
    tau = ref["tau"]
    Rin = float(meta["Rin"])
    Rw_mine = (Rin ** 1.5 + 1.5 * math.sqrt(2 * M) * tau) ** (2 / 3)
    a_mine = (1 + 1.5 * meta["H"] * tau) ** (2 / 3)
    res["reference"] = {"tau_max": float(tau.max()),
                        "max_rel_R_wall": float(np.max(np.abs(ref["R_wall"] / Rw_mine - 1))),
                        "max_rel_a_plateau": float(np.max(np.abs(ref["a_plateau"] / a_mine - 1))),
                        "m_inside_wall_range": [float(ref["m_inside_wall"].min()), float(ref["m_inside_wall"].max())],
                        "R_wall_over_R_in_at_end": float(ref["R_wall"][-1] / Rin),
                        "a_plateau_at_end": float(ref["a_plateau"][-1])}

    # --- Einstein-Straus scales of SCOPE.md section 4 ----------------------------------
    sc = []
    for eps in (0.003, 0.01, 0.03, 0.1):
        Rw = (2 / eps ** 2) ** (1 / 3)
        sc.append({"eps": eps, "R_w": Rw, "H_Rw": eps * Rw, "wall_speed_sqrt_2M_over_Rw": math.sqrt(2 / Rw),
                   "H_R_at_1.5Rw": 1.5 * eps * Rw, "hubble_radius": 1 / eps})
    res["es_scales"] = sc
    res["data_set_eps"] = meta["H"] * M
    res["data_set_R_w_rule"] = (2 / (meta["H"] * M) ** 2) ** (1 / 3)

    # --- particles of the data set: none with mass inside the wall, at rest, mass profile --
    pth = os.path.join(a.data, "es.nrp")
    with open(pth, "rb") as f:
        magic = f.read(8)
        n = int(np.frombuffer(f.read(8), dtype=np.int64)[0])
    rec = np.memmap(pth, dtype=np.float64, mode="r", offset=16, shape=(n, 7))
    mass = np.array(rec[:, 6])
    pos = np.array(rec[:, 0:3])
    uu = np.array(rec[:, 3:6])
    rbp = np.sqrt((pos ** 2).sum(axis=1))
    mass_ok = mass > 1e-25   # tracers carry m = 1e-30
    # cumulative particle mass against the Misner-Sharp mass m(R) - M (R = rbar where psi = 1)
    Rgrid = np.array([37.0, 38, 40, 42, 44, 50, 70, 90, 100, 104, 106, 110])
    mtab = np.interp(Rgrid, R[outer], F["m"][outer])
    mpart = np.array([mass[mass_ok & (rbp < r)].sum() for r in Rgrid])
    res["particles"] = {"magic": magic.decode(), "n": n, "n_massive": int(mass_ok.sum()),
                        "n_massless": int((~mass_ok).sum()),
                        "min_rbar_massive": float(rbp[mass_ok].min()),
                        "max_rbar_massive": float(rbp[mass_ok].max()),
                        "max_abs_u_massive": float(np.abs(uu[mass_ok]).max()),
                        "sum_m": float(mass.sum()), "M_total_minus_M": float(meta["M_total"] - M),
                        "R_grid": Rgrid.tolist(), "m_table_minus_M": (mtab - M).tolist(),
                        "m_particles": mpart.tolist(),
                        "rel_diff": ((mpart - (mtab - M)) / np.maximum(mtab - M, 1e-30)).tolist()}
    del rec

    with open(os.path.join(a.out, "v1_es_slice.json"), "w") as f:
        json.dump(res, f, indent=1)

    # --- figure ------------------------------------------------------------------------
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    o = outer & (R > 2.05)
    a0 = ax[0, 0]
    a0.plot(R[o], np.abs(F["m"][o] - M), color=fs.PAL["blue"], label=r"$|m - M|$")
    a0.plot(R[o], np.abs(F["m"][o] - (M + 0 * R[o])) * 0 + np.abs(rho[o]) * 1e3, color=fs.PAL["red"],
            label=r"$10^3\,|\rho_H|$")
    a0.set_xscale("log"); a0.set_yscale("log")
    a0.set_xlabel(r"$R/M$"); a0.set_ylabel("mass, density")
    a0.axvline(36, **fs.MASK_LINE); a0.axvline(106, **fs.MASK_LINE)
    a0.legend(frameon=False, fontsize=8)
    a0.set_title("Misner-Sharp mass from the table", fontsize=9)
    a1 = ax[0, 1]
    cols = fs.SERIES
    for j, k in enumerate((1, 2, 4, 8)):
        Fk = levels[k]
        Rk = Fk["R"]
        ok2 = np.isfinite(Fk["mom"]) & (Fk["rb"] > rb[i_th])
        a1.plot(Rk[ok2], np.abs(Fk["mom"][ok2]) + 1e-20, color=cols[j], lw=1, label=fr"$h = {k*drb:.2f}\,M$")
    a1.set_xscale("log"); a1.set_yscale("log"); a1.set_ylim(1e-18, 1e-3)
    a1.set_xlabel(r"$R/M$"); a1.set_ylabel(r"$|\mathcal{M}_r|$")
    a1.legend(frameon=False, fontsize=7)
    a1.set_title("momentum residual vs spacing", fontsize=9)
    a2 = ax[1, 0]
    a2.plot(R[o], F["thp"][o] * R[o] / 2, color=fs.PAL["blue"], label=r"$R\theta_+/2$")
    a2.plot(R[o], F["thm"][o] * R[o] / 2, color=fs.PAL["red"], label=r"$R\theta_-/2$")
    a2.plot(R[o], 2 * F["m"][o] / R[o], color=fs.PAL["yellow"], label=r"$2m/R$")
    a2.axhline(0, **fs.THIN)
    a2.set_xscale("log"); a2.set_xlabel(r"$R/M$")
    a2.legend(frameon=False, fontsize=8)
    a2.set_title("expansions on the outer sheet", fontsize=9)
    a3 = ax[1, 1]
    kk = np.array([1, 2, 4, 8]) * drb
    a3.loglog(kk, [regions["transition_vacuum"]["max_abs_mom"][k] for k in (1, 2, 4, 8)], "o-",
              color=fs.PAL["blue"], label="transition (vacuum)")
    a3.loglog(kk, [regions["inner_dust_edge"]["max_abs_mom"][k] for k in (1, 2, 4, 8)], "s-",
              color=fs.PAL["red"], label="inner dust edge")
    a3.loglog(kk, [neg[k] for k in (1, 2, 4, 8)], "^-", color="grey", label=r"control $K_L := K_T$")
    a3.loglog(kk, regions["transition_vacuum"]["max_abs_mom"][8] * (kk / kk[-1]) ** 4, **fs.GUIDE,
              label=r"$\propto h^4$")
    a3.set_xlabel(r"$h/M$"); a3.set_ylabel(r"max $|\mathcal{M}_r|$")
    a3.legend(frameon=False, fontsize=7)
    a3.set_title("convergence and negative control", fontsize=9)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v1_es_slice"))
    os.makedirs(a.figdir, exist_ok=True)
    for p in files:
        if p.endswith(".png"):
            shutil.copy(p, a.figdir)
    print(json.dumps({k: res[k] for k in ("throat", "plateau", "anti_trapped_rows", "max_2m_over_R_outer_sheet",
                                          "puncture", "reference", "negative_control_KL_eq_KT_max_abs_mom", "particles")},
                     indent=1))
    for name, d in regions.items():
        print(name, d["R_range"], "m in", [d["m_min"], d["m_max"]], "rho", [d["rhoH_min"], d["rhoH_max"]],
              "mom", d["max_abs_mom"], d["mom_order"], "rho order", d["rhoH_order"])


if __name__ == "__main__":
    main()
