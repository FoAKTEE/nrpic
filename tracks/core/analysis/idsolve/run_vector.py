#!/usr/bin/env python3
"""Tests V0 to V2 of the vector equation of the initial-data solver (<particles>
id_vector; tracks/core/interfaces/id_solver.md, section 10; predictions in
tracks/core/JOURNAL-idsolve.md, entry 9).

    run_vector.py --exe NEW --base PUBLISHED [--analyze]

V0  without id_vector the new executable writes the same bytes as the published one:
    gauss_code_n32 (T1) and torus_code_p1_n32 (T4), every output file but the log.
V1  moving Gaussian (u_x = 0.1, K = 0, Abar(trial) = 0), N = 32, 64, modes stencil and
    code: (a) the right side written by the code against 8 pi times the cloud-in-cell
    deposit of m u_x from the particle file; (b) the compact operator, applied here with
    the Robin fill of the code, to the W of the code against that right side; (c) the
    iteration record.
V2  the same runs against the semi-analytic continuum W (vector_reference below); ADM
    momentum from the flux of L W through the faces.
Runs are registered by hand (tracks/core/tools/run_registered.py); ids and numbers go to
vector_numbers.json, figures to figs/vector_*.
"""
import argparse
import filecmp
import glob
import os
import struct
import subprocess
import sys
import time

import numpy as np
from scipy.integrate import cumulative_trapezoid

import idlib
import idref
import run_tests
from nrpic import figstyle as fs
from nrpic import io as nio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

IC = run_tests.IC
OUT = os.path.join(idlib.HERE, "vector_numbers.json")
VEC_FIELDS = ("Wx", "Wy", "Wz", "sx", "sy", "sz", "Fx", "Fy", "Fz", "Mx", "My", "Mz",
              "Mx0", "My0", "Mz0")


def registered(purpose, tag, inputs, cmd):
    full = [sys.executable, os.path.join(idlib.WT, "tracks/core/tools/run_registered.py"),
            "--purpose", purpose, "--tag", tag, "--cores", "1"]
    for f in inputs:
        full += ["--input", f]
    out = subprocess.run(full + ["--"] + cmd, capture_output=True, text=True)
    lines = out.stdout.strip().splitlines()
    if len(lines) < 2:
        raise RuntimeError(out.stderr)
    time.sleep(1.2)
    return lines[-1], lines[-2]


def read_idvector_bin(path):
    with open(path, "rb") as f:
        if f.read(8) != b"NRIDVEC1":
            raise ValueError("%s: bad magic" % path)
        n = struct.unpack("3q", f.read(24))
        box = struct.unpack("6d", f.read(48))
        nf, = struct.unpack("q", f.read(8))
        out = dict(n=n, box=box)
        nc = n[0]*n[1]*n[2]
        for name in VEC_FIELDS[:nf]:
            out[name] = np.fromfile(f, dtype=np.float64, count=nc).reshape(n, order="F")
    return out


# ---------------------------------------------------------------- the compact operator
def robin_pad(u, lo, hi, ng=1):
    """u[i, j, k] on n^3 cells -> padded with ng ghost layers filled as MGRobinFill does
    (r u equal in a ghost cell and its mirror cell, directions x, y, z in turn over the
    full extent of the others), centre at the origin."""
    n = u.shape[0]
    h = (hi - lo)/n
    p = np.zeros(tuple(s + 2*ng for s in u.shape))
    p[ng:-ng, ng:-ng, ng:-ng] = u
    c = lo + (np.arange(-ng, n + ng) + 0.5)*h       # centres including ghosts
    for ax in range(3):
        others = [b for b in range(3) if b != ax]
        shp = [1, 1, 1]
        shp[others[0]] = n + 2*ng
        g0 = c.reshape(shp)
        shp = [1, 1, 1]
        shp[others[1]] = n + 2*ng
        g1 = c.reshape(shp)
        t2 = g0**2 + g1**2                            # broadcast over the two others
        for nn in range(ng):
            for side in (0, 1):
                if side == 0:
                    ig, im = ng - 1 - nn, ng + nn
                else:
                    ig, im = ng + n + nn, ng + n - 1 - nn
                xg, xm = c[ig], c[im]
                q = np.sqrt((xm*xm + t2)/(xg*xg + t2))
                sg = [slice(None)]*3
                sm = [slice(None)]*3
                sg[ax] = slice(ig, ig + 1)
                sm[ax] = slice(im, im + 1)
                p[tuple(sg)] = q*p[tuple(sm)]
    return p


