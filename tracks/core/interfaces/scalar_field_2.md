# Scalar field, second pass: initial slice at N*, constraint magnitudes, extended dumps

Status: PROPOSAL of core (branch `core/scalar-2`, 2026-11-15), an amendment to
`scalar_field.md` (release core-v0.3; sections 3, 6, 7.3, 7.4, 8, 10, 11 there). Client:
Track E (requests of 2026-11-15T14:10Z: `initial-slice-at-nstar`,
`sf-diagnostics-and-interface`, `card-build-scalar-field`, `noise-unit-test-results`).
Evidence labels as in the brief; every number carries a run id
(`tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`).
Predictions and outcomes, including the failed ones: `tracks/core/JOURNAL-scalar2.md`.
Paper keys: P1 = arXiv:2512.14649 v2 `PRD_v2.tex`, P2 = arXiv:2502.06783 v3
`main_V2PRD.tex`; SPEC = `tracks/E-stoch-inf/spec/SPEC.md` on `track/E-stoch-inf`.

## 1. What is new

| Where | What |
|---|---|
| `athenak/src/scalar_field/scalar_field_slice.cpp` (new) | `ScalarField::InitialSlice`: the perturbed initial slice of SPEC 5.3 |
| `athenak/src/scalar_field/scalar_field_diag.cpp` (new) | magnitudes [H], [M] of P1:735-745, record `<basename>.sf.con.hst`, dump layout NRSFDMP2 |
| `athenak/src/pgen/nrpic/scalar_field_tests.cpp` | `<problem> id = stochastic` |
| `python/nrpic/sf_inflation.py` (new) | reference: background in e-folds, Mukhanov-Sasaki mode functions from Bunch-Davies data, conversion to code units, mode file, twin of the slice |
| `python/nrpic/scalar_field.py` | `read_dump` reads both layouts; `read_con_history` |
| `problems/scalar/sr_stochastic.athinput`, `sr_stochastic_modes.txt` | the slow-roll case of P1 at 32^3 with every new option |
| `tracks/core/analysis/scalar2/` | case generator `make_case.py`, test drivers, card job, registrar |

Lines of files that existed before (against main at 4ebb05f), all small hooks:

| File | Lines (new numbering) | What |
|---|---|---|
| `scalar_field/scalar_field.hpp` | 167-180, 291-307 | `SfDiagOptions`; declarations and members of the two new files |
| `scalar_field/scalar_field.cpp` | 173, 377-379 | `DiagInit(pin)` in the constructor; constraint record in `Diagnostics` |
| `scalar_field/scalar_field_io.cpp` | 72-74, 240-243 | first constraint record in `Startup`; `WriteDump` hands over to `WriteDumpExtended` |
| `scalar_field/scalar_field_noise.cpp` | 180-184, 337-339, 429-431, 685-687 | `noise_mode_scale`; `NoiseSetup` returns if `InitialSlice` has done it; scale applied to the mode file; no synthesis in a stage when all kicks are off |
| `pgen/nrpic/scalar_field_tests.cpp` | 32-37, 88-89, 91-92, 196, 242-243 | `id = stochastic`: header text, kind 3, error text, background as `flrw`, call of `InitialSlice` |
| `CMakeLists.txt` | 216-217 | the two new sources |

No change outside `scalar_field/`, the problem generator and the source list: Z4c, the
task list, the driver and the output classes are untouched.

## 2. Initial slice (`<problem> pgen_name = scalar_field`, `id = stochastic`)

