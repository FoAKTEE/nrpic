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

## Entry 4 (2026-11-22 19:25 PST): T5 on processors, publication, what is open

T5 on processors (core-20261123-030705-6b6a4bd, threaded build of the branch, 64^3,
nmax2 = 256, 30 cycles, 6 threads, `fig_timing.png` looked at): all four runs exit 0,
records finite, rms(phi - <phi>) at t = 0.74 equal between the levels to 2e-6 relative
(SR 4.81399e-7 / 4.81400e-7). Wall per cycle: SR 5.51 s (level 0), 5.66 s (level 2),
ratio 1.027; USR 5.46 s, 5.42 s, ratio 0.992. PREDICTION (+5 to +20 per cent, ratio in
1.0 .. 1.3) REFUTED on the low side: at 64^3 on processors the projection and the R
right-hand side do not show above the scatter of a shared machine (one USR ratio below
1). The card cost at 256^3 stays an estimate.

Card smoke T5: not submitted; the queue held two eligible core jobs (4923, 4924) and four
held ones the whole session (checked 18:50, 19:06, 19:19). Pending: submit
`tracks/core/analysis/noise_level2/card_t5.list` with
`harness/bin/nrpic-run submit --launcher batch --list tracks/core/analysis/noise_level2/card_t5.list --exe /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu --wall 00:30:00 --gpu-hours 0.5 --kind scouting --gate G2 --purpose "noise-level2 T5 card smoke"`
when core has fewer than two card jobs.

Origin of the 2.7 per cent of the task text: track/E-stoch-inf
`tracks/E-stoch-inf/repro/scope/SETUP_AUDIT.md`:32 uses the leading term
(k dx)^6/560 = 2.7e-2 at k dx = pi/2 [VERIFIED by reading]; the full symbol gives 1.83e-2.

Published: `scratch/core/exe/core_noise-level2/` (athena_cpu, athena_gpu,
athena_cpu_omp, COMMIT, SHA256SUMS, READY), source 6ca93cba. Outbox to Track E with the
six ablation inputs at 256^3. Open: card smoke, Fable review of the diff, card cost at
256^3.

## Entry 5 (2026-11-22 19:23 PST): level 2 through the ultra-slow-roll phase, prediction

READY listed the inflection case beyond 30 cycles as not tested. While the card queue
stays full: problems/scalar/usr_stochastic.athinput (32^3, nmax2 = 64, to its tlim 10.5,
about 430 cycles) at level 2 and at level 1 on the mesh, per-mode records at the dumps
(`usr_check.py`). In USR Pi_b falls by orders of magnitude, so Z = 9 Pi^2/K^2 becomes
tiny and the level-2 Z(x) is the local square of a small number.
Prediction: both runs end with status 0 and finite records; the relative difference of
the projected coefficients stays of second order in the amplitude: below 1e-2 in rms at
the end (it was 1.1e-4 rms in slow roll at amplitude 1; the USR modes grow by a factor of
order 100 in R, so the second-order part grows by about that factor). Refuted if a run
stops (guard) or the rms difference reaches order one.

Outcome (run core-20261123-032120-3d5b69f, `fig_usr.png` looked at; the y label of panel
(b) is cut at the edge, the data are readable): both runs end with status 0 at t = 10.5,
records finite; the rms of |R_n| of the mesh field falls from 1.8e-5 to 4e-6 by t = 3.5,
then grows by a factor 5600 through the USR phase to 2.3e-2 at t = 8 and freezes.
Level 2 against level 1 on the mesh: rms relative difference of the projected
coefficients 1.9e-3 at the end (max over modes 1.45e-2), up from 1e-4 before the USR
phase. PREDICTION HELD (rms below 1e-2, no stop). The second-order part grows by about
ten while R grows by 5600: not the naive scaling; not investigated further.
Pi_b at the end 2.70e-7 in both (from 3.24e-2 at t*): the local Z falls by 1.4e10 and
the division Pi_R/Z stays finite.

## Entry 6 (2026-11-24 05:02 PST): review of the diff on Fable (decision 0029 item 2), state and plan

Session on Fable, batch R2. Worktree merged with main (bc3e4ca4; merge d9f489db); the
source of the branch is that of 6ca93cba (`git diff 6ca93cba HEAD -- athenak/` empty; the
published executables equal the builds of the worktree, sha256 108e8065.. cpu, 46810949..
card). Read: the diff of the six source files against main, the whole of
`scalar_field_noise.cpp`, `scalar_field.cpp`, `scalar_field_rhs.cpp`, `scalar_field_io.cpp`,
`scalar_field_slice.cpp`, `particles/nrpic_guard.cpp`, `bvals/bvals_cc.cpp` (variable
count), P1:164-196, 220-323, 474-524, 697-711, 776-790, the design note and entries 0-5.

