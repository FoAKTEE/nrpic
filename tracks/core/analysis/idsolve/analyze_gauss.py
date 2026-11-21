#!/usr/bin/env python3
"""Test T1 of the initial-data solver: Gaussian density at rest, K = 0, against the exact
conformal factor of the format-1 construction of nrpic_cf (tracks/core/JOURNAL-idsolve.md).

    analyze_gauss.py [--ref64]

Reads the runs named gauss_* in runs.json, writes gauss_numbers.json and the figures
figs/gauss_error, figs/gauss_iter, figs/gauss_H (PDF and PNG).
"""
import argparse
import os
import sys

import numpy as np

import idlib
import idref

sys.path.insert(0, os.path.join(idlib.WT, "problems", "idsolve"))
import make_ic  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MASS, SIGMA, HALF = 1.0, 2.0, 16.0


def one(name, r):
    d = idlib.run_dir(r["run_id"])
    b = idlib.read_idsolve_bin(os.path.join(d, "gauss.idsolve.bin"))
    it, last = idlib.read_idsolve_txt(os.path.join(d, "gauss.idsolve.txt"))
    fld = idlib.read_field(os.path.join(d, "gauss.field.00000.bin"))
    rr, dx, _ = idlib.mesh_r(b)
    pe = make_ic.gaussian_psi(rr, MASS, SIGMA)
    err = b["psi"] - pe
    n = b["n"][0]
    c = slice(n//2 - 1, n//2 + 1)
    rel_c = float(np.mean(err[c, c, c]/(pe[c, c, c] - 1.0)))
    face = []
    for ax in range(3):
        for side in (0, n - 1):
            sl = [c, c, c]
            sl[ax] = side
            face.append(err[tuple(sl)].mean())
    mono = []
    for ax in range(3):
        for side in (0, n - 1):
            sl = [c, c, c]
            sl[ax] = side
            mono.append(float(np.mean(2.0*rr[tuple(sl)]*(b["psi"][tuple(sl)] - 1.0))))
    ng = r.get("ng", 4)
    rel = it[:, 1]
    fac = (rel[1:]/rel[:-1]) if len(rel) > 1 else np.array([])
    out = dict(run_id=r["run_id"], n=n, dx=dx, mode=r["mode"], ng=ng,
               comp=r.get("comp", 0.0),
               iterations=int(it[-1, 0]), cg_steps=int(it[:, 10].sum()),
               v_cycles=int(it[:, 11].sum()), cg_max_per_solve=int(it[:, 10].max()),
               last_factors=[float(v) for v in fac[-4:]],
               rel_final=float(rel[-1]),
               err_centre_rel=rel_c, err_max=float(np.abs(err).max()),
               err_rms=float(np.sqrt(np.mean(err**2))),
               err_face=float(np.mean(face)), monopole_mass=float(np.mean(mono)),
               H_before_max=float(it[0, 4]), H_before_rms=float(it[0, 5]),
               H_after_max_solver=float(it[-1, 4]), H_after_rms_solver=float(it[-1, 5]),
               F7_after_max=float(it[-1, 6]),
               H_field_interior_max=float(np.abs(idlib.interior(fld["H"], ng)).max()),
               H_field_interior_rms=float(np.sqrt(np.mean(idlib.interior(fld["H"], ng)**2))),
               H_field_all_max=float(np.abs(fld["H"]).max()),
               psi_centre=float(b["psi"][c, c, c].mean()),
               summary=last)
    return out, (rr, err, pe, b, it, fld)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref64", action="store_true",
                    help="also the sparse reference at 64 cells (minutes, several GB)")
    a = ap.parse_args()
    runs = idlib.load_json(os.path.join(idlib.HERE, "runs.json"))
    res, data = {}, {}
    for name in sorted(runs):
        if runs[name].get("test") != "t1" or not runs[name]["status"].startswith("exit 0"):
            continue
        res[name], data[name] = one(name, runs[name])

    # ---- predictions of the journal (entry 3): relative error of psi - 1 at the centre
    def pred(dx, mode, comp):
        cloud = 3.0/32.0 - comp
        lapl = 1.0/20.0 if mode == "stencil" else 0.0
        return (lapl - cloud)*(dx/SIGMA)**2
    # (no prediction for two ghost cells: the second-order monitor of the code is not
    # the seven-point Laplacian of psi and has its own truncation error)
    for name, r in res.items():
        r["err_centre_rel_predicted"] = (pred(r["dx"], r["mode"], r["comp"])
                                         if r["ng"] > 2 else float("nan"))

    # ---- independent reference: the same discrete system by a sparse direct solve
    ref = {}
    for n in (32, 64) if a.ref64 else (32,):
        name = "gauss_stencil_n%d" % n
        if name not in res:
            continue
        h = HALF/n      # lattice spacing dx/2
        x, u, m, _ = nio.read_nrp(os.path.join(idlib.SCRATCH, "idsolve_ic",
                                               "gauss_h%s.nrp" % ("%g" % h).replace(".", "p")))
        pr, hist = idref.solve_isolated(x, m, n, -HALF, HALF)
        diff = data[name][3]["psi"] - pr
        ref[name] = dict(max_abs_difference=float(np.abs(diff).max()),
                         reference_iterations=len(hist) - 1,
                         reference_residual=hist[-1],
                         reference_psi_max=float(pr.max()))
        res[name]["reference_max_abs_difference"] = ref[name]["max_abs_difference"]
    idlib.save_json(os.path.join(idlib.HERE, "gauss_numbers.json"),
                    dict(test="T1", mass=MASS, sigma=SIGMA, cases=res, reference=ref))

    fs.use_style()
    col = {32: fs.PAL["yellow"], 64: fs.PAL["red"], 128: fs.PAL["blue"]}

    # ---- figure 1: error profiles scaled by (dx/sigma)^2, and the centre against dx
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.97, wspace=0.28)
    ax = axs[0]
    for mode, ls in (("stencil", "-"), ("code", "--")):
        for n in (32, 64, 128):
            name = "gauss_%s_n%d" % (mode, n)
            if name not in data:
                continue
            rr, err, pe, b, it, fld = data[name]
            dx = res[name]["dx"]
            # mean of the error in radial bins of one cell
            bins = np.arange(0.0, HALF + dx, dx)
            k = np.digitize(rr.ravel(), bins) - 1
            num = np.bincount(k, weights=err.ravel(), minlength=len(bins))
            cnt = np.bincount(k, minlength=len(bins))
            ok = cnt > 0
            ax.plot((bins + 0.5*dx)[ok], (num[ok]/cnt[ok])/(dx/SIGMA)**2, ls=ls,
                    color=col[n], label="%s, dx = %g" % (mode, dx))
    rg = np.linspace(0.01, HALF, 400)
    rhot = make_ic.gaussian_source(rg, MASS, SIGMA)
    ax.plot(rg, -2.0*np.pi*rhot*SIGMA**2*(3.0/32.0), **fs.GUIDE)
    ax.plot(rg, -2.0*np.pi*rhot*SIGMA**2*(3.0/32.0 - 1.0/20.0), color="k", lw=1.0, ls=":")
    ax.set_xlim(0.0, 12.0)
    ax.set_xlabel(r"$r$")
    ax.set_ylabel(r"$(\psi - \psi_{\rm ex})/(\Delta x/\sigma)^2$")
    ax.legend(fontsize=8, ncol=1, loc="lower right")
    ax = axs[1]
    for mode, mk in (("stencil", "o"), ("code", "s")):
        xs, ys, ps = [], [], []
        for n in (32, 64, 128):
            name = "gauss_%s_n%d" % (mode, n)
            if name in res:
                xs.append(res[name]["dx"])
                ys.append(-res[name]["err_centre_rel"])
                ps.append(-res[name]["err_centre_rel_predicted"])
        ax.loglog(xs, ys, mk, color=fs.PAL["red"] if mode == "code" else fs.PAL["blue"],
                  label="measured, " + mode)
        ax.loglog(xs, ps, **(fs.GUIDE if mode == "code" else dict(color="k", lw=1.0, ls=":")))
    xs, ys = [], []
    for n in (32, 64):
        name = "gauss_code_n%d_comp" % n
        if name in res:
            xs.append(res[name]["dx"])
            ys.append(abs(res[name]["err_centre_rel"]))
    if xs:
        ax.loglog(xs, ys, "^", color=fs.PAL["green"], label="code, compensated 1/12")
        ax.loglog(xs, [(d/SIGMA)**2/96.0 for d in xs], color="k", lw=1.0, ls="-.")
    ax.set_xlabel(r"$\Delta x$")
    ax.set_ylabel(r"$-(\psi - \psi_{\rm ex})/(\psi_{\rm ex} - 1)$ at the centre")
    fs.no_minor_labels(ax, "x")
    ax.set_xticks([0.25, 0.5, 1.0])
    ax.set_xticklabels(["0.25", "0.5", "1"])
    ax.legend(fontsize=8, loc="upper left")
    fs.save(fig, os.path.join(idlib.FIGS, "gauss_error"))
    plt.close(fig)

    # ---- figure 2: residual against the iteration number
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.97, wspace=0.28)
    ax = axs[0]
    for mode, ls in (("stencil", "-"), ("code", "--")):
        for n in (32, 64, 128):
            name = "gauss_%s_n%d" % (mode, n)
            if name in data:
                it = data[name][4]
                ax.semilogy(it[:, 0], it[:, 1], ls=ls, marker=".", color=col[n],
                            label="%s, dx = %g" % (mode, res[name]["dx"]))
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel("largest residual / largest term")
    ax.legend(fontsize=8)
    ax = axs[1]
    for ng, c in ((2, fs.PAL["green"]), (3, fs.PAL["orange"]), (4, fs.PAL["red"])):
        name = "gauss_code_n64" if ng == 4 else "gauss_code_n64_ng%d" % ng
        if name in data:
            it = data[name][4]
            ax.semilogy(it[:, 0], it[:, 1], marker=".", color=c,
                        label="code, %d ghost cells" % ng)
    k = np.arange(4, 30)
    ax.semilogy(k, 3.0e-5*(1.0/3.0)**(k - 4), color="k", lw=1.0, ls=":")
    ax.semilogy(k, 3.0e-5*0.511**(k - 4), **fs.GUIDE)
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_ylim(1.0e-12, 3.0)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel("largest residual / largest term")
    ax.legend(fontsize=8)
    fs.save(fig, os.path.join(idlib.FIGS, "gauss_iter"))
    plt.close(fig)

    # ---- figure 3: the constraint monitor along a line through the innermost cells
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 1.0, 3.2))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.96)
    for name, c, lab in (("gauss_code_n64", fs.PAL["red"], "after, code"),
                         ("gauss_stencil_n64", fs.PAL["blue"], "after, stencil")):
        if name not in data:
            continue
        rr, err, pe, b, it, fld = data[name]
        n = b["n"][0]
        x = idlib.centres(n, -HALF, HALF)
        j = n//2
        if name == "gauss_code_n64":
            ax.semilogy(x, np.abs(b["H0"][:, j, j]), color="k", label="before (psi = 1)")
        ax.semilogy(x, np.abs(fld["H"][:, j, j]) + 1.0e-18, color=c, label=lab)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$|H|$ of the constraint monitor at $t = 0$")
    ax.set_ylim(1.0e-16, 3.0)
    ax.legend(fontsize=8)
    fs.save(fig, os.path.join(idlib.FIGS, "gauss_H"))
    plt.close(fig)

    for name in sorted(res):
        r = res[name]
        print("%-22s it %2d cg %3d vc %4d  centre %.3e (pred %.3e)  max %.2e  face %.2e  "
              "H: %.3e -> %.3e (field interior %.3e)  fac %s" % (
                  name, r["iterations"], r["cg_steps"], r["v_cycles"], r["err_centre_rel"],
                  r["err_centre_rel_predicted"], r["err_max"], r["err_face"],
                  r["H_before_max"], r["H_after_max_solver"], r["H_field_interior_max"],
                  " ".join("%.2f" % f for f in r["last_factors"][-3:])))
    for k, v in ref.items():
        print("reference %s: max|psi_code - psi_ref| = %.3e" % (k, v["max_abs_difference"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
