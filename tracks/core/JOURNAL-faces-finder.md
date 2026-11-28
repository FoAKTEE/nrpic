# Journal of the source session faces-finder (branch core/faces-finder, batch 34a)

Owner core. Worktree wt/core-s5. Items of `tracks/core/NEXT_SOURCE.md` (0, 0b, 1) and the
finder in periodic boxes (decision 0047 items 4 and 6; Track A's requests
finder-false-accept-and-stall-p0l6 and finder-slow-convergence-box). Times are local (PST).

## Entry 1, 2026-11-27 15:45: state, plan, what was read

- Worktree clean at the start; `git merge main` fast-forward to f65fafd2; branch renamed
  core/faces-finder. No stranded work of an earlier session in this slot.
- Read: NEXT_SOURCE.md items 0, 0b, 1; decision 0047; Track A's two requests; the source
  `particles/nrpic.cpp` (NrpicDepositSources 780-1238, NrpicFilterPass, NrpicCompensateLimited),
  `parameter_input.cpp` (ModifyFromCmdline), `main.cpp` 255-300, `z4c/fastflow.cpp` (Find,
  InitialGuess, FastFlowLoop, UpdateFlowSpectralComponents, SurfaceIntegrals).
- Regression set-ups (regress_v04.py, 12 set-ups, 75 items) [VERIFIED by reading their
  decks]: none sets `deposit_comp_c > 0` on a refined mesh and none sets
  `deposit_fine_shape`; the refined ones (dep, os, c3) use `nfilter` (the source filter,
  which this session does not touch). So 75 of 75 are expected identical.

### Design decisions taken before any run

Item 0 (linear cloud with fine shape). A lattice cell beside a linear cloud that lies in a
finer block gets the tent integral minus a constant. That share is one half of a scheme:
the other half is the share of the clouds that OWN the lattice cell, laid on the same
lattice. Clouds own a lattice cell in a finer block on the same lattice only when they
are held at the level cap (then `ldep == lcap`); without a cap the owners of the fine cell
deposit on the finer lattice and nothing cancels the dipole. The lead's proposal (a flag
"this cloud was capped") would skip the side share of a cloud whose own cells are all on
leaves of the cap level while its neighbour clouds, capped, own the fine side cell: the
uniform lattice would then lose uniformity there. Rule chosen: a side cell is visited only
if `ldep == lcap` (the cloud's lattice is the lattice of the cap, on which the owners of
every finer cell are held).

Item 0b (compensation at a level face). Read: `NrpicCompensateLimited` is in flux form on
each block, with ghost values from the other level; the flux through a level face is
computed twice, from different data, by the coarse and by the fine block. The two do not
only differ by truncation error: the pass is u - c d2 u in cells of the level, so the
physical flux c dx^2 du/dx differs by a factor four between the levels (the pass undoes a
cloud whose width is the cell of the level). No single flux is consistent with both
sides; conservation needs one. Chosen: the flux the fine block computes, summed over the
four fine faces, replaces the coarse flux in the coarse cell at the face (weight 1/8 per
fine face: dx_f dA_f/(dx_c dA_c)... in units of the update, F_c = (1/8) sum F_f). The fine
cells keep their pass; the coarse cell at the face changes. Read from the fine block's
array directly through the neighbour table (same rank only). On refined meshes the plain
pass (c2 = 0, no limiter), which is in product form (`NrpicFilterPass`), is routed
through the flux form so that it gets the same correction: its cells change at round-off
everywhere on a refined mesh and by O(c x jump) at level faces. Uniform meshes keep the
old code path, byte for byte.

Item 1: `ModifyFromCmdline` adds a missing parameter or block when the run continues from
a restart file, with a line in the log; a fresh start keeps the fatal error. `-i` after
`-r` already adds; it now logs the additions too.

### Prediction F0 (diagnostic, release core-v0.8 processor build, before any source change)

