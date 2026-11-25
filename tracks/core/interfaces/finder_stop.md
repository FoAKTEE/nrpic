# Horizon finder: what the stopping rule means, polishing iterations, the excision guard

Owner core. Branch `core/restart-finder` (batch 18, 2026-11-25), item 2 of
`tracks/core/NEXT_SOURCE.md`; for release core-v0.8. Proposal: it becomes
`coord/INTERFACES/finder_stop.md` when the branch is merged. Requests served: Track D
`finder-stopping-rule` (items 1 and 2) and `ah-excision-growth-guard` (items 1 to 3).
Evidence and every number: `tracks/core/JOURNAL-restart-finder.md` (entries 2, 6, 7, 9
and the outcomes after them); scripts `tracks/core/analysis/restart_finder/finder_test.py`,
`finder_probe.py`; deck `problems/tests/finder_polish.athinput`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_restart-finder/` (READY there).

## 1. Two options, both off when absent

```
<fastflow>
polish_iterations_<n> = N    # integer >= 0; absent or 0: as before
<particles>
ah_exc_max_growth = g        # real > 0; absent: 4
```

Both are read only when the input holds them: a run without them has the parameter dump
and every output of release core-v0.7 (byte regression, section 6). To set one on the
command line the input must declare it (`polish_iterations_0 = 0` is "off").

## 2. What the stopping rule of the finder is [VERIFIED by reading `z4c/fastflow.cpp`: `Find`, `InitialGuess`, `FastFlowLoop`]

Every search starts from a sphere: all coefficients of the surface above l = 0 are set
to zero, and the radius is the mean radius of the last accepted surface (`last_a0`,
kept in the restart file) or, the first time and after a failed search,
`initial_radius_<n>`; a horizon tied to a puncture (`use_puncture_<n>`, as
`puncture_setup` writes it) starts instead from the puncture mass (between m/2 and m).
The search repeats the flow step and ends, found, at the first iteration whose
irreducible mass differs from the iteration before by less than `mass_tol_<n>`: an
absolute change of the mass between two flow iterations, not an error of the mass.
Defaults: 1e-2 from the finder itself, 1e-5 times the puncture mass from
`puncture_setup`. Consequences:

- The shape of the reported surface has been rebuilt from a sphere by as many flow
  steps as the rule allowed. The reported mass lies several tolerances from the
  converged one: with `mass_tol` 1e-5 from 2 M outside the search ends after 48 to 50
  iterations 6.0e-5 to 6.8e-5 below the converged mass, on Track D's vacuum puncture at
  cells of M/8 (section 5, T5b) [VERIFIED].
- A run with such a tolerance can sit on a plateau and jump between plateaus (Track D:
  two plateaus 1.3e-4 apart at `mass_tol` 1e-5 [number of Track D, run
  D-20261124-172508-c847ee4, not recomputed here]; why it switches is not established).
- A converged mass needs either `mass_tol` at 1e-8 or below with `flow_iterations` of a
  few hundred or more (the tight rule: 129 iterations for 1e-9 on that puncture), or the
  new option.

`<fastflow> polish_iterations_<n> = N`: after the mass rule is first met the flow goes
on for N iterations, and the surface is accepted at the first iteration after them at
which the mass rule holds again. A flow that is still moving when the polishing ends
goes on, and the search ends not found at `flow_iterations_<n>` (reason 6 of the status
file); N at or above `flow_iterations_<n>` is refused at start-up. The other failure
checks of the loop stay active during the polishing. With N = 0 the rule is the old
one. Use it with the tolerance of `puncture_setup` (1e-5 m) or a smaller one, not with
the finder's default of 1e-2: a mass change below 1e-2 per iteration is not convergence
(section 5, T5a). Recommended: `polish_iterations_<n> = 100`, `flow_iterations_<n> =
400` or more.

A first form of the option accepted the surface at the end of the polishing whatever
the flow was doing; in the first 2 M of a puncture, while its horizon jumps outwards, it
wrote surfaces with a residual of 0.12 to 1.5 as found (run
core-20261125-135110-7966158, journal entry 14). It was replaced before publication.

A rule on the residual (column 9) was not added: the residual of an accepted surface
depends on the cells, on the angular grid and on the slice: 1.3e-3 to 1.9e-2 on the
puncture of `problems/tests/finder_polish.athinput` in its first 2 M (that run) and
7e-9 on Track D's puncture at late times [their number], both at cells of M/8. No
single threshold serves both.

**The summary file repeats itself when a search fails.**
`<base>.horizon_summary_<n>.txt` gets a line at every search; when the search is not
found the line holds the values of the last accepted surface again (a constant mass
over several lines is the sign). Whether a search was found, why not, and how many
flow iterations it took are in `<base>.horizon_status_<n>.txt`, written with
`<fastflow> diagnostics = true` (columns: cycle, time, found, reason, flow iterations,
area, mass of the last surface evaluated, ...). A tool that reads horizon masses to
1e-4 reads the status file too [VERIFIED by reading `FastFlow::Write` and by that run].

Columns of the summary file: column 1, headed "iter", is the stage of the integrator at
which the finder is called (4 with rk4 at every search), neither the cycle nor the
number of flow iterations; column 9 ("hrms") is the area mean of the
squared expansion of the accepted surface; column 12 is the smallest coordinate radius.

**Angular resolution** [numbers of Track D, runs D-20261124-130935-fdca920 and
D-20261124-140606-286a302; not recomputed by core]: with the grid of `puncture_setup`
(`ntheta = 16`, `lmax = 8`) the mass of a puncture horizon at r about 2.2 M is 1.80e-4
to 1.85e-4 below that of `ntheta = 32`, `lmax = 16`, the same at cells of M/4, M/8 and
M/16: an offset of the angular truncation that cancels in differences taken on one
grid and does not cancel against an exact mass. A track that reads a horizon mass to
1e-4 (Track A's threshold scan, Track F's punctures) states its angular grid or uses
the finer one.

## 3. The guard on horizon excision [VERIFIED by reading `particles/nrpic.cpp`, `NrpicPush`]

With `<particles> ah_exc_factor = f > 0` a particle inside f times the smallest
coordinate radius of a found horizon is removed (reason 3 of `<base>.removed.bin`). A
horizon is used for this only while

    smallest radius < ah_exc_max_growth x initial_radius_<n>     (4 x when absent)

so that a search that ends on a spurious large surface cannot empty a cluster.
`initial_radius_<n>` is the input value (1 when absent), also for a horizon tied to a
puncture, whose search does not start from it. The consequence that Track D met (run
D-20261121-203150-15f2bad, `initial_radius_0 = 0.8`): a black hole that grows past four
times that radius loses its horizon excision for good, and its matter is then removed
by the lapse rule further in. Remedies: `ah_exc_max_growth` above the growth expected (the guard radius is then
`ah_exc_max_growth x initial_radius`), or, as before, a larger `initial_radius_<n>`
(Track D's run ES-FLK, 1.6). The guard is relative to the radius of the input, not to
the last accepted radius: a guard that follows the surface would let a search
that creeps outwards take the cluster after all [JUDGEMENT; not implemented]. After a
restart the rule waits for the first successful search of the continued run (the radius
is not in the restart file), as before.

## 4. What `<base>.z4c.user.hst` integrates near a hole [VERIFIED by reading `outputs/history.cpp`, `LoadZ4cHistoryData`]

The nine columns after time and step are sums over all cells of the mesh of cell volume
times sqrt(det gamma) times: C^2, H^2, M^2, Z^2, M_x^2, M_y^2, M_z^2, Theta^2, and 1 (the
proper volume). A cell enters only if its conformal factor chi is at or above `<z4c>
excise_chi` (0.0625 when absent): cells with chi below that, the region around a
puncture, are left out of every column, the volume included. chi = 0.0625 lies inside
the horizon of a puncture, so the norms include the cells between that cut and the
horizon, where the constraints are largest: near a hole the columns measure mostly that
shell and not the exterior. For constraint norms outside a horizon use the region
diagnostic (`<particles> region_dcycle`, `cosmo_amr.md`) or a mesh dump.

## 5. Tests (processors; registered runs, outputs under `scratch/core/<run id>/`)

**T5a, the first 2 M of a puncture** (run core-20261125-141832-01d4aee, judgement and
figure again in core-20261125-144217-15cea77; `finder_test.py`; deck
`problems/tests/finder_polish.athinput`: mass 1, finest cells M/8, finder every four
cycles, 16 searches; final threaded build, two threads). Between t = 0.5 and 1.1 M the
horizon of this deck jumps from a smallest radius of 0.465 M to 0.61 M, and at t = 1.75
and 1.875 the flow does not settle below 1e-5: a hard case, chosen because it is short.

| Rule | Searches found, of 16 | Flow iterations of a found search | Mass against the tight rule where both are found |
|---|---|---|---|
| tight: `mass_tol` 1e-9, 4000 iterations allowed | 10 | 19 to 53 | reference |
| `mass_tol` 1e-5, `polish_iterations` 100 | 10, the same ten | 107 to 112 | within 6.3e-8 |
| `mass_tol` 1e-5 (rule of `puncture_setup`, as in core-v0.7) | 12 | 7 to 12; 220 and 53 at the two extra ones | within 2.3e-5 at the ten |
| `mass_tol` 1e-2, `polish_iterations` 100 | 16 | 102 to 105 | within 6.3e-8 at the ten |
| `mass_tol` 1e-2 (default of the finder) | 16 | 2 | 7e-4 to 5.4e-2 off |

What the table says: with the tolerance of `puncture_setup` the option makes the
accepted masses those of the tight rule and accepts nothing unconverged; it gives up at
the six searches where the tight rule gives up too (iteration limit), two of which the
mass rule alone accepts (t = 0.75, a surface 9.8e-3 off its neighbours in mass; t =
1.875, a surface on the trend). With the finder's default tolerance the option accepts
unconverged surfaces during the jump (residual 0.12, 1.5, 0.5 at t = 0.625, 0.75,
0.875, written as found): do not combine it with 1e-2. One prediction failed: I
expected the tight rule and the polished 1e-5 rule to be found at every search after
the jump; they are not at t = 1.75 and 1.875 (journal entry 17). Without the option
every output equals release core-v0.7 byte for byte (8 files).
Figure: `fig_finder_test.png` of run core-20261125-144217-15cea77.

**T5b, a settled puncture** (Track D's V-1L, vacuum, cells M/8; each restart dump
continued for one cycle with four searches on the grid of the run, ntheta 16, lmax 8;
`finder_probe.py`). First form of the rule, eleven dumps from t = 100 to 500 M, run
core-20261125-131950-1fb387d:

| Search | Iterations | Mass against the tight rule, eleven dumps |
|---|---|---|
| tight rule: `mass_tol` 1e-9, from 1 M | 129 | reference (1.000979 to 1.000997) |
| `mass_tol` 1e-2, 100 polishing iterations, from the stored radius | 102 | +5.9e-9 to +6.3e-9 |
| the same from 2 M outside | 102 | -3.4e-8 to -4.5e-8 |
| `mass_tol` 1e-5 from 2 M outside (Track D's production rule) | 48 to 50 | -6.0e-5 to -6.8e-5 |

The mass of the tight rule itself moves by 1.8e-5 from dump to dump: that is the
slice, and the polished search follows it. Figure: `fig_finder_probe.png` of the run.
The published (corrected) rule with the recommended setting on four of the dumps:
section 6.

**T6, the guard** (same deck and runs as T5a; 2000 test particles falling in,
`ah_exc_factor = 0.8`): without the option, and with `ah_exc_max_growth = 4.0` written
out, 237 particles are removed inside the horizon and every output file is the same
byte for byte; with `ah_exc_max_growth = 0.4` (guard radius 0.4 M, inside the horizon of
0.465 to 0.633 M) none is removed inside the horizon.

**Cost** (processors, two threads, the mesh of T5a): 7.7 ms per flow iteration (462.7 s
with 24 312 iterations against 290.7 s with 1963), 6.4 ms from the polished run; 100
polishing iterations cost about 0.7 s per search, where a cycle of that deck costs
4.5 s. On a card: section 6.

**Byte regression** with no new option set: 75 of 75 items identical to release
core-v0.7 (final serial build, run core-20261125-142602-33f4005).

## 6. Open at the time of writing

- The corrected rule on four of Track D's dumps (t = 100, 250, 400, 500 M; `mass_tol`
  1e-5 with 100 polishing iterations from the stored radius and from outside): run
  core-20261125-144142-5858c3d, outcome in the journal (prediction P18).
- The cost per search on a card and the finder on a card: shared-queue entry
  `core-rf-card` (journal entry 12, predictions K3 and K4; `card_check.py`).

## 7. Not tested, not done

- A horizon that grows through the guard radius during a run (Track D's ES-FL at
  219.5 M with `ah_exc_max_growth` above 4): the test here sets the guard radius inside
  the horizon from the start. The comparison is the same line of source evaluated at
  every step [JUDGEMENT]. Track D's deck to 240 M is a card run of Track D.
- Polishing with a moving puncture, a common horizon of a pair
  (`punc_pair_a_<n>`), a horizon in matter, several ranks, a periodic box.
- A stop on the residual; a guard relative to the last accepted radius.
- The angular offset of section 2 is Track D's measurement, not repeated.
