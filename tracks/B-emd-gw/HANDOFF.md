# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 40, wave 3, 2026-11-27
23:26 PST to about 00:10: q0107 closed and partly judged; W5 found void; two analyses left running).
Rewritten every session.

State in three lines: G0 and G1 are signed. G2 is HELD, NOT SIGNED (coord/GATES.md; decision
0050). C2 reads FAIL in stage/G2/CHECKLIST.md and is now stated over the whole range (batch 40
addendum at the end of its evidence). A second review limited to C2 follows this session.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "running|submitted"`

Files to read first: `STATUS.md`; stage/G2/CHECKLIST.md item C2 (last paragraph, "Batch 40");
`population/JOURNAL.md` entries 2026-11-27 19:36 (G8a-G8c), 23:35 (W5 void; W5b, W6), 23:55
(outcomes so far); `stage/REVIEW-wave3.md` section "Batch 40"; `coord/DECISIONS/0050-track-b-g2-held.md`.

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`.

## Running at the end of the session (each must be read; none to be killed)

| What | How it is read |
|---|---|
| B-20261128-074111-e2fcd72: analyze_gr.py on q0107 (128^3, 8 ppc, Gamma driver) at t = 12, 14, 18, 21, two workers; started 07:41 UTC on a disk loaded by other owners (one 128^3 dump took 200-390 s instead of 13-35 s) | ended when `$S/B-20261128-074111-e2fcd72/run.log` has `# exit=`; then `harness/bin/nrpic-run finish B-20261128-074111-e2fcd72`; then the judgement, registered: `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/B-emd-gw/population --cores 1 --purpose "G8a, G8b, corollary" -- python3 tracks/B-emd-gw/population/scripts/judge_g8.py --gd8 $S/B-20261128-074111-e2fcd72/analysis_gr_p8gd.json --out '$NRPIC_RUN_DIR'`; read the JSON rows Pgd (G8a: within 1 per cent at a = 64, 100, 2 at 132; REFUTED outside 0.95-1.05), R8 against R1 (corollary: within 2 per cent of 0.950, 0.803, 0.643), Mr_gd8 at a = 141 against Mr_gd1 0.203 (G8b: at or below); look at judge_g8.png with the Read tool |
| B-20261128-074116-363f95f: weyl_gauge.py splitx (W5b, W6), three workers, then two for the three 256^3 dumps (25-30 GB each); every dump chosen by its header time (files printed at the top of run.log) | when ended: finish; rerun judge_g8.py with `--weyl $S/B-20261128-074116-363f95f/weyl_splitx.json` (panel d); judge W6 (R8 against R1, median and larger-lapse half, a = 100, 132: refuted if \|R8-1\| >= 0.8 \|R1-1\| for both at 132) and W5b (M against R: refuted if every \|M-1\| < 0.5 \|R-1\| at 132); table keys R1_*, R8_*, Pgd_*, Pzs_*, M_* (the ratios of the B_ij B^ij statistics; take square roots for amplitudes) |
| Initial data 256^3, eight per cell: B-20261128-030420-33ccdca (one core, since 19:04 PST, 30-55 h) | `tail $S/B-20261128-030420-33ccdca/run.log`; finish; I1-I4 (population/JOURNAL 2026-11-27 19:02); then the 256^3/8 ppc card member (command in git show a92d32519:tracks/B-emd-gw/HANDOFF.md, section 'The card member to queue'; decision 0050: not waited for) |

No card job of this owner is queued or running. q0107 is done and closed (0.774 card-h).

## What is established this session (registered; numbers with their runs)

- q0107 = B-20261128-034731-640f4f4 closed (finish: completed, exit 0, 164 files, 88.2 GB hashed).
  G8c HOLDS (0.7736 card-h). G8b guard part HOLDS (a = 141.7, STATUS DONE tlim, two SIGTERM cuts
  continued, no exit 3).
- W5 (B-20261128-040950-1404d91) is VOID: weyl_gauge.py's `split` mode took the 256^3 file index
  for t; chain segment ends add dumps (headers: file 5 t = 4.484, 11 t = 9.195, 17 t = 14.164,
  23 t = 19.414), so files 14, 18, 21 are t = 12, 15, 18. Its M_* ratios are not to be used (M_V
  = 0.45 = (49/64)^3 gave it away). The 256^3 particle files have no extra dumps (22 files at
  integer t), so the verifier's halo catalogues of that member are at the stated epochs.
- First W6 rows (a = 49 only): eight per cell leaves the gauge ratio of the Weyl invariant
  unchanged: I_B 0.9022 against 0.9021, median 0.9973 against 0.9976.
- C2 written as measured over the whole range in CHECKLIST.md (mesh in the driven gauge met; zero
  shift mesh not after a = 50; particle number zero shift met; gauge within 1.6 per cent only to
  a = 49; invariant not met; particle number in the driven gauge: waiting for G8a).
- Outbox: 20261128T075335Z__to-orch__g2-second-review-c2-ready-in-part.md.

## What G2 waits for

The second review limited to C2 (decision 0050 item 3). It can read G8a and W6 from the two runs
above when they end. Do not reword condition (a) as met: it is not (batch 39, W2 failed, W4
refuted), and at a = 49 the remainder does not fall with the sampling.

Traps:
- Pick dumps by the time in their header (`weyl_gauge.find_dump`), never by index, for any chain run.
- 256^3 Weyl statistics need about 25-30 GB per worker; at most 2-3 workers.
- The disk was saturated tonight; nrpic-run finish of a 30 GB run took 15 min, git status 30 s.
- GR particle files carry the rest-mass weight (R25): use `--equal-mass` for halos.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores.
