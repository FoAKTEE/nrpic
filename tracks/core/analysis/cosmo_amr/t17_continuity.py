#!/usr/bin/env python3
"""T17 of the work package cosmo-amr: is the deposit continuous in the particle position
where a cloud is coarser than the leaf cells (prediction:
tracks/core/JOURNAL-cosmo-amr.md, entries of T17).

    t17_continuity.py --exe EXE --out DIR [--cores N] [--analyse-only]

Homogeneous-universe deck of T1 (box [-3, 3)^3, root 24^3, cells h = 0.25), static level
1 on the central MeshBlock [-1, 1]^3, clouds on the root level (deposit_max_level = 0),
no filter, no step.  One particle at (x_c + s h, 0.2, 0.175), x_c = 0.125 the centre of a
root cell inside the patch; table of tmunu_E along the x line through the leaf row of
the particle.  Shapes cic, tsc, pcs; spreading uniform ("const") and deposit_fine_shape
("lin"); twelve offsets s.  Measured: the share f of each of the ten leaf cells of the
five root cells around x_c in the sum of E along the line (the one-dimensional weights
of the leaf cells), against three references: the uniform spreading, the first-order
form with the analytic slope (source 3c44b74), and for the linear cloud the leaf-cell
integrals of the assignment function shifted to the weight of the lattice cell.
Writes DIR/t17_summary.json and DIR/fig_t17_continuity.{pdf,png}."""
import argparse
import glob
import json
import os
import sys

import numpy as np

import amrlib as A

L, N, NB = 6.0, 24, 8
H = L/N
XC = 0.125
YP, ZP = 0.2, 0.175
YL, ZL = 0.1875, 0.1875
OFFS = (-0.45, -0.3, -0.15, -0.05, -0.01, -1e-6, 1e-6, 0.01, 0.05, 0.15, 0.3, 0.45)
SHAPES = ("cic", "tsc", "pcs")
CELLS = (-2, -1, 0, 1, 2)          # root cells around x_c whose leaves are measured


def lattice(shape, s):
    """Lattice weights and analytic slopes of a cloud at offset s (in lattice cells)
    from the centre of cell 0, as in NrpicDepositSources: dict cell -> (w, g)."""
    if shape == "cic":
        fl = int(np.floor(s))
        sd = s - fl
        return {fl: (1.0 - sd, 1.0), fl + 1: (sd, -1.0)}
    if shape == "tsc":
        fl = int(np.floor(s + 0.5))
        dd = s - fl
        return {fl - 1: (0.5*(0.5 - dd)**2, 0.5 - dd), fl: (0.75 - dd*dd, 2.0*dd),
                fl + 1: (0.5*(0.5 + dd)**2, -(0.5 + dd))}
    fl = int(np.floor(s))
    sd = s - fl
    return {fl - 1: ((1 - sd)**3/6.0, 0.5*(1 - sd)**2),
            fl: ((3*sd**3 - 6*sd**2 + 4)/6.0, 2*sd - 1.5*sd*sd),
            fl + 1: ((-3*sd**3 + 3*sd**2 + 3*sd + 1)/6.0, -2*(1 - sd) + 1.5*(1 - sd)**2),
            fl + 2: (sd**3/6.0, -0.5*sd*sd)}


def ref_const(shape, s):
    lat = lattice(shape, s)
    return np.array([lat.get(c, (0.0, 0.0))[0]/2 for c in CELLS for _ in (0, 1)])


def ref_slope(shape, s):
    lat = lattice(shape, s)
    out = []
    for c in CELLS:
        w, g = lat.get(c, (0.0, 0.0))
        out += [(w - 0.25*g)/2, (w + 0.25*g)/2]
    return np.array(out)


def tent_cdf(t):
    t = np.clip(t, -1.0, 1.0)
    return np.where(t < 0, 0.5*(1 + t)**2, 1.0 - 0.5*(1 - t)**2)


def ref_integral_cic(s):
    """Linear cloud: leaf-cell integrals of the tent, plus the same amount in both leaves
    of a lattice cell so that they sum to the weight of the lattice cell."""
    lat = lattice("cic", s)
    out = []
    for c in CELLS:
        w = lat.get(c, (0.0, 0.0))[0]
        e = np.array([c - 0.5, c, c + 0.5]) - s
        f = tent_cdf(e)
        i0, i1 = f[1] - f[0], f[2] - f[1]
        sh = 0.5*(w - (i0 + i1))
        out += [i0 + sh, i1 + sh]
    return np.array(out)


def base(ic):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo/flrw.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": N, f"x{d}min": -L/2, f"x{d}max": L/2})
        b.set("meshblock", **{f"nx{d}": NB})
    b.set("time", tlim=10.0, nlim=0)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"), snap_dt=-1.0,
          probe_x1=0.01, probe_x2=0.01, probe_x3=0.01, cstat_dcycle=1, hist_dcycle=1,
          nfilter=0, filter_compensate=False, deposit_max_level=0, deposit_adaptive=False)
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    b.set("output1", file_type="hst", dt=0.5)
    b.set("output2", file_type="tab", variable="tmunu_E", dt=100.0, slice_x2=YL,
          slice_x3=ZL, data_format="%24.16e")
    b.set("mesh_refinement", refinement="static", max_nmb_per_rank=64)
    b.set("refined_region1", level=1, x1min=-0.5, x1max=0.5, x2min=-0.5, x2max=0.5,
          x3min=-0.5, x3max=0.5)
    return b


