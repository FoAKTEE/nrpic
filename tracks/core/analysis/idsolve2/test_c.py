#!/usr/bin/env python3
"""Tests C of the initial-data solver, second pass (journal entry 3): refined meshes and
the torus with moving matter.

  G  Gaussian at rest (exact psi known) on uniform meshes and with one and two static
     levels, isolated (Robin faces, multigrid octets)
  T  plane wave on the torus (K = -3H: a slice of constant mean curvature) on a uniform
     mesh and with a refined cube and a nested lattice; with the momenta of the growing
     mode and the vector part; large amplitudes on the uniform mesh
  Z  the Zel'dovich ball of test B with a refined centre, with a short evolution

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_c.py --exe <athena>
                            [--tests g,t,z] [--jobs N]
    test_c.py --analyze DIR
The monitor of the run itself is read from its own output of the constraint variables
(<output> file_type = bin, variable = con), per MeshBlock."""
import argparse
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
import make_ic
from nrpic import figstyle as fs  # noqa: E402

sys.path.insert(0, os.path.join(lib2.WT, "athenak", "vis", "python"))
import bin_convert  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GAUSS = os.path.join(lib2.WT, "problems/idsolve/gaussian.athinput")
TORUS = os.path.join(lib2.WT, "problems/idsolve/torus.athinput")
BALL = os.path.join(lib2.WT, "problems/idsolve/ball.athinput")
HUBBLE_BALL = float(np.sqrt(2.0/1000.0))


def region(k, level, lo, hi):
    s = {"refined_region%d/level" % k: level}
    for d in "123":
        s["refined_region%d/x%smin" % (k, d)] = lo
        s["refined_region%d/x%smax" % (k, d)] = hi
    return s


def con_output(dt):
    return {"output9/file_type": "bin", "output9/variable": "con", "output9/dt": dt}


def smr():
    return {"mesh_refinement/refinement": "static", "mesh_refinement/max_nmb_per_rank": 1024}


