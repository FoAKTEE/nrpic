# HANDOFF of F-hills

State in three lines (2026-11-25 22:20 PST, end of the batch-25 lead session, processors only):
- G0 signed. G1 NOT met: the complete vacuum passage (C8) needs A2 to at least 170 M; the G1
  verifier (C18) is PARTIAL (it checked the passage to 96.23 M). Everything else of G1 passes.
- A2 ended at its segment cap at 133.0 M (11.15 card-hours): the binary is disrupted, m1 falls
  almost radially into M (2.49 M from M), m2 swings by at 8.7 M; Newton gives the reverse fates.
- A2 continues in place from 133.0 M through ONE shared-queue entry, q0069 (below), cap 28
  counted segments, with the finder's status file (processor test R25 passed, JOURNAL batch 25).

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Card runs of this owner (shared queue only; `harness/bin/nrpic-queue list --owner F-hills`)

| | queue id | run id (job) | what | gate, ceiling | read by |
|---|---|---|---|---|---|
| A2 | q0069 (label F-A2c, prio 2; waiting at 22:07 PST, the account at five jobs) | F-20261124-210400-902c650 (continued in place; jobs keep the run id as name) | P1b m/16 from hills.00105.rst (133.0 M) to tlim 200; cap 28 counted segments (19 used); with `-i tracks/F-hills/binary_conv/inputs/fastflow_diag.athinput` (`<fastflow> diagnostics = true`; R25 passed, F-20261126-054626-7301561) | G1, A2's 19.5 card-hours (11.15 used); up to 5 more from G1 only if preemptions eat the margin (0042 item 2) | `stage/review_wave3/b21_a2_state.py`, `b11_passage.py` (join A + A2); the status file `hills.horizon_status_<n>.txt` in the run directory |
| B2 | q0002 (submitted, Slurm 5357 pending at 21:40) | F-20261126-052133-10f9a5f | pair alone m/16 from B's restart 34 (107.85 M) to 140 | G2, 5 | `b11_cards.py` |
| C2 | q0003 (waits after F-B2) | at dispatch | P1b m/12 from C's restart 6 (20.0 M) to 200 | G2, 24 | `b11_passage.py` (C + C2), `b11_cards.py` |

A2's continuation: `tracks/F-hills/binary_conv/scripts/continue_chain.sh F-20261124-210400-902c650
28 [--extra-input tracks/F-hills/binary_conv/inputs/fastflow_diag.athinput]` (dry run:
`--dry-run` first). It checks the dispatch, the deck and executable bytes, the counted segments
(attempts minus uncounted), resubmits `scripts/submit_chain.sh` in place with JOB_NAME = run id,
appends `-i <file>` once to EXTRA_ARGS, records a `continuations` entry in the manifest and
commits it. The executable stays `binary_conv/scripts/athena_resume_bc.sh` -> byte copy
`scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu` of core-v0.5's card build (do not delete it);
the wrapper keeps every segment's tracker files in `<rundir>/trk_keep/<UTC stamp>/`.

## Exact commands for the next session

1. When A2 has new records (registered, 1 core, a minute each):

       harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/stage \
         --parent F-20261124-210400-902c650 --parent F-20261121-203144-b2cf16b \
         --purpose "A2 state to its last record; C25" \
         -- .venv/bin/python tracks/F-hills/stage/review_wave3/b21_a2_state.py --out '$NRPIC_RUN_DIR'

   and the same with `b11_passage.py` (add `--parent F-20261121-203247-961801d`). Judge C25-1 to
   C25-5 (JOURNAL batch 25). Read finder 2's status rows from 133 M on to decide F1
   (stage/G1/OPEN.md item 5). Readers still to extend: the status file, m1's merger with M
   (M's mass jump), m2's pericentre and fate, HRNA and EIH overlays, the waveform of the plunge.
2. When A2 has ended (>= 170 M or its cap): `harness/bin/nrpic-run finish
   F-20261124-210400-902c650` (reads 300+ GB once: start it in the background); judge A2-3 to
   A2-5 and C8; send a verifier for the passage from 96.23 M on (VERIFIER.md section 7 says how
   to rerun `stage/G1/verifier/scripts/run_all.sh` on the completed passage).
3. Close the G1 package: `harness/bin/nrpic-stage collect F-hills G1`, `verify` (once with
   `--full` before review), `report`.
4. Disk: A2 writes a 5.8 GB restart per M. When it has ended, keep every fifth restart file and the
   newest (delete by literal path, never through a shell variable), or ask orch.

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | A2 continuing (queue), B2, C2 queued; README per verifier (a), (b) | README "Results" row for m/16 at 20 M; B2's result |
| stage/review_wave3 | b21_a2_state.py (axis fix batch 25), b11_passage.py, b25_diag_restart.py | extend readers (item 1 above) |
| stage/G1/verifier | VERIFIER.md batch 22 (to 96.23 M) | rerun on the completed passage |
| note | v2 (24 pages) | v3: passage and reversed fates, ledger row 194 without "order", verifier (f) wording |
| g2mesh | cut 2026-11-20; `scripts/card_analysis.py` WIP, untested | G2M-1b outcome; G2M-2/3 |
| novelty | kb's answer on claim 452 | reword NOVELTY.md if needed |
| junk_gauge, kerr, eih, p1, nr_first, khsr_note | closed | T3 junk at P1b's spheres (A + A2 waveforms) |

## Files to read first

`CLAUDE.md`; decisions 0042 (item 2), 0043 (item 5); `STATUS.md`; `JOURNAL.md`, the batch-25 entry
(R25, B25, C25 predictions and outcomes); `RISKS.md` (R20, R22, R23, R24); `stage/G1/OPEN.md`;
`stage/G1/VERIFIER.md`; `stage/REVIEW-wave3.md` (batch 25).

## Decisions pending

- core: a restart that accepts a new parameter on the command line (core's NEXT_SOURCE item 1);
  older: HRNA pair-force spec, wave extraction beyond l = 8, H-norm2 transient in R8.

## Traps

- Segments: the chain counts attempts minus those cut by a signal (`chain/segment` minus
  `chain/uncounted`); the cap is MAX_SEGMENTS of `chain/config.sh` (now set by the wrapper).
- A2's directory starts at 61.80 M: always read A + A2 joined (b11_cards.trackers("A")).
- Horizon rows before 133 M have no status file; column 1 of the summary is the integrator stage,
  not the cycle; a sawtooth band up to 4e-3 in accepted m_AH rows remains (fit slopes).
- `fastflow/diagnostics=true` on the command line of a restart is FATAL; only `-i <file>` works.
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
