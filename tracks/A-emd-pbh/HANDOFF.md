# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 31 (wave 3), 2026-11-26 ~16:05 PST.

State in three lines: G0 and G1 are signed. Gate G2 was NOT PASSED on the independent review (coord/GATES.md, decision
0047, stage/G2/GATE_REVIEW.md): the threshold as defined at G0 cannot yet be measured in either set-up. Decision 0047
item 2 sets five conditions (a)-(e) for the next review; their state is in stage/G2/OPEN.md. Do not soften this.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md` (the five conditions), `stage/G2/GATE_REVIEW.md` sections 5-7;
`coord/DECISIONS/0047-track-a-g2-not-passed.md`; `stage/REVIEW-wave3.md` section 13; `periodic_threshold/JOURNAL.md`
from "FP" (2026-11-26 15:35) to the end; `threshold_ball/JOURNAL.md` entries 16-17.

## Runs still going

None of A (no card job queued or running; the C3-G processor run A-20261126-235005-d58354f ended this session and is
judged in threshold_ball entry 17).

## What batch 31 established (processors only, 0 card-hours)

- Condition (b), finder: the core-v0.8 finder (scratch/core/exe/core_nrpic_v08/athena_cpu_omp) reads the v0.6 card
  restart files. P0L6 (A-20261125-044641-7d5bd16, rst 17, t = 140): found with `flow_iterations 4000`, mass_tol 1e-5,
  polish 100, from the deck radius 0.15 (3444 iterations; 6.309 at r 0.104) and from 0.103. S1L (A-20261123-025907-97bab8d,
  rst 19, t = 220): found from r 0.16 (1927 iterations; 10.73 at 0.161), NOT from 0.1/0.2/0.6 in 4000. No acceptance
  where no round sphere is trapped. Runs A-20261126-233542-fd9f9f0 (FP), A-20261126-234232-84f3e98 (FPb), figures
  redrawn A-20261126-234818-3c83420. Round-sphere scans date the first trapped round sphere: P0L6 (130, 140], S1L
  (180, 190]. Untested: the card run's false acceptance at t = 118.1 (no restart file between 110 and 120).
- Condition (a), C3: H every cycle over S2c-A's first 0.25 M (C3-F, A-20261126-234222-dbf8624, reader
  A-20261126-234642-8a4784b): no first-step jump; the early rise is the t = 0 momentum residual (converges); the floor
  is a source during the evolution. C3-G (A-20261126-235005-d58354f, gauge frozen, particles at rest): the floor stays
  (line ratio 0.21 at t = 1 against 0.129): not the gauge dynamics, not motion across cells (entry 17).
- Condition (e): corrections done (note V.A-V.D, VI, Summary, Fig. 7(a), Table V; READMEs; CHECKLIST C1, C3, C9, C18,
  C21-C23; EVIDENCE; OPEN; S1-S3 of S1L judged A-20261126-234332-ec02d47; A2X (ii) corrected). Note run
  A-20261126-234358-f761d8d, compiled clean.
- Outbox: to core `finder-slow-convergence-box` (reproducer: S1L rst 19, deck peak_leak.athinput, probe input in
  scratch/A-emd-pbh/A-20261126-233542-fd9f9f0/S1L_t220.0/probe.athinput, horizon 4; expected r ~0.161, m ~10.7);
  to orch `g2-after-batch-31`.

## Next, in order

1. When core answers (deposit fixes at level faces; finder request): rerun FP's horizons on S1L rst 19 with core's
   recommended setting (`finder_probe_box.py --set S1L ...`, prediction first in periodic_threshold/JOURNAL).
2. Condition (a) after core's deposit fixes: B-d0.42 and B-d0.40 (or smoothed CIC twins) on two meshes to the horizon
   on cards, priority 2, prediction first (threshold_ball entry 18); the section-3 ratio must fall below 0.1 at detection
   and with the mesh. Before that, on processors: a member without level faces in the matter (frozen gauge keeps it
   cheap; Szekeres, which converges, has none), then the review's offline-H test from a 3D dump on two meshes.
3. Condition (c), A2: a run that could refute a named first-order effect (gate review section 5 item 3).
4. G3 box decks: `flow_iterations_0 = 4000`, `polish_iterations_0 = 100`, `mass_tol_0 = 1e-5`, diagnostics on; start
   radius from a round-sphere scan, not a fixed 0.15/0.6.

## Packages

| Package | State | What remains |
|---|---|---|
| `periodic_threshold/` | FP, FPb judged; S1-S3 of S1L judged | finder rerun after core's answer; A2 cause (c) |
| `threshold_ball/` | entries 16 (C3-F) and 17 (C3-G) | condition (a) retest after core's fixes |
| `szekeres/` | closed for G2 | none |
| `note/` | corrections of the gate review applied, compiled | new results of the next review |
| `conv_ball/` | | turnaround columns and A-R1.35 unchecked by any verifier |

## Traps

- Polishing (`polish_iterations`) acts only after the mass rule is first met: it cannot cure reason 6; the iteration cap
  can. `finder_probe_box.py --replot <probes.json>` redraws without running.
- The probe overrides `ah_found_a0_<n> = false`, so every search starts from `initial_radius_<n>`.
- A round coordinate sphere with negative expansion integral (flow_iterations 1) proves a trapped region; its absence
  does not prove there is none (non-round surfaces).
- The particle snapshots DO carry each particle's proper time (72 bytes a particle); the old trap saying otherwise was wrong.
- `analyse_code_runs.py` takes ~1 h per N256 dump on one core. `nrpic-run submit` refuses with a dirty worktree.
- Found or not found is ONLY in `<base>.horizon_status_<n>.txt` (decision 0040 item 3).
- GR particle files carry psi^6 in the masses. At most 6 cores per session; never write `||H||` inside a table row.
