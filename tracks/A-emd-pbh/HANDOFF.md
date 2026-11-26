# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 23 (wave 3), 2026-11-25 ~19:20 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2's runs are all judged except the Szekeres pair
128 -> 256 (a detached reader is running); G2 is NOT ready for its verifier: four rulings are asked of orch (outbox
g2-state-after-batch-23) and the note's G2 sections, schematics, rerun list and slice mosaic are unwritten.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` section 11; the outbox file
`outbox/*g2-state-after-batch-23.md` and orch's answer (coord/DECISIONS, 0043 or later); `szekeres/JOURNAL.md`
entry 11; `periodic_threshold/JOURNAL.md` last three entries; `threshold_ball/JOURNAL.md` entry 14.

## Processor runs still going (detached by this session)

| run | what | cores | read with |
|---|---|---|---|
| A-20261126-024724-425ed7f | Szekeres reader, members N64 and N128 (A-20261125-213939-0ad9f29), ~15 min per N128 dump, ends ~20:30 PST | 1 | close with `harness/bin/nrpic-run finish A-20261126-024724-425ed7f`; `code_runs_n64n128.json` and its figures give P18 (N128), P19 (64 -> 128), P20 at N = 128 |
| A-20261126-023245-1dd80ad | Szekeres reader, members N128 (A-20261125-213939-0ad9f29) and N256 (A-20261125-231808-0784bc9, dumps tau 0, 10, 20), ~1 h per N256 dump, ends ~22:30 PST | 1 | close with `harness/bin/nrpic-run finish A-20261126-023245-1dd80ad`; its `code_runs_n128n256.json` and figures give P19 (128 -> 256), P20 at N = 256, P21; write the outcome as szekeres JOURNAL entry 12 |

## Card runs: none running or queued for G2. Shared queue: q0015 a-s1l-cont (waiting; continues S1L from t = 198.7
to 220 for SCOPE section 7, not a checklist item; read by job2_q.py and a2 scripts). No card time used in batch 23.

## Next, in order

1. Read orch's rulings on the four questions (C3 with the failure on record; P0L6's finder failure; Szekeres N256 to
   tau 40 or judged at tau <= 20; a half-amplitude GR member for A2 before G2 or in G3). Do what they say.
2. Close and read both Szekeres readers (above); write szekeres JOURNAL entry 12 (P18-P21) with their figures.
3. If the rulings let G2 go on with its failures on record: write the G2 sections of the note (decision 0039 item 9,
   `/paper-writing`), the schematics on core-v0.7 (C16) and the ladder schematic (C10), the rerun list
   `stage/G2/VERIFY` (C6), convergence figures in zoom style (C11), a slice mosaic from the Szekeres N256 dumps
   (`scratch/A-emd-pbh/A-20261125-231808-0784bc9/szk.field.0000[0-2].bin`, uniform 256^3; C13); then
   `harness/bin/nrpic-stage collect/verify/report A-emd-pbh G2` and ask for the verifier of the whole gate.
4. C3: the particle-number leg of S2c-A (S2 with the CIC cloud, mesh M/16, x8 particles, to t = 2, processors,
   prediction first in threshold_ball entry 15); core's answer on the PCS deposit (core's batch-23 test).
5. P0L6's finder: when core answers (outbox finder-false-accept-and-stall-p0l6), rerun the finder on P0L6's restart
   files at t = 136 and 140 on processors with the options core names.

## Packages

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | entry 14: C3 mesh leg judged (G refuted) | particle-number leg (entry 15) |
| `periodic_threshold/` | A2X and AZ1 (N-z128) judged; P0L6 D1-D5 judged | finder rerun after core's answer; half-amplitude member if ruled |
| `szekeres/` | series ran (q0040, q0041); P17 judged, N64 rows read (entry 11) | the two detached readers (above) |
| `conv_ball/` | | A-R1.35 ddet unchecked (verifier) |

## Traps

- `analyse_code_runs.py` takes ~1 min per dump at N = 64, ~8 at 128, ~60 at 256 (one core); run N256 detached.
- A queue entry for a chain without a segment count runs ONE segment (MAX_SEGMENTS = 1): N256 stopped at tau 21.2.
- The particle files hold x, u_i, m only: no Lorentz factor without the metric (a2_invariant.py's bound is empty).
  The 'probe' (column 15 of nrpic.hst) is the normal observer's clock at a fixed COORDINATE point, not a particle;
  the central particle of S1L is at rest (|u_i| < 1e-12), so int alpha_min dt bounds its proper time from below.
- Found or not found is ONLY in `<base>.horizon_status_<n>.txt` (decision 0040 item 3), and even a "found" row can
  be false (P0L6 t = 118.1: check mass, mean and minimum radius, expansion).
- Newtonian controls at one force cell per particle spacing run 26 per cent late (N-z vs N-z128).
- GR particle files carry psi^6 in the masses (B's message, AZ2): never read them as Newtonian masses.
- Quote exact-mass brackets, never a median below the bracket width; with a Gamma-driver use `<z4c> dt_gauge = 0.9`.
- At most 6 cores per session; markdown tables: never write `||H||` inside a table row.
