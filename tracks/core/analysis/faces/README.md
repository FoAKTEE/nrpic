# Package faces: outer boundaries of the Z4c solver (core, waves 3a and 3)

Branch `core/z4c-faces`, closed 2026-11-21 at source commit f6f9a0d (contains release
core-v0.5). Journal (13 entries: predictions before, outcomes after, run ids):
`tracks/core/JOURNAL-faces.md`. Interface text with the options, the recommended
settings, what is tested and the table of results: `tracks/core/interfaces/z4c_faces.md`.
Executables: `/data/haiyangw/nrpic/scratch/core/exe/core_z4c-faces/` (READY).
Source: `athenak/src/z4c/z4c_sbc_ext.hpp` (options as data), `z4c/z4c_sbc_ext.cpp`
(reading them), `z4c/z4c_bcs_falloff.cpp` (ghost fill), `z4c/z4c_Sbc.cpp` (boundary
operator).

Result in three lines: the stock outflow faces make a constraint layer from the first
step and send an error inward; `ghost_falloff = true`, `extrap_order = 4`,
`sbc_variant = nonwave`, `sbc_speed = metric` keep the interior at the residual of a run
with the faces twice as far away until those are felt, and lower the whole-mesh mean |H|
3.5 (ball) to 34 times (vacuum puncture) at t = 8 (`figs/summary.png`). Without the
options every output is byte-identical with release core-v0.5 (test r2).

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
| `analyze_proxy.py` | horizon mass of the processor proxy of Track D's run (c3) |
| `compare_runs.py` | byte comparison of the outputs of pairs of cases (regression r1, r2) |
| `compare_data.py` | the same value for value, with a tolerance, for two executables whose file headers differ (m1) |
| `compare_objects.py` | machine code of two builds, object by object (histogram of instructions): finds a file that the compiler built differently although its source is unchanged (o1; journal entry 12) |
| `results/`, `figs/` | outputs of the registered analysis runs (copied from scratch) |

Rerun a test (from the worktree root, registered):

    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores N \
      --package tracks/core/analysis/faces/plans --purpose "..." \
      -- .venv/bin/python tracks/core/analysis/faces/run_set.py \
         tracks/core/analysis/faces/plans/<plan>.json --jobs N [--only case,case]

Tests and where their outcome is (journal entry): a0, a0b, a1, b1 (2 to 4, 7, 8): what
the stock faces do; c0, c0b (7, 8): the monitor after one step; c1, c2, c3, t1, D (10);
c4 (11, 13): damping in the boundary cells, removed; r1, o1 (12, 13): the failed byte
regression and its cause; r2, m1, t1b, s1, c5, summary (13). Plans that need the removed
options (`c4_damp.json`, `t1_smrface.json`) run only with the source and inputs of
commit cb50e22. Frozen executables of the stages (untracked, `.work/exe/`): base
(27b2ced), sbc1 (224b962), sbc2 (6cd9972), sbc3 (cb50e22), merge0 (c0ada84, merged, with
damping), sbc4 (ca6b46c), sbc5 (f6f9a0d: the delivered source).

Pending: the card check k1 of the delivered card executable, run
core-20261121-083511-2cff9df (Slurm job 4782); close it with `nrpic-run finish` and judge
it with `an_batch.sh k1.txt` (prediction in journal entry 12). Not submitted: k2
(`plans/card_k2.list`, the release card executable, for byte identity on a card).

