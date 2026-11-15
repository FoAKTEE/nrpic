---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-11-22
refs: [arXiv:2502.06783, arXiv:2512.14649, run:E-stoch-inf-20261115-123146-82d2fd4, run:E-stoch-inf-20261115-122806-ef0d039]
---
body: The scalar field on `core/scalar-field` (836ac86) has the kicks, the window and the
lockstep mode functions, but the problem generator offers only `wave`, `flrw` and
`plane`. Track E's G1 (the slow-roll case of arXiv:2512.14649) needs the initial slice at
N*: background (X_b = a*^-2 = 1, gt = delta, K_b = -3 H*, At = 0) plus the linear
geodesic-gauge perturbations of the coarse-grained amplitudes R^> = W(t*) R_k alpha_k,
dot R^> = d(W R)/dt at t*, with the **corrected** delta Pi of
`tracks/E-stoch-inf/spec/SPEC.md` section 5.3 (the printed eq. 17 of 2502.06783 drops a
term: linear Hamiltonian residual 4 eps1^2 H^3 a^2 k^-2 dot R otherwise, run
E-stoch-inf-20261115-123146-82d2fd4). Synthesis through the same per-MeshBlock sums and
the same alpha_n (frozen, epoch 0) as the noise, so the slice and the sources share one
realisation (DESIGN_REVIEW 6.3).

Smallest acceptable answer: a problem-generator id (for example `id = stochastic`) that
reads the background state and the mode file (`|n|^2 Re R Im R Re dR/dtau Im dR/dtau`,
the format `noise_mode_file` already reads) and writes the slice; plus a test that the
linearised H and M of the slice vanish at first order (the same test with the printed
delta Pi must fail at first order). Track E supplies the mode files and background states
of both cases from its reference (`spec/ref/ms_reference.py`) on request, in code units
(G = 1, SPEC 2.5), and checks the slice against the reference per mode.
