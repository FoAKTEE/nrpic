RELEASE core-v0.5 c3eb42e0bf9b9804e569f7e6dd1603ac805a60eb REGRESSION PASS

# Release candidate core-v0.5: four wave-3a source branches of core on top of core-v0.4

Written by the lead of core on 2026-11-21 (decision 0019 item 4; batch 2a). The commit of
the first line is the source commit: the last commit of `core/nrpic` that changes
`athenak/`, `python/`, `problems/` or `scripts/` (the merge of core/mpi). Later commits
of `core/nrpic` add records only (`tracks/core/`, `docs/FORMATS.md`); `git diff c3eb42e0
<tip> -- athenak python problems scripts` is empty [VERIFIED at the tip that holds this
file]. Predictions and outcomes: `tracks/core/JOURNAL.md`, entry of 2026-11-21T06:32Z.
Options, behaviour that changes without an option, formats: `tracks/core/CHANGELOG.md`,
section core-v0.5.

## Executables of the candidate

`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/`, all four built from the source
commit in new build directories of `wt/core` (COMMIT there has the commands and times):

| File | Build | sha256 |
|---|---|---|
| `athena_cpu` | `scripts/build_cpu.sh` (Kokkos Serial, -O2 -g), `.work/build_cpu_v05rc` | b462068a...6c4fce57bb |
| `athena_gpu` | `scripts/build_gpu.sh` (CUDA 12.6, one A100, no MPI), `.work/build_gpu_v05rc` | 9d08dc13...6d6ebe0389 |
| `athena_cpu_omp` | `scripts/build_cpu_omp.sh` (Kokkos OpenMP, -O3 -DNDEBUG -g), `.work/build_omp_v05rc` | 4d327a4d...83f37dbfea |
| `athena_cpu_mpi` | `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh` (Open MPI 5.0.1), `.work/build_cpu_mpi_v05rc` | 003736e1...7d1800a3dc |

With them `COMMIT`, `SHA256SUMS`, `READY` (every new option with one example input, what
is tested and what is not, known defects) and `branches/READY.<branch>` (the READY of
each merged branch).

## Branches merged, in this order (one merge commit each)

| Branch | Tip merged (source) | Merge commit | Review |
|---|---|---|---|
| core/scalar-3 | 88544a5b (5cc28211) | 604e9ad8 | pass |
| core/build-openmp | 983351aa (a9c34e7a) | 0d0f5ba5 | pass |
| core/cosmo-amr | bb360ef2 (1548d49c, the corrected `deposit_fine_shape`) | e103b3e3 | pass; three things act without an option (changelog) |
| core/mpi | f9a2c022 (ca46836a) | c3eb42e0 | pass, with stops added for seven options on several ranks |

Review notes of every branch and the resolutions: journal entry of 2026-11-21T06:32Z
and the four merge commit messages. Conflicts: `tracks/core/interfaces/rng.md`,
`particles.hpp`, `CMakeLists.txt`, `nrpic.cpp`. Resolved without a conflict marker
asking for it, so that both sides keep their behaviour: the fine-shape additions of
cosmo-amr go through the deposit target of build-openmp; the private copies of the
threaded deposit are summed before the clouds of other ranks are added (mpi); a run on
more than one rank stops with a message for `removal_record`, `acc_nsphere`,
`peri_count`, `perturb_gamma`, `id_solve`, `region_dcycle`, `deposit_fine_shape`.

## Branches left out

None of the four offered. Not in this release by plan, unfinished (for core-v0.6):
core/id-solver-2, core/clump-table, core/newton-2, core/oblate, core/z4c-faces
(`tracks/core/stage/G2/OPEN.md`, section of core-v0.5).

## Byte regression on processors against release core-v0.4: PASS

Run core-20261121-063859-e410ee3 (driver `tracks/core/analysis/release/regress_v04.py`,
6 cores, 265 s). Candidate `athena_cpu` (sha256 b462068a...) against the release
executable `/data/haiyangw/nrpic/.work/build_cpu_v04/src/athena` (sha256 daada48f...),
the twelve set-ups of wave 1, new options absent. Every output file except the log is
compared; for jeans and binary the result lines of the log as well. Classes as in
`RELEASE-v0.4.md` (a: 36 unset restart bytes; b: `last_time` lines of an embedded
parameter dump); against core-v0.4 neither should appear, and neither does.

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

