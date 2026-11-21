#!/usr/bin/env python3
"""Tests T2 and T3 of the initial-data solver: the expanding dust ball with the curvature
of its table (the solve must return psi = 1 up to the discretisation), and the same ball
with a triaxial strain of the particle positions (Hamiltonian residual before and after
the solve against resolution). tracks/core/JOURNAL-idsolve.md.

Reads the runs named ball_* and tri_* in runs.json, writes ball_numbers.json and the
figures figs/ball_psi, figs/ball_conv, figs/tri_slice (PDF and PNG).
"""
import os
import sys

import numpy as np

import idlib
from nrpic import figstyle as fs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RB, MTOT, HALF = 10.0, 1.0, 32.0
RHO = 3.0*MTOT/(4.0*np.pi*RB**3)


def one(name, r):
    d = idlib.run_dir(r["run_id"])
    fld = idlib.read_field(os.path.join(d, "ball.field.00000.bin"))
    n = fld["n"][0]
    out = dict(run_id=r["run_id"], n=n, dx=2.0*HALF/n, mode=r["mode"],
               nfilter=r.get("nfilter", 0), edge=r.get("edge", 0.0), e=r.get("e", 0.0))
    ng = 4
    hin = idlib.interior(fld["H"], ng)
    out.update(H_field_interior_max=float(np.abs(hin).max()),
               H_field_interior_rms=float(np.sqrt(np.mean(hin**2))),
               M_field_interior_max=float(max(np.abs(idlib.interior(fld[k], ng)).max()
                                              for k in ("Mx", "My", "Mz"))),
               M_field_interior_rms=float(np.sqrt(np.mean(sum(
                   idlib.interior(fld[k], ng)**2 for k in ("Mx", "My", "Mz"))))))
    if r["mode"] == "off":
        return out, (None, None, fld)
    b = idlib.read_idsolve_bin(os.path.join(d, "ball.idsolve.bin"))
    it, last = idlib.read_idsolve_txt(os.path.join(d, "ball.idsolve.txt"))
    rr, dx, (X, Y, Z) = idlib.mesh_r(b)
    u = b["psi"] - 1.0
    c = slice(n//2 - 1, n//2 + 1)
    mono, axisval = [], {}
    for ax, lab in ((0, "x"), (1, "y"), (2, "z")):
        for side in (0, n - 1):
            sl = [c, c, c]
            sl[ax] = side
            mono.append(float(np.mean(2.0*rr[tuple(sl)]*u[tuple(sl)])))
        # psi - 1 on the axis at |x| = 5 and 15 (mean of the four cells around the axis,
        # both signs, linear interpolation between the two nearest cell centres)
        xc = idlib.centres(n, -HALF, HALF)
        line = [c, c, c]
        line[ax] = slice(None)
        prof = u[tuple(line)]
        prof = prof.mean(axis=tuple(a for a in range(3) if a != ax))
        for rad in (5.0, 15.0):
            v = 0.5*(np.interp(rad, xc, prof) + np.interp(-rad, xc, prof))
            axisval["%s%g" % (lab, rad)] = float(v)
    rel = it[:, 1]
    fac = rel[1:]/rel[:-1] if len(rel) > 1 else np.array([])
    out.update(iterations=int(it[-1, 0]), cg_steps=int(it[:, 10].sum()),
               v_cycles=int(it[:, 11].sum()), cg_max_per_solve=int(it[:, 10].max()),
               last_factors=[float(v) for v in fac[-4:]], rel_final=float(rel[-1]),
               rel_first=float(rel[0]),
               psi_m1_max=float(np.abs(u).max()), psi_m1_rms=float(np.sqrt(np.mean(u**2))),
               psi_m1_centre=float(u[c, c, c].mean()),
               monopole_2r_u=float(np.mean(mono)), axis=axisval,
               H_before_max=float(it[0, 4]), H_before_rms=float(it[0, 5]),
               H_after_max_solver=float(it[-1, 4]), H_after_rms_solver=float(it[-1, 5]),
               F7_before_max=float(it[0, 6]), F7_before_rms=float(it[0, 7]),
               F7_after_max=float(it[-1, 6]), F7_after_rms=float(it[-1, 7]),
               summary=last)
    return out, (b, it, fld)


def main():
    runs = idlib.load_json(os.path.join(idlib.HERE, "runs.json"))
    res, data = {}, {}
    for name in sorted(runs):
        if runs[name].get("test") not in ("t2", "t3"):
            continue
        if not runs[name]["status"].startswith("exit 0"):
            continue
        res[name], data[name] = one(name, runs[name])
    idlib.save_json(os.path.join(idlib.HERE, "ball_numbers.json"),
                    dict(tests="T2, T3", Rb=RB, M=MTOT, rho=RHO, sixteen_pi_rho=16*np.pi*RHO,
                         cases=res))

    fs.use_style()
    col = {32: fs.PAL["yellow"], 64: fs.PAL["red"], 128: fs.PAL["blue"]}

    # ---- figure 1: psi - 1 of the solved ball against radius (T2), sharp and smooth
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.115, right=0.98, bottom=0.15, top=0.92, wspace=0.36)
    for ax, edge, title in ((axs[0], "sharp", "sharp surface"),
                            (axs[1], "smooth", "smooth edge, half-width 2")):
        for n in (32, 64, 128):
            name = "ball_%s_code_f0_n%d" % (edge, n)
            if name not in data:
                continue
            b = data[name][0]
            rr, dx, _ = idlib.mesh_r(b)
            bins = np.arange(0.0, HALF + dx, dx)
            k = np.digitize(rr.ravel(), bins) - 1
            u = (b["psi"] - 1.0).ravel()
            cnt = np.bincount(k, minlength=len(bins))
            mean = np.bincount(k, weights=u, minlength=len(bins))
            lo = np.full(len(bins), np.inf)
            hi = np.full(len(bins), -np.inf)
            np.minimum.at(lo, k, u)
            np.maximum.at(hi, k, u)
            ok = cnt > 0
            rc = (bins + 0.5*dx)[ok]
            ax.plot(rc, 1e4*mean[ok]/cnt[ok]/dx**2, color=col[n], label="dx = %g" % dx)
            fs.band(ax, rc, 1e4*lo[ok]/dx**2, 1e4*hi[ok]/dx**2, col[n])
        ax.axvline(RB, **fs.MASK_LINE)
        ax.axhline(0.0, **fs.THIN)
        ax.set_xlim(0.0, HALF)
        ax.set_xlabel(r"$r$")
        ax.set_ylabel(r"$10^4\,(\psi - 1)/\Delta x^2$")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8, loc="lower right")
    fs.save(fig, os.path.join(idlib.FIGS, "ball_psi"))
    plt.close(fig)

    # ---- figure 2: against resolution: max|psi - 1| (T2) and the residual before and
    #      after the solve (T2 and T3)
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.975, bottom=0.16, top=0.92, wspace=0.40)
    ax = axs[0]
    for key, c, mk, lab in (("ball_sharp_code_f0", fs.PAL["red"], "o", "sharp, code"),
                            ("ball_sharp_stencil_f0", fs.PAL["blue"], "s", "sharp, stencil"),
                            ("ball_sharp_code_f1", fs.PAL["orange"], "v", "sharp, code, 1 filter pass"),
                            ("ball_smooth_code_f0", fs.PAL["green"], "^", "smooth, code")):
        xs = [res[k]["dx"] for k in sorted(res) if k.startswith(key + "_n")]
        ys = [res[k]["psi_m1_max"] for k in sorted(res) if k.startswith(key + "_n")]
        if xs:
            o = np.argsort(xs)
            ax.loglog(np.array(xs)[o], np.array(ys)[o], mk + "-", color=c, label=lab, lw=1.0)
    xg = np.array([0.5, 2.0])
    ax.loglog(xg, 2.0*np.pi*RHO*xg**2, **fs.GUIDE)
    ax.set_xlabel(r"$\Delta x$")
    ax.set_ylabel(r"max $|\psi - 1|$")
    ax.set_title("ball with its table", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    for ax, pre, title in ((axs[1], "ball_sharp", "ball: rms of H"),
                           (axs[2], "tri", "triaxial ball: rms of H")):
        series = [("before", "H_before_rms", "code", "k", "o"),
                  ("after, code", "H_field_interior_rms", "code", fs.PAL["red"], "s"),
                  ("after, stencil", "H_field_interior_rms", "stencil", fs.PAL["blue"], "^")]
        for lab, key, mode, c, mk in series:
            nm = "%s_%s%s" % (pre, mode, "_f0" if pre.startswith("ball") else "")
            ks = [k for k in sorted(res) if k.startswith(nm + "_n")]
            if not ks:
                continue
            xs = np.array([res[k]["dx"] for k in ks])
            ys = np.array([res[k][key] for k in ks])
            o = np.argsort(xs)
            ax.loglog(xs[o], ys[o], mk + "-", color=c, label=lab, lw=1.0)
        ax.set_xlabel(r"$\Delta x$")
        ax.set_ylabel(r"rms of $H$ over the mesh")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=7)
    for ax in axs:
        fs.no_minor_labels(ax, "x")
        ax.set_xticks([0.5, 1.0, 2.0])
        ax.set_xticklabels(["0.5", "1", "2"])
    fs.save(fig, os.path.join(idlib.FIGS, "ball_conv"))
    plt.close(fig)

    # ---- figure 3: slices y = first plane above 0 of the triaxial ball at the finest mesh
    name = None
    for n in (128, 64, 32):
        if "tri_code_n%d" % n in data:
            name = "tri_code_n%d" % n
            break
    if name is not None:
        b, it, fld = data[name]
        n = b["n"][0]
        j = n//2
        ext = [-HALF, HALF, -HALF, HALF]
        fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.3))
        fig.subplots_adjust(left=0.065, right=0.945, bottom=0.14, top=0.90, wspace=0.48)
        panels = [(b["E"][:, j, :]/RHO, "E / rho", "magma", None),
                  (b["H0"][:, j, :]/(16*np.pi*RHO), "H before / 16 pi rho", "RdBu_r", 1.0),
                  ((b["psi"][:, j, :] - 1.0)*1.0e3, "(psi - 1) x 1000", "RdBu_r", None),
                  (np.log10(np.abs(fld["H"][:, j, :])/(16*np.pi*RHO) + 1e-30),
                   "log10 |H after| / 16 pi rho", "viridis", None)]
        for ax, (img, lab, cm, vm) in zip(axs, panels):
            kw = {}
            if cm == "RdBu_r":
                v = vm if vm is not None else np.abs(img).max()
                kw = dict(vmin=-v, vmax=v)
            elif cm == "viridis":
                kw = dict(vmin=-14.0, vmax=0.0)
            im = ax.imshow(img.T, origin="lower", extent=ext, cmap=cm, aspect="equal",
                           interpolation="nearest", rasterized=True, **kw)
            ax.set_xlim(-16, 16)
            ax.set_ylim(-16, 16)
            ax.set_xlabel(r"$x$", labelpad=-2)
            ax.set_title(lab, fontsize=8)
            cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
            cb.ax.tick_params(labelsize=7)
        axs[0].set_ylabel(r"$z$", labelpad=-4)
        fs.save(fig, os.path.join(idlib.FIGS, "tri_slice"))
        plt.close(fig)

    for name in sorted(res):
        r = res[name]
        if r["mode"] == "off":
            print("%-28s H field interior max %.3e rms %.3e | M max %.3e rms %.3e" % (
                name, r["H_field_interior_max"], r["H_field_interior_rms"],
                r["M_field_interior_max"], r["M_field_interior_rms"]))
            continue
        print("%-28s it %2d cg %3d(max %d) vc %4d | psi-1 max %.3e centre %+.3e 2ru %+.2e | "
              "H max %.3e -> %.3e rms %.3e -> %.3e | field int max %.2e rms %.2e | M rms %.2e" % (
                  name, r["iterations"], r["cg_steps"], r["cg_max_per_solve"], r["v_cycles"],
                  r["psi_m1_max"], r["psi_m1_centre"], r["monopole_2r_u"],
                  r["H_before_max"], r["H_after_max_solver"], r["H_before_rms"],
                  r["H_after_rms_solver"], r["H_field_interior_max"],
                  r["H_field_interior_rms"], r["M_field_interior_rms"]))
        if r["e"] > 0:
            print("      axis values of psi - 1: " + ", ".join(
                "%s %+.3e" % (k, v) for k, v in sorted(r["axis"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
