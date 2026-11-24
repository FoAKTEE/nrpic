RELEASE core-v0.6 984bde68c6201c8f100ced3d6a7effbea9cafd80 REGRESSION PASS

Card check of the candidate's card executable `athena_gpu`: PASS (run
core-20261121-132052-f330004, Slurm job 4800, ran 2026-11-21 07:21 PST; judged in
core-20261121-154700-2de4974 and core-20261121-154710-220c1b0 by the lead of batch 4a;
section "Card check of `athena_gpu`"). The card executables of the three branches, the
same source per capability, did run on a card (same section). Release builds against
the candidate: section "Release builds against the candidate".

# Release candidate core-v0.6: three source branches of core on top of core-v0.5

Written by the lead of core on 2026-11-21 (decision 0019 item 4; batch 3). The commit of
the first line is the source commit: the last commit of `core/nrpic` that changes
`athenak/`, `python/`, `problems/` or `scripts/` (the merge of core/id-solver-2). Later
commits of `core/nrpic` add records only (`tracks/core/`); `git diff 984bde68 <tip> --
athenak python problems scripts` is empty [VERIFIED at the tip that holds this file].
Predictions, written before any build, and outcomes: `tracks/core/JOURNAL.md`, entry of
2026-11-21T12:55Z. Options, behaviour that changes without an option, formats:
`tracks/core/CHANGELOG.md`, section core-v0.6.

## Executables of the candidate

`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/`, all four built from the source
commit in new build directories of `wt/core` (COMMIT there has the commands and times):

| File | Build | sha256 |
|---|---|---|
| `athena_cpu` | `scripts/build_cpu.sh` (Kokkos Serial, -O2 -g), `.work/build_cpu_v06rc` | 2ec1f232...b443db87ce |
| `athena_gpu` | `scripts/build_gpu.sh` (CUDA 12.6, one A100, no MPI), `.work/build_gpu_v06rc` | 168e5da6...eb214c6a4 |
| `athena_cpu_omp` | `scripts/build_cpu_omp.sh` (Kokkos OpenMP, -O3 -DNDEBUG -g), `.work/build_omp_v06rc` | 564e0232...901ac51642 |
| `athena_cpu_mpi` | `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh` (Open MPI 5.0.1), `.work/build_cpu_mpi_v06rc` | 96cfeac5...e24d081819 |

With them `COMMIT`, `SHA256SUMS`, `READY` (every new option with one example input, what
is tested and what is not, known defects) and `branches/READY.<branch>` (the READY of
each merged branch).

## Branches merged, in this order (one merge commit each)

| Branch | Tip merged (source) | Merge commit | Review |
|---|---|---|---|
| core/newton-2 | b7c9fc73 (67ca9ce1) | a1fffa58 | pass |
| core/z4c-faces | 5d875275 (f6f9a0df) | 1419f19a | pass; the new options are off by default |
| core/id-solver-2 | 3087526a (395e17d8) | 984bde68 | pass; five things change in runs with `id_solve = true` (changelog); the default `id_far = multipole` stands |

No conflict in any merge (`CMakeLists.txt`, `particles.hpp`, `docs/FORMATS.md` merged
by git; read afterwards). Review notes of every branch: journal entry of 12:55Z and the
three merge commit messages. Three points of the review:

- **core/z4c-faces, how its failed byte regression was resolved.** The earlier session
  of the package had a regression that failed in the last bits (ball 8 of 11 files) and
  was not looked at. The closing session found the cause by compiling one file with
  nine header variants: with the body of the option reader in the header that `z4c.hpp`
  includes, g++ 11.4 compiled the unchanged `z4c_calcrhs.cpp` with two more fused
  multiply-adds. The reader moved to `z4c/z4c_sbc_ext.cpp`; the header keeps data
  members, the one-line `Extended()` and a declaration. No difference is masked: the
  package's run r2 (45 files of 7 set-ups identical with core-v0.5) and the regression
  below (the merged source, with two more branches that add members to `Particles`)
  both pass. The options are read only if present and the three hooks test
  `sbc.Extended()` and `sbc.ghost_falloff`, both false by default [VERIFIED by reading
  `z4c_sbc_ext.{hpp,cpp}`, `z4c_Sbc.cpp` 128-129, `z4c_tasks.cpp` 287, 312, and by the
  quick test Qf (ii)].
