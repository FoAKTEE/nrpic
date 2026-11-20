#!/usr/bin/env python3
"""Tests P of the initial-data solver, second pass (journal entry 5): punctures in the
solve, psi = psi_s + u with psi_s = 1 + sum m_c/(2 |x - x_c|) in closed form.

  P1  one Bowen-York puncture (m = 1, P = (0.5, 0, 0)) at the origin, vacuum, against the
      multipole solution of python/nrpic/bowen_york.py (solve_axisym); stencil residual,
      and mode code with id_puncture_radius 1 and 3; N = 32, 64, 128 (half-width 16)
  P2  a puncture (m = 1, at rest) inside a Gaussian shell of particles at rest (mass 0.5,
      radius 6, width 1), against the radial solution of lap u = -2 pi Etilde/(psi_s + u)
      computed here; stencil residual and mode code (radius 3); N = 32, 64, 128
  P3  P2 and P1 on a refined mesh: root 32^3, static levels in |x_i| < 8 and < 4 (finest
      cell 0.25, as N = 128), mode code (radius 3) and stencil
  P4  three Bowen-York punctures with momenta and a spin (the data of Track F), vacuum,
      stencil residual, N = 32, 64, 128: self-convergence of u at the punctures, and the
      closed-form second-order corrections of nrpic_cf (comp_corr = approx) for comparison
  P5  the puncture of P1 inside the shell of P2 moving with u_x = 0.1, scalar and vector
      part in mode code (vector part: matter momentum; the Bowen-York curvature is left
      out of the numerical divergence), N = 64: P_ADM of the record
  P6  the puncture of P1 with the faces further out (journal entry 10): half-width 32 at
      dx = 1 and 0.5, half-width 64 at dx = 1, stencil residual: the error left by the
      r^-4 tail of the Bowen-York source beyond the sphere of the moments
  P7  the three punctures of P4 on refined meshes (journal entry 10): root 32^3, static
      levels |x_i| < 8 and < 6, then cubes of half-width 2, 1, 0.5 about each puncture
      (finest cell 0.25 to 0.03125), stencil residual: u at the punctures

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_p.py --exe <athena>
                            [--tests p1,p2,p3,p4,p5,p6,p7] [--jobs N]
    test_p.py --analyze <run directory>[,<run directory>...]
"""
import argparse
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
from nrpic import bowen_york as by
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PUNC = os.path.join(lib2.WT, "problems/idsolve/puncture.athinput")
HALF = 16.0
M1, P1X = 1.0, 0.5
SHELL = dict(mass=0.5, r0=6.0, width=1.0)
TRIPLE = [dict(m=1.0, pos=(-3.0, 0.0, 0.0), P=(0.0, 0.2, 0.0), S=(0.0, 0.0, 0.2)),
          dict(m=0.6, pos=(3.0, 1.0, 0.0), P=(0.0, -0.2, 0.1), S=(0.0, 0.0, 0.0)),
          dict(m=0.4, pos=(0.0, -4.0, 1.0), P=(0.1, 0.0, -0.1), S=(0.0, 0.0, 0.0))]


def mb_of(n):
    return 16 if n <= 64 else 32


def punc_sets(plist):
    s = {"problem/ncomp": len(plist)}
    for c, p in enumerate(plist):
        pre = "problem/comp%d_" % c
        s[pre + "type"] = "puncture"
        s[pre + "mass"] = p["m"]
        for a in range(3):
            s[pre + "x%d" % (a + 1)] = p["pos"][a]
            s[pre + "p%d" % (a + 1)] = p["P"][a]
            s[pre + "s%d" % (a + 1)] = p["S"][a]
    return s


def smr_sets():
    s = {"mesh_refinement/refinement": "static", "mesh_refinement/max_nmb_per_rank": 1024}
    for k, (lev, half) in enumerate(((1, 8.0), (2, 4.0))):
        s["refined_region%d/level" % (k + 1)] = lev
        for d in "123":
            s["refined_region%d/x%smin" % (k + 1, d)] = -half
            s["refined_region%d/x%smax" % (k + 1, d)] = half
    return s


