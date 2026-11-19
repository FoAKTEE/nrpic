"""Figures of the tests of work package mpi (called by mpi_tests.py).

One figure per case, `<case>_ranks`: trajectories of tracked particles on the three rank
counts over the MeshBlock grid, particles per rank against time, and the differences of
the history columns from the one-rank run.  Cases with deposit get a second figure,
`<case>_fields`: the energy density in the cells nearest the plane z = 0 on one rank, its
difference on four ranks, and the conservation identity of each run against time.
"""
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nrpic import figstyle as fs

NP_COLOR = {1: fs.PAL["blue"], 2: fs.PAL["red"], 4: fs.PAL["green"], 3: fs.PAL["orange"],
            8: fs.PAL["yellow"]}
NP_STYLE = {1: "-", 2: "--", 4: ":", 3: "-.", 8: "-."}


def _table(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                rows.append([float(t) for t in s.split()])
            except ValueError:
                continue
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


def _one(base, n, pattern):
    g = sorted(glob.glob(os.path.join(base, "np%d" % n, pattern)))
    return g[0] if g else None


def _mesh_lines(par):
    """MeshBlock edges of the uniform mesh of the input file (x1 and x2)."""
    out = []
    for d in ("1", "2"):
        lo, hi = float(par["mesh"]["x%smin" % d]), float(par["mesh"]["x%smax" % d])
        nb = int(par["mesh"]["nx" + d])//int(par["meshblock"]["nx" + d])
        out.append(np.linspace(lo, hi, nb + 1))
    return out


def _read_input(path):
    par, blk = {}, None
    with open(path) as f:
        for line in f:
            s = line.split("#")[0].strip()
            if s.startswith("<") and s.endswith(">"):
                blk = s.strip("<>")
                par.setdefault(blk, {})
            elif "=" in s and blk:
                k, v = s.split("=", 1)
                par[blk][k.strip()] = v.strip()
    return par


def fig_ranks(case, ranks, base, inp):
    fs.use_style()
    par = _read_input(inp)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.0))
    ax = fig.add_axes([0.07, 0.12, 0.40, 0.80])
    xe, ye = _mesh_lines(par)
    for x in xe:
        ax.axvline(x, color="grey", lw=0.5, alpha=0.4)
    for y in ye:
        ax.axhline(y, color="grey", lw=0.5, alpha=0.4)
    periodic = par["mesh"].get("ix1_bc", "") == "periodic"
    shown = 16
    for n in ranks:
        f = _one(base, n, "*.traj.bin")
        if f is None:
            continue
        rec = np.fromfile(f, dtype="<f8").reshape(-1, 8)
        for tag in range(shown):
            r = rec[rec[:, 1] == tag]
            if len(r) == 0:
                continue
            x, y = r[:, 2].copy(), r[:, 3].copy()
            if periodic:      # break the line where the particle wraps
                jump = (np.abs(np.diff(x)) > 0.5*(xe[-1] - xe[0])) | \
                       (np.abs(np.diff(y)) > 0.5*(ye[-1] - ye[0]))
                x[1:][jump] = np.nan
            ax.plot(x, y, color=NP_COLOR.get(n, "k"), ls=NP_STYLE.get(n, "-"),
                    lw=1.2 if n == ranks[0] else 1.0,
                    label=("%d rank%s" % (n, "" if n == 1 else "s")) if tag == 0 else None)
    ax.set_xlim(xe[0], xe[-1])
    ax.set_ylim(ye[0], ye[-1])
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right", ncol=1, fontsize=8)
    ax.set_title("%d tracked particles, MeshBlock edges in grey" % shown, fontsize=10)

    # particles per rank
    ax2 = fig.add_axes([0.57, 0.57, 0.40, 0.35])
    for n in ranks[1:]:
        f = _one(base, n, "*.mpi.hst")
        if f is None:
            continue
        a = _table(f)
        for r in range(n):
            ax2.plot(a[:, 0], a[:, 4 + r], color=NP_COLOR.get(n, "k"), lw=1.0,
                     ls=["-", "--", ":", "-."][r % 4],
                     label=("%d ranks" % n) if r == 0 else None)
    ax2.set_ylabel("particles per rank", fontsize=9)
    ax2.legend(loc="center right", fontsize=8)
    ax2.set_xticklabels([])

    # differences of the history from one rank
    ax3 = fig.add_axes([0.57, 0.12, 0.40, 0.40])
    f1 = _one(base, ranks[0], "*.nrpic.hst")
    a1 = _table(f1)
    cols = {"sum m": 3, "sum m u_x": 5, "int E": 8, "volume": 27}
    floor = 1.0e-18
    for n in ranks[1:]:
        fn = _one(base, n, "*.nrpic.hst")
        if fn is None:
            continue
        an = _table(fn)
        if an.shape != a1.shape:
            continue
        for q, (name, c) in enumerate(cols.items()):
            scale = max(np.abs(a1[:, c]).max(), 1.0e-300)
            d = np.abs(an[:, c] - a1[:, c])/scale
            if np.abs(a1[:, c]).max() == 0.0:
                continue
            ax3.semilogy(a1[:, 0], np.maximum(d, floor), color=fs.SERIES[q],
                         ls=NP_STYLE.get(n, "-"), lw=1.0,
                         label=name if n == ranks[1] else None)
    ax3.axhline(2.2e-16, **fs.MASK_LINE)
    ax3.set_ylim(floor, 1.0e-9)
    ax3.set_xlabel("t")
    ax3.set_ylabel("rel. difference from 1 rank", fontsize=9)
    ax3.legend(loc="upper right", ncol=2, fontsize=8)
    ax2.set_xlim(ax3.get_xlim())
    return fig


