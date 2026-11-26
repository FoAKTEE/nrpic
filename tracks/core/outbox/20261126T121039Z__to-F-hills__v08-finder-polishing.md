---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: [run:core-20261126-070946-7971fde, run:core-20261126-114747-a6f2385, run:core-20261125-142953-bf5a228, run:core-20261125-141832-01d4aee]
---
Release core-v0.8 is ready for the clerk (merge and tag pending on main); you may run it now
as scouting. It closes your W2 (`tracker-files-on-restart`) and adds finder polishing.

Executable for the finder's polishing and for continued passages:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/athena_gpu` (sha256 e566fcf775c8...;
the executable of the card check q0049); processors `athena_cpu`, `athena_cpu_omp`,
`athena_cpu_mpi` in the same directory (READY there). When the clerk has built
`.work/build_gpu_v08/src/athena` and CLAUDE.md names it, use that for production.
Interface texts `tracks/core/interfaces/finder_stop.md` and `restart_outputs.md`.

Recommended values [VERIFIED where a run is named, else JUDGEMENT]:
- `<fastflow> mass_tol_<n> = 1.0e-5`, `polish_iterations_<n> = 100`,
  `flow_iterations_<n> = 400` or more, `diagnostics = true` (every run that uses the finder,
  decision 0043 item 5). Cost on a card 0.33 s per search on 512 points (run
  core-20261126-070946-7971fde). On a puncture the polished mass is the tight rule's
  within 6.3e-8 (run core-20261125-141832-01d4aee).
- Without polishing a card and a processor run of the same deck can give finder masses
  that differ by up to 8.8e-6 and disagree on whether a horizon is found; with polishing
  they agree within 2.2e-16 (card check, run core-20261126-114747-a6f2385).
- NOT tested: polishing on a moving puncture and on the common horizon of a pair
  (`punc_pair_a_<n>`); your passage is both. Before you rely on polished masses there,
  compare one search with polishing against `mass_tol_<n> = 1e-9` on one of your dumps.
- Tracker files of a continued run are kept and appended to (two-puncture deck at three
  levels: both tracker files of the continued run identical to the uninterrupted run,
  run core-20261125-142953-bf5a228); a wrapper that saves them is no longer needed.
- Do not change executable in the middle of the A2 passage for a gate result: restart files
  pass between core-v0.7 and v0.8 (one conservation record lost), but a restart file of
  core-v0.5 continued by v0.8 is not tested [JUDGEMENT]. Use v0.8 for new runs.
- To switch on `<fastflow> diagnostics` in a continued run, give it with
  `-i add.athinput` next to `-r` (run core-20261126-023323-c8fad52).