Table and figure: run core-20261121-071123-2b012d4
(`scratch/core/core-20261121-071123-2b012d4/fig_regress_v04.png`, looked at: twelve bars,
one colour).

The other two processor builds against the same release executable, same driver:

| Build | Run | Result |
|---|---|---|
| `athena_cpu_mpi` started without mpirun | core-20261121-065743-1202666 | 75 of 75 items identical: PASS |
| `athena_cpu_omp` at one thread | core-20261121-070623-077b056 | 31 of 75 identical, 44 differ at rounding level: NOT a byte reference |

For the threaded build the histories of the particle module agree with the release in
every column above rounding to 1.2e-15, the constraint statistics to 1.4e-10 (east,
largest Hamiltonian constraint) and 1.9e-12 (c4); geo and jeans are identical; the
result lines of the multigrid log of binary differ; all runs end with status 0. My
prediction (identical in the ten set-ups without multigrid) failed. The verdict of the
first line is that of the serial executable, the reference of byte comparisons in this
program; the threaded executable is released as a build whose results agree with it to
rounding.

A third build, not published, tested which of the two differences between the builds
does it: the threaded build with the flags of the serial build (`OMP_OPT=debug
scripts/build_cpu_omp.sh`, -O2 -g) at one thread, run core-20261121-071842-f5a8b56: 53
of 75 items identical. The nine set-ups that do not evolve the spacetime (geo, boris,
dep, jeans, binary, c1, c2, c3, c5) are identical; the three with Z4c (east, os, c4)
differ at rounding (module histories 8.8e-16, constraint statistics 1.5e-10), with
identical initial data. So the flags change the last bits of the particle module and
the OpenMP build those of runs with Z4c; my prediction that the flags alone do it was
refuted, and no threaded build is a reference for byte comparisons.

## Quick test of every merged branch on processors: PASS

Runs of core-20261121-065009-29b855c (driver `analysis/release/quick_v05.py`, 6 cores,
31 AthenaK runs), judged in core-20261121-065726-bf06a85. The first call ended FAIL
through two errors of the driver's checks, not of the executables (journal: it compared
whole histories where the fine shape must change the probe and the extrema of E, and it
applied the bound of the module's history to the constraint statistics); the second
call evaluates the same runs without running anything.

One example per branch, serial candidate against the processor executable the branch
published, byte for byte:

| Case | Branch | Input | Files AthenaK wrote | identical | a, b, other |
|---|---|---|---|---|---|
| s3g | scalar-3 | `problems/scalar/sr_stochastic_gauge.athinput` (`con_signed`), 12 steps | 6 | 6 | 0 |
| usr | scalar-3 | `problems/scalar/usr_stochastic.athinput`, 12 steps | 6 | 6 | 0 |
| trk | cosmo-amr | `problems/cosmo_amr/flrw_tracker.athinput`, 12 steps | 5 | 5 | 0 |
| peak | cosmo-amr | `problems/cosmo_amr/peak_amr.athinput` as case ladder of `t9_peak.py` (32^3, three levels, 10 steps) | 5 | 5 | 0 |
| dser | build-openmp | `problems/tests/deposit_threads.athinput` against `athena_cpu_serial` | 1 | 1 | 0 |
| all | | | 23 | 23 | 0 |

In peak the mesh goes from 64 to 120 MeshBlocks with 32768 particles kept and the
deposit identity at 2.0e-14; s3g writes the 27 columns of `con_signed`.

Threaded build (`athena_cpu_omp`), the refined deposit test with a dump of the sources
in double precision; differences over the largest number of the file:

