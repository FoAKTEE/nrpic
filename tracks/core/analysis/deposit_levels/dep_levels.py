#!/usr/bin/env python3
"""Deposit of a uniform lattice across a static refinement boundary (Track A's question
on the PCS cloud, outbox 20261125T161355Z; decision 0041 item 2).

    dep_levels.py --exe ATHENA --out DIR [--cases all|name,name,...]

Set-up: flat metric (nrpic_geodesic without a hole, <adm> dynamic = false), periodic box
x1 in [-16,16], x2, x3 in [-4,4], root cells of 1, MeshBlocks of 8^3, one static level
in the slab |x1| < 8 (cells of 1/2; the boundaries x1 = +-8 are planes). Particles at
rest, one per local cell (at the cell centres, or shifted by a quarter cell in x2 and x3),
mass rho0 times the local cell volume, so the density they represent is rho0 = 1
everywhere. One step (dt 1e-3; particles at rest in flat space do not move). E is read
on the x1 line through x2 = x3 = 0.1 from a tab output in full precision.

Reference: a 1D emulation of the rule of NrpicDepositSources (nrpic.cpp 872-1021): each
particle's cloud is laid on the lattice of the finest level among the owners of the nb
nearest cell centres of its own level; the part that falls into a coarser block goes to
the coarse leaf cell that contains the virtual fine cell; with a level cap the cloud keeps
the width of the cap level and is spread uniformly over the finer leaves. The problem is
planar, so the emulation in x1 alone gives E on the line.

Writes DIR/summary.json, DIR/<case>/ (deck, particles, AthenaK output), and
DIR/fig_dep_levels.{pdf,png}. Exit status 0 if D1-D5 of JOURNAL.md (2026-11-26T02:25Z)
hold, 1 otherwise.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic.io import write_nrp  # noqa: E402

X1 = (-16.0, 16.0)
X23 = (-4.0, 4.0)
XF = 8.0            # fine slab |x1| < XF
H0 = 1.0            # root cell
SLICE = 0.1

DECK = """<comment>
problem = uniform lattice across a static refinement boundary ({name})
<job>
basename = dl
<mesh>
nghost = 4
nx1 = 32
x1min = -16.0
x1max = 16.0
ix1_bc = periodic
ox1_bc = periodic
nx2 = 8
x2min = -4.0
x2max = 4.0
ix2_bc = periodic
ox2_bc = periodic
nx3 = 8
x3min = -4.0
x3max = 4.0
ix3_bc = periodic
ox3_bc = periodic
<meshblock>
nx1 = 8
nx2 = 8
nx3 = 8
<mesh_refinement>
refinement = static
max_nmb_per_rank = 1024
<refined_region1>
level = 1
x1min = -3.9
x1max = 3.9
x2min = -4.0
x2max = 4.0
x3min = -4.0
x3max = 4.0
<time>
evolution = dynamic
integrator = rk2
cfl_number = 0.25
nlim = 1
tlim = 1.0
ndiag = 1
<adm>
dynamic = false
<particles>
particle_type = nrpic
pusher = midpoint
metric = mesh
bh_mass = 0.0
bh_spin = 0.0
tolerance = 1.0e-12
max_iterations = 50
dt = 0.001
deposit = true
deposit_shape = {shape}
nfilter = 0
filter_compensate = false
deposit_max_level = {cap}
deposit_adaptive = false
deposit_max_coarsen = 31
{extra}
hist_dcycle = 1
particle_file = {pfile}
<problem>
pgen_name = nrpic_geodesic
<output1>
file_type = tab
variable = tmunu_E
dt = 0.0005
slice_x2 = {s}
slice_x3 = {s}
data_format = %.17e
"""


def lattice(shift23):
    """One particle per local cell at the cell centres (x1), shifted by shift23 local
    cells in x2 and x3; mass = rho0 dV with rho0 = 1."""
    xs = []
    ms = []
    for lev, (lo, hi) in ((0, (X1[0], -XF)), (1, (-XF, XF)), (0, (XF, X1[1]))):
        h = H0 / 2**lev
        x1 = np.arange(lo + 0.5 * h, hi, h)
        x2 = np.arange(X23[0] + (0.5 + shift23) * h, X23[1], h)
        g1, g2, g3 = np.meshgrid(x1, x2, x2, indexing="ij")
        xs.append(np.stack([g1.ravel(), g2.ravel(), g3.ravel()], axis=1))
        ms.append(np.full(g1.size, h**3))
    x = np.concatenate(xs)
    m = np.concatenate(ms)
    return x, m


# ---------------------------------------------------------------- 1D emulation
def level_of(x):
    """Level of the leaf cell at coordinate x1 (periodic in [-16,16))."""
    xw = (x - X1[0]) % (X1[1] - X1[0]) + X1[0]
    return 1 if abs(xw) < XF else 0


def bspline_weights(xi, nb):
    """Weights and first lattice index of the cloud, as nrpic.cpp 952-991 (xi in
    lattice cells from the lower mesh edge, minus 1/2)."""
    if nb == 3:
        fl = np.floor(xi + 0.5)
        dd = xi - fl
        return [0.5 * (0.5 - dd)**2, 0.75 - dd * dd, 0.5 * (0.5 + dd)**2], fl - 1
    if nb == 4:
        fl = np.floor(xi)
        sd = xi - fl
        return [(1 - sd)**3 / 6, (3 * sd**3 - 6 * sd**2 + 4) / 6,
                (-3 * sd**3 + 3 * sd**2 + 3 * sd + 1) / 6, sd**3 / 6], fl - 1
    fl = np.floor(xi)
    sd = xi - fl
    return [1 - sd, sd], fl


def emulate(shape, cap):
    """Linear density per leaf cell along x1 for the lattice (x2, x3 factor out)."""
    nb = {"cic": 2, "tsc": 3, "pcs": 4}[shape]
    L = X1[1] - X1[0]
    # leaf cells along x1: (centre, width)
    cells = []
    for lo, hi, h in ((X1[0], -XF, 1.0), (-XF, XF, 0.5), (XF, X1[1], 1.0)):
        for c in np.arange(lo + 0.5 * h, hi, h):
            cells.append((c, h))
    cen = np.array([c for c, _ in cells])
    wid = np.array([h for _, h in cells])
    mass = np.zeros(len(cells))

    def leaf_index(x):
        # lattice-cell centres never lie on a leaf face, so the containing leaf is unique
        xw = (x - X1[0]) % L + X1[0]
        j = np.nonzero(np.abs(cen - xw) < 0.5 * wid)[0]
        if len(j) != 1:
            raise RuntimeError("no unique leaf for x1 = %r" % x)
        return int(j[0])

    for xp, h_own in cells:            # one particle per leaf cell, at its centre
        mp = h_own                     # linear mass rho0 h (x2, x3 sums are uniform)
        lev0 = 1 if h_own < 1.0 else 0
        h = h_own
        if lev0 > cap:
            h = H0 / 2**cap
            ldep = cap
        else:
            # finest level among the owners of the nb nearest centres of its own level
            w0, f0 = bspline_weights((xp - X1[0]) / h - 0.5, nb)
            if nb == 3:
                base = np.floor((xp - X1[0]) / h - 0.5 + 0.5) - 1
            elif nb == 4:
                base = np.floor((xp - X1[0]) / h - 0.5) - 1
            else:
                base = np.floor((xp - X1[0]) / h - 0.5)
            lmax = lev0
            for c in range(nb):
                xc = X1[0] + (base + c + 0.5) * h
                lmax = max(lmax, level_of(xc))
            lmax = min(lmax, cap)
            h = H0 / 2**lmax
            ldep = lmax
        w, fl = bspline_weights((xp - X1[0]) / h - 0.5, nb)
        for c, wc in enumerate(w):
            xc = X1[0] + (fl + c + 0.5) * h
            j = leaf_index(xc)
            levleaf = 1 if wid[j] < 1.0 else 0
            if levleaf <= ldep:
                mass[j] += wc * mp
            else:
                # finer leaves inside the lattice cell: uniform density over them
                nsub = 2**(levleaf - ldep)
                hl = h / nsub
                for s in range(nsub):
                    xs = xc - 0.5 * h + (s + 0.5) * hl
                    mass[leaf_index(xs)] += wc * mp / nsub
    return cen, wid, mass / wid


# ---------------------------------------------------------------- AthenaK runs
def read_tab(d):
    files = sorted(f for f in os.listdir(d) if f.endswith(".tab") and "tmunu_E" in f)
    if not files:
        raise RuntimeError("no tab output in %s" % d)
    path = os.path.join(d, files[-1])
    rows = []
    with open(path) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            p = line.split()
            rows.append((float(p[2]), float(p[-1])))
    rows.sort()
    a = np.array(rows)
    return files[-1], a[:, 0], a[:, 1]


CASES = {
    # name: (shape, cap, shift23, extra)
    "cic":        ("cic", 31, 0.0, ""),
    "tsc":        ("tsc", 31, 0.0, ""),
    "pcs":        ("pcs", 31, 0.0, ""),
    "cic_s":      ("cic", 31, 0.25, ""),
    "tsc_s":      ("tsc", 31, 0.25, ""),
    "pcs_s":      ("pcs", 31, 0.25, ""),
    "cic_fs":     ("cic", 31, 0.0, "deposit_fine_shape = true"),
    "tsc_fs":     ("tsc", 31, 0.0, "deposit_fine_shape = true"),
    "pcs_fs":     ("pcs", 31, 0.0, "deposit_fine_shape = true"),
    "cic_cap":    ("cic", 0, 0.0, ""),
    "tsc_cap":    ("tsc", 0, 0.0, ""),
    "pcs_cap":    ("pcs", 0, 0.0, ""),
    "cic_capfs":  ("cic", 0, 0.0, "deposit_fine_shape = true"),
    "tsc_capfs":  ("tsc", 0, 0.0, "deposit_fine_shape = true"),
    "pcs_capfs":  ("pcs", 0, 0.0, "deposit_fine_shape = true"),
    "pcs_comp":   ("pcs", 31, 0.0, "deposit_comp_c = 0.1666666666666667\n"
                                   "deposit_comp_c2 = 0.4666666666666667"),
}


def run_case(exe, out, name):
    shape, cap, shift, extra = CASES[name]
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    x, m = lattice(shift)
    pfile = os.path.join(d, "lattice.nrp")
    write_nrp(pfile, x, np.zeros_like(x), m)
    deck = os.path.join(d, "dl.athinput")
    with open(deck, "w") as fp:
        fp.write(DECK.format(name=name, shape=shape, cap=cap, extra=extra,
                             pfile=pfile, s=SLICE))
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        st = subprocess.run([exe, "-i", deck, "-d", d], stdout=log,
                            stderr=subprocess.STDOUT, cwd=d).returncode
    return st, time.time() - t0, len(m), float(m.sum())


def files_equal(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default="all")
    args = ap.parse_args()
    names = list(CASES) if args.cases == "all" else args.cases.split(",")
    os.makedirs(args.out, exist_ok=True)
    res = {}
    for name in names:
        st, wall, n, mtot = run_case(args.exe, args.out, name)
        r = {"status": st, "wall_s": round(wall, 2), "n_particles": n,
             "mass_total": mtot}
        if st == 0:
            tabname, xa, ea = read_tab(os.path.join(args.out, name))
            shape, cap, shift, extra = CASES[name]
            xc, wc, er = emulate(shape, cap)
            r["tab"] = tabname
            r["n_cells_line"] = int(len(xa))
            ok_grid = len(xa) == len(xc) and np.allclose(xa, xc, atol=1e-12)
            r["grid_matches_emulation"] = bool(ok_grid)
            if ok_grid:
                diff = np.abs(ea - er)
                if shift != 0.0:
                    # amendment of D3: the last fine leaf beside each boundary is reported
                    edge = (np.abs(xa) > XF - 0.5) & (np.abs(xa) < XF)
                    r["edge_fine_cell_code_minus_emulation"] = float(np.max(diff[edge]))
                    diff = diff[~edge]
                r["max_rel_code_minus_emulation"] = float(np.max(diff))
            dev = ea - 1.0
            r["max_abs_dev"] = float(np.max(np.abs(dev)))
            # deviations of the cells next to the boundary x1 = +8
            sel = (xa > 7.0) & (xa < 11.0)
            r["near_boundary"] = [[float(a), float(b)] for a, b in zip(xa[sel], dev[sel])]
            far = np.array([abs(abs(v) - XF) > 3.0 for v in xa])
            r["max_abs_dev_far"] = float(np.max(np.abs(dev[far])))
            r["line_mass_sum"] = float(np.sum(ea * np.where(np.abs(xa) < XF, 0.5, 1.0)))
            np.savetxt(os.path.join(args.out, name, "line.txt"),
                       np.stack([xa, ea, er if ok_grid else np.zeros_like(ea)], 1),
                       header="x1 E_athenak E_emulation")
        res[name] = r
        print(name, json.dumps({k: v for k, v in r.items() if k != "near_boundary"}),
              flush=True)

    checks = {}

    def chk(key, cond, note):
        checks[key] = {"pass": bool(cond), "note": note}

    def get(n, k, default=np.inf):
        return res.get(n, {}).get(k, default)

    chk("all_status_0", all(r["status"] == 0 for r in res.values()), "every run status 0")
    chk("D1", get("cic", "max_abs_dev") < 1e-13, "CIC centred uniform to 1e-13")
    # D2: predicted deviations at the first coarse, second coarse, last fine cell
    pred = {"tsc": (3.0 / 16, -1.0 / 8, -1.0 / 8),
            "pcs": (46.0 / 48 + 1.0 / 6 + 1.0 / 12 - 1, 1.0 / 48 + 2.0 / 3 + 1.0 / 6 - 1,
                    2 * (1.0 / 12 + 1.0 / 3 + 1.0 / 48) - 1)}
    d2 = True
    for sh, (p1, p2, p3) in pred.items():
        nb = dict((round(a, 3), b) for a, b in res.get(sh, {}).get("near_boundary", []))
        got = (nb.get(8.5, np.nan), nb.get(9.5, np.nan), nb.get(7.75, np.nan))
        res.setdefault(sh, {})["D2_pred_got"] = [[p1, got[0]], [p2, got[1]], [p3, got[2]]]
        d2 &= all(abs(a - b) < 1e-12 for a, b in zip((p1, p2, p3), got))
        d2 &= get(sh, "max_abs_dev_far") < 1e-13
    chk("D2", d2, "TSC/PCS boundary deviations as predicted, far cells uniform")
    chk("D2_mass", all(abs(r.get("line_mass_sum", 0) - 32.0) < 1e-10 for n, r in res.items()
                       if "comp" not in n),
        "sum of E dx1 on the line = 32 (rho0 L) for every deposit without compensation")
    d3 = all(r.get("max_rel_code_minus_emulation", np.inf) < 1e-12
             for n, r in res.items() if "comp" not in n)
    chk("D3", d3, "code equals 1D emulation to 1e-12 in every leaf cell")
    d4a = True
    for sh in ("cic", "tsc", "pcs"):
        a = os.path.join(args.out, sh, res.get(sh, {}).get("tab", "x"))
        b = os.path.join(args.out, sh + "_fs", res.get(sh + "_fs", {}).get("tab", "x"))
        d4a &= os.path.exists(a) and os.path.exists(b) and files_equal(a, b)
    d4b = all(get(n, "max_abs_dev") < 1e-13 for n in
              ("cic_cap", "tsc_cap", "pcs_cap", "cic_capfs", "tsc_capfs", "pcs_capfs"))
    chk("D4", d4a and d4b, "fine_shape inert without cap (bytes); capped deposits uniform")
    if "pcs_comp" in res and "pcs" in res:
        g = get("pcs_comp", "max_abs_dev") / max(get("pcs", "max_abs_dev"), 1e-300)
        res["pcs_comp"]["gain_over_pcs"] = g
        chk("D5", (1.0 < g <= 2.2) and get("pcs_comp", "max_abs_dev_far") < 1e-12,
            "compensation enlarges the boundary error by at most ~2, interior uniform")
    summary = {"cases": res, "checks": checks,
               "verdict": "PASS" if all(c["pass"] for c in checks.values()) else "FAIL"}
    with open(os.path.join(args.out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    for k, c in checks.items():
        print("%-14s %s  %s" % (k, "HOLDS" if c["pass"] else "FAILS", c["note"]))
    figure(args.out, res)
    print("DEPOSIT LEVELS", summary["verdict"])
    return 0 if summary["verdict"] == "PASS" else 1


def figure(out, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(3)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3))
    panels = [("uncapped, centred lattice", ["cic", "tsc", "pcs"]),
              ("PCS: lattice shift, compensation", ["pcs", "pcs_s", "pcs_comp"]),
              ("level cap 0 (root-width clouds)", ["cic_capfs", "tsc_capfs", "pcs_capfs"])]
    for ax, (title, names) in zip(axs, panels):
        for c, n in zip(cols, names):
            p = os.path.join(out, n, "line.txt")
            if not os.path.exists(p):
                continue
            a = np.loadtxt(p)
            ax.plot(a[:, 0], a[:, 1] - 1.0, "o-", ms=2.5, lw=0.9, color=c, label=n)
            if "comp" not in n and np.any(a[:, 2]):
                ax.plot(a[:, 0], a[:, 2] - 1.0, "x", ms=4, color="k", lw=0)
        ax.axvline(8.0, color="0.6", lw=0.6, ls="--")
        ax.axvline(-8.0, color="0.6", lw=0.6, ls="--")
        ax.set_xlim(2.0, 14.0)
        ax.set_xlabel(r"$x^1$")
        ax.set_title(title, fontsize=9)
        ax.legend(fontsize=7, loc="lower right")
    axs[0].set_ylabel(r"$E/\rho_0 - 1$ on the line")
    axs[2].set_ylim(-1e-13, 1e-13)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_dep_levels"))


if __name__ == "__main__":
    sys.exit(main())
