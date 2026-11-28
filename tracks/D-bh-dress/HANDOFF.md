# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-27 23:48 PST, lead of batch 40): G0, G1 and G2 SIGNED (G1 and G2 with reservations;
coord/GATES.md). Toward G3 (60 card-hours, 1.52 used): the scope `scope/SCOPE_G3.md` carries amendments A1-A5
(section 11) and a dated note under A1 of this session: the M/16 member of the uniform mesh family (G-16u) does
not fit one card, so the full mesh leg as designed ends and the orchestrator is asked to rule (outbox
`g3-mesh-leg-ruling`, options a-d). The guard test EG8 and the timing runs are read and closed. Owner
D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER`

Files to read first: `STATUS.md`; `scope/SCOPE_G3.md` section 11 (A1-A5 and the note under A1);
`g3/amend/JOURNAL.md` entries 4 (predictions for the amended criteria), 6-7 (timing outcome);
`excguard/JOURNAL.md` entry 4 (EG8 outcome); `stage/REVIEW-wave3.md` section 27; the orchestrator's answer to
`outbox/20261128T074522Z__to-orch__g3-mesh-leg-ruling.md` (inbox).

## Card jobs in flight (check sacct for every job of an entry before reading it)

- q0100 D-G3-G8 (production, chain, cap 3.5), run D-20261128-062142-c5666c4, Slurm job 5632 PENDING at 23:26
  PST. Deck `g3/amend/decks/g3g8.athinput` (core-v0.8, start/stop times of the finder set, diagnostics on,
  polishing 100), to 400 M, about 2.5 card-hours. Output `scratch/D-bh-dress/D-20261128-062142-c5666c4/` (base
  g3g8). When the chain is DONE: `harness/bin/nrpic-run finish D-20261128-062142-c5666c4`, then read it with the
  amended Claim G criteria (SCOPE_G3 section 4 as replaced by A3), which need the vacuum offsets of item 2 below
  first; filter the summary by the status file (eg8_read.py's `filtered_view`).

## What waits, in order

1. The orchestrator's ruling on the mesh leg (no G-16u, G-12u or G-6u entry before it). If (b) is chosen:
   a deck G-6u (root 72, blocks of 18; add it to `g3/amend/tools/make_g3_decks.py`, count blocks with `athena
   -m`), a prediction in g3/amend's journal, then a 2 M card timing run (one job, cap 0.2) before production.
2. Processor work A5 puts before every later member (at most 6 cores): (i) Claim D reader (A2):
   dtau_p = tau_p - tau_LTB(R_p; R0_p) on G2's snapshots (FK, FN4, FNQ, FL16 to 190 M), D1* = twice FN4's largest
   |median dtau| (prediction P-A2, g3/amend entry 4); (ii) polished re-searches of the restart files of V-1L4,
   V-1L, V-1L16 (vacuum offsets at 4, 8, 16 cells per M; core-v0.9 lets `-r` add `fastflow/polish_iterations_0`
   and `diagnostics` from the command line, `scratch/core/exe/core_nrpic_v09/athena_cpu_omp`; whether a v0.9
   executable reads the older restart files is untested: try one first); (iii) G3-G3 power on phase-randomised
   surrogates of FK - FL16 noise (50-190 M) and, once q0100 has run, of G-8's own noise (P-A3).
3. Then, by the ruling: G-12u (9.4 card-hours, cap 11), G-8-4N, G-8-16N (data by flux_tools/esf_data.py at
   lattice h/2.52; check memory), G-8-e1 (shift_eta 1.0); two D chains at most at once; priority 2.

## What this session did (batch 40)

- Closed q0085 (EG8) and q0095 (timing) after sacct; readers committed before they ran; figures looked at.
- EG8: E1, E3-E8 hold; E2 failed at the first bin (band defect). Timing: T-12u held but for its mass band;
  T-16u and P-A1 refuted (memory). Costs: G-8 2.5, G-12u 9.4, G-16u 25.9 (estimate) card-hours to 400 M.
- Note under A1; outbox to orch (ruling) and core (EG8 outcome, memory question); three inbox messages acked;
  rd_checks.py cites kb claim 931 with its hedge. Queued nothing (A5).

## Traps (kept; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12; snapshots carry every particle's proper time after the species array. (7) The finder writes into
`-d`. (8) The finder summary repeats times across restarts: take the LAST record; with diagnostics read the
status file and drop searches not found. (9) Never kill by pattern; never remove files through a path built
from a shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (12) Restart numbers are
not times. (13) `nrpic-run submit` refuses an unclean package: commit first. (16) Horizon excision stops once
the smallest horizon radius exceeds ah_exc_max_growth (4 when absent) x initial_radius_0; G3 uses 4 x 1.6.
(17) The unpolished finder sits up to ~6e-5 off the converged mass. (18) Removal records of preempted
segments: fluxio.drop_overlaps. (20) Judge each mesh against its own-mesh vacuum control. (21) Closes of
40-90 GB chains take 2-10 min. (25) FL16 and V-1L16 end at 299-299.75 M. (26) Close local background runs with
`nrpic-run finish` before reading them. (27) note/main.pdf is 1.1 MB. (28) A serial processor smoke test of an
M/8 ES-FL deck takes ~17 min for two cycles. (30) NEW: AthenaK aligns a refined region to the blocks of the
next coarser level and keeps one block of buffer per level: always count blocks with `athena -m` (g3/amend
tools/check_review.py) before trusting a hierarchy; t = 0 horizon mass of these data is 1 (Schwarzschild),
so the M/8 finder offset is -8.5e-3, M/16 -1.9e-4. (31) use `date` for journal times (sessions write times ahead of the clock). (32) NEW: a
finder summary repeats the last mass for a search not found; drop such rows by the status file before any
criterion (eg8_read.py does). (33) NEW: card memory of the uniform family is about 6.1 GiB + 1696 bytes per cell
(456 blocks with ghost zones): blocks of 36 fit (69 GiB), 48 do not (about 133 GiB); `athena -m` counts blocks,
not bytes.