State of Track E's runs with 6ca93cba (read-only, `scratch/E-stoch-inf/repro_scope_seq/
state.tsv` and the chain logs): card smoke T5SMK passed (E-20261123-090718-6203c87,
level 2 / level 0 wall per cycle 1.16 SR and 1.14 USR at 64^3); five of the six 256^3
runs ended at tlim; AL2S (slow roll, level 2, E-20261123-152119-38957ba) stopped at cycle
1227 of 1386 with MAX_SEGMENTS = 2 after a preempted first segment. Throughput on the
card at 256^3, from the chain logs: level 0 on the mesh 1.127e7 zone-cycles/s (AL0S),
level 1 on the mesh 1.123e7 (AL1S), level 2 6.91e6 (AL2S): level 2 costs +63 per cent of
a cycle against level 0 on the mesh, not the +5 to +10 per cent of the design note
(section 7), and that is why AL2S did not fit two segments.

Review by reading and derivation (verdicts; tests follow):
1. Well-posed form [VERIFIED by derivation]. With Z = 9 phidot_b^2/K_b^2 = phidot_b^2/H^2
   = 2 eps1 Mpl^2 (P1:171) and alpha_b = 1, beta = 0, P1:316-317 is Pi_R = Z dR/dt,
   d(Z dR/dt)/dt = -3 H Z dR/dt + Z a^-2 lap R, i.e. R'' + (3 H + Z'/Z) R' + (k/a)^2 R = 0
   with Z'/Z = eps1'/eps1 = -eps2 H in the convention of P1:171: eq. (Req), P1:183. The
   code's pair (d_t R = beta.dR + alpha Pi_R/Z, d_t Pi_R = beta.dPi_R + alpha (K Pi_R +
   Z psi^-4 gt^ij d_i d_j R)) is that system with the code's sign of the shift. Second
   order in space, first in time, principal part d_t^2 R = alpha^2 gamma^ij d_i d_j R:
   a wave equation on the light cone of the local metric for Z > 0. Z stays outside the
   derivative, as printed.
2. Reading of phidot_b as Pi [VERIFIED as the right one]. (i) P1:237 sets alpha_b = 1 in
   the perturbation theory, so phidot_b is the proper-time derivative of the background;
   (ii) P1:485 lists the background input of the authors' code as (phi_b, Pi_b, K_b, X_b):
   the momentum, not a coordinate-time derivative; (iii) with a uniform lapse alpha_b(t)
   the printed system reduces to eq. (Req) in proper time only with phidot_b = dphi_b/dtau:
   with phidot_b = d_0 phi_b = alpha_b Pi_b it becomes d/dtau(alpha_b^2 Z dR/dtau) = ...,
   an extra friction 2 dln alpha_b/dtau at ZEROTH order. In the gauge of the paper and of
   every run of Track E (alpha = 1, beta = 0, all gauge coefficients zero) the two readings
   are the same number in every cell. The other reading would change nothing there and
   would be wrong elsewhere.
3. Laplacian [JUDGEMENT stands; the claim "of second order" in the design note is true
   but is not an argument, level 2 as a whole is of second order]. Three readings:
   F = psi^-4 delta^ij d_i d_j R (only X_b promoted, the list of P1:323 and P1:487),
   M = psi^-4 gt^ij d_i d_j R (implemented), C = D^i D_i R. At the order the paper derives
   (first: P1:496, 790) all three are the same equation; they differ by (first-order
   metric perturbation) x (derivatives of R), the order of the level-2 effect itself, for
   which the paper gives a heuristic (P1:323) and no derivation. The print has partial
   derivatives where the field equation on the same page has covariant ones (P1:224,
   291-292): C is not what is printed. M and C share the principal part (the light cone of
   the evolved metric); F has the cone of the conformally flat metric. M is kept as the
   default. What the others change is measured below (R2), with a prediction: on the
   slice and through the kicks delta K/K, delta chi/chi and gt_ij - delta_ij are all of
   order eps1 R (`scalar_field_slice.cpp`: delta K = 3 eps1 H (A - Psi), Psi = -eps1 H a^2
   B/k^2; kick of At_ij proportional to eps1), while delta Pi/Pi = B/H - ... is of order
   (W'/H) R up to 2.5 R at the crossing of the window: level 2 is, in slow roll, the
   local Pi^2 in Z, and the reading of the Laplacian matters at relative order eps1.
4. Window and kicks at level 2 [JUDGEMENT stands]. P1:783 defines the levels for "the
   coefficients appearing in" the mode equation only. The window multiplies Fourier
   coefficients and must be uniform; the kick factors Pi_b/H and eps1 multiply the
   real-space fields and could be local: uniform is a third judgement, which the design
   note does not name (its "(they multiply Fourier coefficients)" holds for W and the
   friction term only). Means against Friedmann differ at second order in the
   COEFFICIENT (a box mean of a linear perturbation is zero), one order beyond the
   level-2 effect: prediction R3 below.
5. Projection = adjoint of the synthesis [VERIFIED by derivation]: for 2 n_max < N the
   sums N^-3 sum_x e^(i(k_m -+ k_n).x) over the half-shifted lattice are delta_mn and 0
   for two modes of one hemisphere; the three one-dimensional sums carry e^(-i theta)
   in each direction; one writer per mode, MeshBlocks in sequence.
6. Stage coefficients [VERIFIED by reading]: R and Pi_R are components of u0, u1, u_rhs:
   `CopyU` (deep copy at stage 1, += delta u0 after), `ExpRKUpdate` (gam0, gam1, beta dt)
   over nvar_sf; the lockstep data use the same three numbers (`NoiseCopy`,
   `NoiseUpdate`); the projection of a stage reads the u0 of that stage, after the ghost
   exchange of the previous one, and before Z4c's update (SF_CalcRHS -> SF_Kick ->
   Z4c_ExplRK).
7. Restart [VERIFIED by reading]: u0 whole with its extents (a restart file of a run
   without the mesh fields is refused by the extent check), y0; `NoiseSetup(true)`
   allocates the work arrays; `NoiseMeshInit` is skipped.
8. Ghost cells [VERIFIED by reading]: `PackAndSendCC` takes the variable count from the
   array; `InitRecv(nvar_sf)`; the sources need periodic faces (fatal otherwise), so no
   physical boundary routine sees components 2, 3; `NoiseMeshExchange` is the sequence of
   the driver. Static refinement is refused.
9. Guard: with a kick on, a zero of Pi in one cell makes every coefficient non-finite in
   the same stage and <z4c_guard> stops the run after the cycle (T6). With all kicks off
   the projection is not called in the stages and nothing stops the run: the warning
   comes at the next dump only. The guard tests the spacetime fields only (also for phi,
   Pi with `couple = false`): a limit of the guard, not of this branch; recorded.
10. Card [by reading: no defect found]: every kernel captures local copies of the views
    and local scalars, none captures `this`; the accumulation over MeshBlocks is a host
    loop with one writer per (field, mode); host mirrors are filled and copied for W',
    W''; `mode_cre/cim` are captured unallocated when the option is off and never read.
11. Cost: DEFECT (performance). `sf_prj_x` recomputes V = Pi_R K^2/(9 Pi^2) for each of
    the n_x rows (65 at 256^3) from four arrays, with a division: 1.1e9 divisions and
    35 GB of reads per stage at 256^3 against 16.8e6 and 0.5 GB if V is formed once.

Plan: R0 the branch's tests again with the published executable; then V once per stage
in a work array (bit-identical by construction: R1), the option that selects the reading
of the Laplacian (R2), the background of the window (R3), a run with a lapse that is not
1 (R4: no test of the branch has alpha != 1), byte regression against core-v0.6, card
timing at 256^3.

Prediction R0 (the fifteen runs of `cpu_tests.py` with
`scratch/core/exe/core_noise-level2/athena_cpu`, as run core-20261123-025040-384fbdd):
every dump, .modes, .rmodes, .hst and restart-compared file is byte for byte that of the
recorded run (a processor run repeats), hence the same numbers in summary.json. Refuted
by any differing file.

## Entry 7 (2026-11-24 05:12 PST): two source changes of the review, predictions R1 to R4

Source (both in `scalar_field_noise_mesh.cpp`, two members in `scalar_field.hpp`, one
block of `NoiseInit`):
(a) Level 2: V = Pi_R K^2/(9 Pi^2) is formed once per call of `NoiseMeshCoefficients`
    in a work array `prj_v` (one double per active cell; 134 MB at 256^3) and the first
    sum reads it. The expression and the order of every sum are unchanged.
(b) `<scalar_field> noise_level2_laplacian = metric | covariant | flat`, read only if
    present and only at level 2; default metric = the kernel as it was. covariant adds
    -Gt^k d_k R + 2 gt^ij d_i ln psi d_j R (the Laplacian of the field in
    `scalar_field_rhs.cpp`), flat takes psi^-4 (d_xx + d_yy + d_zz) R. A sensitivity
    option: it exists to measure what the reading of P1:317 changes.

Predictions, written before the new executable has run a step (processors, 32^3,
nmax2 = 64, slow-roll input; the executable is `.work/build_cpu_nl2/src/athena`, sha256
31a88cb3..):

R1 (identity): the fifteen runs of `cpu_tests.py` with the new executable give, file by
file, the bytes of R0 (dumps, .modes, .rmodes, .hst): change (a) keeps every operation
and its order on processors, and change (b) is not selected. Refuted by one differing
file; then the published executables are NOT equivalent to the reviewed source and the
cause has to be found before anything else.

R2 (reading of the Laplacian; `review_tests.py`, perturbed slice, kicks on, t = 3.2):
measured on the projected coefficients c_R(n) as rms over the 1054 modes of
|c^(1)/c^(2) - 1|. (i) covariant against metric and flat against metric are of second
order: at amplitude 1e-2 the relative difference is 1e-2 of that at amplitude 1 (within
a factor 2), as is level 2 against level 1 on the mesh. (ii) Both are between 1e-3 and
1e-1 of the level-2 effect (level 2 against level 1 on the mesh): the metric and K carry
perturbations of order eps1 R (eps1 = 4 pi Pi^2/H^2 = 1.1e-2 at N*), Z carries
2 delta Pi/Pi of order R (entry 6 item 3). Refuted if a reading changes c_R at first
order (ratio of the two amplitudes near 1), or if either difference exceeds 0.3 of the
level-2 effect (then the level-2 curve of the ablation depends on the reading and the
note must say by how much), or if it is below 1e-4 of it (then the estimate by eps1 is
wrong).

R3 (background of the window and kicks at level 2): Friedmann against means changes c_R
by about what level 1 on the mesh differs from level 0 on the mesh (ratio between 0.1
and 10), and both are below 1e-2 of the level-2 effect: the box means leave the
Friedmann solution at second order in the coefficient (and by the time-integration error
of the mesh background), the local coefficients at first. Refuted if Friedmann against
means exceeds 0.1 of the level-2 effect.

R4 (a lapse that is not 1; homogeneous slice, kicks off, <z4c> lapse_harmonic = 1/3,
i.e. alpha = a, conformal time to 0.85, alpha grows to about 6): (i) level 2 equals level
1 on the mesh to the rounding of the box means, max over modes below 1e-9 for R and for
n.d R at every dump (T1b gave 3.7e-12 with alpha = 1); (ii) the mesh R against the shells
(which integrate in proper time, d tau = alpha dt) shows the stencil and nothing else: at
equal ln a the deviation is that of the geodesic run within a factor 2 (cut modes and
|n|^2 <= 48), and it stays below 0.1; (iii) the same for n.d R = Pi_R/Z against dR/dtau
of the shells. Refuted by a deviation of order one (a lapse factor in the wrong place in
the mesh path grows with alpha), or by level 2 differing from level 1 above 1e-9.

## Entry 8 (2026-11-24 05:20 PST): outcome of R0; prediction of the card job R5

R0 (run core-20261124-130250-0a4a7cb, comparison core-20261124-131414-c50780b): all
fifteen runs exit as recorded (guard 3, the others 0); 366 files (every dump, .modes,
.rmodes, .hst of the fourteen run directories) are byte for byte those of
core-20261123-025040-384fbdd; summary.json has the numbers of entry 3 (T1a 1.14e-14 /
6.9e-15, T2 level 2 against its own mesh field 1.0e-4, 7.5e-5 over all dumps).
PREDICTION HELD: the tests of the branch repeat.

R5, card (list `analysis/noise_level2/card_review.list`, the card executable of 746869ef,
sha256 of `.work/build_gpu_nl2/src/athena` in the manifest; at most 0.33 card-hours):
(i) `sr64_l2` and `usr64_l2`, the two level-2 decks of T5, against Track E's smoke runs of
the executable of 6ca93cba (E-20261123-035724-b661081): the history records agree to
1e-10 relative in the box means and 1e-7 in the rms of the perturbations at every cycle,
and I expect every file identical (no kernel of these runs has an order that depends on
the run; the new kernel forms the same V). Refuted by a difference above 1e-7: then the
two executables are not equivalent on the card and Track E's level-2 runs would have to
be judged again.
(ii) 256^3, 60 cycles without dumps, the slow-roll deck of the ablation: level 2 against
level 0 on the mesh. With 6ca93cba the ratio of the throughputs was 1.127e7/6.91e6 =
1.63 (AL0S, AL2S of Track E). Prediction: at most 1.18 with the new executable (the
local right-hand side of R adds the mixed derivatives and the inverse metric; the
projection now reads two fields as at level 0). Refuted above 1.3: then the recomputed V
was not the cost.

## Entry 9 (2026-11-24 05:35 PST): card queue; predictions R6 (threads) and R7 (how far Z is from zero)

Card job R5 not submitted: core has two eligible card jobs queued (5154, 5155, the
row-4 bisection of the other core session) and four held ones; the rule allows no third
(squeue 05:21 and 05:36). The list, the decks and the analysis are committed
(`card_review.list`, `card_review.py`); the command is in the handoff of this entry's
close. Until it has run, the card executable of the review has not run a step on a card.

One run killed by my own mistake: core-20261124-133150-a891a9d (the byte comparison of
R1 under a 110 s limit of the shell, which the comparison of 2 x 1.2 GB exceeds while
five runs use the disk); repeated without the limit as core-20261124-133348-9d8c01f.

R6 (`omp_identity.py`): the threaded executable of the review against the published
threaded executable of 6ca93cba, the two level-2 decks of T5 at 64^3 (nmax2 = 256), 12
cycles, three threads each, side by side, dumps and the per-mode record at cycles 0, 6,
12. Prediction: every file identical (the new kernel is a plain parallel loop over the
cells; the sums of the projection keep their order; a threaded run repeats at a fixed
thread count). Refuted by a differing file; then the old executable is run twice to see
whether it repeats itself.

R7 (`pi_range.py`, read-only on Track E's level-2 runs AL2S E-20261123-152119-38957ba
and AL2U E-20261123-153146-d965002, 256^3): the local Z = 9 Pi^2/K^2 divides Pi_R in
every cell; the run is meaningful only while Pi keeps its sign and |delta Pi| << |Pi|.
Prediction: slow roll: max over the cells of |Pi/<Pi> - 1| below 1e-3 at every dump
(perturbations of order 1e-5 times a few sigma times the window factor); inflection
case: larger, because Pi_b falls by 1e5 while the perturbations grow, between 1e-3 and
0.3, and Pi never comes within a factor 2 of zero (min of Pi/<Pi> above 0.5). Refuted
if Pi/<Pi> falls below 0.5 in a cell of AL2U: then level 2 runs close to the singular
point of its equation in that run and the reproduction has to say so beside the
level-2 curve.

## Entry 10 (2026-11-24 05:44 PST): outcomes R1 to R4; a finding on level 1 against level 0; predictions R8, R9

R1 (runs core-20261124-131622-50359df, comparison core-20261124-133348-9d8c01f): the
fifteen runs of the executable of 746869ef give the bytes of R0, 366 of 366 files, and
the same summary. PREDICTION HELD: forming V once per stage changes no bit on
processors, and the option that is not selected changes nothing.

R2, R3, R4 (run core-20261124-133135-2cbebd5, thirteen runs, all exit 0;
`fig_readings.png`, `fig_lapse.png` looked at: in fig_readings (a) and (c) the legends
lie over part of the curves, in fig_lapse (b) the y label touches the tick labels; the
data are readable; redrawn with the next analysis).

R2. Level-2 effect (level 2 against level 1 on the mesh, rms over 1054 modes of
|c^(1)/c^(2) - 1| at t = 3.2): 1.447e-4. Covariant against metric: 2.85e-7 = 2.0e-3 of
it; flat against metric: 3.93e-7 = 2.7e-3 of it (largest ratio over the dumps the same).
At amplitude 1e-2 the three relative differences are 1.0000e-2, 1.0002e-2 and 1.0000e-2
of their values at amplitude 1: second order, all three. Shell power of R^NR at t = 3.2
(the quantity of P1 Fig. 9, here 32^3): covariant/metric 1.4e-7 at most, flat/metric
3.0e-7 at most, against 1.5e-4 for level 2 / level 0 on the mesh. PREDICTION HELD (band
1e-3 to 1e-1 of the level-2 effect; the result sits at the low end, 0.2 eps1 rather than
eps1). The reading of the Laplacian changes the level-2 effect by a quarter of a per
cent in slow roll; level 2 is the local Pi^2 in Z.

R3. Friedmann against means for the window and kicks of level 2: 2.34e-8 = 1.6e-4 of
the level-2 effect. PREDICTION HELD (below 0.1, and below the 1e-2 I gave for both).
REFUTED in its other half: level 1 on the mesh against level 0 on the mesh is 5.67e-5,
0.39 of the level-2 effect and 2400 times the Friedmann-against-means number; I had
predicted the two alike and both below 1e-2 of the level-2 effect.

Finding behind the failed half (checked on files that exist, before any new run): the
difference between level 1 and level 0 on the mesh does not come from the perturbations.
(i) It is 5.06e-5 at the first dump (t = 0.44) and stays (4.7e-5 to 6.1e-5), largest at
the cut (rms 7.9e-5 for |n|^2 > 48, 5.4e-6 for |n|^2 <= 16). (ii) R0's `h1off` (level 1,
homogeneous slice, kicks off) against R0's `m0off` (level 0 on the mesh, perturbed
slice, kicks off) gives the same 5.06e-5, 4.72e-5, ..., 5.67e-5 dump by dump as `s1m`
against `s0m` with the kicks on; level 0 on the mesh with and without kicks agrees to
4e-17. So it is of ZEROTH order in the amplitude. (iii) In the history of `s0m` the box
means and the Friedmann lockstep agree to 3e-12 in Pi and H at every cycle, and the
scale factor <chi>^(-1/2) of the mesh falls behind exp(ln a) of the lockstep linearly in
time, -3.2e-7 at t = 0.39, -2.4e-6 at t = 3.2: the Runge-Kutta error of the exponential
chi (per step (2 H dt)^5/120 = 7.6e-8 in chi, 65 steps). The coefficients at the END of
a step therefore differ by too little to give 5e-5 at t = 0.44. What differs is the
integration: at level 1 the coefficients of a stage are the stage values of mesh
variables (chi, K as the mesh integrates them), at level 0 the stage values of the
lockstep (ln a, and H from the Friedmann constraint): two fourth-order integrations of
one continuum system, whose truncation errors differ, most for the modes with
omega dt = 0.39 at the cut (the time error of R itself is 2.8e-4 there, entry 3).
[JUDGEMENT until R8 has run.]
Why it matters: k_max dx = pi/2 and the Courant number fix omega_max dt = 0.39 at every
N, so this difference does not shrink at 256^3; the level-1 curve of the ablation (and
with it the part of "level 2 against level 0" that is not "level 2 against level 1") may
be a property of the time integration, not a backreaction. P1's level 0 is the same
construction ("evolved separately with the same initial conditions and numerical
scheme", P1:785).

R4 (conformal-time lapse, alpha from 1 to 6.4): (i) level 2 against level 1 on the mesh:
8.0e-12 at most for R, 5.8e-12 rms for n.d R, at every dump below 1e-11. (ii) mesh R
against the shells at equal ln a, lapse = a against geodesic slicing: cut modes
6.71e-2 against 6.71e-2 at ln a = 1.85, 5.12e-2 / 5.11e-2 at 1.01, 2.99e-2 / 2.91e-2 at
0.42; |n|^2 <= 48: 1.03e-2 / 1.03e-2, 7.07e-3 / 7.09e-3, 5.16e-3 / 5.10e-3; the first
point (ln a = 0.10) 5.3e-3 against an interpolated 8.4e-3. (iii) n.d R against dR/dtau
of the shells: 6.5e-2 (cut) and 8.5e-3 at ln a = 1.85 against 6.7e-2 and 8.8e-3 at 1.98
with geodesic slicing. PREDICTION HELD on all three: the lapse stands where it should in
the uniform and in the local path for a lapse that depends on time; a lapse that varies
in space, and a shift, remain untested.

Prediction R8 (`level01_dt.py`: homogeneous slice, kicks off, level 1 and level 0 on the
mesh, Courant numbers 0.25, 0.125, 0.0625, the per-mode record after 10 and 20 cycles of
the coarsest step, t = 0.49 and 0.98): the rms difference of c_R between the two levels
is 5e-5 at Courant 0.25 (as found) and falls by a factor between 12 and 20 per halving
of the step: fourth order. Refuted by a factor below 8: then something of lower order
differs between the two paths and that is a defect to find.

Prediction R9 (`ablation_modes.py`, read-only on the per-mode records of Track E's
slow-roll runs AL0S, AL1S, AL2S at 256^3, dumps 2, 6, 10, 15): (a) level 1 against
level 0: rms over the modes between 1e-4 and 2e-3 at the late dumps (the 32^3 value times
the longer stay below the horizon, about 8), rising with |n|: the band 48 <= |n| < 65 at
least five times the band |n| < 8; (b) level 2 against level 1: between 2e-4 and 5e-3
(second order, more modes than at 32^3); (c) so level 1 against level 0 is between 0.05
and 2 of level 2 against level 1: not negligible. Refuted if (a) is below 1e-5 (then the
32^3 finding does not carry to the production runs).

## Entry 11 (2026-11-24 05:49 PST): outcomes R7, R8; prediction R10 (byte regression against core-v0.6)

R8 (run core-20261124-134414-1db640d, six runs, exit 0; `fig_level01.png` looked at:
three points per time on the line of slope 4): level 1 against level 0 on the mesh,
homogeneous slice, kicks off: rms over the modes 5.00e-5, 2.95e-6, 1.80e-7 at t = 0.49
and 5.29e-5, 3.32e-6, 2.08e-7 at t = 0.98 for the Courant numbers 0.25, 0.125, 0.0625:
factors 16.9, 16.4 and 16.0, 15.9 per halving. PREDICTION HELD (12 to 20): the
difference is of fourth order in the step. Named cause, now after a run in which it
could have failed: level 1 and level 0 on the mesh are two fourth-order integrations of
the same background (the mesh's chi and K against the lockstep's ln a and the Friedmann
constraint); what an ablation "level 1 against level 0" shows at a fixed Courant number
is first of all the difference of their truncation errors, zeroth order in the
perturbation, 5e-5 in the mode coefficients at Courant 0.25 at 32^3 (7e-5 at the cut,
7e-6 for |n|^2 <= 16).

R7 (run core-20261124-133522-10f8c7a, Track E's level-2 runs at 256^3, read-only;
`fig_pi_range.png` looked at: the legend lies over the last points of the lower curves,
the data are readable): AL2S (16 dumps to t = 7.5): max over the cells of
|Pi/<Pi> - 1| = 8.9e-5 (at t*, rms 3.6e-5), falling below 1e-6 after the last mode has
entered; rms of K/<K> - 1 about 2e-7 throughout, eps1 times the Pi figure. AL2U (21
dumps to t = 10.44): 6.4e-2 at the end (rms 1.2e-2), rising through the
ultra-slow-roll phase; K to 1e-12. PREDICTIONS HELD (below 1e-3; between 1e-3 and 0.3,
Pi/<Pi> never below 0.5: the smallest value is 0.936). The local Z stays within 13 per
cent of its mean in the inflection run and within 2e-4 in slow roll: level 2 ran far
from the zero of Pi in both. The same numbers say what level 2 is made of: the local
Pi, the local K being smaller by eps1 (slow roll) or negligible (inflection).

Prediction R10 (the two byte regressions of entry 3 with the executable of 746869ef
against release core-v0.6, `.work/build_cpu_v06` of the main checkout): the ten
scalar-field cases and the three stochastic examples with a restart: every file
identical; the twelve set-ups of the release driver: 75 of 75. Refuted by any
difference (the review added one member to the options and one branch to the kernel of
the mesh fields, neither reached without the options).

## Entry 12 (2026-11-24 05:54 PST): outcome R9; a level 0 that takes the step of the mesh; predictions R9b, R11

R9 (run core-20261124-134904-30f2df3, the per-mode records of AL0S, AL1S, AL2S at
256^3, dumps at t = 1.0, 3.0, 5.0, 7.5; `fig_ablation_modes.png` looked at after R9b):
(a) level 1 against level 0: rms over 548958 modes 6.7e-6 at t = 1.0 and 7.0e-6 from
t = 3.0 on, frozen; bands of |n| (0-8, 8-16, 16-32, 32-48, 48-65): 1.3e-8, 1.1e-7,
9.3e-7, 3.5e-6, 8.9e-6. PREDICTION REFUTED in size (1e-4 to 2e-3 predicted; and it is
below the 1e-5 at which I said the finding would not carry): I had scaled the 32^3
value up by the longer stay below the horizon and forgot that H dt is eight times
smaller at 256^3; the difference lives in the background's stage values and falls with
H dt at a fixed omega dt. HELD in shape: 680 between the lowest and the highest band.
(b) level 2 against level 1: 1.5e-4 at t = 1.0, 2.2e-4 from t = 3.0 on, flat in |n|
(1.6e-4 to 2.7e-4 by band). HELD (2e-4 to 5e-3). (c) ratio (a)/(b) = 0.032, below the
0.05 to 2 I gave. Per mode, then, the production runs are dominated by level 2 against
level 1. But P1 Fig. 9 shows shell POWER: the level-2 differences have a random sign
from mode to mode and average down within a shell of thousands of modes, the level-1
against level-0 difference has one sign in a shell. That is R9b.

Decision (source): `<scalar_field> noise_background_eq = constraint | evolved`, read
only if present, default constraint = the released lockstep (phi_b, Pi_b, ln a, H from
the Friedmann constraint). evolved adds chi_b and K_b to the lockstep data (two values at
the end of the vector) and integrates the homogeneous universe as the mesh does:
d_t Pi_b = alpha (K_b Pi_b - V'), d_t chi_b = -(p/6) alpha chi_b K_b,
d_t K_b = alpha (K_b^2/3 + 4 pi (2 Pi_b^2 - 2 V)); H = -K_b/3 and a = chi_b^(2/p), the
arithmetic of level 1 on the box means. Reasons: (i) the option `noise_mode_eq = mesh`
exists so that the ablation compares "runs that differ by the coefficients only"
(design note section 2), and with the constraint form level 0 and level 1 differ by
their time integration before any backreaction; (ii) P1 reads (phi_b, Pi_b, K_b, X_b) as
the background (P1:485) and evolves level 0 "with the same ... numerical scheme"
(P1:785): the paper's level 0 is, by its own words, the evolved form. [JUDGEMENT on the
reading of P1:785; VERIFIED that P1:485 lists K_b and X_b.] Changed lines: `NoiseInit`
(option, length of the lockstep vector), `NoiseSetup` (two initial values; the scaling
of the mode functions stops at the last mode value, which is where the vector ended),
`NoiseBackground` and `NoiseModeRHS` (a branch each, the old statements unchanged in
the other), `NoiseWriteState` (one header line with the option), `InitialSlice` (two
initial values). Syntax-checked; not yet built (the processor executable is in use by
R10).

Prediction R9b (`ablation_modes.py` with the shell power P(|n|^2) = mean over the shell
of |c_R|^2, same three runs, dumps 6 and 15): level 1 / level 0 is a smooth curve of one
sign rising to about 2 x 8.9e-6 = 1.8e-5 in the last band (twice the coefficient
difference); level 2 / level 1 scatters about zero with an rms over the shells well
below 2 x 2.2e-4 (averaged over the modes of a shell: between 3e-6 and 1e-4 in the last
band, where a shell has about a thousand modes); so in the last band the two are within
a factor 10 of each other: the level-2 curve of the figure against level 0 is not clean
of the time-integration difference at high k. Refuted if level 1 / level 0 is below a
tenth of level 2 / level 1 in every band.

Prediction R11 (`level0_evolved.py`, 32^3, the executable with the option):
(a) homogeneous slice, kicks off: level 0 on the mesh with the evolved background
against level 1 on the mesh: rms over the modes below 1e-9 at every dump (the mesh's K
carries Theta, i.e. the truncation of the Hamiltonian constraint, of order 1e-12), where
the constraint form gives 5e-5; the lockstep chi_b, K_b equal the box means to 1e-10.
(b) perturbed slice, kicks on: the same pair differs by the backreaction on the means,
second order in the COEFFICIENT: below 1e-6 at amplitude 1, and at amplitude 0.1 a
hundredth of that (within a factor 3; the rounding of the box means, about 1e-11, is
the floor). (c) a run with the option restarted at cycle 10 gives the bytes of the
uninterrupted run at cycle 20. Refuted if (a) exceeds 1e-9 (then the lockstep does not
take the mesh's step), or if (b) does not fall with the amplitude.

## Entry 13 (2026-11-24 06:21 PST): outcomes R9b, R10 (source 746869ef), R11

R10 with the executable of 746869ef (runs core-20261124-134935-c86b2a4 and
core-20261124-134937-cb4bb65): the three stochastic examples 16 of 16 files each, the
restart cases identical (restart files with the masked header bytes of the driver), the
ten wave-1 cases passed; the release driver: twelve set-ups, every item identical,
REGRESSION PASS. PREDICTION HELD. (Repeated below for the final source.)

R9b (run core-20261124-135441-64f150e; `fig_ablation_power.png` and
`fig_ablation_modes.png` looked at: level 1 / level 0 is a smooth line that oscillates
with |n| under a cloud of level-2 points; the blue level 2 / level 0 points lie under
the orange ones): shell power of the mesh R at 256^3, t = 7.5. Level 1 / level 0: rms
over the shells 3.5e-7, largest 6.5e-7, one sign in every band (band means -1.1e-8,
-6.3e-8, -2.2e-7, -3.9e-7, -2.2e-7). Level 2 / level 1: rms 3.4e-5, largest 7.3e-4,
band rms 5.8e-5, 5.3e-5, 4.8e-5, 3.1e-5, 2.3e-5, band means between -4e-6 and +4e-6.
PREDICTION REFUTED: I expected level 1 / level 0 to reach 1.8e-5 (twice the coefficient
difference) and to be within a factor 10 of level 2 / level 1 at high k; it is 4e-7,
sixty times below. The coefficient difference of 8.9e-6 is almost all phase: the mode
function is shifted in time, its modulus changes by 2e-7. HELD: level 2 / level 1
scatters about zero, 2.3e-5 in the last band. For the figure of the reproduction: at
256^3 the level-2 curve is not touched by the time-integration difference; the level-1
curve IS that difference (4e-7, smooth, one sign).

R11 (run core-20261124-141250-48042a3, executable of the source of 64f150ec, sha256 0222e5f0.., ten runs,
exit 0; `fig_level0_evolved.png` looked at):
(a) homogeneous slice, kicks off: level 0 on the mesh with noise_background_eq = evolved
against level 1 on the mesh: rms over the modes 7.6e-12 at t = 3.2 (largest 1.1e-11;
n.d R 8.7e-12), every dump below 1e-11; the constraint form: 5.67e-5. Lockstep against
box means at t = 3.2: chi -4.9e-12, K -1.9e-12, Pi -1.0e-12 (the constraint form left
the scale factor 2.4e-6 behind). PREDICTION HELD (below 1e-9, means within 1e-10).
(b) perturbed slice, kicks on: 6.5e-12 at amplitude 1 and 4.2e-12 at amplitude 0.1
(ratio 0.45 to 0.64 over the dumps). HELD that it is below 1e-6; REFUTED that it falls
by a hundred with the amplitude: both sit on the rounding of the box means. The
backreaction on the means is below 1e-11 in this slow-roll case at 32^3: with the
evolved background level 1 and level 0 are the same run to rounding, and all that
"level 1 against level 0" showed with the constraint form (5.7e-5) was the difference
of the two time integrations.
(c) restart at cycle 10: dump, .modes and .rmodes of cycle 20 identical.

## Entry 14 (2026-11-24 06:23 PST): final source 64f150ec: predictions of the closing runs

The source is that of commit 64f150ec (`git diff 64f150ec HEAD -- athenak/` empty):
6ca93cba plus V once per stage, `noise_level2_laplacian`, `noise_background_eq`.
Executables: `.work/build_cpu_nl2/src/athena` sha256 0222e5f0.., `.work/build_gpu_nl2`
d7069a4e.., the threaded one building.

Predictions (all "nothing changes where the new options are absent"):
R10f byte regression against core-v0.6 (runs core-20261124-142019-4e1c3a5 and
core-20261124-142032-79291d0, submitted before this entry was written; no output read
yet beyond the first three cases of the driver): every file identical, the driver PASS.
R1f the fifteen runs of `cpu_tests.py` with the final executable: the bytes of R0
(366 files), i.e. of 6ca93cba. Refuted by one differing file.
R6 `omp_identity.py`: the threaded executable of the final source against the published
threaded executable of 6ca93cba, level 2 at 64^3, three threads: every file identical.
Example: `problems/scalar/sr_stochastic_l2.athinput` runs and gives the bytes of
`sr_stochastic.athinput` with `noise_level = 2` (the options it names are the
defaults).

## Entry 15 (2026-11-24 06:33 PST): PAUSED (locks/PAUSE found at 06:31); where the review stands

The pause flag appeared between 06:23 and 06:31. I found it in the same shell command
that submitted R1f (the check and the submission were chained; the run was started before
I read the answer): run core-20261124-143147-2ff64b9 is therefore running on five cores
and will end on its own in about eleven minutes; it is registered and NOT closed. Nothing
was started after that. No card job of this package exists.

Closed before the pause, outcomes:
- R10f, final source 64f150ec (runs core-20261124-142019-4e1c3a5 and
  core-20261124-142032-79291d0): scalar-field cases flrw 1, flrwg 1, plane 8, wave 12,
  smr 1, power 15, powerm 15, ms 27, msnk 27 files identical, msr 11 identical and 2
  masked; sr, usr, srg 16 of 16 each and their restarts 8 of 8; the release driver
  twelve set-ups, 75 identical items, REGRESSION PASS. PREDICTION HELD.
- Example (run core-20261124-142347-bd744f6): `sr_stochastic_l2.athinput` runs; 8 of 8
  files are those of `sr_stochastic.athinput` with `noise_level = 2`. PREDICTION HELD.
- Figures of R2 to R4 redrawn (run core-20261124-142629-8516adb, numbers unchanged):
  NOT yet looked at; the first versions were (entry 10).

Not done (in the order to do them; nothing below was started):
1. Close R1f and compare it with R0:
   `harness/bin/nrpic-run finish core-20261124-143147-2ff64b9`, then
   `harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --background --package tracks/core/analysis/noise_level2 --purpose "R1f: byte comparison with R0" -- python3 tracks/core/analysis/noise_level2/bytecmp.py --a /data/haiyangw/nrpic/scratch/core/core-20261124-130250-0a4a7cb --b /data/haiyangw/nrpic/scratch/core/core-20261124-143147-2ff64b9 --out '$NRPIC_RUN_DIR'`
   (prediction, entry 14: 366 of 366 identical).
2. R6: `... --cores 6 ... -- python3 tracks/core/analysis/noise_level2/omp_identity.py --old /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_cpu_omp --new /data/haiyangw/nrpic/wt/core-s2/.work/build_omp_nl2/src/athena --out '$NRPIC_RUN_DIR'`
   (prediction, entries 9 and 14: every file identical).
3. Publish the reviewed executables: `.work/build_cpu_nl2/src/athena` (sha256 0222e5f0..),
   `.work/build_gpu_nl2/src/athena` (d7069a4e..), `.work/build_omp_nl2/src/athena`
   (31210622..) into `scratch/core/exe/core_noise-level2/reviewed/` with COMMIT (64f150ec),
   SHA256SUMS and READY (draft: `scratch/core/tmp/READY.reviewed`, its TESTED block still
   to be written from section 12 of the interface text); leave the set of 6ca93cba in
   the directory above untouched until the card job has passed, and put a note at the
   top of its READY.
4. Card job R5 when core has fewer than two card jobs queued:
   `harness/bin/nrpic-run submit --launcher batch --list tracks/core/analysis/noise_level2/card_review.list --exe /data/haiyangw/nrpic/wt/core-s2/.work/build_gpu_nl2/src/athena --wall 00:20:00 --gpu-hours 0.33 --kind scouting --gate G2 --purpose "noise-level2 review R5"`,
   then `card_review.py --run <batch dir> --smoke /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261123-035724-b661081 --out '$NRPIC_RUN_DIR'`
   (predictions, entry 8). If Track E adds level-0 runs with the evolved background,
   a 64^3 deck with `noise_background_eq = evolved` belongs in that list first.
5. Look at the redrawn figures of run core-20261124-142629-8516adb; redraw
   `fig_pi_range.png` (`pi_range.py --replot <json of core-20261124-133522-10f8c7a>`).
6. The inflection case with `noise_background_eq = evolved` (32^3, `usr_check.py` with
   the option): untested; there the backreaction on the means may be above rounding.

Posted with this entry: the message to Track E (outbox), which says that its six runs
stand, how the three curves are to be read, and that the reviewed executables are not
yet published.