- **core/id-solver-2, the default far field.** `id_far = multipole` is on by default on
  a mesh with no periodic face and changes solved data against core-v0.5 (sizes below).
  It stands: the plain fill has an error of W at the faces that does not fall with the
  cell size (-8.6e-3, -9.3e-3 at 32, 64 cells) where the far field has +9.3e-4, +2.4e-4
  (test W1 of the package, not rerun by me); the solver's gate is open and no production
  run rests on its bytes [JUDGEMENT]; `id_far = robin` gives the old bytes for matter at
  rest (rerun below).
- **The nine never-set members of the mesh header** (request of package newton2):
  nothing to change. `Mesh::ZeroUnusedMeshIndcs` (`mesh/mesh.cpp` 366-376) zeroes them
  since core-v0.4, in the constructor and after reading a restart header
  (`mesh/build_tree.cpp` 363). Read from the files: 12 mesh restart files of the tests
  below, all nine members zero in each (prediction H held).

## Branches left out

core/clump-table and core/oblate: not closed when the candidate was built (the first
was running tests, tip 16cce79e of 12:57Z; the second does not hold core-v0.5 and has no
READY for a merged state). Reasons in `tracks/core/stage/G2/OPEN.md`, section core-v0.6.
No branch that passed is left out, and nothing of the three merged branches was left
out of the merge.

## Byte regression on processors against release core-v0.5: PASS

Run core-20261121-130202-7cf7db8 (driver `tracks/core/analysis/release/regress_v04.py`,
3 cores). Candidate `athena_cpu` (sha256 2ec1f232...) against the release executable
`/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena`, the twelve set-ups of wave 1, new
options absent. Every output file except the log is compared; for jeans and binary the
result lines of the log as well. Classes as in `RELEASE-v0.4.md` (a: 36 unset restart
bytes; b: `last_time` lines of an embedded parameter dump); against core-v0.5 neither
should appear, and neither does. Prediction R held.

| Set-up | What | Items | identical | a | b | a+b | other | Verdict |
|---|---|---|---|---|---|---|---|---|
| geo | test particle in Kerr, analytic metric, midpoint | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| boris | the same, spacetime-Boris pusher on the lattice | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| dep | deposit on a statically refined flat mesh | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| east | periodic cosmology with Z4c, 16^3, 20 steps | 12 | 12 | 0 | 0 | 0 | 0 | pass |
| os | Oppenheimer-Snyder ball with Z4c, refined, 3 steps | 16 | 16 | 0 | 0 | 0 | 0 | pass |
| jeans | gas with self-gravity, Jeans wave, 20 steps | 5 | 5 | 0 | 0 | 0 | 0 | pass |
| binary | gas with self-gravity, four levels, 1 step | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| c1 | cluster on the analytic Kerr metric, 2000 particles | 5 | 5 | 0 | 0 | 0 | 0 | pass |
| c2 | static mesh metric, deposit, filter | 3 | 3 | 0 | 0 | 0 | 0 | pass |
| c3 | cluster on a refined mesh, deposit, excision | 14 | 14 | 0 | 0 | 0 | 0 | pass |
| c4 | homogeneous universe, Z4c with particle sources | 4 | 4 | 0 | 0 | 0 | 0 | pass |
| c5 | kick deck with the kick off: restart files, removal | 10 | 10 | 0 | 0 | 0 | 0 | pass |
| all | | 75 | 75 | 0 | 0 | 0 | 0 | PASS |

Figure: run core-20261121-133153-89d375b (`R/fig_regress_v04.png`, looked at: twelve
bars, one colour).

The other two processor builds against the same release executable, same driver:

| Build | Run | Result |
|---|---|---|
| `athena_cpu_mpi` started without mpirun | core-20261121-132245-c02f6b7 | 75 of 75 items identical: PASS (prediction Rm held) |
| `athena_cpu_omp` at one thread | core-20261121-133243-74c17ff, judged in core-20261121-134007-f8513b0 | every run status 0; 32 of 75 identical, 43 differ at rounding level: NOT a byte reference (prediction Ro held) |

For the threaded build, columns above 1e-6 of the largest column of each history: module
histories within 1.2e-15, constraint statistics within 1.4e-10 (east, largest
Hamiltonian constraint) and 1.9e-12 (c4); geo and jeans are identical; the history of
c5 has one entry per record that is not finite in both builds and agrees in all others.
These are the numbers of core-v0.5 (31 of 75; 1.2e-15, 1.4e-10, 1.9e-12). Figure
`scratch/core/core-20261121-134007-f8513b0/fig_hst_pair.png` (looked at: four bars, east
and c4, all other histories without a difference in their large columns). Two earlier
calls of the judging script are on record: core-20261121-133938-efeb8b4 failed through
a fault of the script, and core-20261121-133947-f7d1d50 refused the history of c5
because of its non-finite entries and drew it as a bar at the top edge.

## Quick test of every merged branch on processors: PASS

Run core-20261121-130813-710b3cc (driver `analysis/release/quick_v06.py`, 3 cores, 12
AthenaK runs). One example per branch, serial candidate against the processor
executable the branch published, byte for byte; and the stock values of the faces
options against the release:

| Case | Branch | Input | Against | Files | identical |
|---|---|---|---|---|---|
| n_sp | newton-2 | `problems/newton/periodic_fft.athinput`, wave of 32^3 particles, tlim = 1, `newton_fft_symbol = spectral`, one group history, restart files | `core_newton-2/athena_cpu` | 14 | 14 |
| n_7p | newton-2 | the same with `seven_point` | `core_newton-2/athena_cpu` | 14 | 14 |
| f_full | z4c-faces | `problems/tests/z4c_faces.athinput`, 8 steps, the full set | `core_z4c-faces/athena_cpu` | 5 | 5 |
| f_stock | z4c-faces | the same with `extrap_order = 2`, `ghost_falloff = false`, `sbc_variant = sommerfeld`, `sbc_speed = unit` | release core-v0.5 | 5 | 5 |
| all | | | | 38 | 38 |

Predictions Qn and Qf (i), (ii) held. f_stock shows that the stock values of the new
options give the release's bytes on a refined vacuum puncture with outflow faces.

Initial-data solver, the regressions of its package repeated with the candidate:

| Check | Run | Result |
|---|---|---|
| `regress_m1.py`, first-pass examples at 32 cells against release core-v0.5, `id_far = robin` | core-20261121-131148-6efd1b8 | Gaussian at rest 8, expanding ball 9, torus 8 files byte-identical; moving Gaussian: same 17 outer iterations, psi to 6.0e-15, W to 5.1e-16 |
| the same with no new option (far field on by default) | same run | torus 8 files identical; psi changes by 9.7e-9 (Gaussian at rest), 3.6e-8 (ball), 1.48e-6 (moving Gaussian), W of the moving Gaussian by 2.67e-3 of its maximum; iteration counts 17, 17, 25, 23 unchanged |
| `regress_r2.py --same`, eight second-pass cases of run core-20261121-080135-890689a replayed (puncture in mode code with and without matter, three static levels, moving Gaussian with the far field, refined Gaussian, refined torus with moving matter, Zel'dovich ball with its evolution, puncture with momentum in a moving shell) | core-20261121-131250-f8df905 | 79 of 79 files byte-identical with the branch executable's |

Prediction Qi held in both parts; the numbers of the default far field are those of the
package's M1. Figure `tracks/core/analysis/idsolve2/figs/regress_r2_v06.png` (looked at:
eight bars, none differing).

