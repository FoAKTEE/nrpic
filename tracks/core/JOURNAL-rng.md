# JOURNAL of core, work package rng (reproducible random numbers)

Append-only, newest at the bottom. Predictions are written before a test runs, outcomes
after. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run outputs live under
`scratch/core/<run_id>/`, manifests under `tracks/core/runs/<run_id>/`.

## 2026-11-15 11:30 UTC  session core-rng  design

Task: brief lines 544-547 (M11), verification row "Reproducible random numbers" (line
853), work packages C-pre-2 and E-pre-4; decision 0010 (everything in this AthenaK).

### What exists and is left alone

- `athenak/src/utils/random.hpp`: `Ran2`, `RanSt`, `RanGaussian` (sequential generators
  with static or caller-held state). Not usable for reproducible parallel draws; not
  touched.
- `athenak/src/pgen/nrpic/nrpic_cosmo.cpp:59-70`: `CosmoNoise`, a splitmix64 hash of
  (cell, component, seed) for the noise test of the cosmology problem generator. Not
  touched (the task forbids changing existing uses).

### Design decisions [JUDGEMENT]

1. Generator: Philox-4x64 with ten rounds (the counter-based family of Salmon et al.,
   "Random123"). Reasons: (a) a 256-bit counter and a 128-bit key give every field of
   (seed, stream, entity, step, draw) its own 64-bit word, with two words for the entity
   (a pair of particle tags, or a cell index plus its level), so nothing has to be packed
   by the user; (b) `numpy.random.Philox` on this machine (numpy 2.2.6; its docstring
   names the 4x64 generator and its 256-bit counter and 128-bit key) is an independent
   implementation of the same function, which gives a known-answer test without
   downloading anything; (c) only integer operations (64-bit multiply high and low, xor,
   add), exact on every platform.
   Layout: key = (seed, stream); counter = (entity, entity_hi, step,
   draw*256 + kind*16 + block). `kind` separates raw words (0), normal pairs (1) and
   directions (2); `block` counts the retries of the rejection step.
2. Derived draws must be bit-identical on processors, on the card and in Python. The
   library logarithm, sine and cosine are not correctly rounded and differ between glibc,
   the CUDA library and NumPy, and a product followed by a sum may or may not be fused
   by the compiler. So the derived draws use only operations that IEEE 754 defines
   uniquely, arranged so that no product feeds a sum unless the product is exact:
   - uniform in (0,1): (floor(w / 2^12) + 1/2) 2^-52, exact, never 0 or 1, mean 1/2;
   - point in the unit disk by rejection on a lattice of odd integers of 26 bits and
     sign (v1, v2 from one word; s = v1^2 + v2^2 < 2^52 is computed in integers);
   - direction (Marsaglia 1972 construction): n = (2 v1 h, 2 v2 h, 1 - 2 s) with
     h = sqrt(1 - s), s in units of 2^52: one exact difference, one square root, one
     product per component. Uniformity on the sphere: for a uniform point in the disk
     s is uniform in (0,1), so n_z = 1 - 2 s is uniform in (-1,1), and the azimuth is
     that of (v1, v2), independent of s;
   - normal pair (polar form of Box-Muller): z_i = v_i sqrt(2 L / s), L = -ln(s 2^-52).
     L comes from the arithmetic-geometric mean, ln(4/y) = pi / (2 agm(1, y)) (1 + O(y^2)),
     with y = 2^-30 (s 2^-52) <= 2^-30: ten steps a <- (a+b)/2, b <- sqrt(a b), then one
     division and one subtraction of the constant 32 ln 2. Every operation is a single
     correctly rounded one whose operands are not products feeding a sum.
3. The Python twin (`python/nrpic/rng.py`) repeats the same operations with NumPy arrays.
4. Demonstration in the code: a test kick of the particle momenta at the end of the push
   (`athenak/src/particles/nrpic_kick.cpp`, off by default), keyed by (run seed, stream
   "tests", particle tag, cycle number), with two control keys that are expected to fail:
   `block` (the key also contains the MeshBlock that owns the particle, as with one
   generator per MeshBlock) and `sequence` (the step is the number of kicks since the
   executable started, as with a generator whose state is not in the restart file).

