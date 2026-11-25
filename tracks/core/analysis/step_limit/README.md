# Package step-limit (core, batch 11): scripts, inputs, how to rerun

The step limit of Z4c and the gauge speeds, `<z4c> dt_gauge`. What it is, the derivation
and the results: `tracks/core/interfaces/step_limit.md`. Predictions before each test and
outcomes after, with run ids: `tracks/core/JOURNAL-step-limit.md`. Source:
`athenak/src/z4c/z4c_newdt_gauge.cpp` (new), hooks in `z4c_newdt.cpp`, `z4c.cpp`, `z4c.hpp`.

| File | What |
|---|---|
| `vonneumann_gauge.py` | reference computation (no simulation): symbols of the code's stencils, stability polynomials of the driver's schemes, scan of the Brillouin zone for the three pairs, Track A's model beside it (`--graddiv product --light scalar`), the reduced bound of the kernel (`reduced_bound`, twin of `PairBound`) against the scan |
| `run_flat.py` | T1/T2: flat space with noise (`problems/tests/z4c_step_limit.athinput`), each bound bracketed at 3 and 7 per cent by runs of the code; the kernel's printed bounds against the twin |
| `run_uniform.sh`, `inputs/diag_uniform.athinput` | T3: Track A's uniform-mesh reproducer without and with the option (copy of its deck, one line added) |
| `run_refined.sh`, `inputs/peak_leak.athinput`, `card_refined.list` | T4: Track A's refined periodic deck, on processors and as a card job (not submitted, see below) |
| `analyse_runs.py` | step against the finest cell, constraint statistics, lapse, cell-to-cell alternation on the line outputs of T3/T4 runs |
| `time_overhead.py` | T5a: cost of evaluating the bound every cycle |
| `survey_default.py` | T6b: the Z4c set-ups of the release regression with `dt_gauge = 1.0` against the same without |
| `publish_exe.sh`, `READY.md` | publication under `scratch/core/exe/core_step-limit/` (final builds of the package, both items; stage `exe`, then `ready`) |

Second item of the package (restart file on SIGTERM, chain script): `../preempt/`
(`term_test.py`, `final_build_check.py`), `scripts/tests/test_submit_chain.py`, interface
text `tracks/core/interfaces/preempted_runs.md`.

## How to rerun (from the worktree root; every run through `harness/bin/nrpic-run`)

```
P=tracks/core/analysis/step_limit
B=/data/haiyangw/nrpic/wt/core-s3/.work            # or scratch/core/exe/core_step-limit/athena_*
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local"
$R --cores 1 --purpose "T0" -- python $P/vonneumann_gauge.py --out '$NRPIC_RUN_DIR'
$R --cores 1 --purpose "T1/T2" -- python $P/run_flat.py --exe $B/build_cpu_sl/src/athena --out '$NRPIC_RUN_DIR' --workers 1
$R --cores 2 --purpose "T3" -- bash $P/run_uniform.sh '$NRPIC_RUN_DIR' 2 $B/build_omp_sl/src/athena G0 G0g
$R --cores 4 --purpose "T4" -- bash $P/run_refined.sh '$NRPIC_RUN_DIR' 4 $B/build_omp_sl/src/athena R0g
$R --cores 1 --purpose "analysis" -- python $P/analyse_runs.py --run G0=<dir>/G0 --run G0g=<dir>/G0g --out '$NRPIC_RUN_DIR' --name uniform
$R --cores 1 --purpose "T5a" -- python $P/time_overhead.py --exe $B/build_cpu_sl/src/athena --out '$NRPIC_RUN_DIR'
$R --cores 1 --purpose "T6a" -- python tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena --new $B/build_cpu_sl/src/athena --out '$NRPIC_RUN_DIR'
$R --cores 2 --purpose "T6b" -- python $P/survey_default.py --exe $B/build_cpu_sl/src/athena --out '$NRPIC_RUN_DIR' --cores 2
Q=tracks/core/analysis/preempt
$R --cores 1 --purpose "S" -- python $Q/term_test.py --exe $B/build_cpu_sl/src/athena --ref-exe /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena --out '$NRPIC_RUN_DIR'
$R --cores 1 --purpose "256 cells" -- python $Q/term_test.py --exe $B/build_cpu_sl/src/athena --big 256 --out '$NRPIC_RUN_DIR'
$R --cores 1 --purpose "chain" -- python scripts/tests/test_submit_chain.py --out '$NRPIC_RUN_DIR'
$R --cores 1 --purpose "F1" -- python $Q/final_build_check.py --old <build of 476fe0c> --new $B/build_cpu_sl/src/athena --out '$NRPIC_RUN_DIR'
```

The card job (in the shared queue since 2026-11-24 15:32 PST as q0036, label
`step-limit-card`, priority 5; `harness/bin/nrpic-queue show q0036`):

```
harness/bin/nrpic-queue add --label step-limit-card --priority 5 -- --kind scouting --gate G2 --launcher batch \
  --wall 00:25:00 --gpu-hours 0.4 --package tracks/core/analysis/step_limit \
  --exe /data/haiyangw/nrpic/scratch/core/exe/core_step-limit/athena_gpu \
  --list tracks/core/analysis/step_limit/card_refined.list \
  --purpose "step-limit T4 on a card and smoke run of the card build: ..."
```

then `analyse_runs.py --run R0=<dir>/R0:0.01953125 --run R0g=<dir>/R0g:0.01953125 --run
R1=<dir>/R1:0.01953125 --bound 0.656 --tmax 6 --name refined_card`. Expected (journal
entry 3, P4a to P4c): R0 jumps near t = 2.5 as card job 4799 did, R0g and R1 do not; R0g
needs fewer steps than R1.