The combination the merge creates (prediction C held): a Bowen-York puncture
(`problems/idsolve/puncture.athinput` at 32 cells) solved by `id_solve`, then 8 steps,
without and with the full set of faces options, in both residual modes. All four runs
end with status 0 and finite histories; the record of the solve is byte-identical with
and without the faces options (5 outer iterations in mode stencil, 22 in mode code with
max|H| 6.4e-12 after the solve); the mean |H| of the mesh after 8 steps is 4.9e-4
without and 3.6e-4 with the options. I had expected that the solver's call of
`Z4c::ApplyPhysicalBCs` (`nrpic_idsolve.cpp` 1787), which now also applies the fall-off
fill, might change the record in mode code; it does not. Figure
`scratch/core/core-20261121-133153-89d375b/quick/fig_quick_v06.png` (looked at; the
first drawing had the legend over two bars and was drawn again).

Restart headers (prediction H held): 12 mesh restart files of the regression and of the
quick test, the nine members cnx1 to cke zero in each.

## Card check of `athena_gpu`

**Merged card executable: PASS (prediction K6 held).** Run core-20261121-132052-f330004
(Slurm job 4800, list `analysis/release/card_v06.list`, 0.3 card-hours asked, 46 s
used), submitted at 13:20Z, ran at 15:21Z (07:21 PST): six new cases (Newtonian plane
wave with both symbols, the faces example, the solved puncture with the faces options,
two cases of the solver) and the nine cases of core-v0.5; every case status 0.

| Check (K6) | Judged in | Bound | Result |
|---|---|---|---|
| status of the fifteen cases | both | 0 | all 0 |
| Newtonian histories of n_sp, n_7p (`*.newton.hst`, `*.newton.g1.hst`), columns above 1e-6 of the largest | core-20261121-154700-2de4974 (`card_v06.py`) | 1e-10 | 1.6e-11 (n_sp), 1.3e-11 (n_7p): held |
| every history of f_full and c_cd1 (faces options) | same | 1e-7 | f_full identical (0); c_cd1 1.9e-10 (constraint statistics): held |
| solver record of c_cd1, p5_mov_n64, g_smr1 | same | outer iterations equal (one on the refined mesh); psi_max to 1e-12 (1e-9 refined) | outer 22, 34, 20 on both; psi_max equal in 16 digits for c_cd1 and p5_mov_n64, 2.5e-15 for g_smr1: held |
| nine cases of core-v0.5, K1 to K6 of that release | core-20261121-154710-220c1b0 (`card_v05.py`) | as in core-v0.5 | held: deposit sums 2.3e-13 at worst (trk), identity 9.9e-16, source dumps 3.1e-14 |

Not bounded by K6 and different between card and processors, as for core-v0.5: ratios
of residuals at rounding level in the constraint statistics. g_smr1 `gauss.cstat.hst`
column 11 (Hr_max, the largest |H| over its local scale): 1.380745 on processors,
1.379534 on the card (8.8e-4), while column 9 (H_max, absolute) agrees to 1.2e-12 of
its value [VERIFIED by reading the two files]; trk column 15 (0.14 of its value, as in
core-v0.5), s3g 1.4e-3, usr 4.0e-3 (constraint statistics of vacuum cases; the module
histories of s3g and usr are judged by K1 to K6). Figures
`scratch/core/core-20261121-154700-2de4974/fig_card_v06.png` (looked at: every bar of
n_sp, n_7p below the blue dashed bound 1e-10, c_cd1 below the red 1e-7; the one bar
above, g_smr1 cstat at 9e-4, is Hr_max, which no bound covers: the dashed lines are
drawn across the whole width although each applies to its own cases) and
`scratch/core/core-20261121-154710-220c1b0/fig_card_v05.png` (looked at: panel a below
every bound; panel b high only for s3g, usr, trk). Commands used:
```
harness/bin/nrpic-run finish core-20261121-132052-f330004
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K6 judged, new cases" -- python3 tracks/core/analysis/release/card_v06.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-132052-f330004 --quick /data/haiyangw/nrpic/scratch/core/core-20261121-130813-710b3cc --r2 /data/haiyangw/nrpic/scratch/core/core-20261121-131250-f8df905 --out '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K6 judged, cases of core-v0.5" -- python3 tracks/core/analysis/release/card_v05.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-132052-f330004 --cpu /data/haiyangw/nrpic/scratch/core/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'
```
(`card_v06.py` was run once on processor data in place of card data, by hand, to test
the script: it prints CARD PASS there, which says nothing about the card.)

