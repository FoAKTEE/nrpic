# verify: verification ladder, regression suite, release proposal, G2 figures (core)

Work package "verify" of owner core. Wave 1 (below the line): C3 of brief section 9.3 as
a re-verification of what exists, regression suite, tag proposal. Wave 2 (this section):
ladder rows 3 and 4 on release core-v0.3, the open analysis of the initial data with
extrinsic curvature (T2d, T3), the figures of the G2 stage check.

## Wave 2 (2026-11-15)

| Path | Content |
|---|---|
| `ladder2/make_ics.py` | initial data of the card runs (make_ic.py: prolate e = 0.9, b = 10 M; clusters of the monoenergetic sequence with the one-percent kick and the equilibrium table, protocol of `runs/st/yc0605_v5`), turning point of E_b/M_0, card job lists |
| `ladder2/cards.py` | card runs registered by hand (`submit`, `finish`): Slurm job through `scripts/gpu_batch.sh` with the release card executable, manifest with inputs and sha256 |
| `ladder2/cluster_fate.py` | fate of each cluster run by the rule fixed in JOURNAL.md (15:30Z), mass radii, binding-energy curve; figure `figs/cluster_threshold` |
| `ladder2/prolate_compare.py` | prolate collapse at finest cells M/16 (`runs/prolate/e09_v8`) against M/8 (wave 2): horizon, curvature, constraint; figures `figs/prolate_resolution`, `figs/prolate_mosaic` (slice mosaic with zoom boxes, check C11) |
| `idcheck/t2d_t3.py` | T2d and T3 of `JOURNAL-id.md` from the runs of `analysis/id`, robust to runs that lost their particles; figures `figs/id_t2d_interior`, `figs/id_t3_bound` |
| `oblate/oblate_reference.py` | potential of a homogeneous oblate spheroid (closed form, checks), the reference an oblate component of `nrpic_cf` needs; figure `figs/oblate_reference` |
| `figscripts/convergence3.py` | three-way convergence of the coupled module (particle number, mesh, gauge and boundary) from existing runs; figure `figs/convergence_three_way` (check C9) |
| `figscripts/schem_ladder.py`, `ladder_status.json` | schematic of the ladder with verdicts (check C8); `figs/schem_ladder` |
| `figscripts/schem_architecture.py` | architecture (exists / wave 1 / to be built) and gate timeline (check C13); `figs/schem_architecture` |
| `figscripts/paperfig.py` | copy of `harness/style/paperfig.py` (schematic style) |

WAVE2_RESULTS_PLACEHOLDER

### How to rerun (wave 2)

Hand registration (see Requests, item 1): `tracks/core/tools/run_registered.py` for
processor runs, `ladder2/cards.py` for card runs. From the worktree:

```
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/ladder2/make_ics.py --out .
python3 tracks/core/verify/ladder2/cards.py submit --list <IC run dir>/job_a.list --purpose "..."
python3 tracks/core/verify/ladder2/cards.py finish <run_id>          # after the job ends
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/ladder2/cluster_fate.py <run dir>/st_yc0p700 ... --earlier
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/ladder2/prolate_compare.py --m16 /data/haiyangw/nrpic/runs/prolate/e09_v8 --m8 <run dir>/prolate_m8
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/idcheck/t2d_t3.py
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/oblate/oblate_reference.py
python3 tracks/core/tools/run_registered.py --purpose "..." -- python3 $PWD/tracks/core/verify/figscripts/convergence3.py --out $PWD/tracks/core/verify/figs/convergence_three_way
python3 tracks/core/verify/figscripts/schem_ladder.py; python3 tracks/core/verify/figscripts/schem_architecture.py
```

### Requests (wave 2)

To orch:
1. `harness/bin/nrpic-run submit` stops with `KeyError: 'outputs'` in `is_live`
   (`harness/bin/nrpic-run` line 163) on the hand-written manifests of wave 1 (they carry
   `output_directory` and `state`, not `outputs.dir` and `status`), so no core run can be
   registered through it. Every run of this package is registered by hand
   (`tracks/core/tools/run_registered.py`, `ladder2/cards.py`). Proposal: skip, or read
   with `.get`, manifests without the harness schema in `budget_state`.

