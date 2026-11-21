# Evidence of core G2 (wave 1, integration): artefacts, paths, run ids

Manifests: `tracks/core/runs/<run_id>/manifest.json` (committed with `git add -f`,
harness/RULES.md "Known issue"); outputs: `/data/haiyangw/nrpic/scratch/core/<run_id>/`.
Run ids of the lead's session end in 5407341, 3629622, 23eca56 or 9377fe8 (the commit of
the worktree when the run started; the executables are those named below in every case).

## Executables (built from a git archive of the source)

| Role | Path | Source |
|---|---|---|
| processor, baseline | `wt/core/.work/build_cpu_base/src/athena` | main source (74ed745 = a1c2237) |
| processor, merged | `wt/core/.work/build_cpu_609a875/src/athena` | 609a875 |
| card, baseline | `wt/core/.work/build_gpu_base/src/athena` (sha256 ad335188...) | 74ed745 |
| card, merged | `wt/core/.work/build_gpu_609a875/src/athena` (sha256 601dbcc9...) | 609a875 |

sha256 of all four: `scratch/core/tmp/lead/exe_sha256.txt`; build logs
`scratch/core/tmp/lead/build_*.out`.

## Merge and fixes (git)

fcc3179 (rng), c88804c (collisions), 65648c8 (scalar-field), dc93a72 (id-extrinsic),
7c11538 (multi-puncture), 66bd4c3 (newton, conflicts resolved), 0f11630 (format-2
curvature added to Bowen-York), 609a875 (collisions refuse the Newtonian mode).

## Regression of existing behaviour

| Check | Run ids | Result |
|---|---|---|
| geo, Kerr midpoint (proc.) | core-20261115-145316-5407341 / -145317-5407341 | 2 files identical |
| boris, Kerr Boris on lattice (proc.) | -145318-5407341 / -145319-5407341 | 2 identical |
| dep, deposit on refined flat mesh (proc.) | -145320-5407341 / -145325-5407341 | 1 identical |
| east, periodic cosmology with Z4c (proc.) | -145329-5407341 / -145337-5407341 | 12 identical |
| os, Oppenheimer-Snyder with Z4c, refined (proc.) | -145344-5407341 / -145755-3629622 | 11 identical; 5 restart files differ in 34 never-set header bytes only (masked: 18 identical) |
| jeans, gas self-gravity (proc.) | -150203-3629622 / -150210-3629622 | 5 identical incl. log result lines |
| binary, gas self-gravity, 4 levels (proc.) | -150217-3629622 / -150256-3629622 | 1 identical incl. log result lines |
| c1-c5 (rng driver, proc.) | core-20261115-145323-5407341 | c1-c4 identical; c5: 3 restart files differ in 32 never-set bytes (masked: identical) |
| c1-c5 (card, job 4430) | core-20261115-145921-3629622 | c1, c2 identical; c3-c5 deposit: baseline not reproducible, no verdict |
| nrpic_cf regress_cf + cf_table_regress (proc.) | core-20261115-145448-3629622 (exit 1 from its faulty P5 part only) | IDENTICAL 16 files; IDENTICAL 9 files (restart bytes masked) |
| nrpic_cf regress_cf + cf_table_regress (card, job 4431) | core-20261115-150426-9377fe8 | IDENTICAL 16 files; IDENTICAL at the start, 6 files |
| options (scan) | `verify/options_at.py 52c44eb 609a875`, `scratch/core/tmp/lead/options_v02_609a875.json` | 80 added, 0 removed, no existing default changed |

## Verify suite on the merged executables

| Test | Run id | Checks | Figure (looked at) |
|---|---|---|---|
| G geodesics (proc.) | core-20261115-065452-3629622 | 104/104, all values equal to core-20261115-032625-45e1779 | `verify/figs/regress_geodesic_core-20261115-065452-3629622.png` |
| O Oppenheimer-Snyder (card, job 4429) | core-20261115-065901-3629622 | 13/13 | `verify/figs/regress_os_core-20261115-065901-3629622.png` |
| F homogeneous universe (card) | core-20261115-065903-3629622 | 13/13, all values equal | `verify/figs/regress_flrw_core-20261115-065903-3629622.png` |
| L linear growth (card) | core-20261115-065904-3629622 | 10/10 | `verify/figs/regress_growth_core-20261115-065904-3629622.png` |

