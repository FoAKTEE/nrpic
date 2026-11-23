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