def smr_punc_sets(lmax):
    """Static levels for the three punctures: |x_i| < 8 (level 1), |x_i| < 6 (level 2),
    then cubes about each puncture of half-width 2, 1, 0.5 (levels 3, 4, 5), up to lmax."""
    s = {"mesh_refinement/refinement": "static", "mesh_refinement/max_nmb_per_rank": 8192}
    boxes = [(1, (0.0, 0.0, 0.0), 8.0), (2, (0.0, 0.0, 0.0), 6.0)]
    for lev, half in ((3, 2.0), (4, 1.0), (5, 0.5)):
        if lev <= lmax:
            boxes += [(lev, p["pos"], half) for p in TRIPLE]
    for k, (lev, c, half) in enumerate(boxes):
        s["refined_region%d/level" % (k + 1)] = lev
        for a, d in enumerate("123"):
            s["refined_region%d/x%smin" % (k + 1, d)] = c[a] - half
            s["refined_region%d/x%smax" % (k + 1, d)] = c[a] + half
    return s


def build_cases(root, exe, tests):
    cases = []

    def add(name, sets, ic=None, n=None, may_fail=False, half=None):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        s = dict(lib2.mesh(n, mb_of(n), half)) if n else {}
        s.update(sets)
        lib2.make_input(PUNC, os.path.join(d, "in.athinput"), s)
        steps = list(ic or []) + [[exe, "-i", "in.athinput"]]
        cases.append(dict(name=name, dir=d, steps=steps, may_fail=may_fail))

    def shell_ic(h, u=0.0):
        return [lib2.py(lib2.MAKE_IC, "shell", "--mass", str(SHELL["mass"]), "--r0",
                        str(SHELL["r0"]), "--width", str(SHELL["width"]), "--h", str(h),
                        "--u", str(u), "--out", ".", "--prefix", "shell")]
    st = {"particles/id_residual": "stencil"}
    c1 = {"particles/id_residual": "code", "particles/id_puncture_radius": 1.0}
    c3 = {"particles/id_residual": "code", "particles/id_puncture_radius": 3.0}
    at_rest = {"problem/comp0_p1": 0.0}
    with_shell = {"particles/particle_file": "shell.nrp"}
    if "p1" in tests:
        for n in (32, 64, 128):
            add("p1_st_n%d" % n, st, n=n)
            add("p1_c1_n%d" % n, c1, n=n, may_fail=True)
            add("p1_c3_n%d" % n, c3, n=n, may_fail=True)
    if "p2" in tests:
        for n in (32, 64, 128):
            h = HALF/n
            add("p2_st_n%d" % n, dict(st, **at_rest, **with_shell), shell_ic(h), n=n)
            add("p2_c3_n%d" % n, dict(c3, **at_rest, **with_shell), shell_ic(h), n=n,
                may_fail=True)
    if "p3" in tests:
        s = dict(lib2.mesh(32, 8))
        s.update(smr_sets())
        add("p3_shell_c3", dict(s, **c3, **at_rest, **with_shell), shell_ic(0.125),
            may_fail=True)
        add("p3_shell_st", dict(s, **st, **at_rest, **with_shell), shell_ic(0.125),
            may_fail=True)
        add("p3_by_st", dict(s, **st), may_fail=True)
    if "p4" in tests:
        for n in (32, 64, 128):
            add("p4_st_n%d" % n, dict(st, **punc_sets(TRIPLE)), n=n)
    if "p5" in tests:
        add("p5_mov_n64", dict({"particles/id_residual": "code",
                                "particles/id_puncture_radius": 3.0,
                                "particles/id_vector": "true",
                                "particles/id_vector_residual": "code"}, **with_shell),
            shell_ic(0.25, u=0.1), n=64, may_fail=True)
    if "p6" in tests:
        for half, n in ((32.0, 64), (32.0, 128), (64.0, 128)):
            add("p6_h%d_n%d" % (half, n), st, n=n, half=half)
    if "p7" in tests:
        for lmax in (2, 3, 4, 5):
            s = dict(lib2.mesh(32, 8))
            s.update(smr_punc_sets(lmax))
            add("p7_l%d" % lmax, dict(s, **st, **punc_sets(TRIPLE)), may_fail=True)
    return cases


