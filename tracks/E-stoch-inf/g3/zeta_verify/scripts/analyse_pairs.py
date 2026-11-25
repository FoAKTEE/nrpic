"""P3-P6 of JOURNAL entry 1 on the 32^3 mirrored pairs of run E-20261125-153148-cfad424
(zp4/zm4 at s = +-1/4, zp2/zm2 at s = +-1/2; dumps at N_f = N* + 10).

Per cell at N_f: y = -3 Pi/K (normal observers; alpha = 1 on the geodesic slice is checked),
Delta N_bg(cell) = e-folds of the homogeneous FKG universe from (phi, y) to phi_e (full
nonlinear map, longdouble RK4) and its second-order expansion about the lockstep background
(variational equations); zeta = -1/2 ln(chi/<chi>) + Delta N_bg - <Delta N_bg>; R^NR as
ladder_lib.curvature, mapped to the cells.  Then Z0, Z2 (i), (iii), (iii'), the map
coefficients of Z1 (exact, and finite differences in float64 and longdouble), the box's
relation and the one-point error of a reader whose coefficient along the momentum alone is off.

Usage: analyse_pairs.py <pairs run dir> <deck> <outdir>
"""
import json
import os
import sys
import time

import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zv_lib as Z  # noqa: E402

LD = Z.LD


def deck_value(path, block, key):
    cur = None
    with open(path) as fh:
        for line in fh:
            t = line.split("#", 1)[0].strip()
            if t.startswith("<"):
                cur = t.strip("<>")
            elif "=" in t and cur == block:
                k, v = (u.strip() for u in t.split("=", 1))
                if k == key:
                    return v
    raise KeyError(f"{block}/{key}")


