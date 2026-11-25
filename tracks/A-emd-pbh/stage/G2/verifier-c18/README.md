# verifier-c18: fresh verifier of item C18 of gate G2 (Track A), batch 18

Helper of A-emd-pbh, 2026-11-25 (decision 0016 item 4, decision 0039 item 2(b)). Recomputes the
numbers of `conv_ball/README.md` and `threshold_ball/README.md` from the registered raw card outputs
with readers and an exact reference of its own; no card run. Report: `../VERIFIER-C18.md`.

## What is here

| path | content |
|---|---|
| `JOURNAL.md` | predictions before every run (entries 1-4, 3a, 3b), outcomes, failed predictions, two defects of my own reader |
| `tables.json` | the eleven tables (data set 3, its 1.25 and 1.35 balls, eight threshold tables) with the exact values the packages quote |
| `scripts/vread.py` | readers: finder summary (with the status file; repeats of the last success removed), trajectories and trajectory metric, tab lines |
| `scripts/vref.py` | exact LTB dust solution from a format-2 table (Misner-Sharp mass, energy, cycloid: turnaround, trapping, areal radius) |
| `scripts/vmeasure.py` | ddet (three interpolations), dtrap, exact horizon mass on the code's slice with its bracket, the persistence rule of threshold_ball entry 1, line constraint ratio, line MOTS |
| `scripts/vmembers.py` | the members' raw output directories and the table each used |
| `scripts/vtests.py` | V0a-f: tests on analytic fields (closed FLRW table, synthetic records and summaries, Schwarzschild line) and the exact events of the tables |
| `scripts/vconv.py`, `scripts/vthresh.py` | recomputation of conv_ball and threshold_ball, figures |
| `scripts/vtable.py`, `scripts/vwindow.py` | claim-by-claim tables; mass medians over the windows of threshold_ball entry 11 |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |

## Runs (all registered, processors, one core)

A-20261125-131605-f9e71ee (V0 final), A-20261125-131436-e9ef7fb (conv_ball), A-20261125-131745-5388fde
(threshold_ball, final), A-20261125-131935-bbac6fd (tables), A-20261125-131954-8c80a3f (windows).
Superseded or withdrawn, on record: A-20261125-130535-b79555d, A-20261125-131418-1b00953 (V0),
A-20261125-130753-314837e (conv_ball, identical numbers), A-20261125-131148-99204e1,
A-20261125-131458-396f809 (threshold rule outcomes withdrawn: reader defects, JOURNAL 3a, 3b),
A-20261125-131608-2269f36 (threshold, same numbers as -131745 without the mass figure).

## How to rerun

From the worktree root, each with `harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/A-emd-pbh/stage/G2/verifier-c18 --cores 1 -- bash -c '...'` (the exact commands are in the
manifests under `tracks/A-emd-pbh/runs/<run id>/`):

    python -I tracks/A-emd-pbh/stage/G2/verifier-c18/scripts/vtests.py --out "$NRPIC_RUN_DIR" --tables tracks/A-emd-pbh/stage/G2/verifier-c18/tables.json
    python -I tracks/A-emd-pbh/stage/G2/verifier-c18/scripts/vconv.py --out "$NRPIC_RUN_DIR"
    python -I tracks/A-emd-pbh/stage/G2/verifier-c18/scripts/vthresh.py --out "$NRPIC_RUN_DIR"
    python -I tracks/A-emd-pbh/stage/G2/verifier-c18/scripts/vtable.py --conv <vconv run dir> --thresh <vthresh run dir> --out "$NRPIC_RUN_DIR"
    python -I tracks/A-emd-pbh/stage/G2/verifier-c18/scripts/vwindow.py --series <vthresh run dir>/vthresh_series.npz --out "$NRPIC_RUN_DIR"

Each takes seconds (vthresh about 20 s).

## Requests

- To the lead of A-emd-pbh: read finder outcomes from `<base>.horizon_status_0.txt`, never from the
  summary alone (it repeats the last success after a failed search, and prints time with six digits);
  state the interpolation used for ddet and its spread near the core edge (VERIFIER-C18.md 5e); give
  the exact-mass bracket of the tracked set with every mass error below about 3e-3 (5f); name the time
  measure of the threshold (5g).
- None to other owners.
