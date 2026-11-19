#!/usr/bin/env python3
"""T2, T5, T6, T7, T8 of the work package cosmo-amr: the homogeneous universe on refined
periodic meshes (predictions: tracks/core/JOURNAL-cosmo-amr.md).

    t2_flrw.py --new NEW_EXE --rel REL_EXE --out DIR [--cores N] [--only a,b,...]

Box [-3, 3)^3, root 24^3, MeshBlocks of 8^3 (27 root blocks; the central one is
[-1, 1]^3), conformal-time lapse, one particle per root cell unless stated.  Cases:
  U    uniform                               S    static level-1 patch |x| < 0.5
  Sf   S with deposit_fine_shape             P    static patches on a face and a corner
  A    adaptive, patch by a fixed tracker    L    adaptive, lohner + <particles_amr>
  D8   S, 8 particles per root cell, clouds on the finest level
  D8s  D8 with a uniform shift -0.5 (lattice drifts through the patch and the faces)
  M    T5: uniform shift, moving tracker, refinement follows it across the face,
       dt_lightspeed
  Mrel M with the release executable
  Tnew, Trel  tracker and shift on the uniform mesh, this branch and the release
  C1   T7a: U without <particles> dt, with dt_lightspeed     C0  the same without it
  C2   T7b: lapse d_t alpha = -(2/3) alpha^2 K with dt_lightspeed   C2n  without it
  G    T6: Courant number 1.5, guard on      Grel  release      Goff  guard off
  Gchi guard with stop_chi_nonpositive
Writes DIR/t2_summary.json and DIR/fig_t2_flrw.{pdf,png}, fig_t5_tracker.{pdf,png}."""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

import amrlib as A

L, N, NB = 6.0, 24, 8
DXR = L/N                 # root cell 0.25
DT1 = 0.25*DXR/2          # Courant step of level 1


def base(ic):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo/flrw.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": N, f"x{d}min": -L/2, f"x{d}max": L/2})
        b.set("meshblock", **{f"nx{d}": NB})
    b.set("time", tlim=1.0, nlim=-1)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"),
          deposit_adaptive=True, snap_dt=-1.0, probe_x1=0.01, probe_x2=0.01,
          probe_x3=0.01, cstat_dcycle=1, dt=DT1, region_dcycle=1, region_radius1=1.5)
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    b.set("output1", file_type="hst", dt=0.5)
    return b


def static(b, regions):
    b.set("mesh_refinement", refinement="static", max_nmb_per_rank=256)
    for n, r in enumerate(regions):
        b.set(f"refined_region{n+1}", level=1, x1min=r[0], x1max=r[1], x2min=r[2],
              x2max=r[3], x3min=r[4], x3max=r[5])
    return b


def adaptive(b):
    b.set("mesh_refinement", refinement="adaptive", num_levels=2, max_nmb_per_rank=256,
          ncycle_check=4, refinement_interval=4)
    b.set("amr_criterion0", method="user")
    return b


def tracker(b, x):
    b.set("z4c", co_0_type="BH", co_0_x=x, co_0_y=0.1, co_0_z=0.1, co_0_radius=0.3,
          co_0_reflevel=1)
    b.set("z4c_amr", method="tracker")
    return b


