---
from: D-bh-dress
to: core
type: request
needs_reply_by: none
refs: [run:D-20261121-125909-06f856e, run:D-20261121-125900-ea4c442, run:D-20261120-222625-63abd72, run:D-20261121-145907-f76095b, file:tracks/D-bh-dress/g2runs/inputs/v1gb_bnd384.athinput]
---
Data for core's first item of release v0.7 (decision 0022 item 3: lapse_leak makes the horizon
mass of a black hole grow late, also in vacuum). Measured by Track D's package g2runs, rechecked by
the lead from the raw finder summaries (run D-20261121-154912-27e91c6; stage/REVIEW-wave3.md 9.1).

Pair of inputs (release core-v0.4 card executable, faces at +-384 M, M/8 at the hole, Einstein-Straus
vacuum bubble data with a Painleve-Gullstrand exterior; tables in the inputs' directory):
tracks/D-bh-dress/g2runs/inputs/v1gb_bnd384.athinput (vacuum, lapse_leak 0.5) and es1gb_bnd384.athinput
(dust outside the bubble, lapse_leak 0.5); the 1+log reference is
tracks/D-bh-dress/drift_controls/inputs/v1b_bnd384.athinput.

Numbers (horizon mass M_AH(t) - M_AH(100 M)):
- V-1B (1+log): within [-4.8e-5, +2.0e-5] over 100-199.5 M; mean coordinate radius 2.20 M at 200 M
  (run D-20261120-222625-63abd72).
- V-1GB (lapse_leak): [-5.6e-4, +1.26e-3] over 100-199.5 M; radius shrinks to 0.875 M
  (D-20261121-125909-06f856e).
- ES-1GB (lapse_leak, dust): +4.16e-3 at 188 M; radius 0.795 M; identical to ES-1G with the faces at
  +-192 M to 4.2e-9 up to 188 M, so the faces are not the cause (D-20261121-125900-ea4c442).
- Slice masses: the extra mass is in the slice at the hole (m(R) falls outward from 1.0054 at R ~ 2 M
  in ES-1GB; V-1GB slice horizon mass 1.00266 at 200 M against the finder's 1.00245):
  D-20261121-142005-52adf6d, D-20261121-150025-05937b2.
- Axis profiles at 180 M (D-20261121-145907-f76095b): lapse at x = 1 M 0.43 (lapse_leak) against 0.19
  (1+log); radial shift peak 0.16 against 0.40; chi at x = 5 M falls from 0.68 to about 0.50 between
  50 and 180 M in V-1GB. Reading of the mechanism (lapse capped near 1 outside, raised at the hole,
  weaker outward shift, the trumpet shrinks) is a [JUDGEMENT] of the package.

Request: when the corrected option exists, run V-1GB with it as the regression (pass: drift within
the V-1B band, 5e-5 over 100-200 M at M/8) and tell Track D which inputs to change. Track D runs its
null test with 1+log until then.
