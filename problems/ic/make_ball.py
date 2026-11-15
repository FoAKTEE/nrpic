#!/usr/bin/env python3
"""Write initial data of the expanding dust ball (python/nrpic/expanding_ball.py): a
radial table of format 2 with the extrinsic curvature (.tab), the particle file (.nrp)
and a JSON parameter file.

Examples
    make_ball.py --Rb 10 --h 0.5 --out /tmp/ic                # marginally bound, sharp
    make_ball.py --Rb 10 --edge 2 --h 0.5 --out /tmp/ic       # smooth edge, half-width 2
    make_ball.py --Rb 5 --e0 0.16 --RE 10 --h 0.25 --out /tmp/ic   # bound, turns around

The particles are dust at rest in the slice (u_i = 0) on the cubic lattice of spacing
h with sites (k + 1/2) h: with a mesh whose cell size is a multiple of h and which has a
cell boundary at the origin, the sites are symmetric about the cell centres.  With
--shift the lattice is displaced by that fraction of h along the three axes (a lattice
that does not match the mesh).

Order of the particles in the file (the tag of a particle is its position): first the
exterior tracers (--tracers, rest mass 1e-30 each, at rest in the slice at the given
multiples of the outer radius along 26 directions), then a random sample of --sample
ball particles, then the others.  With <particles> traj_ntrack = n_tracers + n_sample
the tracers and the sample are written to the trajectory files.

File formats: docs/FORMATS.md.  Units: G = c = 1.
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
from nrpic import expanding_ball as eb  # noqa: E402


def _fmt(v):
    return f"{v:g}".replace(".", "p").replace("-", "m")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--M", type=float, default=1.0, help="mass scale (total mass if edge = 0)")
    p.add_argument("--Rb", type=float, default=10.0, help="areal radius of the surface")
    p.add_argument("--e0", type=float, default=0.0,
                   help="binding, E = -e0 (R/Rb)^2 inside (0: marginally bound)")
    p.add_argument("--RE", type=float, default=None,
                   help="areal radius beyond which the vacuum slice has E = 0 (e0 > 0)")
    p.add_argument("--edge", type=float, default=0.0,
                   help="half-width of the smooth edge of the density (e0 = 0)")
    p.add_argument("--h", type=float, required=True, help="lattice spacing")
    p.add_argument("--shift", type=float, default=0.0,
                   help="displacement of the lattice in units of h (0: sites (k+1/2) h)")
    p.add_argument("--mass-rule", default=None, choices=["volume", "surface", "normalize"],
                   help="default: surface for a sharp surface, volume for a smooth edge")
    p.add_argument("--tracers", default="1.25,1.5,2.0",
                   help="multiples of the outer radius for the exterior tracers ('' for none)")
    p.add_argument("--sample", type=int, default=2000,
                   help="number of ball particles placed first for the trajectory files")
    p.add_argument("--seed", type=int, default=1, help="seed of the sample")
    p.add_argument("--table-points", type=int, default=4000, help="rows across the matter")
    p.add_argument("--table-rmax", type=float, default=1.25,
                   help="table extent in units of the outer radius of the matter")
    p.add_argument("--out", default=".", help="output directory")
    p.add_argument("--prefix", default=None, help="output file stem")
    a = p.parse_args(argv)

    ball = eb.Ball(M=a.M, Rb=a.Rb, e0=a.e0, RE=a.RE, edge=a.edge)
    rule = a.mass_rule or ("volume" if a.edge > 0.0 else "surface")
    x, u, m = ball.lattice(a.h, rule, a.shift)
    nball = len(m)
    rng = np.random.default_rng(a.seed)
    ns = min(a.sample, nball)
    perm = rng.permutation(nball)
    order = np.concatenate([np.sort(perm[:ns]), np.sort(perm[ns:])])
    x, u, m = x[order], u[order], m[order]
    factors = [float(t) for t in a.tracers.split(",") if t.strip()]
    nt = 0
    if factors:
        xt, ut, mt = ball.tracers(factors)
        nt = len(mt)
        x, u, m = np.concatenate([xt, x]), np.concatenate([ut, u]), np.concatenate([mt, m])

    stem = a.prefix
    if stem is None:
        stem = f"ball_Rb{_fmt(a.Rb)}"
        if a.e0:
            stem += f"_e{_fmt(a.e0)}"
        if a.edge:
            stem += f"_w{_fmt(a.edge)}"
        stem += f"_h{_fmt(a.h)}"
        if a.shift:
            stem += f"_s{_fmt(a.shift)}"
    os.makedirs(a.out, exist_ok=True)
    table = ball.write_table(os.path.join(a.out, stem + ".tab"), a.table_points, a.table_rmax)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), x, u, m)

    res = eb.residuals_1d(table, lambda rb: ball.density(ball.areal(rb)))
    mb = m[nt:]
    meta = dict(format="NRPIC001", table_format=2, units="G=c=1",
                generator="problems/ic/make_ball.py",
                argv=sys.argv[1:] if argv is None else list(argv))
    meta.update(ball.summary())
    meta.update(lattice_h=a.h, lattice_shift=a.shift, mass_rule=rule,
                lattice_convention="sites (k + 1/2 + shift) h, |x| <= rbar_out",
                n_tracers=nt, tracer_factors=factors, n_sample=ns,
                traj_ntrack=nt + ns, seed=a.seed,
                particle_file=stem + ".nrp", table_file=stem + ".tab",
                table=dict(rows=int(len(table.rbar)), drbar=table.dr, rmax=table.rlast,
                           breaks=list(table.breaks), exterior=table.exterior,
                           offline_check=dict(max_abs_H=float(np.max(np.abs(res["H"]))),
                                              max_abs_M=float(np.max(np.abs(res["M"]))),
                                              rule="fourth-order differences of the rows "
                                                   "(nrpic.expanding_ball.residuals_1d)")),
                particles=dict(N=int(len(m)), N_ball=int(nball), sum_m=float(mb.sum()),
                               sum_m_over_rest_mass=float(mb.sum() / ball.rest_mass()),
                               m_min=float(mb.min()), m_max=float(mb.max()),
                               r_max=float(np.sqrt(np.sum(x[nt:] ** 2, axis=1)).max())),
                problem_block=dict(pgen_name="nrpic_cf", ncomp=1, comp0_type="table",
                                   comp0_file=stem + ".tab", lapse="table", lapse_comp=0,
                                   shift="zero or table"))
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print(f"wrote {stem}.tab, {stem}.nrp, {stem}.json in {a.out}")
    print(f"  M_total = {meta['M_total']:.10g}, H = {ball.H:.10g}, H Rb = {ball.H * ball.Rb:.6g}, "
          f"rbar_out = {ball.rbar_out:.10g}")
    print(f"  N = {len(m)} ({nt} tracers, {ns} sample), sum m / rest mass = "
          f"{meta['particles']['sum_m_over_rest_mass']:.10f}, mass rule {rule}")
    print(f"  table: {len(table.rbar)} rows, breaks {list(table.breaks)}, offline check "
          f"max|H| = {meta['table']['offline_check']['max_abs_H']:.2e}, "
          f"max|M| = {meta['table']['offline_check']['max_abs_M']:.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
