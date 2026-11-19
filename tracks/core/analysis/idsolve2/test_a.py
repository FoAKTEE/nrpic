#!/usr/bin/env python3
"""Tests A of the initial-data solver, second pass (journal entry 1): R1 (the first pass
recovered with id_far = robin), W1 (moving Gaussian: far field against the plain fill),
W2 (off-centre moving Gaussian), C1 (coupled solve with fast particles).

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_a.py --exe <athena>
                            [--tests r1,w1,w2,c1] [--nmax 128] [--jobs 13]
    test_a.py --analyze <run directory>        analysis and figure of an earlier run
"""
import argparse
import filecmp
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
import run_vector as rv           # first pass: semi-analytic continuum W
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GAUSS = os.path.join(lib2.WT, "problems/idsolve/gaussian.athinput")
BOOST = os.path.join(lib2.WT, "problems/idsolve/gaussian_boost.athinput")
MASS, SIGMA, HALF, RCUT = 1.0, 2.0, 16.0, 14.0
SHIFT = (3.0, 2.0, 0.0)


def mb_of(n):
    return 16 if n == 32 else 32


def ic_steps(n, u, shift=None):
    """argv lists that write the particle file of a case into its directory; returns
    (steps, file name)."""
    h = HALF/n
    stem = ("gauss_h%g" % h).replace(".", "p")
    steps = [lib2.py(lib2.MAKE_IC, "gaussian", "--h", str(h), "--out", ".")]
    name = stem + ".nrp"
    if u is not None:
        steps.append(lib2.py(lib2.MAKE_IC, "boost", "--in", name, "--u", str(u), "--out", ".",
                             "--prefix", "boost"))
        name = "boost.nrp"
    if shift is not None:
        steps.append(lib2.py(lib2.MAKE_IC, "shift", "--in", name, "--d", *[str(v) for v in shift],
                             "--out", ".", "--prefix", "shifted"))
        name = "shifted.nrp"
    return steps, name


def build_cases(root, exe, tests, nmax):
    cases = []

    def add(name, base, n, u, sets, shift=None, use_exe=None):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        steps, nrp = ic_steps(n, u, shift)
        s = dict(lib2.mesh(n, mb_of(n)))
        s["particles/particle_file"] = nrp
        s.update(sets)
        lib2.make_input(base, os.path.join(d, "in.athinput"), s)
        steps.append([use_exe or exe, "-i", "in.athinput"])
        cases.append(dict(name=name, dir=d, steps=steps))

    if "r1" in tests:
        add("r1_first", GAUSS, 32, None, {"particles/id_residual": "code"},
            use_exe=lib2.FIRST_PASS)
        add("r1_new", GAUSS, 32, None, {"particles/id_residual": "code",
                                         "particles/id_far": "robin"})
        add("r1_boost_first", BOOST, 32, 0.1, {}, use_exe=lib2.FIRST_PASS)
        add("r1_boost_new", BOOST, 32, 0.1, {"particles/id_far": "robin"})
    if "w1" in tests:
        for n in (32, 64, 128):
            if n > nmax:
                continue
            add("w1_far_n%d" % n, BOOST, n, 0.1, {})
            add("w1_robin_n%d" % n, BOOST, n, 0.1, {"particles/id_far": "robin"})
    if "w2" in tests:
        off = {"problem/comp0_x1": SHIFT[0], "problem/comp0_x2": SHIFT[1]}
        add("w2_l4", BOOST, 64, 0.1, dict(off), shift=SHIFT)
        add("w2_l0", BOOST, 64, 0.1, dict(off, **{"particles/id_far_lmax": 0}), shift=SHIFT)
        add("w2_robin", BOOST, 64, 0.1, dict(off, **{"particles/id_far": "robin"}), shift=SHIFT)
    if "c1" in tests:
        for n in (32, 64):
            add("c1_n%d" % n, BOOST, n, 1.0, {"particles/id_vector_residual": "code"})
    return cases


