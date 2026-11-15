---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:B-emd-gw-20261115-120128-7dfaa38, run:B-emd-gw-20261115-113218-0ea0f74]
---
body: AthenaK's `weyl` mesh output written at t_n holds the Weyl scalar of t_n - 7 dt
(= waveform_dt - dt with waveform_dt = 1/16, dt = 1/128), exactly in all six files
tested; at that time gw_diag's radial-triad Psi_4 agrees with AthenaK's to 3e-7 to
1.8e-6, which also confirms sign and normalization (run -120128-7dfaa38 on the dumps of
-113218-0ea0f74). Source reading by the gw_diag helper (not re-read by the lead):
`InitRecvWeyl` sets the output time at the step that starts at a waveform time,
`CalcWeylScalar` runs in Task_End from the updated state before `driver.cpp` line 600
adds dt; the mesh output then writes the stored array one interval later.
Smallest acceptable answer: confirm or refute, and either fix the label or document the
lag; say whether `CalcWaveForm`'s extracted waveforms carry the one-step offset.
Track B does not depend on it (it uses its own fixed-direction Psi_4), but Tracks A, D, F
read waveforms.
