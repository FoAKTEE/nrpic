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
| ES-1, V-1 on the card (200 M, 0.769 + 0.672 card-hours) | same inputs; `es_runs/tools/finish.sh` | D-20261115-172726-60ba4c2, D-20261115-172730-c6d151b |
| Outcome of ES-1/V-1 (wave 2b): drift against V-1, wall, crossings, lapse | `es_runs/analyse.py`, `results/es_analysis.json`; figs `horizon_mass.png` (L), `wall.png` (L), `tracers_all.png`, `lapse_probes.png` (L), `axis_profiles.png` (L) | D-20261119-141839-8686bd7 |
| Second look: dust against the wall by direction, onset of tracer errors, slicing at the plateau tracer, turnaround of R0 = 20 M | `es_runs/tools/es_extra.py`, `results/es_extra.json`; figs `extra_*.png` (`extra_horizon.png`, `extra_tracers_vs_t.png` L) | D-20261119-142929-bb375ff; version 2 D-20261119-143659-7adcad7 |
| Lapse features at the probes (no inward signal from the boundary) | `es_runs/tools/probe_fronts.py`, `results/probe_fronts*.json`; figs `probe_fronts_*.png` (`probe_fronts_t100_V-1.png` L) | D-20261119-143413-bce5e71, D-20261119-143444-8a9949c |
| ES-1G: lapse_leak model, processor pre-flight, card run (queued) | `es_runs/tools/es1g_model.py`, `preflight_compare.py`, `inputs/es1g_dx8.athinput`, `tools/finish_es1g.sh`; figs `es1g_model.png` (L), `preflight.png` (L) | D-20261119-142334-4f2bffe; pre-flight D-20261119-143623-8576a6e, D-20261119-143626-7d1fa75, comparison D-20261119-150329-d1d8f03; card run D-20261119-142633-6f72922 (Slurm 4636, queued) |
| Lead's independent re-check of the ES-1/V-1 outcome (Y1-Y6) | `stage/review_wave2/es_finish_check.py`, fig `es_finish_check.png` (L) | D-20261119-151039-b2ce968, figure D-20261119-151119-58b2102 (first attempt D-20261119-151012-b4afa8a superseded: proper-time column misread) |
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
| Matched shell references | `secondary_infall/nm_shells.py` | D-20261115-170824-788678f, -170826-20d5d4a, -170827-ba851f0, -170829-0d86d49, -170831-b379b65, -170834-ac15adf, -170837-af64029, -170839-187b91b |
| Infall runs, clump at a cell centre | `secondary_infall/nm_run.py`, `nm_infall.athinput` | N128c D-20261115-171503-4262f03, N64c -171505-62940f4, N128Lc -171507-d1058a9 |
| Analysis | `secondary_infall/nm_analyze.py`, `nm_growth_cellcentre.txt`; figs `nm_growth.png`, `nm_profiles.png` (L), `nm_selfsim.png` (L), `nm_phase.png` | D-20261115-190541-e27453d; stride test -180251-ffafe32 |
| Vertex runs (failure mode on record) | figs `nm_profiles_vertex.png`, `nm_phase_vertex.png`, `nm_clump_vertex.png` | D-20261115-170700-b2c6d6e, -170703-46ddffa, -170706-71431c6; analysis -190543-783d7be |
| Lead's independent masses | `stage/review_wave2/infall_check.py`, fig `infall_check.png` (L) | D-20261115-193823-88f7f86 |

## Verifier and note

`../G0/VERIFIER.md` (runs D-20261115-170002-8cefc3e, -170224-924d1d9, -171508-94e8cb1,
-171532-ba23a99, -171534-ff5b0e9, -171543-d966aba, -171545-d7e01a7, -171953-908afff,
-171818-a5aefe8, -171733-633d422 (stopped), -173149-7c6dd72); lead's check of
three of its claims: `stage/review_wave2/verifier_check.py`, fig `verifier_check.png` (L),
run D-20261115-193821-8e70d61. Note: `note/` (runs D-bh-dress-20261115-171128-38634d6,
D-bh-dress-20261115-171627-18706fb; lead D-20261115-193951-be7b41d). Superseded lead run of
wave 2: D-20261115-193755-3a53b08. The wave-2b package `flux_tools/` (wave 3a, in progress)
is not part of this gate's evidence.

## Card-hours

Wave 1 2.18 (D-pre-4), wave 2 1.44 (ES-1, V-1); reserved 0.98 (ES-1G, queued);
`nrpic-run budget` on 2026-11-19: G1 used 3.62, left 25.40 of 30.