def compact_operator(W, lo, hi):
    """(Delta_L W)_i on the active cells with the compact stencils of the code."""
    n = W[0].shape[0]
    h = (hi - lo)/n
    P = [robin_pad(w, lo, hi, 1) for w in W]
    s = slice(1, -1)
    sp_, sm_ = slice(2, None), slice(0, -2)

    def at(a, ix, iy, iz):
        return a[ix, iy, iz]
    out = []
    for i in range(3):
        a = P[i]
        lap = (at(a, sp_, s, s) + at(a, sm_, s, s) + at(a, s, sp_, s) + at(a, s, sm_, s)
               + at(a, s, s, sp_) + at(a, s, s, sm_) - 6.0*at(a, s, s, s))/h**2
        sl = [s, s, s]
        slp, slm = list(sl), list(sl)
        slp[i], slm[i] = sp_, sm_
        gd = (a[tuple(slp)] + a[tuple(slm)] - 2.0*a[s, s, s])/h**2
        for j in range(3):
            if j == i:
                continue
            b = P[j]
            def sh(di, dj):
                ss = [s, s, s]
                ss[i] = sp_ if di > 0 else sm_
                ss[j] = sp_ if dj > 0 else sm_
                return b[tuple(ss)]
            gd = gd + (sh(1, 1) - sh(1, -1) - sh(-1, 1) + sh(-1, -1))/(4.0*h*h)
        out.append(lap + gd/3.0)
    return out


# ------------------------------------------------------------ semi-analytic continuum W
def vector_reference(q_of_r, rmax, X, Y, Z, nr=200001):
    """Continuum W of lap W_i + (1/3) d_i d_j W_j = 8 pi q(r) e_x (q radial, zero beyond
    rmax): W = (7/8) V - (1/8)(grad U + x_j grad V_j), lap V_x = 8 pi q,
    lap U = -8 pi x q (l = 0 and l = 1 radial Green's functions)."""
    r = np.linspace(0.0, rmax, nr)
    g = 8.0*np.pi*q_of_r(r)
    G = -8.0*np.pi*r*q_of_r(r)
    A = cumulative_trapezoid(g*r*r, r, initial=0.0)          # int_0^r g r'^2
    B = A[-1]*0.0 + (np.trapz(g*r, r) - cumulative_trapezoid(g*r, r, initial=0.0))
    C = cumulative_trapezoid(G*r**3, r, initial=0.0)         # int_0^r G r'^3
    D = np.trapz(G, r) - cumulative_trapezoid(G, r, initial=0.0)   # int_r^inf G
    R = np.sqrt(X*X + Y*Y + Z*Z)
    Rc = np.minimum(R, rmax)
    Ai = np.interp(Rc, r, A)
    Bi = np.where(R < rmax, np.interp(Rc, r, B), 0.0)
    Ci = np.interp(Rc, r, C)
    Di = np.where(R < rmax, np.interp(Rc, r, D), 0.0)
    v = -(Ai/R + Bi)
    dv = Ai/R**2                                             # v'(r)
    u = -(Ci/R**2 + R*Di)/3.0
    du = -(-2.0*Ci/R**3 + Di)/3.0                            # u'(r)
    xs = (X, Y, Z)
    W = []
    for i in range(3):
        dU = (du - u/R)*X*xs[i]/R**2 + (u/R if i == 0 else 0.0)
        xdV = X*dv*xs[i]/R
        W.append((7.0/8.0)*(v if i == 0 else 0.0) - (dU + xdV)/8.0)
    return W


def gauss_q(meta_u, mass, sigma, rcut):
    sys.path.insert(0, os.path.join(idlib.WT, "problems", "idsolve"))
    import make_ic
    def q(r):
        out = meta_u*make_ic.gaussian_source(r, mass, sigma)*make_ic.gaussian_psi(r, mass, sigma)
        return np.where(r <= rcut, out, 0.0)
    return q