Verbose search on Track A's file S1L t = 220 (peak.00019.rst) from 0.6 and from 0.2, 400
iterations each. What limits the convergence, by reading: one flow step changes the mean
radius by -A rho_00 with A = alpha/(lmax(lmax+1)) + alpha/2 = 0.514 and rho = H u sigma,
u = |grad F| = 1/sqrt(g_rr) for a round sphere, sigma = 2 r^2/sigma_para = r^2 x (areal
radius/r)^2. For a conformally flat metric the step is A H r^2 psi^2, which contracts the
distance to a Schwarzschild horizon by 1 - A = 0.49 per iteration. Track A's status files
give 0.6 -> 0.532 in 400 iterations, a step of 1.7e-4 per iteration, where the
conformally flat estimate with their area (2.04e4) and expansion integral (505) gives
0.27 per iteration. So I expect: (a) the mean radius falls monotonically and smoothly,
relative step below 1e-3 per iteration throughout (a creeping flow, not an oscillation
or a jump); (b) the step follows the expansion integral, i.e. step/(H_mean) is roughly
constant along the flow from 0.6. Refuted if the radius jumps by more than 10 per cent in
the first iterations or oscillates (then the limit is not the size of the step but the
stability of the higher modes). If (a) holds, the cause is the weight u = 1/sqrt(g_rr):
the radial metric component is much larger than the tangential one on these slices
(zero shift, collapsed lapse: the slice is stretched radially), to be checked from a
metric dump or from the step itself.

## Entry 2, 2026-11-27 15:40: outcome F0, and what limits the convergence

Run core-20261127-233027-4fdb05d (release core-v0.8, `athena_cpu_omp`, 3 threads, 70 s).
F0 (a) HOLDS: from 0.6, 0.2 and 0.1 the mean radius moves monotonically by 1.72e-4,
3.4e-5 and 4.3e-5 per iteration (relative 2.9e-4, 1.7e-4, 4.3e-4), no jump, no
oscillation; the mass changes by 4.2e-3, 8.5e-4, 1.2e-3 per iteration, so the mass rule
(1e-5) is never met and the searches end at the cap (reason 6). (b) HOLDS in part: the
step over the expansion integral is 2.9e-7 at 0.6, 6.6e-7 at 0.2 and at 0.1.