### Scouting done before this entry (not a registered test)

- `scratch/core/tmp/rng/proto1.py`: a pure-Python Philox-4x64-10 written from memory of
  the algorithm equals `numpy.random.Philox(counter=c, key=k).random_raw(4)` for 200 of
  200 random (c, k) when evaluated at counter c + 1 (NumPy increments before it
  generates), and for 0 of 200 at counter c. So the multipliers 0xD2E7470EE14C6C93,
  0xCA5A826395121157, the key increments 0x9E3779B97F4A7C15, 0xBB67AE8584CAA73B and the
  round structure are those of NumPy's generator. [VERIFIED by this comparison; the
  registered test repeats it with the shipped twin.]
- `scratch/core/tmp/rng/proto2.py`: the arithmetic-geometric-mean logarithm against mpmath
  (200 bits) on 20000 values of s between 2 and 2^52: maximum absolute error 2.8e-14
  from nine steps on; the result does not change between 9 and 14 steps on 200007 values.
  For s within about 1e-14 of 2^52 the difference comes out negative (-3.6e-15), so the
  result is clamped at zero. Ten steps are used.

### Predictions (written before the tests are run)

P1 Known answer. The shipped Python twin and the C++ header give the words of
   `numpy.random.Philox` for 10^4 random counters and keys. Refuted by one differing word.

P2 Agreement of implementations. For a table of at least 2 x 10^5 keys (edge cases and
   random keys) the raw words, uniforms, integer indices, normal pairs and directions
   are bit-identical between (a) the processor build, (b) the card build, (c) the Python
   twin, and (d) a standalone compilation of the header with g++ at -O0, at -O3 with
   fused multiply-add allowed (-march=native -ffp-contract=fast) and with it forbidden
   (-ffp-contract=off). Refuted by one differing bit in any column. Most likely place of
   a failure: the square roots and the division of the normal pair on the card, or a
   fused product that I have overlooked.

P3 Statistics (Python twin, 10^7 or more draws per test; large samples in the code on
   the card).
   - Uniform: mean, variance, third and fourth central moments within four standard
     errors of 1/2, 1/12, 0, 1/80; chi-square of 1024 equal bins and of pairs in 64 x 64
     bins with p-values not below 10^-4; frequency of each of the upper 52 bits within
     four standard errors of 1/2.
   - Normal: moments up to the eighth within four standard errors of 0, 1, 0, 3, 0, 15,
     0, 105; counts beyond 3, 4, 5 and 6 standard deviations compatible with Poisson
     expectations; Kolmogorov-Smirnov p-value not below 10^-4; the two members of a pair
     uncorrelated.
   - Direction: mean of each component within four standard errors of 0, second moments
     of delta_ij / 3; chi-square of n_z and of the azimuth flat; |n|^2 - 1 below 4e-16.
   - Correlations: lag-one correlation along each field of the key (seed, stream, entity,
     entity_hi, step, draw), between streams, and between the four words of one call,
     within four standard errors (1/sqrt(N)) of zero.
   - The set of all p-values is compatible with a uniform distribution (Kolmogorov-Smirnov
     p not below 10^-3).
   Refuted by a moment or correlation beyond five standard errors, or a p-value below
   10^-6 (with about 60 tests, one p-value below 10^-4 has probability 0.6 percent).

P4 Cost per draw (order of magnitude; refuted if off by more than a factor three).
   One core of the Xeon 8360Y, serial build at -O2: one generator call (four words)
   10 to 20 ns; a normal pair about 100 ns (ten dependent square roots); a direction
   25 to 30 ns. One A100: 1 to 2 x 10^9 generator calls per second, a normal pair 2 to
   4 ns, a direction 1 to 1.5 ns.

