#!/usr/bin/env python3
"""Write NRPIC initial data: particle file (.nrp), radial table (.tab) and a
JSON parameter file, for the Oppenheimer-Snyder ball, a monoenergetic
Shapiro-Teukolsky cluster, the cold prolate spheroid, or the cluster with two
Gaussian clumps of the Jeans-collapse problem.

Examples
    make_ic.py os      --N 10000 --sampler lattice --out /tmp/ic
    make_ic.py os      --N 10000 --sampler mc --seed 3 --out /tmp/ic
    make_ic.py st      --yc 0.819 --N 10000 --sampler stratified --seed 1 --out /tmp/ic
    make_ic.py st      --yc 0.605 --N 10000 --vpert 0.01 --out /tmp/ic
    make_ic.py st      --yc 0.756 --N 10000 --dpert 0.10 --out /tmp/ic
    make_ic.py prolate --e 0.9 --b 10 --N 10000 --seed 1 --out /tmp/ic
    make_ic.py jeans   --N 10000 --seed 1 --out /tmp/ic

jeans: envelope (species 0, radial table) + clumps A, B (species 1, 2, Gaussian
conformal sources), see python/nrpic/clumps.py. The table holds the envelope's
u = psi_env - 1 only (its lapse column is the isolated envelope's and is not used);
the JSON lists every component of psi_tot and the <problem> block of nrpic_cf.

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

from nrpic import clumps as clm  # noqa: E402
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
    p.add_argument("model", choices=["os", "st", "prolate", "jeans"])
    p.add_argument("--N", type=int, default=10000,
                   help="particle count (lattice: target count used to choose n_lat)")
    p.add_argument("--sampler", default=None,
                   help="os: lattice|mc|stratified (default lattice); "
                        "st, jeans: stratified|mc (default stratified); prolate: mc")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default=".", help="output directory")
    p.add_argument("--prefix", default=None, help="output file stem")
    p.add_argument("--species", type=int, default=0)
    p.add_argument("--keep-net-momentum", action="store_true",
                   help="st, jeans: keep the net momentum sum m u_i of the sample "
                        "(default: subtract the mass-weighted mean of u_i, so that "
                        "the cluster stays centred; the removed value is recorded)")
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
    D = clm.DEFAULTS
    g = p.add_argument_group("jeans (species 0 envelope, 1 clump A, 2 clump B; "
                             "--species is ignored)")
    g.add_argument("--env-mass", type=float, default=D["M_env"],
                   help="gravitational (isolated ADM) mass of the envelope")
    g.add_argument("--env-R", type=float, default=D["R_env"],
                   help="areal surface radius of the isolated envelope")
    g.add_argument("--env-yc", type=float, default=None,
                   help="select the envelope by y_c instead of --env-R")
    g.add_argument("--clump-mass", type=float, default=D["m_clump"],
                   help="conformal mass of each clump")
    g.add_argument("--clump-sigma", type=float, default=D["sigma"], help="Gaussian width")
    g.add_argument("--clump-x", type=float, default=D["d"],
                   help="clump centres at (-x, 0, 0) [A] and (+x, 0, 0) [B]")
    g.add_argument("--clump-v", type=float, default=D["v"],
                   help="bulk orthonormal speed: v^y = -v (A), +v (B)")
    g.add_argument("--split", default=":".join(str(s) for s in D["split"]),
                   help="particle-number ratio envelope:A:B")
    g.add_argument("--independent-clumps", action="store_true",
                   help="sample clump B independently instead of as the pi-rotation "
                        "image of clump A about z")
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

    elif a.model == "jeans":
        sampler = a.sampler or "stratified"
        split = tuple(int(s) for s in a.split.split(":"))
        if len(split) != 3:
            p.error("--split needs three integers, e.g. 3:1:1")
        J = clm.JeansModel(M_env=a.env_mass, R_env=a.env_R, yc=a.env_yc,
                           m_clump=a.clump_mass, sigma=a.clump_sigma, d=a.clump_x,
                           v=a.clump_v)
        mirror = not a.independent_clumps
        x, u, m, sp = J.sample(a.N, a.seed, sampler, split, mirror)
        stem = a.prefix or f"jeans_N{a.N}_s{a.seed}"
        tabname = stem + ".tab"
        meta.pop("species")
        meta.update(J.summary())
        meta.update(sampler=sampler, split=list(split), clump_B_mirror_of_A=mirror)
        n_env, n_a, n_b = clm.split_counts(a.N, split)
        comps = [dict(name="envelope", species=0, type="table", file=tabname,
                      center=[0.0, 0.0, 0.0], mass=J.M_env, N=n_env)]
        for k, (name, n) in enumerate((("clump_A", n_a), ("clump_B", n_b))):
            comps.append(dict(name=name, species=k + 1, type="gaussian", mass=J.m_c,
                              sigma=J.sigma, center=[float(c) for c in J.centres[k + 1]],
                              velocity=[float(c) for c in J.velocities[k]],
                              W=J.W, N=n))
        meta["components"] = comps
        meta["psi_tot_definition"] = (
            "psi_tot = 1 + sum_k u_k(|x - center_k|); table: u from the radial table "
            "(continued as M/(2r), M = 2 r_N u_N); gaussian: "
            "u = (mass/2) erf(r/(sqrt(2) sigma))/r")
        prob = dict(pgen_name="nrpic_cf", ncomp=len(comps))
        for c, comp in enumerate(comps):
            pre = f"comp{c}_"
            prob[pre + "type"] = comp["type"]
            if comp["type"] == "table":
                prob[pre + "file"] = comp["file"]
            else:
                prob[pre + "mass"] = comp["mass"]
                prob[pre + "sigma"] = comp["sigma"]
            prob[pre + "x1"], prob[pre + "x2"], prob[pre + "x3"] = comp["center"]
        prob["lapse"] = "isotropic"
        meta["athenak"] = {"problem": prob,
                           "particles": {"particle_file": stem + ".nrp"}}
        meta["particles_by_species"] = J.particle_summary(x, u, m, sp)
        table = lambda path: stc.write_table(J.env, path, a.table_points, a.table_rmax)
        meta["table_lapse"] = ("isolated-envelope static lapse; not used (initial lapse "
                               "(2 - psi_tot)/psi_tot, <problem> lapse = isotropic)")

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

    if a.model in ("st", "jeans") and not a.keep_net_momentum:
        ubar = (m[:, None] * u).sum(0) / m.sum()
        u = u - ubar
        meta["net_momentum_removed"] = dict(
            mean_u=[float(v) for v in ubar],
            note="u_i -> u_i - sum(m u_i)/sum(m); sum m u_i = 0 afterwards")
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
    elif a.model == "jeans":
        e, cl = meta["envelope"], meta["clumps"]
        print(f"  envelope: yc = {e['yc']:.10g}, M_env = {e['M_env']:.6g}, "
              f"R = {e['R_areal']:.8g}, rbar_s = {e['rbar_s']:.8g}, M0 = {e['M0']:.10g}")
        print(f"  psi_tot(0) = {meta['psi_tot']['origin']:.10g}, "
              f"psi_tot(x_A) = {meta['psi_tot']['x_A']:.10g}, "
              f"lapse(0) = {meta['lapse_isotropic']['origin']:.10g}")
        cc = cl["circular_speed_check"]
        print(f"  clumps: v = {cl['v_A'][1]:+.6f}/{cl['v_B'][1]:+.6f}, "
              f"Newtonian v_circ = {cc['v_circ']:.6f}")
        for k in ("envelope", "clump_A", "clump_B", "total"):
            s = meta["particles_by_species"][k]
            c = meta["continuum"][k]
            print(f"  {k:9s} N = {s['N']:7d}  sum m = {s['sum_m']:.8f} "
                  f"(cont. {c['rest_mass']:.8f})  sum mW = {s['sum_mW']:.8f} "
                  f"(cont. {c['sum_mW']:.8f})")
    else:
        keys = ("M_rest", "rbar0", "R0_areal") if a.model == "os" else \
               ("yc", "M0", "R_areal", "rbar_s", "zc", "alpha_c", "Eb_over_M0")
        print("  " + ", ".join(f"{k} = {meta[k]:.10g}" for k in keys))
    print(f"  N = {len(m)}, sum m = {m.sum():.10g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
