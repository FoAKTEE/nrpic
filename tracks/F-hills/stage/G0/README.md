# tracks/F-hills/stage/G0

The G0 stage package of F-hills, and in it the second check of wave 2.

## Files

| Path | Written by | What |
|---|---|---|
| `SCOPING.md`, `EVIDENCE.md`, `OPEN.md` | lead, wave 1 | G0 scoping, evidence, open items |
| `checks/` | lead, wave 1 | lead's checks V4-V7 (`lead_checks.py`, summaries, figures) |
| `SECOND_CHECK.md` | helper, wave 2 | second check of the novelty verdict and of the q = 10 baseline disagreement (results, tests, requests) |
| `JOURNAL.md` | helper, wave 2 | predictions before each run and outcomes after (entries 1-4) |
| `README.md` | helper, wave 2 | this file |
| `second_check/models.py` | helper | independent integrators: Newton with the hole fixed, full Newtonian three-body problem, HRNA of 2404.16270, diagnostic variant `hrna_sym`; capture criterion |
| `second_check/selftest.py` | helper | SC0 (a-c): conservation tests |
| `second_check/flat_binary.py` | helper | SC0d: moving binary in flat space (also runs hrna.py with `--hrna-py`) |
| `second_check/scan.py` | helper | SC1, SC3, SC4, SC6: phase scans at q = 10, 9 models x 9 r_p x 180 phases |
| `second_check/compare_hrna_py.py` | helper | SC2: geodesic_binary/hrna.py at the same phases |
| `second_check/nrstate.py` | helper | SC5: start state of `three_punctures/inputs/hills_q10_m8.athinput` under each model |
| `second_check/nr_invariants.py` | helper | SC7: GR invariants of that state |
| `second_check/figures.py` | helper | all figures and `compare.json` |
| `second_check/inspire_list.py` | helper | lists INSPIRE query records (run with `python3 -I`) |
| `second_check/figures/*.png` | helper | figures of runs F-20261115-181106-52c4613 and -175549-456bf4a |
| `second_check/compare_F-20261115-181106-52c4613.json`, `nr_invariants_F-20261115-175637-a592d7a.json` | helper | copies of the result files |

Runs of the second check (manifests in `tracks/F-hills/runs/<id>/`, outputs in
`/data/haiyangw/nrpic/scratch/F-hills/<id>/`):
- F-20261115-175542-b49d687 (failed: missing output argument)
- -175549-456bf4a (SC0)
- -175620-df20ffe (SC0d)
- -175614-5cc133d (scan)
- -180835-66e13b2 (SC2)
- -175636-5432651 (SC5)
- -175637-a592d7a (SC7)
- -181007-80649f5 (figures, superseded)
- -181106-52c4613 (figures)

## How to rerun

From the worktree, processors only, about 15 minutes in all. The numba environment is needed
only for hrna.py:

    cd /data/haiyangw/nrpic/wt/F-hills
    harness/bin/nrpic-run submit --kind scouting --gate G0 --purpose "..." \
        --package tracks/F-hills/stage/G0 --cores 1 -- python3 tracks/F-hills/stage/G0/second_check/selftest.py
    #   likewise: nrstate.py, nr_invariants.py (1 core);
    #   scan.py --nproc 6 (--cores 6, about 12 min)
    harness/bin/nrpic-run submit ... --cores 1 -- env NUMBA_CACHE_DIR=/data/haiyangw/nrpic/scratch/F-hills/tmp/numba_cache \
        /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python tracks/F-hills/stage/G0/second_check/flat_binary.py --hrna-py
    #   likewise compare_hrna_py.py --nproc 6
    harness/bin/nrpic-run submit ... -- python3 tracks/F-hills/stage/G0/second_check/figures.py \
        --scan <scan run dir> --flat <SC0d dir> --nrstate <SC5 dir> --hrnapy <SC2 dir> --selftest <SC0 dir>

INSPIRE queries go only through
`python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv --inspire-query "<q>" --size 25`.
List the records with
`python3 -I tracks/F-hills/stage/G0/second_check/inspire_list.py <record.json>...`.

## Requests

Requests to other owners (details in `SECOND_CHECK.md`, section Requests):
- R1 to the F lead: rebuild P1's momenta from the GR parabola, or restate P1 as a
  capture-boundary encounter.
- R2 to the F lead: qualify the HRNA percentages in `stage/G1/STATUS.md` and STATUS.md.
- R3 to the geodesic_binary helper: add the flat-space moving-binary test, and test the
  self-force at 2404's parameters.

Harness: every command worked. `nrpic-run submit` refused 12 cores while other helpers held
9; the scan ran on 6. No request to orch or core.
