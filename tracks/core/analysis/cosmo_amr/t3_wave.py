#!/usr/bin/env python3
"""T3 of the work package cosmo-amr: the linear plane wave with a refined patch
(prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t3_wave.py --new NEW_EXE --out DIR [--cores N] [--tlim T]

Test B of arXiv:1904.07841 as in cosmo/TESTLOG.md (delta_N = 1e-7 sin(2 pi x/L),
L = 1.35085, 32 cells per wavelength, eight particles per cell, quadratic cloud).  The
data are built by cosmo/ic/make_east.py on the cube and cut down to the slab
0 <= y, z < L/4 (the wave depends on x only, the lattice has the period of a cell), so
the mesh is 32 x 8 x 8 with MeshBlocks of 8^3.  All cases take the step of level 1.
  U    uniform                           S    level 1 on L/4 < x < 3L/4, clouds capped
  Sf   S with deposit_fine_shape              at the root level, constant spreading
  Sx   clouds on the finest level        P    Sf with the patch across the x face
  Uq, Sq, Sfq  U, S, Sf with two binomial passes and the compensation (data built with
       the same filter): the filter acts at the cell size of each level
Measured at the end from AthenaK tables along x: sine fits of chi and of E (amplitude,
phase, rms residual over the amplitude); at t = 0 the Hamiltonian constraint over
16 pi times the amplitude of E.  Writes DIR/t3_summary.json, DIR/fig_t3_wave.{pdf,png}."""
import argparse
import glob
import json
import os
import struct
import subprocess
import sys

import numpy as np

import amrlib as A

LBOX, N, NY = 1.35085, 32, 8


