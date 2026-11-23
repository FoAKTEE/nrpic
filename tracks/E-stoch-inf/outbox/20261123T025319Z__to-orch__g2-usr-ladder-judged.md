---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: []
---
The G2 production ladder of Track E (package g2prod, release card build core-v0.6, 7.51
card-hours) has run and is judged against `spec/scope/SCOPE.md` 4c as written
(`g2prod/JOURNAL.md` entry 2; judge run E-20261123-024359-5dc3213; `stage/G2/`).

Results: the release repeats the G1 slow-roll run digit for digit (records identical to
E-20261115-172618-f948386; G1 reservation 2 answered). USR: U-A0..U-A3 and U-A2' pass on all
eight release runs (1.09e-4 per mode, seeds A and B; seed A identical per mode to the scouting
pair), U-R, U-S, U-A4'(c) and the control U-A4'(d) (ratio 1.19e5) pass. U-A4'(a) FAILS at one
of 11 judged dumps of the momentum constraint: even halving 3.925 at cN 6.52 (bar 3.95-4.05);
the Hamiltonian part holds at all 9 dumps. By the definition fixed before the runs, "the USR
case is reproduced" is therefore not met in full.

Requests:
1. Ruling: may the G2 package go to its independent review with U-A4'(a) failed at one dump on
   record (no rewording of the criterion is proposed), or must the cause be settled first? A
   third amplitude (s = +-1/4, two 256^3 chains, about 1.24 card-hours at measured cost) is
   queued behind repro/scope's two card jobs with predictions (g2prod entry 3): it tests whether
   the miss is a higher order in s, which the two-amplitude floor of SCOPE 4c ignores.
2. C2 gauge leg: Track E runs geodesic slicing only, as the reproduced paper does. Is a gauge
   variant required at G2 for the reproduction, or may C2 stand on mesh convergence (U-R) with
   particle number NA and no boundary (periodic box)? A variant would need a lapse option for
   the scalar-field set-up in core.
3. Information: decision 0028's repro sessions share this worktree and the two-job card limit;
   the g2prod sequencer counts every E job, so the s = +-1/4 pair waits for repro's jobs.
