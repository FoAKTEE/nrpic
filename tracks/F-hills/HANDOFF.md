# HANDOFF of F-hills

State in three lines (2026-11-15, after the lead session of wave 1):
- G0 package written (`stage/G0/SCOPING.md`, `EVIDENCE.md`, `OPEN.md`; not yet through the stage
  check). Both reference models exist and reproduce the literature; no NR run has been made.
- G1 not met: the three-puncture runs R0, R2, R4 and the passage P1 are fully specified in
  `stage/G1/STATUS.md` but need `core/multi-puncture`, which is not released.
- New: at q = 10 the geodesic reference captures a member in most phases where Newton has none
  (lead runs V6, V7); P1 (q = 10, r_p = 8 M) tests exactly this.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`.

## Exact command to run next

1. Check whether core has released the capability: `git log --oneline main | head` and
   `grep -n multi CLAUDE.md`, and read the replies to `outbox/20261115T1507Z__*`
   (`harness/bin/nrpic-ctx inbox`).
2. If released (or orch allows scouting with core's executables), run R0 on processors (minutes):
   `/data/haiyangw/nrpic/wt/core-mp/.work/build_cpu/src/athena -i tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput -d /data/haiyangw/nrpic/scratch/F-hills/<run_id> time/nlim=0`
   (and the two variants of `stage/G1/STATUS.md`), registered by hand under `runs/<run_id>/`;
   then R2, R4 and P1 with `scripts/submit_chain.sh` as written there.
3. If not released: fix newton3's finite-q energies (see Traps) and rerun
   `python3 scripts/compare_full.py finiteq --workers 6` and `p3` in `tracks/F-hills/newton3`,
   then `scripts/analyze.py finiteq|p3 <run>`.

## Files to read first

`CLAUDE.md`; `coord/CHARTER.md` (sheet 9.9); `tracks/F-hills/STATUS.md`; `stage/G0/SCOPING.md`
(everything in one place); `stage/G1/STATUS.md` (the runs); `JOURNAL.md` (last entry: the lead's
checks V1-V7 with predictions and outcomes); the four helper READMEs
(`novelty/README.md`, `newton3/README.md`, `geodesic_binary/README.md`,
`three_punctures/PLAN.md`).

## Decisions pending (outbox to orch)

Allotment (G1 margin to 50, G2 about 120) and mass ratio of the scan lines (q = 4 for
convergence); timing of object (b) (right after the first (a) passage); the correction to brief
l. 275; a second-agent check; how and when P1 may start.

## Traps

- `runs/` is in `.gitignore`: manifests need `git add -f tracks/F-hills/runs/<run_id>`.
- `python3 -I` hides the user site-packages with numpy: analysis scripts run without `-I` (they
  read only repository files); the uv venv `scratch/F-hills/venv-gb` has numba, numpy, scipy,
  matplotlib (needed by `geodesic_binary/hrna.py` and `stage/G0/checks/lead_checks.py`).
- newton3 energies at finite q (`hills3/threebody.py::_pair_energy` against M alone) oscillate
  when the other member stays bound; use the energy against the barycentre of M and the captured
  member (`lead_checks.py v5b`) until fixed. The PLAN's E1 = +1.75 / +1.53 are superseded by
  +1.613 / +1.312.
- geodesic_binary's `phase` is the release phase (2404 convention), newton3's is the effective
  phase at pericentre: map by the binary orientation of a common state, as `lead_checks.py`
  does.
- HRNA stops when the centre of mass turns around (bound CM) or leaves 30 r_t; a captured member
  may not have reached its second pericentre (q = 4 case, V6).
- The novelty helper's run ids use local time (UTC-8); all others UTC.
- Never kill by pattern; use numeric PIDs, `scancel`, or the chain helper.
- The task's name `REPORT.md` for the G0 document was refused by the session's write tool; the
  document is `stage/G0/SCOPING.md`.
