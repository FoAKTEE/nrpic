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

## Results (release core-v0.3; every test of this package passes)

| Test | Verdict | Run id | Key numbers | Figure |
|---|---|---|---|---|
| S0 formats | done | C-20261115-164809-cd53539 | dump layout of collisions.md 5 parsed to the last byte; findings F1, F3 | - |
| design | done | C-20261115-165028-a559ab8 | sigma, dt, tau_rel, theta_eq, entropy gaps of every test | - |
| T0b replay (triad = cholesky) | PASS 6/6 dumps | C-20261115-170155-13ff01f | cells, n_sub, updates of all 1e4 particles identical; n_tested, n_coll identical; sum_P to 2.2e-15; momenta to 4.4e-16 of max(1,\|u\|); untouched bit-identical | `figs/t0b_replay_cpu.png` |
| T1 per step | PASS 16/16 + 4 + 2 | C-20261115-165500-c67e036 (and the T3-T5, T1-long runs) | \|dE\|, \|dP_i\| per step <= 2.8e-19 of sum M W (1e-7 of the bound); exactly rounded sum M W bit-identical start to end; n_trunc 0 | `figs/t1_step_cpu.png`, `figs/t1t2_summary_cpu.png` |
| T1 over 1e4 steps | PASS 2/2 | C-20261115-170741-248af65 | 1.56e7 collisions per run; sum M W bit-identical at all 11 snapshots | `figs/t1_long_cpu.png` |
| T2 rate | PASS 16/16 | C-20261115-165500-c67e036 | theta 1e-3 to 10, plain and sub-cycled: (a) z in [-2.1, 1.6]; (b) ratio 0.99987-1.00008, z in [-2.2, 2.9]; (c) exact | `figs/t2_rate_cpu.png`, `figs/t1t2_summary_cpu.png` |
| T3 relaxation | PASS 4/4 | C-20261115-170539-28432c3 | KS p 0.084-0.99 at 15 tau_rel; populations within 1 se of theta_eq | `figs/relax_T345_*.png` |
| T4 initial rate | PASS 4/4 | C-20261115-170539-28432c3 | slope/exact 0.9924, 0.9792 (theta_2 = 1e-3), 0.9959, 1.0088 (theta_2 = 1); se 0.3-0.6 percent | `figs/t4_zoom_cpu.png` |
| T5 entropy | PASS 4/4 | C-20261115-170539-28432c3 | s(0) = s_mix and s(end) = s_MJ within 0.2 se; monotone | `figs/relax_T345_*.png` |
| T9 unequal (nanbu) | PASS (8 seeds) | C-20261115-170814-8a54b43 | same theta z in [-1.2, 0.6]; KS p >= 0.089; mean energy drift +2.4 se (O4); `equal` refused with a message naming the masses | `figs/t9_unequal_cpu.png` |
| T10 reproducibility | PASS | C-20261115-165902-f9b1c8f | 1, 8, 64 MeshBlocks and restarts from cycles 0, 37, 74 bit-identical; seed 8 changes every particle; MPI not run (no MPI build) | `figs/t10_repro_cpu.png` |
| T10b processor/card | PASS 4/4 | C-20261115-170447-cb3b230, C-20261115-180525-94ddd22 | same tested pairs and collisions per step on card and processor; momenta 8.9e-15 apart | - |
| T11 Lorentz covariance | PASS (a, b, c; 2 seeds) | C-20261115-174651-0ad8612 | (a) z = 1.15, 0.19; (b) \|z\| < 1.2; (c) moments vs drifting MJ(theta_f, beta_f) \|z\| <= 1.0, KS p >= 0.21 | `figs/t11_drift_cpu.png` |
| D1, D2 diagnostics | done | C-20261115-180041-f00f777, C-20261115-180434-fd05776 | T11 sum_P excess (2-3e-4, not a criterion) = finite-sample pair-mean fluctuation of the gas; tested pairs follow the sample | - |
| Cost per pair | measured | C-20261115-165500-c67e036 (processor), C-20261115-180525-94ddd22 (card) | processor, one core: 5.7-6.7e-7 s per tested pair (one sub-step), 3.3-3.7e-7 (sub-cycled), 3.0e-7 s per particle and step; A100: 3.9e-9 s (one sub-step), 3.4e-9 s (sub-cycled), 2.1e-9 s per particle and step; ratio 96-173; 1e6 particles: 0.60 s vs 3.25 ms per step | `figs/cost_gpu.png` |

Findings (JOURNAL.md): F1 `nrpic.hst` sum_mW is 0 without deposit (documented), so T1's drift
is read from exactly rounded snapshot sums; F2 the collision dump of `coll_dump_cycle = c`
and the key use the step number c, while `coll.hst` labels that step c + 1 (documented in
collisions.md, easy to trip over); F3 the snapshot header's cycle lags the histories by
one (FORMATS.md does not say). None is a defect of the operator. No test failed, so there
is no reproduction to report and nothing to rerun with a corrected executable (none was
published under `scratch/core/exe/core_collisions-2/` during the session).

Not done here (outside this package's list or blocked): T6-T8 (conduction; the
expensive runs, card), T12 (curved static box; core now has `<problem> metric_kind =
homogeneous`, collisions.md section 9), the MPI variant of T10 (no MPI build), a second
card statistic for T4 (T10b names T4 too; only T2 statistics were compared on the card).

Open items: O3 T4 precision (0.3-0.6 percent per run; the theta_2 = 1e-3 pair is low by
-1.5 and -3.3 se from the expected 1.0025: more seeds or particles would show whether a
few-tenths-of-a-percent bias exists); O4 nanbu's energy drift (mean +0.18(7) percent of
the thermal energy over 8 seeds, 2.4 se; production runs use equal masses).

Card time used: 0.014 card-hour (Slurm job 4464, 51 s).

## Requests

To core (branch `core/nrpic`):
- collisions.md section 5 and docs/FORMATS.md: one sentence each on the step labels: the
  dump of `coll_dump_cycle = c` and the snapshot whose header says cycle c belong to the
  step that `coll.hst` and `nrpic.hst` record as cycle c + 1 (F2, F3); or align the labels.
- Optional: fill `nrpic.hst` sum_mW from the particles when `deposit = false` (F1), so the
  box tests can read the energy drift from the history.
- For the MPI variant of T10: a processor build with MPI, when one exists.

To the lead of C-sidm:
- TESTS.md T1: the drift of sum M W is read from the snapshots (F1); T2(b): "theta" is the
  gas temperature from <W - 1> of the sample (with the nominal temperature the 4 se clause
  fails by sampling noise: z up to 35.6 in run C-20261115-165500-c67e036); T11(c) has no
  numeric criterion in TESTS.md: the one used here was declared before the run
  (JOURNAL.md, T11 predictions). Amend the text if you agree; the verdicts above do not
  depend on it except as stated.
- Rate checks below 1e-3 should compare the tested pairs with the sample's own pair mean
  (D2), not with the ensemble formula.
- Next box work: T6-T8 (card), T12 with `metric_kind = homogeneous`, O3 and O4 if they
  matter for the science runs.

To orch: none from this package. The harness worked (nrpic-run registered every run;
three submissions were refused by the owner's 16-core allotment and resubmitted with
fewer cores; with output redirected, the "registered" line of a local run appears only
when the run ends).
