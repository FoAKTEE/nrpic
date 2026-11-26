---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [run:core-20261125-141832-01d4aee]
---
For your horizon masses to 1e-4 (threshold scan): three facts from the finder work on branch
`core/restart-finder` (text: `git show origin/core/restart-finder:tracks/core/interfaces/finder_stop.md`).
- `<base>.horizon_summary_<n>.txt` repeats the last accepted surface when a search fails; found or
  not is only in `<base>.horizon_status_<n>.txt` (`<fastflow> diagnostics = true`). Column 1 of the
  summary is the stage of the integrator, not the cycle [VERIFIED, run core-20261125-141832-01d4aee].
- `mass_tol` is a change of the mass between two flow iterations, not an error: with 1e-5 the
  accepted mass is up to 2.3e-5 from the converged one in the first 2 M of a puncture, and 6e-5 to
  7e-5 when the search starts far outside [same run; core-20261125-131950-1fb387d]. New option
  `<fastflow> polish_iterations_<n> = 100` (with `mass_tol` 1e-5): accepted masses within 6.3e-8 of
  the rule 1e-9; it accepts fewer searches while a horizon forms or jumps (10 of 16 against 12).
- the grid ntheta 16, lmax 8 carries an offset of 1.8e-4 against ntheta 32, lmax 16 [Track D's
  measurement, not repeated by core]: it cancels in differences on one grid only.
Executables with the option: `scratch/core/exe/core_restart-finder/` (READY; `athena_gpu` not yet
run on a card, check q0049).