## Quick tests of the merged capabilities

| Capability | Run id | Result | Figure (looked at) |
|---|---|---|---|
| rng kick demonstration D1 | core-20261115-145543-3629622 | 14/14; checksums equal to core-20261115-121609-fb0491a | package figure `notes/rng_figs/fig_kick_demo.png` |
| rng twin against numpy Philox (no run; lead script `scratch/core/tmp/lead/checks/philox_numpy.py`) | -- | 3000 keys, 0 mismatches | -- |
| collision replay, 7 cases | core-20261115-145545-3629622 | 7/7, 8.9e-16 flat, 9.8e-15 curved | `scratch/core/core-20261115-145545-3629622/fig_replay.png` |
| scalar test 1a | core-20261115-150004-3629622 | orders 1.991, 3.957, 5.918 | package figure `notes/scalar_figs/fig_wave_convergence.png` |
| Newtonian point mass N = 32, 64 | core-20261115-150209-3629622 (failed first attempt core-20261115-150002-3629622) | 1.609e-2, 4.94e-3, order 1.70 | `scratch/core/core-20261115-150209-3629622/field/field_point.png` |
| combined format-2 + Bowen-York curvature (P5), proc. | core-20261115-150404-9377fe8 (first criterion failed: core-20261115-150315-23eca56) | no point above the float32 rounding bound; K(comb) - K(A) up to 5.9 | `scratch/core/core-20261115-150404-9377fe8/fig_cf_combined.png` |
| same, card | core-20261115-150426-9377fe8 (failed set-up: core-20261115-145939-3629622) | PASS | -- |
| Bowen-York reference, id derivation (pure Python) | -- | all checks pass | -- |
| id late card runs, analysis | core-20261115-145804-3629622 (exit 1 in the t3 part) | T2c core part holds; T2d open; T2e refuted for the sharp surface; T3 open | `analysis/id/figs/t2_radius_ct_edge2_prod.png`, `t2_radius_gs0_edge2_ext.png` |

## Evidence of the work packages (their own runs, checked by the lead from the artefacts)

| Package | Interface / journal | Figures looked at by the lead |
|---|---|---|
| doc | `interfaces/SECTION2_CORRECTIONS.md`, `deposit.md`, `pusher.md`, `particle_id.md`, `diagnostics.md`, `cosmo_gauge.md`, `run_manifest.md`, `interfaces/JOURNAL.md`; run core-20261115-112600-b7b431d | (not opened by the lead: `interfaces/figs/d1_*.png`) |
| verify | `verify/LADDER.md`, `RELEASE.md`, `verify/JOURNAL.md` | `verify/figs/ladder_overview_core-20261115-032826-45e1779.png`, `regress_os_core-20261115-032614-45e1779.png`, `regress_geodesic_core-20261115-032625-45e1779.png`, `regress_growth_core-20261115-033408-bac7416.png` |
| rng | `interfaces/rng.md`, `docs/RNG.md`, `JOURNAL-rng.md`; card job 4414 runs core-20261115-135211/135215/135218/135240/135312-a6e5c46 | `notes/rng_figs/fig_kick_demo.png`, `fig_rng_pvalues.png` |
| coll | `interfaces/collisions.md`, `docs/COLLISIONS.md`, `JOURNAL-coll.md` | `scratch/core/core-20261115-134036-5684674/fig_relax_distributions.png`, `scratch/core/core-20261115-142625-67f8c1d/fig_cluster.png` |
| scalar | `interfaces/scalar_field.md`, `JOURNAL-scalar.md` | `notes/scalar_figs/fig_wave_convergence.png`, `fig_flrw_conformal.png`, `fig_noise_ms.png` |
| id | `interfaces/spherical_id_format2.md`, `JOURNAL-id.md` | `analysis/id/figs/t1_exterior.png`, `t2_radius_ct_edge2.png`, `t2_gauge.png` |
| mp | `interfaces/multi_puncture.md`, `JOURNAL-mp.md` | `analysis/mp/figs/static_convergence.png`, `boost_evolution.png`, `triple_evolution.png` |
| newton | `interfaces/newtonian_mode.md`, `JOURNAL-newton.md` | `analysis/newton/collapse.png`, `field_point.png` |