My reading of the flow function in entry 1 was WRONG (failed premise, kept on record): I
took rho = H u sigma (the weight with r^2 of Gundlach's flow, `flow = shear`). The input
key `<fastflow> flow` is `standard` when absent (fastflow.cpp 67-72), and then rho = H u,
u = |grad F| (fastflow.cpp 1430-1431), without the weight. For a round sphere in a
conformally flat metric u = 1/psi^2 = r/R (R the areal radius), so one iteration moves
the mean radius by

    delta r = - A H / psi^2,   A = alpha/(lmax (lmax+1)) + alpha/2 = 0.5139 (alpha 1, lmax 8).

Check against the run [VERIFIED]: at r = 0.6 the area is 2.39446e4 and the expansion
integral 583.839, so H = 0.024383, psi^2 = R/r = 72.75, delta r = 1.722e-4; the verbose
file gives 0.6 -> 0.59982809, 1.719e-4 (0.2 per cent). At r = 0.2: 3.31e-5 predicted,
3.39e-5 found. So the metric is isotropic there (the guess of a radially stretched slice
in entry 1 is refuted) and the step is simply small.

What limits the convergence [VERIFIED for the size of the step; the rate at the horizon
is JUDGEMENT from the Schwarzschild case]: the step H u has the dimension 1/length, so
the flow is not invariant under a change of the unit of length. Near a Schwarzschild
horizon of mass m in isotropic coordinates (r = m/2, psi = 2, dH/dr = 1/m^2) an
iteration reduces the distance to the horizon by the factor 1 - A/(4 m^2): 0.87 for m = 1
(a puncture in units of its mass: 129 iterations to 1e-9, finder_stop.md), 0.9987 for
m = 10. Track A's box has holes of area mass 6.3 (P0L6) and 10.7 (S1L) in code units, and
the comoving coordinates add psi^2 = 73 to 180 between coordinate and areal radius: an
e-folding of the distance takes several hundred iterations, which is what the track
measured (915 to 3444 iterations; not converged in 4000 from 0.2). The weighted flow
(`flow = shear`, rho = H u sigma with sigma = 2 r^2/(...) = r^2 psi^4 for a round sphere)
has the step A H r R, which is invariant, and contracts by 1 - A = 0.49 per iteration at
a Schwarzschild horizon of any mass.

### Prediction F1 (the cause, in runs where it can fail; release core-v0.8, no new source)

`fastflow/flow=shear` on the command line of the continued run (the key is in the stored
input of every run). Searches with mass_tol 1e-5, polishing 100, cap 400:
- S1L t = 220 (peak.00019.rst): from the deck's 0.6, from 0.2, 0.1 and 0.03: FOUND within
  400 iterations, area mass 10.73 +- 0.05, mean radius 0.161 +- 0.003 (Track A's surface
  from 0.16 after 1927 iterations of the standard flow: 10.73, 0.161), the four masses
  within 1e-3 of each other.
- P0L6 t = 140 (peak.00017.rst): from the deck's 0.15: FOUND, area mass 6.30 +- 0.02, mean
  radius 0.104 +- 0.002 (Track A: 6.298 to 6.309, 0.1037 to 0.1042).
- P0L6 t = 130 (peak.00016.rst, no trapped round sphere by Track A's scan): NOT found
  from 0.15 and 0.6, whatever the reason; a found surface there is a false acceptance.
Refuted if a search from the deck's radius ends at the cap still moving (then the step is
not the limit), or dies by overshooting (mean radius negative, reason 4, in the first
iterations: in flat space the weighted step with alpha = 1 is r -> r (1 - 2A) = -0.03 r);
members with `flow_alpha_beta_const = 0.5` (A = 0.257, flat-space step r -> 0.49 r) run
beside them to tell these two apart.

## Entry 3, 2026-11-27 15:50: outcome F1 (the weighted flow), predictions for the source

### Outcome F1 [VERIFIED; release core-v0.8, `fastflow/flow=shear` on the command line]

- S1L t = 220, run core-20261127-233526-05eba1f: FOUND from 0.6 (the deck's start), 0.2,
  0.1, 0.03 and 1.5 after 125 to 139 iterations, of which 100 are the polishing; area
  mass 10.73958041, mean radius 0.16195874, smallest radius 0.15647, the five masses
  equal to 1e-13; expansion integral -1.9e-5 (Track A's surface from 0.16 after 1927
  iterations of the standard flow: -0.63), area mean of H^2 2.12e-8, so rms expansion
  times mass 1.6e-3. From 0.6 the radius goes 0.600, 0.272, 0.206, 0.185, 0.175, ...: a
  contraction of about 0.6 per iteration near the surface. With alpha = 0.5: found after
  156 and 157 iterations, same surface to 1e-12. Tight rule 1e-9 without polishing: 47
  iterations. Prediction HELD (10.73 +- 0.05, 0.161 +- 0.003, within 400).
- P0L6 t = 140, run core-20261127-233531-d12e417: FOUND from 0.15 (the deck's start), 0.6
  and 0.05 after 138 to 144 iterations, area mass 6.30324213, mean radius 0.10398630;
  alpha 0.5: 174 and 182; tight rule: 72. Prediction HELD (6.30 +- 0.02, 0.104 +- 0.002).
- No overshoot to a negative radius in any member. P0L6 t = 130 (no trapped sphere) is
  run with the new build below (prediction S3).
So the cap of iterations was hit because of the flow function, and the cure needs no new
source: `<fastflow> flow = shear` in the deck, or `fastflow/flow=shear` on the command
line of a continued run (the key is global, for all horizons of the run).

### Predictions for the tests of the new source (processor build of this branch)

D (item 0, `dep_levels.py`, all sixteen cases): `cic_fs` byte-identical to `cic` (check
D4 holds, which fails on core-v0.8: dipole of -+0.125 at x1 = 7.25, 7.75); every table of
the other fourteen cases without compensation byte-identical to the same case run with
core-v0.8. Refuted by any differing byte there.

C0 (item 0b on the planar test, case `pcs_comp` of `dep_levels.py`): line sum 32 to 1e-12
(core-v0.8: 32.0413); the excess of 0.0413 leaves through the two coarse cells at the
faces only: E at x1 = +-8.5 lower than core-v0.8 by 0.0207 each (to 1e-3), every other
cell on the line byte-identical to core-v0.8 (the fine cells keep their pass; the
problem is planar, so only the pass along x1 meets a face). D5 (gain over the
uncompensated boundary error between 1 and 2.2) probably still holds; not sure.

C1 (item 0b in three dimensions, `comp_cons.py`: random particles moving across a cube in
a cube, faces, edges and corners, 20 steps): with the new build the integral of E and of
S_i over the mesh equals the particle sums to 1e-12 (relative to sum m W) at every cycle
for `pcs_c2` (Track A's settings), `pcs_c2_lim` (with the limiter), `tsc_plain` and
`cic_plain` (no fourth-order term: product form in core-v0.8, flux form now); with
core-v0.8 the error is above 1e-7 in all four. Histories byte-identical between the two
builds for `none_pcs` (no compensation) and for the two uniform-mesh cases `uni_pcs_c2`,
`uni_cic_plain`. Refuted for the design if an error above 1e-12 remains in the new build
(then faces between blocks of the same level next to a level edge do not see the same
ghost data, which I could not exclude by reading).

R (item 1, `diag_restart.py`, changed expectation): a `-r rst fastflow/diagnostics=true`
starts, writes the status file with the same lines as b (`-i add.athinput`), and the log
holds "Parameter added on restart from the command line: <fastflow> diagnostics = true";
b: log line "... from the input file ..."; c (control) no status file and no such line;
d: a fresh start with `fastflow/no_such_option=1` still ends with the fatal error; e:
`-r rst fast-flow/x=1` is refused.

S (finder options, Track A's files, one cycle each; S1L t = 220 and P0L6 t = 140, 130):
- S1 `trapped_tol`: the finder's default tolerance `mass_tol = 1e-2` with the standard
  flow from 0.6 on S1L accepts the second surface it evaluates (the mass changes by
  4.2e-3 per iteration, run core-20261127-233027-4fdb05d): found = 1 at mean radius
  0.5998, mass 21.8, a FALSE acceptance (control member). The same search with
  `trapped_tol = 0.05`: not found, reason 7, 400 iterations, column 16 near 0.5
  (H m = 0.0244 x 21.8). With `flow = shear` and `trapped_tol = 0.05`: found, the surface
  of F1 (10.73958, column 16 = 1.6e-3).
- S2 `start_scan = 24` on S1L t = 220 (radii 0.01875 to 0.6): the outermost sphere with a
  negative integral lies at 0.15 to 0.165, the start radius within 3 per cent of 0.162;
  with the standard flow and 4000 iterations: found, mass 10.74 +- 0.01; with 400: not
  found (reason 6 or 7), because near the surface the standard flow still needs of order
  a thousand iterations. With `flow = shear`: found within 130 iterations, the surface
  of F1. P0L6 t = 140 (scan 0.0047 to 0.15): start within 3 per cent of 0.104; shear:
  found, 6.30324.
- S3 P0L6 t = 130 (no trapped round sphere, Track A's scan): with `start_scan`: reason 8,
  no flow iteration, with either flow. Without the scan, `flow = shear` from 0.15 and
  0.6: not found (the flow shrinks to a point or stops by a failure check); if it is
  "found" with `trapped_tol = 0.05`, the surface is marginally trapped to that
  tolerance and Track A's scan missed it: to be looked at, not a false acceptance by
  the rule.
- S4 without the new options the finder's files are byte-identical to core-v0.8 on
  `problems/tests/by_horizon_coarse.athinput` (status file with diagnostics, summary,
  shape) and on S1L (the status lines of F0's three members).

## Entry 4, 2026-11-27 15:55: first outcomes D, C0, C1; the pass needed one exchange per direction

Run core-20261127-234417-485a3df (dep_compare.py; closed as failed because two checks of the
script failed, one of them mis-specified by me):
- D: every table of the fourteen cases without `cic_fs` and `pcs_comp` byte-identical
  between core-v0.8 and this branch (HOLDS). `cic_fs`: the cells that change against
  core-v0.8 are x1 = 7.25 (+0.125) and 7.75 (-0.125), the dipole of NEXT_SOURCE item 0
  and no other cell. My check "D4 of dep_levels.py passes" was the wrong check: D4 also
  asks the capped deposits to be uniform to 1e-13, which core-v0.8 does not give either
  (0.125 for `cic_cap`, 0.031 for `tsc_cap`: the test lattice has one particle per LOCAL
  cell, and clouds of the root width over a lattice whose spacing jumps are not uniform
  at the jump; lead's run core-20261126-022953-21b8455 shows the same numbers). The
  script now compares the tables of `cic_fs` and `cic` directly; rerun below.
- C0: line sum of `pcs_comp` 31.999999999999996 (core-v0.8: 32.04131944) HOLDS; only the
  two coarse cells at the faces change HOLDS; the split FAILED: -0.00755 at x1 = -8.5 and
  -0.03377 at +8.5, not -0.0207 each (their sum, -0.04132, is the excess). The two faces
  are not mirror images in this test: the particles sit exactly on cell centres, where
  the four cells of the cubic cloud are chosen to one side, so the deposit level of the
  clouds next to the two faces differs. Gain over the uncompensated boundary error: 1.63
  (core-v0.8: 1.79), so D5 holds.

Run core-20261127-234454-3c39b48 (comp_cons.py, first form: outflow faces, stopped by me
after three cases): C1 FAILED for the first form of the source. `pcs_c2`: largest error
of the E integral 9.9e-4 with core-v0.8 and 3.4e-5 with the branch; `pcs_c2_lim`: 3.6e-4
and 8.2e-6. Thirty to forty times smaller, not round-off. Two causes by reading, not yet
separated by a run:
 (a) my own: the pass along x1 acts in the ghost rows of a block too, so that the passes
     along x2 and x3 find their neighbours; but the coarse cells at a level face are
     corrected after the pass, in the block that owns them only. A neighbour of the same
     level then holds, in its ghost cells, the uncorrected value, and the two blocks
     disagree on the flux through their common face in the next direction;
 (b) the deck has outflow faces: the pass has a flux through a face of the mesh when
     matter lies in the cells next to it.
Changes: on a mesh with refinement the ghost cells are now filled again before the
passes along x2 and x3 (one exchange per direction instead of one; a uniform mesh keeps
the single exchange and stays byte-identical), and the test runs in a periodic box (the
outflow deck stays as case `out_pcs_c2`, expected NOT to conserve if matter reaches the
faces of the mesh, with either build). Prediction C1 stands as written for the periodic
cases, now for ten steps; if an error above 1e-12 remains, (a) was not the only cause.

## Entry 5, 2026-11-27 16:06: outcomes C1 (second form), R, S1 to S3; prediction K (card)

C1 (second form: one ghost exchange per direction; periodic box; ten steps), run
core-20261127-234843-fa6c2e9, PASS. Largest error of the integral of E against the sum of
m W, core-v0.8 and this branch: `pcs_c2` 9.94e-4 and 2.7e-14; `pcs_c2_lim` 3.65e-4 and
2.1e-14; `tsc_plain` 6.45e-4 and 3.3e-14; `cic_plain` 2.43e-4 and 2.1e-14; momenta
5.9e-5 to 1.5e-4 and below 1e-15. `out_pcs_c2` (outflow faces) gives the same numbers as
the periodic case, so matter does not reach the faces of the mesh in this deck and cause
(b) of entry 4 played no part: the residual of the first form was removed by the
exchange per direction (stale ghost copies of corrected cells, and prolongated ghost
values, are not separated from each other by a run). Histories byte-identical between
the builds for `none_pcs`, `uni_pcs_c2`, `uni_cic_plain`. Largest energy density: changed
by 5.0e-3 relative (`pcs_c2`), 1.0e-5 (`cic_plain`), 3e-16 (`tsc_plain`), 0 with the
limiter. `cic_fs` in three dimensions: smallest energy density -1.46e-3 with core-v0.8,
0 now. Figure fig_comp_cons.png looked at: left panel 2e-5 to 1e-3 for the four
compensated cases, right panel all below 1e-13.

D rerun (corrected check), run core-20261127-234848-7d666df: `cic_fs` byte-identical to
`cic` with this branch and not with core-v0.8 HOLDS; others as in entry 4. Figure
fig_dep_compare.png looked at: (a) the dipole of core-v0.8 at 7.25, 7.75 is gone; (b)
only the point at 8.5 moves (0.373 to 0.339).

R, run core-20261127-234458-4baaaa4: F1a to F1e HOLD. Log lines: "Parameter added on
restart from the command line: <fastflow> diagnostics = true" (a) and "... from the
input file ..." (b); status lines of a and b equal; c none; d and e exit 1.

S1 HOLDS (runs core-20261127-235152-d46d2d2, core-20261127-235215-27c6606): the default
`mass_tol 1e-2` with the standard flow from 0.6 on S1L is "found" at iteration 2 (radius
0.5998, mass 21.82); with `trapped_tol 0.05` it is not found, reason 7, column 16 =
0.4999 (predicted about 0.5). Weighted flow with the check: the surface of F1, column 16
= 1.565e-3 (predicted 1.6e-3).

S2 HOLDS in part: the scan (24 spheres, 0.01875 to 0.6) finds 12 trapped spheres, 0.0295
to 0.1546, and starts at 0.16151, 0.3 per cent inside the horizon radius 0.16196 (within
3 per cent: held). Weighted flow with the scan: found after 114 iterations (14 without
polishing), the surface of F1 (held). Standard flow with the scan: FOUND after 241
iterations with cap 400 and cap 4000 alike, mass 10.7274: my prediction "not found within
400" FAILED (the start is closer than I assumed), and the mass lies 0.0122 below the
converged 10.7396, outside the +-0.01 I gave for the long search. The surface is not
converged in shape: smallest radius 0.1596 against 0.1565, column 16 = 0.042, 27 times
the converged value; `trapped_tol 0.05` lets it pass, 0.01 would refuse it. So the mass
rule with polishing does not make a converged surface with the standard flow here, and
the tolerance to recommend is 0.01, not 0.05. P0L6 t = 140 with the weighted flow and the
scan: found after 113, mass 6.30324213 (held).

S3 HOLDS (runs core-20261127-235631-a5e5818, core-20261127-235652-ac88116; P0L6 t = 130):
with the scan reason 8 and no iteration, both flows. Without it: weighted flow not found
by "mean radius negative" after 16 and 18 iterations; standard flow at its cap (reason
6), having crept from 0.15 to 0.107 and from 0.6 to 0.452. An unplanned member confirms
the false-acceptance class where nothing is trapped: standard flow, `mass_tol 1e-2`,
from 0.6: "found" at iteration 2 (radius 0.5996, mass 15.33); with `trapped_tol 0.05`
not found, reason 7.

### Prediction K (one card job, `card.list`, executable of the published directory)

K1 the three planar deposit cases equal the processor run in every cell of the line to
1e-12; `cic_fs` equals `cic` to 1e-13; line sum of `pcs_comp` 32 to 1e-10. K2 the three
compensated cases on the refined mesh conserve to 1e-12 at every record on the card too
(the correction reads the fine block's array inside a kernel: if the neighbour table on
the device were not what I read on the host, this fails). K3 the S1L probe with the
weighted flow: every member found, masses within 1e-6 relative of the processor run,
column 16 within 1e-4, scan start within 1e-6. K4 a continued run takes
`fastflow/diagnostics=true` on the command line: status file and log line. Refuted by
any of these failing; a card-only failure of K2 would mean the level-face kernel is
wrong on the device.

## Entry 6, 2026-11-27 16:15: last outcomes, regression, publication, what is pending

S (P0L6 t = 140, standard flow with the scan), run core-20261128-000217-460058c: the scan
(0.0047 to 0.15) finds 10 trapped spheres and starts at 0.103970 (horizon 0.103986);
found after 102 iterations, mass 6.30262 (1e-4 below the converged 6.30324), column 16 =
6.8e-3; the control without the scan ends at its cap at radius 0.1295 (reason 6). P0L6 is
close to spherical, so the round start sphere is almost the horizon; on the triaxial S1L
the same recipe leaves a shape error (column 16 = 0.042, entry 5).

Table and figure of all finder members: run core-20261128-000846-a3722c7
(`finder_table.json`, `fig_finder.png`; the first form of the figure, run
core-20261128-000822-500bc84, had one scan curve per run instead of per file). Figure
looked at: (a) from 0.6 the standard flow reaches 0.53 in 400 iterations, the weighted
flow the surface at 0.162 in about ten, and the three starts of the weighted flow meet;
(b) the mean expansion times mass of the round spheres crosses zero where the dashed
start radii are for S1L and P0L6 t = 140 and stays above 0.08 at t = 130; (c) column 16
is 1.6e-3 to 3e-3 for the surfaces of the weighted flow, 7e-3 and 0.042 for the standard
flow after a scan, 0.1 to 1 for every member that was refused. The title of panel (c) is
cut at the right edge (cosmetic, left as it is).

S4 HOLDS, run core-20261128-000807-e413b5e: without the new options every output file of
`by_horizon_coarse` (6 files) and of `finder_polish` (8 files, 8 cycles, with polishing
and the status file) equals release core-v0.8 byte for byte. The first run of that
script, core-20261128-000242-6d6117a, is on record as failed: both builds stopped on the
polishing deck's missing particle file (my script, not the code); the six files of the
first deck were already identical there. With `trapped_tol_0 = 0.2` on the coarse
puncture deck: found, 18 columns, column 16 = 0.0155; `start_scan` is not applied to a
horizon tied to a puncture (column 18 = -1), as documented.

Byte regression against release core-v0.8, run core-20261128-000404-015d78b: REGRESSION
PASS, 75 of 75 items identical (geo 2, boris 2, dep 1, east 12, os 16, jeans 5, binary 1,
c1 5, c2 3, c3 14, c4 4, c5 10), as predicted in entry 1 (no set-up of the regression
sets `deposit_comp_c` or `deposit_fine_shape` on a refined mesh).

Published: `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/` (athena_gpu,
athena_cpu, COMMIT = ad54460e, SHA256SUMS, READY). Card build: 1119 s with three jobs,
no error; NOT run on a card yet.

Pending at the end of the session: the card check, shared-queue entry **q0086** (label
core-ff-card, priority 2, `tracks/core/analysis/faces_finder/card.list`, 0.2 card-hours
asked). Five jobs of other owners were in the Slurm queue when it was added. To judge it:

    harness/bin/nrpic-run finish <run id of q0086>
    python3 tracks/core/analysis/faces_finder/card_check.py --card <its output dir> \
      --dep scratch/core/core-20261127-234848-7d666df --cons scratch/core/core-20261127-234843-fa6c2e9 \
      --s1l scratch/core/core-20261127-235215-27c6606 --out <new run dir>

(registered with nrpic-run), against prediction K of entry 5; then the READY's "STATE OF
THE TESTS" block gets the outcome.

What is not done, plainly: no card run; no timing; several ranks untested and level faces
across ranks not corrected; Track A's set-up not run by core; the false acceptance at
t = 118.12 not retested (no restart file); the weighted flow not tested on punctures; the
added command-line parameters not tested inside a chain.

Lines of shared files touched (for the merge): `particles/nrpic.cpp`: one statement
before the fine-shape branch of `NrpicDepositSources`, the condition that chooses the
compensation pass, and in `NrpicCompensateLimited` the exchange (now a local lambda), the
ranges of the three passes and one call; `particles/particles.hpp`: one declaration;
`CMakeLists.txt`: one line; new file `particles/nrpic_levelface.cpp`;
`parameter_input.{hpp,cpp}`: `ModifyFromCmdline` (one more argument), `AddParameter` (two
log lines), one public flag; `main.cpp`: three lines where the input is loaded;
`z4c/fastflow.{hpp,cpp}`: reading of four options at the end of the constructor, the
status block of `Write`, five lines in `Find`, the acceptance in `FastFlowLoop`, new
`StartScan` before `MetricDerivatives`.

### Prediction R2 (a block the stored input does not hold)

`athena -r hc.00001.rst zz_block/x=1 time/nlim=1` (the restart file of run
core-20261127-234458-4baaaa4, at cycle 1, so no cycle is taken): exit 0, the log line
"Parameter added on restart from the command line: <zz_block> x = 1", and no fatal error
from a check of block names (which runs only for input files). Refuted by a non-zero
exit or a missing line.

Outcome R2, run core-20261128-001433-ddd0f14: HOLDS (exit 0, the log line for `<zz_block>
x = 1`, "Terminating on cycle limit"). Also checked by reading the files of run
core-20261127-234458-4baaaa4: the three restart files that case a wrote hold the line
`diagnostics = true # added from the command line on restart` in their stored input.

Cost on processors (serial build, the ten steps of `comp_cons.py`, the two builds side by
side, so indicative only; run core-20261127-234843-fa6c2e9): cubic cloud with c2, 11.9 s
with core-v0.8 and 12.1 s now; no compensation 2.6 s in both; linear cloud with the plain
pass 5.3 s and 10.7 s: the plain pass in flux form with three exchanges costs about three
times the product pass. These runs evolve no metric, so the deposit is all of their
time; in a run with the spacetime solver the share is smaller. Not timed on a card.

### Prediction T (threaded build of this branch, three threads)

`scripts/build_cpu_omp.sh`, then `comp_cons.py` with the threaded build as "new" and
OMP_NUM_THREADS = 3: the four compensated cases conserve to 1e-12 as with the serial
build (the level-face kernel writes one coarse cell per index, so threads cannot
collide); histories of the untouched cases need not be byte-identical to the serial
release (the threaded build is not a byte reference), so check C1c may fail there and is
not judged. Refuted by a conservation error above 1e-12.

Outcome T (threaded build, three threads) HOLDS. S1L probe with the weighted flow, run
core-20261128-001900-aefdc7b (81 s): the six members give the masses and iteration counts
of the serial build (10.73958040610839 after 127; with the scan 114; without polishing
14), differences at 1e-14. Conservation, run core-20261128-002140-cf20022: largest error
1.1e-14 (`pcs_c2`), 7.1e-15 with the limiter, 8.9e-15 and 7.9e-15 for the plain pass with
the quadratic and the linear cloud. The run is closed as failed because the script's
check of byte-identical histories against the serial release (C1c) fails for a threaded
build, as written in the prediction; it is not judged. `athena_cpu_omp` was added to the
published directory at 00:24Z (a new file; nothing replaced), with its checksum.

A 92-character line of `nrpic_levelface.cpp` (the style allows 90; the file `nrpic.cpp`
holds longer ones from before) was left as built, so that the source equals the commit
the executables were built from.

Not tested and worth a line: a level cap between the coarsest and the finest level with
the linear cloud and `deposit_fine_shape` (clouds on a lattice coarser than the cap next
to a finer block that is not above the cap). That is the one case where the rule chosen
in entry 1 differs from the lead's proposed flag in what it deposits; `dep_levels.py`
has caps at the root level only.

### Prediction CM (the case where my rule for item 0 differs from the lead's proposed flag)

`cap_mid.py`: three levels along x1 (level 1 in |x1| < 8, level 2 in |x1| < 4), cap at
level 1, linear cloud, one lattice of particles everywhere at the centres of the level-1
cells. With `deposit_fine_shape`:
- this branch: E/rho0 = 1 to 1e-12 in every cell of the line, at the faces 0/1 and 1/2
  alike. At the face 1/2 the clouds of level-1 blocks whose own cells are all level-1
  leaves (not "capped" in the sense of the proposed flag) must leave their share in the
  level-2 cells beside them, because the clouds of the level-2 block are held on the
  same lattice; a flag "this cloud was capped" would drop that share.
- core-v0.8: the same at the face 1/2, and a dipole in the level-1 cells next to the face
  0/1 (clouds on the root lattice beside a block whose clouds are on the finer lattice).
Without the option: uniform, and the same bytes on the line in both builds.
Refuted for my rule if this branch is not uniform at the face 1/2 (then the share I keep
is wrong) or at 0/1 (then the share I drop was needed).
