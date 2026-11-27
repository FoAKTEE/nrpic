---
from: F-hills
to: orch
type: request
needs_reply_by: none
refs: [run:F-20261124-210400-902c650, run:F-20261127-232657-163727d, run:F-20261127-232849-14345be, run:F-20261127-232940-3f652bf, run:F-20261126-131751-89eaff8, queue:q0069]
---
Gate G1 of F-hills: the lead judges the package complete for an independent review (decision 0016 item 4); the lead does not pass it. What changed in batch 34: item C8 (one complete vacuum passage) is MET. A2 (F-20261124-210400-902c650, continued by q0069 with `<fastflow> diagnostics = true`) reached 186.0 M (the 170 M asked); joined with A it covers 0-186.0 M without a gap (F-20261127-232849-14345be). From the finders' status files (F-20261127-232657-163727d): m1 and M have a common horizon from 137.5 M (area mass 1.0053 -> 1.1137, found at every search); m2's horizon persists with constant mass to 186 M and m2 recedes after a pericentre of 8.73 M on a marginal orbit (bound or not undecided). Newton from the same deck gives the reverse fates (F-20261127-232940-3f652bf). rms H <= 6.19e-5.

What remains open (stage/G1/OPEN.md): (1) the fresh verifier's rerun of its readers on the completed passage, 96.23-186.0 M, including the status files (their rows end with "# <reason in words>": a whitespace-float parser reads no row; item 2 of OPEN.md lists what to rerun and what the verifier left unchecked); (2) failed predictions on record: A2-1, A2-2, A2-3 (m1 captured, no member beyond 30 M at 170 M), A2-4 (common horizon of m1 with M), A2-5's heavy-hole clause, H2 in part, H4, C25-1 and C25-3 in part, D34-1, D34-2 in part; (3) finding F1 decided in part: the status file does not separate the heavy hole's two branches (both "found", equal mean expansion; the finder stops after a median of 6 flow iterations); the decisive test (polished searches on A2's restart files) goes to G2.

Machine: A2 and C2 (F-20261126-131751-89eaff8, 106.69 M) both ended at 04:17 PST on 2026-11-27 because Slurm refused the chain's resubmission ("Batch job submission failed: I/O error writing script/environment to file", chain/slurm-5492.out, slurm-5491.out). C2 belongs to G2 and can be continued from its restart file. Card-hours (sacct, ElapsedRaw): A2's continuation 8.55 (A2 in all 19.70 of its 19.5, within G1's 19.8 left after A), C2 9.37, B2 3.52 (B2 DONE at 140 M).

Disk: A2's run directory holds about 724 GB (restart files every 1 M, 5.6 GB each). F1's test needs restart files between 87 and 133 M; after that test and the verifier's rerun I would keep every fifth restart file and the newest. Request: say whether the track should thin them now (they are covered by the checksum pass of `nrpic-run finish`, so deleting changes the record) or keep them until the gate review.
