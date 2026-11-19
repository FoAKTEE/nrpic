# Package faces: outer boundaries of the Z4c solver (core, wave 3a)

Branch `core/z4c-faces`. Journal (predictions before, outcomes after, run ids):
`tracks/core/JOURNAL-faces.md`. Interface text: `tracks/core/interfaces/z4c_faces.md`.
Source: `athenak/src/z4c/z4c_sbc_ext.hpp` (options), `z4c/z4c_bcs_falloff.cpp` (ghost
fill), `z4c/z4c_Sbc.cpp` (boundary operator, damping).

| Path | What |
|---|---|
| `inputs/ball.athinput`, `punc.athinput`, `punc_h.athinput` | the set-ups of the tests (ball, vacuum and boosted puncture, horizon proxy), faces at 16 |
| `inputs/*_ext.athinput` | the same with every option of the outer faces at its stock value, so that each can be set on the command line (AthenaK refuses command-line parameters the input does not have) |
| `inputs/drift_dx8_ext.athinput` | Track D's long vacuum-puncture input (`tracks/D-bh-dress/puncture_drift/inputs/drift_dx8.athinput`) with the options, to 345 M |
| `plans/*.json` | the cases of each test for `run_set.py`; `plans/card_*.list` the card runs |
| `run_set.py` | runs the cases of a plan on the processors (one core each), writes `cases.json` |
| `an_batch.sh`, `specs/*.txt` | runs a list of analyses as one registered run; outputs in the run directory, copied into `results/` and `figs/` |
| `flib.py` | reading of AthenaK binary dumps, region statistics, differences between runs |
| `analyze_a0.py`, `analyze_c0.py`, `analyze_c0b.py` | the monitor next to a face at t = 0 and after one step, by layer of cells |
| `analyze_evo.py` | residuals (H, M_i, Theta, Gamma constraint) by region against time; difference to a reference with the faces at 32; space-time diagram; front speeds |
| `analyze_summary.py` | the before/after figure of H in the interior and over the box |
| `analyze_drift.py` | the horizon mass of the card runs against Track D's run |
| `compare_runs.py` | byte comparison of the outputs of pairs of cases (regression) |
| `results/`, `figs/` | outputs of the registered analysis runs (copied from scratch) |

Rerun a test (from the worktree root, registered):

    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores N \
      --package tracks/core/analysis/faces/plans --purpose "..." \
      -- .venv/bin/python tracks/core/analysis/faces/run_set.py \
         tracks/core/analysis/faces/plans/<plan>.json --jobs N [--only case,case]
