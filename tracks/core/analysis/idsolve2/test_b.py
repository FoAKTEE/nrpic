#!/usr/bin/env python3
"""Test B of the initial-data solver, second pass (journal entry 2): the expanding ball
with a triaxial Zel'dovich displacement. Constraint residuals before and after the solve
against resolution, and a short evolution, with norms over regions.

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_b.py --exe <athena>
                            [--n 32,64] [--jobs N]
    test_b.py --prepare DIR --n 128     inputs, particle files and the list of a card job
    test_b.py --analyze DIR [DIR ...]   analysis and figures of earlier runs (a case is
                                        a directory <label>_n<N> with the outputs)
"""
import argparse
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BALL = os.path.join(lib2.WT, "problems/idsolve/ball.athinput")
RB, EDGE, STRAIN, HALF = 10.0, 2.0, 0.05, 32.0
HUBBLE = float(np.sqrt(2.0/RB**3))
LABELS = ("sph", "zoff", "zsol", "zsca")
REGIONS = ("interior", "shell", "exterior", "faces")


def case_sets(label, n):
    s = dict(lib2.mesh(n, 32))
    s.update({"time/nlim": 100000, "time/tlim": 2.0, "particles/nfilter": 0,
              "particles/source_density": "true", "particles/source_extrap": "true",
              "z4c/lapse_oplog": 0.0, "z4c/lapse_harmonic": 0.3333333333333333,
              "particles/field_time1": 1.0, "particles/field_time2": 2.0,
              "particles/id_residual": "code", "problem/comp0_file": "ball.tab",
              "particles/particle_file": "ball.nrp" if label == "sph" else "zel.nrp"})
    if label == "zoff":
        s["particles/id_solve"] = "false"
    if label in ("sph", "zsol"):
        s["particles/id_vector"] = "true"
        s["particles/id_vector_residual"] = "code"
    return s


def ic_steps(label, n):
    h = HALF/n
    steps = [lib2.py(lib2.MAKE_BALL, "--Rb", str(RB), "--edge", str(EDGE), "--h", str(h),
                     "--out", ".", "--prefix", "ball")]
    if label != "sph":
        steps.append(lib2.py(lib2.MAKE_IC, "zeldovich", "--in", "ball.nrp", "--e", str(STRAIN),
                             "--hubble", repr(HUBBLE), "--out", ".", "--prefix", "zel"))
    return steps


def build_cases(root, exe, ns, run_ic_only=False):
    cases = []
    for n in ns:
        for label in LABELS:
            name = "%s_n%d" % (label, n)
            d = os.path.join(root, name)
            os.makedirs(d, exist_ok=True)
            lib2.make_input(BALL, os.path.join(d, "in.athinput"), case_sets(label, n))
            steps = ic_steps(label, n)
            if not run_ic_only:
                steps.append([exe, "-i", "in.athinput"])
            cases.append(dict(name=name, dir=d, steps=steps))
    return cases


# ------------------------------------------------------------------------------ analysis
def region_stats(path, nb_face):
    """Means and maxima of |H| and |M| over the regions of a field dump of the ball."""
    d = idlib.read_field(path)
    n = d["n"]
    x = idlib.centres(n[0], -HALF, HALF)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt(X*X + Y*Y + Z*Z)
    face = np.zeros(n, dtype=bool)
    face[:nb_face, :, :] = face[-nb_face:, :, :] = True
    face[:, :nb_face, :] = face[:, -nb_face:, :] = True
    face[:, :, :nb_face] = face[:, :, -nb_face:] = True
    masks = dict(interior=(r < 7.0) & ~face, shell=(r >= 7.0) & (r < 13.5) & ~face,
                 exterior=(r >= 13.5) & ~face, faces=face)
    h = np.abs(d["H"])
    m = np.sqrt(d["Mx"]**2 + d["My"]**2 + d["Mz"]**2)
    out = dict(time=float(d["time"]), H_mean_all=float(h.mean()), M_mean_all=float(m.mean()))
    for k in REGIONS:
        mk = masks[k]
        out[k] = dict(frac=float(mk.mean()), H_mean=float(h[mk].mean()),
                      H_max=float(h[mk].max()), M_mean=float(m[mk].mean()),
                      M_max=float(m[mk].max()),
                      H_share=float(h[mk].sum()/h.sum()) if h.sum() > 0 else 0.0)
    return out, d


