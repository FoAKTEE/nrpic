# Scalar field, third pass: mode keys, the inflection (ultra-slow-roll) case, the first-order constraint part at late entry, lapse conditions

Status: PROPOSAL of core (branch `core/scalar-3`, 2026-11-19), an amendment to
`scalar_field.md` (release core-v0.3) and `scalar_field_2.md` (branch `core/scalar-2`).
Client: Track E. Evidence labels as in the brief; every number carries a run id
(`tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`).
Predictions and outcomes, including the failed ones: `tracks/core/JOURNAL-scalar3.md`
(J3). Paper keys: P1 = arXiv:2512.14649 v2 `PRD_v2.tex`; SPEC =
`tracks/E-stoch-inf/spec/SPEC.md` on `track/E-stoch-inf`.

## 1. What is new

| Where | What |
|---|---|
| `athenak/src/utils/rng_mesh.hpp` | `rng::ModeEntity(nx, ny, nz)`, `rng::StochasticModeStream(dof)`, constants `kModeEntityOffset`, `kStochasticModeBit` |
| `athenak/src/scalar_field/scalar_field_noise.cpp` | `NoiseDrawAlpha` calls the two helpers (same keys as before) |
| `python/nrpic/rng.py` | twins `mode_entity`, `stochastic_mode_stream` |
| `python/nrpic/scalar_field.py` | `mode_alpha` calls the twins; `potential_d2` (V'' of the four analytic potentials) |
| `python/nrpic/sf_inflation.py` | `code_d2v` |
| `python/nrpic/sf_lattice.py` (new) | the linear twin of the mesh: the linearised equations of the code per wave vector with the symbols of its difference operators (section 4) |
| `problems/scalar/usr_stochastic.athinput`, `usr_stochastic_modes.txt` | the inflection case of P1 at 32^3 (section 3) |
| `problems/scalar/sr_stochastic_gauge.athinput` | the quadratic case with a lapse that is not geodesic (section 5) |
| `tracks/core/interfaces/rng.md` | stream 3, rule 2, the mode entity (section 2) |
| `tracks/core/analysis/scalar3/` | drivers of all tests, card list, mode files for nmax2 = 256 and 1024, publish script |

No new input option. Lines of files that existed before (against `core/scalar-2` at
207424d):

| File | Lines (new numbering) | What |
|---|---|---|
| `utils/rng_mesh.hpp` | 11-13, 69-99 | header text; the mode entity and the mode stream, appended after `WrapIndex` |
| `scalar_field/scalar_field_noise.cpp` | 16-20, 451-459 | header text; `NoiseDrawAlpha`: stream and entity through the helpers |

Nothing else under `athenak/` is touched.

## 2. Mode entity and stream 3 (Track E's requests R-1 to R-3)

    rng::ModeEntity(nx, ny, nz)      = CellEntity(nx + 2^20, ny + 2^20, nz + 2^20),  |n_i| < 2^20, entity_hi = 0
    rng::StochasticModeStream(dof)   = Stream(kStreamStochastic, 2^16 + dof),         dof < 2^16
    alpha_n = (z1 + i z2)/sqrt 2,  (z1, z2) = Normal2({seed, StochasticModeStream(dof), ModeEntity(n), epoch}, 0)

The wave numbers are those of the mode on the root mesh. Registry of stream 3, the
degrees of freedom of the two models, the epoch (0 for the frozen amplitudes shared by
the initial slice and all kicks; `ncycle + 1` for amplitudes new in every step) and the
wording of rule 2: `rng.md` sections 3, 5, 6 on this branch. The keys are the integers
the code used before, so every amplitude and every output is unchanged (section 6).

## 3. The inflection (ultra-slow-roll) case

P1:405-420: V = Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2)/(3 (3 phi^2 + 2
v^2)^2), Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl at the Bunch-Davies time, N* -
N0 = 3, N_f - N* = 10 [VERIFIED at the source by core; the form of the code is the
printed one]. In code units (G = 1, time unit 1/H*; `sf_inflation.code_case`): lambda =
8 pi Lambda/H*^2 = 5.333176485e5, vev = v/sqrt(8 pi) = 3.949528576e-2, phi0 =
-0.1643281883, pi0 = 3.236586528e-2 at N*; H*/Mpl = 9.3623188e-6, eps1* = 1.316389e-2,
eps2* = -0.430663 (SPEC 6: 9.36232e-6, 1.3164e-2, -0.4307). Reference background (e-folds
after N*): eps2 > 3 from 2.53 to 6.55, eps1 falls to 9.7e-13 at 8.3, H to 0.9518 H*; 10
e-folds end at t = 10.43.

    cd problems/scalar && <exe> -i usr_stochastic.athinput -d <rundir>

runs 32^3 with k_max/dk = 8 to t = 10.5 (11 minutes on one processor core). Other mode
cuts: `python3 tracks/core/analysis/scalar2/make_case.py --case inflection --nmax2 <n>
--out DIR [--kstart 100]` (with `--kstart` for nmax2 above about 300: a start of every
mode at N0 takes hours for the high shells).

RESULTS_U

## 4. The first-order part of the constraints when the last shells enter

RESULTS_A

## 5. Lapse conditions for a long inflationary run

RESULTS_G

## 6. What is verified

RESULTS_TABLE

## 7. Limits and open points

RESULTS_LIMITS

## 8. Published executables (decision 0013)

RESULTS_PUBLISH
