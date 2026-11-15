#!/usr/bin/env python3
"""Write one expanding-ball data set and register it as a run.

Outputs (in scratch/A-emd-pbh/<run_id>/):
    <stem>.tab                    table format 2 (rbar u KL KT alpha betar, exterior = pg)
    <stem>_strat_N<N>_s<seed>.nrp equal-mass stratified particles, u_i = 0
    <stem>_lat<n>.nrp             mass-weighted lattice, u_i = 0 (surface layer corrected)
    <stem>_mesh<Nm>.npz           3+1 fields on the cell-centred mesh of [-L, L]^3
    <stem>_shells.txt             exact shell table: R_i, rbar_i, m, E, tau_ta, tau_c, tau_AH
    <stem>.json                   parameters, derived quantities, predicted times, file list

Examples
    make_dataset.py --model flat --HRb 0.5
    make_dataset.py --model smooth_tophat --HRb 0.5 --delta-c 1.0 --R1 0.3 --R2 0.75
"""

import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

import numpy as np  # noqa: E402

from expball import exact, mesh, model as M, particles, runlog, table  # noqa: E402


def build_ball(a):
    if a.model == "flat":
        prof = M.Flat()
    else:
        Rb = 2.0 * a.M / a.HRb ** 2
        cls = M.TopHat if a.model == "tophat" else M.SmoothTopHat
        prof = cls(a.delta_c, a.R1 * Rb, a.R2 * Rb)
    return M.Ball.from_HRb(a.HRb, a.M, prof, a.edge_width * 2.0 * a.M / a.HRb ** 2)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", choices=["flat", "tophat", "smooth_tophat"], default="flat")
    p.add_argument("--HRb", type=float, default=0.5, help="H R_b on the slice")
    p.add_argument("--M", type=float, default=1.0, help="mass unit: R_b = 2M/(H R_b)^2")
    p.add_argument("--delta-c", type=float, default=1.0, help="mean density contrast of the core")
    p.add_argument("--R1", type=float, default=0.3, help="core radius / R_b")
    p.add_argument("--R2", type=float, default=0.75, help="outer radius of the compensation / R_b")
    p.add_argument("--edge-width", type=float, default=0.0, help="edge taper half width / R_b")
    p.add_argument("--table-points", type=int, default=4000, help="rows across the matter")
    p.add_argument("--table-extent", type=float, default=1.5, help="table end / rbar of the matter edge")
    p.add_argument("--N", type=int, default=100000, help="stratified particle number")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--nlat", type=int, default=None, help="lattice cells across the diameter")
    p.add_argument("--mesh-N", type=int, default=64)
    p.add_argument("--mesh-L", type=float, default=1.25, help="mesh half width / R_b")
    p.add_argument("--kind", default="production")
    a = p.parse_args(argv)

    ball = build_ball(a)
    stem = f"expball_{a.model}_HRb{a.HRb:g}".replace(".", "p")
    if a.model != "flat":
        stem += f"_dc{a.delta_c:g}_R1{a.R1:g}_R2{a.R2:g}".replace(".", "p")
    if a.edge_width > 0:
        stem += f"_w{a.edge_width:g}".replace(".", "p")
    purpose = (f"A-pre-1 data set: expanding dust ball, model {a.model}, H R_b = {a.HRb}"
               + ("" if a.model == "flat" else f", bound core delta_c = {a.delta_c}, "
                  f"R1 = {a.R1} R_b, R2 = {a.R2} R_b"))
    with runlog.Run(purpose, kind=a.kind, cores=4) as run:
        out = run.out
        summ = ball.summary()
        rm = ball.matter_rbar()
        drbar = rm / a.table_points
        tab = os.path.join(out, stem + ".tab")
        hdr = dict(generator="tracks/A-emd-pbh/expball/scripts/make_dataset.py", run_id=run.run_id,
                   model=a.model, H=repr(ball.H), Rb=repr(ball.Rb), M=repr(ball.M),
                   t_i=repr(ball.t_i), units="G = c = 1, M_ADM = M",
                   alpha="1 (proper-time slicing of the dust)",
                   betar="-v/(psi^2 sqrt(1+2E)) (shift of the dust's proper-time slicing)")
        table.write_format2(tab, ball, drbar, a.table_extent * rm, header=hdr)
        files = dict(table=os.path.basename(tab))
        # particles
        x, u, m, sp = particles.sample(ball, a.N, "stratified", a.seed)
        f1 = f"{stem}_strat_N{a.N}_s{a.seed}.nrp"
        particles.write_nrp(os.path.join(out, f1), x, u, m, sp)
        nlat = a.nlat or particles.nlat_for(a.N)
        xl, ul, ml, spl = particles.lattice(ball, nlat)
        f2 = f"{stem}_lat{nlat}.nrp"
        particles.write_nrp(os.path.join(out, f2), xl, ul, ml, spl)
        files.update(particles_stratified=f1, particles_lattice=f2)
        # mesh fields
        L = a.mesh_L * ball.Rb
        f3 = f"{stem}_mesh{a.mesh_N}.npz"
        mesh.write_mesh_npz(os.path.join(out, f3), ball, a.mesh_N, L,
                            meta=dict(run_id=run.run_id, L=L, N=a.mesh_N, model=a.model))
        files["mesh"] = f3
        # exact shells
        Ri = np.concatenate([np.linspace(ball.R_out / 400, ball.R_out, 400)])
        sh = exact.Shells(ball, Ri)
        rbi = ball.rbar_of_R(Ri)
        f4 = f"{stem}_shells.txt"
        with open(os.path.join(out, f4), "w") as fh:
            fh.write("# exact shells of the expanding ball (expball/exact.py); proper time tau of the\n"
                     "# dust from the initial slice; inf = never. Columns:\n"
                     "# R_i rbar_i m E tau_ta tau_c tau_AH\n")
            for row in zip(Ri, rbi, sh.m, sh.E, sh.tau_ta, sh.tau_c, sh.tau_ah):
                fh.write(" ".join(f"{v:.15e}" for v in row) + "\n")
        files["shells"] = f4
        pred = sh.summary()
        if not np.any(sh.bound):
            pred["first_horizon"] = None          # no shell is bound: no horizon ever
        if a.model != "flat":
            core = Ri <= ball.prof.R1
            pred.update(core_tau_ta=float(sh.tau_ta[core][0]), core_tau_c=float(sh.tau_c[core][0]),
                        core_tau_ta_spread=float(np.ptp(sh.tau_ta[core])),
                        core_edge_shell=dict(R_i=ball.prof.R1, m=float(ball.at(np.array([ball.prof.R1]))["m"][0]),
                                             tau_ah=float(exact.Shells(ball, np.array([ball.prof.R1])).tau_ah[0])))
            tsc = sh.shell_crossing(np.linspace(0.0, 0.999 * pred["core_tau_c"], 2000))
            pred["shell_crossing_before_core_crunch"] = tsc
        else:
            Rb_t = lambda t: float(sh.R(np.array(t))[-1])
            pred.update(ball_edge_R_at_tau={str(t): Rb_t(t) for t in (0.0, 10.0, 50.0, 100.0)},
                        R_b_law="R_b(tau) = R_b (1 + 3 H tau/2)^(2/3) (expands for ever)")
        meta = dict(run_id=run.run_id, args=vars(a), model=summ, predictions=pred, files=files,
                    table=dict(drbar=drbar, rows=int(np.ceil(a.table_extent * rm / drbar)) + 1,
                               rbar_last=float(drbar * np.ceil(a.table_extent * rm / drbar))),
                    particles=dict(stratified=dict(N=int(len(m)), sum_m=float(m.sum())),
                                   lattice=dict(N=int(len(ml)), n_lat=nlat, sum_m=float(ml.sum()),
                                                h=2 * rm / nlat)),
                    mesh=dict(N=a.mesh_N, L=L, layout="cell centres -L + (i+1/2) 2L/N"),
                    notes=["u_i = 0 for every particle: dust at rest w.r.t. the normal observers",
                           "alpha = 1 and betar of the proper-time slicing; the code's gauge differs",
                           "compare with the exact solution through invariants: areal radius of "
                           "a shell against its particles' proper time, Misner-Sharp mass, tau_AH"])
        with open(os.path.join(out, stem + ".json"), "w") as fh:
            json.dump(meta, fh, indent=2, default=float)
        run.results = dict(summary=summ, predictions=pred, files=files)
        run.extra["dataset"] = True
        print(json.dumps(dict(summary=summ, predictions=pred), indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
