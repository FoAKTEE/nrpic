# box_tests: box tests of the collision operator of release core-v0.3

Helper package of C-sidm, wave 2. The Minkowski-box tests of `../collide/TESTS.md` (pass
criteria fixed in wave 1, not changed here) run with the release executables of
core-v0.3 (read-only, main checkout):

- processors: `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (serial Kokkos, no MPI),
- card: `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena` (one A100),

with the option names of `coord/INTERFACES/collisions.md`. Particle files come from the
track's own generator `../collide/analysis/make_box.py`; reference values from
`../collide/REFERENCES/`; the replay of T0b is written from the interface text with the
track's oracle and `python/nrpic/rng.py` (not core's twin `python/nrpic/collide.py`).
Predictions and outcomes, failed ones included: `JOURNAL.md`. Results: section
"Results" below (filled as the runs finish).

## Contents

| Path | What |
|---|---|
| `inputs/box.athinput` | periodic Minkowski box [10, 11)^3, `nrpic_geodesic`, flat Kerr-Schild functor, `triad = cholesky`, collision options of collisions.md |
| `inputs/card_T2.list` | card runs (cost, T10b) on the particle files of the processor T2 run |
| `scripts/boxlib.py` | shared helpers: particle files, running the executable, coll.hst and dump readers, exact sums |
| `scripts/smoke.py` | format check (S0) |
| `scripts/design.py` | design numbers of every test from the track's references (run before the tests) |
| `scripts/t1t2.py` | T1 per step and T2 (rate) on 16 runs; processor cost |
| `scripts/t1long.py` | T1 over 1e4 steps |
| `scripts/replay.py`, `scripts/t0b.py` | T0b: replay of one collision step from the dump |
| `scripts/t10.py` | T10: MeshBlock divisions, restarts, seed |
| `scripts/t345.py` | T3, T4, T5 (relaxation, initial rate, entropy) with the wave-1 analysis `../collide/analysis/an_box.py relax` |
| `scripts/t9.py` | T9: unequal masses (nanbu), 8 seeds; refusal with `equal` |
| `scripts/t11.py` | T11: drifting gas (a, b) and drifting two-temperature start (c) |
| `scripts/card.py` | card cost per pair and T10b against the processor runs |
| `figs/` | figures of the runs (copied from the run directories; each looked at) |
| `JOURNAL.md` | predictions before each run, outcomes after |

## How to rerun

From the worktree root, with the worktree's environment (`harness/bin/nrpic-env create
--no-kokkos` once), every run registered:

    D=/data/haiyangw/nrpic/scratch/C-sidm/C-20261115-165028-a559ab8/design.json
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/C-sidm/box_tests \
        --cores 1 --purpose "design" -- python3 tracks/C-sidm/box_tests/scripts/design.py
    harness/bin/nrpic-run submit ... --cores 8 -- python3 tracks/C-sidm/box_tests/scripts/t1t2.py $D --nproc 8
    harness/bin/nrpic-run submit ... --cores 6 -- python3 tracks/C-sidm/box_tests/scripts/t0b.py $D
    harness/bin/nrpic-run submit ... --cores 4 -- python3 tracks/C-sidm/box_tests/scripts/t10.py
    harness/bin/nrpic-run submit ... --cores 8 -- python3 tracks/C-sidm/box_tests/scripts/t345.py $D --nproc 8
    harness/bin/nrpic-run submit ... --cores 2 -- python3 tracks/C-sidm/box_tests/scripts/t1long.py
    harness/bin/nrpic-run submit ... --cores 2 -- python3 tracks/C-sidm/box_tests/scripts/t9.py $D --nproc 2
    harness/bin/nrpic-run submit ... --cores 4 -- python3 tracks/C-sidm/box_tests/scripts/t11.py --nproc 4
    harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/box_tests/inputs/card_T2.list \
        --gpu-hours 0.25 --wall 00:15:00 --exe /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena ...
    harness/bin/nrpic-run submit ... -- python3 tracks/C-sidm/box_tests/scripts/card.py <card run dir> <T2 run dir>

Processor runs are bit-reproducible (T10); the design JSON is an input of the later runs.

## Results

(see below; each line names its run id)

## Requests

(see below)
