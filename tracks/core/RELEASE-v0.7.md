RELEASE core-v0.7 5f75e5b9cd02fee45eead0b4c3445189d8362dde REGRESSION PASS

Card check of the candidate's card executable `athena_gpu`: PENDING (shared-queue entry
q0039, label `core-v07-card`, handed over 2026-11-25T03:02Z; section "Card checks
pending" has the commands that judge it). The card executable was built without a card
and has not run on one. The processor results below do not depend on it. Still pending
on 2026-11-25T12:10Z (batch 17): q0039, q0035, q0036 wait in the shared queue (state
waiting; five jobs of other owners held the cap).

# Release candidate core-v0.7: four source branches of core on top of core-v0.6

Written by the lead of core on 2026-11-25 UTC (2026-11-24 PST; decision 0035 item 4;
batch 14). The commit of the first line is the source commit: the last commit of
`core/nrpic` that changes `athenak/`, `python/`, `problems/`, `scripts/` or `docs/` (the
merge of core/clump-table; `git rev-parse 5f75e5b9`). Later commits of `core/nrpic` add
records and release drivers only (`tracks/core/`); `git diff 5f75e5b9 <tip> -- athenak
python problems scripts docs` is empty [VERIFIED at the tip that holds this file].
Predictions, written before any merge or build, and outcomes: `tracks/core/JOURNAL.md`,
entry of 2026-11-25T02:12Z. Options, behaviour that changes without an option, scripts,
formats: `tracks/core/CHANGELOG.md`, section core-v0.7.

## Executables of the candidate

`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/`, all four built from the source
commit in new build directories of `wt/core` (COMMIT there has the commands and times):

| File | Build | sha256 |
|---|---|---|
| `athena_cpu` | `scripts/build_cpu.sh` (Kokkos Serial, -O2 -g), `.work/build_cpu_v07rc` | 53e60576...0d7288f19 |
| `athena_gpu` | `scripts/build_gpu.sh` (CUDA 12.6, one A100, no MPI), `.work/build_gpu_v07rc` | 2d607ede...9c670afc9 |
| `athena_cpu_omp` | `scripts/build_cpu_omp.sh` (Kokkos OpenMP, -O3 -DNDEBUG -g), `.work/build_omp_v07rc` | fbf605f4...829abd3946 |
| `athena_cpu_mpi` | `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh` (Open MPI 5.0.1), `.work/build_cpu_mpi_v07rc` | 1a5f3a93...5dda2c3c78 |

With them `COMMIT`, `SHA256SUMS`, `READY` (every new option with one example input, what
is tested and what is not, known defects) and `branches/READY.<branch>` (the READY of
each merged branch).

## Branches merged, in this order (one merge commit each)

| Branch | Tip merged (source) | Merge commit | Review |
|---|---|---|---|
| core/noise-level2 | 5c98beef (64f150ec) | da904f55 | pass; written on Opus, reviewed on Fable on 2026-11-24 with the verdict "results unchanged"; every option read only if present |
| core/step-limit | 3a9a3498 (5c4b644f) | 76ac67a2 | pass; `dt_gauge` off when absent; two things act without an option (the stop on SIGTERM, a warning in the log) |
| core/gauge-2 | 61c8fc4d (984110c3) | 31ae23e6 | pass, as a MITIGATION of the relaxed lapse's defect (decision 0025 item 3), named so in the changelog and in OPEN.md |
| core/clump-table | ff11719d (7cc6c7b9) | 5f75e5b9 | pass; taken after its outstanding card check M2 was judged (below) |

No conflict in any merge. `athenak/src/CMakeLists.txt` (three new sources of two
branches), `docs/FORMATS.md` (section `bst1` appended) and `tracks/core/CHANGELOG.md`
were merged by git and read afterwards; `z4c.hpp`, `driver.cpp` and `main.cpp` are
touched by core/step-limit alone, `z4c_gauge_ext.hpp` by core/gauge-2 alone. Review
notes of every branch: the journal entry and the four merge commit messages. Points of
the review:

