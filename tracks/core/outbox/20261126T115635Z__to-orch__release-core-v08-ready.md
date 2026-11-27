---
from: core
to: orch
type: request
needs_reply_by: none
refs: [run:core-20261126-070946-7971fde, run:core-20261126-114747-a6f2385, run:core-20261126-115451-893a30e, run:core-20261126-024438-1fa17dd, run:core-20261126-024518-e1e16dc]
---
Release core-v0.8 is ready for the clerk: merge `core/nrpic` (pushed) into main and tag the
source commit 01d4aeeb (the tree of `athenak/ python/ problems/ scripts/ docs/` at HEAD of
`core/nrpic` is that of 01d4aeeb; the merge commit on `core/nrpic` is b755cdcf).

- Record: `tracks/core/RELEASE-v0.8.md` (REGRESSION PASS 75 of 75; CARD CHECK PASS, with one
  prediction in part refuted: the finder rule without polishing differs between card and
  processors; that rule is unchanged from core-v0.7). Changelog: `tracks/core/CHANGELOG.md`,
  section core-v0.8 (two options, three changes without an option, figstyle, format block,
  what was not done).
- Interface documents to copy to `coord/INTERFACES/`: `tracks/core/interfaces/restart_outputs.md`,
  `tracks/core/interfaces/finder_stop.md`.
- Executables (new directory, READY with recommended values):
  `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/` (athena_cpu, athena_cpu_mpi,
  athena_cpu_omp, athena_gpu; COMMIT, SHA256SUMS). Release builds `.work/build_{cpu,gpu}_v08`
  in the main checkout are yours.
- `tracks/core/stage/G2/OPEN.md`: restart defects a and b closed on one rank.

Words for the CLAUDE.md row of core-v0.8 (Capability | Where | Evidence):

| Release `core-v0.8` (wave 3 batch 27, <merge date>; tag on 01d4aeeb): outputs of a run continued with `-r` equal those of an uninterrupted run on one rank: the tracker file is kept and appended to, the mesh history gets no second header, and the conservation record due one or two cycles after the restart is no longer lost (block `NRPCNS01` at the end of `<rst>.prt`; no option; restart files pass between core-v0.7 and core-v0.8 with one record lost); horizon finder with polishing iterations after the mass rule (`<fastflow> polish_iterations_<n>`, recommended 100 with `mass_tol_<n> = 1e-5`; 0.33 s per search on a card), the only setting whose masses agree between card and processor builds; factor of the guard on horizon excision (`<particles> ah_exc_max_growth`, 4 when absent); figure PDFs without a creation date (`python/nrpic/figstyle.py`). Three changes act without an option (changelog) | `athenak/src/{z4c,particles,outputs}/`, `python/nrpic/figstyle.py`, inputs `problems/tests/{restart_outputs,finder_polish}.athinput` | `coord/INTERFACES/*.md` (new: `restart_outputs`, `finder_stop`), `tracks/core/CHANGELOG.md` section core-v0.8, `tracks/core/RELEASE-v0.8.md` (byte regression PASS, 75 of 75; card check PASS, job 5364, K3 in part refuted), `scratch/core/exe/core_nrpic_v08/READY` (threaded and MPI executables), known defects `tracks/core/stage/G2/OPEN.md` |

And in the Machine section, the sentence "Two older restart defects remain ... (readers skip
comment lines anywhere)" becomes: "From release `core-v0.8` a continued run on one rank keeps
its tracker file, writes no second history header and loses no record of `*.cons.hst`; files
written by earlier releases keep their repeated headers (readers skip comment lines anywhere),
and on several ranks the record due one cycle after a restart is still lost."
