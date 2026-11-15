# Evidence of the G0 package of D-bh-dress (and of the G1 baselines it rests on)

Paths relative to `tracks/D-bh-dress/`. Manifests: `runs/<run_id>/manifest.json`; outputs:
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/` (untracked). All runs on processors
except the two D-pre-4 card runs. Figures listed were looked at (PNG read) by the helper
that made them and, where marked L, by the lead.

## Scoping (G0)

| Artefact | Path | Run |
|---|---|---|
| Scope, null-test wording, ranges, exit criteria, risks, cost | `scope/SCOPE.md` | D-bh-dress-20261115-120304-795eee9 |
| References read at the source, with locators | `scope/REFERENCES.md` | (kb-data/raw/arxiv) |
| Scoping calculation (turnaround mass, ES scales, cost model) | `scope/scoping_estimates.py`, `scope/figs/scoping_estimates.png` | D-bh-dress-20261115-120304-795eee9; lead rerun identical: D-bh-dress-20261115-145611-5259f48 |
| First-run plan: exact references, lapse estimate, cost | `analysis/lead_checks/first_run_plan.py`, `analysis/lead_checks/first_run_plan.json`, `analysis/lead_checks/figs/first_run_plan.png` (L) | D-bh-dress-20261115-145950-23fa1c7 |

## D-pre-1 (Einstein-Straus benchmark)

| Artefact | Path | Run |
|---|---|---|
| Derivation, disagreements with item 2 | `einstein_straus/DERIVATION.md` | |
| 48 symbolic identities | `einstein_straus/sym/*.py` | D-bh-dress-20261115-042626-f3da881; lead rerun D-bh-dress-20261115-065141-5fdc744 (48/48) |
| Data set (table, particles, references) | `einstein_straus/make_es.py`, `es_model.py`; figs `es_profiles`, `es_expansions` (L), `es_reference` (L), `es_particles` | D-bh-dress-20261115-042653-f3da881 (checked), D-bh-dress-20261115-043445-b782009 (first-run copy) |
| Offline constraint check, fourth order | `einstein_straus/offline_check.py`; figs `check_1d`, `check_3d` (L) | D-bh-dress-20261115-042704-f3da881 |
| Start-time check inside AthenaK (format-2 reader of core/id-extrinsic 408df57) | `einstein_straus/code_t0_check.py`; fig `code_t0` (L) | D-bh-dress-20261115-043002-d51c7f2, -043033-4df1e76, -043327-4df1e76, -043406-4df1e76 |
| Lead's own quadrature of a, m_p | `scratch/D-bh-dress/tmp/lead/es_check_a.py` (not registered; numbers in JOURNAL.md L-outcomes) | |

## D-pre-2 (probe-limit spike)

| Artefact | Path | Run |
|---|---|---|
| Semi-analytic reference against SFW and FdRW | `spike/spike_lib.py`, `spike/spike_reference.py`; figs `ref_constf`, `ref_hernquist` (L) | D-bh-dress-20261115-123029-4df1e76; lead rerun identical: D-bh-dress-20261115-145636-5259f48 |
| Initial data for AthenaK | `spike/sample_spike.py` | D-bh-dress-20261115-123734-25227d4 |
| Stationarity in AthenaK (48000 particles, 20000 M) | `spike/analyze_spike.py`; figs `stationarity_profile` (L), `stationarity_time`, `invariants_losscone` | D-bh-dress-20261115-123755-25227d4, analysis -125739-a18d74d (failed attempt -125724-464611f kept) |
| Loss-cone probes, two time steps | `spike/compare_dt.py`; figs `losscone_dt0.05`, `losscone_dt0.025`, `crossing_dt` | D-bh-dress-20261115-123801-25227d4, -123936-72cd01e, -124246/-124249/-124257-aa9dee7 |
| Particle budget inside 20 Gm | `spike/particle_budget.py`; fig `particle_budget` | D-bh-dress-20261115-123848-72cd01e (also -123952-72cd01e) |

## D-pre-3 (Newtonian secondary infall)

| Artefact | Path | Run |
|---|---|---|
| Radiation-era checks against 1901.08528 and 2106.07480 | `secondary_infall/rd_checks.py`; figs `rd_checks`, `rd_boost_mc` | D-bh-dress-20261115-122051-bf0d6b1 (superseded: -121936-5c715b5; failed: -121837-987643b) |
| Self-similar solution with a seed | `secondary_infall/selfsimilar.py`; fig `selfsimilar` (L) | D-bh-dress-20261115-123813-97afeea (failed: -122303-4e8e8af) |
| Shell calculations (passing, absorbing, warm, vacuum core) | `secondary_infall/shells.py` | D-bh-dress-20261115-123516..123530-cff68f1, -124330..124338-75000d9, -124552-5d687b5, -125957-d087954, -130000-d087954 |
| Analysis and run plan | `secondary_infall/analyze.py`, `RUNS.md`, `run_plan_D-bh-dress-20261115-125613-248fdaf.txt`; figs `growth` (L), `profiles_eps*`, `selfsim_check`, `phase_space`, `angular_momentum` | D-bh-dress-20261115-125613-248fdaf (failed: -125449-60a62b8; superseded: -125507-a75a911) |
| Lead's closed-form re-check | `analysis/lead_checks/infall_recheck.py`; fig `lead_infall_recheck` (L) | D-bh-dress-20261115-145610-5259f48 |

## D-pre-4 (noise floor)

| Artefact | Path | Run |
|---|---|---|
| Card runs, M/8 and M/16, 500 M (0.654 + 1.523 card-hours) | `puncture_drift/inputs/drift_dx8.athinput`, `drift_dx16.athinput` | D-bh-dress-20261115-121313-284ec4f, D-bh-dress-20261115-121314-284ec4f |
| Finder re-search of earlier calibration dumps | `puncture_drift/tools/probe_finder.py`; fig `hcal_finder` | D-bh-dress-20261115-121427-284ec4f |
| Drift, floor, finder spread | `puncture_drift/tools/analyse_drift.py`, `results/drift_drift.txt`; figs `drift_history`, `drift_floor` (L), `drift_finder` | D-bh-dress-20261115-130954-49ed46f |
| Tracer side finding | `puncture_drift/tools/tracer_check.py`; fig `tracer_check` (L) | D-bh-dress-20261115-143918-a5c125a |
| Lead's re-check from the raw finder output | `analysis/lead_checks/drift_recheck.py`; fig `lead_drift_recheck` (L) | D-bh-dress-20261115-145546-5259f48 |

## Journals

`JOURNAL.md` (lead; predictions L1-L6 and outcomes), `scope/JOURNAL.md`,
`einstein_straus/JOURNAL.md`, `spike/JOURNAL.md`, `secondary_infall/JOURNAL.md`,
`puncture_drift/JOURNAL.md`. Failed and superseded runs are kept (listed above).
