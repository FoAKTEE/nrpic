# oblate: the oblate spheroid of `nrpic_cf`, its sampler, and the oblate collapse (core)

Work package "oblate" of owner core, wave 3a (2026-11-19), branch `core/oblate`.
Journal with predictions and outcomes: `tracks/core/JOURNAL-oblate.md`. Interface text:
`tracks/core/interfaces/oblate_spheroid.md`. Published executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_oblate/` (READY, COMMIT, SHA256SUMS).

| Path | Content |
|---|---|
| `newton_spheroid.py` | Newtonian collapse of a cold homogeneous spheroid, continued through the pancake: the semi-analytic reference of T3; figure `figs/newton_spheroid` |
| `cf_check.py` | T1: the oblate component against the reference potential (a: psi at every cell, three shapes; b: Hamiltonian monitor without matter; c: integrals with the sampled particles; d: off the origin, superposed); figures `figs/cf_check_{psi,ham,id,super}` |
| `card_cf.py` | T1, part e: the same conformal factor as the card executable sets it (run `cf_card` of the card job); figure `figs/cf_check_card` |
| `regress.py` | T2: byte regression of existing set-ups against the release executable |
| `make_runs.py` | T3: initial data and the card-job list |
| `run_newton.sh`, `newton_mode.py` | T4: the Newtonian reference of the collapse in AthenaK (release code, `pusher = newton`) with the particles of T3 at cells M/2 and M/4, against the homogeneous spheroid; figures `figs/oblate_newton`, `figs/oblate_newton_particles` |
| `collapse_analysis.py` | T3: particle moments, plane crossing, horizon, curvature, constraint norm of the collapse runs; figures `figs/oblate_collapse`, `figs/oblate_mosaic`, `figs/oblate_particles` |

Inputs: `problems/tests/oblate_cf.athinput`, `oblate_id.athinput`,
`oblate_super.athinput`, `problems/oblate/oblate_amr.athinput`, `problems/oblate/oblate_newton.athinput`. Unit tests of the Python
tools: `python/tests/test_oblate_spheroid.py`.

## Runs

| Test | Run id | State |
|---|---|---|
| T1 a-c | core-20261119-143758-09c669d | holds (two worded sub-predictions failed: journal entry 2) |
| T1 a-d rerun | core-20261119-152206-4d292b9 | holds (journal entry 6) |
| T2 | core-20261119-144947-fb1ccae (first attempt -144337-5c02abf, stopped) | holds |
| T3 initial data | core-20261119-144859-fbf3438 | done |
| T3 card job (cf_card, oblate_m4, oblate_m8) | core-20261119-144923-1a7c274, Slurm job 4647 | see the journal |
| T4 Newtonian reference, cells M/2 and M/4 (processors) | core-20261119-153609-754c44d | see the journal, entry 8 |

## How to finish T3 when the card job has ended

```
cd /data/haiyangw/nrpic/wt/core-oblate
harness/bin/nrpic-run finish core-20261119-144923-1a7c274
R=/data/haiyangw/nrpic/scratch/core/core-20261119-144923-1a7c274
cat $R/batch.list.status                                             # rc of the three runs
harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 1 \
  --purpose "T1 part e: conformal factor of the oblate component on the card" -- \
  python3 tracks/core/analysis/oblate/card_cf.py --card $R/cf_card \
  --cpu /data/haiyangw/nrpic/scratch/core/core-20261119-143758-09c669d/P1a/e09
harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 1 \
  --purpose "T3: analysis of the oblate collapse at M/4 and M/8" -- \
  python3 tracks/core/analysis/oblate/collapse_analysis.py \
  --run m4=$R/oblate_m4 --run m8=$R/oblate_m8 \
  --prolate m8=/data/haiyangw/nrpic/scratch/core/core-20261115-152845-5728b1d/prolate_m8 \
  --prolate m16=/data/haiyangw/nrpic/runs/prolate/e09_v8
```

Then read the three figures, judge P3a to P3d (entry 1) and P3a', P3c' (entry 3) in the
journal, and update READY (card status) and section 5 of the interface text. If a run
stopped on its wall limit before t = 55 M (`Terminating on wall clock limit` in its
log), continue it from its newest restart file with a list line
`<name> $R/<name>/rst/<newest>.rst -t hh:mm:ss` and `nrpic-run submit --launcher batch`;
the card time of the package is one hour in all (job 4647 may use up to 0.75).
A run at M/16 (`make_runs.py --levels 7`) only if the M/8 run shows that it fits in
what is left with a margin of 20 per cent (rule of entry 1): memory first (the prolate
M/16 run peaked at 62 GB with 1352 blocks).
