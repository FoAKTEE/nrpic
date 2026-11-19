# Scalar field, third pass: mode keys, the inflection (ultra-slow-roll) case, the first-order constraint part at late entry, lapse conditions, signed constraint means

Status: PROPOSAL of core (branch `core/scalar-3`, 2026-11-19), an amendment to
`scalar_field.md` (release core-v0.3) and `scalar_field_2.md` (branch `core/scalar-2`).
Client: Track E. Evidence labels as in the brief; every number carries a run id
(`tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`).
Predictions and outcomes, including the failed ones: `tracks/core/JOURNAL-scalar3.md`
(J3, entries 0 to 14 and later). Paper keys: P1 = arXiv:2512.14649 v2 `PRD_v2.tex`; SPEC =
`tracks/E-stoch-inf/spec/SPEC.md` on `track/E-stoch-inf`.

## 1. What is new

| Where | What |
|---|---|
| `athenak/src/utils/rng_mesh.hpp` | `rng::ModeEntity(nx, ny, nz)`, `rng::StochasticModeStream(dof)`, constants `kModeEntityOffset`, `kStochasticModeBit` |
| `athenak/src/scalar_field/scalar_field_noise.cpp` | `NoiseDrawAlpha` calls the two helpers (same keys as before) |
| `athenak/src/scalar_field/scalar_field_diag.cpp`, `scalar_field.hpp` | option `<scalar_field> con_signed` (section 6): `ScalarField::ConstraintSignedMeans` |
| `python/nrpic/rng.py` | twins `mode_entity`, `stochastic_mode_stream` |
| `python/nrpic/scalar_field.py` | `mode_alpha` calls the twins; `potential_d2` (V'' of the four analytic potentials); `read_con_history` reads the columns of `con_signed` |
| `python/nrpic/sf_inflation.py` | `code_d2v` |
| `python/nrpic/sf_lattice.py` (new) | the linear twin of the mesh: the linearised equations of the code per wave vector with the symbols of its difference operators (`Twin`), and the same with the stages of the driver's rk4 and the homogeneous part the mesh carries (`CodeTwin`) (section 4) |
| `problems/scalar/usr_stochastic.athinput`, `usr_stochastic_modes.txt` | the inflection case of P1 at 32^3 (section 3) |
| `problems/scalar/sr_stochastic_gauge.athinput` | the quadratic case with a lapse that is not geodesic (section 5); example of `con_signed` |
| `tracks/core/interfaces/rng.md` | stream 3, rule 2, the mode entity (section 2) |
| `tracks/core/analysis/scalar3/` | drivers of all tests, card lists, mode files for nmax2 = 256 and 1024, publish script |

One new input option, `<scalar_field> con_signed` (default false). Lines of files that
existed before (against `core/scalar-2` at 207424d; another core branch may touch the
same files):

| File | Lines (new numbering) | What |
|---|---|---|
| `utils/rng_mesh.hpp` | 11-13, 68-98 | header text; the mode entity and the mode stream, appended after `WrapIndex` |
| `scalar_field/scalar_field_noise.cpp` | 16-19, 451-458 | header text; `NoiseDrawAlpha`: stream and entity through the helpers |
| `scalar_field/scalar_field.hpp` | 179-180, 307 | `SfDiagOptions::con_signed`; declaration of `ConstraintSignedMeans` |
| `scalar_field/scalar_field_diag.cpp` | 30-33, 95-97, 299-304, 307, 313-319, 323-392 | header text; `DiagInit` reads the option; `WriteConstraintHistory` writes the line ends separately and the seven columns with the option; `ConstraintSignedMeans` (new function after it) |

Nothing under `athenak/src/z4c/` is touched (the relaxed lapse of `core/gauge` merges
without conflict; section 5).

## 2. Mode entity and stream 3 (Track E's requests R-1 to R-3)

    rng::ModeEntity(nx, ny, nz)      = CellEntity(nx + 2^20, ny + 2^20, nz + 2^20),  |n_i| < 2^20, entity_hi = 0
    rng::StochasticModeStream(dof)   = Stream(kStreamStochastic, 2^16 + dof),         dof < 2^16
    alpha_n = (z1 + i z2)/sqrt 2,  (z1, z2) = Normal2({seed, StochasticModeStream(dof), ModeEntity(n), epoch}, 0)