## Paper source locators used (refs/arxiv_2611.12831/src/main.tex, sha256 5f01b119...)

L75 and L676 (common global step), L641 (first-order deposit), L680-682 (binomial filter,
pass count not stated), L836 (independent geodesic integration), L917 (998,592
particles), L926 (Staley et al.), L945 (<~ 1e-3), L971 (prolate horizon at 32 M), L1138
(109 M, 73 M), L1199 (0.833530), L1340 (64.15625 M), L1360 (64.175 M), L1393 (follow-up
list).

## Release candidate core-v0.4 (2026-11-20 and 2026-11-21; `tracks/core/RELEASE-v0.4.md`)

Executables: `wt/core/.work/build_cpu_v04rc/src/athena` (sha256 8bff3107...),
`wt/core/.work/build_gpu_v04rc/src/athena` (sha256 ab3ee2a6...), source f9323185; copies
with READY in `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`. Release executable
of core-v0.3: `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (sha256 d983155b...).
Merges: 3ab47062 (requests-b), 120aa7cf (gauge), 54dc527e (scalar-2), e2498da4
(clump-curvature), de42b294 (id-solver), 7b0fcf27 (requests-adf), f9323185
(collisions-2); late records 148a302e, e9644451.

| Check | Run id | Result | Figure (looked at) |
|---|---|---|---|
| byte regression, 12 set-ups, processors | core-20261120-221607-4985804 | PASS: 75 items, 62 identical, 8 a (unset restart bytes), 5 b (last_time lines), 0 other | `scratch/core/core-20261121-030235-cc329f5/fig_regress_v04.png` (run core-20261121-030235-cc329f5; -030223-bd2eddc superseded) |
| the same, first call of the driver | core-20261120-220849-cea5881 | FAIL by the driver's rule for a case without files (binary); rule corrected, same runs | -- |
| quick tests, 9 cases against the branch executables, processors | core-20261121-025955-bd47414 | PASS: 40 files, 38 identical, 2 b, 0 other; 13 numbers in their bands | `scratch/core/core-20261121-031018-6759268/fig_quick_v04.png` (run core-20261121-031018-6759268) |
| the same, first attempt | core-20261120-222724-75e323c | failed: the driver compared a record of the particle generator (directory name); AthenaK files equal | first figure, layout defects |
| six more READY examples against the branch executables, processors | core-20261121-031604-dccccbb | PASS: 42 files, 40 identical, 2 a (restart files of acc), 0 other; 12 runs status 0 | `scratch/core/core-20261121-032134-8dd42e4/fig_more_v04.png` (run core-20261121-032134-8dd42e4; -032119-f98c422 superseded) |
| card check, 11 cases on one A100 | core-20261121-025945-54dc669 (Slurm job 4758, 0.0094 card-hours); judged by core-20261121-033000-f1c0f5d (-032851-5f911b8 superseded) | PASS: 11 status 0; 13 numbers in their bands; iteration and collision counts equal to the processor runs; differences within the bounds written before the run; the first session's relative bound on the wave error norm failed as written | `scratch/core/core-20261121-033000-f1c0f5d/fig_card_v04.png` |
| options (scan) | `verify/options_at.py core-v0.3 HEAD`, `scratch/core/tmp/lead_v04/options_v03_v04.json` | 61 added, 0 removed, no default changed | -- |
