# What Track E needs from the shared random-number interface

Status: requirements of E-stoch-inf (package noise, E-pre-4) for the interface proposed by
core on branch `core/rng` (`tracks/core/interfaces/rng.md`, cited as rng.md; tip 8e05112
when read on 2026-11-15), the E half of the joint proposal of brief M11 (lines 544-547) and
of the verification row "Reproducible random numbers" (brief line 853). Track C's
requirements (collisions) are not covered here. Labels as in the brief; run ids refer to
`tracks/E-stoch-inf/runs/<run_id>/manifest.json`.

## 1. Requirements and their state in the proposal

| Id | Requirement of the stochastic sources | State in rng.md | Evidence |
|---|---|---|---|
| Q1 | A draw is a pure function of its key; no generator state in the code or in restart files | met (section 1) | rng.md section 7 (core's runs); NOISE_SPEC R1-R4 rest on it |
| Q2 | Normal pairs with the same bits on processors, cards and in Python | met (sections 1, 3, 7) | rng.md: one sha256 for seven tables (run core-20261115-115626-f0258ce) |
| Q3 | The document alone suffices to re-implement the draws bit for bit (an independent check, not only the twin) | met | T-N0, run E-stoch-inf-20261115-125255-fcdcbdc: `ref/philox_ref.py`, written from rng.md sections 2-3 with numpy.random.Philox and the documented AGM logarithm, equals the twin for 307368 deviates of the unit-test lattice and 4000 of random keys, bit for bit; with the library logarithm instead, deviations up to 1.2e-12 (under 3e-14/sqrt(2L), as rng.md's error bound implies) |
| Q4 | An entity for a Fourier mode: three signed wave numbers up to the largest N in view (n_max = N/4 = 64 at N = 256; up to 2^20 allowed) | met by `CellEntity` packing with an offset; rule 1 already names "a Fourier mode: its integer wave numbers" | request R-1 below asks for one named helper |
| Q5 | A sub-stream layout of stream 3 (`kStreamStochastic`) that separates mode entities from cell entities and numbers the degrees of freedom | open: the registry row says "to be fixed by the scalar-field package" | proposal: NOISE_SPEC section 4 (bit 16 = modes, lower 16 bits = degree of freedom); request R-2 |
| Q6 | Initial data and the first evolution step distinguishable when they share a stream | open: rule 2 sets step = ncycle of the step being taken and 0 for initial data, so the first step (ncycle 0) and the initial data share step 0 | the frozen scheme uses step 0 on purpose (one draw for the initial slice and all kicks, P1:375); the Markov scheme uses ncycle + 1; request R-3 |
| Q7 | Cost negligible against the synthesis of the field | met | 548958 normal pairs (N = 256, n_max = 64) take 7.3e-5 s on one A100 and 3.7e-2 s on one core (rng.md section 8 times, counts of run E-stoch-inf-20261115-125603-39cb4dd); the synthesis of one field takes 2.5e9 complex multiply-adds |
| Q8 | Statistical quality at the number of draws of a run | met | up to 5.75e9 normal pairs in a Markov/tanh run of 8 e-folds at N = 256 (run E-stoch-inf-20261115-125603-39cb4dd), below the 1e11 keys of rng.md's tests (section 7) |
| Q9 | Independence of the streams of different degrees of freedom and of different steps | met in rng.md's tests (covariance with the key larger by one in each field, section 7) | additionally tested on the noise itself by A7, A8, A15 of NOISE_SPEC |
| Q10 | The seed survives a restart | met (`<job> rng_seed` stored with the parameters, section 2) | A12 tests the noise after a restart |
| Q11 | Independence of the number of ranks | not tested (rng.md section 9: the particle module runs on one rank) | needed once the scalar field runs on several ranks; NOISE_SPEC A11 with ranks instead of MeshBlocks |
| Q12 | The twin importable by the track's tools from `python/nrpic/rng.py` on main | open: the twin is on `core/rng` only | the validation uses its own `ref/philox_ref.py` and does not need the twin; merging it lets the check T-N0 run against main |

Not needed by Track E: `Uniform`, `Index`, `Direction`, the cell helpers of
`utils/rng_mesh.hpp` (unless a cell-keyed noise is chosen, which NOISE_SPEC section 8 advises
against).

## 2. Requests to core (for `coord/INTERFACES/rng.md`)

- R-1 Add `rng::ModeEntity(int nx, int ny, int nz)` (signed, |n_i| < 2^20, equal to
  `CellEntity(nx + 2^20, ny + 2^20, nz + 2^20)`) to `utils/rng_mesh.hpp` and
  `mode_entity` to the twin, so that code and tools share one definition of the mode key.
- R-2 Fix the meaning of stream 3 in the registry (rng.md section 6): sub-stream bit 16 set
  for mode entities, lower 16 bits = degree of freedom (0 scalar curvature perturbation
  and inflaton, 1-2 tensor polarisations, 3 and above further fields); bit 16 clear for
  cell entities if they are ever used. Entity: `ModeEntity(n)`; entity_hi 0; draw 0 (draw
  1 reserved for a second Gaussian per mode and step).
- R-3 State in rule 2 that a stream shared by initial data and evolution keys evolution
  draws with `ncycle + 1`, unless the sharing of one draw is intended (the frozen noise of
  NOISE_SPEC section 5, which keeps step 0 for both).
- R-4 Merge the twin `python/nrpic/rng.py` into main with the header, so that T-N0
  (`ref/check_twin.py`) can run against main.
- R-5 When the scalar field runs on several ranks, add the rank count to the
  reproducibility test (Q11).

## 3. What Track E checks on its side

Independent of core's own tests: the draws from the document (T-N0, done), and on the
code's noise output the acceptance tests A0-A15 of `NOISE_SPEC.md` section 10, with the
validation `validate/validate_noise.py`, which carries its own implementation of the keys
and draws.
