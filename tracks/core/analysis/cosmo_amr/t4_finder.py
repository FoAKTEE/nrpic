#!/usr/bin/env python3
"""T4 of the work package cosmo-amr: the apparent-horizon finder in a periodic box
(prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t4_finder.py --new NEW_EXE --rel REL_EXE --out DIR [--cores N]

A lattice of unit punctures on the torus through the cosmology generator (file data):
psi = 1 + 1/(2 r_min), r_min the distance to the nearest image of the puncture, K = 0,
lapse psi^-2; box [-4, 4)^3, uniform 64^3 (dx = 1/8), one cycle in the moving-puncture
gauge of problems/cosmo_amr/punc_box16.athinput, finder with metric_drvts = interpolant.
The data of a hole on a face or at a corner of the box are those of the hole at the
centre translated by 32 cells.  Cases:
  a   hole at the centre, finder at (0, 0, 0)        b   finder one period away (8, 0, 0)
  c   hole on the face x = 4, finder at (4, 0, 0)    c2  finder at (-4, 0, 0)
  d   hole at the corner, finder at (4, 4, 4)        e   finder at (-4, -4, -4)
  brel, crel  cases b and c with the release executable
  adir, adirrel  case a started in another directory than the -d output directory
Writes DIR/t4_summary.json and DIR/fig_t4_finder.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A

LBOX, N = 8.0, 64
CALIB = 0.991521          # docs/TESTLOG.md, corrected finder, dx = M/8
TRACKA = 0.9915211031     # Track A, run A-emd-pbh-20261115-154250-527a6d1 (refined mesh)


def make_ic(path, hole):
    from nrp_io import write_fields
    q = -LBOX/2 + (np.arange(N) + 0.5)*LBOX/N
    X, Y, Z = np.meshgrid(q, q, q, indexing="ij")
    d = [X - hole[0], Y - hole[1], Z - hole[2]]
    d = [v - LBOX*np.floor(v/LBOX + 0.5) for v in d]
    r = np.sqrt(d[0]**2 + d[1]**2 + d[2]**2)
    psi = 1.0 + 0.5/r
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_fields(path, psi, np.zeros_like(psi), psi**-2)


def deck(idfile, centre):
    b = A.Inp(os.path.join(A.ROOT, "problems/cosmo_amr/punc_box16.athinput"))
    for d in "123":
        b.set("mesh", **{f"nx{d}": N, f"x{d}min": -LBOX/2, f"x{d}max": LBOX/2,
                         f"ix{d}_bc": "periodic", f"ox{d}_bc": "periodic"})
        b.set("meshblock", **{f"nx{d}": 16})
    for k in list(b.blocks):
        if k.startswith("output") or k.startswith("refined_region") or k in (
                "mesh_refinement", "particles", "problem"):
            b.drop(k)
    b.set("time", nlim=1, tlim=10.0)
    b.set("problem", pgen_name="nrpic_cosmo", id="file", id_file=idfile, hubble=0.0)
    b.set("fastflow", find_every=1, center_x_0=centre[0], center_y_0=centre[1],
          center_z_0=centre[2], initial_radius_0=0.8)
    b.set("output1", file_type="hst", dt=1.0)
    return b


def read_summary(path):
    if not os.path.exists(path):
        return None
    a = np.loadtxt(path, ndmin=2)
    return a[-1] if len(a) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    a = ap.parse_args()
    a.out, a.new, a.rel = (os.path.abspath(v) for v in (a.out, a.new, a.rel))
    os.makedirs(a.out, exist_ok=True)
    holes = dict(centre=(0.0, 0.0, 0.0), face=(4.0, 0.0, 0.0), corner=(4.0, 4.0, 4.0))
    ics = {}
    for k, h in holes.items():
        ics[k] = os.path.join(a.out, "ic_" + k, "fields.bin")
        make_ic(ics[k], h)
    start = os.path.join(a.out, "start_dir")
    os.makedirs(start, exist_ok=True)
    spec = dict(a=("centre", (0, 0, 0)), b=("centre", (8, 0, 0)), c=("face", (4, 0, 0)),
                c2=("face", (-4, 0, 0)), d=("corner", (4, 4, 4)),
                e=("corner", (-4, -4, -4)), brel=("centre", (8, 0, 0)),
                crel=("face", (4, 0, 0)), adir=("centre", (0, 0, 0)),
                adirrel=("centre", (0, 0, 0)))
    jobs, names = [], list(spec)
    for n in names:
        ic, cen = spec[n]
        b = deck(ics[ic], [float(v) for v in cen])
        if not n.endswith("rel"):
            b.set("fastflow", diagnostics=True)
        sd = None
        if n.startswith("adir"):
            sd = os.path.join(start, n)
            os.makedirs(sd, exist_ok=True)
        jobs.append((a.rel if n.endswith("rel") else a.new, b, os.path.join(a.out, n),
                     "punc", (), sd))
    rcs = A.run_many(jobs, a.cores)
    res = {}
    for n, rc in zip(names, rcs):
        d = os.path.join(a.out, n)
        s = read_summary(os.path.join(d, "punc.horizon_summary_0.txt"))
        r = dict(exit=rc[0], wall=round(rc[1], 1), hole=spec[n][0], centre=spec[n][1],
                 summary_in_output_dir=os.path.exists(
                     os.path.join(d, "punc.horizon_summary_0.txt")))
        if n.startswith("adir"):
            sp = os.path.join(start, n, "punc.horizon_summary_0.txt")
            r["summary_in_start_dir"] = os.path.exists(sp)
            if s is None:
                s = read_summary(sp)
        if s is not None:
            r.update(mass=float(s[2]), area=float(s[7]), meanradius=float(s[10]),
                     minradius=float(s[11]), found=bool(np.isfinite(s[2])))
        else:
            r.update(found=False)
        st = os.path.join(d, "punc.horizon_status_0.txt")
        if os.path.exists(st):
            with open(st) as f:
                r["status"] = f.read().splitlines()[-1]
        res[n] = r
    ma = res["a"].get("mass", float("nan"))
    for n in names:
        if res[n].get("found"):
            res[n]["mass_rel_to_a"] = abs(res[n]["mass"]/ma - 1.0)
        print(n, {k: v for k, v in res[n].items() if k != "status"})
    res["reference"] = dict(calibration=CALIB, track_a_periodic=TRACKA,
                            a_minus_track_a=ma - TRACKA)
    with open(os.path.join(a.out, "t4_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.17, top=0.95, wspace=0.30)
    show = ["a", "b", "c", "c2", "d", "e", "brel", "crel"]
    xs = np.arange(len(show))
    for i, n in enumerate(show):
        col = fs.PAL["blue"] if n.endswith("rel") else fs.PAL["red"]
        if res[n].get("found"):
            ax[0].plot(i, res[n]["mass"], "o", color=col)
            if n != "a":
                ax[1].semilogy(i, max(res[n]["mass_rel_to_a"], 1e-17), "o", color=col)
        else:
            ax[0].plot(i, 0.9895, "x", color=col)
            ax[1].semilogy(i, 1.0, "x", color=col)
    ax[0].axhline(CALIB, **fs.GUIDE)
    ax[0].set_xticks(xs)
    ax[0].set_xticklabels(show)
    ax[0].set_ylim(0.989, 0.993)
    ax[0].set_ylabel("horizon mass (cross: none found)")
    ax[1].axhline(1e-10, **fs.GUIDE)
    ax[1].set_xticks(xs)
    ax[1].set_xticklabels(show)
    ax[1].set_ylabel(r"$|M/M_a-1|$ (cross: none found)")
    ax[1].set_ylim(1e-17, 10.0)
    fs.save(fig, os.path.join(a.out, "fig_t4_finder"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
