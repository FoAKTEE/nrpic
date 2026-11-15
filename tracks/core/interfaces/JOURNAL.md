# Journal of the interface package (core helper "doc")

Predictions are written before the run that tests them; outcomes are appended below
them, also when a prediction fails. Times are UTC.

## 2026-11-15 11:21 Reading done; what the processor executable contains

Read: the paper source (`refs/arxiv_2611.12831/src/main.tex`, all 1515 lines), the
particle module (`athenak/src/particles/*.{cpp,hpp}`), the three NRPIC problem
generators, the Z4c options and right-hand side added for NRPIC and cosmology
(`athenak/src/z4c/z4c.cpp` lines 125-166, `z4c.hpp` lines 142-199, `z4c_calcrhs.cpp`
lines 40-69, 155-165, 481-491, 607-729), `docs/FORMATS.md`, `cosmo/README.md`, the two
test logs (by entry), `notes/method_brief.md`, `notes/claims_brief.md`,
`paper/sections/method.tex`, `cosmo/ic/cosmo_id.py` (solver part).

Finding before any run. The processor executable named in `CLAUDE.md`
(`/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena`, file time 2026-11-14 06:03:37
PST) is older than three source changes on `main`: commit 631cfe3 (08:04 PST,
`damp_ch_chipow`), 010aace (08:23 PST, columns 17-19 of `.cstat.hst`) and 0c06525
(08:35 PST, `damp_kappa_gam`). Check: `grep -c -a` of the option strings in the two
executables: `damp_kappa_gam`, `damp_ch_chipow`, `Z_max`, `Theta_mean` occur 0 times in
the processor executable and once in the card executable
(`.work/build_gpu_c3/src/athena`, 08:31:30 PST); `cons_dcycle`, `dt_expansion`,
`deposit_comp_c2`, `interp must be hermite`, `NRPRST05`, `NRFIELD2`, `metric_drvts`,
`ah_exc_factor` occur in both. Consequence: with the processor executable an input
that sets `damp_ch_chipow` or `damp_kappa_gam` runs with the default behaviour
(exponent -1/4, no extra damping) and gives no error, because unknown parameters of
an input block are not checked. Recorded as a request (README, "Requests").

## 2026-11-15 11:25 Test D1, written before the run: the output formats of the module

Purpose: the interface documents `diagnostics.md` and `particle_id.md` describe every
file from the source. This run checks those descriptions against what the processor
executable writes, with a reader (`check/read_outputs.py`) written from the documents
and not from the source.

Set-up (scouting, processors, 4 threads): homogeneous dust universe of
`problems/cosmo/flrw.athinput` on a 16^3 periodic mesh of side 4 in eight 8^3
MeshBlocks, nghost 4, Courant number 0.25 (step 0.0625), to t = 0.5 (8 steps); a
lattice of 16^3 = 4096 particles (`cosmo/ic/make_lattice.py --n 16 --ppc 1 --L 4`,
position noise 0.01, momentum noise 1e-4, seed 1); every diagnostic of the module on:
history every cycle with two additional probes, constraint statistics, conservation
records, line records, field dumps at t = 0 and 0.25 with constraints, trajectories of
10 particles, snapshots and curvature (with the slice y = 1.0) every 0.25, mesh
restart files every 0.25. Then a restart from the dump at t = 0.25 to t = 0.5 in a
second directory.

Predictions (sizes from the documents; N = 4096, n = 16 cells per side, 8 cycles):
1. `.nrpic.hst`: header lists 32 + 3 x 2 = 38 columns; 9 records (t = 0 and every
   cycle), 38 fields each; column 4 (sum m) equals the sum of the masses of the
   particle file to 1e-14 relative and is constant; column 9 (int E) equals column 5
   (sum m W) to 1e-13 relative in every record; column 24 equals column 9 exactly
   (no filter pass).
2. `.cstat.hst`: 16 columns from this executable (the source has 19; see the entry
   above); 9 records.
3. `.cons.hst`: 7 columns; 7 records, the first at t = 0.0625 (two steps after the
   start, time of the middle step), the last at t = 0.4375.
4. `.line.txt`: n = 16 and 16 cell centres 0.125 ... 3.875; `.line.bin`: 9 records of
   1 + 5 x 16 doubles (5832 bytes).
