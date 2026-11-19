# box_tests: box tests of the collision operator (release core-v0.3; wave 2b: core/collisions-2)

Wave 2b (2026-11-19) reran T0b, T1, T2, T10 and the new T12 with core's corrected operator
(`coll_energy = particle`) and measured what it leaves of the King model's energy defect:
section "Wave 2b" below; everything else in this file is the wave-2 state.

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
| `inputs/box_c2.athinput` | wave 2b: `box.athinput` plus `coll_energy` (a command line may only override parameters the deck has) |
| `inputs/box_static.athinput` | wave 2b, T12: the same box in the static homogeneous metric alpha0 = 0.8, psi0 = 1.1 (`static_conformal`, mesh metric) |
| `inputs/king_cc1.athinput` | wave 2b: threshold_scan's `cc1_kn1.athinput` plus `coll_energy` |
| `scripts/t12.py` | wave 2b: T12 in the curved box, against its flat twin (same particles at proper positions, step alpha0 dt) and the analytic rate |
| `scripts/king_defect.py` | wave 2b: first-step energy defect of the King threshold model in both modes, from coll.hst and recomputed from the version-2 dump per collision cell |
| `scripts/compare_modes.py` | wave 2b: one collision step of `coll_energy = particle` against the option absent, from two T0b dumps |
| `scripts/timing.py` | wave 2b: cost of `particle` against `cell` and no collisions under equal load |
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
| T2 rate | PASS 16/16 | C-20261115-165500-c67e036 | theta 1e-3 to 10, plain and sub-cycled: (a) z in [-2.1, 1.6]; (b) ratio 0.99991-1.00010, z in [-2.2, 2.9]; (c) exact | `figs/t2_rate_cpu.png`, `figs/t1t2_summary_cpu.png` |
| T3 relaxation | PASS 4/4 | C-20261115-170539-28432c3 | KS p 0.084-0.99 at 15 tau_rel; <u^2/W>/3 = theta_eq within 0.01 se; populations at theta_eq within the 4 se criterion (about 1 se or less by an estimate of the se) | `figs/relax_T345_*.png` |
| T4 initial rate | PASS 4/4 | C-20261115-170539-28432c3 | slope/exact 0.9924, 0.9792 (theta_2 = 1e-3), 0.9959, 1.0088 (theta_2 = 1); se 0.3-0.6 percent | `figs/t4_zoom_cpu.png` |
| T5 entropy | PASS 4/4 | C-20261115-170539-28432c3 | s(0) = s_mix within 0.25 se, s(end) = s_MJ within 0.03 se; monotone | `figs/relax_T345_*.png` |
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

## Wave 2b (2026-11-19): rerun with core's corrected operator

Executable: core's processor build of branch `core/collisions-2`
(`/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_cpu`, commit f46f159,
READY in that directory), option `<particles> coll_energy = cell | particle`
(`git show core/collisions-2:tracks/core/interfaces/collisions.md`, sections 5 and 11).
Criteria: `../collide/TESTS.md` (wave 1) and its section 2a (wave 2), unchanged.
Predictions R1-R6 and every outcome, failed ones included: `JOURNAL.md`, section "Wave
2b". No card time used.

Rerun (from the worktree root; `X=/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_cpu`,
`D` as above, `S=/data/haiyangw/nrpic/scratch/C-sidm`; each with
`harness/bin/nrpic-run submit --kind scouting --gate G1|G2 --package tracks/C-sidm/box_tests --cores N --purpose ... --`):

    python3 tracks/C-sidm/box_tests/scripts/t0b.py $D --exe $X --tag c2off --ref $S/C-20261115-170155-13ff01f
    python3 tracks/C-sidm/box_tests/scripts/t0b.py $D --exe $X --tag c2particle \
        --deck tracks/C-sidm/box_tests/inputs/box_c2.athinput --set particles/coll_energy=particle
    python3 tracks/C-sidm/box_tests/scripts/compare_modes.py <R1 run dir> <R2 run dir>
    python3 tracks/C-sidm/box_tests/scripts/t1t2.py $D --nproc 8 --exe $X --tag c2particle \
        --deck tracks/C-sidm/box_tests/inputs/box_c2.athinput --set particles/coll_energy=particle \
        --ref $S/C-20261115-165500-c67e036
    python3 tracks/C-sidm/box_tests/scripts/t10.py --exe $X --tag c2particle \
        --deck tracks/C-sidm/box_tests/inputs/box_c2.athinput --set particles/coll_energy=particle
    python3 tracks/C-sidm/box_tests/scripts/t12.py $D --nproc 8          # 25 min per curved run
    python3 tracks/C-sidm/box_tests/scripts/king_defect.py --nproc 6     # 6 min per run
    python3 tracks/C-sidm/box_tests/scripts/timing.py $D
    (t12.py and king_defect.py take --from <run dir> to re-analyse without running AthenaK)

