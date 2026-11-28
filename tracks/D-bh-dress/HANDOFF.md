# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-28 08:43 PST, lead of batch 41): G0, G1 and G2 SIGNED (G1 and G2 with reservations;
coord/GATES.md). Toward G3 (60 card-hours, 3.72 used): the scope `scope/SCOPE_G3.md` carries amendments A1-A6
(section 11). A6 (this session) carries out decision 0051 item 3: the mesh leg is G-8 and G-12u; a coarser G-6u
only if its search at t = 0 is found, and on processors it is not (reason 6), so G-6u is not run and the mesh
error will be |e-bar_8 - e-bar_12| with no order, FL16 beside it. G-8 (the first production member) is read:
G3-G1 holds. core-v0.9 reproduces core-v0.8 byte for byte on the G-8 deck: new members run on core-v0.9.
Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER`

Files to read first: `STATUS.md`; `scope/SCOPE_G3.md` section 11, amendment A6 (the last one); `g3/amend/JOURNAL.md`
entries 8-13 (predictions and outcomes of this session); `stage/REVIEW-wave3.md` section 28; the orchestrator's
answer to `outbox/20261128T162656Z__to-orch__g3-mesh-leg-m6-not-qualified.md` (inbox).

## Card entries in the shared queue (none in Slurm at 08:43 PST; check sacct of every job before reading)

- q0110 D-T6u (batch, one job, cap 0.2, core-v0.9 card build): `g3/amend/decks/timing6.list` (member t6u, deck
  `g3g6u_t2`, G-6u to 2 M). The ruling's literal test of Q1. Read: the first row of `t6u/g3g6u.horizon_status_0.txt`
  (found or not, reason, area mass) against g3/amend entry 10 (prediction: not found, as K2 on processors; if it IS
  found, A6 then needs Q2: queue the null pair `n6es`, `n6v` as chains, cap 1.2 each), the block count and peak
  memory in its log, seconds per M (timing_read.py's method). Close with `nrpic-run finish` first.
- q0111 D-G3-G12u (chain, cap 11, production, core-v0.9): deck `g3/amend/decks/g3g12u.athinput` (M/12 uniform,
  456 blocks of 36, to 400 M; about 9.4 card-hours, several days of queue). Read when chain/STATUS is DONE with
  g8_read.py's method (a copy with base g3g12u) against g3/amend entry 10 and SCOPE_G3 A3/A6: G3-G1 bins; e-bar_12
  against e-bar_8 per 50 M window (no order); the lead; NO criterion read before the processor work below is
  committed (A6).

- q0112 D-G3-G8-4N (chain, cap 4, production, core-v0.9): deck `g3/amend/decks/g3g84n.athinput` (M/8, 4N dust,
  to 400 M; prediction [2.6, 4.0] card-hours, entry 11; smoke test held for blocks, memory 31.4 GiB on processors,
  t = 0 mass, entry 13). Read with g8_read.py's method (base g3g84n, its own data dir D-20261124-130942-29c5de2 for
  labels and growth) for G3-G1 and against G-8 for G3-G4 (needs 16N for the ordering; until then a measured N - 4N
  difference, not a criterion).

## What waits, in order

1. (done this session: leg smoke tests, entry 13.) G-8-e1 (`decks/g3g8e1.athinput`, smoke test held) goes to the
   queue when one of the two D chains (q0111, q0112) ends: chain, cap 3.5, production, core-v0.9, priority 2,
   prediction first (G3-E1 as amended by A4 S6).
2. Processor work of A5/A6 before any G-12u criterion is read (at most 6 cores): (i) Claim D reader (A2):
   dtau_p = tau_p - tau_LTB(R_p; R0_p) on G2's snapshots (FK, FN4, FNQ, FL16 to 190 M), D1* = twice FN4's largest
   |median dtau| (prediction P-A2, g3/amend entry 4); the same reader gives the per-particle lead that replaces the
   verifier's three tracer values in g8_read.py; (ii) polished re-searches of the restart files of V-1L4, V-1L,
   V-1L16 (vacuum offsets at 4, 8, 16 cells per M; core-v0.9 lets `-r` add `fastflow/polish_iterations_0` and
   `diagnostics`: `scratch/core/exe/core_nrpic_v09/athena_cpu_omp`; try one restart file first); (iii) G3-G3 power
   on phase-randomised surrogates of FK - FL16 noise and of G-8's own noise (P-A3).
3. G-8-16N needs its data (flux_tools/esf_data.py at lattice h/2.52) and a memory check (processors: 31 GiB at
   4N for two cycles; the card: 4x the particle part of FN4).

## What this session did (batch 41)

- Closed q0100 (G-8, 2.20 card-hours) and read it with g8_read.py (run D-20261128-160553-b500509, figure
  looked at): G3-G1 holds; lead-bias band failed at its low end; the polished-minus-unpolished gap grows.
- SCOPE_G3 A6; decks g3g6u(_t2), n6es, n6v, g3g84n, g3g8e1 (make_g3_decks.py; older decks unchanged).
- A6 checks (run D-20261128-160418-b618bff): K1 held, K2 refuted (M/6 not found at t = 0), K3 held (v0.9 = v0.8).
- Leg smoke tests (run D-20261128-162112-e80048d): masses at t = 0 equal G-8's; count off by the 140 tracers
  (prediction error); expansion columns differ at round-off (entry 13).
- Queued q0110, q0111, q0112; outbox to orch; release message acked.

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
40-90 GB chains take 2-10 min (G-8: 72 GB, about 6 min). (25) FL16 and V-1L16 end at 299-299.75 M. (26) Close local
background runs with `nrpic-run finish` before reading them. (27) note/main.pdf is 1.1 MB. (28) A serial processor
smoke test of an M/8 ES-FL deck takes ~17-20 min for two cycles. (30) AthenaK aligns a refined region to the
blocks of the next coarser level and keeps one block of buffer per level: count blocks with `athena -m`; t = 0
horizon mass of these data is 1 (Schwarzschild), M/8 finder offset -8.5e-3, M/12 -2.5e-4, M/16 -1.9e-4. (31) use
`date` for journal times. (32) a finder summary repeats the last mass for a search not found; drop such rows by the
status file (eg8_read.filtered_view). (33) card memory of the uniform family is about 6.1 GiB + 1696 bytes per
cell (456 blocks with ghost zones). (34) NEW: a production `nrpic-run submit` needs `--preregistered <path>`.
(35) NEW: at M/6 the finder does not settle at t = 0 (reason 6 after 400 flow iterations, surface near r = 0.6 M).
(36) NEW: G-8's finder minus FK's grows from 6.5e-5 to 1.6e-4 over 400 M: compare polished with polished only.
