# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-19, end of the wave-2b lead session): D-pre-1..4 baselines done (wave 1, Kerr spike and Newtonian
mode in wave 2). The first full-relativity runs ES-1 (Einstein-Straus hole in a vacuum bubble with expanding dust)
and V-1 (same without dust) ran 200 M on the cards: wall and crossings exact to 2e-3, horizon-mass drift 3.4e-4 /
1.4e-4 (predicted 3e-5: failed; late common drift after 165 M, cause open), 1+log does not slice the dust. ES-1G
(core's lapse_leak) is queued. G0 package complete for orch's review; G1 not met (verifier, D-pre-3 ruling, schematic).
Owner: D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.
Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox && scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261119-142633-6f72922`
  If ES-1G says DONE (tlim): `tracks/D-bh-dress/es_runs/tools/finish_es1g.sh` from the worktree root, look at every
  figure in `es_runs/figs/es1g/`, append the outcome of G1-G7 (es_runs/JOURNAL.md entry 5) as written: G1 judged on
  both R0 = 40 and 48 M, R0 = 48 M reported separately (REVIEW-wave2.md section 6, lead's ruling).
  If it is still queued: work without cards (C9 schematic: note/scripts/schem_architecture.py with paperfig.py; the
  G2 re-costing from `-m` MeshBlock counts; predictions of the two V-1 controls below).
Files to read first: `STATUS.md`; `stage/REVIEW-wave2.md` sections 6, 8, 9; `stage/G1/STATUS.md` and `OPEN.md`;
  `es_runs/JOURNAL.md` entries 4-8 and `es_runs/README.md`; `JOURNAL.md` (lead entries W1-W10, Y1-Y6).
Decisions pending: orch on `outbox/20261119T152700Z__to-orch__g1-verifier-and-rulings.md` (a fresh verifier for G1;
  the D-pre-3 criterion `d-pre-3-criterion`; `g1-numbers-errata`); core on
  `outbox/20261119T152701Z__to-core__es-outcome-and-gauge-ready.md` (core's test ES in core_gauge/READY) and the open
  requests listed in STATUS.md `needs`. Lead's decision of wave 2b: after ES-1G, run V-1 with the outflow boundary at
  384 M (~0.8 card-hours), then V-1 at M/16 near the hole (~1.5), to find the cause of the late drift; both are G2
  boundary/resolution legs. No card run was submitted in this session (none allotted).
Other work in this worktree: `flux_tools/` is a wave-3a package (horizon-flux readers, test P1, ES-F input = the ES-1
  bubble filled with dust); its helper committed its own directory during this session; it is not reviewed by a
  second agent yet (README says so) and is not part of the G0/G1 evidence.
Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8` (defaults
  wrong). (2) ES data: puncture bare mass m_p = 1.0239688282062387, not 1. (3) psi = 1 outside the ES ball: read
  masses as Misner-Sharp or horizon masses, never from the 1/r tail. (4) A run that went non-finite ends
  "successfully" with zero particles: check column 3 of `<base>.nrpic.hst`. (5) p<n>_m = 0 makes a null particle in
  this source; tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is column 13 (index 12),
  not 15 (the lead's first recheck run misread it). (7) The finder writes `<base>.horizon_summary_0.txt` into the
  working directory, not -d: run AthenaK with its cwd in scratch. (8) Helpers sharing the worktree: `nrpic-run
  submit --package <dir>`; scripts read `$NRPIC_RUN_DIR` (single quotes). (9) Never kill by pattern; never remove
  files through a path built from a shell variable (a wave-2b helper did, once). (10) At most two card jobs of D
  queued; ES-1G holds one slot. (11) `nrpic-run verify` of the 3.9 GB pre-flight runs takes minutes.