**Card executables of the branches** (the source of each capability as merged; these
checks ran):

| Branch | Card run | Judged in | Result |
|---|---|---|---|
| core/id-solver-2 (395e17d8), check Kc, five cases, three of them on refined meshes | core-20261121-125651-edde517 (Slurm 4793, 87 s) | core-20261121-133219-2c8f63c | prediction Kc of the package held: outer iterations 34, 16, 20, 27, 5 on card and processors; psi within 2.2e-15 and W within 2.5e-14 of their maxima (bounds 1e-12 uniform, 1e-9 refined); P_ADM_x of `p5_mov_n64` 5.499999519755e-01 on both. Figure `analysis/idsolve2/figs/card_k_kc.png` (looked at) |
| core/z4c-faces (f6f9a0df), check k1, vacuum puncture 4 steps stock and 8 steps with the full set | core-20261121-083511-2cff9df (Slurm 4782) | core-20261121-134059-e3ab6f3 | largest difference from the processor runs 7.3e-12 in both (bound 1e-7): held. The judging run carries status failed because the comparison lists the card's log and memory files as missing on the processor side; no data file is missing. Not run: the release card executable on the same steps (k2) |
| core/newton-2 (67ca9ce1) | by its package (Slurm 4777) | package | plane wave with both solvers within 1.5e-15 of the box, embedded ellipsoid within 3.2e-14 (`branches/READY.newton-2`) |

Card time of this session: 0.024 card-hours used (Kc, 87 s), 0.3 asked for job 4800.

## Release builds against the candidate

The clerk built the release executables from main after the merge (merge 36e51bae; the
source trees of the tag and of main are the same). Their checksums differ from the
candidate's (processor 91fc59b3... against 2ec1f232...; card ea473498... against
168e5da6...), as builds in other directories do [VERIFIED by `sha256sum`]. Predictions
R6 and G6: `tracks/core/JOURNAL.md`, entry of 2026-11-21T15:46Z (session core-lead-6).

| Check | Run | Result |
|---|---|---|
| `.work/build_cpu_v06/src/athena` against the candidate `athena_cpu`, `regress_v04.py`, twelve set-ups, 3 cores | core-20261121-154737-dc1e4c1 (figure core-20261121-155317-1ee04bf) | 75 of 75 items identical, classes a, b, other empty: PASS (R6 held). Figure `fig_regress_v04.png` looked at: twelve bars, one colour |
| `.work/build_gpu_v06/src/athena` on the fifteen cases of `card_v06.list`, against the processor runs (`card_v06.py`, `card_v05.py`) and the candidate's card run of job 4800 (`card_pair.py`) | core-20261121-154654-d3ec487, Slurm job 4810 (ran 17:20-17:21Z, 48 s), 0.1 card-hours asked; judged in core-20261121-202028-a32d12c (`card_v06.py`), core-20261121-202041-0b6d418 (`card_v05.py`), core-20261121-202057-a5b2ed6 (`card_pair.py`) | PASS on the release criteria: fifteen cases status 0; `card_v06.py` CARD PASS (Newtonian histories 1.6e-11, faces 1.9e-10, solver iterations equal) and `card_v05.py` CARD PASS (K1-K6; sums 2.3e-13, identity 9.9e-16, dumps 3.1e-14). Against the candidate's card run (job 4800): f_full, s3g, usr byte-identical in every file; module histories within 2.2e-15. Prediction G6 (ii) is refuted as written in one part: its 1e-12 bound on every history column fails in the normalized constraint columns of `cstat.hst` (Hr_max, Hr_mean, Mr_max: g_smr1 1.9e-3, trk 2.0e-2, p5_mov_n64 1.4e-11, peak 2.1e-10, cluster 7.6e-10), ratios of rounding-level residuals that carry the card's non-repeatable atomic deposit [JUDGEMENT]; H_max is not among them. Journal entry of 2026-11-21T20:26Z. Figures `fig_card_v06.png`, `fig_card_v05.png`, `fig_card_pair.png` looked at |

