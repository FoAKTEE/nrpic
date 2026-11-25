# Package g3 (Track E, gate G3): tail statistics of the curvature perturbation

Scope and criteria: `../spec/scope/SCOPE.md` section 4d, written in batch 17 before any G3 run
(decision 0038 item 2). Predictions: `JOURNAL.md` (entry 1 power estimate, entry 2 G3 and pilot).

| Path | What |
|---|---|
| `power.py` | power estimate: Gaussian fields with the 128^3 USR spectrum, box-to-box scatter of the exceedance fractions, seeds needed (run E-20261125-115822-29795d6) |
| `read_seed.py` | per-seed reader, variable (i) R^NR: sigma against sigma_lin, exceedance fractions, histogram; tested on existing USR output (run E-20261125-120930-980b18e, JOURNAL entry 3) |
| `inputs/pilot.list` | the pilot: one batch job, ten baseline seeds, two kdriver, two level 2 (queue label G3P) |

Reference: `../langevin/` (one-patch delta N; 128^3 band pilot run E-20261125-115707-b845282,
`results/ref_inflection_n32.json`).

Runs:

| Label | What | Queue | Run | Card-h |
|---|---|---|---|---|
| G3P | pilot, 14 runs at 128^3 on build_gpu_v07 | see HANDOFF | pending | - |

Still to write before the full set: zeta (delta N to the uniform-field surface) in the reader, with
its two processor tests (SCOPE 4d.1). R^NR is Gaussian to one-box precision (entry 3).
