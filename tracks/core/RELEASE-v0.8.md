RELEASE core-v0.8 01d4aeeb847925b25a9a831c97b7f2aea8127310 REGRESSION PASS, CARD CHECK PASS (K3 in part refuted, below)

Card check of the card executable of this source: PASS for what the release changes, run
core-20261126-070946-7971fde (shared-queue entry q0049, job 5364, 2026-11-26), judged by
the registered analysis core-20261126-114747-a6f2385 (`card_check.py`, figure
`fig_card_check.png` looked at). One prediction failed in part and stays on record: the
finder's rule without polishing gives other masses on the card than on the processors
(section "Card check"). Cost of a finder search on a card: 0.33 s for 100 polishing
iterations on a 512-point surface (3.3e-3 s per flow iteration).

# Release core-v0.8: branch core/restart-finder on top of core-v0.7

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
| MPI build smoke test: one rank against the serial build, two ranks against one (`analysis/release/mpi_smoke_v08.py`) | core-20261126-115451-893a30e | M1, M2 held: 17 files identical; two ranks identical to one rank (0.0) |
| Branch tests (finder polishing, excision guard, two-puncture tracker files, figstyle) | `JOURNAL-restart-finder.md` entries 13-19 | held, except P9 (rule changed) and part of P17 |

## Executables

Published 2026-11-26 by the lead of core in a new directory,
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/` (COMMIT, SHA256SUMS, READY there):
`athena_cpu` (serial; the build of R8 and Q8), `athena_cpu_mpi` (Open MPI; built in this
session from the same tree), `athena_cpu_omp` (threaded) and `athena_gpu` (one A100; the
executable that q0049 ran), all of the source tree 01d4aeeb (`git diff b755cdcf HEAD --
athenak/src python problems scripts docs` empty at the time of publication). The release
builds `.work/build_{cpu,gpu}_v08` in the main checkout are the clerk's.

## Card check

Run core-20261126-070946-7971fde: six runs of the card build in one job (list
`analysis/restart_finder/card/card_rf.list`), all with status 0, 7 min 54 s of the card.
Judged against the processor runs core-20261125-142556-a424739 (restart) and
core-20261125-141832-01d4aee (finder) by `card_check.py`; predictions K1 to K5 in
`JOURNAL-restart-finder.md` entry 12, outcome in entry 23. The first registered pass
(core-20261126-114526-2b1f001) failed on the reader (two tables of different width
compared by shape) and stays on record.

| Prediction | Outcome |
|---|---|
| K1 restart deck on the card | held: 48 tracker cycles, two header lines; twelve `cons.hst` records identical to the processors; the block in the restart files written one cycle before a record |
| K2 the card continues a processor restart file of cycle 27 | held: status 0, first record at t = 1.6875, six records identical to the processors |
| K3 finder, card against processors, each rule within 1e-8 | **held for the polished rule (2.2e-16) and the tight rule (3.3e-16); FAILED for `mass_tol` 1e-5 without polishing**: masses differ by up to 8.8e-6 after a search that ended at its cap, and at two of sixteen searches the card accepts a surface where the processors find none. The card is deterministic (the same rule with another guard gives the same masses, 0.0). Polished against tight on the card: 6.3e-8 at the ten searches where both are found (bound 2e-5) |
| K4 cost below 0.05 s per flow iteration | held: 3.3e-3 s; 100 polishing iterations 0.33 s per search; 16 searches cost 7.8 s (1e-5), 14.5 s (polished), 83.2 s (tight) |
| K5 guard `ah_exc_max_growth = 0.4` | held: no particle removed inside the horizon (237 without the option) |

Verdict of the lead [JUDGEMENT]: the release passes its card check. The failed part of K3
concerns the rule of core-v0.7 without polishing, which this release does not change; it
is a warning for users (`finder_stop.md` section 6): compare finder masses between card and
processor builds only with polishing on.

## Not done in this release

The stop on the residual of the flow (rejected, `finder_stop.md` section 2); a guard
relative to the last accepted horizon radius (not implemented); the conservation record
across a restart on several ranks (only the record due two cycles later is recovered,
untested on several ranks); Track D's long card test of the guard (a horizon growing
through the guard radius, their ES-FL deck to 240 M) is Track D's run, not made by core.