# ------------------------------------------------------------------------- the runs
def run_all(a):
    res = idlib.load_json(OUT) if os.path.exists(OUT) else {}
    # V0
    v0 = {}
    ginp = os.path.join(idlib.WT, "problems/idsolve/gaussian.athinput")
    tinp = os.path.join(idlib.WT, "problems/idsolve/torus.athinput")
    gnrp = run_tests.ic_gauss(0.5)
    wnrp = run_tests.ic_wave(32, 1)
    cases = {}
    if not a.v0_only or "gauss" in a.v0_only:
        cases["gauss_code_n32"] = (ginp, gnrp, run_tests.mesh_args(32, 16) + [
                 "particles/id_residual=code", "particles/particle_file=gauss_h0p5.nrp"])
    if not a.v0_only or "torus" in a.v0_only:
        cases["torus_code_p1_n32"] = (tinp, wnrp, run_tests.mesh_args(32, 16) + [
                 "particles/id_residual=code",
                 "particles/particle_file=" + os.path.basename(wnrp)])
    for name, (inp, nrp, args) in cases.items():
        ids = {}
        for label, exe in (("published", a.base), ("new", a.exe)):
            rid, st = registered("initial-data solver, test V0: %s without id_vector, %s "
                                 "executable" % (name, label), "idsolve-v0-%s-%s" % (name, label),
                                 [inp, nrp], [exe, "-i", os.path.basename(inp)] + args)
            ids[label] = (rid, st)
            print("V0 %s %s %s %s" % (name, label, rid, st), flush=True)
        da, db = idlib.run_dir(ids["published"][0]), idlib.run_dir(ids["new"][0])
        files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(da, "*"))
                       if not os.path.islink(p) and os.path.basename(p) != "run.log")
        diff = [f for f in files if not filecmp.cmp(os.path.join(da, f), os.path.join(db, f),
                                                    shallow=False)]
        v0[name] = dict(published=ids["published"][0], new=ids["new"][0], files=files,
                        differ=diff)
        print("V0 %s: %d files compared, differ: %s" % (name, len(files), diff), flush=True)
    res.setdefault("V0", {}).update(v0)
    idlib.save_json(OUT, res)
    if a.v0_only:
        return
    # V1, V2
    binp = os.path.join(idlib.WT, "problems/idsolve/gaussian_boost.athinput")
    runs = res.get("runs", {})
    for n in (32, 64):
        h = 16.0/n
        nrp = os.path.join(IC, "gauss_h%s_u0p1.nrp" % run_tests.fmt(h))
        if not os.path.exists(nrp):
            subprocess.run([sys.executable, os.path.join(idlib.WT, "problems/idsolve/make_ic.py"),
                            "boost", "--in", run_tests.ic_gauss(h), "--u", "0.1", "--out", IC],
                           check=True)
        for mode in ("stencil", "code"):
            name = "gboost_%s_n%d" % (mode, n)
            rid, st = registered("initial-data solver, tests V1/V2: moving Gaussian with the "
                                 "vector equation, %s" % name, "idsolve-" + name, [binp, nrp],
                                 [a.exe, "-i", os.path.basename(binp)]
                                 + run_tests.mesh_args(n, 16 if n == 32 else 32)
                                 + ["particles/id_residual=" + mode,
                                    "particles/particle_file=" + os.path.basename(nrp)])
            runs[name] = dict(run=rid, status=st, n=n, mode=mode, dx=32.0/n,
                              particle_file=nrp)
            print("V1 %s %s %s" % (name, rid, st), flush=True)
    res["runs"] = runs
    idlib.save_json(OUT, res)