To core (lead):
2. Oblate collapse (ladder row 3) needs source work: an oblate `spheroid` component in
   `athenak/src/pgen/nrpic/nrpic_cf.cpp` (now refused for a > b, line 485) and an oblate
   sampler in `python/nrpic/spheroid.py`. The potential is in `oblate/oblate_reference.py`
   (closed form with atan in place of atanh; checked against quadrature to 4e-12, run
   core-20261115-154359-d74357f); the sampler's closed-form cumulative mass carries over
   unchanged (psibar is quadratic inside). Then one card run as `e09_v8` with a > b.
3. Apply the fix of `idcheck/t2d_t3.py` to `tracks/core/analysis/id/test2_evolution.py`
   (cut tracked records at the first removal; skip dumps without ball particles), or
   point `--prefix t3` users to the verify script.
4. Bound ball at dx = M/8 with the conformal-time lapse blows up when the lapse front
   reaches the centre (largest |H| at the front 0.135, 6.4, 184 -> inf at dx = 1/2,
   1/4, 1/8 M): add to OPEN.md item 7 (lapse front) that the front steepens without
   bound with resolution; OPEN.md item 11 (status 0 after NaN) hit again.
5. STAGE package: the figures for checks C8, C9, C11, C13 are in `figs/`
   (`schem_ladder`, `convergence_three_way`, `prolate_mosaic`, `schem_architecture`);
   CHECKLIST.md and EVIDENCE.md are the lead's to update.


---

# Wave 1


Work package "verify" of owner core: C3 of brief section 9.3 as a re-verification of
what exists, and the proposal for the tags core-v0.1 and core-v0.2.