# ------------------------------------------------------------------------------ references
def shell_reference(m=M1, mass=SHELL["mass"], r0=SHELL["r0"], width=SHELL["width"]):
    """Radial solution of lap u = -2 pi Etilde/(1 + m/2r + u), u -> 0, regular at the
    puncture: u(r) = (1/r) int_0^r s^2 f ds + int_r^inf s f ds, iterated."""
    import make_ic
    r = np.linspace(0.0, r0 + 14.0*width, 400001)
    et = make_ic.shell_profile(r, mass, r0, width)
    u = np.zeros_like(r)
    rs = np.where(r > 0.0, r, 1.0)
    for _ in range(200):
        f = 2.0*np.pi*et/(1.0 + 0.5*m/rs + u)
        f[0] = 0.0
        a = np.concatenate(([0.0], np.cumsum(0.5*(r[1:]**2*f[1:] + r[:-1]**2*f[:-1])
                                             * np.diff(r))))
        b = np.concatenate(([0.0], np.cumsum(0.5*(r[1:]*f[1:] + r[:-1]*f[:-1])
                                             * np.diff(r))))
        unew = np.where(r > 0.0, a/rs, 0.0) + (b[-1] - b)
        err = np.max(np.abs(unew - u))
        u = unew
        if err < 1.0e-15:
            break
    return dict(r=r, u=u, m_adm=m + 2.0*a[-1], u0=float(u[0]))


def by_reference(m=M1, p=P1X):
    sol = by.solve_axisym(m, P=p, lmax=12)
    lr = np.log(sol["r"])
    u0 = sol["ul"][0]
    du0 = np.gradient(u0, sol["r"])

    def u_of(x, y, z):
        r = np.sqrt(x*x + y*y + z*z)
        mu = np.where(r > 0.0, x/np.where(r > 0.0, r, 1.0), 0.0)
        out = np.zeros_like(r)
        lrr = np.log(np.maximum(r, sol["r"][0]))
        for q, l in enumerate(sol["lvals"]):
            c = np.zeros(l + 1)
            c[l] = 1.0
            out += np.interp(lrr, lr, sol["ul"][q])*np.polynomial.legendre.legval(mu, c)
        return out

    def m_inside(R):
        """m + 2 Q(R), Q(R) = -R^2 u_0'(R): the mass that the moments of the source
        within radius R give."""
        return m - 2.0*R*R*float(np.interp(np.log(R), lr, du0))
    return dict(sol=sol, u=u_of, m_adm=sol["m_adm"], u0=sol["u0_centre"], m_inside=m_inside)


# ------------------------------------------------------------------------------ analysis
def psi_s(X, Y, Z, plist):
    out = np.ones_like(X)
    for p in plist:
        out += 0.5*p["m"]/np.sqrt((X - p["pos"][0])**2 + (Y - p["pos"][1])**2
                                  + (Z - p["pos"][2])**2)
    return out