Background as `id = flrw`: `phi0`, `pi0` (the state at N*; "on the attractor" means that
the reference has integrated the background from the Bunch-Davies time N0 to N*, SPEC
5.1), psi = 1 (a* = 1), K = -sqrt(24 pi (Pi^2/2 + V)), alpha = 1, zero shift. On it the
linear perturbations of the coarse-grained curvature perturbation in the geodesic gauge
with chi_0 = E_0 = 0 (SPEC 5.3; P2 eq. 17 with the corrected delta Pi), in the variables
of the code (Pi_b/H is sqrt(2 eps1) Mpl of the papers, sign-safe):

    A = W R,   B = W' R + W R'                    (per mode; R, R' = dR/dtau from the mode file)
    Psi       = -eps1 H a^2 B / k2                (Bardeen potential)
    delta phi = (Pi_b/H) (A - Psi)
    delta K   = 3 eps1 H (A - Psi)                (= 12 pi Pi_b delta phi)
    delta Pi  = (Pi_b/H) B - Pi_b (eps1 + eps2/2) (A - Psi)
    chi       = chi_b (1 + 2 Psi),   gt_ij = delta_ij,   At_ij = 0,   Gamma^i = 0,   Theta = 0

with W = (1 + tanh[s ln(sigma a H/k)])/2, W' = (s/2) sech^2 H (1 - eps1), s =
`noise_sharpness`, sigma = `noise_sigma`, eps1 = 4 pi Pi_b^2/H^2, eps2 = 6 + 2 V'/(H Pi_b) -
2 eps1. Each field is L^(-3/2) sum over the hemisphere of 2 Re[T_n alpha_n e^(ik.(x - x0))]
with the mode set (`noise_nmax2`), the amplitudes alpha_n (degree of freedom 0, epoch 0,
`<job> rng_seed`) and the per-MeshBlock sums of the stochastic sources: the slice and the
sources are one realisation (NOISE_SPEC R7), bit-identical for any division into
MeshBlocks. Requires `<scalar_field> noise = mukhanov_sasaki` with its mode file
(`noise_mode_file`: rows `|n|^2 Re R Im R Re dR/dtau Im dR/dtau` at N*, in code units).
Derivation and the linearised constraints: journal, entry 1.

| Option (`<problem>`) | Default | Meaning |
|---|---|---|
| `phi0`, `pi0` | 0 | background at N* (code units) |
| `slice_window` | true | false: A = R, B = R' (all modes in, no window; with the kicks off this is the initial-value problem of P2, Track E's test L3) |
| `slice_k2` | stencil | k2 of Psi: `stencil` the symbol of the centred second differences of the root mesh (the operator of the Ricci scalar in `Z4c::ADMConstraints`), so that the discrete linearised Hamiltonian constraint vanishes to rounding; `continuum` (2 pi \|n\|/L)^2, which leaves the truncation error of the second difference, (k2_stencil - k2) Psi |
| `slice_delta_pi` | corrected | `printed`: adds Pi_b Psi to delta Pi (the printed eq. 17 of P2); negative control with the linear residual delta H = -4 eps1 H^2 Psi |

| Option (`<scalar_field>`) | Default | Meaning |
|---|---|---|
| `noise_mode_scale` | 1 | factor on the mode functions of the mode file; scales the slice and the sources together (amplitude scans; -1 is the mirrored realisation, which separates the odd and the even order of any output) |

The lockstep background of `noise_level = 0` starts from `phi0`, `pi0` exactly (not from
box means, which carry the rounding of a sum over the cells). With all three kicks off
(`noise_kick_pi = noise_kick_k = noise_kick_a = false`) no field is synthesized during
the run; the mode functions are still integrated and written next to each dump
(`.modes`), as the linear reference.

Not done: a* other than 1; an exact (non-linear) solution of the constraints (the slice
violates them at second order in the perturbation, as the data of P1 and P2 do); tensor
modes; level 2.

## 3. Constraint magnitudes and their record

`<scalar_field> con_dcycle = n` (default 0: off) writes `<basename>.sf.con.hst` every n
cycles (and at the start): box statistics, with coordinate-volume weights, of the
constraints of `Z4c::ADMConstraints` relative to the magnitudes of P1:735-745 in the units
of the code (2/Mpl^2 = 16 pi):

    [H]   = |R| + |(2/3) K^2| + |At_ij At^ij| + |16 pi E|
    [M_i] = |gt^kl Dt_k At_il| + |(3/2) gt^kl At_ik d_l chi/chi| + |(2/3) d_i K| + |8 pi S_i|
    [M]   = sqrt(sum_i [M_i]^2),      |M| = sqrt(sum_i M_i^2)   (covariant components)

Columns: time, cycle, e-folds -ln<chi>/2, <|H|/[H]>, max |H|/[H], <|H|>/<[H]>, <|M|/[M]>,
max |M|/[M], <|M|>/<[M]>, <[H]>, <[M]>, <|H|>, <|M|>, rms H, rms |M|, rms |M_bssn - M_adm|,
<phi>, <Pi>, <K>, <alpha>. P1 plots <|C|/[C]> (P1:771): columns 4 and 7. Reader:
`nrpic.scalar_field.read_con_history`.