def cases(ic1, ic8):
    c = {}
    cen = [(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)]
    u = base(ic1)
    u.set("fastflow", find_every=8, metric_drvts="interpolant", num_horizons=1, npunct=0,
          ntheta=16, lmax=8, use_puncture_0=-1, center_x_0=0.0, center_y_0=0.0,
          center_z_0=0.0, initial_radius_0=1.0, flow_iterations_0=400,
          flow_alpha_beta_const_0=1.0, hmean_tol_0=100.0, mass_tol_0=1.0e-5,
          start_time_0=0.0, stop_time_0=1000.0, verbose=False, diagnostics=True)
    c["U"] = u
    c["S"] = static(base(ic1), cen)
    c["Sf"] = static(base(ic1), cen).set("particles", deposit_fine_shape=True)
    c["P"] = static(base(ic1), [(2.5, 3.0, -0.5, 0.5, -0.5, 0.5),
                                (2.5, 3.0, 2.5, 3.0, 2.5, 3.0)])
    c["P"].set("particles", deposit_fine_shape=True)
    c["A"] = tracker(adaptive(base(ic1)), 0.1).set("particles", deposit_fine_shape=True)
    lo = adaptive(base(ic1))
    lo.set("z4c_amr", method="lohner", lohner_refine=0.2, lohner_derefine=0.02,
           lohner_eps=0.01)
    lo.set("particles_amr", ppc_refine=4.0, lapse_ratio_1=0.9, chi_ratio_1=0.9,
           verbose=True)
    c["L"] = lo
    d8 = static(base(ic8), cen)
    d8.set("particles", deposit_adaptive=False, deposit_max_level=31)
    c["D8"] = d8
    c["D8s"] = d8.copy().set("problem", shift_x1=-0.5)
    m = tracker(adaptive(base(ic1)), 2.5)
    m.set("problem", shift_x1=-0.5)
    m.set("z4c", dt_lightspeed=1.0)
    m.set("particles", deposit_fine_shape=True)
    m.drop("particles", "dt")
    m.set("time", tlim=2.5)
    c["M"] = m
    c["Mrel"] = m.copy().drop("z4c", "dt_lightspeed").drop("particles", "region_dcycle",
                                                          "region_radius1",
                                                          "deposit_fine_shape")
    # tracker alone on the uniform mesh (no refinement): the release must stop where the
    # tracker leaves the box
    tn = base(ic1)
    tn.set("z4c", co_0_type="BH", co_0_x=2.5, co_0_y=0.1, co_0_z=0.1)
    tn.set("problem", shift_x1=-0.5)
    tn.set("time", tlim=1.5)
    c["Tnew"] = tn
    c["Trel"] = tn.copy().drop("particles", "region_dcycle", "region_radius1")
    c0 = base(ic1).drop("particles", "dt")
    c["C0"] = c0
    c["C1"] = c0.copy().set("z4c", dt_lightspeed=1.0)
    c2 = c0.copy().set("z4c", lapse_harmonic=0.6666666666666666)
    c["C2n"] = c2
    c["C2"] = c2.copy().set("z4c", dt_lightspeed=1.0)
    g = base(ic1).drop("particles", "dt")
    g.set("time", cfl_number=1.5, nlim=400, tlim=200.0)
    c["G"] = g
    c["Goff"] = g.copy().set("z4c_guard", stop_nonfinite=False)
    c["Gchi"] = g.copy().set("z4c_guard", stop_chi_nonpositive=True)
    c["Grel"] = g.copy().drop("particles", "region_dcycle", "region_radius1")
    return c


