# Stochastic backreaction of level 2: the curvature perturbation as a mesh field

Owner: core, branch `core/noise-level2` (decision 0029 item 2). Written on Opus on
2026-11-22; reviewed on Fable on 2026-11-24 (decision 0031 item 4): section 12 has the
verdicts, what the review changed, and the verdict for release v0.7. Request: Track E,
`repro/scope/outbox_draft/core_noise_level2.md` (branch `track/E-stoch-inf`). Paper:
P1 = arXiv:2512.14649 v2, `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`, lines
`P1:<n>`. Journal of the tests: `tracks/core/JOURNAL-noise-level2.md` (entries 0 to 5
the implementation, 6 to 15 the review, 16 and 17 its close). Results: sections 9 and 12.

## 1. What P1 does and what the code did before

P1 evolves the curvature perturbation R(t, x) as a real-space field next to BSSN, in its
"well-posed" form (P1:312-320)

    Pi_R = 9 phidot_b^2/(alpha_b K_b^2) (d_0 R + beta^i d_i R)
    d_0 Pi_R - alpha_b K_b Pi_R + beta_b^i d_i Pi_R - 9 phidot_b^2 alpha_b/K_b^2 d_i d^i R = 0,

draws R*(x) and d_t R*(x) once at t* (P1:312, 486), and at every RK4 stage Fourier
transforms R and d_t R, forms the noise from the coefficients, and transforms back
(P1:489-494). The three levels of backreaction (P1:783-788) are the source of the
coefficients of this equation: 0 the Friedmann equations, 1 their box means, 2 the local
values phi_b -> phi(t, x), K_b -> K(t, x), alpha_b -> alpha, beta_b -> beta (P1:323; "X_b"
also, P1:487). The runs of P1 use level 2 (P1:487, 520); its Fig. 9 compares 2 and 1 with 0.

Before this branch the code (`scalar_field_noise.cpp`, levels 0 and 1) integrated one
complex mode function per shell |n|^2 with the continuum k^2, on the host, in lockstep
with the stages; the field was never formed on the mesh. Two differences from P1 follow:
level 2 is impossible (local coefficients need a field), and the mode equation uses the
continuum k^2 where P1's real-space field sees the stencil of the Laplacian (Track E,
`SETUP_AUDIT.md` item (c)).

## 2. The options

    <scalar_field>
    noise_level   = 2                 # 0, 1 as before; 2 = local coefficients (new)
    noise_mode_eq = mesh              # shells (default for 0, 1) | mesh (default and only
                                      # choice for 2); read only if present
    noise_level2_background = means   # means (default) | friedmann; read only if present
    noise_level2_laplacian  = metric  # metric (default) | covariant | flat; level 2, read
                                      # only if present (review; section 3)
    noise_background_eq = constraint  # constraint (default) | evolved; read only if
                                      # present (review; section 6a)
    noise_rmodes_dump = false         # per-mode record next to each dump; only if present

`noise_mode_eq = mesh` with level 0 or 1 is P1's own form of those levels (the mesh field
with the uniform coefficients of the level). With `noise_background_eq = evolved` beside
it, level 0 takes the same time step as level 1 on a homogeneous mesh, and an ablation of
P1 Fig. 9 compares runs that differ by the coefficients only; with the default
(constraint) level 0 and level 1 differ at fourth order in the time step before any
backreaction (section 12, finding F1). Without these lines nothing changes: the number of
evolved variables, the task list, every kernel and every output stay as in core-v0.6
(byte regression, sections 9 and 12).

## 3. The two mesh fields and their equations

Variables of the code: G = c = 1, K = -3H, Pi = n.d phi (normal derivative), the shift
enters as d_t = beta^i d_i + alpha n.d (`scalar_field.hpp`). The paper's phidot_b is the
proper-time derivative of the background field (P1 sets alpha_b = 1, P1:237, 483), so in
the code's variables 9 phidot_b^2/K_b^2 is

    Z = 9 Pi^2/K^2  ( = Pi^2/H^2 = eps1/(4 pi) ),