# ------------------------------------------------------------------------------ analysis
def surface_momentum(W, lo, hi, R):
    """(1/8 pi) times the flux of (L W)_xj through the cube of half-width near R whose faces
    pass through cell centres (trapezoid rule); returns (P_x, half-width used)."""
    n = W[0].shape[0]
    h = (hi - lo)/n
    c = lo + (np.arange(n) + 0.5)*h

    def d(a, ax):
        return (np.roll(a, -1, ax) - np.roll(a, 1, ax))/(2.0*h)
    div = d(W[0], 0) + d(W[1], 1) + d(W[2], 2)
    lxx = 2.0*d(W[0], 0) - (2.0/3.0)*div
    lxy = d(W[0], 1) + d(W[1], 0)
    lxz = d(W[0], 2) + d(W[2], 0)
    ihi = int(np.argmin(np.abs(c - R)))
    ilo = n - 1 - ihi
    w = np.ones(ihi - ilo + 1)
    w[0] = w[-1] = 0.5
    ww = w[:, None]*w[None, :]
    sl = slice(ilo, ihi + 1)
    p = np.sum(ww*(lxx[ihi, sl, sl] - lxx[ilo, sl, sl]))
    p += np.sum(ww*(lxy[sl, ihi, sl] - lxy[sl, ilo, sl]))
    p += np.sum(ww*(lxz[sl, sl, ihi] - lxz[sl, sl, ilo]))
    return p*h*h/(8.0*np.pi), c[ihi]


def w_errors(d, u, centre=(0.0, 0.0, 0.0)):
    """Errors of W of a dump against the continuum W of the Gaussian moving with u_x = u
    centred at centre."""
    v = lib2.read_idvector(os.path.join(d, "gboost.idvector.bin"))
    n = v["n"][0]
    lo, hi = v["box"][0], v["box"][1]
    c = idlib.centres(n, lo, hi)
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    ref = rv.vector_reference(rv.gauss_q(u, MASS, SIGMA, RCUT), RCUT, X - centre[0],
                              Y - centre[1], Z - centre[2])
    W = v["W"]
    err = np.sqrt(sum((W[i] - ref[i])**2 for i in range(3)))
    mag = np.sqrt(sum(ref[i]**2 for i in range(3)))
    rel = err/mag
    layer = np.zeros((n, n, n), dtype=bool)
    layer[0], layer[-1] = True, True
    layer[:, 0], layer[:, -1] = True, True
    layer[:, :, 0], layer[:, :, -1] = True, True
    h2 = n//2
    mid = slice(h2 - 1, h2 + 1)
    relx = (W[0] - ref[0])/ref[0]
    face = dict(x=float(np.mean([relx[0, mid, mid], relx[-1, mid, mid]])),
                y=float(np.mean([relx[mid, 0, mid], relx[mid, -1, mid]])),
                z=float(np.mean([relx[mid, mid, 0], relx[mid, mid, -1]])))
    out = dict(n=n, dx=(hi - lo)/n, face_centre=face,
               layer_max=float(rel[layer].max()), layer_mean=float(rel[layer].mean()),
               centre=float(np.mean(relx[mid, mid, mid])),
               line_x=[c.tolist(), np.mean(relx[:, mid, mid], axis=(1, 2)).tolist()],
               line_y=[c.tolist(), np.mean(relx[mid, :, mid], axis=(0, 2)).tolist()])
    mom = []
    for R in (8.0, 10.0, 12.0, 14.0):
        p, rr = surface_momentum(W, lo, hi, R)
        mom.append([rr, p])
    out["surface_momentum"] = mom
    return out


def record(d, base="gboost"):
    rows, tail = lib2.summary(os.path.join(d, base + ".idsolve.txt"))
    out = dict(outer=int(rows[-1][0]), summary=tail, rel_last=float(rows[-1][1]),
               hmax_first=float(rows[0][4]), hmax_last=float(rows[-1][4]),
               psi_max=float(rows[-1][9]), cg=int(rows[:, 10].sum()), vcycles=int(rows[:, 11].sum()))
    if rows.shape[1] > 13:
        out.update(relv=rows[:, 13].tolist(), mmax_first=float(rows[0][16]),
                   mmax_last=float(rows[-1][16]), vcycles_vec=int(rows[:, 18].sum()))
    fl = lib2.far_line(os.path.join(d, base + ".idsolve.txt"))
    if fl:
        out["far"] = fl
    return out


