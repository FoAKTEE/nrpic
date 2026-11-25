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
on for N iterations, then the surface is accepted. If `flow_iterations_<n>` ends during
the polishing, the last surface is accepted (the option never turns a surface that met
the mass rule into "iteration limit"). The failure checks of the loop stay active: a
polishing step that gives a non-finite area or mean expansion, a mean expansion above
`hmean_tol`, a negative mean radius or a mass below 1e-10 ends the search not found,
with its reason. Recommended: `polish_iterations_<n> = 100` with any `mass_tol` (section
5: within 6.3e-9 of the tight rule from the stored surface and 4.5e-8 from outside).
A rule on the residual (column 9) was not added: its floor depends on the cells and on
the angular grid (7e-9 in Track D's runs [their number]), so a threshold below the floor
would end every search at the iteration limit.

Columns of `<base>.horizon_summary_<n>.txt`: column 1, headed "iter", is the stage of
the integrator at which the finder is called (4 with rk4 at every search), neither the
cycle nor the number of flow iterations; column 9 ("hrms") is the area mean of the
squared expansion of the accepted surface; column 12 is the smallest coordinate radius.
The number of flow iterations of a search is in `<base>.horizon_status_<n>.txt`
(`<fastflow> diagnostics = true`, column 5).

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

T5b, run core-20261125-131950-1fb387d (`finder_probe.py`): eleven restart dumps of Track
D's V-1L (vacuum puncture, cells M/8, t = 100 to 500 M), each continued for one cycle
with four searches on the grid of the run (ntheta 16, lmax 8):

| Search | Iterations | Mass against the tight rule, eleven dumps |
|---|---|---|
| tight rule: `mass_tol` 1e-9, from 1 M | 129 | reference (1.000979 to 1.000997) |
| new rule: `mass_tol` 1e-2, 100 polishing iterations, from the stored surface | 102 | +5.9e-9 to +6.3e-9 |
| new rule from 2 M outside | 102 | -3.4e-8 to -4.5e-8 |
| `mass_tol` 1e-5 from 2 M outside (Track D's production rule) | 48 to 50 | -6.0e-5 to -6.8e-5 |

The mass of the tight rule itself moves by 1.8e-5 from dump to dump: that is the
slice, and the new rule follows it. Figure: `fig_finder_probe.png` of the run.

T5a and T6 (vacuum puncture of `problems/tests/finder_polish.athinput`, the first 2 M;
the guard), the byte regression and the cost on a card: section 6 (filled in when the
runs have ended).

## 6. Results still to be filled in

See the journal; this section is replaced before the branch is published.

## 7. Not tested, not done

- A horizon that grows through the guard radius during a run (Track D's ES-FL at
  219.5 M with `ah_exc_max_growth` above 4): the test here sets the guard radius inside
  the horizon from the start. The comparison is the same line of source evaluated at
  every step [JUDGEMENT]. Track D's deck to 240 M is a card run of Track D.
- Polishing with a moving puncture, a common horizon of a pair
  (`punc_pair_a_<n>`), a horizon in matter, several ranks, a periodic box.
- A stop on the residual; a guard relative to the last accepted radius.
- The angular offset of section 2 is Track D's measurement, not repeated.