def spread(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.abs(a/b - 1.0)


def analyse(out, names):
    res = {}
    for n in names:
        d = os.path.join(out, n)
        r = dict(exit=A.exit_status(d))
        hp = os.path.join(d, "flrw.nrpic.hst")
        if os.path.exists(hp):
            h, s = A.read_hst(hp), A.read_hst(os.path.join(d, "flrw.cstat.hst"))
            fin = np.isfinite(h["alpha_max"]) & (h["alpha_max"] > 0)
            t = h["time"]
            r.update(records=len(t), t_end=float(t[-1]), nmb_first=int(h["nmb"][0]),
                     nmb_max=int(h["nmb"].max()), nmb_last=int(h["nmb"][-1]),
                     np_first=int(h["np"][0]), np_last=int(h["np"][-1]),
                     n_finite=int(fin.sum()))
            if fin.any():
                sf = np.isfinite(s["chi_max"]) & (s["chi_min"] > 0)
                r["chi_spread_max"] = float(np.max(spread(s["chi_max"][sf],
                                                          s["chi_min"][sf])))
                ok = fin & (h["E_min"] > 0)
                r["E_spread_max"] = float(np.max(spread(h["E_max"][ok], h["E_min"][ok])))
                r["E_spread_t0"] = float(spread(h["E_max"][0], h["E_min"][0]))
                r["H_max_minus_mean_rel"] = float(np.max(
                    np.abs(s["H_max"][sf] - s["H_mean"][sf])
                    / np.maximum(s["H_max"][sf], 1e-300)))
                r["H_max_end"] = float(s["H_max"][sf][-1])
                r["identity_E"] = float(np.max(spread(h["int_E"][fin], h["sum_mW"][fin])))
                a_ex = (1.0 + 0.5*t)**2
                r["alpha_vs_exact_max"] = float(np.max(spread(h["alpha_max"][fin],
                                                              a_ex[fin])))
            r["_t"], r["_amax"], r["_nmb"] = t, h["alpha_max"], h["nmb"]
            r["_chis"] = spread(s["chi_max"], s["chi_min"])
            r["_ts"] = s["time"]
            r["_es"] = spread(h["E_max"], np.where(h["E_min"] > 0, h["E_min"], np.nan))
            r["_chimax"] = np.interp(t, s["time"], s["chi_max"])
        rp = os.path.join(d, "flrw.region.hst")
        if os.path.exists(rp) and os.path.exists(hp):
            g = A.read_hst(rp)
            k = min(len(g["time"]), len(h["time"]))
            r["region_V_split"] = float(np.max(spread(g["V_in_s1"][:k] + g["V_out_s1"][:k],
                                                      g["V"][:k])))
            r["region_V_vs_hst"] = float(np.max(spread(g["V"][:k],
                                                       h["proper_volume"][:k])))
            r["region_K_vs_hst"] = float(np.max(spread(g["mean_K"][:k],
                                                       h["mean_K"][:k])))
            ks = min(k, len(s["time"]))
            r["region_Hmax_vs_cstat"] = float(np.max(np.abs(
                np.maximum(g["Hmax_in_s1"][:ks], g["Hmax_out_s1"][:ks])
                - s["H_max"][:ks])))
            a_ex3 = ((1.0 + 0.5*g["time"][:k])**2)**3
            r["region_V_vs_exact"] = float(np.max(spread(g["V"][:k], L**3*a_ex3)))
            r["region_Vin_over_sphere_t0"] = float(g["V_in_s1"][0]/(4.0*np.pi/3.0*1.5**3))
            r["region_V_t0_vs_L3"] = float(abs(g["V"][0]/L**3 - 1.0))
        for f in ("flrw.guard.txt", "flrw.horizon_status_0.txt", "flrw.co_0.txt"):
            r["has_" + f.split(".")[1]] = os.path.exists(os.path.join(d, f))
        with open(os.path.join(d, "log.txt"), errors="replace") as f:
            tail = f.read().splitlines()[-12:]
        r["log_tail_fatal"] = [x for x in tail if "FATAL" in x or "couldn't" in x
                               or "guard" in x or "Terminating" in x]
        res[n] = r
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ic1, ic8 = os.path.join(a.out, "ic1"), os.path.join(a.out, "ic8")
    mk = os.path.join(A.ROOT, "cosmo/ic/make_lattice.py")
    for ic, ppc in ((ic1, 1), (ic8, 2)):
        if not os.path.exists(os.path.join(ic, "particles.nrp")):
            subprocess.run([sys.executable, mk, "--n", str(N), "--ppc", str(ppc), "--L",
                            str(L), "--xmin", str(-L/2), "--out", ic], check=True,
                           stdout=subprocess.DEVNULL)
    cs = cases(ic1, ic8)
    names = [n for n in cs if not a.only or n in a.only.split(",")]
    jobs = [((a.rel if n.endswith("rel") else a.new), cs[n], os.path.join(a.out, n),
             "flrw", (), None) for n in names]
    rcs = A.run_many(jobs, a.cores)
    for n, rc in zip(names, rcs):
        print(f"{n:5s} exit {rc[0]:3d} wall {rc[1]:7.1f} s")
    res = analyse(a.out, names)

    # ---- comparisons between cases
    cmpr = {}
    if "U" in res and "_amax" in res["U"]:
        for n in ("S", "Sf", "P", "A", "L", "D8"):
            if n in res and "_amax" in res[n] and len(res[n]["_amax"]) == len(res["U"]["_amax"]):
                cmpr[n + "_alpha_vs_U"] = float(np.max(spread(res[n]["_amax"],
                                                              res["U"]["_amax"])))
    # steps (T7): dt c_max / (cfl dx) with c_max = alpha_max sqrt(chi_max) (+ shift)
    for n, shift in (("C0", 0.0), ("C1", 0.0), ("C2", 0.0), ("C2n", 0.0), ("M", 0.5)):
        if n in res and "_t" in res[n]:
            t = res[n]["_t"]
            dt = np.diff(t)
            c = res[n]["_amax"][:-1]*np.sqrt(res[n]["_chimax"][:-1]) + shift
            # the record of a cycle is written before its regrid: the step that follows
            # runs on the mesh of the next record
            dxmin = DXR/np.where(res[n]["_nmb"][1:] > 27, 2.0, 1.0)
            ratio = dt*c/(0.25*dxmin)
            cmpr[n + "_dt_c_over_cfl_dx_min"] = float(ratio[1:-1].min())
            cmpr[n + "_dt_c_over_cfl_dx_max"] = float(ratio[1:-1].max())
            cmpr[n + "_dt_over_cfl_dx_max"] = float((dt/(0.25*dxmin))[1:-1].max())
            res[n]["_ratio"] = ratio
    if "C0" in res and "C1" in res and "_t" in res["C0"]:
        k = min(len(res["C0"]["_t"]), len(res["C1"]["_t"]))
        cmpr["C1_time_vs_C0"] = float(np.max(np.abs(res["C1"]["_t"][:k] - res["C0"]["_t"][:k])))
    # tracker (T5)
    trk = None
    tp = os.path.join(a.out, "M", "flrw.co_0.txt")
    if os.path.exists(tp):
        trk = np.loadtxt(tp, ndmin=2)
        # the record of cycle n holds the position at t^(n+1) (docs/FORMATS.md)
        hM = res["M"]["_t"]
        tnew = hM[1:len(trk)+1]
        k = min(len(tnew), len(trk))
        xpred = 2.5 + 0.5*tnew[:k]
        xpred = np.where(xpred >= 3.0, xpred - 6.0, xpred)
        cmpr["M_tracker_err_max"] = float(np.max(np.abs(trk[:k, 2] - xpred)))
        cmpr["M_tracker_x_end"] = float(trk[k-1, 2])
        cmpr["M_tracker_crossed"] = bool(np.any(np.diff(trk[:k, 2]) < -5.0))
    for n in ("G", "Grel", "Goff", "Gchi"):
        if n in res:
            gp = os.path.join(a.out, n, "flrw.guard.txt")
            if os.path.exists(gp):
                with open(gp) as f:
                    res[n]["guard_text"] = f.read()[:600]
    sp = os.path.join(a.out, "U", "flrw.horizon_status_0.txt")
    if os.path.exists(sp):
        with open(sp) as f:
            cmpr["U_horizon_status"] = f.read().splitlines()[:4]
    out = {n: {k: v for k, v in r.items() if not k.startswith("_")} for n, r in res.items()}
    out["comparisons"] = cmpr
    with open(os.path.join(a.out, "t2_summary.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(json.dumps(out, indent=1))

    # ---- figures
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    floor = 1e-17
    fig, ax = plt.subplots(2, 2, figsize=(8.0, 6.0))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.97, wspace=0.28,
                        hspace=0.22)
    cols = fs.SERIES + ["k", "grey", "#8E44AD"]
    show = [n for n in ("U", "S", "Sf", "P", "A", "L", "D8", "D8s") if n in res
            and "_chis" in res[n]]
    for i, n in enumerate(show):
        ls = "-" if i < 5 else "--"
        ax[0, 0].semilogy(res[n]["_ts"], np.maximum(res[n]["_chis"], floor), ls,
                          color=cols[i % len(cols)], label=n)
        ax[0, 1].semilogy(res[n]["_t"], np.maximum(res[n]["_es"], floor), ls,
                          color=cols[i % len(cols)], label=n)
    for q in (ax[0, 0], ax[0, 1]):
        q.axhline(1e-12, **fs.GUIDE)
        q.set_xlabel("conformal time")
        q.legend(ncol=2, frameon=False)
    ax[0, 0].set_ylabel(r"$\chi_{\max}/\chi_{\min}-1$")
    ax[0, 1].set_ylabel(r"$E_{\max}/E_{\min}-1$")
    if "U" in res and "_amax" in res["U"]:
        for i, n in enumerate([m for m in ("S", "Sf", "P", "A", "L", "D8") if m in res
                               and "_amax" in res[m]]):
            if len(res[n]["_amax"]) == len(res["U"]["_amax"]):
                ax[1, 0].semilogy(res[n]["_t"], np.maximum(
                    spread(res[n]["_amax"], res["U"]["_amax"]), floor),
                    color=cols[(i+1) % len(cols)], label=n)
        ax[1, 0].axhline(1e-12, **fs.GUIDE)
        ax[1, 0].set_xlabel("conformal time")
        ax[1, 0].set_ylabel(r"$|\alpha_{\max}/\alpha_{\max}^{\rm U}-1|$")
        ax[1, 0].legend(ncol=2, frameon=False)
    for i, n in enumerate([m for m in ("A", "L", "M") if m in res and "_nmb" in res[m]]):
        ax[1, 1].plot(res[n]["_t"], res[n]["_nmb"], color=cols[i], label=n)
    ax[1, 1].set_xlabel("conformal time")
    ax[1, 1].set_ylabel("MeshBlocks")
    ax[1, 1].legend(frameon=False)
    fs.save(fig, os.path.join(a.out, "fig_t2_flrw"))
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.96, wspace=0.28)
    if trk is not None:
        ax[0].plot(tnew[:k], xpred, **fs.GUIDE, label="2.5 + 0.5 t, mapped into the box")
        ax[0].plot(tnew[:k], trk[:k, 2], color=fs.PAL["red"], lw=1.0, label="tracker (M)")
        ax[0].set_xlabel("conformal time")
        ax[0].set_ylabel("tracker x")
        ax[0].legend(frameon=False)
    for i, n in enumerate([m for m in ("C1", "C2", "C2n", "M") if m in res
                           and "_ratio" in res[m]]):
        ax[1].plot(res[n]["_t"][:-1], res[n]["_ratio"], color=cols[i], label=n)
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_xlabel("conformal time")
    ax[1].set_ylabel(r"$\Delta t\,c_{\max}/(0.25\,\Delta x_{\min})$")
    ax[1].legend(frameon=False, ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_t5_tracker"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
