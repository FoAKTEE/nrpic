"""Reproduction scan of arXiv:2402.02178 with HRNA (JOURNAL entry 3): survival of the paper's
fiducial binary (main.tex:486, 504-515: m1 = 15, m2 = 10 Msun, M = 4e6 Msun, a0 = 2e4 m12, circular)
on E = 1 orbits released at BL r = 100 M in the equatorial plane (main.tex:491-502).

Scan A (Fig. InclD, main.tex:582-605): families
  pos   s = 0.9, equatorial, L_z = upper end of Eq. (Lz)        chart 'bks'
  neg   s = 0.9, equatorial, L_z = lower end of Eq. (Lz)        chart 'bks'
  zero  s = 0.9, L_z = 0 (polar)                                chart 'bks'
  s0    s = 0, equatorial                                       chart 'sch'
  s0cks s = 0, equatorial, Cartesian Kerr-Schild (the defect of entry 2, for the record)
  newt  Newtonian point mass, same binary and pericentre        law 'newton'
  r_p = 6..20 M, iota = k pi/12 (k = 0..12), nodes Omega = j pi/3 (j = 0..5) x phases l pi/4 (l = 0..3).
Scan B (Fig. afin, main.tex:524-562): s = 0.9, r_p = 10, chart 'bks', the paper's 48 x 36 cells
  (L_z from the lower to the upper end of Eq. (Lz), iota = (k + 1/2) pi/36), nodes j pi/2 x phases
  0, pi/2 (8 samples per cell).
Release: sigma_theta = +1; binary circular in the CM proper time ('gamma'); outcome at the CM's
return to r = 100 M (main.tex:610-611).

    <venv>/bin/python -I scan_2402.py <outdir> [--workers N] [--only A|B] [--smoke]
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)

FID = dict(mb=25.0 / 4e6, q12=10.0 / 15.0, a0=20000 * 25.0 / 4e6, r0=100.0)   # m2/m1 = 2/3 (member 1 = 15 Msun)
FAMILIES = {"pos": ("hrna", "bks", 0.9), "neg": ("hrna", "bks", 0.9), "zero": ("hrna", "bks", 0.9),
            "s0": ("hrna", "sch", 0.0), "s0cks": ("hrna", "cks", 0.0), "newt": ("newton", "sch", 0.0)}


def lz_of(fam, rp, spin):
    import hrna_incl as H
    lo, hi = H.lz_range(rp, spin)
    return {"pos": hi, "neg": lo, "zero": 0.0}.get(fam, hi)


def one(job):
    import hrna_incl as H
    law, coords, spin = FAMILIES[job["fam"]]
    Lz = job.get("Lz", lz_of(job["fam"], job["rp"], spin))
    t0 = time.time()
    try:
        r = H.run_incl(law, coords, spin, FID["mb"], FID["q12"], FID["a0"], job["rp"], Lz, job["iota"],
                       job["Omega"], job["phase"], FID["r0"])
        out = dict(job, Lz=Lz, survived=r["survived"], survived_coord=r["survived_coord"],
                   a_fin=r["a_fin"] if math.isfinite(r["a_fin"]) else -1.0, e_fin=r["e_fin"],
                   plunged=r["plunged"], status=r["status"], nsteps=r["nsteps"], cos_flip=r["cos_flip"],
                   r_peri=r["r_peri"], a_min=r["a_min"], wall=time.time() - t0, err="")
    except Exception as exc:                      # recorded, never silent
        out = dict(job, Lz=Lz, survived=False, survived_coord=False, a_fin=-1.0, e_fin=-1.0, plunged=-1,
                   status=-1, nsteps=0, cos_flip=0.0, r_peri=-1.0, a_min=-1.0, wall=time.time() - t0,
                   err=repr(exc))
    return out


def jobs_A(smoke=False):
    J = []
    rps = [6.0, 10.0, 14.0] if smoke else [float(r) for r in range(6, 21)]
    iotas = [k * math.pi / 12 for k in range(13)]
    nodes = [j * math.pi / 3 for j in range(6)]
    phases = [l * math.pi / 4 for l in range(4)]
    if smoke:
        iotas, nodes, phases = iotas[::4], nodes[:2], phases[:2]
    for fam in FAMILIES:
        for rp in rps:
            for io in iotas:
                for Om in nodes:
                    for ph in phases:
                        J.append(dict(scan="A", fam=fam, rp=rp, iota=io, Omega=Om, phase=ph))
    return J


def jobs_B(smoke=False):
    import hrna_incl as H
    lo, hi = H.lz_range(10.0, 0.9)
    lzs = np.linspace(lo, hi, 48)
    iotas = (np.arange(36) + 0.5) * math.pi / 36
    nodes = [j * math.pi / 2 for j in range(4)]
    phases = [0.0, math.pi / 2]
    if smoke:
        lzs, iotas, nodes, phases = lzs[::16], iotas[::12], nodes[:1], phases[:1]
    J = []
    for Lz in lzs:
        for io in iotas:
            for Om in nodes:
                for ph in phases:
                    J.append(dict(scan="B", fam="pos", rp=10.0, Lz=float(Lz), iota=float(io), Omega=Om, phase=ph))
    return J


def main(outdir, workers=1, only=None, smoke=False):
    os.makedirs(outdir, exist_ok=True)
    J = []
    if only in (None, "A"):
        J += jobs_A(smoke)
    if only in (None, "B"):
        J += jobs_B(smoke)
    # interleave so that slow families do not end up on one worker
    order = np.random.default_rng(2402).permutation(len(J))
    J = [J[i] for i in order]
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(one, J, chunksize=16))
    keys = sorted(res[0].keys())
    cols = {k: [r[k] for r in res] for k in keys}
    with open(os.path.join(outdir, "scan_2402.json"), "w") as fh:
        json.dump(dict(fiducial=FID, families={k: list(v) for k, v in FAMILIES.items()},
                       n=len(res), wall=time.time() - t0, workers=workers, columns=cols), fh)
    nerr = sum(1 for r in res if r["err"])
    print(f"{len(res)} encounters in {time.time() - t0:.0f} s on {workers} workers; errors {nerr}; "
          f"status counts {dict(zip(*np.unique([r['status'] for r in res], return_counts=True)))}")


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[a.index("--workers") + 1]) if "--workers" in a else 1
    only = a[a.index("--only") + 1] if "--only" in a else None
    out = a[0] if a and not a[0].startswith("--") else os.environ["NRPIC_RUN_DIR"]
    main(out, w, only, "--smoke" in a)
