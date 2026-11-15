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
| `validate/athenak_io.py` | reader of AthenaK `bin` output (via `athenak/vis/python/bin_convert.py`) and of core's NRSFDMP1 dumps with the parameters of the run's input file; assembly of MeshBlocks; `.npz` runs of the self-test |
| `validate/selftest.py` | T-N2 to T-N4: calibration over seeds, positive controls, 15 mutants |
| `validate/calib_a3.py` | T-N6: calibration of the A3 decisions over 2000 seeds |
| `validate/reader_test.py`, `validate/inputs/reader_test.athinput` | T-N5: the reader on real AthenaK output |
| `validate/dump_selftest.py` | T-N8: the adapter to core's NRSFDMP1 dumps (power model) |
| `fig/` | the figures the documents cite (copies from the runs) |

## How to rerun

Python 3 with numpy, scipy, matplotlib (user site-packages of the machine); none of the
scripts reads downloaded data. From the worktree root, `N=tracks/E-stoch-inf/noise`:

    git show core/rng:python/nrpic/rng.py > scratch/E-stoch-inf/tmp/rng_twin/rng.py
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/ref/check_twin.py --twin scratch/E-stoch-inf/tmp/rng_twin/rng.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/ref/count_draws.py --out {out}
    python3 $N/ref/runreg.py --cores 4 --purpose "..." -- python3 $N/validate/selftest.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/validate/calib_a3.py --out {out}
    python3 $N/ref/runreg.py --purpose "..." -- python3 $N/validate/dump_selftest.py --out {out}
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

Done: NOISE_SPEC.md, RNG_REQUIREMENTS.md, reference, validation of `bin` output and of
core's NRSFDMP1 dumps, and their self-tests T-N0 to T-N8 (JOURNAL.md has every
prediction and outcome, including the refuted ones: T-N3, and parts of T-N0 and T-N6, with
the amendments they caused). Core has written the generator (`core/scalar-field` 5384d02,
`athenak/src/scalar_field/scalar_field_noise.cpp`, untested there) with the keys of
section 4 of NOISE_SPEC. Not done: validation on code output, because no run with noise
exists; the runs are named below.

| Run | Test | Evidence |
|---|---|---|
| E-stoch-inf-20261115-125255-fcdcbdc | T-N0 draws from rng.md alone equal core's twin bit for bit | `fig/fig_check_twin.png` |
| E-stoch-inf-20261115-125603-39cb4dd | T-N1 modes, draws per step, synthesis cost | `fig/fig_count_draws.png` |
| E-stoch-inf-20261115-131126-8eb199a | T-N5 reader on real AthenaK `bin` output | `fig/fig_reader_test.png` |
| E-stoch-inf-20261115-131031-ec74943 | T-N2 to T-N4, first rule (T-N3 refuted) | journal |
| E-stoch-inf-20261115-131551-629fed8, -131820-629fed8 | T-N6, T-N7 calibration of A3 | `fig/fig_calib_a3.png` |
| E-stoch-inf-20261115-132950-16a0168 | T-N3b, T-N4b with the family-wise rule | `fig/fig_selftest_*.png`, `fig/fig_val_*.png` |
| E-stoch-inf-20261115-133731-2031735 | T-N8 adapter to NRSFDMP1 dumps | `fig/fig_dump_selftest.png` |

The `fig_val_pos_*` figures draw the 1/sqrt(M) band of A2 only up to the shells of the
first output (fixed in the code after that run).

## Requests

To core (details NOISE_SPEC section 11, RNG_REQUIREMENTS section 2):
- C3 runs of the generator, named here in the options of `scalar_field_noise.cpp`
  (executable built from `core/scalar-field`; seconds each on processors): pgen
  `scalar_field` with `<scalar_field> couple = false`, `noise = power`,
  `noise_nmax2 = 256`, `noise_window = tanh`, `noise_sharpness = 5`,
  `noise_ksigma0 = 0.9`, `noise_hubble = 1`, `noise_amp = 1`, `noise_tilt = 0`,
  `noise_t0 = 0`, `noise_pi_dof = 1`, `noise_c_phi = noise_c_pi = 0` (fields generated
  and dumped, no kicks), `dump_dcycle = 100`; `<job> rng_seed = 20261115`; mesh 64^3 on
  [-1.25, 1.25)^3, periodic; `nlim = 300`.
  U1 MeshBlocks 64^3; U2 32^3; U3 16^3; U4 U2 restarted from its restart file at cycle
  150; U5a/U5b `noise_nmax2 = 64` at N = 32 and 64 with the Courant number of N = 32
  halved so that dt is the same; U6 `noise_scheme = markov`; U7 Markov with
  `noise_window = heaviside`; U8 U2 with `rng_seed = 20261116`; U9 U2 on a card.
  Then:

      python3 $N/validate/validate_noise.py --input U1/<input> --run U1 --blocks8 U2 \
          --blocks64 U3 --restart U4 --res-lo U5a --res-hi U5b --seed2 U8 \
          --seed2-input U8/<input> [--card U9] --out DIR
      python3 $N/validate/validate_noise.py --input U6/<input> --run U6 --out DIR2
      python3 $N/validate/validate_noise.py --input U7/<input> --run U7 --out DIR3

  (for U5a/U5b the geometry is read from the dumps; the other parameters from --input).
- C1 is met by core's own double-precision dump; the `bin` output stays single precision.
- C5 (new) to confirm that the dump at cycle m holds the increment of the step ending at
  m (the validation assumes it; A1 fails clearly otherwise), and optionally a noise-only
  switch (all other terms of the field off) so that phi(t) is the integrated field of
  A9.
- C2 / R-1, R-2 `rng::ModeEntity` and the meaning of stream 3 in the registry (the code
  already uses this layout through `CellEntity(n + 2^20)`); C4 / R-3 rule 2 of rng.md;
  R-4 merge the twin into main; R-5 rank-count reproducibility once the field runs on
  several ranks.

To the lead (E-stoch-inf) and E-pre-1:
- L1 SPEC section 5.4, third bullet, keys real-space white noise by cell; NOISE_SPEC,
  DESIGN_REVIEW 6.2 and core's code key the amplitudes by wave vector (one realisation at
  every N, no transform needed). Proposed: align SPEC 5.4.
- `codebase/ref/synth.py:hermitian_gaussian` uses numpy's generator; when that reference
  is reused for code output it should take the keys of `ref/philox_ref.py`.

Pending runs for the lead: U1-U9 above, then the three validation commands (no card time
except U9).