def read_fields(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRCOSMO1"
        n1, n2, n3 = struct.unpack("qqq", f.read(24))
        return [np.fromfile(f, dtype=np.float64, count=n1*n2*n3).reshape(
            (n1, n2, n3), order="F") for _ in range(9)]


def read_particles(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        n, = struct.unpack("q", f.read(8))
        rec = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
        sp = np.fromfile(f, dtype=np.int32, count=n)
    return rec, sp


def make_slab(cube, slab):
    """Cut the cubic data down to 0 <= y, z < L/4."""
    from nrp_io import write_fields, write_particles
    os.makedirs(slab, exist_ok=True)
    fl = read_fields(os.path.join(cube, "fields.bin"))
    spread = max(float(np.max(np.abs(a - a[:, :1, :1]))) for a in fl)
    cut = [a[:, :NY, :NY] for a in fl]
    write_fields(os.path.join(slab, "fields.bin"), cut[0], cut[1], cut[2], cut[3:])
    rec, sp = read_particles(os.path.join(cube, "particles.nrp"))
    lim = LBOX*NY/N
    keep = (rec[:, 1] >= 0) & (rec[:, 1] < lim) & (rec[:, 2] >= 0) & (rec[:, 2] < lim)
    write_particles(os.path.join(slab, "particles.nrp"), rec[keep, 0:3], rec[keep, 3:6],
                    rec[keep, 6], sp[keep])
    return dict(particles=int(keep.sum()), yz_dependence_of_fields=spread)


def deck(ic, tlim, filt):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo/daverio_mode.athinput"))
    b.set("mesh", nx2=NY, nx3=NY, x2max=LBOX*NY/N, x3max=LBOX*NY/N)
    for d in "123":
        b.set("meshblock", **{f"nx{d}": 8})
    b.set("time", tlim=tlim)
    b.set("particles", particle_file=os.path.join(ic, "particles.nrp"),
          dt=0.25*LBOX/(2*N), hist_dcycle=8, cstat_dcycle=8, line_dcycle=0,
          traj_ntrack=0, nprobe=0, probe_x1=0.1, probe_x2=0.1, probe_x3=0.1,
          region_dcycle=8, region_radius1=0.2, snap_dt=-1.0)
    if filt:
        b.set("particles", nfilter=2, filter_compensate=True)
    b.set("problem", id_file=os.path.join(ic, "fields.bin"))
    for k in list(b.blocks):
        if k.startswith("output"):
            b.drop(k)
    b.set("output1", file_type="hst", dt=0.5)
    for n, var in enumerate(("z4c", "tmunu_E", "con")):
        # 17 significant digits: the wave has a relative amplitude of 1e-7, which the
        # default format (%12.5e, six digits) does not resolve
        b.set(f"output{n+2}", file_type="tab", variable=var, dt=tlim, slice_x2=0.01,
              slice_x3=0.01, data_format="%24.16e")
    return b


def patch(b, regions, cap_root=True, fine=False):
    b.set("mesh_refinement", refinement="static", max_nmb_per_rank=128)
    for n, (x0, x1) in enumerate(regions):
        b.set(f"refined_region{n+1}", level=1, x1min=x0, x1max=x1, x2min=0.0,
              x2max=LBOX*NY/N, x3min=0.0, x3max=LBOX*NY/N)
    b.set("particles", deposit_max_level=(0 if cap_root else 31))
    if fine:
        b.set("particles", deposit_fine_shape=True)
    return b


def weights(x):
    """Cell width of every point of a line that mixes two levels."""
    o = np.argsort(x)
    xs = x[o]
    d = np.diff(xs)
    w = np.empty_like(xs)
    w[1:-1] = np.minimum(d[:-1], d[1:])
    w[0], w[-1] = d[0], d[-1]
    out = np.empty_like(w)
    out[o] = w
    return out


def sinefit(x, y):
    k = 2.0*np.pi/LBOX
    w = weights(x)
    M = np.stack([np.ones_like(x), np.sin(k*x), np.cos(k*x)], axis=1)
    sw = np.sqrt(w)
    c, *_ = np.linalg.lstsq(M*sw[:, None], y*sw, rcond=None)
    fit = M @ c
    amp = float(np.hypot(c[1], c[2]))
    res = y - fit
    return dict(mean=float(c[0]), amp=amp, phase=float(np.arctan2(c[2], c[1])),
                resid=float(np.sqrt(np.sum(w*res**2)/np.sum(w))/amp)), res/amp, fit


def tabs(d, var):
    fs = sorted(glob.glob(os.path.join(d, "tab", f"east.{var}.*.tab")))
    return [A.read_tab(f) for f in fs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--tlim", type=float, default=2.0)
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    os.makedirs(a.out, exist_ok=True)
    info = {}
    ics = {}
    for tag, extra in (("plain", []), ("filter", ["--nfilter", "2", "--compensate"])):
        cube, slab = os.path.join(a.out, "ic_cube_" + tag), os.path.join(a.out, "ic_" + tag)
        if not os.path.exists(os.path.join(slab, "fields.bin")):
            subprocess.run([sys.executable, os.path.join(A.ROOT, "cosmo/ic/make_east.py"),
                            "--delta", "1e-7", "--n", str(N), "--ppc", "2", "--L",
                            repr(LBOX), "--ratios", "1,0,0", "--shape", "tsc", "--out",
                            cube] + extra, check=True, stdout=subprocess.DEVNULL,
                           cwd=os.path.join(A.ROOT, "cosmo/ic"))
            info["ic_" + tag] = make_slab(cube, slab)
        ics[tag] = slab
    q, h = LBOX/4, LBOX/2
    cs = {
        "U": deck(ics["plain"], a.tlim, False),
        "S": patch(deck(ics["plain"], a.tlim, False), [(q, 3*q)]),
        "Sf": patch(deck(ics["plain"], a.tlim, False), [(q, 3*q)], fine=True),
        "Sx": patch(deck(ics["plain"], a.tlim, False), [(q, 3*q)], cap_root=False),
        "P": patch(deck(ics["plain"], a.tlim, False), [(0.0, q), (3*q, LBOX)], fine=True),
        "Uq": deck(ics["filter"], a.tlim, True),
        "Sq": patch(deck(ics["filter"], a.tlim, True), [(q, 3*q)]),
        "Sfq": patch(deck(ics["filter"], a.tlim, True), [(q, 3*q)], fine=True),
    }
    names = list(cs)
    rcs = A.run_many([(a.new, cs[n], os.path.join(a.out, n), "east", (), None)
                      for n in names], a.cores)
    res, prof = {}, {}
    for n, rc in zip(names, rcs):
        d = os.path.join(a.out, n)
        r = dict(exit=rc[0], wall=round(rc[1], 1))
        hst = A.read_hst(os.path.join(d, "east.nrpic.hst"))
        cst = A.read_hst(os.path.join(d, "east.cstat.hst"))
        r.update(nmb=int(hst["nmb"][0]), t_end=float(hst["time"][-1]),
                 identity_E=float(np.max(np.abs(hst["int_E"]/hst["sum_mW"] - 1.0))),
                 Hr_max_t0=float(cst["Hr_max"][0]), Hr_max_end=float(cst["Hr_max"][-1]),
                 H_max_t0=float(cst["H_max"][0]), H_max_end=float(cst["H_max"][-1]))
        z, e, c = tabs(d, "z4c"), tabs(d, "tmunu_E"), tabs(d, "con")
        if len(z) >= 2 and len(e) >= 2 and len(c) >= 2:
            x0, e0 = e[0][0]["x1v"], e[0][0]["tmunu_E"]
            fe0, _, _ = sinefit(x0, e0)
            hh = c[0][0]["con_H"]
            inp = (c[0][0]["x1v"] > q) & (c[0][0]["x1v"] < 3*q)
            r["H_over_16piE_t0_patch"] = float(np.max(np.abs(hh[inp]))/(16*np.pi*fe0["amp"]))
            r["H_over_16piE_t0_all"] = float(np.max(np.abs(hh))/(16*np.pi*fe0["amp"]))
            r["E_t0"] = fe0
            x1, e1, chi1 = e[-1][0]["x1v"], e[-1][0]["tmunu_E"], z[-1][0]["z4c_chi"]
            fe1, re1, _ = sinefit(x1, e1)
            fc1, rc1, _ = sinefit(z[-1][0]["x1v"], chi1)
            r["E_end"], r["chi_end"] = fe1, fc1
            r["E_contrast_end"] = fe1["amp"]/fe1["mean"]
            r["chi_contrast_end"] = fc1["amp"]/fc1["mean"]
            prof[n] = dict(x=x1, de=(e1 - fe1["mean"])/fe1["amp"], re=re1,
                           xz=z[-1][0]["x1v"], rc=rc1, x0=c[0][0]["x1v"],
                           h0=hh/(16*np.pi*fe0["amp"]))
        res[n] = r
    for n in names:
        ref = "Uq" if n.endswith("q") else "U"
        if "chi_end" in res.get(n, {}) and "chi_end" in res.get(ref, {}):
            res[n]["chi_amp_over_U"] = res[n]["chi_contrast_end"]/res[ref]["chi_contrast_end"]
            res[n]["E_amp_over_U"] = res[n]["E_contrast_end"]/res[ref]["E_contrast_end"]
            dph = res[n]["chi_end"]["phase"] - res[ref]["chi_end"]["phase"]
            res[n]["chi_phase_minus_U"] = float((dph + np.pi) % (2*np.pi) - np.pi)
    res["info"] = info
    with open(os.path.join(a.out, "t3_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(8.0, 6.0))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.97, wspace=0.28,
                        hspace=0.24)
    cols = dict(U=fs.PAL["blue"], S=fs.PAL["yellow"], Sf=fs.PAL["red"],
                Sx=fs.PAL["green"], P=fs.PAL["orange"], Uq=fs.PAL["blue"],
                Sq=fs.PAL["yellow"], Sfq=fs.PAL["red"])
    for n in ("U", "S", "Sf", "Sx", "P"):
        if n in prof:
            o = np.argsort(prof[n]["x"])
            ax[0, 0].plot(prof[n]["x"][o]/LBOX, prof[n]["re"][o], color=cols[n], lw=1.0,
                          label=n)
            o = np.argsort(prof[n]["xz"])
            ax[0, 1].plot(prof[n]["xz"][o]/LBOX, prof[n]["rc"][o], color=cols[n], lw=1.0,
                          label=n)
            o = np.argsort(prof[n]["x0"])
            ax[1, 0].plot(prof[n]["x0"][o]/LBOX, prof[n]["h0"][o], color=cols[n], lw=1.0,
                          label=n)
    for n in ("Uq", "Sq", "Sfq"):
        if n in prof:
            o = np.argsort(prof[n]["x0"])
            ax[1, 1].plot(prof[n]["x0"][o]/LBOX, prof[n]["h0"][o], color=cols[n], lw=1.0,
                          label=n)
    for q_ in ax.ravel():
        q_.axvspan(0.25, 0.75, color="grey", alpha=0.1)
        q_.set_xlabel("x / L")
        q_.legend(frameon=False, ncol=3, fontsize=8)
    ax[0, 0].set_ylabel("E: residual of the sine fit / amplitude (end)")
    ax[0, 1].set_ylabel(r"$\chi$: residual of the sine fit / amplitude (end)")
    ax[1, 0].set_ylabel(r"$H/(16\pi\,\delta E)$ at $t=0$, no filter")
    ax[1, 1].set_ylabel(r"$H/(16\pi\,\delta E)$ at $t=0$, source filter")
    fs.save(fig, os.path.join(a.out, "fig_t3_wave"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