def fig_fields(case, ranks, base):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mpi_tests import read_bin_blocks
    fs.use_style()
    files = sorted(glob.glob(os.path.join(base, "np%d" % ranks[0], "bin", "*.bin")))
    if not files:
        return None
    t, b1 = read_bin_blocks(files[-1])
    name = "tmunu_E"
    # the layer of MeshBlocks just above the mid plane, first layer of cells
    zs = sorted(set(k[2] for k in b1))
    zmid = 0.5*(min(zs) + max(zs))
    zsel = min((z for z in zs if z >= zmid - 1.0e-9), default=zs[0])
    keys = [k for k in b1 if abs(k[2] - zsel) < 1.0e-9]
    xs = sorted(set(k[0] for k in keys))
    ys = sorted(set(k[1] for k in keys))
    nz, ny, nx = b1[keys[0]][name].shape
    img1 = np.zeros((len(ys)*ny, len(xs)*nx))
    for k in keys:
        i, j = xs.index(k[0]), ys.index(k[1])
        img1[j*ny:(j+1)*ny, i*nx:(i+1)*nx] = b1[k][name][0]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax = fig.add_axes([0.06, 0.15, 0.24, 0.72])
    pos = np.where(img1 > 0, img1, np.nan)
    vmax = np.nanmax(pos) if np.isfinite(pos).any() else 1.0
    im = ax.imshow(pos, origin="lower", cmap=fs.CMAP["dens"], aspect="equal",
                   norm=matplotlib.colors.LogNorm(vmin=vmax*1.0e-3, vmax=vmax),
                   interpolation="none", rasterized=True)
    for q in range(1, len(xs)):
        ax.axvline(q*nx - 0.5, color="white", lw=0.4, alpha=0.5)
    for q in range(1, len(ys)):
        ax.axhline(q*ny - 0.5, color="white", lw=0.4, alpha=0.5)
    ax.set_title("E on 1 rank, t = %.3g" % t, fontsize=10)
    ax.set_xlabel("cell in x")
    ax.set_ylabel("cell in y")
    fs.side_colorbar(fig, ax, im, "")

    # deposited E and S_i at the particles (double precision), difference from 1 rank
    floor = 1.0e-18
    ax = fig.add_axes([0.43, 0.15, 0.23, 0.72])
    f1 = _one(base, ranks[0], "*.trajmet.bin")
    if f1 is not None:
        a = np.fromfile(f1, "<f8").reshape(-1, 17)
        times = np.unique(a[:, 0])
        for n in ranks[1:]:
            fn = _one(base, n, "*.trajmet.bin")
            if fn is None:
                continue
            b = np.fromfile(fn, "<f8").reshape(-1, 17)
            if b.shape != a.shape:
                continue
            sE = max(np.abs(a[:, 13]).max(), 1.0e-300)
            sS = max(np.abs(a[:, 14:]).max(), 1.0e-300)
            dE = np.abs(a[:, 13] - b[:, 13])/sE
            dS = np.abs(a[:, 14:] - b[:, 14:]).max(axis=1)/sS
            idx = np.searchsorted(times, a[:, 0])
            mE = np.zeros(len(times))
            mS = np.zeros(len(times))
            np.maximum.at(mE, idx, dE)
            np.maximum.at(mS, idx, dS)
            ax.semilogy(times, np.maximum(mE, floor), color=NP_COLOR.get(n, "k"), lw=1.0,
                        label="%d ranks" % n)
            ax.semilogy(times, np.maximum(mS, floor), color=NP_COLOR.get(n, "k"), lw=1.0,
                        ls="--")
    ax.axhline(2.2e-16, **fs.MASK_LINE)
    ax.set_ylim(floor, 1.0)
    ax.set_xlabel("t")
    ax.set_ylabel("max. difference from 1 rank / max", fontsize=9, labelpad=1)
    ax.set_title("E (solid), S_i (dashed) at the particles", fontsize=10)
    ax.legend(loc="upper right", fontsize=8)

    ax = fig.add_axes([0.76, 0.15, 0.22, 0.72])
    for n in ranks:
        f = _one(base, n, "*.nrpic.hst")
        if f is None:
            continue
        a = _table(f)
        smw = np.maximum(np.abs(a[:, 4]), 1.0e-300)
        dE = np.abs(a[:, 8] - a[:, 4])/smw
        dS = np.abs(a[:, 9:12] - a[:, 5:8]).max(axis=1)/smw
        ax.semilogy(a[:, 0], np.maximum(dE, floor), color=NP_COLOR.get(n, "k"), lw=1.0,
                    label="%d rank%s" % (n, "" if n == 1 else "s"))
        ax.semilogy(a[:, 0], np.maximum(dS, floor), color=NP_COLOR.get(n, "k"), lw=1.0,
                    ls="--")
    ax.axhline(2.2e-16, **fs.MASK_LINE)
    ax.set_ylim(floor, 1.0)
    ax.set_xlabel("t")
    ax.set_title("mesh integral - particle sum", fontsize=10)
    ax.set_ylabel("|difference| / sum m W", fontsize=9, labelpad=1)
    ax.legend(loc="upper right", fontsize=8)
    return fig


def make(case, ranks, base, figdir=None):
    out = []
    inps = sorted(glob.glob(os.path.join(base, "*.athinput")))
    if inps:
        inp = inps[0]
    else:
        import mpi_tests
        inp = os.path.join(mpi_tests.REPO, mpi_tests.CASES[case]["input"])
    dirs = [os.path.join(base, "figs")] + ([figdir] if figdir else [])
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    fig = fig_ranks(case, ranks, base, inp)
    for d in dirs:
        out += fs.save(fig, os.path.join(d, case + "_ranks"))
    plt.close(fig)
    fig = fig_fields(case, ranks, base)
    if fig is not None:
        for d in dirs:
            out += fs.save(fig, os.path.join(d, case + "_fields"))
        plt.close(fig)
    return out
