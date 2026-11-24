# HANDOFF of F-hills

State in three lines (2026-11-24 06:30 PST, end of the lead session of batch 11):
- G0 signed. G1 NOT met: the complete vacuum passage (C8) and the G1 verifier (C18) are missing
  (stage/G1/STATUS.md, OPEN.md, STAGE_REPORT.md). Everything else of G1 passes.
- The isolated m/16 binary does not merge (turns at 3.12 M at 73.9 M); P1b at m/16 reached 61.8 M
  unmerged and was cut by preemptions; it continues as A2 (G1) with C2 (m/12, G2) and B2 (G2).
- A sequencer (pid 604718) keeps C2 held until B2 ends and continues a cut chain in place within
  its registered card-hours.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Card jobs of this owner (registered 2026-11-24 05:54-06:19 PST)

| | run id | what | gate, ceiling | first job |
|---|---|---|---|---|
| A2 | F-20261124-141118-fbc6419 | P1b m/16 from A's restart 23 (t = 61.80 M) to tlim 200; restart every 1 M | G1, 19.5 card-h (19 segments) | 5172 |
| B2 | F-20261124-135408-1e6db58 | binary alone m/16 from B's restart 34 (107.85 M) to tlim 140; restart every 1 M | G2, 5 (5 segments) | 5171 |
| C2 | F-20261124-141842-d5263e9 | P1b m/12 from C's restart 6 (20.0 M) to tlim 200; restart every 1.5 M; HELD until B2 ends | G2, 24 (24 segments) | 5173 (held) |

All: `binary_conv/scripts/athena_resume_bc.sh` -> `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`
(byte copy of release core-v0.5's card build; do not delete it), cfl_number 0.25, constant
shift_eta = 2, no lapse_leak. Each continuation's directory starts where its parent stopped:
read them joined (b11_cards.py does it). Predictions: JOURNAL.md, batch 11, "Q4 decision".

Parents (closed as stopped in nrpic-run; cut by preemption and their segment caps): A
F-20261121-203144-b2cf16b (to 61.8 M), C F-20261121-203247-961801d (to 22.3 M). B
F-20261121-203156-03efdd3 (to 107.85 M) is NOT closed yet: its finish was stopped by the pause
flag at 06:27 PST (nothing written). First thing next session: `harness/bin/nrpic-run finish
F-20261121-203156-03efdd3 --status stopped` (checksums 110 GB: about an hour on a busy disk; it
commits the manifest at the end; G2's budget counts B at its 12.78 ceiling until then).

See the chains: `squeue -u $USER -o "%i %j %T %r"`; `scripts/submit_chain.sh --status <rundir>`.

## Sequencer `binary_conv/scripts/seq_b11.sh` (started 06:18:51 PST, setsid nohup)

    cat /data/haiyangw/nrpic/scratch/F-hills/seq/seq_b11.pid; ps -p <pid>
    tail /data/haiyangw/nrpic/scratch/F-hills/seq/seq_b11.log
    table: /data/haiyangw/nrpic/scratch/F-hills/seq/b11.table (name rundir ceiling after deck)
    stop it: touch /data/haiyangw/nrpic/scratch/F-hills/seq/STOP   (exits within 5 min)
    dry pass: SEQ_DRY=1 tracks/F-hills/binary_conv/scripts/seq_b11.sh <a tmp dir> <table>
    restart it (machine rebooted, chains not all ended): rm -f .../seq/STOP; setsid nohup \
      /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/binary_conv/scripts/seq_b11.sh \
      /data/haiyangw/nrpic/scratch/F-hills/seq /data/haiyangw/nrpic/scratch/F-hills/seq/b11.table \
      >> /data/haiyangw/nrpic/scratch/F-hills/seq/seq_b11.log 2>&1 < /dev/null &

It holds C2 while B2 has not ended for good, then releases it; when a chain ends "FAILED,
MAX_SEGMENTS reached" (preempted jobs count as segments) and its sacct card time is below its
ceiling, it reruns `scripts/submit_chain.sh` on the same run directory with MAX_SEGMENTS raised
(in-place continuation of the registered run; orch asked to object if not acceptable). It leaves
a chain that failed for any other reason alone and exits when all three have ended.

## Exact commands for the next session

1. Read the passage (registered, 1 core, minutes):

       harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/stage \
         --parent F-20261124-141118-fbc6419 --parent F-20261124-135408-1e6db58 --parent F-20261124-141842-d5263e9 \
         --purpose "read A2/B2/C2 against A2-1..A2-5, B2, C2" \
         -- python3 tracks/F-hills/stage/review_wave3/b11_cards.py --out '$NRPIC_RUN_DIR'

   and the passage reader (same form, `b11_passage.py`; tested on A and C, run
   F-20261124-142649-5512ba0): member distances to M, energies against M and the barycentre,
   E_bin, a provisional fate per member, Newton overlaid. Still to add when A2 has passed the
   pericentre: the bound member's pericentre and eccentricity, HRNA and EIH overlays, the
   remnant/horizons near M, the waveform (p1's readers).
2. When A2 has ended: `harness/bin/nrpic-run finish F-20261124-141118-fbc6419`; judge A2-1..A2-5;
   if the binary has separated, ask for the G1 verifier (stage/G1/OPEN.md item 2 lists the
   material); if A2 stopped short of the separation for lack of card-hours, see orch's answer.
3. When B2 has ended: the apocentre against 4.65-4.90 M (Peters, JOURNAL batch 11).
4. Disk: A2 writes a 5.8 GB restart per M (about 800 GB to 200 M), C2 5.3 GB per 1.5 M. When a
   chain has ended, keep every fifth restart file and the newest (delete by literal path, never
   through a shell variable), or ask orch.

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | runs A2, B2, C2 in flight (lead-run); scripts seq_b11.sh, athena_resume_bc.sh | README "Results" row for m/16 at 20 M and the B result (3.12 M minimum) |
| khsr_note | closed, reviewed (batch 11); its note moved to note/ | second-agent check of K3 and the P1-280 numbers (G1 verifier) |
| note | v2 in note/ (24 pages, compiles, checker clean but accepted items) | v3 with the passage; legend of fig_elliptic; floats after Sec. VI; reviewer step |
| g2mesh | cut 2026-11-20; `scripts/card_analysis.py` committed as WIP, untested | G2M-1b outcome; G2M-2/3 analysis of card batch F-20261120-222810-e408386 |
| junk_gauge, kerr, eih, p1, nr_first | closed | T3 junk at P1b's spheres (A2 waveforms); kerr small items (HANDOFF of batch 5 list) |

## Files to read first

`CLAUDE.md`; decisions 0026, 0027, 0030; `STATUS.md`; `JOURNAL.md` last entry (batch 11: state,
Q1-Q4, N1, N1m, L-K, the follow-up predictions); `RISKS.md` (R20, R21); `stage/REVIEW-wave3.md`
(batch 11 section); `stage/G1/OPEN.md`.

## Decisions pending

- orch: allotment for A2's tail (G1 has 1.1 card-hours left); in-place continuation by the
  sequencer; chain cap by card time (outbox 20261124T135319Z__to-orch__cards-read-continuations-allotment).
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