P5 Demonstration in the code.
   D1 (analytic Kerr-Schild metric, `metric = kerr_schild`; the particles do not read the
   mesh): with the kick keyed by tag the final particle states are bit-identical for two
   MeshBlock layouts and for a run restarted halfway, and the per-step checksum of the
   kicks is identical for the layouts, the restart, and between the processor and the card
   builds. Controls: key `block` gives different states for the two layouts; key
   `sequence` gives different states after the restart; another seed gives different
   states. Refuted by any differing bit in the first group or by identical states in a
   control.
   D2 (static Kerr-Schild metric on a uniform mesh, `metric = mesh`): the checksums of
   the kicks are identical for two layouts; the particle states are NOT bit-identical
   between layouts, with or without the kick, because the interpolation forms
   (x - xmin) / dx with the lower edge of the particle's own MeshBlock
   (`nrpic_mesh.hpp:91`), which rounds differently for different edges; I expect relative
   differences between 1e-15 and 1e-9 after a few hundred steps. The restart of one
   layout is bit-identical to the uninterrupted run, also with particles removed at the
   excision threshold. Refuted by bit-identical states across layouts (then the remark
   about the interpolation is wrong) or by a restart that differs.
   Regression: with the kick switched off the modified executable gives byte-identical
   history files and snapshots to the executable built from the unmodified source, on
   processors and on the card.

## 2026-11-15 11:45 UTC  session core-rng  implementation, scouting

Written (uncommitted until the commit that follows this entry): `athenak/src/utils/rng.hpp`,
`python/nrpic/rng.py`, the unit-test problem generator
`athenak/src/pgen/unit_tests/rng_test.cpp` (`pgen_name = rng_test`), the test kick
`athenak/src/particles/nrpic_kick.cpp`, inputs `problems/tests/rng_*.athinput`, and the
drivers under `tracks/core/analysis/rng/`.

Choices made while writing:
- The seed of a run is `<job> rng_seed`, not a block of its own: AthenaK rejects unknown
  block names (`parameter_input.cpp`, `CheckBlockNames`), and a new name would be one
  more line that every branch of this wave edits.
- The options of the kick are read only when `<particles> test_kick` is present, so a run
  without it adds nothing to the parameters stored in restart files.
- On the card the upper half of a 64-bit product is `__umul64hi`; on processors the
  128-bit integer of the compiler; a portable form from 32-bit halves is kept and the
  unit test compares it with the one in use for every key of the table.

Scouting (small, unregistered, in `scratch/core/tmp/rng/`; the registered runs follow):
- Table of 202070 keys, processor build against the Python twin: no differing bit in any
  of the 15 columns; 11682 keys against `numpy.random.Philox`: none differing. The same
  table from a standalone compilation at -O0, -O2, -O3 with and without fused
  multiply-add: identical checksum. One correction to prediction P3: the largest
  deviation of |n|^2 from 1 is 4.44e-16 (two units in the last place), not "below 4e-16";
  the bound I should have written is 1e-15.
- Kick, analytic metric, 2000 particles to t = 20: outcome as predicted (identical bits
  for layouts and restart; the three controls differ). First version of the driver
  compared the number of records of the checksum files, which a restarted run cannot
  match (it records only the cycles after the restart); corrected in the driver.
- Kick, mesh metric, 2000 particles to t = 20: checksums identical for the two layouts;
  states differ by at most 3.6e-14 (positions) and 5.4e-15 (momenta) with the kick, and
  4.0e-14, 5.2e-15 without it; restart identical. The plunging set with L = 0.9 L_circ
  loses no particle before t = 20, so the registered run uses L = 0.3 L_circ, t = 50,
  restart at t = 40 (particle number 2000 -> 1440 at t = 40 -> 176 at t = 50 in a
  scouting run).
- Cost on one core (serial build, 10^6 keys): generator call 28 ns, single uniform
  22 ns, normal pair 93 ns, direction 40 ns.

## 2026-11-15 11:55 UTC  session core-rng  first registered runs, one thing to follow up

Run core-20261115-115230-f0258ce (card, 1e10 keys): the table has the checksum of the
processor table of the scouting run (6527e84f...). Looking at the raw sums before the
analysis script: the second moments of both members of the normal pair are low,
-1.84 and -1.64 standard errors; they are not independent tests (z1^2 + z2^2 = -2 ln s),
and their sum is 2.46 standard errors below 2 N (mean of -ln s = 0.9999754 with standard
error 1.0e-5). One such value among about a hundred statistics is expected, but it is
the one quantity that would show an error of the logarithm or of the rejection step, so
it gets its own test.

