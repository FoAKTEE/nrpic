#!/usr/bin/env python3
"""Build the near-threshold equilibria and write, per model, the particle file (.nrp),
the radial table (.tab) and a JSON description, in the formats of docs/FORMATS.md and
with the conventions of problems/ic/make_ic.py (units G = c = 1, ADM mass M = 1; masses
M0/N; net momentum sum m u_i removed and recorded).

    python3 make_equilibria.py --out DIR [--N 10000] [--seed 1] [--sampler stratified]
                               [--only TAG ...]

The <problem> block for AthenaK is that of problems/st/*.athinput: pgen_name = nrpic_cf,
ncomp = 1, comp0_type = table, comp0_file = <stem>.tab, lapse = table, and
<particles> particle_file = <stem>.nrp.
"""

import argparse
import json
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import evstatic as ev  # noqa: E402
import models  # noqa: E402
from evstatic import nio  # noqa: E402


def particle_stats(x, u, m):
    r = np.sqrt(np.sum(x * x, axis=1))
    return dict(N=int(len(m)), sum_m=float(m.sum()), m_min=float(m.min()),
                m_max=float(m.max()), r_max=float(r.max()), r_min=float(r.min()),
                com=[float(v) for v in (m[:, None] * x).sum(0) / m.sum()],
                sum_m_u=[float(v) for v in (m[:, None] * u).sum(0)])


def build(spec, out, N, seed, sampler, table_points=4000, table_rmax=1.5):
    fam = models.FAMILIES[spec["family"]]
    md = ev.Equilibrium(fam, spec["y0"])
    x, u, m, sp, aux = ev.sample(md, N, sampler, seed)
    stem = f"{spec['tag']}_{sampler}_N{N}_s{seed}"
    meta = dict(format="NRPIC001", units="G=c=1, M_ADM=1", seed=seed, species=0,
                generator="tracks/C-sidm/equilibria/make_equilibria.py", sampler=sampler,
                role=spec["role"], tag=spec["tag"])
    meta.update(md.summary())
    # Killing energy and squared angular momentum of every particle (before the
    # momentum shift): E = alpha W, L = |x cross u|^2 (isotropic coordinates)
    rb = np.linalg.norm(x, axis=1)
    ps = md.psi(rb)
    W = np.sqrt(1.0 + np.sum(u * u, axis=1) / ps ** 4)
    E = md.alpha(rb) * W
    L = np.sum(np.cross(x, u) ** 2, axis=1)
    L0M = fam.L0 * md.Mscale ** 2          # L ~ length^2: paper units -> M units
    meta["particle_invariants"] = dict(
        E_over_E0_max=float(E.max() / md.E0), E_over_E0_min=float(E.min() / md.E0),
        L_min=float(L.min()), L0_M_units=float(L0M),
        note="E = alpha(rbar) W, L = |x x u|^2 in M units; a steady state of the ansatz "
             "needs E <= E0 and L >= L0")
    ubar = (m[:, None] * u).sum(0) / m.sum()
    u = u - ubar
    meta["net_momentum_removed"] = dict(
        mean_u=[float(v) for v in ubar],
        note="u_i -> u_i - sum(m u_i)/sum(m); sum m u_i = 0 afterwards (as make_ic.py)")
    nrp = os.path.join(out, stem + ".nrp")
    nio.write_nrp(nrp, x, u, m, sp)
    meta["particle_file"] = os.path.basename(nrp)
    meta["particles"] = particle_stats(x, u, m)
    # particle form of the constraint: sum m W/psi(r_p) = M_ADM of the table
    W2 = np.sqrt(1.0 + np.sum(u * u, axis=1) / ps ** 4)
    S = float(np.sum(m * W2 / ps))
    meta["table_constraint"] = dict(option="equilibrium (exact static solution)",
                                    particle_sum_m_W_over_psi=S, monopole=md.M,
                                    rel_diff=S / md.M - 1.0)
    tab = os.path.join(out, stem + ".tab")
    r, uu, al = md.write_table(tab, table_points, table_rmax)
    meta["table_file"] = os.path.basename(tab)
    meta["table"] = dict(rows=int(len(r)), dr=float(r[1] - r[0]), r_max=float(r[-1]),
                         M_from_last_row=float(2 * r[-1] * uu[-1]))
    meta["table_lapse"] = "static equilibrium lapse; Schwarzschild continuation outside"
    meta["athenak"] = {"problem": dict(pgen_name="nrpic_cf", ncomp=1, comp0_type="table",
                                       comp0_file=os.path.basename(tab), lapse="table"),
                       "particles": dict(particle_file=os.path.basename(nrp))}
    with open(os.path.join(out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=2)
    return stem, meta


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True)
    p.add_argument("--N", type=int, default=10000)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--sampler", default="stratified", choices=["stratified", "mc"])
    p.add_argument("--only", nargs="*", default=None)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    index = []
    for spec in models.model_set():
        if a.only and spec["tag"] not in a.only and spec["family"] not in a.only:
            continue
        t0 = time.time()
        stem, meta = build(spec, a.out, a.N, a.seed, a.sampler)
        index.append(dict(stem=stem, family=spec["family"], y0=spec["y0"], role=spec["role"],
                          Eb=meta["Eb_over_M0"], Zc=meta["Zc_infinity"],
                          zc_boundary=meta["zc_boundary"], R=meta["R_areal"],
                          rbar_s=meta["rbar_s"], M0=meta["M0"],
                          sum_m_W_over_psi_rel=meta["table_constraint"]["rel_diff"],
                          seconds=round(time.time() - t0, 2)))
        print(f"{stem}: Eb = {meta['Eb_over_M0']:.6f}, Z_c = {meta['Zc_infinity']:.5f}, "
              f"R = {meta['R_areal']:.5f} M, rbar_s = {meta['rbar_s']:.5f} M, "
              f"sum mW/psi - 1 = {meta['table_constraint']['rel_diff']:+.2e} "
              f"({index[-1]['seconds']} s)", flush=True)
    with open(os.path.join(a.out, "index.json"), "w") as f:
        json.dump(dict(N=a.N, seed=a.seed, sampler=a.sampler, models=index), f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
