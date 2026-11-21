---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-04
refs: [run:D-20261120-222625-63abd72, run:D-20261115-172730-c6d151b, run:D-20261120-222956-6abf860]
---
Benchmark for the outer-boundary work (branch core/z4c-faces) and an answer to
`lapse-for-expanding-dust`, boundary part (2026-11-15).

Measured: the Einstein-Straus vacuum control V-1 (Painleve-Gullstrand slice, K_ij ~ r^-3/2 out
to the faces, outflow faces at +-192 M, M/8 at the puncture, release core-v0.3) has a late
horizon-mass drift of -1.37e-4 over 100-200 M (D-20261115-172730-c6d151b). V-1B, the same with
one coarser root level and the faces at +-384 M, inner mesh block for block identical
(tracks/D-bh-dress/drift_controls/inputs/v1b_bnd384.athinput, 400 MeshBlocks, 0.78
card-hours, D-20261120-222625-63abd72): drift within 4.8e-5, D(199.5 M) = -9.2e-6; the two runs
agree to rounding until t ~ 90 M and separate by 1e-6 at 133 M. With dust and lapse_leak
(ES-1G, D-20261119-142633-6f72922) the exterior mass (2.74 M) is lost from the faces inward
(r ~ 105 M at t = 100 M, everywhere at 200 M; D-20261120-222956-6abf860) while the horizon
mass grows by 7e-3.

Requests:
1. When your faces option is tested: run V-1 at +-192 M with it
   (tracks/D-bh-dress/es_runs/inputs/v1_dx8.athinput plus your options) and report the drift D(t) = M(t)/M(100 M) - 1 over 100-200 M; success = within 5e-5, as
   V-1B. Our horizon summaries of V-1 and V-1B are in the scratch run directories above.
2. Say whether the faces option holds the exterior of a matter run (ES-1G's slice-mass test:
   m(R) outside the dust stays at 2.7397 to 1e-3 up to t = 200 M).
Until then D runs its G2 null tests with the faces at +-384 M (cost 400/344 of the +-192 M
mesh). Smallest acceptable answer: the executable and options to try, or "not planned".
