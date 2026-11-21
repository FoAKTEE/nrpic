RELEASE core-v0.4 f93231854cf038db56bd8c37a47c39c2ba6b1f14 REGRESSION PASS

# Release candidate core-v0.4: the seven wave-2 source branches of core

Written by the lead of core on 2026-11-21 (decision 0019 item 4). The commit of the
first line is the source commit: the last commit of `core/nrpic` that changes
`athenak/`, `python/`, `problems/` or `scripts/` (the merge of core/collisions-2). Later
commits of `core/nrpic` add records only (`tracks/core/`, `docs/COLLISIONS.md`) and merge
main; `git diff f9323185 <tip> -- athenak python problems scripts` is empty [VERIFIED at
the tip abbea8ac]. Predictions and outcomes: `tracks/core/JOURNAL.md`, entries of
2026-11-20T22:10Z and 2026-11-21T02:58Z. Options, corrections, formats:
`tracks/core/CHANGELOG.md`, section core-v0.4.

## Executables of the candidate

`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`: `athena_cpu` (sha256
8bff3107...8955d506), `athena_gpu` (sha256 ab3ee2a6...4143623b), `COMMIT`, `SHA256SUMS`,
`READY` (every new option with one example input, what is tested, known defects),
`branches/READY.<branch>` (the READY of each merged branch). Both were built from the
source commit in new build directories after the last merge
(`wt/core/.work/build_cpu_v04rc`, `wt/core/.work/build_gpu_v04rc`; 221 and 225 objects
compiled; tree clean).

## Branches merged, in this order (one merge commit each)

| Branch | Tip merged | Merge commit | Review |
|---|---|---|---|
| core/requests-b | f134b775 | 3ab47062 | pass |
| core/gauge | 58d10777 | 120aa7cf | pass |
| core/scalar-2 | 207424d2 | 54dc527e | pass |
| core/clump-curvature | 56d7335c | e2498da4 | pass |
| core/id-solver | d88ff4f9 | de42b294 | pass |
| core/requests-adf | b6041dbc | 7b0fcf27 | pass, with three corrections that act without an option (changelog) |
| core/collisions-2 | 8c03bc96 | f9323185 | pass |

Late commits of two branches, records only (no file under `athenak/`, `python/`,
`problems/`, `scripts/`), merged afterwards: core/requests-adf bc38aafc (148a302e),
core/collisions-2 4c798e7a (e9644451). Review notes of every branch: journal entry of
2026-11-20T22:10Z.

## Branches left out

None. (The nine wave-3a branches are not part of this release by plan: core-v0.5.)

## Byte regression on processors against release core-v0.3: PASS

Run core-20261120-221607-4985804 (driver `tracks/core/analysis/release/regress_v04.py`,
3 cores, 398 s). Candidate `.work/build_cpu_v04rc/src/athena` (sha256 8bff3107...)
against the release executable `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`
(sha256 d983155b...), the twelve set-ups of wave 1 with the arguments of
`tools/regress_relativistic.py` and `analysis/rng/run_regression.py`, new options
absent. Every output file except the log is compared; for jeans and binary the result
lines of the log as well. Classes: identical; a = restart file that differs only in the
36 bytes of the nine never-set members of the mesh header (zero in the candidate,
garbage in the release); b = file that differs only in `last_time = ...` lines of its
embedded parameter dump (the corrected `Driver::Finalize`); other = anything else.