def load_case(d):
    """Cell centres, u = psi - psi_s, monitor H and cell size from the dump of a case."""
    f = os.path.join(d, "punc.idsolve.bin")
    fb = os.path.join(d, "punc.idsolve.blk.bin")
    plist = TRIPLE if os.path.basename(d).startswith(("p4", "p7")) else \
        [dict(m=M1, pos=(0.0, 0.0, 0.0))]
    if os.path.exists(f):
        a = idlib.read_idsolve_bin(f)
        _, dx, (X, Y, Z) = idlib.mesh_r(a)
        out = dict(X=X, Y=Y, Z=Z, dx=np.full(X.shape, dx), psi=a["psi"], H=a["H"],
                   H0=a["H0"], level=np.zeros(X.shape, dtype=int),
                   half=float(np.abs(X).max() + 0.5*dx))
    elif os.path.exists(fb):
        a = lib2.read_blk(fb)
        X, Y, Z, dxm = lib2.blk_coords(a)
        out = dict(X=X, Y=Y, Z=Z, dx=dxm[:, None, None, None]*np.ones_like(X), psi=a["psi"],
                   H=a["H"], H0=a["H0"],
                   level=(a["level"] - a["level"].min())[:, None, None, None]
                   * np.ones(X.shape, dtype=int), half=float(np.abs(a["box"]).max()))
    else:
        return None
    out["u"] = out["psi"] - psi_s(out["X"], out["Y"], out["Z"], plist)
    out["r"] = np.sqrt(out["X"]**2 + out["Y"]**2 + out["Z"]**2)
    return out


def errors(c, uref, rp):
    """Errors of u against the reference: innermost cells (r < dx), within rp of the
    puncture, between rp and 12 (away from the faces), and the monitor after the solve
    outside rp and 4 length units from the faces."""
    e = c["u"] - uref
    r, dx = c["r"], c["dx"]
    inner = r < 0.9*dx
    near = (r < rp) & ~inner
    mid = (r >= rp) & (r < 12.0)
    half = c.get("half", HALF)
    face = ((np.abs(c["X"]) > half - 4) | (np.abs(c["Y"]) > half - 4)
            | (np.abs(c["Z"]) > half - 4))
    out = dict(e_inner=float(np.mean(e[inner])), u_inner=float(np.mean(c["u"][inner])),
               e_mid_mean=float(np.mean(e[mid])),
               e_near_max=float(np.max(np.abs(e[near]))) if near.any() else 0.0,
               e_mid_max=float(np.max(np.abs(e[mid]))),
               e_mid_rms=float(np.sqrt(np.mean(e[mid]**2))),
               e_3_12_max=float(np.max(np.abs(e[(r >= 3.0) & (r < 12.0)]))),
               e_1_3_max=float(np.max(np.abs(e[(r >= 1.0) & (r < 3.0)]))),
               H_after_max=float(np.max(np.abs(c["H"][(r >= rp) & ~face]))),
               H_before_max=float(np.max(np.abs(c["H0"][(r >= rp) & ~face]))))
    if c["level"].max() > 0:
        out["levels"] = {}
        for lv in range(int(c["level"].max()) + 1):
            mk = (c["level"] == lv) & (r >= rp) & ~face
            out["levels"][str(lv)] = dict(
                e_max=float(np.max(np.abs(e[(c["level"] == lv) & (r < 12.0)]))),
                H_after_max=float(np.max(np.abs(c["H"][mk]))) if mk.any() else None)
    return out, e


def record(d):
    rec = os.path.join(d, "punc.idsolve.txt")
    if not os.path.exists(rec):
        return {}
    rows, tail = lib2.summary(rec)
    out = dict(outer=int(rows[-1][0]), summary=tail, far=lib2.far_line(rec),
               lin=int(rows[:, 10].sum()), vcycles=int(rows[:, 11].sum()),
               converged=any(t.startswith("converged") for t in tail))
    if rows.shape[1] > 13:
        out.update(relv_first=float(rows[0][13]), relv_last=float(rows[-1][13]),
                   mmax_first=float(rows[0][16]), mmax_last=float(rows[-1][16]))
    return out