def analyze():
    res = idlib.load_json(OUT)
    lo, hi = -16.0, 16.0
    q = gauss_q(0.1, 1.0, 2.0, 14.0)
    out = {}
    curves = {}
    for name, r in sorted(res["runs"].items()):
        d = idlib.run_dir(r["run"])
        n = r["n"]
        v = read_idvector_bin(os.path.join(d, "gboost.idvector.bin"))
        txt, last = idlib.read_idsolve_txt(os.path.join(d, "gboost.idsolve.txt"))
        x, u, m, _ = nio.read_nrp(r["particle_file"])
        sx = 8.0*np.pi*idref.cic_open(np.asarray(x), np.asarray(m)*np.asarray(u)[:, 0],
                                      n, lo, hi)
        # (a) right side
        ea = float(np.abs(v["sx"] - sx).max()/np.abs(sx).max())
        eyz = float(max(np.abs(v["sy"]).max(), np.abs(v["sz"]).max())/np.abs(sx).max())
        # (b) the compact operator applied to the W of the code
        W = [v["Wx"], v["Wy"], v["Wz"]]
        AW = compact_operator(W, lo, hi)
        S = [v["sx"], v["sy"], v["sz"]]
        eb = float(max(np.abs(AW[i] - S[i]).max() for i in range(3))/np.abs(sx).max())
        # (c) iteration record: factors of the vector residual
        relv = txt[:, 13]
        fac = relv[1:]/relv[:-1]
        # V2: continuum reference
        c = idlib.centres(n, lo, hi)
        X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
        Wr = vector_reference(q, 14.0, X, Y, Z)
        i0 = n//2 - 1
        inner = (slice(i0, i0 + 2),)*3
        e_in = float(np.mean((W[0][inner] - Wr[0][inner])/Wr[0][inner]))
        # face centres (the 4 cells around the centre of each face)
        fc = []
        for ax in range(3):
            for side in (0, n - 1):
                sl = [slice(i0, i0 + 2)]*3
                sl[ax] = slice(side, side + 1)
                fc.append(float(np.mean((W[0][tuple(sl)] - Wr[0][tuple(sl)])
                                        / Wr[0][tuple(sl)])))
        e_face = float(np.max(np.abs(fc)))
        # ADM momentum: (1/8 pi) flux of (L W)_xj through the faces, L W with central
        # differences on the ghost-padded W, at the outermost active cells
        h = (hi - lo)/n
        Pp = [robin_pad(w, lo, hi, 1) for w in W]
        s = slice(1, -1)

        def dcen(a, ax):
            sp_ = [s, s, s]
            sm_ = [s, s, s]
            sp_[ax] = slice(2, None)
            sm_[ax] = slice(0, -2)
            return (a[tuple(sp_)] - a[tuple(sm_)])/(2.0*h)
        dW = [[dcen(Pp[b], ax) for b in range(3)] for ax in range(3)]   # dW[a][b] = d_a W_b
        div = dW[0][0] + dW[1][1] + dW[2][2]
        LW = [[dW[i][j] + dW[j][i] - (2.0/3.0*div if i == j else 0.0) for j in range(3)]
              for i in range(3)]
        flux = 0.0
        for ax in range(3):
            flux += (LW[0][ax][(slice(None),)*ax + (n - 1,)].sum()
                     - LW[0][ax][(slice(None),)*ax + (0,)].sum())*h*h
        P_flux = flux/(8.0*np.pi)
        P_sum = float(np.sum(np.asarray(m)*np.asarray(u)[:, 0]))
        out[name] = dict(run=r["run"], n=n, mode=r["mode"], dx=h, summary=last,
                         outer_iterations=int(txt.shape[0] - 1),
                         rhs_vs_deposit_rel=ea, rhs_yz_rel=eyz, operator_check_rel=eb,
                         relv_factors=[float(f) for f in fac],
                         relv_final=float(relv[-1]), M_monitor_before=float(txt[0, 16]),
                         M_monitor_after=float(txt[-1, 16]),
                         H_max_after=float(txt[-1, 4]),
                         Wx_centre_code=float(np.mean(W[0][inner])),
                         Wx_centre_ref=float(np.mean(Wr[0][inner])),
                         rel_err_Wx_inner=e_in, rel_err_Wx_faces=fc, rel_err_Wx_face_max=e_face,
                         P_flux=float(P_flux), P_sum=P_sum,
                         P_rel_err=float(P_flux/P_sum - 1.0))
        curves[name] = dict(x=c, Wx=W[0][:, i0, i0], Wr=Wr[0][:, i0, i0],
                            Wy_line=W[0][i0, :, i0], Wr_y=Wr[0][i0, :, i0],
                            relv=relv, h=h)
        print("%-20s %s" % (name, r["run"]))
        for k in ("outer_iterations", "rhs_vs_deposit_rel", "rhs_yz_rel", "operator_check_rel",
                  "relv_final", "M_monitor_before", "M_monitor_after", "H_max_after",
                  "Wx_centre_code", "Wx_centre_ref", "rel_err_Wx_inner", "rel_err_Wx_face_max",
                  "P_flux", "P_sum", "P_rel_err"):
            print("   %-22s %s" % (k, out[name][k]))
        print("   relv factors: " + " ".join("%.3f" % f for f in fac))
    res["analysis"] = out
    idlib.save_json(OUT, res)

    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.15, top=0.9, wspace=0.38)
    col = {32: fs.PAL["blue"], 64: fs.PAL["red"]}
    ax = axs[0]
    for name, cv in sorted(curves.items()):
        if "stencil" not in name:
            continue
        n = out[name]["n"]
        ax.plot(cv["x"], cv["Wx"], ".", color=col[n], ms=3, label="code, %d cells" % n)
    cv = curves["gboost_stencil_n64"]
    ax.plot(cv["x"], cv["Wr"], "-", color="k", lw=0.8, label="continuum")
    ax.set_xlabel(r"$x$ (on the $x$ axis)")
    ax.set_ylabel(r"$W_x$")
    ax.legend(fontsize=7)
    ax = axs[1]
    for name, cv in sorted(curves.items()):
        n = out[name]["n"]
        ls = "-" if "stencil" in name else "--"
        ax.plot(cv["x"], (cv["Wx"] - cv["Wr"])/(cv["h"]/2.0)**2, ls, color=col[n], lw=1.0,
                label="%s, %d" % (out[name]["mode"], n))
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$(W_x - W_x^{\rm cont})/(dx/\sigma)^2$")
    ax.legend(fontsize=7)
    ax = axs[2]
    for name, cv in sorted(curves.items()):
        n = out[name]["n"]
        ls = "-" if "stencil" in name else "--"
        ax.semilogy(np.arange(len(cv["relv"])), cv["relv"], ls, marker=".", color=col[n],
                    label="%s, %d" % (out[name]["mode"], n))
    ax.axhline(1e-10, color="0.5", lw=0.8, ls=":")
    ax.set_xlabel("outer iteration")
    ax.set_ylabel("vector residual / scale")
    ax.legend(fontsize=7)
    fs.save(fig, os.path.join(idlib.FIGS, "vector_gauss"))
    plt.close(fig)
    return 0


