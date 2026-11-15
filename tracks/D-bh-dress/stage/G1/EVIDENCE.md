# Evidence of the G1 package of D-bh-dress

Paths relative to `tracks/D-bh-dress/`; manifests `runs/<run_id>/manifest.json`; outputs
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`. The wave-1 artefacts of D-pre-1..4 are
listed in `../G0/EVIDENCE.md` (sections D-pre-1 to D-pre-4); this file adds wave 2. L marks
figures the lead looked at.

## D-pre-1: Einstein-Straus data with the outer dust edge at 60 M; first evolutions

| Artefact | Path | Run |
|---|---|---|
| Data sets ES and V-1, exact references, prediction numbers | `es_runs/make_data.py`, `es_runs/results/predictions.json`, fig `es_runs/figs/data_compare.png` (L) | D-20261115-170213-d2c2131 |
| Offline constraint check, fourth order | `es_runs/tools/offline_check_es.py`, figs `offline_check_1d_es.png` (L), `offline_check_3d_es.png` | D-20261115-170234-f9b7f03 |
| m = 0 is a null particle in core-v0.3 | `es_runs/tools/tracer_mass_check.py`, fig `tracer_mass_check.png` (L) | D-20261115-172821-f800e34 |
| Smoke runs (344 MeshBlocks) | `es_runs/inputs/es1_dx8.athinput`, `v1_dx8.athinput` | D-20261115-172413-6412daf (D-20261115-170326-dfb2a02 superseded) |
| ES-1, V-1 on the card (running) | same inputs; analysis `es_runs/analyse.py`, `es_runs/tools/finish.sh` | D-20261115-172726-60ba4c2, D-20261115-172730-c6d151b |
| Lead's check of data, closed forms, model, mesh | `stage/review_wave2/es_check.py`, fig `es_check.png` (L) | D-20261115-193819-df9f812 |

## D-pre-2: Kerr spike

| Artefact | Path | Run |
|---|---|---|
| Kerr reference by FdRW's method | `spike/kerr_lib.py`, `kerr_reference.py`; figs `kerr_ref_constf.png`, `kerr_ref_hernquist.png` (L), `kerr_ref_checks.png` | D-bh-dress-20261115-171615-8adbbdd (first: -171134-38634d6) |
| Initial data on the Kerr-Schild slice; reference grid | `spike/sample_kerr.py`, `kerr_expected.py` | D-bh-dress-20261115-172335-9e5ccf9, -172646-ed6a510 |
| AthenaK stationarity a = 0.8, 20000 M | `spike/kerr_geodesic.athinput`, `drive_runs.py`; analysis `analyze_kerr.py`, figs `kerr_main_profile.png` (L), `kerr_main_time.png`, `kerr_main_invariants.png` | D-bh-dress-20261115-172611-1e40191; analyses -174912-b122e01, -174954-786ddcc |
| Slice control | `spike/compare_slice.py`, fig `slice_control.png` (L) | -173649-d343137, -174807-ba95d18, -175504-5b843b8, -175512-5b843b8, -175842-16be482, -175852-16be482 |
| Particle budget inside 10 r_+ | `spike/kerr_budget.py`, fig `kerr_budget.png` | D-bh-dress-20261115-173114-af8bfcc |
| Lead's check from the snapshots; C_crit | `stage/review_wave2/spike_check.py`, fig `spike_check.png` (L) | D-20261115-193844-df4523c |

## D-pre-3: Newtonian mode of AthenaK

| Artefact | Path | Run |
|---|---|---|
| Field calibration (mesh kernel) | `secondary_infall/nm_field.py`, `kernel_nx64.txt`, `kernel_nx128.txt`, fig `nm_field.png` | D-20261115-170112-d70352c, -170122-7c4da35, -170124-1b2ea1a; analysis -170803-d988f59 |
| Clump stability (vertex unstable, cell centre stable) | `secondary_infall/nm_clumpstab.py`, fig `nm_clumpstab.png` (L) | D-20261115-171245-a89f225, -171247-cde0674; analysis -171414-93fdf13 |
| Matched shell references | `secondary_infall/nm_shells.py` | D-20261115-170824-788678f ... -170839-187b91b (eight) |
| Infall runs, clump at a cell centre | `secondary_infall/nm_run.py`, `nm_infall.athinput` | N128c D-20261115-171503-4262f03, N64c -171505-62940f4, N128Lc -171507-d1058a9 |
| Analysis | `secondary_infall/nm_analyze.py`, `nm_growth_cellcentre.txt`; figs `nm_growth.png`, `nm_profiles.png` (L), `nm_selfsim.png` (L), `nm_phase.png` | D-20261115-190541-e27453d; stride test -180251-ffafe32 |
| Vertex runs (failure mode on record) | figs `nm_profiles_vertex.png`, `nm_phase_vertex.png`, `nm_clump_vertex.png` | D-20261115-170700-b2c6d6e, -170703-46ddffa, -170706-71431c6; analysis -190543-783d7be |
| Lead's independent masses | `stage/review_wave2/infall_check.py`, fig `infall_check.png` (L) | D-20261115-193823-88f7f86 |

## Verifier and note

`../G0/VERIFIER.md` (runs D-20261115-170002-8cefc3e ... -173149-7c6dd72); lead's check of
three of its claims: `stage/review_wave2/verifier_check.py`, fig `verifier_check.png` (L),
run D-20261115-193821-8e70d61. Note: `note/` (run D-bh-dress-20261115-171627-18706fb; lead
D-20261115-193951-be7b41d).