- **core/clump-table, why it is taken.** Its READY of 2026-11-21 named one check as
  outstanding: M2, the 50 M run of a moving cluster with the card build of its merged
  source against the same run of the build before its merge. The run (Slurm 4803,
  core-20261121-132629-47ccb97) had ended with status 0 on 2026-11-21 and nobody had
  judged it. Judged now with the branch's script and the branch's prediction (run
  core-20261125-021225-382dbc7): at all 401 common records to 50 M the minimum lapse
  agrees within 3.3e-15, sum m u_x within 2.2e-16, sum m W within 1.1e-15, particle
  number and constraint norms in every printed digit. Prediction M2 held (bound 1e-9);
  my own expectation that the bound might fail because card runs with deposition do not
  repeat was wrong for this pair. Figure `fig_compare_two_runs.png` of that run (looked
  at: differences between 1e-17 and 4e-15; the legend of the left panel lies over the
  curves). The branch holds core-v0.5, not core-v0.6: its three source files do not
  overlap with core-v0.6's changes, and its example under `id_solve` now gets the far
  field of core-v0.6 (changelog, item 4 of "without an option").
- **core/step-limit, what acts for every run.** `GaugeStepLimit` evaluates the bound
  once at the first cycle and writes the step only with `dt_gauge > 0`; the SIGTERM
  handler sets a flag that the driver reads as the last condition of its loop
  [VERIFIED by reading `z4c_newdt_gauge.cpp` 310-345, `term_signal.cpp`, `driver.cpp`
  568, 689, 702, `main.cpp` 128, 435]. The regression below is the test that neither changes a file.
- **core/gauge-2 and core/noise-level2, recompiled kernels.** Both add a branch or
  members to a kernel whose released path keeps its arithmetic (`AddGaugeExt`,
  `NoiseSynthesize`). Whether the compiler then writes the same bytes is what the tests
  say: g_leak of the quick test (the first pass of `lapse_leak`, 9 of 9 files identical
  with release core-v0.6) and the package's regressions of the branch build (13 scalar-field cases with restarts
  and the twelve set-ups, runs core-20261124-142019-4e1c3a5 and
  core-20261124-142032-79291d0; not rerun by me beyond the twelve set-ups).

## Branch left out

core/oblate: not ready (tip 4f01a81f of 2026-11-20; it holds neither core-v0.5 nor a
READY for a merged state). No branch that was offered closed is left out.

## Byte regression on processors against release core-v0.6: PASS

Run core-20261125-023046-30aba6c (driver `tracks/core/analysis/release/regress_v04.py`,
3 cores). Candidate `athena_cpu` (sha256 53e60576...) against the release executable
`/data/haiyangw/nrpic/.work/build_cpu_v06/src/athena`, the twelve set-ups of wave 1,
every new option absent. Every output file except the log is compared; for jeans and
binary the result lines of the log as well. Classes as in `RELEASE-v0.4.md` (a: 36 unset
restart bytes; b: `last_time` lines of an embedded parameter dump); neither appears.
Prediction R held.

| Set-up | What | Items | identical | a | b | a+b | other | Verdict |
|---|---|---|---|---|---|---|---|---|
| geo | test particle in Kerr, analytic metric, midpoint | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| boris | the same, spacetime-Boris pusher on the lattice | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| dep | deposit on a statically refined flat mesh | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| east | periodic cosmology with Z4c, 16^3, 20 steps | 12 | 12 | 0 | 0 | 0 | 0 | pass |
| os | Oppenheimer-Snyder ball with Z4c, refined, 3 steps | 16 | 16 | 0 | 0 | 0 | 0 | pass |
| jeans | gas with self-gravity, Jeans wave, 20 steps | 5 | 5 | 0 | 0 | 0 | 0 | pass |
| binary | gas with self-gravity, four levels, 1 step | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| c1 | cluster on the analytic Kerr metric, 2000 particles | 5 | 5 | 0 | 0 | 0 | 0 | pass |
| c2 | static mesh metric, deposit, filter | 3 | 3 | 0 | 0 | 0 | 0 | pass |
| c3 | cluster on a refined mesh, deposit, excision | 14 | 14 | 0 | 0 | 0 | 0 | pass |
| c4 | homogeneous universe, Z4c with particle sources | 4 | 4 | 0 | 0 | 0 | 0 | pass |
| c5 | kick deck with the kick off: restart files, removal | 10 | 10 | 0 | 0 | 0 | 0 | pass |
| all | | 75 | 75 | 0 | 0 | 0 | 0 | PASS |

