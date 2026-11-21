# code_kb: the code side of the knowledge base (wave 3, batches 1 and 8)

Helper package of owner kb. It covers the upstream watch of AthenaK (decision 0015), the
K7 module descriptions and task-list order (brief 12.7), the verdicts of the 25 curated
paper-code links (request "kb paper-code-links"), the `<z4c> nco` question and the
parameter index at main. No card time was used. Predictions and outcomes are in
`JOURNAL.md`, including the predictions that failed.

## What is here

| Path | What |
|---|---|
| `JOURNAL.md` | predictions before each test, outcomes after (W1, W2, M1, P4, L1, E1, E2, F1) |
| `LINKS.tsv` | verdict, area, test entries (file:line, commit), records, reach locators, outcome and note for each of the 25 links (from run kb-20261121-232843-cbf311f) |
| `scripts/watch_diff.py` | line counts of the src/z4c and src/particles changes between two watch snapshots (W2) |
| `scripts/link_evidence.py` | encodes and checks every locator of the 25 verdicts; also scans athenak/src for `nco` (standard library, `python3 -I`) |
| `scripts/apply_verdicts.py` | writes LINKS.tsv into the status and evidence columns of `kb/curated/paper_code_links.tsv` and changes nothing else |
| `scripts/figs.py` | the three figures and the parameter-index rows of `nco` |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py`, unchanged |
| `figures/fig_link_verdicts.{pdf,png}` | verdicts by area |
| `figures/fig_task_order.{pdf,png}` | one cycle of Driver::Execute, local/nrpic against upstream: particle tasks, tasks that write tmunu, Z4c tasks that read it |
| `figures/fig_watch_summary.{pdf,png}` | watch of 2026-11-20: branch counts, changed files under src/z4c and src/particles |

This package's code outside the directory: `kb/kbtool/code_modules.py`, the `kb code
modules` route in `kb/kbtool/code_cli.py`, `kb/tests/test_code_modules.py` (12 tests), the
generated `kb/reports/code_modules.md`, `kb/reports/code_watch_upstream.md`, and the status
and evidence columns of `kb/curated/paper_code_links.tsv`.

## Commands (from the worktree root; register each with nrpic-run, see JOURNAL)

```text
kb/.venv/bin/python -I kb/bin/kb watch upstream                         # W1
python3 -I tracks/kb/code_kb/scripts/watch_diff.py ...                   # W2 (see the run manifest)
kb/.venv/bin/python -I kb/bin/kb ingest repo --this --ref main           # P4
kb/.venv/bin/python -I kb/bin/kb code modules --db kb-data/db/kb.sqlite --report OUT.md
                       # M1; without --db it reads db/current, the last snapshot
python3 -I tracks/kb/code_kb/scripts/link_evidence.py --out DIR          # E1
python3 -I tracks/kb/code_kb/scripts/apply_verdicts.py DIR/LINKS.tsv RUN_ID kb/curated/paper_code_links.tsv
kb/.venv/bin/python -I kb/bin/kb link load; kb ... link check --db kb-data/db/kb.sqlite   # E2
.venv/bin/python -I tracks/kb/code_kb/scripts/figs.py --links ... --modules-local ... \
    --modules-upstream ... --watch ... --db kb-data/db/kb.sqlite --out DIR             # F1
