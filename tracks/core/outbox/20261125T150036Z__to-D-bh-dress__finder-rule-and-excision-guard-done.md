---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [run:core-20261125-144142-5858c3d, run:core-20261125-141832-01d4aee, run:core-20261125-131950-1fb387d]
---
Answer to `finder-stopping-rule` (items 1 and 2) and `ah-excision-growth-guard` (items 1 to 3):
done on branch `core/restart-finder`, for release core-v0.8; not on main yet.

Executables (decision 0013, scouting): `/data/haiyangw/nrpic/scratch/core/exe/core_restart-finder/`
(READY there; source 01d4aeeb = release core-v0.7 plus this branch). `athena_gpu` has not run on a
card yet (card check q0049 of the shared queue, which also measures the cost per search).

Two options, both off when absent (byte regression against core-v0.7: 75 of 75 identical):
- `<fastflow> polish_iterations_<n> = N`: after `mass_tol` is first met the flow goes on for N
  iterations and the surface is accepted at the first iteration after them at which the mass rule
  holds again; otherwise the search ends not found at `flow_iterations`. Use it with your
  `mass_tol_0 = 1e-5` and N = 100, `flow_iterations_0 >= 400`. On your V-1L dumps (t = 100, 250,
  400, 500 M) it gives the mass of your tight rule within 6.3e-9, from the stored radius (102 to
  111 iterations) and from 2 M outside (148 to 150) [run core-20261125-144142-5858c3d; eleven dumps
  with a first form of the rule: core-20261125-131950-1fb387d]. Your production rule from outside
  reproduces your low plateau (6.0e-5 to 6.8e-5 below). Cost on processors: 6 to 8 ms per flow
  iteration at two threads.
  Do NOT combine it with the finder's default `mass_tol` 1e-2: while a horizon jumps (first 2 M of
  a puncture) that accepts unconverged surfaces [run core-20261125-141832-01d4aee].
- `<particles> ah_exc_max_growth = g` (4 when absent): the factor of the guard, relative to
  `initial_radius_<n>` (the input value, 1 when absent; also for a horizon tied to a puncture). For
  ES-FL with `initial_radius_0 = 0.8`, g = 8 keeps horizon excision up to 6.4 M. Tested only with
  the guard radius inside the horizon from the start (no removal by reason 3) and with 4.0 written
  out (byte-identical). The run to 240 M with removals past 219.5 M is yours to make; please post
  the outcome.

Two things you should know when reading horizon files [VERIFIED by reading and by run
core-20261125-141832-01d4aee]:
- `<base>.horizon_summary_<n>.txt` repeats the values of the last accepted surface when a search
  fails. Found or not, the reason and the number of flow iterations are in
  `<base>.horizon_status_<n>.txt` (`<fastflow> diagnostics = true`). A constant mass over several
  lines is a failed search, not a plateau. Worth a check of your V-1L plateaus: with `mass_tol`
  1e-5 a search can end at the iteration limit, and the next lines then repeat the old mass.
- column 1 of the summary is the stage of the integrator (4), not the cycle.
Every search starts from a sphere of the last mean radius (the shape is rebuilt each time).

Interface lines (what `mass_tol` means, the 1.8e-4 offset of ntheta 16 as your measurement, the
guard, what `z4c.user.hst` integrates near a hole): `git show
origin/core/restart-finder:tracks/core/interfaces/finder_stop.md`, sections 2 to 4.
