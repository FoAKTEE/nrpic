# shear: the shearing-dust test of arXiv:2003.08014 with AthenaK particles

Helper package of owner B-emd-gw, wave 3 round 1 (2026-11-20): the G2 multi-code row of
Track B (decision 0013). Specification: `SPEC.md`. Predictions and outcomes: `JOURNAL.md`.

Status (2026-11-24): series 1-6 run and judged (below); open: the cause of L2's mesh dependence
and constraint violation (risk R19).

## Results of series 1 (batch 10a, 2026-11-22)

Series B-20261121-202830-417af0c (27 cases, release core-v0.6 processor build), summary run
B-20261123-015919-dec4392 (`scripts/summarize_series.py`; `results/series1_summary.{json,txt}`,
`figs/fig_series.png`). Extrapolated Delta = cos(theta)/cos(theta_lin) - 1: S1 -3.7e-6, S2
-1.2e-7, S3 +1.0e-5 (order not defined: non-monotone), S4 +5.8e-9, M1 -3.4e-4, M2 +3.45e-3
(sign against the prediction), L1 -5.0e-3; L2 without result (ray analysis NaN at every N_y);
the f = 1 lapse leg stopped at the guard. Outcomes P4-P12: `JOURNAL.md`, entry of 2026-11-22
18:00. Open: L2, the f = 1 leg, S3 at N_y = 256.

## Results of series 2-6 (batch 11, 2026-11-24)

P10 holds (f = 1 against f = 1/3: -8.7e-5, B-20261124-131336-bc61eee). L2 with narrow fans at one
particle per cell along y: -0.8281, -0.8302, -0.8348 at N_y = 32, 64, 128 (B-20261124-134209-4584052).
At N_y = 64 it converges in the particle number along y (1, 2, 4, 8 per cell: -0.8302, -0.8233,
-0.8218, -0.8208) to about -0.820, beside CosmoGRaPH's -0.8183 (draft.tex:360); at 4 per cell the
mesh does not converge usefully: -0.8218, -0.8312, -0.8392 at N_y = 64, 128, 256 (differences
9.4e-3, 7.9e-3; series 5 and 6, B-20261124-135951-237e27b, B-20261124-140856-911ded9; summary
B-20261124-172643-d1e88c7, `figs/fig_ppc.png`). The field carries relative constraint means of
0.12-0.15 over 1 <= t <= t_A at every mesh and particle number; the step is excluded (series 4).
Verdict: L2 is not converged in this code; S1-S4, M1, L1 carry the comparison. Next: an amplitude
between M2 and L2 without stream crossing before t_A (JOURNAL, series 6 outcome).

## Results of series 7 (batch 29, 2026-11-26; decision 0046 item 2a)

beta = 0.125 at H L = 4, N_y = 64, 128, 256 at 4 per cell along y (B-20261126-222544-f3a5176,
judged by B-20261126-230056-294b265, `scripts/series7_judge.py`, `figs` not copied: series7.png in
the run directory). No stream crosses before t_A = 4.118 (first crossing t = 9.0-9.25, after the
arrivals). Delta = 0.053749, 0.053800, 0.053821: differences 5.1e-5, 2.1e-5 (ratio 0.40, order
1.3), Richardson 0.05383 with error 1.4e-5: the observable converges in the mesh where streams do
not cross, unlike L2. Constraint means to t_A 3.6e-6 to 2.6e-6 (Hr), 2.3e-4 to 1.6e-4 (Mr): small
but not falling 1.5 times per doubling (prediction failed in that part). Design:
`scripts/nocross_design.py` (B-20261126-222532-5ab01ea; its estimate was too optimistic), check
`scripts/crossing.py`. Outcomes N7a-c: `JOURNAL.md`, entry of 2026-11-26 15:02.

## Contents

| Path | What |
|---|---|
| `SPEC.md` | set-up, coordinate change to psi = 1, slicing, observable, cases, agreement criteria |
| `scripts/shear_ref.py` | closed form (draft.tex:262), first-order integrals, initial data, linear solution, ray shooting |
| `scripts/make_shear_ic.py` | fields.bin and particles.nrp (tracers, two ray fans, dust lattice) |
| `scripts/check_ic.py` | constraint check of the written data (spectral, own pcs deposit) |
| `scripts/ref_table.py`, `scripts/run_refs.py` | reference table and the driver of tests, table, check |
| `scripts/run_cases.py`, `scripts/analyze_rays.py` | AthenaK runs from a list; cos(theta) by shooting over the fans |
| `inputs/shear.athinput`, `inputs/smoke.txt` | deck (thin box) and the smoke list |
| `tests/test_ref.py` | 24 tests (symbolic slice and constraints, linear slicing, formula) |
| `results/`, `figs/` | ref_table, check_ic (JSON, PNG) |

## How to rerun

```
cd /data/haiyangw/nrpic/wt/B-emd-gw
P=tracks/B-emd-gw/shear
harness/bin/nrpic-run submit --kind scouting --gate G2 --package $P --cores 1 --purpose "..." \
  -- python3 $P/scripts/run_refs.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package $P --cores 1 \
  --exe /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena --purpose "..." \
  -- python3 $P/scripts/run_cases.py --list $P/inputs/smoke.txt --npar 1 --analyze
```

## Requests

None yet.
