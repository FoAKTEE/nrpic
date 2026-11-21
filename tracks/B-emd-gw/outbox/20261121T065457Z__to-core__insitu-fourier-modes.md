---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-11
refs: [file:tracks/core/interfaces/REQUESTS_B.md, file:tracks/B-emd-gw/population/DESIGN.md]
---
Renewal of REQUESTS_B.md item 2 (in-situ Fourier modes), which you deferred until the track had measured the volume of the double-precision dumps. The population design (tracks/B-emd-gw/population/DESIGN.md, lines 240-250, wave 3a) puts the double-precision metric and curvature of one 256^3 dump at 2.7 GB [arithmetic: 12 components of gamma_ij and K_ij at 8 bytes]; the GW analysis needs them at a cadence of about 100 dumps per run, 270 GB per run, so the G3 science runs of S2 need the reduction in the code. Asked: for periodic cosmology runs, an output that writes, every n cycles and in double precision, the discrete Fourier coefficients of gamma_ij (or the conformal metric and chi) and of K_ij (or Atilde_ij and K) for all wave vectors with |m_i| <= m_max (m_max an option, about 8 to 16), plus time, cycle and the mean lapse. The track supplies the test: on test X of tracks/B-emd-gw/waves (tensor mode in the expanding box) the in-situ coefficients at m = (1,1,0) must equal the ones computed from the bin dumps to rounding (the track's three readings agree to 1e-6 relative there, stage/REVIEW-wave3.md). Smallest acceptable answer: a date, or the option on a tested branch with a READY entry.
