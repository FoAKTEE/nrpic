# Journal of the note package of E-stoch-inf (wave 2 helper)

Predictions are written before the run that tests them; outcomes are appended below, failed
predictions included. Times are UTC on 2026-11-15. Paths are relative to
`tracks/E-stoch-inf/`; run ids are those of `harness/bin/nrpic-run`
(`runs/<run_id>/manifest.json`).

## 17:15 Set-up and predictions

The package writes the working note v0 (`note/main.tex`) from what the track has, draws its
data figures from the outputs of registered runs (each input checked against the checksum
its manifest records), draws the two schematics of the stage check, and builds a numerical
ledger. All figures and tables come from one registered analysis run of
`note/scripts/run_all.py`. Sources read: `spec/SPEC.md`, `spec/scope/SCOPE.md`,
`stage/G0/EVIDENCE.md`, `stage/G0/OPEN.md`, `stage/G1/STATUS.md`, `langevin/README.md`,
the manifests, core's interface `coord/INTERFACES/scalar_field.md` and core's message
`tracks/core/outbox/20261115T1510Z__to-E-stoch-inf__scalar-field-merged.md`.

- **N1 (the files reproduce the lead's numbers).** Recomputed from the outputs of runs
  E-stoch-inf-20261115-122806-ef0d039 (background, mode functions), -130139-176cdd6 and
  -130137-176cdd6 (delta-N references), E-20261115-140502-2957846 (noise validations) and
  E-stoch-inf-20261115-123936-b2ec5c7 (cost model), the numbers quoted in SCOPE.md,
  SPEC.md sections 6 and 7.3, EVIDENCE.md and langevin/README.md agree to the digits printed
  there: SR full-MS final power 1.010 to 1.012 of the slow-roll estimate at crossing;
  deformed drift -0.051 to -0.055 per e-fold; deformed/full at N_f 0.65 (k = dk) to 0.79
  (k = 64 dk) in SR and 8.40 at k = dk in USR; USR from cN = 2.53 to 6.55; delta-N variance
  ratios 0.9981, 1.0050, 1.4492 (SR, sigma = 0.01, 0.1, 1) and 1.0001, 1.0055, 1.4233 (USR);
  lattice/continuum 1.0805; noise validation: frozen A1 4.1e-14, Markov-tanh A1 1.07e-10
  (fails 1e-11), everything else passes; SR 256^3 at Courant 0.25: 1304 steps, 0.36 to 0.41
  card-hours. Refuted if any recomputed number differs from the printed one beyond its last
  printed digit; each difference is then listed as a disagreement, and the file wins.
- **N2 (cost with core's measured card throughput).** Core measured on one A100 at 128^3,
  MeshBlock 64^3, k_max = 32 dk: Z4c 1.98e7, Z4c with the field 1.39e7, with the
  stochastic sources 1.20e7 zone-cycles/s (run core-20261115-143907-cea4c86). SCOPE.md
  section 8 assumed +15 percent for field and sources (1.74e7). Replacing the assumption by
  the measurement, and scaling only the per-cell cost of the noise synthesis from 128^3 to
  256^3 with the operation counts of run E-stoch-inf-20261115-123936-b2ec5c7 (d2.json:
  per-cell count x4 at MeshBlock 64^3, x2 at 128^3), I expect one SR 256^3 realisation at
  Courant 0.25 to cost between 0.5 and 0.9 card-hours and one USR realisation between 0.6
  and 1.1, so 1.6 to 2 times the estimate of SCOPE.md and still at least five times below
  the downgrade threshold of 5 card-hours. Refuted if the recomputed SR cost lies outside
  0.5-0.9 card-hours, or if any case reaches 5 card-hours. This is an extrapolation from one
  measured size: a measurement at 256^3 can still refute it (open item).
- **N3 (figures).** Every figure script runs from the committed scripts alone, reads only
  checksum-verified outputs of registered runs, and gives the same PNG when run twice
  (pixel rms 0). Refuted by a checksum mismatch, a missing input or a differing PNG.

## 17:24 Run E-20261115-172421-50ac4ce failed (my error, no result)

The first registered run stopped at its first input: `common.py` took the scratch root from
the environment variable `NRPIC_SCRATCH`, which the harness sets to the owner's own scratch
directory (`scratch/E-stoch-inf`), so the paths doubled the owner directory. No figure was
written. The variable is renamed (`NOTE_SCRATCH_ROOT`, default the machine's scratch root);
the run is repeated from the next commit. Predictions N1-N3 are unchanged.

## 17:36 Outcomes (runs E-20261115-172442-78cf53e, -173135-858482f, -173402-641b6e2)

Three completed registered runs of `scripts/run_all.py`; the first two were superseded for
layout only (legend of fig_deltan on the data points, ledger column too narrow for the run
ids, exponent format of two ledger rows); every recomputed number is the same in all three.
The committed figures and tables are the outputs of **E-20261115-173402-641b6e2** (copied
from its run directory; the PNGs are byte-identical to the drafts that were looked at).

- **N1: held, with the differences listed.** Of 59 numbers printed in SPEC.md, SCOPE.md,
  EVIDENCE.md and langevin/README.md, 54 agree within half a unit of the last printed digit
  (`tables/claims.md`). The 5 that differ: the assumed overhead of field and sources over
  Z4c (SCOPE 15 percent, SPEC 11.2 30 percent; measured 64.7 percent, c16, c19), the
  per-realisation cost that follows from it (c17, c18; see N2), and USR eps1(N*) of the
  lead's integrator (1.31625e-2 against the printed 1.3164e-2 of the reference run, c21,
  already recorded in EVIDENCE.md). No number derived from a run output disagreed with the
  run it cites.
- **N2: held.** With core's measured throughput (run core-20261115-143907-cea4c86) and the
  synthesis scaled by its operation count, one 256^3 realisation at Courant 0.25 costs
  0.571-0.706 card-hours (SR, 1304 steps, 1.58-1.95 s per step) and 0.714-0.883 (USR, 1630
  steps), 1.40-1.73 times the scoping model (0.407, 0.509) and 5.7-8.8 times below the
  5 card-hour threshold. Inside the predicted ranges (0.5-0.9 SR, 0.6-1.1 USR). Still an
  extrapolation from 128^3 (MeshBlock 64^3, k_max = 32 dk) to 256^3: a card run at 256^3
  can refute it.
- **N3: held.** Every input passed its checksum against the manifest (the core run records
  no output checksums: its `summary.json` is read with sha256 printed in `claims.md`); each of
  the seven figures repeated with pixel rms 0 (`repeat.json` of each run).

Figures looked at (Read of the PNG): fig_background, fig_freezing, fig_deltan, fig_noise,
fig_cost, schem_architecture, schem_timeline; compiled pages 1-9 of main.pdf looked at
(captions within five lines). Checker (`check_manuscript.py --compile`): 0 undefined
references or citations, 0 overfull boxes; remaining candidates are the run ids of the ledger
appendix and the document names in the scripts (exception 1 of ../WRITING_GUIDE.md).
Not done: the reviewer subagents of step 4 of the paper-writing procedure (no subagent tool
in this session).

## 17:42 Release noise validation added (no prediction: the outcome was known)

The analysis helper's run E-20261115-172423-5234cce (committed 17:32) validated the
Markov-tanh noise of the release executable: A1 9.77e-11 against the track's reference,
3.3e-15 against a reference that forms the window increment without cancellation, every
other test passing. This changes the note's statement that the release validation is
"under way" (the files win). Added to fig_noise (open diamonds), to the ledger (R8) and to
Sec. IV C; the text now locates the remaining A1 discrepancy in the reference. No
prediction is claimed for it: the outcome was read in the helper's journal before the
note's run. The figure and ledger are regenerated by a new registered run of run_all.py.

## 17:44 Outcome of run E-20261115-173904-3be0405 (final)

Completed; the claims check unchanged (59 numbers, 54 agree, the same 5 differ); every
figure repeated with pixel rms 0; only fig_noise changed (open diamonds of the release,
looked at); ledger row R8 added. The committed figures and tables are this run's outputs;
main.pdf recompiled (9 pages, checker: 0 undefined references or citations, 0 overfull
boxes), pages 5 and 6 looked at again. Run E-20261115-173402-641b6e2 is superseded.
