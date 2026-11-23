# Stochastic backreaction of level 2: the curvature perturbation as a mesh field

Owner: core, branch `core/noise-level2` (decision 0029 item 2). Written on Opus because the
weekly window does not hold a Fable session; it enters a release only after a review of
the diff on Fable. Request: Track E, `repro/scope/outbox_draft/core_noise_level2.md`
(branch `track/E-stoch-inf`). Paper: P1 = arXiv:2512.14649 v2,
`kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`, lines `P1:<n>`. Journal of the tests:
`tracks/core/JOURNAL-noise-level2.md`. Results: section 9 (filled after the tests).

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

## 2. The option

    <scalar_field>
    noise_level   = 2                 # 0, 1 as before; 2 = local coefficients (new)
    noise_mode_eq = mesh              # shells (default for 0, 1) | mesh (default and only
                                      # choice for 2); read only if present
    noise_level2_background = means   # means (default) | friedmann; read only if present
    noise_rmodes_dump = false         # per-mode record next to each dump; only if present

`noise_mode_eq = mesh` with level 0 or 1 is P1's own form of those levels (the mesh field
with the uniform coefficients of the level); with it, the ablation of P1 Fig. 9 compares
runs that differ by the coefficients only. Without these lines nothing changes: the
number of evolved variables, the task list, every kernel and every output stay as in
core-v0.6 (byte regression, section 8).

## 3. The two mesh fields and their equations

Variables of the code: G = c = 1, K = -3H, Pi = n.d phi (normal derivative), the shift
enters as d_t = beta^i d_i + alpha n.d (`scalar_field.hpp`). The paper's phidot_b is the
proper-time derivative of the background field (P1 sets alpha_b = 1, P1:237, 483), so in
the code's variables 9 phidot_b^2/K_b^2 is

    Z = 9 Pi^2/K^2  ( = Pi^2/H^2 = eps1/(4 pi) ),

and Pi_R = Z n.d R. [JUDGEMENT] For alpha = 1, beta = 0 this is P1's form term by term; for
another lapse it is the normal-observer form, the same choice the code made at levels 0
and 1 (the background proper time runs at alpha_b). The shift sign of P1's BSSN appendix
is opposite to its ADM one (Track E `EQUATIONS.md` conventions); in the code's sign the
equations are

    d_t R    = beta^i d_i R    + alpha Pi_R / Z
    d_t Pi_R = beta^i d_i Pi_R + alpha (K Pi_R + Z psi^-4 gt^ij d_i d_j R)

with the stencils of the field: sixth-order centred differences at nghost = 4 (`Dxx`,
`Dxy`), the advective stencil `Lx` along the shift, and the field's Kreiss-Oliger term
(`<scalar_field> diss`). d_i d^i of P1 is read as gamma^ij d_i d_j R = psi^-4 gt^ij d_i d_j R
(partial derivatives, no Christoffel term: P1 prints partial derivatives; the difference
from D_i D^i R is of second order) [JUDGEMENT].

Coefficients:

| level | alpha | K | Z | psi^-4 gt^ij | shift |
|---|---|---|---|---|---|
| 0, mesh | box mean of the lapse | -3 H of the Friedmann lockstep | Pi_b^2/H^2 of the lockstep | a^-2 delta^ij, a of the lockstep | none |
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
pair (n_x, n_y), over n_z for every mode), MeshBlock by MeshBlock, each mode accumulated
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