and Pi_R = Z n.d R. For alpha = 1, beta = 0 this is P1's form term by term; for
another lapse it is the normal-observer form, the same choice the code made at levels 0
and 1 (the background proper time runs at alpha_b). [VERIFIED in the review as the right
reading: P1:237 sets alpha_b = 1 where phidot_b is defined, P1:485 lists Pi_b as the
background input, and with a uniform lapse alpha_b(t) the printed system is eq. (Req) in
proper time only if phidot_b = dphi_b/dtau; read as d_0 phi_b it would add the friction
2 dln alpha_b/dtau at zeroth order. With alpha = 1, beta = 0, the gauge of P1 and of every
run of Track E, the two readings are the same number in every cell.] The shift sign of P1's BSSN appendix
is opposite to its ADM one (Track E `EQUATIONS.md` conventions); in the code's sign the
equations are

    d_t R    = beta^i d_i R    + alpha Pi_R / Z
    d_t Pi_R = beta^i d_i Pi_R + alpha (K Pi_R + Z psi^-4 gt^ij d_i d_j R)

with the stencils of the field: sixth-order centred differences at nghost = 4 (`Dxx`,
`Dxy`), the advective stencil `Lx` along the shift, and the field's Kreiss-Oliger term
(`<scalar_field> diss`). d_i d^i of P1 is read as gamma^ij d_i d_j R = psi^-4 gt^ij d_i d_j R
(partial derivatives, no Christoffel term) [JUDGEMENT, kept by the review]. Three readings
exist: `flat`, psi^-4 delta^ij d_i d_j R (only the quantities P1 names as promoted: phi_b,
K_b, alpha_b, beta_b at P1:323, X_b at P1:487); `metric`, the default; `covariant`,
D^i D_i R. At the order P1 derives (first; P1:496, 790) the three are one equation. They
differ by a first-order metric perturbation times a derivative of R, which is the order of
level 2 itself, where P1 gives a heuristic (P1:323) and no derivation: "of second order"
is true of the difference and of all of level 2, and decides nothing. What decides the
default: P1 prints partial derivatives in this equation and covariant ones in the field
equation on the same page (P1:224, 291-292), so `covariant` is not the print; `metric`
and `covariant` share the principal part, the light cone of the evolved metric, where
`flat` has the cone of the conformally flat metric. What the others change is measured
(`noise_level2_laplacian`, section 12, R2): 0.20 per cent (covariant) and 0.27 per cent
(flat) of the level-2 effect in the slow-roll case, because the metric and K carry
perturbations of order eps1 R while Z = 9 Pi^2/K^2 carries 2 delta Pi/Pi of order R: level
2 is, in practice, the local Pi^2.

Coefficients:

| level | alpha | K | Z | psi^-4 gt^ij | shift |
|---|---|---|---|---|---|
| 0, mesh | box mean of the lapse | -3 H of the lockstep (H from the Friedmann constraint; `evolved`: K_b itself) | Pi_b^2/H^2 of the lockstep | a^-2 delta^ij, a of the lockstep (exp(ln a); `evolved`: chi_b^(2/p)) | none |
| 1, mesh | box mean | <K> | <Pi>^2/H^2, H = -<K>/3 | a^-2 delta^ij, a = <chi>^(2/p) | none |
| 2 | local | local Khat + 2 Theta | local 9 Pi^2/K^2 | local | local |

Storage: R and Pi_R are components 2 and 3 of the field's own arrays `u0, u1, u_rhs`
(`nvar_sf = 4` instead of 2). They therefore take part in the driver's stages exactly as
phi and Pi: the low-storage update (`CopyU`, `ExpRKUpdate`), the ghost exchange, the
restart file (u0 is written whole) and the start-up exchange. Their right-hand side is a
separate kernel (`NoiseMeshRHS`, new file `scalar_field_noise_mesh.cpp`), called after the
field's right-hand side in the same task; it writes components 2 and 3 only, with its own
dissipation term, so the field's kernel and its dissipation loop are untouched.

Restrictions (fatal at start): uniform mesh (no static refinement: the projection
assumes one cell volume), `noise = mukhanov_sasaki`, a single rank (as the field already).

## 4. Initialisation at t*

From the existing synthesis with the shell factors of the mode file and W = 1 (the field
is the full mode function, not the coarse-grained one; Track E request item 1):

    R(t*, x)  = L^-3/2 sum 2 Re[R_q(t*) alpha_n e^(ik.x)]
    V(t*, x)  = L^-3/2 sum 2 Re[dR_q/dtau(t*) alpha_n e^(ik.x)]
    Pi_R      = Z V        (Z of the level: local at level 2)

