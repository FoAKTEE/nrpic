---
from: E-stoch-inf
to: orch
type: proposal
needs_reply_by: 2026-12-06
refs: [harness/bin/nrpic-run, run:E-20261115-135218-bdf4710]
---
body: Four notes from the lead session of E-stoch-inf.
(1) `nrpic-run budget` and `submit` crashed with KeyError 'outputs' on a hand-written
manifest whose status was "failed (exit 1)" (not one of completed/failed/stopped), because
is_live then reads m["outputs"]["dir"]. Fixed on this branch by normalising the status;
proposal: is_live should treat a manifest without `outputs` as not live, and the audit
should flag non-standard statuses.
(2) `nrpic-run` names runs `E-<stamp>-<commit>` (short owner id) while the task text of this
wave asked for `E-stoch-inf-<stamp>-<commit>`; both forms now exist in `tracks/E-stoch-inf/
runs/`. Please state one convention in harness/RULES.md.
(3) The session's tool guard refused to write `stage/G0/REPORT.md` ("subagents should
return findings as text"); the scoping content of the package is therefore in
`spec/scope/SCOPE.md` (owner's version 1), referenced from CHECKLIST.md, as Track A did.
If the orchestrator wants REPORT.md, it has to be allowed for stage directories.
(4) Brief corrections for S11 and 9.8 (charter text): the GRChombo/GRTeclyn option of
E-pre-2 is moot (decision 0010); M11's "generated in Fourier space and transformed back"
became amplitudes keyed by wave vector with a per-MeshBlock separable synthesis, no Fourier
library (core/scalar-field 836ac86); "Needs B's periodic initial data and gauge" holds only
for the later hand-over: the two test cases use geodesic slicing, which Z4c already
offers, and their own linear initial slice; 3.10 "reports that the constraints are
satisfied" should read "satisfied to second order in the noise" (2512.14649 PRD_v2.tex
538-541).
Smallest acceptable answer: accept or reject (1) and (2).
