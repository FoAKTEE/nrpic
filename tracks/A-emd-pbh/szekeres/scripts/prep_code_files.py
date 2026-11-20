"""Files for AthenaK runs of the Szekeres hole (card series and particle-number check).

For each N: the field file (NRCOSMO1) of `nrpic_cosmo id = file` and the particle file of
the slice t = t_i of the reference model on [-8, 8]^3, written into $NRPIC_RUN_DIR/N<N>/
(or N<N>_ppc<p>/), plus the labels of every cell for the analysis (slice_t0.npz: r, bn,
psi, rho at the cell centres, float64, and r_ltb, the label of the LTB slice with the same
M, k at the same cell, for the size of the non-spherical signal). The map is evaluated in
parallel (--workers).

Particles (--ppc): 1 = one particle per cell centre (codeid.py; with the cloud-in-cell
deposit the code's E equals rho at every cell); 8 = a lattice of spacing h/2 (offsets
+-h/4 from the centre in each direction), m = rho psi^6 (h/2)^3 at the particle. For
ppc = 8 the deposit is not exact: the cloud-in-cell weights 3/4 and 1/4 in each direction
give the cell mass sum_p m_p w_p, which this script also computes (`mass_dep` in
slice_t0.npz, and E_dep = mass_dep/(h^3 psi^6) against rho) so that the prediction of the
code's E at tau = 0 is on record before the run.

    python3 scripts/prep_code_files.py --N 64 128 256 [--ppc 1] [--eps 0.1] [--workers 6]
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402
from szekeres import codeid  # noqa: E402

LH = 8.0
KEYS = ("psi", "rho", "KL", "KT", "r", "bn")
_CM = {}


def _cm(eps):
    if eps not in _CM:
        ltb, szk = common.models(eps=eps if eps > 0 else common.EPS)
        _CM[eps] = ConformalMap(szk if eps > 0 else ltb)
    return _CM[eps]


def _eval(args):
    eps, pts = args
    f = _cm(eps).fields(pts)
    out = {k: f[k] for k in KEYS}
    out["N"] = f["N"]
    return out


def fields_on(points_1d, eps, workers, chunk=1 << 17):
    """Fields at the tensor grid points_1d^3, arrays [i, j, k]."""
    n = len(points_1d)
    X, Y, Z = np.meshgrid(points_1d, points_1d, points_1d, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    del X, Y, Z
    parts = [pts[s:s + chunk] for s in range(0, len(pts), chunk)]
    out = {k: np.empty(len(pts)) for k in KEYS}
    out["N"] = np.empty((len(pts), 3))
    with ProcessPoolExecutor(workers, mp_context=mp.get_context("fork")) as ex:
        s = 0
        for res in ex.map(_eval, [(eps, p) for p in parts]):
            m = len(res["psi"])
            for k in KEYS:
                out[k][s:s + m] = res[k]
            out["N"][s:s + m] = res["N"]
            s += m
    sh = (n, n, n)
    res = {k: out[k].reshape(sh) for k in KEYS}
    res["N"] = out["N"].reshape(sh + (3,))
    return res


def cic_8ppc_cell_mass(m_sub):
    """Cell masses from the h/2 sub-lattice (2N)^3 deposited with cloud-in-cell on the N^3
    cells (periodic): in each direction a sub-particle at offset -h/4 (+h/4) from its cell
    centre gives 3/4 to its cell and 1/4 to the cell below (above)."""
    a = m_sub
    for ax in range(3):
        a = np.moveaxis(a, ax, 0)
        lo, hi = a[0::2], a[1::2]           # offsets -h/4, +h/4 of cell i
        c = 0.75 * (lo + hi) + 0.25 * (np.roll(hi, 1, axis=0) + np.roll(lo, -1, axis=0))
        a = np.moveaxis(c, 0, ax)
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, nargs="+", required=True)
    ap.add_argument("--ppc", type=int, default=1, choices=(1, 8))
    ap.add_argument("--eps", type=float, default=0.2)   # production choice, JOURNAL entry 7
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    rdir = common.run_dir("prep_code_files")
    summary = dict(run_id=common.run_id(), commit=common.git_commit(), eps=a.eps, ppc=a.ppc, LH=LH, members={})
    for N in a.N:
        t0 = time.time()
        tag = f"N{N}" if a.ppc == 1 else f"N{N}_ppc{a.ppc}"
        d = os.path.join(rdir, tag)
        os.makedirs(d, exist_ok=True)
        c, h = codeid.cell_centres(N, LH)
        f = fields_on(c, a.eps, a.workers)
        f["x"], f["h"] = c, h
        r_ltb = fields_on(c, 0.0, a.workers)["r"]     # labels of the LTB slice (eps = 0) at the same cells
        codeid.write_nrcosmo(os.path.join(d, "fields.bin"), f)
        info = dict(N=N, h=h, cells=N ** 3)
        if a.ppc == 1:
            npart = codeid.write_particles(os.path.join(d, "particles.nrp"), f)
            mass_dep = (f["rho"] * f["psi"] ** 6) * h ** 3
        else:
            cs = -LH + (np.arange(2 * N) + 0.5) * (h / 2)
            g = fields_on(cs, a.eps, a.workers)
            m_sub = g["rho"] * g["psi"] ** 6 * (h / 2) ** 3
            X, Y, Z = np.meshgrid(cs, cs, cs, indexing="ij")
            x = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
            del X, Y, Z
            import importlib.util
            spec = importlib.util.spec_from_file_location("nrpic_io", os.path.join(common.ROOT, "python", "nrpic", "io.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.write_nrp(os.path.join(d, "particles.nrp"), x, np.zeros_like(x), m_sub.ravel())
            npart = len(x)
            mass_dep = cic_8ppc_cell_mass(m_sub)
            del g, x
        E_dep = mass_dep / (h ** 3 * f["psi"] ** 6)
        rel = (E_dep - f["rho"]) / f["rho"]
        regions = {"core": f["r"] < common.PROFILE[1],
                   "shell": (f["r"] >= common.PROFILE[1]) & (f["r"] <= common.PROFILE[2]),
                   "outside": f["r"] > common.PROFILE[2]}
        info.update(particles=int(npart), mass_total=float(mass_dep.sum()),
                    predicted_E0_rel_err={k: dict(max=float(np.max(np.abs(rel[m]))), rms=float(np.sqrt(np.mean(rel[m] ** 2))))
                                          for k, m in regions.items()},
                    rho_over_rhob=[float(f["rho"].min() / common.models(eps=a.eps)[1].rho_b),
                                   float(f["rho"].max() / common.models(eps=a.eps)[1].rho_b)],
                    wall_s=time.time() - t0)
        np.savez(os.path.join(d, "slice_t0.npz"), r=f["r"], bn=f["bn"], psi=f["psi"], rho=f["rho"],
                 E_dep=E_dep, r_ltb=r_ltb, x=c, h=h, eps=a.eps)
        sizes = {fn: os.path.getsize(os.path.join(d, fn)) for fn in ("fields.bin", "particles.nrp", "slice_t0.npz")}
        info["bytes"] = sizes
        summary["members"][tag] = info
        print(tag, json.dumps(info), flush=True)
    common.dump(os.path.join(rdir, f"prep_ppc{a.ppc}.json"), summary)
    print("written", rdir)


if __name__ == "__main__":
    main()