## Further runs of waves 1 and 2, named one by one (decision 0016 item 3)

Hand-registered or analysis runs that the tables above (or `../G0/EVIDENCE.md`) name only as
a range or not at all: Newtonian-mode timing probe D-20261115-170127-877c84f; infall analyses
D-20261115-174734-a688058, D-20261115-185248-9dc7934, D-20261115-190403-0bdb9b7 (superseded
by -190541-e27453d and -190543-783d7be); Kerr K2 analysis D-bh-dress-20261115-174815-473134d;
wave-1 shell references D-bh-dress-20261115-123516-cff68f1, -123518-cff68f1,
-123520-cff68f1, -123522-cff68f1, -123524-cff68f1, -123526-cff68f1, -123528-cff68f1,
-123530-cff68f1 and reruns -124330-75000d9, -124332-75000d9, -124334-75000d9,
-124336-75000d9, -124338-75000d9; wave-1 loss-cone analyses D-bh-dress-20261115-124246-aa9dee7,
-124249-aa9dee7, -124257-aa9dee7.

## Wave 3 (2026-11-20 and 2026-11-21)

| Artefact | Path | Run |
|---|---|---|
| ES-1G closed and judged (G1-G7, J1-J6, K1-K2) | `es_runs/JOURNAL.md` entry 9, `es_runs/README.md` "ES-1G results", `results/es1g_judge.json`, `es_extra_es1g.json`, `slicemass_es1g.txt`; figs `es_runs/figs/es1g/*.png` (`judge_horizon.png` L, `slicemass_ES-1G.png` L) | card D-20261119-142633-6f72922; analyses D-20261120-221754-ae3dafe, -222042-59c7d82 (superseded for figures), -222424-230f936, -222956-6abf860 |
| Fresh-context verifier of the G1 material (C17) | `stage/G1/VERIFIER.md` (= `verifier_g1/VERIFIER.md`), `verifier_g1/` scripts and JOURNAL; figs in the run directories (`v2_growth_ratio.png` L, `v3_hern_a0.8.png` L) | D-20261120-222209-871e07f, D-20261121-031031-e23da04, -031711-0d79cb3, -033209-9c0bd44, -034048-17427b0, -035106-0c619ee, -040417-8a3c402, -035114-8a3cb38, -040636-e8d5352, -040826-9d5051a |
| Architecture schematic redrawn (C9), timeline, note v1 figures and ledger | `note/scripts/schem_architecture.py`, `schem_timeline.py`, `fig_kerr.py`, `fig_newton.py`, `fig_esrun.py`, `run_all.py`; `note/figures/schem_architecture.png` (L) | D-20261120-222413-4a67fa2, -222422-983f3f6, -222424-d7cd958, -222429-026731f, -222430-452c907, -223535-24f7f90 |
| Late-drift decomposition (step 1A) | `drift_controls/tools/step1.py`, `results/step1.json`, figs `drift_controls/figs/step1_*.png` | D-20261120-222107-cc4937b |
| Boundary control V-1B (faces at +-384 M) and finder pre-flight | `drift_controls/inputs/v1b_bnd384.athinput`, `tools/probe_finder_es.py` | card D-20261120-222625-63abd72 (0.778 card-hours); pre-flight D-20261120-222820-94f20b3 |
| ES-F construction checked by a second agent; pre-registration of the ES-F run | `flux_tools/check_esf_construction.py`, `results/check_esf_construction.json`, fig `figs/check_esf_construction.png` (L); `flux_tools/JOURNAL.md` entries 6, 6b, 7 | D-20261120-222314-ed5d325, -222651-3180e07, -222815-f8d1b42; data D-20261119-145022-2208a19 |
| D-pre-3 toward a/a_i = 30: design, timing, matched shells, R8 rerun | `secondary_infall/nm_design.py`, `nm_run.py`, `nm_shells.py`, `nm_late.py` | D-20261120-222358-e98ffbd, -222405-ce8922c, -222511-34be8a8, -222513-9849530, -222515-c2ef5b8, -222758-acc6929, -222804-e5183e9, -222550-e472402 |
| Lead's re-check Z1-Z5 (ES-1G horizon and tracers, V-1B against V-1, dress at a/a_i = 2, ES-F particle file) | `stage/review_wave3/wave3_check.py`, fig `wave3_check.png` (L); `../REVIEW-wave3.md` | D-20261121-063617-3f2036f |