5. `.field.00000.bin` and `.field.00001.bin`: magic `NRFIELD2`, dims (16, 16, 16),
   262184 bytes each.
6. `.traj.bin`: 9 x 10 records of 8 doubles (5760 bytes); `.trajmet.bin`: 9 x 10
   records of 17 doubles (12240 bytes); time and tag columns of the two identical.
7. `.part.0000{0,1,2}.bin`: magic `NRPSNAP1`, N = 4096, 294944 bytes each; masses equal
   to those of the particle file.
8. `.curv.hst`: 3 records of 10 columns; `.curv.0000{0,1,2}.bin`: magic `NRPCURV1`, 256
   records (16 x 16 cells cut by y = 1.0), 14360 bytes.
9. Particle restart file next to each mesh restart file: magic `NRPRST05`, N = 4096,
   source-density block present (dims 8, 10, 16, 16, 16), 2933160 bytes.
10. Restarted run: its history records after t = 0.25 equal those of the uninterrupted
    run to all printed digits (as in `cosmo/TESTLOG.md`, "Restart of periodic runs").
11. Physics, for the figure only: the probe lapse follows a(t) = (1 + t/2)^2 within
    1e-3 relative at t = 0.5 (the noise of the lattice is small).

What would refute the documents: any file whose size, magic, column count or record
count differs from the above, without a source change after 06:03 PST that explains it.

## 2026-11-15 11:24 Test D1, outcome (run core-20261115-112600-b7b431d)

Summary: `figs/d1_summary.json`; figures `figs/d1_history.png`, `figs/d1_slices.png`
(both looked at). 24 of 25 checks pass.
1. History: 38 columns, 9 records, column 24 equal to column 9 exactly, column 9 equal
   to column 5 within 3.6e-15 (prediction 1e-13: holds). Column 4 (sum m) is constant
   over the run but differs from the exact sum of the masses (math.fsum) by 6.7e-14
   relative, where I predicted 1e-14: FAILS as written. It equals the sequential sum
   of the masses in file order to all printed digits (7.639437268411487); the
   tolerance I wrote ignored the N eps round-off of a sequential sum (N = 4096). The
   description in `diagnostics.md` says "floating-point sum in the code's order".
2. `.cstat.hst`: 16 columns from this executable, as predicted (the source has 19).
3. `.cons.hst`: 7 columns, 7 records from t = 0.0625 to 0.4375: holds. After the
   restart at t = 0.25 the records resume at t = 0.375 (two steps later) and are equal
   to those of run 1.
4. Line records: holds (n = 16, centres 0.125 ... 3.875, 9 x 81 doubles).
5. Field dumps: `NRFIELD2`, (16, 16, 16), times 0 and 0.25, sizes as predicted.
6. Trajectories: 90 x 8 and 90 x 17, same time and tag columns: holds.
7. Snapshots: holds. Not predicted: the int64 "cycle" of a snapshot is the cycle
   counter before the step that produced the state (3 at t = 0.25, where the history
   says 4). Written into `diagnostics.md`.
8. Curvature: 3 records of 10 columns; slices `NRPCURV1` with 256 records. Not
   predicted: the header of `.curv.hst` contains the names "max E" and "file number"
   with a space, so a parser that splits the header on blanks gets 'max' and 'file'.
   Mean of I on the slice at t = 0.25 is about 3.6, the value 15 H^4 = 3.65 of a
   matter-dominated universe at a = 1.2656 [BACKGROUND formula].
9. Particle restart files `NRPRST05` with the source-density block, 2933160 bytes,
   also at t = 0 (a dump is written at the start).
10. Restart: the four history records, the constraint statistics, the snapshot at
    t = 0.5, the curvature slice and the trajectory records of the restarted run are
    identical to those of run 1 (bitwise for the binary files): holds.
11. Probe lapse over a(t) - 1 = -8.0e-4 at t = 0.5 (prediction within 1e-3: holds).
    The relative momentum constraint is of order one throughout: the data of `id = flrw`
    are not solved for the position and momentum noise of the lattice; this is
    expected and is not a check of the code.
The run used one core for 3.4 s and 1.5 s (the processor executable is not threaded).
