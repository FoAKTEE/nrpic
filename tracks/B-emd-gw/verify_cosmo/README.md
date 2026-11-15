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

REQUESTS