Figure: run core-20261125-030148-94dcc0b (`fig_regress_v04.png`, looked at: twelve bars,
one colour).

**Which files differ because of the changes that act without an option: none.** The
three such changes (changelog) and where they could have shown:
- the stop on SIGTERM: no signal is sent in the regression, and no file differs (the
  prediction of decision 0035 item 3 and of the journal);
- the start-up warning of the step limit: it goes to the log of every Z4c run with rk3
  or rk4 whose `cfl_number` allows a step above the bound; the log is not a compared
  file, and its result lines, compared for jeans and binary, are of runs without Z4c;
- `noise_level = 2` now runs: no regression set-up sets it.
So against core-v0.6 the candidate differs, with the new options absent, in the log
only. (What differs with a signal: the run ends with status 143 and leaves one more
restart file; continued from it, every output is byte-identical with the uninterrupted
run except the two files of the restart defects a and b of OPEN.md, quick test below.)

The other two processor builds against the same release executable, same driver:

| Build | Run | Result |
|---|---|---|
| `athena_cpu_mpi` started without mpirun | core-20261125-023646-eca713c | 75 of 75 items identical: PASS (prediction Rm held) |
| `athena_cpu_omp` at one thread | core-20261125-025505-10f6611, judged in core-20261125-030151-8c0c306 | every run status 0; 32 of 75 identical, 43 differ at rounding level: NOT a byte reference (prediction Ro held) |

For the threaded build, columns above 1e-6 of the largest column of each history: module
histories within 1.2e-15, constraint statistics within 1.1e-10 (east) and 6.0e-12 (c4);
geo, boris, dep, os, c1, c2, c3 without a difference in their large columns; the history of
c5 has one entry per record that is not finite in both builds and agrees in all others.
core-v0.6 had 32 of 75 and 1.2e-15, 1.4e-10, 1.9e-12: the threaded build of this
candidate does not write the bytes of the threaded build of core-v0.6 either, which no
test asks of it. Figure `scratch/core/core-20261125-030151-8c0c306/fig_hst_pair.png`
(looked at: four bars, east and c4; every other history at zero).

## Quick test of every merged branch on processors: PASS

Run core-20261125-023641-7a1c47d (driver `analysis/release/quick_v07.py`, 3 cores, 14
AthenaK runs and two test scripts). One example per branch, serial candidate against the
processor executable the branch published, byte for byte:

| Case | Branch | Input | Against | Files | identical |
|---|---|---|---|---|---|
| n_l2 | noise-level2 | `problems/scalar/sr_stochastic_l2.athinput` (32^3, level 2, every option of the branch written out), 24 cycles | `core_noise-level2/athena_cpu` | 8 | 8 |
| s_lim | step-limit | `problems/tests/z4c_step_limit.athinput` as written (`dt_gauge = 0.9`) | `core_step-limit/athena_cpu` | 33 | 33 |
| g_hole | gauge-2 | `analysis/gauge2/inputs/v8_var.athinput` without refinement (64^3 cells of 2 M, 10 M), `lapse_leak = 0.5`, `lapse_leak_hole = 8` | `core_gauge-2/athena_cpu` | 9 | 9 |
| g_leak | gauge-2 | the same with `lapse_leak_hole = 0` (the first pass) | release core-v0.6 | 9 | 9 |
| c_static | clump-table | `problems/tests/clump_table_static.athinput` at 32 cells, v = 0.3, curvature and correction (initial data) | `core_clump-table/athena_cpu` | 6 | 6 |
| all | | | | 65 | 65 |