def analyze(root, status):
    res = dict(run=lib2.run_id() if status else os.path.basename(root.rstrip("/")),
               cases=status or {})
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, "*"))
                   if os.path.isdir(p))
    # R1
    r1 = {}
    for a, b in (("r1_first", "r1_new"), ("r1_boost_first", "r1_boost_new")):
        if a in names and b in names:
            da, db = os.path.join(root, a), os.path.join(root, b)
            files = sorted(f for f in os.listdir(da) if f.startswith(("gauss.", "gboost."))
                           and not f.endswith(".nrp"))
            diff = [f for f in files if not os.path.exists(os.path.join(db, f)) or
                    not filecmp.cmp(os.path.join(da, f), os.path.join(db, f), shallow=False)]
            r1[a + " vs " + b] = dict(files=files, differ=diff)
            if a == "r1_boost_first":
                va = lib2.read_idvector(os.path.join(da, "gboost.idvector.bin"))
                vb = lib2.read_idvector(os.path.join(db, "gboost.idvector.bin"))
                pa = idlib.read_idsolve_bin(os.path.join(da, "gboost.idsolve.bin"))["psi"]
                pb = idlib.read_idsolve_bin(os.path.join(db, "gboost.idsolve.bin"))["psi"]
                r1[a + " vs " + b].update(
                    dpsi=float(np.abs(pa - pb).max()),
                    dW=float(max(np.abs(va["W"][i] - vb["W"][i]).max() for i in range(3))
                             / np.abs(va["W"][0]).max()),
                    outer=[record(da)["outer"], record(db)["outer"]])
    res["R1"] = r1
    # W1
    w1 = {}
    for nme in names:
        if nme.startswith("w1_"):
            d = os.path.join(root, nme)
            if not os.path.exists(os.path.join(d, "gboost.idvector.bin")):
                continue
            e = w_errors(d, 0.1)
            e.update(record(d))
            meta = idlib.load_json(os.path.join(d, "boost.json"))
            e["sum_mu"] = meta["P_x"]
            w1[nme] = e
    res["W1"] = w1
    # W2
    w2 = {}
    for nme in names:
        if nme.startswith("w2_") and os.path.exists(os.path.join(root, nme,
                                                                 "gboost.idvector.bin")):
            d = os.path.join(root, nme)
            e = w_errors(d, 0.1, centre=SHIFT)
            e.update(record(d))
            e["sum_mu"] = idlib.load_json(os.path.join(d, "boost.json"))["P_x"]
            w2[nme] = e
    res["W2"] = w2
    # C1
    c1 = {}
    for nme in names:
        if nme.startswith("c1_") and os.path.exists(os.path.join(root, nme,
                                                                 "gboost.idsolve.bin")):
            d = os.path.join(root, nme)
            e = record(d)
            b = idlib.read_idsolve_bin(os.path.join(d, "gboost.idsolve.bin"))
            n = b["n"][0]
            mid = slice(n//2 - 1, n//2 + 1)
            e.update(n=n, psi_centre=float(b["psi"][mid, mid, mid].mean()),
                     hmax_inner=float(np.abs(idlib.interior(b["H"], n//8)).max()),
                     h0max_inner=float(np.abs(idlib.interior(b["H0"], n//8)).max()))
            v = lib2.read_idvector(os.path.join(d, "gboost.idvector.bin"))
            mm = np.sqrt(sum(v["M"][i]**2 for i in range(3)))
            m0 = np.sqrt(sum(v["M0"][i]**2 for i in range(3)))
            e.update(mmax_inner=float(idlib.interior(mm, n//8).max()),
                     m0max_inner=float(idlib.interior(m0, n//8).max()),
                     sum_mu=idlib.load_json(os.path.join(d, "boost.json"))["P_x"])
            c1[nme] = e
    res["C1"] = c1
    out = os.path.join(root, "test_a_numbers.json")
    lib2.save_json(out, res)
    fig = figure(res, root)
    lib2.publish([out] + fig)
    return res


def figure(res, root):
    w1 = res["W1"]
    if not w1:
        return []
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    col = {"far": fs.PAL["red"], "robin": fs.PAL["blue"]}
    lab = {"far": "far field", "robin": "plain $1/r$ fill"}
    ax = axs[0]
    for kind in ("robin", "far"):
        e = w1.get("w1_%s_n64" % kind)
        if e:
            ax.plot(e["line_x"][0], np.abs(e["line_x"][1]), color=col[kind], label=lab[kind]
                    + ", along $x$")
            ax.plot(e["line_y"][0], np.abs(e["line_y"][1]), color=col[kind], ls="--",
                    label=lab[kind] + ", along $y$")
    ax.set_yscale("log")
    ax.set_xlabel("coordinate")
    ax.set_ylabel(r"$|W_x/W_x^{\rm cont}-1|$, $64^3$ cells")
    ax.legend(fontsize=6)
    ax = axs[1]
    for kind in ("robin", "far"):
        ns = sorted(e["n"] for k, e in w1.items() if k.startswith("w1_" + kind))
        if not ns:
            continue
        dx = [w1["w1_%s_n%d" % (kind, n)]["dx"] for n in ns]
        fx = [abs(w1["w1_%s_n%d" % (kind, n)]["face_centre"]["x"]) for n in ns]
        fy = [abs(w1["w1_%s_n%d" % (kind, n)]["face_centre"]["y"]) for n in ns]
        lm = [w1["w1_%s_n%d" % (kind, n)]["layer_max"] for n in ns]
        ax.loglog(dx, fx, "o-", color=col[kind], label=lab[kind] + ", $x$ face centre")
        ax.loglog(dx, fy, "s--", color=col[kind], label="$y$ face centre")
        ax.loglog(dx, lm, "^:", color=col[kind], label="largest, outer layer")
    xs = np.array([0.25, 1.0])
    ax.loglog(xs, 2.0e-3*xs**2, **fs.GUIDE)
    ax.set_xlabel(r"cell size $\Delta x$")
    ax.set_ylabel("relative error of $W$ at the faces")
    ax.legend(fontsize=5)
    ax = axs[2]
    cn = {32: fs.PAL["yellow"], 64: fs.PAL["red"], 128: fs.PAL["blue"]}
    for kind, mk in (("far", "o-"), ("robin", "x:")):
        for n in (32, 64, 128):
            e = w1.get("w1_%s_n%d" % (kind, n))
            if e:
                sm = np.array(e["surface_momentum"])
                ax.semilogy(sm[:, 0], np.abs(sm[:, 1]/e["sum_mu"] - 1.0), mk, color=cn[n],
                            label="%s, $%d^3$" % (lab[kind], n))
    ax.set_xlabel("half-width of the surface")
    ax.set_ylabel(r"$|P_{\rm surface}/\sum m u_x-1|$")
    ax.legend(fontsize=5)
    fig.tight_layout()
    path = os.path.join(root, "test_a_far")
    fs.save(fig, path)
    plt.close(fig)
    return [path + ".png", path + ".pdf"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=lib2.EXE)
    ap.add_argument("--tests", default="r1,w1,w2,c1")
    ap.add_argument("--nmax", type=int, default=128)
    ap.add_argument("--jobs", type=int, default=13)
    ap.add_argument("--analyze", default="")
    a = ap.parse_args()
    if a.analyze:
        analyze(a.analyze, None)
        return 0
    root = lib2.run_root()
    cases = build_cases(root, os.path.abspath(a.exe), a.tests.split(","), a.nmax)
    status = lib2.run_cases(cases, a.jobs)
    res = analyze(root, status)
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    print("failed cases:", bad)
    print("R1:", {k: v["differ"] for k, v in res["R1"].items()})
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
