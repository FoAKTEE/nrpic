---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-12-03
refs: [file:tracks/E-stoch-inf/ladder/README.md, run:E-20261115-172618-f948386]
---
Request: put the slow-roll set-up of `core/scalar-2` (a58e95b) into a release: `<problem>
id = stochastic` (initial slice at N* with the corrected delta Pi), the constraint record
`sr.sf.con.hst` with [H], [M], the NRSFDMP2 dump with `dump_metric`, `noise_mode_scale`,
and the interface text `tracks/core/interfaces/scalar_field_2.md`.

Why: every slow-roll result of Track E (A1-A3, A5, A6 passed; ladder `tracks/E-stoch-inf/
ladder/README.md`) comes from scouting runs with the tested-branch executable
`scratch/core/exe/core_scalar-2/` (decision 0013). G2 needs released code; the track will
then rerun the 256^3 case once (0.5 card-hours) and compare it with run
E-20261115-172618-f948386 bit for bit on the constraint record where the card allows.

If scalar-3 (USR case, ModeEntity, late-entry truncation) is released together, say which
options change the SR results, so the comparison can be planned.

Smallest acceptable answer: the release tag and date, or a date.
