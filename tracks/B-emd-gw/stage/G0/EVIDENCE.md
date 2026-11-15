# Evidence of G0 (and of the G1 status) for B-emd-gw

Artefacts with paths (relative to the worktree root `wt/B-emd-gw`) and run ids. Run
manifests: `tracks/B-emd-gw/runs/<run_id>/manifest.json`; outputs:
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/` (untracked). All 78 manifests are
committed (force-added: `.gitignore` line 12 also matches `tracks/<ID>/runs/`).

## Lead review (this session)

| What | Path | Run |
|---|---|---|
| Re-check driver, comparison, registration helper | `tracks/B-emd-gw/analysis/lead_recheck.sh`, `compare_results.py`, `register.py` | L1 B-emd-gw-20261115-131016-03b1119 (stopped misregistered first launch -130926-a1c2237) |
| Independent derivations a-f and figure | `tracks/B-emd-gw/analysis/lead_checks.py`; scratch `lead_checks.{json,png}` | L2 B-emd-gw-20261115-131027-03b1119 |
| Review per package | `tracks/B-emd-gw/stage/G0/REVIEW.md` | L1, L2 |
| Predictions and outcomes | `tracks/B-emd-gw/JOURNAL.md` (entry 2026-11-15T13:05Z) | - |

## scope (B-pre: problem, item 3, regime, compute)

| What | Path | Run |
|---|---|---|
| Scope, references with locators, journal | `tracks/B-emd-gw/scope/{SCOPE,REFERENCES,JOURNAL,README}.md` | - |
| Item 3 symbolic checks 1A-1E | `scope/scripts/check_item3.py`, `scope/results/check_item3.{json,txt}`, `check_item3_supplement_1B.txt` | B-emd-gw-20261115-113102-bc5e082 (also -113120-bc5e082) |
| Crossed-wave quasi-static TT | `scope/scripts/crossed_waves_tt.py`, `scope/results/crossed_waves_tt.json`, `scope/figs/crossed_waves_tt.png` | B-emd-gw-20261115-113148-4e5c33b (also -113151-4e5c33b) |
| Junk-TT decay, virial frequency, compute table | `scope/scripts/regime_estimates.py`, `scope/results/regime_estimates.json`, `scope/figs/regime_estimates.png` | B-emd-gw-20261115-113632-2960145 (also -113246-50c684b) |

## periodic_z4c (B-pre-1)

| What | Path | Runs |
|---|---|---|
| Inputs, case generator, launcher | `periodic_z4c/inputs/{lw_x,lw_3d,gauge}.athinput`, `make_cases.py`, `launch.py`, `cases/` | smoke -112946/-112947/-112948-b7b431d |
| Linear TT wave along x, convergence | `tables/lw_x.{md,json}`, `figs/lw_x_history.png`, `figs/lw_x_convergence.png` | -113219..-113232-0ea0f74, -113236, -113254-0ea0f74 |
| Rounding floor at 128 cells | `tables/lw_x_roundoff.{md,json}`, `figs/lw_x_roundoff.png` | -114947/-114948/-114949-dbd105a, -120348/-120350-3907d49 |
| Oblique data violate the constraints | `tables/lw3d_check.json`, `figs/lw3d_check.png` | -113216-0ea0f74, -113217-0ea0f74 |
| Gauge wave (Apples with Apples) | `tables/awa.{md,json}`, `figs/awa_history.png`, `figs/awa_long.png` | -113212..-113215, -114426, -114809, -114940, -115059-0ea0f74 |
| Lapse and shift record, linear and nonlinear | `tables/gauge.{md,json}`, `figs/gauge_linear.png`, `figs/gauge_nl_profiles.png`, `figs/gauge_nl_gradient.png` | -113304..-114151-0ea0f74, -115139/-115140-42096b9 |
| Metric dumps for gw_diag | scratch `B-emd-gw-20261115-113218-0ea0f74/{rst,bin}`; `tables/dump_check.json`, `figs/dump_check.png` | -113218-0ea0f74 |
| Readers, references, predictions | `analysis/{athena_dumps,refsol,predict_lw,common}.py` | - |

## gw_diag (B-pre-3)

| What | Path | Runs |
|---|---|---|
| Module and tests | `gw_diag/gwdiag/{grid,tt,weyl,analytic,readers}.py`, `gw_diag/tests/` (14 tests) | rerun in L1 |
| TT validation on analytic fields | `scripts/validate_tt.py`, `figs/tt_amplitude_spectrum.png`, `tt_time.png`, `tt_gauge_scalar.png` | -115001-e9262bd, -115125-42096b9, -115206-2e6c497 |
| Weyl validation | `scripts/validate_weyl.py`, `figs/weyl_convergence.png`, `weyl_psi4.png` | -115358-637c30b, -115540-2cb33df, -115637-175cbca, -115846-214d142 |
| End to end on AthenaK output; weyl-output lag | `scripts/validate_athenak.py`, `figs/athenak_tt.png`, `athenak_psi4.png` | -120128-7dfaa38 (input -113218-0ea0f74) |
| Scouting on full-GR cosmology dumps | `scripts/cosmo_demo{,_plot}.py`, `figs/cosmo_tt.png` | -120846-d1509b5, -121143-0eace55; failed -120531-40a3597 (division by zero, kept) |

## baseline (B-pre-4)

| What | Path | Runs |
|---|---|---|
| Baseline specification and results | `baseline/BASELINE.md`, `README.md`, `JOURNAL.md` | - |
| Library and checks T1-T8 | `baseline/scripts/{ellipsoid,run_baseline}.py`, `baseline/results/baseline_results.json`, `baseline/figs/t1..t8_*.png` | -115752-840e994 (earlier -115529-58c7f50) |

## verify_cosmo (B-pre-2, B-pre-5, rows FLRW, growth, multi-code, pancake)

| What | Path | Runs |
|---|---|---|
| Evidence of `cosmo/` against B's criteria | `verify_cosmo/VERIFY.md` | FLRW recheck -115414-7ffbde1 (`results/flrw_recheck.json`, `figs/flrw_recheck.png`) |
| Exact Newtonian plane-wave reference | `verify_cosmo/scripts/{zeldovich,test_zeldovich}.py` | rerun in L1 (13 of 13 PASS) |
| Pancake initial data, input | `verify_cosmo/inputs/pancake.athinput`, `scripts/build_ic.sh` | -114807-dbd105a |
| Pancake GR runs (cards) | scratch dirs | -115217-69ab1db (job 4373, 0.284 card-h), -115902-a3207d7 (job 4388, 0.197 card-h) |
| Newtonian references (`cosmo/newton/pm.py`) | `scripts/newton_pancake.py` | -115239-69ab1db, -122451-01801f6 |
| Pancake analysis | `scripts/analyze_pancake.py`, `results/pancake{,_profiles}.json`, `figs/pancake_*.png` | -123852-ea4475c (first version -122240-b0e4c9d) |

## Existing evidence of `cosmo/` relied on (not produced by this owner)

`cosmo/TESTLOG.md` (lines cited in `VERIFY.md` and `SCOPE.md`), `cosmo/analysis/daverio_{a,b,c256_p3}.json`,
run directories `runs/cosmo/*` of the main checkout (untracked), `cosmo/README.md`,
`cosmo/PLAN.md`.

## Budget

Card-hours used: 0.481 (two jobs of verify_cosmo); allotment 40 to the next gate
(decision 0006). Processor runs: all others, at most 16 cores at a time.
