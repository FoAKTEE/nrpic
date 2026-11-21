# HANDOFF of F-hills

State in three lines (2026-11-21, end of the lead session of wave 3, batch 4a):
- G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met: no complete Hills passage, KHSR, note
  compile, G1 verifier (stage/G1/STATUS.md, OPEN.md).
- P1 (run F-20261119-150017-b45ec5f) ended at t = 280 M and is finished in nrpic-run; its binary
  merged at 48.8 M because the members at m/8 are under-resolved (binary_conv; decision 0022).
- P1b (members at m/16) is prepared and announced but NOT submitted: it waits for rule P1b-D.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

Run next: scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/F-20261121-130351-04074e1

## Card jobs of this owner (queued at 08:15 PST; both read by binary_conv and by rule P1b-D)

| run | what | state | when it ends |
|---|---|---|---|
| F-20261121-130351-04074e1 | R16n: P1's binary alone, members at m/16, MAX_SEGMENTS 3 | segment 1 done (0-7.74 M); segment 2 = Slurm 4807 pending; segment 3 follows by itself | after segment 3 the chain queues a STRAY job: cancel it with `scripts/submit_chain.sh --stop <rundir>` |
| F-20261121-153707-1eaa5d4 | R12: the same at m/12, MAX_SEGMENTS 2 | Slurm 4809 pending | same stray job after segment 2 |

Both run `binary_conv/scripts/athena_keep_trackers_bc.sh`, which keeps tracker files across
restarts (`<rundir>/trk_keep/`) and runs `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`, a byte
copy of release core-v0.5's card build under its own name: do not delete it.

## What to do when both chains have ended (the decision of the next passage)

1. Analysis: the command in `binary_conv/README.md`, section "Analysis" (add `--run R12=...`).
2. Apply rule P1b-D, written before the data in `JOURNAL.md` (entry 2026-11-21T15:55Z, section
   "P1b"): D1 three-point order at t = 15 M from R8, R12, R16n >= 2, monotone, continuum loss in
   -0.02 to 0.12 M; or D2 R16n's separation loss by 20 M <= 0.10 M with flat masses. Do not judge
   by the distance to one 1PN reference (RISKS R17: the 1PN variants differ by up to 0.16 M).
3. If the rule holds and squeue shows fewer than two F-hills jobs: submit P1b with the command
   of `binary_conv/JOURNAL.md` BC-4 item 6 (`--gpu-hours 32`, `--preregistered` pointing to a
   P1b prediction you write first into JOURNAL.md: compare with P1's prediction in
   `stage/G1/STATUS.md` and with Newton, HRNA, EIH from the same start state). The card-hours
   are announced in STATUS.md. The chain runs for days of queue time; a later session analyses.
4. If the rule fails: no P1b; write why, and plan finer members (two cards, MPI card build) or a
   wider binary.
5. Close both runs: `harness/bin/nrpic-run finish <run id>` (takes minutes per 100 GB).

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | partial (batch 3), reviewed | the steps above; BC-5 checks; README's drift labels are fractional (review) |
| junk_gauge | closed (batch 2b), reviewed | none; T3 to be remeasured at P1b's spheres |
| kerr | closed (batch 3), reviewed | open: Fermi-frame tidal reference for L_z > 0 and Fig. afin; geodesic_binary S4 rerun in 'bks'; numba into the track's requirements (kerr used `scratch/F-hills/venv-gb`) |
| p1 | cut; chain DONE and finished | analysis to t = 280 M (`p1/README.md`, "Commands for the next session"); no longer decides G1 |
| note | paused | lead's corrections list (`note/JOURNAL.md`), registered `run_all.py`, compile, `check_manuscript.py --compile`, pages; add Kerr row, P1's merger and cause, junk numbers of batch 4a |
| g2mesh | cut; `scripts/card_analysis.py` UNCOMMITTED (left alone) | G2M-1b outcome; G2M-2 analysis of F-20261120-222810-e408386; cost table (G2 ladder now starts at m/16) |
| KHSR | not started | one result of 1201.4794 with newton3 (`e_orb`; SCOPING 5) |

## Files to read first

`CLAUDE.md`; decisions 0013, 0016, 0019-0022; `STATUS.md`; `stage/REVIEW-wave3.md` (second
part: batch 4a); `stage/G1/STATUS.md`, `OPEN.md`, `CHECKLIST.md`; `RISKS.md` (R15, R17, R18);
`JOURNAL.md` last entry; `binary_conv/README.md` and `JOURNAL.md` BC-3 to BC-5.

## Decisions pending

- orch: a session for P1b-D when the chains end (outbox 20261121T16*); awareness of kerr's
  digitized numbers (rule 9).
- core: stray resubmission after a chain's last segment; H-norm2 transient at t = 0.5 in R8;
  HRNA pair-force specification (T8 d); wave extraction beyond l = 8; tracker files on restart
  (accepted for a later release, no branch); Bowen-York momenta vs 1PN (unanswered).

## Traps

- `nrpic-stage verify` fails while g2mesh's file is uncommitted and while chains run.
- Horizon summaries: a failed search repeats the previous row; at m/8 use masses with hrms < 1e-3;
  at m/16 rows with larger hrms still agree within 1e-4.
- Tracker files are truncated on restart: only the wrappers keep them (`trk_keep/`).
- 1PN references of the binary are not sharp (R17); r_p of an NR passage only with its GR
  turning point; 1PN start states are matched far out, not at pericentre.
- `nrpic-run finish` of a large chain checksums every file (P1: 165 GB, about 15 minutes).
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
