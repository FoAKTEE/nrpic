# Plan of wave 3 for D-bh-dress

Written by the planner of each round (decision 0019 item 3). Each round adds a section; earlier
sections are not edited.

## Round 1 (2026-11-20, planner)

### State read at the start (worktree at 78d470ca, main merged)

- G0: package complete for review since wave 2b (stage/G0, every item PASS or NA, VERIFIER.md
  on the plan); not signed in coord/GATES.md. The gate review belongs to the round's reviewer
  step, not to a package.
- G1: NOT met. Open items of stage/G1/CHECKLIST.md: C7 (D-pre-3 profile criterion; the
  proposal `d-pre-3-criterion` of 2026-11-15 is still open at orch in coord/REQUESTS.md),
  C9 (architecture schematic predates core's wave-2 capabilities), C17 (no fresh-context
  verifier of the G1 material).
- ES-1G (core's lapse_leak on the Einstein-Straus data, run D-20261119-142633-6f72922, Slurm
  4636) RAN UNATTENDED on 2026-11-19 07:36-08:24 PST: chain DONE (tlim), cycle 6400. Not
  finished in nrpic-run (manifest says submitted; 0.98 card-hours still reserved), not
  analysed; predictions G1-G7 exist (es_runs/JOURNAL.md entry 5).
- Cut off but complete as far as it went: flux_tools (wave 3a) built the ES-F matter run
  (data, inputs smoke-tested, analysis tested on synthetic runs); no card time was given,
  so no ES-F run exists; its construction is not checked by a second agent.
- Git status clean: no stranded files. squeue: no job of D queued or running (one job of
  another user). Inbox: four info messages (kb annotations and journal data; core's
  threaded processor build, `scratch/core/exe/core_build-openmp/`, answer to
  openmp-cpu-build). No core_nrpic_v04 executable yet; tags core-v0.1 to core-v0.3 only.
- Card-hours (nrpic-run budget): 3.62 used, 0.98 reserved (ES-1G; actual 0.79), 25.40 left of
  30 to the next gate (decision 0014).

### Gate aimed at

G1 (close C7, C9, C17 so that the package is complete for review), with the G2 groundwork
whose prerequisites exist now running beside it: the ES-1G outcome (gauge for the null
test), the cause of the late horizon drift (the null-test floor), the first matter run ES-F
(growth against flux).

### Queue and card time

Two card jobs of D at a time: one slot for `flux_tools`, one for `drift_controls`; every
other package runs on processors (at most 6 cores per session). Caps: flux_tools 3.0,
drift_controls 2.5, all others 0; sum 5.5 card-hours, within the 24.6 left after ES-1G.
No single run above eight card-hours.

### Packages (in order of value toward G1, then G2)

| Key | Goal | Deliverables | Why now | Card cap |
|---|---|---|---|---|
| `es_runs` | close and judge ES-1G (lapse_leak) against its predictions G1-G7 | run finished and verified; es_runs/JOURNAL.md entry 9 with every prediction judged; figs/es1g/ looked at; README with ES-1G results and a [JUDGEMENT] on the gauge for the matter null test | ran unattended; its outcome decides the gauge of every G2 run with dust | 0 |
| `verifier_g1` | fresh-context verifier of the G1 material (C17) | verifier_g1/VERIFIER.md: verdicts on ES-1/V-1, Newtonian-mode D-pre-3, Kerr reference and stationarity, the note's ledger at 78d470ca; own scripts, registered runs | the only G1 item nobody inside the track can close; orch has not assigned one since 2026-11-19 | 0 |
| `secondary_infall` | D-pre-3 toward the self-similar regime (a/a_i = 30, fallback 16) in AthenaK's Newtonian mode on core's threaded processor build | design, prediction, registered run, analysis against the matched shells and the seeded self-similar profile; README paragraph "What D-pre-3 shows" under both wordings | C7 is blocked on a ruling that has not come in five days; the proposal itself names this run as what is needed if the wording stays; the threaded build (2026-11-19) makes it a processor run; also the section-10 test row "self-similar secondary infall" of G2 | 0 |
| `note` | working note v1: wave-2 baselines, ES-1/V-1, redrawn architecture schematic (C9) | schem_architecture and schem_timeline redrawn; new sections and data figures from registered runs; ledger extended; check_manuscript --compile passes; every page read | C9 is open for the schematic alone; the note is v0 of wave 1 | 0 |
| `flux_tools` | ES-F, the first matter run into the hole: growth against the integrated flux (G2 scouting) | second-agent check of the ES-F construction; pre-registered pass criteria (i)-(iii) committed before submission; ES-F run and analysis; V-0 control if time and slot allow; finish script | every prerequisite exists (data, inputs, card executable with the accretion diagnostics, tested analysis); it is the G2 matter criterion | 3.0 |
| `drift_controls` | cause of the late common horizon drift after t ~ 165 M (risk R13), so that the null-test floor can be stated | processor decomposition of the drift from existing outputs; card runs one change each: finder resolution (restart from 150 M), boundary at +-384 M, M/16 at the hole if the cap allows; G2 cost table from MeshBlock counts | the null-test floor (G2 vacuum-bubble criterion) cannot be stated before; the lead decided these controls in wave 2b | 2.5 |

Independence: each package writes only its own directory and tracks/D-bh-dress/runs/. The
verifier reads the note at the pinned commit 78d470ca, not the working copy that `note`
edits; `note` does not cite this round's new results. `drift_controls` and `flux_tools`
read es_runs outputs only.

Fallbacks: if ES-F's construction check fails, flux_tools fixes the data and runs no card
job; if the queue does not let a card run finish, the package leaves a tested finish script
and names the run as pending; if a/a_i = 30 is unaffordable on 6 cores in about 4 hours,
secondary_infall runs the largest a/a_i >= 16 that is; if the restart in drift_controls
does not accept changed finder parameters, it goes to the boundary run first.

Not planned this round, and why: V-1 at M/32 and anything above M/16 (G2 re-costing comes
first, R9); a puncture on the torus (core's list, not built); dressed binaries (G3 and
later); a G2 production run with lapse_leak and the flux diagnostics together (no
executable has both until core's merged release; ES-1G decides the gauge first).

For the lead of this round: acknowledge the four inbox messages; ask orch again for the
ruling `d-pre-3-criterion` and `g1-numbers-errata` (open since 2026-11-15) with the
evidence of `secondary_infall`; copy verifier_g1/VERIFIER.md into stage/G1/ and recollect
G1; list G0 as complete for the gate review.
