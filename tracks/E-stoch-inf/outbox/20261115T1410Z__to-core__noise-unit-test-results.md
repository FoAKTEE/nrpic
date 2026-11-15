---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-11-22
refs: [run:E-20261115-135523-a32c3a6, run:E-20261115-140502-2957846, run:E-20261115-140553-0b75e1e, tracks/E-stoch-inf/noise/NOISE_SPEC.md]
---
body: Results of the noise unit test on your processor executable
`wt/core-scalar/.work/exe/athena_cpu_836ac86` (sha256 65ff2162...00144), scaled base case
N = 32, nmax2 = 100, 120 cycles (`tracks/E-stoch-inf/analysis/lead/inputs/u_base32.athinput`;
the 64^3 x 300 case costs 95 min per run on the serial processor build):
- frozen tanh (U1, U2, U3, U4, U5a/b, U8): every test passes. A1 exact reconstruction
  from the keys 4.1e-14 of the rms; A11 1, 8 and 64 MeshBlocks bit-identical; A12 restart at
  cycle 60 bit-identical; A13 N = 16 against N = 32 2.4e-15; A15 seeds independent. A1
  passing also confirms your dump convention (request C5): the dump at cycle m holds the
  increment of the step ending at m.
- Markov Heaviside (U7): every test passes.
- Markov tanh (U6): every test passes except A1, 1.07e-10 of the rms against 1e-11. The
  per-mode diagnostic (run E-20261115-140553-0b75e1e, `fig_lu_diag.png`) shows the cause:
  sqrt(W(t) - W(t - dt)) of modes long past crossing, where W is close to 1 and one unit in
  the last place of W (libm exp against numpy exp) is amplified by 1/(2 sqrt(dW)); active
  modes agree to 4e-14 of the base amplitude. Not a key or stage defect.
Requests: (a) form the window increment without cancellation in `NoiseShellFactors`,
dW = 0.5 [tanh(x1) - tanh(x0)] = 0.5 sinh(x1 - x0)/(cosh x1 cosh x0) (the reference will use
the same), so that A1 can be held at 1e-11 for the Markov scheme; (b) the card run U9 once a
card build exists (see the request on the card build); (c) from the earlier requests of
`noise/RNG_REQUIREMENTS.md`: `rng::ModeEntity(nx, ny, nz) = CellEntity(n + 2^20)` in
`utils/rng_mesh.hpp` and the twin, the meaning of stream 3 (bit 16 = modes, lower 16 bits =
degree of freedom) in rng.md section 6, and rule 2 of rng.md for streams shared by initial
data and evolution (epoch ncycle + 1). Smallest acceptable answer: (a) with a commit id.
