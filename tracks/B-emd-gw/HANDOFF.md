# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 39, wave 3, 2026-11-27
19:31-20:45 PST: G2 held by decision 0050; its two conditions started). Rewritten every session.

State in three lines: G0 and G1 are signed. G2 is HELD, NOT SIGNED (coord/GATES.md; decision
0050): C2 (three-way convergence) is met for the band strain only to a = 49 and reads FAIL in
stage/G2/CHECKLIST.md. Condition (a) was measured this session and is NOT met by the magnetic Weyl
invariant; condition (b) is a card run waiting in Slurm. A second review limited to C2 follows.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "submitted|running" && harness/bin/nrpic-queue list | grep B-emd`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/G2/GATE_REVIEW.md` sections 3, 7, 8;
`coord/DECISIONS/0050-track-b-g2-held.md`; `stage/REVIEW-wave3.md` section "Batch 39";
`population/JOURNAL.md` entries 2026-11-27 19:36 to 20:12 (predictions G8a-G8c, W0-W5, outcomes).

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`.

## Running at the end of the session (each must be read; none to be killed)

| What | How it is read |
|---|---|
| q0107 `pop_s014_gr_p8_gd`: 128^3, eight per cell, Gamma driver (decision 0050 item 2b); run B-20261128-034731-640f4f4, Slurm job 5585 (pending, priority); release build v0.8; about 0.85 card-h; chain | `harness/bin/nrpic-queue show q0107`; `$S/B-20261128-034731-640f4f4/chain/events.log`. When DONE: `harness/bin/nrpic-run finish B-20261128-034731-640f4f4`; analyse with `population/scripts/analyze_gr.py` as for B-20261124-210431-6bf48af (the one-per-cell partner, same options) and compare band rms with `compare_legs.py` (band_rms2, |k| <= 8 k_f, corrected spectra) at a = 64, 100, 132: judge G8a (within 1 per cent at 64, 100; 2 at 132; refuted outside 0.95-1.05), its corollary (8 ppc gauge ratio against q0006's zero-shift member reproduces 0.950, 0.803, 0.643 within 2 per cent), G8b (no guard stop; momentum constraint at a = 141 at or below the 1 ppc Gamma-driver member's 0.18-0.20), G8c (0.6-1.2 card-h; refuted above 2). Then `weyl_gauge.py split`-style statistics on it and on q0006 (B-20261124-223926-33194d9 + continuation -20261125-221742-5100a22): does the gauge difference of the invariant shrink at eight per cell? (write that prediction first) |
| W5: 256^3 mesh scale of the invariant, background run B-20261128-040950-1404d91 (`weyl_gauge.py split --t256 14 18 21`, 3 cores, started 20:09 PST, perhaps an hour) | `tail $S/B-20261128-040950-1404d91/run.log`; when ended: `harness/bin/nrpic-run finish B-20261128-040950-1404d91`; read `weyl_split.json` table entries `M_*` (256/128, Gamma driver) against `R_*` (gauge ratio) at a = 100, 132: W5 (population/JOURNAL 20:10) is refuted if every mesh difference is below half the gauge difference at a = 132; regenerate the figure with `weyl_gauge.py fig --split-dir` of this run |
| Initial data 256^3, eight per cell: B-20261128-030420-33ccdca (one core, since 19:04 PST, 30-55 h) | as before: `tail $S/B-20261128-030420-33ccdca/run.log`; finish; check I1-I4 (population/JOURNAL 2026-11-27 19:02); then the 256^3/8 ppc card member (command in the batch-37 HANDOFF, git show a92d32519:tracks/B-emd-gw/HANDOFF.md, section 'The card member to queue'; decision 0050 says it is not waited for) |
| Stage verify of this batch (log `$S/tmp/verify_b39.log`, ends with `exit=`) | if it ended after the last commit: commit stage/G2/VERIFY_RESULTS.*, run `harness/bin/nrpic-stage report B-emd-gw G2`, commit STAGE_REPORT.md. Expected FAIL only on `runs` (the running runs above) |

## What G2 waits for

The second review limited to C2 (decision 0050 item 3), after (b) q0107 is read, and W5. Send the
orchestrator one line (outbox) when both are judged. Condition (a) as measured this session is not
met (W2 failed, W4 refuted): see population/JOURNAL 20:10 and 20:12. Do not reword that.

## Results of this session (registered, figures looked at)

- Invariant reader on analytic waves: B-20261128-034232-f589717 (earlier -033822-a9f17e5,
  -033937-4b23e2f; first -033804-a68e9a1 failed). Gauge pair statistics: B-20261128-040834-8e1587d.
  Figure: B-20261128-041012-0e5b3f2 (population/figs/weyl_gauge.png). Stopped by hand, on record:
  B-20261128-033853-e516942, -034914-1e7a68f.
- Note v6 (B-20261128-035351-296cf80), ladder (B-20261128-035439-399549b), gate review corrections,
  scope amendments (scope/SCOPE.md section 6, 2026-11-27).

Traps:
- `weyl_gauge.py data` runs the track's band reader (analyze_gr._dump_job) and is slow after a = 64
  (7 min per 128^3 dump with 256^3 dumps beside it); use `split` for the invariant (13 s per dump).
- 256^3 Weyl statistics need about 25-30 GB per worker; at most 3 workers at once.
- GR particle files carry the rest-mass weight (R25): use `--equal-mass`.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores.
