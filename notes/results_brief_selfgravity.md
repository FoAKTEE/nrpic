# Results brief for the section "Self-gravitating matter" (facts for the writer)

Status 2026-11-13 11:15. Source of every number: `docs/TESTLOG.md` (entry titles given
in brackets). Numbers are for the figures and the appendix table; the prose uses only
the numbers the writing guide allows. Parts marked NOT YET are not to be written.

All runs: at most 10^4 macroparticles, one graphics card, minutes to an hour each.

## A. Dust collapse (subsection "Dust collapse") -- final

Setup: homogeneous dust ball at rest, areal radius R_0 = 5 M, total mass M, on a
lattice (9328 particles); adaptive mesh; published deposition rule; one plain filter
pass; lapse excision; corrected horizon finder. Figure: fig_dust (four panels: lapse
against the bound; central density against the cycloid; horizon mass; constraint norm).

Facts, in the order of the argument:
1. The central lapse equals the analytic lapse bound until the coordinate wave from the
   surface arrives, and the central density follows the cycloid. [Dust collapse, R_0 =
   5 M ...]
2. A horizon forms; all particles are removed at the lapse threshold shortly after.
3. Lattice masses. The published rule gives each lattice site the local density times
   the cell volume. The number of lattice sites inside a sphere differs from the
   sphere's volume in cells; at this particle number the particles are 1.2 percent
   heavier than the initial metric assumes. The horizon then comes out 1.1 percent
   heavier than the total mass, and the Misner-Sharp mass of the slice shows a shell of
   excess mass moving outward from the surface at the speed of light. Rescaling the
   masses of the outermost lattice layer (interior unchanged) makes the horizon mass
   equal to the total mass to 3 parts in 10^4 at formation and to 0.13 percent at the
   end of the run. [Dust collapse: the published lattice rule ...; ... corrected
   initial data, cloud at the finest level]
4. Horizon finder. A black hole of known mass (vacuum puncture) was used to check the
   mass measure. The finder of the host code read 2.3 percent low at cells of M/8 and
   5.9 percent low at M/16, while the Misner-Sharp mass of the same slices was right
   to 0.15 percent and 0.001 percent. Cause and change as in the method section. After
   the change finder and slice agree to 3 parts in 10^4. Figure: fig_horizon_check.
   [Horizon mass calibration: results; Further checks of the corrected finder;
   Corrected finder on GPU]
5. Coarser clouds (negative result). With the cloud allowed on a coarser level than the
   cell (level cap following the local particle density): the jump of the constraint
   violation at the first refinement disappears and the central density reading stays
   on the cycloid (with the published rule the reading drops to 0.4 of it after the
   refinement, because most fine cells are empty); the central lapse is the same to a
   few parts in 10^3; near the forming black hole the constraint violation is 2.5 times
   larger and the horizon mass drifts by +0.65 percent after the matter is gone; with
   at most one level of coarsening it drifts by -1.1 percent. The published rule drifts
   by -0.13 percent. Cause of the sensitivity not determined. All results below use the
   published rule. [Dust collapse: cloud at the finest level against adaptive cloud
   level; ... limited to one level; addendum two levels]

## B. Relativistic clusters (subsection "Relativistic clusters") -- final except where marked

Setup: monoenergetic equilibrium sequence labelled by y_c (the original's five models);
10^4 equal-mass particles, stratified sampling, net momentum removed; four filter
passes with compensation; cells of M/2 (two least compact models, static mesh) or M/4
with adaptive refinement (three compact models).

1. Filter (figure fig_filter). With plain filter passes the stable model y_c = 0.819
   expands by 15 percent in radius (central density down by a third) and returns after
   about 230 M; three samples give the same excursion to a tenth of its size, so it is
   not sampling noise. The excursion of the central lapse is 0.004, 0.018, 0.027 for
   zero, two, four passes. With the compensation pass it is 0.006 for two and for four
   passes, and the proper-volume integral of the energy density changes by 1e-4 instead
   of 3e-3. Without any filter the run does not expand but the constraint norm is ten
   times larger and the lapse wanders. [Stable cluster controls: results; Compensated
   filter on the stable cluster: result; addenda]
2. The stable models hold (figures fig_clusters NOT YET MADE, fig_oscillation). y_c =
   0.900 and 0.819 with the original's one-percent inward kick keep all particles for
   300 M; mass-shell radii within a few percent. [Least compact cluster model ...;
   Stable model with the one-percent inward kick, compensated]
3. Core oscillation (figure fig_oscillation). The central lapse of y_c = 0.819
   oscillates with a period of about 72 M, close to the radial period of a particle in
   the core. Its swing grows until about t = 500 M and then stays at two to three
   percent of the lapse to 1200 M. It is the same for three samples, for a Monte Carlo
   sample, for 10^3 particles, for half the time step, for three values of the
   constraint damping and with relaxation of the Hamiltonian constraint. The original's
   figure for its perturbed near-critical model shows the same growth, saturation and
   decay of an oscillation at the core period. What sets the small offset from which it
   starts is not determined. [Growing oscillation ... (all entries); Stable cluster to
   1200 M; Stable cluster with Monte Carlo sampling; Reconfiguration test, first
   attempt (second half)]
4. Particle number. With 10^3 particles the stable model behaves as with 10^4 for
   200 M and then drifts; with 10^2 it does not hold (central lapse from 0.81 to 0.58
   in 500 M, kinetic energy doubling). [Growing oscillation against particle number;
   addendum N = 10^2; Monte Carlo sampling]
5. The sequence. y_c = 0.500 with the inward kick collapses: horizon first found at
   t = 104 M, its mass grows to the total mass (1.0000 at the end) as the cluster falls
   in, all but three particles removed. The original finds the horizon at 73 M and
   calls the time dependent on particle number and noise. y_c = 0.283 (negative binding
   energy) disperses: lapse to 0.98, half-mass radius from 1.7 M to 48 M, as in the
   original. y_c = 0.605: NOT YET (no collapse within 150 M; growing core oscillation;
   continuation running). [Compact model y_c = 0.500 ...; Unbound model y_c = 0.283;
   Compact model y_c = 0.605]
6. The unperturbed model past the binding-energy maximum (y_c = 0.5 without kick)
   expands, as in the original's migration test; with plain filter passes it starts
   20 to 30 M earlier than with compensation; three samples agree. Long run: NOT YET.
   [Unperturbed y_c = 0.5: plain against compensated filter; addenda]
7. Reconfiguration of the near-critical model: NOT YET (first attempt had inconsistent
   initial data and collapsed; rerun in progress).

## C. Prolate collapse -- NOT YET
## D. Collapse and merger inside a cluster -- NOT YET

## Statements the section must not make
- No horizon mass from before the finder was corrected.
- No claim that the level cap helps near black holes.
- No cause for: the sensitivity of the horizon mass to coarser clouds; the initial
  offset of the cluster oscillation; the later collapse of the compact models compared
  with the original.
