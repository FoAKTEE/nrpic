RELEASE core-v0.8 01d4aeeb847925b25a9a831c97b7f2aea8127310 REGRESSION PASS

NOT RELEASED. Card check of the card executable of this source: PENDING (shared-queue entry
q0049, label `core-rf-card`, worktree wt/core-s4, added 2026-11-25; commands in
`HANDOFF.md` and `JOURNAL-restart-finder.md` entry 20). The processor results below do not
depend on it.

# Release candidate core-v0.8: branch core/restart-finder on top of core-v0.7

Prepared by the lead of core on 2026-11-26 UTC (2026-11-25 PST; batch 23). The commit of the
first line is the source commit (last change of `athenak/`, `python/`, `problems/`,
`scripts/`, `docs/`); `core/nrpic` holds it through the merge b755cdcf, and `git diff
b755cdcf origin/core/restart-finder -- athenak python problems docs scripts` is empty
[VERIFIED at b755cdcf]. Options, changes without an option, formats:
`tracks/core/CHANGELOG.md`, section "For core-v0.8". Predictions and outcomes:
`tracks/core/JOURNAL.md`, entry 2026-11-26T02:25Z (R8, Q8), and
`JOURNAL-restart-finder.md` (P1-P18, K1-K5).

## Processor evidence

| Check | Run | Result |
|---|---|---|
| R8 byte regression, serial build of the merged tree (`scratch/core/b23_build_cpu`, not published) against `.work/build_cpu_v07/src/athena`, twelve set-ups | core-20261126-024438-1fa17dd (figure core-20261126-031446-af637b5) | 75 of 75 identical, REGRESSION PASS |
| Q8 `restart_test.py`, restart outputs across cuts at every residue of the record interval and a chain | core-20261126-024518-e1e16dc | ALL OK (19 checks); the release loses tracker records, one `cons.hst` record, and repeats history headers |
| Branch tests (finder polishing, excision guard, two-puncture tracker files, figstyle) | `JOURNAL-restart-finder.md` entries 13-19 | held, except P9 (rule changed) and part of P17 |

## Executables

None published for v0.8 yet. The branch published `scratch/core/exe/core_restart-finder/`
(athena_cpu, athena_cpu_omp, athena_gpu of the same source 01d4aeeb; READY there). After
q0049: publish `scratch/core/exe/core_nrpic_v08/` (a new directory), then the release builds.

## Card checks pending

q0049 (K1-K5 of `JOURNAL-restart-finder.md` entry 12): `nrpic-run finish <run>`, then
`tracks/core/analysis/restart_finder/card_check.py --card <run dir> --cpu-restart
scratch/core/core-20261125-142556-a424739 --cpu-finder scratch/core/core-20261125-141832-01d4aee
--out '$NRPIC_RUN_DIR'` (registered); the script has never read card output.
