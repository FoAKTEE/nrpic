# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 29, wave 3, 2026-11-26
14:18-15:05 PST: decision 0046 item 2, the two cheap runs required before G2, and the GM
analysis restarted). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md,
not changed this session: no stage package in batch 29). Three processor runs of B go on in the
background; nothing of B is in the card queue (the C3 card member waits for its initial data).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `coord/DECISIONS/0046-rulings-after-batch-28.md` item 2;
`shear/JOURNAL.md` entries 2026-11-26 14:25 (predictions N7a-c) and 14:29 (first member);
`population/JOURNAL.md` entry 2026-11-26 14:25 (C3 predictions); `stage/G2/OPEN.md`.

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`. Close every run below with
`harness/bin/nrpic-run finish <run id>` once its run.log ends with `# exit=`.

## Running at the end of the session (processors, background, outlive the session)

| Run id | What | How it is read |
|---|---|---|
| B-20261126-222544-f3a5176 | shear series 7 (C1): beta = 0.125, H L = 4, N_y = 64, 128, 256 at 4 per cell along y, snapshots every 0.25, release v0.8 processor build; about 35 min from 14:25 | finish; then register `python3 tracks/B-emd-gw/shear/scripts/series7_judge.py --run $S/B-20261126-222544-f3a5176 --out '$NRPIC_RUN_DIR'` (`--package tracks/B-emd-gw/shear`, one core); look at series7.png; judge N7a (no crossing before t_A), N7b (128-256 difference at most half the 64-128 one, Richardson error below 3e-3, constraint means falling 1.5x per doubling; refuted at a ratio of 0.7 or more), N7c (abs Delta extrapolated 0.007-0.065) in shear/JOURNAL.md; C1 per decision 0046: converges => L2's failure attributed to stream crossing; not => an error of the code |
| B-20261126-222552-2e44186 | 64^3 relativistic initial data at 8 per cell (C3 step 1): `run_gr_ic.sh 64 8 "--nc 3.2 --sigma1 0.014 --seed 1 --ppc 2 --outer 36"`; 30-60 min from 14:25 (log buffered: make_ic.log fills at the end) | finish; check `$S/B-20261126-222552-2e44186/gr_L8_n64/meta.json`: mesh_modes_kept 146 and sigma1_realized 0.012343 (the 128^3 data's, within 1e-3 relative), max_hamiltonian_residual below 1e-10; then queue the card member (line below) |
| B-20261126-221911-a0531db | GM2/GM3 analysis: `analyze_gr.py --equal-mass --workers 4 --times 4,8,12,14,16,18,20,21 --halo-times 14,16,18,20,21` on the 256^3 Gamma-driver box (q0060's run B-20261126-105021-6343c13); started 14:19; the first try (B-20261126-212212-c54d979, 5 workers, foreground) was killed by SIGTERM with its session after 42 min and closed failed | finish; register `compare_legs.py --base $S/B-20261125-115558-2ab4161/analysis_gr_gd.json --halo-base $S/B-20261126-022407-87e8803/analysis_gr_gd.json --leg m256gd:$S/B-20261126-221911-a0531db/analysis_gr_m256gd.json`; look at pop_legs.png; judge GM2 (band ratio within 5 per cent to a = 64, 0.8-1.2 before a = 100, within 20 per cent to a = 132; Omega_cor all shells at a = 121 1.0-2.0x, refuted outside 0.8-3) and GM3 (counts inside 2 sqrt(N) + 2 at a = 64-132, largest mass within 10 per cent) as predicted in population/JOURNAL 2026-11-26 13:22 |

The C3 card member, to queue once the data above are checked (commit first; priority 2):

```
harness/bin/nrpic-queue add --label pop_s014_gr_p8_n64 --priority 2 -- --kind scouting --gate G2 \
  --package tracks/B-emd-gw/population --purpose "population C3 (decision 0046 item 2b): 64^3 at 8 per cell, zero shift, sigma1 = 0.014, to a = 143; mesh pair with the 128^3 member B-20261124-223926-33194d9 + B-20261125-221742-5100a22; predictions C3a-b, population/JOURNAL 2026-11-26 14:25; initial data B-20261126-222552-2e44186" \
  --launcher chain --exe /data/haiyangw/nrpic/.work/build_gpu_v08/src/athena --gpu-hours 1 -- \
  tracks/B-emd-gw/population/inputs/pop_gr_run.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 \
  meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 mesh/x1max=8.0 mesh/x2max=8.0 mesh/x3max=8.0 \
  particles/particle_file=$S/B-20261126-222552-2e44186/gr_L8_n64/particles.nrp \
  problem/id_file=$S/B-20261126-222552-2e44186/gr_L8_n64/fields.bin
```
(`$S` written out in full.) Read it with the registered `analyze_gr.py` constraint part or the
cstat history (`*.cstat.hst`: Hr_mean, Mr_mean against t) beside the 128^3 member's history at
the same times; judge C3a (Hr ratio 64/128 1.5-4 at a = 25-141; refuted below 1.2 at a >= 49) and
C3b (Mr ratio at least 1.2 at a = 49-141), with a figure.

## What G2 still needs (stage/G2/OPEN.md)

- C1: series 7 judged (above); the case L2 as run stays failed on record.
- C3: the 64^3 member judged (above); the predictions that failed at one per cell stay on record.
- C2, C11: GM2/GM3 (above); the mesh figure in the shifted gauge is that comparison's pop_legs.png.
- C17: one paragraph on GM2/GM3 (and on C1, C3 outcomes) in note section VI, a ledger row (run key
  in note/scripts/common.py RUNS, row in ledger.py values_g2/LEDGER_G2), registered run_all.py,
  compile, checker (`python3 ~/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile`).
- C18: the fresh verifier is sent by the orchestrator when C1 and C3 have been read (0046).
- Then stage collect/verify/report once (`nrpic-stage verify B-emd-gw G2 --full` hashes hundreds of GB).

Traps:
- Analyses longer than a session: `nrpic-run submit --background` (a foreground run dies with the
  session's shell: that is what killed B-20261126-212212-c54d979).
- GR particle files carry the rest-mass weight (R25): use `--equal-mass`.
- The shear design estimate (Zel'dovich) underestimates the compression 2-3 times: at beta = 0.125
  the N_y = 64 member crosses at t = 9.25 (after t_A = 4.12); judge crossing before t_A only.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores
  (this session used 6: 4 GM workers, 1 shear, 1 initial data).