- [JUDGEMENT] P1 prints the Christoffel part of the first term of [M_i] with a plus
  sign; the code takes the covariant divergence gt^kl (d_k At_il - Gt^m_ki At_ml -
  Gt^m_kl At_im). The two differ at second order in the perturbations.
- M_bssn is the momentum constraint assembled from the four terms above; its rms
  difference to the M_i of `Z4c::ADMConstraints` is a running check of this file.
- Where [M] = 0 (a homogeneous state) the ratio is set to 0; in a homogeneous run both
  |M| and [M] are rounding, and the ratio means nothing.
- R is recovered from H, so [H] uses the sources the constraints were evaluated with
  (`tmunu_tot` when the field is coupled). `chi_psi_power = -4` is required.
- `<basename>.sf.hst` is unchanged (its column 17 is the mean of [H]).
- The box means of both records carry the rounding of a running sum over the cells
  (6e-13 relative at 32^3 on the serial processor build).

## 4. Dumps in double precision: layout NRSFDMP2

Written instead of NRSFDMP1 when one of the four options below leaves its default; the
old layout and its reader are unchanged.

| Option (`<scalar_field>`) | Default | Adds or removes |
|---|---|---|
| `dump_metric` | false | gxx, gxy, gxz, gyy, gyz, gzz (gt_ij) and Axx ... Azz (At_ij) |
| `dump_magnitudes` | false | Hmag = [H], Mmag = [M], MBx, MBy, MBz (M_i of the BSSN form) |
| `dump_constraints` | true | H, Mx, My, Mz, E |
| `dump_noise` | true | the stochastic fields noise0, ... |

Always: phi, Pi, chi, K = Khat + 2 Theta, alpha. File: 8 bytes `NRSFDMP2`; int64 nmb, nx1,
nx2, nx3, nvar, cycle, nnoise; double time; nvar names of 16 bytes (zero padded); then
per MeshBlock int64 level, lx1, lx2, lx3; double x1min ... x3max; nvar arrays of
nx3 x nx2 x nx1 doubles (first index fastest), active cells. Track E's set (phi, Pi, chi,
gt_ij, K, At_ij, alpha) is `dump_metric = true`, `dump_constraints = false`, `dump_noise =
false`: 17 variables, 2.3 GB per dump at 256^3. `nrpic.scalar_field.read_dump` returns the
names from the file. Cadence as before (`dump_dcycle`, `dump_dt`).

## 5. Reference tools (`python/nrpic/sf_inflation.py`)

`quadratic_model`, `inflection_model` (P1:405-420; potential-position fixing P2:399-405);
`Background` (Friedmann and Klein-Gordon in e-folds from N0); `mode_functions`
(Mukhanov-Sasaki per wave number from Bunch-Davies data; [JUDGEMENT] the form of the
data is that of `tracks/E-stoch-inf/spec/ref/ms_reference.py`, the papers do not write
it); `code_case` (units of the code: G = 1, time unit 1/H*, phi/sqrt(8 pi), V/(8 pi
H*^2), R_k H*^(3/2), box 2 pi/sigma); `write_mode_file`; `slice_transfer` (twin of the
slice). `tracks/core/analysis/scalar2/make_case.py --case quadratic --nmax2 64 --out DIR`
writes the mode file and prints the options. Numbers of the quadratic case in code
units: mass = 0.1828776559, phi0 = -2.6667947899, pi0 = 0.02973004068, H*/Mpl =
9.4869151e-6, eps1* = 1.110710e-2, eps2* = -2.213315e-2 (SPEC 6: 9.48692e-6, 1.1107e-2,
-2.213e-2). The inflection case is in the tool but has not been run in the code.

## 6. What is verified

Predictions were written before the runs (`tracks/core/JOURNAL-scalar2.md`, entries 2, 3,
6, 8); outcomes in entries 4 to 9. Figures: `tracks/core/notes/scalar2_figs/`.

Executables: `.work/exe/athena_cpu_a58e95b` and `athena_gpu_a58e95b` of this worktree
(source of commit a58e95b; published copies: section 8). Case of all runs unless said
otherwise: the quadratic case of P1 in code units (section 5), box 2 pi, nmax2 = 64
(k_max/dk = 8, the convergence set-up of P1:756), seed 20261115, Courant 0.25, geodesic
slicing, `noise_level = 0`.

