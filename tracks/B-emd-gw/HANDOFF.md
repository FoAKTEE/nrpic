# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 37, wave 3, 2026-11-27
18:56-19:40 PST: the fresh G2 verifier answered; the 256^3 member at eight particles per cell).
Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md). The G2 package is complete for the
independent gate review in the lead's judgement (stage/G2/OPEN.md): 20 of 20 items PASS or NA,
failures on record. One processor run of B is going (initial data, about two days); no card job.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/G2/VERIFIER.md` section 5 and
`stage/REVIEW-wave3.md` section "Batch 37" (the answers); `population/JOURNAL.md` entries
2026-11-27 19:02, 19:05, 19:12, 19:11 (predictions and outcomes of this session).

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`.

## Running at the end of the session

| What | How it is read |
|---|---|
| Initial data 256^3, eight per cell: B-20261128-030420-33ccdca (`run_gr_ic.sh 256 8 "--nc 3.2 --sigma1 0.014 --seed 1 --ppc 2 --outer 36"`, one core, detached, started 2026-11-27 19:04 PST; 30-55 h expected; 26 GB host memory after 8 min) | `tail $S/B-20261128-030420-33ccdca/run.log` ends with `# exit=`; `gr_L8_n256/make_ic.log` shows the outer iterations. When it has ended: `harness/bin/nrpic-run finish B-20261128-030420-33ccdca`, then check I1-I4 (population/JOURNAL 2026-11-27 19:02) against `gr_L8_n256/meta.json` of B-20261124-135030-b54972f (mesh_modes_kept 146, sigma1_realized 0.012343020531983813, H residual below 1e-10, 2^27 particles); write the outcome into population/JOURNAL. Do not kill it (it is the member decision 0048 item 3 asks for) |
| `harness/bin/nrpic-stage verify B-emd-gw G2` of this batch (standard pass, checksums from the cache; log `$S/tmp/verify_b37.log`, ends with `exit=`) | if it ended after the session's last commit: commit stage/G2/VERIFY_RESULTS.md/.json, run `harness/bin/nrpic-stage report B-emd-gw G2`, commit STAGE_REPORT.md |

No card job of B is queued or running. q0006 and q0007 are "not completed" in `nrpic-queue
audit`: both known (chain cap; guard stop) and judged, nothing to re-enter.

## The card member to queue once the data are checked (decision 0048 item 3)

Fits one card (42-46 GiB of 80; bound 76 GiB; B-20261128-030350-19295a4); about 12 card-h (8-16)
of the 28.36 left toward G2; about 0.65 TB of disk. Predictions K1-K3 are written (population/
JOURNAL 2026-11-27 19:02, K1 extended at 19:05). Commit first, then from the worktree root:

    harness/bin/nrpic-queue add --label pop_s014_gr256_p8_gd --priority 2 -- --kind scouting --gate G2 \
      --package tracks/B-emd-gw/population --purpose "population: 256^3 at eight particles per cell, sigma1 = 0.014, Gamma driver as q0060, to a = 143; predictions K1-K3 (JOURNAL 2026-11-27 19:02); decision 0048 item 3; initial data B-20261128-030420-33ccdca" \
      --launcher chain --exe /data/haiyangw/nrpic/.work/build_gpu_v08/src/athena --gpu-hours 16 -- \
      tracks/B-emd-gw/population/inputs/pop_gr_run.athinput mesh/nx1=256 mesh/nx2=256 mesh/nx3=256 \
      meshblock/nx1=128 meshblock/nx2=128 meshblock/nx3=128 mesh/x1max=8.0 mesh/x2max=8.0 mesh/x3max=8.0 \
      output2/dt=1.0 output3/dt=1.0 z4c/shift_Gamma=0.75 z4c/shift_eta=1.0 z4c/shift_advect=1.0 z4c/lapse_advect=1.0 \
      particles/particle_file=$S/B-20261128-030420-33ccdca/gr_L8_n256/particles.nrp \
      problem/id_file=$S/B-20261128-030420-33ccdca/gr_L8_n256/fields.bin

(q0060's arguments with the two files changed and the v0.8 release build; check `nrpic-queue add
--dry-run` first; use the newest release build named in CLAUDE.md if core-v0.9 is out by then and
say so in the journal.) If the orchestrator grants the 128^3/8 ppc Gamma-driver partner (outbox
request g2-p8-gamma-driver-partner-128), queue it beside it: q0006's 128^3 arguments (data
B-20261124-135029-3fe13f6) plus the four Gamma-driver options, about 1 card-h, prediction first.

## What G2 waits for

- The gate review by the orchestrator (outbox info g2-verifier-answered-package-ready).
- Nothing else by any criterion as worded; the 256^3/8 ppc member is pending and may be weighed.

## Results of this session (all registered, closed, figures looked at)

- Verifier's corrections a-e: pair_ratio B-20261128-030556-5ef9294 (first run -030537-0172236,
  same numbers); note v5 from run_all B-20261128-030805-78634c0 (first -030728-a5b1b32);
  SPEC item 5 amended; CHECKLIST C1, C2, C3, C18; OPEN.md.
- Member decision: mem_fit B-20261128-030350-19295a4 (first run -030214-20f2961: card time wrong,
  superseded).
- Full checksum pass of batch 34's commit committed (397511402).

Traps:
- Analyses longer than a session: `nrpic-run submit --background`.
- GR particle files carry the rest-mass weight (R25): use `--equal-mass`.
- Wall times of preempted segments have no end line in their logs: time a run from the
  restart-file intervals (mem_fit.py), not from the logs.
- The note's `main.pdf` is 1.44 MB (above the 1 MB guideline, below the 5 MB hook limit).
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores.