def main(rundir, deck, out):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    lam = float(deck_value(deck, "scalar_field", "lambda"))
    vev = float(deck_value(deck, "scalar_field", "vev"))
    phi0 = float(deck_value(deck, "problem", "phi0"))
    pi0 = float(deck_value(deck, "problem", "pi0"))
    pot = Z.Inflection(lam, vev)
    res = dict(deck=dict(lam=lam, vev=vev, phi0=phi0, pi0=pi0))
    H_STEP = 1e-3        # step of the background and variational integration
    H_CELL = 2e-3        # step of the per-cell nonlinear map

    # ------------------------------------------------ background and end surface
    runs = ["zp4", "zm4", "zp2", "zm2"]
    hdr = {r: Z.read_modes_header(os.path.join(rundir, r, "usr.sf.00001.modes")) for r in runs}
    bg = hdr["zp4"]
    for r in runs[1:]:
        for k in ("phi_b", "Pi_b", "ln_a", "H"):
            assert hdr[r][k] == bg[k], (r, k)
    phi_b, Pi_b, lna, Hl = LD(bg["phi_b"]), LD(bg["Pi_b"]), LD(bg["ln_a"]), LD(bg["H"])
    H_F = np.sqrt(Z.hubble2_from_pi(pot, phi_b, Pi_b))
    y_b = Pi_b / Hl
    # my FKG from the deck's slice at N* (H from Friedmann) to ln a of the dump
    H0 = np.sqrt(Z.hubble2_from_pi(pot, LD(phi0), LD(pi0)))
    p10, y10 = Z.integrate_to_N(pot, LD(phi0), LD(pi0) / H0, lna, H_STEP)
    H10 = np.sqrt(Z.hubble2(pot, p10, y10))
    res["background"] = dict(phi_b=float(phi_b), Pi_b=float(Pi_b), ln_a=float(lna),
                             H_lockstep=float(Hl), H_friedmann=float(H_F),
                             rel_H_lock_minus_friedmann=float(Hl / H_F - 1),
                             my_phi_at_lna=float(p10), my_Pi_at_lna=float(y10 * H10),
                             dphi_mine_minus_lockstep=float(p10 - phi_b),
                             rel_dPi_mine_minus_lockstep=float(y10 * H10 / Pi_b - 1))
    dNe = LD(15) - lna
    phi_e, y_e = Z.integrate_to_N(pot, phi_b, y_b, dNe, H_STEP)
    phi_e_half, _ = Z.integrate_to_N(pot, phi_b, y_b, dNe, H_STEP / 2)
    res["end_surface"] = dict(N_e_minus_lna=float(dNe), phi_e=float(phi_e),
                              y_e=float(y_e), phi_e_step_change=float(phi_e_half - phi_e))
    print("background", res["background"], res["end_surface"], flush=True)

    # ------------------------------------------------ map derivatives at the background
    Nb, Na, Nab, info = Z.map_derivatives(pot, phi_b, y_b, phi_e, H_STEP)
    Nb2, Na2, Nab2, _ = Z.map_derivatives(pot, phi_b, y_b, phi_e, H_STEP / 2)
    Ka = -3 * Hl                          # K of the background (the cells: their own K)
    Np, Npp = Z.to_phi_pi(Na, Nab, Hl)    # derivatives in (phi, Pi) at fixed K
    Np2, Npp2 = Z.to_phi_pi(Na2, Nab2, Hl)
    res["map"] = dict(N_b=float(Nb), N_phi=float(Np[0]), N_Pi=float(Np[1]),
                      N_phiphi=float(Npp[0, 0]), N_phiPi=float(Npp[0, 1]), N_PiPi=float(Npp[1, 1]),
                      N_y=float(Na[1]), N_yy=float(Nab[1, 1]), N_phiy=float(Nab[0, 1]),
                      step_change=dict(N_phi=float(Np2[0] / Np[0] - 1), N_Pi=float(Np2[1] / Np[1] - 1),
                                       N_phiphi=float(Npp2[0, 0] / Npp[0, 0] - 1),
                                       N_phiPi=float(Npp2[0, 1] / Npp[0, 1] - 1),
                                       N_PiPi=float(Npp2[1, 1] / Npp[1, 1] - 1)),
                      ratio_NPi_over_Nphi=float(Np[1] / Np[0]),
                      closed_estimate_NPi=float(-1 / (3 * Pi_b)))
    print("map", res["map"], flush=True)

    # ------------------------------------------------ cells
    cells = {}
    for r in runs:
        f, head = Z.read_dump(os.path.join(rundir, r, "usr.sf.00001.dump"))
        assert abs(head["time"] - float(deck_value(deck, "time", "tlim"))) < 1e-9
        phi = f["phi"].astype(LD)
        Pi = f["Pi"].astype(LD)
        K = f["K"].astype(LD)
        y = -3 * Pi / K
        dN_full = Z.efolds_to_surface(pot, phi.ravel(), y.ravel(), phi_e, H_CELL).reshape(phi.shape)
        d = np.stack([phi - phi_b, y - y_b])
        dN_2 = Nb + Na[0] * d[0] + Na[1] * d[1] + 0.5 * (Nab[0, 0] * d[0] ** 2 + 2 * Nab[0, 1] * d[0] * d[1]
                                                    + Nab[1, 1] * d[1] ** 2)
        psi = -0.5 * np.log(f["chi"] / f["chi"].mean())
        zeta_full = psi + np.asarray(dN_full - dN_full.mean(), dtype=float)
        zeta_2 = psi + np.asarray(dN_2 - dN_2.mean(), dtype=float)
        R, aniso = Z.curvature_RNR(f)
        cells[r] = dict(phi=f["phi"], Pi=f["Pi"], K=f["K"], alpha=f["alpha"], chi=f["chi"],
                        zeta=zeta_full, zeta2=zeta_2, R=R, psi=psi, aniso=aniso,
                        third=np.asarray((dN_full - dN_full.mean()) - (dN_2 - dN_2.mean()), dtype=float))
        print(r, "rms zeta", zeta_full.std(), "rms R", R.std(), "max|alpha-1|",
              np.abs(f["alpha"] - 1).max(), "rms dK/K", (f["K"] / f["K"].mean() - 1).std(),
              "t", round(time.time() - t0), flush=True)
    res["cells"] = {r: dict(rms_zeta=float(c["zeta"].std()), rms_R=float(c["R"].std()),
                            rms_psi=float(c["psi"].std()), rms_aniso=float(c["aniso"].std()),
                            max_abs_alpha_minus_1=float(np.abs(c["alpha"] - 1).max()),
                            rms_dK_over_K=float((c["K"] / c["K"].mean() - 1).std()),
                            rms_third_order=float(c["third"].std()),
                            mean_phi_minus_phib=float(c["phi"].mean() - float(phi_b)),
                            rms_dphi=float(c["phi"].std()), rms_dPi=float(c["Pi"].std()))
                    for r, c in cells.items()}

    # ------------------------------------------------ Z0, Z2 per amplitude
    zres = {}
    for tag, (p, m), s in (("s1/4", ("zp4", "zm4"), 0.25), ("s1/2", ("zp2", "zm2"), 0.5)):
        cp, cm = cells[p], cells[m]
        O = {k: 0.5 * (cp[k] - cm[k]) for k in ("zeta", "zeta2", "R", "phi", "Pi", "psi")}
        E = {k: 0.5 * (cp[k] + cm[k]) for k in ("zeta", "zeta2", "R", "phi", "Pi", "psi")}
        for k in E:
            E[k] = E[k] - E[k].mean()
        z0 = float(np.sqrt(((O["zeta"] + O["R"]) ** 2).mean()) / np.sqrt((O["R"] ** 2).mean()))
        slope = Z.regress(O["zeta"], O["R"])
        q = O["zeta"] ** 2 - (O["zeta"] ** 2).mean()
        qR = O["R"] ** 2 - (O["R"] ** 2).mean()
        a_zeta = Z.regress(E["zeta"], q)
        a_zeta2 = Z.regress(E["zeta2"], q)
        a_R = Z.regress(E["R"], qR)
        # the box's relation from the odd parts
        r_rel = Z.regress(O["Pi"], O["phi"])
        perp = O["Pi"] - r_rel * O["phi"]
        r_rel_full = Z.regress(cp["Pi"], cp["phi"])
        perp_full = (cp["Pi"] - cp["Pi"].mean()) - r_rel_full * (cp["phi"] - cp["phi"].mean())
        # map along the relation (straight line in (phi, Pi) at fixed K)
        d1 = float(Np[0] + r_rel * Np[1])
        d2 = float(Npp[0, 0] + 2 * r_rel * Npp[0, 1] + r_rel ** 2 * Npp[1, 1])
        a_map = 0.5 * d2 / d1 ** 2
        a_map_phi = float(0.5 * Npp[0, 0] / Np[0] ** 2)
        # decomposition of E_zeta by the second-order expansion (diagnostic)
        Hc = float(Hl)
        parts = dict(lin_phi=float(Np[0]) * E["phi"], lin_Pi=float(Np[1]) * E["Pi"], psi=E["psi"])
        a_parts = {k: Z.regress(v, q) for k, v in parts.items()}
        zres[tag] = dict(s=s, Z0_ratio=z0, slope_Ozeta_on_OR=slope,
                         a_zeta=a_zeta, a_zeta_secondorder=a_zeta2, a_R=a_R,
                         r_relation=r_rel, r_relation_full_member=r_rel_full,
                         rms_O_phi=float(O["phi"].std()), rms_O_Pi=float(O["Pi"].std()),
                         rms_perp_over_rms_OPi=float(perp.std() / O["Pi"].std()),
                         rms_perp_full_over_rms_dPi=float(perp_full.std() / cp["Pi"].std()),
                         corr_OPi_Ophi=float(np.corrcoef(O["Pi"].ravel(), O["phi"].ravel())[0, 1]),
                         map_along_relation=dict(d1=d1, d2=d2, a_map=a_map), a_map_field_alone=a_map_phi,
                         Z2i_rel_diff=None, Z2iii=a_zeta / a_map - 1,
                         Z2iiiprime=(a_zeta - (a_map - a_R)) / a_map,
                         a_parts=a_parts, rms_zeta1=float(O["zeta"].std()),
                         zeta_perp_share=float(np.sqrt(((float(Np[1]) * perp) ** 2).mean()) / O["zeta"].std()))
        cells[tag] = dict(O=O, E=E, q=q, perp=perp, perp_full=perp_full)
    zres["s1/4"]["Z2i_rel_diff"] = zres["s1/2"]["Z2i_rel_diff"] = \
        zres["s1/2"]["a_zeta"] / zres["s1/4"]["a_zeta"] - 1
    res["Z"] = zres
    print(json.dumps(zres, indent=1, default=float), flush=True)

    # ------------------------------------------------ Z1: coefficients along three directions
    dirs = {"field": (1.0, 0.0), "momentum": (0.0, 1.0),
            "relation": (1.0, zres["s1/4"]["r_relation"])}
    spread = {"field": zres["s1/4"]["rms_O_phi"], "momentum": zres["s1/4"]["rms_O_Pi"],
              "relation": zres["s1/4"]["rms_O_phi"]}
    z1 = {}
    fdscan = {}
    for name, (u, w) in dirs.items():
        exact1 = float(Np[0] * u + Np[1] * w)
        exact2 = float(Npp[0, 0] * u * u + 2 * Npp[0, 1] * u * w + Npp[1, 1] * w * w)
        row = dict(exact_d1=exact1, exact_d2=exact2, eps=spread[name])
        for dt, lab in ((LD, "ld"), (np.float64, "f64")):
            e = spread[name]
            es = np.array([-2 * e, -e, 0.0, e, 2 * e])
            ph = (dt(phi_b) + dt(u) * es.astype(dt)).astype(dt)
            pp = (dt(Pi_b) + dt(w) * es.astype(dt)).astype(dt)
            Nv = Z.efolds_to_surface(pot, ph, pp / dt(Hl), dt(phi_e), H_STEP, dtype=dt)
            Nm2, Nm1, N0, Np1, Np2 = [LD(v) for v in Nv]
            el = LD(e)
            c1 = (Np1 - Nm1) / (2 * el)
            c1b = (8 * (Np1 - Nm1) - (Np2 - Nm2)) / (12 * el)
            c2 = (Np1 + Nm1 - 2 * N0) / el ** 2
            c2b = (Np2 + Nm2 - 2 * N0) / (4 * el ** 2)
            c2r = (16 * (Np1 + Nm1) - (Np2 + Nm2) - 30 * N0) / (12 * el ** 2)
            row[lab] = dict(c1=float(c1), c1_4pt=float(c1b), c2_eps=float(c2), c2_2eps=float(c2b),
                            c2_5pt=float(c2r), rel_c1=float(c1 / LD(exact1) - 1),
                            rel_c2_eps=float(c2 / LD(exact2) - 1), rel_c2_2eps=float(c2b / LD(exact2) - 1),
                            rel_c2_5pt=float(c2r / LD(exact2) - 1),
                            dN2_at_eps=float(0.5 * LD(exact2) * el ** 2))
        z1[name] = row
        # scan of the second finite-difference coefficient in eps
        scan = []
        for frac in np.logspace(-3, 1.5, 19):
            e = spread[name] * frac
            ent = dict(eps=e, eps_over_spread=frac)
            for dt, lab in ((LD, "ld"), (np.float64, "f64")):
                es = np.array([-e, 0.0, e])
                ph = (dt(phi_b) + dt(u) * es.astype(dt)).astype(dt)
                pp = (dt(Pi_b) + dt(w) * es.astype(dt)).astype(dt)
                Nv = Z.efolds_to_surface(pot, ph, pp / dt(Hl), dt(phi_e), H_STEP, dtype=dt)
                c2 = (LD(Nv[0]) + LD(Nv[2]) - 2 * LD(Nv[1])) / LD(e) ** 2
                ent[lab] = float(c2 / LD(exact2) - 1)
            scan.append(ent)
        fdscan[name] = scan
        print("Z1", name, json.dumps(row, default=float), flush=True)
    res["Z1"] = z1
    res["fdscan"] = fdscan

    # analyticity in the momentum: N(phi_b, Pi_b + e) over a wide range against the expansion
    ana = []
    for frac in (-0.5, -0.2, -0.05, -0.01, 0.01, 0.05, 0.2, 0.5, 1.0):
        e = LD(frac) * Pi_b
        Nv = Z.efolds_to_surface(pot, phi_b, (Pi_b + e) / Hl, phi_e, H_STEP)
        quad = Nb + Np[1] * e + 0.5 * Npp[1, 1] * e * e
        ana.append(dict(dPi_over_Pib=frac, N_minus_Nb=float(Nv - Nb), lin=float(Np[1] * e),
                        quad_resid=float(Nv - quad)))
    res["momentum_wide"] = ana

    # round-off floor of N in the integration of the absolute field: N(e) on a dense grid of
    # e within +-3 spreads, a cubic fitted, rms of the residual (float64 and long double, two steps)
    floor = {}
    for name in ("field", "momentum"):
        u, w = dirs[name]
        es = np.linspace(-3, 3, 41) * spread[name]
        for dt, lab in ((LD, "ld"), (np.float64, "f64")):
            for hh in (1e-3, 7.3e-4):
                ph = (dt(phi_b) + dt(u) * es.astype(dt)).astype(dt)
                pp = (dt(Pi_b) + dt(w) * es.astype(dt)).astype(dt)
                Nv = Z.efolds_to_surface(pot, ph, pp / dt(Hl), dt(phi_e), hh, dtype=dt)
                dn = np.asarray(Nv.astype(LD) - LD(Nv[20]), dtype=float)
                x = es / spread[name]
                cf = np.polyfit(x, dn, 3)
                resid = dn - np.polyval(cf, x)
                key = f"{name}_{lab}_h{hh:g}"
                floor[key] = dict(rms_resid=float(resid.std()), x=x.tolist(), resid=resid.tolist(),
                                  dN2_at_spread=float(0.5 * (Npp[0, 0] * u * u + 2 * Npp[0, 1] * u * w
                                                             + Npp[1, 1] * w * w) * LD(spread[name]) ** 2))
                print("floor", key, floor[key]["rms_resid"], floor[key]["dN2_at_spread"], flush=True)
    res["roundoff_floor"] = floor

    # the end surface: phi_e from the deck's slice at N* (my FKG over 15 e-folds) instead of the
    # lockstep state at N_f; the map coefficients there
    p15, _ = Z.integrate_to_N(pot, LD(phi0), LD(pi0) / H0, LD(15), H_STEP)
    Nb_a, Na_a, Nab_a, _ = Z.map_derivatives(pot, phi_b, y_b, p15, H_STEP)
    Np_a, Npp_a = Z.to_phi_pi(Na_a, Nab_a, Hl)
    r4 = zres["s1/4"]["r_relation"]
    d1a = float(Np_a[0] + r4 * Np_a[1])
    d2a = float(Npp_a[0, 0] + 2 * r4 * Npp_a[0, 1] + r4 ** 2 * Npp_a[1, 1])
    res["end_surface_alt"] = dict(phi_e_from_deck_slice=float(p15), dphi_e=float(p15 - phi_e),
                                  N_b=float(Nb_a), rel_N_phi=float(Np_a[0] / Np[0] - 1),
                                  rel_N_Pi=float(Np_a[1] / Np[1] - 1),
                                  rel_N_PiPi=float(Npp_a[1, 1] / Npp[1, 1] - 1),
                                  rel_N_phiphi=float(Npp_a[0, 0] / Npp[0, 0] - 1),
                                  a_map=0.5 * d2a / d1a ** 2,
                                  rel_a_map=(0.5 * d2a / d1a ** 2) / zres["s1/4"]["map_along_relation"]["a_map"] - 1)
    print("end surface alt", res["end_surface_alt"], flush=True)

    # ------------------------------------------------ one-point error of a reader off along Pi
    one = {}
    sig_g3 = 0.4940      # sigma_lin of the 128^3 G3 box (SCOPE 4d.2, run E-20261120-222424-0eb754b)
    for tag in ("s1/4", "s1/2"):
        p = "zp4" if tag == "s1/4" else "zp2"
        c = cells[p]
        zeta = c["zeta"]
        dPi = c["Pi"] - float(Pi_b)
        for frac in (0.142, 1.0):
            dz = 0.5 * frac * float(Npp[1, 1]) * (dPi ** 2 - (dPi ** 2).mean())
            sig = zeta.std()
            x0 = (zeta - zeta.mean()) / sig
            x1 = (zeta + dz - (zeta + dz).mean()) / sig
            ent = dict(rms_dzeta_over_sigma=float(dz.std() / sig),
                       max_dzeta_over_sigma=float(np.abs(dz).max() / sig))
            # error in F at nu from the Gaussian tail: dF ~ pdf(nu) * <dx | x = nu>, bounded by
            # pdf(nu) * max|dx|; at the G3 amplitude dx scales with sigma (dx ~ s)
            for nu in (3.0, 4.0):
                bound = norm.pdf(nu) * np.abs(dz).max() / sig
                ent[f"F({nu:.0f})_rel_bound_here"] = float(bound / norm.sf(nu))
                ent[f"F({nu:.0f})_rel_bound_G3"] = float(bound / norm.sf(nu) * sig_g3 / sig)
                ent[f"F+({nu:.0f})_cells_changed"] = int(((x0 > nu) != (x1 > nu)).sum())
            one[f"{tag} frac={frac}"] = ent
    res["one_point"] = one
    print("one-point", json.dumps(one, indent=1), flush=True)

    with open(os.path.join(out, "pairs.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    np.savez_compressed(os.path.join(out, "pairs_cells.npz"),
                        **{f"{t}_{k}": v for t in ("s1/4", "s1/2")
                           for k, v in [("Ozeta", cells[t]["O"]["zeta"]), ("OR", cells[t]["O"]["R"]),
                                        ("Ezeta", cells[t]["E"]["zeta"]), ("ER", cells[t]["E"]["R"]),
                                        ("Ophi", cells[t]["O"]["phi"]), ("OPi", cells[t]["O"]["Pi"])]})
    figures(res, cells, out)
    print("done", round(time.time() - t0), "s")


def figures(res, cells, out):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = {"s1/4": fs.PAL["blue"], "s1/2": fs.PAL["red"]}
    # ---- Z0 and Z2
    fig, axs = plt.subplots(1, 3, figsize=(10.0, 3.0))
    ax = axs[0]
    for tag in ("s1/2", "s1/4"):
        O = cells[tag]["O"]
        ax.plot(-O["R"].ravel()[::4], O["zeta"].ravel()[::4], ".", ms=1, color=cols[tag],
                label=f"{tag}: Z0 ratio {res['Z'][tag]['Z0_ratio']:.1e}")
    lim = np.abs(cells["s1/2"]["O"]["R"]).max()
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=0.7)
    ax.set_xlabel("$-O_R$")
    ax.set_ylabel("$O_\\zeta$")
    ax.legend(fontsize=6, markerscale=6)
    ax = axs[1]
    for tag in ("s1/2", "s1/4"):
        c = cells[tag]
        sig = c["O"]["zeta"].std()
        ax.plot((c["q"] / sig ** 2).ravel()[::4], (c["E"]["zeta"] / sig ** 2).ravel()[::4], ".", ms=1,
                color=cols[tag], label=f"{tag}: $a_\\zeta$ = {res['Z'][tag]['a_zeta']:.5f}")
    xx = np.linspace(-1, 12, 10)
    am = res["Z"]["s1/4"]["map_along_relation"]["a_map"]
    ax.plot(xx, am * xx, "k--", lw=0.7, label=f"$a_{{\\rm map}}$ = {am:.5f}")
    ax.set_xlabel("$(O_\\zeta^2 - \\langle O_\\zeta^2\\rangle)/\\sigma_1^2$")
    ax.set_ylabel("$E_\\zeta/\\sigma_1^2$")
    ax.legend(fontsize=6, markerscale=6)
    ax = axs[2]
    tags = ["s1/4", "s1/2"]
    xs = np.arange(2)
    az = [res["Z"][t]["a_zeta"] for t in tags]
    pred = [res["Z"][t]["map_along_relation"]["a_map"] - res["Z"][t]["a_R"] for t in tags]
    amap = [res["Z"][t]["map_along_relation"]["a_map"] for t in tags]
    ax.plot(xs, az, "o", color=fs.PAL["red"], label="$a_\\zeta$ (lattice)")
    ax.plot(xs, pred, "s", mfc="none", color=fs.PAL["blue"], label="$a_{\\rm map} - a_R$")
    ax.plot(xs, amap, "^", mfc="none", color=fs.PAL["green"], label="$a_{\\rm map}$")
    ax.set_xticks(xs)
    ax.set_xticklabels(["$s=1/4$", "$s=1/2$"])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylabel("quadratic coefficient")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_z0_z2"))
    plt.close(fig)
    # ---- finite-difference scan
    fig, axs = plt.subplots(1, 3, figsize=(10.0, 3.0), sharey=True)
    for ax, name in zip(axs, ("field", "momentum", "relation")):
        sc = res["fdscan"][name]
        f = np.array([e["eps_over_spread"] for e in sc])
        for lab, c, m in (("f64", fs.PAL["red"], "o"), ("ld", fs.PAL["blue"], "s")):
            v = np.abs(np.array([e[lab] for e in sc]))
            ax.loglog(f, np.maximum(v, 1e-12), m + "-", color=c, ms=3,
                      label={"f64": "float64", "ld": "long double"}[lab])
        ax.axvline(1.0, color="k", lw=0.6, ls=":")
        ax.axvline(2.0, color="k", lw=0.6, ls=":")
        ax.axhline(0.01, color=fs.PAL["green"], lw=0.8, ls="--")
        ax.set_title(f"along the {name}" + (" alone" if name != "relation" else ""), fontsize=8)
        ax.set_xlabel("$\\epsilon$ / box spread ($s=1/4$)")
    axs[0].set_ylabel("$|c_2^{\\rm FD}/N''_{\\rm exact} - 1|$")
    axs[0].legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_fd_scan"))
    plt.close(fig)
    # ---- the box's relation
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axs[0]
    for tag in ("s1/2", "s1/4"):
        O = cells[tag]["O"]
        ax.plot(O["phi"].ravel()[::4], O["Pi"].ravel()[::4], ".", ms=1, color=cols[tag], label=tag)
    r = res["Z"]["s1/4"]["r_relation"]
    xl = np.abs(cells["s1/2"]["O"]["phi"]).max()
    ax.plot([-xl, xl], [-r * xl, r * xl], "k--", lw=0.7, label=f"slope {r:.5f}")
    ax.set_xlabel("$O_\\phi$")
    ax.set_ylabel("$O_\\Pi$")
    ax.legend(fontsize=6, markerscale=6)
    ax = axs[1]
    for tag in ("s1/2", "s1/4"):
        p = cells[tag]["perp"].ravel() / cells[tag]["O"]["Pi"].std()
        ax.hist(p, bins=80, histtype="step", color=cols[tag],
                label=f"{tag}: rms {res['Z'][tag]['rms_perp_over_rms_OPi']:.2e}")
    ax.set_xlabel("$(O_\\Pi - r\\,O_\\phi)/{\\rm rms}(O_\\Pi)$")
    ax.set_ylabel("cells")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_relation"))
    plt.close(fig)
    # ---- the map along the momentum: analytic over a wide range; round-off floor
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axs[0]
    w = res["momentum_wide"]
    f = np.array([e["dPi_over_Pib"] for e in w])
    q = np.array([e["quad_resid"] for e in w])
    ax.loglog(np.abs(f[f > 0]), np.abs(q[f > 0]), "o", color=fs.PAL["red"], label="$\\delta\\Pi>0$")
    ax.loglog(np.abs(f[f < 0]), np.abs(q[f < 0]), "s", mfc="none", color=fs.PAL["blue"],
              label="$\\delta\\Pi<0$")
    ff = np.array([0.01, 1.0])
    ax.loglog(ff, abs(q[f == 0.2][0]) * (ff / 0.2) ** 3, "k--", lw=0.7, label="$\\propto \\delta\\Pi^3$")
    ax.set_xlabel("$|\\delta\\Pi|/\\Pi_b$ (field fixed)")
    ax.set_ylabel("$|N - N_b - N_\\Pi\\delta\\Pi - N_{\\Pi\\Pi}\\delta\\Pi^2/2|$")
    ax.legend(fontsize=6)
    ax = axs[1]
    fl = res["roundoff_floor"]
    for key, c, m in (("momentum_f64_h0.001", fs.PAL["red"], "o"), ("momentum_ld_h0.001", fs.PAL["blue"], "s"),
                      ("momentum_ld_h0.00073", fs.PAL["green"], "^")):
        ax.plot(fl[key]["x"], fl[key]["resid"], m, ms=3, color=c,
                label=key.replace("momentum_", "").replace("_h", ", h=") + f" (rms {fl[key]['rms_resid']:.1e})")
    d2 = fl["momentum_ld_h0.001"]["dN2_at_spread"]
    ax.axhline(d2, color="k", lw=0.6, ls=":")
    ax.axhline(-d2, color="k", lw=0.6, ls=":")
    ax.set_yscale("symlog", linthresh=1e-13)
    ax.set_xlabel("$\\delta\\Pi$ / box spread ($s=1/4$)")
    ax.set_ylabel("$N$ minus cubic fit")
    ax.legend(fontsize=5.5)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_momentum_map"))
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