| Statement | Evidence |
|---|---|
| The slice equals the twin: over the 1054 modes the largest deviation of the coefficients of delta phi, delta Pi, chi - 1, delta K is 3.6e-10, 5.6e-13, 4.2e-11, 3.3e-10 of their rms (rounding of background plus perturbation); nothing outside the mode set above 4.0e-10; gt_ij = delta_ij and At_ij = 0 exactly. Without the window: 5.3e-11, 7.6e-14, 8.0e-11, 4.5e-11 | run core-20261115-154907-eb68eaa, `fig_slice.png` |
| The constraints of the slice are second order: with the mode functions scaled by s = 1, 1/2, 1/4, <\|H\|/[H]> = 2.625e-12, 6.553e-13, 1.630e-13 (factors 4.005, 4.021) and <\|M\|/[M]> = 1.462e-5, 7.310e-6, 3.655e-6 (2.0000, 1.9999; \|M\| second order, [M] first). The part of H odd in s has rms 2.7e-14 (rounding) against the largest linear term 1.59e-6; of M_i 1.06e-15 | the same run |
| Negative control `slice_delta_pi = printed`: odd part of H with rms 1.759e-8, its coefficients equal -4 eps1 H^2 Psi_n alpha_n within 6.1e-7 of their rms; <\|H\|/[H]> = 1.2003e-9, 6.001e-10, 3.001e-10 (factors 2.0000): first order, as Track E's symbolic check found | the same run |
| `slice_k2 = continuum`: odd part of H = -4 (k2_stencil - k2) Psi within 1.6e-5 for the \|n\| = 1 modes at N = 16 (relative size of the k2 error 6.39e-6) and within 0.26 percent at N = 32 (1.02e-7) | the same run |
| Background (A1 of Track E, 1e-4): box means of phi, Pi, K against the Friedmann and Klein-Gordon equations over 8.04 e-folds (172 steps at 32^3) within 6.4e-13, 4.5e-12, 3.6e-12; lockstep background within 2.6e-13, 2.3e-12; e-folds from <chi> within 5.5e-6 (Courant 0.25) and 3.3e-7 (0.125), ratio 16.6 | run core-20261115-155040-eb68eaa, `fig_evolve.png` |
| Constraint ratios in time (P1:538-541 quotes 1e-10 for H during the entry): <\|H\|/[H]> at most 4.7e-11 (N = 2.4), <\|M\|/[M]> at most 3.7e-4 (N = 2.7); both fall after the last crossing, to 3.1e-12 and 1.6e-7 at N = 8.04 | the same run |
| The constraint violation has three parts, separated with runs at s = 0, +-1/2, +-1: a uniform residual of the time integration of the background, 3.0e-11 to 3.3e-11 in H (2.5e-12 to 2.9e-12 of [H]) at Courant 0.25 and 16 times less at 0.125 (late-time floors 3.1e-12 and 1.8e-13); a part odd in s (first order, truncation of the stencils), rms ratio 2.000 between s = 1 and 1/2, up to 6.6e-10 in H at N = 2.4; a second-order part, rms ratio 4.00 +- 0.006 at eight dumps, 1.7e-11 at N = 0.44 and falling | runs core-20261115-155040-eb68eaa, core-20261115-161040-760b515, `fig_parts.png` |
| Negative control `noise_pi_sign = -1`: <\|H\|/[H]> up to 9.8e-8 (5.7e4 times the proper run in the first e-fold, odd in s), <\|M\|/[M]> = 0.16 at one e-fold and up to 0.21 | run core-20261115-155040-eb68eaa |
| The slice and the sources carry one linear solution: R^NR_n = psi_n + (H/Pi_b) delta phi_n extracted from the dumps equals L^(-3/2) W R alpha_n of the lockstep record within 1.1e-11 at t = 0 (modes with W > 1/2) and, at the later dumps to N = 3.14, within 2.7e-5 for \|n\| <= 2 (3.7e-6 after N = 2, no drift), 7.6e-5 for \|n\| <= 4 and 2.8e-3 for all 1054 modes (Track E's A2 asks 2e-2 for k <= k_max/2). With `noise_pi_sign = -1` the deviation is 2 | run core-20261115-160134-3fde433, `fig_rnr.png` |
| M_i assembled from the four BSSN terms of [M_i] equals the M_i of `Z4c::ADMConstraints` within 3.4e-4 of rms \|M\| up to t = 3.2 | run core-20261115-155040-eb68eaa |
| Division of the mesh and restart: 1, 8 and 64 MeshBlocks give bit-identical fields in the dumps at cycles 0, 10, 20 (22 fields each); a restart at cycle 10 gives a byte-identical dump at cycle 20. The box statistics of the records differ by at most 2.7e-14 between divisions | run core-20261115-155719-383321a |
| Track E's noise validation (NOISE_SPEC 9, 10; scaled base case N = 32, nmax2 = 100, 120 cycles) on the processor executable: frozen tanh and Markov Heaviside pass every test (A1 5.3e-14 and 2.4e-15; 1, 8, 64 MeshBlocks and the restart bit-identical; N = 16 against 32 3.0e-15). Markov tanh fails A1 at 9.77e-11 against Track E's reference as written and passes at 3.3e-15 when the reference forms the increment as the code does (dW = sinh(s hubble dt)/(2 cosh x1 cosh x0)); frozen then 3.7e-15. The code has formed it so since 5a6953e (release core-v0.3) | runs core-20261115-155122-eb68eaa, core-20261115-160103-3fde433 |
| Existing behaviour: 120 output files of ten scalar-field cases of wave 1 (two gauges, plane, wave, refined mesh, power sources frozen and Markov, Mukhanov-Sasaki sources with and without kicks, restart) are unchanged against the executable of release core-v0.3: 110 byte-identical, 8 mesh restart files differ inside the 36 unset header bytes, 2 in the recorded path of the restart file only. Seven relativistic and gravity set-ups (geo, boris, dep, east, os, jeans, binary) byte-identical | runs core-20261115-161240-61bb520 (files of -160549-a36abe3); core-20261115-155731-383321a to -160856-a36abe3 |
| Card against processors (one A100, executable of the same source): the slice is bit-identical (phi, Pi, chi, K, alpha, gt_ij, At_ij); after 10 and 20 steps the fields differ by at most 3.3e-14 (K), 2.5e-14 (Pi), 8.7e-15 (At_ij), 4.9e-15 (phi), the constraint fields by 3.4e-13 (H) and 1.1e-13 (M_i); box means within 6.4e-13, <\|H\|/[H]> and <\|M\|/[M]> within 1.4e-5 | card run core-20261115-155404-24c88e3 (job 4444), analysis core-20261115-163549-7be94e4, `fig_card.png` |
| Ladder N = 32, 64, 128 at nmax2 = 64 on the card: the first-order part of the constraints is a truncation error, rms of the odd part of H 6.57e-10, 1.42e-11, 2.53e-13 at t = 2.4 (orders 5.5, 5.8; of \|M\| 5.6, 5.8); the second-order part does not depend on N (even part of \|M\| equal within 1 percent). <\|H\|/[H]> and <\|M\|/[M]> at t = 2.4: 4.65e-11, 1.01e-12, 6.6e-14 and 3.0e-4, 6.5e-6, 9.0e-7 (Track E's A5: order between 4 and 6 from 32 to 64); at N = 64 and 128 they never exceed their values at t = 0 (2.6e-12, 1.46e-5) | the same card run, analysis core-20261115-163726-7be94e4, `fig_ladder.png` |
| M_bssn against M_adm on the ladder: rms difference at most 8.5e-14 (N = 32), 4.4e-15 (64), 7.3e-15 (128, rounding), at most 6.9e-3 of rms \|M\| | the same runs |
| Track E's U9 (U2 of the scaled base case on the card against the processor runs): A14 passes, 1.3e-15 (bound 1e-12). The full base case of NOISE_SPEC 9 (64^3, nmax2 = 256, 300 steps, U1 to U8) on the card: frozen tanh and Markov Heaviside pass every test (A1 9.8e-14 and 2.6e-15; 1, 8, 64 MeshBlocks and the restart at cycle 150 bit-identical on the card; N = 32 against 64 3.5e-15); Markov tanh A1 8.5e-10 against the reference as committed, 4.0e-15 against the cancellation-free one | card run core-20261115-155404-24c88e3; validations core-20261115-163855-7be94e4, core-20261115-163910-7be94e4 |
| Other paths: without window and kicks (`slice_window = false`, nmax2 = 16, 32^3) the 128 modes cross and freeze on R alpha of the lockstep record within 8.3e-4 (5.9e-6 for \|n\| <= 2); with `noise_level = 1` R^NR equals W R alpha within 2.8e-3 for all modes, 5.6e-5 for \|n\| <= 2 (two to four times the level-0 value for these) | runs core-20261115-161659-38adbb8, core-20261115-162142-3407748, `fig_rnr_nowindow.png`, `fig_rnr_level1.png` |
| Cost on one A100, zone-cycles per second (one MeshBlock, nmax2 = (N/4)^2): 128^3: 1.634e7 with the kicks off, 1.484e7 with the sources, 1.459e7 with the constraint record every step; 256^3 (548958 modes): 1.654e7, 1.393e7, 1.364e7, i.e. 1.01, 1.20, 1.23 s per step; eight MeshBlocks of 128^3: 1.30 s. Sources 10 and 19 percent, record 2 percent. One processor core, 32^3 with sources and record: 1.06e4 | card run core-20261115-155404-24c88e3; run core-20261115-155040-eb68eaa |

Failed predictions and failed runs (journal entries 4 to 11): the even part of H does
not scale as s^2 (the uniform time-integration residual dominates it; found by the
test, then predicted and confirmed with the s = 0 run and the Courant factor); the
second-order part of M changes by 1.1 percent with the printed delta Pi ("unchanged"
was too strong); the card comparison "within 1e-11 of the largest value" does not hold
for the fields that are pure perturbations (At_ij 4.4e-8 of 2e-7; the differences are
rounding of order-one quantities and the criterion should have been absolute); with
`noise_level = 1` the lowest shells deviate two to four times more than with level 0,
not "within 20 percent"; the difference M_bssn - M_adm stops falling at N = 128
(rounding). Three runs failed on defects of the test scripts (a relative path; twice
the comparison of restart files, which record the path they were started from).

## 7. Limits and open points

- The slice satisfies the constraints at first order only (as the data of P1 and P2);
  the second-order violation at t = 0 is <|H|/[H]> = 2.6e-12 for the windowed slice of the
  quadratic case and 3.9e-10 with all modes in (`slice_window = false`).
- At 32^3 with nmax2 = 64 (four cells per shortest wavelength) the constraint violation
  during the entry of the upper shells is first order in the amplitude: a truncation
  error of the stencils (the symbols of the first difference squared and of the second
  difference differ by 11 percent at k dx = pi/2). It converges at order 5.5 to 5.8;
  at N >= 64 with the same modes (k_max dx <= pi/4) the ratios stay at or below their
  initial values. The production set-up of P1 (N = 256, nmax2 = 4096) has k_max dx =
  pi/2 again, so its last shells will show the same first-order part (P1:541 reports it
  for the momentum constraint and suggests a smaller k_max).
- The uniform Hamiltonian residual of the background scales with the fourth power of
  the step; at H dt = 0.049 it is 3e-12 of [H].
- a* = 1 only; the stencil k2 and the stencil projector use the cell size of the root
  mesh; refined meshes are not tested with the slice.
- The inflection (USR) case has not been run with the slice; `noise_level = 1` has one
  run (32^3, 3 e-folds). No run beyond 128^3 with dumps; 256^3 only as a cost run of
  ten steps. No refined mesh, no second seed.
- Mode files: `make_case.py --kstart` changes the phase of each mode function (moduli
  agree to 1.6e-6), i.e. the realisation; runs compared mode by mode must share one
  mode file.
- The box means of the records are running sums: 6e-13 relative at 32^3 on the serial
  build, 2.7e-14 between divisions of the mesh.
- [M] of P1: sign of the Christoffel term as in section 3.
- Not done from Track E's requests: `rng::ModeEntity` and the wording of stream 3 and of
  rule 2 in `rng.md` (request (c) of `noise-unit-test-results`); the keys are those of
  `scalar_field.md` section 7.1 and are unchanged. The reference `noise_ref.py:transfer`
  of Track E should form the increment without cancellation (13 lines, quoted in the
  journal, entry 4) to hold A1 at 1e-11 for the Markov scheme.
- `harness/bin/nrpic-run submit` fails in this worktree (journal entry 3); runs are
  registered by hand.

## 8. Published executables (decision 0013)

`/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_gpu` and `athena_cpu`, built
from the source of commit a58e95b (the later commits of the branch change no file
under `athenak/`); files `COMMIT` (commit and checksums) and `READY` (options, example
input, what is tested). These are the executables all runs of section 6 used.
