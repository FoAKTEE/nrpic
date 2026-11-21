#!/usr/bin/env python3
"""Test TS of tracks/core/JOURNAL-clump2.md: the elliptic initial-data solve of the code
(<particles> id_solve) on the moving cluster of the static tests TB, against the radial
second-order correction of psi.

    run_idsolve_static.py [--tb RUN_ID/tb] [--n 64] [--v 0.3] [--box 32 --cells 128]
                          [--kinds rest,curv,corr] [--out DIR]

Three solves with problems/tests/clump_table_idsolve.athinput on the tables and the quiet
lattice of a finished TB run (its directory ic/ and its cases.json): the cluster at rest
(q0), the moving cluster with the curvature of the boost table (curv: trial psi = psi_0),
and the same with the radial correction as the trial (corr). Compared, with psi_t the
trial psi of the TB run's dumps of the same cases (single precision):

  A = s_rest - psi_t(rest)        what the mesh solve changes at rest (the deposit)
  R = psi_t(corr) - psi_t(curv)   the radial correction, V^2 (y0 + y2 P2)
  D = s_curv - s_rest             the motion's part of the solved psi
  s_curv - s_corr                 the same equation from two starts

With --box B --cells N the mesh is [-B, B]^3 with N cells (test TS4: the faces further
out); the trial psi then comes from runs of problems/tests/clump_table_static.athinput on
that mesh, made here. Writes idsolve_static.json and fig_idsolve_static.{pdf,png} into
--out.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "idsolve"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mp_common import read_bin  # noqa: E402
from idlib import read_idsolve_bin, read_idsolve_txt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))
INPUT = os.path.join(WT, "problems", "tests", "clump_table_idsolve.athinput")
STATIC = os.path.join(WT, "problems", "tests", "clump_table_static.athinput")
RCUT = 14.0


def trial_psi(path, n, lo, dx):
    """psi of an adm_psi4 dump on the [i, j, k] grid of the solver's dump"""
    _, _, x, y, z, _, var = read_bin(path)
    out = np.full((n, n, n), np.nan)
    i = np.rint((x - lo) / dx - 0.5).astype(int)
    j = np.rint((y - lo) / dx - 0.5).astype(int)
    k = np.rint((z - lo) / dx - 0.5).astype(int)
    out[i, j, k] = np.asarray(var["adm_psi4"]) ** 0.25
    assert not np.any(np.isnan(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tb", default="core-20261120-222933-0a01a56/tb")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--v", default="0.3")
    ap.add_argument("--box", type=float, default=None, help="half-width of the mesh")
    ap.add_argument("--cells", type=int, default=None, help="cells per direction with --box")
    ap.add_argument("--kinds", default="rest,curv,corr")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    tb = os.path.join(SCRATCH, a.tb)
    mesh = []
    if a.box is not None:
        for c in (1, 2, 3):
            mesh += [f"mesh/nx{c}={a.cells}", f"mesh/x{c}min={-a.box!r}", f"mesh/x{c}max={a.box!r}"]
    with open(os.path.join(tb, "cases.json")) as f:
        tbc = json.load(f)["cases"]
    labels = dict(rest=f"q0_n{a.n}", curv=f"q{a.v}_n{a.n}_curv", corr=f"q{a.v}_n{a.n}_corr")
    env = dict(os.environ, OMP_NUM_THREADS="1")
    res = dict(exe=EXE, input=INPUT, tb=tb, cases={})
    sol, tri = {}, {}
    labels = {k: labels[k] for k in a.kinds.split(",")}
    for kind, lab in labels.items():
        c = tbc[lab]
        args = c["args"] if a.box is None else [x for x in c["args"] if not x.startswith("mesh/")] + mesh
        d = os.path.join(a.out, lab)
        os.makedirs(d, exist_ok=True)
        ic, tabs = c["ic"], c["tables"]
        links = {"particles.nrp": ic + ".nrp", "cluster_c0.tab": tabs + "_c0.tab",
                 "cluster_c0.bst": tabs + "_c0.bst", "cluster_c0_corr.tab": tabs + "_c0_corr.tab"}
        for dst, src in links.items():
            link = os.path.join(d, dst)
            if not os.path.lexists(link):
                os.symlink(os.path.join(tb, "ic", src), link)
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", INPUT, "-d", d, *args], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT, env=env).returncode
        rec = dict(label=lab, args=args, status=st, wall=time.time() - t0)
        res["cases"][kind] = rec
        print(kind, lab, "status", st, f"{rec['wall']:.0f} s", flush=True)
        if st != 0:
            continue
        rows, last = read_idsolve_txt(os.path.join(d, "clump.idsolve.txt"))
        b = read_idsolve_bin(os.path.join(d, "clump.idsolve.bin"))
        sol[kind] = b
        rec.update(summary=last, outer_iterations=int(rows[-1, 0]),
                   rel_residual_last=float(rows[-1, 1]),
                   H_max_first=float(rows[0, 4]), H_rms_first=float(rows[0, 5]),
                   H_max_last=float(rows[-1, 4]), H_rms_last=float(rows[-1, 5]),
                   psi_min=float(b["psi"].min()), psi_max=float(b["psi"].max()))
        n, lo = b["n"][0], b["box"][0]
        dx = (b["box"][1] - lo) / n
        tdir = os.path.join(tb, lab)
        if a.box is not None:       # the trial psi on this mesh: the static input, no solve
            tdir = os.path.join(a.out, lab + "_trial")
            os.makedirs(tdir, exist_ok=True)
            for dst in links:
                if not os.path.lexists(os.path.join(tdir, dst)):
                    os.symlink(os.readlink(os.path.join(d, dst)), os.path.join(tdir, dst))
            with open(os.path.join(tdir, "athena.log"), "w") as log:
                subprocess.run([EXE, "-i", STATIC, "-d", tdir, *args], cwd=tdir, stdout=log,
                               stderr=subprocess.STDOUT, env=env, check=True)
        tri[kind] = trial_psi(os.path.join(tdir, "bin", "clump.adm_psi4.00000.bin"), n, lo, dx)
    if a.box is not None and "curv" in sol and "corr" not in tri:
        # the radial correction on this mesh: one more static run (no solve)
        lab = f"q{a.v}_n{a.n}_corr"
        c = tbc[lab]
        args = [x for x in c["args"] if not x.startswith("mesh/")] + mesh
        tdir = os.path.join(a.out, lab + "_trial")
        os.makedirs(tdir, exist_ok=True)
        for dst in ("particles.nrp", "cluster_c0.tab", "cluster_c0.bst", "cluster_c0_corr.tab"):
            src = os.readlink(os.path.join(a.out, labels["curv"], dst))
            if not os.path.lexists(os.path.join(tdir, dst)):
                os.symlink(src, os.path.join(tdir, dst))
        with open(os.path.join(tdir, "athena.log"), "w") as log:
            subprocess.run([EXE, "-i", STATIC, "-d", tdir, *args], cwd=tdir, stdout=log,
                           stderr=subprocess.STDOUT, env=env, check=True)
        b = sol["curv"]
        n, lo = b["n"][0], b["box"][0]
        tri["corr"] = trial_psi(os.path.join(tdir, "bin", "clump.adm_psi4.00000.bin"), n, lo,
                                (b["box"][1] - lo) / n)
    if "rest" in sol and "curv" in sol and "corr" in tri:
        b = sol["rest"]
        n, lo = b["n"][0], b["box"][0]
        dx = (b["box"][1] - lo) / n
        xc = lo + (np.arange(n) + 0.5) * dx
        X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
        w = np.sqrt(X * X + Y * Y + Z * Z) < RCUT
        A = sol["rest"]["psi"] - tri["rest"]
        R = tri["corr"] - tri["curv"]
        D = sol["curv"]["psi"] - sol["rest"]["psi"]
        both = "corr" in sol
        C = sol["corr"]["psi"] - tri["corr"] if both else np.zeros_like(A)
        same = sol["curv"]["psi"] - sol["corr"]["psi"] if both else np.zeros_like(A)
        rms = lambda f: float(np.sqrt(np.mean(f[w] ** 2)))  # noqa: E731
        mx = lambda f: float(np.max(np.abs(f[w])))  # noqa: E731
        h = n // 2
        ctr = lambda f: float(np.mean(f[h - 1:h + 1, h - 1:h + 1, h - 1:h + 1]))  # noqa: E731
        res["compare"] = dict(
            rcut=RCUT, cells_inside=int(np.count_nonzero(w)),
            A_rms=rms(A), A_max=mx(A), A_centre=ctr(A),
            R_rms=rms(R), R_max=mx(R), R_centre=ctr(R),
            D_rms=rms(D), D_max=mx(D), D_centre=ctr(D),
            C_rms=rms(C), C_max=mx(C), C_centre=ctr(C),
            D_minus_R_rms=rms(D - R), D_minus_R_max=mx(D - R),
            ratio_rms=rms(D - R) / rms(R), ratio_max=mx(D - R) / mx(R),
            centre_ratio=ctr(D) / ctr(R),
            two_starts_max_whole_mesh=float(np.max(np.abs(same))) if both else None,
            D_minus_R_rms_whole_mesh=float(np.sqrt(np.mean((D - R) ** 2))))
        # profiles along the x axis: the four lines of cells next to y = z = 0
        line = lambda f: f[:, h - 1:h + 1, h - 1:h + 1].mean(axis=(1, 2))  # noqa: E731
        res["compare"].update(D_minus_R_axis_first_cell=float(line(D - R)[0]),
                              D_minus_R_axis_last_cell=float(line(D - R)[-1]),
                              D_minus_R_axis_centre=float(line(D - R)[h]),
                              box=float(-lo), cells=int(n))
        print(json.dumps(res["compare"], indent=1))
        fs.use_style()
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
        fig.subplots_adjust(left=0.10, right=0.985, bottom=0.16, top=0.95, wspace=0.30)
        cols = fs.series_colors(4)
        ax[0].plot(xc, 1e3 * line(R), color=cols[0], label=r"radial correction $R$")
        ax[0].plot(xc, 1e3 * line(D), color=cols[1], ls="--", label=r"mesh solve, motion's part $D$")
        ax[0].plot(xc, 1e3 * line(A), color=cols[2], label=r"mesh solve at rest $A$")
        ax[0].set_xlabel(r"$x/M$ on the axis of motion")
        ax[0].set_ylabel(r"$10^3\,\delta\psi$")
        ax[0].legend(loc="center right", fontsize=7)
        ax[1].plot(xc, 1e3 * line(D - R), color=cols[1], label=r"$D - R$")
        if both:
            ax[1].plot(xc, 1e3 * line(C), color=cols[3], ls="--", label=r"left for the solve after $R$")
        ax[1].plot(xc, 1e3 * line(A), color=cols[2], label=r"$A$")
        ax[1].set_xlabel(r"$x/M$ on the axis of motion")
        ax[1].set_ylabel(r"$10^3\,\delta\psi$")
        ax[1].legend(loc="upper right", fontsize=7)
        fs.save(fig, os.path.join(a.out, "fig_idsolve_static"))
    with open(os.path.join(a.out, "idsolve_static.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0 if "compare" in res else 1


if __name__ == "__main__":
    sys.exit(main())
