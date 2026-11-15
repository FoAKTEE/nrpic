# stage/G0: the independent verifier's package (wave 2)

The verifier's files in this directory are `VERIFIER.md` (the verdicts, the three weakest
points of the plan, the comparison with the track's own review), `JOURNAL.md`
(predictions before each test and outcomes, failed ones included), `verify/` (scripts),
`figs/` (PNG copies of the figures, each looked at) and this README. The other files here
(`STAGE_REPORT.md`, `EVIDENCE.md`, `OPEN.md`, `CHECKLIST.md`, `REPORT.md`) belong to the
lead and the note helper.

## Runs (manifests under `tracks/D-bh-dress/runs/<run_id>/`, outputs under `scratch/D-bh-dress/<run_id>/`)

| Run | Claim | What | Registered by |
|---|---|---|---|
| D-20261115-170002-8cefc3e | C1 | `verify/v1_es_slice.py`: the D-pre-1 table rechecked from its rows alone | nrpic-run (outputs moved into the run directory by hand, see manifest notes) |
| D-20261115-170224-924d1d9 | C1 | `verify/v1b_code_t0.sh`, `v1b_compare.py`: t = 0 code check on the release processor executable, cell-by-cell against wave 1 | nrpic-run |
| D-20261115-171508-94e8cb1 | C2 | `verify/v2_drift.py`: D-pre-4 drift from the raw finder output | hand (`verify/hand_run.py`) |
| D-20261115-171532-ba23a99 | C3, C5 | `verify/v3_turnaround_capture.py`: turnaround, absorption, capture threshold | hand |
| D-20261115-171534-ff5b0e9 | C6 | `verify/v6_spike_constf.py`: constant-f spike by own quadrature | hand |
| D-20261115-171543-d966aba | C7 | `verify/v7_mcvittie.py`: McVittie horizon mass (sympy) | hand |
| D-20261115-171545-d7e01a7 | C8 | `verify/v8_cost.py`: cost model against the D-pre-4 card-hours, finest level against the horizon | hand |
| D-20261115-171953-908afff | C8 | `verify/v9_mesh.sh`: MeshBlock counts of the M/8 ... M/64 meshes from the release executable (`-m`) | hand |
| D-20261115-171818-a5aefe8 | C4 | rerun of the track's `secondary_infall/selfsimilar.py --taumax 300` | hand |
| D-20261115-171733-633d422 | C4 | `verify/v4_driver.sh` (first shell runs; stopped after two of five variants, see JOURNAL entry 8) | hand |
| D-20261115-173149-7c6dd72 | C4 | `verify/v4_driver2.sh`: shell code with velocity step limit, N = 2000-16000, comparison with the self-similar m(lambda) (`v4b_compare.py`) | hand |

All runs are on processors (no card time). Development runs of the scripts went to
`scratch/D-bh-dress/tmp/` and are not cited for numbers.

## Rerun

From the worktree root, with the worktree's `.venv` (numpy, scipy, matplotlib, sympy):

    python3 tracks/D-bh-dress/stage/G0/verify/hand_run.py --purpose "..." -- \
        .venv/bin/python tracks/D-bh-dress/stage/G0/verify/<script>.py [args]

(or `harness/bin/nrpic-run submit --package tracks/D-bh-dress/stage/G0 ...` when the
worktree is clean). Arguments as in the manifests' `command`. The scripts read only
registered outputs under `scratch/D-bh-dress/`, the release executables and
`kb-data/raw/arxiv/1305.2619/` (SFW), and write into `$NRPIC_RUN_DIR` plus one PNG copy
into `figs/`.

## Requests

- To orch (harness): `nrpic-run submit` refuses the whole worktree while any helper's
  untracked file lies outside `tracks/` (here `es.horizon_summary_0.txt` in the worktree
  root, written by another helper's run); helpers sharing a worktree then fall back to hand
  registration. Also: a local command given `--out $NRPIC_RUN_DIR` on the command line is
  not expanded (no shell); say so in `--help` or substitute the placeholder.
- To core: the horizon finder writes `<basename>.horizon_summary_<n>.txt` into the working
  directory instead of the `-d` output directory (the stray file above).
- To the lead of D-bh-dress:
  (1) restate the G1 numbers of SCOPE.md section 5 and REPORT.md section 4 against computed
  references: D-pre-2 constant f 2.59 and 9.2 percent (not "3" and "15 percent"); D-pre-3
  AthenaK Newtonian mode against the self-similar m(lambda), not "slope -9/4 +- 0.05 on
  [2 dx, r_ta/2]" (the solution's own mean slope there is -2.35);
  (2) redo the cost of every M/32 and M/64 item with the MeshBlock counts of run
  D-20261115-171953-908afff (3200, 4712, 7848 instead of 456, 512) and size the finest
  region to the horizon's coordinate radius (1.67 M at 500 M);
  (3) take the noise floor in the bubble set-up itself (matched control, as risk R3 of the
  stage report already says) and test the boundary attribution before quoting a floor;
  (4) my commit 633d422 included your new `STAGE_REPORT.md` as it stood in the worktree at
  09:17 local time (content unchanged; my `git add` of the directory picked it up); later
  commits add only the verifier's own paths.
