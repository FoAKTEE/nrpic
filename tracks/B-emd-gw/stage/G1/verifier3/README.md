# stage/G1/verifier3: independent verifier of G1 criterion 1 (tests F and X) and of the spatial-gauge piece

Helper package of B-emd-gw, wave 3 round 1 (2026-11-20, two sessions: 14:13-14:35 and from
18:56 PST). Written in a fresh context from the artefacts (inputs, initial-data script, raw
dumps); the producers' conclusions were read only after my own numbers were committed
(JOURNAL entries 10 and 14 say when). The report is `VERIFIER.md`.

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | the report: what was checked, my numbers, verdicts per claim, criterion 1, V4, weakest points, not checked, requests |
| `JOURNAL.md` | predictions before each step, outcomes after (entries 1-16) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `scripts/exact.py` | exact solutions: flat TT wave of `z4c_linear_wave`, EdS tensor mode T(t), polarization basis |
| `scripts/diag.py` | own readers (AthenaK bin, single/double), Z4c -> ADM, TT projection, mode coefficients, Weyl E/B (spectral or FD6), fixed-direction Psi_4 |
| `scripts/v1_exact.py` | V1: symbolic and numerical checks of the exact solutions |
| `scripts/v2_tests.py` | V2: tests of the readers and diagnostics on analytic fields and initial dumps |
| `scripts/v3_measure.py` | V3: per-dump measurement of F and X (TT, Weyl spectral and FD6, background) |
| `scripts/v3_summary.py` | V3: errors, orders, plus/cross, x1/x10, figures |
| `scripts/v3_extra.py` | V3 supplement: TT-Psi4 difference against the dispersion term, X difference against the background error, non-TT content of F |
| `scripts/v3_classify.py` | numbers for the classification: forward combination of F, own symbol+RK4 predictor, polarization ratios |
| `scripts/v4lib.py` | V4: own second-order spatial-gauge piece (plain and conformal metric), displacement from a metric difference |
| `scripts/v4_gauge_test.py` | V4: exact pure-gauge test |
| `scripts/v4_scan.py` | V4: c_+(k,k,0) zero shift vs Gamma driver before/after the gauge piece, first-source scan dumps |
| `scripts/v4_energy.py` | V4: kinetic/gradient energy ratio of the TT part for a >= 12 |
| `results/*.json` | copies of the run outputs (v1, v2, v3_dumps, v3_summary, v3_extra, v3_classify, v4_gauge_test, v4_scan, v4_energy) |
| `figs/*.png` | figures of the runs (all looked at) |

## How to rerun

Every script reads `NRPIC_RUN_DIR` and is run through the harness from the worktree root with
the worktree's `.venv`, for example:

```
harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/B-emd-gw/stage/G1/verifier3 \
  --purpose "..." --launcher local --cores 5 -- env V3_WORKERS=5 OMP_NUM_THREADS=1 \
  python3 tracks/B-emd-gw/stage/G1/verifier3/scripts/v3_measure.py
```

Order and inputs: `v1_exact.py`, `v2_tests.py` (no inputs); `v3_measure.py` (raw dumps of the
runs listed in its RUNS table, about 2 min on 5 cores); `v3_summary.py`, `v3_extra.py`,
`v3_classify.py` with `V3_DUMPS=<run dir of v3_measure>/v3_dumps.json`; `v4_gauge_test.py`
(none); `v4_scan.py` (scan runs B-20261115-165353-b592d43 and B-20261115-165525-f7c2004,
about 10 min); `v4_energy.py` (scan runs B-20261115-164059-d802e82, -165353-b592d43,
-165525-f7c2004; 4 workers). The local launcher runs in the foreground: give the shell a
timeout above the run time or run it in the background (run B-20261121-025612-ed4a875 was
killed by a 120 s shell timeout).

Runs of this package: B-20261120-222232-3d7d57e (failed), B-20261120-222342-8cda367,
B-20261120-222822-e26afae, B-20261121-025612-ed4a875 (failed), B-20261121-025826-80973e3,
B-20261121-030110-52ae004 (failed), B-20261121-030121-58fe5dc, B-20261121-030542-b2e3eff,
B-20261121-030848-59f89b5, B-20261121-031220-8b9c4d7, B-20261121-031808-3ef8c39 (scan),
B-20261121-031833-c0ec479 (energies).

## Requests

See `VERIFIER.md` section 8 (rewordings for the lead; none blocking for core).
