# Wave 3: started 2026-11-20T22:00Z

Waves 2b and 3a ended on 2026-11-19 at the account's usage limit (39 of 65 agents
finished; the watcher's pause at 95 per cent did not take effect: decision 0019 item 1).
Their reports are under `scratch/orch/wave2b_reports/` and `wave3a_reports/`
(untracked), their work in the owners' worktrees and branches, all pushed.
Wave 3 runs as five workflows at once (decision 0019), up to about fifty agents:

| Workflow (run id) | Content |
|---|---|
| core (wf_4152b1a1-a03), script `scratch/orch/nrpic-core-wave-3.js` | merge of the seven wave-2 branches into `core/nrpic` (release candidate core-v0.4) with a release clerk on main; beside it the nine wave-3a source packages continued (threaded build, several ranks, refined periodic runs, initial-data solver 2, scalar field 3, boosted clumps, Newtonian mode 2, oblate collapse, outer boundaries) and two packages closed (collisions-2, requests-adf); each package then merges v0.4 and retests; merge to core-v0.5 with the G2 package and the answers to the tracks' requests; then a planned round of up to eight source items in the spare worktrees `wt/core-s1` to `-s8` (core-v0.6) |
| rounds A, B (wf_4a57cb66-4e6) | two rounds each of planner, up to six helpers, lead, gate review |
| rounds C, D (wf_25ee3bde-a65) | the same |
| rounds E, F (wf_fee3d131-143) | the same |
| rounds kb, and two clerks on main (wf_390116db-6ef) | knowledge base in rounds; errata and frontier clerk (results of the brief check into `coord/BRIEF_ERRATA.md`, `coord/FRONTIER.md`, digest 2026-W47); harness (hook after installation, waivers, usage self-test, board and requests) |

Script of the rounds: `scratch/orch/nrpic-rounds.js` (owners and rounds are arguments).
Usage: `harness/bin/nrpic-usage watch` and `resume` run beside the workflows; at 95 per
cent of the weekly or the five-hour window the flag `locks/PAUSE` makes every agent wind
down; after the reset the same scripts are started again and continue from the
worktrees. At the start: weekly 51 per cent (window resets 2026-11-20 15:00 PST),
five-hour 2 per cent.
