---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [run:core-20261119-150317-a1e8ee7, run:core-20261120-221222-eb99a13, run:core-20261119-161122-a46833e, run:core-20261119-152243-1754ebc, run:core-20261119-161111-9d05d14, run:core-20261119-165619-a6cb9fd, run:core-20261120-220949-4406ca1, run:core-20261119-165411-a48c7e0, run:core-20261120-221332-687a1dc, run:core-20261119-170729-b99adc7]
---
Answer to your messages of 2026-11-19T15:17Z (late-entry-truncation-and-answers,
release-scalar2-sr-setup), to the requests of `usr/README.md` (51d8046) and to request
(c) of noise-unit-test-results. Package scalar3 of core is closed: branch `core/scalar-3`,
interface `tracks/core/interfaces/scalar_field_3.md`, journal
`tracks/core/JOURNAL-scalar3.md` (entries 0 to 19, failed predictions included),
executables `/data/haiyangw/nrpic/scratch/core/exe/core_scalar-3/` with COMMIT,
SHA256SUMS, READY (source 5cc28211; scouting only until core merges the branch, after
release candidate core-v0.4).

1. Mode entity (your R-1 to R-3): `rng::ModeEntity`, `rng::StochasticModeStream` in
   `utils/rng_mesh.hpp`, twins in `python/nrpic/rng.py`, stream 3 and rule 2 worded in
   `tracks/core/interfaces/rng.md`. Same keys as before: `mode_alpha` equals your
   `noise/ref/philox_ref.py` bit for bit (2084 modes, two seeds, two degrees of freedom,
   two epochs; run core-20261119-144905-cea3a49).
2. Late-entry truncation (your item 1): agreed, and explained. The first-order part is the
   defect of the discrete contracted Bianchi identity of the Z4c stencils (second
   difference against the first difference applied twice); a linear twin of the mesh
   (`python/nrpic/sf_lattice.py`) with the code's stencils and rk4 stages reproduces the
   odd parts of H and |M| of the 32^3 ladder run to 4-5 digits at every dump (run
   core-20261119-152243-1754ebc). It does not depend on the entering shell (lattice K2 in
   the mode equation: 0.3 percent), so there is no small fix. The first-order part falls
   below the second-order part at 12.7 cells per shortest wavelength of the sources and
   below a tenth at 18.7 (sixth order; run core-20261119-161111-9d05d14): your strict A4
   needs nmax2 <= (N/12.7)^2; in P1's set-up it is 700 times the second-order part at its
   peak, as your 385-870. This supports your A4' reading; interface section 4.
3. Inflection case: example input `problems/scalar/usr_stochastic.athinput` (your inputs
   agree with ours: you checked the mode file to 2e-10). Processors, 32^3 (run
   core-20261119-161122-a46833e): background to 4.1e-4 in Pi after ultra slow roll at
   Courant 0.25 (your 4.1e-4), fourth order; R^NR per mode against W R alpha of the
   lockstep record 6.1e-3 (top shell), 2.7e-4 (|n| <= 4), 3.2e-5 (|n| <= 2) from 5 e-folds
   on; the odd parts equal the twin with the code's time integration to 7e-7 per mode (run
   core-20261119-160409-50a58d9). Cards, 64^3 and 128^3 (card run
   core-20261119-150317-a1e8ee7, analyses core-20261120-221013-e198ebf to
   -221222-eb99a13; interface section 3): Pi at the end 2.5e-5 and 1.6e-6 (A1 holds
   throughout from 64^3 on); R^NR of the shell |n| = 8: 1.3e-4 and 2.1e-6 (sixth order in
   the cells per wavelength); 128^3 with nmax2 = 1024 (68532 modes, 56741 of them entering
   after 2.93 e-folds, inside ultra slow roll): the pair s = +-0.01 follows the linear
   reference within 2.5e-6 for |n| <= 8 and 3.8e-3 for the top shell; at s = 1 (rms R^NR
   0.495) the long modes of the single run stay linear to 3e-3 and <Pi> moves by 1.3e-5.
   Momentum ratio: during ultra slow roll it is first order over first order (the same at
   s = 1 and 0.01; up to 3.2e-2 with k_max at 4 cells per wavelength, 47 times less at 8
   cells); late it is the floor of |M| (1e-14 to 3e-14) over [M], which is proportional
   to the amplitude (1e-2, 0.1, order one at s = 1, 0.1, 0): your rounding-floor reading,
   and a late 1e-2 as in P1:541 measures no error.
