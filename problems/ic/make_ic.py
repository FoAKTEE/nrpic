#!/usr/bin/env python3
"""Write NRPIC initial data: particle file (.nrp), radial table (.tab) and a
JSON parameter file, for the Oppenheimer-Snyder ball, a monoenergetic
Shapiro-Teukolsky cluster, or the cold prolate spheroid.

Examples
    make_ic.py os      --N 10000 --sampler lattice --out /tmp/ic
    make_ic.py os      --N 10000 --sampler mc --seed 3 --out /tmp/ic
    make_ic.py st      --yc 0.819 --N 10000 --sampler stratified --seed 1 --out /tmp/ic
    make_ic.py st      --yc 0.605 --N 10000 --vpert 0.01 --out /tmp/ic
    make_ic.py st      --yc 0.756 --N 10000 --dpert 0.10 --out /tmp/ic
    make_ic.py prolate --e 0.9 --b 10 --N 10000 --seed 1 --out /tmp/ic

File formats: docs/FORMATS.md. Units: G = c = 1, ADM mass M = 1.
"""

import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402

from nrpic import io as nio  # noqa: E402
from nrpic import oppenheimer_snyder as osn  # noqa: E402
from nrpic import sampling  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
from nrpic.spheroid import ProlateSpheroid  # noqa: E402


def _fmt(v):
    return f"{v:g}".replace(".", "p").replace("-", "m")