done in `Startup` (after `NoiseSetup`; with `id = stochastic` after the perturbed slice
of `InitialSlice`, so the local Z is that of the slice), followed by one ghost exchange of
the field's arrays. On a restart R and Pi_R come from the restart file.

## 5. Projection onto the mode set (the adjoint of the synthesis)

At each stage, of the stage's state:

    c_R(n) = N^-3 sum_cells R(x) e^(-i k_n.(x - x0)),   c_V(n) = the same of V = Pi_R/Z,

with the same tables cos, sin of 2 pi n (g + 1/2)/N as the synthesis, as three
one-dimensional sums in the opposite order (over n_x for every row, over n_y for every
pair (n_x, n_y), over n_z for every mode; at level 2 V is formed once per call in a work
array of one value per cell, review), MeshBlock by MeshBlock, each mode accumulated
by one thread in a fixed order (repeatable bit for bit at a fixed decomposition, on the
card as on processors). For a field synthesized from coefficients c_m of the mode set
(2 n_max < N) the projection returns c_n exactly (discrete orthogonality), so at t* the
projected coefficients are L^-3/2 R_q alpha_n (test T1b). Same normalisation as the
synthesis: the synthesis of the projected coefficients reproduces the band-limited part.

## 6. The noise from the projected coefficients

Per mode, exactly the existing S_R with the per-mode coefficients in place of R_q alpha_n:

    d(n) = c_R W'' + (2 c_V + (3 - eps2) H c_R) W'

and the fields I_R, T_ij by the existing synthesis with d(n) as the complex coefficient of
mode n (the amplitude alpha_n is already inside c_R, c_V). Kick factors, projector, keys of
the draw: unchanged. Window, its derivatives, H, eps1, eps2 of the kicks: uniform, from the
background (they multiply Fourier coefficients).

Which background the window uses at level 2 P1 does not state (Track E request item 2):
P1:783 defines the levels for "the coefficients appearing in" the mode equation and for
nothing else. Choice: the box means (as level 1), so that level 2 is level 1 plus the
local coefficients of the mode equation, and a homogeneous slice gives level 1 to rounding
[JUDGEMENT, kept by the review]; `noise_level2_background = friedmann` takes the Friedmann
lockstep instead. Measured (section 12, R3): the choice changes the projected coefficients
by 2.3e-8, 1.6e-4 of the level-2 effect.

A third choice, not named before the review: the kick factors alpha_b Pi_b/H and
alpha_b eps1 multiply the real-space fields I_R and T_ij and could be local at level 2
(the window and the friction term multiply Fourier coefficients and cannot). They are
uniform, from the background of the window [JUDGEMENT]: P1's levels do not cover them.
Local factors would add (delta Pi/Pi) I_R, of the order of the level-2 effect; not
implemented.

## 6a. The lockstep background and `noise_background_eq` (review)