Prediction (before the run): with 1e11 keys and another seed (20261116) on the card the
sum of the two second moments is within three standard errors of 2 N (standard error of
the mean of -ln s: 3.2e-6). If the deviation of 2.5e-5 were a bias it would appear as
about eight standard errors; that outcome refutes the claim that the normal draw is
exact to the stated accuracy.

## 2026-11-15 12:04 UTC  session core-rng  outcomes of the first registered runs (commit f0258ce)

(Clock times of the headings of this file were corrected once, at 12:10 UTC, to the times of the commits; no other text was changed.)

- P1 and P2 confirmed. Run core-20261115-115626-f0258ce: the tables of the processor
  build (run core-20261115-115134-f0258ce), of the card build (run
  core-20261115-115230-f0258ce) and of five standalone compilations (-O0; -O2; -O3
  -march=native with and without fused multiply-add; -O2 with the portable 32-bit
  products) have the same sha256 (6527e84f...); the Python twin reproduces all 15 columns
  of the 202070 keys without a differing bit; `numpy.random.Philox` reproduces the words
  of 20902 keys. The binary compiled with fused multiply-add allowed contains one such
  instruction and gives the same table.
- Follow-up of the low second moment (prediction of 11:55): run
  core-20261115-115355-f0258ce, 1e11 keys, seed 20261116: sum of the second moments of
  the pair +0.53 standard errors from 2 N (mean of -ln s = 1.0000017 +- 3.2e-6); single
  members +0.49 and +0.26. The value of -2.46 at 1e10 keys was a fluctuation; no bias at
  the 1e-5 level. Prediction confirmed.
- P5, D1 confirmed on processors, run core-20261115-115701-f0258ce (10000 particles,
  t = 40, 800 steps): key tag: 0 of 10000 particles differ between 1 and 64 MeshBlocks
  and between the uninterrupted and the restarted run, in both kick modes; checksums of
  the kicks identical in 801 (layouts) and 401 (restart) cycles. Controls: key block,
  10000 of 10000 particles differ between the layouts (largest momentum difference
  0.050); key sequence, 10000 differ after the restart (0.029); other seed, 10000 differ.
  Accumulated kick: rms 7.28e-3 against sigma sqrt(t) = 6.32e-3 (ratio 1.15).
- P5, D2 confirmed on processors, run core-20261115-115833-f0258ce (10000 particles):
  checksums identical for 8 and 64 MeshBlocks in 801 cycles; states differ for 9042
  particles by at most 1.2e-13 (positions) and 8.0e-15 (momenta) with the kick, 9048
  particles, 1.1e-13 and 7.8e-15 without it; restart of the plunging set (9073 of 10000
  particles removed by t = 50) bit-identical, checksums identical in 201 cycles.
- P4, card: refuted in the favourable direction. Run core-20261115-115230-f0258ce:
  3.9e10 generator calls per second (0.026 ns per call), normal pair 0.133 ns, direction
  0.043 ns; I had predicted 1 to 2 x 10^9 calls per second, a factor 20 to 40 too slow
  (I underestimated the integer throughput of the card). Processor (run
  core-20261115-115134-f0258ce) to be read from the time file in the summary below.
- Regression (scouting, `scratch/core/tmp/rng/rg0`): five existing set-ups, 36 output
  files, byte-identical between the unmodified and the new processor executable. The
  registered run follows on the final commit.

Added after these runs (not in the plan of 11:30): `athenak/src/utils/rng_mesh.hpp`
(`CellOffsets`, `WrapIndex`) and the part `cell_check` of the unit test, because the
second client of the interface (stochastic sources, track E) keys draws by cells and
needs an entity that does not depend on the MeshBlocks. Scouting
(`scratch/core/tmp/rng/cc1`, before any prediction was written): the checksum per level
is the same for 1, 8 and 64 MeshBlocks on a uniform mesh and equal to the Python twin.
My first expectation for a mesh with two refinement levels was wrong: AthenaK refines
more MeshBlocks than the regions ask for (to keep neighbours within one level), and
which ones depends on the MeshBlock size, so the coarser levels do not hold the same
cells in the two divisions (71 against 309 MeshBlocks). The finest level does, and
agrees. The comparison is therefore made on a mesh with one refined octant (all levels)
and on the finest level of the two-level mesh.