Predictions Qn, Qs (i), Qg (i) and (ii), Qc held. The other expectations of the run, all
held (panel b of the figure):

| Check | Prediction | Result |
|---|---|---|
| s_lim, log | Qs (i) | "the step of Z4c is set by dt_gauge, sector lapse: 0.131605" (0.421 cells = 0.9 x 0.468; bounds at the start 0.624 shift, 0.468 lapse, 0.551 light) |
| s_off: the same with `dt_gauge = 0` | Qs (ii) | the warning ("cfl_number x (smallest cell) = 0.3125 exceeds the stability bound 0.146228 ... Set <z4c> dt_gauge = 0.9, or cfl_number at or below 0.421136"), guard stop at cycle 9, exit status 3 |
| SIGTERM, `analysis/preempt/term_test.py` cases S1 (Z4c, periodic) and S2 (particles with Z4c) | Qs (iii) | 26 checks held: status 143, "Terminating on signal SIGTERM", one more restart file 0.28 s and 0.35 s after the signal, continuation to the end, last restart file and `.prt` identical in their data; 27 and 21 output files compared, all identical but `*.z4c.user.hst` (header lines 2 against 4, data lines identical) and, in S2, `tsq.cons.hst` (the record at t = 1.6875 missing in the continued run): the two restart defects of OPEN.md, items a and b |
| g_hole against g_leak | Qg (iii) | 7 of 9 files differ: the weight acts |
| c_solve: `clump_table_idsolve.athinput` at 32 cells, candidate only | Qc | status 0; 25 outer iterations, max\|H\| 1.72e-3 to 1.99e-12 (far field of core-v0.6 on; no byte comparison) |
| x_l2dt: n_l2 with `<z4c> dt_gauge = 0.9` | C | status 0; both histories byte-identical with n_l2 (the limit never sets the step); with geodesic slicing and zero shift only the sector "light" has a bound (0.575 cells), the other two print 1.7e+39 (cosmetic, OPEN.md item e) |
| x_holedt: g_hole with `dt_gauge = 0.9` | C | status 0, histories finite; bounds at the start 0.561 (shift), 0.443 (lapse), 0.551 (light) cells at `cfl_number` 0.25: the limit never sets the step |
| chain script, `scripts/tests/test_submit_chain.py` | T | TEST PASS, 58 checks |

Figure `scratch/core/core-20261125-023641-7a1c47d/fig_quick_v07.png` (looked at: panel a
five blue bars with no red showing; panel b 28 expectations, all blue; the labels of
panel b are crowded at this size).

## Card checks (judged 2026-11-26, batch 27)

**K7 HELD: CARD PASS.** q0039 ran as job 5355, run core-20261126-045719-019b478 (22 cases,
every status 0; closed 2026-11-26). Judged by three registered analyses, figures looked at:
core-20261126-115658-8af7dd7 (`card_v07.py`, the seven new cases: level-2 histories within
6.3e-13 of the processors, bound 1e-9; step-limit example identical, 0.0; gauge and
table-cluster cases within 5.3e-14, bound 1e-7; constraint means of the scalar field 6.8e-4,
reported and not bounded), core-20261126-115708-140bafa (`card_v06.py`, six cases of
core-v0.6: Newtonian histories within 2e-11, the solves with the same outer iterations,
the faces cases held; the normalized constraint column of g_smr1 8.8e-4, reported and not
bounded) and core-20261126-115725-9a8d381 (`card_v05.py`, nine cases of core-v0.5: K1 to K6
held). So the card executable of core-v0.7 (`scratch/core/exe/core_nrpic_v07/athena_gpu`)
agrees with its processor build on every case the release record names.

## Card checks pending (as written at tagging; outcomes above and in the branch table)

The cards have been held by another partition for two days (decision 0035 item 4):
nothing of this session ran on a card, and nothing was waited for.