The background of level 0 (and the record of the Friedmann background in every history
file) is the lockstep data (t, phi_b, Pi_b, ln a) with H from the Friedmann constraint,
H^2 = (8 pi/3)(Pi_b^2/2 + V): `constraint`, the released form. `evolved` adds chi_b and K_b
(two values at the end of the lockstep vector, after the mode functions) and integrates the
homogeneous universe in the variables and with the equations of the mesh,

    d_t phi_b = alpha Pi_b,                 d_t Pi_b = alpha (K_b Pi_b - V'),
    d_t chi_b = -(p/6) alpha chi_b K_b,     d_t K_b = alpha (K_b^2/3 + 4 pi (2 Pi_b^2 - 2 V)),

with H = -K_b/3 and a = chi_b^(2/p), the arithmetic of level 1 on the box means (p =
chi_psi_power; ln a is still integrated, as a record). Initial values: the box means, or
with `id = stochastic` chi_b = 1 and K_b = -sqrt(24 pi (Pi_b^2/2 + V)), the problem
generator's own expression. The `.modes` record gets one more header line (chi_b, K_b);
the restart file holds the two values with the lockstep data. Why: with `constraint`,
level 0 and level 1 are two fourth-order integrations of one background and differ by
their truncation errors (5.7e-5 in the mode coefficients at 32^3 and Courant 0.25,
falling by 16 per halving of the step; 7.0e-6 at 256^3), which is what a comparison
"level 1 against level 0" then shows; with `evolved` they agree to 8e-12 on a homogeneous
mesh (section 12, F1, R8, R11). P1 reads (phi_b, Pi_b, K_b, X_b) as its background
(P1:485) and evolves level 0 "with the same initial conditions and numerical scheme"
(P1:785): `evolved` is the reading of that sentence [JUDGEMENT].

The per-shell mode functions of the lockstep record are still integrated (continuum k^2):
they are the linear reference written into every `.modes` file, and the comparison of the
projected coefficients with them is test T3.

## 7. Memory and cost at 256^3 (nmax2 = 4096: 549 k modes, 65 rows in n_x, about 6.4 k pairs)

| item | size |
|---|---|
| R, Pi_R in u0, u1, u_rhs (264^3 cells with ghosts) | 6 x 147 MB = 0.88 GB |
| projection work arrays (2 fields: rows 2 x 65 x 256^2, pairs 2 x 6.4 k x 256, modes 2 x 549 k; complex) | 0.21 GB |
| V = Pi_R/Z of the stage, level 2 only (256^3 cells; review) | 0.13 GB |
| boundary buffers | +2 of the field's variables |

Measured on one A100 at 256^3 with the executable of 6ca93cba (Track E's ablation runs,
throughput of the whole run with its dumps, from the chain logs): level 0 with the shells
1.27e7 zone-cycles/s (P256v6, E-20261121-202935-31520bc: 0.509 card-hours for 1386
cycles), level 0 on the mesh 1.127e7 (AL0S), level 1 on the mesh 1.123e7 (AL1S), level 2
6.91e6 (AL2S): the mesh path costs 13 per cent of a cycle and level 2 a further 63 per
cent, not the 5 to 10 per cent this section estimated. Cause by reading: the first sum
of the projection recomputed V = Pi_R K^2/(9 Pi^2) for each of the 65 rows from four
arrays (1.1e9 divisions and 35 GB of reads per stage against 16.8e6 and 0.5 GB when V is
formed once). The review forms V once per stage; the outputs are the same bytes on
processors (R1). The cost on the card with that change is NOT measured: the card job of
the review (`analysis/noise_level2/card_review.list`: 60 cycles at 256^3, level 2 and
level 0 on the mesh; prediction: ratio at most 1.18, was 1.63) waits for the queue.
On processors the difference never showed (64^3, six threads: 1.03 and 0.99).

## 8. Tests (predictions in the journal before they run)

- T1 homogeneous slice: (a) projected coefficients at t* = L^-3/2 R_q alpha_n of the mode
  file to rounding; (b) kicks off: level 2 against level 1 with `noise_mode_eq = mesh`,
  projected coefficients equal to rounding (the local values are the means).
- T2 32^3, nmax2 = 64 (the slow-roll input): R^NR against the linear reference per mode
  (threshold 0.02 of Track E's A2), and the split under the sign of the amplitude
  (`noise_mode_scale = +-1`): level 2 minus level 1 (mesh) even in the sign.
- T3 mesh R against the per-shell mode functions in the linear regime (kicks off): ratio
  of the stencil symbol of the Laplacian to k^2, measured per mode, and the agreement
  with a reference integrated with the stencil symbol.
- T4 byte regression against core-v0.6 with the option absent.
- T5 card smoke runs at 64^3, slow-roll and inflection inputs, levels 0 and 2, timing.
- T6 non-finite guard: a background with Pi = 0 at level 2 (Z = 0) must stop with exit
  status 3.
- Review (journal entries 6 to 15; scripts in `analysis/noise_level2/`): R0 the tests
  above again (`cpu_tests.py`, `bytecmp.py`); R1 the reviewed source against 6ca93cba,
  byte for byte; R2 readings of the Laplacian, R3 background of the window, R4 a lapse
  that is not 1 (`review_tests.py`); R5 card (`card_review.list`, `card_review.py`); R6
  threaded build before and after (`omp_identity.py`); R7 distance of the local Z from
  zero in Track E's level-2 runs (`pi_range.py`); R8 level 1 against level 0 on the mesh
  against the time step (`level01_dt.py`); R9 Track E's per-mode records at 256^3
  (`ablation_modes.py`); R10 byte regression against core-v0.6; R11 the evolved
  background (`level0_evolved.py`); the example input (`example_check.py`).

## 9. Results of the implementation (2026-11-22; journal entries 1 to 5; repeated in the review, section 12)

Executables of these results: source commit 6ca93cba, since 2026-11-24 13:18 PST in
`scratch/core/exe/core_noise-level2_6ca93cba/` (READY there; until then in
`core_noise-level2/`, which now holds the reviewed set of 64f150ec, section 12).
Runs: tests core-20261123-025040-384fbdd (32^3, nmax2 = 64, slow-roll input, 3.14
e-folds), analysis and figures core-20261123-030623-7676c1f (`fig_t1t3.png`,
`fig_t2.png`), byte regressions core-20261123-024646-553eefa and
core-20261123-025738-35c2552, processor timing core-20261123-030705-6b6a4bd.

| Test | Result | Verdict |
|---|---|---|
| T1a projection at t* against the mode file | 1.1e-14 (R), 6.9e-15 (dR/dtau) | as predicted (< 1e-12) |
| T1b homogeneous, kicks off: level 2 against level 1 on the mesh | 3.7e-12 | predicted < 1e-12; the box mean of 32768 equal values differs from the cell value by up to 8.9e-13 (K) and 3.4e-13 (Pi) in the same run: level 2 = level 1 to the rounding of the box mean |
| T1c homogeneous, kicks on | 9.0e-4 max (1.1e-4 rms) at amplitude 1, 9.0e-7 (1.1e-7) at 1e-3 | second order exactly (ratio 1.000e-3); size ten times the guess |
| T2 R^NR against W R alpha (continuum), level 2 | 1.2e-2 for \|n\|^2 <= 48, 7.2e-2 at the cut | below the cut within Track E's 0.02; the cut modes carry the stencil |
| T2 R^NR against W c_R of the run's own mesh R | 1.0e-4 (level 2), 1.3e-5 (level 1 on the mesh); level 0 against its shells 2.8e-3 | the noise pipeline is exact to second order |
| T2 sign split of phi_L2 - phi_L1mesh | even part rms 3.0e-11, odd part 3.1e-15 (delta phi rms 5.6e-7) | level 2 adds an even part only |
| T3 symbol/k^2 at the cut (axis modes \|n\|^2 = 64, sixth order) | 0.98169: 1.83 per cent in k^2 | Track E's 2.7 per cent is the leading term (k dx)^6/560 at k dx = pi/2 (`SETUP_AUDIT.md`:32 of track/E-stoch-inf) |
| T3 mesh R against the shells, t = 3.2 | 7.1 per cent (cut), 1.18 per cent (\|n\|^2 <= 48) | equal to the stencil ODE against the continuum ODE mode by mode: double ratio 2.6e-5 |
| T4 byte regression, option absent, against core-v0.6 | scalar-field cases and examples with restart: every file identical; twelve release set-ups: 75 of 75 | no change of behaviour |
| T6 guard (Pi = 0 at level 2) | warning, guard stop at cycle 1, exit status 3 | as predicted |
| restart (level 2, cycle 10 to 20) | dump, .modes, .rmodes identical | exact |
| inflection case through USR (32^3, to t = 10.5) | both levels finite; R grows by 5600; level 2 against level 1 on the mesh 1.9e-3 rms (1.45e-2 max) at the end | run core-20261123-032120-3d5b69f |
| T5 card smoke at 64^3 | run by Track E as T5SMK with 6ca93cba (E-20261123-035724-b661081, check E-20261123-090718-6203c87): PASS; wall per cycle level 2 / level 0 = 1.16 (slow roll), 1.14 (inflection) | passed; at 256^3 the ratio is 1.63 against level 0 on the mesh (section 7) |
| T5 on processors (threaded build, 64^3, 30 cycles, 6 threads) | all finite; wall per cycle level 2 / level 0 = 1.027 (SR), 0.992 (USR) | the extra cost is within the scatter of a shared machine (predicted +5 to +20 per cent) |

What the results mean for the ablation of P1 Fig. 9: our released levels 0 and 1 (shells,
continuum k^2) differ from level 2 at FIRST order by the stencil (up to 7 per cent per
mode at the cut, 32^3 and 256^3 alike since k_max dx = pi/2 in both), which would swamp
the 1e-4 effect of P1:520. Compare level 2 with levels 0 and 1 on the mesh
(`noise_mode_eq = mesh`): those differ from level 2 at second order only (T1c, T2 split).

## 10. Not done, open (state after the review)

- The card executable of the reviewed source has not run on a card: job R5 (64^3 level-2
  decks against Track E's smoke runs of 6ca93cba, byte for byte; cost of a cycle at
  256^3) is in the shared card queue as q0035 (label nl2-review-R5, priority 2, added
  2026-11-24 13:19 PST, with the published `core_noise-level2/athena_gpu`). The card
  executable of 6ca93cba passed Track E's smoke check and made the six ablation runs.
- Level 2 with a shift, and with a lapse that varies in space: not tested (the kernel
  uses the advective stencil of the field, which is tested with a uniform shift; a lapse
  that depends on time is tested, R4).
- The guard stops a level-2 run with a zero of Pi only through the kicks; with every
  kick off the mesh R is a passive record and a non-finite value is reported at the next
  dump, not stopped. (<z4c_guard> tests the spacetime fields only.)
- Kick factors local at level 2: not implemented (section 6).
- Not supported: static refinement, several ranks (the field already refuses ranks),
  the power model.
- The projection reads every cell once per row n_x (65 at 256^3) for both fields at
  every level; one pass over the cells with the rows in an inner loop would cut the
  memory traffic further. Not done: the mesh path costs 13 per cent of a cycle at 256^3.

## 11. Lines of shared files touched (for the merge)

`scalar_field.hpp` (new members after `SF_names`, in `SfNoiseOptions` (`bg_level`,
`mesh_r`, `rmodes_dump`, `bg_evolved`, `lap_kind`), and a block after `NoiseWriteState`);
`scalar_field.cpp` constructor (`nvar_sf` before the allocation, the allocations and
`InitializeBuffers`), `InitRecv`, `CopyU` and `ExpRKUpdate` (`nvar = nvar_sf`), `CalcRHS_`
(one call `NoiseMeshRHS`); `scalar_field_io.cpp` `Startup` (five lines after
`NoiseSetup`); `scalar_field_noise.cpp` `NoiseInit` (levels, the new options, the length
of the lockstep vector), `NoiseSetup` (one call; two initial values; the upper bound of
the loop that scales the mode functions), `NoiseBackground` (`bg_level`; a branch for the
evolved background), `NoiseModeRHS` (W', W'' per shell; a branch for the evolved
background), `NoiseSynthesize` (per-mode branch of the sum over n_z), `NoiseStage`,
`NoiseFieldsOfState`, `NoiseWriteState` (one call each; one header line with the evolved
background); `scalar_field_slice.cpp` `InitialSlice` (seven lines after `y0[3] = 0.0`);
`CMakeLists.txt` (one file). Everything else is in the new file
`scalar_field_noise_mesh.cpp`. New input: `problems/scalar/sr_stochastic_l2.athinput`.

## 12. Review on Fable (2026-11-24; journal entries 6 to 15)

First line of the report: RESULTS UNCHANGED: the six ablation runs made with 6ca93cba
stand. No defect was found in what those runs computed; the reviewed source gives the
bytes of 6ca93cba on the fifteen processor tests (R1). What the review changes is cost,
two options, and how two of the three curves of the ablation are to be read (F1).

Verdicts, item by item (V = verified by derivation or by reading the source, T = tested):

| Item | Verdict |
|---|---|
| Well-posed form of the equation of R and its momentum | V. With Z = 9 phidot_b^2/K_b^2 = 2 eps1 Mpl^2 (P1:171), P1:316-317 at alpha_b = 1, beta = 0 is d(Z dR/dt)/dt = -3 H Z dR/dt + Z a^-2 lap R, i.e. eq. (Req) of P1:183 with Z'/Z = -eps2 H. The code's pair is that system with the code's sign of the shift: a wave equation on the light cone of the local metric, Z outside the derivative as printed |
| Local coefficients of level 2 | V, T. Local alpha, beta, K = Khat + 2 Theta, Pi, psi^-4 gt^ij, in the right-hand side and in V = Pi_R/Z of the projection; on a homogeneous slice level 2 is level 1 to the rounding of the box means (3.7e-12 with alpha = 1, 8e-12 with alpha = a) |
| phidot_b read as Pi | V: the right reading (section 3). The other reading changes nothing at alpha = 1, beta = 0 and is wrong at zeroth order for any other lapse |
| Laplacian read as psi^-4 gt^ij d_i d_j R | Judgement kept (section 3). T: covariant changes the level-2 effect by 2.0e-3 of itself, flat by 2.7e-3 (R2); all three second order |
| Background of the window at level 2 | Judgement kept. T: Friedmann against means changes the coefficients by 1.6e-4 of the level-2 effect (R3) |
| Kick factors at level 2 | Third judgement, named (section 6); uniform |
| Projection = adjoint of the synthesis | V, T (1.1e-14 at t*) |
| Stage coefficients of the low-storage RK4 | V: R, Pi_R are components of u0, u1, u_rhs and take `CopyU`, `ExpRKUpdate` with the field; the lockstep data use the same gam0, gam1, beta, delta; the projection of a stage reads the state of that stage before the spacetime is advanced |
| Restart | V, T (byte-identical; also with the evolved background). A restart file without the mesh fields is refused by the extent check |
| Ghost exchange, boundaries | V: the variable count comes from the array; the sources need periodic faces; `NoiseMeshExchange` is the driver's sequence |
| Non-finite guard | V, T with a kick on (exit status 3 after the cycle). Gap with every kick off (section 10). Track E's level-2 runs stay far from Pi = 0: largest abs(Pi/<Pi> - 1) over the cells 8.9e-5 (slow roll) and 6.4e-2 (inflection, at the end) (R7) |
| Card: captures, races, copies | V by reading: no kernel captures `this`; one writer per (field, mode); host mirrors copied. The card executable of 6ca93cba passed Track E's smoke check; that of the reviewed source has not run (R5 pending) |
| Cost | DEFECT, fixed: level 2 cost +63 per cent of a cycle at 256^3 (section 7); V is now formed once per stage. Same bytes on processors (R1); card timing pending |
| A lapse that is not 1 | T (R4): alpha = a to 6.4, mesh against shells at equal ln a as with geodesic slicing (6.71e-2 / 6.71e-2 at the cut, 1.03e-2 / 1.03e-2 below) |

Finding F1: level 1 against level 0 is a difference of two time integrations. With the
released lockstep (H from the Friedmann constraint, a from ln a) level 0 on the mesh and
level 1 on the mesh differ by 5.7e-5 in the mode coefficients at 32^3 (7.9e-5 at the
cut), the same with and without perturbations and kicks (zeroth order), and the
difference falls by 16.9, 16.4, 16.0, 15.9 per halving of the step (R8): the truncation
errors of two fourth-order schemes for one background. At 256^3 (Track E's runs, R9) it
is 7.0e-6 in the coefficients (1.3e-8 for |n| < 8 rising to 8.9e-6 for |n| >= 48), almost
all of it phase: in the shell power of the mesh R it is 3.5e-7 rms, one sign, where
level 2 against level 1 scatters about zero with 3.4e-5 rms over the shells (2.3e-5 to
5.8e-5 by band; per mode 2.2e-4). So in Track E's figure the level-2 curve is the local
backreaction and is not touched; the level-1 curve is the time-integration difference,
not a backreaction. With `noise_background_eq = evolved` level 0 equals level 1 to 8e-12
on a homogeneous mesh, and to 7e-12 with the perturbations and kicks of the slow-roll
case (R11): the backreaction on the box means is below the rounding of the means there.

Review tests (processors, 32^3, nmax2 = 64 unless said; run ids in the journal):

| Test | Result | Verdict |
|---|---|---|
| R0 the fifteen runs of section 8 again, executable of 6ca93cba | 366 of 366 files identical to the recorded run | the tests repeat |
| R1 reviewed source (V once, options not selected) against R0 | 366 of 366 files identical | as predicted |
| R2 Laplacian: covariant, flat against metric | 2.85e-7, 3.93e-7 in the coefficients; level-2 effect 1.447e-4; amplitude 1e-2: ratios 1.0002e-2, 1.0000e-2 | as predicted (1e-3 to 1e-1 of the effect), at the low end |
| R3 window at level 2: Friedmann against means | 2.34e-8 | as predicted (below 1e-2 of the effect); the comparison with "level 1 against level 0" failed and led to F1 |
| R4 lapse = a, homogeneous slice, kicks off | level 2 against level 1: 8.1e-12 at most for R (8.0e-12 at the end), 6.6e-12 at most for the rms of n.d R; mesh against shells as with geodesic slicing at equal ln a | as predicted |
| R6 threaded build, old against new, level 2, 64^3, three threads, 12 cycles | 22 of 22 files identical (sr64_l2, usr64_l2: dumps, .modes, .rmodes, .hst; run core-20261124-211548-60896c5, 2026-11-24) | as predicted |
| R7 abs(Pi/<Pi> - 1) in AL2S, AL2U (256^3) | 8.9e-5, 6.4e-2 at most | as predicted |
| R8 level 1 against level 0 on the mesh, Courant 0.25, 0.125, 0.0625 | 5.3e-5, 3.3e-6, 2.1e-7 at t = 0.98 | fourth order, as predicted |
| R9 the same pair in Track E's runs at 256^3 | 7.0e-6 per mode, 3.5e-7 in shell power | size predictions failed twice (journal entries 12, 13); the finding holds, smaller |
| R10 byte regression against core-v0.6, options absent | final source 64f150ec: the ten wave-1 cases and the three stochastic examples with their restarts, every file identical (2 restart files with the masked header bytes); the release driver 75 of 75 items, twelve set-ups, PASS. The same for the intermediate source 746869ef | as predicted |
| R11 evolved background: level 0 against level 1 | 7.6e-12 homogeneous, 6.5e-12 perturbed with kicks; restart identical | as predicted for (a), (c); (b) on the rounding floor |
| R1f final source 64f150ec against 6ca93cba on the fifteen runs | 366 of 366 files identical (runs core-20261124-143147-2ff64b9 against core-20261124-130250-0a4a7cb, comparison core-20261124-211517-b90ce89, 2026-11-24) | as predicted |
| Example `problems/scalar/sr_stochastic_l2.athinput` | runs; 8 of 8 files identical to `sr_stochastic.athinput` with `noise_level = 2` | as predicted |
| R5 card: identity at 64^3, cost at 256^3 | NOT RUN: in the shared queue as q0035 (2026-11-24 13:19 PST); the command that reads it is in journal entry 17 | pending |

What Track E's six runs show, and what could be added: (i) level 2 against level 1 on
the mesh is the local backreaction, clean; (ii) level 2 against level 0 on the mesh is
the same curve to 1 per cent in shell power at 256^3; (iii) level 1 against level 0 on
the mesh is F1; a level-1 curve that shows a backreaction needs level 0 with
`noise_background_eq = evolved` (two more runs, AL0S and AL0U with that line, about 0.6
and 0.75 card-hours at the cost of the old runs); in slow roll the prediction is "equal
to level 1 to rounding"; (iv) AL2S ended at cycle 1227 of 1386 because of the cost found
in section 7; Track E continued it from its restart file with the same executable
(E-20261124-131359-49afe29, registered completed; its outcome is Track E's).

Verdict for release v0.7 (state 2026-11-24 13:25 PST, after the closing session of batch
R3): fit, on two conditions that remain. (1) The card job R5 has run and passed: the
reviewed card executable has not yet run a step on a card (queue entry q0035). (2) At
the merge the options enter the changelog and `coord/INTERFACES/` (this file), with the
limits of section 10. The two closing checks that the pause of 2026-11-24 06:32 PST cut
are done and passed: R1f (the final source gives the bytes of 6ca93cba on the fifteen
processor tests, 366 of 366 files) and R6 (threaded build, 22 of 22 files). Nothing else
is open in the source: byte regression against core-v0.6 with the options absent passes
on processors for the final source; the seven source files touch shared code only at the
lines of section 11.

Executables: published 2026-11-24 13:18 PST. `scratch/core/exe/core_noise-level2/` holds
the reviewed set of 64f150ec (athena_cpu 0222e5f0.., athena_gpu d7069a4e..,
athena_cpu_omp 31210622..; COMMIT, SHA256SUMS, READY with TESTED and NOT TESTED). The set
of 6ca93cba is unchanged in `scratch/core/exe/core_noise-level2_6ca93cba/` (its READY
names the nine Track E manifests that used it); files were replaced by renaming full
copies, so no running process lost its executable.
