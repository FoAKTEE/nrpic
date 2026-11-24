# HANDOFF of F-hills

State in three lines (2026-11-24 13:10 PST, end of the batch-12 session: card runs to the shared queue):
- G0 signed. G1 NOT met: the complete vacuum passage (C8) and the G1 verifier (C18) are missing
  (stage/G1/STATUS.md, OPEN.md, STAGE_REPORT.md). Everything else of G1 passes.
- The isolated m/16 binary does not merge (turns at 3.12 M at 73.9 M); P1b at m/16 reached 61.8 M
  unmerged and was cut by preemptions; it continues as A2 (G1) with C2 (m/12, G2) and B2 (G2).
- Card runs now go through the shared queue only (decision 0033): A2 runs (q0001, Slurm 5207),
  B2 waits (q0002), C2 waits after B2 (q0003). No sequencer of ours runs; start none.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Card runs of this owner in the shared queue (added 2026-11-24 13:03 PST)

On 2026-11-24 12:00 PST orch stopped our sequencer (seq_b11.sh, pid 604718) and cancelled A2
(5172), B2 (5171) and C2 (5173, held) while they waited; none had started (sacct: Start None).
This session closed the three as stopped in nrpic-run (0 card-hours) and added them again to the
queue with the same arguments (new run ids at dispatch; `--notes` names the run each replaces).
See them: `harness/bin/nrpic-queue list --owner F-hills`, `show <id>`.

| | queue id | label, prio | run id (job) | what | gate, ceiling | replaces (stopped) | read by |
|---|---|---|---|---|---|---|---|
| A2 | q0001 | F-A2, 2 | F-20261124-210400-902c650 (Slurm 5207, RUNNING 13:04 PST) | P1b m/16 from A's restart 23 (t = 61.80 M) to tlim 200; restart every 1 M | G1, 19.5 card-h (19 segments) | F-20261124-141118-fbc6419 | stage/review_wave3/b11_cards.py and b11_passage.py (A + A2); G1 C8 |
| B2 | q0002 | F-B2, 5 | at dispatch | binary alone m/16 from B's restart 34 (107.85 M) to tlim 140; restart every 1 M | G2, 5 (5 segments) | F-20261124-135408-1e6db58 | b11_cards.py (R16n + B + B2); Peters apocentre check |
| C2 | q0003 | F-C2, 5, after F-B2 | at dispatch | P1b m/12 from C's restart 6 (20.0 M) to tlim 200; restart every 1.5 M | G2, 24 (24 segments) | F-20261124-141842-d5263e9 | b11_cards.py and b11_passage.py (C + C2) |

The readers still name the OLD run ids (b11_cards.py lines 52-54): put in the new ids from
`nrpic-queue list` (or the `F(run): register` commits) before running them. A chain that its
segment cap cuts is NOT continued by anything now: continue it from its newest restart file
with a `--cmd` wrapper of binary_conv (to write; harness/RULES.md "Shared card queue":
JOB_NAME=<run_id>, MAX_SEGMENTS set, records the continuation in the manifest; dry run first).