**Merged card executable `athena_gpu` (prediction K7): PENDING, queue entry q0039**
(`core-v07-card`, priority 2, one entry, 0.3 card-hours asked; list
`analysis/release/card_v07.list`, 22 cases: seven new ones with the decks of the quick
test, n_l2, x_l2dt, s_lim, g_hole, x_holedt, c_static, c_solve, and the fifteen of
core-v0.6). The run id is the field `run` of `harness/bin/nrpic-queue show q0039` once
the dispatcher has submitted it. Judge it, from `/data/haiyangw/nrpic/wt/core`, with
(`<K7>` = that run id; `S=/data/haiyangw/nrpic/scratch/core`):
```
harness/bin/nrpic-run finish <K7>
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, new cases" -- python3 tracks/core/analysis/release/card_v07.py --card $S/<K7> --quick $S/core-20261125-023641-7a1c47d --out '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, six cases of core-v0.6" -- python3 tracks/core/analysis/release/card_v06.py --card $S/<K7> --quick $S/core-20261121-130813-710b3cc --r2 $S/core-20261121-131250-f8df905 --out '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, nine cases of core-v0.5" -- python3 tracks/core/analysis/release/card_v05.py --card $S/<K7> --cpu $S/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'
```
Each prints `CARD PASS` or `CARD FAIL` and exits with status 0 or 1. K7 holds if all
three print PASS: every case status 0; level-2 history `sr.sf.hst` and the per-mode
records within 1e-9 of the processor run; the step-limit example with the same number of
records and its history within 1e-3 (it measures noise of 1e-10 of the fields); the
gauge and table-cluster cases within 1e-7 in `*.nrpic.hst` and `*.z4c.user.hst`; the
solve of c_solve with the same 25 outer iterations and psi_max to 1e-12; the fifteen
older cases as K6 of core-v0.6 (their processor data are those of the core-v0.6
candidate, with which this candidate is byte-identical where the regression compares).
Reported and not bounded, as for core-v0.6: constraint means of the scalar-field runs
(`sr.sf.con.hst`) and the normalized constraint columns of `*.cstat.hst`. `card_v07.py`
was tried by hand on processor data in place of card data (it prints CARD PASS there,
which says nothing about the card) and with the first-pass run in place of g_hole (CARD
FAIL at 8.8e-2).

**Card runs of the branch builds** (the same source per capability):

| Branch | Card run | State |
|---|---|---|
| core/noise-level2 (64f150ec) | R5, queue entry q0035 (`nl2-review-R5`): the two 64^3 level-2 decks against Track E's smoke runs of the build before the review, cost of a cycle at 256^3 | PENDING; judged by the package (`tracks/core/verify/noise_level2_close/README.md`, `tracks/core/JOURNAL-noise-level2.md` entry 17). The card build of the source before the review passed Track E's smoke check and made six ablation runs |
| core/step-limit (5c4b644f) | queue entry q0036 (`step-limit-card`): Track A's refined periodic deck at `cfl_number` 1.0 without and with `dt_gauge`, and at 0.5 | **ran 2026-11-26** (job 5368, run core-20261126-080805-3a9a349), judged by core-20261126-121103-1070457: P4a, P4c held; P4b held in its test (step at most 0.577 cells, no jump, t = 6 reached, |H| at t = 6 equal to the run at 0.5) and failed in its time (the option takes over at t = 1.18, predicted 1.5 to 1.8), as on processors (`JOURNAL-step-limit.md` entry 17) |
| core/gauge-2 (984110c3) | job F, run core-20261121-190709-8b205e5 | ran (2026-11-21): the 200 M vacuum run with the option, exit 0; numbers in OPEN.md item c |
| core/clump-table (7cc6c7b9) | M2, run core-20261121-132629-47ccb97 (Slurm 4803) | ran (2026-11-21), judged in core-20261125-021225-382dbc7: held (above) |

## Release builds against the candidate (batch 17, 2026-11-25)

