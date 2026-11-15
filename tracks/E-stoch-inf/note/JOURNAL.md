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
