# Package g3 (Track E, gate G3): tail statistics of the curvature perturbation

Scope and criteria: `../spec/scope/SCOPE.md` section 4d, written in batch 17 before any G3 run
(decision 0038 item 2). Predictions: `JOURNAL.md` (entry 1 power estimate, entry 2 G3 and pilot).

| Path | What |
|---|---|
| `power.py` | power estimate: Gaussian fields with the 128^3 USR spectrum, box-to-box scatter of the exceedance fractions, seeds needed (run E-20261125-115822-29795d6) |
| `inputs/pilot.list` | the pilot: one batch job, ten baseline seeds, two kdriver, two level 2 (queue label G3P) |

Reference: `../langevin/` (one-patch delta N; 128^3 band pilot run E-20261125-115707-b845282,
`results/ref_inflection_n32.json`).

Runs:

| Label | What | Queue | Run | Card-h |
|---|---|---|---|---|
| G3P | pilot, 14 runs at 128^3 on build_gpu_v07 | see HANDOFF | pending | - |

Still to write before the full set: the reader (R^NR from `ladder_lib`, zeta to the uniform-field
surface, exceedance fractions per seed) with its two processor tests (SCOPE 4d.1).
