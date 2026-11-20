#!/usr/bin/env python3
"""C2: does the code's initial slice reproduce the table? Particle masses, psi and K at t = 0
in the first outputs of BH-1R and BH-1; total mass and rest mass.

Writes c2_initial.json and fig_c2_initial.{png,pdf} into $NRPIC_RUN_DIR.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import vbio as V               # noqa: E402
from ltb import TableLTB       # noqa: E402


def local_dx(x, run):
    """Cell size of each line point: uniform runs from the deck; BH-1R: M/16 where the cell
    centre is an odd multiple of 1/32, M/8 where it is an odd multiple of 1/16."""
    if run != "bh_smr":
        return np.full_like(x, P.RUN_DX[run])
    x16 = x * 16.0
    coarse = np.abs(x16 - np.round(x16)) < 1e-9                  # x = (2j+1)/16
    return np.where(coarse, 0.125, 0.0625)


def table_fields_at(T, xc, yc, zc, rule="lagrange"):
    r = np.sqrt(xc ** 2 + yc ** 2 + zc ** 2)
    if rule == "lagrange":
        cols = {}
        for name, c in (("u", 1), ("KL", 2), ("KT", 3)):
            cols[name] = V.lagrange4_eval(T.r, T.d[:, c], T.breaks, np.minimum(r, T.r_last))
        # beyond the last row (pg exterior, u = 0 here)
        far = r > T.r_last
        cols["u"][far] = T.d[-1, 1] * T.r_last / r[far]
        for name, c in (("KL", 2), ("KT", 3)):
            cols[name][far] = T.d[-1, c] * (r[far] / T.r_last) ** -1.5
    else:
        cols = {n: T.field(n, r) for n in ("u", "KL", "KT")}
    psi4 = (1.0 + cols["u"]) ** 4
    n = np.stack([xc, yc, zc]) / r
    K = {}
    for a, i in (("x", 0), ("y", 1), ("z", 2)):
        for b, j in (("x", 0), ("y", 1), ("z", 2)):
            K[a + b] = psi4 * (cols["KT"] * (1.0 if i == j else 0.0) + (cols["KL"] - cols["KT"]) * n[i] * n[j])
    return r, psi4, K, cols


def main():
    out = P.outdir()
    T = TableLTB(P.TABLE)
    res = dict(rest_mass_table=float(T.rest_mass()), M_last_row=float(T.slice(np.array([T.r_last]))["m"][0]))

    # ---------------------------------------------------------------- particle files
    lat = {}
    for n, path in P.NRP.items():
        x, u, m, sp = V.read_nrp(path)
        h = 2 * 4.25 / n
        r = np.sqrt(np.sum(x * x, axis=1))
        s = T.slice(r)
        dens = s["rho_H"] * s["psi"] ** 6 * h ** 3          # rest mass per lattice cell
        ratio = m / np.where(dens > 0, dens, np.nan)
        b1, b2 = np.sort(T.breaks)
        interior = ((r < b1 - h) | ((r > b1 + h) & (r < b2 - h)) | ((r > b2 + h) & (r < 4.25 - 0.5)))
        # lattice offsets: sites at (k + 1/2) h ?
        frac = (x / h) - np.floor(x / h)
        lat[n] = dict(N=int(len(m)), sum_m=float(m.sum()), rel_to_table=float(m.sum() / res["rest_mass_table"] - 1),
                      max_abs_u=float(np.max(np.abs(u))), species=sorted(set(sp.tolist())),
                      ratio_interior_min=float(np.nanmin(ratio[interior])),
                      ratio_interior_max=float(np.nanmax(ratio[interior])),
                      ratio_interior_median=float(np.nanmedian(ratio[interior])),
                      site_fraction_of_h=sorted(set(np.round(frac.ravel(), 6).tolist()))[:4],
                      r_max=float(r.max()))
        if n in (68, 136):
            lat[n]["_plot"] = (r, ratio)
    res["lattices"] = {k: {kk: vv for kk, vv in v.items() if kk != "_plot"} for k, v in lat.items()}

    # ---------------------------------------------------------------- outputs at t = 0
    runs = {}
    for run, d in P.RUN_DIR.items():
        rr = {}
        names, h0 = V.read_hst(os.path.join(d, "ball.nrpic.hst"))
        c = {nm: k for k, nm in enumerate(names)}
        x, u, m, sp = V.read_nrp(P.NRP[P.RUN_LAT[run]])
        rr["hst_t0"] = dict(time=float(h0[0, 0]), np=int(h0[0, c["np"]]), sum_m=float(h0[0, c["sum_m"]]),
                            file_sum_m=float(m.sum()), file_N=int(len(m)),
                            rel_diff=float(h0[0, c["sum_m"]] / m.sum() - 1),
                            sum_mW=float(h0[0, c["sum_mW"]]), int_E=float(h0[0, c["int_E"]]))
        adm = V.read_tabout(sorted(V.tabout_series(os.path.join(d, "tab"), "adm"))[0])
        tm = V.read_tabout(sorted(V.tabout_series(os.path.join(d, "tab"), "tmunu"))[0])
        assert adm["time"] == 0.0 and tm["time"] == 0.0
        xc = adm["x1v"]
        dx = local_dx(xc, run)
        yc = zc = 0.5 * dx
        r, psi4, K, cols = table_fields_at(T, xc, yc, zc, "lagrange")
        dpsi = adm["adm_psi4"] / psi4 - 1
        dg = max(np.max(np.abs(adm["adm_g" + k] - psi4 * (1.0 if k[0] == k[1] else 0.0)) / psi4)
                 for k in ("xx", "xy", "xz", "yy", "yz", "zz"))
        Kscale = np.max(np.abs(K["xx"]))
        dK = {k: adm["adm_K" + k] - K[k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")}
        dKmax = max(np.max(np.abs(v)) for v in dK.values())
        # same with the spline rule (difference between rules = interpolation error of the table)
        _, psi4s, Ks, _ = table_fields_at(T, xc, yc, zc, "spline")
        # deposited E against the table density at the cell centres
        s = T.slice(r)
        Edep = tm["tmunu_E"]
        b1, b2 = np.sort(T.breaks)
        far_from_jumps = (np.abs(r - b1) > 3 * dx) & (np.abs(r - b2) > 3 * dx) & (r < 4.25 - 0.6)
        inside = far_from_jumps & (r < 4.25)
        rho_c = float(T.slice(np.array([0.0]))["rho_H"][0])
        relE = (Edep - s["rho_H"]) / rho_c
        core = inside & (r < b1)
        shell = inside & (r > b1) & (r < b2)
        rr["line"] = dict(n=int(len(xc)), psi4_rel_max=float(np.max(np.abs(dpsi))),
                          psi4_rel_max_where=float(xc[np.argmax(np.abs(dpsi))]),
                          gamma_rel_max=float(dg), K_abs_max=float(dKmax), K_scale=float(Kscale),
                          K_rel_max=float(dKmax / Kscale),
                          psi4_rules_diff_max=float(np.max(np.abs(psi4s / psi4 - 1))),
                          E_dep_minus_rho_over_rho_c_core_maxabs=float(np.max(np.abs(relE[core]))) if core.any() else None,
                          E_dep_minus_rho_over_rho_c_shell_maxabs=float(np.max(np.abs(relE[shell]))) if shell.any() else None,
                          E_dep_core_mean_ratio=float(np.mean(Edep[core] / s["rho_H"][core])) if core.any() else None,
                          E_dep_shell_mean_ratio=float(np.mean(Edep[shell] / s["rho_H"][shell])) if shell.any() else None)
        rr["_plot"] = (xc, r, dpsi, dK["xx"] / Kscale, Edep, s["rho_H"])
        runs[run] = rr
    res["runs"] = {k: {kk: vv for kk, vv in v.items() if kk != "_plot"} for k, v in runs.items()}
    with open(os.path.join(out, "c2_initial.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    # ---------------------------------------------------------------- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.4))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, wspace=0.34, hspace=0.42)
    cols = {"bh_smr": fs.PAL["red"], "bh_n256": fs.PAL["blue"], "bh_n192": fs.PAL["green"], "bh_n128": fs.PAL["orange"]}
    lab = {"bh_smr": "BH-1R (M/16 | M/8)", "bh_n256": "BH-1 M/8", "bh_n192": "BH-1 M/6", "bh_n128": "BH-1 M/4"}
    ax = fig.add_subplot(2, 2, 1)
    for run, rr in runs.items():
        xc, r, dpsi, dKxx, Edep, rho = rr["_plot"]
        ax.semilogy(xc, np.abs(dpsi) + 1e-17, ".", ms=2, color=cols[run], label=lab[run])
    ax.set_xlabel(r"$x\,/M$ (line $y=z=dx/2$)")
    ax.set_ylabel(r"$|\psi^4_{\rm code}/\psi^4_{\rm table}-1|$")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title(r"conformal factor at $t=0$", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    for run, rr in runs.items():
        xc, r, dpsi, dKxx, Edep, rho = rr["_plot"]
        ax.semilogy(xc, np.abs(dKxx) + 1e-17, ".", ms=2, color=cols[run])
    ax.set_xlabel(r"$x\,/M$")
    ax.set_ylabel(r"$|K_{xx}^{\rm code}-K_{xx}^{\rm table}|/\max|K_{xx}|$")
    ax.set_title(r"extrinsic curvature at $t=0$", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    for run, rr in runs.items():
        xc, r, dpsi, dKxx, Edep, rho = rr["_plot"]
        o = np.argsort(r)
        ax.plot(r[o], Edep[o] / T.slice(np.array([0.0]))["rho_H"][0], ".", ms=2, color=cols[run], label=lab[run])
    rg = np.linspace(0, 5, 2000)
    ax.plot(rg, T.slice(rg)["rho_H"] / T.slice(np.array([0.0]))["rho_H"][0], **fs.GUIDE, label="table")
    ax.set_xlim(0, 5)
    ax.set_xlabel(r"$\bar r\,/M$")
    ax.set_ylabel(r"$E/\rho_c$ at $t=0$")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("deposited energy density", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    for n, c_ in ((68, fs.PAL["blue"]), (136, fs.PAL["red"])):
        r, ratio = lat[n]["_plot"]
        sel = np.random.default_rng(1).choice(len(r), size=min(len(r), 40000), replace=False)
        ax.plot(r[sel], ratio[sel], ".", ms=1, color=c_, label=f"lattice $n$ = {n}")
    ax.set_ylim(0.9, 1.2)
    ax.set_xlabel(r"$\bar r\,/M$ of the site")
    ax.set_ylabel(r"$m_p/(\rho\,\psi^6 h^3)$")
    ax.legend(fontsize=7, frameon=False, markerscale=6)
    ax.set_title("particle masses against the table", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c2_initial"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