def v3(a):
    """Test V3: the smooth ball and its strained copy with the vector equation (mode
    code, 64 cells): the curvature terms of the right side."""
    res = idlib.load_json(OUT)
    tmp = os.path.join(idlib.SCRATCH, "tmp", "idsolve")
    with open(os.path.join(idlib.WT, "problems/idsolve/ball.athinput")) as f:
        txt = f.read()
    key = "id_dump        = true"
    if key not in txt:
        raise RuntimeError("ball.athinput: '%s' not found" % key)
    txt = txt.replace(key, "id_vector      = true\n" + key)
    binp = os.path.join(tmp, "ball_vector.athinput")
    with open(binp, "w") as f:
        f.write(txt)
    out = {}
    for label, (nrp, tab) in (("sphere", run_tests.ic_ball(0.5, 2.0)),
                              ("strained", run_tests.ic_tri(0.5, 0.05, 2.0))):
        rid, st = registered("initial-data solver, test V3: smooth ball (%s) with the vector "
                             "equation, mode code, 64 cells" % label, "idsolve-v3-" + label,
                             [binp, nrp, tab],
                             [a.exe, "-i", "ball_vector.athinput"] + run_tests.mesh_args(64, 32)
                             + ["particles/id_residual=code", "particles/nfilter=0",
                                "particles/particle_file=" + os.path.basename(nrp),
                                "problem/comp0_file=" + os.path.basename(tab)])
        print("V3 %s %s %s" % (label, rid, st), flush=True)
        d = idlib.run_dir(rid)
        t, last = idlib.read_idsolve_txt(os.path.join(d, "ball.idsolve.txt"))
        v = read_idvector_bin(os.path.join(d, "ball.idvector.bin"))
        n = v["n"][0]
        W = [v["Wx"], v["Wy"], v["Wz"]]
        h = 64.0/n
        Pp = [robin_pad(w, -32.0, 32.0, 1) for w in W]
        sl = slice(1, -1)

        def dcen(arr, ax):
            sp_ = [sl, sl, sl]
            sm_ = [sl, sl, sl]
            sp_[ax] = slice(2, None)
            sm_[ax] = slice(0, -2)
            return (arr[tuple(sp_)] - arr[tuple(sm_)])/(2.0*h)
        dW = [[dcen(Pp[b], ax) for b in range(3)] for ax in range(3)]
        div = dW[0][0] + dW[1][1] + dW[2][2]
        lw2 = np.zeros_like(div)
        for i in range(3):
            for j in range(3):
                lij = dW[i][j] + dW[j][i] - (2.0/3.0*div if i == j else 0.0)
                lw2 += lij*lij
        ds = idlib.read_idsolve_bin(os.path.join(d, "ball.idsolve.bin"))
        out[label] = dict(run=rid, status=st, summary=last, outer_iterations=int(t.shape[0] - 1),
                          H_max_after=float(t[-1, 4]), relv_final=float(t[-1, 13]),
                          M_monitor_before=float(t[0, 16]), M_monitor_after=float(t[-1, 16]),
                          LW_max=float(np.sqrt(lw2).max()),
                          Abar_max=float(np.sqrt(ds["A2"]).max()),
                          W_max=float(max(np.abs(w).max() for w in W)))
        out[label]["LW_over_Abar"] = out[label]["LW_max"]/out[label]["Abar_max"]
        for k, val in out[label].items():
            print("   %-18s %s" % (k, val))
    res["V3"] = out
    idlib.save_json(OUT, res)
    return 0