def analyze(roots, status):
    res = dict(runs=[os.path.basename(r.rstrip("/")) for r in roots], cases={},
               status=status or {})
    slices = {}
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, "*_n*"))):
            name = os.path.basename(d)
            label, n = name.split("_n")
            n = int(n)
            f0 = os.path.join(d, "ball.field.00000.bin")
            if label not in LABELS or not os.path.exists(f0):
                continue
            e = dict(n=n, dx=2.0*HALF/n, label=label, run=os.path.basename(root.rstrip("/")),
                     regions=[])
            for i in range(3):
                fp = os.path.join(d, "ball.field.%05d.bin" % i)
                if os.path.exists(fp):
                    st, fd = region_stats(fp, max(1, int(round(4.0/e["dx"]))))
                    e["regions"].append(st)
                    if i == 2 or (i == 0 and n == 64):
                        k2 = n//2
                        slices[(name, i)] = np.abs(fd["H"][:, :, k2])
            rec = os.path.join(d, "ball.idsolve.txt")
            if os.path.exists(rec):
                rows, tail = lib2.summary(rec)
                e.update(outer=int(rows[-1][0]), summary=tail, far=lib2.far_line(rec),
                         cg=int(rows[:, 10].sum()), vcycles=int(rows[:, 11].sum()))
                if rows.shape[1] > 13:
                    e.update(relv_first=float(rows[0][13]), relv_last=float(rows[-1][13]),
                             vcycles_vec=int(rows[:, 18].sum()))
            cs = os.path.join(d, "ball.cstat.hst")
            if os.path.exists(cs):
                c = np.atleast_2d(np.loadtxt(cs))
                e.update(steps=int(c.shape[0] - 1), finite=bool(np.all(np.isfinite(c))),
                         t_end=float(c[-1, 0]))
            res["cases"][name] = e
    out_dir = roots[0]
    out = os.path.join(out_dir, "test_b_numbers.json")
    lib2.save_json(out, res)
    figs = figure(res, slices, out_dir)
    lib2.publish([out] + figs)
    return res