| Check | Value | Bound |
|---|---|---|
| `deposit_threads = private`, two runs at 4 threads | byte-identical | identical |
| private, 4 threads against 1: history; dump | 2.1e-18; 1.2e-16 | 1.3e-12 (READY of the branch) |
| atomic at 4 threads against private at 1: history; dump | 2.1e-18; 1.2e-16 | 1.3e-12 |
| threaded at 1 thread against the serial build: history; dump | 4.2e-22; 1.1e-14 | 1.3e-12 |
| serial build with and without the line `deposit_threads` | same bytes; it prints "this executable adds atomically" | same bytes |
| deposit identity, worst of the six runs | 5.5e-14 | 1e-13 |
| NEW: `deposit_fine_shape` (cic) with private, two runs at 4 threads | byte-identical | identical |
| fine shape, private, 4 threads against 1: history; dump | 1.1e-18; 2.1e-16 | 1e-12 |
| fine shape, atomic at 4 threads against private at 1: dump | 3.6e-16 | 1e-12 |
| fine shape, threaded at 1 thread against the serial build: dump | 1.1e-14 | 1e-12 |
| fine shape with tsc, private at 4 threads against the serial build: dump | 7.5e-15 | 1e-12 |
| fine shape against plain cic, serial: dump; mesh integrals over sum m W | 0.52; 5.2e-14 | above 1e-3 (the branch is taken); 1e-13 |
| deposit identity with fine shape, worst of the seven runs | 3.0e-14 | 1e-13 |

The rows marked NEW test the combination that exists only in the merged source (the
fine-shape branch of cosmo-amr adding through the deposit target of build-openmp).

MPI build (`athena_cpu_mpi`), 1 rank against 2 ranks, driver `analysis/mpi/mpi_tests.py`
of the package:

| Check | Value | Bound |
|---|---|---|
| Kerr swarm (2000 test particles, 2119 handed over): trajectories, metric at the particles, five snapshots, two particle restart files | 9 files byte-identical | identical |
| cluster with Z4c (4000 particles, 2786 handed over, 53923 deposit packets): positions | 3.1e-15 | 1e-13 |
| cluster: history of the module | 4.6e-13 | 1e-11 |
| cluster: constraint statistics (largest relative Hamiltonian constraint) | 8.5e-10 | none (the package's own run: 8.502235846576052e-10, the same digits) |
| cluster: deposit identity on 1 and on 2 ranks | 7.8e-15, 1.7e-15 | 1e-14 |
| every file of these four runs against the package's runs with its branch executable | 10 of 12, 11 of 13, 20 of 24, 21 of 25 identical; the others are mesh restart files with identical data outside the 36 header bytes that core-v0.4 zeroes | no other difference |
| `deposit_fine_shape` on 2 ranks | stops, status 1, message names the option | stop with a message |
| the same deck on 1 rank of the MPI build | status 0 | runs |

My bound "history within 1e-11" failed for the constraint statistics as I had written it
(I took the READY's number for one file as the bound of all); the merged executable
gives the package's values. Figure: `scratch/core/core-20261121-065726-bf06a85/
fig_quick_v05.png` (looked at; a first version with overlapping labels was redrawn).

## Card check of `athena_gpu`: PENDING (one job in the queue)

Card run core-20261121-070946-1907f7b (Slurm job 4772, 0.2 card-hours asked, list
`analysis/release/card_v05.list`: nine cases, the decks of the quick test and the
cluster of package mpi on one rank) was submitted at 07:09Z behind jobs of other owners
and had not started when this file was written. Until it is judged, `athena_gpu` of
this candidate has NOT run on a card. What is known of its source on a card: the card
executable of core/cosmo-amr (same deposit) passed its check (next section), and the
card executables of core/scalar-3 and core/build-openmp ran their packages' cases
(READY of the branches); the merged card executable itself: nothing.
To close: `harness/bin/nrpic-run finish core-20261121-070946-1907f7b`, then
`card_v05.py --card <its directory> --cpu
/data/haiyangw/nrpic/scratch/core/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'`
as a registered local run, against the predictions K1 to K6 of the journal.

## Check of the card executable of core/cosmo-amr (job 4763 of the package)

The package left one card job unjudged (T14b: its card executable of source 1548d49,
the deposit this release has, on seven decks). It finished; judged with the package's
script, read-only on its outputs, run core-20261121-063923-5ed0a51: homogeneous cases
uniform to 1.1e-13 (bound 1e-12), lapse equal to the processor runs to 1.8e-15, tracker
within 4.4e-16 and the same MeshBlock counts, the ladder case with 64 to 120 MeshBlocks
on card and processors, identity 2.2e-16 (bound 1e-13), largest relative constraint
within 9.2e-12 (bound 1e-9), guard case status 3 with its file (stop at cycle 16
against 18, not predicted). The prediction of the package's journal held. Figure
`scratch/core/core-20261121-063923-5ed0a51/fig_t14_card.png` (looked at). Not judged:
case Sf, and T10g, the scouting run of the same job (it ended with the guard at
t = 12.504).

## Known defects

`tracks/core/stage/G2/OPEN.md`, section of core-v0.5, items a to m; the READY of the
published executables. In short:
- five things act without an option (guard with exit status 3; the finder's summary and
  the tracker file in the `-d` directory; mapping into a periodic box; the refinement
  function of `nrpic_cosmo`; several ranks no longer refused): changelog;
- `athena_cpu_omp` does not give the bytes of `athena_cpu`, at one thread either;
- on several ranks eleven options stop the run; the horizon finder at four cells per
  horizon radius gives rank-dependent surfaces, so excision by a horizon can differ
  between rank counts (the same sensitivity on one rank: run
  core-20261120-223502-f9a2c02 of package mpi); the constraint statistics differ by
  1e-9 between rank counts;
- `deposit_fine_shape`: no limiter (negative leaf-cell energy in sparse regions), one
  rank only; quadratic and cubic clouds are not uniform across a level boundary (use
  cic on refined meshes); refinement levels take one global step;
- untested: MPI with threads; `<particles_amr>` and the guard on several ranks;
  adaptive refinement under threads; the kernels of core-v0.4 under threads; an MPI
  card build (not built for this release);
- carried from core-v0.4 unchanged: `hmean_tol` acts on the surface integral; the
  particle restart file grows with `max_nmb_per_rank`; the initial-data solver on
  uniform meshes without punctures; the wrong comment in `particles.hpp`;
- the capability tests of the packages and the verification ladder were not rerun on
  the merged executables: the release rests on the byte regression, on one example per
  branch against the branch's own executable, on the package's runs on 1 and 2 ranks
  reproduced byte for byte, and on the tests of the two combinations the merge created.

## For the release clerk

Merge `core/nrpic` into main; tag `core-v0.5` (the source commit of the first line, or
the merge on main: the source trees are the same); build `.work/build_gpu_v05` and
`.work/build_cpu_v05` from that source, and if wanted the threaded and the MPI
processor builds (`scripts/build_cpu_omp.sh`; `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON"
scripts/build_cpu.sh`); copy `tracks/core/interfaces/*.md` to `coord/INTERFACES/` (new
since core-v0.4: `scalar_field_3.md`, `threaded_build.md`, `cosmo_amr.md`, `mpi.md`,
`REQUESTS_A2.md`; changed: `rng.md`); announce to all owners the five things that act
without an option, first the guard's exit status 3 and the new place of the finder's
summary and the tracker file. A processor build from the same source in another build
directory need not have the sha256 of `athena_cpu` [JUDGEMENT, not tested]: compare
outputs with `regress_v04.py`, not checksums.

How to repeat the checks:
```
cd /data/haiyangw/nrpic/wt/core
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 6 --purpose "..." -- python3 tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v04/src/athena --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 6
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 6 --purpose "..." -- python3 tracks/core/analysis/release/quick_v05.py --serial <athena_cpu> --omp <athena_cpu_omp> --mpi <athena_cpu_mpi> --out '$NRPIC_RUN_DIR' --cores 6
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher batch --list tracks/core/analysis/release/card_v05.list --exe <athena_gpu> --gpu-hours 0.2 --purpose "..."
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "..." -- python3 tracks/core/analysis/release/card_v05.py --card <card run directory> --cpu <quick run directory> --out '$NRPIC_RUN_DIR'
```
