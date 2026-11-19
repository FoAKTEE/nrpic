# HANDOFF of F-hills

State in three lines (2026-11-19, end of the lead session of wave 2b):
- G0: package complete except the verifier's report (`stage/G0`, C18 open; SECOND_CHECK.md is a
  second agent's check of the plan; verifier asked of orch). G1 not met (`stage/G1/STATUS.md`).
- The first full-GR passage P1 (q = 4, members at m/8) is submitted as a chain: run
  F-20261119-150017-b45ec5f, Slurm 4650 (pending at 15:00Z; 17-20 card-hours, up to 26 segments).
- S2g (core's mass-scaled shift damping on a single member) is queued: run
  F-20261119-143443-f11ebb9, Slurm 4640; its analysis (E10) is not done.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`.

Run next: harness/bin/nrpic-run status F-20261119-143443-f11ebb9 && harness/bin/nrpic-run status F-20261119-150017-b45ec5f

## Exact commands

1. S2g, when Slurm 4640 has ended (`squeue -u $USER`):
   `harness/bin/nrpic-run finish F-20261119-143443-f11ebb9`, then the two analyses of
   `tracks/F-hills/nr_first/README.md` section "Pending" (s2g_compare.py and single_analysis.py
   with S3, S2, S2g; S = scratch/F-hills/F-20261115-173601-2fae2dc, G = scratch/F-hills/
   F-20261119-143443-f11ebb9). Record E10's outcome against its prediction in
   `nr_first/JOURNAL.md` (criteria unchanged), read the figures.
2. P1: `scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f`
   (segments, STATUS, events.log). Do not resubmit while a segment is pending or running. If a
   segment FAILED on the slot limit, resume the same run directory with a higher
   `mesh_refinement/max_nmb_per_rank` (at most about 3000: 26.2 MiB per slot on an 80 GB card).
   When the chain is DONE: `harness/bin/nrpic-run finish F-20261119-150017-b45ec5f`, then
   `harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/nr_first
   --cores 1 --parent F-20261119-150017-b45ec5f --purpose "P1 analysis" -- .venv/bin/python
   tracks/F-hills/nr_first/scripts/p1_analysis.py /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f
   '--out=$NRPIC_RUN_DIR' --baselines=tracks/F-hills/nr_first/results/baselines_p1.json` (without
   `--out` the script writes into P1's run directory), and compare with the P1 prediction in
   `JOURNAL.md` (lead, wave 2b). An intermediate analysis on the segments done so far is allowed
   (same command; the chain keeps writing).
   Tracker files of earlier segments are in `<rundir>/trk_keep/`; `nrread.read_trackers` joins them.
3. G1 work that needs no card: the junk energy of P1's spheres once it passes t = 150 M; Kerr row
   of F-pre-2 (2402.02178); G1 schematics (updated architecture, data flow) and the note's G1
   section; then `harness/bin/nrpic-stage report F-hills G1`.

## Files to read first

`CLAUDE.md`; decisions 0013, 0014, 0016, 0017; `tracks/F-hills/STATUS.md`;
`stage/G1/STATUS.md` (criteria, P1); `stage/REVIEW-wave2.md` (what was checked, what is wrong);
`JOURNAL.md` last entry (V8-V11, the P1 decision and prediction); `nr_first/README.md` and
`nr_first/JOURNAL.md` E3, E7, E10, E11; `RISKS.md`.

## Decisions pending

- orch: a fresh verifier for G0 (or a ruling that SECOND_CHECK.md serves), outbox
  `20261119T151429Z__to-orch__verifier-g0-g1.md`; P1 was submitted into a non-empty queue
  (`...__to-orch__p1-submitted.md`).
- core: tracker files on restart, finder at 4 cells per radius, found flag, mass-scaled damping
  with three holes (outbox `20261119T1514*__to-core__*`).
- Gauge of the passages after P1: depends on S2g and core's three-hole answer.
- The wave-3a package `eih/` (1PN three-body reference, its own runs and a P1 prediction) is
  handed to the next lead: review it from its artefacts before using its numbers.

## Traps

- The chain wrapper `nr_first/scripts/athena_keep_trackers.sh` is the only thing that keeps
  tracker files across segments (AthenaK truncates them on restart).
- Horizon summaries: a failed search repeats the previous row; use `nrread.read_horizon` (fixed)
  and read masses only with hrms < 1e-3 (members from t = 0.5 M, heavy hole from about 4 M).
- `single_P025.athinput` needs `mesh_refinement/max_nmb_per_rank=2400` (1632 blocks after the
  first regrid: E11).
- Member energies: against the barycentre of the heavy hole and the captured member (newton3_fix);
  against M alone they oscillate by +-0.37 units at q = 4.
- "r_p" of an NR passage depends on the reading of the puncture momenta: P1 9.81 M (Newtonian)
  against 9.25 M (GR, hole frame); the q = 10 input turns at 5.77 M in GR.
- Run ids: `F-<UTC>-<commit7>` from nrpic-run; wave-1 ids `F-hills-...` (the novelty helper's in
  local time). Never kill by pattern; `scancel` or `harness/bin/nrpic-run stop <id>`.
- Another helper (wave 3a, `eih/`) may commit in this worktree at the same time: commit
  path-limited (`git commit -- <paths>`).
