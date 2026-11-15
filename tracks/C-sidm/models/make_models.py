#!/usr/bin/env python3
"""Build the particle models of model_set.py with the generator chain of the equilibria
package: tracks/C-sidm/equilibria/make_equilibria.build (sampler, table, particle file,
JSON, formats of docs/FORMATS.md, conventions of problems/ic/make_ic.py), driven with the
solver evstatic_b.py and the families of model_set.py instead of evstatic.py and
models.py. Nothing in equilibria/ is edited; the two module references of
make_equilibria are rebound here (make_equilibria.ev, make_equilibria.models).

    python3 make_models.py [--out DIR] [--N 10000] [--seed 1] [--only TAG|FAMILY ...]

Per model: <tag>_stratified_N<N>_s<seed>.{nrp,tab,json}; the JSON gets, besides the fields
of make_equilibria, the driver, b and w0 (F21 family), and the resolution numbers of the
centre (macroparticle spacing, macroparticles per cell of M/4 and M/8, macroparticles
inside the core radius where n = n_c/2). DIR/index.json lists the models.
"""

import argparse
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "equilibria"))

import numpy as np  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

import evstatic_b as evb  # noqa: E402
import model_set as ms  # noqa: E402
import make_equilibria as me  # noqa: E402  (equilibria's generator)

me.ev = evb          # solver with the b family (King lines unchanged, b = 1.0)
me.models = ms       # FAMILIES of this package


def centre_resolution(md, N):
    """Macroparticle resolution at the centre of model `md` with N equal masses."""
    s = md.summary()
    n_c = s["n_c"]                         # rest-mass density at the centre (M units)
    psi_c = s["psi_c"]
    per_mass = N / md.M0                   # macroparticles per unit rest mass
    nd = per_mass * n_c                    # macroparticles per unit proper volume
    out = dict(n_c=n_c, psi_c=psi_c, spacing_proper=nd ** (-1.0 / 3.0),
               per_cell_dx_M_over_4=nd * psi_c ** 6 * 0.25 ** 3,
               per_cell_dx_M_over_8=nd * psi_c ** 6 * 0.125 ** 3)
    # areal radius where n = n_c/2, and the macroparticles inside it
    f = lambda r: md.matter_areal(np.array([r]), ("n",))["n"][0] - 0.5 * n_c
    r_core = brentq(f, 1e-6 * md.R, md.R * (1 - 1e-9), xtol=1e-12)
    out.update(r_core_areal=r_core, rbar_core=float(md.rbar_of(r_core)[0]),
               N_inside_core=float(N * md.enclosed_fraction_areal(r_core)[0]),
               mass_fraction_inside_core=float(md.enclosed_fraction_areal(r_core)[0]))
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    p.add_argument("--N", type=int, default=10000)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--sampler", default="stratified", choices=["stratified", "mc"])
    p.add_argument("--only", nargs="*", default=None)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    index = []
    for spec in ms.model_set():
        if a.only and spec["tag"] not in a.only and spec["family"] not in a.only:
            continue
        t0 = time.time()
        stem, meta = me.build(spec, a.out, a.N, a.seed, a.sampler)
        md = evb.Equilibrium(ms.FAMILIES[spec["family"]], spec["y0"])
        meta["driver"] = "tracks/C-sidm/models/make_models.py (equilibria/make_equilibria.build " \
                         "with evstatic_b and model_set)"
        fam = ms.FAMILIES[spec["family"]]
        meta["b"] = fam.b
        if fam.kind == "tmb":
            meta["w0_F21"] = ms.w0_of_y0(spec["y0"], fam.b)
        meta["centre_resolution"] = centre_resolution(md, a.N)
        with open(os.path.join(a.out, stem + ".json"), "w") as f:
            json.dump(meta, f, indent=2)
        cr = meta["centre_resolution"]
        index.append(dict(stem=stem, family=spec["family"], y0=spec["y0"], role=spec["role"],
                          b=fam.b, w0_F21=meta.get("w0_F21"),
                          Eb=meta["Eb_over_M0"], Zc=meta["Zc_infinity"],
                          zc_boundary=meta["zc_boundary"], R=meta["R_areal"],
                          rbar_s=meta["rbar_s"], M0=meta["M0"], alpha_c=meta["alpha_c"],
                          psi_c=meta["psi_c"],
                          sum_m_W_over_psi_rel=meta["table_constraint"]["rel_diff"],
                          centre_resolution=cr, seconds=round(time.time() - t0, 2)))
        print(f"{stem}: Eb = {meta['Eb_over_M0']:.6f}, Z_c = {meta['Zc_infinity']:.5f}, "
              f"R = {meta['R_areal']:.4f} M, rbar_s = {meta['rbar_s']:.4f} M, "
              f"sum mW/psi - 1 = {meta['table_constraint']['rel_diff']:+.2e}, "
              f"spacing_c = {cr['spacing_proper']:.3f} M, per M/4 cell {cr['per_cell_dx_M_over_4']:.1f}, "
              f"N(r < r_core) = {cr['N_inside_core']:.0f} ({index[-1]['seconds']} s)", flush=True)
    with open(os.path.join(a.out, "index.json"), "w") as f:
        json.dump(dict(N=a.N, seed=a.seed, sampler=a.sampler, models=index), f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