The wave numbers are those of the mode on the root mesh. Registry of stream 3, the
degrees of freedom of the two models, the epoch (0 for the frozen amplitudes shared by
the initial slice and all kicks; `ncycle + 1` for amplitudes new in every step) and the
wording of rule 2: `rng.md` sections 3, 5, 6 on this branch. The keys are the integers
the code used before, so every amplitude and every output is unchanged.
[VERIFIED, run core-20261119-144905-cea3a49] `mode_entity(n)` equals `cell_entity(n +
2^20)` for the 548958 wave vectors of nmax2 = 4096 and the corners; out-of-range values
are refused; `mode_alpha` equals Track E's independent `noise/ref/philox_ref.py` bit for
bit (2084 modes, two seeds, two degrees of freedom, two epochs).

## 3. The inflection (ultra-slow-roll) case

P1:405-420: V = Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2)/(3 (3 phi^2 + 2
v^2)^2), Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl at the Bunch-Davies time, N* -
N0 = 3, N_f - N* = 10 [VERIFIED at the source by core; the form of the code is the
printed one; Track E found the same by an independent transcription, V and V' to 1e-15].
In code units (G = 1, time unit 1/H*; `sf_inflation.code_case`): lambda = 8 pi
Lambda/H*^2 = 5.333176485e5, vev = v/sqrt(8 pi) = 3.949528576e-2, phi0 = -0.1643281883,
pi0 = 3.236586528e-2 at N*; H*/Mpl = 9.3623188e-6, eps1* = 1.316389e-2, eps2* = -0.430663.

    cd problems/scalar && <exe> -i usr_stochastic.athinput -d <rundir>

runs 32^3 with k_max/dk = 8 to t = 10.5 (214 steps, 10.06 e-folds; 13 minutes on one
processor core). Other mode cuts: `python3 tracks/core/analysis/scalar2/make_case.py
--case inflection --nmax2 <n> --out DIR [--kstart 100]`.

What the processor runs show (32^3, nmax2 = 64, Courant 0.25 and 0.125, mode scales s =
+-1, +-0.1, 0 and the control `noise_pi_sign = -1`; analysis run
core-20261119-161122-a46833e, J3 entry 14) [VERIFIED for this resolution]:

| Quantity | Result |
|---|---|
| Background against the ordinary differential equations (SciPy) | box means: phi within 3.5e-7, K within 9.3e-8; e-folds from <chi> within 7.0e-6; <Pi> relative 2.6e-6 at 3 e-folds, 1.7e-5 at 5, 4.1e-4 after ultra slow roll (Track E's A1, 1e-4, is missed late at this step); every error falls 16.3 to 16.6 times at half the step (fourth order). Ultra slow roll (eps2 > 3) from 2.54 to 6.51 e-folds, eps1 down to 9.72e-13, as the reference |
| Mode functions of the sources (lockstep record against SciPy) | top shell within 5.6e-4; lowest shells within 1e-4 to 6 e-folds, then 4.1e-4 (time step: 2.5e-5 at Courant 0.125, ratio 13.5 to 20); |R| of every shell grows 300 to 24000 times through ultra slow roll, as the reference |
| R^NR per mode (odd part of s = +-0.1) against L^(-3/2) W R alpha of the lockstep record, after 5 e-folds | top shell (k dx = pi/2) 6.1e-3, |n| <= 4 2.7e-4, |n| <= 2 3.2e-5 (the lattice dispersion, which the linear twin predicts exactly); a single run s = 1: 3.1e-4 for |n| <= 2, its even (second-order) part 3e-4, ten times that of s = 0.1; rms of R^NR 6.7e-2 |
| Constraints | <|H|/[H]> is the uniform residual of the time integration of the background: 1.6e-8 to 1.08e-7 to 3 e-folds, 17 times less at half the step, below 1e-14 after 6 e-folds; it does not grow in ultra slow roll. <|M|/[M]> 5e-6 before the entry, 1.7e-2 at most (3.4 e-folds), 3.4e-3 at the end, unchanged at half the step (spatial); odd parts scale with s (10.000), even parts with s^2 (90 to 103 for a factor 10) up to 3 e-folds |
| Control `noise_pi_sign = -1` | |M|/[M] 0.14 to 0.21; R^NR off by 0.5 to 2 |

The parts odd in s of R^NR, H and |M| equal those of the linear twin with the time
integration of the code (section 4) to 7e-7 per mode and 2e-4 in rms (run
core-20261119-160409-50a58d9): at first order the code does on the inflection case what
its linearised equations say. The 256^3 production set-up is Track E's (its G2 plan).

CARD_U

## 4. The first-order part of the constraints when the last shells enter (item 3)

Finding [VERIFIED for the slow-roll case on the ladder N = 32, 64, 128, runs
core-20261119-151758-51d9a71, core-20261119-152243-1754ebc, core-20261119-161111-9d05d14]:
the part of H and M_i that is first order in the amplitude and appears when the last
shells enter (Track E: from ln(N/8) e-folds after N*) is the defect of the discrete
contracted Bianchi identity of the spacetime solver. Linearising the equations the code
solves about the homogeneous background (geodesic slicing, zero shift; J3 entry 1), with
the symbols D1_a -> i q_a and Dxx_a -> -kap_a of the sixth-order stencils, the
constraints of the mesh are driven by the linear solution itself times mu_a = kap_a -
q_a^2, the mismatch between the second difference and the first difference applied
twice (mu/k^2 = 0.110 at 4 cells per wavelength, 2.6e-3 at 8, 4.4e-5 at 16). The twin
(`nrpic.sf_lattice`) built from these equations reproduces the measured odd parts of H
and |M| at N = 32 to 4 to 5 digits at every dump when it carries the stages of the
driver's rk4 (`CodeTwin`), at N = 64 from 1.6 e-folds on, at N = 128 from 2.4 on (before,
the measured values sit on a floor of 5e-13 to 1.7e-12 that the twin does not have).

Consequences:
1. No small change at the entering shell removes it. Evolving the mode functions of the
   sources with the lattice K2 changes it by 0.3 percent. Writing every second
   derivative of Z4c as the first difference applied twice removes it (by 1e-5) but is a
   change of the spacetime solver's stencils and makes the lattice dispersion of R^NR
   seven times worse (2.0e-2 against 2.8e-3 at N = 32; the first difference applied
   twice is 12.8 percent low at k dx = pi/2, the second difference 1.8 percent). Not done.
2. It converges at sixth order in the cells per wavelength (slope -5.93 in the scan) and
   it does not depend on the time step.
3. The resolution the strict criterion needs (Track E's A4: the constraints second order
   during the entry). Largest ratio in time of the first-order part to the second-order
   part (measured even part of the 64^3 runs, quadratic case, nmax2 = 64): 692, 213, 77,
   14.9, 4.0, 1.38, 0.25 at 4, 5, 6, 8, 10, 12, 16 cells per shortest wavelength of the
   sources (H; |M| within 12 percent of these). It falls below 1 at 12.7 cells and below
   0.1 at 18.7 cells (extrapolated). So A4 as written holds only with nmax2 <= (N/12.7)^2,
   i.e. k_max <= 20 dk at 256^3 (P1 uses 64 dk: 4 cells, where the first-order part
   exceeds the second-order part 700 times at its peak). For P1's set-up the reading of
   A4 in odd and even parts (Track E's proposal A4' to orch) is the one the code can meet;
   the twin gives the expected odd part for any N, nmax2 before a run.
4. The lattice error of R^NR at the last dump falls the same way: 2.8e-3, 8.5e-4, 3.1e-4,
   5.9e-5, 1.6e-5, 5.4e-6, 9.9e-7 at 4 to 16 cells; it is the second difference's
   dispersion, which the twin with the lattice K2 in the mode equation removes to 1.2e-6.
   [TO VERIFY by Track E] its statement that the runs follow the continuum mode functions
   (1.2e-4) better than a stencil-k^2 reference (6.2e-3) at 256^3 may use the
   second-order stencil symbol; the code's sixth-order symbol is 1.8 percent low at pi/2.

How to use the twin before a run: `tracks/core/analysis/scalar3/a1_twin.py` (slow roll,
ladder and scan) and `a2_twin_usr.py` (inflection case); both take minutes on one core
for nmax2 = 64.

## 5. Lapse conditions for a long inflationary run (item 4)

The sources carry the box mean of the lapse and their lockstep background runs in the
proper time of that mean, so any lapse with a homogeneous background part can be used.
Measured (J3 entries 3, 6, 8, 12):

| Lapse (`<z4c>`) | On this branch | Result |
|---|---|---|
| geodesic, `lapse_harmonic = 0` | yes | reference; background to 4e-13 over 8 e-folds (run core-20261119-144906-69c60cc). Wastes steps at high resolution: H dt = 2 pi C/N is 0.006 at 256^3, eight times below what the time integration needs |
| `lapse_harmonic = 0.05` (alpha grows to 1.62 in 3.2 e-folds) | yes | sources and slice work: box means against the lockstep background 2e-11, mean lapse as 1/(1 - 0.15 int H dt) to 3.4e-7, R^NR per mode as geodesic within a factor 0.55 to 1.6 except the first dump (3.7, not explained), constraints as geodesic (run core-20261119-160004-63c808c) |
| `lapse_kdriver = 2` (mean lapse 1) | yes | mean lapse 1 to 6.5e-12, lapse perturbation 3e-6; R^NR and constraint ratios as geodesic except that the lowest modes drift to 4 times the geodesic deviation late (1.5e-5 at 3.2 e-folds; not explained) (same run) |
| conformal time, `lapse_harmonic = 1/3` | yes | unusable beyond about ln(0.05 N/(2 pi C)) e-folds: the step in e-folds grows as alpha = a; at 16^3 with the step of 32^3 the e-folds are off by 1.2 after 3.4 e-folds (run core-20261119-144906-69c60cc) |
| 1+log, `lapse_oplog = 2` | yes | unusable: alpha = 1 + 6N, non-finite after 3.06 e-folds at the step of 32^3 (same run) |
| 1+log relaxed, `lapse_leak = 10` | needs `core/gauge` | the lapse settles at exp(6 H T) = 1.81 and follows H; the solution is unchanged at equal field value (K to 3.3e-11, e-folds to 5.2e-5) (runs -144906-69c60cc, -150816-a8f9558) |
| conformal time capped, `lapse_harmonic = 1/3`, `lapse_leak = 50`, `lapse_leak_alpha = 8` | needs `core/gauge` | alpha = a to 7.8e-8 until 8, then the root of ln(alpha/8) = T H alpha (9.5); at the step of a 256^3 run 8 e-folds take 252 steps instead of 1341 (5.3 times fewer), the solution unchanged at equal field value (K to 6.8e-12) (run core-20261119-150838-0251a5e) |

G5_RESULT

What a long run needs from `core/gauge` [JUDGEMENT]: only the relaxation term
(`lapse_leak`, `lapse_leak_alpha`; `z4c/z4c_gauge_ext.hpp`, seven lines in `z4c.cpp`,
`z4c.hpp`, `z4c_calcrhs.cpp`). It merges with this branch without conflict (this branch
touches nothing under `z4c/`; test build `scratch/core/tmp/gmerge/`). Recommended for a
256^3 inflationary run once both are merged: the capped conformal-time lapse with
alpha_0 = 0.05 N/(2 pi C) (8 at 256^3, Courant 0.25) and T = 0.02: the run then takes
(1 - 1/alpha_0) N/(2 pi C) steps for the first ln alpha_0 e-folds and 20 per e-fold after.
Not tested: refined meshes, a perturbation that collapses, the 1+log part of
`core/gauge` with the sources.

## 6. Signed constraint means: `<scalar_field> con_signed` (Track E's request 3 of its USR package)

    con_signed = true    # columns 21-27 of <basename>.sf.con.hst

[21] <H>, [22-24] <M_x>, <M_y>, <M_z> (signed, coordinate-volume weights), and with H' = H -
<H>: [25] <|H'|/[H]>, [26] max |H'|/[H], [27] rms H'. A uniform residual of the time
integration of the background sits in <H> and drops out of H', so H' carries the parts
of H that the perturbations make. Two reductions per record. Without the option the
record is byte for byte that of `core/scalar-2`. Reader: `read_con_history` (names
H_mean, Mx_mean, My_mean, Mz_mean, Hp_ratio, Hp_ratio_max, Hp_rms). Example:
`problems/scalar/sr_stochastic_gauge.athinput`.

S_RESULT

## 7. What is verified, and what is not

R_RESULT

Not tested, known limits:
- No run of this branch beyond 32^3 on processors; the card runs of section 3 are listed
  there with their state. One seed.
- The early floor of the odd constraint parts on the card ladder (N = 64, 128) is not in
  the twin ([JUDGEMENT] rounding).
- The drift of the lowest modes under `lapse_kdriver` and the first dump under
  `lapse_harmonic = 0.05` are not explained.
- The relaxed and the capped lapse need `core/gauge`; their test with the sources ran on
  a test build outside both branches (section 5).
- The initial slice satisfies the constraints at first order only; a* = 1 only; no refined
  mesh.

## 8. Published executables (decision 0013)

PUBLISH