def leaves(rundir):
    fs = sorted(glob.glob(os.path.join(rundir, "tab", "flrw.tmunu_E.*.tab")))
    d, _ = A.read_tab(fs[0])
    xk = [k for k in d if k.startswith("x1")][0]
    ek = [k for k in d if "tmunu" in k or k == "E"]
    ek = ek[0] if ek else list(d)[-1]
    x, e = d[xk], d[ek]
    tot = float(np.sum(e))
    out = []
    for c in CELLS:
        for q in (-0.25, 0.25):
            xl = XC + (c + q)*H
            i = int(np.argmin(np.abs(x - xl)))
            if abs(x[i] - xl) > 1e-9:
                raise RuntimeError(f"no leaf cell at x = {xl} in {fs[0]}")
            out.append(e[i]/tot)
    return np.array(out), tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args()
    a.out, a.exe = os.path.abspath(a.out), os.path.abspath(a.exe)
    os.makedirs(a.out, exist_ok=True)
    from nrp_io import write_particles
    jobs, keys = [], []
    for io, s in enumerate(OFFS):
        ic = os.path.join(a.out, "ic", f"s{io:02d}")
        if not a.analyse_only:
            os.makedirs(ic, exist_ok=True)
            write_particles(os.path.join(ic, "particles.nrp"),
                            np.array([[XC + s*H, YP, ZP]]), np.zeros((1, 3)),
                            np.array([1e-6]))
        for shape in SHAPES:
            for fine in (False, True):
                b = base(ic).set("particles", deposit_shape=shape)
                if fine:
                    b.set("particles", deposit_fine_shape=True)
                key = (shape, "lin" if fine else "const", io)
                keys.append(key)
                jobs.append((a.exe, b, os.path.join(a.out, f"{key[0]}-{key[1]}", f"s{io:02d}"),
                             "flrw", (), None))
    if not a.analyse_only:
        rcs = A.run_many(jobs, a.cores)
        bad = [k for k, rc in zip(keys, rcs) if rc[0] != 0]
        print(f"{len(jobs)} runs, {len(bad)} with a non-zero exit status {bad[:6]}", flush=True)
    f = {}
    for key, j in zip(keys, jobs):
        f[key], _ = leaves(j[2])
    im, ip = OFFS.index(-1e-6), OFFS.index(1e-6)
    res = {}
    for shape in SHAPES:
        for mode in ("const", "lin"):
            arr = np.array([f[(shape, mode, io)] for io in range(len(OFFS))])
            r = {"jump": float(np.max(np.abs(arr[ip] - arr[im]))),
                 "pattern_minus": [float(v) for v in arr[im]],
                 "pattern_plus": [float(v) for v in arr[ip]],
                 "min_share": float(arr.min()),
                 "dev_const": float(max(np.max(np.abs(arr[io] - ref_const(shape, s)))
                                        for io, s in enumerate(OFFS))),
                 "dev_slope": float(max(np.max(np.abs(arr[io] - ref_slope(shape, s)))
                                        for io, s in enumerate(OFFS)))}
            if shape == "cic":
                r["dev_integral"] = float(max(np.max(np.abs(arr[io] - ref_integral_cic(s)))
                                              for io, s in enumerate(OFFS)))
            # largest change of a leaf share between neighbouring offsets, per unit of s
            r["max_rate"] = float(max(np.max(np.abs(arr[i+1] - arr[i]))/(OFFS[i+1] - OFFS[i])
                                      for i in range(len(OFFS) - 1) if i != im))
            res[f"{shape}-{mode}"] = r
            print(f"{shape}-{mode:5s} jump {r['jump']:.3e}  min share {r['min_share']:+.4f}  "
                  f"dev const {r['dev_const']:.2e} slope {r['dev_slope']:.2e}"
                  + (f" integral {r['dev_integral']:.2e}" if shape == "cic" else ""),
                  flush=True)
    with open(os.path.join(a.out, "t17_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(10.0, 5.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.12, top=0.94, wspace=0.06,
                        hspace=0.10)
    sfine = np.linspace(-0.49, 0.49, 197)
    show = (3, 4, 5, 6)             # leaves of cell -1 (right), cell 0, cell +1 (left)
    names = {3: "cell $-1$, right leaf", 4: "cell 0, left leaf", 5: "cell 0, right leaf",
             6: "cell $+1$, left leaf"}
    for ic_, shape in enumerate(SHAPES):
        for im_, mode in enumerate(("const", "lin")):
            q = ax[im_, ic_]
            arr = np.array([f[(shape, mode, io)] for io in range(len(OFFS))])
            for n, j in enumerate(show):
                q.plot(OFFS, arr[:, j], "o", ms=3.5, color=fs.SERIES[n], label=names[j])
                if mode == "lin":
                    q.plot(sfine, [ref_slope(shape, s)[j] for s in sfine], "-", lw=0.8,
                           color=fs.SERIES[n])
                    if shape == "cic":
                        q.plot(sfine, [ref_integral_cic(s)[j] for s in sfine], "--", lw=0.8,
                               color=fs.SERIES[n])
                else:
                    q.plot(sfine, [ref_const(shape, s)[j] for s in sfine], "-", lw=0.8,
                           color=fs.SERIES[n])
            q.axhline(0.0, color="grey", lw=0.5, ls=":")
            q.set_title(f"{shape}, " + ("fine shape" if mode == "lin" else "uniform spreading"),
                        fontsize=9)
            if im_ == 1 and ic_ == 1:
                q.set_xlabel(r"offset $s$ of the particle from the centre of cell 0 (cells)")
            if ic_ == 0:
                q.set_ylabel("share of the leaf cell")
    ax[0, 0].legend(frameon=False, fontsize=7, loc="center left")
    fig.text(0.07, 0.01, "points: run; lines: the forms in the script (dashed: integral "
             "form of the linear cloud)", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_t17_continuity"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
