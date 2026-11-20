# shear: the shearing-dust test of arXiv:2003.08014 with AthenaK particles

Helper package of owner B-emd-gw, wave 3 round 1 (2026-11-20): the G2 multi-code row of
Track B (decision 0013). Specification: `SPEC.md`. Predictions and outcomes: `JOURNAL.md`.

Status: PAUSED 2026-11-20 22:35 UTC (usage pause flag). Done: SPEC, predictions P1-P12,
reference with tests (P1, P2 met), initial-data writer with constraint check (P3 met),
run B-20261120-223409-29c92ec. Not done: the AthenaK runs (smoke run failed on a deck
parameter, fix in JOURNAL 22:35), analysis, verdict.

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
