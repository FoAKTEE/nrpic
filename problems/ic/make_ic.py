#!/usr/bin/env python3
"""Write NRPIC initial data: particle file (.nrp), radial table (.tab) and a
JSON parameter file, for the Oppenheimer-Snyder ball, a monoenergetic
Shapiro-Teukolsky cluster, the cold prolate spheroid, the cluster with two
Gaussian clumps of the Jeans-collapse problem, isolated Gaussian clumps with
momentum and spin, or equilibrium clusters with a bulk velocity.

Examples
    make_ic.py os      --N 10000 --sampler lattice --out /tmp/ic
    make_ic.py os      --N 10000 --sampler mc --seed 3 --out /tmp/ic
    make_ic.py st      --yc 0.819 --N 10000 --sampler stratified --seed 1 --out /tmp/ic
    make_ic.py st      --yc 0.605 --N 10000 --vpert 0.01 --out /tmp/ic
    make_ic.py st      --yc 0.756 --N 10000 --dpert 0.10 --out /tmp/ic
    make_ic.py st      --yc 0.756 --N 10000 --dpert 0.10 --no-consistent-table --out /tmp/ic
    make_ic.py prolate --e 0.9 --b 10 --N 10000 --seed 1 --out /tmp/ic
    make_ic.py jeans   --N 10000 --seed 1 --out /tmp/ic
    make_ic.py jeans   --N 10000 --seed 1 --clump-curvature --out /tmp/ic
    make_ic.py clumps  --gaussian 0.2,1,0,0,0,0.06,0,0 --N 100000 --out /tmp/ic
    make_ic.py clumps  --gaussian 0.05,0.3,-1.5,0,0,0,0.01,0 \
                       --gaussian 0.05,0.3,1.5,0,0,0,-0.01,0 \
                       --puncture 1,0,-25,0,0.02,0,0 --N 20000 --out /tmp/ic
    make_ic.py boosted --cluster 0.819,1,0,0,0,0.3,0,0 --N 10000 --seed 1 --out /tmp/ic
    make_ic.py boosted --cluster 0.819,1,-20,0,0,0,-0.08,0 \
                       --cluster 0.819,1,20,0,0,0,0.08,0 --N 10000 --out /tmp/ic

jeans: envelope (species 0, radial table) + clumps A, B (species 1, 2, Gaussian
conformal sources), see python/nrpic/clumps.py. The table holds the envelope's
u = psi_env - 1 only (its lapse column is the isolated envelope's and is not used);
the JSON lists every component of psi_tot and the <problem> block of nrpic_cf.
--clump-curvature adds the clumps' momenta (comp<c>_p1..3: the problem generator then
adds the smeared Bowen-York curvature that solves the momentum constraint for them);
--clump-momentum-rule gaussian makes every clump particle carry an equal share of the
clump's momentum, so that the momentum density is the Gaussian the curvature solves
for (python/nrpic/clumps.py).

clumps: isolated Gaussian clumps, each "mass,sigma,x,y,z,px,py,pz[,sx,sy,sz]" with
momentum P and spin S, and optional punctures "mass,x,y,z[,px,py,pz[,sx,sy,sz]]"
(python/nrpic/clumps.GaussianClumps); --N particles per clump; species = index of
the clump. --sampler lattice puts weighted particles on a lattice of spacing
--lattice-h (noise-free deposit, for tests).

boosted: equilibrium clusters (monoenergetic model y_c, ADM mass of the isolated
cluster) that move, each "yc,mass,x,y,z,vx,vy,vz" with the speed v of the clump
(--cluster-p: with its momentum instead; clusters given by momentum come after those
given by velocity), and optional punctures (python/nrpic/boosted_cluster.py): the static cluster on the maximal
slice of its boosted spacetime. Written per cluster k: <stem>_c<k>.tab (radial table),
<stem>_c<k>.bst (boost table: moments of the momentum density for the curvature, and
the comoving shift), <stem>_c<k>_corr.tab (second-order correction of psi; not with
--no-psi-correction); the JSON holds the <problem> block of nrpic_cf. --N particles per
cluster, species = index of the cluster; --sampler stratified|mc|quiet (quiet: weighted
lattice of spacing --lattice-h with six momenta per site, for tests). --boost-shift
asks for the comoving shift at the start.

st with --dpert/--vpert: by default the table solves the Hamiltonian constraint
for the perturbed particles (nrpic.st_cluster.PerturbedST; stem suffix '_hc'),
its ADM mass M' differs slightly from 1 and is in the JSON (table_constraint);
--no-consistent-table writes the unperturbed equilibrium table as before.

File formats: docs/FORMATS.md. Units: G = c = 1, ADM mass M = 1 (of the
unperturbed model for st).
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

from nrpic import boosted_cluster as bcl  # noqa: E402
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
    p.add_argument("model", choices=["os", "st", "prolate", "jeans", "clumps",
                                     "boosted"])
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
    g.add_argument("--lattice-surface-correction", action="store_true",
                   help="lattice: rescale the masses of the outermost layer (one lattice "
                        "spacing) so that the total equals the continuum rest mass; the "
                        "published rule m = rho_0 psi^6 h^3 is off by the lattice-count "
                        "error of the sphere (+1.2 percent at n_lat = 26)")
    g = p.add_argument_group("st")
    g.add_argument("--yc", type=float, default=None, help="central y_c of the sequence")
    g.add_argument("--vpert", type=float, default=0.0,
                   help="inward radial velocity perturbation, fraction of local speed")
    g.add_argument("--vpert-profile", choices=["uniform", "linear"], default="uniform")
    g.add_argument("--dpert", type=float, default=0.0,
                   help="density perturbation (homologous compression by (1+dpert)^(-1/3))")
    g.add_argument("--consistent-table", action=argparse.BooleanOptionalAction, default=True,
                   help="with --dpert/--vpert: write the table (psi and lapse) that solves "
                        "the Hamiltonian constraint for the perturbed matter "
                        "(stc.PerturbedST; file stem gets the suffix '_hc'). "
                        "--no-consistent-table writes the unperturbed equilibrium table "
                        "(old behaviour, violates the constraint)")
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
    g.add_argument("--clump-curvature", action="store_true",
                   help="write the clumps' momenta sum m u_i into the <problem> block "
                        "(comp<c>_p1..3): smeared Bowen-York curvature in nrpic_cf")
    g.add_argument("--clump-momentum-rule", choices=["velocity", "gaussian"],
                   default=None,
                   help="velocity: one orthonormal bulk velocity per clump (default of "
                        "jeans, as before); gaussian: equal momentum per particle, the "
                        "momentum density the curvature solves for (default of clumps)")
    g = p.add_argument_group("clumps")
    g.add_argument("--gaussian", action="append", default=[],
                   help="mass,sigma,x,y,z,px,py,pz[,sx,sy,sz] (repeatable)")
    g.add_argument("--puncture", action="append", default=[],
                   help="mass,x,y,z[,px,py,pz[,sx,sy,sz]] (repeatable)")
    g.add_argument("--lattice-h", type=float, default=None,
                   help="sampler lattice: spacing of the particle lattice")
    g.add_argument("--lattice-rcut", type=float, default=6.0,
                   help="sampler lattice: cut-off radius in units of sigma")
    g = p.add_argument_group("boosted (also --puncture, --lattice-h)")
    g.add_argument("--cluster", action="append", default=[],
                   help="yc,mass,x,y,z,vx,vy,vz (repeatable): equilibrium cluster with "
                        "the bulk velocity v")
    g.add_argument("--cluster-p", action="append", default=[],
                   help="yc,mass,x,y,z,px,py,pz (repeatable): the same with the momentum "
                        "sum m u_i of the cluster instead of its velocity")
    g.add_argument("--no-psi-correction", action="store_true",
                   help="leave out the second-order correction of psi")
    g.add_argument("--boost-shift", action="store_true",
                   help="comp<c>_boost_shift = true: start with the comoving shift")
    a = p.parse_args(argv)

    os.makedirs(a.out, exist_ok=True)
    meta = dict(format="NRPIC001", units="G=c=1, M_ADM=1", seed=a.seed,
                species=a.species, generator="problems/ic/make_ic.py",
                argv=sys.argv[1:] if argv is None else list(argv))
    table = None

    if a.model == "os":
        sampler = a.sampler or "lattice"
        x, u, m, sp = sampling.sample_os(a.N, sampler, a.seed, a.R0, 1.0, a.nlat,
                                         a.species, a.normalize_lattice_mass,
                                         a.lattice_surface_correction)
        meta["lattice_surface_correction"] = bool(a.lattice_surface_correction)
        meta.update(osn.summary(a.R0))
        meta["sampler"] = sampler
        if sampler == "lattice":
            nlat = a.nlat or sampling.os_nlat_for(a.N)
            meta.update(n_lat=nlat, lattice_h=2 * osn.isotropic_radius(a.R0) / nlat,
                        lattice_convention="cell centres -rbar0+(i+1/2)h, |x|<=rbar0")
        stem = a.prefix or (f"os_R{_fmt(a.R0)}_{sampler}_N{len(m)}_s{a.seed}"
                            + ("_sc" if a.lattice_surface_correction else ""))
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
        perturbed = bool(a.vpert or a.dpert)
        consistent = perturbed and a.consistent_table
        stem = a.prefix
        if stem is None:
            stem = f"st_yc{_fmt(a.yc)}_{sampler}_N{a.N}_s{a.seed}"
            if a.vpert:
                stem += f"_vp{_fmt(a.vpert)}"
            if a.dpert:
                stem += f"_dp{_fmt(a.dpert)}"
            if consistent:
                stem += "_hc"
        if consistent:
            pst = stc.PerturbedST(model, a.dpert, a.vpert, a.vpert_profile)
            hc = pst.summary()
            hc["fd_residual"] = pst.constraint_residual(a.table_points, a.table_rmax)
            meta["table_constraint"] = hc
            meta["units"] = ("G=c=1, M_ADM of the unperturbed equilibrium = 1; ADM mass of "
                             f"these data = table_constraint.M_ADM = {pst.M!r}")
            table = lambda path: pst.write_table(path, a.table_points, a.table_rmax)
            meta["table_lapse"] = ("k alpha_0(r/s) inside (alpha_0 the static equilibrium "
                                   "lapse, k = table_constraint.alpha_factor), "
                                   "Schwarzschild isotropic with the perturbed M_ADM "
                                   "outside, continuous at the perturbed surface")
        else:
            table = lambda path: stc.write_table(model, path, a.table_points, a.table_rmax)
            meta["table_lapse"] = "static equilibrium lapse; Schwarzschild continuation outside"
            if perturbed:
                pst = stc.PerturbedST(model, a.dpert, a.vpert, a.vpert_profile)
                I_old, rel = pst.equilibrium_table_mismatch()
                meta["table_constraint"] = dict(
                    option="unperturbed_equilibrium_table",
                    warning="table of the unperturbed equilibrium: the Hamiltonian "
                            "constraint is NOT solved for the perturbed matter",
                    int_D_over_psi=I_old, monopole=model.M, mismatch_rel=rel,
                    M_ADM_consistent=pst.M, psi_c_consistent=pst.psi_c)
            else:
                meta["table_constraint"] = dict(option="equilibrium (exact)")

    elif a.model == "jeans":
        sampler = a.sampler or "stratified"
        split = tuple(int(s) for s in a.split.split(":"))
        if len(split) != 3:
            p.error("--split needs three integers, e.g. 3:1:1")
        J = clm.JeansModel(M_env=a.env_mass, R_env=a.env_R, yc=a.env_yc,
                           m_clump=a.clump_mass, sigma=a.clump_sigma, d=a.clump_x,
                           v=a.clump_v)
        mirror = not a.independent_clumps
        if a.clump_momentum_rule in (None, "velocity"):
            x, u, m, sp = J.sample(a.N, a.seed, sampler, split, mirror)
        else:
            x, u, m, sp = J.sample(a.N, a.seed, sampler, split, mirror,
                                   momentum=a.clump_momentum_rule)
            meta["clump_momentum_rule"] = a.clump_momentum_rule
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

    elif a.model == "clumps":
        if not a.gaussian:
            p.error("clumps needs at least one --gaussian")
        gs, bs = [], []
        for spec in a.gaussian:
            v = [float(c) for c in spec.split(",")]
            if len(v) not in (8, 11):
                p.error("--gaussian needs mass,sigma,x,y,z,px,py,pz[,sx,sy,sz]")
            gs.append(dict(mass=v[0], sigma=v[1], centre=v[2:5], P=v[5:8],
                           S=v[8:11] if len(v) == 11 else [0.0, 0.0, 0.0]))
        for spec in a.puncture:
            v = [float(c) for c in spec.split(",")]
            if len(v) not in (4, 7, 10):
                p.error("--puncture needs mass,x,y,z[,px,py,pz[,sx,sy,sz]]")
            v += [0.0] * (10 - len(v))
            bs.append(dict(mass=v[0], centre=v[1:4], P=v[4:7], S=v[7:10]))
        sampler = a.sampler or "stratified"
        G = clm.GaussianClumps(gs, bs)
        rule = a.clump_momentum_rule or "gaussian"
        x, u, m, sp = G.sample(a.N, a.seed, sampler, rule, a.lattice_h, a.lattice_rcut)
        stem = a.prefix or f"clumps_N{len(m)}_s{a.seed}"
        meta.pop("species")
        meta.update(model="gaussian_clumps_with_momentum", M_ADM=G.M_adm,
                    units="G=c=1", sampler=sampler,
                    momentum_rule=rule,
                    gaussians=[{k: (list(v) if hasattr(v, "__len__") else v)
                                for k, v in g_.items()} for g_ in G.gaussians],
                    punctures=[{k: (list(v) if hasattr(v, "__len__") else v)
                                for k, v in b_.items()} for b_ in G.punctures])
        if sampler == "lattice":
            meta.update(lattice_h=a.lattice_h, lattice_rcut=a.lattice_rcut)
        summ = G.particle_summary(x, u, m, sp)
        meta["particles_by_clump"] = summ
        prob = G.problem_block()
        # the curvature is given the momentum the particles carry
        for k, s_ in enumerate(summ):
            for c_ in range(3):
                prob[f"comp{k}_p{c_ + 1}"] = s_["sum_m_u"][c_]
        meta["athenak"] = {"problem": prob,
                           "particles": {"particle_file": stem + ".nrp"}}
        meta["constraints"] = ("momentum constraint solved by the smeared Bowen-York "
                               "curvature for the rule 'gaussian'; Hamiltonian residual "
                               "-psi^-12 Abar_ij Abar_ij, second order in P and S")

    elif a.model == "boosted":
        if not a.cluster and not a.cluster_p:
            p.error("boosted needs at least one --cluster or --cluster-p")
        cs, bs = [], []
        for spec in a.cluster:
            v = [float(c) for c in spec.split(",")]
            if len(v) != 8:
                p.error("--cluster needs yc,mass,x,y,z,vx,vy,vz")
            cs.append(dict(yc=v[0], mass=v[1], centre=v[2:5], v=v[5:8]))
        for spec in a.cluster_p:
            v = [float(c) for c in spec.split(",")]
            if len(v) != 8:
                p.error("--cluster-p needs yc,mass,x,y,z,px,py,pz")
            cs.append(dict(yc=v[0], mass=v[1], centre=v[2:5], P=v[5:8]))
        for spec in a.puncture:
            v = [float(c) for c in spec.split(",")]
            if len(v) not in (4, 7, 10):
                p.error("--puncture needs mass,x,y,z[,px,py,pz[,sx,sy,sz]]")
            v += [0.0] * (10 - len(v))
            bs.append(dict(mass=v[0], centre=v[1:4], P=v[4:7], S=v[7:10]))
        sampler = a.sampler or "stratified"
        BC = bcl.BoostedClusters(cs, bs, correction=not a.no_psi_correction)
        x, u, m, sp = BC.sample(a.N, a.seed, sampler, a.lattice_h, a.keep_net_momentum)
        stem = a.prefix or f"boosted_N{len(m)}_s{a.seed}"
        summ = BC.particle_summary(x, u, m, sp)
        momenta = [s_["sum_m_u"] for s_ in summ]
        files = BC.write_tables(a.out, stem, a.table_points, a.table_rmax)
        meta.pop("species")
        cl = []
        for s_, b_ in zip(BC.spec, BC.boost):
            Vh = b_.lam ** 2 * s_["V"]
            cl.append(dict(
                yc=s_["yc"], mass=s_["mass"], centre=[float(c) for c in s_["centre"]],
                v=[float(c) for c in s_["v"]], V_linear_rule=[float(c) for c in s_["V"]],
                lam=b_.lam, pmass=b_.pmass, conformal_mass=b_.conformal_mass,
                kappa=b_.kappa, rbar_s=b_.rs / b_.lam ** 2,
                wa_centre=float(b_.wa_nodes[0]),
                second_order_mass=(b_.second_order_mass(Vh) / b_.lam
                                   if BC.with_correction else 0.0)))
        meta.update(model="boosted_equilibrium_clusters", units="G=c=1", sampler=sampler,
                    clusters=cl, psi_correction=BC.with_correction,
                    M_ADM_first_order=BC.M_adm_first_order,
                    M_ADM=BC.M_adm_first_order + sum(c_["second_order_mass"] for c_ in cl),
                    punctures=[{k: (list(v) if hasattr(v, "__len__") else v)
                                for k, v in b_.items()} for b_ in BC.punctures],
                    table_files=files, particles_by_cluster=summ)
        if sampler == "quiet":
            meta.update(lattice_h=a.lattice_h)
        meta["athenak"] = {"problem": BC.problem_block(stem, momenta,
                                                       boost_shift=a.boost_shift),
                           "particles": {"particle_file": stem + ".nrp"}}
        meta["constraints"] = (
            "momentum constraint solved in the continuum by the curvature of the boost "
            "table (comp<c>_p1..3 = sum m u_i of the cluster's particles); Hamiltonian "
            "constraint to second order in the velocity with the correction table, "
            "without it a residual of second order; cross terms of several bodies and "
            "the tidal variation of their psi across a cluster are not solved")

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
    if a.model == "jeans" and a.clump_curvature:
        # momenta of the clumps as the particles carry them (after the mean removal)
        cur = {}
        for k in (1, 2):
            Pk = (m[sp == k, None] * u[sp == k]).sum(0)
            cur[f"comp{k}"] = [float(v) for v in Pk]
            for c_ in range(3):
                meta["athenak"]["problem"][f"comp{k}_p{c_ + 1}"] = float(Pk[c_])
        meta["clump_curvature"] = dict(
            momenta=cur, note="smeared Bowen-York curvature of nrpic_cf, "
                              "comp<c>_p1..3 = sum m u_i of the clump's particles")
    nrp = os.path.join(a.out, stem + ".nrp")
    nio.write_nrp(nrp, x, u, m, sp)
    meta["particle_file"] = os.path.basename(nrp)
    meta["particles"] = _particle_stats(x, u, m)
    if a.model == "st" and meta["table_constraint"]["option"] != "equilibrium (exact)":
        # particle-level form of the constraint: sum m W/psi(r_p) = M_ADM of the table
        rp = np.sqrt(np.sum(x * x, axis=1))
        u2 = np.sum(u * u, axis=1)
        for key, f, M in (("consistent", pst.psi, pst.M),
                          ("equilibrium", model.psi, model.M)):
            ps = f(rp)
            S = float(np.sum(m * np.sqrt(1.0 + u2 / ps ** 4) / ps))
            meta["table_constraint"].setdefault("particle_sum_m_W_over_psi", {})[key] = dict(
                sum=S, monopole=M, rel_diff=S / M - 1.0)
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
    elif a.model == "boosted":
        for k, (c_, s_) in enumerate(zip(meta["clusters"], meta["particles_by_cluster"])):
            print(f"  cluster {k}: yc = {c_['yc']:g}, lam = {c_['lam']:.8f}, N = {s_['N']}, "
                  f"sum m = {s_['sum_m']:.8f}, sum mW = {s_['sum_mW']:.8f}, sum m u = "
                  + ", ".join(f"{v:+.8e}" for v in s_["sum_m_u"])
                  + " (continuum "
                  + ", ".join(f"{v:+.8e}" for v in s_["continuum_momentum"]) + ")")
        print(f"  M_ADM = {meta['M_ADM']:.8f} (first order {meta['M_ADM_first_order']:.8f})")
    elif a.model == "clumps":
        for k, s_ in enumerate(meta["particles_by_clump"]):
            print(f"  clump {k}: N = {s_['N']}, sum m = {s_['sum_m']:.8f}, "
                  f"sum mW = {s_['sum_mW']:.8f}, sum m u = "
                  + ", ".join(f"{v:+.8e}" for v in s_["sum_m_u"])
                  + f", v_max = {s_['v_max']:.4f}")
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
        if a.model == "st" and meta["table_constraint"]["option"] != "equilibrium (exact)":
            tc = meta["table_constraint"]
            I_old, rel_old = pst.equilibrium_table_mismatch()
            print(f"  table: {tc['option']}")
            print(f"  unperturbed equilibrium: psi_c = {model.psi_c:.12f}, "
                  f"alpha_c = {model.alpha_c:.12f}, M_ADM = {model.M:.12f}")
            print(f"  consistent (perturbed):  psi_c = {pst.psi_c:.12f}, "
                  f"alpha_c = {pst.alpha_c:.12f}, M_ADM' = {pst.M:.12f} "
                  f"(dM/M = {pst.M / model.M - 1:+.4e}; {pst.iterations} iterations, "
                  f"fixed-point residual {pst.fixed_point_residual:.1e})")
            print(f"  old equilibrium table:   psi_c = {float(model.psi(0.0)):.12f} "
                  f"(consistent - old = {pst.psi_c - float(model.psi(0.0)):+.4e})")
            print(f"  old table, perturbed matter: int D/psi_0 d^3x = {I_old:.12f} vs "
                  f"monopole {model.M:.12f}: rel. diff {rel_old:+.4e}")
            if consistent:
                fr = tc["fd_residual"]
                print(f"  FD residual of the written table: max |Lap psi + 2 pi D/psi| = "
                      f"{fr['max_abs']:.2e} ({fr['max_rel']:.2e} of the largest source)")
            for key, d in tc["particle_sum_m_W_over_psi"].items():
                print(f"  particles: sum m W/psi [{key:11s} table] = {d['sum']:.12f}, "
                      f"monopole {d['monopole']:.12f}, rel. diff {d['rel_diff']:+.3e}")
    print(f"  N = {len(m)}, sum m = {m.sum():.10g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
