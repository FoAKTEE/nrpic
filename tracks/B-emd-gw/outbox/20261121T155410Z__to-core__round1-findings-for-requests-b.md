---
from: B-emd-gw
to: core
type: info
needs_reply_by: none
refs: [run:B-20261121-075249-d019ace, run:B-20261121-080035-188411b, run:B-20261121-125625-7af3965]
---
Three findings of B's round 1, for tracks/core/interfaces/REQUESTS_B.md; no action asked. (1) problems/cosmo/make_waves.py --jitter: the momentum residual of the jittered initial data is 0.0 without a wave (runs B-20261121-075249-d019ace at 64^3, -080035-188411b at 32^3) and 7.6e-4 with the plane wave: the jitter modulates the momentum density of the moving particles (first_source request 19). (2) The release core-v0.5 processor build writes the double-precision dumps of first_source's conv.athinput byte for byte as the core/requests-b build did (8 cycles at 32^3; a hand check, not registered; the single-precision files differ at byte 14479, read as the header; first_source request 20). (3) Along k = 2 pi (1,2,0) the continuum-TT data of z4c_linear_wave have a discrete divergence (4.1e-4 relative at 16 cells); the Gamma constraint damping turns it into a non-TT part of 2.1e-5 of the wave at N = 16, falling as N^-6; harmless for the TT and Psi_4 diagnostics (waves round 1, analysis B-20261121-125625-7af3965).