Prediction for the registered cell check (processor and card): per level, the same
number of cells and the same checksum as the Python twin computes from the geometry, in
all seven runs. Refuted by one differing checksum.

## 2026-11-15 12:08 UTC  session core-rng  a bound of mine exceeded

Run core-20261115-120534-5bdb22c (logarithm against mpmath, 202050 values): largest
absolute error 3.004e-14 (at s = 57447), above the "below 3e-14" that I had written into
the header after the scouting sample of 20000 values (2.8e-14). The registered test
therefore failed. The number is a property of ten rounded steps and one quotient of
size up to 58, a few units in the last place, and a sample cannot bound it; the claim in
the header and in the test is restated as "below 1e-13 (largest found 3.0e-14)". Nothing
else changes: 11 of the values next to 2^52 come out negative before the clamp, the
result does not change from ten steps on (0 of 202050 values between 10 and 14 steps),
and the error of the radius sqrt(2 L) is at most 8.4e-8 (for L below 1e-12, probability
1e-12 per draw) and 4.7e-10 relative for L above 1e-6. The test is rerun with the
restated bound; the failed run stays on record.

## 2026-11-15 12:15 UTC  session core-rng  the kick against the Python twin, prediction

Looking at the first figure of the kick demonstration (run core-20261115-120913-564b404):
the accumulated kick of run a1, (u_x with kick minus u_x without) over sigma sqrt(t), is
visibly wider than the normal density (rms ratio 1.15, lower peak, wider wings). That is
the geodesic flow, which shears a momentum kick into later momentum changes, not the
generator; but the panel then shows nothing about the draws. A clean check needs
dynamics that leave the momentum alone: the same set-up with `bh_mass = 0`, where the
analytic metric is flat and the push does not change u_i at all. Then
u_i(end) = u_i(0) + sigma sqrt(dt) * (sum over the cycles of the deviates of this tag),
which the Python twin can evaluate from the keys (seed, stream tests/16, tag, cycle),
draw 0 for the first two components and draw 1 for the third.

Prediction (run f1 added to the analytic case of `run_kick_demo.py`, 10000 particles,
800 steps of 0.05): every momentum component of every particle agrees with the twin to
better than 1e-13 (the code may fuse the product and the sum of the kick, the twin does
not, so identical bits are not promised; the sum has 800 terms of about 2e-4); the
accumulated kick over sigma sqrt(t) has mean within four standard errors of 0 and
variance within four standard errors of 1. Refuted by a larger difference, which would
mean that the keys used inside the particle module are not the ones the interface
document states.

## 2026-11-15 12:25 UTC  session core-rng  statistics: outcome, and one pattern to test

Run core-20261115-120536-5bdb22c (253 tests with a p-value: 81 with the Python twin at
2e7 keys, 60 each from the sums of the code on processors at 2e8 keys, on the card at
1e10 and at 1e11 keys): smallest p-value 1.1e-3, four below 1e-2, none below 1e-3;
largest deviation 3.26 standard errors; the p-values are compatible with a uniform
distribution (Kolmogorov-Smirnov p = 0.61). P3 holds by its own criteria.

But the two largest deviations are of one kind: the covariance of two words of the same
generator call, words 0 and 1 at 1e11 keys (-3.26 standard errors, seed 20261116) and
words 0 and 2 at 1e10 keys (-3.17, seed 20261115); and the pair (0,1) at 1e10 keys was
-1.25, which is what a real correlation of -1e-5 would give at both sizes. Two values
beyond 3.1 among the 15 word-pair statistics of this run have probability 4e-4 by
chance (a few 1e-3 after allowing for my having picked the category afterwards). A
generator of this family with a linear correlation of 1e-5 between output words would
contradict what is published about it [BACKGROUND], so I expect chance, but this is
cheap to settle.

Prediction (before the run): 1e12 generator calls with fourteen new seeds (1001 to 1014,
a standalone program on 14 cores): each of the six covariances between words of a call
within 3.5 standard errors of zero (standard error of the correlation 1e-6). A real
correlation of -1e-5 between words 0 and 1 would show as -10 standard errors and would
refute the independence of the four words, with consequences for Uniform4, the normal
pair and the direction.
