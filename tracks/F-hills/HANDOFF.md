# HANDOFF of F-hills

State in three lines (2026-11-21, end of the lead session of wave 3, batch 2a):
- G0: package complete for an independent review (verifier's report in, every WRONG item
  corrected, `stage/REVIEW-wave3.md`); review asked of orch; not signed (`coord/GATES.md`).
- G1 not met. P1 (run F-20261119-150017-b45ec5f) runs its last segments to t = 280 M, but its binary
  MERGED at t = 48.8 M before the passage (confirmed by the lead's own parser): RISKS R15.
- Five round-1 packages were cut on 2026-11-20 (note, p1, junk_gauge, kerr, g2mesh); state below.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

Run next: scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f

## Card job running

P1's chain: segment 14 = Slurm 4769 (started 2026-11-20 22:24 PST at t = 231.9 M, about 20 M per
segment; MAX_SEGMENTS 18), so segment 15 (and perhaps 16) follow by themselves; about 1.5
card-hours left. Read by: package p1 (`p1/scripts/run_all.sh`, `nr_first/scripts/p1_analysis.py`)
and junk_gauge (J4, the spheres). When `chain/STATUS` says DONE:
`harness/bin/nrpic-run finish F-20261119-150017-b45ec5f`, then the two analyses in
`p1/README.md` ("Commands for the next session"). If the chain stops on MAX_SEGMENTS before
t = 280, resume with the command in `p1/README.md` (MAX_SEGMENTS 20). If a segment dies with exit
143/137 and no AthenaK message, it was an outside kill: resume the same way (p1 README).

## Packages cut on 2026-11-20 and what each still needs

| package | committed? | what remains |
|---|---|---|
| p1 | yes (intermediate analysis committed by the lead, bb68684b) | analysis to t = 280 M; outcomes of the resumed-chain predictions (entry 1) and P1 items 1, 2 (last clause), 3b; the cause of the merger is NOT p1's job: next action 1 below |
| junk_gauge | yes, to the J4 prediction | E10's outcome into `nr_first/JOURNAL.md` (analyses F-20261120-222403-b8dc28c, -222415-137ada9 exist); J4 measurement at P1's spheres (remember the merger signal after t = 48.8 M); README |
| kerr | NO: all files uncommitted (JOURNAL entries 0-1 = predictions, `hrna_incl.py`, `tests/t5_rotation.py`, `tests/t6_kerr_single.py`, `scripts/{digitize_2402,paper_2402,figstyle}.py`) | run its tests and the 2402.02178 comparison, record outcomes, commit (digitised third-party curves stay in scratch) |
| g2mesh | yes, except `scripts/card_analysis.py` | G2M-1b outcome; G2M-2 analysis of card run F-20261120-222810-e408386 (m16_b16_s3000 ran at 78785 MiB; m8_b32_s1150 aborted rc 134); cost table |
| note | yes (paused, 70257ac0; lead edits c865ba7a) | the lead's corrections list (`note/JOURNAL.md`, lead entry items 1-7) into `scripts/ledger.py`, prediction, registered `run_all.py`, latexmk, `check_manuscript.py --compile`, read every page; README; P1's merger in Sec. V |

## Next actions (most important first)

1. Isolated binary test (decides RISKS R15): the two members of P1 alone (same a_b, momenta,
   `corr`, gauge `shift_eta = 2`) at m/8 and at m/16, about 60 M, on one card (m/16 fits: 3000
   slots). Prediction first: if only m/8 merges, resolution; if both, gauge or data. Then decide
   the next passage (finer members or wider binary; 1PN-consistent start state from eih).
2. P1 to the end (above); the junk (J4) and E10.
3. KHSR: one result of 1201.4794 with newton3 (`e_orb`; SCOPING 5, verifier D8).
4. When 1-3 and the cut packages are done: a fresh verifier of the G1 material (ledger tables
   3-4, P1, junk, eih), then `nrpic-stage collect/verify/report F-hills G1`.

## Files to read first

`CLAUDE.md`; decisions 0013, 0016, 0019, 0020; `STATUS.md`; `stage/REVIEW-wave3.md` (what was
checked and corrected); `stage/G0/VERIFIER.md` section 3 (defects D1-D10) and
`stage/G0/SCOPING.md` ([amended: D<n>]); `stage/G1/STATUS.md` and `OPEN.md`; `p1/JOURNAL.md` entry 4;
`RISKS.md` (R15 first); `JOURNAL.md` last entry.

## Decisions pending

- orch: G0 independent review; waivers for F-20261115-173719-923135a, -181805-f9c3473,
  -182100-613c9c6; errata row 1.5; chain rule for outside kills (outbox 20261121T*).
- core: tracker files truncated on restart (reminder); Bowen-York momenta against canonical 1PN
  momenta (eih's request).
- Track: whether the next passage uses finer members or a wider binary (after action 1).

## Traps

- P1's chain runs the real executable under the name `p1-ak03-gpu`
  (`scratch/F-hills/tmp/p1/exe/`): do not delete it while the chain runs.
- Tracker files are truncated on restart: only `nr_first/scripts/athena_keep_trackers.sh` keeps
  them (`<rundir>/trk_keep/`); a later file wins where times overlap.
- Horizon summaries: a failed search repeats the previous row; masses only with hrms < 1e-3.
- After t = 48.8 M finders 0 and 1 both follow the remnant (mass about 0.268).
- The reference percentages near the separation edge (V7) depend on the start construction;
  quote them only with it (verifier D2). r_p of an NR passage: always with its GR turning point.
- 1PN start states must be matched far out and integrated in, not at pericentre (lead's failed
  first attempt, run F-20261121-063527-b4453db).
- `nrpic-stage verify` fails while the worktree holds kerr's and g2mesh's uncommitted files and
  while P1 runs; commit path-limited (`git commit -- <paths>`).
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, or numeric PIDs.