def build_cases(root, exe, tests):
    cases = []

    def add(name, base, sets, ic):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        lib2.make_input(base, os.path.join(d, "in.athinput"), sets)
        cases.append(dict(name=name, dir=d, steps=ic + [[exe, "-i", "in.athinput"]]))

    if "g" in tests:
        ic = [lib2.py(lib2.MAKE_IC, "gaussian", "--h", "0.25", "--out", ".", "--prefix", "g")]
        com = {"particles/particle_file": "g.nrp", "particles/id_residual": "code"}
        com.update(con_output(1.0e30))
        add("g_uni32", GAUSS, dict(lib2.mesh(32, 16), **com), ic)
        add("g_uni64", GAUSS, dict(lib2.mesh(64, 32), **com), ic)
        s1 = dict(lib2.mesh(32, 8), **com)
        s1.update(smr())
        s1.update(region(1, 1, -4.0, 4.0))
        add("g_smr1", GAUSS, s1, ic)
        add("g_smr1_st", GAUSS, dict(s1, **{"particles/id_residual": "stencil"}), ic)
        s2 = dict(s1)
        s2.update(region(2, 2, -2.0, 2.0))
        add("g_smr2", GAUSS, s2, ic)
    if "t" in tests:
        def wave(amp, nest=False, vel=False):
            a = lib2.py(lib2.MAKE_IC, "wave", "--n", "32", "--ppc", "2", "--amp", str(amp),
                        "--out", ".", "--prefix", "w")
            if nest:
                a += ["--nest", "0.5", "1.5"]
            if vel:
                a += ["--velocity"]
            return [a]
        com = {"particles/particle_file": "w.nrp", "particles/id_residual": "code"}
        com.update(con_output(1.0e30))
        vec = {"particles/id_vector": "true", "particles/id_vector_residual": "code"}
        ts = dict(lib2.mesh(32, 8), **com)
        ts.update(smr())
        ts.update(region(1, 1, 0.5, 1.5))
        add("t_uni", TORUS, dict(lib2.mesh(32, 16), **com), wave(0.1))
        add("t_smr", TORUS, ts, wave(0.1, nest=True))
        add("t_smr_off", TORUS, dict(ts, **{"particles/id_solve": "false"}), wave(0.1, nest=True))
        add("t_smr_mov", TORUS, dict(ts, **vec), wave(0.1, nest=True, vel=True))
        for amp, tag in ((0.1, "a1"), (0.5, "a5"), (0.9, "a9")):
            add("t_uni_mov_" + tag, TORUS, dict(lib2.mesh(32, 16), **dict(com, **vec)),
                wave(amp, vel=True))
    if "z" in tests:
        ic = [lib2.py(lib2.MAKE_BALL, "--Rb", "10", "--edge", "2", "--h", "0.5", "--out", ".",
                      "--prefix", "ball"),
              lib2.py(lib2.MAKE_IC, "zeldovich", "--in", "ball.nrp", "--e", "0.05", "--hubble",
                      repr(HUBBLE_BALL), "--out", ".", "--prefix", "zel")]
        zs = dict(lib2.mesh(32, 8))
        zs.update(smr())
        zs.update(region(1, 1, -16.0, 16.0))
        zs.update(con_output(1.0))
        zs.update({"time/nlim": 100000, "time/tlim": 2.0, "particles/nfilter": 0,
                   "particles/source_density": "true", "particles/source_extrap": "true",
                   "z4c/lapse_oplog": 0.0, "z4c/lapse_harmonic": 0.3333333333333333,
                   "particles/id_residual": "code", "problem/comp0_file": "ball.tab",
                   "particles/particle_file": "zel.nrp"})
        add("z_smr_off", BALL, dict(zs, **{"particles/id_solve": "false"}), ic)
        add("z_smr_sol", BALL, dict(zs, **{"particles/id_vector": "true",
                                          "particles/id_vector_residual": "code"}), ic)
    return cases


# ------------------------------------------------------------------------------ analysis
def read_con(path):
    """A bin output of the constraint variables -> dict with level[m], box[m] (6), dx[m] and
    H, Mx, My, Mz as arrays [m, i, j, k], and the time."""
    f = bin_convert.read_binary(path)
    nmb = f["n_mbs"]
    # the binary output writes x1min, x1max, x2min, x2max, x3min, x3max per MeshBlock
    # (athenak/src/outputs/binary.cpp 139, 198-201; the docstring of bin_convert.py,
    # "x1i, x2i, x3i, dx1, dx2, dx3", does not describe what is written)
    box = np.array(f["mb_geometry"], dtype=float)
    n1, n2, n3 = f["nx1_out_mb"], f["nx2_out_mb"], f["nx3_out_mb"]
    out = dict(time=float(f["time"]), nmb=nmb, n=(n1, n2, n3),
               level=np.array(f["mb_logical"])[:, 3], dx=(box[:, 1] - box[:, 0])/n1)
    out["box"] = box
    names = list(f["var_names"])
    for key in ("H", "Mx", "My", "Mz"):
        nm = [v for v in names if v.endswith("_" + key) or v == key]
        out[key] = np.array(f["mb_data"][nm[0]]).transpose(0, 3, 2, 1)
    out["var_names"] = names
    return out