| Test | Verdict | Run id | Key numbers | Figure |
|---|---|---|---|---|
| R1 T0b, option absent | PASS 6/6 | C-20261119-141502-95f0200 | every output file byte-identical to the release run C-20261115-170155-13ff01f | `figs/t0b_replay_c2off.png` |
| R2 T0b, `particle` (flat) | PASS 6/6 | C-20261119-141711-7db7a6a (first attempt -141614-e42b5ec failed: relative deck path) | dump version 2, metric at the particles exactly flat; cell-frame replay: same pairs and collisions, momenta to 4.4e-16; n_noroot = n_balance = 0, lam = 1 exactly | `figs/t0b_replay_c2particle.png` |
| R2b modes compared | done | C-20261119-141854-b2b664d | against the option absent: same particles updated, momenta within 7.8e-16 of max(1, \|u\|) after 21 steps | `figs/compare_modes_c2.png` |
| R3 T1, T2 (`particle`) | PASS 16/16 + 16/16 | C-20261119-141806-af19c1c | n_tested, n_coll, max_nsub identical to the release run in all 3200 steps; T2 z values equal to wave 2; T1 within 1.1e-7 of the bound; final momenta within 1.4e-14; positions within 200 ulp (failed clause of my prediction, rounding) | `figs/t2_rate_c2particle.png`, `figs/t1_step_c2particle.png`, `figs/paired_c2particle.png` |
| R3(v') cost | measured (prediction failed) | C-20261119-143146-226b0e0 | collision part of `particle` 1.68 times that of `cell` in the flat box (1.89e-6 against 1.13e-6 s per tested pair on a loaded core); whole run 1.40 | none (numbers in `results/timing_*.json`) |
| R4 T10 (`particle`) | PASS | C-20261119-143041-f94e350 | MeshBlocks 1, 8, 64 and restarts bit-identical; seed differs; 385554 collisions as in the release run | `figs/t10_repro_c2particle.png` |
| R5 T12 (curved, `particle`) | PASS 4/4 | C-20261119-143049-0cf699a (AthenaK; driver stopped at the figure), C-20261119-145925-dbcfb9c (analysis) | alpha0 = 0.8, psi0 = 1.1: rate per coordinate time and volume / flat twin = alpha0 psi0^6 = 1.41725 exactly (identical counts in every step); analytic rate 0.99997-1.00009 (\|z\| <= 2.4); T1 within 3.6e-7 of the bound; `cell` = `particle` in the homogeneous metric | `figs/t12_c2.png` |
| R6 King threshold model | measured | C-20261119-141431-a351ac7 (runs), C-20261119-142957-c5da7d0 (figure) | step 1 per collision: cell mode +8.0(3.4)e-11 of sum M W_p and +1.11(0.47)e-10 M of sum M H_p at Kn = 0.01 (predicted 1.74e-10 and 2.40e-10 M); `particle`: d sum M H_p = +1.5-1.9e-21 M per collision (rounding; 1e-11 of the old defect), per step <= 4.5e-17 of the sum against 3.9e-6; d sum M W_p -1.7(2.4)e-11 (zero); n_noroot 0, n_balance <= 2.7e-4 | `figs/king_defect_c2.png` |

Findings of wave 2b:
- With the option absent the new executable is the release (R1, bytes); with
  `coll_energy = particle` in a flat box it takes exactly the collisions of the release
  and differs in the last bits of the momenta only (R2, R3); T10 holds.
- T12 passes: the collision rate in the static homogeneous metric is alpha0 psi0^6 times
  the flat value per coordinate time and volume; this closes the T12 item left open in
  wave 2 (G2 criterion "budgets of conserved quantities close in curved spacetime", for
  this homogeneous case and, for the collision step alone, in the King model).
- In the King threshold model the new option removes the first-step energy defect: the
  canonical energy is conserved to a systematic +1.7e-21 of its sum per collision (about
  half of the 16-ulp stopping tolerance of the energy root), against +1.3(0.5)e-10 with the
  core-v0.3 operator. The deposited energy sum M W_p shows no mean change (it is not
  conserved by design).
- The cell-mode defect measured here (+8.0(3.4)e-11 per collision at Kn = 0.01) is
  0.46 of the pair-model prediction of threshold_scan (2.8 se low); the card runs of wave 2
  were low too (factor 0.70). Not explained.
- Cost: `particle` makes the collision step 1.7 times as expensive on the processor in a
  flat box; the curved mesh-metric runs of T12 took 4.4-5.3 times as long as the flat twins
  (push with Hermite reconstruction and coll_budget).
- Trap: AthenaK accepts on the command line only parameters the deck has; the reruns use
  decks that carry `coll_energy` (`inputs/box_c2.athinput`, `inputs/king_cc1.athinput`).

Not done in wave 2b: card runs (the card executable of core/collisions-2 was not used;
its `CARD_TESTS.log` lists FAIL lines of parts R against the release card executable,
which core's own analysis has to settle); T3-T5, T9, T11 with the option (their
statistics follow from identical collisions in the flat box, R3, but were not rerun);
T12 with a modulated metric (core's tests G1-G4 cover it; the track has not checked them
independently); the King measurement beyond two steps.

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

Wave 2b (2026-11-19):

To core (branch `core/collisions-2`):
- Informational: with `coll_energy = particle` the canonical energy of a pair is not
  conserved to zero mean but to +1.5-1.9e-21 M per collision in the King model (about
  half of the 16-ulp tolerance, always positive; run C-20261119-141431-a351ac7). Harmless
  (2e-15 of sum M H over 300 M at Kn = 1); one more Newton step after the tolerance is met,
  or a symmetric stopping rule, would remove the bias if it ever matters.
- READY: say that `coll_energy` must be in the input file to be set on the command line
  (only parameters the deck has can be overridden), and that the cost of the collision
  step with `particle` is about 1.7 times that of `cell` on the processor (run
  C-20261119-143146-226b0e0); collisions.md 11.5 says "about the same time" in a run
  dominated by the push.
- The card executable: settle the FAIL lines of `CARD_TESTS.log` (parts R against the
  release card executable) before tracks use it for card runs with collisions.

To the lead of C-sidm:
- Use `coll_energy = particle` for every cluster run with collisions: the core-v0.3
  defect (+1.1(0.5)e-10 M of Killing energy per collision at the start, run
  C-20261119-141431-a351ac7; threshold_scan: 1.6-1.7e-3 of
  sum M W before the collapse at Kn = 1) is gone at the collision step.
- The threshold_scan conclusion "both King models collapse with collisions" was obtained
  with the defect; rerunning CC1/CC2 at Kn = 10 and 1 with `particle` (about 1.2 card-hours:
  the four collisional runs of wave 2's 1.73) decides whether the defect mattered; that needs card time and the
  card executable cleared by core.
- T12 now passes; TESTS.md could name the twin comparison (identical counts) as the sharp
  form of the T12 criterion.

To orch: none from this package (wave 2b).

To orch (wave 2): none from this package. The harness worked (nrpic-run registered every run;
three submissions were refused by the owner's 16-core allotment and resubmitted with
fewer cores; with output redirected, the "registered" line of a local run appears only
when the run ends).