```

`kb code modules [--repo this|upstream] [--report PATH] [--no-write] [--json] [--db PATH]`
writes `kb-data/build/code/<repo>/modules.json` inside the writer lock. For src/z4c,
src/particles, src/pgen, src/mesh and src/bvals it gives each file's path, line count, the
first sentences of its header comment and the definitions from the code index. It also
extracts the order of the task lists from Driver::Execute, MeshBlockPack::AddPhysics, the
numerical-relativity queues and every AddTask/QueueTask call. It reads this repository
from git objects at the indexed commit, and the upstream clone as files after checking that
its HEAD is the indexed commit. Nothing is run.

## Results

| Item | Result | Evidence |
|---|---|---|
| Upstream watch | main unchanged at c5a0d7f9155a; 124 branches, 1 new, 1 removed, 3 moved. src/z4c changed on project/bbh and project/largesim-m1; new branch m1-nucleon-recoil differs from main in 61 src/z4c files (adds M1_SetTmunu). src/particles unchanged on every branch. Message to core sent | runs kb-20261120-221925-1630d0b, kb-20261120-222055-dd59ec1; `tracks/kb/outbox/20261120T222130Z__to-core__upstream-watch.md` |
| Parameter index | main carries core-v0.4 to v0.6. local/nrpic re-indexed at 47ab19ab: 869 files, 5030 symbols, 1386 parameter reads. 25 links checked, 0 problems | run kb-20261121-231826-3b32fc1 |
| Module descriptions | 156 files (local) and 119 files (upstream) in the five directories; 392 and 372 task registrations. Report generated and committed | runs kb-20261121-231936-a33f7f1 (5deee18, from the snapshot), kb-20261121-232013-52c350a (47ab19ab); `kb/reports/code_modules.md` |
| Task order | Prediction M1 held at 5deee18 and at 47ab19ab. Particle sources are deposited once per step in after_timeintegrator and held through the stages; upstream refreshes tmunu at every stage | same runs; `figures/fig_task_order.png` |
| Link verdicts | 19 verified, 5 claimed (M18, M19, M20, M24, M25), 1 refuted (M23); 203 locator checks, 0 failed; loaded into impl_links | runs kb-20261121-232843-cbf311f, kb-20261121-232940-3759b31; `LINKS.tsv`; `figures/fig_link_verdicts.png` |
| `<z4c> nco` | Dead. No read in athenak/src at 47ab19ab and no parameter-index row. The trackers are counted from `co_<n>_type` (z4c.cpp:256-262) | runs kb-20261121-232843-cbf311f, kb-20261121-232940-3759b31, kb-20261121-233234-7319264 |
| Figures | Three figures, each inspected | runs kb-20261121-233219-304e3e7 and kb-20261121-233234-7319264 (the second, after a label fix, is the one in `figures/`) |

Failed predictions (details in JOURNAL):
- W2: no file has more than 500 changed lines. Wrong for the new branch, because it was
  compared with a main two months older than its tip.
- P4: file count up by 20 to 40. It rose by 79, almost all new example inputs.
- L1: 0 refuted. M23 was refuted.
- E2: nco hits in input files. The param query covers source reads only.

## Open items

- M18, M19, M20, M24, M25 need a test from core, or core's confirmation of kb's
  candidates (outbox message of 2026-11-21).
- M23: if core confirms, the curated row needs a new symbol (NrpicWriteHistory). That
  column is outside this package's write permission (status and evidence only), so the
  kb lead makes the change.
- The comment at the top of `kb/curated/paper_code_links.tsv` (lines 7-8, "Status `claimed`
  throughout") is now stale. Comment lines are outside this package's columns, so the kb
  lead updates them.
- Not tested: the number of explicit stages (`nexp_stages`) of the integrators the runs
  use. The extraction reads the loop, not its count.
- The watch was not repeated this session. It ran 25 h earlier in the same wave; the next
  weekly watch is due about 2026-11-27.
- The whole kb suite has one failure outside this package:
  `test_meta_papers.py::test_additions_file_is_valid` (61 additions against 26). It is
  ingest3's request.

## Requests

- core: the five claimed links and M23 (`tracks/kb/outbox/20261121T233243Z__to-core__paper-code-links-tests.md`);
  `<z4c> nco` can be removed from problems/jeans/jeans.athinput.
- kb lead: the stale comment lines of `kb/curated/paper_code_links.tsv`; the symbol of M23
  after core answers; close the request row "kb paper-code-links" in coord/REQUESTS.md
  through orch; a `kb snapshot`, so that `db/current` carries the 47ab19ab index (until
  then `kb code`/`kb code modules` without `--db` read 5deee18).
