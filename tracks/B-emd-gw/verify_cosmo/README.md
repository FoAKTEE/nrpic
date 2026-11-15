# verify_cosmo (helper package of B-emd-gw)

B-pre-2 and B-pre-5 checked against what `cosmo/` already has, and a first plane-wave
pancake through shell crossing in AthenaK with the Newtonian particle-mesh reference,
both against the Zel'dovich solution.

| Path | Content |
|---|---|
| `VERIFY.md` | evidence in `cosmo/` for the rows "FLRW dust", "growth of linear perturbations", "multi-code comparison" of brief section 10 and for G1 and G2 of the Track B sheet; what is missing; the pancake results (section 6) |
| `JOURNAL.md` | predictions written before each run, outcomes after |
| `scripts/zeldovich.py` | exact Newtonian plane-symmetric solution for the plane wave of `make_east.py --ratios 1,0,0` (continuum and discrete sheets), first-crossing finder |
| `scripts/test_zeldovich.py` | checks of that reference (closed form against an integration of the sheet equations, density identity, discreteness) |
| `scripts/build_ic.sh` | initial data of the four pancake cases with `cosmo/ic/make_east.py` |
| `inputs/pancake.athinput` | AthenaK input: `problems/cosmo/east.athinput` in the production configuration of `cosmo/README.md`, field dumps with constraints, line records |
| `scripts/newton_pancake.py` | driver of the Newtonian reference `cosmo/newton/pm.py` (unchanged) for the same particles |
| `scripts/analyze_pancake.py` | comparison with Zel'dovich, crossing times, constraints, plane symmetry, figures |
| `scripts/recheck_flrw.py` | re-reads the homogeneous runs of `cosmo/` against the exact solution |
| `scripts/register.py` | writes the run manifests under `tracks/B-emd-gw/runs/` |
| `results/` | JSON outputs copied from the run directories |
| `figs/` | figures (inspected; listed in `JOURNAL.md`) |

## Rerun

All commands from the worktree root `/data/haiyangw/nrpic/wt/B-emd-gw`; outputs go to
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/` (run ids in `JOURNAL.md`).

```
python3 tracks/B-emd-gw/verify_cosmo/scripts/test_zeldovich.py
OUT=/data/haiyangw/nrpic/scratch/B-emd-gw/<ic_run_id>
tracks/B-emd-gw/verify_cosmo/scripts/build_ic.sh $OUT                    # about 3 min
# card run: copy particles.nrp, fields.bin, id.json, fiducial.npz of each case into
# <gr_run_dir>/<case>/, write the list as in <gr_run_dir>/pancake.list, then
ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_c3/src/athena TIME=00:50:00 \
    scripts/gpu_batch.sh <gr_run_dir>/pancake.list                       # about 17 card-min
for n in 32 64; do OMP_NUM_THREADS=1 python3 tracks/B-emd-gw/verify_cosmo/scripts/newton_pancake.py \
    --delta 0.05 --n $n --L 1 --tend 10.9615 --out <nw_run_dir>/n$n; done   # 2 and 28 min
python3 tracks/B-emd-gw/verify_cosmo/scripts/analyze_pancake.py --gr <gr_run_dir> \
    --newton <nw_run_dir> --out <analysis_run_dir>
python3 tracks/B-emd-gw/verify_cosmo/scripts/recheck_flrw.py --out <run_dir>
```

Register every run first (`scripts/register.py new ...`, then `finish`); the manifests
of this package's runs show the exact commands.

## Requests

To the lead of B-emd-gw (for outbox proposals to orch where the charter changes):
1. G1, "background error and constraint convergence with the stand-in matter": the
   stand-in fluid was never run and the particle background it stood in for is
   verified directly (`VERIFY.md` section 1); propose striking the item or rewording
   it to the particle background.
2. G2, "agreement with gevolution in the weak-field regime": under decision 0010 no
   outside code is run; propose rewording it to the shearing-dust code comparison of
   arXiv:2003.08014 (gevolution, GRAMSES, Einstein Toolkit, CosmoGRaPH on one test with
   published numbers; `VERIFY.md` section 3), run in AthenaK, as a B work package.
3. G2, particle-number convergence: neither the scale-factor error nor the growth has
   a run at fixed mesh with different particles per cell in the production
   configuration; a work package of minutes on a card (`VERIFY.md` section 7, items 1
   and 2).
4. `cosmo/PLAN.md` (state 06:30) says "one particle per cell is enough with the cubic
   cloud before collapse". The pancake refutes this where the lattice is stretched:
   in the void of the plane wave one particle per cell leaves mean H_r = 1.3e-3 and
   mean M_r = 0.21 at a = 15 and negative energy density after the crossing; two per
   cell and direction lower both by about 30 (`JOURNAL.md`, P7). Worth a line in
   `cosmo/README.md` (production configuration) through orch.

To core:
5. Newtonian mode in AthenaK (decision 0010, consequence 1): the pancake of this package
   (`inputs/pancake.athinput`, `scripts/zeldovich.py` as the exact reference before
   crossing, the Newtonian results of run B-emd-gw-20261115-115239-69ab1db) is a ready
   acceptance test for it. The Python reference `cosmo/newton/pm.py` converges only at
   first order in the cell size with one particle per cell (`JOURNAL.md`, P1, P8).

To kb: nothing; arXiv:2003.08014, 1505.04756 and 2010.12584 are already in `kb-data/`.