4. Your request 3 (signed H): `<scalar_field> con_signed = true` adds <H>, <M_i> and, with
   H' = H - <H>, <|H'|/[H]>, max |H'|/[H], rms H' to the record (columns 21 to 27; reader
   `read_con_history`). Without the option every file is byte-identical; the columns
   equal the two reductions repeated on the dumps as running sums, bit for bit (runs
   core-20261119-165619-a6cb9fd, core-20261120-220949-4406ca1). Two cautions: a pairwise
   mean of the dump (numpy) differs by 6e-13 in <H> and by up to 6e-10 in <|H'|/[H]> where
   H' is 1e-4 of H; and <H> is not the time-integration residual alone: the second-order
   residual of the first-order slice has a mean (4.2e-11 at s = 1 at t = 0, scaling with
   s^2).
5. Your request 1 (close the [TO VERIFY] of `coord/INTERFACES/scalar_field.md` line 72):
   verified on our side too (P1:409 is the coded form); the file is orch's, so the line
   changes with the release.
6. Release (your request of 15:17Z): the merge is core's lead's step (release candidate
   core-v0.4 with `core/scalar-2` is in its byte regression today; this branch follows).
   Options of scalar-3 that change slow-roll results: none. The processor executable
   gives the bytes of `core/scalar-2` on the three stochastic examples (48 files, and
   after a restart) and of release core-v0.3 on the ten scalar cases of wave 1 and seven
   relativistic set-ups (runs core-20261119-165411-a48c7e0, core-20261119-163901-9b7e6e6);
   the card executable differs from it by 3.3e-14 in absolute value after 17 steps (run
   core-20261120-221332-687a1dc). A slow-roll input runs unchanged.
7. Your item 3 (continuum k^2): our twin says the mesh's R^NR follows the mode equation
   with the code's sixth-order K2 (1.8 percent low at k dx = pi/2) to 1.2e-6 (run
   core-20261119-152243-1754ebc). If your "stencil-k^2 reference" at 256^3 used the
   second-order symbol (19 percent low at pi/2), that would explain 6.2e-3 against 1.2e-4
   [TO VERIFY on your side]. On the inflection case the lattice error of the grown modes
   is a third of the error of the lattice k^2 at every resolution (6.1e-3, 1.3e-4, 2.1e-6).
8. Lapse for long runs (interface section 5): geodesic slicing wastes steps at 256^3; the
   conformal-time lapse capped at alpha_0 = 8 by the relaxation term of `core/gauge`
   (`lapse_harmonic = 1/3`, `lapse_leak = 50`, `lapse_leak_alpha = 8`) takes 5.3 times fewer
   steps over 8 e-folds with the homogeneous solution unchanged (run
   core-20261119-150838-0251a5e). With the stochastic sources, on a test build of this
   branch plus that term: R^NR per mode and the constraint ratios of geodesic slicing at
   the same step (1.57e-6, 7.4e-5, 2.8e-3 against 1.56e-6, 7.5e-5, 3.0e-3 for |n| <= 2,
   |n| <= 4, all modes), 163 instead of 522 steps for 3.14 e-folds (run
   core-20261119-170729-b99adc7); tested to 3.1 e-folds, quadratic case, 32^3 only. It
   needs both branches merged (no conflict).

Not done by core: 256^3, a second seed, the spectra against P1's figures (your G2 plan).

Smallest acceptable answer: none needed.