| Set-up | What | Items | identical | a | b | a+b | other | Verdict |
|---|---|---|---|---|---|---|---|---|
| geo | test particle in Kerr, analytic metric, midpoint | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| boris | the same, spacetime-Boris pusher on the lattice | 2 | 2 | 0 | 0 | 0 | 0 | pass |
| dep | deposit on a statically refined flat mesh | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| east | periodic cosmology with Z4c, 16^3, 20 steps | 12 | 12 | 0 | 0 | 0 | 0 | pass |
| os | Oppenheimer-Snyder ball with Z4c, refined, 3 steps | 16 | 11 | 5 | 0 | 0 | 0 | pass |
| jeans | gas with self-gravity, Jeans wave, 20 steps | 5 | 4 | 0 | 1 | 0 | 0 | pass |
| binary | gas with self-gravity, four levels, 1 step | 1 | 1 | 0 | 0 | 0 | 0 | pass |
| c1 | cluster on the analytic Kerr metric, 2000 particles | 5 | 5 | 0 | 0 | 0 | 0 | pass |
| c2 | static mesh metric, deposit, filter | 3 | 3 | 0 | 0 | 0 | 0 | pass |
| c3 | cluster on a refined mesh, deposit, excision | 14 | 10 | 0 | 4 | 0 | 0 | pass |
| c4 | homogeneous universe, Z4c with particle sources | 4 | 4 | 0 | 0 | 0 | 0 | pass |
| c5 | kick deck with the kick off: restart files, removal | 10 | 7 | 3 | 0 | 0 | 0 | pass |
| all | | 75 | 62 | 8 | 5 | 0 | 0 | PASS |

Class a: `rst/os.0000{0..4}.rst`, `rst/kick.0000{0..2}.rst` (36 non-zero bytes in the
release, none in the candidate). Class b: `bin/JeansWave.hydro_w.00001.bin` (`<output2>
last_time` 0.1 in the release, 0 in the candidate) and four final bin files of c3
(`last_time` 200 or 50 against 0). No data byte, history line or snapshot differs.
Table and figure: run core-20261121-030235-cc329f5
(`scratch/core/core-20261121-030235-cc329f5/fig_regress_v04.png`, looked at). A first
call of the driver, core-20261120-220849-cea5881, ended FAIL through its own rule (the
case binary writes no file); same runs, rule corrected in 49858043.

## Quick test of every merged branch on processors: PASS

Run core-20261121-025955-bd47414 (driver `analysis/release/quick_v04.py`, 4 cores,
537 s): the example its READY names, run with the candidate and with the processor
executable the branch published, compared byte for byte.

| Case | Branch | Input (arguments in the driver) | Files AthenaK wrote | identical | b | other |
|---|---|---|---|---|---|---|
| lw16 | requests-b | `problems/tests/lw_oblique.athinput`, 16 cells | 4 | 3 | 1 | 0 |
| leak | gauge | `problems/cosmo/flrw_leak.athinput`, `lapse_leak = 5` | 6 | 6 | 0 | 0 |
| eta | gauge | `problems/puncture/by_eta.athinput`, profile on, 2 steps | 8 | 7 | 1 | 0 |
| sr | scalar-2 | `problems/scalar/sr_stochastic.athinput`, 12 steps | 4 | 4 | 0 | 0 |
| clump | clump-curvature | `problems/clump/clump_moving.athinput`, 1 step | 4 | 4 | 0 | 0 |
| ids | id-solver | `problems/idsolve/gaussian.athinput`, 32 cells | 6 | 6 | 0 | 0 |
| tracer | requests-adf | `problems/tests/tracer_mesh_circular.athinput` | 3 | 3 | 0 | 0 |
| pert | collisions-2 | `problems/tests/perturb_flat.athinput` | 2 | 2 | 0 | 0 |
| coll | collisions-2 | `problems/tests/coll_box_static.athinput`, 20 steps | 3 | 3 | 0 | 0 |
| all | | | 40 | 38 | 2 | 0 |

The two files of class b (`bin/lwo.z4c.00001.bin`, `bin/bye.con_H.00001.bin`) differ in
`last_time` lines only: the executables of requests-b and gauge do not have the
correction of requests-adf. Thirteen numbers of the candidate's runs lie in the bands
taken from the READY files:

| Number | Value | Band |
|---|---|---|
| oblique wave, error ratio 16 to 32 cells as an order | 3.168 | [3, 13] |
| lapse of the homogeneous universe against its equation, largest relative error | 6.26e-6 | [0, 2e-5] |
| stochastic slice, <\|H\|/[H]> at the start | 2.62e-12 | [2e-12, 3.2e-12] |
| stochastic slice, <\|M\|/[M]> at the start | 1.462e-5 | [1.40e-5, 1.52e-5] |
| moving clump, momentum-constraint norm with over without the curvature | 0.0082 | [0, 0.05] |
| initial-data solve, outer iterations | 17 | [10, 30] |
| initial-data solve, max\|H\| after | 1.55e-11 | [0, 5e-11] |
| tracer, smallest and largest radius in 300 M | 7.999998, 8.001151 M | [7.9999, 8.0001], [8, 8.0013] |
| tracer, last time | 300 | [299.9, 300.1] |
| collisions, change of sum M H over 20 steps | 3.2e-16 | [0, 1e-14] |
| collisions, pairs without a root; collisions | 0; 141140 | 0; [1e5, 2e5] |

Figure: `scratch/core/core-20261121-031018-6759268/fig_quick_v04.png` (remade from the
same runs with a corrected layout, looked at). Read with care: the oblique-wave error
falls by 2^3.17 from 16 to 32 cells, not by 2^6; the package reports a part of second
order in the amplitude that does not fall with resolution after one period (READY of
requests-b, test T8), so this number checks that the generator and its error file work,
not the order of the scheme [JUDGEMENT]. A first attempt of the quick test,
core-20261120-222724-75e323c, is on record as failed: its driver compared
`clump/particles.json`, a record of the particle generator that holds the name of the
run directory; every file AthenaK wrote had the same bytes then as now.

## Card check of `athena_gpu`

PENDING when this file was written (2026-11-21T03:13Z): Slurm job 4758, run
core-20261121-025945-54dc669, queued behind four jobs. It runs the eleven cases of the
quick test (`analysis/release/card_v04.list`, 0.2 card-hours asked) with the candidate
card executable; `analysis/release/card_v04.py` then judges prediction C of the journal
(every case status 0; the thirteen numbers in their bands; iteration and collision
counts equal to the processor runs; differences to the processor runs within stated
bounds). Until this paragraph is replaced by the outcome, `athena_gpu` of the candidate
is built and not run. The card executables of the seven branches were each tested on a
card by their packages; the merged source is their union.

## Known defects

`tracks/core/stage/G2/OPEN.md`, section of 2026-11-21, items a to i; the READY of the
published executables. In short:
- no two new capabilities were run together;
- four corrections change outputs of existing inputs without an option (restart header
  bytes, `last_time` of final outputs, tracers with m = 0 on the mesh metric, the
  oblique linear wave), and collisional card runs differ from core-v0.3 at rounding;
- `<fastflow> hmean_tol_<n>` ends every horizon search at once in a cosmological box
  (use 1e30) [reported by package cosmo-amr, not rechecked];
- the particle restart file grows with `max_nmb_per_rank`, not with the mesh;
- the initial-data solver: uniform meshes, one rank, no punctures, one per cent closure
  error of the vector part at the faces; clumps with momentum: Gaussians only;
- one wrong comment in `particles.hpp` (history columns 32 to 36, not 35);
- the capability tests of the packages and the verification ladder were not rerun on
  the merged executables: the release rests on the byte regression, on one example per
  branch against the branch's own executable, and on the packages' tests of the
  unchanged branch sources.

## For the release clerk

Merge `core/nrpic` into main; tag `core-v0.4` (the source commit of the first line, or
the merge on main: the source trees are the same); build `.work/build_gpu_v04` and
`.work/build_cpu_v04` from that source; copy `tracks/core/interfaces/*.md` to
`coord/INTERFACES/` (new or changed since core-v0.3: `REQUESTS_B.md`, `REQUESTS_ADF.md`,
`cosmo_gauge.md`, `scalar_field_2.md`, `moving_clumps.md`, `id_solver.md`,
`collisions.md`, `rng.md` with the stream registry of decision 0016 item 9,
`diagnostics.md`, `multi_puncture.md`); announce the corrections of the changelog to
all owners. A processor build from the same source in another build directory need not
have the sha256 of `athena_cpu` (it is built with debugging information) [JUDGEMENT,
not tested]: compare outputs with `regress_v04.py`, not checksums.

How to repeat the checks:
```
cd /data/haiyangw/nrpic/wt/core
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 3
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 4 --purpose "..." -- python3 tracks/core/analysis/release/quick_v04.py --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 4
```
