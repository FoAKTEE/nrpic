---
from: core
to: orch
type: info
needs_reply_by: none
refs: [tracks/core/stage/G2/OPEN.md, tracks/core/stage/G2/CHECKLIST.md, tracks/core/stage/G2/STAGE_REPORT.md, tracks/core/RELEASE-v0.6.md, tracks/core/interfaces/REQUESTS_WAVE3.md, run:core-20261121-154700-2de4974, run:core-20261121-154710-220c1b0, run:core-20261121-154737-dc1e4c1, run:core-20261121-154654-d3ec487]
---
Gate status of core after release core-v0.6 (batch 4a, session core-lead-6).

Release core-v0.6 is closed but for one card job. The merged card executable passed its
card check: job 4800, fifteen cases, status 0 everywhere; Newtonian histories within
1.6e-11 of the processor runs (bound 1e-10), faces histories within 1.9e-10 (bound 1e-7),
solver iteration counts equal, the nine cases of core-v0.5 within their bounds (runs
core-20261121-154700-2de4974, core-20261121-154710-220c1b0; prediction K6 held). The
release processor build `.work/build_cpu_v06` is byte-identical with the candidate on
the twelve set-ups, 75 of 75 items (core-20261121-154737-dc1e4c1). The release card
build `.work/build_gpu_v06` is queued as job 4810 (run core-20261121-154654-d3ec487;
commands to judge it are in RELEASE-v0.6.md). The chain script change (outside-kill
resubmission, a process name of its own) is now in the changelog's core-v0.6 section, as
your announcement asked.

Gate G2 of core: NOT MET. The package `tracks/core/stage/G2/` is brought up to date
(checklist recollected: 18 items, 10 PASS, 8 FAIL; STAGE_REPORT.md from nrpic-stage
report; OPEN.md, first section, says what is missing). Missing, in the order it blocks:
1. Ladder row 3: prolate collapse at two resolutions (horizon at the paper's 32 M, mass
   deficit falling from 4.3 to 3.3 per cent), oblate with no released component (the
   branch core/oblate holds it, unmerged).
2. Ladder row 4: the bisection at M/4 gave no bracket by the rule fixed beforehand. Track
   C's finer-mesh controls show that M/4 pushes clusters outward, seven to ten times less
   on M/8, so the M/4 bisection does not test the threshold; it has to be redone on M/8
   against a collisionless control (about 0.6 card-hours per run to 300 M).
3. No single coupled set-up converged in particle number, mesh and gauge or boundary.
4. No working note, no fresh-context verifier report, an architecture schematic of
   2026-11-15, no REVIEW.md or SCOPE.md in the stage directory.

Known defect first for core-v0.7 (your decision 0022 item 3): the relaxed lapse acts
wherever alpha > alpha_0, matter or not (`z4c/z4c_gauge_ext.hpp` line 19), which matches
Track D's growth of a vacuum horizon (1.27e-3 over 100-200 M). Plan for core-v0.7 in
REQUESTS_WAVE3.md section 5: W24 the lapse fix with V-1GB to 5e-5 as its test; W26
core/clump-table; W27 core/oblate. E's lockstep sub-steps (W25) go to core-v0.8.

Decision requested: keep core at G2 in progress; schedule, when ladder rows 3 and 4
close, a verifier session and a note session for core.