def mstats(d, base):
    """Mean and max of the monitor's |M| before and after a solve with id_vector."""
    v = read_idvector_bin(os.path.join(d, base + ".idvector.bin"))
    m1 = np.sqrt(v["Mx"]**2 + v["My"]**2 + v["Mz"]**2)
    m0 = np.sqrt(v["Mx0"]**2 + v["My0"]**2 + v["Mz0"]**2)
    return dict(M_mean_before=float(m0.mean()), M_mean_after=float(m1.mean()),
                M_max_before=float(m0.max()), M_max_after=float(m1.max()))


def v5(a):
    """Tests V5 (the vector part with the monitor as residual: smooth ball, its strained
    copy, moving Gaussian) and V6 (evolution of the strained ball with both solves)."""
    res = idlib.load_json(OUT)
    tmp = os.path.join(idlib.SCRATCH, "tmp", "idsolve")
    extra = "id_vector      = true\nid_vector_residual = code\n"
    with open(os.path.join(idlib.WT, "problems/idsolve/ball.athinput")) as f:
        txt = f.read()
    key = "id_dump        = true"
    binp = os.path.join(tmp, "ball_vector_code.athinput")
    with open(binp, "w") as f:
        f.write(txt.replace(key, extra + key))
    with open(os.path.join(idlib.WT, "problems/idsolve/gaussian_boost.athinput")) as f:
        txt = f.read()
    key2 = "id_vector      = true     # also solve the momentum constraint for W (Abar = L W)"
    if key not in txt or key2 not in txt:
        raise RuntimeError("input files changed")
    ginp = os.path.join(tmp, "gaussian_boost_code.athinput")
    with open(ginp, "w") as f:
        f.write(txt.replace(key2, key2 + "\nid_vector_residual = code"))
    out = {}
    for label, (nrp, tab) in (("sphere", run_tests.ic_ball(0.5, 2.0)),
                              ("strained", run_tests.ic_tri(0.5, 0.05, 2.0))):
        rid, st = registered("initial-data solver, test V5: smooth ball (%s), vector part "
                             "with the monitor as residual, 64 cells" % label,
                             "idsolve-v5-" + label, [binp, nrp, tab],
                             [a.exe, "-i", os.path.basename(binp)] + run_tests.mesh_args(64, 32)
                             + ["particles/id_residual=code", "particles/nfilter=0",
                                "particles/particle_file=" + os.path.basename(nrp),
                                "problem/comp0_file=" + os.path.basename(tab)])
        d = idlib.run_dir(rid)
        t, last = idlib.read_idsolve_txt(os.path.join(d, "ball.idsolve.txt"))
        out[label] = dict(run=rid, status=st, summary=last, outer_iterations=int(t.shape[0] - 1),
                          H_max_after=float(t[-1, 4]), relv_final=float(t[-1, 13]),
                          **mstats(d, "ball"))
        print("V5 %s %s %s" % (label, rid, st), flush=True)
    nrp = os.path.join(IC, "gauss_h0p25_u0p1.nrp")
    rid, st = registered("initial-data solver, test V5: moving Gaussian, vector part with the "
                         "monitor as residual, 64 cells", "idsolve-v5-gboost-n64",
                         [ginp, nrp], [a.exe, "-i", os.path.basename(ginp)]
                         + run_tests.mesh_args(64, 32) + ["particles/id_residual=code",
                                                          "particles/particle_file="
                                                          + os.path.basename(nrp)])
    d = idlib.run_dir(rid)
    t, last = idlib.read_idsolve_txt(os.path.join(d, "gboost.idsolve.txt"))
    out["gboost_n64"] = dict(run=rid, status=st, summary=last,
                             outer_iterations=int(t.shape[0] - 1), H_max_after=float(t[-1, 4]),
                             relv_final=float(t[-1, 13]), **mstats(d, "gboost"))
    print("V5 gboost %s %s" % (rid, st), flush=True)
    # V6: evolution of the strained ball with both solves (settings of test E)
    nrp, tab = run_tests.ic_tri(0.5, 0.05, 2.0)
    rid, st = registered("initial-data solver, test V6: evolution of the smooth strained "
                         "ball with the scalar and the vector solve (mode code), settings "
                         "of test E", "idsolve-v6-evo", [binp, nrp, tab],
                         [a.exe, "-i", os.path.basename(binp)] + run_tests.mesh_args(64, 32)
                         + ["time/nlim=8", "time/tlim=100.0", "particles/nfilter=0",
                            "particles/source_density=true", "particles/source_extrap=true",
                            "z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333",
                            "particles/id_residual=code",
                            "particles/particle_file=" + os.path.basename(nrp),
                            "problem/comp0_file=" + os.path.basename(tab)])
    c = np.loadtxt(os.path.join(idlib.run_dir(rid), "ball.cstat.hst"), ndmin=2)
    out["evolution"] = dict(run=rid, status=st, time=[float(x) for x in c[:, 0]],
                            H_max=[float(x) for x in c[:, 8]], H_mean=[float(x) for x in c[:, 9]],
                            M_max=[float(x) for x in c[:, 12]],
                            M_mean=[float(x) for x in c[:, 13]])
    print("V6 %s %s" % (rid, st), flush=True)
    res["V5"] = out
    idlib.save_json(OUT, res)
    for k, v in out.items():
        print(k)
        for kk, vv in v.items():
            print("   %-16s %s" % (kk, vv))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=os.path.join(idlib.WT, ".work/build_cpu_vec/src/athena"))
    ap.add_argument("--base", default="/data/haiyangw/nrpic/scratch/core/exe/core_id-solver/"
                                      "athena_cpu")
    ap.add_argument("--analyze", action="store_true", help="analysis of earlier runs only")
    ap.add_argument("--v0-only", default="", help="rerun V0 only for these cases "
                    "(gauss, torus), then analyse")
    ap.add_argument("--v3", action="store_true", help="test V3 only")
    ap.add_argument("--v5", action="store_true", help="tests V5 and V6 only")
    a = ap.parse_args()
    if a.v3:
        return v3(a)
    if a.v5:
        return v5(a)
    if not a.analyze:
        run_all(a)
    return analyze()


if __name__ == "__main__":
    sys.exit(main())