def analyze(roots, status, tag="", out_dir=None):
    """Cases of every directory in roots; numbers and figures with the suffix tag into
    out_dir (default the first root)."""
    if isinstance(roots, str):
        roots = [roots]
    root = out_dir or roots[0]
    res = dict(run=lib2.run_id(), sources=[os.path.basename(r.rstrip("/")) for r in roots],
               status=status or {}, cases={})
    byr = by_reference()
    shr = shell_reference()
    res["reference"] = dict(by_m_adm=byr["m_adm"], by_u0=byr["u0"],
                            by_m_inside_16=byr["m_inside"](HALF),
                            shell_m_adm=shr["m_adm"], shell_u0=shr["u0"])
    prof = {}
    for d in sorted(sum([glob.glob(os.path.join(r, "p*_*")) for r in roots], [])):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        e = dict(record(d))
        c = load_case(d)
        if c is None:
            res["cases"][name] = e
            continue
        rp = 3.0 if "_c3" in name else 1.0
        if name.startswith(("p1", "p6")) or name == "p3_by_st":
            uref = byr["u"](c["X"], c["Y"], c["Z"])
            st, err = errors(c, uref, rp)
            e.update(st)
            e["u_ref_inner"] = float(byr["u0"])
            e["half"] = c["half"]
            e["dx_min"] = float(c["dx"].min())
            e["m_inside_ref"] = float(byr["m_inside"](c["half"]))
        elif name.startswith(("p2", "p3_shell")):
            uref = np.interp(c["r"], shr["r"], shr["u"])
            st, err = errors(c, uref, rp)
            e.update(st)
        elif name.startswith(("p4", "p7")):
            pts = {}
            for k, p in enumerate(TRIPLE):
                rr = np.sqrt((c["X"] - p["pos"][0])**2 + (c["Y"] - p["pos"][1])**2
                             + (c["Z"] - p["pos"][2])**2)
                mk = rr < 0.9*c["dx"]
                lam = 1.0 + sum(0.5*q["m"]/np.linalg.norm(np.subtract(p["pos"], q["pos"]))
                                for j, q in enumerate(TRIPLE) if j != k)
                ua = by.approx_u(np.array([p["pos"]]) + 1e-9, p["pos"], p["m"], p["P"],
                                 p["S"], lam=lam)
                pts[str(k)] = dict(u=float(np.mean(c["u"][mk])), u_approx=float(ua[0]),
                                   lam=float(lam), ncell=int(mk.sum()),
                                   dx=float(c["dx"][mk].min()))
            e["punctures"] = pts
            e["ncells"] = int(c["X"].size)
            face = ((np.abs(c["X"]) > HALF - 4) | (np.abs(c["Y"]) > HALF - 4)
                    | (np.abs(c["Z"]) > HALF - 4))
            far = np.ones(c["X"].shape, dtype=bool)
            for p in TRIPLE:
                far &= np.sqrt((c["X"] - p["pos"][0])**2 + (c["Y"] - p["pos"][1])**2
                               + (c["Z"] - p["pos"][2])**2) >= p["m"]
            e["H_after_max"] = float(np.max(np.abs(c["H"][far & ~face])))
            e["H_before_max"] = float(np.max(np.abs(c["H0"][far & ~face])))
            err = None
        else:
            err = None
        if err is not None and c["level"].max() == 0:
            # profile along the x axis (the cells nearest to y = z = 0)
            n = c["X"].shape[0]
            j = n//2
            prof[name] = (c["X"][:, j, j], c["u"][:, j, j], err[:, j, j], c["dx"][0, 0, 0])
        res["cases"][name] = e
    out = os.path.join(root, "test_p_numbers%s.json" % tag)
    lib2.save_json(out, res)
    figs = figure(res, prof, byr, shr, root, tag)
    if any(k.startswith(("p4", "p6", "p7")) for k in res["cases"]):
        figs += figure_extra(res, root, tag)
    lib2.publish([out] + figs)
    return res


