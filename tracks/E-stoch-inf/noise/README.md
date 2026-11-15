# noise: coloured Gaussian noise of the stochastic sources (E-pre-4 under decision 0010)

Owner: E-stoch-inf (helper package). The generator is code in `athenak/src/`, written by
core with the scalar field (branch `core/scalar-field`) on the random-number interface of
`core/rng`. This directory holds the specification, the reference calculation, the
validation of the code's output and the requirements on the shared interface.
Predictions and outcomes: `JOURNAL.md`. Run manifests: `tracks/E-stoch-inf/runs/`.

## Contents

| Path | What |
|---|---|
| `NOISE_SPEC.md` | the specification for core: Fourier convention and normalisation, mode set, keys (seed, degree of freedom, wave vector, epoch), frozen and Markov schemes, numbers at the resolutions of the specification, what must be reproducible, the unit test the code provides (runs U1-U9), acceptance tests A0-A15 with pass criteria |
| `RNG_REQUIREMENTS.md` | what Track E needs from `core/rng`, checked against core's proposal; requests R-1 to R-5 |
| `ref/philox_ref.py` | the draws re-implemented from rng.md alone (numpy.random.Philox, documented AGM logarithm) and the noise keys |
| `ref/noise_ref.py` | reference: lattice and half space, amplitudes, transfer functions of the unit test, synthesis and analysis on the mesh, expected statistics |
| `ref/check_twin.py` | T-N0: philox_ref against core's twin `python/nrpic/rng.py` |
| `ref/count_draws.py` | T-N1: modes, draws per step, step counts, synthesis cost |
| `ref/runreg.py` | runs a command as a registered run (manifest in `tracks/E-stoch-inf/runs/`) |
| `validate/validate_noise.py` | the validation of code output, tests A0-A15 |
| `validate/athenak_io.py` | reader of AthenaK `bin` output (via `athenak/vis/python/bin_convert.py`), assembly of MeshBlocks, parameters from the file header; `.npz` runs of the self-test |
| `validate/selftest.py` | T-N2 to T-N4: calibration over seeds, positive controls, 15 mutants |
| `validate/calib_a3.py` | T-N6: calibration of the A3 decisions over 2000 seeds |
| `validate/reader_test.py`, `validate/inputs/reader_test.athinput` | T-N5: the reader on real AthenaK output |
| `fig/` | the figures the documents cite (copies from the runs) |

## How to rerun

Python 3 with numpy, scipy, matplotlib (user site-packages of the machine); none of the
scripts reads downloaded data. From the worktree root, `N=tracks/E-stoch-inf/noise`:

    git show core/rng:python/nrpic/rng.py > scratch/E-stoch-inf/tmp/rng_twin/rng.py
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/ref/check_twin.py --twin scratch/E-stoch-inf/tmp/rng_twin/rng.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/ref/count_draws.py --out {out}
    python3 $N/ref/runreg.py --cores 4 --purpose "..." -- python3 $N/validate/selftest.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/validate/calib_a3.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/validate/reader_test.py --athena .work/build_cpu_c1/src/athena --input $N/validate/inputs/reader_test.athinput --out {out}

(`.work/...` is the processor executable of the main checkout, `/data/haiyangw/nrpic/.work`.)
Validation of the code's unit test once core has run U1-U9 (NOISE_SPEC section 9), each
argument a run directory with the `bin` files:

    python3 $N/validate/validate_noise.py --run U1 --blocks8 U2 --blocks64 U3 --restart U4 \
        --res-lo U5a --res-hi U5b --seed2 U8 [--card U9] --out DIR
    python3 $N/validate/validate_noise.py --run U6 --out DIR2      # Markov, tanh
    python3 $N/validate/validate_noise.py --run U7 --out DIR3      # Markov, Heaviside

Exit status 1 if a test fails; `validation.json` holds every test with value and criterion.
The parameter names the reader expects are those of NOISE_SPEC section 9
(`athenak_io.params_from_header`); if core chooses other names, only that function changes.

## State (2026-11-15)

Done: NOISE_SPEC.md, RNG_REQUIREMENTS.md, reference, validation and its self-test (see
JOURNAL.md for every outcome, including the refuted prediction T-N3 and the amendments it
caused). Not done: validation on code output. `core/scalar-field` had no commit beyond
main when this package ended, so no noise field written by the code exists; the runs are
named for the lead below.

## Requests

To core (details NOISE_SPEC section 11, RNG_REQUIREMENTS section 2):
- C1 double-precision `bin` output (the writer uses `float`, `outputs/binary.cpp` line 96;
  verified on real output in run E-stoch-inf-20261115-131126-8eb199a), or a double dump
  of the unit test in the same layout.
- C2 / R-1, R-2 the mode key: `rng::ModeEntity`, meaning of stream 3 (bit 16 = modes,
  lower 16 bits = degree of freedom) in the registry.
- C3 the unit test `stoch_noise_test` of NOISE_SPEC section 9 and runs U1-U9 (seconds
  each, processors; U9 on a card if a card build is made). This track then validates.
- C4 / R-3 Markov epoch = ncycle + 1; rule 2 of rng.md to say so for shared streams.
- R-4 merge the twin into main; R-5 rank-count reproducibility once the field runs on
  several ranks.

To the lead (E-stoch-inf) and E-pre-1:
- L1 SPEC section 5.4, third bullet, keys real-space white noise by cell; NOISE_SPEC and
  DESIGN_REVIEW 6.2 key the amplitudes by wave vector (one realisation at every N, no
  transform needed). Proposed: wave-vector keys; SPEC 5.4 to be aligned.
- The half space of the draw is that of DESIGN_REVIEW (`codebase/ref/synth.py:half_space`)
  and the entity packing that of NOISE_SPEC section 4; `synth.py:hermitian_gaussian` uses
  numpy's generator and should switch to these keys when the reference of E-pre-2 is
  reused.

Pending run for the lead: once `core/scalar-field` has the unit test, run U1-U9 and the
three validation commands above (no card time needed except U9).
