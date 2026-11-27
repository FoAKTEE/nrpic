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
