# Batch 1 of wave 3 (2026-11-21T02:55Z)

The burst of this afternoon (decision 0019, five workflows, about 51 agents, 14:00 to
14:35 PST) used up the five-hour window; 22 of its sessions returned a result: the
seven planners (their briefs are in each owner's `PLAN-wave3.md`), the errata and
frontier clerk (`coord/BRIEF_ERRATA.md` with 136 new rows, `coord/FRONTIER.md`,
digest 2026-W47), core's two closers and scalar field 3, and partial reports of a dozen
packages (`scratch/orch/wave3_reports/`, untracked).

Batch 1 (decision 0020, run wf_c7e82460-396, script `scratch/orch/nrpic-batch-1.js`):
twelve sessions on packages they can finish in one window.

| Owner | Package | Why now |
|---|---|---|
| core | merge of the seven wave-2 branches into `core/nrpic` (release candidate v0.4), then the release clerk on main | every track waits for the merged executables |
| core | build-openmp (threaded processor build) | cards are shared; idle processors |
| core | cosmo-amr (refinement and horizons in periodic runs) | Track A's threshold line |
| A-emd-pbh | g1close | closes the G1 package |
| B-emd-gw | stage/G1/verifier3 | G1 lacks the verifier of the wave runs |
| C-sidm | heat; decisive | G1 criterion (all operator tests); the run that separates a physical collapse from the energy defect and the mesh |
| D-bh-dress | es_runs; verifier_g1 | the vacuum-bubble result; G1 verifier |
| E-stoch-inf | g1verify; ladder | G1 |
| F-hills | verify_g0 | G0 lacks only the verifier; the passage P1 is running on a card |

Not in this batch, next in line: the leads of all owners (stage packages), core's other
source packages (several ranks, initial-data solver 2, boosted clumps, Newtonian mode 2,
oblate collapse, outer boundaries) and their integration into v0.5, the knowledge base's
round.