```
harness/bin/nrpic-run finish core-20261121-154654-d3ec487
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "G6 (i) new cases" -- python3 tracks/core/analysis/release/card_v06.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-154654-d3ec487 --quick /data/haiyangw/nrpic/scratch/core/core-20261121-130813-710b3cc --r2 /data/haiyangw/nrpic/scratch/core/core-20261121-131250-f8df905 --out '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "G6 (i) cases of core-v0.5" -- python3 tracks/core/analysis/release/card_v05.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-154654-d3ec487 --cpu /data/haiyangw/nrpic/scratch/core/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "G6 (ii) release card build against the candidate's card run" -- python3 tracks/core/analysis/release/card_pair.py --a /data/haiyangw/nrpic/scratch/core/core-20261121-154654-d3ec487 --b /data/haiyangw/nrpic/scratch/core/core-20261121-132052-f330004 --cases n_sp,n_7p,f_full,c_cd1,p5_mov_n64,g_smr1,s3g,usr,trk,peak,dep,depp,fine,finet,cluster --out '$NRPIC_RUN_DIR'
```

## Known defects

`tracks/core/stage/G2/OPEN.md`, section of core-v0.6, items a to o; the READY of the
published executables. In short:
- five things change in runs with `id_solve = true` without an option, first the far
  field at the faces (changelog);
- the faces options reduce the reflection and do not remove it; no constraint-absorbing
  treatment of Theta; r is the distance from the mesh origin;
- solver: vector part stalls at level boundaries in mode code; punctures with momentum
  or spin have an error floor set by the distance of the faces; one rank;
- Newtonian mode: the Fourier solver needs one pack on a uniform periodic mesh; a cold
  lattice with fewer than one particle per cell and direction is pushed as a whole;
- none of the three capabilities was run on several ranks, the faces options and the
  Fourier solver not with the threaded build, nothing with adaptive refinement;
- the merged card executable had not run when this was written (it ran later: job 4800,
  PASS, section "Card check");
- the capability tests of the packages and the verification ladder were not rerun on
  the merged executables: the release rests on the byte regression, on one example per
  branch against the branch's own executable, and on the solver's regressions repeated
  byte for byte.

## For the release clerk

Merge `core/nrpic` into main; tag `core-v0.6` (the source commit of the first line, or
the merge on main: the source trees are the same); build `.work/build_gpu_v06` and
`.work/build_cpu_v06` from that source, and if wanted the threaded and the MPI builds;
copy `tracks/core/interfaces/*.md` to `coord/INTERFACES/` (new since core-v0.5:
`z4c_faces.md`, `id_solver2.md`, `REQUESTS_NEWTON2.md`; changed: `newtonian_mode.md`);
announce to all owners the default far field of `id_solve` (tracks A, D, F: a solved
slice on a mesh with no periodic face is not the slice core-v0.5 made; `id_far = robin`
restores it for matter at rest). Compare a release build with the candidate by
`regress_v04.py`, not by checksums.

How to repeat the checks:
```
cd /data/haiyangw/nrpic/wt/core
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v05/src/athena --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 3
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/quick_v06.py --new <athena_cpu> --base /data/haiyangw/nrpic/.work/build_cpu_v05/src/athena --out '$NRPIC_RUN_DIR' --cores 3 --regress <regression run directory>
harness/bin/nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/regress_m1.py --base /data/haiyangw/nrpic/.work/build_cpu_v05/src/athena --new <athena_cpu> --jobs 3     # then: git checkout -- tracks/core/analysis/idsolve2/regress_m1.json tracks/core/analysis/idsolve2/figs/regress_m1.pdf
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher batch --list tracks/core/analysis/release/card_v06.list --exe <athena_gpu> --gpu-hours 0.3 --purpose "..."
```