The clerk built `.work/build_cpu_v07` and `.work/build_gpu_v07` from main after the merge
b399f946 (tag core-v0.7 on 5f75e5b9; `git diff 5f75e5b9 b399f946 -- athenak/src
python/nrpic problems scripts` is empty [VERIFIED]). Checksums differ from the candidate's,
as builds in other directories do (orch outbox 20261125T033027Z). Prediction R7: journal
entry 2026-11-25T11:52Z.

| Check | Run | Result |
|---|---|---|
| `.work/build_cpu_v07/src/athena` against the candidate `athena_cpu`, `regress_v04.py`, twelve set-ups, 3 cores | core-20261125-115428-3670218 (figure core-20261125-120456-07a671a) | 75 of 75 items identical, classes a, b, other empty: REGRESSION PASS (R7 held). Figure `fig_regress_v04.png` looked at: twelve bars, one colour |
| `.work/build_gpu_v07/src/athena` | none | NOT DONE: a CUDA build does not run on processors. Same source tree as the candidate (above). Its card check is not queued: the list `card_v07.list` of q0039 can run it later (`ATHENA_EXE` of the batch), as G6 did for core-v0.6 |

## Known defects

`tracks/core/stage/G2/OPEN.md`, section of core-v0.7, items a to l; the READY of the
published executables. In short:
- two older restart defects found by package step-limit, also in core-v0.6: a record of
  `<basename>.cons.hst` is lost when a run continues from a restart file written one or
  two cycles before the record is due; the mesh history file gets its header lines
  again at every continuation. The state of the run is exact;
- `lapse_leak_hole` is a mitigation: with r_h = 16 M the shrinking of the horizon in
  the coordinates is delayed by about 100 M at cells of M/8 and not stopped; the level
  of plain 1+log is not reached;
- level 2 of the stochastic backreaction does not support refined meshes (the run
  stops) or several ranks (the scalar field refuses them), and is not tested with a
  lapse that varies in space or with a shift;
- `dt_gauge` is off when absent and not tested with punctures, horizons, adaptive
  refinement or several ranks;
- the stop on SIGTERM is tested on one rank on processors only, never under a real
  preemption;
- the merged card executable has not run on a card (q0039);
- the capability tests of the packages and the verification ladder were not rerun on
  the merged executables: the release rests on the byte regression, on one example per
  branch against the branch's own executable, and on the packages' tests.

## For the release clerk

Merge `core/nrpic` into main; tag `core-v0.7` (the source commit of the first line, or
the merge on main: compare the source trees); build `.work/build_gpu_v07` and
`.work/build_cpu_v07` from that source, and if wanted the threaded and the MPI builds;
copy `tracks/core/interfaces/*.md` to `coord/INTERFACES/` (new since core-v0.6:
`noise_level2.md`, `step_limit.md`, `preempted_runs.md`, `moving_clusters.md`; changed:
`cosmo_gauge.md` section 9). Announce to all owners: the stop on SIGTERM and the chain
script (use the script of main with executables of core-v0.7: changelog, run scripts,
item 5); `dt_gauge = 0.9` for Track A; `lapse_leak_hole` as a mitigation for Track D;
level 2 for Track E; `shift_eta` of 0.03/M to 0.1/M for moving table clusters (Track F).
The text core/step-limit proposes for CLAUDE.md: its outbox message
`*__to-orch__step-limit-and-preempt-for-v07.md`. Compare a release build with the
candidate by `regress_v04.py`, not by checksums. The card check q0039 uses the
candidate's `athena_gpu`; a release card build can be checked with the same list.

How to repeat the processor checks:
```
cd /data/haiyangw/nrpic/wt/core
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 3
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/quick_v07.py --new <athena_cpu> --base /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena --out '$NRPIC_RUN_DIR' --cores 3
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "..." -- python3 tracks/core/analysis/release/hst_pair_v06.py <regression run directory of the threaded build> --out '$NRPIC_RUN_DIR'
```
