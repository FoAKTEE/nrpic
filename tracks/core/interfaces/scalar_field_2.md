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
| `scalar_field/scalar_field_noise.cpp` | 180-184, 337-339, 430-432, 687-689 | `noise_mode_scale`; `NoiseSetup` returns if `InitialSlice` has done it; scale applied to the mode file; no synthesis in a stage when all kicks are off |
| `pgen/nrpic/scalar_field_tests.cpp` | 32-37, 88-93, 193, 239-240 | `id = stochastic`: header text, kind 3, background as `flrw`, call of `InitialSlice` |
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

See section 7 of this file's journal (`tracks/core/JOURNAL-scalar2.md`, entries 3 on) for
the predictions and the failed ones. Figures: `tracks/core/notes/scalar2_figs/`.

RESULTS_TABLE

## 7. Limits and open points

OPEN_POINTS