All: `binary_conv/scripts/athena_resume_bc.sh` -> `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`
(byte copy of release core-v0.5's card build; do not delete it), cfl_number 0.25, constant
shift_eta = 2, no lapse_leak. Each continuation's directory starts where its parent stopped:
read them joined (b11_cards.py does it). Predictions: JOURNAL.md, batch 11, "Q4 decision"
(A2-1 to A2-5, B2, C2); they stand unchanged for the requeued runs.

Parents (closed as stopped in nrpic-run; cut by preemption and their segment caps): A
F-20261121-203144-b2cf16b (to 61.8 M), C F-20261121-203247-961801d (to 22.3 M). B
F-20261121-203156-03efdd3 (to 107.85 M) is NOT closed yet: its finish was stopped by the pause
flag at 06:27 PST (nothing written). First thing next session: `harness/bin/nrpic-run finish
F-20261121-203156-03efdd3 --status stopped` (checksums 110 GB: about an hour on a busy disk; it
commits the manifest at the end; G2's budget counts B at its 12.78 ceiling until then).

See the chains: `squeue -u $USER -o "%i %j %T %r"`; `scripts/submit_chain.sh --status <rundir>`.

## Sequencer `binary_conv/scripts/seq_b11.sh`: retired (decision 0033)

Stopped by orch on 2026-11-24 12:00 PST (pid 604718 gone). Do not restart it or any sequencer:
the shared queue's `--after` replaces its hold, and a `--cmd` wrapper replaces its in-place
continuation. Its table and log stay in scratch/F-hills/seq/ for the record.

## Exact commands for the next session

1. Read the passage (registered, 1 core, minutes):

       harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/stage \
         --parent F-20261124-210400-902c650 --parent <B2's new run id> --parent <C2's new run id> \
         --purpose "read A2/B2/C2 against A2-1..A2-5, B2, C2" \
         -- python3 tracks/F-hills/stage/review_wave3/b11_cards.py --out '$NRPIC_RUN_DIR'

   (first set the new run ids in b11_cards.py lines 52-54 and commit; ids from `nrpic-queue list`)

   and the passage reader (same form, `b11_passage.py`; tested on A and C, run
   F-20261124-142649-5512ba0): member distances to M, energies against M and the barycentre,
   E_bin, a provisional fate per member, Newton overlaid. Still to add when A2 has passed the
   pericentre: the bound member's pericentre and eccentricity, HRNA and EIH overlays, the
   remnant/horizons near M, the waveform (p1's readers).
2. When A2 has ended: `harness/bin/nrpic-run finish F-20261124-210400-902c650`; judge A2-1..A2-5;
   if the binary has separated, ask for the G1 verifier (stage/G1/OPEN.md item 2 lists the
   material); if A2 stopped short of the separation for lack of card-hours, see orch's answer.
3. When B2 has ended: the apocentre against 4.65-4.90 M (Peters, JOURNAL batch 11).
4. Disk: A2 writes a 5.8 GB restart per M (about 800 GB to 200 M), C2 5.3 GB per 1.5 M. When a
   chain has ended, keep every fifth restart file and the newest (delete by literal path, never
   through a shell variable), or ask orch.

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | runs A2 (running), B2, C2 (queued) (lead-run); script athena_resume_bc.sh (seq_b11.sh retired) | README "Results" row for m/16 at 20 M and the B result (3.12 M minimum) |
| khsr_note | closed, reviewed (batch 11); its note moved to note/ | second-agent check of K3 and the P1-280 numbers (G1 verifier) |
| note | v2 in note/ (24 pages, compiles, checker clean but accepted items) | v3 with the passage; legend of fig_elliptic; floats after Sec. VI; reviewer step |
| g2mesh | cut 2026-11-20; `scripts/card_analysis.py` committed as WIP, untested | G2M-1b outcome; G2M-2/3 analysis of card batch F-20261120-222810-e408386 |
| junk_gauge, kerr, eih, p1, nr_first | closed | T3 junk at P1b's spheres (A2 waveforms); kerr small items (HANDOFF of batch 5 list) |

## Files to read first

`CLAUDE.md`; decisions 0026, 0027, 0030; `STATUS.md`; `JOURNAL.md` last entry (batch 11: state,
Q1-Q4, N1, N1m, L-K, the follow-up predictions); `RISKS.md` (R20, R21); `stage/REVIEW-wave3.md`
(batch 11 section); `stage/G1/OPEN.md`.

## Decisions pending

- orch: allotment for A2's tail (G1: 11.1 card-hours left beyond A2 under the 60 of decision 0032); in-place continuation (now: a `--cmd` wrapper through the queue); chain cap by card time (outbox 20261124T135319Z__to-orch__cards-read-continuations-allotment).
- core: restart on SIGTERM (outbox 20261124T135319Z__to-core__restart-on-sigterm); older: stray
  resubmission after a chain's last segment (seen again: A's job 5135), H-norm2 transient in R8,
  HRNA pair-force spec, wave extraction beyond l = 8.

## Traps

- A preempted job counts as a chain segment; a night of preemptions ends a chain at its cap.
- A2, B2, C2 directories start at 61.8, 107.85 and 20.0 M; their tracker files hold only that part.
- Horizon summaries: a failed search repeats the previous row; a sawtooth band of up to 4e-3 in
  m_AH remains after nrread's filter (fig_b11_health); fit slopes, do not read single rows.
- nrpic-run finish of a 100+ GB run takes about an hour on a busy disk; its commit lands at the
  end: do not commit by hand at that moment.
- 1PN references of the binary are not sharp (R17).
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
