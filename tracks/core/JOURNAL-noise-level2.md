# Journal of package noise-level2 (core, branch core/noise-level2)

Task: `<scalar_field> noise_level = 2` of arXiv:2512.14649 (P1), decision 0029 item 2.
Design: `tracks/core/interfaces/noise_level2.md`. Written on Opus; review of the diff on
Fable before any release.

## Entry 0 (2026-11-22 18:40 PST): state, reading, design

Worktree `wt/core-s2` merged with main (8a4a98df), branch renamed `core/noise-level2`.
Read: Track E's request draft (`track/E-stoch-inf:tracks/E-stoch-inf/repro/scope/
outbox_draft/core_noise_level2.md`), P1:220-323, 474-500, 697-713, 776-791, Track E
`EQUATIONS.md` section (e), `scalar_field_noise.cpp`, `scalar_field.cpp`,
`scalar_field_rhs.cpp`, `scalar_field_slice.cpp`, `scalar_field_io.cpp`,
`particles/nrpic_guard.cpp`, `coord/INTERFACES/scalar_field.md` section 7.

Design decisions (details and labels in the design note):
1. R and Pi_R = Z n.d R (Z = 9 Pi^2/K^2) as components 2 and 3 of the field's arrays, so
   the driver's stages, ghost exchange and restart carry them; own right-hand-side kernel.
2. Coefficients: local at level 2; with the new `noise_mode_eq = mesh` also levels 0 and 1
   on the mesh (uniform coefficients of the level). Reason found while designing: our
   level 0/1 per-shell mode functions use the continuum k^2 and P1's levels all use the
   real-space field; a level-2 run compared with our per-shell level 0 differs at FIRST
   order in the noise by the stencil symbol, which would swamp the 1e-4 effect of P1 Fig. 9.
   The ablation must compare mesh runs.
3. Window and kick coefficients at level 2 from the box means (option: Friedmann).
4. Projection: adjoint of the synthesis, three one-dimensional sums, deterministic.

Stencil symbol (computed before any run, `.venv/bin/python`, d2_symbol of nghost = 4):
at 32^3 with nmax2 = 64 the symbol/k^2 is 1.00000 for |n|^2 = 1, 0.99962 for 16, 32, 48,
and 0.98169 for the cut shell |n|^2 = 64 (only the six axis modes (+-8,0,0)...): a deficit
of 1.83 per cent in k^2 at the cut, not the 2.7 per cent of the task text (2.7 per cent
is what the fourth-order symbol gives in k, sqrt(0.9457) = 0.9725; to be checked against
Track E's source of the number).

## Entry 1 (2026-11-22 18:45 PST): predictions, before any build or run

T1 homogeneous slice: the slow-roll input at 32^3, nmax2 = 64, with `<problem> id = flrw`
(phi0, pi0 of the input; no perturbation in the slice), so that every cell is the same:
- T1a: at t* the projected coefficients divided by L^-3/2 alpha_n equal the mode file's
  R_q and dR_q/dtau: max relative deviation < 1e-12. Refuted if larger.
- T1b: kicks off: level 2 against level 1 with `noise_mode_eq = mesh`: the fields stay
  homogeneous, the local coefficients equal the box means up to the rounding of the sum,
  so the projected coefficients agree to < 1e-12 relative at every dump. Refuted if
  larger. (Level 2 against level 1 with per-shell modes differs by the stencil: T3.)
- T1c: kicks on: level 2 minus level 1-mesh is of second order in the noise: relative
  difference of the projected coefficients ~ |R| ~ 1e-5 or below, and it falls by 1e-3
  when the amplitude (`noise_mode_scale`) falls by 1e-3. Refuted if not.
T2 (32^3, nmax2 = 64, kicks on, t = 0 .. 3.2 as T8 of scalar2):
- R^NR against W R alpha of the lockstep (continuum) per mode: modes with |n|^2 <= 48
  within 0.02 (the level-0 values of T8 were a few 1e-3); the six cut modes |n|^2 = 64
  deviate by 1 to 7 per cent (phase error of the stencil: 0.92 per cent in omega over
  about 7 radians of sub-Hubble phase from k/(aH) = 8 to 1, about 0.064 rad). Refuted if
  the cut modes agree within 1e-3 (then the mesh R would not see the stencil) or if any
  mode below the cut exceeds 0.02.
- Sign split: runs with noise_mode_scale = +1 and -1 at levels 2 and 1-mesh. In each run
  the field perturbation delta phi(s); define D(s) = delta phi_L2(s) - delta phi_L1(s).
  Prediction: |D(+1) + D(-1)| / |D(+1) - D(-1)| >> 1 (D even in s: level 2 adds an even
  part only), and |D| / |delta phi| ~ amplitude ~ 1e-5 (second order). Refuted if the odd
  part of D is comparable to its even part.
T3 (kicks off, level 0 mesh, uniform coefficients): projected R per mode against
  (a) the per-shell continuum mode functions: ratio departs by up to ~6 per cent for the
  cut modes and < 1e-3 for |n|^2 <= 48 by t = 3; (b) a SciPy reference with k^2 replaced
  by the stencil symbol per mode and the same background: agreement to the time
  integration error, < 1e-6 relative. Refuted if (b) fails at 1e-4.
T4 byte regression against core-v0.6 (option absent): every file identical.
T5 card smoke at 64^3, both scenarios, levels 0 and 2: completes, finite; level 2 costs
  +5 to +20 per cent of the step time at 64^3 (relatively more than at 256^3 because the
  synthesis share is larger at small N? no: smaller; take +5 to +20).
T6 guard: Pi0 = 0 at level 2 -> Z = 0 -> R non-finite at the first stage -> spacetime
  non-finite through the kicks -> exit status 3 after cycle 1.

## Entry 2 (2026-11-22 19:08 PST): T5 on processors while the card queue is full, prediction

The card queue holds two eligible core jobs (4923, 4924) and four held ones of the row-4
bisection: the rule allows no submission now. T5 is done first with the threaded
processor build of this branch (`.work/build_omp_nl2`), 64^3, nmax2 = 256, 30 cycles of
each of the four inputs of the card list, 6 threads, one after another.
Prediction: every run ends with status 0 and finite records; level 2 costs +5 to +20 per
cent of the wall time of level 0 per cycle (the projection of two fields is about one
third of the six-field synthesis, plus the R right-hand side). Refuted if a run fails, if
a record is not finite, or if the ratio is outside 1.0 .. 1.3.

## Entry 3 (2026-11-22 19:10 PST): outcomes of T1, T2, T3, T4, T6 and the restart check

Runs: processor tests core-20261123-025040-384fbdd (15 runs, 32^3, nmax2 = 64, slow-roll
input, t = 0 .. 3.2 = 3.14 e-folds; exit status 0 for all but the guard run, which ends
with 3); analysis with the figures core-20261123-030623-7676c1f (`fig_t1t3.png`,
`fig_t2.png`, looked at; the legend of fig_t1t3 (b) runs off the right edge, the data are
readable); byte regressions core-20261123-024646-553eefa (scalar field) and
core-20261123-025738-35c2552 (release driver, twelve set-ups).

T1a (projection at t* = the mode file): max relative deviation 1.14e-14 for R and
6.9e-15 for dR/dtau, in the homogeneous level-2 run, the perturbed level-2 run and the
level-0 mesh run. PREDICTION HELD (< 1e-12): the projection is the adjoint of the
synthesis with the same normalisation.

T1b (homogeneous slice, kicks off, level 2 against level 1 on the mesh): max relative
difference of the projected coefficients 3.7e-12 at t = 3.2 (rms 3.0e-12), flat after the
first dump. PREDICTION REFUTED at face value (< 1e-12). Cause, checked in the same run:
the box means are not the cell values to rounding of one operation but to the rounding
of a sequential sum of 32768 equal values: in the dumps of h2off, <K> differs from the
(uniform) cell value by 5.3e-13 to 8.9e-13 relative and <Pi> by 4e-14 to 3.4e-13, so the
level-1 Z = <Pi>^2/H^2 differs from the local 9 Pi^2/K^2 by about 2e-12. The mesh fields
are homogeneous to the last bit (spread of Pi exactly 0). Level 2 equals level 1 to the
rounding of the box mean.

T1c (homogeneous slice, kicks on): max relative difference 9.0e-4 (rms 1.1e-4) at
amplitude 1 and 9.0e-7 (rms 1.1e-7) at amplitude 1e-3: the ratio is 1.000e-3 to four
digits at every dump, so the difference is exactly of second order. PREDICTION HELD for
the order; REFUTED for the size (predicted ~1e-5): the maximum over 1054 modes picks the
modes with small |alpha_n|, and every mode receives the products of all others through
delta Z (x) grad^2 R; the rms 1.1e-4 is ten times the guess.

T2 (32^3, kicks on, t = 3.2): R^NR against the continuum linear reference W R alpha:
level 0 (shells, as released) 2.8e-3 at most (6.8e-4 for |n|^2 <= 48); level 2: 1.2e-2
for |n|^2 <= 48 (within the 0.02 of A2), 7.2e-2 for the six cut modes (+-8,0,0)...;
level 1 on the mesh: 1.2e-2 and 7.1e-2. PREDICTION HELD (cut modes 1 to 7 per cent: at the
top; below the cut within 0.02). Against W c_R of the run's own mesh field (projected
coefficients) the deviation is 1.0e-4 at most for level 2 and 1.3e-5 for level 1 on the
mesh (7.5e-5 over all dumps): the pipeline from the mesh R to R^NR is ten to a hundred
times more accurate than level 0 against its shells, because the mesh R and the mesh
R^NR see the same Laplacian.
Sign split: D = phi_L2 - phi_L1mesh, runs with noise_mode_scale = +1 and -1: even part
rms 3.0e-11, odd part 3.1e-15 at t = 3.2 (ratio 1e-4, every dump between 2e-4 and 1e-4),
against delta phi rms 5.6e-7. PREDICTION HELD: level 2 adds an even part only, of
relative size 5e-5 (second order).

T3 (level 0 on the mesh, kicks off): symbol/k^2 at the cut (axis modes |n|^2 = 64) =
0.98169, a deficit of 1.83 per cent in k^2 (the task text says 2.7 per cent; the
sixth-order symbol gives 1.83; [TO VERIFY] where 2.7 comes from). Mesh R against the
shells at t = 3.2: 7.1 per cent for the cut modes, 3.4 per cent below the cut, 1.18 per
cent for |n|^2 <= 48. PREDICTION REFUTED for |n|^2 <= 48 (predicted < 1e-3): I had
evaluated the symbol only on the shells 1, 16, 32, 48, 64, whose vectors are axis or
diagonal multiples of 4; modes such as (6,0,0) (|n|^2 = 36, symbol/k^2 = 0.9963) carry
0.19 per cent in omega over about 5.7 rad of phase, 1.1 per cent in R. Against a SciPy
reference with k^2 replaced by the stencil symbol mode by mode: 2.8e-4 (prediction <
1e-6: REFUTED); the code's own shells against the SciPy continuum reference differ by
the same 3.0e-4 in the same run, i.e. this is the RK4 time error of the code at
dt = 0.049 (omega dt up to 0.39), common to shells and mesh. The double ratio
(R_mesh/R_shell)/(R_stencil-ODE/R_continuum-ODE) removes it: 2.6e-5 at most at t = 3.2,
against a stencil effect of 7.1e-2. The mesh R and the shells differ by the stencil
symbol of the Laplacian and by nothing else at the level of 4e-4 of the effect
(fig_t1t3 (b): the measured points sit on the predicted ones).

T4 byte regression with the option absent: the ten scalar-field cases of wave 1 and the
three stochastic examples with a restart, against release core-v0.6
(core-20261123-024646-553eefa): every file identical (restart files with the masked
header bytes as defined by the driver). The twelve set-ups of the release driver
(core-20261123-025738-35c2552): 75 of 75 items identical, PASS. PREDICTION HELD.

T6 guard: level 2 on the homogeneous slice with Pi = 0: the warning "1054 noise
coefficients of the mesh path are not finite at time 0", then "NRPIC guard: the run
stops at time 4.9e-02, cycle 1", exit status 3. PREDICTION HELD.

Restart: level 2, 20 cycles, restart file at cycle 10, restarted run to cycle 20: the
dump, the .modes and the .rmodes files of cycle 20 identical byte for byte.

Cost on processors at 32^3 (serial, the runs shared the machine with others): level 0
163.7 s, level 1 on the mesh 163.8 s, level 2 173.7 s (+6 per cent) for 65 cycles.