def figure(res, slices, out_dir):
    cases = res["cases"]
    if not cases:
        return []
    fs.use_style()
    col = dict(sph=fs.PAL["blue"], zoff=fs.PAL["yellow"], zsol=fs.PAL["red"],
               zsca=fs.PAL["green"])
    lab = dict(sph="sphere, solved", zoff="Zel'dovich, not solved",
               zsol="Zel'dovich, solved", zsca="Zel'dovich, scalar part only")
    ns = sorted(set(e["n"] for e in cases.values()))
    # figure 1: residuals at t = 0 against resolution (H and M, interior and shell)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    for ax, key, ylab in ((axs[0], "H_mean", r"mean $|H|$ at $t=0$"),
                          (axs[1], "M_mean", r"mean $|M|$ at $t=0$")):
        for label in LABELS:
            for reg, ls, mk in (("interior", "-", "o"), ("shell", "--", "s")):
                xs = [cases["%s_n%d" % (label, n)]["dx"] for n in ns
                      if "%s_n%d" % (label, n) in cases]
                ys = [cases["%s_n%d" % (label, n)]["regions"][0][reg][key] for n in ns
                      if "%s_n%d" % (label, n) in cases]
                if xs:
                    ax.loglog(xs, np.maximum(ys, 1e-16), mk + ls, color=col[label],
                              label="%s, %s" % (lab[label], reg) if reg == "interior"
                              else None)
        ax.set_xlabel(r"cell size $\Delta x$")
        ax.set_ylabel(ylab)
    axs[0].legend(fontsize=6)
    fig.tight_layout()
    p1 = os.path.join(out_dir, "test_b_static")
    fs.save(fig, p1)
    plt.close(fig)
    # figure 2: evolution, mean |H| per region against time, one row per resolution
    fig, axs = plt.subplots(len(ns), 4, figsize=(fs.FULL_WIDTH, 1.9*len(ns) + 0.5),
                            squeeze=False, sharex=True)
    for r, n in enumerate(ns):
        for c, reg in enumerate(REGIONS):
            ax = axs[r][c]
            for label in LABELS:
                e = cases.get("%s_n%d" % (label, n))
                if e and e["regions"]:
                    t = [s["time"] for s in e["regions"]]
                    y = [max(s[reg]["H_mean"], 1e-14) for s in e["regions"]]
                    ax.semilogy(t, y, "o-", color=col[label], label=lab[label])
            if r == 0:
                ax.set_title(reg, fontsize=8)
            if c == 0:
                ax.set_ylabel(r"mean $|H|$, $%d^3$" % n)
            if r == len(ns) - 1:
                ax.set_xlabel("$t$")
    axs[0][0].legend(fontsize=5)
    fig.tight_layout()
    p2 = os.path.join(out_dir, "test_b_evolution")
    fs.save(fig, p2)
    plt.close(fig)
    out = [p1 + ".png", p1 + ".pdf", p2 + ".png", p2 + ".pdf"]
    # figure 3: slices of |H| at t = 2 in the plane z = 0, finest resolution present
    nf = ns[-1]
    have = [lb for lb in LABELS if ("%s_n%d" % (lb, nf), 2) in slices]
    if have:
        fig, axs = plt.subplots(1, len(have), figsize=(fs.FULL_WIDTH, 2.3), squeeze=False)
        for ax, lb in zip(axs[0], have):
            a = slices[("%s_n%d" % (lb, nf), 2)]
            im = ax.imshow(np.log10(np.maximum(a.T, 1e-12)), origin="lower",
                           extent=(-HALF, HALF, -HALF, HALF), vmin=-8, vmax=-2.5,
                           cmap="magma")
            ax.set_title(lab[lb], fontsize=7)
            ax.set_xticks([-24, 0, 24])
            ax.set_yticks([-24, 0, 24] if lb == have[0] else [])
        fig.colorbar(im, ax=list(axs[0]), fraction=0.02, pad=0.01,
                     label=r"$\log_{10}|H|$ at $t=2$, $%d^3$" % nf)
        p3 = os.path.join(out_dir, "test_b_slices")
        fs.save(fig, p3)
        plt.close(fig)
        out += [p3 + ".png", p3 + ".pdf"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=lib2.EXE)
    ap.add_argument("--n", default="32,64")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--prepare", default="")
    ap.add_argument("--analyze", nargs="*", default=[])
    a = ap.parse_args()
    ns = [int(v) for v in a.n.split(",")]
    if a.analyze:
        analyze(a.analyze, None)
        return 0
    if a.prepare:
        cases = build_cases(a.prepare, "", ns, run_ic_only=True)
        lib2.run_cases(cases, a.jobs)
        with open(os.path.join(a.prepare, "batch.list"), "w") as f:
            for c in cases:
                f.write("%s %s particles/particle_file=%s problem/comp0_file=%s\n" % (
                    c["name"], os.path.join(c["dir"], "in.athinput"),
                    os.path.join(c["dir"], "ball.nrp" if c["name"].startswith("sph")
                                 else "zel.nrp"), os.path.join(c["dir"], "ball.tab")))
        return 0
    root = lib2.run_root()
    cases = build_cases(root, os.path.abspath(a.exe), ns)
    status = lib2.run_cases(cases, a.jobs)
    analyze([root], status)
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    print("failed cases:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
