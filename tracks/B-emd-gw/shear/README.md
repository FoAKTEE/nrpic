# shear: the shearing-dust test of arXiv:2003.08014 with AthenaK particles

Helper package of owner B-emd-gw, wave 3 round 1 (2026-11-20): the G2 multi-code row of
Track B (decision 0013). Specification: `SPEC.md`. Predictions and outcomes: `JOURNAL.md`.

Status: PAUSED 2026-11-20 22:35 UTC (usage pause flag). Done: SPEC, predictions P1-P12,
reference with tests (P1, P2 met), initial-data writer with constraint check (P3 met),
run B-20261120-223409-29c92ec. Not done: the AthenaK runs (smoke run failed on a deck
parameter, fix in JOURNAL 22:35), analysis, verdict.

## Results of series 1 (batch 10a, 2026-11-22)

Series B-20261121-202830-417af0c (27 cases, release core-v0.6 processor build), summary run
B-20261123-015919-dec4392 (`scripts/summarize_series.py`; `results/series1_summary.{json,txt}`,
`figs/fig_series.png`). Extrapolated Delta = cos(theta)/cos(theta_lin) - 1: S1 -3.7e-6, S2
-1.2e-7, S3 +1.0e-5 (order not defined: non-monotone), S4 +5.8e-9, M1 -3.4e-4, M2 +3.45e-3
(sign against the prediction), L1 -5.0e-3; L2 without result (ray analysis NaN at every N_y);
the f = 1 lapse leg stopped at the guard. Outcomes P4-P12: `JOURNAL.md`, entry of 2026-11-22
18:00. Open: L2, the f = 1 leg, S3 at N_y = 256.

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