def _particle_stats(x, u, m):
    r = np.sqrt(np.sum(x * x, axis=1))
    return dict(N=int(len(m)), sum_m=float(m.sum()), m_min=float(m.min()),
                m_max=float(m.max()), r_max=float(r.max()),
                com=[float(v) for v in (m[:, None] * x).sum(0) / m.sum()],
                sum_m_u=[float(v) for v in (m[:, None] * u).sum(0)])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model", choices=["os", "st", "prolate"])
    p.add_argument("--N", type=int, default=10000,
                   help="particle count (lattice: target count used to choose n_lat)")
    p.add_argument("--sampler", default=None,
                   help="os: lattice|mc|stratified (default lattice); "
                        "st: stratified|mc (default stratified); prolate: mc")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default=".", help="output directory")
    p.add_argument("--prefix", default=None, help="output file stem")
    p.add_argument("--species", type=int, default=0)
    p.add_argument("--table-points", type=int, default=4000,
                   help="table rows across the matter (dr = rbar_s/table_points)")
    p.add_argument("--table-rmax", type=float, default=1.5,
                   help="table extent in units of the isotropic surface radius")
    g = p.add_argument_group("os")
    g.add_argument("--R0", type=float, default=5.0, help="initial areal radius / M")
    g.add_argument("--nlat", type=int, default=None, help="lattice cells across the diameter")
    g.add_argument("--normalize-lattice-mass", action="store_true")
    g = p.add_argument_group("st")
    g.add_argument("--yc", type=float, default=None, help="central y_c of the sequence")
    g.add_argument("--vpert", type=float, default=0.0,
                   help="inward radial velocity perturbation, fraction of local speed")
    g.add_argument("--vpert-profile", choices=["uniform", "linear"], default="uniform")
    g.add_argument("--dpert", type=float, default=0.0,
                   help="density perturbation (homologous compression by (1+dpert)^(-1/3))")
    g = p.add_argument_group("prolate")
    g.add_argument("--e", type=float, default=0.9, help="eccentricity")
    g.add_argument("--b", type=float, default=10.0, help="polar semi-axis / M")
    g.add_argument("--no-symmetrize", action="store_true")
    a = p.parse_args(argv)

    os.makedirs(a.out, exist_ok=True)
    meta = dict(format="NRPIC001", units="G=c=1, M_ADM=1", seed=a.seed,
                species=a.species, generator="problems/ic/make_ic.py",
                argv=sys.argv[1:] if argv is None else list(argv))
    table = None

    if a.model == "os":
        sampler = a.sampler or "lattice"
        x, u, m, sp = sampling.sample_os(a.N, sampler, a.seed, a.R0, 1.0, a.nlat,
                                         a.species, a.normalize_lattice_mass)
        meta.update(osn.summary(a.R0))
        meta["sampler"] = sampler
        if sampler == "lattice":
            nlat = a.nlat or sampling.os_nlat_for(a.N)
            meta.update(n_lat=nlat, lattice_h=2 * osn.isotropic_radius(a.R0) / nlat,
                        lattice_convention="cell centres -rbar0+(i+1/2)h, |x|<=rbar0")
        stem = a.prefix or f"os_R{_fmt(a.R0)}_{sampler}_N{len(m)}_s{a.seed}"
        table = lambda path: osn.write_table(path, a.R0, 1.0, a.table_points, a.table_rmax)
        meta["table_lapse"] = "alpha = 1 (initial lapse); do not use tabulated-lapse continuation"

    elif a.model == "st":
        if a.yc is None:
            p.error("st needs --yc")
        sampler = a.sampler or "stratified"
        model = stc.STModel(a.yc)
        x, u, m, sp = sampling.sample_st(model, a.N, sampler, a.seed, a.vpert,
                                         a.vpert_profile, a.dpert, a.species)
        meta.update(model.summary())
        meta.update(sampler=sampler, vpert=a.vpert, vpert_profile=a.vpert_profile,
                    dpert=a.dpert)
        stem = a.prefix
        if stem is None:
            stem = f"st_yc{_fmt(a.yc)}_{sampler}_N{a.N}_s{a.seed}"
            if a.vpert:
                stem += f"_vp{_fmt(a.vpert)}"
            if a.dpert:
                stem += f"_dp{_fmt(a.dpert)}"
        table = lambda path: stc.write_table(model, path, a.table_points, a.table_rmax)
        meta["table_lapse"] = "static equilibrium lapse; Schwarzschild continuation outside"

    else:
        sym = not a.no_symmetrize
        N = a.N - a.N % 4 if sym else a.N
        if N != a.N:
            print(f"note: N rounded down to {N} (multiple of 4 for the symmetrization)")
        sph = ProlateSpheroid(a.e, a.b)
        x, u, m, sp = sampling.sample_spheroid(N, seed=a.seed, symmetrize=sym,
                                               species=a.species, spheroid=sph)
        meta.update(sph.summary())
        meta.update(sampler="mc", symmetrize=sym)
        stem = a.prefix or f"prolate_e{_fmt(a.e)}_b{_fmt(a.b)}_N{N}_s{a.seed}"

    nrp = os.path.join(a.out, stem + ".nrp")
    nio.write_nrp(nrp, x, u, m, sp)
    meta["particle_file"] = os.path.basename(nrp)
    meta["particles"] = _particle_stats(x, u, m)
    if table is not None:
        tab = os.path.join(a.out, stem + ".tab")
        r, uu, al = table(tab)
        meta["table_file"] = os.path.basename(tab)
        meta["table"] = dict(rows=int(len(r)), dr=float(r[1] - r[0]), r_max=float(r[-1]),
                             M_from_last_row=float(2 * r[-1] * uu[-1]))
    js = os.path.join(a.out, stem + ".json")
    with open(js, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"wrote {nrp}" + (f", {tab}" if table is not None else "") + f", {js}")
    if a.model == "prolate":
        print("spheroid parameters (no table; the generator evaluates psibar = 1 - Phi_N):")
        for k in ("e", "a", "b", "c_focal", "rhoN", "M_rest", "psibar_c", "I0", "Ja0", "Jb0"):
            print(f"  {k:9s} = {meta[k]!r}")
        print(f"  inside: psibar = c0 - cR (x^2+y^2) - cz z^2, {meta['psibar_coeffs_inside']}")
    else:
        keys = ("M_rest", "rbar0", "R0_areal") if a.model == "os" else \
               ("yc", "M0", "R_areal", "rbar_s", "zc", "alpha_c", "Eb_over_M0")
        print("  " + ", ".join(f"{k} = {meta[k]:.10g}" for k in keys))
    print(f"  N = {len(m)}, sum m = {m.sum():.10g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