Which background the window uses at level 2 P1 does not state (Track E request item 2;
[TO VERIFY] from P1's text only). Choice: the box means (as level 1), so that level 2 is
level 1 plus the local coefficients of the mode equation, and a homogeneous slice gives
level 1 to rounding [JUDGEMENT]; `noise_level2_background = friedmann` takes the
Friedmann lockstep instead (level 0 plus local coefficients).

The per-shell mode functions of the lockstep record are still integrated (continuum k^2):
they are the linear reference written into every `.modes` file, and the comparison of the
projected coefficients with them is test T3.

## 7. Memory and cost at 256^3 (nmax2 = 4096: 549 k modes, 65 rows in n_x, about 6.4 k pairs)

| item | size |
|---|---|
| R, Pi_R in u0, u1, u_rhs (264^3 cells with ghosts) | 6 x 147 MB = 0.88 GB |
| projection work arrays (2 fields: rows 2 x 65 x 256^2, pairs 2 x 6.4 k x 256, modes 2 x 549 k; complex) | 0.21 GB |
| boundary buffers | +2 of the field's variables |

Operations per stage: the projection costs about one third of the six-field synthesis
(the sum over n_x dominates: 2 fields instead of 6); the right-hand side of R and Pi_R is
small against the Z4c right-hand side. Expected: +5 to +10 per cent of the time of a step
at 256^3 against level 0 [TO VERIFY by the card smoke runs at 64^3, section 9].

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

## 9. Results (2026-11-22; journal entries 1 to 4)

Executables: `scratch/core/exe/core_noise-level2/` (source commit 6ca93cba; READY there).
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
| T5 card smoke at 64^3 | NOT RUN: two core card jobs queued during the session (decision rule) | pending; the list is `analysis/noise_level2/card_t5.list` |
| T5 on processors (threaded build, 64^3, 30 cycles, 6 threads) | all finite; wall per cycle level 2 / level 0 = 1.027 (SR), 0.992 (USR) | the extra cost is within the scatter of a shared machine (predicted +5 to +20 per cent) |

What the results mean for the ablation of P1 Fig. 9: our released levels 0 and 1 (shells,
continuum k^2) differ from level 2 at FIRST order by the stencil (up to 7 per cent per
mode at the cut, 32^3 and 256^3 alike since k_max dx = pi/2 in both), which would swamp
the 1e-4 effect of P1:520. Compare level 2 with levels 0 and 1 on the mesh
(`noise_mode_eq = mesh`): those differ from level 2 at second order only (T1c, T2 split).

## 10. Not done, open

- Card smoke T5 on the card (both scenarios, 64^3, levels 0 and 2): not run in this
  session (queue rule); the card executable is built from the tested source but has not
  run a single step on a card.
- Byte equality card against processors is not expected (card runs with sums in another
  order); the processor projection is deterministic for a fixed decomposition.
- Review on Fable of the diff (decision 0029 item 2), in particular the choices labelled
  [JUDGEMENT] in sections 3 and 6.
- Cost at 256^3 on a card: estimated in section 7, not measured.
- Not supported: static refinement, several ranks (the field already refuses ranks),
  the power model.
- Possible optimisation for the review: at level 2 the projection recomputes
  V = Pi_R K^2/(9 Pi^2) in every row of the sum over n_x (65 times per cell at 256^3)
  and reads four arrays for it; a work array of V filled once per stage would halve the
  memory traffic of the projection. Not done, to keep the change small.

## 11. Lines of shared files touched (for the merge)

`scalar_field.hpp` (new members after `SF_names`, `SfNoiseOptions`, and a block after
`NoiseWriteState`); `scalar_field.cpp` constructor (`nvar_sf` before the allocation, the
allocations and `InitializeBuffers`), `InitRecv`, `CopyU` and `ExpRKUpdate` (`nvar =
nvar_sf`), `CalcRHS_` (one call `NoiseMeshRHS`); `scalar_field_io.cpp` `Startup` (five
lines after `NoiseSetup`); `scalar_field_noise.cpp` `NoiseInit` (levels and the new
options), `NoiseSetup` (one call), `NoiseBackground` (`bg_level`), `NoiseModeRHS` (W', W''
per shell), `NoiseSynthesize` (per-mode branch of the sum over n_z), `NoiseStage`,
`NoiseFieldsOfState`, `NoiseWriteState` (one call each); `CMakeLists.txt` (one file).
Everything else is in the new file `scalar_field_noise_mesh.cpp`.