| Path | Content |
|---|---|
| `LADDER.md` | the rows of brief section 10 marked CORE, with the existing evidence, the measured numbers and the criterion of the core sheet; verdict per row |
| `RELEASE.md` | proposal for core-v0.1 (7daed19) and core-v0.2 (52c44eb): why these commits, executables, CHANGELOG of capabilities and options, evidence, known limitations, tag commands |
| `JOURNAL.md` | predictions written before each run, outcomes after it (refuted ones included) |
| `regress/` | regression suite on the current source with the release executables (no build) |
| `regress/criteria.json` | pass criteria, each with the earlier result it comes from and why it has its size |
| `regress/lib.py` | paths, release executables, run ids, checksums, manifests |
| `regress/geodesic/` | G: Kerr e = 0.99 passage, three pushers, analytic metric and Hermite lattice, processors |
| `regress/os/` | O: Oppenheimer-Snyder collapse, 9328 lattice particles, to 25 M, card |
| `regress/flrw/` | F: homogeneous matter-dominated universe, 32^3, to a = 4, card |
| `regress/growth/` | L: linear growth at amplitude 1e-4, 32^3, to a = 30, card (variants `number`, the earlier construction; `newtonian`, the generator's current default; `copy`, the earlier files) |
| `regress/submit_gpu.py` | prepares the card tests and submits them as one Slurm job through `scripts/gpu_batch.sh` |
| `ladder_measure.py` | re-reads the self-gravitating numbers of LADDER.md from the earlier run files |
| `options_at.py` | input options read by `athenak/src` at given commits (CHANGELOG of RELEASE.md) |
| `figs/` | figures of every run of this package (PDF and PNG; all inspected) |
| `manifests/` | tracked copies of the run manifests (see Requests) |

## Results (2026-11-15)

| Test | Run id | Checks | Card-hours |
|---|---|---|---|
| G geodesic passage (processors) | `core-20261115-032625-45e1779` | 104 of 104 pass | 0 (10 s, one core) |
| O dust collapse | `core-20261115-032614-45e1779` | 13 of 13 pass | 0.088 |
| F homogeneous universe | `core-20261115-032615-45e1779` | 13 of 13 pass | 0.0003 |
| L linear growth, variant number | `core-20261115-033408-bac7416` | 10 of 10 pass | 0.0008 |
| L linear growth, variant copy (control) | `core-20261115-033410-bac7416` | 10 of 10 pass | 0.0008 |
| L linear growth, variant newtonian (first pass, set-up error) | `core-20261115-032617-45e1779` | 6 of 10 pass; failed, kept on record | 0.001 |
| ladder re-measurement (analysis) | `core-20261115-032826-45e1779` | -- | 0 |

Card time of the two Slurm jobs (sacct): 4342, 5 min 23 s; 4346, 7 s; 0.092 card-hours
of the 2 allowed. Outputs under `/data/haiyangw/nrpic/scratch/core/<run_id>/`, with
`judge.json` per run.

## How to rerun

From the worktree, with the system Python (numpy, scipy, matplotlib, mpmath):

```
cd /data/haiyangw/nrpic/wt/core/tracks/core/verify/regress
python3 geodesic/run.py                       # prints the run id; about 10 s
python3 geodesic/judge.py <run_id>
python3 submit_gpu.py --tests O F L           # one card job, about 6 min; prints run ids
python3 os/judge.py <run_id_O>                # after the job ends
python3 flrw/judge.py <run_id_F>
python3 growth/judge.py <run_id_L>
python3 submit_gpu.py --tests Lcopy Lnewtonian    # optional controls
cd .. && python3 ladder_measure.py            # re-read the ladder numbers
python3 options_at.py 338bcb1 7daed19 52c44eb # options per tag
```

Each judge prints one PASS/FAIL line per check, writes `judge.json` next to the run
outputs and the figure into `figs/`, and records the verdict, the wall time and the
card-hours in the manifest. A judge exits with status 1 when any check fails. The
earlier results the judges compare with are read from `/data/haiyangw/nrpic/runs/`
(untracked) and `problems/kerr/results/kerr_summary.json` (tracked); the run scripts
regenerate the initial data with the current tools and record their checksums against
the earlier files. The executables are the release executables named in CLAUDE.md;
`lib.py` holds their paths.

## Not done in this package

- No new run of the prolate collapse or the cluster sequence: they are not in the suite
  this package was asked for, and their ladder rows rest on the earlier run files,
  re-read today. From their logs, the prolate run to 45 M took 0.48 card-hours
  (`runs/prolate/e09_v8`), a stable cluster to 300 M 0.14 (`runs/st/yc0819_v4`), the
  y_c = 0.500 collapse to 120 M 0.58 (`runs/st/yc0500_v5`), the y_c = 0.605 collapse to
  300 M 1.18 (two segments, `runs/st/yc0605_v5`) (athena "cpu time used", one card):
  the first two would fit a later regression pass.
- The regression does not exercise the cosmology production configuration (B-spline
  clouds, compensation passes, spline interpolation, step limit, alternative lapse
  conditions), the level cap, the restart path or refined periodic meshes.
- The kernel test `tests/kernel/kernel_test.cpp` was not compiled ("no build"); the
  geodesic test goes through the AthenaK processor executable instead.
- The comparison with arXiv:1801.02378 and arXiv:1710.09164 named in section 10 for
  row 1 is not made.

## Requests

To orch:
1. The ignore rule `runs/` of `.gitignore` also excludes `tracks/*/runs/`, the place the
   rules name for run manifests; CLAUDE.md forbids committing what the ignore list
   excludes. Proposal: anchor the rule (`/runs/`) so that `tracks/<ID>/runs/` is tracked.
   Until then this package keeps tracked copies in `tracks/core/verify/manifests/`.
2. Create the tags with the commands of RELEASE.md after review.

To core (lead):
3. Rebuild the processor release executable from core-v0.2: the present one
   (`.work/build_cpu_c1`, 2026-11-14 06:03) lacks `<z4c> damp_ch_chipow` and
   `damp_kappa_gam`; and let `scripts/_build.sh` write the source commit into
   `git-state.txt` (it now records the Kokkos submodule commit only).
4. Consider making `<fastflow> metric_drvts = interpolant` the default (the default
   `stored` reads horizon masses 2 to 3 percent low, `docs/TESTLOG.md` lines 310-386).
5. Correct `docs/TESTLOG.md` lines 1541-1542: the paper's 1e-3 horizon-mass statement
   belongs to the dust collapse (main.tex lines 945 and 1371-1373), not to the prolate
   collapse, for which the paper gives no horizon-mass number.

To B-emd-gw (verification of `cosmo/`):
6. The C1 linear-growth number (0.5 percent from linear theory at 32^3) holds for the
   relativistic ("number") displacement; with the current default of
   `cosmo/ic/make_east.py` (Newtonian displacement, masses carrying the rest) the same
   run is 0.6 to 1.0 percent off (`core-20261115-032617-45e1779`). And regenerating the
   C1 data today changes the conformal factor by 2.9e-8 (3e-4 of its perturbation),
   cause not determined.