def con_stats(c, half_lo, half_hi, margin, masks=None):
    """Statistics of |H| and |M| of a constraint dump per level, away from the faces of
    the mesh (margin; None on the torus) and, for the ball, per region."""
    X, Y, Z, dx = lib2.blk_coords(c)
    vol = (dx**3)[:, None, None, None]*np.ones_like(X)
    h = np.abs(c["H"])
    m = np.sqrt(c["Mx"]**2 + c["My"]**2 + c["Mz"]**2)
    keep = np.ones(X.shape, dtype=bool)
    if margin is not None:
        for A in (X, Y, Z):
            keep &= (A > half_lo + margin) & (A < half_hi - margin)
    out = dict(time=c["time"], levels={})
    lev0 = int(c["level"].min())
    for lv in sorted(set(int(v) for v in c["level"])):
        mk = keep & (c["level"] == lv)[:, None, None, None]
        if mk.any():
            out["levels"][str(lv - lev0)] = dict(
                H_max=float(h[mk].max()), H_mean=float((h*vol)[mk].sum()/vol[mk].sum()),
                M_max=float(m[mk].max()), M_mean=float((m*vol)[mk].sum()/vol[mk].sum()),
                cells=int(mk.sum()))
    out["H_max"] = float(h[keep].max())
    out["M_max"] = float(m[keep].max())
    if masks:
        r = np.sqrt(X*X + Y*Y + Z*Z)
        for name, (r0, r1) in masks.items():
            mk = keep & (r >= r0) & (r < r1)
            out[name] = dict(H_mean=float((h*vol)[mk].sum()/vol[mk].sum()),
                             H_max=float(h[mk].max()),
                             M_mean=float((m*vol)[mk].sum()/vol[mk].sum()))
    return out


def blk_centre(d, base):
    """psi at the cells nearest the origin of a block dump or a uniform dump."""
    pb = os.path.join(d, base + ".idsolve.blk.bin")
    pu = os.path.join(d, base + ".idsolve.bin")
    if os.path.exists(pb):
        b = lib2.read_blk(pb)
        X, Y, Z, dx = lib2.blk_coords(b)
        r = np.sqrt(X*X + Y*Y + Z*Z)
        return b, X, Y, Z, r, b["psi"]
    b = idlib.read_idsolve_bin(pu)
    r, dxu, (X, Y, Z) = idlib.mesh_r(b)
    return b, X, Y, Z, r, b["psi"]


def record(path):
    rows, tail = lib2.summary(path)
    e = dict(outer=int(rows[-1][0]), summary=tail, lin_steps=int(rows[:, 10].sum()),
             vcycles=int(rows[:, 11].sum()), hmax_first=float(rows[0][4]),
             hmax_last=float(rows[-1][4]), rel=rows[:, 1].tolist(), far=lib2.far_line(path))
    if rows.shape[1] > 13:
        e.update(relv_first=float(rows[0][13]), relv_last=float(rows[-1][13]),
                 mmax_first=float(rows[0][16]), mmax_last=float(rows[-1][16]),
                 vmean_removed=float(rows[-1][17]))
    return e


def analyze(root, status, out_dir=None):
    """Analysis of the cases in root; numbers and figure into out_dir (default root)."""
    out_dir = out_dir or root
    res = dict(run=os.path.basename(root.rstrip("/")), status=status or {}, G={}, T={}, Z={})
    prof = {}
    for d in sorted(glob.glob(os.path.join(root, "*_*"))):
        name = os.path.basename(d)
        if not os.path.isdir(d):
            continue
        kind = name[0].upper()
        base = dict(G="gauss", T="torus", Z="ball")[kind]
        e = {}
        rec = os.path.join(d, base + ".idsolve.txt")
        if os.path.exists(rec):
            e.update(record(rec))
        cons = sorted(glob.glob(os.path.join(d, "bin", "*.con.*.bin")))
        if kind == "G":
            if cons:
                e["monitor"] = con_stats(read_con(cons[0]), -16.0, 16.0, 4.0)
            if os.path.exists(rec):
                b, X, Y, Z, r, psi = blk_centre(d, base)
                ex = make_ic.gaussian_psi(r, 1.0, 2.0)
                rel = (psi - ex)/(ex - 1.0)
                inner = r < 1.0
                e.update(err_centre=float(rel[inner].mean()), psi_max=float(psi.max()),
                         err_r6=float(rel[(r > 5.5) & (r < 6.5)].mean()))
                order = np.argsort(r.ravel())
                prof[name] = (r.ravel()[order], rel.ravel()[order])
        elif kind == "T":
            if cons:
                e["monitor"] = con_stats(read_con(cons[0]), 0.0, 2.0, None)
        elif kind == "Z":
            e["monitor"] = [con_stats(read_con(p), -32.0, 32.0, 4.0,
                                      masks=dict(interior=(0.0, 7.0), shell=(7.0, 13.5)))
                            for p in cons]
        res[kind][name] = e
    out = os.path.join(out_dir, "test_c_numbers.json")
    lib2.save_json(out, res)
    figs = figure(res, prof, out_dir)
    lib2.publish([out] + figs)
    return res


