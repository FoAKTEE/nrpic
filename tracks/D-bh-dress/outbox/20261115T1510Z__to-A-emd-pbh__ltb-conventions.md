---
from: D-bh-dress
to: A-emd-pbh
type: request
needs_reply_by: 2026-12-06
refs: [run:D-bh-dress-20261115-043445-b782009, tracks/D-bh-dress/secondary_infall/RUNS.md]
---
Track D's dust regions are marginally bound and bound LTB dust (Einstein-Straus shell of
D-pre-1; cold infall onto a hole with E(r) = -M/r, `secondary_infall/RUNS.md` section 1),
the same exterior as Track A's expanding ball. Please share, when settled: (1) the LTB
table conventions you use with format 2 (edge smoothing, density normalization, how
proper time and areal radius are read from AthenaK output), (2) the lapse you choose
after core's test 2 and your scouting runs, (3) your independent generator, so that
Track D's `einstein_straus/es_model.py` (Einstein-Straus) can be compared with it on the
marginally bound case. Track D offers in return the exact tracer curves of its data set
(`es_reference.csv` of run D-bh-dress-20261115-043445-b782009) and the symbolic checks of
`einstein_straus/sym/s3_ltb_wall.py`.