def figure_extra(res, root, tag=""):
    """(a) the mean error of u of the vacuum puncture against the half-width of the mesh
    (P1, P6); (b) the deficit of M_psi against the ADM mass; (c) u at the three punctures
    against the cell size there (P4 uniform, P7 refined)."""
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.5))
    cs = res["cases"]
    for dx, mk, c in ((1.0, "o-", fs.PAL["blue"]), (0.5, "s-", fs.PAL["red"])):
        hs, off, dm = [], [], []
        for k in sorted(cs):
            e = cs[k]
            if not (k.startswith(("p1_st", "p6")) and "e_mid_mean" in e and "half" in e):
                continue
            if abs(e["dx_min"] - dx) > 1e-9:
                continue
            hs.append(e["half"])
            off.append(abs(e["e_mid_mean"]))
            dm.append(res["reference"]["by_m_adm"] - e["far"]["M"])
        if hs:
            o = np.argsort(hs)
            axs[0].loglog(np.array(hs)[o], np.array(off)[o], mk, color=c,
                          label=r"$\Delta x=%g$" % dx)
            axs[1].loglog(np.array(hs)[o], np.array(dm)[o], mk, color=c,
                          label=r"$\Delta x=%g$" % dx)
    hh = np.array([16.0, 64.0])
    axs[0].loglog(hh, 2.7e-4*(16.0/hh)**2, "k:", lw=0.8, label=r"$\propto R^{-2}$")
    axs[1].loglog(hh, 0.026*(16.0/hh), "k:", lw=0.8, label=r"$\propto R^{-1}$")
    axs[0].set_ylabel(r"$|\langle u-u_{\rm ref}\rangle|$, $1<r<12$")
    axs[1].set_ylabel(r"$M_{\rm ADM}-M_\psi$")
    for ax in axs[:2]:
        ax.set_xlabel("half-width $R$ of the mesh")
        ax.set_xticks([16, 32, 64])
        ax.set_xticklabels(["16", "32", "64"])
        ax.minorticks_off()
        ax.legend(fontsize=5)
    cols = (fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"])
    for k in range(3):
        for pre, mk in (("p4", "o--"), ("p7", "s-")):
            xs, us = [], []
            for name in sorted(cs):
                e = cs[name]
                if name.startswith(pre) and "punctures" in e:
                    xs.append(e["punctures"][str(k)].get("dx", 2*HALF/int(name.split("n")[-1])
                                                         if "_n" in name else np.nan))
                    us.append(e["punctures"][str(k)]["u"])
                    ua = e["punctures"][str(k)]["u_approx"]
            if xs:
                o = np.argsort(xs)
                axs[2].semilogx(np.array(xs)[o], np.array(us)[o], mk, color=cols[k], ms=3,
                                label="puncture %d, %s" % (k + 1, "uniform" if pre == "p4"
                                                           else "refined"))
                axs[2].axhline(ua, color=cols[k], lw=0.6, ls=":")
    axs[2].set_xlabel(r"cell size at the puncture")
    axs[2].set_ylabel(r"$u$ at the puncture")
    axs[2].legend(fontsize=4.5)
    fig.tight_layout()
    p = os.path.join(root, "test_p_extra" + tag)
    fs.save(fig, p)
    plt.close(fig)
    return [p + ".png", p + ".pdf"]


def figure(res, prof, byr, shr, root, tag=""):
    fs.use_style()
    col = {32: fs.PAL["yellow"], 64: fs.PAL["red"], 128: fs.PAL["blue"]}
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0))
    # (a) P1 stencil: u along x against the reference; (b) its error scaled by dx^2
    for col_i, (pre, title) in enumerate((("p1_st", "P1 stencil"), ("p1_c3", "P1 code, r_p = 3"),
                                          ("p2_st", "P2 stencil"))):
        ax, axe = axs[0][col_i], axs[1][col_i]
        for n in (32, 64, 128):
            k = "%s_n%d" % (pre, n)
            if k not in prof:
                continue
            x, u, e, dx = prof[k]
            ax.plot(x, u, "o", ms=2, color=col[n], label="$N=%d$" % n)
            axe.plot(x, np.abs(e)/dx**2, "-", color=col[n], label="$N=%d$" % n)
        xx = np.linspace(-HALF, HALF, 801) + 1e-3
        if pre.startswith("p1"):
            ax.plot(xx, byr["u"](xx, 0*xx + 1e-3, 0*xx + 1e-3), "k-", lw=0.8,
                    label="reference")
        else:
            ax.plot(xx, np.interp(np.abs(xx), shr["r"], shr["u"]), "k-", lw=0.8,
                    label="reference")
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("$x$ ($y$, $z$ nearest 0)")
        ax.set_ylabel("$u=\\psi-\\psi_s$")
        axe.set_yscale("log")
        axe.set_xlabel("$x$")
        axe.set_ylabel("$|u-u_{\\rm ref}|/\\Delta x^2$")
        ax.legend(fontsize=5)
    fig.tight_layout()
    p = os.path.join(root, "test_p_profiles" + tag)
    fs.save(fig, p)
    plt.close(fig)
    out = [p + ".png", p + ".pdf"]
    # convergence summary
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.4))
    for pre, mk, lab in (("p1_st", "o-", "P1 stencil"), ("p1_c1", "s--", "P1 code r_p=1"),
                         ("p1_c3", "^-", "P1 code r_p=3"), ("p2_st", "o-", "P2 stencil"),
                         ("p2_c3", "^-", "P2 code r_p=3")):
        ns, a, b, h = [], [], [], []
        for n in (32, 64, 128):
            e = res["cases"].get("%s_n%d" % (pre, n), {})
            if "e_mid_max" in e:
                ns.append(2*HALF/n)
                a.append(abs(e["e_inner"]))
                b.append(e["e_mid_max"])
                h.append(max(e["H_after_max"], 1e-16))
        if ns:
            axs[0].loglog(ns, a, mk, label=lab)
            axs[1].loglog(ns, b, mk, label=lab)
            axs[2].loglog(ns, h, mk, label=lab)
    for ax, t in zip(axs, ("error of $u$ at the puncture", "max error of $u$, $r_p<r<12$",
                           "monitor $|H|$ after, outside $r_p$")):
        ax.set_xlabel(r"$\Delta x$")
        ax.set_title(t, fontsize=8)
        ax.set_xticks([0.25, 0.5, 1.0])
        ax.set_xticklabels(["0.25", "0.5", "1"])
        ax.minorticks_off()
    xs = np.array([0.25, 1.0])
    axs[1].loglog(xs, 1e-3*xs**2, "k:", lw=0.8, label=r"$\propto\Delta x^2$")
    axs[0].legend(fontsize=5)
    axs[1].legend(fontsize=5)
    fig.tight_layout()
    p2 = os.path.join(root, "test_p_convergence" + tag)
    fs.save(fig, p2)
    plt.close(fig)
    return out + [p2 + ".png", p2 + ".pdf"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=lib2.EXE)
    ap.add_argument("--tests", default="p1,p2,p3,p4,p5")
    ap.add_argument("--tag", default="", help="suffix of the files of --analyze")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--analyze", default="", help="comma-separated run directories")
    a = ap.parse_args()
    tag = "" if a.tests == "p1,p2,p3,p4,p5" else "_" + a.tests.replace(",", "")
    if a.analyze:
        analyze(a.analyze.split(","), None, tag=a.tag, out_dir=lib2.run_root())
        return 0
    root = lib2.run_root()
    cases = build_cases(root, os.path.abspath(a.exe), a.tests.split(","))
    # the largest cases first, so that they do not end the run alone
    cases.sort(key=lambda c: ("n128" not in c["name"] and "p3" not in c["name"]
                              and "p7_l5" not in c["name"]))
    status = lib2.run_cases(cases, a.jobs)
    analyze([root], status, tag=tag)
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    print("failed cases:", bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