def figure(res, prof, root):
    if not res["G"]:
        return []
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    col = dict(g_uni32=fs.PAL["yellow"], g_uni64=fs.PAL["blue"], g_smr1=fs.PAL["red"],
               g_smr2=fs.PAL["green"], g_smr1_st=fs.PAL["orange"])
    lab = dict(g_uni32=r"uniform, $\Delta x=1$", g_uni64=r"uniform, $\Delta x=0.5$",
               g_smr1=r"one level ($|x_i|<4$)", g_smr2=r"two levels ($|x_i|<4$, $<2$)",
               g_smr1_st="one level, stencil mode")
    ax = axs[0]
    for name, (r, rel) in prof.items():
        nb = 40
        edges = np.linspace(0.0, 14.0, nb + 1)
        idx = np.digitize(r, edges) - 1
        ys = [np.mean(rel[idx == k]) if np.any(idx == k) else np.nan for k in range(nb)]
        ax.plot(0.5*(edges[1:] + edges[:-1]), np.abs(ys), color=col.get(name, "k"),
                label=lab.get(name, name))
    ax.set_yscale("log")
    ax.set_xlabel("$r$")
    ax.set_ylabel(r"$|(\psi-\psi_{\rm ex})/(\psi_{\rm ex}-1)|$")
    ax.legend(fontsize=5)
    ax = axs[1]
    for name, e in res["G"].items():
        if "rel" in e:
            ax.semilogy(e["rel"], color=col.get(name, "k"), label=lab.get(name, name))
    for name, e in res["T"].items():
        if "rel" in e:
            ax.semilogy(e["rel"], color="0.5", lw=0.6)
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel("residual over scale (grey: torus cases)")
    ax = axs[2]
    names = [n for n in list(res["G"]) + list(res["T"]) if "monitor" in
             dict(res["G"], **res["T"])[n]]
    allc = dict(res["G"], **res["T"])
    xs = np.arange(len(names))
    for lv, mk in (("0", "o"), ("1", "s"), ("2", "^")):
        ys = [allc[n]["monitor"]["levels"].get(lv, {}).get("H_max", np.nan) for n in names]
        ax.semilogy(xs, ys, mk, label="level %s" % lv)
    ax.set_xticks(xs)
    ax.set_xticklabels(names, rotation=90, fontsize=5)
    ax.set_ylabel(r"max $|H|$ of the run's monitor at $t=0$")
    ax.legend(fontsize=6)
    fig.tight_layout()
    path = os.path.join(root, "test_c_refined")
    fs.save(fig, path)
    plt.close(fig)
    return [path + ".png", path + ".pdf"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=lib2.EXE)
    ap.add_argument("--tests", default="g,t,z")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="")
    ap.add_argument("--analyze", default="")
    a = ap.parse_args()
    if a.analyze:
        analyze(a.analyze, None, out_dir=lib2.run_root())
        return 0
    root = lib2.run_root()
    cases = build_cases(root, os.path.abspath(a.exe), a.tests.split(","))
    if a.only:
        cases = [c for c in cases if c["name"] in a.only.split(",")]
    status = lib2.run_cases(cases, a.jobs)
    analyze(root, status)
    bad = [k for k, v in status.items() if v["status"] != "completed"]
    print("failed cases:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
